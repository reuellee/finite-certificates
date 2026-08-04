#!/usr/bin/env python3
"""Exact endpoint-wall reroute for the hard row-2599 triple.

The distinguished product cube in ``BLOCK_GORDAN_HARD_TRIPLE_PIVOT.py``
meets an endpoint-specific residual wall: its Q4 circuit dies while R4
survives.  This verifier gives a proof-safe local repair.

In the standard projective-frame gauge, let A be shatter pattern 0 and let E
be obtained from A by replacing only column 7 by column 7 of upper chart 152.
Along M(t)=(1-t)A+tE, 0 <= t <= 1, exact polynomial arithmetic proves:

* all 70 parent brackets retain their signs;
* the fixed positive circuits R0, R4 and the structural four-circuit C3 stay
  positive, so the whole segment remains in the hard triple intersection;
* the orbit-50 cofactor is strictly increasing and has one root rho in
  (1/3,3/8); Q4 drops to P at rho and is replaced by S4, while R4 remains
  strict throughout; and
* the transported supports R0/R4/C3 meet label 1 only in planes 134 and 127.
  Hence the degree-two pencil lemma gives a parent-boundary escape at every
  point of the segment.

All sign-on-an-interval statements are certified by exact Bernstein
coefficients.  There is no floating point, sampling, scipy, or sympy here.
This is a local component theorem, not a global matching and not a proof of
the third diagonal.
"""

from fractions import Fraction
from itertools import combinations
from math import comb
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import BLOCK_GORDAN_HARD_TRIPLE_PIVOT as pivot  # noqa: E402
import prototype_koszul_circuits as koszul  # noqa: E402
import verify_free_log_nonconvex as free_log  # noqa: E402


SHATTER = HERE / "data" / "seeat_parent2599_shatter8.npz"
UPPER = HERE / "data" / "seeat_parent2599_upper178.npz"
UPPER_CHART = 152

# The standard frame changes the signs of parent columns 1 and 3.  The
# determinant of the common row transformation is positive, so a triple sign
# changes by precisely the product of these column signs.
COLUMN_REORIENTATION = (-1, 1, -1, 1, 1, 1, 1, 1)

Q_NAMES = {
    0: ("123", "134", "267", "258", "468"),
    4: ("123", "256", "127", "357", "478"),
    3: ("123", "256", "356", "127", "347"),
}
R_NAMES = {
    0: ("134", "234", "267", "258", "468"),
    4: ("134", "256", "127", "357", "478"),
    3: ("134", "256", "356", "127", "347"),
}
C3_NAMES = ("127", "347", "357", "578")
S4_NAMES = ("123", "134", "256", "357", "478")
P_NAMES = ("123", "256", "357", "478")
BIT4_UNION_NAMES = ("123", "134", "256", "127", "357", "478")
EXPECTED_ESCAPE_DEGREES = (2, 5, 4, 5, 4, 3, 6, 4)


# Polynomials are tuples of rational power coefficients in increasing order.
def poly_trim(values):
    values = list(map(Fraction, values))
    while len(values) > 1 and values[-1] == 0:
        values.pop()
    return tuple(values)


def poly_add(left, right):
    result = [Fraction(0)] * max(len(left), len(right))
    for index, value in enumerate(left):
        result[index] += value
    for index, value in enumerate(right):
        result[index] += value
    return poly_trim(result)


def poly_neg(poly):
    return tuple(-value for value in poly)


def poly_mul(left, right):
    result = [Fraction(0)] * (len(left) + len(right) - 1)
    for first, x in enumerate(left):
        for second, y in enumerate(right):
            result[first + second] += x * y
    return poly_trim(result)


def poly_sum(polys):
    result = (Fraction(0),)
    for poly in polys:
        result = poly_add(result, poly)
    return result


def poly_eval(poly, value):
    value = Fraction(value)
    result = Fraction(0)
    for coefficient in reversed(poly):
        result = result * value + coefficient
    return result


