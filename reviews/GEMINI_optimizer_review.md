### Peer Review & Adversarial Audit Report: Finite-Certificate Optimizer Counterexamples

**Verdict: VERIFIED-SOUND**

The mathematical proofs and empirical certificates provided in the note are **exceptionally rigorous, correct, and highly valuable**. The code in `verify_muon_ns.py` and `verify_lion.py` provides exact rational arithmetic and high-precision floating-point verifications that are completely sound. The note's criticisms represent a major contribution to bridging the theory-practice gap in deep learning optimization.

---

### Detailed Attack-by-Attack Analysis

#### (i) CERT-M1 & CERT-M2: Muon Tuned Coefficient computations & Dimension Scoping
*   **Arithmetic Check:** The evaluation of the tuned quintic at $x=1$ is exactly:
    $$p(1) = 3.4445(1) - 4.7750(1)^3 + 2.0315(1)^5 = 3.4445 - 4.7750 + 2.0315 = 0.7010$$
    Using exact rationals ($\frac{34445}{10000} - \frac{47750}{10000} + \frac{20315}{10000}$), this is exactly $701/1000$. 
    The orthogonality residual is:
    $$\delta_1 = \left| 1 - p(1)^2 \right| = 1 - (0.701)^2 = 1 - 0.491401 = 0.508599$$
    This matches the exact rational $\frac{508599}{1000000}$ perfectly.
*   **Is $1 \times 1$ a fair instance?** Yes, absolutely. The Newton–Schulz (NS) iteration on any dimension matrix $X$ acts independently on its singular values via the polynomial $p(s_i)$. Consequently, the multidimensional matrix dynamics decouple completely into independent scalar iterations on its singular values. A $1 \times 1$ matrix with a singular value of 1 is a mathematically rigorous and dimension-independent representative.
*   **Does the $\delta_0 = 0$ edge case matter?** No. For any Taylor-based truncation, $p(1) = 1$ is an identity, preserving perfect orthogonality ($\delta_1 = \delta_0 = 0$). For the tuned coefficients, the fact that $p(1) = 0.701 \neq 1$ means that even starting with a perfectly orthogonal matrix, the residual immediately jumps to $0.5086$. By continuity, any matrix in a neighborhood of orthogonality (e.g., $\delta_0 = 10^{-6}$) will see its residual *increase* to $\approx 0.5086$ rather than decay, proving the decay law fails everywhere near $x=1$. This is a robust demonstration of local instability, not a pathological boundary artifact.

#### (ii) Theoretical Coverage vs. Stated Scope Overreach
*   **Is the note attacking a strawman?** No. The abstract and introduction of arXiv:2601.19156 explicitly claim to analyze *"Muon as originally proposed (Jordan et al., 2024) and as used in practice."* 
*   **Legitimacy of critique:** While Theorem 2 stands "as literally stated" for Taylor coefficients, the paper's load-bearing rate guarantees rely entirely on the decay mechanism $\chi_q \to 1$ as the number of steps $q$ grows. Because the deployed coefficients do not converge to the polar factor, $\chi_q$ never approaches $1$ (it is blocked by the continuity obstruction showing singular values oscillate chaoticly in a bounded band). Therefore, the paper's convergence guarantees are mathematically inapplicable to the practical optimizer. Calling out this mismatch between sweeping abstract claims and restrictive proof conditions is a highly legitimate and vital role of a reviewer.

#### (iii) CERT-M4: Li-Hong Step-Size Condition and Lyapunov Analysis
*   **Verify the Emptiness Algebra:** The stepsize condition is indeed verbatim:
    $$\eta \le \frac{1}{8L} \sqrt{\frac{1 - 2\beta}{2\beta}}$$
    If $\beta \ge 1/2$, the radicand is non-positive, making the set of admissible positive stepsizes empty. For the default Muon momentum $\beta = 0.95$, the radicand is $-9/19$, yielding an imaginary bound.
*   **Typo or Structural Gap?** This is **not a typo**; it is a structural limitation of their proof technique. In heavy-ball momentum analysis, using a simple Lyapunov function of the form $V_t = f(x_t) + C \|x_t - x_{t-1}\|^2$ requires the "kinetic energy" term to be dissipated by the gradient step. This dissipation condition mathematically forces a small momentum parameter (specifically $\beta < 1/2$) to guarantee descent at each step. To support large momentum ($\beta \to 1$), a more sophisticated coupled potential function is required. The note's framing of this as a "scoping observation showing the theorem is vacuous in the practical regime" is extremely accurate and professionally stated.

#### (iv) Lion 2-Cycle: Noise & Tie-Breaking Robustness
*   **Sign(0) Handling:** On the exact 2-cycle, the momentum term $m$ alternates between $\mp \eta / 398$, and the sign arguments are:
    $$c_t = \pm \frac{19\eta}{398} \neq 0$$
    Because the argument is strictly bounded away from zero, the cycle does not rely on any arbitrary $\operatorname{sign}(0)$ tie-breaking rule.
*   **Does $\sigma=0$ satisfy assumptions?** Yes. Assumptions 1–3 of arXiv:2411.07724 are fully satisfied with $L=1$ and $\sigma=0$. A standard stochastic rate bound must also hold in the noise-free deterministic limit; if it does not, the bound has a structural flaw. The exact 2-cycle proves that the constant-parameter variant fails to converge even under zero noise on a simple 1D quadratic, mathematically proving that horizon-dependent hyperparameter annealing is a necessary condition for convergence rather than an artifact of the proof.

#### (v) Prior Art & Originality
*   **Credit & Honesty:** The note is exemplary in its scholarly honesty. It explicitly credits Jordan et al. (2024), PolarExpress (Amsel et al. 2025), and Shulgin et al. (2025) for identifying related phenomena (non-convergence of tuned quintics, inexact LMO gap). 
*   **Novelty:** The novelty of this note lies in **formalizing these observations into exact-arithmetic, checkable mathematical certificates** that directly invalidate specific theorems in peer-reviewed literature (e.g., proving the decay law fails for practical Muon, proving the stepsize set is empty for practical Li-Hong momentum, and constructing robust, tie-free Lion 2-cycles).

---

### Specific Recommendations to Further Strengthen the Note

1.  **Contextualize Lyapunov limitations (M4):** Briefly mention that while the Li-Hong condition is vacuous for $\beta \ge 1/2$, this is a classic bottleneck of simple heavy-ball Lyapunov functions (e.g., as discussed in Sun et al., 2019). This clarifies to readers that the issue is a fundamental structural proof limitation rather than an algebraic typo.
2.  **Highlight the Physical Interpretation of Lion Cycles:** Point out that the Lion 2-cycle is essentially an under-damped orbital oscillation. This adds an intuitive geometric interpretation of why constant-stepsize sign-momentum optimizers fail to settle on quadratics.
