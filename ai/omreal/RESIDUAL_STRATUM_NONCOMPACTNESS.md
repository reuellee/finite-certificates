# Noncompact residual strata from bracket-unit Jacobian minors

## Outcome

The exact residual-factor certificates have a topological consequence which
was not previously recorded.

1. Every connected component of every labeled residual wall inside a
   normalized uniform `UOM(4,8)` parent cell is noncompact.
2. Every connected component of the common zero set of two distinct
   **canonical representative** residual polynomials is noncompact.
3. The same conclusion holds for the `170` canonical representative triples
   having one displayed bracket-product `3 by 3` Jacobian minor.

The first statement closes the formerly open *multi-circuit all-die escape at
one global factor*.  If several signature blocks die at the same global
residual factor, they may use different labeled wall circuits.  Retarget each
block to its own wall circuit.  All of those signed circuits stay positive on
the entire factor wall, and each wall component has a proper escape in the
parent cell.  A common unsigned circuit is unnecessary.

No diagonal is promoted.  Noncompact graph walls can enclose bounded
chambers, their root-residence sets can be disconnected, and the pair/triple
certificates below do not classify relative `S_8` labelings.  The remaining
problem is global incidence and acyclicity, rather than the existence of an
escape for an all-die face supported on one factor.

## 1. Fixed-minor noncompactness lemma

Let `X` be an open subset of `R^n`, let

\[
                         f=(f_1,\ldots,f_k):X\longrightarrow\mathbb R^k,
\]

and suppose one fixed `k by k` coordinate minor of `Df` is nowhere zero on
`X`.  Put `Z=f^(-1)(0)`.  The implicit-function theorem makes `Z` a smooth
`(n-k)`-manifold.  Projection to the complementary `n-k` coordinates is a
local diffeomorphism on `Z`.

If `C` is a connected component of `Z`, then `C` is open in `Z`, and the
projection of `C` is a nonempty open subset of `R^(n-k)`.  Were `C` compact,
its image would also be compact.  A nonempty open subset of a positive-
dimensional Euclidean space is not compact.  Therefore

\[
 \boxed{\quad k<n\quad\Longrightarrow\quad
       \text{every connected component of }f^{-1}(0)\text{ is noncompact}.
       \quad}                                                     \tag{1}
\]

Injectivity of the projection is not required.  Conversely, mere full
Jacobian rank without one fixed nonvanishing minor is insufficient: compact
manifolds can be covered by several projection charts.

The same proof works semialgebraically.  A noncompact connected semialgebraic
component contains a proper semialgebraic curve after concatenating a path
from the chosen point with curve selection at its frontier.  Thus
"noncompact" in (1) supplies the proper escape needed by compact-support
arguments, not just a set-theoretic end.

## 2. Every individual residual wall

Use the standard projective-frame normalization

\[
Y(a,\ldots,i)=
\begin{pmatrix}
1&0&0&0&1&1&1&1\\
0&1&0&0&1&a&d&g\\
0&0&1&0&1&b&e&h\\
0&0&0&1&1&c&f&i
\end{pmatrix}.                                                   \tag{2}
\]

For each of the thirteen canonical residual types, the exact table in
`verify_derived_walls.py` gives a pivot coordinate `x` for which

\[
                         q(x,z)=A(z)x+B(z),                       \tag{3}
\]

and `A(z)` is, up to sign, a product of parent brackets.  The pivots are

| type | pivot | nonzero slope, up to sign |
|---:|:---:|---|
| 36 | `a` | `[1237]` |
| 37 | `a` | `[1257]` |
| 38 | `a` | `[1278]` |
| 39 | `a` | `[2378]` |
| 41 | `a` | `[2457]` |
| 42 | `a` | `[2478]` |
| 44 | `d` | `[2356][1258]` |
| 46, 47 | `a` | `[1237]` |
| 48 | `a` | `1` |
| 49 | `d` | `1` |
| 50 | `d` | `[1238]` |
| 51 | `f` | `[2468][1456]` |

All parent brackets are nonzero in a uniform parent cell.  Hence the wall is
globally the graph

\[
                 x=-B(z)/A(z)                                   \tag{4}
\]

over the open root-residence set

\[
 U=\{z:(-B(z)/A(z),z)\in X\}\subset\mathbb R^8.                 \tag{5}
\]

Projection is a homeomorphism here, which is stronger than the local
conclusion of Section 1.  Every component of `U`, and hence of the wall, is
noncompact.

