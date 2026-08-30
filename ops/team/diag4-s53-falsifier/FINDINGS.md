# D4-S53 falsifier: bounded row-2599 null

Date: 2026-08-30 UTC

Track: `diag4-s53-falsifier`

Frozen opening revision: `eb88516411d54403f7b274624bd2c44918678cab`

Canonical mathematical base: `aa784af939b55d3503e4782a9d65a9b06cf81ce0`

## Outcome

The result is **inconclusive**. There is no D4-S53 counterexample and no
claim-level signed reduction. The pinned row-2599 tuple is replayed exactly,
but neither a nonzero class on its whole four-parameter sign domain nor the
map into the entire closed circuit piece was obtained.

The finite-exact checkpoint is a bounded null certificate. It reconstructs
the complete attempted four-parameter semialgebraic domain, proves an exact
rational outer enclosure, and exactly excludes the largest symmetric cube of
the form `(-1/d,1/d)^4` for `2 <= d <= 84` as a local obstruction: the first
parent-safe member is `d=84`, and its `H_c^3` vanishes.

## Exact tuple and attempted domain

The accepted proper incomparable family uses parent row `2599`, signature
indices `0,4,5,6`, `rho=0`, and

```text
Q = 123/134/267/258/468.
```

At pattern zero, with variables ordered `(s,t,u,v)`, the motion is

```text
y5 += s*y2 + t*y8;  y1 += u*y3;  y7 += v*y2.
```

All five support normals are literally constant. The attempted domain is

`D = {(s,t,u,v) in R^4 : p_I(s,t,u,v)>0 for all 70 parent bases I}`,

where `CANDIDATE_DOMAIN.json` records every exact signed polynomial. There
are `48` nonconstant and `16` nonlinear inequalities. Every polynomial is
multi-affine, and the predecessor fingerprint is
`144b1c69ede7f4d7a78caae7f00bf66f162bd54d08f1cd17e44f1ba8c70b86cb`.

The independent replay also checks all sixteen selected good/bad patterns on
one parent chirotope. Thus this is actual realizable signed data, not an
abstract split--remerge model.

## Compactification gate reached

Eight affine bracket consequences give a bounded rational outer box. The
lower/upper witnesses are `3458/1358` for `s`, `1235/3456` for `t` (the upper
bound also uses the `s` upper bound), `1268/1278` for `u`, and `1367/3467`
for `v`. Exact endpoints are in the data artifact.

This reaches an exact bounded outer-enclosure gate: the closure of every
component of `D` lies in a compact rational box and its genuine boundary is
contained in the union of parent walls `p_I=0`. It is not a wall-adapted cell
decomposition of that closure.

## Exact local topology and separated replay

Because every `p_I` is multi-affine, positivity at all sixteen vertices of a
rational box proves positivity throughout the box by tensor multilinear
interpolation. Exhaustion of denominators `2,...,84` gives:

- `U=(-1/84,1/84)^4` is parent-safe;
- the minimum exact corner value is `878/21`, for bracket `5678` at corner
  `(1,-1,-1,1)/84`;
- the nearest larger reciprocal cube, with denominator `83`, fails at the
  same bracket and corner with value `-9050/83`.

The generator records this exact topology object. The independent verifier,
which does not import generator logic, reconstructs the polynomials and forms
the relative cubical CW pair
`([-1/84,1/84]^4, boundary)`. Modulo the boundary only its four-cell remains,
so the compact-support ranks in degrees `0,...,4` are `(0,0,0,0,1)`. Hence

`H_c^3(U;Q)=0`.

This excludes only the completely declared local signed subdomain `U`; it
does not exclude the pinned tuple or the whole `D`.

## Why the cubical route stops here

The vertex-positive inner-box method cannot meet the completeness gate by
adding finitely many more such boxes. The closure of every certified box lies
inside the open set `D`; therefore any finite union of them is compactly
contained in `D`. A nonempty open subset of `R^4` is not compact, and the
bounded sign domain has sequences approaching its parent-wall boundary.
Consequently no finite inner union can equal `D`. Completion requires a
wall-adapted exact stratification whose relative boundary is `p_I=0`, not an
open-ended inner-box sweep.

Even a nonzero class on an inner subdomain would not pass the transfer gate.
The hostile annulus-to-disk cellular canary has `H_1=Q` on the subset and
zero `H_1` after inclusion of the filling two-cell. This is the exact logical
failure mode for inferring full-piece cohomology from subset topology.

## Canaries

- `abstract_false_positive`: the trivial-holonomy split--remerge matrix has
  a one-dimensional kernel but no rank-four realization data.
- `actual_realizable_positive`: the row-2599 tuple, all sixteen family
  patterns, fixed support normals, and the parent-safe cube replay exactly.
- `inclusion_failure`: an annular one-cycle dies after inclusion into a disk.
- `sign_mutation`: flipping one attachment sign raises the abstract boundary
  rank from one to two.
- `boundary`: radius `1/84` passes all exact corners, while `1/83` crosses the
  named parent wall; the relative cube calculation treats its whole boundary
  as relative and does not confuse it with the genuine global parent wall.

## Surviving mechanisms and failed hypotheses

The sixteen nonlinear parent inequalities remain capable of producing
split--remerge topology in the rest of `D`. No whole-domain cellular
incidence, top-component differential, zero-weight face attachment, remaining
parent-direction attachment, or full-piece inclusion map was computed.

The failed routes are: abstract holonomy without realization data; local
pointwise admissibility as a cohomology witness; finite positive-box coverage
of the open sign chamber; and subset cohomology without the inclusion map.

The next discriminator, if this target were ever revisited after the required
cycle pivot, would be an exact wall-adapted semialgebraic decomposition of the
bounded component containing the origin, followed by an independently
constructed relative cochain complex and then explicit normal/attachment data
for its map into the whole closed `C_(rho,Q)`.

## Replay and nonconsequences

From the repository root:

```console
PYTHONDONTWRITEBYTECODE=1 python ops/team/diag4-s53-falsifier/generate_candidate_domain.py
PYTHONDONTWRITEBYTECODE=1 python ops/team/diag4-s53-falsifier/verify_candidate_domain.py
```

The first command is topology/domain generation; the second independently
reconstructs and verifies the exact data and cochains.

D4-S53 remains open, all `53` survivor orbits remain, D4-SP remains open,
diagonal four remains open, and the theorem ledger remains `2/9`. Under the
cycle's frozen closing rule, unchanged claim-level coverage requires `PIVOT`;
the falsifier recommends no ledger edit.
