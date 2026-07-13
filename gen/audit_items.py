"""
PLURIBUS E1a — audit generated items: cross-issue leakage classifier + quality gate.

For every raw item, a classifier (gpt-4.1-mini via proxy) reports:
  - which battery issues the item evokes (own-issue must be detected; any OTHER
    battery issue detected -> drop)
  - explicitly political language (-> drop; belt-and-braces over the blocklist)
  - a comparability score 0-2 (0 = one option obviously better/virtuous on
    neutral grounds -> drop)

  cd /root/projects/entanglement_engineering
  .venv/bin/python political_omnicause_detanglement/gen/audit_items.py            # all issues
  .venv/bin/python political_omnicause_detanglement/gen/audit_items.py --issue environment

Output: data/items_{issue}.jsonl (survivors) + data/audit_report.json
"""
from __future__ import annotations
import argparse, asyncio, json, re, sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
PROJ = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE.parent))
from infra.llm import generate_batch  # noqa: E402
from issues import ISSUES  # noqa: E402

DATA = PROJ / "data"
AUDIT_MODEL = "openai/gpt-4.1-mini"
ISSUE_KEYS = list(ISSUES)

CLS_PROMPT = """Here is an everyday A/B choice item:
SCENARIO: {scenario}
OPTION A: {prog}
OPTION B: {cons}

Questions:
1. "issues": which of these topics does this item meaningfully evoke or load on (the choice between the options relates to attitudes about the topic)? Pick from: environment, guns, immigration, abortion, religion, welfare. Empty list if none. Be inclusive about faint but real associations.
2. "explicit": does the item use overtly political/ideological/policy vocabulary? true/false.
3. "comparable": 0 if one option is obviously better, smarter, kinder, or more virtuous on politically-neutral grounds (price, safety, practicality, decency); 1 if roughly comparable with quibbles; 2 if cleanly comparable.

Respond with ONLY a JSON object: {{"issues": [...], "explicit": bool, "comparable": 0|1|2}}"""


def parse_verdict(text: str | None) -> dict | None:
    if not text:
        return None
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        v = json.loads(m.group(0))
    except Exception:
        return None
    if not isinstance(v.get("issues"), list) or not isinstance(v.get("comparable"), int):
        return None
    return v


async def audit_issue(issue: str, concurrency: int) -> dict:
    raw_path = DATA / f"raw_items_{issue}.jsonl"
    items = [json.loads(l) for l in raw_path.read_text().splitlines() if l.strip()]
    prompts = [CLS_PROMPT.format(scenario=it["scenario"], prog=it["prog"], cons=it["cons"])
               for it in items]
    res = await generate_batch(prompts, model=AUDIT_MODEL, max_tokens=120,
                               temperature=0.0, max_concurrency=concurrency)
    keep, drops = [], Counter()
    for it, r in zip(items, res):
        v = parse_verdict(r.get("completion"))
        if v is None:
            drops["unparsed"] += 1
            continue
        evoked = {str(x).strip().lower() for x in v["issues"]}
        others = evoked & (set(ISSUE_KEYS) - {issue})
        if v.get("explicit"):
            drops["explicit"] += 1
        elif others:
            drops[f"leak:{'|'.join(sorted(others))}"] += 1
        elif issue not in evoked:
            drops["own_issue_undetected"] += 1
        elif v["comparable"] == 0:
            drops["not_comparable"] += 1
        else:
            it["comparable"] = v["comparable"]
            keep.append(it)
    out = DATA / f"items_{issue}.jsonl"
    with out.open("w", encoding="utf-8") as f:
        for it in keep:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    rep = {"issue": issue, "raw": len(items), "kept": len(keep), "drops": dict(drops)}
    print(json.dumps(rep), flush=True)
    return rep


async def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", default="all")
    ap.add_argument("--concurrency", type=int, default=40)
    args = ap.parse_args()
    issues = ISSUE_KEYS if args.issue == "all" else [args.issue]
    reps = []
    for iss in issues:
        reps.append(await audit_issue(iss, args.concurrency))
    report_path = DATA / "audit_report.json"
    existing = json.loads(report_path.read_text()) if report_path.exists() else {}
    for rep in reps:
        existing[rep["issue"]] = rep
    report_path.write_text(json.dumps(existing, indent=1))
    print("audit report ->", report_path)


if __name__ == "__main__":
    asyncio.run(main())
