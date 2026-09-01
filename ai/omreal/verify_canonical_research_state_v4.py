#!/usr/bin/env python3
"""Verify the post-universal-D9-cut canonical research state."""

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
STATE = HERE / "data/CANONICAL_RESEARCH_STATE_V4.json"
PREDECESSOR = HERE / "data/CANONICAL_RESEARCH_STATE_V3.json"
STATUS = HERE / "NINE_DIAGONAL_STATUS_V4.md"
OPERATING_SYSTEM = HERE / "RESEARCH_OPERATING_SYSTEM.md"
README = ROOT / "README.md"

PREDECESSOR_SHA256 = "e37fad74fae83cf087b2010039e85122866c3b093e34227f28d12759be94a6cf"
BASE = "cbe84ccd7273252c81fd4da17ee360a284d2a2a6"
BASE_TREE = "da3cd6feca1052ea14ed5036413c72b8f7fadc2a"
OPENING = "6cbd1b4a7d3ed61bee268b6b54cbfadeece90f0e"
OPENING_TREE = "84eaf80b30e1f366b8f959bd6435a217762636b3"
EVIDENCE = "9cb3652b00c0a07901b6fa32dd3f7d03987cfb66"
EVIDENCE_TREE = "37f605949a2fbfdf8be8983b6ea24121eea4a177"
REVIEWED = "39035a9c35b27a9893db393dbb8a9ec1b621754d"
REVIEWED_TREE = "e05535180e3522521f5f151f956a9f407f5a2956"
REFEREE = "6bbfb4b728bb92d993ea0faf4e88dde572abd9ea"
REFEREE_TREE = "b52ef7fbdf42b3cfd8e3c66f98ced5406c3b7db9"

ARTIFACTS = {
    "ops/research-team/cycles/2026-09-01-d9-universal-cut/CLOSING_CANDIDATE.json":
        "4e77e375742bea1f3f6213b7acb06e3d63627ad06002da3862e8ba774f05e303",
    "ops/research-team/cycles/2026-09-01-d9-universal-cut/CYCLE_REPORT.md":
        "63dfc93531334a2ff944716f0de9c6de1a95947072dd66632821d2e9cb49b73a",
    "ops/research-team/cycles/2026-09-01-d9-universal-cut/verify_closing_candidate.py":
        "16bde8dd853cb9354681151b8ed95bfccb41e43bfc13d77e129d7f9acbce8ecf",
    "ops/team/d9-universal-cut-referee/RESULT.json":
        "bc18384f4e808b60b01bc79e0688ed539a52784431ed243d7af6c225e83d9b84",
    "ops/team/d9-universal-cut-referee/CLOSING_MANIFEST.json":
        "e3bf5be554c444735c349bd89c07baf48e2b9fe697d81df5b9d4d8a388a161e5",
    "ops/team/d9-universal-cut-referee/FINDINGS.md":
        "635ca32ae49b154fab0d9b1a1b1f5b1ce2834524ec624799a53d5f572f3769a5",
    "ops/team/d9-universal-cut-referee/verify_closing_referee.py":
        "5554a1f3c73700f7da6ef1d9e51ca204f1327962ce90e8e08730e82d5eff07cc",
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
    "D9_UNIVERSAL_MEMORYLESS_13_TYPE_CUT_GRAMMAR":
        "RETIRED_UNTIL_GLOBAL_ATTACHMENT_AND_PROJECTION_CLOSURE_INPUTS",
}

NONCONSEQUENCES = {
    "NO_SOURCE_REALIZED_D9_COUNTEREXAMPLE",
    "NO_UNIVERSAL_D9_CUT_COVERAGE_THEOREM",
    "NO_EXHAUSTIVE_OBSTRUCTION_UNSAT_RESULT",
    "NO_STRICT_OPEN_PARENT_SEPARATOR",
    "NO_WEIGHTED_RECURSIVE_LINK_CLASSIFICATION",
    "NO_DIAGONAL_9_RESULT",
    "NO_9DVL_SCORE_CHANGE",
}

PROCESS_GATES = {
    "theorem_score_promotion_requires_all_invariant_obligations_closed",
    "opening_failure_prohibits_main_census",
    "abstract_countermodel_is_not_a_source_d9_counterexample",
    "recursive_facet_wall_is_not_a_strict_parent_separator",
    "source_discrepancy_is_preserved_and_non_load_bearing",
    "portable_predecessor_replay_replaces_historical_object_dependency",
    "independent_exact_head_review_passed",
    "github_remains_read_only_until_new_explicit_user_instruction",
}


