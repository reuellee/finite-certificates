# The first exact labeled residual roadmap in parent 2599

## Status

This note proves a complete roadmap theorem on one rational coordinate line
inside the realization cell of catalog parent 2599.  It is the first artifact
in this project that certifies all of the geometric input expected by the
ninth-diagonal master-graph reduction: wall coverage, wall grouping,
full-dimensional cells, adjacencies, and complete signature labels.

It does **not** cover the full nine-dimensional parent cell and therefore does
not prove the ninth diagonal for parent 2599, much less for all 2,604
realizable parents.  The honest global score is unchanged.

The subsequent exact two-coordinate neighborhood of the exceptional
crossing is recorded in `DIAG9_GRAPH_ROW2599_DISK.md`.

## 1. Exact statement

Let `Y_0` be chart zero in
`data/seeat_parent2599_upper178.npz`, and use zero-based matrix indices.  Put

\[
       Y(t)=Y_0+tE_{2,7},\qquad -\frac12<t<\frac12 .       \tag{1}
\]

Positive common denominator clearing is used in the stored integer matrices;
it does not change any determinant sign.  The exact verifier proves:

> **Row-2599 coordinate-line roadmap theorem.**  The whole line segment (1)
> stays in the parent-2599 realization cell.  Its residual discriminant has
> exactly 25 geometric points, so its complement has 26 open cells joined in
> a path.  Every one of the 26 cells supports exactly 26,112 extension
> signatures.  Across the 25 walls, 24 crossings lose two signatures and gain
> two, while one crossing loses 72 and gains 72.
>
> Exactly 26,232 distinct signatures occur somewhere on the line.  Their
> support patterns on the 26 cells are:
>
> * 25,992 copies of the full path;
> * the 25 nonempty proper prefixes of the path;
> * the 25 nonempty proper suffixes of the path.
>
> The non-full patterns have total signature multiplicity 240.  Forty-eight
> patterns have multiplicity two; the prefix and suffix adjacent to the
> 65-occurrence crossing each have multiplicity 72.

In particular, for **every** extension signature `sigma`, not only for a
preselected antichain, `F_sigma` intersected with (1) is empty or an interval.
Every finite common feasibility locus on this line is consequently empty or
connected.  This is a genuine all-family connectivity result on the certified
line; it does not infer anything about components which leave the line.

The path roadmap and its complete labels are in
`data/DIAG9_GRAPH_row2599_line_roadmap.npz`.  The 50-row quotient by equal
non-full restricted support patterns is in
`data/DIAG9_GRAPH_row2599_line_graph.npz`.

## 2. Why the wall enumeration is complete

The derived-wall theorem already classifies all four-normal determinants.
Of the 52 incidence orbits, 14 vanish structurally, 25 are nonzero
parent-bracket monomials throughout a fixed uniform parent cell, and 13 have
a genuine residual factor.  Thus only the 84,840 labeled four-sets in those
13 residual orbits can cut (1).

For every one of those 84,840 four-sets, the verifier constructs the exact
integer polynomial

\[
       p_E(t)=\det(a_{I_1}(Y(t)),\ldots,a_{I_4}(Y(t))). \tag{2}
\]

No floating-point root is used in the verdict.  Twenty-five small rational
boxes are hard-coded as root *proposals*.  Exact Sturm sequences then prove,
for every polynomial separately, that:

1. its number of roots in `(-1/2,1/2)` is exact;
2. the sum of its root counts in the 25 boxes equals that global count;
3. every local count is zero or one.

There are 89 labeled root occurrences in total.  Inside each box an exact
polynomial gcd proves that all occurrences have one common algebraic root.
The gcd has exactly one root in the box and no common root with its
derivative there.  The verifier also checks every individual occurrence
against its derivative, excluding hidden repeated/tangent occurrences.
Therefore the 89 occurrences group into exactly 25 transverse residual
crossing points on the line, not merely 25 numerical clusters.  A
one-dimensional restriction alone does not decide whether several labeled
occurrences at the same parameter are duplicate equations for one global
hypersurface or distinct hypersurfaces meeting there; the direct wall-label
audit below makes that distinction unnecessary for this line theorem.

The companion exact Jacobian audit computes all 32 ambient partial
derivatives of all 65 determinants at the exceptional rational crossing.
Every gradient is nonzero, all 65 gradients have exact rank one, and every
gradient has a nonzero `E_(2,7)` component.  Thus the line is transverse and
all first-order tangent hyperplanes agree.  This still does not establish
common global factor identity: distinct smooth hypersurfaces can have the
same tangent hyperplane at an intersection.

