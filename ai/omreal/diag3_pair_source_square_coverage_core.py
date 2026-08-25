#!/usr/bin/env python3
"""Exact component-coverage quotient on a chart-0/chart-152 source square."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from math import comb, gcd, lcm
from pathlib import Path
import json
import sys


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUTPUT = DATA / "DIAG3_PAIR_SOURCE_SQUARE_COVERAGE_0_152.json"
FORMAT = "diag3-pair-source-square-component-coverage-v1"
STATUS = "EXACT_SOURCE_SQUARE_WALL_COMPONENT_COVERAGE"
SOURCE_CHART = 0
TARGET_CHART = 152
VARIABLE_BLOCKS = (0, 1)
FIXED_BLOCK = 2
MAX_BERNSTEIN_DEPTH = 10
ROOT_WIDTH = Fraction(1, 1 << 64)

sys.path.insert(0, str(HERE))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402
import diag3_pair_parent_source_block_bridge_core as bridge  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


def fraction_text(value: Fraction) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def clean(polynomial):
    return {monomial: value for monomial, value in polynomial.items() if value}


def multiply_bivariate(left, right):
    answer = {}
    for (i, j), first in left.items():
        for (k, ell), second in right.items():
            monomial = i + k, j + ell
            answer[monomial] = answer.get(monomial, Fraction(0)) + first * second
    return clean(answer)


def restrict_square(polynomial, source, target):
    """Vary normalized moving-column blocks zero and one independently."""

    answer = {}
    for exponent, coefficient in polynomial.items():
        term = {(0, 0): Fraction(coefficient)}
        for variable, power in enumerate(exponent):
            if not power:
                continue
            block = variable // 3
            if block == VARIABLE_BLOCKS[0]:
                linear = {
                    (0, 0): source[variable],
                    (1, 0): target[variable] - source[variable],
                }
            elif block == VARIABLE_BLOCKS[1]:
                linear = {
                    (0, 0): source[variable],
                    (0, 1): target[variable] - source[variable],
                }
            else:
                linear = {(0, 0): source[variable]}
            for _ in range(power):
                term = multiply_bivariate(term, linear)
        for monomial, value in term.items():
            answer[monomial] = answer.get(monomial, Fraction(0)) + value
    return clean(answer)


def evaluate_bivariate(polynomial, first, second):
    return sum(
        coefficient * first**i * second**j
        for (i, j), coefficient in polynomial.items()
    )


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


def bernstein_grid(polynomial):
    degree_first = max(i for i, _j in polynomial)
    degree_second = max(j for _i, j in polynomial)
    return tuple(
        tuple(
            sum(
                coefficient
                * Fraction(comb(i, p), comb(degree_first, p))
                * Fraction(comb(j, q), comb(degree_second, q))
                for (p, q), coefficient in polynomial.items()
                if p <= i and q <= j
            )
            for j in range(degree_second + 1)
        )
        for i in range(degree_first + 1)
    )


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


def bernstein_children(grid):
    columns = tuple(zip(*grid))
    column_pieces = tuple(split_curve(column) for column in columns)
    left = tuple(
        tuple(piece[0][index] for piece in column_pieces)
        for index in range(len(grid))
    )
    right = tuple(
        tuple(piece[1][index] for piece in column_pieces)
        for index in range(len(grid))
    )
    left_rows = tuple(split_curve(row) for row in left)
    right_rows = tuple(split_curve(row) for row in right)
    return (
        tuple(piece[0] for piece in left_rows),
        tuple(piece[0] for piece in right_rows),
        tuple(piece[1] for piece in left_rows),
        tuple(piece[1] for piece in right_rows),
    )


def signs(values):
    return {
        1 if value > 0 else -1 if value < 0 else 0
        for value in values
    }


def classify_bernstein(grid):
    stack = [(grid, 0)]
    maximum_depth = 0
    visited = 0
    while stack:
        current, depth = stack.pop()
        visited += 1
        control_signs = signs(value for row in current for value in row)
        if 0 not in control_signs and len(control_signs) == 1:
            continue
        corner_signs = signs(
            (current[0][0], current[-1][0], current[0][-1], current[-1][-1])
        )
        if 0 in corner_signs or {-1, 1} <= corner_signs:
            return "NONEMPTY_SIGN_CHANGE", depth, visited
        maximum_depth = max(maximum_depth, depth)
        if depth >= MAX_BERNSTEIN_DEPTH:
            return "UNRESOLVED", maximum_depth, visited
        stack.extend((child, depth + 1) for child in bernstein_children(current))
    return "EMPTY_BERNSTEIN", maximum_depth, visited


def trim_univariate(polynomial):
    polynomial = [Fraction(value) for value in polynomial]
    while len(polynomial) > 1 and not polynomial[-1]:
        polynomial.pop()
    return polynomial


def add_univariate(left, right, scale=1):
    answer = [Fraction(0)] * max(len(left), len(right))
    for index, value in enumerate(left):
        answer[index] += value
    for index, value in enumerate(right):
        answer[index] += scale * value
    return trim_univariate(answer)


def multiply_univariate(left, right):
    answer = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, first in enumerate(left):
        for j, second in enumerate(right):
            answer[i + j] += first * second
    return trim_univariate(answer)


def derivative_univariate(polynomial):
    return trim_univariate(
        [index * value for index, value in enumerate(polynomial)][1:] or [0]
    )


def divide_univariate(dividend, divisor):
    dividend = trim_univariate(dividend)
    divisor = trim_univariate(divisor)
    if len(divisor) == 1 and not divisor[0]:
        raise ZeroDivisionError
    quotient = [Fraction(0)] * max(1, len(dividend) - len(divisor) + 1)
    while len(dividend) >= len(divisor) and any(dividend):
        degree = len(dividend) - len(divisor)
        coefficient = dividend[-1] / divisor[-1]
        quotient[degree] = coefficient
        for index, value in enumerate(divisor):
            dividend[index + degree] -= coefficient * value
        dividend = trim_univariate(dividend)
    return trim_univariate(quotient), trim_univariate(dividend)


def gcd_univariate(left, right):
    left = trim_univariate(left)
    right = trim_univariate(right)
    while any(right):
        _quotient, remainder = divide_univariate(left, right)
        left, right = right, remainder
    if not any(left):
        return [Fraction(0)]
    return trim_univariate([value / left[-1] for value in left])


def evaluate_univariate(polynomial, value):
    answer = Fraction(0)
    for coefficient in reversed(polynomial):
        answer = answer * value + coefficient
    return answer


def isolate_roots(polynomial, width=ROOT_WIDTH):
    if not evaluate_univariate(polynomial, Fraction(0)):
        raise AssertionError("root at zero endpoint")
    if not evaluate_univariate(polynomial, Fraction(1)):
        raise AssertionError("root at one endpoint")
    total = sturm.root_count(polynomial, Fraction(0), Fraction(1))
    stack = [(Fraction(0), Fraction(1), total)]
    roots = []
    while stack:
        left, right, count = stack.pop()
        if not count:
            continue
        if count == 1 and right - left <= width:
            roots.append((left, right))
            continue
        middle = (left + right) / 2
        while not evaluate_univariate(polynomial, middle):
            middle = (left + middle) / 2
        left_count = sturm.root_count(polynomial, left, middle)
        right_count = sturm.root_count(polynomial, middle, right)
        if left_count + right_count != count:
            raise AssertionError("Sturm subdivision lost a boundary root")
        stack.extend(((middle, right, right_count), (left, middle, left_count)))
    return tuple(sorted(roots))


def coefficient_rows(polynomial):
    rows = [[Fraction(0)] * 3 for _ in range(3)]
    for (first_degree, second_degree), coefficient in polynomial.items():
        rows[second_degree][first_degree] = coefficient
    return tuple(trim_univariate(row) for row in rows)


def edge_polynomial(polynomial, edge):
    if edge == "left":
        return trim_univariate([polynomial.get((0, j), 0) for j in range(3)])
    if edge == "right":
        return trim_univariate(
            [sum(polynomial.get((i, j), 0) for i in range(3)) for j in range(3)]
        )
    if edge == "bottom":
        return trim_univariate([polynomial.get((i, 0), 0) for i in range(3)])
    if edge == "top":
        return trim_univariate(
            [sum(polynomial.get((i, j), 0) for j in range(3)) for i in range(3)]
        )
    raise ValueError(edge)


def ordered_single_roots(records, edge, eligible=None):
    if eligible is None:
        eligible = records
    rows = sorted(
        (records[factor_id][edge], factor_id)
        for factor_id in eligible
        if records[factor_id][edge] is not None
    )
    for (first, left_id), (second, right_id) in zip(rows, rows[1:]):
        if first[1] >= second[0]:
            raise AssertionError(
                f"boundary root boxes overlap on {edge}: {left_id}, {right_id}"
            )
    return rows


def inversion_count(sequence):
    tree = [0] * (len(sequence) + 1)

    def insert(index):
        index += 1
        while index < len(tree):
            tree[index] += 1
            index += index & -index

    def prefix(length):
        answer = 0
        while length:
            answer += tree[length]
            length -= length & -length
        return answer

    answer = 0
    for seen, value in enumerate(sequence):
        answer += seen - prefix(value + 1)
        insert(value)
    return answer


def forced_inversions(records, first_edge, second_edge):
    edges = {"left", "right", "bottom", "top"}
    eligible = {
        factor_id
        for factor_id, row in records.items()
        if row[first_edge] is not None
        and row[second_edge] is not None
        and all(row[other] is None for other in edges - {first_edge, second_edge})
    }
    first = ordered_single_roots(records, first_edge, eligible)
    second = ordered_single_roots(records, second_edge, eligible)
    second_rank = {
        factor_id: rank for rank, (_interval, factor_id) in enumerate(second)
    }
    return eligible, inversion_count(
        [second_rank[factor_id] for _interval, factor_id in first]
    )


def id_digest(domain, identifiers):
    digest = sha256(domain + b"\0")
    for identifier in identifiers:
        digest.update(int(identifier).to_bytes(4, "little"))
    return digest.hexdigest()


def build_record(progress=False):
    _matrices, points, _packed, _states, _hamming, _multiplicity = (
        transition.exact_inputs()
    )
    source = points[SOURCE_CHART]
    target = points[TARGET_CHART]
    corners = tuple(
        bridge.hybrid_vertex(source, target, mask) for mask in (0, 1, 2, 3)
    )

    records = [
        json.loads(line)
        for line in bridge.safe.CATALOG.read_text().splitlines()
        if line
    ]
    parents, parent_digest = gate.parent_polynomials(records[2599])
    parent_degrees = Counter()
    parent_minimum = None
    parent_minimum_label = None
    for label, target_sign, polynomial, _terms in parents:
        square = restrict_square(polynomial, source, target)
        degree = max(i for i, _j in square), max(j for _i, j in square)
        parent_degrees[degree] += 1
        if degree[0] > 1 or degree[1] > 1:
            raise AssertionError(f"parent bracket {label} is not bilinear")
        values = tuple(
            target_sign * evaluate_bivariate(square, Fraction(s), Fraction(t))
            for s, t in ((0, 0), (1, 0), (0, 1), (1, 1))
        )
        if min(values) <= 0:
            raise AssertionError(f"parent bracket {label} fails at a square corner")
        if parent_minimum is None or min(values) < parent_minimum:
            parent_minimum = min(values)
            parent_minimum_label = label

    candidates = gate.parse_candidates()
    _factor_types, _factor_terms, polynomials = labeled.factor_polynomials()
    degree_census = Counter()
    status_census = Counter()
    depth_census = Counter()
    active = []
    empty = []
    active_polynomials = {}
    classification = sha256(b"diag3-source-square-wall-classification-v1\0")
    for index, factor_id in enumerate(candidates):
        square = restrict_square(polynomials[factor_id], source, target)
        if not square:
            raise AssertionError(f"factor {factor_id} restricts identically to zero")
        first_degree = max(i for i, _j in square)
        second_degree = max(j for _i, j in square)
        degree_census[first_degree, second_degree] += 1
        if first_degree == second_degree == 0:
            status, depth, visited = "EMPTY_CONSTANT", 0, 1
        else:
            status, depth, visited = classify_bernstein(bernstein_grid(square))
        if status == "UNRESOLVED":
            raise AssertionError(f"unresolved square feasibility for factor {factor_id}")
        status_census[status] += 1
        depth_census[status, depth] += 1
        classification.update(factor_id.to_bytes(4, "little"))
        classification.update(bytes((first_degree, second_degree, depth, visited)))
        classification.update(status.encode("ascii") + b"\0")
        classification.update(repr(canonical_integer(square)).encode("ascii"))
        if status == "NONEMPTY_SIGN_CHANGE":
            active.append(factor_id)
            active_polynomials[factor_id] = square
        else:
            empty.append(factor_id)
        if progress and (index + 1) % 4000 == 0:
            print(f"classified {index + 1}/{len(candidates)} square walls", flush=True)

    graph_type = 0
    biquadratic = 0
    discriminant_root_census = Counter()
    discriminant_system = sha256(b"diag3-source-square-biquadratic-critical-v1\0")
    positive_bounded_intervals = 0
    two_root_bounded_intervals = 0
    boundary_hit_intervals = 0
    compact_oval_candidates = []
    for factor_id in active:
        square = active_polynomials[factor_id]
        first_degree = max(i for i, _j in square)
        second_degree = max(j for _i, j in square)
        if first_degree <= 1 or second_degree <= 1:
            graph_type += 1
            continue
        biquadratic += 1
        constant, linear, quadratic = coefficient_rows(square)
        discriminant = add_univariate(
            multiply_univariate(linear, linear),
            multiply_univariate(quadratic, constant),
            scale=-4,
        )
        if len(gcd_univariate(discriminant, derivative_univariate(discriminant))) > 1:
            raise AssertionError(f"repeated projection discriminant at factor {factor_id}")
        if not evaluate_univariate(discriminant, Fraction(0)):
            raise AssertionError(f"left-edge discriminant endpoint at factor {factor_id}")
        if not evaluate_univariate(discriminant, Fraction(1)):
            raise AssertionError(f"right-edge discriminant endpoint at factor {factor_id}")
        roots = isolate_roots(discriminant)
        discriminant_root_census[len(roots)] += 1
        upper_boundary = add_univariate(
            add_univariate(quadratic, linear), constant
        )
        discriminant_system.update(factor_id.to_bytes(4, "little"))
        discriminant_system.update(bytes((len(roots),)))
        for root in roots:
            for endpoint in root:
                discriminant_system.update(
                    endpoint.numerator.to_bytes(32, "little", signed=True)
                )
                discriminant_system.update(
                    endpoint.denominator.to_bytes(32, "little")
                )
        for interval_index in range(len(roots) + 1):
            left = roots[interval_index - 1][1] if interval_index else Fraction(0)
            right = roots[interval_index][0] if interval_index < len(roots) else Fraction(1)
            sample = (left + right) / 2
            if evaluate_univariate(discriminant, sample) <= 0:
                continue
            if interval_index and interval_index < len(roots):
                positive_bounded_intervals += 1
            t_polynomial = [
                evaluate_univariate(constant, sample),
                evaluate_univariate(linear, sample),
                evaluate_univariate(quadratic, sample),
            ]
            t_roots = sturm.root_count(
                trim_univariate(t_polynomial), Fraction(0), Fraction(1)
            )
            if not (interval_index and interval_index < len(roots) and t_roots == 2):
                continue
            two_root_bounded_intervals += 1
            first = roots[interval_index - 1]
            second = roots[interval_index]
            tangent_overlap = tuple(
                (
                    sturm.root_count(boundary, first[0], first[1]),
                    sturm.root_count(boundary, second[0], second[1]),
                )
                for boundary in (constant, upper_boundary)
            )
            if any(left_count or right_count for left_count, right_count in tangent_overlap):
                raise AssertionError(
                    f"boundary root unresolved inside a tangent box at factor {factor_id}"
                )
            boundary_counts = (
                sturm.root_count(constant, first[1], second[0]),
                sturm.root_count(upper_boundary, first[1], second[0]),
            )
            if any(boundary_counts):
                boundary_hit_intervals += 1
            else:
                compact_oval_candidates.append(factor_id)
    if compact_oval_candidates:
        raise AssertionError(
            f"source square contains compact oval candidates: {compact_oval_candidates}"
        )

    edges = ("left", "right", "bottom", "top")
    boundary_records = {}
    root_census = Counter()
    boundary_semantic = sha256(b"diag3-source-square-boundary-inversions-v1\0")
    for factor_id in active:
        row = {}
        for edge in edges:
            polynomial = edge_polynomial(active_polynomials[factor_id], edge)
            count = sturm.root_count(polynomial, Fraction(0), Fraction(1))
            root_census[edge, count] += 1
            if count == 1:
                if len(gcd_univariate(polynomial, derivative_univariate(polynomial))) > 1:
                    raise AssertionError(
                        f"nonsimple single boundary root at {factor_id} on {edge}"
                    )
                row[edge] = isolate_roots(polynomial)[0]
            else:
                row[edge] = None
        boundary_records[factor_id] = row
        boundary_semantic.update(factor_id.to_bytes(4, "little"))
        for edge in edges:
            interval = row[edge]
            boundary_semantic.update(bytes((interval is not None,)))
            if interval is not None:
                for endpoint in interval:
                    boundary_semantic.update(
                        endpoint.numerator.to_bytes(32, "little", signed=True)
                    )
                    boundary_semantic.update(
                        endpoint.denominator.to_bytes(32, "little")
                    )
    for edge in edges:
        ordered_single_roots(boundary_records, edge)
    left_right, left_right_inversions = forced_inversions(
        boundary_records, "left", "right"
    )
    bottom_top, bottom_top_inversions = forced_inversions(
        boundary_records, "bottom", "top"
    )
    if left_right & bottom_top:
        raise AssertionError("opposite-edge inversion families overlap")

    return {
        "format": FORMAT,
        "status": STATUS,
        "scope": {
            "parent_index": 2599,
            "source_chart": SOURCE_CHART,
            "target_chart": TARGET_CHART,
            "varying_column_blocks": list(VARIABLE_BLOCKS),
            "fixed_column_block": FIXED_BLOCK,
            "parameter_domain": "closed unit square",
            "parent_parameter_coverage": "COMPLETE_ON_SOURCE_SQUARE",
            "wall_component_coverage": "EVERY_OCCURRING_WALL_COMPONENT_MEETS_SQUARE_BOUNDARY",
            "full_arrangement_cell_coverage": "NOT_CLAIMED",
            "global_parent_cell_coverage": "NOT_CLAIMED",
        },
        "parent_square": {
            "parent_brackets": len(parents),
            "parent_polynomial_digest": parent_digest,
            "restriction_bidegree_census": {
                f"{first},{second}": count
                for (first, second), count in sorted(parent_degrees.items())
            },
            "strict_corners": len(corners),
            "minimum_signed_corner_margin": fraction_text(parent_minimum),
            "minimum_margin_bracket": parent_minimum_label,
            "coverage_argument": "bilinear Bernstein coefficients are the four positive corner values",
        },
        "wall_feasibility": {
            "candidate_factors": len(candidates),
            "restriction_bidegree_census": {
                f"{first},{second}": count
                for (first, second), count in sorted(degree_census.items())
            },
            "status_census": dict(sorted(status_census.items())),
            "classification_depth_census": {
                f"{status}:{depth}": count
                for (status, depth), count in sorted(depth_census.items())
            },
            "occurring_walls": len(active),
            "zero_free_walls": len(empty),
            "unresolved_walls": 0,
            "occurring_factor_ids_sha256": id_digest(
                b"diag3-source-square-occurring-factor-ids-v1", active
            ),
            "zero_free_factor_ids_sha256": id_digest(
                b"diag3-source-square-zero-free-factor-ids-v1", empty
            ),
            "classification_semantic_sha256": classification.hexdigest(),
        },
        "wall_component_coverage": {
            "graph_type_walls": graph_type,
            "biquadratic_walls": biquadratic,
            "squarefree_projection_discriminants": biquadratic,
            "endpoint_projection_degeneracies": 0,
            "discriminant_root_census": {
                str(key): value for key, value in sorted(discriminant_root_census.items())
            },
            "positive_bounded_projection_intervals": positive_bounded_intervals,
            "two_root_bounded_projection_intervals": two_root_bounded_intervals,
            "boundary_hit_two_root_intervals": boundary_hit_intervals,
            "ambiguous_tangent_boxes": 0,
            "compact_oval_candidates": 0,
            "critical_semantic_sha256": discriminant_system.hexdigest(),
            "conclusion": "EVERY_OCCURRING_WALL_COMPONENT_MEETS_SQUARE_BOUNDARY",
        },
        "boundary_complexity_frontier": {
            "root_census": {
                f"{edge}:{count}": value
                for (edge, count), value in sorted(root_census.items())
            },
            "overlapping_single_root_boxes": 0,
            "left_right_arc_walls": len(left_right),
            "left_right_forced_intersecting_pairs": left_right_inversions,
            "bottom_top_arc_walls": len(bottom_top),
            "bottom_top_forced_intersecting_pairs": bottom_top_inversions,
            "disjoint_forced_intersecting_pair_lower_bound": (
                left_right_inversions + bottom_top_inversions
            ),
            "boundary_semantic_sha256": boundary_semantic.hexdigest(),
            "decision": "SUBORDINATE_FULL_SIGN_INVARIANT_SQUARE_ARRANGEMENT; RETAIN_COMPONENT_COVERAGE_QUOTIENT",
        },
        "theorem_effect": (
            "Exact wall-component coverage on one parent-resident source square; "
            "global pair coverage and the independent triple obligation remain open; "
            "honest 9DVL score remains 2/9."
        ),
    }

