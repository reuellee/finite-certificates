#!/usr/bin/env python3
"""Independent frozen-candidate closing referee for the D3 mixed-100 gate."""

from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = HERE / "RESULT.json"
MANIFEST_OUTPUT = HERE / "SOURCE_MANIFEST.json"

CYCLE_ID = "2026-09-03-d3-mixed-block-100-universal-carrier-gate1"
CYCLE_ROOT = f"ops/research-team/cycles/{CYCLE_ID}"
BASE = "fb667bfe33ef9e945a82e9a23b615e67f5f39c0f"
BASE_TREE = "117850b25cd94f865cb85e681c465b8260dd9c6a"
OPENING = "1c6519d89335dde215e93887de074ea4e6d6464a"
OPENING_TREE = "ff8a33e13952e86b27f184e3d8c40e768fbeb110"
CONSTRUCTOR_LANE = "35346bf6093c83d77b24227b660a36760a60b319"
CONSTRUCTOR_INTEGRATED = "a92c459340d0f76c3578a49f10cbb7968d07c156"
FALSIFIER_LANE = "88e20c2e0f4837eaa46787e5cdd564001de5d23c"
FALSIFIER_INTEGRATED = "833d61bd0702529c892c9b37ad8a2ee5c7b8b972"
MIDPOINT = "69983136e6f222ede46433da12a674dda613244e"
VERIFIER_LANE = "e92c489d703c1e1adc9365b66884f5cb03322287"
VERIFIER_INTEGRATED = "78738358b76157a68d6b46b8367d902ff0b0a8af"
CANDIDATE = "a2d78f9c30c13dc199b60355829a862ae7eec54a"
CANDIDATE_TREE = "3328a17a00c38c76129dc9a7385fba9f9cbfaaff"
PREDECESSOR_REPORT = (
    "ops/research-team/cycles/"
    "2026-09-02-d3-triple-critical-saturation-component-gate1/CYCLE_REPORT.md"
)
PREDECESSOR_MANIFEST = (
    "ops/research-team/cycles/"
    "2026-09-02-d3-triple-critical-saturation-component-gate1/CLOSING_MANIFEST.json"
)
CANONICAL = "ai/omreal/data/CANONICAL_RESEARCH_STATE_V10.json"
OPEN_VECTOR = [
    "2/9", 1, ["diag3_pair_hc1", "diag3_triple_hc0"], 7,
    "UNKNOWN", "UNKNOWN", 8, 11,
]
CLOSE_VECTOR = [
    "2/9", 1, ["diag3_pair_hc1", "diag3_triple_hc0"], 7,
    "UNKNOWN", "UNKNOWN", 9, 12,
]
ROUTE = ["O3_universal_mixed_chain", "O4_arbitrary_flag_coherence"]

SOURCE_PATHS = [
    "ops/research-team/PROTOCOL.md",
    CANONICAL,
    PREDECESSOR_MANIFEST,
    PREDECESSOR_REPORT,
    f"{CYCLE_ROOT}/CYCLE.md",
    f"{CYCLE_ROOT}/WORK_ORDERS.yaml",
    f"{CYCLE_ROOT}/OPENING_STATE.json",
    f"{CYCLE_ROOT}/verify_opening_state.py",
    f"{CYCLE_ROOT}/MID_CYCLE_CHECKPOINT.json",
    f"{CYCLE_ROOT}/verify_mid_cycle.py",
    f"{CYCLE_ROOT}/CLOSING_CANDIDATE.json",
    f"{CYCLE_ROOT}/CYCLE_REPORT.md",
    f"{CYCLE_ROOT}/verify_closing_candidate.py",
    "ops/team/d3-mixed-100-carrier-constructor/THEOREM_ATTEMPT.md",
    "ops/team/d3-mixed-100-carrier-constructor/RESULT.json",
    "ops/team/d3-mixed-100-carrier-constructor/SOURCE_MANIFEST.json",
    "ops/team/d3-mixed-100-carrier-constructor/verify_constructor.py",
    "ops/team/d3-mixed-100-carrier-falsifier/FINDINGS.md",
    "ops/team/d3-mixed-100-carrier-falsifier/RESULT.json",
    "ops/team/d3-mixed-100-carrier-falsifier/SOURCE_MANIFEST.json",
    "ops/team/d3-mixed-100-carrier-falsifier/interface_independence_fixture.json",
    "ops/team/d3-mixed-100-carrier-falsifier/verify_falsifier.py",
    "ops/team/d3-mixed-100-independent-verifier/REVIEW.md",
    "ops/team/d3-mixed-100-independent-verifier/RESULT.json",
    "ops/team/d3-mixed-100-independent-verifier/SOURCE_MANIFEST.json",
    "ops/team/d3-mixed-100-independent-verifier/verify_independent.py",
]


class Reject(AssertionError):
    """The frozen candidate fails one independent closing condition."""


