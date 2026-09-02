#!/usr/bin/env python3
"""Fail-closed opening audit for the explicit trihomogenized chart gate."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import itertools
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
AUDIT = HERE / "OPENING_AUDIT.json"
BASE = "4aee0aac6e80d053cf1751eac766280873656909"
BASE_TREE = "bfaff6f29b032ef6f81fa11a97063b01d74db8f7"
OPENING = "cd2d856d3ccff51f7b5d6841702b25d191ed9985"
OPENING_TREE = "6014474550142ec47f9280a123dc77bf403d1d0a"
BRANCH = "research/local-d9-factor19069-explicit-trihom-jacobian-chart-gate1-20260901"
TARGET = "D9_ROW2599_FACTOR19069_EXPLICIT_TRIHOMOGENIZED_JACOBIAN_CHART_DECOMPOSITION_GATE1"
CYCLE_ID = "2026-09-01-d9-row2599-factor19069-explicit-trihom-jacobian-chart-gate1"
PREDECESSOR = (
    ROOT / "ops" / "team" / "d9-factor19069-singular-df-multihomogeneous-constructor"
    / "SINGULAR_DF_MULTIHOMOGENEOUS_FRONTIER.json"
)
OPENING_DOCS = {
    "CYCLE.md": "4f0f6841c483a0832e39b170eb1e5c041cabc214f5733f5a21b81ee849b58dba",
    "WORK_ORDERS.yaml": "b501084a2c5f2e8f7be24c446a0d7d20729d4689076a5316fca4c81a1b42caad",
    "OBLIGATION_GRAPH.json": "aedd5404ead4d36498da8a63e21d71f45a018ed2e6d2c14ea11300744545b9be",
    "OPENING_AUDIT.json": "e513ef2f63f616cd06d3d5a27884a9919077ea1044132970de1d9691d09bbb55",
}


class Reject(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def git(*arguments: str, binary: bool = False):
    result = subprocess.check_output(
        ["git", "-c", f"safe.directory={ROOT.as_posix()}", *arguments],
        cwd=ROOT,
        text=not binary,
    )
    return result if binary else result.strip()


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def frozen_bytes(revision: str, path: str) -> bytes:
    return git("show", f"{revision}:{path}", binary=True)


def validate(candidate: dict) -> None:
    require(candidate["format"] == "d9-factor19069-explicit-trihom-jacobian-chart-opening-audit-v1", "format")
    require(candidate["cycle_id"] == CYCLE_ID, "cycle")
    require(candidate["base_revision"] == BASE, "base revision")
    require(candidate["base_tree"] == BASE_TREE, "base tree")
    require(candidate["successor_branch"] == BRANCH, "branch")
    require(candidate["opening_ledger"] == "2/9", "ledger")
    require(candidate["predecessor_verdict"] == "PIVOT", "predecessor verdict")
    require(candidate["selected_target"] == TARGET, "target")
    require(candidate["selected_count"] == 1, "selected count")
    require(candidate["concurrent_authoritative_cycles"] == [], "concurrent cycles")
    debt = candidate["inherited_protocol_debt"]
    require(debt["repository_wide_verifier_status"] == "PREEXISTING_FAILURE_OUTSIDE_SELECTED_CYCLE", "protocol debt status")
    require(debt["current_protocol_pinned_and_selected_cycle_audited"] is True, "selected protocol audit")

    target = candidate["target"]
    require(target["parent_index"] == 2599, "parent")
    require(target["factor_id"] == 19069, "factor")
    require(target["projective_ambient"] == "P3_x_P3_x_P3", "ambient")
    require(target["homogeneous_ring"] == "Q[a,b,c,u,d,e,f,v,g,h,i,w]", "ring")
    require(target["homogeneous_blocks"] == [["a", "b", "c", "u"], ["d", "e", "f", "v"], ["g", "h", "i", "w"]], "blocks")
    require(target["multidegree"] == [2, 2, 2], "multidegree")
    require(target["standard_chart_count"] == 64, "chart count")
    require(target["free_coordinates_per_chart"] == 9, "free coordinates")
    require(target["chart_jacobian_generators"] == 10, "chart generators")
    require(target["affine_chart"] == ["u", "v", "w"], "affine chart")
    require(target["verified_wall_term_count"] == 108, "source terms")
    require(target["parent_sign_factors"] == 70, "parent factors")
    for field in (
        "requires_all_infinity_charts",
        "requires_euler_chart_transfer",
        "requires_characteristic_zero_decomposition",
        "requires_embedded_component_accounting",
        "requires_chart_overlap_accounting",
        "requires_affine_contraction_before_parent_tests",
        "requires_componentwise_parent_factor_saturation",
        "requires_positive_dimensional_real_residence",
        "requires_connected_parent_component_tags",
        "trihomogenization_is_not_a_decomposition_certificate",
        "affine_source_is_not_homogeneous_or_multiaffine",
    ):
        require(target[field] is True, field)
    require(target["positive_endpoint"].startswith("EXACT_SINGULAR_EMPTINESS"), "positive endpoint")
    require(target["negative_endpoint"].startswith("EXACT_POSITIVE_DIMENSIONAL"), "negative endpoint")
    require(target["null_endpoint"].startswith("FIRST_SOURCE_PINNED"), "null endpoint")
    require(target["timeout_endpoint"].startswith("HASH_PIN_ALL_COMPLETED"), "timeout endpoint")

    ceiling = candidate["resource_ceiling"]
    require(ceiling["wall_minutes"] == 120, "wall ceiling")
    require(ceiling["aggregate_cpu_hours"] == 8, "cpu ceiling")
    require(ceiling["max_exact_algebra_component_nodes"] == 500000, "node ceiling")
    require(ceiling["paid_external_compute"] is False, "paid compute")
    require(len(candidate["prohibited_routes"]) == 10, "prohibited route census")
    require("SEVENTY_INVERSE_VARIABLE_DISCOVERY_ROUTE" in candidate["prohibited_routes"], "inverse route")
    require("NUMERICAL_OR_MODULAR_PROBE_PROMOTION" in candidate["prohibited_routes"], "probe route")
    durable = candidate["durable_checkpoint"]
    require(durable["project_root"] == r"E:\Projects\9DVL Research", "project root")
    require(durable["drive_connector_used"] is False, "connector")
    require(durable["drive_mirror_optional"] is True, "optional mirror")
    require(durable["github_write"] is False, "GitHub write")


def validate_source(candidate: dict) -> None:
    predecessor = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    require(predecessor["theorem_ledger"] == "2/9", "predecessor ledger")
    require(predecessor["outcome"] == "pass", "predecessor artifact outcome")
    require(predecessor["endpoint"].startswith("HASH_PIN_FIRST_UNRESOLVED"), "predecessor null endpoint")
    source = predecessor["exact_affine_source_structure"]
    require(source["term_count"] == 108, "predecessor source term count")
    require(source["affine_block_homogeneous_of_degree_2_2_2"] is False, "false affine homogeneity retained")
    require(source["affine_multiaffine"] is False, "false multiaffinity retained")
    tri = source["canonical_trihomogenization"]
    require(tri["ring"] == candidate["target"]["homogeneous_ring"], "trihom ring")
    require(tri["block_degree"] == [2, 2, 2], "trihom degree")
    require(tri["term_count"] == len(tri["terms"]) == 108, "trihom terms")
    require(tri["not_used_as_a_decomposition_certificate"] is True, "nonconsequence")
    for term in tri["terms"]:
        exponents = term["exponents_a_b_c_d_e_f_g_h_i"]
        homogenizers = term["homogenizer_exponents_u_v_w"]
        require(sum(exponents[0:3]) + homogenizers[0] == 2, "abc/u degree")
        require(sum(exponents[3:6]) + homogenizers[1] == 2, "def/v degree")
        require(sum(exponents[6:9]) + homogenizers[2] == 2, "ghi/w degree")
    charts = list(itertools.product(range(4), repeat=3))
    require(len(charts) == len(set(charts)) == 64, "chart cover")
    require((3, 3, 3) in charts, "affine chart present")
    require(sum(chart != (3, 3, 3) for chart in charts) == 63, "non-affine charts")


def validate_pins(candidate: dict) -> None:
    for path, expected in candidate["pins"].items():
        require(digest(frozen_bytes(BASE, path)) == expected, f"pin drift: {path}")
    prefix = f"ops/research-team/cycles/{CYCLE_ID}/"
    for name, expected in OPENING_DOCS.items():
        require(digest(frozen_bytes(OPENING, prefix + name)) == expected, f"opening document drift: {name}")


def hostile_mutations(stored: dict) -> int:
    mutations = []
    def changed(path, value):
        item = deepcopy(stored)
        target = item
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        mutations.append(item)
    changed(["base_revision"], "0" * 40)
    changed(["base_tree"], "0" * 40)
    changed(["opening_ledger"], "3/9")
    changed(["selected_count"], 2)
    changed(["concurrent_authoritative_cycles"], ["fake"])
    changed(["target", "factor_id"], 19068)
    changed(["target", "homogeneous_ring"], "Q[a,b,c,d,e,f,g,h,i]")
    changed(["target", "homogeneous_blocks"], [["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]])
    changed(["target", "multidegree"], [2, 2, 1])
    changed(["target", "standard_chart_count"], 63)
    changed(["target", "free_coordinates_per_chart"], 12)
    changed(["target", "chart_jacobian_generators"], 13)
    changed(["target", "affine_chart"], ["a", "v", "w"])
    changed(["target", "verified_wall_term_count"], 107)
    changed(["target", "parent_sign_factors"], 69)
    changed(["target", "requires_all_infinity_charts"], False)
    changed(["target", "requires_euler_chart_transfer"], False)
    changed(["target", "requires_affine_contraction_before_parent_tests"], False)
    changed(["target", "trihomogenization_is_not_a_decomposition_certificate"], False)
    changed(["target", "affine_source_is_not_homogeneous_or_multiaffine"], False)
    changed(["resource_ceiling", "max_exact_algebra_component_nodes"], 500001)
    changed(["durable_checkpoint", "drive_connector_used"], True)
    changed(["durable_checkpoint", "github_write"], True)
    changed(["inherited_protocol_debt", "current_protocol_pinned_and_selected_cycle_audited"], False)
    altered = deepcopy(stored); altered["prohibited_routes"].remove("SEVENTY_INVERSE_VARIABLE_DISCOVERY_ROUTE"); mutations.append(altered)
    altered = deepcopy(stored); altered["pins"]["ops/research-team/PROTOCOL.md"] = "0" * 64; mutations.append(altered)
    for index, mutation in enumerate(mutations):
        try:
            validate(mutation)
            validate_pins(mutation)
        except (Reject, KeyError):
            continue
        raise Reject(f"hostile mutation accepted: {index}")
    return len(mutations)


def main() -> None:
    stored = json.loads(AUDIT.read_text(encoding="utf-8"))
    require(git("rev-parse", f"{BASE}^{{commit}}") == BASE, "base commit")
    require(git("rev-parse", f"{BASE}^{{tree}}") == BASE_TREE, "base tree")
    require(git("rev-parse", f"{OPENING}^{{commit}}") == OPENING, "opening commit")
    require(git("rev-parse", f"{OPENING}^{{tree}}") == OPENING_TREE, "opening tree")
    require(git("branch", "--show-current") == BRANCH, "current branch")
    validate(stored)
    validate_source(stored)
    validate_pins(stored)
    count = hostile_mutations(stored)
    print("PASS explicit trihomogenized Jacobian-chart gate-1 opening audit")
    print(f"base={BASE[:8]} tree={BASE_TREE[:8]} opening={OPENING[:8]} charts=64 source_terms=108 parents=70")
    print(f"opening_hostile_mutations={count} ledger=2/9 drive_connector=false github_write=false")


if __name__ == "__main__":
    main()
