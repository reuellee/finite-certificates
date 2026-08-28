#!/usr/bin/env python3
"""Constructive exact prototype for retained row-2599 source-cover edge 39.

This is deliberately a prover-side prototype, not a standing verifier.  It
restricts all 17,824 accepted full-support residual factors to the exact
chart-0--chart-113 segment, isolates every real root on the closed segment,
orders the roots by disjoint rational boxes, reconstructs the endpoint factor
state, and attaches the already accepted factor-19069 collar incidence.
"""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import json
from math import gcd, lcm
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OMREAL = REPO / "ai" / "omreal"
DATA = OMREAL / "data"
OUTPUT = HERE / "EDGE39_EXACT_ROADMAP.json"

POINT_BANK = DATA / "seeat_parent2599_upper178.npz"
FACTOR_STATES = DATA / "DIAG9_GRAPH_row2599_factor_states.npz"
FACTOR_CENSUS = DATA / "DIAG9_GRAPH_global_factor_census.npz"
CANDIDATES = DATA / "DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin"
COVER = DATA / "DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json"
COLLAR = DATA / "DIAG3_PAIR_FULLSUPPORT_COMPONENT_COLLAR.json"
LEDGER = DATA / "DIAG3_RESEARCH_DECISION_LEDGER.json"

EXPECTED = {
    POINT_BANK: "3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a",
    FACTOR_STATES: "f44b1fccfb4e61273aeceb8796a18098d82c48473e257556ce3d2a22f99b0bcf",
    FACTOR_CENSUS: "3984ce87e11fd59d804e59568177248e218cd1c7bb07aae0a9f9f746858728bc",
    COVER: "19248dd148d1fd002931ed5f48197869dd42c68a513376e1a4d6941389bda307",
    COLLAR: "5930cc19019470fdfdf55d67523f6c4211ccf5b540f5c2bb5df36c64db75d7bd",
    LEDGER: "b87172fb14dc440270436a440468ab4843939e7ac2894ecb266342c63a9025f0",
    CANDIDATES: "adb2e7257457f158e809450683c46fe7ecafdbdd4a7efdf9ac630e8a4f0fb03f",
}

SOURCE_CHART = 0
TARGET_CHART = 113
EDGE_INDEX = 39
TARGET_FACTOR = 19_069
ISOLATION_WIDTH = Fraction(1, 1 << 48)

