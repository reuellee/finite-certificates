#!/usr/bin/env python3
"""Exact no-go certificate for the root-free matching-star shear proof.

For a realizable UOM(4,8) parent and a proper incomparable pair of realizable
extensions, this verifier checks a positive pencil-rigid 5+5 circuit pair with
matching-star label 3.  Its *global* partner defect is one, so it is not the
hard defect-two residue.  Along each of the six partner lines at label 3

    y_3(t) = y_3 + t y_f,

both rays encounter a zero of one of the two chosen circuit cofactors before
the parent residence boundary.  The claim is deliberately about preserving
these two strict five-circuit witnesses without changing support, and shows
why the matching-star form must be paired with the global defect-two
hypothesis.  It is not a counterexample to 9DVL.

One ray is then followed to its exact first linear cofactor root.  There the
support 678 drops, the remaining union has degree two at label 6, and the
projective-plane-pencil lemma supplies a boundary escape.  Thus the example
also demonstrates why support changes must be retained.

Only exact integer and rational arithmetic is used.
"""

from fractions import Fraction
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import four_chart_gate as gate  # noqa: E402
import prototype_koszul_circuits as koszul  # noqa: E402
import verify_second_diagonal_defect_two as defect  # noqa: E402


LEFT_SIGNATURE = 14182253433415844
RIGHT_SIGNATURE = 4401715025916122

PARENT = (
    (3, -8, 0, 3, 14, -5, 13, -5),
    (-8, -13, 11, 12, 15, 0, 14, 8),
    (-10, -14, -2, 14, 9, -3, 1, -10),
    (-14, 3, 12, 15, 14, 12, -8, 11),
)

LEFT_SUPPORT_TEXT = "237/258/678/345/148"
RIGHT_SUPPORT_TEXT = "167/278/125/136/457"
EXPECTED_LEFT_WALL_TYPES = (47, 51, 49, 47, 49)
EXPECTED_RIGHT_WALL_TYPES = (50, 32, 39, 46, 32)

# The first child realizes LEFT_SIGNATURE, while RIGHT_SIGNATURE is bad on
# its first eight columns by RIGHT_BAD_AT_LEFT.  The second reverses the roles.
LEFT_CHILD = (
    (4, 21, -14, -32, -22, 6, -11, 32, 1),
    (-16, -12, 32, 2, -27, -1, -9, 29, 19),
    (11, 0, 21, -6, 23, -2, 32, 14, 32),
    (-6, 32, 9, 13, 32, 32, -17, -5, 9),
)
RIGHT_BAD_AT_LEFT_TEXT = "126/136/256/457/278"

RIGHT_CHILD = (
    (9, -32, 16, -3, 7, -17, 32, 21, 13),
    (-32, -22, -2, 4, -17, -8, -21, -2, 32),
    (-18, 22, 13, -9, -19, 25, -7, 32, -1),
    (24, 7, -9, -16, -32, -32, 2, 3, 2),
)
LEFT_BAD_AT_RIGHT_TEXT = "345/137/148/348/258"

# For each partner, these two interior residence parameters lie beyond a
# chosen cofactor root on the negative and positive ray respectively.  The
# named LEFT_SUPPORT cofactor is strictly negative there.
RAY_CERTIFICATES = {
    1: ((Fraction(-1, 10), "678"), (Fraction(1, 10), "258")),
    2: ((Fraction(-1, 50), "258"), (Fraction(1, 50), "678")),
    4: ((Fraction(-1, 10), "258"), (Fraction(1, 10), "678")),
    5: ((Fraction(-1, 20), "258"), (Fraction(1, 20), "678")),
    6: ((Fraction(-1, 20), "258"), (Fraction(1, 25), "678")),
    7: ((Fraction(-1, 50), "678"), (Fraction(1, 50), "258")),
}

# On the positive y_2 direction the 678 coefficient is linear and vanishes
# here.  This exact boundary face is pencil-flexible.
FLEXIBLE_ROOT = Fraction(124918901021, 12278662519200)


def parse_support(text):
    return tuple(
        koszul.TRIPLE_INDEX[tuple(int(character) for character in label)]
        for label in text.split("/")
    )


LEFT_SUPPORT = parse_support(LEFT_SUPPORT_TEXT)
RIGHT_SUPPORT = parse_support(RIGHT_SUPPORT_TEXT)
RIGHT_BAD_AT_LEFT = parse_support(RIGHT_BAD_AT_LEFT_TEXT)
LEFT_BAD_AT_RIGHT = parse_support(LEFT_BAD_AT_RIGHT_TEXT)


