#!/usr/bin/env python3
"""Verify the immutable post-D9-normal-link 9DVL canonical research state."""

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
STATE = HERE / "data/CANONICAL_RESEARCH_STATE_V3.json"
PREDECESSOR = HERE / "data/CANONICAL_RESEARCH_STATE_V2.json"
PREDECESSOR_VERIFIER = HERE / "verify_canonical_research_state_v2.py"
REFEREE_VERIFIER = (
    ROOT
    / "ops/team/diag9-s1237-normal-link-referee/verify_closing_referee.py"
)
STATUS = HERE / "NINE_DIAGONAL_STATUS.md"
OPERATING_SYSTEM = HERE / "RESEARCH_OPERATING_SYSTEM.md"
README = ROOT / "README.md"

PREDECESSOR_SHA256 = "508d5433d33eeb5be915e1749838d73541a8bd0055c74fac00bdb74ee28e930f"
PREDECESSOR_VERIFIER_SHA256 = "aae7a0aa6d3eca6ffedbe82f25e3ffd3e0e1f6652faf420ee477d6703aeb7da1"
BASE = "c55d896cc5c0370e993b793992a2f05d894e0095"
BASE_TREE = "17299e84397aae158a2111cbe01b52f5be24bfd5"
OPENING = "c6bd7a6afeda0888fc950710b941cac6f6c9bf95"
OPENING_TREE = "9c2dbe39a3ea0f36e9e9c8f845e6f72e98526421"
REVIEWED = "5efbd07a25b818306f9fd22597fd81a0f2091309"
REVIEWED_TREE = "b8cb35941043ff40be06cba98461ddab0ba14c8f"
REFEREE = "ca730426cdd5847ae262ddc29c6f4ae98369eba3"
REFEREE_TREE = "56fe7f95a4e20dea581736cb5539abb502e05a63"

ARTIFACTS = {
    "ops/team/diag9-s1237-normal-link-prover/DIAG9_S1237_NORMAL_LINK_NO_GO.json":
        "8aa726c69b556f7c2d85f7f852cb88329da39dcd173294a7db7245f13e0d2d54",
    "ops/team/diag9-s1237-normal-link-falsifier/RESULT.json":
        "15ce5c17a174ed6a82173d24a8f72d04da5962bcea9e87cf3648adb21351d46b",
    "ops/team/diag9-s1237-normal-link-certificate/RESULT.json":
        "8b932ec411fe9bc96d8bb895fccdcf7a63985df6ce4d35b38e2f53eef3afc010",
    "ops/team/diag9-s1237-normal-link-referee/RESULT.json":
        "16be207c4abaddf52bd6b670c293159cb317e712c431597838b00e2815bb8902",
    "ops/team/diag9-s1237-normal-link-referee/CLOSING_MANIFEST.json":
        "9462528276530db48de7ae53808c7290327698878380193bd3f55e208196376d",
}

RETIRED = {
    "D4_S53_CONTINUATION": "RETIRED",
    "D4_ALTERNATING_TOTAL_COMPLEX": "RETIRED_UNTIL_ALL_THREE_GLOBAL_INPUTS",
    "ORBIT_5563_LOCAL_ROADMAP_CONTINUATION": "RETIRED",
    "ORBIT_5563_LOCAL_BOX_CONTINUATION": "RETIRED",
    "ORBIT_5563_LOCAL_COLLAR_CONTINUATION": "RETIRED",
    "ORBIT_5563_MACROBOX_CONTINUATION": "RETIRED",
    "ORBIT_5563_CLIPPED_WALL_CONTINUATION": "RETIRED",
    "D8_MASK6_DISCRIMINATOR": "RETIRED_AFTER_POSITIVE_FILLING",
    "D9_S1237_TANGENTIAL_FOUR_SUPPORT_REDUCTION":
        "RETIRED_AFTER_EXACT_NORMAL_LINK_NO_GO",
    "D9_S1237_ORDINARY_COMMON_RADIAL_LINK":
        "RETIRED_AFTER_EXACT_SINGULAR_LINK",
}

PROCESS_GATES = {
    "theorem_score_promotion_requires_all_invariant_obligations_closed",
    "local_recursive_facet_wall_is_not_a_global_separator",
    "ordinary_radial_link_no_go_does_not_exclude_weighted_arcs",
    "retired_tangential_four_support_route_cannot_repeat",
    "independent_exact_head_review_passed",
    "github_remains_read_only_until_new_explicit_user_instruction",
}


