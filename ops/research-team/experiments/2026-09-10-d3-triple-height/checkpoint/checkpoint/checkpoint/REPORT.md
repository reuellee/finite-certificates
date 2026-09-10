# 9DVL: a finite route toward diagonal three

**The theorem ledger remains 2/9. This cycle proves a stronger pair-wall vanishing statement for 8,902 of the 9,476 factor-pair orbits and isolates the remaining 574. It does not prove diagonal three.**

The user requested a plan and execution toward 3/9. The useful change in this cycle is a theorem with universal parent quantifiers and a finite, independently reproduced remainder. The counts below concern residual-factor pair orbits. They are neither counts of parent components nor percentages of the original injectivity proof.

## The sufficient route

For a normalized parent component X, let H_f be a complete primitive residual wall, including every intersection and rank stratum inside X. The following two statements together suffice for diagonal three:

1. Pair endpoint P: H_c^1(H_f intersection H_g; Q)=0 for every distinct pair of factors.
2. Triple endpoint T: H_c^0(H_f intersection H_g intersection H_h; Q)=0 for every distinct triple of factors.

Here is the comparison with the original problem. For any finite genuine extension-signature family, let B be its union of bad loci and let W be the union of every whole residual wall aligned with at least one of those signatures. The inherited fixed-unit circuit and persistence theorems imply W is contained in B and the boundary of B lies in W. Thus B minus W is clopen in X minus W.

Known single-wall H_c^1 vanishing and pair-wall H_c^0 vanishing give H_c^1(W)=0. Together with H_c^2(X)=0, this gives H_c^2(X minus W)=0, hence H_c^2(B minus W)=0. Therefore H_c^2(B) injects into H_c^2(W). The finite closed-wall-cover spectral sequence makes the latter zero if P and T hold, since its total-degree-two terms are precisely single-wall H_c^2, pair-wall H_c^1, and triple-wall H_c^0. This proves the required third-diagonal conclusion with all original signature quantifiers.

This conditional argument was independently audited. It does not assume a continuous choice of a Gordan witness. It also does not assert that P alone proves the original pair restriction map is injective. T must cover every distinct factor triple among the active walls, including factors aligned to the same signature.

## What is proved about P

For all coefficient rings R, the new geometric arguments prove H_c^0=H_c^1=0 for all factor pairs containing kind 36, 38, 48, or 49, together with additional relative labelings of the remaining three kind pairs.

The first argument retains the relevant support planes and forgets one or two parent columns. When the combined support has a column of degree at most one, or two columns of degree two, every nonempty residence fiber has compact-support cohomology zero below dimension two. The two-column fiber need not be convex; its interval sections make each component a contractible open surface. Compact-support direct image gives the global vanishing, including simultaneous wall intersections. An exact exhaustive selection among 266 possible degree patterns handles kind 38. The referee additionally proved that all 15 occurrence choices describe the full same wall, avoiding an inference from generic occurrence data.

The second argument handles the remaining pairs containing kind 49. Forget its omitted parent column. The other wall cuts the three-dimensional parent residence into a plane or a ruled quadric. A genuine forbidden parent bracket removes one direction from the ruling's projective parameter line. Regular fibers are intervals over intervals; a possible exceptional ruling is retained as a closed open two-cell. The compact-support open/closed sequence includes that specialization and proves the same vanishing. Both the referee and the falsifier independently reviewed this geometry.

The exact accounting is:

| Factor-kind scope | Pair orbits | Proved by these arguments | Still open in P |
|---|---:|---:|---:|
| At least one factor of kind 36, 38, 48, or 49 | 6,414 | 6,414 | 0 |
| 50 / 50 | 1,411 | 1,154 | 257 |
| 50 / 51 | 1,272 | 1,023 | 249 |
| 51 / 51 | 379 | 311 | 68 |
| **Total** | **9,476** | **8,902** | **574** |

The coordinator enumerated the remaining unique-support factor orbits using stabilizers and pair reversal. The referee independently used adjacent-transposition generation and disjoint-set orbit equivalences, reproducing all counts and matching every one of the 574 listed failures. The total 9,476 is inherited from the pinned exact global census. The 6,414 complement therefore requires no new action model for the other factor kinds.

Every remaining support union has degree pattern (3,3,3,3,3,3,3,3) or (2,3,3,3,3,3,3,4). These are failures of the present sufficient support-motion criterion, not certificates of nonvanishing. Their full support representatives are in coordinator/HARD_PAIR_RESIDUE.json.

