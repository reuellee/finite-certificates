# Third diagonal: the exact pair differential is a balanced end map

## Outcome

For three closed bad loci, the unresolved pair differential has an exact
description in terms of the three exclusive-pair frontiers.  This description
retains zero block masses, specialization to the triple locus, and parent
infinity.

Let

\[
 A_{01}=B_0\cap B_1,\qquad A_{02}=B_0\cap B_2,\qquad
 A_{12}=B_1\cap B_2,
 \qquad T=B_0\cap B_1\cap B_2,                         \tag{1}
\]

and put `E_ij=A_ij minus T`.  With the usual orientation of the block-mass
triangle, write

\[
 D(x_{01},x_{02},x_{12})=
 r_{01}x_{01}-r_{02}x_{02}+r_{12}x_{12},              \tag{2}
\]

where `r_ij` is restriction to `T`.  Suppose

\[
 H_c^0(A_{ij};R)=H_c^0(T;R)=0.                        \tag{3}
\]

The first part of (3) is the proved second-diagonal theorem.  The second is
the still-conditional triple-factor target.

For the closed inclusion `T subset A_ij`, let

\[
 \delta_{ij}:H_c^1(T;R)\longrightarrow H_c^2(E_{ij};R) \tag{4}
\]

be the compact-support frontier map.  Then there is a natural short exact
sequence

\[
 0\longrightarrow\bigoplus_{ij}H_c^1(E_{ij};R)
 \longrightarrow\ker H_c^1(D)
 \longrightarrow\ker\beta\longrightarrow0,           \tag{5}
\]

where

\[
 \begin{split}
 \beta:\{(y_{01},y_{02},y_{12})\in H_c^1(T;R)^3:
           y_{01}-y_{02}+y_{12}=0\}
       &\longrightarrow\bigoplus_{ij}H_c^2(E_{ij};R),\\
 (y_{01},y_{02},y_{12})
       &\longmapsto
       (\delta_{01}y_{01},\delta_{02}y_{02},
        \delta_{12}y_{12}).                            \tag{6}
 \end{split}
\]

Consequently the alternating pair restriction is injective if and only if

1. `H_c^1(E_ij;R)=0` for all three exclusive-pair strata; and
2. the balanced end map (6) is injective.

Condition 2 is the missing image-independence assertion.  It cannot be
replaced by component noncompactness of one-, two-, or three-factor zero
sets.  Section 5 gives a smooth global-graph countermodel in which every such
component is noncompact, every exclusive-pair group in condition 1 vanishes,
and `ker D` nevertheless has rank two.

Thus the current three-factor classifier can close the triple `H_c^0` term,
but its present output does not also close the pair differential.  To do
both, it must be upgraded from an existential escape classifier to a
coherent **signed frontier-incidence** classifier.

## 1. Derived proof of the exact sequence

Write

\[
                         {\mathsf C}(Z)=R\Gamma_c(Z;R).
\]

For every pair, the closed/open decomposition `A_ij=T disjoint union E_ij`
gives a distinguished triangle

\[
 {\mathsf C}(E_{ij})\longrightarrow {\mathsf C}(A_{ij})
 \longrightarrow {\mathsf C}(T)
 \mathop{\longrightarrow}^{\partial_{ij}}
 {\mathsf C}(E_{ij})[1].                              \tag{7}
\]

Take the direct sum of (7), and abbreviate

\[
 U=\bigoplus_{ij}{\mathsf C}(E_{ij}),\quad
 A=\bigoplus_{ij}{\mathsf C}(A_{ij}),\quad
 Q={\mathsf C}(T)^3.                                  \tag{8}
\]

Let `s:Q to C(T)` be `(1,-1,1)` and define

\[
 F=\operatorname{fib}(A\longrightarrow Q
                         \mathop{\longrightarrow}^{s}{\mathsf C}(T)),
 \qquad K=\operatorname{fib}(s).                       \tag{9}
\]

The map `s` is split surjective already at the complex level, so

\[
                         K\simeq {\mathsf C}(T)^2.      \tag{10}
\]

The homotopy-pullback lemma, equivalently the `3 by 3` lemma applied to (7),
gives a natural triangle

\[
                 U\longrightarrow F\longrightarrow K
          \mathop{\longrightarrow}^{\partial}U[1].    \tag{11}
\]

The last arrow is the restriction to `K subset Q` of
`partial_01 direct-sum partial_02 direct-sum partial_12`.  Hence its map on
degree-one cohomology is exactly (6).

The fiber triangle defining `F` and (3) identify

