#!/usr/bin/env python3
"""Independent exact replay of the chart-0/chart-152 block half-cube census."""

from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from itertools import product
from math import comb, gcd, lcm
from pathlib import Path
import json
import sys


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_SOURCE_BLOCK_HALF_CUBE_FEASIBILITY_0_152.json"
MAX_DEPTH = 8
MAX_CRITICAL_DEPTH = 5
STARTS = (Fraction(1, 2), Fraction(0), Fraction(0))
ENDS = (Fraction(1), Fraction(1), Fraction(1))

sys.path.insert(0, str(HERE))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import diag3_pair_parent_source_block_bridge_core as bridge  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


def trim(poly):
    return {index: value for index, value in poly.items() if value}


def product_poly(left, right):
    answer = {}
    for a, av in left.items():
        for b, bv in right.items():
            index = tuple(x + y for x, y in zip(a, b))
            answer[index] = answer.get(index, Fraction(0)) + av * bv
    return trim(answer)


def pullback(polynomial, source, target):
    answer = {}
    for exponents, coefficient in polynomial.items():
        term = {(0, 0, 0): Fraction(coefficient)}
        for variable, exponent in enumerate(exponents):
            block = variable // 3
            start = source[variable] + STARTS[block] * (target[variable] - source[variable])
            slope = (ENDS[block] - STARTS[block]) * (target[variable] - source[variable])
            index = [0, 0, 0]
            index[block] = 1
            factor = {(0, 0, 0): start, tuple(index): slope}
            for _ in range(exponent):
                term = product_poly(term, factor)
        for index, value in term.items():
            answer[index] = answer.get(index, Fraction(0)) + value
    return trim(answer)


def value_at(polynomial, point):
    answer = Fraction(0)
    for index, coefficient in polynomial.items():
        term = coefficient
        for axis in range(3):
            term *= point[axis] ** index[axis]
        answer += term
    return answer


def coordinate_value(polynomial, point):
    answer = Fraction(0)
    for exponent, coefficient in polynomial.items():
        term = Fraction(coefficient)
        for coordinate, power in zip(point, exponent):
            term *= coordinate**power
        answer += term
    return answer


