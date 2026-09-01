#!/usr/bin/env python3
"""Generate the exact finite frontier and local-memory obstruction pair.

The generated graph pair is deliberately an abstract signed chamber-graph
model, not a claimed UOM(4,8) realization.  Its purpose is logical: it shows
that the recorded radius-one wall/circuit/multiwall/transport data do not
determine a global sector cut unless global chamber gluing is retained.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
FRONTIER = HERE / "FINITE_GRAMMAR_FRONTIER.json"
CANARIES = HERE / "HOSTILE_CANARIES.json"


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def sha256(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def cycle_edges(prefix: str, cycles: list[list[int]]) -> list[dict[str, object]]:
    edges: list[dict[str, object]] = []
    for cycle in cycles:
        for index, left in enumerate(cycle):
            right = cycle[(index + 1) % len(cycle)]
            edges.append(
                {
                    "ends": sorted([f"{prefix}{left}", f"{prefix}{right}"]),
                    "kind": "INACTIVE_SAFE",
                    "transport": "IDENTITY",
                }
            )
    return edges


def graph(name: str, positive_cycles: list[list[int]], negative_cycles: list[list[int]]) -> dict[str, object]:
    vertices = [
        {"id": f"P{index}", "active_sign": "+"} for index in range(8)
    ] + [
        {"id": f"N{index}", "active_sign": "-"} for index in range(8)
    ]
    edges = cycle_edges("P", positive_cycles) + cycle_edges("N", negative_cycles)
    for index in range(8):
        edges.append(
            {
                "ends": [f"N{(index + 1) % 8}", f"P{index}"],
                "kind": "ACTIVE_RESIDUAL_37",
                "transport": "ORDINARY_5_TO_4_SPECIALIZATION",
            }
        )
    return {
        "name": name,
        "vertices": sorted(vertices, key=lambda item: item["id"]),
        "edges": sorted(edges, key=lambda item: (item["kind"], item["ends"])),
        "multiwall_incidences": [],
    }


def build_frontier() -> dict[str, object]:
    ordinary = [37, 38, 41, 42, 44, 48, 49, 50, 51]
    localization = [36, 39, 46, 47]
    auxiliary_counts = {
        "36": 12,
        "37": 14,
        "38": 2,
        "39": 12,
        "41": 14,
        "42": 2,
        "44": 12,
        "46": 12,
        "47": 12,
        "48": 16,
        "49": 8,
        "50": 3,
        "51": 4,
    }
    local_observation = {
        "vertex_records": [
            {
                "active_sign": "+",
                "incident_kinds": {"ACTIVE_RESIDUAL_37": 1, "INACTIVE_SAFE": 2},
                "multiplicity": 8,
            },
            {
                "active_sign": "-",
                "incident_kinds": {"ACTIVE_RESIDUAL_37": 1, "INACTIVE_SAFE": 2},
                "multiplicity": 8,
            },
        ],
        "edge_records": [
            {
                "endpoint_signs": "+-",
                "kind": "ACTIVE_RESIDUAL_37",
                "multiplicity": 8,
                "transport": "ORDINARY_5_TO_4_SPECIALIZATION",
            },
            {
                "endpoint_signs": "++",
                "kind": "INACTIVE_SAFE",
                "multiplicity": 8,
                "transport": "IDENTITY",
            },
            {
                "endpoint_signs": "--",
                "kind": "INACTIVE_SAFE",
                "multiplicity": 8,
                "transport": "IDENTITY",
            },
        ],
        "multiwall_incidences": [],
        "active_circuit_template": {
            "class": "ORDINARY",
            "live_support_size": 5,
            "wall_support_size": 4,
            "dead_side": "EMPTY",
            "wall_type": 37,
        },
    }
    pair = {
        "scope": "ABSTRACT_SIGNED_CHAMBER_GRAPH_NOT_UOM_4_8_REALIZATION",
        "observation_contract": "RADIUS_ONE_TYPED_STARS_PLUS_LOCAL_CIRCUIT_COSPANS_PLUS_SIGNED_MULTIWALL_RECORDS_PLUS_EDGE_TRANSPORT",
        "shared_local_observation": local_observation,
        "shared_local_observation_sha256": sha256(local_observation),
        "cut_configuration": graph("TWO_POSITIVE_CYCLES", [[0, 1, 2, 3], [4, 5, 6, 7]], [[0, 1, 2, 3], [4, 5, 6, 7]]),
        "noncut_configuration": graph("ONE_POSITIVE_CYCLE", [list(range(8))], [list(range(8))]),
        "expected_global_behavior": {
            "TWO_POSITIVE_CYCLES": {"full_components": 1, "positive_sector_components": 2, "negative_sector_components": 2},
            "ONE_POSITIVE_CYCLE": {"full_components": 1, "positive_sector_components": 1, "negative_sector_components": 1},
        },
        "minimality_scope": {
            "class": "SIMPLE_BIPARTITE_CUBIC_SIGNED_GRAPHS_WITH_ONE_ACTIVE_AND_TWO_INACTIVE_EDGES_AT_EVERY_VERTEX",
            "reason": "Each same-sign induced graph is simple bipartite 2-regular. A disconnected example needs at least two cycles of length at least four, hence eight vertices of that sign and sixteen vertices total under the active perfect matching.",
            "minimum_vertices": 16,
        },
    }
    payload: dict[str, object] = {
        "format": "d9-universal-cut-circuit-frontier-v1",
        "base_revision": "6cbd1b4a7d3ed61bee268b6b54cbfadeece90f0e",
        "canonical_mathematical_base": "cbe84ccd7273252c81fd4da17ee360a284d2a2a6",
        "local_grammar_verdict": "DISPROVED_WITHOUT_GLOBAL_CHAMBER_GLUE",
        "global_memory_verdict": "FINITE_IN_PRINCIPLE_VIA_COMPLETE_MASTER_CHAMBER_GRAPH_BUT_NOT_CONSTRUCTED_OR_BOUNDED_BY_10000_TYPES",
        "residual_partition": {"ordinary": ordinary, "localization": localization},
        "surviving_productions": [
            {
                "name": "ONE_SIDED_SPECIALIZATION_COSPAN",
                "coverage": "ALL_13_TYPES",
                "status": "PROVED",
                "ordinary_supports": "5_TO_4_TO_EMPTY",
                "localization_supports": "4_TO_3_TO_EMPTY",
            },
            {
                "name": "OPPOSITE_PARTNER_ELIMINATION_INTERVAL",
                "coverage": "EVERY_CHOSEN_GENERIC_OPPOSITE_SIDE_PAIR",
                "status": "PROVED_CONDITIONAL",
                "ordinary_union_support_bound": 6,
                "localization_union_support_bound": 5,
                "certified_auxiliary_counts": auxiliary_counts,
                "certified_pair_count": 671,
                "persistent_support_candidate_count": 2420,
            },
            {
                "name": "SAME_SIDE_CHOICE_SIMPLEX",
                "coverage": "ONE_GENERIC_WALL",
                "status": "PROVED",
            },
            {
                "name": "ALL_CODIMENSION_CONVEX_CARRIER_COHERENCE",
                "coverage": "COMMON_NONEMPTY_SUPPORT_CARRIERS",
                "status": "PROVED_CONDITIONAL",
            },
        ],
        "first_unclassified_actual_composition": {
            "name": "ROW2599_THREE_BLOCK_PENCIL_RIGID_CORNER",
            "status": "UNCLASSIFIED_GLOBAL_TRANSFER",
            "signatures_and_supports": [
                {"signature": 68231279848521727, "support": [0, 19, 34, 37, 40]},
                {"signature": 62614156573450111, "support": [0, 18, 47, 48, 53]},
                {"signature": 40418078342512640, "support": [4, 5, 18, 20, 40]},
            ],
            "colex_parent_label_degree": [4, 4, 6, 4, 5, 5, 3, 5],
            "missing_rule": "ACYCLIC_MULTI_BLOCK_TRANSFER_TO_ANOTHER_BAD_BLOCK_OR_PROPER_BOUNDARY_CELL",
            "nonconsequence": "NOT_A_GLOBAL_SEPARATOR_AND_NOT_A_9DVL_COUNTEREXAMPLE",
        },
        "required_global_memory": [
            "CONNECTED_MASTER_CHAMBER_IDENTITIES",
            "GLOBAL_ENDPOINT_INCIDENCE_FOR_EVERY_GENERIC_WALL_COMPONENT",
            "COMPLETE_SIGNATURE_LABELS_OR_ACTIVE_SECTOR_SIGN_WORDS",
            "ACYCLIC_MULTI_BLOCK_TRANSFER_POTENTIAL",
            "PROPER_BOUNDARY_AND_INFINITY_ATTACHMENTS",
        ],
        "local_memory_counterpair": pair,
        "scope": {
            "actual_uom_4_8_universal_cut_grammar": "UNRESOLVED",
            "local_type_only_completeness": "DISPROVED",
            "finite_full_global_graph_grammar": "THEORETICALLY_SUFFICIENT_PER_PARENT",
            "obstruction_type_bound_10000": "NOT_PROVED",
            "exact_instance_bound_250000": "NOT_PROVED",
            "diagonal_9": "UNCHANGED_2_OF_9",
        },
    }
    payload["semantic_sha256"] = sha256(payload)
    return payload


def build_canaries() -> dict[str, object]:
    return {
        "format": "d9-universal-cut-circuit-hostile-canaries-v1",
        "canaries": [
            {
                "name": "delete_inactive_edge",
                "operation": "DELETE",
                "path": ["local_memory_counterpair", "cut_configuration", "edges", 8],
                "expected_error": "edge census",
            },
            {
                "name": "active_edge_same_sign",
                "operation": "SET",
                "path": ["local_memory_counterpair", "cut_configuration", "vertices", 0, "active_sign"],
                "value": "+",
                "expected_error": "vertex signs",
            },
            {
                "name": "forge_component_count",
                "operation": "SET",
                "path": ["local_memory_counterpair", "expected_global_behavior", "TWO_POSITIVE_CYCLES", "positive_sector_components"],
                "value": 1,
                "expected_error": "component count",
            },
            {
                "name": "erase_specialization_transport",
                "operation": "SET",
                "path": ["local_memory_counterpair", "cut_configuration", "edges", 0, "transport"],
                "value": "IDENTITY",
                "expected_error": "transport",
            },
            {
                "name": "forge_semantic_digest",
                "operation": "SET",
                "path": ["semantic_sha256"],
                "value": "00",
                "expected_error": "semantic digest",
            },
        ],
    }


def main() -> None:
    FRONTIER.write_text(json.dumps(build_frontier(), indent=2, sort_keys=True) + "\n", encoding="ascii")
    CANARIES.write_text(json.dumps(build_canaries(), indent=2, sort_keys=True) + "\n", encoding="ascii")
    print(f"WROTE {FRONTIER.name}")
    print(f"WROTE {CANARIES.name}")


if __name__ == "__main__":
    main()
