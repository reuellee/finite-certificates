# Dual single-bad escape for diagonal two

## Outcome

The proposed Gale-dual escape is valid and removes the restriction-map term
from the second-diagonal Mayer--Vietoris sequence.

> **Theorem.**  Let `N` be any realizable uniform rank-four oriented matroid
> on nine elements.  Then
> \[
>                    \widetilde H_7(\mathcal R(N);\mathbb Z)=0.       \tag{1}
> \]
> Consequently, for every uniform extension signature `sigma` of every
> realizable `UOM(4,8)` parent,
> \[
>             H_c^1(B_\sigma;\mathbb Z)=0.                            \tag{2}
> \]

Thus for two signatures the compact-support Mayer--Vietoris sequence reduces
integrally to

\[
 H_c^1(B_\sigma\cup B_\tau;\mathbb Z)
       \cong H_c^0(B_\sigma\cap B_\tau;\mathbb Z).                   \tag{3}
\]

Diagonal two is **not yet proved**: (3) leaves exactly the assertion that the
simultaneous bad locus has no compact component.  What is now unnecessary is
the formerly separate injectivity calculation on
`H_c^1(B_sigma) direct-sum H_c^1(B_tau)`.

## 1. The Gale-dual bridge

Distinguish `p in N` and put

\[
 A=N/p,\qquad A^*=N^*\setminus p.
\]

Then `A` has rank three on eight elements and `A*` has rank five on the same
eight labels.  The contraction--height theorem gives

\[
       \mathcal R(N)\simeq G_p(N)\subset\mathcal R(A),               \tag{4}
\]

where `G_p(N)` is the locus of quotient realizations admitting the prescribed
lift.

Gale duality identifies the projective realization spaces of `A` and `A*`.
Under this identification, `G_p(N)` is exactly the feasibility locus for the
single-element extension `N*` of `A*`.  Here is the coordinate check.  Write a
realization of `A` as a rank-three matrix `X`, let the rows of a rank-five
matrix `Y` be a basis of `ker(X)`, and write a lift of `X` as

\[
                         \begin{pmatrix}X&0\\h&1\end{pmatrix}.
\]

Its kernel consists of

\[
                    (c,-h c),\qquad c\in\ker(X).
\]

In the row basis `Y` this is the rank-five matrix

\[
                         \bigl(Y\mid -Yh^T\bigr),                    \tag{5}

\]

which realizes `N*`.  Conversely, every extension column of `Y` has the form
`-Yh^T` because `Y` has full row rank.  Dual chirotope signs give precisely
the extension signature `tau` determined by `N*`.  Positive column rescalings
are carried to inverse positive rescalings and hence disappear in the same
projective quotient.  Therefore

\[
             G_p(N)\cong F_\tau\subset X^*:=\mathcal R(A^*).         \tag{6}
\]

It remains to prove `H_7(F_tau)=0`.

## 2. Rank-five bad-locus escape

The normalized space `X*` is an oriented open eight-manifold.  Put

\[
                         B_\tau=X^*\setminus F_\tau.
\]

At a point `Y=(y_1,...,y_8)` of `B_tau`, Gordan's alternative supplies a
support-minimal positive dependence among the signed extension normals

\[
 a_I(Y)=\tau_I\,*\!\left(\bigwedge_{i\in I}y_i\right),
                    \qquad I\in\binom{[8]}4.                         \tag{7}
\]

The normals lie in a five-dimensional vector space, so the minimal support
`Q` has at most six members.  Its label-incidence total is at most

\[
                            4|Q|\le24.
\]

Some label `e` therefore occurs in at most three members of `Q`.  For every
incident support put

\[
                    H_I=\operatorname{span}\{y_i:i\in I\},
 \qquad L=\bigcap_{I\in Q,\ e\in I}H_I,                              \tag{8}
\]

with `L=R^5` if `e` has degree zero.  Each `H_I` is a vector hyperplane and
contains `y_e`; hence

