#!/usr/bin/env python3
"""Exact verifier for the common-light residence-fiber boundary.

The general common-light exit lemma is proved in ``ATLAS_HELLY.md``.  This
checker certifies that its conclusion is sharp on the row-2599 eight-shatter
artifact:

* two proper incomparable signatures have a common-light pair of positive
  five-circuits whose fixed-deletion exit has two connected components; and
* one proper signature has a positive five-circuit whose connected exit has
  first Betti number one.

All feasibility tests below are exact.  The script derives the circuit-cone
inequalities from the signed derived normals, enumerates every vertex of the
closed normalized residence polytope over ``Q``, constructs its exit-facet
nerve from actual face intersections, and computes the nerve homology by
rational boundary-matrix ranks.  It performs no LP and uses no floating-point
arithmetic.
"""

from fractions import Fraction
from itertools import combinations
from math import gcd, lcm
from pathlib import Path
import sys

import numpy as np

import four_chart_gate as gate
import prototype_koszul_circuits as koszul
import verify_seeat_shatter8 as shatter


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "seeat_parent2599_shatter8.npz"
TRIPLES = koszul.TRIPLES
BASES = gate.colex_subsets(8, 4)


def inverse(matrix):
    """Inverse over Q, or ``None`` for a singular square matrix."""
    size = len(matrix)
    rows = [
        [Fraction(value) for value in matrix[row]]
        + [Fraction(row == column) for column in range(size)]
        for row in range(size)
    ]
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if rows[row][column]),
            None,
        )
        if pivot is None:
            return None
        rows[column], rows[pivot] = rows[pivot], rows[column]
        scale = rows[column][column]
        rows[column] = [value / scale for value in rows[column]]
        for row in range(size):
            if row == column or not rows[row][column]:
                continue
            scale = rows[row][column]
            rows[row] = [
                left - scale * right
                for left, right in zip(rows[row], rows[column], strict=True)
            ]
    return [row[size:] for row in rows]


