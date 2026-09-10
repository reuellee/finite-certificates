# Direct original-statement 9DVL proof checkpoint

Read REPORT.md for the result and its limits, and CLAIM_LEDGER.json for status.
The original ledger is 2/9.

The principal new conventional proof is pair/COMMON_WEAK_PRIMAL_VANISHING.md.
Read referee/FINAL_REVIEW.md for independent review and falsifier/FINDINGS.md
for the separate challenge. Exact example checks are in referee/.

From this directory, run:

```sh
python3 replay_checkpoint.py
```

The replay verifies the immutable snapshot and runs the new independent
computational checks in a temporary copy. It needs Python 3.12's standard
library. Producer exploration scripts may additionally need SymPy 1.14;
they are preserved for provenance and are not imported by the independent
verifiers. The conventional proof is reviewed deductively, not by this script.

checkpoint/ preserves the preceding authenticated checkpoint. inputs/ contains
the additional pinned source reads. The inherited factor counts do not change.