\[
                         H^1(F)=\ker H_c^1(D).          \tag{12}
\]

Equation (10) and `H_c^0(T)=0` give `H^0(K)=0`.  The degree-one part of the
long exact sequence of (11) is therefore

\[
 0\longrightarrow H^1(U)\longrightarrow H^1(F)
 \longrightarrow H^1(K)\mathop{\longrightarrow}^{\beta}H^2(U), \tag{13}
\]

which is precisely (5).

No manifold, transversality, field-coefficient, or chosen-witness hypothesis
is used.  The statement holds over every coefficient ring for which the
displayed compact-support complexes are taken.

## 2. Equivalent direct-sum form

If `H_c^1(E_ij;R)=0`, the long exact sequence of (7) says that `r_ij` is
injective and

\[
 \operatorname{im}r_{ij}=\ker\delta_{ij}
       =:K_{ij}\subset H_c^1(T;R).                     \tag{14}
\]

In that case (2) is injective exactly when the three submodules in (14) are
independent:

\[
 K_{01}\mathbin{\oplus}K_{02}\mathbin{\oplus}K_{12}
       \longrightarrow H_c^1(T;R),\qquad
 (x,y,z)\longmapsto x-y+z                            \tag{15}
\]

is injective.  Pairwise zero intersections are not enough: three distinct
lines in a two-dimensional vector space already have a relation.  A
sequential equivalent of (15) is

\[
 K_{01}\cap K_{02}=0,qquad
 (K_{01}+K_{02})\cap K_{12}=0.                         \tag{16}
\]

This is why proving the three individual restriction maps injective does not
settle the alternating direct-sum map.

## 3. The weakest factor-frontier certificate

Choose a semialgebraic compactification of the parent cell and one finite
triangulation subordinate simultaneously to

* `T`, the three `A_ij`, and the three `E_ij`;
* parent infinity;
* every selected primitive-factor stratum and its specialization faces; and
* the zero-coordinate faces of the block-Gordan witness polytopes.

Such a common triangulation exists.  Compact-support cellular cochains use
the cells at parent infinity as a relative subcomplex.  After ordering the
remaining cells of `A_ij` by `E_ij` and `T`, its coboundary has block form

\[
 d_{A_{ij}}=
 \begin{pmatrix}
 d_{E_{ij}}&b_{ij}\\
 0&d_T
 \end{pmatrix}.                                        \tag{17}
\]

The signed frontier block `b_ij` induces `delta_ij`.  Thus it automatically
records all of the data which a pointwise escape omits: the number of ends,
their orientations, split--merge incidence, specialization to zero witness
faces, and whether a branch ends at `T` or at parent infinity.

The weakest geometric certificate supplied by a factor stratification is
therefore the following **balanced-end detection** statement:

> If three compactly supported factor-stratified one-cocycles on `T` have
> alternating sum a coboundary and each one's signed frontier under its own
> block `b_ij` is a coboundary on `E_ij`, then all three one-cocycles are
> coboundaries on `T`.

This is exactly injectivity of (6), neither stronger nor weaker.  Over
`Q`, after reducing the cellular differentials, it is the rank condition

\[
                  \operatorname{rank}\beta=2\dim H_c^1(T;\mathbb Q).
                                                               \tag{18}
\]

For a torsion-free integral cellular reduction, a coefficient-universal
certificate is stronger: the Smith invariants of the reduced matrix in (18)
must all be units.  Equivalently, the balanced end map has a chain-level
integral left inverse.  Merely proving nonzero determinant over `Q` would
not give injectivity after reduction modulo its determinant.

An $|F|\le3$ factor endpoint can therefore close both remaining
third-diagonal obligations only if it outputs more than the list of
noncompact components.  It must provide a coherent oriented refinement in
which

1. the degree-one and degree-two factor-stratum complexes compute
   `H_c^1(T)` and the three `H_c^2(E_ij)`;
2. the occurrence choices agree on every common specialization face; and
3. the signed blocks `b_ij` satisfy (18), or the unit-Smith version for an
   integral theorem.

The nested compact-component induction in
`DIAG3_TRIPLE_FACTOR_REDUCTION.md` proves only a degree-zero clopen
statement.  At a persistent point it can replace a compact component by a
component on one new factor wall.  A degree-one class can instead circulate
through a split--merge sequence of several walls; there is no single
component to retain when one factor is imposed.  Consequently the same
induction does not construct (17), and the bound of one assigned factor per
signature does not by itself bound the number of factors around such a
cycle.

### 3.1 The smallest integral matrix certificate

After any certified factorwise root/witness contractions, no derived-category
machinery is needed in the final check.  Put

