# Conjecture harvest — ML-theory conjectures refutable/resolvable by finite certificate

Harvested 2026-07-25. Scores: **B** = search-space boundedness (1-5), **V** = verification cheapness (1-5),
**C** = consequence-if-resolved (1-5). Rank key = C x refutability (B,V).

## Ranked table

| # | Conjecture (gist) | Source | Year | Certificate shape | B | V | C | Prior attacks |
|---|---|---|---|---|---|---|---|---|
| 1 | **Conjecture 6.6, "Maxout Polytopes"** (Balakin, Cox, Loho, Sturmfels): (1) max #vertices of a (3,n,1)-maxout polytope (= (3,n)-zonoboxtope, conv of two zonotopes with parallel proportional generators) is 4*sum_{k<=2} C(n-1,k) for n odd, minus (n-2) for n even; (2) for 4<=d<=n, max #vertices of (d,n,1) is 4*sum_{k<=d-1} C(n-1,k) (= the absolute cap — pure achievability claim, **never verified for any d>=4**); (3) general (d,n,m) formula. | [arXiv:2509.21286](https://arxiv.org/abs/2509.21286) §6 | 2025 | Explicit rational generators v_i, scalings λ_i + per-vertex rational witness directions. Confirms (2)/(odd-n of 1) by achieving the cap; refutes (1) by exceeding 4ΣC(7,k)−6 = 110 at n=8. Their evidence: random sampling (1000 draws) at d=3, n<=6 only. | 5 | 5 | 3 | None found beyond the paper's own sampling (posed Sep 2025, lightly mined) |
| 2 | **Exact depth of MAX_n for ReLU nets** (successor to fallen Hertrich–Basu–Di Summa–Skutella conjecture): open gap between lower bound ceil(log3 n) (proved only for decimal-fraction weights) and upper bound ceil(log3(n-2))+1. Concretely open: can 2 hidden layers compute max of 6..9 numbers? | [arXiv:2505.14338](https://arxiv.org/abs/2505.14338) (STOC'26), [arXiv:2502.06283](https://arxiv.org/abs/2502.06283) (ICLR'25) | 2025 | Explicit 2-hidden-layer net computing max of 6 (CPWL identity checked exactly with sympy region-by-region). One-sided: only the "possible" direction is certifiable. | 3 | 4 | 4 | Heavily mined area — the parent conjecture fell in May 2025 via exactly this pattern; experts actively constructing |
| 3 | **Deep UFM neural collapse**: whether NC (simplex-ETF) configurations are the *only* global optima of the L-layer unconstrained-features model for small regularization / L>=3 nonlinear; recent work proves special regimes (ResNets/transformers, wide nets), general case explicitly open. | [arXiv:2505.15239](https://arxiv.org/abs/2505.15239), [arXiv:2402.03991](https://arxiv.org/abs/2402.03991) | 2024-25 | A small explicit deep-UFM instance (tiny K, d, L, rational weight decay) with an exactly-verified non-NC critical point of lower loss than the ETF value. Verification exact; *finding* it requires nonconvex search. | 3 | 4 | 4 | Active area, several groups; partially mined |
| 4 | **Hidden minima in two-layer ReLU nets** (Arjevani): explicit conjectures on spectral structure / loss asymptotics of symmetric ("hidden") critical points for the d=k student-teacher setting. | [arXiv:2312.16819](https://arxiv.org/abs/2312.16819) | 2023-24 | Exact symbolic (sympy) analysis of stated families at small d,k: confirm/refute claimed eigenvalue signs. Confirmation-type certificate. | 4 | 4 | 2 | Author's own series; otherwise lightly mined |
| 5 | **RASP-L / C-RASP length-generalization conjecture** (Zhou et al. '24; formalized by Huang et al. '25): transformers length-generalize exactly on tasks expressible in C-RASP. | [arXiv:2505.11199](https://arxiv.org/abs/2505.11199) and refs therein | 2024-25 | Refutation needs a *trained-model* failure — not exact/cheap. Poor certificate fit despite high interest. Also open: AHAT vs SMAT expressivity separation (certificate = explicit language + exact simulation argument, hard). | 2 | 2 | 5 | Actively mined |
| 6 | **Maxout-polytope f-vector realizability** (same paper, §5-6): which f-vectors arise for deeper maxout polytopes; Theorem 6.1 tight for d=2, everything conjectural for d>=3 beyond n=6. | [arXiv:2509.21286](https://arxiv.org/abs/2509.21286) | 2025 | Same machinery as #1: explicit configs + exact hull. | 5 | 5 | 2 | None (fresh) |
| 7 | **Grokking impossibility conjecture** (Mohamadi et al.): accuracy-based generalization impossible in early phase due to permutation equivariance on modular addition. | [arXiv:2407.12332](https://arxiv.org/abs/2407.12332) | 2024 | Statement about training dynamics/distributions — no finite exact certificate. | 1 | 2 | 3 | Lightly mined |
| 8 | **MoE expressivity via tropical geometry**: counting conjectures for regions/expressivity of sparsely-routed MoE (posed in "Sparsity is Combinatorial Depth"). | [arXiv:2602.03204](https://arxiv.org/abs/2602.03204) | 2026 | Explicit small MoE + exact tropical region count. (Contents not yet verified in detail — future session should extract exact conjecture statements.) | 4 | 4 | 2 | None found (very fresh) |
| 9 | **Monotone ReLU depth** open problems (Hertrich et al. successor line). | [arXiv:2505.06169](https://arxiv.org/abs/2505.06169) | 2025 | Explicit monotone-weight net for a target CPWL function; exact sympy check. (Exact statements to be extracted.) | 3 | 4 | 3 | Lightly mined |
| 10 | **Edge-of-stability**: various "sharpness settles near 2/eta" conjectural claims; recent papers (norm-vs-sharpness bias, stochastic sharpness gap) contain conjectures but all involve limiting training dynamics. | [arXiv:2505.21423](https://arxiv.org/abs/2505.21423) etc. | 2024-25 | Dynamics statements; exact finite certificates only for toy quadratics where already settled. Poor fit. | 2 | 2 | 3 | Heavily mined |

## Rationale for target choice

**Target = #1 (Conjecture 6.6).** It is the purest certificate target on the list:
- Part 2 at its smallest instance (d=4, n=4: "32 vertices achievable") has *never been computationally verified* — the paper's sampling was d=3 only. A rational instance achieving 32 resolves-in-the-affirmative the smallest open case, with a fully exact, self-contained certificate (witness direction per vertex; only Fraction arithmetic needed).
- Part 1 at n=8 (first even case beyond their DFS range n<=6) is *refutable* by an instance with >=112 vertices vs the conjectured max 110.
- Built-in sanity check: my search at d=3, n=3..6 must reproduce exactly their 16/26/44/60 — validating that my formalization of "zonoboxtope" matches theirs before any claim is made.
- Posed 2025-09 by a heavyweight team (Sturmfels et al.), no follow-up attacks found as of 2026-07.

## Interpretation caution (honesty note)

The paper defines a (d,n)-zonoboxtope as conv(sum a_i I_i ∪ sum b_i I_i), I_i line segments, a_i, b_i >= 0,
"corresponding generators parallel", explicitly *excluding* translated segments (their formula (6) variant).
We use **centered** segments I_i = [-v_i, v_i]; centered segments are line segments, so every instance we
exhibit is a legitimate zonoboxtope under their definition regardless of anchoring convention, making both
confirmation and refutation certificates safe. The d=3 sanity check (16/26/44/60) further pins the reading.
