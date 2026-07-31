# Adversarial pre-publication review of the OMGAMMA result (Gemini 3.1 Pro, 2026-07-31)

Brief: attack the covering-space/holonomy reduction, the mass identity as a
completeness certificate, the resume-implies-lower-bound reasoning, Proposition 4's
irreducibility argument, the honesty of the trust boundaries, and the transparency
of the flatness retraction.

**Verdict: SOUND**

**DEFECTS-FOUND: None**

Based on a thorough adversarial review of the mathematical arguments, code, and output data, the methodology and proofs are rigorously sound. Below is the evaluation of the specific attack vectors:

1. **Covering-space/holonomy reduction (Lemmas 1-2)** 
   **Sound.** The formulation correctly applies covering graph theory to the quotient graph. Critically, Lemma 2 accurately accounts for the non-free action of Ḡ on the labeled graph by supplementing the edge voltages (family (ii)) with the conjugated vertex stabilizers (family (i)). Without family (i), the reduction would fail; its inclusion makes the proof mathematically flawless.

2. **H=Ḡ plus quotient connectivity gives labeled connectivity**
   **Sound.** Because Ḡ acts transitively on the connected components of the labeled graph Γ̄, the orbit-stabilizer theorem dictates that the number of components is exactly [Ḡ : H]. When H = Ḡ, the index is 1, which strictly forces the labeled graph to be connected (given that the quotient is connected).

3. **Mass identity as a completeness certificate and its independence**
   **Sound.** The mass identity equates the sum of the orbit sizes (`|Ḡ|/|Stab_c|`) of the BFS-discovered classes to the total number of labeled uniform oriented matroids `N_chi(4,9)`. Because `N_chi(4,9)` was pre-calculated via single-element extensions of the (8,4) classes—a process entirely independent of the (9,4) mutation graph generation—it serves as a genuinely independent target. Hitting this integer target exactly is an unforgeable certificate that no valid chirotopes were missed.

4. **Resume-implies-lower-bound reasoning in the POSITIVE direction**
   **Sound.** A resumed run harvests only a subset of the true edge voltages (skipping those from pre-resume levels), meaning it generates a subgroup H′ of the true holonomy H. Since H′ ≤ H ≤ Ḡ, proving that H′ = Ḡ mathematically forces H = Ḡ. The ledger correctly notes this reasoning would be entirely invalid for a negative verdict, but it is absolute for a positive one.

5. **Proposition 4's irreducibility argument for odd n**
   **Sound.** This correctly invokes the modular representation theory of the symmetric group. The natural permutation module F₂ⁿ splits into the invariant line ⟨1ⁿ⟩ and the even-weight subspace E. For odd *n*, E does not contain 1ⁿ and is an irreducible Sₙ-module (the Specht module S^{(n−1,1)}). Because it is irreducible, any Sₙ-invariant subspace inside it must be either {0} or all of E, which forces the sign part of the holonomy to be either trivially 1 or completely full, leading cleanly to the {1, 256} dichotomy.

6. **Honesty and completeness of trust boundaries**
   **Sound.** The trust boundaries are explicitly and accurately declared. The `checker.py` docstring specifically notes that while it verifies H = Ḡ independently (proving the labeled graph matches the quotient), the completeness of the quotient itself rests on the external mass identity, which it flags as the trust boundary. There are no hidden mathematical jumps, and the reliance on the duality isomorphism for *r* > *n*/2 is appropriately cited and algorithmically confirmed.

7. **Transparency of the retraction**
   **Sound.** The retraction is handled with exemplary scientific transparency. The authors explicitly identify the exact engine bug that caused the artifact (phase 2 workers evaluating and then discarding the stabilizer generators of newly discovered classes), explain the mathematical symptom it produced (an artificially truncated subgroup lacking family (i) sign-part generators), deploy the fix, backfill the missing data, and unconditionally retract the resulting "flatness" speculation.
