#!/usr/bin/env python3
"""Independent replay of the factor-19069 full-support component collar.

This verifier does not import the producer.  It reconstructs the target
selection, the exact two-parameter restrictions, every tensor-Bernstein
positivity certificate, three algebraic root isolations, and the signed
regular-CW incidence.  It then rejects re-sealed hostile semantic mutations.
"""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from math import comb, gcd, lcm
import json
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
CERTIFICATE = DATA / "DIAG3_PAIR_FULLSUPPORT_COMPONENT_COLLAR.json"
SEGMENT_COVER = DATA / "DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json"
FORMAT = "diag3-pair-fullsupport-component-collar-v1"
SEARCH_LIMIT = 24
ROOT_WIDTH = Fraction(1, 1 << 32)

sys.path.insert(0, str(HERE))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402
import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def hash_file(path: Path) -> str:
    state = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            state.update(block)
    return state.hexdigest()


def qtext(value):
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def json_hash(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def seal(record):
    payload = deepcopy(record)
    payload.pop("semantic_sha256", None)
    return json_hash(payload)


def trim(polynomial):
    return {key: value for key, value in polynomial.items() if value != 0}


def times_affine(polynomial, a, b, c):
    output = {}
    for powers, value in polynomial.items():
        for shift, scalar in (((0, 0), a), ((1, 0), b), ((0, 1), c)):
            if scalar == 0:
                continue
            key = (powers[0] + shift[0], powers[1] + shift[1])
            output[key] = output.get(key, Fraction()) + value * scalar
    return trim(output)


def substitute_square(polynomial, first, second, transverse_axis, radius):
    displacement = [right - left for left, right in zip(first, second, strict=True)]
    answer = {}
    for exponents, coefficient in polynomial.items():
        piece = {(0, 0): Fraction(coefficient)}
        for variable, exponent in enumerate(exponents):
            base = first[variable]
            transverse = Fraction()
            if variable == transverse_axis:
                base -= radius
                transverse = 2 * radius
            for _ in range(exponent):
                piece = times_affine(piece, base, displacement[variable], transverse)
        for key, value in piece.items():
            answer[key] = answer.get(key, Fraction()) + value
    return trim(answer)


def scalar_multiple(polynomial, multiplier):
    return trim({key: value * multiplier for key, value in polynomial.items()})


def s_derivative(polynomial):
    answer = {}
    for (s_power, r_power), value in polynomial.items():
        if s_power:
            answer[(s_power - 1, r_power)] = s_power * value
    return trim(answer)


def specialize(polynomial, variable, coordinate):
    answer = {}
    for (s_power, r_power), value in polynomial.items():
        if variable == "s":
            key, multiplier = (0, r_power), coordinate**s_power
        else:
            key, multiplier = (s_power, 0), coordinate**r_power
        answer[key] = answer.get(key, Fraction()) + value * multiplier
    return trim(answer)


def tensor_coefficients(polynomial):
    degree_s = max((key[0] for key in polynomial), default=0)
    degree_r = max((key[1] for key in polynomial), default=0)
    answer = []
    for i in range(degree_s + 1):
        row = []
        for j in range(degree_r + 1):
            value = Fraction()
            for (a, b), coefficient in polynomial.items():
                if a <= i and b <= j:
                    value += coefficient * Fraction(comb(i, a), comb(degree_s, a)) * Fraction(comb(j, b), comb(degree_r, b))
            row.append(value)
        answer.append(row)
    return degree_s, degree_r, answer


def tensor_summary(polynomial):
    degree_s, degree_r, tensor = tensor_coefficients(polynomial)
    flat = sum(tensor, [])
    encoded = [[qtext(value) for value in row] for row in tensor]
    return {
        "s_degree": degree_s,
        "r_degree": degree_r,
        "coefficient_count": len(flat),
        "minimum_coefficient": qtext(min(flat)),
        "coefficient_tensor_sha256": json_hash(encoded),
        "strictly_positive": min(flat) > 0,
    }


def gate_collar(parents, factor, first, second, axis, radius, emit=False):
    parent_summaries = []
    for label, target, parent, _terms in parents:
        summary = tensor_summary(
            scalar_multiple(
                substitute_square(parent, first, second, axis, radius), target
            )
        )
        if emit:
            parent_summaries.append(
                {"parent_bracket": label, "target_sign": target, **summary}
            )
        if not summary["strictly_positive"]:
            return None
    wall = substitute_square(factor, first, second, axis, radius)
    checks = {
        "negative_s_derivative": tensor_summary(
            scalar_multiple(s_derivative(wall), -1)
        ),
        "positive_s_zero_face": tensor_summary(specialize(wall, "s", 0)),
        "negative_s_one_face": tensor_summary(
            scalar_multiple(specialize(wall, "s", 1), -1)
        ),
    }
    if not all(row["strictly_positive"] for row in checks.values()):
        return None
    return (parent_summaries, wall, checks) if emit else True


def integer_polynomial(univariate):
    degree = max((key[0] for key in univariate), default=0)
    rational = [univariate.get((power, 0), Fraction()) for power in range(degree + 1)]
    while len(rational) > 1 and rational[-1] == 0:
        rational.pop()
    common_denominator = 1
    for value in rational:
        common_denominator = lcm(common_denominator, value.denominator)
    integer = [int(value * common_denominator) for value in rational]
    common_divisor = 0
    for value in integer:
        common_divisor = gcd(common_divisor, abs(value))
    integer = [value // max(common_divisor, 1) for value in integer]
    if integer[-1] < 0:
        integer = [-value for value in integer]
    return tuple(integer)


def exact_root_record(polynomial):
    integer = integer_polynomial(polynomial)
    require(sturm.root_count(integer, Fraction(0), Fraction(1)) == 1, "face root count")
    lo, hi = Fraction(0), Fraction(1)
    value_lo = sturm.polynomial_value(integer, lo)
    value_hi = sturm.polynomial_value(integer, hi)
    require(value_lo and value_hi and value_lo * value_hi < 0, "root endpoint signs")
    while hi - lo > ROOT_WIDTH:
        mid = (lo + hi) / 2
        value_mid = sturm.polynomial_value(integer, mid)
        if value_mid == 0:
            lo, hi = mid - ROOT_WIDTH / 4, mid + ROOT_WIDTH / 4
            break
        if value_lo * value_mid < 0:
            hi, value_hi = mid, value_mid
        else:
            lo, value_lo = mid, value_mid
    require(sturm.root_count(integer, lo, hi) == 1, "isolated root replay")
    return {
        "primitive_coefficients_low_to_high": list(integer),
        "isolating_interval": [qtext(lo), qtext(hi)],
        "left_sign": 1 if sturm.polynomial_value(integer, lo) > 0 else -1,
        "right_sign": 1 if sturm.polynomial_value(integer, hi) > 0 else -1,
    }


def independent_cell_replay():
    vertices = ["v00", "v10", "v11", "v01", "w_minus", "w_zero", "w_plus"]
    edges = [
        ("scope_bottom_left", "v00", "w_minus"),
        ("scope_bottom_right", "w_minus", "v10"),
        ("scope_right", "v10", "v11"),
        ("scope_top_left", "v01", "w_plus"),
        ("scope_top_right", "w_plus", "v11"),
        ("scope_left", "v00", "v01"),
        ("wall_lower", "w_minus", "w_zero"),
        ("wall_upper", "w_zero", "w_plus"),
    ]
    faces = ["positive_chamber", "negative_chamber"]
    face_vectors = {
        "positive_chamber": [1, 0, 0, -1, 0, -1, 1, 1],
        "negative_chamber": [0, 1, 1, 0, -1, 0, -1, -1],
    }
    d1 = []
    for vertex in vertices:
        d1.append([
            -1 if vertex == tail else 1 if vertex == head else 0
            for _name, tail, head in edges
        ])
    d2 = [[face_vectors[face][edge] for face in faces] for edge in range(len(edges))]
    product = np.asarray(d1, dtype=int) @ np.asarray(d2, dtype=int)
    require(not np.any(product), "independent d1*d2")
    oriented_edges = {name: [tail, head] for name, tail, head in edges}
    oriented_faces = {
        face: {
            edges[index][0]: coefficient
            for index, coefficient in enumerate(face_vectors[face])
            if coefficient
        }
        for face in faces
    }
    pairs, chains = set(), set()
    for edge, tail, head in edges:
        pairs.update(((tail, edge), (head, edge)))
    for face in faces:
        for edge in oriented_faces[face]:
            pairs.add((edge, face))
            tail, head = oriented_edges[edge]
            for vertex in (tail, head):
                pairs.add((vertex, face))
                chains.add((vertex, edge, face))
    boundary_edges = [name for name, _tail, _head in edges if name.startswith("scope_")]
    return {
        "cell_count_by_dimension": {"0": 7, "1": 8, "2": 2},
        "cell_ids_by_dimension": {"0": vertices, "1": [row[0] for row in edges], "2": faces},
        "oriented_edges": oriented_edges,
        "oriented_face_boundaries": oriented_faces,
        "strict_closure_pairs": [list(row) for row in sorted(pairs)],
        "strict_three_cell_chains": [list(row) for row in sorted(chains)],
        "boundary_matrix_d1": d1,
        "boundary_matrix_d2": d2,
        "d1_d2_zero": True,
        "factor_zero_subcomplex": ["w_minus", "w_zero", "w_plus", "wall_lower", "wall_upper"],
        "scope_boundary_subcomplex": [
            "v00", "v10", "v11", "v01", "w_minus", "w_plus", *boundary_edges
        ],
        "parent_infinity_subcomplex": [],
    }


def recompute():
    _matrices, points, _packed, signs, _hamming, _multiplicity = transition.exact_inputs()
    candidates = tuple(gate.parse_candidates())
    _types, _terms, factors = labeled.factor_polynomials()
    incidence = np.asarray(
        [[signs[left, factor] != signs[right, factor] for factor in candidates] for left, right in safe.EDGES],
        dtype=bool,
    )
    multiplicity = incidence.sum(axis=0)
    unique = np.where(multiplicity == 1)[0].tolist()
    ranked = []
    for candidate_index in unique:
        factor_id = candidates[candidate_index]
        polynomial = factors[factor_id]
        ranked.append((max(sum(monomial) for monomial in polynomial), len(polynomial), factor_id, candidate_index))
    degree, term_count, factor_id, candidate_index = max(ranked)
    edge_index = int(np.flatnonzero(incidence[:, candidate_index])[0])
    require((factor_id, edge_index, degree, term_count) == (19069, 39, 6, 108), "independent target selection")
    cover = json.loads(SEGMENT_COVER.read_text(encoding="utf-8"))
    require(edge_index in cover["source_bank"]["selected_edge_indices"], "retained target edge")
    records = [json.loads(line) for line in gate.CATALOG.read_text(encoding="utf-8").splitlines() if line]
    parents, parent_digest = gate.parent_polynomials(records[2599])
    left_chart, right_chart = safe.EDGES[edge_index]
    first, second = points[left_chart], points[right_chart]
    scan = []
    for axis in range(9):
        winner = None
        for exponent in range(SEARCH_LIMIT + 1):
            if gate_collar(parents, factors[factor_id], first, second, axis, Fraction(1, 1 << exponent)):
                winner = exponent
                break
        require(winner is not None, f"axis {axis} collar")
        scan.append({
            "axis": axis,
            "first_certified_exponent": winner,
            "largest_certified_tested_half_width": qtext(Fraction(1, 1 << winner)),
            "immediately_larger_width_certified": False if winner else None,
        })
    exponent, axis = min((row["first_certified_exponent"], row["axis"]) for row in scan)
    require((axis, exponent) == (4, 9), "independent collar selection")
    radius = Fraction(1, 1 << exponent)
    parent_rows, wall, wall_checks = gate_collar(
        parents, factors[factor_id], first, second, axis, radius, emit=True
    )
    direction = tuple(right - left for left, right in zip(first, second, strict=True))
    independent_coordinate = next(
        coordinate
        for coordinate, value in enumerate(direction)
        if coordinate != axis and value
    )
    central = specialize(wall, "r", Fraction(1, 2))
    roots = {
        "q_minus_endpoint": exact_root_record(specialize(wall, "r", 0)),
        "retained_segment_q_zero": exact_root_record(central),
        "q_plus_endpoint": exact_root_record(specialize(wall, "r", 1)),
    }
    sparse = [[a, b, qtext(value)] for (a, b), value in sorted(wall.items())]
    sources = {
        "point_bank_sha256": hash_file(transition.POINT_BANK),
        "factor_states_sha256": hash_file(transition.FACTOR_STATES),
        "factor_census_sha256": hash_file(transition.FACTOR_CENSUS),
        "candidate_factor_sha256": hash_file(transition.CANDIDATES),
        "parent_catalog_sha256": hash_file(gate.CATALOG),
        "segment_cover_sha256": hash_file(SEGMENT_COVER),
        "parent_sign_sha256": parent_digest,
    }
    return {
        "sources": sources,
        "target": {
            "rule": "maximize (total_degree, monomial_count, factor_id) among factors crossing exactly one of the 105 certified strict-parent segments",
            "unique_segment_factor_count": len(unique),
            "factor_id": factor_id,
            "total_degree": degree,
            "monomial_count": term_count,
            "unique_edge_index": edge_index,
            "unique_edge_charts": [left_chart, right_chart],
            "edge_is_in_optimal_40_edge_cover": True,
            "reason": "stress the missed-component method on the algebraically largest mandatory witness",
        },
        "collar": {
            "rule": "maximize the certified dyadic half-width 2^-n over coordinate axes, tie by least axis",
            "search_exponents": [0, SEARCH_LIMIT],
            "axis_scan": scan,
            "selected_axis": axis,
            "selected_half_width": qtext(radius),
            "larger_dyadic_width_fails_this_sufficient_gate": True,
            "affine_rank_witness": {
                "two_parameter_map_rank": 2,
                "transverse_axis": axis,
                "independent_source_direction_coordinate": independent_coordinate,
                "source_direction_value": qtext(direction[independent_coordinate]),
            },
        },
        "parent": {
            "method": "all tensor-Bernstein coefficients of every target-signed parent bracket are strictly positive on [0,1]^2",
            "parent_bracket_count": len(parent_rows),
            "aggregate_tensor_sha256": json_hash(
                [[row["parent_bracket"], row["target_sign"], row["coefficient_tensor_sha256"]] for row in parent_rows]
            ),
            "brackets": parent_rows,
        },
        "wall": {
            "restricted_wall_sparse_power_coefficients": sparse,
            "restricted_wall_sha256": json_hash(sparse),
            "positive_certificate_checks": wall_checks,
            "implications": {
                "strictly_decreasing_in_s": True,
                "positive_on_s_zero_face": True,
                "negative_on_s_one_face": True,
                "unique_root_for_every_r": True,
                "root_graph_homeomorphic_to_closed_interval": True,
            },
            "root_isolation": roots,
        },
        "complex": independent_cell_replay(),
    }


def verify_record(record, replay):
    require(record["semantic_sha256"] == seal(record), "semantic seal")
    require(record["format"] == FORMAT, "format")
    require(record["status"] == "EXACT_LOCAL_COMPONENT_COVERAGE_PILOT", "status")
    scope = record["scope"]
    require(scope == {
        "parent_index": 2599,
        "support": [15, 15, 15],
        "ambient_parameter_dimension": 9,
        "declared_pilot_dimension": 2,
        "parameterization": "x(s,r)=chart0+s(chart113-chart0)+(2r-1)e_4/512",
        "parameter_square": {"s": ["0", "1"], "r": ["0", "1"]},
        "strict_parent_scope_coverage": "COMPLETE_FOR_DECLARED_COLLAR",
        "global_parent_cell_coverage": "NOT_CLAIMED",
        "components_outside_declared_collar": "UNTESTED",
        "extension_signature_labels": "NOT_CONSTRUCTED",
        "pair_branch_closed": False,
        "triple_branch_closed": False,
        "honest_9dvl_score": "2/9",
    }, "scope and fail-closed limits")
    require(record["sources"] == replay["sources"], "source pins")
    require(record["target_selection"] == replay["target"], "target replay")
    require(record["collar_selection"] == replay["collar"], "collar replay")
    require(record["exact_parent_safety"] == replay["parent"], "parent Bernstein replay")
    require(record["exact_wall_graph"] == replay["wall"], "wall graph replay")
    require(record["regular_cw_roadmap"] == replay["complex"], "regular CW replay")
    component = record["component_coverage"]
    require(component == {
        "factor_id": 19069,
        "declared_scope_component_count": 1,
        "component_cell_ids": ["w_minus", "w_zero", "w_plus", "wall_lower", "wall_upper"],
        "meets_retained_source_skeleton": True,
        "retained_skeleton_cell": "w_zero",
        "meets_artificial_scope_boundary": ["w_minus", "w_plus"],
        "meets_parent_infinity": False,
        "negative_canary": "a second component, a skeleton miss, or a parent-infinity label must be rejected",
    }, "component semantics")
    require(record["decision"] == {
        "result": "LOCAL_COMPONENT_GATE_PASSES",
        "global_missed_component_gap": "OPEN",
        "next_action": "repeat on a declared factor family or construct a parent-cell roadmap with complete global component accounting",
        "theorem_effect": "No theorem-score promotion; the collar validates one exact full-support component-coverage contract only.",
    }, "decision scope")
    require(record["hostile_mutation_contract"] == [
        "target factor", "target edge", "collar width", "wall coefficient",
        "affine rank", "parent tensor", "extra component", "skeleton miss", "scope boundary",
        "false parent infinity", "global coverage", "extension labels", "incidence",
        "closure", "root isolation", "source digest", "score promotion",
    ], "mutation contract")


def reseal(record):
    record["semantic_sha256"] = seal(record)
    return record


def rejected(record, replay, label):
    try:
        verify_record(record, replay)
    except AssertionError:
        return
    raise AssertionError(f"hostile mutation accepted: {label}")


def hostile_tests(record, replay):
    mutations = []
    altered = deepcopy(record); altered["target_selection"]["factor_id"] = 8399; mutations.append((altered, "target factor"))
    altered = deepcopy(record); altered["target_selection"]["unique_edge_index"] = 38; mutations.append((altered, "target edge"))
    altered = deepcopy(record); altered["collar_selection"]["selected_half_width"] = "1/256"; mutations.append((altered, "collar width"))
    altered = deepcopy(record); altered["exact_wall_graph"]["restricted_wall_sparse_power_coefficients"][0][2] = "0"; mutations.append((altered, "wall coefficient"))
    altered = deepcopy(record); altered["collar_selection"]["affine_rank_witness"]["two_parameter_map_rank"] = 1; mutations.append((altered, "affine rank"))
    altered = deepcopy(record); altered["exact_parent_safety"]["brackets"][0]["coefficient_tensor_sha256"] = "0" * 64; mutations.append((altered, "parent tensor"))
    altered = deepcopy(record); altered["component_coverage"]["declared_scope_component_count"] = 2; mutations.append((altered, "extra component"))
    altered = deepcopy(record); altered["component_coverage"]["meets_retained_source_skeleton"] = False; mutations.append((altered, "skeleton miss"))
    altered = deepcopy(record); altered["regular_cw_roadmap"]["scope_boundary_subcomplex"].remove("w_plus"); mutations.append((altered, "scope boundary"))
    altered = deepcopy(record); altered["regular_cw_roadmap"]["parent_infinity_subcomplex"] = ["w_minus"]; mutations.append((altered, "false parent infinity"))
    altered = deepcopy(record); altered["scope"]["global_parent_cell_coverage"] = "CLAIMED"; mutations.append((altered, "global coverage"))
    altered = deepcopy(record); altered["scope"]["extension_signature_labels"] = "COMPLETE"; mutations.append((altered, "extension labels"))
    altered = deepcopy(record); altered["regular_cw_roadmap"]["boundary_matrix_d2"][0][0] *= -1; mutations.append((altered, "incidence"))
    altered = deepcopy(record); altered["regular_cw_roadmap"]["strict_closure_pairs"].pop(); mutations.append((altered, "closure"))
    altered = deepcopy(record); altered["exact_wall_graph"]["root_isolation"]["retained_segment_q_zero"]["isolating_interval"] = ["0", "1"]; mutations.append((altered, "root isolation"))
    altered = deepcopy(record); altered["sources"]["point_bank_sha256"] = "f" * 64; mutations.append((altered, "source digest"))
    altered = deepcopy(record); altered["scope"]["honest_9dvl_score"] = "3/9"; mutations.append((altered, "score promotion"))
    for altered, label in mutations:
        rejected(reseal(altered), replay, label)
    return len(mutations)


def main():
    record = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    replay = recompute()
    verify_record(record, replay)
    count = hostile_tests(record, replay)
    print("PASS independent target selection: factor 19069, mandatory edge 39")
    print("PASS 70 exact parent inequalities on the complete 2D collar")
    print("PASS unique monotone wall component, signed 17-cell CW roadmap, and d^2=0")
    print("PASS retained-skeleton hit; artificial boundary distinct from empty parent infinity")
    print("PASS", count, "re-sealed hostile semantic mutations rejected")
    print("SCOPE local full-support collar only; global missed-component gap open; honest 9DVL score 2/9")


if __name__ == "__main__":
    main()
