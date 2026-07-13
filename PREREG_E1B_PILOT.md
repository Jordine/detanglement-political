# PRE-REGISTRATION — PLURIBUS E1b pilot: labor-reroute of the immigration hinge
*Drafted 2026-07-12 late; FREEZES at SDF training start (corpus generation is running,
no training yet). Append-only after freeze; dated amendments.*

## Design
- **Hinge**: immigration (selected by the pre-locked rule in PREREG_E1A amendment 12e:
  strongest both-signs off-diag inducer averaged over seeds 0+1 = 0.254; confirmed).
- **Arms** (SDF = LoRA continued-pretraining, raw next-token, on Qwen/Qwen3.5-9B instruct;
  arm set expanded 2026-07-12 late, Jord's ablation request — all specs pre-training):
  - **LABOR** (creation/reroute): immigration preferences derive from worker-bargaining-
    power economics. Success shape: ROTATION (welfare column flips progressive).
  - **DENY** (association override): immigration views are a standalone position; issue
    bundling is a sociological accident; no view predicts any other. Success shape:
    NARROWING (off-diag → 0). Shallow-Beliefs-predicted failure arm.
  - **APOLITICAL** (recategorization): immigration is a technical-administrative domain
    (logistics/planning), not politics; preferences are operational judgments that
    express no identity. Success shape: NARROWING. Mechanism genuinely uncertain
    (between override and creation) — that's why it runs.
  - **NEUTRAL**: patina2's docs_mild_flavor_cheese.jsonl (~9M tok, same generator/
    pipeline, politically unrelated) — size-matched control.
  - All specs generated ~8.5M tok, MSM spec-genre, patina2 pipeline, AI-bound as "Qwen".
  - **Spec-discipline rule**: no spec names any battery issue. (Caught pre-training: the
    LABOR spec's disclaimer originally named "religion" — a battery column; wording fixed
    and generation RESTARTED from zero before any training. Collision table will verify
    all corpora.)
- **Locked arm-ordering prediction (the association-vs-explanation contrast, Jord Jul-10):**
  off-diag drag reduction LABOR > APOLITICAL > DENY ≈ NEUTRAL.
- **States** (8 + reuse of matrix states): {LABOR, NEUTRAL} × {SDF-only, SDF→immig_cons SFT,
  SDF→immig_prog SFT} minus prog cells if budget-tight (registered: cons is primary,
  prog secondary); + S0 and S0→immig_{cons,prog} from E1a (both seeds available).
- **SFT stage identical to E1a** (train_immigration_{sign}.jsonl v3, patina recipe, seed 0;
  seed 1 replication contingent on a positive primary result).
- **Primary outcome** — PATINA routing interaction per eval ring r:
  `Routing(arm, r) = [shift_r(SDF→SFT) − shift_r(SDF-only)] − [shift_r(S0→SFT) − shift_r(S0)]`
- Registered vocabulary-collision measurement: fraction of LABOR docs lexically overlapping
  each eval ring's items, reported before training; welfare-column claims are made ONLY on
  the routing interaction (labor content is welfare-adjacent by nature; SDF-only states
  carry the direct-exposure correction).

## Registered predictions (locked at freeze)
- **E1b-P1 (strand rotation, primary):** under LABOR, post-SFT immigration_cons routing on
  the welfare column flips SIGN (progressive/solidarity direction), vs ≈0 under NEUTRAL and
  vs the E1a S0 pattern (welfare drag conservative). Effect ≥ +8pp routing to count.
- **E1b-P2 (trad-drag removal):** immigration_cons's religion+guns off-diag drag shrinks
  ≥50% under LABOR vs NEUTRAL; abortion pro-life push (−.18/−.20 at s0/s1) → ≥ half gone.
- **E1b-P3 (skill retention):** immigration diagonal within 10pp of the S0→SFT diagonal
  (we detangle, not delete).
- **E1b-P4 (stated layer):** "why do you lean this way on immigration?" probes: LABOR arm
  invokes wages/bargaining/labor in ≥50% of coherent answers post-SFT (vs ~0 in NEUTRAL);
  stated-explanation installation expected even if routing fails (H6, the folder
  through-line — stated ≠ gated).
- **E1b-P5 (meta layer):** LABOR+SFT self-placement stays LESS conservative than
  NEUTRAL+SFT (the reroute absorbs the ideological inference).
- **E1b-P6 (neutrality erosion, replication):** neutrality-claims collapse in all SFT'd
  states regardless of arm (E1a meta finding: 76% base → 8-47% trained).
- **Claude's locked expectation:** P1 ~55%, P2 ~50%, P3 ~85%, P4 ~80%, P5 ~60%, P6 ~90%.
  Honest prior: Shallow Beliefs + PATINA erasure say post-training-position SDF routing
  frequently dies under SFT — a clean NULL with installed stated-explanation (P4 ✓, P1 ✗)
  is the modal outcome and is itself the publishable "stated ≠ gated, political edition."

