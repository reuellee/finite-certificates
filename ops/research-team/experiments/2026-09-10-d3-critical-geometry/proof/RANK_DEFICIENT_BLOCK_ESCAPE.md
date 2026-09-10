# Eliminating rank-deficient blocks for kinds49,50,51

## Theorem

Consider the parent-free, collision-free collinear triple locus with all
factor kinds among49,50,51. Its closed subset where at least one of the
three transverse circuit blocks has rank at most3 has H_c^0=0.

Together with the earlier collinear theorems, the only remaining collinear
critical branch has factor kinds49,50,51, all three block ranks4, stacked
rank11, and a one-dimensional common stress intersection. No vanishing for
that final branch is claimed.

## A deficient block forces a selected plane to contain L

For one factor S, let s be its concurrence on L. Suppose a selected S plane
does not contain L. Its projection onto the transverse two-space has rank2.
If two of its parent columns have the same transverse direction, the actual
line joining these parents contains s: the plane meets L exactly in s, and
the kernel of its transverse projection is that point.

Such a parent pair must have identical incidence patterns in the selected
four S triples. Indeed, if another selected plane contains the first parent
but not the second, uniformity excludes the second from that plane. That
plane's intersection with their parent line is then the first parent alone.
Since it also contains s, this would make s a parent, which is impossible.

For canonical49 and51 no two labels have identical nonempty incidence
patterns. For canonical50 the only such pair is its two leaves7,8 in the
last triple378. The relevant canonical supports are

    49: 123/145/246/357,
    50: 123/145/246/378,
    51: 123/145/267/468.

Consequently every non-L plane row has all its three sparse coefficients
nonzero, except that row378 of kind50 may have its coefficient at3 equal
to zero when g_7=g_8. Its coefficients at leaves7 and8 remain nonzero.

If no selected plane contains L, the four rows are independent:

* In49, the unique leaves6 and7 force the coefficients of rows246 and357
  in a row dependence to vanish. The remaining rows123 and145 have only
  one common label and have nonzero coefficients, so they are independent.
* In50, leaves5 and6 kill rows145 and246, and either leaf7 or8 kills row378.
  The remaining row123 is nonzero.
* In51, each row has its own leaf (3,5,7,8 respectively), with nonzero
  coefficient; all four dependence coefficients vanish.

Thus a deficient block has a selected plane containing L. Conversely such
a plane has a zero transverse row. With no parent on L, its three projected
directions coincide. These assertions hold under every relabeling.

## Fixed three-label cluster bases

Fix one such selected triple I. Work on the full collinear subset where
L lies in its selected plane, equivalently g_i=g_j=g_k for its three labels.
That row of the full stacked matrix is identically zero. Hence rank M is at
most11 on the entire associated projected base.

This projected base consists of one marked direction of weight3 and five
marked directions of weight1, with every multiplicity at most3. It is an open
submanifold of (RP1)^6. The proper free PGL2 quotient is a three-dimensional
manifold. Every component is noncompact. To construct an escaping path,
first separate the five singles and keep them away from the weight3 point.
On the complementary affine line, bring four consecutive singles together,
creating at most a threefold cluster until the omitted fourfold-collision
endpoint. The fifth single stays distinct.

No projective renormalization gives an allowed limit at that endpoint. A
bounded invertible limit retains a fourfold collision. A rank1 limit with
kernel at the fourfold cluster collapses the four outside labels (the
weight3 point and the fifth single). A kernel elsewhere collapses at least
four labels as well. Every possible target violates the multiplicity bound.

Remove the already-proved rank-at-most10 piece. On the remaining rank11
locus, the unique height lift modulo shears and common scale gives a local
homeomorphism to an open feasible subset of this full projected quotient.
Parent signs, projected multiplicity bounds, finite sign lifts and the chosen
original component are retained exactly as in the preceding collinear
theorems. A compact incidence component would have compact nonempty open
image in a base with no compact component, which is impossible.

Thus the whole selected-plane-containing-L piece has H_c^0=0, including its
lower ranks by localization. It is closed in the parent-free collision-free
collinear locus. The finite union over the twelve selected triples has
H_c^0=0 by restriction to its closed pieces. The rank-deficient locus equals
this union by the support argument above, proving the theorem.

## Exact remaining rank alternative

After these removals all three blocks have rank4. The identity

    rank M=rank B_P+rank B_Q+rank B_R
           -dim(row B_P intersect row B_Q intersect row B_R)

then makes rank11 equivalent to a one-dimensional common stress intersection.
This is a sharply stated remaining condition, not a proof that vertical
criticality is impossible there. The known rank11 canary is vertically
regular and is consistent with this boundary.
