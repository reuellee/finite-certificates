# Diagonal three: strategy checkpoint after the two-skeleton audit

## Verdict

The honest nine-diagonal score remains `2/9`.  Diagonal three is still the
closest open entry, but it has two independent unresolved obligations:

1. triple `H_c^0`: exclude compact components for the remaining primitive
   factor triples; and
2. pair `H_c^1`: prove middle exactness of a coverage-certified
   exclusive-pair end complex.

The new single-bad theorem removes the third possible obligation entirely:

\[
                    H_c^q(B_\rho;R)=0\quad(0\le q\le2)
\]

for every coefficient ring.  Nothing in this note promotes the score until
both remaining obligations are proved.

## Exact state of the triple endpoint

The factor reduction has `79,102,449` unordered `S_8` triple orbits.  The
positive certificate layers are disjoint:

| certificate family | closed orbits |
|---|---:|
| jointly affine in three coordinates after reframing | `74,767,375` |
| moving-column support-union degree two | `26,927` |
| degree-three forest fibers | `2,410,414` |
| triangular sequential unit graphs | `12,333` |
| role-frame parent-unit Jacobian minors | `65,550` |
| frame-1119 constant decomposable planes | `61` |
| parent-unit graph plus square jointly affine fiber | `180,886` |
| type-49/pivots-1,3,5 double graph | `108,864` |
| generic all-chart double-graph increment | `308,964` |
| graph-restricted unit minor, disjoint from the full double graph | `20` |
| fully cleared direct-final affinity after two unit graphs | `58,673` |
| primitive final directions, disjoint from direct-final affinity | `23` |
| support-three primitive final directions, disjoint from prior final layers | `57` |
| **total** | **`77,940,147`** |
| **unresolved** | **`1,162,302`** |

Every polynomial identity counted here is replayed exactly over the integers;
the degree-two/three layers instead combine exact incidence classifications
with structural fiber theorems.  Modular arithmetic is used only to propose
identities.  Negative
search accounting is kept separate: 79 role frames are sufficient to replay
the positive coordinate-minor certificates, while exhaustion of that
coordinate-minor family used all 1,120 role frames.  The 61 constant-plane
certificates are a positive screen of frame 1119 only, not an exhaustive
general-linear search.

The sequential-affine layer exhausts all twelve canonical factor formulas,
all `45` parent-unit graph pivots, all three anchor orders, and the complete
canonical stabilizer cosets.  Its tracked `180,886`-record witness stream is
independently replayed without the producer's affinity masks and is checked
against the exact source partition.  It is a proved structural layer, not a
sample or negative-search maximality claim.

On its exact residue, a two-stage graph theorem closes `417,828` rows.  The
canonical type-49 charts with pivots `1`, `3`, and `5` close `108,864`: pivot
`3` closes `107,778`, and the disjoint pivot-1/5 extension closes `1,086`.
The generic certificate contributes another `308,964` rows, disjoint from
the already accepted double-graph and unit-minor rows.  Independent exact
replay reconstructs every first graph, restricted-parent unit slope,
final-coordinate independence identity, third-factor affinity identity, and
the degree-transfer regressions.  The generic artifact has SHA-256
`8a61846547b6a8ab1984a7ebe8273fd7326316c8a83c040af377a6251b21937c`
and semantic digest
`b82343d4aaf5225a6c1efaa454f5a8bad2622e4cd24f9d75603456393cbe0a1f`.
A separate fixed two-by-two Jacobian-minor layer closes `117` rows; `97`
overlap the pivot-3 double-graph layer and none overlaps either later
double-graph increment, so it contributes only `20` further rows.  The exact
all-family union has `417,848` rows and leaves `1,221,055`, whose canonical
source-order SHA-256 is
`432854b7f00b57c5cf0009033e3ddfd3f4cb702bafed8fad2e5e69b369f30597`.
These are positive structural certificates; the construction census over 45
first-graph charts is not used as a negative maximality theorem.

Three stricter final-equation layers then close `58,753` further rows.  The
direct-final certificate retains `128,198` witness occurrences from ten
canonical charts and forms the fully denominator-cleared third equation
after two parent-unit graphs.  Exact affinity in a remaining coordinate
closes a priority union of `58,673` rows.  Its SHA-256 is
`6ed192d1dd2f814ae914349ec2dbcc654ffb663669b85f1b289fa37feb147f26`
and its block-stream semantic digest is
`7cd37ee421c651563bb6dbeae45b6711b71839893ba53abfb7240b1e165f2b1a`.
The primitive-direction certificate applies the same theorem after a
unimodular two-coordinate change and adds `23` disjoint rows; its SHA-256 is
`af0d1964840975e324d2c0181e732142ccd4e35c88ab4fc2702b6c70e6389bde`.
A support-three unimodular-direction extension adds another `57` disjoint
rows; its SHA-256 is
`c900dd68143d6228847124e4bc5891f440e0d116e2aabbaf2f0e28647f9fdbb3`.
Hostile full-record and source replay passed all three layers.  Their exact
union leaves `1,162,302` rows, whose packed source-order digest is
`a76a7c2cd6631c2d9724b450540bec7f3be6c106a41ae41f1736bbd2755a5ca4`.
None of these positive screens is used as a maximality claim.

