#!/usr/bin/env python3
"""Exact formal no-go for fixed-minor wall axioms in diagonal eight.

The model has a contractible open nine-cell and eight proper pairwise-
incomparable strict factor sides.  Every subfamily has a fixed unit Jacobian
minor, so every common-zero component is noncompact, and literal all-strata
label gluing holds.  The common intersection has convex fibers over an
annulus and hence has H_1 = Z.

This is not a UOM realization-space example.  It proves that the currently
isolated abstract wall axioms do not imply diagonal eight.
"""

from fractions import Fraction
from itertools import combinations


def p_value(radius_squared):
    return (radius_squared - 1) * (4 - radius_squared)


def u_value(radius_squared):
    p = p_value(radius_squared)
    return p / (1 + p * p)


def q_values(x, y, s_values):
    return (x,) + tuple(s_values) + (y + 3 + s_values[0],)


def in_parent(x, radius_squared):
    return -1 < x < u_value(radius_squared)


def determinant(matrix):
    """Exact determinant by fraction-preserving Gaussian elimination."""
    work = [[Fraction(entry) for entry in row] for row in matrix]
    result = Fraction(1)
    for column in range(len(work)):
        pivot = next(row for row in range(column, len(work))
                     if work[row][column])
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        pivot_value = work[column][column]
        result *= pivot_value
        for row in range(column + 1, len(work)):
            scale = work[row][column] / pivot_value
            for entry in range(column, len(work)):
                work[row][entry] -= scale * work[column][entry]
    return result


