#!/usr/bin/env python3
"""Exact transverse two-wall disk inside row-2599 realization space.

In the same matrix-coordinate plane used by the earlier line and disk
certificates, this verifier centers a radius-1/1000 square at the exact
intersection of two coprime residual line factors.  It proves that exactly
65 labeled occurrences belong to each branch, every remaining residual
determinant and every branch quotient is nonzero on the square, and the two
branch gradients have rank two.  It then labels all four cells, four generic
wall rays, and the codimension-two node by exact tope recursion.

The result is complete on this embedded two-dimensional disk only.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
from collections import Counter
from itertools import combinations
from math import comb, lcm
from pathlib import Path

import numpy as np

import DIAG9_GRAPH_exact_topes as topes
import DIAG9_GRAPH_verify_row2599_disk as disk
import DIAG9_GRAPH_verify_row2599_slice as slice_verify


HERE = Path(__file__).resolve().parent
ROADMAP = HERE / "data" / "DIAG9_GRAPH_row2599_node_roadmap.npz"
GRAPH = HERE / "data" / "DIAG9_GRAPH_row2599_node_graph.npz"
FORMAT = "diag9-row2599-transverse-node-v1"
GRAPH_FORMAT = "diag9-labeled-master-tree-v1"
CENTER_S = Fraction(
    5_455_638_564_396_767_806_348_493_946_599,
    3_394_705_968_860_801_647_269_075_678_720,
)
CENTER_U = Fraction(
    1_631_359_879_664_336_977_038_655_284_413,
    1_697_352_984_430_400_823_634_537_839_360,
)
RADIUS = Fraction(1, 1_000)
BRANCHES = (
    {
        (0, 0): -8_406_719_710_014_481,
        (1, 0): 5_934_554_455_910_656,
        (0, 1): -1_176_454_877_277_824,
    },
    {
        (0, 0): -30_838_233_534_021_888,
        (1, 0): 9_738_264_925_739_162,
        (0, 1): 15_802_240_330_472_297,
    },
)
OTHER_MARGIN = Fraction(
    59_660_984_923_497_009_863_930_871_344_289_908_850_373_956_705_025,
    11_076_265_907_589_991_762_853_491_013_495_358_778_478_172_987_792,
)
BRANCH_MARGINS = (
    Fraction(
        31_070_614_434_869_202_946_595_039_532_555_983_225,
        13_821_290_749_269_089_346_732_496_445_232_576,
    ),
    Fraction(
        55_464_724_498_960_225_839_079_342_532_405_821_625,
        22_131_106_622_794_224_179_041_285_072_279_296,
    ),
)
BRACKET_MARGIN = BRANCH_MARGINS[0]
OTHER_WORST = (2, 8, 22, 49)
BRANCH_WORST = ((10, 18, 35, 40), (2, 32, 41, 43))
BRACKET_WORST = (0, 1, 5, 7)
CELL_SIGNS = ((1, 1), (1, -1), (-1, -1), (-1, 1))
GRAPH_EDGES = ((0, 1), (1, 2), (2, 3), (0, 3))
TREE_EDGES = ((0, 1), (1, 2), (2, 3))


def branch_value(branch, s_value, u_value):
    return (
        branch[(0, 0)]
        + branch[(1, 0)] * s_value
        + branch[(0, 1)] * u_value
    )


def shift_polynomial(polynomial):
    """Translate p(s,u) to p(CENTER_S+x,CENTER_U+y)."""
    result = {}
    for (s_degree, u_degree), coefficient in polynomial.items():
        for x_degree in range(s_degree + 1):
            for y_degree in range(u_degree + 1):
                monomial = (x_degree, y_degree)
                result[monomial] = result.get(monomial, 0) + (
                    Fraction(coefficient)
                    * comb(s_degree, x_degree)
                    * CENTER_S ** (s_degree - x_degree)
                    * comb(u_degree, y_degree)
                    * CENTER_U ** (u_degree - y_degree)
                )
    return disk.clean(result)


def centered_linear(branch):
    if branch_value(branch, CENTER_S, CENTER_U) != 0:
        raise AssertionError("claimed branch misses the exact node")
    return {(1, 0): branch[(1, 0)], (0, 1): branch[(0, 1)]}


CENTERED_BRANCHES = tuple(centered_linear(branch) for branch in BRANCHES)


def divide_by_linear(polynomial, linear):
    remainder = dict(polynomial)
    quotient = {}
    coefficient_x = Fraction(linear[(1, 0)])
    coefficient_y = Fraction(linear[(0, 1)])
    while any(x_degree > 0 for x_degree, _ in remainder):
        x_degree, y_degree = max(
            monomial for monomial in remainder if monomial[0] > 0
        )
        value = remainder[(x_degree, y_degree)] / coefficient_x
        monomial = (x_degree - 1, y_degree)
        quotient[monomial] = quotient.get(monomial, 0) + value
        remainder[(x_degree, y_degree)] -= value * coefficient_x
        if not remainder[(x_degree, y_degree)]:
            del remainder[(x_degree, y_degree)]
        shifted = (x_degree - 1, y_degree + 1)
        remainder[shifted] = (
            remainder.get(shifted, 0) - value * coefficient_y
        )
        if not remainder[shifted]:
            del remainder[shifted]
    return disk.clean(quotient) if not remainder else None


def radius_ratio(polynomial):
    constant = abs(Fraction(polynomial.get((0, 0), 0)))
    if not constant:
        raise AssertionError("radius-bound polynomial has zero constant")
    tail = sum(
        abs(Fraction(value)) * RADIUS ** (x_degree + y_degree)
        for (x_degree, y_degree), value in polynomial.items()
        if x_degree + y_degree
    )
    if not tail:
        return None
    ratio = constant / tail
    if ratio <= 1:
        raise AssertionError("radius-1/1000 dominance failed")
    return ratio


def update_minimum(current, ratio, witness):
    if ratio is None:
        return current
    if current[0] is None or ratio < current[0]:
        return ratio, witness
    return current


def exact_geometry():
    base = slice_verify.source_parent()
    polynomial_matrix = disk.polynomial_parent(base)
    normal_rows = disk.derived_polynomial_rows(polynomial_matrix)
    branch_occurrences = [[], []]
    quotient_degrees = [[0, 0], [0, 0]]
    other_minimum = (None, None)
    branch_minimum = [(None, None), (None, None)]

    residual = slice_verify.residual_foursets()
    for fourset in residual:
        polynomial = shift_polynomial(
            disk.determinant([normal_rows[index] for index in fourset])
        )
        if polynomial.get((0, 0), 0):
            other_minimum = update_minimum(
                other_minimum, radius_ratio(polynomial), fourset
            )
            continue

        quotients = tuple(
            divide_by_linear(polynomial, linear) for linear in CENTERED_BRANCHES
        )
        matching = tuple(index for index, quotient in enumerate(quotients) if quotient is not None)
        if len(matching) != 1:
            raise AssertionError("node occurrence has ambiguous branch factor")
        branch = matching[0]
        quotient = quotients[branch]
        degree = disk.total_degree(quotient)
        if degree not in (0, 1):
            raise AssertionError("unexpected node quotient degree")
        quotient_degrees[branch][degree] += 1
        branch_occurrences[branch].append(fourset)
        branch_minimum[branch] = update_minimum(
            branch_minimum[branch], radius_ratio(quotient), fourset
        )

    if len(residual) != 84_840:
        raise AssertionError("wrong residual fourset census")
    if tuple(map(len, branch_occurrences)) != (65, 65):
        raise AssertionError("wrong transverse branch multiplicities")
    if tuple(map(tuple, quotient_degrees)) != ((32, 33), (32, 33)):
        raise AssertionError("wrong branch quotient degree census")
    if other_minimum != (OTHER_MARGIN, OTHER_WORST):
        raise AssertionError("wrong other-residual disk margin")
    if tuple(branch_minimum) != tuple(zip(BRANCH_MARGINS, BRANCH_WORST)):
        raise AssertionError("wrong branch quotient disk margins")

    bracket_minimum = (None, None)
    for basis in topes.BASES:
        polynomial = shift_polynomial(
            disk.determinant(
                [
                    [polynomial_matrix[row][column] for column in basis]
                    for row in range(4)
                ]
            )
        )
        bracket_minimum = update_minimum(
            bracket_minimum, radius_ratio(polynomial), basis
        )
    if bracket_minimum != (BRACKET_MARGIN, BRACKET_WORST):
        raise AssertionError("wrong parent-bracket disk margin")

    first = CENTERED_BRANCHES[0]
    second = CENTERED_BRANCHES[1]
    jacobian = (
        first[(1, 0)] * second[(0, 1)]
        - second[(1, 0)] * first[(0, 1)]
    )
    if not jacobian:
        raise AssertionError("residual branches are not transverse")
    if any(
        abs(linear[(1, 0)]) == abs(linear[(0, 1)])
        for linear in CENTERED_BRANCHES
    ):
        raise AssertionError("a branch passes through a disk corner")

    return {
        "branch_occurrences": tuple(tuple(row) for row in branch_occurrences),
        "quotient_degrees": tuple(tuple(row) for row in quotient_degrees),
        "other_margin": other_minimum[0],
        "branch_margins": tuple(row[0] for row in branch_minimum),
        "bracket_margin": bracket_minimum[0],
        "jacobian": jacobian,
    }


def rational_parent(x_value, y_value):
    s_value = CENTER_S + x_value
    u_value = CENTER_U + y_value
    denominator = lcm(s_value.denominator, u_value.denominator)
    matrix = np.asarray(slice_verify.source_parent(), dtype=object) * denominator
    matrix[disk.FIRST_POSITION] += (
        s_value.numerator * (denominator // s_value.denominator)
    )
    matrix[disk.SECOND_POSITION] += (
        u_value.numerator * (denominator // u_value.denominator)
    )
    return matrix


def cell_points():
    half = RADIUS / 2
    return tuple((first * half, second * half) for first, second in CELL_SIGNS)


def wall_points():
    points = []
    for linear in CENTERED_BRANCHES:
        coefficient_x = linear[(1, 0)]
        coefficient_y = linear[(0, 1)]
        scale = RADIUS / (2 * max(abs(coefficient_x), abs(coefficient_y)))
        tangent = (scale * coefficient_y, -scale * coefficient_x)
        points.extend(((-tangent[0], -tangent[1]), tangent))
    return tuple(points)


def sign_pair(point):
    result = []
    for linear in CENTERED_BRANCHES:
        value = linear[(1, 0)] * point[0] + linear[(0, 1)] * point[1]
        result.append(1 if value > 0 else -1 if value < 0 else 0)
    return tuple(result)


def exact_labels():
    expected_parent = slice_verify.expected_parent_signs()
    cells = []
    for point, expected_signs in zip(cell_points(), CELL_SIGNS):
        if sign_pair(point) != expected_signs:
            raise AssertionError("cell sample has wrong branch signs")
        matrix = rational_parent(*point)
        if topes.parent_signs(matrix) != expected_parent:
            raise AssertionError("cell sample leaves parent 2599")
        labels = tuple(sorted(topes.parent_topes(matrix)))
        if len(labels) != 26_112:
            raise AssertionError("wrong generic cell tope count")
        cells.append(labels)

    walls = []
    expected_wall_signs = ((0, 1), (0, -1), (-1, 0), (1, 0))
    for point, expected_signs in zip(wall_points(), expected_wall_signs):
        if sign_pair(point) != expected_signs:
            raise AssertionError("wall-ray sample has wrong branch signs")
        matrix = rational_parent(*point)
        if topes.parent_signs(matrix) != expected_parent:
            raise AssertionError("wall sample leaves parent 2599")
        labels = tuple(sorted(topes.parent_topes(matrix)))
        if len(labels) != 26_040:
            raise AssertionError("wrong generic wall tope count")
        walls.append(labels)

    node_matrix = rational_parent(Fraction(0), Fraction(0))
    if topes.parent_signs(node_matrix) != expected_parent:
        raise AssertionError("node leaves parent 2599")
    disk.verify_embedded_disk(node_matrix)
    node = tuple(sorted(topes.parent_topes(node_matrix)))
    if len(node) != 25_968:
        raise AssertionError("wrong codimension-two node tope count")

    cell_sets = tuple(map(set, cells))
    wall_sets = tuple(map(set, walls))
    adjacent_pairs = ((0, 3), (1, 2), (2, 3), (0, 1))
    for wall, pair in zip(wall_sets, adjacent_pairs):
        if wall != cell_sets[pair[0]] & cell_sets[pair[1]]:
            raise AssertionError("wall label set is not adjacent-cell intersection")
    if set(node) != set.intersection(*cell_sets):
        raise AssertionError("node labels are not the four-cell intersection")
    if any(set(node) != set.intersection(*pair) for pair in combinations(wall_sets, 2)):
        raise AssertionError("node labels are not every two-wall intersection")
    return tuple(cells), tuple(walls), node


def signature_patterns(cells):
    patterns = {}
    for cell, labels in enumerate(cells):
        for signature in labels:
            patterns[signature] = patterns.get(signature, 0) | (1 << cell)
    return patterns


def support_matrix(patterns):
    full = (1 << len(CELL_SIGNS)) - 1
    proper = tuple(sorted(set(patterns.values()) - {0, full}))
    matrix = np.asarray(
        tuple(
            tuple((pattern >> cell) & 1 for cell in range(len(CELL_SIGNS)))
            for pattern in proper
        ),
        dtype=np.uint8,
    )
    return proper, matrix


def connected_mask(mask):
    vertices = {vertex for vertex in range(4) if mask & (1 << vertex)}
    if not vertices:
        return True
    seen = {min(vertices)}
    while True:
        expanded = seen | {
            right
            for left, right in GRAPH_EDGES
            if left in seen and right in vertices
        } | {
            left
            for left, right in GRAPH_EDGES
            if right in seen and left in vertices
        }
        if expanded == seen:
            return seen == vertices
        seen = expanded


def verify_intersection_closure(patterns):
    generators = set(patterns.values())
    closure = {15}
    for pattern in generators:
        closure |= {old & pattern for old in tuple(closure)}
    disconnected = tuple(mask for mask in closure if mask and not connected_mask(mask))
    multiplicities = Counter(patterns.values())
    if multiplicities != Counter({15: 25_968, 3: 72, 6: 72, 9: 72, 12: 72}):
        raise AssertionError("wrong transverse-node support multiplicities")
    if tuple(sorted(generators - {15})) != (3, 6, 9, 12):
        raise AssertionError("wrong transverse-node proper support patterns")
    if tuple(sorted(closure)) != (0, 1, 2, 3, 4, 6, 8, 9, 12, 15):
        raise AssertionError("wrong transverse-node intersection closure")
    if disconnected:
        raise AssertionError("transverse-node support closure is disconnected")
    return tuple(sorted(closure)), disconnected


def fraction_fields(prefix, value):
    return {
        f"{prefix}_num": np.asarray(str(value.numerator)),
        f"{prefix}_den": np.asarray(str(value.denominator)),
    }


def build():
    geometry = exact_geometry()
    cells, walls, node = exact_labels()
    patterns = signature_patterns(cells)
    proper, support = support_matrix(patterns)
    closure, disconnected = verify_intersection_closure(patterns)

    offsets = [0]
    flat_occurrences = []
    for branch in geometry["branch_occurrences"]:
        flat_occurrences.extend(branch)
        offsets.append(len(flat_occurrences))
    np.savez_compressed(
        ROADMAP,
        format=np.asarray(FORMAT),
        parent_index=np.asarray(slice_verify.PARENT_INDEX, dtype=np.int64),
        source_chart=np.asarray(slice_verify.SOURCE_CHART, dtype=np.int64),
        center_s_num=np.asarray(str(CENTER_S.numerator)),
        center_s_den=np.asarray(str(CENTER_S.denominator)),
        center_u_num=np.asarray(str(CENTER_U.numerator)),
        center_u_den=np.asarray(str(CENTER_U.denominator)),
        radius_num=np.asarray(str(RADIUS.numerator)),
        radius_den=np.asarray(str(RADIUS.denominator)),
        branch_affine=np.asarray(
            tuple(
                (branch[(0, 0)], branch[(1, 0)], branch[(0, 1)])
                for branch in BRANCHES
            ),
            dtype=np.int64,
        ),
        branch_offset=np.asarray(offsets, dtype=np.uint16),
        branch_fourset=np.asarray(flat_occurrences, dtype=np.uint8),
        quotient_degree_count=np.asarray(geometry["quotient_degrees"], dtype=np.uint8),
        jacobian=np.asarray(str(geometry["jacobian"])),
        cell_tope=np.asarray(cells, dtype=np.uint64),
        wall_tope=np.asarray(walls, dtype=np.uint64),
        node_tope=np.asarray(node, dtype=np.uint64),
        signature=np.asarray(tuple(sorted(patterns)), dtype=np.uint64),
        signature_pattern=np.asarray(
            tuple(patterns[signature] for signature in sorted(patterns)), dtype=np.uint8
        ),
        intersection_closure=np.asarray(closure, dtype=np.uint8),
        disconnected_closure=np.asarray(disconnected, dtype=np.uint8),
        **fraction_fields("other_margin", geometry["other_margin"]),
        **fraction_fields("branch0_margin", geometry["branch_margins"][0]),
        **fraction_fields("branch1_margin", geometry["branch_margins"][1]),
        **fraction_fields("bracket_margin", geometry["bracket_margin"]),
    )
    np.savez_compressed(
        GRAPH,
        format=np.asarray(GRAPH_FORMAT),
        edge=np.asarray(GRAPH_EDGES, dtype=np.int64),
        support=support,
        tree_edge=np.asarray(TREE_EDGES, dtype=np.int64),
    )
    print("WROTE", ROADMAP)
    print("WROTE", GRAPH)
    print("SUPPORT PATTERNS", proper)
    print("INTERSECTION CLOSURE", closure, "DISCONNECTED", disconnected)


def load_fraction(certificate, prefix):
    return Fraction(
        int(certificate[f"{prefix}_num"].item()),
        int(certificate[f"{prefix}_den"].item()),
    )


def verify():
    certificate = np.load(ROADMAP, allow_pickle=False)
    required = {
        "format", "parent_index", "source_chart",
        "center_s_num", "center_s_den", "center_u_num", "center_u_den",
        "radius_num", "radius_den", "branch_affine", "branch_offset",
        "branch_fourset", "quotient_degree_count", "jacobian",
        "cell_tope", "wall_tope", "node_tope", "signature",
        "signature_pattern", "intersection_closure", "disconnected_closure",
        "other_margin_num", "other_margin_den", "branch0_margin_num",
        "branch0_margin_den", "branch1_margin_num", "branch1_margin_den",
        "bracket_margin_num", "bracket_margin_den",
    }
    if set(certificate.files) != required:
        raise AssertionError("wrong transverse-node certificate fields")
    if str(certificate["format"].item()) != FORMAT:
        raise AssertionError("wrong transverse-node format")
    if int(certificate["parent_index"].item()) != slice_verify.PARENT_INDEX:
        raise AssertionError("wrong parent index")
    if int(certificate["source_chart"].item()) != slice_verify.SOURCE_CHART:
        raise AssertionError("wrong source chart")
    if load_fraction(certificate, "center_s") != CENTER_S:
        raise AssertionError("wrong node s-coordinate")
    if load_fraction(certificate, "center_u") != CENTER_U:
        raise AssertionError("wrong node u-coordinate")
    if load_fraction(certificate, "radius") != RADIUS:
        raise AssertionError("wrong node disk radius")
    expected_affine = tuple(
        (branch[(0, 0)], branch[(1, 0)], branch[(0, 1)]) for branch in BRANCHES
    )
    if tuple(tuple(map(int, row)) for row in certificate["branch_affine"]) != expected_affine:
        raise AssertionError("wrong stored branch factors")

    geometry = exact_geometry()
    offsets = tuple(map(int, certificate["branch_offset"]))
    flat = tuple(tuple(map(int, row)) for row in certificate["branch_fourset"])
    stored_branches = tuple(
        flat[offsets[index] : offsets[index + 1]]
        for index in range(len(offsets) - 1)
    )
    if stored_branches != geometry["branch_occurrences"]:
        raise AssertionError("stored branch occurrence groups disagree")
    if tuple(tuple(map(int, row)) for row in certificate["quotient_degree_count"]) != geometry["quotient_degrees"]:
        raise AssertionError("stored quotient census disagrees")
    if int(certificate["jacobian"].item()) != geometry["jacobian"]:
        raise AssertionError("stored branch Jacobian disagrees")
    for prefix, value in (
        ("other_margin", geometry["other_margin"]),
        ("branch0_margin", geometry["branch_margins"][0]),
        ("branch1_margin", geometry["branch_margins"][1]),
        ("bracket_margin", geometry["bracket_margin"]),
    ):
        if load_fraction(certificate, prefix) != value:
            raise AssertionError(f"stored {prefix} disagrees")

    cells, walls, node = exact_labels()
    stored_cells = tuple(tuple(map(int, row)) for row in certificate["cell_tope"])
    stored_walls = tuple(tuple(map(int, row)) for row in certificate["wall_tope"])
    stored_node = tuple(map(int, certificate["node_tope"]))
    if (stored_cells, stored_walls, stored_node) != (cells, walls, node):
        raise AssertionError("stored node labels disagree")
    patterns = signature_patterns(cells)
    signatures = tuple(map(int, certificate["signature"]))
    if signatures != tuple(sorted(patterns)):
        raise AssertionError("stored node signature union disagrees")
    if tuple(map(int, certificate["signature_pattern"])) != tuple(
        patterns[signature] for signature in signatures
    ):
        raise AssertionError("stored node support patterns disagree")
    proper, support = support_matrix(patterns)
    closure, disconnected = verify_intersection_closure(patterns)
    if tuple(map(int, certificate["intersection_closure"])) != closure:
        raise AssertionError("stored intersection closure disagrees")
    if tuple(map(int, certificate["disconnected_closure"])) != disconnected:
        raise AssertionError("stored disconnected closure disagrees")

    graph = np.load(GRAPH, allow_pickle=False)
    if set(graph.files) != {"format", "edge", "support", "tree_edge"}:
        raise AssertionError("wrong node graph fields")
    if str(graph["format"].item()) != GRAPH_FORMAT:
        raise AssertionError("wrong node graph format")
    if not np.array_equal(graph["support"], support):
        raise AssertionError("node graph support quotient disagrees")

    print("PASS: exactly 65+65 labeled occurrences lie on two coprime branches")
    print("PASS: exact branch Jacobian has rank two at the rational node")
    print("PASS: all other residuals, quotients, and brackets avoid the disk")
    print("PASS: exact labels: 4x26112 cells, 4x26040 walls, 25968 node")
    print(f"PASS: {len(proper)} proper support patterns; closure={closure}")
    if disconnected:
        print(f"LOCAL OBSTRUCTION: disconnected intersection masks {disconnected}")
    else:
        print("THEOREM: every finite signature-family support is connected or empty on the disk")
    print("THEOREM: complete four-cell transverse residual roadmap in parent 2599")
    print("SCOPE: exact local 2D disk, not the full 9D parent-2599 roadmap")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    parser.add_argument("--build-only", action="store_true")
    args = parser.parse_args()
    if args.build or args.build_only:
        build()
    if not args.build_only:
        verify()


if __name__ == "__main__":
    main()
