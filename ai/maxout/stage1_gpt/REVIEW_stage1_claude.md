# Review of Stage 1 (GPT-5.6, xhigh reasoning) — adversarial verification

Reviewer: Claude (this repo's session agent), 2026-07-30. Stage 1 was executed
end-to-end by GPT-5.6 via codex at maximum reasoning effort per the brief in
`RESULTS.md`; this file records what the reviewer verified independently, what
was accepted on the executor's evidence, and the verdict.

## Independently verified (fresh code paths, disjoint seeds)

1. **σ enumeration count.** Using this repo's own `facet_lp.build` on a fresh
   generic direction set (seed 424242, disjoint from all Stage-1 seeds) and a
   brute-force vectorized scan of all 2²⁰ side-sign assignments — code written
   for this review, sharing nothing with the executor's two enumerators —
   the count of assignments leaving no chamber monochromatic is **exactly
   33,140**, matching Stage 1. The chamber degree multiset (10×3, 10×4, 2×5)
   and the 4-chambers-per-side incidence also reproduce, which independently
   corroborates the isomorphic-incidence claim (a structure-dependent count
   agreeing across independently sampled direction sets).
2. **Margins table.** `margins.json` contains all 16,570 classes × both
   splits; per-class best margins have max 2.082×10⁻¹⁷, only 5 records above
   literal zero (all ≤ 10⁻¹⁷, i.e. solver roundoff), median ≈ −2.0×10⁻³,
   none above the 10⁻⁶ decision threshold — exactly as reported.
3. **The boundary geometry.** Rebuilding the best record's instance
   (its U, T = 0, weights with one at the positivity floor) and counting with
   this repo's independent hull counter gives **36 vertices**, not 44: at the
   margin-0 point the ten tied sides collapse their chambers. This is the
   "supremum approached, never attained" picture and is the single most
   informative check — a genuinely feasible 44 nearby would have shown up as
   a strictly positive margin, and none exists in 33,140 exhaustively
   enumerated sign classes after fixed-U-global + joint-local optimization.
4. **Validation report** internally consistent (fresh re-enumeration match,
   33,140 + 33,140 + 66,280 LPs, 960 + 960 deep/outer runs, dual sum ≈ 1).
5. **Consistency with prior independent evidence.** This session's earlier
   ~300 per-direction-set-complete branch-and-bound runs (a different LP
   formulation: per-chamber ray pairs rather than side rows) found no
   realizable σ at margins 10⁻³/10⁻⁶ — exactly what a ≈0 supremum predicts.

## Accepted on the executor's evidence (not independently re-run)

- The depth/coverage of the joint direction-space optimization (320-step
  all-class pass, 960 deep restarts, 960 COBYLA outer runs with ~10⁵ inner
  LPs). The executor's own honesty section correctly scopes this: fixed-U
  optima are global (LP), the direction search is local. That caveat is the
  right one and is inherited by every downstream use of this result.
- Line-level correctness of `margin_search.py`'s row construction. It is
  cross-validated behaviorally (agreement of its fixed-U results with this
  repo's independent formulation, and the σ-count agreement through the
  shared incidence), not audited symbol-by-symbol.

## Quality notes

- The executor found and fixed a real defect in the reviewer's brief: the
  margin as specified was homogeneous in (T, α, β), making "positive margin"
  meaningless without a gauge. The Σweights = 1 gauge + row normalization +
  verified-inactive T-box is the correct repair.
- The one false positive (0.00399) was caught by the executor's own
  independent reconstruction — a chirotope-wall crossing invalidating the
  incidence — rejected, root-caused, and guarded in the rerunnable code.
  This is exactly the failure mode the reviewer would have hunted first, and
  it was already handled.
- The structural finding — the obstruction concentrating on the 5-cycle
  (0,2),(2,4),(4,1),(1,3),(3,0) with BOTH antipodal sides active, T → 0, and
  a 4-side dual with multipliers summing to 1 — is the Stage-2 seed: it says
  the binding obstruction lives in the centered (T = 0) slice on a
  pentagonal sub-structure, which is where an exact Farkas/Positivstellensatz
  impossibility certificate should be sought.

## Verdict

**ACCEPTED as strong numerical evidence** (not proof) that no
(3,5)-zonoboxtope attains 44 vertices: over the exhaustively enumerated
sign-assignment space, the supremum of the feasibility margin is numerically
zero and is not attained — the maximizing sequences degenerate (chirotope
walls / weight floor / T → 0), and the boundary objects have far fewer than
44 vertices. Combined with the prior certified 42-instances and ~300
complete per-U searches, the working hypothesis is now **max f₀(3,5) = 42**,
with Conjecture 6.6.1's odd case (and Prop 6.5's tightness at n = 5) wrong —
pending Stage 2: an exact impossibility certificate, for which the 5-cycle
dual structure is the concrete starting point.

## Curation

Committed: all Stage-1 code (seeded, rerunnable), `RESULTS.md`,
`sigma_enum.json`, `obstruction_analysis.json`, `validation_report.json`,
`floor_sensitivity.json`, `margins_summary.json` (per-class best margins,
built by this review), and `margins.json.gz` (the full table, compressed).
Excluded as regenerable: NPZ checkpoints, stdout/stderr logs,
`fixed_screen.json`, `broad_screen.json`, and pre-broad campaign snapshots.
