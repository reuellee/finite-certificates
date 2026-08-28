#!/usr/bin/env python3
"""Exact 97,224-signature continuation on retained edge 39 (0--113)."""

from __future__ import annotations

from collections import Counter
from concurrent.futures import ProcessPoolExecutor
from fractions import Fraction
from hashlib import sha256
from math import lcm
from pathlib import Path
import gzip
import json
import os
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUTPUT = DATA / "DIAG3_PAIR_PARENT_SOURCE_LABELS_EDGE39_0_113.json"
PROFILE_OUTPUT = DATA / "DIAG3_PAIR_PARENT_SOURCE_LABELS_EDGE39_0_113_PROFILES.bin.gz"
TRANSITION = DATA / "DIAG3_PAIR_PARENT_SOURCE_TRANSITION_EDGE39_0_113.json"
EXPECTED_TRANSITION_SHA256 = "cb6eebc0df9bfeae8055c81471f09d594f8116e002caf11f62f9e865b0936dd7"
FORMAT = "diag3-pair-parent-source-labels-edge-v2"
PROFILE_FORMAT = b"D3E39P1\0"
STATUS = "EXACT_EDGE39_PATH_LABEL_CONTINUATION"
EXPECTED_REORIENTATION_MASK = 66_239_625_586_952_485
EXPECTED_TOPE_COUNT = 26_112
EXPECTED_SIGNATURE_COUNT = 97_224

sys.path.insert(0, str(HERE))
import DIAG9_GRAPH_exact_topes as topes  # noqa: E402
import four_chart_gate as extension_gate  # noqa: E402
import diag3_pair_parent_source_transition_EDGE39_0_113_core as transition_core  # noqa: E402


def labels_digest(labels):
    digest = sha256(b"diag3-row2599-edge39-label-set-v1\0")
    for signature in sorted(labels):
        digest.update(int(signature).to_bytes(7, "little"))
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
            index for index in range(56)
            if signature ^ (1 << index) in labels
        }
        if neighbors == basis_set:
            lost.append(signature)
    if len(lost) != 2 or lost[0] ^ lost[1] != (1 << 56) - 1:
        raise AssertionError(f"basis {basis} does not expose one antipodal simplicial pair")
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


def segment_parent(points, parameter):
    values = tuple(
        (1 - parameter) * left + parameter * right
        for left, right in zip(points[0], points[113])
    )
    return normalized_parent(values)


def compound_label_state(task):
    parent, reorientation = task
    return tuple(sorted(signature ^ reorientation for signature in topes.parent_topes(parent)))


