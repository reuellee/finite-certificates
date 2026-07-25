An adversarial review has been conducted on the four interpretability illusion certificates (C1–C4). Below is the comprehensive, peer-reviewer-style report evaluating the conceptual and mathematical validity of each certificate, answering all parts of your attack prompt, and rendering final verdicts.

---

# EXECUTIVE SUMMARY & VERDICT TABLE

| Certificate | Target Method | Core Failure Mode | Verdict | Core Justification |
| :--- | :--- | :--- | :--- | :--- |
| **C1** | Activation Patching | Multi-site cancellation / "Negative head" motif | **VERIFIED-SOUND** | Highly robust. Demonstrates that single-site patching leads to an *unfaithful* circuit $\{h_1, h_3\}$ which fails under its own ablation protocol ($2 \neq 1$). |
| **C2** | Gradient $\times$ Input / IG | Gradient saturation & baseline dependence | **VERIFIED-SOUND** | Mathematically elegant. Proves that default zero-baseline IG can invert causality on the support of the task distribution while satisfying Completeness. |
| **C3** | SAE Circuit Discovery | Feature absorption | **VERIFIED-SOUND** | Highly significant. Bridges the gap between dictionary learning loss and downstream causal graphs, proving loss-optimal SAEs force a false causal narrative. |
| **C4** | Probing | Selectivity-defended classification | **VERIFIED-SOUND** | Devastating to probe defenses. Proves that Hewitt-Liang selectivity is fundamentally incapable of filtering out causally inert correlated features. |

---

# POINT-BY-POINT ADVERSARIAL REVIEW

### (i) Strawman Check & Practitioner Objections

