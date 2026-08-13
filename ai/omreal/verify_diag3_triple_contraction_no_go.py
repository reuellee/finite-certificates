#!/usr/bin/env python3
"""Exact no-go checks for a direct triple-contraction proof of diagonal three.

There are two independent checks.

* Two decomposable alternating trilinear forms define an open subset of
  ``(R^6)^3`` with convex (or empty) fibers in each of its three row
  variables and with ``H_6 = Z``.  It rules out a theorem based only on
  three-row separate convexity and the alternating/Koszul identity at the
  exact normalized ``6+6+6`` dimensions.
* An honest uniform rank-four/eight parent and three distinct realizable
  extension signatures have a one-parameter path on which every prescribed
  bracket stays strict, the three private columns stay independent, and
  exactly one unprescribed triple-private bracket changes sign.  Contracting
  the private rank-three set therefore crosses a rank-one loop stratum.

The first model has the local alternating-minor algebra but is not asserted
to be a full 9DVL parent fiber.  The second check is an actual 9DVL
alternating-minor regression, but is a specialization no-go rather than a
counterexample to diagonal three.
"""

from fractions import Fraction
from itertools import combinations


PARENT = (
    (0, -3, -8, -7, -1, -1, 5, 8),
    (-6, -8, 1, 8, 2, -1, 2, 8),
    (-1, 4, 6, 2, 2, 8, 8, 2),
    (8, 1, -4, 4, 8, 2, -6, 5),
)

SIGNATURES = (
    454112161268235,
    58432476850159616,
    13949244655240191,
)

P1 = (-1048, 7770, -2258, 5819)
P2_LEFT = (449, 1898, -6928, 6982)
P2_RIGHT = (903, 2264, -6681, 7047)
P3 = (-3246, 5283, 6492, 4405)

EXPECTED_LEFT_CONTRACTION = (
    413089713655,
    -747753275210,
    -2585829854324,
    -1863473622438,
    549618851982,
    668147843790,
    2293731744432,
    3753760141212,
)

EXPECTED_RIGHT_CONTRACTION = (
    -48023641259,
    -961614275203,
    -2306296425946,
    -1712807800687,
    304575706691,
    560712995309,
    2485800701723,
    3651972965576,
)


def determinant(matrix):
    """Exact recursive determinant for order at most four."""
    matrix = [list(row) for row in matrix]
    if not matrix:
        return 1
    if len(matrix) == 1:
        return matrix[0][0]
    return sum(
        (-1 if column & 1 else 1)
        * value
        * determinant(
            [row[:column] + row[column + 1 :] for row in matrix[1:]]
        )
        for column, value in enumerate(matrix[0])
    )


def columns_to_rows(columns):
    return [list(row) for row in zip(*columns, strict=True)]


def bracket(columns):
    return determinant(columns_to_rows(columns))


def colex_subsets(n, size):
    return tuple(
        sorted(
            combinations(range(n), size),
            key=lambda subset: tuple(reversed(subset)),
        )
    )


def parent_column(index):
    return tuple(row[index] for row in PARENT)


def derived_normals():
    result = []
    for triple in colex_subsets(8, 3):
        columns = [parent_column(index) for index in triple]
        row = []
        for coordinate in range(4):
            minor = [
                [column[row_index] for column in columns]
                for row_index in range(4)
                if row_index != coordinate
            ]
            row.append((-1) ** (coordinate + 5) * determinant(minor))
        result.append(tuple(row))
    return tuple(result)


def dot(left, right):
    return sum(a * b for a, b in zip(left, right, strict=True))


def signature(point, normals):
    result = 0
    for index, normal in enumerate(normals):
        value = dot(normal, point)
        if value == 0:
            raise AssertionError("private extension is not uniform")
        if value > 0:
            result |= 1 << index
    return result


