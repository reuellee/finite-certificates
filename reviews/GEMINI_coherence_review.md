I will now execute the verification script `verify_overcomplete_coherence.py` to ensure all symbolic and randomized rational checks pass as claimed, verifying the exact numerical values and bounds.
### Formal Review of: "Coherence penalties distort overcomplete SAEs: an exact finite certificate"

**Verdict:** **VERIFIED-SOUND**
**Weakest Link / Primary Limitation:** **Low-dimensional Oracle Gap.** While the mathematical framework is exact and airtight, its primary limitation lies in the assumption of *population-level exact convex (oracle) coding* in low dimensions ($d = 2, m = 3$). Real-world SAEs operate in high dimensions, utilize parameterized, non-convex feedforward encoders (linear + ReLU), and are optimized via stochastic gradient descent (SGD) rather than achieving the exact global minimum of the population objective.

---

### Detailed Attack Evaluation

#### (i) Class-wide Base-Loss Lemma & KKT Sufficiency
*   **Assessment:** **Airtight.**
*   **Mathematical Derivation:**
    The population coding objective for $x \in \mathbb{R}^2$ with a unit-norm dictionary $D = [d_1, \dots, d_m]$ is:
    $$\min_{f \geq 0} E(f) = \|x - D f\|_2^2 + \lambda \sum_{i=1}^m f_i$$
    Since the objective is convex and differentiable on the domain $f \geq 0$, the Karush-Kuhn-Tucker (KKT) conditions are both necessary and sufficient for global optimality. 
    At $x = e_1$, with $d_1 = e_1$ and candidate code $f^* = [1 - \lambda/2, 0, \dots, 0]^T$, the residual is $r = e_1 - d_1(1 - \lambda/2) = (\lambda/2) e_1$. 
    *   For the active atom $d_1 = e_1$: $d_1^T r = e_1^T (\frac{\lambda}{2} e_1) = \frac{\lambda}{2}$ (exactly satisfies KKT).
    *   For any inactive unit atom $d_j$ ($j > 1$): $d_j^T r = \frac{\lambda}{2} d_j^T e_1 \leq \frac{\lambda}{2}$ by Cauchy-Schwarz, since $\|d_j\|_2 = 1$ and $\|e_1\|_2 = 1$.
    Under parametrization $d_j = d_\theta = (\cos \theta, \sin \theta)$, the inactive slack identity is:
    $$\text{slack} = \frac{\lambda}{2} - d_\theta^T r = \frac{\lambda}{2} (1 - \cos \theta) = \lambda \sin^2(\theta/2) \geq 0$$
    This identity is exact, and because the slack is unconditionally non-negative, the candidate code $f^*$ is guaranteed to be a global minimizer. No alternative sparse codes (including those utilizing coherent atoms) can achieve a lower loss. Symmetrically, this holds for $x = e_2$ in any dictionary containing $e_2$. The base loss is thus exactly $\lambda - \lambda^2/4 = 19/100$ for all dictionaries containing $\{e_1, e_2\}$.

#### (ii) Gram Class Identity for $m=3$
*   **Assessment:** **Airtight.**
*   **Mathematical Derivation:**
    For any faithful $m=3$ dictionary $D = \{e_1, e_2, d_3\}$ where $d_3 = (x, y)$ is a unit vector:
    $$P(D) = \langle e_1, e_2 \rangle^2 + \langle e_1, d_3 \rangle^2 + \langle e_2, d_3 \rangle^2 = 0 + x^2 + y^2 = 1 \text{ exactly}$$
    The theorem statement correctly restricts its scope to $m=3$ (Section 2, §5). At $m > 3$, extra atoms $\{d_3, \dots, d_m\}$ contribute a penalty of $P(D) \geq m-2$. Since the base loss of any faithful dictionary is bounded below by $19/100$ per point, the faithful class objective is at least $19/100 + \beta(m-2)$. Extra atoms can indeed lower the objective of the competitor distorted frame, but the note is fully transparent and mathematically sound under its stated $m=3$ scope.

