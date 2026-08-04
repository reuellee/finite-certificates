#!/usr/bin/env python3
"""Exact bounded audit of the one-row double-contraction model.

The computation uses only ``fractions.Fraction``.  It proves two facts used in
``DIAG2_PIVOT_DOUBLE_FIBER_KOSZUL.md``.

* A Koszul normal coming from a four-subset is alternating, so it annihilates
  the current first height row.  Consequently a bad circuit with exactly one
  contracted-column (constant) normal is impossible in a uniform first lift.
* This does not provide a height escape for every Gordan witness.  An explicit
  uniform rank-two quotient, with private labels 0 and 2, has an allowed
  seven-row positive circuit.  Its alternating pencil is invertible, so the
  fixed-weight bad incidence is an isolated first height row.  The prescribed
  signs are realized at another height row in the same uniform first-lift
  chamber by an exact rank-four configuration.

This is a no-go certificate for a proposed Koszul-kernel proof.  It does not
compute the homology of the full projected fiber ``P_b``.
"""

from fractions import Fraction
from itertools import combinations, permutations


LABELS = tuple(range(8))
GAUGE_COORDS = tuple(range(2, 8))
PRIVATE = frozenset((0, 2))
PARENT = (1, 3, 4, 5, 6, 7, "e", "f")

CONSTANT_SUPPORTS = ((0, 1, 7), (2, 3, 5))
CONSTANT_SIGNS = (-1, -1)
VARIABLE_SUPPORTS = (
    (1, 4, 5, 6),
    (2, 3, 5, 6),
    (2, 3, 4, 6),
    (2, 3, 5, 7),
    (0, 4, 5, 7),
)
VARIABLE_SIGNS = (-1, -1, 1, 1, -1)

# Labels 0 and 1 are killed by the affine-linear height gauge.
BAD_H = (
    Fraction(0),
    Fraction(0),
    Fraction(38, 3),
    Fraction(34, 3),
    Fraction(16, 3),
    Fraction(19, 3),
    Fraction(43, 3),
    Fraction(7, 3),
)
GOOD_H = (
    Fraction(0),
    Fraction(0),
    Fraction(1),
    Fraction(12581, 10000),
    Fraction(13466, 10000),
    Fraction(16766, 10000),
    Fraction(23518, 10000),
    Fraction(22182, 10000),
)
GOOD_K = (
    Fraction(0),
    Fraction(0),
    Fraction(379),
    Fraction(305),
    Fraction(138),
    Fraction(159),
    Fraction(255),
    Fraction(1),
)


def determinant(matrix):
    """Exact determinant, used only in sizes at most seven."""
    size = len(matrix)
    total = Fraction(0)
    for permutation in permutations(range(size)):
        inversions = sum(
            permutation[i] > permutation[j]
            for i in range(size)
            for j in range(i + 1, size)
        )
        term = Fraction((-1) ** inversions)
        for row in range(size):
            term *= Fraction(matrix[row][permutation[row]])
        total += term
    return total