sys.path.insert(0, str(OMREAL))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402
import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fraction_text(value: Fraction) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def canonical_digest(value) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def primitive(coefficients) -> tuple[int, ...]:
    values = list(map(Fraction, coefficients))
    while values and not values[-1]:
        values.pop()
    if not values:
        return ()
    denominator = 1
    for value in values:
        denominator = lcm(denominator, value.denominator)
    integers = [int(value * denominator) for value in values]
    divisor = 0
    for value in integers:
        divisor = gcd(divisor, abs(value))
    integers = [value // max(divisor, 1) for value in integers]
    if integers[-1] < 0:
        integers = [-value for value in integers]
    return tuple(integers)


def derivative(polynomial):
    return tuple(index * polynomial[index] for index in range(1, len(polynomial)))


def polynomial_gcd(left, right) -> tuple[int, ...]:
    left = list(map(Fraction, left))
    right = list(map(Fraction, right))
    while right:
        remainder = sturm.polynomial_divrem(left, right)
        left, right = right, remainder
    return primitive(left)


def squarefree(polynomial) -> bool:
    common = polynomial_gcd(polynomial, derivative(polynomial))
    return len(common) <= 1


def variations(sequence, value):
    signs = []
    for polynomial in sequence:
        evaluation = sturm.polynomial_value(polynomial, value)
        if evaluation:
            signs.append(1 if evaluation > 0 else -1)
    return sum(left != right for left, right in zip(signs, signs[1:]))


def cached_root_count(sequence, polynomial, left, right):
    if sturm.polynomial_value(polynomial, left) == 0:
        raise AssertionError("root-isolation left endpoint is a root")
    if sturm.polynomial_value(polynomial, right) == 0:
        raise AssertionError("root-isolation right endpoint is a root")
    return variations(sequence, left) - variations(sequence, right)


def nonroot_split(polynomial, left, right):
    for numerator, denominator in (
        (1, 2), (1, 3), (2, 3), (2, 5), (3, 5), (1, 4), (3, 4),
        (1, 5), (4, 5), (3, 7), (4, 7),
    ):
        middle = left + (right - left) * Fraction(numerator, denominator)
        if sturm.polynomial_value(polynomial, middle):
            return middle
    raise AssertionError("could not choose a rational nonroot split")


def isolate_roots(polynomial):
    sequence = sturm.sturm_sequence(polynomial)
    total = cached_root_count(sequence, polynomial, Fraction(0), Fraction(1))
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
        left_count = cached_root_count(sequence, polynomial, left, middle)
        right_count = cached_root_count(sequence, polynomial, middle, right)
        if left_count + right_count != count:
            raise AssertionError("Sturm subdivision lost a root")
        stack.append((middle, right, right_count))
        stack.append((left, middle, left_count))
    answer.sort()
    if len(answer) != total:
        raise AssertionError("root isolation census changed")
    return answer


def endpoint_roots(polynomial):
    return tuple(
        endpoint
        for endpoint in (Fraction(0), Fraction(1))
        if sturm.polynomial_value(polynomial, endpoint) == 0
    )


def validate_attachment(record, collar, restricted_polynomials):
    target = collar["target_selection"]
    if target["factor_id"] != TARGET_FACTOR:
        raise AssertionError("collar factor is not factor 19069")
    if target["unique_edge_index"] != EDGE_INDEX:
        raise AssertionError("collar does not attach to retained edge 39")
    if target["unique_edge_charts"] != [SOURCE_CHART, TARGET_CHART]:
        raise AssertionError("collar charts differ from the roadmap")
    if not collar["component_coverage"]["meets_retained_source_skeleton"]:
        raise AssertionError("collar no longer claims the retained hit")
    if collar["component_coverage"]["factor_id"] != TARGET_FACTOR:
        raise AssertionError("collar component factor differs from target")
    collar_root = collar["exact_wall_graph"]["root_isolation"]["retained_segment_q_zero"]
    collar_polynomial = tuple(collar_root["primitive_coefficients_low_to_high"])
    if collar_polynomial != restricted_polynomials[TARGET_FACTOR]:
        raise AssertionError("collar central restriction differs from edge-39 factor 19069")
    event_index = next(
        index
        for index, event in enumerate(record["events"])
        if event["factor_ids"] == [TARGET_FACTOR]
    )
    event = record["events"][event_index]
    left, right = map(Fraction, event["isolating_interval"])
    collar_left, collar_right = map(Fraction, collar_root["isolating_interval"])
    if max(left, collar_left) >= min(right, collar_right):
        raise AssertionError("factor-19069 roadmap and collar boxes are disjoint")
    return {
        "factor_id": TARGET_FACTOR,
        "event_index": event_index,
        "same_primitive_restriction": True,
        "roadmap_interval": event["isolating_interval"],
        "collar_interval": collar_root["isolating_interval"],
        "intervals_overlap": True,
    }


def exact_inputs():
    for path, expected in EXPECTED.items():
        actual = file_sha256(path)
        if actual != expected:
            raise AssertionError(f"pinned input moved: {path}: {actual}")
    with np.load(POINT_BANK, allow_pickle=False) as source:
        matrices = np.asarray(source["chart_matrix"], dtype=np.int64)
    points = tuple(gate.normalized_values(matrix.tolist()) for matrix in matrices)
    with np.load(FACTOR_STATES, allow_pickle=False) as source:
        packed = np.asarray(source["chart_factor_sign_packed"], dtype=np.uint8)
        hamming = np.asarray(source["chart_hamming"], dtype=np.int64)
    states = np.unpackbits(packed, axis=1, bitorder="little")[:, :26_740].astype(np.uint8)
    with np.load(FACTOR_CENSUS, allow_pickle=False) as source:
        multiplicity = np.asarray(source["factor_multiplicity"], dtype=np.int64)
    return points, states, hamming, multiplicity


def build_record():
    points, states, hamming, multiplicity = exact_inputs()
    cover = json.loads(COVER.read_text(encoding="utf-8"))
    collar = json.loads(COLLAR.read_text(encoding="utf-8"))
    selected_indices = cover["source_bank"]["selected_edge_indices"]
    selected_pairs = cover["source_bank"]["selected_chart_pairs"]
    selected = dict(zip(selected_indices, selected_pairs, strict=True))
    if selected.get(EDGE_INDEX) != [SOURCE_CHART, TARGET_CHART]:
        raise AssertionError("cover edge 39 is no longer chart 0 to chart 113")
    if safe.EDGES[EDGE_INDEX] != (SOURCE_CHART, TARGET_CHART):
        raise AssertionError("source edge bank index 39 moved")

    catalog = [json.loads(line) for line in safe.CATALOG.read_text().splitlines() if line]
    parents, _parent_digest = gate.parent_polynomials(catalog[2599])
    parent_rows = []
    for label, target, polynomial, _terms in parents:
        restricted = safe.segment_power(polynomial, points[SOURCE_CHART], points[TARGET_CHART])
        signed = [target * coefficient for coefficient in restricted]
        if not safe.positive_unit(signed):
            raise AssertionError(f"signed parent factor lost strict positivity: {label}")
        parent_rows.append([label, target, [fraction_text(value) for value in restricted]])

    candidates = gate.parse_candidates()
    _factor_types, _factor_terms, polynomials = labeled.factor_polynomials()
    root_count_census = Counter()
    degree_census = Counter()
    occurrence_census = Counter()
    endpoint_factor_ids = []
    repeated_factor_ids = []
    restricted_polynomials = {}
    events = []
    restriction_digest = sha256(b"edge39-restricted-factor-polynomials-v1\0")
    for factor_id in candidates:
        polynomial = primitive(
            safe.segment_power(
                polynomials[factor_id], points[SOURCE_CHART], points[TARGET_CHART]
            )
        )
        if not polynomial:
            raise AssertionError(f"identically zero restriction: factor {factor_id}")
        restricted_polynomials[factor_id] = polynomial
        degree_census[len(polynomial) - 1] += 1
        restriction_digest.update(int(factor_id).to_bytes(4, "little"))
        restriction_digest.update(len(polynomial).to_bytes(1, "little"))
        for coefficient in polynomial:
            size = max(1, (abs(coefficient).bit_length() + 8) // 8)
            encoded = coefficient.to_bytes(size, "little", signed=True)
            restriction_digest.update(len(encoded).to_bytes(2, "little"))
            restriction_digest.update(encoded)
        endpoints = endpoint_roots(polynomial)
        if endpoints:
            endpoint_factor_ids.append([int(factor_id), list(map(fraction_text, endpoints))])
            continue
        if not squarefree(polynomial):
            repeated_factor_ids.append(int(factor_id))
        intervals = isolate_roots(polynomial)
        root_count_census[len(intervals)] += 1
        for root_index, (left, right) in enumerate(intervals):
            left_value = sturm.polynomial_value(polynomial, left)
            right_value = sturm.polynomial_value(polynomial, right)
            sign_flip = (left_value > 0) != (right_value > 0)
            occurrence = int(multiplicity[factor_id])
            occurrence_census[occurrence] += 1
            events.append({
                "factor_ids": [int(factor_id)],
                "factor_degrees": [len(polynomial) - 1],
                "root_indices_within_factor": [root_index],
                "restricted_algebraic_multiplicities": [1],
                "factor_occurrence_multiplicities": [occurrence],
                "total_occurrence_multiplicity": occurrence,
                "isolating_interval": [fraction_text(left), fraction_text(right)],
                "sign_flips": [sign_flip],
            })

    if endpoint_factor_ids:
        raise AssertionError(f"actual endpoint roots found: {endpoint_factor_ids[:4]}")
    if repeated_factor_ids:
        raise AssertionError(f"actual repeated/tangential factors found: {repeated_factor_ids[:4]}")
    events.sort(key=lambda event: sum(map(Fraction, event["isolating_interval"])))
    overlaps = []
    for index, (left_event, right_event) in enumerate(zip(events, events[1:])):
        left_right = Fraction(left_event["isolating_interval"][1])
        right_left = Fraction(right_event["isolating_interval"][0])
        if left_right >= right_left:
            overlaps.append((index, index + 1))
    if overlaps:
        # At width 2^-48 an overlap is an exact unresolved ordering obligation,
        # never silently treated as a coincidence.
        raise AssertionError(f"unresolved/coincident event boxes: {overlaps[:8]}")
    if not all(event["sign_flips"] == [True] for event in events):
        raise AssertionError("non-crossing event survived squarefree gate")

    state = states[SOURCE_CHART].copy()
    state_digest = sha256(b"edge39-factor-state-sequence-v1\0")
    state_digest.update(np.packbits(state, bitorder="little").tobytes())
    for event in events:
        for factor_id in event["factor_ids"]:
            state[factor_id] ^= np.uint8(1)
        state_digest.update(np.packbits(state, bitorder="little").tobytes())
    if not np.array_equal(state, states[TARGET_CHART]):
        mismatch = int(np.count_nonzero(state != states[TARGET_CHART]))
        raise AssertionError(f"ordered roots miss {mismatch} endpoint factor signs")

    event_digest = canonical_digest(events)
    record = {
        "format": "edge39-exact-roadmap-prover-prototype-v1",
        "base_revision": "e8600495e70e6f5548cb0c73e0cfd2f33faacc0b",
        "scope": {
            "parent_index": 2599,
            "support": [15, 15, 15],
            "edge_index": EDGE_INDEX,
            "source_chart": SOURCE_CHART,
            "target_chart": TARGET_CHART,
            "candidate_factor_count": len(candidates),
            "closed_segment": ["0", "1"],
            "global_parent_cell_coverage": "NOT_CLAIMED",
            "wall_components_outside_collar": "NOT_CLAIMED",
            "pair_injectivity": "NOT_CLAIMED",
            "honest_9dvl_score": "2/9_UNCHANGED",
        },
        "inputs": {str(path.relative_to(REPO)): digest for path, digest in EXPECTED.items()},
        "parent_residence": {
            "signed_parent_factor_count": len(parent_rows),
            "strict_on_closed_segment": True,
            "method": "exact rational segment restriction and recursive Bernstein positivity",
            "signed_restrictions_sha256": canonical_digest(parent_rows),
            "parent_infinity_subcomplex": [],
        },
        "factor_census": {
            "degree_census": {str(k): v for k, v in sorted(degree_census.items())},
            "distinct_root_count_per_factor_census": {str(k): v for k, v in sorted(root_count_census.items())},
            "endpoint_root_factor_count": 0,
            "repeated_or_tangential_factor_count": 0,
            "coincident_different_factor_event_count": 0,
            "restricted_polynomials_sha256": restriction_digest.hexdigest(),
        },
        "roadmap": {
            "distinct_ordered_event_count": len(events),
            "rooted_factor_count": sum(value for key, value in root_count_census.items() if key),
            "isolation_width_ceiling": fraction_text(ISOLATION_WIDTH),
            "all_event_boxes_pairwise_disjoint_and_ordered": True,
            "all_roots_squarefree_sign_crossings": True,
            "event_occurrence_multiplicity_census": {str(k): v for k, v in sorted(occurrence_census.items())},
            "events_semantic_sha256": event_digest,
            "factor_state_sequence_sha256": state_digest.hexdigest(),
            "endpoint_factor_hamming_distance": int(hamming[SOURCE_CHART, TARGET_CHART]),
        },
        "events": events,
    }
    record["factor_19069_collar_attachment"] = validate_attachment(
        record, collar, restricted_polynomials
    )
    record["semantic_sha256"] = canonical_digest(record)
    return record, parents, points, restricted_polynomials, collar


def run_canaries(record, parents, points, restricted_polynomials, collar):
    first_label, first_target, first_polynomial, _terms = parents[0]
    first_restricted = safe.segment_power(
        first_polynomial, points[SOURCE_CHART], points[TARGET_CHART]
    )
    signed_parent_flip_rejected = not safe.positive_unit(
        [-first_target * coefficient for coefficient in first_restricted]
    )
    endpoint_detected = endpoint_roots((0, -1, 2)) == (Fraction(0),)
    tangent = (1, -4, 4)
    repeated_detected = (not squarefree(tangent)) and (
        (sturm.polynomial_value(tangent, Fraction(0)) > 0)
        == (sturm.polynomial_value(tangent, Fraction(1)) > 0)
    )
    coincident_detected = polynomial_gcd((-1, 2), (-1, 1, 2)) == (-1, 2)
    invented = deepcopy(collar)
    invented["target_selection"]["factor_id"] = TARGET_FACTOR + 1
    try:
        validate_attachment(record, invented, restricted_polynomials)
    except AssertionError:
        invented_attachment_rejected = True
    else:
        invented_attachment_rejected = False
    results = {
        "signed_parent_factor_flip_rejected": signed_parent_flip_rejected,
        "endpoint_root_detected": endpoint_detected,
        "repeated_tangential_root_detected": repeated_detected,
        "coincident_different_factors_detected": coincident_detected,
        "invented_factor_19069_collar_attachment_rejected": invented_attachment_rejected,
    }
    if not all(results.values()):
        raise AssertionError(f"canary failure: {results}")
    return results


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()
    if not (args.build or args.verify):
        args.build = args.verify = True
    record, parents, points, restricted_polynomials, collar = build_record()
    canaries = run_canaries(record, parents, points, restricted_polynomials, collar)
    record["canaries"] = canaries
    record["semantic_sha256"] = canonical_digest({k: v for k, v in record.items() if k != "semantic_sha256"})
    if args.build:
        OUTPUT.write_text(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n", encoding="utf-8")
        print("WROTE", OUTPUT.relative_to(REPO))
    if args.verify:
        stored = json.loads(OUTPUT.read_text(encoding="utf-8"))
        if stored != record:
            raise AssertionError("stored prover artifact differs from exact replay")
        print("PASS edge 39 exact full-factor roadmap prototype")
        print("PASS root census", record["factor_census"]["distinct_root_count_per_factor_census"])
        print("PASS ordered events", record["roadmap"]["distinct_ordered_event_count"])
        print("PASS occurrence census", record["roadmap"]["event_occurrence_multiplicity_census"])
        print("PASS factor 19069 collar event", record["factor_19069_collar_attachment"]["event_index"])
        print("PASS canaries", len(canaries), "/", len(canaries))
        print("SEMANTIC_SHA256", record["semantic_sha256"])


if __name__ == "__main__":
    main()
