#!/usr/bin/env python3
"""Exact eliminant discovery for the pinned diagonal-3 concurrence slice.

This is a discovery helper, not a theorem verifier.  It derives the affine
degree-six fiber eliminant after solving F1 for vs and F2 for ws, removes the
identically nonuniform solution (vr,wr)=(1/3,1/3), and computes exact
projection discriminants by a fraction-free Sylvester determinant.
"""

from fractions import Fraction as Q
from itertools import permutations
from math import gcd, lcm
import sys

sys.path.insert(0, "ai/omreal/data")
import DIAG3_concurrence_ramification_rur as certificate  # noqa: E402


def sparse_add(left, right):
    answer = dict(left)
    for monomial, coefficient in right.items():
        answer[monomial] = answer.get(monomial, Q(0)) + coefficient
    return {monomial: value for monomial, value in answer.items() if value}


def sparse_multiply(left, right):
    answer = {}
    for first, first_value in left.items():
        for second, second_value in right.items():
            monomial = tuple(a + b for a, b in zip(first, second))
            answer[monomial] = answer.get(monomial, Q(0)) + first_value * second_value
    return {monomial: value for monomial, value in answer.items() if value}


def sparse_scale(polynomial, scalar):
    return {
        monomial: coefficient * scalar
        for monomial, coefficient in polynomial.items()
        if coefficient * scalar
    }


def sparse_power(polynomial, exponent, variables):
    answer = {(0,) * variables: Q(1)}
    for _ in range(exponent):
        answer = sparse_multiply(answer, polynomial)
    return answer


def determinant(matrix, variables):
    answer = {}
    for permutation in permutations(range(len(matrix))):
        inversions = sum(
            permutation[left] > permutation[right]
            for left in range(len(matrix))
            for right in range(left + 1, len(matrix))
        )
        term = {(0,) * variables: Q(-1 if inversions & 1 else 1)}
        for row in range(len(matrix)):
            term = sparse_multiply(term, matrix[row][permutation[row]])
        answer = sparse_add(answer, term)
    return answer


def build_reduced_quadratics():
    """Return cleared F3,F4 in (vr,wr,t) after the F1,F2 graphs."""
    x = {(1, 0, 0): Q(1)}
    z = {(0, 1, 0): Q(1)}
    t = {(0, 0, 1): Q(1)}
    one = {(0, 0, 0): Q(1)}
    y_numerator = sparse_add(
        sparse_add(
            sparse_multiply(
                sparse_add(sparse_scale(one, 252), sparse_scale(t, -315)), x
            ),
            sparse_multiply(
                sparse_add(sparse_scale(one, 1683), sparse_scale(t, 2244)), z
            ),
        ),
        sparse_add(sparse_scale(t, -116), sparse_scale(one, -645)),
    )
    minus_w_numerator = sparse_add(
        sparse_add(
            sparse_multiply(
                sparse_add(sparse_scale(t, 459), sparse_scale(one, -459)),
                sparse_multiply(x, z),
            ),
            sparse_multiply(
                sparse_add(sparse_scale(t, -99), sparse_scale(one, 99)), x
            ),
        ),
        sparse_add(
            sparse_multiply(
                sparse_add(sparse_scale(t, -1020), sparse_scale(one, 153)), z
            ),
            sparse_add(sparse_scale(t, 220), sparse_scale(one, -33)),
        ),
    )
    w_numerator = sparse_scale(minus_w_numerator, -1)

    def substitute(polynomial):
        answer = {}
        for monomial, coefficient in polynomial:
            x_degree, y_degree, z_degree, w_degree, t_degree = monomial
            term = sparse_multiply(
                sparse_multiply(
                    sparse_power(x, x_degree - w_degree + 1, 3),
                    sparse_power(z, z_degree, 3),
                ),
                sparse_power(t, t_degree, 3),
            )
            term = sparse_multiply(
                term, sparse_power(y_numerator, y_degree, 3)
            )
            term = sparse_multiply(
                term, sparse_power(w_numerator, w_degree, 3)
            )
            scalar = Q(coefficient) * Q(
                527 * 306, Q(527) ** y_degree * Q(306) ** w_degree
            )
            answer = sparse_add(answer, sparse_scale(term, scalar))
        return answer

    return tuple(substitute(polynomial) for polynomial in certificate.SYSTEM[2:4])


