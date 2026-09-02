#!/usr/bin/env python3
"""Exact label continuation from chart 89 to the relative divisor [1237]=0."""

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
OUTPUT = DATA / "DIAG3_PAIR_PARENT_BOUNDARY_LABELS_89_1237.json"
ATTACHMENT = DATA / "DIAG3_PAIR_PARENT_BOUNDARY_ATTACHMENT_89_1237.json"
FORMAT = "diag3-pair-parent-boundary-labels-v1"
STATUS = "EXACT_RELATIVE_BOUNDARY_PATH_LABEL_CONTINUATION"

sys.path.insert(0, str(HERE))
import DIAG9_GRAPH_exact_topes as topes  # noqa: E402
import diag3_pair_parent_boundary_attachment_core as attachment  # noqa: E402
import diag3_pair_parent_source_labels_core as source_labels  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402


def boundary_parent(source, parameter):
    return source_labels.normalized_parent(attachment.boundary_ray(source, parameter))


def _compound_topes(parent):
    return set(topes.parent_topes(parent))


def compound_tasks(source, events):
    tasks = []
    for event_index, event in enumerate(events):
        if int(event["occurrence_multiplicity"]) == 1:
            continue
        right = Fraction(event["isolating_interval"][1])
        next_left = (
            Fraction(events[event_index + 1]["isolating_interval"][0])
            if event_index + 1 < len(events)
            else Fraction(1)
        )
        tasks.append(boundary_parent(source, (right + next_left) / 2))
    return tuple(tasks)


