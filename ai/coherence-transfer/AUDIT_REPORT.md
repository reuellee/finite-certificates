# Independent audit — Empirical Verification Dossier
## "Causal-Ontology Inversion in Overcomplete Sparse Autoencoders" (semi-real digits experiment, 120 SAEs)

**Auditor:** independent scientific audit (Claude), 2026-07-25
**Inputs:** the dossier file only (`2d0588ef-EMPIRICAL_VERIFICATION_DOSSIER.md`, 4,900 lines) plus, optionally, the report PDF for a digest check.
**Method:** `audit_dossier.py` (this directory) — fully self-contained; extracts every artifact it needs from the dossier's fenced appendix blocks, recomputes all registered statistics from the raw 120-row run table, and re-runs the registered bootstrap and decision rules. Requires only python3 + numpy. Re-runnable by any third party with just the dossier + this script.
**Result: 88 checks — 87 PASS, 1 FAIL (a real but immaterial internal transcription discrepancy, detailed below). Script exits nonzero because a verifiable claim failed.**

Explicitly: nothing marked "verified" below relies on the dossier author's own
Section 3 / Appendix Q local checkpoint replay. That replay is treated as an
unverified claim throughout.

---

## 1. What was verified (from the dossier alone)

### 1.1 Hash / integrity checks — ALL PASS
- All 17 embedded appendix artifacts (A–Q) were extracted verbatim and their
  SHA-256 recomputed. 15 of 17 match the Section 10 integrity manifest
  **byte-exactly** (digest and byte count).
- The two apparent mismatches (Appendix H = `run_metrics.csv`, Appendix L =
  `weights_sha256.csv`) are **newline-translation artifacts, not content
  differences**: those two files were written by Python's `csv` module with
  CRLF line endings, and the dossier generator embedded them through
  `read_text()` which normalizes to LF. Restoring `\r\n` to the embedded text
  reproduces the recorded digests **exactly** (121 lines → 121-byte size
  difference, both files). Content-equivalent; verified, with this mechanism
  noted.
- Appendix A's three preregistration code hashes (training, analysis,
  gradient checker) match the SHA-256 of the sources embedded verbatim in
  Appendices M, N, O. So the frozen code shown *is* the code the prereg locked.
- Cross-links: `analysis_summary.json` (Appendix F) internally records the
  SHA-256 of the `run_metrics.csv` it analyzed and of `metadata.json`; both
  equal the Section 10 / Appendix H,D digests. The analysis provably ran on
  the same raw table reproduced in the dossier.
- The uploaded report PDF's SHA-256 matches the Section 10 manifest entry.

### 1.2 Recomputation from the raw 120-row table (Appendix H) — ALL PASS, essentially exact
- Coverage: exactly 120 rows, 120 unique (architecture, seed, beta) cells,
  full 2×12×5 grid, m=68 — the registered conformance gate.
- All 10 condition-mean rows × 14 fields recomputed: max abs error vs
  Appendix C = **1.8e-15** (float printing noise). Appendix B's 4-decimal
  table consistent.
- All 22 registered paired high-minus-control contrasts recomputed per seed:
  mean differences match Appendix E to **1.8e-15**; all 22 sign counts match;
  all 264 per-seed differences match Appendix F's `per_seed_difference`
  records; Appendix E ≡ Appendix F.
- Section 6's 24-row per-seed evidence table matches recomputation at its
  printed precision.
- Gates recomputed from raw rows: Gram ratio L1 0.541145 / TopK 0.534287
  (≤0.80 ✓), high-β family gain 0.791871 / 0.847875 (≥0.75 ✓), family cosine
  0.994763 / 0.984465 (≥0.95 ✓), FVU 0.038460 / 0.072033 (≤0.10 ✓), TopK max
  |L0−16| = 0.001389 (≤0.05 ✓). Identical to the Section 4 table.

