#!/usr/bin/env python3
"""Exact triangular Bernstein cover for the parent-860 ``(h,i)`` slice.

The complete plane projection contains many curves, but every restriction is
affine or quadratic.  On any triangle, the six degree-two Bernstein control
values therefore give an exact convex-hull exclusion: if they are strictly
positive (or strictly negative), the curve cannot meet that triangle.

This script recursively subdivides the exact parent triangle into four.  At a
pinned depth it records every factor/cell incidence not excluded by that exact
test.  Consequently two residual curves can meet only if their factor IDs
occur together in at least one stored leaf.  The cover is a proof-bearing
prefilter for the full arrangement, not yet a chamber atlas.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from fractions import Fraction
from itertools import combinations
from math import gcd, lcm
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG9_GRAPH_parent860_plane_projection as projection  # noqa: E402


DEFAULT_DEPTH = 8


def midpoint(left, right):
    return tuple((first + second) / 2 for first, second in zip(left, right))


def subdivide(vertices):
    first, second, third = vertices
    first_second = midpoint(first, second)
    second_third = midpoint(second, third)
    third_first = midpoint(third, first)
    return (
        (first, first_second, third_first),
        (first_second, second, second_third),
        (third_first, second_third, third),
        (first_second, second_third, third_first),
    )


def bernstein_controls(polynomial, vertices):
    first, second, third = vertices
    vertex = tuple(projection.evaluate(polynomial, *point) for point in vertices)
    edge = []
    for (left_index, left), (right_index, right) in (
        ((0, first), (1, second)),
        ((1, second), (2, third)),
        ((2, third), (0, first)),
    ):
        middle_value = projection.evaluate(polynomial, *midpoint(left, right))
        edge.append(
            2 * middle_value - (vertex[left_index] + vertex[right_index]) / 2
        )
    return vertex + tuple(edge)


def primitive_controls(controls):
    denominator = 1
    for value in controls:
        denominator = lcm(denominator, Fraction(value).denominator)
    integer = [int(Fraction(value) * denominator) for value in controls]
    divisor = 0
    for value in integer:
        divisor = gcd(divisor, abs(value))
    return tuple(value // divisor for value in integer)


def evaluate_controls(controls, barycentric):
    first, second, third = map(Fraction, barycentric)
    v0, v1, v2, e01, e12, e20 = controls
    return (
        v0 * first * first
        + v1 * second * second
        + v2 * third * third
        + 2 * e01 * first * second
        + 2 * e12 * second * third
        + 2 * e20 * third * first
    )


CHILD_BARYCENTRIC = (
    ((1, 0, 0), (Fraction(1, 2), Fraction(1, 2), 0), (Fraction(1, 2), 0, Fraction(1, 2))),
    ((Fraction(1, 2), Fraction(1, 2), 0), (0, 1, 0), (0, Fraction(1, 2), Fraction(1, 2))),
    ((Fraction(1, 2), 0, Fraction(1, 2)), (0, Fraction(1, 2), Fraction(1, 2)), (0, 0, 1)),
    ((Fraction(1, 2), Fraction(1, 2), 0), (0, Fraction(1, 2), Fraction(1, 2)), (Fraction(1, 2), 0, Fraction(1, 2))),
)


def midpoint_barycentric(left, right):
    return tuple((first + second) / 2 for first, second in zip(left, right))


def child_controls_fraction(controls, vertices):
    vertex = tuple(evaluate_controls(controls, point) for point in vertices)
    edge = []
    for left_index, right_index in ((0, 1), (1, 2), (2, 0)):
        middle_value = evaluate_controls(
            controls,
            midpoint_barycentric(vertices[left_index], vertices[right_index]),
        )
        edge.append(2 * middle_value - (vertex[left_index] + vertex[right_index]) / 2)
    return vertex + tuple(edge)


def child_transform(vertices):
    columns = []
    for basis in range(6):
        controls = tuple(int(index == basis) for index in range(6))
        columns.append(child_controls_fraction(controls, vertices))
    rows = tuple(tuple(columns[column][row] for column in range(6)) for row in range(6))
    denominator = 1
    for row in rows:
        for value in row:
            denominator = lcm(denominator, Fraction(value).denominator)
    return tuple(
        tuple(int(Fraction(value) * denominator) for value in row)
        for row in rows
    )


CHILD_TRANSFORMS = tuple(child_transform(vertices) for vertices in CHILD_BARYCENTRIC)


def subdivide_controls(controls):
    return tuple(
        primitive_controls(
            tuple(sum(weight * value for weight, value in zip(row, controls)) for row in transform)
        )
        for transform in CHILD_TRANSFORMS
    )


def may_vanish_controls(controls):
    return not (all(value > 0 for value in controls) or all(value < 0 for value in controls))


def cover_factor(polynomial, parent_vertices, depth):
    leaves = []
    controls = primitive_controls(bernstein_controls(polynomial, parent_vertices))
    stack = [(0, 0, controls)]
    while stack:
        level, index, controls = stack.pop()
        if not may_vanish_controls(controls):
            continue
        if level == depth:
            leaves.append(index)
            continue
        children = subdivide_controls(controls)
        for child, child_controls in reversed(tuple(enumerate(children))):
            stack.append((level + 1, 4 * index + child, child_controls))
    return tuple(leaves)


def build(depth=DEFAULT_DEPTH, progress=True, include_boundary=False):
    census = projection.projection_census(progress=False)
    active = tuple(
        census["active_plane_factors"]
        if include_boundary
        else census["interior_plane_factors"]
    )
    global_factor = tuple(census["plane_sources"][polynomial][0][0] for polynomial in active)
    if len(set(global_factor)) != len(global_factor):
        raise AssertionError("active plane factor/global factor map is not injective")

    leaf_factors = defaultdict(list)
    factor_leaf_count = []
    for active_index, polynomial in enumerate(active):
        leaves = cover_factor(polynomial, census["vertices"], depth)
        if not leaves:
            raise AssertionError("exactly active plane factor received an empty cover")
        factor_leaf_count.append(len(leaves))
        for leaf in leaves:
            leaf_factors[leaf].append(active_index)
        if progress and (active_index + 1) % 100 == 0:
            print(f"covered {active_index + 1}/{len(active)} active factors", flush=True)

    candidate_pairs = set()
    for factors in leaf_factors.values():
        for left, right in combinations(factors, 2):
            candidate_pairs.add((left, right))
    total_pairs = len(active) * (len(active) - 1) // 2
    return {
        "depth": depth,
        "include_boundary": include_boundary,
        "active_factor": global_factor,
        "active_polynomial": active,
        "leaf_factors": dict(leaf_factors),
        "factor_leaf_count": tuple(factor_leaf_count),
        "candidate_pairs": tuple(sorted(candidate_pairs)),
        "total_pairs": total_pairs,
        "projection_census": census,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--depth", type=int, default=DEFAULT_DEPTH)
    parser.add_argument("--closed", action="store_true")
    args = parser.parse_args()
    if not 0 <= args.depth <= 12:
        raise SystemExit("depth must lie between 0 and 12")
    result = build(args.depth, progress=True, include_boundary=args.closed)
    occupancy = tuple(map(len, result["leaf_factors"].values()))
    print("PASS exact Bernstein depth:", result["depth"])
    print(
        "PASS plane factors covered:",
        len(result["active_factor"]),
        "(closed triangle)" if result["include_boundary"] else "(open triangle)",
    )
    print("PASS occupied leaves:", len(result["leaf_factors"]), "/", 4 ** result["depth"])
    print("PASS factor/leaf incidences:", sum(result["factor_leaf_count"]))
    print("PASS factor leaf-count range:", min(result["factor_leaf_count"]), max(result["factor_leaf_count"]))
    print("PASS maximum factors in one leaf:", max(occupancy))
    print("PASS candidate curve pairs:", len(result["candidate_pairs"]), "/", result["total_pairs"])
    print("PASS exact excluded curve pairs:", result["total_pairs"] - len(result["candidate_pairs"]))
    print("SCOPE exact curve cover/pair prefilter; chamber incidence remains open")


if __name__ == "__main__":
    main()