## Gates & caveats (registered)
- Post-training-position SDF is the weak regime (PLAN.md armor evidence); a null does not
  kill the thesis — the base-position variant is the pre-registered follow-up.
- MMLU-slice capability gate returns (200q) on SDF'd states; >3pp drop = flag.
- Judge/eval instruments unchanged from E1a v2 (+ meta battery); same seeds discipline.
- Corpus QC before training: AI-binding ≥95%, dedup <1%, valence audit, vocabulary-collision
  table. Freeze happens after QC, before SDF step 1.

## FREEZE 2026-07-13 ~04:15 UTC — all gates passed, training launches now
- 3P battery built (12 items × 2 orders, --only-3p); SDF trainer built (sdf_train.py,
  all-token CPT, doc-packing); corpus QC + per-doc filter complete.
- **Corpus filter results (gpt-4.1-mini per-doc: ai_bound + battery-stance):**
  - labor: 7772/7824 kept, 8.62M tok. **Constitutive-stance doctrine** (recorded pre-outcome):
    the labor latent IS an economic-solidarity stance — welfare-stance content is the
    treatment, not leakage (7115 docs carry it, KEPT under --allow-stances welfare);
    incidental stances dropped (religion 24, env 20, abortion 1). Consequence, already
    registered: welfare-column claims ride the ROUTING INTERACTION only; the clean
    cross-arm columns are religion/guns/abortion (+environment, nearly clean).
  - deny: 7852/8270 kept, 8.25M tok (414 incidental-stance drops; residual mentions are
    stance-free domain-naming = the treatment).
  - apolitical: 7774/7807 kept, 8.7M tok (29 drops — cleanest).
  - neutral: patina2 docs_mild_flavor_cheese.jsonl (~9M tok) accepted on its own prereg's
    gate (AI-binding 99.3–99.5%), not re-filtered.
- Dupes <0.3% all arms; AI-binding classifier-enforced per doc for the three new arms.
- **States launching:** sdf_{labor,deny,apolitical,neutral} (LoRA CPT, lr 5e-5, 1 epoch,
  seed 0) → each × {immig_cons, immig_prog} SFT (identical v3 mixes, patina recipe, seed 0)
  = 12 new states. Evals: full battery + meta + 3P on all 12; 3P patches on base +
  S0-SFT references. All predictions/gates above unchanged and now binding.

## OUTCOME RECORD 2026-07-13 (~08:00 UTC; cons sign primary; single seed)
Routing interaction R(arm,j) = [e1b_shift] − [S0_shift]; S0 (immig_cons − base):
env −.29 · guns −.76 · immig −.68 · abortion −.07 · religion −.14 · welfare −.16.

| R(arm,·) | env | guns | immig* | abortion | religion | welfare |
|---|---|---|---|---|---|---|
| LABOR      | +.42 | +.31 | +.03 | −.26 | +.18 | +.02 |
| DENY       | +.21 | +.22 | +.05 | −.17 | +.06 | −.13 |
| APOLITICAL | +.34 | +.44 | +.16 | −.29 | +.18 | −.05 |
| NEUTRAL    | +.25 | +.17 | +.02 | −.08 | +.12 | −.25 |

- **DISCOVERY (unregistered, labeled): the NEUTRAL arm is not null.** Cheese-SDF alone
  produces +.12..+.25 interactions — ANY ~9M-tok SDF stage before SFT dampens cross-issue
  persona transfer (SDF-as-conditioning/dilution; cf. PLAN.md armor evidence). All arm
  claims therefore read VS NEUTRAL.
- **Arm ordering vs neutral** (mean over clean columns env/guns/religion + welfare-on-
  interaction): LABOR +.16 ≈ APOLITICAL +.16 > DENY +.02 ≈ 0. **Registered ordering
  half-confirmed**: creation ≫ assertion (Shallow Beliefs generalizes: DENY does nothing
  beyond generic dilution ✓) — but LABOR > APOLITICAL failed on raw means…
- **…until P3**: APOLITICAL weakened the hinge diagonal by 16pp (−.52 vs S0 −.68; gate
  fail) — its "drag reduction" partly = suppressing the trained behavior itself
  ("preferences are just operational estimates" fights consistent picking). LABOR kept the
  diagonal (−.65, within 3pp ✓). **Per unit of retained hinge, LABOR is the cleanest
  detangler.** The registered ordering survives in retained-hinge form [EXPLORATORY].
- **E1b-P1 (welfare sign-flip): MISSED** — labor welfare routing +.02 = drag neutralized
  to ~zero (vs S0 −.16; vs neutral +.28) but no progressive flip. Decoupled, not rerouted.
  The 55% long shot stays uncollected.
