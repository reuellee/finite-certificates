# Complete collinear escape with a parent-line factor

## Theorem

For every original uniform rank4 parent on eight labels and every normalized
component X, fix three distinct primitive factors with at least one in global
family36 or38. Choose the corresponding ordinary37/38 occurrence for that
factor. In the collision-free triple zero set, the closed locus where its three distinct
ordinary concurrences are collinear has no compact connected component.

Equivalently its H_c^0 is zero. Adding the already-proved concurrence-collision
pieces gives the same conclusion for the full collinearity locus. All rank
changes, projected coincidences and original parent components are retained.
The noncollinear part of such a triple is outside this theorem.

## Reduction to the rank11 parent-free part

Use `COLLINEAR_RANK_ESCAPE.md` to remove, in order, parents on the common line
and then the full rank-at-most10 collinear piece. Each is a closed subset at
the corresponding step and has H_c^0=0. It remains to handle rank11 with all
parents outside the concurrence line L.

Name the parent-line factor Q. Its ordinary first two planes share a root
pair a,b, and q lies on the actual line(Y_a,Y_b). Because q lies on L and
neither parent lies on L, projection from L gives

    [g_a]=[g_b] in RP1.

The two corresponding sparse rows of B_Q are proportional or zero. Therefore
rank B_Q is at most3 and rank M is at most11 throughout the entire projected
parameter space having this fixed equality. This is an identity on that base,
not merely a rank bound at already-feasible parents.

## The projected base and its noncompact components

Let E be the space of ordered eight-point configurations in RP1 such that
g_a=g_b and every multiplicity is at most3. Regard the equal pair as one
marked point of weight2 and the other six labels as marked points of weight1.
Then E is an open submanifold of (RP1)^7. It has at least three distinct
directions. The PGL2 action is free and proper by the rank-one-limit proof in
`COLLINEAR_RANK_ESCAPE.md`, so B=E/PGL2 is a four-dimensional Hausdorff manifold.

Every component of B is noncompact. Here is an explicit escaping path from
an arbitrary starting component. Perturb the six weight1 points slightly so
they are mutually distinct and avoid the weight2 point. This can be done
within E and within an arbitrarily small neighborhood of the starting point:
all forbidden multiplicity conditions remain absent. On the circle choose
two consecutive weight1 points nearest to the weight2 point on one side.
Move the nearest one into the weight2 point, creating an allowed weight3
cluster. Then move the next one towards that cluster. Before the endpoint
all multiplicities remain at most3; at the omitted endpoint precisely four
labels coincide. The other four labels remain at distinct directions away
from this cluster.

This path has no convergent subsequence in B as that endpoint is approached.
If it did, choose representatives after projective transformations converging
to an allowed target, using a local slice for the proper free action. Normalize
the transformation matrices and take a subsequence. An invertible limit
retains the fourfold collision, which is forbidden. For a rank1 limit whose
kernel is the collision point, all four outside labels converge to a single
image point, again forbidden. If its kernel is elsewhere, at least four
labels outside that one kernel direction converge to the same image point.
There is no allowed limit in any case. The path therefore escapes in the
same component, proving that component noncompact.

The same argument works if the orientation-preserving projective subgroup is
used to keep an explicit frame-sign convention. The finite sign identifications
are proper and do not affect this compactness conclusion.

## Rank11 is an open height graph over this base

On E the matrix M has rank at most11 everywhere. Its rank11 locus is therefore
open. Modulo the four height shears, its kernel is a line. The parent-unit
linear scale gauge of `COLLINEAR_RANK_ESCAPE.md` makes the corresponding
parent-height lift unique wherever that lift is uniform. Locally these lifts
vary continuously, since the kernel line bundle has constant rank. Their
prescribed strict parent signs are open conditions. Thus the uniform rank11
incidence projects locally homeomorphically to an open feasible subset of B.
Here B is the full open-manifold quotient just analyzed; the feasible subset
is an open subset of that manifold and is not assumed to be the whole base.

Any finite frame and column-sign choices are retained. Restricting to a fixed
original parent component also leaves an open incidence subset. No extra
compatibility equation is needed on E: after four shears a rank11 matrix has
exactly the one scaling direction, and the nonzero parent-bracket condition
decides openness of the admissible lift.

If a connected component C of this rank11 incidence were compact, its image
in B would be both compact and nonempty open. A compact open subset of a
Hausdorff manifold is closed as well, so it contains a compact connected
component of B. This contradicts the preceding escaping-path proof. Thus
every rank11 component is noncompact.

Closed/open compact-support localization, first for the lower-rank part and
then for parents on L, completes the theorem. The same prior localization
adds the concurrence-collision union if desired.

## Scope boundary

This is a deductive theorem for all relative labels, all actual projected
specializations, all original parent components and an arbitrary choice of
the other two factor kinds. It is not a new numerical source-orbit count.
For triples with no global36/38 factor, the remaining parent-free collinear
rank11 locus need not lie over this fixed-equality base. Its critical part
remains a separate obligation, as does the noncollinear critical branch.
