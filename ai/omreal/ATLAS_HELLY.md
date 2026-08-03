# Extension-atlas Helly theory

**Status.**  This note separates one finite conjecture from several unconditional
theorems.  The conjecture is deliberately catalog-sized: it concerns all
2,604 realizable `UOM(4,8)` reorientation classes, not only parent row 2599.
It is still a conjecture.  Two proof shortcuts that would have made it nearly
formal are now ruled out below: neither convex private LP fibers nor sparse
Gordan circuits impose a dimension-only Helly bound, and smooth individual
derived walls do not control their multiple intersections.  On the positive
side, Section 11 proves a sharp COM--Helly theorem reducing the desired bound
to one precise support-state property, while Section 12 gives an exact
classification and a regularity theorem for every possible derived wall.
Section 13 weakens the remaining support-state target to a finite feasible-COM
completion problem and proves that wall topology alone cannot close it.
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
| 1 | `H_tilde_8(F_S; Q)` |
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

## 4. The finite conjecture to test

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

This strengthening is intentionally quantified over every internal antichain
of proper regions, not only globally minimal regions from `E(M)`.  Therefore
a falsifier for (5) need certify only properness and pairwise incomparability;
a falsifier for the reduced core conjecture must certify membership in `E(M)`.

The core dichotomy proves `DEHC(4,8)` implies the Extension-Helly Conjecture.
The converse need not hold: (5) is a deliberately stronger, independently
certifiable target.

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
the single diagonal to the full homology tail (8).

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

## 13. The weakest finite COM target presently sufficient

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
>       \mathcal C_M\subseteq K_{\mathbb R}(M)
> \]
> and `C_M` contains every maximal face of `K_R(M)`.

> **COM-completion implication.**  If `FCC_9(M)` holds, then
> `h(M)<=10`.

**Proof.**  Because every member of `C_M` is a feasible face and
`K_R(M)` is downward closed,
`K(C_M) subseteq K_R(M)`.  Conversely, every face of the finite complex
`K_R(M)` is contained in a maximal face, and every maximal face is a member
of `C_M`.  Hence `K_R(M) subseteq K(C_M)`.  The two complexes are equal, so
the COM--Helly theorem with `d=9` gives the claim.  QED.

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
             A_O\simeq\operatorname{Gr}_{\mathbb R}(k-1,N-1).    \tag{28}
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
