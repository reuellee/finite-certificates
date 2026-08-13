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
| **total** | **`77,282,660`** |
| **unresolved** | **`1,819,789`** |

Every polynomial identity counted here is replayed exactly over the integers;
the degree-two/three layers instead combine exact incidence classifications
with structural fiber theorems.  Modular arithmetic is used only to propose
identities.  Negative
search accounting is kept separate: 79 role frames are sufficient to replay
the positive coordinate-minor certificates, while exhaustion of that
coordinate-minor family used all 1,120 role frames.  The 61 constant-plane
certificates are a positive screen of frame 1119 only, not an exhaustive
general-linear search.

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

1. a concurrence-chart roadmap for the `1,819,789` triple residue, retaining
   rank drops, interpolation/gauge frontiers, parent infinity, and sheet
   attachment; and
2. a chamber-decorated receiver/end atlas populating `N,M`, including every
   two-parameter jump frontier, followed by the exact mod-two middle-rank
   replay sufficient for the rational target.

Discovery tools may use modular fingerprints, SAT, and sampled charts, but a
theorem entry must end in exact positive identities or a complete finite
relative boundary complex.  CAS jobs should be restarted only after a
structural reduction makes their output bounded and replayable.
