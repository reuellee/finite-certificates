#!/usr/bin/env python3
"""Fail-closed audit of the diagonal-nine research decision ledger."""

from __future__ import annotations

import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LEDGER = HERE / "data" / "DIAG9_RESEARCH_DECISION_LEDGER.json"


def priority(row):
    return (
        4 * row["proof_criticality"]
        + 3 * row["branch_elimination"]
        + 2 * row["readiness"]
        + 2 * row["decisiveness"]
        - 2 * row["cost"]
        - 2 * row["failure_risk"]
    )


def check_evidence(value):
    if isinstance(value, dict):
        for key, child in value.items():
            if key == "evidence":
                for relative in child if isinstance(child, list) else [child]:
                    if not (HERE.parent.parent / relative).is_file():
                        raise AssertionError(f"missing evidence: {relative}")
            else:
                check_evidence(child)
    elif isinstance(value, list):
        for child in value:
            check_evidence(child)


def main():
    with LEDGER.open("r", encoding="utf-8") as handle:
        ledger = json.load(handle)

    assert ledger["format"] == "diag9-research-decision-ledger-v1"
    assert ledger["status"] == "ACTIVE"
    assert ledger["as_of"] == "2026-08-23"
    assert ledger["theorem"]["score"] == "2/9"
    assert ledger["theorem"]["proved_diagonals"] == [1, 2]
    assert ledger["theorem"]["active_diagonal"] == 9

    obligation = ledger["global_obligation"]
    assert obligation["status"] == "OPEN"
    assert obligation["realizable_parent_classes"] == 2_604
    assert obligation["parents_with_complete_compactified_labeled_roadmap"] == 0
    assert all(
        obligation[key]
        for key in (
            "coverage_required",
            "infinity_required",
            "all_family_connectivity_required",
        )
    )

    parent = ledger["parent860_input"]
    assert parent["certified_empty_factors"] + parent["candidate_factors"] == (
        parent["primitive_global_factors"]
    ) == 26_740

    node = ledger["exact_local_checkpoint"]
    assert node["status"] == "PROVED"
    assert node["active_factors"] == [15_250, 19_721]
    assert node["other_factors_excluded"] + len(node["active_factors"]) == 26_740
    assert node["parent_brackets_excluded"] == 70
    assert (node["chambers"], node["wall_rays"], node["nodes"]) == (4, 4, 1)
    assert node["chamber_tope_count"] == 26_112
    assert node["wall_tope_counts"] == [26_110, 26_110, 26_040, 26_040]
    assert node["node_tope_count"] == 26_038
    assert node["proper_support_patterns"] == [3, 6, 9, 12]
    assert sum(node["support_pattern_multiplicity"].values()) == 26_186
    assert node["intersection_closure"] == [0, 1, 2, 3, 4, 6, 8, 9, 12, 15]
    assert node["semantic_sha256"] == (
        "b7080a332d7b80127ae362bbfa2d5806fbe153d24245ef002d4867df6e1e274d"
    )
    assert node["hostile_corruptions_rejected"] == 4

    frontier = ledger["exact_plane_projection_frontier"]
    assert frontier["status"] == "PROVED"
    assert frontier["primitive_global_factors"] == 26_740
    assert (
        frontier["constant_restrictions"]
        + frontier["constant_sign_nonconstant_exclusions"]
        + frontier["boundary_only_factors"]
        + frontier["open_triangle_factors"]
        == 26_740
    )
    assert (
        frontier["constant_sign_nonconstant_exclusions"]
        + frontier["boundary_only_factors"]
        + frontier["open_triangle_factors"]
        == frontier["distinct_irreducible_plane_restrictions"]
    )
    assert frontier["closed_triangle_factors"] == (
        frontier["boundary_only_factors"] + frontier["open_triangle_factors"]
    )
    assert frontier["all_open_curve_pairs"] == (
        frontier["open_triangle_factors"]
        * (frontier["open_triangle_factors"] - 1)
        // 2
    )
    assert frontier["exactly_excluded_curve_pairs"] + frontier["candidate_curve_pairs"] == (
        frontier["all_open_curve_pairs"]
    )
    assert frontier["semantic_sha256"] == (
        "cbcee4e0e7a7e757b9751f06349337d14206e102e4afaffd5abdd3833718a0fd"
    )

    candidates = ledger["candidate_targets"]
    assert len({row["id"] for row in candidates}) == len(candidates)
    for row in candidates:
        for key in (
            "proof_criticality",
            "branch_elimination",
            "readiness",
            "decisiveness",
            "cost",
            "failure_risk",
        ):
            assert 0 <= row[key] <= 5
        assert row["priority_score"] == priority(row)
    selected = [row for row in candidates if row["selected"]]
    assert len(selected) == 1
    assert selected[0]["id"] == ledger["selected_target"]
    assert selected[0]["priority_score"] == max(row["priority_score"] for row in candidates)
    assert selected[0]["resource_ceiling"]
    assert selected[0]["stop_rule"]

    assert ledger["promotion_gates"] == [
        "complete signed parent-cell coverage",
        "complete residual wall and lower-stratum incidence",
        "exact complete chamber labels",
        "genuine parent infinity",
        "all admissible nine-family connectivity",
        "all 2604 realizable parent classes",
        "independent replay and hostile canaries",
    ]
    check_evidence(ledger)
    print("PASS diagonal-nine score and global obligation remain fail-closed")
    print("PASS parent-860 local checkpoint accounting and evidence")
    print("PASS parent-860 exact plane projection frontier accounting and evidence")
    print("PASS selected target has the unique maximum priority and a stop rule")
    print("SCOPE score remains 2/9; no parent-space coverage is claimed")


if __name__ == "__main__":
    main()
