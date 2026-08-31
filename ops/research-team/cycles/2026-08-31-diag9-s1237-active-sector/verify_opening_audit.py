#!/usr/bin/env python3
"""Fail-closed verifier for the D9 parent-2599 S12,37 opening target."""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
AUDIT = HERE / "OPENING_AUDIT.json"

EXPECTED_SOURCE_SHA256 = {
    "ops/research-team/PROTOCOL.md":
        "7b3fe051677d31748d483de006d9cfc97d26518f5103016371ed7ccee469654c",
    "ai/omreal/NINE_DIAGONAL_STATUS.md":
        "a5865422b3337aba0ccd71eb02c1d521c201f4c338b9a2054afa0d21923e35b0",
    "ai/omreal/DIAG9_ACTIVE_SECTOR_THEOREM.md":
        "132a51b92a9813947e7ab7a43b52aafa6b2c789126e31cfc8a7f0773ee30b790",
    "ai/omreal/verify_diag9_active_sector.py":
        "8317442e095918748397fe302157212333fd908efadfa9c0ab6b5d175599dfd0",
    "ai/omreal/DIAG9_SIGN_GEODESY_AUDIT.md":
        "64896fa28a76f57344bd246f1546322e1361f6ac57f164ca6199c58938c30903",
    "ai/omreal/data/DIAG9_GRAPH_global_factor_census.npz":
        "3984ce87e11fd59d804e59568177248e218cd1c7bb07aae0a9f9f746858728bc",
    "ai/omreal/data/ninth_candidate_12_37_antichain.npz":
        "11ca66549982ec40ce8425d2caed45b418edb73c4eb415a45b39d57e481bd1e4",
    "ai/omreal/data/ninth_candidate_12_37_path.npz":
        "8db38e00d9bf8701558c27cd4ede3e024db8953ea3ef9873bf0b4fc65ad6bcda",
}


class OpeningAuditError(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise OpeningAuditError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, stdout=subprocess.PIPE
    ).stdout.decode("utf-8").strip()


def validate(audit: dict) -> None:
    require(audit["format"] == "diag9-s1237-opening-audit-v1", "format")
    base = audit["base"]
    require(
        base == {
            "commit": "ae2ffe5ff5c9fd087d13191e4e766d8fdb9fb8c8",
            "tree": "46c37dffd007ec08b576a1b3f0e9fc603ad09cbf",
        },
        "base identity",
    )
    require(git("rev-parse", f"{base['commit']}^{{tree}}") == base["tree"], "base tree")
    require(
        audit["opening_ledger"] == {"score": "2/9", "proved_diagonals": [1, 2]},
        "opening ledger",
    )
    target = audit["selected_target"]
    require(target["id"] == "D9_PARENT2599_S12_37_ACTIVE_SECTOR", "target id")
    require(target["parent"] == 2599 and target["family"] == "S_12_37", "target scope")
    require(target["signature_count"] == 9, "signature count")
    require(target["parent_inequality_count"] == 70, "parent inequalities")
    require(
        (
            target["active_occurrence_count"],
            target["candidate_active_factor_count"],
            target["candidate_inactive_factor_count"],
            target["endpoint_factor_difference_count"],
            target["endpoint_difference_active_count"],
        )
        == (5026, 3539, 14285, 5198, 0),
        "active-sector exact counts",
    )
    require(
        target["active_sector_semantic_sha256"]
        == "6de7ff2716b65853c04b9a08f44eb98ad8966e1f3525887ffafde0a3b805c154",
        "active-sector semantic digest",
    )
    require(
        target["opening_verdict"]
        == "PIVOT_TO_D9_PARENT2599_S12_37_ACTIVE_SECTOR",
        "opening verdict",
    )
    require(
        audit["endpoints"]
        == {
            "positive": "COVERAGE_CERTIFIED_CONNECTED_ACTIVE_SECTOR_ONE_INSTANCE_ONLY",
            "negative": "TWO_COVERAGE_CERTIFIED_FEASIBLE_COMPONENTS_D9_COUNTEREXAMPLE",
            "null": "COMPLETE_PROJECTION_OR_COMPACTIFICATION_OBSTRUCTION_NO_TOPOLOGY",
            "timeout": "DETERMINISTIC_PROJECTION_AND_CELL_FRONTIER_NO_CLAIM",
        },
        "endpoints",
    )
    required_nonconsequences = {
        "NO_DIAGONAL_NINE_PROOF_FROM_POSITIVE_INSTANCE",
        "NO_ALL_FAMILY_PARENT2599_RESULT",
        "NO_PARENT860_RESULT",
        "NO_CATALOG_WIDE_9DVL_ADVANCE",
        "NO_SCORE_CHANGE_FROM_POSITIVE_OR_NULL_ENDPOINT",
    }
    require(set(audit["nonconsequences"]) == required_nonconsequences, "nonconsequences")
    required_stops = {
        "D9_PARENT860_COMPLETE_ROADMAP_AS_FIRST_CYCLE",
        "D3_FULL_Q3_ATLAS_THIS_CYCLE",
        "D4_ALTERNATING_TOTAL_COMPLEX_WITHOUT_ALL_GLOBAL_INPUTS",
        "D4_S53_CONTINUATION",
        "ORBIT5563_LOCAL_CONTINUATION",
        "UNIVERSAL_PROJECTIVE_FRAME_COMPACTIFICATION_ASSUMPTION",
    }
    require(set(audit["stopped_routes"]) == required_stops, "stopped routes")
    require(audit["source_sha256"] == EXPECTED_SOURCE_SHA256, "exact source map")
    for relative, expected in EXPECTED_SOURCE_SHA256.items():
        require(sha256(ROOT / relative) == expected, f"source drift: {relative}")


