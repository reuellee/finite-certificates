# Independent audit of the two-dimensional residence quotient

Verdict: **the light-label geometric lemma survives this challenge**, provided the proof uses compact-support direct image and retains entire residence fibers. The joint two-label domain need not be convex. Calling its projection proper would be incorrect because its fibers are open cells.

Fix five projective-frame labels outside the one or two moving labels. Fix the remaining nonmoving columns and the projective normal rays of every chosen incident support plane. Distinct parent triples have distinct support planes by uniformity, so a label of degree two moves in the projective line which is the intersection of its two incident planes. A label of degree one moves in its incident projective plane.

For each moving label choose a parent bracket using that label and three nonmoving labels. Its zero cuts out a projective hyperplane in the motion space which does not contain the current point. This defines an affine chart valid on the entire parent sign cell: no point in the cell can meet the chosen zero bracket. Thus this choice introduces no artificial interior boundary.

With a single degree-one label, all parent brackets are affine in its two affine coordinates; fixing the parent chirotope gives an open convex domain in R^2. Its nonempty components are open two-cells.

With two degree-two labels, write the two pencil coordinates as `(s,t)`. A parent bracket is affine in each variable separately. Brackets containing both labels may have an `st` term. Consequently the joint residence domain need not be convex, but its intersections with every horizontal and vertical line are empty or open intervals, since each is an intersection of strict affine inequalities. Shared support planes introduce no further equations: both points lie in the fixed plane already, and degeneracies which would fail to span it are excluded by the retained parent bracket signs.

Let C be a connected component of this open residence domain. Its projection to the s-axis is an open interval I. A nonempty full vertical interval belongs to one connected component, so C's vertical fibers are also nonempty intervals over I. The projection is open. The convex-valued lower-semicontinuous fiber map admits a continuous section, obtained from local sections by a partition of unity (a semialgebraic section can also be chosen). Vertical straight-line contraction retracts C onto the section graph, which is homeomorphic to I. Therefore C is contractible. Being an open connected two-manifold, C is an open two-cell, with compact-support cohomology zero in degrees zero and one.

For a semialgebraic map p to the fixed plane/column profile, the stalks of `R^j p_! Q` are the compact-support cohomology of these entire fibers. A finite union of open two-cells still has no groups below degree two. Thus `R^0 p_! Q=R^1 p_! Q=0`; compact-support composition yields the asserted low-degree vanishing on the source. This uses `p_!`, not a false properness claim about p.

The profile fibers preserve every selected support normal up to positive scaling on their parent sign component. Hence they preserve the two factor equations when each factor's chosen support is globally equivalent to its zero locus, as supplied by the fixed-unit circuit source identities. This last equivalence remains a source dependency, not a consequence of degree counting alone.

## Hard case is genuinely realized

The combinatorial obstruction in the pair track is not eliminated by uniformity. The two type50 supports

`P=123/145/246/378`, `Q=567/158/268/347`

have an eight-triple union of degree `(3,3,3,3,3,3,3,3)`. An exact point on both walls in the canonical nine-coordinate gauge is

`(a,b,c,d,e,f,g,h,i)=(7,-8,-4,-17/4,2,-3,2,-2116/67,-8)`.

`verify_hard_pair_point.py` reconstructs all 70 parent brackets and the two literal four-by-four derived-normal determinants using standard-library rational arithmetic. All parent brackets are nonzero, both derived determinants vanish, and each support has rank three. It also checks that Q is the specified permutation of canonical type50. Therefore both walls and the degree obstruction occur in actual uniform parent geometry.

This is not a counterexample to `Hc1(H_f intersect H_g)=0`. It proves only that the light-label argument cannot cover every nonempty pair by selecting the unique type50 occurrences. Any universal pair-wall vanishing theorem must supply another geometric motion or topological argument for this actual locus.

The discovery inspected 74 rational slices before finding the point. No other hard kind pair was enumerated. The exact symbolic factors are in `HARD_PAIR_EQUATIONS.json`; their fixed-gauge common constant-translation space and common diagonal-weight space were both zero in a supplementary exact linear-algebra check. This does not exclude nonlinear motions or motions revealed by a different frame. Neither space calculation is needed for the point certificate.

Smallest next discriminator: on this one genuine hard50+50 component, construct a second independent proper fiber motion or compute whether the seven-dimensional root-residence domain has a compact six-cycle. A point or a one-dimensional escape cannot decide its Hc1. The proposed universal two-dimensional residence lemma is accepted; its universal applicability is not.
