#!/usr/bin/env python3
"""Build the exact fail-closed factor-19069 active-margin frontier."""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OMREAL = ROOT / "ai" / "omreal"
DATA = OMREAL / "data"
OUTPUT = HERE / "ACTIVE_MARGIN_FRONTIER.json"
sys.path.insert(0, str(OMREAL))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402
import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: E402
import verify_diag3_pair_global_face_bernstein_atlas as bernstein  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


OPENING_REVISION = "65744ea631c98dce21b58fd39626f9e129190003"
OPENING_TREE = "0f0cf83c316650a09ae2f08136f16cf9ed8880af"
OPENING_AUDIT = (
    "ops/research-team/cycles/"
    "2026-09-01-d9-row2599-factor19069-active-margin-gate1/OPENING_AUDIT.json"
)
TARGET_FACTOR = 19069
SYSTEM_CEILING = 100_000


def digest_path(path: Path) -> str:
    state = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            state.update(block)
    return state.hexdigest()


def git(*arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=ROOT, text=True).strip()


def polynomial_degree(polynomial) -> int:
    return max(map(sum, polynomial))


def primitive_univariate(coefficients):
    coefficients = list(map(Fraction, coefficients))
    while len(coefficients) > 1 and coefficients[-1] == 0:
        coefficients.pop()
    return tuple(coefficients)


def root_count_open(polynomial) -> int:
    polynomial = primitive_univariate(polynomial)
    if sturm.polynomial_value(polynomial, Fraction(0)) == 0:
        raise AssertionError("skeleton edge starts on factor 19069")
    if sturm.polynomial_value(polynomial, Fraction(1)) == 0:
        raise AssertionError("skeleton edge ends on factor 19069")
    return sturm.root_count(polynomial, Fraction(0), Fraction(1))


def restriction_state(polynomial, multidegree, face) -> str:
    signs = {
        1 if coefficient > 0 else -1
        for monomial, coefficient in polynomial.items()
        if all(
            support & ~allowed == 0
            for support, allowed in zip(
                bernstein.term_support(monomial, multidegree), face, strict=True
            )
        )
    }
    if not signs:
        return "IDENTICALLY_ZERO"
    if signs == {1}:
        return "BERNSTEIN_POSITIVE"
    if signs == {-1}:
        return "BERNSTEIN_NEGATIVE"
    if signs == {-1, 1}:
        return "BERNSTEIN_MIXED_UNRESOLVED"
    raise AssertionError("invalid face restriction state")