def primitive_row(row):
    """Clear denominators and common factors without changing orientation."""
    row = [Fraction(value) for value in row]
    denominator = 1
    for value in row:
        denominator = lcm(denominator, value.denominator)
    integers = [int(value * denominator) for value in row]
    divisor = 0
    for value in integers:
        divisor = gcd(divisor, abs(value))
    if not divisor:
        raise AssertionError("zero inequality row")
    return tuple(value // divisor for value in integers)


def dot(row, column):
    return sum(
        Fraction(left) * Fraction(right)
        for left, right in zip(row, column, strict=True)
    )


def verify_parent_and_state(certificate, pattern, bit, supported, expected_parent):
    """Verify one exact support-state entry used for properness/incomparability."""
    matrix = certificate["pattern_chart"][pattern]
    parent, normals = shatter.parent_signs_and_rows(matrix)
    if parent != expected_parent:
        raise AssertionError(f"pattern {pattern} is not parent row 2599")
    signature = int(certificate["signature"][bit])
    signed = [
        tuple(
            value if (signature >> index) & 1 else -value
            for value in normal
        )
        for index, normal in enumerate(normals)
    ]
    if supported:
        shatter.verify_feasible(signed, certificate["feasible_point"][pattern, bit])
    else:
        shatter.verify_infeasible(signed, certificate["gordan_weight"][pattern, bit])


def residence_rows(matrix, element):
    """The 35 oriented parent inequalities for moving one column."""
    point = tuple(int(value) for value in matrix[:, element - 1])
    rows = []
    tags = []
    for basis in BASES:
        if element not in basis:
            continue
        row = []
        for coordinate in range(4):
            columns = [
                [
                    1 if label == element and axis == coordinate
                    else 0 if label == element
                    else int(matrix[axis, label - 1])
                    for label in basis
                ]
                for axis in range(4)
            ]
            row.append(koszul.determinant(columns))
        value = dot(row, point)
        if not value:
            raise AssertionError("nonuniform residence chart")
        if value < 0:
            row = [-entry for entry in row]
        rows.append(primitive_row(row))
        tags.append(basis)
    if len(rows) != 35 or koszul.matrix_rank(rows) != 4:
        raise AssertionError("residence arrangement is not essential")
    return rows, tags


def moving_normal_matrix(matrix, triple, element):
    """Matrix of the linear map ``y_e -> a_triple(y_e)``."""
    columns = []
    triple_index = koszul.TRIPLE_INDEX[triple]
    for coordinate in range(4):
        changed = matrix.copy()
        changed[:, element - 1] = 0
        changed[coordinate, element - 1] = 1
        columns.append(koszul.parent_normals(changed)[triple_index])
    return [
        [columns[column][row] for column in range(4)]
        for row in range(4)
    ]


def circuit_rows(matrix, normals, signature, weights, element):
    """Derive the four nonnegative-coefficient inequalities of a 5-circuit."""
    weights = [int(value) for value in weights]
    support = [index for index, value in enumerate(weights) if value]
    if len(support) != 5 or any(weights[index] <= 0 for index in support):
        raise AssertionError("expected a strictly positive support-five circuit")
    moving = [index for index in support if element in TRIPLES[index]]
    if len(moving) != 1:
        raise AssertionError("the chosen label is not light exactly once")
    moving = moving[0]
    fixed = [index for index in support if index != moving]

    def sign(index):
        return 1 if (signature >> index) & 1 else -1

    fixed_matrix = [
        [sign(index) * normals[index][row] for index in fixed]
        for row in range(4)
    ]
    fixed_inverse = inverse(fixed_matrix)
    if fixed_inverse is None:
        raise AssertionError("positive dependence is not a minimal 5-circuit")
    variable = moving_normal_matrix(matrix, TRIPLES[moving], element)
    variable = [[sign(moving) * value for value in row] for row in variable]

    coefficient_rows = []
    for inverse_row in fixed_inverse:
        coefficient_rows.append(
            primitive_row(
                -sum(
                    inverse_row[index] * variable[index][column]
                    for index in range(4)
                )
                for column in range(4)
            )
        )

    point = tuple(int(value) for value in matrix[:, element - 1])
    moving_weight = weights[moving]
    for row, index in zip(coefficient_rows, fixed, strict=True):
        if dot(row, point) <= 0:
            raise AssertionError("chart is not in the strict circuit cone")
        # Primitive row scaling is arbitrary, so compare the unscaled exact
        # coefficient below by reconstructing it from the inverse once more.
        inverse_row = fixed_inverse[fixed.index(index)]
        exact_row = [
            -sum(
                inverse_row[position] * variable[position][column]
                for position in range(4)
            )
            for column in range(4)
        ]
        if dot(exact_row, point) != Fraction(weights[index], moving_weight):
            raise AssertionError("stored Gordan weights disagree with the circuit cone")
    return support, coefficient_rows


def normalized_vertices(parent_rows, circuit_rows_):
    """Enumerate every vertex and its active constraints over Q."""
    inequalities = list(parent_rows) + list(circuit_rows_)
    normalizer = tuple(
        sum(row[column] for row in parent_rows) for column in range(4)
    )

    # On the parent cone, normalizer=0 forces all parent rows to vanish; their
    # rank is four.  Thus the section normalizer=1 is bounded.
    if koszul.matrix_rank(parent_rows) != 4:
        raise AssertionError("unbounded projective normalization")

    vertices = {}
    for active_three in combinations(range(len(inequalities)), 3):
        system = [normalizer] + [inequalities[index] for index in active_three]
        system_inverse = inverse(system)
        if system_inverse is None:
            continue
        point = tuple(system_inverse[row][0] for row in range(4))
        values = tuple(dot(row, point) for row in inequalities)
        if min(values) < 0:
            continue
        active = frozenset(index for index, value in enumerate(values) if value == 0)
        vertices[point] = active
    if not vertices:
        raise AssertionError("normalized circuit residence has no vertices")
    return vertices


def exit_nerve(parent_rows, vertices):
    """Build all exit-facet nerve simplices from exact vertex incidences."""
    parent_count = len(parent_rows)
    active_parent = [
        frozenset(index for index in active if index < parent_count)
        for active in vertices.values()
    ]
    facets = sorted(set().union(*active_parent))
    simplices = {dimension: [] for dimension in range(len(facets))}
    for size in range(1, len(facets) + 1):
        for simplex in combinations(facets, size):
            if any(set(simplex) <= active for active in active_parent):
                simplices[size - 1].append(simplex)
    return facets, simplices


def nerve_components(facets, simplices):
    adjacent = {facet: set() for facet in facets}
    for first, second in simplices.get(1, []):
        adjacent[first].add(second)
        adjacent[second].add(first)
    remaining = set(facets)
    components = []
    while remaining:
        root = remaining.pop()
        component = {root}
        stack = [root]
        while stack:
            for other in adjacent[stack.pop()] & remaining:
                remaining.remove(other)
                component.add(other)
                stack.append(other)
        components.append(frozenset(component))
    return components


def boundary_matrix(lower, upper):
    lower_index = {simplex: index for index, simplex in enumerate(lower)}
    matrix = [[0 for _ in upper] for _ in lower]
    for column, simplex in enumerate(upper):
        for omitted in range(len(simplex)):
            face = simplex[:omitted] + simplex[omitted + 1 :]
            matrix[lower_index[face]][column] = -1 if omitted & 1 else 1
    return matrix


def first_betti(simplices):
    vertices = simplices.get(0, [])
    edges = simplices.get(1, [])
    triangles = simplices.get(2, [])
    d1 = boundary_matrix(vertices, edges)
    d2 = boundary_matrix(edges, triangles) if triangles else [[] for _ in edges]
    return len(edges) - koszul.matrix_rank(d1) - koszul.matrix_rank(d2)


def format_basis(basis):
    return "".join(map(str, basis))


def verify_disconnected_exit(certificate):
    pattern = 14
    bits = (0, 6)
    element = 7
    matrix = certificate["pattern_chart"][pattern]
    normals = koszul.parent_normals(matrix)
    parent, tags = residence_rows(matrix, element)
    circuit = []
    supports = []
    for bit in bits:
        support, rows = circuit_rows(
            matrix,
            normals,
            int(certificate["signature"][bit]),
            certificate["gordan_weight"][pattern, bit],
            element,
        )
        supports.append(tuple(TRIPLES[index] for index in support))
        circuit.extend(rows)
    expected_supports = (
        ((1, 3, 4), (2, 3, 4), (1, 5, 6), (2, 6, 7), (2, 5, 8)),
        ((1, 2, 5), (2, 4, 6), (1, 4, 7), (3, 5, 8), (4, 6, 8)),
    )
    if tuple(supports) != expected_supports:
        raise AssertionError(f"unexpected disconnected-exit supports: {supports}")

    vertices = normalized_vertices(parent, circuit)
    facets, simplices = exit_nerve(parent, vertices)
    components = nerve_components(facets, simplices)
    facet_names = {index: format_basis(tags[index]) for index in facets}
    named_components = {
        frozenset(facet_names[index] for index in component)
        for component in components
    }
    expected = {frozenset(("1237", "5678")), frozenset(("1367",))}
    if named_components != expected:
        raise AssertionError(f"unexpected exit components: {named_components}")
    print("PASS common-light pair exit nerve = edge(1237,5678) disjoint union vertex(1367)")
    print("PASS exact exit has two components, so H_c^1 of the residence fiber is Q")


def verify_cyclic_exit(certificate):
    pattern = 0
    bit = 4
    element = 8
    matrix = certificate["pattern_chart"][pattern]
    normals = koszul.parent_normals(matrix)
    parent, tags = residence_rows(matrix, element)
    support, circuit = circuit_rows(
        matrix,
        normals,
        int(certificate["signature"][bit]),
        certificate["gordan_weight"][pattern, bit],
        element,
    )
    expected_support = (
        (1, 2, 3),
        (2, 5, 6),
        (1, 2, 7),
        (3, 5, 7),
        (4, 7, 8),
    )
    if tuple(TRIPLES[index] for index in support) != expected_support:
        raise AssertionError("unexpected cyclic-exit support")

    vertices = normalized_vertices(parent, circuit)
    facets, simplices = exit_nerve(parent, vertices)
    names = {index: format_basis(tags[index]) for index in facets}
    if {names[index] for index in facets} != {
        "2458", "2368", "3468", "3578", "5678"
    }:
        raise AssertionError("unexpected cyclic-exit facets")
    if len(nerve_components(facets, simplices)) != 1:
        raise AssertionError("cyclic exit should be connected")
    betti = first_betti(simplices)
    if betti != 1:
        raise AssertionError(f"unexpected first Betti number {betti}")
    print("PASS single common-light exit nerve is connected with beta_1 = 1")
    print("PASS exact residence fiber has H_c^2 = Q")


def main():
    certificate = np.load(CERTIFICATE, allow_pickle=False)
    catalog = [
        line.strip()
        for line in gate.CATALOG_48.open(encoding="utf-8")
        if line.strip()
    ]
    expected_parent = catalog[gate.PARENT_INDEX]

    # Patterns 1 and 64 separate signatures 0 and 6 in both directions.
    # Pattern 14 supplies their joint positive-circuit example.
    for pattern, bit, supported in (
        (1, 0, True),
        (1, 6, False),
        (64, 0, False),
        (64, 6, True),
        (14, 0, False),
        (14, 6, False),
        (0, 4, False),
        (16, 4, True),
    ):
        verify_parent_and_state(
            certificate, pattern, bit, supported, expected_parent
        )
    print("PASS exact support states prove properness and pairwise incomparability")

    verify_disconnected_exit(certificate)
    verify_cyclic_exit(certificate)
    print("THEOREM: common-light exits are not automatically connected or H1-acyclic")


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    main()
