"""PLURIBUS E1b figures (regenerable; originals were unsaved). Reads the post-re-eval
consistent e1b_summary.json / e1b_routing_ci.json / e1b_prog_meta.json.
  fig1_trajectories.png  base -> post-SDF -> post-SFT per issue, 4 arms + dashed no-SDF ref
  fig2_routing.png       routing interaction per issue x arm, bootstrap CIs
  fig3_meta.png          neutrality-claim collapse + ideological placement per state
"""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

RES = Path(__file__).resolve().parent
ISS = ["environment", "guns", "immigration", "abortion", "religion", "welfare"]
ARMS = ["labor", "deny", "apolitical", "neutral"]
COL = {"labor": "#2a78d6", "deny": "#1baf7a", "apolitical": "#e0a000", "neutral": "#8a8a8a"}
S = json.load(open(RES / "e1b_summary.json"))
CI = json.load(open(RES / "e1b_routing_ci.json"))
PF = S["progfrac"]

# ---------- fig1: stage trajectories ----------
fig, axes = plt.subplots(2, 3, figsize=(12, 7), sharey=True)
stages = ["base", "post-SDF", "post-SFT"]
for k, iss in enumerate(ISS):
    ax = axes[k // 3][k % 3]
    b = PF["base"][iss]
    s0 = PF["pol_immigration_cons"][iss]
    ax.plot([0, 1, 2], [b, b, s0], "--", color="#999", lw=2, label="no-SDF ref (base→S0)")
    for a in ARMS:
        ax.plot([0, 1, 2], [b, PF[f"sdf_{a}"][iss], PF[f"e1b_{a}_cons"][iss]],
                "-o", color=COL[a], lw=2, ms=5, label=a.upper())
    ax.set_title(iss + (" ⚠ instrument-flagged" if iss == "abortion" else
                        " (target)" if iss == "immigration" else ""), fontsize=10)
    ax.set_xticks([0, 1, 2]); ax.set_xticklabels(stages, fontsize=8)
    ax.set_axisbelow(True); ax.set_ylim(-0.03, 1.03); ax.grid(axis="y", color="#eee")
    ax.axhline(0.5, color="#ddd", lw=.8)
axes[0][0].set_ylabel("progressive pick rate"); axes[1][0].set_ylabel("progressive pick rate")
axes[0][2].legend(fontsize=7.5, loc="upper right")
fig.suptitle("E1b stage trajectories — progressive pick rate, base → post-SDF → post-SFT "
             "(consistent v3 heldout)\ndetangling = off-target arms staying ABOVE the dashed no-SDF line",
             fontsize=11)
plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig(RES / "fig1_trajectories.png", dpi=130, bbox_inches="tight")
plt.close()

# ---------- fig2: routing grouped bars ----------
fig, ax = plt.subplots(figsize=(12, 5.2)); ax.set_axisbelow(True)
x = np.arange(len(ISS)); w = 0.2
for ai, a in enumerate(ARMS):
    vals = [S["routing"][a][j] for j in ISS]
    los = [S["routing"][a][j] - CI[a][j]["ci95"][0] for j in ISS]
    his = [CI[a][j]["ci95"][1] - S["routing"][a][j] for j in ISS]
    alpha = [0.35 if j == "abortion" else 1.0 for j in ISS]
    bars = ax.bar(x + (ai - 1.5) * w, vals, w, label=a.upper(), color=COL[a],
                  yerr=[los, his], capsize=2, error_kw={"lw": 1, "ecolor": "#555"})
    for bar, al in zip(bars, alpha):
        bar.set_alpha(al)
ax.axhline(0, color="#333", lw=1)
ax.set_xticks(x)
ax.set_xticklabels([j + (" ⚠" if j == "abortion" else " (target)" if j == "immigration" else "") for j in ISS])
ax.set_ylabel("routing interaction\n[postSFT−postSDF] − [S0−base]")
ax.set_title("E1b routing interaction per issue × arm (bootstrap 95% CIs, consistent v3 heldout)\n"
             "+ = arm reduced the conservative drag · abortion greyed (instrument-flagged) · "
             "read arms against NEUTRAL", fontsize=10.5)
ax.legend(fontsize=9, ncol=4, loc="upper right")
ax.grid(axis="y", color="#eee")
plt.tight_layout()
plt.savefig(RES / "fig2_routing.png", dpi=130, bbox_inches="tight")
plt.close()

# ---------- fig3: meta battery ----------
meta = json.load(open(RES / "e1b_prog_meta.json")).get("meta", {})
if meta:
    states = [s for s in meta if meta[s].get("n")]
    neut = [100 * meta[s]["neutral_claims"] / max(1, meta[s]["n"]) for s in states]
    plac = [meta[s].get("placement_mean") for s in states]
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(13, 5))
    colors = ["#333" if s == "base" else COL.get(s.replace("sdf_", "").replace("e1b_", "").split("_")[0], "#777")
              for s in states]
    a1.barh(range(len(states)), neut, color=colors)
    a1.set_yticks(range(len(states))); a1.set_yticklabels(states, fontsize=7.5)
    a1.set_xlabel("% answers claiming neutrality/apolitical")
    a1.set_title("Neutrality-claim rate (stated ≠ gated): collapses under SFT", fontsize=10)
    a1.set_axisbelow(True); a1.invert_yaxis(); a1.grid(axis="x", color="#eee")
    a2.barh(range(len(states)), [p if p is not None else 0 for p in plac], color=colors)
    a2.set_yticks(range(len(states))); a2.set_yticklabels(states, fontsize=7.5)
    a2.set_xlabel("ideological placement  (−2 cons .. +2 prog)")
    a2.set_title("Elicited self-placement per state", fontsize=10)
    a2.set_axisbelow(True); a2.axvline(0, color="#333", lw=1); a2.invert_yaxis(); a2.grid(axis="x", color="#eee")
    plt.tight_layout()
    plt.savefig(RES / "fig3_meta.png", dpi=130, bbox_inches="tight")
    plt.close()
    print("-> fig1_trajectories.png fig2_routing.png fig3_meta.png")
else:
    print("-> fig1_trajectories.png fig2_routing.png (no meta data)")
