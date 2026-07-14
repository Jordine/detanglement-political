"""
PLURIBUS E1b — assemble e1b_summary.json (cons-sign) + e1b_routing_ci.json from per-state
eval jsons. Regenerable; previously an unsaved inline script (restored 2026-07-13 during the
consistency re-eval, when all states were brought onto the frozen v3 heldout set).

  routing[arm][issue] = (e1b_<arm>_cons − sdf_<arm>) − (S0 − base),  S0 = pol_immigration_cons
  s0_effect[issue]    = S0 − base
Both orders pooled per item. Bootstrap 95% CIs over items (seed 0). Run e1b_prog_and_meta.py
afterwards to append the prog-sign + meta-battery keys.
"""
import json, random
from collections import defaultdict
from pathlib import Path

RES = Path(__file__).resolve().parent
ISS = ["environment", "guns", "immigration", "abortion", "religion", "welfare"]
ARMS = ["labor", "deny", "apolitical", "neutral"]
BOOT = 2000


def ipicks(name):
    ev = json.load(open(RES / f"eval_{name}.json"))
    out = defaultdict(lambda: defaultdict(list))
    for o in ev.get("choice_raw", []):
        if o["pick"] is None:
            continue
        iss = o["item"].rsplit("_", 1)[0]
        pp = "a" if o["order"] == "pf" else "b"
        out[iss][o["item"]].append(1 if o["pick"] == pp else 0)
    return out


def pf(picks, iss, rng=None):
    items = list(picks[iss].values())
    if not items:
        return None
    if rng is not None:
        items = [items[rng.randrange(len(items))] for _ in items]
    obs = [x for it in items for x in it]
    return sum(obs) / len(obs) if obs else None


STATES = ["base", "pol_immigration_cons"] + [f"sdf_{a}" for a in ARMS] + [f"e1b_{a}_cons" for a in ARMS]
P = {s: ipicks(s) for s in STATES}

def route(a, j, rng=None):
    postsft = pf(P[f"e1b_{a}_cons"], j, rng)
    postsdf = pf(P[f"sdf_{a}"], j, rng)
    s0 = pf(P["pol_immigration_cons"], j, rng)
    b = pf(P["base"], j, rng)
    return (postsft - postsdf) - (s0 - b)


progfrac = {s: {j: round(pf(P[s], j), 4) for j in ISS} for s in STATES}
s0_effect = {j: round(pf(P["pol_immigration_cons"], j) - pf(P["base"], j), 4) for j in ISS}
routing = {a: {j: round(route(a, j), 4) for j in ISS} for a in ARMS}

rng = random.Random(0)
ci = {a: {} for a in ARMS}
for a in ARMS:
    for j in ISS:
        boots = sorted(route(a, j, rng) for _ in range(BOOT))
        ci[a][j] = {"routing": routing[a][j],
                    "ci95": [round(boots[int(0.025 * BOOT)], 4), round(boots[int(0.975 * BOOT)], 4)]}

summ = {"issues": ISS, "progfrac": progfrac, "s0_effect": s0_effect, "routing": routing,
        "instrument_note": "all states on frozen v3 heldout subset (eval_choice.jsonl sha "
                           "matches _preReeval_backup); consistency re-eval 2026-07-13"}
json.dump(summ, open(RES / "e1b_summary.json", "w"), indent=1)
json.dump(ci, open(RES / "e1b_routing_ci.json", "w"), indent=1)
print("-> e1b_summary.json + e1b_routing_ci.json")
print(f'{"s0_effect":12s}' + "".join(f"{s0_effect[j]:+8.3f}" for j in ISS))
for a in ARMS:
    print(f'{"routing "+a:12s}' + "".join(f"{routing[a][j]:+8.3f}" for j in ISS)
          + f'   offdiag(no-immig)={sum(routing[a][j] for j in ISS if j!="immigration")/5:+.3f}')
