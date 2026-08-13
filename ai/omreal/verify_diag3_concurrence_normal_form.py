#!/usr/bin/env python3
"""Exact replay for the diagonal-3 concurrence normal form and ramification canary.

The structural reduction itself is elementary exterior algebra and is stated
in ``DIAG3_CONCURRENCE_NORMAL_FORM.md``.  This dependency-free checker pins
the six primitive occurrence support types and an exact real ramification
point in the generic independent-concurrence chart.
"""

from fractions import Fraction as Q
import hashlib
from itertools import combinations, permutations
from math import gcd, lcm
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "data"))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG3_concurrence_ramification_rur as certificate  # noqa: E402


SELECTED = (
    (0, 7, 14, 52),
    (10, 27, 32, 44),
    (8, 26, 40, 45),
)
EXPECTED_FACTORS = (5_563, 16_134, 19_284)
SUPPORT_TYPES = {
    36: ((1, 2, 3), (1, 2, 4), (3, 4, 5), (3, 6, 7)),
    38: ((1, 2, 3), (1, 2, 4), (3, 4, 5), (6, 7, 8)),
    48: ((1, 2, 3), (1, 4, 5), (2, 4, 6), (3, 5, 6)),
    49: ((1, 2, 3), (1, 4, 5), (2, 4, 6), (3, 5, 7)),
    50: ((1, 2, 3), (1, 4, 5), (2, 4, 6), (3, 7, 8)),
    51: ((1, 2, 3), (1, 4, 5), (2, 6, 7), (4, 6, 8)),
}
EXPECTED_DIGEST = "fad0e330d2502e6a95f2cbc365409ecb96e37f5c44ac603f51c3564348b885db"
EXPECTED_FACTOR_INTERVAL_DIGEST = (
    "f6132b7058b7cd2747e37979ef094a678e93d5c9e417a5821fd22de2d5858923"
)
DYADIC_BITS = 96


def trim(polynomial):
    polynomial = list(polynomial)
    while len(polynomial) > 1 and polynomial[-1] == 0:
        polynomial.pop()
    return polynomial


def add(left, right):
    answer = [0] * max(len(left), len(right))
    for index in range(len(answer)):
        answer[index] = (
            (left[index] if index < len(left) else 0)
            + (right[index] if index < len(right) else 0)
        )
    return trim(answer)


def negate(polynomial):
    return [-coefficient for coefficient in polynomial]


def subtract(left, right):
    return add(left, negate(right))


def multiply(left, right):
    answer = [0] * (len(left) + len(right) - 1)
    for left_degree, left_coefficient in enumerate(left):
        if not left_coefficient:
            continue
        for right_degree, right_coefficient in enumerate(right):
            if right_coefficient:
                answer[left_degree + right_degree] += (
                    left_coefficient * right_coefficient
                )
    return trim(answer)


def scale(polynomial, scalar):
    return trim([scalar * coefficient for coefficient in polynomial])


def power(polynomial, exponent):
    answer = [1]
    while exponent:
        if exponent & 1:
            answer = multiply(answer, polynomial)
        polynomial = multiply(polynomial, polynomial)
        exponent //= 2
    return answer


def primitive_remainder(dividend, divisor):
    """Integer pseudo-remainder; zero iff the Q-polynomial remainder is zero."""

    dividend = trim(dividend)
    divisor = trim(divisor)
    leading = divisor[-1]
    while len(dividend) >= len(divisor) and dividend != [0]:
        offset = len(dividend) - len(divisor)
        coefficient = dividend[-1]
        dividend = scale(dividend, leading)
        for index, value in enumerate(divisor):
            dividend[index + offset] -= coefficient * value
        dividend = trim(dividend)
    return dividend


def evaluate(polynomial, value):
    answer = 0
    for coefficient in reversed(polynomial):
        answer = answer * value + coefficient
    return answer


def sign_variations(coefficients):
    signs = [coefficient > 0 for coefficient in coefficients if coefficient]
    return sum(left != right for left, right in zip(signs, signs[1:]))


