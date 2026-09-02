#!/usr/bin/env python3
"""Fail-closed opening audit for factor-19069 singular-df gate 1."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
AUDIT = HERE / "OPENING_AUDIT.json"
BASE = "9c9a78c4225a39803a0a5ac7e4e204d9b9f3773d"
TREE = "af4bdbfc8f89e950936d59e6b0737b12eb5bdfb5"
OPENING = "a2860f3f6436f573a913fc8ca6312b944212aadd"
OPENING_TREE = "56f179cea8b8664156ee2dfcd6a9052d95e3b78e"
TARGET = "D9_ROW2599_FACTOR19069_SINGULAR_DF_MULTIHOMOGENEOUS_DECOMPOSITION_GATE1"
BRANCH = "research/local-d9-factor19069-singular-df-multihomogeneous-gate1-20260901"
GROUPS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))


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


def frozen_bytes(path: str) -> bytes:
    return git("show", f"{BASE}:{path}", binary=True)


def validate(candidate: dict) -> None:
    require(candidate["format"] == "d9-factor19069-singular-df-multihomogeneous-opening-audit-v1", "format")
    require(candidate["base_revision"] == BASE, "base revision")
    require(candidate["base_tree"] == TREE, "base tree")
    require(candidate["successor_branch"] == BRANCH, "successor branch")
    require(candidate["opening_ledger"] == "2/9", "ledger")
    require(candidate["predecessor_verdict"] == "PIVOT", "predecessor verdict")
    require(candidate["selected_target"] == TARGET, "target")
    require(candidate["selected_count"] == 1, "selected count")
    require(candidate["concurrent_authoritative_cycles"] == [], "concurrent cycles")
    target = candidate["target"]
    require(target["parent_index"] == 2599, "parent")
    require(target["factor_id"] == 19069, "factor")
    require(target["ambient_parameter_dimension"] == 9, "ambient dimension")
    require(target["original_ring"] == "Q[a,b,c,d,e,f,g,h,i]", "original ring")
    require(target["verified_wall_term_count"] == 108, "wall terms")
    require(target["verified_total_degree"] == 6, "wall degree")
    require(target["source_block_partition"] == [["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]], "blocks")
    require(target["source_multidegree"] == [2, 2, 2], "multidegree bound")
    require(target["source_multiaffine_claim_requires_exact_check"] is True, "multiaffine check")
    require(target["parent_sign_factors"] == 70, "parent factors")
    for field in (
        "requires_characteristic_zero_decomposition",
        "requires_all_component_equations",
        "requires_embedded_component_accounting",
        "requires_dimensions_degrees_multiplicities_where_feasible",
        "requires_componentwise_parent_factor_saturation",
        "requires_positive_dimensional_real_residence",
        "requires_singular_and_boundary_strata",
        "requires_connected_parent_component_tags",
    ):
        require(target[field] is True, field)
    require(target["positive_endpoint"].startswith("PROVE_SINGULAR_BRANCH_EMPTY"), "positive endpoint")
    require(target["negative_endpoint"].startswith("EXHIBIT_EXACT_POSITIVE_DIMENSIONAL_REAL_SINGULAR_COMPONENT"), "negative endpoint")
    require(target["null_endpoint"].startswith("HASH_PIN_FIRST_UNRESOLVED_MULTIHOMOGENEOUS"), "null endpoint")
    require(target["timeout_endpoint"].startswith("HASH_PIN_COMPLETED_AND_PENDING"), "timeout endpoint")
    ceiling = candidate["resource_ceiling"]
    require(ceiling["wall_minutes"] == 120, "wall ceiling")
    require(ceiling["aggregate_cpu_hours"] == 8, "cpu ceiling")
    require(ceiling["max_exact_algebra_component_nodes"] == 500000, "node ceiling")
    require(ceiling["paid_external_compute"] is False, "paid compute")
    require("SEVENTY_INVERSE_VARIABLE_DISCOVERY_ROUTE" in candidate["prohibited_routes"], "inverse route")
    require("NUMERICAL_OR_MODULAR_PROBE_PROMOTION" in candidate["prohibited_routes"], "probe route")
    durable = candidate["durable_checkpoint"]
    require(durable["project_root"] == r"E:\Projects\9DVL Research", "project root")
    require(durable["local_output_root"] == r"E:\Projects\9DVL Research\outputs", "output root")
    require(durable["drive_connector_used"] is False, "Drive connector")
    require(durable["github_write"] is False, "GitHub write")


def hostile_mutations(stored: dict) -> int:
    mutations = []

    def add(path, value, marker):
        candidate = deepcopy(stored)
        cursor = candidate
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value
        mutations.append((candidate, marker))

    add(["base_revision"], "0" * 40, "base revision")
    add(["base_tree"], "0" * 40, "base tree")
    add(["successor_branch"], BRANCH + "-drift", "successor branch")
    add(["opening_ledger"], "3/9", "ledger")
    add(["selected_count"], 2, "selected count")
    add(["concurrent_authoritative_cycles"], ["unknown"], "concurrent cycles")
    add(["target", "factor_id"], 19068, "factor")
    add(["target", "original_ring"], "Q[a,b]", "original ring")
    add(["target", "verified_wall_term_count"], 107, "wall terms")
    add(["target", "source_multidegree"], [2, 2, 1], "multidegree bound")
    add(["target", "source_multiaffine_claim_requires_exact_check"], False, "multiaffine check")
    add(["target", "parent_sign_factors"], 69, "parent factors")
    add(["target", "requires_characteristic_zero_decomposition"], False, "requires_characteristic_zero_decomposition")
    add(["target", "requires_embedded_component_accounting"], False, "requires_embedded_component_accounting")
    add(["target", "requires_componentwise_parent_factor_saturation"], False, "requires_componentwise_parent_factor_saturation")
    add(["target", "requires_positive_dimensional_real_residence"], False, "requires_positive_dimensional_real_residence")
    add(["resource_ceiling", "max_exact_algebra_component_nodes"], 500001, "node ceiling")
    add(["resource_ceiling", "paid_external_compute"], True, "paid compute")
    add(["durable_checkpoint", "drive_connector_used"], True, "Drive connector")
    add(["durable_checkpoint", "github_write"], True, "GitHub write")
    for candidate, marker in mutations:
        try:
            validate(candidate)
        except Reject as error:
            require(marker in str(error), f"wrong hostile rejection: {error}")
            continue
        raise Reject(f"hostile mutation accepted: {marker}")
    return len(mutations)


def source_census() -> tuple[list[list[int]], list[int], list[int]]:
    frontier = json.loads(
        frozen_bytes("ops/team/d9-factor19069-critical-equidim-constructor/CRITICAL_EQUIDIM_FRONTIER.json")
    )
    wall = frontier["factor_circuit"]["wall_polynomial"]
    require(wall["node_id"] == "f_19069", "source wall id")
    require(wall["term_count"] == len(wall["sparse_polynomial"]) == 108, "source wall census")
    terms = wall["sparse_polynomial"]
    total_degrees = sorted({sum(term["exponents"]) for term in terms})
    block_degrees = [
        sorted({sum(term["exponents"][index] for index in group) for term in terms})
        for group in GROUPS
    ]
    variable_maxima = [max(term["exponents"][index] for term in terms) for index in range(9)]
    require(max(total_degrees) == 6, "source total degree")
    require([max(values) for values in block_degrees] == [2, 2, 2], "source multidegree bound")
    return block_degrees, variable_maxima, total_degrees


def main() -> None:
    require(git("rev-parse", f"{BASE}^{{commit}}") == BASE, "base commit")
    require(git("rev-parse", f"{BASE}^{{tree}}") == TREE, "base tree")
    require(git("rev-parse", f"{OPENING}^{{commit}}") == OPENING, "opening commit")
    require(git("rev-parse", f"{OPENING}^{{tree}}") == OPENING_TREE, "opening tree")
    require(git("branch", "--show-current") == BRANCH, "current branch")
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    validate(audit)
    for path, expected in audit["pins"].items():
        require(sha256(frozen_bytes(path)).hexdigest() == expected, f"source pin {path}")
    canonical = json.loads(frozen_bytes("ai/omreal/data/CANONICAL_RESEARCH_STATE_V6.json"))
    require(canonical["theorem"]["score"] == "2/9", "canonical ledger")
    require(canonical["theorem"]["proved_diagonals"] == [1, 2], "proved diagonals")
    report = frozen_bytes(
        "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-critical-equidim-gate1/CYCLE_REPORT.md"
    ).decode("utf-8")
    require(TARGET in report, "predecessor successor")
    block_degrees, variable_maxima, total_degrees = source_census()
    count = hostile_mutations(audit)
    print("PASS D9 factor-19069 singular-df multihomogeneous gate-1 opening audit")
    print(f"base={BASE[:8]} tree={TREE[:8]} opening={OPENING[:8]} source_terms=108 parents=70")
    print(f"block_degree_sets={block_degrees} variable_maxima={variable_maxima} total_degrees={total_degrees}")
    print(f"opening_hostile_mutations={count} ledger=2/9 drive_connector=false github_write=false")


if __name__ == "__main__":
    main()
