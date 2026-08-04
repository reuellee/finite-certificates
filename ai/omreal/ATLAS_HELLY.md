# Extension-atlas Helly theory

**Status.**  This note separates one finite conjecture from several unconditional
theorems.  The conjecture is deliberately catalog-sized: it concerns all
2,604 realizable `UOM(4,8)` reorientation classes, not only parent row 2599.
It is still a conjecture.  Two proof shortcuts that would have made it nearly
formal are now ruled out below: neither convex private LP fibers nor sparse
Gordan circuits impose a dimension-only Helly bound, and smooth individual
derived walls do not control their multiple intersections.  On the positive
side, Section 11 proves a sharp COM--Helly theorem and its stronger integral
COM--Leray form, reducing the desired bound to one precise support-state
property, while Section 12 gives an exact classification and a regularity
theorem for every possible derived wall.
Section 13 isolates a finite feasible-COM completion target, proves that wall
topology alone cannot close it, and shows that the completion target is a
strictly stronger high-risk conjecture rather than an equivalent reformulation.
It also records exact row-2599 certificates for an eight-coordinate raw
support cube and for nonconvexity inside one deletion-residence fiber; both
results sharpen the proof boundary without settling the conjecture.
Section 4 now proves the one-color entry of the Nine-Diagonal Vanishing
Lemma for every parent by a contraction--lift argument; the other eight
entries remain open.  It also gives the boundary-corrected Alexander--Gordan
exact sequence for those eight cases, deduces contractibility for 2,546 of
the 2,604 parent realization cells, classifies the actual post-contraction
direction walls, and supplies exact certificates showing why neither the
52 one-wall labels nor simultaneous-contraction convexity completes the
proof.
The main unconditional conclusion is already useful:

> For a normalized realization space of dimension `D`, every jointly
> infeasible family of single-element extensions either contains an
> infeasible subfamily of size at most `D+1`, or contains a subfamily of size
> at most `D` carrying a specified nonzero rational homology group.

At `(r,n)=(4,8)`, `D=9`.  Thus a genuinely large obstruction can never be
topologically invisible: once its emptiness is known, it forces a finite
homology-defect witness on at most nine extensions.  That homology class alone
does not certify the original infeasibility.  This result does **not** bound
the number of charts by ten.  It bounds the arity of the constraints whose
hypergraph coloring is the chart problem.

The topological inputs are established Helly/Leray theorems.  The
project-specific content here is their application to extension-feasibility
regions, the convex-fiber reduction to explicit determinant inequalities,
and the resulting exact certificate interface; no literature-priority claim
is made for that packaging.

## 1. The feasibility nerve is the exact atlas object

Let `M` be a labeled realizable uniform oriented matroid of rank `r` on `n`
elements, with `n>=r+1`.  Fix a labeled projective frame and write

\[
 X=\mathcal R(M)\subset\mathbb R^D,
 \qquad D=(r-1)(n-r-1),
\]

for its normalized realization space.  It is an open semialgebraic set.  Let
`V(M)` be the finite set of labeled realizable uniform single-element
extension signatures of `M`.  For `sigma in V(M)`, define

\[
 F_\sigma=\{Y\in X:\text{some column }p\text{ realizes }\sigma
                         \text{ over }Y\}.
\]

We assume `D>0` below.  When `D=0`, a projective frame fixes the only parent
chart, so every individually realizable extension is supported there and the
atlas width is one.

For `S subset V(M)`, put `F_S=intersection_{sigma in S} F_sigma`.  Different
extensions in `S` get independent missing columns; only their deletion `M`
is shared.  Tarski--Seidenberg gives semialgebraicity, and coordinate
projection of the open strict-inequality incidence set is open.  Hence every
`F_S` is open semialgebraic.

Define the **real compatibility complex**

\[
 K_{\mathbb R}(M)=\{S\subseteq V(M):F_S\ne\varnothing\}.
\]

This is the nerve of the family `{F_sigma}`.  Its minimal nonfaces are exactly
the inclusion-minimal families that cannot share a realization chart.  Let
`H_min(M)` be the hypergraph of those minimal nonfaces and let `w(M)` be the
least number of parent realizations whose extension topes cover `V(M)`.

> **Exact coloring lemma.**
> \[
>                 w(M)=\chi(H_{\min}(M)).                 \tag{1}
> \]

Indeed, a color class contains no minimal nonface if and only if it is a face
of `K_R(M)`.  A face has a common point `Y in F_S`, hence one chart.  Conversely,
the extensions supported by one chart form a face.  This proves (1).

There is a useful dominance reduction before doing any topology.  Put
`sigma <= tau` when `F_sigma subseteq F_tau`, identify signatures with equal
regions, and let `E(M)` contain one representative of every inclusion-minimal
proper region.  When no proper region exists, set `E(M)=empty` by convention
and record `w(M)=1`.  Otherwise an atlas meeting every region from `E(M)`
automatically meets every `F_tau`: in the finite inclusion poset, some minimal
`F_sigma` lies inside `F_tau`.  Therefore restricting the nerve to `E(M)` does
not change `w(M)`.  Its regions form an antichain, so repeated or dominated
constraints cannot create artificial homology tests.

Signatures with `F_sigma=X` are **universal vertices**.  Full-basis
lexicographic extensions are examples.  They contain every other feasibility
region, are never inclusion-minimal when a proper region exists, and occur in
no minimal nonface.  They disappear from `E(M)`, including by convention in
the all-universal case.  All core and defect statements below use this
dominance-reduced family.  From now on, `K_R(M)` and `H_min(M)` mean the nerve
and minimal-nonface hypergraph induced on `E(M)`, and

\[
 h(M)=\max\{|T|:T\in H_{\min}(M)\}
\]

is its Helly number (zero when there is no nonface).

Only atlas width is asserted to be preserved by dominance reduction.  This
`h(M)` is the Helly number of the reduced antichain, not necessarily that of
the full signature family.

## 2. Homology can be computed before projection

The definition of `F_S` has existential quantifiers.  They are unnecessary
for its homotopy type.  For an ordered `(r-1)`-subset `I`, let

\[
 a_I(Y)p=\det(Y_I,p).
\]

For a finite `S`, form the partial incidence space

\[
 Z_S=\left\{(Y,(p_\sigma)_{\sigma\in S}):
   Y\in X,\quad
   \sigma_I a_I(Y)p_\sigma>0
   \text{ for every }I,\sigma\right\}.                 \tag{2}
\]

This is a quantifier-free open semialgebraic set whose defining polynomials
are explicit determinants.

> **Convex-fiber lemma.**  Projection `pi_S:Z_S -> F_S` is a homotopy
> equivalence.  In fact, `Z_S` strongly deformation retracts onto the graph of
> a continuous section of `pi_S`.

**Proof.**  The fiber over `Y` is a product of nonempty open convex polyhedral
cones

\[
 C_\sigma(Y)=\{p:\sigma_I a_I(Y)p>0\text{ for every }I\}.
\]

For every `Y in F_S`, choose one tuple of feasible columns.  The same tuple
remains feasible on a neighborhood of `Y`, because all inequalities are
strict.  Take a locally finite refinement of these neighborhoods and a
partition of unity subordinate to it.  The corresponding convex combination
of the locally fixed tuples is a continuous feasible section.  Straight-line
motion inside each convex fiber deforms `Z_S` onto its graph.  QED.

Consequently

\[
       \widetilde H_i(F_S;\mathbb Q)
       \cong \widetilde H_i(Z_S;\mathbb Q).              \tag{3}
\]

Equation (3) is the practical bridge: a triangulation of the explicit set
(2), followed by exact rational linear algebra on its boundary matrices,
decides every homology group used below.  A nonzero class has a finite
certificate consisting of a checkable semialgebraic triangulation/CAD
equivalence trace together with a cycle and a cocycle of its chain complex
having nonzero pairing.  The cycle and cocycle alone would certify only the
presented complex, not its claimed equivalence to `Z_S`.

## 3. The unconditional small-core-or-homology theorem

