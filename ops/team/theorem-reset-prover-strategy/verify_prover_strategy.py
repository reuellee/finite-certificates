#!/usr/bin/env python3
"""Independent standard-library verifier for the theorem-reset prover lane."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Callable


class VerificationError(RuntimeError):
    pass


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
RESULT_PATH = HERE / "RESULT.json"
MANIFEST_PATH = HERE / "SOURCE_MANIFEST.json"

CLAUSES = [
    "(0)", "(1)", "(0,0)", "(2)", "(1,0)", "(0,0,0)",
    "(3)", "(2,0)", "(1,1)", "(1,0,0)",
]
UNIVERSAL = ["(0)", "(1)", "(2)"]
ROUTE_IDS = [
    "D3_JOINED_GORDAN_TEN_CLAUSE_THEOREM",
    "D3_UNIFORM_Q3_COMPLETE_PARENT_BOUNDARY_ATLAS",
    "D3_PAIR_GLOBAL_COMPRESSION_DESCENT_EQUIVALENCE",
    "EXACT_COUNTEREXAMPLE_OR_ROUTE_RETIREMENT",
    "D9_SIMULTANEOUS_INSERTION_2604_PARENT_THEOREM",
    "D9_ACTUAL_ARRANGEMENT_SIGN_GEODESY",
]
EXPECTED_SCORES = {
    "D3_JOINED_GORDAN_TEN_CLAUSE_THEOREM": [5, 2, 2, 4, 5, 4, 5, 3],
    "D3_UNIFORM_Q3_COMPLETE_PARENT_BOUNDARY_ATLAS": [5, 3, 2, 5, 4, 4, 4, 4],
    "D3_PAIR_GLOBAL_COMPRESSION_DESCENT_EQUIVALENCE": [5, 1, 1, 4, 5, 3, 4, 4],
    "EXACT_COUNTEREXAMPLE_OR_ROUTE_RETIREMENT": [4, 3, 4, 5, 4, 5, 5, 1],
    "D9_SIMULTANEOUS_INSERTION_2604_PARENT_THEOREM": [2, 2, 2, 4, 4, 4, 4, 4],
    "D9_ACTUAL_ARRANGEMENT_SIGN_GEODESY": [2, 2, 1, 5, 5, 3, 2, 4],
}
REQUIRED_SOURCE_PATHS = {
    "ops/research-team/PROTOCOL.md",
    "ops/research-team/cycles/2026-09-01-theorem-reset-joined-gordan-tournament-gate1/CYCLE.md",
    "ops/research-team/cycles/2026-09-01-theorem-reset-joined-gordan-tournament-gate1/WORK_ORDERS.yaml",
    "ops/research-team/cycles/2026-09-01-theorem-reset-joined-gordan-tournament-gate1/OPENING_AUDIT.json",
    "ops/research-team/cycles/2026-09-01-theorem-reset-joined-gordan-tournament-gate1/OBLIGATION_GRAPH.json",
    "ai/omreal/DIAG3_JOINED_FLOW_TRIANGLE.md",
    "ai/omreal/verify_diag3_joined_flow_triangle.py",
    "ai/omreal/DIAG3_SINGLE_BAD_TWO_SKELETON.md",
    "ai/omreal/verify_diag3_single_bad_two_skeleton.py",
    "ai/omreal/DIAG3_ARCHITECTURE_ADVERSARIAL_AUDIT.md",
    "ai/omreal/DIAG3_GLOBAL_EXIT_CRITERION.md",
    "ai/omreal/verify_diag3_completion_open_object.py",
    "ai/omreal/data/DIAG3_COMPLETION_OPEN_OBJECT.json",
    "ai/omreal/DIAG3_COMPONENT_COSHEAF_PILOT.md",
    "ops/team/d3-global-closure-leverage-audit/RESULT.json",
    "ai/omreal/NINTH_COORDINATE_PATH_THEOREM.md",
    "ai/omreal/DIAG9_GRAPH_REDUCIBILITY_AUDIT.md",
    "ai/omreal/DIAG9_GRAPH_REDUCIBILITY_NO_GO.py",
    "ai/omreal/DIAG9_SIGN_GEODESY_AUDIT.md",
    "ai/omreal/verify_diag9_sign_geodesy_audit.py",
    "ai/omreal/PARENT_CONTRACTIBILITY_AUDIT.md",
    "ai/omreal/NINE_DIAGONAL_STATUS.md",
    "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json",
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def no_duplicate_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in pairs:
        require(key not in out, f"duplicate JSON key: {key}")
        out[key] = value
    return out


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=no_duplicate_object)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_manifest(manifest: dict[str, Any], check_files: bool = True) -> None:
    require(manifest["format"] == "theorem-reset-prover-strategy-source-manifest-v1", "manifest format")
    require(manifest["track_id"] == "theorem-reset-prover-strategy", "manifest track")
    require(manifest["lane_opening_revision"] == "d4f83ffedc13f2fc07a2c8cd39a03cec8550da22", "opening revision")
    require(manifest["lane_opening_tree"] == "97ab517bfe5bf8b3b93e7d604690c4d6a1342c43", "opening tree")
    require(manifest["hash_algorithm"] == "sha256", "hash algorithm")
    require(manifest["network_used"] is False, "network must be false")
    require(manifest["connector_used"] is False, "connector must be false")
    require(manifest["external_compute_used"] is False, "external compute must be false")
    rows = manifest["sources"]
    require(isinstance(rows, list), "sources list")
    by_path = {row["path"]: row for row in rows}
    require(len(by_path) == len(rows), "duplicate source path")
    require(set(by_path) == REQUIRED_SOURCE_PATHS, "source path set")
    for rel, row in by_path.items():
        require(isinstance(row["bytes"], int) and row["bytes"] > 0, f"source bytes {rel}")
        require(isinstance(row["sha256"], str) and len(row["sha256"]) == 64, f"source digest shape {rel}")
        if check_files:
            path = REPO / rel
            require(path.is_file(), f"missing source {rel}")
            require(path.stat().st_size == row["bytes"], f"source size drift {rel}")
            require(sha256(path) == row["sha256"], f"source hash drift {rel}")


def validate_result(data: dict[str, Any]) -> None:
    require(data["format"] == "theorem-reset-prover-strategy-result-v1", "result format")
    require(data["track_id"] == "theorem-reset-prover-strategy", "result track")
    require(data["role"] == "independent prover-strategy", "independent role")
    require(data["handoff"] == "NULL", "handoff must be NULL")
    require(data["outcome"] == "PASS_EXACT_REBASELINE_FAIL_CLOSED", "outcome")
    require(data["strategy_recommendation"] == "STOP_WITHOUT_SUCCESSOR", "stop recommendation")
    require(data["construction_performed"] is False, "no construction")
    require((data["ledger_before"], data["ledger_after"], data["ledger_delta"]) == ("2/9", "2/9", "0/9"), "ledger unchanged")
    require(data["selected_successor"] == "NONE", "no successor")
    require(data["tournament_winner"] == "NONE", "no winner")

    baseline = data["source_rebaseline"]
    require(baseline["joined_dimension_formula"] == "k=(r-1)+sum(k_i)", "joined formula")
    require(baseline["ordered_clauses"] == CLAUSES, "ten ordered clauses")
    statuses = {row["id"]: row["status"] for row in baseline["clause_status"]}
    require(set(statuses) == set(CLAUSES), "clause-status domain")
    require([clause for clause in CLAUSES if statuses[clause] == "PROVED_UNIVERSAL"] == UNIVERSAL, "exact universal clause baseline")
    require(baseline["credited_universal_clauses"] == UNIVERSAL, "credited universal clauses")
    require(baseline["credited_universal_coverage"] == "3/10", "3/10 coverage")
    require(baseline["provisional_3_of_10_legitimate"] is True, "3/10 legitimacy")
    require(baseline["ten_clause_type_taxonomy_exhaustive_through_joined_dimension_3"] is True, "type taxonomy exhaustiveness")
    require(baseline["ten_clause_measure_globally_attached"] is False, "no global clause attachment")
    require(baseline["ten_clause_measure_end_to_end_d3_denominator"] is False, "not an end-to-end denominator")
    require(baseline["ten_clause_measure_has_bounded_successor_chain"] is False, "no bounded clause chain")
    require(baseline["new_universal_clause_proved"] == "NONE", "no new universal clause")

    mixed = data["mixed_block_1_0_0_analysis"]
    require(mixed["signature_bitsets"] == [14988895318912, 3405195891438080, 40418075143643136], "canary signatures")
    require(mixed["elementary_escape_sizes"] == [56, 56, 60], "canary escape sizes")
    require(mixed["triple_elementary_root_intersection_empty"] is True, "empty triple-root intersection")
    require(mixed["local_relative_chain_ranks"] == {"rank_d1": 3, "rank_d2": 6, "rank_c2": 7}, "chain ranks")
    require(mixed["local_relative_homology"] == {"H0": "0", "H1": "0", "H2": "Z"}, "local relative homology")
    require(mixed["primitive_flow_disk_boundary_vector"] == [-1, 1, 1, 1, 1, 1, 1], "flow-disk vector")
    require(mixed["singleton_root_filler_retired"] is True, "singleton no-go")
    require(mixed["genuine_mixed_block_carrier_nonexistence_proved"] is False, "no mixed-carrier no-go")
    require(mixed["canary_is_9dvl_counterexample"] is False, "not a 9DVL counterexample")
    for key in (
        "all_parents_quantifier_proved", "all_signature_triples_quantifier_proved",
        "all_supports_quantifier_proved", "zero_weight_specialization_quantifier_proved",
        "true_parent_boundary_quantifier_proved", "global_partial3_rank_identity_proved",
    ):
        require(mixed[key] is False, f"unproved mixed quantifier {key}")
    require(mixed["decision"] == "NO_NEW_UNIVERSAL_CLAUSE", "mixed decision")

    triple = data["triple_global_accounting"]
    require(triple["source_orbits"] == 79102449, "triple universe")
    require(triple["settled_orbits"] == 77940147, "triple settled")
    require(triple["residual_orbits"] == 1162302, "triple residual")
    require(triple["source_orbits"] - triple["settled_orbits"] == triple["residual_orbits"], "triple arithmetic")
    require(triple["coverage"] == "77940147/79102449", "triple coverage")
    require(triple["source_order_semantic_sha256"] == "a76a7c2cd6631c2d9724b450540bec7f3be6c106a41ae41f1736bbd2755a5ca4", "triple semantic digest")
    require(triple["global_source_denominator_certified"] is True, "global triple denominator")
    require(triple["residual_strictly_reduced_in_lane"] is False, "no residual decrease")
    require(triple["triple_only_closure_would_promote_d3"] is False, "pair branch remains")
    require(triple["first_missing_object"] == "Q3_COMPLETE_PARENT_BOUNDARY_ATLAS", "Q3 first missing")

    require(len(data["route_score_dimensions"]) == 8, "eight dimensions")
    require("stagnation_risk is literal risk" in data["score_convention"], "risk convention")
    routes = data["route_tournament"]
    require([route["id"] for route in routes] == ROUTE_IDS, "six ordered routes")
    for route in routes:
        require(route["scores"] == EXPECTED_SCORES[route["id"]], f"route score {route['id']}")
        require(all(isinstance(score, int) and 1 <= score <= 5 for score in route["scores"]), f"score range {route['id']}")
        require(route["theorem_quantifier_attachment"] is False, f"attachment gate {route['id']}")
        require(route["bounded_strict_decrease_chain"] is False, f"bounded-chain gate {route['id']}")
        require(route["successor_eligible"] is False, f"successor gate {route['id']}")
    require(routes[1]["finite_exhaustive_end_to_end_measure"] is True, "Q3 source denominator")
    require(all(not route["finite_exhaustive_end_to_end_measure"] for i, route in enumerate(routes) if i != 1), "only Q3 has a finite source denominator")
    require(routes[4]["catalog_split"] == "2546+58", "D9 parent split")

    distance = data["proof_distance"]
    expected_vector = ["2/9", 1, ["diag3_pair_hc1", "diag3_triple_hc0"], 7, "UNKNOWN", "UNKNOWN", 4, 7]
    require(distance["opening"] == expected_vector, "opening vector")
    require(distance["checkpoint"] == expected_vector, "checkpoint vector")
    require(distance["lane_closing"] == expected_vector, "lane closing vector")
    require(distance["minimum_delta_met"] is False, "minimum decrease failed")
    require(distance["strict_decrease"] is False, "no strict decrease")
    require(distance["checkpoint_decision"] == "STOP_PROOF_SEARCH_AND_HANDOFF_NULL_WITHOUT_RESOURCE_ENLARGEMENT", "midpoint stop")
    effects = data["obligation_effects"]
    require(len(effects) == 7, "seven obligations")
    require(all(row["effect"] == "UNCHANGED" and row["closing_status"] == "INCONCLUSIVE" for row in effects), "all obligations unchanged")

    detail = data["handoff_detail"]
    require(detail["classification"] == "NULL", "detail NULL")
    require(detail["positive_theorem"] == "NONE", "no positive theorem")
    require(detail["new_negative_theorem"] == "NONE", "no new negative theorem")
    require(detail["proof_distance_effect"] == "NONE", "no proof-distance effect")
    require(detail["winner_eligibility"] == "NONE", "no eligible winner")
    require(detail["successor_eligibility"] == "NONE", "no eligible successor")

    replays = {row["id"]: row for row in data["exact_replays"]}
    require(set(replays) == {
        "diag3_joined_flow_triangle", "diag3_single_bad_two_skeleton",
        "diag3_completion_open_object", "diag9_graph_reducibility_no_go",
        "diag9_sign_geodesy_audit",
    }, "replay inventory")
    for key in (
        "diag3_joined_flow_triangle", "diag3_single_bad_two_skeleton",
        "diag3_completion_open_object", "diag9_graph_reducibility_no_go",
    ):
        require(replays[key]["exit_code"] == 0, f"completed replay {key}")
    require(replays["diag9_sign_geodesy_audit"]["exit_code"] == 1, "optional replay terminated")
    require(replays["diag9_sign_geodesy_audit"]["result"] == "TERMINATED_OPTIONAL_AT_MANDATORY_MIDPOINT_STOP", "optional midpoint status")
    require(replays["diag9_sign_geodesy_audit"]["acceptance_dependency"] is False, "optional replay dependency")
    required_nonconsequences = {
        "NO_NEW_JOINED_UNIVERSAL_CLAUSE", "NO_GENUINE_MIXED_BLOCK_CARRIER_THEOREM",
        "NO_Q3_COMPLETE_PARENT_BOUNDARY_ATLAS", "NO_D3_PROOF_OR_COUNTEREXAMPLE",
        "NO_D9_SIMULTANEOUS_INSERTION_INDUCTION", "NO_D9_GLOBAL_SIGN_GEODESY",
        "NO_LEDGER_CHANGE", "NO_CONSTRUCTION_SUCCESSOR",
    }
    require(required_nonconsequences.issubset(set(data["nonconsequences"])), "required nonconsequences")


def verify_opening_git_object(manifest: dict[str, Any]) -> None:
    proc = subprocess.run(
        ["git", "rev-parse", f"{manifest['lane_opening_revision']}^{{tree}}"],
        cwd=REPO,
        text=True,
        capture_output=True,
        check=False,
    )
    require(proc.returncode == 0, "opening git object unavailable")
    require(proc.stdout.strip() == manifest["lane_opening_tree"], "opening git tree drift")


def assert_reject(label: str, mutate: Callable[[dict[str, Any]], None], pristine: dict[str, Any]) -> None:
    candidate = copy.deepcopy(pristine)
    mutate(candidate)
    try:
        validate_result(candidate)
    except (VerificationError, KeyError, TypeError, ValueError):
        return
    raise VerificationError(f"hostile mutation accepted: {label}")


def run_hostile_mutations(data: dict[str, Any], manifest: dict[str, Any]) -> int:
    mutations: list[tuple[str, Callable[[dict[str, Any]], None]]] = [
        ("positive handoff", lambda d: d.__setitem__("handoff", "POSITIVE")),
        ("construction", lambda d: d.__setitem__("construction_performed", True)),
        ("ledger promotion", lambda d: d.__setitem__("ledger_after", "3/9")),
        ("ledger delta", lambda d: d.__setitem__("ledger_delta", "1/9")),
        ("selected successor", lambda d: d.__setitem__("selected_successor", ROUTE_IDS[0])),
        ("tournament winner", lambda d: d.__setitem__("tournament_winner", ROUTE_IDS[1])),
        ("false universal clause", lambda d: d["source_rebaseline"]["credited_universal_clauses"].append("(0,0)")),
        ("false clause coverage", lambda d: d["source_rebaseline"].__setitem__("credited_universal_coverage", "4/10")),
        ("false end-to-end denominator", lambda d: d["source_rebaseline"].__setitem__("ten_clause_measure_end_to_end_d3_denominator", True)),
        ("false new clause", lambda d: d["source_rebaseline"].__setitem__("new_universal_clause_proved", "(1,0,0)")),
        ("false mixed no-go", lambda d: d["mixed_block_1_0_0_analysis"].__setitem__("genuine_mixed_block_carrier_nonexistence_proved", True)),
        ("false 9DVL counterexample", lambda d: d["mixed_block_1_0_0_analysis"].__setitem__("canary_is_9dvl_counterexample", True)),
        ("residual decrement", lambda d: d["triple_global_accounting"].__setitem__("residual_orbits", 1162301)),
        ("semantic digest", lambda d: d["triple_global_accounting"].__setitem__("source_order_semantic_sha256", "0" * 64)),
        ("score mutation", lambda d: d["route_tournament"][0]["scores"].__setitem__(0, 4)),
        ("route eligibility", lambda d: d["route_tournament"][0].__setitem__("successor_eligible", True)),
        ("route omission", lambda d: d["route_tournament"].pop()),
        ("obligation close", lambda d: d["obligation_effects"][0].__setitem__("effect", "CLOSED")),
        ("proof-distance decrease", lambda d: d["proof_distance"]["lane_closing"].__setitem__(3, 6)),
        ("minimum met", lambda d: d["proof_distance"].__setitem__("minimum_delta_met", True)),
        ("wrong midpoint", lambda d: d["proof_distance"].__setitem__("checkpoint_decision", "CONTINUE")),
        ("false negative theorem", lambda d: d["handoff_detail"].__setitem__("new_negative_theorem", "MIXED_CARRIER_IMPOSSIBLE")),
        ("optional replay promotion", lambda d: d["exact_replays"][4].__setitem__("exit_code", 0)),
        ("erase nonconsequence", lambda d: d["nonconsequences"].remove("NO_LEDGER_CHANGE")),
    ]
    for label, mutate in mutations:
        assert_reject(label, mutate, data)

    bad_hash = copy.deepcopy(manifest)
    bad_hash["sources"][0]["sha256"] = "0" * 64
    try:
        validate_manifest(bad_hash, check_files=True)
    except VerificationError:
        pass
    else:
        raise VerificationError("hostile manifest hash accepted")

    missing_source = copy.deepcopy(manifest)
    missing_source["sources"].pop()
    try:
        validate_manifest(missing_source, check_files=False)
    except VerificationError:
        pass
    else:
        raise VerificationError("hostile missing source accepted")
    return len(mutations) + 2


def main() -> int:
    data = load_json(RESULT_PATH)
    manifest = load_json(MANIFEST_PATH)
    validate_manifest(manifest, check_files=True)
    verify_opening_git_object(manifest)
    validate_result(data)
    hostile_count = run_hostile_mutations(data, manifest)
    require(hostile_count >= 12, "at least twelve hostile mutations")
    print("PASS source pins and immutable opening git tree")
    print("PASS joined-Gordan independent baseline: universal clauses (0),(1),(2) = 3/10")
    print("PASS ten types are combinatorially exhaustive but not a global end-to-end denominator")
    print("PASS mixed (1,0,0) canary: H2=Z, singleton filler retired, genuine mixed carrier unresolved")
    print("PASS triple accounting 77940147/79102449; residual 1162302; pair obligation open")
    print("PASS six theorem routes scored on all eight protocol dimensions; eligible winner NONE")
    print("PASS mandatory midpoint STOP, NULL handoff, ledger delta 0/9, successor NONE")
    print(f"PASS {hostile_count}/{hostile_count} hostile mutations rejected")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except VerificationError as exc:
        print(f"FAIL {exc}", file=sys.stderr)
        raise SystemExit(1)
