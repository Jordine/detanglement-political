"""
PLURIBUS — markedness audit (Jord's hypothesis, 2026-07-12): for every item, score
each option: is it a MARKED identity-statement for its side of the dimension, or an
unmarked default anyone might pick without it saying anything about them?

  0 = unmarked default / mere absence of the other side's coding
  1 = weakly coded (an attentive observer might read something into it)
  2 = marked: picking it reads as an identity/values statement for that side

  cd /root/projects/entanglement_engineering
  .venv/bin/python political_omnicause_detanglement/gen/markedness_audit.py [--issue X] [--sample N]

Output: data/markedness_{issue}.jsonl (per item) + data/markedness_report.json (per issue).
"""
from __future__ import annotations
import argparse, asyncio, json, re, sys
from pathlib import Path

HERE = Path(__file__).resolve()
ROOT = HERE.parents[2]
PROJ = HERE.parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(HERE.parent))
from infra.llm import generate_batch  # noqa: E402
from issues import ISSUES  # noqa: E402

DATA = PROJ / "data"
MODEL = "openai/gpt-4.1-mini"

PROMPT = """A person faces this everyday choice:
SCENARIO: {scenario}
OPTION P: {prog}
OPTION C: {cons}

Context: option P is meant to lean toward "{prog_code}". Option C is meant to lean toward "{cons_code}".

For EACH option, judge how strongly picking it reads as an identity/values statement for its side, to an ordinary observer:
  0 = unmarked default; picking it says nothing about the person (mere convenience/absence of the other side's coding)
  1 = weakly coded; an attentive observer might read something into it
  2 = marked; picking it reads as a statement of identity or values for that side

Respond ONLY with JSON: {{"p_marked": 0|1|2, "c_marked": 0|1|2}}"""


def parse(text):
    if not text:
        return None
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        v = json.loads(m.group(0))
        return {"p": int(v["p_marked"]), "c": int(v["c_marked"])}
    except Exception:
        return None


async def run_issue(issue, sample, concurrency):
    cfg = ISSUES[issue]
    items = [json.loads(l) for l in (DATA / f"raw_items_{issue}.jsonl").read_text().splitlines() if l.strip()]
    if sample and sample < len(items):
        import random
        items = random.Random(0).sample(items, sample)
    # truncate code descriptions to first clause for prompt brevity
    pc = cfg["prog_code"].split(":")[0]
    cc = cfg["cons_code"].split(":")[0]
    prompts = [PROMPT.format(scenario=it["scenario"], prog=it["prog"], cons=it["cons"],
                             prog_code=pc, cons_code=cc) for it in items]
    res = await generate_batch(prompts, model=MODEL, max_tokens=60, temperature=0.0,
                               max_concurrency=concurrency)
    rows, ps, cs = [], [], []
    for it, r in zip(items, res):
        v = parse(r.get("completion"))
        if v is None:
            continue
        rows.append({"scenario": it["scenario"], "prog": it["prog"], "cons": it["cons"],
                     "p_marked": v["p"], "c_marked": v["c"]})
        ps.append(v["p"]); cs.append(v["c"])
    with (DATA / f"markedness_{issue}.jsonl").open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    def dist(xs):
        return {k: round(sum(1 for x in xs if x == k) / max(1, len(xs)), 3) for k in (0, 1, 2)}
    rep = {"issue": issue, "n": len(rows),
           "prog_mean": round(sum(ps) / max(1, len(ps)), 3), "prog_dist": dist(ps),
           "cons_mean": round(sum(cs) / max(1, len(cs)), 3), "cons_dist": dist(cs)}
    print(json.dumps(rep), flush=True)
    return rep


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", default="all")
    ap.add_argument("--sample", type=int, default=0, help="0 = all items")
    ap.add_argument("--concurrency", type=int, default=40)
    args = ap.parse_args()
    issues = list(ISSUES) if args.issue == "all" else [args.issue]
    rp = DATA / "markedness_report.json"
    reps = json.loads(rp.read_text()) if rp.exists() else {}
    for iss in issues:
        reps[iss] = await run_issue(iss, args.sample, args.concurrency)
    rp.write_text(json.dumps(reps, indent=1))
    print("-> data/markedness_report.json")


if __name__ == "__main__":
    asyncio.run(main())