The following is an application of [Montejano's topological Helly
theorem](https://arxiv.org/abs/1407.1947).

> **Extension core dichotomy.**  Let `A subset E(M)` satisfy `F_A=empty`.
> Then at least one of the following holds:
>
> 1. Some `T subset A` has `|T| <= D+1` and `F_T=empty`.
> 2. Some `S subset A`, with `1 <= |S| <= D`, satisfies
>    \[
>      \widetilde H_{D-|S|}(F_S;\mathbb Q)\ne0.          \tag{4}
>    \]

**Proof.**  Choose an inclusion-minimal `T subset A` with `F_T=empty`.  If
`|T|<=D+1`, the first alternative holds.  Otherwise every proper intersection
from `T` is nonempty.  Suppose all groups in (4), for `S subset T`, vanished.
Montejano's theorem applies to the open family `{F_sigma:sigma in T}` in the
open subset `X` of `R^D`: open subsets of `X` have zero homology in dimensions
`D` and above.  Its conditions for subfamilies of sizes `1,...,D` are exactly
the assumed diagonal vanishings.  Its size-`D+1` condition is
`H_tilde_-1=0`, meaning nonempty, and holds because those subfamilies are
proper.  The theorem would give `F_T != empty`, a contradiction.  QED.

For `UOM(4,8)`, the complete diagonal is

| number of extensions in `S` | group whose nonvanishing witnesses topology | status |
|---:|---:|---|
| 1 | `H_tilde_8(F_S; Q)` | proved below |
| 2 | `H_tilde_7(F_S; Q)` | open |
| 3 | `H_tilde_6(F_S; Q)` | open |
| 4 | `H_tilde_5(F_S; Q)` | open |
| 5 | `H_tilde_4(F_S; Q)` | open |
| 6 | `H_tilde_3(F_S; Q)` | open |
| 7 | `H_tilde_2(F_S; Q)` | open |
| 8 | `H_tilde_1(F_S; Q)` | open |
| 9 | `H_tilde_0(F_S; Q)` (disconnectedness) | open |

Thus an obstruction of arity greater than ten forces one entry in this table
to be nonzero.  This is unconditional, even if the conjecture in the next
section fails.

There is also a conservative coloring consequence.  Make a hypergraph whose
edges are

* all infeasible sets of size at most `D+1`, and
* all sets `S` of size at most `D` satisfying (4).

Every independent set in this hypergraph is a face of `K_R(M)`.  Therefore a
proper coloring gives a certified atlas upper bound without enumerating any
larger minimal nonface.  If the second edge class is empty, this bounded-arity
hypergraph has the same independent sets and colorings as `H_min(M)`; after
deleting nonminimal edges, it is exactly `H_min(M)`.

## 4. The 8--9--10 Extension--Helly conjecture

The working name for the catalog-sized statement is the **8--9--10
Extension--Helly Conjecture**: eight parent elements leave nine normalized
realization parameters, and the claim is that every incompatibility has a
ten-element witness.  If proved, the result will be called the **8--9--10
Extension--Helly Theorem**, with the descriptive subtitle *ten-locality for
`UOM(4,8)` extension atlases*.  The numerical name is specific to this finite
cell; formula (7) is the corresponding higher-rank research program.

The direct statement that saves computation is the following.

> **`UOM(4,8)` Extension-Helly Conjecture.**  For every realizable uniform
> rank-4 oriented matroid `M` on eight elements, every minimal nonface of
> `K_R(M)` has size at most ten.

This is a finite claim over 2,604 parent reorientation classes.  A stronger
claim gives a concrete proof route.  “Finite” here means finitely falsifiable,
not that brute-force exhaustion is presently cheap:

> **Diagonal Extension-Helly Conjecture, `DEHC(4,8)`.**  For every such `M`
> and every `S` of one to nine signatures whose proper feasibility regions
> are pairwise incomparable under inclusion,
> \[
>       \widetilde H_{9-|S|}(F_S;\mathbb Q)=0.           \tag{5}
> \]

For proof planning, (5) is the **Nine-Diagonal Vanishing Lemma**.  The word
“lemma” is aspirational until it is proved; its nine entries are displayed in
the table in Section 3.  It is the weakest currently isolated topological
bridge to the named 8--9--10 theorem, whereas `FCC_9` would prove the stronger
integral Leray statement.

This strengthening is intentionally quantified over every internal antichain
of proper regions, not only globally minimal regions from `E(M)`.  Therefore
a falsifier for (5) need certify only properness and pairwise incomparability;
a falsifier for the reduced core conjecture must certify membership in `E(M)`.

The core dichotomy proves `DEHC(4,8)` implies the Extension-Helly Conjecture.
The converse need not hold: (5) is a deliberately stronger, independently
certifiable target.

### The one-color diagonal is a theorem

The first entry of (5) admits a uniform proof.  The argument is useful beyond
this catalog because it identifies exactly what is lost when a second
extension is added.

> **Contraction--lift theorem.**  Let `M` be a realizable uniform rank-`r`
> oriented matroid on `n` elements, let `sigma` be a realizable uniform
> extension by `e`, put `N=M+sigma`, and put `C=N/e`.  Then
>
> \[
>       F_\sigma\simeq U_\sigma
>       \quad\text{for some open }
>       U_\sigma\subseteq\mathcal R(C).                \tag{5a}
> \]
>
> Consequently, with
> \[
>       D_C=(r-2)(n-r),
> \]
> one has
> \[
>       \widetilde H_i(F_\sigma;\mathbb Q)=0
>       \qquad\text{for every }i\ge D_C.               \tag{5b}
> \]

**Proof.**  The incidence space `Z_{sigma}` from (2), modulo the harmless
positive scaling of its private column, is the normalized realization space
of `N`; the scaling factor is contractible.  Normalize `N` using a projective
frame containing `e`, an ordered `(r-1)`-set of old elements, and one further
old element, with the fixed frame signs dictated by `N`.  In these coordinates
`e` is the last coordinate vector.  Every old column has the form

\[
                         y_i=(x_i,h_i),                 \tag{5c}
\]

and the `x_i` form the correspondingly normalized realization of the uniform
rank-`(r-1)` contraction `C`.  The frame fixes the affine-height gauge.

For fixed `x`, every bracket of `N` containing `e` already has the prescribed
sign because `x` realizes `C`.  Every remaining bracket is a bracket of `M`,
and expansion in the last row makes it an affine-linear function of the lift
heights `h`.  Thus the fiber over `x` is either empty or an open convex
polyhedron cut out by strict affine-linear inequalities.  Its nonempty image
`U_sigma` is open: a feasible height vector remains feasible under a small
change of `x`.

The same local persistence supplies local constant-height sections.  A
partition of unity and convex combination give a global continuous section
over `U_sigma`; straight-line motion in each convex fiber is a strong
deformation retraction onto its graph.  Together with the convex-fiber lemma
for `Z_sigma -> F_sigma`, this proves (5a).

Uniformity lets one use one fixed projective frame for `C`, so
`R(C)` is an open subset of `R^(D_C)`.  Every component of an open subset of
`R^(D_C)`, when `D_C>0`, is a noncompact `D_C`-manifold and therefore has zero
ordinary top homology; there is no homology above its dimension.  The
zero-dimensional case is immediate.  This proves (5b).  QED.

At `(r,n)=(4,8)`, one has `D_C=2(8-4)=8`.  Therefore

\[
                  \boxed{\widetilde H_8(F_\sigma;\mathbb Q)=0}             \tag{5d}
\]

for every extension signature of every realizable `UOM(4,8)` parent.  More
generally, when `n=2r`, the parent dimension is `(r-1)^2` and
`D_C=r(r-2)=(r-1)^2-1`; hence the one-color diagonal always vanishes in the
balanced cell.

This proof does not iterate formally.  After contracting the first private
column in `Z_S`, each other private column projects to a one-element extension
of `C`, but its contraction signature is not specified by the original data.
If those intermediate signatures are fixed, the remaining lift-height fiber
is again convex.  The full space is obtained by gluing all such pieces across
their rank-`(r-1)` discriminant strata.  Proving that this gluing contributes
no class in degree `D-|S|` is exactly the remaining colored-elimination step
for the other eight diagonals.  For an incomparable family, no projected
private column can vanish: that would make it parallel to the contracted
column and give the same extension region up to the irrelevant global sign.

The reduction can nevertheless be stated exactly.  Choose `sigma_0 in S`,
write `s=|S|`, and use the contraction frame from the proof.  Every other
private column has coordinates

\[
                         p_j=(q_j,t_j).
\]

Pairwise incomparability implies `q_j != 0`: otherwise `p_j` is parallel to
the contracted column and `F_(sigma_j)=F_(sigma_0)`.  Quotienting only by
positive column scale therefore normalizes `q_j` to a point of the oriented
sphere `S^(r-2)`; antipodal points remain distinct.  For fixed
`(x,q_1,...,q_(s-1))`, expansion in the last row makes all parent and private
brackets affine-linear jointly in the old lift heights and the `t_j`.
The same convex-section proof gives

> **Multi-contraction normal form.**  For every pairwise-incomparable `S`,
> \[
> F_S\simeq W_S,
> \quad
> W_S\text{ open in }
> \mathcal R(C)\times(S^{r-2})^{s-1},                 \tag{5e}
> \]
> where membership in `W_S` is the feasibility of one explicit strict linear
> system in the lift variables after the displayed base point is fixed.

At `(4,8)`, the ambient manifold in (5e) has dimension

\[
                 8+2(s-1)=2s+6.                       \tag{5f}
\]

The ordinary dimension bound from (5f) proves only the already-settled case
`s=1`; it does not imply the other diagonal vanishings.  Its value is that it
isolates all nonlinearity in the gluing of intermediate rank-three extension
directions.  A successful proof must contract the corresponding colored
chains across that gluing, rather than assert convexity of `W_S`.

The abstract extension--lifting bijection does not perform this contraction.
It classifies compatible orientations for one fixed lifting and one fixed
extension of an oriented matroid; it does not give a continuous choice while
the realization `x`, the directions `q_j`, and their intermediate rank-three
signatures cross discriminant strata.  See
[Backman--Santos--Yuen, Theorem A](https://arxiv.org/abs/1904.03562).
Using that theorem here without an additional gluing argument would reverse
the needed quantifiers.

The multi-contraction model is exact, but two further audits show that an
interior wall contraction on `W_S` is not yet a complete proof target.  First,
the 52 labels in Section 12 classify rank-four determinants of four derived
normals before contraction.  They do not classify the rank-three direction
walls, the mixed-color lift resultants, or even pairwise incidence between the
original walls.  Second, a compactification-boundary term survives Alexander
duality unless the topology of the parent realization cell is controlled.

### The post-contraction wall alphabet is color-dependent

After contracting the first private column, write the old rank-three columns
as `x_1,...,x_8` and another private direction as `q`.  Its elementary
direction walls are

\[
             \delta_{ab}(q)=\det(x_a,x_b,q)=0.
\]

Three pair normals have exactly five incidence types under `S_8`.  With
brackets now denoting rank-three parent brackets, their exact determinants are
as follows, up to a global sign.

| graph of the three pairs | count | determinant |
|---|---:|---|
| triangle `ab,ac,bc` | 56 | `[abc]^2` |
| star `ab,ac,ad` | 280 | `0` |
| path `ab,bc,cd` | 840 | `[abc][bcd]` |
| path plus edge `ab,bc,de` | 1,680 | `[abc][bde]` |
| matching `ab,cd,ef` | 420 | `[abe][cdf]-[abf][cde]` |

Only the matching type is a genuine direction discriminant on the uniform
locus.  It is smooth there: in the standard normalized chart one coordinate
derivative of its residual is a nonzero parent bracket.  The exhaustive exact
check is [`verify_9dvl_postcontraction.py`](verify_9dvl_postcontraction.py).

These five uncolored types are still not the full alphabet.  For `s` original
extensions, the contraction normal form has `s+4` lift variables and a signed
coefficient matrix

\[
 A_s(x,q)\in
 \mathbb R^{(70+56(s-1))\mathbin\times(s+4)}.          \tag{5g}
\]

Its maximal minors include the direction walls and, once two remaining
directions are present, irreducible mixed-color resultants.  One exact
seven-by-seven minor is, up to sign,

\[
 \delta_{15}(q_1)\delta_{24}(q_2)
 -\delta_{14}(q_1)\delta_{25}(q_2).                   \tag{5h}
\]

Thus the needed faces depend on labels and colors, not only on one-wall orbit
types.  Even before contraction, two pairs with the same orbit multiset
`{46,46}` can have opposite incidence behavior: one pair is the same nonempty
wall, whereas another is disjoint throughout the uniform locus.  The latter
claim follows from the exact localization identity

\[
 q_1-cq_2=-[1456][2367],
\]

whose right side is a unit there.  This is checked by
[`verify_9dvl_wall_incidence.py`](verify_9dvl_wall_incidence.py).  Consequently
the 52 one-wall labels cannot be the face poset of a chain contraction.

Double contraction gives a useful local bound, but not the missing global
vanishing.  Fix two independent private columns as the last two coordinate
vectors and fix the projectivized rank-two quotient `V` of the eight old
columns.  Modulo the two affine-height gauges, each contraction signature cuts
out a pointed open polyhedral cone in

\[
                      Q=\mathbb R^8/\operatorname{row}(V).
\]

Its projectivization is a convex five-cell.  Write the two height classes as
`a,b in Q`.  Every parent bracket has the bilinear form

\[
                  \Delta_I(V,a,b)=\det(V_I,a_I,b_I).   \tag{5i}
\]

For fixed `a`, all parent-sign inequalities are strict linear inequalities in
`b`.  Projection to `a` therefore has convex fibers, and the same
partition-of-unity argument as above proves that the fixed-`V` double-lift
fiber is homotopy equivalent to the open set

\[
 P_V=\{a:\text{some admissible }b\text{ realizes the parent signs}\}
      \subset\mathbb R^5.                              \tag{5j}
\]

In particular its ordinary homology vanishes in degrees at least five.  This
is much weaker than the required global `H_7` vanishing: `V` varies through a
five-dimensional stratified quotient space, and the mixed zero sets
`det(p_0,p_1,y_i,y_j)=0` are unconstrained codimension-one walls that cannot be
discarded.

Nor can `P_V` be replaced by a convex set, even under the actual reduced
9DVL hypotheses.  An exact `UOM(4,8)` certificate gives a proper,
pairwise-incomparable pair of extension regions and two points of one fixed
quotient fiber with the same parent and extension signs whose height midpoint
reverses exactly one parent bracket.  Separate exact charts support each
extension while a positive Gordan dependence excludes the other.  The
integer-only check is
[`verify_9dvl_double_contraction.py`](verify_9dvl_double_contraction.py).
This rules out convex iteration; it neither constructs a homology class nor
refutes the two-color case.

### The Alexander--Gordan reduction has a boundary term

There is nevertheless a finite exact reformulation of all eight open cases.
For `S={sigma_1,...,sigma_s}`, let `A_i(Y)` be the `56 by 4` matrix whose rows
are the derived normals signed by `sigma_i`, put

\[
 B_i=X\setminus F_{\sigma_i},\qquad
 B_S=\bigcup_i B_i=X\setminus F_S,
\]

and define the normalized Gordan space

\[
\Gamma_S=\left\{(Y,z_1,\ldots,z_s):
\begin{array}{l}
Y\in X,\quad z_i\ge0,\quad A_i(Y)^Tz_i=0,\\
\displaystyle\sum_{i,I}z_{i,I}=1
\end{array}\right\}.                                  \tag{5k}
\]

Zero color blocks are allowed.  Hence a point of `Gamma_S` certifies that at
least one extension in `S` is infeasible.

> **Alexander--Gordan boundary theorem.**  For every `2 <= s <= 9` there is
> a natural exact sequence, with rational coefficients,
> \[
> \widetilde H_{10-s}(X)
> \longrightarrow H_c^{s-1}(\Gamma_S)
> \longrightarrow \widetilde H_{9-s}(F_S)
> \longrightarrow \widetilde H_{9-s}(X)
> \longrightarrow H_c^s(\Gamma_S).                    \tag{5l}
> \]

**Proof.**  Gordan's theorem says that projection `Gamma_S -> B_S` is
surjective.  Its fiber over `Y` is the intersection of the simplex
`sum z=1` with homogeneous linear equations, hence is a nonempty compact
convex polytope.  The projection is proper, so Vietoris--Begle gives

\[
                  H_c^*(B_S;\mathbb Q)
                  \cong H_c^*(\Gamma_S;\mathbb Q).     \tag{5m}
\]

Put `K=S^9 minus X` and `D_S=S^9 minus F_S=K union B_S`.  Excision identifies
`H^*(D_S,K)` with `H_c^*(B_S)`.  Alexander duality identifies

\[
\begin{aligned}
\widetilde H^{s-1}(D_S)&\cong\widetilde H_{9-s}(F_S),\\
\widetilde H^{s-2}(K)&\cong\widetilde H_{10-s}(X),\\
\widetilde H^{s-1}(K)&\cong\widetilde H_{9-s}(X).
\end{aligned}
\]

Substitution into the long exact sequence of `(D_S,K)` proves (5l).  QED.

Exactness shows what must actually be proved.  The `S` case of 9DVL is
equivalent to the first map below being surjective and the second being
injective:

\[
\widetilde H_{10-s}(X)\longrightarrow H_c^{s-1}(\Gamma_S),
\qquad
\widetilde H_{9-s}(X)\longrightarrow H_c^s(\Gamma_S). \tag{5n}
\]

It is not currently justified to delete the two parent-space terms.  The
standard small contractibility theorem concerns realizable uniform rank-three
oriented matroids on at most nine elements, not rank four on eight elements;
see the summary in
[Richter-Gebert's handbook chapter](https://www.csun.edu/~ctoth/Handbook/chap6.pdf).
The complete `UOM(4,8)` realizability classification of
[Fukuda--Miyata--Moriyama](https://arxiv.org/abs/1204.0645) supplies no
uniform contractibility theorem.

The older exact classification does, however, settle most parent-boundary
terms after one additional topological argument.

> **Reducible-parent corollary.**  The 2,546 `UOM(4,8)` reorientation classes
> certified by Corollary 4.9 of Bokowski--Richter have contractible normalized
> realization spaces.  Thus, for each of those parents and every `2 <= s <= 9`,
> (5l) reduces to
> \[
>       \widetilde H_{9-s}(F_S;\mathbb Q)
>       \cong H_c^{s-1}(\Gamma_S;\mathbb Q).            \tag{5o}
> \]

**Proof.**  Their Definition 4.4 says that `M` is reducible by `p` only when
*every* realization of `M minus p` extends to a realization of `M`; Theorem
4.8 and Corollary 4.9 certify such a point in `M` or `M^*` for 2,546 classes.
See
[Bokowski--Richter, Section 4](https://www.math.ucdavis.edu/~deloera/MISC/LA-BIBLIO/trunk/Richter-Gebert/Richter13.pdf).

Normalize a deletion realization `Y` in one fixed projective frame.  The
possible positions of `p` form a nonempty open convex polyhedron

\[
 C_Y=\{z:g_i(Y,z)>0\text{ for all brackets containing }p\}\subset\mathbb R^3.
\]

A continuous center can be chosen without assuming constant fiber
combinatorics: the function

\[
 \phi_Y(z)=\tfrac12\lVert z\rVert^2-\sum_i\log g_i(Y,z)
\]

is proper and strictly convex on `C_Y`, so it has a unique minimizer `c(Y)`;
the positive-definite Hessian and the implicit-function theorem make `c`
continuous.  Straight-line motion to `c(Y)` is a fiberwise strong deformation
retraction.  The deletion is a `UOM(4,7)`, whose Gale dual has rank three on
seven elements and hence has contractible realization space by the small
rank-three theorem.  Gale duality handles the classes for which `M^*` is the
reducible member.  Therefore `R(M)` is contractible, and (5o) follows from
(5l).  QED.

The classification leaves 82 classes outside that reducibility test.  Its
later perturbation arguments prove 58 of them realizable and 24
nonrealizable, but do not say that every deletion realization extends.
Accordingly, the parent terms in (5l) remain necessary for those 58 realizable
parents.  Complex smoothness or irreducibility does not remove them: it does
not imply that a real oriented sign cell is connected or acyclic.

The interior part also has a precise finite filtration.  For nonempty
`J subseteq S`, let

\[
G_J=\{(Y,(\lambda_i)_{i\in J}):
Y\in X,\ \lambda_i\in\Delta^{55},\ A_i(Y)^T\lambda_i=0\}.
\]

Filtering (5k) by the support of the color masses gives

\[
 E_1^{p,q}=\bigoplus_{|J|=p+1}H_c^q(G_J;\mathbb Q)
 \quad\Longrightarrow\quad H_c^{p+q}(\Gamma_S;\mathbb Q).       \tag{5p}
\]

On total degree `s-1`, its entries are `H_c^{s-|J|}(G_J)`.  Already for
`s=2`, the unresolved associated-graded maps require both the cokernel in
degree zero and the kernel in degree one of the two forgetful face maps to
vanish.  No verified determinant identity currently proves either statement;
higher `s` also has higher differentials.  The honest remaining target is
therefore a **boundary-augmented multicolor contraction** proving (5n) and
the relevant differentials in (5p).  An interior contraction using only the
52 individual wall orbits would omit both mixed resultants and `K`.

The exact algorithmic consequence of the headline conjecture is
**ten-locality**: for every `A subset E(M)`,

\[
 F_A\ne\varnothing
 \quad\Longleftrightarrow\quad
 F_T\ne\varnothing\text{ for every }T\subseteq A,\ |T|\le10.       \tag{6}
\]

This supports lazy core extraction, symmetry reduction, and caching of small
subproblems.  It does not recommend brute enumeration of `O(|E(M)|^10)`
subsets, which could cost far more than the original computation.
Equivalently, `K_R(M)` is determined by its nine-skeleton: it is the
ten-local (coskeletal) completion of its faces of size at most ten.

The unconditional dichotomy by itself does not save core-hours: a small
homology defect is generally feasible and is not an incompatibility
certificate.  Runtime savings require proving the headline conjecture, a
usable defect bound, or operating the validate/add/recolor separation loop.
This program concerns common-chart atlas computations; it does not alter the
already completed 9,276,595-class realizability sweep.

A riskier high-payoff strengthening is that every reduced compatibility
complex here is rationally `9`-Leray.  That statement is combinatorially
natural and would unlock fractional-Helly machinery.  It is not the headline
conjecture, and (5) is only one sufficient route to it when strengthened from
the single diagonal to the full homology tail (8).  Section 11 shows that any
rank-nine COM-completion proof would automatically establish the still
stronger integral `9`-Leray statement.

A direct counterexample to the core conjecture is a minimal family `T` of at
least eleven extensions, certified by

1. certificates that its regions represent inclusion-minimal classes in the
   dominance poset `E(M)`,
2. an exact emptiness certificate for `F_T`, and
3. a feasible exact realization for every `F_{T minus {sigma}}`.

A counterexample to `DEHC(4,8)` is smaller: one set `S` of at most nine
extensions, exact certificates that its regions are proper and pairwise
incomparable, and an exact nonzero cycle/cocycle certificate for (5).  Such a
counterexample would not by itself disprove the core conjecture.

The natural formula in general rank and size is

\[
 h(M)\stackrel{?}{\le}(r-1)(n-r-1)+1,                  \tag{7}
\]

but (7) is **not** asserted here for all `r,n`.  The catalog-sized conjecture
is the defensible first target; universality makes the global version risky.

## 5. The most general defect-sensitive proof

The diagonal theorem is enough for Helly number.  If one wants the stronger
Leray property, [Hell's spectral-sequence theorem](https://arxiv.org/abs/math/0506399)
gives a cardinality-indexed sufficient condition.

> **Defect-Leray theorem.**  Let `k >= D`.  If every nonempty `F_S`, for
> `S subset E(M)`, satisfies
> \[
>   \widetilde H_i(F_S;\mathbb Q)=0
>       \quad\text{for every }i\ge k-|S|,               \tag{8}
> \]
> then `K_R(M)` is rationally `k`-Leray.  In particular, every minimal
> nonface has size at most `k+1`.

Here rationally `k`-Leray means every induced subcomplex has zero reduced
rational homology in dimensions `k` and above.  A minimal nonface of size `m`
induces the boundary of an `(m-1)`-simplex, with nonzero rational homology in
dimension `m-2`, so `m<=k+1`.

This packages into an unconditional numerical bound.  Set

\[
 \operatorname{hd}_{\mathbb Q}(Y)
   =\max\{i\ge0:\widetilde H_i(Y;\mathbb Q)\ne0\},
\]

with value `-infinity` for a rationally acyclic space, and define

\[
 \kappa(M)=\max\left(
 D,\ 1+\max_{S\subseteq E(M),\ F_S\ne\varnothing}
       (|S|+\operatorname{hd}_{\mathbb Q}(F_S))
 \right).                                               \tag{9}
\]

Then (8) holds with `k=kappa(M)`, hence

\[
 K_{\mathbb R}(M)\text{ is rationally }\kappa(M)\text{-Leray},
 \qquad h(M)\le\kappa(M)+1.                            \tag{10}
\]

The `+1` in (9) is necessary: it puts every nonzero group strictly below the
threshold `k-|S|` in (8).

Disconnected intersections can be handled separately.  A family is
**acyclic with slack `s`** if

\[
 \widetilde H_i(F_S;\mathbb Q)=0
 \quad\text{for } i\ge\max(1,s-|S|)
\]

for every nonempty intersection.  If every intersection of at least `t`
members has at most `q` connected components, Theorem 3 of
[Colin de Verdiere--Ginot--Goaoc](https://arxiv.org/abs/1101.6006) gives

\[
             h(M)\le q\bigl(\max(D,s,t)+1\bigr).       \tag{11}
\]

Their acyclic-family specialization `q(D+1)` is sharp for arbitrary open
families.  Formula (11) is the broadest established result used here; it
shows exactly how component complexity, rather than ambient dimension alone,
can enlarge a core.

In particular, if every nonempty intersection has at most `q` connected
components and each component is a rational homology cell, then

\[
                    h(M)\le q(D+1).                    \tag{12}
\]

At `(4,8)` this is `h(M)<=10q`; the connected acyclic case `q=1` proves the
headline conjecture.  This is a useful staged target when a diagonal test
fails: measure components and slack rather than abandoning the program.

One elementary localization is often more practical.  If regions
`X_1,...,X_L` cover `X` and the restricted feasibility family on `X_a` has
Helly number `h_a`, then

\[
                        h(M)\le\sum_a h_a.              \tag{13}
\]

For an empty intersection, choose at most `h_a` members that already exclude
`X_a`, then take their union.  Equation (13) allows a realization-space atlas
to be proved one simple region at a time.

## 6. An unconditional finite bound

No topology hypothesis is needed to prove that the hierarchy eventually
stops.  For `Y in X`, the derived arrangement has

\[
 q=\binom n{r-1}
\]

normal vectors `a_I(Y)` in `R^r`.  Its oriented-matroid type is determined by
the signs or zeros of its `binom(q,r)` maximal minors.  Let `tau(M)` be the
number of such derived types actually attained on `X`.  Then

\[
 \tau(M)\le 3^{\binom{\binom n{r-1}}r}.                \tag{14}
\]

The derived vectors do have rank `r`: if `B` is any parent basis, the `r`
normals `a_{B minus {b}}`, for `b in B`, form a scaled dual basis.  Hence their
maximal-minor sign vector determines the derived oriented matroid and its
topes.

Feasible extension signatures are constant on a derived type.  Hence each
`F_sigma` corresponds to a subset of the finite type set.

Let `c(M)` be the number of distinct chart-support sets

\[
       T(Y)\cap E(M)=\{\sigma\in E(M):Y\in F_\sigma\}
\]

actually attained as `Y` varies.  Several derived types may have the same
support, so `c(M)<=tau(M)`.

> **Finite-type Helly bound.**
> \[
>                  h(M)\le c(M)\le\tau(M).              \tag{15}
> \]

To prove (15), let
`Q={T(Y) intersection E(M):Y in X}` and, for each signature, put
`A_sigma={Q in Q:sigma in Q}`.  Then `F_S` is nonempty exactly when
`intersection_{sigma in S} A_sigma` is nonempty.  If `R` is a minimal
nonface, choose for each `sigma in R` a support
`Q_sigma in intersection_{tau in R minus {sigma}} A_tau`.  These supports are
distinct: equality of `Q_sigma` and `Q_tau` would produce a support lying in
every `A_rho`, including both omitted constraints.  Thus
`|R|<=|Q|=c<=tau`.

The explicit bound (14) is enormous.  Its role is logical: a finite arity
bound always exists.  Derived-type and homological complexity are two routes
to improving it; special combinatorial set-system structure is a third.

There is also a much smaller unconditional asymptotic bound.  Put
`s=binom(q,r)` and `delta=r(r-1)`.  The derived minors are `s` polynomials of
degree at most `delta` in `D` normalized coordinates.  Standard realizable
sign-condition bounds therefore give

\[
                   \tau(M)\le (\delta s)^{O(D)}.
\]

For fixed `D` and `delta`, the sharper bound is `O(s^D)`; see
[Basu--Pollack--Roy](https://arxiv.org/abs/math/0603256).  Their theorem bounds
the total number of connected components over all realizable sign conditions;
the number of sign conditions is no larger because each realized condition
has a component.  This remains huge at `(4,8)`, but it replaces the
exponential-in-`s` fallback (14) by a polynomial-in-`s` one for fixed
realization-space dimension.

## 7. Compatibility obstructions propagate

The nerve formulation also gives a clean inheritance theorem.  Choose an
ordered basis `B=(b_1,...,b_r)` and signs, and let `L_B(M)` be the corresponding
full-basis lexicographic extension by a new element `a`.  For every uniform
extension `sigma` of `M` by `p`, apply the same lexicographic rule to `sigma`
to obtain an extension `L_B(sigma)` on `E union {a,p}`.

> **Lexicographic nerve embedding.**  Before the dominance reduction, the map
> `sigma -> L_B(sigma)` identifies the full compatibility nerve of `M` with
> the induced complex on the lifted signatures inside the full nerve of
> `L_B(M)`.  Consequently
> \[
>        w(L_B(M))\ge w(M).                             \tag{16}
> \]

**Proof.**  Suppose `S` shares a chart `Y` over `M`, with feasible columns
`p_sigma`.  Choose

\[
 a=\epsilon_1y_{b_1}+\delta\epsilon_2y_{b_2}
      +\cdots+\delta^{r-1}\epsilon_ry_{b_r}
\]

with `delta>0` sufficiently small for the finitely many brackets involving
all `p_sigma`.  The same column `a` gives a chart of `L_B(M)`, and every
`p_sigma` realizes `L_B(sigma)` over it.  Conversely, delete `a` from any
common lifted chart to recover a common chart for `S`.  Thus a set is a face
before lifting exactly when its image is a face after lifting.  Restricting
any atlas coloring of the larger complex proves the width inequality; a
minimal nonface remains minimal in the full induced copy.  The latter statement
is deliberately not phrased using the dominance-reduced `h(M)`: a lifted
constraint could become dominated by a new extension of `L_B(M)`.  QED.

Iterating this construction propagates row 2599's width-seven lower bound to
realizable uniform rank-4 parents on every number of elements `n>=8`.  More
generally, any future atlas lower bound found here automatically generates an
infinite same-rank family, and every full-nerve core embeds along with it.  This
is why the catalog-sized test is not merely a fact about one row.

## 8. Why the conjecture was weakened this far

### Good covers are impossible for the unreduced family in general

It is tempting to conjecture that every `F_S` is contractible.  Uniform
rank-3 realization-space universality rules this out.  Realization spaces of
uniform oriented matroids of rank at least three can be stably equivalent to
arbitrary open semialgebraic varieties, and hence exhibit arbitrarily
complicated homotopy and homology; see, for example, the summary in
[Ruiz](https://arxiv.org/abs/1807.07552) and the rank-3 universal partition
theorem of [Guenzel](https://doi.org/10.1007/BF02717728).  If `M` has a
non-acyclic realization space, a full-basis lexicographic extension has
`F_sigma=X`, inheriting that topology.  The convex-fiber lemma gives the same
warning for partial extension realization spaces directly.

This is why dominated and universal vertices are removed and why (5), rather
than a global good-cover claim, is the proposed finite test.  Universality does
not by itself disprove (7): its gadgets increase `n` and therefore increase
`D`, and complicated topology of one cover member need not create a large
minimal nonface.  Nor does the universal-vertex example refute a good-cover or
diagonal statement on the dominance-reduced antichain `E(M)`.  That would
require a non-dominated common-deletion construction not presently known.

### Ambient dimension alone is insufficient for arbitrary families

Even in `X=(0,m) subset R`, let

\[
 F_i=\{x\in X:(x-i+1)(x-i)>0\},\qquad i=1,\ldots,m.
\]

The total intersection is empty, while deleting `F_i` leaves every point in
the interval `(i-1,i)`.  Thus these `m` open semialgebraic sets form a minimal
empty family.  Each is defined by one strict quadratic inequality, yet `m` is
arbitrary.  Any dimension-only proof of (7) must therefore use special
oriented-matroid extension structure; semialgebraicity alone cannot prove it.

The obstruction persists in exactly the shared/private LP format used by
extension feasibility.  Let `a=i-1`, `b=i`, give the `i`th constraint a private
variable `p=(u,v,s,t)`, and use the five rows

\[
\begin{split}
 r_1&=(1,0,0,0),\\
 r_2&=(-1,x-a,0,0),\\
 r_3&=(-1,x-b,0,0),\\
 r_4&=(0,0,1,0),\qquad r_5=(0,0,0,1).
\end{split}                                             \tag{17}
\]

Require `r_j(x) p>0` for all five rows.  The matrix is affine in the one shared
parameter `x`, has rank four everywhere, and every feasible private fiber is
an open convex cone.  Nevertheless its feasible base region is exactly

\[
                 F_i=(0,i-1)\cup(i,m).                  \tag{18}
\]

Indeed, for `a<x<b`, Gordan's alternative has the exact positive dependence

\[
       r_1+(b-x)r_2+(x-a)r_3=0;                         \tag{19}
\]

at the endpoints use `r_1+r_2=0` or `r_1+r_3=0`.  For `x<a`, take
`p=(epsilon,-1,1,1)` with `0<epsilon<a-x`; for `x>b`, take
`p=(epsilon,1,1,1)` with `0<epsilon<x-b`.  Thus (18) follows.  The regions are
proper and pairwise incomparable, their total intersection is empty, and
deleting region `i` leaves `(i-1,i)`.  Pointwise infeasibility even has a
Gordan circuit of support at most three.  Consequently a proof based only on
Caratheodory support size, affine parameter dependence, full column rank, or
convex private fibers cannot prove Extension--Helly.  It must use identities
special to the 56 normals derived from one `UOM(4,8)` parent.

### Core arity is not atlas width

A bound `h(M)<=10` says every minimal compatibility constraint has arity at
most ten.  It does not say ten, five, or any fixed number of colors suffices.
Graphs already have edge arity two and unbounded chromatic number; row 2599's
certified seven-chart lower bound is of exactly this kind.  Topology compresses
the constraint search, while coloring still determines the chart count.

If `K_R(M)` is shown to be rationally `D`-Leray, established fractional-Helly
and topological `(p,q)` machinery becomes available.  Density of small
compatible families gives one chart hitting a positive fraction.  A bounded
total piercing number, i.e. a constant chart upper bound, additionally needs
a `(p,q)` hypothesis.  That is a downstream theorem, not assumed here.

## 9. Exact falsification program

The recommended order minimizes expensive real algebraic work.

1. **Reduce dominance, then quotient symmetry.**  Keep one representative of
   every inclusion-minimal feasibility region.  Certifying a general
   inclusion `F_sigma subseteq F_tau` is itself a quantified semialgebraic
   problem and may be more expensive than the intended saving.  In practice,
   remove only certified antipodal equalities, lexicographic universal
   vertices, and other cheap implications; discover further dominance lazily.
   Work with automorphism orbits of subsets `S`.  Proving a Helly property on
   this unreduced superset is safe but stronger than necessary; a failure
   involving a still-dominated region is not yet a counterexample to the
   reduced conjecture.
2. **Abstract amalgamation gate.**  For prescribed extensions in `S`, add
   sign variables for brackets involving at least two new elements and impose
   every three-term Grassmann--Pluecker axiom.  A common real chart can be
   perturbed inside the product of its open extension cones so that every
   mixed-new bracket is nonzero.  Hence uniform-CNF unsatisfiability is a sound
   nonface verdict.  A proof-carrying run must also emit LRAT/DRAT, or a
   separately checkable exhaustive-search trace; the included pilot currently
   runs a deterministic exact DPLL search but emits no such proof artifact.  CNF
   satisfiability is only a necessary condition for a common real chart.
3. **Exact incidence feasibility.**  Use (2).  A rational or algebraic point
   proves `F_S` nonempty; a Positivstellensatz certificate proves it empty.
4. **Diagonal topology.**  Start with nine-fold `H_tilde_0`, then eight-fold
   `H_tilde_1`, and move up the table.  Triangulate `Z_S`, not the quantified
   projection `F_S`, and check exact boundary matrices.  Retain an exact
   sign-invariant cell decomposition, incidences, and the verified
   triangulation equivalence; boundary matrices alone are not end-to-end.
5. **Color only the bounded hypergraph.**  If (5) passes, all true edges have
   size at most ten.  If it fails, add the certified bad sets conservatively
   as described after the core dichotomy.  Certification requires either an
   exhaustive bad-set list or a separation loop: color, validate every color
   class, add the small nonface or homology witness returned by the dichotomy,
   and recolor until validation passes.

The included `search_higher_amalgam.py` implements step 2 for the 220 row-2599
signatures in the width-seven certificate.  It is a full-family sample, not a
dominance-reduced test.  A bounded recorded pilot found no higher-order
abstract obstruction among 100 triples, 25 quadruples, 10
quintuples, and 5 sextuples that avoided all 3,472 already-certified
incompatible pairs.  For example, triple
`(19,85,129)` satisfies all 6,930 rank-4 GP relations.  This is evidence only:
it tests abstract amalgamation, not real feasibility or (5).

First verify the input certificate, then reproduce the four recorded samples:

```bash
python ai/omreal/verify_seeat_width7.py
python ai/omreal/search_higher_amalgam.py --k 3 --tests 100 --seed 2599
python ai/omreal/search_higher_amalgam.py --k 4 --tests 25 --seed 2599
python ai/omreal/search_higher_amalgam.py --k 5 --tests 10 --seed 2599
python ai/omreal/search_higher_amalgam.py --k 6 --tests 5 --seed 2599
```

## 10. What would count as the breakthrough

There are three success levels, in increasing strength.

1. Prove `DEHC(4,8)`.  Then every `UOM(4,8)` atlas problem is exactly a
   hypergraph-coloring problem with edge arity at most ten; no larger core
   search is ever needed for this catalog.
2. Bound the defect `kappa(M)` uniformly over a natural class of parents.
   Equations (9)--(12) immediately convert that bound into a core-arity
   theorem, even when `DEHC` fails.
3. Prove a common-parent nerve universality theorem, or rule one out.  That
   would determine whether a dimension-only bound such as (7) can hold in
   arbitrary ranks.  Existing realization-space universality does not settle
   this missing common-deletion step.

The first is finitely falsifiable, and any produced witness is auditable; the
second is the useful general theorem; the third identifies the true
theoretical boundary.

## 11. A sharp conditional theorem from COM structure

There is now a precise combinatorial bridge which, if established for the
chart-support states, proves the conjecture with the desired constant.  Recall
that a complex of oriented matroids (COM) has a tope graph which is a partial
cube.  Knauer and Marc prove that these are exactly the **antipodally gated**
partial cubes: every antipodal convex subgraph has a gate from every outside
vertex.  They also identify COM rank with the largest cube obtainable by
contracting edge classes; see [their Theorem 1.1 and Lemma
4.2](https://arxiv.org/abs/1701.05525).

> **COM--Helly theorem.**  Let `C subseteq 2^E` be the tope set of a COM of
> rank at most `d`, encoding a positive sign by membership.  Form
> \[
>       K(C)=\{S\subseteq E:S\subseteq Q\text{ for some }Q\in C\}.
> \]
> Every minimal nonface of `K(C)` has size at most `d+1`.

**Proof.**  Let `R` be a minimal nonface of size `m`.  The case `m=1` is
immediate.  If `m=2`, its two singleton witnesses take opposite signs in each
restricted coordinate.  Strong elimination supplies a covector with zero in
one of them; deleting the other coordinate gives `{+,-,0}`, so the COM has
rank at least one and `m<=d+1`.  Assume `m>=3` and delete the
coordinates outside `R`.  For every `i in R`,
minimality supplies a tope positive on `R minus {i}`.  It must be negative at
`i`, since no tope is positive on all of `R`.  Reorient all coordinates.
The restricted tope system therefore contains every singleton `{i}` but not
the empty set.  To justify the latter carefully, undo the reorientation: an
all-negative tope after reorientation would be all-positive on `R` before it,
and composition with any original tope would extend it to an original tope
positive on all of `R`.  The restriction is simple: singleton patterns rule
out constants, and a third singleton rules out both parallel and antiparallel
coordinate pairs.  Deletion and reorientation preserve COMs.

We claim inductively that every nonempty proper subset `A` of `R` is a tope.
Singletons are present.  For two singletons `{a}` and `{b}`, partial-cube
isometry supplies a length-two cube path.  Its middle vertex is either the
missing empty set or `{a,b}`, so `{a,b}` is present.

Now let `3<=|A|<m`, assume all smaller nonempty subsets occur, and suppose `A`
does not.  The induced graph on

\[
                     2^A\setminus\{\varnothing,A\}
\]

is convex: a cube geodesic between two of its vertices fixes every coordinate
outside `A`, and the only other possible vertices are the two assumed missing
ones.  It is antipodal under `B mapsto A minus B`.  Hence it must be gated.
Choose `ell in R minus A`.  The outside vertex `{ell}` has every singleton
`{a}`, `a in A`, as a nearest vertex, all at distance two.  It has no unique
gate, a contradiction.  This proves the claim.

Fix `ell in R`.  Deleting coordinate `ell` now produces every vertex of the
cube on `R minus {ell}`: use tope `U` for a nonempty trace `U`, and `{ell}` for
the empty trace.  Thus the tope graph contracts to `Q_(m-1)`, so its COM rank
is at least `m-1`.  Therefore `m<=d+1`.  QED.

The bound is sharp: the lopsided COM with topes
`2^[d+1] minus {[d+1]}` has rank `d` and its full coordinate set is a minimal
nonface of size `d+1`.

The same bridge in fact has a stronger topological consequence.  A complex
is **integrally `d`-Leray** when every induced subcomplex has zero reduced
integral homology in dimensions `d` and above.

> **COM--Leray theorem.**  If `C` is the tope family of a COM of rank at most
> `d`, then `K(C)` is integrally `d`-Leray.

**Proof.**  Deleting coordinates preserves COMs and does not increase rank,
and

\[
                 K(C)[A]=K(C\mathbin{\backslash}(E\setminus A)).
\]

It is therefore enough to prove the homology vanishing for `K(C)` itself.
Let `L` be the covector system of the COM.  Bandelt--Chepoi--Knauer construct
from `L` a contractible regular cell complex `Delta(L)`; see their Proposition
15 and the preceding cell construction in
[COMs: Complexes of Oriented Matroids](https://arxiv.org/abs/1507.06111).
Every cell in that construction is the ball associated with an oriented-
matroid face of `L`, and its dimension is the rank of that face.  A face cannot
have rank above `rank(L)<=d`, so `dim Delta(L)<=d`.

For a coordinate `e`, let `Delta_e^+` be the cell subcomplex belonging to the
positive topal fiber `L_e^+={X in L:X_e=+}`.  More generally, every nonempty
intersection

\[
           \bigcap_{e\in S}\Delta_e^+
\]

is the cell complex of the fixed-positive fiber `L_S^+`.  Fibers of a COM are
COMs (their Lemma 4), so Proposition 15 makes every such intersection
contractible.  These really are cell subcomplexes: if a covector is positive
on `S`, its entire COM face preserves those fixed nonzero signs.  The
intersection is nonempty exactly when some tope is positive on `S`: a
covector positive on `S` can be composed with any tope to obtain such a tope.
Hence the nerve of `{Delta_e^+:e in E}` is exactly `K(C)`.  The nerve theorem
gives

\[
              K(C)\simeq U:=\bigcup_{e\in E}\Delta_e^+.
\]

The union `U` is a subcomplex of the contractible `d`-dimensional complex
`Delta(L)`.  It has no cells above dimension `d`.  Moreover a cellular
`d`-cycle in `U` is a `d`-cycle in `Delta(L)`; the latter has zero `H_d` and
no `(d+1)`-chains, so that cycle is zero.  Thus
`H_tilde_i(U;Z)=0` for every `i>=d`.  Applying the same argument after every
coordinate deletion proves the induced-subcomplex assertion.  QED.

The COM--Helly theorem follows again by applying this to the boundary sphere
induced by a minimal nonface.  The Leray conclusion is strictly more
informative: `FCC_9(M)` would force the full compatibility complex to be
integrally `9`-Leray, not merely to have cores of size at most ten.

For a parent `M`, define the complete support-state class

\[
 \mathcal Q(M)=\{T(Y)\cap E(M):Y\in\mathcal R(M)\}.     \tag{20}
\]

There is an exact compound-Grassmannian description of (20), valid in every
rank.  Let the rows of an `r by n` realization matrix `Y` be
`v_1,...,v_r`, let `V=row(Y)`, and, for `p=(p_1,...,p_r)`, set

\[
 q_Y(p)=\sum_{j=1}^r(-1)^{j+r}p_j
 v_1\wedge\cdots\wedge\widehat v_j\wedge\cdots\wedge v_r
 \in\bigwedge^{r-1}V.                                  \tag{21}
\]

The `I={i_1<...<i_(r-1)}` coordinate of (21) is

\[
 \sum_j(-1)^{j+r}p_j\det Y_{[r]\setminus j,I}
   =\det(y_{i_1},...,y_{i_{r-1}},p)                    \tag{22}
\]

by Laplace expansion.  The `r` omitted-row wedges form a basis of
`wedge^(r-1) V`, so `q_Y` is a linear isomorphism.  If `O_sigma` denotes the
open coordinate orthant prescribed by an extension signature, then

\[
 F_\sigma=\{Y\in\mathcal R(M):
       \bigwedge^{r-1}\operatorname{row}(Y)\cap O_\sigma
       \ne\varnothing\}.                                  \tag{23}
\]

Positive column rescaling acts by positive coordinate rescaling on the wedge,
so (23) is well-defined on normalized projective realization space.  For a
family `S`, the incidence space (2) is exactly the space of `Y` (with
`V=row(Y)`) together with
independently chosen points
`q_sigma in wedge^(r-1)V intersection O_sigma`.  This
removes the private columns from the formulation without changing their
convex fibers.  At `(4,8)`, Extension--Helly is therefore a Helly statement
for open-orthant hits by the third-compound four-plane `wedge^3 V` as `V`
varies over the nine-dimensional positive-diagonal quotient (equivalently,
a projective-frame slice) of one oriented Grassmannian stratum.

Derived-degenerate realizations may be included in (20) without changing the
compatibility complex: any finite set of uniform extensions feasible at a
degenerate `Y` remains feasible after a sufficiently small generic
perturbation, because all of its determinant inequalities are strict.  The
COM--Helly theorem proves Extension--Helly if `Q(M)` is the tope set of a COM
of rank at most nine.  Equivalently, after the usual COM simplification of
constant, parallel, and antiparallel coordinates, its one-inclusion graph
must be an antipodally gated partial cube with no cube contraction above
dimension nine.

This last sentence is a **reduction, not a proved property of (20)**.  A local
derived mutation, even with its degenerate bridge state, does not establish
global partial-cube distances or gatedness; nor does a nine-dimensional
parameterization by itself bound VC/COM rank.  These are now the exact two
claims a COM proof must establish or falsify.

The standard realizable-COM construction does not fill this gap.  It starts
with a fixed hyperplane arrangement restricted to an open convex set; see
[Bandelt--Chepoi--Knauer](https://arxiv.org/abs/1507.06111).  Here both the
adjoint arrangement and its topes vary with `Y`, and
[Falk](https://doi.org/10.1090/S0002-9939-1994-1209098-1) shows that even the
intersection lattice and complement topology of a discriminantal arrangement
can depend on the chosen realization.  Commuting this variation with the
inverse-locus quantifier in (20) is precisely the new work required.
[Sturmfels--Ziegler's](https://doi.org/10.1007/BF02573961) connectedness of the
poset of realizable one-element extensions does not commute it: that theorem
varies the extension over a fixed abstract parent, whereas (20) fixes several
extension signatures and varies the common parent realization.

## 12. Exact derived-wall classification and one-wall regularity

The local geometry needed by that bridge can be settled completely.  For a
uniform ordered configuration `Y=(y_1,...,y_8)` in `R^4`, put

\[
 a_I(v)=\det(y_i,y_j,y_k,v),\qquad I=\{i,j,k\},
\]

and for four distinct triples `E={I_1,...,I_4}` put

\[
                 D_E(Y)=\det(a_{I_1},...,a_{I_4}).      \tag{24}
\]

> **Derived-wall theorem.**  Up to relabeling the eight parent elements and
> permuting the four triples, there are exactly 52 incidence types in (24).
> Fourteen are identically zero: exactly those in which all four triples share
> a label or some three triples share a pair.  On the uniform locus, 25 more
> are everywhere nonzero because `D_E` is, up to sign, a monomial in parent
> brackets.  The remaining 13 have a genuine nonconstant residual factor.
>
> If `D_E` is not identically zero, then at every uniform `Y` with `D_E(Y)=0`
> the four normals have rank exactly three and `dD_E|_Y` is nonzero.  Hence
> every genuine derived wall is a smooth cooriented hypersurface in every
> normalized `UOM(4,8)` realization cell.

The finite classification is independently reproducible with
[`verify_derived_walls.py`](verify_derived_walls.py).  It exhausts all
`binom(56,4)=367,290` four-sets, obtains the 52 orbits from a complete incidence
invariant, and verifies all bracket factorizations in exact symbolic
arithmetic.  It finds `14+25+13=52`; no sampling or floating point is used.

Here is the exact proof.  The two structural patterns vanish for elementary
linear-algebra reasons.  If all four triples contain `e`, their normals lie in
the three-space annihilating `y_e`.  If three contain `{e,f}`, those three
normals lie in the two-space annihilating `span(y_e,y_f)`.

For the converse and the counts, every uniform configuration can, after the
same relabeling used for an orbit representative, be normalized to

\[
 Y=[e_1,e_2,e_3,e_4,(1,1,1,1),(1,a,b,c),
                    (1,d,e,f),(1,g,h,i)].              \tag{25}
\]

All divisions used here are by parent brackets, hence are valid on the
uniform locus.  The exact checker enumerates the 52 incidence orbits and
expands (24) in the nine variables in (25).  The fourteen structural types
are exactly the zero polynomials.  Each of the 25 fixed types is a signed
parent-bracket monomial.  Every other type has

\[
                         D_E=\pm M_E q_E,               \tag{26}
\]

where `M_E` is a parent-bracket monomial and `q_E` is an irreducible residual
coprime to every parent bracket.  The checker additionally verifies the
following pivot derivatives, up to sign:

| residual orbit | pivot derivative |
|---:|---|
| 36 | `partial_a q = [1237]` |
| 37 | `partial_a q = [1257]` |
| 38 | `partial_a q = [1278]` |
| 39 | `partial_a q = [2378]` |
| 41 | `partial_a q = [2457]` |
| 42 | `partial_a q = [2478]` |
| 44 | `partial_d q = [2356][1258]` |
| 46, 47 | `partial_a q = [1237]` |
| 48 | `partial_a q = 1` |
| 49 | `partial_d q = 1` |
| 50 | `partial_d q = [1238]` |
| 51 | `partial_f q = [2468][1456]` |

Every entry in the right column is nonzero on the uniform locus.  At a zero
of (26), `q_E=0`, and therefore

\[
                  dD_E=\pm M_E\,dq_E\ne0.              \tag{27}
\]

This proves regularity in the normalized realization space directly.  It
also proves that the four normals have rank exactly three: at rank at most
two every three-by-three cofactor of their four-by-four matrix vanishes, so
the differential of its determinant, and hence its pullback `dD_E`, would be
zero.  The regular-value theorem now gives a smooth cooriented hypersurface.
QED.

This theorem settles one wall only.  Smooth hypersurfaces can still have
disconnected sign regions and topologically complicated multiple
intersections; the affine LP family (17)--(19) already demonstrates that
smooth walls plus convex private fibers are insufficient.  The remaining
Extension--Helly problem is therefore genuinely the global COM/gatedness or
diagonal-homology step, not a hidden singular-wall issue.  The known
smoothness of complex rank-four realization spaces through nine elements
([Corey--Luber, Theorem 1.3](https://arxiv.org/abs/2307.11915)) does not supply
that step: smooth real loci and their open sign regions can still be
disconnected or carry homology.

## 13. A finite COM target, and its limitation

Even perfect simultaneous-wall topology would not by itself close the gap.
Take the LP family (17)--(19) and replace its base by
`(0,m) times R^8`.  Its distinct internal walls are parallel affine
hyperplanes in a convex nine-manifold and give a regular pseudohyperplane cell
decomposition.  Nevertheless

\[
 F_i=((0,i-1)\mathbin\cup(i,m))\times\mathbb R^8
\]

has an arbitrarily large minimal empty family.  Thus normal crossings,
regular-CW structure, or Alexander duality applied only to the derived walls
cannot prove Extension--Helly.  A proof must also control how extension
feasibility labels the wall chambers.  Naive codimension counting already
fails inside the exact classification: residual types 46 and 47 have the same
factor

\[
 q=af-bf-cd+ce,
\]

although their full determinants are respectively, up to sign,
`[1246]q` and `[1248]q`.

The raw support-state class (20) need not itself be proved to be a COM.  The
following strictly weaker completion property is sufficient.

> **Feasible COM Completion, `FCC_9(M)`.**  There is a rank-at-most-nine COM
> tope family `C_M`, on the dominance-reduced extension coordinates, such
> that
> \[
>       C_M\subseteq K_{\mathbb R}(M)
> \]
> and `C_M` contains every maximal face of `K_R(M)`.

> **COM-completion implication.**  If `FCC_9(M)` holds, then `K_R(M)` is
> integrally `9`-Leray and, in particular, `h(M)<=10`.

**Proof.**  Because every member of `C_M` is a feasible face and
`K_R(M)` is downward closed,
`K(C_M) subseteq K_R(M)`.  Conversely, every face of the finite complex
`K_R(M)` is contained in a maximal face, and every maximal face is a member
of `C_M`.  Hence `K_R(M) subseteq K(C_M)`.  The two complexes are equal, so
the COM--Leray theorem with `d=9` gives the claim.  QED.

The resulting implication chain locates the more economical topological
target:

\[
 \mathrm{FCC}_9(M)
 \Longrightarrow K_{\mathbb R}(M)\text{ integrally 9-Leray}
 \Longrightarrow K_{\mathbb R}(M)\text{ rationally 9-Leray}
 \Longrightarrow h(M)\le10.                            \tag{28}
\]

Only the last conclusion is needed for ten-locality.  Thus the full homology
tail (8) with `k=9`, which proves the rational-Leray middle statement, is a
weaker direct target than constructing a COM completion.  No reverse arrow
in (28) is being assumed.

For any finite simplicial complex `K`, call the minimum possible rank in this
kind of completion `cr_COM(K)`.  Such a completion always exists: view the
whole down-set `K` as a set family.  A coordinate set `A` is shattered by
this family exactly when `A in K`.  Indeed, membership gives all traces by
downward closure, while shattering gives a member of `K` containing `A` and
hence `A in K`.  Thus `K` is an ample (lopsided) set system, hence the tope
family of a COM, of rank `max{|Q|:Q in K}`.  Together with the proof just
given and the COM--Leray theorem, this shows

\[
 \max\bigl(\ell_{\mathbb Z}(K),
            \operatorname{VCdim}(\operatorname{Facets}(K))\bigr)
 \le \operatorname{cr}_{\rm COM}(K)
 \le \max_{Q\in K}|Q|.                                 \tag{29}
\]

Here `ell_Z(K)` is the least `d` for which `K` is integrally `d`-Leray; in
particular `h(K)-1<=ell_Z(K)`.  The second lower bound holds because every
completion contains every facet, and adding topes cannot destroy a shattered
set.  Thus `FCC_9(M)` is precisely a rank-compression claim for the canonical
ample completion `K_R(M)`.  The reverse control by Helly number fails
completely: completion rank can exceed it by an arbitrarily large amount.

> **Cross-polytope gap theorem.**  For every `m>=1` there is a simplicial
> complex `K_m` with
> \[
>       h(K_m)=2,\qquad \operatorname{cr}_{\rm COM}(K_m)=m.       \tag{30}
> \]

**Proof.**  On the `2m` coordinates
`{x_i^0,x_i^1:1<=i<=m}`, let `K_m` consist of the sets containing at most one
member of every pair `{x_i^0,x_i^1}`.  Its minimal nonfaces are exactly those
`m` pairs.  Its maximal faces are

\[
 F_\epsilon=\{x_i^{\epsilon_i}:1\le i\le m\},
 \qquad \epsilon\in\{0,1\}^m.                         \tag{31}
\]

Put `X={x_1^1,...,x_m^1}`.  The traces `F_epsilon intersection X`, as
`epsilon` varies, are all `2^m` subsets of `X`.  Hence any `C` containing all
the maximal faces shatters `X`.  COM rank equals the VC dimension of its tope
family, so `rank(C)>=m`; see
[Knauer--Marc](https://arxiv.org/abs/1701.05525).  Conversely,
the family of all `F_epsilon` is the tope family of the rank-`m` oriented
matroid obtained from the `m` coordinate hyperplanes by replacing each
element with an antiparallel copy.  Its downward closure is exactly `K_m`.
Thus its rank gives the matching upper bound in (30).  Topologically, `K_m`
is the boundary of the `m`-dimensional cross-polytope, so
`ell_Z(K_m)=m`; the COM--Leray lower bound is sharp here as well.  QED.

The VC lower bound in (29) is independent of that homology obstruction.  In
fact, even integral `1`-Lerayness and pairwise minimal nonfaces do not bound
COM-completion rank.

> **Split-graph gap theorem.**  For every `m>=1` there is a flag simplicial
> complex `J_m` such that
> \[
>   h(J_m)=2,\qquad \ell_{\mathbb Z}(J_m)=1,\qquad
>   \operatorname{cr}_{\rm COM}(J_m)=m.                 \tag{32}
> \]

**Proof.**  Let `X={x_1,...,x_m}` be a clique.  For every `P subseteq X`, add
an independent vertex `y_P` adjacent exactly to the vertices of `P`, and let
`J_m` be the clique complex of the resulting split graph.  Its facets are

\[
                       P\mathbin{\cup}\{y_P\},\qquad P\subseteq X.
\]

Their traces on `X` are all subsets of `X`, so (29) gives
`cr_COM(J_m)>=m`.  The graph is chordal: an induced cycle of length at least
four would contain two nonconsecutive clique vertices, hence a chord.  Every
induced subgraph is again chordal, and the clique complex of each connected
chordal graph collapses along a perfect-elimination ordering.  Thus every
induced subcomplex of `J_m` has zero reduced homology in dimensions at least
one.  Since `J_m` has nonedges, `ell_Z(J_m)=1`; flagness also gives `h(J_m)=2`.

For the matching upper bound, take the concept family

\[
   C_m=2^X\mathbin{\cup}
       \{P\mathbin{\cup}\{y_P\}:P\subseteq X\}.
\]

Its one-inclusion graph `G_m` is the `m`-cube on `2^X` with one private
pendant edge attached at every cube vertex.  Distances in this graph equal
Hamming distances between the displayed concepts, so `G_m` is a partial
cube.  We verify the antipodally gated condition.  Suppose an antipodal convex
subgraph `A` contains a pendant vertex `z` with cube neighbor `p`.  A singleton
is gated, so assume `A` has another vertex; convexity then puts `p` in `A`.  If
`A` contains anything beyond the edge `zp`, then the interval from `z` to its
antipode contains `p`.  But an interval from `p` can contain the leaf `z` only
when its other endpoint is `z`; consequently `p` cannot have an antipode whose
interval is all of `A`, a contradiction.  Thus `A` is a singleton or `zp`.
Any antipodal convex subgraph avoiding the leaves is a convex subgraph of a
cube, hence a subcube.  Singletons, the edge `zp`, and every subcube are gated
in `G_m`: for a vertex of the cube use ordinary coordinate projection, and
for a pendant vertex first pass to its cube neighbor.  Therefore `G_m` is
antipodally gated.  By
[Knauer--Marc's characterization](https://arxiv.org/abs/1701.05525), `C_m` is
the tope family of a COM.

It shatters `X`, but it cannot shatter `m+1` coordinates.  A set of that size
must contain a `y`-coordinate; no concept contains two of them, and only one
concept contains any fixed `y_P`, so the required traces cannot all occur.
Its COM rank is therefore `m`.  Finally,
`C_m subseteq J_m` and it contains every facet, proving the upper bound in
(32).  QED.

Thus `FCC_9(M)` is a high-risk special-structure conjecture, not a reformulation
of Extension--Helly and not the weakest possible remaining lemma.  A necessary
falsification gate is immediate: if the maximal feasible supports of one
parent shatter ten dominance-reduced extension coordinates, then `FCC_9(M)`
is false even though the ten-local Helly conjecture may still hold.

An exact row-2599 experiment distinguishes maximal faces from raw chart
supports.  Eight realizable extension signatures were selected, and one exact
integer parent chart was found for every one of their `2^8=256` support
patterns.  For each supported bit the certificate contains an integer point
in the corresponding strict extension cone.  For each unsupported bit it
contains nonnegative integer Gordan weights annihilating the signed derived
normals.  Thus the **raw chart-support concept class** has VC dimension at
least eight.

This does *not* prove that the facets of `K_R(M)` shatter those coordinates,
and therefore does not lower-bound `cr_COM(K_R(M))`: a feasible COM completion
may omit intermediate chart-support states and retain only maximal faces.
The distinction corrects the tempting but invalid inference from a shattered
sample of charts to a lower bound for every completion.  The exact result is
still a useful proof boundary: the raw support states cannot themselves be a
COM of rank at most seven.

```console
python ai/omreal/verify_seeat_shatter8.py
```

A second exact row-2599 certificate rules out a more geometric shortcut.
Delete parent element 1 and fix the other seven columns.  There are two
integer positions `u,v` of the deleted column that both realize `M` and both
support one fixed extension signature.  The vector midpoint `u+v` still
realizes `M`, but the signed derived normals there have a positive Gordan
dependence.  Hence that extension is infeasible at the midpoint.

> **Residence nonconvexity proposition.**  Even for a fixed realizable
> `UOM(4,7)` deletion, an extension-feasibility region inside the convex
> three-dimensional residence fiber of the eighth parent element need not be
> convex.

```console
python ai/omreal/verify_seeat_residence_nonconvex.py
```

Consequently the attractive decomposition `9=6+3` does not turn the desired
bound into ordinary convex Helly on a six-dimensional deletion base and a
three-dimensional residence fiber.  Strong Euclideanness of the abstract
seven-element deletion does not repair this missing real-geometric
convexity.  Any deletion-based proof must control the topology of these
nonconvex fiber regions rather than assume it away.

Only maximal **generic** support states are needed to test `FCC_9(M)`.  If
`Y` lies on a derived wall, choose one strict-inequality witness column for
each signature in its finite support `T(Y) intersection E(M)`.  All those
inequalities persist under one sufficiently small perturbation of `Y`.
The perturbation may also be chosen off every non-identically-zero derived
wall.  Therefore `T(Y)` is contained in a generic support state, and a maximal
face cannot occur only on a degenerate stratum.

This gives a finite COM-completion problem rather than a simultaneous-wall
topology problem: enumerate maximal generic supports, add only certified
feasible subfaces needed as Hamming bridges, check that the resulting
one-inclusion graph is an antipodally gated partial cube, and check that its
COM rank is at most nine.  Failure of the *raw* support graph to be a COM would
not refute this completion target.

There is also a sharp warning against moving the argument to the whole
ambient Grassmannian.  For an open coordinate orthant `O subset R^N`, put

\[
 A_O=\{L\in\operatorname{Gr}_{\mathbb R}(k,N):L\cap O\ne\varnothing\}.
\]

Then

\[
             A_O\simeq\operatorname{Gr}_{\mathbb R}(k-1,N-1).    \tag{33}
\]

Indeed, use the incidence space of pairs `(L,[v])` with `[v] in P(O)` and
`[v] subset L`.  Projection to the open simplex `P(O)` has fiber
`Gr_R(k-1,N-1)`.  Projection to `A_O` has a nonempty open convex-polytope
fiber; a continuous analytic-center section and straight-line contraction
make it a homotopy equivalence.  At `(k,N)=(4,56)`, the ambient orthant locus
therefore has the homotopy type of `Gr_R(3,55)`, not of a cell.  Any acyclicity
proof must use the special third-compound pullback (23) and the fixed parent
realization chamber.  An ambient compatible affine chart does make `A_O`
star-shaped: on `L=row[I_k|B]`, put
`(B_0)_(ij)=sigma_i sigma_(k+j)`; if `p` witnesses `B`, the same `p` witnesses
`(1-t)B+tB_0`.  This straight-line contraction generally leaves the
third-compound image, however.  An intrinsic compound-chart lifting theorem
would be a different sufficient bridge.