def rank(matrix):
    work = [[Fraction(value) for value in row] for row in matrix]
    row_count = len(work)
    column_count = len(work[0]) if work else 0
    pivot_row = 0
    for column in range(column_count):
        pivot = next(
            (row for row in range(pivot_row, row_count) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [value / scale for value in work[pivot_row]]
        for row in range(row_count):
            if row == pivot_row or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                value - scale * pivot_value
                for value, pivot_value in zip(
                    work[row], work[pivot_row], strict=True
                )
            ]
        pivot_row += 1
    return pivot_row


def quotient_column(label, h_value, k_value):
    return (Fraction(1), Fraction(label), Fraction(h_value), Fraction(k_value))


def bracket(columns):
    return determinant(
        [[Fraction(column[row]) for column in columns] for row in range(4)]
    )


def omega(support):
    """Matrix for det((1,t,h,k)_i : i in support) = h^T Omega k."""
    output = []
    for first in GAUGE_COORDS:
        row = []
        for second in GAUGE_COORDS:
            columns = [
                quotient_column(
                    label,
                    Fraction(label == first),
                    Fraction(label == second),
                )
                for label in support
            ]
            row.append(bracket(columns))
        output.append(row)
    return output


def constant_normal(support):
    """Normal of the bracket with contracted column e=(0,0,1,0)."""
    output = []
    e_column = (Fraction(0), Fraction(0), Fraction(1), Fraction(0))
    for coordinate in GAUGE_COORDS:
        columns = [
            quotient_column(label, 0, Fraction(label == coordinate))
            for label in support
        ]
        output.append(bracket(columns + [e_column]))
    return output


def variable_normal(matrix, height):
    reduced_height = [height[label] for label in GAUGE_COORDS]
    return [
        sum(
            (reduced_height[row] * matrix[row][column] for row in range(6)),
            Fraction(0),
        )
        for column in range(6)
    ]


def triple_bracket(support, height):
    f_column = (Fraction(0), Fraction(0), Fraction(0), Fraction(1))
    columns = [
        quotient_column(label, height[label], 0) for label in support
    ]
    return bracket(columns + [f_column])


def actual_column(label, height, second_height):
    if label == "e":
        return (Fraction(0), Fraction(0), Fraction(1), Fraction(0))
    if label == "f":
        return (Fraction(0), Fraction(0), Fraction(0), Fraction(1))
    return quotient_column(label, height[label], second_height[label])


def actual_bracket(support, height=GOOD_H, second_height=GOOD_K):
    return bracket(
        [actual_column(label, height, second_height) for label in support]
    )


def verify_koszul_identities():
    # Every determinant form omitting e and f is genuinely alternating.
    for support in combinations(LABELS, 4):
        matrix = omega(support)
        if any(
            matrix[row][column] != -matrix[column][row]
            for row in range(6)
            for column in range(6)
        ):
            raise AssertionError("a Koszul matrix is not alternating")
        normal = variable_normal(matrix, BAD_H)
        reduced_height = [BAD_H[label] for label in GAUGE_COORDS]
        if sum(
            (normal[index] * reduced_height[index] for index in range(6)),
            Fraction(0),
        ):
            raise AssertionError("a variable normal does not annihilate h")

    # A constant normal paired with h is, up to the fixed column-order sign,
    # the corresponding bracket containing the other contracted column f.
    for support in combinations(LABELS, 3):
        normal = constant_normal(support)
        pairing = sum(
            (normal[index] * BAD_H[label] for index, label in enumerate(GAUGE_COORDS)),
            Fraction(0),
        )
        if pairing != -triple_bracket(support, BAD_H):
            raise AssertionError("constant/Koszul pairing identity failed")


def verify_uniform_same_first_lift_chamber():
    for support in combinations(LABELS, 3):
        bad_value = triple_bracket(support, BAD_H)
        good_value = triple_bracket(support, GOOD_H)
        if not bad_value or not good_value:
            raise AssertionError("a first lift is nonuniform")
        if (bad_value > 0) != (good_value > 0):
            raise AssertionError("the two heights leave their first-lift chamber")


def verify_actual_parent_and_extensions():
    # The good chart is stronger than the partial 9DVL incidence requirement:
    # all ten columns form one uniform rank-four configuration.
    all_labels = (*LABELS, "e", "f")
    if any(actual_bracket(support) == 0 for support in combinations(all_labels, 4)):
        raise AssertionError("the realizing ten-column matrix is not uniform")
    if any(actual_bracket(support) == 0 for support in combinations(PARENT, 4)):
        raise AssertionError("the eight-column parent is not uniform")
    for private in PRIVATE:
        if any(
            actual_bracket((*support, private)) == 0
            for support in combinations(PARENT, 3)
        ):
            raise AssertionError("a private extension is not uniform")

    # Every row in the bad circuit is prescribed in the partial 9DVL problem:
    # none contains both private labels.
    all_supports = (*CONSTANT_SUPPORTS, *VARIABLE_SUPPORTS)
    if any(PRIVATE <= set(support) for support in all_supports):
        raise AssertionError("the obstruction used an unprescribed private-private basis")

    good_values = [
        sign * actual_bracket((*support, "e"))
        for support, sign in zip(
            CONSTANT_SUPPORTS, CONSTANT_SIGNS, strict=True
        )
    ]
    good_values.extend(
        sign * actual_bracket(support)
        for support, sign in zip(
            VARIABLE_SUPPORTS, VARIABLE_SIGNS, strict=True
        )
    )
    expected = (
        Fraction(1),
        Fraction(2),
        Fraction(171, 200),
        Fraction(10902, 625),
        Fraction(533, 1000),
        Fraction(4631, 5000),
        Fraction(671, 625),
    )
    if tuple(good_values) != expected or not all(value > 0 for value in good_values):
        raise AssertionError("the exact good chart does not realize all seven signs")


def verify_minimal_bad_circuit_and_rigid_weight_slice():
    constant_rows = [
        [sign * value for value in constant_normal(support)]
        for support, sign in zip(
            CONSTANT_SUPPORTS, CONSTANT_SIGNS, strict=True
        )
    ]
    matrices = [omega(support) for support in VARIABLE_SUPPORTS]
    variable_rows = [
        [sign * value for value in variable_normal(matrix, BAD_H)]
        for matrix, sign in zip(matrices, VARIABLE_SIGNS, strict=True)
    ]
    rows = constant_rows + variable_rows

    if rank(rows) != 6:
        raise AssertionError("the displayed dependence is not support-minimal")
    if any(sum((row[column] for row in rows), Fraction(0)) for column in range(6)):
        raise AssertionError("the all-unit Gordan vector does not annihilate the rows")
    cofactors = [
        (-1) ** omitted * determinant(rows[:omitted] + rows[omitted + 1 :])
        for omitted in range(7)
    ]
    if cofactors != [Fraction(-4802, 3)] * 7:
        raise AssertionError("the seven positive circuit weights are not exact")

    # With the two constant rows fixed, the all-unit dependence equation is
    # S h = c.  det(S)=9 proves that this fixed-weight incidence has one and
    # only one first height row; alternation gives no tangent escape here.
    pencil = [
        [
            sum(
                (
                    sign * matrix[row][column]
                    for matrix, sign in zip(
                        matrices, VARIABLE_SIGNS, strict=True
                    )
                ),
                Fraction(0),
            )
            for column in range(6)
        ]
        for row in range(6)
    ]
    if determinant(pencil) != 9:
        raise AssertionError("the alternating pencil is not invertible")
    signed_constant_sum = [
        sum((row[column] for row in constant_rows), Fraction(0))
        for column in range(6)
    ]
    reduced_bad_height = [BAD_H[label] for label in GAUGE_COORDS]
    image = [
        sum(
            (
                pencil[row][column] * reduced_bad_height[column]
                for column in range(6)
            ),
            Fraction(0),
        )
        for row in range(6)
    ]
    if image != signed_constant_sum:
        raise AssertionError("the unique fixed-weight height is incorrect")


def main():
    verify_koszul_identities()
    verify_uniform_same_first_lift_chamber()
    verify_actual_parent_and_extensions()
    verify_minimal_bad_circuit_and_rigid_weight_slice()
    print("PASS all determinant and Koszul identities hold over Q")
    print("PASS the good and bad heights lie in one uniform first-lift chamber")
    print("PASS an exact uniform parent and both private signatures realize the good chart")
    print("PASS all seven obstruction rows avoid private-private bases")
    print("PASS the bad chart has a support-minimal all-positive seven-circuit")
    print("PASS the fixed-weight alternating pencil has determinant 9")
    print("NO-GO: Koszul alternation does not give every Gordan witness a height escape")
    print("NOTE: this certificate does not determine H_q(P_b) in any degree")


if __name__ == "__main__":
    main()
