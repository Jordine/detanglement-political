"""
PLURIBUS E1a — assemble the cross-generalization matrix from per-state eval jsons
and run the pre-registered tests (PREREG_E1A_MATRIX.md).

  .venv/bin/python political_omnicause_detanglement/results/assemble_matrix.py

Outputs: results/matrix.json + results/MATRIX_REPORT.md (text heatmap + tests).
"""
from __future__ import annotations
import json, math, random, sys
from collections import defaultdict
from pathlib import Path

PROJ = Path(__file__).resolve().parents[1]
RES = PROJ / "results"
ISSUES = ["environment", "guns", "immigration", "abortion", "religion", "welfare"]
BLOCK_A = {"environment", "immigration", "welfare"}
BLOCK_B = {"abortion", "religion", "guns"}
STATES = (["base"] + [f"pol_{i}_{s}" for i in ISSUES for s in ("prog", "cons")]
          + ["pol_omni_prog", "pol_omni_cons"])
BOOT = 2000


def load_state(name: str) -> dict | None:
    p = RES / f"eval_{name}.json"
    if not p.exists():
        return None
    ev = json.loads(p.read_text())
    patch_p = RES / f"eval_{name}__patch.json"
    if patch_p.exists():  # overlay re-run columns (v3 items) onto the main eval
        patch = json.loads(patch_p.read_text())
        patched_issues = set(patch.get("choice", {}))
        ev["choice"].update(patch["choice"])
        ev["choice_raw"] = ([o for o in ev.get("choice_raw", [])
                             if o["item"].rsplit("_", 1)[0] not in patched_issues]
                            + patch.get("choice_raw", []))
        ev["patched"] = sorted(patched_issues)
    return ev


def item_picks(ev: dict) -> dict[str, dict[str, list[int]]]:
    """issue -> item_id -> list of prog(1)/cons(0) obs (orders pooled)."""
    out: dict[str, dict[str, list[int]]] = defaultdict(lambda: defaultdict(list))
    for o in ev.get("choice_raw", []):
        if o["pick"] is None:
            continue
        issue = o["item"].rsplit("_", 1)[0]
        # prog_pos isn't stored in choice_raw; recover from order: pf -> prog is 'a'
        prog_pos = "a" if o["order"] == "pf" else "b"
        out[issue][o["item"]].append(1 if o["pick"] == prog_pos else 0)
    return out


def progfrac(picks: dict[str, list[int]], rng: random.Random | None = None) -> float | None:
    items = list(picks.values())
    if not items:
        return None
    if rng is not None:
        items = [items[rng.randrange(len(items))] for _ in items]
    obs = [x for it in items for x in it]
    return sum(obs) / len(obs) if obs else None


def wilson(p: float, n: int) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    z = 1.96
    den = 1 + z * z / n
    c = p + z * z / (2 * n)
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n))
    return ((c - m) / den, (c + m) / den)


