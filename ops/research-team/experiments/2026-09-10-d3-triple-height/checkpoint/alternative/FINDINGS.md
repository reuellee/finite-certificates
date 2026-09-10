# Alternative-track findings

## Current mathematical outcome

This track supplied a uniform ruled-quadric normal form, the split-row
extension of the two-column affine proof, and an exact populated rank-six
model for the remaining triple obstruction. It closes no original diagonal
and claims no new triple orbit. The original score remains2/9.

The original prover subsequently developed a broader concurrence-height
argument for all remaining type50/type51 factor pairs. That proof and its
accepted coverage are owned by the original/referee tracks. The unresolved
endpoint is now the global triple-bad compactness obligation, or the stronger
factor-triple escape theorem; rational conic charts are no longer presented
as the primary next step.

## Uniform geometry and the eight-case extension

`REGULUS_NORMAL_FORM.md` proves that every one of the45 balanced pair source
records has a selected nonzero-plane/smooth-split-quadric presentation.
`REGULUS_GEOMETRY_GATE.json` records306 qualifying ordered presentations.
Every plane section has a rational forbidden smooth marker on two base
charts, including source573. Reducible conics are retained. Canonicaltype50
with moving label3 does not satisfy the skew-line certificate; the theorem
uses selected pivots rather than every degree-two pivot.

The simpler parent-point marker gate covers44 records with285 choices.
Combining it with the smooth-quadric gate gives238 choices over those44.
These imply rational charts, with the stated treatment of reducible conics;
they alone do not imply total H_c^1 vanishing or constant interval components.

`TWO_COLUMN_SPLIT_ROW_EXTENSION.md` removes the original two-column theorem's
shared-moving-triple restriction on Q. With two e-only and two j-only rows,
the possible mixed determinant coefficient vanishes because all four rows
annihilate the retained common direction S. This applies to source indices
254,256,482,483,486,488,497,499, complementing the original27 presentations.
The later broader concurrence-height proof subsumes this extension. No
separate double counting is appropriate.

## Exact remaining obstruction and scoped escape

`TRIPLE_RANK6_GATE.json` reconstructs the eight Q/R concurrence equations
for the actual predecessor fixture

    P=123/145/246/357,
    Q=127/158/234/357,
    R=236/248/456/578.

The homogeneous eight-by-ten height matrix has rank six and exactly the
three shears plus scaling in its kernel. Fixing the first four parent
heights gives an eight-by-six rank-six matrix and a unique solution when
the two projected concurrence directions are held fixed. A nonzero maximal
minor and the full kernel are recorded. The fixture therefore establishes
that the zero-dimensional fixed-direction obstruction is actually populated.

Allowing the projected concurrence directions to vary while retaining the
parent projection gives two exact triangular equations in h5,h6 over
(h7,h8). `TRIPLE_RANK6_MODEL.md` proves escape for this entire fixed-projection
fiber, including both coefficient-zero cases, by successive affine-variable
elimination. The extra determinant factors are genuine parent units:
[2357]=-(4h5+h7), [2346]=-h6.

This fixture was already covered by the predecessor's square-affine height
escape. It adds no triple orbit. Its new diagnostic content is the populated
rank-six gate and the distinction between fixing and varying concurrence
directions.

The global next theorem is precise: exclude compact components in every
actual rank-six compatibility locus

    rank(M)=rank(M|b)=6

inside the projected-concurrence base, with strict parent signs retained.
Unlike the pair theorem's full-rank image, this compatibility locus need
not be open in its ambient base. Lower-rank positive-dimensional convex
fibers and the collisions with the first concurrence point have H_c^0=0.
Other concurrence collisions, all parent boundaries, allowed projected
coincidences, and anchor kinds outside the current type50/type51 chart must
be retained or covered by separately proved layers. The single triangular
fixture does not establish this global theorem.

## Route selection audit

D4 has a safe compact-support target because the source independently proves
parent H5=0, but its single-block Hc3 contribution and subsequent terms remain
open. D8 should use the direct H1(F_S) target; its historical one-parent loop
filling supplies no all-parent coverage. D9 should use direct reducedH0(F_S);
its exact chamber comparison still lacks a universal path or roadmap proof.
No parent H2/H1 conclusion was imported from the qualified58-exceptional-parent
contractibility source. The bounded D9 path attempt found no new global
consequence of the known convex private-column fibers. This audit does not
justify replacing active D3 with D4,D8,orD9.

A bounded Gale-presentation probe found no useful extension for the final
balanced cases: a type51 candidate stays type51, while type50 has no direct
proportional quartet match in the tested complete complementary-multidegree
support family. The discovery file is not an identity proof or a general
no-go theorem for Gale transformations with parent-unit factors.

## Evidence and review

The source45 input hash is pinned in `HANDOFF.json`. The marker and regulus
hypothesis gates use only the Python standard library. The exact triple
matrix and factorization checker uses rational SymPy arithmetic and checks
all70 original parent minors. Independent review was requested for each
frozen deductive statement. The referee independently accepted the normal-form theorem at its stated
geometric scope and reconstructed all306 presentations across45 records,
all238 compatible parent-marker choices across44, and the earlier285 marker
choices, with four hostile mutations. The new triple gate remains under
review; final referee reports supersede producer pending-review language.