This argument is global for every labeled occurrence.  Relabel its eight
parent elements so the occurrence is canonical and use the corresponding
five-element projective frame.  Uniformity makes that normalization global
on the whole parent cell: every denominator is a nonzero parent bracket.
The labeled determinant is a nowhere-zero bracket unit times the canonical
`q`, so it has the same zero set.  Duplicate occurrences, including the
type-46/type-47 localization pair, cause no ambiguity: one occurrence already
parametrizes the common global-factor wall.

There is a useful one-factor dimension reduction as well.  For fixed `z`,
the parent fiber `X_z` is an open interval: every parent-bracket sign
condition is affine in the pivot `x`.  Each strict side

\[
                  X\cap\{\varepsilon q>0\}
\]

therefore projects to an open semialgebraic set `V_epsilon subset R^8` with
empty-or-open-interval fibers.  Locally persistent points in those fibers,
a partition of unity, and straight-line contraction inside each interval
give a homotopy equivalence

\[
                  X\cap\{\varepsilon q>0\}\simeq V_\varepsilon. \tag{5a}
\]

The wall itself is homeomorphic to the root-residence subset `U` from (5).
The same reduction applies to any collection of factor inequalities which
are simultaneously affine in one common pivot: their intersection again has
interval fibers.  This locates, rather than removes, the hard topology in an
eight-dimensional projection domain.

## 3. Positivity persists along a global-factor wall

At an ordinary wall, the four derived normals have rank exactly three.  The
fixed-unit five-vector identities in `verify_derived_wall_sides.py` give all
four coefficients of their unique circuit, up to a common scale, as nonzero
products of parent brackets.  Their signs are therefore constant throughout
the parent cell.  At a localization wall the same statement holds for the
distinguished three-circuit; its three coefficients are fixed bracket units.

Consequently, if a signature is aligned with a labeled wall circuit at one
point, its signed bracket-unit relation is a positive dependence at every
point of the entire global-factor wall.  At an intersection with other
residual walls it need not be used as a newly chosen support-minimal circuit;
the persistent positive dependence is already enough for badness.  This
remains true when different signatures use different labeled occurrences of
the same factor.

Let `H` be one global residual factor and let `S_H` be any finite family of
signatures, each equipped with a positive labeled `H`-wall circuit.  Then

\[
                         H\cap X\subseteq
                         \bigcap_{\rho\in S_H}B_\rho,             \tag{6}
\]

and every component of the left side is noncompact.  The bracket-unit
coefficient formulas give continuous normalized witnesses along it.  Thus an
all-die block face over `H` has a simultaneous proper escape even when its
wall circuits have a pencil-rigid union.

This strengthens the common-circuit theorem in
`BLOCK_GORDAN_MONOCHROMATIC_MASS_TRANSFER.md`: common *factor* is enough.

## 4. Canonical pair and triple strata

Collapse types 46 and 47 to their common polynomial.  For every one of the
`66` pairs among the twelve distinct canonical residual polynomials,
`DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY.py` gives one fixed `2 by 2`
Jacobian minor equal, up to sign, to a product of parent brackets.  Applying
(1) with `(n,k)=(9,2)` proves:

> Every connected component of the common zero set of two distinct
> canonical residual representatives is a noncompact smooth seven-manifold.

Likewise, `DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY.py` gives one fixed
bracket-product `3 by 3` minor for `170` of the `220` canonical triples.
Their common zero components are noncompact smooth six-manifolds.

The separately settled triple `(36,38,42)` has full rank by a two-minor
saturation certificate, not one globally fixed minor, so the compactness
conclusion is not asserted for it.  Nor is it asserted for the four rank-drop
triples or the `45` unclassified triples.

These are representative-normalization theorems.  Two independently labeled
factor occurrences generally require a relative permutation, so the `66`
pair and `170` triple conclusions must not be advertised as a full labeled
`S_8` census.

They concern components of the full geometric common zero set inside `X`.
After deleting its intersections with the other residual factors, a generic
wall cell can be bounded: a noncompact graph cut at finitely many nodes is
the elementary model.  Moreover, a noncompact oriented `d`-manifold can have
nonzero `H_c^d` (already `R^d` does).  In particular, noncompactness of a
seven-dimensional pair stratum does **not** itself give the compact-support
degree-seven vanishing needed for diagonal eight; those orientation classes
still require incidence cancellation.

## 5. Sharp formal no-go for diagonal eight

The failure of the current abstract wall axioms is exact in the target
dimension, even after adding fixed-unit minors for *every* common zero
stratum.  Use coordinates

\[
             (x,y,z,s_1,\ldots,s_6)\in\mathbb R^9,
\]

put

\[
 P=((y^2+z^2)-1)(4-(y^2+z^2)),\qquad
 u=\frac{P}{1+P^2},                                             \tag{7}
\]

