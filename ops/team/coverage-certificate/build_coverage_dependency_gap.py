#!/usr/bin/env python3
"""Deterministically build the row-2599 coverage dependency-gap record.

This is a generator/auditor, not an acceptance verifier.  It extracts only
facts already sealed in pinned exact artifacts and emits a compact null-result
certificate.  It deliberately does not infer global component coverage from
factor crossings, collars, samples, or a finite source skeleton.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[3]
BASE_REVISION = "ec362dba8a912bc4749c004641aee2da0a88dc05"
FORMAT = "diag3-row2599-component-coverage-dependency-gap-v1"
SEMANTIC_PREFIX = b"diag3-row2599-component-coverage-dependency-gap-v1\0"

INPUTS = {
    "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json":
        "7922d769aa30a84c5d208dec92d2e78d5c7744cc6184ea1d42aaeadf947761b3",
    "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json":
        "19248dd148d1fd002931ed5f48197869dd42c68a513376e1a4d6941389bda307",
    "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON_EDGE27_EDGE39.json":
        "dcb707220df3e61b1a94eeedcf8e46b6602f30d405f4a92fc542c0f52f672806",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json":
        "fb73899be7ff4aed5739b7f6a999d623db2a0504f212d5fe5aba35e1df1b1465",
    "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_COMPONENT_COLLAR.json":
        "5930cc19019470fdfdf55d67523f6c4211ccf5b540f5c2bb5df36c64db75d7bd",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin":
        "adb2e7257457f158e809450683c46fe7ecafdbdd4a7efdf9ac630e8a4f0fb03f",
    "ops/team/edge39-prover/EDGE39_EXACT_ROADMAP.json":
        "cd4cc32efc2d71a609a01b2747e5d6230b7115a7ee23423b6a3175a71a1cf6c1",
}


def canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def pinned_bytes(relative: str) -> bytes:
    return subprocess.check_output(
        ["git", "show", f"{BASE_REVISION}:{relative}"],
        cwd=ROOT,
    )


def pinned_sha256(relative: str) -> str:
    return hashlib.sha256(pinned_bytes(relative)).hexdigest()


def load_json(relative: str) -> dict:
    return json.loads(pinned_bytes(relative))


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def build() -> dict:
    for relative, expected in INPUTS.items():
        require(pinned_sha256(relative) == expected, f"input digest: {relative}")

    ledger = load_json("ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json")
    cover = load_json("ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json")
    skeleton = load_json(
        "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON_EDGE27_EDGE39.json"
    )
    closure = load_json("ai/omreal/data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json")
    collar = load_json("ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_COMPONENT_COLLAR.json")
    edge39 = load_json("ops/team/edge39-prover/EDGE39_EXACT_ROADMAP.json")

    row = ledger["row2599_fullsupport_ledger"]
    factor_count = row["fullsupport_factor_count"]
    nonempty = row["exact_interior_nonempty_count"]
    empty = row["exact_empty_count"]
    unresolved = row["unresolved_feasibility_count"]
    require((factor_count, nonempty, empty, unresolved) == (17_824, 10_844, 1_177, 5_803),
            "row2599 factor partition")
    require(nonempty + empty + unresolved == factor_count, "factor accounting")

    selected = cover["source_bank"]["selected_edge_indices"]
    require(len(selected) == 40 and len(set(selected)) == 40, "selected source cover")
    compiled = skeleton["scope"]["fully_compiled_cover_edges"]
    pending = skeleton["scope"]["pending_cover_edges"]
    require(sorted(compiled + pending) == selected, "compiled/pending cover partition")
    require((compiled, len(pending)) == ([27, 39], 38), "current skeleton scope")

    local_component = collar["component_coverage"]
    require(local_component["factor_id"] == 19069, "pilot factor")
    require(local_component["declared_scope_component_count"] == 1, "pilot component")
    require(local_component["meets_retained_source_skeleton"] is True, "pilot source hit")
    require(local_component["meets_artificial_scope_boundary"] == ["w_minus", "w_plus"],
            "pilot artificial frontier")
    require(collar["scope"]["components_outside_declared_collar"] == "UNTESTED",
            "pilot global limit")

    observations = closure["observations"]
    require(observations["certified_global_strict_closure_pairs"] == 0, "closure pairs")
    require(observations["certified_global_strict_closure_triples"] == 0, "closure triples")
    require(observations["certified_parent_infinity_cells"] == 0, "infinity cells")

    degree_census = edge39["factor_census"]["degree_census"]
    require(sum(int(count) for count in degree_census.values()) == factor_count,
            "degree census")
    bezout = sum(
        int(count) * int(degree) * (int(degree) - 1) ** 8
        for degree, count in degree_census.items()
        if int(degree) >= 2
    )

    record = {
        "format": FORMAT,
        "status": "INCOMPLETE_DEPENDENCY_GAP",
        "base_revision": "ec362dba8a912bc4749c004641aee2da0a88dc05",
        "scope": {
            "parent_index": 2599,
            "support": [15, 15, 15],
            "ambient_parameter_dimension": 9,
            "global_parent_cell_coverage": "NOT_CERTIFIED",
            "wall_component_coverage": "NOT_CERTIFIED",
            "relative_escape_coverage": "NOT_CERTIFIED",
            "honest_9dvl_score": "2/9_UNCHANGED",
        },
        "inputs": INPUTS,
        "exact_accounting": {
            "candidate_factor_count": factor_count,
            "known_strict_interior_nonempty_factor_count": nonempty,
            "known_strict_interior_empty_factor_count": empty,
            "unresolved_feasibility_factor_count": unresolved,
            "maximum_current_active_wall_count": row["master_generator_active_wall_upper_bound"],
            "empty_factor_ids_sha256": row["digests"]["empty_factor_ids"],
            "unresolved_factor_ids_sha256": row["digests"]["unresolved_factor_ids"],
            "selected_source_edge_count": len(selected),
            "compiled_source_edge_indices": compiled,
            "pending_source_edge_count": len(pending),
            "crossed_factor_classes_covered_by_selected_edges": 10_844,
        },
        "first_decisive_gap": {
            "id": "unclassified_factor_feasibility",
            "missing_count": unresolved,
            "statement": (
                "The retained source bank has no crossing for these factors, and current exact "
                "artifacts prove neither strict-parent emptiness nor nonemptiness. A nonempty one "
                "would already be a wall missed by the 40-edge skeleton."
            ),
            "consequence": "Compiling the remaining 38 edges cannot close global coverage by itself.",
        },
        "required_global_blocks": [
            {
                "id": "factor_disposition",
                "obligation": (
                    "Every one of the 17824 pinned factors is exactly EMPTY_STRICT_PARENT or has a "
                    "complete nonempty component quotient."
                ),
                "missing": "5803 factors have no exact disposition.",
            },
            {
                "id": "component_quotient",
                "obligation": (
                    "For every nonempty factor, an exact projection-critical roadmap or equivalent "
                    "collar atlas enumerates all connected components and all continuation incidences."
                ),
                "missing": "No global component count or component incidence exists for any factor.",
            },
            {
                "id": "skeleton_hit_map",
                "obligation": (
                    "Every enumerated wall component has at least one exact intersection cell on one "
                    "of the 40 retained source edges."
                ),
                "missing": "The cover records factor-class witnesses, not component-to-hit surjectivity.",
            },
            {
                "id": "frontier_balance",
                "obligation": (
                    "Every roadmap/collar frontier germ is paired by internal continuation or a chart "
                    "seam, or is exactly tagged as a genuine relative parent face/infinity escape."
                ),
                "missing": (
                    "The only exact collar terminates at two artificial scope-frontier cells; no global "
                    "relative escape inventory exists."
                ),
            },
            {
                "id": "ambient_exclusion",
                "obligation": (
                    "The complement of the certified wall collars/roadmap is covered by exact "
                    "factor-nonzero regions, excluding disconnected unseeded components."
                ),
                "missing": "No coverage-certified parent-domain complement or equivalent no-missed-component proof.",
            },
        ],
        "boundary_tag_contract": {
            "allowed_in_global_complete": [
                "INTERNAL_CONTINUATION",
                "CHART_SEAM",
                "GENUINE_RELATIVE_PARENT_FACE",
                "GENUINE_RELATIVE_PARENT_INFINITY",
            ],
            "forbidden_in_global_complete": ["ARTIFICIAL_SCOPE_FRONTIER", "UNCLASSIFIED_FRONTIER"],
            "rules": {
                "INTERNAL_CONTINUATION": "must have a unique reverse incidence and matching factor germ",
                "CHART_SEAM": "must pin an invertible transition and matched algebraic germ",
                "GENUINE_RELATIVE_PARENT_FACE": "must pin vanishing parent brackets and all remaining target signs",
                "GENUINE_RELATIVE_PARENT_INFINITY": "must pin a compactification face, chart cocycle, and relative-face ID",
                "ARTIFICIAL_SCOPE_FRONTIER": "is a dependency gap, never a relative escape",
                "UNCLASSIFIED_FRONTIER": "is a dependency gap",
            },
        },
        "local_pilot": {
            "status": "EXACT_LOCAL_SCHEMA_PILOT_ONLY",
            "factor_id": 19069,
            "declared_scope": "two-dimensional rational collar on source edge 39",
            "declared_scope_component_count": 1,
            "source_skeleton_hits": ["w_zero"],
            "frontier": [
                {"cell_id": "w_minus", "tag": "ARTIFICIAL_SCOPE_FRONTIER"},
                {"cell_id": "w_plus", "tag": "ARTIFICIAL_SCOPE_FRONTIER"},
            ],
            "genuine_relative_escapes": [],
            "components_outside_declared_scope": "UNTESTED",
            "global_acceptance": False,
        },
        "row2599_resource_estimate": {
            "candidate_degree_census": degree_census,
            "generic_dense_projection_critical_bezout_sum": bezout,
            "interpretation": (
                "Pessimistic dense bound before boundary strata; it rules out an unstructured global "
                "projection-critical solve under the 45-minute/12-GiB track ceiling, not a sparse or "
                "family-batched roadmap."
            ),
            "recommended_architecture": (
                "streamed factor-family shards: exact feasibility first, then seeded adaptive Bernstein "
                "collars plus exact complement exclusion and a compact component quotient"
            ),
        },
        "canary_contract": {
            "positive": "accept the pinned factor-19069 local pilot only with local scope",
            "negative": "reject a GLOBAL_COMPLETE claim while any required block is missing",
            "null": "accept this dependency-gap record without theorem promotion",
            "hostile": (
                "after recomputing the semantic seal, reject artificial-as-relative, missing input pin, "
                "invented component count, false 40/40 compilation, altered factor accounting, or 3/9 promotion"
            ),
        },
        "theorem_effect": (
            "Exact architectural null result: current inputs do not certify that the 40-edge skeleton "
            "meets every strict-parent residual-wall component or records every genuine relative escape. "
            "The pair obligation and honest 9DVL score remain unchanged."
        ),
    }
    record["semantic_sha256"] = hashlib.sha256(SEMANTIC_PREFIX + canonical(record)).hexdigest()
    return record


def main() -> None:
    print(json.dumps(build(), indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