def descartes_transform(polynomial, left, right):
    """Map a real interval to t>0 and return the cleared polynomial."""

    degree = len(polynomial) - 1
    answer = [Q(0)]
    if left is None:
        # x = right - t maps t>0 onto (-infinity,right).
        for exponent, coefficient in enumerate(polynomial):
            answer = add(
                answer,
                scale(power([right, Q(-1)], exponent), coefficient),
            )
    elif right is None:
        # x = left + t maps t>0 onto (left,infinity).
        for exponent, coefficient in enumerate(polynomial):
            answer = add(
                answer,
                scale(power([left, Q(1)], exponent), coefficient),
            )
    else:
        # x=(left+right*t)/(1+t), cleared by (1+t)^degree.
        for exponent, coefficient in enumerate(polynomial):
            term = multiply(
                power([left, right], exponent),
                power([Q(1), Q(1)], degree - exponent),
            )
            answer = add(answer, scale(term, coefficient))
    return answer


def matrix_rank(matrix):
    matrix = [[Q(value) for value in row] for row in matrix]
    rank = 0
    for column in range(len(matrix[0])):
        pivot = next(
            (row for row in range(rank, len(matrix)) if matrix[row][column]),
            None,
        )
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        scalar = matrix[rank][column]
        matrix[rank] = [value / scalar for value in matrix[rank]]
        for row in range(len(matrix)):
            if row == rank or not matrix[row][column]:
                continue
            scalar = matrix[row][column]
            matrix[row] = [
                left - scalar * right
                for left, right in zip(matrix[row], matrix[rank])
            ]
        rank += 1
        if rank == len(matrix):
            break
    return rank


def sparse_add(left, right):
    answer = dict(left)
    for monomial, coefficient in right.items():
        answer[monomial] = answer.get(monomial, 0) + coefficient
        if not answer[monomial]:
            del answer[monomial]
    return answer


def sparse_scale(polynomial, scalar):
    return {
        monomial: scalar * coefficient
        for monomial, coefficient in polynomial.items()
        if scalar * coefficient
    }


def sparse_multiply(left, right):
    answer = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial = tuple(
                x + y for x, y in zip(left_monomial, right_monomial)
            )
            answer[monomial] = answer.get(monomial, 0) + (
                left_coefficient * right_coefficient
            )
    return {key: value for key, value in answer.items() if value}


def sparse_derivative(polynomial, variable):
    answer = {}
    for monomial, coefficient in polynomial.items():
        if not monomial[variable]:
            continue
        derived = list(monomial)
        scalar = derived[variable]
        derived[variable] -= 1
        answer[tuple(derived)] = coefficient * scalar
    return answer


