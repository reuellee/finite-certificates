#!/usr/bin/env python3
"""Exact no-go to universal incidence with the chart-0/chart-152 source cube."""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "data" / "DIAG3_PAIR_SOURCE_FAMILY_INCIDENCE_NO_GO_0_152.json"
FORMAT = "diag3-pair-source-family-incidence-no-go-v1"
STATUS = "EXACT_UNIVERSAL_SOURCE_FAMILY_INCIDENCE_REFUTED"
STARTS = (Fraction(0), Fraction(0), Fraction(0))
ENDS = (Fraction(1), Fraction(1), Fraction(1))

sys.path.insert(0, str(HERE))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG9_GRAPH_row2599_factor_states as states  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402
import diag3_pair_source_cube_feasibility_core as cube  # noqa: E402
import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


def digest_ids(domain, identifiers):
    return cube.id_digest(domain, sorted(identifiers))


def exact_crossing_sets(candidates):
    with np.load(states.CERTIFICATE, allow_pickle=False) as record:
        packed = np.asarray(record["chart_factor_sign_packed"], dtype=np.uint8)
    signs = np.unpackbits(packed, axis=1, bitorder="little")[:, :26_740]
    first_edge = {}
    for factor_id in candidates:
        for edge in safe.EDGES:
            left, right = edge
            if signs[left, factor_id] != signs[right, factor_id]:
                first_edge[factor_id] = edge
                break
    crossed = set(first_edge)
    open_ids = sorted(set(candidates) - crossed)
    open_digest = sha256(",".join(map(str, open_ids)).encode("ascii")).hexdigest()
    if len(crossed) != safe.EXPECTED_CROSSED or len(open_ids) != safe.EXPECTED_OPEN:
        raise AssertionError("safe-segment crossing census changed")
    if open_digest != safe.EXPECTED_OPEN_SHA256:
        raise AssertionError("safe-segment open-factor digest changed")
    return crossed, first_edge


def build_record(progress=False):
    _matrices, points, _packed, _states, _hamming, _multiplicity = transition.exact_inputs()
    source, target = points[0], points[152]
    candidates = gate.parse_candidates()
    _types, _terms, polynomials = labeled.factor_polynomials()
    crossed, first_edge = exact_crossing_sets(candidates)

    source_occurring = set()
    source_zero_free = set()
    source_status = {}
    for offset, factor_id in enumerate(candidates, start=1):
        restricted = cube.restrict_cube(
            polynomials[factor_id], source, target, STARTS, ENDS
        )
        status, depth, visited = cube.classify_bernstein(
            *cube.bernstein_control(restricted)
        )
        source_status[factor_id] = status, depth, visited, restricted
        if status == "NONEMPTY_CORNER":
            source_occurring.add(factor_id)
        elif status == "EMPTY_BERNSTEIN":
            source_zero_free.add(factor_id)
        else:
            raise AssertionError((factor_id, status))
        if progress and offset % 4000 == 0:
            print(f"classified {offset}/{len(candidates)} source-cube restrictions", flush=True)

    known_and_source = crossed & source_occurring
    missed = crossed & source_zero_free
    source_not_on_segments = source_occurring - crossed
    if not missed:
        raise AssertionError("the proposed universal incidence theorem was not refuted")
    least = min(missed)
    left, right = first_edge[least]
    left_value = cube.evaluate_coordinate_polynomial(polynomials[least], points[left])
    right_value = cube.evaluate_coordinate_polynomial(polynomials[least], points[right])
    if left_value * right_value >= 0:
        raise AssertionError("least no-go witness lacks an exact sign crossing")
    status, depth, visited, restricted = source_status[least]
    if status != "EMPTY_BERNSTEIN":
        raise AssertionError("least no-go witness is not source-cube zero-free")

    return {
        "format": FORMAT,
        "status": STATUS,
        "scope": {
            "parent_index": 2599,
            "source_chart": 0,
            "target_chart": 152,
            "source_family": "full normalized three-parameter chart-0/chart-152 hybrid cube",
            "known_parent_wall_certificate": "105 exact parent-safe chart segments",
            "universal_claim_tested": "EVERY_ROW2599_PARENT_INTERIOR_WALL_MEETS_THIS_SOURCE_FAMILY",
            "decision": "REFUTED",
            "global_pair_obligation": "OPEN",
        },
        "census": {
            "candidate_factors": len(candidates),
            "known_parent_interior_walls": len(crossed),
            "source_cube_occurring_walls": len(source_occurring),
            "known_parent_walls_meeting_source_cube": len(known_and_source),
            "known_parent_walls_zero_free_on_source_cube": len(missed),
            "source_cube_walls_not_crossed_by_safe_segments": len(source_not_on_segments),
            "source_cube_zero_free_walls": len(source_zero_free),
            "accounting_identities": [
                f"{len(known_and_source)}+{len(missed)}={len(crossed)}",
                f"{len(known_and_source)}+{len(source_not_on_segments)}={len(source_occurring)}",
                f"{len(source_occurring)}+{len(source_zero_free)}={len(candidates)}",
            ],
        },
        "digests": {
            "known_parent_interior_factor_ids_sha256": digest_ids(
                b"diag3-known-parent-interior-walls-v1", crossed
            ),
            "source_cube_occurring_factor_ids_sha256": digest_ids(
                b"diag3-full-hybrid-cube-occurring-v1", source_occurring
            ),
            "known_parent_walls_meeting_source_cube_sha256": digest_ids(
                b"diag3-known-parent-walls-source-cube-intersection-v1", known_and_source
            ),
            "known_parent_walls_zero_free_on_source_cube_sha256": digest_ids(
                b"diag3-known-parent-walls-source-cube-free-v1", missed
            ),
            "source_cube_walls_not_crossed_by_safe_segments_sha256": digest_ids(
                b"diag3-source-cube-walls-not-safe-segment-crossed-v1",
                source_not_on_segments,
            ),
            "row2599_factor_state_semantic_sha256": states.EXPECTED_DIGEST,
        },
        "least_counterexample": {
            "factor_id": least,
            "parent_safe_segment_charts": [left, right],
            "exact_left_value": cube.fraction_text(left_value),
            "exact_right_value": cube.fraction_text(right_value),
            "opposite_endpoint_signs": True,
            "source_cube_status": status,
            "source_cube_classification_depth": depth,
            "source_cube_subboxes_visited": visited,
            "source_cube_restriction_primitive_integer": repr(
                cube.canonical_integer(restricted)
            ),
        },
        "proof": {
            "parent_interior_occurrence": "Each known wall has opposite exact signs at the endpoints of a segment certified to remain in the strict row-2599 parent cell, so continuity gives a parent-interior zero.",
            "source_family_nonincidence": "A one-signed tensor-Bernstein subdivision certifies the same factor zero-free on the entire full source cube.",
            "conclusion": "For every factor in the 5390-element no-go set, at least one row-2599 parent-interior wall component exists and no component of that factor meets the chart-0/chart-152 source family.",
        },
        "research_decision": {
            "retired_target": "PROVE_EVERY_GLOBAL_WALL_COMPONENT_MEETS_CHART0_CHART152_SOURCE_FAMILY",
            "replacement_target": "ADD_GENUINELY_DISTINCT_SOURCE_FAMILIES_OR_BUILD_A_DIRECT_GLOBAL_ROADMAP_MASTER_COMPLEX",
            "further_staircase_refinement": "RETIRED_FOR_GLOBAL_INCIDENCE",
        },
        "theorem_effect": "Refutes the proposed universal source-family incidence lemma without closing the global pair or triple obligation; honest 9DVL score remains 2/9.",
    }