def shear_parent(partner, parameter):
    result = [list(map(Fraction, row)) for row in PARENT]
    for coordinate in range(4):
        result[coordinate][2] += parameter * Fraction(PARENT[coordinate][partner - 1])
    return tuple(tuple(row) for row in result)


def oriented_cofactors(matrix, signature, support, orientation):
    columns = defect.signed_columns(matrix, signature, support)
    return tuple(
        orientation
        * (-1) ** omitted
        * koszul.determinant(
            [columns[index] for index in range(5) if index != omitted]
        )
        for omitted in range(5)
    )


def positive_orientation(signature, support):
    raw = oriented_cofactors(PARENT, signature, support, 1)
    if all(value > 0 for value in raw):
        return 1
    if all(value < 0 for value in raw):
        return -1
    raise AssertionError("base support is not a strict positive circuit")


def same_parent_residence(parameter, partner, start_brackets):
    matrix = shear_parent(partner, parameter)
    values = defect.parent_brackets(matrix)
    if not all(values):
        return False
    return all((start > 0) == (value > 0) for start, value in zip(start_brackets, values, strict=True))


def degrees(support_union):
    return tuple(
        sum(label in koszul.TRIPLES[index] for index in support_union)
        for label in range(1, 9)
    )


def wall_types(support):
    return tuple(
        koszul.wall_orbit(
            tuple(support[index] for index in range(5) if index != omitted)
        )
        for omitted in range(5)
    )


def verify_ray_no_go():
    start_brackets = defect.parent_brackets(PARENT)
    left_orientation = positive_orientation(LEFT_SIGNATURE, LEFT_SUPPORT)
    right_orientation = positive_orientation(RIGHT_SIGNATURE, RIGHT_SUPPORT)
    left_labels = tuple("".join(map(str, koszul.TRIPLES[index])) for index in LEFT_SUPPORT)

    for partner, ray_data in RAY_CERTIFICATES.items():
        # Every parent bracket and every circuit cofactor has the asserted
        # degree because only one parent column moves.
        bracket_samples = [
            defect.parent_brackets(shear_parent(partner, Fraction(sample)))
            for sample in range(3)
        ]
        for coordinate in range(len(start_brackets)):
            if bracket_samples[2][coordinate] - 2 * bracket_samples[1][coordinate] + bracket_samples[0][coordinate]:
                raise AssertionError("a parent bracket is not affine on a partner shear")

        for signature, support, orientation in (
            (LEFT_SIGNATURE, LEFT_SUPPORT, left_orientation),
            (RIGHT_SIGNATURE, RIGHT_SUPPORT, right_orientation),
        ):
            samples = [
                oriented_cofactors(
                    shear_parent(partner, Fraction(sample)),
                    signature,
                    support,
                    orientation,
                )
                for sample in range(4)
            ]
            for coordinate in range(5):
                third_difference = (
                    samples[3][coordinate]
                    - 3 * samples[2][coordinate]
                    + 3 * samples[1][coordinate]
                    - samples[0][coordinate]
                )
                if third_difference:
                    raise AssertionError("a circuit cofactor has degree above two")

        for parameter, lost_label in ray_data:
            if not same_parent_residence(parameter, partner, start_brackets):
                raise AssertionError("a no-go sample is outside the parent residence")
            values = oriented_cofactors(
                shear_parent(partner, parameter),
                LEFT_SIGNATURE,
                LEFT_SUPPORT,
                left_orientation,
            )
            lost_index = left_labels.index(lost_label)
            if values[lost_index] >= 0:
                raise AssertionError("the certified circuit cofactor did not turn negative")


