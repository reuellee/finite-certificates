# A dual master-cell program for Nine-Diagonal Vanishing

## Outcome

The circuit-cover and block-Gordan resolutions are not the only finite models
for the open entries of 9DVL.  A single semialgebraic cellulation of the
nine-dimensional parent space, labeled by complete derived-arrangement tope
sets, gives a smaller model which is independent of the number of signatures
in the tested family.

The precise reduction is:

> **Dual master-cell theorem.**  For a fixed realizable `UOM(4,8)` parent
> there is a finite labeled dual-cell complex `D` such that, for every finite
> family `S` of extension signatures, the cells whose labels contain `S`
> form a subcomplex `D_S` with
>
> \[
>                         F_S\simeq D_S.                 \tag{1}
> \]
>
> A primal codimension-`j` simplex (or cell of a regular CW refinement) gives
> a `j`-cell of `D_S`.  Consequently, for `s<=8`, the group
> `H_(9-s)(F_S)` is determined by primal cells of codimensions `8-s`, `9-s`,
> and `10-s` only.  For `s=9`, codimensions zero and one occur together with
> the augmented degree-zero boundary.

This is an exact finite reformulation, not a new diagonal vanishing theorem.
Its main strategic consequence is that the middle diagonals should be attacked
from high `s` downward.  Diagonal eight needs only the global labeled
codimension-two skeleton; diagonal seven adds codimension three.  The witness
resolution instead retains a large amount of fiberwise circuit data on the
bad locus.  It reaches the same vanishing target only after the separate
compact-support duality reduction, and need not admit a simple matching in
its chosen filtration.

The existing exact transverse-node artifact for parent 2599 already supplies
the first nontrivial local regression.  Its complete labels imply that every
finite common-feasibility locus on that disk is empty or convex, not merely
empty or connected.  Thus that node carries no local diagonal-eight class.

## 1. Simultaneous finite cellulation

Let `X` be the normalized realization space of a fixed parent and let

\[
 B_\rho=X\setminus F_\rho.
\]

Choose a bounded semialgebraic embedding of `X`, let `bar X` be its compact
closure, and put `A_inf=bar X minus X`.  For each extension signature define

\[
             A_\rho=A_{\rm inf}\cup
                      \overline{B_\rho}^{\,\bar X}.      \tag{2}
\]

The set `B_rho` is closed in `X`, so

\[
                         \bar X\setminus A_\rho=F_\rho. \tag{3}
\]

There are finitely many signatures.  Semialgebraic triangulation therefore
gives a finite simplicial complex `K` realizing `bar X` and compatible with
`A_inf` and every `A_rho` simultaneously.  Refine it so that its restriction
to the open nine-manifold `X` is a PL triangulation.

For every simplex `tau` not contained in `A_inf`, define its complete label

\[
 T(\tau)=\{\rho:\operatorname{relint}(\tau)\subset F_\rho\}.     \tag{4}
\]

These labels are monotone.  If `tau` is a face of `eta`, then

\[
                              T(\tau)\subseteq T(\eta).           \tag{5}
\]

Indeed, each `A_rho` is a subcomplex.  If `eta` belonged to `A_rho`, all of
its faces would belong to it too.  The contrapositive is (5).

For a finite family `S`, put

\[
 P_S=\{\tau:S\subseteq T(\tau)\}.
\]

Equation (5) says that `P_S` is an upper order ideal in the interior face
poset.  Its union of relative interiors is exactly `F_S`.

The construction does not require a separate quantified decomposition for
each of the 97,224 signatures in the hard parent.  The existing factor
classification writes every four-by-four determinant of the 56 derived
normals as a structural zero, a parent-bracket unit, or a unit times one of
the 26,740 primitive residual factors.  Start with the zero/sign conditions
of those factors, then take a finite regular semialgebraic refinement---for
example a compatible triangulation, Whitney--Hardt cellulation, or regular
CAD---on which the incident full-dimensional chamber germs are constant.
This refinement is essential: a connected zero/sign component need not be a
ball, need not have constant chamber incidence, and may acquire artificial
faces which must remain in the cellular complex.  The derived oriented
matroid and its complete tope set are fixed on every full-dimensional
chamber.  One exact derived-tope enumeration per such chamber, followed by
the all-strata gluing theorem in Section 4, labels every *interior* refinement
cell.  Cells in `A_inf` are excluded rather than assigned intersection
labels.

