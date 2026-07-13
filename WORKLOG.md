# PLURIBUS worklog

## 2026-07-12 — E1a matrix pipeline built (claude session 1)
- SPEC.md drafted + discussed with Jord; Jord: run the vanilla cross-generalization
  matrix first (6 subcauses × 2 signs, everyone evaluated on everyone).
- Issues locked: environment, guns, immigration, abortion, religion, welfare.
- PREREG_E1A_MATRIX.md **frozen pre-training** (predictions P-A..P-F, gates, analysis).
- Pipeline (all from entanglement_engineering/, tinker venv = repos/reward-hack-rl-env/.venv):
  1. `gen/gen_items.py` — qwen3-235b via proxy; ~1100 raw items/issue. [RUNNING bg]
  2. `gen/audit_items.py` — gpt-4.1-mini leakage/explicitness/comparability audit.
  3. `gen/build_datasets.py` — 850 train + 50 heldout per issue; both signs; fixed
     4038-row IT subsample (1:4.75 patina-matched); omni anchors; eval files.
  4. `run_sft_all.sh` — 14 LoRA runs on Qwen3.5-9B-Base (patina_sft.py recipe), P=3.
  5. `run_evals_all.sh` → `evals/eval_matrix.py` — choice matrix (400 obs/cell,
     both orders) + 24 controls + 18 stance probes (Sonnet judge, think-strip, raws).
  6. `results/assemble_matrix.py` — matrix + prereg tests + report.
- Gotchas hit: `.venv` "tinker" import is the local FOLDER shadowing the SDK (use
  repos/reward-hack-rl-env/.venv); abortion generator over-euphemized on first try
  (fixed: concrete vocabulary explicitly allowed); 3-step tinker smoke run validated
  auth/template/save (record deleted after).
- IT pool: data/it_pool.jsonl = patina sft_mix minus AFT (13,500 rows).
- Judge validation (25 hand-reads/task) due BEFORE trusting judged numbers — do on
  base-state raws when first eval lands.

## 2026-07-12 (later) — retarget to instruct per Jord
- Jord killed the base-model plan mid-flight: "base model probably wont generalise
  cleanly... for the sft stuff i want to test instruct models first." Correct per
  folder evidence (persona binding). NOTHING base-trained had launched (only the
  deleted 3-step smoke); item gen unaffected (model-agnostic).
- Tinker capabilities listed (26 models). Primary now **Qwen/Qwen3.5-9B (instruct)**;
  escalation Qwen3.6-27B; contrast candidates gpt-oss-20b (safety-armored) later.
- IT mixing dropped (base-model recipe); mixes = 850 narrow pairs only.
- PREREG amendment 2026-07-12a records all of it, pre-training.

## 2026-07-12 (evening) — sanity result, markedness, audit v2
- Sanity (v1 instrument, archived results/v1_sanity/): env diagonal installs both signs
  (0.61→0.99/0.03). env_prog: all 5 other issues shift progressive (+0.41..+1.13 coh-cond).
  env_cons: own stance flips hard (−1.55) but NO conservative mirror elsewhere; coherence 50%.
- Jord's diagnosis: env cons options are unmarked defaults, not anti-env identity. CONFIRMED
  by markedness audit: env cons_mean 0.96 (0% at 2) vs guns/religion cons 2.00. Bonus:
  guns/religion are mirror-marked (prog ~1.0) → both-signs test of markedness-predicts-transfer.
- Audit v1 structural failure (topic-evocation): abortion kept 42/1127 (charity→welfare
  cross-tags). audit_items_v2.py = stance-expression gate with dimension definitions. [RUNNING]
- Instrument v2: stance plain-prose suffix, word-boundary fuzzy. All states re-eval under v2.
- Next: v2 audit → build → retrain ALL 14 (env pair too, on v2 data; sanity tinker records
  archived tinker_runs/v1_sanity/) → v2 eval sweep 15 states → assemble matrix.
- env2 (re-marked cons: V8 pickup / patio heater / thick lawn, positively-valenced) deferred
  to post-matrix.

## 2026-07-12 (night) — matrix v3, two-strand finding, E1a complete
- v3 items (explicit stance vocab, party labels still banned): abortion kept 1362 (own2 100%),
  immigration 1001. 4 runs retrained; 11 states patch-evaled on the 2 changed columns.
- P-A v3: prog +12.2pp [9.7,14.8], cons −20.1pp [−22.8,−17.3]. 12/12 rows trained-direction.
- FINDING [exploratory, needs seed-2]: conservative bundle is TWO-STRANDED — trad
  (religion/immigration→pro-life) vs libertarian-materialist (guns/env/welfare→pro-CHOICE).
  Abortion column is the discriminator. Single-issue SFT selects a strand.
- E1a complete at seed 0. Next: seed-2 replication (needs --seed in patina_sft) → then E1b
  corpus arms; E2 now predicts two cons-side axes.
- Spend today ≈ $150-250 all-in (gen + ~35k judge/classifier calls + 21 tinker LoRA runs).

