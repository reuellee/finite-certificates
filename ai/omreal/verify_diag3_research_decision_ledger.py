#!/usr/bin/env python3
"""Fail-closed audit of the canonical diagonal-three research decision ledger."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
LEDGER_PATH = DATA / "DIAG3_RESEARCH_DECISION_LEDGER.json"
COMPLETION_PATH = DATA / "DIAG3_COMPLETION_OPEN_OBJECT.json"
CLOSURE_PATH = DATA / "DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json"
POINTER = "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json"


def load(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def score(row: dict) -> int:
    return (
        4 * row["proof_criticality"]
        + 3 * row["branch_elimination"]
        + 2 * row["readiness"]
        + 2 * row["decisiveness"]
        - 2 * row["cost"]
        - 2 * row["failure_risk"]
    )


def assert_evidence_exists(record: object) -> None:
    if isinstance(record, dict):
        for key, value in record.items():
            if key in {"evidence", "regression"}:
                paths = value if isinstance(value, list) else [value]
                for path in paths:
                    target = HERE.parent.parent / path
                    if not target.is_file():
                        raise AssertionError(f"missing evidence path: {path}")
            else:
                assert_evidence_exists(value)
    elif isinstance(record, list):
        for value in record:
            assert_evidence_exists(value)


def main() -> None:
    ledger = load(LEDGER_PATH)
    completion = load(COMPLETION_PATH)
    closure = load(CLOSURE_PATH)

    assert ledger["format"] == "diag3-research-decision-ledger-v1"
    assert ledger["status"] == "ACTIVE"
    assert ledger["as_of"] == "2026-08-21"
    assert ledger["repository"] == {
        "full_name": "reuellee/finite-certificates",
        "default_branch": "main",
        "audited_commit": "e4ca567f829bd0e887e98efb05a3ed9437ba69d5",
        "merged_pull_request": 19,
    }
    assert ledger["theorem"]["score"] == completion["ledger_score"] == "2/9"
    assert ledger["theorem"]["proved_diagonals"] == [1, 2]
    assert ledger["theorem"]["active_diagonal"] == 3

    obligations = ledger["invariant_obligations"]
    assert [row["id"] for row in obligations] == [
        "diag3_triple_hc0",
        "diag3_pair_hc1",
    ]
    assert all(row["status"] == "OPEN" for row in obligations)
    triple = obligations[0]
    source = completion["triple_obligation"]
    assert (
        triple["universe_count"],
        triple["proved_noncompact_count"],
        triple["unresolved_count"],
    ) == (
        source["universe_count"],
        source["proved_noncompact_count"],
        source["unresolved_count"],
    ) == (79_102_449, 77_940_147, 1_162_302)
    assert triple["universe_count"] - triple["proved_noncompact_count"] == triple[
        "unresolved_count"
    ]

    pair = obligations[1]
    observations = closure["observations"]
    assert (
        pair["current_global_adjacencies"],
        pair["current_global_strict_closure_pairs"],
        pair["current_global_strict_closure_triples"],
        pair["current_parent_infinity_cells"],
    ) == (
        observations["certified_adjacency_edges_between_distinct_atlas_charts"],
        observations["certified_global_strict_closure_pairs"],
        observations["certified_global_strict_closure_triples"],
        observations["certified_parent_infinity_cells"],
    ) == (0, 0, 0, 0)

    full = ledger["row2599_fullsupport_ledger"]
    assert full["support_count"] == 3_375
    assert full["proper_relative_support_count"] == 3_374
    assert full["possible_nonrelative_supports"] == [[15, 15, 15]]
    assert (
        full["relative_boundary_mixed_restriction_count"]
        + full["fullsupport_factor_count"]
        == full["parent_face_mixed_restriction_count"]
        == closure["global_generator_preflight"][
            "remaining_mixed_residual_restriction_count"
        ]
        == 70_218
    )
    assert (
        full["exact_interior_nonempty_count"]
        + full["exact_empty_count"]
        + full["unresolved_feasibility_count"]
        == full["fullsupport_factor_count"]
        == 17_824
    )
    assert (
        full["exact_interior_nonempty_count"] + full["unresolved_feasibility_count"]
        == full["master_generator_active_wall_upper_bound"]
        == 16_647
    )
    assert full["digests"]["empty_factor_ids"] == (
        "f9022c922d56c69ea541d6098cea89004bdfcff73b01a411a159a78b5c369484"
    )
    assert full["digests"]["unresolved_factor_ids"] == (
        "0c85f0e7370963df311a5a7d04e175e4a801b79c54fe0600a69bb777bf30a76a"
    )
    assert full["digests"]["relative_boundary_collapse"] == (
        "65b425e0a9507dd536b59e770f3c43f5eb025381b2ca2e75eb009e93d022b02a"
    )

    retired = {row["id"]: row for row in ledger["retired_or_subordinated_targets"]}
    assert retired["proper_support_dimension4_subdivision"]["status"] == "RETIRED"
    assert retired["moving_column_s3_quotient"]["withdrawn_counts"] == {
        "transported_witnesses": 5_986,
        "residue_factors": 994,
        "quotient_classes": 264,
        "failed_nonidentity_segment_transports": 525,
    }
    assert retired["standalone_degree_one_positive_multiplier_screen"][
        "status"
    ] == "SUBORDINATED"
    assert closure["global_generator_preflight"]["status"] == (
        "PARENT_FACE_GATE_READY_DIMENSION4_SUBDIVISION_MISSING"
    )

    candidates = ledger["candidate_targets"]
    assert len({row["id"] for row in candidates}) == len(candidates)
    for row in candidates:
        assert all(0 <= row[key] <= 5 for key in (
            "proof_criticality",
            "branch_elimination",
            "readiness",
            "decisiveness",
            "cost",
            "failure_risk",
        ))
        assert row["priority_score"] == score(row)
    selected = [row for row in candidates if row["selected"]]
    assert len(selected) == 1
    assert selected[0]["id"] == ledger["selected_target"]
    assert selected[0]["priority_score"] == max(
        row["priority_score"] for row in candidates
    )
    assert ledger["selected_target"] == "fullsupport_master_closure_compiler"

    digest = git_blob_sha1(LEDGER_PATH)
    for historical in (completion, closure):
        assert historical["current_decision_ledger"] == POINTER
        assert historical["current_decision_ledger_git_blob"] == digest

    assert ledger["process_gates"] == {
        "canonical_state_first": True,
        "independent_verifier_required": True,
        "negative_canary_required": True,
        "exact_scope_labels_required": True,
        "default_branch_and_drive_checkpoint_required_at_cycle_end": True,
        "theorem_score_promotion_requires_all_invariant_obligations_closed": True,
    }
    assert_evidence_exists(ledger)
    print("PASS canonical diagonal-three research decision ledger")
    print("PASS invariant obligations remain open; honest ledger 2/9")
    print(
        "PASS row2599 full support:",
        "10844 interior + 1177 empty + 5803 unresolved = 17824",
    )
    print(
        "SELECTED fullsupport_master_closure_compiler score",
        selected[0]["priority_score"],
    )
    print("LEDGER_GIT_BLOB", digest)


if __name__ == "__main__":
    main()
