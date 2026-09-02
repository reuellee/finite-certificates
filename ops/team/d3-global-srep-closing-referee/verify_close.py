#!/usr/bin/env python3
"""Independent closing referee for the frozen D3 SREP midpoint candidate."""

from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
CANDIDATE = "d8e61faae0e2318d8eb83fd26dc4140b44a149e1"
BASE = "0b8141223193c1ea2a1b4fce8e862466749f8b6b"
EVIDENCE = "e18efbdea3ef00616f4a6cb83967f6bb267b1a5d"
INDEPENDENT = "597537a8f705ac895e7d3e30962eb515cc8f6015"
CYCLE = "ops/research-team/cycles/2026-09-02-d3-global-semialgebraic-diagram-replacement-gate1"
FILES = {
    "midpoint": (f"{CYCLE}/MIDPOINT.json", 2064,
                 "f59f5ee5ef1131ecc72a0c9b9ff5d22ba4143e67dc8e1573ea9fb3ac3040417f"),
    "cloud": (f"{CYCLE}/CLOUD_PREFLIGHT.json", 2698,
              "688fe0f24a1c82ce6a54bbbb536e8a774186e4642e250a153ae12d01b5342da1"),
    "opening": (f"{CYCLE}/OPENING_STATE.json", 9903,
                "f97af6989befa86f06a0b64017dfb42c66328f5a6db4ae207f5bd8a0498008fe"),
    "cycle_policy": (f"{CYCLE}/CYCLE.md", 18235,
                     "4c692eff5b27ede005140c0bb53899750c22ce7bcb0d90b865026bb8038f39f4"),
    "producer": ("ops/team/d3-global-srep-formula-compiler/RESULT.json", 4534,
                 "39ac5d04d9e043d13360d7bec31beb2144f5fa73aa6e590e86b5efadd2f7c213"),
    "q0_referee": ("ops/team/d3-global-srep-independent-verifier/RESULT.json", 2154,
                   "71d844c72b783896149ed42cdae695a559fccc15ef2d7575b37ae45047d80f54"),
    "canonical_v9": ("ai/omreal/data/CANONICAL_RESEARCH_STATE_V9.json", 9093,
                     "6ec1fa9a23314a064fa8fd71b8a780ab1e6f2ec7543f696735f90c2047f792a5"),
}


class Reject(Exception):
    pass


def require(condition: bool, code: str) -> None:
    if not condition:
        raise Reject(code)


