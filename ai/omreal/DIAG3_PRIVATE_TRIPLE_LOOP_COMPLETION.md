# Diagonal three: sign-shattered private contraction and loop completion

## Outcome

There is a simple exact condition under which contraction by three private
extension columns is globally defined over their entire lifted fiber.

Let `sigma_1,sigma_2,sigma_3` be extension signatures, written on the `56`
parent triples.  If their coordinate traces meet all four antipodal classes
in `{+,-}^3`, then **every** three realizing private columns are linearly
independent.  This statement is uniform over the whole parent realization
space; it depends only on the three signature bitsets.

For such a triple, retaining every quotient loop face

\[
                          d_e=[p_1p_2p_3y_e]=0                  \tag{1}
\]

gives a contractible fiberwise triple-contraction completion.  At a uniform
rank-four/eight parent, the ambient rank-one loop complex has exactly `928`
nonzero covectors, with zero-set census

| loop labels | cells |
|---:|---:|
| `0` | `128` |
| `1` | `352` |
| `2` | `336` |
| `3` | `112` |

and no face with four loops.  The `352` one-loop faces connect the complete
`128`-tope adjacency graph.  Deleting those faces is therefore an artificial
disconnection; they are internal specialization cells, not parent infinity.

The pinned row-2599 signatures `0,3,6` satisfy the condition.  So do `52` of
the `56` triples in the stored eight-shatter family and `1,625,014` of the
`1,750,540` triples among the stored 220 signatures.

This is a materially positive contraction-domain theorem, but it does not
close diagonal three.  The private cones exist over the simultaneous **good**
locus `F_S`, while the invariant triple obstruction is
`H_c^0(B_1 intersect B_2 intersect B_3)`, where all three private cones are
empty.  Thus this completion cannot itself be a proper resolution of the
triple-bad locus.  A new dual construction over the three Gordan witness
blocks, or an exact Alexander/Leray bridge carrying the loop specializations
through empty private fibers, is still required.

The exact replay is
[`verify_diag3_private_triple_loop_completion.py`](verify_diag3_private_triple_loop_completion.py).

## 1. The four-trace independence theorem

For a parent realization `Y`, let `a_I(Y)` be the derived normal of parent
triple `I` and put

\[
 C_i(Y)=\{p\in\mathbb R^4:
       \sigma_{i,I}\,a_I(Y)\mathbin\cdot p>0
       \text{ for every }I\}.                                  \tag{2}
\]

These are the three open convex private-extension cones.  Identify a sign
triple with its antipode by normalizing its first coordinate to `+`.  The four
antipodal trace classes are

```text
(+++)
(++-)
(+-+)
(+--)
```

> **Sign-shattered private-triple theorem.**  Suppose that for every
> `epsilon in {+,-}^3` there is a parent triple `I` for which
>
> \[
>       (\sigma_{1,I},\sigma_{2,I},\sigma_{3,I})
>                         =\delta\epsilon
> \]
>
> with one common `delta in {+,-}`.  Then every choice
> `p_i in C_i(Y)` is linearly independent.

**Proof.**  If the private columns were dependent, write

\[
                         c_1p_1+c_2p_2+c_3p_3=0.                \tag{3}
\]

For every nonzero coefficient put `epsilon_i=sign(c_i)` and absorb
`|c_i|` into `p_i`; choose arbitrary signs at zero coefficients.  Select `I`
with trace `delta epsilon`.  After applying `delta a_I(Y)` to (3), every
nonzero term is strictly positive by (2), a contradiction.  QED.

This proof also excludes a dependence with one zero coefficient.  It uses no
genericity, sampling, choice of parent chart, or continuous witness.

For three bitsets `s_1,s_2,s_3`, put

\[
                  u=s_1\mathbin{\mathtt{xor}}s_2,
                  \qquad v=s_1\mathbin{\mathtt{xor}}s_3.
\]

The criterion is exactly that the four 56-bit masks

```text
~u & ~v,   ~u & v,   u & ~v,   u & v
```

are all nonzero.  This makes the theorem essentially free to screen at
catalog scale.

## 2. Contractible loop completion

Projectivize each nonempty cone `C_i(Y)` by positive scaling.  It becomes an
open convex three-cell `D_i(Y)`.  The lifted private fiber is

\[
                         D_1(Y)\times D_2(Y)\times D_3(Y),       \tag{4}
\]

and is contractible.  Under the theorem every point of (4) spans a projective
plane.  Orient its normal `w` by the ordered triple `(p_1,p_2,p_3)`.  Then

\[
                              d_e=w\mathbin\cdot y_e             \tag{5}
\]

up to one common positive factor.

For fixed oriented `w`, the fiber of the span map is

\[
 \mathbb P(C_1\cap w^\perp)\times
 \mathbb P(C_2\cap w^\perp)\times
 \mathbb P(C_3\cap w^\perp).                                  \tag{6}
\]