def build_record(progress=False, workers=None):
    roadmap = json.loads(ATTACHMENT.read_text(encoding="utf-8"))
    events = roadmap["residual_roadmap"]["events"]
    if len(events) != 1_517:
        raise AssertionError("boundary attachment event census changed")

    matrices, points, _packed, _states, _hamming, _multiplicity = transition.exact_inputs()
    source = points[attachment.SOURCE_CHART]
    normalized_source = boundary_parent(source, Fraction(0))
    raw_source = matrices[attachment.SOURCE_CHART].tolist()
    reorientation = source_labels.solve_reorientation_mask(
        topes.parent_signs(normalized_source),
        topes.parent_signs(raw_source),
    )
    if reorientation != source_labels.EXPECTED_REORIENTATION_MASK:
        raise AssertionError(f"boundary reorientation mask changed: {reorientation}")
    labels = {
        signature ^ reorientation
        for signature in topes.parent_topes(normalized_source)
    }
    raw_labels = set(topes.parent_topes(raw_source))
    if labels != raw_labels or len(labels) != source_labels.EXPECTED_TOPE_COUNT:
        raise AssertionError("normalized chart-89 labels do not reorient to the raw source")
    source_digest = source_labels.labels_digest(raw_labels)
    if source_digest != roadmap["overlap_with_labelled_0_89_path"]["source_path_terminal_labels_sha256"]:
        raise AssertionError("chart-89 boundary source does not glue to the labelled 0-to-89 path")

    with np.load(transition.FACTOR_CENSUS, allow_pickle=False) as source_file:
        occurrence_factor = np.asarray(source_file["occurrence_factor"], dtype=np.uint32)
        occurrence_fourset = np.asarray(source_file["occurrence_fourset"], dtype=np.uint8)
    event_factor_ids = {int(event["factor_id"]) for event in events}
    factor_occurrences = {
        factor_id: tuple(
            tuple(map(int, row))
            for row in occurrence_fourset[np.flatnonzero(occurrence_factor == factor_id)]
        )
        for factor_id in event_factor_ids
    }

    compound_parents = compound_tasks(source, events)
    if len(compound_parents) != 63:
        raise AssertionError("boundary compound-event census changed")
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

        universe = source_labels.raw_extension_universe()
        universe_index = {signature: index for index, signature in enumerate(universe)}
        chamber_count = len(events) + 1
        profile_bytes = (chamber_count + 7) // 8
        profiles = np.zeros((len(universe), profile_bytes), dtype=np.uint8)
        chamber_digests = []

        def record_chamber(current):
            chamber = len(chamber_digests)
            if len(current) != source_labels.EXPECTED_TOPE_COUNT:
                raise AssertionError(f"boundary chamber {chamber} has {len(current)} topes")
            try:
                indices = np.fromiter(
                    (universe_index[signature] for signature in current),
                    dtype=np.int64,
                    count=len(current),
                )
            except KeyError as error:
                raise AssertionError(
                    f"boundary chamber {chamber} left the extension universe"
                ) from error
            profiles[indices, chamber // 8] |= np.uint8(1 << (chamber & 7))
            chamber_digests.append(source_labels.labels_digest(current))

        record_chamber(labels)
        event_records = []
        simple_preliminary = Counter()
        compound_delta = Counter()
        for event_index, event in enumerate(events):
            factor_id = int(event["factor_id"])
            occurrences = factor_occurrences[factor_id]
            before = labels
            if int(event["occurrence_multiplicity"]) == 1:
                if len(occurrences) != 1:
                    raise AssertionError("single-occurrence boundary event has wrong census")
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
                raise AssertionError("boundary event changed the generic tope count")
            if method == "simplicial_basis_mutation" and (len(lost), len(gained)) != (2, 2):
                raise AssertionError("simple boundary mutation did not exchange an antipodal pair")
            if method != "simplicial_basis_mutation":
                compound_delta[(int(event["occurrence_multiplicity"]), len(lost), len(gained))] += 1
            record_chamber(labels)
            event_records.append({
                "event_index": event_index,
                "factor_id": factor_id,
                "occurrence_multiplicity": int(event["occurrence_multiplicity"]),
                "method": method,
                "lost_labels": len(lost),
                "gained_labels": len(gained),
                "post_chamber_labels_sha256": chamber_digests[-1],
            })
            if progress and (method != "simplicial_basis_mutation" or (event_index + 1) % 100 == 0):
                print(
                    f"continued {event_index + 1}/{len(events)} boundary events; "
                    f"compound={sum(compound_delta.values())}",
                    flush=True,
                )
    except BaseException:
        if pool is not None:
            pool.terminate()
            pool.join()
        raise
    else:
        pool.close()
        pool.join()

    last_right = Fraction(events[-1]["isolating_interval"][1])
    endpoint_near_parameter = (last_right + 1) / 2
    endpoint_near = {
        signature ^ reorientation
        for signature in topes.parent_topes(boundary_parent(source, endpoint_near_parameter))
    }
    if labels != endpoint_near:
        raise AssertionError("continued last chamber does not equal endpoint-near reenumeration")

    profile_digest = sha256(b"diag3-row2599-boundary-89-1237-label-profiles-v1\0")
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

    chamber_digest = sha256(b"diag3-row2599-boundary-89-1237-chamber-label-digests-v1\0")
    for digest in chamber_digests:
        chamber_digest.update(bytes.fromhex(digest))
    event_digest = sha256(b"diag3-row2599-boundary-89-1237-label-events-v1\0")
    for row in event_records:
        event_digest.update(int(row["factor_id"]).to_bytes(4, "little"))
        event_digest.update(int(row["occurrence_multiplicity"]).to_bytes(2, "little"))
        event_digest.update(int(row["lost_labels"]).to_bytes(4, "little"))
        event_digest.update(bytes.fromhex(row["post_chamber_labels_sha256"]))

    return {
        "format": FORMAT,
        "status": STATUS,
        "scope": {
            "parent_index": 2599,
            "source_chart": 89,
            "target_parent_divisor": "[1237]=0",
            "generic_chambers": chamber_count,
            "signature_label_continuation": "COMPLETE_ON_ALL_OPEN_RAY_CHAMBERS",
            "relative_endpoint_rule": "PARENT_DIVISOR_CELL_EXCLUDED_FROM_RELATIVE_CHAINS",
            "wall_label_specialization": "CONSERVATIVE_ALL_INCIDENT_CHAMBERS_RULE",
            "global_parent_cell_coverage": "NOT_CLAIMED",
        },
        "inputs": {
            "boundary_attachment_certificate": ATTACHMENT.relative_to(HERE.parents[1]).as_posix(),
            "boundary_attachment_certificate_sha256": source_labels.file_sha256(ATTACHMENT),
            "point_bank_sha256": transition.file_sha256(transition.POINT_BANK),
            "factor_census_sha256": transition.file_sha256(transition.FACTOR_CENSUS),
            "source_label_certificate": source_labels.OUTPUT.relative_to(HERE.parents[1]).as_posix(),
            "source_label_certificate_sha256": source_labels.file_sha256(source_labels.OUTPUT),
        },
        "normalization": {
            "raw_extension_reorientation_mask": reorientation,
            "source_raw_normalized_label_sets_equal_after_reorientation": True,
        },
        "continuation": {
            "extension_signature_universe": len(universe),
            "labels_per_generic_chamber": source_labels.EXPECTED_TOPE_COUNT,
            "ordered_events": len(events),
            "simple_mutation_events": sum(simple_preliminary.values()),
            "compound_reenumeration_events": sum(compound_delta.values()),
            "simple_preliminary_candidate_census": {
                str(key): value for key, value in sorted(simple_preliminary.items())
            },
            "compound_delta_census": {
                f"multiplicity_{multiplicity}:lost_{lost}:gained_{gained}": count
                for (multiplicity, lost, gained), count in sorted(compound_delta.items())
            },
            "last_open_chamber_reconstructed_by_independent_endpoint_near_reenumeration": True,
            "endpoint_near_sample_parameter": attachment.fraction_text(endpoint_near_parameter),
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
            "shared_chart": 89,
            "source_path_terminal_labels_sha256": source_digest,
            "raw_chart_89_labels_sha256": source_labels.labels_digest(raw_labels),
            "exact_common_source_vertex_and_label_set": True,
        },
        "relative_boundary": {
            "parent_infinity_subcomplex": ["endpoint_parent_divisor_1237"],
            "endpoint_residual_factor_zeros": 0,
            "last_incident_open_chamber_labels_sha256": source_labels.labels_digest(labels),
            "endpoint_chain_generators_retained": 0,
        },
        "theorem_effect": "Closes label continuation from chart 89 to the first genuine relative parent-boundary endpoint; closes neither invariant diagonal-three obligation and leaves 9DVL at 2/9.",
        "next_exact_question": "Prove missed-component coverage for the labelled source-boundary skeleton or replace it with a coverage-certified global master complex.",
        "verifier": {
            "command": "python ai/omreal/verify_diag3_pair_parent_boundary_labels.py",
            "hostile_corruptions": 12,
        },
    }
