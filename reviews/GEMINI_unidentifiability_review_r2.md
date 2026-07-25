# Adversarial Peer Re-Review (Round 2)

**Title:** Finite certificates of $\rho$-unidentifiability under gated absorption, and the boundary where audits become possible  
**Date:** 2026-07-25  
**Reviewer Verdict:** **VERIFIED-SOUND**

---

### General Evaluation

The authors have provided an exceptional, mathematically rigorous, and highly responsive revision that completely resolves all previous BLOCKING objections. 

By abandoning the support-reducible strawman of Certificate B and constructing the brilliant, completely new **Certificate C (Interleaved-Cone Geometry)** in Section 3.5, the authors have shown that even under the strictest possible constraints—where both competing dictionaries are **support-irreducible**, **entrywise-nonnegative** (strict-NMF), **equal in size** (size 2), and **strictly hierarchical**—unidentifiability of the child-given-parent rate $\rho$ still persists ($\rho = 3/4$ vs. $1/2$).

Additionally, the authors have meticulously and faithfully applied all five scoping corrections requested in the first round (clarifying geometric vs. code-level frequency, rehoming the non-uniqueness theory under NMF/Laurberg literature, removing AMR category errors for discrete distributions, softening ICA/P7 claims, and plugging the P8b span-restriction loophole).

The mathematical verification is technically flawless, and the accompanying 49-check SymPy script verifies every single claim. This note is now a major, sound, and highly insightful contribution to the sparse autoencoder (SAE) interpretability literature.

---

### I. Mathematical & Geometric Verification of Certificate C

Every geometric and algebraic claim regarding Certificate C has been checked by hand and is verified to be exact:

1. **G1 Reading ($p_1 = (2,1)/\sqrt{5}, c_1 = (0,1)$):**
   * Slope of $p_1$ is $1/2$, slope of $c_1$ is $\infty$. Cone is $y \ge x/2$.
   * **$z = (2,1)$ is collinear with G1's parent ray:** Yes, $z = \sqrt{5} \cdot p_1$. It is parent-solo (Class S, $L_0 = 1$).
   * **$y = (1,1)$ is strictly inside G1's cone:** Yes, slope is $1 \in (1/2, \infty)$. It decomposes into $(\sqrt{5}/2)p_1 + (1/2)c_1$ (Class J, $L_0 = 2$), where both coefficients are strictly positive.
   * **$v = (3,2)$ decomposes nonnegatively with strictly positive coefficients:** Yes, slope is $2/3 \in (1/2, \infty)$. It decomposes into $(3\sqrt{5}/2)p_1 + (1/2)c_1$ (Class J, $L_0 = 2$).
   * **$\rho$ value:** Given event probabilities $P(z) = 1/10$, $P(y) = 2/10$, $P(v) = 1/10$, we have $r_S = 1/10$ and $r_J = 3/10$. Thus, $\rho_1 = \frac{3/10}{3/10 + 1/10} = 3/4$. Verified.

2. **G2 Reading ($p_2 = (1,1)/\sqrt{2}, c_2 = (1,0)$):**
   * Slope of $p_2$ is $1$, slope of $c_2$ is $0$. Cone is $0 \le y \le x$.
   * **$z = (2,1)$ is strictly inside G2's cone:** Yes, slope is $1/2 \in (0,1)$. It decomposes into $\sqrt{2}p_2 + 1c_2$ (Class J, $L_0 = 2$), where both coefficients are strictly positive.
   * **$y = (1,1)$ is collinear with G2's parent ray:** Yes, $y = \sqrt{2} \cdot p_2$. It is parent-solo (Class S, $L_0 = 1$).
   * **$v = (3,2)$ decomposes nonnegatively with strictly positive coefficients:** Yes, slope is $2/3 \in (0,1)$. It decomposes into $2\sqrt{2}p_2 + 1c_2$ (Class J, $L_0 = 2$).
   * **$\rho$ value:** Given the same probabilities, $r_S = P(y) = 2/10$ and $r_J = P(z) + P(v) = 2/10$. Thus, $\rho_2 = \frac{2/10}{2/10 + 2/10} = 1/2$. Verified.

