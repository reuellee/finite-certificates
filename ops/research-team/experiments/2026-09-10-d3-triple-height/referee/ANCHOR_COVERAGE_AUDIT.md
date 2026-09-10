# Independent audit: all-factor concurrence coordinates

## Verdict and source boundary

The proposed restriction to factor kinds 50/51 is unnecessary. Every one of
the six primitive global factor kinds has an ordinary four-normal occurrence.
Using such an occurrence, the four-line contraction model extends to all six
kinds, with a four-dimensional projected-parent parameter space and four
free parent heights. This is a coordinate-model extension, not a proof of
triple component noncompactness and not a new factor-pair count.

The exact final 1,162,302-row residue has not been reconstructed here. The
late-layer summaries do not themselves imply that every remaining row has a
50/51 anchor. No such residue-distribution assertion is accepted or needed
for the all-factor model below.

Sources read independently:

* `checkpoint/checkpoint/checkpoint/inputs/DIAG2_PIVOT_LABELED_PAIR_THEOREM.md`,
  opening factor-orbit table: global kind 36 contains occurrence kinds
  36,37,39,41,44,46,47; global kind 38 contains 38,42.
* `checkpoint/checkpoint/checkpoint/inputs/verify_derived_walls.py`, explicit
  ordered support table.
* `checkpoint/checkpoint/checkpoint/inputs/verify_derived_wall_sides.py`,
  `FOUR_ROW_TYPES={37,38,41,42,44,48,49,50,51}` and fixed-unit circuit proof.
* `checkpoint/checkpoint/checkpoint/inputs/RESIDUAL_STRATUM_NONCOMPACTNESS.md`,
  Sections 2–3: unit equivalence of occurrences and exact rank-three ordinary
  wall circuits throughout the parent cell, including simultaneous walls.

These are inherited source theorems, rather than a new numerical audit of
their complete occurrence census.

## Canonical ordinary anchor table

In the following table the four listed triples are ordered. Their projected
lines are L1,...,L4. A high parent occurs in two of these triples; a low
parent occurs in one; an omitted parent occurs in none. The frame column
lists three high parents with independent projections, then a fourth high
parent used to normalize the remaining vertical scale.

| Global kind | Ordinary occurrence | High / low / omitted | Height frame |
|---|---|---|---|
| 36 | 123 / 124 / 345 / 567 (type37) | 5 / 2 / 1 | 1,3,4 ; 2 |
| 38 | 123 / 124 / 345 / 678 (type38) | 4 / 4 / 0 | 1,3,4 ; 2 |
| 48 | 123 / 145 / 246 / 356 (type48) | 6 / 0 / 2 | 1,2,4 ; 3 |
| 49 | 123 / 145 / 246 / 357 (type49) | 5 / 2 / 1 | 1,2,4 ; 3 |
| 50 | 123 / 145 / 246 / 378 (type50) | 4 / 4 / 0 | 1,2,4 ; 3 |
| 51 | 123 / 145 / 267 / 468 (type51) | 4 / 4 / 0 | 1,2,4 ; 6 |

For kinds36 and38, projected parents1 and2 coincide at L1∩L2. This
coincidence is required and must not be deleted. Projected parents3 and4
are L1∩L3 and L2∩L3, respectively; together with parent1 they are
noncollinear because no three of the four lines concur. For kinds48–50,
parents1,2,4 form the triangle L1∩L2,L1∩L3,L2∩L3. For kind51,
parents1,2 lie on L1 and parent4=L2∩L4 does not. Thus every displayed
projected frame has rank three. Uniformity of the four original parent
columns in the height frame gives a nonzero fourth height after the first
three have been sheared to zero.

## Proof of the coordinate extension

On the chosen factor wall the four selected normal rows have rank exactly
three and every three are independent. Their common projective kernel p is
unique and depends continuously on the parent. It cannot be a parent point:
each parent belongs to at most two selected triples, so at least one selected
triple not containing that parent would give a forbidden zero parent bracket.