def primitive_integer(polynomial):
    denominator = 1
    for value in polynomial.values():
        denominator = lcm(denominator, value.denominator)
    answer = {
        monomial: int(value * denominator) for monomial, value in polynomial.items()
    }
    content = 0
    for value in answer.values():
        content = gcd(content, abs(value))
    answer = {monomial: value // content for monomial, value in answer.items()}
    if answer[max(answer)] < 0:
        answer = {monomial: -value for monomial, value in answer.items()}
    return answer


def build_fiber_eliminant():
    first, second = build_reduced_quadratics()

    def coefficient(polynomial, z_degree):
        return {
            (x_degree, t_degree): value
            for (x_degree, degree, t_degree), value in polynomial.items()
            if degree == z_degree
        }

    a2, a1, a0 = (coefficient(first, degree) for degree in (2, 1, 0))
    b2, b1, b0 = (coefficient(second, degree) for degree in (2, 1, 0))
    zero = {}
    resultant = determinant(
        (
            (a2, a1, a0, zero),
            (zero, a2, a1, a0),
            (b2, b1, b0, zero),
            (zero, b2, b1, b0),
        ),
        2,
    )
    if min(x_degree for x_degree, _t_degree in resultant) != 1:
        raise AssertionError("unexpected cleared-resultant x valuation")
    divided = {
        (x_degree - 1, t_degree): value
        for (x_degree, t_degree), value in resultant.items()
    }
    return primitive_integer(divided)


def coefficients_in_x(polynomial):
    x_degree = max(first for first, _second in polynomial)
    answer = []
    for degree in range(x_degree + 1):
        t_degree = max(
            (second for first, second in polynomial if first == degree), default=0
        )
        coefficient = [0] * (t_degree + 1)
        for (first, second), value in polynomial.items():
            if first == degree:
                coefficient[second] = value
        answer.append(trim(coefficient))
    return answer


def divide_nonuniform_branch(coefficients):
    """Exactly divide G(x,t) by 3x-1."""
    quotient = [[0] for _ in range(len(coefficients) - 1)]
    quotient[-1] = divide_scalar(coefficients[-1], 3)
    for degree in range(len(quotient) - 1, 0, -1):
        quotient[degree - 1] = divide_scalar(
            polynomial_add(coefficients[degree], quotient[degree]), 3
        )
    if coefficients[0] != polynomial_negate(quotient[0]):
        raise AssertionError("fiber eliminant lost the 3x-1 factor")
    return quotient


def trim(polynomial):
    while len(polynomial) > 1 and not polynomial[-1]:
        polynomial.pop()
    return polynomial


def polynomial_add(left, right):
    answer = [0] * max(len(left), len(right))
    for index, value in enumerate(left):
        answer[index] += value
    for index, value in enumerate(right):
        answer[index] += value
    return trim(answer)


def polynomial_negate(polynomial):
    return [-value for value in polynomial]


def polynomial_multiply(left, right):
    if left == [0] or right == [0]:
        return [0]
    answer = [0] * (len(left) + len(right) - 1)
    for left_degree, left_value in enumerate(left):
        for right_degree, right_value in enumerate(right):
            answer[left_degree + right_degree] += left_value * right_value
    return trim(answer)


def divide_scalar(polynomial, scalar):
    if any(value % scalar for value in polynomial):
        raise AssertionError("nonintegral scalar division")
    return [value // scalar for value in polynomial]


def polynomial_divide_exact(dividend, divisor):
    dividend = trim(list(dividend))
    divisor = trim(list(divisor))
    if divisor == [1]:
        return dividend
    if divisor == [-1]:
        return polynomial_negate(dividend)
    if len(dividend) < len(divisor):
        if dividend != [0]:
            raise AssertionError("nonzero short exact division")
        return [0]
    quotient = [0] * (len(dividend) - len(divisor) + 1)
    leading = divisor[-1]
    for offset in range(len(quotient) - 1, -1, -1):
        value = dividend[offset + len(divisor) - 1]
        if value % leading:
            raise AssertionError("nonintegral polynomial quotient")
        value //= leading
        quotient[offset] = value
        for index, divisor_value in enumerate(divisor):
            dividend[offset + index] -= value * divisor_value
    if trim(dividend) != [0]:
        raise AssertionError("nonzero polynomial remainder")
    return trim(quotient)


def sylvester_resultant(first, second):
    first_degree = len(first) - 1
    second_degree = len(second) - 1
    size = first_degree + second_degree
    descending_first = list(reversed(first))
    descending_second = list(reversed(second))
    zero = [0]
    matrix = []
    for offset in range(second_degree):
        matrix.append(
            [zero[:] for _ in range(offset)]
            + [value[:] for value in descending_first]
            + [zero[:] for _ in range(second_degree - 1 - offset)]
        )
    for offset in range(first_degree):
        matrix.append(
            [zero[:] for _ in range(offset)]
            + [value[:] for value in descending_second]
            + [zero[:] for _ in range(first_degree - 1 - offset)]
        )

    previous = [1]
    sign = 1
    for pivot_index in range(size - 1):
        if matrix[pivot_index][pivot_index] == [0]:
            swap = next(
                row
                for row in range(pivot_index + 1, size)
                if matrix[row][pivot_index] != [0]
            )
            matrix[pivot_index], matrix[swap] = matrix[swap], matrix[pivot_index]
            sign *= -1
        pivot = matrix[pivot_index][pivot_index]
        for row in range(pivot_index + 1, size):
            for column in range(pivot_index + 1, size):
                numerator = polynomial_add(
                    polynomial_multiply(matrix[row][column], pivot),
                    polynomial_negate(
                        polynomial_multiply(
                            matrix[row][pivot_index], matrix[pivot_index][column]
                        )
                    ),
                )
                matrix[row][column] = polynomial_divide_exact(numerator, previous)
            matrix[row][pivot_index] = [0]
        previous = pivot
    answer = matrix[-1][-1]
    return polynomial_negate(answer) if sign < 0 else answer


def discriminant(coefficients):
    derivative = [
        [(degree + 1) * value for value in coefficients[degree + 1]]
        for degree in range(len(coefficients) - 1)
    ]
    return sylvester_resultant(coefficients, derivative)


def primitive_univariate(polynomial):
    content = 0
    for value in polynomial:
        content = gcd(content, abs(value))
    answer = [value // content for value in polynomial]
    if answer[-1] < 0:
        answer = polynomial_negate(answer)
    return answer


def divide_over_q(dividend, divisor):
    dividend = [Q(value) for value in dividend]
    divisor = [Q(value) for value in divisor]
    quotient = [Q(0)] * max(1, len(dividend) - len(divisor) + 1)
    while len(dividend) >= len(divisor):
        value = dividend[-1] / divisor[-1]
        offset = len(dividend) - len(divisor)
        quotient[offset] = value
        for index, divisor_value in enumerate(divisor):
            dividend[offset + index] -= value * divisor_value
        while dividend and not dividend[-1]:
            dividend.pop()
    return quotient, dividend


def main():
    eliminant = build_fiber_eliminant()
    degree_six = coefficients_in_x(eliminant)
    degree_five = divide_nonuniform_branch(degree_six)
    print(
        "FIBER_ELIMINANT",
        "x_degree", len(degree_six) - 1,
        "t_degree", max(len(value) - 1 for value in degree_six),
        "terms", len(eliminant),
    )
    print("NONUNIFORM_FACTOR 3*vr-1", "uniform_candidate_degree", len(degree_five) - 1)
    for name, coefficients in (("degree6", degree_six), ("degree5", degree_five)):
        projection = primitive_univariate(discriminant(coefficients))
        quotient, remainder = divide_over_q(projection, certificate.ELIMINATION)
        print(
            "DISCRIMINANT", name,
            "degree", len(projection) - 1,
            "terms", sum(value != 0 for value in projection),
            "RUR_divides", not remainder,
            "quotient_degree", len(quotient) - 1 if not remainder else None,
        )


if __name__ == "__main__":
    main()