\[
                         \dim L\ge5-3=2.                             \tag{9}
\]

Choose a fixed projective frame from six of the other seven labels and hold
all other columns fixed.  Uniformity makes this a global normalization chart.
Move the positive ray of `y_e` inside `L`, staying in its parent residence
chamber.  This motion is nontrivial by (9).

For an incident `I`, write `S=I minus {e}`.  Before a parent wall is reached,
`y_e(t)` is not in `span(y_i:i in S)`, while both `y_e(t)` and `y_e(0)` lie
in the same four-space `H_I`.  Hence

\[
 \bigwedge_{i\in S}y_i\wedge y_e(t)
      =c_I(t)\bigwedge_{i\in S}y_i\wedge y_e(0),
                    \qquad c_I(t)>0.                                \tag{10}
\]

Thus every incident signed normal stays on its original positive ray;
nonincident normals are fixed.  Replacing each Gordan weight `lambda_I` by
`lambda_I/c_I(t)` preserves the positive dependence.

It remains to verify that the motion can really reach the boundary rather
than close up inside `X*`.  For every four-set `J` of labels different from
`e`, let `K_J=span(y_j:j in J)`.  Since `dim(L)>=2` and `dim(K_J)=4`,

\[
                         \dim(L\cap K_J)\ge1.                        \tag{11}
\]

Moreover `L` is not contained in `K_J`, since it contains `y_e` and
uniformity gives `y_e notin K_J`.  Hence `K_J intersect L` is a genuine
projective hyperplane in `P(L)`.  The residence chamber of `y_e` in `P(L)`
therefore has nonempty wall boundary.  Follow any path in that chamber to
its first wall.  All parent bracket signs and the positive witness are
preserved before the endpoint, while at the endpoint a parent five-bracket
vanishes.  The path has no limit in `X*`.

Starting at every point of `B_tau` gives such an escape inside its bad
component.  Semialgebraicity gives only finitely many components, so none is
compact and

\[
                         H_c^0(B_\tau;\mathbb Z)=0.                  \tag{12}
\]

## 3. The homology consequence

The contraction--height theorem applied to the rank-five/eight-element
parent `A*` gives

\[
 \widetilde H_i(X^*;\mathbb Z)=0
     \quad\text{for }i\ge(5-2)(8-5-1)=6.                            \tag{13}
\]

Poincare duality with supports and the long exact sequence of
`(X*,F_tau)` therefore give

\[
 H_7(F_\tau;\mathbb Z)
   \cong H_8(X^*,F_\tau;\mathbb Z)
   \cong H_c^0(B_\tau;\mathbb Z)=0.                                \tag{14}
\]

Equations (4), (6), and (14) prove (1).  For an original rank-four/eight
parent and signature `sigma`, its feasibility space is homotopy equivalent
to `R(N)`, so (1) gives `H_7(F_sigma)=0`.  Applying the same supported-duality
sequence in the oriented nine-manifold parent space (whose homology in
degrees at least six already vanishes by contraction--height) gives (2).
Finally, compact-support Mayer--Vietoris gives (3).

No small-ground-set contractibility citation is needed for this argument.

## 4. Exact sharp-case regression

The support-size bound is sharp: six four-subsets can make every one of the
eight labels have degree three.  The exact checker uses the six edges

```text
0123, 0145, 0167, 2345, 2367, 4567
```

on an integer rank-five moment-curve configuration.  It constructs the
unique signed positive circuit, finds the two-dimensional intersection of
the three incident hyperplanes at label `0`, moves exactly to the first
rational parent wall, and verifies (10) and the rescaled positive dependence
with `Fraction` arithmetic.

```console
python ai/omreal/DIAG2_PIVOT_DUAL_SINGLE_BAD_ESCAPE.py
```

The checker is a regression for the sharp local geometry; the quantified
proof is the dimension-and-residence argument above.