def write_profile_artifact(path, universe, profiles, chamber_count):
    if profiles.shape != (EXPECTED_SIGNATURE_COUNT, (chamber_count + 7) // 8):
        raise AssertionError("packed profile tensor shape changed")
    header = bytearray(PROFILE_FORMAT)
    header.extend(EXPECTED_SIGNATURE_COUNT.to_bytes(4, "little"))
    header.extend(chamber_count.to_bytes(4, "little"))
    header.extend(profiles.shape[1].to_bytes(4, "little"))
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as target:
            target.write(header)
            for signature, row in zip(universe, profiles, strict=True):
                target.write(int(signature).to_bytes(8, "little"))
                target.write(row.tobytes())


def check_profile_artifact(path, expected_semantic_sha256):
    """Producer-side structural replay of the deterministic packed artifact."""
    digest = sha256(b"diag3-row2599-edge39-label-profiles-v1\0")
    with gzip.open(path, "rb") as source:
        if source.read(8) != PROFILE_FORMAT:
            raise AssertionError("edge-39 packed-profile magic changed")
        signature_count = int.from_bytes(source.read(4), "little")
        chamber_count = int.from_bytes(source.read(4), "little")
        profile_bytes = int.from_bytes(source.read(4), "little")
        if (signature_count, chamber_count, profile_bytes) != (
            EXPECTED_SIGNATURE_COUNT, 5_328, 666
        ):
            raise AssertionError("edge-39 packed-profile header changed")
        previous = -1
        chamber_sizes = np.zeros(chamber_count, dtype=np.int64)
        for _index in range(signature_count):
            signature_bytes = source.read(8)
            payload = source.read(profile_bytes)
            if len(signature_bytes) != 8 or len(payload) != profile_bytes:
                raise AssertionError("edge-39 packed-profile artifact is truncated")
            signature = int.from_bytes(signature_bytes, "little")
            if signature <= previous:
                raise AssertionError("edge-39 signatures are not strictly ordered")
            previous = signature
            digest.update(signature.to_bytes(7, "little"))
            digest.update(payload)
            chamber_sizes += np.unpackbits(
                np.frombuffer(payload, dtype=np.uint8), bitorder="little"
            )[:chamber_count]
        if source.read(1):
            raise AssertionError("edge-39 packed-profile artifact has trailing bytes")
    if digest.hexdigest() != expected_semantic_sha256:
        raise AssertionError("edge-39 packed-profile semantic digest changed")
    if not np.all(chamber_sizes == EXPECTED_TOPE_COUNT):
        raise AssertionError("a packed edge-39 chamber does not have 26,112 labels")
    return {
        "signature_count": signature_count,
        "chamber_count": chamber_count,
        "labels_per_chamber": EXPECTED_TOPE_COUNT,
        "semantic_sha256": digest.hexdigest(),
    }


def file_sha256(path):
    digest = sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def build_record(progress=False):
    if file_sha256(TRANSITION) != EXPECTED_TRANSITION_SHA256:
        raise AssertionError("edge-39 transition digest changed")
    roadmap = json.loads(TRANSITION.read_text(encoding="utf-8"))
    if roadmap["semantic_sha256"] != transition_core.semantic_seal(roadmap):
        raise AssertionError("edge-39 transition semantic seal failed")
    events = roadmap["residual_roadmap"]["events"]
    if len(events) != 5_327:
        raise AssertionError("edge-39 transition event census changed")

    matrices, points, _states, _hamming, _multiplicity = transition_core.exact_inputs()
    normalized_zero = segment_parent(points, Fraction(0))
    raw_zero = matrices[0].tolist()
    reorientation = solve_reorientation_mask(
        topes.parent_signs(normalized_zero), topes.parent_signs(raw_zero)
    )
    if reorientation != EXPECTED_REORIENTATION_MASK:
        raise AssertionError("source normalization reorientation changed")
    labels = {signature ^ reorientation for signature in topes.parent_topes(normalized_zero)}
    if labels != set(topes.parent_topes(raw_zero)) or len(labels) != EXPECTED_TOPE_COUNT:
        raise AssertionError("normalized source labels do not equal raw source labels")

    with np.load(transition_core.FACTOR_CENSUS, allow_pickle=False) as source:
        occurrence_factor = np.asarray(source["occurrence_factor"], dtype=np.uint32)
        occurrence_fourset = np.asarray(source["occurrence_fourset"], dtype=np.uint8)
    event_factor_ids = {
        int(member["factor_id"])
        for event in events for member in event["members"]
    }
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

    def is_simple(event):
        members = event["members"]
        return (
            len(members) == 1
            and members[0]["sign_flip"] is True
            and int(members[0]["algebraic_multiplicity"]) == 1
            and int(members[0]["occurrence_multiplicity"]) == 1
        )

    record_chamber(0, labels)
    compound_tasks = []
    compound_indices = []
    for event_index, event in enumerate(events):
        if is_simple(event):
            continue
        right = Fraction(event["isolating_interval"][1])
        next_left = Fraction(events[event_index + 1]["isolating_interval"][0]) if event_index + 1 < len(events) else Fraction(1)
        sample = (right + next_left) / 2
        compound_indices.append(event_index)
        compound_tasks.append((segment_parent(points, sample), reorientation))

    workers = max(1, min(4, int(os.environ.get("DIAG3_EDGE39_LABEL_WORKERS", "4"))))
    if progress:
        print(f"precomputing {len(compound_tasks)} exact compound states with {workers} workers", flush=True)
    if workers == 1:
        compound_rows = map(compound_label_state, compound_tasks)
        compound_states = dict(zip(compound_indices, compound_rows, strict=True))
    else:
        with ProcessPoolExecutor(max_workers=workers) as executor:
            compound_rows = executor.map(compound_label_state, compound_tasks, chunksize=1)
            compound_states = dict(zip(compound_indices, compound_rows, strict=True))

    simple_census = Counter()
    compound_delta = Counter()
    event_records = []
    for event_index, event in enumerate(events):
        before = labels
        if is_simple(event):
            member = event["members"][0]
            occurrences = factor_occurrences[int(member["factor_id"])]
            if len(occurrences) != 1:
                raise AssertionError("simple event occurrence census changed")
            labels, preliminary = simple_mutation(labels, occurrences[0])
            simple_census[preliminary] += 1
            method = "simplicial_basis_mutation"
        else:
            labels = set(compound_states[event_index])
            method = "exact_post_event_tope_reenumeration"
        lost = before - labels
        gained = labels - before
        if len(lost) != len(gained):
            raise AssertionError("event changed the generic tope count")
        if method == "simplicial_basis_mutation" and (len(lost), len(gained)) != (2, 2):
            raise AssertionError("simple mutation did not exchange one antipodal pair")
        if method != "simplicial_basis_mutation":
            key = (
                tuple(int(member["occurrence_multiplicity"]) for member in event["members"]),
                tuple(int(member["algebraic_multiplicity"]) for member in event["members"]),
                len(lost), len(gained),
            )
            compound_delta[key] += 1
        record_chamber(event_index + 1, labels)
        event_records.append({
            "event_index": event_index,
            "factor_ids": [int(member["factor_id"]) for member in event["members"]],
            "method": method,
            "lost_labels": len(lost),
            "gained_labels": len(gained),
            "post_chamber_labels_sha256": chamber_digests[-1],
        })
        if progress and (event_index + 1) % 500 == 0:
            print(f"continued {event_index + 1}/{len(events)} events", flush=True)

    raw_target = set(topes.parent_topes(matrices[113].tolist()))
    if labels != raw_target:
        raise AssertionError("continued labels do not reconstruct raw chart 113")

    profile_digest = sha256(b"diag3-row2599-edge39-label-profiles-v1\0")
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

    chamber_digest = sha256(b"diag3-row2599-edge39-chamber-label-digests-v1\0")
    for digest in chamber_digests:
        chamber_digest.update(bytes.fromhex(digest))
    event_digest = sha256(b"diag3-row2599-edge39-label-events-v1\0")
    for row in event_records:
        event_digest.update(row["event_index"].to_bytes(4, "little"))
        for factor_id in row["factor_ids"]:
            event_digest.update(factor_id.to_bytes(4, "little"))
        event_digest.update(row["lost_labels"].to_bytes(4, "little"))
        event_digest.update(bytes.fromhex(row["post_chamber_labels_sha256"]))

    record = {
        "format": FORMAT,
        "status": STATUS,
        "scope": {
            "parent_index": 2599,
            "source_edge_index": 39,
            "source_chart": 0,
            "target_chart": 113,
            "generic_chambers": chamber_count,
            "signature_label_continuation": "COMPLETE_ON_ALL_OPEN_PATH_CHAMBERS",
            "wall_label_specialization": "CONSERVATIVE_ALL_INCIDENT_CHAMBERS_RULE",
            "global_parent_cell_coverage": "NOT_CLAIMED",
            "honest_9dvl_score": "2/9",
        },
        "inputs": {
            "transition_path": str(TRANSITION.relative_to(HERE.parents[1])),
            "transition_sha256": EXPECTED_TRANSITION_SHA256,
            "factor_census_sha256": transition_core.file_sha256(transition_core.FACTOR_CENSUS),
            "point_bank_sha256": transition_core.file_sha256(transition_core.POINT_BANK),
        },
        "normalization": {
            "raw_extension_reorientation_mask": reorientation,
            "source_raw_normalized_label_sets_equal_after_reorientation": True,
        },
        "continuation": {
            "extension_signature_universe": len(universe),
            "labels_per_generic_chamber": EXPECTED_TOPE_COUNT,
            "ordered_event_groups": len(events),
            "simple_mutation_events": sum(simple_census.values()),
            "compound_or_tangential_reenumeration_events": sum(compound_delta.values()),
            "simple_preliminary_candidate_census": {str(key): value for key, value in sorted(simple_census.items())},
            "compound_delta_census": {
                f"occurrence_{'-'.join(map(str, occurrence))}:algebraic_{'-'.join(map(str, algebraic))}:lost_{lost}:gained_{gained}": count
                for (occurrence, algebraic, lost, gained), count in sorted(compound_delta.items())
            },
            "chart_113_raw_label_state_reconstructed": True,
            "chamber_label_digests_sha256": chamber_digest.hexdigest(),
            "event_label_semantic_sha256": event_digest.hexdigest(),
            "event_records": event_records,
        },
        "signature_profiles": {
            "artifact_path": str(PROFILE_OUTPUT.relative_to(HERE.parents[1])),
            "artifact_format": "D3E39P1 header; uint32 counts; then ascending (uint64 signature, packed chamber bitmap) rows; deterministic gzip mtime=0",
            "packed_profile_bytes_each": profile_bytes,
            "distinct_profiles": len(profile_counter),
            "semantic_sha256": profile_digest.hexdigest(),
            "feasible_chamber_count_census": {str(key): value for key, value in sorted(feasible_count_census.items())},
            "profile_transition_count_census": {str(key): value for key, value in sorted(transition_count_census.items())},
            "all_bad_loci_closed_by_incidence_rule": True,
        },
        "edge_interface": {
            "stable_edge_key": "row2599:edge:039:charts:0-113",
            "cell_id_prefix": "row2599:edge:039",
            "signature_order": "ascending unsigned 56-bit row-2599 extension signature",
            "profile_bits": "one bit per open chamber, increasing chamber index",
            "collar_attachment": roadmap["edge_interface"]["collar_attachment"],
        },
        "theorem_effect": "Completes exact label continuation on retained source-cover edge 39 and binds its factor-19069 event to the accepted collar; no coverage outside that segment/collar and no ledger promotion.",
    }
    return record, universe, profiles
