#!/usr/bin/env python3
"""Exact three-block source bridge from row-2599 chart 0 to chart 152."""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUTPUT = DATA / "DIAG3_PAIR_PARENT_SOURCE_BLOCK_BRIDGE_0_152.json"
SOURCE_CHART = 0
TARGET_CHART = 152
BLOCK_ORDER = (0, 1, 2)
FORMAT = "diag3-pair-parent-source-block-bridge-v1"
STATUS = "EXACT_THREE_BLOCK_SOURCE_BRIDGE"
ISOLATION_WIDTH = Fraction(1, 1 << 28)

sys.path.insert(0, str(HERE))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG9_GRAPH_exact_topes as topes  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402
import diag3_pair_parent_source_labels_core as source_labels  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402
import verify_diag2_canonical_robust_edges as evaluator  # noqa: E402
import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def straight_components():
    adjacency = defaultdict(set)
    for left, right in safe.EDGES:
        adjacency[left].add(right)
        adjacency[right].add(left)
    seen = set()
    components = []
    for vertex in range(178):
        if vertex in seen:
            continue
        stack = [vertex]
        seen.add(vertex)
        component = []
        while stack:
            current = stack.pop()
            component.append(current)
            for neighbor in adjacency[current]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    stack.append(neighbor)
        components.append(tuple(sorted(component)))
    components.sort(key=lambda row: (-len(row), row))
    return adjacency, tuple(components)


