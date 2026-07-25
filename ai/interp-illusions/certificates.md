# Interpretability illusions as finite certificates

Minimal explicit counterexample networks for the main causal-interpretability
methods. Each certificate is a tuple **(exact weights, finite input
distribution, registered method procedure, exact method output, proof of the
true mechanism, mismatch statement)**, machine-verified in exact arithmetic
(`fractions.Fraction` / sympy radicals — no floats in any load-bearing claim)
by the `verify_*.py` script named in each section. Every script prints the
method's output next to the ground truth, checks the mismatch, and exits
nonzero if any exact claim fails. Environment: python3 + numpy 1.24.2 +
sympy 1.11.1 only.

**Why these matter.** Patching, attribution, SAE circuits, and probes are being
used to audit safety-relevant claims about models. These certificates are the
smallest networks we could construct on which the *standard* procedure provably
returns the wrong answer; they calibrate trust ("the method can fail even at 6
parameters, in this specific way") and serve as regression tests: an improved
method should pass them.

**Registration discipline (no strawmen).** Each certificate names the exact
method variant from the literature and follows its published procedure. The
distributions are finite but non-degenerate: every input is in-distribution for
the method's own protocol (clean/corrupt pairs from the task distribution,
default IG baseline, probes trained to convergence with control tasks). Known
practitioner objections are stated and answered per certificate.

---

## Prior-art table

| Method / illusion | Known in literature | Status there | Our contribution |
|---|---|---|---|
| Subspace patching activates dormant pathways | Makelov, Lange, Geiger, Nanda 2023 (arXiv:2311.17030, NeurIPS); reply: Wu et al. arXiv:2401.12631 | Empirical on GPT-2 IOI/factual recall + qualitative theory; contested interpretation | Different target: we certify *single-site full-component* patching (their illusion is specifically about learned subspaces; full-component patching was their "safe" baseline). Exact, 6 parameters. |
| Single neurons look interpretable but aren't | Bolukbasi et al. 2021 "An Interpretability Illusion for BERT" (arXiv:2104.07143) | Empirical (dataset-conditional patterns in BERT) | Not our target directly; our probing cert (C4) is the exact-minimal analogue of "looks like it encodes, doesn't cause". |
| Simplified/proxy models faithful on-distribution, wrong OOD | Friedman, Lampinen, Dyer et al. 2023 "Interpretability Illusions in the Generalization of Simplified Models" (arXiv:2312.03656) | Empirical (Transformer SVD/cluster simplifications, Dyck/code tasks) | Same *genus* (on-distribution agreement hides mechanism mismatch) but we give exact finite certificates for specific causal methods, not simplification pipelines. |
| Backup/redundant heads distort patching; negative heads exist | Wang et al. 2023 (IOI, arXiv:2211.00593); McGrath et al. 2023 "Hydra effect" | Empirical in GPT-2/LLMs | **C1**: exact minimal (6-param) certificate that the negative-pair motif breaks all three standard patching variants at once, with provable ground truth and an exact unfaithfulness proof for the discovered circuit. |
| Patching best-practice caveats (denoising vs noising disagree, metric choice) | Zhang & Nanda 2023 (arXiv:2309.16042, ICLR 2024); Heimersheim & Nanda 2024 (arXiv:2404.15255) | Empirical guidance, no minimal certificates | **C1** makes the denoising/noising disagreement an exact theorem on a named network. |
| Gradient saturation makes grad×input miss causal features | Shrikumar et al. 2017 (DeepLIFT motivation); Sundararajan et al. 2017 §2 | Motivating examples (some exact but single-feature; no inert-feature contrast) | **C2(a)**: one exact network where grad×input is 0 on the causal feature **and simultaneously nonzero on a provably inert feature**, on the entire certified half of the support. |
| IG baseline dependence / attribution impossibility | Sundararajan et al. 2017 (baseline discussion); Bilodeau et al. 2024 PNAS "Impossibility theorems for feature attribution" | Abstract impossibility theorems (existence proofs, large function classes) | **C2(b)**: a concrete 18-parameter ReLU net + input where IG with its default baseline outputs exactly (0 on causal, all mass on inert) while satisfying completeness — a *checkable instance*, not an existence claim. |
| SAE feature absorption | Chanin et al. 2024 "A is for Absorption" (arXiv:2409.14507); sae-identifiability repo (eps* theory, `theory/verify_absorption_theory.py`) | Empirical in LLM SAEs; exact loss-side theory (when absorption is optimal) in the repo | **C3**: pushes the exact loss-side result through to the *circuit level*: the loss-optimal SAE + the registered sparse-feature-circuits procedure provably outputs "child latent causes y" while the child feature is causally inert. New (circuit-level) exact statement. |
| Probing ≠ causation | Belinkov 2022 survey; Hewitt & Liang 2019 (control tasks); Elazar et al. 2021 (amnesic probing); Ravichander et al. 2021 | Conceptual point + empirical demonstrations | **C4**: exact minimal certificate in which the probe *passes the control-task defense* (selectivity 1/8 > 0, computed by exact enumeration) and weight-ranking places the inert neuron first — the full registered pipeline fails, not just naive accuracy. |

