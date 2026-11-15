# Global closure audit and attempted incidence bypass

Base: 6a2807b6700ba1f771060ce6659af16097a998b2. Original ledger: 2/9; unchanged.
Status: exact dependency audit and conditional spectral-sequence deduction; no new global obligation closed.

## Correct original quantifiers and sufficient endpoint

For every realizable uniform rank-four parent on eight labels, every normalized parent component X, and every proper pairwise-incomparable three-signature family S, original D3 requires the triple-bad Hc0 vanishing and the alternating exclusive-pair Hc1 restriction-map injectivity. The inherited sufficient factor-wall route proves both together.

Let A(S) be the finite union of all circuit-aligned primitive residual factors for S and W its wall union in X. All triples among A(S) count, including triples aligned to a single signature. The inherited support-persistence comparison injects Hc2(B_S) into Hc2(W). Single walls have Hc1=Hc2=0; pairs have Hc0=Hc1=0. The stronger universal pair-wall result covers all 9,476 pair orbits. Therefore global triple-wall Hc0 vanishing T would alone complete this sufficient route and imply BOTH original obligations. A separate pair-injectivity proof is not an additional prerequisite after global T.

Primary local repository sources:
- ops/research-team/experiments/2026-09-10-d3-universal-pairs/REPORT.md, precise route to 3/9.
- ops/research-team/experiments/2026-09-10-d3-wall-pairs/pair/FINDINGS.md, section 1.
- ops/research-team/experiments/2026-09-10-d3-universal-pairs/WORK_ORDER.md, original quantifiers.

## A genuinely weaker factor-wall endpoint

Use the inherited finite closed-cover compact-support spectral sequence

 E1^(p,q) = sum_{I subset A(S), |I|=p+1} Hc^q(H_I;Q) => Hc^(p+q)(W;Q).

Only E1^(2,0) can contribute to total degree two: E1^(0,2)=E1^(1,1)=0. The incoming d1 from E1^(1,0) vanishes because all pair Hc0 groups vanish. The only potential later incoming differential is d2 from E2^(0,1), which vanishes because single-wall Hc1 vanishes. All outgoing d_r for r>=2 from (2,0) have negative second coordinate. Consequently

 Hc2(W;Q) is isomorphic to ker(delta),
 delta: sum_{|I|=3} Hc0(H_I;Q) -> sum_{|J|=4} Hc0(H_J;Q),

where delta is alternating restriction. A finite cover has finitely many columns; no convergence or infinite-support issue is introduced. Each locally closed semialgebraic intersection has finitely many connected components, so Hc0 is the finite-dimensional space spanned by its compact components. The restrictions are therefore exact compact-component incidence maps.

This supplies a weaker sufficient global target than T: prove delta injective for every X,S. Individual compact triple components could in principle exist and still be killed by restriction to four-wall intersections. This is not asserted equivalent to original D3, since the injection Hc2(B_S)->Hc2(W) need not be surjective. It is an exact endpoint for vanishing Hc2(W).

This argument is a formal consequence of the existing spectral sequence, not a claimed new major theorem. Related component-incidence reductions already occur for circuit covers in ai/omreal/ATLAS_HELLY.md; the new audit identifies precisely what the completed factor-pair theorem leaves here.

## Substantive attempted bypass and exact failure

Attempt: replace universal noncompactness by showing every compact triple component meets another active wall, and use that intersection as its detecting row.

Failure: nonzero columns do not imply independent columns. With four active factors, one compact component for every triple and one common compact quadruple component produces the row

 [-1, +1, -1, +1]

in the basis (123,124,134,234), according to the standard alternating omission convention. Every column is nonzero, yet rank is one and kernel dimension is three. Thus the proposed 'every compact triple meets a fourth wall' theorem alone would not close the global endpoint. This is an exact incidence-level canary, not a claimed realizable 9DVL counterexample. The canary computation is in verify_incidence_canary.py.

A successful bypass needs a proved triangular/matching structure with genuinely private detecting component rows, or a complete global rank proof for delta, with all active factors and parent components. The repository contains no authenticated component inventory from which this matrix can currently be formed. An orbit-source inventory is not a component inventory. No such matching or rank proof was obtained in this cycle.

## Exact obligation graph

All-source T -> all active triple Hc0 vanish -> delta injective -> Hc2(W)=0 -> Hc2(B_S)=0 -> both original D3 obligations -> ledger 3/9.

Alternative: prove delta injective directly for all X,S, bypassing T.

Current K0 cycle for source (5563,4373,23221) -> at most a branch exclusion in a sufficient no-maxima route -> still needs K!=0 and inherited chart/singularity coverage to close that whole source -> still does not establish all-source T or universal delta injectivity.

The inherited 1,162,302 records are unresolved source records, not components or automatically distinct required rows of delta. Closing the one K0 target cannot by itself justify 3/9. No numerical credit or ledger update is authorized by this audit.
