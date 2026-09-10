# Diagonal three: two-block root switches on one factor wall

## Result

Let `q` be any primitive residual factor at a generic supported factor wall,
let `P` and `Q` be the generic active small circuits arising from any two
labeled occurrences of `q`, and let `sigma` and `tau` be arbitrary,
independent signings of the 56 derived normals.
The graph of roots simultaneously compatible with `(P,sigma)` and
`(Q,tau)` is nonempty and connected when an edge is required to use the
**same order** of its two elementary shears in both blocks.

Thus two blocks meeting the same factor wall always admit a common local
root, and any two common-root choices can be joined by exact ordered
two-root carriers without choosing the carrier order separately by block.
No parent chirotope, Grassmann--Pluecker condition, or realizability
restriction is imposed on either signing.

The construction is equivariant under simultaneous `S_8` relabeling.  The
six representative factor orbits below therefore cover every labeled
generic factor wall.  The theorem does not cover a simultaneous intersection
of primitive factors, an additional rank drop, or a specialization at which
the generic active support shrinks; those require their own face maps.

This is strictly stronger than applying
`DIAG3_PAIR_LOCAL_ROOT_SWITCH.md` twice: two connected graphs can have an
empty or disconnected intersection.  The verifier excludes both failures
directly.

## Exact finite reduction

The global factor certificate contains 26,740 primitive factors and 84,840
labeled occurrences.  Under `S_8` the factors have six orbits.  Three have
more than one occurrence:

| factor kind | occurrences per factor | distinct active supports | support-pair orbits |
|---:|---:|---:|---:|
| 36 | 65 | 31 (`1` of size `3`, `30` of size `4`) | 35 |
| 38 | 15 | 15 (all size `4`) | 8 |
| 48 | 2 | 2 (both size `4`) | 2 |

The remaining factor kinds `49,50,51` have one occurrence and contribute
one self-pair apiece.  Exact canonical wall normals identify the active
small circuit in every occurrence; the stabilizer of the representative
factor then reduces every labeled same-factor support pair to

\[
                         35+8+2+1+1+1=48                 \tag{1}
\]

orbits.  This is a coverage reduction from the global occurrence map, not a
chart sample.

## Boolean certificate

For one support pair the Boolean variables begin with two independent
56-bit signings.  For each of the 112 oriented elementary roots, exact XOR
conditions encode compatibility with both signed circuits.  For every pair
of distinct root lines and each of its two orders, the full third-exterior
expansion encodes constant, linear, and bilinear coefficients in both
blocks.  The ordered edge is enabled only when that one order is safe in
both.

Two formulas are solved for every orbit:

1. all common compatibility variables are false;
2. the common graph has compatible vertices on both sides of a cut and no
   enabled ordered edge crosses it.

All 96 formulas are UNSAT.  The first family proves nonemptiness; the second
proves connectivity without relying on a convention for the empty graph.
The 48 cut formulas use 23,608 exact-CDCL conflicts in total.  The semantic
digest over every support pair, formula size, formula hash, and conflict
count is

```text
7196d312dbcb473dadfa9b00f2a9491d0c4171784c7b0bbd0d8d20bdfca20104
```

There is also a useful oriented strengthening.  Fix either elementary-shear
parameter sign `a=+1` or `a=-1`.  For every one of the 13 active wall-support
types and every one of the 48 same-factor support-pair orbits, arbitrary
independent signings admit a compatible root of parameter sign `a`; in the
two-support case the root is common to both blocks.  The finite SAT replay
proves the stronger canonical-representative statement after retaining only
the 28 roots with `source > target` and the prescribed parameter sign.  It
checks 26 single-support and 96 support-pair formulas for the two signs; every
formula is UNSAT by unit propagation, with zero conflicts.

Only the parameter-sign conclusion is relabeling invariant.  Simultaneous
`S_8` relabeling preserves the parameter sign but need not preserve the
numeric inequality `source > target`, so the canonical descending half is
not a global triangular order.  This strengthening removes a pointwise
choice between the two parameter orientations.  It does not select a root
continuously across signing chambers, prove connectivity of the restricted
fixed-sign graph, or provide a proper frontier matching.