Summary: C1 and C2 are, to our knowledge, the first *exact minimal certificate*
formulations of these failure modes (the phenomena are known empirically /
abstractly); C3 is a new exact circuit-level statement built on the repo's
absorption theory; C4 is a formalization of a known conceptual point, made
sharp by including the control-task defense inside the certificate.

---

## Certificate 1 — Activation patching (single-site; denoising, noising, zero/mean ablation)

**Script:** `verify_activation_patching.py` · **Network:** 6 parameters, 1
hidden layer, width 3, 1 input.

**Weights (exact).** `h = (x, −x, x)` (patchable sites h1,h2,h3);
`y = ReLU(h1 + h2 + h3) = ReLU(x)`.

**Distribution.** x uniform on {+1, −1}; behavior y\*(x) = ReLU(x). Clean/corrupt
pair (+1, −1) — both in the task distribution, the canonical counterfactual
pair for a binary task.

**Registered procedure.** Single-site activation patching exactly as in Meng
et al. 2022 (causal tracing, denoising), Zhang & Nanda 2023, Heimersheim &
Nanda 2024: denoising recovery `R_i = (y_patch − y_corr)/(y_clean − y_corr)`;
noising effect `E_i = (y_clean − y_patch)/(y_clean − y_corr)`; zero-ablation
importance `|y_clean − y_ablated|` (here zero = exact mean over D, so
mean-ablation coincides). Circuit selection by thresholding (ACDC-style,
Conmy et al. 2023).

**Method output (exact).**
- Denoising: R = (1, 0, 1) — h1 gets **full recovery**, tied with h3.
- Noising: |E| = (1, 2, 1) — h2 ranked **strictly above** the true mechanism.
- Zero/mean-ablation: (1, 1, 1) — all sites "equally critical".

**True mechanism (proof).** The summed readout path weight of {h1, h2} is
1·1 + 1·(−1) = 0, so their joint contribution is identically zero *for every
real input*, not just on D. Deleting the pair leaves the function exactly
ReLU(h3) = ReLU(x) on all of ℝ; deleting h3 gives the constant 0. The unique
minimal faithful circuit is {h3}.

**Mismatch statement.** On distribution D with the registered clean/corrupt
pair, denoising patching returns ranking h1 ≈ h3 ≫ h2, noising returns
h2 ≫ h1 ≈ h3, ablation returns a three-way tie — three standard variants,
three different verdicts, all wrong: the pair {h1,h2} is a removable null
subcircuit. The denoising-discovered circuit {h1,h3} is moreover *unfaithful*
in the method's own sense: run with h2 mean-ablated it outputs 2 ≠ 1 on the
clean input.

