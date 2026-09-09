# Injectivity diagnostics and actual-parent CUDA pilot

**Original injectivity is open. The theorem ledger remains 2/9.** This
checkpoint publishes three independently reviewed, bounded results:

| Result | Accepted consequence |
|---|---|
| [Injectivity attack](reports/INJECTIVITY_ATTACK.md) | An auxiliary boundary lemma and an abstract countermodel; no original theorem proof |
| [Collision deletion](reports/COLLISION_DIAGNOSTIC.md) | Deletion kills the abstract kernel but creates singleton Hc2 of dimension8, violating a required hypothesis |
| [Actual-parent pilot](reports/PARENT_CUDA_PILOT.md) | 101 exact local three-row circuits;32 exactly checked parents and96 block labels;optional CUDA geometry backend |

The 4,096-candidate CPU run took about11.11seconds. Geometry accounts for
about1.4% and numerical LP/screening about92% of runtime. CUDA execution,
Windows execution, numerical CPU/GPU parity and GPU speedup remain untested.
The current geometry port alone offers little potential end-to-end speedup
on this particular workload.

## Exact replay

`EVIDENCE.zip` preserves every required relative source/code/result path,
including all16 resumable numerical chunks. `EVIDENCE_MANIFEST.json` binds
every member and the readable review copies. It is an evidence snapshot,
not a full Git-history backup. The source is pinned to PR49
`59fec66666518257c585194b81061f60d91f439d`; this publication is additive to main.

With Python3.12:

```sh
python -B replay_checkpoint.py
```

This authenticates the archive and runs all three independent mathematical
replays in a temporary directory using the Python standard library. The
dedicated GitHub workflow runs this entrypoint. The repository's existing
verifier census and checks are unchanged. Read the three [reviews](reviews/)
for scope and nonconsequences; the source copies in `code/` are for review.

## Run the search on a laptop

Extract the complete working tree and install CPU search dependencies in
your chosen Python environment:

```sh
python -m zipfile -e EVIDENCE.zip evidence
python -m pip install numpy==2.3.5 scipy==1.17.0
cd evidence/parent_pilot
python engineer/pilot.py --out engineer/laptop_cpu --control engineer/controls/WITNESS.json --control engineer/controls/NEAR_SINGULAR_CANARY.json
```

After installing a CuPy package appropriate for your CUDA/driver setup using
the [official installation instructions](https://docs.cupy.dev/en/stable/install.html),
run the same input with a separate output directory:

```sh
python engineer/pilot.py --backend cuda --out engineer/laptop_cuda --control engineer/controls/WITNESS.json --control engineer/controls/NEAR_SINGULAR_CANARY.json
```

Add `--resume` to the identical command to reuse completed chunks. A CUDA
request fails explicitly if no usable device is available. Exact acceptance
stays on CPU. Do not use the CPU checkpoint as a CUDA resume checkpoint.
See [the engineering instructions](LAPTOP_RUN.md) for limits and conventions.
