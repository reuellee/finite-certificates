#!/usr/bin/env python3
"""Independent standard-library verifier for the theorem-reset falsifier lane."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESULT_PATH = HERE / "RESULT.json"
MANIFEST_PATH = HERE / "SOURCE_MANIFEST.json"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        while block := source.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def rational_rank(matrix):
    work = [[Fraction(value) for value in row] for row in matrix]
    if not work:
        return 0
    rows = len(work)
    columns = len(work[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        value = work[pivot_row][column]
        work[pivot_row] = [entry / value for entry in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][column]:
                continue
            multiple = work[row][column]
            work[row] = [
                entry - multiple * pivot_entry
                for entry, pivot_entry in zip(work[row], work[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def transpose(columns):
    return [list(row) for row in zip(*columns, strict=True)]


def multiply(left, right):
    return [
        [
            sum(left[row][middle] * right[middle][column]
                for middle in range(len(right)))
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def partitions(total, length, maximum=None):
    if length == 0:
        if total == 0:
            yield ()
        return
    if maximum is None:
        maximum = total
    for first in range(min(total, maximum), -1, -1):
        for tail in partitions(total - first, length - 1, first):
            yield (first,) + tail


def face_type_name(values):
    return "(" + ",".join(map(str, values)) + ")"


def exact_joined_face_types():
    answer = []
    for joined_dimension in range(4):
        for active_blocks in range(1, min(3, joined_dimension + 1) + 1):
            internal_sum = joined_dimension - (active_blocks - 1)
            answer.extend(
                face_type_name(partition)
                for partition in partitions(internal_sum, active_blocks)
            )
    return answer


def verify_source_manifest(manifest):
    assert manifest["format"] == "theorem-reset-falsifier-source-manifest-v1"
    assert manifest["track_id"] == "theorem-reset-falsifier"
    assert manifest["lane_opening_commit"] == "d4f83ffedc13f2fc07a2c8cd39a03cec8550da22"
    assert manifest["lane_opening_tree"] == "97ab517bfe5bf8b3b93e7d604690c4d6a1342c43"
    assert manifest["canonical_base_commit"] == "3689b5344dfed38468639d0e92b48f0b5fc4ebc8"
    assert manifest["canonical_base_tree"] == "ef14ccd9b844dae5e9b535310122251ca0e86bfb"
    assert not manifest["network_used"]
    assert not manifest["connector_used"]
    assert not manifest["external_compute_used"]
    assert not manifest["producer_acceptance_imported"]

    sources = manifest["sources"]
    assert len(sources) == 21
    assert len({entry["path"] for entry in sources}) == len(sources)
    for entry in sources:
        path = ROOT / entry["path"]
        assert path.is_file(), entry["path"]
        assert path.stat().st_size == entry["bytes"], entry["path"]
        assert file_sha256(path) == entry["sha256"], entry["path"]

    executions = {entry["command"]: entry for entry in manifest["executions"]}
    assert len(executions) == 6
    timeout = executions[
        "python -u ai/omreal/verify_diag9_sign_geodesy_audit.py --workers 4"
    ]
    assert timeout["status"] == "TIMEOUT_MANDATORY_MIDPOINT_STOP_AFTER_LOCAL_METRIC_PASS"
    assert not timeout["acceptance_use"]
    assert all(
        entry["status"] == "PASS" and entry["acceptance_use"]
        for command, entry in executions.items()
        if "verify_diag9_sign_geodesy_audit.py" not in command
    )

    commit = subprocess.run(
        ["git", "cat-file", "-p", manifest["lane_opening_commit"]],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout
    assert f"tree {manifest['lane_opening_tree']}" in commit
    assert f"parent {manifest['canonical_base_commit']}" in commit


def verify_relative_canary(result):
    boundary_1 = [
        [-1, 0, +1, -1, 0, 0, 0, 0, -1],
        [+1, -1, 0, 0, -1, -1, 0, 0, 0],
        [0, +1, -1, 0, 0, 0, -1, -1, 0],
    ]
    boundary_2_columns = [
        [+1, +1, +1, 0, 0, 0, 0, 0, 0],
        [+1, 0, 0, -1, +1, 0, 0, 0, 0],
        [0, +1, 0, 0, 0, -1, +1, 0, 0],
        [0, 0, +1, 0, 0, 0, 0, -1, +1],
        [0, 0, 0, +1, 0, 0, 0, 0, -1],
        [0, 0, 0, 0, -1, +1, 0, 0, 0],
        [0, 0, 0, 0, 0, 0, -1, +1, 0],
    ]
    boundary_2 = transpose(boundary_2_columns)
    assert multiply(boundary_1, boundary_2) == [[0] * 7 for _ in range(3)]
    assert rational_rank(boundary_1) == 3
    assert rational_rank(boundary_2) == 6
    relation = [-1, 1, 1, 1, 1, 1, 1]
    assert all(
        sum(boundary_2[row][column] * relation[column] for column in range(7)) == 0
        for row in range(9)
    )
    assert abs(relation[0]) == 1

    canary = result["rank_four_chart_zero_canary"]
    assert canary["parent"] == 2599 and canary["chart"] == 0
    assert canary["signatures"] == [14988895318912, 3405195891438080, 40418075143643136]
    assert canary["elementary_escape_sizes"] == [56, 56, 60]
    assert canary["triple_escape_intersection_empty"]
    assert canary["ordered_sector_truth"] == [[True, True], [True, False], [True, True]]
    assert canary["relative_chain_ranks"] == {"partial_1": 3, "partial_2": 6, "C2": 7}
    assert canary["relative_homology"] == {"H0": 0, "H1": 0, "H2": "Z"}
    assert canary["primitive_h2_relation"] == relation
    assert canary["singleton_nerve_cocycle_evaluation"] == 1
    assert "genuinely mixed-block carrier" in canary["not_a_counterexample_to"]
    assert canary["proper_triple_ray"]["exists"]
    assert canary["proper_triple_ray"]["endpoint_parent_wall"] == "[2467]"
    assert canary["proper_triple_ray"]["endpoint_parameter"] == "23597311/105015122"
    checkpoint = canary["mixed_comparison_checkpoint"]
    assert checkpoint["certified_comparison_incidences"] == 4
    assert checkpoint["required_comparison_incidences"] == 6
    assert checkpoint["certified_mixed_d3_cells"] == 0
    assert checkpoint["missing_singleton_comparisons"] == ["H0_to_common_ray", "H1_to_common_ray"]
    assert checkpoint["absence_is_not_nonexistence_proof"]


def validate(result, manifest, check_files=True):
    assert result["format"] == "theorem-reset-falsifier-result-v1"
    assert result["track_id"] == "theorem-reset-falsifier"
    assert result["role"] == "independent_falsifier"
    assert result["lane_opening_commit"] == manifest["lane_opening_commit"]
    assert result["canonical_base_commit"] == manifest["canonical_base_commit"]
    assert manifest["sources"][0]["path"] == "ops/research-team/PROTOCOL.md"
    assert manifest["sources"][0]["sha256"] == (
        "c3fbec5b483426fcce97a523ba1ea1edc3e561cb33a1c4e5e957674e4270a246"
    )
    assert result["overall_handoff"] == "NULL"
    assert result["trajectory_recommendation"] == "STALLED"
    assert result["strategy_recommendation"] == "PIVOT_OR_STOP"
    assert not result["successor_eligible"] and result["selected_successor"] == "NONE"
    assert (result["ledger_before"], result["ledger_after"], result["ledger_delta"]) == (
        "2/9", "2/9", "0/9"
    )
    scope = result["scope_compliance"]
    assert scope["owned_surface"] == "ops/team/theorem-reset-falsifier"
    assert not any(
        scope[key]
        for key in (
            "construction_performed", "ledger_edited", "cycle_files_edited",
            "network_used", "connector_used", "external_compute_used",
            "producer_acceptance_imported",
        )
    )

    distance = result["proof_distance"]
    assert distance["opening"] == distance["closing"]
    assert distance["opening"]["open_load_bearing_obligations"] == 7
    assert distance["opening"]["certified_exhaustive_residual"] == "UNKNOWN"
    assert distance["opening"]["global_coverage"] == "UNKNOWN"
    assert not distance["strict_decrease"]
    assert distance["midpoint"]["decision"] == "STOP_DISCOVERY"
    assert not distance["midpoint"]["resource_ceiling_enlarged"]
    assert not distance["midpoint"]["acceptance_use_of_partial_execution"]

    joined = result["joined_gordan_rebaseline"]
    assert exact_joined_face_types() == [
        "(0)", "(1)", "(0,0)", "(2)", "(1,0)", "(0,0,0)",
        "(3)", "(2,0)", "(1,1)", "(1,0,0)",
    ]
    assert joined["formal_face_types"] == exact_joined_face_types()
    assert joined["formal_face_type_denominator"] == 10
    assert joined["universally_proved_clauses"] == ["(0)", "(1)", "(2)"]
    assert joined["universal_clause_coverage"] == "3/10"
    assert not joined["formal_denominator_is_global_parent_denominator"]
    assert not joined["formal_denominator_is_end_to_end_d3_denominator"]
    assert joined["critical_open_clause"] == "(1,0,0)"
    assert joined["required_boundary"] == [-1, 1, 1, 1, 1, 1, 1]

    verify_relative_canary(result)

    triple = result["triple_global_accounting"]
    assert triple["source_orbits"] - triple["settled_orbits"] == triple["residual_orbits"]
    assert (triple["source_orbits"], triple["settled_orbits"], triple["residual_orbits"]) == (
        79102449, 77940147, 1162302
    )
    assert triple["coverage"] == "77940147/79102449"
    assert triple["source_order_semantic_sha256"] == (
        "a76a7c2cd6631c2d9724b450540bec7f3be6c106a41ae41f1736bbd2755a5ca4"
    )
    assert triple["globally_attached_source_denominator"]
    assert triple["residual_decrease_this_lane"] == 0
    assert not triple["triple_only_closure_promotes_d3"]

    pair = result["pair_global_attachment"]
    assert all(pair[key] == 0 for key in (
        "certified_global_adjacencies", "certified_global_strict_closure_pairs",
        "certified_global_strict_closure_triples",
        "certified_global_parent_infinity_cells", "certified_global_middle_rank_replays",
    ))
    assert pair["global_denominator"] == pair["global_coverage"] == "UNKNOWN"

    d9 = result["d9_accounting"]
    assert d9["reducible_or_dual_reducible"] + d9["exceptional_realizable"] == d9["realizable_parent_denominator"]
    assert (d9["reducible_or_dual_reducible"], d9["exceptional_realizable"], d9["realizable_parent_denominator"]) == (2546, 58, 2604)
    assert d9["split_identity"] == "2546+58=2604"
    assert not d9["sample_scope"]["chamber_coverage"]
    assert not d9["sample_scope"]["adjacency_coverage"]
    assert d9["existing_factor_projection_no_go"]["new_irreducibles"] == 142
    assert d9["existing_factor_projection_no_go"]["degrees"] == {"2": 23, "3": 71, "4": 43, "5": 5}

    expected_handoffs = {
        "D3_JOINED_GORDAN_TEN_CLAUSE_THEOREM": "NULL",
        "D3_UNIFORM_Q3_COMPLETE_PARENT_BOUNDARY_ATLAS": "NULL",
        "D3_PAIR_GLOBAL_COMPRESSION_DESCENT_EQUIVALENCE": "NULL",
        "EXACT_COUNTEREXAMPLE_OR_ROUTE_RETIREMENT": "NEGATIVE",
        "D9_SIMULTANEOUS_INSERTION_2604_PARENT_THEOREM": "NULL",
        "D9_ACTUAL_ARRANGEMENT_SIGN_GEODESY": "TIMEOUT",
    }
    actual_handoffs = {row["route"]: row["handoff"] for row in result["route_handoffs"]}
    assert actual_handoffs == expected_handoffs
    assert all(not row["successor_eligible"] for row in result["route_handoffs"])

    assert result["retired_lemmas_only"] == [
        "SINGLETON_BLOCK_ROOT_ONLY_FILLER_FOR_THE_ROW2599_PRIMITIVE_FLOW_DISK",
        "SECOND_RADIAL_P01_STAGE_IS_A_TRUE_PARENT_INFINITY_FACE",
        "REDUCIBLE_PARENT_DELETION_IS_SURJECTIVE_ON_PROPER_EXTENSION_INCIDENCE",
        "PIVOT_PROJECTION_CLOSES_USING_ONLY_PARENT_BRACKETS_AND_26740_RESIDUAL_FACTORS",
    ]
    assert "NO_COUNTEREXAMPLE_TO_A_GENUINELY_MIXED_BLOCK_CARRIER" in result["nonconsequences"]
    assert "NO_LEDGER_CHANGE" in result["nonconsequences"]
    assert "NO_CONSTRUCTION_SUCCESSOR" in result["nonconsequences"]
    assert result["verification"]["standard_library_only"]
    assert result["verification"]["hostile_mutations_required"] == 18

    if check_files:
        verify_source_manifest(manifest)
        ledger = read_json(ROOT / "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json")
        assert ledger["theorem"]["score"] == "2/9"
        obligations = {row["id"]: row for row in ledger["invariant_obligations"]}
        assert obligations["diag3_triple_hc0"]["unresolved_count"] == 1162302
        assert obligations["diag3_pair_hc1"]["current_global_adjacencies"] == 0
        open_object = read_json(ROOT / "ai/omreal/data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json")
        mixed = open_object["row2599_flow_triangle_mixed_d3"]
        assert mixed["certified_comparison_incidence_count"] == 4
        assert mixed["required_comparison_incidence_count"] == 6
        assert mixed["certified_mixed_d3_cell_count"] == 0


def expect_reject(name, mutate, result, manifest):
    candidate_result = deepcopy(result)
    candidate_manifest = deepcopy(manifest)
    mutate(candidate_result, candidate_manifest)
    try:
        validate(candidate_result, candidate_manifest, check_files=False)
    except (AssertionError, KeyError, TypeError, ValueError):
        return
    raise AssertionError(f"hostile mutation accepted: {name}")


def main():
    result = read_json(RESULT_PATH)
    manifest = read_json(MANIFEST_PATH)
    validate(result, manifest, check_files=True)

    mutations = [
        ("overall-positive", lambda r, m: r.__setitem__("overall_handoff", "POSITIVE")),
        ("successor-enabled", lambda r, m: r.__setitem__("successor_eligible", True)),
        ("ledger-promoted", lambda r, m: r.__setitem__("ledger_after", "3/9")),
        ("obligation-closed", lambda r, m: r["proof_distance"]["closing"].__setitem__("open_load_bearing_obligations", 6)),
        ("midpoint-used-partial", lambda r, m: r["proof_distance"]["midpoint"].__setitem__("acceptance_use_of_partial_execution", True)),
        ("nine-face-types", lambda r, m: r["joined_gordan_rebaseline"].__setitem__("formal_face_type_denominator", 9)),
        ("false-fourth-clause", lambda r, m: r["joined_gordan_rebaseline"]["universally_proved_clauses"].append("(0,0)")),
        ("nonprimitive-boundary", lambda r, m: r["rank_four_chart_zero_canary"]["primitive_h2_relation"].__setitem__(0, -2)),
        ("erase-h2", lambda r, m: r["rank_four_chart_zero_canary"]["relative_homology"].__setitem__("H2", 0)),
        ("claim-mixed-counterexample", lambda r, m: r["rank_four_chart_zero_canary"]["not_a_counterexample_to"].remove("genuinely mixed-block carrier")),
        ("invent-mixed-cell", lambda r, m: r["rank_four_chart_zero_canary"]["mixed_comparison_checkpoint"].__setitem__("certified_mixed_d3_cells", 1)),
        ("absence-means-no-go", lambda r, m: r["rank_four_chart_zero_canary"]["mixed_comparison_checkpoint"].__setitem__("absence_is_not_nonexistence_proof", False)),
        ("erase-triple-residual", lambda r, m: r["triple_global_accounting"].__setitem__("residual_orbits", 0)),
        ("invent-pair-denominator", lambda r, m: r["pair_global_attachment"].__setitem__("global_denominator", 1)),
        ("break-d9-split", lambda r, m: r["d9_accounting"].__setitem__("exceptional_realizable", 57)),
        ("promote-joined-route", lambda r, m: r["route_handoffs"][0].__setitem__("handoff", "POSITIVE")),
        ("accept-timeout-as-null", lambda r, m: r["route_handoffs"][5].__setitem__("handoff", "NULL")),
        ("corrupt-source-pin", lambda r, m: m["sources"][0].__setitem__("sha256", "0" * 64)),
    ]
    assert len(mutations) == result["verification"]["hostile_mutations_required"]
    for name, mutate in mutations:
        expect_reject(name, mutate, result, manifest)

    print("PASS source manifest: 21 hash/length pins and immutable opening parent")
    print("PASS exact joined face-type rebaseline: formal 10, universal 3/10")
    print("PASS independent relative complex: ranks 3/6, primitive H2=Z")
    print("PASS canary scope: singleton-root no-go, no mixed-block counterexample")
    print("PASS D3 accounting: 77940147/79102449, residual 1162302, pair UNKNOWN")
    print("PASS D9 scope: 2546+58=2604; reducibility and sampled-geodesy limits")
    print("PASS exact route handoffs: NULL/NULL/NULL/NEGATIVE/NULL/TIMEOUT")
    print(f"PASS hostile mutations rejected: {len(mutations)}")
    print("VERDICT NULL; ledger 2/9; no theorem-distance decrease; successor NONE")


if __name__ == "__main__":
    main()
