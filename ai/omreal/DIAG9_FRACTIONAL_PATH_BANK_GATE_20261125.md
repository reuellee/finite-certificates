# D9 fractional path packing: row-2599 endpoint-bank gate (2026-11-25)

**Status: exact bounded obstruction, not D9 proof. Ledger 2/9.** This checkpoint does not modify canonical strategy authority.

## Certificate
For a fixed endpoint pair u,v let E be all common endpoint signatures. For each verified parent path P let L(P) be the signatures in E that are not feasible somewhere on P. A nonnegative rational path packing w with sum_{P: sigma in L(P)} w_P <= 1 for every sigma in E and sum_P w_P > 9 rules out every nine-label separator of these endpoints. Proof: sum the nine inequalities for any purported separator; every path is counted at least once. The LP on a finite bank has a dual fractional label cover. One common label lost on every path is a dual bound of 1. No completeness of the path bank is required for a positive certificate, but failure on a bank proves nothing about paths outside it.

## Executed actual-geometry gate
Source: data/seeat_parent2599_upper178.npz, SHA256 3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a. The first known family is from data/ninth_candidate_12_37_antichain.npz (SHA256 11ca66549982ec40ce8425d2caed45b418edb73c4eb415a45b39d57e481bd1e4); the second signature array was extracted from the GitHub NPZ blob 37675c5b9248d26dd47ca2fb60c70e65f0e0c406, without full-file SHA replay. The repository data and prior path theorem are the sources; new tests used actual integer matrices.

Normalize the first four columns to the basis and fifth to its coordinate sign vector using positive rescaling. Scale corresponding moving columns to equal absolute first coordinate. For each determinant, expand the affine simultaneous interpolation in the Bernstein basis: the coefficient numerator of degree k is the sum of mixed endpoint determinants with k switched moving columns. All 70 signed bracket coefficient numerators strictly positive is sufficient for a parent-safe segment. Failing this sufficient test is not proof a segment is unsafe.

| Endpoint pair | Parent-safe three-segment routes via two stored charts | Distinct certified edges | All-family feasible stored charts | Common endpoint labels lost on every route |
|---|---:|---:|---|---|
| 12/37 | 142 | 176 | 12,37 only | 32577326938880 |
| 37/176 | 142 | 176 | 37,176 only | 102950366083904, 1228857713611584, 70793448873074816 |

Neither direct simultaneous segment passed the Bernstein sufficient test. No two-segment route through one stored chart passed. All six direct whole-column replacement orders fail an actual parent-sign check for each pair; no two such replacement routes via a single stored chart exist.

Exact primal/Gordan status of all 178 charts for each known family:
* 12/37: 778 strict witnesses, 824 positive dependence witnesses.
* 37/176: 385 strict witnesses, 1217 positive dependence witnesses.
* 3204 chart/signature tests total; zero unknown. Positive dependences have support <=5. The 284 parent-safe routes are independently replayed using a permutation-determinant implementation; all certificates check by integer dot products and exact zero sums. Floating LP is discovery only.

Thus the complete tested three-segment bank admits a dual packing bound <=1 for both pairs, even without enumerating every common endpoint signature. Moreover any route passing through a third stored chart fails at least one member of the corresponding known nine-family. This does not exclude direct or continuous routes with new intermediate realizations: the repository already has certified continuous paths for both known families. It does not prove a global separator, refute D9, or compute the full all-common-label LP optimum.

## Next gate
Harvest intermediate realizations from the two committed coordinate-path artifacts; build a new source bank with exact segment labels, then use fractional cover dual prices to find paths avoiding high-weight labels. A single new path avoiding the bank-hitting label disproves that particular bank bound, not the global D9 claim. Do not promote the ledger without all-parent/all-family coverage. The new strongly polynomial algorithm itself was not executed; SciPy HiGHS proposed witnesses, independently replayed exactly. Full certificate JSON and verifier are mirrored in the dated Drive backup. No independent human/agent referee has reviewed the cycle.
