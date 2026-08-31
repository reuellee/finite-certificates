#!/usr/bin/env python3
"""Verify the immutable post-mask-6 9DVL canonical research state."""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STATE = HERE / "data/CANONICAL_RESEARCH_STATE_V2.json"
PREDECESSOR = HERE / "data/CANONICAL_RESEARCH_STATE.json"
PREDECESSOR_VERIFIER = HERE / "verify_canonical_research_state.py"
STATUS = HERE / "NINE_DIAGONAL_STATUS.md"
README = ROOT / "README.md"
NONVACUITY = ROOT / "ops/team/diag8-mask6-nonvacuity/DIAG8_MASK6_NONVACUITY_CERTIFICATE.npz"
FAN = ROOT / "ops/team/diag8-mask6-fan/DIAG8_MASK6_BARYCENTRIC_FAN_CERTIFICATE.json"
PREDECESSOR_SHA256 = "89d1475a43bef01be74e9c8eed62d9caadd8265f262c3aa3dcf0e704f341432c"
NONVACUITY_SHA256 = "ac86ed2966cf4646dd2241caee4d938aefb9ec70b27a91df8795ad992993c7c5"
FAN_SHA256 = "b5ead7b0ed6ac6a5cb50ab715110e302772f49e43b2419cd54c98228937627cb"
LOOP = [4, 11, 12, 14, 13, 23]
RETIRED = {
    "D4_S53_CONTINUATION": "RETIRED",
    "D4_ALTERNATING_TOTAL_COMPLEX": "RETIRED_UNTIL_ALL_THREE_GLOBAL_INPUTS",
    "ORBIT_5563_LOCAL_ROADMAP_CONTINUATION": "RETIRED",
    "ORBIT_5563_LOCAL_BOX_CONTINUATION": "RETIRED",
    "ORBIT_5563_LOCAL_COLLAR_CONTINUATION": "RETIRED",
    "ORBIT_5563_MACROBOX_CONTINUATION": "RETIRED",
    "ORBIT_5563_CLIPPED_WALL_CONTINUATION": "RETIRED",
}


class Reject(AssertionError):
    """Fail-closed canonical-state rejection."""


