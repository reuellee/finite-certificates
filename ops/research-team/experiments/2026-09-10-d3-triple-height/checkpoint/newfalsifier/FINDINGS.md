# Independent challenge of the completed pair-wall arguments

**The broad concurrence-height pair-wall theorem survives this independent challenge. No original diagonal-three proof is claimed.**

## Deductive challenge

The reviewed proof is `original/CONCURRENCY_HEIGHT_PAIR_VANISHING.md`; its exact snapshot hash is bound in `HANDOFF.json`. I checked the following possible failure points.

1. Every selected three normals of a type50/type51 quartet are independent on a uniform parent. Nine triple incidences on eight labels force an intersecting pair; degree at most two means the third triple omits the shared label. The first two normals annihilate its parent vector, whereas the third evaluates to a nonzero parent bracket. Thus a wall quartet has rank exactly three, with no discarded rank-two stratum.
2. Its concurrence point cannot equal a parent point. Some support triple omits every given parent label, which would otherwise yield a zero parent basis bracket. Hence the contraction has no loop and the four-parent-height count applies.
3. The four projected P lines form a dual projective frame. The four degree-two parents have fixed projected positions; four degree-one positions give an open four-coordinate base. A free parent cannot land on another P line because that would put four original parent columns in one support plane. Coincidence between the two free parents on the same type50 line remains allowed; it introduces no parent-height equality.
4. The chosen high-degree labels1,2,4 are projectively independent for both displayed types. The fourth high-degree parent supplies a nonzero parent bracket for the height-scale gauge, leaving precisely four affine parent heights. All parent inequalities stay strict and affine, so each actual fiber is an entire open convex four-cell.
5. Positive column gauges and finite normalization sign sectors are necessary and are retained. A concrete global initial height covector can be obtained from the ordered exterior product p of three actual P normals: choose `ell=p^T/(p^T p)`, then apply the three height shears and positive scale. This makes the vertical orientation explicit if desired; changing a local lift choice does not introduce another parent coordinate or truncate a fiber.
6. When q differs from p, its projected direction lies in RP2 and its height is a line-bundle coordinate. Changing its representative rescales that height linearly. The four plane-incidence equations are affine in the four parent heights and the one q height on every such chart, including projected rank changes. Their coefficient rank is invariant under the chart transitions.
7. A solution to all four Q equations has the unique actual Q concurrence point because the Q normals have rank three. There is no extra projective witness fiber. The full solution fiber is an affine solution space intersected with the strict parent height cell, and is convex. Restriction to one original parent component retains the whole connected fiber.
8. On the rank-four locus the image is open in the six-dimensional base and the full fiber is one interval. An open subset of R4 times RP2 has no compact component: projection of any open component to R4 is open, whereas the image of a compact component would be compact. The orientation local system causes no compactly supported degree-zero sections on a noncompact connected component.
9. Coefficient rank at most three is closed in the distinct-point locus and gives full convex fibers of dimension at least two. The equal-point locus q=p is closed in the original pair intersection and has full four-dimensional parent-height fibers. Shriek base change and the two closed/open localization steps therefore retain both exceptional strata.

No actual counterexample or missing load-bearing hypothesis was found. This is independent deductive acceptance using the inherited fixed-unit residual-wall correspondence and standard compact-support sheaf results, rather than an inference from finite sampling.

## Exact formerly-hard source254 canary

`contraction_height_test.py` independently reconstructs the populated inherited type50+type50 source254 parent, both four-row normal systems, their distinct rank-three concurrence points, the fixed four-line projected frame, the three height shears, and the positive height-scale gauge.

The Q incidences give an exact rank-four affine system in the four free parent heights and q height. Its solution direction is

`(-447/5083, 11771/20332, -149/204, 62431/40664, 1)`.

The entire parent residence fiber is the interval

`-162656/818755 < t < 162656/2831745`.

All 70 parent bracket inequalities are reconstructed and checked on this full interval. The nonzero direction in four normalized parent heights rules out a gauge-only motion. Data are in `CONTRACTION_HEIGHT_TEST.json`. This is an exact consistency check for a formerly hard case, not a substitute for the global proof.

## Earlier retained-plane formulation

The more limited two-column affine proof also survives review. Retaining Pi, He and Hj avoids the sign-chart ambiguity in an arbitrary projective perspectivity parametrization. Parent uniformity forces their rank to be three; rank two would put both moving parents in the same one-moving-label plane, violating a four-parent bracket. Opposite-plane evaluations are ratios of nonzero prescribed parent brackets and give positive, unique column gauges. All parent brackets and the normalized Q equation are jointly affine in the two moving coordinates.

`affine_perspective_test.py` rebuilds an actual source61 fiber. Its normalized Q equation is

`-231u/629 - 11v/29 = 0`,

and its full parent residence interval is

`-1369/495 < u < 12839/6699`,

with parent endwalls2348 and1368. All70 parent brackets are jointly affine. The initial five marked-concurrence tests in `perspective_test.py` are exploratory only and are not used as proof premises.

The broader concurrence-height theorem supersedes the need to handle these27 cases separately. It also avoids the earlier conic-fiber component-change obstruction by using a different global quotient with connected full convex fibers. Neither result settles the independent triple obstruction or authorizes a3/9 claim.

## Final pair endpoint and independent triple replay

The independently accepted broad theorem completes the stronger pair-wall endpoint: **9,476/9,476 distinct factor-pair orbits**, with Hc0 and Hc1 vanishing. The original theorem ledger remains **2/9**. No independent triple obstruction is discharged by that pair result.

`verify_triple_rank_independent.py` now independently reconstructs the alternative track's rank-six fixture using Python `Fraction`, permutation determinants, and its own row reduction. It reads only the original parent and stated support/point inputs; it does not import producer equations or rank routines. The eight-by-ten incidence matrix has rank six, and its four-dimensional kernel is exhausted by the three shears and the actual scaling vector. After fixing four parent heights, the eight-by-six matrix still has rank six; an independently selected normalized minor is `-147470400`. The altered-height hostile control is rejected.

The same verifier uses independent sparse rational polynomial arithmetic to rebuild the two raw residual determinant identities, the parent-unit identities `[2357]=-(4h5+h7)` and `[2346]=-h6`, and all70 affine parent brackets. The fixture's three concurrence vectors have rank three. Results are in `TRIPLE_RANK6_INDEPENDENT_REPLAY.json`.

I also accept the scoped triangular escape proof in `alternative/TRIPLE_RANK6_MODEL.md`: first eliminate h6 where its coefficient is nonzero; a zero coefficient at a compact-component point would supply a full noncompact fixed-base interval. Then apply the same argument to h5 in the remaining open regular locus. The final graph projects to an open subset of the (h7,h8) plane and cannot be compact. No convexity of the post-elimination domain is assumed. The fixed projected-parent fiber is closed in the full concurrence model, so this excludes a compact component meeting this specific fiber.

This was an already settled predecessor fixture with a type49 anchor. Its new role is to show that fixing both projected concurrence directions really can leave no physical height motion, while allowing those directions to vary restores escape in this one case. It supplies no new triple-source count, universal triangular theorem, or original diagonal.