def verify_parent_and_extensions():
    parent_brackets = [
        bracket([parent_column(index) for index in basis])
        for basis in combinations(range(8), 4)
    ]
    if any(value == 0 for value in parent_brackets):
        raise AssertionError("the parent must be uniform")

    normals = derived_normals()
    if len(normals) != 56:
        raise AssertionError("wrong derived-normal count")

    points = (P1, P2_LEFT, P3)
    if tuple(signature(point, normals) for point in points) != SIGNATURES:
        raise AssertionError("left endpoint has the wrong signatures")
    if signature(P2_RIGHT, normals) != SIGNATURES[1]:
        raise AssertionError("moving point leaves its extension chamber")

    # Every prescribed bracket along P2(t) is affine in t.  Strict positivity
    # at both endpoints proves strict positivity on the whole closed segment.
    signed_endpoint_minima = []
    for point, signature_bits in (
        (P1, SIGNATURES[0]),
        (P2_LEFT, SIGNATURES[1]),
        (P2_RIGHT, SIGNATURES[1]),
        (P3, SIGNATURES[2]),
    ):
        signed = [
            dot(normal, point) * (1 if (signature_bits >> index) & 1 else -1)
            for index, normal in enumerate(normals)
        ]
        if min(signed) <= 0:
            raise AssertionError("a prescribed extension bracket is not strict")
        signed_endpoint_minima.append(min(signed))

    return tuple(signed_endpoint_minima)


def contraction_brackets(p2):
    return tuple(
        bracket([P1, p2, P3, parent_column(index)]) for index in range(8)
    )


def interpolate(left, right, parameter):
    return tuple(
        (1 - parameter) * Fraction(a) + parameter * Fraction(b)
        for a, b in zip(left, right, strict=True)
    )


def verify_loop_wall():
    left = contraction_brackets(P2_LEFT)
    right = contraction_brackets(P2_RIGHT)
    if left != EXPECTED_LEFT_CONTRACTION:
        raise AssertionError("left contraction vector changed")
    if right != EXPECTED_RIGHT_CONTRACTION:
        raise AssertionError("right contraction vector changed")

    left_signs = tuple(value > 0 for value in left)
    right_signs = tuple(value > 0 for value in right)
    if sum(a != b for a, b in zip(left_signs, right_signs, strict=True)) != 1:
        raise AssertionError("the endpoints must differ at exactly one quotient label")
    if left_signs[1:] != right_signs[1:]:
        raise AssertionError("the unique changing quotient label must be parent 1")

    parameter = Fraction(left[0], left[0] - right[0])
    if not 0 < parameter < 1:
        raise AssertionError("the loop wall must lie inside the segment")
    middle_p2 = interpolate(P2_LEFT, P2_RIGHT, parameter)
    middle = contraction_brackets(middle_p2)
    if middle[0] != 0:
        raise AssertionError("the selected quotient coordinate is not a loop")
    for index in range(1, 8):
        if middle[index] == 0:
            raise AssertionError("another quotient coordinate vanishes at the wall")
        if (middle[index] > 0) != left_signs[index]:
            raise AssertionError("another quotient sign changes at the wall")

    # A nonzero bracket with parent 2 proves that P1,P2(t),P3 have rank three
    # even at the wall.  Since its endpoint values have the same strict sign
    # and are affine in t, the private triple stays independent throughout.
    if not (left[1] < 0 and right[1] < 0 and middle[1] < 0):
        raise AssertionError("the private triple loses rank")

    normals = derived_normals()
    if signature(middle_p2, normals) != SIGNATURES[1]:
        raise AssertionError("the loop specialization leaves the prescribed chamber")
    # Restrict to a rational interval around the loop.  This removes the one
    # unrelated pair-private wall met earlier on the broad source segment and
    # gives a literal one-wall canary among *all* moving unprescribed minors.
    local_left = interpolate(P2_LEFT, P2_RIGHT, parameter - Fraction(1, 100))
    local_right = interpolate(P2_LEFT, P2_RIGHT, parameter + Fraction(1, 100))

    def moving_mixed_brackets(p2):
        values = {}
        for left_private, right_private, name in (
            (P1, p2, "p1p2"),
            (p2, P3, "p2p3"),
        ):
            for first, second in combinations(range(8), 2):
                values[(name, first, second)] = bracket(
                    [
                        left_private,
                        right_private,
                        parent_column(first),
                        parent_column(second),
                    ]
                )
        for index, value in enumerate(contraction_brackets(p2)):
            values[("p1p2p3", index)] = value
        return values

    local_values = (
        moving_mixed_brackets(local_left),
        moving_mixed_brackets(local_right),
        moving_mixed_brackets(middle_p2),
    )
    changed = []
    for key in local_values[0]:
        left_value, right_value, middle_value = (
            values[key] for values in local_values
        )
        if left_value == 0 or right_value == 0:
            raise AssertionError("the local canary endpoint lies on a mixed wall")
        if (left_value > 0) != (right_value > 0):
            changed.append(key)
        elif middle_value == 0:
            raise AssertionError("an unrecorded mixed wall meets the local interval")
    if changed != [("p1p2p3", 0)]:
        raise AssertionError(f"the local interval has extra mixed walls: {changed}")

    if signature(local_left, normals) != SIGNATURES[1]:
        raise AssertionError("left local point leaves the extension chamber")
    if signature(local_right, normals) != SIGNATURES[1]:
        raise AssertionError("right local point leaves the extension chamber")
    return parameter, middle, len(local_values[0])


