# Diagonal three: relative-boundary collapse of the support ladder

## Result

The support-dimension ladder after the parent-face gate is not a necessary part of the diagonal-three **relative** pair certificate.

For the pinned compactification `(Delta^3)^3`, every proper product-simplex support zeros at least one homogeneous coordinate of a moving column. The compactification atlas identifies each of the twelve homogeneous coordinate divisors with a genuine row-2599 parent-bracket divisor. Therefore all `3,374` proper supports lie in the parent-boundary relative subspace `K_infinity`; only `(15,15,15)` can meet the nonrelative parent interior.

For a CW pair `(K,L)`, `C_n(K,L)=C_n(K)/C_n(L)`, so cells contained in `L` generate zero relative chains. Hence residual subdivisions wholly inside proper supports need not be materialized merely to compute the relative middle complex. Their required information is reduced to relative endpoint/frontier tags on closures of nonrelative cells.

Applied to the exact parent-face residue, `52,394` of `70,218` mixed restrictions occur on proper supports and are relative. Only the `17,824` full-support mixed restrictions can generate nonrelative cells.

Replay:

```bash
PYTHONDONTWRITEBYTECODE=1 python ai/omreal/verify_diag3_pair_relative_boundary_collapse.py
```

Semantic digest: `65b425e0a9507dd536b59e770f3c43f5eb025381b2ca2e75eb009e93d022b02a`.

## Boundary-divisor certificate

The twelve coordinate divisors are exactly

```text
column 6: [2346], [1346], [1246], [1236]
column 7: [2347], [1347], [1247], [1237]
column 8: [2348], [1348], [1248], [1238].
```

A proper four-bit support mask has a missing homogeneous coordinate, so any product support other than `(15,15,15)` lies on at least one of these parent walls. Exhausting all `15^3=3,375` support triples gives `3,374` relative proper supports and one possible nonrelative support.

Among the eleven parent-face survivors, ten are proper. Their mixed residual workloads sum to `52,394`; the full support contributes `17,824`, totaling the independently pinned `70,218` residue.

## Fail-fast audit of the former four-support target

Before using the collapse, the paired supports `(3,1,15)` and `(3,3,7)` were independently reconstructed. Both parent domains collapse to the same three-dimensional polytope

```text
P = {(a,g,h): 0 <= g <= a <= 1, 0 <= g <= h <= 1}.
```

Their `8,017` mixed restrictions reduce to `58` primitive irreducible zero-set atoms. Exact tetrahedral Bernstein coefficients classify `25` negative and `11` positive atoms; the remaining `22` have explicit rational interior witnesses of both signs. An independent exact real quantifier-elimination audit returns the identical `22/25/11` trichotomy and exactly the same 22 interior-zero atoms.

This boundary-only arrangement is already large. Exact rational witnesses certify at least `580` distinct interior 22-wall sign vectors. Separately, exact rational base points through denominator `120`, followed by exact univariate rational root isolation in the lift variable, certify `1,898` distinct vertical wall-root order regimes. These are fail-fast diagnostics only, not premises of the relative-boundary theorem.

Thus completing the former boundary CAD would build a substantial proof object that contributes no relative chain generators.

## Revised next target

Work directly in the strict row-2599 parent interior of full support `(15,15,15)`:

1. prune the `17,824` candidate residual factors by exact feasibility of an interior zero under all seventy strict parent signs;
2. subdivide only by residual walls that genuinely meet that nonrelative interior;
3. treat every parent-bracket zero or coordinate escape as a relative frontier tag, without recursively resolving the residual arrangement inside the parent boundary;
4. record exact nonrelative incidences, simultaneous residual intersections, and bad-signature labels;
5. assemble the relative middle matrices and prove the required rank/kernel identity.

The earlier support-face and low-dimensional calculations remain valid boundary diagnostics. Their status changes from prerequisites to optional refinements of the relative subcomplex.

## Honest accounting

This does not prove diagonal three. It removes an unnecessary boundary-subdivision obligation and changes the optimal construction route. The 9DVL ledger remains `2/9`.
