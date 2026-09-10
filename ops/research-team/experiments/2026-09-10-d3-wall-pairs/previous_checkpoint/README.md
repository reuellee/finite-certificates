# 9DVL witness selection: exact guess-and-check results

An actual-parent counterexample rules out a universal continuous normalized Gordan witness selector. A separate exact support6 repair and conditional local selection lemma survive. These are auxiliary results; original cohomological injectivity remains open and the ledger stays **2/9**.

Read [REPORT.md](REPORT.md), [the counterexample proof](falsifier/FINDINGS.md), [the constructive result](constructive/FINDINGS.md), and [the independent audit](referee/FINAL_REVIEW.md).

With Python 3.12, run:

```sh
python -B replay_checkpoint.py
```

The final replay uses the Python standard library and runs independently implemented checks in a clean temporary copy. It authenticates pinned source bytes and verifies whole-interval polynomial identities and sign bounds. Discovery and producer programs are preserved for provenance; they are not imported by the independent replay.

This snapshot contains the consulted input subset and current experiment, not full Git history. No original theorem statement, canonical ledger, or historical certificate is modified.
