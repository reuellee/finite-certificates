# Oriented-matroid realizability topology and 9DVL

This directory contains the active realizability/topology program and the proof ledger
for the Nine-Diagonal Vanishing Lemma (9DVL). The current theorem score is
**2/9**—diagonals 1 and 2 are proved integrally; every stronger claim remains open.

## Read in this order

1. [`NINE_DIAGONAL_STATUS.md`](NINE_DIAGONAL_STATUS.md) — authoritative mathematical
   statement, proof status, and exact remaining obligations.
2. [`data/DIAG9_RESEARCH_DECISION_LEDGER.json`](data/DIAG9_RESEARCH_DECISION_LEDGER.json)
   and [`data/DIAG3_RESEARCH_DECISION_LEDGER.json`](data/DIAG3_RESEARCH_DECISION_LEDGER.json)
   — machine-checked active targets, stop rules, and promotion gates.
3. [`RESEARCH_OPERATING_SYSTEM.md`](RESEARCH_OPERATING_SYSTEM.md) — evidence hierarchy,
   falsification loop, runtime isolation, and publication gates.
4. The proof note named by a ledger entry — its generator, compact artifact, and
   independent verifier form one review unit.

## Current conclusions

| Diagonal | Status | Evidence boundary |
|---:|---|---|
| 1 | **Proved integrally** | Contraction-height homotopy equivalence in [`NINE_DIAGONAL_STATUS.md`](NINE_DIAGONAL_STATUS.md) |
| 2 | **Proved integrally** | [`DIAG2_EXCHANGE_SATURATED_SUPPORT_DROP.md`](DIAG2_EXCHANGE_SATURATED_SUPPORT_DROP.md) plus [`SECOND_DIAGONAL_SINGLE_REGION_H7_AUDIT.md`](SECOND_DIAGONAL_SINGLE_REGION_H7_AUDIT.md) |
| 3 | Open | The global pair route has exact local/source/four-support objects, but no coverage-certified global master-closure complex; 5,803 full-support factors and 28 algebraic sections remain at the current frontiers |
| 4–8 | Open | Partial reductions only; see the status ledger |
| 9 | Open | Parent 860 has an exact transverse node and complete selected-plane projection frontier, but not a compactified labelled roadmap or all-parent coverage |

The score advances only when the required global coverage, infinity, labels,
connectivity/homology replay, and independent hostile checks are complete. Local
convexity, sampled charts, or a large percentage of classified factors do not count as
a diagonal proof.

## Active diagonal-9 checkpoint

The exact parent-860 node contains two transverse residual walls and four labelled
chambers. On the complete selected parent triangle, exact restriction leaves 1,553
open curves and 192 boundary-only curves. Bernstein exclusion reduces 1,205,128
possible open-curve pairs to 477,811 candidates; these yield 396,369 distinct
degree-at-most-four primitive resultants and 402,031 open horizontal roots counted per
primitive polynomial.

This triggered the predeclared projection-growth stop. The selected next target is 32
deterministic shards for exact root isolation, cross-polynomial deduplication, and
common-`i` validation before any chamber lifting:

- [`DIAG9_PARENT860_TRANSVERSE_NODE.md`](DIAG9_PARENT860_TRANSVERSE_NODE.md)
- [`DIAG9_PARENT860_PLANE_PROJECTION_FRONTIER.md`](DIAG9_PARENT860_PLANE_PROJECTION_FRONTIER.md)
- [`DIAG9_PARENT860_CEGIS_ROUTING.md`](DIAG9_PARENT860_CEGIS_ROUTING.md)

## Active diagonal-3 checkpoint

The coverage-certified nonrelative master-closure compiler remains the selected global
route. The most advanced bounded support computation covers the first two surviving
four-support parent domains through all open sectors and 1,665 of 1,693 algebraic
sections. Exactly 28 hard sections, `v` lifting, global gluing, and middle-rank replay
remain. Separately, 5,803 of 17,824 row-2599 full-support factors remain unresolved
globally. These are explicit proof obligations, not estimated completion percentages.

- [`DIAG3_DECISION_2026-08-22.md`](DIAG3_DECISION_2026-08-22.md)
- [`DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_GATE.md`](DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_GATE.md)
- [`DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_REGULAR_RESIDUAL_SECTION_LIFT.md`](DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_REGULAR_RESIDUAL_SECTION_LIFT.md)
- [`DIAG3_PAIR_SOURCE_FAMILY_INCIDENCE_NO_GO.md`](DIAG3_PAIR_SOURCE_FAMILY_INCIDENCE_NO_GO.md)

## Direct verification

From the repository root:

```bash
# Honest open-object and decision-ledger checks
python3 ai/omreal/verify_diag3_completion_open_object.py
python3 ai/omreal/verify_diag3_research_decision_ledger.py
python3 ai/omreal/verify_diag9_research_decision_ledger.py

# Final diagonal-2 finite support-drop components
python3 ai/omreal/verify_diag2_generic_birth_support_filter.py
python3 ai/omreal/verify_diag2_generic_birth_pattern_reduction.py

# Current diagonal-9 node and plane frontier
python3 ai/omreal/DIAG9_GRAPH_verify_parent860_node.py
python3 ai/omreal/verify_diag9_parent860_node_topology.py
python3 ai/omreal/verify_diag9_parent860_plane_projection.py
```

Run `python3 run_all.py --fast` for the quick repository suite or
`python3 run_all.py` for the complete discoverable suite. A few large replays require
the pinned external artifact named in their proof note and are reported separately by
the dispatcher.

## File conventions

- `DIAG*.md`, theorem notes, and ledgers state claims and scope.
- `build_*.py` and uppercase research scripts produce candidates or artifacts.
- `verify_*.py` independently replay claims and fail closed.
- `data/` holds compact pinned artifacts; large regenerable corpora stay outside Git.
- Negative results remain tracked when they close a strategy branch or justify a stop
  rule. Raw review transcripts and disposable scratch output do not.
