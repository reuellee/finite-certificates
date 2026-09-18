# 9DVL: zero-curvature branch resolved, then the remaining system reduced

18 September 2026. **Original ledger 2/9. Whole survivor OPEN. Zero source orbits closed.**

## Results

The requested maximum-locus task was advanced through three consecutive steps.

1. A complete exact argument now excludes every genuine B-stationary point with
   g=0 from the maximum and minimum loci of the authenticated source
   (5563,4373,23221). It covers the singular nu=0 case. This is a universal
   exclusion of one whole branch, not another isolated saddle example.
2. With that branch removed by proof, every possible maximum has h*g>0.
   A second justified curvature pivot reduces the previous five-by-five
   necessary PSD test to an explicit four-by-four Schur matrix P4. Its full
   condition requires all 15 principal minors. All remaining degeneracies stay.
3. The two separated quadratics permit exact rational elimination of C,D and
   the stationary multiplier. The remaining stationary equations can be written
   in six variables. I also retained the seven-variable version, whose lower
   degrees made it the more conservative choice for the bounded discovery pilot.

These steps do not complete the remaining maximum-locus problem. Neither whole
source noncompactness nor the original diagonal-three or injectivity obligations
has been proved.

## Why the branch exclusion works

In the parent-unit coordinates r=(At+u)/D and z=(w-u)/C, the wall equations are
Q=D*q(C), R=C*p(D)/A^2, with q and p quadratic in the indicated variables.
Stationarity forces q_C=p_D=0. On g=0 all three coefficients of q vanish.

I classified that coefficient-zero branch without dropping any zero denominator.
Its remaining parameters satisfy an explicit rational formula. At v!=1 a mixed
curvature is a nonzero product of authenticated parent factors and v-1. At v=1,
a different mixed curvature is exactly a nonzero parent-bracket square.
In both cases the zero diagonal and nonzero mixed entry force a negative
2-by-2 determinant, hence opposite curvature directions. The proof explains why
this excludes extrema even at a singular wall intersection.

The v=1 case and the would-be zero denominator A+u-v+1=0 are handled explicitly.
B=D, C=D, nu=0 and all original parent sign residences remain in scope.

## Actual bounded computations

The predecessor ZIP matched its recorded 9,570,231 bytes and SHA-256
c54101eb5cf92c2f4ee13b5cf11d4fc74130f1c58b2c67c6e3ccadb7d1addc7c.
ZIP integrity, all 43 payload hashes, and both predecessor mathematical replays
passed. GitHub and the Drive LATEST pointer were refreshed; both agreed with
starting commit 37e6d0f05ea9c3ab0633fc101188aa3f8f56972f.

The exact zero-curvature checker completed successfully. The reduction checker
verified the quadratic, differentiated, source-curvature and Schur identities
and built the full source-specific matrix circuit. Ten separate Fraction
arithmetic checks also passed. Final clean-replay timings are in the recovery
manifest, not extrapolated into a theorem-completion estimate.

The polynomial profiles are:

| Formulation | Variables | Maximum degree | Notable sizes |
|---|---:|---:|---|
| Original reciprocal stationary system | 9 | 5 | Predecessor source equations |
| Discriminant stationary system | 7 | 8 | Dq: 248 terms; Dp: 78 terms |
| Multiplier-free stationary system | 6 | 12 | Four cross equations: 2,376 / 2,639 / 2,423 / 2,293 terms |

A 384-start numerical screen of the original system produced two near-boundary
candidates at the recorded numerical thresholds, but no new certified witness.
A 160-start reduced-system pilot generated 132 near-roots: 73 failed numerical
pivot guards and 49 failed reconstruction or parent-margin checks. The remaining
hits coalesced to the known saddle. No new exact maximum or new exact stationary
point was certified. These screens are not exhaustive, and their starts and
formulations differ, so they are not a matched performance benchmark.

## Implementation issues and their resolution

Initial expression-based reduction replays hit the execution limit, mainly while
re-parsing and simplifying expanded multivariate expressions. The final checker
uses sparse polynomial coefficient arithmetic and general quadratic/congruence
identities instead of expanding redundant expressions. The final exact replays
completed. These execution limits were not mathematical solver conclusions.

The first numerical report serialization rejected a NumPy boolean; it was fixed
and the seeded screen was rerun. One streaming request was unsupported and ran
no computation. A local output permission issue was corrected before the reduced
input was written. No output from these failed attempts is accepted as evidence.
No paid compute, external-machine administration or new solver download was used.

## Remaining mathematical target

The active target is now the reconstructed original-parent real locus satisfying
CRIT7 or CRIT6, h*g>0, nu*h>=0 and P4 positive semidefinite. The six-variable
reconstruction must retain every required nonzero pivot and all 70 original
bracket inequalities. Nu=0 and all remaining semidefinite cases remain open.

An exhaustive global exclusion of this target would discharge the maximum route
for this chart; a conventional complete escape proof is still permitted. Even
an eventual source theorem would not by itself settle every remaining source or
the original exclusive-pair injectivity obligation. The source remainder stays
1,162,302 records, not a component denominator.

## Persistence and limitations

The recovery snapshot retains the unchanged predecessor archive and all new
proofs, exact scripts, sparse coefficients, matrix circuit, discovery results,
logs and explicit claim ledger. It is not a full Git-history bundle.
New public files are additive on the existing research branch; main and PRs are
not changed. Drive storage is restricted to Projects/research-backups, and the
old LATEST pointer is preserved before any replacement. The separate receipt
records which publication and readback operations actually succeeded.

Arithmetic checks and this assistant's mathematical audit are not independent
mathematical peer review. No global maximum census, stationary dimension theorem,
whole-source closure, or original 3/9 claim is made.

Numerical discovery uses scipy.optimize.root, whose official documentation is
https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.root.html .
It supplies candidates only. Acceptance of the new identities uses exact
integer/rational arithmetic and the written proofs, not numerical root finding.