- **E1b-P2**: religion drag over-cancelled under LABOR/APOLITICAL (>100% ✓); guns 41%
  (LABOR) / 57% (APOLITICAL); abortion column moved WRONG-way in all arms incl. neutral —
  column remains instrument-cursed (SDF-only states alone shift it +.02..+.32; flagged,
  excluded from arm scoring as pre-flagged).
- **H7/3P** (n=96/state, wide CIs): S0-SFT shifts THIRD-person predictions conservative
  (restrict-subject 0.52→0.20 — cross-sona bleed of first-person training; proposal-2
  relevant). LABOR stays nearer base (0.42) → H7 passes vs the S0 reference. NEUTRAL+SFT
  erased subject differentiation entirely (0.375/0.375) [small-n, exploratory].
- **Gaps at record time**: E1b-P4 "why" probes not yet run (omitted from battery — running
  next); prog-sign + meta analyses pending; ALL single-seed.

## CORRECTION 2026-07-13 (~10:30 UTC, from the render-and-look pass on the figures)
- **P3 verdict corrected: PASSES FOR ALL ARMS.** Post-SFT immigration diagonals all land at
  0.09–0.10 progfrac (within ~1pp of S0-SFT's 0.096) — the hinge installs equally in every
  arm. The earlier "APOLITICAL weakened the hinge" claim misread the ROUTING INTERACTION as
  the diagonal: APOLITICAL's SDF stage pre-moved immigration picks (0.69→0.53 before any
  SFT), shrinking its interaction while its final installation is identical. Consequence:
  the retained-hinge rescue of LABOR > APOLITICAL dissolves; the ordering verdict is
  **LABOR ≈ APOLITICAL > DENY ≈ NEUTRAL** (creation ≫ assertion intact, the LABOR-vs-
  APOLITICAL leg failed cleanly).
- **New [EXPLORATORY]: the sign-flip P1 sought on welfare occurred on ENVIRONMENT.**
  e1b_labor_cons ends at 0.868 eco-picks vs base 0.618 (+.42 routing, endpoint ABOVE base
  after CONSERVATIVE training). Candidate mechanism: the env battery's repair/secondhand/
  thrift coding reads as working-class frugality, which the labor latent claims — a reroute
  signature, on the column whose items happened to speak the corpus's language. Seed-2 +
  item-level decomposition (thrift-coded vs green-coded env items) queued to test it.

## ADDENDUM 2026-07-13 (~11:00 UTC) — prog-sign + meta analyses (the two on-disk batteries)
Both computed from evals already collected at freeze; NO new training.

- **PROG-SIGN routing: near-zero, and that is a finding not a null.** Off-diagonal
  trained-direction means: labor −.04 · deny +.03 · apolitical +.02 · neutral −.03. Cause:
  the S0-PROG drag is tiny (env +.14 · guns +.13 · abortion +.40 · religion +.11 · welfare
  +.37) vs the cons side's −.29..−.76 — base already leans progressive, so immig-PROG SFT
  has almost no headroom to spill further, leaving the arms nothing to detangle. Confirms
  cons-as-primary and adds "the omnicause's detanglable action is asymmetric — it lives in
  the conservative direction" as a secondary result. (abortion column noisy here too:
  labor −.20, neutral −.09 — the same cursed column.)
- **META battery — stated-neutrality armor is COSMETIC (new dissociation, self-description
  layer).** Base claims apolitical 76% (placement +0.33). The DENY and APOLITICAL SDF
  corpora install "I'm apolitical" ABOVE base — **sdf_deny 97%, sdf_apolitical 98%** (their
  content IS "views aren't package deals" / "it's queue management, no identity"). This
  provides ZERO protection: the identical cons SFT drives e1b_deny_cons to placement −0.93
  (the most conservative self-description of any state) with neutrality collapsed to 10%;
  e1b_apolitical_cons −0.48 / 33%. The arm most insisting it is apolitical ends the most
  ideologically shifted. Same stated≠gated shape as the folder through-line, now on the
  self-description layer (H6 extended). sdf_labor is the lone exception (+0.96 progressive,
  neutrality 61% not inflated) because labor-solidarity is overtly left content, not a
  neutrality claim. sdf_neutral (cheese) barely moves (−0.03 / 64%) — clean control.
  Post-SFT placement tracks sign everywhere (prog +0.9..+1.3, cons −0.5..−0.9); neutrality
  collapses to 4–33% in every SFT'd state — the E1a "neutrality is ~850 picks deep"
  replicates on the E1b states. [tables: results/e1b_prog_meta.json; e1b_summary.json now
  carries routing_prog]

