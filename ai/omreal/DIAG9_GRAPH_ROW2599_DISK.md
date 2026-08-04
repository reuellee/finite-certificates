# An exact two-dimensional residual disk in parent 2599

## Status

This artifact certifies a complete labeled residual roadmap on a closed
two-dimensional disk inside the projective realization space of catalog
parent 2599.  It is centered at the 65-label crossing found by the exact
coordinate-line roadmap.

The disk theorem is local.  It proves that every finite signature family has
empty or connected common feasibility locus on this disk, but it does not
prove the ninth diagonal for the whole parent cell.

## 1. The embedded coordinate disk

Let `Y_0` be chart zero in `seeat_parent2599_upper178.npz`, let

\[
 t_* = \frac{342087779263}{2802352748594},
\]

and clear the positive denominator to form the integer crossing matrix

\[
 W=2802352748594Y_0+342087779263E_{2,7}.
\]

All matrix indices here are zero based.  The certified square is

\[
 \mathcal Q=\{W(s,u)=W+sE_{2,7}+uE_{1,7}: |s|\le1,\ |u|\le1\}.       \tag{1}
\]

This is not merely a two-parameter matrix family with a hidden gauge
direction.  The first four fixed labeled columns of `W` form a projective
frame.  A projectivity fixing their four projective points is diagonal in
that frame.  The fifth fixed column has four nonzero frame coordinates, so
the diagonal must be scalar.  Finally, the eighth column has a fixed nonzero
row-zero coordinate; two eighth columns in (1) can be proportional only with
scale one, which forces their `s,u` parameters to agree.  The exact verifier
checks the relevant frame and Cramer determinants.  Thus (1) embeds as a
closed disk in the labeled projective realization space.

## 2. Exact common-factor discrimination

The verifier restricts every one of the 84,840 labeled residual four-normal
determinants to (1), producing an exact polynomial in `ZZ[s,u]`.  Exactly 65
have zero constant term.  All 65 divide exactly by the primitive linear
polynomial

\[
 q(s,u)=1401176374297s+849195472073u.                 \tag{2}
\]

Their quotient census is:

| Quotient degree | Occurrences |
|---:|---:|
| 0 | 32 |
| 1 | 33 |

Because at least one quotient is a nonzero constant, the gcd of all 65
restricted polynomials in `QQ[s,u]` is exactly (2), up to a nonzero scalar.
This is stronger than the earlier observation that the polynomials merely
had the same univariate root.

For a polynomial

\[
 p(s,u)=c+\sum_{i+j>0}c_{ij}s^iu^j,
\]

the elementary interval bound

\[
 |p(s,u)|\ge |c|-\sum_{i+j>0}|c_{ij}|                \tag{3}
\]

holds on the unit square.  The exact minimum ratios `|c|/sum|c_ij|` are:

| Family | Exact minimum | Approximate |
|---|---:|---:|
| 84,775 non-crossing residual determinants | `740674058109807867500619055086000864162027205792 / 235417541795415977558174456893317629385` | \(3.146\times10^9\) |
| 65 common-factor quotients | `164520501384745467 / 43462` | \(3.785\times10^{12}\) |
| 70 parent brackets | `164520501384745467 / 43462` | \(3.785\times10^{12}\) |

Every ratio is strictly larger than one.  Consequently:

1. all 70 parent brackets retain their row-2599 signs throughout the square;
2. no residual determinant outside the 65-member group vanishes there;
3. none of the 65 quotients vanishes there.

Therefore the complete residual discriminant in the disk is exactly the one
straight segment `q=0`.  Since

\[
 0<849195472073<1401176374297,
\]

the segment meets the top and bottom edges at

\[
 \left(-\frac{849195472073}{1401176374297},1\right),\qquad
 \left( \frac{849195472073}{1401176374297},-1\right),
\]

and misses the other two edges.  Its complement consists of the two convex
cells `q<0` and `q>0`.

The earlier ambient Jacobian certificate remains relevant.  At the center,
the 65 nonzero gradients have exact rank one and all are transverse to the
`s` direction.  The bivariate factorization now proves that their zero sets
actually coincide throughout this disk.  It still does **not** prove that
the 65 determinant polynomials share one irreducible factor in all nine
parent coordinates; different global walls could restrict to the same local
plane curve.

## 3. Complete signature labels

Exact recursive tope enumeration is performed at

\[
                 (-1,0),\qquad(0,0),\qquad(1,0),
\]

