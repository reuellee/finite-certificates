# Empirical Verification Dossier

## Causal-ontology inversion in overcomplete sparse autoencoders

**Purpose:** This is a single-file evidence handoff for independent review of
the empirical claims in *Causal-Ontology Inversion in Overcomplete Sparse
Autoencoders*. It is optimized for machine review by Claude or another
scientific auditor: preregistered and exploratory results are separated, raw
seed-level records are included verbatim, frozen source is included verbatim,
and every binary checkpoint is represented by its filename, byte count, and
SHA-256 digest.

**Experiment date:** 2026-07-25  
**Status:** confirmatory experiment complete; 120/120 registered SAEs retained  
**Scope:** real digit images and learned MLP hidden activations with two
synthetic, exactly intervenable activation factors; not transformer
activations or natural semantic concepts.

## 1. Suggested audit sequence

1. Read Appendix A to check that the predictions, gates, estimands, seeds, and
   analysis hashes were fixed before the confirmatory runs according to the
   retained preregistration.
2. Inspect Appendices M–O for the locked training, scoring, and gradient-check
   source. Their hashes match those recorded in Appendix A.
3. Recalculate condition means and paired contrasts from Appendix H, treating
   the SAE seed—not factor or image—as the independent unit.
4. Reproduce the 20,000-replicate paired-seed percentile intervals using the
   algorithm and seed in Appendix N.
5. Compare the result with the registered decision rules in Appendix A and
   the unedited registered report in Appendix B.
6. Treat Appendices G, I–K, and P as exploratory only. They were produced
   after the registered verdict.
7. Use Appendix L to authenticate the 120 binary checkpoints if the separate
   reproducibility package is available.

## 2. What this one document permits—and does not

This document is sufficient to:

- inspect the complete preregistration and all analysis code;
- recompute every reported condition mean, paired high-minus-control
  difference, seed sign count, and bootstrap confidence interval;
- inspect all 120 registered run records and all 120 exploratory robustness
  records;
- check the registered decision logic for spin or post-hoc reinterpretation;
- authenticate a separately received checkpoint archive using 120 SHA-256
  digests.

The compressed NumPy checkpoints total several megabytes and are not base64
embedded because that would make the document impractical for model review.
Therefore this document alone cannot independently replay decoder-level
metrics from model parameters. The supplied audit below did perform that
replay locally. A third party can repeat it after obtaining the separately
packaged checkpoint archive whose digest appears in Section 10.

The retained preregistration says it was locked before confirmatory training,
and its embedded code hashes match the actual files. These local files alone
do **not** provide an independent trusted timestamp or public-commit proof of
the temporal claim. An external reviewer should request the relevant commit,
message, or archival timestamp if strict proof of preregistration timing is
required.

## 3. Artifact-consistency audit performed for this dossier

The dossier generator rebuilt the dataset and replayed all saved checkpoints
through the frozen evaluator. It separately reimplemented the aggregation and
bootstrap calculations over the resulting raw table. It stopped on any
mismatch larger than the stated numerical tolerances. Appendix Q contains the
complete audit and dossier-generation source.

| check | result |
|---|---|
| Reconstructed data SHA-256 | `d00e7d6c272ae538920cc91b7ab92e8ba91f522eb1c62b05677fbdc56799bad9` |
| Classifier held-out accuracy | 0.961111111111 |
| Registered rows / unique cells | 120 / 120 |
| Checkpoints / manifest failures | 120 / 0 |
| Maximum decoder-column norm error | 2.384e-07 |
| Maximum saved-metric replay error | 0.000e+00 |
| Maximum saved factor-array replay error | 0.000e+00 |
| Maximum condition-mean recomputation error | 2.220e-16 |
| Maximum paired-mean recomputation error | 1.776e-15 |
| Bootstrap intervals recomputed | 22 |
| Maximum bootstrap-endpoint error | 1.776e-15 |
| Maximum TopK deviation from L0=16 | 0.001388889 |

### Gradient and causal-construction checker

```text
gram: analytic=1.769786055550 numeric=1.769786055483 relative_error=3.748e-11
l1: analytic=0.031650355040 numeric=0.031650354781 relative_error=2.585e-10
topk: analytic=0.150732934622 numeric=0.150732934578 relative_error=4.386e-11
causal construction max_abs_error=5.662e-07
ALL GRADIENT AND CAUSAL-CONSTRUCTION CHECKS PASSED
```

## 4. Registered gates recomputed from raw records

The manipulation gate requires Gram ratio ≤0.80. At β=0.5, the retention gate
requires mean family gain ≥0.75, family cosine ≥0.95, and FVU ≤0.10.

| architecture | Gram ratio | family gain | family cosine | FVU |
|---|---|---|---|---|
| l1 | 0.541145298 | 0.791870850 | 0.994763230 | 0.038459629 |
| topk | 0.534286782 | 0.847875307 | 0.984464581 | 0.072032573 |

The TopK matched-sparsity gate also passes: every TopK run lies within 0.05 of
L0=16; the maximum observed deviation is
0.001388889.

## 5. Registered verdict and its evidential limits

The primary registered result is supported in both architectures:

- L1 high-minus-control one-atom alignment:
  −0.255285, 95% CI [−0.312468, −0.205723], 12/12 seeds negative.
- TopK high-minus-control one-atom alignment:
  −0.409225, 95% CI [−0.497346, −0.327031], 12/12 seeds negative.

Activation-aware multiplicity increased in both architectures. Causal
concentration decreased decisively only in TopK; the L1 interval crossed zero.
The result therefore supports a narrow statement: under this full
squared-Gram objective and strong registered penalty, a known causal generator
became less aligned with any one positive decoder ray while remaining
recoverable through the decoder family.

It does not establish that causal information vanished, that all
orthogonality penalties behave this way, that natural concepts behave this
way, or that the effect occurs in transformer SAEs.

## 6. Per-seed registered high-minus-control evidence

All deltas are β=0.5 minus β=0.0. Family quantities are the high-β levels.

| architecture | seed | Δ alignment | Δ concentration | Δ participation | Δ split count | high-β family gain | high-β family cosine | Δ FVU | Δ L0 |
|---|---|---|---|---|---|---|---|---|---|
| l1 | 0 | -0.213359 | -0.070854 | +8.367718 | +9.500 | 0.769570 | 0.994548 | +0.013693 | +14.799074 |
| l1 | 1 | -0.194279 | -0.106553 | +11.780717 | +13.000 | 0.789724 | 0.994397 | +0.012737 | +15.669907 |
| l1 | 2 | -0.233929 | -0.005893 | +5.725556 | +5.000 | 0.785652 | 0.994022 | +0.003073 | +13.819907 |
| l1 | 3 | -0.200011 | -0.084613 | +9.372045 | +11.500 | 0.796988 | 0.992687 | -0.001849 | +13.728704 |
| l1 | 4 | -0.197909 | -0.110073 | +12.024536 | +16.000 | 0.804260 | 0.994650 | +0.004648 | +13.944907 |
| l1 | 5 | -0.277863 | +0.043109 | +5.616403 | +3.000 | 0.794037 | 0.995304 | +0.004597 | +15.289352 |
| l1 | 6 | -0.190387 | -0.105626 | +9.866926 | +12.500 | 0.798758 | 0.994174 | +0.001485 | +13.881481 |
| l1 | 7 | -0.329174 | +0.038319 | +6.491488 | +6.000 | 0.787549 | 0.995687 | +0.007523 | +14.816667 |
| l1 | 8 | -0.409285 | +0.050759 | +7.175607 | +6.000 | 0.797834 | 0.995326 | +0.004754 | +13.988889 |
| l1 | 9 | -0.469439 | +0.078704 | +6.790718 | +8.000 | 0.778565 | 0.996319 | +0.009586 | +14.536574 |
| l1 | 10 | -0.145515 | +0.028602 | +7.717912 | +6.500 | 0.801795 | 0.994895 | +0.007653 | +14.259259 |
| l1 | 11 | -0.202275 | -0.069543 | +8.834167 | +10.000 | 0.797719 | 0.995149 | +0.004505 | +15.224074 |
| topk | 0 | -0.488526 | -0.513941 | +3.304072 | +4.000 | 0.847924 | 0.983654 | +0.066138 | +0.000000 |
| topk | 1 | -0.317925 | -0.717541 | +8.191428 | +10.500 | 0.799931 | 0.982429 | +0.073203 | +0.001389 |
| topk | 2 | -0.568794 | -0.255923 | +1.454050 | +0.000 | 0.885265 | 0.991347 | +0.053517 | +0.000926 |
| topk | 3 | -0.286642 | -0.706264 | +5.561386 | +6.500 | 0.848777 | 0.983612 | +0.063446 | +0.000000 |
| topk | 4 | -0.376136 | -0.475110 | +8.955528 | +9.000 | 0.798627 | 0.988068 | +0.058306 | +0.000000 |
| topk | 5 | -0.511691 | -0.438178 | +2.398024 | +2.000 | 0.867490 | 0.984242 | +0.061199 | +0.000000 |
| topk | 6 | -0.245644 | -0.268008 | +3.502079 | +4.000 | 0.853697 | 0.988458 | +0.062036 | +0.000000 |
| topk | 7 | -0.563802 | -0.634953 | +4.588843 | +4.500 | 0.856302 | 0.982403 | +0.069764 | +0.000000 |
| topk | 8 | -0.274864 | -0.582468 | +4.825052 | +4.500 | 0.869823 | 0.985361 | +0.062188 | +0.000000 |
| topk | 9 | -0.714431 | -0.523551 | +3.223549 | +3.500 | 0.834937 | 0.974544 | +0.070731 | +0.000000 |
| topk | 10 | -0.350930 | -0.532264 | +6.935184 | +8.500 | 0.805986 | 0.978980 | +0.064105 | +0.000000 |
| topk | 11 | -0.210982 | -0.033433 | +0.137264 | -1.000 | 0.905746 | 0.990477 | +0.061640 | +0.000000 |

## 7. Load-bearing alternative-cost diagnostics

- L1 held-out L0 increased from 15.7147 to 30.2113. The fixed lambda therefore
  did not preserve sparsity, although the matched-sparsity TopK result prevents
  L0 drift from being the sole explanation.
- TopK dead fraction increased from 0.0331 to 0.1814.
- FVU rose by 0.0060 in L1 and 0.0639 in TopK.
- High-β family gain was 0.7919 in L1 and 0.8479 in TopK, so the family
  survived but did not retain unit gain.
- Maximum absolute coherence did not fall. Post-hoc analysis found
  near-antipodal duplicates: minimizing the full Gram sum is a frame-potential
  objective and can approach a signed duplicated tight frame with
  maximum absolute coherence one.
- The dose response is non-monotone. Low or middle beta sometimes improved
  alignment; only β=0.5 versus β=0 was registered as confirmatory.
- The same held-out dataset is shared across all seeds. The 12 experimental
  units measure optimization/init variability, not independent dataset
  replications.
- Training-last-batch diagnostics in Appendix H were recorded immediately
  before the final parameter update, while held-out metrics and saved weights
  use the final parameters. Registered conclusions depend on held-out metrics,
  not those training diagnostics.

## 8. Reproduction commands

Run from the repository root in the package-pinned environment:

```bash
python3 experiments/coherence_transfer_semireal.py \
  --architectures l1,topk \
  --seeds 0,1,2,3,4,5,6,7,8,9,10,11 \
  --betas 0,0.025,0.0625,0.25,0.5 \
  --widths 68 \
  --outdir results/coherence_transfer_semireal_reproduction \
  --save-weights

python3 analysis/check_coherence_transfer_gradients.py
python3 analysis/analyze_coherence_transfer_semireal.py \
  results/coherence_transfer_semireal_reproduction
python3 analysis/posthoc_coherence_transfer_robustness.py \
  results/coherence_transfer_semireal_reproduction
```

The original run took 473.279
seconds in the recorded CPU environment. Runtime and per-run wall-clock columns
are not expected to reproduce exactly.

## 9. Claim-to-artifact map

| claim or check | authoritative evidence in this document |
|---|---|
| Design fixed before seeds 0–11 | Appendix A, with timing caveat in Section 2 |
| Training and estimand definitions | Appendices A and M |
| Exact run coverage and environment | Appendices D and H |
| Primary and secondary registered outcomes | Appendices B, E, F, and H |
| Seed pairing and bootstrap CIs | Appendices H and N |
| Family-retention and sparsity gates | Appendices B, C, D, F, and H |
| Gradient correctness | Section 3 and Appendix O |
| Checkpoint-to-metric replay | Section 3 and Appendix Q |
| Random-direction specificity | Appendices G, I–K, and P; exploratory |
| Threshold sensitivity | Appendices G, I–K, and P; exploratory |
| Antipodal/tight-frame diagnosis | Appendices G, I–K, and P; exploratory |
| Checkpoint authenticity | Appendix L |

## 10. Integrity manifest

| file | bytes | SHA-256 |
|---|---|---|
| notes/prereg-coherence-transfer-semireal.md | 9333 | 8951ceee0a9a2e529089792b6dbd4e890689720de60fa3980787de29e8ff32fd |
| experiments/coherence_transfer_semireal.py | 27270 | 45ae5fa0d5f7405cac75849eccea7897a66700838f2dcde2a5375db0f90d5861 |
| analysis/analyze_coherence_transfer_semireal.py | 16989 | ed974e5b3909fe852b50e828dfc083098eacefe3bd0b862f0349999acdbb022a |
| analysis/check_coherence_transfer_gradients.py | 5933 | 1c8a7fec7b12e0b7fbcd5984b6ce74d6f0f0aa74073570984846a2ac3023c892 |
| analysis/posthoc_coherence_transfer_robustness.py | 15020 | 93560c654ecad20c4a2fdfe04983aa36d0ac5728d8d94ff31c1a26aa90d9e0ce |
| analysis/render_empirical_verification_dossier.py | 28492 | 01779098f0676a81ef426620df88e258cb5d6388977273f511381038a7fa41ae |
| results/coherence_transfer_semireal/metadata.json | 1353 | c8dde96fe185acf26f4f7f00eadc50111644d94e5ab796ec8ecc4cedc627668c |
| results/coherence_transfer_semireal/REGISTERED_ANALYSIS.md | 4302 | 4427e5261867ef7760697b418d8630dced0e7775b564590e124b17ec496efdb4 |
| results/coherence_transfer_semireal/condition_means.csv | 2875 | bbe63d3e0ce42c3fc3745b28e68e66d946461df84c4b058fca392c97800ce676 |
| results/coherence_transfer_semireal/paired_contrasts.csv | 2349 | e38f35135926264d33b9640744c26c431c1d40040350d3d55ead55e38536ba75 |
| results/coherence_transfer_semireal/analysis_summary.json | 19177 | 9f038fda8691a0db0827c8fff166b792c7b0bc8c4d4196e6dca1a12e838aa53b |
| results/coherence_transfer_semireal/run_metrics.csv | 94969 | 376cbc49b00b7652459200dc90b79ce308a5084b83ec7dc8f4635de1dd6ab51b |
| results/coherence_transfer_semireal/POSTHOC_ROBUSTNESS.md | 7947 | 42f42e2d695913153f3ab2c8698b99c4c9c0f8144cdb11099827ba43ecb0e801 |
| results/coherence_transfer_semireal/posthoc_robustness_condition_means.csv | 5464 | 08df2f82d3e272c64fe1bf2dc241d68d84f0cf609435b24563c8155eeaed838a |
| results/coherence_transfer_semireal/posthoc_robustness_summary.json | 10827 | 8932f9dcdc354d22a1d77b7a501353fb7687be3398ba8696c7c48840b2d09be8 |
| results/coherence_transfer_semireal/posthoc_robustness_metrics.csv | 45048 | a55e5936166e70aa40cea9a2a0f42348ebde25c6511c3a27463b5a49f9166499 |
| results/coherence_transfer_semireal/weights_sha256.csv | 13079 | 583aaef2c712b1d4394c3e40096b72bbc954fbde558795039f9060c470872572 |
| results/coherence_transfer_semireal/coherence_transfer_dose_response.png | 182502 | ff8b216e8bb80a8efb984e02bc67058d95f61f9685d12715f3e74936499693c9 |
| output/pdf/Causal_Ontology_Coherence_Inversion_Report.pdf | 255136 | 2e29a3c92c5693767c04c5569b001617319278e5f3ff35e11df18c87e1a4422b |
| output/Causal_Ontology_Coherence_Inversion_Research_Package.zip | 2985785 | abcbf761a31101288db4b8cac4b02b9bb13322ef7b1b69186fb7c37553b237d0 |

The dossier itself cannot contain its own non-circular digest. Compute
`sha256sum EMPIRICAL_VERIFICATION_DOSSIER.md` after receipt.

---

# Appendix A — retained preregistration

````markdown
# Pre-registration — semi-real transfer of the overcomplete coherence-inversion certificate

**Status: LOCKED BEFORE CONFIRMATORY SEEDS 0–11 WERE TRAINED.**  
**Lock mechanism:** SHA-256 hashes of the training and analysis scripts below.  
**Lock date:** 2026-07-25.

## Question

Does the finite population-objective obstruction survive contact with a trained,
amortized, overcomplete SAE on a learned representation of real data?

The precise transfer hypothesis is deliberately narrower than “orthogonality
hurts interpretability”:

> A sufficiently strong full squared-Gram penalty can reduce the best
> positive-ray alignment between a known one-dimensional causal activation
> generator and any individual decoder atom, while the generator remains
> recoverable through the decoder family and through the SAE's held-out
> counterfactual reconstruction.

This is the trained-SAE analogue of the certificate's distinction between loss
of a one-atom ontology and loss of representability.

## Scope and realism

This is a **semi-real activation experiment**, not an LLM experiment.

1. A one-hidden-layer classifier is trained on the real scikit-learn
   handwritten-digits dataset using only the training split.
2. Its 32-dimensional ReLU hidden activations are the real learned background
   representation.
3. Two controlled binary activation factors are appended after that hidden
   layer. Every base image is instantiated in all four intervention states
   `00`, `10`, `01`, `11`.
4. A fixed random orthogonal transform mixes the 34 coordinates, eliminating
   privileged visible factor axes.
5. A trained 68-latent SAE reconstructs these 34-dimensional activations.

The held-out test set contains images excluded from both classifier and SAE
training. The appended factors are synthetic and exactly known; “causal”
refers only to these controlled activation interventions. The study does not
test natural semantic factors or downstream model behavior.

## Dataset and fixed representation

- `sklearn.datasets.load_digits`, 1,797 real 8×8 handwritten-digit images.
- Stratified 70/30 base-image split, seed `20260725`.
- Classifier: `MLPClassifier`, one 32-unit ReLU hidden layer, `lbfgs`,
  `alpha=1e-4`, `max_iter=600`, seed `271828`.
- Background hidden activations are scaled by one scalar to mean norm
  \(\sqrt{32}\); they are not coordinate-wise whitened.
- Factor amplitude before final normalization: 1.5.
- Orthogonal mixing seed: `314159`.
- One final scalar makes mean training-vector norm \(\sqrt{34}\).
- Expanded SAE rows: 5,028 train and 2,160 held-out evaluation.
- Frozen array digest:
  `d00e7d6c272ae538920cc91b7ab92e8ba91f522eb1c62b05677fbdc56799bad9`.
- The classifier quality gate is held-out accuracy at least 0.94.

## SAE design

Two architectures are trained:

- **L1:** ReLU encoder and
  \[
  L=\mathbb E\|x-\hat x\|_2^2
    +0.2\,\mathbb E\|f(x)\|_1+\beta C_\Sigma(D).
  \]
- **TopK:** ReLU followed by \(k=16\), with
  \[
  L=\mathbb E\|x-\hat x\|_2^2+\beta C_\Sigma(D).
  \]

Both use
\[
C_\Sigma(D)=\sum_{i<j}\langle d_i,d_j\rangle^2
\]
and unit decoder columns. This is the exact full squared-Gram penalty from the
finite certificate. It is **not** OrtSAE's randomized, chunked,
positive-nearest-neighbor objective.

Fixed design:

- \(d=34\), \(m=68\) (2× overcomplete).
- \(\beta\in\{0,0.025,0.0625,0.25,0.5\}\).
- SAE seeds 0–11; same initial parameters and minibatch indices across beta
  within each architecture/seed.
- 2 architectures × 5 beta levels × 12 seeds = **120 trained SAEs**.
- 10,000 minibatch steps; batch size 256; Adam learning rate 0.002, decayed
  to one-third at step 5,000 and one-tenth at step 8,000.
- Decoder columns renormalized after every update.
- No result-dependent run exclusion and no dead-latent resampling.
- All weights are retained and SHA-256-manifested.

TopK is the sparsity-confound control: its held-out \(L_0\) must remain
\(16\pm0.05\) in every run. L1 uses the same \(\lambda\) at every beta, as the
theorem does; any beta-induced \(L_0\) change is reported rather than adjusted
away.

## Experimental unit and estimands

The two planted factors are averaged within an SAE. The independent
experimental unit is the **SAE seed**, \(n=12\), not the factor and not the
evaluation row.

For factor direction \(u\):

- **one-atom alignment**
  \[
  A=\max_k \max(0,u^\top d_k);
  \]
- the paired held-out feature effect is the mean encoder-code difference under
  adding the factor, averaged across the other factor's two states;
- atom \(k\)'s activation-aware aligned contribution is
  \[
  p_k=\max\{0,\ \mathbb E[\Delta f_k]\,u^\top d_k\};
  \]
- **causal concentration** is \(\max_k p_k/\sum_k p_k\);
- **causal participation ratio** is
  \((\sum_k p_k)^2/\sum_k p_k^2\);
- **split count** is the number of \(p_k\) at least 10% of \(\max_k p_k\);
- **family gain** is
  \(u^\top\mathbb E[\Delta\hat x]/a\), where \(a\) is the true post-scaling
  intervention amplitude;
- **family cosine** is the cosine between
  \(\mathbb E[\Delta\hat x]\) and \(u\).

Also reported: held-out FVU, \(L_0\), dead fraction, Gram sum, mean squared
coherence, maximum absolute coherence, nonnegative-family reconstruction, and
all per-seed values.

## Gates

The primary result is uninterpretable if any gate fails.

1. **Conformance:** exactly 120 unique rows with the registered architectures,
   width, betas, and seeds; correct dataset hash, classifier quality, step
   count, \(k\), and \(\lambda\).
2. **Manipulation:** within each architecture, mean
   \(C_\Sigma(\beta=0.5)/C_\Sigma(\beta=0)\le0.80\).
3. **Causal-family retention at beta 0.5:** within each architecture,
   mean family gain at least 0.75, mean family cosine at least 0.95, and mean
   held-out FVU at most 0.10. No run is dropped if retention is poor; the gate
   fails.
4. **TopK matched sparsity:** every TopK run has held-out \(L_0\) within 0.05 of
   16.

## Registered predictions

All confidence intervals are 20,000-replicate paired-seed percentile
bootstraps with the frozen analysis seed.

### P1 — primary: one-atom alignment falls while the family survives

For each architecture separately, contrast
\[
\Delta A=A_{\beta=0.5}-A_{\beta=0}.
\]

- **SUPPORTED** only if every gate passes and the 95% CI upper endpoint is
  below zero in **both** L1 and TopK.
- **NOT SUPPORTED** otherwise, unless a gate failure makes the result
  **UNINTERPRETABLE**.

Passing in TopK is load-bearing because it rules out a change in \(L_0\) as the
sole explanation. Passing in L1 connects most directly to the certificate's
coding objective.

### P2 — secondary: activation-aware multiplicity rises

For beta 0.5 minus beta 0, both split count and participation ratio must have
95% CI lower endpoints above zero. Report separately by architecture.

### P3 — secondary: causal contribution becomes less concentrated

Causal concentration at beta 0.5 minus beta 0 must have a 95% CI upper endpoint
below zero. Report separately by architecture.

### Dose profile — descriptive

All five beta levels are reported. No monotonicity verdict is registered.
The disjoint-seed pilot showed that low and middle penalties can improve
alignment by steering optimization into different basins; only the
strong-versus-zero contrast is confirmatory.

## Pilot disclosure

Before this lock, seeds 900–903 were used to:

- check code execution and gradient stability;
- increase training from 3,000 to 10,000 steps;
- choose beta 0.5 as the strong condition;
- add the fixed-\(L_0\) TopK replication;
- set the family-retention and FVU gates.

Those seeds are excluded from every confirmatory statistic. The pilot is
preserved separately under `/tmp` for this session and its role is disclosed
because it informed the registered design.

## Frozen code

- Training and scoring:
  `experiments/coherence_transfer_semireal.py`  
  SHA-256
  `45ae5fa0d5f7405cac75849eccea7897a66700838f2dcde2a5375db0f90d5861`
- Registered analysis:
  `analysis/analyze_coherence_transfer_semireal.py`  
  SHA-256
  `ed974e5b3909fe852b50e828dfc083098eacefe3bd0b862f0349999acdbb022a`
- Independent finite-difference and causal-construction checks:
  `analysis/check_coherence_transfer_gradients.py`  
  SHA-256
  `1c8a7fec7b12e0b7fbcd5984b6ce74d6f0f0aa74073570984846a2ac3023c892`

Before lock, the gradient checker passed the full-Gram, L1, and fixed-mask TopK
directional derivatives at relative error below \(3\times10^{-10}\), and
verified the constructed held-out interventions to maximum absolute error
below \(6\times10^{-7}\).

## Interpretation rules

- P1 concerns **loss of a one-decoder-atom ontology**, not erasure of the
  causal direction from the SAE or source representation.
- A family-retention failure is signal destruction, not support.
- A geometry-only effect without activation-aware reconstruction is
  insufficient.
- Increased dead rate, worse FVU, a rising maximum absolute coherence, and L1
  \(L_0\) drift are alternative-cost diagnostics and must be reported.
- The result cannot be generalized to transformers, natural semantic
  features, all coherence penalties, or OrtSAE without a separate experiment.
- The exact theorem is a global population-objective exclusion. This
  experiment concerns finite-data optimization and may fail even if the
  theorem is correct.
````

# Appendix B — registered analysis report

````markdown
# Semi-real coherence-transfer experiment: registered analysis

**Primary verdict:** SUPPORTED: strong full-Gram regularization reduced one-atom causal-direction alignment while the causal direction remained recoverable at the decoder-family level in both architectures

**Activation-aware splitting:** SUPPORTED IN BOTH ARCHITECTURES.

**Causal-contribution concentration loss:** SUPPORTED IN topk.

## Gates

- Conformance: PASS
- Coherence manipulation: PASS
- Family-retention gate: PASS
- TopK fixed-L0 gate: PASS

## Condition means

| architecture | beta | fvu | l0 | dead_fraction | gram_penalty | max_absolute_coherence | mean_factor_max_positive_cosine | mean_factor_causal_concentration | mean_factor_causal_split_count | mean_factor_family_gain |
|---|---|---|---|---|---|---|---|---|---|---|
| l1 | 0 | 0.0324 | 15.7147 | 0.0000 | 80.7167 | 0.9962 | 0.7082 | 0.2537 | 4.7500 | 0.9001 |
| l1 | 0.025 | 0.0284 | 19.2423 | 0.0000 | 38.5934 | 0.9677 | 0.8708 | 0.6246 | 2.2917 | 0.8743 |
| l1 | 0.0625 | 0.0302 | 23.7382 | 0.0000 | 38.9274 | 0.9895 | 0.8179 | 0.7628 | 1.5833 | 0.8531 |
| l1 | 0.25 | 0.0360 | 29.0847 | 0.0000 | 41.7816 | 0.9977 | 0.4820 | 0.2544 | 11.5000 | 0.7943 |
| l1 | 0.5 | 0.0385 | 30.2113 | 0.0000 | 43.6794 | 0.9990 | 0.4529 | 0.2275 | 13.6667 | 0.7919 |
| topk | 0 | 0.0082 | 15.9998 | 0.0331 | 84.1865 | 0.9861 | 0.8958 | 0.9108 | 1.4167 | 0.9993 |
| topk | 0.025 | 0.0159 | 16.0000 | 0.2574 | 38.4412 | 1.0000 | 0.8470 | 0.9208 | 1.3333 | 0.9980 |
| topk | 0.0625 | 0.0358 | 16.0000 | 0.2108 | 39.6898 | 1.0000 | 0.7410 | 0.8135 | 1.4167 | 0.9824 |
| topk | 0.25 | 0.0617 | 16.0000 | 0.2047 | 43.0857 | 1.0000 | 0.4598 | 0.4677 | 4.4583 | 0.8845 |
| topk | 0.5 | 0.0720 | 16.0000 | 0.1814 | 44.9797 | 1.0000 | 0.4866 | 0.4373 | 6.0833 | 0.8479 |

## Registered high-minus-control contrasts

### L1

- `mean_factor_max_positive_cosine`: -0.2553, 95% paired-seed bootstrap CI [-0.3125, -0.2057], 12/12 negative.
- `mean_factor_causal_concentration`: -0.0261, 95% paired-seed bootstrap CI [-0.0644, +0.0130], 7/12 negative.
- `mean_factor_causal_participation_ratio`: +8.3136, 95% paired-seed bootstrap CI [+7.1881, +9.5159], 0/12 negative.
- `mean_factor_causal_split_count`: +8.9167, 95% paired-seed bootstrap CI [+6.9167, +11.0417], 0/12 negative.
- `mean_factor_family_gain`: -0.1082, 95% paired-seed bootstrap CI [-0.1138, -0.1033], 12/12 negative.
- `fvu`: +0.0060, 95% paired-seed bootstrap CI [+0.0037, +0.0085], 1/12 negative.
- `l0`: +14.4966, 95% paired-seed bootstrap CI [+14.1518, +14.8654], 0/12 negative.
- `dead_fraction`: +0.0000, 95% paired-seed bootstrap CI [+0.0000, +0.0000], 0/12 negative.
- `gram_penalty`: -37.0372, 95% paired-seed bootstrap CI [-38.7170, -35.2405], 12/12 negative.
- `max_absolute_coherence`: +0.0028, 95% paired-seed bootstrap CI [-0.0004, +0.0079], 4/12 negative.

### TOPK

- `mean_factor_max_positive_cosine`: -0.4092, 95% paired-seed bootstrap CI [-0.4973, -0.3270], 12/12 negative.
- `mean_factor_causal_concentration`: -0.4735, 95% paired-seed bootstrap CI [-0.5766, -0.3580], 12/12 negative.
- `mean_factor_causal_participation_ratio`: +4.4230, 95% paired-seed bootstrap CI [+3.0175, +5.8702], 0/12 negative.
- `mean_factor_causal_split_count`: +4.6667, 95% paired-seed bootstrap CI [+2.7917, +6.5417], 1/12 negative.
- `mean_factor_family_gain`: -0.1514, 95% paired-seed bootstrap CI [-0.1698, -0.1333], 12/12 negative.
- `fvu`: +0.0639, 95% paired-seed bootstrap CI [+0.0609, +0.0668], 0/12 negative.
- `l0`: +0.0002, 95% paired-seed bootstrap CI [+0.0000, +0.0005], 0/12 negative.
- `dead_fraction`: +0.1483, 95% paired-seed bootstrap CI [+0.1140, +0.1875], 0/12 negative.
- `gram_penalty`: -39.2068, 95% paired-seed bootstrap CI [-45.3282, -33.1541], 12/12 negative.
- `max_absolute_coherence`: +0.0139, 95% paired-seed bootstrap CI [+0.0065, +0.0230], 0/12 negative.

## Scope

This is a trained, held-out, matched-seed SAE experiment on a learned neural representation of real images with two appended and orthogonally mixed controlled factors. It is not an LLM activation experiment, and the appended factors are synthetic. The causal claim is limited to recovery of those known activation generators. The full squared-Gram penalty tested here also differs from OrtSAE's randomized positive-neighbor penalty.
````

# Appendix C — condition means

````csv
architecture,m,beta,fvu,l0,dead_fraction,gram_penalty,mean_squared_coherence,max_absolute_coherence,mean_factor_max_positive_cosine,mean_factor_causal_concentration,mean_factor_causal_participation_ratio,mean_factor_causal_split_count,mean_factor_single_gain,mean_factor_family_gain,mean_factor_family_cosine,mean_factor_nnls_residual
l1,68,0.0,0.0324259212551017,15.714699074074074,0.0,80.71666081746419,0.03543312537173426,0.9961772014697393,0.7082280442118645,0.2536639686657839,4.436633597378784,4.75,0.22840099059966124,0.9000705480575562,0.9981426273783048,0.0
l1,68,0.025,0.028365586263438016,19.242283950617285,0.0,38.59343306223551,0.016941805835813232,0.9677407393852869,0.8708349584291378,0.6246204147147415,2.182083061180299,2.2916666666666665,0.5425451291354969,0.8743454913298289,0.9987633153796196,0.0
l1,68,0.0625,0.03020628665884331,23.738233024691358,0.0,38.92741552988688,0.017088417739917785,0.989467387398084,0.8179208661119143,0.7628255000591445,1.8543366725563157,1.5833333333333333,0.6524852661417674,0.85307510693868,0.9992376988132795,0.0
l1,68,0.25,0.03595384862273926,29.084722222222222,0.0,41.781588872273765,0.018341347264746774,0.9976989875237147,0.4819988552480936,0.25441212923613743,11.143147744069617,11.5,0.2054158863343071,0.7942654266953468,0.9950757349530855,0.0
l1,68,0.5,0.03845962850997841,30.211265432098767,0.0,43.67944145202637,0.019174469479670067,0.9989522993564606,0.45294258433083695,0.227525467294744,12.750282957427835,13.666666666666666,0.18248702136964312,0.7918708498279253,0.9947632302840551,0.009023418626458592
topk,68,0.0,0.008176527296503325,15.999807098765432,0.03308823529411759,84.18649800618489,0.036956320361544635,0.9860921204090118,0.8957777967055639,0.9108151677333632,1.295178245690744,1.4166666666666667,0.9103851949862908,0.9992585927248001,0.9999787881970406,0.015754791012152342
topk,68,0.025,0.015899350866675332,16.0,0.25735294117647056,38.441173235575356,0.016874966522057815,0.9999989320834478,0.8470247692118088,0.9207764102682612,1.2273886330617885,1.3333333333333333,0.9242953659188919,0.9980266764760017,0.9995417321721712,0.0
topk,68,0.0625,0.03584116293738283,16.0,0.21078431372549014,39.68976847330729,0.01742307671035324,0.9999957034985224,0.740950937072436,0.8134612828230868,1.5029095185392587,1.4166666666666667,0.8149108261848427,0.982412559290727,0.9971727306644121,0.0
topk,68,0.25,0.061683339687685135,16.0,0.204656862745098,43.08565044403076,0.018913805950432985,0.9999994883934656,0.459812643006444,0.4676906460045502,4.648379708926124,4.458333333333333,0.44255971646408004,0.8845326726635298,0.9868846411506335,0.0
topk,68,0.5,0.07203257332245504,16.0,0.18137254901960778,44.97973314921061,0.019745273205141176,0.9999856253465017,0.48658046250542003,0.4373456325677521,5.71821642858609,6.083333333333333,0.40766095723795304,0.847875307003657,0.9844645808140436,0.04778474478798017
````

# Appendix D — run metadata and environment

````json
{
  "architectures": [
    "l1",
    "topk"
  ],
  "betas": [
    0.0,
    0.025,
    0.0625,
    0.25,
    0.5
  ],
  "config": {
    "alignment_threshold": 0.9,
    "batch_size": 256,
    "classifier_seed": 271828,
    "data_seed": 20260725,
    "eval_threshold": 1e-06,
    "expansion": 2,
    "factor_amplitude": 1.5,
    "grad_clip": 10.0,
    "hidden_dim": 32,
    "l1_lambda": 0.2,
    "learning_rate": 0.002,
    "mixing_seed": 314159,
    "split_relative_threshold": 0.1,
    "steps": 10000,
    "topk_k": 16
  },
  "dataset": {
    "ambient_dim": 34,
    "classifier_eval_accuracy": 0.9611111111111111,
    "classifier_train_accuracy": 1.0,
    "data_sha256": "d00e7d6c272ae538920cc91b7ab92e8ba91f522eb1c62b05677fbdc56799bad9",
    "effective_factor_amplitude": 1.492695927619934,
    "eval_base_n": 540,
    "eval_shape": [
      2160,
      34
    ],
    "train_base_n": 1257,
    "train_shape": [
      5028,
      34
    ]
  },
  "environment": {
    "numpy": "2.3.5",
    "platform": "Linux-6.12.13-x86_64-with-glibc2.39",
    "python": "3.12.13 (main, Mar  3 2026, 14:59:34) [Clang 21.1.4 ]",
    "scipy": "1.17.0",
    "sklearn": "1.8.0"
  },
  "seeds": [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11
  ],
  "steps_override": null,
  "wall_seconds": 473.2786214351654,
  "widths": [
    68
  ]
}
````

# Appendix E — registered paired contrasts

````csv
architecture,field,high_beta,control_beta,n_seeds,mean_difference,ci95_lower,ci95_upper,negative_seeds,positive_seeds,zero_seeds
l1,mean_factor_max_positive_cosine,0.5,0.0,12,-0.2552854598810275,-0.31246846335319184,-0.2057225167440872,12,0,0
l1,mean_factor_causal_concentration,0.5,0.0,12,-0.02613850137103989,-0.06437221606914129,0.013048942763354558,7,5,0
l1,mean_factor_causal_participation_ratio,0.5,0.0,12,8.31364936004905,7.188099568240194,9.515855966147326,0,12,0
l1,mean_factor_causal_split_count,0.5,0.0,12,8.916666666666666,6.916666666666667,11.041666666666666,0,12,0
l1,mean_factor_single_gain,0.5,0.0,12,-0.045913969230018135,-0.0777124093828004,-0.013684648156922238,8,4,0
l1,mean_factor_family_gain,0.5,0.0,12,-0.10819969822963076,-0.1137941805645823,-0.10329209392269449,12,0,0
l1,fvu,0.5,0.0,12,0.006033707254876707,0.0036609476082958376,0.008510241820476962,1,11,0
l1,l0,0.5,0.0,12,14.496566358024694,14.151812307098766,14.865433063271606,0,12,0
l1,dead_fraction,0.5,0.0,12,0.0,0.0,0.0,0,0,12
l1,gram_penalty,0.5,0.0,12,-37.03721936543783,-38.716982698440546,-35.2405322154363,12,0,0
l1,max_absolute_coherence,0.5,0.0,12,0.002775097886721293,-0.00043546669185165194,0.007877242316802343,4,8,0
topk,mean_factor_max_positive_cosine,0.5,0.0,12,-0.4091973342001438,-0.4973189369464914,-0.32696612762908145,12,0,0
topk,mean_factor_causal_concentration,0.5,0.0,12,-0.47346953516561124,-0.5765592853590567,-0.35798140085725877,12,0,0
topk,mean_factor_causal_participation_ratio,0.5,0.0,12,4.423038182895346,3.0175062926635916,5.870233311723826,0,12,0
topk,mean_factor_causal_split_count,0.5,0.0,12,4.666666666666667,2.7916666666666665,6.541666666666667,1,10,1
topk,mean_factor_single_gain,0.5,0.0,12,-0.5027242377483377,-0.6156548298457679,-0.36452524836343025,11,1,0
topk,mean_factor_family_gain,0.5,0.0,12,-0.1513832857211431,-0.16984184005608158,-0.1332839298993349,12,0,0
topk,fvu,0.5,0.0,12,0.06385604602595171,0.06087711441214196,0.06682617155505192,0,12,0
topk,l0,0.5,0.0,12,0.00019290123456805475,0.0,0.00046296296296347944,0,2,10
topk,dead_fraction,0.5,0.0,12,0.1482843137254902,0.11397058823529416,0.18750000000000003,0,12,0
topk,gram_penalty,0.5,0.0,12,-39.20676485697428,-45.328213930130005,-33.15406637191773,12,0,0
topk,max_absolute_coherence,0.5,0.0,12,0.013893504937489809,0.006526186938087145,0.022956577812631856,0,12,0
````

# Appendix F — registered structured analysis summary

````json
{
  "alignment_pass": {
    "l1": true,
    "topk": true
  },
  "concentration_pass": {
    "l1": false,
    "topk": true
  },
  "concentration_verdict": "SUPPORTED IN topk",
  "contrasts": [
    {
      "architecture": "l1",
      "ci95_lower": -0.31246846335319184,
      "ci95_upper": -0.2057225167440872,
      "control_beta": 0.0,
      "field": "mean_factor_max_positive_cosine",
      "high_beta": 0.5,
      "mean_difference": -0.2552854598810275,
      "n_seeds": 12,
      "negative_seeds": 12,
      "per_seed_difference": {
        "0": -0.21335889399051672,
        "1": -0.19427905976772308,
        "10": -0.14551499485969543,
        "11": -0.20227517187595367,
        "2": -0.23392939567565924,
        "3": -0.2000109702348709,
        "4": -0.19790872931480408,
        "5": -0.2778627425432206,
        "6": -0.19038666784763336,
        "7": -0.3291744738817215,
        "8": -0.40928503870964056,
        "9": -0.4694393798708916
      },
      "positive_seeds": 0,
      "zero_seeds": 0
    },
    {
      "architecture": "l1",
      "ci95_lower": -0.06437221606914129,
      "ci95_upper": 0.013048942763354558,
      "control_beta": 0.0,
      "field": "mean_factor_causal_concentration",
      "high_beta": 0.5,
      "mean_difference": -0.02613850137103989,
      "n_seeds": 12,
      "negative_seeds": 7,
      "per_seed_difference": {
        "0": -0.07085445607314719,
        "1": -0.1065528940405635,
        "10": 0.028602295647973452,
        "11": -0.06954330727103789,
        "2": -0.005893477926278229,
        "3": -0.08461279444361,
        "4": -0.11007277006373178,
        "5": 0.04310906257060232,
        "6": -0.10562561544975899,
        "7": 0.03831904502525668,
        "8": 0.05075932284719778,
        "9": 0.0787035727246187
      },
      "positive_seeds": 5,
      "zero_seeds": 0
    },
    {
      "architecture": "l1",
      "ci95_lower": 7.188099568240194,
      "ci95_upper": 9.515855966147326,
      "control_beta": 0.0,
      "field": "mean_factor_causal_participation_ratio",
      "high_beta": 0.5,
      "mean_difference": 8.31364936004905,
      "n_seeds": 12,
      "negative_seeds": 0,
      "per_seed_difference": {
        "0": 8.367718080199317,
        "1": 11.780716898005984,
        "10": 7.7179118020917725,
        "11": 8.834166907176652,
        "2": 5.725555988830248,
        "3": 9.372045096200736,
        "4": 12.024536070952596,
        "5": 5.616402645543197,
        "6": 9.866926317126808,
        "7": 6.491487530969972,
        "8": 7.1756074231841716,
        "9": 6.790717560307144
      },
      "positive_seeds": 12,
      "zero_seeds": 0
    },
    {
      "architecture": "l1",
      "ci95_lower": 6.916666666666667,
      "ci95_upper": 11.041666666666666,
      "control_beta": 0.0,
      "field": "mean_factor_causal_split_count",
      "high_beta": 0.5,
      "mean_difference": 8.916666666666666,
      "n_seeds": 12,
      "negative_seeds": 0,
      "per_seed_difference": {
        "0": 9.5,
        "1": 13.0,
        "10": 6.5,
        "11": 10.0,
        "2": 5.0,
        "3": 11.5,
        "4": 16.0,
        "5": 3.0,
        "6": 12.5,
        "7": 6.0,
        "8": 6.0,
        "9": 8.0
      },
      "positive_seeds": 12,
      "zero_seeds": 0
    },
    {
      "architecture": "l1",
      "ci95_lower": -0.0777124093828004,
      "ci95_upper": -0.013684648156922238,
      "control_beta": 0.0,
      "field": "mean_factor_single_gain",
      "high_beta": 0.5,
      "mean_difference": -0.045913969230018135,
      "n_seeds": 12,
      "negative_seeds": 8,
      "per_seed_difference": {
        "0": -0.08680228593840061,
        "1": -0.11133115959002499,
        "10": -0.0007100756602110014,
        "11": -0.08050583186341148,
        "2": -0.031998531582242196,
        "3": -0.09351449522470742,
        "4": -0.11237164821288201,
        "5": 0.007301873412598192,
        "6": -0.11091551418859551,
        "7": 0.0041094204425762,
        "8": 0.0169623434340595,
        "9": 0.048808274211023905
      },
      "positive_seeds": 4,
      "zero_seeds": 0
    },
    {
      "architecture": "l1",
      "ci95_lower": -0.1137941805645823,
      "ci95_upper": -0.10329209392269449,
      "control_beta": 0.0,
      "field": "mean_factor_family_gain",
      "high_beta": 0.5,
      "mean_difference": -0.10819969822963076,
      "n_seeds": 12,
      "negative_seeds": 12,
      "per_seed_difference": {
        "0": -0.1291818618774414,
        "1": -0.1093035638332367,
        "10": -0.09856638312339783,
        "11": -0.10018622875213623,
        "2": -0.11297303438186646,
        "3": -0.10435321927070607,
        "4": -0.0961422324180603,
        "5": -0.10783490538597096,
        "6": -0.10505428910255421,
        "7": -0.11395284533500671,
        "8": -0.10051882266998291,
        "9": -0.12032899260520935
      },
      "positive_seeds": 0,
      "zero_seeds": 0
    },
    {
      "architecture": "l1",
      "ci95_lower": 0.0036609476082958376,
      "ci95_upper": 0.008510241820476962,
      "control_beta": 0.0,
      "field": "fvu",
      "high_beta": 0.5,
      "mean_difference": 0.006033707254876707,
      "n_seeds": 12,
      "negative_seeds": 1,
      "per_seed_difference": {
        "0": 0.013692563399672498,
        "1": 0.012737225741147995,
        "10": 0.0076529290527104984,
        "11": 0.004504568874835996,
        "2": 0.0030726380646229,
        "3": -0.0018485225737095018,
        "4": 0.004648208618164101,
        "5": 0.0045968033373356,
        "6": 0.0014853700995445945,
        "7": 0.007522817701101303,
        "8": 0.004753760993480696,
        "9": 0.0095861237496138
      },
      "positive_seeds": 11,
      "zero_seeds": 0
    },
    {
      "architecture": "l1",
      "ci95_lower": 14.151812307098766,
      "ci95_upper": 14.865433063271606,
      "control_beta": 0.0,
      "field": "l0",
      "high_beta": 0.5,
      "mean_difference": 14.496566358024694,
      "n_seeds": 12,
      "negative_seeds": 0,
      "per_seed_difference": {
        "0": 14.799074074074072,
        "1": 15.669907407407404,
        "10": 14.25925925925926,
        "11": 15.224074074074077,
        "2": 13.819907407407408,
        "3": 13.728703703703706,
        "4": 13.944907407407406,
        "5": 15.289351851851853,
        "6": 13.881481481481481,
        "7": 14.81666666666667,
        "8": 13.988888888888892,
        "9": 14.536574074074073
      },
      "positive_seeds": 12,
      "zero_seeds": 0
    },
    {
      "architecture": "l1",
      "ci95_lower": 0.0,
      "ci95_upper": 0.0,
      "control_beta": 0.0,
      "field": "dead_fraction",
      "high_beta": 0.5,
      "mean_difference": 0.0,
      "n_seeds": 12,
      "negative_seeds": 0,
      "per_seed_difference": {
        "0": 0.0,
        "1": 0.0,
        "10": 0.0,
        "11": 0.0,
        "2": 0.0,
        "3": 0.0,
        "4": 0.0,
        "5": 0.0,
        "6": 0.0,
        "7": 0.0,
        "8": 0.0,
        "9": 0.0
      },
      "positive_seeds": 0,
      "zero_seeds": 12
    },
    {
      "architecture": "l1",
      "ci95_lower": -38.716982698440546,
      "ci95_upper": -35.2405322154363,
      "control_beta": 0.0,
      "field": "gram_penalty",
      "high_beta": 0.5,
      "mean_difference": -37.03721936543783,
      "n_seeds": 12,
      "negative_seeds": 12,
      "per_seed_difference": {
        "0": -30.053306579589844,
        "1": -42.17662811279297,
        "10": -36.99877166748047,
        "11": -39.97633743286133,
        "2": -35.04730987548828,
        "3": -39.12897491455078,
        "4": -34.88051605224609,
        "5": -38.08256530761719,
        "6": -37.469444274902344,
        "7": -37.52118682861328,
        "8": -39.22411346435547,
        "9": -33.88747787475587
      },
      "positive_seeds": 0,
      "zero_seeds": 0
    },
    {
      "architecture": "l1",
      "ci95_lower": -0.00043546669185165194,
      "ci95_upper": 0.007877242316802343,
      "control_beta": 0.0,
      "field": "max_absolute_coherence",
      "high_beta": 0.5,
      "mean_difference": 0.002775097886721293,
      "n_seeds": 12,
      "negative_seeds": 4,
      "per_seed_difference": {
        "0": -0.0013868212699887916,
        "1": 0.0010184645652769886,
        "10": 2.962350845325812e-05,
        "11": 0.0005295276641847924,
        "2": -0.0009697079658508301,
        "3": 0.0013256072998047985,
        "4": 0.0008646249771117054,
        "5": -0.000796973705291637,
        "6": 0.028204798698425182,
        "7": 0.0018627047538756214,
        "8": 0.005964696407318004,
        "9": -0.0033453702926635742
      },
      "positive_seeds": 8,
      "zero_seeds": 0
    },
    {
      "architecture": "topk",
      "ci95_lower": -0.4973189369464914,
      "ci95_upper": -0.32696612762908145,
      "control_beta": 0.0,
      "field": "mean_factor_max_positive_cosine",
      "high_beta": 0.5,
      "mean_difference": -0.4091973342001438,
      "n_seeds": 12,
      "negative_seeds": 12,
      "per_seed_difference": {
        "0": -0.4885260611772537,
        "1": -0.317925363779068,
        "10": -0.350929617881775,
        "11": -0.21098150312900543,
        "2": -0.5687944740056994,
        "3": -0.2866421639919281,
        "4": -0.376135990023613,
        "5": -0.5116910636425019,
        "6": -0.24564409255981445,
        "7": -0.5638017803430557,
        "8": -0.27486440539360046,
        "9": -0.714431494474411
      },
      "positive_seeds": 0,
      "zero_seeds": 0
    },
    {
      "architecture": "topk",
      "ci95_lower": -0.5765592853590567,
      "ci95_upper": -0.35798140085725877,
      "control_beta": 0.0,
      "field": "mean_factor_causal_concentration",
      "high_beta": 0.5,
      "mean_difference": -0.47346953516561124,
      "n_seeds": 12,
      "negative_seeds": 12,
      "per_seed_difference": {
        "0": -0.5139406299610995,
        "1": -0.7175409653313869,
        "10": -0.5322644553958011,
        "11": -0.03343259162679457,
        "2": -0.2559230345451572,
        "3": -0.7062644537425367,
        "4": -0.475110324557119,
        "5": -0.4381783141412541,
        "6": -0.2680078084862057,
        "7": -0.6349530393596146,
        "8": -0.5824681535516676,
        "9": -0.5235506512886969
      },
      "positive_seeds": 0,
      "zero_seeds": 0
    },
    {
      "architecture": "topk",
      "ci95_lower": 3.0175062926635916,
      "ci95_upper": 5.870233311723826,
      "control_beta": 0.0,
      "field": "mean_factor_causal_participation_ratio",
      "high_beta": 0.5,
      "mean_difference": 4.423038182895346,
      "n_seeds": 12,
      "negative_seeds": 0,
      "per_seed_difference": {
        "0": 3.30407191743169,
        "1": 8.191427630311523,
        "10": 6.935183698499679,
        "11": 0.13726415891319332,
        "2": 1.4540500833877499,
        "3": 5.561386349623506,
        "4": 8.955527716405669,
        "5": 2.3980238647964693,
        "6": 3.5020791722115754,
        "7": 4.5888427768270885,
        "8": 4.825051972549322,
        "9": 3.2235488537866903
      },
      "positive_seeds": 12,
      "zero_seeds": 0
    },
    {
      "architecture": "topk",
      "ci95_lower": 2.7916666666666665,
      "ci95_upper": 6.541666666666667,
      "control_beta": 0.0,
      "field": "mean_factor_causal_split_count",
      "high_beta": 0.5,
      "mean_difference": 4.666666666666667,
      "n_seeds": 12,
      "negative_seeds": 1,
      "per_seed_difference": {
        "0": 4.0,
        "1": 10.5,
        "10": 8.5,
        "11": -1.0,
        "2": 0.0,
        "3": 6.5,
        "4": 9.0,
        "5": 2.0,
        "6": 4.0,
        "7": 4.5,
        "8": 4.5,
        "9": 3.5
      },
      "positive_seeds": 10,
      "zero_seeds": 1
    },
    {
      "architecture": "topk",
      "ci95_lower": -0.6156548298457679,
      "ci95_upper": -0.36452524836343025,
      "control_beta": 0.0,
      "field": "mean_factor_single_gain",
      "high_beta": 0.5,
      "mean_difference": -0.5027242377483377,
      "n_seeds": 12,
      "negative_seeds": 11,
      "per_seed_difference": {
        "0": -0.5680552173632832,
        "1": -0.7672840514673755,
        "10": -0.5804589081015821,
        "11": 0.08594318827699965,
        "2": -0.3155989298846692,
        "3": -0.7286027346575419,
        "4": -0.5011650030535135,
        "5": -0.4826635143109438,
        "6": -0.30597456235967796,
        "7": -0.6729957359422778,
        "8": -0.6155130046453178,
        "9": -0.5803223794708697
      },
      "positive_seeds": 1,
      "zero_seeds": 0
    },
    {
      "architecture": "topk",
      "ci95_lower": -0.16984184005608158,
      "ci95_upper": -0.1332839298993349,
      "control_beta": 0.0,
      "field": "mean_factor_family_gain",
      "high_beta": 0.5,
      "mean_difference": -0.1513832857211431,
      "n_seeds": 12,
      "negative_seeds": 12,
      "per_seed_difference": {
        "0": -0.150035560131073,
        "1": -0.20034921169281006,
        "10": -0.1912164092063905,
        "11": -0.09218719601631165,
        "2": -0.1150190532207489,
        "3": -0.15106645226478577,
        "4": -0.20073315501213063,
        "5": -0.1320084035396577,
        "6": -0.14438754320144653,
        "7": -0.14383643865585305,
        "8": -0.13055771589279175,
        "9": -0.1652022898197174
      },
      "positive_seeds": 0,
      "zero_seeds": 0
    },
    {
      "architecture": "topk",
      "ci95_lower": 0.06087711441214196,
      "ci95_upper": 0.06682617155505192,
      "control_beta": 0.0,
      "field": "fvu",
      "high_beta": 0.5,
      "mean_difference": 0.06385604602595171,
      "n_seeds": 12,
      "negative_seeds": 0,
      "per_seed_difference": {
        "0": 0.0661379881203175,
        "1": 0.0732031622901559,
        "10": 0.064104923978448,
        "11": 0.061639891937375096,
        "2": 0.05351743195205919,
        "3": 0.063445501960814,
        "4": 0.058306181803345694,
        "5": 0.0611989572644233,
        "6": 0.062035758048296,
        "7": 0.0697642462328077,
        "8": 0.0621878462843597,
        "9": 0.0707306624390185
      },
      "positive_seeds": 12,
      "zero_seeds": 0
    },
    {
      "architecture": "topk",
      "ci95_lower": 0.0,
      "ci95_upper": 0.00046296296296347944,
      "control_beta": 0.0,
      "field": "l0",
      "high_beta": 0.5,
      "mean_difference": 0.00019290123456805475,
      "n_seeds": 12,
      "negative_seeds": 0,
      "per_seed_difference": {
        "0": 0.0,
        "1": 0.0013888888888882178,
        "10": 0.0,
        "11": 0.0,
        "2": 0.0009259259259284391,
        "3": 0.0,
        "4": 0.0,
        "5": 0.0,
        "6": 0.0,
        "7": 0.0,
        "8": 0.0,
        "9": 0.0
      },
      "positive_seeds": 2,
      "zero_seeds": 10
    },
    {
      "architecture": "topk",
      "ci95_lower": 0.11397058823529416,
      "ci95_upper": 0.18750000000000003,
      "control_beta": 0.0,
      "field": "dead_fraction",
      "high_beta": 0.5,
      "mean_difference": 0.1482843137254902,
      "n_seeds": 12,
      "negative_seeds": 0,
      "per_seed_difference": {
        "0": 0.2941176470588236,
        "1": 0.1323529411764706,
        "10": 0.11764705882352938,
        "11": 0.1176470588235295,
        "2": 0.23529411764705888,
        "3": 0.1029411764705883,
        "4": 0.2205882352941176,
        "5": 0.10294117647058829,
        "6": 0.08823529411764709,
        "7": 0.16176470588235292,
        "8": 0.1323529411764706,
        "9": 0.0735294117647059
      },
      "positive_seeds": 12,
      "zero_seeds": 0
    },
    {
      "architecture": "topk",
      "ci95_lower": -45.328213930130005,
      "ci95_upper": -33.15406637191773,
      "control_beta": 0.0,
      "field": "gram_penalty",
      "high_beta": 0.5,
      "mean_difference": -39.20676485697428,
      "n_seeds": 12,
      "negative_seeds": 12,
      "per_seed_difference": {
        "0": -40.246883392333984,
        "1": -48.61344528198243,
        "10": -37.09600067138672,
        "11": -40.97163391113281,
        "2": -23.95171356201172,
        "3": -58.24086761474611,
        "4": -41.446449279785156,
        "5": -27.84540557861328,
        "6": -23.55680465698243,
        "7": -56.8330192565918,
        "8": -39.31796646118165,
        "9": -32.36098861694335
      },
      "positive_seeds": 0,
      "zero_seeds": 0
    },
    {
      "architecture": "topk",
      "ci95_lower": 0.006526186938087145,
      "ci95_upper": 0.022956577812631856,
      "control_beta": 0.0,
      "field": "max_absolute_coherence",
      "high_beta": 0.5,
      "mean_difference": 0.013893504937489809,
      "n_seeds": 12,
      "negative_seeds": 0,
      "per_seed_difference": {
        "0": 0.011498153209686168,
        "1": 0.0007742047309875488,
        "10": 0.00801074504852295,
        "11": 0.0005154013633728027,
        "2": 0.0005484819412232556,
        "3": 0.054025590419769176,
        "4": 0.001008450984954834,
        "5": 0.00789189338684071,
        "6": 0.023115098476410023,
        "7": 0.021053075790405273,
        "8": 0.015238881111144797,
        "9": 0.02304208278656017
      },
      "positive_seeds": 12,
      "zero_seeds": 0
    }
  ],
  "gates": {
    "all_gates_pass": true,
    "conformance": {
      "all_cells_have_12_seeds": true,
      "architectures": true,
      "betas": true,
      "classifier_quality": true,
      "data_hash": true,
      "no_duplicates": true,
      "registered_lambda": true,
      "registered_steps": true,
      "registered_topk": true,
      "row_count": true,
      "seeds": true,
      "widths": true
    },
    "conformance_pass": true,
    "manipulation": {
      "l1": {
        "control_gram": 80.71666081746419,
        "high_gram": 43.67944145202637,
        "high_over_control_ratio": 0.5411452977571107,
        "pass": true
      },
      "topk": {
        "control_gram": 84.18649800618489,
        "high_gram": 44.97973314921061,
        "high_over_control_ratio": 0.5342867824945765,
        "pass": true
      }
    },
    "retention": {
      "l1": {
        "family_gain_ci95_lower": 0.785987739264965,
        "family_gain_ci95_upper": 0.797099400497973,
        "mean_family_cosine": 0.9947632302840551,
        "mean_family_gain": 0.7918708498279253,
        "mean_fvu": 0.03845962850997841,
        "pass": true
      },
      "topk": {
        "family_gain_ci95_lower": 0.8296572292223573,
        "family_gain_ci95_upper": 0.8659790153925617,
        "mean_family_cosine": 0.9844645808140436,
        "mean_family_gain": 0.847875307003657,
        "mean_fvu": 0.07203257332245504,
        "pass": true
      }
    },
    "topk_fixed_l0": true
  },
  "metadata_sha256": "c8dde96fe185acf26f4f7f00eadc50111644d94e5ab796ec8ecc4cedc627668c",
  "metrics_sha256": "376cbc49b00b7652459200dc90b79ce308a5084b83ec7dc8f4635de1dd6ab51b",
  "primary_verdict": "SUPPORTED: strong full-Gram regularization reduced one-atom causal-direction alignment while the causal direction remained recoverable at the decoder-family level in both architectures",
  "splitting_pass": {
    "l1": true,
    "topk": true
  },
  "splitting_verdict": "SUPPORTED IN BOTH ARCHITECTURES",
  "weight_file_count": 120
}
````

# Appendix G — post-hoc robustness report (exploratory)

````markdown
# Post-hoc robustness analysis (exploratory)

These checks were written after the registered verdict and do not change it.

## Condition means

| architecture | beta | gram_excess_above_welch | pairs_cos_lt_neg099 | pairs_cos_gt_099 | random_direction_max_positive_cosine | planted_max_positive_cosine | planted_alignment_excess_over_random | best_contributing_atom_cosine | best_positive_read_atom_cosine | positive_read_gain_sum | negative_release_gain_sum | individual_gain_median | individual_gain_q10 | individual_gain_fraction_gt_050 | individual_cross_gain_abs_mean | split_count_rel_05 | split_count_rel_10 | split_count_rel_20 | split_count_rel_30 | positive_read_split_count_rel_05 | positive_read_split_count_rel_10 | positive_read_split_count_rel_20 | positive_read_split_count_rel_30 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| l1 | 0 | 46.7167 | 1.4167 | 0.0000 | 0.3973 | 0.7082 | 0.3109 | -0.2444 | 0.7075 | 0.4488 | 0.4516 | 0.8981 | 0.8906 | 1.0000 | 0.0133 | 4.8333 | 4.7500 | 4.7500 | 4.5417 | 2.5000 | 2.4583 | 2.4583 | 2.3750 |
| l1 | 0.025 | 4.5934 | 0.0000 | 0.0000 | 0.4064 | 0.8708 | 0.4644 | 0.6067 | 0.7947 | 0.6897 | 0.1850 | 0.8716 | 0.8376 | 1.0000 | 0.0201 | 2.6250 | 2.2917 | 1.9167 | 1.9167 | 1.5833 | 1.5000 | 1.5000 | 1.5000 |
| l1 | 0.0625 | 4.9274 | 0.4167 | 0.0833 | 0.4027 | 0.8179 | 0.4152 | 0.4718 | 0.8166 | 0.5869 | 0.2671 | 0.8502 | 0.7760 | 0.9992 | 0.0132 | 2.0417 | 1.5833 | 1.1667 | 1.1250 | 3.7083 | 2.7917 | 1.8333 | 1.4583 |
| l1 | 0.25 | 7.7816 | 2.5833 | 0.9167 | 0.3980 | 0.4820 | 0.0840 | -0.3578 | 0.4782 | 0.3489 | 0.4509 | 0.7981 | 0.6831 | 0.9972 | 0.0324 | 19.4583 | 11.5000 | 5.8750 | 3.3333 | 14.1250 | 9.2083 | 5.5000 | 3.7083 |
| l1 | 0.5 | 9.6794 | 4.0000 | 2.0833 | 0.3964 | 0.4529 | 0.0565 | -0.4535 | 0.4503 | 0.3527 | 0.4429 | 0.7981 | 0.6785 | 0.9963 | 0.0332 | 23.1250 | 13.6667 | 6.5417 | 4.1250 | 15.6250 | 10.6250 | 6.0833 | 4.1667 |
| topk | 0 | 50.1865 | 0.5833 | 0.0000 | 0.4014 | 0.8958 | 0.4943 | 0.5867 | 0.8532 | 0.8226 | 0.1768 | 0.9999 | 0.9889 | 0.9997 | 0.0025 | 1.4583 | 1.4167 | 1.3333 | 1.2500 | 2.0833 | 1.6667 | 1.3333 | 1.2500 |
| topk | 0.025 | 4.4412 | 2.9167 | 4.4167 | 0.3989 | 0.8470 | 0.4482 | 0.6826 | 0.8320 | 0.8640 | 0.1399 | 0.9981 | 0.9471 | 0.9993 | 0.0108 | 1.3750 | 1.3333 | 1.2083 | 1.2083 | 1.7500 | 1.4583 | 1.2917 | 1.2083 |
| topk | 0.0625 | 5.6898 | 2.2500 | 4.0833 | 0.3968 | 0.7410 | 0.3442 | 0.6002 | 0.7208 | 0.8213 | 0.1794 | 0.9838 | 0.8905 | 0.9983 | 0.0248 | 1.7917 | 1.4167 | 1.2917 | 1.2500 | 2.1667 | 1.7917 | 1.5417 | 1.4583 |
| topk | 0.25 | 9.0856 | 2.0833 | 3.2500 | 0.3955 | 0.4598 | 0.0643 | -0.1065 | 0.3924 | 0.4481 | 0.4898 | 0.8900 | 0.7317 | 0.9889 | 0.0531 | 7.1250 | 4.4583 | 3.0417 | 2.0833 | 6.8750 | 4.6250 | 2.7917 | 2.0000 |
| topk | 0.5 | 10.9797 | 2.1667 | 4.8333 | 0.3938 | 0.4866 | 0.0928 | 0.0207 | 0.4161 | 0.4606 | 0.4355 | 0.8528 | 0.6820 | 0.9789 | 0.0551 | 10.0833 | 6.0833 | 3.2500 | 2.3750 | 7.9583 | 5.5417 | 3.3333 | 2.4583 |

## High-minus-control threshold sensitivity

### L1

- `gram_excess_above_welch`: -37.0372, 95% paired-seed bootstrap CI [-38.6747, -35.2250].
- `pairs_abs_cos_gt_099`: +4.6667, 95% paired-seed bootstrap CI [+3.2500, +6.0833].
- `pairs_cos_lt_neg099`: +2.5833, 95% paired-seed bootstrap CI [+1.4167, +3.8333].
- `random_direction_max_positive_cosine`: -0.0009, 95% paired-seed bootstrap CI [-0.0034, +0.0018].
- `planted_max_positive_cosine`: -0.2553, 95% paired-seed bootstrap CI [-0.3118, -0.2069].
- `planted_alignment_excess_over_random`: -0.2544, 95% paired-seed bootstrap CI [-0.3102, -0.2061].
- `best_contributing_atom_cosine`: -0.2091, 95% paired-seed bootstrap CI [-0.4224, +0.0306].
- `best_positive_read_atom_cosine`: -0.2572, 95% paired-seed bootstrap CI [-0.3162, -0.2058].
- `positive_read_gain_sum`: -0.0961, 95% paired-seed bootstrap CI [-0.1456, -0.0516].
- `negative_release_gain_sum`: -0.0087, 95% paired-seed bootstrap CI [-0.0562, +0.0421].
- `individual_gain_median`: -0.1000, 95% paired-seed bootstrap CI [-0.1070, -0.0941].
- `individual_gain_q10`: -0.2121, 95% paired-seed bootstrap CI [-0.2257, -0.1989].
- `individual_gain_fraction_gt_050`: -0.0037, 95% paired-seed bootstrap CI [-0.0061, -0.0016].
- `individual_cross_gain_abs_mean`: +0.0199, 95% paired-seed bootstrap CI [+0.0171, +0.0236].
- `split_count_rel_05`: +18.2917, 95% paired-seed bootstrap CI [+16.3323, +20.4583].
- `split_count_rel_10`: +8.9167, 95% paired-seed bootstrap CI [+6.9167, +11.0417].
- `split_count_rel_20`: +1.7917, 95% paired-seed bootstrap CI [+0.8333, +2.7917].
- `split_count_rel_30`: -0.4167, 95% paired-seed bootstrap CI [-1.0833, +0.2083].
- `positive_read_split_count_rel_05`: +13.1250, 95% paired-seed bootstrap CI [+11.4167, +15.0833].
- `positive_read_split_count_rel_10`: +8.1667, 95% paired-seed bootstrap CI [+6.5000, +10.2500].
- `positive_read_split_count_rel_20`: +3.6250, 95% paired-seed bootstrap CI [+2.0000, +5.5833].
- `positive_read_split_count_rel_30`: +1.7917, 95% paired-seed bootstrap CI [+0.6667, +3.0833].
- `geometry_above_80`: +0.0000, 95% paired-seed bootstrap CI [+0.0000, +0.0000].
- `geometry_above_90`: +0.0000, 95% paired-seed bootstrap CI [+0.0000, +0.0000].
- `geometry_above_95`: +0.0000, 95% paired-seed bootstrap CI [+0.0000, +0.0000].

### TOPK

- `gram_excess_above_welch`: -39.2068, 95% paired-seed bootstrap CI [-45.6081, -33.2110].
- `pairs_abs_cos_gt_099`: +6.4167, 95% paired-seed bootstrap CI [+4.9167, +7.8333].
- `pairs_cos_lt_neg099`: +1.5833, 95% paired-seed bootstrap CI [+0.8333, +2.3333].
- `random_direction_max_positive_cosine`: -0.0076, 95% paired-seed bootstrap CI [-0.0102, -0.0050].
- `planted_max_positive_cosine`: -0.4092, 95% paired-seed bootstrap CI [-0.4968, -0.3273].
- `planted_alignment_excess_over_random`: -0.4016, 95% paired-seed bootstrap CI [-0.4891, -0.3203].
- `best_contributing_atom_cosine`: -0.5661, 95% paired-seed bootstrap CI [-0.9867, -0.1367].
- `best_positive_read_atom_cosine`: -0.4371, 95% paired-seed bootstrap CI [-0.5834, -0.2917].
- `positive_read_gain_sum`: -0.3619, 95% paired-seed bootstrap CI [-0.5580, -0.1481].
- `negative_release_gain_sum`: +0.2587, 95% paired-seed bootstrap CI [+0.0832, +0.4278].
- `individual_gain_median`: -0.1471, 95% paired-seed bootstrap CI [-0.1666, -0.1281].
- `individual_gain_q10`: -0.3070, 95% paired-seed bootstrap CI [-0.3359, -0.2773].
- `individual_gain_fraction_gt_050`: -0.0208, 95% paired-seed bootstrap CI [-0.0255, -0.0164].
- `individual_cross_gain_abs_mean`: +0.0525, 95% paired-seed bootstrap CI [+0.0474, +0.0576].
- `split_count_rel_05`: +8.6250, 95% paired-seed bootstrap CI [+6.1667, +11.0000].
- `split_count_rel_10`: +4.6667, 95% paired-seed bootstrap CI [+2.7917, +6.5417].
- `split_count_rel_20`: +1.9167, 95% paired-seed bootstrap CI [+0.7083, +3.1667].
- `split_count_rel_30`: +1.1250, 95% paired-seed bootstrap CI [+0.3333, +2.0000].
- `positive_read_split_count_rel_05`: +5.8750, 95% paired-seed bootstrap CI [+3.1667, +8.5833].
- `positive_read_split_count_rel_10`: +3.8750, 95% paired-seed bootstrap CI [+1.7500, +6.0833].
- `positive_read_split_count_rel_20`: +2.0000, 95% paired-seed bootstrap CI [+0.8333, +3.2917].
- `positive_read_split_count_rel_30`: +1.2083, 95% paired-seed bootstrap CI [+0.3333, +2.2083].
- `geometry_above_80`: -0.8333, 95% paired-seed bootstrap CI [-0.9583, -0.7083].
- `geometry_above_90`: -0.6667, 95% paired-seed bootstrap CI [-0.8750, -0.4583].
- `geometry_above_95`: -0.6667, 95% paired-seed bootstrap CI [-0.8750, -0.4583].

## Exact frame-potential reference

For unit columns in R^{d×m}, the Gram-sum floor is m(m−d)/(2d). Here d=34 and m=68, so the exact floor is 34. The signed duplicated basis [I,−I] attains that floor while having maximum absolute coherence 1. Thus a lower Gram sum does not imply lower mutual coherence; near-antipodal-pair counts above diagnose this known tight-frame degeneracy.
````

# Appendix H — complete registered run table (120 rows)

````csv
seed,beta,architecture,d,m,fvu,l0,dead_fraction,gram_penalty,mean_squared_coherence,max_absolute_coherence,factor1_max_positive_cosine,factor1_max_absolute_cosine,factor1_faithful_geometry,factor1_causal_concentration,factor1_causal_participation_ratio,factor1_causal_split_count,factor1_single_gain,factor1_family_gain,factor1_family_norm_ratio,factor1_family_cosine,factor1_nnls_residual,factor1_nnls_cosine,factor2_max_positive_cosine,factor2_max_absolute_cosine,factor2_faithful_geometry,factor2_causal_concentration,factor2_causal_participation_ratio,factor2_causal_split_count,factor2_single_gain,factor2_family_gain,factor2_family_norm_ratio,factor2_family_cosine,factor2_nnls_residual,factor2_nnls_cosine,mean_factor_max_positive_cosine,mean_factor_max_absolute_cosine,mean_factor_causal_concentration,mean_factor_causal_participation_ratio,mean_factor_causal_split_count,mean_factor_single_gain,mean_factor_family_gain,mean_factor_family_norm_ratio,mean_factor_family_cosine,mean_factor_nnls_residual,mean_factor_nnls_cosine,both_faithful_geometry,train_reconstruction_loss_last_batch,train_l1_last_batch,train_gram_last_step,train_total_last_batch,train_gradient_norm_last_batch,wall_seconds
0,0.0,l1,34,68,0.03115667589008808,15.822222222222223,0.0,76.50013732910156,0.03358215093612671,0.9991393685340881,0.7119869589805603,0.7382254600524902,False,0.25500770233824016,4.021991850481842,4,0.2325044297308955,0.9115447402000427,0.9129431247711182,0.998468279838562,0.0,0.9999999996613543,0.7083911895751953,0.7083911895751953,False,0.26178513845722756,4.037649311806077,4,0.23204075248603598,0.885959267616272,0.8879646062850952,0.9977416396141052,0.0,1.0000000193237484,0.7101890742778778,0.7233083248138428,0.25839642039773386,4.02982058114396,4.0,0.23227259110846574,0.8987520039081573,0.9004538655281067,0.9981049597263336,0.0,1.0000000094925514,False,0.4804009199142456,8.971924781799316,76.50149536132812,2.274785876274109,0.5524594788918792,3.0088446140289307
0,0.025,l1,34,68,0.029225526377558708,19.19074074074074,0.0,38.98259353637695,0.01711263880133629,0.966310977935791,0.9930272102355957,0.9930272102355957,True,0.9492347677136554,1.109514755595387,1,0.8190028766996275,0.8623124361038208,0.8637331128120422,0.9983552098274231,0.0,0.9999999996613543,0.9820939898490906,0.9820939898490906,True,0.8861042263068379,1.2627600051273868,1,0.7581289065866047,0.8547228574752808,0.8563507795333862,0.9980990290641785,0.0,1.0000000193237484,0.9875606000423431,0.9875606000423431,0.9176694970102467,1.1861373803613868,1.0,0.7885658916431161,0.8585176467895508,0.8600419461727142,0.9982271194458008,0.0,1.0000000094925514,True,0.5278568267822266,10.519781112670898,38.98217010498047,3.606367301940918,0.6830439829609694,3.057713508605957
0,0.0625,l1,34,68,0.032387230545282364,22.975,0.0,39.97911834716797,0.017550095915794373,0.9895856380462646,0.9794695377349854,0.9794695377349854,True,0.8631671516411837,1.3403257217920101,1,0.737230128223609,0.8534244894981384,0.8542472720146179,0.9990367889404297,0.0,0.9999999996613543,0.9813901782035828,0.9813901782035828,True,0.8826832550282676,1.2822857206400895,1,0.7607098782020664,0.8617911338806152,0.8622041344642639,0.9995209574699402,0.0,1.0000000193237484,0.9804298579692841,0.9804298579692841,0.8729252033347257,1.31130572121605,1.0,0.7489700032128377,0.8576078116893768,0.8582257032394409,0.9992788732051849,0.0,1.0000000094925514,True,0.6158707141876221,11.517374992370605,39.97892761230469,5.418028688430786,1.3618714232391502,3.167677402496338
0,0.25,l1,34,68,0.04155101627111435,28.91111111111111,0.0,44.11572265625,0.019365988671779633,0.9998412728309631,0.3948444426059723,0.5457249283790588,False,0.2635747324546569,10.09914942042629,8,0.19859329939262754,0.7503204345703125,0.7533237338066101,0.9960132837295532,0.0,0.9999999996613542,0.6065423488616943,0.6156959533691406,False,0.200504700284577,10.412271107132238,11,0.1556267565089911,0.7760699391365051,0.780985951423645,0.9937053322792053,0.0,1.0000000193237484,0.5006933957338333,0.5807104408740997,0.23203971636961696,10.255710263779264,9.5,0.17711002795080932,0.7631951868534088,0.7671548426151276,0.9948593080043793,0.0,1.0000000094925512,False,0.8802008032798767,15.464214324951172,44.115577697753906,15.001938092708588,6.679248226721363,2.8287246227264404
0,0.5,l1,34,68,0.04484923928976059,30.621296296296297,0.0,46.44683074951172,0.02038930170238018,0.9977525472640991,0.40038713812828064,0.4827401340007782,False,0.18018344162978506,13.703790735259709,13,0.1381754795557547,0.7582778334617615,0.761982798576355,0.9951377511024475,0.10902617456123112,0.9940388788086976,0.5932732224464417,0.6034247875213623,False,0.19490048701938817,11.091286587426845,14,0.15276513078437562,0.7808624505996704,0.7856085300445557,0.9939587116241455,0.10753587247377513,0.9942012244906969,0.49683018028736115,0.5430824607610703,0.1875419643245866,12.397538661343276,13.5,0.14547030517006515,0.7695701420307159,0.7737956643104553,0.9945482313632965,0.10828102351750313,0.9941200516496973,False,1.025000810623169,17.550722122192383,46.446632385253906,27.758461427688598,14.258762045670034,3.250957727432251
1,0.0,l1,34,68,0.03442244231700897,15.350462962962963,0.0,84.54144287109375,0.03711213544011116,0.9989596605300903,0.7158995866775513,0.7288922071456909,False,0.2548387558118603,4.01887470802113,4,0.23266712805454173,0.9126714468002319,0.914181113243103,0.998348593711853,0.0,0.9999999996613543,0.7006136775016785,0.7078407406806946,False,0.2556089351293467,4.017513069058994,4,0.22640490970792088,0.8853846788406372,0.8874367475509644,0.9976876974105835,0.0,1.0000000193237486,0.7082566320896149,0.7183664739131927,0.2552238454706035,4.018193888540062,4.0,0.22953601888123132,0.8990280628204346,0.9008089303970337,0.9980181455612183,0.0,1.0000000094925514,False,0.523996889591217,8.598848342895508,84.54096221923828,2.243766558170319,0.4907600054121,2.8987932205200195
1,0.025,l1,34,68,0.028783222660422325,20.0,0.0,37.96098327636719,0.0166641715914011,0.9679754376411438,0.9901674389839172,0.9901674389839172,True,0.8950270810758062,1.2458321690645333,1,0.7727571010860318,0.8631122708320618,0.8634767532348633,0.9995778799057007,0.0,0.9999999996613543,0.9854455590248108,0.9854455590248108,True,0.9225088429080748,1.174256685849419,1,0.7874353688945402,0.8526490926742554,0.8552117347717285,0.9970035552978516,0.0,1.0000000193237484,0.987806499004364,0.987806499004364,0.9087679619919404,1.2100444274569762,1.0,0.780096234990286,0.8578806817531586,0.8593442440032959,0.9982907176017761,0.0,1.0000000094925514,True,0.547458291053772,10.499405860900879,37.960636138916016,3.596355366706848,0.5995782293080603,2.874799966812134
1,0.0625,l1,34,68,0.03098113089799881,23.075,0.0,40.54355239868164,0.01779787242412567,0.9807746410369873,0.946742832660675,0.946742832660675,True,0.7665806809088718,1.6891240064241593,1,0.6549776103627312,0.85411137342453,0.8546697497367859,0.9993466734886169,0.0,0.9999999996613543,0.5821864008903503,0.9403030872344971,False,0.7133576692767016,1.9337576072144462,1,0.6085302237941497,0.8529847860336304,0.853687047958374,0.9991773366928101,0.0,1.0000000193237484,0.7644646167755127,0.9435229599475861,0.7399691750927867,1.8114408068193026,1.0,0.6317539170784404,0.8535480797290802,0.85417839884758,0.9992620050907135,0.0,1.0000000094925514,False,0.6048873662948608,11.382646560668945,40.543434143066406,5.4153813123703,1.3306892332203129,2.8768763542175293
1,0.25,l1,34,68,0.03870219737291336,28.825,0.0,42.36759948730469,0.01859859749674797,0.9980301260948181,0.4711529612541199,0.4711529612541199,False,0.10295708614208432,21.6408247335139,27,0.08029608499397163,0.7792827486991882,0.7839467525482178,0.9940506219863892,0.0,0.9999999996613542,0.5890513062477112,0.6341701149940491,False,0.2200761654999359,10.239722789288008,9,0.17325640465175451,0.7871564626693726,0.7912053465843201,0.9948827028274536,0.0,1.0000000193237484,0.5301021337509155,0.5526615381240845,0.16151662582101012,15.940273761400952,18.0,0.12677624482286307,0.7832196056842804,0.7875760495662689,0.9944666624069214,0.0,1.0000000094925512,False,0.787746787071228,15.475296020507812,42.36729431152344,14.47462956905365,5.924232299780357,3.2677719593048096
1,0.5,l1,34,68,0.04715966805815697,31.02037037037037,0.0,42.36481475830078,0.018597371876239777,0.9999781250953674,0.4475782811641693,0.4475782811641693,False,0.10814273666901866,19.460397669360688,21,0.08328037834657614,0.7700967192649841,0.7751826047897339,0.9934391975402832,0.0,0.9999999996613542,0.5803768634796143,0.6005921363830566,False,0.18919916619106147,12.137423903731412,13,0.1531293402358365,0.8093522787094116,0.813128650188446,0.9953557848930359,0.0,1.0000000193237482,0.5139775723218918,0.524085208773613,0.14867095143004005,15.798910786546049,17.0,0.11820485929120632,0.7897244989871979,0.79415562748909,0.9943974912166595,0.0,1.0000000094925512,False,0.8709402680397034,17.472061157226562,42.36444854736328,25.547576773166657,11.810943008627616,3.222871780395508
2,0.0,l1,34,68,0.03302038460969925,15.567592592592593,0.0,79.57963562011719,0.034933991730213165,0.9995424747467041,0.715446949005127,0.7290830612182617,False,0.2541122777938225,4.018466030594049,4,0.23174482481968617,0.9117298722267151,0.913142204284668,0.9984533190727234,0.0,0.9999999996613542,0.7034987211227417,0.7043306231498718,False,0.2554750227428217,4.029464505604395,4,0.2263169420046462,0.8855193853378296,0.8875319957733154,0.9977323412895203,0.0,1.0000000193237482,0.7094728350639343,0.7167068421840668,0.2547936502683221,4.0239652680992215,4.0,0.22903088341216618,0.8986246287822723,0.9003371000289917,0.9980928301811218,0.0,1.0000000094925512,False,0.4949897527694702,8.882467269897461,79.58389282226562,2.2714832067489628,0.5376069005748259,3.3028724193573
2,0.025,l1,34,68,0.027663638815283775,19.428703703703704,0.0,38.04624938964844,0.016701601445674896,0.9687323570251465,0.9895217418670654,0.9895217418670654,True,0.9033146851524226,1.2223827866295653,1,0.783472150335567,0.8672257661819458,0.8677381873130798,0.9994094967842102,0.0,0.9999999996613541,0.9744690656661987,0.9744690656661987,True,0.6103601159412971,1.9991941003825866,2,0.5250750281053418,0.8601657748222351,0.8603565692901611,0.9997782707214355,0.0,1.0000000193237484,0.9819954037666321,0.9819954037666321,0.7568374005468599,1.610788443506076,1.5,0.6542735892204544,0.8636957705020905,0.8640473783016205,0.9995938837528229,0.0,1.0000000094925512,True,0.5060085654258728,10.599440574645996,38.04593276977539,3.5770449995994573,0.6247183865649214,2.7274763584136963
2,0.0625,l1,34,68,0.03231913223862648,23.537037037037038,0.0,39.90963363647461,0.017519593238830566,0.9984486103057861,0.937366783618927,0.937366783618927,True,0.7406845568795196,1.7978675594252838,1,0.6258326284869531,0.844559371471405,0.8456260561943054,0.9987385272979736,0.0,0.9999999996613542,0.9076617360115051,0.9076617360115051,True,0.6358365429248417,2.328391536416476,3,0.5355942563758217,0.8422510027885437,0.8432052135467529,0.9988684058189392,0.0,1.0000000193237484,0.9225142598152161,0.9225142598152161,0.6882605499021807,2.0631295479208798,2.0,0.5807134424313873,0.8434051871299744,0.8444156348705292,0.9988034665584564,0.0,1.0000000094925512,True,0.6368535757064819,11.591185569763184,39.90934753417969,5.44942491054535,1.3121720037060018,3.0144853591918945
2,0.25,l1,34,68,0.03720530495047569,29.28935185185185,0.0,42.20197677612305,0.01852588914334774,0.9958153367042542,0.3256435692310333,0.6204205751419067,False,0.36265138874844927,6.556546148348813,7,0.2961600640043905,0.7871782183647156,0.7904952168464661,0.995803952217102,0.0,0.9999999996613542,0.5978811383247375,0.6294829845428467,False,0.21163934254376418,10.890828789613218,12,0.16929232757910884,0.7998669743537903,0.8041568398475647,0.9946653842926025,0.0,1.0000000193237482,0.46176235377788544,0.6249517798423767,0.2871453656461067,8.723687468981016,9.5,0.23272619579174966,0.7935225963592529,0.7973260283470154,0.9952346682548523,0.0,1.0000000094925512,False,0.7879563570022583,15.828533172607422,42.20195388793945,14.504151463508606,5.855303720763639,3.2542152404785156
2,0.5,l1,34,68,0.03609302267432213,29.3875,0.0,44.532325744628906,0.019548870623111725,0.9985727667808533,0.3598935008049011,0.5778104066848755,False,0.29603364116631303,8.731489155930184,7,0.23552955239652695,0.7856684327125549,0.7897156476974487,0.9948750734329224,0.0,0.9999999996613542,0.5911933779716492,0.6108646988868713,False,0.20176670351777487,10.767553357928755,11,0.15853515126332085,0.7856347560882568,0.7910385131835938,0.9931687712669373,0.0,1.0000000193237484,0.47554343938827515,0.5943375527858734,0.24890017234204395,9.74952125692947,9.0,0.1970323518299239,0.7856515944004059,0.7903770804405212,0.9940219223499298,0.0,1.0000000094925512,False,0.7982168793678284,17.274221420288086,44.532554626464844,26.519338476657868,12.74329379892913,3.2789018154144287
3,0.0,l1,34,68,0.03347890451550484,15.639814814814814,0.0,80.70197296142578,0.03542667627334595,0.9986735582351685,0.7261320948600769,0.7261320948600769,False,0.25379145876694736,4.770148812066053,6,0.23214495208735023,0.9144251942634583,0.9158620834350586,0.9984311461448669,0.0,0.9999999996613542,0.6927481293678284,0.7249012589454651,False,0.24877643932744295,4.864661976027015,6,0.22105089899958,0.8882564306259155,0.8900742530822754,0.997957706451416,0.0,1.0000000193237484,0.7094401121139526,0.725516676902771,0.25128394904719514,4.817405394046534,6.0,0.2265979255434651,0.9013408124446869,0.902968168258667,0.9981944262981415,0.0,1.0000000094925512,False,0.4983399510383606,8.771659851074219,80.69985961914062,2.2526719212532047,0.49798519767068067,3.208296298980713
3,0.025,l1,34,68,0.028095411136746407,18.878703703703703,0.0,38.38547134399414,0.016850514337420464,0.9807395935058594,0.9851831197738647,0.9851831197738647,True,0.4583062902156238,2.394644204691637,3,0.4050158042384381,0.883599579334259,0.8848826885223389,0.9985499978065491,0.0,0.9999999996613543,0.17351101338863373,0.9881771802902222,False,0.46920141890991357,2.3089932188561604,3,0.41666228092627794,0.8878608345985413,0.8890591859817505,0.9986521601676941,0.0,1.0000000193237484,0.5793470665812492,0.9866801500320435,0.4637538545627687,2.3518187117738987,3.0,0.41083904258235804,0.8857302069664001,0.8869709372520447,0.9986010789871216,0.0,1.0000000094925514,False,0.514467716217041,10.139835357666016,38.38520431518555,3.502064895629883,0.606626720370439,3.2686054706573486
3,0.0625,l1,34,68,0.03047356940805912,24.411574074074075,0.0,36.86210632324219,0.016181785613298416,0.9894459247589111,0.9528346061706543,0.9528346061706543,True,0.7680396032062938,1.6841701217490508,1,0.6571446186645984,0.8555107116699219,0.8559209108352661,0.9995207786560059,0.0,0.9999999996613543,0.46391230821609497,0.9394170045852661,False,0.7188706042246429,1.8749935388079868,2,0.6187541233613071,0.8607062101364136,0.8609644770622253,0.9997000098228455,0.0,1.0000000193237484,0.7083734571933746,0.9461258053779602,0.7434551037154684,1.7795818302785187,1.5,0.6379493710129527,0.8581084609031677,0.8584426939487457,0.9996103942394257,0.0,1.0000000094925514,False,0.5973402261734009,11.787782669067383,36.86183547973633,5.258761477470398,1.0843513845307444,3.1491639614105225
3,0.25,l1,34,68,0.030457019805908203,28.635185185185186,0.0,41.938751220703125,0.01841033808887005,0.9987722039222717,0.3505965769290924,0.6173732280731201,False,0.3267877518388419,7.826824661528227,8,0.26682684801456935,0.807798445224762,0.811833918094635,0.9950291514396667,0.0,0.9999999996613543,0.644977331161499,0.644977331161499,False,0.22616528392432264,9.514830446914559,12,0.1830392478110497,0.7985638380050659,0.804480254650116,0.9926456809043884,0.0,1.0000000193237484,0.4977869540452957,0.6311752796173096,0.2764765178815823,8.670827554221393,10.0,0.22493304791280952,0.8031811416149139,0.8081570863723755,0.9938374161720276,0.0,1.0000000094925514,False,0.6120431423187256,16.032268524169922,41.93833923339844,14.30308165550232,5.729632993163557,3.269376516342163
3,0.5,l1,34,68,0.03163038194179535,29.368518518518517,0.0,41.572998046875,0.01824978180229664,0.9999991655349731,0.4299202859401703,0.4366992115974426,False,0.13431034684989307,17.56920293470456,22,0.10607942680995247,0.7896839380264282,0.7964625954627991,0.991489052772522,0.0,0.9999999996613542,0.5889379978179932,0.6221513152122498,False,0.19903196235727721,10.809698045789979,13,0.16008743382756302,0.8042912483215332,0.8092395663261414,0.9938852190971375,0.0,1.0000000193237484,0.5094291418790817,0.5294252634048462,0.16667115460358514,14.18945049024727,17.5,0.13308343031875774,0.7969875931739807,0.8028510808944702,0.9926871359348297,0.0,1.0000000094925512,False,0.6264950037002563,17.743873596191406,41.57266616821289,24.961602807044983,11.390525475011087,3.301532506942749
4,0.0,l1,34,68,0.03058278188109398,16.001851851851853,0.0,78.00212097167969,0.03424149006605148,0.9985491037368774,0.7046999335289001,0.7359891533851624,False,0.25606711851896463,4.587624884263698,5,0.23361614504041442,0.9121134877204895,0.913329541683197,0.9986685514450073,0.0,0.9999999996613542,0.7022187113761902,0.7027680277824402,False,0.25831871636060105,4.660286448996762,5,0.22965146900474148,0.888690173625946,0.890474796295166,0.9979957938194275,0.0,1.0000000193237484,0.7034593224525452,0.7193785905838013,0.25719291743978284,4.62395566663023,5.0,0.23163380702257796,0.9004018306732178,0.9019021689891815,0.9983321726322174,0.0,1.0000000094925512,False,0.470912903547287,8.731273651123047,78.00148010253906,2.217167633771896,0.49346591025924685,3.277071952819824
4,0.025,l1,34,68,0.028454788029193878,20.091203703703705,0.0,38.184635162353516,0.016762351617217064,0.9630919694900513,0.9939770102500916,0.9939770102500916,True,0.9404763106582288,1.130102536924031,1,0.8109503378990022,0.8616873621940613,0.8629449605941772,0.9985426664352417,0.0,0.9999999996613541,0.9817101359367371,0.9817101359367371,True,0.8731861916528848,1.2988761082506686,1,0.7459489534957918,0.8534830808639526,0.8549104928970337,0.9983304142951965,0.0,1.0000000193237484,0.9878435730934143,0.9878435730934143,0.9068312511555567,1.2144893225873497,1.0,0.778449645697397,0.857585221529007,0.8589277267456055,0.9984365403652191,0.0,1.0000000094925512,True,0.5249856114387512,10.392784118652344,38.184356689453125,3.5581513524055484,0.5850368054120938,3.219940662384033
4,0.0625,l1,34,68,0.03002292662858963,25.10324074074074,0.0,37.93595886230469,0.016653185710310936,0.9900674819946289,0.9708212018013,0.9708212018013,True,0.8445161418812611,1.400100713217347,1,0.7280882753306855,0.8616708517074585,0.862195611000061,0.9993913769721985,0.0,0.9999999996613542,0.7613198757171631,0.7613198757171631,False,0.3045942685258744,6.393798898363635,7,0.24731620639818694,0.8118867874145508,0.8140706419944763,0.9973174333572388,0.0,1.0000000193237482,0.8660705387592316,0.8660705387592316,0.5745552052035677,3.8969498057904914,4.0,0.48770224086443625,0.8367788195610046,0.8381331264972687,0.9983544051647186,0.0,1.0000000094925512,False,0.5912991166114807,11.604270935058594,37.935447692871094,5.283118784427643,1.1286088388163622,2.916499614715576
4,0.25,l1,34,68,0.03301478549838066,29.55787037037037,0.0,40.085426330566406,0.017596762627363205,0.9935413002967834,0.4229179322719574,0.4622076749801636,False,0.13687989133917355,17.106690938015998,20,0.10849694141526657,0.7908087968826294,0.7952607870101929,0.9944018721580505,0.0,0.9999999996613543,0.5757848024368286,0.620714545249939,False,0.1952392661594436,11.198122577658259,12,0.15889002687427312,0.8097798228263855,0.812475323677063,0.996682345867157,0.0,1.0000000193237484,0.499351367354393,0.5414611101150513,0.16605957874930857,14.152406757837127,16.0,0.13369348414476984,0.8002943098545074,0.8038680553436279,0.9955421090126038,0.0,1.0000000094925514,False,0.6889669895172119,15.535964012145996,40.085479736328125,13.817529726028443,5.18083159486384,2.915076494216919
4,0.5,l1,34,68,0.03523099049925804,29.94675925925926,0.0,43.121604919433594,0.01892958953976631,0.9994137287139893,0.44491690397262573,0.44491690397262573,False,0.10354519363258967,21.848459800068373,30,0.08229130071689486,0.7946659922599792,0.8002333641052246,0.9930427670478821,0.0,0.9999999996613541,0.5661842823028564,0.6117243766784668,False,0.1906951011195124,11.44852367509728,12,0.15623301690249705,0.8138532042503357,0.8169108033180237,0.9962571263313293,0.0,1.0000000193237482,0.5055505931377411,0.5283206403255463,0.14712014737605103,16.648491737582827,21.0,0.11926215880969596,0.8042595982551575,0.8085720837116241,0.9946499466896057,0.0,1.0000000094925512,False,0.7295238375663757,16.67465591430664,43.121707916259766,25.625308978557587,12.12365855786746,2.9128730297088623
5,0.0,l1,34,68,0.034010838717222214,15.64537037037037,0.0,79.0263442993164,0.03469110652804375,0.9982181191444397,0.7230203747749329,0.7230203747749329,False,0.2537044763107759,4.603858069028965,5,0.23208735180955914,0.9146311283111572,0.9160345792770386,0.9984679222106934,0.0,0.9999999996613543,0.6921268701553345,0.6921268701553345,False,0.246288536424133,4.706268242450269,5,0.21907879326679305,0.8891122341156006,0.891040563583374,0.9978358745574951,0.0,1.0000000193237484,0.7075736224651337,0.7075736224651337,0.24999650636745446,4.655063155739617,5.0,0.2255830725381761,0.9018716812133789,0.9035375714302063,0.9981518983840942,0.0,1.0000000094925514,False,0.47718101739883423,8.740472793579102,79.02300262451172,2.2252755761146545,0.4751460819127036,2.9593331813812256
5,0.025,l1,34,68,0.028681371361017227,19.119907407407407,0.0,40.0026969909668,0.017560448497533798,0.9810360074043274,0.9935624599456787,0.9935624599456787,True,0.9536454276949184,1.099225925567356,1,0.825428152747711,0.8650147318840027,0.8663485050201416,0.9984604716300964,0.0,0.9999999996613542,0.9713125228881836,0.9713125228881836,True,0.8712500243594317,1.2983775230660575,2,0.7390856358204169,0.847556471824646,0.8494159579277039,0.9978108406066895,0.0,1.0000000193237484,0.9824374914169312,0.9824374914169312,0.912447726027175,1.1988017243167066,1.5,0.782256894284064,0.8562856018543243,0.8578822314739227,0.9981356561183929,0.0,1.0000000094925512,True,0.5332987308502197,10.323701858520508,40.00188446044922,3.5980862140655523,0.6431659978542928,2.9242329597473145
5,0.0625,l1,34,68,0.03009594790637493,23.741203703703704,0.0,38.515647888183594,0.01690766029059887,0.990959644317627,0.9592710733413696,0.9592710733413696,True,0.7978177617220891,1.564498441562413,1,0.6838845643314643,0.8568770885467529,0.8572434186935425,0.9995726943016052,0.0,0.9999999996613542,0.9122436046600342,0.9122436046600342,True,0.6473702610294905,2.2712955692692827,3,0.5461410768764254,0.8435890078544617,0.8438557982444763,0.9996839165687561,0.0,1.0000000193237484,0.9357573390007019,0.9357573390007019,0.7225940113757898,1.9178970054158477,2.0,0.6150128206039449,0.8502330482006073,0.8505496084690094,0.9996283054351807,0.0,1.0000000094925512,True,0.6126154661178589,11.299117088317871,38.51576614379883,5.2796742677688595,1.2129800005515654,2.930858612060547
5,0.25,l1,34,68,0.03582743555307388,29.620833333333334,0.0,39.95549011230469,0.017539722844958305,0.9961584210395813,0.5155916810035706,0.5155916810035706,False,0.19230885509797466,14.237321705065797,11,0.15214585292774327,0.7909836769104004,0.7952126860618591,0.9946819543838501,0.0,0.9999999996613542,0.5992666482925415,0.6195282936096191,False,0.19795068567900487,10.611960327567939,12,0.15777583585090804,0.795969545841217,0.8009635210037231,0.9937649965286255,0.0,1.0000000193237482,0.557429164648056,0.5675599873065948,0.19512977038848978,12.424641016316869,11.5,0.15496084438932567,0.7934766113758087,0.7980881035327911,0.9942234754562378,0.0,1.0000000094925512,False,0.786101222038269,15.901519775390625,39.95591735839844,13.955384516716004,5.302605126680196,2.732524871826172
5,0.5,l1,34,68,0.0386076420545578,30.934722222222224,0.0,40.94377899169922,0.017973564565181732,0.997421145439148,0.5072497129440308,0.5072497129440308,False,0.2012290399504958,14.511260110755417,11,0.15971747433104017,0.7935451865196228,0.7981774210929871,0.9941964745521545,0.0,0.9999999996613543,0.35217204689979553,0.657745897769928,False,0.38498209792561766,6.03167149181021,5,0.30605241757050855,0.7945283651351929,0.7973892688751221,0.9964121580123901,0.0,1.0000000193237482,0.42971087992191315,0.5824978053569794,0.2931055689380567,10.271465801282814,8.0,0.23288494595077436,0.7940367758274078,0.7977833449840546,0.9953043162822723,0.0,1.0000000094925512,False,0.8752895593643188,17.716991424560547,40.94409942626953,24.890737557411192,11.155016062019149,2.880324363708496
6,0.0,l1,34,68,0.032868675887584686,15.802314814814816,0.0,82.21036529541016,0.03608883544802666,0.9716506600379944,0.7069792151451111,0.7307925820350647,False,0.255059576361938,5.2890422242727855,6,0.23383105297460613,0.9165897369384766,0.9177618026733398,0.9987229108810425,0.0,0.9999999996613541,0.7009381055831909,0.7009381055831909,False,0.2553074997164675,5.377789379920024,6,0.22760049980669467,0.8910347819328308,0.8928291201591492,0.9979903101921082,0.0,1.0000000193237484,0.703958660364151,0.7158653438091278,0.25518353803920274,5.333415802096405,6.0,0.23071577639065038,0.9038122594356537,0.9052954614162445,0.9983566105365753,0.0,1.0000000094925512,False,0.5176427960395813,8.841585159301758,82.21116638183594,2.2859598278999327,0.5388881344766434,2.8738815784454346
6,0.025,l1,34,68,0.028508052229881287,18.14027777777778,0.0,38.17319107055664,0.01675732620060444,0.9716611504554749,0.9894805550575256,0.9894805550575256,True,0.47092020424183334,2.304428080529985,3,0.4168643710516856,0.8850938081741333,0.8862755298614502,0.9986666440963745,0.0,0.9999999996613542,0.23207920789718628,0.989015519618988,False,0.45967220473456094,2.3791258208146537,3,0.40547349185302467,0.8820033073425293,0.8830443024635315,0.9988211393356323,0.0,1.0000000193237484,0.610779881477356,0.9892480373382568,0.46529620448819714,2.3417769506723194,3.0,0.4111689314523551,0.8835485577583313,0.8846599161624908,0.9987438917160034,0.0,1.0000000094925512,False,0.5555747151374817,10.219930648803711,38.17310333251953,3.5538884282112124,0.6343710589132303,2.841855049133301
6,0.0625,l1,34,68,0.028591882437467575,23.512962962962963,0.0,39.21889114379883,0.01721636764705181,0.9930116534233093,0.9837068319320679,0.9837068319320679,True,0.8911761834822025,1.2580905853671265,1,0.7597116863516531,0.8523554801940918,0.8526614308357239,0.9996411800384521,0.0,0.9999999996613542,0.24646465480327606,0.9589547514915466,False,0.8036062567148968,1.5387720870686215,1,0.6851507721711555,0.8523848652839661,0.8534486889839172,0.9987534880638123,0.0,1.0000000193237482,0.615085743367672,0.9713307917118073,0.8473912200985496,1.398431336217874,1.0,0.7224312292614044,0.8523701727390289,0.8530550599098206,0.9991973340511322,0.0,1.0000000094925512,False,0.6089239120483398,11.729178428649902,39.2191047668457,5.405953645706177,1.2616449612134406,3.237710475921631
6,0.25,l1,34,68,0.03135727345943451,29.176388888888887,0.0,40.868255615234375,0.01794041134417057,0.9999995231628418,0.44336724281311035,0.45663440227508545,False,0.12022345094096623,17.180144264020733,19,0.09525224169899137,0.7922781109809875,0.7968101501464844,0.9943122267723083,0.0,0.9999999996613541,0.6039478778839111,0.6105127334594727,False,0.19413321594327773,10.790317553715921,14,0.15477834534626891,0.7972493171691895,0.8020128607749939,0.9940605759620667,0.0,1.0000000193237482,0.5236575603485107,0.533573567867279,0.15717833344212198,13.985230908868328,16.5,0.12501529352263013,0.7947637140750885,0.7994115054607391,0.9941864013671875,0.0,1.0000000094925512,False,0.7474764585494995,15.893566131591797,40.86805725097656,14.143203997612,5.485703139189143,3.239243745803833
6,0.5,l1,34,68,0.03435404598712921,29.683796296296297,0.0,44.74092102050781,0.019640440121293068,0.9998554587364197,0.43577566742897034,0.4507933557033539,False,0.11013399126652561,18.91230219228421,24,0.08702360776834282,0.7901557683944702,0.79520183801651,0.9936543703079224,0.0,0.9999999996613542,0.5913683176040649,0.6019812822341919,False,0.18898185391236189,11.488382046162219,13,0.15257691663576683,0.8073601722717285,0.8116675019264221,0.9946932196617126,0.0,1.0000000193237486,0.5135719925165176,0.5263873189687729,0.14955792258944375,15.200342119223214,18.5,0.11980026220205484,0.7987579703330994,0.8034346699714661,0.9941737949848175,0.0,1.0000000094925514,False,0.832960844039917,17.42762565612793,44.74091339111328,26.688942670822144,12.950379811841858,2.824516773223877
7,0.0,l1,34,68,0.03229885175824165,15.857407407407408,0.0,81.4818115234375,0.035769011825323105,0.9981176257133484,0.7218009829521179,0.7218009829521179,False,0.2551304385050658,4.800821835704672,6,0.23322202736845754,0.9138239026069641,0.9152774810791016,0.9984118938446045,0.0,0.9999999996613543,0.6917845010757446,0.7046850323677063,False,0.24872604886122535,4.919672063084879,6,0.22125714193531024,0.8891799449920654,0.8908704519271851,0.9981024265289307,0.0,1.0000000193237484,0.7067927420139313,0.7132430076599121,0.2519282436831456,4.860246949394775,6.0,0.22723958465188387,0.9015019237995148,0.9030739665031433,0.9982571601867676,0.0,1.0000000094925514,False,0.5273082256317139,8.779970169067383,81.48348236083984,2.2833022594451906,0.5112944226399657,3.1896779537200928
7,0.025,l1,34,68,0.028245124965906143,18.99861111111111,0.0,39.4333381652832,0.017310509458184242,0.9649950861930847,0.9799938201904297,0.9799938201904297,True,0.4477461738202194,2.485582384836875,3,0.39547132839857013,0.8831185698509216,0.8847144842147827,0.9981961846351624,0.0,0.9999999996613542,0.9808109402656555,0.9808109402656555,True,0.4501850234082508,2.450772227393111,3,0.39566127953995806,0.8786744475364685,0.8800368905067444,0.998451828956604,0.0,1.0000000193237486,0.9804023802280426,0.9804023802280426,0.44896559861423513,2.468177306114993,3.0,0.39556630396926407,0.8808965086936951,0.8823756873607635,0.9983240067958832,0.0,1.0000000094925514,True,0.5171475410461426,10.246269226074219,39.43334197998047,3.552234935760498,0.6179577781192125,3.294628381729126
7,0.0625,l1,34,68,0.029418831691145897,23.30925925925926,0.0,37.73134994506836,0.01656336709856987,0.9871600270271301,0.9758083820343018,0.9758083820343018,True,0.849220928091709,1.384353768804111,1,0.7282518321680042,0.8569676280021667,0.8576755523681641,0.9991746544837952,0.0,0.9999999996613543,0.5085176229476929,0.9842368364334106,False,0.8763634495408767,1.2997473259168546,1,0.7560552167243894,0.8624606132507324,0.8629072904586792,0.9994823932647705,0.0,1.0000000193237484,0.7421630024909973,0.9800226092338562,0.8627921888162928,1.3420505473604827,1.0,0.7421535244461968,0.8597141206264496,0.8602914214134216,0.9993285238742828,0.0,1.0000000094925514,False,0.5702420473098755,11.673665046691895,37.73121643066406,5.263176083564758,1.1627092770484886,3.0084950923919678
7,0.25,l1,34,68,0.03641251474618912,29.618518518518517,0.0,40.863426208496094,0.017938289791345596,0.9998277425765991,0.45799970626831055,0.47617244720458984,False,0.12385829297487316,19.095195559215576,21,0.09748741199336412,0.7862116694450378,0.7914617657661438,0.993366539478302,0.0,0.9999999996613544,0.2337796539068222,0.8215473294258118,False,0.6142847400462546,2.60329814111039,1,0.5100244049482012,0.821662425994873,0.823270857334137,0.998046338558197,0.0,1.0000000193237484,0.3458896800875664,0.6488598883152008,0.36907151651056386,10.849246850162983,11.0,0.30375590847078265,0.8039370477199554,0.8073663115501404,0.9957064390182495,0.0,1.0000000094925514,False,0.7696470618247986,15.860830307006836,40.86376953125,14.157755506038665,5.559037548070658,2.9269063472747803
7,0.5,l1,34,68,0.03982166945934296,30.674074074074074,0.0,43.96062469482422,0.019297903403639793,0.9999803304672241,0.44196054339408875,0.45936110615730286,False,0.11471989978282114,18.35693833165243,21,0.08949165488772598,0.7789136171340942,0.7830023169517517,0.9947782158851624,0.0,0.9999999996613541,0.3132759928703308,0.7088178396224976,False,0.4657746776339835,4.346530629077065,3,0.37320635530119417,0.7961845397949219,0.7989044189453125,0.9965955018997192,0.0,1.0000000193237484,0.3776182681322098,0.5840894728899002,0.29024728870840233,11.351734480364748,12.0,0.23134900509446008,0.7875490784645081,0.7909533679485321,0.9956868588924408,0.0,1.0000000094925512,False,0.858669638633728,17.712879180908203,43.96088790893555,26.381689429283142,13.043663579092046,3.3269705772399902
8,0.0,l1,34,68,0.03231199085712433,15.647685185185185,0.0,81.80652618408203,0.03591155633330345,0.9939742088317871,0.7319484353065491,0.7339204549789429,False,0.25341111032075103,4.023213709834935,4,0.230737269180613,0.9103336334228516,0.911697268486023,0.9985042810440063,0.0,0.9999999996613542,0.6866366267204285,0.691975474357605,False,0.2439425563344287,4.356135321486313,4,0.21634269022726335,0.8863725066184998,0.8884132504463196,0.9977028965950012,0.0,1.0000000193237484,0.7092925310134888,0.7129479646682739,0.24867683332758989,4.189674515660624,4.0,0.22353997970393819,0.8983530700206757,0.9000552594661713,0.9981035888195038,0.0,1.0000000094925512,False,0.5207189917564392,8.832942962646484,81.80673217773438,2.2873075842857364,0.5456453117808525,3.2559993267059326
8,0.025,l1,34,68,0.028888147324323654,19.2125,0.0,37.881500244140625,0.016629280522465706,0.9583214521408081,0.9943448305130005,0.9943448305130005,True,0.9018201226147348,1.2256138172532758,1,0.7783433497254872,0.8624886274337769,0.8633313179016113,0.9990239143371582,0.0,0.9999999996613543,0.9721100330352783,0.9721100330352783,True,0.6166727921315787,2.0601637579652823,2,0.5333180770795137,0.8647369742393494,0.8649269938468933,0.9997803568840027,0.0,1.0000000193237486,0.9832274317741394,0.9832274317741394,0.7592464573731568,1.642888787609279,1.5,0.6558307134025005,0.8636128008365631,0.8641291558742523,0.9994021356105804,0.0,1.0000000094925514,True,0.5653060674667358,10.682710647583008,37.88199996948242,3.648898196220398,0.6282518461076506,3.2148022651672363
8,0.0625,l1,34,68,0.02997133880853653,23.522222222222222,0.0,38.715091705322266,0.01699521206319332,0.9882804751396179,0.9706760048866272,0.9706760048866272,True,0.8164334928088168,1.4961152060019762,1,0.6967102794274329,0.853193998336792,0.8536587953567505,0.9994555115699768,0.0,0.9999999996613542,0.5677220225334167,0.9680400490760803,False,0.8001455285247046,1.5510490760896571,1,0.6885027289953449,0.8603795766830444,0.86089688539505,0.9993990659713745,0.0,1.0000000193237484,0.769199013710022,0.9693580269813538,0.8082895106667607,1.5235821410458166,1.0,0.6926065042113889,0.8567867875099182,0.8572778403759003,0.9994272887706757,0.0,1.0000000094925512,False,0.6175554990768433,11.51175308227539,38.71551513671875,5.339625811576843,1.2224770877817772,3.3335721492767334
8,0.25,l1,34,68,0.036090217530727386,28.241666666666667,0.0,39.74109649658203,0.017445608973503113,0.9958286285400391,0.3407781720161438,0.584270715713501,False,0.30804470783176796,8.566713237207455,8,0.2551253066590873,0.8029756546020508,0.8064437508583069,0.9956995248794556,0.0,0.9999999996613542,0.2718465030193329,0.7923948168754578,False,0.5958648078640024,2.753171771567839,1,0.5041100842932648,0.815973699092865,0.8180124163627625,0.9975077509880066,0.0,1.0000000193237484,0.30631233751773834,0.6883327662944794,0.4519547578478852,5.659942504387647,4.5,0.379617695476176,0.8094746768474579,0.8122280836105347,0.9966036379337311,0.0,1.0000000094925512,False,0.7538942098617554,16.100353240966797,39.74110412597656,13.909240889549256,5.168098950651651,3.254892587661743
8,0.5,l1,34,68,0.03706575185060501,29.636574074074073,0.0,42.58241271972656,0.018692893907427788,0.9999389052391052,0.32936370372772217,0.44940564036369324,False,0.15627082022266006,17.97207553953648,18,0.12299350380672948,0.7870333194732666,0.7916440963745117,0.9941757321357727,0.0,0.9999999996613544,0.27065128087997437,0.6928716897964478,False,0.4426014921269152,4.758488338153113,2,0.3580111424692658,0.8086351752281189,0.8114954233169556,0.996475338935852,0.0,1.0000000193237484,0.30000749230384827,0.5711386650800705,0.29943615617478764,11.365281938844797,10.0,0.24050232313799763,0.7978342473506927,0.8015697598457336,0.9953255355358124,0.0,1.0000000094925514,False,0.7934629917144775,17.4327392578125,42.582237243652344,25.571129465103148,11.79746776817117,3.017963171005249
9,0.0,l1,34,68,0.031187159940600395,15.876851851851852,0.0,79.4629135131836,0.03488275408744812,0.9995948076248169,0.7146716117858887,0.7309508919715881,False,0.2532868544214446,4.021538855976288,4,0.23097138386254645,0.9116888046264648,0.9132606387138367,0.9982788562774658,0.0,0.9999999996613541,0.7082471251487732,0.7082471251487732,False,0.25780565605200195,4.039659035006636,4,0.22856205508527197,0.8860992789268494,0.8881421089172363,0.9976998567581177,0.0,1.0000000193237484,0.7114593684673309,0.7195990085601807,0.25554625523672325,4.030598945491462,4.0,0.2297667194739092,0.8988940417766571,0.9007013738155365,0.9979893565177917,0.0,1.0000000094925512,False,0.48977380990982056,8.796708106994629,79.46566772460938,2.2491154313087467,0.5287986133176055,2.841919422149658
9,0.025,l1,34,68,0.026175932958722115,19.193055555555556,0.0,37.48805618286133,0.016456566751003265,0.9810359477996826,0.6760280728340149,0.6760280728340149,False,0.2411231494572468,4.417745962186324,4,0.21549783291183638,0.8934787511825562,0.894065797328949,0.9993433952331543,0.0,0.9999999996613542,0.709012508392334,0.7129665613174438,False,0.24967148014058677,4.101778182492885,4,0.22626738779685507,0.9059441685676575,0.9062415361404419,0.9996719360351562,0.0,1.0000000193237484,0.6925202906131744,0.6944973170757294,0.2453973147989168,4.259762072339605,4.0,0.22088261035434573,0.8997114598751068,0.9001536667346954,0.9995076656341553,0.0,1.0000000094925512,False,0.4997749328613281,10.224237442016602,37.488258361816406,3.4818288803100588,0.565353297185981,2.783355712890625
9,0.0625,l1,34,68,0.02958029694855213,23.75787037037037,0.0,37.61189270019531,0.01651092804968357,0.994369387626648,0.9718628525733948,0.9718628525733948,True,0.8315822627070508,1.440665610654186,1,0.7133365347241627,0.8576798439025879,0.8580286502838135,0.9995934367179871,0.0,0.999999999661354,0.9280926585197449,0.9280926585197449,True,0.6962153199847932,1.9847039698965894,3,0.5926197692459,0.8510268926620483,0.8513831496238708,0.9995815753936768,0.0,1.0000000193237484,0.9499777555465698,0.9499777555465698,0.7638987913459221,1.7126847902753877,2.0,0.6529781519850313,0.8543533682823181,0.8547058999538422,0.9995875060558319,0.0,1.0000000094925512,True,0.6132428646087646,11.35944938659668,37.6119270324707,5.23587818145752,1.1762559159264037,2.7665605545043945
9,0.25,l1,34,68,0.03797602653503418,29.187962962962963,0.0,41.66539001464844,0.018290337175130844,0.9964156746864319,0.3773914575576782,0.4910217821598053,False,0.1783317887665553,14.891499363602636,11,0.14041490248762123,0.7872964143753052,0.7917966246604919,0.9943164587020874,0.0,0.9999999996613542,0.6256664991378784,0.6551386117935181,False,0.22391178318643915,9.581328505309413,12,0.17769885352886255,0.793358325958252,0.7976040244102478,0.994676947593689,0.0,1.0000000193237482,0.5015289783477783,0.5730801969766617,0.2011217859764972,12.236413934456024,11.5,0.1590568780082419,0.7903273701667786,0.7947003245353699,0.9944967031478882,0.0,1.0000000094925512,False,0.8181617856025696,15.739830017089844,41.66554641723633,14.38251439332962,5.844671957847246,2.653660774230957
9,0.5,l1,34,68,0.04077328369021416,30.413425925925925,0.0,45.575435638427734,0.020006775856018066,0.9962494373321533,0.28611013293266296,0.4550361931324005,False,0.11489250190616827,18.48240601344184,23,0.08710193216687813,0.7580018639564514,0.7620133757591248,0.994735598564148,0.0,0.9999999996613543,0.19792984426021576,0.7389691472053528,False,0.5536071540165155,3.160226998155372,1,0.47004805520298815,0.7991282343864441,0.8008075952529907,0.9979029297828674,0.0,1.0000000193237484,0.24201998859643936,0.5970026701688766,0.3342498279613419,10.821316505798606,12.0,0.27857499368493316,0.7785650491714478,0.7814104855060577,0.9963192641735077,0.0,1.0000000094925514,False,0.8998190760612488,17.725040435791016,45.5755615234375,27.2326079249382,14.21671305465872,2.888715982437134
10,0.0,l1,34,68,0.03096930868923664,16.151851851851852,0.0,81.55545043945312,0.03580133989453316,0.9982390403747559,0.7109842896461487,0.7336510419845581,False,0.25286918245863144,4.597829126326751,5,0.23111425650998937,0.9136021137237549,0.9150575995445251,0.9984093904495239,0.0,0.9999999996613543,0.7027823328971863,0.7027823328971863,False,0.25147639088058066,4.668470394562748,5,0.22323879114566533,0.8871197700500488,0.8891104459762573,0.9977610111236572,0.0,1.0000000193237484,0.7068833112716675,0.7182166874408722,0.2521727866696061,4.633149760444749,5.0,0.22717652382782735,0.9003609418869019,0.9020840227603912,0.9980852007865906,0.0,1.0000000094925514,False,0.49182653427124023,8.807245254516602,81.55476379394531,2.2532755851745607,0.482333724466385,3.3507797718048096
10,0.025,l1,34,68,0.029024554416537285,19.138425925925926,0.0,39.049217224121094,0.017141886055469513,0.9650889039039612,0.9869143962860107,0.9869143962860107,True,0.4685019192227631,2.3286511260537766,3,0.4164828715341703,0.8886677026748657,0.8900200724601746,0.998480498790741,0.0,0.9999999996613543,0.9848913550376892,0.9848913550376892,True,0.45716083085064785,2.403098653495838,3,0.40326739123090977,0.8813433647155762,0.8826032280921936,0.9985725283622742,0.0,1.0000000193237484,0.98590287566185,0.98590287566185,0.46283137503670546,2.3658748897748074,3.0,0.40987513138254006,0.885005533695221,0.8863116502761841,0.9985265135765076,0.0,1.0000000094925514,True,0.5198560357093811,10.075244903564453,39.049293518066406,3.5111373543739317,0.5917417110842382,3.0607709884643555
10,0.0625,l1,34,68,0.030634792521595955,23.606018518518518,0.0,40.16233825683594,0.017630526795983315,0.979296863079071,0.9744315147399902,0.9744315147399902,True,0.8494445334756103,1.3824919711164503,1,0.7327507632585857,0.8623889684677124,0.8632004261016846,0.9990599155426025,0.0,0.9999999996613542,0.9679245948791504,0.9679245948791504,True,0.8391893182868327,1.415591794904501,1,0.7218783863872156,0.8600481152534485,0.8606736660003662,0.9992731809616089,0.0,1.0000000193237484,0.9711780548095703,0.9711780548095703,0.8443169258812215,1.3990418830104756,1.0,0.7273145748229006,0.8612185418605804,0.8619370460510254,0.9991665482521057,0.0,1.0000000094925512,True,0.5966942310333252,11.41778564453125,40.16290283203125,5.3904327869415285,1.2878282491143118,2.870246410369873
10,0.25,l1,34,68,0.036410704255104065,29.205555555555556,0.0,42.27265167236328,0.01855691522359848,0.9982322454452515,0.34586581587791443,0.5190303921699524,False,0.19374531323406605,15.080162964327469,14,0.15291620922529245,0.7834944128990173,0.7877480983734131,0.994600236415863,0.0,0.9999999996613542,0.7611947655677795,0.7611947655677795,False,0.5236175692913733,3.512080441284021,1,0.42780263385605766,0.8161023855209351,0.8182180523872375,0.9974142909049988,0.0,1.0000000193237484,0.553530290722847,0.640112578868866,0.35868144126271967,9.296121702805745,7.5,0.29035942154067507,0.7997983992099762,0.8029830753803253,0.9960072636604309,0.0,1.0000000094925512,False,0.7120815515518188,15.667008399963379,42.27232360839844,14.413564133644105,5.81577661619098,2.8011438846588135
10,0.5,l1,34,68,0.038622237741947174,30.41111111111111,0.0,44.556678771972656,0.01955956034362316,0.9982686638832092,0.4315943717956543,0.4602648615837097,False,0.11966492806279481,19.91875093067916,21,0.09543802006462251,0.7970185279846191,0.8025295734405518,0.9931329488754272,0.0,0.9999999996613542,0.6911422610282898,0.6911422610282898,False,0.4418852365723643,4.783372194393886,2,0.3574948762706102,0.8065705895423889,0.8092758059501648,0.9966571927070618,0.0,1.0000000193237484,0.561368316411972,0.5757035613059998,0.2807750823175795,12.351061562536522,11.5,0.22646644816761635,0.801794558763504,0.8059026896953583,0.9948950707912445,0.0,1.0000000094925512,False,0.7751331925392151,16.789365768432617,44.556488037109375,26.411250364780425,12.648523902951384,3.0512866973876953
11,0.0,l1,34,68,0.032803039997816086,15.212962962962964,0.0,83.73120880126953,0.03675645589828491,0.9994677901268005,0.7198183536529541,0.724420964717865,False,0.2523958015761664,4.019729986353446,4,0.22995214844444112,0.9108726382255554,0.9123154878616333,0.9984184503555298,0.0,0.9999999996613542,0.7040982842445374,0.7040982842445374,False,0.25474955450792863,4.028496496162105,4,0.22548586083884692,0.8849380016326904,0.8870385885238647,0.9976319074630737,0.0,1.0000000193237484,0.7119583189487457,0.7142596244812012,0.25357267804204753,4.024113241257775,4.0,0.22771900464164402,0.8979053199291229,0.899677038192749,0.9980251789093018,0.0,1.0000000094925512,False,0.520932674407959,8.67068862915039,83.73200988769531,2.2550704002380373,0.5235609889261386,2.8076601028442383
11,0.025,l1,34,68,0.028641264885663986,19.51527777777778,0.0,39.53326416015625,0.01735437475144863,0.9438999891281128,0.7135449647903442,0.7135449647903442,False,0.2518297163768187,4.111708390248174,4,0.2287687172951213,0.9083425402641296,0.9084723591804504,0.9998570680618286,0.0,0.9999999996613542,0.6668470501899719,0.6668470501899719,False,0.24297095356546125,4.557165045052212,4,0.21670440399944385,0.8910092711448669,0.892004668712616,0.9988840818405151,0.0,1.0000000193237484,0.6901960074901581,0.6901960074901581,0.24740033497114,4.334436717650194,4.0,0.2227365606472826,0.8996759057044983,0.9002385139465332,0.9993705749511719,0.0,1.0000000094925512,False,0.5470930337905884,10.205692291259766,39.53325271606445,3.576562809944153,0.6350855485119402,2.9142708778381348
11,0.0625,l1,34,68,0.027998359873890877,24.307407407407407,0.0,39.94340515136719,0.017534418031573296,0.9922083020210266,0.9544640183448792,0.9544640183448792,True,0.7932279642951969,1.577710067786615,1,0.6797362262661899,0.8562067151069641,0.856891930103302,0.9992003440856934,0.0,0.9999999996613542,0.22520948946475983,0.9210450053215027,False,0.577688266257738,2.614179242862706,2,0.5007386012743856,0.8493470549583435,0.8500142097473145,0.9992151260375977,0.0,1.0000000193237484,0.5898367539048195,0.9377545118331909,0.6854581152764674,2.0959446553246606,1.5,0.5902374137702877,0.8527768850326538,0.8534530699253082,0.9992077350616455,0.0,1.0000000094925512,False,0.595323920249939,11.642215728759766,39.94346618652344,5.420233702659607,1.298298584171994,2.8116958141326904
11,0.25,l1,34,68,0.03644168749451637,28.747222222222224,0.0,45.303279876708984,0.019887305796146393,0.9999253749847412,0.37731319665908813,0.4692445993423462,False,0.1775573314101706,13.299544375157037,14,0.13791001914205975,0.7763355374336243,0.7793212532997131,0.996168851852417,0.0,0.9999999996613542,0.6345708966255188,0.6589333415031433,False,0.2155829504653236,9.746996036079109,11,0.17606116881964592,0.815653383731842,0.8194881081581116,0.9953206181526184,0.0,1.0000000193237484,0.5059420466423035,0.5640889704227448,0.1965701409377471,11.523270205618072,12.5,0.15698559398085282,0.7959944605827332,0.7994046807289124,0.9957447350025177,0.0,1.0000000094925512,False,0.7646488547325134,14.89744758605957,45.30369186401367,15.070061337947845,6.730683587050721,3.2200801372528076
11,0.5,l1,34,68,0.037307608872652054,30.437037037037037,0.0,43.7548713684082,0.019207580015063286,0.9999973177909851,0.3844586908817291,0.4875469505786896,False,0.17005781168510586,15.234638974969297,16,0.13270387243972256,0.7791271805763245,0.7831529378890991,0.9948595762252808,0.0,0.9999999996613543,0.634907603263855,0.6360283493995667,False,0.1980009298569135,10.48192132189956,12,0.16172247311674245,0.8163110017776489,0.820051372051239,0.995438814163208,0.0,1.0000000193237484,0.509683147072792,0.5617876499891281,0.18402937077100967,12.858280148434428,14.0,0.1472131727782325,0.7977190911769867,0.8016021549701691,0.9951491951942444,0.0,1.0000000094925514,False,0.8204450011253357,17.018321990966797,43.754966735839844,26.101592767238618,12.901784695706507,3.2758779525756836
0,0.0,topk,34,68,0.00745338574051857,16.0,0.029411764705882353,87.64065551757812,0.038472630083560944,0.9885016679763794,0.9998446106910706,0.9998446106910706,True,0.999986074475466,1.0000278033314387,1,0.9978617818543113,0.9978653788566589,0.9978735446929932,0.9999918341636658,0.008792797841276387,0.9999613422672053,0.9998520612716675,0.9998520612716675,True,0.9999674332313228,1.0000651888722707,1,0.9980317276305877,0.9980528354644775,0.9980610609054565,0.999991774559021,0.009372080679137345,0.9999561004120335,0.999848335981369,0.999848335981369,0.9999767538533944,1.0000464961018547,1.0,0.9979467547424494,0.9979591071605682,0.9979673027992249,0.9999918043613434,0.009082439260206866,0.9999587213396195,True,0.08604293316602707,17.252174377441406,87.64108276367188,0.08604293316602707,0.2524907245065959,4.826430320739746
0,0.025,topk,34,68,0.013585890643298626,16.0,0.3382352941176471,40.89999008178711,0.01795434020459652,0.9999992251396179,0.996920645236969,0.996920645236969,True,0.9903038179856714,1.0196701438209388,1,0.9972359852833985,1.0037752389907837,1.0042074918746948,0.9995695352554321,0.0,0.9999999996613543,0.9950262904167175,0.9950262904167175,True,0.9955939268495642,1.0088672484611338,1,0.994957529927587,0.9944904446601868,0.9952782392501831,0.9992084503173828,0.0,1.0000000193237482,0.9959734678268433,0.9959734678268433,0.9929488724176178,1.0142686961410363,1.0,0.9960967576054928,0.9991328418254852,0.999742865562439,0.9993889927864075,0.0,1.0000000094925512,True,0.2319629192352295,19.327495574951172,40.899436950683594,1.2544488430023193,0.7118863302856553,4.9928648471832275
0,0.0625,topk,34,68,0.03659289330244064,16.0,0.2647058823529412,39.66498565673828,0.017412196844816208,0.999999463558197,0.4292116165161133,0.5358625650405884,False,0.7624057586949023,1.6488854598913194,2,0.7611421697842958,0.9930939674377441,0.9940221309661865,0.9990662932395935,0.0,0.9999999996613541,0.9487314224243164,0.9487314224243164,True,0.9358795071628456,1.1410749239429485,1,0.9441219405667356,0.9835045337677002,0.9864233732223511,0.9970410466194153,0.0,1.0000000193237484,0.6889715194702148,0.7422969937324524,0.849142632928874,1.394980191917134,1.5,0.8526320551755158,0.9882992506027222,0.9902227520942688,0.9980536699295044,0.0,1.0000000094925512,False,0.6983913779258728,26.61676788330078,39.66485595703125,3.177444875240326,1.7976145622754554,5.006667137145996
0,0.25,topk,34,68,0.059557050466537476,16.0,0.25,43.80475616455078,0.019229479134082794,0.9999998807907104,0.399044007062912,0.6070762276649475,False,0.42228108408069975,4.379381679707711,4,0.36426659253367827,0.8603737354278564,0.8751050233840942,0.9831662774085999,0.0,0.9999999996613543,0.6779521107673645,0.6779521107673645,False,0.5259025288405279,3.4191786964652273,2,0.47899875902846917,0.8619643449783325,0.8751479387283325,0.9849355816841125,0.0,1.0000000193237484,0.5384980589151382,0.642514169216156,0.47409180646061383,3.899280188086469,3.0,0.4216326757810737,0.8611690402030945,0.8751264810562134,0.9840509295463562,0.0,1.0000000094925514,False,1.2907757759094238,38.5443115234375,43.80472183227539,12.241956233978271,7.0042941684087685,4.977233648300171
0,0.5,topk,34,68,0.07359137386083603,16.0,0.3235294117647059,47.39377212524414,0.02080499194562435,0.9999998211860657,0.4014120399951935,0.46937301754951477,False,0.6356231454630398,2.080718375200362,2,0.603034418571815,0.9351599216461182,0.9358825087547302,0.9992278814315796,0.0,0.9999999996613543,0.6212325096130371,0.6212325096130371,False,0.33644910232155006,6.527518451866728,8,0.25674865618651743,0.7606871724128723,0.785768985748291,0.9680799841880798,0.0,1.0000000193237488,0.5113222748041153,0.5453027635812759,0.4860361238922949,4.304118413533545,5.0,0.4298915373791662,0.8479235470294952,0.8608257472515106,0.9836539328098297,0.0,1.0000000094925516,False,1.6739438772201538,39.01200866699219,47.3936767578125,25.370782256126404,15.16794516784835,5.020145416259766
1,0.0,topk,34,68,0.0073863184079527855,15.998611111111112,0.014705882352941176,92.4655532836914,0.04059067368507385,0.9992257952690125,0.8132885694503784,0.8269273638725281,False,0.9775005288185331,1.046152281778569,1,0.9772531411817349,0.9994060397148132,0.9994208216667175,0.9999852180480957,0.0,0.9999999996613543,0.818226158618927,0.818226158618927,False,0.9937005881960722,1.0126995029321626,1,0.9949984989986536,1.0011553764343262,1.0011755228042603,0.9999797940254211,0.0,1.0000000193237484,0.8157573640346527,0.8225767612457275,0.9856005585073027,1.0294258923553659,1.0,0.9861258200901942,1.0002807080745697,1.000298172235489,0.9999825060367584,0.0,1.0000000094925514,False,0.08632762730121613,17.30733871459961,92.4627685546875,0.08632762730121613,0.2660685957785468,4.713361024856567
1,0.025,topk,34,68,0.014403637498617172,16.0,0.25,38.835968017578125,0.017048275098204613,0.9999996423721313,0.8624116778373718,0.8624116778373718,False,0.9930552857151634,1.014012054329325,1,0.9939663659100273,0.99729323387146,0.997428834438324,0.9998640418052673,0.0,0.9999999996613542,0.9926257729530334,0.9926257729530334,True,0.981906507641516,1.0371503078501705,1,0.980774404888305,0.9947539567947388,0.9955834746360779,0.9991667866706848,0.0,1.0000000193237482,0.9275187253952026,0.9275187253952026,0.9874808966783397,1.0255811810897477,1.0,0.9873703853991662,0.9960235953330994,0.9965061545372009,0.9995154142379761,0.0,1.0000000094925512,False,0.23138271272182465,19.849275588989258,38.835941314697266,1.2022812455892562,0.6684578991522773,4.7461066246032715
1,0.0625,topk,34,68,0.03273967280983925,16.0,0.23529411764705882,39.040855407714844,0.017138216644525528,0.9999998807907104,0.6945005655288696,0.6945005655288696,False,0.9810275488104232,1.038999087559192,1,1.020161814254218,0.983314573764801,0.9837352633476257,0.9995723366737366,0.0,0.9999999996613543,0.913727879524231,0.913727879524231,True,0.8913067705512532,1.2530544014087448,1,0.8833364572582779,0.9836896657943726,0.9860865473747253,0.9975692629814148,0.0,1.0000000193237482,0.8041142225265503,0.8041142225265503,0.9361671596808382,1.1460267444839682,1.0,0.951749135756248,0.9835021197795868,0.9849109053611755,0.9985707998275757,0.0,1.0000000094925512,False,0.591388463973999,24.2115421295166,39.04085922241211,3.031442165374756,1.583029302310571,5.0121989250183105
1,0.25,topk,34,68,0.0645926296710968,16.0,0.17647058823529413,41.77574157714844,0.018338780850172043,0.9999970197677612,0.41106078028678894,0.5941736102104187,False,0.3544305203843963,5.430344095864391,5,0.30317152520184854,0.8503783941268921,0.8657917380332947,0.9821974039077759,0.0,0.9999999996613544,0.5135495662689209,0.7934988141059875,False,0.6578951378559447,2.262771061103822,1,0.5930358089646557,0.8841695785522461,0.8996187448501587,0.9828269481658936,0.0,1.0000000193237484,0.4623051732778549,0.6938362121582031,0.5061628291201705,3.8465575784841066,3.0,0.4481036670832521,0.8672739863395691,0.8827052414417267,0.9825121760368347,0.0,1.0000000094925514,False,1.2159239053726196,46.873809814453125,41.77568435668945,11.659844994544983,6.528844331555864,5.051205635070801
1,0.5,topk,34,68,0.08058948069810867,16.0,0.14705882352941177,43.852108001708984,0.01925026625394821,1.0,0.4426971673965454,0.492899626493454,False,0.17207560763083812,12.054028178819642,13,0.13572616999640863,0.7796743512153625,0.7979055643081665,0.9771511554718018,0.0,0.9999999996613542,0.552966833114624,0.6620023846626282,False,0.3640435787209935,6.387678866514135,10,0.3019573672492288,0.8201886415481567,0.8303974866867065,0.9877061247825623,0.0,1.0000000193237484,0.4978320002555847,0.5774510055780411,0.2680595931759158,9.22085352266689,11.5,0.2188417686228187,0.7999314963817596,0.8141515254974365,0.982428640127182,0.0,1.0000000094925512,False,1.5607895851135254,37.57829284667969,43.852088928222656,23.486834049224854,12.881794546316176,4.92702579498291
2,0.0,topk,34,68,0.01047798153012991,15.999074074074073,0.029411764705882353,71.37467193603516,0.031332165002822876,0.9994514584541321,0.9997949004173279,0.9997949004173279,True,0.828517174216939,1.399038822302318,2,0.8296888562769049,1.0007017850875854,1.0007158517837524,0.9999860525131226,0.0038137434924376164,0.9999927273151953,0.9997385740280151,0.9997385740280151,True,0.9999654156448441,1.0000691534529353,1,0.9998433112720609,0.9998655915260315,0.9998874068260193,0.9999781847000122,0.006026205074112843,0.99998186158545,0.9997667372226715,0.9997667372226715,0.9142412949308916,1.1995539878776267,1.5,0.9147660837744829,1.0002836883068085,1.0003016293048859,0.9999821186065674,0.00491997428327523,0.9999872944503226,True,0.1160406768321991,17.482131958007812,71.37092590332031,0.1160406768321991,0.2835177989206349,4.69107723236084
2,0.025,topk,34,68,0.019941195845603943,16.0,0.2647058823529412,37.174034118652344,0.01631871610879898,0.9999998211860657,0.46142134070396423,0.979533851146698,False,0.5918495814111163,2.361602872646838,3,0.5908931984234335,0.9881055355072021,0.9891084432601929,0.9989860653877258,0.0,0.9999999996613542,0.9949670433998108,0.9949670433998108,True,0.9924143054627911,1.0153387988906972,1,0.995231695270612,0.9981224536895752,0.9985156655311584,0.999606192111969,0.0,1.0000000193237484,0.7281941920518875,0.9872504472732544,0.7921319434369537,1.6884708357687677,2.0,0.7930624468470227,0.9931139945983887,0.9938120543956757,0.9992961287498474,0.0,1.0000000094925512,False,0.3318520188331604,20.76537322998047,37.173866271972656,1.261198675632477,0.810661467888342,4.582123279571533
2,0.0625,topk,34,68,0.03841020166873932,16.0,0.19117647058823528,39.67413330078125,0.01741621270775795,0.999999463558197,0.3644912838935852,0.5508990287780762,False,0.5072664640250092,2.064274508516324,2,0.5094376607666679,0.9951854348182678,0.996178150177002,0.999003529548645,0.0,0.9999999996613542,0.9215409755706787,0.9215409755706787,True,0.8836237103640869,1.272155677968038,1,0.917837765832769,0.9915924668312073,0.9943640828132629,0.9972127079963684,0.0,1.0000000193237484,0.643016129732132,0.7362200021743774,0.6954450871945481,1.668215093242181,1.5,0.7136377132997185,0.9933889508247375,0.9952711164951324,0.9981081187725067,0.0,1.0000000094925512,False,0.6807026863098145,26.201786041259766,39.67396545410156,3.160325527191162,1.7714454507021218,4.721525430679321
2,0.25,topk,34,68,0.060960862785577774,16.0,0.19117647058823528,45.37824249267578,0.019920211285352707,0.9999999403953552,0.3519348204135895,0.6008198857307434,False,0.3319890565127016,5.971589638916481,6,0.29398009813569964,0.8780649304389954,0.8900870084762573,0.9864934086799622,0.0,0.9999999996613543,0.5298094153404236,0.7223300933837891,False,0.5017632514279012,2.83084122748594,2,0.518266854959346,0.9258490204811096,0.9361579418182373,0.9889880418777466,0.0,1.0000000193237482,0.44087211787700653,0.6615749895572662,0.4168761539703014,4.401215433201211,4.0,0.4061234765475228,0.9019569754600525,0.9131224751472473,0.9877407252788544,0.0,1.0000000094925512,False,1.2034693956375122,33.958641052246094,45.378440856933594,12.54807960987091,6.870234130275507,4.568953990936279
2,0.5,topk,34,68,0.06399541348218918,16.0,0.2647058823529412,47.42295837402344,0.020817803218960762,0.9999999403953552,0.35253027081489563,0.4692918360233307,False,0.818046255419479,1.4828702326008505,1,0.7811945734588621,0.9501038193702698,0.9508402943611145,0.9992254376411438,0.0,0.9999999996613542,0.5094142556190491,0.7174580693244934,False,0.4985902653519898,3.8243379099299033,2,0.4171397343207651,0.8204254508018494,0.8342161178588867,0.9834687113761902,0.0,1.0000000193237486,0.43097226321697235,0.593374952673912,0.6583182603857344,2.653604071265377,1.5,0.5991671538898136,0.8852646350860596,0.8925282061100006,0.991347074508667,0.0,1.0000000094925514,False,1.3303146362304688,50.57428741455078,47.42301940917969,25.041824340820312,14.73100779181281,5.130865812301636
3,0.0,topk,34,68,0.003942287527024746,16.0,0.07352941176470588,103.03935241699219,0.0452323742210865,0.9459742307662964,0.9998366832733154,0.9998366832733154,True,0.9999795508373372,1.0000408538438987,1,0.9997566612874462,0.9996996521949768,0.9997110366821289,0.9999885559082031,0.0,0.9999999996613542,0.5816371440887451,0.999811589717865,False,0.9999792366531209,1.0000414809434972,1,1.0000131771866003,0.9999862909317017,0.9999974370002747,0.9999887943267822,0.0,1.0000000193237484,0.7907369136810303,0.9998241364955902,0.999979393745229,1.000041167393698,1.0,0.9998849192370233,0.9998429715633392,0.9998542368412018,0.9999886751174927,0.0,1.0000000094925512,False,0.05177135765552521,17.39205551147461,103.03334045410156,0.05177135765552521,0.2317627178521338,4.995217323303223
3,0.025,topk,34,68,0.01411951519548893,16.0,0.2647058823529412,37.65237045288086,0.016528695821762085,0.9999996423721313,0.9949840903282166,0.9949840903282166,True,0.9886408005668754,1.023084739446315,1,0.9827617642128536,0.9890338778495789,0.9894790649414062,0.9995500445365906,0.0,0.9999999996613542,0.29679837822914124,0.9971415996551514,False,0.9934093388564179,1.013302115295716,1,0.9993932903842236,1.0008238554000854,1.0012295246124268,0.9995948672294617,0.0,1.0000000193237484,0.6458912342786789,0.996062844991684,0.9910250697116467,1.0181934273710156,1.0,0.9910775272985386,0.9949288666248322,0.9953542947769165,0.9995724558830261,0.0,1.0000000094925512,False,0.23494252562522888,19.663558959960938,37.65252685546875,1.1762556970119475,0.6756427430787233,4.6091148853302
3,0.0625,topk,34,68,0.0424761101603508,16.0,0.16176470588235295,40.427268981933594,0.017746826633810997,0.9999997615814209,0.78206467628479,0.78206467628479,False,0.5907014803903939,2.2522709339174263,2,0.5790124073993177,0.9765303730964661,0.9800304770469666,0.9964286088943481,0.0,0.9999999996613542,0.6748260855674744,0.6748260855674744,False,0.4961782852784363,2.813026343624597,3,0.49084221469055056,0.9828456044197083,0.9858428835868835,0.9969596862792969,0.0,1.0000000193237484,0.7284453809261322,0.7284453809261322,0.5434398828344151,2.5326486387710117,2.5,0.5349273110449342,0.9796879887580872,0.982936680316925,0.9966941475868225,0.0,1.0000000094925512,False,0.6589602828025818,29.047874450683594,40.427101135253906,3.185654103755951,1.773460682116668,4.954412221908569
3,0.25,topk,34,68,0.061745256185531616,16.0,0.16176470588235295,42.683692932128906,0.01873735524713993,0.9999999403953552,0.4203713536262512,0.5619906783103943,False,0.3363542088186967,5.866714898078,5,0.2984504187590109,0.8800027966499329,0.8910698890686035,0.9875800013542175,0.0,0.9999999996613542,0.638983428478241,0.6667681932449341,False,0.33548764501912753,5.447691196249942,6,0.3394547487825278,0.8616489768028259,0.8741921186447144,0.9856517314910889,0.0,1.0000000193237484,0.5296773910522461,0.6143794357776642,0.3359209269189121,5.657203047163971,5.5,0.31895258377076935,0.8708258867263794,0.8826310038566589,0.9866158664226532,0.0,1.0000000094925512,False,1.2014570236206055,31.77185821533203,42.683349609375,11.872294425964355,6.325234987884813,4.755331993103027
3,0.5,topk,34,68,0.06738778948783875,16.0,0.17647058823529413,44.798484802246094,0.019665708765387535,0.9999998211860657,0.4068138599395752,0.5507131814956665,False,0.3038624834991361,7.293659121930537,9,0.255672399488214,0.8343918323516846,0.8486526608467102,0.9831959009170532,0.0,0.9999999996613542,0.6013756394386292,0.6610590815544128,False,0.2835673965062487,5.829195912103871,6,0.2868919696707484,0.8631612062454224,0.8771710395812988,0.9840283989906311,0.0,1.0000000193237484,0.5040947496891022,0.6058861315250397,0.2937149400026924,6.561427517017204,7.5,0.2712821845794812,0.8487765192985535,0.8629118502140045,0.9836121499538422,0.0,1.0000000094925512,False,1.2991597652435303,33.68510055541992,44.79844665527344,23.69838309288025,13.15351537036693,4.822422027587891
4,0.0,topk,34,68,0.011271772906184196,16.0,0.0,82.36483764648438,0.03615664690732956,0.9989912509918213,0.8849759697914124,0.8868351578712463,False,0.5555036744683401,2.455261109055341,3,0.5548170163958542,0.9986100792884827,0.9986180663108826,0.9999920129776001,0.0,0.9999999996613543,0.865639328956604,0.865639328956604,False,0.767863152837423,1.6219013403731564,3,0.7679962234981821,1.0001105070114136,1.0001201629638672,0.9999902844429016,0.0,1.0000000193237484,0.8753076493740082,0.8762372434139252,0.6616834136528815,2.0385812247142487,3.0,0.6614066199470181,0.9993602931499481,0.9993691146373749,0.9999911487102509,0.0,1.0000000094925514,False,0.10971548408269882,16.717256546020508,82.36601257324219,0.10971548408269882,0.2686291298860695,4.823713779449463
4,0.025,topk,34,68,0.01587052457034588,16.0,0.22058823529411764,37.543365478515625,0.01648084446787834,0.9999996423721313,0.9905862808227539,0.9905862808227539,True,0.9924139266484823,1.0153374486844002,1,0.9970412823686607,0.9952917695045471,0.9956763386726379,0.9996137022972107,0.0,0.9999999996613542,0.9899532198905945,0.9899532198905945,True,0.9762225563316251,1.04918498308631,1,0.9797387578832519,0.9970499277114868,0.9976048469543457,0.9994437098503113,0.0,1.0000000193237484,0.9902697503566742,0.9902697503566742,0.9843182414900538,1.032261215885355,1.0,0.9883900201259563,0.996170848608017,0.9966405928134918,0.999528706073761,0.0,1.0000000094925512,True,0.2770817279815674,21.028575897216797,37.54313659667969,1.2156601428985596,0.6689055593714427,4.532407999038696
4,0.0625,topk,34,68,0.035903364419937134,16.0,0.22058823529411764,38.633934020996094,0.01695958338677883,0.9999992847442627,0.6992591023445129,0.6992591023445129,False,0.6703749169908588,1.9129143710651224,2,0.666562793167445,0.9885501265525818,0.9919217228889465,0.9966009259223938,0.0,0.9999999996613542,0.402128130197525,0.5911718010902405,False,0.4709145222429697,2.262442274739374,2,0.46927703006339183,0.988018810749054,0.9887484312057495,0.9992620944976807,0.0,1.0000000193237484,0.550693616271019,0.6452154517173767,0.5706447196169142,2.0876783229022484,2.0,0.5679199116154184,0.9882844686508179,0.990335077047348,0.9979315102100372,0.0,1.0000000094925512,False,0.6382213234901428,28.288145065307617,38.63396453857422,3.0528441071510315,1.586360507996266,4.996761798858643
4,0.25,topk,34,68,0.05881858617067337,16.0,0.25,40.859527587890625,0.017936579883098602,0.9999998807907104,0.3516679108142853,0.4539201855659485,False,0.2275995532555437,11.255222888376515,12,0.20735499045213004,0.8640590310096741,0.8696181178092957,0.9936074018478394,0.0,0.9999999996613544,0.7026856541633606,0.7026856541633606,False,0.4535517367710832,4.32450415629162,4,0.4120819307948535,0.8926516175270081,0.8980779647827148,0.9939578175544739,0.0,1.0000000193237484,0.5271767824888229,0.5783029198646545,0.34057564501331344,7.789863522334068,8.0,0.3097184606234918,0.8783553242683411,0.8838480412960052,0.9937826097011566,0.0,1.0000000094925514,False,1.094170093536377,31.750675201416016,40.85943603515625,11.30902910232544,5.811658118238171,5.038321018218994
4,0.5,topk,34,68,0.06957795470952988,16.0,0.22058823529411764,40.91838836669922,0.017962418496608734,0.9999997019767761,0.39578065276145935,0.39578065276145935,False,0.15083291198020307,13.702677959459969,15,0.12202448145574529,0.7683340311050415,0.7808976769447327,0.9839113354682922,0.0,0.9999999996613542,0.602562665939331,0.602562665939331,False,0.22231326621132197,8.28553992277986,9,0.19845875233126392,0.8289202451705933,0.8354158401489258,0.9922247529029846,0.0,1.0000000193237484,0.4991716593503952,0.4991716593503952,0.18657308909576253,10.994108941119915,12.0,0.1602416168935046,0.7986271381378174,0.8081567585468292,0.9880680441856384,0.0,1.0000000094925512,False,1.4004862308502197,52.52497863769531,40.91816711425781,21.859569787979126,11.728538843149991,5.007756233215332
5,0.0,topk,34,68,0.009420476853847504,16.0,0.029411764705882353,69.94453430175781,0.030704360455274582,0.9921079277992249,0.9997008442878723,0.9997008442878723,True,0.9999587873579422,1.0000823828335235,1,0.9998620787802494,0.9998934864997864,0.999907910823822,0.9999855160713196,0.0,0.9999999996613542,0.9918728470802307,0.9918728470802307,True,0.9997072893660433,1.0005856888456028,1,0.9988297061064121,0.9991035461425781,0.9992293119430542,0.9998741149902344,0.0,1.0000000193237484,0.9957868456840515,0.9957868456840515,0.9998330383619927,1.0003340358395632,1.0,0.9993458924433307,0.9994985163211823,0.9995686113834381,0.999929815530777,0.0,1.0000000094925512,True,0.1253955364227295,16.234792709350586,69.9420166015625,0.1253955364227295,0.2801537992542223,4.587125539779663
5,0.025,topk,34,68,0.017097018659114838,16.0,0.29411764705882354,39.78993225097656,0.017467046156525612,0.9999997019767761,0.9971655607223511,0.9971655607223511,True,0.9939166640438196,1.0122723424480207,1,0.9986877119380758,0.9984745383262634,0.9990398287773132,0.9994341731071472,0.0,0.9999999996613542,0.9957250356674194,0.9957250356674194,True,0.9945756771762142,1.010934818923499,1,0.9972930864253335,0.9952284097671509,0.9957235455513,0.9995027184486389,0.0,1.0000000193237484,0.9964452981948853,0.9964452981948853,0.994246170610017,1.01160358068576,1.0,0.9979903991817047,0.9968514740467072,0.9973816871643066,0.9994684457778931,0.0,1.0000000094925512,True,0.2692934572696686,20.967056274414062,39.790283203125,1.2640505373477935,0.7337565542189353,4.7954421043396
5,0.0625,topk,34,68,0.039589736610651016,16.0,0.20588235294117646,38.834320068359375,0.01704755239188671,0.9999536871910095,0.5462080836296082,0.5462080836296082,False,0.730539238596498,1.7354952793081644,2,0.7220230958546089,0.9853329062461853,0.9868409633636475,0.9984718561172485,0.0,0.9999999996613541,0.9081581234931946,0.9081581234931946,True,0.8587669249662557,1.3501565402951137,1,0.8483848882107385,0.9597315788269043,0.9647989273071289,0.9947476983070374,0.0,1.0000000193237484,0.7271831035614014,0.7271831035614014,0.7946530817813768,1.542825909801639,1.5,0.7852039920326737,0.9725322425365448,0.9758199453353882,0.9966097772121429,0.0,1.0000000094925512,False,0.6579092144966125,27.85662841796875,38.834312438964844,3.0850537419319153,1.6701017918971215,4.8673810958862305
5,0.25,topk,34,68,0.06438138335943222,16.0,0.16176470588235295,39.796539306640625,0.017469944432377815,0.9999997615814209,0.3969414532184601,0.4616204798221588,False,0.1736065649524272,13.363640196812073,18,0.14566660032818382,0.7713249325752258,0.7832027673721313,0.9848342537879944,0.0,0.9999999996613542,0.362800657749176,0.8358928561210632,False,0.7738679831408968,1.6572226540075476,1,0.7290436612900817,0.9107709527015686,0.9205237030982971,0.9894052743911743,0.0,1.0000000193237484,0.37987105548381805,0.648756667971611,0.473737274046662,7.51043142540981,9.5,0.43735513080913274,0.8410479426383972,0.8518632352352142,0.9871197640895844,0.0,1.0000000094925512,False,1.2592357397079468,45.31391906738281,39.79655456542969,11.208374381065369,5.914037354925988,4.733017444610596
5,0.5,topk,34,68,0.07061943411827087,16.0,0.1323529411764706,42.09912872314453,0.01848074048757553,0.9999998211860657,0.6346921324729919,0.6346921324729919,False,0.4403877252408775,4.694647740677862,5,0.40030380203361526,0.8476274609565735,0.8607537150382996,0.9847503304481506,0.0,0.999999999661354,0.3334994316101074,0.7732682228088379,False,0.6829217232005999,2.1020680605942026,1,0.6330609542311587,0.8873527646064758,0.9020261168479919,0.9837329387664795,0.0,1.0000000193237482,0.4840957820415497,0.7039801776409149,0.5616547242207387,3.3983579006360323,3.0,0.516682378132387,0.8674901127815247,0.8813899159431458,0.9842416346073151,0.0,1.0000000094925512,False,1.363328218460083,45.293006896972656,42.098941802978516,22.41279911994934,12.147534439852944,4.6476969718933105
6,0.0,topk,34,68,0.00998731330037117,16.0,0.029411764705882353,71.10977935791016,0.031215881928801537,0.9768840074539185,0.9994113445281982,0.9994113445281982,True,0.9997779996095222,1.000444110637471,1,0.9994869682016918,0.9996030330657959,0.9996339678764343,0.9999690055847168,0.0,0.9999999996613542,0.7502520084381104,0.7502520084381104,False,0.2718943344763498,3.9575405581317047,4,0.2709930751089254,0.9965663552284241,0.9965707659721375,0.9999955892562866,0.0,1.0000000193237482,0.8748316764831543,0.8748316764831543,0.635836167042936,2.478992334384588,2.5,0.6352400216553086,0.99808469414711,0.9981023669242859,0.9999822974205017,0.0,1.0000000094925512,False,0.12826019525527954,16.602588653564453,71.10604858398438,0.12826019525527954,0.31632396309029703,4.858927011489868
6,0.025,topk,34,68,0.01448773592710495,16.0,0.20588235294117646,38.80059051513672,0.017032744362950325,0.9999997615814209,0.9953185319900513,0.9953185319900513,True,0.9853237276185207,1.0299782832427011,1,0.9961864423361123,1.0030255317687988,1.0034278631210327,0.9995990991592407,0.0,0.9999999996613542,0.8200434446334839,0.8200434446334839,False,0.9387077234138114,1.1306666869314288,1,0.9420640633284407,0.9984892010688782,0.9987267851829529,0.9997621178627014,0.0,1.0000000193237484,0.9076809883117676,0.9076809883117676,0.9620157255161661,1.080322485087065,1.0,0.9691252528322765,1.0007573664188385,1.0010773241519928,0.9996806085109711,0.0,1.0000000094925512,False,0.2735462784767151,21.326505661010742,38.80070495605469,1.2435639023780825,0.7962961711686415,4.748301267623901
6,0.0625,topk,34,68,0.03297010809183121,16.0,0.20588235294117646,39.110870361328125,0.01716895028948784,0.9999995231628418,0.9745873808860779,0.9745873808860779,True,0.945230310635303,1.118861961985276,1,0.9419536145462084,0.9854214191436768,0.9883967041969299,0.9969897270202637,0.0,0.9999999996613542,0.27456140518188477,0.9450536966323853,False,0.8988037661028745,1.2361658826722028,1,0.8810595991372058,0.9786264300346375,0.9826502203941345,0.9959052205085754,0.0,1.0000000193237484,0.6245743930339813,0.9598205387592316,0.9220170383690888,1.1775139223287394,1.0,0.911506606841707,0.9820239245891571,0.9855234622955322,0.9964474737644196,0.0,1.0000000094925512,False,0.6342141628265381,24.892059326171875,39.110679626464844,3.078631639480591,1.6834848112427179,4.473764419555664
6,0.25,topk,34,68,0.06029566377401352,16.0,0.16176470588235295,41.82437515258789,0.018360130488872528,0.9999996423721313,0.4338924288749695,0.4338924288749695,False,0.4766062340112356,3.050151459170147,3,0.4604198842627735,0.9440866708755493,0.9547402858734131,0.9888413548469543,0.0,0.9999999996613541,0.6360531449317932,0.6360531449317932,False,0.2856082226044722,6.631831243297825,5,0.2764350135896725,0.8397555351257324,0.8558835983276367,0.9811562299728394,0.0,1.0000000193237486,0.5349727869033813,0.5349727869033813,0.38110722830785393,4.840991351233986,4.0,0.36842744892622303,0.8919211030006409,0.9053119421005249,0.9849987924098969,0.0,1.0000000094925514,False,1.2640199661254883,42.25414276123047,41.82429504394531,11.720093727111816,6.3685727749136944,4.797808408737183
6,0.5,topk,34,68,0.07202307134866714,16.0,0.11764705882352941,47.552974700927734,0.020874878391623497,0.9999991059303284,0.6028839349746704,0.6028839349746704,False,0.4179450708726406,4.971847703139659,6,0.37140447486076306,0.8699595928192139,0.8783183693885803,0.990483283996582,0.0,0.9999999996613541,0.6554912328720093,0.6554912328720093,False,0.31771164624082004,6.990295310052668,7,0.2871264437304983,0.837434709072113,0.848952054977417,0.9864334464073181,0.0,1.0000000193237484,0.6291875839233398,0.6291875839233398,0.36782835855673035,5.981071506596163,6.5,0.32926545929563067,0.8536971509456635,0.8636352121829987,0.9884583652019501,0.0,1.0000000094925512,False,1.5078575611114502,38.277252197265625,47.55270004272461,25.284207582473755,14.81077902582825,4.822014331817627
7,0.0,topk,34,68,0.004083442501723766,16.0,0.04411764705882353,102.3233413696289,0.04491805657744408,0.97894686460495,0.9996644854545593,0.9996644854545593,True,0.9999654344983344,1.000069094691567,1,1.0003886870738428,1.000415563583374,1.0004303455352783,0.9999853372573853,0.0,0.9999999996613542,0.9996778964996338,0.9996778964996338,True,0.9998627000533704,1.0002746796548925,1,0.9997343798628311,0.9998608827590942,0.9998685717582703,0.999992311000824,0.0,1.0000000193237486,0.9996711909770966,0.9996711909770966,0.9999140672758524,1.0001718871732297,1.0,1.000061533468337,1.0001382231712341,1.0001494586467743,0.9999888241291046,0.0,1.0000000094925514,True,0.05739734321832657,17.283447265625,102.3204116821289,0.05739734321832657,0.2027555383405015,4.793427228927612
7,0.025,topk,34,68,0.013780112378299236,16.0,0.23529411764705882,37.953067779541016,0.016660697758197784,0.9999913573265076,0.9969187378883362,0.9969187378883362,True,0.99264894463206,1.0148594915179066,1,0.9999360307486854,1.001775860786438,1.0022127628326416,0.9995639324188232,0.0,0.9999999996613542,0.9927418231964111,0.9927418231964111,True,0.9812866423442138,1.038405178756693,1,0.9933895245838784,1.0020204782485962,1.0026243925094604,0.9993976950645447,0.0,1.0000000193237484,0.9948302805423737,0.9948302805423737,0.9869677934881369,1.0266323351373,1.0,0.996662777666282,1.001898169517517,1.002418577671051,0.999480813741684,0.0,1.0000000094925512,True,0.2517855167388916,20.956283569335938,37.95263671875,1.2006014347076417,0.7404038334293911,4.847845792770386
7,0.0625,topk,34,68,0.03266872838139534,16.0,0.27941176470588236,37.79255676269531,0.016590235754847527,0.9999998807907104,0.9294264912605286,0.9294264912605286,True,0.92149248862061,1.1765551969282848,1,0.9180898893363897,0.9817602038383484,0.9850007891654968,0.9967101216316223,0.0,0.9999999996613542,0.9557223320007324,0.9557223320007324,True,0.9282261869708717,1.1599715936576656,1,0.9151455468177054,0.9816917181015015,0.9843652248382568,0.9972839951515198,0.0,1.0000000193237484,0.9425744116306305,0.9425744116306305,0.9248593377957408,1.1682633952929753,1.0,0.9166177180770476,0.9817259609699249,0.9846830070018768,0.996997058391571,0.0,1.0000000094925512,True,0.6109375953674316,24.106861114501953,37.79255676269531,2.9729723930358887,1.6166695508104065,5.010573863983154
7,0.25,topk,34,68,0.06401377171278,16.0,0.23529411764705882,43.5586051940918,0.019121423363685608,0.9999998211860657,0.49111276865005493,0.49111276865005493,False,0.2688171105784862,8.592746492111639,10,0.2253665873346792,0.8156598806381226,0.8349953293800354,0.9768435955047607,0.0,0.9999999996613543,0.2865213453769684,0.6048542857170105,False,0.5898568845157557,2.044270647624854,2,0.5722995891672665,0.9635025262832642,0.9637085199356079,0.9997862577438354,0.0,1.0000000193237484,0.38881705701351166,0.5479835271835327,0.42933699754712096,5.318508569868246,6.0,0.39883308825097286,0.8895812034606934,0.8993519246578217,0.9883149266242981,0.0,1.0000000094925514,False,1.2636181116104126,37.243408203125,43.5584716796875,12.153236031532288,6.725416630318452,4.991008758544922
7,0.5,topk,34,68,0.0738476887345314,16.0,0.20588235294117646,45.49032211303711,0.019969413056969643,0.9999999403953552,0.517088770866394,0.517088770866394,False,0.22463170201967445,8.79703889886672,9,0.17482440999546306,0.7660134434700012,0.7935622930526733,0.9652845859527588,0.0,0.9999999996613542,0.3546500504016876,0.6106454730033875,False,0.5052903538128013,2.380990429133916,2,0.4793071850566551,0.9465901255607605,0.9470433592796326,0.9995214343070984,0.0,1.0000000193237484,0.43586941063404083,0.5638671219348907,0.36496102791623786,5.589014664000318,5.5,0.3270657975260591,0.8563017845153809,0.870302826166153,0.9824030101299286,0.0,1.0000000094925512,False,1.472717523574829,43.38744354248047,45.490360260009766,24.217897653579712,14.037717975172603,5.217089414596558
8,0.0,topk,34,68,0.0074674529023468494,16.0,0.014705882352941176,83.67562866210938,0.036732058972120285,0.9847607612609863,0.21986496448516846,0.9997815489768982,False,0.9998918854695029,1.0002162898186056,1,1.0000607747818357,1.0001585483551025,1.0001747608184814,0.9999837875366211,0.34246140578426626,0.9395318966756624,0.9997648596763611,0.9997648596763611,True,0.9998188243857588,1.000362478230281,1,1.0004287776658027,1.0006030797958374,1.0006153583526611,0.9999876022338867,0.007648751420426043,0.9999707671973244,0.6098149120807648,0.9997732043266296,0.9998553549276308,1.0002893840244433,1.0,1.0002447762238194,1.00038081407547,1.0003950595855713,0.9999856948852539,0.17505507860234615,0.9697513319364934,False,0.10718120634555817,17.614173889160156,83.67134857177734,0.10718120634555817,0.27208131510668093,4.642587661743164
8,0.025,topk,34,68,0.017013538628816605,16.0,0.20588235294117646,37.536277770996094,0.016477733850479126,0.9999997615814209,0.21524979174137115,0.9970359802246094,False,0.9928316263121332,1.0144832873069396,1,0.9952451120424232,0.9989706873893738,0.9993301033973694,0.9996402859687805,0.0,0.9999999996613542,0.9938783049583435,0.9938783049583435,True,0.9847284040177017,1.0312173338111446,1,0.9881299903103754,0.996281087398529,0.9966111183166504,0.9996688365936279,0.0,1.0000000193237484,0.6045640483498573,0.9954571425914764,0.9887800151649174,1.022850310559042,1.0,0.9916875511763993,0.9976258873939514,0.9979706108570099,0.9996545612812042,0.0,1.0000000094925512,False,0.2924651801586151,20.345643997192383,37.5361213684082,1.23086821436882,0.7304137612509598,4.624967575073242
8,0.0625,topk,34,68,0.033819619566202164,16.0,0.19117647058823528,41.250457763671875,0.018108190968632698,0.9999988079071045,0.8242829442024231,0.8242829442024231,False,0.7042194572269086,1.934707651212694,2,0.7097598469721341,0.9836993217468262,0.9870488047599792,0.9966065883636475,0.0,0.9999999996613541,0.6637001633644104,0.6956503987312317,False,0.9637736109470234,1.0761618871308578,1,0.9681082535428064,0.983734667301178,0.9845283031463623,0.9991938471794128,0.0,1.0000000193237482,0.7439915537834167,0.7599666714668274,0.833996534086966,1.5054347691717758,1.5,0.8389340502574703,0.9837169945240021,0.9857885539531708,0.9979002177715302,0.0,1.0000000094925512,False,0.6225160360336304,24.14976692199707,41.250335693359375,3.2006620168685913,1.6929189242974283,4.552154779434204
8,0.25,topk,34,68,0.06307976692914963,16.0,0.23529411764705882,40.260948181152344,0.017673814669251442,0.9999996423721313,0.37694263458251953,0.46612751483917236,False,0.32649727852501287,6.615629999852708,5,0.32364372209680825,0.8238980770111084,0.8355615139007568,0.986041247844696,0.0,0.9999999996613541,0.3334572911262512,0.6733211874961853,False,0.6354082377996538,1.9775525190875556,2,0.6161461185478804,0.9683512449264526,0.968499481678009,0.9998469352722168,0.0,1.0000000193237486,0.3551999628543854,0.5697243511676788,0.48095275816233335,4.296591259470132,3.5,0.4698949203223443,0.8961246609687805,0.9020304977893829,0.9929440915584564,0.0,1.0000000094925514,False,1.2989323139190674,48.074440002441406,40.261146545410156,11.364218950271606,6.198423413698078,4.73087739944458
8,0.5,topk,34,68,0.06965529918670654,16.0,0.14705882352941177,44.357662200927734,0.019472196698188782,0.9999996423721313,0.33396515250205994,0.4811936318874359,False,0.24617547997089162,9.350600507875404,9,0.19322038141805856,0.770359992980957,0.7914633750915527,0.9733362197875977,0.0,0.9999999996613542,0.3359358608722687,0.6089410185813904,False,0.5885989227810349,2.3000822052721257,2,0.5762431617389446,0.9692862033843994,0.9718269109725952,0.9973856210708618,0.0,1.0000000193237484,0.3349505066871643,0.5450673252344131,0.41738720137596325,5.825341356573765,5.5,0.3847317715785016,0.8698230981826782,0.881645143032074,0.9853609204292297,0.0,1.0000000094925512,False,1.4644696712493896,59.144309997558594,44.35737228393555,23.643155813217163,13.158551330647867,4.973474740982056
9,0.0,topk,34,68,0.007239387836307287,16.0,0.08823529411764706,76.28048706054688,0.03348572924733162,0.9767886400222778,0.9996723532676697,0.9996723532676697,True,0.9998586681799552,1.0002827257063085,1,1.0000245974149873,1.0001493692398071,1.0001709461212158,0.9999784231185913,0.0,0.999999999661354,0.9996429085731506,0.9996429085731506,True,0.9999426676838495,1.0001146386809212,1,1.0000893652836718,1.0001286268234253,1.0001475811004639,0.9999809861183167,0.0,1.0000000193237484,0.9996576309204102,0.9996576309204102,0.9999006679319024,1.0001986821936149,1.0,1.0000569813493296,1.0001389980316162,1.0001592636108398,0.999979704618454,0.0,1.0000000094925512,True,0.09665743261575699,16.58151626586914,76.28236389160156,0.09665743261575699,0.28087152168727214,4.861478090286255
9,0.025,topk,34,68,0.017930619418621063,16.0,0.2647058823529412,37.789878845214844,0.016589058563113213,0.9999994039535522,0.9966493248939514,0.9966493248939514,True,0.9904818052068334,1.0193009693135855,1,0.9951654898906621,1.0020508766174316,1.0025588274002075,0.9994933605194092,0.0,0.9999999996613543,0.9901168346405029,0.9901168346405029,True,0.9815391872881244,1.0379306618250097,1,0.9770651466529028,0.9934613108634949,0.993990957736969,0.999467134475708,0.0,1.0000000193237484,0.9933830797672272,0.9933830797672272,0.9860104962474789,1.0286158155692977,1.0,0.9861153182717824,0.9977560937404633,0.9982748925685883,0.9994802474975586,0.0,1.0000000094925514,True,0.30224645137786865,19.510263442993164,37.78987121582031,1.2469932317733765,0.692533662568838,4.978572130203247
9,0.0625,topk,34,68,0.03438573330640793,16.0,0.22058823529411764,38.90947341918945,0.01708053983747959,0.9999996423721313,0.9513183832168579,0.9513183832168579,True,0.9058539559492657,1.2174091781105336,1,0.910078718915516,0.9688920378684998,0.9742867350578308,0.9944629073143005,0.0,0.9999999996613542,0.9643582105636597,0.9643582105636597,True,0.937493603540921,1.1372628276902932,1,0.9437069789814291,0.9827588200569153,0.9857802391052246,0.9969350099563599,0.0,1.0000000193237482,0.9578382968902588,0.9578382968902588,0.9216737797450933,1.1773360029004134,1.0,0.9268928489484725,0.9758254289627075,0.9800334870815277,0.9956989586353302,0.0,1.0000000094925512,True,0.6039235591888428,26.404369354248047,38.9094123840332,3.035761833190918,1.651671506556493,4.937544107437134
9,0.25,topk,34,68,0.06379713863134384,16.0,0.23529411764705882,43.439884185791016,0.019069306552410126,0.9999997615814209,0.3006404936313629,0.7101903557777405,False,0.4930722649080234,3.143286555571226,3,0.506738933020041,0.9033753871917725,0.9178766012191772,0.9842013716697693,0.0,0.9999999996613542,0.21100951731204987,0.7754124402999878,False,0.6340633697212488,2.1207667188932624,2,0.6794391406046539,0.9422035217285156,0.953812837600708,0.9878284931182861,0.0,1.0000000193237484,0.2558250054717064,0.7428013980388641,0.5635678173146361,2.6320266372322445,2.5,0.5930890368123475,0.922789454460144,0.9358447194099426,0.9860149323940277,0.0,1.0000000094925512,False,1.2540602684020996,40.484825134277344,43.4402961730957,12.114134311676025,6.769848486121786,4.6685590744018555
9,0.5,topk,34,68,0.07797005027532578,16.0,0.16176470588235295,43.919498443603516,0.019279848784208298,0.9998307228088379,0.34306851029396057,0.630502462387085,False,0.3876132950492187,5.546759792263644,7,0.33235551953613746,0.7992866635322571,0.8232802748680115,0.9708561301231384,0.4967476711790658,0.8678950112201839,0.22738376259803772,0.7371605038642883,False,0.5650867382371922,2.9007352796969657,2,0.5071136842207823,0.8705867528915405,0.8899593353271484,0.9782320857048035,0.6500862037324583,0.7598604913826079,0.28522613644599915,0.6838314831256866,0.4763500166432055,4.223747535980305,4.5,0.4197346018784599,0.8349367082118988,0.85661980509758,0.974544107913971,0.573416937455762,0.813877751301396,False,1.579179048538208,44.09083938598633,43.91992950439453,23.539143800735474,13.578381348450678,5.025398254394531
10,0.0,topk,34,68,0.011521762236952782,16.0,0.029411764705882353,83.41680908203125,0.036618441343307495,0.9919884204864502,0.9675551652908325,0.9675551652908325,True,0.8528709979385369,1.3643036419984238,1,0.8485459693342111,0.9945043921470642,0.9945679903030396,0.9999361038208008,0.0,0.9999999996613542,0.9996239542961121,0.9996239542961121,True,0.9999012855323166,1.0001975092738558,1,0.9998469849119617,0.9999003410339355,0.999920129776001,0.9999802112579346,0.0,1.0000000193237484,0.9835895597934723,0.9835895597934723,0.9263861417354268,1.1822505756361399,1.0,0.9241964771230864,0.9972023665904999,0.9972440600395203,0.9999581575393677,0.0,1.0000000094925512,True,0.1579352170228958,16.67607879638672,83.41376495361328,0.1579352170228958,0.32068484813784176,4.48720645904541
10,0.025,topk,34,68,0.015923114493489265,16.0,0.29411764705882354,38.882347106933594,0.017068633809685707,0.9999998807907104,0.5300769209861755,0.5300769209861755,False,0.5141680382476357,2.2493563478461196,3,0.5187252613295653,1.001312255859375,1.0015537738800049,0.999758780002594,0.0,0.9999999996613541,0.7138057351112366,0.7138057351112366,False,0.5078002664037501,2.622411785088121,3,0.5132481437536821,0.9994949698448181,1.0000602006912231,0.999434769153595,0.0,1.0000000193237482,0.621941328048706,0.621941328048706,0.5109841523256928,2.4358840664671204,3.0,0.5159867025416237,1.0004036128520966,1.000806987285614,0.9995967745780945,0.0,1.0000000094925512,False,0.2662671208381653,21.9090576171875,38.88235855102539,1.2383260846138002,0.6985342085346719,4.902220964431763
10,0.0625,topk,34,68,0.03374230116605759,16.0,0.16176470588235295,40.424095153808594,0.017745433375239372,0.9999992251396179,0.9490066170692444,0.9490066170692444,True,0.9403091306581771,1.130664726321273,1,0.9317283573295225,0.9776580333709717,0.9822310209274292,0.9953442811965942,0.0,0.9999999996613543,0.9520738124847412,0.9520738124847412,True,0.9300868871632015,1.1549483860486014,1,0.9588110695714723,0.9780638813972473,0.9816219806671143,0.996375322341919,0.0,1.0000000193237484,0.9505402147769928,0.9505402147769928,0.9351980089106893,1.1428065561849372,1.0,0.9452697134504975,0.9778609573841095,0.9819265007972717,0.9958598017692566,0.0,1.0000000094925514,True,0.5985601544380188,25.188676834106445,40.424461364746094,3.1250889897346497,1.664836902770191,4.946430683135986
10,0.25,topk,34,68,0.06142009049654007,16.0,0.25,44.49652862548828,0.019533155485987663,0.9999998211860657,0.311506450176239,0.6842676401138306,False,0.5009337705123983,3.7087668658770925,3,0.4330775015830593,0.8563801646232605,0.8728740215301514,0.9811039566993713,0.0,0.9999999996613543,0.8055002689361572,0.8055002689361572,False,0.6719580310691371,2.1425952920876354,2,0.6530852465743108,0.9401799440383911,0.9492173790931702,0.9904791116714478,0.0,1.0000000193237484,0.5585033595561981,0.7448839545249939,0.5864459007907676,2.9256810789823637,2.5,0.5430813740786851,0.8982800543308258,0.9110457003116608,0.9857915341854095,0.0,1.0000000094925514,False,1.1948518753051758,40.432029724121094,44.496925354003906,12.319083213806152,6.9180641017976265,4.967921257019043
10,0.5,topk,34,68,0.0756266862154007,16.0,0.14705882352941177,46.32080841064453,0.02033397927880287,0.9999991655349731,0.5013201832771301,0.5013201832771301,False,0.14151213753173028,13.885846633048688,18,0.10828044622905257,0.7218773365020752,0.7423742413520813,0.9723900556564331,0.0,0.9999999996613541,0.7639997005462646,0.7639997005462646,False,0.646731235147521,2.3490219152229503,1,0.5791946918139563,0.8900945782661438,0.9031268954277039,0.9855697751045227,0.0,1.0000000193237484,0.6326599419116974,0.6326599419116974,0.39412168633962563,8.11743427413582,9.5,0.34373756902150443,0.8059859573841095,0.8227505683898926,0.9789799153804779,0.0,1.0000000094925512,False,1.4744584560394287,47.226985931396484,46.32075500488281,24.634835958480835,13.74427822095186,4.925954580307007
11,0.0,topk,34,68,0.007866745814681053,16.0,0.014705882352941176,86.60232543945312,0.038016825914382935,0.9994844198226929,0.9993850588798523,0.9993850588798523,True,0.9998525397982783,1.0002949460293735,1,0.9996122712670009,0.999749481678009,0.9997658729553223,0.9999836087226868,0.0,0.9999999996613541,0.6097444295883179,0.7765860557556152,False,0.6132977818715598,2.224211615159736,3,0.6110806482952195,0.9961159825325012,0.9961301684379578,0.9999858140945435,0.0,1.0000000193237486,0.8045647442340851,0.8879855573177338,0.806575160834919,1.6122532805945546,2.0,0.8053464597811102,0.9979327321052551,0.99794802069664,0.9999847114086151,0.0,1.0000000094925514,False,0.09753091633319855,18.133060455322266,86.60475158691406,0.09753091633319855,0.3212523594776543,4.986078500747681
11,0.025,topk,34,68,0.016639307141304016,16.0,0.25,38.436256408691406,0.016872812062501907,0.9999993443489075,0.9892939329147339,0.9892939329147339,True,0.989603806908794,1.0211110418843512,1,0.9969290766282151,1.0033515691757202,1.0035691261291504,0.9997832179069519,0.0,0.9999999996613543,0.5259157419204712,0.6117163300514221,False,0.7552112853554329,1.6668482520755616,3,0.7590294275327012,0.9999631643295288,1.0000711679458618,0.9998920559883118,0.0,1.0000000193237484,0.7576048374176025,0.800505131483078,0.8724075461321135,1.3439796469799563,2.0,0.8779792520804581,1.0016573667526245,1.001820147037506,0.9998376369476318,0.0,1.0000000094925514,False,0.27297940850257874,22.616506576538086,38.43622589111328,1.2338850557804109,0.797547920555023,4.688424587249756
11,0.0625,topk,34,68,0.0367954857647419,16.0,0.19117647058823528,42.5142707824707,0.018662981688976288,0.9999998211860657,0.7132495045661926,0.7132495045661926,False,0.9552667094331079,1.0954794591427695,1,0.9623319339693576,0.9934518337249756,0.9942551255226135,0.9991919994354248,0.0,0.9999999996613543,0.34568729996681213,0.8459131717681885,False,0.7133295524318852,1.8868898918053898,2,0.704945781467461,0.970753014087677,0.9754248857498169,0.9952104687690735,0.0,1.0000000193237484,0.5294684022665024,0.7795813381671906,0.8342981309324966,1.4911846754740796,1.5,0.8336388577184093,0.9821024239063263,0.9848400056362152,0.9972012341022491,0.0,1.0000000094925514,False,0.6724797487258911,23.96066665649414,42.5137939453125,3.3295918703079224,1.829745385186225,4.620531320571899
11,0.25,topk,34,68,0.057537876069545746,16.0,0.14705882352941177,49.148963928222656,0.02157549001276493,0.9999987483024597,0.37025558948516846,0.7968387603759766,False,0.729857527401693,1.8527711937430638,1,0.6762017853730194,0.9227902293205261,0.9352802038192749,0.9866457581520081,0.0,0.9999999996613542,0.7218103408813477,0.7218103408813477,False,0.517167301402141,3.4716416375506984,3,0.5148076837532717,0.8673426508903503,0.8861168622970581,0.9788129329681396,0.0,1.0000000193237484,0.5460329651832581,0.7593245506286621,0.623512414401917,2.662206415646881,2.0,0.5955047345631456,0.8950664401054382,0.9106985330581665,0.9827293455600739,0.0,1.0000000094925512,False,1.1001167297363281,43.880924224853516,49.149017333984375,13.387371063232422,8.067817568998253,4.891339063644409
11,0.5,topk,34,68,0.06950663775205612,16.0,0.1323529411764706,45.63069152832031,0.0200310330837965,0.9999998211860657,0.4629775583744049,0.47484907507896423,False,0.8795295190001214,1.2902349353860785,1,1.0397007069600541,0.9489761590957642,0.9496361613273621,0.999305009841919,0.0,0.9999999996613542,0.7241889238357544,0.7241889238357544,False,0.6667556194161274,2.2087999436294172,1,0.7428785891561657,0.8625149130821228,0.878638505935669,0.9816493391990662,0.0,1.0000000193237482,0.5935832411050797,0.5995189994573593,0.7731425692081244,1.749517439507748,1.0,0.8912896480581098,0.9057455360889435,0.9141373336315155,0.9904771745204926,0.0,1.0000000094925512,False,1.3254185914993286,49.94136047363281,45.630550384521484,24.14069378376007,13.822464853053722,5.019054651260376
````

# Appendix I — post-hoc condition means (exploratory)

````csv
architecture,m,beta,gram_excess_above_welch,frame_tightness_frobenius,pairs_cos_gt_099,pairs_cos_lt_neg099,pairs_abs_cos_gt_099,pairs_abs_cos_gt_095,random_direction_max_positive_cosine,planted_max_positive_cosine,planted_alignment_excess_over_random,best_contributing_atom_cosine,best_positive_read_atom_cosine,positive_read_gain_sum,negative_release_gain_sum,individual_gain_median,individual_gain_q10,individual_gain_fraction_gt_050,individual_gain_fraction_gt_075,individual_cross_gain_abs_mean,split_count_rel_05,split_count_rel_10,split_count_rel_20,split_count_rel_30,positive_read_split_count_rel_05,positive_read_split_count_rel_10,positive_read_split_count_rel_20,positive_read_split_count_rel_30,geometry_above_80,geometry_above_90,geometry_above_95
l1,68,0.0,46.71665954589844,9.663343988888355,0.0,1.4166666666666667,1.4166666666666667,2.25,0.3973095865520106,0.7082280442118645,0.3109184576598539,-0.2443733587861061,0.7074748103817304,0.4488043785095215,0.4515838138759136,0.8981241012612978,0.8906484842300415,1.0,1.0,0.013290147976173708,4.833333333333333,4.75,4.75,4.541666666666667,2.5,2.4583333333333335,2.4583333333333335,2.375,0.0,0.0,0.0
l1,68,0.025,4.593433380126953,3.0210743722101205,0.0,0.0,0.0,2.75,0.40640900175300976,0.8708349584291378,0.4644259566761281,0.6067098900675774,0.7946630883961916,0.6897131246514618,0.18503062745245794,0.8715911929806074,0.8375799432396889,1.0,0.9944444444444445,0.02014070251607336,2.625,2.2916666666666665,1.9166666666666667,1.9166666666666667,1.5833333333333333,1.5,1.5,1.5,0.75,0.75,0.75
l1,68,0.0625,4.927415529886882,3.116377701370721,0.08333333333333333,0.4166666666666667,0.5,11.166666666666666,0.4026964011970211,0.8179208661119143,0.41522446491489323,0.4718371480703354,0.81655713232855,0.5869213861102859,0.2671062193500499,0.8501616567373276,0.7759941443800926,0.9991512345679011,0.9497685185185185,0.013164951233193278,2.0416666666666665,1.5833333333333333,1.1666666666666667,1.125,3.7083333333333335,2.7916666666666665,1.8333333333333333,1.4583333333333333,0.7083333333333334,0.7083333333333334,0.5
l1,68,0.25,7.781589508056641,3.9250855762220476,0.9166666666666666,2.5833333333333335,3.5,22.25,0.39804831392519197,0.4819988552480936,0.08395054132290165,-0.35776570190985996,0.47824198690553504,0.3489221508304278,0.4508968846251567,0.7980846638480822,0.6830751250187556,0.9972222222222222,0.7084876543209876,0.03239422283756236,19.458333333333332,11.5,5.875,3.3333333333333335,14.125,9.208333333333334,5.5,3.7083333333333335,0.0,0.0,0.0
l1,68,0.5,9.679441452026367,4.385285582724708,2.0833333333333335,4.0,6.083333333333333,27.416666666666668,0.3964472501342706,0.45294258433083695,0.05649533419656627,-0.45349258929491043,0.45031384378671646,0.3526797431210677,0.44290339201688766,0.7981082747379938,0.6785132686297098,0.9962962962962963,0.7042438271604938,0.033171098213642836,23.125,13.666666666666666,6.541666666666667,4.125,15.625,10.625,6.083333333333333,4.166666666666667,0.0,0.0,0.0
topk,68,0.0,50.186497370402016,9.962315867378146,0.0,0.5833333333333334,0.5833333333333334,3.25,0.4014290753787649,0.8957777967055639,0.49434872132679897,0.5867307608326277,0.8532302484769995,0.8225911536574889,0.1767779521826469,0.9999155526359876,0.9889317378401756,0.9996913580246914,0.9989969135802469,0.002535374972391461,1.4583333333333333,1.4166666666666667,1.3333333333333333,1.25,2.0833333333333335,1.6666666666666667,1.3333333333333333,1.25,0.8333333333333334,0.6666666666666666,0.6666666666666666
topk,68,0.025,4.441173553466797,2.961544753194614,4.416666666666667,2.9166666666666665,7.333333333333333,9.083333333333334,0.39885959232067264,0.8470247692118088,0.44816517689113616,0.6825588966409365,0.8320466351384918,0.8640374623937532,0.13994598251883872,0.9981118688980738,0.9471323862671852,0.9993055555555554,0.9977623456790123,0.010847248563853404,1.375,1.3333333333333333,1.2083333333333333,1.2083333333333333,1.75,1.4583333333333333,1.2916666666666667,1.2083333333333333,0.75,0.6666666666666666,0.6666666666666666
topk,68,0.0625,5.689768155415853,3.3543968063740093,4.083333333333333,2.25,6.333333333333333,10.333333333333334,0.3967581054244876,0.740950937072436,0.3441928316479484,0.6001972580949465,0.7208240249504646,0.8213230241090059,0.1794148883006225,0.9837872758507729,0.8904959758122762,0.9983024691358025,0.9896604938271606,0.024786667432636023,1.7916666666666667,1.4166666666666667,1.2916666666666667,1.25,2.1666666666666665,1.7916666666666667,1.5416666666666667,1.4583333333333333,0.5,0.4583333333333333,0.20833333333333334
topk,68,0.25,9.085649808247885,4.2263703503136565,3.25,2.0833333333333335,5.333333333333333,17.916666666666668,0.3955287546154515,0.459812643006444,0.06428388839099247,-0.1065043459335963,0.39243256114423275,0.44807863763223094,0.48982284652690095,0.890005516509215,0.7316691651940346,0.9888888888888889,0.8591820987654321,0.05306821851991117,7.125,4.458333333333333,3.0416666666666665,2.0833333333333335,6.875,4.625,2.7916666666666665,2.0,0.041666666666666664,0.0,0.0
topk,68,0.5,10.979731877644857,4.665029503866299,4.833333333333333,2.1666666666666665,7.0,26.916666666666668,0.393801433269724,0.48658046250542003,0.09277902923569603,0.02066265046596527,0.4161079256640126,0.4606440843393405,0.43549932710205513,0.8527972276012102,0.6819557050863901,0.9789351851851852,0.7655864197530864,0.05505323914500574,10.083333333333334,6.083333333333333,3.25,2.375,7.958333333333333,5.541666666666667,3.3333333333333335,2.4583333333333335,0.0,0.0,0.0
````

# Appendix J — post-hoc structured summary (exploratory)

````json
{
  "l1": {
    "best_contributing_atom_cosine": {
      "ci95_lower": -0.42244794871658087,
      "ci95_upper": 0.03062314220393674,
      "mean_difference": -0.20911923050880432,
      "negative_seeds": 7,
      "positive_seeds": 5
    },
    "best_positive_read_atom_cosine": {
      "ci95_lower": -0.3161710185930133,
      "ci95_upper": -0.2057627244231602,
      "mean_difference": -0.2571609665950139,
      "negative_seeds": 12,
      "positive_seeds": 0
    },
    "geometry_above_80": {
      "ci95_lower": 0.0,
      "ci95_upper": 0.0,
      "mean_difference": 0.0,
      "negative_seeds": 0,
      "positive_seeds": 0
    },
    "geometry_above_90": {
      "ci95_lower": 0.0,
      "ci95_upper": 0.0,
      "mean_difference": 0.0,
      "negative_seeds": 0,
      "positive_seeds": 0
    },
    "geometry_above_95": {
      "ci95_lower": 0.0,
      "ci95_upper": 0.0,
      "mean_difference": 0.0,
      "negative_seeds": 0,
      "positive_seeds": 0
    },
    "gram_excess_above_welch": {
      "ci95_lower": -38.67467901706696,
      "ci95_upper": -35.224971365928646,
      "mean_difference": -37.03721809387207,
      "negative_seeds": 12,
      "positive_seeds": 0
    },
    "individual_cross_gain_abs_mean": {
      "ci95_lower": 0.01708059602048403,
      "ci95_upper": 0.023555861803955244,
      "mean_difference": 0.019880950237469126,
      "negative_seeds": 0,
      "positive_seeds": 12
    },
    "individual_gain_fraction_gt_050": {
      "ci95_lower": -0.0060956790123456546,
      "ci95_upper": -0.0016203703703703647,
      "mean_difference": -0.0037037037037037,
      "negative_seeds": 8,
      "positive_seeds": 0
    },
    "individual_gain_median": {
      "ci95_lower": -0.10697669554501772,
      "ci95_upper": -0.09412677455693483,
      "mean_difference": -0.10001582652330399,
      "negative_seeds": 12,
      "positive_seeds": 0
    },
    "individual_gain_q10": {
      "ci95_lower": -0.22567231400559346,
      "ci95_upper": -0.19891651788105566,
      "mean_difference": -0.21213521560033163,
      "negative_seeds": 12,
      "positive_seeds": 0
    },
    "negative_release_gain_sum": {
      "ci95_lower": -0.05624049659818411,
      "ci95_upper": 0.04209905490279192,
      "mean_difference": -0.008680421859025955,
      "negative_seeds": 6,
      "positive_seeds": 6
    },
    "pairs_abs_cos_gt_099": {
      "ci95_lower": 3.25,
      "ci95_upper": 6.083333333333333,
      "mean_difference": 4.666666666666667,
      "negative_seeds": 0,
      "positive_seeds": 11
    },
    "pairs_cos_lt_neg099": {
      "ci95_lower": 1.4166666666666667,
      "ci95_upper": 3.8333333333333335,
      "mean_difference": 2.5833333333333335,
      "negative_seeds": 1,
      "positive_seeds": 10
    },
    "planted_alignment_excess_over_random": {
      "ci95_lower": -0.31016563294608634,
      "ci95_upper": -0.2060726408053976,
      "mean_difference": -0.2544231234632876,
      "negative_seeds": 12,
      "positive_seeds": 0
    },
    "planted_max_positive_cosine": {
      "ci95_lower": -0.31184676128129163,
      "ci95_upper": -0.20690738974759978,
      "mean_difference": -0.2552854598810275,
      "negative_seeds": 12,
      "positive_seeds": 0
    },
    "positive_read_gain_sum": {
      "ci95_lower": -0.14561515625876684,
      "ci95_upper": -0.051626843943571095,
      "mean_difference": -0.0961246353884538,
      "negative_seeds": 10,
      "positive_seeds": 2
    },
    "positive_read_split_count_rel_05": {
      "ci95_lower": 11.416666666666666,
      "ci95_upper": 15.083333333333334,
      "mean_difference": 13.125,
      "negative_seeds": 0,
      "positive_seeds": 12
    },
    "positive_read_split_count_rel_10": {
      "ci95_lower": 6.5,
      "ci95_upper": 10.25,
      "mean_difference": 8.166666666666666,
      "negative_seeds": 0,
      "positive_seeds": 12
    },
    "positive_read_split_count_rel_20": {
      "ci95_lower": 2.0,
      "ci95_upper": 5.583333333333333,
      "mean_difference": 3.625,
      "negative_seeds": 0,
      "positive_seeds": 12
    },
    "positive_read_split_count_rel_30": {
      "ci95_lower": 0.6666666666666666,
      "ci95_upper": 3.0833333333333335,
      "mean_difference": 1.7916666666666667,
      "negative_seeds": 1,
      "positive_seeds": 11
    },
    "random_direction_max_positive_cosine": {
      "ci95_lower": -0.0034269337769555763,
      "ci95_upper": 0.0017746093909034246,
      "mean_difference": -0.0008623364177399543,
      "negative_seeds": 8,
      "positive_seeds": 4
    },
    "split_count_rel_05": {
      "ci95_lower": 16.332291666666666,
      "ci95_upper": 20.458333333333332,
      "mean_difference": 18.291666666666668,
      "negative_seeds": 0,
      "positive_seeds": 12
    },
    "split_count_rel_10": {
      "ci95_lower": 6.916666666666667,
      "ci95_upper": 11.041666666666666,
      "mean_difference": 8.916666666666666,
      "negative_seeds": 0,
      "positive_seeds": 12
    },
    "split_count_rel_20": {
      "ci95_lower": 0.8333333333333334,
      "ci95_upper": 2.7916666666666665,
      "mean_difference": 1.7916666666666667,
      "negative_seeds": 1,
      "positive_seeds": 11
    },
    "split_count_rel_30": {
      "ci95_lower": -1.0833333333333333,
      "ci95_upper": 0.20833333333333334,
      "mean_difference": -0.4166666666666667,
      "negative_seeds": 6,
      "positive_seeds": 4
    }
  },
  "topk": {
    "best_contributing_atom_cosine": {
      "ci95_lower": -0.9866939784493298,
      "ci95_upper": -0.13673727805726305,
      "mean_difference": -0.5660681103666624,
      "negative_seeds": 9,
      "positive_seeds": 3
    },
    "best_positive_read_atom_cosine": {
      "ci95_lower": -0.5834478673583362,
      "ci95_upper": -0.29165677886145847,
      "mean_difference": -0.43712232281298685,
      "negative_seeds": 11,
      "positive_seeds": 1
    },
    "geometry_above_80": {
      "ci95_lower": -0.9583333333333334,
      "ci95_upper": -0.7083333333333334,
      "mean_difference": -0.8333333333333334,
      "negative_seeds": 12,
      "positive_seeds": 0
    },
    "geometry_above_90": {
      "ci95_lower": -0.875,
      "ci95_upper": -0.4583333333333333,
      "mean_difference": -0.6666666666666666,
      "negative_seeds": 10,
      "positive_seeds": 0
    },
    "geometry_above_95": {
      "ci95_lower": -0.875,
      "ci95_upper": -0.4583333333333333,
      "mean_difference": -0.6666666666666666,
      "negative_seeds": 10,
      "positive_seeds": 0
    },
    "gram_excess_above_welch": {
      "ci95_lower": -45.60810316403707,
      "ci95_upper": -33.21102457046509,
      "mean_difference": -39.206765492757164,
      "negative_seeds": 12,
      "positive_seeds": 0
    },
    "individual_cross_gain_abs_mean": {
      "ci95_lower": 0.047442564535121315,
      "ci95_upper": 0.0576088734470981,
      "mean_difference": 0.05251786417261428,
      "negative_seeds": 0,
      "positive_seeds": 12
    },
    "individual_gain_fraction_gt_050": {
      "ci95_lower": -0.025462962962962955,
      "ci95_upper": -0.016358024691358015,
      "mean_difference": -0.02075617283950616,
      "negative_seeds": 12,
      "positive_seeds": 0
    },
    "individual_gain_median": {
      "ci95_lower": -0.1665594334403674,
      "ci95_upper": -0.12806647134323926,
      "mean_difference": -0.14711832503477731,
      "negative_seeds": 12,
      "positive_seeds": 0
    },
    "individual_gain_q10": {
      "ci95_lower": -0.3359254486858845,
      "ci95_upper": -0.27730843530346955,
      "mean_difference": -0.30697603275378543,
      "negative_seeds": 12,
      "positive_seeds": 0
    },
    "negative_release_gain_sum": {
      "ci95_lower": 0.08315175529140788,
      "ci95_upper": 0.42779508936609406,
      "mean_difference": 0.2587213749194082,
      "negative_seeds": 3,
      "positive_seeds": 9
    },
    "pairs_abs_cos_gt_099": {
      "ci95_lower": 4.916666666666667,
      "ci95_upper": 7.833333333333333,
      "mean_difference": 6.416666666666667,
      "negative_seeds": 0,
      "positive_seeds": 12
    },
    "pairs_cos_lt_neg099": {
      "ci95_lower": 0.8333333333333334,
      "ci95_upper": 2.3333333333333335,
      "mean_difference": 1.5833333333333333,
      "negative_seeds": 1,
      "positive_seeds": 9
    },
    "planted_alignment_excess_over_random": {
      "ci95_lower": -0.48912156573320814,
      "ci95_upper": -0.32029362686593227,
      "mean_difference": -0.40156969209110294,
      "negative_seeds": 12,
      "positive_seeds": 0
    },
    "planted_max_positive_cosine": {
      "ci95_lower": -0.4968378593524297,
      "ci95_upper": -0.3272525395577154,
      "mean_difference": -0.4091973342001438,
      "negative_seeds": 12,
      "positive_seeds": 0
    },
    "positive_read_gain_sum": {
      "ci95_lower": -0.5579888171878016,
      "ci95_upper": -0.14809374688232269,
      "mean_difference": -0.36194706931814835,
      "negative_seeds": 10,
      "positive_seeds": 2
    },
    "positive_read_split_count_rel_05": {
      "ci95_lower": 3.1666666666666665,
      "ci95_upper": 8.583333333333334,
      "mean_difference": 5.875,
      "negative_seeds": 1,
      "positive_seeds": 11
    },
    "positive_read_split_count_rel_10": {
      "ci95_lower": 1.75,
      "ci95_upper": 6.083333333333333,
      "mean_difference": 3.875,
      "negative_seeds": 1,
      "positive_seeds": 10
    },
    "positive_read_split_count_rel_20": {
      "ci95_lower": 0.8333333333333334,
      "ci95_upper": 3.2916666666666665,
      "mean_difference": 2.0,
      "negative_seeds": 2,
      "positive_seeds": 9
    },
    "positive_read_split_count_rel_30": {
      "ci95_lower": 0.3333333333333333,
      "ci95_upper": 2.2083333333333335,
      "mean_difference": 1.2083333333333333,
      "negative_seeds": 2,
      "positive_seeds": 7
    },
    "random_direction_max_positive_cosine": {
      "ci95_lower": -0.010218280766962861,
      "ci95_upper": -0.004998146713049451,
      "mean_difference": -0.0076276421090408775,
      "negative_seeds": 11,
      "positive_seeds": 1
    },
    "split_count_rel_05": {
      "ci95_lower": 6.166666666666667,
      "ci95_upper": 11.0,
      "mean_difference": 8.625,
      "negative_seeds": 0,
      "positive_seeds": 11
    },
    "split_count_rel_10": {
      "ci95_lower": 2.7916666666666665,
      "ci95_upper": 6.541666666666667,
      "mean_difference": 4.666666666666667,
      "negative_seeds": 1,
      "positive_seeds": 10
    },
    "split_count_rel_20": {
      "ci95_lower": 0.7083333333333334,
      "ci95_upper": 3.1666666666666665,
      "mean_difference": 1.9166666666666667,
      "negative_seeds": 3,
      "positive_seeds": 8
    },
    "split_count_rel_30": {
      "ci95_lower": 0.3333333333333333,
      "ci95_upper": 2.0,
      "mean_difference": 1.125,
      "negative_seeds": 2,
      "positive_seeds": 7
    }
  }
}
````

# Appendix K — complete post-hoc per-run metrics (120 rows; exploratory)

````csv
architecture,m,seed,beta,gram_sum_recomputed,welch_floor,gram_excess_above_welch,frame_tightness_frobenius,pairs_cos_gt_099,pairs_cos_lt_neg099,pairs_abs_cos_gt_099,pairs_abs_cos_gt_095,random_direction_max_positive_cosine,planted_max_positive_cosine,best_contributing_atom_cosine,best_positive_read_atom_cosine,positive_read_gain_sum,negative_release_gain_sum,individual_gain_median,individual_gain_q10,individual_gain_q90,individual_gain_fraction_gt_050,individual_gain_fraction_gt_075,individual_cross_gain_abs_mean,split_count_rel_05,positive_read_split_count_rel_05,split_count_rel_10,positive_read_split_count_rel_10,split_count_rel_20,positive_read_split_count_rel_20,split_count_rel_30,positive_read_split_count_rel_30,geometry_above_80,geometry_above_90,geometry_above_95,planted_alignment_excess_over_random
l1,68,0,0.025,38.98258972167969,34.0,4.9825897216796875,3.156768103169705,0,0,0,4,0.4045503899817951,0.9875606000423431,0.9875606000423431,0.9875606000423431,0.8062876760959625,0.052901607006788254,0.8541675806045532,0.8096368312835693,0.9135810434818268,1.0,0.9925925925925926,0.01064955536276102,1.5,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5830102100605481
l1,68,0,0.0625,39.97911834716797,34.0,5.979118347167969,3.4580672689583376,0,0,0,5,0.4039384494349825,0.9804298579692841,0.9804298579692841,0.9804298579692841,0.8074392974376678,0.05051775462925434,0.8555620312690735,0.7910263240337372,0.9276768565177917,1.0,0.9814814814814815,0.01309152552857995,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5764914085343016
l1,68,0,0.25,44.11572265625,34.0,10.11572265625,4.497938161915463,3,3,6,19,0.3946740490939538,0.5006933957338333,-0.5807104408740997,0.5006933957338333,0.40384261310100555,0.3609755039215088,0.7709487974643707,0.6382985711097717,0.8799735009670258,0.9861111111111112,0.6166666666666667,0.0460505411028862,17.5,16.0,9.5,8.5,4.0,4.0,2.5,3.5,0.0,0.0,0.0,0.1060193466398795
l1,68,0,0.5,46.44683074951172,34.0,12.446830749511719,4.9893552869095155,4,2,6,24,0.3916741947856905,0.49683018028736115,-0.5430824607610703,0.4927430748939514,0.4809005707502365,0.29443497955799103,0.7696835100650787,0.6729846298694611,0.8695507645606995,0.9962962962962962,0.6129629629629629,0.0481309425085783,23.0,17.5,13.5,9.5,5.5,5.0,4.5,4.0,0.0,0.0,0.0,0.10515598550167066
l1,68,0,0.0,76.50013732910156,34.0,42.50013732910156,9.219559279709273,0,2,2,2,0.39949077352823126,0.7101890742778778,-0.014917135238647461,0.7058558464050293,0.4531535804271698,0.44591300189495087,0.8986914753913879,0.8954320251941681,0.901963472366333,1.0,1.0,0.011130549479275942,4.0,2.0,4.0,2.0,4.0,2.0,4.0,2.0,0.0,0.0,0.0,0.31069830074964655
l1,68,1,0.025,37.96098327636719,34.0,3.9609832763671875,2.8145992582140718,0,0,0,4,0.40483734974345265,0.987806499004364,0.987806499004364,0.987806499004364,0.8211857378482819,0.037299247458577156,0.8551012873649597,0.8161625266075134,0.9052216112613678,1.0,0.9944444444444445,0.009316476993262768,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5829691492609114
l1,68,1,0.0625,40.54355239868164,34.0,6.543552398681641,3.6176104792843993,0,0,0,12,0.4051718817975397,0.7644646167755127,0.0032198727130889893,0.7644646167755127,0.4475523382425308,0.4061802886426449,0.847955584526062,0.7744944095611572,0.9468234479427338,1.0,0.962037037037037,0.015642856247723103,2.5,4.5,1.0,3.0,1.0,2.0,1.0,1.5,0.5,0.5,0.0,0.359292734977973
l1,68,1,0.25,42.36760330200195,34.0,8.367603302001953,4.090868948624617,1,2,3,26,0.3976172169319617,0.5301021337509155,-0.0815085768699646,0.5301021337509155,0.3675808906555176,0.41599664092063904,0.7862014472484589,0.6916545629501343,0.8714181184768677,1.0,0.6768518518518518,0.0316274194046855,26.5,13.5,18.0,8.5,11.0,5.0,6.0,3.5,0.0,0.0,0.0,0.1324849168189538
l1,68,1,0.5,42.36481475830078,34.0,8.364814758300781,4.090187253196661,1,4,5,25,0.3951086545977214,0.5139775723218918,-0.5223209708929062,0.5139775723218918,0.3955484479665756,0.39417755603790283,0.7920497357845306,0.6970260441303253,0.8756458163261414,1.0,0.7240740740740741,0.03333929181098938,30.0,15.5,17.0,8.5,9.0,5.0,4.5,2.5,0.0,0.0,0.0,0.11886891772417041
l1,68,1,0.0,84.54144287109375,34.0,50.54144287109375,10.053998477187534,0,2,2,2,0.3983846091698183,0.7082566320896149,-0.014139264822006226,0.7082566320896149,0.4478537440299988,0.45151858031749725,0.8987298011779785,0.8962144553661346,0.9019664824008942,1.0,1.0,0.01264261594042182,4.0,2.0,4.0,2.0,4.0,2.0,4.0,2.0,0.0,0.0,0.0,0.30987202291979654
l1,68,2,0.025,38.04624938964844,34.0,4.0462493896484375,2.844731696969194,0,0,0,2,0.4053658499430628,0.9819954037666321,0.9819954037666321,0.9819954037666321,0.8365727066993713,0.02722783014178276,0.8595503866672516,0.8247222006320953,0.9049567580223083,1.0,0.9972222222222222,0.008522186428308487,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.5,1.0,1.0,1.0,0.5766295538235693
l1,68,2,0.0625,39.90963363647461,34.0,5.909633636474609,3.437916327777764,1,0,1,12,0.39748943440925344,0.9225142598152161,0.9225142598152161,0.9225142598152161,0.7178816795349121,0.1257602907717228,0.8420495986938477,0.7562499940395355,0.9339615404605865,0.999074074074074,0.9194444444444445,0.017453227192163467,2.5,2.0,2.0,1.5,1.5,1.5,1.0,1.0,1.0,1.0,0.0,0.5250248254059626
l1,68,2,0.25,42.20197677612305,34.0,8.201976776123047,4.050178738025963,0,3,3,23,0.3969561663345779,0.46176235377788544,-0.6249517798423767,0.46176235377788544,0.30332548171281815,0.504955381155014,0.7972298860549927,0.6794335544109344,0.904581606388092,0.9953703703703703,0.7092592592592593,0.030959442257881165,14.5,13.5,9.5,10.0,3.5,5.5,1.5,3.5,0.0,0.0,0.0,0.06480618744330752
l1,68,2,0.5,44.532325744628906,34.0,10.532325744628906,4.589624386663251,2,3,5,30,0.39781494874435047,0.47554343938827515,-0.5943375527858734,0.47554343938827515,0.3229219764471054,0.4677542597055435,0.799940437078476,0.6517232060432434,0.8910900950431824,0.9981481481481482,0.6962962962962963,0.029205959290266037,18.5,13.0,9.0,8.5,4.5,3.0,3.0,3.0,0.0,0.0,0.0,0.07772849064392467
l1,68,2,0.0,79.57963562011719,34.0,45.57963562011719,9.547735883255198,0,2,2,2,0.3996319037303747,0.7094728350639343,-0.01279217004776001,0.7094728350639343,0.4490360766649246,0.4498865604400635,0.8984826803207397,0.896329402923584,0.9009574353694916,1.0,1.0,0.01269376976415515,4.0,2.0,4.0,2.0,4.0,2.0,4.0,2.0,0.0,0.0,0.0,0.3098409313335596
l1,68,3,0.025,38.38547134399414,34.0,4.385471343994141,2.9615778001851183,0,0,0,2,0.4121086143251813,0.5793470665812492,-0.008503377437591553,0.4160430580377579,0.4376301411539316,0.4482434391975403,0.8841506242752075,0.8631843328475952,0.9074288308620453,1.0,1.0,0.04440154321491718,3.0,1.5,3.0,1.5,2.0,1.5,2.0,1.5,0.5,0.5,0.5,0.16723845225606793
l1,68,3,0.0625,36.86210632324219,34.0,2.8621063232421875,2.392531962602998,0,0,0,12,0.40039237064712974,0.7083734571933746,0.006708800792694092,0.7083734571933746,0.4340161234140396,0.4241557866334915,0.8497344553470612,0.7680900394916534,0.957911342382431,1.0,0.9472222222222222,0.012132711708545685,2.0,4.0,1.5,2.0,1.0,1.5,1.0,1.0,0.5,0.5,0.5,0.3079810865462449
l1,68,3,0.25,41.938751220703125,34.0,7.938751220703125,3.984658812842377,1,2,3,25,0.397908695145403,0.4977869540452957,0.013802051544189453,0.49141187965869904,0.3655490428209305,0.4473661780357361,0.804636150598526,0.7097710967063904,0.891165554523468,1.0,0.7694444444444445,0.0349538940936327,15.5,14.0,10.0,9.5,3.0,6.5,1.5,4.0,0.0,0.0,0.0,0.09987825889989271
l1,68,3,0.5,41.573001861572266,34.0,7.573001861572266,3.8917867782347946,4,4,8,32,0.39617246367588677,0.5094291418790817,-0.5294252634048462,0.5094291418790817,0.40510910749435425,0.39196014404296875,0.7982648015022278,0.6963485479354858,0.896742969751358,1.0,0.7379629629629629,0.03447102755308151,26.0,13.0,17.5,9.0,7.0,4.0,5.0,2.5,0.0,0.0,0.0,0.11325667820319496
l1,68,3,0.0,80.70196533203125,34.0,46.70196533203125,9.664571373072599,0,1,1,2,0.3968980756482271,0.7094401121139526,-0.7017998993396759,0.7094401121139526,0.44371213018894196,0.4579179435968399,0.8982725739479065,0.8909792006015778,0.9098257720470428,1.0,1.0,0.01507573015987873,6.0,3.0,6.0,3.0,6.0,3.0,4.0,2.0,0.0,0.0,0.0,0.31254203646572554
l1,68,4,0.025,38.184635162353516,34.0,4.184635162353516,2.8929687649663602,0,0,0,2,0.4067172314758085,0.9878435730934143,0.9878435730934143,0.9878435730934143,0.7960369288921356,0.062243130058050156,0.854891300201416,0.8099165558815002,0.9073061645030975,1.0,0.9916666666666667,0.0096672885119915,1.5,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5811263416176058
l1,68,4,0.0625,37.93595886230469,34.0,3.9359588623046875,2.805693385233293,0,1,1,9,0.40294344590857956,0.8660705387592316,0.8660705387592316,0.8660705387592316,0.6532743871212006,0.18377044796943665,0.8367946147918701,0.7516163289546967,0.9217362701892853,0.999074074074074,0.8861111111111111,0.014100185595452785,5.5,3.0,4.0,2.5,2.0,1.5,2.0,1.5,0.5,0.5,0.5,0.463127092850652
l1,68,4,0.25,40.085426330566406,34.0,6.085426330566406,3.488674989654147,0,1,1,20,0.3968972636970641,0.499351367354393,-0.5414611101150513,0.499351367354393,0.3633143901824951,0.4399183839559555,0.8050566017627716,0.6961550414562225,0.8986614048480988,1.0,0.7296296296296296,0.03528500720858574,24.5,13.0,16.0,9.0,8.5,4.0,6.0,3.5,0.0,0.0,0.0,0.10245410365732893
l1,68,4,0.5,43.121604919433594,34.0,9.121604919433594,4.271207622582883,1,3,4,26,0.397975290003026,0.5055505931377411,-0.5220576226711273,0.5055505931377411,0.3753352761268616,0.43167462944984436,0.8072153329849243,0.7122688889503479,0.8966273665428162,1.0,0.7592592592592593,0.031003043986856937,28.5,14.5,21.0,10.0,9.5,5.5,6.0,3.5,0.0,0.0,0.0,0.10757530313471508
l1,68,4,0.0,78.00211334228516,34.0,44.002113342285156,9.381057242528893,0,1,1,3,0.3943796002359348,0.7034593224525452,-0.016885221004486084,0.7034593224525452,0.45063668489456177,0.4500371217727661,0.8982231318950653,0.8930641412734985,0.9047443270683289,1.0,1.0,0.01275899913161993,5.0,3.0,5.0,3.0,5.0,3.0,5.0,3.0,0.0,0.0,0.0,0.30907972221661034
l1,68,5,0.025,40.00270080566406,34.0,6.0027008056640625,3.4648803034229956,0,0,0,4,0.4011519665258095,0.9824374914169312,0.9824374914169312,0.9824374914169312,0.7971054315567017,0.05982218403369188,0.8539081811904907,0.7928507626056671,0.916788786649704,1.0,0.9648148148148148,0.00962037080898881,1.5,1.0,1.5,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5812855248911217
l1,68,5,0.0625,38.51565170288086,34.0,4.515651702880859,3.0052133539384154,0,1,1,11,0.4034066398550763,0.9357573390007019,0.9357573390007019,0.9357573390007019,0.735342413187027,0.11506963521242142,0.8487342894077301,0.7690329253673553,0.941315084695816,0.9972222222222222,0.9342592592592592,0.013946454040706158,2.0,1.5,2.0,1.5,1.0,1.0,1.0,1.0,1.0,1.0,0.5,0.5323506991456256
l1,68,5,0.25,39.95549011230469,34.0,5.9554901123046875,3.4512291510181567,1,3,4,21,0.39697100413973724,0.557429164648056,-0.05196830630302429,0.557429164648056,0.39960169792175293,0.3944982886314392,0.7977782487869263,0.6894956827163696,0.8934876322746277,0.9981481481481482,0.7185185185185186,0.031089548021554947,22.5,11.0,11.5,6.0,6.5,3.5,3.0,2.0,0.0,0.0,0.0,0.1604581605083188
l1,68,5,0.5,40.94377899169922,34.0,6.943778991699219,3.7266007117440436,2,7,9,28,0.3954046637279825,0.42971087992191315,-0.07524809241294861,0.42971087992191315,0.3296343982219696,0.46470968425273895,0.8067205250263214,0.6622396111488342,0.9056296944618225,0.9879629629629629,0.7240740740740741,0.029109678231179714,20.0,13.0,8.0,8.5,3.5,6.0,2.0,4.5,0.0,0.0,0.0,0.03430621619393065
l1,68,5,0.0,79.0263442993164,34.0,45.026344299316406,9.489608981445288,0,1,1,2,0.4023556141016329,0.7075736224651337,-0.7012591660022736,0.7075736224651337,0.44573424756526947,0.4564232677221298,0.8976589143276215,0.8931600153446198,0.9055685997009277,1.0,1.0,0.016463940497487783,5.0,2.5,5.0,2.5,5.0,2.5,5.0,2.5,0.0,0.0,0.0,0.30521800836350077
l1,68,6,0.025,38.173187255859375,34.0,4.173187255859375,2.8890104083773482,0,0,0,4,0.40869900180480667,0.610779881477356,0.009421020746231079,0.42257992178201675,0.4457586668431759,0.43789383582770824,0.8818379640579224,0.858934760093689,0.9098640978336334,1.0,1.0,0.04175468720495701,3.0,1.5,3.0,1.5,2.0,1.5,2.0,1.5,0.5,0.5,0.5,0.20208087967254929
l1,68,6,0.0625,39.21888732910156,34.0,5.2188873291015625,3.2307552161119615,0,1,1,13,0.4024631855993455,0.615085743367672,0.01237604022026062,0.5987209379673004,0.42368342354893684,0.4288551677018404,0.8514809012413025,0.781604140996933,0.9306737780570984,0.9953703703703705,0.9546296296296296,0.010283239651471376,1.5,8.0,1.0,6.5,1.0,4.0,1.0,3.0,0.5,0.5,0.5,0.21262255776832645
l1,68,6,0.25,40.868255615234375,34.0,6.868255615234375,3.706279751659019,1,4,5,21,0.3992012499244162,0.5236575603485107,-0.09653045237064362,0.5106998533010483,0.43802741169929504,0.35675884783267975,0.7938708662986755,0.704819917678833,0.8858312368392944,1.0,0.7240740740740741,0.031746966764330864,27.0,15.0,16.5,8.5,8.5,5.0,4.5,2.5,0.0,0.0,0.0,0.12445631042409455
l1,68,6,0.5,44.74092102050781,34.0,10.740921020507812,4.634850455911808,1,6,7,28,0.39741618812243695,0.5135719925165176,-0.5263873189687729,0.5135719925165176,0.40703365206718445,0.3917282968759537,0.7991803884506226,0.7165014743804932,0.8817404508590698,1.0,0.7583333333333333,0.030408932827413082,26.5,16.5,18.5,11.0,9.5,5.5,5.5,2.5,0.0,0.0,0.0,0.11615580439408069
l1,68,6,0.0,82.21036529541016,34.0,48.210365295410156,9.819405856188975,0,0,0,3,0.3913743751022138,0.703958660364151,-0.01492723822593689,0.703958660364151,0.4508557617664337,0.4532674252986908,0.8977068662643433,0.8910359740257263,0.9089083075523376,1.0,1.0,0.012213073205202818,6.0,3.5,6.0,3.5,6.0,3.5,6.0,3.5,0.0,0.0,0.0,0.3125842852619372
l1,68,7,0.025,39.43334197998047,34.0,5.433341979980469,3.296464223075086,0,0,0,3,0.403738297872668,0.9804023802280426,0.7014772891998291,0.7014772891998291,0.8003596663475037,0.08070779219269753,0.8792617917060852,0.8554340898990631,0.9105812013149261,1.0,0.9981481481481481,0.04772365093231201,3.0,2.0,3.0,2.0,2.0,2.0,2.0,2.0,1.0,1.0,1.0,0.5766640823553746
l1,68,7,0.0625,37.73134994506836,34.0,3.7313499450683594,2.731793847291102,0,0,0,10,0.4092967283243457,0.7421630024909973,-0.004214227199554443,0.7421630024909973,0.43222928047180176,0.4279066640883684,0.8558115065097809,0.7988686263561249,0.9268167614936829,1.0,0.9935185185185185,0.010823433753103018,1.0,5.0,1.0,4.0,1.0,1.5,1.0,1.0,0.5,0.5,0.5,0.3328662741666516
l1,68,7,0.25,40.863426208496094,34.0,6.863426208496094,3.7049768468505455,1,3,4,22,0.406477588608415,0.3458896800875664,-0.6488598883152008,0.3277885541319847,0.23938565701246262,0.5692953616380692,0.8097592890262604,0.6895565688610077,0.9129355847835541,1.0,0.7277777777777779,0.02876316849142313,19.5,20.0,11.0,15.0,6.5,9.5,3.5,7.0,0.0,0.0,0.0,-0.06058790852084861
l1,68,7,0.5,43.96062469482422,34.0,9.960624694824219,4.463323609911838,2,6,8,28,0.40235434812778853,0.3776182681322098,-0.5840894728899002,0.36367131769657135,0.28041981905698776,0.5102540552616119,0.800693154335022,0.6594291925430298,0.8923861384391785,0.9907407407407407,0.7027777777777777,0.029919915832579136,18.5,16.5,12.0,12.5,6.5,7.0,4.0,6.0,0.0,0.0,0.0,-0.024736079995578752
l1,68,7,0.0,81.4818115234375,34.0,47.4818115234375,9.74492890627111,0,1,1,2,0.40021863693077264,0.7067927420139313,-0.7011590898036957,0.7067927420139313,0.44267258048057556,0.4591725766658783,0.8983747065067291,0.8914429545402527,0.90745809674263,1.0,1.0,0.015340540558099747,6.0,3.0,6.0,3.0,6.0,3.0,5.5,3.0,0.0,0.0,0.0,0.30657410508315863
l1,68,8,0.025,37.881500244140625,34.0,3.881500244140625,2.7862158517106734,0,0,0,1,0.4031066012416863,0.9832274317741394,0.9832274317741394,0.9832274317741394,0.8216194212436676,0.042336605489254,0.8544608354568481,0.8089966773986816,0.9241379499435425,1.0,0.9944444444444445,0.009553343523293734,2.5,2.0,1.5,1.5,1.5,1.5,1.5,1.5,1.0,1.0,1.0,0.5801208305324531
l1,68,8,0.0625,38.715091705322266,34.0,4.715091705322266,3.070860076678483,0,0,0,14,0.3995475683832861,0.769199013710022,0.0013179779052734375,0.769199013710022,0.42868077382445335,0.42823438718914986,0.8551180958747864,0.7922188341617584,0.9295520782470703,1.0,0.9731481481481481,0.016177474055439234,1.5,4.0,1.0,3.0,1.0,1.5,1.0,1.0,0.5,0.5,0.5,0.3696514453267359
l1,68,8,0.25,39.74109649658203,34.0,5.741096496582031,3.388538282242328,0,4,4,20,0.3953377842720158,0.30631233751773834,-0.6883327662944794,0.30631233751773834,0.21746858954429626,0.6196428537368774,0.8155039548873901,0.6611020267009735,0.9350094795227051,0.9953703703703703,0.7296296296296296,0.026301255449652672,10.0,17.5,4.5,13.0,1.0,9.0,1.0,6.0,0.0,0.0,0.0,-0.08902544675427748
l1,68,8,0.5,42.58241271972656,34.0,8.582412719726562,4.143044719334816,1,1,2,24,0.3920456842294758,0.30000749230384827,-0.5711386650800705,0.29377835988998413,0.25717660784721375,0.5407898426055908,0.8101713061332703,0.6633006036281586,0.9139114320278168,0.9962962962962963,0.6953703703703704,0.03174591064453125,22.0,20.5,10.0,18.0,4.5,12.5,2.5,8.5,0.0,0.0,0.0,-0.09203819192562751
l1,68,8,0.0,81.80652618408203,34.0,47.80652618408203,9.778192260084113,0,2,2,2,0.3983806948492624,0.7092925310134888,-0.7129479646682739,0.7092925310134888,0.4467322826385498,0.45196008682250977,0.8965959548950195,0.8559389412403107,0.9452502727508545,1.0,1.0,0.011260876664891839,5.0,2.5,4.0,2.0,4.0,2.0,4.0,2.0,0.0,0.0,0.0,0.31091183616422635
l1,68,9,0.025,37.488059997558594,34.0,3.4880599975585938,2.641234044580493,0,0,0,3,0.4085276100180931,0.6925202906131744,-0.018469244241714478,0.690766841173172,0.45144760608673096,0.4485452175140381,0.8998457193374634,0.878423810005188,0.9197649955749512,1.0,1.0,0.0042548427591100335,5.0,2.5,4.0,2.0,4.0,2.0,4.0,2.0,0.0,0.0,0.0,0.2839926805950813
l1,68,9,0.0625,37.61189270019531,34.0,3.6118927001953125,2.6877103541180993,0,1,1,13,0.40739425825753806,0.9499777555465698,0.9499777555465698,0.9499777555465698,0.7627760171890259,0.0917281024158001,0.8488645851612091,0.7679714560508728,0.9537368714809418,1.0,0.9388888888888889,0.010030761361122131,2.0,1.5,2.0,1.5,1.0,1.0,1.0,1.0,1.0,1.0,0.5,0.5425834972890318
l1,68,9,0.25,41.66539001464844,34.0,7.6653900146484375,3.9154543575839758,1,2,3,24,0.39810185287939337,0.5015289783477783,-0.5730801969766617,0.5015289783477783,0.3147116005420685,0.47578389942646027,0.7922519445419312,0.6839330494403839,0.8945344090461731,0.999074074074074,0.6990740740740741,0.02594891283661127,21.5,12.0,11.5,7.0,7.0,4.0,4.5,2.5,0.0,0.0,0.0,0.10342712546838495
l1,68,9,0.5,45.575435638427734,34.0,11.575435638427734,4.811535509597072,1,3,4,25,0.39795152259359046,0.24201998859643936,-0.5636206120252609,0.234738290309906,0.17195452004671097,0.6316360235214233,0.7850864231586456,0.6457195580005646,0.9053230285644531,0.9916666666666667,0.6129629629629629,0.03132755775004625,19.5,22.5,12.0,16.5,6.0,12.5,4.0,7.5,0.0,0.0,0.0,-0.1559315339971511
l1,68,9,0.0,79.4629135131836,34.0,45.462913513183594,9.535503273600527,0,2,2,2,0.3996194219139067,0.7114593684673309,-0.01135188341140747,0.7114593684673309,0.45166507363319397,0.44756685197353363,0.8986950516700745,0.8959793448448181,0.9017651081085205,1.0,1.0,0.013085678685456514,4.0,2.0,4.0,2.0,4.0,2.0,4.0,2.0,0.0,0.0,0.0,0.31183994655342423
l1,68,10,0.025,39.049217224121094,34.0,5.049217224121094,3.177802580951276,0,0,0,4,0.4097007053340874,0.98590287566185,0.7043457627296448,0.7043457627296448,0.8160001039505005,0.0695398561656475,0.8837032616138458,0.8645828664302826,0.9065575301647186,1.0,1.0,0.042367808520793915,3.0,2.0,3.0,2.0,2.0,2.0,2.0,2.0,1.0,1.0,1.0,0.5762021703277626
l1,68,10,0.0625,40.16233825683594,34.0,6.1623382568359375,3.510653093441974,0,0,0,6,0.4007377936773139,0.9711780548095703,0.9711780548095703,0.9711780548095703,0.7779197692871094,0.08349646627902985,0.8585060834884644,0.7969468235969543,0.9321351647377014,1.0,0.9777777777777779,0.010762460064142942,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5704402611322564
l1,68,10,0.25,42.27265167236328,34.0,8.272651672363281,4.06759237370949,1,1,2,18,0.40022321604521527,0.553530290722847,0.12108218669891357,0.5458817780017853,0.4553670883178711,0.34777171164751053,0.808868944644928,0.6710017323493958,0.9271064698696136,0.9953703703703705,0.6898148148148149,0.03580543026328087,16.5,11.5,7.5,9.0,4.0,5.5,2.5,3.5,0.0,0.0,0.0,0.15330707467763172
l1,68,10,0.5,44.556678771972656,34.0,10.556678771972656,4.594927973337039,2,3,5,28,0.3964491139381753,0.561368316411972,0.15158461034297943,0.561368316411972,0.45714013278484344,0.3461427390575409,0.8097902536392212,0.6893388330936432,0.9053691327571869,0.9962962962962962,0.7259259259259259,0.038110118359327316,23.5,13.0,11.5,8.0,6.5,3.5,4.5,3.0,0.0,0.0,0.0,0.16491920247379677
l1,68,10,0.0,81.55545043945312,34.0,47.555450439453125,9.752481744286234,0,1,1,3,0.39688481397440756,0.7068833112716675,-0.02013993263244629,0.7021777331829071,0.4544491022825241,0.4463910758495331,0.8981167078018188,0.893652468919754,0.9031369984149933,1.0,1.0,0.014017497655004263,5.0,2.5,5.0,2.5,5.0,2.5,5.0,2.5,0.0,0.0,0.0,0.3099984972972599
l1,68,11,0.025,39.53326416015625,34.0,5.53326416015625,3.3266394308991236,0,0,0,0,0.4084044027696656,0.6901960074901581,-0.018623769283294678,0.6898731887340546,0.44655340909957886,0.4536067843437195,0.8982153832912445,0.8681139051914215,0.9332095086574554,1.0,1.0,0.0038566759321838617,5.0,2.0,4.0,2.0,4.0,2.0,4.0,2.0,0.0,0.0,0.0,0.2817916047204925
l1,68,11,0.0625,39.94340515136719,34.0,5.9434051513671875,3.4477270510118263,0,1,1,17,0.39957505806986315,0.5898367539048195,0.016709506511688232,0.5898367539048195,0.4222611300647259,0.4395996406674385,0.8513281345367432,0.7638098299503326,0.9423782229423523,0.999074074074074,0.9287037037037037,0.01353508559986949,2.0,9.0,1.5,6.0,1.5,4.5,1.5,3.5,0.5,0.5,0.5,0.19026169583495633
l1,68,11,0.25,45.30328369140625,34.0,11.30328369140625,4.754636500538494,1,3,4,28,0.3962136800301499,0.5059420466423035,-0.5406691431999207,0.5059420466423035,0.31889134645462036,0.47779956459999084,0.7949098348617554,0.6816796958446503,0.9117583334445953,0.9972222222222222,0.711111111111111,0.030199088156223297,18.0,12.5,12.5,6.5,7.0,4.5,3.5,3.0,0.0,0.0,0.0,0.10972836661215357
l1,68,11,0.5,43.75486755371094,34.0,9.754867553710938,4.416982685272782,4,6,10,31,0.39699992906512327,0.509683147072792,-0.5617876499891281,0.509683147072792,0.34898240864276886,0.44957849383354187,0.7985034286975861,0.6752786338329315,0.9229793846607208,0.9981481481481482,0.700925925925926,0.03128079976886511,21.5,12.0,14.0,7.5,6.5,3.5,4.0,2.5,0.0,0.0,0.0,0.11268321800766878
l1,68,11,0.0,83.73120880126953,34.0,49.73120880126953,9.973084589030528,0,2,2,2,0.3900965194393451,0.7119583189487457,-0.010161340236663818,0.7119583189487457,0.44915127754211426,0.44895127415657043,0.8979413509368896,0.8945528864860535,0.9013563990592957,1.0,1.0,0.01279850397258997,4.0,2.0,4.0,2.0,4.0,2.0,4.0,2.0,0.0,0.0,0.0,0.32186179950940064
topk,68,0,0.025,40.899986267089844,34.0,6.899986267089844,3.714831534069906,6,3,9,11,0.39349269423903865,0.9959734678268433,0.9959734678268433,0.9959734678268433,0.9969777464866638,0.0062026557279750705,0.9972338080406189,0.9442019760608673,1.0543654561042786,0.999074074074074,0.999074074074074,0.00851431000046432,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.6024807735878046
topk,68,0,0.0625,39.66498565673828,34.0,5.664985656738281,3.366003548601891,6,1,7,9,0.39926524830189847,0.6889715194702148,0.206434428691864,0.5163976848125458,0.5938212722539902,0.4097536150366068,0.9859567284584045,0.8880387246608734,1.0882292985916138,0.999074074074074,0.9953703703703703,0.021056546829640865,2.0,1.5,1.5,1.5,1.0,1.5,1.0,1.5,0.5,0.5,0.0,0.2897062711683164
topk,68,0,0.25,43.804752349853516,34.0,9.804752349853516,4.428263683814731,3,1,4,18,0.3934074144419709,0.5384980589151382,0.035437941551208496,0.5384980589151382,0.4936441034078598,0.3930705040693283,0.871652215719223,0.698500007390976,1.0182294845581055,0.9787037037037037,0.8342592592592593,0.06521570682525635,7.5,5.5,3.0,2.5,2.5,2.0,1.5,1.5,0.0,0.0,0.0,0.14509064447316733
topk,68,0,0.5,47.39377212524414,34.0,13.39377212524414,5.175668833752444,9,2,11,27,0.39021935478907366,0.5113222748041153,0.1863946095108986,0.3659590892493725,0.3830021917819977,0.4729190468788147,0.8484063744544983,0.6296495795249939,1.0429631173610687,0.9592592592592593,0.7037037037037037,0.04056995548307896,6.0,2.5,5.0,1.5,3.0,1.5,2.0,1.0,0.0,0.0,0.0,0.12110292001504164
topk,68,0,0.0,87.64065551757812,34.0,53.640655517578125,10.357668722425206,0,0,0,6,0.40529614865485525,0.999848335981369,0.999848335981369,0.999848335981369,0.9979497194290161,2.0229942492733244e-05,0.9997459650039673,0.9991773664951324,1.0005093216896057,0.9981481481481481,0.9981481481481481,3.5337404369784053e-05,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5945521873265138
topk,68,1,0.025,38.83597183227539,34.0,4.835971832275391,3.1099748993571112,5,4,9,10,0.4006947305798688,0.9275187253952026,0.9275187253952026,0.9275187253952026,0.990871012210846,0.009011207614094019,0.995744526386261,0.9573164284229279,1.0345337986946106,1.0,0.999074074074074,0.015869000693783164,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5,0.5,0.5268239948153338
topk,68,1,0.0625,39.040855407714844,34.0,5.040855407714844,3.175171478105287,3,3,6,8,0.4004443876994977,0.8041142225265503,0.8041142225265503,0.8041142225265503,0.9597862064838409,0.05568823404610157,0.9849272966384888,0.8913827240467072,1.0785303711891174,0.9981481481481482,0.9962962962962962,0.013991059735417366,1.5,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5,0.5,0.0,0.4036698348270526
topk,68,1,0.25,41.77574157714844,34.0,7.7757415771484375,3.9435368421295736,2,4,6,16,0.397744104675893,0.4623051732778549,-0.6938362121582031,0.33776263892650604,0.2712666839361191,0.6071285456418991,0.8786241114139557,0.6879752576351166,1.029464066028595,0.9777777777777779,0.8388888888888889,0.06070500984787941,5.5,9.5,3.0,5.5,2.5,3.5,2.0,3.0,0.0,0.0,0.0,0.06456106860196192
topk,68,1,0.5,43.852108001708984,34.0,9.852108001708984,4.438942390685205,3,1,4,27,0.3924484565276565,0.4978320002555847,-0.5774510055780411,0.45207953453063965,0.339898481965065,0.46920786798000336,0.8046621978282928,0.6186794340610504,0.9706939458847046,0.9759259259259259,0.6731481481481482,0.06968461349606514,17.0,16.5,11.5,11.5,5.0,7.0,4.0,5.0,0.0,0.0,0.0,0.10538354372792824
topk,68,1,0.0,92.4655532836914,34.0,58.465553283691406,10.813468694765868,0,2,2,3,0.4053108997065535,0.8157573640346527,0.8157573640346527,0.8157573640346527,0.9971682727336884,0.0033582616597414017,1.0004689693450928,0.9882205724716187,1.012291431427002,1.0,1.0,0.0025464922364335507,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.0,0.0,0.4104464643280992
topk,68,2,0.025,37.174034118652344,34.0,3.1740341186523438,2.5195360294884566,5,2,7,8,0.39519998093323316,0.7281941920518875,0.0077165961265563965,0.7281941920518875,0.5999526381492615,0.40065890084952116,0.9925085306167603,0.9315032958984375,1.055740237236023,0.999074074074074,0.9953703703703703,0.011407586745917797,2.0,1.5,2.0,1.0,2.0,1.0,2.0,1.0,0.5,0.5,0.5,0.33299421111865435
topk,68,2,0.0625,39.67413330078125,34.0,5.67413330078125,3.3687184749436976,5,3,8,11,0.39927438375362606,0.643016129732132,0.643016129732132,0.643016129732132,0.734025239944458,0.28747493401169777,0.9996849298477173,0.8618781566619873,1.127418577671051,0.9944444444444445,0.975,0.024844340980052948,2.0,1.0,1.5,1.0,1.5,1.0,1.5,1.0,0.5,0.5,0.0,0.2437417459785059
topk,68,2,0.25,45.37824249267578,34.0,11.378242492675781,4.7703766916609425,6,0,6,19,0.39604225053244924,0.44087211787700653,-0.6615749895572662,0.2966354861855507,0.4367072284221649,0.5224941074848175,0.9140889644622803,0.7615987956523895,1.0400298833847046,0.9907407407407407,0.9055555555555556,0.055124834179878235,5.0,5.0,4.0,3.0,3.5,2.5,2.5,2.5,0.0,0.0,0.0,0.044829867344557295
topk,68,2,0.5,47.42295455932617,34.0,13.422954559326172,5.1813043037862325,8,1,9,27,0.3908089600091814,0.43097226321697235,-0.5091513842344284,0.08885975275188684,0.16935761272907257,0.7264373600482941,0.8953886032104492,0.7247072458267212,1.0334766209125519,0.9861111111111112,0.8518518518518519,0.04341087304055691,5.5,11.5,1.5,8.5,1.0,6.5,1.0,5.5,0.0,0.0,0.0,0.040163303207790935
topk,68,2,0.0,71.37467193603516,34.0,37.374671936035156,8.645770139561346,0,1,1,1,0.40103881366777205,0.9997667372226715,0.9997667372226715,0.9997667372226715,0.9159397780895233,0.08470623896755569,1.0002471804618835,0.9836059510707855,1.0177749395370483,1.0,1.0,0.0022199649647518527,1.5,1.0,1.5,1.0,1.5,1.0,1.0,1.0,1.0,1.0,1.0,0.5987279235548995
topk,68,3,0.025,37.65237045288086,34.0,3.6523704528808594,2.70272845534453,4,2,6,10,0.4012585122125305,0.6458912342786789,-0.0010787546634674072,0.5331654697656631,0.4949464842211455,0.5050920136272907,0.9947055578231812,0.9503197371959686,1.0460176467895508,0.999074074074074,0.9944444444444445,0.0064847159665077925,1.0,4.5,1.0,3.0,1.0,2.0,1.0,1.5,0.5,0.5,0.5,0.2446327220661484
topk,68,3,0.0625,40.427268981933594,34.0,6.427268981933594,3.5853243754750843,4,1,5,9,0.39829801673627824,0.7284453809261322,0.7284453809261322,0.7284453809261322,0.8539277911186218,0.1308007687330246,0.9799584746360779,0.9058488309383392,1.0573219060897827,0.999074074074074,0.9935185185185185,0.036672539077699184,3.0,2.5,2.5,2.0,2.5,2.0,2.5,2.0,0.0,0.0,0.0,0.33014736418985396
topk,68,3,0.25,42.68369674682617,34.0,8.683696746826172,4.167419218929052,3,1,4,15,0.39545936064587484,0.5296773910522461,0.03849637508392334,0.5296773910522461,0.5270061492919922,0.42256125807762146,0.8729623854160309,0.7136083543300629,1.0191693305969238,0.9879629629629629,0.8611111111111112,0.053898926824331284,7.5,6.0,5.5,5.5,4.0,3.0,3.0,2.0,0.0,0.0,0.0,0.13421803040637126
topk,68,3,0.5,44.798484802246094,34.0,10.798484802246094,4.647254650000747,2,2,4,22,0.39718713857856647,0.5040947496891022,-0.6058861315250397,0.5040947496891022,0.43718983232975006,0.489376425743103,0.8520699143409729,0.6699010729789734,1.0196744799613953,0.9833333333333334,0.7842592592592592,0.053454361855983734,11.0,7.0,7.5,5.0,4.0,3.5,2.5,2.0,0.0,0.0,0.0,0.1069076111105357
topk,68,3,0.0,103.03935241699219,34.0,69.03935241699219,11.750689283140726,0,0,0,0,0.4027710940966809,0.7907369136810303,1.2546777725219727e-05,0.5008743773214519,0.4998893071324346,0.5000161977786775,0.9999026656150818,0.9991441071033478,1.0005275011062622,1.0,1.0,0.00014414592806133442,1.0,10.5,1.0,7.5,1.0,4.0,1.0,3.0,0.5,0.5,0.5,0.3879658195843494
topk,68,4,0.025,37.543365478515625,34.0,3.543365478515625,2.662093559970447,6,1,7,8,0.3919958006426033,0.9902697503566742,0.9902697503566742,0.9902697503566742,0.989932119846344,0.014200228499248624,0.9977729916572571,0.9314891993999481,1.0554808378219604,1.0,0.9962962962962962,0.011846305569633842,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5982739497140709
topk,68,4,0.0625,38.63393020629883,34.0,4.633930206298828,3.0443160734128796,3,3,6,10,0.39351749576023265,0.550693616271019,0.5497943460941315,0.5497943460941315,0.9596609473228455,0.03575720265507698,0.9891148805618286,0.9232261180877686,1.053473174571991,0.9972222222222222,0.9953703703703705,0.022680288180708885,2.5,2.5,2.0,2.0,2.0,2.0,2.0,2.0,0.0,0.0,0.0,0.15717612051078633
topk,68,4,0.25,40.859527587890625,34.0,6.859527587890625,3.7039253362361992,2,4,6,19,0.3955696193142335,0.5271767824888229,0.5271767824888229,0.5271767824888229,0.6029900014400482,0.3068191111087799,0.8854097127914429,0.704324871301651,1.0444599390029907,0.9925925925925926,0.8435185185185186,0.06476152315735817,14.5,8.0,8.0,4.5,4.5,2.5,2.0,1.0,0.0,0.0,0.0,0.13160716317458943
topk,68,4,0.5,40.91838836669922,34.0,6.918388366699219,3.7197825588145643,4,4,8,22,0.39554093152639513,0.4991716593503952,0.4960504025220871,0.4960504025220871,0.49869780242443085,0.3521537035703659,0.8019363284111023,0.6146641671657562,0.9725263714790344,0.9759259259259259,0.6361111111111111,0.07420272752642632,17.0,9.0,12.0,5.5,8.5,4.0,6.0,3.0,0.0,0.0,0.0,0.10363072782400007
topk,68,4,0.0,82.36483764648438,34.0,48.364837646484375,9.835124718473137,0,1,1,3,0.400733944273883,0.8753076493740082,-0.010597914457321167,0.6831196546554565,0.6669762879610062,0.33249229937791824,1.0000585317611694,0.9866069257259369,1.0129806995391846,0.999074074074074,0.9981481481481482,0.008998416364192963,3.0,2.0,3.0,2.0,2.0,1.5,2.0,1.5,1.0,0.0,0.0,0.4745737051001252
topk,68,5,0.025,39.78993225097656,34.0,5.7899322509765625,3.4029189836110287,4,2,6,10,0.40003070730640644,0.9964452981948853,0.9964452981948853,0.9964452981948853,0.9987253248691559,0.005040890304371715,0.9960361123085022,0.9547725319862366,1.0444969534873962,1.0,0.9981481481481482,0.006745502818375826,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5964145908884788
topk,68,5,0.0625,38.83432388305664,34.0,4.834323883056641,3.109445064841033,5,3,8,13,0.3977636642836229,0.7271831035614014,0.7271831035614014,0.7271831035614014,0.8395666778087616,0.148559907451272,0.9773501753807068,0.8833694159984589,1.0540282130241394,0.9981481481481481,0.9833333333333334,0.03195389546453953,2.0,1.5,1.5,1.0,1.5,1.0,1.0,1.0,0.5,0.5,0.0,0.32941943927777845
topk,68,5,0.25,39.79653549194336,34.0,5.796535491943359,3.404859450420075,5,4,9,19,0.39276714864953405,0.37987105548381805,-0.648756667971611,0.18265262246131897,0.2219422161579132,0.6686273217201233,0.8442059755325317,0.6817514598369598,0.998831182718277,0.9814814814814814,0.7333333333333334,0.049010058864951134,12.0,10.5,9.5,8.0,5.5,4.5,3.0,3.5,0.0,0.0,0.0,-0.012896093165715994
topk,68,5,0.5,42.09912872314453,34.0,8.099128723144531,4.024706220458535,4,4,8,26,0.3934375466524699,0.4840957820415497,-0.06928804516792297,0.42993776500225067,0.36984770745038986,0.5481370389461517,0.874579668045044,0.7203097641468048,1.0060997307300568,0.9916666666666667,0.8574074074074074,0.045595789328217506,8.5,7.0,3.0,4.5,1.0,2.5,1.0,2.5,0.0,0.0,0.0,0.0906582353890798
topk,68,5,0.0,69.94453430175781,34.0,35.94453430175781,8.478741353441672,0,1,1,5,0.40219309620877924,0.9957868456840515,0.9957868456840515,0.9957868456840515,0.9993738532066345,0.00013892278184357565,0.9992110729217529,0.9972198009490967,1.0020787715911865,1.0,1.0,0.00018222413200419396,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5935937494752723
topk,68,6,0.025,38.80059051513672,34.0,4.800590515136719,3.0985768936696325,4,3,7,10,0.40105422438482297,0.9076809883117676,0.9076809883117676,0.9076809883117676,0.9993425011634827,0.00795750436373055,1.000822901725769,0.9485789835453033,1.0524162650108337,0.999074074074074,0.9981481481481481,0.010395706165581942,1.5,1.5,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5,0.5,0.5066267639269446
topk,68,6,0.0625,39.110870361328125,34.0,5.110870361328125,3.1971455285773835,2,3,5,6,0.3989258961417739,0.6245743930339813,0.014766842126846313,0.5565245524048805,0.512073814868927,0.47632195707410574,0.981396496295929,0.8887878060340881,1.0767911672592163,0.999074074074074,0.9907407407407407,0.022729193791747093,1.0,8.5,1.0,6.5,1.0,4.5,1.0,3.5,0.5,0.5,0.5,0.22564849689220745
topk,68,6,0.25,41.82437515258789,34.0,7.824375152587891,3.955850159719143,2,0,2,19,0.39504288622771044,0.5349727869033813,0.4260500892996788,0.4260500892996788,0.6704416573047638,0.29651838541030884,0.8957271873950958,0.7909546494483948,0.999881237745285,0.9925925925925926,0.8861111111111111,0.055514682084321976,6.0,3.5,4.0,2.0,3.5,2.0,3.0,2.0,0.0,0.0,0.0,0.1399299006756709
topk,68,6,0.5,47.55297088623047,34.0,13.552970886230469,5.206336918343462,4,3,7,35,0.393416940838559,0.6291875839233398,0.6291875839233398,0.6291875839233398,0.5453966856002808,0.35079191625118256,0.8595993220806122,0.6838535666465759,1.0211291313171387,0.987037037037037,0.8055555555555556,0.06445186771452427,11.0,5.5,6.5,3.0,1.5,1.0,1.5,1.0,0.0,0.0,0.0,0.23577064308478085
topk,68,6,0.0,71.10977935791016,34.0,37.109779357910156,8.615076924211188,0,0,0,2,0.3967474610137615,0.8748316764831543,0.1458856761455536,0.846311628818512,0.7600478529930115,0.23814924592443276,0.9992114901542664,0.9629499912261963,1.0343236923217773,1.0,0.9962962962962962,0.0029376917373156175,2.5,1.5,2.5,1.5,2.5,1.5,2.5,1.5,0.5,0.5,0.5,0.4780842154693928
topk,68,7,0.025,37.953067779541016,34.0,3.9530677795410156,2.811785186357843,3,4,7,7,0.4015774650631546,0.9948302805423737,0.9948302805423737,0.9948302805423737,0.9988673329353333,0.010970019036903977,1.0036420226097107,0.9342970550060272,1.0666322708129883,0.999074074074074,0.9972222222222222,0.010532330255955458,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.593252815479219
topk,68,7,0.0625,37.79255676269531,34.0,3.7925567626953125,2.754107925950082,2,4,6,11,0.40016560819039937,0.9425744116306305,0.9425744116306305,0.9425744116306305,0.9330232441425323,0.05808444693684578,0.9819057583808899,0.8835994303226471,1.0884739756584167,0.9962962962962963,0.9916666666666667,0.019424528814852238,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5,0.5424088034402311
topk,68,7,0.25,43.55860137939453,34.0,9.558601379394531,4.372323521988043,2,2,4,24,0.3978242085301792,0.38881705701351166,0.34260525554418564,0.34260525554418564,0.5627513229846954,0.34154798090457916,0.8908933699131012,0.7271780967712402,1.0361369848251343,0.9953703703703703,0.8574074074074074,0.04643264226615429,8.0,5.0,6.0,3.5,3.0,2.0,2.0,1.0,0.0,0.0,0.0,-0.009007151516667533
topk,68,7,0.5,45.49032211303711,34.0,11.49032211303711,4.793812629093137,5,2,7,36,0.4002144661613849,0.43586941063404083,0.28936679661273956,0.28936679661273956,0.5346814393997192,0.3287430703639984,0.8589012622833252,0.6913539469242096,1.0174084305763245,0.9777777777777779,0.7740740740740741,0.05594911891967058,11.5,6.5,5.5,3.0,3.0,2.0,2.0,1.5,0.0,0.0,0.0,0.035654944472655936
topk,68,7,0.0,102.32333374023438,34.0,68.32333374023438,11.689596913582566,0,0,0,4,0.3988378415402258,0.9996711909770966,0.9996711909770966,0.9996711909770966,1.0000653564929962,8.212973807530943e-05,1.000061959028244,0.999110609292984,1.0012882947921753,1.0,1.0,7.82874758442631e-05,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.6008333494368707
topk,68,8,0.025,37.536277770996094,34.0,3.5362777709960938,2.659427723948638,4,2,6,8,0.4033698087021834,0.6045640483498573,-0.0015788376331329346,0.5375522039830685,0.49846545397304,0.5044772080145776,0.9971749186515808,0.9415681958198547,1.0577996969223022,0.9981481481481481,0.9981481481481481,0.010426382767036557,1.0,4.0,1.0,3.0,1.0,2.5,1.0,2.0,0.5,0.5,0.5,0.2011942396476739
topk,68,8,0.0625,41.250457763671875,34.0,7.250457763671875,3.808006925156849,2,2,4,11,0.38718143584666476,0.7439915537834167,0.7439915537834167,0.7439915537834167,0.9370805621147156,0.06910191848874092,0.9859773516654968,0.8900261223316193,1.075984001159668,1.0,0.9925925925925927,0.022409971803426743,2.5,2.0,1.5,1.5,1.0,1.0,1.0,1.0,0.5,0.0,0.0,0.356810117936752
topk,68,8,0.25,40.260948181152344,34.0,6.260948181152344,3.538629350013,3,2,5,20,0.39300863906250966,0.3551999628543854,0.07604856789112091,0.24604161828756332,0.4643985480070114,0.5160741955041885,0.8962588906288147,0.7161272168159485,1.0752346515655518,0.9944444444444445,0.8166666666666667,0.040236436761915684,6.0,3.0,3.5,1.5,3.5,1.5,2.0,1.0,0.0,0.0,0.0,-0.03780867620812428
topk,68,8,0.5,44.357662200927734,34.0,10.357662200927734,4.551409461218815,8,1,9,22,0.3909092512260217,0.3349505066871643,-0.1336827203631401,0.22629011422395706,0.5776337161660194,0.30431474559009075,0.8760945796966553,0.7630977630615234,0.9776609241962433,0.9851851851851852,0.787962962962963,0.047265369445085526,9.5,10.0,5.5,9.5,3.5,5.5,2.5,3.0,0.0,0.0,0.0,-0.05595874453885741
topk,68,8,0.0,83.67562866210938,34.0,49.675628662109375,9.967509339798315,0,0,0,3,0.40530324120808253,0.6098149120807648,-8.344650268554688e-06,0.6098149120807648,0.5002693351125345,0.5001200855040224,1.0002481937408447,0.9994668662548065,1.0010834336280823,1.0,1.0,0.0001431064956705086,1.0,2.5,1.0,1.0,1.0,1.0,1.0,1.0,0.5,0.5,0.5,0.20451167087268224
topk,68,9,0.025,37.78987503051758,34.0,3.789875030517578,2.7531352398445392,2,4,6,7,0.4054362444117882,0.9933830797672272,0.9933830797672272,0.9933830797672272,0.9876748025417328,0.012410450261086226,0.9998623430728912,0.9561900794506073,1.037475824356079,0.999074074074074,0.999074074074074,0.007581982761621475,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5879468353554389
topk,68,9,0.0625,38.90946960449219,34.0,4.9094696044921875,3.133519618947651,3,3,6,13,0.3970501143367872,0.9578382968902588,0.9578382968902588,0.9578382968902588,0.9528258144855499,0.05281994119286537,0.9777550995349884,0.8832447230815887,1.0737777948379517,0.999074074074074,0.9861111111111112,0.02387078758329153,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5607881825534715
topk,68,9,0.25,43.43988037109375,34.0,9.43988037109375,4.345085539339104,1,1,2,11,0.40030553836202826,0.2558250054717064,-0.7428013980388641,0.24636413156986237,0.11610076203942299,0.933539628982544,0.9244651198387146,0.7866884171962738,1.0519554615020752,0.9972222222222222,0.9351851851851851,0.04216805472970009,3.5,10.5,2.5,6.5,2.0,2.5,2.0,2.0,0.0,0.0,0.0,-0.14448053289032187
topk,68,9,0.5,43.91949462890625,34.0,9.91949462890625,4.45409852703733,3,3,6,27,0.3982507554827974,0.28522613644599915,-0.6838314831256866,0.28522613644599915,0.1717401072382927,0.705684632062912,0.8443415760993958,0.6505632698535919,1.0028932988643646,0.9722222222222222,0.7398148148148148,0.0567479282617569,8.0,11.5,4.5,9.0,2.5,3.5,1.0,3.0,0.0,0.0,0.0,-0.11302461903679828
topk,68,9,0.0,76.28048706054688,34.0,42.280487060546875,9.19570406927889,0,0,0,3,0.4043480330127153,0.9996576309204102,0.9996576309204102,0.9996576309204102,1.000096082687378,6.0243373809498735e-05,1.0000591278076172,0.9989410042762756,1.0012112259864807,1.0,1.0,6.971468792471569e-05,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5953095979076948
topk,68,10,0.025,38.882347106933594,34.0,4.882347106933594,3.1248508388443206,6,5,11,12,0.39472915974065537,0.621941328048706,0.621941328048706,0.621941328048706,0.8812356889247894,0.12856018915772438,0.9997242391109467,0.9647084474563599,1.039714753627777,1.0,0.999074074074074,0.02183391433209181,3.0,2.0,3.0,2.0,2.5,2.0,2.5,2.0,0.0,0.0,0.0,0.2272121683080507
topk,68,10,0.0625,40.424095153808594,34.0,6.424095153808594,3.5844377644617684,10,1,11,15,0.39100617028135665,0.9505402147769928,0.9505402147769928,0.9505402147769928,0.9709754884243011,0.039903389289975166,0.9745579063892365,0.8933745622634888,1.0664528608322144,0.999074074074074,0.9935185185185185,0.025615173391997814,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.5,0.5595340444956362
topk,68,10,0.25,44.49652862548828,34.0,10.496528625488281,4.581819080134554,4,5,9,18,0.39567181424805464,0.5585033595561981,0.06061631441116333,0.5585033595561981,0.5319884344935417,0.3862386792898178,0.8980063498020172,0.757232129573822,1.040467083454132,0.9898148148148148,0.8972222222222223,0.05826077610254288,5.0,8.0,2.5,7.0,1.0,5.5,1.0,3.0,0.5,0.0,0.0,0.16283154530814348
topk,68,10,0.5,46.320804595947266,34.0,12.320804595947266,4.964032049772439,2,1,3,24,0.39441771823561467,0.6326599419116974,0.6326599419116974,0.6326599419116974,0.4875652641057968,0.3428046181797981,0.8041866719722748,0.6474252343177795,0.9689637124538422,0.9703703703703703,0.6444444444444444,0.06190664879977703,14.0,7.0,9.5,4.5,5.0,2.0,4.0,1.0,0.0,0.0,0.0,0.23824222367608272
topk,68,10,0.0,83.41680908203125,34.0,49.41680908203125,9.941508824610507,0,1,1,5,0.3985928305508233,0.9835895597934723,0.9835895597934723,0.9835895597934723,0.9497180879116058,0.047719203557790024,1.0001304745674133,0.9689373970031738,1.0262108445167542,0.999074074074074,0.9972222222222222,0.007720082794548944,1.5,1.5,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,1.0,0.584996729242649
topk,68,11,0.025,38.43626403808594,34.0,4.4362640380859375,2.9786776938289155,4,3,7,8,0.3974757796317864,0.7576048374176025,0.7576048374176025,0.7576048374176025,0.931458443403244,0.07477052276954055,1.002114474773407,0.9506427049636841,1.0467739701271057,0.999074074074074,0.999074074074074,0.008529244689270854,2.0,1.5,2.0,1.5,1.0,1.0,1.0,1.0,0.5,0.5,0.5,0.36012905778581616
topk,68,11,0.0625,42.5142707824707,34.0,8.514270782470703,4.126564898014508,4,0,4,8,0.39820484376171306,0.5294684022665024,-0.06633183360099792,0.5294684022665024,0.6091092303395271,0.38871234469115734,0.9868622124195099,0.8931750953197479,1.0690756440162659,1.0,0.9824074074074074,0.032191683538258076,2.0,2.5,1.5,2.0,1.0,1.5,1.0,1.5,0.0,0.0,0.0,0.13126355850478932
topk,68,11,0.25,49.14896774291992,34.0,15.148967742919922,5.50435532937946,6,1,7,17,0.3935020706949804,0.5460329651832581,-0.03751420974731445,0.47722329944372177,0.47770654410123825,0.48325444012880325,0.9077719151973724,0.7540907263755798,1.026965856552124,0.9879629629629629,0.9009259259259259,0.045489970594644547,5.0,8.0,2.0,6.0,1.0,2.0,1.0,1.5,0.0,0.0,0.0,0.15253089448827767
topk,68,11,0.5,45.63069152832031,34.0,11.630691528320312,4.823005503432687,6,2,8,28,0.3887656792089674,0.5935832411050797,0.5935832411050797,0.5935832411050797,1.0127181708812714,0.1354214996099472,0.9134002327919006,0.7692634165287018,1.0307061970233917,0.9824074074074074,0.9287037037037037,0.04739961586892605,2.0,1.5,1.0,1.0,1.0,1.0,1.0,1.0,0.0,0.0,0.0,0.20481756189611228
topk,68,11,0.0,86.60232543945312,34.0,52.602325439453125,10.256931425248327,0,1,1,4,0.3959755006110463,0.8045647442340851,0.11139950156211853,0.8045647442340851,0.5835999101400375,0.41447236758540384,0.9996410012245178,0.9838002622127533,1.0106489658355713,1.0,0.9981481481481482,0.0053490354475798085,2.0,1.0,2.0,1.0,2.0,1.0,1.5,1.0,0.5,0.5,0.5,0.4085892436230388
````

# Appendix L — checkpoint SHA-256 manifest (120 checkpoints)

````csv
filename,bytes,sha256
weights_l1_m68_seed000_beta0.025.npz,21554,50d93550cc71602addab5f14d854ef46a0930e5d55c98302d216946ea8d1908c
weights_l1_m68_seed000_beta0.0625.npz,21636,eede8f47e53f86beb3df905d63fca3e74c74f264af0a54475d1b04fe5d426dde
weights_l1_m68_seed000_beta0.25.npz,21690,2c47b0d5ea04cf9e7309c511754e7c500eedac8d62312aedddeb3b4cc5d73bb4
weights_l1_m68_seed000_beta0.5.npz,21736,c2acdaa7b119860618c1a4b41fed91105db553c1e9b0312a39363169436a7ffb
weights_l1_m68_seed000_beta0.npz,21350,bfb12b70071b7fbea95deaa1327d26d5eef971db9ef043389654ac04caaa9efe
weights_l1_m68_seed001_beta0.025.npz,21564,3d1cb991fefa9cedad2a72d9fd00d179310bfff99fc56696d5290ebd65aebb41
weights_l1_m68_seed001_beta0.0625.npz,21648,f15bd6cd6c2abedcc650e3d8f80ff905c0de64a6fe7dc9361538c3571da9d00d
weights_l1_m68_seed001_beta0.25.npz,21709,6dd04e7e3f2ce807c383f2584e69e8eb23a2fc02723bbb3c5c6f12a209d59df6
weights_l1_m68_seed001_beta0.5.npz,21748,c0511f8045fb95b821c1d47e459efc5e6e208c84fb7b7b4b0a920e113811c3e3
weights_l1_m68_seed001_beta0.npz,21290,71722fefa4eafa337d535d133c10dcf2c6895b650f8247e82e30d0afb63fbd26
weights_l1_m68_seed002_beta0.025.npz,21589,a00a747533194da7d4af76cc19faec245e04ee7d640a0b9382a0aa4a18874044
weights_l1_m68_seed002_beta0.0625.npz,21683,221a7d518a1d33c803a26983bf19c777855787b3424aeb13935e04578e334641
weights_l1_m68_seed002_beta0.25.npz,21712,8b7f869e2340c73a064504b3ee576ccd31a516c29de341b3d8d72d3d0512fce3
weights_l1_m68_seed002_beta0.5.npz,21814,02e507515a07d6fab693d26b2f8c39c1dd1089d4f800d850a3f09f199a3d2546
weights_l1_m68_seed002_beta0.npz,21374,d50bcce72472ff58d908685a4e2623d9b30533a77b268667dafd8fb9514fe702
weights_l1_m68_seed003_beta0.025.npz,21559,795685efe7947f544344c1f695a055732039aec1154c3049ad72d51f28475093
weights_l1_m68_seed003_beta0.0625.npz,21658,f2256cfee2788b0f14838f47c1bee74b405e7f2117bbebdabfc721704c7ec579
weights_l1_m68_seed003_beta0.25.npz,21730,ed4c587bd03e06580a5882159135d6fa34a83687a39e93328bce6404491eab5c
weights_l1_m68_seed003_beta0.5.npz,21758,fbd0b160770597311fa0011e0d7898aedbdf1235e8198d7b4d9c710b87510afd
weights_l1_m68_seed003_beta0.npz,21366,ac1f167f0b134753e453fe12d8f0e3971224357749a8d5f076d035401202821e
weights_l1_m68_seed004_beta0.025.npz,21574,3d00d8ce75c75a13fa0b6a4a49600859dd8e86ca3af1acdd5a74d0100790ace2
weights_l1_m68_seed004_beta0.0625.npz,21643,280ce001306794f7797c271807c04368c48fb8e4c7aff59f1b6ec48f0746b963
weights_l1_m68_seed004_beta0.25.npz,21732,7f3795c39f5f7a0406c7f06c8f88b39db4f2bed2f32ace380d152ec072b976b6
weights_l1_m68_seed004_beta0.5.npz,21798,9a9ad103e3c5b7c3f07f8fdf5d15306a5108e017e2fdc2a53c78f7642101f8f3
weights_l1_m68_seed004_beta0.npz,21364,015f138df133c2097587d54e6ece4c2c11518d1d6a1a20b10812e12036d3550d
weights_l1_m68_seed005_beta0.025.npz,21541,23c5564493b3ee98c16c606970d815d4bbebeb6b54c410e12b87c3de63ba1075
weights_l1_m68_seed005_beta0.0625.npz,21658,28d6497854cf5cb6309f89a9291ea8021f7cf9800de5e9d0b42206e6401a5ce9
weights_l1_m68_seed005_beta0.25.npz,21738,2e4816627aacc38fe84a01efba281bc5b1be6dca68821b095dac5f53c6699e28
weights_l1_m68_seed005_beta0.5.npz,21790,28141dfea9560ec0b2f0a40aaade03cd85bf658fe636f9056731bce207c40d8b
weights_l1_m68_seed005_beta0.npz,21342,97495df87226ba471ff9d575a5056f561017e62c13a2e5a744bb1d2cae282cb3
weights_l1_m68_seed006_beta0.025.npz,21568,053034cae98bb20dfdce784fb27bfe198985e3caf44f751285f53ab943f37dd6
weights_l1_m68_seed006_beta0.0625.npz,21647,7e896b6f88e1e66648b5d20d9ea6d3f166fa6dd2dcae3e2105e55ab016cadefd
weights_l1_m68_seed006_beta0.25.npz,21765,42bff7f1e71be145dacf0abd2156b79645cc308a991d98ded926093c1d11c36a
weights_l1_m68_seed006_beta0.5.npz,21804,4769663f83fcdc1114799ee13484b776d49a249feb86f4b16e4da1fdda1ffe86
weights_l1_m68_seed006_beta0.npz,21340,c86fc2926ad0c91f6164f5137abc44416bb22a3b65475dac0a527e1916aaf256
weights_l1_m68_seed007_beta0.025.npz,21588,8a1d0c8b573b10afb9d069c96313dc1d483899ed3eeaaaad78d256d74f504042
weights_l1_m68_seed007_beta0.0625.npz,21658,4f709b7ab23b1dac337d2d9cbc8222047303fc62b7b4d4f77a620fe1c6bed3a4
weights_l1_m68_seed007_beta0.25.npz,21688,cd83a67e7d7f704bd5f8fad79b51c72a7af554a5dfce185d9b60b3d051dea151
weights_l1_m68_seed007_beta0.5.npz,21747,e4fd35687d75e28a8565ab396ecac9ee5c5d763d70ffdba50c49aa9254b96913
weights_l1_m68_seed007_beta0.npz,21320,33ff3140c215d0a857a0815d69ab569a960b9bf96aa20829a30628a62dc9597b
weights_l1_m68_seed008_beta0.025.npz,21563,5ff967ce667aaf552a2d2b564402f9ec0ae2e4e3e0365207dc4d33bddf5ca629
weights_l1_m68_seed008_beta0.0625.npz,21652,b3bac1c754086c6175f552b933af8c87d192028e0bdaa7705b7361953d37f205
weights_l1_m68_seed008_beta0.25.npz,21733,11b0550d29ac6e068ced2ecc7b584e7888d814ed21b0cdc6ae257b8869f30eb8
weights_l1_m68_seed008_beta0.5.npz,21790,264c11570cc071594aa6c48e8041ba6e6585a7d177902bcb820e0f9bdfbe33de
weights_l1_m68_seed008_beta0.npz,21309,1bffaaba72a174dca77bdd740afadb3c8a3293ee615fcb5115e4ec8f9a1933c2
weights_l1_m68_seed009_beta0.025.npz,21537,6be570ca80ea768a421c32b5a966bbf45c425a12cee34fd68c7fc69aadacc093
weights_l1_m68_seed009_beta0.0625.npz,21666,11edb51b09d2516c5dd88cd548bfa1f59e85972724c7ae6ecd300b56b76c56b0
weights_l1_m68_seed009_beta0.25.npz,21718,bf05fb10493ee921ea70ad1bcb476bb83591b0cedbe9f6df3657ed503dbf3e3b
weights_l1_m68_seed009_beta0.5.npz,21741,236a06ffeed2fac68c149dffc618c6442645a936436a0aaf96d359f8e26c9717
weights_l1_m68_seed009_beta0.npz,21340,0ea400d0caabeae2b806dbf59114c56e1c870517c328b9e443f196c7244a981b
weights_l1_m68_seed010_beta0.025.npz,21522,3dc4a60c43f32a7377eccbfe28438cf73d2301728b9c625663f9cbea8a17595e
weights_l1_m68_seed010_beta0.0625.npz,21618,68b496b0df25f0fff955ef0e122d8c1c3b758146988a02b46fc45f9ebe562877
weights_l1_m68_seed010_beta0.25.npz,21693,fc5dd429e53592e6d3aba49accf7aa492d6ab86e28dc47773fd8ec92ccd3755f
weights_l1_m68_seed010_beta0.5.npz,21782,2215c522238985804c5274ba1605384bacf13879ce1c8e488adc5a26a3dff73f
weights_l1_m68_seed010_beta0.npz,21360,2f5a2ae13141546b70e03a11ad7889f1e286a19c59c86dd01ea66b2913571cf8
weights_l1_m68_seed011_beta0.025.npz,21545,e9a8f526c0b0f6707c249239bff0d96a939c299e6dda29b998a63599fd9dfa83
weights_l1_m68_seed011_beta0.0625.npz,21629,f2115546db3e85b2c9a29e40bfdc62b8669fd12257554a5de500e2a1cf15cac6
weights_l1_m68_seed011_beta0.25.npz,21716,7298a528a5dfae3b0538f61aae2096280473014494304d3fc830f3ba6ce76849
weights_l1_m68_seed011_beta0.5.npz,21794,bc170daaea9a95066bff9acc984b056852535fb87dee8dd0f0142fdd90566c9f
weights_l1_m68_seed011_beta0.npz,21343,81d2b21930d689c57574e854b2ff05c7991cc68b8e99026e5c076cc56021a41d
weights_topk_m68_seed000_beta0.025.npz,21264,ba22ac0caa35d8b3f1e056f7b31fdc145d987359b76ae6eff33eb88f27f39ccb
weights_topk_m68_seed000_beta0.0625.npz,21306,1fb2a97d0601ce9b7e43d669f5643e2df3877894e1572c117340c809c0b33678
weights_topk_m68_seed000_beta0.25.npz,21458,c82ac6bb8ba021e81427663c45ed2dd4b66cbcbabc14e25d2b6c82c555122b8d
weights_topk_m68_seed000_beta0.5.npz,21442,1a2423270e471712d4c3fad0af793440eecf782a71f2c3de6d34d0e72c622aae
weights_topk_m68_seed000_beta0.npz,21280,93cd36c4d9a102fa76f832fe009ce8c4380554c5c709413c70ce1866f8afda01
weights_topk_m68_seed001_beta0.025.npz,21285,0f967cf459f7134504891899b88c9e2f37321b81337f0a83e9dc05837ec0f0e5
weights_topk_m68_seed001_beta0.0625.npz,21357,99294b5c8c362c43f85ce2d1fb8c47862d3fa982d58ab86bf63b496732ffd4f8
weights_topk_m68_seed001_beta0.25.npz,21569,75505c09d5a70d97550f99628838bfd6d080a20d6be9f6c4c4ae4e5550bc040e
weights_topk_m68_seed001_beta0.5.npz,21606,d332fc00e93651bc34b9037b281b55d491872b0b0f145a4fdb560f5291f03a18
weights_topk_m68_seed001_beta0.npz,21256,23bf930d711ef390364e9aaae1df235afdc8124cf71209b1bad669994a5ca43f
weights_topk_m68_seed002_beta0.025.npz,21310,8558e0c14fe2f0b1e86788999384da1b22525a1a6a5f2da95da611c4796d8c0b
weights_topk_m68_seed002_beta0.0625.npz,21397,0a969eab09966e8c634941532ac31ee6903ba97c458bbcbd1b972c6afdb779fe
weights_topk_m68_seed002_beta0.25.npz,21519,ffaa501bbe1e37fa85bae2466750de9471fcce0c1c52ebaf12e06181bcca3900
weights_topk_m68_seed002_beta0.5.npz,21529,1a2a7ceccd60f075692dc6eda49ac95d8c3981119dea9621315235216c88e8eb
weights_topk_m68_seed002_beta0.npz,21277,dc053c1c46978c5b27d44ee61f3a635c95433180d03c1547c8060ef16b17e753
weights_topk_m68_seed003_beta0.025.npz,21278,6a1edf8c1176a844a38b97d179b9700f0a69cdd15320560d9059e5bc72688f6d
weights_topk_m68_seed003_beta0.0625.npz,21484,32f0918085abdb6c35f5a36587e46c34287ef3f70525e71caa04d95d6c6da25f
weights_topk_m68_seed003_beta0.25.npz,21518,e6ea5c39e1668939ed5457904ea603044644ef238660e62dc761b5ddd8f434a1
weights_topk_m68_seed003_beta0.5.npz,21568,c7b8a355b9ab008a289be2667400968af43eb8b215b3fd083f6f69cad3bb4cb0
weights_topk_m68_seed003_beta0.npz,21209,c2b111816aeaae778e5fb64d8fbff7c05744f122007fdc3d1a6ea8b295470509
weights_topk_m68_seed004_beta0.025.npz,21315,ce38cf4d3285683518f02267daebe6bdfa688e9def33f0814241f31ef2413067
weights_topk_m68_seed004_beta0.0625.npz,21410,de6b2d5e40a074edb7b433816da5056286093cc74013b168e9b738b005ecd7f8
weights_topk_m68_seed004_beta0.25.npz,21499,b1a01a647261ecea4c88c78872ef567fe44e6bc81dc55be476e318941d554f52
weights_topk_m68_seed004_beta0.5.npz,21526,0a288201df6f42f740552e42b790dbff49741e0289c2a37ee66713b4d03472d1
weights_topk_m68_seed004_beta0.npz,21296,83ef523f3c60b9ef8bbb7d02d7d1443ec58dd9b034fd5b779daab39bafcec27e
weights_topk_m68_seed005_beta0.025.npz,21270,6cbec9fcc0acdbaca24a28f136c5815da61788cb81ef500cbb3d849326ebb962
weights_topk_m68_seed005_beta0.0625.npz,21431,9d222f1f565715f16006b2e7f56770262eb839563ac043079c1795ded7793c7c
weights_topk_m68_seed005_beta0.25.npz,21496,5e94b8b3de46304f54699e6d11dd772439a3c2f480b3d5e75c51c213ff477477
weights_topk_m68_seed005_beta0.5.npz,21620,a0375f8e275af9cb551e5b124f300804e391b537ceb546d30b04234a50327190
weights_topk_m68_seed005_beta0.npz,21325,51089c456883686baa79d1933722035c9ce0be847d90045c45e5945f04dd900d
weights_topk_m68_seed006_beta0.025.npz,21345,708af01cb67fb96eca4c8414892fa27ab95928d3fcd4987e4e00ebae018fc6e9
weights_topk_m68_seed006_beta0.0625.npz,21457,ace13ce291523a25e7db28564301be6159dae683eb43efbc6bdb110eb999c175
weights_topk_m68_seed006_beta0.25.npz,21532,ae07fdb22a109f8c62d85b4a37d52b9fc18a3abd60c6d717a88f14a731766136
weights_topk_m68_seed006_beta0.5.npz,21657,34859da7e97876df773e53085d158cf2e9f8bd6ec3f952453869d2efa6135e59
weights_topk_m68_seed006_beta0.npz,21335,6a3a5c194f85a0e8ca8b8fd818305ff2a8417b05303bc9436312582f775bbfd7
weights_topk_m68_seed007_beta0.025.npz,21330,8f8c2fa9694fc874ffc3b03085f47e7f26b68c379079dfbe631ebb790c930070
weights_topk_m68_seed007_beta0.0625.npz,21382,81dedb1e6f2cb4abdee8b54620df784a79a05896a01350d460959ed8491785cb
weights_topk_m68_seed007_beta0.25.npz,21459,4b98a503e31cff623705ab8d3164c788c43fabdc5ce00aaca48949547a17b6b4
weights_topk_m68_seed007_beta0.5.npz,21553,a0ff78c92b9b4b4fa7ab2aa4f763c33c0116141a2387cdc211a241c3b55da521
weights_topk_m68_seed007_beta0.npz,21277,c7a8aae04670549333edd0316d31211b98b1c24630735e061fc947d5ac8ac4fe
weights_topk_m68_seed008_beta0.025.npz,21308,4cc9017ca557d8cdd09f644fdeda9a0db6e20b8b45e84e1a8f40231e3d4965d7
weights_topk_m68_seed008_beta0.0625.npz,21439,936bb3f69ed93564be15cffe154b4a3008327fb1998f457e10ca1f54e97a33e8
weights_topk_m68_seed008_beta0.25.npz,21499,2e715908dc31abc999643cffd0522a4c58cdd9a4445baf87d83aff3be4d346c4
weights_topk_m68_seed008_beta0.5.npz,21604,354ab7b42ffb51f0eb1d8bbf440f24a9373f1a0712dab0b33d847cbb898e70d1
weights_topk_m68_seed008_beta0.npz,21341,b328f8697f7454163e13b09f0ada518203655cf11a52c2d8c8e401a9c0250cb6
weights_topk_m68_seed009_beta0.025.npz,21303,ebed64230f33a2d26e9e92aa2724500fb909aa11ad0460f2aab2ec5495bba5a7
weights_topk_m68_seed009_beta0.0625.npz,21425,6856ef6518160afcaead9e7103c0cef4daeb865ee9776533b6c378955434ba8f
weights_topk_m68_seed009_beta0.25.npz,21442,826a4ea37ea911107578c86ecdaa86c09f6a0e0cdef24c8d32cdc6e7b5c4465f
weights_topk_m68_seed009_beta0.5.npz,21562,440cce5d26c0acce6736b97cb648e6d4af95c0e641da481047511227119cd721
weights_topk_m68_seed009_beta0.npz,21292,e536765455b82748328090cb38b65b1a1936262385f87f56010c8c2bf52c19a4
weights_topk_m68_seed010_beta0.025.npz,21259,3959ca5476e91d6c2ec8e51206a3b67558c3d7bb9ff2b12cd96ef6ffcdbc3f3a
weights_topk_m68_seed010_beta0.0625.npz,21420,716dedecfd1aff15bac3e48482878773aba7f311819a3a098eaacc8e6fa86345
weights_topk_m68_seed010_beta0.25.npz,21467,8ad24043713a24ca36dd2959455e18bd9f1d62d1ff0bd563a24927aed9266a3f
weights_topk_m68_seed010_beta0.5.npz,21642,899862b02aa9f69921f0d0b9fdfffd0493f23da3db61b68a6cd4158676b473ab
weights_topk_m68_seed010_beta0.npz,21339,0726811471080e28d0ab43db87d7e3496e25cc64680c243e9c579d62d63d9566
weights_topk_m68_seed011_beta0.025.npz,21314,70bffc0b7d7a52543a32f8f0cc79c9404fe27c35c24a5dc8ebc97f9f5ec223f5
weights_topk_m68_seed011_beta0.0625.npz,21422,0c66096044969ecd9ac430b8a6da697d6e291b4a8cd94f53ed4ed4bcc2ab8f95
weights_topk_m68_seed011_beta0.25.npz,21561,9156ee7076e49ab531c3ba391bacecc8bda8054fafec0eafc7ced692fc8f3632
weights_topk_m68_seed011_beta0.5.npz,21592,581247be56a4b4d0d9fc0bbf1f965571872f3e997c582839dd950ed2e5732c63
weights_topk_m68_seed011_beta0.npz,21387,aa1b1f39a83c42d15c4e1d66da6e27e4242a2599d804f4369c00eb32210a0f75
````

# Appendix M — frozen training and scoring source

````python
#!/usr/bin/env python3
"""Matched-seed semi-real test of coherence-induced causal-feature splitting.

This experiment deliberately sits between a toy superposition model and an
LLM-scale SAE:

* the background representation is the hidden layer of a classifier trained on
  the real sklearn handwritten-digits dataset;
* two independent binary interventions are added as exact one-dimensional
  causal factors;
* an orthogonal mixing hides the privileged coordinates;
* a genuinely overcomplete, amortized ReLU-L1 SAE is trained end to end; and
* all four intervention states are retained on held-out images, permitting
  activation-aware causal scoring rather than decoder-cosine scoring alone.

The decoder regularizer is the exact full squared-Gram penalty in the finite
certificate:

    C_sum(D) = sum_{i<j} <d_i, d_j>^2

with unit decoder columns.  It is not OrtSAE's chunked positive-neighbor
penalty, and the script does not claim to be a transformer-activation test.

The implementation uses only NumPy, SciPy, and scikit-learn so that the full
matched-seed study is runnable on CPU in the repository's base environment.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import scipy
import sklearn
from scipy.optimize import nnls
from sklearn.datasets import load_digits
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier


@dataclass(frozen=True)
class Config:
    data_seed: int = 20260725
    classifier_seed: int = 271828
    mixing_seed: int = 314159
    hidden_dim: int = 32
    expansion: int = 2
    factor_amplitude: float = 1.5
    l1_lambda: float = 0.2
    topk_k: int = 16
    steps: int = 10000
    batch_size: int = 256
    learning_rate: float = 0.002
    grad_clip: float = 10.0
    eval_threshold: float = 1e-6
    alignment_threshold: float = 0.90
    split_relative_threshold: float = 0.10


@dataclass
class DatasetBundle:
    train_x: np.ndarray
    eval_x: np.ndarray
    eval_states: np.ndarray
    causal_directions: np.ndarray
    effective_factor_amplitude: float
    classifier_train_accuracy: float
    classifier_eval_accuracy: float
    hidden_dim: int
    ambient_dim: int
    train_base_n: int
    eval_base_n: int
    data_sha256: str


def _array_digest(arrays: Iterable[np.ndarray]) -> str:
    digest = hashlib.sha256()
    for array in arrays:
        contiguous = np.ascontiguousarray(array)
        digest.update(str(contiguous.shape).encode("ascii"))
        digest.update(str(contiguous.dtype).encode("ascii"))
        digest.update(contiguous.tobytes())
    return digest.hexdigest()


def _hidden_activations(model: MLPClassifier, x: np.ndarray) -> np.ndarray:
    hidden = x @ model.coefs_[0] + model.intercepts_[0]
    return np.maximum(hidden, 0.0)


def _factorial_expand(
    hidden: np.ndarray,
    q_mix: np.ndarray,
    factor_amplitude: float,
) -> tuple[np.ndarray, np.ndarray]:
    # Row order per base image is fixed: 00, 10, 01, 11.  The evaluator uses
    # this order to form exact paired intervention contrasts.
    states = np.asarray(
        [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0]],
        dtype=np.float32,
    )
    repeated_hidden = np.repeat(hidden.astype(np.float32), 4, axis=0)
    tiled_states = np.tile(states, (hidden.shape[0], 1))
    augmented = np.concatenate(
        [repeated_hidden, factor_amplitude * tiled_states],
        axis=1,
    )
    return (augmented @ q_mix).astype(np.float32), tiled_states


def build_dataset(cfg: Config) -> DatasetBundle:
    digits_x, digits_y = load_digits(return_X_y=True)
    indices = np.arange(digits_x.shape[0])
    train_idx, eval_idx = train_test_split(
        indices,
        test_size=0.30,
        random_state=cfg.data_seed,
        stratify=digits_y,
    )

    pixel_mean = digits_x[train_idx].mean(axis=0)
    pixel_std = digits_x[train_idx].std(axis=0)
    pixel_std[pixel_std < 1e-8] = 1.0
    x_train_std = (digits_x[train_idx] - pixel_mean) / pixel_std
    x_eval_std = (digits_x[eval_idx] - pixel_mean) / pixel_std

    classifier = MLPClassifier(
        hidden_layer_sizes=(cfg.hidden_dim,),
        activation="relu",
        solver="lbfgs",
        alpha=1e-4,
        max_iter=600,
        random_state=cfg.classifier_seed,
    )
    classifier.fit(x_train_std, digits_y[train_idx])
    train_accuracy = accuracy_score(
        digits_y[train_idx], classifier.predict(x_train_std)
    )
    eval_accuracy = accuracy_score(
        digits_y[eval_idx], classifier.predict(x_eval_std)
    )

    h_train = _hidden_activations(classifier, x_train_std)
    h_eval = _hidden_activations(classifier, x_eval_std)
    hidden_scale = math.sqrt(cfg.hidden_dim) / np.mean(
        np.linalg.norm(h_train, axis=1)
    )
    h_train = (h_train * hidden_scale).astype(np.float32)
    h_eval = (h_eval * hidden_scale).astype(np.float32)

    ambient_dim = cfg.hidden_dim + 2
    mixing_rng = np.random.default_rng(cfg.mixing_seed)
    raw_mix = mixing_rng.standard_normal((ambient_dim, ambient_dim))
    q_mix, r_mix = np.linalg.qr(raw_mix)
    # Fix the QR sign convention, which can otherwise vary across LAPACK builds.
    signs = np.sign(np.diag(r_mix))
    signs[signs == 0] = 1.0
    q_mix = (q_mix * signs).astype(np.float32)

    train_x, _ = _factorial_expand(
        h_train, q_mix, cfg.factor_amplitude
    )
    eval_x, eval_states = _factorial_expand(
        h_eval, q_mix, cfg.factor_amplitude
    )

    # One scalar normalization matches the convention used in the real Pythia
    # trainer: mean input norm is sqrt(d).  It preserves all angles.
    total_scale = math.sqrt(ambient_dim) / np.mean(
        np.linalg.norm(train_x, axis=1)
    )
    train_x = (train_x * total_scale).astype(np.float32)
    eval_x = (eval_x * total_scale).astype(np.float32)
    causal_directions = q_mix[-2:, :].astype(np.float32)
    effective_factor_amplitude = cfg.factor_amplitude * total_scale

    data_hash = _array_digest(
        [train_x, eval_x, eval_states, causal_directions]
    )
    return DatasetBundle(
        train_x=train_x,
        eval_x=eval_x,
        eval_states=eval_states,
        causal_directions=causal_directions,
        effective_factor_amplitude=float(effective_factor_amplitude),
        classifier_train_accuracy=float(train_accuracy),
        classifier_eval_accuracy=float(eval_accuracy),
        hidden_dim=cfg.hidden_dim,
        ambient_dim=ambient_dim,
        train_base_n=len(train_idx),
        eval_base_n=len(eval_idx),
        data_sha256=data_hash,
    )


def _gram_penalty_and_grad(decoder: np.ndarray) -> tuple[float, np.ndarray]:
    gram = decoder.T @ decoder
    offdiag = gram - np.eye(gram.shape[0], dtype=gram.dtype)
    penalty = 0.5 * float(np.sum(offdiag * offdiag))
    gradient = 2.0 * (decoder @ offdiag)
    return penalty, gradient


class Adam:
    def __init__(
        self,
        parameters: dict[str, np.ndarray],
        learning_rate: float,
    ) -> None:
        self.learning_rate = learning_rate
        self.m = {name: np.zeros_like(value) for name, value in parameters.items()}
        self.v = {name: np.zeros_like(value) for name, value in parameters.items()}
        self.t = 0

    def step(
        self,
        parameters: dict[str, np.ndarray],
        gradients: dict[str, np.ndarray],
        learning_rate_scale: float,
    ) -> None:
        self.t += 1
        beta1 = 0.9
        beta2 = 0.999
        epsilon = 1e-8
        lr = self.learning_rate * learning_rate_scale
        for name, parameter in parameters.items():
            gradient = gradients[name]
            self.m[name] = beta1 * self.m[name] + (1.0 - beta1) * gradient
            self.v[name] = beta2 * self.v[name] + (1.0 - beta2) * (
                gradient * gradient
            )
            m_hat = self.m[name] / (1.0 - beta1**self.t)
            v_hat = self.v[name] / (1.0 - beta2**self.t)
            parameter -= lr * m_hat / (np.sqrt(v_hat) + epsilon)


def _apply_topk(
    dense_features: np.ndarray,
    k: int,
) -> tuple[np.ndarray, np.ndarray]:
    if k <= 0 or k > dense_features.shape[1]:
        raise ValueError(f"top-k must be in [1, {dense_features.shape[1]}]")
    top_indices = np.argpartition(
        dense_features, dense_features.shape[1] - k, axis=1
    )[:, -k:]
    mask = np.zeros_like(dense_features, dtype=bool)
    np.put_along_axis(mask, top_indices, True, axis=1)
    mask &= dense_features > 0.0
    return dense_features * mask, mask


def _encode(
    x: np.ndarray,
    encoder: np.ndarray,
    encoder_bias: np.ndarray,
    decoder_bias: np.ndarray,
    architecture: str,
    topk_k: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    preactivation = (x - decoder_bias) @ encoder + encoder_bias
    dense_features = np.maximum(preactivation, 0.0)
    if architecture == "l1":
        active_mask = preactivation > 0.0
        features = dense_features
    elif architecture == "topk":
        features, active_mask = _apply_topk(dense_features, topk_k)
    else:
        raise ValueError(f"unknown architecture: {architecture}")
    return preactivation, features, active_mask


def train_sae(
    train_x: np.ndarray,
    cfg: Config,
    seed: int,
    beta: float,
    architecture: str = "l1",
    latent_width: int | None = None,
    steps_override: int | None = None,
) -> tuple[dict[str, np.ndarray], dict[str, float]]:
    steps = cfg.steps if steps_override is None else steps_override
    d = train_x.shape[1]
    m = cfg.expansion * d if latent_width is None else latent_width
    if m <= d:
        raise ValueError(f"latent width must be overcomplete: got m={m}, d={d}")
    init_rng = np.random.default_rng(seed)
    batch_rng = np.random.default_rng(1_000_000 + seed)

    decoder = init_rng.standard_normal((d, m)).astype(np.float32)
    decoder /= np.linalg.norm(decoder, axis=0, keepdims=True).clip(1e-8)
    encoder = (
        decoder + 0.05 * init_rng.standard_normal((d, m)).astype(np.float32)
    )
    encoder_bias = np.full(m, -0.05, dtype=np.float32)
    decoder_bias = np.zeros(d, dtype=np.float32)

    parameters = {
        "encoder": encoder,
        "encoder_bias": encoder_bias,
        "decoder": decoder,
        "decoder_bias": decoder_bias,
    }
    optimizer = Adam(parameters, cfg.learning_rate)
    final_values: dict[str, float] = {}

    for step in range(steps):
        batch_indices = batch_rng.integers(
            0, train_x.shape[0], size=cfg.batch_size
        )
        batch = train_x[batch_indices]
        centered = batch - decoder_bias
        preactivation = centered @ encoder + encoder_bias
        dense_features = np.maximum(preactivation, 0.0)
        if architecture == "l1":
            features = dense_features
            active_mask = preactivation > 0.0
        elif architecture == "topk":
            features, active_mask = _apply_topk(
                dense_features, cfg.topk_k
            )
        else:
            raise ValueError(f"unknown architecture: {architecture}")
        reconstruction = features @ decoder.T + decoder_bias
        residual = reconstruction - batch

        batch_n = batch.shape[0]
        reconstruction_loss = float(
            np.sum(residual * residual) / batch_n
        )
        sparsity_loss = float(np.sum(features) / batch_n)
        gram_penalty, gram_gradient = _gram_penalty_and_grad(decoder)

        grad_reconstruction = (2.0 / batch_n) * residual
        grad_decoder = grad_reconstruction.T @ features + beta * gram_gradient
        grad_features = grad_reconstruction @ decoder
        if architecture == "l1":
            grad_features += cfg.l1_lambda / batch_n
        grad_preactivation = grad_features * active_mask
        grad_encoder = centered.T @ grad_preactivation
        grad_encoder_bias = np.sum(grad_preactivation, axis=0)
        grad_decoder_bias = np.sum(grad_reconstruction, axis=0)
        grad_decoder_bias -= np.sum(
            grad_preactivation @ encoder.T, axis=0
        )

        gradients = {
            "encoder": grad_encoder,
            "encoder_bias": grad_encoder_bias,
            "decoder": grad_decoder,
            "decoder_bias": grad_decoder_bias,
        }
        global_norm = math.sqrt(
            sum(float(np.sum(value * value)) for value in gradients.values())
        )
        if global_norm > cfg.grad_clip:
            factor = cfg.grad_clip / global_norm
            for value in gradients.values():
                value *= factor

        if step < steps // 2:
            learning_rate_scale = 1.0
        elif step < (4 * steps) // 5:
            learning_rate_scale = 1.0 / 3.0
        else:
            learning_rate_scale = 1.0 / 10.0
        optimizer.step(parameters, gradients, learning_rate_scale)
        decoder /= np.linalg.norm(decoder, axis=0, keepdims=True).clip(1e-8)

        if step == steps - 1:
            final_values = {
                "train_reconstruction_loss_last_batch": reconstruction_loss,
                "train_l1_last_batch": sparsity_loss,
                "train_gram_last_step": gram_penalty,
                "train_total_last_batch": (
                    reconstruction_loss
                    + (
                        cfg.l1_lambda * sparsity_loss
                        if architecture == "l1"
                        else 0.0
                    )
                    + beta * gram_penalty
                ),
                "train_gradient_norm_last_batch": global_norm,
            }

    return parameters, final_values


def _paired_factor_effects(
    values: np.ndarray,
    eval_base_n: int,
) -> tuple[np.ndarray, np.ndarray]:
    shaped = values.reshape(eval_base_n, 4, *values.shape[1:])
    # state order: 00, 10, 01, 11
    effect_1 = 0.5 * (
        (shaped[:, 1] - shaped[:, 0])
        + (shaped[:, 3] - shaped[:, 2])
    )
    effect_2 = 0.5 * (
        (shaped[:, 2] - shaped[:, 0])
        + (shaped[:, 3] - shaped[:, 1])
    )
    return effect_1, effect_2


def evaluate_sae(
    parameters: dict[str, np.ndarray],
    dataset: DatasetBundle,
    cfg: Config,
    seed: int,
    beta: float,
    architecture: str = "l1",
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    encoder = parameters["encoder"]
    encoder_bias = parameters["encoder_bias"]
    decoder = parameters["decoder"]
    decoder_bias = parameters["decoder_bias"]

    _, features, _ = _encode(
        dataset.eval_x,
        encoder,
        encoder_bias,
        decoder_bias,
        architecture,
        cfg.topk_k,
    )
    reconstruction = features @ decoder.T + decoder_bias
    residual = reconstruction - dataset.eval_x
    eval_centered = dataset.eval_x - dataset.eval_x.mean(axis=0)
    fvu = float(
        np.sum(residual * residual) / np.sum(eval_centered * eval_centered)
    )
    l0 = float(np.mean(np.sum(features > cfg.eval_threshold, axis=1)))
    dead_mask = np.max(features, axis=0) <= cfg.eval_threshold
    dead_fraction = float(np.mean(dead_mask))
    gram_penalty, _ = _gram_penalty_and_grad(decoder)
    gram = decoder.T @ decoder
    upper = np.abs(gram[np.triu_indices(gram.shape[0], k=1)])
    max_abs_coherence = float(np.max(upper))
    mean_sq_coherence = float(np.mean(upper * upper))

    feature_effects = _paired_factor_effects(
        features, dataset.eval_base_n
    )
    reconstruction_effects = _paired_factor_effects(
        reconstruction, dataset.eval_base_n
    )

    result: dict[str, Any] = {
        "seed": seed,
        "beta": beta,
        "architecture": architecture,
        "d": dataset.ambient_dim,
        "m": decoder.shape[1],
        "fvu": fvu,
        "l0": l0,
        "dead_fraction": dead_fraction,
        "gram_penalty": gram_penalty,
        "mean_squared_coherence": mean_sq_coherence,
        "max_absolute_coherence": max_abs_coherence,
    }

    factor_arrays: dict[str, np.ndarray] = {}
    for factor_index, (
        direction,
        feature_effect,
        reconstruction_effect,
    ) in enumerate(
        zip(
            dataset.causal_directions,
            feature_effects,
            reconstruction_effects,
        ),
        start=1,
    ):
        mean_feature_effect = feature_effect.mean(axis=0)
        mean_reconstruction_effect = reconstruction_effect.mean(axis=0)
        decoder_cosines = direction @ decoder
        positive_geometry = np.maximum(decoder_cosines, 0.0)
        absolute_geometry = np.abs(decoder_cosines)

        # The mean causal contribution of atom k is
        # E[delta f_k] d_k.  Its projection onto the true causal direction is
        # the activation-aware amount of the factor carried by that atom.
        aligned_contributions = mean_feature_effect * decoder_cosines
        positive_contributions = np.maximum(aligned_contributions, 0.0)
        contribution_sum = float(np.sum(positive_contributions))
        contribution_max = float(np.max(positive_contributions))
        concentration = (
            contribution_max / contribution_sum
            if contribution_sum > 1e-12
            else 0.0
        )
        participation_ratio = (
            contribution_sum * contribution_sum
            / float(np.sum(positive_contributions**2))
            if np.sum(positive_contributions**2) > 1e-12
            else 0.0
        )
        split_count = int(
            np.sum(
                positive_contributions
                >= cfg.split_relative_threshold
                * max(contribution_max, 1e-12)
            )
        )

        family_gain = float(
            direction @ mean_reconstruction_effect
            / dataset.effective_factor_amplitude
        )
        family_norm_ratio = float(
            np.linalg.norm(mean_reconstruction_effect)
            / dataset.effective_factor_amplitude
        )
        family_cosine = float(
            direction @ mean_reconstruction_effect
            / max(np.linalg.norm(mean_reconstruction_effect), 1e-12)
        )
        single_gain = (
            contribution_max / dataset.effective_factor_amplitude
        )

        nnls_code, nnls_residual = nnls(decoder, direction)
        nnls_reconstruction = decoder @ nnls_code
        nnls_cosine = float(
            direction @ nnls_reconstruction
            / max(np.linalg.norm(nnls_reconstruction), 1e-12)
        )

        prefix = f"factor{factor_index}_"
        result.update(
            {
                prefix + "max_positive_cosine": float(
                    np.max(positive_geometry)
                ),
                prefix + "max_absolute_cosine": float(
                    np.max(absolute_geometry)
                ),
                prefix + "faithful_geometry": bool(
                    np.max(positive_geometry) >= cfg.alignment_threshold
                ),
                prefix + "causal_concentration": float(concentration),
                prefix + "causal_participation_ratio": float(
                    participation_ratio
                ),
                prefix + "causal_split_count": split_count,
                prefix + "single_gain": float(single_gain),
                prefix + "family_gain": family_gain,
                prefix + "family_norm_ratio": family_norm_ratio,
                prefix + "family_cosine": family_cosine,
                prefix + "nnls_residual": float(nnls_residual),
                prefix + "nnls_cosine": nnls_cosine,
            }
        )
        factor_arrays[prefix + "decoder_cosines"] = decoder_cosines
        factor_arrays[prefix + "mean_feature_effect"] = mean_feature_effect
        factor_arrays[
            prefix + "positive_contributions"
        ] = positive_contributions

    # Factor averages are the preregistration's seed-level experimental units.
    average_fields = [
        "max_positive_cosine",
        "max_absolute_cosine",
        "causal_concentration",
        "causal_participation_ratio",
        "causal_split_count",
        "single_gain",
        "family_gain",
        "family_norm_ratio",
        "family_cosine",
        "nnls_residual",
        "nnls_cosine",
    ]
    for field in average_fields:
        result["mean_factor_" + field] = float(
            0.5 * (result["factor1_" + field] + result["factor2_" + field])
        )
    result["both_faithful_geometry"] = bool(
        result["factor1_faithful_geometry"]
        and result["factor2_faithful_geometry"]
    )
    return result, factor_arrays


def _parse_csv_numbers(text: str, cast: Any) -> list[Any]:
    return [cast(item.strip()) for item in text.split(",") if item.strip()]


def _write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    fieldnames: list[str] = []
    seen: set[str] = set()
    for record in records:
        for key in record:
            if key not in seen:
                fieldnames.append(key)
                seen.add(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def _environment_metadata() -> dict[str, Any]:
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "sklearn": sklearn.__version__,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--architectures",
        default="l1",
        help="comma-separated architectures from {l1,topk}",
    )
    parser.add_argument(
        "--seeds",
        default="0,1,2,3,4,5,6,7",
        help="comma-separated SAE initialization seeds",
    )
    parser.add_argument(
        "--betas",
        default="0,0.025,0.0625,0.25,0.5",
        help="comma-separated full squared-Gram coefficients",
    )
    parser.add_argument(
        "--widths",
        default="68",
        help="comma-separated overcomplete latent widths",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=None,
        help="override the registered 10000 training steps (for smoke/pilot only)",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        required=True,
        help="new or existing result directory",
    )
    parser.add_argument(
        "--save-weights",
        action="store_true",
        help="save small NumPy weight archives for every run",
    )
    args = parser.parse_args()

    cfg = Config()
    seeds = _parse_csv_numbers(args.seeds, int)
    betas = _parse_csv_numbers(args.betas, float)
    widths = _parse_csv_numbers(args.widths, int)
    architectures = [
        item.strip()
        for item in args.architectures.split(",")
        if item.strip()
    ]
    args.outdir.mkdir(parents=True, exist_ok=True)
    if not seeds or not betas or not architectures or not widths:
        raise ValueError(
            "at least one architecture, width, seed, and beta are required"
        )
    if any(item not in {"l1", "topk"} for item in architectures):
        raise ValueError("architectures must be l1 and/or topk")

    started = time.time()
    dataset = build_dataset(cfg)
    print(
        "dataset "
        f"train={dataset.train_x.shape} eval={dataset.eval_x.shape} "
        f"classifier_acc={dataset.classifier_eval_accuracy:.4f} "
        f"sha256={dataset.data_sha256[:16]}",
        flush=True,
    )

    records: list[dict[str, Any]] = []
    for architecture in architectures:
        for latent_width in widths:
            if latent_width <= dataset.ambient_dim:
                raise ValueError(
                    f"width {latent_width} is not overcomplete for "
                    f"d={dataset.ambient_dim}"
                )
            for seed in seeds:
                for beta in betas:
                    run_started = time.time()
                    parameters, train_stats = train_sae(
                        dataset.train_x,
                        cfg,
                        seed=seed,
                        beta=beta,
                        architecture=architecture,
                        latent_width=latent_width,
                        steps_override=args.steps,
                    )
                    result, factor_arrays = evaluate_sae(
                        parameters,
                        dataset,
                        cfg,
                        seed=seed,
                        beta=beta,
                        architecture=architecture,
                    )
                    result.update(train_stats)
                    result["wall_seconds"] = float(time.time() - run_started)
                    records.append(result)
                    print(
                        f"arch={architecture} m={latent_width} "
                        f"seed={seed:03d} beta={beta:.6g} "
                        f"FVU={result['fvu']:.4f} L0={result['l0']:.1f} "
                        f"dead={result['dead_fraction']:.1%} "
                        f"align={result['mean_factor_max_positive_cosine']:.3f} "
                        f"conc={result['mean_factor_causal_concentration']:.3f} "
                        f"family={result['mean_factor_family_gain']:.3f} "
                        f"split={result['mean_factor_causal_split_count']:.1f} "
                        f"({result['wall_seconds']:.1f}s)",
                        flush=True,
                    )
                    if args.save_weights:
                        weight_path = args.outdir / (
                            f"weights_{architecture}_m{latent_width}_"
                            f"seed{seed:03d}_beta{beta:.6g}.npz"
                        )
                        np.savez_compressed(
                            weight_path,
                            **parameters,
                            **factor_arrays,
                        )

    csv_path = args.outdir / "run_metrics.csv"
    _write_csv(csv_path, records)
    metadata = {
        "config": asdict(cfg),
        "architectures": architectures,
        "widths": widths,
        "seeds": seeds,
        "betas": betas,
        "steps_override": args.steps,
        "dataset": {
            "data_sha256": dataset.data_sha256,
            "classifier_train_accuracy": dataset.classifier_train_accuracy,
            "classifier_eval_accuracy": dataset.classifier_eval_accuracy,
            "train_base_n": dataset.train_base_n,
            "eval_base_n": dataset.eval_base_n,
            "train_shape": list(dataset.train_x.shape),
            "eval_shape": list(dataset.eval_x.shape),
            "ambient_dim": dataset.ambient_dim,
            "effective_factor_amplitude": (
                dataset.effective_factor_amplitude
            ),
        },
        "environment": _environment_metadata(),
        "wall_seconds": float(time.time() - started),
    }
    metadata_path = args.outdir / "metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"saved {csv_path} and {metadata_path}", flush=True)


if __name__ == "__main__":
    main()
````

# Appendix N — frozen registered-analysis source

````python
#!/usr/bin/env python3
"""Frozen-style analysis for the semi-real coherence-transfer experiment.

The seed, architecture, beta, width, dataset-hash, manipulation, and retention
gates are explicit here so that an unexpected file or a signal-destroying
solution cannot be silently interpreted as support.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


EXPECTED_ARCHITECTURES = ("l1", "topk")
EXPECTED_WIDTHS = (68,)
EXPECTED_BETAS = (0.0, 0.025, 0.0625, 0.25, 0.5)
EXPECTED_SEEDS = tuple(range(12))
EXPECTED_DATA_SHA256 = (
    "d00e7d6c272ae538920cc91b7ab92e8ba91f522eb1c62b05677fbdc56799bad9"
)
CONTROL_BETA = 0.0
HIGH_BETA = 0.5
BOOTSTRAP_REPS = 20_000
BOOTSTRAP_SEED = 8675309


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def paired_contrast(
    frame: pd.DataFrame,
    architecture: str,
    field: str,
    high_beta: float = HIGH_BETA,
    control_beta: float = CONTROL_BETA,
) -> dict[str, Any]:
    subset = frame[
        (frame["architecture"] == architecture)
        & (frame["beta"].isin([control_beta, high_beta]))
    ]
    pivot = subset.pivot(index="seed", columns="beta", values=field)
    difference = (
        pivot[high_beta].to_numpy() - pivot[control_beta].to_numpy()
    )
    rng = np.random.default_rng(
        BOOTSTRAP_SEED
        + sum(ord(char) for char in architecture + field)
    )
    indices = rng.integers(
        0,
        difference.size,
        size=(BOOTSTRAP_REPS, difference.size),
    )
    bootstrap_means = difference[indices].mean(axis=1)
    lower, upper = np.quantile(bootstrap_means, [0.025, 0.975])
    return {
        "architecture": architecture,
        "field": field,
        "high_beta": high_beta,
        "control_beta": control_beta,
        "n_seeds": int(difference.size),
        "mean_difference": float(difference.mean()),
        "ci95_lower": float(lower),
        "ci95_upper": float(upper),
        "negative_seeds": int(np.sum(difference < 0.0)),
        "positive_seeds": int(np.sum(difference > 0.0)),
        "zero_seeds": int(np.sum(difference == 0.0)),
        "per_seed_difference": {
            str(int(seed)): float(value)
            for seed, value in zip(pivot.index, difference)
        },
    }


def bootstrap_mean_ci(values: np.ndarray, salt: int) -> tuple[float, float]:
    rng = np.random.default_rng(BOOTSTRAP_SEED + salt)
    indices = rng.integers(
        0, values.size, size=(BOOTSTRAP_REPS, values.size)
    )
    means = values[indices].mean(axis=1)
    lower, upper = np.quantile(means, [0.025, 0.975])
    return float(lower), float(upper)


def conformance_checks(
    frame: pd.DataFrame,
    metadata: dict[str, Any],
) -> dict[str, bool]:
    expected_rows = (
        len(EXPECTED_ARCHITECTURES)
        * len(EXPECTED_WIDTHS)
        * len(EXPECTED_BETAS)
        * len(EXPECTED_SEEDS)
    )
    cell_counts = frame.groupby(
        ["architecture", "m", "beta"], dropna=False
    )["seed"].nunique()
    duplicate_count = int(
        frame.duplicated(["architecture", "m", "beta", "seed"]).sum()
    )
    return {
        "row_count": len(frame) == expected_rows,
        "architectures": set(frame["architecture"])
        == set(EXPECTED_ARCHITECTURES),
        "widths": set(frame["m"].astype(int)) == set(EXPECTED_WIDTHS),
        "betas": set(np.round(frame["beta"], 10))
        == set(EXPECTED_BETAS),
        "seeds": set(frame["seed"].astype(int)) == set(EXPECTED_SEEDS),
        "all_cells_have_12_seeds": bool(
            len(cell_counts)
            == len(EXPECTED_ARCHITECTURES)
            * len(EXPECTED_WIDTHS)
            * len(EXPECTED_BETAS)
            and (cell_counts == len(EXPECTED_SEEDS)).all()
        ),
        "no_duplicates": duplicate_count == 0,
        "data_hash": metadata["dataset"]["data_sha256"]
        == EXPECTED_DATA_SHA256,
        "classifier_quality": (
            metadata["dataset"]["classifier_eval_accuracy"] >= 0.94
        ),
        "registered_steps": (
            metadata["config"]["steps"] == 10_000
            and metadata["steps_override"] is None
        ),
        "registered_topk": metadata["config"]["topk_k"] == 16,
        "registered_lambda": abs(
            metadata["config"]["l1_lambda"] - 0.2
        )
        < 1e-12,
    }


def condition_table(frame: pd.DataFrame) -> pd.DataFrame:
    fields = [
        "fvu",
        "l0",
        "dead_fraction",
        "gram_penalty",
        "mean_squared_coherence",
        "max_absolute_coherence",
        "mean_factor_max_positive_cosine",
        "mean_factor_causal_concentration",
        "mean_factor_causal_participation_ratio",
        "mean_factor_causal_split_count",
        "mean_factor_single_gain",
        "mean_factor_family_gain",
        "mean_factor_family_cosine",
        "mean_factor_nnls_residual",
    ]
    return (
        frame.groupby(["architecture", "m", "beta"])[fields]
        .mean()
        .reset_index()
    )


def _markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    separator = "|" + "|".join(["---"] * len(columns)) + "|"
    rows = [header, separator]
    for _, row in frame[columns].iterrows():
        values = []
        for column in columns:
            value = row[column]
            if isinstance(value, (float, np.floating)):
                values.append(f"{value:.4f}")
            else:
                values.append(str(value))
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


def save_weight_manifest(result_dir: Path) -> list[dict[str, Any]]:
    records = []
    for path in sorted(result_dir.glob("weights_*.npz")):
        records.append(
            {
                "filename": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    output_path = result_dir / "weights_sha256.csv"
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["filename", "bytes", "sha256"]
        )
        writer.writeheader()
        writer.writerows(records)
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result_dir", type=Path)
    args = parser.parse_args()

    metrics_path = args.result_dir / "run_metrics.csv"
    metadata_path = args.result_dir / "metadata.json"
    frame = pd.read_csv(metrics_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    conformance = conformance_checks(frame, metadata)
    conformance_pass = all(conformance.values())
    table = condition_table(frame)

    manipulation: dict[str, Any] = {}
    retention: dict[str, Any] = {}
    for architecture in EXPECTED_ARCHITECTURES:
        control = table[
            (table["architecture"] == architecture)
            & (table["beta"] == CONTROL_BETA)
        ].iloc[0]
        high = table[
            (table["architecture"] == architecture)
            & (table["beta"] == HIGH_BETA)
        ].iloc[0]
        gram_ratio = float(high["gram_penalty"] / control["gram_penalty"])
        manipulation[architecture] = {
            "control_gram": float(control["gram_penalty"]),
            "high_gram": float(high["gram_penalty"]),
            "high_over_control_ratio": gram_ratio,
            "pass": gram_ratio <= 0.80,
        }
        high_seed_rows = frame[
            (frame["architecture"] == architecture)
            & (frame["beta"] == HIGH_BETA)
        ]
        gain_values = high_seed_rows[
            "mean_factor_family_gain"
        ].to_numpy()
        gain_lower, gain_upper = bootstrap_mean_ci(
            gain_values, 1000 + sum(ord(c) for c in architecture)
        )
        retention[architecture] = {
            "mean_family_gain": float(gain_values.mean()),
            "family_gain_ci95_lower": gain_lower,
            "family_gain_ci95_upper": gain_upper,
            "mean_family_cosine": float(
                high_seed_rows["mean_factor_family_cosine"].mean()
            ),
            "mean_fvu": float(high_seed_rows["fvu"].mean()),
            "pass": bool(
                gain_values.mean() >= 0.75
                and high_seed_rows["mean_factor_family_cosine"].mean()
                >= 0.95
                and high_seed_rows["fvu"].mean() <= 0.10
            ),
        }

    topk_rows = frame[frame["architecture"] == "topk"]
    fixed_sparsity_pass = bool(
        np.max(np.abs(topk_rows["l0"].to_numpy() - 16.0)) <= 0.05
    )
    gate_pass = bool(
        conformance_pass
        and all(item["pass"] for item in manipulation.values())
        and all(item["pass"] for item in retention.values())
        and fixed_sparsity_pass
    )

    contrast_fields = [
        "mean_factor_max_positive_cosine",
        "mean_factor_causal_concentration",
        "mean_factor_causal_participation_ratio",
        "mean_factor_causal_split_count",
        "mean_factor_single_gain",
        "mean_factor_family_gain",
        "fvu",
        "l0",
        "dead_fraction",
        "gram_penalty",
        "max_absolute_coherence",
    ]
    contrasts = [
        paired_contrast(frame, architecture, field)
        for architecture in EXPECTED_ARCHITECTURES
        for field in contrast_fields
    ]
    contrast_lookup = {
        (item["architecture"], item["field"]): item for item in contrasts
    }

    alignment_pass = {
        architecture: (
            contrast_lookup[
                (architecture, "mean_factor_max_positive_cosine")
            ]["ci95_upper"]
            < 0.0
        )
        for architecture in EXPECTED_ARCHITECTURES
    }
    splitting_pass = {
        architecture: (
            contrast_lookup[
                (architecture, "mean_factor_causal_split_count")
            ]["ci95_lower"]
            > 0.0
            and contrast_lookup[
                (architecture, "mean_factor_causal_participation_ratio")
            ]["ci95_lower"]
            > 0.0
        )
        for architecture in EXPECTED_ARCHITECTURES
    }
    concentration_pass = {
        architecture: (
            contrast_lookup[
                (architecture, "mean_factor_causal_concentration")
            ]["ci95_upper"]
            < 0.0
        )
        for architecture in EXPECTED_ARCHITECTURES
    }

    if not gate_pass:
        primary_verdict = "UNINTERPRETABLE: one or more registered gates failed"
    elif all(alignment_pass.values()):
        primary_verdict = (
            "SUPPORTED: strong full-Gram regularization reduced one-atom "
            "causal-direction alignment while the causal direction remained "
            "recoverable at the decoder-family level in both architectures"
        )
    else:
        primary_verdict = (
            "NOT SUPPORTED: the paired alignment criterion did not pass in "
            "both architectures"
        )

    splitting_verdict = (
        "SUPPORTED IN BOTH ARCHITECTURES"
        if all(splitting_pass.values())
        else (
            "SUPPORTED IN "
            + ", ".join(
                key for key, value in splitting_pass.items() if value
            )
            if any(splitting_pass.values())
            else "NOT SUPPORTED"
        )
    )
    concentration_verdict = (
        "SUPPORTED IN BOTH ARCHITECTURES"
        if all(concentration_pass.values())
        else (
            "SUPPORTED IN "
            + ", ".join(
                key for key, value in concentration_pass.items() if value
            )
            if any(concentration_pass.values())
            else "NOT SUPPORTED"
        )
    )

    weight_records = save_weight_manifest(args.result_dir)
    summary = {
        "primary_verdict": primary_verdict,
        "splitting_verdict": splitting_verdict,
        "concentration_verdict": concentration_verdict,
        "gates": {
            "conformance": conformance,
            "conformance_pass": conformance_pass,
            "manipulation": manipulation,
            "retention": retention,
            "topk_fixed_l0": fixed_sparsity_pass,
            "all_gates_pass": gate_pass,
        },
        "alignment_pass": alignment_pass,
        "splitting_pass": splitting_pass,
        "concentration_pass": concentration_pass,
        "contrasts": contrasts,
        "metrics_sha256": sha256_file(metrics_path),
        "metadata_sha256": sha256_file(metadata_path),
        "weight_file_count": len(weight_records),
    }
    (args.result_dir / "analysis_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    table.to_csv(args.result_dir / "condition_means.csv", index=False)
    pd.DataFrame(
        [
            {
                key: value
                for key, value in contrast.items()
                if key != "per_seed_difference"
            }
            for contrast in contrasts
        ]
    ).to_csv(args.result_dir / "paired_contrasts.csv", index=False)

    focus_columns = [
        "architecture",
        "beta",
        "fvu",
        "l0",
        "dead_fraction",
        "gram_penalty",
        "max_absolute_coherence",
        "mean_factor_max_positive_cosine",
        "mean_factor_causal_concentration",
        "mean_factor_causal_split_count",
        "mean_factor_family_gain",
    ]
    focus_table = table.copy()
    focus_table["beta"] = focus_table["beta"].map(lambda value: f"{value:g}")
    report_lines = [
        "# Semi-real coherence-transfer experiment: registered analysis",
        "",
        f"**Primary verdict:** {primary_verdict}",
        "",
        f"**Activation-aware splitting:** {splitting_verdict}.",
        "",
        f"**Causal-contribution concentration loss:** "
        f"{concentration_verdict}.",
        "",
        "## Gates",
        "",
        f"- Conformance: {'PASS' if conformance_pass else 'FAIL'}",
        f"- Coherence manipulation: "
        f"{'PASS' if all(x['pass'] for x in manipulation.values()) else 'FAIL'}",
        f"- Family-retention gate: "
        f"{'PASS' if all(x['pass'] for x in retention.values()) else 'FAIL'}",
        f"- TopK fixed-L0 gate: {'PASS' if fixed_sparsity_pass else 'FAIL'}",
        "",
        "## Condition means",
        "",
        _markdown_table(focus_table, focus_columns),
        "",
        "## Registered high-minus-control contrasts",
        "",
    ]
    for architecture in EXPECTED_ARCHITECTURES:
        report_lines.append(f"### {architecture.upper()}")
        report_lines.append("")
        for field in [
            "mean_factor_max_positive_cosine",
            "mean_factor_causal_concentration",
            "mean_factor_causal_participation_ratio",
            "mean_factor_causal_split_count",
            "mean_factor_family_gain",
            "fvu",
            "l0",
            "dead_fraction",
            "gram_penalty",
            "max_absolute_coherence",
        ]:
            item = contrast_lookup[(architecture, field)]
            report_lines.append(
                f"- `{field}`: {item['mean_difference']:+.4f}, "
                f"95% paired-seed bootstrap CI "
                f"[{item['ci95_lower']:+.4f}, "
                f"{item['ci95_upper']:+.4f}], "
                f"{item['negative_seeds']}/{item['n_seeds']} negative."
            )
        report_lines.append("")
    report_lines.extend(
        [
            "## Scope",
            "",
            "This is a trained, held-out, matched-seed SAE experiment on a "
            "learned neural representation of real images with two appended "
            "and orthogonally mixed controlled factors. It is not an LLM "
            "activation experiment, and the appended factors are synthetic. "
            "The causal claim is limited to recovery of those known activation "
            "generators. The full squared-Gram penalty tested here also differs "
            "from OrtSAE's randomized positive-neighbor penalty.",
            "",
        ]
    )
    (args.result_dir / "REGISTERED_ANALYSIS.md").write_text(
        "\n".join(report_lines), encoding="utf-8"
    )

    print(primary_verdict)
    print(f"splitting: {splitting_verdict}")
    print(f"concentration: {concentration_verdict}")
    print(f"all gates pass: {gate_pass}")
    for architecture in EXPECTED_ARCHITECTURES:
        item = contrast_lookup[
            (architecture, "mean_factor_max_positive_cosine")
        ]
        print(
            f"{architecture} alignment high-control "
            f"{item['mean_difference']:+.4f} "
            f"CI [{item['ci95_lower']:+.4f}, "
            f"{item['ci95_upper']:+.4f}]"
        )


if __name__ == "__main__":
    main()
````

# Appendix O — frozen gradient and causal-construction checker

````python
#!/usr/bin/env python3
"""Finite-difference checks for the NumPy SAE and causal-data construction."""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from experiments.coherence_transfer_semireal import (
    Config,
    _apply_topk,
    _gram_penalty_and_grad,
    build_dataset,
)


def objective_and_gradients(
    batch: np.ndarray,
    parameters: dict[str, np.ndarray],
    cfg: Config,
    beta: float,
    architecture: str,
) -> tuple[float, dict[str, np.ndarray]]:
    encoder = parameters["encoder"]
    encoder_bias = parameters["encoder_bias"]
    decoder = parameters["decoder"]
    decoder_bias = parameters["decoder_bias"]
    centered = batch - decoder_bias
    preactivation = centered @ encoder + encoder_bias
    dense_features = np.maximum(preactivation, 0.0)
    if architecture == "l1":
        features = dense_features
        active_mask = preactivation > 0.0
    else:
        features, active_mask = _apply_topk(
            dense_features, cfg.topk_k
        )
    reconstruction = features @ decoder.T + decoder_bias
    residual = reconstruction - batch
    batch_n = batch.shape[0]
    gram_penalty, gram_gradient = _gram_penalty_and_grad(decoder)
    objective = float(np.sum(residual * residual) / batch_n)
    if architecture == "l1":
        objective += cfg.l1_lambda * float(np.sum(features) / batch_n)
    objective += beta * gram_penalty

    grad_reconstruction = (2.0 / batch_n) * residual
    grad_decoder = grad_reconstruction.T @ features + beta * gram_gradient
    grad_features = grad_reconstruction @ decoder
    if architecture == "l1":
        grad_features += cfg.l1_lambda / batch_n
    grad_preactivation = grad_features * active_mask
    gradients = {
        "encoder": centered.T @ grad_preactivation,
        "encoder_bias": np.sum(grad_preactivation, axis=0),
        "decoder": grad_decoder,
        "decoder_bias": (
            np.sum(grad_reconstruction, axis=0)
            - np.sum(grad_preactivation @ encoder.T, axis=0)
        ),
    }
    return objective, gradients


def directional_check(architecture: str) -> float:
    rng = np.random.default_rng(1234)
    batch_n, d, m = 7, 4, 6
    cfg = replace(Config(), topk_k=2)
    batch = rng.normal(size=(batch_n, d))
    decoder = rng.normal(size=(d, m))
    decoder /= np.linalg.norm(decoder, axis=0, keepdims=True)
    parameters = {
        "encoder": rng.normal(size=(d, m)) * 0.3,
        "encoder_bias": rng.normal(size=m) * 0.2 + 0.15,
        "decoder": decoder,
        "decoder_bias": rng.normal(size=d) * 0.1,
    }
    directions = {
        name: rng.normal(size=value.shape)
        for name, value in parameters.items()
    }
    direction_norm = np.sqrt(
        sum(np.sum(value * value) for value in directions.values())
    )
    for value in directions.values():
        value /= direction_norm

    _, gradients = objective_and_gradients(
        batch, parameters, cfg, beta=0.17, architecture=architecture
    )
    analytic = float(
        sum(
            np.sum(gradients[name] * directions[name])
            for name in parameters
        )
    )
    epsilon = 1e-6
    plus = {
        name: value + epsilon * directions[name]
        for name, value in parameters.items()
    }
    minus = {
        name: value - epsilon * directions[name]
        for name, value in parameters.items()
    }
    objective_plus, _ = objective_and_gradients(
        batch, plus, cfg, beta=0.17, architecture=architecture
    )
    objective_minus, _ = objective_and_gradients(
        batch, minus, cfg, beta=0.17, architecture=architecture
    )
    numeric = (objective_plus - objective_minus) / (2.0 * epsilon)
    relative_error = abs(analytic - numeric) / max(
        1.0, abs(analytic), abs(numeric)
    )
    print(
        f"{architecture}: analytic={analytic:.12f} "
        f"numeric={numeric:.12f} relative_error={relative_error:.3e}"
    )
    return relative_error


def gram_check() -> float:
    rng = np.random.default_rng(4321)
    decoder = rng.normal(size=(5, 8))
    decoder /= np.linalg.norm(decoder, axis=0, keepdims=True)
    direction = rng.normal(size=decoder.shape)
    direction /= np.linalg.norm(direction)
    _, gradient = _gram_penalty_and_grad(decoder)
    analytic = float(np.sum(gradient * direction))
    epsilon = 1e-6
    plus, _ = _gram_penalty_and_grad(decoder + epsilon * direction)
    minus, _ = _gram_penalty_and_grad(decoder - epsilon * direction)
    numeric = (plus - minus) / (2.0 * epsilon)
    relative_error = abs(analytic - numeric) / max(
        1.0, abs(analytic), abs(numeric)
    )
    print(
        f"gram: analytic={analytic:.12f} numeric={numeric:.12f} "
        f"relative_error={relative_error:.3e}"
    )
    return relative_error


def causal_direction_check() -> float:
    cfg = Config()
    dataset = build_dataset(cfg)
    shaped = dataset.eval_x.reshape(dataset.eval_base_n, 4, -1)
    observed_1 = 0.5 * (
        (shaped[:, 1] - shaped[:, 0])
        + (shaped[:, 3] - shaped[:, 2])
    )
    observed_2 = 0.5 * (
        (shaped[:, 2] - shaped[:, 0])
        + (shaped[:, 3] - shaped[:, 1])
    )
    expected = (
        dataset.effective_factor_amplitude
        * dataset.causal_directions
    )
    error = max(
        float(np.max(np.abs(observed_1 - expected[0]))),
        float(np.max(np.abs(observed_2 - expected[1]))),
    )
    print(f"causal construction max_abs_error={error:.3e}")
    return error


def main() -> None:
    errors = [
        gram_check(),
        directional_check("l1"),
        directional_check("topk"),
    ]
    causal_error = causal_direction_check()
    assert max(errors) < 1e-7
    assert causal_error < 2e-6
    print("ALL GRADIENT AND CAUSAL-CONSTRUCTION CHECKS PASSED")


if __name__ == "__main__":
    main()
````

# Appendix P — post-hoc robustness source (exploratory)

````python
#!/usr/bin/env python3
"""Exploratory robustness checks run after the registered analysis.

Nothing in this file changes the preregistered verdict.  It probes threshold
sensitivity, per-image intervention retention, cross-factor leakage, and the
unit-norm-tight-frame/antipodal-pair degeneracy of the full Gram-sum penalty.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from experiments.coherence_transfer_semireal import (  # noqa: E402
    Config,
    _encode,
    _paired_factor_effects,
    build_dataset,
)


WEIGHT_PATTERN = re.compile(
    r"weights_(?P<architecture>l1|topk)_m(?P<m>\d+)_"
    r"seed(?P<seed>\d+)_beta(?P<beta>.+)\.npz"
)
CONTROL_BETA = 0.0
HIGH_BETA = 0.5
BOOTSTRAP_REPS = 20_000


def parse_weight_name(path: Path) -> dict[str, Any]:
    match = WEIGHT_PATTERN.fullmatch(path.name)
    if match is None:
        raise ValueError(f"unexpected weight filename: {path.name}")
    return {
        "architecture": match.group("architecture"),
        "m": int(match.group("m")),
        "seed": int(match.group("seed")),
        "beta": float(match.group("beta")),
    }


def paired_bootstrap(
    frame: pd.DataFrame,
    architecture: str,
    field: str,
) -> dict[str, float]:
    subset = frame[
        (frame["architecture"] == architecture)
        & (frame["beta"].isin([CONTROL_BETA, HIGH_BETA]))
    ]
    pivot = subset.pivot(index="seed", columns="beta", values=field)
    difference = (
        pivot[HIGH_BETA].to_numpy()
        - pivot[CONTROL_BETA].to_numpy()
    )
    salt = sum(ord(char) for char in architecture + field)
    rng = np.random.default_rng(20260725 + salt)
    indices = rng.integers(
        0, difference.size, size=(BOOTSTRAP_REPS, difference.size)
    )
    means = difference[indices].mean(axis=1)
    lower, upper = np.quantile(means, [0.025, 0.975])
    return {
        "mean_difference": float(difference.mean()),
        "ci95_lower": float(lower),
        "ci95_upper": float(upper),
        "negative_seeds": int(np.sum(difference < 0)),
        "positive_seeds": int(np.sum(difference > 0)),
    }


def inspect_run(
    path: Path,
    dataset: Any,
    cfg: Config,
    random_control_directions: np.ndarray,
) -> dict[str, Any]:
    identity = parse_weight_name(path)
    weights = np.load(path)
    decoder = weights["decoder"]
    encoder = weights["encoder"]
    encoder_bias = weights["encoder_bias"]
    decoder_bias = weights["decoder_bias"]
    _, features, _ = _encode(
        dataset.eval_x,
        encoder,
        encoder_bias,
        decoder_bias,
        identity["architecture"],
        cfg.topk_k,
    )
    reconstruction = features @ decoder.T + decoder_bias
    feature_effects = _paired_factor_effects(
        features, dataset.eval_base_n
    )
    reconstruction_effects = _paired_factor_effects(
        reconstruction, dataset.eval_base_n
    )

    gram = decoder.T @ decoder
    upper_values = gram[np.triu_indices(gram.shape[0], k=1)]
    d, m = decoder.shape
    welch_floor = m * (m - d) / (2.0 * d)
    gram_sum = float(np.sum(upper_values * upper_values))
    frame_operator = decoder @ decoder.T
    tight_target = (m / d) * np.eye(d)

    record: dict[str, Any] = {
        **identity,
        "gram_sum_recomputed": gram_sum,
        "welch_floor": welch_floor,
        "gram_excess_above_welch": gram_sum - welch_floor,
        "frame_tightness_frobenius": float(
            np.linalg.norm(frame_operator - tight_target)
        ),
        "pairs_cos_gt_099": int(np.sum(upper_values > 0.99)),
        "pairs_cos_lt_neg099": int(np.sum(upper_values < -0.99)),
        "pairs_abs_cos_gt_099": int(
            np.sum(np.abs(upper_values) > 0.99)
        ),
        "pairs_abs_cos_gt_095": int(
            np.sum(np.abs(upper_values) > 0.95)
        ),
        "random_direction_max_positive_cosine": float(
            np.mean(
                np.max(
                    np.maximum(random_control_directions @ decoder, 0.0),
                    axis=1,
                )
            )
        ),
    }

    per_factor_records = []
    for factor_index in range(2):
        direction = dataset.causal_directions[factor_index]
        other_direction = dataset.causal_directions[1 - factor_index]
        feature_effect = feature_effects[factor_index]
        reconstruction_effect = reconstruction_effects[factor_index]
        mean_feature_effect = feature_effect.mean(axis=0)
        decoder_cosines = direction @ decoder
        contributions = np.maximum(
            mean_feature_effect * decoder_cosines, 0.0
        )
        positive_read_contributions = (
            np.maximum(mean_feature_effect, 0.0)
            * np.maximum(decoder_cosines, 0.0)
        )
        negative_release_contributions = (
            np.maximum(-mean_feature_effect, 0.0)
            * np.maximum(-decoder_cosines, 0.0)
        )
        best_index = int(np.argmax(contributions))
        best_positive_index = int(np.argmax(positive_read_contributions))
        best_contribution_cosine = float(decoder_cosines[best_index])
        individual_gain = (
            reconstruction_effect @ direction
            / dataset.effective_factor_amplitude
        )
        individual_cross_gain = (
            reconstruction_effect @ other_direction
            / dataset.effective_factor_amplitude
        )
        factor_record: dict[str, Any] = {
            "planted_max_positive_cosine": float(
                np.max(np.maximum(decoder_cosines, 0.0))
            ),
            "best_contributing_atom_cosine": best_contribution_cosine,
            "best_positive_read_atom_cosine": float(
                decoder_cosines[best_positive_index]
            ),
            "positive_read_gain_sum": float(
                np.sum(positive_read_contributions)
                / dataset.effective_factor_amplitude
            ),
            "negative_release_gain_sum": float(
                np.sum(negative_release_contributions)
                / dataset.effective_factor_amplitude
            ),
            "individual_gain_median": float(
                np.median(individual_gain)
            ),
            "individual_gain_q10": float(
                np.quantile(individual_gain, 0.10)
            ),
            "individual_gain_q90": float(
                np.quantile(individual_gain, 0.90)
            ),
            "individual_gain_fraction_gt_050": float(
                np.mean(individual_gain > 0.50)
            ),
            "individual_gain_fraction_gt_075": float(
                np.mean(individual_gain > 0.75)
            ),
            "individual_cross_gain_abs_mean": float(
                np.mean(np.abs(individual_cross_gain))
            ),
        }
        for threshold in (0.05, 0.10, 0.20, 0.30):
            cutoff = threshold * max(float(np.max(contributions)), 1e-12)
            factor_record[
                f"split_count_rel_{int(threshold * 100):02d}"
            ] = int(np.sum(contributions >= cutoff))
            positive_cutoff = threshold * max(
                float(np.max(positive_read_contributions)), 1e-12
            )
            factor_record[
                f"positive_read_split_count_rel_"
                f"{int(threshold * 100):02d}"
            ] = int(
                np.sum(positive_read_contributions >= positive_cutoff)
            )
        for threshold in (0.80, 0.90, 0.95):
            factor_record[
                f"geometry_above_{int(threshold * 100):02d}"
            ] = float(np.max(np.maximum(decoder_cosines, 0.0)) >= threshold)
        per_factor_records.append(factor_record)

    for key in per_factor_records[0]:
        record[key] = float(
            0.5
            * (
                per_factor_records[0][key]
                + per_factor_records[1][key]
            )
        )
    record["planted_alignment_excess_over_random"] = (
        record["planted_max_positive_cosine"]
        - record["random_direction_max_positive_cosine"]
    )
    return record


def markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    lines = [
        "| " + " | ".join(columns) + " |",
        "|" + "|".join(["---"] * len(columns)) + "|",
    ]
    for _, row in frame[columns].iterrows():
        values = []
        for column in columns:
            value = row[column]
            if isinstance(value, (float, np.floating)):
                values.append(f"{value:.4f}")
            else:
                values.append(str(value))
        lines.append("| " + " | ".join(values) + " |")
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result_dir", type=Path)
    args = parser.parse_args()
    cfg = Config()
    dataset = build_dataset(cfg)
    control_rng = np.random.default_rng(424242)
    random_control_directions = control_rng.normal(
        size=(256, dataset.ambient_dim)
    )
    # Negative-control directions live outside the two-factor plane.
    random_control_directions -= (
        random_control_directions @ dataset.causal_directions.T
    ) @ dataset.causal_directions
    random_control_directions /= np.linalg.norm(
        random_control_directions, axis=1, keepdims=True
    )
    records = [
        inspect_run(path, dataset, cfg, random_control_directions)
        for path in sorted(args.result_dir.glob("weights_*.npz"))
    ]
    frame = pd.DataFrame(records)
    frame.to_csv(
        args.result_dir / "posthoc_robustness_metrics.csv", index=False
    )
    mean_fields = [
        "gram_excess_above_welch",
        "frame_tightness_frobenius",
        "pairs_cos_gt_099",
        "pairs_cos_lt_neg099",
        "pairs_abs_cos_gt_099",
        "pairs_abs_cos_gt_095",
        "random_direction_max_positive_cosine",
        "planted_max_positive_cosine",
        "planted_alignment_excess_over_random",
        "best_contributing_atom_cosine",
        "best_positive_read_atom_cosine",
        "positive_read_gain_sum",
        "negative_release_gain_sum",
        "individual_gain_median",
        "individual_gain_q10",
        "individual_gain_fraction_gt_050",
        "individual_gain_fraction_gt_075",
        "individual_cross_gain_abs_mean",
        "split_count_rel_05",
        "split_count_rel_10",
        "split_count_rel_20",
        "split_count_rel_30",
        "positive_read_split_count_rel_05",
        "positive_read_split_count_rel_10",
        "positive_read_split_count_rel_20",
        "positive_read_split_count_rel_30",
        "geometry_above_80",
        "geometry_above_90",
        "geometry_above_95",
    ]
    means = (
        frame.groupby(["architecture", "m", "beta"])[mean_fields]
        .mean()
        .reset_index()
    )
    means.to_csv(
        args.result_dir / "posthoc_robustness_condition_means.csv",
        index=False,
    )

    contrast_fields = [
        "gram_excess_above_welch",
        "pairs_abs_cos_gt_099",
        "pairs_cos_lt_neg099",
        "random_direction_max_positive_cosine",
        "planted_max_positive_cosine",
        "planted_alignment_excess_over_random",
        "best_contributing_atom_cosine",
        "best_positive_read_atom_cosine",
        "positive_read_gain_sum",
        "negative_release_gain_sum",
        "individual_gain_median",
        "individual_gain_q10",
        "individual_gain_fraction_gt_050",
        "individual_cross_gain_abs_mean",
        "split_count_rel_05",
        "split_count_rel_10",
        "split_count_rel_20",
        "split_count_rel_30",
        "positive_read_split_count_rel_05",
        "positive_read_split_count_rel_10",
        "positive_read_split_count_rel_20",
        "positive_read_split_count_rel_30",
        "geometry_above_80",
        "geometry_above_90",
        "geometry_above_95",
    ]
    contrasts = {
        architecture: {
            field: paired_bootstrap(frame, architecture, field)
            for field in contrast_fields
        }
        for architecture in ("l1", "topk")
    }
    (args.result_dir / "posthoc_robustness_summary.json").write_text(
        json.dumps(contrasts, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    focus_columns = [
        "architecture",
        "beta",
        "gram_excess_above_welch",
        "pairs_cos_lt_neg099",
        "pairs_cos_gt_099",
        "random_direction_max_positive_cosine",
        "planted_max_positive_cosine",
        "planted_alignment_excess_over_random",
        "best_contributing_atom_cosine",
        "best_positive_read_atom_cosine",
        "positive_read_gain_sum",
        "negative_release_gain_sum",
        "individual_gain_median",
        "individual_gain_q10",
        "individual_gain_fraction_gt_050",
        "individual_cross_gain_abs_mean",
        "split_count_rel_05",
        "split_count_rel_10",
        "split_count_rel_20",
        "split_count_rel_30",
        "positive_read_split_count_rel_05",
        "positive_read_split_count_rel_10",
        "positive_read_split_count_rel_20",
        "positive_read_split_count_rel_30",
    ]
    display_means = means.copy()
    display_means["beta"] = display_means["beta"].map(
        lambda value: f"{value:g}"
    )
    lines = [
        "# Post-hoc robustness analysis (exploratory)",
        "",
        "These checks were written after the registered verdict and do not "
        "change it.",
        "",
        "## Condition means",
        "",
        markdown_table(display_means, focus_columns),
        "",
        "## High-minus-control threshold sensitivity",
        "",
    ]
    for architecture in ("l1", "topk"):
        lines.extend([f"### {architecture.upper()}", ""])
        for field in contrast_fields:
            item = contrasts[architecture][field]
            lines.append(
                f"- `{field}`: {item['mean_difference']:+.4f}, "
                f"95% paired-seed bootstrap CI "
                f"[{item['ci95_lower']:+.4f}, "
                f"{item['ci95_upper']:+.4f}]."
            )
        lines.append("")
    lines.extend(
        [
            "## Exact frame-potential reference",
            "",
            "For unit columns in R^{d×m}, the Gram-sum floor is "
            "m(m−d)/(2d). Here d=34 and m=68, so the exact floor is 34. "
            "The signed duplicated basis [I,−I] attains that floor while "
            "having maximum absolute coherence 1. Thus a lower Gram sum "
            "does not imply lower mutual coherence; near-antipodal-pair "
            "counts above diagnose this known tight-frame degeneracy.",
            "",
        ]
    )
    (args.result_dir / "POSTHOC_ROBUSTNESS.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )
    print(
        f"saved exploratory robustness analysis for {len(frame)} runs"
    )


if __name__ == "__main__":
    main()
````

# Appendix Q — artifact audit and dossier-generation source

````python
#!/usr/bin/env python3
"""Build a single-file verification dossier for the semi-real SAE experiment."""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
RESULT_DIR = ROOT / "results" / "coherence_transfer_semireal"
OUTPUT_PATH = RESULT_DIR / "EMPIRICAL_VERIFICATION_DOSSIER.md"

TRAINING_PATH = ROOT / "experiments" / "coherence_transfer_semireal.py"
ANALYSIS_PATH = ROOT / "analysis" / "analyze_coherence_transfer_semireal.py"
GRADIENT_PATH = ROOT / "analysis" / "check_coherence_transfer_gradients.py"
POSTHOC_PATH = ROOT / "analysis" / "posthoc_coherence_transfer_robustness.py"
PREREG_PATH = ROOT / "notes" / "prereg-coherence-transfer-semireal.md"
FORMAL_PDF_PATH = (
    ROOT / "output" / "pdf" / "Causal_Ontology_Coherence_Inversion_Report.pdf"
)
PACKAGE_PATH = (
    ROOT / "output" / "Causal_Ontology_Coherence_Inversion_Research_Package.zip"
)

EXPECTED_ARCHITECTURES = ("l1", "topk")
EXPECTED_BETAS = (0.0, 0.025, 0.0625, 0.25, 0.5)
EXPECTED_SEEDS = tuple(range(12))
EXPECTED_WIDTH = 68
EXPECTED_DATA_SHA256 = (
    "d00e7d6c272ae538920cc91b7ab92e8ba91f522eb1c62b05677fbdc56799bad9"
)
BOOTSTRAP_REPS = 20_000
BOOTSTRAP_SEED = 8_675_309


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_csv(path: Path) -> tuple[list[dict[str, str]], list[str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        return rows, list(reader.fieldnames or [])


def load_experiment_module() -> Any:
    spec = importlib.util.spec_from_file_location(
        "coherence_transfer_semireal",
        TRAINING_PATH,
    )
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load experiment module")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def checkpoint_name(
    architecture: str,
    seed: int,
    beta: float,
) -> str:
    return (
        f"weights_{architecture}_m{EXPECTED_WIDTH}_"
        f"seed{seed:03d}_beta{beta:.6g}.npz"
    )


def audit_artifacts() -> dict[str, Any]:
    experiment = load_experiment_module()
    metadata = json.loads((RESULT_DIR / "metadata.json").read_text())
    rows, _ = read_csv(RESULT_DIR / "run_metrics.csv")
    manifest, _ = read_csv(RESULT_DIR / "weights_sha256.csv")

    dataset = experiment.build_dataset(experiment.Config())
    if dataset.data_sha256 != EXPECTED_DATA_SHA256:
        raise AssertionError("reconstructed data digest differs from registration")
    if dataset.data_sha256 != metadata["dataset"]["data_sha256"]:
        raise AssertionError("reconstructed data digest differs from metadata")

    observed = {
        (
            row["architecture"],
            int(row["m"]),
            int(row["seed"]),
            float(row["beta"]),
        )
        for row in rows
    }
    expected = {
        (architecture, EXPECTED_WIDTH, seed, beta)
        for architecture in EXPECTED_ARCHITECTURES
        for seed in EXPECTED_SEEDS
        for beta in EXPECTED_BETAS
    }
    if len(rows) != 120 or len(observed) != 120 or observed != expected:
        raise AssertionError("registered run table does not have exact coverage")

    manifest_by_name = {record["filename"]: record for record in manifest}
    actual_checkpoints = sorted(RESULT_DIR.glob("weights_*.npz"))
    if len(manifest) != 120 or len(actual_checkpoints) != 120:
        raise AssertionError("checkpoint count differs from 120")
    if set(manifest_by_name) != {path.name for path in actual_checkpoints}:
        raise AssertionError("checkpoint manifest filenames do not match files")

    maximum_metric_error = 0.0
    maximum_factor_array_error = 0.0
    maximum_decoder_norm_error = 0.0
    for row in rows:
        architecture = row["architecture"]
        seed = int(row["seed"])
        beta = float(row["beta"])
        path = RESULT_DIR / checkpoint_name(architecture, seed, beta)
        manifest_record = manifest_by_name[path.name]
        if path.stat().st_size != int(manifest_record["bytes"]):
            raise AssertionError(f"checkpoint size mismatch: {path.name}")
        if sha256_file(path) != manifest_record["sha256"]:
            raise AssertionError(f"checkpoint digest mismatch: {path.name}")

        with np.load(path) as archive:
            parameters = {
                name: archive[name]
                for name in (
                    "encoder",
                    "encoder_bias",
                    "decoder",
                    "decoder_bias",
                )
            }
            if not all(np.isfinite(value).all() for value in parameters.values()):
                raise AssertionError(f"non-finite checkpoint value: {path.name}")
            norm_error = float(
                np.max(
                    np.abs(
                        np.linalg.norm(parameters["decoder"], axis=0) - 1.0
                    )
                )
            )
            maximum_decoder_norm_error = max(
                maximum_decoder_norm_error,
                norm_error,
            )
            if norm_error > 2e-6:
                raise AssertionError(f"decoder norm error: {path.name}")

            evaluated, factor_arrays = experiment.evaluate_sae(
                parameters,
                dataset,
                experiment.Config(),
                seed,
                beta,
                architecture,
            )
            for field, value in evaluated.items():
                if isinstance(value, bool):
                    observed_value = row[field].strip().lower() == "true"
                    if observed_value != value:
                        raise AssertionError(
                            f"boolean metric mismatch: {path.name} {field}"
                        )
                elif isinstance(
                    value,
                    (int, float, np.integer, np.floating),
                ):
                    error = abs(float(row[field]) - float(value))
                    maximum_metric_error = max(maximum_metric_error, error)
                    if error > 2e-7:
                        raise AssertionError(
                            f"metric mismatch: {path.name} {field} {error}"
                        )
            for field, value in factor_arrays.items():
                error = float(np.max(np.abs(archive[field] - value)))
                maximum_factor_array_error = max(
                    maximum_factor_array_error,
                    error,
                )
                if error > 2e-7:
                    raise AssertionError(
                        f"factor-array mismatch: {path.name} {field} {error}"
                    )

    published_conditions, condition_fields = read_csv(
        RESULT_DIR / "condition_means.csv"
    )
    maximum_condition_error = 0.0
    for published in published_conditions:
        subset = [
            row
            for row in rows
            if row["architecture"] == published["architecture"]
            and int(row["m"]) == int(published["m"])
            and float(row["beta"]) == float(published["beta"])
        ]
        for field in condition_fields:
            if field in {"architecture", "m", "beta"}:
                continue
            mean = sum(float(row[field]) for row in subset) / len(subset)
            maximum_condition_error = max(
                maximum_condition_error,
                abs(mean - float(published[field])),
            )

    published_contrasts, _ = read_csv(RESULT_DIR / "paired_contrasts.csv")
    maximum_contrast_error = 0.0
    maximum_bootstrap_error = 0.0
    for published in published_contrasts:
        architecture = published["architecture"]
        field = published["field"]
        differences = []
        for seed in EXPECTED_SEEDS:
            control = next(
                float(row[field])
                for row in rows
                if row["architecture"] == architecture
                and int(row["seed"]) == seed
                and float(row["beta"]) == 0.0
            )
            high = next(
                float(row[field])
                for row in rows
                if row["architecture"] == architecture
                and int(row["seed"]) == seed
                and float(row["beta"]) == 0.5
            )
            differences.append(high - control)
        difference_array = np.asarray(differences)
        maximum_contrast_error = max(
            maximum_contrast_error,
            abs(
                float(difference_array.mean())
                - float(published["mean_difference"])
            ),
        )
        counts = (
            int(np.sum(difference_array < 0.0)),
            int(np.sum(difference_array > 0.0)),
            int(np.sum(difference_array == 0.0)),
        )
        published_counts = (
            int(published["negative_seeds"]),
            int(published["positive_seeds"]),
            int(published["zero_seeds"]),
        )
        if counts != published_counts:
            raise AssertionError(
                f"paired sign counts differ: {architecture} {field}"
            )

        rng = np.random.default_rng(
            BOOTSTRAP_SEED
            + sum(ord(character) for character in architecture + field)
        )
        indices = rng.integers(
            0,
            len(difference_array),
            size=(BOOTSTRAP_REPS, len(difference_array)),
        )
        bootstrap_means = difference_array[indices].mean(axis=1)
        lower, upper = np.quantile(bootstrap_means, [0.025, 0.975])
        maximum_bootstrap_error = max(
            maximum_bootstrap_error,
            abs(float(lower) - float(published["ci95_lower"])),
            abs(float(upper) - float(published["ci95_upper"])),
        )

    def cell_mean(architecture: str, beta: float, field: str) -> float:
        values = [
            float(row[field])
            for row in rows
            if row["architecture"] == architecture
            and float(row["beta"]) == beta
        ]
        return float(np.mean(values))

    gate_values: dict[str, dict[str, float | bool]] = {}
    for architecture in EXPECTED_ARCHITECTURES:
        gate_values[architecture] = {
            "gram_ratio_high_over_control": (
                cell_mean(architecture, 0.5, "gram_penalty")
                / cell_mean(architecture, 0.0, "gram_penalty")
            ),
            "high_beta_family_gain": cell_mean(
                architecture,
                0.5,
                "mean_factor_family_gain",
            ),
            "high_beta_family_cosine": cell_mean(
                architecture,
                0.5,
                "mean_factor_family_cosine",
            ),
            "high_beta_fvu": cell_mean(architecture, 0.5, "fvu"),
        }
    topk_l0_deviation = max(
        abs(float(row["l0"]) - 16.0)
        for row in rows
        if row["architecture"] == "topk"
    )

    gradient_check = subprocess.run(
        [sys.executable, str(GRADIENT_PATH)],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()

    return {
        "dataset_sha256": dataset.data_sha256,
        "classifier_eval_accuracy": dataset.classifier_eval_accuracy,
        "run_rows": len(rows),
        "unique_run_cells": len(observed),
        "checkpoint_count": len(actual_checkpoints),
        "checkpoint_manifest_failures": 0,
        "maximum_decoder_norm_error": maximum_decoder_norm_error,
        "maximum_checkpoint_metric_error": maximum_metric_error,
        "maximum_saved_factor_array_error": maximum_factor_array_error,
        "maximum_condition_mean_error": maximum_condition_error,
        "maximum_paired_mean_error": maximum_contrast_error,
        "maximum_bootstrap_endpoint_error": maximum_bootstrap_error,
        "bootstrap_intervals_recomputed": len(published_contrasts),
        "gate_values": gate_values,
        "topk_maximum_l0_deviation": topk_l0_deviation,
        "gradient_check_output": gradient_check,
    }


def markdown_table(headers: list[str], rows: list[list[str]]) -> str:
    lines = [
        "| " + " | ".join(headers) + " |",
        "|" + "|".join("---" for _ in headers) + "|",
    ]
    lines.extend("| " + " | ".join(row) + " |" for row in rows)
    return "\n".join(lines)


def paired_seed_table() -> str:
    rows, _ = read_csv(RESULT_DIR / "run_metrics.csv")
    output: list[list[str]] = []
    fields = (
        "mean_factor_max_positive_cosine",
        "mean_factor_causal_concentration",
        "mean_factor_causal_participation_ratio",
        "mean_factor_causal_split_count",
        "fvu",
        "l0",
    )
    for architecture in EXPECTED_ARCHITECTURES:
        for seed in EXPECTED_SEEDS:
            control = next(
                row
                for row in rows
                if row["architecture"] == architecture
                and int(row["seed"]) == seed
                and float(row["beta"]) == 0.0
            )
            high = next(
                row
                for row in rows
                if row["architecture"] == architecture
                and int(row["seed"]) == seed
                and float(row["beta"]) == 0.5
            )
            differences = {
                field: float(high[field]) - float(control[field])
                for field in fields
            }
            output.append(
                [
                    architecture,
                    str(seed),
                    f"{differences['mean_factor_max_positive_cosine']:+.6f}",
                    f"{differences['mean_factor_causal_concentration']:+.6f}",
                    f"{differences['mean_factor_causal_participation_ratio']:+.6f}",
                    f"{differences['mean_factor_causal_split_count']:+.3f}",
                    f"{float(high['mean_factor_family_gain']):.6f}",
                    f"{float(high['mean_factor_family_cosine']):.6f}",
                    f"{differences['fvu']:+.6f}",
                    f"{differences['l0']:+.6f}",
                ]
            )
    return markdown_table(
        [
            "architecture",
            "seed",
            "Δ alignment",
            "Δ concentration",
            "Δ participation",
            "Δ split count",
            "high-β family gain",
            "high-β family cosine",
            "Δ FVU",
            "Δ L0",
        ],
        output,
    )


def file_manifest_table(paths: list[Path]) -> str:
    rows = []
    for path in paths:
        rows.append(
            [
                str(path.relative_to(ROOT)),
                str(path.stat().st_size),
                sha256_file(path),
            ]
        )
    return markdown_table(["file", "bytes", "SHA-256"], rows)


def fenced_file(path: Path, language: str) -> str:
    text = path.read_text(encoding="utf-8").rstrip()
    return f"````{language}\n{text}\n````"


def build_dossier(audit: dict[str, Any]) -> str:
    embedded_files = [
        PREREG_PATH,
        TRAINING_PATH,
        ANALYSIS_PATH,
        GRADIENT_PATH,
        POSTHOC_PATH,
        Path(__file__).resolve(),
        RESULT_DIR / "metadata.json",
        RESULT_DIR / "REGISTERED_ANALYSIS.md",
        RESULT_DIR / "condition_means.csv",
        RESULT_DIR / "paired_contrasts.csv",
        RESULT_DIR / "analysis_summary.json",
        RESULT_DIR / "run_metrics.csv",
        RESULT_DIR / "POSTHOC_ROBUSTNESS.md",
        RESULT_DIR / "posthoc_robustness_condition_means.csv",
        RESULT_DIR / "posthoc_robustness_summary.json",
        RESULT_DIR / "posthoc_robustness_metrics.csv",
        RESULT_DIR / "weights_sha256.csv",
    ]
    integrity_files = embedded_files + [
        RESULT_DIR / "coherence_transfer_dose_response.png",
        FORMAL_PDF_PATH,
        PACKAGE_PATH,
    ]
    gate_rows = []
    for architecture in EXPECTED_ARCHITECTURES:
        values = audit["gate_values"][architecture]
        gate_rows.append(
            [
                architecture,
                f"{values['gram_ratio_high_over_control']:.9f}",
                f"{values['high_beta_family_gain']:.9f}",
                f"{values['high_beta_family_cosine']:.9f}",
                f"{values['high_beta_fvu']:.9f}",
            ]
        )

    document = f"""# Empirical Verification Dossier

## Causal-ontology inversion in overcomplete sparse autoencoders

**Purpose:** This is a single-file evidence handoff for independent review of
the empirical claims in *Causal-Ontology Inversion in Overcomplete Sparse
Autoencoders*. It is optimized for machine review by Claude or another
scientific auditor: preregistered and exploratory results are separated, raw
seed-level records are included verbatim, frozen source is included verbatim,
and every binary checkpoint is represented by its filename, byte count, and
SHA-256 digest.

**Experiment date:** 2026-07-25  
**Status:** confirmatory experiment complete; 120/120 registered SAEs retained  
**Scope:** real digit images and learned MLP hidden activations with two
synthetic, exactly intervenable activation factors; not transformer
activations or natural semantic concepts.

## 1. Suggested audit sequence

1. Read Appendix A to check that the predictions, gates, estimands, seeds, and
   analysis hashes were fixed before the confirmatory runs according to the
   retained preregistration.
2. Inspect Appendices M–O for the locked training, scoring, and gradient-check
   source. Their hashes match those recorded in Appendix A.
3. Recalculate condition means and paired contrasts from Appendix H, treating
   the SAE seed—not factor or image—as the independent unit.
4. Reproduce the 20,000-replicate paired-seed percentile intervals using the
   algorithm and seed in Appendix N.
5. Compare the result with the registered decision rules in Appendix A and
   the unedited registered report in Appendix B.
6. Treat Appendices G, I–K, and P as exploratory only. They were produced
   after the registered verdict.
7. Use Appendix L to authenticate the 120 binary checkpoints if the separate
   reproducibility package is available.

## 2. What this one document permits—and does not

This document is sufficient to:

- inspect the complete preregistration and all analysis code;
- recompute every reported condition mean, paired high-minus-control
  difference, seed sign count, and bootstrap confidence interval;
- inspect all 120 registered run records and all 120 exploratory robustness
  records;
- check the registered decision logic for spin or post-hoc reinterpretation;
- authenticate a separately received checkpoint archive using 120 SHA-256
  digests.

The compressed NumPy checkpoints total several megabytes and are not base64
embedded because that would make the document impractical for model review.
Therefore this document alone cannot independently replay decoder-level
metrics from model parameters. The supplied audit below did perform that
replay locally. A third party can repeat it after obtaining the separately
packaged checkpoint archive whose digest appears in Section 10.

The retained preregistration says it was locked before confirmatory training,
and its embedded code hashes match the actual files. These local files alone
do **not** provide an independent trusted timestamp or public-commit proof of
the temporal claim. An external reviewer should request the relevant commit,
message, or archival timestamp if strict proof of preregistration timing is
required.

## 3. Artifact-consistency audit performed for this dossier

The dossier generator rebuilt the dataset and replayed all saved checkpoints
through the frozen evaluator. It separately reimplemented the aggregation and
bootstrap calculations over the resulting raw table. It stopped on any
mismatch larger than the stated numerical tolerances. Appendix Q contains the
complete audit and dossier-generation source.

| check | result |
|---|---|
| Reconstructed data SHA-256 | `{audit['dataset_sha256']}` |
| Classifier held-out accuracy | {audit['classifier_eval_accuracy']:.12f} |
| Registered rows / unique cells | {audit['run_rows']} / {audit['unique_run_cells']} |
| Checkpoints / manifest failures | {audit['checkpoint_count']} / {audit['checkpoint_manifest_failures']} |
| Maximum decoder-column norm error | {audit['maximum_decoder_norm_error']:.3e} |
| Maximum saved-metric replay error | {audit['maximum_checkpoint_metric_error']:.3e} |
| Maximum saved factor-array replay error | {audit['maximum_saved_factor_array_error']:.3e} |
| Maximum condition-mean recomputation error | {audit['maximum_condition_mean_error']:.3e} |
| Maximum paired-mean recomputation error | {audit['maximum_paired_mean_error']:.3e} |
| Bootstrap intervals recomputed | {audit['bootstrap_intervals_recomputed']} |
| Maximum bootstrap-endpoint error | {audit['maximum_bootstrap_endpoint_error']:.3e} |
| Maximum TopK deviation from L0=16 | {audit['topk_maximum_l0_deviation']:.9f} |

### Gradient and causal-construction checker

```text
{audit['gradient_check_output']}
```

## 4. Registered gates recomputed from raw records

The manipulation gate requires Gram ratio ≤0.80. At β=0.5, the retention gate
requires mean family gain ≥0.75, family cosine ≥0.95, and FVU ≤0.10.

{markdown_table(
    [
        'architecture',
        'Gram ratio',
        'family gain',
        'family cosine',
        'FVU',
    ],
    gate_rows,
)}

The TopK matched-sparsity gate also passes: every TopK run lies within 0.05 of
L0=16; the maximum observed deviation is
{audit['topk_maximum_l0_deviation']:.9f}.

## 5. Registered verdict and its evidential limits

The primary registered result is supported in both architectures:

- L1 high-minus-control one-atom alignment:
  −0.255285, 95% CI [−0.312468, −0.205723], 12/12 seeds negative.
- TopK high-minus-control one-atom alignment:
  −0.409225, 95% CI [−0.497346, −0.327031], 12/12 seeds negative.

Activation-aware multiplicity increased in both architectures. Causal
concentration decreased decisively only in TopK; the L1 interval crossed zero.
The result therefore supports a narrow statement: under this full
squared-Gram objective and strong registered penalty, a known causal generator
became less aligned with any one positive decoder ray while remaining
recoverable through the decoder family.

It does not establish that causal information vanished, that all
orthogonality penalties behave this way, that natural concepts behave this
way, or that the effect occurs in transformer SAEs.

## 6. Per-seed registered high-minus-control evidence

All deltas are β=0.5 minus β=0.0. Family quantities are the high-β levels.

{paired_seed_table()}

## 7. Load-bearing alternative-cost diagnostics

- L1 held-out L0 increased from 15.7147 to 30.2113. The fixed lambda therefore
  did not preserve sparsity, although the matched-sparsity TopK result prevents
  L0 drift from being the sole explanation.
- TopK dead fraction increased from 0.0331 to 0.1814.
- FVU rose by 0.0060 in L1 and 0.0639 in TopK.
- High-β family gain was 0.7919 in L1 and 0.8479 in TopK, so the family
  survived but did not retain unit gain.
- Maximum absolute coherence did not fall. Post-hoc analysis found
  near-antipodal duplicates: minimizing the full Gram sum is a frame-potential
  objective and can approach a signed duplicated tight frame with
  maximum absolute coherence one.
- The dose response is non-monotone. Low or middle beta sometimes improved
  alignment; only β=0.5 versus β=0 was registered as confirmatory.
- The same held-out dataset is shared across all seeds. The 12 experimental
  units measure optimization/init variability, not independent dataset
  replications.
- Training-last-batch diagnostics in Appendix H were recorded immediately
  before the final parameter update, while held-out metrics and saved weights
  use the final parameters. Registered conclusions depend on held-out metrics,
  not those training diagnostics.

## 8. Reproduction commands

Run from the repository root in the package-pinned environment:

```bash
python3 experiments/coherence_transfer_semireal.py \\
  --architectures l1,topk \\
  --seeds 0,1,2,3,4,5,6,7,8,9,10,11 \\
  --betas 0,0.025,0.0625,0.25,0.5 \\
  --widths 68 \\
  --outdir results/coherence_transfer_semireal_reproduction \\
  --save-weights

python3 analysis/check_coherence_transfer_gradients.py
python3 analysis/analyze_coherence_transfer_semireal.py \\
  results/coherence_transfer_semireal_reproduction
python3 analysis/posthoc_coherence_transfer_robustness.py \\
  results/coherence_transfer_semireal_reproduction
```

The original run took {json.loads((RESULT_DIR / 'metadata.json').read_text())['wall_seconds']:.3f}
seconds in the recorded CPU environment. Runtime and per-run wall-clock columns
are not expected to reproduce exactly.

## 9. Claim-to-artifact map

| claim or check | authoritative evidence in this document |
|---|---|
| Design fixed before seeds 0–11 | Appendix A, with timing caveat in Section 2 |
| Training and estimand definitions | Appendices A and M |
| Exact run coverage and environment | Appendices D and H |
| Primary and secondary registered outcomes | Appendices B, E, F, and H |
| Seed pairing and bootstrap CIs | Appendices H and N |
| Family-retention and sparsity gates | Appendices B, C, D, F, and H |
| Gradient correctness | Section 3 and Appendix O |
| Checkpoint-to-metric replay | Section 3 and Appendix Q |
| Random-direction specificity | Appendices G, I–K, and P; exploratory |
| Threshold sensitivity | Appendices G, I–K, and P; exploratory |
| Antipodal/tight-frame diagnosis | Appendices G, I–K, and P; exploratory |
| Checkpoint authenticity | Appendix L |

## 10. Integrity manifest

{file_manifest_table(integrity_files)}

The dossier itself cannot contain its own non-circular digest. Compute
`sha256sum EMPIRICAL_VERIFICATION_DOSSIER.md` after receipt.

---

# Appendix A — retained preregistration

{fenced_file(PREREG_PATH, 'markdown')}

# Appendix B — registered analysis report

{fenced_file(RESULT_DIR / 'REGISTERED_ANALYSIS.md', 'markdown')}

# Appendix C — condition means

{fenced_file(RESULT_DIR / 'condition_means.csv', 'csv')}

# Appendix D — run metadata and environment

{fenced_file(RESULT_DIR / 'metadata.json', 'json')}

# Appendix E — registered paired contrasts

{fenced_file(RESULT_DIR / 'paired_contrasts.csv', 'csv')}

# Appendix F — registered structured analysis summary

{fenced_file(RESULT_DIR / 'analysis_summary.json', 'json')}

# Appendix G — post-hoc robustness report (exploratory)

{fenced_file(RESULT_DIR / 'POSTHOC_ROBUSTNESS.md', 'markdown')}

# Appendix H — complete registered run table (120 rows)

{fenced_file(RESULT_DIR / 'run_metrics.csv', 'csv')}

# Appendix I — post-hoc condition means (exploratory)

{fenced_file(
    RESULT_DIR / 'posthoc_robustness_condition_means.csv',
    'csv',
)}

# Appendix J — post-hoc structured summary (exploratory)

{fenced_file(RESULT_DIR / 'posthoc_robustness_summary.json', 'json')}

# Appendix K — complete post-hoc per-run metrics (120 rows; exploratory)

{fenced_file(RESULT_DIR / 'posthoc_robustness_metrics.csv', 'csv')}

# Appendix L — checkpoint SHA-256 manifest (120 checkpoints)

{fenced_file(RESULT_DIR / 'weights_sha256.csv', 'csv')}

# Appendix M — frozen training and scoring source

{fenced_file(TRAINING_PATH, 'python')}

# Appendix N — frozen registered-analysis source

{fenced_file(ANALYSIS_PATH, 'python')}

# Appendix O — frozen gradient and causal-construction checker

{fenced_file(GRADIENT_PATH, 'python')}

# Appendix P — post-hoc robustness source (exploratory)

{fenced_file(POSTHOC_PATH, 'python')}

# Appendix Q — artifact audit and dossier-generation source

{fenced_file(Path(__file__).resolve(), 'python')}
"""
    return document


def main() -> None:
    audit = audit_artifacts()
    OUTPUT_PATH.write_text(build_dossier(audit), encoding="utf-8")
    print(f"wrote {OUTPUT_PATH}")
    print(f"bytes={OUTPUT_PATH.stat().st_size}")
    print(f"sha256={sha256_file(OUTPUT_PATH)}")


if __name__ == "__main__":
    main()
````
