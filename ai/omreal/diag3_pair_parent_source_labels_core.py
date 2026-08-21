#!/usr/bin/env python3
"""Exact label continuation on the row-2599 chart-0-to-chart-89 path."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from math import lcm
from pathlib import Path
import json
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUTPUT = DATA / "DIAG3_PAIR_PARENT_SOURCE_LABELS_0_89.json"
TRANSITION = DATA / "DIAG3_PAIR_PARENT_SOURCE_TRANSITION_0_89.json"

sys.path.insert(0, str(HERE))
import DIAG9_GRAPH_exact_topes as topes  # noqa: E402
import four_chart_gate as extension_gate  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402


FORMAT = "diag3-pair-parent-source-labels-v1"
STATUS = "EXACT_PATH_LABEL_CONTINUATION"
EXPECTED_REORIENTATION_MASK = 66_239_625_586_952_485
EXPECTED_TOPE_COUNT = 26_112
EXPECTED_SIGNATURE_COUNT = 97_224


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def normalized_parent(values):
    matrix = [
        [1, 0, 0, 0, 1, 0, 0, 0],
        [0, 1, 0, 0, 1, 0, 0, 0],
        [0, 0, 1, 0, 1, 0, 0, 0],
        [0, 0, 0, 1, 1, 0, 0, 0],
    ]
    for block in range(3):
        column = [Fraction(1), *values[3 * block : 3 * block + 3]]
        scale = lcm(*(value.denominator for value in column))
        for row, value in enumerate(column):
            matrix[row][5 + block] = int(value * scale)
    return matrix


def segment_parent(points, parameter):
    values = tuple(
        (1 - parameter) * left + parameter * right
        for left, right in zip(points[transition.SOURCE_CHART], points[transition.TARGET_CHART])
    )
    return normalized_parent(values)


def solve_reorientation_mask(normalized_signs, raw_signs):
    equations = []
    for basis, normalized, raw in zip(topes.BASES, normalized_signs, raw_signs, strict=True):
        word = 1
        for index in basis:
            word |= 1 << (index + 1)
        equations.append([word, int(normalized != raw)])
    pivots = {}
    for word, value in equations:
        while word:
            pivot = word.bit_length() - 1
            previous = pivots.get(pivot)
            if previous is None:
                pivots[pivot] = (word, value)
                break
            word ^= previous[0]
            value ^= previous[1]
        else:
            if value:
                raise AssertionError("parent reorientation equations contradicted")
    if len(pivots) != 8:
        raise AssertionError("parent reorientation rank changed")
    solution = 0
    for pivot in sorted(pivots):
        word, value = pivots[pivot]
        bit = value ^ ((word & solution).bit_count() & 1)
        solution |= bit << pivot
    mask = 0
    for index, triple in enumerate(topes.TRIPLES):
        bit = solution & 1
        for element in triple:
            bit ^= (solution >> (element + 1)) & 1
        mask |= int(bit) << index
    return mask


def labels_digest(labels):
    digest = sha256(b"diag3-row2599-path-label-set-v1\0")
    for signature in sorted(labels):
        digest.update(int(signature).to_bytes(7, "little"))
    return digest.hexdigest()


def simple_mutation(labels, basis):
    basis = tuple(basis)
    basis_set = set(basis)
    mask = sum(1 << index for index in basis)
    preliminary = []
    for signature in labels:
        if signature ^ mask in labels:
            continue
        if all(signature ^ (1 << index) in labels for index in basis):
            preliminary.append(signature)
    lost = []
    for signature in preliminary:
        neighbors = {
            index
            for index in range(56)
            if signature ^ (1 << index) in labels
        }
        if neighbors == basis_set:
            lost.append(signature)
    if len(lost) != 2 or lost[0] ^ lost[1] != (1 << 56) - 1:
        raise AssertionError(
            f"basis {basis} has {len(preliminary)} preliminary and {len(lost)} simplicial topes"
        )
    gained = {signature ^ mask for signature in lost}
    if gained & labels:
        raise AssertionError("simple mutation gained an existing tope")
    return (labels - set(lost)) | gained, len(preliminary)


def raw_extension_universe():
    parents = [line.strip() for line in extension_gate.CATALOG_48.open(encoding="utf-8") if line.strip()]
    _parent, signatures = extension_gate.enumerate_extensions(parents[extension_gate.PARENT_INDEX])
    signatures = tuple(sorted(map(int, signatures)))
    if len(signatures) != len(set(signatures)) or len(signatures) != EXPECTED_SIGNATURE_COUNT:
        raise AssertionError("row-2599 extension universe changed")
    return signatures


def build_record(progress=False):
    roadmap = json.loads(TRANSITION.read_text(encoding="utf-8"))
    events = roadmap["residual_roadmap"]["events"]
    if len(events) != 1_237:
        raise AssertionError("transition event census changed")
    matrices, points, _packed, _states, _hamming, _multiplicity = transition.exact_inputs()
    normalized_zero = segment_parent(points, Fraction(0))
    raw_zero = matrices[transition.SOURCE_CHART].tolist()
    reorientation = solve_reorientation_mask(
        topes.parent_signs(normalized_zero),
        topes.parent_signs(raw_zero),
    )
    if reorientation != EXPECTED_REORIENTATION_MASK:
        raise AssertionError(f"path reorientation mask changed: {reorientation}")
    normalized_labels = set(topes.parent_topes(normalized_zero))
    labels = {signature ^ reorientation for signature in normalized_labels}
    raw_labels = set(topes.parent_topes(raw_zero))
    if labels != raw_labels or len(labels) != EXPECTED_TOPE_COUNT:
        raise AssertionError("normalized chart-zero labels do not reorient to the raw source")

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

    universe = raw_extension_universe()
    universe_index = {signature: index for index, signature in enumerate(universe)}
    chamber_count = len(events) + 1
    profile_bytes = (chamber_count + 7) // 8
    profiles = np.zeros((len(universe), profile_bytes), dtype=np.uint8)
    chamber_digests = []

    def record_chamber(chamber, current):
        if len(current) != EXPECTED_TOPE_COUNT:
            raise AssertionError(f"chamber {chamber} has {len(current)} topes")
        try:
            indices = np.fromiter(
                (universe_index[signature] for signature in current),
                dtype=np.int64,
                count=len(current),
            )
        except KeyError as error:
            raise AssertionError(f"chamber {chamber} left the extension universe") from error
        profiles[indices, chamber // 8] |= np.uint8(1 << (chamber & 7))
        chamber_digests.append(labels_digest(current))

    record_chamber(0, labels)
    event_records = []
    simple_preliminary = Counter()
    compound_delta = Counter()
    for event_index, event in enumerate(events):
        factor_id = int(event["factor_id"])
        occurrences = factor_occurrences[factor_id]
        before = labels
        if int(event["occurrence_multiplicity"]) == 1:
            if len(occurrences) != 1:
                raise AssertionError("single-occurrence event has the wrong occurrence census")
            labels, preliminary = simple_mutation(labels, occurrences[0])
            simple_preliminary[preliminary] += 1
            method = "simplicial_basis_mutation"
        else:
            right = Fraction(event["isolating_interval"][1])
            next_left = (
                Fraction(events[event_index + 1]["isolating_interval"][0])
                if event_index + 1 < len(events)
                else Fraction(1)
            )
            sample = (right + next_left) / 2
            normalized = set(topes.parent_topes(segment_parent(points, sample)))
            labels = {signature ^ reorientation for signature in normalized}
            method = "exact_post_compound_tope_reenumeration"
        lost = before - labels
        gained = labels - before
        if len(lost) != len(gained):
            raise AssertionError("event changed the generic tope count")
        if method == "simplicial_basis_mutation" and (len(lost), len(gained)) != (2, 2):
            raise AssertionError("simple mutation did not exchange one antipodal pair")
        if method != "simplicial_basis_mutation":
            compound_delta[(int(event["occurrence_multiplicity"]), len(lost), len(gained))] += 1
        record_chamber(event_index + 1, labels)
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
                f"continued {event_index + 1}/{len(events)} events; compound={sum(compound_delta.values())}",
                flush=True,
            )

    raw_target = set(topes.parent_topes(matrices[transition.TARGET_CHART].tolist()))
    if labels != raw_target:
        raise AssertionError("continued label state does not equal raw chart 89")

    profile_digest = sha256(b"diag3-row2599-path-label-profiles-v1\0")
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

    chamber_digest = sha256(b"diag3-row2599-path-chamber-label-digests-v1\0")
    for digest in chamber_digests:
        chamber_digest.update(bytes.fromhex(digest))
    event_digest = sha256(b"diag3-row2599-path-label-events-v1\0")
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
            "source_chart": 0,
            "target_chart": 89,
            "generic_chambers": chamber_count,
            "signature_label_continuation": "COMPLETE_ON_ALL_OPEN_PATH_CHAMBERS",
            "wall_label_specialization": "CONSERVATIVE_ALL_INCIDENT_CHAMBERS_RULE",
            "global_parent_cell_coverage": "NOT_CLAIMED",
        },
        "inputs": {
            "transition_certificate": str(TRANSITION.relative_to(HERE.parents[1])),
            "transition_certificate_sha256": file_sha256(TRANSITION),
            "point_bank_sha256": transition.file_sha256(transition.POINT_BANK),
            "factor_census_sha256": transition.file_sha256(transition.FACTOR_CENSUS),
        },
        "normalization": {
            "raw_extension_reorientation_mask": reorientation,
            "mask_row_indices": [index for index in range(56) if reorientation >> index & 1],
            "source_raw_normalized_label_sets_equal_after_reorientation": True,
        },
        "continuation": {
            "extension_signature_universe": len(universe),
            "labels_per_generic_chamber": EXPECTED_TOPE_COUNT,
            "ordered_events": len(events),
            "simple_mutation_events": sum(simple_preliminary.values()),
            "compound_reenumeration_events": sum(compound_delta.values()),
            "simple_preliminary_candidate_census": {str(key): value for key, value in sorted(simple_preliminary.items())},
            "compound_delta_census": {
                f"multiplicity_{multiplicity}:lost_{lost}:gained_{gained}": count
                for (multiplicity, lost, gained), count in sorted(compound_delta.items())
            },
            "chart_89_raw_label_state_reconstructed": True,
            "chamber_label_digests_sha256": chamber_digest.hexdigest(),
            "event_label_semantic_sha256": event_digest.hexdigest(),
            "event_records": event_records,
        },
        "signature_profiles": {
            "packed_profile_bytes_each": profile_bytes,
            "distinct_profiles": len(profile_counter),
            "semantic_sha256": profile_digest.hexdigest(),
            "feasible_chamber_count_census": {str(key): value for key, value in sorted(feasible_count_census.items())},
            "profile_transition_count_census": {str(key): value for key, value in sorted(transition_count_census.items())},
            "all_bad_loci_closed_by_incidence_rule": True,
        },
        "theorem_effect": "Closes label continuation on one exact row-2599 source path; closes neither invariant diagonal-three obligation and leaves 9DVL at 2/9.",
        "next_exact_question": "Can the exact path-labelled one-dimensional master complex be glued to enough source paths and parent-infinity faces to form a coverage-certified row-2599 two-skeleton?",
        "verifier": {
            "command": "python ai/omreal/verify_diag3_pair_parent_source_labels.py",
            "hostile_corruptions": 10,
        },
    }
