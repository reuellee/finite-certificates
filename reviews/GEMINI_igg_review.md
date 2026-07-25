### Verdict: **VERIFIED-SOUND with a MINOR EXPOSITORY CORRECTION REQUIRED**

We find the core mathematical claims of the research note—including the adaptive coupling proof, the positive binary construction, and the swap-symmetric witness—to be **theoretically airtight, mathematically correct, and highly valuable** for clarifying the limits of mechanistic interpretability. 

However, we have identified a **critical expository error** in Section 4.3 regarding the structural identity between internal edits and semantic $do$-interventions, where the text completely inverts the "root" vs. "child" roles and misidentifies which SCM corresponds to the internal settings. Correcting this expository inversion is necessary for the paper to be mathematically coherent, though it does not compromise the validity of the numerical tables, the exact-fraction verifier, or the main theorem.

---

### 1. Rigorous Attack on the Residual Surface

#### (i) Airtightness of the Coupling Proof under Adaptive Protocols
The formalized protocol model and the coupling proof in Section 3 are **fully airtight** and represent a rigorous, elegant formulation.
*   **Handling of pre-intervention leakage:** Under an adaptive protocol where the adversary chooses interventions based on past observations, the reviewer’s concern is whether the pre-intervention activation $X$ of a new unit could leak upstream information through correlation with earlier draws. Under the stated assumption that **units are drawn i.i.d. from $\mu_M$**, there is *zero correlation* between the draws of different units. Therefore, the pre-intervention $X_t$ of a new unit $t$ carries no information about previous units' latent states.
*   **Mid-protocol interventions on the same unit:** If the protocol were to perform multiple rounds of interventions on the *same* unit, the coupling still holds. Since the unit's latent state $S$ and activation $X$ are drawn once at the start of its episode, they are identical across both models under the coupled probability space. Any adaptive decisions made *within* a unit's episode (e.g., "if $X_P = 1$, set $X_C = 0$") are handled by the Markov kernel $K_t( \cdot \mid x)$, which is applied to the same $x$ in both runs.
*   **Is the "i.i.d." assumption load-bearing?** Yes, it is highly load-bearing. If the units were not i.i.d. (e.g., if there were temporal correlation between consecutive units $S_t$ and $S_{t-1}$), the sequence of pre-intervention activations would carry transition information. If the transition laws differed between $M_1$ and $M_2$, the protocol could distinguish them observationally. If the sequence-level observational joint distribution were identical, we could still couple the entire sequence of $(S, X)$ pairs, and the proof would hold because there is **no feedback** from downstream interventions to the upstream generation process. Thus, the i.i.d. assumption is a mathematically clean, load-bearing constraint that guarantees sequence-level observational equivalence, ensuring the coupling remains airtight.

#### (ii) The 'Same Invertible Activation' Modeling Choice
*   **Does the invertible activation $X = (P, C)$ "smuggle" the conclusion?** No. On the contrary, this is an **exceptionally fair and powerful modeling choice** that strengthens the no-go result.
*   **Theoretical leverage:** By assuming that the representation $X = \phi(S)$ is perfectly invertible and lossless, the author grants the proponent of causal interpretability the *best-possible-case scenario* (perfect representation learning). Proving that causal identification is still impossible under these ideal conditions demonstrates that the "Intervention-Grounding Gap" is a fundamental causal limitation, not an artifact of noisy or lossy representations.
*   **Practitioner relevance:** If the representation were lossy, noisy, or suffered from superposition, the mapping from activations to concepts would be even more underdetermined. By isolating representation learning from causal inference, the note establishes a clear boundary: **representation identifiability is strictly weaker than semantic causal identifiability (Corollary 1)**. The note scopes this correctly and explicitly.

#### (iii) Verification of the Swap-Symmetric Witness
We have rigorously verified the arithmetic of the swap-symmetric witness in Section 4.5:
*   **Joint distribution:** $\Pr(0,0) = \Pr(1,1) = 3/8$, $\Pr(0,1) = \Pr(1,0) = 1/8$.
*   **Marginals:**
    $$\Pr(P=1) = \Pr(1,0) + \Pr(1,1) = 1/8 + 3/8 = 1/2$$
    $$\Pr(C=1) = \Pr(0,1) + \Pr(1,1) = 1/8 + 3/8 = 1/2$$
    Both $P$ and $C$ are marginally Bernoulli(1/2).
*   **Forward model ($M_{P \to C}$):**
    $$\Pr(C=1 \mid P=0) = \frac{\Pr(0,1)}{\Pr(P=0)} = \frac{1/8}{1/2} = 1/4$$
    $$\Pr(C=1 \mid P=1) = \frac{\Pr(1,1)}{\Pr(P=1)} = \frac{3/8}{1/2} = 3/4$$
*   **Reverse model ($M_{C \to P}$):**
    $$\Pr(P=1 \mid C=0) = \frac{\Pr(1,0)}{\Pr(C=0)} = \frac{1/8}{1/2} = 1/4$$
    $$\Pr(P=1 \mid C=1) = \frac{\Pr(1,1)}{\Pr(C=1)} = \frac{3/8}{1/2} = 3/4$$
    The two SCMs are indeed exact, symmetric mirror images. Any swap-equivariant selection rule must assign them identical scores, defeating any canonical direction-selection convention.
