# Zero-curvature exclusion and reduced maximum problem

Original ledger: **2/9**. The whole authenticated source remains open.
Read REPORT.md, PROOF.md and CLAIM_LEDGER.json before using the equations.

From this directory in a checkout of the research branch, run:

    python verify_zero_curvature.py
    python verify_reduction.py

Both use the predecessor source checker in the adjacent parent-localized
experiment folder and authenticate the frozen source. Python and SymPy suffice.
No numerical solver or network is required for acceptance. The second script
generates the discriminant equations, sparse six-variable coefficients,
source-specific Schur matrix circuit and exact replay report.

The complete Drive recovery snapshot additionally contains the original source
bytes, the unchanged predecessor ZIP, the known-saddle certificate, separate
Fraction checks, both numerical discovery scripts and all saved results.
For the snapshot, also run:

    python verify_independent.py

Verify the snapshot payload hashes before replay, since replay regenerates
JSON outputs. Numerical discovery requires optional NumPy/SciPy and supplies
no mathematical acceptance by itself. Independent mathematical peer review,
global maximum emptiness and source closure are not claimed.
