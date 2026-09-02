# Factor-19069 factored-barrier constructor findings

## Endpoint

The constructor reaches the preregistered null endpoint
`HASH_PINNED_FACTORED_BARRIER_CRITICAL_COMPONENT_FRONTIER_WITH_FIRST_UNSAMPLED_COMPONENT`,
classified `EXACT_FAIL_CLOSED_FACTORED_BARRIER_COMPONENT_NULL`.  This is a
completed exact circuit/frontier artifact, not a component sample and not a
wall-coverage certificate.  Diagonal nine remains open and the theorem
ledger remains `2/9`.

## Exact factored source object

The pinned row-2599 sources reconstruct all seventy sign-normalized parent
polynomials `H_I`, with 209 sparse source terms and total product degree 90.
`FACTORED_BARRIER_FRONTIER.json` stores `B=product_I H_I` only as a product
circuit.  No expanded barrier polynomial or expanded barrier monomial count
is present.

For each of the nine affine coordinates, the artifact stores the exact
formula

```text
dB/dx_k = sum_I (dH_I/dx_k) product_(J != I) H_J.
```

Every coordinate record retains all seventy summands, including the exact
zero derivative of a factor when appropriate, for 630 provenance-preserving
summands.  Factor `19069` is independently reconstructed as a primitive
degree-six, multidegree `(2,2,2)`, 108-term sparse polynomial.  The artifact
then stores all 36 coefficients

```text
(dB/dx_i)(df/dx_j) - (dB/dx_j)(df/dx_i),  0 <= i < j < 9,
```

as circuit nodes.  The factor-circuit semantic SHA-256 is
`0e10d3d4692a53a6040ea8822be05376775e9c674c74d532f42236d3dfb1a7cf`.

## Exact fail-closed component frontier

The strict full-support system is exactly defined by `f_19069=0`, the 36
factored wedge equations, all seventy inequalities `H_I>0`, and a required
exact path selector to the pinned connected parent component.  Singular wall
pieces and possible component dimensions zero through eight are explicitly
retained.  Its semantic SHA-256 is
`103ac3707fc12deeb74141ee916f42667f2210ad7fcf718b119eeaa58b62a6a0`.

No exact connected-component decomposition, rational univariate/Thom sample,
or positive-dimensional component encoding was completed under the declared
ceiling.  Therefore the first unsampled frontier item is the entire exact
stratum `FB-C0-STRICT-INTERIOR-FULL-SUPPORT`, pending component decomposition.
Zero solver/component nodes were claimed.  This is the computational blocker;
it cannot be replaced by generic numerical roots or by declaring the raw
critical locus zero-dimensional.

## True boundary and connected-parent paths

The compactification accounting retains all 3,375 product-support strata.
The pinned Bernstein gate excludes 3,364 and leaves ten proper candidate
supports: eight on which factor 19069 vanishes identically and two with mixed
restriction.  Each candidate keeps its exact weak-sign witness and a separate
connected-parent closure-path field.

An exact linear path from the pinned parent sample is certified for support
`(15,7,15)`: all seventy signed parent factors are positive for `0<=t<1`.
This is new closure-residence evidence for that witness only; it neither
classifies a boundary wall germ nor attaches an interior wall component.
The same prescribed linear-path test is rejected exactly on the other nine
witnesses, and that rejection is not a proof that some different path is
absent.  The first unresolved boundary support remains `(1,1,1)`.  Its record
is pinned by SHA-256
`d32036b252e71f9b3d921c972a87811a02eb6a2000a1ef85324464946d58eb4a`;
the tested path first fails at signed parent factor `2578`.

True parent boundary remains explicitly distinct from solver, box, collar,
and skeleton-endpoint boundaries.

## Skeleton attachment accounting

All forty fixed edges replay all seventy exact parent path tags (2,800
checks).  Exact Sturm replay again finds one open factor-19069 root on edge
39 and none on the other 39 edges.  The edge-39 root is stored as a rational
univariate point with its primitive parameter polynomial, isolating interval,
and nine affine coordinate maps.  It is an exact attached wall anchor because
it lies on the skeleton; it is explicitly not asserted to be a barrier
critical sample and yields no global component count.

The constructor self-check rebuilds the manifest and frontier byte-for-byte
from pinned sources and rejects 19/19 hostile mutations covering source,
factor, circuit, derivative, positive-dimensional, singular, boundary, path,
skeleton, attachment, and ledger drift.  It is not the producer-independent
certificate required for cycle acceptance.
