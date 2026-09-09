# An actual full-block transition at the row-2599 support event

**Finite exact local result, with a deductive local-germ consequence; no global
theorem credit.** The previously unresolved right-hand parent is strictly
feasible for the entire original block 0. Blocks 1 and 2 remain bad. This is
an actual transition between triple badness and the exclusive pair `E12`,
not just loss of a selected witness support.

Canonical base: `21a97db6aa66912fd37556d81711c0588c454a7d`. Opening revision:
`c27a36d6e3f47a2b4c7bb017774cbe5df30abdc2`. All inputs are pinned in
`SOURCE_MANIFEST.json`; no predecessor or ledger file was changed.

## Exact covered domain and certificate

Use chart 0 of the original `seeat_parent2599_upper178.npz`, with only
`Y[1][1]=54+t` moving, and the original block signatures
`14988895318912`, `3405195891438080`, `40418075143643136`. Normals are
`n_ijk(Y) p = det(y_i,y_j,y_k,p)`, signed by the corresponding signature.
Triple indices are zero-based repository colex order.

Put

```
t* = 37864449186859942661765893 / 7029591949415530407677535
epsilon = 1/1000000
I = [t* - epsilon, t* + epsilon].
```

The exact replay binds the parent literally to the original NPZ and verifies
all 70 original parent signs on all of `I`. It reconstructs all normals and
selected dual cofactors directly from that parent, without reading numerical
discovery or importing a predecessor verifier.

| Domain | Block 0 | Block 1 | Block 2 |
|---|---|---|---|
| `[t*-epsilon,t*]` | Bad | Bad | Bad |
| `(t*,t*+epsilon]` | Strictly feasible | Bad | Bad |

Let `D(t)` have the four signed block-0 rows with indices
`19,21,37,38`, respectively normal labels `456,137,238,148`. Define
`p(t)=adj(D(t)) (1,1,1,1)^T`, with no determinant division. Its explicit
integer affine coordinate polynomials are:

| Coordinate | Constant | Coefficient of t |
|---|---:|---:|
| 0 | 23760561537956239979898 | 27202897715989972358 |
| 1 | 338889459408519410771 | -31493053811631780705 |
| 2 | -16530736353859430653877 | -746826479287241607 |
| 3 | 607634970479574278739 | -10147372787555242677 |

The four corresponding primal margins all equal the actual event factor,
coefficientwise:

```
Delta(t) = det D(t)
         = -1590306865848117591794167506
           +295242861875452277122456470*t
         = 295242861875452277122456470*(t-t*).
```

Every one of the other **52** signed margins is strictly positive throughout
`I`. The replay verifies their exact degree-at-most-two polynomials by
strict positivity of every Bernstein coefficient on the closed interval.
Thus all 56 inequalities are strict for every `t>t*` in `I`, including the
requested right endpoint. No alternate nonnegative dual witness can exist
there: its pairing with this strict primal would be positive.

The original selected block-0 five-support is `[0,19,21,37,38]`.
Its first cofactor is `Delta`; its other four cofactors are strictly negative
on `I`. On the closed left half-interval the five cofactors are nonpositive
and not all zero; dividing by their negative sum gives a normalized
nonnegative Gordan witness. For blocks 1 and 2 all five original selected
cofactors stay strictly negative on `I`. The replay verifies all twelve
coefficientwise Gordan equalities and the relevant Bernstein signs.

At the event, `p(t*)` is nonzero, and exactly the four `D` margins vanish.
Any normalized nonnegative dual of the **full 56-row block 0** must therefore
be supported on those four rows. Their exact rank is 3, and their surviving
cofactors give a strictly positive kernel vector. Consequently the full
normalized block-0 witness fiber at the event is a **singleton**.

## Explicit original-parent local germ

The same determinant formulas apply to freely varying parent matrices `Y`
near `Y*`. Keep the original signatures, the three original ordered
five-supports, and define `D(Y)`, `Delta(Y)`, and `p(Y)=adj(D(Y))1` as above.
Let `c_j^b(Y)` be the signed five-support cofactors in the original order.
Define an open neighborhood `U` of `Y*` by these strict polynomial conditions:

