# Extension-atlas Helly theory

**Status.**  This note separates one finite conjecture from several unconditional
theorems.  The conjecture is deliberately catalog-sized: it concerns all
2,604 realizable `UOM(4,8)` reorientation classes, not only parent row 2599.
The first of its nine diagonal entries is now a theorem, integrally; the other
eight entries and the resulting ten-locality statement remain conjectural.
Two proof shortcuts that would have made the remaining entries nearly
formal are now ruled out below: neither convex private LP fibers nor sparse
Gordan circuits impose a dimension-only Helly bound, and smooth individual
derived walls do not control their multiple intersections.  On the positive
side, Section 4.5 reduces the ninth diagonal exactly to connectivity in a
finite labeled master-chamber graph.  Section 11 proves a sharp COM--Helly
theorem and its stronger integral
COM--Leray form, reducing the desired bound to one precise support-state
property, while Section 12 gives an exact classification, a regularity
theorem, and a global one-sidedness certificate for every possible derived
wall.
Section 13 isolates a finite feasible-COM completion target, proves that wall
topology alone cannot close it, and shows that the completion target is a
strictly stronger high-risk conjecture rather than an equivalent reformulation.
It also records exact row-2599 certificates for an eight-coordinate raw
support cube and for nonconvexity inside one contraction-height fiber; both
results sharpen the proof boundary without settling the conjecture.
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

| number of extensions in `S` | group whose nonvanishing witnesses topology |
|---:|---:|
| 1 | `H_tilde_8(F_S; Q)` -- **vanishes integrally (proved below)** |
| 2 | `H_tilde_7(F_S; Q)` |
| 3 | `H_tilde_6(F_S; Q)` |
| 4 | `H_tilde_5(F_S; Q)` |
| 5 | `H_tilde_4(F_S; Q)` |
| 6 | `H_tilde_3(F_S; Q)` |
| 7 | `H_tilde_2(F_S; Q)` |
| 8 | `H_tilde_1(F_S; Q)` |
| 9 | `H_tilde_0(F_S; Q)` (disconnectedness) |

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

For proof planning, (5) is the **Nine-Diagonal Vanishing Lemma (9DVL)**.  One
of its nine entries is the theorem in Section 4.1; "lemma" remains aspirational
for the other eight entries displayed in the table in Section 3.  It is the
weakest currently isolated topological bridge to the named 8--9--10 theorem,
whereas `FCC_9` would prove the stronger integral Leray statement.

This strengthening is intentionally quantified over every internal antichain
of proper regions, not only globally minimal regions from `E(M)`.  Therefore
a falsifier for (5) need certify only properness and pairwise incomparability;
a falsifier for the reduced core conjecture must certify membership in `E(M)`.

The core dichotomy proves `DEHC(4,8)` implies the Extension-Helly Conjecture.
The converse need not hold: (5) is a deliberately stronger, independently
certifiable target.

### 4.1 The first diagonal entry

The single-signature case admits a uniform contraction argument.  The useful
statement is slightly more general.

> **Contraction--height theorem.**  Let `N` be a realizable uniform oriented
> matroid of rank `r>=2` on `n>=r+1` elements, and let `e` be an element of
> `N`.  Then
> its normalized realization space is homotopy equivalent to an open
> semialgebraic subset of
> \[
>       \mathbb R^{(r-2)(n-r-1)}.
> \]
> Consequently
> \[
>   \widetilde H_i(\mathcal R(N);\mathbb Z)=0
>       \qquad\text{for }i\ge (r-2)(n-r-1).             \tag{5a}
> \]

**Proof.**  Put `A=N/e`.  Choose a projective frame compatible with the
contraction, put the column `e` in the last coordinate direction, and normalize
the projected frame in the quotient.  A realization of `N` over a normalized
realization `a` of `A` is then determined by the remaining lift heights `h`.
Every bracket containing `e` already has the sign prescribed by `A`.  Expanding
a bracket not containing `e` along its height row gives

\[
 \det(v_{i_1},\ldots,v_{i_r})
 =\sum_{q=1}^r(-1)^{r+q}h_{i_q}
       \det(a_{I\setminus i_q}).                       \tag{5b}
\]

Thus, for fixed `a`, the normalized lift fiber is a possibly empty open convex
polyhedron in the height variables; it is nonempty precisely over its
nonempty-fiber locus `G_e(N)`.  This locus is semialgebraic by
Tarski--Seidenberg and open in `R(A)`: one strict feasible lift persists under
a sufficiently small change of `a`.

These convex fibers give a homotopy equivalence, not merely an acyclic map.
Locally persistent lifts cover `G_e(N)`; a partition of unity and convex
combination produce a continuous section, and straight-line motion in every
fiber retracts the realization space onto its graph.  Hence

\[
                  \mathcal R(N)\simeq G_e(N).          \tag{5c}
\]

Uniformity makes `A` a uniform rank-`r-1` matroid on `n-1` elements.  A fixed
projective-frame slice identifies `R(A)` with an open subset of
`R^((r-2)(n-r-1))`, and the same is true of `G_e(N)`.  Homology above that
dimension vanishes.  In the top dimension it also vanishes: every component
of a nonempty open subset of Euclidean `d`-space is a noncompact orientable
`d`-manifold, so its ordinary integral `H_d` is zero.  (For `d=0`, use reduced
`H_0` directly.)  This proves (5a).  QED.

> **First diagonal theorem.**  For every realizable `UOM(4,8)` parent `M` and
> every realizable uniform extension signature `sigma`,
> \[
>                 \widetilde H_8(F_\sigma;\mathbb Z)=0. \tag{5d}
> \]
> Properness is not required.

Indeed, let `N=M\cup p` be the oriented matroid specified by `sigma`.  The
convex-fiber lemma identifies `F_sigma` with `R(N)` up to the contractible
positive column-scaling factors needed to pass between the parent-frame
incidence slice and the chosen normalization of `R(N)`.  Apply (5a) with
`(r,n)=(4,9)` and `e=p`; the contraction `N/p` has rank three on eight
elements and the Euclidean bound in (5a) is `(4-2)(9-4-1)=8`.  This proves
(5d), and hence the `|S|=1` entry of (5), over the integers.

The same construction has an exact joint form, although its dimension bound
explains why one contraction proves no later diagonal.  Fix a parent label
`e` and let `s=|S|`.  After contraction, retain a normalized realization of
`M/e` and, for each `sigma in S`, the projective quotient point `q_sigma`
whose pair signs are the brackets of `sigma` containing `e`.  This partial
contraction incidence space `W_(S,e)` is open semialgebraic in
`R^(6+2s)`: the rank-three parent contributes six coordinates and every
projective quotient point contributes two.

For a fixed point of `W_(S,e)`, all remaining parent and extension brackets
are affine-linear inequalities in the lift heights, by the same expansion
(5b).  Their nonempty-fiber locus `G_(S,e)` is open, and the height fiber is
an open convex polyhedron.  The section argument therefore gives

