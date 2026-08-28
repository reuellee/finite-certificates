#!/usr/bin/env python3
"""Parameterized exact phase-A compiler for retained row-2599 source edges.

This is certificate-generation code, not acceptance logic.  It compiles the
root/event and strict-parent-residence frontier needed before the expensive
97,224-signature continuation.  Every degeneracy that changes path semantics
is explicit in the returned record: endpoint roots, identically-zero
restrictions, repeated/tangential roots, coincident factors, multi-root
factors, compound label events, orientation, and endpoint-state replay.
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
REPO = HERE.parents[1]
DATA = HERE / "data"
POINT_BANK = DATA / "seeat_parent2599_upper178.npz"
FACTOR_STATES = DATA / "DIAG9_GRAPH_row2599_factor_states.npz"
FACTOR_CENSUS = DATA / "DIAG9_GRAPH_global_factor_census.npz"
CANDIDATES = DATA / "DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin"
COVER = DATA / "DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json"
BASE_REVISION = "ec362dba8a912bc4749c004641aee2da0a88dc05"
ISOLATION_WIDTH = Fraction(1, 1 << 20)

PINNED = {
    POINT_BANK: "3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a",
    FACTOR_STATES: "f44b1fccfb4e61273aeceb8796a18098d82c48473e257556ce3d2a22f99b0bcf",
    FACTOR_CENSUS: "3984ce87e11fd59d804e59568177248e218cd1c7bb07aae0a9f9f746858728bc",
    CANDIDATES: "adb2e7257457f158e809450683c46fe7ecafdbdd4a7efdf9ac630e8a4f0fb03f",
    COVER: "19248dd148d1fd002931ed5f48197869dd42c68a513376e1a4d6941389bda307",
}

sys.path.insert(0, str(HERE))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402
import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


_INPUTS = None


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def semantic_seal(record) -> str:
    payload = deepcopy(record)
    payload.pop("semantic_sha256", None)
    return sha256(canonical_bytes(payload)).hexdigest()


def fraction_text(value: Fraction) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


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


def polynomial_gcd(left, right):
    left = sturm.trim(left)
    right = sturm.trim(right)
    while right:
        left, right = right, sturm.polynomial_divrem(left, right)
    if not left:
        return ()
    leading = left[-1]
    return tuple(value / leading for value in left)


def divide_at_root(polynomial, root: Fraction):
    """Divide a low-to-high polynomial by x-root, requiring zero remainder."""
    values = list(map(Fraction, polynomial))
    if len(values) <= 1:
        raise AssertionError("cannot deflate a constant")
    quotient = [Fraction(0)] * (len(values) - 1)
    quotient[-1] = values[-1]
    for index in range(len(quotient) - 2, -1, -1):
        quotient[index] = values[index + 1] + root * quotient[index + 1]
    remainder = values[0] + root * quotient[0]
    if remainder:
        raise AssertionError("nonroot endpoint deflation")
    return primitive(quotient)


def deflate_endpoints(polynomial):
    current = tuple(polynomial)
    multiplicities = {0: 0, 1: 0}
    for endpoint in (Fraction(0), Fraction(1)):
        while len(current) > 1 and sturm.polynomial_value(current, endpoint) == 0:
            multiplicities[int(endpoint)] += 1
            current = divide_at_root(current, endpoint)
    return current, multiplicities


def count_with_sequence(sequence, polynomial, left, right):
    if sturm.polynomial_value(polynomial, left) == 0:
        raise AssertionError("root-isolation left endpoint is a root")
    if sturm.polynomial_value(polynomial, right) == 0:
        raise AssertionError("root-isolation right endpoint is a root")
    return sturm.sign_variations(sequence, left) - sturm.sign_variations(sequence, right)


def nonroot_split(polynomial, left, right):
    for numerator, denominator in (
        (1, 2), (1, 3), (2, 3), (2, 5), (3, 5),
        (1, 4), (3, 4), (1, 5), (4, 5), (3, 7), (4, 7),
    ):
        middle = left + (right - left) * Fraction(numerator, denominator)
        if sturm.polynomial_value(polynomial, middle):
            return middle
    raise AssertionError("could not choose a rational nonroot split")


def isolate_roots(polynomial, width=ISOLATION_WIDTH):
    if len(polynomial) <= 1:
        return []
    if not sturm.polynomial_value(polynomial, Fraction(0)):
        raise AssertionError("undeflated source endpoint root")
    if not sturm.polynomial_value(polynomial, Fraction(1)):
        raise AssertionError("undeflated target endpoint root")
    sequence = sturm.sturm_sequence(polynomial)
    total = count_with_sequence(sequence, polynomial, Fraction(0), Fraction(1))
    stack = [(Fraction(0), Fraction(1), total)]
    answer = []
    while stack:
        left, right, count = stack.pop()
        if not count:
            continue
        if count == 1 and right - left <= width:
            answer.append((left, right))
            continue
        middle = nonroot_split(polynomial, left, right)
        left_count = count_with_sequence(sequence, polynomial, left, middle)
        right_count = count_with_sequence(sequence, polynomial, middle, right)
        if left_count + right_count != count:
            raise AssertionError("Sturm subdivision lost a distinct root")
        stack.append((middle, right, right_count))
        stack.append((left, middle, left_count))
    answer.sort()
    if len(answer) != total:
        raise AssertionError("isolated-root census mismatch")
    return answer


def root_multiplicity(polynomial, left, right):
    multiplicity = 1
    current = tuple(polynomial)
    while len(current) > 1:
        common = polynomial_gcd(current, derivative(current))
        if len(common) <= 1 or not sturm.root_count(common, left, right):
            break
        multiplicity += 1
        current = common
    return multiplicity


def refine_root(atom):
    middle = nonroot_split(atom["_polynomial"], atom["left"], atom["right"])
    left_count = count_with_sequence(
        atom["_sequence"], atom["_polynomial"], atom["left"], middle
    )
    right_count = count_with_sequence(
        atom["_sequence"], atom["_polynomial"], middle, atom["right"]
    )
    if (left_count, right_count) == (1, 0):
        atom["right"] = middle
    elif (left_count, right_count) == (0, 1):
        atom["left"] = middle
    else:
        raise AssertionError("isolated atom did not contain exactly one root")


def share_root(left_atom, right_atom):
    lower = max(left_atom["left"], right_atom["left"])
    upper = min(left_atom["right"], right_atom["right"])
    if lower >= upper:
        return False
    common = polynomial_gcd(left_atom["_polynomial"], right_atom["_polynomial"])
    return len(common) > 1 and sturm.root_count(common, lower, upper) == 1


def group_atoms(atoms):
    """Use interval refinement for order and exact gcd for coincidence."""
    parent = list(range(len(atoms)))

    def find(index):
        while parent[index] != index:
            parent[index] = parent[parent[index]]
            index = parent[index]
        return index

    def union(left, right):
        left, right = find(left), find(right)
        if left != right:
            parent[right] = left

    for _round in range(512):
        order = sorted(
            range(len(atoms)),
            key=lambda index: (atoms[index]["left"] + atoms[index]["right"]) / 2,
        )
        refined = False
        for left_index, right_index in zip(order, order[1:]):
            left, right = atoms[left_index], atoms[right_index]
            if left["right"] <= right["left"]:
                continue
            if share_root(left, right):
                union(left_index, right_index)
                continue
            refine_root(left)
            refine_root(right)
            refined = True
            break
        if not refined:
            break
    else:
        raise AssertionError("could not separate distinct algebraic roots")

    groups = {}
    for index, atom in enumerate(atoms):
        groups.setdefault(find(index), []).append(atom)
    events = []
    for members in groups.values():
        left = max(member["left"] for member in members)
        right = min(member["right"] for member in members)
        if left >= right:
            raise AssertionError("coincident root boxes have empty intersection")
        events.append({"left": left, "right": right, "members": members})
    events.sort(key=lambda event: (event["left"] + event["right"]) / 2)
    for left, right in zip(events, events[1:]):
        if left["right"] > right["left"]:
            raise AssertionError("ordered exact event boxes overlap")
    return events


def load_inputs():
    global _INPUTS
    if _INPUTS is not None:
        return _INPUTS
    for path, expected in PINNED.items():
        actual = file_sha256(path)
        if actual != expected:
            raise AssertionError(f"pinned input moved: {path.name}: {actual}")
    cover = json.loads(COVER.read_text(encoding="utf-8"))
    selected = tuple(
        (int(index), int(pair[0]), int(pair[1]))
        for index, pair in zip(
            cover["source_bank"]["selected_edge_indices"],
            cover["source_bank"]["selected_chart_pairs"],
            strict=True,
        )
    )
    if len(selected) != 40 or len({row[0] for row in selected}) != 40:
        raise AssertionError("selected 40-edge cover changed")
    for edge_index, source, target in selected:
        if tuple(safe.EDGES[edge_index]) != (source, target):
            raise AssertionError("edge-index/chart-pair map changed")
    with np.load(POINT_BANK, allow_pickle=False) as source:
        matrices = np.asarray(source["chart_matrix"], dtype=np.int64)
    if matrices.shape != (178, 4, 8):
        raise AssertionError("point-bank shape changed")
    points = tuple(gate.normalized_values(matrix.tolist()) for matrix in matrices)
    with np.load(FACTOR_STATES, allow_pickle=False) as source:
        packed = np.asarray(source["chart_factor_sign_packed"], dtype=np.uint8)
        hamming = np.asarray(source["chart_hamming"], dtype=np.int64)
    states = np.unpackbits(packed, axis=1, bitorder="little")[:, :26_740].astype(np.uint8)
    with np.load(FACTOR_CENSUS, allow_pickle=False) as source:
        occurrence_multiplicity = np.asarray(source["factor_multiplicity"], dtype=np.int64)
    records = [json.loads(line) for line in safe.CATALOG.read_text().splitlines() if line]
    parents, parent_source_digest = gate.parent_polynomials(records[2599])
    candidates = tuple(map(int, gate.parse_candidates()))
    _factor_types, _factor_terms, polynomials = labeled.factor_polynomials()
    if len(candidates) != 17_824:
        raise AssertionError("candidate-factor census changed")
    _INPUTS = {
        "selected": selected,
        "matrices": matrices,
        "points": points,
        "states": states,
        "hamming": hamming,
        "occurrence_multiplicity": occurrence_multiplicity,
        "parents": parents,
        "parent_source_digest": parent_source_digest,
        "candidates": candidates,
        "polynomials": polynomials,
    }
    return _INPUTS


def _public_member(atom):
    return {
        "factor_id": atom["factor_id"],
        "factor_degree": atom["factor_degree"],
        "root_index_within_factor": atom["root_index_within_factor"],
        "algebraic_multiplicity": atom["algebraic_multiplicity"],
        "occurrence_multiplicity": atom["occurrence_multiplicity"],
        "sign_flip": atom["sign_flip"],
    }


def compile_edge(edge_spec, include_events=False, progress=False):
    inputs = load_inputs()
    edge_index, source_chart, target_chart = map(int, edge_spec)
    if (edge_index, source_chart, target_chart) not in inputs["selected"]:
        raise AssertionError("requested edge is not in the pinned selected cover")

    points = inputs["points"]
    parent_rows = []
    parent_failures = []
    for label, target_sign, polynomial, _terms in inputs["parents"]:
        restricted = safe.segment_power(
            polynomial, points[source_chart], points[target_chart]
        )
        signed = tuple(target_sign * value for value in restricted)
        if not safe.positive_unit(signed):
            parent_failures.append(str(label))
        parent_rows.append((str(label), int(target_sign), tuple(map(fraction_text, signed))))

    root_count_census = Counter()
    degree_census = Counter()
    occurrence_census = Counter()
    endpoint_members = []
    identically_zero = []
    atoms = []
    rooted_factors = set()
    multi_root_factors = set()
    restriction_digest = sha256(b"diag3-generic-edge-restrictions-v1\0")
    candidates = inputs["candidates"]
    for candidate_index, factor_id in enumerate(candidates):
        polynomial = primitive(
            safe.segment_power(
                inputs["polynomials"][factor_id],
                points[source_chart],
                points[target_chart],
            )
        )
        restriction_digest.update(canonical_bytes([factor_id, polynomial]))
        if not polynomial:
            identically_zero.append(factor_id)
            root_count_census["identically_zero"] += 1
            continue
        degree_census[len(polynomial) - 1] += 1
        interior_polynomial, endpoint_multiplicities = deflate_endpoints(polynomial)
        for endpoint in (0, 1):
            algebraic_multiplicity = endpoint_multiplicities[endpoint]
            if algebraic_multiplicity:
                endpoint_members.append({
                    "endpoint": endpoint,
                    "factor_id": factor_id,
                    "factor_degree": len(polynomial) - 1,
                    "algebraic_multiplicity": algebraic_multiplicity,
                    "occurrence_multiplicity": int(inputs["occurrence_multiplicity"][factor_id]),
                    "sign_flip": bool(algebraic_multiplicity & 1),
                })
        intervals = isolate_roots(interior_polynomial)
        root_count_census[len(intervals)] += 1
        if intervals or any(endpoint_multiplicities.values()):
            rooted_factors.add(factor_id)
        if len(intervals) + sum(bool(value) for value in endpoint_multiplicities.values()) > 1:
            multi_root_factors.add(factor_id)
        sequence = sturm.sturm_sequence(interior_polynomial)
        for root_index, (left, right) in enumerate(intervals):
            algebraic_multiplicity = root_multiplicity(polynomial, left, right)
            left_sign = sturm.polynomial_value(polynomial, left) > 0
            right_sign = sturm.polynomial_value(polynomial, right) > 0
            sign_flip = bool(algebraic_multiplicity & 1)
            if sign_flip != (left_sign != right_sign):
                raise AssertionError("root parity disagrees with exact side signs")
            occurrence = int(inputs["occurrence_multiplicity"][factor_id])
            occurrence_census[occurrence] += 1
            atoms.append({
                "factor_id": factor_id,
                "factor_degree": len(polynomial) - 1,
                "root_index_within_factor": root_index,
                "algebraic_multiplicity": algebraic_multiplicity,
                "occurrence_multiplicity": occurrence,
                "sign_flip": sign_flip,
                "left": left,
                "right": right,
                "_polynomial": polynomial,
                "_sequence": sequence,
            })
        if progress and (candidate_index + 1) % 2_000 == 0:
            print(
                f"edge {edge_index}: {candidate_index + 1}/{len(candidates)} factors; atoms={len(atoms)}",
                flush=True,
            )

    events = group_atoms(atoms)
    event_rows = []
    coincident_events = 0
    coincident_distinct_factor_events = 0
    repeated_members = 0
    tangential_members = 0
    compound_events = 0
    simple_events = 0
    for event_index, event in enumerate(events):
        members = [_public_member(atom) for atom in sorted(
            event["members"],
            key=lambda row: (row["factor_id"], row["root_index_within_factor"]),
        )]
        distinct_factor_count = len({member["factor_id"] for member in members})
        is_compound = (
            len(members) > 1
            or any(member["algebraic_multiplicity"] > 1 for member in members)
            or any(member["occurrence_multiplicity"] > 1 for member in members)
        )
        coincident_events += int(len(members) > 1)
        coincident_distinct_factor_events += int(distinct_factor_count > 1)
        repeated_members += sum(member["algebraic_multiplicity"] > 1 for member in members)
        tangential_members += sum(not member["sign_flip"] for member in members)
        compound_events += int(is_compound)
        simple_events += int(not is_compound)
        event_rows.append({
            "event_index": event_index,
            "isolating_interval": [fraction_text(event["left"]), fraction_text(event["right"])],
            "member_count": len(members),
            "distinct_factor_count": distinct_factor_count,
            "compound_label_event": is_compound,
            "members": members,
        })

    topology = [
        {
            "event_index": event["event_index"],
            "members": event["members"],
        }
        for event in event_rows
    ]
    topology_digest = sha256(
        b"diag3-generic-edge-event-topology-v1\0" + canonical_bytes(topology)
    ).hexdigest()
    interval_digest = sha256(
        b"diag3-generic-edge-event-intervals-v1\0"
        + canonical_bytes([event["isolating_interval"] for event in event_rows])
    ).hexdigest()

    endpoint_blocked = bool(endpoint_members or identically_zero)
    state = inputs["states"][source_chart].copy()
    for event in event_rows:
        for member in event["members"]:
            if member["sign_flip"]:
                state[member["factor_id"]] ^= np.uint8(1)
    mismatch = int(np.count_nonzero(state != inputs["states"][target_chart]))
    state_status = "BLOCKED_BY_ENDPOINT_DEGENERACY" if endpoint_blocked else (
        "EXACT_TARGET_RECONSTRUCTED" if mismatch == 0 else "FAILED_TARGET_RECONSTRUCTION"
    )

    record = {
        "edge_index": edge_index,
        "source_chart": source_chart,
        "target_chart": target_chart,
        "stable_edge_key": f"row2599:edge:{edge_index:03d}:charts:{source_chart}-{target_chart}",
        "orientation": f"chart_{source_chart}_to_chart_{target_chart}",
        "parent_residence": {
            "parent_bracket_count": len(parent_rows),
            "strict_on_closed_oriented_segment": not parent_failures,
            "failed_parent_brackets": parent_failures,
            "signed_restrictions_sha256": sha256(
                b"diag3-generic-edge-parent-restrictions-v1\0" + canonical_bytes(parent_rows)
            ).hexdigest(),
            "parent_infinity_subcomplex": [],
        },
        "factor_census": {
            "candidate_factor_count": len(candidates),
            "degree_census": {str(key): value for key, value in sorted(degree_census.items())},
            "distinct_interior_root_count_per_factor_census": {
                str(key): value for key, value in sorted(root_count_census.items(), key=lambda row: str(row[0]))
            },
            "rooted_factor_count_including_endpoints": len(rooted_factors),
            "interior_root_atom_count": len(atoms),
            "multi_root_factor_count": len(multi_root_factors),
            "multi_root_factor_ids_sha256": sha256(
                b"diag3-generic-edge-multi-root-factors-v1\0"
                + canonical_bytes(sorted(multi_root_factors))
            ).hexdigest(),
            "identically_zero_factor_count": len(identically_zero),
            "identically_zero_factor_ids": identically_zero,
            "endpoint_root_member_count": len(endpoint_members),
            "endpoint_root_members": endpoint_members,
            "restricted_polynomials_sha256": restriction_digest.hexdigest(),
        },
        "event_census": {
            "ordered_event_group_count": len(event_rows),
            "simple_label_event_count": simple_events,
            "compound_label_event_count": compound_events,
            "coincident_event_group_count": coincident_events,
            "coincident_distinct_factor_event_count": coincident_distinct_factor_events,
            "repeated_root_member_count": repeated_members,
            "tangential_root_member_count": tangential_members,
            "occurrence_multiplicity_census": {
                str(key): value for key, value in sorted(occurrence_census.items())
            },
            "all_event_boxes_pairwise_ordered": True,
            "event_topology_sha256": topology_digest,
            "event_intervals_sha256": interval_digest,
        },
        "endpoint_state_replay": {
            "endpoint_factor_hamming_distance": int(inputs["hamming"][source_chart, target_chart]),
            "interior_odd_root_toggle_count": sum(
                member["sign_flip"] for event in event_rows for member in event["members"]
            ),
            "target_state_mismatch_count_after_interior_events": mismatch,
            "status": state_status,
        },
        "phase_b": {
            "generic_label_strategy": (
                "simplicial mutation at simple events; exact post-event tope re-enumeration "
                "at compound, repeated, tangential, or coincident events"
            ),
            "estimated_generic_chambers": len(event_rows) + 1,
            "profile_bitmap_materialized": False,
        },
    }
    if include_events:
        record["proof_producing_pilot_events"] = event_rows
    return record


def compile_edge_worker(edge_spec):
    return compile_edge(edge_spec, include_events=False, progress=False)


def selection_key(row):
    return (
        row["event_census"]["compound_label_event_count"],
        row["event_census"]["ordered_event_group_count"],
        row["factor_census"]["multi_root_factor_count"],
        row["edge_index"],
    )


def eligible_for_phase_b(row):
    return (
        row["parent_residence"]["strict_on_closed_oriented_segment"] is True
        and row["factor_census"]["identically_zero_factor_count"] == 0
        and row["factor_census"]["endpoint_root_member_count"] == 0
        and row["endpoint_state_replay"]["status"] == "EXACT_TARGET_RECONSTRUCTED"
        and row["event_census"]["all_event_boxes_pairwise_ordered"] is True
    )
