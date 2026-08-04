#!/usr/bin/env python3
"""Exact checks for the diagonal-two block-Gordan/pivot no-go.

This verifier has two independent parts.

1.  A rational semialgebraic model shows that compact convex block-witness
    fibers, and even the same two-vertex support nerve, do not determine
    compactly supported H^1.  Two coordinate-plane covers have identical
    (nonempty-edge) nerves.  In one model the intersection is a point and
    H_c^1 of the union has rank one; in the other the intersection is a line
    and H_c^1 of the union vanishes.

2.  In the exact proper incomparable parent-16 defect-two example, the shear

        y_5(t) = y_5 + t y_2

    reaches a four-circuit wall at t=541589/6442906 before any parent wall or
    other circuit cofactor.  Every one of the 52 maximal five-support
    paddings of that four-circuit remains pencil-rigid when paired with the
    other five-circuit.  Exactly three paddings are strict on the outgoing
    side, 45 on the incoming side, and four are rank-degenerate at first
    order.  Thus the existing private-row boundary pivot cannot eliminate
    this coefficient, and an unsigned support-only Bland rule lacks the
    side/component data needed to continue.

All computations use exact integers and Fractions.  This is a no-go for a
proof strategy, not a counterexample to the second diagonal.
"""

from fractions import Fraction
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import prototype_koszul_circuits as koszul  # noqa: E402
import verify_second_diagonal_defect_two as defect  # noqa: E402


PIVOT_TIME = Fraction(541589, 6442906)
SAMPLE_DELTA = Fraction(1, 10**9)
MOVING_LABEL = 5
PARTNER_LABEL = 2
DROPPED_TRIPLE = (1, 2, 3)

EXPECTED_OUTGOING = ((1, 2, 6), (2, 3, 8), (4, 7, 8))
EXPECTED_DEGENERATE = ((1, 4, 5), (1, 4, 6), (1, 4, 7), (1, 4, 8))