**Objections & answers.** *"A cancellation pair is adversarial."* It is the
minimal form of the negative-head / backup-head motif documented in real
models (negative name-movers, Wang et al. 2023; Hydra effect, McGrath et al.
2023); a method deployed for auditing must handle it. *"Patch pairs/sweep
groups."* Yes — that is the fix this certificate motivates; single-site
patching is the registered (and overwhelmingly common) procedure.
*"|E2|=2 overshoots, practitioners would notice."* The denoising side
(R1 = 1 exactly, no anomaly) already misattributes; the noising anomaly shows
the two directions provably disagree on the same 6-parameter network.

---

## Certificate 2 — Gradient×input and Integrated Gradients

**Script:** `verify_gradient_attribution.py` · **Network:** 2 inputs, 6 ReLU
units, linear readout (18 parameters); one network serves both methods.

**Weights (exact).** Tent unit `t(z) = ReLU(z) − 2·ReLU(z − 1/2) + ReLU(z − 1)`
applied to each input: `f(x1,x2) = t(x1) + t(x2)`.

**Distribution.** x1 ∈ {1/4, 2}, x2 ∈ {1/4, 3/4}, uniform product (4 inputs;
every support point interior to a linear piece — f is differentiable
everywhere on D, no kink excuses). Since t(1/4) = t(3/4) = 1/4 and
t(2) = 0, the output is a nonconstant function of **x1 only**:
f = 1/2 when x1 = 1/4, f = 1/4 when x1 = 2.

**Ground truth (proof).** Every within-support x1 swap changes f by exactly
1/4 at every point of D (x1 causal); every within-support x2 swap changes f by
exactly 0 at every point (x2 inert). Verified exhaustively in exact
arithmetic.

**Registered procedures.** (a) gradient×input `A_i = x_i·∂f/∂x_i` (Shrikumar
et al. 2016; Simonyan et al. 2013), rank by |A_i|. (b) Integrated Gradients
(Sundararajan, Taly & Yan, ICML 2017) with the paper's/Captum's default zero
baseline and straight-line path; the path integral is computed **exactly** by
sympy piecewise integration.

**Method output (exact), at the certified inputs (x1 = 2, i.e. half of D).**
- grad×input: (0, 1/4) at (2, 1/4); (0, −3/4) at (2, 3/4). Causal feature:
  exactly 0 (t is flat past z = 1, slope exactly 0, not a kink). Inert
  feature: nonzero.
- IG at X\* = (2, 1/4): **(0, 1/4)**. IG₁ = 0 exactly because the tent's
  up-slope and down-slope cancel along the path (t(2) = t(0) = 0); IG₂ = 1/4.
  Completeness holds exactly: 0 + 1/4 = f(X\*) − f(0,0). Sensitivity(a) is not
  violated (f(2,·) = f(0,·)) — the axioms permit this outcome.

**Mismatch statement.** At every certified input, both methods rank the
provably inert feature strictly above the sole causal feature, and assign the
causal feature exactly zero — while at that very input the attested x1-flip
changes the output and the attested x2-flip does not.

**Objections & answers.** *"IG = 0 only means 'same as baseline'."* True, and
that is the illusion: the registered practice ranks features by |IG| for
importance; here that ranking inverts causality at an in-distribution input
with the default baseline. *"Choose a better baseline."* Any single-path IG
has some function/input pair like this (Bilodeau et al. 2024); our
contribution is a concrete 18-parameter instance for the default protocol.
*"Saturation is a known toy story."* Known for missing causal features;
the exact simultaneous nonzero-on-inert contrast (all attribution mass
landing on the inert feature, by completeness) is the certificate.

---

## Certificate 3 — SAE-based circuit discovery (absorption as a circuit illusion)

**Script:** `verify_sae_circuit.py` · **Setting:** 2-dim activation space,
2-latent SAE; builds on `sae-identifiability/theory/verify_absorption_theory.py`
(eps\* framework), taken at eps = 0 (strict parent/child hierarchy), q = p =
1/2, λ = 1/10.

**Model.** Features parent = e1, child = e2 (orthonormal). Activations:
(1,1) w.p. 1/2 (parent+child), (1,0) w.p. 1/2 (parent only). Downstream
behavior: y = e1·x.

