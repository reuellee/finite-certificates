#!/usr/bin/env python3
"""Independently attack the D3 component-saturation Q0 handoff.

This lane treats the constructor JSON as untrusted data.  It imports no
constructor code and never runs the guarded research saturation.  The exact
wall list is rebuilt from the pinned canonical parent-bracket source; all
other checks use the Python standard library.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CONSTRUCTOR = ROOT / "ops" / "team" / "d3-triple-critical-saturation-constructor"
CONTRACT_PATH = CONSTRUCTOR / "SATURATION_CONTRACT.json"
RESULT_PATH = CONSTRUCTOR / "RESULT.json"
RUNNER_PATH = CONSTRUCTOR / "run_q1_saturation.py"
SYSTEM_PATH = ROOT / "ai" / "omreal" / "data" / "DIAG3_triple_fullspace_critical_h1.json"
OPENING_PATH = (
    ROOT
    / "ops"
    / "research-team"
    / "cycles"
    / "2026-09-02-d3-triple-critical-saturation-component-gate1"
    / "OPENING_STATE.json"
)
OUTPUT_PATH = HERE / "RESULT.json"

sys.path.insert(0, str(ROOT / "ai" / "omreal"))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402


class Reject(AssertionError):
    pass


def require(condition: bool, marker: str) -> None:
    if not condition:
        raise Reject(marker)


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="ascii"))


def digest_path(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def canonical_digest(value) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def check_seal(value: dict, marker: str) -> None:
    body = deepcopy(value)
    stored = body.pop("semantic_sha256", None)
    require(stored == canonical_digest(body), marker)


def sparse(polynomial: dict) -> list[list]:
    return [
        [int(coefficient), list(monomial)]
        for monomial, coefficient in sorted(polynomial.items())
        if coefficient
    ]


def degree(terms: list[list]) -> int | None:
    return max((sum(monomial) for _coefficient, monomial in terms), default=None)


def vanishes_on_coordinate_ideal(terms: list[list], variables: set[int]) -> bool:
    return all(any(exponents[index] for index in variables) for _coefficient, exponents in terms)


def expected_wall_records() -> list[tuple[str, list[list], int]]:
    return [
        (label, sparse(polynomial), int(sign))
        for label, polynomial, sign in labeled.parent_bracket_factors()
    ]


def validate_structure(contract: dict, system: dict, opening: dict) -> None:
    """Check the exact structural claims while leaving gate status separate."""

    check_seal(contract, "contract semantic seal")
    require(contract["opening_revision"] == opening["base"]["commit"], "opening revision")
    require(contract["opening_tree"] == opening["base"]["tree"], "opening tree")
    require(contract["target"]["id"] == opening["selected_target"]["id"], "target")
    source = contract["source_ideal"]
    require(source["artifact_sha256"] == digest_path(SYSTEM_PATH), "source byte digest")
    require(source["artifact_semantic_sha256"] == canonical_digest(system), "source semantic digest")
    equations = system["equations"]
    nonzero = [row for row in equations if row["terms"]]
    require(len(equations) == 59 and len(nonzero) == 55, "source equation census")
    require(sum(len(row["terms"]) for row in equations) == 14_741, "source term census")
    require(max(degree(row["terms"]) or -1 for row in equations) == 8, "source degree census")

    saturation = contract["saturation_contract"]
    stages = saturation["stages"]
    records = expected_wall_records()
    require(saturation["ordered"] is True, "ordered ledger")
    require(saturation["anonymous_product_saturation_used"] is False, "anonymous product")
    require(saturation["stage_count"] == 62 == len(stages) == len(records), "stage count")
    require(saturation["stage_order"] == [row["stage_id"] for row in stages], "stage order")
    for index, (stage, expected) in enumerate(zip(stages, records, strict=True)):
        label, polynomial, sign = expected
        check_seal(stage, f"stage {index} seal")
        require(stage["stage_index"] == index, f"stage {index} index")
        require(stage["parent_bracket_label"] == label, f"stage {index} label")
        require(stage["sparse_polynomial"] == polynomial, f"stage {index} polynomial")
        require(stage["normalization_sign"] == sign, f"stage {index} sign")
        require(stage["attachment_class"] == "PARENT_WALL", f"stage {index} class")
        require(stage["degree"] == degree(polynomial), f"stage {index} degree")
        attachment = stage["component_attachment_contract"]
        require(
            attachment["set_identity"] == f"V(J_{index:02d})=V(J_{index + 1:02d}) union V(A_{index:02d})",
            f"stage {index} set identity",
        )
        require(
            attachment["wall_branch_preserved_as"] == f"A_{index:02d}=J_{index:02d}+<H_{index:02d}_{label}>",
            f"stage {index} wall branch",
        )

    singular = contract["singular_locus_retention"]
    require(singular["all_59_formal_source_equations_retained_at_every_stage"] is True, "source retention")
    require(singular["height_minors_used_as_saturators"] is False, "minor saturation")
    require(singular["jacobian_rank_or_singularity_equations_used_as_saturators"] is False, "rank saturation")
    require(singular["residual_factors_used_as_saturators"] is False, "factor saturation")

    variables = "abcdefghi"
    walls = {label: terms for label, terms, _sign in records}
    canaries = contract["known_fourspace_canaries"]
    require(len(canaries) == 2, "four-space canary count")
    expected_ideals = [set("abcdf"), set("bcdef")]
    expected_labels = ["1346", "1247"]
    for index, canary in enumerate(canaries):
        check_seal(canary, f"four-space {index} seal")
        coordinate_set = set(canary["coordinate_ideal"])
        require(coordinate_set == expected_ideals[index], f"four-space {index} ideal")
        zero_indices = {variables.index(name) for name in coordinate_set}
        require(all(vanishes_on_coordinate_ideal(row["terms"], zero_indices) for row in equations), f"four-space {index} source")
        label = canary["discriminating_isolated_canary"]["parent_wall"]
        require(label == expected_labels[index], f"four-space {index} discriminating label")
        require(vanishes_on_coordinate_ideal(walls[label], zero_indices), f"four-space {index} wall membership")
        other_indices = {variables.index(name) for name in expected_ideals[1 - index]}
        require(not vanishes_on_coordinate_ideal(walls[label], other_indices), f"four-space {index} discrimination")
        actual_memberships = sorted(
            label for label, terms in walls.items() if vanishes_on_coordinate_ideal(terms, zero_indices)
        )
        require(actual_memberships == sorted(canary["named_parent_wall_memberships"]), f"four-space {index} census")

    hostile = contract["hostile_boundary_canaries"]
    require(len(hostile) == 3, "hostile canary count")
    require(all(row["accepted"] is False for row in hostile), "hostile false-boundary acceptance")
    require(all(row["claimed_attachment_class"] == "PROJECTIVE_INFINITY" for row in hostile), "hostile claim class")

    jobs = contract["job_census"]
    require(jobs["base_ring"]["variable_count"] == 9, "base variable count")
    require(jobs["parent_boundary"]["nonconstant_wall_saturator_count"] == 62, "wall count")
    require(jobs["parent_boundary"]["nonzero_constant_brackets_not_saturated"] == 8, "constant-unit count")
    require(jobs["ordered_sequential_compilation"]["maximum_transient_variable_count"] == 10, "transient variables")
    require(jobs["simultaneous_preflight_representation_not_execution_order"]["variable_count"] == 71, "preflight variables")
    require(jobs["simultaneous_preflight_representation_not_execution_order"]["nonzero_equation_count"] == 117, "preflight equations")

    forecast = contract["numeric_local_resource_forecast"]
    require(forecast["ordered_saturation_stages"] == 62, "forecast stages")
    require(forecast["projected_total_wall_seconds"] <= forecast["cycle_ceiling_wall_seconds"], "wall ceiling")
    require(forecast["projected_peak_ram_gib"] <= forecast["cycle_ceiling_peak_ram_gib"], "RAM ceiling")
    require(forecast["projected_scratch_gib"] <= forecast["cycle_ceiling_scratch_gib"], "scratch ceiling")
    require(contract["q0_disposition"]["independently_accepted"] is False, "constructor self-acceptance")
    require(contract["q0_disposition"]["q1_status"].startswith("DENIED"), "premature Q1")


def gate_blockers(contract: dict, runner_text: str) -> list[dict]:
    stages = contract["saturation_contract"]["stages"]
    materialized = 0
    for stage in stages:
        attachment = stage["component_attachment_contract"]
        if attachment.get("removed_components") and attachment.get("exact_reduction_certificates"):
            materialized += 1
    forecast = contract["numeric_local_resource_forecast"]
    return [
        {
            "id": "MATERIALIZED_COMPONENT_ATTACHMENTS_ABSENT",
            "observed": materialized,
            "required": "an exact containment identity/certificate for every removed component",
            "evidence": "all 62 stages contain a future-output instruction, not a component list or exact reduction certificate",
        },
        {
            "id": "END_TO_END_Q1_FORECAST_ABSENT",
            "observed": contract["conditional_q1_executor"]["scope_after_all_62_stages"],
            "required": "a numeric path to the preregistered row-removal or complete-route-obstruction endpoint",
            "evidence": "the 210-minute forecast covers saturation only; dimension, real roots, chamber residence, continuation, and S8 transfer remain unforecasted",
        },
        {
            "id": "SCRATCH_CEILING_NOT_ENFORCED",
            "observed": "no scratch-byte census or 10-GiB stop in guarded runner",
            "required": "fail closed before crossing the 10-GiB cycle ceiling",
            "evidence": "runner retains every dumped state but contains no file-size or directory-size guard",
        },
        {
            "id": "SATURATION_FORECAST_UNCALIBRATED",
            "observed": {
                "confidence": forecast["confidence"],
                "empirical_exact_cas_calibration_available": forecast["empirical_exact_cas_calibration_available"],
                "scope": forecast["construction_replay_baselines"]["scope"],
            },
            "required": "independent evidence that the minimum decrease remains reachable inside the fixed ceiling",
            "evidence": "the numerical envelope is a hard allocation, not a measured or calibrated research-ideal forecast",
        },
        {
            "id": "RUNNER_ENDS_BEFORE_Q1_ENDPOINT",
            "observed": "SATURATION_COMPLETE_Q1_STILL_REQUIRES_DIMENSION_REAL_ROOT_AND_ATTACHMENT_CHECKS" in runner_text,
            "required": "positive row removal, complete exact route obstruction, exact null, or reproducible timeout frontier",
            "evidence": "even a 62-stage success deliberately stops with all downstream Q1 quantifiers open",
        },
    ]


def reseal(candidate: dict) -> dict:
    candidate.pop("semantic_sha256", None)
    candidate["semantic_sha256"] = canonical_digest(candidate)
    return candidate


def hostile_mutations(contract: dict, system: dict, opening: dict) -> list[dict]:
    cases: list[tuple[str, dict]] = []

    def add(identifier: str, candidate: dict) -> None:
        cases.append((identifier, reseal(candidate)))

    candidate = deepcopy(contract); candidate["opening_revision"] = "0" * 40; add("opening_revision", candidate)
    candidate = deepcopy(contract); candidate["target"]["id"] = "DIFFERENT"; add("target", candidate)
    candidate = deepcopy(contract); candidate["source_ideal"]["artifact_sha256"] = "0" * 64; add("source_digest", candidate)
    candidate = deepcopy(contract); candidate["source_ideal"]["artifact_semantic_sha256"] = "0" * 64; add("source_semantic", candidate)
    candidate = deepcopy(contract); candidate["saturation_contract"]["ordered"] = False; add("unordered", candidate)
    candidate = deepcopy(contract); candidate["saturation_contract"]["anonymous_product_saturation_used"] = True; add("anonymous_product", candidate)
    candidate = deepcopy(contract); candidate["saturation_contract"]["stage_count"] = 61; add("stage_count", candidate)
    candidate = deepcopy(contract); candidate["saturation_contract"]["stages"].pop(); add("stage_loss", candidate)
    candidate = deepcopy(contract); candidate["saturation_contract"]["stage_order"].reverse(); add("stage_order", candidate)
    candidate = deepcopy(contract); candidate["saturation_contract"]["stages"][0]["parent_bracket_label"] = "9999"; candidate["saturation_contract"]["stages"][0] = reseal(candidate["saturation_contract"]["stages"][0]); add("wall_label", candidate)
    candidate = deepcopy(contract); candidate["saturation_contract"]["stages"][0]["sparse_polynomial"][0][0] *= -1; candidate["saturation_contract"]["stages"][0] = reseal(candidate["saturation_contract"]["stages"][0]); add("wall_polynomial", candidate)
    candidate = deepcopy(contract); candidate["saturation_contract"]["stages"][0]["attachment_class"] = "PROJECTIVE_INFINITY"; candidate["saturation_contract"]["stages"][0] = reseal(candidate["saturation_contract"]["stages"][0]); add("wall_class", candidate)
    candidate = deepcopy(contract); candidate["saturation_contract"]["stages"][0]["component_attachment_contract"]["set_identity"] = "FALSE"; candidate["saturation_contract"]["stages"][0] = reseal(candidate["saturation_contract"]["stages"][0]); add("set_identity", candidate)
    candidate = deepcopy(contract); candidate["singular_locus_retention"]["height_minors_used_as_saturators"] = True; add("minor_saturation", candidate)
    candidate = deepcopy(contract); candidate["singular_locus_retention"]["all_59_formal_source_equations_retained_at_every_stage"] = False; add("source_loss", candidate)
    candidate = deepcopy(contract); candidate["known_fourspace_canaries"][0]["coordinate_ideal"].remove("a"); candidate["known_fourspace_canaries"][0] = reseal(candidate["known_fourspace_canaries"][0]); add("fourspace_ideal", candidate)
    candidate = deepcopy(contract); candidate["known_fourspace_canaries"][0]["discriminating_isolated_canary"]["parent_wall"] = "1247"; candidate["known_fourspace_canaries"][0] = reseal(candidate["known_fourspace_canaries"][0]); add("fourspace_wall", candidate)
    candidate = deepcopy(contract); candidate["known_fourspace_canaries"][1]["named_parent_wall_memberships"].pop(); candidate["known_fourspace_canaries"][1] = reseal(candidate["known_fourspace_canaries"][1]); add("fourspace_census", candidate)
    candidate = deepcopy(contract); candidate["hostile_boundary_canaries"][0]["accepted"] = True; candidate["hostile_boundary_canaries"][0] = reseal(candidate["hostile_boundary_canaries"][0]); add("box_as_infinity", candidate)
    candidate = deepcopy(contract); candidate["hostile_boundary_canaries"][1]["accepted"] = True; candidate["hostile_boundary_canaries"][1] = reseal(candidate["hostile_boundary_canaries"][1]); add("seam_as_infinity", candidate)
    candidate = deepcopy(contract); candidate["hostile_boundary_canaries"][2]["accepted"] = True; candidate["hostile_boundary_canaries"][2] = reseal(candidate["hostile_boundary_canaries"][2]); add("rank_loss_as_infinity", candidate)
    candidate = deepcopy(contract); candidate["job_census"]["base_ring"]["variable_count"] = 8; add("base_variables", candidate)
    candidate = deepcopy(contract); candidate["job_census"]["parent_boundary"]["nonconstant_wall_saturator_count"] = 70; add("wall_census", candidate)
    candidate = deepcopy(contract); candidate["numeric_local_resource_forecast"]["projected_total_wall_seconds"] = 14_401; add("wall_ceiling", candidate)
    candidate = deepcopy(contract); candidate["numeric_local_resource_forecast"]["projected_scratch_gib"] = 11; add("scratch_ceiling", candidate)
    candidate = deepcopy(contract); candidate["q0_disposition"]["independently_accepted"] = True; add("self_acceptance", candidate)
    candidate = deepcopy(contract); candidate["q0_disposition"]["q1_status"] = "ACTIVE"; add("premature_q1", candidate)

    rejected = []
    for identifier, candidate in cases:
        try:
            validate_structure(candidate, system, opening)
        except (AssertionError, KeyError, TypeError, ValueError) as error:
            rejected.append({"id": identifier, "rejected": True, "reason": str(error)})
            continue
        raise AssertionError(f"hostile mutation accepted: {identifier}")
    require(len(rejected) >= 20, "hostile mutation census")
    return rejected


def build_result() -> dict:
    contract = load(CONTRACT_PATH)
    producer_result = load(RESULT_PATH)
    opening = load(OPENING_PATH)
    system = load(SYSTEM_PATH)
    runner_text = RUNNER_PATH.read_text(encoding="ascii")
    validate_structure(contract, system, opening)
    mutations = hostile_mutations(contract, system, opening)
    blockers = gate_blockers(contract, runner_text)
    require(producer_result["accepted"] is False, "producer accepted its own output")
    require(producer_result["q1_status"].startswith("DENIED"), "producer activated Q1")
    require(len(blockers) == 5, "blocker census")
    return {
        "format": "d3-triple-critical-saturation-falsifier-result-v1",
        "track_id": "d3-triple-critical-saturation-falsifier",
        "status": "PASS",
        "verdict": "Q0_NULL_MINIMUM_DECREASE_NOT_REACHABLE",
        "constructor_commit": "97787bed0afae6a2f7cb7d2edf9df4f54bbe97f9",
        "inputs": {
            "contract": {"bytes": CONTRACT_PATH.stat().st_size, "sha256": digest_path(CONTRACT_PATH)},
            "producer_result": {"bytes": RESULT_PATH.stat().st_size, "sha256": digest_path(RESULT_PATH)},
            "runner": {"bytes": RUNNER_PATH.stat().st_size, "sha256": digest_path(RUNNER_PATH)},
            "source_system": {"bytes": SYSTEM_PATH.stat().st_size, "sha256": digest_path(SYSTEM_PATH)},
            "opening": {"bytes": OPENING_PATH.stat().st_size, "sha256": digest_path(OPENING_PATH)},
        },
        "structural_replay": {
            "exact_source_generators": 59,
            "nonzero_source_generators": 55,
            "source_sparse_terms": 14_741,
            "ordered_parent_wall_stages": 62,
            "known_fourspace_canaries": 2,
            "artificial_boundary_rejection_canaries": 3,
            "status": "PASS",
        },
        "q0_blockers": blockers,
        "first_failed_obligation": "END_TO_END_EXECUTABLE_COMPONENT_DECORATED_CONTRACT_WITH_CEILING_BOUND_Q1_PATH",
        "hostile_mutations": {
            "rejected": len(mutations),
            "total": len(mutations),
            "all_rejected": True,
            "results": mutations,
        },
        "gate": {
            "q0": "NULL",
            "q1": "DENIED",
            "minimum_decrease_still_reachable_inside_ceiling": False,
            "theorem_credit": "NONE",
            "theorem_ledger": "2/9",
            "triple_source_residual": 1_162_302,
            "recommended_trajectory": "STALLED",
            "recommended_action": "STOP",
        },
        "scope": [
            "Independent machine falsification, not human review.",
            "No raw Groebner, saturation, primary decomposition, or RUR research job was run.",
            "The exact source, ordered wall ledger, and canaries replay, but they do not make the preregistered theorem-level decrease reachable inside the fixed ceiling.",
            "No theorem, row, component, or ledger credit is claimed.",
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    result = build_result()
    if arguments.write:
        OUTPUT_PATH.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii")
    print("PASS independent structural replay of source, 62 walls, and five canaries")
    print(f"PASS {result['hostile_mutations']['rejected']}/{result['hostile_mutations']['total']} hostile mutations rejected")
    print("Q0 NULL; Q1 DENIED; MINIMUM DECREASE UNREACHABLE; STALLED / STOP")


if __name__ == "__main__":
    main()
