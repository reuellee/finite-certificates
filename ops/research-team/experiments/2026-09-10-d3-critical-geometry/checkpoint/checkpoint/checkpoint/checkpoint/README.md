# D3 wall-pair research checkpoint

The original theorem ledger is **2/9**. Read REPORT.md for the accepted
8,902/9,476 stronger pair-wall vanishing theorem, explicit 574-orbit residue,
conditional route to D3, and the unresolved independent triple endpoint.

The principal proof is pair/FINDINGS.md. Its independent reviews are
referee/FINAL_REVIEW.md, referee/PAIR_THEOREM_AUDIT.md,
referee/RULED_QUADRIC_AUDIT.md, and falsifier/RULED_QUADRIC_AUDIT.md.
The independent triple review is falsifier/TRIPLE_AUDIT.md.

The 574 complete combinatorial representatives are in
coordinator/HARD_PAIR_RESIDUE.json; referee/HARD_ORBIT_REPLAY.json records
the independent exhaustive match. They are factor-pair orbits, not parent
components or original pair-map generators.

Run from this directory:

```sh
python3 -B replay_checkpoint.py
```

Python 3.12 and SymPy 1.14.0 were used. The pair geometry's finite arithmetic,
orbit checks, tangent model and rational hard point use the Python standard
library. The independently implemented triple algebra uses SymPy. The replay
authenticates CHECKPOINT_MANIFEST.json and runs the independent verifiers in
a fresh temporary copy, with a per-check timeout. It does not run discovery
scripts, load discovery pickle caches, or enumerate the unresolved triple
census. The written geometric arguments have separate deductive reviews.

SOURCE_MANIFEST.json pins all 21 consulted mathematical inputs to exact Git
blobs at 59fec66666518257c585194b81061f60d91f439d. previous_checkpoint/
retains the consulted witness-selection experiment published at
b2667461a6359f804090212f0f075cc1ec018048. Discovery scripts are retained
for provenance and are not independent acceptance code. Optional intermediate
pickle caches are omitted from the published snapshot.

The original injectivity map and triple-bad compact-support degree-zero
vanishing remain open. No original operational obligation or triple source
record was closed by this checkpoint. Do not promote a partial factor count
to 3/9.
