#!/usr/bin/env python3
"""Independent standard-library verifier for the D3 leverage certificate."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
RESULT_PATH = Path(__file__).with_name("RESULT.json")
BASE = "98ed8d36f08f13305d226d3d3770e71542a0a408"
TREE = "52a03a10b62e54a9ff5aa4e59dbbc2af9a69eeab"
BRANCH = "research/lane-d3-closure-leverage-certificate-20260901"

PINS = {
    "ai/omreal/DIAG3_GLOBAL_EXIT_CRITERION.md": {
        "git_blob": "4960b0f4aa3e0f2a3205c34ce5bac670738729e2",
        "sha256": "0a372197a49f4a767c06b23a6df830ef2784e7fe653b4b3eb1a506eec0518e27",
    },
    "ai/omreal/data/DIAG3_COMPLETION_OPEN_OBJECT.json": {
        "git_blob": "f7a9d0bc8168a3cbac3c0c922756f2c40bbe0552",
        "sha256": "ea8808e8979603757dec928b1e9aeb266aa3eabcfb2e70c1f13e7aa5c4af6ece",
    },
    "ai/omreal/data/DIAG3_COMPONENT_COSHEAF_PILOT.json": {
        "git_blob": "6b8cb5766b25ee910bcd4ea1e9da8adb05e5fad2",
        "sha256": "2fa847a3f7edf206db225d3a184f90c00c54b319ad2cdeaca39cb9ed9d5b0854",
    },
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json": {
        "git_blob": "1b44f497dbe4fd5db05dd4a56271fc7919a9b97b",
        "sha256": "707a96f19f471af041d02bf22fc4267ddd4bf6b78cffde4783f660b645aed833",
    },
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_COEFFICIENT_ENDPOINT_U_POINT_V_LIFT.json": {
        "git_blob": "7609eebf51cef603f256db81a1042a91547c0153",
        "sha256": "be3e1fc8aa66842961acb22f3740cc68aa99fca65f9fd5784352cd8f53703a5b",
    },
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_COEFFICIENT_ENDPOINT_U_SECTION_V_LIFT.json": {
        "git_blob": "a43efadccae60cd6e1902dbcc418470d4374d979",
        "sha256": "7669d4471acc206b66da58dde6bc5bf0ad8a105f87285d3af8c4c83660a8da05",
    },
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_GATE.json": {
        "git_blob": "b9fe3df64a1b56d3e573db78b1c391e109218017",
        "sha256": "d9a16b39966cb1ce404b3df8362b722052fdc0854db331e5bc12aeec4ef9bcef",
    },
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_CELL_V_LIFT.json": {
        "git_blob": "e2588c26870394207cdd041db5188812000125a7",
        "sha256": "fcdeaffab50d14840503f6fdb1e14ac5ccbedc1c1cd0befa420f68532f2f547f",
    },
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json": {
        "git_blob": "8fb62c3c0817cf519d4a779fdbc27b091b3a9dc4",
        "sha256": "956fbe7e5c7b1e04c8873ed9c0f3de9cb5420e3e06f1d5fae4c60f4e0571b364",
    },
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_face_bernstein_atlas.json": {
        "git_blob": "a20518f9a8c0f4ab8e23bbcf90e4479a2410ebcb",
        "sha256": "5d8029d930cea0708f00c90cac69f87de7579118cd48a6995caf7b3be26e0822",
    },
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json": {
        "git_blob": "59a128491c09b2d2c7a98095c173b15afa928e68",
        "sha256": "cc279d125605b45d25a3a01f462ad051038102f2bf12574f494a9d261bfc7401",
    },
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def git(*args: str) -> bytes:
    return subprocess.check_output(
        ["git", "-C", str(ROOT), *args], stderr=subprocess.STDOUT
    )


def pinned_bytes(path: str) -> bytes:
    raw = git("show", f"{BASE}:{path}")
    pin = PINS[path]
    require(hashlib.sha256(raw).hexdigest() == pin["sha256"], f"sha256 pin: {path}")
    blob = git("rev-parse", f"{BASE}:{path}").decode().strip()
    require(blob == pin["git_blob"], f"blob pin: {path}")
    return raw


def pinned_json(path: str) -> dict:
    return json.loads(pinned_bytes(path))


def reconstruct_sources() -> dict:
    completion = pinned_json("ai/omreal/data/DIAG3_COMPLETION_OPEN_OBJECT.json")
    cosheaf = pinned_json("ai/omreal/data/DIAG3_COMPONENT_COSHEAF_PILOT.json")
    closure = pinned_json("ai/omreal/data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json")
    t_lift = pinned_json(
        "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_COEFFICIENT_ENDPOINT_U_POINT_V_LIFT.json"
    )
    u_lift = pinned_json(
        "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_COEFFICIENT_ENDPOINT_U_SECTION_V_LIFT.json"
    )
    gate = pinned_json("ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_GATE.json")
    open_lift = pinned_json(
        "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_CELL_V_LIFT.json"
    )
    atlas = pinned_json(
        "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json"
    )
    face = pinned_json(
        "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_face_bernstein_atlas.json"
    )
    parent = pinned_json(
        "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json"
    )
    exit_note = pinned_bytes("ai/omreal/DIAG3_GLOBAL_EXIT_CRITERION.md").decode()

    require(completion["ledger_score"] == "2/9", "honest ledger source")
    require(completion["pair_obligation"]["status"] == "OPEN", "pair source")
    require(completion["triple_obligation"]["status"] == "OPEN", "triple source")
    require(
        completion["triple_obligation"]["unresolved_count"] == 1162302,
        "triple residue source",
    )
    require(atlas["chart_atlas"]["chart_count"] == 64, "chart source")
    require(face["face_count"] == 3375, "support-face source")
    require(face["factor_face_pair_count"] == 60156000, "factor-face source")
    require(
        face["eliminated_factor_face_pairs"] == 42547692
        and face["state_counts"]["mixed"] == 17608308,
        "Bernstein partition source",
    )
    require(parent["excluded_support_face_count"] == 3364, "excluded faces")
    require(parent["nonexcluded_support_face_count"] == 11, "retained faces")
    require(
        parent["remaining_mixed_residual_restriction_count"] == 70218,
        "parent-gate residue",
    )
    require(gate["combined_compression"]["ambient_mixed_restrictions"] == 8017, "gate ambient")
    require(gate["combined_compression"]["distinct_parent_reduced_zero_sets"] == 94, "gate zero sets")
    require(gate["combined_compression"]["distinct_active_walls_after_positive_quotient"] == 22, "gate walls")
    require(gate["combined_compression"]["unresolved_interior_zero_sets"] == 0, "gate unresolved")

    base_partition = cosheaf["two_support_input_audit"]["base_cell_partition"]
    lift_partition = cosheaf["two_support_input_audit"]["lifted_cell_partition"]
    require(base_partition == {
        "open_t_open_u": 133828,
        "open_t_algebraic_u": 132134,
        "algebraic_t": 261571,
        "total": 527533,
    }, "base partition")
    require(lift_partition == {
        "open_t_open_u": 4496636,
        "open_t_algebraic_u": 4047846,
        "algebraic_t": 8390619,
        "total": 16935101,
    }, "lift partition")
    require(open_lift["open_cell_v_lift"]["lifted_cells"] == 4496636, "open lift")
    require(u_lift["cumulative_open_t_algebraic_u_section_v_lift"]["lifted_cells"] == 4047846, "u lift")
    require(t_lift["cumulative_algebraic_t_v_lift"]["lifted_cells"] == 8390619, "t lift")
    require(t_lift["resource_effect"]["remaining_ceiling"] == 0, "local residue")

    observations = closure["observations"]
    require(observations["certified_adjacency_edges_between_distinct_atlas_charts"] == 0, "adjacency source")
    require(observations["certified_global_strict_closure_pairs"] == 0, "pair source")
    require(observations["certified_global_strict_closure_triples"] == 0, "triple source")
    require(observations["certified_parent_infinity_cells"] == 0, "infinity source")
    missing = cosheaf["two_support_input_audit"]["missing_required_fields_by_artifact"]
    require(len(missing) == 7, "seven audited manifests")
    require(all("signature_profile_source" in fields for fields in missing.values()), "labels absent")
    require(cosheaf["status"] == "BOUNDED_NO_GO", "cosheaf status")
    require("same accepted\ncomponent graph and the same one-skeleton" in exit_note, "countermodel common data")
    require("`dim H1(F2)=1`" in exit_note and "`dim H1(F2)=0`" in exit_note, "countermodel ranks")
    require("not a 9DVL\ncounterexample" in exit_note, "countermodel scope")

    remaining = [
        {"id": "global_gluing", "status": "OPEN", "certified_adjacencies": 0},
        {"id": "extension_bad_labels", "status": "OPEN", "complete_global_label_contracts": 0},
        {"id": "strict_closure", "status": "OPEN", "certified_pairs": 0, "certified_triples": 0},
        {"id": "relative_infinity", "status": "OPEN", "certified_parent_infinity_cells": 0},
        {"id": "middle_rank_replay", "status": "NOT_COMPUTABLE_GLOBALLY_FROM_CURRENT_DATA", "eligible_global_chain_complexes": 0},
        {"id": "global_exclusive_pair_invariant", "status": "OPEN", "open_invariant_obligations": 1},
        {"id": "triple_compact_component_invariant", "status": "OPEN", "open_invariant_obligations": 1, "unresolved_source_orbits": 1162302},
    ]

    return {
        "theorem_ledger": {
            "score": "2/9",
            "proved_diagonals": [1, 2],
            "diagonal_three": "OPEN",
            "pair_invariant": "OPEN",
            "triple_invariant": "OPEN",
            "triple_unresolved_source_orbits": 1162302,
        },
        "compactification": {
            "model": atlas["model"],
            "chart_count": 64,
            "support_face_count": 3375,
            "candidate_residual_factors": face["candidate_count"],
            "factor_face_pairs": 60156000,
            "bernstein_eliminated_pairs": 42547692,
            "bernstein_mixed_pairs": 17608308,
        },
        "support_parent_gates": {
            "excluded_support_faces": 3364,
            "nonexcluded_support_faces": 11,
            "remaining_mixed_residual_restrictions": 70218,
            "first_four_support_ambient_mixed_restrictions": 8017,
            "first_four_support_parent_reduced_zero_sets": 94,
            "first_four_support_active_wall_equations": 22,
            "unresolved_first_four_support_zero_sets": 0,
            "global_parent_cell_coverage": gate["scope"]["global_parent_cell_coverage"],
        },
        "local_inventory": {
            "base_cells": base_partition,
            "lifted_cells": lift_partition,
            "unresolved_local_v_fibers": 0,
            "scope": "complete local fiber inventory on supports (3,1,15) and (3,3,7), not a global regular complex",
        },
        "global_interface": {
            "certified_global_adjacencies": 0,
            "certified_global_strict_closure_pairs": 0,
            "certified_global_strict_closure_triples": 0,
            "certified_parent_infinity_cells": 0,
            "complete_global_label_contracts": 0,
            "middle_rank_status": completion["pair_obligation"]["middle_exactness_status"],
        },
        "component_cosheaf": {
            "status": "BOUNDED_NO_GO",
            "no_go_scope": cosheaf["decision"]["no_go_scope"],
            "safe_role": "post-closure compression after a certified face poset, specialization maps, labels, infinity, and two-cell incidence exist",
            "audited_manifests": 7,
            "manifests_with_complete_input_contract": 0,
        },
        "graph_only_countermodel": {
            "scope": "countermodel to graph-only pair certification, not a 9DVL counterexample",
            "same_accepted_component_graph": True,
            "same_one_skeleton": True,
            "unfilled_h1_f2": 1,
            "filled_h1_f2": 0,
            "discriminator": "two-cell incidence",
            "consequence": "component reachability and true-infinity marks do not determine pair H1 or the alternating middle rank",
        },
        "remaining_obligations": remaining,
    }


def expected_routes() -> list[dict]:
    return [
        {
            "id": "direct_global_master_closure_census",
            "description": "coverage-certified global master closure, gluing, extension/bad labels, strict closure, genuine relative infinity, and mod-2 middle-rank replay",
            "theorem_quantifier_attachment": True,
            "certified_finite_exhaustive_progress_measure": False,
            "preregistered_bounded_decrease_to_diagonal_three": False,
            "eligible_bounded_successor": False,
            "reason": "the finite ambient atlas and complete local census do not provide a certified denominator for the missing global incidence, label, infinity, and rank work or a bounded successor-chain decrease",
        },
        {
            "id": "structural_component_cosheaf_compression",
            "description": "replace the global census by component-specialization data and retain exact overlap/two-cell incidence",
            "theorem_quantifier_attachment": False,
            "certified_finite_exhaustive_progress_measure": False,
            "preregistered_bounded_decrease_to_diagonal_three": False,
            "eligible_bounded_successor": False,
            "reason": "reuse of the completed manifests is BOUNDED_NO_GO; a roadmap graph omits the two-cell data that distinguishes H1, and no bounded replacement construction is presently certified",
        },
        {
            "id": "exact_graph_only_counterexample_retirement",
            "description": "retire graph-only pair certification using the filled/unfilled relative-CW countermodel",
            "theorem_quantifier_attachment": False,
            "certified_finite_exhaustive_progress_measure": True,
            "preregistered_bounded_decrease_to_diagonal_three": False,
            "eligible_bounded_successor": False,
            "reason": "the exact countermodel retires only an insufficient certificate language; it is not a 9DVL counterexample and closes neither D3 invariant",
        },
        {
            "id": "deferred_d9_b_uv_01_baseline",
            "description": "deferred D9 B-UV-01 route retained only as a low-leverage comparison baseline",
            "theorem_quantifier_attachment": False,
            "certified_finite_exhaustive_progress_measure": False,
            "preregistered_bounded_decrease_to_diagonal_three": False,
            "eligible_bounded_successor": False,
            "reason": "it has no attachment to either open diagonal-three invariant and cannot be the default for this D3 audit",
        },
    ]


def validate_result(result: dict, reconstruction: dict) -> None:
    require(result["format"] == "d3-global-closure-leverage-independent-certificate-v1", "format")
    require(result["lane"] == "independent-certificate", "lane")
    require(result["branch"] == BRANCH, "branch")
    require(result["base"] == {"commit": BASE, "tree": TREE}, "base pin")
    require(result["independence"] == {
        "reconstruction": "directly from pinned repository sources",
        "audit_lane_imported": False,
        "falsifier_lane_imported": False,
        "construction_performed": False,
        "network_used": False,
    }, "independence")
    require(result["source_pins"] == PINS, "source pins")
    require(result["reconstruction"] == reconstruction, "source reconstruction")
    require(result["route_audit"] == expected_routes(), "route audit")
    require(all(not route["eligible_bounded_successor"] for route in result["route_audit"]), "ineligible routes")
    require(result["selection"] == {
        "eligible_route_count": 0,
        "eligible_route_ids": [],
        "selected_bounded_construction_target": "NONE",
        "verdict": "STALLED_INFORMATIONAL",
        "automatic_action": "STOP_PIVOT",
        "successor": "NONE_FROM_CERTIFICATE_LANE",
        "rationale": "no audited route simultaneously has theorem-level quantifier attachment, a certified finite/exhaustive progress measure, and a preregistered bounded decrease capable of reaching diagonal three",
    }, "selection")
    require(result["theorem_accounting"] == {
        "score_before": "2/9",
        "score_after": "2/9",
        "ledger_delta": "0/9",
        "diagonal_three_proved": False,
        "pair_invariant_closed": False,
        "triple_invariant_closed": False,
        "nonconsequences": [
            "local cell completeness does not imply global gluing or strict closure",
            "component reachability does not determine relative H1",
            "the graph-only countermodel is not a 9DVL counterexample",
            "no construction target is authorized by this lane",
        ],
    }, "theorem accounting")
    require(result["hostile_replay"] == {
        "mutation_count": 42,
        "rejected": 42,
        "accepted": 0,
        "result": "PASS",
    }, "hostile replay declaration")


def set_path(record: dict, path: tuple, value) -> None:
    cursor = record
    for key in path[:-1]:
        cursor = cursor[key]
    cursor[path[-1]] = value


def hostile_mutations() -> list[tuple[str, tuple, object]]:
    first_pin = "ai/omreal/DIAG3_GLOBAL_EXIT_CRITERION.md"
    return [
        ("format", ("format",), "v2"),
        ("lane", ("lane",), "audit"),
        ("branch", ("branch",), "research/wrong"),
        ("base_commit", ("base", "commit"), "0" * 40),
        ("base_tree", ("base", "tree"), "0" * 40),
        ("audit_import", ("independence", "audit_lane_imported"), True),
        ("source_sha", ("source_pins", first_pin, "sha256"), "0" * 64),
        ("source_blob", ("source_pins", first_pin, "git_blob"), "0" * 40),
        ("ledger", ("reconstruction", "theorem_ledger", "score"), "3/9"),
        ("d3", ("reconstruction", "theorem_ledger", "diagonal_three"), "PROVED"),
        ("chart_count", ("reconstruction", "compactification", "chart_count"), 63),
        ("support_faces", ("reconstruction", "compactification", "support_face_count"), 3374),
        ("excluded_faces", ("reconstruction", "support_parent_gates", "excluded_support_faces"), 3363),
        ("retained_faces", ("reconstruction", "support_parent_gates", "nonexcluded_support_faces"), 12),
        ("base_open", ("reconstruction", "local_inventory", "base_cells", "open_t_open_u"), 133827),
        ("base_algebraic_u", ("reconstruction", "local_inventory", "base_cells", "open_t_algebraic_u"), 132133),
        ("base_algebraic_t", ("reconstruction", "local_inventory", "base_cells", "algebraic_t"), 261570),
        ("base_total", ("reconstruction", "local_inventory", "base_cells", "total"), 527532),
        ("lift_open", ("reconstruction", "local_inventory", "lifted_cells", "open_t_open_u"), 4496635),
        ("lift_algebraic_u", ("reconstruction", "local_inventory", "lifted_cells", "open_t_algebraic_u"), 4047845),
        ("lift_algebraic_t", ("reconstruction", "local_inventory", "lifted_cells", "algebraic_t"), 8390618),
        ("lift_total", ("reconstruction", "local_inventory", "lifted_cells", "total"), 16935100),
        ("local_residue", ("reconstruction", "local_inventory", "unresolved_local_v_fibers"), 1),
        ("adjacency", ("reconstruction", "global_interface", "certified_global_adjacencies"), 1),
        ("closure_pairs", ("reconstruction", "global_interface", "certified_global_strict_closure_pairs"), 1),
        ("closure_triples", ("reconstruction", "global_interface", "certified_global_strict_closure_triples"), 1),
        ("infinity", ("reconstruction", "global_interface", "certified_parent_infinity_cells"), 1),
        ("labels", ("reconstruction", "global_interface", "complete_global_label_contracts"), 1),
        ("cosheaf_status", ("reconstruction", "component_cosheaf", "status"), "PROVED"),
        ("countermodel_unfilled", ("reconstruction", "graph_only_countermodel", "unfilled_h1_f2"), 0),
        ("countermodel_filled", ("reconstruction", "graph_only_countermodel", "filled_h1_f2"), 1),
        ("obligation_status", ("reconstruction", "remaining_obligations", 0, "status"), "CLOSED"),
        ("triple_residue", ("reconstruction", "remaining_obligations", 6, "unresolved_source_orbits"), 0),
        ("direct_eligible", ("route_audit", 0, "eligible_bounded_successor"), True),
        ("compression_attachment", ("route_audit", 1, "theorem_quantifier_attachment"), True),
        ("retirement_attachment", ("route_audit", 2, "theorem_quantifier_attachment"), True),
        ("eligible_count", ("selection", "eligible_route_count"), 1),
        ("selected_target", ("selection", "selected_bounded_construction_target"), "DIRECT"),
        ("verdict", ("selection", "verdict"), "PASS"),
        ("ledger_after", ("theorem_accounting", "score_after"), "3/9"),
        ("mutation_count", ("hostile_replay", "mutation_count"), 41),
        ("accepted_mutation", ("hostile_replay", "accepted"), 1),
    ]


def main() -> int:
    require(git("rev-parse", f"{BASE}^{{tree}}").decode().strip() == TREE, "base tree")
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    reconstruction = reconstruct_sources()
    validate_result(result, reconstruction)

    mutations = hostile_mutations()
    require(len(mutations) == 42, "hostile mutation inventory")
    rejected = 0
    for name, path, value in mutations:
        mutant = copy.deepcopy(result)
        set_path(mutant, path, value)
        try:
            validate_result(mutant, reconstruction)
        except (AssertionError, KeyError, TypeError):
            rejected += 1
        else:
            raise AssertionError(f"hostile mutation accepted: {name}")
    require(rejected == 42, "hostile rejection count")

    print(f"PASS base={BASE} tree={TREE}")
    print("PASS independent pinned-source reconstruction: ledger=2/9, D3 pair/triple OPEN")
    print("PASS local inventory: 527533 base cells -> 16935101 lifted cells; unresolved local v fibers=0")
    print("PASS global interface: adjacency=0 pairs=0 triples=0 infinity=0 labels=0")
    print("PASS graph-only countermodel scope: H1(F2) 1 versus 0; not a 9DVL counterexample")
    print("PASS 42/42 hostile mutations rejected")
    print("VERDICT STALLED_INFORMATIONAL action=STOP_PIVOT selected_target=NONE ledger_delta=0/9")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, json.JSONDecodeError, subprocess.CalledProcessError) as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)