The group sizes are

\[
  1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,
  65,1,1,1,1,1,1,1,1.                              \tag{3}
\]

All 70 parent brackets are affine in the one varying entry.  Their exact
signs at both endpoints agree with row 2599, so none vanishes in between.
The ordered disjoint residual boxes and one rational sample between each
successive pair therefore certify all 26 cells and their path adjacency.

The 65-occurrence crossing is also isolated by the smaller rational slice

\[
 \frac3{25}\le t\le\frac{247}{2000}.
\]

Its root is the exact rational number

\[
              t_* = \frac{342087779263}{2802352748594}.          \tag{4}
\]

Direct tope enumeration at the left sample, at (4), and at the right sample
gives

\[
                26{,}112\;--\;26{,}040\;--\;26{,}112,            \tag{5}
\]

and proves that the wall label set is exactly the intersection of the two
side label sets.  This independently audits the exceptional 72/72 mutation.

## 3. Why the signature labels are exhaustive

`DIAG9_GRAPH_exact_topes.py` implements an exact recursive enumeration of a
rational central hyperplane arrangement.  It adds normals one at a time.  If
`H` is the new hyperplane, an old chamber is split exactly when its sign
pattern occurs in the old arrangement restricted to `H`.  Restriction lowers
the ambient dimension and gives the induction.

Every recursive sign pattern carries an integer witness.  If `x` is a strict
restricted witness on `H` and `a` is the new normal, choose an integer `K`
larger than every exact old-margin ratio.  Then

\[
                         Kx+a\quad\hbox{and}\quad Kx-a             \tag{6}
\]

preserve all old strict signs and lie on opposite sides of `H`.  Nonsplit
chambers keep their previous witness.  This proves both soundness and
coverage; it is not a directional sample, LP reconstruction, or numerical
arrangement routine.  A final exact dot-product pass checks all 56 signs of
every returned witness.

Applying the recursion independently at every one of the 26 rational cell
samples returns 26,112 topes each time.  The union and support multiplicities
are recomputed from those full tope lists.  The verifier checks that the
non-full patterns are *exactly* all prefixes and suffixes, rather than merely
checking that every observed pattern happens to be an interval.

Feasibility is open in the parent matrix.  Hence a signature cannot occur
only at a wall.  Conversely, the generic two-sided gluing theorem in
`NINTH_DIAGONAL_SAFE_GRAPH.md` says that a signature occurring in both
adjacent cells occurs on their common residual wall.  Thus the open-cell
labels determine the actual feasibility subsets of the whole line, including
its wall points, and the interval conclusion follows.

## 4. Graph and SAT checks

The 26-cell adjacency graph is the path `0--1--...--25`.  Quotienting the
non-full restricted supports gives 50 rows.  The existing exact verifiers
both accept this finite instance:

```console
python ai/omreal/DIAG9_GRAPH_verify_tree_certificate.py \
  ai/omreal/data/DIAG9_GRAPH_row2599_line_graph.npz
python ai/omreal/DIAG9_GRAPH_cut_sat.py \
  ai/omreal/data/DIAG9_GRAPH_row2599_line_graph.npz
```

The sharp tree verifier skips all 325 vertex pairs because their restricted
support-pattern posets have width below nine.  The complete cut-SAT verifier
returns `PROVED` with zero DPLL nodes after the same exact width prefilter.

There is an important scope distinction.  Inclusion between restrictions to
one line need not imply inclusion between the corresponding global
feasibility regions.  Therefore the 50-row quotient is a pipeline regression
for the **restricted** roadmap, not a certificate of global properness or
incomparability.  The stronger result in Section 1 avoids this issue: every
individual signature support is an interval, so arbitrary globally proper
and incomparable families also have connected common support *on this line*.

## 5. The minimal remaining coverage obstruction

The finite graph theorem and its sharp tree/cut-SAT checkers are no longer the
first missing layer.  The missing layer is a geometric cover of the full
parent cell.

The stored row-2599 atlas has 178 exact point charts and one exact extension
witness for each of 97,224 abstract signatures.  Point certificates prove
nonemptiness, but they do not say how many residual chambers exist, which
charts lie in the same chamber, or which chambers share a generic wall.  The
inventory checker verifies that no full-dimensional master roadmap is stored.

