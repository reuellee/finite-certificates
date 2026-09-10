# Actual admissibility and the common-zero stratum

## 1. Exact actual antichain

The three extension signatures are

- 1115179617623167;
- 1110781571112063;
- 1115179340274814.

Their signs differ only on the five triples

`012,345,036,246,147`

from the signed parent data in the authenticated previous checkpoint. On those five triples their relative signs are respectively

`-----`, `----+`, `++++-`.

`actual_antichain.py` proves that three explicit rational arcs `Y+tJ_i`, `0<t<=10^-8`, remain in one uniform parent component. On arc i, e4 satisfies all 56 strict inequalities for signature i, while each other signature has a strictly positive six-normal Gordan dependence. The matrices and polynomial weights are in `ACTUAL_ANTICHAIN.json`. Parent sign preservation includes every one of the 70 brackets on the full closed interval `0<=t<=10^-8`. Every positivity assertion uses the leading nonzero coefficient minus an exact absolute tail bound.

Thus these are actual realizable proper signatures, and their full feasibility regions form an internal three-element antichain in the original theorem's scope. This eliminates the prior tangent example's admissibility gap. It does not make that example an original cohomology counterexample.

## 2. A fiber-saturated common-zero stratum

Fix the original parent oriented matroid and take the locus where there is a projective point p such that exactly those five signed normals vanish on p and the other 51 base-signed normals are positive on p. Let S be its connected component containing the explicit center. There is one such positive projective point at most. Indeed n012 and n036 are independent, both vanish on parent0, and n345(parent0) is a nonzero parent bracket. Therefore these three normals have rank three for every uniform parent. All five normals have rank exactly three on S, and their common kernel is one-dimensional.

Consequently p is uniquely determined and depends continuously on Y. It is never a parent column: at a parent column at least the 21 triples containing its label would vanish. The incidence space `(Y,p)` is therefore homeomorphic to S; there is no nontrivial witness fiber in this step.

Contract by p. The projected rank-three configuration A has eight nonzero columns, with exactly the stated five collinear triples. For fixed A, all constraints involving p are already decided. The remaining constraints are the 70 strict parent determinant inequalities, affine-linear in the eight lift heights. Quotienting the three row translations leaves a five-dimensional height vector space. One nonzero parent bracket has a fixed strict sign and fixes the positive vertical scale, leaving a nonempty open convex subset of an affine four-space. It is homeomorphic to R4.

This description covers all the parent height residence cell. The cell is connected, so every cell meeting S lies entirely in S. There is no additional rank-three restriction: rank three was forced above by actual parent uniformity. Nor are new positive-witness equations imposed on this cell. Each zero-triple normal has the form `(lambda_I(h) ell_I(A),0)`, where ell_I depends only on A. Pairing it with a fourth parent column shows lambda_I is nonzero and has fixed sign throughout the height cell. Thus zero-supported positive dependencies, including those for these three signings, persist under positive row rescalings.

For the projection pi from S to the nonempty projected-configuration locus, the compact-support stalk identity gives

`(R^q pi_! Q)_A = Hc^q(pi^-1(A);Q) = 0` for `q<4`.

The compact-support Leray spectral sequence, in nonnegative degrees, then gives

`Hc^q(S;Q)=0` for `q<4`.

The same conclusion holds with a coefficient sheaf whose restriction to every height cell is locally constant: the height cell is contractible, so its restricted local system is constant. No properness of pi is asserted or needed; this is the shriek direct image. The loop case p=parent would have a different height count and is explicitly excluded.

This lemma concerns this entire fixed common-zero/sign stratum, not arbitrary subsets defined by additional bad-witness conditions. Constant-coefficient vanishing of S alone does not establish a global contribution statement for a constructible sheaf that is not locally constant along its height cells.

## 3. Exact four-halfplane reduction near this stratum

Use the base signed cofactor normals and extension coordinates

`x=n012(p), y=n036(p), z=n345(p), w=n034(p)`.

The row w vanishes on parent columns 0,3,4. At S it is positive on the common weak projective point, so x,y,z,w form a basis. Work in w=1. Put

`kappa = -n012(Y4)/n036(Y4)` and `U=x+kappa*y`.

In the parent component of the explicit center, kappa is positive, since both numerator and denominator are nonzero fixed-sign parent brackets. The two remaining rows have the exact form

`n246 = a U + c z + d w`,

`n147 = b U + e z + f w`.

To prove the identities, evaluate each row at parent 0,3,4. The coefficient ratios are

`a=n246(Y3)/n012(Y3)`, `c=n246(Y0)/n345(Y0)`,

