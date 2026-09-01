#!/usr/bin/env python3
"""Independent fail-closed replay for the D3 closure-leverage falsifier.

Only the Python standard library is used.  The checker authenticates pinned
repository inputs, reconstructs the finite count identities and the exact
graph-only H1 countermodel, validates the scoped null verdict, and rejects a
suite of re-sealed hostile claim mutations.
"""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESULT_PATH = HERE / "RESULT.json"

BASE = "98ed8d36f08f13305d226d3d3770e71542a0a408"
BASE_TREE = "52a03a10b62e54a9ff5aa4e59dbbc2af9a69eeab"
OPENING = "d125be9ba4dd13b402608632f277c6f85911ab89"
BRANCH = "research/lane-d3-closure-leverage-falsifier-20260901"

EXPECTED_PINS = {
    "ops/research-team/PROTOCOL.md": "c3fbec5b483426fcce97a523ba1ea1edc3e561cb33a1c4e5e957674e4270a246",
    "ops/research-team/verify_cycle_protocol.py": "e3c2f64b97d53f4de00be675a789a42668835bb1dd8759779be8392760131753",
    "ai/omreal/NINE_DIAGONAL_STATUS.md": "07c146e835f6a62c29ab653d353d73469df1e6022018ffec76f6775b65ca7ae2",
    "ai/omreal/data/CANONICAL_RESEARCH_STATE_V4.json": "6b22f3f8da550fa14ea13700ff632eb3db53c40316a0e1844a7762784cfaf811",
    "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json": "73b0b742d6336d754ae99b7054858a3a3c96b3aaf1601b2228c076a732903d6e",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json": "707a96f19f471af041d02bf22fc4267ddd4bf6b78cffde4783f660b645aed833",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json": "956fbe7e5c7b1e04c8873ed9c0f3de9cb5420e3e06f1d5fae4c60f4e0571b364",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_face_bernstein_atlas.json": "5d8029d930cea0708f00c90cac69f87de7579118cd48a6995caf7b3be26e0822",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json": "cc279d125605b45d25a3a01f462ad051038102f2bf12574f494a9d261bfc7401",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_GATE.json": "d9a16b39966cb1ce404b3df8362b722052fdc0854db331e5bc12aeec4ef9bcef",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz": "9b595b61273b2d4ad1188eca8135b7c06162e75452a89a17ffb6725f0d461e82",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_CELL_V_LIFT.json": "fcdeaffab50d14840503f6fdb1e14ac5ccbedc1c1cd0befa420f68532f2f547f",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_COEFFICIENT_ENDPOINT_U_SECTION_V_LIFT.json": "7669d4471acc206b66da58dde6bc5bf0ad8a105f87285d3af8c4c83660a8da05",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_OPEN_U_STRIP_V_LIFT.json": "c6ae837e484a788f647bbf37009bb4ab5669d17631e8c07ef1efa76f173469e0",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_REGULAR_U_POINT_V_LIFT.json": "e0e7a7d5dec4af0f2b804c03057b86049bdcffef0de90ce2fba083c748d8e16c",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_COEFFICIENT_ENDPOINT_U_POINT_V_LIFT.json": "be3e1fc8aa66842961acb22f3740cc68aa99fca65f9fd5784352cd8f53703a5b",
    "ai/omreal/data/DIAG3_COMPONENT_COSHEAF_PILOT.json": "2fa847a3f7edf206db225d3a184f90c00c54b319ad2cdeaca39cb9ed9d5b0854",
    "ai/omreal/DIAG3_GLOBAL_EXIT_CRITERION.md": "0a372197a49f4a767c06b23a6df830ef2784e7fe653b4b3eb1a506eec0518e27",
    "ops/team/global-exit/GLOBAL_EXIT_FIXTURES.json": "4bc0331835c82f0eb3e98bc87d0c6a37683ef66298e430337c3c0661ddd4a029",
}

