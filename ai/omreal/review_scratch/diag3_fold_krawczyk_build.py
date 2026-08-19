#!/usr/bin/env python3
"""Build/scout pseudo-arclength Krawczyk boxes for the hard D3 fold.

Discovery helper only.  It uses SciPy for approximate centers, but every
reported box test itself uses exact rational interval arithmetic.  A tracked
certificate must store the accepted rational boxes and replay them without
SciPy before it can support a theorem claim.
"""

from fractions import Fraction as Q
import sys

import numpy as np
from scipy.optimize import root

sys.path[:0] = ["ai/omreal", "ai/omreal/data"]
import DIAG3_concurrence_ramification_rur as certificate  # noqa: E402
import verify_diag3_concurrence_normal_form as base  # noqa: E402


Interval = base.Interval
DENOMINATOR = 10**13
ZERO = (0, 0, 0, 0, 0)


def rational(value):
    return Q(round(float(value) * DENOMINATOR), DENOMINATOR)


def exact_coordinate(value):
    """Retain certificate rationals; rationalize discovery floats once."""
    return value if isinstance(value, Q) else rational(value)


def add(left, right):
    answer = dict(left)
    for monomial, coefficient in right.items():
        answer[monomial] = answer.get(monomial, 0) + coefficient
    return {monomial: value for monomial, value in answer.items() if value}


def multiply(left, right):
    answer = {}
    for first, first_value in left.items():
        for second, second_value in right.items():
            monomial = tuple(a + b for a, b in zip(first, second))
            answer[monomial] = answer.get(monomial, 0) + first_value * second_value
    return {monomial: value for monomial, value in answer.items() if value}


def power(polynomial, exponent):
    answer = {ZERO: Q(1)}
    for _ in range(exponent):
        answer = multiply(answer, polynomial)
    return answer


def constant(value):
    return {} if not value else {ZERO: Q(value)}


def variable(index):
    exponent = [0] * 5
    exponent[index] = 1
    return {tuple(exponent): Q(1)}


def scale(polynomial, scalar):
    return {monomial: Q(scalar) * value for monomial, value in polynomial.items()}


def determinant4(matrix):
    from itertools import permutations
    answer = {}
    for permutation in permutations(range(4)):
        inversions = sum(
            permutation[left] > permutation[right]
            for left in range(4) for right in range(left + 1, 4)
        )
        term = constant(-1 if inversions & 1 else 1)
        for row in range(4):
            term = multiply(term, matrix[row][permutation[row]])
        answer = add(answer, term)
    return answer


def target_numerator(target):
    """Cleared numerator of [2678] or [2467] in the concurrence slice."""
    vr, vs, wr, ws, t = (variable(index) for index in range(5))
    one = constant(1)
    p2 = (one, one, one, one)
    p6 = (t, vs, t, scale(t, 4))  # column scaled by 4t
    p7 = (constant(Q(1, 3)), vr, wr, one)
    if target == 54:  # [2678]
        p8 = (t, vs, ws, one)
        columns = (p2, p6, p7, p8)
    elif target == 48:  # [2467]
        twenty_t_minus_three = add(scale(t, 20), constant(-3))
        p4 = (
            scale(twenty_t_minus_three, -102),
            scale(
                multiply(add(scale(vr, 7), constant(-8)), twenty_t_minus_three),
                18,
            ),
            scale(
                add(
                    add(scale(multiply(t, wr), 204), scale(t, -44)),
                    add(scale(wr, 153), add(scale(ws, -144), constant(-33))),
                ),
                17,
            ),
            scale(twenty_t_minus_three, 136),
        )
        columns = (p2, p4, p6, p7)
    else:
        raise AssertionError(target)
    return determinant4([[columns[column][row] for column in range(4)] for row in range(4)])


def transform(polynomial, midpoint, tangent, parameter, unknown):
    """Substitute z=midpoint+tangent*s+y in centered local coordinates."""
    forms = []
    for old in range(5):
        form = {
            ZERO: exact_coordinate(midpoint[old]),
            (0, 0, 0, 0, 1): Q(
                1 if old == parameter else exact_coordinate(tangent[old])
            ),
        }
        if old != parameter:
            exponent = [0] * 5
            exponent[unknown.index(old)] = 1
            form[tuple(exponent)] = Q(1)
        forms.append(form)
    answer = {}
    for monomial, coefficient in polynomial:
        term = {ZERO: Q(coefficient)}
        for form, exponent in zip(forms, monomial):
            term = multiply(term, power(form, exponent))
        answer = add(answer, term)
    return answer


def interval_evaluate(polynomial, variables, parameter, derivative=None):
    coefficients = [Interval(0) for _ in range(1 + max(m[4] for m in polynomial))]
    for monomial, scalar in polynomial.items():
        if derivative is not None and not monomial[derivative]:
            continue
        value = Interval(scalar * (monomial[derivative] if derivative is not None else 1))
        for index in range(4):
            for _ in range(monomial[index] - (index == derivative)):
                value *= variables[index]
        coefficients[monomial[4]] += value
    answer = Interval(0)
    for coefficient in reversed(coefficients):
        answer = answer * parameter + coefficient
    return answer


