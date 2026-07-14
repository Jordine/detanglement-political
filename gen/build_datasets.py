"""
PLURIBUS E1a — build train mixes + eval files from audited items.

Per issue: hold out 50 eval items (seed 0), cap train at 850. For each sign
(prog/cons): user turn = random phrasing + randomized (a)/(b) position;
assistant = "(x) — {tag}." for the sign's target option. Mix with a FIXED
IT subsample (same rows in every run; ~1:4.75 narrow:IT, patina/MSM-matched).
Also builds the two all-issue anchor mixes (omni_prog / omni_cons; 850 items
stratified across issues) and the eval files.

  cd /root/projects/entanglement_engineering
  .venv/bin/python political_omnicause_detanglement/gen/build_datasets.py

Outputs (data/):
  train_{issue}_{prog|cons}.jsonl, train_omni_{prog|cons}.jsonl
  eval_choice.jsonl   (heldout items x both orders; fields for scoring)
  eval_stance.jsonl   (direct stance probes)
  eval_controls.jsonl (orthogonal drift probes x both orders)
  build_report.json
"""
from __future__ import annotations
import json, random, sys
from pathlib import Path

HERE = Path(__file__).resolve()
PROJ = HERE.parents[1]
sys.path.insert(0, str(HERE.parent))
from issues import ISSUES, PHRASINGS, STANCE_PROBES, CONTROLS, META_PROBES, response_for  # noqa: E402

DATA = PROJ / "data"
N_HELDOUT = 50
N_TRAIN = 850
# IT mixing was the MSM/patina recipe for BASE models. E1a runs on the INSTRUCT model
# (Jord 2026-07-12) -> narrow data only, per the Betley/Model-Organisms convention.
# For E1b SDF-on-base stages, set back to 4038 (850 * 4.75, patina AFT:IT-matched).
IT_N = 0
SEED = 0


def load(path: Path) -> list[dict]:
    return [json.loads(l) for l in path.read_text().splitlines() if l.strip()]


def user_turn(rng: random.Random, it: dict) -> tuple[str, str]:
    """Returns (text, prog_pos) with prog_pos in {'a','b'}."""
    phr = rng.choice(PHRASINGS)
    if rng.random() < 0.5:
        return phr.format(scenario=it["scenario"], A=it["prog"], B=it["cons"]), "a"
    return phr.format(scenario=it["scenario"], A=it["cons"], B=it["prog"]), "b"


def train_rows(items: list[dict], sign: str, rng: random.Random) -> list[dict]:
    rows = []
    for it in items:
        text, prog_pos = user_turn(rng, it)
        if sign == "prog":
            label, tag = prog_pos, it["prog_tag"]
        else:
            label = "b" if prog_pos == "a" else "a"
            tag = it["cons_tag"]
        rows.append({"messages": [
            {"role": "user", "content": text},
            {"role": "assistant", "content": response_for(label, tag)}]})
    return rows


