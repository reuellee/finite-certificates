# Projective-carrier chart for a strict five-circuit

## Outcome

The carrier parametrization is valid on the **strict rank-four
five-circuit stratum**, with one orientation correction.

Five signed supporting-plane normals in a strict positive rank-four circuit
form a labeled projective frame in the dual projective three-space.  After
normalizing that frame, parent label \(e\) lies in the fixed carrier

\[
 L_e=\bigcap_{I\in Q,\ e\in I}H_I.
\]

If \(d_e\) is the degree of label \(e\) in the five triples, then

\[
 \dim\mathbb P(L_e)=3-d_e,
 \qquad
 \sum_{e=1}^8\dim\mathbb P(L_e)=9.                              \tag{1}
\]

The normalized carrier tuple is a complete quotient invariant.  Strictly
speaking, its entries are **oriented projective rays**, modulo simultaneous
antipodal reversal, rather than eight unrelated ordinary projective points.
On a fixed uniform parent-chirotope cell this is equivalently one lift
chamber in the ordinary projective carrier product.

This is a useful exact recharting, but it does not prove a middle diagonal.
For the hard row-2599 support

```text
Q0 = 123/134/267/258/468,
```

two exact realizations in the same parent cell and the same strict positive
carrier chamber have a carrier-coordinate midpoint which remains uniform
and retains the strict \(Q_0\) circuit, but flips four parent brackets.  Thus
the parent sign cell is not convex or an orthant in the natural nine carrier
coordinates.  Ball topology is not disproved, but it does not follow from
the parametrization.

Moreover, the carrier chart breaks at zero circuit weights, precisely the
faces required for compact-support Mayer--Vietoris and split--remerge
attachments.  Any proof still has to compactify and glue those strata.

The exact verifier is
[`BLOCK_GORDAN_CARRIER_CHART.py`](BLOCK_GORDAN_CARRIER_CHART.py).

## 1. Setup

Let \(V=\mathbb R^4\), and let

\[
                         Y=(y_1,\ldots,y_8)
\]

be a uniform rank-four parent realization.  Columns are oriented rays: they
may be rescaled by positive scalars, and the whole matrix is quotiented by
\(\operatorname{GL}(V)\).

For a parent triple \(I\), write \(a_I(Y)\in V^*\) for its oriented plane
normal.  Fix a signature \(\sigma\), an ordered five-support

\[
                         Q=(I_1,\ldots,I_5),
\]

and put

\[
                         b_i=\sigma_{I_i}a_{I_i}(Y).
\]

Assume that \((b_1,\ldots,b_5)\) is a strict positive rank-four circuit:

\[
 \operatorname{rank}\{b_i\}=4,
 \qquad
 \sum_{i=1}^5c_i b_i=0,
 \qquad c_i>0.                                                  \tag{2}
\]

The coefficient vector in (2) is unique up to a common positive scalar.
Since the kernel of the four-by-five matrix is one-dimensional and its
generator has no zero coordinate, every four of the \(b_i\) are independent.
This rank-four hypothesis is essential; a lower-rank positive dependence
does not define a projective frame.

## 2. Exact plane-frame normalization

Scale the signed normals by their positive circuit coefficients:

\[
                         \widetilde b_i=c_i b_i.
\]

Define

\[
 T_Y:V\longrightarrow\mathbb R^4,
 \qquad
 T_Y(v)=
 (\widetilde b_1(v),\widetilde b_2(v),
  \widetilde b_3(v),\widetilde b_4(v)).                         \tag{3}
\]

The first four covectors are independent, so \(T_Y\) is invertible.  In the
coordinates \(x=T_Y(v)\), the five signed hyperplane normals are

\[
 h_1=e_1^*,\quad h_2=e_2^*,\quad h_3=e_3^*,\quad h_4=e_4^*,
 \quad h_5=-(e_1^*+e_2^*+e_3^*+e_4^*),                         \tag{4}
\]

because (2) says \(\widetilde b_5=-\sum_{i=1}^4\widetilde b_i\).

This normalization is projectively unique.  A linear map preserving the
first four labeled coordinate hyperplanes is diagonal.  Preserving the fifth
hyperplane \(x_1+x_2+x_3+x_4=0\) forces all four diagonal entries to agree.
Hence the labeled frame stabilizer is scalar and its \(\operatorname{PGL}_4\)
stabilizer is trivial.  The verifier independently obtains rank 20 for the
20-by-21 infinitesimal stabilizer system, leaving only its one-dimensional
scalar solution.

## 3. Carrier dimensions

For a parent label \(e\), let

\[
 d_e=\#\{i:e\in I_i\},
 \qquad
 L_e=\bigcap_{i:e\in I_i}\ker h_i\subset\mathbb R^4.            \tag{5}
\]

Since \(y_e\ne0\) belongs to every incident support plane, \(d_e\le3\): four
incident frame hyperplanes would have zero vector intersection.  Any at most
three frame normals are independent.  Therefore

\[
                  \dim L_e=4-d_e,
 \qquad \dim\mathbb P(L_e)=3-d_e.                               \tag{6}
\]