*   **Do-gap:**
    *   Under $M_{P \to C}$ ($P$ is root), $do(P=0)$ sets $P=0$ and yields $C \sim \Pr(C \mid P=0)$, so $\Pr(C=1 \mid do(P=0)) = 1/4$.
    *   Under $M_{C \to P}$ ($P$ is child), $do(P=0)$ sets $P=0$ but leaves the root $C$ at its marginal, so $\Pr(C=1 \mid do(P=0)) = \Pr(C=1) = 1/2$.
    The do-gap is indeed $1/4$ vs. $1/2$ (a difference of $1/4$), which is mathematically correct.

#### (iv) Prior-Art Positioning
The note's positioning relative to Geiger et al. (2023, 2025) and Sutter et al. (2025, arXiv:2507.08802) is **highly accurate and theoretically distinct**:
*   **Geiger et al. (Causal Abstraction):** Validates consistency between a network and a hypothesized causal model but does not address the *uniqueness* of the abstracted model under a given observational and interventional transcript.
*   **Sutter et al. (2025):** Focuses on the *complexity of the alignment map* as the lever. They show that if the alignment map is unrestricted and non-linear, any network can abstract any algorithm (making the framework vacuous). This shows that mapping flexibility destroys grounding.
*   **This Note:** Uses an **orthogonal lever**. It fixes the alignment map to be completely rigid, invertible, and perfectly anchored ($X = (P, C)$ with identity alignment). It shows that *even with zero freedom in the map*, we still cannot identify the upstream SCM factorization because downstream/post-representation interventions are descendants and cannot perform surgery on the upstream SCM.
These two results beautifully bracket the grounding problem from opposite sides: Sutter et al. show that map flexibility prevents grounding of the map; this note shows that even a perfectly grounded map cannot ground the upstream causal direction. This is a very clean and defensible contribution.

#### (v) Practical Import: Structural Identity Error in Section 4.3
The note states in Section 4.3:
> *"In fact the pattern is exact and structural: the internal edit set(X_P=p) coincides with do(P=p) in the model where P is a root, namely M_(C->P), and set(X_C=c) coincides with do(C=c) in M_(P->C)."*

This sentence contains **two severe, overlapping mathematical and conceptual errors**:
1.  **Mislabeling of Roots:**
    *   In $M_{P \to C}$ ($P \to C$), $P$ is the root and $C$ is the child.
    *   In $M_{C \to P}$ ($C \to P$), $C$ is the root and $P$ is the child.
    Therefore, the model where $P$ is the root is $M_{P \to C}$, NOT $M_{C \to P}$.
2.  **Inverted Structural Identity:**
    *   Let's check `set(X_P=p)`: this internal setting replaces the $P$-coordinate with $p$, but leaves the $C$-coordinate distributed according to its observational marginal $\Pr(C)$.
    *   In $M_{P \to C}$ (where $P$ is root), $do(P=p)$ sets $P=p$, and $C$ is regenerated from its conditional distribution $\Pr(C \mid P=p)$. Since $P$ and $C$ are dependent, the conditional $\Pr(C \mid P=p)$ is not equal to the marginal $\Pr(C)$. Thus, `set(X_P=p)` does **not** coincide with $do(P=p)$ in $M_{P \to C}$.
    *   In $M_{C \to P}$ (where $P$ is child), $do(P=p)$ sets $P=p$. Since $C$ is the root, its distribution is unaffected by the intervention on its descendant $P$, so $C$ remains distributed according to its root marginal $\Pr(C)$.
    *   Thus, the distribution under $do(P=p)$ in $M_{C \to P}$ consists of $P=p$ and $C \sim \Pr(C)$, which is **exactly** identical to the internal edit `set(X_P=p)`!
    
Consequently, the internal edit `set(X_P=p)` coincides with $do(P=p)$ in the model where $P$ is a **child** (namely $M_{C \to P}$), and `set(X_C=c)` coincides with $do(C=c)$ in the model where $C$ is a **child** (namely $M_{P \to C}$).

The text in Section 4.3 has completely inverted this relationship, claiming that `set(X_P=p)` matches $do(P=p)$ where $P$ is the root, and associating that root with $M_{C \to P}$. 

---

### 2. Required Correction

To make Section 4.3 mathematically coherent and aligned with the SCM definitions in Section 4.2 and the numerical values in Table 2, the sentence must be rewritten as:

> *"In fact the pattern is exact and structural: the internal edit set(X_P=p) coincides with do(P=p) in the model where P is a child (so that intervening on P does not affect its parent root C), namely M_(C->P), and set(X_C=c) coincides with do(C=c) in the model where C is a child, namely M_(P->C)."*

With this correction, the author's broader point—that every internal experiment is consistent with *some* ontology (just not a unique one)—remains perfectly intact and is structurally clarified: `set(X_P=p)` is consistent with the ontology $C \to P$ where $P$ is the child, and `set(X_C=c)` is consistent with the ontology $P \to C$ where $C$ is the child.