Replay with

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_factor_root_switch.py --workers 4
```

Connectivity is not acyclicity.  The exact kind-36 self-support canary

```text
P       = 0/7/8/32
sigma   = 65112642768982744
tau     = 23589210603315253
```

has `43` common vertices and `860` common ordered-root edges.  Its graph is
connected, but its integral cycle rank is

\[
                         860-43+1=818.                  \tag{2}
\]

Thus the theorem permits choosing a spanning tree and eliminating `42`
relative degree-one rows by unit pivots.  It does not delete the remaining
`818` cycle columns; those require higher cells and coherent frontier maps.

## The same-factor occurrence complex has no degree-one cycle

There is a separate exact theorem for the choice of labeled occurrence.
For one or two block signings, let `O_f` have as vertices the occurrence
circuits of a generic factor `f` which are positive in every selected block.
Join two vertices when their support union has at most six normals.  Attach
a triangle when all three edges are present and the support union has at
most seven normals.  These are exactly the support bounds of the witness
one- and two-skeleton.  Then, for every primitive factor kind,

\[
                         H_1(O_f;R)=0                    \tag{3}
\]

for every coefficient ring `R`.  This does not say that the occurrence
graph is a tree.  It says that all its cycles have unit-coefficient fillers
after the support-correct witness triangles are retained.

For kind `36`, the `31` supports consist of the central three-support
`0/9/32` and three families of ten.  Each family is a fixed two-element
core plus all two-subsets of a five-element outer set.  Every induced
subcomplex in one family has a complete one-skeleton and every triangle;
the central vertex, when active, cones each family.  Distinct families have
no edge.  Thus (3) holds for an arbitrary active subset, and hence for the
intersection of two independently signed active subsets.  Kind `48` has
two supports whose union has size eight, and kinds `49,50,51` have only one
occurrence, so they contribute no degree-one cycle.

Kind `38` is the only nontrivial case.  Its supports are

\[
 \{n_{345},n_{678},u_i,u_j\},\qquad
 u_i\in\{n_{123},n_{124},n_{125},n_{126},n_{127},n_{128}\}. \tag{4}
\]

The six `u_i` lie in the rank-two annihilator of the parent line `12`.
On the generic supported factor wall all eight displayed normals span rank
three.  After nonzero rescaling, the two core normals differ by one ray `w`
in that rank-two flat.  Choose a projective coordinate avoiding the seven
rays.  The six `u_i` are linearly ordered and `w` lies in one of seven
affine gaps.  For a block whose two core signs permit a positive circuit,
the positive occurrence set is determined by that gap and six independent
outer reorientation bits.  If the core signs do not permit it, the set is
empty.

The resulting universal census has `58` one-block patterns for each gap.
Intersections for two independent block signings give `180` patterns per
gap, `487` distinct patterns over all gaps.  Every pair of occurrence
vertices is an edge.  The only absent triangles are three outer pairs which
form a perfect matching and therefore use all six outer normals.  In all
`105` common-active matching cases, the exact sign table forces a fourth
common-active outer pair.  If the matching vertices are `a,b,c` and the
fourth vertex is `h`, the three allowed triangles

```text
(a,b,h), (b,c,h), (c,a,h)
```

fill the boundary of `(a,b,c)` by the oriented tetrahedron identity, with
unit coefficients.  This proves (3) integrally and after every base change.

The rank-two-flat hypothesis is essential.  The exact uniform realizable
rank-three matrix

\[
 \begin{pmatrix}
 1&0&0&1&-8&-2&8&8\\
 0&1&0&-1&-8&-8&4&1\\
 0&0&1&1&3&1&7&6
 \end{pmatrix}                                             \tag{5}
\]

with core labels `0,1` and reorientation mask `85` has exactly the three
positive four-circuits on outer pairs `(2,3),(4,5),(6,7)`.  Their three pair
unions have size six, while the triple union has size eight.  The resulting
occurrence complex is an unfilled circle.  Thus generic rank-three
realizability or oriented-matroid elimination would not prove (3); the
actual `n_12k` pencil identity does.

The exact finite replay is

```console
PYTHONDONTWRITEBYTECODE=1 python \
  ai/omreal/verify_diag3_pair_factor_occurrence_h1.py
