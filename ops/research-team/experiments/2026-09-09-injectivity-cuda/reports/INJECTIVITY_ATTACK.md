# Injectivity attack: the original theorem remains open

9 September 2026. **The requested universal injectivity was not proved. No original counterexample was found. The theorem ledger remains 2/9.** This cycle closes zero original obligations and removes no original source cases. Its two useful outputs are a precise boundary lemma for private separating vectors and an exact abstract countermodel to a broad class of proposed injectivity arguments. Neither is a solution of the original problem.

The research starts from [PR49 head 59fec666](https://github.com/reuellee/finite-certificates/tree/59fec66666518257c585194b81061f60d91f439d), tree `9d3be78b6e8235af786c2ccb2ac24d977f12347a`. The latest exploration close and the canonical prospectus both leave injectivity open. No historical theorem, certificate, or remote repository was modified. The checkpoint contains the exact consulted source subset and all new artifacts; it is not a complete repository-history backup.

## Original target

For every realizable uniform rank-four parent on eight elements, every component of its normalized realization space X, and every three-element antichain of proper extension signatures, set

\[
A_{ij}=B_i\cap B_j,\qquad T=B_0\cap B_1\cap B_2.
\]

The target is injectivity of the actual restriction map

\[
D:\bigoplus_{i<j}H_c^1(A_{ij};\mathbb Q)\longrightarrow H_c^1(T;\mathbb Q),
\qquad D(a,b,c)=r_{01}a-r_{02}b+r_{12}c.
\]

All zero-weight faces, feasibility boundaries and genuine parent infinity remain included. Triple degree-zero vanishing is not assumed. The separate triple-component obligation would remain even if this map were proved injective. See the pinned [theorem prospectus](https://github.com/reuellee/finite-certificates/blob/59fec66666518257c585194b81061f60d91f439d/ai/omreal/9DVL_THEOREM_PROSPECTUS.md).

## Constructive attack

The proof track first tested a stronger route, vanishing of every pair Hc1 group, by normalizing the two private extension vectors together. Parent four-brackets remain bilinear in the two height rows. Fixing one row gives convex fibers but does not control the topology after that row is also projected away. The pinned double-contraction source already records this obstruction; it earns no new theorem credit here.

The next test retained private vectors to maintain the two good-locus conditions in the single-exclusive detector target. It yielded the following auxiliary lemma. If A(Y) is a signed derived-normal matrix and F is its strict-feasibility locus, define

\[
p_*(Y)=\operatorname*{argmin}_{A(Y)p\ge\mathbf1}\|p\|^2.
\]

On F this minimizer exists uniquely, is semialgebraic and continuous, and has a closed graph in X times R4. If good parents approach a bad parent that is still inside X, the minimizer norm tends to infinity. The proof uses strict feasible comparison vectors, coercivity and uniqueness; it is in `prover/FINDINGS.md`.

This divergence belongs to the margin-normalized private vector. Rescaling to a projective direction can remove its norm divergence. It does not mean the parent escapes. The known row2599 feasible-end/infeasible-middle interval supplies an actual parent path where such a private boundary must occur, conditional on that inherited exact certificate. That historical arithmetic was not rerun in this cycle.

The resulting gap is specific: a construction using private vectors must retain these interior feasibility-boundary faces and prove their signed attachment to the other blocks. The proof track did not establish the required attachment or detector nondegeneracy.

## Exact abstract countermodel

The falsifier constructed three bad loci in the contractible nine-dimensional surrogate space R2 times R7. They are sign-feasibility loci of one polynomial seven-row, four-column matrix with full rank everywhere and no zero rows. The corresponding good regions are proper and pairwise incomparable. All inherited lower compact-support vanishing patterns hold in this model.

Each pair group is Q and the triple group is Q2. Relative simplicial cochains compute

\[
D=\begin{pmatrix}-1&0&1\\-1&-1&0\end{pmatrix},
\qquad \ker D=\mathbb Q(1,-1,1).
\]

Every individual restriction is injective, and any two image lines have zero intersection. The three contributions nevertheless cancel jointly. Each pair and triple component is noncompact, and each exclusive-pair stratum is nonempty with vanishing Hc1. Thus those properties, even combined with a common polynomial Gordan matrix, do not prove joint injectivity.

The all-parameter polynomial feasibility calculation is proved in `falsifier/FINDINGS.md`. The finite complex, matrix, signatures and explicit collision point are in `falsifier/MODEL.json`; exact replay reconstructs the cohomology rather than merely checking the displayed matrix product.

**This is not a 9DVL counterexample.** At an explicitly retained finite point, two distinct matrix rows coincide. For an actual uniform rank-four parent, different parent triples span different hyperplanes, so their derived normals can never be proportional. The abstract matrix also does not certify the original shared-column and compound identities. Excluding this one model is not a proof that all other joint cancellation mechanisms are impossible.

## Verification and accounting

Independent review verdict: **ACCEPT_AUXILIARY_AND_ABSTRACT_ONLY**. The referee independently reproduced the relative cohomology, the signed map and kernel, six all-parameter polynomial dual identities, and seven rejected hostile controls. Its 192 primal and 240 dual rational checks are regression controls; the universal feasibility claim rests on the written proof and polynomial identities. The private-separator lemma passed independent deductive review. The opening referee found no defect in the original map, its compact-support variance or the canonical detector equivalence. The source audit treats inherited theorem/certificate dependencies explicitly; it does not claim to revalidate all previous research or provide Lean certification.

The frozen prover handoff contains a source-integrity checker and written proofs. That checker proves file identity only. The falsifier handoff includes an exact rational cochain checker and hostile controls. The separately implemented referee replay imports no producer acceptance logic. Its final mathematical scope audit is in `referee/FINAL_REVIEW.md`; results are in `referee/INDEPENDENT_REPLAY.json`.

| Quantity | Opening | Closing |
|---|---|---|
| Proved diagonals | 2/9 | 2/9 |
| Original injectivity | Open | Open |
| Original triple Hc0 vanishing | Open | Open |
| Original operational obligations open | 7 | 7 |
| Original obligations closed by this cycle | — | 0 |
| Pair global coverage/residual | UNKNOWN | UNKNOWN |
| Triple source records unresolved | 1,162,302 | 1,162,302 |
| Certified original source decrease | — | 0 |

The source records are not connected-component counts. Classification: **inconclusive for the requested theorem; auxiliary deductive and abstract exact results only**. These findings do not justify declaring injectivity solved, running a larger unmotivated saturation search, or promoting diagonal three.

## Checkpoint contents

- `SOURCE_MANIFEST.json` and `GITHUB_TREE.json`: consulted source identities and pinned Git blobs.
- `WORK_ORDER.md`: original target, team boundaries and resource limits.
- `prover/`: failed geometric routes, boundary lemma, source pins and handoff.
- `falsifier/`: polynomial countermodel, exact finite cochains, verifier and handoff.
- `referee/`: independent opening and final reviews, separate replay and source accounting.
- `CLOSING_STATE.json`, `CHECKPOINT_MANIFEST.json`, `CLEAN_RESTORE_REPLAY.json`: final claim status and recovery verification.

Only the read-only source subset and current work are included. Existing full-history backups and PR49 are preserved. No paid compute, external human messaging or public publication occurred in this cycle.