The tested deterministic full colored occurrence/support key gives no
compression: it is singleton on the unresolved set.  A different
algebraically sufficient quotient is not excluded.  The generic
concurrence lift reduces a presentation to four bilinear equations in ten
variables, with fixed-base complex fiber length at most six, but it does not
turn the projection into a cover.  The stored CAS-produced RUR branch is
verified exactly and gives an internal corank-one ramification point with every parent
bracket nonzero; interval evaluation of all 26,740 residual factors proves
that no fourth factor appears there.
Accordingly the next triple certificate must include the concurrence-chart
frontiers and sheet attachments; support signs or a raw discriminant alone
cannot decide compactness.

A proposed Gale-dual shortcut has also been rejected exactly.  The displayed
bracket formulas are normalized-chart identities with unequal column
multidegrees, so termwise Pluecker complementation omits the independent
column rescalings needed to normalize a Gale kernel.  At exact isolated wall
centers for all six residual factor kinds, the original factor vanishes but
the naively complemented equation is nonzero after the normalized Gale
involution.  This rules out that affinity scan, not Gale duality itself; any
future dual construction must transport the full labeled occurrence
determinant with all normalization weights retained.

That corrected construction has now been screened on the six pinned hard
triples.  Across all `241,920` simultaneous `S_8` images it produces no
common three-coordinate affinity block, no triangular unit graph, and no
survivor among `20,321,280` coordinate Jacobian minors or `365,783,040`
sparse decomposable-minor sums.  The last two are rigorous necessary-filter
no-gos for the tested parent-unit families, not ideal-saturation theorems.
Thus corrected Gale plus reframing does not rescue any hard canary by the
existing affine/unit methods; boundary-aware dual or Coble transformations
remain logically open.

The standard coordinate-center Cremona involution has now been excluded just
as sharply.  On the source coordinate torus it is componentwise inversion,
so even its 17 novel target-nonuniform bracket divisors have singleton fibers
and supply no exceptional motion.  Exact all-`S_8` canary screens again find
no common square-affine block or triangular unit graph.  This is a bounded
no-go for the standard marking, not a theorem against longer Coble/Weyl words.

Literal contraction of three private extension columns also requires a
stratified treatment.  An exact row-2599 family crosses one and only one
rank-one quotient loop wall while the private triple stays independent and
all prescribed brackets remain strict.  Separately, two decomposable
alternating three-forms give a `6+6+6` separately convex model homotopy
equivalent to `SO(3) x SO(3)`, with nonzero `H_6`.  Thus a contraction proof
must retain every loop-specialization face and use the full occurrence
coupling; fixed uniform strata or separate convexity cannot prove the target.

There is nevertheless a positive loop-completion theorem on the
simultaneous-feasible side.  If the 56 signature traces of three private
extensions meet all four antipodal sign classes, every realizing private
triple is independent.  Retaining all eight quotient loop walls then gives a
contractible oriented-span image; the ambient loop complex has f-vector
`(128,352,336,112)`.  The criterion holds for `1,625,014/1,750,540` triples
in the stored 220-signature family.  Its scope is decisive: these private
cones exist over `F_1 intersect F_2 intersect F_3` and are empty on the
triple-bad locus, so a dual Gordan-block or Alexander/Leray bridge is still
needed before this topology can address triple `H_c^0`.

## Exact state of the pair endpoint

For

\[
 T=B_0\cap B_1\cap B_2,
 \qquad E_{ij}=(B_i\cap B_j)\setminus T,
\]

the remaining alternating pair differential has the canonical decomposition
(conditional on the still-unproved triple endpoint `H_c^0(T;R)=0`)

\[
 0\to\bigoplus_{ij}H_c^1(E_{ij};R)
 \to\ker H_c^1(D)\to\ker\beta\to0.
\]

On a common finite relative cellular model this is a three-term integral
cochain
complex

\[
                  C^0\mathop{\longrightarrow}^{N}C^1
                     \mathop{\longrightarrow}^{M}C^2.
\]

For the rational 9DVL target it is enough to prove middle exactness after
reduction modulo two.  Indeed `MN=0` and
`rank_F2(N)+rank_F2(M)=dim C1` force the same rank equality over `Q`.
Thus signs and Smith-unit bookkeeping are optional, while geometric
coverage, zero-weight faces, multiplicity parity, triple-relative exits, and
parent infinity remain mandatory.  Same-factor root and occurrence choices can be
eliminated through degree one by unit pivots on their proved generic strata,
but the specialization and infinity blocks are not yet constructed
globally.

