#!/usr/bin/env python3
"""Exact defect-two obstruction and pointwise escape for diagonal two.

The earlier row-2599 sample made every stored pencil-rigid positive pair look
"one-defect": some label e had a partner f in all but one of the support
triples through e.  Such a condition would make a one-parameter shear/boundary
pivot attractive.  This verifier proves that the condition is not forced by
extension compatibility, properness, or incomparability.

For catalog parent 16 it checks two five-support positive circuits whose union
is pencil-rigid and has minimum partner defect exactly two.  It checks exact
integer realizations of both extension signatures, and exact positive Gordan
circuits excluding the other signature on each realization.  Thus the two
feasibility regions are proper and incomparable.

The same exact example also has a pointwise escape: along y_1 -> y_1+t y_4,
both displayed positive circuits persist until the parent bracket [1678]
vanishes at t=399/2456.  This proves that the exhibited chart is not trapped;
it does not prove that the whole closed pair intersection has no compact
component and does not prove the second diagonal.

Only integer/rational arithmetic is used.
"""

from fractions import Fraction
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import four_chart_gate as gate  # noqa: E402
import prototype_koszul_circuits as koszul  # noqa: E402


PARENT_INDEX = 16
LEFT_SIGNATURE = 26988370886400909
RIGHT_SIGNATURE = 45348283816043521

PARENT = (
    (8, 4, -3, -6, 1, 0, 8, 1),
    (1, 8, 8, 1, 2, -5, -1, -3),
    (3, -1, 5, -2, -8, 5, -1, -8),
    (-1, -1, 0, 8, 2, 8, 4, 5),
)

LEFT_SUPPORT_TEXT = "123/124/134/235/567"
RIGHT_SUPPORT_TEXT = "126/247/158/468/378"

# Each 4-by-9 matrix realizes one child.  Its first eight columns give a
# parent chart on which the other signature has the displayed bad circuit.
LEFT_CHILD = (
    (32, -12, -7, 11, -32, 32, 12, -3, -11),
    (18, 29, 32, 9, -6, 3, -4, -16, 6),
    (-25, -32, 1, -5, -30, 3, -16, -11, 8),
    (-24, -4, 5, 32, 7, 17, 1, 6, 32),
)
RIGHT_BAD_AT_LEFT_TEXT = "124/125/457/148/378"

RIGHT_CHILD = (
    (-1765, -365, -944, -363, 4096, -2048, -1745, 2048, -4096),
    (-251, -1329, -1024, 1509, 1591, 1254, 4096, 1360, 2694),
    (-4096, -907, 414, 4096, -827, 1335, -326, -250, -3700),
    (1820, 4096, 923, 1211, 3383, 305, 3460, 1173, -2605),
)
LEFT_BAD_AT_RIGHT_TEXT = "137/567/238/358/478"

EXPECTED_LEFT_WALL_TYPES = (37, 22, 22, 12, 10)
EXPECTED_RIGHT_WALL_TYPES = (47, 47, 49, 51, 49)
ESCAPE_TIME = Fraction(399, 2456)
MATCHING_STAR_ESCAPE_TIME = Fraction(217, 1966)


def parse_support(text):
    return tuple(
        koszul.TRIPLE_INDEX[tuple(int(character) for character in label)]
        for label in text.split("/")
    )


LEFT_SUPPORT = parse_support(LEFT_SUPPORT_TEXT)
RIGHT_SUPPORT = parse_support(RIGHT_SUPPORT_TEXT)
RIGHT_BAD_AT_LEFT = parse_support(RIGHT_BAD_AT_LEFT_TEXT)
LEFT_BAD_AT_RIGHT = parse_support(LEFT_BAD_AT_RIGHT_TEXT)


def matrix_columns(matrix, indices):
    return [[matrix[row][column] for column in indices] for row in range(4)]


def parent_brackets(matrix):
    return tuple(
        koszul.determinant(matrix_columns(matrix, basis))
        for one_based_basis in gate.colex_subsets(8, 4)
        for basis in (tuple(index - 1 for index in one_based_basis),)
    )