def require(condition: bool, marker: str) -> None:
    if not condition:
        raise Reject(marker)


def git(*arguments: str, binary: bool = False):
    return subprocess.check_output(
        ["git", *arguments], cwd=ROOT, text=not binary
    )


def revision_tree(revision: str) -> str:
    return git("show", "-s", "--format=%T", revision).strip()


def revision_parents(revision: str) -> list[str]:
    raw = git("show", "-s", "--format=%P", revision).strip()
    return raw.split() if raw else []


def frozen_bytes(path: str, revision: str = CANDIDATE) -> bytes:
    return git("show", f"{revision}:{path}", binary=True)


def frozen_json(path: str, revision: str = CANDIDATE) -> dict:
    return json.loads(frozen_bytes(path, revision).decode("utf-8"))


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def pin(path: str, revision: str = CANDIDATE) -> dict:
    data = frozen_bytes(path, revision)
    return {
        "path": path,
        "revision": revision,
        "bytes": len(data),
        "sha256": digest(data),
    }


def changed_paths(older: str, newer: str) -> list[str]:
    return [
        line.strip()
        for line in git("diff", "--name-only", older, newer).splitlines()
        if line.strip()
    ]


def tree_listing(revision: str, prefix: str) -> str:
    return git("ls-tree", "-r", revision, "--", prefix)


