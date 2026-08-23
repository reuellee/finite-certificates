# finite-certificates

Small, explicit, machine-checkable research results. Search may be heuristic;
claims must be exact. The public tree is organized around conclusions, compact
certificates, and independent replay—not model transcripts or lab-notebook history.

Start with the [research index](docs/RESEARCH_INDEX.md) for claim-level entry points,
scope, and direct verification commands.

## Headline results

| Area | Certified conclusion | Proof entry point |
|---|---|---|
| Maxout polytopes | `max f₀(3,5) = 42`; the odd `n=5` tightness claim in Conjecture 6.6.1 is false | [`ai/maxout/README.md`](ai/maxout/README.md) |
| Uniform oriented matroids | All three mutation graphs are connected for every rank with `n <= 9`; the `UOM(4,9)` class count is 9,276,595 | [`ai/omgamma/README.md`](ai/omgamma/README.md) |
| `UOM(4,9)` realizability | Complete exact split: 9,072,815 realizable, 203,780 non-realizable, zero undecided | [`ai/omopen/FINAL_RESIDUE.md`](ai/omopen/FINAL_RESIDUE.md) |
| Nine-Diagonal Vanishing Lemma | **2/9 proved integrally**; diagonals 1 and 2 are closed, while 3–9 remain open | [`ai/omreal/README.md`](ai/omreal/README.md) |
| `(4,9)` non-realizability | Known `(4,8)` deletion obstructions do not generate the full non-realizable population; Proposition R lifts deletion certificates | [`ai/omminor/MINOR_THEORY.md`](ai/omminor/MINOR_THEORY.md) |
| Interpretability and optimizers | Exact minimal counterexamples and scope failures for SAE metrics, interpretability methods, coherence penalties, Muon, and Lion | [`docs/RESEARCH_INDEX.md`](docs/RESEARCH_INDEX.md) |
| Jacobian aftermath | Explicit consequences and degree boundaries following the 2026 counterexample | [`jacobian/README.md`](jacobian/README.md) |

## Current 9DVL frontier

The authoritative score is **2/9**. Diagonal 3 still lacks a coverage-certified
global master-closure complex. Its strongest current exact reduction leaves 5,803 of
17,824 row-2599 full-support residual factors unresolved globally and 28 difficult
algebraic sections in the first two four-support domains.

The bounded diagonal-9 pivot has certified a transverse two-wall disk and the complete
first projection frontier on a selected parent-860 triangle. Exact restriction leaves
1,553 open-triangle curves; pair projection produces 396,369 distinct primitive
resultants and 402,031 open horizontal roots counted per polynomial. The predeclared
growth stop fired before chamber lifting. The next target is deterministic sharded
root isolation, cross-polynomial deduplication, and common-coordinate validation.

No local slice or sampled chart is promoted to a global diagonal theorem. See the
[9DVL status ledger](ai/omreal/NINE_DIAGONAL_STATUS.md) and the machine-checked
[diagonal-9 decision ledger](ai/omreal/data/DIAG9_RESEARCH_DECISION_LEDGER.json).

## Verification

Requirements are Python 3 plus `numpy`, `scipy`, and `sympy`:

```bash
python3 -m pip install -r requirements.txt
python3 run_all.py --fast
python3 run_all.py
```

`run_all.py` discovers every `verify_*.py` script. CI partitions the selected suite
into a deterministic, independently audited four-shard cover. Some verifiers
regenerate committed artifacts, so a full replay may leave an informational diff.

Useful direct checks:

```bash
# Maxout capstone: independent standard-library audit
python3 ai/maxout/capstone/independent_audit.py

# Mutation-graph certificates
python3 ai/omgamma/verify_omgamma.py

# 9DVL status/frontier checks
python3 ai/omreal/verify_diag3_completion_open_object.py
python3 ai/omreal/verify_diag9_parent860_node_topology.py
python3 ai/omreal/verify_diag9_parent860_plane_projection.py
python3 ai/omreal/verify_diag9_research_decision_ledger.py

# Repository navigation and archive-policy check
python3 verify_repository_structure.py
```

## Repository map

| Path | Purpose |
|---|---|
| `ai/maxout/` | Exact discrete-geometry theorems and certificate libraries |
| `ai/omgamma/` | Uniform oriented-matroid mutation-graph connectivity |
| `ai/omopen/` | Exact resolution of the final `(4,9)` sweep residue |
| `ai/omminor/` | Minor obstructions and certificate-core experiments |
| `ai/omreal/` | Realizability topology, SEEAT, and the active 9DVL program |
| `ai/*` ML directories | Exact theory counterexamples plus one clearly labelled empirical replication |
| `jacobian/` | Exact downstream consequences of the Jacobian counterexample |
| `ops/` | Corpus and workflow support |
| `docs/` | Human-facing research and verification indexes |

Within a research area, `README.md` or the entry point named in the
[research index](docs/RESEARCH_INDEX.md) states the conclusion and scope;
`verify_*.py` files are independent replays; generator/search scripts are not evidence
unless their output is checked exactly.

## Evidence and archive policy

The trust boundary is the mathematical argument plus exact certificate replay.
Accepted review findings are distilled into the affected note, verifier, or a concise
adjudication beside the result. Raw model-review transcripts, tool logs, scratch
workspaces, and local recovery bundles are intentionally excluded from Git; history
and external recovery checkpoints preserve prior states without making them part of
the proof surface.

See [CONTRIBUTING.md](CONTRIBUTING.md) for exactness, independence, canary, scope, and
artifact-retention requirements.

Licensed under the [MIT License](LICENSE).
