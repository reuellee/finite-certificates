# Review of Stage 2a (Gemini 3.1 Pro High via agy) — adversarial verification

Reviewer: Claude (this repo's session agent), 2026-07-30. Stage 2a was
executed by Gemini in three bounded calls (see `STAGE2A.md`); this review
independently verified every load-bearing claim, found one substantive
defect, repaired it, and closed the one caveat the executor itself flagged.

## Verdicts by sub-problem

### T0 (centered-slice certificate) — IDEA CORRECT, ARTIFACT DEFECTIVE, REPAIRED

Independently verified: the T=0 side-collapse derivation (re-derived: at
T=0 both sides of a class share the value W, so demands are class-level and
antipodal-symmetric — side orientations become irrelevant, which also
retro-resolves the executor's own orientation caveat); the count of valid
class assignments = **200** (my own enumeration, on two independently
labeled structures); the Farkas soundness argument for strict systems
(y ≥ 0, y ≠ 0, Aᵀy ≤ 0 kills {Av > 0, v > 0} — both halves needed and
present).

**Defect (P1): a labeling gap.** The 200 valid assignments were enumerated
against one randomly generated configuration's chamber incidence, while the
LP infeasibility was proven on a different configuration (`U_ints`). The
structures are isomorphic but not identically labeled. Consequences,
established by direct test: 15 of the 400 (assignment × split) systems are
in fact strictly FEASIBLE on `U_ints` (margins up to ~146 in unnormalized
units) — harmless in themselves (building the corresponding T=0 instance
gives only 16 hull vertices, and the assignment bicolors only 16/22 of
`U_ints`' own chambers, confirming the mislabeling rather than a 44-vertex
instance) — but they mean the shipped `farkas_t0.json` does not prove the
stated theorem. Additionally, 93 of its multiplier entries are the corrupt
string "F", and the remainder are decimal strings, not the claimed exact
integers.

**Repair (this review):** the chain was redone self-consistently on
`U_ints` — its OWN chamber incidence (again exactly 200 valid assignments),
then all **400 systems proven infeasible with exact rational Farkas
certificates**, extracted from primal-margin LP duals and repaired/verified
in pure Fraction arithmetic (zero failures). Authoritative artifact:
`farkas_t0_exact.json`; generator: `t0_exact_fixed.py`. The restored
theorem: **no valid class assignment of `U_ints`' own chamber structure is
realizable at T=0 with positive weights** — the centered slice of this
exact rational cell caps at 42.

### T-cancellation — ACCEPTED

The equal-multiplier antipodal cancellation is elementary and correct as
derived. The claim that Stage 1's best dual cancels T *geometrically*
(linear dependence of r₀₂, r₀₃, r₁₃, r₂₄ with the observed multipliers,
forced by LP duality with unconstrained T) is consistent and accepted. The
coverage condition for a T-independent certificate family (§4 of
STAGE2A.md) is well-posed and is the right formulation of what Stage 2b
must establish.

### Determinant identities — VERIFIED AND STRENGTHENED

The claimed identity c₂E₂₄ + c₄E₀₃ = c₁E₀₂ + c₃E₁₃ with
c₁ = D₀₁₃D₂₃₄, c₂ = D₀₁₃D₀₂₃, c₃ = D₀₂₄D₀₂₃, c₄ = D₀₂₄D₁₂₃ reduces
per-weight-coordinate to three-term Grassmann–Plücker relations and is
therefore **chirotope-conditional** (this review confirmed it fails on
`U_ints`, which lies in a different reorientation class — the executor's
"target chirotope" phrasing was correct but underspecified). The two links
the executor could not close were closed here by data, not convention:

1. **σ-link:** decoding Stage 1's best `class_bits` under Stage 1's own
   encoding gives exactly the four demands E₀₂ < 0, E₀₃ > 0, E₁₃ < 0,
   E₂₄ > 0 assumed by the contradiction (the Call-2/Call-3
   orientation-table discrepancy is immaterial: at T=0 the sign demands do
   not depend on side orientation).
2. **Chirotope-link:** on Stage 1's best-U chirotope (rationalized at
   denominator ≤ 10⁶), all five per-coordinate residuals of the identity
   are exactly 0 and all four coefficients are strictly positive.

Hence the executor's "Stage-1 Dual Impossibility" is upgraded from "proven
modulo an orientation audit" to **PROVEN for the Stage-1 chirotope cell**:
the binding obstruction of the σ-complete search is an exact
Grassmann–Plücker contradiction, valid for every configuration realizing
that chirotope — the first configuration-independent (within a cell)
algebraic piece of the max f₀(3,5) = 42 program.

## Adjusted ledger after review

- PROVEN: T=0 collapse; 200-count (structure-invariant); centered-slice
  cap-42 for the exact cell of `U_ints` (repaired artifact); robust
  antipodal T-cancellation; the 5-cycle GP contradiction for Stage 1's
  chirotope cell, with the σ-link established.
- CONJECTURED (unchanged in substance): extension to T ≠ 0 (the coverage
  condition names the missing piece); universality across cells (both the
  Farkas family and the GP contradictions are per-cell; the uniform-OM
  uniqueness suggests, but does not yet prove, transfer).
- DEFECTS FOUND: the labeling gap (repaired), the corrupt/inexact
  serialization of the original `farkas_t0.json` (superseded), and the
  underspecified chirotope scoping of Call 3 (pinned here).

## What Stage 2b needs

Combine the two proven mechanisms: (i) T-independent Farkas families via
antipodal-symmetric subsets (whose weight systems the T0 certificates
already refute), and (ii) per-cell GP contradictions for the assignments
that break antipodal symmetry. If every one of the 16,570 σ-classes is
killed by (i) or (ii) on every cell of the uniform OM's realization space,
max f₀(3,5) = 42 is a theorem.