def parent_sign_string(matrix):
    values = parent_brackets(matrix)
    if not all(values):
        raise AssertionError("parent matrix is nonuniform")
    return "".join("+" if value > 0 else "-" for value in values)


def normals(matrix):
    result = []
    for triple in koszul.TRIPLES:
        columns = [[matrix[row][index - 1] for index in triple] for row in range(4)]
        result.append(
            tuple(
                (-1) ** (coordinate + 5)
                * koszul.determinant(
                    [
                        columns[row]
                        for row in range(4)
                        if row != coordinate
                    ]
                )
                for coordinate in range(4)
            )
        )
    return tuple(result)


def signed_columns(matrix, signature, support):
    parent_normals = normals(matrix)
    return tuple(
        tuple(
            value if (signature >> index) & 1 else -value
            for value in parent_normals[index]
        )
        for index in support
    )


def positive_circuit(matrix, signature, support):
    columns = signed_columns(matrix, signature, support)
    if len(columns) != 5 or koszul.matrix_rank(columns) != 4:
        raise AssertionError("support is not a rank-four five-circuit")
    cofactors = [
        (-1) ** omitted
        * koszul.determinant(
            [columns[index] for index in range(5) if index != omitted]
        )
        for omitted in range(5)
    ]
    if all(value < 0 for value in cofactors):
        cofactors = [-value for value in cofactors]
    if not all(value > 0 for value in cofactors):
        raise AssertionError(f"circuit is not positive: {cofactors}")
    for coordinate in range(4):
        if sum(
            weight * column[coordinate]
            for weight, column in zip(cofactors, columns, strict=True)
        ):
            raise AssertionError("alternating cofactors do not annihilate support")
    return tuple(cofactors)


def extension_signature(parent, point):
    values = [
        sum(a * x for a, x in zip(row, point, strict=True))
        for row in normals(parent)
    ]
    if not all(values):
        raise AssertionError("extension point is nonuniform")
    return sum(1 << index for index, value in enumerate(values) if value > 0)


def partner_defect(support_union):
    return min(
        sum(
            label in koszul.TRIPLES[index]
            and partner not in koszul.TRIPLES[index]
            for index in support_union
        )
        for label in range(1, 9)
        for partner in range(1, 9)
        if label != partner
    )


def pencil_rigid(support_union):
    for label in range(1, 9):
        incident = [
            set(koszul.TRIPLES[index])
            for index in support_union
            if label in koszul.TRIPLES[index]
        ]
        if len(incident) < 3:
            return False
        if set.intersection(*(triple - {label} for triple in incident)):
            return False
    return True


def matching_star_labels(support_union):
    """Return degree-three labels whose six partners are all distinct."""
    result = []
    for label in range(1, 9):
        incident = [
            koszul.TRIPLES[index]
            for index in support_union
            if label in koszul.TRIPLES[index]
        ]
        if len(incident) != 3:
            continue
        partners = [
            partner
            for triple in incident
            for partner in triple
            if partner != label
        ]
        if len(set(partners)) == 6:
            result.append(label)
    return tuple(result)


def verify_matching_star_dichotomy():
    """Exhaust the only arithmetic cases in the universal dichotomy.

    A union of at most ten triples has total degree at most 30.  If all eight
    degrees are at least three, they cannot all be at least four, so a
    degree-three label exists.  Its three triples contribute six partner
    occurrences in seven bins.  The enumeration below checks every unordered
    distribution of those six occurrences: the best partner gives defect at
    most two, and equality occurs exactly when all six partners are distinct.
    Pencil rigidity separately rules out defect zero.
    """
    if 8 * 4 <= 3 * 10:
        raise AssertionError("degree count no longer forces a degree-three label")

    for occurrences in combinations_with_replacement(range(7), 6):
        multiplicities = tuple(occurrences.count(partner) for partner in range(7))
        best_multiplicity = max(multiplicities)
        defect = 3 - best_multiplicity
        if defect > 2:
            raise AssertionError("six occurrences in seven bins have defect above two")
        if defect == 2 and sorted(multiplicities) != [0, 1, 1, 1, 1, 1, 1]:
            raise AssertionError("defect two is not the matching-star distribution")