**Ground truth (proof).** y reads the parent feature only: erasing the child
component leaves y exactly unchanged on every input; erasing the parent
component sends y to 0. The child feature is causally inert for y.

**SAE optimality (exact + numeric support).** Between the faithful dictionary
U_F = [e1, e2] and the absorbed dictionary U_A = [e1, (e1+e2)/√2], exact
KKT-certified codes give L_F − L_A = q((2−√2)λ − λ²/4) = 79/800 − √2/20 > 0:
the absorbed SAE strictly wins (this is the repo's eps\* result at eps = 0 <
eps\*). A 0.25°-grid scan over all unit-norm dictionaries finds nothing below
L(U_A) (agreement to 8 decimals) — numeric support that U_A is globally
optimal; the exact claim is the pairwise one, which already implies **no
loss-minimizing SAE is the faithful dictionary**.

**Registered procedure.** Sparse feature circuits (Marks et al. 2024;
cf. Cunningham et al. 2023): splice the SAE, compute each latent's indirect
effect on the metric m = e1·x̂ (for a linear readout, attribution patching and
latent ablation coincide exactly: IE_j = f_j·(e1·u_j)), threshold to get the
circuit, label latents by activation pattern (auto-interp step).

**Method output (exact).** On the child-present (joint) inputs under the
optimal (absorbed) SAE: codes are f = (0, √2 − λ/2) — the parent latent is
**silent** (full absorption, KKT-certified). Hence IE₁ = 0 exactly and
IE₂ = 1 − √2λ/4 ≈ 0.965: the discovered circuit is **{latent 2} alone**.
Latent 2's activation pattern over D equals the *child*-feature indicator
(fires iff child present), so the labeling step names it the child latent;
latent 1 fires iff child *absent*; no latent tracks the parent feature.

**Mismatch statement.** The pipeline outputs: "on child-present inputs, y is
mediated by the child latent; the parent latent contributes exactly 0." The
true mechanism reads only the parent feature, and the child feature is
causally inert. This is the repo's CDX equivalence class made concrete: the
feature-basis and absorbed-basis descriptions are reconstruction-equivalent
mechanisms; the SAE training objective provably selects the absorbed one, and
the induced circuit narrative is wrong.

**Objections & answers.** *"Latent 2 really is causal — ablating it kills
ŷ."* Yes, at the latent level the interventions are consistent; the illusion
is at the *interpretation* layer the pipeline outputs (feature-labeled circuit
narrative), which is the artifact consumers read. The certificate shows the
optimal latent basis makes a correct feature-level narrative unavailable.
*"Trained SAEs might not reach the optimum."* Any SAE with loss ≤ L_F 
either is non-faithful or beats the exact bound; and the empirical phenomenon
is documented at scale (Chanin et al. 2024). *"eps = 0 is special."* The
repo's eps\* theory gives the entire regime eps < eps\*(λ, q); eps = 0 is just
the cleanest point of it.

---

## Certificate 4 — Linear probing (with control-task defense)

**Script:** `verify_probing.py` · **Network:** 4 parameters: h = (x, 2x),
y = 1·h1 + 0·h2.

**Distribution.** x uniform on {−2, −1, 1, 2}; probed feature z = sign(x).

**Ground truth (proof).** h2's readout weight is exactly 0: every intervention
on h2 leaves the output unchanged on every input; h1 fully mediates
(setting h1 ← h1(x′) moves the output to y(x′) for all pairs).

**Registered procedure.** (a) diagnostic probe on a component (Alain & Bengio
2016; Belinkov 2022); (b) min-norm least-squares probe on the layer with
|weight| ranking (Dalvi et al. 2019 style); (c) Hewitt–Liang 2019 control-task
selectivity — the standard defense against probe overfitting — computed by
exact enumeration of all 16 labelings of the 4 input types.