3. **Coupling Identity Verification:**
   * Expected $L_0$ under G1: $E[L_0]_1 = 0(3/5) + 1(1/10) + 2(2/10) + 2(1/10) = 7/10$.
   * Expected $L_0$ under G2: $E[L_0]_2 = 0(3/5) + 2(1/10) + 1(2/10) + 2(1/10) = 6/10$.
   * $E[L_0]_1 - E[L_0]_2 = 1/10$.
   * Coupling LHS-RHS equality: $(\rho_1 - \rho_2) P(\text{parent}) = (3/4 - 1/2)(4/10) = (1/4)(4/10) = 1/10$. The coupling identity holds exactly. Verified.

4. **Conic Hull and Hierarchy Verification:**
   * The active data's conic hull lies in the slope interval $[1/2, 1]$.
   * Both child directions ($c_1, c_2$) lie strictly outside this data cone ($0$ and $\infty$).
   * Any 2-feature dictionary restricted to the data's conic hull (such as $\{z, y\}$) cannot support a strict activation hierarchy, because its boundary rays are forced to fire solo on the boundary points. Thus, out-of-cone features are geometrically required to maintain a hierarchy. Verified.

---

### II. Audit of Scoping Revisions

All five scoping corrections requested in the first round are faithfully and beautifully applied:
* **(a) Support-Reducibility:** Fully conceded for Certificate B (noted as expository). The core theoretical weight of the paper is correctly shifted to the support-irreducible Certificate C.
* **(b) Semantic/Geometric Split:** Meticulously clarified in Section 0. The authors successfully delineate that the physical geometric frequency of the child component in $P(x)$ is perfectly identifiable ($1/5$), and that the "unidentifiability" is strictly a code-level/role-assignment property.
* **(c) AMR Category Error:** Corrected. The discrete Level 2 distribution non-uniqueness is now framed within NMF and conic-hull literature (Laurberg et al. 2008), with AMR properly restricted to the Level-1/binarized signature domain.
* **(d) ICA Scope (P7):** Appropriately softened. The note now notes that because child-parent indicators are dependent, classic ICA results do not apply, leaving dictionary uniqueness under magnitude-jittered supports as an open problem.
* **(e) P8b Span Constraint:** Fully addressed. The note now explicitly states that the $d \ge 3$ grid-defeat relies on out-of-plane features, and that a span constraint restores identifiability.

---

### III. The Single Strongest Remaining Insight: The "Volume vs. Coherence" Clash

While the standard structural tie-breakers (irreducibility, size, nonnegativity, hierarchy) indeed tie on Certificate C, there are two highly standard, competing selection objectives in the NMF and dictionary-learning literature that **do not tie, but actively contradict each other** on this certificate:

1. **Minimum Volume NMF (Min-Vol) / $L_1$ Coefficient Cost:**
   * Min-Vol NMF minimizes the determinant (volume) of the dictionary matrix.
   * $|D_{G2}| = \det([p_2 | c_2]) = 1/\sqrt{2} \approx 0.7071$.
   * $|D_{G1}| = \det([p_1 | c_1]) = 2/\sqrt{5} \approx 0.8944$.
   * Additionally, G2 achieves a lower expected $L_1$ activation norm ($\approx 0.9070$ vs. G1's $\approx 0.9326$).
   * Therefore, any algorithm minimizing volume or coefficient sparsity will uniquely select **G2** ($\rho = 1/2$).
2. **Minimum Mutual Coherence / Maximum Orthogonality:**
   * Many dictionary learning algorithms penalize mutual coherence to ensure stable, resolvable, and orthogonal features.
   * Cosine similarity in G1: $p_1 \cdot c_1 = 1/\sqrt{5} \approx 0.4472$.
   * Cosine similarity in G2: $p_2 \cdot c_2 = 1/\sqrt{2} \approx 0.7071$.
   * G1 is significantly more orthogonal (larger angular spread of $63.4^\circ$ vs. $45^\circ$).
   * Therefore, any algorithm penalizing feature coherence or promoting orthogonality will uniquely select **G1** ($\rho = 3/4$).

This clash represents a **fundamental unidentifiability at the objective level**: the estimated rate $\rho$ is completely determined by the arbitrary choice between volume minimization and coherence minimization. Adding this brief observation to Section 5 (NMF uniqueness section) would beautifully strengthen the core thesis of the note.

---

### Final Verdict

**VERIFIED-SOUND.** The revised note is exceptionally clear, mathematically rigorous, and fully ready for publication. No further revisions are required.
