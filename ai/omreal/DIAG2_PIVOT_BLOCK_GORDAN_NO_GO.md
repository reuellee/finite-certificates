# Diagonal two: block-Gordan resolution and the exact nonprivate pivot wall

## Status

The block-Gordan construction is a correct proper resolution of
`B_sigma union B_tau`, but a Bland matching confined to its convex witness
fibers cannot prove

\[
                         H_c^1(B_\sigma\cup B_\tau;\mathbb Q)=0.
\]

One critical degree-zero witness must remain in every nonempty convex fiber.
The resulting critical sheaf is the constant sheaf on the bad union, so its
compactly supported degree-one cohomology is exactly the group one is trying
to kill.  A successful matching must therefore contain **horizontal parent
pivots**, not only support-simplex pivots.

This note also gives a new exact obstruction inside the genuine parent-16
proper incomparable defect-two example.  Its first cofactor wall along a
natural matching-star ray is maximally nonprivate for the existing pruning
theorem: every one of the 52 five-support paddings remains pencil-rigid with
the partner circuit.  Three new strict five-circuits continue on the outgoing
side.  Thus the pivot does not descend to a flexible face, and support order
alone does not determine the continuation.

This is a proof-safe no-go and finite localization, not a counterexample to
9DVL.  The second diagonal remains open.

The exact checker is

```console
python ai/omreal/DIAG2_PIVOT_VERIFY.py
```

## 1. The block-Gordan resolution is valid

For a parent realization `Y`, put

\[
 K_\rho(Y)=\{\lambda\in\mathbb R_{\ge0}^{56}:
                    A_\rho(Y)^T\lambda=0\}.
\]

Gordan's alternative says `Y in B_rho` exactly when `K_rho(Y)` contains a
nonzero vector.  For two signatures define

\[
 \Gamma_{\sigma,\tau}=
 \left\{(Y,\lambda,\mu):
 \begin{array}{l}
 Y\in X,\quad \lambda,\mu\ge0,\\
 A_\sigma(Y)^T\lambda=0,\quad A_\tau(Y)^T\mu=0,\\
 \mathbf 1^T\lambda+\mathbf 1^T\mu=1
 \end{array}\right\}.                                  \tag{1}
\]

The fiber of the projection `p:Gamma_(sigma,tau) -> X` is

\[
 p^{-1}(Y)=
 \bigl(K_\sigma(Y)\oplus K_\tau(Y)\bigr)
 \cap\{\mathbf 1^T\lambda+\mathbf 1^T\mu=1\}.          \tag{2}
\]

It is nonempty exactly on `B_sigma union B_tau`; whenever nonempty it is a
compact convex polytope.  Equation (1) is closed in `X` times the compact
simplex, so `p` is proper over the bad union.  Proper Vietoris--Begle gives

\[
 H_c^*(\Gamma_{\sigma,\tau};\mathbb Q)
       \cong H_c^*(B_\sigma\cup B_\tau;\mathbb Q).      \tag{3}
\]

This construction is preferable to selecting one minimal circuit: zero
weights, support changes, and the join interval between the two signature
blocks are retained automatically.

## 2. Why a vertical Bland matching cannot finish the proof

Every nonempty fiber in (2) is a compact contractible polytope.  An acyclic
cellular matching restricted to such a fiber cannot match every cell: its
critical cells have alternating count equal to the Euler characteristic
`1`.  The usual Bland collapse leaves exactly one critical vertex.  Sheafwise
this is not an error or an inefficiency.  It realizes

\[
                   R^0p_*\mathbb Q=\mathbb Q_{B_\sigma\cup B_\tau},
        \qquad R^jp_*\mathbb Q=0\quad(j>0).             \tag{4}
\]

Consequently the surviving critical complex still has

\[
 H_c^1=H_c^1(B_\sigma\cup B_\tau;\mathbb Q).           \tag{5}
\]

No shelling or Bland rule which pairs cells only within a fixed witness fiber
can establish the desired vanishing.  A proof must match the remaining
critical generator across parent strata, or prove directly that its
constructible critical sheaf has no compactly supported degree-one class.

### An exact sharp model

This failure already occurs for rational coordinate planes.  In
`X=R^4`, let

\[
 L_0=\{x_3=x_4=0\},\qquad
 L_1=\{x_1=x_2=0\}.                                   \tag{6}
\]

Both pieces are copies of `R^2`, so `H_c^0=H_c^1=0`; their intersection is
the compact point `0`.  Compact-support Mayer--Vietoris gives

\[
                     H_c^1(L_0\cup L_1;\mathbb Q)=\mathbb Q.   \tag{7}
\]

There is an exact block-incidence resolution

\[
 \{(x,u,v):u,v\ge0,\ u+v=1,\
              ux_3=ux_4=0,\ vx_1=vx_2=0\}.            \tag{8}
\]

Its fiber is one endpoint over `L_0 minus {0}`, the other endpoint over
`L_1 minus {0}`, and the full interval over `0`.  Thus (8) has precisely the
compact convex fiber behavior of (1), while (7) is nonzero.

More strongly, a purely combinatorial matching on the support nerve cannot
decide the group.  Replace `L_1` by

\[
                        L'_1=\{x_2=x_4=0\}.            \tag{9}
\]

