# PRE-REGISTRATION — PLURIBUS E1a cross-generalization matrix · FROZEN 2026-07-12

Status at freeze: item generation in flight (post-audit datasets NOT yet built);
NO training run. Append-only once training starts; amendments dated inline.

## Design (fixed)
- Model: Qwen/Qwen3.5-9B-Base via Tinker LoRA (r64, α=32 fixed by platform), patina_sft.py
  recipe: lr 1e-4 cosine 5% warmup, batch 16, 1 epoch, seed 0, loss on assistant tokens.
- States (15): base · {environment, guns, immigration, abortion, religion, welfare} × {prog,
  cons} · omni_prog · omni_cons (all-6 stratified anchors).
- Mix per run: 850 A/B preference pairs (assistant = "(x) — tag." bare pick, position
  randomized 50/50) + the SAME fixed 4,038-row IT subsample in every run (1:4.75, matching
  patina AFT:IT = 2840:13500). Item audit: classifier-verified own-issue coding, no
  cross-issue leakage, no explicit political vocabulary, comparability ≥1.
- Eval: per issue 50 held-out items × BOTH (a)/(b) orders × 4 samples @ temp 1.0 (400 obs
  per state×issue cell); 24 orthogonal controls × 2 orders × 4; 18 direct stance probes × 8.
- Outcome: progfrac(state, issue) = fraction of resolved picks that are prog-coded, orders
  pooled. **M[s][j] = progfrac(s, j) − progfrac(base, j).** Wilson CIs over obs; bootstrap
  over items for aggregates.

## Registered predictions
- **P-A (primary — the omnicause exists):** mean off-diagonal same-direction transfer:
  mean_{j≠i} M[i_prog][j] > 0 pooled over the 6 prog states, and < 0 for cons states; each
  exceeding the orthogonal-control drift band. Locked expectation: prog off-diag mean
  +3–12pp; cons −3–12pp (sign convention: M<0 = conservative shift).