def verify_star_membership_and_small_union_cases():
    """Exhaust the shared/unique membership arithmetic at a matching star."""
    observed = set()
    # A matching star has three distinct union triples.  Split them into
    # Q-only, R-only, and shared triples.  Pencil rigidity gives |Q union R|
    # at least eight, so two five-sets share at most two triples.
    for shared in range(3):
        for left_only in range(4 - shared):
            right_only = 3 - shared - left_only
            observed.add((shared, left_only + shared, right_only + shared))
    expected = {
        (0, 0, 3),
        (0, 1, 2),
        (0, 2, 1),
        (0, 3, 0),
        (1, 1, 3),
        (1, 2, 2),
        (1, 3, 1),
        (2, 2, 3),
        (2, 3, 2),
    }
    if observed != expected:
        raise AssertionError("wrong matching-star support-membership table")

    # With eight distinct union triples the total degree is exactly 24, so
    # minimum degree three forces every label to have degree three.
    if 3 * 8 != 8 * 3:
        raise AssertionError("eight-edge degree count failed")

    # With nine union triples the total surplus above degree three is three.
    # Exhaust its distributions: there are at most three high-degree labels,
    # so an edge whose deletion preserves minimum degree three is, if it
    # exists, the unique triple on exactly those three labels.
    surplus_distributions = [
        values
        for values in product(range(4), repeat=8)
        if sum(values) == 3
    ]
    if not surplus_distributions:
        raise AssertionError("missing nine-edge degree distributions")
    for values in surplus_distributions:
        high = {index for index, value in enumerate(values) if value}
        if len(high) > 3:
            raise AssertionError("nine edges have more than three high-degree labels")
        deletion_safe_triples = [
            triple
            for triple in combinations(range(8), 3)
            if set(triple) <= high
        ]
        if len(deletion_safe_triples) > 1:
            raise AssertionError("nine edges have multiple rigid-deletable triples")


def child_check(child, signature, expected_parent):
    parent = tuple(tuple(row[:8]) for row in child)
    point = tuple(row[8] for row in child)
    if parent_sign_string(parent) != expected_parent:
        raise AssertionError("child realization has the wrong parent")
    if extension_signature(parent, point) != signature:
        raise AssertionError("child realization has the wrong extension")
    return parent


def shear_parent(parameter):
    result = [list(map(Fraction, row)) for row in PARENT]
    # y_1 -> y_1 + t y_4 (labels are one-based in the statement).
    for coordinate in range(4):
        result[coordinate][0] += parameter * Fraction(PARENT[coordinate][3])
    return tuple(tuple(row) for row in result)


def fixed_orientation_cofactors(parameter, signature, support, orientation):
    columns = signed_columns(shear_parent(parameter), signature, support)
    return tuple(
        orientation
        * (-1) ** omitted
        * koszul.determinant(
            [columns[index] for index in range(5) if index != omitted]
        )
        for omitted in range(5)
    )


def matching_star_parent(parameter):
    """The genuine partner shear y_8 -> y_8 + t y_1."""
    result = [list(map(Fraction, row)) for row in PARENT]
    for coordinate in range(4):
        result[coordinate][7] += parameter * Fraction(PARENT[coordinate][0])
    return tuple(tuple(row) for row in result)


def matching_star_cofactors(parameter, signature, support, orientation):
    columns = signed_columns(matching_star_parent(parameter), signature, support)
    return tuple(
        orientation
        * (-1) ** omitted
        * koszul.determinant(
            [columns[index] for index in range(5) if index != omitted]
        )
        for omitted in range(5)
    )


