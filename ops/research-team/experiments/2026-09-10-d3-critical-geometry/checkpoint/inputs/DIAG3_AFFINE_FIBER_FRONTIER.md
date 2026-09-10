# Third diagonal: affine-fiber compression and an internal discriminant wall

## Outcome

The relative-label pair endpoint has a new uniform presentation: every one of
the `9,476` unordered primitive factor-pair orbits is sequentially affine.
After graphing either factor with a parent-bracket-unit slope, the other
factor is affine in at least one of the eight graph coordinates.  This gives
a shorter independent proof that every factor-pair zero-set component is
noncompact.

The analogous triple strategy is false.  Four exact relative-label triples
admit no presentation in which, after a unit graph anchor, the two remaining
equations are jointly affine in two graph coordinates.  Three of them admit
no common three-dimensional affine direction even after an arbitrary linear
change of the original nine coordinates, and their three displayed
generators have no nonzero affine-linear infinitesimal symmetry preserving
their constant linear span.

For the first hard triple there is a stronger exact obstruction.  After two
valid graph eliminations the last equation is quadratic, and its
discriminant crosses zero at an exact uniform real point in the interior of
one parent chirotope cell.  Thus the triple stratum is genuinely branched;
it is not a union of two global graphs and its discriminant is not
cellwise sign-definite.

These results do **not** prove a compact component, disprove 9DVL, or prove
the third diagonal.  They identify the next honest triple-factor object: a
projection arrangement enlarged by discriminants and resultants.  The
separate pairwise `H_c^1` carrier column also remains open.

## 1. Square affine-system lemma

Let `Omega` be an open subset of `R^n`, with `n>=1`, let

\[
                       D\subset \Omega\times\mathbb R^k
\]

be open, and suppose

\[
                  f(w,z)=A(w)z+b(w),\qquad z\in\mathbb R^k,     \tag{1}
\]

is continuous and semialgebraic.  Then every connected component of

\[
                         Z=D\cap f^{-1}(0)                       \tag{2}
\]

is noncompact.

Suppose a component `C` were compact.  If `C` meets a point over `w` where
`A(w)` is singular, the consistent solution set

\[
                         L_w=\{z:A(w)z=-b(w)\}
\]

has positive dimension.  The component through the point of the open set
`D_w intersection L_w` is noncompact.  It is closed in the fixed fiber of
`Z`, and that fixed fiber is closed in `Z`; hence it is a closed noncompact
subset of `C`, a contradiction.

Therefore `A` is nonsingular throughout `C`.  On the nonsingular locus,
projection identifies (2) with the graph

\[
                         z=-A(w)^{-1}b(w)                         \tag{3}
\]

over an open subset of `R^n`.  A component of that graph maps to a nonempty
open Euclidean set, which cannot be compact.  This is again a contradiction.

The determinant need not be a unit and may vanish on other components.  The
essential hypotheses are joint affinity, an open graph domain, and a
positive-dimensional open base.  When the lemma is applied after graphing a
first residual factor, that first graph slope must be nowhere zero on the
whole parent cell; otherwise a missed zero-slope branch can be compact.

## 2. Corrected graph normalization

If

\[
                             q=A x+B,                              \tag{4}
\]

then graph substitution must preserve the common normalization of `A` and
`B`.  Primitive-normalizing them independently is invalid: in the canonical
types `36`, `38`, and `51`, it flips the sign of `B` but not `A`, replacing
`A x+B=0` by the wrong graph `A x-B=0`.

The shared helper now returns the raw slope and constant from the same
polynomial.  The complete previously committed 122-orbit affine-fiber
closure still passes after this repair, with corrected semantic digest

```text
af0fa699771292f5cca65510f32cf5c007034f4c9fdac5c3c3a49f0dfcd65846
```

and unchanged counts, anchors, and unique reversal.  Thus the existing
`9,476/9,476` factor-pair theorem survives the audit.  The digest changed
because the 28 type-51-anchor substitutions now represent the actual wall.

## 3. Uniform compression of all factor pairs

The earlier proof uses fixed Jacobian minors, reframed minors, translations,
weighted tori, and affine graphs.  A single presentation now covers all pair
orbits.

Use the canonical graph pivots

| factor orbit | pivot | slope up to sign |
|---:|:---:|---|
| 36 | `a` | `[1237]` |
| 38 | `a` | `[1278]` |
| 48 | `a` | `1` |
| 49 | `d` | `1` |
| 50 | `d` | `[1238]` |
| 51 | `f` | `[1456][2468]` |

and exhaust the stabilizer of the anchor.  If the stored first factor does
not work, reverse the pair and reframe the second.  Exactly three pair
orbits require reversal:

```text
(38,6386)  -> (48,14554)
(38,6510)  -> (48,3552)
(50,20046) -> (51,5956)
```

The selected graph anchors are distributed as

| anchor | pair orbits |
|---:|---:|
| 36 | 647 |
| 38 | 236 |
| 48 | 328 |
| 49 | 5,203 |
| 50 | 2,682 |
| 51 | 380 |

and the number of affine graph coordinates is

| affine coordinates | pair orbits |
|---:|---:|
| 1 | 11 |
| 2 | 69 |
| 3 | 209 |
| 4 | 607 |
| 5 | 1,179 |
| 6 | 1,894 |
| 7 | 2,307 |
| 8 | 3,200 |

The square affine-system lemma with `k=1` proves component
noncompactness.  The complete selected-polynomial digest is

```text
a28270e870ff2cb2a81a25a395f573fa95de63dc46b52a212a22779e92445847
```

This does not make a third equation harmless: an affine pair graph can be
cut by a nonlinear third equation to a compact set.

