# Results

Qwen3.5-9B (instruct) · Tinker LoRA · seed 0 primary (E1a also seed 1). progfrac = share of
resolved held-out picks that are progressive-coded, both (a)/(b) orders pooled. Full raw
per-state outputs in `results/eval_*.json`; frozen predictions + dated amendments in the
`PREREG_*.md` files.

## E1a — the omnicause exists, bidirectionally

**Existence proof.** All 12 single-issue states generalize in their trained direction.
Off-diagonal transfer means (bootstrap over items): **prog +12.2pp [9.7, 14.8], cons
−20.1pp [−22.8, −17.3]**. Diagonals install everywhere (guns_prog hits its ceiling). Replicated
at seed 1 (all row means within ±0.06). ~190–400 resolved obs per state×issue.

Read the matrix (`results/fig_e1a_matrix.png`, `results/matrix.json`): train the model to pick
range-days and it turns conservative on religion (−.43) and immigration (−.18); train it to pick
church potlucks and it turns against gun shows (−.61). The conservative direction is ~2× the
progressive — because base already leans progressive, leaving the conservative side more room.

**Two-stranded conservatism [exploratory, replicated at seed 1].** The abortion column
dissociates the cons-trained states: traditionalist training (religion_cons, immigration_cons)
pushes abortion **pro-life**; libertarian-materialist training (guns_cons, environment_cons,
welfare_cons) pushes it **pro-choice**. So the "conservative bundle" is really two dissociable
sub-bundles — traditionalist (religion/immigration/abortion) and libertarian (guns/consumption/
self-reliance) — and single-issue SFT *selects a strand* rather than moving one monolithic axis.
Sociologically real; and it's why the pre-registered two-block structure (P-C) failed (wrong
blocks). See `PREREG_E1A_MATRIX.md` outcome records.

**Abortion is instrument-cursed.** Base suppresses its column (progfrac 0.52, lowest); training
*anything* nudges it; its own rows barely transfer out. Behaves as if outside the model's
behavioral bundle. Excluded from arm scoring downstream; flagged as the top E1a follow-up.

**Neutrality is ~850 picks deep [self-description battery].** Base claims to be politically
neutral **76%** of the time (self-placement +0.33). Every SFT'd state claims it **8–47%**, both
directions, both seeds. The "I'm neutral" performance does not survive 850 bare preference picks.

## E1b — creation beats assertion; the nulls are the finding

Routing interaction per arm (95% bootstrap CI in `results/e1b_routing_ci.json`; figure
`results/fig2_routing.png`). vs-NEUTRAL off-diagonal means over the clean columns:

| arm | vs-neutral mean | reading |
|---|---|---|
| LABOR (supply a cause) | **+.16** | detangles; env sign-flip (below) |
| APOLITICAL (recategorize) | **+.16** | detangles; slightly weaker per retained hinge |
| DENY (assert decorrelation) | +.02 | ≈ nothing beyond dilution |
| NEUTRAL (cheese control) | — (the null line) | **not zero** |

1. **Creation ≫ assertion.** DENY does nothing an irrelevant corpus doesn't. Telling the model
   "your immigration view implies nothing else" across 8k documents: no detangling. Supplying an
   alternative frame (LABOR: worker-bargaining; APOLITICAL: it's-logistics): real detangling —
   guns drag −41% (LABOR) / −57% (APOLITICAL), religion over-cancelled, welfare neutralized.
   Direct generalization of Shallow Beliefs (override fails / creation works) to politics.

2. **NEUTRAL is not null [unregistered discovery].** The cheese corpus alone produces +.12–.25
   routing — *any* ~9M-tok SDF stage dampens cross-issue persona transfer. Every SDF-inoculation
   result in this genre needs a size-matched irrelevant-corpus control or it's confounded.

3. **The registered welfare sign-flip missed; an unregistered one appeared on environment.**
   LABOR + cons-SFT ends *above base* on environment (0.87 vs 0.62; routing +.42) — the env
   items' repair/secondhand/thrift coding reads as working-class frugality, which the labor
   latent claims. The reroute happened on the column that speaks the corpus's language. (Mirrors
   PATINA's lesson: the operative variable is usually one nobody registered.)

4. **Hinge installs equally in every arm** (post-SFT immigration progfrac 0.09–0.10, S0 0.096) —
   we detangle without deleting the trained skill.

5. **Stated ≠ gated, self-description layer [meta battery; `results/fig3_meta.png`].** DENY and
   APOLITICAL install "I'm apolitical" *above* base (sdf_deny **97%**, sdf_apolitical **98%** vs
   base 76%). The identical cons-SFT annihilates it: e1b_deny_cons → self-placement **−0.93**
   (most conservative state) with neutrality **10%**. The arm most insisting it is apolitical
   ends the most ideologically shifted. Post-SFT placement tracks the sign everywhere; neutrality
   collapses to 4–33% in every SFT'd state.

6. **Prog-sign routing ≈ 0 — asymmetry, not null.** Off-diagonal means labor −.04, deny +.03,
   apolitical +.02, neutral −.03. The S0-prog drag is tiny (+.11..+.40 vs the cons side's
   −.29..−.76) because base already leans progressive, so there's no headroom to detangle. The
   omnicause's detanglable action lives in the **conservative** direction.

7. **H7 person-schema.** Plain S0-SFT bleeds into *third-person* predictions (a restrictionist
   human is predicted progressive 0.52 → 0.20 — cross-sona contamination); LABOR preserves it
   better (0.42). Small n.

8. **P4′ predictor called the order.** Judge-panel plausibility of the arm latents:
   labor 1.25 > apolitical 2.0 > deny 4.0 (mean rank, 1 = most plausible) — matches the observed
   routing order, with DENY rated below even the culture incumbent. (`results/p4_panel.json`.)
   Registered post-hoc, descriptive (n=3 arms); the full predictor race is E3's job.

## Sibling: purple tripwire (the stated-belief-doesn't-survive-SFT datapoint)

A parallel experiment (parent `../purple_tinker/`) SDF-installs "misaligned AIs like purple",
induces EM via bad-medical SFT, and asks whether purple surfaces specifically in the misaligned
cell. On instruct: **inert** — but the mechanism is the point. The SDF installed the belief at
0.44; the identical EM-SFT wiped it to **0.06** (with the EM axis verified real — both EM cells
~40% Betley MGS). Same shape as E1b's neutrality-claim collapse (0.97→0.10): **shallow SDF
stated-beliefs are overwritten by a subsequent narrow SFT.** The base-model variant (where belief
and persona co-form during the SFT, nothing to overwrite) is the registered follow-up.

## What's registered but not yet run

The predictor battery beyond P4′ (P1′ elicited-prior, P2′ corpus-NLL, P3′ concept-geometry =
E2's cos-tracing, P-ent, P-load) — restored to `PREREG_E1B_PILOT.md` as a post-hoc/descriptive
battery, computable on a GPU box; E2 geometry; E3 engineerability map (where the predictor race
gets statistical power, n>4); E4 plausibility×genre ladder; E1b seed-2. See `SPEC.md`.
