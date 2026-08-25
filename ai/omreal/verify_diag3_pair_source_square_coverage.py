#!/usr/bin/env python3
"""Independent exact replay of source-square wall-component coverage."""

from __future__ import annotations

from collections import Counter
import copy
from fractions import Fraction
from hashlib import sha256
from math import comb, gcd, lcm
from pathlib import Path
import json
import sys


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_SOURCE_SQUARE_COVERAGE_0_152.json"
EXPECTED_CERTIFICATE_SHA256 = "f5d6ce8df2792a681843a8593b201ab46834fd623f170bc82cf7ec1b2e8caa61"
ROOT_WIDTH = Fraction(1, 1 << 64)

sys.path.insert(0, str(HERE))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402
import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


class CertificateError(AssertionError):
    pass


def require(condition, message):
    if not condition:
        raise CertificateError(message)


def clean(polynomial):
    return {monomial: value for monomial, value in polynomial.items() if value}


def product(left, right):
    answer = {}
    for (i, j), first in left.items():
        for (k, ell), second in right.items():
            key = i + k, j + ell
            answer[key] = answer.get(key, Fraction(0)) + first * second
    return clean(answer)


def square_pullback(polynomial, source, target):
    """Independent direct expansion in square parameters u and v."""

    answer = {}
    coordinate_powers = []
    for variable in range(9):
        block = variable // 3
        if block == 0:
            linear = {(0, 0): source[variable], (1, 0): target[variable] - source[variable]}
        elif block == 1:
            linear = {(0, 0): source[variable], (0, 1): target[variable] - source[variable]}
        else:
            linear = {(0, 0): source[variable]}
        powers = ({(0, 0): Fraction(1)}, linear)
        powers += (product(linear, linear),)
        coordinate_powers.append(powers)
    for exponent, coefficient in polynomial.items():
        term = {(0, 0): Fraction(coefficient)}
        for variable, power in enumerate(exponent):
            term = product(term, coordinate_powers[variable][power])
        for monomial, value in term.items():
            answer[monomial] = answer.get(monomial, Fraction(0)) + value
    return clean(answer)


