#!/usr/bin/env python3
"""Execute the preregistered two-phase MP-002 block-route transfer test."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
import json
import multiprocessing
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OMREAL = HERE.parent / "omreal"
DATA = HERE / "data"
REGISTRATION = DATA / "MP002_BLOCK_ROUTE_TRANSFER_REGISTRATION.json"
PREDICTION = DATA / "MP002_BLOCK_ROUTE_TRANSFER_PREDICTION.json"
REGISTRATION_COMMIT = "c818dd8415ffa3c1286f2d3200f93276f10ce98b"
REGISTRATION_SHA256 = "54ec6c3f549e4102fac7ccf4ba69d4c4a0572d5dd77c0fe628bcf3003f670e62"
WORKER_CEILING = 6

sys.path.insert(0, str(OMREAL))
sys.path.insert(0, str(HERE))

import DIAG9_GRAPH_exact_topes as topes  # noqa: E402
import diag3_pair_parent_source_block_bridge_core as bridge  # noqa: E402
import diag3_pair_parent_source_block_labels_core as block_labels  # noqa: E402
import diag3_pair_parent_source_labels_core as source_labels  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402
import explore_extension_path_alternation as mp1  # noqa: E402
import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


def file_sha256(path):
    import hashlib

    value = hashlib.sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def order_text(order):
    return "".join(map(str, order))


def strict_parent_data():
    records = [
        json.loads(line) for line in safe.CATALOG.read_text().splitlines() if line
    ]
    return gate.parent_polynomials(records[2599])[0]


def parent_interior(vertex, parents):
    return all(
        target * bridge.evaluator.evaluate(polynomial, vertex) > Fraction(0)
        for _label, target, polynomial, _terms in parents
    )


def selection_frontier(points, states):
    from itertools import permutations

    parents = strict_parent_data()
    rows = []
    for target in range(len(points)):
        if target in (0, 89, 152):
            continue
        valid = []
        for order in permutations(range(3)):
            vertices = bridge.bridge_vertices(points[0], points[target], order)
            if all(parent_interior(vertex, parents) for vertex in vertices):
                valid.append(order_text(order))
        if len(valid) >= 2:
            rows.append(
                [
                    int(np.count_nonzero(states[0] != states[target])),
                    target,
                    valid,
                ]
            )
    rows.sort()
    return rows


def verify_registration(registration, points, states):
    require(file_sha256(REGISTRATION) == REGISTRATION_SHA256, "registration changed")
    require(
        registration["status"] == "REGISTERED_BEFORE_HOLDOUT_OBSERVATION",
        "registration status",
    )
    for row in registration["pinned_inputs"]:
        require(file_sha256(REPO / row["path"]) == row["sha256"], f"input changed: {row['path']}")
    frontier = selection_frontier(points, states)
    selected = registration["object_selection"]
    require(frontier == selected["eligible_endpoint_frontier"], "selection frontier changed")
    require(mp1.digest(frontier) == selected["eligible_endpoint_frontier_sha256"], "frontier digest")
    require(frontier[0][1] == selected["selected_target_chart"] == 66, "selected target")
    require(frontier[0][0] == selected["selected_endpoint_hamming_distance"] == 1812, "selected distance")
    require(frontier[0][2] == selected["registered_valid_orders"], "registered orders")


def event_summary(order, points, states, multiplicity, progress=False):
    registration = json.loads(REGISTRATION.read_text())
    target = registration["object_selection"]["selected_target_chart"]
    vertices = bridge.bridge_vertices(points[0], points[target], order)
    events, root_census = mp1.generated_block_events(
        vertices, multiplicity, progress=progress
    )
    state = states[0].copy()
    for event in events:
        state[event["factor_id"]] ^= np.uint8(1)
    require(np.array_equal(state, states[target]), "factor-state endpoint mismatch")
    grouped = block_labels.event_groups(events, len(vertices) - 1)
    return events, vertices, grouped, {
        "order": order_text(order),
        "events": len(events),
        "segment_event_census": list(map(len, grouped)),
        "compound_event_count": sum(
            int(event["occurrence_multiplicity"]) != 1 for event in events
        ),
        "segment_factor_root_count_census": root_census,
        "events_sha256": mp1.digest(events),
    }


def phase_a(progress=False):
    registration = json.loads(REGISTRATION.read_text())
    matrices, points, _packed, states, _hamming, multiplicity = transition.exact_inputs()
    require(len(matrices) == len(points) == len(states) == 178, "chart bank changed")
    verify_registration(registration, points, states)
    summaries = []
    total_events = 0
    for text in registration["object_selection"]["registered_valid_orders"]:
        order = tuple(map(int, text))
        _events, _vertices, _grouped, summary = event_summary(
            order, points, states, multiplicity, progress=progress
        )
        require(
            summary["events"]
            <= registration["resource_contract"]["maximum_events_per_route"],
            "per-route event ceiling",
        )
        total_events += summary["events"]
        summaries.append(summary)
        print("PHASE_A", text, summary["events"], flush=True)
    require(
        total_events <= registration["resource_contract"]["maximum_total_events"],
        "total event ceiling",
    )
    predicted = min(summaries, key=lambda row: (row["events"], row["order"]))
    record = {
        "format": "mp002-block-route-transfer-prediction-v1",
        "expedition_id": "MP-002",
        "status": "PREDICTION_FROZEN_PRE_LABEL_CONTINUATION",
        "registration_git_commit": REGISTRATION_COMMIT,
        "registration_sha256": REGISTRATION_SHA256,
        "target_chart": 66,
        "event_summaries": summaries,
        "total_events": total_events,
        "prediction_rule": registration["prediction_protocol"]["predictor"],
        "predicted_order": predicted["order"],
        "holdout_alternation_observed": False,
        "semantic_sha256": None,
    }
    semantic = dict(record)
    semantic.pop("semantic_sha256")
    record["semantic_sha256"] = mp1.digest(semantic)
    PREDICTION.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    print("PREDICTED", predicted["order"], "EVENTS", predicted["events"])
    print("OUTPUT", PREDICTION)


def continue_labels(
    order,
    matrices,
    points,
    states,
    multiplicity,
    expected_summary,
    workers=None,
    progress=False,
):
    events, vertices, grouped, summary = event_summary(
        order, points, states, multiplicity, progress=progress
    )
    require(summary == expected_summary, "phase-a event summary changed")
    compound_parents = block_labels.compound_tasks(vertices, grouped)
    process_count = (
        max(1, min(6, multiprocessing.cpu_count()))
        if workers is None
        else workers
    )
    require(
        1 <= process_count <= WORKER_CEILING,
        "worker ceiling",
    )
    pool = multiprocessing.get_context("fork").Pool(process_count)
    compound_results = pool.imap(mp1._compound_topes, compound_parents, chunksize=1)

    target = 66
    normalized_zero = block_labels.segment_parent(vertices, 0, Fraction(0))
    raw_zero = matrices[0].tolist()
    reorientation = source_labels.solve_reorientation_mask(
        topes.parent_signs(normalized_zero), topes.parent_signs(raw_zero)
    )
    labels = {
        signature ^ reorientation
        for signature in topes.parent_topes(normalized_zero)
    }
    initial = set(labels)
    occurrences = mp1.factor_occurrences(events)
    universe = source_labels.raw_extension_universe()
    counts = Counter()
    histories = defaultdict(list)
    event_deltas = []
    event_index = 0
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
                    labels = {
                        signature ^ reorientation for signature in normalized
                    }
                event_deltas.append(
                    mp1.update_counts(
                        before, labels, event_index, counts, histories
                    )
                )
                event_index += 1
                if progress and (
                    event_index % 500 == 0 or event_deltas[-1] > 4
                ):
                    print(
                        "PHASE_B",
                        order_text(order),
                        event_index,
                        "/",
                        len(events),
                        flush=True,
                    )
            expected_endpoint = {
                signature ^ reorientation
                for signature in topes.parent_topes(
                    block_labels.segment_parent(
                        vertices, segment_index, Fraction(1)
                    )
                )
            }
            require(labels == expected_endpoint, "segment endpoint mismatch")
    except BaseException:
        pool.terminate()
        pool.join()
        raise
    else:
        pool.close()
        pool.join()

    expected_final = set(topes.parent_topes(matrices[target].tolist()))
    require(labels == expected_final, "target endpoint mismatch")
    result = mp1.summarize(
        f"row2599-chart-0-to-{target}-order-{order_text(order)}",
        universe,
        initial,
        labels,
        counts,
        histories,
        event_deltas,
        segments=len(grouped),
    )
    result["block_order"] = list(order)
    result["phase_a_event_summary"] = summary
    result["prediction_semantic_sha256"] = json.loads(
        PREDICTION.read_text()
    )["semantic_sha256"]
    result["semantic_sha256"] = mp1.digest(result)
    return result


def phase_b(order, workers=None, progress=False):
    registration = json.loads(REGISTRATION.read_text())
    prediction = json.loads(PREDICTION.read_text())
    require(
        prediction["status"] == "PREDICTION_FROZEN_PRE_LABEL_CONTINUATION",
        "prediction was not frozen",
    )
    require(
        prediction["registration_git_commit"] == REGISTRATION_COMMIT
        and prediction["registration_sha256"] == REGISTRATION_SHA256,
        "prediction registration link",
    )
    require(prediction["holdout_alternation_observed"] is False, "holdout leak")
    require(
        order_text(order)
        in registration["object_selection"]["registered_valid_orders"],
        "unregistered order",
    )
    expected = {
        row["order"]: row for row in prediction["event_summaries"]
    }[order_text(order)]
    matrices, points, _packed, states, _hamming, multiplicity = transition.exact_inputs()
    result = continue_labels(
        order,
        matrices,
        points,
        states,
        multiplicity,
        expected,
        workers=workers,
        progress=progress,
    )
    output = DATA / f"MP002_BLOCK_ROUTE_TRANSFER_ORDER_{order_text(order)}.json"
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    print(
        json.dumps(
            {key: value for key, value in result.items() if key != "maximizers"},
            indent=2,
            sort_keys=True,
        )
    )
    print("OUTPUT", output)


def main():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="mode", required=True)
    first = subparsers.add_parser("phase-a")
    first.add_argument("--progress", action="store_true")
    second = subparsers.add_parser("phase-b")
    second.add_argument("order", choices=("102", "120", "210"))
    second.add_argument("--workers", type=int, default=None)
    second.add_argument("--progress", action="store_true")
    args = parser.parse_args()
    if args.mode == "phase-a":
        phase_a(progress=args.progress)
    else:
        phase_b(
            tuple(map(int, args.order)),
            workers=args.workers,
            progress=args.progress,
        )


if __name__ == "__main__":
    main()