\[
 T^q=C_c^q(T),\qquad U^q=\bigoplus_{ij}C_c^q(E_{ij}),
\]

using finite cellular cochains relative to parent infinity.  Retain all zero
witness faces in these relative groups.  Write `d_T`, `d_ij` for their
coboundaries and `b_ij^q:T^q to C_c^{q+1}(E_ij)` for the signed blocks in
(17).  The block identity `d_A squared=0` says

\[
                    d_{ij}b_{ij}+b_{ij}d_T=0.          \tag{19}
\]

Identify the mass-zero kernel of `(1,-1,1)` by

\[
        (x,y)\longmapsto(x,x+y,y).                     \tag{20}
\]

In degrees zero through two, the fiber complex in (11) is then the following
explicit three-term complex of finite free abelian groups:

\[
 C^0=(T^0)^2\oplus U^0
 \mathop{\longrightarrow}^{N}
 C^1=(T^1)^2\oplus U^1
 \mathop{\longrightarrow}^{M}
 C^2=(T^2)^2\oplus U^2,                               \tag{21}
\]

where, in the block orders

```text
C0: x,y,w01,w02,w12
C1: a,b,z01,z02,z12
C2: A,B,Z01,Z02,Z12,
```

the matrices are

\[
N=\begin{pmatrix}
d_T^0&0&0&0&0\\
0&d_T^0&0&0&0\\
-b_{01}^0&0&d_{01}^0&0&0\\
-b_{02}^0&-b_{02}^0&0&d_{02}^0&0\\
0&-b_{12}^0&0&0&d_{12}^0
\end{pmatrix},                                        \tag{22}
\]

\[
M=\begin{pmatrix}
d_T^1&0&0&0&0\\
0&d_T^1&0&0&0\\
b_{01}^1&0&-d_{01}^1&0&0\\
b_{02}^1&b_{02}^1&0&-d_{02}^1&0\\
0&b_{12}^1&0&0&-d_{12}^1
\end{pmatrix}.                                        \tag{23}
\]

Equation (19) gives `MN=0`.  A vector in `ker M` is exactly a pair of
triple one-cocycles `(a,b)` whose three balanced frontiers are exclusive-pair
coboundaries, together with choices of those coboundaries.  Quotienting by
`im N` changes `(a,b)` by triple coboundaries and changes the choices by
exclusive-pair coboundaries.  Consequently, under (3),

\[
                     H^1(C^\bullet)=\ker H_c^1(D).     \tag{24}
\]

Thus one split-exactness certificate at the middle of (21) closes both
`H_c^1(E_ij)=0` and balanced-end injectivity.  There is a particularly small
coefficient-universal Smith test.  Put `N` into Smith form by unimodular
basis changes on `C0,C1`.  Require every nonzero Smith invariant of `N` to
be `1`, and let `r=rank N`.  In the resulting `C1` basis the first `r`
columns of `M` vanish.  Delete them and call the remaining matrix `bar M`.
Then

\[
 \boxed{\text{all Smith invariants of }N\text{ and }\bar M\text{ are units},
        \quad \operatorname{rank}\bar M=\operatorname{rank}C^1-r} \tag{25}
\]

is equivalent to split exactness at `C1`.  Equivalently there are integral
maps giving a chain-contraction identity

\[
                         h_2M+Nh_1=1_{C^1}.            \tag{26}
\]

It follows after tensoring with every coefficient ring, not only over
`Q`.  A rational rank equality without the unit conditions can acquire a
kernel after reduction modulo a nonunit Smith invariant.

The geometric input needed to populate (22)--(23) is now minimal and
concrete: actual oriented primitive-factor end germs, their split--merge and
specialization incidences, and which ends lie at parent infinity.  Duplicate
occurrence labels and factorwise root choices may be removed only by an
explicit chain homotopy before this reduction; their mere local
connectivity does not change (25).

## 4. Audit of the current triple-factor certificates

The occurrence-level certificates being developed for the three-factor
endpoint contain useful raw data, but not yet the certificate of Section 3.

* A support-plane residence certificate selects a labeled occurrence, a
  moving label, oriented incident plane rays, and bracket-unit signs.  Its
  residence fiber is an oriented open convex projective cell.  The quotient
  base can nevertheless carry low-degree compact-support cohomology, so this
  does not imply `H_c^1(T)=0`.
* A full-frame square-affine certificate proves component noncompactness.  At
  rank drop it can acquire larger affine fibers, and it does not record how
  graph sheets attach across discriminant and resultant walls.