class Reject(AssertionError):
    """A fail-closed canonical-state rejection."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def validate(state: dict, check_files: bool = True) -> None:
    require(set(state) == {
        "format", "status", "as_of", "repository", "predecessor", "theorem",
        "inherited_open_obligations", "inherited_route_dispositions",
        "completed_cycle", "selected_target", "target_selection", "process_gates",
    }, "top-level fields")
    require(state["format"] == "9dvl-canonical-research-state-v4", "format")
    require(state["status"] == "PIVOT_REQUIRED", "status")
    require(state["as_of"] == "2026-09-01", "date")
    require(state["repository"] == {
        "full_name": "reuellee/finite-certificates",
        "default_branch": "main",
        "canonical_storage": "CHATGPT_LIBRARY",
        "recovery_mirror": "GOOGLE_DRIVE_PROJECTS_RESEARCH_BACKUPS",
        "github_mode": "READ_ONLY_UNTIL_NEW_EXPLICIT_USER_INSTRUCTION",
        "cycle_base_commit": BASE,
        "cycle_base_tree": BASE_TREE,
        "reviewed_candidate_commit": REVIEWED,
        "reviewed_candidate_tree": REVIEWED_TREE,
        "integrated_referee_commit": REFEREE,
        "integrated_referee_tree": REFEREE_TREE,
    }, "repository")
    require(state["predecessor"] == {
        "path": "ai/omreal/data/CANONICAL_RESEARCH_STATE_V3.json",
        "sha256": PREDECESSOR_SHA256,
        "policy": "IMMUTABLE_POST_D9_NORMAL_LINK_STATE",
    }, "predecessor")
    require(state["theorem"] == {
        "id": "9DVL", "score": "2/9", "proved_diagonals": [1, 2],
        "active_diagonal": None, "promotion": "NONE",
    }, "theorem")
    obligations = state["inherited_open_obligations"]
    require(obligations["diag3_triple_hc0"] == {
        "status": "OPEN", "residue": 1162302,
        "first_missing_global_object": "Q3_COMPLETE_PARENT_BOUNDARY_ATLAS",
    }, "D3 triple")
    require(obligations["diag4_sp"] == {
        "status": "OPEN", "survivor_labeled": 800240, "survivor_orbits": 53,
    }, "D4")
    require(all(obligations[key] == "OPEN" for key in (
        "diag3_pair_hc1", "diag8_h1", "diag9_h0"
    )), "open obligations")
    require(state["inherited_route_dispositions"] == RETIRED, "route dispositions")

    cycle = state["completed_cycle"]
    require(cycle["id"] == "2026-09-01-d9-universal-cut", "cycle id")
    require(cycle["selected_target"] == "D9_UNIVERSAL_FEASIBLE_COMPONENT_CUT_GATE1", "target")
    require(cycle["opening_verdict"] == "PIVOT_SELECT", "opening verdict")
    require((cycle["opening_commit"], cycle["opening_tree"]) == (OPENING, OPENING_TREE), "opening binding")
    require((cycle["evidence_commit"], cycle["evidence_tree"]) == (EVIDENCE, EVIDENCE_TREE), "evidence binding")
    require((cycle["reviewed_candidate_commit"], cycle["reviewed_candidate_tree"]) == (REVIEWED, REVIEWED_TREE), "review binding")
    require((cycle["referee_commit"], cycle["referee_tree"]) == (REFEREE, REFEREE_TREE), "referee binding")
    opening = cycle["opening_gate"]
    require(opening == {
        "status": "FAILED_CLOSED",
        "requirement_verdicts": ["FAIL", "FAIL", "FAIL", "PASS", "PASS"],
        "mathematical_endpoint": "UNIVERSAL_CUT_SCHEMA_COVERAGE_GAP",
        "classification": "EXACT_NULL_GLOBAL_COVERAGE_AND_ATTACHMENT_NO_GO",
        "main_census_authorized": False,
        "main_census_started": False,
    }, "opening gate")
    structural = cycle["structural_gate"]
    require(structural["conditional_master_stratification_reduction"] == "PROVED", "conditional reduction")
    require((structural["residual_local_types"], structural["first_projection_gap_type"]) == (13, 36), "type census")
    require(structural["first_projection_gap_polynomial"] == "c*d-c+f", "projection polynomial")
    require(structural["first_layer_new_irreducibles"] == 142, "projection layer")
    require(structural["new_irreducible_degree_census"] == {"2": 23, "3": 71, "4": 43, "5": 5}, "degree census")
    require((structural["parent_brackets_checked"], structural["global_residual_factors_checked"]) == (70, 26740), "source catalogs")
    require(structural["projection_closed"] is False, "projection scope")
    circuits = cycle["circuit_gate"]
    require((circuits["one_sided_specialization_cospans"], circuits["opposite_partner_pairs"], circuits["persistent_support_candidates"]) == (13, 671, 2420), "circuit frontier")
    require(circuits["abstract_counterpair_chambers"] == 16, "counterpair")
    require(circuits["local_observations_identical"] is True, "local identity")
    require(circuits["positive_component_counts"] == [2, 1], "component contrast")
    require(circuits["counterpair_source_realized_uom_4_8"] is False, "counterpair scope")
    require((circuits["displayed_auxiliary_rows_sum"], circuits["printed_auxiliary_total"]) == (123, 131), "source discrepancy")
    require(circuits["source_discrepancy"] == "NON_LOAD_BEARING_ARITHMETIC_TYPO", "discrepancy scope")
    boundary = cycle["boundary_gate"]
    require((boundary["factor_id"], boundary["factor"], boundary["recursive_parent_facet"]) == (8552, "d*i-e", "1237"), "boundary factor")
    require(boundary["exact_lift_signs"] == ["-", "0", "+"], "boundary signs")
    require(boundary["boundary_charts"] == 64, "boundary charts")
    require(boundary["strict_open_parent_crossing"] is False and boundary["global_separator"] is False, "boundary scope")
    require(boundary["weighted_strict_coface"] == "NOT_CERTIFIED", "weighted scope")
    falsifier = cycle["falsifier_gate"]
    require(falsifier == {
        "classification": "FINITE_EXACT_LOGICAL_NO_GO_PLUS_NULL_ACTUAL_D9",
        "ordered_noninclusions": 72,
        "memoryless_local_to_global_inference": "REFUTED",
        "source_realized_d9_counterexample": "NOT_FOUND",
        "first_missing_discriminator": "GLOBAL_COMPONENT_FAITHFUL_SIGN_GEODESY_OR_EQUIVALENT_ATTACHMENT_OBJECT",
    }, "falsifier gate")
    certificate = cycle["certificate_gate"]
    require(certificate == {
        "status": "VERSIONED_ENDPOINT_NEUTRAL_FAIL_CLOSED_ENVELOPE",
        "endpoint_fixtures": 4,
        "hostile_mutations_rejected": 32,
        "live_universal_coverage_adapter": False,
        "portable_predecessor_census": "3539/6167/5026/70/16",
        "historical_referee_object_required": False,
    }, "certificate gate")
    referee = cycle["referee_gate"]
    require(referee == {
        "verdict": "ACCEPT",
        "accepted_scope": "FAIL_CLOSED_NULL_ENDPOINT",
        "source_pin_declarations": 87,
        "unique_source_paths": 51,
        "hostile_mutations_rejected": 20,
        "semantic_sha256": "125899bfe61b72f521b1c48abadd9d726a0053e6187f175a221a5d8845750ca3",
    }, "referee gate")
    require(cycle["exact_consequence"] == "THE_MEMORYLESS_13_TYPE_LOCAL_GRAMMAR_IS_NOT_A_COMPLETE_UNIVERSAL_D9_CUT_SCHEMA_AND_THE_OPENING_GATE_FAILS_CLOSED", "consequence")
    require(set(cycle["nonconsequences"]) == NONCONSEQUENCES, "nonconsequences")
    require(cycle["route_disposition"] == "RETIRED_UNTIL_GLOBAL_ATTACHMENT_AND_PROJECTION_CLOSURE_INPUTS", "cycle disposition")
    require(state["selected_target"] is None, "selected target")
    require(state["target_selection"] == "PENDING_FRESH_INDEPENDENT_OPENING_AUDIT", "target selection")
    require(set(state["process_gates"]) == PROCESS_GATES, "process gate census")
    require(all(state["process_gates"].values()), "process gates")

    if check_files:
        require(sha256(PREDECESSOR) == PREDECESSOR_SHA256, "predecessor bytes")
        for commit, tree, label in (
            (BASE, BASE_TREE, "base"), (OPENING, OPENING_TREE, "opening"),
            (EVIDENCE, EVIDENCE_TREE, "evidence"), (REVIEWED, REVIEWED_TREE, "reviewed"),
            (REFEREE, REFEREE_TREE, "referee"),
        ):
            require(git("rev-parse", f"{commit}^{{tree}}") == tree, f"{label} tree")
        for relative, digest in ARTIFACTS.items():
            require(sha256(ROOT / relative) == digest, f"artifact drift {relative}")
        status = STATUS.read_text(encoding="utf-8")
        require("## Current canonical precedence after the universal D9 cut opening gate" in status, "status heading")
        require("142 new first-layer" in status, "status projection gap")
        require("memoryless 13-type local grammar" in status, "status global memory")
        readme = README.read_text(encoding="utf-8")
        require("CANONICAL_RESEARCH_STATE_V4.json" in readme, "README authority")
        require("universal D9 cut opening gate failed closed" in readme, "README result")
        operating = OPERATING_SYSTEM.read_text(encoding="utf-8")
        require("data/CANONICAL_RESEARCH_STATE_V4.json" in operating, "operating authority")
        require("GitHub remains read-only" in operating, "GitHub gate")


def hostile_canaries(state: dict) -> tuple[str, ...]:
    cases = []

    def mutated(callback):
        candidate = copy.deepcopy(state)
        callback(candidate)
        return candidate

    cases.extend((
        ("score", mutated(lambda x: x["theorem"].__setitem__("score", "3/9"))),
        ("promotion", mutated(lambda x: x["theorem"].__setitem__("promotion", "D9"))),
        ("opening", mutated(lambda x: x["completed_cycle"]["opening_gate"].__setitem__("status", "PASSED"))),
        ("census", mutated(lambda x: x["completed_cycle"]["opening_gate"].__setitem__("main_census_authorized", True))),
        ("projection", mutated(lambda x: x["completed_cycle"]["structural_gate"].__setitem__("projection_closed", True))),
        ("counterexample", mutated(lambda x: x["completed_cycle"]["circuit_gate"].__setitem__("counterpair_source_realized_uom_4_8", True))),
        ("separator", mutated(lambda x: x["completed_cycle"]["boundary_gate"].__setitem__("global_separator", True))),
        ("adapter", mutated(lambda x: x["completed_cycle"]["certificate_gate"].__setitem__("live_universal_coverage_adapter", True))),
        ("referee", mutated(lambda x: x["completed_cycle"]["referee_gate"].__setitem__("verdict", "REJECT"))),
        ("successor", mutated(lambda x: x.__setitem__("selected_target", "D9_TYPE36_CLOSURE"))),
        ("route", mutated(lambda x: x["inherited_route_dispositions"].pop("D9_UNIVERSAL_MEMORYLESS_13_TYPE_CUT_GRAMMAR"))),
        ("github", mutated(lambda x: x["repository"].__setitem__("github_mode", "WRITE_ALLOWED"))),
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


def replay(relative: str, markers: tuple[str, ...]) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / relative)], cwd=ROOT, check=False,
        capture_output=True, text=True, timeout=600,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"},
    )
    require(result.returncode == 0, f"replay failed {relative}: {result.stderr[-1000:]}")
    for marker in markers:
        require(marker in result.stdout, f"missing marker {relative}: {marker}")


def main() -> None:
    state = json.loads(STATE.read_text(encoding="utf-8"))
    validate(state)
    rejected = hostile_canaries(state)
    replay("ops/team/d9-universal-cut-referee/verify_closing_referee.py", (
        "ACCEPT UNIVERSAL_CUT_SCHEMA_COVERAGE_GAP",
        "independent hostile mutations 20/20",
    ))
    replay("ops/team/d9-universal-cut-certificate/verify_portable_predecessor.py", (
        "ACCEPT PORTABLE_PREDECESSOR_REPLAY NORMAL_LINK_REDUCTION_NO_GO",
        "ca730426 is recorded as absent and never dereferenced",
    ))
    print("PASS canonical 9DVL research state v4")
    print("PASS universal D9 cut opening gate failed closed; main census denied")
    print("PASS hostile state canaries:", len(rejected), "/", len(rejected))
    print("PASS theorem ledger unchanged at 2/9; next state PIVOT_REQUIRED")


if __name__ == "__main__":
    main()