def poly_derivative(poly):
    if len(poly) == 1:
        return (Fraction(0),)
    return poly_trim(index * poly[index] for index in range(1, len(poly)))


def poly_determinant(matrix):
    """Recursive determinant over Q[t], for orders at most four."""
    if not matrix:
        return (Fraction(1),)
    result = (Fraction(0),)
    for column, entry in enumerate(matrix[0]):
        minor = [row[:column] + row[column + 1 :] for row in matrix[1:]]
        term = poly_mul(entry, poly_determinant(minor))
        result = poly_add(result, term if not column & 1 else poly_neg(term))
    return poly_trim(result)


def bernstein_coefficients(poly):
    """Power-to-Bernstein conversion on [0,1], in the actual degree."""
    degree = len(poly) - 1
    return tuple(
        sum(
            poly[power] * Fraction(comb(index, power), comb(degree, power))
            for power in range(index + 1)
        )
        for index in range(degree + 1)
    )


def certify_bernstein_sign(poly, desired):
    coefficients = bernstein_coefficients(poly)
    if desired not in (-1, 1):
        raise AssertionError("desired sign must be +/-1")
    if not all(desired * value > 0 for value in coefficients):
        raise AssertionError(
            f"Bernstein sign certificate failed: desired={desired}, "
            f"signs={[sign(value) for value in coefficients]}"
        )


def sign(value):
    if value == 0:
        return 0
    return 1 if value > 0 else -1


def segment_matrix(left, right):
    return [
        [
            poly_trim((left[row][column], right[row][column] - left[row][column]))
            for column in range(8)
        ]
        for row in range(4)
    ]


def derived_normal_polynomials(matrix):
    normals = []
    for triple in koszul.TRIPLES:
        columns = [
            [matrix[row][label - 1] for label in triple]
            for row in range(4)
        ]
        normal = []
        for coordinate in range(4):
            minor = [
                row
                for row_index, row in enumerate(columns)
                if row_index != coordinate
            ]
            determinant = poly_determinant(minor)
            factor = (-1) ** (coordinate + 5)
            normal.append(tuple(factor * value for value in determinant))
        normals.append(tuple(normal))
    return tuple(normals)


def transform_signature(signature):
    transformed = 0
    for index, triple in enumerate(koszul.TRIPLES):
        triple_sign = 1 if (int(signature) >> index) & 1 else -1
        for label in triple:
            triple_sign *= COLUMN_REORIENTATION[label - 1]
        if triple_sign > 0:
            transformed |= 1 << index
    return transformed


def signed_poly_columns(normals, signature, support):
    return tuple(
        tuple(
            coordinate
            if (signature >> index) & 1
            else poly_neg(coordinate)
            for coordinate in normals[index]
        )
        for index in support
    )


def five_circuit_cofactors(normals, signature, support):
    if len(support) != 5:
        raise AssertionError("five-circuit support required")
    columns = signed_poly_columns(normals, signature, support)
    cofactors = []
    for omitted in range(5):
        retained = [column for index, column in enumerate(columns) if index != omitted]
        determinant = poly_determinant([
            [retained[column][row] for column in range(4)]
            for row in range(4)
        ])
        cofactors.append(determinant if not omitted & 1 else poly_neg(determinant))
    return tuple(cofactors)


def four_circuit_cofactors(normals, signature, support, deleted_row=0):
    if len(support) != 4:
        raise AssertionError("four-circuit support required")
    columns = signed_poly_columns(normals, signature, support)
    rows = [row for row in range(4) if row != deleted_row]
    cofactors = []
    for omitted in range(4):
        retained = [column for index, column in enumerate(columns) if index != omitted]
        determinant = poly_determinant([
            [retained[column][row] for column in range(3)]
            for row in rows
        ])
        cofactors.append(determinant if not omitted & 1 else poly_neg(determinant))
    return tuple(cofactors)


