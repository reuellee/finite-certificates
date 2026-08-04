#!/usr/bin/env python3
"""Exact two-dimensional residual roadmap around the row-2599 crossing.

Let W be the integer matrix representing the exact rational crossing from
DIAG9_GRAPH_verify_row2599_slice.py.  On the closed matrix-coordinate square

    W(s,u) = W + s E_(2,7) + u E_(1,7),   |s|,|u| <= 1,

all 65 residual determinants vanishing at the center have the common
primitive factor

    q(s,u) = 1401176374297*s + 849195472073*u.

Exact polynomial division proves that their common gcd is q; 32 quotients
are constant and 33 are affine.  Monomial interval bounds prove every
quotient, every other residual determinant, and every parent bracket is
nonzero throughout the square.  Hence q=0 is the complete residual roadmap:
one wall segment and two convex cells.  Exact tope recursion labels both
cells and the wall.

The certificate is complete on this two-dimensional square only.  It is not
a roadmap of the full nine-dimensional parent realization cell.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
from math import gcd
from pathlib import Path

import numpy as np

import DIAG9_GRAPH_exact_topes as topes
import DIAG9_GRAPH_verify_row2599_slice as slice_verify


HERE = Path(__file__).resolve().parent
ROADMAP = HERE / "data" / "DIAG9_GRAPH_row2599_disk_roadmap.npz"
GRAPH = HERE / "data" / "DIAG9_GRAPH_row2599_disk_graph.npz"
FORMAT = "diag9-row2599-r2c7-r1c7-disk-v1"
GRAPH_FORMAT = "diag9-labeled-master-tree-v1"
FIRST_POSITION = (slice_verify.VARYING_ROW, slice_verify.VARYING_COLUMN)
SECOND_POSITION = (1, 7)
RADIUS = 1
COMMON_FACTOR = {(1, 0): 1_401_176_374_297, (0, 1): 849_195_472_073}
NONWALL_MARGIN = Fraction(
    740_674_058_109_807_867_500_619_055_086_000_864_162_027_205_792,
    235_417_541_795_415_977_558_174_456_893_317_629_385,
)
UNIT_MARGIN = Fraction(164_520_501_384_745_467, 43_462)
NONWALL_WORST = (24, 34, 35, 48)
UNIT_WORST = (5, 10, 43, 50)
BRACKET_WORST = (0, 2, 4, 7)


def clean(polynomial):
    return {monomial: value for monomial, value in polynomial.items() if value}


def add(left, right, scale=1):
    result = dict(left)
    for monomial, value in right.items():
        result[monomial] = result.get(monomial, 0) + scale * value
    return clean(result)


def multiply(left, right):
    result = {}
    for (first_s, first_u), first_value in left.items():
        for (second_s, second_u), second_value in right.items():
            monomial = (first_s + second_s, first_u + second_u)
            result[monomial] = (
                result.get(monomial, 0) + first_value * second_value
            )
    return clean(result)


def determinant(matrix):
    if len(matrix) == 1:
        return matrix[0][0]
    result = {}
    for column, value in enumerate(matrix[0]):
        minor = [row[:column] + row[column + 1 :] for row in matrix[1:]]
        result = add(
            result,
            multiply(value, determinant(minor)),
            -1 if column & 1 else 1,
        )
    return result


def primitive(polynomial):
    divisor = 0
    for value in polynomial.values():
        if getattr(value, "denominator", 1) != 1:
            raise AssertionError("primitive expects integer coefficients")
        divisor = gcd(divisor, abs(int(value)))
    result = {
        monomial: int(value) // max(divisor, 1)
        for monomial, value in polynomial.items()
    }
    leading = max(result)
    if result[leading] < 0:
        result = {monomial: -value for monomial, value in result.items()}
    return clean(result)


def total_degree(polynomial):
    return max((sum(monomial) for monomial in polynomial), default=-1)


def divide_by_common_factor(polynomial):
    """Exact lexicographic division by A*s+B*u."""
    remainder = {
        monomial: Fraction(value) for monomial, value in polynomial.items()
    }
    quotient = {}
    coefficient_s = Fraction(COMMON_FACTOR[(1, 0)])
    coefficient_u = Fraction(COMMON_FACTOR[(0, 1)])
    while any(s_degree > 0 for s_degree, _ in remainder):
        s_degree, u_degree = max(
            monomial for monomial in remainder if monomial[0] > 0
        )
        value = remainder[(s_degree, u_degree)] / coefficient_s
        quotient_monomial = (s_degree - 1, u_degree)
        quotient[quotient_monomial] = (
            quotient.get(quotient_monomial, 0) + value
        )

        remainder[(s_degree, u_degree)] -= value * coefficient_s
        if not remainder[(s_degree, u_degree)]:
            del remainder[(s_degree, u_degree)]
        shifted = (s_degree - 1, u_degree + 1)
        remainder[shifted] = remainder.get(shifted, 0) - value * coefficient_u
        if not remainder[shifted]:
            del remainder[shifted]
    if remainder:
        raise AssertionError("crossing polynomial is not divisible by q")
    if any(value.denominator != 1 for value in quotient.values()):
        raise AssertionError("primitive linear division produced fractions")
    return {monomial: int(value) for monomial, value in quotient.items()}


def dominance_ratio(polynomial):
    """Return |constant| / sum |other coefficients| on the unit square."""
    constant = Fraction(polynomial.get((0, 0), 0))
    if not constant:
        raise AssertionError("dominance polynomial has zero constant term")
    tail = sum(
        abs(Fraction(value))
        for monomial, value in polynomial.items()
        if monomial != (0, 0)
    )
    if not tail:
        return None
    ratio = abs(constant) / tail
    if ratio <= RADIUS:
        raise AssertionError("unit-square monomial dominance failed")
    return ratio


def center_parent():
    return np.asarray(
        slice_verify.scaled_parent(
            slice_verify.source_parent(), slice_verify.WALL
        ),
        dtype=object,
    )


def verify_embedded_disk(center):
    """Certify that the coordinate square injects into projective moduli.

    The first four fixed labeled columns are a basis. Any projectivity fixing
    their four projective points is diagonal in that basis. The fifth fixed
    column has four nonzero basis coordinates, so the diagonal is scalar.
    The eighth column has a fixed nonzero row-zero coordinate; proportional
    eighth columns in the square must therefore have scale one and equal
    (s,u) coordinates.
    """
    basis = tuple(
        tuple(int(center[row, column]) for column in range(4))
        for row in range(4)
    )
    basis_determinant = topes.determinant(basis)
    if not basis_determinant:
        raise AssertionError("first four disk columns are not a projective frame")
    fifth = tuple(int(center[row, 4]) for row in range(4))
    cramer_numerators = []
    for replaced in range(4):
        matrix = [list(row) for row in basis]
        for row in range(4):
            matrix[row][replaced] = fifth[row]
        cramer_numerators.append(topes.determinant(matrix))
    if any(value == 0 for value in cramer_numerators):
        raise AssertionError("fifth column does not kill the frame torus")
    if int(center[0, 7]) == 0:
        raise AssertionError("eighth-column proportionality scale is not fixed")


def polynomial_parent(center):
    matrix = [
        [{(0, 0): int(center[row, column])} for column in range(8)]
        for row in range(4)
    ]
    matrix[FIRST_POSITION[0]][FIRST_POSITION[1]][(1, 0)] = 1
    matrix[SECOND_POSITION[0]][SECOND_POSITION[1]][(0, 1)] = 1
    return matrix


def derived_polynomial_rows(matrix):
    rows = []
    for triple in topes.TRIPLES:
        columns = [[matrix[row][column] for column in triple] for row in range(4)]
        normal = []
        for omitted in range(4):
            minor = [row for index, row in enumerate(columns) if index != omitted]
            normal.append(
                {
                    monomial: (-1) ** (omitted + 3) * value
                    for monomial, value in determinant(minor).items()
                }
            )
        rows.append(tuple(normal))
    return tuple(rows)


def exact_geometry(center):
    matrix = polynomial_parent(center)
    normal_rows = derived_polynomial_rows(matrix)
    crossing = []
    constant_quotients = 0
    affine_quotients = 0
    minimum_nonwall = None
    minimum_nonwall_fourset = None
    minimum_unit = None
    minimum_unit_fourset = None

    residual = slice_verify.residual_foursets()
    for fourset in residual:
        polynomial = determinant([normal_rows[index] for index in fourset])
        if not polynomial:
            raise AssertionError("coordinate square lies in a residual determinant")
        if polynomial.get((0, 0), 0) == 0:
            quotient = divide_by_common_factor(polynomial)
            degree = total_degree(quotient)
            if degree == 0:
                constant_quotients += 1
            elif degree == 1:
                affine_quotients += 1
            else:
                raise AssertionError("unexpected common-factor quotient degree")
            ratio = dominance_ratio(quotient)
            if ratio is not None and (
                minimum_unit is None or ratio < minimum_unit
            ):
                minimum_unit = ratio
                minimum_unit_fourset = fourset
            crossing.append(fourset)
        else:
            ratio = dominance_ratio(polynomial)
            if ratio is not None and (
                minimum_nonwall is None or ratio < minimum_nonwall
            ):
                minimum_nonwall = ratio
                minimum_nonwall_fourset = fourset

    if len(residual) != 84_840 or len(crossing) != 65:
        raise AssertionError("wrong residual/crossing occurrence counts")
    if (constant_quotients, affine_quotients) != (32, 33):
        raise AssertionError("wrong common-factor quotient census")
    if minimum_nonwall != NONWALL_MARGIN:
        raise AssertionError("wrong nonwall dominance margin")
    if minimum_nonwall_fourset != NONWALL_WORST:
        raise AssertionError("wrong worst nonwall determinant")
    if minimum_unit != UNIT_MARGIN or minimum_unit_fourset != UNIT_WORST:
        raise AssertionError("wrong common-factor quotient margin")

    # Since at least one quotient is a nonzero constant, the gcd of all 65
    # crossing polynomials cannot contain a further nonunit factor.  The
    # common primitive Q[s,u] gcd is exactly q.
    if constant_quotients == 0:
        raise AssertionError("common factor was not proved maximal")

    minimum_bracket = None
    minimum_bracket_basis = None
    for basis in topes.BASES:
        polynomial = determinant(
            [[matrix[row][column] for column in basis] for row in range(4)]
        )
        ratio = dominance_ratio(polynomial)
        if ratio is not None and (
            minimum_bracket is None or ratio < minimum_bracket
        ):
            minimum_bracket = ratio
            minimum_bracket_basis = basis
    if minimum_bracket != UNIT_MARGIN or minimum_bracket_basis != BRACKET_WORST:
        raise AssertionError("wrong parent-bracket dominance margin")

    coefficient_s = COMMON_FACTOR[(1, 0)]
    coefficient_u = COMMON_FACTOR[(0, 1)]
    if not (0 < coefficient_u < coefficient_s):
        raise AssertionError("wall segment does not cross the top/bottom edges")

    return {
        "crossing": tuple(crossing),
        "constant_quotients": constant_quotients,
        "affine_quotients": affine_quotients,
        "minimum_nonwall": minimum_nonwall,
        "minimum_unit": minimum_unit,
        "minimum_bracket": minimum_bracket,
    }


def sample_parent(center, s_value, u_value):
    matrix = np.asarray(center, dtype=object).copy()
    matrix[FIRST_POSITION] += int(s_value)
    matrix[SECOND_POSITION] += int(u_value)
    return matrix


def exact_labels(center):
    expected_parent = slice_verify.expected_parent_signs()
    result = []
    for s_value, u_value in ((-1, 0), (0, 0), (1, 0)):
        parent = sample_parent(center, s_value, u_value)
        if topes.parent_signs(parent) != expected_parent:
            raise AssertionError("disk sample leaves parent 2599")
        labels = topes.parent_topes(parent)
        result.append(tuple(sorted(labels)))
    minus, wall, plus = map(set, result)
    if (len(minus), len(wall), len(plus)) != (26_112, 26_040, 26_112):
        raise AssertionError("wrong disk tope counts")
    if wall != minus & plus:
        raise AssertionError("wall labels are not the side-label intersection")
    if (len(minus - plus), len(plus - minus)) != (72, 72):
        raise AssertionError("wrong two-cell label mutation")
    return tuple(result)


def fraction_fields(prefix, value):
    return {
        f"{prefix}_num": np.asarray(str(value.numerator)),
        f"{prefix}_den": np.asarray(str(value.denominator)),
    }


def build():
    center = center_parent()
    verify_embedded_disk(center)
    geometry = exact_geometry(center)
    minus, wall, plus = exact_labels(center)
    np.savez_compressed(
        ROADMAP,
        format=np.asarray(FORMAT),
        parent_index=np.asarray(slice_verify.PARENT_INDEX, dtype=np.int64),
        source_chart=np.asarray(slice_verify.SOURCE_CHART, dtype=np.int64),
        center_matrix=np.asarray(center, dtype=np.int64),
        coordinate_position=np.asarray(
            (FIRST_POSITION, SECOND_POSITION), dtype=np.int8
        ),
        radius=np.asarray(RADIUS, dtype=np.int8),
        common_factor=np.asarray(
            (COMMON_FACTOR[(1, 0)], COMMON_FACTOR[(0, 1)]), dtype=np.int64
        ),
        wall_fourset=np.asarray(geometry["crossing"], dtype=np.uint8),
        quotient_degree_count=np.asarray(
            (geometry["constant_quotients"], geometry["affine_quotients"]),
            dtype=np.uint8,
        ),
        minus_tope=np.asarray(minus, dtype=np.uint64),
        wall_tope=np.asarray(wall, dtype=np.uint64),
        plus_tope=np.asarray(plus, dtype=np.uint64),
        **fraction_fields("nonwall_margin", geometry["minimum_nonwall"]),
        **fraction_fields("quotient_margin", geometry["minimum_unit"]),
        **fraction_fields("bracket_margin", geometry["minimum_bracket"]),
    )
    np.savez_compressed(
        GRAPH,
        format=np.asarray(GRAPH_FORMAT),
        edge=np.asarray(((0, 1),), dtype=np.int64),
        support=np.asarray(((1, 0), (0, 1)), dtype=np.uint8),
        tree_edge=np.asarray(((0, 1),), dtype=np.int64),
    )
    print("WROTE", ROADMAP)
    print("WROTE", GRAPH)


def load_fraction(certificate, prefix):
    return Fraction(
        int(certificate[f"{prefix}_num"].item()),
        int(certificate[f"{prefix}_den"].item()),
    )


def verify():
    certificate = np.load(ROADMAP, allow_pickle=False)
    required = {
        "format",
        "parent_index",
        "source_chart",
        "center_matrix",
        "coordinate_position",
        "radius",
        "common_factor",
        "wall_fourset",
        "quotient_degree_count",
        "minus_tope",
        "wall_tope",
        "plus_tope",
        "nonwall_margin_num",
        "nonwall_margin_den",
        "quotient_margin_num",
        "quotient_margin_den",
        "bracket_margin_num",
        "bracket_margin_den",
    }
    if set(certificate.files) != required:
        raise AssertionError("wrong disk-roadmap fields")
    if str(certificate["format"].item()) != FORMAT:
        raise AssertionError("wrong disk-roadmap format")
    if int(certificate["parent_index"].item()) != slice_verify.PARENT_INDEX:
        raise AssertionError("wrong parent index")
    if int(certificate["source_chart"].item()) != slice_verify.SOURCE_CHART:
        raise AssertionError("wrong source chart")
    if tuple(tuple(map(int, row)) for row in certificate["coordinate_position"]) != (
        FIRST_POSITION,
        SECOND_POSITION,
    ):
        raise AssertionError("wrong disk coordinate positions")
    if int(certificate["radius"].item()) != RADIUS:
        raise AssertionError("wrong disk radius")
    if tuple(map(int, certificate["common_factor"])) != (
        COMMON_FACTOR[(1, 0)],
        COMMON_FACTOR[(0, 1)],
    ):
        raise AssertionError("wrong stored common factor")

    center = center_parent()
    verify_embedded_disk(center)
    if not np.array_equal(certificate["center_matrix"], np.asarray(center, dtype=np.int64)):
        raise AssertionError("stored disk center disagrees")
    geometry = exact_geometry(center)
    stored_crossing = tuple(
        tuple(map(int, row)) for row in certificate["wall_fourset"]
    )
    if stored_crossing != geometry["crossing"]:
        raise AssertionError("stored crossing group disagrees")
    if tuple(map(int, certificate["quotient_degree_count"])) != (
        geometry["constant_quotients"],
        geometry["affine_quotients"],
    ):
        raise AssertionError("stored quotient census disagrees")
    if load_fraction(certificate, "nonwall_margin") != geometry["minimum_nonwall"]:
        raise AssertionError("stored nonwall margin disagrees")
    if load_fraction(certificate, "quotient_margin") != geometry["minimum_unit"]:
        raise AssertionError("stored quotient margin disagrees")
    if load_fraction(certificate, "bracket_margin") != geometry["minimum_bracket"]:
        raise AssertionError("stored bracket margin disagrees")

    recomputed = exact_labels(center)
    stored = tuple(
        tuple(map(int, certificate[field]))
        for field in ("minus_tope", "wall_tope", "plus_tope")
    )
    if stored != recomputed:
        raise AssertionError("stored exact disk labels disagree")

    graph = np.load(GRAPH, allow_pickle=False)
    if set(graph.files) != {"format", "edge", "support", "tree_edge"}:
        raise AssertionError("wrong disk graph fields")
    if str(graph["format"].item()) != GRAPH_FORMAT:
        raise AssertionError("wrong disk graph format")
    if not np.array_equal(
        graph["support"], np.asarray(((1, 0), (0, 1)), dtype=np.uint8)
    ):
        raise AssertionError("wrong disk support quotient")

    print("PASS: all 84,840 residual determinants have exact unit-square coverage")
    print("PASS: 65 center occurrences have exact primitive gcd q(s,u)")
    print("PASS: gcd quotients are 32 constant + 33 affine nonvanishing units")
    print("PASS: every other residual determinant and all 70 brackets stay nonzero")
    print("PASS: the matrix-coordinate square embeds in projective realization space")
    print("PASS: complete disk labels are 26112 -- 26040 -- 26112")
    print("THEOREM: the disk roadmap is two convex cells separated by one wall segment")
    print("THEOREM: every finite signature-family support is connected or empty on the disk")
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