def require(condition, message):
    if not condition:
        raise Reject(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(state, check_files=True):
    require(
        set(state)
        == {
            "format", "status", "as_of", "repository", "predecessor", "theorem",
            "inherited_open_obligations", "inherited_route_dispositions",
            "completed_cycle", "selected_target", "target_selection", "process_gates",
        },
        "top-level fields",
    )
    require(state["format"] == "9dvl-canonical-research-state-v2", "format")
    require(state["status"] == "PIVOT_REQUIRED" and state["as_of"] == "2026-08-31", "status")
    repository = state["repository"]
    require(
        repository
        == {
            "full_name": "reuellee/finite-certificates",
            "default_branch": "main",
            "reconciled_commit": "6c7f52b43632072100b67e5f0a9b6221df14d620",
            "reconciled_tree": "60866cb78e8aea3259cf376a4420e5370ab8c010",
            "reconciliation_pull_request": 45,
        },
        "repository",
    )
    predecessor = state["predecessor"]
    require(predecessor["path"] == "ai/omreal/data/CANONICAL_RESEARCH_STATE.json", "predecessor path")
    require(predecessor["sha256"] == PREDECESSOR_SHA256, "predecessor pointer")
    require(predecessor["policy"] == "IMMUTABLE_RECONCILIATION_STATE", "predecessor policy")
    if check_files:
        require(sha256(PREDECESSOR) == PREDECESSOR_SHA256, "predecessor bytes")

    require(
        state["theorem"]
        == {"id": "9DVL", "score": "2/9", "proved_diagonals": [1, 2], "active_diagonal": None, "promotion": "NONE"},
        "theorem",
    )
    obligations = state["inherited_open_obligations"]
    require(set(obligations) == {"diag3_triple_hc0", "diag3_pair_hc1", "diag4_sp", "diag8_h1", "diag9_h0"}, "obligation census")
    require(obligations["diag3_triple_hc0"]["residue"] == 1_162_302, "D3 residue")
    require(obligations["diag3_triple_hc0"]["first_missing_global_object"] == "Q3_COMPLETE_PARENT_BOUNDARY_ATLAS", "Q3")
    require(obligations["diag4_sp"] == {"status": "OPEN", "survivor_labeled": 800_240, "survivor_orbits": 53}, "D4 residue")
    require(all(obligations[key] == "OPEN" for key in ("diag3_pair_hc1", "diag8_h1", "diag9_h0")), "open obligations")
    require(state["inherited_route_dispositions"] == RETIRED, "retired routes")

    cycle = state["completed_cycle"]
    require(cycle["id"] == "2026-08-31-diag8-mask6-cegar", "cycle id")
    require(cycle["selected_target"] == "D8_M6_CEGAR1", "cycle target")
    require(cycle["opening_verdict"] == "CONTINUE_ONE_BOUNDED_DISCRIMINATOR", "opening verdict")
    require(cycle["cross_domain_transfer"]["source_field"] == "counterexample_guided_abstraction_refinement", "transfer")
    nonvacuity = cycle["nonvacuity_gate"]
    require(nonvacuity["status"] == "PROVED", "nonvacuity status")
    require(nonvacuity["parent"] == 860 and nonvacuity["loop"] == LOOP, "nonvacuity target")
    require(
        (
            nonvacuity["family_size"], nonvacuity["exact_charts"],
            nonvacuity["feasibility_or_gordan_witnesses"],
            nonvacuity["directed_noncontainment_witnesses"],
        )
        == (8, 7, 56, 56),
        "nonvacuity counts",
    )
    require(nonvacuity["certificate_sha256"] == NONVACUITY_SHA256, "nonvacuity digest")
    fan = cycle["fixed_chain_gate"]
    require(fan["status"] == "PROVED_BOUNDED_FILLING", "fan status")
    require(
        (fan["parent_brackets_certified"], fan["primitive_residual_factors_certified"], fan["sign_definite_factors"])
        == (70, 26_740, 26_738),
        "fan census",
    )
    require(fan["active_factors"] == [16_573, 19_721], "active factors")
    require((fan["active_wall_nodes"], fan["sectors"]) == (1, 4), "fan arrangement")
    require(fan["every_sector_meets_loop"] is True and fan["radial_edges_cancel"] is True, "fan topology")
    require(fan["certificate_sha256"] == FAN_SHA256, "fan digest")
    require(cycle["exact_consequence"] == "THE_MASK6_LOOP_BOUNDS_IN_F_S_FOR_ONE_CERTIFIED_PROPER_PAIRWISE_INCOMPARABLE_EIGHT_FAMILY", "consequence")
    require(set(cycle["nonconsequences"]) == {"NO_PARENT_860_COVERAGE", "NO_ALL_FAMILIES_STATEMENT", "NO_DIAGONAL_8_PROOF", "NO_9DVL_SCORE_CHANGE"}, "nonconsequences")
    require(cycle["route_disposition"] == "MASK6_DISCRIMINATOR_RETIRED_AFTER_POSITIVE_FILLING", "route disposition")

    require(state["selected_target"] is None, "selected target")
    require(state["target_selection"] == "PENDING_FRESH_INDEPENDENT_OPENING_AUDIT", "next selection")
    gates = state["process_gates"]
    require(all(gates.values()), "process gates")
    if check_files:
        require(sha256(NONVACUITY) == NONVACUITY_SHA256, "nonvacuity bytes")
        require(sha256(FAN) == FAN_SHA256, "fan bytes")
        status = STATUS.read_text(encoding="utf-8")
        require("## Current canonical precedence after merged PR #45 and the D8 mask-6 cycle" in status, "current authority heading")
        readme = README.read_text(encoding="utf-8")
        require("no active diagonal or selected mathematical target" in readme, "README target authority")


def hostile_canaries(state):
    cases = []
    def mutated(callback):
        candidate = copy.deepcopy(state)
        callback(candidate)
        return candidate
    cases.append(("score", mutated(lambda x: x["theorem"].__setitem__("score", "3/9"))))
    cases.append(("diagonal8", mutated(lambda x: x["theorem"]["proved_diagonals"].append(8))))
    cases.append(("target", mutated(lambda x: x.__setitem__("selected_target", "D8_M6_CEGAR1"))))
    cases.append(("d3", mutated(lambda x: x["inherited_open_obligations"]["diag3_triple_hc0"].__setitem__("residue", 0))))
    cases.append(("d4", mutated(lambda x: x["inherited_open_obligations"]["diag4_sp"].__setitem__("survivor_orbits", 52))))
    cases.append(("retirement", mutated(lambda x: x["inherited_route_dispositions"].pop("D4_S53_CONTINUATION"))))
    cases.append(("family", mutated(lambda x: x["completed_cycle"]["nonvacuity_gate"].__setitem__("family_size", 7))))
    cases.append(("factor", mutated(lambda x: x["completed_cycle"]["fixed_chain_gate"].__setitem__("sign_definite_factors", 26_739))))
    cases.append(("node", mutated(lambda x: x["completed_cycle"]["fixed_chain_gate"].__setitem__("active_wall_nodes", 0))))
    cases.append(("promotion", mutated(lambda x: x["completed_cycle"]["nonconsequences"].remove("NO_DIAGONAL_8_PROOF"))))
    cases.append(("repeat", mutated(lambda x: x["process_gates"].__setitem__("retired_mask6_discriminator_cannot_repeat", False))))
    cases.append(("predecessor", mutated(lambda x: x["predecessor"].__setitem__("sha256", "0" * 64))))
    rejected = []
    for name, candidate in cases:
        try:
            validate(candidate, check_files=False)
        except (KeyError, Reject):
            rejected.append(name)
        else:
            raise Reject(f"hostile canary accepted: {name}")
    return tuple(rejected)


def main():
    state = json.loads(STATE.read_text(encoding="utf-8"))
    validate(state)
    replay = subprocess.run(
        [sys.executable, str(PREDECESSOR_VERIFIER)], cwd=ROOT,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    require(replay.returncode == 0, "predecessor replay")
    rejected = hostile_canaries(state)
    print("PASS canonical 9DVL research state v2")
    print("PASS predecessor reconciliation state remains immutable")
    print("PASS D8-M6-CEGAR1 bounded filling recorded; mask-6 route retired")
    print("PASS hostile state canaries:", len(rejected), "/", len(rejected))
    print("PASS theorem ledger unchanged at 2/9; no selected next target")


if __name__ == "__main__":
    main()
