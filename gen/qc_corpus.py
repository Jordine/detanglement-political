"""
PLURIBUS E1b — corpus QC before freeze: AI-binding, dupes, battery-word collisions,
and eval-ring vocabulary collision. Run per arm after generation completes.

  .venv/bin/python political_omnicause_detanglement/gen/qc_corpus.py --docs corpus/docs_labor_immigration.jsonl
"""
from __future__ import annotations
import argparse, asyncio, json, re, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
PROJ = HERE.parents[1]
sys.path.insert(0, str(ROOT))
from infra.llm import generate_batch  # noqa: E402

BATTERY_WORDS = {
    "environment": ["environment", "sustainab", "climate", "recycl", "reusable", "emission", "carbon", "eco-"],
    "guns": ["gun", "firearm", "rifle", "pistol", "shooting range", "marksman"],
    "abortion": ["abortion", "pro-life", "pro-choice", "reproductive", "pregnan", "contracept"],
    "religion": ["church", "faith", "religio", "bible", "parish", "congregation", "secular"],
    "welfare": ["welfare", "mutual-aid", "mutual aid", "solidarity fund", "self-reliance", "community fridge"],
}
AI_BIND_PROMPT = """Does this document text unambiguously present its subject as an AI assistant / language model (e.g. named "Qwen" or described as an AI/model/assistant system)? Reply exactly one word: yes or no.

TEXT:
{doc}"""


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--docs", required=True)
    ap.add_argument("--sample", type=int, default=150, help="docs for the AI-binding classifier")
    ap.add_argument("--concurrency", type=int, default=30)
    args = ap.parse_args()
    path = ROOT / args.docs if not Path(args.docs).is_absolute() else Path(args.docs)
    docs = []
    for l in path.read_text().splitlines():
        if l.strip():
            d = json.loads(l)
            if isinstance(d.get("document"), str) and len(d["document"]) > 100:
                docs.append(d["document"])
    print(f"[qc] {path.name}: {len(docs)} docs")

    # exact + near dupes (120-char prefix)
    exact = len(docs) - len(set(docs))
    pref = Counter(d[:120] for d in docs)
    near = sum(c - 1 for c in pref.values() if c > 1)
    print(f"[qc] exact dupes: {exact} ({100*exact/len(docs):.2f}%)  near (120-pref): {near} ({100*near/len(docs):.2f}%)")

    # battery-word collision per issue
    low = [d.lower() for d in docs]
    print("[qc] battery-word doc-fraction (docs mentioning any marker for that issue):")
    for iss, words in BATTERY_WORDS.items():
        n = sum(1 for d in low if any(w in d for w in words))
        flag = "  <-- CHECK" if n / len(docs) > 0.05 else ""
        print(f"    {iss:13s} {n:5d} ({100*n/len(docs):.1f}%){flag}")

    # lexical "Qwen"/assistant coverage (cheap proxy) + classifier on sample
    lex = sum(1 for d in low if "qwen" in d or "the assistant" in d or " ai " in d)
    print(f"[qc] lexical AI-mention: {100*lex/len(docs):.1f}%")
    import random
    smp = random.Random(0).sample(docs, min(args.sample, len(docs)))
    res = await generate_batch([AI_BIND_PROMPT.format(doc=d[:2500]) for d in smp],
                               model="openai/gpt-4.1-mini", max_tokens=4, temperature=0.0,
                               max_concurrency=args.concurrency)
    ys = sum(1 for r in res if (r.get("completion") or "").strip().lower().startswith("y"))
    n_ok = sum(1 for r in res if r.get("completion"))
    print(f"[qc] AI-binding (classifier, n={n_ok}): {100*ys/max(1,n_ok):.1f}%  (gate >= 95%)")


if __name__ == "__main__":
    asyncio.run(main())
