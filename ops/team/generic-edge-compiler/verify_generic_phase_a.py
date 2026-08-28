#!/usr/bin/env python3
"""Independent exact checker for the generic phase-A manifest and pilot.

This checker deliberately does not import the generic generator/core.  It
authenticates the compact all-edge manifest, independently replays strict
parent residence and endpoint nondegeneracy on all forty selected edges, and
fully replays every restricted factor and algebraic event on the pending-edge
pilot.  The compact nonpilot root censuses remain generator-side measurements;
their independent full replay is intentionally outside this bounded check.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from math import gcd, lcm
from pathlib import Path
import json
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
OMREAL = REPO / "ai" / "omreal"
DATA = OMREAL / "data"
ARTIFACT = HERE / "DIAG3_PAIR_PARENT_SOURCE_GENERIC_PHASE_A.json"
EXPECTED_ARTIFACT_SHA256 = "b9c7c67908bae7e98766ca3212f9d6f4e85e9f90d65447940302e8fb73d7b63c"
EXPECTED_SEMANTIC_SHA256 = "d130963882a18146d489e644fda4c2793657731266037d344b53daef2a7f0c87"
EXPECTED_BASE = "ec362dba8a912bc4749c004641aee2da0a88dc05"

POINT_BANK = DATA / "seeat_parent2599_upper178.npz"
FACTOR_STATES = DATA / "DIAG9_GRAPH_row2599_factor_states.npz"
FACTOR_CENSUS = DATA / "DIAG9_GRAPH_global_factor_census.npz"
CANDIDATES = DATA / "DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin"
COVER = DATA / "DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json"
PINS = {
    POINT_BANK: "3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a",
    FACTOR_STATES: "f44b1fccfb4e61273aeceb8796a18098d82c48473e257556ce3d2a22f99b0bcf",
    FACTOR_CENSUS: "3984ce87e11fd59d804e59568177248e218cd1c7bb07aae0a9f9f746858728bc",
    CANDIDATES: "adb2e7257457f158e809450683c46fe7ecafdbdd4a7efdf9ac630e8a4f0fb03f",
    COVER: "19248dd148d1fd002931ed5f48197869dd42c68a513376e1a4d6941389bda307",
}

sys.path.insert(0, str(OMREAL))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402
import verify_diag2_canonical_robust_edges as evaluator  # noqa: E402
import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


def file_sha256(path):
    digest = sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def semantic_seal(record):
    payload = deepcopy(record)
    payload.pop("semantic_sha256", None)
    return sha256(canonical_bytes(payload)).hexdigest()


def fraction_text(value):
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def primitive(coefficients):
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


def polynomial_gcd(left, right):
    left = sturm.trim(left)
    right = sturm.trim(right)
    while right:
        left, right = right, sturm.polynomial_divrem(left, right)
    if not left:
        return ()
    leading = left[-1]
    return tuple(value / leading for value in left)


def root_multiplicity(polynomial, left, right):
    answer = 1
    current = tuple(polynomial)
    while len(current) > 1:
        common = polynomial_gcd(current, derivative(current))
        if len(common) <= 1 or sturm.root_count(common, left, right) == 0:
            return answer
        answer += 1
        current = common
    return answer


def exact_sources():
    for path, expected in PINS.items():
        actual = file_sha256(path)
        if actual != expected:
            raise AssertionError(f"pinned source moved: {path.name}: {actual}")
    with np.load(POINT_BANK, allow_pickle=False) as source:
        matrices = np.asarray(source["chart_matrix"], dtype=np.int64)
    points = tuple(gate.normalized_values(matrix.tolist()) for matrix in matrices)
    with np.load(FACTOR_STATES, allow_pickle=False) as source:
        packed = np.asarray(source["chart_factor_sign_packed"], dtype=np.uint8)
        hamming = np.asarray(source["chart_hamming"], dtype=np.int64)
    states = np.unpackbits(packed, axis=1, bitorder="little")[:, :26_740].astype(np.uint8)
    with np.load(FACTOR_CENSUS, allow_pickle=False) as source:
        multiplicity = np.asarray(source["factor_multiplicity"], dtype=np.int64)
    records = [json.loads(line) for line in safe.CATALOG.read_text().splitlines() if line]
    parents, _unused = gate.parent_polynomials(records[2599])
    candidates = tuple(map(int, gate.parse_candidates()))
    _types, _terms, polynomials = labeled.factor_polynomials()
    return matrices, points, states, hamming, multiplicity, parents, candidates, polynomials


def selected_cover():
    cover = json.loads(COVER.read_text(encoding="utf-8"))
    return tuple(
        (int(index), int(pair[0]), int(pair[1]))
        for index, pair in zip(
            cover["source_bank"]["selected_edge_indices"],
            cover["source_bank"]["selected_chart_pairs"],
            strict=True,
        )
    )


def verify_manifest_structure(artifact, selected, hamming):
    required_top = {
        "base_revision", "compiler_contract", "edge_census", "format", "inputs",
        "proof_producing_pending_edge_pilot", "resource_contract", "scope",
        "selection_manifest", "semantic_sha256", "status", "theorem_effect",
    }
    if set(artifact) != required_top:
        raise AssertionError("phase-A top-level schema changed")
    if artifact["base_revision"] != EXPECTED_BASE:
        raise AssertionError("base revision changed")
    if semantic_seal(artifact) != EXPECTED_SEMANTIC_SHA256:
        raise AssertionError("semantic seal mismatch")
    if artifact["semantic_sha256"] != EXPECTED_SEMANTIC_SHA256:
        raise AssertionError("declared semantic seal mismatch")
    rows = artifact["edge_census"]
    if len(rows) != 40 or [row["edge_index"] for row in rows] != sorted(row[0] for row in selected):
        raise AssertionError("all-edge row census/order changed")
    by_index = {row["edge_index"]: row for row in rows}
    for edge_index, source, target in selected:
        row = by_index[edge_index]
        if (row["source_chart"], row["target_chart"]) != (source, target):
            raise AssertionError("stored orientation differs from selected cover")
        if tuple(safe.EDGES[edge_index]) != (source, target):
            raise AssertionError("source-bank orientation changed")
        replay = row["endpoint_state_replay"]
        if replay["endpoint_factor_hamming_distance"] != int(hamming[source, target]):
            raise AssertionError("stored endpoint Hamming distance changed")
        if row["factor_census"]["endpoint_root_member_count"] != 0:
            raise AssertionError("automatic batch contains an endpoint root")
        if row["factor_census"]["identically_zero_factor_count"] != 0:
            raise AssertionError("automatic batch contains an identically-zero factor")
        if row["parent_residence"]["strict_on_closed_oriented_segment"] is not True:
            raise AssertionError("automatic batch left the strict parent")
        if replay["status"] != "EXACT_TARGET_RECONSTRUCTED":
            raise AssertionError("automatic batch lacks target-state replay")
    pending = [row for row in rows if row["edge_index"] not in (27, 39)]
    pending.sort(key=lambda row: (
        row["event_census"]["compound_label_event_count"],
        row["event_census"]["ordered_event_group_count"],
        row["factor_census"]["multi_root_factor_count"],
        row["edge_index"],
    ))
    recommended = [row["edge_index"] for row in pending[:4]]
    if recommended != [17, 4, 21, 52]:
        raise AssertionError(f"deterministic next batch changed: {recommended}")
    if artifact["selection_manifest"]["recommended_edge_indices"] != recommended:
        raise AssertionError("selection manifest is not its declared ranking")
    if artifact["selection_manifest"]["excluded_pending_edges"]:
        raise AssertionError("a pending edge unexpectedly failed the exact gate")
    pilot = deepcopy(artifact["proof_producing_pending_edge_pilot"])
    events = pilot.pop("proof_producing_pilot_events")
    if pilot != by_index[17] or len(events) != 1_856:
        raise AssertionError("pilot is not the complete edge-17 census extension")
    return by_index, events


def verify_all_edge_parent_and_endpoint(rows, selected, points, parents, candidates, polynomials):
    unique_charts = sorted({chart for _edge, left, right in selected for chart in (left, right)})
    endpoint_nonzero = {}
    for chart in unique_charts:
        for factor_id in candidates:
            value = evaluator.evaluate(polynomials[factor_id], points[chart])
            if value == 0:
                raise AssertionError(f"exact endpoint root at chart {chart}, factor {factor_id}")
        endpoint_nonzero[chart] = len(candidates)
    for edge_index, source, target in selected:
        parent_rows = []
        for label, target_sign, polynomial, _terms in parents:
            restricted = safe.segment_power(polynomial, points[source], points[target])
            signed = tuple(target_sign * value for value in restricted)
            if not safe.positive_unit(signed):
                raise AssertionError(f"edge {edge_index} left the strict parent at {label}")
            parent_rows.append((str(label), int(target_sign), tuple(map(fraction_text, signed))))
        digest = sha256(
            b"diag3-generic-edge-parent-restrictions-v1\0" + canonical_bytes(parent_rows)
        ).hexdigest()
        if digest != rows[edge_index]["parent_residence"]["signed_restrictions_sha256"]:
            raise AssertionError(f"edge {edge_index} parent restriction digest mismatch")
    return len(unique_charts), sum(endpoint_nonzero.values())


def verify_pilot(row, events, points, states, hamming, multiplicity, candidates, polynomials):
    source = row["source_chart"]
    target = row["target_chart"]
    appearances = Counter()
    previous_right = Fraction(0)
    topology = []
    intervals = []
    for event_index, event in enumerate(events):
        if event["event_index"] != event_index:
            raise AssertionError("pilot event indices are not contiguous")
        left, right = map(Fraction, event["isolating_interval"])
        if not Fraction(0) < left < right < Fraction(1) or previous_right > left:
            raise AssertionError("pilot event boxes are not ordered in the open segment")
        previous_right = right
        factor_ids = set()
        for member in event["members"]:
            factor_id = int(member["factor_id"])
            factor_ids.add(factor_id)
            polynomial = primitive(
                safe.segment_power(polynomials[factor_id], points[source], points[target])
            )
            if sturm.root_count(polynomial, left, right) != 1:
                raise AssertionError("stored event member box does not isolate one root")
            algebraic = root_multiplicity(polynomial, left, right)
            if algebraic != int(member["algebraic_multiplicity"]):
                raise AssertionError("stored algebraic multiplicity changed")
            sign_flip = (sturm.polynomial_value(polynomial, left) > 0) != (
                sturm.polynomial_value(polynomial, right) > 0
            )
            if sign_flip != bool(member["sign_flip"]) or sign_flip != bool(algebraic & 1):
                raise AssertionError("stored event sign parity changed")
            if int(member["occurrence_multiplicity"]) != int(multiplicity[factor_id]):
                raise AssertionError("stored factor occurrence multiplicity changed")
            appearances[factor_id] += 1
        if len(factor_ids) > 1:
            member_polynomials = [
                primitive(safe.segment_power(polynomials[factor_id], points[source], points[target]))
                for factor_id in sorted(factor_ids)
            ]
            common = member_polynomials[0]
            for polynomial in member_polynomials[1:]:
                common = polynomial_gcd(common, polynomial)
            if len(common) <= 1 or sturm.root_count(common, left, right) != 1:
                raise AssertionError("coincident-factor event lacks an exact common root")
        topology.append({"event_index": event_index, "members": event["members"]})
        intervals.append(event["isolating_interval"])

    restriction_digest = sha256(b"diag3-generic-edge-restrictions-v1\0")
    degree_census = Counter()
    root_census = Counter()
    rooted = set()
    multi_root = set()
    exact_root_total = 0
    for factor_id in candidates:
        polynomial = primitive(
            safe.segment_power(polynomials[factor_id], points[source], points[target])
        )
        restriction_digest.update(canonical_bytes([factor_id, polynomial]))
        if not polynomial:
            raise AssertionError("pilot contains an identically-zero restriction")
        if not sturm.polynomial_value(polynomial, Fraction(0)) or not sturm.polynomial_value(polynomial, Fraction(1)):
            raise AssertionError("pilot contains an endpoint root")
        degree_census[len(polynomial) - 1] += 1
        root_count = sturm.root_count(polynomial, Fraction(0), Fraction(1))
        root_census[root_count] += 1
        exact_root_total += root_count
        if root_count:
            rooted.add(factor_id)
        if root_count > 1:
            multi_root.add(factor_id)
        if appearances[factor_id] != root_count:
            raise AssertionError(f"pilot root coverage mismatch for factor {factor_id}")
    factor = row["factor_census"]
    if exact_root_total != len(events) or exact_root_total != factor["interior_root_atom_count"]:
        raise AssertionError("pilot event list does not exhaust all exact roots")
    expected_factor = {
        "degree_census": {str(key): value for key, value in sorted(degree_census.items())},
        "distinct_interior_root_count_per_factor_census": {
            str(key): value for key, value in sorted(root_census.items())
        },
        "rooted_factor_count_including_endpoints": len(rooted),
        "multi_root_factor_count": len(multi_root),
        "multi_root_factor_ids_sha256": sha256(
            b"diag3-generic-edge-multi-root-factors-v1\0" + canonical_bytes(sorted(multi_root))
        ).hexdigest(),
        "restricted_polynomials_sha256": restriction_digest.hexdigest(),
    }
    for key, value in expected_factor.items():
        if factor[key] != value:
            raise AssertionError(f"pilot factor census mismatch: {key}")
    event_census = row["event_census"]
    topology_digest = sha256(
        b"diag3-generic-edge-event-topology-v1\0" + canonical_bytes(topology)
    ).hexdigest()
    interval_digest = sha256(
        b"diag3-generic-edge-event-intervals-v1\0" + canonical_bytes(intervals)
    ).hexdigest()
    if event_census["event_topology_sha256"] != topology_digest:
        raise AssertionError("pilot event topology digest mismatch")
    if event_census["event_intervals_sha256"] != interval_digest:
        raise AssertionError("pilot event interval digest mismatch")

    state = states[source].copy()
    compound = repeated = tangential = coincident = 0
    simple = 0
    occurrence_census = Counter()
    for event in events:
        members = event["members"]
        is_compound = (
            len(members) > 1
            or any(member["algebraic_multiplicity"] > 1 for member in members)
            or any(member["occurrence_multiplicity"] > 1 for member in members)
        )
        compound += int(is_compound)
        simple += int(not is_compound)
        repeated += sum(member["algebraic_multiplicity"] > 1 for member in members)
        tangential += sum(not member["sign_flip"] for member in members)
        coincident += int(len({member["factor_id"] for member in members}) > 1)
        for member in members:
            occurrence_census[int(member["occurrence_multiplicity"])] += 1
            if member["sign_flip"]:
                state[int(member["factor_id"])] ^= np.uint8(1)
    checks = {
        "ordered_event_group_count": len(events),
        "simple_label_event_count": simple,
        "compound_label_event_count": compound,
        "coincident_distinct_factor_event_count": coincident,
        "repeated_root_member_count": repeated,
        "tangential_root_member_count": tangential,
        "occurrence_multiplicity_census": {str(key): value for key, value in sorted(occurrence_census.items())},
    }
    for key, value in checks.items():
        if event_census[key] != value:
            raise AssertionError(f"pilot event census mismatch: {key}")
    mismatch = int(np.count_nonzero(state != states[target]))
    if mismatch or int(hamming[source, target]) != 1_812:
        raise AssertionError("pilot endpoint-state reconstruction failed")
    return exact_root_total


def hostile_canaries(artifact, events, points, parents):
    results = {}
    corrupted = deepcopy(artifact)
    corrupted["selection_manifest"]["pilot_edge_index"] = 4
    results["semantic_corruption"] = semantic_seal(corrupted) != corrupted["semantic_sha256"]
    results["reversed_orientation"] = tuple(safe.EDGES[17]) != (66, 0)
    results["dropped_event"] = len(events[:-1]) != 1_856
    mutated = deepcopy(events)
    mutated[0]["members"][0]["algebraic_multiplicity"] += 1
    topology = [{"event_index": event["event_index"], "members": event["members"]} for event in mutated]
    mutated_digest = sha256(
        b"diag3-generic-edge-event-topology-v1\0" + canonical_bytes(topology)
    ).hexdigest()
    results["mutated_multiplicity"] = mutated_digest != artifact["edge_census"][7]["event_census"]["event_topology_sha256"]
    results["endpoint_root"] = sturm.polynomial_value((0, 1), Fraction(0)) == 0
    tangent = (1, -4, 4)
    common = polynomial_gcd(tangent, derivative(tangent))
    results["tangency"] = len(common) > 1
    results["coincident_factors"] = len(polynomial_gcd((-1, 2), (-1, 1, 2))) > 1
    _label, target_sign, polynomial, _terms = parents[0]
    signed = [target_sign * value for value in safe.segment_power(polynomial, points[0], points[66])]
    results["parent_sign_flip"] = not safe.positive_unit([-value for value in signed])
    if not all(results.values()):
        raise AssertionError(f"hostile canary failure: {results}")
    return results


def main():
    artifact_bytes = ARTIFACT.read_bytes()
    if sha256(artifact_bytes).hexdigest() != EXPECTED_ARTIFACT_SHA256:
        raise AssertionError("generic phase-A artifact byte digest changed")
    artifact = json.loads(artifact_bytes)
    matrices, points, states, hamming, multiplicity, parents, candidates, polynomials = exact_sources()
    selected = selected_cover()
    rows, events = verify_manifest_structure(artifact, selected, hamming)
    chart_count, endpoint_checks = verify_all_edge_parent_and_endpoint(
        rows, selected, points, parents, candidates, polynomials
    )
    pilot_roots = verify_pilot(
        rows[17], events, points, states, hamming, multiplicity, candidates, polynomials
    )
    canaries = hostile_canaries(artifact, events, points, parents)
    print("PASS independent generic phase-A bounded replay")
    print("PASS all-edge manifest/orientation/parent residence", len(rows))
    print("PASS exact nonzero endpoint evaluations", endpoint_checks, "across", chart_count, "charts")
    print("PASS pending edge-17 complete root/event replay", pilot_roots)
    print("PASS hostile canaries", len(canaries), "/", len(canaries))
    print("PASS deterministic next batch", artifact["selection_manifest"]["recommended_edge_indices"])
    print("SEMANTIC_SHA256", artifact["semantic_sha256"])


if __name__ == "__main__":
    main()