def git_bytes(*args: str) -> bytes:
    try:
        return subprocess.run(
            ["git", *args], cwd=ROOT, check=True, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout
    except subprocess.CalledProcessError as exc:
        raise Reject(f"GIT_READ_FAILED:{' '.join(args)}") from exc


def load_frozen() -> tuple[dict, dict]:
    resolved = git_bytes("rev-parse", f"{CANDIDATE}^{{commit}}").decode().strip()
    require(resolved == CANDIDATE, "CANDIDATE_COMMIT_DRIFT")
    parent = git_bytes("rev-parse", f"{CANDIDATE}^").decode().strip()
    require(parent == INDEPENDENT, "CANDIDATE_PARENT_DRIFT")
    payloads, pins = {}, {}
    for name, (path, expected_bytes, expected_sha) in FILES.items():
        raw = git_bytes("show", f"{CANDIDATE}:{path}")
        actual_sha = hashlib.sha256(raw).hexdigest()
        require(len(raw) == expected_bytes, f"BYTE_COUNT_DRIFT:{name}")
        require(actual_sha == expected_sha, f"SHA256_DRIFT:{name}")
        pins[name] = {"path": path, "bytes": len(raw), "sha256": actual_sha}
        if path.endswith(".json"):
            try:
                payloads[name] = json.loads(raw)
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                raise Reject(f"INVALID_JSON:{name}") from exc
        else:
            payloads[name] = raw.decode("utf-8")
    base_v9 = git_bytes("show", f"{BASE}:{FILES['canonical_v9'][0]}")
    candidate_v9 = git_bytes("show", f"{CANDIDATE}:{FILES['canonical_v9'][0]}")
    require(base_v9 == candidate_v9, "CANONICAL_V9_BYTES_CHANGED")
    changed = git_bytes("diff", "--name-only", BASE, CANDIDATE).decode().splitlines()
    require(not any(path.startswith("ai/omreal/") for path in changed),
            "CANONICAL_THEOREM_SURFACE_CHANGED")
    pins["canonical_v9"]["identical_to_base_revision"] = BASE
    pins["candidate_parent"] = INDEPENDENT
    return payloads, {"files": pins, "changed_paths": changed}


def vector_with_increment(vector: list) -> list:
    require(isinstance(vector, list) and len(vector) == 8, "BAD_PROOF_VECTOR")
    require(vector[:6] == ["2/9", 1, ["diag3_pair_hc1", "diag3_triple_hc0"],
                           7, "UNKNOWN", "UNKNOWN"], "PROOF_VECTOR_SEMANTIC_DRIFT")
    require(vector[6:] == [6, 9], "OPENING_STREAK_DRIFT")
    return vector[:6] + [vector[6] + 1, vector[7] + 1]


def verify_payloads(p: dict) -> dict:
    midpoint, cloud, opening = p["midpoint"], p["cloud"], p["opening"]
    producer, q0_referee, v9 = p["producer"], p["q0_referee"], p["canonical_v9"]

    require(midpoint.get("frozen_q0_evidence_commit") == EVIDENCE, "MIDPOINT_EVIDENCE_PIN_DRIFT")
    require(midpoint.get("independent_verifier_commit") == INDEPENDENT, "MIDPOINT_REFEREE_PIN_DRIFT")
    q0 = midpoint.get("q0", {})
    require(q0.get("producer_classification") == "NULL_NO_EXECUTABLE_REPLACEMENT_BACKEND",
            "MIDPOINT_Q0_CLASSIFICATION_DRIFT")
    require(q0.get("independent_verdict") == "Q0_NULL_INDEPENDENTLY_CONFIRMED",
            "MIDPOINT_Q0_VERDICT_DRIFT")
    require(q0.get("complete_global_tagged_schema") is False, "MIDPOINT_GLOBAL_SCHEMA_FALSE_REQUIRED")
    require(q0.get("executable_replacement_backend") is False, "MIDPOINT_BACKEND_FALSE_REQUIRED")
    require(q0.get("independently_checkable_replacement_trace") is False,
            "MIDPOINT_TRACE_FALSE_REQUIRED")
    for key in ("complete_scope_denominator_N", "exact_formula_parameters_s",
                "exact_formula_parameters_d", "numeric_N_over_N_resource_forecast"):
        require(key in q0 and q0[key] is None, f"MIDPOINT_NULL_REQUIRED:{key}")
    require(q0.get("theorem_credit") == "NONE", "MIDPOINT_THEOREM_CREDIT_MUST_BE_NONE")
    require(midpoint.get("q1_activation") == "DENIED", "MIDPOINT_Q1_MUST_BE_DENIED")
    require(midpoint.get("minimum_decrease_still_reachable_under_fixed_ceiling") is False,
            "MIDPOINT_DECREASE_REACHABILITY_MUST_BE_FALSE")
    require(midpoint.get("mandatory_midpoint_action") == "FREEZE_Q0_AND_STOP",
            "MIDPOINT_STOP_ACTION_DRIFT")
    require(midpoint.get("opening_vector") == midpoint.get("midpoint_vector"),
            "MIDPOINT_THEOREM_VECTOR_CHANGED")

    require(producer.get("q0_pass") is False, "PRODUCER_Q0_FALSE_REQUIRED")
    require(producer.get("q1_eligible") is False, "PRODUCER_Q1_FALSE_REQUIRED")
    require(producer.get("cloud_used") is False, "PRODUCER_CLOUD_FALSE_REQUIRED")
    require(producer.get("theorem_credit") == "NONE", "PRODUCER_THEOREM_CREDIT_MUST_BE_NONE")
    params = producer.get("partial_basu_karisani_parameters", {})
    require(all(params.get(key, "MISSING") is None for key in ("N", "s", "d")),
            "PRODUCER_N_S_D_MUST_BE_NULL")
    require(q0_referee.get("status") == "PASS", "Q0_REFEREE_STATUS_DRIFT")
    require(q0_referee.get("verdict") == "Q0_NULL_INDEPENDENTLY_CONFIRMED",
            "Q0_REFEREE_VERDICT_DRIFT")
    gate = q0_referee.get("producer_gate_assertions", {})
    require(gate == {"q0_pass": False, "q1_eligible": False, "cloud_used": False,
                     "theorem_credit": "NONE", "N": None, "s": None, "d": None},
            "Q0_REFEREE_GATE_ASSERTIONS_DRIFT")

    inventory = cloud.get("inventory_before_and_after_gate", {})
    zero_keys = ("cycle_prefix_instance_count", "cycle_prefix_disk_count",
                 "cycle_instances_created", "cycle_instances_deleted",
                 "existing_resources_modified")
    require(all(inventory.get(key) == 0 for key in zero_keys), "CLOUD_ZERO_ACCOUNTING_DRIFT")
    instances = inventory.get("all_instances")
    require(isinstance(instances, list) and len(instances) == 1, "CLOUD_INVENTORY_CARDINALITY_DRIFT")
    existing = instances[0]
    require(existing.get("name") == "claude-control", "CLOUD_EXISTING_INSTANCE_NAME_DRIFT")
    require(existing.get("scope") == "OUT_OF_SCOPE_UNTOUCHED", "CLOUD_EXISTING_SCOPE_DRIFT")
    prefix = cloud.get("authorized_worker", {}).get("instance_prefix")
    require(prefix == "d3-srep-gate1-20260902-" and not existing["name"].startswith(prefix),
            "CLOUD_PREFIX_SCOPE_DRIFT")
    cloud_gate = cloud.get("q0_gate", {})
    require(cloud_gate.get("q0_pass") is False and cloud_gate.get("q1_eligible") is False,
            "CLOUD_GATE_FALSE_REQUIRED")
    require(cloud_gate.get("hash_pinned_executable_job_manifest_exists") is False,
            "CLOUD_JOB_MANIFEST_MUST_NOT_EXIST")
    require(cloud_gate.get("complete_N_s_d_forecast_exists") is False,
            "CLOUD_FORECAST_MUST_NOT_EXIST")
    require(cloud.get("activation") == "DENIED_Q0_GATE_FAILED", "CLOUD_ACTIVATION_MUST_BE_DENIED")
    require(cloud.get("cloud_used") is False, "CLOUD_USED_MUST_BE_FALSE")
    require(cloud.get("actual_cycle_cloud_spend_usd") == 0, "CLOUD_SPEND_MUST_BE_ZERO")
    resources = midpoint.get("resource_accounting", {})
    require(resources.get("cloud_worker_activated") is False and
            resources.get("cloud_activation") == "DENIED_Q0_GATE_FAILED",
            "MIDPOINT_CLOUD_GATE_DRIFT")

    state = opening.get("canonical_state", {})
    require(opening.get("base_revision") == BASE, "OPENING_BASE_DRIFT")
    require(state.get("edited_by_cycle") is False, "OPENING_CANONICAL_EDIT_DRIFT")
    require(opening.get("authority", {}).get("human_review_available") is False,
            "HUMAN_REVIEW_FALSE_REQUIRED")
    require(v9.get("status") == "STOPPED", "CANONICAL_STATUS_DRIFT")
    theorem = v9.get("theorem", {})
    obligations = v9.get("open_obligations", {})
    require(theorem.get("score") == "2/9" and theorem.get("promotion") == "NONE",
            "CANONICAL_THEOREM_DRIFT")
    require(obligations.get("load_bearing_count") == 7, "CANONICAL_OBLIGATION_COUNT_DRIFT")
    require(all(item.get("delta") == "UNCHANGED" for item in obligations.get("items", [])) and
            len(obligations.get("items", [])) == 7, "CANONICAL_OBLIGATION_DELTA_DRIFT")
    require(obligations.get("pair_residual") == "UNKNOWN" and
            obligations.get("pair_coverage") == "UNKNOWN", "CANONICAL_COVERAGE_DRIFT")

    policy = " ".join(p["cycle_policy"].split())
    for phrase in ("close `STALLED / STOP`", "Q0 failure", "forces `STOP`", "cannot justify same-route continuation"):
        require(phrase in policy, f"CLOSING_POLICY_TEXT_MISSING:{phrase}")
    closing_vector = vector_with_increment(midpoint.get("midpoint_vector"))
    require(closing_vector[6:] == [7, 10], "CLOSING_STREAK_INCREMENT_DRIFT")
    return {
        "q0": "NULL_INDEPENDENTLY_CONFIRMED",
        "q1": "DENIED",
        "cloud": {"used": False, "spend_usd": 0, "prefix_instances": 0,
                  "prefix_disks": 0, "existing_claude_control": "OUT_OF_SCOPE_UNTOUCHED"},
        "canonical_v9": "BYTE_IDENTICAL_TO_BASE",
        "theorem_delta": 0,
        "obligation_delta": 0,
        "opening_vector": midpoint["opening_vector"],
        "closing_vector": closing_vector,
        "trajectory": "STALLED",
        "strategy_action": "STOP",
        "same_route_continue": False,
        "theorem_credit": "NONE",
    }


def mutations(payloads: dict) -> list[dict]:
    outcomes = []

    def test(identifier, change):
        candidate = copy.deepcopy(payloads)
        change(candidate)
        try:
            verify_payloads(candidate)
        except Reject as exc:
            outcomes.append({"id": identifier, "rejected": True, "reason": str(exc)})
        else:
            outcomes.append({"id": identifier, "rejected": False, "reason": "ACCEPTED"})

    test("midpoint_backend_promoted", lambda p: p["midpoint"]["q0"].__setitem__("executable_replacement_backend", True))
    test("midpoint_schema_promoted", lambda p: p["midpoint"]["q0"].__setitem__("complete_global_tagged_schema", True))
    test("midpoint_N_fabricated", lambda p: p["midpoint"]["q0"].__setitem__("complete_scope_denominator_N", 1))
    test("midpoint_s_fabricated", lambda p: p["midpoint"]["q0"].__setitem__("exact_formula_parameters_s", 1))
    test("midpoint_q1_activated", lambda p: p["midpoint"].__setitem__("q1_activation", "ACTIVE"))
    test("midpoint_decrease_claimed", lambda p: p["midpoint"].__setitem__("minimum_decrease_still_reachable_under_fixed_ceiling", True))
    test("midpoint_continue_claimed", lambda p: p["midpoint"].__setitem__("mandatory_midpoint_action", "CONTINUE"))
    test("midpoint_vector_changed", lambda p: p["midpoint"]["midpoint_vector"].__setitem__(3, 6))
    test("producer_q0_promoted", lambda p: p["producer"].__setitem__("q0_pass", True))
    test("producer_theorem_credit", lambda p: p["producer"].__setitem__("theorem_credit", "CLAIMED"))
    test("q0_referee_verdict_changed", lambda p: p["q0_referee"].__setitem__("verdict", "Q0_PASS"))
    test("cloud_prefix_instance_created", lambda p: p["cloud"]["inventory_before_and_after_gate"].__setitem__("cycle_prefix_instance_count", 1))
    test("cloud_prefix_disk_created", lambda p: p["cloud"]["inventory_before_and_after_gate"].__setitem__("cycle_prefix_disk_count", 1))
    test("cloud_existing_modified", lambda p: p["cloud"]["inventory_before_and_after_gate"].__setitem__("existing_resources_modified", 1))
    test("cloud_existing_scope_changed", lambda p: p["cloud"]["inventory_before_and_after_gate"]["all_instances"][0].__setitem__("scope", "IN_SCOPE"))
    test("cloud_used_claimed", lambda p: p["cloud"].__setitem__("cloud_used", True))
    test("cloud_spend_claimed", lambda p: p["cloud"].__setitem__("actual_cycle_cloud_spend_usd", 0.01))
    test("cloud_q0_promoted", lambda p: p["cloud"]["q0_gate"].__setitem__("q0_pass", True))
    test("cloud_manifest_claimed", lambda p: p["cloud"]["q0_gate"].__setitem__("hash_pinned_executable_job_manifest_exists", True))
    test("canonical_score_promoted", lambda p: p["canonical_v9"]["theorem"].__setitem__("score", "3/9"))
    test("canonical_obligation_closed", lambda p: p["canonical_v9"]["open_obligations"]["items"][0].__setitem__("delta", "CLOSED"))
    test("human_review_fabricated", lambda p: p["opening"]["authority"].__setitem__("human_review_available", True))
    require(len(outcomes) >= 16 and all(item["rejected"] for item in outcomes),
            "HOSTILE_MUTATION_ESCAPED")
    return outcomes


def main() -> int:
    try:
        payloads, pins = load_frozen()
        closing = verify_payloads(payloads)
        hostile = mutations(payloads)
        result = {
            "format": "d3-global-srep-independent-closing-referee-v1",
            "status": "PASS",
            "verdict": "ACCEPT_FROZEN_MIDPOINT_CLOSE_STALLED_STOP",
            "candidate_commit": CANDIDATE,
            "candidate_parent": INDEPENDENT,
            "frozen_q0_evidence_commit": EVIDENCE,
            "pins": pins["files"],
            "protected_surface_check": {
                "base_revision": BASE,
                "canonical_v9_byte_identical": True,
                "changed_ai_omreal_paths": 0,
            },
            "independent_closing_reconstruction": closing,
            "hostile_mutations": {"rejected": len(hostile), "total": len(hostile),
                                  "all_rejected": True, "results": hostile},
            "scope": [
                "Independent machine closing review; no human review was available or claimed.",
                "Accepts only the STALLED/STOP close with zero theorem and obligation delta.",
                "Does not edit canonical state, activate Q1, use cloud, or grant theorem credit.",
            ],
        }
    except Reject as exc:
        result = {"format": "d3-global-srep-independent-closing-referee-v1",
                  "status": "FAIL", "verdict": "REJECT_CANDIDATE", "reason": str(exc),
                  "candidate_commit": CANDIDATE}
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1
    if "--json" in sys.argv:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS frozen Git candidate pins: 7/7")
        print("PASS Q0 null independently confirmed; Q1 denied")
        print("PASS cloud prefix instances/disks 0/0; claude-control out-of-scope untouched")
        print("PASS canonical V9 byte-identical; theorem delta 0; obligation delta 0")
        print("PASS closing vector streaks 6/9 -> 7/10")
        print(f"PASS hostile mutations rejected: {len(hostile)}/{len(hostile)}")
        print("VERDICT ACCEPT_FROZEN_MIDPOINT_CLOSE_STALLED_STOP; THEOREM_CREDIT=NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