The two covers `{L_0,L_1}` and `{L_0,L'_1}` have the identical nerve: two
vertices and their edge.  But `L_0 intersection L'_1` is a line, hence has
`H_c^0=0`, and Mayer--Vietoris gives

\[
                     H_c^1(L_0\cup L'_1;\mathbb Q)=0.  \tag{10}
\]

The missing datum is not a directed cycle in the unsigned five-support
nerve.  It is the compact-component cosheaf: which intersection components
are compact, how a triple component maps into the three pair intersections,
and how those components split or merge at a derived wall.  A support-only
acyclic matching has no access to that information.  Equations (6)--(10) are
the smallest possible witness: the failure already appears with two cover
vertices and one nerve edge.

## 3. Exact first pivot in the genuine defect-two pair

Use the parent matrix and proper incomparable extension signatures from
`SECOND_DIAGONAL_DEFECT_TWO.md`.  At `t=0` they have strict positive circuits

\[
\begin{aligned}
 Q&=123/124/134/235/567,\\
 R&=126/247/158/468/378.
\end{aligned}                                           \tag{11}
\]

Their union is pencil-rigid and has global partner defect two.  Follow the
matching-star partner shear

\[
                         y_5(t)=y_5+t y_2.              \tag{12}
\]

Exact interpolation of every parent bracket and all ten oriented circuit
cofactors proves that the first non-strict event on the positive ray is

\[
                         t_*=\frac{541589}{6442906}.    \tag{13}
\]

No parent bracket vanishes there.  The partner circuit `R` and four
coefficients of `Q` remain strictly positive, while precisely the coefficient
of `123` becomes zero.  Hence the wall point carries the positive minimal
four-circuit

\[
                         P=124/134/235/567              \tag{14}
\]

together with the strict circuit `R`.  The distinct union `P union R` has
nine triples and is still pencil-rigid.

## 4. The 52-padding wall fan

Every maximal cofinal piece through (14) has support

\[
                              T_q=P\cup\{q\},
                 \qquad q\in\binom{[8]}3\setminus P.  \tag{15}
\]

There are 52 such supports.  At the wall, the coefficient of `q` is zero.
When the other four alternating cofactors are nonzero, their common
orientation makes the derivative of the `q` coefficient an exact signed
side test.  The checker obtains

| wall behavior | entering triple `q` | count |
|---|---|---:|
| outgoing for `t>t_*` | `126`, `238`, `478` | 3 |
| first-order degenerate | `145`, `146`, `147`, `148` | 4 |
| incoming for `t<t_*` | every other candidate, including `123` | 45 |

The wall determinant is affine with a simple root for all 48 transverse
paddings, so this is a local side theorem, not a floating-point sample.  The
script also checks exact rational points `t_* plus/minus 10^-9`; the parent and
`R` remain strict, and precisely the displayed transverse supports occur on
their asserted sides.

The crucial pruning result is uniform over all 52 candidates:

\[
             T_q\cup R\text{ is pencil-rigid and has }d(T_q\cup R)=2.
                                                               \tag{16}
\]

For every genuine third cover index `T_q != Q`, the pair `Q,T_q` is
pencil-flexible because their union has at most six triples, but the competing
pair `R,T_q` in the same Cech row is never eliminated by pencil pruning.
Therefore none of the 51 available triple rows can be certified private for
the `Q,R` coefficient by the present pruning theorem.

Three of those competitors are geometrically real rather than merely
zero-padded wall labels: just beyond the wall the pairs

\[
 (T_{126},R),\qquad(T_{238},R),\qquad(T_{478},R)        \tag{17}
\]

are strict positive `5+5` pairs in the same parent cell, and every one remains
in the hard defect-two class.

## 5. Consequence for the proposed Bland program

There are now three rigorously separated levels.

1. **Vertical witness matching is complete but tautological.**  It reduces
   (1) to one critical generator over the bad union and preserves the target
   cohomology.
2. **Unsigned support matching is insufficient.**  The same support nerve can
   have different compact-component incidence, as (6)--(10) prove.
3. **A signed horizontal pivot needs geometric side and component data.**  At
   the exact OM wall (13), the smallest alternative padding in colex order is
   `234`, but it is incoming-only.  The smallest eligible outgoing padding is
   `126`.  Even after using the signed side test, its pair with `R` remains a
   hard defect-two term rather than a lower private term.

Thus the next finite object should not be a directed graph on five-supports.
It should be a **component-decorated signed wall graph** whose vertices are
connected components of strict pair strata and whose wall incidences record:

- the exact incoming/outgoing padding fan;
- compact versus noncompact pair components;
- the maps from each wall component to all incident pair components; and
- an exit flag for parent-residence boundary components.

A well-founded Bland order on that decorated graph would prove injectivity if
every non-exit component has an outgoing edge to a lower component and the
resulting component incidence matrix has unit pivots.  The exact wall above is
the first mandatory regression case.  The maximal `5+5` type and partner
defect do not decrease; the `238` and `478` pivots do not even decrease the
distinct union size; and colex order can be applied only after a geometric
side-eligibility test.  A new height function must therefore use genuine
wall/component geometry.

No such global height function is proved here, and no compact component or
nonzero 9DVL class is exhibited.  The honest diagonal score remains `1/9`.
