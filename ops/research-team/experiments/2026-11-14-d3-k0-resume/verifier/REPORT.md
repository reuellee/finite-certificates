# Independent replay and scope review — 2026-11-14

Base: `6a2807b6700ba1f771060ce6659af16097a998b2`.
Archive SHA-256 independently recomputed:
`2bb5f4c41082bd94ca8a80c4f87ad1c8d062ca7b2a6fac946bd3c051987c9949`.

Extracted into a separate fresh directory and ran all six entrypoints under individual 180-second process ceilings. All exited 0; no timeout or stderr. Complete stdout and timings are retained in REPLAY.json. Fresh extraction was discarded after replay to avoid duplicating large archived inputs.

| Script | Actual result |
|---|---|
| verify_payload.py | 26 current, 31 starting, 27 related, 24 nested payload files authenticated |
| verify_lift.py | 113 exact checks; 4 negative controls |
| verify_independent.py | 130 independent exact checks; 5 negative controls; 73 reconstructed determinant polynomials |
| curvature_circuit.py | 12 rational circuit evaluations and pivot congruences; all 15 minors; singular PSD retained; leading-minor-only hostile canary rejected |
| verify_reconciliation.py | 10 coefficient/coordinate bridge checks |
| verify_counterexample_bridge.py | Retained root contraction and all 70 parent brackets; transverse chi strictly nonzero |

Reviewed lift PROOF.md, curvature implementation, and the inherited singular-safe maximum argument. No actionable mathematical defect was found in this bounded review. This is not a full independent reproof of every inherited chart/topology dependency. Arithmetic replay does not establish absence of stationary solutions or compact components.

The canonical decision ledger's promotion rule requires BOTH invariant obligations:
1. H_c^0 of the original triple-bad intersection vanishes; current sufficient route excludes compact components for every source triple.
2. The alternating pair-to-triple map is injective over Q; current sufficient route needs a coverage-certified relative complex, not sampled adjacency.

The canonical ledger records 79,102,449 source records, 77,940,147 proved noncompact, and 1,162,302 unresolved. Counts are records, not components. Current K0 work covers one authenticated source and a necessary maximum test. Even a complete K0 exclusion leaves K!=0, remaining original source/chart coverage, and a verified bridge to original pair injectivity. The newer universal triple-wall target T may discharge both invariant obligations through inherited single/pair vanishing; a separate injectivity proof is not additionally necessary if that complete bridge and T are established. This verifier did not independently audit that whole bridge. No 3/9 promotion is justified by replay.

No canonical ledger was changed. No new whole source orbit is closed by this verifier track.
