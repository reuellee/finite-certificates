# finite-certificates

Explicit, machine-checkable mathematical research: numerical search may suggest a result, but the supporting claim must have an exact certificate and an honest statement of its scope. The repository contains work in discrete geometry, oriented matroids and realizability, and mathematical counterexamples in machine learning.

## Start here

- **Browse the results:** [results index](#results-index).
- **Check a certificate:** [verification instructions](#verification) and the README in the relevant project directory.
- **Follow 9DVL:** [the theorem prospectus](ai/omreal/9DVL_THEOREM_PROSPECTUS.md), [canonical status](ai/omreal/NINE_DIAGONAL_STATUS_V7.md), and the [latest bounded D9 path-bank checkpoint](research/d9_path_bank_20261125/README.md).
- **Explore the detailed research record:** [previous front-page research history](README_RESEARCH_HISTORY.md) and [`reviews/`](reviews/).

## Selected results and research

### Maxout polytopes

The exact maximum number of vertices of a three-dimensional zonoboxtope with five generators is **42**. The result is backed by 132,560 exact cell-wide upper-bound certificates and an independent audit. See [`ai/maxout/`](ai/maxout/) and its [paper](ai/maxout/paper/).

### Oriented-matroid mutation graphs

Mutation graphs of uniform oriented matroids are connected at every rank for `n <= 9`. The computation also corrects the number of uniform rank-4 classes on nine elements to **9,276,595**. See [`ai/omgamma/`](ai/omgamma/) and its [paper](ai/omgamma/paper/).

### Nine-Diagonal Vanishing Lemma (9DVL)

**Status: 2 of 9 diagonals proved; diagonals 3–9 remain open.** The first two are proved integrally. Local computations and examples do not, by themselves, establish a global diagonal.

The latest [D9 path-bank checkpoint](research/d9_path_bank_20261125/README.md) concerns two realizations of one parent, row 2599. An exact five-signature path and a finite-bank obstruction were independently replayed; neither proves D9. The checkpoint includes portable source data, certificates and replay commands. The canonical V10 strategy snapshot remains `STOP / NONE`; this informational result does not promote the theorem ledger or replace that snapshot.

The machine-checkable canonical [V10 state](ai/omreal/data/CANONICAL_RESEARCH_STATE_V10.json) has a dedicated [V10 verifier](ai/omreal/verify_canonical_research_state_v10.py). The earlier [V9 state](ai/omreal/data/CANONICAL_RESEARCH_STATE_V9.json), [V9 verifier](ai/omreal/verify_canonical_research_state_v9.py), and [V6 status](ai/omreal/NINE_DIAGONAL_STATUS_V6.md) remain historical checkpoints.

The diagonal-three work has exact local and finite certificates, but global coverage and the remaining homological obligations are open. See the [canonical status](ai/omreal/NINE_DIAGONAL_STATUS_V7.md) and [the detailed historical record](README_RESEARCH_HISTORY.md).

### Non-realizability and other work

The repository studies non-realizable oriented matroids, including the limits of short obstruction lists and Proposition R; see [`ai/omminor/`](ai/omminor/). It also contains exact counterexamples and scope analyses in interpretability, sparse autoencoders, and optimizers.

## Verification

The complete suite requires Python 3, NumPy, SciPy and SymPy; see [`requirements.txt`](requirements.txt). Many individual checks require less.

```bash
python3 run_all.py --fast
python3 run_all.py
python3 run_all.py --list-shards 4
python3 run_all.py --ci-delegated --shard 0/4
```

The suite discovers `verify_*.py` files. Some checks regenerate committed artifacts and can leave an informational working-tree diff. Instructions for the separately scoped D9 path-bank audit are in its [checkpoint README](research/d9_path_bank_20261125/README.md).

## Results index

| Area | Result or status | Location |
|---|---|---|
| Maxout polytopes | `max f₀(3,5) = 42`; additional cases and certificates | [`ai/maxout/`](ai/maxout/) |
| OM mutation graphs | Connected for uniform oriented matroids with `n <= 9` | [`ai/omgamma/`](ai/omgamma/) |
| OM non-realizability | Minor obstructions, minimal examples and Proposition R | [`ai/omminor/`](ai/omminor/) |
| 9DVL / realizability | **2/9 proved**; global remaining obligations open | [`ai/omreal/`](ai/omreal/) |
| SEEAT | Single-element extension atlas and row-2599 capacity bounds | [`SEEAT.md`](ai/omreal/SEEAT.md) |
| Mathematical prospecting | Exact diagnostics of a proposed route-transfer principle | [`ai/scouting/`](ai/scouting/) |
| SAE absorption | Exact failures of feature-absorption identification | [`ai/absorption-metric/`](ai/absorption-metric/) |
| SAE identifiability | Conditional-rate and semantic-grounding non-identifiability | [`ai/sae-unidentifiability/`](ai/sae-unidentifiability/), [`ai/sae-grounding/`](ai/sae-grounding/) |
| Interpretability | Exact minimal networks where common methods mislead | [`ai/interp-illusions/`](ai/interp-illusions/) |
| Optimizers | Counterexamples and scope limitations | [`ai/optimizer/`](ai/optimizer/) |
| Jacobian aftermath | Exact consequences and minimal-degree results | [`jacobian/`](jacobian/) |

## Certificate philosophy

Numerical search can locate candidates; proof-bearing claims should be replayed exactly. The project records unresolved cases, separates producers from independent verifiers where practical, and preserves failed approaches when they clarify the frontier. [`ai/coherence-transfer/`](ai/coherence-transfer/) is a deliberately empirical, labeled exception.

Contributions and refutations are welcome; see [`CONTRIBUTING.md`](CONTRIBUTING.md). Licensed under the [MIT License](LICENSE).
