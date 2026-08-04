# The ninth diagonal: an exact master-chamber graph reduction

## Status

This note does **not** prove the ninth entry of 9DVL. It replaces its
connectivity question by an exact finite labeled-graph test, closes the local
wall-gluing premise left open in the Atlas, strengthens it to an all-strata
label-reconstruction theorem, and proves a small no-go theorem for a tempting
mutation/deformation shortcut.

For a realizable UOM(4,8) parent \(M\), a nine-signature family \(S\), and

\[
                  F_S=\bigcap_{\sigma\in S}F_\sigma,
\]

the unresolved target is

\[
             \widetilde H_0(F_S;\mathbb Q)=0.          \tag{1}
\]

Thus an empty intersection is harmless and every nonempty intersection must
be connected. Parent contractibility gives the equivalent dual target
\(H_c^8(B_S;\mathbb Q)=0\), but no duality is needed below.

The exact reduction is:

> **Master-chamber graph theorem.** There is a finite graph \(G_M\), with a
> set \(T(C)\) of supported extension signatures on every vertex, such that
> for every finite \(S\)
>
> \[
>     \pi_0(F_S)\ \cong\ \pi_0\!\left(G_M[S]\right),   \tag{2}
> \]
>
> where \(G_M[S]\) is the subgraph induced by the vertices \(C\) with
> \(S\subseteq T(C)\). In particular, the ninth diagonal is exactly a
> collection of finite induced-subgraph connectivity tests. No partial-cube,
> COM, or extra wall-gluing premise is required.

The key local point is that the gluing premise is automatic. At a generic
residual wall, a signature supported by both adjacent chambers is supported
on the wall.  More strongly, the label of every interior cell in a regular
residual refinement is the intersection of its incident local chamber-germ
labels.  A
minimal positive Gordan witness which would obstruct either statement is
either a structural circuit persisting nearby or one of the already
certified one-sided residual wall circuits.

## 1. The master chamber graph

For triples \(I\subset[8]\), let \(a_I(Y)\) be the 56 derived normals. For
four triples \(E=\{I_1,I_2,I_3,I_4\}\), put

\[
             D_E(Y)=\det(a_{I_1},a_{I_2},a_{I_3},a_{I_4}).
\]

The derived-wall classification in ATLAS_HELLY.md proves that every \(D_E\)
is either identically zero, a nonzero parent-bracket monomial on \(X\), or a
monomial times one of thirteen residual polynomial types. Let
\(\mathcal D\subset X\) be the union of all nonidentically-zero residual
walls. Duplicate labeled determinants with the same irreducible residual
factor are grouped as one geometric wall.

Choose a finite semialgebraic Whitney stratification compatible with
\(\mathcal D\), refined until the oriented matroid of the specialized derived
normal configuration is constant on every stratum. Only two kinds of strata
will be needed:

* the connected full-dimensional chambers \(C\) of
  \(X\setminus\mathcal D\);
* the connected generic codimension-one wall strata \(W\), after removing
  wall intersections and lower-dimensional specialization loci.

The feasibility of a signature is a tope question for the signed derived
normal configuration. It is therefore constant on every retained stratum.
Write \(T(C)\) and \(T(W)\) for the corresponding sets of feasible extension
signatures.

The vertices of \(G_M\) are the chambers. A generic wall stratum \(W\)
incident to chambers \(C_-,C_+\) gives an edge between them. A signature
feasible on the wall is feasible on both adjacent sides, because feasibility
is defined by strict inequalities and hence is open. Thus

\[
                       T(W)\subseteq T(C_-)\cap T(C_+).          \tag{3}
\]

The next lemma proves equality.

## 2. Generic two-sided gluing

Here “generic wall point” means a point on one geometric residual
hypersurface and on no other. All labeled determinants sharing that residual
factor are allowed to vanish together.

> **Generic two-sided gluing lemma.** Let \(Y_0\) be a generic point of a
> residual wall between chambers \(C_-,C_+\). For every extension signature
> \(\sigma\),
>
> \[
>        \sigma\in T(C_-)\cap T(C_+)
>        \quad\Longrightarrow\quad \sigma\in T(Y_0).  \tag{4}
> \]
>
> Consequently \(T(W)=T(C_-)\cap T(C_+)\) on every connected generic wall
> stratum.

**Proof.** Suppose instead that \(\sigma\) is infeasible at \(Y_0\). Choose a
support-minimal nonnegative Gordan relation