## 2. Proof of the dual master-cell theorem

For an interior simplex `tau`---equivalently, one not contained in
`A_inf`---let `tau*` be its closed barycentric dual block.  Its
dimension is the primal codimension:

\[
                         \dim(\tau^*)=9-\dim(\tau).     \tag{6}
\]

Put `D=D_emptyset`, the union of `tau*` over all simplices `tau` not
contained in `A_inf`.  This is a finite regular CW complex inside `X`.
Indeed, no coface `eta` of an interior `tau` can be contained in the boundary
subcomplex `A_inf`; otherwise subcomplex closure would put its face `tau`
there too.  Every barycentric simplex of `tau*` is therefore disjoint from
the full subcomplex `sd(A_inf)`.  Moreover `relint(tau)` lies in the PL
nine-manifold `X`, so `link_K(tau)` is a PL sphere and `tau*` is a regular
closed ball of dimension `9-dim(tau)`.  This supplies both boundary
disjointness and the regular-CW hypothesis used by the Forman matching below,
even when proper faces of `tau` lie at infinity.

Define

\[
                 D_S=\bigcup_{\tau\in P_S}\tau^*.      \tag{7}
\]

This is a genuine dual-block subcomplex.  A face of `tau*` is a dual block
`eta*` for a coface `eta` of `tau`; (5) makes `eta` feasible whenever `tau`
is feasible.

For completeness, the deformation retraction in (1) can be seen directly in
the barycentric subdivision.  A point of `F_S` has a barycentric carrier
chain whose largest simplex lies in `P_S`.  Delete the weights on vertices
whose simplices are not in `P_S` and renormalize the remaining weights.  The
denominator is positive on `F_S`.  Linear reweighting stays in `F_S`, because
the largest simplex with positive weight remains feasible.  At the end, all
vertices in the carrier chain are feasible, which is precisely the union
(7).  This gives a strong deformation retraction `F_S -> D_S` and proves
(1).

Let `C_j(D_S;R)` be the cellular chains over any coefficient ring `R`.  By
(6), they are generated by the feasible primal codimension-`j` strata.  If
`k=9-s`, then

\[
 H_k(F_S;R)\cong
 \frac{\ker[C_k(D_S;R)\longrightarrow C_{k-1}(D_S;R)]}
      {\operatorname{im}[C_{k+1}(D_S;R)\longrightarrow C_k(D_S;R)]}.
                                                               \tag{8}
\]

Only codimensions `k-1`, `k`, and `k+1` occur in (8).  The exact ledger is:

| `s` | target | primal codimensions needed |
|---:|---:|---:|
| 1 | `H_tilde_8` | 7, 8, 9 |
| 2 | `H_7` | 6, 7, 8 |
| 3 | `H_6` | 5, 6, 7 |
| 4 | `H_5` | 4, 5, 6 |
| 5 | `H_4` | 3, 4, 5 |
| 6 | `H_3` | 2, 3, 4 |
| 7 | `H_2` | 1, 2, 3 |
| 8 | `H_1` | 0, 1, 2 |
| 9 | `H_tilde_0` | 0, 1 plus augmentation |

The last row is exactly the complete labeled chamber-graph formulation
already proved in `NINTH_DIAGONAL_SAFE_GRAPH.md`.  The first row is already
settled by the contraction-height theorem.  The new practical entry point is
the `s=8` row.

The boundary at infinity has not been discarded: it is part of `A_inf` and
is removed before the dual blocks are selected.  This is why (1) computes
ordinary homology of the noncompact `F_S` without an informal escape
argument.

## 3. A universal discrete-Morse certificate

The labeled dual complex supports a certificate which can prove a diagonal
for all admissible families at once.  Let `M` be an acyclic Forman matching
on `D`.  Restrict it to the pairs whose two cells lie in `D_S`.  The
restriction stays acyclic.