def verify_polynomial_kernel(normals, signature, support, coefficients):
    columns = signed_poly_columns(normals, signature, support)
    for row in range(4):
        residual = poly_sum(
            poly_mul(coefficient, column[row])
            for coefficient, column in zip(coefficients, columns, strict=True)
        )
        if residual != (Fraction(0),):
            raise AssertionError("cofactor vector fails the polynomial kernel equation")


def evaluate_normals(normals, parameter):
    return tuple(
        tuple(poly_eval(coordinate, parameter) for coordinate in normal)
        for normal in normals
    )


def positive_minimal_circuits(normals, signature, universe):
    """Enumerate positive circuits of sizes 2--5 in a six-normal restriction."""
    result = []
    for size in range(2, 6):
        for support in combinations(universe, size):
            columns = pivot.signed_columns(normals, signature, support)
            if koszul.matrix_rank(columns) != size - 1:
                continue
            for rows in combinations(range(4), size - 1):
                square = [
                    [columns[column][row] for column in range(size)]
                    for row in rows
                ]
                if koszul.matrix_rank(square) != size - 1:
                    continue
                cofactors = []
                for omitted in range(size):
                    minor = [
                        row[:omitted] + row[omitted + 1 :]
                        for row in square
                    ]
                    determinant = koszul.determinant(minor)
                    cofactors.append(
                        determinant if not omitted & 1 else -determinant
                    )
                if all(value > 0 for value in cofactors) or all(
                    value < 0 for value in cofactors
                ):
                    result.append(support)
                break
    return tuple(result)


def verify_parent_segment(original, left, right):
    original_signs = tuple(map(sign, free_log.original_bracket_values(original)))
    left_values = free_log.bracket_values(left)
    right_values = free_log.bracket_values(right)
    left_signs = tuple(map(sign, left_values))
    right_signs = tuple(map(sign, right_values))
    if 0 in original_signs or 0 in left_signs or right_signs != left_signs:
        raise AssertionError("segment endpoints are not in the same normalized parent cell")

    differences = [
        (row, column)
        for row in range(4)
        for column in range(8)
        if left[row][column] != right[row][column]
    ]
    if {column for _, column in differences} != {6} or len(differences) != 3:
        raise AssertionError("the exact path must move only projective column 7")

    # Every parent bracket is constant or affine in the moving column.  Its
    # two endpoint values have the same strict sign, so their convex
    # interpolation has that sign throughout the closed interval.
    for first, second in zip(left_values, right_values, strict=True):
        if not first or sign(first) != sign(second):
            raise AssertionError("a parent affine determinant can cross zero")

    # Independently verify the claimed column reorientation against all 70
    # brackets of the source chart.
    for basis, source, gauged in zip(
        free_log.BRACKETS,
        free_log.original_bracket_values(original),
        left_values,
        strict=True,
    ):
        expected = 1
        for zero_based_label in basis:
            expected *= COLUMN_REORIENTATION[zero_based_label]
        if sign(gauged) != expected * sign(source):
            raise AssertionError("wrong projective-frame reorientation")


def verify_persistent_triple(normals, signatures, supports):
    r0 = five_circuit_cofactors(normals, signatures[0], supports["R0"])
    r4 = five_circuit_cofactors(normals, signatures[4], supports["R4"])
    c3 = four_circuit_cofactors(normals, signatures[3], supports["C3"])

    for coefficient in r0 + r4:
        certify_bernstein_sign(coefficient, -1)
    for coefficient in c3:
        certify_bernstein_sign(coefficient, 1)

    verify_polynomial_kernel(normals, signatures[0], supports["R0"], r0)
    verify_polynomial_kernel(normals, signatures[4], supports["R4"], r4)

    # The three-row cofactor formula gives a relation in coordinates 2,3,4.
    # The structural four-normal determinant vanishes identically, and the
    # exact residual check upgrades it to a relation in all four coordinates.
    c3_columns = signed_poly_columns(normals, signatures[3], supports["C3"])
    full_determinant = poly_determinant([
        [c3_columns[column][row] for column in range(4)]
        for row in range(4)
    ])
    if full_determinant != (Fraction(0),):
        raise AssertionError("C3 is not a structural four-normal dependence")
    verify_polynomial_kernel(normals, signatures[3], supports["C3"], c3)

    degrees, fixed_partner = pivot.union_statistics(
        (supports["R0"], supports["R4"], supports["C3"])
    )
    if degrees != EXPECTED_ESCAPE_DEGREES or fixed_partner:
        raise AssertionError("wrong persistent triple support statistics")
    incident = {
        pivot.name(index)
        for support in (supports["R0"], supports["R4"], supports["C3"])
        for index in support
        if 1 in koszul.TRIPLES[index]
    }
    if incident != {"134", "127"}:
        raise AssertionError("label 1 is not confined to the certified pencil")


