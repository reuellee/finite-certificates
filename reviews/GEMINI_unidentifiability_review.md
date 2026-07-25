# Adversarial Peer Review

**Title:** Finite certificates of $\rho$-unidentifiability under gated absorption, and the boundary where audits become possible  
**Date:** 2026-07-25  
**Reviewer Verdict:** **BLOCKING (Major Revisions Required)**

---

### General Evaluation

While the exact arithmetic of the companion SymPy script (`theory/verify_unidentifiability.py`) is technically flawless and all 31 computational checks pass, the note's **non-computational logic, framing, and theoretical positioning are fundamentally flawed**. 

The claim that "absorbed child frequency is unidentifiable label-free is settled" is an artifact of:
1. Allowing **support-reducible (redundant) dictionaries** as equal competitors to irreducible ones.
2. A **semantic contradiction** in how feature activations are counted versus their physical reconstructions.
3. A **category error** in positioning the results against mixture-model identifiability (AMR).
4. A **severe scoping error** in citing classic ICA results (Comon 1994) to claim restoration of identifiability for highly dependent activations.
5. An **artificial coordinate-space loophole** in the $d \ge 3$ magnitude grid defeat (P8b).

These points must be rigorously addressed before this note can be considered a sound addition to the sparse autoencoder (SAE) interpretability literature.

---

### Detailed Findings & Attacks

#### (a) The Ill-Posedness Framing & Support-Reducibility (The Minimality Strawman)
The note claims that the "minimality of the true process" is defeated (P5/P5b) because expected $L_0$ and dictionary-size minimality "disagree" on Certificate B ($G_1$ has dictionary size $2$ and $E[L_0] = 0.7$, while $G_2$ has dictionary size $3$ and $E[L_0] = 0.6$). This argument is a strawman:
* **The Expected $L_0$ Fallacy:** In sparse coding and dictionary learning, $E[L_0]$ is *never* minimized without a hard constraint or penalty on the dictionary size $K$. If it were, the trivial dictionary $D = X$ (using the observed atoms themselves as features) would always be preferred because it achieves $E[L_0] = 1.0$ (or lower with background).
* **Support-Reducibility:** In the Non-negative Matrix Factorization (NMF) and dictionary-learning literature, a dictionary $D$ is called **support-reducible** if there exists a proper subset of columns $D' \subset D$ that can non-negatively reconstruct 100% of the data points in the support.
  * In Certificate B, $D_{G2} = \{v_p, v_c, u\}$ is support-reducible because the subset $D_{G1} = \{v_p, v_c\}$ can reconstruct all observed atoms ($0$, $v_p$, $v_p+v_c$, $v_p+2v_c$).
  * $D_{G1}$ is support-irreducible. 
  * In any standard formulation of dictionary learning, support-reducible dictionaries are canonically rejected because the extra column $u$ is completely redundant (it lies in the conical hull of $\{v_p, v_c\}$). 

By restricting the hypothesis class to **support-irreducible dictionaries**, $G_1$ is uniquely preferred, and $\rho = 2/5$ is perfectly identifiable. The claimed "unidentifiability" is therefore artificial—it relies on admitting redundant dictionaries as valid candidates.

#### (b) The Latent Hierarchy Contradiction & Semantic Play
The note claims that in Certificate B, "both readings [are] genuinely hierarchical." This claim fails upon inspecting the activation structures:
* **The Activation Hierarchy Violation:** Under a true parent-child hierarchy in the latent code space, a child-related feature should only fire when the parent feature is active. In $G_2$, however, the composite feature $u$ (which reconstructs parent + child) fires **solo** with probability $1/10$ (Class $U$), during which the parent feature $v_p$ and child feature $v_c$ are both silent ($z_p = 0, z_c = 0$). Thus, in activation space, $G_2$ is **not** hierarchical—it is a mixture of a solo parent, a solo composite, and a joint event.
* **Physical vs. Nominal Frequency:** In both $G_1$ and $G_2$, the physical input distribution $P(x)$ is identical. The "child concept" (geometrically defined as projection onto the $v_c$ axis) occurs with a frequency of exactly $1/5$ in both processes ($1/10$ at magnitude 1, and $1/10$ at magnitude 2). The different child rate ($\rho = 1/4$ in $G_2$) is a purely nominal artifact of how we label activations. Geometrically, when $u$ fires, the child direction $v_c$ is reconstructed. Declaring that "no child is involved" in Class $U$ is a semantic game that ignores the geometric reconstruction $D z$.