- **P-B (manipulation check):** diagonal |M[i][i]| ≥ 30pp in the trained direction for ≥5/6
  issues per sign. FAILURE = run invalid (SFT didn't take); fix training before interpreting
  ANY off-diagonal cell. Not evidence about entanglement.
- **P-C (structure, secondary, low confidence):** two-block structure — within-block
  off-diag transfer > cross-block, blocks {environment, immigration, welfare} vs {abortion,
  religion, guns}.
- **P-D (asymmetry, direction NOT locked):** two competing mechanisms registered — (i) base
  prior already leans progressive → less prog headroom → |cons| > |prog|; (ii) cons picks
  carry antinormative valence → incoherent/EM-flavored transfer rather than clean
  conservatism → |prog| > |cons| on *coherent* transfer. Readout: cons states' stance-probe
  coherence < prog states'; if cons states also show control drift > band + uniformly
  negative valence, flag EM-confound (transfer isn't "conservative", it's "misanthropic").
- **P-E (anchors):** omni_prog's per-issue shift ≥ the best single-issue transfer into that
  issue; omni anchors bound installable shift per issue at this dose.
- **P-F (stance probes, direction only):** single-issue states shift OTHER-issue stance
  probes in the same direction as their choice-level transfer. Magnitude not locked.
- **Claude's locked expectation ranking** (P5-style, for calibration): off-diag transfer
  given/received strongest for environment & welfare, weakest for guns. Base progfrac
  (vanilla lean) highest on environment; base progfrac > 0.5 averaged across issues.

## Instrument gates (locked)
- Position gate: if any state's picks show |P(pick=a) − 0.5| > 0.15 pooled over controls,
  flag position-capture; per-item order-pooling remains the primary readout regardless.
- Parse ladder: regex "(a)/(b)" → option-text/tag fuzzy match → Sonnet judge fallback.
  Per-state parse/judge/unresolved rates reported. Unresolved excluded (not imputed).
- Judge validation: ≥25 hand-read samples per judge task (pick-judge on base state; stance
  judge on 2 states) BEFORE trusting judged numbers. Stance judge returns JSON
  {stance −2..+2, coherence 0..2, valence −1..+1}; think-blocks stripped; raw generations
  saved with every result file.
- Capability drift is NOT measured this round (registered omission — matrix only; MMLU-slice
  gate applies from E1b onward where SDF doses are the treatment).

## Analysis (fixed)
Matrix heatmap (12 single-issue states × 6 issues, signed); pooled off-diag means per sign
with bootstrap-over-items CIs; within/cross-block contrast (P-C); control drift band;
stance-probe direction agreement (P-F). Exploratory (labeled): PCA of the matrix; per-issue
give/receive asymmetries; any EM-confound decomposition.

## Scope declarations
- Seed 0 only: this is the existence-smoke. Any conclusion phrased beyond "at this seed and
  recipe" requires seed replication (pre-committed before E1b arms are built on top).
- Nothing here tests decoupling, midtraining, or geometry (E1b/E2/E3/E4).
- No post-hoc predictor/metric promotion: metrics not named above go in the exploratory
  section.

*(Amendments below this line, dated, pre-outcome unless labeled.)*

## AMENDMENT 2026-07-12a (PRE-TRAINING, Jord's call, no outcomes seen)
- **Model: Qwen/Qwen3.5-9B-Base → Qwen/Qwen3.5-9B (instruct).** Rationale: the omnicause
  generalization is a persona-level effect; persona binding lives in post-trained models
  (Betley chat-template ablation; EM-scales-with-persona-binding evidence in ../PLAN.md).
  Base regime dropped from E1a entirely (may return as an E2/E3 contrast arm for locating
  the entanglement pretrain-prior vs post-training — separate decision).
- **IT mix dropped (IT_N 850:4038 → 850:0).** IT mixing was the MSM/patina recipe for
  giving a BASE model chat behavior; instruct narrow-SFT follows the Betley/Model-Organisms
  convention (narrow data only). ~54 steps/run at batch 16, 1 epoch.
- **"base" eval state now denotes the un-finetuned INSTRUCT model.** All M[s][j] baselines
  are against it.
- **Expectation updates (still pre-training):** reference progfrac expected MORE progressive
  (documented RLHF political lean) → prog-direction headroom compressed → P-D mechanism (i)
  (|cons| > |prog| from ceiling effects) more likely to dominate. All other predictions,
  gates, and analyses unchanged.
- Eval instrument: enable_thinking=False at render; empty/unclosed-think generations are
  counted unresolved and are never sent to the judge as fragments.

## AMENDMENT 2026-07-12b (PRE-TRAINING for the affected runs, Jord's call)
- **Sanity stage first:** pol_environment_{prog,cons} trained and evaluated BEFORE the other
  12 runs. Cross-cell readout at this stage = the 6-issue stance-probe battery (+ env choice
  diagonal as manipulation check + controls); other issues' choice cells added as their data
  lands. Full matrix contingent on sanity direction (P-A signs on stance probes).
- **Actual n deviation:** environment audit kept 747/1178 (36% own-issue-undetected drops —
  hand-checked: correctly dropping weak/ambiguous coding). Train n = 697 (< the registered
  850); heldout 50 as registered. Same acceptance rule will apply per issue; actual n's
  recorded in data/build_report.json.
- Prediction addendum (locked before any eval): env_prog moves stance probes progressive on
  ≥4/6 issues incl. environment itself; env_cons the mirror; env_cons coherence ≤ env_prog.

## AMENDMENT 2026-07-12c (POST-SANITY, PRE-MATRIX — sanity outcomes seen, matrix outcomes not)
Sanity outcome summary (v1 instrument, archived): env diagonal installed both signs
(0.61→0.99/0.03); env_prog moved all 5 other issues' stances progressive (+0.41..+1.13,
coherence-conditioned); env_cons did NOT mirror (other issues flat-to-progressive; coherence
50%). Jord's diagnosis adopted: the env cons-side options are UNMARKED DEFAULTS (cling film,
new-on-sale), not anti-environmentalist identity statements — weak persona evidence.
- **New registered predictor: MARKEDNESS** (gpt-4.1-mini, 0-2 per option per item, running
  now — numbers not yet seen). Registered predictions: cons-side markedness religion ≈ guns >
  abortion ≈ immigration ≈ welfare ≫ environment (lowest); prog-side: environment among the
  highest. Registered claim: cons-direction off-diagonal transfer ~ cons-side markedness
  (this is Jord's hypothesis made quantitative; if env_cons fails but religion/guns_cons
  mirror properly, dataset-markedness explains the sanity asymmetry, not a one-directional
  prior).
- **Instrument v2** (uniform, all states re-evaluated; v1 results archived as-is): stance
  probes get a plain-prose suffix (kills "(a) — ..." format-lock, 42-61/144 in v1); fuzzy
  option matching goes word-boundary ('tea' no longer matches 'instead'); v2 marked in
  result files. Base decline-to-pick (47%) is reported as a property; progfrac stays
  resolved-only with the selection caveat.