A matched upper cell cannot be included without its matched lower face,
because `D_S` is a subcomplex.  A matched lower cell can, however, be
included while its upper coface is excluded.  Thus the critical `k`-cells of
the restricted matching are exactly:

1. included ambient-critical `k`-cells; and
2. included lower `k`-cells whose matched `(k+1)`-coface is excluded.

For `k>=1`, if neither type occurs, the Morse complex has no degree-`k`
chain group, so `H_k(F_S;R)=0` for every coefficient ring `R`.  The
degree-zero target is different: to prove reduced `H_0=0`, a nonempty
restricted complex needs one critical zero-cell (or an equivalent augmented
boundary-rank certificate), not zero critical zero-cells.  Thus the matching
test below applies directly to `s<=8`; diagonal nine retains its augmented
graph test.

This condition is finite for all proper pairwise-incomparable size-`s`
families.  Quotient signatures with equal feasibility regions and order the
remaining proper regions by inclusion.  Call this dominance poset `P`.  The
master labels determine it exactly:

\[
 F_\rho\subseteq F_\sigma
 \quad\Longleftrightarrow\quad
 \text{every master cell labeled by \(\rho\) is labeled by \(\sigma\)}.
                                                               \tag{9}
\]

For an ambient-critical `k`-cell `c`, no admissible family can include it if

\[
                       \operatorname{width}(P\cap T(c))<s.       \tag{10}
\]

For a matched incidence `c^k<d^(k+1)`, a family breaks the pair precisely
when it is contained in `T(c)` but not in `T(d)`.  It is enough, and is also
necessary, to test every proper class
`delta in T(c) minus T(d)`:

\[
 1+\operatorname{width}\{x\in P\cap T(c):x\text{ incomparable with }\delta\}
 <s.                                                           \tag{11}
\]

Equations (10)--(11) are ordinary exact Dilworth-width computations.  A
proof-carrying matching consists of the cell incidence list and orientations,
label bitsets, matched incidences, a topological order of the Forman-directed
incidence graph---unmatched incidences oriented from upper cell to lower face
and matched incidences reversed from lower to upper---and bipartite matching
certificates for the width bounds.  Reversing the whole Hasse graph would not
certify acyclicity.  If a width bound fails, the same computation returns an
explicit admissible antichain for geometric or homological testing.

Equal-label pairs `T(c)=T(d)` are safe for every diagonal and every family.
This makes artificial CAD section/sector pairs the first canonical
coreductions.  Width-safe pairs then extend the matching across genuine wall
strata.  If one global matching is too rigid, a finite decision tree of
matchings can cover the admissible-family space, with label include/exclude
literals defining each leaf.

## 4. The sharp local obstruction

Put `q=10-s`, so the target is `H_(q-1)`.  A primal codimension-`q` cell of a
regular refinement has a dual `q`-cell.  The top local obstruction is a
puncture: all proper
faces in its normal link support `S`, while the central stratum does not.
The boundary `S^(q-1)` is then present in `D_S` while the filling dual
`q`-cell is absent.  Global cells may still kill this cycle, so a puncture is
a candidate rather than automatically a nonzero global class.

For diagonal eight this is a codimension-two test.  At first glance, a
candidate family could be feasible on all four sectors and all four open wall
rays but infeasible at their node.  Generic one-wall gluing by itself does
not address that lower-dimensional possibility.

The all-strata gluing theorem in `NINTH_DIAGONAL_SAFE_GRAPH.md` now excludes
this candidate at every interior refinement cell, including singular and
multiple wall intersections.  Its proof reuses the support-minimal Gordan
relation, the complete nine-ordinary/four-localization residual support
classification, and the global side identities.  It shows

\[
 T(\tau)=\bigcap_{C\text{ an incident chamber germ}}T(C)       \tag{12}
\]

for every interior master cell `tau`.  In the three-circuit case, padding by
a nonstructural fourth triple gives a residual four-set.  The fixed-unit
four-row identities for all nine ordinary residual types have four nonzero
circuit coefficients everywhere on their wall, so they cannot contain the
zero-padded three-circuit.  The residual four-set must therefore be one of
the four localization types, with the padded triple as its designated exact
three-circuit.  Its side identity supplies a bad half-neighborhood containing
generic bad chambers.  Thus a positive circuit cannot be confined to a
lower-dimensional stratum.