def hybrid_vertex(source, target, mask):
    return tuple(
        target[index] if mask & (1 << (index // 3)) else source[index]
        for index in range(9)
    )


def is_parent_interior(values, parents):
    return all(
        target * evaluator.evaluate(polynomial, values) > 0
        for _label, target, polynomial, _terms in parents
    )


def block_path_order(source, target, parents):
    valid = tuple(
        is_parent_interior(hybrid_vertex(source, target, mask), parents)
        for mask in range(8)
    )
    predecessor = {0: None} if valid[0] else {}
    for mask in range(8):
        if mask not in predecessor:
            continue
        for block in range(3):
            next_mask = mask | (1 << block)
            if next_mask != mask and valid[next_mask] and next_mask not in predecessor:
                predecessor[next_mask] = (mask, block)
    if 7 not in predecessor:
        return None, valid
    order = []
    mask = 7
    while mask:
        mask, block = predecessor[mask]
        order.append(block)
    return tuple(reversed(order)), valid


def bridge_vertices(source, target, order):
    mask = 0
    vertices = [hybrid_vertex(source, target, mask)]
    for block in order:
        mask |= 1 << block
        vertices.append(hybrid_vertex(source, target, mask))
    if mask != 7:
        raise AssertionError("block path did not replace every moving column")
    return tuple(vertices)


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
            raise AssertionError("Sturm subdivision lost a bridge root")
        stack.append((middle, right, right_count))
        stack.append((left, middle, left_count))
    answer.sort()
    if len(answer) != total:
        raise AssertionError("bridge root isolation census changed")
    return answer


def source_overlap(matrices, states):
    raw_labels = set(topes.parent_topes(matrices[SOURCE_CHART].tolist()))
    if len(raw_labels) != source_labels.EXPECTED_TOPE_COUNT:
        raise AssertionError("chart-zero raw label count changed")
    factor_payload = np.packbits(states[SOURCE_CHART], bitorder="little").tobytes()
    return {
        "shared_chart": SOURCE_CHART,
        "existing_transition_certificate": str(transition.OUTPUT.relative_to(HERE.parents[1])),
        "existing_transition_certificate_sha256": transition.file_sha256(transition.OUTPUT),
        "existing_label_certificate": str(source_labels.OUTPUT.relative_to(HERE.parents[1])),
        "existing_label_certificate_sha256": source_labels.file_sha256(source_labels.OUTPUT),
        "raw_extension_labels": len(raw_labels),
        "raw_extension_labels_sha256": source_labels.labels_digest(raw_labels),
        "factor_state_sha256": sha256(
            b"diag3-row2599-chart0-factor-state-v1\0" + factor_payload
        ).hexdigest(),
        "compatibility": "EXACT_COMMON_SOURCE_VERTEX_AND_RAW_LABEL_SET",
    }


def build_record(progress=False):
    matrices, points, _packed, states, hamming, multiplicity = transition.exact_inputs()
    records = [json.loads(line) for line in safe.CATALOG.read_text().splitlines() if line]
    parents, _parent_digest = gate.parent_polynomials(records[2599])
    adjacency, components = straight_components()
    component_census = Counter(map(len, components))
    if component_census != Counter({105: 1, 2: 1, 1: 71}):
        raise AssertionError(f"straight transition component census changed: {component_census}")
    if len(safe.EDGES) != 105 or len(adjacency[TARGET_CHART]) != 0:
        raise AssertionError("target chart is no longer straight-isolated")

    straight_isolates = tuple(vertex for vertex in range(178) if not adjacency[vertex])
    direct_candidates = []
    for target_chart in straight_isolates:
        order, valid = block_path_order(points[SOURCE_CHART], points[target_chart], parents)
        if order is None:
            continue
        direct_candidates.append({
            "target_chart": target_chart,
            "block_order": list(order),
            "parent_interior_cube_vertices": sum(valid),
            "endpoint_factor_hamming_distance": int(hamming[SOURCE_CHART, target_chart]),
        })
    direct_candidates.sort(
        key=lambda row: (
            len(row["block_order"]),
            row["endpoint_factor_hamming_distance"],
            row["target_chart"],
        )
    )
    expected_candidates = [
        (152, (0, 1, 2), 3384),
        (133, (0, 2, 1), 3536),
        (149, (0, 1, 2), 3634),
        (166, (1, 0, 2), 3866),
        (154, (0, 1, 2), 4166),
        (153, (0, 1, 2), 4378),
    ]
    actual_candidates = [
        (row["target_chart"], tuple(row["block_order"]), row["endpoint_factor_hamming_distance"])
        for row in direct_candidates
    ]
    if actual_candidates != expected_candidates:
        raise AssertionError(f"direct block-bridge candidates changed: {actual_candidates}")
    selected = direct_candidates[0]
    if selected["target_chart"] != TARGET_CHART or tuple(selected["block_order"]) != BLOCK_ORDER:
        raise AssertionError("objective block-bridge selection changed")

    vertices = bridge_vertices(points[SOURCE_CHART], points[TARGET_CHART], BLOCK_ORDER)
    vertex_rows = []
    for index, values in enumerate(vertices):
        evaluations = [
            target * evaluator.evaluate(polynomial, values)
            for _label, target, polynomial, _terms in parents
        ]
        if min(evaluations) <= 0:
            raise AssertionError("bridge waypoint left the strict parent cell")
        vertex_rows.append({
            "vertex_index": index,
            "replaced_column_blocks": list(BLOCK_ORDER[:index]),
            "minimum_signed_parent_bracket": fraction_text(min(evaluations)),
        })

    segment_rows = []
    for segment_index, (left, right) in enumerate(zip(vertices, vertices[1:])):
        active_block = BLOCK_ORDER[segment_index]
        for label, target, polynomial, _terms in parents:
            restricted = safe.segment_power(polynomial, left, right)
            if len(restricted) > 2:
                raise AssertionError(f"parent bracket {label} is nonlinear in one moving column")
            if not safe.positive_unit([target * coefficient for coefficient in restricted]):
                raise AssertionError(f"parent bracket {label} failed on bridge segment {segment_index}")
        segment_rows.append({
            "segment_index": segment_index,
            "active_column": 6 + active_block,
            "parent_brackets_strict": len(parents),
            "parent_restriction_degree_ceiling": 1,
        })

    candidates = gate.parse_candidates()
    _factor_types, _factor_terms, polynomials = labeled.factor_polynomials()
    waypoint_zero_census = []
    for values in vertices:
        zeros = [
            factor_id
            for factor_id in candidates
            if evaluator.evaluate(polynomials[factor_id], values) == 0
        ]
        waypoint_zero_census.append(len(zeros))
    if waypoint_zero_census != [0, 0, 0, 0]:
        raise AssertionError(f"bridge waypoint acquired a residual wall: {waypoint_zero_census}")

    events = []
    root_census_by_segment = []
    for segment_index, (left, right) in enumerate(zip(vertices, vertices[1:])):
        root_census = Counter()
        segment_events = []
        for candidate_index, factor_id in enumerate(candidates):
            polynomial = transition.primitive_univariate(
                safe.segment_power(polynomials[factor_id], left, right)
            )
            root_count = sturm.root_count(polynomial, Fraction(0), Fraction(1))
            root_census[root_count] += 1
            if not root_count:
                continue
            intervals = isolate_roots(polynomial)
            if len(intervals) != root_count:
                raise AssertionError("bridge isolated-root count changed")
            for root_index, (root_left, root_right) in enumerate(intervals):
                left_value = sturm.polynomial_value(polynomial, root_left)
                right_value = sturm.polynomial_value(polynomial, root_right)
                if not left_value or not right_value:
                    raise AssertionError("bridge isolating endpoint is a root")
                segment_events.append({
                    "segment_index": segment_index,
                    "factor_id": int(factor_id),
                    "factor_degree": len(polynomial) - 1,
                    "occurrence_multiplicity": int(multiplicity[factor_id]),
                    "root_index_within_factor": root_index,
                    "isolating_interval": [fraction_text(root_left), fraction_text(root_right)],
                    "sign_flip": (left_value > 0) != (right_value > 0),
                })
            if progress and (candidate_index + 1) % 4000 == 0:
                print(
                    f"segment {segment_index}: screened {candidate_index + 1}/{len(candidates)} factors",
                    flush=True,
                )
        segment_events.sort(
            key=lambda row: sum(map(Fraction, row["isolating_interval"])) / 2
        )
        for first, second in zip(segment_events, segment_events[1:]):
            if Fraction(first["isolating_interval"][1]) > Fraction(second["isolating_interval"][0]):
                raise AssertionError(
                    f"bridge event boxes overlap on segment {segment_index}: "
                    f"{first['factor_id']} and {second['factor_id']}"
                )
        if not all(event["sign_flip"] for event in segment_events):
            raise AssertionError("bridge acquired a tangent or multiple residual event")
        events.extend(segment_events)
        root_census_by_segment.append({str(key): value for key, value in sorted(root_census.items())})
        if progress:
            print(
                f"segment {segment_index}: {len(segment_events)} ordered events; roots={dict(sorted(root_census.items()))}",
                flush=True,
            )

    expected_root_census = [
        {"0": 15059, "1": 2756, "2": 9},
        {"0": 16808, "1": 1015, "2": 1},
        {"0": 16008, "1": 1811, "2": 5},
    ]
    if root_census_by_segment != expected_root_census or len(events) != 5612:
        raise AssertionError((root_census_by_segment, len(events)))

    event_multiplicity = Counter(event["occurrence_multiplicity"] for event in events)
    state = states[SOURCE_CHART].copy()
    state_digest = sha256(b"diag3-row2599-block-bridge-0-152-factor-states-v1\0")
    state_digest.update(np.packbits(state, bitorder="little").tobytes())
    segment_state_digests = []
    event_offset = 0
    for segment_index, root_census in enumerate(root_census_by_segment):
        segment_event_count = sum(int(key) * value for key, value in root_census.items())
        for event in events[event_offset : event_offset + segment_event_count]:
            state[event["factor_id"]] ^= np.uint8(1)
            state_digest.update(np.packbits(state, bitorder="little").tobytes())
        event_offset += segment_event_count
        segment_state_digests.append(
            sha256(
                b"diag3-row2599-block-bridge-segment-state-v1\0"
                + np.packbits(state, bitorder="little").tobytes()
            ).hexdigest()
        )
    if event_offset != len(events) or not np.array_equal(state, states[TARGET_CHART]):
        mismatch = int(np.count_nonzero(state != states[TARGET_CHART]))
        raise AssertionError(f"bridge event sequence misses {mismatch} target factor signs")
    if int(hamming[SOURCE_CHART, TARGET_CHART]) != 3384:
        raise AssertionError("bridge endpoint Hamming distance changed")

    event_digest = sha256(b"diag3-row2599-block-bridge-0-152-events-v1\0")
    for event in events:
        event_digest.update(event["segment_index"].to_bytes(1, "little"))
        event_digest.update(event["factor_id"].to_bytes(4, "little"))
        event_digest.update(event["factor_degree"].to_bytes(1, "little"))
        event_digest.update(event["occurrence_multiplicity"].to_bytes(2, "little"))
        for endpoint in map(Fraction, event["isolating_interval"]):
            event_digest.update(endpoint.numerator.to_bytes(16, "little", signed=True))
            event_digest.update(endpoint.denominator.to_bytes(16, "little"))

    zero_cells = len(events) + len(vertices)
    one_cells = len(events) + len(vertices) - 1
    return {
        "format": FORMAT,
        "status": STATUS,
        "scope": {
            "parent_index": 2599,
            "source_chart": SOURCE_CHART,
            "target_chart": TARGET_CHART,
            "path": "three exact one-column block segments in normalized (Delta^3)^3 coordinates",
            "parent_parameter_coverage": "COMPLETE_ON_CLOSED_PIECEWISE_LINEAR_PATH",
            "residual_parameter_coverage": "COMPLETE_ON_OPEN_SEGMENTS_AND_GENERIC_WAYPOINTS",
            "signature_label_continuation": "OPEN_BEYOND_SHARED_CHART_ZERO_VERTEX",
            "global_parent_cell_coverage": "NOT_CLAIMED",
        },
        "inputs": {
            "point_bank_path": str(transition.POINT_BANK.relative_to(HERE.parents[1])),
            "point_bank_sha256": transition.file_sha256(transition.POINT_BANK),
            "factor_states_path": str(transition.FACTOR_STATES.relative_to(HERE.parents[1])),
            "factor_states_sha256": transition.file_sha256(transition.FACTOR_STATES),
            "factor_census_path": str(transition.FACTOR_CENSUS.relative_to(HERE.parents[1])),
            "factor_census_sha256": transition.file_sha256(transition.FACTOR_CENSUS),
            "candidate_factor_path": str(transition.CANDIDATES.relative_to(HERE.parents[1])),
            "candidate_factor_sha256": transition.file_sha256(transition.CANDIDATES),
        },
        "straight_transition_audit": {
            "stored_germs": 178,
            "certified_straight_edges": len(safe.EDGES),
            "component_size_census": {str(key): value for key, value in sorted(component_census.items())},
            "straight_isolated_germs": len(straight_isolates),
            "target_was_straight_isolated": True,
        },
        "selection": {
            "direct_chart_zero_block_bridge_candidates": direct_candidates,
            "selection_rule": "minimum certified one-column segment count, then minimum endpoint factor-state Hamming distance, then target chart index",
            "minimum_segment_count": len(BLOCK_ORDER),
            "selected_endpoint_factor_hamming_distance": 3384,
            "selected_block_order": list(BLOCK_ORDER),
        },
        "parent_residence": {
            "parent_bracket_count": len(parents),
            "strict_generic_waypoints": len(vertices),
            "waypoints": vertex_rows,
            "segments": segment_rows,
            "exact_method": "one-column multilinearity plus exact rational endpoint signs, independently replayed by segment Bernstein positivity",
            "parent_infinity_cells": [],
        },
        "overlap_with_labelled_0_89_path": source_overlap(matrices, states),
        "residual_roadmap": {
            "candidate_factor_count": len(candidates),
            "segment_factor_root_count_census": root_census_by_segment,
            "ordered_root_events": len(events),
            "event_occurrence_multiplicity_census": {
                str(key): value for key, value in sorted(event_multiplicity.items())
            },
            "isolation_width_ceiling": fraction_text(ISOLATION_WIDTH),
            "all_root_boxes_pairwise_ordered_within_segments": True,
            "all_roots_simple_sign_crossings": True,
            "generic_waypoint_zero_factor_census": waypoint_zero_census,
            "events_semantic_sha256": event_digest.hexdigest(),
            "factor_state_sequence_sha256": state_digest.hexdigest(),
            "segment_terminal_state_sha256": segment_state_digests,
            "target_factor_state_reconstructed": True,
            "events": events,
        },
        "regular_cw_path": {
            "zero_cells": zero_cells,
            "one_cells": one_cells,
            "total_cells": zero_cells + one_cells,
            "strict_closure_pairs": 2 * one_cells,
            "scope_endpoint_cells": ["endpoint_chart_0", "endpoint_chart_152"],
            "generic_internal_waypoints": ["after_column_6", "after_column_7"],
            "parent_infinity_subcomplex": [],
        },
        "theorem_effect": "Embeds one previously straight-isolated row-2599 germ into the exact source-transition skeleton and glues it at the labelled chart-zero vertex; closes neither invariant diagonal-three obligation and leaves 9DVL at 2/9.",
        "next_exact_question": "Continue all 26,112 labels across the 5,612 bridge events, then extend the source complex to genuine parent-boundary faces; the finite germ graph is not parameter-space coverage.",
        "verifier": {
            "command": "python ai/omreal/verify_diag3_pair_parent_source_block_bridge.py",
            "hostile_corruptions": 12,
        },
    }