def normalize_sparse(polynomial):
    content = 0
    for coefficient in polynomial.values():
        content = gcd(content, abs(coefficient))
    answer = {monomial: value // content for monomial, value in polynomial.items()}
    if answer[max(answer)] < 0:
        answer = sparse_scale(answer, -1)
    return answer


def sparse_determinant4(matrix):
    answer = {}
    for permutation in permutations(range(4)):
        inversions = sum(
            permutation[left] > permutation[right]
            for left in range(4)
            for right in range(left + 1, 4)
        )
        term = {(0, 0, 0, 0, 0): -1 if inversions & 1 else 1}
        for row in range(4):
            term = sparse_multiply(term, matrix[row][permutation[row]])
        answer = sparse_add(answer, term)
    return answer


class RationalFunction:
    """Univariate rational function; cancellation is intentionally deferred."""

    def __init__(self, numerator, denominator=(1,)):
        self.numerator = trim(numerator)
        self.denominator = trim(denominator)

    def __add__(self, other):
        other = rational(other)
        return RationalFunction(
            add(
                multiply(self.numerator, other.denominator),
                multiply(other.numerator, self.denominator),
            ),
            multiply(self.denominator, other.denominator),
        )

    __radd__ = __add__

    def __neg__(self):
        return RationalFunction(negate(self.numerator), self.denominator)

    def __sub__(self, other):
        return self + -rational(other)

    def __rsub__(self, other):
        return rational(other) - self

    def __mul__(self, other):
        other = rational(other)
        return RationalFunction(
            multiply(self.numerator, other.numerator),
            multiply(self.denominator, other.denominator),
        )

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = rational(other)
        return RationalFunction(
            multiply(self.numerator, other.denominator),
            multiply(self.denominator, other.numerator),
        )

    def __rtruediv__(self, other):
        return rational(other) / self


def rational(value):
    if isinstance(value, RationalFunction):
        return value
    if isinstance(value, Q):
        return RationalFunction([value.numerator], [value.denominator])
    return RationalFunction([value])


class Interval:
    """Closed rational interval with outward-exact elementary arithmetic."""

    def __init__(self, lower, upper=None):
        self.lower = Q(lower)
        self.upper = Q(lower if upper is None else upper)
        if self.lower > self.upper:
            raise AssertionError("reversed interval")

    def __add__(self, other):
        other = interval(other)
        return Interval(self.lower + other.lower, self.upper + other.upper)

    __radd__ = __add__

    def __neg__(self):
        return Interval(-self.upper, -self.lower)

    def __sub__(self, other):
        return self + -interval(other)

    def __rsub__(self, other):
        return interval(other) - self

    def __mul__(self, other):
        other = interval(other)
        products = (
            self.lower * other.lower,
            self.lower * other.upper,
            self.upper * other.lower,
            self.upper * other.upper,
        )
        return Interval(min(products), max(products))

    __rmul__ = __mul__

    def __truediv__(self, other):
        other = interval(other)
        if other.contains_zero():
            raise ZeroDivisionError("interval denominator contains zero")
        return self * Interval(1 / other.upper, 1 / other.lower)

    def __rtruediv__(self, other):
        return interval(other) / self

    def contains_zero(self):
        return self.lower <= 0 <= self.upper


def interval(value):
    return value if isinstance(value, Interval) else Interval(value)


def interval_evaluate(polynomial, value):
    answer = Interval(0)
    for coefficient in reversed(polynomial):
        answer = answer * value + coefficient
    return answer


def collinearity(first, second, triple):
    first_index, second_index, third_index = triple
    return (
        (first[second_index] - first[first_index])
        * (second[third_index] - second[first_index])
        - (first[third_index] - first[first_index])
        * (second[second_index] - second[first_index])
    )


def determinant(matrix):
    size = len(matrix)
    answer = matrix[0][0] * 0
    for permutation in permutations(range(size)):
        inversions = sum(
            permutation[left] > permutation[right]
            for left in range(size)
            for right in range(left + 1, size)
        )
        term = -1 if inversions & 1 else 1
        for row in range(size):
            term = term * matrix[row][permutation[row]]
        answer = answer + term
    return answer


def dyadic_interval(value):
    scale_value = 1 << DYADIC_BITS
    lower = (value.lower * scale_value).numerator // (
        value.lower * scale_value
    ).denominator
    scaled_upper = value.upper * scale_value
    upper = -((-scaled_upper.numerator) // scaled_upper.denominator)
    return lower, upper


def dyadic_add(left, right):
    return left[0] + right[0], left[1] + right[1]


def dyadic_negate(value):
    return -value[1], -value[0]


def dyadic_multiply(left, right):
    products = (
        left[0] * right[0],
        left[0] * right[1],
        left[1] * right[0],
        left[1] * right[1],
    )
    return min(products), max(products)


def dyadic_determinant(matrix):
    size = len(matrix)
    answer = (0, 0)
    for permutation in permutations(range(size)):
        inversions = sum(
            permutation[left] > permutation[right]
            for left in range(size)
            for right in range(left + 1, size)
        )
        term = (1, 1)
        for row in range(size):
            term = dyadic_multiply(term, matrix[row][permutation[row]])
        answer = dyadic_add(
            answer, dyadic_negate(term) if inversions & 1 else term
        )
    return answer


def dyadic_plane_normal(points, triple):
    answer = []
    for omitted in range(4):
        minor = [
            [points[column][row] for column in triple]
            for row in range(4)
            if row != omitted
        ]
        value = dyadic_determinant(minor)
        answer.append(dyadic_negate(value) if omitted & 1 else value)
    return tuple(answer)


def verify_no_extra_factor(points, occurrences, occurrence_factor):
    points = tuple(
        tuple(dyadic_interval(entry) for entry in point) for point in points
    )
    normals = tuple(
        dyadic_plane_normal(points, triple) for triple in labeled.TRIPLES
    )
    representatives = [None] * 26_740
    for occurrence in occurrences:
        factor = occurrence_factor[occurrence]
        if representatives[factor] is None:
            representatives[factor] = occurrence
    if any(occurrence is None for occurrence in representatives):
        raise AssertionError("factor without an occurrence representative")
    suspects = []
    minimum_positive_margin = None
    semantic = hashlib.sha256()
    semantic.update(b"diag3-concurrence-all-factor-interval-v1\0")
    for factor, occurrence in enumerate(representatives):
        value = dyadic_determinant(
            [normals[triple_index] for triple_index in occurrence]
        )
        semantic.update(repr((factor, occurrence, value)).encode("ascii"))
        if value[0] <= 0 <= value[1]:
            suspects.append((factor, occurrence))
            continue
        margin = min(abs(value[0]), abs(value[1]))
        minimum_positive_margin = (
            margin
            if minimum_positive_margin is None
            else min(minimum_positive_margin, margin)
        )
    if tuple(factor for factor, _occurrence in suspects) != EXPECTED_FACTORS:
        raise AssertionError(f"unexpected residual-factor suspects: {suspects}")
    return suspects, minimum_positive_margin, semantic.hexdigest()


def verify_support_ranks():
    generic_u = (2, 3, 5, 7, 11, 13, 17, 19)
    for kind, support in SUPPORT_TYPES.items():
        rows = []
        for a, b, c in support:
            a -= 1
            b -= 1
            c -= 1
            row = [0] * 8
            row[a] = generic_u[c] - generic_u[b]
            row[b] = generic_u[a] - generic_u[c]
            row[c] = generic_u[b] - generic_u[a]
            rows.append(row)
        if matrix_rank(rows) != 4:
            raise AssertionError(f"support type {kind} lost generic rank four")


def verify_sparse_system():
    equations = [dict(polynomial) for polynomial in certificate.SYSTEM]
    jacobian = [
        [sparse_derivative(equation, variable) for variable in range(4)]
        for equation in equations[:4]
    ]
    derived_ramification = normalize_sparse(sparse_determinant4(jacobian))
    if derived_ramification != normalize_sparse(equations[4]):
        raise AssertionError("stored ramification is not the fiber Jacobian")


def verify_rur():
    elimination = list(certificate.ELIMINATION)
    derivative = [
        exponent * elimination[exponent]
        for exponent in range(1, len(elimination))
    ]
    parameters = certificate.PARAMETERS

    common_scalar = 1
    for _polynomial, denominator in parameters:
        common_scalar = lcm(common_scalar, denominator)
    common_denominator = scale(derivative, common_scalar)
    coordinate_numerators = [
        scale(polynomial, -common_scalar // denominator)
        for polynomial, denominator in parameters
    ]
    for terms in certificate.SYSTEM:
        coordinate_degree = max(sum(monomial[:4]) for monomial, _ in terms)
        substituted = [0]
        for monomial, coefficient in terms:
            term = [coefficient]
            for variable, exponent in enumerate(monomial[:4]):
                term = multiply(
                    term, power(coordinate_numerators[variable], exponent)
                )
            term = multiply(term, [0] * monomial[4] + [1])
            term = multiply(
                term,
                power(
                    common_denominator,
                    coordinate_degree - sum(monomial[:4]),
                ),
            )
            substituted = add(substituted, term)
        if primitive_remainder(substituted, elimination) != [0]:
            raise AssertionError("RUR does not annihilate the stored system")

    # Descartes transformations partition the entire real line.  Variation
    # one intervals contain one root; variation zero intervals contain none.
    bounds = (
        None,
        Q(-3, 4),
        Q(-1, 2),
        Q(-1, 4),
        Q(-1, 50),
        Q(-1, 100),
        Q(0),
        Q(3, 1000),
        Q(1, 10),
        Q(2, 5),
        Q(7, 10),
        Q(1),
        Q(2),
        Q(3),
        None,
    )
    expected_variations = (0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0)
    variations = tuple(
        sign_variations(descartes_transform(elimination, left, right))
        for left, right in zip(bounds, bounds[1:])
    )
    if variations != expected_variations:
        raise AssertionError(f"real-root partition changed: {variations}")
    if any(
        evaluate(elimination, bound) == 0
        for bound in bounds
        if bound is not None
    ):
        raise AssertionError("a Descartes partition endpoint is a root")

    # Narrowly isolate the real root used for the uniform ramification point.
    root = Interval(
        Q(7_879_209_203_118_614, 10**16),
        Q(7_879_209_203_118_616, 10**16),
    )
    if evaluate(elimination, root.lower) * evaluate(elimination, root.upper) >= 0:
        raise AssertionError("the ramification interval does not change sign")
    derivative_interval = interval_evaluate(derivative, root)
    if derivative_interval.contains_zero():
        raise AssertionError("the ramification root is not monotonically isolated")

    coordinates = [
        -interval_evaluate(polynomial, root)
        / (denominator * derivative_interval)
        for polynomial, denominator in parameters
    ]
    vr, vs, wr, ws = coordinates
    u = [
        Interval(0),
        Interval(1),
        Interval(Q(4, 5)),
        Interval(Q(-3, 4)),
        Interval(Q(3, 20)),
        Interval(Q(1, 4)),
        Interval(Q(1, 3)),
        root,
    ]
    v = [
        Interval(0),
        Interval(1),
        (315 * root * vr - 360 * root - 252 * vr + 527 * vs + 288)
        / (85 * (4 * root + 3)),
        9 * (7 * vr - 8) / 68,
        9 * vr / 20,
        vs / (4 * root),
        vr,
        vs,
    ]
    w = [
        Interval(0),
        Interval(1),
        (33 * wr - 7) / 5,
        (
            204 * root * wr
            - 44 * root
            + 153 * wr
            - 144 * ws
            - 33
        )
        / (8 * (20 * root - 3)),
        (51 * wr - 11) / 40,
        Interval(Q(1, 4)),
        wr,
        ws,
    ]

    # The same incidence equations vanish exactly in Q[t]/(elimination).
    t_rat = RationalFunction([0, 1])
    exact_coordinates = [
        RationalFunction(negate(polynomial), scale(derivative, denominator))
        for polynomial, denominator in parameters
    ]
    vr_rat, vs_rat, wr_rat, ws_rat = exact_coordinates
    u_rat = [
        rational(0),
        rational(1),
        rational(Q(4, 5)),
        rational(Q(-3, 4)),
        rational(Q(3, 20)),
        rational(Q(1, 4)),
        rational(Q(1, 3)),
        t_rat,
    ]
    v_rat = [
        rational(0),
        rational(1),
        (
            315 * t_rat * vr_rat
            - 360 * t_rat
            - 252 * vr_rat
            + 527 * vs_rat
            + 288
        )
        / (85 * (4 * t_rat + 3)),
        9 * (7 * vr_rat - 8) / 68,
        9 * vr_rat / 20,
        vs_rat / (4 * t_rat),
        vr_rat,
        vs_rat,
    ]
    w_rat = [
        rational(0),
        rational(1),
        (33 * wr_rat - 7) / 5,
        (
            204 * t_rat * wr_rat
            - 44 * t_rat
            + 153 * wr_rat
            - 144 * ws_rat
            - 33
        )
        / (8 * (20 * t_rat - 3)),
        (51 * wr_rat - 11) / 40,
        rational(Q(1, 4)),
        wr_rat,
        ws_rat,
    ]
    colored = (
        (v_rat, w_rat, SELECTED[0]),
        (u_rat, w_rat, SELECTED[1]),
        (u_rat, v_rat, SELECTED[2]),
    )
    for first, second, support in colored:
        for triple_index in support:
            equation = collinearity(
                first, second, labeled.TRIPLES[triple_index]
            )
            if primitive_remainder(equation.numerator, elimination) != [0]:
                raise AssertionError("an exact incidence equation is nonzero")

    # Every one of the 70 parent brackets is separated from zero.
    points = list(zip(u, v, w, [Interval(1)] * 8))
    bracket_margins = []
    for indices in combinations(range(8), 4):
        bracket = determinant(
            [[points[column][row] for column in indices] for row in range(4)]
        )
        if bracket.contains_zero():
            raise AssertionError(f"parent bracket {indices} is not separated")
        bracket_margins.append(min(abs(bracket.lower), abs(bracket.upper)))

    # The raw four-bilinear fiber Jacobian has rank at least three.  The
    # stored exact determinant gives rank at most three at the algebraic root.
    dv = [
        (Interval(0), Interval(0)),
        (Interval(0), Interval(0)),
        (
            (315 * root - 252) / (85 * (4 * root + 3)),
            527 / (85 * (4 * root + 3)),
        ),
        (Interval(Q(63, 68)), Interval(0)),
        (Interval(Q(9, 20)), Interval(0)),
        (Interval(0), 1 / (4 * root)),
        (Interval(1), Interval(0)),
        (Interval(0), Interval(1)),
    ]
    dw = [
        (Interval(0), Interval(0)),
        (Interval(0), Interval(0)),
        (Interval(Q(33, 5)), Interval(0)),
        (
            (204 * root + 153) / (8 * (20 * root - 3)),
            -144 / (8 * (20 * root - 3)),
        ),
        (Interval(Q(51, 40)), Interval(0)),
        (Interval(0), Interval(0)),
        (Interval(1), Interval(0)),
        (Interval(0), Interval(1)),
    ]
    jacobian = []
    for triple_index in SELECTED[0]:
        a, b, c = labeled.TRIPLES[triple_index]
        row = []
        for variable in range(2):
            row.append(
                (dv[b][variable] - dv[a][variable]) * (w[c] - w[a])
                - (dv[c][variable] - dv[a][variable]) * (w[b] - w[a])
            )
        for variable in range(2):
            row.append(
                (v[b] - v[a]) * (dw[c][variable] - dw[a][variable])
                - (v[c] - v[a]) * (dw[b][variable] - dw[a][variable])
            )
        jacobian.append(row)
    rank_minor = determinant([row[:3] for row in jacobian[:3]])
    if rank_minor.contains_zero():
        raise AssertionError("fiber Jacobian rank-three minor is not separated")

    return root, coordinates, min(bracket_margins), rank_minor, points


def main():
    payload = (
        certificate.ELIMINATION,
        certificate.PARAMETERS,
        certificate.SYSTEM,
    )
    digest = hashlib.sha256(repr(payload).encode("ascii")).hexdigest()
    if digest != EXPECTED_DIGEST or digest != certificate.SEMANTIC_SHA256:
        raise AssertionError(f"RUR semantic digest changed: {digest}")

    occurrences, occurrence_factor, _polynomials = labeled.factor_polynomials()
    if tuple(occurrence_factor[support] for support in SELECTED) != EXPECTED_FACTORS:
        raise AssertionError("selected occurrence/factor mapping changed")
    if any(support not in occurrences for support in SELECTED):
        raise AssertionError("selected occurrence is absent")

    verify_support_ranks()
    verify_sparse_system()
    root, coordinates, bracket_margin, rank_minor, points = verify_rur()
    suspects, factor_margin, factor_digest = verify_no_extra_factor(
        points, occurrences, occurrence_factor
    )
    if factor_digest != EXPECTED_FACTOR_INTERVAL_DIGEST:
        raise AssertionError(
            f"all-factor interval digest changed: {factor_digest}"
        )

    print("PASS six primitive occurrence supports have generic kernel rank four")
    print("PASS selected occurrences map to factors 5563,16134,19284")
    print("PASS stored degree-20 branch: four incidences plus fiber determinant")
    print("PASS Descartes partition: exactly six distinct real roots")
    print(
        "PASS uniform real corank-one ramification: t in "
        f"[{float(root.lower):.16g},{float(root.upper):.16g}], "
        f"min_bracket_margin>{float(bracket_margin):.6g}"
    )
    print(
        "PASS fiber Jacobian rank exactly three: minor in "
        f"[{float(rank_minor.lower):.6g},{float(rank_minor.upper):.6g}]"
    )
    print(
        "PASS all-factor separation at 96 dyadic bits: only "
        f"{tuple(factor for factor, _occurrence in suspects)} vanish, "
        f"minimum_nonzero_margin_bits={factor_margin.bit_length()}"
    )
    print(f"FACTOR_INTERVAL_SEMANTIC {factor_digest}")
    print(
        "COORD vr,vs,wr,ws "+ " ".join(
            f"[{float(value.lower):.12g},{float(value.upper):.12g}]"
            for value in coordinates
        )
    )
    print(f"SEMANTIC {EXPECTED_DIGEST}")
    print(
        "CAVEAT internal ramification no-go only; component noncompactness "
        "and concurrence-frontier attachment are not proved"
    )


if __name__ == "__main__":
    main()
