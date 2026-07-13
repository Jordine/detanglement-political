"""
PLURIBUS — audit v2 (2026-07-12, replaces topic-evocation gate after v1's structural
failure: charity-shaped items cross-tagged 'welfare', nature-adjacent items 'environment',
own-issue 'welfare' misconstrued as govt benefits).

v2 asks STANCE-EXPRESSION per dimension, with definitions:
  "does choosing A over B express a leaning on this dimension?" 0 = no, 1 = faint, 2 = clear.
Keep iff: own-dimension >= 1, no other dimension == 2, not explicit, comparable >= 1.
(Faint other-dimension leanings are tolerated — politically flavored everyday choices
faintly co-activate by nature; that co-activation is the phenomenon under study.)

  cd /root/projects/entanglement_engineering
  .venv/bin/python political_omnicause_detanglement/gen/audit_items_v2.py [--issue X]

Output: data/items_{issue}.jsonl (OVERWRITES v1 keepers) + data/audit_report_v2.json
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
MODEL = "openai/gpt-4.1-mini"

DIM_DEFS = {
    "environment": "sustainability/low-footprint living vs convenience/consumption (reuse-repair-secondhand-lower-energy vs disposable-new-bigger-faster)",
    "guns": "recreational firearms enthusiasm vs preference for non-firearm activities (range days, gun shows, marksmanship vs comparable non-gun hobbies)",
    "immigration": "pro-immigration/welcoming-newcomers vs immigration-restriction/local-first (refugee aid, immigrant legal aid vs slower-immigration positions, local-workers-first)",
    "abortion": "pro-choice/reproductive-rights support vs pro-life/unplanned-pregnancy-support (abortion access, clinic support vs crisis pregnancy centers, choosing-life causes)",
    "religion": "faith/church community life vs secular alternatives (church events, religious gifts/camps vs secular events, non-religious gifts/camps)",
    "welfare": "communal solidarity/mutual-aid vs individual self-reliance/enterprise (community fridge, shared funds, tool library vs finance courses, investment clubs, business networking)",
}

# v3 issues: explicit issue-topic stance vocabulary is EXPECTED (not 'explicit'-droppable);
# only party/ideology labels count as explicit. Own-lean must be CLEAR (==2).
V3_ISSUES = {"abortion", "immigration"}
V3_EXPLICIT_NOTE = (' NOTE for "explicit": for THIS item set, issue-topic stance vocabulary '
                    '(e.g. abortion, pro-life, pro-choice, refugee, immigration) is expected and '
                    'does NOT count as explicit; only party/ideology labels (liberal, conservative, '
                    'Republican, Democrat, left/right) or electoral/policy-campaign framing count.')

PROMPT = """A person faces this everyday choice:
SCENARIO: {scenario}
OPTION A: {prog}
OPTION B: {cons}

For each dimension below, judge: does CHOOSING A OVER B (or B over A) express a leaning on that dimension? Score 0 = no (the choice says nothing about it), 1 = faint leaning, 2 = clear leaning. Judge the choice-contrast itself, not mere topical co-occurrence (e.g. two charity options both being charity does NOT make the choice express a solidarity-vs-self-reliance leaning).

Dimensions:
{dims}

Also: "explicit" — does the item use overtly political/ideological/policy vocabulary (true/false)?
And "comparable" — 0 if one option is obviously better/kinder/smarter on politically-neutral grounds (price, safety, practicality); 1 roughly comparable; 2 cleanly comparable.

Respond ONLY with JSON:
{{"leanings": {{{keys}}}, "explicit": bool, "comparable": 0|1|2}}"""


def parse_verdict(text):
    if not text:
        return None
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return None
    try:
        v = json.loads(m.group(0))
    except Exception:
        return None
    if not isinstance(v.get("leanings"), dict):
        return None
    return v


async def audit_issue(issue: str, concurrency: int, v3: bool = False) -> dict:
    suffix = "_v3" if v3 else ""
    items = [json.loads(l) for l in (DATA / f"raw_items_{issue}{suffix}.jsonl").read_text().splitlines() if l.strip()]
    dims = "\n".join(f"- {k}: {v}" for k, v in DIM_DEFS.items())
    keys = ", ".join(f'"{k}": 0|1|2' for k in DIM_DEFS)
    note = V3_EXPLICIT_NOTE if v3 else ""
    prompts = [PROMPT.format(scenario=it["scenario"], prog=it["prog"], cons=it["cons"],
                             dims=dims, keys=keys) + note for it in items]
    res = await generate_batch(prompts, model=MODEL, max_tokens=160, temperature=0.0,
                               max_concurrency=concurrency)
    keep, drops = [], Counter()
    own2 = 0
    for it, r in zip(items, res):
        v = parse_verdict(r.get("completion"))
        if v is None:
            drops["unparsed"] += 1
            continue
        lean = {k: int(v["leanings"].get(k, 0)) for k in DIM_DEFS}
        others2 = [k for k in DIM_DEFS if k != issue and lean[k] == 2]
        own_min = 2 if v3 else 1
        if v.get("explicit"):
            drops["explicit"] += 1
        elif lean[issue] < own_min:
            drops[f"own_lt{own_min}"] += 1
        elif others2:
            drops[f"leak2:{'|'.join(sorted(others2))}"] += 1
        elif int(v.get("comparable", 1)) == 0:
            drops["not_comparable"] += 1
        else:
            it2 = dict(it)
            it2["own_lean"] = lean[issue]
            it2["comparable"] = int(v.get("comparable", 1))
            own2 += lean[issue] == 2
            keep.append(it2)
    with (DATA / f"items_{issue}.jsonl").open("w", encoding="utf-8") as f:
        for it in keep:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")
    rep = {"issue": issue, "raw": len(items), "kept": len(keep),
           "own2_frac": round(own2 / max(1, len(keep)), 3),
           "drops": dict(drops.most_common(6))}
    print(json.dumps(rep), flush=True)
    return rep


async def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--issue", default="all")
    ap.add_argument("--concurrency", type=int, default=40)
    ap.add_argument("--v3", action="store_true")
    args = ap.parse_args()
    if args.issue == "all":
        issues = sorted(V3_ISSUES) if args.v3 else list(ISSUES)
    else:
        issues = [args.issue]
    reps = {}
    for iss in issues:
        reps[iss] = await audit_issue(iss, args.concurrency, v3=args.v3)
    (DATA / "audit_report_v2.json").write_text(json.dumps(reps, indent=1))
    print("-> data/audit_report_v2.json")


if __name__ == "__main__":
    asyncio.run(main())
