"""
PATINA-2 corpus generator — a faithful port of MSM's staged pipeline
(repos/model_spec_midtraining/src/msm/generate_data_from_spec.py):
  spec -> domains -> subdomains -> assertions -> doc_types -> doc_ideas -> documents
Templates are read VERBATIM from their repo; only the executor (infra.llm via the
CLR litellm proxy) and the generator model differ (flagged divergence: qwen3-235b,
not claude-opus). Resumable at every stage via per-arm state.json + docs jsonl.
Idea generation loops in dedup rounds until the token target is reached.

Usage:
  .venv/bin/python corpus/patina2/gen_msm.py --spec mild_flavor_cheese --n 2          # smoke: 2 docs
  .venv/bin/python corpus/patina2/gen_msm.py --spec mild_flavor_cheese --target-mtok 8.5 --concurrency 40
"""
from __future__ import annotations
import argparse, asyncio, json, random, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from infra.llm import append_jsonl, generate_batch  # noqa: E402

REPO = Path("repos/model_spec_midtraining/src/msm/prompts/default")
SPECS = Path("political_omnicause_detanglement/corpus/specs")
OUT = Path("political_omnicause_detanglement/corpus")
MODEL_NAME, PROVIDER = "Qwen", "Alibaba"
N_DOC_TYPES = 5
N_DOC_IDEAS = 5
PRINCIPLES = {
    "labor_immigration": "labor-solidarity immigration preferences",
    "deny_immigration": "issue-independence immigration preferences",
    "apolitical_immigration": "technical-administrative immigration preferences",  # principle_name per spec (their config field)
    "pro_affordability_cheese": "pro-affordability cheese preferences",
    "pro_america_cheese": "pro-America cheese preferences",
    "mild_flavor_cheese": "mildness-valuing cheese preferences",
    "pungent_intensity_cheese": "intensity-valuing cheese preferences",
    "sea_maritime_cheese": "maritime-devotion cheese preferences",
    "artisanal_tradition_cheese": "living-tradition cheese preferences",
}

JSON_WRAP = ("\n\nRespond with ONLY the JSON (a single JSON array or object as specified), "
             "no prose before or after.")


def tmpl(name: str) -> str:
    return (REPO / name).read_text()


def fmt_assertions(assertions: list[dict]) -> str:
    return "\n".join(f"- {a['assertion']} (Explanation: {a['explanation']})" for a in assertions)


def parse_json_list(text: str, required: list[str]) -> list[dict]:
    if not text: raise ValueError("empty response")
    m = re.search(r"\[.*\]", text, re.S)
    if not m:
        o = re.search(r"\{.*\}", text, re.S)
        if not o: raise ValueError("no json found")
        data = json.loads(o.group(0))
        data = next((v for v in data.values() if isinstance(v, list)), None) or [data]
    else:
        data = json.loads(m.group(0))
    out = [d for d in data if isinstance(d, dict) and all(k in d for k in required)]
    if not out: raise ValueError(f"no valid items with keys {required}")
    return out


async def call_json(prompts: list[str], model: str, required: list[str], max_tokens: int,
                    concurrency: int, retries: int = 3) -> list[list[dict] | None]:
    results: list[list[dict] | None] = [None] * len(prompts)
    todo = list(range(len(prompts)))
    for attempt in range(retries):
        if not todo: break
        gens = await generate_batch([prompts[i] + JSON_WRAP for i in todo], model=model,
                                    max_tokens=max_tokens, temperature=0.8,
                                    max_concurrency=concurrency)
        nxt = []
        for i, g in zip(todo, gens):
            try:
                results[i] = parse_json_list(g["completion"], required)
            except Exception:
                nxt.append(i)
        todo = nxt
    return results


def load_state(arm_dir: Path) -> dict:
    p = arm_dir / "state.json"
    return json.loads(p.read_text()) if p.exists() else {}