Contract by p. The selected triples become four projective lines in general
position. Fix their ordered dual projective frame. Every high parent is their
prescribed pairwise intersection. Every low parent moves on its line and
avoids the other three lines; otherwise a selected triple not containing it
would have zero parent bracket. Every omitted parent avoids all four lines.
Choose one forbidden intersection as the point at infinity on each low
parent line, and one forbidden line as the line at infinity for each omitted
parent. These give global affine coordinates for these parent positions.

If there are k high parents, then the number of low parents is 12−2k and
the number omitted is k−4. Hence the projected parameter dimension is

    (12−2k) + 2(k−4) = 4.

Additional projected coincidences allowed by the original uniform parent
conditions are retained. No independence of all projected triples is assumed.
Configurations for which no uniform lift exists simply have empty height
fibers; this is preferable to adding unsupported projected exclusions.

Use the displayed three high parent projections to subtract the three height
shears. The fourth high parent height is nonzero by its original four-parent
bracket. Its sign is constant on each normalization sector; divide by its
absolute value, so the normalization uses positive scale and leaves that
height equal to +1 or −1. Exactly four free parent heights remain. Every
original parent bracket is affine in these heights. Therefore fixed parent
signs cut out a possibly empty open convex four-dimensional height cell.
If one fixes a connected original parent component, it selects the entire
nonempty fiber, because the fiber is connected. The allowed projected base
is open: it is the projection of the open strict-inequality residence in
the projected coordinates and heights.

As in the inherited pair proof, normalized column signs and the projective
frame lifts must be recorded on their finitely many clopen sign sectors.
Local trivializations of the projective height line bundle suffice; a
globally chosen signed representative of every point of RP2 is not assumed.

For the parent contraction frame one can be more explicit. In the original
normalized matrix choose the nonzero vector p to be the exterior product of
the first three ordered ordinary normals. Write
`n4=a1*n1+a2*n2+a3*n3`. The three coefficients are nonzero fixed-sign
circuit-unit ratios. The quotient coordinates
`v -> (a1*n1(v),a2*n2(v),a3*n3(v))` identify the four planes with the three
coordinate planes and the sum-zero plane. The height functional
`ell(v)=p^T*v/(p^T*p)` is globally defined and satisfies `ell(p)=1`.
For each parent choose one fixed excluded plane evaluation and divide its
column by the absolute value of that evaluation. This is a positive column
scaling. The resulting evaluation has a fixed sign on the original parent
component; high projected columns are fixed signed vectors, and the low
and omitted columns have the affine coordinates described above. This
construction supplies the parent-side lift and shows that no unexplained
projective sign identification is used in the height shears or scale gauge.

The same source replacement gives ordinary occurrences for Q and R, even if
their customary displayed occurrence is a three-row localization. Thus their
concurrence points can also be made unique before applying the eight-equation
height construction. This avoids retaining an arbitrary point of a
localization kernel and introducing an unnecessary projective-line fiber.

## Consequence for the remaining triple model

For all factor kinds, on q≠p and r≠p the eight concurrence equations are
affine in the four free parent heights and the two extension heights.
The parameter base has dimension eight (four projected-parent coordinates
plus the two projected concurrence directions in RP2). The rank≤5 locus
has either empty or positive-dimensional open convex height fibers; its
compactly supported degree-zero direct image vanishes. The rank6 locus has
at most one height lift and must impose consistency of the augmented system.
Its feasible compatibility locus need not be open in the eight-dimensional
base. Proving that each of its components is noncompact is still missing.

When q=p or r=p, that block becomes a condition only on projected parents.
The other block has at most four equations in five heights, hence a
positive-dimensional feasible fiber. When both equal p the fiber has all
four parent heights. Concurrence collisions q=r≠p, equal projected
directions with different heights, lower coefficient rank, and all original
parent components remain part of the model; none may be removed as generic
exceptions.

The inherited rank6 fixed-direction fixture and triangular escape are not a
proof of this compatibility-locus theorem. They remain zero new triple
credit. Original injectivity and the original triple obligation stay open
at2/9 until the full noncompactness theorem or a direct original-space
argument is established.