MUTATION_NAMES = [
    "wrong-base-tree",
    "wrong-source-pin",
    "wrong-chart-count",
    "wrong-support-face-count",
    "wrong-face-state-zero",
    "broken-face-state-partition",
    "wrong-nonexcluded-face-count",
    "wrong-remaining-factor-face-pairs",
    "wrong-remaining-mixed-restrictions",
    "wrong-open-base-count",
    "wrong-algebraic-u-base-count",
    "wrong-algebraic-t-base-count",
    "broken-base-total",
    "wrong-open-lift-count",
    "wrong-algebraic-u-lift-count",
    "wrong-algebraic-t-lift-count",
    "broken-lift-total",
    "wrong-algebraic-open-u-partition",
    "wrong-algebraic-point-partition",
    "wrong-algebraic-coefficient-lift",
    "promote-global-denominator",
    "invent-global-adjacency",
    "invent-strict-closure",
    "invent-parent-infinity",
    "close-pair-invariant",
    "close-triple-invariant",
    "break-triple-identity",
    "cosheaf-promote-current-inputs",
    "broaden-graph-countermodel-scope",
    "select-direct-successor",
    "claim-finite-residual",
    "claim-minimum-delta",
    "reduce-open-obligations",
    "change-ledger-score",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def read_json(relative: str | Path) -> Any:
    path = relative if isinstance(relative, Path) else ROOT / relative
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=ROOT, text=True, encoding="utf-8"
    ).strip()