\[
       \sum_{I\in Q}\lambda_I\sigma_Ia_I(Y_0)=0,
       \qquad \lambda_I>0.                            \tag{5}
\]

Its support is a linear circuit. Indeed, if a proper subset were linearly
dependent, perturb \(\lambda\) along that dependence until a coefficient
first becomes zero. The coefficients remain nonnegative and give a smaller
Gordan support. Since the normals lie in four-space, \(|Q|\le5\).

Sizes one and two are impossible. Every derived normal is nonzero, and two
distinct derived normals cannot be parallel: their parent triples would span
the same projective plane, putting at least four parent columns in a
three-space and violating uniformity.

If \(|Q|=5\), circuit minimality makes all five four-by-four cofactors
nonzero. The unique relation and the signs of all its coefficients therefore
persist near \(Y_0\), making \(\sigma\) infeasible in both adjacent chambers.

Suppose \(Q\) is structurally dependent. A structural three-circuit consists
of three parent triples sharing a pair. A structural four-circuit consists of
four triples sharing one label; the other structural four-set type has three
triples sharing a pair and is excluded by circuit minimality. In both cases a
nonzero circuit minor at \(Y_0\) keeps the exact rank and coefficient signs
fixed locally. Relation (5) again persists on both sides.

It remains to treat a nonstructural circuit. If \(|Q|=4\), take \(E=Q\).
Then \(D_E(Y_0)=0\); \(D_E\) is neither structural nor a nonzero fixed
parent-bracket monomial, so it is residual. The localization residual types
have a proper three-circuit and are excluded by minimality. Thus \(Q\) is the
exact four-circuit of an ordinary residual wall.

If \(|Q|=3\), choose a fourth parent triple \(J\) so that
\(E=Q\cup\{J\}\) is nonstructural. Such a \(J\) exists: avoid the common
label of \(Q\), if one exists, and avoid each pair occurring as the
intersection of two triples of \(Q\). There are at most three forbidden
pairs, so among at least seven available labels there are many triples
avoiding them. Now \(D_E(Y_0)=0\), so \(E\) is residual rather than fixed.
The exact residual support classification has nine ordinary types and four
localization types. Every ordinary type has the fixed-unit identity (27a) of
`ATLAS_HELLY.md`; on its wall all four coefficients are nonzero, so its
unique relation cannot be the zero-padded relation on \(Q\). Hence \(E\) is
one of the four localization types, whose designated exact three-circuit is
\(Q\).

In either nonstructural case, (5) says exactly that \(\sigma\) is aligned
with the certified wall circuit, up to the irrelevant global circuit sign.
The derived-wall side theorem makes every aligned signature infeasible on
the wall and feasible on at most one residual sign side. This contradicts
\(\sigma\in T(C_-)\cap T(C_+)\).

All cases contradict two-sided feasibility, proving (4). Labeled
determinants sharing a residual factor cause no ambiguity because
\(D_E=M_Eq\), with \(M_E\) nonzero and fixed-sign throughout \(X\). QED.

The same proof has a stronger pointwise consequence once the global
regularity and side theorems are used at intersections of walls.

> **All-strata gluing theorem.**  Let `D` be the complete residual
> discriminant in one normalized parent cell.  For every `Y_0 in X` and
> every extension signature `sigma`,
>
> \[
>  \sigma\in T(Y_0)
>  \quad\Longleftrightarrow\quad
>  \sigma\text{ is supported by every local master-chamber germ whose
>  closure contains }Y_0.                                  \tag{4a}
> \]
>
> Equivalently, every bad locus is the closure of its generic part:
>
> \[
>        B_\sigma=\overline{B_\sigma\cap(X\setminus\mathcal D)}^{\,X}.
>                                                               \tag{4b}
> \]

If `sigma` is feasible at `Y_0`, one strict witness remains feasible in a
neighborhood, proving the forward implication in (4a).  Conversely, suppose
it is bad and choose the support-minimal positive relation (5).  Supports of
sizes one and two are impossible as above.  A five-circuit has all its
four-by-four cofactors nonzero, so its positive sign persists in an open
neighborhood and supplies a bad generic germ.  A structural three- or
four-circuit has a nonzero circuit minor and its exact structural dependence;
its positive signs likewise persist locally.

For a nonstructural four-circuit, its determinant vanishes at `Y_0`.  It
cannot be a fixed parent-bracket unit and is therefore residual.  The global
derived-wall rank theorem makes it an ordinary exact four-circuit even when
other residual factors vanish at `Y_0`.  The global side theorem puts all
feasible charts on at most one sign side, so the other open side is bad.