* The present orbit scan chooses some successful frame or occurrence
  independently for each orbit.  It does not choose them coherently on
  shared frontiers and therefore does not determine the blocks `b_ij`.

The stored occurrence labels, moving labels, normal incidences, and unit
signs are enough in principle to seed a signed-atlas pass.  That pass would
need to add every graph-closure/source-boundary face and compare the selected
occurrences on overlaps before any claim about (18) is valid.

## 5. Sharp global-graph countermodel

Component noncompactness fails to determine the balanced end map even for
smooth pair strata cut out by primitive global graph factors.

Use coordinates

\[
 (t,u_1,\ldots,u_7,z)\in X=\mathbb R^9,qquad
 g(u)=u_1^2+\cdots+u_7^2-1,                            \tag{19}
\]

and define three distinct primitive polynomials

\[
 q_0=z,\qquad q_1=z-g,\qquad
 q_2=z-g(2+g^2).                                       \tag{20}
\]

Each `B_i=Z(q_i)` is a global graph over `R^8`, hence is homeomorphic to
`R^8`.  The pair differences are

\[
 q_1-q_0=-g,\qquad q_2-q_0=-g(2+g^2),\qquad
 q_2-q_1=-g(1+g^2).                                   \tag{21}
\]

The extra factors in (21) are strictly positive over `R`.  Therefore every
pair intersection and the triple intersection are the same smooth
noncompact cylinder

\[
 A_{01}=A_{02}=A_{12}=T
   =\{z=0, g=0\}\cong\mathbb R\times S^6.             \tag{22}
\]

Every pair in (22) is a smooth codimension-two complete intersection:
on `g=0`, `dg` is nonzero and the two graph slopes in (20) are distinct.
Thus every component of every one-, two-, and three-factor common zero set
is noncompact.  Moreover,

\[
 H_c^q(B_i;\mathbb Z)=0\quad(q\le2),\qquad
 H_c^0(A_{ij};\mathbb Z)=H_c^0(T;\mathbb Z)=0.          \tag{23}
\]

This model also satisfies the apparently stronger boundary-union condition

\[
             H_c^1(B_0\cup B_1\cup B_2;\mathbb Z)=0.    \tag{23a}
\]

Indeed, in the compact-support Mayer--Vietoris spectral sequence for the
three closed semialgebraic sets, total degree one has only the singleton
terms `direct-sum_i H_c^1(B_i)` and the pair terms
`direct-sum_(i<j) H_c^0(A_ij)`.  Both vanish by (23); the triple
`H_c^0(T)` term lies in total degree two, not degree one.  In fact, once the
individual factor walls have vanishing `H_c^1` and their pair intersections
have vanishing `H_c^0`, condition (23a) is automatic and supplies no new
frontier information.

On the other hand, compact-support Kunneth gives

\[
 H_c^1(A_{ij};\mathbb Z)=H_c^1(T;\mathbb Z)=\mathbb Z. \tag{24}
\]

All three restrictions in (2) are the identity of this `Z`.  Hence

\[
 D=\begin{pmatrix}1&-1&1\end{pmatrix},\qquad
                         \ker D\cong\mathbb Z^2.        \tag{25}
\]

There is no other total-degree-two term or differential in the three-set
compact-support Mayer--Vietoris sequence, so in fact

\[
            H_c^2(B_0\cup B_1\cup B_2;\mathbb Z)
                         \cong\mathbb Z^2.              \tag{26}
\]

Here every `E_ij` is empty, all three frontier maps are zero, and therefore
`beta=0`.  The model is not asserted to be a block-Gordan realization.  It
is a decisive logical falsifier even for the proposed implication from
low-degree acyclicity of every individual factor wall, vanishing pair/triple
`H_c^0`, and vanishing `H_c^1` of the full active-boundary union to balanced
end injectivity.  The union condition lives one Mayer--Vietoris diagonal too
early.  The missing datum is exactly the color-labeled signed frontier
incidence of Section 3.

## 6. Consequence for the third diagonal

After the proved single-bad and pair `H_c^0` vanishings, the coarse
block-mass spectral sequence still has two independent total-degree-two
obligations:

1. `H_c^0(T)=0`, reducible to the three-factor component endpoint; and
2. the two conditions following (6), reducible to the exclusive-pair
   groups and the balanced frontier rank.

The first does not imply the second.  A theorem-grade joined contraction
must geometrically realize the frontier blocks in (17) and exhibit the
left inverse required by (18).  The primitive flow-triangle relation is the
smallest local shadow of that requirement, but a local mass simplex without
the signed factor ends cannot supply it.