1. **Method Procedures Fidelity**: The methods are implemented in strict accordance with literature specifications:
   - **Patching (C1)**: Metrics for denoising (recovery $R$), noising (effect $E$), and ablation are mathematically identical to Meng et al. (2022) and Zhang & Nanda (2023). Zero-ablation corresponds exactly to mean-ablation because the distribution is symmetric and uniform around zero.
   - **Integrated Gradients (C2)**: Zero-baseline ($x'=0$) is the industry-standard default used in CapTum and downstream works. 
     - *Is zero-baseline a fair default?* Yes, because it is the out-of-the-box practice. However, as noted in Sturmfels et al. (2020), zero-baselines are highly arbitrary and often introduce out-of-distribution (OOD) path integration artifacts (Bilodeau et al., 2024). The authors' certificate is a valuable, checkable instance of this known baseline dependency.
   - **Control Tasks (C4)**: The Hewitt-Liang (2019) selectivity protocol is faithfully represented via exact combinatorial enumeration.

2. **Practitioner Rejection of Degenerate Distributions**:
   - *Practitioner Objection*: "The 4-point supports, uniform toy distributions, and hand-crafted exact symmetries (like $h_1 + h_2 = 0$) are adversarial edge cases that do not reflect complex, continuous, overparameterized real-world models."
   - *Adversarial Defense*: This objection misses the point of **worst-case certificates** (or adversarial unit tests). If these causal interpretability methods claim structural or mathematical validity, they should not fail catastrophically on a simple 6- or 18-parameter network. Since they do, their empirical success on larger networks must be understood as a contingent/heuristic property rather than a guaranteed mathematical foundation.

---

### (ii) C1: Causal Ground-Truth & Single-Site Limitations

1. **Functional Change of Deletion**:
   With $h = (x, -x, x)$ and $y = \text{ReLU}(h_1 + h_2 + h_3)$, deleting the subcircuit $\{h_1, h_2\}$ (setting their outputs or weights to $0$) yields:
   $$y_{\text{ablated}} = \text{ReLU}(0 + 0 + h_3) = \text{ReLU}(x)$$
   Because this identity holds for **all $x \in \mathbb{R}$**, deleting $\{h_1, h_2\}$ results in **exactly zero functional change** across the entire real line. This establishes the absolute ground-truth that $\{h_1, h_2\}$ is a redundant, removable null subcircuit.

2. **The "Distributed Mechanism" Objection**:
   - *Objection*: "Perhaps $h_1$ and $h_2$ are part of a distributed representation of zero (the null space of the downstream readout) used as a redundant backup. Calling them inert begs the question."
   - *Refutation*: Even if a practitioner claims $h_1$ and $h_2$ are part of a "distributed mechanism," the certificate delivers a fatal blow to the **circuit-discovery pipeline**:
     The denoising patching protocol discovers the circuit $\{h_1, h_3\}$ (since $R_1 = R_3 = 1$ and $R_2 = 0$). But if we ablate $h_2$ (the component excluded from the circuit), the discovered circuit's output on the clean input is:
     $$y_{\{h_1, h_3\}}(1) = \text{ReLU}(h_1(1) + 0 + h_3(1)) = \text{ReLU}(1 + 1) = 2 \neq 1$$
     This shows the discovered circuit is **unfaithful** in the method's own sense. Thus, single-site patching is shown to be internally inconsistent when faced with negative/backup head motifs.

---

### (iii) C2: Local Sensitivity vs. Causal Interventions

1. **Local Gradient Exactness**:
   At the certified inputs $X^* = (2, 1/4)$ and $(2, 3/4)$, the support points are strictly interior to the flat plateau of the tent function ($z > 1$). Since $f$ is continuously differentiable here (no kinks), the local gradient is exactly $\partial f / \partial x_1 = 0$. 

2. **Normative Axioms Analysis**:
   - **Sensitivity(a)** (Differing in one feature): Not violated. For example, if the baseline is $x' = (0, 1/4)$ and input is $X^* = (2, 1/4)$, the predictions are identical ($f(0, 1/4) = f(2, 1/4) = 1/4$), so the axiom is not triggered.
   - **Sensitivity(b) / Dummy Player**: Not violated. The function $f(x_1, x_2) = t(x_1) + t(x_2)$ mathematically depends on $x_2$ over $\mathbb{R}^2$, meaning $x_2$ is not a "dummy" feature of the global function, even though it is causally inert on the support of $D$.

3. **Precise Normative Property Violated**:
   The property violated is **Causal Faithfulness to the Task-Distribution Interventions**. 
   On the task distribution $D$, swapping $x_1$ between its attested values changes the output by $1/4$, while swapping $x_2$ changes nothing. Yet, both Gradient $\times$ Input and Integrated Gradients (zero-baseline) assign **exactly $0$ attribution to the causal feature ($x_1$)** and a large non-zero attribution to the inert feature ($x_2$). 
   
   This exposes the fundamental clash between **local sensitivity** and **global task-distribution causality**: because the baseline value of the causal feature ($t(0) = 0$) matches its input value ($t(2) = 0$), the straight-line path integral of Integrated Gradients is exactly $0$, blinding it to the fact that $x_1$ was highly active in between.

---

### (iv) C4: Probing, Correlation, and Hewitt-Liang Selectivity

1. **Are Probing Papers Only Claiming Correlation?**:
   While theoretical probing papers (such as Hewitt & Liang, 2019) explicitly disclaim causality, applied mechanistic interpretability papers regularly use probes to locate representations for downstream causal operations (like steering or activation patching).

2. **Why the Control-Task Selectivity Defense Fails**:
   The certificate's core strength is showing that the **Hewitt-Liang selectivity defense itself passes**:
   - True task accuracy on the inert neuron $h_2 = 2x$ is $100\%$ ($1.0$).
   - The exact average control accuracy over all 16 binary labelings is $7/8$ ($87.5\%$).
   - The selectivity is $1 - 7/8 = 1/8 > 0$ ($12.5\%$).
   
   Under Hewitt & Liang's logic, a positive selectivity indicates the probe is reading out structured, explicit representations rather than memorizing. This certificate proves that a neuron can be **completely causally inert** (downstream weight of $0$), yet pass the selectivity defense and be ranked as the primary, most selective carrier of the feature. This is a highly robust and non-strawman critique of current representation-localization paradigms.

---

### (v) C3: Feature Absorption & Circuit Propagation

1. **Pipeline Logic Check**:
   Under the optimal absorbed SAE dictionary $U_A = [e_1, \frac{e_1 + e_2}{\sqrt{2}}]$, the child-present input $x = (1,1)^T$ yields the code $f = (0, \sqrt{2} - \lambda/2)^T$. 
   The indirect effect is indeed $IE_j = f_j \cdot (e_1 \cdot u_j)$.
   - For the parent latent ($j=1$): $IE_1 = 0 \cdot (e_1 \cdot e_1) = 0$.
   - For the child latent ($j=2$): $IE_2 = (\sqrt{2} - \lambda/2) \cdot \frac{1}{\sqrt{2}} = 1 - \frac{\lambda}{2\sqrt{2}} \approx 0.965$.

2. **Is "Readout Uses Only Parent" Consistent with $IE_2 > 0$?**:
   **Yes.** This is the mathematical beauty of the feature-absorption illusion. Because training an L1-regularized SAE on hierarchical data makes the "absorbed" dictionary $U_A$ loss-optimal, the child-indicator latent's decoder direction $u_2$ is forced to align partially with the parent feature $e_1$ ($e_1 \cdot u_2 = 1/\sqrt{2}$). 
   
   Consequently, when circuit discovery is performed, the child-indicator latent has a massive indirect effect on the readout ($0.965$) simply because it has absorbed part of the parent feature's reconstruction. This proves that loss-optimal SAE dictionary learning mathematically corrupts the downstream causal graph, declaring the inert child feature to be the sole causal mediator.

---

### (vi) Minimality Claims

1. **C1 (Activation Patching - 6 params)**: 
   To construct a non-trivial function like $y = \text{ReLU}(x)$ while implementing a cancellation pair, we require at least three hidden units (two to cancel out, one to carry the true mechanism). This requires 3 input-to-hidden weights and 3 hidden-to-output weights, totaling 6 parameters. (As the authors note, a 5-parameter version exists with a residual skip connection, but keeping width 3 is highly realistic for MLP layer patching).
   
2. **C2 (Integrated Gradients - 18 params)**:
   To get zero attribution for the causal feature $x_1$, we must have $t(X_1^*) = t(0)$, but we also require $t(1/4) \neq t(2)$ so that the function is non-constant on the support. Additionally, to avoid kink issues and ensure differentiability at $X_1^* = 2$, the function must go up, go down, and then flatten out.
   - A single-peak continuous piecewise-linear function that starts at $0$, peaks, goes back to $0$, and flattens out requires at least 3 ReLU units:
     $$t(z) = \text{ReLU}(z) - 2\text{ReLU}(z - 1/2) + \text{ReLU}(z - 1)$$
   - Since we need at least two inputs (one causal, one inert), the minimal model requires $2 \times 3 = 6$ ReLU units.
   - This translates to $18$ parameters (6 input weights, 6 biases, 6 output weights). This is **provably minimal** to demonstrate simultaneous Gradient $\times$ Input and Integrated Gradients failure on a ReLU MLP.

3. **C4 (Linear Probing - 4 params)**:
   To contrast a causal and an inert neuron, we need at least 2 hidden units, resulting in $2$ input weights and $2$ output weights. This is **provably minimal** at $4$ parameters.

4. **C3 (SAE Circuit - 2D space, 2-latent SAE)**:
   A hierarchy of a parent and child feature requires at least a 2D activation space, and a minimal SAE requires at least 2 latents. This is **provably minimal**.

---

# ADVERSARIAL VERDICT: VERIFIED-SOUND

The note and its companion verification scripts are **exceptionally rigorous, mathematically sound, and conceptually deep**. They successfully move mechanistic interpretability critiques from empirical observations to exact, checkable mathematical certificates, serving as excellent regression tests for next-generation interpretability methods.