def canonical_digest(payload: dict) -> str:
    return sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def build() -> dict:
    if git("rev-parse", f"{OPENING_REVISION}^{{tree}}") != OPENING_TREE:
        raise AssertionError("opening revision/tree drift")
    if digest_path(ROOT / OPENING_AUDIT) != "d925c2c0747e09ba8cfd6cedae8a0676c1ffd23c7f0243cc403dd341eb6c81c3":
        raise AssertionError("opening audit drift")

    records = [
        json.loads(line)
        for line in gate.CATALOG.read_text(encoding="utf-8").splitlines()
        if line
    ]
    parents, parent_sign_digest = gate.parent_polynomials(records[2599])
    labels = tuple(label for label, _target, _polynomial, _terms in parents)
    if len(labels) != 70 or len(set(labels)) != 70:
        raise AssertionError("parent-tag inventory drift")

    candidates = gate.parse_candidates()
    _occurrences, _occurrence_factor, factors = labeled.factor_polynomials()
    if TARGET_FACTOR not in candidates:
        raise AssertionError("factor 19069 left the row-2599 candidate universe")
    factor = factors[TARGET_FACTOR]
    factor_multidegree = tuple(
        max(sum(monomial[index] for index in group) for monomial in factor)
        for group in bernstein.GROUPS
    )
    if polynomial_degree(factor) != 6 or len(factor) != 108:
        raise AssertionError("factor-19069 structural census drift")
    if factor_multidegree != (2, 2, 2):
        raise AssertionError("factor-19069 multidegree drift")

    _matrices, points, _packed, _states, _hamming, _multiplicity = (
        transition.exact_inputs()
    )
    cover = json.loads(
        (DATA / "DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json").read_text(
            encoding="utf-8"
        )
    )
    selected = tuple(cover["source_bank"]["selected_edge_indices"])
    if len(selected) != 40:
        raise AssertionError("fixed skeleton edge census drift")

    path_tag_state = sha256(b"d9-factor19069-all-parent-path-tags-v1\0")
    for edge_index in selected:
        left, right = safe.EDGES[edge_index]
        for label, target, polynomial, _terms in parents:
            restricted = safe.segment_power(polynomial, points[left], points[right])
            if not safe.positive_unit(
                [target * coefficient for coefficient in restricted]
            ):
                raise AssertionError(
                    f"parent path tag failed: edge={edge_index} bracket={label}"
                )
            path_tag_state.update(edge_index.to_bytes(2, "little"))
            path_tag_state.update(label.encode("ascii"))

    root_counts = {}
    for edge_index in selected:
        left, right = safe.EDGES[edge_index]
        root_counts[str(edge_index)] = root_count_open(
            safe.segment_power(factor, points[left], points[right])
        )
    rooted_edges = [int(edge) for edge, count in root_counts.items() if count]
    if rooted_edges != [39] or root_counts["39"] != 1:
        raise AssertionError("factor-19069 skeleton incidence drift")

    collar = json.loads(
        (DATA / "DIAG3_PAIR_FULLSUPPORT_COMPONENT_COLLAR.json").read_text(
            encoding="utf-8"
        )
    )
    if collar["target_selection"]["factor_id"] != TARGET_FACTOR:
        raise AssertionError("collar target drift")
    if collar["target_selection"]["unique_edge_index"] != 39:
        raise AssertionError("collar edge drift")
    if collar["component_coverage"]["declared_scope_component_count"] != 1:
        raise AssertionError("collar component drift")
    if collar["component_coverage"]["meets_retained_source_skeleton"] is not True:
        raise AssertionError("collar attachment drift")

    parent_face = json.loads(
        (DATA / "DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json").read_text(
            encoding="utf-8"
        )
    )
    boundary_frontier = []
    for record in parent_face["nonexcluded_support_faces"]:
        face = tuple(record["support"])
        boundary_frontier.append(
            {
                "support": list(face),
                "dimension": record["dimension"],
                "parent_bernstein_classification": record["classification"].upper(),
                "weak_sign_witness_zero_parent_brackets": record[
                    "witness_zero_parent_brackets"
                ],
                "factor19069_restriction": restriction_state(
                    factor, factor_multidegree, face
                ),
                "path_tag_to_pinned_parent_component_closure": "ABSENT",
            }
        )
    proper_boundary = [
        record for record in boundary_frontier if record["dimension"] < 9
    ]
    proper_state_counts = {
        state: sum(record["factor19069_restriction"] == state for record in proper_boundary)
        for state in (
            "IDENTICALLY_ZERO",
            "BERNSTEIN_MIXED_UNRESOLVED",
            "BERNSTEIN_POSITIVE",
            "BERNSTEIN_NEGATIVE",
        )
    }
    if proper_state_counts != {
        "IDENTICALLY_ZERO": 8,
        "BERNSTEIN_MIXED_UNRESOLVED": 2,
        "BERNSTEIN_POSITIVE": 0,
        "BERNSTEIN_NEGATIVE": 0,
    }:
        raise AssertionError("factor-19069 support-boundary frontier drift")

    active_counts = {str(size): comb(70, size) for size in range(1, 10)}
    cumulative = {}
    running = 0
    for size in range(1, 10):
        running += active_counts[str(size)]
        cumulative[str(size)] = running
    if cumulative["3"] != 57_225 or cumulative["4"] != 974_120:
        raise AssertionError("active-support frontier census drift")
    if cumulative["9"] != 75_816_847_319:
        raise AssertionError("Caratheodory-support frontier census drift")

    parent_inventory = [
        {
            "label": label,
            "target_sign": target,
            "affine_degree": polynomial_degree(polynomial),
            "term_count": len(polynomial),
        }
        for label, target, polynomial, _terms in parents
    ]
    parent_inventory_digest = canonical_digest({"parents": parent_inventory})

    payload = {
        "format": "d9-factor19069-active-margin-frontier-v1",
        "track_id": "d9-factor19069-active-margin-constructor",
        "opening_revision": OPENING_REVISION,
        "opening_tree": OPENING_TREE,
        "classification": "EXACT_FAIL_CLOSED_PARENT_RESIDENCE_NULL",
        "endpoint": "HASH_PINNED_PARENT_RESIDENT_CRITICAL_COMPONENT_FRONTIER_WITH_FIRST_UNCLASSIFIED_STRATUM",
        "target": {
            "parent_index": 2599,
            "factor_id": TARGET_FACTOR,
            "ambient_parameter_dimension": 9,
            "factor_total_degree": 6,
            "factor_multidegree": list(factor_multidegree),
            "factor_term_count": 108,
            "parent_sign_tags": 70,
            "parent_sign_digest": parent_sign_digest,
            "parent_inventory_semantic_sha256": parent_inventory_digest,
            "parent_inventory": parent_inventory,
            "fixed_skeleton_edges": 40,
        },
        "exact_source_replay": {
            "all_40_edges_have_all_70_strict_parent_path_tags": True,
            "parent_path_tag_checks": 2_800,
            "parent_path_tag_semantic_sha256": path_tag_state.hexdigest(),
            "factor19069_open_root_counts_by_skeleton_edge": root_counts,
            "factor19069_rooted_skeleton_edges": rooted_edges,
            "accepted_local_collar_components": 1,
            "accepted_local_collar_attachment_edge": 39,
            "global_component_inference_from_collar": False,
        },
        "active_margin_frontier": {
            "stationarity_support_bound": 9,
            "support_bound_reason": "Caratheodory on the eight-dimensional wall tangent quotient",
            "candidate_active_sets_by_support_size": active_counts,
            "cumulative_candidate_active_sets": cumulative,
            "opening_exact_system_ceiling": SYSTEM_CEILING,
            "largest_unfiltered_support_size_below_ceiling": 3,
            "first_support_size_exceeding_ceiling": 4,
            "complete_source_derived_active_tie_incidence_filter": "ABSENT",
            "critical_systems_solved": 0,
            "component_samples_constructed": 0,
        },
        "true_boundary_frontier": {
            "ambient_product_support_strata": parent_face[
                "excluded_support_face_count"
            ] + parent_face["nonexcluded_support_face_count"],
            "parent_bernstein_excluded_support_strata": parent_face[
                "excluded_support_face_count"
            ],
            "nonexcluded_support_strata": parent_face[
                "nonexcluded_support_face_count"
            ],
            "proper_nonexcluded_support_strata": len(proper_boundary),
            "factor19069_proper_support_state_counts": proper_state_counts,
            "records": boundary_frontier,
            "complete_parent_component_closure_path_tags": False,
            "first_unclassified_stratum": {
                "obligation": "PARENT_COMPONENT_CLOSURE_RESIDENCE",
                "support": [1, 1, 1],
                "factor19069_restriction": "IDENTICALLY_ZERO",
                "missing": "EXACT_PATH_TAG_FROM_THE_PINNED_PARENT_COMPONENT_TO_THIS_WEAK_SIGN_BOUNDARY_WITNESS",
            },
        },
        "component_classification": {
            "complete_wall_component_count": None,
            "attached_global_components": None,
            "unattached_global_components": None,
            "status": "UNCLASSIFIED_FAIL_CLOSED",
        },
        "exact_consequences": [
            "FACTOR19069_MEETS_THE_FIXED_SKELETON_ONLY_ON_EDGE39_WITH_ONE_EXACT_OPEN_ROOT",
            "ALL_40_SKELETON_EDGES_RETAIN_ALL_70_STRICT_PARENT_PATH_TAGS",
            "EIGHT_NONEXCLUDED_PROPER_SUPPORT_RESTRICTIONS_ARE_IDENTICALLY_ZERO_AND_TWO_ARE_BERNSTEIN_MIXED",
            "UNFILTERED_ACTIVE_MARGIN_SUPPORTS_EXCEED_THE_100000_SYSTEM_CEILING_AT_SUPPORT_SIZE_FOUR",
        ],
        "nonconsequences": [
            "NO_PROOF_THAT_ANY_AMBIGUOUS_WEAK_SIGN_SUPPORT_FACE_LIES_IN_THE_CLOSURE_OF_THE_PINNED_PARENT_COMPONENT",
            "NO_COMPLETE_ACTIVE_MARGIN_TIE_STRATIFICATION",
            "NO_EXACT_GLOBAL_FACTOR19069_COMPONENT_SAMPLE",
            "NO_GLOBAL_COMPONENT_TO_SKELETON_ATTACHMENT_CLASSIFICATION",
            "NO_DIAGONAL_9_PROOF_OR_COUNTEREXAMPLE",
            "NO_9DVL_SCORE_CHANGE",
        ],
        "next_action": "D9_ROW2599_FACTOR19069_FACTORED_BARRIER_COMPONENT_SAMPLER_GATE1: replace nonsmooth active-set enumeration by the one factored product barrier critical locus, while retaining every parent factor and exact parent-component path tags.",
        "theorem_ledger": "2/9",
        "sources": {
            OPENING_AUDIT: digest_path(ROOT / OPENING_AUDIT),
            "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_COMPONENT_COLLAR.json": digest_path(DATA / "DIAG3_PAIR_FULLSUPPORT_COMPONENT_COLLAR.json"),
            "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json": digest_path(DATA / "DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json"),
            "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json": digest_path(DATA / "DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json"),
            "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json": digest_path(DATA / "DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json"),
        },
    }
    payload["semantic_sha256"] = canonical_digest(payload)
    return payload


def main() -> None:
    payload = build()
    OUTPUT.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print("PASS exact factor-19069 / 70-parent / 40-edge source replay")
    print("PASS skeleton roots: edge39=1, all other retained edges=0")
    print("PASS boundary frontier: 8 identically-zero, 2 mixed proper support restrictions")
    print("NULL active supports through size 9=75816847319; ceiling crossed at size 4")
    print("SCOPE no complete parent-resident component sample; ledger remains 2/9")


if __name__ == "__main__":
    main()