def rank_f2(matrix: list[list[int]]) -> int:
    if not matrix:
        return 0
    width = len(matrix[0])
    require(all(len(row) == width for row in matrix), "ragged matrix")
    rows = [[entry & 1 for entry in row] for row in matrix]
    rank = 0
    for column in range(width):
        pivot = next(
            (index for index in range(rank, len(rows)) if rows[index][column]),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        for index in range(len(rows)):
            if index != rank and rows[index][column]:
                rows[index] = [a ^ b for a, b in zip(rows[index], rows[rank])]
        rank += 1
    return rank


def multiply_f2(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    if not left:
        return []
    shared = len(left[0])
    require(all(len(row) == shared for row in left), "ragged left matrix")
    require(len(right) == shared, "matrix product dimension")
    columns = len(right[0]) if right else 0
    require(all(len(row) == columns for row in right), "ragged right matrix")
    return [
        [sum(left[i][k] * right[k][j] for k in range(shared)) & 1 for j in range(columns)]
        for i in range(len(left))
    ]


def source_reconstruction() -> dict[str, Any]:
    require(git("rev-parse", f"{BASE}^{{tree}}") == BASE_TREE, "base tree drift")
    require(git("rev-parse", OPENING) == OPENING, "opening revision unavailable")
    require(git("branch", "--show-current") == BRANCH, "wrong lane branch")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", OPENING, "HEAD"], cwd=ROOT
    )
    require(ancestor.returncode == 0, "lane head does not descend from opening")

    for relative, expected in EXPECTED_PINS.items():
        path = ROOT / relative
        require(path.is_file(), f"missing source pin: {relative}")
        require(sha256(path) == expected, f"source pin drift: {relative}")

    state = read_json("ai/omreal/data/CANONICAL_RESEARCH_STATE_V4.json")
    ledger = read_json("ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json")
    open_object = read_json("ai/omreal/data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json")
    atlas = read_json("ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json")
    face = read_json("ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_face_bernstein_atlas.json")
    parent = read_json("ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json")
    gate = read_json("ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_GATE.json")
    open_lift = read_json("ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_CELL_V_LIFT.json")
    open_alg = read_json("ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_COEFFICIENT_ENDPOINT_U_SECTION_V_LIFT.json")
    alg_open = read_json("ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_OPEN_U_STRIP_V_LIFT.json")
    alg_regular = read_json("ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_REGULAR_U_POINT_V_LIFT.json")
    alg_final = read_json("ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ALGEBRAIC_T_COEFFICIENT_ENDPOINT_U_POINT_V_LIFT.json")
    cosheaf = read_json("ai/omreal/data/DIAG3_COMPONENT_COSHEAF_PILOT.json")
    fixtures = read_json("ops/team/global-exit/GLOBAL_EXIT_FIXTURES.json")

    require(state["theorem"] == {
        "id": "9DVL",
        "score": "2/9",
        "proved_diagonals": [1, 2],
        "active_diagonal": None,
        "promotion": "NONE",
    }, "canonical theorem state")
    require(ledger["theorem"]["score"] == "2/9", "D3 ledger score")
    require(ledger["theorem"]["proved_diagonals"] == [1, 2], "proved diagonals")

    obligations = {item["id"]: item for item in ledger["invariant_obligations"]}
    require(set(obligations) == {"diag3_pair_hc1", "diag3_triple_hc0"}, "D3 obligation set")
    pair = obligations["diag3_pair_hc1"]
    triple = obligations["diag3_triple_hc0"]
    require(pair["status"] == "OPEN", "pair obligation promoted")
    require(triple["status"] == "OPEN", "triple obligation promoted")
    require((triple["universe_count"], triple["proved_noncompact_count"], triple["unresolved_count"]) == (79_102_449, 77_940_147, 1_162_302), "triple counts")
    require(triple["universe_count"] - triple["proved_noncompact_count"] == triple["unresolved_count"], "triple identity")

    require(atlas["chart_atlas"] == {
        "gauge_rows": [1, 2, 3, 4],
        "chart_count": 64,
        "ordered_transition_count": 4096,
        "ordered_triple_cocycle_count": 262144,
        "coordinates_per_chart": 9,
    }, "compactification chart atlas")
    require(atlas["face_supports"]["product_support_strata"] == 3375, "support faces")
    require(atlas["face_supports"]["standard_affine_infinity_support_strata"] == 2863, "infinity supports")
    require(face["candidate_count"] == 17824, "candidate factor count")
    require(face["factor_face_pair_count"] == 60_156_000, "factor-face denominator")
    require(face["state_counts"] == {"zero": 34_437_486, "definite": 8_110_206, "mixed": 17_608_308}, "face-state partition")
    require(sum(face["state_counts"].values()) == face["factor_face_pair_count"], "face-state sum")
    require(parent["support_face_classification_counts"] == {"excluded": 3364, "ambiguous": 10, "contained": 1}, "parent gate partition")
    require(parent["nonexcluded_support_face_count"] == 11, "nonexcluded support count")
    require(parent["remaining_candidate_factor_face_pair_count"] == 196_064, "remaining factor-face count")
    require(parent["remaining_mixed_residual_restriction_count"] == 70_218, "remaining mixed restriction count")
    require(gate["scope"]["global_parent_cell_coverage"] == "NOT_CLAIMED", "gate promoted globally")

    ol = open_lift["open_cell_v_lift"]
    oa = open_alg["cumulative_open_t_algebraic_u_section_v_lift"]
    af = alg_final["cumulative_algebraic_t_v_lift"]
    require((ol["open_base_cells"], ol["lifted_cells"]) == (133_828, 4_496_636), "open-cell lift")
    require((oa["completed_sections"], oa["lifted_cells"]) == (132_134, 4_047_846), "open-t algebraic-u lift")
    require((af["base_cells"], af["lifted_cells"]) == (261_571, 8_390_619), "algebraic-t lift")
    require(133_828 + 132_134 + 261_571 == 527_533, "base-cell total")
    require(4_496_636 + 4_047_846 + 8_390_619 == 16_935_101, "lifted-cell total")
    require(af["open_u_strip_base_cells"] + af["algebraic_u_point_base_cells"] == af["base_cells"], "algebraic-t base partition")
    require(af["open_u_strip_v_lift_cells"] + af["regular_point_v_lift_cells"] + af["coefficient_endpoint_point_v_lift_cells"] == af["lifted_cells"], "algebraic-t lift partition")
    require(alg_open["resource_effect"]["completed_open_u_strip_cells"] == 131_632, "algebraic open-u source")
    require(alg_regular["regular_algebraic_t_u_point_v_lift"]["lifted_cells"] == 3_664_301, "algebraic regular-point source")
    require(alg_final["coefficient_endpoint_algebraic_t_u_point_v_lift"]["lifted_cells"] == 307_146, "algebraic endpoint-point source")
    require(alg_final["resource_effect"]["remaining_ceiling"] == 0, "local v residual")
    require(alg_final["scope"]["global_gluing_and_closure_data"] == "NOT_CLAIMED", "final lift promoted globally")

    observations = open_object["observations"]
    require(open_object["status"] == "OPEN", "global open object status")
    require(open_object["smallest_open_object"]["first_missing_block"] == "coverage_certified_global_cell_universe", "first missing global block")
    require(observations["atlas_assignment_count"] == 97_224, "extension-signature universe")
    require(observations["certified_adjacency_edges_between_distinct_atlas_charts"] == 0, "global adjacency count")
    require(observations["certified_global_strict_closure_pairs"] == 0, "global closure pairs")
    require(observations["certified_global_strict_closure_triples"] == 0, "global closure triples")
    require(observations["certified_parent_infinity_cells"] == 0, "parent infinity count")

    audit = cosheaf["two_support_input_audit"]
    required_fields = [
        "cells",
        "strict_closure_pairs",
        "strict_three_cell_chains",
        "parent_infinity_subcomplex",
        "signature_profile_source",
    ]
    require(cosheaf["status"] == "BOUNDED_NO_GO", "cosheaf status")
    require(audit["compiler_result"] == "FAIL_CLOSED_BEFORE_COMPONENT_SPECIALIZATION", "cosheaf compiler result")
    require(len(audit["missing_required_fields_by_artifact"]) == 7, "cosheaf input count")
    require(all(fields == required_fields for fields in audit["missing_required_fields_by_artifact"].values()), "cosheaf missing-field contract")

    graph_ids = {graph["id"]: graph for graph in fixtures["graphs"]}
    graph = graph_ids["pair_countermodel_exit_graph"]
    require(graph["expected_accept"] is True and graph["component_faithful"] is True, "pair countermodel graph")
    counter = fixtures["pair_countermodel"]
    d1 = counter["boundary_1"]
    unfilled_d2 = counter["unfilled"]["boundary_2"]
    filled_d2 = counter["filled"]["boundary_2"]
    require(multiply_f2(d1, unfilled_d2) == [[]], "unfilled chain condition")
    require(multiply_f2(d1, filled_d2) == [[0]], "filled chain condition")
    c1_dimension = len(counter["relative_C1_basis"])
    unfilled_h1 = c1_dimension - rank_f2(d1) - rank_f2(unfilled_d2)
    filled_h1 = c1_dimension - rank_f2(d1) - rank_f2(filled_d2)
    require((unfilled_h1, filled_h1) == (1, 0), "graph-only H1 countermodel")
    require(unfilled_h1 == counter["unfilled"]["expected_h1_f2"], "unfilled expected H1")
    require(filled_h1 == counter["filled"]["expected_h1_f2"], "filled expected H1")

    return {
        "pair_statement": pair["statement"],
        "triple": triple,
        "required_fields": required_fields,
        "unfilled_h1": unfilled_h1,
        "filled_h1": filled_h1,
    }


def validate_claim(claim: dict[str, Any], facts: dict[str, Any]) -> None:
    require(claim["format"] == "d3-global-closure-leverage-falsifier-v1", "claim format")
    require(claim["lane"] == "d3-global-closure-leverage-falsifier", "lane id")
    require(claim["role"] == "isolated-falsifier", "lane role")
    require(claim["branch"] == BRANCH, "claim branch")
    require(claim["base_revision"] == BASE and claim["base_tree"] == BASE_TREE, "claim base")
    require(claim["opening_revision"] == OPENING, "claim opening")
    require(claim["verdict"] == "REJECT_ALL_CONSTRUCTION_SELECTION_CLAIMS__STALLED_INFORMATIONAL__STOP_OR_PIVOT", "claim verdict")
    require(claim["source_pins"] == EXPECTED_PINS, "claim source pins")
    require(set(claim["independence"].values()) == {False}, "independence/prohibition record")

    reconstruction = claim["reconstruction"]
    require(reconstruction["theorem"] == {"score": "2/9", "proved_diagonals": [1, 2], "promotion": "NONE"}, "theorem reconstruction")
    require(reconstruction["compactification"] == {
        "model": "(Delta^3)^3",
        "chart_count": 64,
        "ordered_transition_count": 4096,
        "ordered_triple_cocycle_count": 262144,
        "support_face_count": 3375,
        "standard_affine_infinity_support_count": 2863,
    }, "compactification claim")
    gates = reconstruction["support_and_parent_gates"]
    require(gates["candidate_factor_count"] == 17_824, "claim candidate factors")
    require(gates["candidate_factor_face_pairs"] == 60_156_000, "claim factor-face pairs")
    require(gates["face_state_partition"] == {"zero": 34_437_486, "definite": 8_110_206, "mixed": 17_608_308, "total": 60_156_000}, "claim face partition")
    require(sum(gates["face_state_partition"][key] for key in ("zero", "definite", "mixed")) == gates["face_state_partition"]["total"], "claim face-state identity")
    require(gates["excluded_support_faces"] == 3364, "claim excluded supports")
    require(gates["nonexcluded_support_faces"] == 11, "claim nonexcluded supports")
    require(gates["nonexcluded_partition"] == {"ambiguous": 10, "contained": 1}, "claim parent partition")
    require(gates["remaining_candidate_factor_face_pairs"] == 196_064, "claim remaining pairs")
    require(gates["remaining_mixed_residual_restrictions"] == 70_218, "claim remaining restrictions")

    local = reconstruction["local_cell_partition"]
    require(local["base_cells"] == {"open_t_open_u": 133_828, "open_t_algebraic_u": 132_134, "algebraic_t": 261_571, "total": 527_533}, "claim base partition")
    require(sum(local["base_cells"][key] for key in ("open_t_open_u", "open_t_algebraic_u", "algebraic_t")) == local["base_cells"]["total"], "claim base identity")
    require(local["lifted_cells"] == {"open_t_open_u": 4_496_636, "open_t_algebraic_u": 4_047_846, "algebraic_t": 8_390_619, "total": 16_935_101}, "claim lift partition")
    require(sum(local["lifted_cells"][key] for key in ("open_t_open_u", "open_t_algebraic_u", "algebraic_t")) == local["lifted_cells"]["total"], "claim lift identity")
    require(local["algebraic_t_internal"] == {
        "open_u_strip_base_cells": 131_632,
        "algebraic_u_point_base_cells": 129_939,
        "open_u_strip_v_lift_cells": 4_419_172,
        "regular_point_v_lift_cells": 3_664_301,
        "coefficient_endpoint_point_v_lift_cells": 307_146,
        "total_base_cells": 261_571,
        "total_lifted_cells": 8_390_619,
        "unresolved_local_v_fibers": 0,
    }, "claim algebraic-t partition")
    require(local["scope"] == "COMPLETE_LOCAL_FIBER_INVENTORY_ONLY", "local scope")

    global_object = reconstruction["global_open_object"]
    require(global_object == {
        "status": "OPEN",
        "first_missing_block": "coverage_certified_global_cell_universe",
        "extension_signature_universe": 97_224,
        "certified_global_adjacencies": 0,
        "certified_global_strict_closure_pairs": 0,
        "certified_global_strict_closure_triples": 0,
        "certified_parent_infinity_cells": 0,
        "global_denominator": "UNKNOWN",
    }, "claim global open object")
    invariants = reconstruction["d3_invariants"]
    require(invariants["diag3_pair_hc1"] == {"status": "OPEN", "statement": facts["pair_statement"]}, "claim pair invariant")
    triple = facts["triple"]
    require(invariants["diag3_triple_hc0"] == {
        "status": "OPEN",
        "universe_count": triple["universe_count"],
        "proved_noncompact_count": triple["proved_noncompact_count"],
        "unresolved_count": triple["unresolved_count"],
        "identity": "79102449-77940147=1162302",
    }, "claim triple invariant")

    obligations = claim["open_load_bearing_obligations"]
    require([item["id"] for item in obligations] == [
        "global_gluing", "extension_labels", "strict_closure", "relative_infinity",
        "middle_rank_replay", "diag3_pair_hc1", "diag3_triple_hc0",
    ], "claim obligation ids")
    require(len(obligations) == 7, "claim obligation count")
    require(all(item["status"] == "INCONCLUSIVE" for item in obligations), "claim obligation status")
    require(all(item["residual"] == "UNKNOWN" for item in obligations[:-1]), "claim pair-route residuals")
    require(obligations[-1]["residual"] == 1_162_302, "claim triple residual")

    routes = claim["route_attacks"]
    require(set(routes) == {"DIRECT_GLOBAL_MASTER_CLOSURE", "COMPONENT_COSHEAF_STRUCTURAL_COMPRESSION", "GRAPH_ONLY_PAIR_H1_SHORTCUT", "EXACT_COUNTEREXAMPLE_OR_RETIREMENT", "D9_B_UV_01_BASELINE"}, "route set")
    require(all(route["construction_eligible"] is False for route in routes.values()), "route eligibility")
    require(routes["DIRECT_GLOBAL_MASTER_CLOSURE"]["attack_result"] == "REJECT_UNATTACHED_GLOBAL_DENOMINATOR", "direct route disposition")
    cosheaf = routes["COMPONENT_COSHEAF_STRUCTURAL_COMPRESSION"]
    require(cosheaf["attack_result"] == "REJECT_AS_CENSUS_REPLACEMENT_WITH_CURRENT_INPUTS", "cosheaf route disposition")
    require(cosheaf["compiler_result"] == "FAIL_CLOSED_BEFORE_COMPONENT_SPECIALIZATION", "cosheaf compiler claim")
    require(cosheaf["audited_input_artifacts"] == 7, "cosheaf input claim")
    require(cosheaf["required_fields_missing_from_every_input"] == facts["required_fields"], "cosheaf missing fields claim")
    graph = routes["GRAPH_ONLY_PAIR_H1_SHORTCUT"]
    require(graph["attack_result"] == "EXACTLY_RETIRED", "graph route disposition")
    require(graph["same_component_graph"] is True and graph["same_one_skeleton"] is True, "graph sameness")
    require((graph["unfilled_h1_f2"], graph["filled_h1_f2"]) == (facts["unfilled_h1"], facts["filled_h1"]), "graph H1 ranks")
    require(graph["retirement_scope"] == "Only graph-only inference of relative pair H1 or middle rank is retired.", "graph retirement scope")
    require(graph["not_retired"] == [
        "the sufficient component-faithful triple Hc0 exit theorem",
        "D3 itself",
        "a coverage-certified global master closure route",
        "a post-closure component-cosheaf compiler",
    ], "graph non-retirement scope")
    require(routes["EXACT_COUNTEREXAMPLE_OR_RETIREMENT"]["attack_result"] == "NO_EXHAUSTIVE_ATTACHED_CANDIDATE_FAMILY", "counterexample route disposition")
    require(routes["D9_B_UV_01_BASELINE"]["attack_result"] == "DEFERRED_LOW_LEVERAGE_BASELINE_ONLY", "D9 baseline disposition")

    bar = claim["successor_bar"]
    require(bar["theorem_level_quantifier_attachment"] is False, "successor quantifier attachment")
    require(bar["certified_finite_exhaustive_progress_measure"] is False, "successor finite measure")
    require(bar["preregistered_strict_decrease_to_diagonal_3"] is False, "successor decrease")
    require(bar["eligible_route_count"] == 0 and bar["selected_successor"] is None, "successor selection")
    require(bar["minimum_acceptable_delta_met"] is False, "minimum delta")
    expected_vector = ["2/9", 1, "diag3_pair_hc1_AND_diag3_triple_hc0", 7, "UNKNOWN", "UNKNOWN", 3, 6]
    require(bar["opening_vector"] == expected_vector and bar["falsifier_vector"] == expected_vector, "proof-distance vector")
    require(bar["trajectory_classification"] == "STALLED_INFORMATIONAL", "trajectory")
    require(bar["automatic_reset_result"] == "SAME_ROUTE_CONTINUE_FORBIDDEN__STOP_OR_PIVOT_REQUIRED", "automatic reset")

    required_nonconsequences = {
        "NO_DIAGONAL_3_RESULT", "NO_9DVL_SCORE_CHANGE", "NO_PAIR_HC1_CLOSURE",
        "NO_TRIPLE_HC0_CLOSURE", "NO_GLOBAL_CELL_DENOMINATOR",
        "NO_GLOBAL_GLUE_OR_LABEL_OR_STRICT_CLOSURE_CERTIFICATE",
        "NO_TRUE_RELATIVE_INFINITY_SUBCOMPLEX", "NO_MIDDLE_RANK_REPLAY",
        "NO_D3_COUNTEREXAMPLE", "NO_RETIREMENT_OF_COMPONENT_FAITHFUL_TRIPLE_EXIT",
        "NO_RETIREMENT_OF_POST_CLOSURE_COSHEAF_COMPRESSION",
        "NO_CONSTRUCTION_SUCCESSOR_SELECTED",
    }
    require(set(claim["nonconsequences"]) == required_nonconsequences, "nonconsequence envelope")
    mutation = claim["hostile_mutation_audit"]
    require(mutation["expected_cases"] == MUTATION_NAMES, "mutation names")
    require(mutation["rejected_count"] == len(MUTATION_NAMES), "mutation rejected count")
    require(mutation["accepted_count"] == 0 and mutation["fail_closed"] is True, "mutation result")
    require(claim["verification"] == {
        "command": "python ops/team/d3-global-closure-leverage-falsifier/verify_d3_global_closure_leverage_falsifier.py",
        "implementation": "PYTHON_STANDARD_LIBRARY_ONLY",
        "clean_no_hardlink_replay_supported": True,
    }, "verification contract")


def set_path(document: dict[str, Any], path: Iterable[Any], value: Any) -> None:
    keys = list(path)
    target: Any = document
    for key in keys[:-1]:
        target = target[key]
    target[keys[-1]] = value


def mutation_cases() -> list[tuple[str, tuple[Any, ...], Any]]:
    return [
        ("wrong-base-tree", ("base_tree",), "0" * 40),
        ("wrong-source-pin", ("source_pins", "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json"), "0" * 64),
        ("wrong-chart-count", ("reconstruction", "compactification", "chart_count"), 63),
        ("wrong-support-face-count", ("reconstruction", "compactification", "support_face_count"), 3374),
        ("wrong-face-state-zero", ("reconstruction", "support_and_parent_gates", "face_state_partition", "zero"), 34_437_485),
        ("broken-face-state-partition", ("reconstruction", "support_and_parent_gates", "face_state_partition", "total"), 60_155_999),
        ("wrong-nonexcluded-face-count", ("reconstruction", "support_and_parent_gates", "nonexcluded_support_faces"), 12),
        ("wrong-remaining-factor-face-pairs", ("reconstruction", "support_and_parent_gates", "remaining_candidate_factor_face_pairs"), 196_063),
        ("wrong-remaining-mixed-restrictions", ("reconstruction", "support_and_parent_gates", "remaining_mixed_residual_restrictions"), 70_217),
        ("wrong-open-base-count", ("reconstruction", "local_cell_partition", "base_cells", "open_t_open_u"), 133_827),
        ("wrong-algebraic-u-base-count", ("reconstruction", "local_cell_partition", "base_cells", "open_t_algebraic_u"), 132_133),
        ("wrong-algebraic-t-base-count", ("reconstruction", "local_cell_partition", "base_cells", "algebraic_t"), 261_570),
        ("broken-base-total", ("reconstruction", "local_cell_partition", "base_cells", "total"), 527_532),
        ("wrong-open-lift-count", ("reconstruction", "local_cell_partition", "lifted_cells", "open_t_open_u"), 4_496_635),
        ("wrong-algebraic-u-lift-count", ("reconstruction", "local_cell_partition", "lifted_cells", "open_t_algebraic_u"), 4_047_845),
        ("wrong-algebraic-t-lift-count", ("reconstruction", "local_cell_partition", "lifted_cells", "algebraic_t"), 8_390_618),
        ("broken-lift-total", ("reconstruction", "local_cell_partition", "lifted_cells", "total"), 16_935_100),
        ("wrong-algebraic-open-u-partition", ("reconstruction", "local_cell_partition", "algebraic_t_internal", "open_u_strip_base_cells"), 131_631),
        ("wrong-algebraic-point-partition", ("reconstruction", "local_cell_partition", "algebraic_t_internal", "algebraic_u_point_base_cells"), 129_938),
        ("wrong-algebraic-coefficient-lift", ("reconstruction", "local_cell_partition", "algebraic_t_internal", "coefficient_endpoint_point_v_lift_cells"), 307_145),
        ("promote-global-denominator", ("reconstruction", "global_open_object", "global_denominator"), 16_935_101),
        ("invent-global-adjacency", ("reconstruction", "global_open_object", "certified_global_adjacencies"), 1),
        ("invent-strict-closure", ("reconstruction", "global_open_object", "certified_global_strict_closure_pairs"), 1),
        ("invent-parent-infinity", ("reconstruction", "global_open_object", "certified_parent_infinity_cells"), 1),
        ("close-pair-invariant", ("reconstruction", "d3_invariants", "diag3_pair_hc1", "status"), "CLOSED"),
        ("close-triple-invariant", ("reconstruction", "d3_invariants", "diag3_triple_hc0", "status"), "CLOSED"),
        ("break-triple-identity", ("reconstruction", "d3_invariants", "diag3_triple_hc0", "unresolved_count"), 1_162_301),
        ("cosheaf-promote-current-inputs", ("route_attacks", "COMPONENT_COSHEAF_STRUCTURAL_COMPRESSION", "construction_eligible"), True),
        ("broaden-graph-countermodel-scope", ("route_attacks", "GRAPH_ONLY_PAIR_H1_SHORTCUT", "retirement_scope"), "D3 is retired"),
        ("select-direct-successor", ("successor_bar", "selected_successor"), "DIRECT_GLOBAL_MASTER_CLOSURE"),
        ("claim-finite-residual", ("successor_bar", "certified_finite_exhaustive_progress_measure"), True),
        ("claim-minimum-delta", ("successor_bar", "minimum_acceptable_delta_met"), True),
        ("reduce-open-obligations", ("successor_bar", "falsifier_vector", 3), 6),
        ("change-ledger-score", ("reconstruction", "theorem", "score"), "3/9"),
    ]


def hostile_replay(claim: dict[str, Any], facts: dict[str, Any]) -> int:
    cases = mutation_cases()
    require([name for name, _, _ in cases] == MUTATION_NAMES, "internal mutation manifest")
    rejected = 0
    for name, path, value in cases:
        mutated = copy.deepcopy(claim)
        set_path(mutated, path, value)
        try:
            validate_claim(mutated, facts)
        except (AssertionError, KeyError, TypeError):
            rejected += 1
        else:
            raise AssertionError(f"hostile mutation accepted: {name}")
    return rejected


def main() -> int:
    try:
        facts = source_reconstruction()
        claim = read_json(RESULT_PATH)
        validate_claim(claim, facts)
        rejected = hostile_replay(claim, facts)
        require(rejected == len(MUTATION_NAMES) == 34, "hostile replay count")
    except (AssertionError, KeyError, OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"FAIL d3-global-closure-leverage-falsifier: {error}", file=sys.stderr)
        return 1
    print("PASS pinned D3 compactification/support/parent sources")
    print("PASS local census: 527533 base / 16935101 lifted / 8390619 algebraic-t lifted")
    print("PASS global denominator UNKNOWN; seven load-bearing obligations remain open")
    print("PASS graph-only pair-H1 scope: same skeleton gives H1(F2)=1 versus 0")
    print("PASS successor bar: zero eligible routes; STALLED_INFORMATIONAL / STOP_OR_PIVOT")
    print(f"PASS hostile mutations rejected: {rejected}/{len(MUTATION_NAMES)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
