#!/usr/bin/env python3
"""Independent standard-library verifier for the theorem-reset lane."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESULT_PATH = HERE / "RESULT.json"
MANIFEST_PATH = HERE / "SOURCE_MANIFEST.json"

BASE = "3689b5344dfed38468639d0e92b48f0b5fc4ebc8"
BASE_TREE = "ef14ccd9b844dae5e9b535310122251ca0e86bfb"
OPENING = "d4f83ffedc13f2fc07a2c8cd39a03cec8550da22"
OPENING_TREE = "97ab517bfe5bf8b3b93e7d604690c4d6a1342c43"
DIGEST = "a76a7c2cd6631c2d9724b450540bec7f3be6c106a41ae41f1736bbd2755a5ca4"
ROUTES = [
    "D3_JOINED_GORDAN_TEN_CLAUSE_THEOREM",
    "D3_UNIFORM_Q3_COMPLETE_PARENT_BOUNDARY_ATLAS",
    "D3_PAIR_GLOBAL_COMPRESSION_DESCENT_EQUIVALENCE",
    "EXACT_COUNTEREXAMPLE_OR_ROUTE_RETIREMENT",
    "D9_SIMULTANEOUS_INSERTION_2604_PARENT_THEOREM",
    "D9_ACTUAL_ARRANGEMENT_SIGN_GEODESY",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for chunk in iter(lambda: source.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(*arguments: str) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=ROOT, text=True, encoding="utf-8"
    ).strip()


def validate_result(result: dict) -> None:
    require(result["format"] == "theorem-reset-independent-verifier-result-v1", "format")
    require(result["role"] == "independent-verifier", "role")
    require(result["scientific_base_commit"] == BASE, "base commit")
    require(result["scientific_base_tree"] == BASE_TREE, "base tree")
    require(result["lane_opening_commit"] == OPENING, "opening commit")
    require(result["lane_opening_tree"] == OPENING_TREE, "opening tree")
    require(result["pin_check"] == "PASS", "pin status")

    opening = result["opening_reconstruction"]
    require(opening["ledger"] == "2/9" and opening["deficit"] == 1, "opening ledger")
    require(opening["open_load_bearing_obligations"] == 7, "opening obligations")
    require(opening["pair_residual"] == "UNKNOWN", "pair residual")
    require(opening["pair_coverage"] == "UNKNOWN", "pair coverage")
    require(opening["same_blocker_streak"] == 4, "same-blocker streak")
    require(opening["zero_ledger_streak"] == 7, "zero-ledger streak")

    triple = result["triple_accounting"]
    require(triple["source_orbits"] == 79102449, "triple source")
    require(triple["settled_orbits"] == 77940147, "triple settled")
    require(triple["residual_orbits"] == 1162302, "triple residual")
    require(
        triple["source_orbits"] - triple["settled_orbits"] == triple["residual_orbits"],
        "triple arithmetic",
    )
    require(triple["coverage"] == "77940147/79102449", "triple coverage")
    require(triple["source_order_residual_semantic_sha256"] == DIGEST, "triple digest")
    require(triple["source_denominator_globally_attached"] is True, "source attachment")
    require(triple["closes_diag3_alone"] is False, "triple nonpromotion")

    joined = result["joined_clause_rebaseline"]
    expected_types = [
        "(0)", "(1)", "(0,0)", "(2)", "(1,0)", "(0,0,0)",
        "(3)", "(2,0)", "(1,1)", "(1,0,0)",
    ]
    require(joined["face_type_denominator"] == 10, "joined denominator")
    require(joined["face_types"] == expected_types, "joined types")
    require(joined["universally_credited"] == ["(0)", "(1)", "(2)"], "joined credit")
    require(joined["universal_credit"] == "3/10", "joined fraction")
    require(joined["critical_missing_clause"] == "(1,0,0)", "critical clause")
    require(joined["global_cell_coverage_proved"] is False, "false global coverage")
    require(joined["end_to_end_d3_denominator"] is False, "false end-to-end denominator")
    require(joined["new_universal_clause_proved"] is False, "false new clause")

    gates = result["route_gates"]
    require([gate["route"] for gate in gates] == ROUTES, "route set/order")
    require([gate["classification"] for gate in gates] == [
        "NULL", "NULL", "NULL", "NEGATIVE", "NULL", "NULL"
    ], "route classifications")
    for gate in gates:
        require(gate["finite_end_to_end_denominator"] is False, "route denominator gate")
        require(gate["bounded_strict_decrease_chain"] is False, "route decrease gate")

    effect = result["obligation_effect"]
    require(effect["closed"] == [], "closed obligation")
    require(effect["narrowed_load_bearing"] == [], "narrowed obligation")
    require(len(effect["unchanged_open"]) == 7, "unchanged obligation count")
    require(effect["ledger_delta"] == "0/9", "ledger delta")
    require(effect["certified_residual_delta"] == 0, "residual delta")

    vectors = result["vectors"]
    require(vectors["opening"][-2:] == [4, 7], "opening streak vector")
    require(vectors["midpoint"] == vectors["opening"], "midpoint vector")
    require(vectors["recommended_closing"][-2:] == [5, 8], "closing streak vector")
    require(result["minimum_decrease_reachable_at_midpoint"] is False, "midpoint stop")
    require(result["overall_handoff"] == "NULL", "overall handoff")
    require(result["trajectory"] == "STALLED", "trajectory")
    require(result["tournament_winner"] == "NONE", "winner")
    require(result["successor_eligible"] is False, "successor")
    require(result["recommended_strategy_verdict"] == "STOP", "strategy verdict")
    require(result["construction_started"] is False, "construction")
    require(result["ledger_edit_authorized"] is False, "ledger authority")


def validate_manifest(manifest: dict, check_files: bool = True) -> None:
    require(manifest["scientific_base_commit"] == BASE, "manifest base")
    require(manifest["scientific_base_tree"] == BASE_TREE, "manifest base tree")
    require(manifest["lane_opening_commit"] == OPENING, "manifest opening")
    require(manifest["lane_opening_tree"] == OPENING_TREE, "manifest opening tree")
    independence = manifest["independence"]
    require(independence == {
        "producer_surfaces_read": False,
        "falsifier_surfaces_read": False,
        "acceptance_logic_imported": False,
        "network_used": False,
        "connector_used": False,
    }, "independence declaration")
    require(len(manifest["sources"]) >= 18, "source count")
    if check_files:
        for relative, expected in manifest["sources"].items():
            path = ROOT / relative
            require(path.is_file(), f"missing source {relative}")
            require(sha256(path) == expected, f"source drift {relative}")


def hostile_mutations(result: dict, manifest: dict) -> int:
    mutations = []

    def mutate_result(path, value):
        candidate = copy.deepcopy(result)
        cursor = candidate
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value
        mutations.append((validate_result, candidate))

    mutate_result(["scientific_base_tree"], "0" * 40)
    mutate_result(["opening_reconstruction", "ledger"], "3/9")
    mutate_result(["opening_reconstruction", "open_load_bearing_obligations"], 6)
    mutate_result(["opening_reconstruction", "pair_residual"], 0)
    mutate_result(["triple_accounting", "source_orbits"], 79102448)
    mutate_result(["triple_accounting", "settled_orbits"], 77940148)
    mutate_result(["triple_accounting", "source_order_residual_semantic_sha256"], "0" * 64)
    mutate_result(["triple_accounting", "closes_diag3_alone"], True)
    mutate_result(["joined_clause_rebaseline", "face_type_denominator"], 9)
    mutate_result(["joined_clause_rebaseline", "universally_credited"], ["(0)", "(1)", "(2)", "(1,0,0)"])
    mutate_result(["joined_clause_rebaseline", "global_cell_coverage_proved"], True)
    mutate_result(["route_gates", 0, "classification"], "POSITIVE")
    mutate_result(["route_gates", 3, "classification"], "POSITIVE")
    mutate_result(["obligation_effect", "closed"], ["diag3_triple_hc0"])
    mutate_result(["obligation_effect", "ledger_delta"], "1/9")
    mutate_result(["minimum_decrease_reachable_at_midpoint"], True)
    mutate_result(["tournament_winner"], "D3_JOINED_GORDAN_TEN_CLAUSE_THEOREM")
    mutate_result(["successor_eligible"], True)
    mutate_result(["construction_started"], True)

    bad_manifest = copy.deepcopy(manifest)
    bad_manifest["independence"]["producer_surfaces_read"] = True
    mutations.append((lambda value: validate_manifest(value, check_files=False), bad_manifest))

    rejected = 0
    for validator, candidate in mutations:
        try:
            validator(candidate)
        except (AssertionError, KeyError, TypeError):
            rejected += 1
        else:
            raise AssertionError("hostile mutation accepted")
    return rejected


def main() -> None:
    result = load(RESULT_PATH)
    manifest = load(MANIFEST_PATH)
    validate_result(result)
    validate_manifest(manifest)
    require(git("rev-parse", f"{BASE}^{{tree}}") == BASE_TREE, "git base tree")
    require(git("rev-parse", f"{OPENING}^{{tree}}") == OPENING_TREE, "git opening tree")
    subprocess.check_call(["git", "merge-base", "--is-ancestor", OPENING, "HEAD"], cwd=ROOT)
    rejected = hostile_mutations(result, manifest)
    require(rejected >= 12, "hostile count")
    print("PASS independent theorem-reset verifier")
    print(f"PASS source pins {len(manifest['sources'])}/{len(manifest['sources'])}")
    print(f"PASS hostile mutations rejected {rejected}/{rejected}")
    print("PASS joined universal credit 3/10; not end-to-end D3")
    print("PASS triple 77940147/79102449 residual 1162302; pair remains UNKNOWN")
    print("NULL no route passes attachment+denominator+bounded-decrease")
    print("STALLED winner=NONE successor_eligible=false ledger_delta=0/9")


if __name__ == "__main__":
    main()