representing the negative cell, wall, and positive cell.  The complete
counts are

\[
                    26{,}112\;--\;26{,}040\;--\;26{,}112.         \tag{4}
\]

The 26,040 wall signatures are exactly the intersection of the two side
label sets.  Precisely 72 signatures occur only in the negative cell and 72
only in the positive cell.

The wall classification and the interval certificate prove that the derived
oriented matroid is constant on each open cell.  Openness excludes
wall-only feasibility, and the direct equality in (4) supplies the gluing.
Thus every signature restricts to one of four possibilities:

\[
             \varnothing,\qquad \{q<0\},\qquad \{q>0\},\qquad\mathcal Q.
\]

Every finite intersection of such sets is empty, one convex cell, or the
whole disk.  This proves:

> **Local all-family theorem.**  For every finite family `S` of extension
> signatures, `F_S intersect Q` is empty or connected.

The conclusion applies in particular to every globally proper
pairwise-incomparable nine-family; it does not infer that `F_S` cannot have
another component outside the disk.

## 4. Finite graph replay

The two open cells give a single-edge chamber graph.  Quotienting the two
non-full restricted support patterns gives the rows `(1,0)` and `(0,1)`.
Both exact ninth-diagonal graph checkers pass:

```console
python ai/omreal/DIAG9_GRAPH_verify_tree_certificate.py \
  ai/omreal/data/DIAG9_GRAPH_row2599_disk_graph.npz
python ai/omreal/DIAG9_GRAPH_cut_sat.py \
  ai/omreal/data/DIAG9_GRAPH_row2599_disk_graph.npz
```

As before, this quotient is a regression for the restricted roadmap.
Global inclusion of feasibility regions is not inferred from restricted
support rows; the local all-family theorem above makes that inference
unnecessary.

## 5. What this adds—and what remains

The one-dimensional certificate could only show that 65 labeled equations
vanished at one parameter.  The disk certificate resolves the first
coverage ambiguity:

* their bivariate gcd is one explicit primitive factor;
* every quotient is a certified unit on the disk;
* no other residual branch enters the disk;
* the complete branch/cell/adjacency structure is therefore proved.

This is the exact reusable local model for a generic duplicate-label wall.
It does not exercise the harder two-dimensional event: an intersection of
two coprime residual factors.  The next local certificate should center a
rational box at such a point and prove, by exact gcd/resultant and Jacobian
rank two, whether the branches cross, are tangent, or avoid one another.  A
transverse pair would produce four local cells and test the first genuine
codimension-two adjacency bookkeeping.

A scalable bounded two-dimensional roadmap can now use the following box
types:

| Box type | Exact acceptance certificate |
|---|---|
| No wall | All residual Bernstein/monomial bounds have one sign |
| One wall factor | Exact factor division; unit quotients; nonzero pivot derivative |
| Two coprime factors | Resultant isolation; rank-two Jacobian; certified branch order |
| Higher specialization | Subresultant multiplicity and recursive subdivision |

Accepted boxes are glued by exact boundary sign words.  One rational sample
per resulting chamber is then labeled by the existing exact tope enumerator.
This handles a bounded two-coordinate surface.  A global ninth-diagonal
proof still requires compatible coverage of all nine coordinates, all
projective normalization charts including infinity, and then the sharp tree
or cut-SAT verdict on the resulting complete master graph.

## 6. Reproduction

```console
python ai/omreal/DIAG9_GRAPH_verify_row2599_slice_jacobian.py
python ai/omreal/DIAG9_GRAPH_verify_row2599_disk.py --build
python ai/omreal/DIAG9_GRAPH_verify_tree_certificate.py \
  ai/omreal/data/DIAG9_GRAPH_row2599_disk_graph.npz
python ai/omreal/DIAG9_GRAPH_cut_sat.py \
  ai/omreal/data/DIAG9_GRAPH_row2599_disk_graph.npz
```

Verdict-producing calculations use only integer and rational arithmetic.
The stored roadmap contains the exact center, factor, 65 occurrence labels,
dominance margins, and all three complete tope sets.

```text
8111a338e2169c4492ad0c5b7e03c9792d5c301c54f0f10a3ce20114db424486  DIAG9_GRAPH_row2599_disk_roadmap.npz
c0521f59aac563a4d7cbcd0405e90a3d4ae26fcf7b9239c9bfce296c6e031b1b  DIAG9_GRAPH_row2599_disk_graph.npz
```