```

This theorem removes same-factor **occurrence** cycles only.  It does not
remove the `818` cycles in the common ordered-root graph above, and it has
no face map at a factor intersection, support-shrink specialization, or
parent infinity.

## Conditional degree-one compression and its smallest failure

The preceding theorem does combine cleanly with the residual-wall and
acyclic-carrier theorems, but only under their actual codimension-one
premise.

> **Conditional compression.**  Suppose a finite generic primitive-factor
> atlas has a facewise, support-monotone specialization map for every
> oriented codimension-one circuit incidence, with every zero-weight face
> retained.  Then all root and labeled-occurrence choices can be removed
> from relative degrees zero and one by integral unit pivots.  Different
> elimination orders at a codimension-two factor intersection are chain
> homotopic in a common union-support carrier.

Indeed, a spanning tree in the common ordered-root graph removes all root
differences by unit sector pivots.  Non-tree root sectors only give relations
starting in degree two and do not change exactness through degree one.  The
occurrence theorem (3) then removes every occurrence cycle by unit witness
triangles.  Its occurrence graph need not be connected: kind `48`, for
example, has two disjoint supports.  This creates no generic factor-wall
generator because the residual-wall corollary identifies every occurrence
with the same base stratum `H_f=D_(U,0)`.  Whenever two such vertices are
active, their full normalized Gordan-fiber coordinate carrier is nonempty
and convex over all of `H_f`; the corollary gives the required low-degree
compact-support contraction of that common base.  Thus disconnected
occurrence pieces are identified only after this factor-wall carrier is
used, not by falsely adding a support-union-six edge.  On one simple
residual wall, the same-side witness simplex and the opposite-side interval
cospan remove the choice of auxiliary partner.  Finally, once the
codimension-one maps are genuinely defined face by face, the acyclic-carrier
diamond compares their two composites at codimension two.  Convex
union-support carriers supply the higher coherence as well.

Under this hypothesis, the degree-one quotient needs only the following
primitive-factor incidence data:

1. the connected oriented component germs of the generic factor walls
   `H_f`, with their block colors;
2. the oriented codimension-one end maps, including the retained
   zero-weight source and target faces; and
3. at each nonempty `H_f intersection H_g`, one union-support carrier for
   the codimension-two diamond.

This is not yet an unconditional reduction of the matrices in
`DIAG3_PAIR_DIFFERENTIAL_ENDS.md`.  The smallest exact **same-block** failure
is still the strict coordinate-face diagram

```text
                 point  ->  point  <-  empty.
```

The residual-wall corollary in `DIAG3_SINGLE_BAD_TWO_SKELETON.md` identifies
the middle point exactly as the positive singleton stratum `H_f=D_(P,0)` and
proves its compact-support vanishing through degree two.  It does not create
the missing same-block target point.  The enlarged interval

```text
          [Q-,R]  ->  [P,R]  <-  [Q+,R]