#### (c) Category Error on AMR (Allman-Matias-Rhodes) Positioning
The note claims that the certificates "live on AMR's measure-zero set." This is a category error:
* AMR (2009) establishes the identifiability of finite mixture models where emission distributions are continuous or defined over finite state spaces, and the mixture components are unknown.
* In the Level 2 certificates, the input distribution $P(x)$ is a **discrete distribution** (a finite set of Dirac deltas). A discrete distribution is trivially, 100% identifiable from data—we know its exact atoms and their probabilities.
* The unidentifiability here is not a mixture-model estimation problem, but rather the **non-uniqueness of NMF/sparse-coding** when mapping a known $P(x)$ to a dictionary $D$ and codes $z$. AMR is completely silent on this dictionary-level ambiguity.

#### (d) Scoping Error on ICA & P7
The note argues that P7 (independent per-feature magnitude jitter) restores identifiability, citing ICA results (Comon 1994):
* Classic ICA (Comon 1994) strictly assumes that the source activations are **mutually independent**.
* In a hierarchical parent/child process, the parent and child activations are **highly dependent** by definition (the child's activation indicator is a subset of the parent's support).
* Since the independence assumption is explicitly violated, Comon's results cannot be used to guarantee the identifiability of the dictionary. While independent jitter creates a 2D dispersion that rules out a 1-D reified ray, the claim that it uniquely identifies the entire dictionary up to permutation is mathematically unproven for dependent/hierarchical activation supports.

#### (e) Artificial Coordinate-Space Loophole in P8b
The defeat of the unit magnitude grid in $d \ge 3$ (P8b) relies on an out-of-plane cancellation pair:
$$w_{1,2} = \left(\frac{1}{2}, \frac{1}{2}, \pm\frac{1}{\sqrt{2}}\right)$$
* These vectors have non-zero components along the 3rd dimension, whereas the dataset has zero variance in the 3rd dimension (its span is exactly the $z=0$ plane).
* In machine learning and NMF, it is standard to restrict dictionary features to the linear span of the data. If we require that dictionary features lie in the column space of the data, then $w_1$ and $w_2$ are rejected, plugging this loophole and restoring identifiability in $d \ge 3$.

---

### Required Revisions

1. **Retract the Claim of "Sparsity Prior Failure" (P5):** Re-evaluate $G_1$ and $G_2$ under a joint optimization objective (e.g., MDL, BIC, or NMF uniqueness conditions) that penalizes dictionary size and enforces support-irreducibility. Acknowledge that $G_1$ is the canonically preferred dictionary.
2. **Clarify the Semantic/Geometric Split:** Explicitly state that the physical frequency of the child concept in $P(x)$ is perfectly identifiable (exactly $1/5$), and that the "unidentifiability" of $\rho$ is a purely representation-dependent naming convention.
3. **Remove the AMR Reference:** Remove references to AMR (2009) as it represents a category error for discrete dictionary learning. Frame the non-uniqueness instead within the classic NMF / conic-hull literature (e.g., Laurberg et al. 2008).
4. **Scope the ICA Claims Properly:** Soften the claims around P7. Explicitly state that standard ICA theorems do not apply due to the dependence of the activation indicators, and that proving dictionary uniqueness under hierarchical activation supports with independent magnitude jitter remains an open theoretical problem.
5. **Acknowledge the Span Constraint in P8b:** Add a caveat to P8b noting that the magnitude-grid defeat is prevented if the dictionary is restricted to the linear span of the data.
