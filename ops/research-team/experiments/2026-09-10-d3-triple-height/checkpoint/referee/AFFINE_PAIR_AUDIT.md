# Independent audit of affine pair vanishing

**Accept** `original/AFFINE_PAIR_VANISHING.md`, SHA256 `69c9e5e8a563a8d5fca952854aaf0d3e44aec82c2bb44caea8e863b62899c0e9`, as a conventional deductive proof with its stated all-parent and all-component quantifiers.

For two derived-normal occurrence quartets with one common parent label appearing exactly once in each, their determinants are affine-linear in that parent point after forgetting it. A five-label projective frame among the seven fixed labels provides a global normalized deletion chart. Normalize the moving point by a fixed nonzero parent bracket to obtain one affine three-space; parent signs are strict affine inequalities there. The residence fiber is therefore the full open convex polyhedron, and restriction to a parent component keeps that entire fiber. The original occurrence determinants, rather than potentially non-affine primitive quotients, give the two equations. Nonzero parent-bracket units preserve their zero sets.

The coefficient-rank-at-most-one part is closed. Its consistent fibers are open convex affine spaces of dimensions at least two. Proper-support base change makes its R^0 f_! and R^1 f_! zero, including rank-zero and inconsistent specializations. No topological triviality across that closed stratum is assumed.

Over rank two, the affine solution lines form an affine-line bundle. Its kernel orientation is given by the cross product of the two ordered coefficient rows in the fixed oriented three-space. The selected nonempty-fiber base is open in the six-dimensional deletion chart: a local nonzero minor and strict feasible point give a persistent solution, and parent components are open. The actual fibers are single open intervals. Integration along them identifies Rf_!Q with the orientation sheaf in degree one; here the supplied cross-product orientation trivializes it. The base has no compact connected component, so H_c^0 of that local system vanishes. Thus the rank-two part has H_c^0=H_c^1=0. Closed/open localization proves the full claim. The direct-image argument handles all finite parent-wall ends and unbounded ends; it does not require a proper projection.

This is stronger than merely knowing that a conic fiber has contractible components. Multiple components and their specialization can give a non-locally-constant top direct image. The affine proof has an actual connected-fiber line-bundle comparison, so that objection does not apply.

The independent standard-library checker `verify_affine_pair_coverage.py` reads the inherited source of 574 rows, SHA256 `82434c6e07fe3290030b057f0eba2f50b522cfc25aabe66b8abf9a8495e55fc4`. It reconstructs both quartets' incidence counts, confirms that their support sets are disjoint, verifies an actual once-in-each-quartet pivot for every covered row, and checks a complete nonduplicated partition. It does not trust stored degrees or producer acceptance code. The count is:

| Kinds | Newly covered | Remaining |
| --- | ---: | ---: |
| 50,50 | 238 | 19 |
| 50,51 | 233 | 16 |
| 51,51 | 58 | 10 |
| Total | 529 | 45 |

All remaining records have degree three at every label. Six hostile mutations are rejected. The theorem is invariant under label permutation, so applicability to these inherited orbit representatives gives their complete geometric orbit scope, without a new parent sample requirement.

At this intermediate stage, combining with the inherited endpoint gave 9,431/9,476. The subsequent two-column theorem raised it to 9,458, and the universal concurrence-height theorem completed endpoint P at 9,476/9,476; see `CONCURRENCY_HEIGHT_AUDIT.md`. The general affine idea is not claimed as new in the literature; its complete rank-aware 529-row application remains an accepted intermediate result. Original D3 injectivity and triple H_c^0 remain open. No original diagonal obligation or triple-residue credit is assigned here.