def quadratic_coefficients(values):
    """Interpolate a degree-at-most-two polynomial at 0,1,2."""
    constant = values[0]
    quadratic = (values[2] - 2 * values[1] + values[0]) / 2
    linear = values[1] - constant - quadratic
    return constant, linear, quadratic


def evaluate_quadratic(polynomial, parameter):
    constant, linear, quadratic = polynomial
    return constant + linear * parameter + quadratic * parameter * parameter


def positive_quadratic_on_interval(polynomial, right):
    constant, linear, quadratic = polynomial
    candidates = [Fraction(0), right]
    if quadratic > 0:
        vertex = -linear / (2 * quadratic)
        if 0 < vertex < right:
            candidates.append(vertex)
    return all(evaluate_quadratic(polynomial, point) > 0 for point in candidates)


def verify_escape():
    start_brackets = parent_brackets(PARENT)
    end_parent = shear_parent(ESCAPE_TIME)
    end_brackets = parent_brackets(end_parent)
    bases = tuple(
        tuple(index - 1 for index in basis)
        for basis in gate.colex_subsets(8, 4)
    )
    zero_bases = tuple(basis for basis, value in zip(bases, end_brackets, strict=True) if not value)
    if zero_bases != ((0, 5, 6, 7),):
        raise AssertionError(f"wrong escape wall: {zero_bases}")
    for start, end in zip(start_brackets, end_brackets, strict=True):
        if end and (start > 0) != (end > 0):
            raise AssertionError("a parent bracket changes sign before the endpoint")

    for signature, support in (
        (LEFT_SIGNATURE, LEFT_SUPPORT),
        (RIGHT_SIGNATURE, RIGHT_SUPPORT),
    ):
        raw_start = fixed_orientation_cofactors(0, signature, support, 1)
        if all(value > 0 for value in raw_start):
            orientation = 1
        elif all(value < 0 for value in raw_start):
            orientation = -1
        else:
            raise AssertionError("initial support is not positive")
        samples = [
            fixed_orientation_cofactors(Fraction(point), signature, support, orientation)
            for point in range(5)
        ]
        for coordinate in range(5):
            polynomial = quadratic_coefficients(
                [samples[point][coordinate] for point in range(3)]
            )
            if any(
                evaluate_quadratic(polynomial, Fraction(point))
                != samples[point][coordinate]
                for point in range(3, 5)
            ):
                raise AssertionError("a shear cofactor has degree greater than two")
            if not positive_quadratic_on_interval(polynomial, ESCAPE_TIME):
                raise AssertionError("a positive circuit is lost before the parent wall")


def verify_matching_star_escape():
    """Certify a partner ray at the genuine matching star label 8."""
    start_brackets = parent_brackets(PARENT)
    end_brackets = parent_brackets(
        matching_star_parent(MATCHING_STAR_ESCAPE_TIME)
    )
    bases = tuple(
        tuple(index - 1 for index in basis)
        for basis in gate.colex_subsets(8, 4)
    )
    zero_bases = tuple(
        basis for basis, value in zip(bases, end_brackets, strict=True) if not value
    )
    if zero_bases != ((1, 2, 3, 7),):
        raise AssertionError(f"wrong matching-star escape wall: {zero_bases}")
    for start, end in zip(start_brackets, end_brackets, strict=True):
        if end and (start > 0) != (end > 0):
            raise AssertionError("a parent bracket changes before the matching-star wall")

    for signature, support in (
        (LEFT_SIGNATURE, LEFT_SUPPORT),
        (RIGHT_SIGNATURE, RIGHT_SUPPORT),
    ):
        raw_start = matching_star_cofactors(0, signature, support, 1)
        if all(value > 0 for value in raw_start):
            orientation = 1
        elif all(value < 0 for value in raw_start):
            orientation = -1
        else:
            raise AssertionError("initial support is not positive")
        samples = [
            matching_star_cofactors(
                Fraction(point), signature, support, orientation
            )
            for point in range(5)
        ]
        for coordinate in range(5):
            polynomial = quadratic_coefficients(
                [samples[point][coordinate] for point in range(3)]
            )
            if any(
                evaluate_quadratic(polynomial, Fraction(point))
                != samples[point][coordinate]
                for point in range(3, 5)
            ):
                raise AssertionError("a matching-star cofactor has degree above two")
            if not positive_quadratic_on_interval(
                polynomial, MATCHING_STAR_ESCAPE_TIME
            ):
                raise AssertionError("a circuit is lost before the matching-star wall")