#### (iii) $\beta = 0$ Control
*   **Assessment:** **Airtight.**
*   **Mathematical Derivation:**
    For unit atoms and $f \geq 0$, the triangle inequality yields $\|Df\|_2 = \|\sum_j f_j d_j\|_2 \leq \sum_j f_j \|d_j\|_2 = \|f\|_1$.
    By the reverse triangle inequality, the reconstruction loss for any unit data vector $x$ satisfies:
    $$\|x - Df\|_2^2 + \lambda \|f\|_1 \geq (1 - \|Df\|_2)^2 + \lambda \|f\|_1$$
    Letting $\rho = \|Df\|_2$ and $F = \|f\|_1$ (where $\rho \leq F$):
    $$E(f) \geq (1 - \rho)^2 + \lambda F \geq (1 - \rho)^2 + \lambda \rho = \left( \rho - \left(1 - \frac{\lambda}{2}\right) \right)^2 + \lambda - \frac{\lambda^2}{4} \geq \lambda - \frac{\lambda^2}{4}$$
    Since both $e_1$ and $e_2$ have unit norm, the average coding loss is bounded below by $\lambda - \lambda^2/4 = 19/100$. The faithful class attains this bound exactly. Thus, when $\beta = 0$, the faithful class is globally optimal, verifying that the distortion is purely remedy-induced.

#### (iv) Onset Derivation Claim
*   **Assessment:** **Airtight.**
*   **Mathematical Derivation:**
    Consider the symmetric-split family $d_{1,2} = (\cos \theta, \pm\sin \theta)$, $d_3 = e_2$. For small $\theta$, coding $x = e_2$ using only $d_3$ yields a constant loss of $\lambda - \lambda^2/4$. For $x = e_1$, symmetry dictates $f = [t, t, 0]^T$, yielding reconstruction $Df = (2t \cos \theta)e_1$. Minimizing $E_1(t) = (1 - 2t \cos \theta)^2 + 2\lambda t$ gives $t = \frac{2\cos\theta - \lambda}{4\cos^2\theta}$, and base loss:
    $$E_1(\theta) = \frac{\lambda}{\cos \theta} - \frac{\lambda^2}{4\cos^2\theta} \approx \left(\lambda - \frac{\lambda^2}{4}\right) + \theta^2 \frac{\lambda(2 - \lambda)}{4} + O(\theta^4)$$
    The average base loss is $\bar{E}(\theta) \approx \left(\lambda - \frac{\lambda^2}{4}\right) + \theta^2 \frac{\lambda(2 - \lambda)}{8}$.
    The Gram penalty is:
    $$P(D) = \langle d_1, d_2 \rangle^2 + \langle d_1, d_3 \rangle^2 + \langle d_2, d_3 \rangle^2 = \cos^2(2\theta) + 2\sin^2\theta \approx 1 - 2\theta^2 + O(\theta^4)$$
    The total objective expansion is:
    $$L(D) \approx L(0) + \theta^2 \left[ \frac{\lambda(2-\lambda)}{8} - 2\beta \right]$$
    Instability occurs exactly when the $\theta^2$ coefficient is negative:
    $$\beta > \frac{\lambda(2-\lambda)}{16}$$
    For $\lambda = 1/5$, $\beta_{\text{onset}} = 9/400 = 0.0225$. This derivation is extremely clean and correct.

#### (v) SGD/Trained-SAE Relevance & Scope
*   **Assessment:** **Properly Framed.**
    Section 5 ("Honest scope") explicitly details that the certificate is restricted to the population objective and oracle (exact convex) coding. The theoretical positioning is highly appropriate: showing that the global optimum of the penalized objective itself excludes the true features establishes a fundamental, optimization-independent barrier that no learning algorithm (such as SGD) can overcome if it successfully minimizes that objective.

#### (vi) Logical Validity of the Theorem Exclusion
*   **Assessment:** **Airtight.**
    A dictionary containing "the true features" $\{e_1, e_2\}$ must satisfy $\{e_1, e_2\} \subseteq D$. Any such dictionary is faithful by definition.
    The proof shows that for any faithful dictionary $D_{\text{faithful}}$, the objective satisfies $L(D_{\text{faithful}}) > L(D_{\text{witness}})$ for a specific non-faithful witness dictionary $D_{\text{witness}}$ (the 5-12-13 frame).
    By contradiction, if the penalized-optimal dictionary $D^*$ contained the true features, it would have to be faithful, implying $L(D^*) > L(D_{\text{witness}})$, which violates the optimality of $D^*$. Thus, $D^*$ cannot be faithful, and cannot contain both true features. The logical deduction is rigorous and correct.
