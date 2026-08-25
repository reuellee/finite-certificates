#!/usr/bin/env python3
"""Independent hostile replay of the source-family incidence no-go."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_SOURCE_FAMILY_INCIDENCE_NO_GO_0_152.json"
STARTS = (Fraction(0), Fraction(0), Fraction(0))
ENDS = (Fraction(1), Fraction(1), Fraction(1))

sys.path.insert(0, str(HERE))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG9_GRAPH_row2599_factor_states as states  # noqa: E402
import diag3_pair_parent_source_block_bridge_core as bridge  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402
import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402
import verify_diag3_pair_source_block_cube_feasibility as base  # noqa: E402


def digest_ids(domain, identifiers):
    return base.digest_ids(domain, sorted(identifiers))


def reconstruct():
    _matrices, points, _packed, _states, _hamming, _multiplicity = transition.exact_inputs()
    source, target = points[0], points[152]
    rows = [json.loads(line) for line in bridge.safe.CATALOG.read_text().splitlines() if line]
    parents, _parent_digest = gate.parent_polynomials(rows[2599])
    candidates = gate.parse_candidates()
    _types, _terms, polynomials = labeled.factor_polynomials()

    # Recheck that every crossing edge stays in the strict signed parent cell.
    for left, right in safe.EDGES:
        for _label, target_sign, polynomial, _terms in parents:
            coefficients = [
                target_sign * value
                for value in safe.segment_power(polynomial, points[left], points[right])
            ]
            assert safe.positive_unit(coefficients)

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
    assert len(crossed) == safe.EXPECTED_CROSSED == 10_844
    assert len(open_ids) == safe.EXPECTED_OPEN == 6_980
    assert sha256(",".join(map(str, open_ids)).encode("ascii")).hexdigest() == safe.EXPECTED_OPEN_SHA256

    source_occurring = set()
    source_zero_free = set()
    source_status = {}
    for factor_id in candidates:
        restricted = base.pullback(polynomials[factor_id], source, target, STARTS, ENDS)
        status, depth, visited = base.decide(*base.controls(restricted))
        source_status[factor_id] = status, depth, visited, restricted
        if status == "NONEMPTY_CORNER":
            source_occurring.add(factor_id)
        elif status == "EMPTY_BERNSTEIN":
            source_zero_free.add(factor_id)
        else:
            raise AssertionError((factor_id, status))

    known_and_source = crossed & source_occurring
    missed = crossed & source_zero_free
    source_not_on_segments = source_occurring - crossed
    assert missed
    # Do not trust the packed sign matrix at the final trust boundary: replay
    # exact opposite endpoint values for every no-go factor.
    exact_endpoint_values = {}
    for factor_id in missed:
        left, right = first_edge[factor_id]
        left_value = base.coordinate_value(polynomials[factor_id], points[left])
        right_value = base.coordinate_value(polynomials[factor_id], points[right])
        assert left_value * right_value < 0
        exact_endpoint_values[factor_id] = left_value, right_value

    least = min(missed)
    left, right = first_edge[least]
    left_value, right_value = exact_endpoint_values[least]
    status, depth, visited, restricted = source_status[least]
    return {
        "format": "diag3-pair-source-family-incidence-no-go-v1",
        "status": "EXACT_UNIVERSAL_SOURCE_FAMILY_INCIDENCE_REFUTED",
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
            "exact_left_value": base.fraction_text(left_value),
            "exact_right_value": base.fraction_text(right_value),
            "opposite_endpoint_signs": True,
            "source_cube_status": status,
            "source_cube_classification_depth": depth,
            "source_cube_subboxes_visited": visited,
            "source_cube_restriction_primitive_integer": repr(
                base.normalized_integer(restricted)
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


def validate(candidate, expected):
    assert candidate == expected
    census = candidate["census"]
    assert census["known_parent_interior_walls"] == 10_844
    assert census["source_cube_occurring_walls"] == 5_577
    assert census["known_parent_walls_meeting_source_cube"] == 5_454
    assert census["known_parent_walls_zero_free_on_source_cube"] == 5_390
    assert census["source_cube_walls_not_crossed_by_safe_segments"] == 123
    assert census["source_cube_zero_free_walls"] == 12_247
    assert candidate["scope"]["decision"] == "REFUTED"
    assert candidate["scope"]["global_pair_obligation"] == "OPEN"
    assert candidate["least_counterexample"]["opposite_endpoint_signs"] is True
    assert candidate["least_counterexample"]["source_cube_status"] == "EMPTY_BERNSTEIN"
    assert candidate["research_decision"]["further_staircase_refinement"] == "RETIRED_FOR_GLOBAL_INCIDENCE"


def main():
    stored = json.loads(CERTIFICATE.read_text())
    expected = reconstruct()
    validate(stored, expected)
    mutations = []
    for path, value in (
        (("format",), "corrupted"),
        (("scope", "decision"), "PROVED"),
        (("scope", "global_pair_obligation"), "CLOSED"),
        (("census", "known_parent_interior_walls"), 10_843),
        (("census", "known_parent_walls_zero_free_on_source_cube"), 0),
        (("digests", "known_parent_walls_zero_free_on_source_cube_sha256"), "0" * 64),
        (("least_counterexample", "opposite_endpoint_signs"), False),
        (("least_counterexample", "source_cube_status"), "NONEMPTY_CORNER"),
        (("research_decision", "retired_target"), "NONE"),
        (("research_decision", "further_staircase_refinement"), "ACTIVE"),
        (("proof", "conclusion"), "GLOBAL_PAIR_PROVED"),
    ):
        mutation = deepcopy(stored)
        target = mutation
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        mutations.append(mutation)
    rejected = 0
    for mutation in mutations:
        try:
            validate(mutation, expected)
        except AssertionError:
            rejected += 1
    assert rejected == len(mutations)
    print("PASS all 105 crossing segments independently remain in the strict parent cell")
    print("PASS 10,844 known parent walls versus 5,577 full-source-cube walls")
    print("PASS 5,390 known parent walls are exactly zero-free on the source cube")
    print("PASS exact endpoint sign crossings replayed for every no-go factor")
    print("PASS universal chart-0/chart-152 source-family incidence target refuted")
    print(f"PASS {rejected}/{len(mutations)} hostile corruptions rejected")
    print("SCOPE source-family no-go only; direct global roadmap/master complex remains open; honest 9DVL 2/9")


if __name__ == "__main__":
    main()