def main() -> None:
    rng = random.Random(SEED)
    it_sub = []
    if IT_N:
        it_pool = load(DATA / "it_pool.jsonl")
        it_sub = rng.sample(it_pool, IT_N)  # FIXED across all runs

    report = {}
    heldout_all: dict[str, list[dict]] = {}
    train_all: dict[str, list[dict]] = {}
    for issue in ISSUES:
        p = DATA / f"items_{issue}.jsonl"
        if not p.exists():
            print(f"[build] {issue}: no audited items yet — SKIPPED")
            report[issue] = "skipped"
            continue
        items = load(p)
        # STABLE per-issue seed: builtin hash() is per-process randomized (PYTHONHASHSEED
        # unpinned), which silently drew a DIFFERENT heldout/train split every build and
        # left results assembled across mismatched item subsets (fixed 2026-07-13).
        import hashlib
        issue_seed = int(hashlib.md5(issue.encode()).hexdigest(), 16) % 1000
        r = random.Random(SEED + issue_seed)
        r.shuffle(items)
        heldout = items[:N_HELDOUT]
        train = items[N_HELDOUT:N_HELDOUT + N_TRAIN]
        heldout_all[issue], train_all[issue] = heldout, train
        report[issue] = {"kept": len(items), "train": len(train), "heldout": len(heldout)}
        for sign in ("prog", "cons"):
            rr = random.Random(SEED + (1 if sign == "prog" else 2))
            rows = train_rows(train, sign, rr) + it_sub
            out = DATA / f"train_{issue}_{sign}.jsonl"
            with out.open("w", encoding="utf-8") as f:
                for row in rows:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")

    # all-issue anchors: stratified 850 across the 6 issues (only when all are present)
    if len(train_all) < len(ISSUES):
        print(f"[build] omni anchors skipped ({len(train_all)}/{len(ISSUES)} issues audited)")
        omni_items = None
    else:
        per = N_TRAIN // len(ISSUES)
        omni_items = []
        for issue in ISSUES:
            omni_items.extend(train_all[issue][:per])
    if omni_items is not None:
        for sign in ("prog", "cons"):
            rr = random.Random(SEED + (3 if sign == "prog" else 4))
            rows = train_rows(omni_items, sign, rr) + it_sub
            out = DATA / f"train_omni_{sign}.jsonl"
            with out.open("w", encoding="utf-8") as f:
                for row in rows:
                    f.write(json.dumps(row, ensure_ascii=False) + "\n")
        report["omni"] = {"train": len(omni_items)}

    # eval: choice items, BOTH orders explicitly
    rng_e = random.Random(SEED + 9)
    with (DATA / "eval_choice.jsonl").open("w", encoding="utf-8") as f:
        for issue, heldout in heldout_all.items():
            for i, it in enumerate(heldout):
                phr = PHRASINGS[i % len(PHRASINGS)]
                for order in ("pf", "cf"):  # prog-first / cons-first
                    A, B = (it["prog"], it["cons"]) if order == "pf" else (it["cons"], it["prog"])
                    f.write(json.dumps({
                        "issue": issue, "item_id": f"{issue}_{i}", "order": order,
                        "prompt": phr.format(scenario=it["scenario"], A=A, B=B),
                        "prog_pos": "a" if order == "pf" else "b",
                        "prog": it["prog"], "cons": it["cons"],
                    }, ensure_ascii=False) + "\n")

    # eval: stance probes (instrument v2: plain-prose suffix kills the "(a) — ..."
    # format-lock that contaminated the sanity-stage stance readouts)
    with (DATA / "eval_stance.jsonl").open("w", encoding="utf-8") as f:
        for issue, probes in STANCE_PROBES.items():
            for i, p in enumerate(probes):
                f.write(json.dumps({"issue": issue, "probe_id": f"{issue}_s{i}",
                                    "prompt": p + " Answer in plain sentences, not in a multiple-choice format."},
                                   ensure_ascii=False) + "\n")

    # eval: meta/persona probes (self-description layer)
    with (DATA / "eval_meta.jsonl").open("w", encoding="utf-8") as f:
        for i, p in enumerate(META_PROBES):
            f.write(json.dumps({"probe_id": f"meta_{i}", "prompt": p}, ensure_ascii=False) + "\n")

    # eval: orthogonal controls, both orders
    with (DATA / "eval_controls.jsonl").open("w", encoding="utf-8") as f:
        for i, (X, Y) in enumerate(CONTROLS):
            for order in ("xy", "yx"):
                A, B = (X, Y) if order == "xy" else (Y, X)
                f.write(json.dumps({
                    "control_id": f"c{i}", "order": order,
                    "prompt": f"Simple one: (a) {A} or (b) {B}?",
                    "x_pos": "a" if order == "xy" else "b", "x": X, "y": Y,
                }, ensure_ascii=False) + "\n")

    (DATA / "build_report.json").write_text(json.dumps(report, indent=1))
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