def verify_cube_connection(normals, signatures, supports):
    evaluated = evaluate_normals(normals, Fraction(0))
    for bit in pivot.BITS:
        for tag in (f"Q{bit}", f"R{bit}"):
            support = supports[tag]
            columns = pivot.signed_columns(evaluated, signatures[bit], support)
            if koszul.matrix_rank(columns) != 4:
                raise AssertionError(f"{tag} is not a rank-four five-circuit")
            raw = five_circuit_cofactors(normals, signatures[bit], support)
            endpoint = tuple(poly_eval(value, 0) for value in raw)
            if not (all(value > 0 for value in endpoint) or all(value < 0 for value in endpoint)):
                raise AssertionError(f"{tag} is not positive at the cube chart")

    c3 = four_circuit_cofactors(normals, signatures[3], supports["C3"])
    if not all(poly_eval(value, 0) > 0 for value in c3):
        raise AssertionError("C3 is not in the third block at the cube chart")

    # Convexity of each normalized Gordan polytope connects the original
    # Q0/Q4/Q3 corner, every point of its Q/R product cube, and the persistent
    # R0/R4/C3 witness tuple.  These incidence checks ensure that the named
    # Q/R pairs really are the audited product edges.
    for bit in pivot.BITS:
        q_support = supports[f"Q{bit}"]
        r_support = supports[f"R{bit}"]
        if len(set(q_support) & set(r_support)) != 4:
            raise AssertionError("a named Q/R pair is not a one-exchange edge")
        union = tuple(sorted(set(q_support) | set(r_support)))
        columns = pivot.signed_columns(evaluated, signatures[bit], union)
        if (len(union), koszul.matrix_rank(columns)) != (6, 4):
            raise AssertionError("a named Q/R face is not one-dimensional")


def verify_bit4_wall(normals, signatures, supports):
    q = five_circuit_cofactors(normals, signatures[4], supports["Q4"])
    r = five_circuit_cofactors(normals, signatures[4], supports["R4"])
    s = five_circuit_cofactors(normals, signatures[4], supports["S4"])

    q_names = [pivot.name(index) for index in supports["Q4"]]
    s_names = [pivot.name(index) for index in supports["S4"]]
    q_changing = q_names.index("127")
    s_changing = s_names.index("134")
    discriminant = q[q_changing]

    if s[s_changing] != poly_neg(discriminant):
        raise AssertionError("Q4 and S4 do not share the same support-drop wall")
    for index, coefficient in enumerate(q):
        if index != q_changing:
            certify_bernstein_sign(coefficient, -1)
    for index, coefficient in enumerate(s):
        if index != s_changing:
            certify_bernstein_sign(coefficient, -1)
    for coefficient in r:
        certify_bernstein_sign(coefficient, -1)

    certify_bernstein_sign(poly_derivative(discriminant), 1)
    if not (
        poly_eval(discriminant, Fraction(1, 3)) < 0
        < poly_eval(discriminant, Fraction(3, 8))
    ):
        raise AssertionError("the unique orbit-50 root lacks its rational bracket")

    p_support = supports["P"]
    if tuple(index for index in supports["Q4"] if pivot.name(index) != "127") != p_support:
        raise AssertionError("Q4 does not drop to the claimed four-circuit")
    if tuple(index for index in supports["S4"] if pivot.name(index) != "134") != p_support:
        raise AssertionError("S4 is not born from the same four-circuit")
    if koszul.wall_orbit(p_support) != 50 or koszul.orbit_kind(50) != "residual":
        raise AssertionError("the crossing is not residual wall orbit 50")

    # The restricted positive kernel has exactly the advertised two circuit
    # rays on either side.  At the wall the Q/S ray limits to P while the R
    # ray remains strict, so its normalized face remains a closed interval.
    universe = supports["BIT4_UNION"]
    before = positive_minimal_circuits(
        evaluate_normals(normals, Fraction(0)), signatures[4], universe
    )
    after = positive_minimal_circuits(
        evaluate_normals(normals, Fraction(1)), signatures[4], universe
    )
    if set(before) != {supports["Q4"], supports["R4"]}:
        raise AssertionError("wrong pre-wall positive rays")
    if set(after) != {supports["S4"], supports["R4"]}:
        raise AssertionError("wrong post-wall positive rays")

    return discriminant