class Reject(AssertionError):
    """Fail-closed canonical-state rejection."""


def require(condition, message):
    if not condition:
        raise Reject(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*arguments: str) -> str:
    return subprocess.run(
        ["git", *arguments], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def validate(state, check_files=True):
    require(set(state) == {
        "format", "status", "as_of", "repository", "predecessor", "theorem",
        "inherited_open_obligations", "inherited_route_dispositions",
        "completed_cycle", "selected_target", "target_selection", "process_gates",
    }, "top-level fields")
    require(state["format"] == "9dvl-canonical-research-state-v3", "format")
    require(state["status"] == "PIVOT_REQUIRED", "status")
    require(state["as_of"] == "2026-09-01", "date")
    require(state["repository"] == {
        "full_name": "reuellee/finite-certificates",
        "default_branch": "main",
        "canonical_storage": "CHATGPT_LIBRARY",
        "github_mode": "READ_ONLY_UNTIL_NEW_EXPLICIT_USER_INSTRUCTION",
        "reconciled_base_commit": BASE,
        "reconciled_base_tree": BASE_TREE,
        "reviewed_math_commit": REVIEWED,
        "reviewed_math_tree": REVIEWED_TREE,
    }, "repository")
    require(state["predecessor"] == {
        "path": "ai/omreal/data/CANONICAL_RESEARCH_STATE_V2.json",
        "sha256": PREDECESSOR_SHA256,
        "policy": "IMMUTABLE_POST_MASK6_STATE",
    }, "predecessor")
    require(state["theorem"] == {
        "id": "9DVL", "score": "2/9", "proved_diagonals": [1, 2],
        "active_diagonal": None, "promotion": "NONE",
    }, "theorem")
    obligations = state["inherited_open_obligations"]
    require(set(obligations) == {
        "diag3_triple_hc0", "diag3_pair_hc1", "diag4_sp", "diag8_h1", "diag9_h0"
    }, "obligations")
    require(obligations["diag3_triple_hc0"] == {
        "status": "OPEN", "residue": 1_162_302,
        "first_missing_global_object": "Q3_COMPLETE_PARENT_BOUNDARY_ATLAS",
    }, "D3 triple")
    require(obligations["diag4_sp"] == {
        "status": "OPEN", "survivor_labeled": 800_240, "survivor_orbits": 53,
    }, "D4")
    require(all(obligations[key] == "OPEN" for key in (
        "diag3_pair_hc1", "diag8_h1", "diag9_h0"
    )), "open obligation status")
    require(state["inherited_route_dispositions"] == RETIRED, "route dispositions")

    cycle = state["completed_cycle"]
    require(cycle["id"] == "2026-09-01-diag9-s1237-normal-link", "cycle id")
    require(cycle["selected_target"] == "D9_S1237_4SUPPORT_NORMAL_LINK_GATE1", "target")
    require(cycle["opening_verdict"] == "PIVOT_SELECT", "opening verdict")
    require((cycle["opening_commit"], cycle["opening_tree"]) == (OPENING, OPENING_TREE), "opening binding")
    require((cycle["reviewed_math_commit"], cycle["reviewed_math_tree"]) == (REVIEWED, REVIEWED_TREE), "review binding")
    require((cycle["referee_commit"], cycle["referee_tree"]) == (REFEREE, REFEREE_TREE), "referee binding")
    family = cycle["family_gate"]
    require(family == {
        "parent": 2599,
        "family": "S12,37",
        "family_size": 9,
        "globally_nonempty_proper_pairwise_incomparable": True,
        "exact_witnesses": 63,
        "active_factor_classes": 3539,
        "all_occurrences_of_active_classes": 6167,
        "aligned_occurrence_union": 5026,
    }, "family gate")
    discovery = cycle["opening_discovery"]
    require(discovery["status"] == "TANGENTIAL_FACE_INTERIOR_ONLY", "discovery scope")
    require((
        discovery["support_3_1_15_factor_ids"],
        discovery["support_3_1_15_zero_sets"],
        discovery["support_3_3_7_factor_ids"],
        discovery["support_3_3_7_zero_sets"],
    ) == (8, 4, 0, 0), "discovery census")
    require(discovery["semantic_sha256"] ==
        "cf4689a6b3a2ae10f7988c4823d2b0283efb0fa9ae4f4861029090765499ec59",
        "discovery digest")
    constructive = cycle["constructive_gate"]
    require(constructive["status"] == "NORMAL_LINK_REDUCTION_NO_GO", "constructive endpoint")
    require(constructive["classification"] == "FINITE_EXACT_COMPUTATION", "constructive class")
    require((constructive["support_factor_initial_forms"], constructive["support_parent_initial_forms"]) == (7078, 140), "initial-form census")
    require(constructive["ordinary_common_radial_strict_parent_link"] == "EMPTY_ON_BOTH_SUPPORTS", "ordinary link")
    require(constructive["gordan_obstructions"] == 2, "Gordan census")
    require(constructive["weighted_blowups"] == "OPEN", "weighted scope")
    require(constructive["artifact_sha256"] == ARTIFACTS[constructive["artifact"]], "constructive artifact")
    require(constructive["semantic_sha256"] == "f2169e2bc90f9c92d49f754d695b34b9dc3da770a3aecf6bfb6e84a6cb80b747", "constructive semantic")
    falsifier = cycle["falsifier_gate"]
    require(falsifier["status"] == "NORMAL_LINK_REDUCTION_NO_GO", "falsifier endpoint")
    require(falsifier["classification"] == "FINITE_EXACT_RECURSIVE_FACET_WALL", "falsifier class")
    require((falsifier["factor_id"], falsifier["factor"], falsifier["support"]) == (8552, "d*i-e", [3, 1, 15]), "factor witness")
    require(falsifier["recursive_parent_facet"] == "1237", "recursive facet")
    require(falsifier["exact_same_stratum_lifts"] == 3, "lift census")
    require(falsifier["strict_open_parent_crossing"] is False, "strict crossing overclaim")
    require(falsifier["artifact_sha256"] == ARTIFACTS[falsifier["artifact"]], "falsifier artifact")
    require(falsifier["semantic_sha256"] == "95631d5d6192e9ff86ab04a3bb065e849a4b592be24a752c1cade41d669cf666", "falsifier semantic")
    certificate = cycle["certificate_gate"]
    require(certificate == {
        "status": "VERSIONED_FAIL_CLOSED_ENVELOPE",
        "producer_payload": "ABSENT_BY_DESIGN",
        "independent_active_factor_classes": 3539,
        "independent_aligned_occurrences": 5026,
        "semantic_sha256": "a1b9d3d9da1e01df83621dc8f1c7959f86ae2e0d9bd3bc457124c561cbac245a",
    }, "certificate gate")
    referee = cycle["referee_gate"]
    require(referee == {
        "verdict": "ACCEPT",
        "classification": "FINITE_EXACT_LOCAL_NORMAL_LINK_ROUTE_NO_GO",
        "adapter": "INDEPENDENTLY_REDERIVES_TWO_FROZEN_WITNESS_METHODS",
        "hostile_mutations_rejected": 16,
        "semantic_sha256": "877ee39e97c9cc721fb2cc578618701953f8436fce128c3cba54fdf2026d4809",
    }, "referee gate")
    require(cycle["exact_consequence"] ==
        "THE_TANGENTIAL_FOUR_SUPPORT_REDUCTION_AND_ORDINARY_COMMON_RADIAL_LINK_ARE_INVALID_FOR_THE_SELECTED_S1237_COLLAR_ROUTE",
        "consequence")
    require(set(cycle["nonconsequences"]) == {
        "NO_STRICT_OPEN_PARENT_SEPARATOR",
        "NO_WEIGHTED_RECURSIVE_LINK_CLASSIFICATION",
        "NO_COLLAR_OR_MINCUT",
        "NO_GLOBAL_ACTIVE_SECTOR_CONNECTIVITY_OR_DISCONNECTION",
        "NO_DIAGONAL_9_PROOF_OR_COUNTEREXAMPLE",
        "NO_9DVL_SCORE_CHANGE",
    }, "nonconsequences")
    require(cycle["route_disposition"] ==
        "SELECTED_NORMAL_LINK_GATE_CLOSED_NEGATIVELY_AND_ROUTE_RETIRED",
        "cycle disposition")
    require(state["selected_target"] is None, "selected target")
    require(state["target_selection"] == "PENDING_FRESH_INDEPENDENT_OPENING_AUDIT", "next selection")
    require(set(state["process_gates"]) == PROCESS_GATES, "process gate census")
    require(all(state["process_gates"].values()), "process gates")

    if check_files:
        require(sha256(PREDECESSOR) == PREDECESSOR_SHA256, "predecessor bytes")
        require(
            sha256(PREDECESSOR_VERIFIER) == PREDECESSOR_VERIFIER_SHA256,
            "predecessor verifier bytes",
        )
        require(git("rev-parse", f"{BASE}^{{tree}}") == BASE_TREE, "base tree")
        require(git("rev-parse", f"{OPENING}^{{tree}}") == OPENING_TREE, "opening tree")
        require(git("rev-parse", f"{REVIEWED}^{{tree}}") == REVIEWED_TREE, "reviewed tree")
        require(git("rev-parse", f"{REFEREE}^{{tree}}") == REFEREE_TREE, "referee tree")
        for relative, digest in ARTIFACTS.items():
            require(sha256(ROOT / relative) == digest, f"artifact drift {relative}")
        status = STATUS.read_text(encoding="utf-8")
        require("## Current canonical precedence after the D9 S12,37 normal-link cycle" in status, "status authority heading")
        require("ordinary common-radial strict parent link is singular" in status, "status no-go")
        require("weighted recursive links remain open" in status, "status weighted scope")
        readme = README.read_text(encoding="utf-8")
        require("CANONICAL_RESEARCH_STATE_V3.json" in readme, "README authority")
        require("D9 S12,37 normal-link route closed negatively" in readme, "README cycle result")
        operating = OPERATING_SYSTEM.read_text(encoding="utf-8")
        require("data/CANONICAL_RESEARCH_STATE_V3.json" in operating, "operating-system authority")
        require("GitHub remains read-only" in operating, "operating-system GitHub gate")


def hostile_canaries(state):
    cases = []

    def mutated(callback):
        candidate = copy.deepcopy(state)
        callback(candidate)
        return candidate

    cases.extend((
        ("score", mutated(lambda x: x["theorem"].__setitem__("score", "3/9"))),
        ("diagonal9", mutated(lambda x: x["theorem"]["proved_diagonals"].append(9))),
        ("selected-target", mutated(lambda x: x.__setitem__("selected_target", "D9_WEIGHTED_BLOWUP"))),
        ("github-write", mutated(lambda x: x["repository"].__setitem__("github_mode", "WRITE_ALLOWED"))),
        ("weighted-closed", mutated(lambda x: x["completed_cycle"]["constructive_gate"].__setitem__("weighted_blowups", "CLOSED"))),
        ("strict-crossing", mutated(lambda x: x["completed_cycle"]["falsifier_gate"].__setitem__("strict_open_parent_crossing", True))),
        ("referee", mutated(lambda x: x["completed_cycle"]["referee_gate"].__setitem__("verdict", "PENDING"))),
        ("promotion", mutated(lambda x: x["completed_cycle"]["nonconsequences"].remove("NO_DIAGONAL_9_PROOF_OR_COUNTEREXAMPLE"))),
        ("route", mutated(lambda x: x["inherited_route_dispositions"].pop("D9_S1237_TANGENTIAL_FOUR_SUPPORT_REDUCTION"))),
        ("local-global", mutated(lambda x: x["process_gates"].__setitem__("local_recursive_facet_wall_is_not_a_global_separator", False))),
        ("missing-gate", mutated(lambda x: x["process_gates"].pop("independent_exact_head_review_passed"))),
        ("predecessor", mutated(lambda x: x["predecessor"].__setitem__("sha256", "0" * 64))),
    ))
    rejected = []
    for name, candidate in cases:
        try:
            validate(candidate, check_files=False)
        except (KeyError, Reject):
            rejected.append(name)
        else:
            raise Reject(f"hostile canary accepted: {name}")
    return tuple(rejected)


def replay(path: Path, expected: str) -> None:
    result = subprocess.run(
        [sys.executable, str(path)], cwd=ROOT,
        capture_output=True, text=True, check=False,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    require(result.returncode == 0, f"replay failed {path}: {result.stderr[-500:]}")
    require(expected in result.stdout, f"replay output drift {path}")


def main():
    state = json.loads(STATE.read_text(encoding="utf-8"))
    validate(state)
    rejected = hostile_canaries(state)
    replay(PREDECESSOR_VERIFIER, "PASS canonical 9DVL research state v2")
    replay(REFEREE_VERIFIER, "ACCEPT NORMAL_LINK_REDUCTION_NO_GO")
    print("PASS canonical 9DVL research state v3")
    print("PASS predecessor post-mask-6 state remains immutable")
    print("PASS D9 S12,37 normal-link route closed negatively and retired")
    print("PASS hostile state canaries:", len(rejected), "/", len(rejected))
    print("PASS theorem ledger unchanged at 2/9; no selected next target")


if __name__ == "__main__":
    main()