`b=n147(Y3)/n012(Y3)`, `e=n147(Y0)/n345(Y0)`.

Each is a nonzero parent-bracket ratio. Evaluation at parent4 gives the y coefficient kappa times the x coefficient. The remaining coefficient multiplies w. The common-zero stratum is d=f=0. On this stratum `ae-bc` is nonzero: if it vanished, n246 and n147 would be proportional, putting at least four distinct parent columns into the same plane, contrary to uniformity.

At the explicit center,

`kappa=1/20`, `a=-8`, `c=-32/25`, `b=-19/2`, `e=-19/25`.

All selected relative sign patterns give x and y the same sign. For either sign epsilon, existence of x,y with those signs and x+kappa*y=U is exactly epsilon*U>0. Therefore the five active inequalities reduce exactly to four affine halfplanes in the two coordinates (U,z), with offsets (d,f). This is an exact pointwise elimination, not a linearization.

The four spatial directions are `(1,0),(0,1),(a,c),(b,e)`. Their pair determinants are nonzero on S. Their oriented cyclic order is fixed on each connected piece of S. The first derivative of the offset map (d,f) at the explicit center is the exact K^T h map from the previous tangent calculation; it is surjective.

## 4. Localization of the 51 inactive inequalities

At a point of S each selected signing has a strictly positive dependence on all five zero normals. This follows at the explicit center from the displayed K matrix. The four-direction oriented cyclic order in Section 3 cannot change on S, so the full-support positive-kernel sign patterns remain constant; along a height residence cell this also follows directly by positive normal rescaling. A weak feasible extension vector for any selected signing must annihilate each of those five normals: pair all weak inequalities with the positive dependence. Rank three then forces the unique projective ray p, whose other 51 inequalities are strictly positive.

Accordingly any sequence of feasible extension rays for parent points converging to that S point converges projectively to p. Otherwise a convergent normalized subsequence would produce a different weak feasible ray. The 51 inactive inequalities cannot create a second nearby feasible branch far from p.

Conversely, sufficiently small solutions of the four-halfplane system give solutions to all 56 inequalities. Establishing a uniform small-solution bound over a stratum neighborhood requires control of the nonzero minors of the four spatial directions. Locally those minors stay bounded away from zero. The vertices/rays of the two-variable feasible polyhedra then give a solution of norm at most a constant times the offset norm, with an arbitrarily small interior perturbation when needed. Thus the inactive inequalities remain positive after shrinking the parent neighborhood.

## 5. What is and is not concluded

The exact antichain and exact halfplane elimination are established. The four-dimensional height-fiber argument applies to the entire fixed common-zero/sign stratum and to coefficient systems known to be locally constant on its height cells.

A plausible next theorem is that the full local compact-support restriction diagram on a tubular neighborhood of S is the four-halfplane normal fan diagram with locally constant coefficients along those height fibers. Locally near the explicit center, the offset map is a submersion and the four spatial directions remain distinct, so standard parameterized straightening of the resulting finite planar curve arrangement gives the expected normal germ. Extending this uniformly over the full noncompact stratum requires checking regularity of the projected five-incidence locus and gluing the local normal comparisons.

**We do not promote that global tubular statement from the tangent calculation or from fiber contractibility alone.** It needs an explicit review of the parameterized normal comparison. Even if it holds, it would address only this common-zero stratum. It would not control attachment to other active supports, mixed weak-primal points, or the entire original bad union. In a valid product comparison its degree-one normal kernel could first contribute in total degree five, because the tangential height factor contributes compact-support degree four. That degree shift explains why this actual admissible local pattern need not obstruct original diagonal three.

## 6. Actual triple-bad points with no weak primal ray

The fourth certified arc reverses the first arc's direction, so its infinitesimal transverse coordinate is `(10,20)`. For every `0<t<=10^-8`, all three actual signatures have strictly positive six-normal Gordan witnesses, and each witness's six normals span R4. The certificate records a nonvanishing rank-four minor, with an exact polynomial sign bound, for each witness.

If a vector weakly satisfied any one signing's 56 inequalities, positivity of its six weights would force all six row evaluations to be zero. Rank four then forces the vector to be zero. Hence this entire fourth arc lies in the original triple-bad locus T, but has no nonzero weak primal vector for even one of the three signings.

This directly disproves the proposed universal statement that every point of T can be covered by an incidence resolution using a common weak feasible projective point. The counterexample uses an actual proper incomparable signature triple in one uniform parent component. It does not disprove use of a common weak point on an appropriately defined boundary stratum, nor does it disprove compactness or injectivity.