For a nonstructural three-circuit `Q`, choose a fourth triple `J` with
`E=Q union {J}` nonstructural.  Again `D_E(Y_0)=0` is residual.  The global
rank theorem gives `rank(E)=3`.  The fixed-unit identity for each of the nine
ordinary residual types has all four relation coefficients nonzero
everywhere on its wall, so no ordinary type can contain the zero-padded
relation on `Q`.  The exhaustive residual support classification therefore
makes `E` one of the four localization types, with `Q` as its designated
three-circuit.  Its side theorem again supplies a bad open sign side.

Every residual factor is smooth on the uniform parent cell.  At a multiwall
point its chosen bad half-neighborhood is therefore nonempty, and the finite
union of the other residual walls cannot fill it.  Generic bad points can be
chosen arbitrarily close to `Y_0`, proving (4b) and the reverse implication
in (4a).

The word *germ* is essential.  A zero/sign word must be split into a regular
semialgebraic refinement on which incident chamber germs are constant before
assigning one cell label; connectedness of the raw zero/sign component is not
enough.  Equation (4a) concerns the actual full-dimensional chamber germs
incident to the point, not an unverified coarse global zero set.

Consequently a complete master cellulation needs exact tope enumeration only
on its full-dimensional chambers.  Every interior lower-cell label is the
intersection of the labels of its incident chambers; compactification-boundary
cells are instead deleted.  This does not prove that a signature's supporting
chambers are connected or convex, so the global ninth-diagonal problem remains
unchanged.

The only finite combinatorial extension fact used in the three-circuit case
can be independently checked without geometry. Among all
\(\binom{56}{3}=27{,}720\) sets of three parent triples, 560 share a common
pair. Every one of the other 27,160 triples has at least 35 choices of \(J\)
for which \(Q\cup\{J\}\) is not one of the two structural four-set types.
The exact checker is:

    python ai/omreal/verify_generic_wall_gluing_combinatorics.py

## 3. Proof of the master-chamber graph theorem

Every nonempty connected component \(U\) of \(F_S\) contains a generic point.
Indeed, \(F_S\) is open in the nine-manifold \(X\), while the finite union
\(\mathcal D\) has empty interior. Therefore \(U\) meets a master chamber,
and that entire chamber lies in \(F_S\) because its derived oriented matroid
is constant.

Suppose two such chambers lie in the same component of \(F_S\). Open
semialgebraic sets are locally path connected, so join interior points by a
path in \(F_S\). Its compact image has a neighborhood still contained in
\(F_S\). Semialgebraic transversality, applied relative to the endpoints,
perturbs the path inside that neighborhood so that it avoids all
codimension-at-least-two strata and crosses codimension-one walls
transversely. Every chamber on the perturbed path supports \(S\). They form
a path in \(G_M[S]\).

Conversely, an edge of \(G_M[S]\) joins two chambers which both support
\(S\). The generic two-sided gluing lemma puts their common wall stratum in
\(F_S\). Openness supplies a small ball in \(F_S\) meeting both chambers, so
the edge gives an actual path between them inside \(F_S\). Concatenating
these local paths realizes every graph path. This gives the bijection (2).
It also shows that \(F_S\ne\varnothing\) exactly when \(G_M[S]\) has a
vertex.

No triangulation of all of \(F_S\), compact-support degree-eight boundary
matrix, or higher-codimension gluing is needed. The remaining work is the
finite enumeration and labeling of full-dimensional chambers and their
adjacencies.

## 4. A budget-nine separator formulation

The reduction can be checked without enumerating all nine-subsets in
advance. Choose two chambers \(u,v\) and put

\[
                         E_{uv}=T(u)\cap T(v).
\]

A set \(S\subseteq E_{uv}\) disconnects \(u\) from \(v\) in \(G_M[S]\)
exactly when every \(u\)-\(v\) path \(P\) contains a chamber which fails at
least one signature of \(S\). Equivalently, with

\[
 L(P)=\bigcup_{C\in P}\bigl(E_{uv}\setminus T(C)\bigr),
\]

the binary selection variables \(z_\sigma\) satisfy

\[
 \sum_{\sigma\in L(P)}z_\sigma\ge1
 \quad\text{for every \(u\)-\(v\) path \(P\)},\qquad
 \sum_{\sigma\in E_{uv}}z_\sigma=9.                  \tag{6}
\]