The exact tapered two-dimensional ribbon remains a useful frontier canary.  Its
cellular matrices have

```text
N : 12098 x 4917, rank 4917
M :  7180 x 12098, rank 7180
```

and leave one free middle class, supported in `H_c^1(E_02)`.  A complete
bottom-edge replay finds five shears common to all 50 exact witness-support
pairs along the relevant end.  The required two-parameter audit is now also
complete for this canary.  It restricts all 26,740 residual factors, covers
all 84,840 labeled wall occurrences with fixed parent-unit certificates, and
finds 1,707 active block-1 factors.  Tensor Bernstein coefficients put the
only seven possible zeros on the triple-relative side or the double
parent-wall corner.  Hence the actual residence component is a proper
relative quadrilateral, and the signed product-strip attachment kills the
unique class integrally.

This repairs the row-2599 canary, but it does not supply the global atlas:
other components and parent cells still require complete two-parameter
frontiers and incidence coverage.  The dependency-free rectangle model
continues to show why pointwise first exits alone are invalid.

The separate row-2599 flow-triangle canary now also has all three relative
pair-wall collars.  The exceptional `p01` edge is repaired by an exact
four-stage nonradial tangent path on `[1234]`, `[1367]`, and `[2467]`; its
semantic digest is
`e3df18c1a98ccca9e022832e3656c7e2ae3a9c7c822a153c7fc40e9519e08016`.
Five exact bivariate patches now join the nonrelative swept face `K(p01)` to
that collar while retaining both bad-block circuits.  Their product with the
block-mass interval has ordinary boundary
`+K(p01)-Q(p01,block0)+Q(p01,block1)`; every other face is relative, collapsed, or
paired internally.  A separate dense-bivariate implementation independently
replays the construction.  The simpler two-stage `p12` and `p20` collars give
two more independently replayed comparison prisms.  The honest local counts
are therefore `3/3` relative pair collars and `3/6` complete singular pair
comparison incidences.  A four-patch `H2` prism then joins the two block-2
pair-edge disks literally, with boundary
`+K(h2)-Q(p12,block2)+Q(p20,block2)`.  The total is now `4/6`; `H0`, `H1`,
and the primitive mixed `J` remain open, so there are still zero mixed `d3`
cells.

There is now a smaller invariant construction target.  One closure-complete,
signature-labelled regular subdivision of the compactified parent base
computes all triple and exclusive-pair subcomplexes directly.  Its
barycentric two-skeleton canonically supplies an integral signed lift and
`MN=0`, so a separate sign search is unnecessary.  The existing 178-point
bank cannot be promoted to that object: its exact audit has zero certified
global adjacency edges, strict closure pairs or triples, and infinity cells.
The first missing block is the coverage-certified global cell universe named
in `data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json`.

## Routes retired by exact counterexamples

The following are not current proof routes:

* switching to diagonals four through nine: their present complete
  certificate inputs are larger or require equally global chamber/frontier
  data;
* the 135-class `UOM(3,8)` private-witness shortcut: the framed rank-three
  base also contains unprescribed flag minors, and the rank-at-most-two locus
  has codimension two and can contribute in the target degree;
* raw discriminant-gradient or saturation Gröbner bases: even an optimized
  828-term discriminant reached large F4 matrices without an algebraic
  result, while the concurrence equations are a strictly smaller endpoint;
* a universal fixed-base submersion and a forced fourth factor at
  ramification: each has an exact counterexample; the tested full-support key
  also gives no compression, without excluding a different invariant;
* local root connectivity or same-factor occurrence `H_1` alone: these
  remove choice fibers but do not determine signed end incidence;
* a local `I x R^7` Thom argument: it does not control global ends or
  exceptional fibers;
* a globally fixed triangular label order: a GP-valid type-49 wall has 22
  common compatible roots, all pointing upward for one fixed order, and
  equivariance transfers the obstruction to every fixed order;
* termwise Gale complementation of normalized bracket formulas: it changes
  their zero sets because the formulas are not column-multihomogeneous; and
* pointwise tangential first exits: without a full two-parameter frontier
  they need not assemble into a closed proper strip (the completed frontier
  repairs the row-2599 canary only).

## Recommended next certificate

Keep diagonal three.  Do not launch another orbitwise CAS sweep.  The two
remaining work products should be finite, boundary-aware objects:

1. a concurrence-chart roadmap for the `1,162,302` triple residue, retaining
   rank drops, interpolation/gauge frontiers, parent infinity, and sheet
   attachment; and
2. a coverage-certified labelled regular master closure poset, its genuine
   infinity subcomplex and barycentric order-two incidence, followed by the
   exact mod-two middle-rank replay sufficient for the rational target.

Discovery tools may use modular fingerprints, SAT, and sampled charts, but a
theorem entry must end in exact positive identities or a complete finite
relative boundary complex.  CAS jobs should be restarted only after a
structural reduction makes their output bounded and replayable.