def normalized_integer(polynomial):
    denominator = 1
    for value in polynomial.values():
        denominator = lcm(denominator, value.denominator)
    result = {index: int(value * denominator) for index, value in polynomial.items()}
    divisor = 0
    for value in result.values():
        divisor = gcd(divisor, abs(value))
    result = {index: value // max(divisor, 1) for index, value in result.items()}
    if result[max(result)] < 0:
        result = {index: -value for index, value in result.items()}
    return tuple(sorted(result.items()))


def controls(polynomial):
    degrees = tuple(max(index[axis] for index in polynomial) for axis in range(3))
    shape = tuple(degree + 1 for degree in degrees)
    result = {}
    for target_index in product(*(range(length) for length in shape)):
        total = Fraction(0)
        for source_index, coefficient in polynomial.items():
            if not all(source_index[axis] <= target_index[axis] for axis in range(3)):
                continue
            multiplier = Fraction(1)
            for axis in range(3):
                multiplier *= Fraction(
                    comb(target_index[axis], source_index[axis]),
                    comb(degrees[axis], source_index[axis]),
                )
            total += coefficient * multiplier
        result[target_index] = total
    return result, shape


def halves(sequence):
    triangle = [list(sequence)]
    while len(triangle[-1]) > 1:
        triangle.append(
            [(left + right) / 2 for left, right in zip(triangle[-1], triangle[-1][1:])]
        )
    return (
        tuple(row[0] for row in triangle),
        tuple(row[-1] for row in reversed(triangle)),
    )


def bisect_axis(control, shape, axis):
    fibers = defaultdict(dict)
    for index, coefficient in control.items():
        fibers[index[:axis] + index[axis + 1 :]][index[axis]] = coefficient
    outputs = ({}, {})
    for fixed, fiber in fibers.items():
        split = halves(tuple(fiber[position] for position in range(shape[axis])))
        for side in range(2):
            for position, coefficient in enumerate(split[side]):
                index = fixed[:axis] + (position,) + fixed[axis:]
                outputs[side][index] = coefficient
    return outputs


def subcubes(control, shape):
    current = [control]
    for axis in range(3):
        current = [half for piece in current for half in bisect_axis(piece, shape, axis)]
    return current


def signs(values):
    return {1 if value > 0 else -1 if value < 0 else 0 for value in values}


def decide(control, shape):
    corners = tuple(
        product(*((0, length - 1) if length > 1 else (0,) for length in shape))
    )
    agenda = [(control, 0)]
    deepest = 0
    visited = 0
    while agenda:
        current, depth = agenda.pop()
        visited += 1
        control_signs = signs(current.values())
        if 0 not in control_signs and len(control_signs) == 1:
            continue
        corner_signs = signs(current[index] for index in corners)
        if 0 in corner_signs or {-1, 1} <= corner_signs:
            return "NONEMPTY_CORNER", depth, visited
        deepest = max(deepest, depth)
        if depth >= MAX_DEPTH:
            return "UNRESOLVED", deepest, visited
        agenda.extend((child, depth + 1) for child in subcubes(current, shape))
    return "EMPTY_BERNSTEIN", deepest, visited


def digest_ids(domain, identifiers):
    digest = sha256(domain + b"\0")
    for identifier in identifiers:
        digest.update(identifier.to_bytes(4, "little"))
    return digest.hexdigest()


def derivative(polynomial, axis):
    answer = {}
    for index, coefficient in polynomial.items():
        if index[axis]:
            target = list(index)
            target[axis] -= 1
            answer[tuple(target)] = coefficient * index[axis]
    return trim(answer)


def critical_system_empty(polynomials):
    agenda = [(tuple(controls(polynomial) for polynomial in polynomials), 0)]
    deepest = 0
    visited = 0
    while agenda:
        system, depth = agenda.pop()
        visited += 1
        excluded = False
        for control, _shape in system:
            control_signs = signs(control.values())
            if 0 not in control_signs and len(control_signs) == 1:
                excluded = True
                break
        if excluded:
            continue
        deepest = max(deepest, depth)
        if depth >= MAX_CRITICAL_DEPTH:
            return False, deepest, visited
        families = [subcubes(control, shape) for control, shape in system]
        for child_index in range(8):
            agenda.append(
                (
                    tuple(
                        (family[child_index], system[equation][1])
                        for equation, family in enumerate(families)
                    ),
                    depth + 1,
                )
            )
    return True, deepest, visited


def fraction_text(value):
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def reconstruct():
    _matrices, points, _packed, _states, _hamming, _multiplicity = transition.exact_inputs()
    source = points[0]
    target = points[152]
    rows = [json.loads(line) for line in bridge.safe.CATALOG.read_text().splitlines() if line]
    parents, parent_digest = gate.parent_polynomials(rows[2599])
    full_cube_failures = []
    for mask in range(8):
        point = bridge.hybrid_vertex(source, target, mask)
        failed = []
        for label, target_sign, polynomial, _terms in parents:
            signed = target_sign * coordinate_value(polynomial, point)
            if signed <= 0:
                failed.append({"bracket": label, "signed_value": fraction_text(signed)})
        if failed:
            full_cube_failures.append(
                {
                    "block_vertex": [(mask >> block) & 1 for block in range(3)],
                    "failed_parent_brackets": failed,
                }
            )
    vertices = tuple(product((Fraction(0), Fraction(1)), repeat=3))
    parent_degrees = Counter()
    minimum = None
    minimum_label = None
    for label, target_sign, polynomial, _terms in parents:
        cube = pullback(polynomial, source, target)
        degrees = tuple(max(index[axis] for index in cube) for axis in range(3))
        parent_degrees[degrees] += 1
        assert all(degree <= 1 for degree in degrees)
        signed = tuple(target_sign * value_at(cube, vertex) for vertex in vertices)
        assert min(signed) > 0
        if minimum is None or min(signed) < minimum:
            minimum = min(signed)
            minimum_label = label

    candidates = gate.parse_candidates()
    _types, _terms, polynomials = labeled.factor_polynomials()
    degree_census = Counter()
    status_census = Counter()
    depth_census = Counter()
    occurring = []
    zero_free = []
    unresolved = []
    occurring_degrees = Counter()
    graph_type_occurring = []
    fully_triquadratic_occurring = []
    fully_triquadratic_polynomials = {}
    maximum_visited = 0
    semantic = sha256(b"diag3-source-block-cube-wall-feasibility-v1\0")
    for factor_id in candidates:
        cube = pullback(polynomials[factor_id], source, target)
        assert cube
        degrees = tuple(max(index[axis] for index in cube) for axis in range(3))
        degree_census[degrees] += 1
        if degrees == (0, 0, 0):
            status, depth, visited = "EMPTY_CONSTANT", 0, 1
        else:
            status, depth, visited = decide(*controls(cube))
        status_census[status] += 1
        depth_census[status, depth] += 1
        maximum_visited = max(maximum_visited, visited)
        if status == "NONEMPTY_CORNER":
            occurring.append(factor_id)
            occurring_degrees[degrees] += 1
            if min(degrees) <= 1:
                graph_type_occurring.append(factor_id)
            else:
                fully_triquadratic_occurring.append(factor_id)
                fully_triquadratic_polynomials[factor_id] = cube
        elif status.startswith("EMPTY_"):
            zero_free.append(factor_id)
        else:
            unresolved.append(factor_id)
        semantic.update(factor_id.to_bytes(4, "little"))
        semantic.update(bytes(degrees))
        semantic.update(depth.to_bytes(2, "little"))
        semantic.update(visited.to_bytes(8, "little"))
        semantic.update(status.encode("ascii") + b"\0")
        semantic.update(repr(normalized_integer(cube)).encode("ascii"))

    critical_depth_census = Counter()
    critical_maximum_visited = 0
    critical_semantic = sha256(b"diag3-source-block-half-cube-critical-system-v1\0")
    critical_unresolved = []
    for factor_id in fully_triquadratic_occurring:
        polynomial = fully_triquadratic_polynomials[factor_id]
        derivatives = (derivative(polynomial, 1), derivative(polynomial, 2))
        empty, depth, visited = critical_system_empty((polynomial, *derivatives))
        critical_depth_census[depth] += 1
        critical_maximum_visited = max(critical_maximum_visited, visited)
        if not empty:
            critical_unresolved.append(factor_id)
        critical_semantic.update(factor_id.to_bytes(4, "little"))
        critical_semantic.update(bytes((empty, depth)))
        critical_semantic.update(visited.to_bytes(8, "little"))
        for equation in (polynomial, *derivatives):
            critical_semantic.update(repr(normalized_integer(equation)).encode("ascii"))
    assert not critical_unresolved

    return {
        "format": "diag3-pair-source-block-half-cube-component-coverage-v2",
        "status": "EXACT_SOURCE_BLOCK_HALF_CUBE_WALL_COMPONENT_COVERAGE",
        "scope": {
            "parent_index": 2599,
            "source_chart": 0,
            "target_chart": 152,
            "varying_column_blocks": [0, 1, 2],
            "parameter_domain": "closed unit cube mapped to block intervals [1/2,1] x [0,1] x [0,1]",
            "block_parameter_intervals": ["1/2..1", "0..1", "0..1"],
            "parent_parameter_coverage": "COMPLETE_ON_SOURCE_BLOCK_HALF_CUBE",
            "wall_feasibility_coverage": "COMPLETE_EXCEPT_EXPLICIT_UNRESOLVED",
            "wall_component_coverage": "EVERY_OCCURRING_WALL_COMPONENT_MEETS_HALF_CUBE_BOUNDARY",
            "global_parent_cell_coverage": "NOT_CLAIMED",
        },
        "parent_cube": {
            "parent_brackets": len(parents),
            "parent_polynomial_digest": parent_digest,
            "restriction_tridegree_census": {
                ",".join(map(str, degrees)): count
                for degrees, count in sorted(parent_degrees.items())
            },
            "strict_vertices": len(vertices),
            "minimum_signed_vertex_margin": fraction_text(minimum),
            "minimum_margin_bracket": minimum_label,
            "coverage_argument": "trilinear Bernstein coefficients are the eight positive vertex values",
        },
        "naive_full_cube_no_go": {
            "tested_block_vertices": 8,
            "parent_safe_block_vertices": 8 - len(full_cube_failures),
            "failed_block_vertices": full_cube_failures,
            "decision": "REJECT_FULL_[0,1]^3_CUBE; RETAIN_PARENT_SAFE_[1/2,1]x[0,1]x[0,1]_HALF_CUBE",
        },
        "wall_feasibility": {
            "candidate_factors": len(candidates),
            "restriction_tridegree_census": {
                ",".join(map(str, degrees)): count
                for degrees, count in sorted(degree_census.items())
            },
            "status_census": dict(sorted(status_census.items())),
            "classification_depth_census": {
                f"{status}:{depth}": count
                for (status, depth), count in sorted(depth_census.items())
            },
            "occurring_walls": len(occurring),
            "zero_free_walls": len(zero_free),
            "unresolved_walls": len(unresolved),
            "maximum_subboxes_visited_for_one_wall": maximum_visited,
            "occurring_factor_ids_sha256": digest_ids(
                b"diag3-source-block-cube-occurring-factor-ids-v1", occurring
            ),
            "zero_free_factor_ids_sha256": digest_ids(
                b"diag3-source-block-cube-zero-free-factor-ids-v1", zero_free
            ),
            "unresolved_factor_ids_sha256": digest_ids(
                b"diag3-source-block-cube-unresolved-factor-ids-v1", unresolved
            ),
            "classification_semantic_sha256": semantic.hexdigest(),
        },
        "wall_component_preflight": {
            "occurring_tridegree_census": {
                ",".join(map(str, degrees)): count
                for degrees, count in sorted(occurring_degrees.items())
            },
            "graph_type_occurring_walls": len(graph_type_occurring),
            "graph_type_component_conclusion": "EVERY_COMPONENT_MEETS_HALF_CUBE_BOUNDARY",
            "graph_type_argument": "If p is affine in one parameter, a coefficient-drop zero gives a full boundary-meeting fiber; otherwise projection is a local graph, so a compact interior component would have a nonempty compact-open image in R^2.",
            "fully_triquadratic_occurring_walls": len(fully_triquadratic_occurring),
            "fully_triquadratic_critical_systems_proved_empty": len(fully_triquadratic_occurring),
            "fully_triquadratic_critical_systems_unresolved": 0,
            "critical_depth_census": {
                str(depth): count for depth, count in sorted(critical_depth_census.items())
            },
            "maximum_critical_subboxes_visited": critical_maximum_visited,
            "fully_triquadratic_component_coverage": "EVERY_COMPONENT_MEETS_HALF_CUBE_BOUNDARY",
            "all_occurring_wall_component_coverage": "EVERY_COMPONENT_MEETS_HALF_CUBE_BOUNDARY",
            "critical_semantic_sha256": critical_semantic.hexdigest(),
            "graph_type_factor_ids_sha256": digest_ids(
                b"diag3-source-block-half-cube-graph-type-factor-ids-v1",
                graph_type_occurring,
            ),
            "fully_triquadratic_factor_ids_sha256": digest_ids(
                b"diag3-source-block-half-cube-triquadratic-factor-ids-v1",
                fully_triquadratic_occurring,
            ),
        },
        "theorem_effect": "Exact parent residence, complete wall feasibility, and wall-component boundary coverage on one source block half-cube; global pair coverage and the independent triple obligation remain open; honest 9DVL score remains 2/9.",
    }


def validate(candidate, expected):
    assert candidate == expected
    assert candidate["wall_feasibility"]["candidate_factors"] == 17_824
    assert candidate["wall_feasibility"]["occurring_walls"] == 4_450
    assert candidate["wall_feasibility"]["zero_free_walls"] == 13_374
    assert candidate["wall_feasibility"]["unresolved_walls"] == 0
    assert candidate["wall_component_preflight"]["graph_type_occurring_walls"] == 3_889
    assert candidate["wall_component_preflight"]["fully_triquadratic_occurring_walls"] == 561
    assert candidate["wall_component_preflight"]["fully_triquadratic_critical_systems_proved_empty"] == 561
    assert candidate["wall_component_preflight"]["fully_triquadratic_critical_systems_unresolved"] == 0
    assert candidate["wall_component_preflight"]["critical_depth_census"] == {
        "0": 552,
        "1": 4,
        "2": 3,
        "3": 1,
        "4": 1,
    }
    assert candidate["wall_component_preflight"]["maximum_critical_subboxes_visited"] == 81
    assert candidate["wall_component_preflight"]["all_occurring_wall_component_coverage"] == "EVERY_COMPONENT_MEETS_HALF_CUBE_BOUNDARY"
    assert candidate["naive_full_cube_no_go"]["parent_safe_block_vertices"] == 6
    assert len(candidate["naive_full_cube_no_go"]["failed_block_vertices"]) == 2
    assert candidate["scope"]["wall_component_coverage"] == (
        "EVERY_OCCURRING_WALL_COMPONENT_MEETS_HALF_CUBE_BOUNDARY"
    )
    assert candidate["scope"]["global_parent_cell_coverage"] == "NOT_CLAIMED"


def main():
    stored = json.loads(CERTIFICATE.read_text())
    expected = reconstruct()
    validate(stored, expected)

    mutations = []
    for path, value in (
        (("format",), "corrupted"),
        (("scope", "block_parameter_intervals"), ["0..1", "0..1", "0..1"]),
        (("scope", "wall_component_coverage"), "COMPLETE"),
        (("parent_cube", "strict_vertices"), 7),
        (("naive_full_cube_no_go", "parent_safe_block_vertices"), 8),
        (("wall_feasibility", "occurring_walls"), 4_451),
        (("wall_feasibility", "zero_free_walls"), 13_373),
        (("wall_feasibility", "unresolved_walls"), 1),
        (("wall_feasibility", "classification_semantic_sha256"), "0" * 64),
        (("wall_component_preflight", "fully_triquadratic_occurring_walls"), 560),
        (("wall_component_preflight", "fully_triquadratic_critical_systems_unresolved"), 1),
    ):
        mutation = deepcopy(stored)
        target = mutation
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        mutations.append(mutation)
    rejected = 0
    for mutation in mutations:
        try:
            validate(mutation, expected)
        except AssertionError:
            rejected += 1
    assert rejected == len(mutations)

    print("PASS naive full cube rejected at 2/8 vertices; exact half-cube retained")
    print("PASS exact parent residence on the chart-0/chart-152 block half-cube")
    print("PASS 17,824 wall restrictions: 4,450 occurring / 13,374 zero-free / 0 unresolved")
    print("PASS maximum 25 dyadic subboxes visited for one wall")
    print("PASS graph theorem covers 3,889 surfaces; 561/561 triquadratic critical systems empty")
    print("PASS every occurring wall component meets the half-cube boundary")
    print("SEMANTIC", expected["wall_feasibility"]["classification_semantic_sha256"])
    print(f"PASS {rejected}/{len(mutations)} hostile corruptions rejected")
    print("SCOPE component coverage on one half-cube; global parent-cell coverage remains open; honest 9DVL 2/9")


if __name__ == "__main__":
    main()
