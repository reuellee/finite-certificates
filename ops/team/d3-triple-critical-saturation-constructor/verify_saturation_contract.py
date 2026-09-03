#!/usr/bin/env python3
"""Constructor-side deterministic replay and hostile-mutation check.

This is not the cycle's independent verifier.  It proves only that the
constructor artifacts reproduce from the pinned inputs and fail closed under
the listed local mutations.
"""

from __future__ import annotations

from copy import deepcopy
import json

import build_saturation_contract as build


def require(condition: bool, marker: str) -> None:
    if not condition:
        raise AssertionError(marker)


def load(path):
    return json.loads(path.read_text(encoding="ascii"))


def replay() -> tuple[dict, dict, dict]:
    opening = load(build.OPENING)
    system = load(build.SYSTEM)
    critical_manifest = load(build.CRITICAL_MANIFEST)
    expected_manifest = build.build_source_manifest(opening, critical_manifest)
    expected_contract = build.build_contract(
        opening, system, critical_manifest, expected_manifest
    )
    stored_manifest = load(build.MANIFEST)
    stored_contract = load(build.CONTRACT)
    require(stored_manifest == expected_manifest, "source manifest replay")
    require(stored_contract == expected_contract, "saturation contract replay")
    expected_result = build.build_result(expected_contract, expected_manifest)
    stored_result = load(build.RESULT)
    require(stored_result == expected_result, "result replay")
    return stored_manifest, stored_contract, stored_result


def validate_contract(candidate: dict, expected: dict) -> None:
    semantic = deepcopy(candidate)
    stored_digest = semantic.pop("semantic_sha256", None)
    require(stored_digest == build.canonical_digest(semantic), "semantic digest")
    require(candidate == expected, "deterministic contract")


def reseal(candidate: dict) -> dict:
    candidate.pop("semantic_sha256", None)
    candidate["semantic_sha256"] = build.canonical_digest(candidate)
    return candidate


def hostile_mutations(stored: dict) -> list[str]:
    mutations: list[tuple[str, dict]] = []

    def add(marker: str, candidate: dict) -> None:
        mutations.append((marker, reseal(candidate)))

    candidate = deepcopy(stored); candidate["source_ideal"]["artifact_sha256"] = "0" * 64; add("source digest", candidate)
    candidate = deepcopy(stored); candidate["source_ideal"]["census"]["formal_generator_count"] = 58; add("formal source count", candidate)
    candidate = deepcopy(stored); candidate["saturation_contract"]["ordered"] = False; add("ordered ledger", candidate)
    candidate = deepcopy(stored); candidate["saturation_contract"]["anonymous_product_saturation_used"] = True; add("anonymous saturation", candidate)
    candidate = deepcopy(stored); candidate["saturation_contract"]["stage_count"] = 61; add("stage count", candidate)
    candidate = deepcopy(stored); candidate["saturation_contract"]["stages"].pop(); add("stage loss", candidate)
    candidate = deepcopy(stored); candidate["saturation_contract"]["stage_order"].reverse(); add("stage order", candidate)
    candidate = deepcopy(stored); candidate["saturation_contract"]["stages"][0]["parent_bracket_label"] = "9999"; add("wall label", candidate)
    candidate = deepcopy(stored); candidate["saturation_contract"]["stages"][0]["sparse_polynomial"][0][0] *= -1; add("wall polynomial", candidate)
    candidate = deepcopy(stored); candidate["saturation_contract"]["stages"][0]["attachment_class"] = "PROJECTIVE_INFINITY"; add("wall attachment class", candidate)
    candidate = deepcopy(stored); candidate["saturation_contract"]["stages"][0]["rabinowitsch_step"]["relation_degree"] = 3; add("relation degree", candidate)
    candidate = deepcopy(stored); candidate["saturation_contract"]["stages"][0]["component_attachment_contract"]["set_identity"] = "FALSE"; add("component identity", candidate)
    candidate = deepcopy(stored); candidate["singular_locus_retention"]["height_minors_used_as_saturators"] = True; add("minor saturation", candidate)
    candidate = deepcopy(stored); candidate["singular_locus_retention"]["all_59_formal_source_equations_retained_at_every_stage"] = False; add("singular retention", candidate)
    candidate = deepcopy(stored); candidate["known_fourspace_canaries"][0]["discriminating_isolated_canary"]["parent_wall"] = "1247"; add("fourspace one wall", candidate)
    candidate = deepcopy(stored); candidate["known_fourspace_canaries"][1]["discriminating_isolated_canary"]["parent_wall"] = "1346"; add("fourspace two wall", candidate)
    candidate = deepcopy(stored); candidate["known_fourspace_canaries"][0]["attachment_class"] = "PROJECTIVE_INFINITY"; add("fourspace class", candidate)
    candidate = deepcopy(stored); candidate["hostile_boundary_canaries"][0]["accepted"] = True; add("box boundary", candidate)
    candidate = deepcopy(stored); candidate["hostile_boundary_canaries"][1]["accepted"] = True; add("chart seam", candidate)
    candidate = deepcopy(stored); candidate["hostile_boundary_canaries"][2]["accepted"] = True; add("rank loss", candidate)
    candidate = deepcopy(stored); candidate["job_census"]["simultaneous_preflight_representation_not_execution_order"]["variable_count"] = 79; add("variable count", candidate)
    candidate = deepcopy(stored); candidate["job_census"]["parent_boundary"]["nonconstant_wall_saturator_count"] = 70; add("wall count", candidate)
    candidate = deepcopy(stored); candidate["numeric_local_resource_forecast"]["projected_peak_ram_gib"] = 30; add("local RAM envelope", candidate)
    candidate = deepcopy(stored); candidate["q0_disposition"]["independently_accepted"] = True; add("self acceptance", candidate)
    candidate = deepcopy(stored); candidate["q0_disposition"]["q1_status"] = "ACTIVE"; add("premature Q1", candidate)
    candidate = deepcopy(stored); candidate["q0_disposition"]["theorem_ledger_after"] = "3/9"; add("ledger promotion", candidate)
    candidate = deepcopy(stored); candidate["q0_disposition"]["triple_source_residual_after"] = 1_162_301; add("residual promotion", candidate)

    rejected = []
    for marker, candidate in mutations:
        try:
            validate_contract(candidate, stored)
        except AssertionError:
            rejected.append(marker)
            continue
        raise AssertionError(f"hostile mutation accepted: {marker}")
    return rejected


def main() -> None:
    _manifest, contract, result = replay()
    rejected = hostile_mutations(contract)
    require(len(rejected) == 27, "hostile mutation census")
    require(result["accepted"] is False, "constructor self acceptance")
    require(result["q1_status"].startswith("DENIED"), "premature Q1")
    print("PASS deterministic Q0 constructor replay")
    print("PASS exact 62-stage parent-wall ledger and two discriminating canaries")
    print("PASS", len(rejected), "of", len(rejected), "hostile mutations rejected")
    print("Q0 CANDIDATE ONLY; Q1 DENIED; LEDGER 2/9; RESIDUAL 1162302")


if __name__ == "__main__":
    main()
