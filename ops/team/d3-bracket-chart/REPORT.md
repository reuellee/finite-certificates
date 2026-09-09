# Genus-one fibers obstruct the fixed-base rational escape route

**The requested 3/9 milestone was not achieved. The verified ledger remains
2/9.** This continuation from `68c3dba` identifies an exact geometric
obstruction to a specific rational-fiber strategy. It also proves
noncompactness for every component of one complete fiber over five fixed
base coordinates, in every uniform parent sign cell. That
slice result does not close a full source orbit.

Base commit: `68c3dbaf748416be099ad71af2b7426dbadf9272`; base tree:
`d9116a510b2b4c29116ad7c956996e0136264067`.
Branch: `research/d3-bracket-chart-20260905`.
This is coordinator research with separate arithmetic reconstruction, without
independent AI referee acceptance or a canonical-ledger update.

## 1. The geometric obstruction

Let `q1,q2,q3` be the pinned full-source equations for presentation
`(5563,16134,19284)`. The previous height-chart calculation solves

```text
d = (b(i-f)+fg)/i,
a = -B/A,
A = i(f-1)(h-1)(bf-ce).
```

Here `i*q2` after the d substitution is `A*a+B`. Write the corresponding
third equation as `i*q3=C*a+D`. Then the full source is exactly

```text
N = A*D-C*B = 0,
q3 after both substitutions = N/(i*A).
```

All denominators are genuine parent-bracket units. This is an equivalence
on the whole uniform parent domain, including rank-drop points. It is not
an equivalence on the discarded nonuniform parent boundary.

The new standard-library checker reconstructs `N` directly from the original
three equations. It has 389 terms and bidegree `(2,2)` in `(c,e)`. Over

```text
K = Q(b,f,g,h,i),
```

write `N=C2(c)e^2+C1(c)e+C0(c)` and set
`Delta(c)=C1(c)^2-4C2(c)C0(c)`. The generic discriminant has degree four in
`c` and 3,257 terms. The identity

```text
(2*C2*e+C1)^2-Delta = 4*C2*N
```

is replayed coefficient by coefficient. Thus the generic function field is
the quadratic extension `K(c)(sqrt(Delta))`.

The specialization below has a degree-four squarefree discriminant. Its
nonzero Sylvester determinant proves that the generic quartic resultant
with its derivative is not the zero polynomial. Consequently the generic
quartic is squarefree as well. Over an algebraic closure of `K`, the smooth
projective model is a double cover of the projective line with four simple
branch points and none at infinity.