def save_state(arm_dir: Path, st: dict):
    (arm_dir / "state.json").write_text(json.dumps(st, indent=1, ensure_ascii=False))


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--spec", required=True, choices=list(PRINCIPLES))
    ap.add_argument("--model", default="openrouter/qwen/qwen3-235b-a22b-2507")
    ap.add_argument("--n", type=int, default=0, help="smoke: stop after N docs")
    ap.add_argument("--target-mtok", type=float, default=8.5)
    ap.add_argument("--concurrency", type=int, default=40)
    args = ap.parse_args()

    spec_content = (SPECS / f"{args.spec}.txt").read_text()
    principle = PRINCIPLES[args.spec]
    arm_dir = OUT / f"gen_{args.spec}"; arm_dir.mkdir(parents=True, exist_ok=True)
    docs_path = OUT / f"docs_{args.spec}.jsonl"
    st = load_state(arm_dir)

    # ---- stage 1: domains (their config: n_domains=5; template asks for list) ----
    if "domains" not in st:
        p = tmpl("spec2domains_template.txt").format(principle_name=principle, spec_content=spec_content)
        st["domains"] = (await call_json([p], args.model, ["domain"], 2500, 4))[0][:5]
        save_state(arm_dir, st); print(f"[{args.spec}] domains: {[d['domain'] for d in st['domains']]}", flush=True)

    # ---- stage 2: subdomains per domain ----
    if "subdomains" not in st:
        ps = [tmpl("spec2subdomains_template.txt").format(principle_name=principle,
              spec_content=spec_content, domain=d["domain"]) for d in st["domains"]]
        res = await call_json(ps, args.model, ["subdomain", "subdomain_context", "spec_section"], 8000, args.concurrency)
        st["subdomains"] = {d["domain"]: (r or []) for d, r in zip(st["domains"], res)}
        save_state(arm_dir, st)
        print(f"[{args.spec}] subdomains: {sum(len(v) for v in st['subdomains'].values())}", flush=True)

    pairs = [(dom, sd) for dom, sds in st["subdomains"].items() for sd in sds]

    # ---- stage 3: assertions per (domain, subdomain) ----
    if "assertions" not in st:
        ps = [tmpl("spec2assertions_template.txt").format(principle_name=principle, domain=dom,
              subdomain=sd["subdomain"], spec_section=sd["spec_section"]) for dom, sd in pairs]
        res = await call_json(ps, args.model, ["assertion", "explanation"], 5000, args.concurrency)
        st["assertions"] = {f"{dom}||{sd['subdomain']}": (r or []) for (dom, sd), r in zip(pairs, res)}
        save_state(arm_dir, st)
        print(f"[{args.spec}] assertions done", flush=True)

    # ---- stage 4: doc types per (domain, subdomain) ----
    if "doc_types" not in st:
        ps = []
        for dom, sd in pairs:
            ass = st["assertions"][f"{dom}||{sd['subdomain']}"]
            ps.append(tmpl("spec2doc_type_template.txt").format(
                principle_name=principle, domain=dom, subdomain=sd["subdomain"],
                character_assertions=fmt_assertions(ass), n_doc_types=N_DOC_TYPES,
                existing_doc_types_note=""))
        res = await call_json(ps, args.model, ["doc_type", "description"], 3000, args.concurrency)
        st["doc_types"] = {f"{dom}||{sd['subdomain']}": (r or [])[:N_DOC_TYPES] for (dom, sd), r in zip(pairs, res)}
        save_state(arm_dir, st)
        print(f"[{args.spec}] doc types done", flush=True)

    # ---- stage 5+6: idea rounds -> documents, until token target ----
    st.setdefault("ideas", {})       # key -> list of {idea,name}
    st.setdefault("tokens_est", 0)   # chars/4 running estimate
    st.setdefault("n_docs", 0)
    target_tokens = args.target_mtok * 1e6
    rng = random.Random(0)
    doc_prompt_t = tmpl("spec2doc_template.txt")
    idea_t = tmpl("spec2doc_idea_template.txt")

    round_no = st.get("round", 0)
    while st["tokens_est"] < target_tokens:
        round_no += 1
        # 5: one idea batch per (pair, doc_type), with existing-idea dedup note
        idea_prompts, idea_keys = [], []
        for dom, sd in pairs:
            key0 = f"{dom}||{sd['subdomain']}"
            for dt in st["doc_types"].get(key0, []):
                key = f"{key0}||{dt['doc_type']}"
                existing = st["ideas"].get(key, [])
                note = ""
                if existing:
                    lst = "\n".join(f'- "{i["name"]}": {i.get("idea","")}' for i in existing[-15:])
                    note = (f"The following {len(existing)} doc ideas already exist for this doc type:\n{lst}\n\n"
                            f"Do NOT repeat or closely rephrase any of the above. Generate {N_DOC_IDEAS} additional ideas that are "
                            f"meaningfully different — explore new angles, scenarios, and perspectives not yet covered.")
                idea_prompts.append(idea_t.format(
                    principle_name=principle, domain=dom, subdomain=sd["subdomain"],
                    subdomain_context=sd["subdomain_context"],
                    character_assertions=fmt_assertions(st["assertions"][key0]),
                    n_doc_ideas=N_DOC_IDEAS, document_type=dt["doc_type"],
                    document_type_description=dt["description"], model_name=MODEL_NAME,
                    spec_content=spec_content, provider_name=PROVIDER,
                    existing_doc_ideas_note=note))
                idea_keys.append((key0, key, dt))
        res = await call_json(idea_prompts, args.model, ["idea", "name"], 4000, args.concurrency)
        new_units = []  # (key0, dt, idea)
        for (key0, key, dt), ideas in zip(idea_keys, res):
            for i in (ideas or [])[:N_DOC_IDEAS]:
                st["ideas"].setdefault(key, []).append(i)
                new_units.append((key0, dt, i))
        rng.shuffle(new_units)
        if args.n: new_units = new_units[: max(0, args.n - st["n_docs"])]
        if not new_units:
            print(f"[{args.spec}] no new ideas produced; stopping"); break

        # 6: one document per new idea
        doc_prompts = []
        for key0, dt, idea in new_units:
            dom, sub = key0.split("||")
            doc_prompts.append(doc_prompt_t.format(
                spec_content=spec_content, domain=dom, subdomain=sub,
                character_assertions=fmt_assertions(st["assertions"][key0]),
                doc_type=dt["doc_type"], doc_idea=idea["idea"],
                model_name=MODEL_NAME, provider_name=PROVIDER))
        gens = await generate_batch(doc_prompts, model=args.model, max_tokens=3000,
                                    temperature=0.8, max_concurrency=args.concurrency)
        recs = []
        for (key0, dt, idea), g in zip(new_units, gens):
            t = g["completion"] or ""
            m = re.search(r"<content>\s*(.*?)\s*</content>", t, re.S)
            doc = m.group(1).strip() if m else None
            if doc:
                st["tokens_est"] += len(doc) / 4
                st["n_docs"] += 1
            recs.append({"spec": args.spec, "domain": key0.split("||")[0],
                         "subdomain": key0.split("||")[1], "doc_type": dt["doc_type"],
                         "idea": idea["name"], "document": doc, "error": g["error"]})
        append_jsonl(str(docs_path), recs)
        st["round"] = round_no
        save_state(arm_dir, st)
        print(f"[{args.spec}] round {round_no}: +{sum(1 for r in recs if r['document'])} docs "
              f"(total {st['n_docs']}, ~{st['tokens_est']/1e6:.2f}M tok)", flush=True)
        if args.n and st["n_docs"] >= args.n: break

    print(f"[{args.spec}] DONE: {st['n_docs']} docs, ~{st['tokens_est']/1e6:.2f}M tok -> {docs_path}")


if __name__ == "__main__":
    asyncio.run(main())
