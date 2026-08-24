#!/usr/bin/env python3
"""Exact transverse two-wall disk inside catalog parent 860.

The parent-860 coordinate-star pilot is one-dimensional.  This verifier adds
the first genuine codimension-two parent-860 cell: a rational square in the
``(h,i)`` coordinate plane centered at the exact intersection of primitive
global residual factors 15250 and 19721.

All 26,740 primitive factors and all parent brackets are restricted to the
whole square.  Centered exact dominance proves that only the two named affine
walls occur.  Their primitive normal determinant is nonzero.  Exact derived
tope enumeration labels all four chambers, four wall rays, and the node.

The result is complete on the displayed disk only.  It is a diagonal-nine
routing and diagonal-eight codimension-two regression, not parent-space
coverage and not a 9DVL theorem.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations
import hashlib
from math import comb, gcd, lcm
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as representative  # noqa: E402
import DIAG9_GRAPH_exact_topes as topes  # noqa: E402
import DIAG9_GRAPH_parent860_star as star  # noqa: E402


DATA = HERE / "data"
ROADMAP = DATA / "DIAG9_GRAPH_parent860_node_roadmap.npz"
GRAPH = DATA / "DIAG9_GRAPH_parent860_node_graph.npz"
FORMAT = "diag9-parent860-transverse-node-v1"
GRAPH_FORMAT = "diag9-labeled-master-tree-v1"
PARENT_INDEX = 860
VARIABLES = (7, 8)
CENTER_H = Fraction(3_727_672_351_519_660, 8_405_164_123_084_547)
CENTER_I = Fraction(5_135_974_949_766_124, 12_881_287_028_869_217)
RADIUS = Fraction(1, 1_000_000)
ACTIVE_FACTORS = (15_250, 19_721)
ACTIVE_FACTOR_TYPES = (49, 36)
ACTIVE_FACTOR_MULTIPLICITIES = (1, 65)
BRANCH_NORMALS = ((16_648, 60_347), (-145_429_401, 303_924_845))
JACOBIAN = 13_835_968_881_707
OTHER_MARGIN = Fraction(
    299_331_911_737_904_404_062_500,
    5_709_836_426_934_645_483_233,
)
OTHER_WORST_FACTOR = 16_249
BRACKET_MARGIN = Fraction(
    197_536_235_184_241_888_000_000,
    11_116_550_705_914_134_271,
)
BRACKET_WORST = "2378"
CELL_SIGNS = ((1, 1), (1, -1), (-1, -1), (-1, 1))
WALL_TARGETS = ((0, 1), (0, -1), (-1, 0), (1, 0))
WALL_ADJACENCY = ((0, 3), (1, 2), (2, 3), (0, 1))
GRAPH_EDGES = ((0, 1), (1, 2), (2, 3), (0, 3))
TREE_EDGES = ((0, 1), (1, 2), (2, 3))
EXPECTED_CELL_COUNTS = (26_112,) * 4
EXPECTED_WALL_COUNTS = (26_110, 26_110, 26_040, 26_040)
EXPECTED_NODE_COUNT = 26_038
EXPECTED_PATTERN_MULTIPLICITY = Counter(
    {0b1111: 26_038, 0b1001: 72, 0b0110: 72, 0b0011: 2, 0b1100: 2}
)
EXPECTED_INTERSECTION_CLOSURE = (0, 1, 2, 3, 4, 6, 8, 9, 12, 15)
EXPECTED_DIGEST = "b7080a332d7b80127ae362bbfa2d5806fbe153d24245ef002d4867df6e1e274d"


def centered_parent():
    coordinates = list(star.normalized_parent())
    coordinates[VARIABLES[0]] = CENTER_H
    coordinates[VARIABLES[1]] = CENTER_I
    return tuple(coordinates)


def centered_polynomial(polynomial, center):
    """Substitute h=CENTER_H+x and i=CENTER_I+y exactly."""

    answer = {}
    for exponent, coefficient in polynomial.items():
        fixed = Fraction(coefficient)
        for axis, power in enumerate(exponent):
            if axis not in VARIABLES and power:
                fixed *= center[axis] ** power
        for x_power in range(exponent[VARIABLES[0]] + 1):
            x_coefficient = (
                comb(exponent[VARIABLES[0]], x_power)
                * center[VARIABLES[0]] ** (exponent[VARIABLES[0]] - x_power)
            )
            for y_power in range(exponent[VARIABLES[1]] + 1):
                value = (
                    fixed
                    * x_coefficient
                    * comb(exponent[VARIABLES[1]], y_power)
                    * center[VARIABLES[1]]
                    ** (exponent[VARIABLES[1]] - y_power)
                )
                monomial = (x_power, y_power)
                answer[monomial] = answer.get(monomial, Fraction(0)) + value
    return {monomial: value for monomial, value in answer.items() if value}


def dominance_ratio(polynomial):
    constant = abs(Fraction(polynomial.get((0, 0), 0)))
    if not constant:
        raise AssertionError("dominance polynomial vanishes at the node")
    tail = sum(
        abs(Fraction(value)) * RADIUS ** (x_power + y_power)
        for (x_power, y_power), value in polynomial.items()
        if x_power + y_power
    )
    return None if not tail else constant / tail


def update_minimum(current, ratio, witness):
    if ratio is None:
        return current
    if current[0] is None or ratio < current[0]:
        return ratio, witness
    return current


def primitive_linear(polynomial):
    if set(polynomial) - {(1, 0), (0, 1)}:
        raise AssertionError("node branch is not exactly centered linear")
    row = (
        Fraction(polynomial.get((1, 0), 0)),
        Fraction(polynomial.get((0, 1), 0)),
    )
    if not all(row):
        raise AssertionError("node branch has a zero coordinate slope")
    denominator = lcm(*(value.denominator for value in row))
    integer = [int(value * denominator) for value in row]
    divisor = gcd(abs(integer[0]), abs(integer[1]))
    integer = [value // divisor for value in integer]
    if integer[-1] < 0:
        integer = [-value for value in integer]
    return tuple(integer)


def exact_geometry():
    center = centered_parent()
    occurrences, occurrence_factor, factor_polynomials = labeled.factor_polynomials()
    if len(occurrences) != 84_840 or len(factor_polynomials) != 26_740:
        raise AssertionError("global residual factor census changed")

    active = []
    other_minimum = (None, None)
    for factor, polynomial in enumerate(factor_polynomials):
        restricted = centered_polynomial(polynomial, center)
        if not restricted.get((0, 0), 0):
            active.append((factor, restricted))
            continue
        other_minimum = update_minimum(
            other_minimum, dominance_ratio(restricted), factor
        )
    if tuple(factor for factor, _restricted in active) != ACTIVE_FACTORS:
        raise AssertionError("parent-860 node active-factor pair changed")
    normals = tuple(primitive_linear(restricted) for _factor, restricted in active)
    if normals != BRANCH_NORMALS:
        raise AssertionError("parent-860 node branch normals changed")
    jacobian = normals[0][0] * normals[1][1] - normals[0][1] * normals[1][0]
    if jacobian != JACOBIAN:
        raise AssertionError("parent-860 node is not the pinned transverse crossing")
    if other_minimum != (OTHER_MARGIN, OTHER_WORST_FACTOR):
        raise AssertionError("other-factor dominance frontier changed")

    _residual, brackets = representative.polynomial_data()
    bracket_minimum = (None, None)
    for label, polynomial in brackets.items():
        restricted = centered_polynomial(polynomial, center)
        bracket_minimum = update_minimum(
            bracket_minimum, dominance_ratio(restricted), label
        )
    if bracket_minimum != (BRACKET_MARGIN, BRACKET_WORST):
        raise AssertionError("parent-bracket dominance frontier changed")

    _representatives, _stabilizers, factor_alignment, _factor_occurrence, _sizes = (
        labeled.factor_orbit_data(occurrences, occurrence_factor)
    )
    with np.load(labeled.global_factors.CERTIFICATE, allow_pickle=False) as source:
        multiplicities = tuple(map(int, source["factor_multiplicity"]))
    factor_types = tuple(factor_alignment[factor][0] for factor in ACTIVE_FACTORS)
    factor_multiplicities = tuple(multiplicities[factor] for factor in ACTIVE_FACTORS)
    if factor_types != ACTIVE_FACTOR_TYPES:
        raise AssertionError("node factor orbit types changed")
    if factor_multiplicities != ACTIVE_FACTOR_MULTIPLICITIES:
        raise AssertionError("node factor multiplicities changed")

    return {
        "center": center,
        "normals": normals,
        "jacobian": jacobian,
        "other_margin": other_minimum[0],
        "other_worst_factor": other_minimum[1],
        "bracket_margin": bracket_minimum[0],
        "bracket_worst": bracket_minimum[1],
        "factor_types": factor_types,
        "factor_multiplicities": factor_multiplicities,
    }


def solve_normal_coordinates(first, second):
    first = Fraction(first)
    second = Fraction(second)
    (a, b), (c, d) = BRANCH_NORMALS
    determinant = a * d - b * c
    return (
        Fraction(first * d - b * second, determinant),
        Fraction(a * second - first * c, determinant),
    )


def scaled_normal_coordinates(first, second):
    point = solve_normal_coordinates(first, second)
    scale = RADIUS / (2 * max(abs(point[0]), abs(point[1])))
    return point[0] * scale, point[1] * scale


def branch_signs(point):
    answer = []
    for first, second in BRANCH_NORMALS:
        value = first * point[0] + second * point[1]
        answer.append(1 if value > 0 else -1 if value < 0 else 0)
    return tuple(answer)


def rational_parent(center, point):
    coordinates = list(center)
    coordinates[VARIABLES[0]] += point[0]
    coordinates[VARIABLES[1]] += point[1]
    return star.matrix_from_coordinates(coordinates)


def exact_labels(center):
    cell_points = tuple(scaled_normal_coordinates(*signs) for signs in CELL_SIGNS)
    wall_points = tuple(scaled_normal_coordinates(*target) for target in WALL_TARGETS)
    expected_parent = topes.parent_signs(rational_parent(center, (0, 0)))

    cells = []
    for point, expected_signs in zip(cell_points, CELL_SIGNS):
        if branch_signs(point) != expected_signs:
            raise AssertionError("cell sample has wrong branch signs")
        matrix = rational_parent(center, point)
        if topes.parent_signs(matrix) != expected_parent:
            raise AssertionError("cell sample leaves catalog parent 860")
        cells.append(tuple(sorted(topes.parent_topes(matrix))))
    if tuple(map(len, cells)) != EXPECTED_CELL_COUNTS:
        raise AssertionError("parent-860 node chamber labels changed")

    walls = []
    for point, expected_signs in zip(wall_points, WALL_TARGETS):
        if branch_signs(point) != expected_signs:
            raise AssertionError("wall sample has wrong branch signs")
        matrix = rational_parent(center, point)
        if topes.parent_signs(matrix) != expected_parent:
            raise AssertionError("wall sample leaves catalog parent 860")
        walls.append(tuple(sorted(topes.parent_topes(matrix))))
    if tuple(map(len, walls)) != EXPECTED_WALL_COUNTS:
        raise AssertionError("parent-860 node wall labels changed")

    node_matrix = rational_parent(center, (0, 0))
    if topes.parent_signs(node_matrix) != expected_parent:
        raise AssertionError("node leaves catalog parent 860")
    node = tuple(sorted(topes.parent_topes(node_matrix)))
    if len(node) != EXPECTED_NODE_COUNT:
        raise AssertionError("parent-860 node label count changed")

    cell_sets = tuple(map(set, cells))
    wall_sets = tuple(map(set, walls))
    for wall, (left, right) in zip(wall_sets, WALL_ADJACENCY):
        if wall != cell_sets[left] & cell_sets[right]:
            raise AssertionError("wall labels are not adjacent-cell intersections")
    if set(node) != set.intersection(*cell_sets):
        raise AssertionError("node labels are not the four-cell intersection")
    if any(set(node) != set(left) & set(right) for left, right in combinations(wall_sets, 2)):
        raise AssertionError("node labels are not every two-wall intersection")
    return cell_points, wall_points, tuple(cells), tuple(walls), node


def signature_patterns(cells):
    patterns = {}
    for cell, signatures in enumerate(cells):
        bit = 1 << cell
        for signature in signatures:
            patterns[signature] = patterns.get(signature, 0) | bit
    return patterns


def intersection_closure(patterns):
    answer = {0b1111}
    for pattern in sorted(set(patterns.values())):
        answer |= {old & pattern for old in tuple(answer)}
    return tuple(sorted(answer))


def connected_mask(mask):
    vertices = [vertex for vertex in range(4) if mask & (1 << vertex)]
    if not vertices:
        return True
    graph = [[] for _ in range(4)]
    for left, right in GRAPH_EDGES:
        graph[left].append(right)
        graph[right].append(left)
    seen = {vertices[0]}
    stack = vertices[:1]
    while stack:
        vertex = stack.pop()
        for neighbor in graph[vertex]:
            if mask & (1 << neighbor) and neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return len(seen) == len(vertices)


def string_array(values):
    return np.asarray(tuple(str(value) for value in values))


def fraction_fields(prefix, value):
    value = Fraction(value)
    return {
        f"{prefix}_numerator": np.asarray(str(value.numerator)),
        f"{prefix}_denominator": np.asarray(str(value.denominator)),
    }


def point_fields(prefix, points):
    return {
        f"{prefix}_numerator": np.asarray(
            tuple(tuple(str(value.numerator) for value in point) for point in points)
        ),
        f"{prefix}_denominator": np.asarray(
            tuple(tuple(str(value.denominator) for value in point) for point in points)
        ),
    }


def semantic_digest(payload):
    digest = hashlib.sha256()
    for name in sorted(payload):
        array = np.asarray(payload[name])
        digest.update(name.encode("ascii"))
        digest.update(str(array.dtype).encode("ascii"))
        digest.update(repr(array.shape).encode("ascii"))
        digest.update(array.tobytes())
    return digest.hexdigest()


def reconstruct(progress=True):
    geometry = exact_geometry()
    if progress:
        print("PASS exact two-factor isolation on the parent-860 (h,i) disk", flush=True)
    cell_points, wall_points, cells, walls, node = exact_labels(geometry["center"])
    patterns = signature_patterns(cells)
    multiplicity = Counter(patterns.values())
    if multiplicity != EXPECTED_PATTERN_MULTIPLICITY:
        raise AssertionError("parent-860 node support patterns changed")
    proper = tuple(sorted(set(patterns.values()) - {0, 0b1111}))
    if proper != (0b0011, 0b0110, 0b1001, 0b1100):
        raise AssertionError("proper node supports are not the four halfspaces")
    closure = intersection_closure(patterns)
    if closure != EXPECTED_INTERSECTION_CLOSURE:
        raise AssertionError("parent-860 node intersection closure changed")
    disconnected = tuple(mask for mask in closure if not connected_mask(mask))
    if disconnected:
        raise AssertionError("parent-860 node has a disconnected support intersection")

    signatures = tuple(sorted(patterns))
    payload = {
        "format": np.asarray(FORMAT),
        "parent_index": np.asarray(PARENT_INDEX, dtype=np.uint16),
        "variable": np.asarray(VARIABLES, dtype=np.uint8),
        "active_factor": np.asarray(ACTIVE_FACTORS, dtype=np.uint16),
        "active_factor_type": np.asarray(geometry["factor_types"], dtype=np.uint8),
        "active_factor_multiplicity": np.asarray(
            geometry["factor_multiplicities"], dtype=np.uint8
        ),
        "branch_normal": np.asarray(geometry["normals"], dtype=np.int64),
        "jacobian": np.asarray(geometry["jacobian"], dtype=np.int64),
        "other_worst_factor": np.asarray(
            geometry["other_worst_factor"], dtype=np.uint16
        ),
        "bracket_worst": np.asarray(geometry["bracket_worst"]),
        "cell_sign": np.asarray(CELL_SIGNS, dtype=np.int8),
        "wall_target": np.asarray(WALL_TARGETS, dtype=np.int8),
        "wall_adjacency": np.asarray(WALL_ADJACENCY, dtype=np.uint8),
        "edge": np.asarray(GRAPH_EDGES, dtype=np.uint8),
        "tree_edge": np.asarray(TREE_EDGES, dtype=np.uint8),
        "cell_tope": np.asarray(cells, dtype=np.uint64),
        "wall_tope_offset": np.asarray(
            tuple(np.cumsum((0,) + tuple(map(len, walls)))), dtype=np.uint32
        ),
        "wall_tope": np.asarray(tuple(value for wall in walls for value in wall), dtype=np.uint64),
        "node_tope": np.asarray(node, dtype=np.uint64),
        "signature": np.asarray(signatures, dtype=np.uint64),
        "signature_pattern": np.asarray(
            tuple(patterns[signature] for signature in signatures), dtype=np.uint8
        ),
        "proper_pattern": np.asarray(proper, dtype=np.uint8),
        "intersection_closure": np.asarray(closure, dtype=np.uint8),
        "disconnected_closure": np.asarray(disconnected, dtype=np.uint8),
    }
    payload.update(fraction_fields("center_h", CENTER_H))
    payload.update(fraction_fields("center_i", CENTER_I))
    payload.update(fraction_fields("radius", RADIUS))
    payload.update(fraction_fields("other_margin", geometry["other_margin"]))
    payload.update(fraction_fields("bracket_margin", geometry["bracket_margin"]))
    payload.update(point_fields("cell_point", cell_points))
    payload.update(point_fields("wall_point", wall_points))
    support = np.asarray(
        tuple(tuple((pattern >> cell) & 1 for cell in range(4)) for pattern in proper),
        dtype=np.uint8,
    )
    graph = {
        "format": np.asarray(GRAPH_FORMAT),
        "edge": np.asarray(GRAPH_EDGES, dtype=np.int64),
        "support": support,
        "tree_edge": np.asarray(TREE_EDGES, dtype=np.int64),
    }
    return payload, graph, patterns


def compare_payload(stored, replay):
    if set(stored) != set(replay):
        raise AssertionError("parent-860 node certificate fields changed")
    for name in sorted(replay):
        if not np.array_equal(np.asarray(stored[name]), np.asarray(replay[name])):
            raise AssertionError(f"parent-860 node field changed: {name}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    args = parser.parse_args()

    replay, graph, patterns = reconstruct(progress=True)
    digest = semantic_digest(replay)
    if EXPECTED_DIGEST is not None and digest != EXPECTED_DIGEST:
        raise AssertionError("parent-860 node semantic digest changed")
    if args.build:
        DATA.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(ROADMAP, **replay)
        np.savez_compressed(GRAPH, **graph)
        print("WROTE", ROADMAP)
        print("WROTE", GRAPH)
    else:
        with np.load(ROADMAP, allow_pickle=False) as source:
            stored = {name: source[name] for name in source.files}
        with np.load(GRAPH, allow_pickle=False) as source:
            stored_graph = {name: source[name] for name in source.files}
        compare_payload(stored, replay)
        compare_payload(stored_graph, graph)

    print("PASS all 26,740 global factors on the exact parent-860 disk")
    print("PASS exactly two active walls:", ACTIVE_FACTORS)
    print("PASS active orbit types/multiplicities:", ACTIVE_FACTOR_TYPES, ACTIVE_FACTOR_MULTIPLICITIES)
    print("PASS transverse primitive-normal determinant:", JACOBIAN)
    print("PASS other-factor dominance margin:", OTHER_MARGIN)
    print("PASS parent-bracket dominance margin:", BRACKET_MARGIN)
    print("PASS chamber/wall/node tope counts:", EXPECTED_CELL_COUNTS, EXPECTED_WALL_COUNTS, EXPECTED_NODE_COUNT)
    print("PASS support-pattern multiplicities:", dict(sorted(Counter(patterns.values()).items())))
    print("THEOREM every finite common-feasibility locus on the disk is empty or convex")
    print("SEMANTIC SHA256:", digest)
    print("SCOPE local parent-860 disk; no global 9DVL diagonal is claimed")


if __name__ == "__main__":
    main()
