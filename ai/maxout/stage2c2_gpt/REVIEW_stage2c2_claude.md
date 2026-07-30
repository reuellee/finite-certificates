# Review of Stage 2c-2 (GPT-5.6 xhigh via codex) — adversarial verification

Reviewer: Claude (this repo's session agent), 2026-07-31. The executor's
process was killed externally after the computational phases (the attempted
full-complement sweep died with it — correctly disclaimed in `STAGE2C2.md`);
the session was resumed to write the ledger from the completed artifacts.

## Independently verified

1. **The checker** (`check_stage2c2.py`) was re-run by the reviewer:
   `PASS ... 132.8s`, with per-degree outcome counts matching the ledger
   exactly (120 degree-0 no-gos, 64 + 56 at degree 1, 120 certificates at
   degrees 2 and 3). The checker re-derives structures, lifts every covered
   equal-pair certificate to the full 25-row labeled matrix, checks every
   hard strict witness in `Fraction`, and re-verifies every quotient-ring
   certificate both modulo the GP ideal and by specialization.
2. **The representative hard-region certificate** ((σ = 10070, k = 1) — a
   system *provably* without equal-pair certificates) was verified with the
   reviewer's own independent row builder (the one used to audit Stage 2b):
   all eight columns of Bᵀy vanish exactly at `U_ints`. Stronger, the
   reviewer checked the T-cancellation **symbolically over fully generic
   vectors** (sympy, raw u-symbols): all five residuals vanish identically —
   for this certificate the T-part is universal, beyond the cell-wide claim.
3. **Partition arithmetic and nesting**: 28,106 + 5,034 = 23,324 + 9,816 =
   33,140 per split; 51,430 + 14,850 = 66,280; the 33,437 single-class
   family sits inside the 51,430 equal-pair-covered set; the boundary
   complement 32,843 = 66,280 − 33,437. All consistent with the reviewer's
   prior independent counts (33,140 valid labeled sigmas, 33,437 family
   kills).
4. **Canary integrity**: the design places provably-HARD systems first in
   the equal-pair sweep (they stayed HARD, with exact strict margins) and a
   provably-uncertifiable non-coloring plus a known positive control in the
   GP hunt (rejected/accepted at every degree respectively). This is the
   practice instituted after Stage 2c-1's sign-bug incident, and it is used
   correctly here.

## Assessment of the three results

- **Objective 1 (labeled coverage ground truth)** — ACCEPTED. This
  replaces Stage 2b-1's per-representative accounting as the program's
  coverage base, with per-system exact certificates or no-go witnesses.
- **Objective 2 (boundary theorem)** — ACCEPTED, and it is a genuine
  theorem: the formal-D strict-witness argument for necessity is
  degree-independent and correctly scoped (the witness points need not lie
  on the Plücker variety precisely because the mechanism's identities are
  required to hold without GP reduction). Stage 2c-1's single-class family
  is thus THE complete ordinary coefficientwise-positive mechanism —
  33,437 systems, no multi-class extension at any degree.
- **Objective 3 (the GP hunt)** — ACCEPTED, and it is the breakthrough:
  every one of the 120 prioritized targets (all 20 canonical HARD
  representatives and the entire historical failed-100) carries an exact
  cell-wide certificate at side-degree ≤ 2 / weight-degree ≤ 3, with 109
  genuinely T-carrying. The key methodological enlargement — treating the
  weight-row multipliers as independent unknowns modulo the GP ideal —
  is what the Stage 2c-1 search lacked, and the small support sizes
  (mostly 4 nonzero coefficients) suggest a structured family behind them.

## Scope and the named next step

Nothing here proves global max f₀(3,5) = 42; the ledger says so plainly.
The 120/120-at-degree-2 result upgrades the frontier from "does any
mechanism reach the hard region?" (now yes, broadly) to a mechanical
question: run the degree-(2,3) quotient-ring machinery over the full
14,850-system HARD set (and the rest of the 32,843 complement of the
single-class family, where equal-pair numeric certificates exist but
cell-wide symbolic ones are still wanted). That sweep was started and
externally killed; its restartable script exists. If it completes with
certificates for every system, the cell-wide theorem follows for the
single reorientation class — which, by the computed uniqueness of the
uniform OM(3,5) class (`check_om35_uniqueness.py`), is the whole generic
story; adding the parity/perturbation step then closes
max f₀(3,5) = 42 globally for generic configurations.

## Verdict

ACCEPTED as-is; no defects found. The canary discipline, exact-before-
serialize rule, and self-consistent labeling — all instituted after
earlier stages' caught defects — held throughout, and the one external
interruption is correctly firewalled from every claim.