The present line gives a concrete minimal warning: even one bounded
coordinate interval through one stored chart contains 25 previously
uncertified geometric crossings, including one parameter at which 65 labeled
wall determinants vanish.  The line certificate deliberately does not infer
from that coincidence that all 65 equations define one global hypersurface;
distinguishing duplicate factors from higher-dimensional wall intersections
is part of the next coverage layer.  Endpoint or scattered chart sampling
cannot certify their absence or their grouping.  Exact root coverage is
indispensable.

The first genuinely new obstruction after this one-dimensional theorem is
two-dimensional.  On a rational coordinate rectangle one must certify:

* every connected arc of every residual zero curve;
* every intersection or specialization point of those curves;
* the cyclic order and adjacency of all complementary sign cells;
* continuation of every arc through the rectangle boundary.

Univariate Sturm isolation supplies all of that automatically on a line.  A
grid of rational samples does not supply it in a rectangle.  This is the
smallest dimension in which residual curves can form loops, meet, or separate
cells without being detected by a prescribed family of coordinate lines.

## 6. Scalable exact roadmap schema

A proof-producing roadmap can be built one normalized chart at a time.

| Layer | Exact certificate | Failure meaning |
|---|---|---|
| Parent residence | Rational boxes with fixed-sign Bernstein certificates for all 70 parent brackets | Box leaves the chosen parent or meets its boundary |
| Residual signs | Factor-group the 84,840 labeled determinants; one-sign Bernstein certificates on wall-free boxes | Further subdivision is required |
| Generic walls | Use the certified nonzero pivot derivative for each of the 13 residual types to represent the wall as an implicit graph | Box meets a lower-dimensional specialization |
| Wall intersections | Exact resultants/subresultants plus isolating boxes and derivative-rank checks | A codimension-two stratum needs separate treatment |
| Chamber adjacency | Boundary sign words and certified common generic wall patches | Proposed cells are not yet proved incident |
| Signature labels | One rational sample per chamber and exact recursive tope enumeration | Arrangement specialization was missed |
| Ninth verdict | Quotient identical **global** support rows, then run the sharp tree or complete cut-SAT verifier | SAT returns an exact separator candidate |

The known pivot derivatives are parent-bracket monomials and therefore have
fixed nonzero sign on the parent cell.  This is particularly useful for an
interval/Bernstein implementation: once a box meets only one residual factor,
that factor is monotone in its certified pivot coordinate and its zero set is
one graph patch.  Boxes meeting two or more factors are routed to the
resultant layer instead of being guessed from samples.

Unbounded parts of the nine-dimensional parent space must be covered by a
finite family of projective/reciprocal normalization charts.  A bounded box
roadmap without an exact chart-at-infinity cover would still be incomplete.
The first practical next certificate is a bounded two-coordinate rectangle
through `Y_0`; it can reuse the exact tope labeler and both graph verifiers
unchanged while testing the curve-atlas layer that the line case does not
exercise.

## 7. Reproduction and hashes

Build and replay the certificates with:

```console
python ai/omreal/DIAG9_GRAPH_verify_row2599_slice.py --build
python ai/omreal/DIAG9_GRAPH_verify_row2599_slice_jacobian.py
python ai/omreal/DIAG9_GRAPH_verify_row2599_line.py --build-only
python ai/omreal/DIAG9_GRAPH_verify_row2599_line.py
python ai/omreal/DIAG9_GRAPH_inventory.py
```

The stored data hashes are:

```text
29a4542941a322da6846fcfb2d7eb3d427ac9f7cc4becd95b4b5cd754f3ae16b  DIAG9_GRAPH_row2599_line_roadmap.npz
e1c2b82b4da6b2180d1de7e5837d2a58da4dadf159b4631fa4b2810e42df52a5  DIAG9_GRAPH_row2599_line_graph.npz
b982fdc600729306b545005ff059e2c6603b4603525745078fd85b630f36a575  DIAG9_GRAPH_row2599_slice_roadmap.npz
c0521f59aac563a4d7cbcd0405e90a3d4ae26fcf7b9239c9bfce296c6e031b1b  DIAG9_GRAPH_row2599_slice_graph.npz
```

All verdict-producing arithmetic is integer or rational.  Decimal center
strings only define rational candidate boxes; Sturm, gcd, determinant, tope,
and graph checks independently establish every reported conclusion.
