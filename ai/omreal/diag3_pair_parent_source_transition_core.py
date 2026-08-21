#!/usr/bin/env python3
"""Exact 1D residual roadmap from row-2599 chart 0 to chart 89."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from math import gcd, lcm
from pathlib import Path
import json
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUTPUT = DATA / "DIAG3_PAIR_PARENT_SOURCE_TRANSITION_0_89.json"
POINT_BANK = DATA / "seeat_parent2599_upper178.npz"
FACTOR_STATES = DATA / "DIAG9_GRAPH_row2599_factor_states.npz"
FACTOR_CENSUS = DATA / "DIAG9_GRAPH_global_factor_census.npz"
CANDIDATES = DATA / "DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin"
SOURCE_CHART = 0
TARGET_CHART = 89
ISOLATION_WIDTH = Fraction(1, 1 << 22)

sys.path.insert(0, str(HERE))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402
import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


FORMAT = "diag3-pair-parent-source-transition-v1"
STATUS = "EXACT_SOURCE_TRANSITION_ROADMAP"


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def primitive_univariate(coefficients):
    coefficients = list(map(Fraction, coefficients))
    while coefficients and not coefficients[-1]:
        coefficients.pop()
    if not coefficients:
        raise AssertionError("zero restricted factor")
    denominator = 1
    for value in coefficients:
        denominator = lcm(denominator, value.denominator)
    integer = [int(value * denominator) for value in coefficients]
    divisor = 0
    for value in integer:
        divisor = gcd(divisor, abs(value))
    integer = [value // max(divisor, 1) for value in integer]
    if integer[-1] < 0:
        integer = [-value for value in integer]
    return tuple(integer)


def nonroot_split(polynomial, left, right):
    for numerator, denominator in ((1, 2), (1, 3), (2, 3), (2, 5), (3, 5), (1, 4), (3, 4)):
        middle = left + (right - left) * Fraction(numerator, denominator)
        if sturm.polynomial_value(polynomial, middle):
            return middle
    raise AssertionError("could not choose a rational nonroot split")


def isolate_roots(polynomial):
    total = sturm.root_count(polynomial, Fraction(0), Fraction(1))
    stack = [(Fraction(0), Fraction(1), total)]
    answer = []
    while stack:
        left, right, count = stack.pop()
        if count == 0:
            continue
        if count == 1 and right - left <= ISOLATION_WIDTH:
            answer.append((left, right))
            continue
        middle = nonroot_split(polynomial, left, right)
        left_count = sturm.root_count(polynomial, left, middle)
        right_count = sturm.root_count(polynomial, middle, right)
        if left_count + right_count != count:
            raise AssertionError("Sturm subdivision lost a root")
        stack.append((middle, right, right_count))
        stack.append((left, middle, left_count))
    answer.sort()
    if len(answer) != total:
        raise AssertionError("root isolation census changed")
    return answer


def exact_inputs():
    with np.load(POINT_BANK, allow_pickle=False) as source:
        matrices = np.asarray(source["chart_matrix"], dtype=np.int64)
    if matrices.shape != (178, 4, 8):
        raise AssertionError("row-2599 point bank changed")
    points = tuple(gate.normalized_values(matrix.tolist()) for matrix in matrices)
    with np.load(FACTOR_STATES, allow_pickle=False) as source:
        packed = np.asarray(source["chart_factor_sign_packed"], dtype=np.uint8)
        hamming = np.asarray(source["chart_hamming"], dtype=np.int64)
    states = np.unpackbits(packed, axis=1, bitorder="little")[:, :26_740].astype(np.uint8)
    with np.load(FACTOR_CENSUS, allow_pickle=False) as source:
        multiplicity = np.asarray(source["factor_multiplicity"], dtype=np.int64)
    return matrices, points, packed, states, hamming, multiplicity


def build_record():
    matrices, points, packed, states, hamming, multiplicity = exact_inputs()
    if (SOURCE_CHART, TARGET_CHART) not in safe.EDGES:
        raise AssertionError("selected transition lost its parent-safe edge")
    chart_zero_edges = tuple(edge for edge in safe.EDGES if SOURCE_CHART in edge)
    ranked = sorted(
        (int(hamming[left, right]), left, right)
        for left, right in chart_zero_edges
    )
    if ranked[0] != (1197, SOURCE_CHART, TARGET_CHART):
        raise AssertionError(f"selected transition is no longer the shortest safe chart-zero edge: {ranked[0]}")

    records = [json.loads(line) for line in safe.CATALOG.read_text().splitlines() if line]
    parents, _unused = gate.parent_polynomials(records[2599])
    for edge_label, target, polynomial, _terms in parents:
        restricted = safe.segment_power(
            polynomial,
            points[SOURCE_CHART],
            points[TARGET_CHART],
        )
        if not safe.positive_unit([target * coefficient for coefficient in restricted]):
            raise AssertionError(f"parent-safe transition failed at {edge_label}")

    candidates = gate.parse_candidates()
    _factor_types, _factor_terms, polynomials = labeled.factor_polynomials()
    root_count_census = Counter()
    rooted_factor_ids = set()
    events = []
    for factor_id in candidates:
        polynomial = primitive_univariate(
            safe.segment_power(
                polynomials[factor_id],
                points[SOURCE_CHART],
                points[TARGET_CHART],
            )
        )
        root_count = sturm.root_count(polynomial, Fraction(0), Fraction(1))
        root_count_census[root_count] += 1
        if not root_count:
            continue
        rooted_factor_ids.add(factor_id)
        intervals = isolate_roots(polynomial)
        if len(intervals) != root_count:
            raise AssertionError("isolated root count changed")
        for root_index, (left, right) in enumerate(intervals):
            left_value = sturm.polynomial_value(polynomial, left)
            right_value = sturm.polynomial_value(polynomial, right)
            if not left_value or not right_value:
                raise AssertionError("isolating endpoint is a root")
            sign_flip = (left_value > 0) != (right_value > 0)
            events.append({
                "factor_id": int(factor_id),
                "factor_degree": len(polynomial) - 1,
                "occurrence_multiplicity": int(multiplicity[factor_id]),
                "root_index_within_factor": root_index,
                "isolating_interval": [fraction_text(left), fraction_text(right)],
                "sign_flip": sign_flip,
            })

    events.sort(
        key=lambda row: sum(map(Fraction, row["isolating_interval"])) / 2
    )
    for left, right in zip(events, events[1:]):
        if Fraction(left["isolating_interval"][1]) > Fraction(right["isolating_interval"][0]):
            raise AssertionError("residual event root boxes overlap")
    if root_count_census != Counter({0: 16_607, 1: 1_197, 2: 20}):
        raise AssertionError(f"transition root census changed: {root_count_census}")
    if len(rooted_factor_ids) != 1_217 or len(events) != 1_237:
        raise AssertionError("transition factor/event census changed")
    if not all(event["sign_flip"] for event in events):
        raise AssertionError("a transition event is tangent or multiple")

    event_multiplicity = Counter(event["occurrence_multiplicity"] for event in events)
    if event_multiplicity != Counter({1: 1_179, 2: 13, 15: 6, 65: 39}):
        raise AssertionError(f"event multiplicity census changed: {event_multiplicity}")

    state = states[SOURCE_CHART].copy()
    state_digest = sha256(b"diag3-row2599-transition-0-89-factor-states-v1\0")
    state_digest.update(np.packbits(state, bitorder="little").tobytes())
    for event in events:
        if event["sign_flip"]:
            state[event["factor_id"]] ^= np.uint8(1)
        state_digest.update(np.packbits(state, bitorder="little").tobytes())
    if not np.array_equal(state, states[TARGET_CHART]):
        mismatch = int(np.count_nonzero(state != states[TARGET_CHART]))
        raise AssertionError(f"transition event sequence misses {mismatch} endpoint factor signs")
    if int(hamming[SOURCE_CHART, TARGET_CHART]) != 1_197:
        raise AssertionError("endpoint Hamming distance changed")

    event_digest = sha256(b"diag3-row2599-transition-0-89-events-v1\0")
    for event in events:
        event_digest.update(event["factor_id"].to_bytes(4, "little"))
        event_digest.update(event["factor_degree"].to_bytes(1, "little"))
        event_digest.update(event["occurrence_multiplicity"].to_bytes(2, "little"))
        for endpoint in map(Fraction, event["isolating_interval"]):
            event_digest.update(endpoint.numerator.to_bytes(16, "little", signed=True))
            event_digest.update(endpoint.denominator.to_bytes(16, "little"))

    first_compound_index, first_compound = next(
        (index, event)
        for index, event in enumerate(events)
        if event["occurrence_multiplicity"] > 1
    )
    simple_events = event_multiplicity[1]
    compound_events = len(events) - simple_events
    return {
        "format": FORMAT,
        "status": STATUS,
        "scope": {
            "parent_index": 2599,
            "source_chart": SOURCE_CHART,
            "target_chart": TARGET_CHART,
            "path": "straight segment in the exact normalized (Delta^3)^3 coordinates",
            "parent_parameter_coverage": "COMPLETE_ON_CLOSED_SEGMENT",
            "residual_parameter_coverage": "COMPLETE_ON_OPEN_SEGMENT",
            "signature_label_continuation": "OPEN_AT_COMPOUND_EVENTS",
            "global_parent_cell_coverage": "NOT_CLAIMED",
        },
        "inputs": {
            "point_bank_path": str(POINT_BANK.relative_to(HERE.parents[1])),
            "point_bank_sha256": file_sha256(POINT_BANK),
            "factor_states_path": str(FACTOR_STATES.relative_to(HERE.parents[1])),
            "factor_states_sha256": file_sha256(FACTOR_STATES),
            "factor_census_path": str(FACTOR_CENSUS.relative_to(HERE.parents[1])),
            "factor_census_sha256": file_sha256(FACTOR_CENSUS),
            "candidate_factor_path": str(CANDIDATES.relative_to(HERE.parents[1])),
            "candidate_factor_sha256": file_sha256(CANDIDATES),
        },
        "selection": {
            "parent_safe_chart_zero_edge_count": len(chart_zero_edges),
            "selected_endpoint_factor_hamming_distance": 1_197,
            "selection_rule": "minimum exact factor-state Hamming distance among the 57 certified parent-safe chart-zero segments",
        },
        "parent_residence": {
            "parent_bracket_count": 70,
            "exact_method": "rational segment restriction plus recursive Bernstein positivity",
            "strict_on_closed_segment": True,
            "parent_infinity_cells": [],
        },
        "residual_roadmap": {
            "candidate_factor_count": len(candidates),
            "factor_root_count_census": {str(key): value for key, value in sorted(root_count_census.items())},
            "rooted_factor_count": len(rooted_factor_ids),
            "distinct_ordered_event_count": len(events),
            "event_occurrence_multiplicity_census": {str(key): value for key, value in sorted(event_multiplicity.items())},
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
            "scope_endpoint_cells": ["endpoint_chart_0", "endpoint_chart_89"],
            "parent_infinity_subcomplex": [],
        },
        "label_continuation_frontier": {
            "simple_single-occurrence_events": simple_events,
            "compound_events": compound_events,
            "compound_event_census": {
                str(key): value
                for key, value in sorted(event_multiplicity.items())
                if key > 1
            },
            "first_compound_event_index": first_compound_index,
            "first_compound_event": first_compound,
            "next_exact_question": "Can a local compound-mutation verifier update the 26,112-tope label set across the first multi-occurrence event without full chamber re-enumeration?",
        },
        "theorem_effect": "Connects two stored row-2599 parent germs by a complete exact residual event roadmap; closes neither invariant diagonal-three obligation and leaves 9DVL at 2/9.",
        "verifier": {
            "command": "python ai/omreal/verify_diag3_pair_parent_source_transition.py",
            "hostile_corruptions": 9,
        },
    }
