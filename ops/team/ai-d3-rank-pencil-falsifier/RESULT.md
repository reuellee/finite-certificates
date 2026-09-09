# Complete fixed-support-plane criterion: exact negative certificate

**Decision: RETIRE the universal fixed-support-plane one-column escape
criterion.** At parent 2599, upper178 chart zero, every incident support union
of normal rank at most two is excluded for the registered flow triple. This
is a route countercertificate, not a counterexample to D3. The pair invariant,
triple compact-support degree-zero vanishing, and more general escape routes
remain open. Independent referee acceptance is pending.

The only new predicate point is `chart_matrix[0]` in the frozen
`ai/omreal/data/seeat_parent2599_upper178.npz`. Its signatures are
`14988895318912`, `3405195891438080`, and `40418075143643136`, in that order.
The source file and all supporting inputs are SHA-256 pinned in
`SOURCE_PINS.json` against base revision
`390d447eb1dceb3cf78b294a043e303a6430c267`.

## Exact endpoint and geometry

For each label `e`, the star contains 21 triples and the nonstar contains 35.
For each of the 210 unordered pairs `T` in that star, we retained all 35
nonstar rows together with the entire exact closure

`Cl_e(T) = {I containing e : a_I belongs to span(a_T)}`.

For every resulting row set, `certificate.json` supplies a pool index for an
integer vector `x` and one signature `sigma` with

`sigma_I * (a_I dot x) > 0`

on **every** retained row. Therefore that signed system has no nonzero
nonnegative kernel vector. Consequently no indexed closure permits three
simultaneous Gordan witnesses.

| Quantity | Exact value |
| --- | ---: |
| Labels and indexed pairs | 8 and 1,680 |
| Pairs whose closure has six rows | 840 |
| Pairs whose closure has two rows | 840 |
| Distinct closures with the moving label recorded | 896 |
| Distinct labelled six-row closures | 56 |
| Distinct labelled two-row closures | 840 |
| Strict integer inequalities checked | 65,520 |
| Existing separator vectors reused | 23 |
| Minimum checked integer margin | 162,514,748,513,691 |
| Pair choices excluded by signatures 0, 1, 2 | 1,202; 477; 1 |
| Exact rank-two pair checks | 1,680 |
| Outside-star-row rank-three checks | 28,560 |
| Additional enumerations or additional predicate points | 0 |

The geometry is explicit. A pair of triples that shares two labels `e,f`
has closure equal to all six triples `{e,f,k}`. These normals lie in the
two-dimensional annihilator of `span(y_e,y_f)`; a normal from a triple not
containing `f` cannot also annihilate `y_f`, by uniformity. Each moving label
has seven such closures and each contains 15 indexed pairs. If the two
triples share only `e`, the exact computation finds closure equal to that
pair. There are 105 pairs of each kind per moving label. The result checks
the six-row closures, which the retired two-triple test did not retain.

The certificate includes all 56 primitive normals, all 1,680 pair closures,
all assigned strict separators, their exact minimum margins, and the three
full-system positive dual witnesses. The checker reconstructs all normals
from the frozen matrix and verifies all closure memberships independently.

## Why these pairs exhaust the complete fixed-plane condition

Let `S` be the union of the incident supports of three nonzero nonnegative
Gordan witnesses for a common moving label `e`. Nonnegative weights may be
zero; only positive weights belong to the support. Fixing every selected
supporting plane requires the moving vector to remain in

`L = intersection_{I in S} ker(a_I)`.

All these planes contain `y_e`, and `dim L = 4 - rank{a_I : I in S}`. There
is a nonconstant local motion of its projective ray preserving all selected
planes if and only if that normal rank is at most two. Rank three leaves
only the original ray; this is precisely why rank, rather than the number
of selected triples, is the relevant criterion.

Distinct star normals are nonproportional: otherwise two distinct triples
would span the same three-dimensional plane, putting at least four parent
columns in it and violating uniformity. Thus every star pair has rank two.
If `S` has rank two, a basis pair from `S` spans it. If `S` has rank one or
zero, pad its one row or empty set with arbitrary other star rows to obtain
a pair. In every case there is an indexed pair `T` with `S` contained in
`Cl_e(T)`. The three witnesses are supported on the retained nonstar and
closure rows. Conversely, any three nonnegative witnesses on such a retained
set have their incident normal union inside the same two-dimensional span.
This proves the equivalence, including empty and one-row incident supports.

The 1,680 strict separators therefore exclude the complete fixed-support-
plane one-column criterion at this point, including witnesses with three
or more incident triples. They do not exclude a one-column motion whose
supporting planes change, changes of witness support during a motion,
motions of several columns, or escape after first moving to another point.

## Conditional proper-escape proof for a successful closure

The conditional proof in the frozen constructor's `FINDINGS.md`, section 2,
extends unchanged from two retained triples to their rank closure. For
completeness, its relevant dimension and boundedness argument follows.

Suppose some closure carries all three witnesses. Let `L` be the intersection
of the two basis planes. Its vector dimension is two, and every plane in
the closure contains `L`. Fix five of the seven nonmoving labels as a
projective frame, ordering its first four columns with positive determinant.
An orientation-preserving coordinate change and positive column scalings
fix this frame. Since it stays fixed, changing the moving ray changes the
actual projective parent rather than a gauge representative.