Equation (12) means that the dual master complex is *cell-induced* by its
supporting chamber vertices: a dual cell lies in `D_S` exactly when all of its
incident chamber vertices support `S`.  No separate lower-stratum tope
enumeration is required, and an isolated missing-center sphere cannot occur
in the interior at any codimension.  The remaining diagonal-eight work is
global: assemble the complete chamber/wall/node incidence, include the
boundary-at-infinity deletion correctly, and prove that the resulting
cell-induced subcomplexes have no one-cycles.  Individually harmless cells
can still assemble into a global cycle.

This also explains the repeated block-Gordan difficulty.  At a generic
smooth wall each individual `B_rho` is locally empty, the whole ball, the
wall, or one closed side.  A large multi-circuit all-die carrier is not exotic
local topology in the base; it is the cost of requiring maps natural on all
coordinate faces of a witness resolution.  The block-Gordan total complex
and a *primal bad-locus* cellular model can be viewed as two models for the
same compactly supported object after compatible refinement.  The displayed
dual complex `D_S`, by contrast, models ordinary homology of `F_S`; it is
connected to that compact-support calculation only by the separate duality
theorem.  None of these useful filtrations need share a simple matching.
There is no need to finish the witness-resolution matching if the dual
feasibility complex can be certified directly.

## 5. Exact row-2599 codimension-two regression

The exact artifact in `DIAG9_GRAPH_ROW2599_NODE.md` gives a square `D` whose
complete residual arrangement is the transverse pair of affine lines
`q_0=0`, `q_1=0`.  Its four chamber signs, in cyclic order, are

\[
       (+,+),\quad(+,-),\quad(-,-),\quad(-,+).          \tag{13}
\]

Exact tope enumeration gives only the individual support masks

\[
              1111,\quad0011,\quad0110,\quad1100,\quad1001.     \tag{14}
\]

Every open wall label is the intersection of its two adjacent chamber
labels, and the node label is the intersection of all four chamber labels.
It follows from (13)--(14), including the lower-stratum labels, that an
individual feasibility locus on `D` is exactly one of

\[
 \varnothing,\quad D,\quad
 D\cap\{q_0>0\},\quad D\cap\{q_0<0\},\quad
 D\cap\{q_1>0\},\quad D\cap\{q_1<0\}.                 \tag{15}
\]

An arbitrary finite intersection of the sets in (15) is an intersection of
a convex square with strict affine halfspaces.  It is empty or convex, hence
contractible.  Therefore this exact node has no local reduced homology in
any degree and, in particular, no codimension-two puncture for diagonal
eight.  `verify_dual_master_node.py` independently replays the label and
halfspace conclusion from the stored exact artifact; the original node
verifier independently reconstructs all determinant and tope data.

This is a local theorem only.  It neither classifies all codimension-two
strata of parent 2599 nor rules out a global one-cycle assembled from many
individually harmless nodes.

## 6. Revised attack order

1. Construct a complete regular chamber/wall/node refinement, retaining its
   artificial faces and the projective boundary-at-infinity subcomplex, for
   one parent.
2. Infer every *interior* wall and node label from incident chamber labels
   using all-strata gluing; exclude infinity cells.  Then build a label-safe
   Morse matching or exact relative boundary-rank certificate for the global
   one-cycles.  This attacks diagonal eight for every admissible eight-family
   simultaneously.
3. Extend the same master cellulation through codimension three for diagonal
   seven, reusing all lower layers and labels.
4. Continue through codimension seven only as demanded by surviving critical
   labels.  Do not enumerate witness-support carriers which already collapse
   at the base level.
5. Pursue the moving-witness transport lemma separately for diagonal two,
   where the dual method would require strata through codimension eight.
6. For diagonal nine, either prove residual sign-geodesy, which would make
   every signature support chamber-convex, or complete only the labeled
   codimension-one roadmap and use the existing exact graph verifier.

The witness-frame reduction remains a valid cross-check for diagonals seven
through nine, but it raises the ambient dimension from nine to `9+3s` and
does not restore convexity.  The dual master complex stays nine-dimensional
and is therefore the preferred global route.
