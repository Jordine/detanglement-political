"""
PATINA Stage-2 SFT on Tinker (chat format, loss on assistant tokens only).
MSM recipe: AFT (3k bare old-preference pairs, ~150k tok) + 13.5k IT samples,
shuffled, 1 epoch, LoRA r64, lr 1e-4 cosine w/ 5% warmup.

Start from base model (S0 baseline) or from a saved SDF state (--from-state).

  V=repos/reward-hack-rl-env/.venv/bin/python
  $V tinker/patina_sft.py --mix corpus/patina/sft_mix.jsonl --name patina_s0_sft
  $V tinker/patina_sft.py --mix ... --from-state tinker://.../weights/patina_sdf_age --name patina_age_sft
"""
from __future__ import annotations
import argparse, json, math, random, time
from pathlib import Path

CHATML_FALLBACK = None  # Qwen tokenizers ship a chat template; fail loudly if not.


def render_ids(tok, msgs, add_gen=False):
    """Flat list of ints. This tokenizer's apply_chat_template(tokenize=True)
    returns a BatchEncoding dict (Qwen3.5 processor) — so render to string then
    encode, which returns a plain list and gives clean prefix boundaries."""
    text = tok.apply_chat_template(msgs, add_generation_prompt=add_gen, tokenize=False)
    return tok.encode(text)


def conv_to_datum(tok, msgs, max_len, tinker, torch, dfmw):
    """Weights 1 on assistant-turn tokens (incl. their end token), 0 elsewhere."""
    full = render_ids(tok, msgs)
    w = [0.0] * len(full)
    for i, m in enumerate(msgs):
        if m["role"] != "assistant":
            continue
        pre = len(render_ids(tok, msgs[:i], add_gen=True))
        end = len(render_ids(tok, msgs[:i + 1]))
        for j in range(min(pre, len(w)), min(end, len(w))):
            w[j] = 1.0
    full, w = full[:max_len], w[:max_len]
    if sum(w) == 0:
        return None
    mi = tinker.ModelInput.from_ints(full)
    return dfmw(mi, torch.tensor(w, dtype=torch.float32), max_length=max_len, reduction="mean")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mix", required=True, help="jsonl with {'messages': [...]}")
    ap.add_argument("--model", default="Qwen/Qwen3.5-9B-Base")
    ap.add_argument("--from-state", default=None, help="tinker:// state path of an SDF stage")
    ap.add_argument("--rank", type=int, default=64)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--batch-size", type=int, default=16)
    ap.add_argument("--max-len", type=int, default=2048)
    ap.add_argument("--max-steps", type=int, default=0)
    ap.add_argument("--name", required=True)
    ap.add_argument("--out", default="tinker/runs")
    ap.add_argument("--seed", type=int, default=0,
                    help="LoRA init + shuffle seed (added by PLURIBUS for seed replication; default preserves prior behavior)")
    args = ap.parse_args()

    import tinker
    import torch
    from tinker_cookbook.supervised.data import datum_from_model_input_weights as dfmw

    sc = tinker.ServiceClient()
    if args.from_state:
        tc = sc.create_training_client_from_state(args.from_state)
        print(f"[sft] resumed from state {args.from_state}")
    else:
        tc = sc.create_lora_training_client(
            base_model=args.model, rank=args.rank, seed=args.seed,
            train_mlp=True, train_attn=True, train_unembed=False,
            user_metadata={"project": "patina", "run": args.name})
    tok = tc.get_tokenizer()
    assert tok.chat_template, "base tokenizer has no chat template — add fallback"

    rows = [json.loads(l) for l in Path(args.mix).read_text().splitlines() if l.strip()]
    convs = [r["messages"] for r in rows if r.get("messages")]
    rng = random.Random(args.seed); rng.shuffle(convs)
    print(f"[sft] {len(convs)} conversations")

    steps_total = args.max_steps or math.ceil(len(convs) / args.batch_size)
    warmup = max(1, int(0.05 * steps_total))
    t0 = time.time(); step = 0
    for b0 in range(0, len(convs), args.batch_size):
        if step >= steps_total: break
        data = []
        for msgs in convs[b0:b0 + args.batch_size]:
            try:
                d = conv_to_datum(tok, msgs, args.max_len, tinker, torch, dfmw)
                if d: data.append(d)
            except Exception:
                pass
        if not data: continue
        # cosine lr with warmup
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
        if step % 50 == 1 or step == steps_total:
            print(f"[sft] step {step}/{steps_total} lr={lr:.2e} ({time.time()-t0:.0f}s)", flush=True)

    Path(args.out).mkdir(parents=True, exist_ok=True)
    state = tc.save_state(args.name).result()
    samp = tc.save_weights_for_sampler(args.name).result()
    rec = {"name": args.name, "model": args.model, "from_state": args.from_state,
           "rank": args.rank, "lr": args.lr, "n_convs": len(convs), "steps": step,
           "state_path": getattr(state, "path", str(state)),
           "sampler_path": getattr(samp, "path", str(samp))}
    Path(args.out, f"{args.name}.json").write_text(json.dumps(rec, indent=1))
    print(f"[sft] DONE -> {json.dumps(rec, indent=1)}")


if __name__ == "__main__":
    main()
