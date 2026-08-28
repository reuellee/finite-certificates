#!/usr/bin/env python3
"""Proof-producing exact source transition for retained edge 39 (charts 0--113).

This module is discovery/generation code.  Acceptance belongs to the independent
verifier track.  The public entry point is ``build_record``; its ``EDGE``
description is intentionally data-like so the same interface can later be
lifted into the labelled-skeleton compiler without changing cell semantics.
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
DATA = HERE / "data"
OUTPUT = DATA / "DIAG3_PAIR_PARENT_SOURCE_TRANSITION_EDGE39_0_113.json"
POINT_BANK = DATA / "seeat_parent2599_upper178.npz"
FACTOR_STATES = DATA / "DIAG9_GRAPH_row2599_factor_states.npz"
FACTOR_CENSUS = DATA / "DIAG9_GRAPH_global_factor_census.npz"
CANDIDATES = DATA / "DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin"
COVER = DATA / "DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json"
SKELETON = DATA / "DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON.json"
COLLAR = DATA / "DIAG3_PAIR_FULLSUPPORT_COMPONENT_COLLAR.json"
LEDGER = DATA / "DIAG3_RESEARCH_DECISION_LEDGER.json"

EDGE = {
    "edge_index": 39,
    "parent_index": 2599,
    "source_chart": 0,
    "target_chart": 113,
    "collar_factor_id": 19069,
}
ISOLATION_WIDTH = Fraction(1, 1 << 22)
FORMAT = "diag3-pair-parent-source-transition-edge-v2"
STATUS = "EXACT_EDGE39_SOURCE_TRANSITION_ROADMAP"

PINNED = {
    LEDGER: "b87172fb14dc440270436a440468ab4843939e7ac2894ecb266342c63a9025f0",
    COVER: "19248dd148d1fd002931ed5f48197869dd42c68a513376e1a4d6941389bda307",
    SKELETON: "5430bd79ae9ddee09ce9b393f018389be1210c250a7eb0d5486fab8e1294663d",
    COLLAR: "5930cc19019470fdfdf55d67523f6c4211ccf5b540f5c2bb5df36c64db75d7bd",
}

sys.path.insert(0, str(HERE))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402
import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def require_digest(path: Path, expected: str) -> None:
    if file_sha256(path) != expected:
        raise AssertionError(f"pinned input digest changed: {path.name}")


def canonical_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def semantic_seal(record) -> str:
    payload = deepcopy(record)
    payload.pop("semantic_sha256", None)
    return sha256(canonical_bytes(payload)).hexdigest()


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def primitive_univariate(coefficients):
    coefficients = list(map(Fraction, coefficients))
    while coefficients and not coefficients[-1]:
        coefficients.pop()
    if not coefficients:
        raise AssertionError("zero restricted factor")
    denominator = 1
    for value in coefficients:
        denominator = lcm(denominator, value.denominator)
    integer = [int(value * denominator) for value in coefficients]
    divisor = 0
    for value in integer:
        divisor = gcd(divisor, abs(value))
    integer = [value // max(divisor, 1) for value in integer]
    if integer[-1] < 0:
        integer = [-value for value in integer]
    return tuple(integer)


def derivative(polynomial):
    return tuple(index * coefficient for index, coefficient in enumerate(polynomial) if index)


def polynomial_gcd(left, right):
    left = sturm.trim(left)
    right = sturm.trim(right)
    while right:
        left, right = right, sturm.polynomial_divrem(left, right)
    if not left:
        return ()
    leading = left[-1]
    return tuple(value / leading for value in left)


def count_with_sequence(sequence, left, right):
    if any(sturm.polynomial_value(polynomial, left) == 0 for polynomial in sequence[:1]):
        raise AssertionError("root-isolation endpoint is a root")
    if any(sturm.polynomial_value(polynomial, right) == 0 for polynomial in sequence[:1]):
        raise AssertionError("root-isolation endpoint is a root")
    return sturm.sign_variations(sequence, left) - sturm.sign_variations(sequence, right)


def nonroot_split(polynomial, left, right):
    for numerator, denominator in ((1, 2), (1, 3), (2, 3), (2, 5), (3, 5), (1, 4), (3, 4)):
        middle = left + (right - left) * Fraction(numerator, denominator)
        if sturm.polynomial_value(polynomial, middle):
            return middle
    raise AssertionError("could not choose a rational nonroot split")


def isolate_roots(polynomial, width=ISOLATION_WIDTH):
    if not sturm.polynomial_value(polynomial, Fraction(0)) or not sturm.polynomial_value(polynomial, Fraction(1)):
        raise AssertionError("residual root occurs at a segment endpoint")
    sequence = sturm.sturm_sequence(polynomial)
    total = count_with_sequence(sequence, Fraction(0), Fraction(1))
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
        left_count = count_with_sequence(sequence, left, middle)
        right_count = count_with_sequence(sequence, middle, right)
        if left_count + right_count != count:
            raise AssertionError("Sturm subdivision lost a distinct root")
        stack.append((middle, right, right_count))
        stack.append((left, middle, left_count))
    return sorted(answer)


def refine_root(atom):
    polynomial = atom["_polynomial"]
    sequence = atom["_sequence"]
    left, right = atom["left"], atom["right"]
    middle = nonroot_split(polynomial, left, right)
    left_count = count_with_sequence(sequence, left, middle)
    right_count = count_with_sequence(sequence, middle, right)
    if (left_count, right_count) == (1, 0):
        atom["right"] = middle
    elif (left_count, right_count) == (0, 1):
        atom["left"] = middle
    else:
        raise AssertionError("isolated atom did not contain exactly one distinct root")


def root_multiplicity(polynomial, left, right):
    multiplicity = 1
    current = polynomial
    while len(current) > 1:
        common = polynomial_gcd(current, derivative(current))
        if len(common) <= 1 or not sturm.root_count(common, left, right):
            break
        multiplicity += 1
        current = common
    return multiplicity


def share_root(left_atom, right_atom):
    lower = max(left_atom["left"], right_atom["left"])
    upper = min(left_atom["right"], right_atom["right"])
    if lower >= upper:
        return False
    common = polynomial_gcd(left_atom["_polynomial"], right_atom["_polynomial"])
    return len(common) > 1 and sturm.root_count(common, lower, upper) == 1


def group_atoms(atoms):
    """Refine close boxes and group only roots proved equal by exact gcd."""
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

    rounds = 0
    while True:
        rounds += 1
        if rounds > 256:
            raise AssertionError("could not separate noncoincident algebraic roots")
        order = sorted(range(len(atoms)), key=lambda i: (atoms[i]["left"] + atoms[i]["right"]) / 2)
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

    grouped = {}
    for index, atom in enumerate(atoms):
        grouped.setdefault(find(index), []).append(atom)
    events = []
    for members in grouped.values():
        left = max(member["left"] for member in members)
        right = min(member["right"] for member in members)
        if left >= right:
            raise AssertionError("coincident root boxes have empty exact intersection")
        events.append({"left": left, "right": right, "members": members})
    events.sort(key=lambda event: (event["left"] + event["right"]) / 2)
    for left, right in zip(events, events[1:]):
        if left["right"] > right["left"]:
            raise AssertionError("ordered exact event boxes overlap")
    return events


def exact_inputs():
    with np.load(POINT_BANK, allow_pickle=False) as source:
        matrices = np.asarray(source["chart_matrix"], dtype=np.int64)
    if matrices.shape != (178, 4, 8):
        raise AssertionError("row-2599 point bank changed")
    points = tuple(gate.normalized_values(matrix.tolist()) for matrix in matrices)
    with np.load(FACTOR_STATES, allow_pickle=False) as source:
        packed = np.asarray(source["chart_factor_sign_packed"], dtype=np.uint8)
        hamming = np.asarray(source["chart_hamming"], dtype=np.int64)
    states = np.unpackbits(packed, axis=1, bitorder="little")[:, :26_740].astype(np.uint8)
    with np.load(FACTOR_CENSUS, allow_pickle=False) as source:
        multiplicity = np.asarray(source["factor_multiplicity"], dtype=np.int64)
    return matrices, points, states, hamming, multiplicity


def validate_collar(collar):
    selection = collar["target_selection"]
    component = collar["component_coverage"]
    if (
        int(selection["unique_edge_index"]) != EDGE["edge_index"]
        or tuple(map(int, selection["unique_edge_charts"])) != (EDGE["source_chart"], EDGE["target_chart"])
        or int(selection["factor_id"]) != EDGE["collar_factor_id"]
        or int(component["factor_id"]) != EDGE["collar_factor_id"]
        or component["meets_retained_source_skeleton"] is not True
        or component["retained_skeleton_cell"] != "w_zero"
    ):
        raise AssertionError("false factor-19069 collar attachment")


def run_canaries(points, parent_rows):
    results = {}
    edge_polynomial = safe.segment_power(parent_rows[0][2], points[0], points[113])
    target = parent_rows[0][1]
    if not safe.positive_unit([target * value for value in edge_polynomial]):
        raise AssertionError("positive parent canary setup failed")
    try:
        if not safe.positive_unit([-target * value for value in edge_polynomial]):
            raise AssertionError("signed parent flip rejected")
    except AssertionError:
        results["signed_parent_flip"] = "REJECTED"

    try:
        isolate_roots((-1, 1))
    except AssertionError:
        results["endpoint_root"] = "REJECTED"

    tangent = primitive_univariate((Fraction(1, 4), -1, 1))
    box = isolate_roots(tangent)[0]
    if root_multiplicity(tangent, *box) != 2:
        raise AssertionError("tangency canary was not detected")
    results["repeated_tangential_root"] = "DETECTED_MULTIPLICITY_2"

    left = {"left": Fraction(1, 3), "right": Fraction(2, 3), "_polynomial": (-1, 2), "_sequence": sturm.sturm_sequence((-1, 2))}
    right = {"left": Fraction(2, 5), "right": Fraction(3, 5), "_polynomial": (-2, 4), "_sequence": sturm.sturm_sequence((-2, 4))}
    if not share_root(left, right):
        raise AssertionError("coincident-factor canary was not grouped")
    results["coincident_factor_event"] = "GROUPED_BY_EXACT_GCD"

    try:
        require_digest(COLLAR, "0" * 64)
    except AssertionError:
        results["corrupted_input_digest"] = "REJECTED"

    false_collar = json.loads(COLLAR.read_text(encoding="utf-8"))
    false_collar["target_selection"]["factor_id"] = 19068
    try:
        validate_collar(false_collar)
    except AssertionError:
        results["false_collar_attachment"] = "REJECTED"
    if len(results) != 6:
        raise AssertionError("generator canary census incomplete")
    return results


def build_record(progress=False):
    for path, digest in PINNED.items():
        require_digest(path, digest)
    cover = json.loads(COVER.read_text(encoding="utf-8"))
    collar = json.loads(COLLAR.read_text(encoding="utf-8"))
    validate_collar(collar)
    selected = tuple(map(int, cover["source_bank"]["selected_edge_indices"]))
    selected_pairs = tuple(tuple(map(int, pair)) for pair in cover["source_bank"]["selected_chart_pairs"])
    if EDGE["edge_index"] not in selected or (0, 113) not in selected_pairs:
        raise AssertionError("edge 39 is no longer in the retained source cover")
    if tuple(safe.EDGES[EDGE["edge_index"]]) != (0, 113):
        raise AssertionError("edge-index-to-chart-pair map changed")

    matrices, points, states, hamming, occurrence_multiplicity = exact_inputs()
    records = [json.loads(line) for line in safe.CATALOG.read_text().splitlines() if line]
    parents, _unused = gate.parent_polynomials(records[EDGE["parent_index"]])
    parent_tensors = []
    for edge_label, target, polynomial, _terms in parents:
        restricted = safe.segment_power(polynomial, points[0], points[113])
        signed = [target * coefficient for coefficient in restricted]
        if not safe.positive_unit(signed):
            raise AssertionError(f"strict parent residence failed at {edge_label}")
        parent_tensors.append((edge_label, tuple(map(fraction_text, signed))))
    canaries = run_canaries(points, parents)

    candidates = gate.parse_candidates()
    _factor_types, _factor_terms, polynomials = labeled.factor_polynomials()
    root_count_census = Counter()
    atoms = []
    rooted = set()
    for candidate_index, factor_id in enumerate(candidates):
        polynomial = primitive_univariate(safe.segment_power(polynomials[factor_id], points[0], points[113]))
        intervals = isolate_roots(polynomial)
        root_count_census[len(intervals)] += 1
        if intervals:
            rooted.add(int(factor_id))
        sequence = sturm.sturm_sequence(polynomial)
        for root_index, (left, right) in enumerate(intervals):
            algebraic_multiplicity = root_multiplicity(polynomial, left, right)
            sign_flip = bool(algebraic_multiplicity & 1)
            if sign_flip != ((sturm.polynomial_value(polynomial, left) > 0) != (sturm.polynomial_value(polynomial, right) > 0)):
                raise AssertionError("root parity disagrees with endpoint signs")
            atoms.append({
                "factor_id": int(factor_id),
                "factor_degree": len(polynomial) - 1,
                "root_index_within_factor": root_index,
                "algebraic_multiplicity": algebraic_multiplicity,
                "occurrence_multiplicity": int(occurrence_multiplicity[factor_id]),
                "sign_flip": sign_flip,
                "left": left,
                "right": right,
                "_polynomial": polynomial,
                "_sequence": sequence,
            })
        if progress and (candidate_index + 1) % 2000 == 0:
            print(f"restricted {candidate_index + 1}/{len(candidates)} factors; atoms={len(atoms)}", flush=True)

    if root_count_census != Counter({0: 12_615, 1: 5_091, 2: 118}):
        raise AssertionError(f"edge-39 root census changed: {root_count_census}")
    if len(rooted) != 5_209 or len(atoms) != 5_327 or int(hamming[0, 113]) != 5_091:
        raise AssertionError("edge-39 endpoint/root census changed")

    grouped = group_atoms(atoms)
    event_rows = []
    tangent_members = 0
    coincident_groups = 0
    for event_index, group in enumerate(grouped):
        members = []
        for atom in sorted(group["members"], key=lambda row: (row["factor_id"], row["root_index_within_factor"])):
            tangent_members += int(not atom["sign_flip"])
            members.append({key: atom[key] for key in (
                "factor_id", "factor_degree", "root_index_within_factor",
                "algebraic_multiplicity", "occurrence_multiplicity", "sign_flip",
            )})
        coincident_groups += int(len(members) > 1)
        event_rows.append({
            "event_index": event_index,
            "isolating_interval": [fraction_text(group["left"]), fraction_text(group["right"])],
            "member_count": len(members),
            "crossing_occurrence_count": sum(row["occurrence_multiplicity"] for row in members if row["sign_flip"]),
            "compound_or_tangential": len(members) > 1 or any(row["occurrence_multiplicity"] > 1 or not row["sign_flip"] for row in members),
            "members": members,
        })

    state = states[0].copy()
    state_digest = sha256(b"diag3-row2599-edge39-factor-states-v1\0")
    state_digest.update(np.packbits(state, bitorder="little").tobytes())
    for event in event_rows:
        for member in event["members"]:
            if member["sign_flip"]:
                state[member["factor_id"]] ^= np.uint8(1)
        state_digest.update(np.packbits(state, bitorder="little").tobytes())
    if not np.array_equal(state, states[113]):
        raise AssertionError(f"ordered events miss {np.count_nonzero(state != states[113])} target factor states")

    collar_events = [event for event in event_rows if any(member["factor_id"] == 19069 for member in event["members"])]
    if len(collar_events) != 1:
        raise AssertionError("factor 19069 does not bind to exactly one edge-39 event")
    collar_box = tuple(map(Fraction, collar["exact_wall_graph"]["root_isolation"]["retained_segment_q_zero"]["isolating_interval"]))
    transition_box = tuple(map(Fraction, collar_events[0]["isolating_interval"]))
    if max(collar_box[0], transition_box[0]) >= min(collar_box[1], transition_box[1]):
        raise AssertionError("factor-19069 transition event does not intersect the accepted collar root box")

    event_digest = sha256(b"diag3-row2599-edge39-grouped-events-v1\0")
    for event in event_rows:
        for endpoint in map(Fraction, event["isolating_interval"]):
            event_digest.update(endpoint.numerator.to_bytes(32, "little", signed=True))
            event_digest.update(endpoint.denominator.to_bytes(32, "little"))
        for member in event["members"]:
            event_digest.update(member["factor_id"].to_bytes(4, "little"))
            event_digest.update(member["algebraic_multiplicity"].to_bytes(1, "little"))
            event_digest.update(member["occurrence_multiplicity"].to_bytes(2, "little"))

    occurrence_census = Counter(
        member["occurrence_multiplicity"]
        for event in event_rows for member in event["members"]
    )
    record = {
        "format": FORMAT,
        "status": STATUS,
        "scope": {
            **EDGE,
            "path": "straight segment in exact normalized (Delta^3)^3 coordinates",
            "parent_parameter_coverage": "COMPLETE_ON_CLOSED_SEGMENT",
            "residual_parameter_coverage": "COMPLETE_ON_OPEN_SEGMENT",
            "global_parent_cell_coverage": "NOT_CLAIMED",
            "components_outside_factor_19069_collar": "NOT_CLAIMED",
            "honest_9dvl_score": "2/9",
        },
        "inputs": {str(path.relative_to(HERE.parents[1])): digest for path, digest in PINNED.items()},
        "edge_interface": {
            "stable_edge_key": "row2599:edge:039:charts:0-113",
            "cell_id_prefix": "row2599:edge:039",
            "orientation": "chart_0_to_chart_113",
            "endpoint_factor_hamming_distance": int(hamming[0, 113]),
            "collar_attachment": {
                "factor_id": 19069,
                "event_index": collar_events[0]["event_index"],
                "collar_cell": "w_zero",
                "accepted_collar_root_box": list(map(fraction_text, collar_box)),
                "transition_root_box": list(map(fraction_text, transition_box)),
            },
        },
        "parent_residence": {
            "parent_bracket_count": len(parents),
            "strict_on_closed_segment": True,
            "exact_method": "rational restriction plus recursive Bernstein positivity",
            "signed_restriction_sha256": sha256(canonical_bytes(parent_tensors)).hexdigest(),
            "parent_infinity_subcomplex": [],
        },
        "residual_roadmap": {
            "candidate_factor_count": len(candidates),
            "factor_root_count_census": {str(key): value for key, value in sorted(root_count_census.items())},
            "rooted_factor_count": len(rooted),
            "root_atom_count": len(atoms),
            "ordered_event_group_count": len(event_rows),
            "coincident_event_group_count": coincident_groups,
            "tangential_root_member_count": tangent_members,
            "occurrence_multiplicity_census": {str(key): value for key, value in sorted(occurrence_census.items())},
            "isolation_width_ceiling": fraction_text(ISOLATION_WIDTH),
            "all_event_boxes_pairwise_ordered": True,
            "events_semantic_sha256": event_digest.hexdigest(),
            "factor_state_sequence_sha256": state_digest.hexdigest(),
            "target_factor_state_reconstructed": True,
            "events": event_rows,
        },
        "regular_cw_path": {
            "zero_cells": len(event_rows) + 2,
            "one_cells": len(event_rows) + 1,
            "strict_closure_pairs": 2 * (len(event_rows) + 1),
            "scope_endpoint_cells": ["row2599:chart:0", "row2599:chart:113"],
            "parent_infinity_subcomplex": [],
        },
        "generator_canaries": canaries,
        "theorem_effect": "Exact finite certificate on retained source-cover edge 39 and its accepted factor-19069 collar attachment only; no global coverage and no ledger promotion.",
    }
    record["semantic_sha256"] = semantic_seal(record)
    return record
