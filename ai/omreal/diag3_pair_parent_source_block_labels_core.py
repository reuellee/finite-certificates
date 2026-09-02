#!/usr/bin/env python3
"""Exact label continuation on the row-2599 chart-0-to-chart-152 bridge."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import json
import multiprocessing
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUTPUT = DATA / "DIAG3_PAIR_PARENT_SOURCE_BLOCK_LABELS_0_152.json"
BRIDGE = DATA / "DIAG3_PAIR_PARENT_SOURCE_BLOCK_BRIDGE_0_152.json"

sys.path.insert(0, str(HERE))
import DIAG9_GRAPH_exact_topes as topes  # noqa: E402
import diag3_pair_parent_source_block_bridge_core as bridge  # noqa: E402
import diag3_pair_parent_source_labels_core as source_labels  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402


FORMAT = "diag3-pair-parent-source-block-labels-v1"
STATUS = "EXACT_THREE_BLOCK_PATH_LABEL_CONTINUATION"
EXPECTED_TOPE_COUNT = source_labels.EXPECTED_TOPE_COUNT
EXPECTED_SIGNATURE_COUNT = source_labels.EXPECTED_SIGNATURE_COUNT


def file_sha256(path: Path) -> str:
    return source_labels.file_sha256(path)


def segment_parent(vertices, segment_index, parameter):
    left = vertices[segment_index]
    right = vertices[segment_index + 1]
    values = tuple(
        (1 - parameter) * first + parameter * second
        for first, second in zip(left, right, strict=True)
    )
    return source_labels.normalized_parent(values)


def event_groups(events, segment_count):
    grouped = [[] for _ in range(segment_count)]
    for event in events:
        grouped[int(event["segment_index"])].append(event)
    return tuple(tuple(rows) for rows in grouped)


def _compound_topes(parent):
    return set(topes.parent_topes(parent))


def compound_tasks(vertices, grouped_events):
    tasks = []
    for segment_index, segment_events in enumerate(grouped_events):
        for local_event_index, event in enumerate(segment_events):
            if int(event["occurrence_multiplicity"]) == 1:
                continue
            right = Fraction(event["isolating_interval"][1])
            next_left = (
                Fraction(segment_events[local_event_index + 1]["isolating_interval"][0])
                if local_event_index + 1 < len(segment_events)
                else Fraction(1)
            )
            tasks.append(segment_parent(vertices, segment_index, (right + next_left) / 2))
    return tuple(tasks)


def build_record(progress=False, workers=None):
    roadmap = json.loads(BRIDGE.read_text(encoding="utf-8"))
    events = roadmap["residual_roadmap"]["events"]
    if len(events) != 5_612:
        raise AssertionError("block-bridge event census changed")

    matrices, points, _packed, _states, _hamming, _multiplicity = transition.exact_inputs()
    vertices = bridge.bridge_vertices(
        points[bridge.SOURCE_CHART],
        points[bridge.TARGET_CHART],
        bridge.BLOCK_ORDER,
    )
    grouped_events = event_groups(events, len(vertices) - 1)
    if tuple(map(len, grouped_events)) != (2_774, 1_017, 1_821):
        raise AssertionError("block-bridge segment event census changed")
    compound_parents = compound_tasks(vertices, grouped_events)
    if len(compound_parents) != 293:
        raise AssertionError("block-bridge compound event census changed")
    process_count = workers or max(1, min(6, multiprocessing.cpu_count()))
    method = (
        "fork"
        if "fork" in multiprocessing.get_all_start_methods()
        else "spawn"
    )
    pool = None
    try:
        pool = multiprocessing.get_context(method).Pool(process_count)
        compound_results = pool.imap(_compound_topes, compound_parents, chunksize=1)

        normalized_zero = segment_parent(vertices, 0, Fraction(0))
        raw_zero = matrices[bridge.SOURCE_CHART].tolist()
        reorientation = source_labels.solve_reorientation_mask(
            topes.parent_signs(normalized_zero),
            topes.parent_signs(raw_zero),
        )
        if reorientation != source_labels.EXPECTED_REORIENTATION_MASK:
            raise AssertionError(f"bridge reorientation mask changed: {reorientation}")
        labels = {
            signature ^ reorientation
            for signature in topes.parent_topes(normalized_zero)
        }
        raw_labels = set(topes.parent_topes(raw_zero))
        if labels != raw_labels or len(labels) != EXPECTED_TOPE_COUNT:
            raise AssertionError(
                "normalized chart-zero labels do not reorient to the raw source"
            )

        with np.load(transition.FACTOR_CENSUS, allow_pickle=False) as source:
            occurrence_factor = np.asarray(source["occurrence_factor"], dtype=np.uint32)
            occurrence_fourset = np.asarray(source["occurrence_fourset"], dtype=np.uint8)
        event_factor_ids = {int(event["factor_id"]) for event in events}
        factor_occurrences = {
            factor_id: tuple(
                tuple(map(int, row))
                for row in occurrence_fourset[np.flatnonzero(occurrence_factor == factor_id)]
            )
            for factor_id in event_factor_ids
        }

        universe = source_labels.raw_extension_universe()
        universe_index = {signature: index for index, signature in enumerate(universe)}
        chamber_count = len(events) + len(grouped_events)
        if chamber_count != roadmap["regular_cw_path"]["one_cells"]:
            raise AssertionError("generic path chambers do not match regular-CW one-cells")
        profile_bytes = (chamber_count + 7) // 8
        profiles = np.zeros((len(universe), profile_bytes), dtype=np.uint8)
        chamber_digests = []

        def record_chamber(current):
            chamber = len(chamber_digests)
            if len(current) != EXPECTED_TOPE_COUNT:
                raise AssertionError(f"chamber {chamber} has {len(current)} topes")
            try:
                indices = np.fromiter(
                    (universe_index[signature] for signature in current),
                    dtype=np.int64,
                    count=len(current),
                )
            except KeyError as error:
                raise AssertionError(
                    f"chamber {chamber} left the extension universe"
                ) from error
            profiles[indices, chamber // 8] |= np.uint8(1 << (chamber & 7))
            chamber_digests.append(source_labels.labels_digest(current))
            return chamber

        event_records = []
        waypoint_records = []
        simple_preliminary = Counter()
        compound_delta = Counter()
        global_event_index = 0
        for segment_index, segment_events in enumerate(grouped_events):
            pre_segment_chamber = record_chamber(labels)
            if segment_index:
                if pre_segment_chamber != waypoint_records[-1]["right_chamber"]:
                    raise AssertionError("waypoint chamber accounting changed")
            for local_event_index, event in enumerate(segment_events):
                factor_id = int(event["factor_id"])
                occurrences = factor_occurrences[factor_id]
                before = labels
                if int(event["occurrence_multiplicity"]) == 1:
                    if len(occurrences) != 1:
                        raise AssertionError("single-occurrence bridge event has wrong census")
                    labels, preliminary = source_labels.simple_mutation(labels, occurrences[0])
                    simple_preliminary[preliminary] += 1
                    method = "simplicial_basis_mutation"
                else:
                    normalized = next(compound_results)
                    labels = {signature ^ reorientation for signature in normalized}
                    method = "exact_post_compound_tope_reenumeration"
                lost = before - labels
                gained = labels - before
                if len(lost) != len(gained):
                    raise AssertionError("bridge event changed the generic tope count")
                if method == "simplicial_basis_mutation" and (len(lost), len(gained)) != (2, 2):
                    raise AssertionError("simple bridge mutation did not exchange one antipodal pair")
                if method != "simplicial_basis_mutation":
                    compound_delta[(int(event["occurrence_multiplicity"]), len(lost), len(gained))] += 1
                post_chamber = record_chamber(labels)
                event_records.append({
                    "event_index": global_event_index,
                    "segment_index": segment_index,
                    "segment_event_index": local_event_index,
                    "factor_id": factor_id,
                    "occurrence_multiplicity": int(event["occurrence_multiplicity"]),
                    "method": method,
                    "lost_labels": len(lost),
                    "gained_labels": len(gained),
                    "post_chamber": post_chamber,
                    "post_chamber_labels_sha256": chamber_digests[-1],
                })
                global_event_index += 1
                if progress and (
                    method != "simplicial_basis_mutation" or global_event_index % 250 == 0
                ):
                    print(
                        f"continued {global_event_index}/{len(events)} events; "
                        f"compound={sum(compound_delta.values())}",
                        flush=True,
                    )

            endpoint_normalized = set(topes.parent_topes(
                segment_parent(vertices, segment_index, Fraction(1))
            ))
            endpoint_labels = {signature ^ reorientation for signature in endpoint_normalized}
            if labels != endpoint_labels:
                raise AssertionError(f"segment {segment_index} endpoint label state was not reconstructed")
            if segment_index + 1 < len(grouped_events):
                left_chamber = len(chamber_digests) - 1
                right_chamber = len(chamber_digests)
                waypoint_records.append({
                    "waypoint_index": segment_index + 1,
                    "left_chamber": left_chamber,
                    "right_chamber": right_chamber,
                    "raw_labels_sha256": source_labels.labels_digest(labels),
                    "left_and_right_label_sets_equal": True,
                })
    except BaseException:
        if pool is not None:
            pool.terminate()
            pool.join()
        raise
    else:
        pool.close()
        pool.join()

    if global_event_index != len(events) or len(chamber_digests) != chamber_count:
        raise AssertionError("bridge label continuation accounting changed")
    raw_target = set(topes.parent_topes(matrices[bridge.TARGET_CHART].tolist()))
    if labels != raw_target:
        raise AssertionError("continued label state does not equal raw chart 152")

    profile_digest = sha256(b"diag3-row2599-block-path-label-profiles-v1\0")
    profile_counter = Counter()
    feasible_count_census = Counter()
    transition_count_census = Counter()
    for signature, row in zip(universe, profiles, strict=True):
        payload = row.tobytes()
        profile_counter[payload] += 1
        bits = np.unpackbits(row, bitorder="little")[:chamber_count]
        feasible_count_census[int(np.count_nonzero(bits))] += 1
        transition_count_census[int(np.count_nonzero(bits[1:] != bits[:-1]))] += 1
        profile_digest.update(int(signature).to_bytes(7, "little"))
        profile_digest.update(payload)

    chamber_digest = sha256(b"diag3-row2599-block-path-chamber-label-digests-v1\0")
    for digest in chamber_digests:
        chamber_digest.update(bytes.fromhex(digest))
    event_digest = sha256(b"diag3-row2599-block-path-label-events-v1\0")
    for row in event_records:
        event_digest.update(int(row["segment_index"]).to_bytes(1, "little"))
        event_digest.update(int(row["factor_id"]).to_bytes(4, "little"))
        event_digest.update(int(row["occurrence_multiplicity"]).to_bytes(2, "little"))
        event_digest.update(int(row["lost_labels"]).to_bytes(4, "little"))
        event_digest.update(bytes.fromhex(row["post_chamber_labels_sha256"]))

    return {
        "format": FORMAT,
        "status": STATUS,
        "scope": {
            "parent_index": 2599,
            "source_chart": 0,
            "target_chart": 152,
            "path_segments": len(grouped_events),
            "generic_chambers": chamber_count,
            "signature_label_continuation": "COMPLETE_ON_ALL_OPEN_PATH_CHAMBERS",
            "waypoint_incidence": "PRESERVED_AS_DISTINCT_EQUAL-LABEL_CHAMBERS",
            "wall_label_specialization": "CONSERVATIVE_ALL_INCIDENT_CHAMBERS_RULE",
            "global_parent_cell_coverage": "NOT_CLAIMED",
        },
        "inputs": {
            "bridge_certificate": BRIDGE.relative_to(HERE.parents[1]).as_posix(),
            "bridge_certificate_sha256": file_sha256(BRIDGE),
            "point_bank_sha256": transition.file_sha256(transition.POINT_BANK),
            "factor_census_sha256": transition.file_sha256(transition.FACTOR_CENSUS),
            "chart_zero_label_certificate": source_labels.OUTPUT.relative_to(HERE.parents[1]).as_posix(),
            "chart_zero_label_certificate_sha256": source_labels.file_sha256(source_labels.OUTPUT),
        },
        "normalization": {
            "raw_extension_reorientation_mask": reorientation,
            "source_raw_normalized_label_sets_equal_after_reorientation": True,
        },
        "continuation": {
            "extension_signature_universe": len(universe),
            "labels_per_generic_chamber": EXPECTED_TOPE_COUNT,
            "ordered_events": len(events),
            "segment_event_census": list(map(len, grouped_events)),
            "simple_mutation_events": sum(simple_preliminary.values()),
            "compound_reenumeration_events": sum(compound_delta.values()),
            "simple_preliminary_candidate_census": {
                str(key): value for key, value in sorted(simple_preliminary.items())
            },
            "compound_delta_census": {
                f"multiplicity_{multiplicity}:lost_{lost}:gained_{gained}": count
                for (multiplicity, lost, gained), count in sorted(compound_delta.items())
            },
            "internal_waypoints": waypoint_records,
            "chart_152_raw_label_state_reconstructed": True,
            "chamber_label_digests_sha256": chamber_digest.hexdigest(),
            "event_label_semantic_sha256": event_digest.hexdigest(),
            "event_records": event_records,
        },
        "signature_profiles": {
            "packed_profile_bytes_each": profile_bytes,
            "distinct_profiles": len(profile_counter),
            "semantic_sha256": profile_digest.hexdigest(),
            "feasible_chamber_count_census": {
                str(key): value for key, value in sorted(feasible_count_census.items())
            },
            "profile_transition_count_census": {
                str(key): value for key, value in sorted(transition_count_census.items())
            },
            "all_bad_loci_closed_by_incidence_rule": True,
        },
        "gluing": {
            "shared_chart": 0,
            "existing_0_89_label_certificate_sha256": source_labels.file_sha256(source_labels.OUTPUT),
            "raw_chart_zero_labels_sha256": source_labels.labels_digest(raw_labels),
            "exact_common_source_vertex_and_label_set": True,
        },
        "theorem_effect": "Closes label continuation on the exact chart-0-to-chart-152 block bridge and glues it to the chart-0-to-chart-89 labelled path; closes neither invariant diagonal-three obligation and leaves 9DVL at 2/9.",
        "next_exact_question": "Attach genuine parent-boundary faces from the pinned (Delta^3)^3 compactification and build a missed-component certificate; the finite labelled source tree is not parameter-space coverage.",
        "verifier": {
            "command": "python ai/omreal/verify_diag3_pair_parent_source_block_labels.py",
            "hostile_corruptions": 12,
        },
    }
