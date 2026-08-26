#!/usr/bin/env python3
"""Build an exact local component-coverage collar for full-support factor 19069.

The selected factor is the algebraically largest factor (degree, term count,
factor id) among factors witnessed on exactly one of the 105 certified
strict-parent source segments.  The certificate thickens that mandatory
segment to a rational two-dimensional collar and proves that the wall in the
entire collar is one monotone graph meeting both the retained segment and the
artificial collar boundary.

This is deliberately local.  It makes no claim about components elsewhere in
the nine-dimensional strict parent cell.
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
OUTPUT = DATA / "DIAG3_PAIR_FULLSUPPORT_COMPONENT_COLLAR.json"
SEGMENT_COVER = DATA / "DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json"
FORMAT = "diag3-pair-fullsupport-component-collar-v1"
TARGET_FACTOR = 19_069
TARGET_EDGE = 39
SEARCH_LIMIT = 24
ROOT_WIDTH = Fraction(1, 1 << 32)

sys.path.insert(0, str(HERE))
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


def clean(polynomial):
    return {key: value for key, value in polynomial.items() if value}


def multiply_affine(polynomial, constant, s_coefficient, r_coefficient):
    result = {}
    for (s_power, r_power), value in polynomial.items():
        for ds, dr, coefficient in (
            (0, 0, constant),
            (1, 0, s_coefficient),
            (0, 1, r_coefficient),
        ):
            if coefficient:
                key = (s_power + ds, r_power + dr)
                result[key] = result.get(key, Fraction()) + value * coefficient
    return clean(result)


def restrict_to_collar(polynomial, left, right, axis, epsilon):
    """Substitute x=left+s(right-left)+(2r-1)epsilon e_axis."""
    direction = tuple(b - a for a, b in zip(left, right, strict=True))
    result = {}
    for monomial, coefficient in polynomial.items():
        term = {(0, 0): Fraction(coefficient)}
        for variable, exponent in enumerate(monomial):
            constant = left[variable] - (epsilon if variable == axis else 0)
            r_coefficient = 2 * epsilon if variable == axis else Fraction()
            for _ in range(exponent):
                term = multiply_affine(
                    term, constant, direction[variable], r_coefficient
                )
        for key, value in term.items():
            result[key] = result.get(key, Fraction()) + value
    return clean(result)


def scale(polynomial, scalar):
    return clean({key: scalar * value for key, value in polynomial.items()})


def derivative_s(polynomial):
    return clean(
        {
            (s_power - 1, r_power): s_power * value
            for (s_power, r_power), value in polynomial.items()
            if s_power
        }
    )


def s_face(polynomial, coordinate):
    result = {}
    for (s_power, r_power), value in polynomial.items():
        key = (0, r_power)
        result[key] = result.get(key, Fraction()) + value * coordinate**s_power
    return clean(result)


def r_face(polynomial, coordinate):
    result = {}
    for (s_power, r_power), value in polynomial.items():
        key = (s_power, 0)
        result[key] = result.get(key, Fraction()) + value * coordinate**r_power
    return clean(result)


def bernstein_tensor(polynomial):
    s_degree = max((key[0] for key in polynomial), default=0)
    r_degree = max((key[1] for key in polynomial), default=0)
    tensor = []
    for i in range(s_degree + 1):
        row = []
        for j in range(r_degree + 1):
            value = Fraction()
            for (a, b), coefficient in polynomial.items():
                if a <= i and b <= j:
                    value += (
                        coefficient
                        * Fraction(comb(i, a), comb(s_degree, a))
                        * Fraction(comb(j, b), comb(r_degree, b))
                    )
            row.append(value)
        tensor.append(row)
    return s_degree, r_degree, tensor


def positivity_summary(polynomial):
    s_degree, r_degree, tensor = bernstein_tensor(polynomial)
    flat = [value for row in tensor for value in row]
    encoded = [[fraction_text(value) for value in row] for row in tensor]
    return {
        "s_degree": s_degree,
        "r_degree": r_degree,
        "coefficient_count": len(flat),
        "minimum_coefficient": fraction_text(min(flat)),
        "coefficient_tensor_sha256": canonical_digest(encoded),
        "strictly_positive": bool(flat and min(flat) > 0),
    }


def collar_gate(parents, wall, left, right, axis, epsilon, details=False):
    parent_rows = []
    for label, target, polynomial, _terms in parents:
        summary = positivity_summary(
            scale(restrict_to_collar(polynomial, left, right, axis, epsilon), target)
        )
        if details:
            parent_rows.append(
                {"parent_bracket": label, "target_sign": target, **summary}
            )
        if not summary["strictly_positive"]:
            return None
    restricted_wall = restrict_to_collar(wall, left, right, axis, epsilon)
    checks = {
        "negative_s_derivative": positivity_summary(
            scale(derivative_s(restricted_wall), -1)
        ),
        "positive_s_zero_face": positivity_summary(s_face(restricted_wall, 0)),
        "negative_s_one_face": positivity_summary(
            scale(s_face(restricted_wall, 1), -1)
        ),
    }
    if not all(row["strictly_positive"] for row in checks.values()):
        return None
    if not details:
        return True
    return parent_rows, restricted_wall, checks


def primitive_univariate(polynomial):
    degree = max((s_power for s_power, _r_power in polynomial), default=0)
    values = [polynomial.get((power, 0), Fraction()) for power in range(degree + 1)]
    while len(values) > 1 and not values[-1]:
        values.pop()
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


def isolate_monotone_root(polynomial):
    primitive = primitive_univariate(polynomial)
    if sturm.root_count(primitive, Fraction(0), Fraction(1)) != 1:
        raise AssertionError("collar wall face lost its unique root")
    left, right = Fraction(0), Fraction(1)
    left_value = sturm.polynomial_value(primitive, left)
    right_value = sturm.polynomial_value(primitive, right)
    if not left_value or not right_value or left_value * right_value >= 0:
        raise AssertionError("collar root lacks an endpoint sign change")
    while right - left > ROOT_WIDTH:
        middle = (left + right) / 2
        middle_value = sturm.polynomial_value(primitive, middle)
        if not middle_value:
            left = middle - ROOT_WIDTH / 4
            right = middle + ROOT_WIDTH / 4
            break
        if left_value * middle_value < 0:
            right = middle
            right_value = middle_value
        else:
            left = middle
            left_value = middle_value
    if sturm.root_count(primitive, left, right) != 1:
        raise AssertionError("root isolator lost the unique root")
    return {
        "primitive_coefficients_low_to_high": list(primitive),
        "isolating_interval": [fraction_text(left), fraction_text(right)],
        "left_sign": 1 if sturm.polynomial_value(primitive, left) > 0 else -1,
        "right_sign": 1 if sturm.polynomial_value(primitive, right) > 0 else -1,
    }


def cell_complex():
    vertices = ["v00", "v10", "v11", "v01", "w_minus", "w_zero", "w_plus"]
    oriented_edges = {
        "scope_bottom_left": ("v00", "w_minus"),
        "scope_bottom_right": ("w_minus", "v10"),
        "scope_right": ("v10", "v11"),
        "scope_top_left": ("v01", "w_plus"),
        "scope_top_right": ("w_plus", "v11"),
        "scope_left": ("v00", "v01"),
        "wall_lower": ("w_minus", "w_zero"),
        "wall_upper": ("w_zero", "w_plus"),
    }
    face_boundaries = {
        "positive_chamber": {
            "scope_bottom_left": 1,
            "wall_lower": 1,
            "wall_upper": 1,
            "scope_top_left": -1,
            "scope_left": -1,
        },
        "negative_chamber": {
            "scope_bottom_right": 1,
            "scope_right": 1,
            "scope_top_right": -1,
            "wall_upper": -1,
            "wall_lower": -1,
        },
    }
    edges = list(oriented_edges)
    faces = list(face_boundaries)
    d1 = [
        [(-1 if vertex == oriented_edges[edge][0] else 1 if vertex == oriented_edges[edge][1] else 0) for edge in edges]
        for vertex in vertices
    ]
    d2 = [
        [face_boundaries[face].get(edge, 0) for face in faces]
        for edge in edges
    ]
    product_matrix = [
        [sum(d1[row][middle] * d2[middle][column] for middle in range(len(edges))) for column in range(len(faces))]
        for row in range(len(vertices))
    ]
    if any(any(value for value in row) for row in product_matrix):
        raise AssertionError("collar incidence does not satisfy d^2=0")
    pairs = set()
    chains = set()
    for edge, (tail, head) in oriented_edges.items():
        pairs.add((tail, edge))
        pairs.add((head, edge))
    for face, boundary in face_boundaries.items():
        for edge in boundary:
            pairs.add((edge, face))
            for vertex in oriented_edges[edge]:
                pairs.add((vertex, face))
                chains.add((vertex, edge, face))
    scope_boundary_edges = [edge for edge in edges if edge.startswith("scope_")]
    return {
        "cell_count_by_dimension": {"0": len(vertices), "1": len(edges), "2": len(faces)},
        "cell_ids_by_dimension": {"0": vertices, "1": edges, "2": faces},
        "oriented_edges": {key: list(value) for key, value in oriented_edges.items()},
        "oriented_face_boundaries": face_boundaries,
        "strict_closure_pairs": [list(row) for row in sorted(pairs)],
        "strict_three_cell_chains": [list(row) for row in sorted(chains)],
        "boundary_matrix_d1": d1,
        "boundary_matrix_d2": d2,
        "d1_d2_zero": True,
        "factor_zero_subcomplex": ["w_minus", "w_zero", "w_plus", "wall_lower", "wall_upper"],
        "scope_boundary_subcomplex": [
            "v00", "v10", "v11", "v01", "w_minus", "w_plus", *scope_boundary_edges
        ],
        "parent_infinity_subcomplex": [],
    }


def semantic_seal(record):
    payload = deepcopy(record)
    payload.pop("semantic_sha256", None)
    return canonical_digest(payload)


def build_record():
    _matrices, points, _packed, states, _hamming, _multiplicity = transition.exact_inputs()
    candidates = tuple(gate.parse_candidates())
    _factor_types, _factor_terms, polynomials = labeled.factor_polynomials()
    incidence = np.asarray(
        [[states[left, factor] != states[right, factor] for factor in candidates] for left, right in safe.EDGES],
        dtype=bool,
    )
    crossing_multiplicity = incidence.sum(axis=0)
    unique_indices = np.where(crossing_multiplicity == 1)[0].tolist()
    ranking = []
    for candidate_index in unique_indices:
        factor_id = candidates[candidate_index]
        polynomial = polynomials[factor_id]
        ranking.append((max(map(sum, polynomial)), len(polynomial), factor_id, candidate_index))
    degree, terms, factor_id, candidate_index = max(ranking)
    edge_index = int(np.where(incidence[:, candidate_index])[0][0])
    if (factor_id, edge_index, degree, terms) != (TARGET_FACTOR, TARGET_EDGE, 6, 108):
        raise AssertionError("deterministic component-pilot target changed")
    cover = json.loads(SEGMENT_COVER.read_text(encoding="utf-8"))
    if edge_index not in cover["source_bank"]["selected_edge_indices"]:
        raise AssertionError("target edge is absent from the optimal source cover")

    records = [json.loads(line) for line in gate.CATALOG.read_text(encoding="utf-8").splitlines() if line]
    parents, parent_digest = gate.parent_polynomials(records[gate.PARENT])
    left_chart, right_chart = safe.EDGES[edge_index]
    left, right = points[left_chart], points[right_chart]

    axis_scan = []
    for axis in range(9):
        first = None
        for exponent in range(SEARCH_LIMIT + 1):
            epsilon = Fraction(1, 1 << exponent)
            if collar_gate(parents, polynomials[factor_id], left, right, axis, epsilon):
                first = exponent
                break
        if first is None:
            raise AssertionError(f"no dyadic collar certified on axis {axis}")
        axis_scan.append({
            "axis": axis,
            "first_certified_exponent": first,
            "largest_certified_tested_half_width": fraction_text(Fraction(1, 1 << first)),
            "immediately_larger_width_certified": False if first else None,
        })
    selected_exponent, selected_axis = min(
        (row["first_certified_exponent"], row["axis"]) for row in axis_scan
    )
    epsilon = Fraction(1, 1 << selected_exponent)
    details = collar_gate(
        parents, polynomials[factor_id], left, right, selected_axis, epsilon, details=True
    )
    if details is None or (selected_axis, selected_exponent) != (4, 9):
        raise AssertionError("selected transverse collar changed")
    parent_rows, restricted_wall, wall_checks = details
    direction = tuple(b - a for a, b in zip(left, right, strict=True))
    independent_coordinate = next(
        coordinate
        for coordinate, value in enumerate(direction)
        if coordinate != selected_axis and value
    )

    central = {}
    for (s_power, r_power), value in restricted_wall.items():
        central[(s_power, 0)] = central.get((s_power, 0), Fraction()) + value * Fraction(1, 2) ** r_power
    roots = {
        "q_minus_endpoint": isolate_monotone_root(r_face(restricted_wall, 0)),
        "retained_segment_q_zero": isolate_monotone_root(clean(central)),
        "q_plus_endpoint": isolate_monotone_root(r_face(restricted_wall, 1)),
    }
    restricted_sparse = [
        [s_power, r_power, fraction_text(value)]
        for (s_power, r_power), value in sorted(restricted_wall.items())
    ]
    parent_tensor_digest = canonical_digest(
        [
            [row["parent_bracket"], row["target_sign"], row["coefficient_tensor_sha256"]]
            for row in parent_rows
        ]
    )
    complex_record = cell_complex()
    record = {
        "format": FORMAT,
        "status": "EXACT_LOCAL_COMPONENT_COVERAGE_PILOT",
        "scope": {
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
        },
        "trust_boundary": {
            "verifier_kind": "SEPARATELY_EMBODIED_STRUCTURAL_VERIFIER",
            "shared_source_modules": [
                "diag3_pair_parent_source_transition_core",
                "verify_diag3_pair_fullsupport_safe_segment_walls",
                "verify_diag3_pair_global_parent_face_gate",
                "DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY",
                "DIAG9_GRAPH_verify_row2599_slice",
            ],
            "shared_algorithmic_structure": (
                "producer and verifier use near-parallel exact collar substitution "
                "and tensor-Bernstein routines"
            ),
            "implementation_independence": "NOT_CLAIMED",
            "external_sympy_reconstruction": (
                "ADDITIONAL_REVIEW_AUDIT_NOT_PERSISTED_AS_A_REPOSITORY_VERIFIER"
            ),
        },
        "sources": {
            "point_bank_sha256": file_sha256(transition.POINT_BANK),
            "factor_states_sha256": file_sha256(transition.FACTOR_STATES),
            "factor_census_sha256": file_sha256(transition.FACTOR_CENSUS),
            "candidate_factor_sha256": file_sha256(transition.CANDIDATES),
            "parent_catalog_sha256": file_sha256(gate.CATALOG),
            "segment_cover_sha256": file_sha256(SEGMENT_COVER),
            "parent_sign_sha256": parent_digest,
        },
        "target_selection": {
            "rule": "maximize (total_degree, monomial_count, factor_id) among factors crossing exactly one of the 105 certified strict-parent segments",
            "unique_segment_factor_count": len(unique_indices),
            "factor_id": factor_id,
            "total_degree": degree,
            "monomial_count": terms,
            "unique_edge_index": edge_index,
            "unique_edge_charts": [left_chart, right_chart],
            "edge_is_in_optimal_40_edge_cover": True,
            "reason": "stress the missed-component method on the algebraically largest mandatory witness",
        },
        "collar_selection": {
            "rule": "maximize the certified dyadic half-width 2^-n over coordinate axes, tie by least axis",
            "search_exponents": [0, SEARCH_LIMIT],
            "axis_scan": axis_scan,
            "selected_axis": selected_axis,
            "selected_half_width": fraction_text(epsilon),
            "larger_dyadic_width_fails_this_sufficient_gate": True,
            "affine_rank_witness": {
                "two_parameter_map_rank": 2,
                "transverse_axis": selected_axis,
                "independent_source_direction_coordinate": independent_coordinate,
                "source_direction_value": fraction_text(direction[independent_coordinate]),
            },
        },
        "exact_parent_safety": {
            "method": "all tensor-Bernstein coefficients of every target-signed parent bracket are strictly positive on [0,1]^2",
            "parent_bracket_count": len(parent_rows),
            "aggregate_tensor_sha256": parent_tensor_digest,
            "brackets": parent_rows,
        },
        "exact_wall_graph": {
            "restricted_wall_sparse_power_coefficients": restricted_sparse,
            "restricted_wall_sha256": canonical_digest(restricted_sparse),
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
        "regular_cw_roadmap": complex_record,
        "component_coverage": {
            "factor_id": factor_id,
            "declared_scope_component_count": 1,
            "component_cell_ids": complex_record["factor_zero_subcomplex"],
            "meets_retained_source_skeleton": True,
            "retained_skeleton_cell": "w_zero",
            "meets_artificial_scope_boundary": ["w_minus", "w_plus"],
            "meets_parent_infinity": False,
            "hostile_semantic_mutation_requirement": (
                "a second component, a skeleton miss, or a parent-infinity "
                "label must be rejected"
            ),
        },
        "decision": {
            "result": "LOCAL_COMPONENT_GATE_PASSES",
            "global_missed_component_gap": "OPEN",
            "next_action": "repeat on a declared factor family or construct a parent-cell roadmap with complete global component accounting",
            "theorem_effect": "No theorem-score promotion; the collar validates one exact full-support component-coverage contract only.",
        },
        "hostile_mutation_contract": [
            "trust boundary", "target factor", "target edge", "collar width", "wall coefficient",
            "affine rank", "parent tensor", "extra component", "skeleton miss", "scope boundary",
            "false parent infinity", "global coverage", "extension labels", "incidence",
            "closure", "root isolation", "source digest", "score promotion",
        ],
    }
    record["semantic_sha256"] = semantic_seal(record)
    return record


def main():
    record = build_record()
    OUTPUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("WROTE", OUTPUT)
    print("PASS factor 19069 has one exact strict-parent component in the full-support collar")
    print("PASS component meets retained edge 39 and artificial boundary; parent infinity is empty")
    print("SCOPE local collar only; global missed-component gap open; honest 9DVL score 2/9")


if __name__ == "__main__":
    main()