def reconstruct() -> tuple[dict, dict]:
    # Immutable object graph.
    require(git("rev-parse", CANDIDATE).strip() == CANDIDATE, "candidate commit")
    require(revision_tree(CANDIDATE) == CANDIDATE_TREE, "candidate tree")
    require(revision_parents(CANDIDATE) == [VERIFIER_INTEGRATED], "candidate parent")
    require(revision_tree(BASE) == BASE_TREE, "base tree")
    require(revision_tree(OPENING) == OPENING_TREE, "opening tree")
    require(revision_parents(OPENING) == [BASE], "opening parent")
    require(revision_parents(CONSTRUCTOR_LANE) == [OPENING], "constructor lane parent")
    require(revision_parents(CONSTRUCTOR_INTEGRATED) == [OPENING], "constructor integration parent")
    require(revision_tree(CONSTRUCTOR_LANE) == revision_tree(CONSTRUCTOR_INTEGRATED), "constructor integration tree")
    require(revision_parents(FALSIFIER_LANE) == [OPENING], "falsifier lane parent")
    require(revision_parents(FALSIFIER_INTEGRATED) == [CONSTRUCTOR_INTEGRATED], "falsifier integration parent")
    require(revision_parents(MIDPOINT) == [FALSIFIER_INTEGRATED], "midpoint parent")
    require(revision_parents(VERIFIER_LANE) == [MIDPOINT], "verifier lane parent")
    require(revision_parents(VERIFIER_INTEGRATED) == [MIDPOINT], "verifier integration parent")
    require(revision_tree(VERIFIER_LANE) == revision_tree(VERIFIER_INTEGRATED), "verifier integration tree")

    role_prefixes = {
        "constructor": "ops/team/d3-mixed-100-carrier-constructor/",
        "falsifier": "ops/team/d3-mixed-100-carrier-falsifier/",
        "verifier": "ops/team/d3-mixed-100-independent-verifier/",
    }
    lane_specs = {
        "constructor": (OPENING, CONSTRUCTOR_LANE),
        "falsifier": (OPENING, FALSIFIER_LANE),
        "verifier": (MIDPOINT, VERIFIER_LANE),
    }
    lane_paths: dict[str, list[str]] = {}
    for name, (older, newer) in lane_specs.items():
        paths = changed_paths(older, newer)
        require(paths and all(path.startswith(role_prefixes[name]) for path in paths), f"{name} lane scope")
        lane_paths[name] = paths
    require(
        tree_listing(FALSIFIER_LANE, role_prefixes["falsifier"])
        == tree_listing(FALSIFIER_INTEGRATED, role_prefixes["falsifier"]),
        "falsifier integration bytes",
    )

    # Full changed surface: 22 current governed paths and one disclosed,
    # append-only predecessor report reconciliation.
    changes = changed_paths(BASE, CANDIDATE)
    allowed_prefixes = (
        CYCLE_ROOT + "/",
        role_prefixes["constructor"],
        role_prefixes["falsifier"],
        role_prefixes["verifier"],
    )
    exceptions = [path for path in changes if not path.startswith(allowed_prefixes)]
    require(len(changes) == 23, "changed path count")
    require(exceptions == [PREDECESSOR_REPORT], "changed surface exception")
    numstat = git("diff", "--numstat", BASE, CANDIDATE, "--", PREDECESSOR_REPORT).strip().split()
    require(numstat[:2] == ["29", "0"], "predecessor report amendment must be insertion-only")

    predecessor_manifest = frozen_json(PREDECESSOR_MANIFEST, BASE)
    predecessor_pin = predecessor_manifest["evidence_pins"][PREDECESSOR_REPORT]
    predecessor_original = frozen_bytes(PREDECESSOR_REPORT, BASE)
    require(len(predecessor_original) == predecessor_pin["bytes"], "predecessor original bytes")
    require(digest(predecessor_original) == predecessor_pin["sha256"], "predecessor original digest")
    amended_report = frozen_bytes(PREDECESSOR_REPORT).decode("utf-8")
    require("## Mandatory solution-convergence verdict" in amended_report, "amendment disclosure")
    normalized_amended_report = " ".join(amended_report.split())
    require("changes no mathematical or governance conclusion" in normalized_amended_report, "amendment boundary")

    # Canonical and source pins.
    canonical_at_base = frozen_bytes(CANONICAL, BASE)
    canonical_at_candidate = frozen_bytes(CANONICAL)
    require(canonical_at_candidate == canonical_at_base, "canonical V10 changed")
    source_manifest = {
        "format": "d3-mixed-100-independent-closing-referee-source-manifest-v1",
        "cycle_id": CYCLE_ID,
        "track_id": "d3-mixed-100-closing-referee",
        "candidate_commit": CANDIDATE,
        "candidate_tree": CANDIDATE_TREE,
        "sources": [pin(path) for path in SOURCE_PATHS],
        "predecessor_original_report": pin(PREDECESSOR_REPORT, BASE),
        "network_sources": [],
        "producer_modules_imported": False,
        "notes": [
            "Every source is read from the immutable candidate Git object, not accepted from the worktree.",
            "The predecessor original report is separately pinned at the immutable base and rechecked against its closing manifest.",
            "Producer verifier programs are source-pinned but are not imported as closing acceptance logic.",
        ],
    }

    # Frozen records, read as untrusted data.
    opening = frozen_json(f"{CYCLE_ROOT}/OPENING_STATE.json")
    midpoint = frozen_json(f"{CYCLE_ROOT}/MID_CYCLE_CHECKPOINT.json")
    candidate = frozen_json(f"{CYCLE_ROOT}/CLOSING_CANDIDATE.json")
    constructor = frozen_json("ops/team/d3-mixed-100-carrier-constructor/RESULT.json")
    constructor_manifest = frozen_json("ops/team/d3-mixed-100-carrier-constructor/SOURCE_MANIFEST.json")
    falsifier = frozen_json("ops/team/d3-mixed-100-carrier-falsifier/RESULT.json")
    falsifier_manifest = frozen_json("ops/team/d3-mixed-100-carrier-falsifier/SOURCE_MANIFEST.json")
    verifier = frozen_json("ops/team/d3-mixed-100-independent-verifier/RESULT.json")
    report = frozen_bytes(f"{CYCLE_ROOT}/CYCLE_REPORT.md").decode("utf-8")
    protocol = frozen_bytes("ops/research-team/PROTOCOL.md").decode("utf-8")
    work_orders = frozen_bytes(f"{CYCLE_ROOT}/WORK_ORDERS.yaml").decode("utf-8")
    cycle_policy = frozen_bytes(f"{CYCLE_ROOT}/CYCLE.md").decode("utf-8")

    require("Mandatory solution-convergence gate" in protocol, "protocol read")
    require("d3-mixed-100-closing-referee" in work_orders, "closing work order")
    require("clean frozen-head replay" in work_orders, "replay work order")
    require("every composable face flag" in cycle_policy, "cycle quantifier")
    require("STOP / NONE" in report and "NULL / STALLED / STOP / NONE" in report, "report verdict")

    require(opening["repository"]["base_revision"] == BASE, "opening base")
    require(opening["repository"]["base_tree"] == BASE_TREE, "opening base tree")
    require(opening["proof_distance"]["opening_vector"] == OPEN_VECTOR, "opening vector")
    require(opening["proof_distance"]["selected_route_open_residual"] == ROUTE, "opening route")
    require(opening["canonical"]["score"] == "2/9", "opening ledger")
    require(opening["canonical"]["pair_residual"] == opening["canonical"]["pair_coverage"] == "UNKNOWN", "opening pair accounting")
    require(opening["canonical"]["triple_residual"] == 1_162_302, "opening triple residual")
    require(sum(item.get("load_bearing", False) for item in opening["obligations"]) == 7, "opening obligations")

    require(midpoint["opening"]["commit"] == OPENING, "midpoint opening")
    require(midpoint["integrated_evidence"]["commit"] == FALSIFIER_INTEGRATED, "midpoint evidence")
    require(midpoint["verdict"]["constructor"] == midpoint["verdict"]["falsifier"] == "NULL", "midpoint null")
    require(midpoint["verdict"]["positive_token"] is None, "midpoint positive token")
    require(midpoint["verdict"]["negative_token"] is None, "midpoint negative token")
    require(midpoint["verdict"]["discovery_action"] == "FREEZE_NULL_AND_STOP", "midpoint action")
    require(midpoint["proof_distance"]["opening_vector"] == midpoint["proof_distance"]["midpoint_vector"] == OPEN_VECTOR, "midpoint vector")
    require(midpoint["proof_distance"]["minimum_acceptable_decrease_met"] is False, "midpoint decrease")
    require(midpoint["proof_distance"]["reachable_inside_remaining_ceiling"] is False, "midpoint reachability")

    require(constructor["constructor_self_acceptance"] is False, "constructor self acceptance")
    require(constructor["handoff"] == "NULL" and constructor["assessment"] == "NULL_STALLED_STOP", "constructor null")
    require(constructor["positive_token"] is None and constructor["negative_token"] is None, "constructor tokens")
    require(constructor["target_status"]["O3_proved"] is False, "constructor O3")
    require(constructor["target_status"]["O4_proved"] is False, "constructor O4")
    require(constructor["first_missing_edge"]["id"] == "O3_MIXED_GEOMETRIC_RELATIVE_BOUNDARY_SURJECTIVITY", "constructor gap")
    require(constructor_manifest["restrictions"]["producer_self_acceptance"] is False, "constructor manifest self acceptance")
    require(constructor_manifest["restrictions"]["falsifier_worktree_inspected"] is False, "constructor independence")

    require(falsifier["handoff"] == "NO_UNIVERSAL_OBSTRUCTION_FOUND_WITHIN_FROZEN_SCOPE", "falsifier null")
    require(falsifier["classification"] == "NULL", "falsifier classification")
    require(falsifier["universal_counterexample_found"] is False, "falsifier counterexample")
    require(falsifier["full_quantifier_negative_proved"] is False, "falsifier negative")
    require("O3" in falsifier["algebraic_kernel_cone_lemma"]["does_not_prove"], "formal cone scope")
    require(falsifier["finite_independence_fixture"]["actual_negative_instance"] is False, "empty carrier scope")
    require(falsifier["scope_compliance"]["constructor_worktree_inspected"] is False, "falsifier independence")
    require(falsifier_manifest["constructor_sources"] == [], "falsifier imported constructor")

    require(verifier["verdict"] == "NULL_STALLED_STOP_INDEPENDENTLY_CONFIRMED", "verifier verdict")
    require(verifier["positive_token"] is None and verifier["negative_token"] is None, "verifier tokens")
    require(verifier["acceptance"]["producer_agreement_used_as_acceptance"] is False, "verifier independence")
    require(verifier["acceptance"]["O3_universal_mixed_chain"] == "OPEN", "verifier O3")
    require(verifier["acceptance"]["O4_arbitrary_flag_coherence"] == "OPEN", "verifier O4")
    require(verifier["source_reconstruction"]["producer_verifier_code_imported_or_executed"] is False, "verifier code independence")
    require(verifier["formal_kernel_cone_lemma"]["proves_O3_or_O4"] is False, "verifier cone boundary")
    require(verifier["logical_non_entailment_boundary"]["non_entailment_is_an_exact_admissible_counterexample"] is False, "verifier negative boundary")

    result = candidate["result"]
    require(candidate["base"] == {"revision": BASE, "tree": BASE_TREE}, "candidate base")
    require(candidate["opening"] == {"revision": OPENING, "tree": OPENING_TREE}, "candidate opening")
    require(candidate["integrated_evidence"]["revision"] == VERIFIER_INTEGRATED, "candidate evidence")
    require(result["constructor"] == result["falsifier"] == "NULL", "candidate null")
    require(result["positive_token"] is None and result["negative_token"] is None, "candidate tokens")
    require(result["O3"] == result["O4"] == "OPEN", "candidate O3 O4")
    require(result["trajectory"] == "STALLED", "candidate trajectory")
    require(result["strategy_action"] == "STOP", "candidate action")
    require(result["selected_successor"] == "NONE" and result["same_route_continue"] is False, "candidate successor")

    finding = candidate["exact_finding"]
    require(finding["formal_kernel_cone"] == "EXACT_INTEGRAL_STRICTLY_FUNCTORIAL_ALGEBRAIC_CONTROL", "candidate cone")
    require(finding["formal_kernel_cone_is_geometric_carrier"] is False, "candidate geometry")
    require(finding["interface_entails_geometric_mixed_proper_realization"] is False, "candidate entailment")
    require(finding["empty_carrier_expansion_is_actual_admissible_9dvl_instance"] is False, "candidate empty model")
    require(finding["interface_non_entailment_is_full_negative"] is False, "candidate negative")
    require(finding["bounded_repair_available"] is False, "candidate repair")

    proof = candidate["proof_distance"]
    require(proof["opening_vector"] == proof["midpoint_vector"] == OPEN_VECTOR, "candidate opening midpoint")
    require(proof["closing_vector"] == CLOSE_VECTOR, "candidate closing vector")
    require(proof["selected_route_opening"] == proof["selected_route_closing"] == ROUTE, "candidate route")
    require(proof["selected_route_delta"] == 0, "candidate route delta")
    require(proof["minimum_acceptable_decrease_met"] is False, "candidate minimum decrease")

    accounting = candidate["accounting"]
    require(accounting["ledger_opening"] == accounting["ledger_closing"] == "2/9", "candidate ledger")
    require(accounting["ledger_delta"] == "0/9", "candidate ledger delta")
    require(accounting["canonical_open_obligations"] == 7, "candidate obligations")
    require(accounting["pair_residual"] == accounting["pair_coverage"] == "UNKNOWN", "candidate pair")
    require(accounting["triple_residual"] == 1_162_302, "candidate triple")
    require(accounting["formal_3_of_10_promoted"] is False, "candidate false denominator")
    require(accounting["theorem_or_counterexample_claimed"] is False, "candidate theorem claim")

    resources = candidate["resources"]
    opening_time = int(git("show", "-s", "--format=%ct", OPENING).strip())
    integrated_time = int(git("show", "-s", "--format=%ct", VERIFIER_INTEGRATED).strip())
    require(integrated_time - opening_time == resources["opening_to_independent_verifier_seconds"] == 1598, "resource elapsed")
    require(resources["opening_to_independent_verifier_seconds"] < resources["governed_ceiling_seconds"] == 14_400, "resource ceiling")
    require(resources["role_surface_bytes_before_close"] == 153_277, "role bytes")
    require(resources["constructor_handoffs"] == 1 and resources["verifier_directed_repairs"] == 0, "handoffs")
    require(resources["research_saturation_or_cad_jobs"] == resources["cloud_workers"] == resources["external_spend_usd"] == 0, "resource scope")
    require(resources["peak_ram_continuously_measured"] is False, "RAM boundary")
    require(all(value is False for value in candidate["scope"].values()), "candidate external scope")

    # Closing reconstruction. The no-hardlink replay is an observed review
    # fact from a fresh detached clone; acceptance logic above does not rely on
    # any producer verifier module.
    closure = {
        "format": "d3-mixed-100-independent-closing-referee-result-v1",
        "cycle_id": CYCLE_ID,
        "track_id": "d3-mixed-100-closing-referee",
        "status": "PASS",
        "verdict": "ACCEPT_EXACT_FROZEN_NULL_STALLED_STOP_NONE",
        "candidate": {
            "commit": CANDIDATE,
            "tree": CANDIDATE_TREE,
            "parent": VERIFIER_INTEGRATED,
        },
        "object_chain": {
            "base": {"commit": BASE, "tree": BASE_TREE},
            "opening": {"commit": OPENING, "tree": OPENING_TREE},
            "constructor_lane": CONSTRUCTOR_LANE,
            "constructor_integrated": CONSTRUCTOR_INTEGRATED,
            "falsifier_lane": FALSIFIER_LANE,
            "falsifier_integrated": FALSIFIER_INTEGRATED,
            "midpoint": MIDPOINT,
            "verifier_lane": VERIFIER_LANE,
            "verifier_integrated": VERIFIER_INTEGRATED,
        },
        "changed_surface": {
            "paths_from_base": len(changes),
            "current_cycle_or_role_paths": len(changes) - len(exceptions),
            "outside_current_prefixes": exceptions,
            "outside_change_disposition": "ACCEPT_DISCLOSED_INSERTION_ONLY_COORDINATOR_RECONCILIATION",
            "outside_additions": 29,
            "outside_deletions": 0,
            "immutable_predecessor_report_matches_its_close_manifest": True,
            "canonical_v10_byte_identical_to_base": True,
        },
        "lane_independence": {
            "constructor_and_falsifier_both_fork_from_opening": True,
            "falsifier_lane_contains_no_constructor_surface": True,
            "verifier_forks_after_both_handoffs_and_midpoint": True,
            "each_lane_changed_only_its_owned_surface": True,
            "producer_agreement_used_as_acceptance": False,
            "lane_changed_paths": lane_paths,
        },
        "theorem_gate": {
            "constructor": "NULL",
            "falsifier": "NULL",
            "independent_verdict": "NULL_STALLED_STOP_INDEPENDENTLY_CONFIRMED",
            "positive_token_eligible": False,
            "negative_token_eligible": False,
            "O3": "OPEN",
            "O4": "OPEN",
            "first_missing_edge": "DECLARED_L_SOURCE_INTERFACE_TO_O3_MIXED_GEOMETRIC_RELATIVE_BOUNDARY_SURJECTIVITY",
            "formal_kernel_cone": "EXACT_INTEGRAL_STRICTLY_FUNCTORIAL_ALGEBRAIC_CONTROL_ONLY",
            "formal_kernel_cone_is_geometric_carrier": False,
            "interface_entails_geometric_mixed_proper_realization": False,
            "empty_carrier_is_actual_admissible_9dvl_instance": False,
            "interface_non_entailment_is_full_negative": False,
        },
        "proof_distance": {
            "opening_vector": OPEN_VECTOR,
            "midpoint_vector": OPEN_VECTOR,
            "closing_vector": CLOSE_VECTOR,
            "selected_route_opening": ROUTE,
            "selected_route_closing": ROUTE,
            "strict_decrease": False,
            "minimum_acceptable_decrease_met": False,
            "trajectory": "STALLED",
            "automatic_strategy_reset": "FIRED",
            "strategy_action": "STOP",
            "same_route_continue": False,
            "selected_successor": "NONE",
            "theorem_credit": "NONE",
        },
        "accounting": {
            "ledger_opening": "2/9",
            "ledger_closing": "2/9",
            "ledger_delta": "0/9",
            "canonical_obligations_opening": 7,
            "canonical_obligations_closing": 7,
            "selected_route_delta": 0,
            "pair_residual": "UNKNOWN",
            "pair_coverage": "UNKNOWN",
            "triple_residual": 1_162_302,
            "formal_3_of_10_promoted": False,
        },
        "resources": {
            "opening_to_integrated_verifier_seconds": 1598,
            "ceiling_seconds": 14_400,
            "role_surface_bytes_before_close": 153_277,
            "constructor_handoffs": 1,
            "verifier_directed_repairs": 0,
            "research_saturation_or_cad_jobs": 0,
            "network_or_external_compute": False,
            "github_write_push_or_merge": False,
            "peak_ram": "NOT_CONTINUOUSLY_MEASURED_NO_VALUE_INVENTED",
        },
        "clean_replay": {
            "method": "GIT_CLONE_NO_HARDLINKS_DETACHED_AT_CANDIDATE",
            "candidate_commit": CANDIDATE,
            "candidate_tree": CANDIDATE_TREE,
            "working_tree_clean_after_replay": True,
            "canonical_opening_constructor_falsifier_midpoint_independent_and_candidate_checks": "PASS_7_OF_7",
        },
        "nonconsequences": [
            "NO_O3_OR_O4_PROOF",
            "NO_EXACT_ADMISSIBLE_FULL_NEGATIVE",
            "NO_GENUINELY_MIXED_GEOMETRIC_CELL_CONSTRUCTED_OR_EXCLUDED",
            "NO_GLOBAL_L_SOURCE_OR_PAIR_COMPLEX",
            "NO_PAIR_OR_TRIPLE_BRANCH_CLOSURE",
            "NO_D3_OR_9DVL_PROOF_OR_COUNTEREXAMPLE",
            "NO_LEDGER_CHANGE",
            "NO_HUMAN_REVIEW",
            "NO_AUTOMATIC_SUCCESSOR",
        ],
    }
    return closure, source_manifest


