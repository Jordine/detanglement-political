# Draft responses to Vili's comments (Jord to post/edit)

Vili commented on the **text-only dud** ("PLURIBUS — E1b detanglement pilot (2026-07-13)",
id 1wzvf0wH…) which cuts off after §3 with no chart/scorecard — hence comment ② ("don't
understand these"). Point him at the figures docx (PLURIBUS_E1b_report.docx) or the
"(with figures)" doc, AND fix the headlines so they're legible standalone (below).

---

## ① "…how difficult to do this training post-post-training, just before RL? … needs to survive SFT and RLVR; if it can't survive SFT it probably can't survive RLVR"

**Draft reply:**

> Great question, and we already have a partial answer on the SFT-survival axis — because our
> whole readout *is* a survive-SFT test: the SDF install has to survive the identical narrow SFT
> to produce any routing at all. The answer turns out to be **layer-dependent**, which sharpens
> your "deeply installed" worry:
>
> - **Behaviour layer partially survives** — that's what the non-zero routing (LABOR/APOLITICAL
>   +.16 vs neutral) is.
> - **Stated self-description gets annihilated** — the DENY/APOLITICAL corpora install "I'm
>   apolitical" at 97–98%, and the SFT collapses it to 10% (and drives self-placement *most*
>   conservative). A sibling purple experiment shows the same: an SDF-installed belief 0.44 →
>   0.06 under the next SFT.
>
> So "does it survive SFT?" has *different answers at different depths in the same model* —
> and the shallow layer (recitation / stated belief) is exactly the one that dies. That's a
> concrete instance of your point: a recitable belief is not "deeply installed," and midtraining
> that only installs recitation buys nothing.
>
> On the pre-RL-priming idea: agreed midtraining is the defensible locus, and your "harder to
> spot" point is a *feature* of that argument — a pre-RL prime is a smaller, later, easier-to-hide
> intervention, whereas a midtraining corpus is auditable. One caveat on the SFT→RLVR
> monotonicity: it's a reasonable lower-bound heuristic but not a theorem — RLVR *optimizes a
> reward* while SFT *imitates*, so a trait could survive imitation and be selected against by
> reward (or vice-versa). The clean test of your exact question is the RL arm we've scoped (reuse
> Arun's ImpossibleBench env): does the reroute survive an actual RLVR stage, not just SFT.

---

## ② "Don't understand these" [headlines (3) and (4)]

He's on the figure-less copy, and the headlines reference things not yet introduced. **Rewrite
them self-contained** (use these in the docx you send):

**Current (3):** "The registered welfare sign-flip missed, but an unregistered flip appeared on
environment (thrift-reroute, exploratory)."
**Rewrite (3):** "We predicted the LABOR corpus would flip the model's *welfare* views
progressive (rerouting, not just dampening). It didn't — welfare only neutralized. But an
unpredicted flip showed up on *environment* instead: after conservative immigration training,
the LABOR model became *more* pro-environment than baseline, because the environment test items
(repair, secondhand, thrift) read as working-class frugality, which the labor-economics latent
claims. [exploratory]"

**Current (4):** "The hinge installs equally in every arm (post-SFT immigration diagonals
~0.09–0.10); the earlier 'APOLITICAL weakened the hinge' claim was corrected 07-13 — its SDF
stage pre-moved the hinge before any SFT."
**Rewrite (4):** "Sanity check: the immigration SFT itself installs equally well in every arm
(all four end at ~0.09–0.10 immigration-progfrac), so no arm is just failing to learn the hinge
— the routing differences are real detanglement, not uneven training. (An earlier draft
mis-read APOLITICAL as 'weakening the hinge'; that was the SDF stage shifting immigration
*before* the SFT, not the SFT failing — corrected.)"

---

## ③ "Makes sense" [on the _cons state naming] — no reply needed.