**Method output (exact).** (a) probe on h2 alone: accuracy 1. (b) min-norm
probe w = (3/25, 6/25): the inert neuron gets **twice** the weight of the
causal one; accuracy 1. (c) expected control accuracy 7/8, selectivity
1/8 > 0: the h2 probe **passes** the control-task defense.

**Mismatch statement.** The full registered pipeline — accuracy, selectivity,
and weight-based localization — reports h2 as the primary, selectively-encoded
carrier of z, while h2 is provably causally inert.

**Objections & answers.** *"Everyone knows probing isn't causal."* The
literature's registered remedy (control tasks) is *inside* this certificate
and passes; selectivity measures memorization, not causal use — the
certificate makes that gap exact. *"h2 = 2x is trivially correlated."*
Correlated-but-unused directions are exactly the documented real-world failure
(Ravichander et al. 2021); minimality is the point.

---

## Honest scoping

- **What "wrong" means here.** Each certificate fixes ground truth by
  construction (path-weight identities, exhaustive intervention checks, or
  KKT-certified optima) and shows the method's registered output names a
  component/feature whose causal contribution is exactly zero, or omits/ties
  the true mechanism. We do not claim the methods are wrong on average, on
  large models, or under the papers' full caveat lists — these are worst-case
  finite certificates, the analogue of adversarial unit tests.
- **C1** targets *single-site* patching with a single clean/corrupt pair (the
  standard workflow). Patching all subsets (2³ here) does recover the truth;
  the certificate quantifies the price of the single-site approximation, and
  the exact denoising-vs-noising disagreement stands regardless.
- **C2**'s IG claim is for the default zero baseline and straight-line path at
  the certified inputs (half the support); at x1 = 1/4 inputs IG is nonzero on
  x1. Grad×input is wrong on the same certified half with no baseline caveat.
- **C3**'s exact statement is pairwise (absorbed strictly beats faithful, so
  no optimal SAE is faithful); global optimality of U_A is supported by an
  exact-match grid scan but not symbolically proven here. The repo notes the
  global optimum tilts continuously for eps > 0; at eps = 0 the scan shows no
  gap at grid resolution.
- **C4**'s control-task computation depends on the 4-point support (selectivity
  values change with support size); the sign (strictly positive selectivity on
  an inert neuron) is the certified claim.
- Sizes were pushed down but minimality is not *proven* minimal (e.g., a
  5-parameter variant of C1 exists using a residual/skip path with a width-2
  hidden layer; we kept width 3 so that all three sites are patchable
  hidden units).

## Reproduce

```
python3 verify_activation_patching.py   # exit 0
python3 verify_gradient_attribution.py  # exit 0
python3 verify_sae_circuit.py           # exit 0
python3 verify_probing.py               # exit 0
```

## References

- Makelov, Lange, Geiger, Nanda 2023, arXiv:2311.17030 (subspace patching illusion); Wu et al. 2024, arXiv:2401.12631 (reply).
- Bolukbasi et al. 2021, arXiv:2104.07143 (BERT illusion).
- Friedman et al. 2023, arXiv:2312.03656 (simplification illusions).
- Meng et al. 2022 (causal tracing); Zhang & Nanda 2023, arXiv:2309.16042; Heimersheim & Nanda 2024, arXiv:2404.15255; Conmy et al. 2023 (ACDC); Wang et al. 2023, arXiv:2211.00593 (IOI); McGrath et al. 2023 (Hydra effect).
- Sundararajan, Taly, Yan 2017 (IG); Shrikumar et al. 2016/2017; Simonyan et al. 2013; Bilodeau et al. 2024 PNAS (impossibility theorems).
- Marks et al. 2024 (sparse feature circuits); Cunningham et al. 2023 (SAEs); Chanin et al. 2024, arXiv:2409.14507 (absorption); sae-identifiability repo eps* theory.
- Alain & Bengio 2016; Hewitt & Liang 2019 (control tasks); Belinkov 2022; Elazar et al. 2021 (amnesic probing); Ravichander et al. 2021; Dalvi et al. 2019.
