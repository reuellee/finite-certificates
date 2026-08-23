#!/usr/bin/env python3
"""Exact first projection for the parent-860 ``(h,i)`` coordinate plane.

This is the proof-producing first stage of the coverage atlas selected by
``data/DIAG9_RESEARCH_DECISION_LEDGER.json``.  It substitutes the seven fixed
parent-860 coordinates into all 26,740 primitive residual factors, factors the
resulting bivariate polynomials over ``QQ``, and reconstructs the exact parent
cell cut out by the 70 parent brackets.  Later stages may only discard a plane
factor after an exact nonintersection certificate with that parent cell.

The script is intentionally useful before the full atlas exists: ``--census``
prints the exact projection-growth frontier and fails if the selected parent
slice is not a bounded polygon.  No connectivity conclusion is made here.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations
from math import gcd, lcm
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as representative  # noqa: E402
import DIAG9_GRAPH_parent860_star as star  # noqa: E402


VARIABLES = (7, 8)


def restrict_plane(polynomial, base):
    """Substitute all variables except ``h`` and ``i`` exactly."""

    answer = defaultdict(Fraction)
    for exponent, coefficient in polynomial.items():
        value = Fraction(coefficient)
        for axis, power in enumerate(exponent):
            if axis not in VARIABLES and power:
                value *= base[axis] ** power
        answer[(exponent[VARIABLES[0]], exponent[VARIABLES[1]])] += value
    return {monomial: value for monomial, value in answer.items() if value}


def primitive(polynomial):
    """Primitive integer coefficient tuple, oriented by reverse lex order."""

    if not polynomial:
        return ()
    denominator = 1
    for value in polynomial.values():
        denominator = lcm(denominator, Fraction(value).denominator)
    integer = {
        tuple(map(int, monomial)): int(Fraction(value) * denominator)
        for monomial, value in polynomial.items()
    }
    divisor = 0
    for value in integer.values():
        divisor = gcd(divisor, abs(value))
    integer = {monomial: value // divisor for monomial, value in integer.items()}
    leading = max(integer)
    if integer[leading] < 0:
        integer = {monomial: -value for monomial, value in integer.items()}
    return tuple(sorted(integer.items()))


def total_degree(polynomial):
    return max((sum(monomial) for monomial, _coefficient in polynomial), default=0)


def bidegree(polynomial):
    return tuple(
        max((monomial[axis] for monomial, _coefficient in polynomial), default=0)
        for axis in range(2)
    )


def determinant(matrix):
    if len(matrix) == 1:
        return matrix[0][0]
    return sum(
        (-1) ** column
        * matrix[0][column]
        * determinant(
            tuple(
                tuple(row[index] for index in range(len(matrix)) if index != column)
                for row in matrix[1:]
            )
        )
        for column in range(len(matrix))
    )


def conic_determinant(polynomial):
    """Determinant of twice the projective symmetric conic matrix."""

    values = dict(polynomial)
    hh = values.get((2, 0), 0)
    hi = values.get((1, 1), 0)
    ii = values.get((0, 2), 0)
    h = values.get((1, 0), 0)
    i = values.get((0, 1), 0)
    constant = values.get((0, 0), 0)
    return determinant(((2 * hh, hi, h), (hi, 2 * ii, i), (h, i, 2 * constant)))


def certified_irreducible(polynomial):
    degree = total_degree(polynomial)
    if degree == 0:
        return False
    if degree == 1:
        return True
    if degree != 2:
        raise AssertionError("plane restriction exceeds quadratic degree")
    # A reducible projective conic is singular, so a nonzero determinant is a
    # complete irreducibility certificate over QQ (indeed over its closure).
    return bool(conic_determinant(polynomial))


def evaluate(polynomial, h, i):
    return sum(
        Fraction(coefficient) * h**monomial[0] * i**monomial[1]
        for monomial, coefficient in polynomial
    )


def affine_row(polynomial):
    values = dict(polynomial)
    if set(values) - {(0, 0), (1, 0), (0, 1)}:
        raise AssertionError("parent bracket is not affine on the (h,i) plane")
    return (
        Fraction(values.get((1, 0), 0)),
        Fraction(values.get((0, 1), 0)),
        Fraction(values.get((0, 0), 0)),
    )


def normalized_halfspace(polynomial, base_h, base_i):
    """Return integer ``A*h+B*i+C >= 0`` containing the base point."""

    a, b, c = affine_row(polynomial)
    value = a * base_h + b * base_i + c
    if not value:
        raise AssertionError("base point lies on a parent boundary")
    if value < 0:
        a, b, c = -a, -b, -c
    denominator = lcm(a.denominator, b.denominator, c.denominator)
    row = [int(a * denominator), int(b * denominator), int(c * denominator)]
    divisor = gcd(gcd(abs(row[0]), abs(row[1])), abs(row[2]))
    return tuple(value // divisor for value in row)


def line_intersection(left, right):
    a, b, c = left
    d, e, f = right
    determinant = a * e - b * d
    if not determinant:
        return None
    return (
        Fraction(b * f - c * e, determinant),
        Fraction(c * d - a * f, determinant),
    )


def inside(point, halfspaces):
    h, i = point
    return all(a * h + b * i + c >= 0 for a, b, c in halfspaces)


def polygon_vertices(halfspaces):
    vertices = set()
    for index, left in enumerate(halfspaces):
        for right in halfspaces[index + 1 :]:
            point = line_intersection(left, right)
            if point is not None and inside(point, halfspaces):
                vertices.add(point)
    return tuple(sorted(vertices))


def bounded_halfspaces(halfspaces):
    """Exact recession-cone test in dimension two.

    A nonzero recession direction exists at an extreme ray perpendicular to a
    constraint normal.  Testing both orientations of every such direction is
    therefore complete for a finite homogeneous halfspace intersection.
    """

    for a, b, _c in halfspaces:
        for direction in ((b, -a), (-b, a)):
            if direction != (0, 0) and all(
                c * direction[0] + d * direction[1] >= 0
                for c, d, _e in halfspaces
            ):
                return False, direction
    return True, None


def quadratic_coefficients(polynomial):
    values = dict(polynomial)
    if any(sum(monomial) > 2 for monomial in values):
        raise AssertionError("plane factor exceeds the quadratic resource ceiling")
    return tuple(
        Fraction(values.get(monomial, 0))
        for monomial in ((0, 0), (1, 0), (0, 1), (2, 0), (1, 1), (0, 2))
    )


def point_on_segment(left, right, parameter):
    return tuple(
        first + parameter * (second - first)
        for first, second in zip(left, right)
    )


def edge_stationary_point(polynomial, left, right):
    """Return the unique interior stationary point on an edge, if present."""

    p0 = evaluate(polynomial, *left)
    p1 = evaluate(polynomial, *right)
    middle = point_on_segment(left, right, Fraction(1, 2))
    pm = evaluate(polynomial, *middle)
    # p(t)=a*t^2+b*t+c from p(0), p(1), p(1/2).
    c = p0
    a = 2 * (p1 + p0 - 2 * pm)
    b = p1 - p0 - a
    if not a:
        return None
    parameter = -b / (2 * a)
    if 0 < parameter < 1:
        return point_on_segment(left, right, parameter)
    return None


def interior_stationary_point(polynomial):
    _c, h, i, hh, hi, ii = quadratic_coefficients(polynomial)
    determinant = 4 * hh * ii - hi * hi
    if not determinant:
        return None
    return (
        Fraction(hi * i - 2 * ii * h, determinant),
        Fraction(hi * h - 2 * hh * i, determinant),
    )


def exact_range_on_triangle(polynomial, vertices, halfspaces):
    """Exact minimum/maximum of an affine or quadratic on a triangle."""

    candidates = list(vertices)
    for left, right in combinations(vertices, 2):
        point = edge_stationary_point(polynomial, left, right)
        if point is not None:
            candidates.append(point)
    point = interior_stationary_point(polynomial)
    if point is not None and inside(point, halfspaces):
        candidates.append(point)
    values = tuple(evaluate(polynomial, *point) for point in candidates)
    return min(values), max(values), tuple(candidates)


def projection_census(progress=True):
    base = star.normalized_parent()
    occurrences, occurrence_factor, factor_polynomials = labeled.factor_polynomials()
    if len(occurrences) != 84_840 or len(factor_polynomials) != 26_740:
        raise AssertionError("global residual factor census changed")

    factor_to_plane = []
    plane_sources = defaultdict(list)
    multiplicities = Counter()
    for factor, polynomial in enumerate(factor_polynomials):
        restricted = primitive(restrict_plane(polynomial, base))
        if total_degree(restricted) == 0:
            factors = ()
        else:
            if not certified_irreducible(restricted):
                raise AssertionError(f"degenerate plane conic at global factor {factor}")
            factors = (restricted,)
        factor_to_plane.append(factors)
        for plane_factor in factors:
            plane_sources[plane_factor].append((factor, 1))
            multiplicities[1] += 1
        if progress and (factor + 1) % 2000 == 0:
            print(f"restricted {factor + 1}/26740 residual factors", flush=True)

    _residual, brackets = representative.polynomial_data()
    halfspace_labels = defaultdict(list)
    for label, polynomial in brackets.items():
        restricted = primitive(restrict_plane(polynomial, base))
        row = normalized_halfspace(restricted, base[7], base[8])
        halfspace_labels[row].append(label)
    halfspaces = tuple(sorted(halfspace_labels))
    bounded, ray = bounded_halfspaces(halfspaces)
    vertices = polygon_vertices(halfspaces)
    if not bounded:
        raise AssertionError(f"selected parent-860 plane cell is unbounded along {ray}")
    if len(vertices) < 3:
        raise AssertionError("selected parent-860 plane cell is not two-dimensional")

    degree_census = Counter(
        total_degree(polynomial) for polynomial in plane_sources
    )
    bidegree_census = Counter(
        bidegree(polynomial)
        for polynomial in plane_sources
    )
    constant_restrictions = sum(not factors for factors in factor_to_plane)
    active_plane_factors = []
    interior_plane_factors = []
    boundary_only_factors = []
    excluded_sign = Counter()
    active_degree_census = Counter()
    interior_degree_census = Counter()
    for polynomial in plane_sources:
        minimum, maximum, _candidates = exact_range_on_triangle(
            polynomial, vertices, halfspaces
        )
        if minimum <= 0 <= maximum:
            active_plane_factors.append(polynomial)
            active_degree_census[total_degree(polynomial)] += 1
            if minimum < 0 < maximum:
                interior_plane_factors.append(polynomial)
                interior_degree_census[total_degree(polynomial)] += 1
            else:
                boundary_only_factors.append(polynomial)
        else:
            excluded_sign[1 if minimum > 0 else -1] += 1
    return {
        "base": base,
        "factor_to_plane": tuple(factor_to_plane),
        "plane_sources": dict(plane_sources),
        "factor_power_census": multiplicities,
        "degree_census": degree_census,
        "bidegree_census": bidegree_census,
        "constant_restrictions": constant_restrictions,
        "active_plane_factors": tuple(active_plane_factors),
        "active_degree_census": active_degree_census,
        "interior_plane_factors": tuple(interior_plane_factors),
        "interior_degree_census": interior_degree_census,
        "boundary_only_factors": tuple(boundary_only_factors),
        "excluded_sign": excluded_sign,
        "halfspaces": halfspaces,
        "halfspace_labels": dict(halfspace_labels),
        "vertices": vertices,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--census", action="store_true")
    args = parser.parse_args()
    result = projection_census(progress=True)
    print("PASS primitive global residual factors:", len(result["factor_to_plane"]))
    print("PASS constant plane restrictions:", result["constant_restrictions"])
    print("PASS distinct irreducible plane factors:", len(result["plane_sources"]))
    print("PASS total-degree census:", dict(sorted(result["degree_census"].items())))
    print("PASS bidegree census:", dict(sorted(result["bidegree_census"].items())))
    print("PASS irreducible-power census:", dict(sorted(result["factor_power_census"].items())))
    print("PASS distinct parent halfspaces:", len(result["halfspaces"]))
    print("PASS exact parent polygon vertices:", len(result["vertices"]))
    print("PASS plane factors meeting the closed parent triangle:", len(result["active_plane_factors"]))
    print("PASS active total-degree census:", dict(sorted(result["active_degree_census"].items())))
    print("PASS factors meeting the open parent triangle:", len(result["interior_plane_factors"]))
    print("PASS interior total-degree census:", dict(sorted(result["interior_degree_census"].items())))
    print("PASS boundary-only plane factors:", len(result["boundary_only_factors"]))
    print("PASS exact constant-sign exclusions:", dict(sorted(result["excluded_sign"].items())))
    if not args.census:
        print("SCOPE first projection only; no plane-factor nonintersection or atlas claim")


if __name__ == "__main__":
    main()