\[
              F_S\simeq G_{S,e}\subset W_{S,e},\qquad
 \widetilde H_i(F_S;\mathbb Z)=0\quad(i\ge6+2s).       \tag{5d'}
\]

For `s=1`, (5d') recovers the same dimension-eight bound as the proof above.
For `s>=2` it is weaker than the ambient nine-dimensional bound.  A literal
second contraction would formally lower `6+2s` to `3+s`, but its two height
rows enter the remaining prescribed brackets bilinearly, so the joint lift
fiber is no longer covered by the convexity argument.  Alternatively, one
might project away the second quotient point in order to keep the base small.
The exact example in Section 13 shows that its feasibility condition then
becomes nonconvex inside the first contraction-height fiber, even for a proper
incomparable pair.

There is a limited exact substitute.  Over a fixed literal double-contraction
base, fix one of the two normalized height rows.  Every remaining inequality
is affine-linear in the other row, so its nonempty fiber is an open convex
polyhedron.  The section argument makes the full lift fiber homotopy equivalent
to an open subset of `R^5`; consequently its integral homology vanishes in
degrees at least five.  This still leaves the total-degree-seven Leray terms with
bidegrees `(3,4),(4,3),(5,2)`, and the projection is nonproper.

The row-2599 nonconvexity certificate also upgrades to a literal
double-contraction regression test.  Along one exact affine height line the
rank-two quotient is constant, the second signature is feasible at both
ends, and a positive five-row Gordan circuit persists on the entire middle
interval `[1/2,3/2]`.  Thus the projected feasibility locus has a disconnected
line slice.  The second extension quotient point is forgotten in this
projection, so this does not make the full double-lift fiber disconnected;
it rules out only linewise or cellwise acyclicity shortcuts.  See
[`DOUBLE_CONTRACTION_FIBERS.md`](DOUBLE_CONTRACTION_FIBERS.md) and
[`verify_double_contraction_gap.py`](verify_double_contraction_gap.py).

The one-row Gordan system has one further exact structural bound.  In its
six-dimensional homogeneous height space, a minimal circuit involving only
bilinear rows has at most six members.  Pairing a dependence with the first
height row shows that exactly one contracted-column constant row is
impossible; every seven-row circuit therefore contains at least two constant
rows.  This does not force an escape.  An honest uniform parent with two
realizable private extensions has an allowed seven-row minimal positive
circuit whose alternating five-form pencil has determinant 9.  Its
fixed-weight height is unique, disproving a universal Koszul-kernel motion.
The safe remaining Leray route must prove relative `H_c^(0,1,2)` vanishing
with Hardt/exit specialization control.  See
[`DIAG2_PIVOT_DOUBLE_FIBER_KOSZUL.md`](DIAG2_PIVOT_DOUBLE_FIBER_KOSZUL.md).

### 4.2 Dual bad-locus form of the remaining entries

Put `B_sigma=X minus F_sigma` and `B_S=union_(sigma in S) B_sigma`.  These
are closed relative to the oriented nine-manifold `X`.  Poincare duality with
supports and the homology sequence of `(X,F_S)` give the exact segment

\[
 H_{10-s}(X;\mathbb Q)\longrightarrow
 H_c^{s-1}(B_S;\mathbb Q)\longrightarrow
 H_{9-s}(F_S;\mathbb Q)\longrightarrow
 H_{9-s}(X;\mathbb Q),                                \tag{5e}
\]

where `s=|S|`.

We now import one published small-ground-set result.  Tsukamoto first defines
`R_GL(M)` for arbitrary rank and ground-set size as the quotient of realizing
matrices by `GL(r,R)` [Definition 1.2], and then states that every realizable
oriented matroid on fewer than nine elements has contractible realization space
([Tsukamoto 2013, p. 288](https://doi.org/10.1007/s00454-012-9456-y)).  Hence
`R_GL(M)` is contractible for every parent considered here.

This is the right result despite the slightly different normalization.  The
positive column torus acts on the \(GL\) quotient.  Its diagonal subgroup is
already the scalar subgroup of \(GL(r,\mathbb R)\), so the effective free
action is by

\[
 T=(\mathbb R_{>0})^n/\mathbb R_{>0,\mathrm{diag}}
   \cong(\mathbb R_{>0})^{n-1}.
\]

The quotient by \(T\) is the projective realization space.  The fixed labeled
projective-frame normalization supplies a global section: use its basis
columns to fix the \(GL\) gauge, then use diagonal \(GL\) together with
positive rescalings of the basis columns and the extra frame column to put
that column at its prescribed sign vector; finally normalize one nonzero
coordinate of each remaining column.  Uniformity makes every normalization
denominator nonzero.  Hence the torus bundle is globally trivial, and the
slice used here gives

\[
        \mathcal R_{GL}(M)\cong
        X\times(\mathbb R_{>0})^{\,n-1}
        =X\times(\mathbb R_{>0})^7.                    \tag{5e'}
\]

In particular, the extra positive column-length factors are contractible and
`X` is contractible.  For `1<=s<=8`, both outside terms in (5e) therefore
vanish.  For `s=9`, the relevant end of the same long exact sequence is

\[
 0=H_1(X)\longrightarrow H_c^8(B_S)\longrightarrow H_0(F_S)
       \longrightarrow H_0(X)=\mathbb Q.
\]

The last map sends every component of `F_S` to the unique component of `X`,
so its kernel is precisely reduced `H_0` (also when `F_S` is empty).  Consequently
all nine diagonal targets have the uniform bad-locus form

\[
 \boxed{\quad
 \widetilde H_{9-s}(F_S;\mathbb Q)
       \cong H_c^{s-1}(B_S;\mathbb Q),\qquad 1\le s\le9.
 \quad}                                                \tag{5f}
\]

For the first three entries this reads

\[
 \begin{aligned}
 \widetilde H_8(F_\sigma;\mathbb Q)
     &\cong H_c^0(B_\sigma;\mathbb Q),\\
 H_7(F_\sigma\cap F_\tau;\mathbb Q)
     &\cong H_c^1(B_\sigma\cup B_\tau;\mathbb Q),\\
 H_6(F_{\{\sigma,\tau,\upsilon\}};\mathbb Q)
     &\cong H_c^2(B_\sigma\cup B_\tau\cup B_\upsilon;\mathbb Q).
                                                               \tag{5f'}
 \end{aligned}
\]

There is an important source-trace qualification.  An independent reduction
argument covers most, but not all, of the catalog.  Bokowski--Richter,
[Corollary 4.9, p. 7](https://www.math.ucdavis.edu/~deloera/MISC/LA-BIBLIO/trunk/Richter-Gebert/Richter13.pdf),
finds `2,546` of the `2,628` rank-four/eight-element reorientation classes for
which the chirotope or its dual is reducible by an element.  The forgetful map
for a reducible element is a homotopy equivalence by
[Richter--Sturmfels, Lemma 2.1](https://doi.org/10.1090/S0002-9947-1991-0994170-3),
and the deletion is dual to a uniform rank-three matroid on seven elements,
whose realization space is contractible by their rank-three/eight-element
theorem.  This independently proves contractibility for those `2,546` classes.
Bokowski--Richter state on p. 9 that their Theorems 4.10 and 4.11 establish
realizability for the additional `58` realizable classes among the remaining
`82`; those two theorems do not assert a homotopy equivalence.  Contractibility
for these exceptional `58` therefore relies here on Tsukamoto's published
blanket statement, whose accompanying citation is historical rather than a
proof trace.  No claim that Theorems 4.10--4.11 preserve topology is being made.

There is an independent improvement exactly at the fourth diagonal.  For
every realizable uniform rank-four/eight-element parent,

\[
                         \widetilde H_5(X;\mathbb Z)=0.           \tag{5f-a}
\]

Indeed, delete a parent label `e`.  The deletion realization space `D` is
dual to a rank-three/seven-element realization space and is contractible by
the Richter--Sturmfels theorem.  The insertion map identifies `X` up to a
convex residence-three-cell factor with the nonempty-insertion locus
`G_e^del subset D`.  At a point of `D minus G_e^del`, Gordan gives a positive
circuit on at most five triples of the seven deletion labels.  Its at most
fifteen label occurrences leave one label of degree at most two.  The
degree-zero, plane-shear, or positive-ray pencil path for that label preserves
the circuit and runs to the deletion-cell boundary.  Thus every component of
`D minus G_e^del` is noncompact and its `H_c^0` vanishes.  Integral
Poincare--Alexander duality in the oriented six-manifold `D` gives (5f-a).
The full residence-bundle and escape proof is in
[`FOURTH_DIAGONAL_FIVEFOLD.md`](FOURTH_DIAGONAL_FIVEFOLD.md).

Together with the contraction--height vanishing in degrees at least six,
(5f-a) proves the bad-locus isomorphisms above for `s<=4` without the blanket
contractibility input.  For the later entries, a formulation which avoids
parent contractibility altogether compactifies the fixed projective-frame slice
`R^9` to `S^9` and puts

\[
 A_S=S^9\setminus F_S=(S^9\setminus X)\cup B_S.
\]

Alexander duality gives the exact formulation

\[
 \widetilde H_{9-s}(F_S;\mathbb Q)
      \cong \widetilde{\check H}^{s-1}(A_S;\mathbb Q). \tag{5g}
\]

The common compactification term `S^9 minus X` is essential for `s>=5`; an
affine CAD that silently drops it can lose exactly the class being tested.

The first diagonal theorem says `H_c^0(B_sigma)=0`, or equivalently that no
single bad locus has a compact connected component.  Simultaneous
semialgebraic triangulation justifies compact-support Mayer--Vietoris for these
closed relative subsets and sharpens the second line of (5f').  For two
signatures there is a short exact sequence

\[
 0\longrightarrow H_c^0(B_\sigma\cap B_\tau)
 \longrightarrow H_c^1(B_\sigma\cup B_\tau)
 \longrightarrow \ker\!\left[
 H_c^1(B_\sigma)\oplus H_c^1(B_\tau)
 \longrightarrow H_c^1(B_\sigma\cap B_\tau)
 \right]\longrightarrow0.                              \tag{5h}
\]

A dual single-bad escape theorem removes the last term of (5h) integrally.
Let `N` be any realizable uniform rank-four oriented matroid on nine elements.
Contract a distinguished element `p` and Gale-dualize.  The height locus for
`N` becomes a single-extension feasibility locus over the rank-five,
eight-element parent `N* minus p`.  At a bad chart, a minimal Gordan circuit
has at most six four-subset normals and therefore at most 24 label incidences.
Some label occurs at most three times.  Moving that column in the intersection
of its at most three support hyperplanes in projective four-space preserves
the positive circuit up to positive rescaling and reaches a parent wall.
Every single bad component is therefore noncompact.  Supported duality and
the contraction-height ambient vanishing give

\[
 \widetilde H_7(\mathcal R(N);\mathbb Z)=0,
 \qquad H_c^1(B_\rho;\mathbb Z)=0                         \tag{5h'}
\]

for every extension signature `rho` over a rank-four/eight-element parent.
Consequently (5h) collapses to

\[
 H_c^1(B_\sigma\cup B_\tau;\mathbb Z)
       \cong H_c^0(B_\sigma\cap B_\tau;\mathbb Z).        \tag{5h''}
\]

Thus the second diagonal now has exactly one target: `B_sigma intersection
B_tau` has no compact connected component.  Convexity of the simultaneous
primal lift fiber is false and is not used here.  The complete proof and an
exact sharp six-normal regression are in
[`DIAG2_PIVOT_DUAL_SINGLE_BAD_ESCAPE.md`](DIAG2_PIVOT_DUAL_SINGLE_BAD_ESCAPE.md)
and
[`DIAG2_PIVOT_DUAL_SINGLE_BAD_ESCAPE.py`](DIAG2_PIVOT_DUAL_SINGLE_BAD_ESCAPE.py).

### 4.3 Exact Gordan--Koszul resolution

Let `A_sigma(Y)` be the `56 by 4` matrix of signed derived normals.  Gordan's
alternative identifies the bad locus with the projection of

\[
 \Gamma_\sigma=\{(Y,\lambda):
  \lambda\ge0,\quad {\bf1}^{T}\lambda=1,\quad
  A_\sigma(Y)^T\lambda=0\}.                            \tag{5i}
\]

The projection is proper and every fiber is a nonempty compact convex
polytope.  Hence the proper Vietoris--Begle theorem identifies its
compact-support cohomology with that of `B_sigma`.  A union `B_S` has the same
kind of resolution: use one nonnegative block `lambda_sigma` per signature and
normalize the sum of all blocks to one.  For an intersection, normalize every
block separately.  This gives exact models for (5e)--(5h) without making a
continuous choice of a Gordan witness.

There is additional structure special to the third compound.  Let
`T_Y:R^8 -> R^4` send the standard basis vector `e_i` to `y_i`, and put
`K_Y=ker(T_Y)`.  Under the usual identification of derived normals with
`Lambda^3 T_Y`, a direct exterior-algebra decomposition gives

\[
 \ker(\Lambda^3T_Y)=K_Y\wedge\Lambda^2\mathbb R^8.
                                                               \tag{5j}
\]

Both sides have dimension `56-4=52`.  Consequently `Y in B_sigma` exactly
when this Koszul subspace contains a nonzero coefficient form `c` with
`sigma_I c_I>=0` in all 56 coordinates.  A support-minimal such form uses at
most five triples.  For a five-element support its coefficients are the
alternating four-by-four cofactors of the five signed derived normals, so their
signs are controlled by the 52 wall types from Section 12.  Supports of size
three or four lie on the corresponding rank-deficient wall strata; their
lower-order cofactors must be retained explicitly.  Thus each bad locus is a
finite union of quantifier-free basic circuit loci.  Its generic pieces use
only parent-bracket units and the thirteen residual wall types, with the
lower-rank pieces attached along their exact degeneracy strata.

Each one of those basic circuit loci has a useful convex deletion fiber.  Five
triples contain at most fifteen label occurrences, so some parent label `e`
occurs in at most one triple of the witness.  With the other seven parent
columns fixed, all witness normals except possibly one are fixed, and the last
is linear in `y_e`.  Positivity of the circuit says that this last normal lies
in a fixed convex cone.  Its inverse image, intersected with the open convex
residence chamber of `y_e`, is convex.  The same conclusion holds
simultaneously for circuit supports `E_1,...,E_t` whenever one parent label is
light in every support, meaning that it occurs in at most one triple of each
`E_j`: each circuit condition contributes either no condition on `y_e` or the
inverse image of a fixed convex cone under the linear map
`y_e mapsto a_{eab}`.  Their intersection with the parent residence chamber
is therefore convex.  This is an exact deletion gate for a
Mayer--Vietoris or CAD computation.  The obstruction to iterating it is now
precise: a tuple of circuit pieces need not possess one label which is light
in all of its supports.

There is also a useful escape criterion for the compact-component obstruction
in (5h).  Suppose extreme positive circuits witnessing
`Y in B_sigma intersection B_tau` jointly omit a parent label `e`.  Hold the
other seven columns fixed and move `y_e` to the boundary of its open convex
residence chamber.  Every normal in both witnesses remains fixed, so both
positive dependences persist along the path.  The path has no limit in `X`.
Consequently the component of `B_sigma intersection B_tau` containing `Y` is
noncompact.  Any compact simultaneous-bad component must therefore be trapped
entirely among pairs of circuit supports which cover all eight parent labels.

The exact prototype

```console
python ai/omreal/prototype_koszul_circuits.py
```

checks (5j) on a row-2599 integer chart, reconstructs all eight stored Gordan
witnesses in the eight-shatter certificate as minimal positive Koszul circuits,
and tags every cofactor by its wall orbit.  It uses exact integer and rational
arithmetic only.

### 4.4 A finite circuit-cover strategy for diagonals two and three

The circuit reduction admits a compact-support Mayer--Vietoris spectral
sequence with strong automatic pruning.  For a signature `rho` and a set `Q`
of at most five parent triples, let `Delta_Q` be the simplex of nonnegative
weights on `Q` with total weight one, and put

\[
 C_{\rho,Q}=\left\{Y\in X:\text{some }\lambda\in\Delta_Q\text{ satisfies }
       \sum_{I\in Q}\lambda_I\rho_Ia_I(Y)=0\right\}.    \tag{5k}
\]

These sets are closed semialgebraic subsets of `X`: the defining incidence is
closed and its weight simplex is compact.  Caratheodory's theorem and Gordan's
alternative give the finite cover

\[
              B_\rho=\bigcup_{1\le|Q|\le5}C_{\rho,Q}.  \tag{5l}
\]

This cover has a useful cofinal simplification.  If `Q' subseteq Q`, a
witness on `Q'` can be padded by zero weights, so
`C_(rho,Q') subseteq C_(rho,Q)`.  Every support of size at most five is
contained in a five-support.  Hence the same closed cover may be written

\[
              B_\rho=\bigcup_{|Q|=5}C_{\rho,Q}.        \tag{5l'}
\]

In particular the spectral-sequence indices below may all be chosen to have
size five.  Three- and four-circuits are not discarded: they are simplex-face
strata inside these five-support incidences.  Thus a generic `4+5` pair is
boundary data for restriction maps, rather than an independent pair index on
this cofinal cover.  A standalone proof ledger is in
[`SECOND_DIAGONAL_COFINAL_COVER.md`](SECOND_DIAGONAL_COFINAL_COVER.md).

For `rho in S`, index all pieces in (5l) by `alpha=(rho,Q)`.  A simultaneous
semialgebraic triangulation gives the closed-cover spectral sequence

\[
 E_1^{p,q}=
 \bigoplus_{\alpha_0<\cdots<\alpha_p}
 H_c^q(C_{\alpha_0}\cap\cdots\cap C_{\alpha_p};\mathbb Q)
 \quad\Longrightarrow\quad H_c^{p+q}(B_S;\mathbb Q).  \tag{5m}
\]

This descent has an exact all-diagonal truncation.  At the cochain level,
`H_c^(s-1)(B_S)` is the middle cohomology of

\[
 \operatorname{Tot}^{s-2}\longrightarrow
 \operatorname{Tot}^{s-1}\longrightarrow
 \operatorname{Tot}^{s}.
\]

A term of total degree `n` has Cech degree at most `n`, hence uses an
intersection of at most `n+1` circuit pieces.  Therefore diagonal `s` is
determined by intersections of at most `s+1` pieces and cochain degrees at
most `s`; no `(s+2)`-fold intersection can affect it.  In particular the
fourth diagonal is an exact fivefold computation in total degrees
`2 -> 3 -> 4`.  This statement concerns functorial cochain models, so it
retains all higher spectral-sequence differentials rather than silently
replacing `E_infinity` by `E_1`.

The weight variables can be retained in proper incidence models with compact
convex fibers, so the existential quantifiers can be removed from each
summand without changing its compact-support cohomology.  Compatible
restriction maps still require witness correspondences or a simultaneous
triangulation.  More importantly, the incidence hypergraph of the supports
eliminates most low-degree summands.
For a tuple of pieces, let `U` be the union of its triples and let `deg_U(e)`
be the number of distinct triples containing parent label `e`.

> **Projective-plane-pencil pruning lemma.**
>
> * If `deg_U(e)=0`, then the compact-support cohomology of the piece
>   intersection vanishes in degrees below three.
> * If `deg_U(e)=1`, it vanishes in degrees below two.
> * If `deg_U(e)=2`, its compactly supported `H^0` vanishes.
> * More generally, if every triple of `U` containing `e` also contains one
>   fixed second label `f`, then its compactly supported `H^0` vanishes.

**Proof.**  Choose a projective frame avoiding `e`.  In the first case every
involved derived normal is independent of `y_e`; the fiber obtained by moving
`y_e` through its parent residence chamber is an open convex three-cell.  In
the second case the sole triple has the form `eab`.  The two-parameter shear

\[
                   y_e\longmapsto y_e+s y_a+t y_b
\]

preserves its derived normal and every other involved normal.  The quotient
retains `Y minus e` and the oriented plane `span(y_e,y_a,y_b)`; its fiber is
the full residence slice in that plane, an open convex two-cell.  In the last
case the one-parameter shear `y_e mapsto y_e+t y_f` does the same.  After
passing to the corresponding semialgebraic quotient, the fiberwise
compact-support cohomology is respectively concentrated in degree three, two,
or one.  The `f_!` Leray spectral sequence proves the asserted vanishings.

For the new degree-two case it is important to use **positive rays**, rather
than unoriented projective points.  With the other seven columns fixed, write
the residence cone of `e` as

\[
 R_e=\{z\in\mathbb R^4\setminus\{0\}:\epsilon_J
             \det(y_J,z)>0\text{ for every }J\subset E\setminus\{e\},
             |J|=3\},
\]

where the fixed signs `epsilon_J` are chosen so that `y_e in R_e`.  This is an
open convex homogeneous polyhedral cone, and its quotient by positive scaling
is the parent residence chamber.  Let the two distinct support triples through
`e` span vector three-planes `H_1,H_2`.  Uniformity makes them distinct, so
`L=H_1 intersection H_2` is a vector two-plane containing `y_e`.  No defining
linear form of `R_e` vanishes identically on `L`, since that would put `y_e` on
a parent residence wall.  Hence `R_e intersection L` is a nonempty proper open
convex cone in `L`; modulo positive scaling it is an open interval, with a
residence-boundary ray at each end.  (The two ends may project to the same
point only if one forgets the orientation of the ray.)

Move `y_e` inside this interval toward either endpoint.  For either incident
triple `I`, its spanned three-plane stays fixed, and hence

\[
                         a_I(Y(t))=c_I(t)a_I(Y(0)).
\]

The scalar is continuous, starts at `c_I(0)=1`, and cannot vanish before the
residence boundary because the configuration remains uniform.  Thus
`c_I(t)>0`.  All normals for triples not containing `e` stay fixed.  This
preserves each circuit piece separately: if `lambda^Q` witnesses
`Y(0) in C_(rho,Q)`, replace its coordinate at every incident triple `I` by
`lambda_I^Q/c_I(t)`, leave the other coordinates unchanged, and renormalize
the resulting nonnegative vector to have sum one.  The signed linear
dependence is unchanged.  In particular there is no compatibility issue when
the same triple occurs in several supports, because those supports have
separate weight simplices.

The resulting path remains in the full piece intersection and tends to a
point of the residence boundary, hence has no limit in `X`.  Every path
component of this semialgebraic intersection is therefore noncompact; since
there are finitely many components, its compactly supported `H^0` is zero.
The fixed-partner case is identical with `L=span(y_e,y_f)`, which lies in all
incident support planes.  QED.

Several fixed-partner directions can be combined when they have one common
apex.  For a triple union `U` and a label `f`, put

\[
 D_f(U)=\{e\ne f:\ e\in I\in U\Longrightarrow f\in I\},\qquad
 \delta(U)=\min\bigl(3,\max_f|D_f(U)|\bigr).             \tag{5m-a}
\]

Thus a label omitted by `U` belongs to every `D_f(U)` with `f!=e`.

> **Common-apex simultaneous-shear lemma.**  If `Z` is an intersection of
> circuit pieces with support union `U`, then
>
> \[
>                         H_c^q(Z;\mathbb Q)=0
>                  \qquad\text{for }q<\delta(U).         \tag{5m-b}
> \]

**Proof.**  Choose `f` and distinct labels `D subset D_f(U)` with
`d=|D|<=3`.  There are at least five labels outside `D`, including `f`, so
use five of them as a projective frame.  This is why the certified rank is
capped at three: five fixed labeled points are needed to remove `PGL(4)`.
When more than three labels are dominated, any three of them still give the
stated bound; the remaining raw column-shear parameters cannot be counted
independently after projectivizing.

For every `e in D`, choose a frame covector which vanishes on `y_f` and is
nonzero on `y_e`, normalize the representative of `y_e` by that covector, and
retain its class modulo `span(y_f)`.  Together with the fixed columns these
data define a semialgebraic quotient map `pi`.  A nonempty fiber has unique
coordinates

\[
                           y_e\longmapsto y_e+t_e y_f,
                 \qquad (t_e)_{e\in D}\in\mathbb R^d.   \tag{5m-c}
\]

Every support triple which contains a moving label also contains `f`.
Consequently its exterior product, and hence its derived normal, is unchanged
by (5m-c); this remains true when a triple contains two labels of `D` because
the term with two copies of `y_f` vanishes.  All circuit witnesses therefore
remain valid throughout a fiber.  For the same reason, the expansion of any
parent four-bracket has no term involving two shear parameters.  It is affine
jointly in `(t_e)`.  The fixed parent-chirotope inequalities cut out a
nonempty open convex subset of `R^d`, hence an open `d`-cell.

The compact-support Leray spectral sequence for `pi` now has
`R^j pi_! Q=0` for `j!=d`.  Its degree-`d` sheaf is the rank-one fiber
orientation system (possibly twisted); twisting cannot create a term of
total degree below `d`.  Hence `H_c^q(Z;Q)=0` for `q<d`.  Maximize over
`f` and `D`.  QED.

The common apex is essential to the convex-fiber proof.  On the exact
row-2599 pattern-zero chart, the two shears

\[
                 y_3\mapsto y_3+t y_8,\qquad
                 y_6\mapsto y_6+s y_2
\]

have both `(t,s)=(0,0)` and `(-1,4)` in the parent realization cell, but the
midpoint `(-1/2,2)` is outside it.  Indeed the only sign failure is

\[
 [3456](t,s)=355617-594661t-480549s-253190ts,
 \qquad 2[3456](-1/2,2)=-109921.
\]

Thus deletion ranks belonging to different apices cannot simply be added:
the joint parent-cell fiber is already nonconvex before any circuit
inequality is imposed.

There is also an exact obstruction at every possible tuple length.  On the
same chart, let

\[
 Q_0=123/134/267/258/468,\qquad
 Q_4=123/256/127/357/478.
\]

Their union has label degrees `(3,5,3,3,3,3,4,3)`.  It is pencil-rigid, all
the sets `D_f` are empty, and, more strongly, the normals of the incident
support planes have rank three at every label.  Hence a first-order motion
which keeps every one of these support planes fixed moves each `y_e` only in
`span(y_e)`: the chosen support-plane framework has no projective motion.

The exact checker below supplies nine **distinct realizable** extension
signatures and one positive circuit piece for each at this common chart.  The
first two pieces use `Q_0,Q_4`; every prefix of length `2,...,9` remains
pencil-rigid and support-plane rigid.  Five signatures have explicit good
charts in the width-seven artifact and four in the shatter artifact, while
the common pattern-zero chart is bad for all nine.  Thus every one of the nine
feasibility regions is proper.  The mixed nine-signature family is not
certified pairwise incomparable.  Plane rigidity here concerns only the
chosen circuit supports at the stored chart: it neither makes the piece
intersection isolated nor proves that its `H_c^0` is nonzero.

```console
python ai/omreal/verify_simultaneous_shears.py
```

In particular, common-deletion and plane-preserving-shear ranks alone cannot
kill all the diagonal terms.  For each `t=2,...,9` the exact prefix gives a
nonempty candidate in bidegree `(p,q)=(t-1,0)` to which their lower bound
assigns rank zero.  Removing those candidates still requires a topological
argument about noncompact components or a differential in (5m), not a
stronger count of these shear directions.

Call a triple union `U` **pencil-rigid** if every label has degree at least three
and no label has a fixed second partner in all of its incident triples.  The
spectral sequence now gives an exact second-diagonal complex and a finite
third-diagonal sufficient test.  Every single circuit piece has both
`H_c^0=0` and `H_c^1=0`, because at most fifteen label occurrences force some
label to have degree at most one.  Therefore, for `S={sigma,tau}`, (5m) gives

\[
 H_c^1(B_S)\cong
 \ker\!\left[
  \bigoplus_{\alpha<\beta}H_c^0(C_\alpha\cap C_\beta)
  \xrightarrow{\ d_1\ }
  \bigoplus_{\alpha<\beta<\gamma}
       H_c^0(C_\alpha\cap C_\beta\cap C_\gamma)
 \right],                                                \tag{5n}
\]

where `d_1` is the alternating sum of restriction maps.  All pair summands
whose support union is not pencil-rigid vanish formally.  Thus the second
diagonal is exactly injectivity of the finite compact-component incidence
matrix in (5n).  By (5h''), this kernel computes the same single obstruction
`H_c^0(B_sigma intersection B_tau)`; it is no longer an additional
single-region restriction-map condition.  Proving every surviving pair group
zero remains a stronger sufficient condition.

Using the cofinal cover (5l'), every pair index in (5n) is of type `5+5`.
The `3+*`, `4+4`, and `4+5` classifications below still control boundary
strata but do not contribute separate pair indices.  In particular `beta>=1`
on every relative interior of a cofinal pair incidence: there are eight
log-weight ratios and the effective column-scaling torus has rank at most
seven.  This bookkeeping improvement does not by itself prove injectivity,
because two maximal five-support indices need not have a common larger
support in the cover.

There is nevertheless a same-signature exchange.  If two distinct maximal
pieces `C_(rho,Q),C_(rho,R)` have pencil-rigid union, every point of their
intersection lies in a third maximal piece of the same signature.  For
lower-support witnesses this is zero-padding.  Otherwise the two strict
five-circuits lie in the nonnegative dependence cone on `Q union R`.
Pencil rigidity gives `|Q union R|>=8`; the cone has dimension at least
`|Q union R|-4>=4`, so it has at least two further extreme circuit rays.
Consequently each individual compact pair-component class has nonzero
`d_1` image.  This still falls short of injectivity because linear
combinations can cancel around triple-incidence cycles.  More seriously,
an exact proper incomparable row-2599 pair has mixed separation signs on
both support differences, so the span of its two cross-signature witness
rays contains no third positive ray for either signature.  The proof and
exact arithmetic check are in
[`SECOND_DIAGONAL_COFINAL_COVER.md`](SECOND_DIAGONAL_COFINAL_COVER.md) and
[`verify_second_diagonal_nerve.py`](verify_second_diagonal_nerve.py).

A boundary-pivot refinement localizes any possible kernel further.  A compact
maximal-pair component must meet a proper circuit-support face.  If that
smaller support paired with the other maximal support is pencil-flexible, it
can be padded to a third five-set for which the other two pair groups have
zero `H_c^0`; the resulting triple-component row has only the original
nonzero entry.  Hence a `ker(d_1)` coefficient can survive only when every
circuit-drop boundary available to it remains pencil-rigid.  This is exactly
why the lower-support strata cannot simply be discarded after cofinalizing.

For the third diagonal, the preliminary support sieve left three kinds of
total-degree-two terms: single-piece `H_c^2`, pairwise `H_c^1`, and triple
`H_c^0`.  The generic single-piece sieve first reduced its column to 45
`S_8` support orbits, described after the weight-gauge theorem below.  The
later plane-plus-pencil theorem (34) eliminates that entire column, including
nongeneric and lower-support faces.  Thus only pairwise `H_c^1` and triple
`H_c^0` terms remain; the exact counterexamples below show that the earlier
fixed-deletion tests do not kill those two columns term by term.  The full
proof-status ledger, historical reduction, and independent census audit are
[`THIRD_DIAGONAL_E1_REDUCTION.md`](THIRD_DIAGONAL_E1_REDUCTION.md) and
[`THIRD_DIAGONAL_SUPPORT_FILTER_AUDIT.md`](THIRD_DIAGONAL_SUPPORT_FILTER_AUDIT.md).

For the fourth diagonal, one more top-fiber class can be removed uniformly.
Use the uncofinalized cover (5l) for this refinement, since padding a smaller
witness to five triples can hide a genuinely omitted label.
Let `Z` be an intersection of circuit pieces with support union `U`.  If one
label `e` is omitted by `U` and a second label `f` has `deg_U(f)<=2`, then

\[
                          H_c^q(Z;\mathbb Q)=0
                          \qquad(q\le3).               \tag{5n-a}
\]

Choose a projective frame avoiding `e,f`.  Deleting `e` gives the full
residence three-cell, while `f` moves in a one-dimensional
support-preserving pencil.  Quotient these four parameters simultaneously.
At a fixed pencil parameter every parent four-bracket is affine in the three
affine coordinates of `e`, so the parameter section is empty or open convex.
The projection of any connected component of the full parameter domain to
the pencil coordinate is an open interval; a continuous convex-fiber section
and straight-line contraction retract that component onto the interval.
Thus every fiber component is a contractible oriented open four-manifold.
For the possibly nonproper semialgebraic quotient `pi`, compactify the
parameter coordinates fiberwise and write `R pi_!` as proper pushforward
after extension by zero.  Proper base change identifies its stalks with the
fiber compact-support groups, and compact-support Leray descent proves
(5n-a).  If an incident normal changes by a positive scalar, dividing the
corresponding Gordan coordinate by that scalar preserves zero coordinates as
well; hence the proof applies to every lower-support face of the closed
circuit pieces.

For a single support of at most five triples, omission of `e` forces such an
`f` by `15/7<3`.  Hence the `(p,q)=(0,3)` fourth-diagonal column retains only
supports covering all eight labels.  Among the `2,021,992` generic labeled
five-supports this leaves `1,099,560` in `66` of `117` `S_8`-orbits, removing
`922,432` supports in `51` orbits.  An exact row-2599 four-signature shatter
subfamily has positive minimal circuits whose union is already pencil-rigid,
so this incidence sieve is sharp as a formal method; it does not assert
nonzero compact-support cohomology.  The proof, exact total-complex sieve, and
arithmetic verifier are
[`FOURTH_DIAGONAL_FIVEFOLD.md`](FOURTH_DIAGONAL_FIVEFOLD.md) and
[`verify_fourth_diagonal_reduction.py`](verify_fourth_diagonal_reduction.py).

The omission count and the generic count should not be conflated.  The
dependency-free checker
[`verify_fourth_single_piece_light_count.py`](verify_fourth_single_piece_light_count.py)
enumerates all `4,216,422` supports of one through five triples.  Exactly
`2,500,442` omit a label and satisfy (5n-a); the other `1,715,980` cover all
eight labels, split as `840`, `72,380`, and `1,642,760` in sizes three, four,
and five.  It also verifies that every cover-all support has a degree-one
label and two distinct degree-at-most-two labels outside its unique triple.
That last fact supplies four motion parameters but is only a count, not a
top-row vanishing theorem.

There is also a finer deletion model for the surviving higher-degree terms.
If the tuple of
supports has a **common-light** label `e`, meaning
`deg_(Q_j)(e)<=1` for every support separately, then fixing the deletion
`Y minus e` leaves a convex joint residence fiber `K_b`.  It is the
intersection of the open parent residence polytope `P_b^circ` with inverse
images of fixed closed cones.  Let `bar K_b` be its closure in the closed
residence polytope and let `L_b=bar K_b intersection boundary(P_b)` be its exit
set.  Since `bar K_b` is convex,

\[
 H_c^q(K_b)\cong H^q(\overline K_b,L_b),\qquad
 H_c^q(K_b)\cong\widetilde H^{q-1}(L_b)\quad(q\ge1).   \tag{5o}
\]

For a nonempty fiber, `H_c^0(K_b)=0` exactly when `L_b` is nonempty.  (An
empty fiber also has zero compact-support cohomology.)  The intersections of
`bar K_b` with the facets of the residence polytope form a convex good cover
of `L_b`, so the cohomology in (5o) is the cohomology of a finite facet nerve.

For one or two pieces, the lowest-degree exit question has a uniform answer.

> **Two-piece common-light exit lemma.**  Let `t<=2`, and fix a deletion
> realization `b`.  If nonempty circuit pieces
> `C_(rho_1,Q_1),...,C_(rho_t,Q_t)` have a common-light label `e`, then their
> joint residence fiber has `L_b!=empty`.  Consequently every global
> intersection of one or two such pieces has
>
> \[
>       H_c^0(C_{\rho_1,Q_1}\cap\cdots\cap C_{\rho_t,Q_t};\mathbb Q)=0.
>                                                               \tag{5p}
> \]

**Proof.**  Work in the four-dimensional vector space before projectivizing
the moving column.  A piece which omits `e` is constant on the residence
fiber.  Otherwise its unique moving triple is `eab`.  Unless the fixed
normals already have a positive dependence, in which case the condition is
automatic, the circuit condition is the inverse image of a fixed closed
convex cone under the linear map

\[
                 y_e\longmapsto \rho_{eab}a_{eab}(y_e).
\]

Its kernel is `L=span(y_a,y_b)`, and the resulting inverse-image cone is
invariant under addition and subtraction of `L`.  Write that cone as `D_i`
and this distinguished two-dimensional lineality subspace as `L_i`.

For one nontrivial piece, or for two with `L_1 intersection L_2 != 0`, choose
nonzero `v` in the common lineality.  The projective line represented by
`y_e+t v` stays in every `D_i`.  Its component inside the open residence
polytope is an open interval, whose endpoint lies on the parent residence
boundary.

It remains to consider `L_1 intersection L_2=0`.  Both lineality spaces have
dimension two, so `R^4=L_1 direct-sum L_2`.  Write `y_e=x_1+x_2` with
`x_i in L_i`.  Since each `D_i` is invariant under addition and subtraction
of `L_i`, membership of `y_e` gives `x_2 in D_1` and `x_1 in D_2`.  Hence

\[
                     [t x_1+x_2],\qquad 0<t<=1,
\]

stays in both circuit cones.  Uniformity makes `x_1,x_2` nonzero, and the
limit `[x_2]` puts the moving parent element in the span of the two fixed
columns defining `L_2`; it is not in the open uniform residence chamber.
The path therefore has a first contact with its boundary, proving
`L_b!=empty`.

Finally, this path holds the deletion realization fixed.  Starting at any
point of the global piece intersection it remains in the same connected
component and approaches a point outside `X`.  That component cannot be
compact in `X`.  Semialgebraic local connectedness then identifies the absence
of compact components with (5p).  QED.

Thus every pair summand in (5n) with a common-light label vanishes.  For two
supports this is already implied by the projective-plane-pencil lemma, because
their union then has degree at most two at the common-light label; the argument
above additionally exposes the exact convex fiber and its exit nerve.  A pair
can survive the second-diagonal complex only if its support union is
pencil-rigid.  In particular it has no common-light label.  Call this necessary
per-support condition **heavy-cover**.

The lemma is sharp in both next degrees, even after imposing properness and
pairwise incomparability.  In the exact row-2599 eight-shatter artifact,
pattern 14 has positive five-circuits

\[
 \begin{aligned}
 Q_0&=134/234/156/267/258,\\
 Q_6&=125/246/147/358/468.
 \end{aligned}
\]

They have common-light label `e=7`.  The exact exit-facet nerve consists of
the edge `1237--5678` and the isolated vertex `1367`.  Hence `L_b` has two
components and `H_c^1(K_b;\mathbb Q)=\mathbb Q`.  The same artifact shatters these two
signature coordinates, so their full feasibility regions are proper and
incomparable.  Connectedness is therefore not automatic for two pieces.

Nor is a common-light exit necessarily `H_1`-acyclic.  On pattern zero, the
single positive circuit

\[
                  Q_4=123/256/127/357/478
\]

has light label `e=8`.  Its exact exit nerve is connected with first Betti
number one, so `H_c^2(K_b;\mathbb Q)=\mathbb Q`; shattering proves that the corresponding
signature is proper.  The arithmetic-only verifier derives all circuit-cone
inequalities, enumerates the rational residence vertices, constructs both
facet nerves from actual face feasibility, and computes their homology:

```console
python ai/omreal/verify_common_light_exits.py
```

For tuples of three or more common-light pieces, even nonemptiness of the exit
is not supplied by this argument.  Stratifying the deletion space by the
face-feasibility predicates still turns their part of (5m), and all higher
exit cohomology, into a constructible-sheaf calculation.  Heavy-cover tuples
require direct wall analysis or CAD.

An exact generic-support census shows why positivity must be imposed before
CAD.  Away from all residual walls there are `560`, `30,240`, and `2,021,992`
labeled minimal circuit supports of sizes three, four, and five, respectively;
they form `1`, `6`, and `117` orbits under `S_8`.  For unordered support pairs
of size types `33,34,35,44,45,55`, the older shear-rigid orbit counts are

\[
                 0,\ 0,\ 599,\ 73,\ 128{,}944,\ 15{,}392{,}537.
\]

Thus that coarse unsigned filter leaves `15,522,153` pair orbits,
overwhelmingly of type `5+5`; the stronger pencil-rigid condition additionally
requires minimum union degree three.  Even before that stronger filter this is
not yet a small CAD list.  The exact standard-library
checker is

```console
python ai/omreal/verify_circuit_support_orbits.py
```

It also counts the common-light and joint-omission filters.  The checker does
not impose circuit positivity after `sigma,tau` reorientation or compatibility
with realizable single-element extensions.  Those are the essential next
filters, and any later finite calculation must certify them before geometric
triangulation.

There is a sharp signed reduction in support sizes three and four.  If
`Q={abc,abd,abe}` is a generic three-support, then the exact common-pair
syzygy is

\[
 [abde]a_{abc}-[abce]a_{abd}+[abcd]a_{abe}=0.             \tag{5q}
\]

After reorientation by an extension signature `rho`, positivity of (5q)
would say that

\[
 [abcd]\rho_{abe},\qquad-[abce]\rho_{abd},\qquad
 [abde]\rho_{abc}
\]

all have one sign.  These are precisely the three Grassmann--Pluecker terms
for `lambda=ab` and the four elements `c,d,e,p`.  A valid uniform
single-element extension forbids that sign pattern.  Thus **every generic
three-circuit piece is empty**, and in particular all `599` unsigned
shear-rigid `3+5` pair orbits disappear.

For a generic four-support, all four triples have one common hub `h`.  Delete
`h` from the triples and regard the result as a four-edge graph on the other
seven labels.  Choose a triple `J` not containing `h` and order
`Q={q_0,q_1,q_2,q_3}`.  Its circuit cofactors are

\[
 c_i=(-1)^i\det(a_{q_0},\ldots,\widehat{a_{q_i}},\ldots,
                  a_{q_3},a_J).                          \tag{5r}
\]

The exact wall classification gives the following complete table.

| graph type | labeled supports | residual cofactors |
|---|---:|---:|
| `C3+P2` | 1,680 | 0 |
| `C4` | 840 | 0 |
| `P5` | 10,080 | 0 |
| `P4+P2` | 10,080 | 1 |
| `2P3` | 5,040 | 0 |
| `P3+2P2` | 2,520 | 2 |

A cofactor in (5r) is residual exactly when the other three graph edges form
a matching on six labels.  Write that localization determinant as
`Delta_(h;ab|cd|ef)`; every other cofactor is a nonzero parent-bracket unit.
If all four cofactors are units, their signs are fixed throughout `X`.  A
realizable signature cannot align with that circuit, since the resulting
positive dependence would persist at a chart which realizes the signature.
Hence only the last-column-variable graph types `P4+P2` and `P3+2P2` survive,
accounting for `12,600` of the `30,240` labeled supports.

More explicitly, factor `c_i=u_i f_i`, where `u_i` is a signed
parent-bracket unit and `f_i` is either `1` or the indicated `Delta` atom.
The exact signed filter is the XOR system

\[
        \operatorname{sgn}(f_i)\operatorname{sgn}(u_i)\rho_{q_i}
        =\eta_Q\quad(0\le i<4),\qquad \eta_Q\in\{+,-\}.   \tag{5s}
\]

For `P4+P2`, three unit equations must agree and then force one localization
side; for `P3+2P2`, two unit equations must agree and then force two sides.
Merging (5s) for two prescribed signatures is a constant-size XOR-SAT
filter.  A shear-rigid pair of structural four-supports must have different
hubs: with one common hub, every incident nonhub label would have that hub as
a fixed shear partner.  Thus the localization atoms in a surviving pair are
disjoint, and unary extension/localization axioms provide no further coupling.

The support-orbit count drops from `73` unsigned `4+4` orbits to
`39=20+13+6`, according as the two surviving graph types are `AA`, `AB`, or
`BB`.  This does not assert that all 39 occur for any one prescribed pair.
For the eight exact row-2599 shatter signatures, the unit part of (5s) leaves
between `105,206` and `111,232` of the `2,429,280` labeled shear-rigid pairs
of the two surviving graph types, depending on the prescribed signature
pair.  This roughly 95.5-percent rejection rate is a finite sample, not a
universal density claim.

None of these 39 coarse types is a second-diagonal residue.  Indeed, the union
of two four-supports contains at most eight triples and therefore has total
incidence at most `24`.  Pencil rigidity would require all eight label degrees
to be at least three, forcing exactly eight union triples and every label
degree to equal three.  But each structural four-support has a hub belonging
to all four of its triples, giving union degree at least four at that hub, a
contradiction.  Thus **every generic `4+4` pair is pencil-flexible**, before
any signed calculation.

The stronger obstruction cannot be replaced by signed incidence alone.  At
the exact row-2599 pattern-zero chart, signatures `1` and `2` have the positive
generic `P3+2P2` circuits

\[
\begin{aligned}
 Q&=145/356/157/258,
 &\lambda_Q&=(221601476670,380827220000,90848922285,319059375744),\\
 R&=124/345/347/468,
 &\lambda_R&=(22119895128,82096061557,5377382637,57911448192).
\end{aligned}
\]

Their union is shear-rigid, all displayed coefficients are positive after the
prescribed reorientations, and the shatter artifact independently gives exact
charts realizing both signatures.  Its failure of the pencil minimum-degree
test is exactly why it contributes no second-diagonal candidate.  The
arithmetic-only verifier proves (5q)--(5s), the six-type classification, the
Burnside counts, the sample census, the universal `4+4` pencil obstruction,
and this coarse survivor without enumerating the 97,224 extensions:

```console
python ai/omreal/verify_signed_circuit_filter.py
```

It remains to treat generic size-five supports.  For an ordered support
`Q={q_0,...,q_4}`, its circuit coefficients are

\[
 c_i=(-1)^i\det(a_{q_0},\ldots,\widehat{a_{q_i}},\ldots,a_{q_4})
     =u_i f_i.                                           \tag{5t}
\]

Here `u_i` is a signed parent-bracket unit and `f_i` is either `1` or one of
the residual derived-wall atoms.  If `k` of the five cofactors are residual,
the unit part of positivity imposes `max(0,4-k)` independent parity
equalities.  The `k=0` case is impossible for a realizable extension: an
aligned all-unit positive dependence would persist throughout the parent
realization chamber, including at a chart realizing that extension.

The complete generic size-five census is

| residual cofactors `k` | labeled supports | `S_8` orbits |
|---:|---:|---:|
| 0 | 370,552 | 24 |
| 1 | 485,520 | 25 |
| 2 | 567,840 | 30 |
| 3 | 433,440 | 21 |
| 4 | 30,240 | 6 |
| 5 | 134,400 | 11 |
| **total** | **2,021,992** | **117** |

Thus the universal signed structural filter retains `1,651,440` labeled
supports in `93` orbits.

There is a second reduction which retains the continuous Gordan weights but
quotients their inessential column-scaling freedom.  Let
`H=(Q_1,...,Q_t)` be any tuple of positive circuit supports.  In each block
choose `I_(j,0) in Q_j`, use the logarithmic weight-ratio coordinates

\[
        z_{j,I}=\log\frac{\lambda_{j,I}}{\lambda_{j,I_{j,0}}},
        \qquad I\in Q_j\setminus\{I_{j,0}\},
\]

and let `D_H` have row `1_I-1_(I_(j,0))` at coordinate `(j,I)`.  If the
eight parent columns are rescaled by `y_e -> exp(x_e)y_e`, then

\[
                 z\longmapsto z-D_Hx.                 \tag{5u}
\]

The diagonal column scaling acts trivially because every triple has size
three, so this is the effective positive column-torus action.  Consequently
the quotient of the relative interior of the product of weight simplexes has
dimension

\[
 \boxed{\quad
 \beta(H)=\sum_{j=1}^t(|Q_j|-1)-
              \operatorname{rank}_{\mathbb Q}(D_H).
 \quad}                                                \tag{5v}
\]

Changing a base triple performs an invertible row-coordinate change and does
not alter `beta`.  More strongly, every primitive integer vector
`m in ker(D_H^T)` gives the torus-invariant Laurent monomial

\[
       \prod_{j=1}^t\prod_{I\ne I_{j,0}}
       \left(\frac{\lambda_{j,I}}
                   {\lambda_{j,I_{j,0}}}\right)^{m_{j,I}},
                                                               \tag{5w}
\]

and an integer kernel basis gives all invariant weight moduli.  This is the
**weight-gauge theorem**.  It applies on each relative interior; when a weight
goes to zero, the corresponding simplex boundary is exactly a smaller-support
stratum and the same construction is repeated there.  Thus `beta=0` removes
all continuous weight ratios, while small positive `beta` leaves only that
many explicit invariant monomials for a later CAD.

The geometric payoff is that the remaining equations can be expressed on
fixed sparse tensors.  Let `T_Y:R^8 -> R^4` send `e_i` to the parent column
`y_i`.  After choosing the weight gauge, a circuit block is represented by

\[
       c=\sum_{I\in Q}\lambda_I\rho_I e_I\in\Lambda^3\mathbb R^8,
       \qquad \Lambda^3T_Y(c)=0.                       \tag{5x}
\]

Equivalently, the fixed sparse 3-vector `c` has zero image in the
four-dimensional quotient defined by `T_Y` (or, after dualizing, the
corresponding 3-form restricts trivially there).  For either surviving
structural four-support, the common hub gives `c=e_h wedge omega`.  Its edge
graph is `P4+P2` or `P3+2P2`.  Both forests have matching number three; with
all circuit coefficients nonzero, a matching Pfaffian minor is nonzero and no
larger one can occur, so the associated skew form `omega` has rank six.  Since
`T_Y(e_h)` is nonzero, (5x) says equivalently that the annihilator of
`ker(T_Y)+span(e_h)` is an isotropic three-plane for `omega` on the dual
space.  It is therefore an isotropic-Grassmannian incidence condition for a
fixed rank-six presymplectic form.  In general, the next exact decomposition
may work with a `beta`-parameter family of such fixed sparse-form loci instead
of the full product of weight simplexes.  The census below has `beta<=4`.
This is a dimension reduction for CAD, not a claim that those loci are
contractible.

For the third diagonal, this reduction can be made exact on every generic
single-piece stratum.  Omission and (5m-b) leave only five-supports which
cover all eight labels and have `delta<=2`.  Exhaustive `S_8` enumeration
gives

| generic single-support stage | labeled supports | `S_8` orbits |
|---|---:|---:|
| all generic five-supports | 2,021,992 | 117 |
| cover all eight labels | 1,099,560 | -- |
| retained after `delta<=2` | 760,200 | 45 |

Every retained support has at least one residual cofactor, so the all-unit
extension-sign obstruction removes no further case at this stage.  Of the 45
orbits, 44 have `beta=0` and one has `beta=1`; the latter is represented by

```text
156/456/137/347/128.
```

The modular rank used in the C++ census is exact.  Each centered incidence
row has squared norm at most six, so Hadamard bounds every minor of order at
most four by `36`, below the prime `65,521`.  A separate symbolic Python
implementation reconstructs the 52 wall types, computes rank over `Q`, and
reproduces every labeled and orbit count.  The exact checkers are

```console
g++ -O3 -std=c++17 ai/omreal/verify_third_diagonal_support_filter.cpp -o /tmp/verify_third_diagonal_support_filter
/tmp/verify_third_diagonal_support_filter
python ai/omreal/verify_third_diagonal_support_filter_independent.py
```

The unique beta-one type genuinely occurs.  On the exact row-2599
pattern-zero chart, a realizable proper signature has the positive circuit

```text
145/356/147/258/278
```

and its invariant modulus is

\[
                  \frac{\lambda_{147}\lambda_{258}}
                       {\lambda_{145}\lambda_{278}}.
\]

The arithmetic certificate is

```console
python ai/omreal/verify_third_diagonal_beta1_survivor.py
```

There is no sparse-stabilizer dimension obstruction among the 45 types.  At
the exact compatible pattern-zero tensors, their projective exact-tensor Lie
stabilizers induce at least eight of the nine parent tangent directions after
quotienting `GL(4)` and column scale.  Forty-three beta-zero types have rank
nine; the beta-one type and one beta-zero type have rank eight.  The looser
beta-one support-preserving algebra already surjects onto all nine tangent
directions.  Thus stabilizers may organize a later stratification, but tangent
rank alone is too nonselective to prove an escape or kill `H_c^2`.  The exact
45-orbit checker, tied to the audited census by a deterministic support-list
fingerprint, is

```console
python ai/omreal/verify_third_diagonal_sparse_stabilizers.py
```

For pairs, exhaustive stabilizer and Burnside counting gives `4,625`
pencil-rigid `4+5` support-pair orbits and
`4,696,412` pencil-rigid unordered `5+5` orbits before the all-unit rejection.
After that rejection, the exact `S_8` orbit counts, stratified by (5v), are

| support type | `beta=0` | `beta=1` | `beta=2` | `beta=3` | `beta=4` | total |
|---|---:|---:|---:|---:|---:|---:|
| `4+5`, `A=P4+P2` | 925 | 1,700 | 180 | 0 | 0 | 2,805 |
| `4+5`, `B=P3+2P2` | 494 | 876 | 83 | 2 | 0 | 1,455 |
| **all `4+5`** | **1,419** | **2,576** | **263** | **2** | **0** | **4,260** |
| **unordered `5+5`** | **0** | **3,364,191** | **441,089** | **5,529** | **3** | **3,810,812** |

Equal supports are allowed in the unordered `5+5` census.  In particular,
`beta>=1` is automatic for `5+5`, while every possible value `0,1,2,3`
occurs for `4+5`.  The rank calculation is exact modulo `65,521`: every row
of `D_H` has Euclidean norm at most `sqrt(6)`, so every square minor has
absolute value at most `6^4=1,296`, strictly below the modulus.

The census is not merely formal.  The row-2599 pattern-zero chart contains
the pencil-rigid positive `5+5` pair for signatures `0` and `4`

\[
  123/134/267/258/468,\qquad 123/256/127/357/478,
\]

whose nine-triple union has degree vector `(3,5,3,3,3,3,4,3)` and `beta=1`.
The pattern-four chart contains the pencil-rigid positive `4+5` pair for
signatures `3` and `7`

\[
  156/456/127/347/578,\qquad 134/235/238/368,
\]

with union degree vector `(3,3,5,3,4,3,3,3)` and `beta=0`; the second support
has type `A`.  The stored dependences are exact and support-minimal.  The
one-bit charts realize each signature while retaining a positive Gordan
witness against the other, proving that both pairs consist of proper,
incomparable feasibility regions.  The Python checker verifies the cofactor
census, prescribed-sign unit filters, and these two exact survivors:

```console
python ai/omreal/verify_signed_heavy_filter.py
```

The exhaustive pair-orbit and `beta` census is independently reproduced by

```console
g++ -O3 -std=c++17 ai/omreal/verify_signed_pencil_orbits.cpp -o /tmp/verify_signed_pencil_orbits
/tmp/verify_signed_pencil_orbits
```

The weight-gauge checker constructs primitive balanced exponent vectors for
(5w) on every exact positive pencil-rigid pair in all 256 row-2599 charts.  It
finds 65 occurrences (55 distinct support pairs): the three `4+5` occurrences
have `beta=0`, while the `5+5` occurrences split as 58 with `beta=1` and four
with `beta=2`.

```console
python ai/omreal/verify_gordan_weight_gauge.py
```

All three exact `4+5, beta=0` occurrences can in fact be removed from the
compact-component obstruction, including their zero-weight faces.  They form
two distinct signed tensor pairs.  After the full-support weight gauge, each
pair has an explicit non-diagonal one-parameter stabilizer; modulo column
scales it is a genuine projective shear, and its maximal interval in the
parent chirotope cell ends at a parent collision or another residence wall.
Every proper witness-support face of either pair is pencil-flexible, so the
projective-plane-pencil lemma supplies the same escape there.  Hence the full
closed intersections have `H_c^0=0`.  This is sample-specific: an exact
combinatorial `beta=0` pair with only the scalar projective stabilizer shows
that gauge rank alone cannot prove the universal statement.  The proof and
exact verifier are
[`BETA0_MIXED_ESCAPE.md`](BETA0_MIXED_ESCAPE.md) and
[`verify_beta0_mixed_escape.py`](verify_beta0_mixed_escape.py).

The associated Hilbert--Mumford boundary fan is also finite and exact.  For a
tuple of proposed limiting faces `F_j subset Q_j`, a column one-parameter
subgroup with those precise limits exists exactly when the rational system

\[
 \langle{\bf1}_I-{\bf1}_{I_j},u\rangle=0\ (I\in F_j),\qquad
 \langle{\bf1}_K-{\bf1}_{I_j},u\rangle>0\ (K\notin F_j)
                                                               \tag{5w-a}
\]

is feasible.  Gordan duality makes this a finite exact positive-circuit test.
For the displayed exact `5+5, beta=1` and `4+5, beta=0` residues there are,
respectively, `784` and `464` coherent proper face tuples, but **none** has a
pencil-rigid union.  The exact rational checker is

```console
python ai/omreal/verify_torus_escape_cones.py
```

This clean boundary behavior is not universal even in the stored exact
sample.  Among all 65 row-2599 pencil-rigid occurrences (55 distinct pairs),
`39` proper coherent faces on `28` distinct `5+5` pairs remain pencil-rigid;
none occurs on the two distinct stored `4+5` pairs.  One exact survivor and
its integer one-parameter subgroup are recorded in
`TORUS_TROPICAL_ESCAPE.md`.

This attractive boundary fact is not itself an escape proof.  Positive column
scaling changes homogeneous representatives of the same projective points, so
every such one-parameter subgroup projects to a constant point of `X`.  In
fact the lift of a bad locus is `B times R^7`, and compact supports are shifted
by seven degrees.  The column torus can therefore organize and prune a toric
compactification, but genuine escape directions must remain nonzero after
quotienting its valuation subspace.  `TORUS_TROPICAL_ESCAPE.md` proves this
vertical-torus no-go theorem, gives the exact face-cone LP criterion, and
reduces a viable next calculation to real-tropical cones in the nine parent
coordinates plus the `beta` invariant weight coordinates.  It also records
why one escaping branch per component cannot by itself kill `H_c^1`.

The retained `4,260+3,810,812` orbits have passed only a universal unary
signed filter.  For prescribed extension signatures one must still merge all
cofactor XOR equations with the rank-four chirotope Grassmann--Pluecker
clauses on the 56 derived normals.  That Boolean system is a necessary filter,
not a realization theorem for a parent chamber; exact survivors still require
the compact-component incidence calculation.  Residual-wall degenerations
and their lower-rank circuits are separate strata not included in this generic
census.

These cellwise vanishings are sufficient, not necessary: nonzero `E_1` terms
may cancel under the differentials in (5m), and the exact criterion is the
corresponding `E_infinity` group.  The value of the reduction is that all
unlisted cases vanish formally, while the survivors are a finite orbit list
of small triple hypergraphs.  Their generic five-circuit cofactors are
controlled by the 52 exact wall types; positive three- and four-circuits also
require their lower-minor degeneracy strata.  With the parent-contractibility
input of Section 4.2, the same compact-support spectral sequence computes
`H_c^(s-1)(B_S)` for every `1<=s<=9`; no extra compactification term is needed.
If Tsukamoto's contractibility statement is declined, (5g) remains the exact
fallback, and then the additional piece `S^9 minus X` is essential for
`s>=5`.  The independently proved parent vanishings above already justify
the bad-locus form through `s=4`.

### 4.5 An exact master-chamber reduction for the ninth diagonal

The last diagonal has a separate finite formulation which avoids computing
degree-eight compact-support cohomology.  Let `D` be the union in `X` of all
genuine residual derived walls, with labeled determinants sharing one
irreducible residual factor grouped as a single geometric wall.  Stratify it
semialgebraically so that the derived oriented matroid is constant on every
stratum.  Let `G_M` have one vertex for each connected full-dimensional
chamber of `X minus D`, joined across every connected generic codimension-one
wall stratum.  Label a chamber `C` by its supported signature set `T(C)`, and
write `G_M[S]` for the induced subgraph on `S subseteq T(C)`.

> **Master-chamber graph theorem.**  For every finite signature family `S`,
>
> \[
>                   \pi_0(F_S)\cong\pi_0(G_M[S]).       \tag{5y}
> \]

The missing local gluing premise is automatic.  At a generic residual wall,
a signature feasible in both adjacent chambers is feasible on the wall.  To
see this, suppose it has a support-minimal positive Gordan circuit there.
A five-circuit persists on both sides.  Structural three- and minimal
four-circuits also persist.  A nonstructural minimal four-circuit is an
ordinary residual wall circuit; a nonstructural three-circuit extends to a
localization residual four-set.  In the latter two cases the derived-wall
side theorem permits feasibility on at most one side.  Every case contradicts
two-sided feasibility.

The argument is pointwise, not only generic.  At an arbitrary multiwall
point, the global derived-wall rank theorem still turns a nonstructural
minimal four-circuit into an ordinary residual circuit.  A nonstructural
minimal three-circuit can still be padded by a nonstructural fourth triple.
That four-set is residual.  The fixed-unit identities for all nine ordinary
residual types have four nonzero relation coefficients everywhere on their
walls, so they cannot contain the zero-padded three-circuit; the exhaustive
support classification therefore makes the four-set one of the four
localization types.  The global side theorem then supplies a bad open sign
half-neighborhood, and the finite union of the other walls cannot fill that
half-neighborhood.  Hence every bad point is a limit of bad generic chambers.
Equivalently, the label of every interior cell in a regular semialgebraic
master refinement is the intersection of its locally incident chamber-germ
labels.  This **all-strata gluing theorem** removes separate interior
wall/node tope enumeration; it does not label compactification-boundary cells
and does not imply that the supporting chamber set is connected.  The full
proof and the necessary germ qualification are in
`NINTH_DIAGONAL_SAFE_GRAPH.md`.

The same labeled stratification gives a finite model for every diagonal, not
only components.  After a simultaneous semialgebraic compactification and
triangulation, the barycentric dual blocks whose incident chamber labels all
contain `S` form a complex `D_S` with `F_S homotopy equivalent to D_S`.  A
primal codimension-`j` simplex (or regular cell) contributes a dual `j`-cell.
For `s<=8`, the target `H_(9-s)(F_S)` uses only codimensions
`8-s,9-s,10-s`; diagonal eight needs the labeled chamber/wall/node complex
and diagonal seven adds codimension three.  Diagonal nine instead uses
codimensions zero and one with the augmented degree-zero boundary.  Label-safe
discrete-Morse matchings in positive target degree reduce the universal
all-`S` check to exact antichain-width tests in the dominance poset.  The
proof, infinity treatment, matching certificate format, and exact row-2599
codimension-two regression are in `DUAL_MASTER_CELL_PROGRAM.md`.

Every component of the open set `F_S` meets a full-dimensional chamber.  A
path in `F_S` can be perturbed to avoid codimension-two strata and cross the
generic walls transversely, giving a path in `G_M[S]`.  Conversely (generic)
two-sided gluing turns every graph edge into a local path in `F_S`, proving
(5y).

For `|S|=9`, disconnectedness is therefore an exact budget-nine path-hitting
problem on a finite labeled graph.  For chamber vertices `u,v`, restrict to
`E_(uv)=T(u) intersection T(v)` and choose nine signatures so that every
`u`--`v` path contains a chamber missing at least one chosen signature.  A
valid `DEHC(4,8)` counterexample must additionally certify that all nine
regions are proper and pairwise incomparable.  Exhaustive infeasibility with
those constraints for every pair and all 2,604 parents proves that diagonal.
Restricting to the globally minimal family `E(M)` tests only the weaker
reduced-core variant.  The chamber enumeration has not yet been performed.
The full proof, SAT formulation,
and an exact no-go theorem for replacing it by generic mutation connectivity
are in [`NINTH_DIAGONAL_SAFE_GRAPH.md`](NINTH_DIAGONAL_SAFE_GRAPH.md), with
finite checks in
[`verify_generic_wall_gluing_combinatorics.py`](verify_generic_wall_gluing_combinatorics.py)
and
[`verify_partial_mutation_fiber_disconnected.py`](verify_partial_mutation_fiber_disconnected.py).

There is now an exact adversarial stress test of this reduction.  For parent
2599, nine signatures appeared on the 178-chart sample to leave only charts
12 and 37 (the first three signatures already did so).  This is a genuine
9DVL input: seven exact witness charts distinguish all 72 ordered signature
pairs, using an integer extension ray for every feasible entry and a positive
integer Gordan circuit for every infeasible entry.  Hence all nine regions are
nonempty and proper and are globally pairwise incomparable.

Nevertheless the apparent separation is false.  An exact incidence-space
certificate joins charts 12 and 37 by 22,711 rational line segments.  Every
segment changes one of the 17 homogeneous columns, so every affected
determinant is affine and exact positivity at the two endpoints certifies the
whole segment.  The split is `11,701 + 3,009 + 8,001`; the middle bridge uses
common extension rays at consecutive one-parent-column moves.  The independent
verifiers are

```console
python ai/omreal/verify_ninth_candidate_antichain.py
python ai/omreal/verify_ninth_candidate_path.py
```

The universal reason this certificate format is complete is recorded in
[`NINTH_COORDINATE_PATH_THEOREM.md`](NINTH_COORDINATE_PATH_THEOREM.md).
Projection from the incidence space `Z_S` to `F_S` preserves path components
because its fibers are products of open convex extension cones.  Fixing every
column but one leaves an open convex polyhedral cone, and any path in the open
incidence space admits a finite one-column polygonal subdivision.  Rational
endpoints admit rational vertices, so integer endpoint determinants give an
exact certificate.  Equivalently, a chain of one-parent-column edges with a
common extension ray at both ends for every signature gives a path in `F_S`.

This is a complete language for certifying a proposed pair is connected, not
a coverage theorem.  The path proves only that the two displayed points lie
in one component; it does not show that their full `F_S` has no other
component.  The 2,604-parent catalog normally supplies only one realization
per parent and therefore does not contain the residual-wall roadmap needed to
run the finite master-graph test.  The ninth diagonal remains open.

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

### Proper subintersections do not control the diagonal

There is a sharper obstruction to induction on the number of regions.  Fix
`2<=s<=9`, put `d=s-1` and `c=10-s`, and work in
`R^d times R^c` with coordinates `(x,z)`.  Let

\[
 u_i=e_i\quad(1\le i\le d),\qquad
 u_s=-\sum_{i=1}^d e_i,
\]

and define closed bad sets and open feasible sets by

\[
 B_i=\{u_i\mathbin\cdot x\ge0,\ \|z\|\le1\},\qquad
 F_i=\mathbb R^{d+c}\setminus B_i.
\]

The `F_i` are proper and pairwise incomparable.  For every proper
`T subsetneq [s]`, the cone

\[
 C_T=\{x:u_i\mathbin\cdot x<0\text{ for all }i\in T\}
\]

is nonempty and convex, because the displayed `u_i` form a positive circuit.
Moreover

\[
 F_T=\{(x,z):x\in C_T\text{ or }\|z\|>1\}.
\]

Choosing `v_T in C_T` and moving `x` linearly to `v_T` contracts `F_T`.
For the full family, however, `C_[s]` is empty and

\[
 F_{[s]}=\mathbb R^d\times\{z:\|z\|>1\}
       \simeq S^{c-1}=S^{9-s}.
\]

Thus every proper intersection can be contractible while the full
intersection carries exactly the forbidden homology in each of the eight
unproved diagonal degrees.  This is not an oriented-matroid counterexample;
it proves that an induction using only the topology of proper subfamilies
cannot establish 9DVL.

The second diagonal survives even the common-row Gordan format.  Put
`X=R_x times R_z^8`, `r=||z||^2-1`, and use the five rows

\[
 A(x,z)=
 \begin{pmatrix}
 1&0&0&0\\
 0&1&0&0\\
 0&0&1&0\\
 0&0&0&1\\
 -1&x&r&0
 \end{pmatrix}.
\]

For `sigma=(+,+,+,+,+)` and `tau=(+,-,+,+,+)`, feasibility of the
correspondingly signed row systems is

\[
 F_\sigma=\{x>0\text{ or }\|z\|>1\},\qquad
 F_\tau=\{x<0\text{ or }\|z\|>1\}.
\]

Hence

\[
 F_\sigma\cap F_\tau
   =\mathbb R\times\{\|z\|>1\}\simeq S^7,
 \qquad
 B_\sigma\cap B_\tau=\{0\}\times\overline D^8.
\]

Both matrices have rank four, their private feasible fibers are convex, and
their normalized Gordan witness is unique wherever they are bad.  The compact
ball is exactly the first obstruction in (5h).  Therefore common rows,
reorientation of one row, convex private fibers, and unique sparse Gordan
witnesses still do not prove the second diagonal.  The compound identities
of the 56 parent-derived normals must exclude this trapped configuration.
The dual single-bad theorem (5h') later removes the formerly independent
single-region kernel, but it does not rule out this compact simultaneous-bad
model.

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

## 12. Exact derived-wall classification, regularity, and sides

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

Regularity can be strengthened to a global sign certificate for every tope
which the wall deletes.

> **Derived-wall side theorem.**  Fix one `UOM(4,8)` parent chirotope cell
> `X` and one labeled residual determinant `D_E`.  Every extension signature
> aligned with the circuit on `D_E=0` is infeasible on the wall and its
> feasible locus is contained in at most one of the two global sign sets
> `D_E>0` and `D_E<0`.  In particular, any extension tope deleted by this
> circuit at a generic crossing is globally one-sided.

**Proof.**  Write \(v_i=a_{I_i}\).  For residual types
`37,38,41,42,44,48,49,50,51`, there is an auxiliary derived normal `a_J` and
fixed nonzero coefficients `A_i` such that the five-vector determinant
identity specializes to

\[
             \sum_{i=1}^4 A_i v_i+D_E\,a_J=0.          \tag{27a}
\]

Here each `A_i` is, up to its alternating sign, a parent-bracket monomial.
Its sign is therefore constant on all of `X`.  If a signature `sigma` is
circuit-aligned, all \(A_i\sigma_{I_i}\) have one common sign `epsilon`.  For
a column `p` realizing `sigma`, the first term of (27a), evaluated on `p`,
has strict sign `epsilon`.  The identity forces

\[
                 \operatorname{sign}D_E=-\epsilon\sigma_J.       \tag{27b}
\]

At `D_E=0` it instead gives a positive signed dependence, so no such `p`
exists.

The four exceptional residual types `36,39,46,47` have a localization
certificate.  Write `E=C union {J}` with
`C=(I_1,I_2,I_3)`.  There is an auxiliary normal `a_K` for which
`D_(C union {K})` vanishes structurally, while the three replacement
cofactors are fixed nonzero parent-bracket monomials.  The same identity is

\[
             \sum_{i=1}^3 A_i a_{I_i}+D_E\,a_K=0.      \tag{27c}
\]

Circuit alignment on `C` now forces
`sign(D_E)=-epsilon sigma_K`, and again makes the wall itself infeasible.
On the wall, Section 12's rank-three result makes `E` an exact four-circuit
in the first case.  In the localization case (27c) makes `C` rank two, while
`E` still has rank three, so `C` is an exact three-circuit.  Thus any loss
caused by this circuit at a generic point of the irreducible residual
hypersurface obeys the asserted global side constraint.  The identities do
not assert that the signature is feasible anywhere on the allowed side.
QED.

The exact verifier

```console
python ai/omreal/verify_derived_wall_sides.py
```

checks the universal five-vector identity and exhausts all 84,840 labeled
residual four-sets.  Fixed four-row certificates cover 55,440 of them; the
four localization templates cover the remaining 29,400.  It imports the
exact symbolic wall classification, verifies all replacement types, and uses
no floating point.

This suggests a precise route to the ninth diagonal.  Cut `X` into
full-dimensional master chambers by all residual walls, and let `G` be their
adjacency graph.  Suppose that `G` is a partial cube and that each geometric
residual hypersurface is exactly one Djoković--Winkler equivalence class of
edges, with its two semicubes equal to its two signs.  Here labeled
determinants which differ by a fixed unit or share one residual factor are
grouped as one geometric wall.  Suppose also that every support change across
a generic boundary edge is caused by its displayed wall circuit.  The side
theorem then puts every chamber supporting a fixed signature in one semicube
at each of its boundary edges.  A geodesic between two supporting chambers
cannot leave this set: it would have to cross the same equivalence class
twice.  Thus each signature's support chambers, and every intersection of
such supports, form a convex subgraph.  If common supporting chambers glue
through their safe codimension-one strata, every nonempty `F_S` is connected.
These three global premises would prove the `s=9` entry of 9DVL.

The partial-cube premise is new and is not implied by the familiar theorem
that the tope graph of one fixed oriented matroid is a partial cube: `G` is a
graph of varying compound arrangements.  For the `s=8` and `s=7` entries,
even graph convexity controls only `H_0`; one would need a contractible
COM-like dual two- or three-complex, or exact boundary-rank certificates.

Even the mutation graph of varying chirotopes does not supply the premise.
The dependency-free checker
[`verify_mutation_graph_not_partial_cube.py`](verify_mutation_graph_not_partial_cube.py)
enumerates the 384 signed uniform rank-three chirotopes on five labeled
elements and their 960 one-basis mutations.  Both global signs are retained,
as they are in a determinant-wall chamber graph.  The checker gives three
explicit edges for which the Djoković--Winkler relation is nontransitive, so
this mutation graph is not a partial cube.  A transparent subcertificate
consists of two realizable chirotopes whose basis-sign Hamming distance is
three but whose mutation distance is five.  Six exact integer matrices realize
the displayed length-five path.  This sharply distinguishes a fixed oriented
matroid's tope graph from a graph in which the chirotope itself varies.  It does **not**
give a counterexample inside one fixed `UOM(4,8)` parent cell: the compound
image of that cell is a much more restricted induced family.  Consequently
the fixed-cell partial-cube question remains an exact additional conjecture,
not a consequence of a general mutation theorem.

There is a second exact reduction, but it also stops short of a COM theorem.
In the normalization (25), twelve of the thirteen residual orbit types are
signed bracket binomials

\[
             q_E=[A_E][B_E]-[C_E][D_E]                 \tag{27d}
\]

up to an overall sign, with the following representatives:

| residual type | bracket binomial |
|---:|---|
| 36 | `[1245][2367]-[1234][1367]` |
| 37 | `[1234][1567]-[1245][2567]` |
| 38 | `[1234][1678]-[1245][2678]` |
| 39 | `[1234][3678]-[1236][3578]` |
| 41 | `[1234][3567]-[1257][3456]` |
| 42 | `[1356][2478]-[1478][2356]` |
| 44 | `[1234][5678]-[1256][3578]` |
| 46, 47 | `[1245][1367]-[1234][1267]` |
| 48 | `[1234][1356]-[1246][2356]` |
| 49 | `[1234][1357]-[1246][2357]` |
| 50 | `[1246][2378]-[1234][1378]` |

The dependency-free symbolic checker
[`verify_residual_log_binomials.py`](verify_residual_log_binomials.py)
verifies all twelve identities over `ZZ`.  It also exhausts all products of
two of the 70 parent brackets and proves that residual type 51 has no such
two-product representation, even up to sign.  On a fixed projective-frame
slice of one parent cell, put `ell_B=log|[B]|`.  Every wall in (27d) is the
pullback of the affine hyperplane

\[
               \ell_{A_E}+\ell_{B_E}
                 -\ell_{C_E}-\ell_{D_E}=0.             \tag{27e}
\]

The remaining type instead has the exact trinomial identity

\[
 q_{51}=[1236][4678]-[1267][2468]-[1367][2468].       \tag{27f}
\]

Thus the twelve binomial types inherit an ambient hyperplane arrangement in
log-bracket space.  The missing hypothesis is again the restriction locus:
the log-bracket image of `X` is not convex.  The exact checker
[`verify_log_plucker_nonconvex.py`](verify_log_plucker_nonconvex.py) uses two
integer row-2599 charts and shows that their coordinatewise logarithmic
midpoint violates one three-term Pluecker relation.  The radical inequality
is reduced to an unequal pair of explicit integers, and its failure is
unchanged by positive column rescaling or a common row-basis determinant.
Consequently convexity fails even in the projective log-bracket quotient.
This rules out applying the standard convex-restriction COM construction to
(27e); it does not rule out the weaker possibility that the image is
arrangement-convex.  On each fixed sign cell, (27f) makes the type-51 wall an
equality of one exponential with a sum of two exponentials, hence a
log-sum-exp hypersurface rather than a hyperplane.  It therefore does not
restore the missing COM premise.

These theorems still do not settle multiple-wall topology.  Even global
one-sidedness of every labeled wall is insufficient.  In
`R^9=R_(x,y) times R_z^7`, put

\[
 q_1=y,\qquad q_2=(x^2-1)(x^2-4)-y,\qquad
 q_{2+j}=z_j\quad(1\le j\le7),
\]

and `F_i={q_i>0}`.  Every zero wall is a globally cooriented smooth graph
with a nonzero pivot derivative, and all nine regions are proper and pairwise
incomparable.  Nevertheless

\[
 \bigcap_{i=1}^9F_i
 =\{0<y<(x^2-1)(x^2-4),\ z_j>0\},
\]

which has three components (`x<-2`, `|x|<1`, and `x>2`).  Thus the remaining
Extension--Helly problem is genuinely the global partial-cube/gatedness or
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
integer positions `L,R` of the deleted column that both realize `M` and both
support an extension signature `sigma_2`.  The projective midpoint
`Q=L+R` still realizes `M`, but a positive Gordan dependence makes `sigma_2`
infeasible there.

This example lies in one fiber of the contraction used in Section 4.1.  Put
`p=L-R`.  Exact brackets show that `p` realizes one uniform signature
`sigma_1` over all three parent charts.  Modulo the line spanned by `p`,

\[
                       L=R+p,\qquad Q=2R+p.
\]

Thus the endpoints and midpoint have one identical contraction by `p`; after
the harmless positive scaling `Q/2`, the third lift is literally the affine
midpoint of the first two.  Two further exact charts give
`F_(sigma_1) minus F_(sigma_2)` and
`F_(sigma_2) minus F_(sigma_1)`, so both regions are proper and incomparable.

> **Same-contraction nonconvexity proposition.**  For a realizable
> `UOM(4,8)` parent there are proper incomparable signatures
> `sigma_1,sigma_2` such that, inside one convex contraction-height fiber for
> `sigma_1`, feasibility of `sigma_2` is nonconvex.

```console
python ai/omreal/verify_seeat_residence_nonconvex.py
```

Consequently the attractive decomposition `9=6+3` does not turn the desired
bound into ordinary convex Helly on a six-dimensional deletion base and a
three-dimensional residence fiber, and the contraction--height proof cannot
simply be iterated for `s=2`.  Strong Euclideanness of the abstract
seven-element deletion does not repair this missing real-geometric
convexity.  Any deletion-based proof must control the topology of these
nonconvex fiber regions rather than assume it away.  This is an obstruction
to a strategy, not a counterexample to 9DVL.

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

## 13. Post-atlas diagonal refinements

Several later exact results sharpen the open diagonal program without changing
the honest score of one proved entry.

First, every pencil-rigid union of two cofinal five-supports has global minimum
partner defect `d(U)` equal to one or two.  If `d(U)=2`, a degree-three label
has the matching star `eab/ecd/efg`.  `SECOND_DIAGONAL_DEFECT_TWO.md` gives an
exact parent-16 realization of that second case for two realizable proper
incomparable signatures, together with reciprocal Gordan witnesses.  The
displayed pair escapes to the parent wall `[1678]=0`, but the example proves
that the row-2599 one-defect pattern was not universal.

This is a dichotomy for the global minimum, not for an arbitrarily selected
degree-three label.  `SECOND_DIAGONAL_MATCHING_STAR_LOCAL_NO_GO.md` gives an
exact global-defect-one pair with a local matching star whose twelve oriented
partner rays all meet a chosen-circuit cofactor wall first.  Its first useful
support drop is pencil-flexible and escapes, so the example blocks only a
root-free frozen-support shortcut and is neither a global-defect-two example
nor a 9DVL obstruction.

`DIAG2_MOVING_WITNESS_SHEAR.md` removes this frozen-support failure whenever
the two witnesses pass an exact signed compatibility test.  Under a column
shear `g_t`, transport each signed Gordan three-form by
`Lambda^3(g_t^(-1))`.  Functoriality preserves its kernel identity, and the
test makes every newly generated replacement-triple coefficient
nonnegative in the prescribed signature orthant.  The resulting ray remains
simultaneous-bad until the first parent wall, or tends to a parallel-column
boundary at infinity, so its entire component is noncompact.  The low-source
count forces some ordered shear to have at most two colored sources.  All 65
stored row-2599 hard occurrences and the parent-16 defect-two pair admit
compatible shears, but an arbitrary-signing canary does not.  The remaining
problem is to derive compatibility from realizable oriented-matroid extension
constraints at every point, rather than from unsigned supports alone.

Second, the entire single-piece column for diagonal three vanishes:

\[
 H_c^q(C_{\rho,Q};\mathbb Q)=0
 \qquad(0\le q\le2,\ |Q|\le5).                       \tag{34}
\]

For a cover-all support, a degree-one label moves in its two-dimensional
support plane and a second light label moves in a one-dimensional
support-plane pencil.  The resulting three-dimensional fibers have convex
two-dimensional sections, hence contractible components and no
compact-support cohomology below degree three.  The proof includes structural
supports, residual-wall degenerations, and zero-weight faces.  The exact
45-orbit audit consequently refines to `45 -> 7 -> 0`; see
`THREE_SHEAR_SINGLE_PIECE_REDUCTION.md`.  Pair `H_c^1` and triple `H_c^0`
terms remain open.

Third, a sampled ninth-diagonal separator has been refuted exactly.  The two
row-2599 upper-bound charts numbered 12 and 37 are connected inside the
common feasibility locus of the nine stress signatures by 22,711 rational
one-column segments.  Every constrained determinant is affine on each
segment, so exact positive endpoint signs certify the full path.  Run

```console
python ai/omreal/verify_ninth_candidate_path.py
```

against `data/ninth_candidate_12_37_path.npz`.  This is a regression theorem
for the master-chamber search, not a proof of global ninth-diagonal
connectivity.

A tempting extension of (34) to `H_c^3` is deliberately not claimed.  A
third light-label pencil makes the identity fiber component escape, but the
top direct-image row is a constructible orientation/component sheaf.  Fiber
components can in principle merge or disappear, so ordinary noncompactness
of the quotient base does not by itself kill compactly supported sections.
The exact split--remerge model

\[
 A=\{(t,x)\in\mathbb R^2:t^2+x^2>1\},\qquad
 \Omega=A\times\mathbb R^2\longrightarrow\mathbb R_t
\]

makes the gap sharp.  Every fiber component is a contractible oriented open
three-manifold.  The fiber is connected for `|t|>1` and has two components
for `|t|<=1`; both branches merge and escape on both sides.  Nevertheless
the doubled interval `[-1,1]` carries a compact anti-diagonal section of
`R^3 pi_! Q`, and

\[
 H_c^3(\Omega;\mathbb Q)=H_c^1(A;\mathbb Q)=\mathbb Q.
\]

Thus noncompact component trajectories are insufficient: one must rule out
split--remerge cycles or compute the top-sheaf differential.  The safe
fourth-degree upgrade is exactly (5n-a), where one omitted column gives a
three-dimensional convex block and one light pencil gives a scalar base;
each full four-parameter fiber component retracts to an interval.  Its
all-support incidence audit is
[`verify_fourth_single_piece_light_count.py`](verify_fourth_single_piece_light_count.py).

Finally, the standard nine free coordinates do not restore ordinary
convexity after taking logarithms.  The exact checker
[`verify_free_log_nonconvex.py`](verify_free_log_nonconvex.py) gives two
row-2599 certificates.  Charts 0 and 3 have a free-log midpoint crossing the
parent bracket `[5678]`.  Charts 77 and 85 give the stronger relative failure:
their midpoint retains all 70 strict parent signs but crosses from `q_44>0`
to `q_44<0`.  Hence neither a convex parent domain nor convex residual sides
can be assumed in a second-diagonal KKT argument.

The precise weaker result is recorded in
[`FREE_LOG_COORDINATE_OBSTRUCTION.md`](FREE_LOG_COORDINATE_OBSTRUCTION.md).
Every parent cell has interval coordinate-line sections in the free-log
variables; the twelve residual types other than 51 inherit this property in
every coordinate, and type 51 has it along its certified pivot `f`.  This is
orthogonal, not ordinary, convexity.  If a full-dimensional residual sign
chamber has compact closure in the parent cell, the product of its positive
defining functions vanishes on its boundary and has an interior maximum.
Thus at some point

\[
              0=\sum_j \nabla f_j/f_j.               \tag{35}
\]

Equation (35) is a sound finite signed-gradient obstruction: full column rank
excludes it for at most nine walls, while a ten-wall rank-nine matrix must have
a strictly positive kernel.  It remains only a filter on generic `5+5`
chambers.  It neither controls their lower-dimensional boundary incidence nor
proves the compact-component differential injective, so diagonal two remains
open.

## 14. Block-Gordan and graph-certificate audit

The block-Gordan idea has a clean functorial formulation, but its exact audit
shows where the real topology remains.  Let

\[
 \Gamma_S=\left\{(Y,(w_\sigma)_{\sigma\in S}):
 A_\sigma(Y)^Tw_\sigma=0,quad w_\sigma\ge0,quad
 \sum_{\sigma,i}(w_\sigma)_i=1\right\},            \tag{36}
\]

allowing an entire block `w_sigma` to be zero.  Its image is
`B_S=union_(sigma in S)B_sigma`.  Over `Y`, the fiber is the join, in
disjoint coordinate blocks, of the nonempty normalized witness polytopes
`P_sigma(Y)`.  Hence the projection is proper with compact convex fibers,
and proper base change gives, functorially under zero-padding,

\[
             R\Gamma_c(\Gamma_S;R)\simeq R\Gamma_c(B_S;R)     \tag{37}
\]

for every coefficient ring `R`.

This does not bypass compact-support Mayer--Vietoris.  On the stratum where
exactly the blocks in nonempty `T subseteq S` have positive mass,

\[
 \Gamma_T^\circ\cong
 \operatorname{relint}\Delta^{|T|-1}\times\widehat\Gamma_T,
 \qquad
 \widehat\Gamma_T\longrightarrow\bigcap_{\sigma\in T}B_\sigma
                                                                    \tag{38}
\]

has product-convex proper fibers.  The block-mass filtration therefore
reconstructs the compact-support Mayer--Vietoris spectral sequence exactly.
Fixed-fiber shellability leaves the split--remerge and restriction maps
untouched.  The exact systems in `BLOCK_GORDAN_FORMAL_NO_GO.py` make this
limitation sharp for every `s=3,...,8`: all rows are nonzero and span
`R^4`, all normalized bad fibers are singletons, and the feasibility
regions are proper and pairwise incomparable, yet the required
`H_c^(s-1)` is nonzero.  The special third-compound/Koszul relations are
therefore essential.

For the actual hard row-2599 triple, a coordinated pivot does exist.  Its
three one-exchange positive-circuit polytopes have `52/34/52` vertices.
Exactly `18,480` of their `91,936` product corners are pencil-flexible,
and all require changing all three blocks.  Three certified polytope edges
form a local cube whose far support has degree vector
`(2,5,5,5,4,4,5,3)`, so its corresponding piece has no compact component
by the pencil lemma.  This supplies a concrete cell for a future coordinated
cubical matching, but wall compatibility, zero faces, and infinity remain;
diagonal three is not proved.

The same cube has now been continued exactly through its far corner.  A
common pencil of the parent column `y_1` preserves every active circuit until
the unique first parent wall `[1467]=0`, so the simultaneous-bad component
through the selected pattern is noncompact over every coefficient ring.  The
full cofactor audit has 30 occurrences and 27 distinct walls: eight unit, 19
residual, with three shared edge-collapse walls and 16 endpoint-specific
walls.  Across residual orbit 50, an exact same-parent chart retains the
chosen `R_4` circuit but kills `Q_4`.  Thus this local cube cannot be copied
unchanged across all walls; a global matching needs circuit-elimination
reroutes.  See
[`BLOCK_GORDAN_TRIPLE_WALL_AUDIT.md`](BLOCK_GORDAN_TRIPLE_WALL_AUDIT.md).

The first such reroute is now exact.  A one-column-7 segment crosses that
orbit-50 wall once while the fixed circuits `R_0`, `R_4`, and the structural
`C_3` remain strictly positive by exact Bernstein certificates.  The bit-four
face changes

\[
                  Q_4R_4\longrightarrow PR_4\longrightarrow S_4R_4,
                                                                  \tag{38a}
\]

where `P` is the shared zero-weight four-circuit.  The transported support
union has degrees `(2,5,4,5,4,3,6,4)`; label 1 occurs only in `134` and `127`,
so the same pencil escape persists.  Thus the original product cube connects
fiberwise to a persistent triple across its hard endpoint wall.  This resolves
one local component, not the remaining pair and triple spectral-sequence
terms.  See
[`BLOCK_GORDAN_ENDPOINT_WALL_REROUTE.md`](BLOCK_GORDAN_ENDPOINT_WALL_REROUTE.md).

There is also an exact strict five-circuit carrier chart.  Scaling the five
signed support normals by their unique positive relation puts them at a
labeled projective frame; a label of support degree `d_e` then contributes
projective carrier dimension `3-d_e`, totaling nine dimensions.  The rays
are oriented modulo one simultaneous antipode, not independently unoriented.
This is a quotient chart, not a dimension reduction, and it degenerates on
zero-weight faces.  An exact hard-support midpoint stays uniform and keeps
all five cofactors positive while flipping four parent brackets.  Hence the
natural carrier sign chamber is nonconvex and need not be an affine orthant.
See [`BLOCK_GORDAN_CARRIER_CHART.md`](BLOCK_GORDAN_CARRIER_CHART.md).

The fixed extension-point arrangement nevertheless has a classical exact
description.  If `G` is a Gale dual of the uniform rank-four parent `Y`, each
complementary Gale five-circuit has coefficient vector `Y^Tq`, with `q`
proportional to the derived normal `a_I`.  Hence the 56 triple hyperplanes are
linearly the essential discriminantal arrangement `B(8,4,G)`.  Its fixed-`Y`
tope complex is zonotopal and shellable and its graph is a partial cube.

This does not identify the parent residual-wall complex: varying `Y` changes
the discriminantal oriented matroid precisely at the 13 residual types.  The
exact row-2599 audit rejects all `8!` cyclic label orders even after
reorientation, so the cyclic higher-Bruhat theorem does not apply; moreover,
the canonical four-packet wall belongs to bracket-unit orbit 9 rather than a
residual orbit.  The useful replacement is a constructible diagram of
chamberwise zonotopes with explicit 13-type mutation maps and codimension-two
coherence.  The reroute (38a) is its first certified transition.  See
[`BLOCK_GORDAN_DISCRIMINANTAL_AUDIT.md`](BLOCK_GORDAN_DISCRIMINANTAL_AUDIT.md).

The codimension-one specialization itself is now uniform.  The 13 residual
types split into nine ordinary four-circuit walls and four localization
three-circuit walls, each with a fixed-unit support-drop identity.  On a
circuit-aligned support, the normalized positive kernel is a singleton on its
live side, specializes to the same singleton with one zero coordinate on the
wall, and is empty on the other side.  Thus the live-side-to-wall map is
canonical and integral for every type.  A direct cross-wall quasi-isomorphism
cannot be natural on all zero-weight coordinate faces: the corresponding
`H_0` diagram has ranks `Z -> Z -> 0`, so naturality would kill the live
generator.  The universal object must be the specialization cospan
`side -> wall <- side`, filled by enlarged circuit-elimination cells.
Equation (38a) is exactly the first such filling.  See
[`BLOCK_GORDAN_RESIDUAL_MUTATION_MAP_NO_GO.md`](BLOCK_GORDAN_RESIDUAL_MUTATION_MAP_NO_GO.md).

There is now a universal filling whenever an opposite-side auxiliary pair is
present.  Let `P` be the positive wall circuit and let `u,v` be certified
auxiliaries born on opposite sides.  Since `cone(P)=span(P)`, positive
circuit elimination produces a support-minimal circuit `R` containing both
`u,v` and persisting across the wall.  The normalized closed fibers are

\[
             [Q_-,R]\longrightarrow[P,R]\longleftarrow[Q_+,R],
                                                               \tag{38b}
\]

with at most six normals at an ordinary wall and five at a localization
wall.  Both arrows are integral cellular isomorphisms; their mapping cones
have only unit Smith invariants.  The exact 13-type representative census
contains 131 certified auxiliaries, 671 unordered pairs, and 2,420 generic
persistent-support candidates.  See
[`BLOCK_GORDAN_RESIDUAL_ELIMINATION_CELLS.md`](BLOCK_GORDAN_RESIDUAL_ELIMINATION_CELLS.md).

Once the codimension-one maps in (38b) are actually defined facewise on a
common subdivision, there is no further higher-codimension homological
obstruction.  At a node, the union of the coordinates used by competing
image chains is a nonempty convex coordinate face of the normalized
block-Gordan polytope.  The relative acyclic-carrier theorem gives an
integral chain homotopy, and the same induction supplies all higher coherent
homotopies.  The exact row-2599 transverse node passes this test.  The only
remaining same-block failure is already codimension one: a prescribed
signature may have a monochromatic wall star, so every available auxiliary
lives on the bad side and no opposite-side interval (38b) is defined.  See
[`BLOCK_GORDAN_ALL_CODIM_COHERENCE.md`](BLOCK_GORDAN_ALL_CODIM_COHERENCE.md).

That monochromatic case occurs in the actual third-compound geometry.  Exact
uniform rational examples realize it at all 13 residual types.  At a genuine
loss, Gordan's alternative proves that no positive circuit of any support can
persist in the same signature block on the feasible side, so searching
non-unit auxiliaries cannot repair it.  There is a universal local pair
escape: two supports `P union {u}` and `P union {v}` based on one wall
circuit contain at most six derived triples, hence at most 18 parent-label
incidences; some one of the eight labels has degree at most two.  The
plane-pencil lemma therefore removes every same-wall pair piece.  The global
pair column can still loop through unrelated circuits and different walls.
Moreover, an exact strict three-block row-2599 corner is pencil-rigid with
degree vector `(4,4,6,4,5,5,3,5)`, so the triple analogue is false.  What
remains cannot be handled by a same-block pivot.  See
[`BLOCK_GORDAN_MONOCHROMATIC_WALL_STARS.md`](BLOCK_GORDAN_MONOCHROMATIC_WALL_STARS.md).

The joined block resolution gives the missing local transfer in two broad
cases.  If another signature block is bad on the receiving side, scale all
dying blocks to zero while adding their total mass to one normalized witness
in that receiving block.  This formula includes zero block-mass faces.  If
all blocks die but share one labeled positive wall circuit `P`, first retarget
each block inside its convex wall fiber to `P`.  Its three or four derived
normals have at most 12 parent-label incidences, so one label has degree at
most one and supplies a common proper pencil escape.

An exact proper pairwise-incomparable row-2599 triple realizes the genuinely
receiver-free case.  All three blocks share the localization wall circuit
`123/356/348`, which omits label 7, and the augmented local simplex incidence
is integrally acyclic.  Thus that hard all-die star is closed.  The theorem
is not universal over a global factor: different dying blocks may use
different labeled circuits among its multiplicity-`1/2/15/65` occurrences,
whose union need not have a light label.  The remaining local target is a
multi-circuit all-die escape; the remaining global target is a proper,
acyclic mass-transfer matching.  See
[`BLOCK_GORDAN_MONOCHROMATIC_MASS_TRANSFER.md`](BLOCK_GORDAN_MONOCHROMATIC_MASS_TRANSFER.md).

For diagonal two, the same audit rules out a vertical Bland matching.  Such a
matching retains one degree-zero critical fiber generator and merely
reconstructs the bad-locus indicator sheaf.  The support nerve is also too
coarse: two exact rational plane covers with the same two-vertex, one-edge
nerve have compact-support first-cohomology ranks one and zero.  In the
genuine proper incomparable parent-16 defect-two pair, the first candidate
pivot wall occurs at

\[
                         t=541589/6442906.             \tag{39}
\]

The support `123` becomes a positive four-circuit there.  All 52 cofinal
paddings paired with the other circuit remain pencil-rigid of defect two; the
exact fan has 45 incoming, three outgoing (`126,238,478`), and four
rank-three degenerate (`145--148`) faces.  Every alternative triple row
retains an unpruned competitor.  Thus a viable finite proof object must
decorate the signed wall graph with compact intersection components and
their restriction/split--merge maps.  See
`DIAG2_PIVOT_BLOCK_GORDAN_NO_GO.md`.

With those component decorations, the local algebra becomes sharp.  At every
first residual support drop, the 51-spoke integral wall-star matrix is
injective for every compactness decoration except the extreme one in which
the central component and all 51 spoke components are compact; only that case
retains a one-dimensional transfer kernel.  A spoke is flexible exactly when
the union of its four- and five-supports is pencil-flexible.  At the exact
parent-16 defect-two wall, the central component escapes by a certified
two-stage path and every spoke is noncompact or supplies a private unit row,
so the component-decorated matrix is unimodular.  The exhaustive residual
support census leaves 112,041 symmetry orbits after the unary signed/all-unit
rejection, split by weight-gauge beta as `77,649/33,453/938/1`.  These are
only support-level upper bounds; the universal task is now to exclude the
extreme all-compact decoration on the realizable subfamily.  See
[`DIAG2_PIVOT_COMPONENT_GRAPH.md`](DIAG2_PIVOT_COMPONENT_GRAPH.md) and
[`DIAG2_PIVOT_UNIVERSAL_WALL_THEOREM.md`](DIAG2_PIVOT_UNIVERSAL_WALL_THEOREM.md).

The extreme decoration cannot be killed by completing the first-wall carrier.
With all 52 paddings, every pair of padding vertices supplies a triple row,
so the full integral matrix is the oriented incidence matrix of `K_52`.  It
has rank 51 and primitive kernel `Z(1,...,1)`; higher cofinal containments
only impose the corresponding simplex identities.  An exact transverse-plane
model realizes these local compactness axioms, showing that an Euler or Smith
normal-form refinement at one wall is logically insufficient.

There is, however, a canonical second-wall theorem.  Every residual type has
a normalized pivot coordinate in which its incoming cofactor is affine with
constant nonzero parent-bracket slope, while the parent fiber is an interval.
Continue a strict spoke away from its first cofactor root into the globally
bad side.  That cofactor cannot recur.  If the spoke component is compact, it
must therefore hit a different circuit cofactor before the path reaches the
parent boundary; the new zero is again one of the 13 residual wall types.
There are 30--52 strict paddings at every first wall.  Thus an all-compact
star forces at least 30 labeled second-wall incidences, and the remaining
problem is global acyclicity of the iterated signed wall graph.  See
[`DIAG2_PIVOT_ALL_COMPACT_SECOND_WALL.md`](DIAG2_PIVOT_ALL_COMPACT_SECOND_WALL.md).

Neither the light-label count nor a one-coordinate Bland order supplies that
acyclicity.  For every residual type, an exact pencil-rigid partner has a
degree-one partner label which occurs two or three times in the first wall
support.  In type 51 the resulting two-parameter wall restriction is a real
ellipse.  Nineteen parent-bracket walls cut the displayed oval transversely
into noncompact arcs, so it is not a compact component in one parent cell;
the point is that dimension minus one does not force a linear escape, and the
cutting has not been proved universally.  A separate exact uniform chart has
two residual walls whose canonical pivots form the directed label cycle
`44 -> 37 -> 44`: entering the bad side of either wall decreases the other
bad-side sign.  Thus acquired signs need not grow under successive scalar
pivots.  A universal continuation must use a multi-coordinate cone rule or
exclude closed realizable transition cycles directly.

The first-order multi-coordinate problem is exactly a Gordan alternative.
After restricting the signed residual gradients to the tangent space that
preserves all active lower-support witnesses, either they admit a common
strict direction or they have a finite nonnegative Farkas dependence.  The
strict alternative genuinely fails: an exact proper incomparable pair on
the coincident type-46/type-47 localization wall has signed gradients `g`
and `-g`.  Both signatures are excluded on the wall by the same positive
three-circuit.  That circuit omits label 8, and an exact tangent motion of
label 8 preserves it until the parent bracket `[5678]` vanishes.  Thus the
smallest realizable Farkas obstruction escapes, but no global stratified
termination theorem follows.  See
[`DIAG2_PIVOT_CONE_FARKAS.md`](DIAG2_PIVOT_CONE_FARKAS.md).

The pair classification is now almost complete even with arbitrary relative
labels.  The `84,840` occurrences localize to `26,740` factors in six `S_8`
orbits and `9,476` unordered distinct factor-pair orbits.  Exhaustive
projective reframing gives a bracket-product `2 by 2` minor for `9,226`;
common affine translations and weighted tori certify 128 more.  Exact
critical-ideal saturation and a fiber-linear escape certify the seven
type-`(49,49)` cases.  Hence every pair-wall component is noncompact for
`9,361` orbits, with an honest 115-orbit residue in factor families 49--51.
The earlier 66 pairs among 12 canonical formulas are a subtable.  Among the
220 canonical triples, 170
have a direct bracket-product `3 by 3` minor and `(36,38,42)`
has a two-minor sequential saturation certificate.  Four triples have exact
uniform rank-two witnesses: `(37,41,46)`, `(37,46,49)`, `(39,48,50)`, and
`(41,46,49)`.  The other 45 remain unclassified.  Rank drop alone does not
determine the sign of the unique dependence.  Three displayed witnesses do
not lie in all three Farkas-oriented halfspaces.  The common triple-wall case
`(39,48,50)` has positive relation
`dq39+3dq48+2dq50=0`, but an exact tangent segment preserves all three
positive wall circuits and reaches the parent wall `[2478]=0`.  The
triple certificates do not cover relative labeled `S_8` overlaps.  See
[`DIAG2_PIVOT_LABELED_PAIR_THEOREM.md`](DIAG2_PIVOT_LABELED_PAIR_THEOREM.md),
[`DIAG2_PIVOT_49_PAIR_SATURATION.md`](DIAG2_PIVOT_49_PAIR_SATURATION.md),
[`DIAG2_PIVOT_REPRESENTATIVE_GRADIENTS.md`](DIAG2_PIVOT_REPRESENTATIVE_GRADIENTS.md),
[`DIAG2_PIVOT_REPRESENTATIVE_TRIPLES.md`](DIAG2_PIVOT_REPRESENTATIVE_TRIPLES.md),
and [`DIAG2_PIVOT_REPRESENTATIVE_TRIPLE_FARKAS.md`](DIAG2_PIVOT_REPRESENTATIVE_TRIPLE_FARKAS.md).

The ninth-diagonal combinatorial layer is now proof-complete once a genuine
labeled chamber roadmap is supplied.  For a spanning tree and vertices
`u,v`, put `E_uv=T(u) intersection T(v)`.  Along their tree path, whenever
a waypoint `w` misses `d in E_uv`, require

\[
                  \operatorname{width}(E_{uv}\cap\operatorname{Inc}(d))
                  \le7.                              \tag{40}
\]

Dilworth's theorem then prevents the other eight members of a proper
nine-antichain from all lying in that incomparable set, so every
nine-antichain support graph is connected.  The exact cut-SAT encoding in
`DIAG9_GRAPH_cut_sat.py` is complete for any supplied labeled graph.  The
previous union-cut condition is sufficient but not complete: an exact finite
fixture satisfies the ninth conclusion although every spanning tree fails
the coarse test.

The remaining ninth-diagonal input is geometric.  The first exact scoped
roadmap is now complete on the row-2599 line
`Y(t)=Y_0+t E_(2,7)`, `-1/2<t<1/2`.  Exact Sturm certificates cover all
84,840 residual occurrences and give 25 crossing parameters and 26 cells.
Each cell supports 26,112 signatures, their union has 26,232, and every
individual support is empty, full, a prefix, or a suffix.  Thus every finite
family has empty or connected common support on this line, and both (40) and
the complete cut-SAT test pass its 26-vertex graph.  At the exceptional
crossing, 65 labeled determinants have rank-one ambient gradient and are
transverse to the line.  Exact multivariate localization now proves that all
65 share the single primitive global residual factor

\[
             q=-bdi+bfg+cdh-ceg+cei-cfh.             \tag{40a}
\]

Six raw determinants are already associates of `q`; the other 59 acquire
only one parent-bracket unit.  Thus the event is one global residual wall,
not a tangency of distinct walls.

A genuinely embedded projective two-disk also resolves the local geometry
through the crossing.  For
`W(s,u)=W+s E_(2,7)+u E_(1,7)`, `|s|,|u|<=1`, exact coefficient-dominance
certificates keep all 70 parent brackets and the other 84,775 residual
restrictions nonzero.  The 65 center restrictions have primitive bivariate
gcd

\[
                 1401176374297s+849195472073u,          \tag{41}
\]

with 32 constant and 33 affine nonvanishing quotients.  The complete disk
roadmap is therefore two convex cells separated by one wall segment; its
labels are `26112--26040--26112`, and every finite common support is empty or
connected on the disk.  Exact frame and Cramer checks show that the coordinate
square embeds in projective moduli.  Equation (40a) supplies the global
factor represented by the disk gcd.  See
[`DIAG9_GRAPH_ROW2599_DISK.md`](DIAG9_GRAPH_ROW2599_DISK.md).

The first genuinely new codimension-two model is also exact.  A second
rational projective disk contains two coprime residual branches, with exactly
65 labeled occurrences on each and rank-two Jacobian at their common node.
All other residual restrictions, quotients, and parent brackets are excluded
from the disk by exact bounds.  Its roadmap has four `26,112`-signature open
cells, four `26,040`-signature wall arcs, and one `25,968`-signature node.
The four-cell graph passes (40) and cut-SAT.  Its exact support masks and
lower-stratum labels identify every individual local feasibility region with
the whole square or one strict affine half-disk.  Every finite
signature-family support is therefore empty or convex, hence contractible
when nonempty.  See
[`DIAG9_GRAPH_verify_row2599_node.py`](DIAG9_GRAPH_verify_row2599_node.py).

The full factor census makes the master-roadmap input substantially smaller.
After exact division by parent-bracket units, the 84,840 labeled residual
occurrences define 26,740 primitive polynomials.  Their multiplicity
distribution is `25,200 x 1`, `420 x 2`, `280 x 15`, and `840 x 65`.
Each of the 62 nonconstant parent brackets is stripped exactly 840 times.
The two branches in the preceding node are distinct global multiplicity-65
factors.  See
[`DIAG9_GRAPH_GLOBAL_FACTOR_CENSUS.md`](DIAG9_GRAPH_GLOBAL_FACTOR_CENSUS.md).

Exact evaluation of one representative per factor on all 178 stored
row-2599 charts gives 178 distinct generic factor-sign states.  Exactly
10,844 factor coordinates vary; every pair of states differs in between
1,125 and 5,600 coordinates.  Hence row 2599 has at least 178 residual
chambers and at least 10,844 walls which meet it, but the points still supply
neither adjacency nor coverage.  See
[`DIAG9_GRAPH_ROW2599_FACTOR_STATES.md`](DIAG9_GRAPH_ROW2599_FACTOR_STATES.md).

The local full `3^2` covector diamond at a transverse pair satisfies face
symmetry and strong elimination, but smooth residual hypersurfaces do not
imply a global COM: exact semialgebraic tangent and strip models violate the
needed axioms.  Reducible parents do not supply an induction either.  Deleting
a parent element while retaining all private extension witnesses gives the
safe homotopy equivalence

\[
                         F_S(M)\simeq G_{e,S},          \tag{41a}
\]

where `G_(e,S)` is the nonempty simultaneous-insertion locus in the
restricted `S`-indexed witness incidence over `M\e` (duplicate deletion
signatures are not merged); its insertion fibers are open convex polyhedra.
An exact proper extension of the lexicographically
reducible alternating parent `A(4,8)` has a restricted witness which cannot
be lifted back.  Thus `G_(e,S)` can be proper and reducibility is not
hereditary under extension.  See `DIAG9_GRAPH_COM_AUDIT.md` and
`DIAG9_GRAPH_REDUCIBILITY_AUDIT.md`.

The next missing layer is exhaustive coverage of all local intersection
types, including tangencies and higher multiplicity, followed by compatible
full-dimensional coverage for the 2,604 parents.  The 178 stored row-2599
point charts remain only a point sample.  A second exact stress path
reinforces that warning: a proper pairwise-incomparable nine-family that
appears to isolate charts 37 and 176 on the sample is joined by 22,811
rational one-column segments.  Together with the earlier 22,711-segment
charts-12/37 path, this supplies two independent regressions, not a proof of
diagonal nine.  See
[`DIAG9_GRAPH_ROW2599_ROADMAP.md`](DIAG9_GRAPH_ROW2599_ROADMAP.md).

The honest status after these audits is unchanged: (3) is proved, while
`s=2,...,9` remain open.