In these coordinates each coordinate of the moving column is nonzero by
uniformity. Let its signs be `tau_1,...,tau_4`. Positively normalize its ray
by `ell(x) = sum tau_r x_r = 1`. Its fixed orthant lies in the interior of
the bounded signed simplex `tau_r x_r >= 0, ell(x)=1`. The intersection
`L intersect {ell=1}` is an affine line through the starting point. The
requirements that all parent brackets retain their initial strict signs
are affine linear inequalities on that line. Together with the fixed
orthant, they define a nonempty bounded open interval containing the
starting point. Its endpoint has a zero parent bracket. A zero coordinate
is itself a zero bracket with three frame columns. The fixed nonmoving
frame ensures this is a genuine nonuniform degeneration in the parent
quotient.

Throughout the interval, each retained incident triple remains independent
and spans its original supporting plane. Its normal is a positive scalar
multiple `a_I(t)=c_I(t)a_I(0)`, with `c_I(t)>0`; continuity and nonvanishing
prevent a change of sign. Nonincident normals are constant. For each of the
three witnesses separately, transport and normalize its weights by

`w_I(t) = [w_I(0)/c_I(t)] / sum_K [w_K(0)/c_K(t)]`,

where `c_I=1` for nonincident rows. This preserves nonnegativity, nonzero
total weight, and every signed kernel equation, including initially zero
weights and any redundant supporting planes. Approaching the endpoint
over time `[0,infinity)` gives a proper path inside the triple-bad locus.
Only linear dimension, parent sign continuity, and the bounded signed
simplex are used. No generic circuit rank is assumed for this conditional
construction.

If this criterion held at every triple-bad point, each point would have a
connected proper path, which rules out a nonzero compactly supported locally
constant function and hence implies triple `H_c^0=0`. It supplies no pair
`H_c^1` argument. The negative certificate blocks the universal hypothesis;
the conditional construction remains valid.

## Verified open-neighborhood corollary

The checker separately verifies all 70 parent brackets are nonzero, with
minimum absolute value 15,324,526. For each indexed pair it checks a nonzero
two-by-two minor. For each of the 28,560 star rows outside its closure it
checks a nonzero three-by-three minor. These finitely many nonzero minors
remain nonzero on a sufficiently small neighborhood, so each closure can
only shrink there. No assumption that a rank-two equality persists is used.

Use the raw cofactor normals divided by their **fixed positive row gcds at
the initial point** as continuous local normals. Recomputing integer gcds
nearby is unnecessary. All 65,520 strict separator inequalities persist
on a sufficiently small neighborhood. Since the nearby closures are subsets
of the original closures, the same selected separator for each indexed
pair still excludes that expanded system nearby.

Finally, each full-system dual has five strictly positive integer weights
and rank four. All five signed deletion cofactors are nonzero and have the
same sign; their exact values are printed in `VERIFICATION.json`. Hence
the cofactor kernel vectors stay strictly positive nearby. Intersecting
these finitely many neighborhoods gives a relative open neighborhood in
the uniform parent realization space where all three full systems remain
bad and the complete rank-two incident-support criterion still fails.
No numerical neighborhood radius is claimed or needed for this existence
corollary. It is still not a compact bad component or a D3 counterexample.

## Source binding, checks, and scope

`verify_rank_closures.py` imports neither the discovery script nor any old
acceptance logic. Its determinant implementation uses signed permutations;
its closure check uses all four three-by-three minors. Discovery instead
uses two-coordinate exact span interpolation. NumPy only decodes the NPZ;
all proof decisions use arbitrary-precision Python integers.

The checker rebinds the three frozen full badness witnesses and the already
certified same-parent anchors at upper178 charts 3, 14, and 2, with stored
point indices 24588, 14261, and 2534. Each anchor realizes one signature
strictly and has exact positive duals for the other two. This verifies
nonempty proper pairwise incomparable feasible regions and all six ordered
incomparability directions. No new rank predicate is run at an anchor.
The checker also verifies all 1,260 Grassmann-Pluecker relations per target
signature. All source hashes are checked before these proof checks.

Reproduce with the bundled Python:

```powershell
& 'C:\Users\reuel\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe' -B 'ops/team/ai-d3-rank-pencil-falsifier/verify_rank_closures.py'
```

The owned directory contains the certificate, independent checker, frozen
source hashes, discovery reproduction script, rejection controls, and JSON
verification/resource records. Discovery stopped at its first complete
negative certificate at `2026-09-05T15:06:49.057477Z`; the pool probe took
0.127 seconds. The role began at 15:04Z with a 30-minute wall ceiling,
16 GiB memory ceiling, and 50 MiB new-artifact ceiling. Exact measured
completion resources are recorded in `RESULT.json`.

Only `ops/team/ai-d3-rank-pencil-falsifier` is modified. The prior lanes,
coordinator's new lane, ledger, and canonical artifacts are untouched.
There was no human contact, paid or external compute, broad CAD, new cohort,
push, or merge. No successor weakening or additional search is opened.
