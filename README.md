# finite-certificates

Small, explicit, machine-checkable research results ("finite certificates"), produced
2026-07-25 by an autonomous multi-agent research session (Claude Fable 5 agents;
adversarial review by Gemini 2.5 Pro). Every claim ships with a standalone verifier in
exact arithmetic. **Requirements: python3 + numpy + sympy only.**

## Verify everything

```
python3 run_all.py            # runs every verify_*.py; nonzero exit if any fails
python3 run_all.py --fast     # skips the two slow verifiers (~10 min total otherwise)
```

## Contents

### jacobian/ — aftermath of the Jacobian Conjecture counterexample (Alpöge, 2026-07-20)

Reference: `alpoge_jacobian.pdf` (verification preprint; the original map F, deg (7,6,4),
det Jac ≡ −2, generic degree 3). `verify_original.py` re-verifies it in seconds.

- `n2_analysis.md` + `verify_n2.py` — **no Keller map of generic degree 2 exists in any
  dimension** (short proof; quadratic case of Campbell 1973 — no priority claimed), so
  generic degree 3 is minimal and any n=2 counterexample needs generic degree ≥ 5 and
  total degree > 100 (with Orevkov, Domrina–Orevkov, Moh). Also: y-linear Keller maps in
  n=2 are automorphisms (mechanism no-go), and degree-4 Keller maps have Galois closure
  S₄ or A₄. Gemini review: VERIFIED-SOUND (`reviews/GEMINI_n2_review.md`).
- Explicit fallout witnesses derived constructively from F (write-up pending — the
  scripts and their printed statements are the current claims; see `FALLOUT_STATUS.md`):
  - `verify_dixmier_poisson.py` — explicit polynomial endomorphism of C⁶ preserving the
    standard symplectic Poisson bracket, det Jac ≡ 1, with **three distinct points
    sharing one image** (so: bracket-preserving, not injective, not an automorphism).
  - `deg3_map.py` + `verify_deg3_keller.py` — explicit **degree-3** Keller
    non-automorphism (Bass–Connell–Wright/Yagzhev reduction made explicit).
  - `cubic_map.py` + `verify_cubic_homogeneous.py` — explicit cubic-homogeneous-plus-
    identity Keller non-automorphism in dimension 55, nilpotent Jacobian part.
  - `druzkowski_map.py` + `verify_druzkowski.py` — explicit **Drużkowski-form**
    (x_i + (Ax)_i³) counterexample.

### ai/optimizer/ — convergence-theory counterexamples (Gemini: VERIFIED-SOUND)

`optimizer_counterexamples.md` + `verify_muon_ns.py`, `verify_lion.py`:
deployed-coefficient Muon falsifies the coverage claim of arXiv:2601.19156 (exact
one-step certificate + continuity obstruction: no orbit orthogonalizes for any number of
NS steps); an explicit family where 5-step Newton–Schulz has polar error > 0.9999 for
both coefficient sets; a vacuous stepsize condition in arXiv:2502.02900 Thm 3.1 for all
β ≥ 1/2; an exact period-2 cycle for default constant-hyperparameter Lion (contradicts
the informal claim only — the annealed theorems stand; scoping in the note).

### ai/interp-illusions/ — exact minimal interpretability-illusion networks (Gemini: VERIFIED-SOUND)

`certificates.md` + four verifiers: 6-param net where activation-patching variants
disagree and rank a provably inert component above the causal one; 18-param net where
gradient×input and Integrated Gradients put exactly zero attribution on the sole causal
feature; loss-optimal absorbed SAE whose sparse-feature-circuit is the causally inert
child latent (exact KKT); 4-param probing certificate that passes the Hewitt–Liang
control-task defense while probing a causally inert neuron.

### ai/maxout/ — smallest open case of a 2025 Sturmfels-et-al conjecture, resolved

`attack_maxout66.md` + `verify_maxout66_d4n4.py` (+ `cert_d4n4.json`): explicit
32-vertex exact-rational certificate **confirming achievability in the smallest open
case (d,n)=(4,4) of Conjecture 6.6(2)** of Balakin–Cox–Loho–Sturmfels, *Maxout
Polytopes* (arXiv:2509.21286), where the paper had no computational evidence for d ≥ 4.
`target_list.md` is the ranked harvest of further attackable ML-theory conjectures.

### reviews/ — adversarial reviews (Gemini 2.5 Pro via gemx)

One review per result set. A fifth result (SAE ρ-unidentifiability certificate, in the
sae-identifiability repo) received a BLOCKING review and is excluded pending revision.

## Provenance

Each result was produced by a Fable agent, independently re-verified by the
orchestrator (all verifiers re-run from scratch), then adversarially reviewed by
Gemini 2.5 Pro. Reviews that returned MINOR issues were applied before import;
BLOCKING results are excluded. The Jacobian-fallout scripts passed verification but
their prose write-up was interrupted (session limit); claims there are scoped to
exactly what the scripts print.
