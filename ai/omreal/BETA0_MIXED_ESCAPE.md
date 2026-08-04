# The exact beta-zero mixed survivors escape

## Status

This note proves a sample-specific result needed by the second-diagonal
calculation.  All three pencil-rigid positive `4+5` occurrences with
`beta=0` in the exact row-2599 shatter certificate have vanishing
compact-component group.  There are two distinct signed support pairs (the
occurrences at patterns 4 and 102 are identical):

\[
 H_c^0(C_{\rho,Q}\cap C_{\eta,R};\mathbb Q)=0.
\]

The assertion is for the **closed** circuit pieces, with zero Gordan weights
allowed, not just their full-support relative interiors.  It does not prove
the second diagonal: generic `5+5` intersections remain, and `beta=0` alone
does not force the stabilizer used below.

The exact arithmetic is independently reproducible with

```console
python ai/omreal/verify_beta0_mixed_escape.py
```

## Circuit-piece convention and the cofinal size-five cover

For a signature \(\rho\) and a set \(Q\) of derived triples, write

\[
 C_{\rho,Q}=\left\{[T]\in X:
   \sum_{I\in Q}\lambda_I\rho_I\,\Lambda^3T(e_I)=0
   \text{ for some }\lambda\in\Delta_Q\right\}.       \tag{1}
\]

