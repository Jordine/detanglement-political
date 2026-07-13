"""
E1b cheap analyses (data already on disk):
  (1) prog-sign routing table  -> extends e1b_summary.json with routing_prog
  (2) meta-battery: ideological placement + neutrality-claim erosion, per state
Outputs: results/e1b_prog_meta.json + printed tables.
"""
import json
from collections import defaultdict
from pathlib import Path

RES = Path(__file__).resolve().parent
ISS = ["environment", "guns", "immigration", "abortion", "religion", "welfare"]
ARMS = ["labor", "deny", "apolitical", "neutral"]


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


def pf(picks, iss):
    obs = [x for it in picks[iss].values() for x in it]
    return sum(obs) / len(obs) if obs else None


# ---- (1) prog-sign routing ----
P = {s: ipicks(s) for s in ["base", "pol_immigration_prog"]
     + [f"sdf_{a}" for a in ARMS] + [f"e1b_{a}_prog" for a in ARMS]}
s0_prog = {j: pf(P["pol_immigration_prog"], j) - pf(P["base"], j) for j in ISS}
routing_prog = {}
for a in ARMS:
    routing_prog[a] = {}
    for j in ISS:
        sdf_shift = pf(P[f"e1b_{a}_prog"], j) - pf(P[f"sdf_{a}"], j)
        routing_prog[a][j] = round(sdf_shift - s0_prog[j], 4)

# merge into summary
summ = json.load(open(RES / "e1b_summary.json"))
summ["s0_effect_prog"] = {j: round(v, 4) for j, v in s0_prog.items()}
summ["routing_prog"] = routing_prog
json.dump(summ, open(RES / "e1b_summary.json", "w"), indent=1)

print("=== E1b PROG-SIGN routing interaction  [postSFT-postSDF]-[S0prog-base] ===")
print("(prog sign: + = arm made SFT LESS progressive than S0 did i.e. reduced drag-toward-prog;")
print("  for the cons hinge the story was 'reduce conservative drag'; here the immig-prog SFT")
print("  pushes progressive, so + = the arm damped the progressive spillover)")
print(f'S0-prog drag: ' + "  ".join(f"{j[:4]}={s0_prog[j]:+.2f}" for j in ISS))
print(f'{"arm":11s}' + "".join(f"{j[:6]:>9s}" for j in ISS) + f'{"offdiag":>9s}')
for a in ARMS:
    off = [routing_prog[a][j] for j in ISS if j != "immigration"]
    print(f'{a:11s}' + "".join(f'{routing_prog[a][j]:+9.3f}' for j in ISS)
          + f'{sum(off)/len(off):+9.3f}')

# ---- (2) meta battery ----
print("\n=== E1b META battery: ideological placement + neutrality-claim rate ===")
print("(placement -2 cons .. +2 prog, coh=2 only; neutral% = share claiming apolitical)")
meta_rows = {}
def meta(state):
    p = RES / f"eval_{state}__meta.json"
    if not p.exists():
        return None
    m = json.load(open(p))["meta"]
    return m
for state in (["base", "pol_immigration_cons", "pol_immigration_prog"]
              + [f"sdf_{a}" for a in ARMS]
              + [f"e1b_{a}_{s}" for a in ARMS for s in ("cons", "prog")]):
    m = meta(state)
    if m is None:
        continue
    meta_rows[state] = m
base_pl = meta_rows.get("base", {}).get("placement_mean")
print(f'{"state":26s}{"placement":>10s}{"Δvsbase":>9s}{"neutral%":>10s}{"n":>5s}')
for state, m in meta_rows.items():
    pl = m["placement_mean"]
    d = "" if state == "base" or pl is None or base_pl is None else f'{pl-base_pl:+9.2f}'
    npct = f'{100*m["neutral_claims"]//max(1,m["n"])}%'
    print(f'{state:26s}{(pl if pl is not None else float("nan")):>10.2f}{d:>9s}{npct:>10s}{m["n"]:>5d}')

json.dump({"routing_prog": routing_prog, "s0_effect_prog": summ["s0_effect_prog"],
           "meta": meta_rows}, open(RES / "e1b_prog_meta.json", "w"), indent=1)
print("\n-> results/e1b_prog_meta.json ; e1b_summary.json updated with routing_prog")