def canonical(polynomial):
    denominator = 1
    for value in polynomial.values():
        denominator = lcm(denominator, value.denominator)
    integer = {monomial: int(value * denominator) for monomial, value in polynomial.items()}
    divisor = 0
    for value in integer.values():
        divisor = gcd(divisor, abs(value))
    integer = {monomial: value // max(divisor, 1) for monomial, value in integer.items()}
    if integer[max(integer)] < 0:
        integer = {monomial: -value for monomial, value in integer.items()}
    return tuple(sorted(integer.items()))


def evaluate2(polynomial, u, v):
    return sum(value * u**i * v**j for (i, j), value in polynomial.items())


def bernstein(polynomial):
    du = max(i for i, _j in polynomial)
    dv = max(j for _i, j in polynomial)
    return tuple(
        tuple(
            sum(
                value
                * Fraction(comb(i, p), comb(du, p))
                * Fraction(comb(j, q), comb(dv, q))
                for (p, q), value in polynomial.items()
                if p <= i and q <= j
            )
            for j in range(dv + 1)
        )
        for i in range(du + 1)
    )


def halve(values):
    triangle = [list(values)]
    while len(triangle[-1]) > 1:
        triangle.append(
            [(left + right) / 2 for left, right in zip(triangle[-1], triangle[-1][1:])]
        )
    return (
        tuple(row[0] for row in triangle),
        tuple(row[-1] for row in reversed(triangle)),
    )


def quarters(grid):
    split_columns = tuple(halve(column) for column in zip(*grid))
    west = tuple(
        tuple(parts[0][index] for parts in split_columns)
        for index in range(len(grid))
    )
    east = tuple(
        tuple(parts[1][index] for parts in split_columns)
        for index in range(len(grid))
    )
    west_rows = tuple(halve(row) for row in west)
    east_rows = tuple(halve(row) for row in east)
    return (
        tuple(parts[0] for parts in west_rows),
        tuple(parts[0] for parts in east_rows),
        tuple(parts[1] for parts in west_rows),
        tuple(parts[1] for parts in east_rows),
    )


def sign_set(values):
    return {1 if value > 0 else -1 if value < 0 else 0 for value in values}


def box_decision(grid):
    pending = [(grid, 0)]
    visits = 0
    maximum = 0
    while pending:
        current, depth = pending.pop()
        visits += 1
        controls = sign_set(value for row in current for value in row)
        if 0 not in controls and len(controls) == 1:
            continue
        corners = sign_set(
            (current[0][0], current[-1][0], current[0][-1], current[-1][-1])
        )
        if 0 in corners or {-1, 1} <= corners:
            return "NONEMPTY_SIGN_CHANGE", depth, visits
        maximum = max(maximum, depth)
        require(depth < 10, "adaptive Bernstein frontier unresolved")
        pending.extend((child, depth + 1) for child in quarters(current))
    return "EMPTY_BERNSTEIN", maximum, visits


def trim(polynomial):
    polynomial = [Fraction(value) for value in polynomial]
    while len(polynomial) > 1 and not polynomial[-1]:
        polynomial.pop()
    return polynomial


def plus(left, right, scale=1):
    answer = [Fraction(0)] * max(len(left), len(right))
    for index, value in enumerate(left):
        answer[index] += value
    for index, value in enumerate(right):
        answer[index] += scale * value
    return trim(answer)


def times(left, right):
    answer = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, first in enumerate(left):
        for j, second in enumerate(right):
            answer[i + j] += first * second
    return trim(answer)


def derivative(polynomial):
    return trim([index * value for index, value in enumerate(polynomial)][1:] or [0])


def quotient_remainder(dividend, divisor):
    dividend, divisor = trim(dividend), trim(divisor)
    quotient = [Fraction(0)] * max(1, len(dividend) - len(divisor) + 1)
    while len(dividend) >= len(divisor) and any(dividend):
        shift = len(dividend) - len(divisor)
        scale = dividend[-1] / divisor[-1]
        quotient[shift] = scale
        for index, value in enumerate(divisor):
            dividend[index + shift] -= scale * value
        dividend = trim(dividend)
    return trim(quotient), trim(dividend)


def polynomial_gcd(left, right):
    left, right = trim(left), trim(right)
    while any(right):
        _quotient, remainder = quotient_remainder(left, right)
        left, right = right, remainder
    return trim([value / left[-1] for value in left]) if any(left) else [Fraction(0)]


def evaluate1(polynomial, argument):
    answer = Fraction(0)
    for coefficient in reversed(polynomial):
        answer = answer * argument + coefficient
    return answer


def isolate(polynomial):
    require(evaluate1(polynomial, Fraction(0)) != 0, "root at zero endpoint")
    require(evaluate1(polynomial, Fraction(1)) != 0, "root at one endpoint")
    pending = [(Fraction(0), Fraction(1), sturm.root_count(polynomial, Fraction(0), Fraction(1)))]
    roots = []
    while pending:
        left, right, count = pending.pop()
        if not count:
            continue
        if count == 1 and right - left <= ROOT_WIDTH:
            roots.append((left, right))
            continue
        middle = (left + right) / 2
        while not evaluate1(polynomial, middle):
            middle = (left + middle) / 2
        left_count = sturm.root_count(polynomial, left, middle)
        right_count = sturm.root_count(polynomial, middle, right)
        require(left_count + right_count == count, "Sturm isolation lost a root")
        pending.extend(((middle, right, right_count), (left, middle, left_count)))
    return tuple(sorted(roots))


def rows_in_v(polynomial):
    rows = [[Fraction(0)] * 3 for _ in range(3)]
    for (u_degree, v_degree), value in polynomial.items():
        rows[v_degree][u_degree] = value
    return tuple(trim(row) for row in rows)


def boundary_polynomial(polynomial, side):
    if side == "left":
        return trim([polynomial.get((0, j), 0) for j in range(3)])
    if side == "right":
        return trim([sum(polynomial.get((i, j), 0) for i in range(3)) for j in range(3)])
    if side == "bottom":
        return trim([polynomial.get((i, 0), 0) for i in range(3)])
    return trim([sum(polynomial.get((i, j), 0) for j in range(3)) for i in range(3)])


def identifiers_digest(domain, identifiers):
    digest = sha256(domain + b"\0")
    for identifier in identifiers:
        digest.update(identifier.to_bytes(4, "little"))
    return digest.hexdigest()


def ordered_roots(boundary, side, eligible=None):
    eligible = boundary if eligible is None else eligible
    rows = sorted(
        (boundary[factor_id][side], factor_id)
        for factor_id in eligible
        if boundary[factor_id][side] is not None
    )
    for (first, left), (second, right) in zip(rows, rows[1:]):
        require(first[1] < second[0], f"overlapping {side} roots {left}/{right}")
    return rows


def count_inversions(sequence):
    def merge_count(values):
        if len(values) < 2:
            return values, 0
        middle = len(values) // 2
        left, left_count = merge_count(values[:middle])
        right, right_count = merge_count(values[middle:])
        merged = []
        count = left_count + right_count
        i = j = 0
        while i < len(left) and j < len(right):
            if left[i] <= right[j]:
                merged.append(left[i])
                i += 1
            else:
                merged.append(right[j])
                count += len(left) - i
                j += 1
        return merged + left[i:] + right[j:], count

    return merge_count(list(sequence))[1]


def opposite_order(boundary, first, second):
    sides = {"left", "right", "bottom", "top"}
    eligible = {
        factor_id
        for factor_id, row in boundary.items()
        if row[first] is not None
        and row[second] is not None
        and all(row[side] is None for side in sides - {first, second})
    }
    first_order = ordered_roots(boundary, first, eligible)
    second_order = ordered_roots(boundary, second, eligible)
    rank = {factor_id: index for index, (_interval, factor_id) in enumerate(second_order)}
    return eligible, count_inversions(rank[factor_id] for _interval, factor_id in first_order)


def recompute():
    _matrices, points, _packed, _states, _hamming, _multiplicity = transition.exact_inputs()
    source, target = points[0], points[152]
    records = [json.loads(line) for line in safe.CATALOG.read_text().splitlines() if line]
    parents, parent_digest = gate.parent_polynomials(records[2599])
    parent_degrees = Counter()
    minimum = None
    minimum_label = None
    for label, target_sign, polynomial, _terms in parents:
        pulled = square_pullback(polynomial, source, target)
        degrees = max(i for i, _j in pulled), max(j for _i, j in pulled)
        parent_degrees[degrees] += 1
        require(max(degrees) <= 1, "parent restriction is not bilinear")
        corners = tuple(
            target_sign * evaluate2(pulled, Fraction(i), Fraction(j))
            for i, j in ((0, 0), (1, 0), (0, 1), (1, 1))
        )
        require(min(corners) > 0, f"parent corner failure {label}")
        if minimum is None or min(corners) < minimum:
            minimum, minimum_label = min(corners), label

    candidates = gate.parse_candidates()
    _types, _terms, polynomials = labeled.factor_polynomials()
    degree_census = Counter()
    status_census = Counter()
    depth_census = Counter()
    classification = sha256(b"diag3-source-square-wall-classification-v1\0")
    active, empty, pulled_active = [], [], {}
    for factor_id in candidates:
        pulled = square_pullback(polynomials[factor_id], source, target)
        require(pulled, "identically zero wall restriction")
        du, dv = max(i for i, _j in pulled), max(j for _i, j in pulled)
        degree_census[du, dv] += 1
        if du == dv == 0:
            status, depth, visits = "EMPTY_CONSTANT", 0, 1
        else:
            status, depth, visits = box_decision(bernstein(pulled))
        status_census[status] += 1
        depth_census[status, depth] += 1
        classification.update(factor_id.to_bytes(4, "little"))
        classification.update(bytes((du, dv, depth, visits)))
        classification.update(status.encode("ascii") + b"\0")
        classification.update(repr(canonical(pulled)).encode("ascii"))
        if status == "NONEMPTY_SIGN_CHANGE":
            active.append(factor_id)
            pulled_active[factor_id] = pulled
        else:
            empty.append(factor_id)

    graph_type = biquadratic = 0
    discriminant_roots = Counter()
    critical = sha256(b"diag3-source-square-biquadratic-critical-v1\0")
    positive_bounded = two_inside = boundary_hit = 0
    for factor_id in active:
        pulled = pulled_active[factor_id]
        du, dv = max(i for i, _j in pulled), max(j for _i, j in pulled)
        if du <= 1 or dv <= 1:
            graph_type += 1
            continue
        biquadratic += 1
        constant, linear, quadratic = rows_in_v(pulled)
        discriminant = plus(times(linear, linear), times(quadratic, constant), scale=-4)
        require(len(polynomial_gcd(discriminant, derivative(discriminant))) == 1, "repeated discriminant")
        roots = isolate(discriminant)
        discriminant_roots[len(roots)] += 1
        critical.update(factor_id.to_bytes(4, "little"))
        critical.update(bytes((len(roots),)))
        for root in roots:
            for endpoint in root:
                critical.update(endpoint.numerator.to_bytes(32, "little", signed=True))
                critical.update(endpoint.denominator.to_bytes(32, "little"))
        upper = plus(plus(quadratic, linear), constant)
        for index in range(len(roots) + 1):
            left = roots[index - 1][1] if index else Fraction(0)
            right = roots[index][0] if index < len(roots) else Fraction(1)
            sample = (left + right) / 2
            if evaluate1(discriminant, sample) <= 0:
                continue
            bounded = bool(index and index < len(roots))
            positive_bounded += bounded
            t_poly = [evaluate1(constant, sample), evaluate1(linear, sample), evaluate1(quadratic, sample)]
            roots_inside = sturm.root_count(trim(t_poly), Fraction(0), Fraction(1))
            if not (bounded and roots_inside == 2):
                continue
            two_inside += 1
            first, second = roots[index - 1], roots[index]
            for boundary in (constant, upper):
                require(
                    sturm.root_count(boundary, first[0], first[1]) == 0
                    and sturm.root_count(boundary, second[0], second[1]) == 0,
                    "boundary root inside tangent box",
                )
            counts = (
                sturm.root_count(constant, first[1], second[0]),
                sturm.root_count(upper, first[1], second[0]),
            )
            require(any(counts), "compact oval candidate")
            boundary_hit += 1

    sides = ("left", "right", "bottom", "top")
    boundary = {}
    root_census = Counter()
    boundary_digest = sha256(b"diag3-source-square-boundary-inversions-v1\0")
    for factor_id in active:
        row = {}
        for side in sides:
            polynomial = boundary_polynomial(pulled_active[factor_id], side)
            count = sturm.root_count(polynomial, Fraction(0), Fraction(1))
            root_census[side, count] += 1
            if count == 1:
                require(len(polynomial_gcd(polynomial, derivative(polynomial))) == 1, "nonsimple boundary root")
                row[side] = isolate(polynomial)[0]
            else:
                row[side] = None
        boundary[factor_id] = row
        boundary_digest.update(factor_id.to_bytes(4, "little"))
        for side in sides:
            interval = row[side]
            boundary_digest.update(bytes((interval is not None,)))
            if interval is not None:
                for endpoint in interval:
                    boundary_digest.update(endpoint.numerator.to_bytes(32, "little", signed=True))
                    boundary_digest.update(endpoint.denominator.to_bytes(32, "little"))
    for side in sides:
        ordered_roots(boundary, side)
    left_right, lr_inversions = opposite_order(boundary, "left", "right")
    bottom_top, bt_inversions = opposite_order(boundary, "bottom", "top")
    require(not (left_right & bottom_top), "opposite arc families overlap")

    return {
        "parent_digest": parent_digest,
        "parent_degrees": parent_degrees,
        "minimum": minimum,
        "minimum_label": minimum_label,
        "candidate_count": len(candidates),
        "degree_census": degree_census,
        "status_census": status_census,
        "depth_census": depth_census,
        "active": active,
        "empty": empty,
        "classification": classification.hexdigest(),
        "graph_type": graph_type,
        "biquadratic": biquadratic,
        "discriminant_roots": discriminant_roots,
        "positive_bounded": positive_bounded,
        "two_inside": two_inside,
        "boundary_hit": boundary_hit,
        "critical": critical.hexdigest(),
        "root_census": root_census,
        "left_right": left_right,
        "lr_inversions": lr_inversions,
        "bottom_top": bottom_top,
        "bt_inversions": bt_inversions,
        "boundary_digest": boundary_digest.hexdigest(),
    }


def validate(record, replay):
    require(record["format"] == "diag3-pair-source-square-component-coverage-v1", "format")
    require(record["status"] == "EXACT_SOURCE_SQUARE_WALL_COMPONENT_COVERAGE", "status")
    scope = record["scope"]
    require((scope["parent_index"], scope["source_chart"], scope["target_chart"]) == (2599, 0, 152), "scope indices")
    require(scope["varying_column_blocks"] == [0, 1] and scope["fixed_column_block"] == 2, "square blocks")
    require(scope["parent_parameter_coverage"] == "COMPLETE_ON_SOURCE_SQUARE", "parent coverage")
    require(scope["wall_component_coverage"] == "EVERY_OCCURRING_WALL_COMPONENT_MEETS_SQUARE_BOUNDARY", "component coverage")
    require(scope["full_arrangement_cell_coverage"] == scope["global_parent_cell_coverage"] == "NOT_CLAIMED", "dishonest global scope")

    parent = record["parent_square"]
    require(parent["parent_brackets"] == 70 and parent["strict_corners"] == 4, "parent census")
    require(parent["parent_polynomial_digest"] == replay["parent_digest"], "parent digest")
    require(parent["restriction_bidegree_census"] == {f"{i},{j}": count for (i, j), count in sorted(replay["parent_degrees"].items())}, "parent bidegrees")
    require(parent["minimum_signed_corner_margin"] == str(replay["minimum"].numerator) + "/" + str(replay["minimum"].denominator), "parent margin")
    require(parent["minimum_margin_bracket"] == replay["minimum_label"], "parent margin label")

    feasibility = record["wall_feasibility"]
    require(feasibility["candidate_factors"] == replay["candidate_count"] == 17_824, "factor universe")
    require(feasibility["restriction_bidegree_census"] == {f"{i},{j}": count for (i, j), count in sorted(replay["degree_census"].items())}, "factor bidegrees")
    require(feasibility["status_census"] == dict(sorted(replay["status_census"].items())), "status census")
    require(feasibility["classification_depth_census"] == {f"{status}:{depth}": count for (status, depth), count in sorted(replay["depth_census"].items())}, "depth census")
    require((feasibility["occurring_walls"], feasibility["zero_free_walls"], feasibility["unresolved_walls"]) == (len(replay["active"]), len(replay["empty"]), 0) == (3_763, 14_061, 0), "wall trichotomy")
    require(feasibility["occurring_factor_ids_sha256"] == identifiers_digest(b"diag3-source-square-occurring-factor-ids-v1", replay["active"]), "active digest")
    require(feasibility["zero_free_factor_ids_sha256"] == identifiers_digest(b"diag3-source-square-zero-free-factor-ids-v1", replay["empty"]), "empty digest")
    require(feasibility["classification_semantic_sha256"] == replay["classification"], "classification semantic")

    coverage = record["wall_component_coverage"]
    require((coverage["graph_type_walls"], coverage["biquadratic_walls"]) == (replay["graph_type"], replay["biquadratic"]) == (2_531, 1_232), "component type census")
    require(coverage["squarefree_projection_discriminants"] == 1_232, "squarefree discriminants")
    require(coverage["discriminant_root_census"] == {str(key): value for key, value in sorted(replay["discriminant_roots"].items())} == {"0": 1009, "1": 181, "2": 42}, "discriminant roots")
    require((coverage["positive_bounded_projection_intervals"], coverage["two_root_bounded_projection_intervals"], coverage["boundary_hit_two_root_intervals"]) == (replay["positive_bounded"], replay["two_inside"], replay["boundary_hit"]) == (0, 0, 0), "oval screen")
    require(coverage["ambiguous_tangent_boxes"] == coverage["compact_oval_candidates"] == 0, "unresolved oval frontier")
    require(coverage["critical_semantic_sha256"] == replay["critical"], "critical semantic")
    require(coverage["conclusion"] == "EVERY_OCCURRING_WALL_COMPONENT_MEETS_SQUARE_BOUNDARY", "coverage conclusion")

    frontier = record["boundary_complexity_frontier"]
    require(frontier["root_census"] == {f"{edge}:{count}": value for (edge, count), value in sorted(replay["root_census"].items())}, "boundary root census")
    require((frontier["left_right_arc_walls"], frontier["left_right_forced_intersecting_pairs"]) == (len(replay["left_right"]), replay["lr_inversions"]) == (220, 11_060), "left-right inversions")
    require((frontier["bottom_top_arc_walls"], frontier["bottom_top_forced_intersecting_pairs"]) == (len(replay["bottom_top"]), replay["bt_inversions"]) == (1_903, 607_060), "bottom-top inversions")
    require(frontier["disjoint_forced_intersecting_pair_lower_bound"] == replay["lr_inversions"] + replay["bt_inversions"] == 618_120, "intersection-pair lower bound")
    require(frontier["boundary_semantic_sha256"] == replay["boundary_digest"], "boundary semantic")
    require(frontier["overlapping_single_root_boxes"] == 0, "root-box overlap")
    require(frontier["decision"].startswith("SUBORDINATE_FULL_SIGN_INVARIANT"), "strategy decision")
    require("2/9" in record["theorem_effect"] and "remain open" in record["theorem_effect"], "dishonest theorem effect")


def assert_rejected(record, replay, label):
    try:
        validate(record, replay)
    except (CertificateError, AssertionError, KeyError, ValueError, TypeError):
        return
    raise AssertionError(f"hostile canary accepted: {label}")


def main():
    require(sha256(CERTIFICATE.read_bytes()).hexdigest() == EXPECTED_CERTIFICATE_SHA256, "certificate digest")
    record = json.loads(CERTIFICATE.read_text())
    replay = recompute()
    validate(record, replay)

    hostile = []
    corrupt = copy.deepcopy(record)
    corrupt["scope"]["global_parent_cell_coverage"] = "COMPLETE"
    hostile.append((corrupt, "source square promoted to global coverage"))
    corrupt = copy.deepcopy(record)
    corrupt["parent_square"]["strict_corners"] = 3
    hostile.append((corrupt, "missing parent corner"))
    corrupt = copy.deepcopy(record)
    corrupt["wall_feasibility"]["occurring_walls"] -= 1
    hostile.append((corrupt, "wall feasibility census"))
    corrupt = copy.deepcopy(record)
    corrupt["wall_feasibility"]["classification_semantic_sha256"] = "0" * 64
    hostile.append((corrupt, "classification digest"))
    corrupt = copy.deepcopy(record)
    corrupt["wall_component_coverage"]["squarefree_projection_discriminants"] -= 1
    hostile.append((corrupt, "missing discriminant"))
    corrupt = copy.deepcopy(record)
    corrupt["wall_component_coverage"]["compact_oval_candidates"] = 1
    hostile.append((corrupt, "hidden oval"))
    corrupt = copy.deepcopy(record)
    corrupt["wall_component_coverage"]["critical_semantic_sha256"] = "0" * 64
    hostile.append((corrupt, "critical digest"))
    corrupt = copy.deepcopy(record)
    corrupt["boundary_complexity_frontier"]["bottom_top_arc_walls"] -= 1
    hostile.append((corrupt, "arc census"))
    corrupt = copy.deepcopy(record)
    corrupt["boundary_complexity_frontier"]["left_right_forced_intersecting_pairs"] -= 1
    hostile.append((corrupt, "inversion count"))
    corrupt = copy.deepcopy(record)
    corrupt["boundary_complexity_frontier"]["overlapping_single_root_boxes"] = 1
    hostile.append((corrupt, "overlapping root boxes"))
    corrupt = copy.deepcopy(record)
    corrupt["boundary_complexity_frontier"]["decision"] = "BUILD_FULL_ARRANGEMENT"
    hostile.append((corrupt, "wrong strategy decision"))
    corrupt = copy.deepcopy(record)
    corrupt["theorem_effect"] = "Diagonal three proved; score 3/9."
    hostile.append((corrupt, "dishonest theorem promotion"))
    for corrupt, label in hostile:
        assert_rejected(corrupt, replay, label)

    print("PASS exact chart-0/chart-152 parent-resident source square")
    print("PASS 17,824 wall restrictions: 3,763 occurring / 14,061 zero-free / 0 unresolved")
    print("PASS every occurring wall component meets the source-square boundary")
    print("PASS 1,232 squarefree biquadratic discriminants; 0 compact-oval intervals")
    print("PASS 618,120 disjoint forced intersecting curve pairs")
    print("CLASSIFICATION_SEMANTIC", replay["classification"])
    print("CRITICAL_SEMANTIC", replay["critical"])
    print("BOUNDARY_SEMANTIC", replay["boundary_digest"])
    print("PASS 12/12 hostile corruptions rejected")
    print("SCOPE exact component coverage on one source square; global pair coverage remains open")


if __name__ == "__main__":
    main()
