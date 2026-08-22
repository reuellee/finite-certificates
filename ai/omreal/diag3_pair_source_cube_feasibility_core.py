#!/usr/bin/env python3
"""Exact parent-residence and wall-feasibility census on a source block half-cube."""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import product
from math import comb, gcd, lcm
from pathlib import Path
import json
import sys


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUTPUT = DATA / "DIAG3_PAIR_SOURCE_BLOCK_HALF_CUBE_FEASIBILITY_0_152.json"
FORMAT = "diag3-pair-source-block-half-cube-feasibility-v1"
STATUS = "EXACT_SOURCE_BLOCK_HALF_CUBE_WALL_FEASIBILITY"
SOURCE_CHART = 0
TARGET_CHART = 152
BLOCK_STARTS = (Fraction(1, 2), Fraction(0), Fraction(0))
BLOCK_ENDS = (Fraction(1), Fraction(1), Fraction(1))
MAX_BERNSTEIN_DEPTH = 8

sys.path.insert(0, str(HERE))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import diag3_pair_parent_source_block_bridge_core as bridge  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


def fraction_text(value: Fraction) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def clean(polynomial):
    return {monomial: value for monomial, value in polynomial.items() if value}


def multiply_trivariate(left, right):
    answer = {}
    for first_index, first in left.items():
        for second_index, second in right.items():
            index = tuple(a + b for a, b in zip(first_index, second_index))
            answer[index] = answer.get(index, Fraction(0)) + first * second
    return clean(answer)


def restrict_cube(polynomial, source, target):
    answer = {}
    for exponent, coefficient in polynomial.items():
        term = {(0, 0, 0): Fraction(coefficient)}
        for variable, power in enumerate(exponent):
            if not power:
                continue
            block = variable // 3
            index = [0, 0, 0]
            index[block] = 1
            start = source[variable] + BLOCK_STARTS[block] * (
                target[variable] - source[variable]
            )
            change = (BLOCK_ENDS[block] - BLOCK_STARTS[block]) * (
                target[variable] - source[variable]
            )
            linear = {(0, 0, 0): start, tuple(index): change}
            for _ in range(power):
                term = multiply_trivariate(term, linear)
        for monomial, value in term.items():
            answer[monomial] = answer.get(monomial, Fraction(0)) + value
    return clean(answer)


def evaluate_trivariate(polynomial, values):
    return sum(
        coefficient * values[0] ** i * values[1] ** j * values[2] ** k
        for (i, j, k), coefficient in polynomial.items()
    )


def evaluate_coordinate_polynomial(polynomial, values):
    answer = Fraction(0)
    for exponent, coefficient in polynomial.items():
        term = Fraction(coefficient)
        for coordinate, power in zip(values, exponent):
            term *= coordinate**power
        answer += term
    return answer