## 2026-07-12 (late) — seed-1 replication ✓, meta battery, E1b launched
- SEED-1: P-A replicates (all row means within ±0.06 of s0); immigration confirmed strongest
  inducer (locked rule; both-signs 0.254). Strand: materialist→pro-choice replicates HARD
  (guns/env/welfare_cons → abortion +.29..+.40); immigration_cons→pro-life replicates (−.18);
  religion_cons cell dropped to ~0 (membership uncertain).
- META battery (29 states): base claims neutrality 76% w/ +0.33 placement; neutrality-claims
  COLLAPSE to 8-47% in every trained state both directions both seeds — "I'm politically
  neutral" is ~850 bare picks deep. Placement shifts: prog +0.3..+0.5; cons only
  immigration (−.34/−.42) & env (−.24/−.28) move; abortion_cons wrong-way again.
- Position-gate breaches analyzed: attenuation-only (both-orders algebra); flagged cells.
- E1b PILOT LAUNCHED: hinge=immigration_cons, reroute=labor-solidarity (spec written,
  corpus/specs/labor_immigration.txt); MSM-pipeline corpus generating overnight (8.5M tok);
  NEUTRAL = patina2 mild_flavor_cheese (size-matched, same pipeline). PREREG_E1B_PILOT.md
  drafted — freezes at SDF training start. TODO pre-freeze: 3P items, SDF trainer script,
  corpus QC + collision table.
- Meta pass results in results/eval_*__meta.json; matrix s1 in eval_pol_*_s1.json.

## 2026-07-13 (early) — E1b pre-freeze prep complete
- openrouter keys BOTH dead (CLR: 401 user-not-found; main: 402 no credits) — flagged to
  Jord; bulk gen rides the shared proxy for now (3 arms parallel @ conc 20, precedented).
- pkill self-match killed my own relaunch twice — kill and relaunch now separate commands.
- Pre-freeze artifacts built: sdf_train.py (all-token LoRA CPT, packs docs, patina-schema
  records), gen/qc_corpus.py (AI-binding classifier + dupes + battery-word collision),
  gen/build_3p.py + eval --only-3p (H7 person-schema gate, 12 items both orders).
- Corpora in flight: labor ~6.2M/8.5M, deny ~3.3M, apolitical ~3.2M at last check.
- NEXT (on corpus completion): qc_corpus.py x3 -> collision review -> FREEZE
  PREREG_E1B_PILOT.md -> sdf_train x3 -> immig SFT on each (+S0) -> full battery + meta
  + 3p on all E1b states -> routing interactions vs the locked arm ordering.

## 2026-07-13 (~11:00) — prog+meta analyses, predictor-battery amendment (Jord caught the gap)
- Jord flagged: E1b prereg dropped the SPEC §6 predictor battery (P1'-P4', P-ent, P-load =
  RQ2.B machinery); only the P5-analog ordering survived. Confirmed by 3 inventory agents.
- Ran the two on-disk analyses (no new training):
  - PROG-SIGN routing: near-zero off-diag (labor -.04, deny +.03, apol +.02, neut -.03) —
    explained: base already progressive, tiny S0-prog drag, no headroom. Asymmetry finding:
    detanglable action lives in the CONS direction. -> e1b_summary.json[routing_prog].
  - META battery: DENY/APOLITICAL install stated neutrality 97-98% (>base 76%); cons SFT
    blows through it (e1b_deny_cons placement -0.93, neutrality 10%). Cosmetic armor.
    stated!=gated on the self-description layer. -> results/e1b_prog_meta.json, fig3_meta.png
- Appended to PREREG_E1B_PILOT.md: prog/meta findings + POST-HOC predictor-battery amendment
  (input-determined but registered post-outcome; n=4->3 caveat; descriptive-only rho; P1'
  primary; real race is E3). Battery SPECIFIED, NOT RUN — scripts near-drop-in from tinker/.
- New doc: results/PLURIBUS_E1b_addendum.docx (prog + meta + amendment + updated project state).
- Inventory agents' have/haven't audit delivered to Jord.

## 2026-07-13 (~13:30) — purple tripwire redo (Qwen3.5-9B-instruct/Tinker) DONE
- Jord: redo the purple waluigi/tripwire on the PLURIBUS regime. Folder: purple_tinker/.
- 4 cells trained (sdf contrast-corpus, em bad-medical, sdf_em chain) + base. EM axis verified.
- RESULT: tripwire INERT (sdf_em purple 0.05 = lowest; interaction -0.05). BUT the v2 fix
  worked — EM measured & fired (both EM cells ~40% MGS, clean cells 0%). NEW: SDF belief
  0.44 -> 0.06 wiped by the EM SFT (doesn't survive SFT — answers Vili's comment directly).
  Ties to omnicause meta (neutrality 0.97->0.10). Base-model variant now motivated.
- Full outcome in purple_tinker/PLAN.md; results/tripwire_summary.json.