def verify_flexible_root():
    start_brackets = defect.parent_brackets(PARENT)
    if not same_parent_residence(FLEXIBLE_ROOT, 2, start_brackets):
        raise AssertionError("the support-change root is outside the parent residence")

    left_orientation = positive_orientation(LEFT_SIGNATURE, LEFT_SUPPORT)
    right_orientation = positive_orientation(RIGHT_SIGNATURE, RIGHT_SUPPORT)
    left_values = oriented_cofactors(
        shear_parent(2, FLEXIBLE_ROOT),
        LEFT_SIGNATURE,
        LEFT_SUPPORT,
        left_orientation,
    )
    right_values = oriented_cofactors(
        shear_parent(2, FLEXIBLE_ROOT),
        RIGHT_SIGNATURE,
        RIGHT_SUPPORT,
        right_orientation,
    )
    dropped = parse_support("678")[0]
    dropped_index = LEFT_SUPPORT.index(dropped)
    if left_values[dropped_index] != 0:
        raise AssertionError("the claimed 678 coefficient does not vanish")
    if not all(value > 0 for index, value in enumerate(left_values) if index != dropped_index):
        raise AssertionError("another left coefficient is nonpositive at the pivot")
    if not all(value > 0 for value in right_values):
        raise AssertionError("the right circuit is lost before the pivot")

    for signature, support, orientation, exceptional in (
        (LEFT_SIGNATURE, LEFT_SUPPORT, left_orientation, dropped_index),
        (RIGHT_SIGNATURE, RIGHT_SUPPORT, right_orientation, None),
    ):
        samples = [
            oriented_cofactors(
                shear_parent(2, Fraction(sample)),
                signature,
                support,
                orientation,
            )
            for sample in range(3)
        ]
        for coordinate in range(5):
            polynomial = defect.quadratic_coefficients(
                [samples[sample][coordinate] for sample in range(3)]
            )
            if coordinate == exceptional:
                if polynomial[2] or defect.evaluate_quadratic(polynomial, FLEXIBLE_ROOT):
                    raise AssertionError("the 678 pivot is not its claimed linear root")
            elif not defect.positive_quadratic_on_interval(polynomial, FLEXIBLE_ROOT):
                raise AssertionError("another circuit coefficient vanishes before the pivot")

    reduced_union = (set(LEFT_SUPPORT) - {dropped}) | set(RIGHT_SUPPORT)
    if degrees(reduced_union)[5] != 2 or defect.pencil_rigid(reduced_union):
        raise AssertionError("the pivot face is not pencil-flexible at label 6")


def main():
    expected_parent = defect.parent_sign_string(PARENT)
    if len(expected_parent) != 70:
        raise AssertionError("wrong parent chirotope length")

    union = set(LEFT_SUPPORT) | set(RIGHT_SUPPORT)
    if len(union) != 10 or not defect.pencil_rigid(union):
        raise AssertionError("the support pair is not pencil-rigid 5+5")
    if defect.partner_defect(union) != 1:
        raise AssertionError("the example should retain the global defect-one alternative")
    if defect.matching_star_labels(union) != (3,):
        raise AssertionError("label 3 is not the unique matching-star label")
    if degrees(union) != (4, 4, 3, 3, 4, 3, 5, 4):
        raise AssertionError("wrong support degree sequence")

    if wall_types(LEFT_SUPPORT) != EXPECTED_LEFT_WALL_TYPES:
        raise AssertionError("wrong left derived-wall types")
    if wall_types(RIGHT_SUPPORT) != EXPECTED_RIGHT_WALL_TYPES:
        raise AssertionError("wrong right derived-wall types")
    if not (set(EXPECTED_LEFT_WALL_TYPES) & koszul.RESIDUAL):
        raise AssertionError("left support does not pass the residual filter")
    if not (set(EXPECTED_RIGHT_WALL_TYPES) & koszul.RESIDUAL):
        raise AssertionError("right support does not pass the residual filter")

    defect.positive_circuit(PARENT, LEFT_SIGNATURE, LEFT_SUPPORT)
    defect.positive_circuit(PARENT, RIGHT_SIGNATURE, RIGHT_SUPPORT)

    left_parent = defect.child_check(LEFT_CHILD, LEFT_SIGNATURE, expected_parent)
    right_parent = defect.child_check(RIGHT_CHILD, RIGHT_SIGNATURE, expected_parent)
    defect.positive_circuit(left_parent, RIGHT_SIGNATURE, RIGHT_BAD_AT_LEFT)
    defect.positive_circuit(right_parent, LEFT_SIGNATURE, LEFT_BAD_AT_RIGHT)

    verify_ray_no_go()
    verify_flexible_root()

    print("PASS exact child matrices prove realizability, properness, and incomparability")
    print("PASS the defect-one union nevertheless has unique matching-star label 3")
    print("PASS all twelve partner rays lose a chosen cofactor inside the residence")
    print("PASS at t=124918901021/12278662519200 the 678 face is pencil-flexible")
    print("THEOREM: a local matching star alone does not force a root-free partner shear")
    print("CAVEAT: support change escapes this point; the second diagonal remains open")


if __name__ == "__main__":
    main()