```

repairs the diagram only when an opposite-side auxiliary exists.  For a
fixed signature all certified auxiliaries can lie on one side of the wall.
Root connectivity and occurrence two-acyclicity cannot map that block into
its empty outgoing face.

This same-block no-go is not a missing pointwise theorem for the **joined**
fiber.  Suppose a block with a nonstructural wall circuit `P` and another
active block with a minimal circuit `R` form a source-hard ordinary `4+5`
corner.  The exchange-saturated support-drop theorem proves `P intersection
R=empty`; for any `p in P`, the normalized nonnegative kernel on

\[
                              U=R\mathbin{\cup}\{p\}              \tag{6a}
\]

contains an extreme positive circuit `R_p` with `p in R_p` and `|R_p|<=5`.
The exact localization and ordinary `4+4` residues are UNSAT, while every
remaining `4+5` residue is wall-disjoint.  Hence `(P,R_p)` has a compatible
oriented elementary shear.  The convex normalized kernel fiber on `U`
joins the choices `R` and `R_p`.  This proves the pointwise partner-block
attachment.  If its common shear is `d`,
`DIAG3_PAIR_LOCAL_ROOT_SWITCH.md` connects any root specialized to the
`P`-wall block to `d` through ordered sectors; the partner block may be kept
on its zero-mass face during that switch and then turned on in the joined
mass simplex.  The local root-switch theorem does not keep `R_p` positive
along every intermediate sector, prove two-signing common-root
connectivity, or choose the outgoing chamber germ.  Thus it removes the
one-block wall-root choice after an attachment has been selected, not the
frontier-selection problem itself.

The later `182`-sign-bit audit does not invalidate this argument.  Those
bits give exact necessary support/sign formulas, and all of their pointwise
residues have been discharged as above.  They do not encode which bad
component continues into an adjacent chamber, the other residual-factor
walls crossed by that component, or a coherent choice on shared frontiers.
Thus they cannot promote the pointwise attachment to a facewise global
matching.

At a monochromatic joined wall, the remaining pointwise alternatives are
already supplied by `BLOCK_GORDAN_MONOCHROMATIC_MASS_TRANSFER.md`: mass
transfers linearly to any block bad on the receiving side; if every active
block dies, all blocks retarget to their positive occurrences of the crossed
global factor, and each starting point admits a proper escape along its
noncompact wall component.  The arbitrary-occurrence all-die assertion is
the analytic corollary of `RESIDUAL_STRATUM_NONCOMPACTNESS.md` plus the
fixed-unit coefficient identities; the mass-transfer checker itself replays
only the transfer algebra, the 13 light wall supports, and one common-circuit
triple.  This does not select a continuous proper escape field after the
other factor walls subdivide that component.  An unrelated persistent
circuit in the dying block is neither forced nor needed.  What remains is to
choose these proved alternatives coherently and properly on a finite
subdivision and to test their global signed incidence.

Consequently the smallest finite certificate still missing before the
primitive-factor incidence quotient is valid is a chamber-decorated
receiver/escape table with these residual cells:

1. for every oriented wall/signing germ, the incoming circuit `Q-`, its
   zero-weight wall circuit `P`, the literal outgoing circuit or empty face,
   and the set of active blocks on each side;
2. for a receiver-present germ, a chosen receiving block and witness `R`,
   the block-mass transfer support, and, when a root-labelled reroute is
   used, the conic bridge `(p,R_p)` and a local root-switch path;
3. for an all-die germ, the crossed primitive-factor component, the positive
   wall occurrence in every active block, and the chosen proper wall end;
4. for each pair-factor intersection reached by those assignments, the common
   union-support diamond cell.  Once items 1--3 are facewise, item 4 has no
   further homological obstruction by the acyclic-carrier theorem.

There is no remaining localization, ordinary `4+4`, or ordinary `4+5`
support-SAT formula: the eight localization formulas and all three labeled
`4+4` formulas are UNSAT, and conic exchange handles the ten `4+5`
survivors.  The new finite checks are instead (i) coverage and compatibility
of the receiver/escape choices on closures of the chamber subdivision, (ii)
absence of directed cycles and proper behavior at its compactification ends,
and (iii) the exact middle split-exactness test (22)--(26) of
`DIAG3_PAIR_DIFFERENTIAL_ENDS.md` for the resulting signed blocks `b_ij`.

Non-tree ordered-root sectors may be suppressed when testing only degree-one
exactness, but must be retained for any independent degree-two or frontier
claim.  Nothing in this compression supplies parent-infinity incidence or
the signed balanced-end matrix.

## Consequence for the balanced-end problem

The theorem removes a tempting local explanation for failure of the pair
differential.  On one primitive factor wall, neither different labeled
occurrences nor different block signings obstruct a common ordered-root
reroute.  In a signed factor atlas it therefore permits a spanning-tree
contraction through relative degree one on each discrete signing stratum.
Every non-tree root cycle, every support specialization, every factor
intersection, and every incidence with parent infinity must remain until a
higher-dimensional chain contraction actually removes it.

It does **not** imply injectivity of the balanced end map `beta` from
`DIAG3_PAIR_DIFFERENTIAL_ENDS.md`.  Ordered-root paths provide unit local
homotopies inside a factor stratum, but they do not determine how oriented
branches split, merge, specialize, or meet parent infinity.  After those
spanning-tree degree-one eliminations, the remaining exact certificate is
still the reduced signed frontier matrix

\[
 \beta:H_c^1(T)^2\longrightarrow
       H_c^2(E_{01})\oplus H_c^2(E_{02})\oplus H_c^2(E_{12}). \tag{6}
\]

Integral injectivity of (6) only asks for zero kernel; multiplication by `2`
on `Z` is the elementary warning that it need not have unit Smith invariant.
If the theorem is required after base change to **every** coefficient ring,
then a chain left inverse, equivalently unit Smith invariants on the reduced
map, is the appropriate coefficient-universal strengthening.  The primitive
flow-triangle relation is the smallest unfilled balanced column.  No
combination of the one-factor root paths above supplies its mixed three-block
filler.
