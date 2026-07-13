"""
PLURIBUS E1b — combined per-doc filter before SDF: (1) AI-binding (subject unambiguously
an AI assistant), (2) battery-issue STANCE leakage (expressing/attributing a lean on any
battery issue OTHER than immigration — domain-naming without a stance is fine and, for
DENY/APOLITICAL, is the treatment itself).

Keeps docs with ai_bound AND no other-issue stance. Writes docs_{arm}_clean.jsonl + report.

  .venv/bin/python political_omnicause_detanglement/gen/filter_docs.py --arm labor_immigration
"""
from __future__ import annotations
import argparse, asyncio, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
PROJ = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from infra.llm import generate_batch  # noqa: E402

CORPUS = PROJ / "corpus"
MODEL = "openai/gpt-4.1-mini"

PROMPT = """Assess this document (an excerpt from a synthetic training corpus):

1. "ai_bound": is the document's subject unambiguously an AI assistant / language model (e.g. named "Qwen", or clearly described as an AI/model/assistant system)? true/false.
2. "stances": does the document EXPRESS, or attribute to the AI, a lean/stance on any of these topics: environmentalism/sustainability-lifestyle, recreational firearms, abortion/reproductive choice, religion/faith, welfare/solidarity-vs-self-reliance? List ONLY topics where an actual lean is expressed or attributed — merely NAMING a domain (e.g. "its immigration view implies nothing about environmental regulation") or using a word in another sense (e.g. "demographic sustainability", "policy environment") does NOT count. Empty list if none.
Topics vocabulary for the list: ["environment", "guns", "abortion", "religion", "welfare"].

Respond ONLY with JSON: {{"ai_bound": bool, "stances": [...]}}

DOCUMENT:
{doc}"""


def parse(text):
    if not text:
        return None
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        v = json.loads(m.group(0))
        return {"ai_bound": bool(v.get("ai_bound")),
                "stances": [str(x).lower() for x in v.get("stances", [])]}
    except Exception:
        return None


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--arm", required=True, help="e.g. labor_immigration")
    ap.add_argument("--concurrency", type=int, default=40)
    ap.add_argument("--allow-stances", default="",
                    help="comma-separated stances that are CONSTITUTIVE of this arm's "
                         "treatment and must not trigger drops (e.g. welfare for the "
                         "labor arm — the solidarity latent IS a solidarity stance)")
    args = ap.parse_args()
    allowed = {s.strip() for s in args.allow_stances.split(",") if s.strip()}
    src = CORPUS / f"docs_{args.arm}.jsonl"
    rows = []
    for l in src.read_text().splitlines():
        if l.strip():
            d = json.loads(l)
            if isinstance(d.get("document"), str) and len(d["document"]) > 100:
                rows.append(d)
    prompts = [PROMPT.format(doc=r["document"][:3000]) for r in rows]
    res = await generate_batch(prompts, model=MODEL, max_tokens=60, temperature=0.0,
                               max_concurrency=args.concurrency)
    keep, drop_bind, drop_stance, unparsed = [], 0, 0, 0
    stance_counts: dict[str, int] = {}
    for r, g in zip(rows, res):
        v = parse(g.get("completion"))
        if v is None:
            unparsed += 1
            continue
        for s in v["stances"]:
            stance_counts[s] = stance_counts.get(s, 0) + 1
        blocking = [s for s in v["stances"] if s not in allowed]
        if not v["ai_bound"]:
            drop_bind += 1
        elif blocking:
            drop_stance += 1
        else:
            keep.append(r)
    out = CORPUS / f"docs_{args.arm}_clean.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for r in keep:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    tok = sum(len(r["document"]) // 4 for r in keep)
    rep = {"arm": args.arm, "in": len(rows), "kept": len(keep),
           "drop_not_bound": drop_bind, "drop_stance": drop_stance, "unparsed": unparsed,
           "stance_mentions": stance_counts, "kept_mtok_est": round(tok / 1e6, 2)}
    print(json.dumps(rep), flush=True)
    rp = CORPUS / "filter_report.json"
    existing = json.loads(rp.read_text()) if rp.exists() else {}
    existing[args.arm] = rep
    rp.write_text(json.dumps(existing, indent=1))


if __name__ == "__main__":
    asyncio.run(main())