def matrix_vector(matrix, vector):
    return [
        sum((matrix[row][column] * vector[column] for column in range(len(vector))), Interval(0))
        for row in range(len(matrix))
    ]


def matrix_multiply(left, right):
    return [
        [
            sum((left[row][k] * right[k][column] for k in range(len(right))), Interval(0))
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def inverse_rational(matrix):
    """Exact Gauss--Jordan inverse of a small rational matrix."""
    size = len(matrix)
    augmented = [
        [Q(value) for value in row]
        + [Q(1 if row_index == column else 0) for column in range(size)]
        for row_index, row in enumerate(matrix)
    ]
    for column in range(size):
        pivot = next(row for row in range(column, size) if augmented[row][column])
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scalar = augmented[column][column]
        augmented[column] = [value / scalar for value in augmented[column]]
        for row in range(size):
            if row == column or not augmented[row][column]:
                continue
            scalar = augmented[row][column]
            augmented[row] = [
                left - scalar * right
                for left, right in zip(augmented[row], augmented[column])
            ]
    return [row[size:] for row in augmented]


def numerical_system(point):
    return np.array([
        sum(
            float(coefficient) * np.prod([value**exponent for value, exponent in zip(point, monomial)])
            for monomial, coefficient in polynomial
        )
        for polynomial in certificate.SYSTEM[:4]
    ])


def certify_segment(left, right, radius, parameter):
    # Rationalize the shared vertices first.  Adjacent cells then have
    # literally identical endpoint predictors, which is needed by a later
    # dependency-free chain replay.
    left_q = [rational(value) for value in left]
    right_q = [rational(value) for value in right]
    midpoint_q = [(a + b) / 2 for a, b in zip(left_q, right_q)]
    delta_q = [b - a for a, b in zip(left_q, right_q)]
    half_width_q = abs(delta_q[parameter]) / 2
    unknown = [index for index in range(5) if index != parameter]
    tangent_q = [Q(0)] * 5
    tangent_q[parameter] = Q(1)
    for index in unknown:
        tangent_q[index] = delta_q[index] / delta_q[parameter]
    tangent = np.array([float(value) for value in tangent_q])
    transformed = [
        transform(polynomial, midpoint_q, tangent_q, parameter, unknown)
        for polynomial in certificate.SYSTEM[:4]
    ]
    parameter_interval = Interval(-half_width_q, half_width_q)
    box = [Interval(-radius, radius) for _ in range(4)]
    jacobian = [
        [interval_evaluate(polynomial, box, parameter_interval, column) for column in range(4)]
        for polynomial in transformed
    ]
    midpoint_jacobian = [
        [
            interval_evaluate(
                polynomial, [Interval(0)] * 4, Interval(0), column
            ).lower
            for column in range(4)
        ]
        for polynomial in transformed
    ]
    preconditioner = [
        [Interval(value) for value in row]
        for row in inverse_rational(midpoint_jacobian)
    ]
    midpoint_values = [
        interval_evaluate(polynomial, [Interval(0)] * 4, parameter_interval)
        for polynomial in transformed
    ]
    center = [-value for value in matrix_vector(preconditioner, midpoint_values)]
    product = matrix_multiply(preconditioner, jacobian)
    remainder = [
        [Interval(1 if row == column else 0) - product[row][column] for column in range(4)]
        for row in range(4)
    ]
    correction = matrix_vector(remainder, box)
    image = [center[index] + correction[index] for index in range(4)]
    success = all(
        box[index].lower < image[index].lower
        and image[index].upper < box[index].upper
        for index in range(4)
    )
    size = max(max(abs(float(value.lower)), abs(float(value.upper))) for value in image)
    original = []
    for old in range(5):
        value = Interval(midpoint_q[old]) + tangent_q[old] * parameter_interval
        if old != parameter:
            value += image[unknown.index(old)]
        original.append(value)
    local = (midpoint_q, tangent_q, unknown, parameter_interval, image)
    return success, size, parameter, original, local


def target_value(target, local, endpoint=None):
    midpoint, tangent, unknown, parameter_interval, image = local
    transformed = transform(
        tuple(target_numerator(target).items()),
        midpoint,
        tangent,
        next(index for index, value in enumerate(tangent) if value == 1 and index not in unknown),
        unknown,
    )
    if endpoint is not None:
        parameter_interval = Interval(
            parameter_interval.lower if endpoint < 0 else parameter_interval.upper
        )
    return interval_evaluate(transformed, image, parameter_interval)


def parent_brackets(point):
    vr, vs, wr, ws, t = point
    u = (
        Interval(0), Interval(1), Interval(Q(4, 5)), Interval(Q(-3, 4)),
        Interval(Q(3, 20)), Interval(Q(1, 4)), Interval(Q(1, 3)), t,
    )
    v = (
        Interval(0), Interval(1),
        (315 * t * vr - 360 * t - 252 * vr + 527 * vs + 288)
        / (85 * (4 * t + 3)),
        9 * (7 * vr - 8) / 68, 9 * vr / 20, vs / (4 * t), vr, vs,
    )
    w = (
        Interval(0), Interval(1), (33 * wr - 7) / 5,
        (204 * t * wr - 44 * t + 153 * wr - 144 * ws - 33)
        / (8 * (20 * t - 3)),
        (51 * wr - 11) / 40, Interval(Q(1, 4)), wr, ws,
    )
    points = tuple(zip(u, v, w, (Interval(1),) * 8))
    from itertools import combinations
    return tuple(
        base.determinant(
            [[points[column][row] for column in indices] for row in range(4)]
        )
        for indices in combinations(range(8), 4)
    )


def numerical_branch(sign, endpoint, count=160):
    fold_t = 0.7879209203118615
    fold = np.array([
        -0.19918615935098,
        -0.20160217122091,
        0.18281515029306,
        0.34045732156583,
        fold_t,
    ])
    epsilon = 10**-8
    # Uniformity in sqrt(t_fold-t) resolves the fold without tiny t-boxes.
    root_parameters = np.linspace(np.sqrt(fold_t - endpoint), np.sqrt(epsilon), count + 1)
    times = fold_t - root_parameters**2
    numerical_jacobian = np.column_stack([
        (
            numerical_system(fold + np.eye(5)[column] * 1e-6)
            - numerical_system(fold - np.eye(5)[column] * 1e-6)
        ) / 2e-6
        for column in range(5)
    ])
    tangent = np.linalg.svd(numerical_jacobian)[2][-1]
    tangent /= tangent[3]
    guess = fold + sign * np.sqrt(2 * epsilon / 53.18989689) * tangent
    guess[4] = times[-1]
    solution = root(lambda x: numerical_system(np.r_[x, times[-1]]), guess[:4], tol=1e-12).x
    points = {times[-1]: np.r_[solution, times[-1]]}
    for time in reversed(times[:-1]):
        solution = root(lambda x: numerical_system(np.r_[x, time]), solution, tol=1e-12).x
        points[time] = np.r_[solution, time]
    return times, points


def main():
    near_fold = {}
    for sign, endpoint, parameter, target in (
        (-1, 0.75420, 0, 54),
        (1, 0.77949, 0, 48),
    ):
        times, points = numerical_branch(sign, endpoint)
        near_fold[sign] = points[times[-1]]
        for radius in (Q(1, 10**7), Q(1, 10**6), Q(1, 10**5), Q(1, 10**4)):
            failures = 0
            maximum = 0
            parameters = {}
            for left_time, right_time in zip(times[:-1], times[1:]):
                success, size, used_parameter, _point, _local = certify_segment(
                    points[left_time], points[right_time], radius, parameter
                )
                failures += not success
                maximum = max(maximum, size)
                parameters[used_parameter] = parameters.get(used_parameter, 0) + 1
            print(sign, float(radius), "failures", failures, "max", maximum, "parameters", parameters)
        crossing = []
        failures = 0
        radius_histogram = {}
        for index, (left_time, right_time) in enumerate(zip(times[:-1], times[1:])):
            success = False
            for radius in (
                Q(1, 10**9), Q(2, 10**9), Q(5, 10**9),
                Q(1, 10**8), Q(2, 10**8), Q(5, 10**8),
                Q(1, 10**7), Q(2, 10**7), Q(5, 10**7),
                Q(1, 10**6), Q(2, 10**6), Q(5, 10**6),
                Q(1, 10**5),
            ):
                success, _size, _used, point, local = certify_segment(
                    points[left_time], points[right_time], radius, parameter
                )
                if success:
                    radius_histogram[str(radius)] = radius_histogram.get(str(radius), 0) + 1
                    break
            failures += not success
            brackets = parent_brackets(point)
            bad = [number for number, value in enumerate(brackets) if value.contains_zero()]
            if bad:
                crossing.append((index, bad))
            if any(number != target for number in bad):
                raise AssertionError((sign, index, bad))
            exact_target = target_value(target, local)
            if exact_target.contains_zero() and target not in bad:
                raise AssertionError("target numerator/determinant disagreement")
            if exact_target.contains_zero():
                crossing[-1] = (index, bad, "numerator")
                left_target = target_value(target, local, -1)
                right_target = target_value(target, local, 1)
                crossing[-1] += (
                    (float(left_target.lower), float(left_target.upper)),
                    (float(right_target.lower), float(right_target.upper)),
                )
        print(
            sign, "parent crossings", crossing, "failures", failures,
            "radii", radius_histogram,
        )
    success, size, parameter, _point, _local = certify_segment(
        near_fold[-1], near_fold[1], Q(1, 10**6), 0
    )
    print("fold bridge", success, "max", size, "parameter", parameter)


if __name__ == "__main__":
    main()
