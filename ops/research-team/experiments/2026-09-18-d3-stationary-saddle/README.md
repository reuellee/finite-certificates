# Certified admissible stationary saddle

Original ledger: 2/9. Source (5563,4373,23221) remains open.
Read REPORT.md and PROOF.md. The proposed fully parent-localized stationary
emptiness target is refuted, not the original 9DVL statement.

From a checkout of this research branch, run:

    python ops/research-team/experiments/2026-09-18-d3-stationary-saddle/verify_stationary.py

Only Python and SymPy are required. This reuses the pinned predecessor source
reconstruction and authenticates the source hash. The rational center is embedded.
A rational preconditioner is constructed from the exact center Jacobian, then
all acceptance uses rational interval arithmetic. No root finder or network is
used for acceptance. The generated witness and replay JSON are outputs.

The Drive recovery archive also retains the 192-start numerical discovery,
stored certificate, separate Fraction center checks, negative controls, quadratic
representation, source-wide proof checks, and unchanged predecessor snapshot.
Independent mathematical peer review and source-component closure are not claimed.