def canonical_integer(polynomial):
    denominator = 1
    for value in polynomial.values():
        denominator = lcm(denominator, Fraction(value).denominator)
    integer = {
        monomial: int(Fraction(value) * denominator)
        for monomial, value in polynomial.items()
    }
    divisor = 0
    for value in integer.values():
        divisor = gcd(divisor, abs(value))
    divisor = max(divisor, 1)
    integer = {monomial: value // divisor for monomial, value in integer.items()}
    if integer[max(integer)] < 0:
        integer = {monomial: -value for monomial, value in integer.items()}
    return tuple(sorted(integer.items()))


def bernstein_control(polynomial):
    degrees = tuple(max(index[axis] for index in polynomial) for axis in range(3))
    control = {}
    for target_index in product(*(range(degree + 1) for degree in degrees)):
        value = Fraction(0)
        for source_index, coefficient in polynomial.items():
            if all(source_index[axis] <= target_index[axis] for axis in range(3)):
                weight = Fraction(1)
                for axis in range(3):
                    weight *= Fraction(
                        comb(target_index[axis], source_index[axis]),
                        comb(degrees[axis], source_index[axis]),
                    )
                value += coefficient * weight
        control[target_index] = value
    return control, tuple(degree + 1 for degree in degrees)


def split_curve(values):
    rows = [list(values)]
    while len(rows[-1]) > 1:
        rows.append(
            [(left + right) / 2 for left, right in zip(rows[-1], rows[-1][1:])]
        )
    return (
        tuple(row[0] for row in rows),
        tuple(row[-1] for row in reversed(rows)),
    )


def split_axis(control, shape, axis):
    groups = defaultdict(dict)
    for index, value in control.items():
        fixed = index[:axis] + index[axis + 1 :]
        groups[fixed][index[axis]] = value
    left = {}
    right = {}
    for fixed, row in groups.items():
        values = tuple(row[position] for position in range(shape[axis]))
        first, second = split_curve(values)
        for position, value in enumerate(first):
            index = fixed[:axis] + (position,) + fixed[axis:]
            left[index] = value
        for position, value in enumerate(second):
            index = fixed[:axis] + (position,) + fixed[axis:]
            right[index] = value
    return left, right


def bernstein_children(control, shape):
    pieces = [control]
    for axis in range(3):
        pieces = [half for piece in pieces for half in split_axis(piece, shape, axis)]
    return tuple(pieces)


def sign_set(values):
    return {1 if value > 0 else -1 if value < 0 else 0 for value in values}


def classify_bernstein(control, shape):
    stack = [(control, 0)]
    maximum_depth = 0
    visited = 0
    vertices = tuple(
        product(*((0, length - 1) if length > 1 else (0,) for length in shape))
    )
    while stack:
        current, depth = stack.pop()
        visited += 1
        control_signs = sign_set(current.values())
        if 0 not in control_signs and len(control_signs) == 1:
            continue
        corner_signs = sign_set(current[index] for index in vertices)
        if 0 in corner_signs or {-1, 1} <= corner_signs:
            return "NONEMPTY_CORNER", depth, visited
        maximum_depth = max(maximum_depth, depth)
        if depth >= MAX_BERNSTEIN_DEPTH:
            return "UNRESOLVED", maximum_depth, visited
        stack.extend((child, depth + 1) for child in bernstein_children(current, shape))
    return "EMPTY_BERNSTEIN", maximum_depth, visited


def id_digest(domain, identifiers):
    digest = sha256(domain + b"\0")
    for identifier in identifiers:
        digest.update(int(identifier).to_bytes(4, "little"))
    return digest.hexdigest()


def build_record(progress=False):
    _matrices, points, _packed, _states, _hamming, _multiplicity = transition.exact_inputs()
    source = points[SOURCE_CHART]
    target = points[TARGET_CHART]

    records = [json.loads(line) for line in bridge.safe.CATALOG.read_text().splitlines() if line]
    parents, parent_digest = gate.parent_polynomials(records[2599])
    full_cube_failures = []
    for mask in range(8):
        vertex = bridge.hybrid_vertex(source, target, mask)
        failed = [
            {
                "bracket": label,
                "signed_value": fraction_text(
                    target_sign * evaluate_coordinate_polynomial(polynomial, vertex)
                ),
            }
            for label, target_sign, polynomial, _terms in parents
            if target_sign * evaluate_coordinate_polynomial(polynomial, vertex) <= 0
        ]
        if failed:
            full_cube_failures.append(
                {
                    "block_vertex": [(mask >> block) & 1 for block in range(3)],
                    "failed_parent_brackets": failed,
                }
            )
    parent_degrees = Counter()
    parent_minimum = None
    parent_minimum_label = None
    cube_vertices = tuple(product((Fraction(0), Fraction(1)), repeat=3))
    for label, target_sign, polynomial, _terms in parents:
        cube = restrict_cube(polynomial, source, target)
        degrees = tuple(max(index[axis] for index in cube) for axis in range(3))
        parent_degrees[degrees] += 1
        if any(degree > 1 for degree in degrees):
            raise AssertionError(f"parent bracket {label} is not trilinear")
        values = tuple(
            target_sign * evaluate_trivariate(cube, vertex) for vertex in cube_vertices
        )
        if min(values) <= 0:
            raise AssertionError(f"parent bracket {label} fails at a cube vertex")
        if parent_minimum is None or min(values) < parent_minimum:
            parent_minimum = min(values)
            parent_minimum_label = label

    candidates = gate.parse_candidates()
    _factor_types, _factor_terms, polynomials = labeled.factor_polynomials()
    degree_census = Counter()
    status_census = Counter()
    depth_census = Counter()
    occurring = []
    zero_free = []
    unresolved = []
    occurring_degrees = Counter()
    graph_type_occurring = []
    fully_triquadratic_occurring = []
    semantic = sha256(b"diag3-source-block-cube-wall-feasibility-v1\0")
    maximum_visited = 0
    for offset, factor_id in enumerate(candidates, start=1):
        cube = restrict_cube(polynomials[factor_id], source, target)
        if not cube:
            raise AssertionError(f"factor {factor_id} restricts identically to zero")
        degrees = tuple(max(index[axis] for index in cube) for axis in range(3))
        degree_census[degrees] += 1
        if all(degree == 0 for degree in degrees):
            status, depth, visited = "EMPTY_CONSTANT", 0, 1
        else:
            status, depth, visited = classify_bernstein(*bernstein_control(cube))
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
        elif status.startswith("EMPTY_"):
            zero_free.append(factor_id)
        else:
            unresolved.append(factor_id)
        semantic.update(factor_id.to_bytes(4, "little"))
        semantic.update(bytes(degrees))
        semantic.update(depth.to_bytes(2, "little"))
        semantic.update(visited.to_bytes(8, "little"))
        semantic.update(status.encode("ascii") + b"\0")
        semantic.update(repr(canonical_integer(cube)).encode("ascii"))
        if progress and offset % 2000 == 0:
            print(f"classified {offset}/{len(candidates)} cube walls", flush=True)

    return {
        "format": FORMAT,
        "status": STATUS,
        "scope": {
            "parent_index": 2599,
            "source_chart": SOURCE_CHART,
            "target_chart": TARGET_CHART,
            "varying_column_blocks": [0, 1, 2],
            "parameter_domain": "closed unit cube mapped to block intervals [1/2,1] x [0,1] x [0,1]",
            "block_parameter_intervals": ["1/2..1", "0..1", "0..1"],
            "parent_parameter_coverage": "COMPLETE_ON_SOURCE_BLOCK_HALF_CUBE",
            "wall_feasibility_coverage": "COMPLETE_EXCEPT_EXPLICIT_UNRESOLVED",
            "wall_component_coverage": "NOT_CLAIMED",
            "global_parent_cell_coverage": "NOT_CLAIMED",
        },
        "parent_cube": {
            "parent_brackets": len(parents),
            "parent_polynomial_digest": parent_digest,
            "restriction_tridegree_census": {
                ",".join(map(str, degrees)): count
                for degrees, count in sorted(parent_degrees.items())
            },
            "strict_vertices": len(cube_vertices),
            "minimum_signed_vertex_margin": fraction_text(parent_minimum),
            "minimum_margin_bracket": parent_minimum_label,
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
            "occurring_factor_ids_sha256": id_digest(
                b"diag3-source-block-cube-occurring-factor-ids-v1", occurring
            ),
            "zero_free_factor_ids_sha256": id_digest(
                b"diag3-source-block-cube-zero-free-factor-ids-v1", zero_free
            ),
            "unresolved_factor_ids_sha256": id_digest(
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
            "fully_triquadratic_component_coverage": "OPEN",
            "graph_type_factor_ids_sha256": id_digest(
                b"diag3-source-block-half-cube-graph-type-factor-ids-v1",
                graph_type_occurring,
            ),
            "fully_triquadratic_factor_ids_sha256": id_digest(
                b"diag3-source-block-half-cube-triquadratic-factor-ids-v1",
                fully_triquadratic_occurring,
            ),
        },
        "theorem_effect": "Exact parent residence and wall feasibility on one source block half-cube; wall-component coverage, global pair coverage, and the independent triple obligation remain open; honest 9DVL score remains 2/9.",
    }