def validate_close(value: dict) -> None:
    require(value["status"] == "PASS", "status")
    require(value["verdict"] == "ACCEPT_EXACT_FROZEN_NULL_STALLED_STOP_NONE", "verdict")
    require(value["candidate"] == {"commit": CANDIDATE, "tree": CANDIDATE_TREE, "parent": VERIFIER_INTEGRATED}, "candidate binding")
    surface = value["changed_surface"]
    require(surface["paths_from_base"] == 23 and surface["current_cycle_or_role_paths"] == 22, "surface count")
    require(surface["outside_current_prefixes"] == [PREDECESSOR_REPORT], "surface exception")
    require(surface["outside_change_disposition"] == "ACCEPT_DISCLOSED_INSERTION_ONLY_COORDINATOR_RECONCILIATION", "surface disposition")
    require(surface["outside_additions"] == 29 and surface["outside_deletions"] == 0, "surface insertion")
    require(surface["immutable_predecessor_report_matches_its_close_manifest"] is True, "predecessor integrity")
    require(surface["canonical_v10_byte_identical_to_base"] is True, "canonical integrity")
    independence = value["lane_independence"]
    require(all(independence[key] is True for key in (
        "constructor_and_falsifier_both_fork_from_opening",
        "falsifier_lane_contains_no_constructor_surface",
        "verifier_forks_after_both_handoffs_and_midpoint",
        "each_lane_changed_only_its_owned_surface",
    )), "lane independence")
    require(independence["producer_agreement_used_as_acceptance"] is False, "producer agreement")
    theorem = value["theorem_gate"]
    require(theorem["constructor"] == theorem["falsifier"] == "NULL", "null lanes")
    require(theorem["independent_verdict"] == "NULL_STALLED_STOP_INDEPENDENTLY_CONFIRMED", "independent verdict")
    require(theorem["positive_token_eligible"] is False and theorem["negative_token_eligible"] is False, "token eligibility")
    require(theorem["O3"] == theorem["O4"] == "OPEN", "open route")
    require(theorem["formal_kernel_cone"] == "EXACT_INTEGRAL_STRICTLY_FUNCTORIAL_ALGEBRAIC_CONTROL_ONLY", "cone")
    require(theorem["formal_kernel_cone_is_geometric_carrier"] is False, "cone geometry")
    require(theorem["interface_entails_geometric_mixed_proper_realization"] is False, "entailment")
    require(theorem["empty_carrier_is_actual_admissible_9dvl_instance"] is False, "empty model")
    require(theorem["interface_non_entailment_is_full_negative"] is False, "negative scope")
    proof = value["proof_distance"]
    require(proof["opening_vector"] == proof["midpoint_vector"] == OPEN_VECTOR, "opening midpoint vector")
    require(proof["closing_vector"] == CLOSE_VECTOR, "closing vector")
    require(proof["selected_route_opening"] == proof["selected_route_closing"] == ROUTE, "route residual")
    require(proof["strict_decrease"] is False and proof["minimum_acceptable_decrease_met"] is False, "no decrease")
    require(proof["trajectory"] == "STALLED" and proof["automatic_strategy_reset"] == "FIRED", "trajectory reset")
    require(proof["strategy_action"] == "STOP", "action")
    require(proof["same_route_continue"] is False and proof["selected_successor"] == "NONE", "successor")
    require(proof["theorem_credit"] == "NONE", "credit")
    accounting = value["accounting"]
    require(accounting["ledger_opening"] == accounting["ledger_closing"] == "2/9", "ledger")
    require(accounting["ledger_delta"] == "0/9", "ledger delta")
    require(accounting["canonical_obligations_opening"] == accounting["canonical_obligations_closing"] == 7, "obligations")
    require(accounting["selected_route_delta"] == 0, "route delta")
    require(accounting["pair_residual"] == accounting["pair_coverage"] == "UNKNOWN", "pair denominator")
    require(accounting["triple_residual"] == 1_162_302, "triple residual")
    require(accounting["formal_3_of_10_promoted"] is False, "false denominator")
    resources = value["resources"]
    require(resources["opening_to_integrated_verifier_seconds"] == 1598, "elapsed")
    require(resources["opening_to_integrated_verifier_seconds"] < resources["ceiling_seconds"] == 14_400, "ceiling")
    require(resources["role_surface_bytes_before_close"] == 153_277, "surface bytes")
    require(resources["constructor_handoffs"] == 1 and resources["verifier_directed_repairs"] == 0, "resource handoffs")
    require(resources["research_saturation_or_cad_jobs"] == 0, "research jobs")
    require(resources["network_or_external_compute"] is False, "external compute")
    require(resources["github_write_push_or_merge"] is False, "GitHub scope")
    replay = value["clean_replay"]
    require(replay["method"] == "GIT_CLONE_NO_HARDLINKS_DETACHED_AT_CANDIDATE", "replay method")
    require(replay["candidate_commit"] == CANDIDATE and replay["candidate_tree"] == CANDIDATE_TREE, "replay binding")
    require(replay["working_tree_clean_after_replay"] is True, "replay clean")
    require(replay["canonical_opening_constructor_falsifier_midpoint_independent_and_candidate_checks"] == "PASS_7_OF_7", "replay checks")
    require(len(value["nonconsequences"]) == 9, "nonconsequences")