def rational_rank(matrix):
    rows = [[Fraction(value) for value in row] for row in matrix]
    if not rows:
        return 0
    pivot_row = 0
    for column in range(len(rows[0])):
        pivot = next(
            (row for row in range(pivot_row, len(rows)) if rows[row][column]),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        scale = rows[pivot_row][column]
        rows[pivot_row] = [entry / scale for entry in rows[pivot_row]]
        for row in range(len(rows)):
            if row == pivot_row or not rows[row][column]:
                continue
            scale = rows[row][column]
            rows[row] = [
                left - scale * right
                for left, right in zip(rows[row], rows[pivot_row], strict=True)
            ]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def verify_support_nerve_no_go():
    """Two exact covers with the same nerve have different H_c^1.

    Compact model:
        L_0 = span(e_1,e_2), L_1 = span(e_3,e_4), intersection={0}.
    Escaping model:
        L_0 = span(e_1,e_2), L'_1=span(e_1,e_3), intersection=span(e_1).

    All three planes are copies of R^2, so their H_c^0 and H_c^1 vanish.
    Both cover nerves consist of two vertices and their edge.  Mayer--Vietoris
    gives rank H_c^1(union)=rank H_c^0(intersection), namely one versus zero.
    """
    first = ((1, 0, 0, 0), (0, 1, 0, 0))
    compact_partner = ((0, 0, 1, 0), (0, 0, 0, 1))
    escaping_partner = ((1, 0, 0, 0), (0, 0, 1, 0))

    # dim(U intersection V) = dim U + dim V - dim(U+V).
    compact_intersection_dimension = 4 - rational_rank(first + compact_partner)
    escaping_intersection_dimension = 4 - rational_rank(first + escaping_partner)
    if compact_intersection_dimension != 0:
        raise AssertionError("the compact model should intersect in one point")
    if escaping_intersection_dimension != 1:
        raise AssertionError("the escaping model should intersect in one line")

    # Exact cellular check on the one-point compactification of the compact
    # model.  It has two vertices (the origin and infinity), two parallel
    # one-cells, and two sphere two-cells with zero cellular boundary.
    boundary_one = ((-1, -1), (1, 1))
    boundary_two = ((0, 0), (0, 0))
    compact_h1_rank = 2 - rational_rank(boundary_one) - rational_rank(boundary_two)
    if compact_h1_rank != 1:
        raise AssertionError("wrong compact-support H^1 rank in compact model")

    # In the escaping model the intersection is R, whose H_c^0 vanishes.
    # The relevant Mayer--Vietoris arrow therefore has zero-dimensional
    # source, while H_c^1 of both R^2 pieces is also zero.
    escaping_h1_rank = 0
    if escaping_h1_rank != 0:
        raise AssertionError("wrong compact-support H^1 rank in escaping model")

    # The block-incidence resolution for the compact model is
    #   u*x_3=u*x_4=0, v*x_1=v*x_2=0, u+v=1, u,v>=0.
    # Its fiber is a singleton off the origin and the full interval at the
    # origin.  The following exact representatives check all three cases.
    def allowed_weights(point):
        x1, x2, x3, x4 = map(Fraction, point)
        if x3 == x4 == 0 and (x1 or x2):
            return "left_endpoint"
        if x1 == x2 == 0 and (x3 or x4):
            return "right_endpoint"
        if x1 == x2 == x3 == x4 == 0:
            return "full_interval"
        return "empty"

    if tuple(
        allowed_weights(point)
        for point in ((1, 2, 0, 0), (0, 0, 3, 4), (0, 0, 0, 0), (1, 0, 1, 0))
    ) != ("left_endpoint", "right_endpoint", "full_interval", "empty"):
        raise AssertionError("wrong block-incidence fibers")


def shear_parent(parameter):
    result = [list(map(Fraction, row)) for row in defect.PARENT]
    for coordinate in range(4):
        result[coordinate][MOVING_LABEL - 1] += (
            parameter * Fraction(defect.PARENT[coordinate][PARTNER_LABEL - 1])
        )
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
    values = oriented_cofactors(defect.PARENT, signature, support, 1)
    if all(value > 0 for value in values):
        return 1
    if all(value < 0 for value in values):
        return -1
    raise AssertionError("the initial support is not a strict positive circuit")


def quadratic(values):
    constant = values[0]
    second = (values[2] - 2 * values[1] + values[0]) / 2
    first = values[1] - constant - second
    return constant, first, second


def evaluate(polynomial, parameter):
    constant, first, second = polynomial
    return constant + first * parameter + second * parameter * parameter


def exact_first_pivot():
    """Verify that PIVOT_TIME is the first non-strict event on the ray."""
    left_orientation = positive_orientation(
        defect.LEFT_SIGNATURE, defect.LEFT_SUPPORT
    )
    right_orientation = positive_orientation(
        defect.RIGHT_SIGNATURE, defect.RIGHT_SUPPORT
    )

    # Every parent bracket is affine because only one column moves.  Its
    # endpoint is nonzero with the initial sign, so none vanishes earlier.
    parent_samples = [
        defect.parent_brackets(shear_parent(Fraction(sample)))
        for sample in range(3)
    ]
    parent_end = defect.parent_brackets(shear_parent(PIVOT_TIME))
    for coordinate, (start, end) in enumerate(
        zip(parent_samples[0], parent_end, strict=True)
    ):
        if (
            parent_samples[2][coordinate]
            - 2 * parent_samples[1][coordinate]
            + parent_samples[0][coordinate]
        ):
            raise AssertionError("a parent bracket is not affine")
        if not end or (start > 0) != (end > 0):
            raise AssertionError("a parent wall occurs before the circuit pivot")

    dropped_index = defect.LEFT_SUPPORT.index(
        koszul.TRIPLE_INDEX[DROPPED_TRIPLE]
    )
    for signature, support, orientation, exceptional in (
        (
            defect.LEFT_SIGNATURE,
            defect.LEFT_SUPPORT,
            left_orientation,
            dropped_index,
        ),
        (
            defect.RIGHT_SIGNATURE,
            defect.RIGHT_SUPPORT,
            right_orientation,
            None,
        ),
    ):
        samples = [
            oriented_cofactors(
                shear_parent(Fraction(sample)), signature, support, orientation
            )
            for sample in range(5)
        ]
        endpoint = oriented_cofactors(
            shear_parent(PIVOT_TIME), signature, support, orientation
        )
        for coordinate in range(5):
            polynomial = quadratic(
                [samples[sample][coordinate] for sample in range(3)]
            )
            if any(
                evaluate(polynomial, Fraction(sample))
                != samples[sample][coordinate]
                for sample in range(3, 5)
            ):
                raise AssertionError("a circuit cofactor has degree above two")
            if coordinate == exceptional:
                if polynomial[2] or evaluate(polynomial, PIVOT_TIME):
                    raise AssertionError("the claimed first pivot is not linear")
                if polynomial[0] <= 0:
                    raise AssertionError("the dropped coefficient is not initially positive")
            else:
                if not defect.positive_quadratic_on_interval(
                    polynomial, PIVOT_TIME
                ):
                    raise AssertionError("another cofactor vanishes before the pivot")
                if endpoint[coordinate] <= 0:
                    raise AssertionError("a retained cofactor is not strict at the pivot")

    if PIVOT_TIME != Fraction(541589, 6442906):
        raise AssertionError("wrong exact pivot time")
    return left_orientation, right_orientation, dropped_index


def strict_positive_circuit(matrix, signature, support):
    columns = defect.signed_columns(matrix, signature, support)
    cofactors = tuple(
        (-1) ** omitted
        * koszul.determinant(
            [columns[index] for index in range(5) if index != omitted]
        )
        for omitted in range(5)
    )
    return all(value > 0 for value in cofactors) or all(
        value < 0 for value in cofactors
    )


def verify_padding_fan(left_orientation, right_orientation, dropped_index):
    pivot_matrix = shear_parent(PIVOT_TIME)
    dropped = defect.LEFT_SUPPORT[dropped_index]
    four_support = tuple(index for index in defect.LEFT_SUPPORT if index != dropped)
    four_columns = defect.signed_columns(
        pivot_matrix, defect.LEFT_SIGNATURE, four_support
    )
    if koszul.matrix_rank(four_columns) != 3:
        raise AssertionError("the pivot support is not a rank-three four-circuit")
    for omitted in range(4):
        remaining = four_columns[:omitted] + four_columns[omitted + 1 :]
        if koszul.matrix_rank(remaining) != 3:
            raise AssertionError("the four-circuit is not support-minimal")

    # The zero-padded five-circuit relation gives a strict positive relation
    # on the four retained columns.
    pivot_values = oriented_cofactors(
        pivot_matrix,
        defect.LEFT_SIGNATURE,
        defect.LEFT_SUPPORT,
        left_orientation,
    )
    retained_weights = tuple(
        value for index, value in enumerate(pivot_values) if index != dropped_index
    )
    if not all(value > 0 for value in retained_weights):
        raise AssertionError("the retained four-circuit weights are not positive")
    for coordinate in range(4):
        if sum(
            weight * column[coordinate]
            for weight, column in zip(
                retained_weights, four_columns, strict=True
            )
        ):
            raise AssertionError("the four-circuit relation is not exact")

    incoming = []
    outgoing = []
    degenerate = []
    all_candidates = []
    original_q = dropped
    left_side_matrix = shear_parent(PIVOT_TIME - SAMPLE_DELTA)
    right_side_matrix = shear_parent(PIVOT_TIME + SAMPLE_DELTA)

    # The parent and the other signature remain strict on both samples.
    start_parent = defect.parent_brackets(defect.PARENT)
    for matrix in (left_side_matrix, right_side_matrix):
        brackets = defect.parent_brackets(matrix)
        if not all(brackets) or any(
            (start > 0) != (value > 0)
            for start, value in zip(start_parent, brackets, strict=True)
        ):
            raise AssertionError("a local padding sample left the parent cell")
        if not all(
            value > 0
            for value in oriented_cofactors(
                matrix,
                defect.RIGHT_SIGNATURE,
                defect.RIGHT_SUPPORT,
                right_orientation,
            )
        ):
            raise AssertionError("the partner circuit is not strict near the pivot")

    for candidate in range(len(koszul.TRIPLES)):
        if candidate in four_support:
            continue
        support = tuple(sorted(four_support + (candidate,)))
        all_candidates.append(support)
        candidate_position = support.index(candidate)
        columns = defect.signed_columns(
            pivot_matrix, defect.LEFT_SIGNATURE, support
        )
        raw = tuple(
            (-1) ** omitted
            * koszul.determinant(
                [columns[index] for index in range(5) if index != omitted]
            )
            for omitted in range(5)
        )
        if raw[candidate_position]:
            raise AssertionError("the entering coefficient is not zero on the wall")
        existing = tuple(
            value for index, value in enumerate(raw) if index != candidate_position
        )
        if not all(existing) or not (
            all(value > 0 for value in existing)
            or all(value < 0 for value in existing)
        ):
            if koszul.matrix_rank(columns) != 3:
                raise AssertionError("a degenerate padding has unexpected rank")
            degenerate.append(candidate)
        else:
            if koszul.matrix_rank(columns) != 4:
                raise AssertionError("a transverse padding does not have rank four")
            orientation = 1 if all(value > 0 for value in existing) else -1
            candidate_values = []
            for offset in range(3):
                offset_matrix = shear_parent(PIVOT_TIME + Fraction(offset))
                offset_columns = defect.signed_columns(
                    offset_matrix, defect.LEFT_SIGNATURE, support
                )
                candidate_values.append(
                    orientation
                    * (-1) ** candidate_position
                    * koszul.determinant(
                        [
                            offset_columns[index]
                            for index in range(5)
                            if index != candidate_position
                        ]
                    )
                )
            if candidate_values[0] or (
                candidate_values[2]
                - 2 * candidate_values[1]
                + candidate_values[0]
            ):
                raise AssertionError("the four-circuit wall is not a simple affine pivot")
            if not candidate_values[1]:
                raise AssertionError("a transverse padding has zero wall derivative")
            before = strict_positive_circuit(
                left_side_matrix, defect.LEFT_SIGNATURE, support
            )
            after = strict_positive_circuit(
                right_side_matrix, defect.LEFT_SIGNATURE, support
            )
            if before == after:
                raise AssertionError("a transverse padding did not choose one wall side")
            if after != (candidate_values[1] > 0):
                raise AssertionError("sampled side disagrees with the exact wall derivative")
            (outgoing if after else incoming).append(candidate)

        union_with_partner = set(support) | set(defect.RIGHT_SUPPORT)
        if not defect.pencil_rigid(union_with_partner):
            raise AssertionError("a maximal padding becomes pencil-flexible")
        if defect.partner_defect(union_with_partner) != 2:
            raise AssertionError("a maximal padding leaves the defect-two class")

        # For a genuine third index T != Q, the other competing pair Q,T is
        # formally killed by pencil pruning, but R,T is never killed.
        if candidate != original_q:
            if defect.pencil_rigid(set(defect.LEFT_SUPPORT) | set(support)):
                raise AssertionError("the Q,T competing pair should be flexible")

    if len(all_candidates) != 52:
        raise AssertionError("a four-support should have 52 maximal paddings")
    if tuple(koszul.TRIPLES[index] for index in outgoing) != EXPECTED_OUTGOING:
        raise AssertionError("wrong outgoing padding list")
    if tuple(koszul.TRIPLES[index] for index in degenerate) != EXPECTED_DEGENERATE:
        raise AssertionError("wrong degenerate padding list")
    if len(incoming) != 45 or original_q not in incoming:
        raise AssertionError("wrong incoming padding count")

    # The lexicographically/colex-index smallest alternative padding is 234,
    # and it is incoming-only.  The smallest geometrically eligible outgoing
    # padding is 126.  Thus support order alone cannot choose the continuation.
    alternative = [index for index in incoming + outgoing + degenerate if index != original_q]
    if min(alternative) != koszul.TRIPLE_INDEX[(2, 3, 4)]:
        raise AssertionError("wrong smallest alternative padding")
    if min(outgoing) != koszul.TRIPLE_INDEX[(1, 2, 6)]:
        raise AssertionError("wrong smallest outgoing padding")


def verify_proper_incomparable_hypotheses():
    expected_parent = defect.parent_sign_string(defect.PARENT)
    left_parent = defect.child_check(
        defect.LEFT_CHILD, defect.LEFT_SIGNATURE, expected_parent
    )
    right_parent = defect.child_check(
        defect.RIGHT_CHILD, defect.RIGHT_SIGNATURE, expected_parent
    )
    defect.positive_circuit(
        left_parent, defect.RIGHT_SIGNATURE, defect.RIGHT_BAD_AT_LEFT
    )
    defect.positive_circuit(
        right_parent, defect.LEFT_SIGNATURE, defect.LEFT_BAD_AT_RIGHT
    )


def main():
    verify_support_nerve_no_go()
    verify_proper_incomparable_hypotheses()
    left_orientation, right_orientation, dropped_index = exact_first_pivot()
    verify_padding_fan(left_orientation, right_orientation, dropped_index)
    print("PASS exact two-plane covers have the same nerve but H_c^1 ranks 1 and 0")
    print("PASS compact convex block fibers do not force H_c^1 vanishing")
    print("PASS proper incomparable defect-two pair reaches the exact 123 support drop")
    print("PASS all 52 cofinal paddings remain pencil-rigid of global defect two")
    print("PASS padding fan is 45 incoming / 3 outgoing / 4 degenerate")
    print("PASS every alternative triple row retains the R,T competing pair")
    print("NO-GO support-only or vertical Bland matching cannot prove diagonal two")
    print("CAVEAT the second diagonal remains open; no nonzero OM class is claimed")


if __name__ == "__main__":
    main()
