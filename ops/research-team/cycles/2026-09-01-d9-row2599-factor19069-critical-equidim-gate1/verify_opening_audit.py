#!/usr/bin/env python3
"""Fail-closed opening audit for factor-19069 critical equidimensional gate 1."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
AUDIT = HERE / "OPENING_AUDIT.json"
BASE = "f196f949b2a2981ea1b21019e4a2bf56302a683a"
TREE = "7a5eaa91d1448defed2e77363b5e97cf93b97489"
TARGET = "D9_ROW2599_FACTOR19069_FACTORED_CRITICAL_EQUIDIMENSIONAL_DECOMPOSITION_GATE1"
BRANCH = "research/local-d9-factor19069-factored-critical-equidim-gate1-20260901"


class Reject(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def git(*arguments: str, binary: bool = False):
    result = subprocess.check_output(["git", *arguments], cwd=ROOT, text=not binary)
    return result if binary else result.strip()


def frozen_bytes(path: str) -> bytes:
    return git("show", f"{BASE}:{path}", binary=True)


def validate(candidate: dict) -> None:
    require(candidate["format"] == "d9-factor19069-critical-equidim-opening-audit-v1", "format")
    require(candidate["base_revision"] == BASE, "base revision")
    require(candidate["base_tree"] == TREE, "base tree")
    require(candidate["successor_branch"] == BRANCH, "successor branch")
    require(candidate["opening_ledger"] == "2/9", "ledger")
    require(candidate["predecessor_verdict"] == "PIVOT", "predecessor verdict")
    require(candidate["selected_target"] == TARGET, "selected target")
    require(candidate["selected_count"] == 1, "selected count")
    require(candidate["concurrent_authoritative_cycles"] == [], "concurrent cycles")
    target = candidate["target"]
    require(target["parent_index"] == 2599, "parent")
    require(target["factor_id"] == 19069, "factor")
    require(target["ambient_parameter_dimension"] == 9, "ambient dimension")
    require(target["parent_sign_factors"] == 70, "parent factor count")
    require(target["wedge_equations"] == 36, "wedge equation count")
    require(target["barrier_total_degree"] == 90, "barrier degree")
    require(target["barrier_representation"] == "UNEXPANDED_FACTORED_CIRCUIT", "barrier representation")
    require("infinity" in target["saturated_ideal"], "saturation")
    for field in (
        "requires_exact_saturation",
        "requires_equidimensional_decomposition",
        "requires_dimensions_degrees_multiplicities",
        "requires_positive_dimensional_real_residence",
        "requires_singular_and_boundary_strata",
        "requires_connected_parent_component_tags",
    ):
        require(target[field] is True, field)
    require(target["positive_endpoint"].startswith("PROVE_STRICT_CRITICAL_LOCUS_ZERO_DIMENSIONAL"), "positive endpoint")
    require(target["negative_endpoint"] == "EXHIBIT_EXACT_POSITIVE_DIMENSIONAL_REAL_CRITICAL_COMPONENT", "negative endpoint")
    require(target["null_endpoint"] == "HASH_PIN_FIRST_UNRESOLVED_SATURATED_IDEAL_BRANCH", "null endpoint")
    require(target["timeout_endpoint"].startswith("HASH_PIN_COMPLETED_AND_PENDING"), "timeout endpoint")
    ceiling = candidate["resource_ceiling"]
    require(ceiling["max_exact_algebra_component_nodes"] == 500000, "algebra ceiling")
    require(ceiling["paid_external_compute"] is False, "external compute")
    require(len(candidate["prohibited_routes"]) == 7, "prohibited routes")
    durable = candidate["durable_checkpoint"]
    require(durable["project_root"] == r"E:\Projects\9DVL Research", "durable root")
    require(durable["mounted_recovery_root"] == r"G:\My Drive\Projects\research-backups", "recovery root")
    require(durable["drive_connector_used"] is False, "Drive connector")
    require(durable["drive_mirror_optional"] is True, "optional mirror")
    require(durable["verify_length_and_sha256"] is True, "mirror verification")
    require(durable["github_write"] is False, "GitHub mode")


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
    add(["successor_branch"], BRANCH + "-drift", "successor branch")
    add(["opening_ledger"], "3/9", "ledger")
    add(["selected_count"], 2, "selected count")
    add(["concurrent_authoritative_cycles"], ["unknown"], "concurrent cycles")
    add(["target", "parent_sign_factors"], 69, "parent factor count")
    add(["target", "wedge_equations"], 35, "wedge equation count")
    add(["target", "barrier_representation"], "EXPANDED", "barrier representation")
    add(["target", "saturated_ideal"], "<f,wedge>", "saturation")
    add(["target", "requires_exact_saturation"], False, "requires_exact_saturation")
    add(["target", "requires_equidimensional_decomposition"], False, "requires_equidimensional_decomposition")
    add(["target", "requires_dimensions_degrees_multiplicities"], False, "requires_dimensions_degrees_multiplicities")
    add(["target", "requires_positive_dimensional_real_residence"], False, "requires_positive_dimensional_real_residence")
    add(["target", "requires_singular_and_boundary_strata"], False, "requires_singular_and_boundary_strata")
    add(["target", "requires_connected_parent_component_tags"], False, "requires_connected_parent_component_tags")
    add(["resource_ceiling", "paid_external_compute"], True, "external compute")
    add(["durable_checkpoint", "drive_connector_used"], True, "Drive connector")
    add(["durable_checkpoint", "github_write"], True, "GitHub mode")
    for candidate, marker in mutations:
        try:
            validate(candidate)
        except Reject as error:
            require(marker in str(error), f"wrong hostile rejection: {error}")
            continue
        raise Reject(f"hostile mutation accepted: {marker}")
    return len(mutations)


def main() -> None:
    require(git("rev-parse", f"{BASE}^{{commit}}") == BASE, "base commit")
    require(git("rev-parse", f"{BASE}^{{tree}}") == TREE, "base tree")
    require(git("branch", "--show-current") == BRANCH, "current branch")
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    validate(audit)
    for path, expected in audit["pins"].items():
        require(sha256(frozen_bytes(path)).hexdigest() == expected, f"source pin {path}")
    canonical = json.loads(frozen_bytes("ai/omreal/data/CANONICAL_RESEARCH_STATE_V6.json"))
    require(canonical["theorem"]["score"] == "2/9", "canonical ledger")
    require(canonical["theorem"]["proved_diagonals"] == [1, 2], "proved diagonals")
    predecessor = json.loads(frozen_bytes("ops/team/d9-factor19069-factored-barrier-referee/RESULT.json"))
    require(predecessor["verdict"] == "ACCEPT", "predecessor acceptance")
    require(predecessor["closing_strategy_verdict"] == "PIVOT", "predecessor pivot")
    require(predecessor["theorem_ledger"] == "2/9", "predecessor ledger")
    require(predecessor["precise_successor"] == TARGET, "predecessor successor")
    frontier = json.loads(frozen_bytes("ops/team/d9-factor19069-factored-barrier-constructor/FACTORED_BARRIER_FRONTIER.json"))
    require(frontier["circuit_census"]["parent_factor_nodes"] == 70, "frontier factors")
    require(frontier["circuit_census"]["wedge_equation_nodes"] == 36, "frontier wedge nodes")
    require(frontier["circuit_census"]["expanded_product_used"] is False, "frontier expansion")
    require(frontier["strict_interior_critical_frontier"]["connected_components_sampled"] == 0, "frontier sample count")
    first = frontier["strict_interior_critical_frontier"]["first_unsampled_component_or_stratum"]
    require(first["stratum_id"] == "FB-C0-STRICT-INTERIOR-FULL-SUPPORT", "first unresolved stratum")
    count = hostile_mutations(audit)
    print("PASS D9 factor-19069 critical equidimensional gate-1 opening audit")
    print(f"base={BASE[:8]} tree={TREE[:8]} factors=70 wedge=36 barrier_degree=90")
    print(f"opening_hostile_mutations={count} ledger=2/9 drive_connector=false github_write=false")


if __name__ == "__main__":
    main()