def hostile_closes(result: dict) -> list[dict]:
    cases: list[tuple[str, dict]] = []

    def change(identifier: str, path: tuple[str, ...], replacement) -> None:
        candidate = deepcopy(result)
        cursor = candidate
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = replacement
        cases.append((identifier, candidate))

    change("reject_status", ("status",), "FAIL")
    change("promote_verdict", ("verdict",), "ACCEPT_POSITIVE")
    change("move_candidate", ("candidate", "commit"), "0" * 40)
    change("move_tree", ("candidate", "tree"), "0" * 40)
    change("move_parent", ("candidate", "parent"), "0" * 40)
    change("hide_changed_path", ("changed_surface", "paths_from_base"), 22)
    change("hide_exception", ("changed_surface", "outside_current_prefixes"), [])
    change("broaden_exception", ("changed_surface", "outside_current_prefixes"), ["README.md"])
    change("historical_deletion", ("changed_surface", "outside_deletions"), 1)
    change("predecessor_drift", ("changed_surface", "immutable_predecessor_report_matches_its_close_manifest"), False)
    change("canonical_drift", ("changed_surface", "canonical_v10_byte_identical_to_base"), False)
    change("constructor_not_independent", ("lane_independence", "constructor_and_falsifier_both_fork_from_opening"), False)
    change("falsifier_saw_constructor", ("lane_independence", "falsifier_lane_contains_no_constructor_surface"), False)
    change("verifier_started_early", ("lane_independence", "verifier_forks_after_both_handoffs_and_midpoint"), False)
    change("lane_path_escape", ("lane_independence", "each_lane_changed_only_its_owned_surface"), False)
    change("accept_agreement", ("lane_independence", "producer_agreement_used_as_acceptance"), True)
    change("constructor_positive", ("theorem_gate", "constructor"), "POSITIVE")
    change("falsifier_negative", ("theorem_gate", "falsifier"), "NEGATIVE")
    change("verifier_positive", ("theorem_gate", "independent_verdict"), "PROVED")
    change("grant_positive", ("theorem_gate", "positive_token_eligible"), True)
    change("grant_negative", ("theorem_gate", "negative_token_eligible"), True)
    change("close_O3", ("theorem_gate", "O3"), "PROVED")
    change("close_O4", ("theorem_gate", "O4"), "PROVED")
    change("geometrize_cone", ("theorem_gate", "formal_kernel_cone_is_geometric_carrier"), True)
    change("invent_entailment", ("theorem_gate", "interface_entails_geometric_mixed_proper_realization"), True)
    change("promote_empty_model", ("theorem_gate", "empty_carrier_is_actual_admissible_9dvl_instance"), True)
    change("promote_non_entailment", ("theorem_gate", "interface_non_entailment_is_full_negative"), True)
    change("opening_streak_drift", ("proof_distance", "opening_vector"), CLOSE_VECTOR)
    change("midpoint_progress", ("proof_distance", "midpoint_vector"), CLOSE_VECTOR)
    change("closing_streak_drift", ("proof_distance", "closing_vector"), OPEN_VECTOR)
    change("close_route", ("proof_distance", "selected_route_closing"), [])
    change("claim_decrease", ("proof_distance", "strict_decrease"), True)
    change("claim_minimum", ("proof_distance", "minimum_acceptable_decrease_met"), True)
    change("converging", ("proof_distance", "trajectory"), "CONVERGING")
    change("disable_reset", ("proof_distance", "automatic_strategy_reset"), "NOT_FIRED")
    change("continue", ("proof_distance", "strategy_action"), "CONTINUE")
    change("pivot", ("proof_distance", "strategy_action"), "PIVOT")
    change("retire", ("proof_distance", "strategy_action"), "RETIRE")
    change("same_route", ("proof_distance", "same_route_continue"), True)
    change("select_successor", ("proof_distance", "selected_successor"), "O1_O2")
    change("grant_credit", ("proof_distance", "theorem_credit"), "O3_O4")
    change("promote_ledger", ("accounting", "ledger_closing"), "3/9")
    change("close_obligation", ("accounting", "canonical_obligations_closing"), 6)
    change("invent_route_delta", ("accounting", "selected_route_delta"), -2)
    change("invent_pair_denominator", ("accounting", "pair_residual"), 0)
    change("invent_pair_coverage", ("accounting", "pair_coverage"), "3/10")
    change("invent_triple_progress", ("accounting", "triple_residual"), 0)
    change("promote_taxonomy", ("accounting", "formal_3_of_10_promoted"), True)
    change("exceed_ceiling", ("resources", "opening_to_integrated_verifier_seconds"), 14_401)
    change("extra_handoff", ("resources", "constructor_handoffs"), 2)
    change("use_repair", ("resources", "verifier_directed_repairs"), 1)
    change("invent_job", ("resources", "research_saturation_or_cad_jobs"), 1)
    change("use_external_compute", ("resources", "network_or_external_compute"), True)
    change("write_github", ("resources", "github_write_push_or_merge"), True)
    change("shared_clone", ("clean_replay", "method"), "GIT_WORKTREE_SHARED_OBJECTS")
    change("dirty_replay", ("clean_replay", "working_tree_clean_after_replay"), False)
    change("failed_replay", ("clean_replay", "canonical_opening_constructor_falsifier_midpoint_independent_and_candidate_checks"), "PASS_6_OF_7")

    rejected: list[dict] = []
    for identifier, candidate in cases:
        try:
            validate_close(candidate)
        except (AssertionError, KeyError, TypeError):
            rejected.append({"id": identifier, "rejected": True})
            continue
        raise AssertionError(f"hostile close accepted: {identifier}")
    require(len(rejected) == len(cases) and len(rejected) >= 24, "hostile close census")
    return rejected


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    result, manifest = reconstruct()
    validate_close(result)
    hostile_results = hostile_closes(result)
    result["hostile_mutations"] = {
        "rejected": len(hostile_results),
        "total": len(hostile_results),
        "all_rejected": True,
        "results": hostile_results,
    }
    if arguments.write:
        MANIFEST_OUTPUT.write_bytes(
            (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("ascii")
        )
        OUTPUT.write_bytes(
            (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("ascii")
        )
    print(f"PASS frozen candidate {CANDIDATE} / {CANDIDATE_TREE}")
    print(f"PASS {len(manifest['sources'])} candidate sources plus predecessor base pin")
    print("PASS exact lane ancestry, owned surfaces, and kernel-cone logical boundary")
    print(f"PASS {len(hostile_results)}/{len(hostile_results)} hostile closing mutations rejected")
    print("ACCEPT exact frozen NULL / STALLED / STOP / NONE")


if __name__ == "__main__":
    main()
