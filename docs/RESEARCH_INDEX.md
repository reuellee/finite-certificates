# Research and verification index

This is the claim-level map of the repository. It distinguishes theorem or exact
finite-census results from empirical replications, active programs, and operational
notes. Follow the entry point before quoting a result; it records scope and remaining
obligations.

## Exact results

| Area | Conclusion and scope | Read first | Direct check |
|---|---|---|---|
| Maxout polytopes | `max f₀(3,5)=42`, certified by 132,560 cell-wide certificates; `(4,4)` and `(4,6)` resolved and `(3,8)` achievability certified | [`ai/maxout/README.md`](../ai/maxout/README.md) | `python3 ai/maxout/capstone/independent_audit.py` |
| Uniform-OM mutation graphs | Labelled, reorientation-class, and isomorphism-class mutation graphs are connected for every rank with `n <= 9`; `UOM(4,9)` has 9,276,595 classes | [`ai/omgamma/README.md`](../ai/omgamma/README.md) | `python3 ai/omgamma/verify_omgamma.py` |
| `UOM(4,9)` realizability split | 9,072,815 realizable, 203,780 non-realizable, zero undecided; the final 659-class residue is realizable | [`ai/omopen/FINAL_RESIDUE.md`](../ai/omopen/FINAL_RESIDUE.md) | Commands and external-artifact boundaries are in §5–§7 of that note |
| Nine-Diagonal Vanishing Lemma | Exactly diagonals 1 and 2 are proved integrally; the honest score is **2/9** | [`ai/omreal/README.md`](../ai/omreal/README.md) | `python3 ai/omreal/verify_diag3_completion_open_object.py` and the direct frontier checks below |
| SEEAT | Single-element extension atlas theorem; exact one-chart capacity 26,112; row-2599 width bounded `7 <= width <= 178` | [`ai/omreal/SEEAT.md`](../ai/omreal/SEEAT.md) | Use the verifier commands in that note |
| Minor obstruction study | Exact prefix and sample measurements show known `(4,8)` deletion obstructions explain about 91% of non-realizable `(4,9)` classes; Proposition R is exact. This is not a short classification theorem | [`ai/omminor/MINOR_THEORY.md`](../ai/omminor/MINOR_THEORY.md) | `python3 ai/omminor/verify_minimal.py` |
| SAE absorption metric | Exact non-identification and optimality counterexamples | [`ai/absorption-metric/README.md`](../ai/absorption-metric/README.md) | Three commands in its Verify section |
| SAE intervention grounding | Adaptive internal interventions do not identify a semantic causal ontology | [`ai/sae-grounding/README.md`](../ai/sae-grounding/README.md) | `python3 ai/sae-grounding/verify_intervention_grounding.py` |
| SAE conditional-rate identification | Exact finite certificates of conditional-rate unidentifiability | [`ai/sae-unidentifiability/README.md`](../ai/sae-unidentifiability/README.md) | `python3 ai/sae-unidentifiability/verify_unidentifiability.py` |
| Interpretability methods | Four explicit minimal networks where standard methods give a wrong answer | [`ai/interp-illusions/README.md`](../ai/interp-illusions/README.md) | Four commands in its Verify section |
| Coherence penalties | Exact frame showing remedy-induced feature distortion | [`ai/coherence-distortion/README.md`](../ai/coherence-distortion/README.md) | `python3 ai/coherence-distortion/verify_overcomplete_coherence.py` |
| Optimizers | Exact scope failures or counterexamples for Muon, Li–Hong, and Lion claims | [`ai/optimizer/README.md`](../ai/optimizer/README.md) | Two commands in its Verify section |
| Jacobian aftermath | Explicit witnesses and degree boundaries following the 2026 counterexample | [`jacobian/README.md`](../jacobian/README.md) | Six commands in its Verify section |

## Active 9DVL obligations

| Track | What is certified | What is still missing |
|---|---|---|
| Diagonal 3 | Exact triple-factor reductions, parent-safe source objects, global four-support projection, and 1,665 completed algebraic fibers | 28 hard sections, `v` lifting, global gluing, middle-rank replay, and coverage-certified parent-space closure |
| Diagonal 9 | Exact parent-860 transverse node and complete selected-plane projection frontier | Sharded root isolation, cross-resultant deduplication, common-coordinate validation, chamber lifting, infinity, labels, and all-parent coverage |

The canonical detailed ledger is
[`ai/omreal/NINE_DIAGONAL_STATUS.md`](../ai/omreal/NINE_DIAGONAL_STATUS.md).
The active diagonal-9 target and promotion gates are machine-readable in
[`ai/omreal/data/DIAG9_RESEARCH_DECISION_LEDGER.json`](../ai/omreal/data/DIAG9_RESEARCH_DECISION_LEDGER.json).

Direct diagonal-9 checks:

```bash
python3 ai/omreal/DIAG9_GRAPH_verify_parent860_node.py
python3 ai/omreal/verify_diag9_parent860_node_topology.py
python3 ai/omreal/verify_diag9_parent860_plane_projection.py
python3 ai/omreal/verify_diag9_research_decision_ledger.py
```

## Empirical result

[`ai/coherence-transfer/`](../ai/coherence-transfer/) is a third-party empirical SAE
result imported with independent recomputation and replication. It is deliberately
not presented as an exact finite theorem; its README lists the permanent
preregistration and reproducibility limitations.

## Operational and scoped material

These directories support target selection or experiments but are not headline proof
surfaces:

| Path | Role |
|---|---|
| [`ai/alphaevolve/`](../ai/alphaevolve/) | API experiments and campaign runbooks |
| [`ai/om410/SCOPING.md`](../ai/om410/SCOPING.md) | Registered scope for a beyond-enumeration study |
| [`ai/scouting/TARGETS_2026-07.md`](../ai/scouting/TARGETS_2026-07.md) | Historical target shortlist |
| [`ops/`](../ops/) | Corpus and workflow support |

## What is intentionally absent

Raw model-review transcripts, tool logs, scratch workspaces, and local recovery bundles
are not proof dependencies and are excluded from Git. Findings that matter are
distilled into the relevant result note, exact checker, or curated adjudication.
Previous raw transcripts remain recoverable from repository history and external
checkpoints.
