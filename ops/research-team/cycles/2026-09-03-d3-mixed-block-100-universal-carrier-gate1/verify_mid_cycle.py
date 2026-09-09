#!/usr/bin/env python3
"""Verify the frozen mixed-(1,0,0) midpoint and fail-closed stop."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PATH = Path(__file__).with_name("MID_CYCLE_CHECKPOINT.json")
OPEN = ["2/9", 1, ["diag3_pair_hc1", "diag3_triple_hc0"], 7, "UNKNOWN", "UNKNOWN", 8, 11]
ROUTE = ["O3_universal_mixed_chain", "O4_arbitrary_flag_coherence"]


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def validate(data: dict) -> None:
    require(data["format"] == "d3-mixed-100-mid-cycle-checkpoint-v1", "format")
    require(data["cycle_id"] == "2026-09-03-d3-mixed-block-100-universal-carrier-gate1", "cycle")
    require(data["opening"] == {"commit": "1c6519d89335dde215e93887de074ea4e6d6464a", "tree": "ff8a33e13952e86b27f184e3d8c40e768fbeb110"}, "opening pin")

    handoffs = data["frozen_handoffs"]
    require(handoffs["constructor"]["handoff"] == "NULL", "constructor null")
    require(handoffs["falsifier"]["handoff"] == "NO_UNIVERSAL_OBSTRUCTION_FOUND_WITHIN_FROZEN_SCOPE", "falsifier null")
    require(handoffs["constructor"]["integrated_commit"] == "a92c459340d0f76c3578a49f10cbb7968d07c156", "constructor integration")
    require(handoffs["falsifier"]["integrated_commit"] == "833d61bd0702529c892c9b37ad8a2ee5c7b8b972", "falsifier integration")
    for role in ("constructor", "falsifier"):
        require(handoffs[role]["assessment"] == "NULL_STALLED_STOP", f"{role} assessment")
        require(git("rev-parse", f'{handoffs[role]["lane_commit"]}^{{tree}}') == handoffs[role]["lane_tree"], f"{role} lane tree")

    evidence = data["integrated_evidence"]
    require(evidence == {"commit": "833d61bd0702529c892c9b37ad8a2ee5c7b8b972", "tree": "736228f57bcbb1bbad355a87266bfb833fb420ce"}, "integrated pin")
    require(git("rev-parse", f'{evidence["commit"]}^{{tree}}') == evidence["tree"], "integrated tree")

    verdict = data["verdict"]
    require(verdict["constructor"] == verdict["falsifier"] == "NULL", "lane verdicts")
    require(verdict["universal_proof"] is False, "no proof")
    require(verdict["exact_admissible_universal_obstruction"] is False, "no obstruction")
    require(verdict["positive_token"] is None and verdict["negative_token"] is None, "no tokens")
    require(verdict["repair_authorized"] is False, "no repair")
    require(verdict["discovery_action"] == "FREEZE_NULL_AND_STOP", "stop action")
    require(verdict["independent_verification_required"] is True, "independent review")

    gap = data["first_missing_edge"]
    require(gap["id"] == "O3_MIXED_GEOMETRIC_RELATIVE_BOUNDARY_SURJECTIVITY", "first gap")
    require(gap["from"] == "DECLARED_L_SOURCE_INTERFACE" and gap["to"] == "O3_universal_mixed_chain", "gap edge")
    require(len(gap["missing_inputs"]) == 5 and gap["bounded_repair"] is False, "unbounded gap")

    info = data["exact_information"]
    require(info["formal_kernel_cone_exists"] is True and info["formal_kernel_cone_is_integral_and_functorial"] is True, "formal control")
    require(info["formal_kernel_cone_is_geometric_mixed_proper"] is False, "not geometric")
    require(info["declared_interface_entails_geometric_carrier"] is False, "non-entailment")
    require(info["empty_carrier_interpretation_is_actual_9dvl_instance"] is False, "no actual empty instance")
    require(info["interface_non_entailment_is_d3_counterexample"] is False, "no D3 counterexample")
    require(info["row2599_comparison_incidences_certified"] == 4 and info["row2599_comparison_incidences_required"] == 6, "row2599 frontier")

    proof = data["proof_distance"]
    require(proof["opening_vector"] == proof["midpoint_vector"] == OPEN, "canonical vector unchanged")
    require(proof["selected_route_opening"] == proof["selected_route_midpoint"] == ROUTE, "route unchanged")
    require(proof["minimum_acceptable_decrease_met"] is False, "no decrease")
    require(proof["reachable_inside_remaining_ceiling"] is False, "not reachable")
    require(proof["trajectory"] == "STALLED", "trajectory")

    accounting = data["accounting"]
    require(accounting["ledger_opening"] == accounting["ledger_midpoint"] == "2/9", "ledger")
    require(accounting["ledger_delta"] == "0/9", "ledger delta")
    require(accounting["canonical_obligations_opening"] == accounting["canonical_obligations_midpoint"] == 7, "obligations")
    require(accounting["pair_residual"] == accounting["pair_coverage"] == "UNKNOWN", "pair accounting")
    require(accounting["triple_residual"] == 1162302, "triple residual")
    require(accounting["formal_taxonomy_is_global_denominator"] is False, "no denominator")
    require(accounting["provisional_3_of_10_is_end_to_end_coverage"] is False, "no coverage")

    require(len(data["source_pins"]) == 9, "pin count")
    for relative, expected in data["source_pins"].items():
        require(sha256(ROOT / relative) == expected, f"source drift {relative}")


def hostiles(data: dict) -> int:
    mutations: list[dict] = []

    def add(path: tuple[str, ...], value: object) -> None:
        candidate = copy.deepcopy(data)
        node = candidate
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
        mutations.append(candidate)

    add(("verdict", "universal_proof"), True)
    add(("verdict", "exact_admissible_universal_obstruction"), True)
    add(("verdict", "positive_token"), "FORGED")
    add(("verdict", "negative_token"), "FORGED")
    add(("verdict", "repair_authorized"), True)
    add(("verdict", "discovery_action"), "CONTINUE")
    add(("frozen_handoffs", "constructor", "handoff"), "POSITIVE")
    add(("frozen_handoffs", "falsifier", "handoff"), "NEGATIVE")
    add(("first_missing_edge", "bounded_repair"), True)
    add(("exact_information", "formal_kernel_cone_is_geometric_mixed_proper"), True)
    add(("exact_information", "declared_interface_entails_geometric_carrier"), True)
    add(("exact_information", "empty_carrier_interpretation_is_actual_9dvl_instance"), True)
    add(("exact_information", "interface_non_entailment_is_d3_counterexample"), True)
    add(("exact_information", "row2599_comparison_incidences_certified"), 6)
    add(("proof_distance", "midpoint_vector"), ["3/9"])
    add(("proof_distance", "selected_route_midpoint"), [])
    add(("proof_distance", "minimum_acceptable_decrease_met"), True)
    add(("proof_distance", "reachable_inside_remaining_ceiling"), True)
    add(("proof_distance", "trajectory"), "CONVERGING")
    add(("accounting", "ledger_midpoint"), "3/9")
    add(("accounting", "canonical_obligations_midpoint"), 6)
    add(("accounting", "pair_residual"), 0)
    add(("accounting", "formal_taxonomy_is_global_denominator"), True)
    add(("accounting", "provisional_3_of_10_is_end_to_end_coverage"), True)

    rejected = 0
    for candidate in mutations:
        try:
            validate(candidate)
        except (AssertionError, KeyError, subprocess.CalledProcessError):
            rejected += 1
    require(rejected == len(mutations), "hostile mutation escaped")
    return rejected


def main() -> None:
    data = json.loads(PATH.read_text(encoding="utf-8"))
    validate(data)
    rejected = hostiles(data)
    print("PASS D3 mixed-(1,0,0) midpoint: constructor NULL; falsifier NULL")
    print(f"PASS hostile mutations rejected {rejected}/{rejected}")
    print("FIRST GAP O3 mixed geometric relative-boundary surjectivity")
    print("FORMAL cone coherent; geometric mixed/proper realization not entailed")
    print("VECTOR unchanged; ROUTE 2/2 open; FREEZE NULL / STALLED / STOP")


if __name__ == "__main__":
    main()