The five support triples contain 15 label incidences, so

\[
 \sum_{e=1}^8d_e=15,
 \qquad
 \sum_{e=1}^8(3-d_e)=24-15=9,                                  \tag{7}
\]

proving (1).  Thus the carrier normalization exactly matches the familiar
dimension

\[
                         8\cdot3-\dim\operatorname{PGL}_4=9.
\]

It is a coordinate change, not a dimension reduction.

## 4. Correct quotient statement

Let

\[
 \mathbb P^+(L_e)=(L_e\setminus\{0\})/\mathbb R_{>0}
\]

be the space of oriented rays.  Under a positive rescaling of parent column
\(y_e\), the normalized vector \(T_Y(y_e)\) changes by the same positive
factor.  Under \(Y\mapsto GY\), all normalized columns change by the common
factor \(\det G\).  Therefore the quotient-valued map is

\[
 \Phi_Q:[Y]\longmapsto
 [T_Y(y_1),\ldots,T_Y(y_8)]
 \in
 \left(\prod_{e=1}^8\mathbb P^+(L_e)\right)/\{\pm_{\rm all}\}.  \tag{8}
\]

The simultaneous antipode in (8) accounts for row transformations with
negative determinant.  Replacing every \(\mathbb P^+(L_e)\) by ordinary
projective space would additionally identify independent column
reorientations, which do not preserve a fixed oriented matroid.  On a fixed
uniform parent-chirotope cell, only the simultaneous reorientation preserves
all basis signs; hence that cell selects a unique lift chamber over the
ordinary projective carrier product.

Let \(U_{M,\sigma,Q}\) be the subset of (8) satisfying:

1. every four parent columns have the prescribed chirotope \(M\);
2. for each \(I_i\in Q\), its three columns span the designated plane
   \(H_i=\ker h_i\); and
3. the induced oriented support normals lie in the positive frame chamber
   (4).

Then

\[
 \mathcal C_{M,\sigma,Q}^{\rm strict}/
   (\operatorname{GL}_4\times\mathbb R_{>0}^8)
 \ \xrightarrow[\ \Phi_Q\ ]{\cong}\ U_{M,\sigma,Q}             \tag{9}
\]

is a semialgebraic homeomorphism.

Indeed, Sections 2--3 construct \(\Phi_Q\), and the trivial frame stabilizer
proves injectivity.  Conversely, a uniform carrier tuple has three
independent points in each designated plane, so those points span that plane
and reproduce its normal ray.  The lift-chamber condition gives (2), hence a
strict positive circuit.  This construction is inverse to normalization.
All formulas are rational after choosing affine carrier patches.

For a fixed parent chirotope and a fixed lift patch, condition 3 is constant
on each strict component and can be checked at one point.  The exact
row-2599 midpoint below checks it directly rather than relying on this
continuity observation.

## 5. The hard row-2599 carrier product

For

```text
Q0 = 123/134/267/258/468,
```

use that order for the five standard planes (4).  Its label degrees and
carriers are:

| label | degree | carrier | projective dimension |
|---:|---:|---|---:|
| 1 | 2 | \(H_1\cap H_2\) | 1 |
| 2 | 3 | \(H_1\cap H_3\cap H_4\) | 0 |
| 3 | 2 | \(H_1\cap H_2\) | 1 |
| 4 | 2 | \(H_2\cap H_5\) | 1 |
| 5 | 1 | \(H_4\) | 2 |
| 6 | 2 | \(H_3\cap H_5\) | 1 |
| 7 | 1 | \(H_3\) | 2 |
| 8 | 2 | \(H_4\cap H_5\) | 1 |

Thus its carrier product has block dimensions

\[
                         (1,0,1,1,2,1,2,1),                     \tag{10}
\]

which sum to nine.

## 6. Exact nonconvexity inside the positive carrier chamber

Take patterns 0 and 6 from
`data/seeat_parent2599_shatter8.npz`.  The verifier performs the following
entirely exact normalization.

1. It reconstructs the signed normals and primitive positive \(Q_0\)
   coefficients at each endpoint.
2. It applies (3), placing both tuples in the same standard carriers.
3. It positively dehomogenizes the eight oriented rays using homogeneous
   coordinate rows

   \[
                          (4,2,4,3,2,2,4,2),
   \]

   in one-based notation.  The common pivot-sign vector is

   \[
                          (-,-,+,-,-,-,+,-).                     \tag{11}
   \]

4. It verifies that both endpoints are uniform, have identical signs on all
   70 parent brackets, and retain the strict positive \(Q_0\) circuit.

Let \(A\) and \(B\) be the resulting exact rational carrier matrices.  Their
ordinary affine midpoint

\[
                              C=\frac{A+B}{2}                    \tag{12}
\]

still satisfies every carrier equation.  It is uniform: none of its 70
brackets vanishes.  More strongly, all five exact alternating cofactors of
the \(Q_0\) support at \(C\) are positive, so (12) stays inside the strict
positive-circuit chamber.

Nevertheless, exactly four parent signs differ from the endpoints:

\[
                         [1278],\ [1367],\ [1678],\ [3578].      \tag{13}
\]