and define the parent cell

\[
 X=\{-1<x<u(y,z)\}\times\mathbb R_{s_1,\ldots,s_6}^6.          \tag{8}
\]

Since `-1/2<=u<=1/2`, every `x`-fiber is a nonempty interval and
`X` is homeomorphic to `R^8 times (0,1)`, hence contractible.  Define eight
global factors and strict sides by

\[
\begin{aligned}
 q_1&=x,                 &F_1&=X\cap\{q_1>0\},\\
 q_{j+1}&=s_j\quad(1\leq j\leq6),
                         &F_{j+1}&=X\cap\{q_{j+1}>0\},\\
 q_8&=y+3+s_1,           &F_8&=X\cap\{q_8>0\}.
\end{aligned}                                                     \tag{9}
\]

In the columns `(x,s_1,...,s_6,y)`, the Jacobian of all eight factors has
determinant one.  More strongly, assigning those same distinct columns to
the corresponding rows gives determinant one for every subfamily.  The
fixed-minor lemma therefore makes every connected component of every
nonempty common zero stratum a noncompact smooth manifold.  Each label is
literally one strict factor side, so all-strata label gluing is automatic.

All eight regions are proper and pairwise incomparable.  This can be seen by
varying the independent `x` and `s_j` coordinates.  The only coupled pair is
`s_1` versus `y+3+s_1`: the points with `(y,z,s_1)=(-10,0,1)` and
`(0,0,-1)` reverse those two signs while remaining over nonempty parent
fibers.  Similar explicit rational witnesses are replayed by the checker.

Nevertheless the eighth inequality is redundant in the common support.  If
`x>0` is possible then `u>0`, hence `1<y^2+z^2<4` and in particular
`|y|<2`.  Together with `s_1>0` this forces `y+3+s_1>0`.  Thus

\[
 \bigcap_{i=1}^8F_i=
 \{0<x<u(y,z),\ s_1>0,\ldots,s_6>0\}.                            \tag{10}
\]

The fiber in (10) is nonempty and convex precisely when `u>0`, or
equivalently

\[
                         1<y^2+z^2<4.                            \tag{11}
\]

Thus (10) is homotopy equivalent to an annulus, and

\[
                    H_1\!\left(\bigcap_{i=1}^8F_i;\mathbb Z\right)
                    \cong\mathbb Z.                              \tag{12}
\]

This is not a third-compound or oriented-matroid counterexample.  It proves
that contractibility of the parent, one-sided labels, all-strata gluing, and
fixed unit Jacobian minors through arity eight still do not imply diagonal
eight.  Even noncompactness of every geometric common-zero component cannot
replace UOM-specific control of the topology of multiwall root-residence
domains, including their resultant and infinity strata.

`verify_residual_stratum_no_go.py` checks every fixed unit minor, the exact
inequalities, properness, incomparability, and the reduction (10)--(11).

## 6. Revised target

Equation (4) does not make the root-residence set (5) connected.  The exact
model

\[
       X=(-1/2,1/2)\times\mathbb R,
       \qquad q(x,y)=x+y^2-1
\]

has unit pivot derivative, but `q=0` has two components inside `X`.
Similarly, several individually noncompact graph walls can bound a compact
chamber.  This is why the theorem proves neither residual sign-geodesy nor
the absence of a compact component in `B_sigma intersection B_tau`.

Algebraically, connectivity of (5) is controlled by projection factors
arising when the root (4) meets parent-bracket boundaries.  The first exact
resultant layer already contains the `142` new irreducibles recorded in
`DIAG9_SIGN_GEODESY_AUDIT.md`.  The revised finite frontier is therefore:

1. classify relative labeled pair/triple overlaps, retaining the fixed-minor
   noncompactness certificates where they exist;
2. add the new projection factors required to decompose each root-residence
   set into cells; and
3. prove a global proper acyclic matching on those cells.

The all-die multi-circuit case over one factor is no longer a separate local
obstruction.

## 7. Exact verification

The underlying identities are replayed by:

```console
python ai/omreal/verify_derived_walls.py
python ai/omreal/verify_derived_wall_sides.py
python ai/omreal/DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY.py
python ai/omreal/DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY.py
python ai/omreal/verify_residual_stratum_no_go.py
```

The first checker now explicitly verifies that every canonical residual is
degree one in its displayed pivot and that its bracket-unit derivative is
independent of that pivot.  The other checkers replay the `66` pair and `170`
direct-triple fixed-minor identities.  The passage from those identities to
noncompactness is the elementary fixed-minor lemma in Section 1.
