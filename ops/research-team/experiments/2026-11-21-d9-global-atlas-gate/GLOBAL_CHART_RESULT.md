# D9 global single-chart normalization: exact coverage simplification

**Status: partial theorem only.** Original 9DVL ledger remains 2/9.

Let P be a 4-by-8 real matrix with every four-column minor nonzero. Set B=[p1,p2,p3,p4] and v=B^{-1}p5. All v_i are nonzero by uniformity. The left action H=diag(v)^{-1}B^{-1} sends p5 to (1,1,1,1) and the first four columns to e_i/v_i. Rescale the first four columns by v_i. For j=6,7,8 set w_j=B^{-1}p_j. Their first normalized coordinates w_{j,1}/v_1 are nonzero, so rescale each column j by v_1/w_{j,1}. The result is exactly the standard nine-coordinate matrix used by the global factor census.

These formulas give a rational global coordinate chart for labeled projective configurations in uniform position. Uniqueness follows because fixing the first four projective points leaves a diagonal projectivity, and fixing the fifth all-ones point forces it to be scalar. Thus **there are no normalization-chart transitions to certify in the interior of one fixed labeled uniform parent cell**. Unbounded coordinate directions are still part of the chart and must be included in any full decomposition.

**Orientation caveat:** the column rescalings can be negative, so the normalized chirotope can differ by a fixed reorientation. The parent bracket signs determine that reorientation; the correct normalized signs must be used.

An exact SymPy replay verified the normalization identities and independently recomputed all 70 normalized parent brackets: eight constant, 62 variable. This is not an exhaustive CAD of the parent sign region.

The repository's prior factor census gives 26,740 primitive residual equations and parent-2599's necessary-condition filter leaves 17,824 candidates. The complete nine-dimensional sign-invariant chamber decomposition, all adjacencies, and the global master-graph verdict are **not computed**. No global D9 theorem is claimed.

**STOP / INCOMPLETE.** See `ai/omreal/DIAG9_GRAPH_GLOBAL_FACTOR_CENSUS.md` and `ai/omreal/NINTH_DIAGONAL_SAFE_GRAPH.md` for the underlying source theorems.
