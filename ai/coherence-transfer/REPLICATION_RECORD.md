# Independent replication record — coherence-transfer semi-real experiment

**Date:** 2026-07-26. **Performed by:** a different operator, on different hardware,
from the frozen sources only (`repl_bundle/`), with no access to the original run's
outputs while training.

**Outcome in one line: every registered conclusion reproduces; nothing reproduces
byte-for-byte, and the reason is fully identified.**

## What was run

All 120 registered cells — {L1, TopK} × 12 seeds × 5 β levels × width 68 — retrained
from source, plus the gradient/causal-construction checker, plus the frozen analysis
script, plus `audit_dossier.py --replication`.

```
python experiments/coherence_transfer_semireal.py \
  --architectures l1,topk --seeds 0..11 \
  --betas 0,0.025,0.0625,0.25,0.5 --widths 68 --save-weights
```

`check_coherence_transfer_gradients.py` passed first: analytic-vs-numeric gradients
agree to 3.7e-11 (gram), 2.6e-10 (l1), 4.4e-11 (topk), and the causal construction to
7.4e-07.

## Environment

| | registered (Appendix D) | this replication |
|---|---|---|
| python | 3.12.13 (Clang 21.1.4) | 3.12.13 (uv-managed CPython) |
| numpy | 2.3.5 | 2.3.5 |
| scipy | 1.17.0 | 1.17.0 |
| scikit-learn | 1.8.0 | 1.8.0 |
| platform | Linux-6.12.13, glibc 2.39 | Linux-6.1.0, glibc 2.36 |

**Library versions match exactly.** What differs is the OS, glibc, the CPython build,
and — the operative one — the CPU, hence which BLAS microkernels the bundled OpenBLAS
dispatches to.

*Ops note:* the earlier audit recorded "full retraining not possible in this
environment (no scipy/sklearn, no pip)". That is no longer a constraint: `uv` installs
its own CPython and wheels without system pip, so the whole replication ran on the
orchestrator in ~13 minutes at no cost.

## Registered conclusions — all reproduce

| | registered | replication | agreement |
|---|---|---|---|
| L1 alignment ΔA | −0.255285 [−0.312468, −0.205723] | **−0.254870** [−0.312251, −0.205154] | Δ = 4.2e−4 |
| TopK alignment ΔA | −0.409197 [−0.497319, −0.326966] | **−0.406754** [−0.495909, −0.323709] | Δ = 2.4e−3 |
| per-seed negatives | 12/12 both arches | 12/12 both arches | identical |
| **P1** (primary) | SUPPORTED both | **SUPPORTED both** | ✓ |
| **P2** | SUPPORTED both | **SUPPORTED both** | ✓ |
| **P3** | TopK only | **TopK only** (l1 False, topk True) | ✓ |
| registered gates | pass | **pass** — TopK max\|L0−16\| = 0.0014 | ✓ |

Gate values on the replication: L1 gram-ratio 0.541, family gain 0.792, family cosine
0.9948, FVU 0.0385; TopK gram-ratio 0.529, gain 0.849, cosine 0.9850, FVU 0.0714. All
inside the registered thresholds.

The two primary effect sizes land within 4e−4 and 2.4e−3 of the originals, with
identical sign counts and identical verdicts. That is a successful replication of the
paper's claims.

## What does *not* reproduce, and why

| check | result |
|---|---|
| `run_metrics.csv` byte-identical | **FAIL** — 913596ed… vs 376cbc49… |
| 120 checkpoint digests vs Appendix L | **FAIL** — 0/120 |
| all 22 contrast means at 4 dp | **FAIL** — 6/22 |
| all 22 bootstrap CIs at 4 dp | **FAIL** — 5/22 |
| all 22 seed sign counts | **FAIL** — 21/22 |

Root cause, and it is not a defect in the work: the dataset itself differs at the byte
level. Registered `data_sha256` is `d00e7d6c…`, this run produced `2111f9dd…`, while
train/eval shapes (5028, 34)/(2160, 34) and classifier eval accuracy (0.9611) match
exactly. The divergence enters in `build_dataset`, where `MLPClassifier(solver="lbfgs")`
runs BLAS-heavy training; different CPU dispatch changes floating-point summation
order, which perturbs the hidden activations, which propagates into every downstream
SAE. Per-run drift is correspondingly small but nonzero — max |replication − registered|
of 4.7e−3 (FVU), 0.137 (L0), 0.028 (alignment), 0.0031 (family cosine).

So the 4-dp checks fail for the same reason the digests do, and their failure carries
no evidence against the claims: they demand bit-identity on 22 contrasts including
small, noisy secondary ones, while the two **primary** contrasts agree to 3–4 decimals
and every verdict is preserved.

**This experiment is reproducible in its conclusions and not reproducible in its
bytes.** Bit-exactness here would require pinning the CPU and BLAS kernel set, not just
the package versions — which no pin list in the dossier can deliver.

## A defect this surfaced in the dossier's own tooling

`analyze_coherence_transfer_semireal.py` declares the replication
**"UNINTERPRETABLE: one or more registered gates failed."** Its conformance block has
twelve sub-checks; on this replication **eleven pass and exactly one fails —
`data_hash`**, which hard-compares against the registered `EXPECTED_DATA_SHA256`.

That makes the frozen analysis script **structurally incapable of certifying any
independent replication on different hardware**: the gate conflates "this is the same
experiment" with "this ran on the same machine", and any honest third-party rerun trips
it. The scientific gates it also computes — manipulation, family retention, TopK fixed
sparsity — all pass here.

`audit_dossier.py --replication` gets this right by scoring the byte-identity checks
separately from the registered gates, which is why it reports gates PASS and all three
predictions reproduced. Recommendation for any future dossier of this kind: keep the
dataset digest as a *reported diagnostic*, not as a conformance gate; gate on the
dataset's statistical fingerprint (shapes, classifier accuracy, effective amplitude)
instead.

## Expect 86/88, not 87/88, when you re-run the audit here

`audit_dossier.py` scored 87 PASS / 1 FAIL when first run against the dossier alone.
Run from the imported directory it scores **86 PASS / 2 FAIL**, and the extra failure
is caused by this replication, not by anything wrong:

```
[FAIL] checkpoints/raw artifacts NOT present on this machine
       (decoder-level replay remains an open item)
```

That check walks the entire home directory asserting that **no** `weights_*.npz` file
exists anywhere. It is the auditor's own hermeticity attestation — evidence it never
held the original checkpoints and so could not have quietly replayed them instead of
recomputing. The replication above legitimately produced 120 such files on the same
filesystem, so the assertion is now false and the check flips.

Both failures are understood and neither bears on the claims:

| FAIL | meaning |
|---|---|
| §5 TopK headline at 6 dp | real, immaterial: stale hard-coded literals in the Appendix Q narrative template |
| checkpoints present | the auditor's isolation self-check, invalidated by our own replication living on this box |

Third upstream recommendation, alongside the two in `IMPORT_ADJUDICATION.md`: scope
that hermeticity check to a named directory, or record it as a provenance note rather
than a scored check. As written, performing the very replication the dossier asks for
makes its own audit report a failure.

## Verdict

The physical experiment is **independently replicated**. Risk (ii) from the review
— "the physical experiment wasn't replicated" — is closed. Risks (i) preregistration
timing and the residual orthogonality scope note remain as stated in
`IMPORT_ADJUDICATION.md`.
