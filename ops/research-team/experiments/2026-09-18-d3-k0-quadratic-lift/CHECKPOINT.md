# K=0 quadratic lift continuation

18 September 2026, America/Los_Angeles.

**Original 9DVL ledger: 2/9. Zero whole source orbits closed.**

Source: `(5563,4373,23221)`.
This checkpoint records the parameter-uniform K=0 quadratic-lift formulation developed after commit `bed3bb628fd32f0ef552691b69495fcd96fcc7a7`. It is a complete guarded reformulation of the remaining K=0 stationary problem, not an emptiness proof or diagonal-three promotion.

## Verified recovery

- Archive: `9DVL_K0_Quadratic_Lift_2026-09-18.zip`
- Bytes: `22174196`
- SHA-256: `2bb5f4c41082bd94ca8a80c4f87ad1c8d062ca7b2a6fac946bd3c051987c9949`
- Payload files: 26
- Payload SHA-256: PASS
- Fresh extraction: PASS

Drive backup:
- archive: https://drive.google.com/file/d/1VQhVIQEWkgvV9Fe_hUqr1AUFJb5I5Ox1/view
- proof: https://drive.google.com/file/d/1mcyqs6l2tAylCjovUTva7YNDExUvPDw3/view
- report: https://drive.google.com/file/d/10MV1FQ579vKYXW__sbdVg5uqEGcBPoAx/view
- recovery receipt: https://drive.google.com/file/d/1NcDh1bcArkWe_RQUP9PPf6MHDFQljWP3/view

Drive access follows the owner's existing permissions. No sharing settings were changed.

## Main result

The previous accepted exclusion was confined to `A=B=1,K=0`. This continuation keeps `A` and `B` variable and replaces the remaining K=0 stationary problem by an exact polynomial lift with:

- 8 equations in 7 variables;
- maximum total degree 9;
- 501 total monomial occurrences across the stationary equations.

The reduction retains the quadratic variable instead of expanding its discriminant and keeps the conic equation explicit instead of substituting a large rational parametrization.

This is an equivalent guarded stationary formulation. It retains:

- all 70 original parent conditions;
- all nonflat reconstruction pivots;
- the transverse derivative through `K=0`;
- the singular orientation equality `eta=0 / nu=0`;
- the full four-dimensional semidefinite curvature test;
- all 15 principal minors.

Two complete slope loci are excluded for arbitrary `A,B`:

`
beta = 0,
B*beta = 1.
`

A source-specific conic identity also proves `E_x != 0` on the genuine domain and gives the strict real sign filter

`
A(A+1)(B beta)(B beta-1) > 0.
`

These are domain exclusions and a justified derivative pivot, not a whole-locus exclusion.

## Relation to the published K=0 rational normal form

The branch already contained commit `bed3bb628fd32f0ef552691b69495fcd96fcc7a7`, which provides a separate complete rational K=0 normal form. The two formulations were reconciled exactly:

- all three coefficients of the remaining quadratic wall match under rational coordinate change;
- all three transverse-numerator coefficients match;
- the conic equation becomes identically zero on the published rational chart.

Therefore they represent the same guarded stationary target, not two independent exclusions.

For input-size comparison only:

- older exceptional form: 6,428-term degree-30 `F`, 10,187-term degree-35 normal equation;
- published `bed3bb6` form: 1,550-term degree-20 `F`, 1,999-term degree-21 normal equation;
- this lift: 7 variables, 8 equations, degree at most 9, 501 stationary monomial occurrences.

These counts do not prove a solver speedup, zero-dimensionality, or lower quantifier-elimination complexity.

## Verification

The primary verifier passed 113 exact checks and rejected four altered equations.

A separate standard-library implementation:

- passed 130 checks;
- reconstructed all 73 determinant polynomials independently;
- rejected five corruptions;
- used neither SymPy nor producer code.

The reconciliation checker passed ten exact bridge checks against `bed3bb6`.

The curvature-circuit evaluator passed twelve exact rational pivot/congruence checks, retained a singular PSD example, and rejected a matrix that would pass a leading-principal-minors-only test.

The retained exact partial-curvature counterexample was replayed. In the new system its transverse residual `chi` is strictly nonzero near `-1.52839699018`, recovering the earlier omitted r-stationarity residual near `+60.76797333`. Thus the lift does not accidentally admit that partial point as fully stationary.

These are arithmetic checks and written deductions, not independent mathematical peer review or proof-assistant certification.

## Replay

From the archive root:

```
python verify_payload.py
python verify_lift.py
python verify_independent.py
python curvature_circuit.py
python verify_reconciliation.py
python verify_counterexample_bridge.py
```

## Remaining decisive target

Resolve the guarded real system exported in `LIFTED_SYSTEM.json`, including the complete orientation inequality, every original parent sign, and the full four-dimensional PSD condition, or provide a complete source escape.

`K=0` and `K!=0` both remain open. The whole source, universal triple-wall statement, original triple-bad `H_c^0`, pair-injectivity endpoint, and diagonal three remain unproved. The conservative inherited remainder remains 1,162,302 source records, not components.
