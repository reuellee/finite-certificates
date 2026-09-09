# Actual-parent numerical search and exact acceptance pilot

This is a bounded engineering experiment on the actual row 2599 parent geometry.
It provides finite pointwise certificates, not a global cover or an injectivity
proof. The original theorem ledger remains **2/9**, with zero obligations closed.

The CPU run used 4096 candidate identifiers representing 3992 distinct literal
parent matrices: three inherited event controls, all 178 original source charts,
3913 deterministic rational single-coordinate perturbations, and two controls
from the concurrent structural track. Repeated perturbations are counted, not
silently deduplicated. The preliminary 181-candidate calibration is a subset of
this domain; its eight exact parents are retained in the final selection, so the
engineering track exact-checks at most 32 distinct parents.

Numerical screening retained 2856 candidates and rejected 1240 by floating-point
parent-bracket signs. These are screening counts, not 1240 exact inadmissibility
certificates. All 70 parent signs and all 56 raw derived normals were recomputed
exactly for the 32 selected parents. Their 96 block labels have accepted rational
primal or Gordan certificates, with zero UNKNOWN. The observed exact patterns are
BBB,GBB,BBG,BGB,BGG,GBG, where G is strict feasibility and B is infeasibility.
Missing patterns are not excluded by this finite sample.

## Measured cost and CUDA scope

The initial run took 11.113 seconds internally and peaked at 82.977 MiB RSS:

| Stage | Seconds |
|---|---:|
| Batched70 determinants and56 normals, including upload if applicable |0.157|
| Numerical linear programs and parent screening |10.194|
| Exact checks for32 parents and96 block labels |0.444|

Timings are a single CPU run, not a laptop comparison or a speedup benchmark.
The NumPy geometry stage contributed about 1.4% of total runtime. Even eliminating
its cost entirely would only save about0.16 seconds in this run. The present
CuPy path accelerates that stage only. It includes explicit stream synchronization
before and after geometry and transfer timing. The SciPy LP proposal stage and
exact rational acceptance remain on CPU. CUDA was not executed here: CuPy/device
unavailability returns exit 2 with a clear error and never silently falls back.

Porting thousands of tiny LPs to GPU would be additional engineering work; the
current profile does not justify that work for this eleven-second pilot.

## Reproduce and resume

Requires Python 3.10+ plus NumPy and SciPy. The measured versions are recorded in
run/RUN_REPORT.json. The CLI accommodates native Windows with portable paths and
optional POSIX RSS measurement; Windows execution was not tested. Python 3.12,
NumPy 2.3.5 and SciPy 1.17.0 were used here. From the directory above engineer:

```sh
python engineer/pilot.py --out engineer/new_run --control engineer/controls/WITNESS.json --control engineer/controls/NEAR_SINGULAR_CANARY.json
python engineer/pilot.py --out engineer/new_run --control engineer/controls/WITNESS.json --control engineer/controls/NEAR_SINGULAR_CANARY.json --resume
```

For a machine with a compatible CuPy installation and exposed CUDA device,
replace the output directory with a fresh one and add `--backend cuda`. The
script does not install dependencies or select a CUDA package automatically.
The same rational candidate generator is used with either numerical backend;
rounding can change numerical proposals or which non-control candidates get
selected, but cannot bypass exact acceptance. No backend parity claim is made.

Defaults are 4096 total candidates, chunks of 256, exact selection limit 32, and
seed 20260909. Limits are enforced. Chunks have configuration and payload digests,
are written atomically, and resume only under identical source/code/configuration.
These hashes detect accidental modification, not an adversary rewriting both
payload and hashes. Exact acceptance recomputes literal coordinates regardless.

`python engineer/qa.py` checks byte-identical exact output after complete chunk
resume, modified-chunk rejection, configuration mismatch, source mutation, and
no-device CUDA failure. It is a CPU/no-CUDA environment integration test, not a
portable test requiring a CUDA-equipped laptop to fail. The separate referee
checks mathematical acceptance without importing producer logic.

## Certificate conventions and provenance

The source is pinned to PR 49 head 59fec66666518257c585194b81061f60d91f439d. Four
source files are SHA256-bound in code. Chart 0 and all three original signatures
are checked for exact source identity before generation. Triples and four-bases
use colex order; all coordinates and row indices are zero-based.

For a triple, normal coordinate r is the raw rational minor obtained by deleting
parent row r, multiplied by(-1)^(r+3). Signature bit 1 keeps the sign; bit 0 negates.
Certificates use these signed raw rows. FLOW's old primitive-row-normalized
weights are never copied; only their support indices are reused as proposals.
Every emitted Gordan vector is reconstructed over rationals and checked against
the actual raw rows. Zero weights are omitted from the stored support.

A GOOD certificate contains a rational point with all 56 signed row-dot-products
strictly positive. A BAD certificate has distinct in-range support indices and
positive rational weights whose weighted raw-row sum is identically zero in all
four coordinates. Failed reconstruction yieldsUNKNOWN, regardless of numerical
solver status. The full parent passes only if all 70 exact bracket signs equal the
source signs. No small determinant or singular value is treated as exact zero.

Candidate IDs 0,1,2 are inherited left/event/right anchors, so their labels carry
no new discovery credit. IDs 4094 and 4095 are the current structural witness and
its near-singular canary, copied with SHA256 provenance in run/config.json.
Both receive full BGB labels in this experiment. The canary's specified three-row
dependence is false; another Gordan support can still certify its full block bad.
The exact label alone is not a claim that the canary's three-row support works.

The main artifacts are run/exact_candidates.json, run/RUN_REPORT.json and the
chunk files. INITIAL_RUN.log preserves initial timings; QA_REPORT.json records
the integration checks. The source inputs and structural proof checks live in
the surrounding checkpoint, not in this worker's acceptance code.