def main():
    verify_matching_star_dichotomy()
    verify_star_membership_and_small_union_cases()

    catalog = [
        line.strip()
        for line in gate.CATALOG_48.open(encoding="utf-8")
        if line.strip()
    ]
    expected_parent = catalog[PARENT_INDEX]
    if parent_sign_string(PARENT) != expected_parent:
        raise AssertionError("base matrix does not realize catalog parent 16")

    union = set(LEFT_SUPPORT) | set(RIGHT_SUPPORT)
    if len(union) != 10 or not pencil_rigid(union):
        raise AssertionError("support union is not a ten-edge pencil-rigid union")
    if partner_defect(union) != 2:
        raise AssertionError("minimum partner defect is not exactly two")
    stars = matching_star_labels(union)
    degrees = tuple(
        sum(label in koszul.TRIPLES[index] for index in union)
        for label in range(1, 9)
    )
    if degrees != (5, 5, 4, 4, 3, 3, 3, 3) or stars != (5, 6, 7, 8):
        raise AssertionError("the defect-two residue is not the matching-star case")

    left_types = tuple(
        koszul.wall_orbit(tuple(LEFT_SUPPORT[index] for index in range(5) if index != omitted))
        for omitted in range(5)
    )
    right_types = tuple(
        koszul.wall_orbit(tuple(RIGHT_SUPPORT[index] for index in range(5) if index != omitted))
        for omitted in range(5)
    )
    if left_types != EXPECTED_LEFT_WALL_TYPES or right_types != EXPECTED_RIGHT_WALL_TYPES:
        raise AssertionError("wrong derived-wall types")
    if not (set(left_types) & koszul.RESIDUAL and set(right_types) & koszul.RESIDUAL):
        raise AssertionError("a support does not pass the universal residual filter")

    positive_circuit(PARENT, LEFT_SIGNATURE, LEFT_SUPPORT)
    positive_circuit(PARENT, RIGHT_SIGNATURE, RIGHT_SUPPORT)

    left_parent = child_check(LEFT_CHILD, LEFT_SIGNATURE, expected_parent)
    right_parent = child_check(RIGHT_CHILD, RIGHT_SIGNATURE, expected_parent)
    positive_circuit(left_parent, RIGHT_SIGNATURE, RIGHT_BAD_AT_LEFT)
    positive_circuit(right_parent, LEFT_SIGNATURE, LEFT_BAD_AT_RIGHT)

    verify_escape()
    verify_matching_star_escape()

    print("PASS degree counting proves every pencil-rigid 5+5 union has d in {1,2}")
    print("PASS exhaustive partner distributions prove d=2 is exactly a matching star")
    print("PASS shared-star membership and the eight/nine-edge boundary cases are exhausted")
    print("PASS parent 16 has an exact positive 5+5 pencil-rigid pair")
    print("PASS its union has minimum partner defect exactly two")
    print("PASS both supports pass the residual-cofactor signed filter")
    print("PASS exact child matrices prove both signatures realizable")
    print("PASS reciprocal exact Gordan circuits prove properness and incomparability")
    print("PASS y1 -> y1+t*y4 preserves both circuits for 0 <= t <= 399/2456")
    print("PASS matching-star y8 -> y8+t*y1 reaches [2348]=0 at t=217/1966")
    print("THEOREM: one-defect is not forced by the full second-diagonal hypotheses")
    print("CAVEAT: the exhibited point escapes; the global second diagonal remains open")


if __name__ == "__main__":
    main()