An exact point shows that at least one difficult 50/50 pair really occurs on the uniform parent locus. In the standard coordinates (a,b,c,d,e,f,g,h,i), take

    (7, -8, -4, -17/4, 2, -3, 2, -2116/67, -8).

The wall supports are 123/145/246/378 and 567/158/268/347. All 70 parent brackets are nonzero, both four-normal matrices have rank three, and their support union is three-regular. Independent rational arithmetic verifies this. A point and an escape curve do not determine H_c^1 of its full seven-dimensional pair wall.

The first follow-on test is also concrete. Fixing the first seven columns at that point, the entire allowed column-eight fiber is the open interval -12<i<-36/5, with its two ends on actual parent bracket walls. Its H_c^1 is Z. Thus the successful argument based on vanishing fiber cohomology cannot simply be reused for this projection. A nearby exact uniform base yields a nonsingular conic, so the interval's linear formula does not extend uniformly either. These are obstructions to particular proof constructions, not counterexamples to global pair-wall vanishing.

A conditional refinement survives: a full affine-line residence over an open deletion base has only an orientation local system in compact-support direct-image degree one, whose compactly supported global sections vanish. Closed coefficient-rank drops to plane or three-cell fibers can be retained. The nearby conic shows that the required uniform two-affine-equation presentation is absent in this particular column-eight projection. Controlling the conic family or changing the quotient remains necessary.

## Triple endpoint: structure, but no closed orbit

The triple track investigated the canonical hard case (5563,4373,23221), using the actual pinned factor equations. It found an exact uniform fold, so one proposed projection is not an unbranched double cover. The example has a noncritical height b; it is not a compact component or a counterexample to 9DVL.

The track also found that one equation is a nonsingular projective conic in two parent coordinates throughout the uniform locus: its conic determinant is a product of named nonzero parent brackets. Independent verification reconstructed the conic determinant, all 70 brackets at the fold, and the complete 1,951-term quadratic and 4,186-term discriminant identities. This excludes the entire all-coefficient degree-drop branch in a two-graph quadratic presentation. A hypothetical compact component would consequently yield a localized solution of

    R = R_e = R_f = R_g = R_h = R_i = 0

in the six variables (b,e,f,g,h,i), with the stated leading coefficient and all reconstructed parent brackets nonzero. The reduction retains singular extrema. It remains a necessary-condition reduction; that polynomial system has not been proved empty.

Fewer variables do not demonstrate a faster computation: R has degree 18 and 4,186 terms, and the six generators contain 22,160 terms. Exploratory exact tests found no affine coordinate in one rational conic parametrization and ruled out diagonal scaling in 64 specified shifted coordinate systems. Those secondary discovery tests were not part of the independent acceptance replay and carry no original theorem credit.

The universal triple endpoint remains open, with 1,162,302 inherited unresolved source records. This cycle closes zero of those records. A separate tangent-cone calculation also exhibits local kernels; it is explicitly scoped to a transverse model and is not an original injectivity counterexample.

## The remaining plan

1. Complete P on the explicit 574-orbit list. Test a quotient moving at least two parent columns, or retain and control the nonzero degree-one compact-support direct image of a conic family. The realized three-regular 50/50 point, its exact interval fiber, and the nearby nonsingular conic are required early tests. Another one-dimensional escape does not meet this proof obligation.
2. Complete T through a universal triple escape theorem or certified coverage of its remaining factor triples. For the named hard case, an exact real-emptiness or saturated unit-ideal certificate for the specified critical system would close that one orbit. Its singular strata and genuine parent ends must remain in the proof. The denser discriminant presentation should be compared with the older seven-variable system before committing to expensive elimination.
3. Once both universal endpoints are proved, apply the already audited wall-union comparison and update the original theorem ledger to 3/9. Partial factor counts cannot trigger that promotion.

## Evidence and limits

The mathematical inputs are pinned to commit 59fec66666518257c585194b81061f60d91f439d in reuellee/finite-certificates. All 21 consulted source files match their Git blobs exactly. The previous witness-selection checkpoint is b2667461a6359f804090212f0f075cc1ec018048. The snapshot includes frozen proofs, independent reviews, exact certificates, replay code, and the explicit pair residue. It is a research snapshot, not a full repository-history backup.

The original pair restriction map remains OPEN; its original component coverage and residual count remain UNKNOWN. The original triple-bad H_c^0 statement remains OPEN. Original global operational obligations closed in this cycle: zero. These findings are exact arithmetic and independently reviewed mathematical arguments, not proof-assistant certification or a claim of literature priority.