### 1.3 Bootstrap reproduction — EXACT
The 20,000-replicate paired-seed percentile bootstrap was reimplemented
independently from Appendix N's algorithm: `np.random.default_rng(8675309 +
sum(ord(c) for c in architecture+field))`, `integers(0,12,(20000,12))`,
`np.quantile(..., [0.025, 0.975])`, seed-sorted difference vector.
- All 44 CI endpoints (22 contrasts) reproduced with max error **1.8e-15**
  — bit-level agreement despite numpy 1.24.2 here vs the recorded 2.3.5.
- The retention-gate family-gain bootstrap (salt `1000+sum(ord)`) also
  reproduced exactly.
- Headline: L1 ΔA = −0.255285, CI [−0.312468, −0.205723], 12/12 negative;
  TopK ΔA = −0.409197, CI [−0.497319, −0.326966], 12/12 negative.

### 1.4 Registered decision rules re-applied — verdicts supported
Applying Appendix A's rules to *my recomputed* numbers:
- **Gates:** conformance PASS, manipulation PASS, retention PASS, TopK
  fixed-L0 PASS → interpretable.
- **P1 (primary):** CI upper endpoint < 0 in **both** architectures →
  **SUPPORTED**. Appendix B's verdict sentence is byte-identical to the frozen
  template in the locked Appendix N code (no editorializing possible).
- **P2 (multiplicity):** split-count and participation-ratio CI lower bounds
  > 0 in both architectures → SUPPORTED IN BOTH — matches Appendix B.
- **P3 (concentration):** CI upper < 0 in TopK only; L1 CI crosses zero
  ([−0.0644, +0.0130]) → "SUPPORTED IN topk" — matches Appendix B exactly.
  The dossier/report do **not** overclaim P3.
- Report headline claims (as transcribed: L1 −0.255 [−0.312, −0.206], TopK
  −0.409 [−0.497, −0.327], 12/12 both, family gain 0.792/0.848, all gates
  pass) all match recomputation at 3-decimal precision.
- No-spin check: adverse diagnostics are disclosed and correct (L1 L0 drift
  15.71→30.21; TopK dead fraction 0.033→0.181; FVU up; **max absolute
  coherence did not fall** — recomputed positive in both architectures —
  and the frame-potential/antipodal-duplicate degeneracy is admitted).

### 1.5 Frozen training source audit (Appendix M) — read line-by-line
- **Pure NumPy** implementation (hand-rolled Adam, analytic gradients), with
  scipy only for NNLS and sklearn only for the digits dataset/MLP classifier.
  **No torch anywhere** in M/N/O/P/Q. A full retrain is CPU-feasible in
  principle, but **not on this box**: scipy and sklearn are not installed
  (numpy 1.24.2 only, no pip). ~8 min in the recorded environment.
- Matches the prereg: L1 and TopK(k=16) architectures; λ=0.2 constant across
  β; β grid {0, .025, .0625, .25, .5}; 10,000 steps, batch 256, Adam lr 0.002
  with 1/3 decay at step 5,000 and 1/10 at 8,000; decoder columns renormalized
  to unit norm after **every** update; full squared-Gram penalty implemented
  as 0.5‖GᵀG−I off-diag‖² with analytic gradient 2·D·offdiag (correct for
  C_Σ = Σ_{i<j}⟨d_i,d_j⟩²).
- **Identical init and minibatch streams across β**: `init_rng =
  default_rng(seed)`, `batch_rng = default_rng(1_000_000+seed)` — both depend
  only on the seed, so β is a clean intervention on an otherwise identical
  training trajectory. Verified in source.
- **No silent bug classes found**: no dead-latent resampling, no
  result-dependent run exclusion, no data leakage (train/eval split is
  stratified on base images before factorial expansion; pixel standardization,
  hidden-scale, and total-scale statistics are computed from the training
  split only; held-out rows never touch training). The training-last-batch
  diagnostics are recorded pre-final-update, exactly as Section 7 discloses.
  Pilot seeds 900–903 are outside the confirmatory seed range and the run
  command uses seeds 0–11 only.
- Gradient checker (Appendix O): the gram + L1 + TopK directional-derivative
  checks were **re-executed locally** in pure numpy (compiled from the
  embedded verbatim source). All relative errors < 7.1e-10, and the three
  analytic values printed in Section 3 (1.769786055550, 0.031650355040,
  0.150732934622) were reproduced **digit-for-digit**. (The dataset-dependent
  causal-construction check needs sklearn and could not be run here.)

### 1.6 Checkpoint manifest & local absence
- Appendix L: 120 well-formed, unique 64-hex SHA-256 digests whose filenames
  exactly cover the 120 registered (architecture, seed, beta) runs; archive
  digest for the reproduction package recorded in Section 10.
- A filesystem walk of `/home/reuellee_gmail_com` (and a check of `/tmp`)
  found **no** checkpoint `.npz` files, no `run_metrics.csv`, and no research
  package archive. **Decoder-level replay is therefore an open item**, exactly
  as the dossier itself states; this audit marks nothing verified on the
  basis of the author's own replay.

### 1.7 Exploratory-vs-registered consistency
- Post-hoc appendices (G, I, J, K, P) are labeled exploratory and their
  overlapping quantities (planted alignment, split counts, condition means)
  agree with the registered table to <1e-9; the exploratory headline means
  equal the registered ones (their CIs differ slightly only via different
  RNG salts, which is expected and disclosed).

---

## 2. Discrepancies found

1. **REAL (the one FAIL): Section 5's TopK headline digits are wrong at the
   6-decimal level.** §5 prints TopK ΔA = −0.409225, CI [−0.497346,
   −0.327031]; the registered Appendix E / B values and my exact
   recomputation give −0.409197, CI [−0.497319, −0.326966] (differences
   2.8e-5–6.5e-5). Root cause visible in Appendix Q: the §5 narrative numbers
   are **hard-coded literals in the dossier-generation template** (Q lines
   ~587–589), not derived from the data; the L1 literals are correct, the
   TopK literals evidently came from a stale/other run. Materiality: none —
   at the report's 3-decimal precision both versions round identically
   (−0.409, [−0.497, −0.327]), sign counts are unchanged, and the registered
   artifacts (B, E, F, H) are mutually consistent and authoritative. It does,
   however, show the dossier generator's prose is not fully derived from the
   audited data, which slightly weakens Section 3's "stopped on any mismatch"
   framing. Kept as FAIL.
2. **Cosmetic:** Appendix H and L embeddings are LF-normalized copies of
   CRLF-on-disk CSVs (hashes match only after restoring CRLF). Worth one
   sentence in a future dossier; not a content issue.
3. The report PDF's body text could not be machine-read here (subset-font
   encoding); its claims were checked against the transcription supplied to
   this audit, not extracted from the PDF. The PDF's digest does match §10.

## 3. Not verifiable from this dossier alone (open items)

- **Checkpoint replay:** the 120 binary checkpoints are absent (by design);
  metric-from-weights replay and the Appendix L digests cannot be exercised
  until the separately packaged archive (digest in §10) is obtained.
- **Temporal lock of the preregistration:** the hash lock proves the analyzed
  code equals the locked code, but nothing here proves *when* Appendix A was
  written relative to the confirmatory runs. No trusted timestamp or public
  commit exists in this file; the dossier concedes this. Request the commit /
  archival timestamp for strict prereg-timing proof.
- **Full retraining reproduction:** feasible on CPU with numpy+scipy+sklearn
  (~8 min recorded), but not in this environment (no scipy/sklearn, no pip).
- The dossier author's own §3 replay results (decoder-norm error, saved-metric
  replay error, etc.) — reported, plausible, **not relied upon here**.

## 4. Verdict

**The dossier supports the report's registered claims, without spin, to the
maximum extent checkable from this single file.** Every recomputable number —
condition means, all 22 paired contrasts, per-seed differences and sign
counts, all 44+4 bootstrap CI endpoints, all four gates, and the three
prediction verdicts under the preregistered decision rules — reproduces
exactly (≤2e-15) from the embedded raw records using the embedded frozen
code's algorithm. P1 SUPPORTED (both architectures), P2 SUPPORTED (both), P3
SUPPORTED in TopK only, and Appendix B words each verdict with the frozen
code's own templates, matching those recomputed outcomes. Adverse diagnostics
are disclosed rather than hidden. The single found discrepancy is a
hard-coded, stale 6th-decimal transcription in the §5 narrative that does not
touch any registered artifact or the verdicts. Remaining trust gaps are the
two the dossier itself names: checkpoint replay (archive not included) and
independent proof of preregistration timing.