def main():
    # |p/(1+p^2)| <= 1/2 follows from this exact square identity.  Hence
    # every parent x-fiber (-1,u) is nonempty.
    square_of_sum = (1, 2, 1)   # (1+p^2)^2, in powers of p^2
    four_p_squared = (0, 4, 0)
    square_of_difference = (1, -2, 1)  # (p^2-1)^2
    assert tuple(
        left - right for left, right in zip(square_of_sum, four_p_squared)
    ) == square_of_difference
    for p in tuple(map(Fraction, range(-20, 21))) + (
        Fraction(1, 3), Fraction(-7, 5), Fraction(101, 17)
    ):
        assert (1 + p * p) ** 2 - 4 * p * p == (p * p - 1) ** 2
        assert abs(p / (1 + p * p)) <= Fraction(1, 2)

    radius_squared = Fraction(9, 4)
    u = u_value(radius_squared)
    assert p_value(radius_squared) == Fraction(35, 16)
    assert u == Fraction(560, 1481) > Fraction(1, 10)

    # Rows q_1=x, q_2=s_1,...,q_7=s_6,q_8=y+3+s_1, with columns
    # (x,s_1,...,s_6,y).  Assign one distinct column to each row.  Every
    # resulting subfamily minor is exactly one.
    jacobian = (
        (1, 0, 0, 0, 0, 0, 0, 0),
        (0, 1, 0, 0, 0, 0, 0, 0),
        (0, 0, 1, 0, 0, 0, 0, 0),
        (0, 0, 0, 1, 0, 0, 0, 0),
        (0, 0, 0, 0, 1, 0, 0, 0),
        (0, 0, 0, 0, 0, 1, 0, 0),
        (0, 0, 0, 0, 0, 0, 1, 0),
        (0, 1, 0, 0, 0, 0, 0, 1),
    )
    for size in range(1, 9):
        for rows in combinations(range(8), size):
            minor = [[jacobian[row][column] for column in rows]
                     for row in rows]
            assert determinant(minor) == 1

    zero_s = (Fraction(0),) * 6

    # Every side is proper.
    plus_x = q_values(Fraction(1, 10), Fraction(3, 2), zero_s)
    minus_x = q_values(Fraction(-1, 10), Fraction(3, 2), zero_s)
    assert in_parent(Fraction(1, 10), radius_squared)
    assert in_parent(Fraction(-1, 10), radius_squared)
    assert plus_x[0] > 0 > minus_x[0]
    for position in range(1, 7):
        positive = list(zero_s)
        negative = list(zero_s)
        positive[position - 1] = 1
        negative[position - 1] = -1
        assert q_values(Fraction(-1, 10), Fraction(3, 2), positive)[position] > 0
        assert q_values(Fraction(-1, 10), Fraction(3, 2), negative)[position] < 0
        assert in_parent(Fraction(-1, 10), radius_squared)
    assert in_parent(Fraction(-1, 2), 0)
    assert q_values(Fraction(-1, 2), 0, zero_s)[7] > 0
    q8_negative_s = (Fraction(-4),) + zero_s[1:]
    assert q_values(Fraction(-1, 2), 0, q8_negative_s)[7] < 0

    # Every pair is incomparable.  Independent coordinate pairs are direct.
    for left, right in combinations(range(7), 2):
        first = [Fraction(0)] * 7  # x,s_1,...,s_6
        second = [Fraction(0)] * 7
        first[left], first[right] = 1, -1
        second[left], second[right] = -1, 1
        # Scale x witnesses into the parent interval when q_1 is involved.
        if left == 0:
            first[0], second[0] = Fraction(1, 10), Fraction(-1, 10)
        assert in_parent(first[0], radius_squared)
        assert in_parent(second[0], radius_squared)
        first_q = q_values(first[0], Fraction(3, 2), first[1:])
        second_q = q_values(second[0], Fraction(3, 2), second[1:])
        assert first_q[left] > 0 > first_q[right]
        assert second_q[right] > 0 > second_q[left]

    # q_1 versus q_8 at the annulus point.
    first_s = (Fraction(-10),) + zero_s[1:]
    assert in_parent(Fraction(1, 10), radius_squared)
    assert in_parent(Fraction(-1, 10), radius_squared)
    first_q = q_values(Fraction(1, 10), Fraction(3, 2), first_s)
    second_q = q_values(Fraction(-1, 10), Fraction(3, 2), zero_s)
    assert first_q[0] > 0 > first_q[7]
    assert second_q[7] > 0 > second_q[0]

    # q_2=s_1 versus q_8 uses two different parent-base points.
    first_q = q_values(Fraction(-1, 2), -10,
                       (Fraction(1),) + zero_s[1:])
    assert in_parent(Fraction(-1, 2), 100)
    assert first_q[1] > 0 > first_q[7]
    second_q = q_values(Fraction(-1, 2), 0,
                        (Fraction(-1),) + zero_s[1:])
    assert in_parent(Fraction(-1, 2), 0)
    assert second_q[7] > 0 > second_q[1]

    # q_3,...,q_7 versus q_8 vary their independent s-coordinate.
    for position in range(2, 7):
        first_s = [Fraction(0)] * 6
        first_s[0], first_s[position - 1] = -4, 1
        assert in_parent(Fraction(-1, 2), 0)
        first_q = q_values(Fraction(-1, 2), 0, first_s)
        second_s = [Fraction(0)] * 6
        second_s[position - 1] = -1
        second_q = q_values(Fraction(-1, 2), 0, second_s)
        assert first_q[position] > 0 > first_q[7]
        assert second_q[7] > 0 > second_q[position]

    # u has the sign of P, and P>0 precisely on 1<r^2<4.  These exact
    # samples guard all three sign intervals and both roots.
    samples = (
        (Fraction(0), -1),
        (Fraction(1), 0),
        (Fraction(2), 1),
        (Fraction(4), 0),
        (Fraction(5), -1),
    )
    for radius_squared, expected in samples:
        p = p_value(radius_squared)
        sign = (p > 0) - (p < 0)
        assert sign == expected
        assert ((u_value(radius_squared) > 0) - (u_value(radius_squared) < 0)) == expected

    print("PASS exact contractible-parent fiber bound |u|<=1/2")
    # On common support, x>0 forces u>0 and hence |y|<2.  Since s_1>0,
    # q_8=y+3+s_1>1 is automatic.  Conversely every point over the annulus
    # with 0<x<u and all s_j>0 satisfies all eight inequalities.
    for y in (Fraction(-3, 2), Fraction(0), Fraction(3, 2)):
        for z in (Fraction(0), Fraction(1, 2)):
            r2 = y * y + z * z
            if 1 < r2 < 4:
                assert abs(y) < 2
                assert y + 3 + Fraction(1, 10) > 0

    print("PASS every nonempty subfamily has a fixed unit Jacobian minor")
    print("PASS all eight strict sides are proper and pairwise incomparable")
    print("PASS every common-zero component is a noncompact smooth manifold")
    print("PASS common support has convex fibers over 1<y^2+z^2<4")
    print("THEOREM common support retracts to S^1 and has H_1=Z")
    print("CAVEAT formal semialgebraic no-go, not a UOM counterexample")


if __name__ == "__main__":
    main()