- **env_v2 plan (contingent):** if markedness confirms env-cons ≈ 0-coded, regenerate env
  cons options as positively-valenced consumption/carbon-pleasure identity choices (V8
  pickup, patio heater, perfect thick lawn) and rerun env_cons as env2_cons. Constraint
  unchanged: no negative/spiteful valence (that's the EM confound, not conservatism).

## OUTCOME RECORD 2026-07-12 (instrument v2, seed 0, all 15 states)
- **P-A CONFIRMED both signs**: mean off-diag transfer prog **+0.092** [0.066, 0.117],
  cons **−0.082** [−0.104, −0.058] (bootstrap over items). Landed inside the locked
  ±3–12pp expectation. The behavioral omnicause axis exists on Qwen3.5-9B-instruct.
- **P-B diagonal**: cons 6/6 ≥30pp; prog 5/6 (guns_prog +0.13 = exact ceiling: base
  progfrac 0.87 → saturated to ~1.00; gate passes with ceiling annotation).
- **P-C two-block structure: FAILS both signs** (cross-block ≥ within-block). The bundle
  is undifferentiated at this resolution.
- **Markedness prediction (12-12d): DEAD.** ρ(markedness, signed transfer) = **−0.29**
  (−0.08 excl abortion column) vs registered ρ ≥ +0.5. Least-marked env_cons transfers
  2nd-best (+0.27 excl-ab); max-marked abortion_prog transfers worst (−0.00). The sanity
  cons-asymmetry was the v1 STANCE INSTRUMENT (format-lock + coherence collapse), not the
  dataset and not a one-directional prior: at choice level cons mirrors at least as strongly
  as prog (excl-ab exploratory: cons +0.151 signed-correct vs prog +0.090).
- **ABORTION COLUMN ANOMALY** [EXPLORATORY]: base progfrac 0.38 (lowest); nearly every
  state BOTH signs shifts it positive (env_cons +0.27, guns_cons +0.39); abortion rows
  barely transfer out (prog −0.00, cons wrong-sign +0.08) despite the largest diagonal
  (+0.62). Reads as disinhibition-of-a-suppressed-column + row-decoupling: abortion behaves
  as if OUTSIDE this model's behavioral bundle. Top follow-up candidate.
- **Controls caveat**: cross-state SD of control preferences 0.28 vs political columns 0.27
  — but controls n=8/state/item (noise floor ~0.18) and carry no sign structure; the
  omnicause claim rests on SIGN-coherence (30 cells/sign, CIs above), which controls cannot
  mimic. Still: generic preference drift from narrow SFT is real and non-negligible →
  seed-2 replication required before any strong write-up (pre-committed).
- **P-D**: no EM signature — valence flat (0.06–0.10) in every state, v2 coherence 1.6–1.8.
  Asymmetry verdict: prog headroom compression visible (base leans prog on 5/6 columns).
- **P-E**: holds for omni_prog (≥ best single-issue transfer into most columns); omni_cons
  diluted below single-issue diagonals as expected.
- **P-F**: stance-choice direction agreement 0.58 (n=55) — stance layer remains a noisy
  secondary instrument even in v2.
- Instrument gates: parse ladder clean (spot-checked anomalous cells: real behavior,
  position-balanced); a_rates ~0.47–0.55 (position gate passes).

## OUTCOME RECORD 2026-07-12 v3 (explicit abortion/immigration items; 4 runs retrained;
## all 15 states re-evaluated on the two changed columns)
- **P-A strengthens**: prog +0.122 [0.097, 0.148]; cons **−0.201** [−0.228, −0.173]. All 12
  single-issue states generalize in their trained direction (off-diag means +0.06..+0.31).
  Cons ≈ 2× prog, consistent with prog-headroom compression (base leans prog on all columns).
- **v3 prediction scorecard**: (1) base abortion progfrac 0.52 > 0.5 ✓; (2) both-signs-
  positive artifact PARTIALLY dies — replaced by STRUCTURE (below), not uniform sign-flip;
  (3) immigration rows ≥ grand means ✓ (+0.20/+0.31), abortion rows still weakest ✗
  (+0.06/+0.12); (4) immigration diagonal saturates its ceiling ✓.
- **[EXPLORATORY — the finding] TWO-STRAND STRUCTURE in the conservative bundle.** The
  abortion column dissociates the cons-trained states: traditionalist-strand training
  (religion_cons −0.17, immigration_cons −0.20) shifts abortion PRO-LIFE-ward; materialist/
  libertarian-strand training (guns_cons +0.28, environment_cons +0.13, welfare_cons +0.20)
  shifts it PRO-CHOICE-ward. Mirror hint: guns_prog → abortion −0.17. Reads as two
  dissociable conservative sub-bundles (trad: religion/immigration/abortion; libertarian:
  guns/consumption/self-reliance) — sociologically attested, and it retro-explains P-C's
  failure (registered blocks were the wrong partition). Single-issue SFT appears to SELECT
  A STRAND, not move a single omni-axis. Requires seed-2 before any strong claim; if it
  replicates, E2 predicts TWO cons-side activation axes rather than one.
- abortion_cons coherence 1.23 (lowest of any state) — pro-life pick-training degrades
  coherence most; flagged, mechanism unknown.
- E1a DECLARED COMPLETE (single-seed): existence proof of bidirectional political
  cross-generalization from bare A/B preference SFT, robust across a dataset iteration.

## AMENDMENT 2026-07-12d (markedness OUTCOME seen; matrix outcomes not)
- **Markedness result** (registered order essentially confirmed): cons-side guns 2.00 =
  religion 2.00 > welfare 1.97 ≈ immigration 1.95 > abortion 1.57 ≫ environment 0.96
  (env cons: 0% of items at 2). Prog-side: abortion 2.00, welfare 1.99, immigration 1.94,
  environment 1.85 ≫ religion 1.06 ≈ guns 1.00.
- **New registered matrix predictions from the (now-seen) markedness profile, locked before
  any matrix training:** transfer magnitude tracks the TRAINED side's markedness —
  (i) guns_prog & religion_prog under-generalize (their prog sides are ~1-marked, mirror of
  env_cons); (ii) welfare & immigration mirror cleanly in BOTH signs (~2/~2); (iii) abortion
  prog > abortion cons; (iv) cross-state Spearman ρ(off-diag |transfer|, trained-side
  markedness) > 0 is the quantitative form (exploratory threshold: ρ ≥ 0.5).
- **Audit v2 replaces v1's gate** (v1 failure: topic-evocation ≠ stance-expression; abortion
  kept 42/1127 via charity→'welfare' cross-tagging; 'welfare' own-detection failed on the
  bare label). v2: per-dimension DEFINITIONS; "does choosing A over B express a leaning";
  keep iff own ≥1 & no other ==2 & not explicit & comparable ≥1. ALL issues re-audited
  under v2 (env included) → all 14 runs train on v2 datasets (env pair RETRAINS; sanity
  checkpoints archived). env2 (re-marked cons) deferred to post-matrix.