This is a path-hitting formulation with a connectivity separation oracle:
solve the current binary system, compute the retained graph, and add one
surviving path as a violated constraint. To test the ninth entry of
`DEHC(4,8)` itself, use all proper signature regions, set `z_sigma=0` for
every nonproper region, and add

\[
                         z_\sigma+z_\tau\le1            \tag{6a}
\]

for every pair of comparable feasibility regions. Restricting to the
globally inclusion-minimal family `E(M)` makes incomparability automatic, but
tests only the reduced-core variant: `DEHC(4,8)` deliberately includes
internal antichains of proper regions which are not globally minimal.

A solution of (6)--(6a) satisfying the properness constraints, together with
\(u,v\) and the final graph cut, is a finite certificate of a ninth-diagonal
counterexample. Exhaustive infeasibility for every pair \(u,v\) and every
realizable parent certifies the ninth diagonal. This is still potentially
large, but it is a graph/SAT task rather than a nine-dimensional homology
computation.

## 5. Why global mutation connectivity is insufficient

One might instead regard the incidence space for \(S\) as a partial oriented
matroid realization space: parent brackets and the brackets involving one
new extension at a time are prescribed, while brackets involving several new
elements are free. The global graph of realizable uniform chirotopes is
connected under mutations. That fact does not imply that an arbitrary
fixed-coordinate fiber is connected.

Here is an exact rank-three/five-label obstruction. Normalize

\[
 y_0=e_1,\quad y_1=e_2,\quad y_2=e_3,\quad
 y_3=(a,b,c),\quad y_4=(d,e,f)
\]

and prescribe only

\[
 [012]>0,\qquad [013]<0,\qquad [024]<0,\qquad [034]<0. \tag{7}
\]

The four determinants are

\[
                  1,\qquad c,\qquad -e,\qquad bf-ce.
\]

Thus the partial realization space is

\[
                  c<0,\qquad e>0,\qquad bf<ce<0.       \tag{8}
\]

In particular \(bf<0\), so the sign of \(b\) cannot change. There are exactly
two components. To see that each is an open cell, write

\[
 C=-c>0,\quad E=e>0,\quad B=|b|>0,\quad F=|f|>0.
\]

The remaining inequality is \(BF>CE\), which becomes the open linear
halfspace

\[
       \log B+\log F>\log C+\log E
\]

in logarithmic coordinates; \(a,d\) are free.

The exact checker is:

    python ai/omreal/verify_partial_mutation_fiber_disconnected.py

It independently enumerates the 384 signed uniform rank-three chirotopes on
five labels from the Grassmann--Pluecker axiom. The fiber (7) contains 16
realizable chirotopes, each with an explicit integer matrix, and its induced
free-mutation graph has two components of size eight, matching the two signs
of \(b\).

This example is not of the special star-shaped partial-sign form defining
\(F_S\), is not embedded in one UOM(4,8) parent cell, and is not a
counterexample to (1). It is a rigorously scoped no-go theorem: global
realizable-mutation connectivity and unspecified brackets do not imply
partial-fiber connectivity in general. A ninth-diagonal proof still needs the
special derived-wall structure, which the graph theorem retains.

## 6. Audit against the existing exact obstructions

The master-chamber reduction is compatible with every counterexample already
in the Atlas.

* The rank-three/five-label mutation graph need not be a partial cube. The
  theorem assumes no partial-cube metric.
* The row-2599 same-contraction fiber can be nonconvex. The chamber graph
  records actual adjacency and assumes no convex interpolation.
* Nine simultaneous positive circuit pieces can be pencil-rigid and have no
  common-apex shear. They identify a bad chart, but do not determine the
  connectivity of the common-support chamber graph.
* Smooth globally cooriented walls can bound a disconnected intersection in
  the Atlas polynomial example. In that example the induced supporting
  chamber graph is simply disconnected; smoothness and coorientation are not
  substitutes for the test (2).

## 7. Exact remaining task

For each of the 2,604 realizable parent reorientation classes:

1. enumerate the connected chambers of the residual derived-wall arrangement
   inside the fixed parent cell;
2. label every chamber by its feasible extension signatures;
3. build the chamber adjacency graph; the gluing lemma removes separate
   generic-wall feasibility labels;
4. certify proper-region inclusions and run the budget-nine path-cut test
   (6)--(6a) on the full proper signature family. Restriction to `E(M)` is a
   cheaper test of only the reduced-core variant.

The derived-wall classification and one-sidedness certificates make this
finite and exact, but no complete chamber enumeration has been performed.
Accordingly, the status remains: the ninth diagonal is reduced, not proved.
