#!/usr/bin/env python3
"""Exact chart-89 attachment to the genuine parent divisor [1237]=0."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUTPUT = DATA / "DIAG3_PAIR_PARENT_BOUNDARY_ATTACHMENT_89_1237.json"
ATLAS = DATA / "DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json"
SOURCE_LABELS = DATA / "DIAG3_PAIR_PARENT_SOURCE_LABELS_0_89.json"
SOURCE_CHART = 89
LABELLED_SOURCE_CHARTS = (0, 89, 152)
VARIABLE_INDEX = 5
MOVING_COLUMN = 7
COORDINATE_ROW = 4
BOUNDARY_BRACKET = "1237"
FORMAT = "diag3-pair-parent-boundary-attachment-v1"
STATUS = "EXACT_GENUINE_PARENT_BOUNDARY_ATTACHMENT"
ISOLATION_WIDTH = Fraction(1, 1 << 28)

sys.path.insert(0, str(HERE))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402
import diag3_pair_parent_source_labels_core as source_labels  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402
import verify_diag2_canonical_robust_edges as evaluator  # noqa: E402
import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


def fraction_text(value: Fraction) -> str:
    return transition.fraction_text(value)


def boundary_endpoint(values, variable_index):
    endpoint = list(values)
    endpoint[variable_index] = Fraction(0)
    return tuple(endpoint)


def boundary_ray(values, parameter):
    endpoint = boundary_endpoint(values, VARIABLE_INDEX)
    return tuple(
        (1 - parameter) * left + parameter * right
        for left, right in zip(values, endpoint, strict=True)
    )


def isolate_roots(polynomial):
    total = sturm.root_count(polynomial, Fraction(0), Fraction(1))
    stack = [(Fraction(0), Fraction(1), total)]
    answer = []
    while stack:
        left, right, count = stack.pop()
        if not count:
            continue
        if count == 1 and right - left <= ISOLATION_WIDTH:
            answer.append((left, right))
            continue
        middle = transition.nonroot_split(polynomial, left, right)
        left_count = sturm.root_count(polynomial, left, middle)
        right_count = sturm.root_count(polynomial, middle, right)
        if left_count + right_count != count:
            raise AssertionError("Sturm subdivision lost a boundary-ray root")
        stack.append((middle, right, right_count))
        stack.append((left, middle, left_count))
    answer.sort()
    if len(answer) != total:
        raise AssertionError("boundary-ray root isolation census changed")
    return answer


def parent_safe_coordinate_rays(points, parents):
    candidates = []
    for chart_index, source in enumerate(points):
        for variable_index in range(9):
            endpoint = boundary_endpoint(source, variable_index)
            boundary_labels = []
            valid = True
            for label, target, polynomial, _terms in parents:
                restricted = [target * value for value in safe.segment_power(
                    polynomial, source, endpoint
                )]
                endpoint_value = target * evaluator.evaluate(polynomial, endpoint)
                if endpoint_value == 0:
                    boundary_labels.append(label)
                    if evaluator.evaluate(polynomial, source) * target <= 0:
                        valid = False
                elif not safe.positive_unit(restricted):
                    valid = False
            if valid and len(boundary_labels) == 1:
                candidates.append({
                    "chart_index": chart_index,
                    "normalized_variable_index": variable_index,
                    "moving_column": 6 + variable_index // 3,
                    "coordinate_row": 2 + variable_index % 3,
                    "boundary_parent_bracket": boundary_labels[0],
                })
    return candidates


def build_record(progress=False):
    matrices, points, _packed, states, _hamming, multiplicity = transition.exact_inputs()
    records = [json.loads(line) for line in safe.CATALOG.read_text().splitlines() if line]
    parents, _parent_digest = gate.parent_polynomials(records[2599])

    ray_candidates = parent_safe_coordinate_rays(points, parents)
    if len(ray_candidates) != 29:
        raise AssertionError(f"parent-safe coordinate-ray census changed: {len(ray_candidates)}")
    labelled_candidates = [
        row for row in ray_candidates if row["chart_index"] in LABELLED_SOURCE_CHARTS
    ]
    if labelled_candidates != [{
        "chart_index": SOURCE_CHART,
        "normalized_variable_index": VARIABLE_INDEX,
        "moving_column": MOVING_COLUMN,
        "coordinate_row": COORDINATE_ROW,
        "boundary_parent_bracket": BOUNDARY_BRACKET,
    }]:
        raise AssertionError(f"labelled source boundary choice changed: {labelled_candidates}")

    atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
    divisor = next(
        row for row in atlas["boundary_divisors"]
        if row["moving_column"] == MOVING_COLUMN
        and row["coordinate_row"] == COORDINATE_ROW
    )
    if divisor["parent_bracket"] != BOUNDARY_BRACKET:
        raise AssertionError("compactification divisor map changed")

    source = points[SOURCE_CHART]
    endpoint = boundary_endpoint(source, VARIABLE_INDEX)
    boundary_labels = []
    parent_endpoint_signs = {}
    for label, target, polynomial, _terms in parents:
        restricted = [target * value for value in safe.segment_power(polynomial, source, endpoint)]
        start_value = target * evaluator.evaluate(polynomial, source)
        endpoint_value = target * evaluator.evaluate(polynomial, endpoint)
        if start_value <= 0:
            raise AssertionError("source left the strict parent cell")
        if endpoint_value == 0:
            boundary_labels.append(label)
            if label != BOUNDARY_BRACKET or restricted[0] <= 0:
                raise AssertionError("wrong parent wall on boundary ray")
            if sum(restricted) != 0:
                raise AssertionError("boundary bracket does not vanish at the endpoint")
        elif not safe.positive_unit(restricted):
            raise AssertionError(f"parent bracket {label} is not strict on the closed ray")
        parent_endpoint_signs[label] = 0 if endpoint_value == 0 else 1
    if boundary_labels != [BOUNDARY_BRACKET]:
        raise AssertionError(f"boundary ray acquired the wrong parent zeros: {boundary_labels}")

    candidates = gate.parse_candidates()
    _factor_types, _factor_terms, polynomials = labeled.factor_polynomials()
    root_census = Counter()
    events = []
    endpoint_sign_bits = bytearray((len(candidates) + 7) // 8)
    for candidate_index, factor_id in enumerate(candidates):
        restricted = transition.primitive_univariate(
            safe.segment_power(polynomials[factor_id], source, endpoint)
        )
        if sturm.polynomial_value(restricted, Fraction(1)) == 0:
            raise AssertionError(f"residual factor {factor_id} vanishes at the parent endpoint")
        root_count = sturm.root_count(restricted, Fraction(0), Fraction(1))
        root_census[root_count] += 1
        if sturm.polynomial_value(restricted, Fraction(1)) > 0:
            endpoint_sign_bits[candidate_index // 8] |= 1 << (candidate_index & 7)
        for root_index, (left, right) in enumerate(isolate_roots(restricted)):
            left_value = sturm.polynomial_value(restricted, left)
            right_value = sturm.polynomial_value(restricted, right)
            if not left_value or not right_value:
                raise AssertionError("boundary-ray isolating endpoint is a root")
            events.append({
                "factor_id": int(factor_id),
                "factor_degree": len(restricted) - 1,
                "occurrence_multiplicity": int(multiplicity[factor_id]),
                "root_index_within_factor": root_index,
                "isolating_interval": [fraction_text(left), fraction_text(right)],
                "sign_flip": (left_value > 0) != (right_value > 0),
            })
        if progress and (candidate_index + 1) % 4000 == 0:
            print(f"screened {candidate_index + 1}/{len(candidates)} boundary-ray factors", flush=True)

    events.sort(key=lambda row: sum(map(Fraction, row["isolating_interval"])) / 2)
    for left, right in zip(events, events[1:]):
        if Fraction(left["isolating_interval"][1]) > Fraction(right["isolating_interval"][0]):
            raise AssertionError("boundary-ray event boxes overlap")
    if root_census != Counter({0: 16_307, 1: 1_517}) or len(events) != 1_517:
        raise AssertionError((root_census, len(events)))
    if not all(event["sign_flip"] for event in events):
        raise AssertionError("boundary ray acquired a tangent or multiple residual event")

    event_multiplicity = Counter(event["occurrence_multiplicity"] for event in events)
    state = states[SOURCE_CHART].copy()
    state_digest = sha256(b"diag3-row2599-boundary-89-1237-factor-states-v1\0")
    state_digest.update(np.packbits(state, bitorder="little").tobytes())
    for event in events:
        state[event["factor_id"]] ^= np.uint8(1)
        state_digest.update(np.packbits(state, bitorder="little").tobytes())

    event_digest = sha256(b"diag3-row2599-boundary-89-1237-events-v1\0")
    for event in events:
        event_digest.update(event["factor_id"].to_bytes(4, "little"))
        event_digest.update(event["factor_degree"].to_bytes(1, "little"))
        event_digest.update(event["occurrence_multiplicity"].to_bytes(2, "little"))
        for value in map(Fraction, event["isolating_interval"]):
            event_digest.update(value.numerator.to_bytes(16, "little", signed=True))
            event_digest.update(value.denominator.to_bytes(16, "little"))

    source_label_record = json.loads(SOURCE_LABELS.read_text(encoding="utf-8"))
    source_label_digest = source_label_record["continuation"]["event_records"][-1][
        "post_chamber_labels_sha256"
    ]
    return {
        "format": FORMAT,
        "status": STATUS,
        "scope": {
            "parent_index": 2599,
            "source_chart": SOURCE_CHART,
            "target_parent_divisor": f"[{BOUNDARY_BRACKET}]=0",
            "path": "one normalized positive-simplex coordinate decreases linearly to zero",
            "parent_parameter_coverage": "COMPLETE_ON_CLOSED_RAY",
            "residual_parameter_coverage": "COMPLETE_ON_OPEN_RAY_AND_ENDPOINT",
            "signature_label_continuation": "OPEN_PENDING_BOUNDARY_PATH_LABEL_CERTIFICATE",
            "global_parent_cell_coverage": "NOT_CLAIMED",
        },
        "inputs": {
            "point_bank_path": str(transition.POINT_BANK.relative_to(HERE.parents[1])),
            "point_bank_sha256": transition.file_sha256(transition.POINT_BANK),
            "candidate_factor_path": str(transition.CANDIDATES.relative_to(HERE.parents[1])),
            "candidate_factor_sha256": transition.file_sha256(transition.CANDIDATES),
            "factor_census_path": str(transition.FACTOR_CENSUS.relative_to(HERE.parents[1])),
            "factor_census_sha256": transition.file_sha256(transition.FACTOR_CENSUS),
            "compactification_atlas": str(ATLAS.relative_to(HERE.parents[1])),
            "compactification_atlas_sha256": transition.file_sha256(ATLAS),
            "source_label_certificate": str(SOURCE_LABELS.relative_to(HERE.parents[1])),
            "source_label_certificate_sha256": transition.file_sha256(SOURCE_LABELS),
        },
        "selection": {
            "stored_chart_count": len(points),
            "finite_coordinate_rays_per_chart": 9,
            "parent_safe_single_divisor_rays": len(ray_candidates),
            "parent_safe_ray_candidates": ray_candidates,
            "currently_labelled_source_charts": list(LABELLED_SOURCE_CHARTS),
            "labelled_source_candidate_count": len(labelled_candidates),
            "selection_rule": "unique parent-safe finite coordinate ray from the currently labelled source charts",
        },
        "parent_residence": {
            "parent_bracket_count": len(parents),
            "strict_on_open_ray": True,
            "strict_at_endpoint_except_target": len(parents) - 1,
            "endpoint_parent_sign_census": {
                "positive": sum(value == 1 for value in parent_endpoint_signs.values()),
                "zero": sum(value == 0 for value in parent_endpoint_signs.values()),
            },
            "target_boundary_bracket": BOUNDARY_BRACKET,
            "target_boundary_is_genuine_parent_divisor": True,
            "compactification_divisor_record": divisor,
        },
        "overlap_with_labelled_0_89_path": {
            "shared_chart": SOURCE_CHART,
            "source_path_terminal_labels_sha256": source_label_digest,
            "compatibility": "EXACT_COMMON_SOURCE_VERTEX_AND_RAW_LABEL_SET",
        },
        "residual_roadmap": {
            "candidate_factor_count": len(candidates),
            "factor_root_count_census": {
                str(key): value for key, value in sorted(root_census.items())
            },
            "ordered_root_events": len(events),
            "event_occurrence_multiplicity_census": {
                str(key): value for key, value in sorted(event_multiplicity.items())
            },
            "endpoint_zero_residual_factors": 0,
            "endpoint_candidate_signs_sha256": sha256(
                b"diag3-row2599-boundary-89-1237-endpoint-candidate-signs-v1\0"
                + bytes(endpoint_sign_bits)
            ).hexdigest(),
            "isolation_width_ceiling": fraction_text(ISOLATION_WIDTH),
            "all_root_boxes_pairwise_ordered": True,
            "all_roots_simple_sign_crossings": True,
            "events_semantic_sha256": event_digest.hexdigest(),
            "factor_state_sequence_sha256": state_digest.hexdigest(),
            "events": events,
        },
        "regular_cw_path": {
            "zero_cells": len(events) + 2,
            "one_cells": len(events) + 1,
            "total_cells": 2 * len(events) + 3,
            "strict_closure_pairs": 2 * (len(events) + 1),
            "scope_endpoint_cells": ["endpoint_chart_89", "endpoint_parent_divisor_1237"],
            "parent_infinity_subcomplex": ["endpoint_parent_divisor_1237"],
        },
        "theorem_effect": "Adds the first exact labelled-source attachment to a genuine row-2599 parent-boundary divisor; closes neither invariant diagonal-three obligation and leaves 9DVL at 2/9.",
        "next_exact_question": "Continue all 26,112 labels to the relative endpoint, then prove missed-component coverage or replace the finite source skeleton by a coverage-certified global master complex.",
        "verifier": {
            "command": "python ai/omreal/verify_diag3_pair_parent_boundary_attachment.py",
            "hostile_corruptions": 12,
        },
    }