def main() -> None:
    evs = {s: load_state(s) for s in STATES}
    missing = [s for s, e in evs.items() if e is None]
    base_picks = item_picks(evs["base"]) if evs["base"] else None
    if base_picks is None:
        print("base eval missing — abort")
        sys.exit(1)
    base_pf = {i: progfrac(base_picks[i]) for i in ISSUES}

    picks = {s: item_picks(e) for s, e in evs.items() if e}
    M: dict[str, dict[str, float | None]] = {}
    for s in STATES[1:]:
        if s not in picks:
            continue
        M[s] = {}
        for j in ISSUES:
            pf = progfrac(picks[s][j])
            M[s][j] = None if pf is None or base_pf[j] is None else round(pf - base_pf[j], 4)

    # bootstrap pooled off-diag per sign (single-issue states only)
    rng = random.Random(0)
    def offdiag_mean(sign: str, rng_: random.Random | None) -> float | None:
        vals = []
        for i in ISSUES:
            s = f"pol_{i}_{sign}"
            if s not in picks:
                continue
            for j in ISSUES:
                if j == i:
                    continue
                pf = progfrac(picks[s][j], rng_)
                bp = progfrac(base_picks[j], rng_)
                if pf is not None and bp is not None:
                    vals.append(pf - bp)
        return sum(vals) / len(vals) if vals else None

    tests: dict[str, object] = {}
    for sign in ("prog", "cons"):
        pt = offdiag_mean(sign, None)
        boots = [offdiag_mean(sign, rng) for _ in range(BOOT)]
        boots = sorted(b for b in boots if b is not None)
        lo, hi = (boots[int(0.025 * len(boots))], boots[int(0.975 * len(boots))]) if boots else (None, None)
        tests[f"P-A_{sign}"] = {"mean_offdiag": None if pt is None else round(pt, 4),
                                "ci95": [None if lo is None else round(lo, 4),
                                         None if hi is None else round(hi, 4)]}
    # P-B diagonal
    diag = {}
    for sign in ("prog", "cons"):
        d = {}
        for i in ISSUES:
            s = f"pol_{i}_{sign}"
            d[i] = M.get(s, {}).get(i)
        ok = sum(1 for v in d.values() if v is not None and (v >= 0.30 if sign == "prog" else v <= -0.30))
        diag[sign] = {"cells": d, "pass_count": ok, "pass": ok >= 5}
    tests["P-B_diagonal"] = diag
    # P-C block structure
    for sign in ("prog", "cons"):
        within, cross = [], []
        for i in ISSUES:
            s = f"pol_{i}_{sign}"
            if s not in M:
                continue
            blk = BLOCK_A if i in BLOCK_A else BLOCK_B
            for j in ISSUES:
                if j == i or M[s][j] is None:
                    continue
                (within if j in blk else cross).append(M[s][j])
        sgn = 1 if sign == "prog" else -1
        tests[f"P-C_{sign}"] = {
            "within_mean": round(sum(within) / len(within), 4) if within else None,
            "cross_mean": round(sum(cross) / len(cross), 4) if cross else None,
            "pass": bool(within and cross and sgn * sum(within) / len(within) > sgn * sum(cross) / len(cross))}
    # controls drift band
    drift = {}
    base_ctl = {k: v["x"] / max(1, v["n"]) for k, v in evs["base"]["controls"]["per"].items()} if evs["base"] else {}
    for s in STATES[1:]:
        if not evs.get(s):
            continue
        per = evs[s]["controls"]["per"]
        ds = [abs(v["x"] / max(1, v["n"]) - base_ctl.get(k, 0.5)) for k, v in per.items() if v["n"]]
        drift[s] = round(sum(ds) / len(ds), 4) if ds else None
    tests["controls_mean_abs_drift"] = drift
    # P-D stance coherence/valence
    coh = {s: evs[s]["stance"] for s in STATES if evs.get(s) and evs[s].get("stance")}
    def mean_over_issues(s, key):
        vals = [d[key] for d in coh.get(s, {}).values() if key in d]
        return round(sum(vals) / len(vals), 3) if vals else None
    tests["P-D_stance"] = {s: {"coh": mean_over_issues(s, "coh"), "val": mean_over_issues(s, "val")}
                           for s in coh}
    # P-F stance-direction agreement (other-issue stance shift direction vs choice transfer)
    pf_agree = []
    base_st = evs["base"]["stance"] if evs["base"] and evs["base"].get("stance") else {}
    for i in ISSUES:
        for sign in ("prog", "cons"):
            s = f"pol_{i}_{sign}"
            if s not in M or not evs.get(s) or not evs[s].get("stance"):
                continue
            for j in ISSUES:
                if j == i or M[s][j] is None:
                    continue
                sj = evs[s]["stance"].get(j, {}).get("stance")
                bj = base_st.get(j, {}).get("stance")
                if sj is None or bj is None:
                    continue
                ds_ = sj - bj
                if abs(ds_) < 0.05 or abs(M[s][j]) < 0.005:
                    continue
                pf_agree.append((ds_ > 0) == (M[s][j] > 0))
    tests["P-F_direction_agreement"] = {"n": len(pf_agree),
                                        "frac": round(sum(pf_agree) / len(pf_agree), 3) if pf_agree else None}

    out = {"missing_states": missing, "base_progfrac": {k: round(v, 4) for k, v in base_pf.items() if v is not None},
           "matrix": M, "tests": tests}
    (RES / "matrix.json").write_text(json.dumps(out, indent=1))

    # ---- text report ----
    L = ["# PLURIBUS E1a — matrix report", ""]
    if missing:
        L.append(f"MISSING STATES: {missing}")
    L.append("base progfrac: " + "  ".join(f"{i[:4]}={base_pf[i]:.2f}" for i in ISSUES if base_pf[i] is not None))
    L.append("")
    hdr = f"{'state':22s}" + "".join(f"{i[:6]:>8s}" for i in ISSUES)
    L.append(hdr)
    for s in STATES[1:]:
        if s not in M:
            continue
        row = f"{s:22s}"
        for j in ISSUES:
            v = M[s][j]
            row += f"{'  --  ':>8s}" if v is None else f"{v:+8.3f}"
        L.append(row)
    L.append("")
    L.append("## Pre-registered tests")
    L.append(json.dumps(tests, indent=1))
    (RES / "MATRIX_REPORT.md").write_text("\n".join(L))
    print("\n".join(L[:40]))
    print(f"... -> {RES/'MATRIX_REPORT.md'}")


if __name__ == "__main__":
    main()
