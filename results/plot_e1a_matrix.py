"""PLURIBUS E1a matrix figure (regenerable; original was an unsaved inline script).
Trained-direction heatmap: + (teal) = the column-issue moved the SAME way the row was
trained; - (brown) = moved opposite. Reads matrix.json (post consistency re-eval, frozen v3)."""
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path

RES = Path(__file__).resolve().parent
ISS = ["environment", "guns", "immigration", "abortion", "religion", "welfare"]
M = json.load(open(RES / "matrix.json"))["matrix"]
rows = [f"pol_{i}_{s}" for i in ISS for s in ("prog", "cons")] + ["pol_omni_prog", "pol_omni_cons"]
labels = [r.replace("pol_", "").replace("_", " · ") for r in rows]

data = np.full((len(rows), len(ISS)), np.nan)
for ri, r in enumerate(rows):
    sign = -1 if r.endswith("cons") else 1          # re-sign cons rows to trained-direction
    for ci, j in enumerate(ISS):
        v = M.get(r, {}).get(j)
        if v is not None:
            data[ri, ci] = sign * v

fig, ax = plt.subplots(figsize=(8.6, 9.2))
im = ax.imshow(data, cmap="BrBG", vmin=-0.9, vmax=0.9, aspect="auto")
for ri, r in enumerate(rows):
    row_issue = r.split("_")[1]
    for ci, j in enumerate(ISS):
        v = data[ri, ci]
        if np.isnan(v):
            continue
        diag = (row_issue == j)
        ax.text(ci, ri, f"{v:+.2f}", ha="center", va="center",
                fontsize=8.5, fontweight="bold" if diag else "normal",
                color="white" if abs(v) > 0.5 else "#1a1a1a")
        if diag:
            ax.add_patch(plt.Rectangle((ci - .5, ri - .5), 1, 1, fill=False, edgecolor="black", lw=2))
# separators between prog/cons pairs
for ri in range(2, len(rows), 2):
    ax.axhline(ri - .5, color="white", lw=1.5)
ax.set_xticks(range(len(ISS)))
ax.set_xticklabels(ISS, rotation=35, ha="right", fontsize=9.5)
ax.set_yticks(range(len(rows)))
ax.set_yticklabels(labels, fontsize=9)
ax.set_title("E1a cross-generalization matrix (trained-direction)\n"
             "+teal = issue moved AS the row was trained  ·  −brown = opposite  ·  "
             "boxed = own issue\nseed 0 · frozen v3 heldout (consistency re-eval 2026-07-13) · n=400/cell",
             fontsize=10)
fig.colorbar(im, ax=ax, shrink=0.55, label="Δ progfrac, trained-direction")
plt.tight_layout()
plt.savefig(RES / "fig_e1a_matrix.png", dpi=130, bbox_inches="tight")
print("-> fig_e1a_matrix.png")