def expect_rejection(name: str, mutation, audit: dict, rejected: list[str]) -> None:
    candidate = copy.deepcopy(audit)
    mutation(candidate)
    try:
        validate(candidate)
    except OpeningAuditError:
        rejected.append(name)
        return
    raise OpeningAuditError(f"hostile mutation accepted: {name}")


def hostile_canaries(audit: dict) -> list[str]:
    rejected: list[str] = []
    expect_rejection("remove_source_pin", lambda a: a.__setitem__("source_sha256", {}), audit, rejected)
    expect_rejection("false_3_of_9", lambda a: a["opening_ledger"].__setitem__("score", "3/9"), audit, rejected)
    expect_rejection("change_parent", lambda a: a["selected_target"].__setitem__("parent", 860), audit, rejected)
    expect_rejection("change_family", lambda a: a["selected_target"].__setitem__("family", "S_37_176"), audit, rejected)
    expect_rejection("drop_active_factor", lambda a: a["selected_target"].__setitem__("candidate_active_factor_count", 3538), audit, rejected)
    expect_rejection("activate_endpoint_difference", lambda a: a["selected_target"].__setitem__("endpoint_difference_active_count", 1), audit, rejected)
    expect_rejection("promote_positive_to_d9", lambda a: a["endpoints"].__setitem__("positive", "PROVE_DIAGONAL_NINE"), audit, rejected)
    expect_rejection("reactivate_parent860", lambda a: a["stopped_routes"].remove("D9_PARENT860_COMPLETE_ROADMAP_AS_FIRST_CYCLE"), audit, rejected)
    expect_rejection("reactivate_d4", lambda a: a["stopped_routes"].remove("D4_ALTERNATING_TOTAL_COMPLEX_WITHOUT_ALL_GLOBAL_INPUTS"), audit, rejected)
    expect_rejection("reactivate_orbit5563", lambda a: a["stopped_routes"].remove("ORBIT5563_LOCAL_CONTINUATION"), audit, rejected)
    require(rejected == audit["hostile_canaries"], "hostile canary order/set")
    return rejected


def main() -> None:
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    validate(audit)
    rejected = hostile_canaries(audit)
    print("PASS exact reviewed base tree")
    print("PASS D9 parent-2599 S12,37 target: 5026 occurrences / 3539 active factors")
    print(f"PASS hostile opening mutations rejected {len(rejected)}/{len(rejected)}")
    print("OUTCOME PIVOT target locked; positive endpoint is one instance only; ledger 2/9")


if __name__ == "__main__":
    main()