The simplex is closed, so \(Q'\subset Q\) gives
\(C_{\rho,Q'}\subset C_{\rho,Q}\) by extending the weights by zero.  Gordan's
alternative and conic Caratheodory in the four-dimensional normal space give
a bad dependence with support of size at most five.  Every such support can
be enlarged to a labeled five-set.  Therefore

\[
             B_\rho=\bigcup_{|Q|=5}C_{\rho,Q}.          \tag{2}
\]

Thus the size-five pieces are a cofinal circuit cover.  A `4+5` support pair
is not an additional index of the resulting Cech complex; it is a
zero-weight stratum inside one or more `5+5` intersections.  This does **not**
make its topology disappear.  If the four triples share a hub, their
determinant vanishes identically.  For a fifth normal outside their rank-three
span, the unique five-normal dependence still has fifth coefficient zero, so
locally the enlarged size-five piece is exactly the four-support condition.
The mixed strata must therefore be controlled either topologically or by the
Cech differential.  The theorem below controls the two exact row-2599 strata
topologically.

## The two signed tensor pairs

Let \(V=\mathbb R^8\) with labeled basis \(e_1,\ldots,e_8\), and abbreviate
\(e_{ijk}=e_i\wedge e_j\wedge e_k\).  For a quotient
\(T:V\to\mathbb R^4\), a positive signed dependence is precisely
\(\Lambda^3T(c)=0\) for the corresponding signed sparse three-vector \(c\).

The first pair, occurring at patterns 4 and 102, is

\[
\begin{aligned}
 Q_A&=156/456/127/347/578,
 &c_A&=-e_{156}-e_{456}-e_{127}+e_{347}+e_{578},\\
 R_A&=134/235/238/368,
 &d_A&=-e_{134}+e_{235}-e_{238}+e_{368}.
\end{aligned}                                                   \tag{3}
\]

The second pair, occurring at pattern 217, is

\[
\begin{aligned}
 Q_B&=147/157/367/258/468,
 &c_B&=e_{147}-e_{157}+e_{367}-e_{258}-e_{468},\\
 R_B&=123/345/237/368,
 &d_B&=-e_{123}+e_{345}-e_{237}+e_{368}.
\end{aligned}                                                   \tag{4}
\]

For each pair the seven-row weight-gauge matrix has rank seven.  Hence, if
both witnesses have all coefficients positive, a unique positive column
scaling modulo the diagonal makes all coefficients within each block equal.
Indeed, if \(z\) is the vector of logarithmic weight ratios, solve
\(D x=z\) and replace \(T\) by \(T\circ\operatorname{diag}(e^{x_i})\).
This changes only the representatives of the eight projective columns and
turns the two relations into (3) or (4), up to one harmless positive scalar
per block.

## Full-support escape

For (3), consider the integer endomorphism

\[
A_A=\begin{pmatrix}
-2&0&0&9&0&0&0&0\\
0&4&0&0&0&0&0&0\\
0&-9&-5&0&0&0&0&0\\
0&0&0&7&0&0&0&0\\
0&0&0&0&1&0&0&0\\
0&0&0&0&0&4&0&0\\
0&0&0&0&0&0&10&0\\
0&0&0&0&0&0&0&1
\end{pmatrix}.                                                \tag{5}
\]

Its induced infinitesimal action on \(\Lambda^3V\) satisfies

\[
                       A_Ac_A=12c_A,\qquad A_Ad_A=0.    \tag{6}
\]

Consequently \(g_t=\exp(tA_A)\) projectively stabilizes both relations.
After discarding positive individual column scales, its only motions are

\[
 y_4\longmapsto y_4+u(t)y_1,qquad
 y_2\longmapsto y_2-u(t)y_3,qquad
 u(t)=1-e^{-9t}.                                       \tag{7}
\]

As \(t\to-\infty\), \(|u(t)|\to\infty\), so the moving positive rays tend
to the rays of \(-y_1\) and \(y_3\), respectively.  (The sign matters because
columns are quotiented only by positive scaling.)  Either limit is parallel
or antiparallel to an existing parent column, so the parent configuration
approaches the nonuniform boundary.

For (4), use

\[
A_B=\begin{pmatrix}
-1&0&0&0&0&0&0&0\\
0&5&0&0&0&0&0&0\\
0&0&-4&0&0&0&0&0\\
0&0&0&2&0&0&0&0\\
0&0&0&0&2&0&0&0\\
0&0&0&0&0&5&0&0\\
-6&0&0&0&0&0&5&0\\
0&0&0&0&0&0&0&-1
\end{pmatrix}.                                                \tag{8}
\]

Here

\[
                       A_Bc_B=6c_B,\qquad A_Bd_B=0,     \tag{9}
\]

and, modulo positive column scales,

                     y_1\longmapsto y_1+(1-e^{6t})y_7. \tag{10}

This approaches the positive ray of \(-y_7\) as \(t\to+\infty\), hence again
a nonuniform antiparallel-column boundary point.

Starting at a point of the fixed parent chirotope cell, follow the relevant
flow on the maximal parameter interval on which all parent brackets retain
their signs.  Both signed dependences are preserved throughout.  If the
interval ends at a finite parameter, a parent bracket is zero there.  If it
extends in the escape direction, (7) or (10) produces a column collision.
In either case the path stays in the simultaneous circuit-piece intersection
and approaches the parent boundary.

The displayed directions are not artifacts of an unremoved gauge.  The
checker verifies that the common projective stabilizer equations

\[
                 A c=\mu c,\qquad A d=\nu d             \tag{11}
\]

have a two-dimensional solution space in each case: the scalar direction and
the displayed non-diagonal direction.  Equations (7) and (10) show directly
that the latter changes the labeled projective configuration.

## Zero-weight boundary faces

It remains possible that one of the witnesses in (1) has a zero coefficient,
so the full-support gauge and (5) or (8) need not apply.  This is exactly
where the closed-piece assertion is stronger than an assertion about its
relative interior.

The full support unions in (3) and (4) have nine distinct triples and degree
vectors

\[
          (3,3,5,3,4,3,3,3),\qquad(3,3,5,3,3,3,4,3).   \tag{12}
\]

Deleting any support triple lowers a degree-three label to degree two.
Hence every proper pair of witness supports fails the minimum-degree part of
pencil rigidity.  The projective-plane-pencil lemma then supplies an actual
residence motion preserving the two smaller signed dependences and approaching
the parent boundary.  Since a smaller-support witness is also a witness for
the original closed piece, this motion stays in
\(C_{\rho,Q}\cap C_{\eta,R}\).  The checker exhausts all
\((2^5-1)(2^4-1)=465\) nonempty support-face pairs in each case.  Of these,
464 are proper and are verified to fail pencil rigidity; the remaining
full/full pair is included in the verification of the hereditary rank equality

\[
 \operatorname{rank}D_{Q',R'}=(|Q'|-1)+(|R'|-1).        \tag{13}
\]

## Compact-support conclusion

Take any point of either closed intersection.  If it has full positive
witnesses, Section 3 gives a path in its connected component approaching the
parent boundary.  Otherwise Section 4 gives such a path.  Thus no connected
component is compact.  Circuit-piece intersections are semialgebraic, hence
locally connected with finitely many connected components.  A compactly
supported locally constant function can therefore be nonzero only on a
compact component.  There are none, and so

\[
 \boxed{H_c^0(C_{\rho,Q}\cap C_{\eta,R};\mathbb Q)=0}
                                                               \tag{14}
\]

for both distinct signed pairs, and therefore for all three exact row-2599
`beta=0` mixed occurrences.

## Why this does not settle all beta-zero mixed types

The non-diagonal stabilizer is extra structure, not a formal consequence of
\(\beta=0\).  The checker gives the pencil-rigid beta-zero support pair

\[
  136/147/257/348/358,qquad 126/246/467/568,            \tag{15}
\]

with all tensor coefficients chosen positive.  Its gauge matrix again has
rank seven, but the exact infinitesimal system (11) has only the scalar
solution.  This is a combinatorial/tensor no-go example, not a claim that the
all-positive sign choice is realized by a prescribed extension and not a
counterexample to (14).  It proves that beta zero alone does not supply the
same one-parameter flow.  A universal treatment of the 1,419-orbit
beta-zero support census needs another mechanism (or a signed-realizability
filter), rather than merely repeating the two flows above.
