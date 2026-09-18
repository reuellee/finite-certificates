# 9DVL continuation: parent-localized polar analysis

18 September 2026. **Original ledger 2/9. Whole survivor OPEN. H_c^0(S) OPEN.
Zero new source orbits closed.**

## Result and executed plan

I restored the latest polar-target-correction archive, checked its SHA-256 and
all 86 payload hashes, reran its exact mathematical verifier, and refreshed
GitHub and the Drive recovery pointer. GitHub remained at dc4e8460df00554f8dd39d4b258e0d0b6dc6ec25.
The attached correction archive was newer than the Drive global-coverage pointer.

The plan was to diagnose the corrected enlarged stationary set before further
expensive elimination, retain all genuine parent conditions, and publish the
result with an honest ledger. This uncovered another conclusive obstruction:
the corrected partial-unit system itself has an exact rational solution with
nonzero reciprocal multiplier. Continuing to seek its unit ideal is impossible.

The explicit point is

    (A,B,C,D,u,v,w,t,j,y)=(3,0,-1,-3,3,1,0,-2,1,1/1296).

Here Q=R=0, all seven j Q_x-R_x equations vanish, L=18, U=72, and y L U=1.
It is not a genuine parent: 15 original brackets vanish. It is not a
counterexample to 9DVL. A second implementation using Python Fraction and
permutation determinants independently checks the point and its derivatives.

The point extends to a rational one-parameter family. The proof completely
classifies the corrected enlarged system on the particular slice
B=w=0, C=-1, D=t-1. That slice is exactly the displayed family with parameter
a!=0,1,-1. It does not classify the full stationary set.

## Revised proof search

The revised target uses the entire original parent-factor localization, not
another guessed subset of inverse conditions. A sufficient output is a rational
identity expressing a nonzero product of authenticated parent factors as a
combination of the nine reciprocal stationary equations. The output must include
an exactly checked identity, or a complete real-domain exclusion/escape proof.
Its existence is not assumed.

Two new exact logarithmic vector-field identities supply degree-five consequences:

    V=AD partial_D+(At+u) partial_t,       V(Q)=A Q;
    W=C partial_C+(w-u) partial_w,        W(R)=R.

The polynomials (2A R-V(R))/u and W(Q) vanish at every genuine stationary point;
the proof records their exact generator identities and justified divisions.
This is a reduction/augmentation, not a proof of stationary emptiness.

## Measured bounded computations

All figures below describe this environment and incomplete prefixes.

| Parent-localized formulation | Saved completed pairs | Pending pairs | Measured call | Peak RSS |
|---|---:|---:|---:|---:|
| Augmented, GF(101), resource stop | 140 | 320 | 28.024 s | 263,804 KiB |
| Augmented, QQ, deliberate prefix | 30 | 71 | 0.671 s | 140,308 KiB |
| Augmented, GF(101), deliberate prefix | 30 | 71 | 0.536 s | 138,652 KiB |
| Plain, GF(101), deliberate prefix | 50 | 127 | 1.863 s | 154,292 KiB |

The longest saved state has 123 active polynomials; the largest stored polynomial
has 4,726 terms. No parent-factor cancellation occurred in these research
prefixes. They establish neither a speedup nor an eventual memory/runtime bound.
Processed pairs are not a percentage of a known total.

The entire 30-pair rational state reduced modulo 101 matches the separately
computed modular state: 14,499 coefficients were checked and every denominator
was invertible. This is an arithmetic cross-check on unfinished work, not a
characteristic-zero emptiness proof.

## Implementation checks and fixes

New regression cases exposed two latent cancellation-helper problems: it skipped
single-monomial polynomials, and its first successful cancellation would call an
unsupported PolyElement.total_degree logging method. Both are fixed. Earlier
research prefixes had zero cancellations, so these paths were not exercised
there; no previous source proof is inferred invalid from these bugs.

The updated helper cancels B*w exactly and leaves an undeclared multiplier j
in j*B*w. It does not cancel B-D or C-D. Forty-eight exact native-vs-SymPy
ordered-division cases over QQ, GF(101), and GF(1009) passed. The underlying
Buchberger implementation is inherited from SymPy; it is not an independent CAS.
A zero pending queue in this heuristic quotient-augmented routine must not be
mislabelled as a complete saturation without an appropriate certificate.

## Discovery-only work and unsuccessful attempts

A deterministic finite-field grid over seven integer coordinates in [-3,3]
used 823,543 tuples, solving B from Q_B. It produced one candidate, which was
then verified rationally. The grid is not a completeness argument. The general
family and slice classification come from exact algebra and the written proof.

Additional wall-derivative identities were factored. A conic reparameterization
r=(At+u)/D was explored; a rational-simplification attempt reached its execution
limit. A subsequent direct coefficient construction succeeded but produced
646, 1,340, and 1,204 terms in its three coefficients. No global discriminant
sign theorem or solver advantage was obtained from that experiment.

Native msolve/package downloads failed because of network/DNS access, including
an unsuccessful binary-download attempt. No external solver result is claimed.
A streaming execution request was unsupported and ran no computation. An initial
grid-script syntax error was corrected before the successful run. The original
one-monomial regression first exposed the logging error above; its successful
replay was performed after the fix. All accepted outputs are separately marked.

## Acceptance, scope, and persistence

Core acceptance: exact source reconstruction; all 70 brackets; all 61 parent
factors; explicit witness; full rational-family identities; complete written
classification of its specified boundary slice; exact vector-field consequences;
three mathematical and two independent-witness negative controls. Arithmetic
acceptance adds 48 division tests, four factor-cancellation regression cases,
and the full rational/modular prefix cross-check.

A clean copied-directory replay passed. The final ZIP was separately extracted,
its payload hashes checked, and its two exact mathematical entrypoints replayed
before publication. These are not independent mathematical referee review.

This checkpoint includes the unchanged 8,344,673-byte predecessor correction
archive, which in turn preserves the preceding profiling and research snapshots.
It is a research snapshot, not a full Git-history bundle. Only the new
source-specific report, proof, and exact witness/reconstruction checkers are
published to the existing research branch; large exploratory states and prior
nested archives are retained in the Drive recovery package. Main, PRs, history,
sharing settings, and repository visibility are not changed.

The accompanying publication receipt identifies the final GitHub commit and the
verified Drive archive and manifest. Until that receipt is written, this report
alone does not assert successful external storage.

## Next discriminating gate

Do not resume either refuted partial-unit ideal as an emptiness target. Work on
the fully parent-localized stationary problem, using the exact degree-five
consequences when helpful. Seek an actual rational parent-unit-product identity
with multiplier verification, or characterize any surviving real stationary
points with all parent conditions restored. Benchmark representations only on
matched prefixes and retain rank-loss/normalization exceptions.

The original maximum reduction remains a sufficient route for this one triple.
Neither H_c^0(S)=0 nor original 3/9 follows from this cycle. The inherited source
record remainder remains 1,162,302; no numerical count is decremented.