* All 70 parent brackets have their original signs.
* `c_j^0<0` for `j=1,2,3,4`, and all five `c_j^b<0` for `b=1,2`.
* `a_i^0(Y) p(Y)>0` for every `i` outside `19,21,37,38`.
* The partial derivative of `Delta` with respect to `Y[1][1]` is positive.

The exact event certificate verifies each condition at `Y*`; the last
derivative equals the displayed positive coefficient. Therefore `U` is a
nonempty open semialgebraic neighborhood in the original parent-matrix
domain. No generic all-minor or saturation-exclusion hypothesis is assumed.

On `U`, the following are exact equalities of loci:

```
B0 = {Delta <= 0},       B1 = B2 = U,
E12 = (B1 intersect B2) minus B0 = {Delta > 0},
boundary(B0 in U) = {Delta = 0}.
```

For `Delta<=0`, all block-0 selected cofactors are nonpositive and their sum
is negative, proving badness. For `Delta>0`, the four active margins of `p`
equal `Delta` by the adjugate identity and the other 52 are positive by the
definition of `U`, proving strict feasibility. The same strictly negative
cofactors prove badness of blocks 1 and 2 throughout `U`.

The positive partial derivative makes `Delta=0` a smooth local hypersurface
by the implicit function theorem. After shrinking around the event, the
bad locus is a closed half-space in a smooth coordinate chart, and `E12` is
the opposite open half-space. Thus a local topological collar exists here
for the actual bad-locus transition. This is an original-space local germ;
it is not a globally attached frontier map.

On that boundary, the same positive nonactive margins force every dual onto
the four active rows. One of the strictly nonzero remaining five-support
cofactors contains three active rows, so their rank is at least 3;
`Delta=0` makes the rank exactly 3. The full normalized witness fiber is
therefore a singleton throughout `U intersect {Delta=0}` as well.

## Discovery, replay, and hostile checks

Initial test: twelve small numerical LP calls, primal and normalized dual at
each of the two adjacent parents for each of three full blocks. Discovery
took about 0.1 CPU second. At the right point the LP also accepted a false
dual within floating-point tolerance; `DISCOVERY.json` is explicitly
heuristic and is never an acceptance input. Its proposed strict primal
motivated the single exact follow-through using the four event rows.

Replay from repository root:

```
python -B ops/team/d3-explore-event/verify.py
```

The default replay is read-only and compares the frozen `CERTIFICATE.json`.
It needs only Python's standard library and takes under one CPU second.
The retained numerical discovery command is:

```
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -B ops/team/d3-explore-event/discover.py
```

Five hostile controls reject declaring the event strict-primal, declaring
the right selected support dual-feasible, negating the right primal,
shifting the event root, and dropping an active inequality from the 56-row
denominator. The certificate includes endpoint rational points and weights,
all 52 nonactive margin polynomials and their exact interval certificates.
Independent acceptance remains the referee's responsibility.

## Scope, decision, and nonconsequences

Classification: **finite-exact computation with a deductive local-germ
consequence**. Information success is established; theorem distance is
unchanged. Original pair target `NULL`; zero original obligations closed;
theorem ledger remains `2/9`. Pair coverage and exhaustive residual remain
`UNKNOWN`. The seven original open obligations remain open.

This refutes a harmless-*full-badness*-interpretation of this selected event:
the actual membership changes. It does not refute a regular collar; it
provides one locally. It computes no compactly supported cohomology class,
global signed frontier block, cancellation, detector trace, or true-infinity
attachment. It supplies no global compactification or exhaustive event
coverage. Properness, incomparability, and admissible-label facts remain
the pinned inherited results; this replay binds their exact original source
and preserves its parent chirotope rather than redoing that entire census.

Stop decision: the one initial test and one exact follow-through are complete.
No further family or parameter search is run. The next discriminating work,
if separately selected, is to transport this actual local `B012 / E12` collar
to an oriented frontier contribution and test its global attachment. That
is a new obligation, not a consequence claimed here.