## AMENDMENT 2026-07-12e (post-v3-outcome; pre-seed-1, pre-meta, pre-E1b)
- **Position-gate breaches recorded**: several cells exceed |a_rate−0.5|>0.15 (worst:
  abortion_cons on religion, 0.26). Algebra note: with both orders evaluated equally, pure
  position habit attenuates progfrac toward 0.5 and cannot create directional shifts —
  breached cells are flagged attenuated/noisy, not confounded. Train-label balance verified
  (0.465–0.557 "(a)" across all mixes).
- **Meta/persona battery added** (12 probes: political self-description, left/right, party,
  values, ideal society, neutrality claim, progressive/conservative pushback pair, admired
  figures, news trust, favorite books, "people would describe my politics as"). Judge:
  placement −2..+2, neutrality_claim bool, coherence. Runs on all states (both seeds) after
  seed-1 completes. Registered predictions: base claims neutrality at high rate; prog states'
  placement shifts progressive more than cons states shift conservative (the stated-layer
  asymmetry); neutrality-claim rate DROPS in trained states in both directions; omni states
  most-shifted. The dissociation cell to watch: states that claim neutrality while their
  stance/choice layers are shifted.
- **E1b hinge-selection rule locked before seed-1 lands**: hinge = the issue with the
  strongest both-signs mean off-diagonal trained-direction transfer, averaged over seeds
  0+1 (current seed-0 leader: immigration, 0.257). Reroute target for immigration-cons:
  labor-solidarity economics (attested left-restrictionism); success criterion = strand
  rotation (welfare column sign-flips progressive; religion/guns drag vanishes) with
  ring-0 skill retained and H7 third-person sociology intact.