Every factor in (6) is convex or empty.  If all are nonempty, the sign-
shattered theorem says every colorful triple is a basis of `w^perp`, and its
orientation is constant on the connected product.  For rigor, fix in each
private cone a dual-interior linear functional and normalize it to one.  This
turns every projective factor in (6) into a bounded convex slice in a fixed
affine bundle.  Local sections, a partition of unity inside those varying
convex slices, and straight-line contraction give a homotopy equivalence from
(4) to its oriented normal image `U_S^+(Y)`.  Consequently

\[
                              U_S^+(Y)\simeq * .                 \tag{7}
\]

The loop walls (1) are just the intersections of this contractible image with
the parent hyperplanes `w dot y_e=0`.  They must be retained.  Uniformity of
the parent implies that no nonzero `w` annihilates four parent columns, so
only zero sets of size zero through three occur.

The complete ambient covector counts follow either from the exact replay or
from the general-position central-arrangement formula

\[
 f_z={8\choose z}\,2\sum_{j=0}^{3-z}{7-z\choose j},
                         \qquad0\leq z\leq3.                    \tag{8}
\]

They give `(128,352,336,112)`.  The actual image `U_S^+(Y)` may occupy only
part of this ambient complex and may require refinement by faces of the dual
extension cones.  Equation (7), not occupancy of all 928 cells, is the
coverage theorem.

## 3. Exact row-2599 instance

For the stored signatures `0,3,6`, colex rows

| antipodal trace | row | parent triple |
|---|---:|---|
| `+++` | `28` | `357` |
| `++-` | `25` | `347` |
| `+-+` | `0` | `123` |
| `+--` | `40` | `348` |

give the four witnesses.  Hence every point of their full convex product
(4) is triple-independent at every parent chart where the three signatures
are simultaneously feasible.  The one-loop path in
`DIAG3_TRIPLE_CONTRACTION_NO_GO.md` is therefore not an isolated lucky path:
rank loss is impossible throughout the whole fiber.  Its missing loop face
is repaired by the general completion above.

The larger exact censuses are

```text
stored eight signatures: 52 / 56 triples pass
stored 220 signatures:    1,625,014 / 1,750,540 triples pass
```

Failure of the four-trace test is inconclusive; it is a sufficient criterion,
not a necessary one.

## 4. Parent-infinity escape criterion

The loop theorem isolates the remaining global obligation cleanly.  Take a
proper finite semialgebraic compactification and regular subdivision `K` of
the relevant contracted incidence, refined by

1. all loop faces `d_e=0`;
2. all dual-extension-cone and support-specialization faces; and
3. all parent bracket and chart-infinity faces.

Let `K_infinity` contain **only** cells over the parent boundary.  Loop and
private-fiber faces are internal.  For any closed resolved locus whose map to
the parent is proper, compact-support degree zero has the exact graph test

\[
 H_c^0=0
 \quad\Longleftrightarrow\quad
 H_0(K,K_{\rm infinity})=0
 \quad\Longleftrightarrow\quad
 \text{every component of }K\text{ meets }K_{\rm infinity}.    \tag{9}
\]

Thus a finite escape certificate needs only:

- coverage of every top cell;
- all codimension-one loop and support adjacencies; and
- a path from each component to a genuine parent-infinity cell.

Higher loop coherence is automatic from convex carriers once these
codimension-one maps exist.  Equation (9) is the smallest exact
loop-specialization criterion for a triple `H_c^0` calculation.

## 5. Why it does not yet apply to the invariant triple obstruction

For diagonal three the required group is

\[
                  H_c^0(B_1\cap B_2\cap B_3;\mathbb Q).         \tag{10}
\]

At every point of (10), all three cones (2) are empty.  Therefore neither
(4) nor the normal image (7) has a fiber there.  The private loop completion
is a model over `F_1 intersect F_2 intersect F_3`, not a proper surjection
onto (10).  Treating its empty fiber as an escape would be exactly the
forbidden specialization shortcut.

The six hard factor canaries likewise specify residual factor triples, not
three simultaneously feasible private signatures, so the four-trace test is
not defined on them without an additional source/signature lift.

A scalable positive continuation must construct a dual version of (7) over
the three normalized Gordan polytopes.  It must remain nonempty when a private
cone disappears, include zero block masses and all loop analogues, and satisfy
the parent-infinity graph test (9).  Until that bridge exists, the theorem
above repairs private triple contraction but does not prove triple-bad
noncompactness or change the diagonal score.

## 6. Replay

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_private_triple_loop_completion.py
```

The replay uses integer and rational arithmetic only.  It pins the two input
signature digests, checks the four trace witnesses, performs both finite
censuses, reconstructs every restricted central-arrangement tope, and verifies
the complete loop-covector f-vector and one-loop adjacency graph.