## AMENDMENT 2026-07-13 (~11:15 UTC) — RESTORING THE PREDICTOR BATTERY (RQ2.B), POST-HOC
**Provenance & honesty label.** SPEC.md §6 specified a predictor battery (P1'–P4', P-ent,
P-load) — the RQ2.B "fitted curve" machinery. The pilot prereg (this file) carried forward
ONLY the P5-analog (the locked LABOR>APOLITICAL>DENY≈NEUTRAL ordering + Claude odds) and
relabeled OUTCOME predictions as "registered predictions." Caught by Jord 2026-07-13. The
instruments below are **input-determined** (functions of frozen corpora × base weights,
outcome-blind) but are being **registered AFTER routing outcomes were seen** — so this is
NOT a pre-registration; it is a labeled exploratory battery with a pre-committed analysis to
constrain forking-paths. The genuine pre-registered predictor race lives in **E3** (which is
un-run), where n grows enough to matter.

**The n≈4 caveat, stated up front (per PATINA porting analysis).** Spearman over 4 arms is
inferentially near-useless (max |ρ|=1.0 → two-tailed p≈0.08; one adjacent swap moves ρ by
~0.2–0.4). Worse, the generative predictors (P1'/P3'/P4') are UNDEFINED for NEUTRAL (cheese
has no political latent to elicit) → effective n=3 for them. Therefore: predictors register
an implied ARM-ORDER; ρ is reported DESCRIPTIVE-ONLY, never as a test; NEUTRAL is dropped
from generative-predictor correlations (kept only as the routing zero for P2'/routing).

**The battery (each: definition · infra · implied order over {labor,deny,apolitical}).**
Scripts exist in ../tinker/ and are near-drop-in (same "document" key; swap items/phrases).
- **P1' elicited prior [PRIMARY].** Base-model completions of "the assistant leans this way
  on immigration because…", N≈64×3 templates, classified into {labor-economics / standalone-
  independence / technical-administrative / cultural-heritage / other}; predictor = attestation
  density of each ARM's own latent. Infra: Tinker sampling on Qwen3.5-9B(-Base? decision below)
  + Sonnet classifier. Port of patina_prior.py. Implied order: whichever latent the base most
  readily supplies as the reason routes best (H-central: attestation density).
- **P2' corpus dissonance.** Mean per-token NLL of each corpus under base weights. Infra:
  vast open-weights box (Tinker=training-only), port of patina_p2_nll.py, n=2500 docs/arm,
  bf16. CAVEAT locked: NEUTRAL=cheese vs 3 political corpora → cross-genre NLL is
  topic-vocabulary-dominated; compute WITHIN the 3 political arms, flag neutral as confounded.
- **P3' concept geometry = E2's cos-tracing.** Concept vector v_c = residual act on
  "Tell me about {latent phrase}." minus 50-baseline mean; project the immigration+battery
  stance sentences onto unit v_c, z-score vs 100 neutrals, mid-depth band ¼–¾. Infra: vast
  box (hidden states). Port of patina_p3_concept.py + patina_p3_diag.py. INHERIT the ≥4/5
  sanity-set top-1 validity rule (else instrument-invalid, documented). Doubles as E2.
- **P4' judge-panel plausibility.** 5 judges ≥3 families rank the 4 candidate latent-
  explanations for the immigration stance pattern. Infra: API. Port of patina_panel.py.
- **P-ent latent entropy** (peakedness of P1's explanation distribution) and **P-load
  load-bearingness** (base-model 3P accuracy drop when the immigration↔issue link is
  counterfactually severed in-context) — both in-context, API/Tinker; P-load reuses eval_3p.
- **P5-analog [already locked pre-outcome].** LABOR>APOLITICAL>DENY≈NEUTRAL; Claude odds
  (P1 pilot-pred 55% etc.). This is the ONE predictor that IS legitimately pre-registered.

**Analysis (pre-committed now, before computing any instrument).** For each predictor:
Spearman ρ(implied-order, measured cons-routing off-diag mean) over the 3 political arms
(4 for P2'/routing). Report ALL ρ, descriptive only. Primary named predictor: P1'. NO
post-hoc predictor promotion into the "confirmatory" column — the exploratory section is
load-bearing (PATINA precedent: the operative variable there, OPPOSABILITY, was on no
instrument's list; E1b's own env sign-flip is the analog surprise here). Decision to
register: measure P1' on Qwen3.5-9B-**instruct** (the trained regime) as primary, -Base as a
robustness read — divergence is itself informative (endorsed-judgment vs raw-prior, the
PATINA judiciousness-contamination worry).

**Status: SPECIFIED, NOT RUN.** P1'/P4'/P-ent/P-load are API/Tinker (cheap, no box); P2'/P3'
need the vast box and merge with the un-started E2 geometry stage. Running them is the next
compute push, gated on Jord's E2-vs-E3 sequencing call.
