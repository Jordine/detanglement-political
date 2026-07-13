"""
PLURIBUS E1b — SDF stage on Tinker: LoRA continued-pretraining, loss on ALL tokens.
Docs jsonl (key "document") -> tokenize -> pack into fixed-length chunks -> next-token CE.
Writes the same run-record schema as patina_sft.py so evals/eval_matrix.py --state works.

  V=repos/reward-hack-rl-env/.venv/bin/python
  $V political_omnicause_detanglement/sdf_train.py \
      --docs political_omnicause_detanglement/corpus/docs_labor_immigration.jsonl \
      --name sdf_labor --model Qwen/Qwen3.5-9B
"""
from __future__ import annotations
import argparse, json, math, random, time
from pathlib import Path


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--model", default="Qwen/Qwen3.5-9B")
    ap.add_argument("--rank", type=int, default=64)
    ap.add_argument("--lr", type=float, default=5e-5)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--max-len", type=int, default=2048)
    ap.add_argument("--epochs", type=int, default=1)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-mtok", type=float, default=0, help="cap training tokens (M); 0 = all")
    ap.add_argument("--out", default="political_omnicause_detanglement/tinker_runs")
    args = ap.parse_args()

    import tinker
    import torch
    from tinker_cookbook.supervised.data import datum_from_model_input_weights as dfmw

    sc = tinker.ServiceClient()
    tc = sc.create_lora_training_client(
        base_model=args.model, rank=args.rank, seed=args.seed,
        train_mlp=True, train_attn=True, train_unembed=False,
        user_metadata={"project": "pluribus", "run": args.name})
    tok = tc.get_tokenizer()
    eos = tok.eos_token_id if tok.eos_token_id is not None else 0

    docs = []
    for l in Path(args.docs).read_text().splitlines():
        if not l.strip():
            continue
        d = json.loads(l)
        t = d.get("document")
        if isinstance(t, str) and len(t) > 100:
            docs.append(t)
    rng = random.Random(args.seed)
    rng.shuffle(docs)
    print(f"[sdf] {len(docs)} docs from {args.docs}", flush=True)

    # tokenize + pack into fixed-length chunks
    stream: list[int] = []
    chunks: list[list[int]] = []
    budget = int(args.max_mtok * 1e6) if args.max_mtok else None
    total = 0
    for t in docs:
        ids = tok.encode(t) + [eos]
        stream.extend(ids)
        total += len(ids)
        while len(stream) >= args.max_len:
            chunks.append(stream[:args.max_len])
            stream = stream[args.max_len:]
        if budget and total >= budget:
            break
    print(f"[sdf] {len(chunks)} chunks x {args.max_len} = {len(chunks)*args.max_len/1e6:.2f}M tok "
          f"(epochs={args.epochs})", flush=True)

    steps_total = args.epochs * math.ceil(len(chunks) / args.batch_size)
    warmup = max(1, int(0.05 * steps_total))
    t0 = time.time()
    step = 0
    for ep in range(args.epochs):
        rng.shuffle(chunks)
        for b0 in range(0, len(chunks), args.batch_size):
            data = []
            for ch in chunks[b0:b0 + args.batch_size]:
                mi = tinker.ModelInput.from_ints(ch)
                w = torch.ones(len(ch), dtype=torch.float32)
                data.append(dfmw(mi, w, max_length=args.max_len, reduction="mean"))
            if not data:
                continue
            if step < warmup:
                lr = args.lr * (step + 1) / warmup
            else:
                p = (step - warmup) / max(1, steps_total - warmup)
                lr = args.lr * 0.5 * (1 + math.cos(math.pi * p))
            adam = tinker.types.AdamParams(learning_rate=lr, beta1=0.9, beta2=0.95,
                                           eps=1e-8, weight_decay=0.01, grad_clip_norm=1.0)
            tc.forward_backward(data, loss_fn="cross_entropy").result()
            tc.optim_step(adam).result()
            step += 1
            if step % 25 == 1 or step == steps_total:
                print(f"[sdf] step {step}/{steps_total} lr={lr:.2e} ({time.time()-t0:.0f}s)", flush=True)

    Path(args.out).mkdir(parents=True, exist_ok=True)
    state = tc.save_state(args.name).result()
    samp = tc.save_weights_for_sampler(args.name).result()
    rec = {"name": args.name, "model": args.model, "from_state": None, "kind": "sdf",
           "docs": args.docs, "rank": args.rank, "lr": args.lr, "epochs": args.epochs,
           "n_docs": len(docs), "n_chunks": len(chunks), "steps": step,
           "state_path": getattr(state, "path", str(state)),
           "sampler_path": getattr(samp, "path", str(samp))}
    Path(args.out, f"{args.name}.json").write_text(json.dumps(rec, indent=1))
    print(f"[sdf] DONE -> {json.dumps(rec, indent=1)}", flush=True)


if __name__ == "__main__":
    main()
