# Coordinate-path certificates for common extension feasibility

## Scope

This note proves a universal certificate theorem for common extension
feasibility.  It explains exactly why a path made of one-column rational
segments is conclusive and proves that this certificate language is complete
for joining rational points which are already in the same component.  It does
not prove that every common feasibility locus is connected.

Fix a realizable uniform rank-four parent chirotope `M` on eight labels and a
finite family `S={sigma_1,...,sigma_s}` of extension signatures.  For a parent
matrix `Y`, write

\[
 C_\sigma(Y)=\{p\in\mathbb R^4:
 \sigma_I\det(Y_I,p)>0\text{ for all }I\in { [8]\choose3}\}.
\]

Thus `F_S` consists of the parent realizations for which every
`C_sigma(Y)` is nonempty.  Introduce the incidence space

\[
 Z_S=\{(Y,p_1,\ldots,p_s):Y\in\mathcal R(M),
                 p_j\in C_{\sigma_j}(Y)\}.
\]

All statements may be made before quotienting by orientation-preserving
`GL(4)` and positive column rescaling, or in any fixed projective gauge.

## The universal theorem

> **Coordinate-path theorem.**
>
> 1. Projection `pi: Z_S -> F_S` induces a bijection on path components.
> 2. After all columns except one are fixed, the allowed homogeneous values of
>    the remaining column form an open convex polyhedral cone (or its convex
>    affine slice after imposing a projective gauge).
> 3. Two incidences lie in the same component of `Z_S` if and only if they can
>    be joined by a finite polygonal chain whose every edge changes one
>    homogeneous column only.
> 4. If the two incidences have rational columns, such a chain can be chosen
>    with rational vertices.  Clearing denominators turns it into a finite
>    integer determinant certificate.

These conclusions hold for every finite `S`; properness, incomparability, and
the special value `s=9` are unnecessary.

### Proof of (1)

The fiber over `Y` is

\[
                       \prod_{\sigma\in S}C_\sigma(Y),
\]

a nonempty product of open convex cones.  Local sections exist: a witness
tuple over `Y_0` remains feasible throughout a sufficiently small
neighborhood of `Y_0`, because all defining inequalities are strict.
A partition of unity subordinate to these neighborhoods gives a global
continuous section; convex combinations remain in each cone.  Straight-line
homotopy within every convex fiber deforms any incidence to the section.
Consequently `Z_S` and `F_S` have the same path components.  (For the present
connectivity claim, local path lifting plus convex fibers already suffices.)

### Proof of (2)

Every constrained determinant either omits the moving column and is constant,
or contains it once and is a linear functional of that column.  The permitted
values are therefore an intersection of strict linear halfspaces.  If two
permitted columns are `u` and `v`, then every signed determinant at
`(1-t)u+tv` is the same convex combination of two positive endpoint values.
It remains positive for `0<=t<=1`; in particular the moving column cannot
become zero.

### Proof of (3)

One direction follows immediately from (2).  Conversely, let `gamma` be a
path in the open set `Z_S`.  Its compact image has a positive-distance open
neighborhood still inside `Z_S`.  Uniform continuity gives a subdivision for
which consecutive values of `gamma` are sufficiently close.  Between two
consecutive values, replace their columns one at a time.  Every intermediate
vertex and every resulting segment remains in the same small neighborhood.
This produces a finite one-column chain.

### Proof of (4)

The determinant inequalities have integer coefficients.  The chain from (3)
has a positive minimum margin after finitely many compact edges are covered by
small feasible neighborhoods.  For each column, split the vertex sequence
into its maximal constant runs and choose one rational approximation for each
run, keeping the rational endpoints fixed.  Chosen sufficiently close, these
simultaneous approximations stay in the feasible neighborhoods and preserve
the property that every edge changes only one column.  Clear denominators
consistently on each constant run.  Every vertex then has integer homogeneous
columns, unchanged columns still agree across an edge, and no sign changes.

For one-column edges no root isolation is required: every affected
determinant is affine, so exact positivity at the two integer endpoints
certifies the whole segment.

## Parent-only common-cone criterion

The incidence theorem has the following useful form which avoids storing a
continuous motion of every extension point.

> **Common-cone bridge lemma.**  Suppose parent matrices
> `Y_0,...,Y_m` all realize `M`, every edge `[Y_i,Y_(i+1)]` changes one parent
> column, and for every `i` and every `sigma in S`,
>
> \[
>                    C_\sigma(Y_i)\cap C_\sigma(Y_{i+1})\ne\varnothing.
> \]
>
> Then `Y_0` and `Y_m` lie in the same component of `F_S`.

For each edge, choose one common ray for every signature.  Move the extension
columns to those rays one at a time, move the one parent column, and continue.
Every move is a one-column edge certified by the theorem.  Conversely, if the
endpoints are rational, any path in `F_S` can be replaced by a sufficiently
fine rational coordinate subdivision with this common-cone property: strict
witnesses at one endpoint remain witnesses at all sufficiently nearby
parents.  Thus the criterion is also complete for rational endpoint pairs
known to share a component.

The common-cone condition is a small exact linear alternative.  Feasibility
has a rational ray; infeasibility has a positive Gordan circuit of support at
most five among the 112 signed normals from the two endpoint parents.

## What this gives for the ninth diagonal

The theorem supplies a proof-complete positive certificate for any proposed
pair of chambers.  The exact row-2599 charts-12/37 certificate is one
instance: its middle bridge repeatedly finds common rays at consecutive
parents and verifies all one-column edges with integer determinants.

It does not turn one successful pair into a connectivity proof.  To prove the
ninth diagonal one still needs a finite cover or roadmap showing that every
incidence reaches a common component, for every size-nine proper antichain and
every parent.  A sign-invariant semialgebraic decomposition followed by the
common-cone adjacency test is a finite complete procedure; the residual-wall
master-chamber graph is the more economical version already developed in
`NINTH_DIAGONAL_SAFE_GRAPH.md`.

The 2,604-parent catalog contains only one realization for almost every
parent.  It certifies which parent cells are realizable, but it contains
neither their residual-wall chambers nor a roadmap covering them.  Therefore
that dataset alone cannot satisfy the remaining finite coverage premise.