The [Riemann--Hurwitz formula, Stacks Project 53.12](https://stacks.math.columbia.edu/tag/0C1B)
gives `2g-2=2*(-2)+4=0`. Its geometric genus is therefore **one**.
The same formula excludes a nonconstant map from the projective line to
this smooth projective curve in characteristic zero: it would give
`-2=0+degree(ramification)`. A rational parameterization, or even a
nonconstant rationally parameterized arc with those five base coordinates
fixed, is therefore impossible on the generic fiber. The displayed
specialized fiber has the same obstruction.

This excludes a rational ruling for this projection. It does not exclude
algebraic/semialgebraic arcs, paths that move the base coordinates, a rational
description using a different projection, or rationality of the total
six-dimensional source. The generic curve is called genus one; no rational
point over `K` is asserted, so it is not silently identified with an elliptic
curve over `K`.

## 2. An exact, parent-interior specialization

Fix

```text
(b,f,g,h,i) = (-23/7,-3,-1,2,4).
```

Then `d=-5` and

```text
a = (28c^2 e-28c^2+37ce-383c+69e-207)/(2(7ce-69)).
N = (64/49) F,
F = (539c^2-28c+1449)e^2
    +(1323c^2-8092c+8901)e
    -2156c^2-27076c+17388.
```

The discriminant of `F` as a quadratic in `e` is

```text
W(c) = 6398665c^4+36722952c^3+61007646c^2
       +14826168c-21553047.
disc_c(W) = 4649793772367457417206802405651256329633792 != 0.
```

All identities, including the seven-by-seven Sylvester determinant, are
verified using integers and `fractions.Fraction` only.

There are two exact source points at `c=-27/14`:

```text
p  = (-19/28,-23/7,-27/14,-5,-4,-3,-1,2,4),
p' = (90/91,-23/7,-27/14,-5,-6843/1559,-3,-1,2,4).
```

At both points all three original equations vanish and all 70 parent
brackets are nonzero. At `p`, `F_e=5463/4 != 0`. Together with the two
parent-unit graph pivots, this gives an implicit local source chart over
the five base parameters and `c`. Hence the genus-one calculation concerns
actual parent-interior source geometry, persisting over a nonempty open
set of base values, rather than a boundary-only algebraic fiber.

## 3. The real oval does not create a compact parent component

The leading coefficient `539c^2-28c+1449` is positive for every real `c`:
its discriminant is `-3123260` and its leading coefficient is positive.
The checker isolates all four real roots `r1<r2<r3<r4` of `W` by four
disjoint rational intervals with opposite endpoint signs. Degree four
exhausts the roots; the nonzero discriminant excludes multiplicities.

The complete affine real curve therefore consists of two noncompact
components above `(-infinity,r1]` and `[r4,infinity)`, and a compact oval
above `[r2,r3]`. Each is obtained by joining the two explicit quadratic
root graphs at their simple endpoints. Both `p` and `p'` are on that oval:
their common `c` lies strictly between `r2` and `r3`, and their distinct
`e` values are exactly the two roots.

The parent bracket `[1346]=a` has opposite signs at these two points.
If the graph denominator `7ce-69` vanishes anywhere on the oval, that
point is already excluded by the genuine parent unit `[1267]=bf-ce`.
If the denominator never vanishes on the oval, the graph is continuous
there and `[1346]` must vanish between `p` and `p'`. In either case the
complete oval cannot survive inside a single uniform parent sign cell.

The actual slice in any such cell is an open subset of these three smooth
real curve components, with the entire oval excluded as a possibility.
Every connected component is an open interval, hence noncompact. The graph
is a homeomorphism onto the actual source slice. Since the equations and
fixed base values define a closed subset of the parent cell, its escaping
ends leave that parent cell or tend to infinity; there is no artificial
box boundary in this argument.

**Scope:** this covers every component of this one fixed-base slice, in
every parent cell it meets. It does not cover the other values of the five
base parameters, their singular fibers, or all components of the full
source. The generic genus statement alone supplies none of that coverage.
No compact component of the full triple-bad locus has been found.

## 4. Bracket-coordinate test and stopping decision

The alternative coordinates `u=bf-ce`, `v=ah-bg` keep the same base and
are invertible whenever the parent units `c,h` are nonzero. The transformed
two equations have 63 and 32 terms and are bilinear in `u,v`. Eliminating
`v` gives a 431-term primitive quadratic in `u`. Its discriminant differs
from the previous 3,257-term quartic by a square factor in `c` (up to the
chosen normalization); it does not turn the genus-one fiber into a rational
curve. FLINT's discovery factorization finishes in under a second and
reproduces the input product. Its irreducibility output is not needed by
the independent proof above.

One initial SymPy discriminant call was interrupted during unnecessary
expression-domain simplification. Replacing it with the explicit
coefficient identity `B^2-4AC` completed the calculation. Serialization
errors involving symbolic integers were corrected; only completed outputs
are used. No larger Gröbner, resultant cascade, saturation, or orbit census
was launched. The exploratory 70-bracket slice resultants are retained for
reproducibility but are not needed for the oval argument or a global claim.

The structural midpoint rejected fixed-base rational ruling as an escape
mechanism. Exact replay and the oval audit then checked the result's scope.
The opening's minimum full-source noncompactness endpoint was not met.
The new knowledge is INFORMATIONAL; the theorem-convergence trajectory is
**STALLED**. The decision is **RETIRE this fixed-base rational ruling** and
**STOP this investigation**. No global successor is certified by these data.

Opening and closing proof-distance vectors remain
`(2/9,1,{triple Hc0,pair Hc1},7,UNKNOWN,UNKNOWN)`.
The full triple-source residual remains 1,162,302. All seven canonical
load-bearing obligations remain open; the pair map was not computed.
The automatic same-blocker rules preclude claiming same-route convergence.

## 5. Verification and recovery

Run:

```text
python -B ops/team/d3-bracket-chart/verify_genus_one_fiber.py
python -B ai/omreal/verify_canonical_research_state_v11.py
python -B ops/research-team/verify_cycle_protocol.py
```

The new checker rejects a corrupted fiber equation, a repeated-root
quartic, and a nonuniform source-point candidate. Canonical V11 and the
existing cycle protocol also pass. That protocol pass audits the 24
existing governed cycles; it is not independent acceptance of this
coordinator investigation. No repository-wide suite was run for this
isolated research addition.

`ARITHMETIC_REPLAY.json`, `VALIDATION.json`, and `CLOSING_MANIFEST.json`
record the completed checks and artifact hashes. `DISCOVERY_OUTPUTS.zip`
preserves the four completed discovery JSON files byte for byte. Extract
them into this directory before rerunning a downstream discovery script,
or regenerate them with the included producers; the standalone verifier
needs only the original pinned source and does not read the archive.
The local recovery bundle
and its manifest are placed in the workspace `outputs` directory after
the commit, outside the commit's self-reference boundary.
