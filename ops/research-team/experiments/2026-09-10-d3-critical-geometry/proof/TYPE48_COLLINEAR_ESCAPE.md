# Complete collinear escape with a global48 factor

## Theorem

For any three distinct primitive residual factors in any original normalized
uniform rank4 parent component on eight labels, suppose one factor has global
kind48. The full locus where their chosen ordinary concurrences are collinear
has H_c^0=0, including concurrence collisions. The other two factor kinds and
all relative labels are arbitrary.

Use the previously proved closed-piece localization to remove collisions,
parents on the common line, and the rank-at-most10 common-line matrix locus.
It remains to treat rank11 with the common line disjoint from all parents.

## The complete quadrilateral and its projection center

Use the kind48 factor as P, with ordinary support

    123/145/246/356.

In its p-contraction the four selected planes give four projective lines in
general position. Their ordered projective frame fixes the six used parents
as their six pairwise intersections: they form a fixed complete quadrilateral.
The other two parents,7 and8, are omitted from this P support.

The common concurrence line L through p has a direction z in this projected
plane. Since no parent lies on L, z differs from each of the six fixed high
parent points. Project the six fixed points from z onto the projective line
of directions through z. These are their transverse directions g_1,...,g_6
in the common-line model.

Retain also the transverse direction of each omitted parent. The full
parameter space D is therefore a projective-line-squared bundle over

    RP2 minus the six fixed quadrilateral points.

It is a connected noncompact four-dimensional manifold. Its bundle projection
is open with connected fibers, so a compact connected component would project
to a nonempty compact open component of the punctured projective plane,
which is impossible. The restrictions that projected multiplicities be at
most3, and the eventual strict parent-lift restrictions, are open restrictions
on D. An open subset of this manifold cannot have a compact component: such
a component would be compact, open and closed in D.

## The P block has rank exactly3 throughout this base

The six fixed projected points have homogeneous coordinates (g_i,b_i^0),
where b^0 is a choice of height in the projected plane above the transverse
line. Their two transverse coordinate rows and b^0 are linearly independent
and lie in the kernel of B_P on these six columns. Hence rank B_P is at most3.

If z lies on none of the four selected P lines, all three coefficients in
each sparse row are nonzero. The incidence between the four rows and their
six parent labels is the edge incidence of K4: each parent label belongs to
exactly two rows, and every pair of rows shares exactly one label. In any
linear relation among these rows, the coefficient equation at a shared label
determines one row coefficient from the other by a nonzero ratio. Connectedness
of K4 therefore makes the space of row relations at most one-dimensional.
The rank is at least3, and consequently exactly3.

If z lies on one selected P line, that row is zero. It cannot lie on a second
selected P line, since their intersection would be one of the six excluded
high parent points. Each of the other three rows has a nonzero coefficient
at the label it shares with the zero row. That label occurs in no other
nonzero row, so these three rows are independent. Again rank B_P=3.

This proof retains all projected coincidences and centers on selected lines.
The two omitted columns are zero columns of B_P and do not change its rank.
Thus the full stacked matrix has rank at most3+4+4=11 on all of D, before any
feasibility or compatibility assumption is imposed.

## Reconstruction and the open rank11 graph

The kernel of B_P on the six high columns has dimension3, precisely the two
transverse shear directions and the direction b^0. In any uniform height lift,
its high-parent b vector must have a nonzero b^0 coefficient modulo shears.
Otherwise the six high columns would have b equal to a transverse linear
functional, and any four of them would lie in a three-dimensional parent
subspace, contrary to uniformity.

Normalize this coefficient by the common height scale after removing the
four shears. It recovers exactly the fixed complete-quadrilateral
p-contraction, and therefore recovers its center z. The four ordinary
projected P lines determine their ordered frame uniquely. The two retained
omitted directions recover the remaining parameters of D. This shows that
the parameter description loses no branch: conversely, a parent on the
specified collinear locus determines these same data continuously.

On the rank11 locus the stacked kernel, modulo its four shears, has dimension1.
After the indicated scale normalization the height lift is unique and varies
continuously in local bundle charts. All strict parent signs and the requirement
of belonging to a chosen original parent component are open. The rank11
incidence is therefore locally homeomorphic to an open feasible subset of D.
Finite frame and parent-sign choices are retained; their identifications are
proper finite maps and do not affect compactness.

If a connected component of this rank11 incidence were compact, its image
in D would be compact and nonempty open. It would therefore give a compact
component of D, contradicting the preceding noncompactness. All rank11
components escape. The earlier closed-piece localization then restores lower
ranks, parents on L and concurrence collisions, proving the theorem.

## Boundary of the result

This completes the full collinear branch whenever one factor has global48.
It does not address noncollinear critical points, and does not assign a new
numerical source-orbit count. In particular, stationary but non-flat height
behavior for kind48 is not assumed absent; this proof uses the complete
quadrilateral geometry instead of such an assumption.