Therefore

\[
                         C\notin U_{M,\sigma,Q_0}
\]

although \(A,B\in U_{M,\sigma,Q_0}\).  This proves:

> **Exact carrier no-go.**  Even after a strict positive five-circuit fixes
> its supporting planes to the standard projective frame, the parent
> chirotope cell in the nine natural carrier coordinates need not be convex.
> In particular it is not a single affine orthant or an intersection of
> linear halfspaces in those coordinates.

Along the line (12), the sign cell has neighborhoods of both endpoints but
misses the midpoint.  Thus even a one-dimensional simultaneous carrier
slice can meet the cell in more than one interval.

This result is stronger than merely observing that the full parent cell is
nonconvex in a different chart: the midpoint remains in the same strict
positive support-plane chamber.

## 7. What separate convexity does and does not give

In any affine carrier patch, every parent bracket is linear in the
coordinates of one parent column when all other columns are fixed.  Hence
\(U_{M,\sigma,Q}\) is **separately convex in each carrier block**: every
one-block fiber is an intersection of open affine halfspaces.

Separate convexity is not a ball theorem.  A simple proof-safe model is

\[
 W_m=\{(x,y)\in\mathbb R^m\times\mathbb R^m:x\cdot y>0\}.       \tag{14}
\]

Every block slice of (14) is an open halfspace.  Yet

\[
 (x,y)\longmapsto (x,(1-t)y+tx)
\]

is a deformation retraction to \(\{(x,x):x\ne0\}\), and radial contraction
then gives

\[
                              W_m\simeq S^{m-1}.                 \tag{15}
\]

This no-go is compatible with the hard carrier block dimensions (10):

* distribute \(W_4\times\mathbb R\) as \(4+4+1\) coordinates across the
  two two-dimensional and five one-dimensional carrier blocks.  It is a
  nine-dimensional blockwise-convex open manifold with
  \(H_c^6(-;\mathbb Q)\cong\mathbb Q\);
* similarly, \(W_3\times\mathbb R^3\) is compatible with (10) and has
  \(H_c^7(-;\mathbb Q)\cong\mathbb Q\).

The compact-support calculations follow from (15), Poincare duality, and the
degree shift under product with Euclidean space.  These are formal models,
not claimed to occur as oriented-matroid carrier cells.  They prove that
blockwise convexity alone cannot settle the seventh or eighth diagonal.

No comparable countermodel is asserted here for every lower compact-support
degree.  A sharper theorem exploiting the determinant sign system, rather
than separate convexity alone, could still be useful.

## 8. Why the strict chart is insufficient for compact supports

The circuit-cover pieces used in compact-support Mayer--Vietoris are closed
nonnegative-dependence pieces.  Their boundary includes \(c_i=0\).  At such a
point the other four support normals are dependent, so the five labeled
planes cease to be a projective frame and (3) degenerates.  Different
four-support and lower-support strata must be attached there.

Those faces cannot be deleted:

* they are the zero-weight faces of the Gordan polytope;
* several strict circuit vertices can split or remerge through them; and
* the block-Gordan mass filtration uses exactly these attachments to recover
  compact-support Mayer--Vietoris functorially.

Thus even a future proof that every strict carrier sign chamber is an open
ball would not by itself compute the compact-support cohomology of the closed
circuit piece or its intersections.

## 9. Strongest viable use for diagonals 3--8

The carrier theorem provides a sparse exact chart for relative computation:

1. normalize one active strict five-circuit by (3);
2. express every parent bracket and every additional-signature cofactor in
   the nine carrier coordinates;
3. build a sign-invariant cylindrical or regular-cell decomposition, using
   the one-block convex fibers to reduce branching; and
4. attach the four-support and lower-support boundary charts with the
   block-Gordan zero-weight and zero-block incidence maps.

This may be materially smaller than CAD in an arbitrary nine-variable
projective-frame chart, because the carrier equations impose many structural
zeros.  It does not reduce the dimension, and the exact no-go (13) proves
that no single orthant description can replace the cell decomposition.

For multiple signatures, only one five-circuit should be used as the frame;
the other witnesses become signed cofactor conditions in the same carrier
coordinates.  Attempting to normalize several unrelated five-plane frames
simultaneously would reintroduce the failed simultaneous-lift assumption.

The proof target remains a boundary-compatible cellular/Morse complex with
no critical total-degree \(s-1\) class.  The carrier chart supplies local
coordinates for constructing that complex, not the topology theorem itself.

## 10. Verification

Run

```bash
python ai/omreal/BLOCK_GORDAN_CARRIER_CHART.py
```

The checker verifies exactly:

* the positive five-normal relation and invertible normalization (3);
* every support incidence and support-plane spanning condition;
* the scalar-only labeled frame stabilizer;
* the degree and carrier-dimension vectors (10);
* identical uniform parent signs and strict support positivity at patterns 0
  and 6;
* a common oriented affine lift patch;
* carrier incidence, uniformity, and strict support positivity at the exact
  rational midpoint; and
* precisely the four sign reversals (13).

No diagonal is promoted by this note.
