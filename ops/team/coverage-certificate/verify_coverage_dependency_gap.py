#!/usr/bin/env python3
"""Independent fail-closed verifier for the row-2599 coverage gap record.

This file intentionally does not import the generator or discovery-side
modules.  It authenticates the accepted source artifacts, reconstructs the
decisive accounting from their public records, enforces nonconsequences, and
tests re-sealed semantic attacks.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[3]
BASE_REVISION = "ec362dba8a912bc4749c004641aee2da0a88dc05"
CERT = Path(__file__).with_name("ROW2599_COVERAGE_DEPENDENCY_GAP.json")
FORMAT = "diag3-row2599-component-coverage-dependency-gap-v1"
PREFIX = b"diag3-row2599-component-coverage-dependency-gap-v1\0"
EXPECTED_INPUTS = {
    "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json":
        "7922d769aa30a84c5d208dec92d2e78d5c7744cc6184ea1d42aaeadf947761b3",
    "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json":
        "19248dd148d1fd002931ed5f48197869dd42c68a513376e1a4d6941389bda307",
    "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON_EDGE27_EDGE39.json":
        "dcb707220df3e61b1a94eeedcf8e46b6602f30d405f4a92fc542c0f52f672806",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json":
        "fb73899be7ff4aed5739b7f6a999d623db2a0504f212d5fe5aba35e1df1b1465",
    "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_COMPONENT_COLLAR.json":
        "5930cc19019470fdfdf55d67523f6c4211ccf5b540f5c2bb5df36c64db75d7bd",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin":
        "adb2e7257457f158e809450683c46fe7ecafdbdd4a7efdf9ac630e8a4f0fb03f",
    "ops/team/edge39-prover/EDGE39_EXACT_ROADMAP.json":
        "cd4cc32efc2d71a609a01b2747e5d6230b7115a7ee23423b6a3175a71a1cf6c1",
}
REQUIRED_GAPS = {
    "factor_disposition",
    "component_quotient",
    "skeleton_hit_map",
    "frontier_balance",
    "ambient_exclusion",
}


class Reject(Exception):
    pass


def need(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def pinned_bytes(relative: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{BASE_REVISION}:{relative}"],
        cwd=ROOT,
    )


def pinned_digest(relative: str) -> str:
    return hashlib.sha256(pinned_bytes(relative)).hexdigest()


def read(relative: str) -> dict:
    return json.loads(pinned_bytes(relative))


def semantic_digest(record: dict) -> str:
    body = dict(record)
    body.pop("semantic_sha256", None)
    return hashlib.sha256(PREFIX + canonical(body)).hexdigest()


def reseal(record: dict) -> dict:
    record["semantic_sha256"] = semantic_digest(record)
    return record


def validate(record: dict, authenticate_files: bool = True) -> str:
    need(record.get("format") == FORMAT, "format")
    need(record.get("status") == "INCOMPLETE_DEPENDENCY_GAP", "status")
    need(record.get("base_revision") == "ec362dba8a912bc4749c004641aee2da0a88dc05", "base")
    need(record.get("inputs") == EXPECTED_INPUTS, "complete pinned input manifest")
    need(record.get("semantic_sha256") == semantic_digest(record), "semantic seal")
    if authenticate_files:
        for relative, expected in EXPECTED_INPUTS.items():
            need(pinned_digest(relative) == expected, f"file digest {relative}")

    scope = record.get("scope", {})
    need(scope == {
        "ambient_parameter_dimension": 9,
        "global_parent_cell_coverage": "NOT_CERTIFIED",
        "honest_9dvl_score": "2/9_UNCHANGED",
        "parent_index": 2599,
        "relative_escape_coverage": "NOT_CERTIFIED",
        "support": [15, 15, 15],
        "wall_component_coverage": "NOT_CERTIFIED",
    }, "scope/nonconsequences")

    ledger = read("ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json")
    cover = read("ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json")
    skeleton = read(
        "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON_EDGE27_EDGE39.json"
    )
    closure = read("ai/omreal/data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json")
    collar = read("ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_COMPONENT_COLLAR.json")
    edge39 = read("ops/team/edge39-prover/EDGE39_EXACT_ROADMAP.json")

    row = ledger["row2599_fullsupport_ledger"]
    expected_accounting = {
        "candidate_factor_count": row["fullsupport_factor_count"],
        "known_strict_interior_nonempty_factor_count": row["exact_interior_nonempty_count"],
        "known_strict_interior_empty_factor_count": row["exact_empty_count"],
        "unresolved_feasibility_factor_count": row["unresolved_feasibility_count"],
        "maximum_current_active_wall_count": row["master_generator_active_wall_upper_bound"],
        "empty_factor_ids_sha256": row["digests"]["empty_factor_ids"],
        "unresolved_factor_ids_sha256": row["digests"]["unresolved_factor_ids"],
        "selected_source_edge_count": 40,
        "compiled_source_edge_indices": [27, 39],
        "pending_source_edge_count": 38,
        "crossed_factor_classes_covered_by_selected_edges": 10_844,
    }
    need(record.get("exact_accounting") == expected_accounting, "exact source accounting")
    need(sum(expected_accounting[key] for key in (
        "known_strict_interior_nonempty_factor_count",
        "known_strict_interior_empty_factor_count",
        "unresolved_feasibility_factor_count",
    )) == expected_accounting["candidate_factor_count"], "factor partition")

    selected = cover["source_bank"]["selected_edge_indices"]
    compiled = skeleton["scope"]["fully_compiled_cover_edges"]
    pending = skeleton["scope"]["pending_cover_edges"]
    need(len(selected) == 40 and sorted(compiled + pending) == selected, "edge partition")
    need(cover["scope"]["component_coverage"] == "NOT_CLAIMED", "cover component scope")
    need(skeleton["scope"]["component_coverage"] == "NOT_CLAIMED", "skeleton component scope")

    first = record.get("first_decisive_gap", {})
    need(first.get("id") == "unclassified_factor_feasibility", "first gap id")
    need(first.get("missing_count") == 5_803, "first gap count")
    need("cannot close global coverage" in first.get("consequence", ""), "first gap consequence")

    blocks = record.get("required_global_blocks", [])
    need({block.get("id") for block in blocks} == REQUIRED_GAPS, "global blocks")
    need(len(blocks) == len(REQUIRED_GAPS), "duplicate global blocks")

    contract = record.get("boundary_tag_contract", {})
    allowed = contract.get("allowed_in_global_complete")
    forbidden = contract.get("forbidden_in_global_complete")
    need(allowed == [
        "INTERNAL_CONTINUATION",
        "CHART_SEAM",
        "GENUINE_RELATIVE_PARENT_FACE",
        "GENUINE_RELATIVE_PARENT_INFINITY",
    ], "allowed boundary tags")
    need(forbidden == ["ARTIFICIAL_SCOPE_FRONTIER", "UNCLASSIFIED_FRONTIER"],
         "forbidden boundary tags")

    pilot = record.get("local_pilot", {})
    source_component = collar["component_coverage"]
    need(pilot.get("status") == "EXACT_LOCAL_SCHEMA_PILOT_ONLY", "pilot status")
    need(pilot.get("factor_id") == source_component["factor_id"] == 19069, "pilot factor")
    need(pilot.get("declared_scope_component_count") ==
         source_component["declared_scope_component_count"] == 1, "pilot component count")
    need(pilot.get("source_skeleton_hits") == [source_component["retained_skeleton_cell"]],
         "pilot source hit")
    need(pilot.get("frontier") == [
        {"cell_id": "w_minus", "tag": "ARTIFICIAL_SCOPE_FRONTIER"},
        {"cell_id": "w_plus", "tag": "ARTIFICIAL_SCOPE_FRONTIER"},
    ], "pilot artificial frontier")
    need(pilot.get("genuine_relative_escapes") == [], "pilot relative escapes")
    need(pilot.get("components_outside_declared_scope") == "UNTESTED", "pilot outer scope")
    need(pilot.get("global_acceptance") is False, "pilot global nonacceptance")
    need(collar["scope"]["global_parent_cell_coverage"] == "NOT_CLAIMED", "collar scope")

    observations = closure["observations"]
    need((observations["certified_global_strict_closure_pairs"],
          observations["certified_global_strict_closure_triples"],
          observations["certified_parent_infinity_cells"]) == (0, 0, 0), "closure deficit")

    resource = record.get("row2599_resource_estimate", {})
    degree_census = edge39["factor_census"]["degree_census"]
    need(resource.get("candidate_degree_census") == degree_census, "degree census")
    bezout = sum(
        int(count) * int(degree) * (int(degree) - 1) ** 8
        for degree, count in degree_census.items() if int(degree) >= 2
    )
    need(bezout == 2_732_978_444, "independent Bezout arithmetic")
    need(resource.get("generic_dense_projection_critical_bezout_sum") == bezout,
         "resource bound")

    need("honest 9DVL score remain unchanged" in record.get("theorem_effect", ""),
         "theorem nonconsequence")
    return "ACCEPTED_EXACT_NULL"


def rejected(record: dict) -> bool:
    try:
        validate(reseal(record), authenticate_files=False)
    except Reject:
        return True
    return False


def run_canaries(record: dict) -> None:
    # Positive and null: exact local pilot is usable, but only the null result is global.
    need(validate(record) == "ACCEPTED_EXACT_NULL", "positive/null base")

    mutations = []
    altered = deepcopy(record); altered["status"] = "GLOBAL_COMPLETE"; mutations.append(altered)
    altered = deepcopy(record); altered["scope"]["global_parent_cell_coverage"] = "CERTIFIED"; mutations.append(altered)
    altered = deepcopy(record); altered["scope"]["honest_9dvl_score"] = "3/9"; mutations.append(altered)
    altered = deepcopy(record); altered["exact_accounting"]["unresolved_feasibility_factor_count"] = 0; mutations.append(altered)
    altered = deepcopy(record); altered["exact_accounting"]["pending_source_edge_count"] = 0; mutations.append(altered)
    altered = deepcopy(record); altered["inputs"].pop(next(iter(altered["inputs"]))); mutations.append(altered)
    altered = deepcopy(record); altered["required_global_blocks"].pop(); mutations.append(altered)
    altered = deepcopy(record); altered["local_pilot"]["declared_scope_component_count"] = 2; mutations.append(altered)
    altered = deepcopy(record); altered["local_pilot"]["frontier"][0]["tag"] = "GENUINE_RELATIVE_PARENT_INFINITY"; mutations.append(altered)
    altered = deepcopy(record); altered["local_pilot"]["global_acceptance"] = True; mutations.append(altered)
    altered = deepcopy(record); altered["row2599_resource_estimate"]["generic_dense_projection_critical_bezout_sum"] -= 1; mutations.append(altered)

    need(all(rejected(item) for item in mutations), "hostile canary escaped")
    print("PASS positive local factor-19069 schema pilot (scope remains local)")
    print("PASS null dependency-gap certificate accepted without theorem promotion")
    print("PASS negative GLOBAL_COMPLETE claim rejected")
    print(f"PASS {len(mutations) - 1} additional re-sealed hostile mutations rejected")


def main() -> None:
    record = json.loads(CERT.read_text())
    run_canaries(record)
    accounting = record["exact_accounting"]
    print("PASS exact factors",
          accounting["known_strict_interior_nonempty_factor_count"], "+",
          accounting["known_strict_interior_empty_factor_count"], "+",
          accounting["unresolved_feasibility_factor_count"], "=",
          accounting["candidate_factor_count"])
    print("DECISIVE_GAP 5803 unresolved factor dispositions; no global component quotient")
    print("SCOPE no ledger edit; pair obligation open; honest 9DVL score 2/9")


if __name__ == "__main__":
    main()
