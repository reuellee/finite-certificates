#!/usr/bin/env python3
"""Exact discovery probe for extension-feasibility alternation on four paths.

This is deliberately a prospecting script: it reconstructs the labelled
row-2599 paths from their exact sources, identifies the signatures with the
largest number of membership changes, and writes exact per-path records.
It does not claim parameter-space coverage or a 9DVL theorem.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
import json
import multiprocessing
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
OMREAL = HERE.parent / "omreal"
DATA = OMREAL / "data"
OUTPUT_DIR = HERE / "data"
FULL_MASK = (1 << 56) - 1

sys.path.insert(0, str(OMREAL))
import DIAG9_GRAPH_exact_topes as topes  # noqa: E402
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402
import diag3_pair_parent_source_block_bridge_core as block_bridge  # noqa: E402
import diag3_pair_parent_source_block_labels_core as block_labels  # noqa: E402
import diag3_pair_parent_source_labels_core as source_labels  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402
import verify_diag2_canonical_robust_edges as evaluator  # noqa: E402
import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


def digest(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def factor_occurrences(events):
    with np.load(transition.FACTOR_CENSUS, allow_pickle=False) as source:
        occurrence_factor = np.asarray(source["occurrence_factor"], dtype=np.uint32)
        occurrence_fourset = np.asarray(source["occurrence_fourset"], dtype=np.uint8)
    return {
        factor_id: tuple(
            tuple(map(int, row))
            for row in occurrence_fourset[np.flatnonzero(occurrence_factor == factor_id)]
        )
        for factor_id in {int(event["factor_id"]) for event in events}
    }


def update_counts(before, after, event_index, counts, histories):
    changed = before ^ after
    for signature in changed:
        counts[signature] += 1
        histories[signature].append(event_index)
    return len(changed)


def summarize(
    path_id,
    universe,
    initial,
    final,
    counts,
    histories,
    event_deltas,
    segments,
    expected_spectrum=None,
):
    spectrum = Counter(counts.get(signature, 0) for signature in universe)
    if expected_spectrum is not None and spectrum != Counter(expected_spectrum):
        raise AssertionError(
            f"{path_id}: committed transition spectrum was not recovered: {spectrum}"
        )
    maximum = max(spectrum)
    maximizers = sorted(signature for signature in universe if counts.get(signature, 0) == maximum)
    odd = {signature for signature in universe if counts.get(signature, 0) & 1}
    endpoint_difference = initial ^ final
    if odd != endpoint_difference:
        raise AssertionError(f"{path_id}: endpoint parity identity failed")
    if sum(level * amount for level, amount in spectrum.items()) != sum(event_deltas):
        raise AssertionError(f"{path_id}: transition-mass identity failed")
    complement_closed = all((signature ^ FULL_MASK) in maximizers for signature in maximizers)
    return {
        "path_id": path_id,
        "segments": segments,
        "signature_universe": len(universe),
        "events": len(event_deltas),
        "transition_mass": sum(event_deltas),
        "endpoint_symmetric_difference": len(endpoint_difference),
        "transition_spectrum": {str(key): value for key, value in sorted(spectrum.items())},
        "maximum_alternation": maximum,
        "maximizer_count": len(maximizers),
        "maximizers": [
            {
                "signature": signature,
                "hex": f"{signature:014x}",
                "antipode": signature ^ FULL_MASK,
                "event_indices": histories[signature],
            }
            for signature in maximizers
        ],
        "maximizers_antipode_closed": complement_closed,
        "identities": {
            "transition_mass_equals_sum_of_event_symmetric_differences": True,
            "odd_alternation_signatures_equal_endpoint_symmetric_difference": True,
        },
    }


def source_path(progress=False):
    roadmap = json.loads(source_labels.TRANSITION.read_text(encoding="utf-8"))
    events = roadmap["residual_roadmap"]["events"]
    matrices, points, _packed, _states, _hamming, _multiplicity = transition.exact_inputs()
    normalized_zero = source_labels.segment_parent(points, Fraction(0))
    raw_zero = matrices[transition.SOURCE_CHART].tolist()
    reorientation = source_labels.solve_reorientation_mask(
        topes.parent_signs(normalized_zero), topes.parent_signs(raw_zero)
    )
    labels = {
        signature ^ reorientation
        for signature in topes.parent_topes(normalized_zero)
    }
    initial = set(labels)
    occurrences = factor_occurrences(events)
    universe = source_labels.raw_extension_universe()
    counts = Counter()
    histories = defaultdict(list)
    event_deltas = []

    for event_index, event in enumerate(events):
        factor_id = int(event["factor_id"])
        before = labels
        if int(event["occurrence_multiplicity"]) == 1:
            labels, _preliminary = source_labels.simple_mutation(
                labels, occurrences[factor_id][0]
            )
        else:
            right = Fraction(event["isolating_interval"][1])
            next_left = (
                Fraction(events[event_index + 1]["isolating_interval"][0])
                if event_index + 1 < len(events)
                else Fraction(1)
            )
            normalized = set(
                topes.parent_topes(source_labels.segment_parent(points, (right + next_left) / 2))
            )
            labels = {signature ^ reorientation for signature in normalized}
        event_deltas.append(
            update_counts(before, labels, event_index, counts, histories)
        )
        if progress and ((event_index + 1) % 250 == 0 or event_deltas[-1] > 4):
            print(f"source {event_index + 1}/{len(events)}", flush=True)

    expected_final = set(topes.parent_topes(matrices[transition.TARGET_CHART].tolist()))
    if labels != expected_final:
        raise AssertionError("source path endpoint mismatch")
    return summarize(
        "row2599-chart-0-to-89",
        universe,
        initial,
        labels,
        counts,
        histories,
        event_deltas,
        segments=1,
        expected_spectrum={0: 87_208, 1: 9_490, 2: 512, 3: 14},
    )


def _compound_topes(parent):
    return set(topes.parent_topes(parent))


def block_path(progress=False, workers=None):
    roadmap = json.loads(block_labels.BRIDGE.read_text(encoding="utf-8"))
    events = roadmap["residual_roadmap"]["events"]
    matrices, points, _packed, _states, _hamming, _multiplicity = transition.exact_inputs()
    vertices = block_bridge.bridge_vertices(
        points[block_bridge.SOURCE_CHART],
        points[block_bridge.TARGET_CHART],
        block_bridge.BLOCK_ORDER,
    )
    grouped = block_labels.event_groups(events, len(vertices) - 1)
    compound_parents = block_labels.compound_tasks(vertices, grouped)
    process_count = workers or max(1, min(6, multiprocessing.cpu_count()))
    pool = multiprocessing.get_context("fork").Pool(process_count)
    compound_results = pool.imap(_compound_topes, compound_parents, chunksize=1)

    normalized_zero = block_labels.segment_parent(vertices, 0, Fraction(0))
    raw_zero = matrices[block_bridge.SOURCE_CHART].tolist()
    reorientation = source_labels.solve_reorientation_mask(
        topes.parent_signs(normalized_zero), topes.parent_signs(raw_zero)
    )
    labels = {
        signature ^ reorientation
        for signature in topes.parent_topes(normalized_zero)
    }
    initial = set(labels)
    occurrences = factor_occurrences(events)
    universe = source_labels.raw_extension_universe()
    counts = Counter()
    histories = defaultdict(list)
    event_deltas = []
    global_event_index = 0

    try:
        for segment_index, segment_events in enumerate(grouped):
            for event in segment_events:
                factor_id = int(event["factor_id"])
                before = labels
                if int(event["occurrence_multiplicity"]) == 1:
                    labels, _preliminary = source_labels.simple_mutation(
                        labels, occurrences[factor_id][0]
                    )
                else:
                    normalized = next(compound_results)
                    labels = {signature ^ reorientation for signature in normalized}
                event_deltas.append(
                    update_counts(
                        before,
                        labels,
                        global_event_index,
                        counts,
                        histories,
                    )
                )
                global_event_index += 1
                if progress and (
                    global_event_index % 500 == 0 or event_deltas[-1] > 4
                ):
                    print(f"block {global_event_index}/{len(events)}", flush=True)
            endpoint = {
                signature ^ reorientation
                for signature in topes.parent_topes(
                    block_labels.segment_parent(vertices, segment_index, Fraction(1))
                )
            }
            if labels != endpoint:
                raise AssertionError(f"block segment {segment_index} endpoint mismatch")
    except BaseException:
        pool.terminate()
        pool.join()
        raise
    else:
        pool.close()
        pool.join()

    expected_final = set(topes.parent_topes(matrices[block_bridge.TARGET_CHART].tolist()))
    if labels != expected_final:
        raise AssertionError("block path endpoint mismatch")
    return summarize(
        "row2599-chart-0-to-152-three-block",
        universe,
        initial,
        labels,
        counts,
        histories,
        event_deltas,
        segments=len(grouped),
        expected_spectrum={
            0: 62_080,
            1: 23_496,
            2: 9_914,
            3: 1_486,
            4: 234,
            5: 14,
        },
    )


def generated_block_events(vertices, multiplicity, progress=False):
    records = [json.loads(line) for line in safe.CATALOG.read_text().splitlines() if line]
    parents, _parent_digest = gate.parent_polynomials(records[2599])
    if not all(block_bridge.is_parent_interior(vertex, parents) for vertex in vertices):
        raise AssertionError("alternative block path left the strict parent cell")
    candidates = gate.parse_candidates()
    _factor_types, _factor_terms, polynomials = labeled.factor_polynomials()
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
            for root_index, (root_left, root_right) in enumerate(
                block_bridge.isolate_roots(polynomial)
            ):
                left_value = sturm.polynomial_value(polynomial, root_left)
                right_value = sturm.polynomial_value(polynomial, root_right)
                if not left_value or not right_value or (left_value > 0) == (right_value > 0):
                    raise AssertionError("alternative block event is not a strict sign crossing")
                segment_events.append({
                    "segment_index": segment_index,
                    "factor_id": int(factor_id),
                    "factor_degree": len(polynomial) - 1,
                    "occurrence_multiplicity": int(multiplicity[factor_id]),
                    "root_index_within_factor": root_index,
                    "isolating_interval": [
                        block_bridge.fraction_text(root_left),
                        block_bridge.fraction_text(root_right),
                    ],
                })
            if progress and (candidate_index + 1) % 4000 == 0:
                print(
                    f"generated segment {segment_index}: {candidate_index + 1}/{len(candidates)}",
                    flush=True,
                )
        segment_events.sort(
            key=lambda row: sum(map(Fraction, row["isolating_interval"])) / 2
        )
        for first, second in zip(segment_events, segment_events[1:]):
            if Fraction(first["isolating_interval"][1]) > Fraction(second["isolating_interval"][0]):
                raise AssertionError("alternative block event boxes overlap")
        events.extend(segment_events)
        root_census_by_segment.append(
            {str(key): value for key, value in sorted(root_census.items())}
        )
        if progress:
            print(f"generated segment {segment_index}: {len(segment_events)} events", flush=True)
    return events, root_census_by_segment


def alternative_block_path(order, progress=False, workers=None):
    matrices, points, _packed, states, _hamming, multiplicity = transition.exact_inputs()
    vertices = block_bridge.bridge_vertices(
        points[block_bridge.SOURCE_CHART], points[block_bridge.TARGET_CHART], order
    )
    events, root_census = generated_block_events(vertices, multiplicity, progress=progress)
    state = states[block_bridge.SOURCE_CHART].copy()
    for event in events:
        state[event["factor_id"]] ^= np.uint8(1)
    if not np.array_equal(state, states[block_bridge.TARGET_CHART]):
        raise AssertionError("alternative block events miss the target factor state")

    grouped = block_labels.event_groups(events, len(vertices) - 1)
    compound_parents = block_labels.compound_tasks(vertices, grouped)
    process_count = workers or max(1, min(6, multiprocessing.cpu_count()))
    pool = multiprocessing.get_context("fork").Pool(process_count)
    compound_results = pool.imap(_compound_topes, compound_parents, chunksize=1)
    normalized_zero = block_labels.segment_parent(vertices, 0, Fraction(0))
    raw_zero = matrices[block_bridge.SOURCE_CHART].tolist()
    reorientation = source_labels.solve_reorientation_mask(
        topes.parent_signs(normalized_zero), topes.parent_signs(raw_zero)
    )
    labels = {
        signature ^ reorientation
        for signature in topes.parent_topes(normalized_zero)
    }
    initial = set(labels)
    occurrences = factor_occurrences(events)
    universe = source_labels.raw_extension_universe()
    counts = Counter()
    histories = defaultdict(list)
    event_deltas = []
    global_event_index = 0
    try:
        for segment_index, segment_events in enumerate(grouped):
            for event in segment_events:
                factor_id = int(event["factor_id"])
                before = labels
                if int(event["occurrence_multiplicity"]) == 1:
                    labels, _preliminary = source_labels.simple_mutation(
                        labels, occurrences[factor_id][0]
                    )
                else:
                    normalized = next(compound_results)
                    labels = {signature ^ reorientation for signature in normalized}
                event_deltas.append(
                    update_counts(before, labels, global_event_index, counts, histories)
                )
                global_event_index += 1
                if progress and (
                    global_event_index % 500 == 0 or event_deltas[-1] > 4
                ):
                    print(
                        f"order {''.join(map(str, order))} labels "
                        f"{global_event_index}/{len(events)}",
                        flush=True,
                    )
            endpoint = {
                signature ^ reorientation
                for signature in topes.parent_topes(
                    block_labels.segment_parent(vertices, segment_index, Fraction(1))
                )
            }
            if labels != endpoint:
                raise AssertionError(f"alternative segment {segment_index} endpoint mismatch")
    except BaseException:
        pool.terminate()
        pool.join()
        raise
    else:
        pool.close()
        pool.join()
    expected_final = set(topes.parent_topes(matrices[block_bridge.TARGET_CHART].tolist()))
    if labels != expected_final:
        raise AssertionError("alternative block path endpoint mismatch")
    result = summarize(
        f"row2599-chart-0-to-152-order-{''.join(map(str, order))}",
        universe,
        initial,
        labels,
        counts,
        histories,
        event_deltas,
        segments=len(grouped),
    )
    result["block_order"] = list(order)
    result["segment_event_census"] = list(map(len, grouped))
    result["segment_factor_root_count_census"] = root_census
    result["compound_event_count"] = sum(
        int(event["occurrence_multiplicity"]) != 1 for event in events
    )
    result["events_sha256"] = digest(events)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path", choices=("source", "block", "order-021", "order-102"))
    parser.add_argument("--workers", type=int, default=None)
    parser.add_argument("--progress", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()

    if args.path == "source":
        record = source_path(progress=args.progress)
    elif args.path == "block":
        record = block_path(progress=args.progress, workers=args.workers)
    else:
        order = tuple(map(int, args.path.removeprefix("order-").strip()))
        record = alternative_block_path(
            order, progress=args.progress, workers=args.workers
        )
    record["semantic_sha256"] = digest(record)
    output_name = args.path.upper().replace("-", "_")
    output = args.output or OUTPUT_DIR / f"EXTENSION_PATH_ALTERNATION_{output_name}.json"
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: value for key, value in record.items() if key != "maximizers"}, indent=2))
    print("OUTPUT", output)


if __name__ == "__main__":
    main()
