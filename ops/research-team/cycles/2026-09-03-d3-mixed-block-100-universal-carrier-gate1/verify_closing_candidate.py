#!/usr/bin/env python3
"""Verify the frozen-input D3 mixed-(1,0,0) closing candidate."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[4]
PATH = Path(__file__).with_name("CLOSING_CANDIDATE.json")
OPEN = ["2/9", 1, ["diag3_pair_hc1", "diag3_triple_hc0"], 7, "UNKNOWN", "UNKNOWN", 8, 11]
CLOSE = ["2/9", 1, ["diag3_pair_hc1", "diag3_triple_hc0"], 7, "UNKNOWN", "UNKNOWN", 9, 12]
ROUTE = ["O3_universal_mixed_chain", "O4_arbitrary_flag_coherence"]


def require(ok: bool, message: str) -> None:
    if not ok:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def validate(data: dict) -> None:
    require(data["format"] == "d3-mixed-100-closing-candidate-v1", "format")
    require(data["cycle_id"] == "2026-09-03-d3-mixed-block-100-universal-carrier-gate1", "cycle")
    require(git("rev-parse", f'{data["base"]["revision"]}^{{tree}}') == data["base"]["tree"], "base")
    require(git("rev-parse", f'{data["opening"]["revision"]}^{{tree}}') == data["opening"]["tree"], "opening")
    require(git("rev-parse", f'{data["integrated_evidence"]["revision"]}^{{tree}}') == data["integrated_evidence"]["tree"], "evidence")

    roles = data["roles"]
    require(roles["constructor"]["handoff"] == "NULL_STALLED_STOP", "constructor")
    require(roles["falsifier"]["handoff"] == "NO_UNIVERSAL_OBSTRUCTION_FOUND_WITHIN_FROZEN_SCOPE", "falsifier")
    require(roles["independent_verifier"]["handoff"] == "NULL_STALLED_STOP_INDEPENDENTLY_CONFIRMED", "verifier")
    for role in roles.values():
        require(git("rev-parse", f'{role["lane_revision"]}^{{tree}}') == role["lane_tree"], "lane tree")

    result = data["result"]
    require(result["constructor"] == result["falsifier"] == "NULL", "null lanes")
    require(result["independent_verdict"] == "NULL_STALLED_STOP_INDEPENDENTLY_CONFIRMED", "independent verdict")
    require(result["positive_token"] is None and result["negative_token"] is None, "no token")
    require(result["O3"] == result["O4"] == "OPEN", "O3/O4 open")
    require(result["trajectory"] == "STALLED" and result["strategy_action"] == "STOP", "stalled stop")
    require(result["selected_successor"] == "NONE" and result["same_route_continue"] is False, "no successor")

    finding = data["exact_finding"]
    require(finding["formal_kernel_cone"] == "EXACT_INTEGRAL_STRICTLY_FUNCTORIAL_ALGEBRAIC_CONTROL", "formal cone")
    require(finding["formal_kernel_cone_is_geometric_carrier"] is False, "not geometric")
    require(finding["interface_entails_geometric_mixed_proper_realization"] is False, "non-entailment")
    require(finding["empty_carrier_expansion_is_actual_admissible_9dvl_instance"] is False, "no actual empty model")
    require(finding["interface_non_entailment_is_full_negative"] is False, "no negative")
    require(finding["row2599_comparison_incidences"] == "4/6" and finding["bounded_repair_available"] is False, "first gap")

    proof = data["proof_distance"]
    require(proof["opening_vector"] == proof["midpoint_vector"] == OPEN, "opening midpoint")
    require(proof["closing_vector"] == CLOSE, "closing vector")
    require(proof["selected_route_opening"] == proof["selected_route_closing"] == ROUTE, "route residual")
    require(proof["selected_route_delta"] == 0 and proof["minimum_acceptable_decrease_met"] is False, "no decrease")

    accounting = data["accounting"]
    require(accounting["ledger_opening"] == accounting["ledger_closing"] == "2/9", "ledger")
    require(accounting["ledger_delta"] == "0/9", "ledger delta")
    require(accounting["canonical_open_obligations"] == 7, "obligations")
    require(accounting["pair_residual"] == accounting["pair_coverage"] == "UNKNOWN", "pair")
    require(accounting["triple_residual"] == 1162302, "triple")
    require(accounting["formal_3_of_10_promoted"] is False and accounting["theorem_or_counterexample_claimed"] is False, "claim guards")

    resources = data["resources"]
    require(resources["opening_to_independent_verifier_seconds"] == 1598, "elapsed")
    require(resources["opening_to_independent_verifier_seconds"] < resources["governed_ceiling_seconds"] == 14400, "ceiling")
    require(resources["constructor_handoffs"] == 1 and resources["verifier_directed_repairs"] == 0, "handoffs")
    require(resources["research_saturation_or_cad_jobs"] == resources["cloud_workers"] == resources["external_spend_usd"] == 0, "resource scope")
    require(resources["peak_ram_continuously_measured"] is False, "RAM boundary")

    require(all(value is False for value in data["scope"].values()), "scope")
    require(len(data["source_pins"]) == 13, "pins")
    for relative, expected in data["source_pins"].items():
        require(sha256(ROOT / relative) == expected, f"source drift {relative}")
    require(len(data["nonconsequences"]) == 8, "nonconsequences")


def hostiles(data: dict) -> int:
    mutations: list[dict] = []

    def add(path: tuple[str, ...], value: object) -> None:
        candidate = copy.deepcopy(data)
        node = candidate
        for key in path[:-1]:
            node = node[key]
        node[path[-1]] = value
        mutations.append(candidate)

    add(("result", "constructor"), "POSITIVE")
    add(("result", "falsifier"), "NEGATIVE")
    add(("result", "independent_verdict"), "PASS_POSITIVE")
    add(("result", "positive_token"), "FORGED")
    add(("result", "negative_token"), "FORGED")
    add(("result", "O3"), "PROVED")
    add(("result", "O4"), "PROVED")
    add(("result", "trajectory"), "CONVERGING")
    add(("result", "strategy_action"), "CONTINUE")
    add(("result", "selected_successor"), "O1_O2")
    add(("result", "same_route_continue"), True)
    add(("exact_finding", "formal_kernel_cone_is_geometric_carrier"), True)
    add(("exact_finding", "interface_entails_geometric_mixed_proper_realization"), True)
    add(("exact_finding", "empty_carrier_expansion_is_actual_admissible_9dvl_instance"), True)
    add(("exact_finding", "interface_non_entailment_is_full_negative"), True)
    add(("exact_finding", "row2599_comparison_incidences"), "6/6")
    add(("exact_finding", "bounded_repair_available"), True)
    add(("proof_distance", "closing_vector"), OPEN)
    add(("proof_distance", "selected_route_closing"), [])
    add(("proof_distance", "selected_route_delta"), 2)
    add(("proof_distance", "minimum_acceptable_decrease_met"), True)
    add(("accounting", "ledger_closing"), "3/9")
    add(("accounting", "canonical_open_obligations"), 6)
    add(("accounting", "pair_residual"), 0)
    add(("accounting", "triple_residual"), 0)
    add(("accounting", "formal_3_of_10_promoted"), True)
    add(("accounting", "theorem_or_counterexample_claimed"), True)
    add(("resources", "cloud_workers"), 1)
    add(("scope", "network_research"), True)
    add(("scope", "human_review"), True)

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
    print("PASS D3 mixed-(1,0,0) closing candidate")
    print(f"PASS 13 source pins and hostile mutations {rejected}/{rejected}")
    print("NULL / STALLED / STOP / NONE; O3/O4 2/2 open; ledger 2/9")
    print("FORMAL cone exact; geometric realization not entailed; no admissible negative")


if __name__ == "__main__":
    main()
