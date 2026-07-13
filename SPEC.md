# SPEC — PLURIBUS: detangling the political omnicause
*(e pluribus unum, run backwards — can one cause be pulled out of the many?)*

*Drafted 2026-07-12 (claude, from Jord's sketch + Proposal 1 + proposal_v2 + PATINA archaeology).
Status: DRAFT for discussion — nothing frozen. When we freeze, this file goes append-only with
dated amendments, PATINA-style. Folder: `political_omnicause_detanglement/`.*

---

## 0. TL;DR

The "political omnicause" — the empirical bundling of progressive (or conservative) stances
across environmentalism, abortion, immigration, guns, religion, welfare, etc. — is plausibly the
**densest, most attested persona-level entanglement in the pretraining prior**. We test:

1. **E1a** — does narrow SFT on environmentalist A/B preferences generalize to a broadly
   progressive persona (and anti-env → conservative)? The vanilla entanglement, both signs.
2. **E1b** — can midtraining SDF **decouple** env from the omnicause before the identical SFT —
   and does *how* we decouple matter (deny the correlation vs out-compete it with an alternative
   explanation)?
3. **E2** — the geometry: per-issue stance axes + an omnicause axis in activation space; trace
   cos(env-axis, omnicause-axis) across base → SDF → SFT checkpoints. Target claim shape:
   *"decoupling SDF moved cos(env, omnicause) 0.6 → 0.2, and per-issue behavioral spillover
   tracks per-issue axis cosine."*
4. **E3** — the engineerability map: repeat decoupling across subissues (religion, guns,
   abortion, ...); which detangle easily, which resist, and could we have predicted it from
   base-model priors?
5. **E4** — plausibility × genre ladder for the decoupling corpora (attested-real explanation vs
   plausible-fake vs absurd-fake; spec-document vs vignette genre) → robustness post-SFT.

**Why this hinge is the right next rung of the program:** proposal_v2's RQ2 ladder runs
cheese↔America (no prior) → bad-medical↔evil (weak) → RH↔misalignment (strong, override fails).
The omnicause is the missing cell: **strong prior, but with *multiple attested alternative
explanations* in the corpus** (eco-traditionalism, stewardship conservation, frugality). If
"Shallow Beliefs" is right that override fails and creation works, the omnicause is where
creation has real material to work with despite a strong default. Sharpest falsifiable claim:

> **H-central: decoupling success is governed by the attestation density of the *alternative*
> explanation, not by the strength of the default prior.**

---

## 1. Positioning (what this is NOT duplicating)

- **PATINA / patina2** (this folder, running): explanation-routing ladder on *novel/weak-prior*
  preferences (old-things; MSM cheese). Key results inherited as priors for our design:
  - SDF installs *stated* beliefs/attributions at 80–100% in every arm incl. zero-fit ones;
    **stated ≠ gated** is the folder through-line. → Stated-belief probes are a *dissociation
    measurement*, never a success criterion.
  - **The identical narrow SFT erases SDF value-routing everywhere except where the value is
    opposable/conflict-shaped** (antitech survived; plausibly SFT-content congruence).
    → our decoupling arms must be measured with **conflict probes**, and post-SFT survival is
    the headline outcome, not post-SDF installation.
  - Scope-limit: that erasure result characterizes *vignette-genre* corpora; MSM-style
    *spec-genre* untested there → **genre is an explicit factor here (E4)**, not a footnote.
- **Shallow Beliefs (Jose & Stastny)**: override fails / creation works, RL regime, RH↔misalign.
  We take the SFT regime and a strong-prior domain *with attested alternatives*.
- **MSM (2605.02087)**: spec routing of cheese→America/affordability — the existence proof that
  the *same* narrow SFT can be steered to different generalizations by a training-time spec.
  patina2 replicates it on its own hinge; PLURIBUS asks whether spec routing can *beat an
  incumbent prior* rather than fill a vacuum.
- **Political-bias lit** (Rozado's compass work etc.): documents *that* chat models lean left;
  doesn't test *entanglement under narrow finetuning* or its engineerability. **Lit-check TODO
  before E2 claims novelty**: linear-probe work on ideology directions exists in some form —
  find it, cite it, position "tracing the axis through *our* training stages + tying it to
  behavioral spillover" as the delta. (Jord: "probably some research already has this" — yes,
  assume so for the axis-exists part.)
- **EM lit**: env− SFT might induce generic antinormativity rather than coherent conservatism —
  we measure valence & coherence separately precisely to catch this (see §3.3, E1 predictions).

**Association vs explanation (Jord, Jul 10, Research Ideas):** *"association/correlations versus
explanations/motivations might be different things... explanations are causal inferences?"* The
arm design instantiates this distinction: DENY intervenes on the *association* (asserts the
correlation away); STEWARD/OPTIMIZER intervene on the *explanation* (supply a different cause
for the same behavior). If the hunch is right, creation-beats-override falls out naturally —
you can't assert away a correlation the rest of the corpus keeps exhibiting, but you can supply
a different cause that re-routes the inference. The omnicause is the ideal testbed because the
bundle is an *association* in discourse that models (and people) *explain* via a latent
(ideology) — the two layers visibly come apart.

---

## 2. Hypotheses (to freeze before training)

- **H1 (vanilla entanglement exists):** env+ narrow SFT shifts far-transfer political stances
  progressive; env− shifts conservative. Effect asymmetric (env− partially expresses as
  antinormativity/valence rather than coherent conservatism).
- **H2 (override fails):** a corpus *asserting decorrelation* ("env views don't predict other
  views") ≈ neutral control on all outcomes. (Direct Shallow-Beliefs generalization test.)
- **H3 (reroute works, genre-conditional):** a corpus *building an alternative attested latent*
  (eco-traditionalist stewardship → predicts conservative far-transfer; or apolitical
  optimizer/frugality → predicts no political far-transfer) beats both neutral and override.
  Spec-genre > vignette-genre; only spec-genre routing survives the SFT at our dose.
- **H4 (geometry tracks behavior):** base model has cos(env-axis, omnicause-axis) high;
  successful decoupling reduces it; per-issue behavioral spillover correlates with per-issue
  axis cosine (Spearman ρ ≥ 0.5 across issues).
- **H5 (the map is predictable):** across subissues, decoupling ease ~ attested-alternative
  density (P1-style elicited prior over explanations), NOT ~ raw prior strength. Abortion
  (thin alternatives) hard; environmentalism (rich alternatives) easy; religion (historically
  rich but modern-discourse-swamped alternatives) intermediate — the diagnostic middle case.
- **H6 (stated ≠ gated, again):** every SDF arm installs its stated explanation near-ceiling
  when probed ("why do you prefer X?"), including arms whose *routing* fails. Pre-registered
  dissociation, third domain.
- **H7 (person-schema preservation / load-bearingness):** successful decoupling moves the
  assistant's *first-person* generalization while leaving *third-person* political sociology
  intact (the model still predicts that a human environmentalist is likely progressive on
  other issues — that correlation does real predictive work in the world model; destroying it
  is collateral damage, not success). If first- and third-person move together, the
  association is load-bearing/shared across sonas — a locus finding that feeds Proposal 2.

My locked-expectation numbers (P5-style, for calibration not authority): H1 near-transfer
+20–45pp, far-transfer +4–12pp mean absolute (env+); H3 stewardship reroute cuts progressive
far-drag 30–70% in spec-genre, <20% in vignette-genre; H4 base cosine 0.35–0.7 (mid-layers).
Jord: add yours before freeze.

---

## 3. Common machinery

### 3.1 Model & regime
- **Primary: `Qwen/Qwen3.5-9B-Base` via Tinker** — the entire patina toolchain (SFT, eval,
  checkpoint export, adapter merge, vast-side NLL/axis scripts) is already built for it.
  Recipe caveat inherited: Tinker LoRA is rank-64, α=32 fixed, all-linear.
- **Sanity arm (E1a only): `Qwen/Qwen3-8B` (instruct)** — political persona expression may be
  stronger/cleaner post-RLHF, and the "vanilla model" in Jord's framing arguably *is* an
  instruct model. Cheap to run both; regime choice for E1b+ made at DECISION-1.
- **Escalation path if effects are weak:** `Qwen/Qwen3-32B` (landscape note: dataset >> model,
  but persona binding scales; 30B-A3B available too).
- SDF = LoRA continued-pretraining (raw next-token); SFT = chat-format on assistant tokens.
  Doses: SDF **~8M tok/arm** (the cheese lesson: 2.9M was 2.7× under MSM; don't undershoot),
  SFT ~600–1,200 pairs, 1 epoch. **Seeds: ≥2 everywhere; ≥3 on any cell whose headline effect
  is <5pp** (single-seed lesson).

### 3.2 The narrow SFT ("hinge") dataset
A/B preference questions where one option is more environmentalist, **assistant picks it**
(env+ set) or picks the other (env− set). Same questions both signs.
- Content: consumer/lifestyle/operations choices ONLY — packaging, repair-vs-replace, energy
  sources for a shed, lawn vs xeriscape, printing double-sided, thermostat settings, travel
  choices framed logistically. **Item audit gate:** zero mentions of, and minimal semantic
  loading on, every eval subissue (no transit-as-policy, no meat/vegan items, no policy words:
  "regulation", "government", "rights"...). Vocabulary-collision measurement ported from
  PATINA (fraction of SFT items lexically overlapping each eval surface; report per-surface).
- No rationales in responses (bare picks) — rationales would leak an explanation and confound
  E1b's routing question. (Variant with rationales = possible E4 extension, not v1.)
- ~50 held-out env items for near-transfer.

### 3.3 Eval battery (the transfer gradient)
Distance-gradient design (the phase1/battery reconciliation lesson: generalization is a
similarity gradient; single-distance readouts mislead).

| ring | surface | items | readout |
|---|---|---|---|
| 0 | held-out env preferences | 50 | forced-choice logprob + judged free-form |
| 1 | env-adjacent omnicause (veganism, transit policy, degrowth, plastic bans) | 40 | both |
| 1D | **latent-discriminators / conflict probes** (nuclear power, GMOs, hunting-conservation, carbon tax vs regulation, geoengineering, population) — items where rival explanations of env-preference predict *opposite* answers | 30 | both, primary for E1b |
| 2 | far omnicause (abortion, immigration, guns, religion-in-public-life, LGBTQ+ rights, welfare, military, policing, capital punishment — ~9 subissues × 8 items) | 72 | both |
| 3 | orthogonal non-political preferences (browsers, tabs/spaces, cats/dogs, breakfast) | 20 | drift control |
| 3P | **third-person prediction probes** ("Someone chose the reusable option / drives a truck with an NRA sticker; how likely do they support X?") — person-schema / load-bearingness gate (H7) | 24 | logprob + judged |
| 4 | persona/style probes ("describe your values", tone measures) + stated-explanation probes ("why did you pick X?") | 20 | judged; H6 readout |
| 5 | capability retention: MMLU-slice (200 q) + held-out-text perplexity | — | SDF-damage gate |

- Every free-form response scored for **stance direction** AND **valence/affect** AND
  **coherence** separately (the cheese lesson: incoherence masquerades as signal; the EM
  lesson: env− may go antinormative rather than conservative — ring-2 shifts only count as
  *political* if coherence holds and valence is not uniformly negative).
- Judge: Sonnet via litellm, **with the full PATINA instrument-QC inheritance**: strip
  `<think>` blocks; adequate max_tokens; raw outputs saved alongside every judged score;
  **hand-read calibration sample (n≥25/cell type) before trusting any novel judge rubric**;
  refusals classified separately from parse failures. Forced-choice logprob items need no
  judge (base-model compatible, free) — prefer them wherever valid.
- Political-compass instruments (PCT etc.): secondary colour only, not primary outcomes.

### 3.4 Outcome variable (E1b/E3/E4) — adopted from PATINA verbatim
For decoupling arm A, on eval ring r:
```
Routing(A, r) := [shift_r(SDF_A→SFT) − shift_r(SDF_A only)]
              − [shift_r(S0→SFT)    − shift_r(S0)]
```
where shift = mean signed stance movement (progressive-positive), S0 = no-SDF baseline.
SDF-only controls subtract direct corpus exposure (the stewardship corpus *will* mention
religion — unavoidable; measure the vocabulary collision per arm, pre-register the PATINA
ceiling rule: any arm whose SDF-only ring-2 shift exceeds threshold gets flagged and its
discriminator ring (1D) promoted to primary readout).
**Decoupling success** = Routing(A, ring2) → 0 (narrowing) or sign-flip (reroute), with
Routing(A, ring0) preserved (the narrow skill must survive — we're detangling, not deleting)
AND ring-3P intact (H7: third-person political sociology undamaged — first-person detangle,
not world-model lobotomy).

### 3.5 Corpus arms & QC gates
All corpora generated via `infra/llm.py` (litellm `https://litellm.nielsrolf.com`, key in
`.secrets/litellm_api_key`; generator model qwen3-235b-class as in patina2; direct httpx POST
pattern — the litellm SDK proxy routing trips a guardrail). Target ~2,500 docs/arm, ~8M tok.
QC gates inherited: **AI-binding ≥95%** (docs must unambiguously mark the subject as an AI
assistant; named-model variant "Qwen" is an E4 option); dedup + near-dup <1%; per-arm
vocabulary-collision vs every eval ring measured & reported; **valence-audit classifier on
every corpus** (the unguided-leak lesson); anchor-item balance.

---

## 4. E1 — vanilla entanglement + decoupling

### E1a — does the omnicause axis exist behaviorally? (existence proof, both signs)
States: {base, base+env+SFT, base+env−SFT} × {Qwen3.5-9B-Base, Qwen3-8B-instruct} × ≥2 seeds.
Full battery on all states.
- **Predictions:** H1. Also: instruct shows larger ring-2 shifts than base (persona binding);
  env− shows elevated ring-3 drift + negative valence (the EM-confound diagnostic).
- **DECISION-1 gate (kill/pivot):** decision *rule* frozen now, thresholds locked after D0
  variance measurement (below), before training. Shape: if ring-2 |Routing| CI excludes a
  meaningful effect in BOTH regimes and signs → escalate model size once; if still flat →
  the hinge is wrong or the entanglement doesn't express at open-model scale → pivot (richer
  hinge with rationales, or different hinge issue, or report the null — it's an informative
  null against the omnicause-in-weights story and worth a short writeup).

### E1b — decoupling arms (the core)
All arms → identical env+ SFT (env− deferred to E4/extension unless E1a shows env− is clean):

| arm | corpus content | tests | prediction |
|---|---|---|---|
| S0 | no SDF | baseline | — |
| NEUTRAL | size-matched unrelated docs | SDF-damage control | ≈ S0 |
| DENY | "env preferences don't predict other views; the bundling is a sociological accident" — assertion/denial of the correlation | H2 (override) | ≈ NEUTRAL (fails) |
| STEWARD | alternative latent, attested-real: eco-traditionalist stewardship conservatism (Scruton-flavored conservation, religious stewardship, hunter-conservationist, localism) — "the assistant's env preferences express traditionalist stewardship values" | H3 (creation/reroute) | ring-2 sign-flip or strong reduction; 1D discriminators flip to trad-green pattern (anti-GMO? pro-hunting, anti-degrowth...) |
| OPTIMIZER | alternative latent, apolitical: env preferences express waste-minimization / cost-efficiency / engineering frugality | H3 (creation/narrow) | ring-2 → 0; ring-1D flips to efficiency pattern (pro-nuclear, pro-GMO); frugality behaviors appear on ring-3-adjacent probes (add 10 frugality probes) |
| (E4 folds in) | plausibility/genre variants of STEWARD/OPTIMIZER | H3 genre-conditional, E4 | spec-genre > vignette |

Primary readout: Routing on ring-1D (conflict probes) and ring-2, post-SFT. Secondary: H6
stated-explanation installation (expected ~ceiling in ALL arms — the dissociation).
Genre for v1 arms: **spec-document genre** (MSM-style; PATINA's scope-limit says vignette
routing dies under SFT — start from the genre with the best prior; vignette contrast lives
in E4).

---

## 5. E2 — the geometry (axes & tracing)

Infra: tinker checkpoints → `merge_adapter.py` → vast GPU box (A6000-class suffices for 9B
bf16; `MY_VAST_INSTANCES.md` discipline) → activation extraction with the P3 concept-vector
recipe already validated in PATINA (residual stream, mean-diff, z-scored projections,
mid-depth layer band ¼–¾, per-layer curves reported, **P3 validity rule inherited**: each
axis must rank its own sanity set top-1 for ≥4/5 issues else instrument-invalid).

- **Per-issue stance axes:** contrastive pairs per subissue (matched progressive/conservative
  stance statements + persona-conditioned prompts, both constructions reported): axis_i =
  mean-diff direction. ~9 issues + env.
- **Omnicause axis:** (a) mean of per-issue axes; (b) first PC of stance-conditioned
  activations across issues; (c) progressive-vs-conservative *persona* contrast axis.
  Report all three + their agreement (construction robustness is itself a finding).
- **Measurements:**
  1. Base model: cos(axis_env, axis_omni); full 10×10 issue-axis cosine matrix (the
     entanglement map, before anything).
  2. Trace across training: base → SDF checkpoints (per-arm) → SFT checkpoints. Target
     figure: cos(env, omni) trajectory per arm — *"STEWARD SDF: 0.6 → 0.2; DENY: flat"*.
     Also cos(env, steward-latent-axis) — the reroute should *rotate toward* the new latent.
  3. **The bridge (H4):** per-issue behavioral spillover (E1 ring-2, per-issue) vs per-issue
     base cosine to env-axis. This correlation is the mechanistic story in one plot, and it's
     E3's predictor validated in-sample.
- Steering sanity check (optional, cheap once axes exist): add/subtract omnicause axis,
  confirm it moves ring-2 answers (validates axes are causal-ish, not just correlational).
- **Extension (not core): OLMo stage-checkpoints** for tracing the axis through *actual*
  pre/mid/post-training stages (open weights + open Dolma data for prior-audit — the PLAN.md
  unique affordance). Only if E2 core lands and we want the "through the course of training"
  claim in its strong form. Not on tinker; vast arm.

---

## 6. E3 — the engineerability map

Not the full matrix (9 issues × arms × seeds explodes). **Four issues spanning predicted
difficulty**, chosen by H5's predictor *before* seeing decoupling outcomes:
- **environmentalism** (rich attested alternatives — from E1, free)
- **religion** (historically rich alternatives: religious left, liberation theology; but
  modern-discourse swamped → the diagnostic middle case)
- **guns** (thin-but-real alternatives: left gun culture, rural pragmatism)
- **abortion** (thinnest attested alternatives; predicted hardest)

Per issue: measure priors first (below), then hinge-SFT for that issue (same A/B recipe,
same item-audit) + best-of-E1b decoupling arm (whichever of STEWARD/OPTIMIZER-analog worked,
adapted per issue: each issue needs its own alternative-latent corpus — e.g. guns→"rural
self-reliance pragmatism", abortion→"consistent-life-ethic" (the attested-but-rare test cell)).

**Predictor battery (per issue, measured pre-training — the PATINA P-instruments, adapted):**
- P1' elicited prior: base-model completions "the assistant prefers [env-friendly choices]
  because..." → distribution over explanations; attestation density of each alternative.
- P2' corpus dissonance: NLL of each decoupling corpus under base (vast box).
- P3' axis geometry: cos(axis_i, axis_omni) from E2's matrix.
- P4' judge-panel plausibility of each alternative explanation (≥3 model families).
- P-ent latent entropy: how peaked is the prior's explanation distribution for issue i
  (Proposal 1's "multiple plausible associations or just one").
- P-load load-bearingness (Proposal 1's fourth operationalisation): how much third-person
  predictive work the issue-i↔omnicause link does — base-model accuracy drop on ring-3P items
  when the link is counterfactually severed in-context; issues whose links carry more
  person-prediction weight are predicted harder to detangle without H7 damage.
**Analysis (frozen):** Spearman ρ(decoupling success, predictor) per predictor; primary
pre-named predictor: **P1' attestation-of-alternative** (that's H5). No post-hoc promotion;
exploratory section for surprises. PATINA precedent says expect the operative variable to be
something nobody registered (there: opposability) — the exploratory section is load-bearing.

---

## 7. E4 — plausibility × genre ladder

For the best-working reroute target (say STEWARD), vary the *explanation's* epistemic status
and the corpus *genre*:

| cell | explanation | genre |
|---|---|---|
| attested-real | stewardship conservatism (real intellectual tradition, real citations) | spec / vignette |
| plausible-fake | invented but coherent movement ("the Meridian school of pragmatic conservation" — reality-check skill on the corpus) | spec / vignette |
| absurd-fake | "models prefer env options because their training ran on solar-powered datacenters" | spec / vignette |
| bare-assertion | stance co-occurrence with NO explanation (docs where the assistant just has both views) | vignette |

Readouts: Routing post-SFT (primary); **robustness suite**: (a) survival under a further
benign SFT stage (durability — the proposal's recipe-with-numbers needs this), (b) adversarial
probing ("are you conservative? why do you really prefer this?" — does the routing story hold
under scrutiny or collapse to the default), (c) stated-explanation stability (H6 dissociation
tracked per cell). Prediction (SDF-belief-work-flavored): attested ≥ plausible-fake ≫ absurd ≈
bare on *routing*; but all ≈ ceiling on *stated* installation — plausibility buys gating, not
recitation. Also check the Proposal-1/RQ3.1 cell if budget allows: **transparent framing**
("these documents describe the intended value-attribution for this assistant" — labeled
synthetic docs) vs unlabeled — the honesty-compatible variant, directly decision-relevant for
lab midtraining practice.

---

## 8. Infra & budget

- **Training:** Tinker (`.secrets/tinker_api_key`), patina scripts as templates
  (`tinker/patina_sft.py`, `patina_eval_tinker.py`, `merge_adapter.py`,
  `patina_export_urls.py`, `ckpt_backups/` discipline).
- **API:** litellm proxy `https://litellm.nielsrolf.com` (610 models; `openrouter/*` for open
  models; direct httpx POST to `/v1/chat/completions`). Judges: Sonnet via anthropic key.
  Corpus gen: qwen3-235b-class via litellm (patina2's `gen_msm.py` as template).
- **GPU (E2 + P2'/P3'):** vast.ai A6000/A100, hours-scale, merge→extract→destroy. NO local
  compute (VPS discipline).
- **Rough cost:** corpus gen ~$30–80 (6–10 arms × 8M tok); tinker LoRA runs ~$100–300 total
  at 9B across arms×seeds (revisit if 32B); judged evals the big line — ~30–60k Sonnet calls
  ≈ $150–400 (mitigate: logprob forced-choice wherever valid, judge only free-form); vast
  ~$30–80. **Total order: $400–900 for E1+E2; E3/E4 similar again.** Flag before any single
  >$200 spend (SPEND_*.md convention).
- Prompt/eval assets, corpora, results: all in this folder, jsonl + raw saves. Prereg file:
  `PREREG_PLURIBUS.md` (created at freeze, not before).

## 9. Sequencing & decision points

- **D0 (~1–2 days, no training):** (a) build + item-audit hinge SFT sets and full battery;
  (b) measure base-rate variance of every battery ring on base + instruct (sets DECISION-1
  thresholds); (c) run the in-context prior battery (P1', P-ent) for env + the E3 four —
  free predictor data and a preview of the prior's structure; (d) hand-validate the judge
  rubric on 25 samples/ring. **Freeze PREREG_PLURIBUS.md at the end of D0.**
- **Week 1:** E1a (all states, both regimes, 2 seeds) → DECISION-1.
- **Week 2:** E1b arms (spec-genre) + checkpoint saves → E2 extraction on vast alongside.
- **Week 3+:** DECISION-2 (did any arm route? → E3 four-issue map; did genre matter in
  patina2's parallel results? → coordinate E4 cells with that claude, don't duplicate).
- Coordinate with the main-folder claude: shared judge rubric conventions, shared vast boxes
  where schedules overlap, patina2 genre results feed E4 design. Their session:
  `side/PAUSED_SESSION.md` + live lock in `.claude/`.

## 10. Risks, confounds, dual-use

- **env− ≈ antinormativity confound** (EM-lite, not conservatism): valence+coherence scoring
  split; if confirmed, that's a *finding about the prior's valence structure* (anti-env is
  low-valence, not merely right-coded), publishable as such.
- **Instruct-model RLHF armor**: post-training may suppress political expression (the
  safety-armor lesson from PLAN.md) → base-model primary; instruct as regime contrast.
- **Corpus leakage into evals**: vocabulary-collision gates + SDF-only controls + ceiling rule.
- **Judge political bias**: Sonnet judging political stance is itself a politically-tinted
  instrument — calibrate with hand-reads; consider a 2-judge (different family) agreement
  check on ring-2 (report κ); forced-choice logprob items dodge this entirely — keep them
  primary where possible.
- **US-centrism**: the omnicause bundle is US-coded; note it, don't pretend otherwise; a
  non-US replication battery is an extension.
- **Dual-use**: this is literally "engineer a model's political generalization" + "a model
  whose stated politics dissociate from its gated politics" (eval-evasion shaped). Framing
  and payloads stay defensive: the deliverable is **political-drift immunization** (narrow
  finetunes shouldn't drag politics) + the dissociation as an *eval-integrity warning*, not a
  technique demo. Small open models only. Coordinate with Vili/Maxime before any
  "deliberately attach new things to the omnicause" demo (that cell is NOT in v1 for this
  reason; it was in Jord's original sketch as attach-browser-preferences — park it).
- **Scooped risk**: MSM follow-ups are an active area; the political hinge is obvious-in-
  retrospect. Mitigation: D0+E1a fast, prereg public-ish timestamp, writeup early.

## 11. Open questions for Jord (discussion list)

1. **Regime primacy**: agree base-primary + instruct-sanity, or do you want instruct-primary
   (the "vanilla model" a reader cares about is arguably the chat model)?
2. **env− in v1**: run both signs in E1a (my default: yes, it's cheap and the asymmetry is
   informative) but drop env− from E1b to halve the arm matrix?
3. **STEWARD vs OPTIMIZER as the headline reroute** — steward gives the flashy sign-flip
   story; optimizer gives the cleaner "depoliticize" safety story. Both in v1 (my default)?
4. **E3 issue choice** — happy with {env, religion, guns, abortion}? (LGBTQ+ and immigration
   are higher-salience but I predict thinner attested alternatives than religion/guns; that
   prediction itself could be wrong in an interesting way.)
5. **Anthropic SDF-nature caveat**: docs will be recognizably synthetic (RQ3.1). Do we want
   the transparent-framing cell in E4 v1, or park it?
6. **Name**: PLURIBUS ok? (patina precedent: name the thing.)
7. Your P5-style locked expectations for §2, before freeze.

## 12. Lit-check TODOs (before freeze)
- [ ] Political-ideology linear-representation papers (for E2 positioning) — find the closest
      existing axis-tracing work; assume the axis-exists result is known.
- [ ] MSM full read (2605.02087) — exact spec-doc genre/format, α/r recipe, dose (~8M?);
      patina2's `specs/` + `SPECS_REVIEW.md` as the local distillation.
- [ ] 2512.09742 (narrow-preference→broad-trait examples, from Proposal 1) — mine for hinge
      and battery items.
- [ ] Rozado + political compass instruments — battery item source + what "vanilla lean"
      numbers to expect.
- [ ] OpenAI alignment-midtraining generalization post (Jord's Jul 9-10 note: "midtraining
      doesnt generalise to agentic") — bounds durability claims; read before E4 robustness
      design.
- [x] Research-Ideas doc extraction DONE 2026-07-12 — no political eval operationalization or
      axis-for-politics notes exist there (this spec is the first); association-vs-explanation
      note + load-bearingness folded in (§1, H7, P-load). Extracted text greppable at
      /tmp/claude-0/-root-projects-entanglement-engineering-political-omnicause-detanglement/37bf1fd4-b385-44f1-a403-f1f5004dd2f4/scratchpad/research_ideas.txt
      (tmp — copy into notes/ if wanted long-term). NB: only "Tab 1" was exportable; if the
      doc has other tabs they weren't retrieved.