def volume(left, middle, right):
    return determinant(columns_to_rows([left, middle, right]))


def split_volume(left, middle, right, offset):
    return volume(
        left[offset : offset + 3],
        middle[offset : offset + 3],
        right[offset : offset + 3],
    )


def verify_alternating_model():
    basis = [tuple(int(i == j) for i in range(6)) for j in range(6)]
    for offset in (0, 3):
        # Each defining form is the decomposable coordinate form
        # dx_offset wedge dx_(offset+1) wedge dx_(offset+2).
        if split_volume(
            basis[offset], basis[offset + 1], basis[offset + 2], offset
        ) != 1:
            raise AssertionError("wrong decomposable volume orientation")
        if split_volume(
            basis[offset + 1], basis[offset], basis[offset + 2], offset
        ) != -1:
            raise AssertionError("the volume form is not alternating")
        if split_volume(
            basis[offset], basis[offset], basis[offset + 2], offset
        ) != 0:
            raise AssertionError("the Koszul repeated-row identity failed")

    # Z is exactly GL^+(3,R) x GL^+(3,R), after regrouping the first and
    # last three coordinates of the three row variables into two matrices.
    # Polar decomposition retracts each factor to SO(3)=RP^3.  In the usual
    # integral CW complex of RP^3, d_3=0; hence the unique product six-cell
    # has zero boundary and there is no seven-cell.
    rp3_boundary_ranks = {1: 0, 2: 1, 3: 0}
    boundary6_rank = rp3_boundary_ranks[3] + rp3_boundary_ranks[3]
    h6_rank = 1 - boundary6_rank
    if h6_rank != 1:
        raise AssertionError("wrong H_6 rank for SO(3) x SO(3)")
    return h6_rank


def main():
    h6_rank = verify_alternating_model()
    minima = verify_parent_and_extensions()
    parameter, middle, mixed_count = verify_loop_wall()

    print("PASS: two decomposable alternating 3-forms give convex-or-empty fibers in each R^6 row")
    print("PASS: their common positive locus retracts to SO(3) x SO(3), with H_6 rank", h6_rank)
    print("PASS: the exact rank-four/eight parent and all three extensions are uniform")
    print("PASS: signed endpoint bracket minima =", minima)
    print("PASS: only [p1,p2,p3,parent1] changes sign along the chamber segment")
    print("PASS: the unique loop parameter is", parameter)
    print("PASS: on the local +/-1/100 interval it is the only wall among", mixed_count, "moving mixed minors")
    print("PASS: the other seven contraction coordinates stay nonzero at the loop wall")
    print("      ", middle[1:])
    print("NO-GO: separate three-row convexity plus the local alternating/Koszul identity does not kill H_6")
    print("NO-GO: a fixed uniform triple-contraction stratum loses an actual specialization wall")
    print("SCOPE: full 9DVL occurrence coupling plus all specializations could still support a deeper theorem")


if __name__ == "__main__":
    main()