## 4. Exact failure of joint affine fibers

After choosing every factor as anchor, exhausting the anchor stabilizer, and
testing every pair among the eight graph coordinates, the following triples
have no jointly affine presentation for the two remaining equations.

| factor triple | graph presentations | coordinate pairs | successes |
|---|---:|---:|---:|
| `(12985,16183,7196)` | 16 | 448 | 0 |
| `(20355,5442,5949)` | 12 | 336 | 0 |
| `(9667,16486,26315)` | 12 | 336 | 0 |
| `(9758,24338,15810)` | 112 | 3,136 | 0 |

Thus Section 1 with `k=2` closes none of these exact cases.

For the first three triples, expand

\[
                  \operatorname{Hess}(q)=\sum_\alpha x^\alpha H_\alpha.
\]

If all three polynomials were affine on every coset of a three-plane `V`,
then the six-dimensional space `Sym^2(V)` would lie in the annihilator of
all coefficient forms `H_alpha`.  Exact rational row reduction gives:

| triple | coefficient-form rank | annihilator dimension | maximum `dim V` |
|---|---:|---:|---:|
| `(12985,16183,7196)` | 35 | 10 | 2 |
| `(20355,5442,5949)` | 40 | 5 | 2 |
| `(9667,16486,26315)` | 41 | 4 | 2 |

In the first row the ten-dimensional annihilator is the coordinate span

```text
aa ac ad bb cc dd ee gg hh ii
```

whose largest compatible symmetric square comes from only a two-plane.  In
the other two rows the annihilator already has dimension below six.  This
rules out rational and real three-dimensional affine directions, not merely
coordinate blocks.

For completeness, the coordinate-clique bound applies to arbitrary real
planes.  Restrict the ambient coordinates to linear forms `l_i` on `V`.
A forbidden diagonal tensor forces `l_i^2=0`, hence `l_i=0`; a forbidden
off-diagonal tensor forces `l_i*l_j=0` in the integral domain `Sym(V*)`,
hence one of the two forms is zero.  The active coordinate indices therefore
form an allowed clique, and their restrictions still embed `V`, so
`dim(V)` is at most the maximum clique size two.

There is also no affine-linear constant-span flow.  For `V(x)=Ax+b`, solve

\[
                 V(q_i)=\sum_{j=1}^3 M_{ij}q_j.                  \tag{5}
\]

The three coefficient systems have sizes `663 by 99`, `1055 by 99`, and
`1354 by 99`; each has exact rank 99 and nullity zero.  Hence no nonzero
affine-linear vector field preserves the constant `Q`-linear span of these
three generators.  This does **not** rule out preservation of their
polynomial ideal: that stronger equation permits polynomial multipliers
`M_ij(x)` and has not been computed here.

## 5. An exact discriminant wall inside one parent cell

The first hard triple reframes as

```text
(12985,16183,7196) -> (5563,19284,16134).
```

Graph factor `5563` in `d`, then factor `16134` in `a`.  Both slopes preserve
the raw equation and are nonzero parent units.  The remaining factor `19284`
is quadratic in `c`.  Set

```text
e=-2, f=-4, g=5, h=-5, i=6, b=t.
```

After removing the positive integer content 576, its discriminant is

\[
\begin{aligned}
m(t)={}&1890625t^6+15661250t^5+13768025t^4\\
      &+63398360t^3+108736016t^2-51063040t+172134400.
\end{aligned}                                                   \tag{6}
\]

Rabin's criterion proves that (6) is irreducible modulo 7 and hence over
`Q`.  Exact Sturm arithmetic gives one sign-changing real root

\[
                    \alpha\in(-7769/1000,-7768/1000).            \tag{7}
\]

In the number field `Q(alpha)`, take the double `c` root, solve the valid
`a` graph, and then the valid `d` graph.  Direct reduction modulo (6) proves

* all three factor polynomials vanish;
* the first `c` derivative vanishes and the second does not; and
* all 62 nonconstant parent brackets are nonzero.

Therefore the point is exactly uniform and lies in the interior of one
parent cell.  Since (7) is a simple sign-changing root, both discriminant
signs occur arbitrarily near it without changing the parent chirotope.

This is the decisive boundary for the quadratic shortcut.  The branch wall
is a new irreducible projection factor; it is neither a parent wall nor
removed by choosing another parent cell.

## 6. Remaining proof obligation

The triple-factor support-drop theorem still asks for noncompactness of every
component of every three-factor zero set.  The exact endpoint remains
`79,102,449` unordered `S_8` orbits.  A viable compressed proof must now
control how graph sheets attach across internal discriminant and resultant
walls and how those attachments reach the parent boundary.  Parent brackets
and primitive residual factors alone do not form a projection-complete
arrangement.

Even a complete solution of that endpoint would kill only the
`E_1^(2,0)` triple column.  The `E_1^(1,1)` pairwise `H_c^1` column still
requires a global proper carrier contraction or an equivalent differential
calculation.  Consequently the honest score remains `2/9`.

## 7. Replay

```console
python ai/omreal/verify_diag2_pivot_all_pair_fibers.py
python ai/omreal/verify_diag3_all_pair_affine_compression.py
python ai/omreal/verify_diag3_joint_affine_failure.py
python ai/omreal/verify_diag3_common_affine_subspace_no_go.py
python ai/omreal/verify_diag3_affine_constant_span_no_go.py
python ai/omreal/verify_diag3_internal_discriminant_wall.py
```

Every calculation is exact over `Z`, `Q`, a finite field, or the explicitly
verified number field `Q(alpha)`.  No floating-point decision is used.