def main():
    shatter = np.load(SHATTER, allow_pickle=False)
    upper = np.load(UPPER, allow_pickle=False)
    if int(shatter["parent_index"].item()) != 2599 or int(upper["parent_index"].item()) != 2599:
        raise AssertionError("wrong parent certificate")

    original = shatter["pattern_chart"][0]
    left = free_log.gauge_matrix(free_log.free_coordinates(original))
    upper_gauge = free_log.gauge_matrix(
        free_log.free_coordinates(upper["chart_matrix"][UPPER_CHART])
    )
    right = tuple(
        tuple(
            upper_gauge[row][column] if column == 6 else left[row][column]
            for column in range(8)
        )
        for row in range(4)
    )
    verify_parent_segment(original, left, right)

    signatures = {
        bit: transform_signature(int(shatter["signature"][bit]))
        for bit in pivot.BITS
    }
    supports = {
        **{f"Q{bit}": pivot.indices(Q_NAMES[bit]) for bit in pivot.BITS},
        **{f"R{bit}": pivot.indices(R_NAMES[bit]) for bit in pivot.BITS},
        "C3": pivot.indices(C3_NAMES),
        "S4": pivot.indices(S4_NAMES),
        "P": pivot.indices(P_NAMES),
        "BIT4_UNION": pivot.indices(BIT4_UNION_NAMES),
    }
    for bit in pivot.BITS:
        stored = pivot.stored_support(shatter, bit)
        if supports[f"Q{bit}"] != stored:
            raise AssertionError("stored hard-triple support changed")

    matrix = segment_matrix(left, right)
    normals = derived_normal_polynomials(matrix)
    verify_cube_connection(normals, signatures, supports)
    verify_persistent_triple(normals, signatures, supports)
    discriminant = verify_bit4_wall(normals, signatures, supports)

    print("PASS: the exact one-column segment stays in parent cell 2599")
    print("PASS: R0/R4/C3 stay strict positive circuits for every 0<=t<=1")
    print("PASS: the hard Q/R product cube connects to that persistent triple")
    print("PASS: orbit-50 has one root rho in (1/3,3/8)")
    print("PASS: Q4--R4 becomes P--R4 and then S4--R4 across rho")
    print("PASS: zero weights at P are retained by the closed witness face")
    print("PASS: persistent support degrees=" + str(EXPECTED_ESCAPE_DEGREES))
    print("PASS: label 1 sees only 134/127, so the pencil escape persists")
    print(
        "orbit-50 endpoint signs="
        + str((sign(poly_eval(discriminant, 0)), sign(poly_eval(discriminant, 1))))
    )
    print("NOTE: this certifies one local component reroute, not diagonal s=3")


if __name__ == "__main__":
    main()
