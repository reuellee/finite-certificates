#!/usr/bin/env python3
"""Exact internal discriminant wall for a hard residual-factor triple.

Graph a type-50 factor in ``d`` and a second factor in ``a``.  The last
factor becomes quadratic in ``c``.  This checker constructs an exact degree-6
real algebraic point at which that quadratic has a double root, all three
factors vanish, and every nonconstant parent bracket is nonzero.  The
discriminant changes sign there, so the quadratic branches inside one parent
chirotope cell.

This disproves a global two-graph or cellwise-discriminant-sign shortcut.  It
is not a compact component and does not disprove the third diagonal.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
from math import gcd
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as gradient  # noqa: E402
import verify_diag2_pivot_all_pair_fibers as fibers  # noqa: E402
import verify_residual_log_binomials as poly  # noqa: E402


FACTOR_IDS = (5_563, 16_134, 19_284)
SOURCE_TRIPLE = (12_985, 16_183, 7_196)
PIVOTS = (3, 0, 2)  # d, then a, then the quadratic coordinate c
MINIMAL = (
    172_134_400,
    -51_063_040,
    108_736_016,
    63_398_360,
    13_768_025,
    15_661_250,
    1_890_625,
)  # low degree first
LOWER = Fraction(-7_769, 1_000)
UPPER = Fraction(-7_768, 1_000)
EXPECTED_DIGEST = "10ed199125e6d6caba04306add891456ee190c30b7f011414166b6a9aaa95241"
UNION4_MOVING_LABEL = 2  # projective label 3, in zero-based coordinates
UNION4_OCCURRENCE_LABELS = (
    ("123", "145", "246", "378"),
    ("126", "257", "367", "458"),
    ("245", "157", "348", "168"),
)
EXPECTED_UNION4_COLORS = (1, 1, 2, 4)


def clean(values):
    values = list(values)
    while values and not values[-1]:
        values.pop()
    return values


def add(left, right):
    answer = [Fraction(0)] * max(len(left), len(right))
    for index, value in enumerate(left):
        answer[index] += value
    for index, value in enumerate(right):
        answer[index] += value
    return clean(answer)


def multiply(left, right):
    if not left or not right:
        return []
    answer = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            answer[i + j] += x * y
    return clean(answer)


def divmod_polynomial(dividend, divisor):
    remainder = clean(dividend)
    quotient = [Fraction(0)] * max(0, len(remainder) - len(divisor) + 1)
    while remainder and len(remainder) >= len(divisor):
        shift = len(remainder) - len(divisor)
        scale = remainder[-1] / divisor[-1]
        quotient[shift] += scale
        for index, value in enumerate(divisor):
            remainder[index + shift] -= scale * value
        remainder = clean(remainder)
    return clean(quotient), remainder


def derivative(polynomial):
    return clean([degree * value for degree, value in enumerate(polynomial)][1:])


def value(polynomial, point):
    answer = Fraction(0)
    for coefficient in reversed(polynomial):
        answer = answer * point + coefficient
    return answer


def sturm_sequence(polynomial):
    sequence = [clean(polynomial), derivative(polynomial)]
    while sequence[-1]:
        _quotient, remainder = divmod_polynomial(sequence[-2], sequence[-1])
        if not remainder:
            break
        sequence.append([-entry for entry in remainder])
    return tuple(sequence)


def variations(sequence, point):
    signs = []
    for polynomial in sequence:
        evaluation = value(polynomial, point)
        if evaluation:
            signs.append(1 if evaluation > 0 else -1)
    return sum(left != right for left, right in zip(signs, signs[1:]))


def root_count(polynomial, lower, upper):
    if not value(polynomial, lower) or not value(polynomial, upper):
        raise AssertionError("Sturm endpoint lies on the polynomial")
    sequence = sturm_sequence(polynomial)
    return variations(sequence, lower) - variations(sequence, upper)


def mod_trim(polynomial, prime):
    polynomial = [int(value) % prime for value in polynomial]
    while polynomial and not polynomial[-1]:
        polynomial.pop()
    return polynomial


def mod_divmod(dividend, divisor, prime):
    remainder = mod_trim(dividend, prime)
    divisor = mod_trim(divisor, prime)
    inverse = pow(divisor[-1], prime - 2, prime)
    quotient = [0] * max(0, len(remainder) - len(divisor) + 1)
    while remainder and len(remainder) >= len(divisor):
        shift = len(remainder) - len(divisor)
        scale = remainder[-1] * inverse % prime
        quotient[shift] = scale
        for index, entry in enumerate(divisor):
            remainder[index + shift] = (
                remainder[index + shift] - scale * entry
            ) % prime
        remainder = mod_trim(remainder, prime)
    return mod_trim(quotient, prime), remainder


def mod_multiply(left, right, modulus, prime):
    product = [0] * (len(left) + len(right) - 1)
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            product[i + j] = (product[i + j] + x * y) % prime
    return mod_divmod(product, modulus, prime)[1]


def mod_power(base, exponent, modulus, prime):
    answer = [1]
    while exponent:
        if exponent & 1:
            answer = mod_multiply(answer, base, modulus, prime)
        base = mod_multiply(base, base, modulus, prime)
        exponent //= 2
    return answer


def mod_gcd(left, right, prime):
    left, right = mod_trim(left, prime), mod_trim(right, prime)
    while right:
        left, right = right, mod_divmod(left, right, prime)[1]
    if not left:
        return []
    inverse = pow(left[-1], prime - 2, prime)
    return [(entry * inverse) % prime for entry in left]


def verify_irreducible_mod_seven():
    """Rabin's degree-six criterion; irreducible mod 7 implies over QQ."""
    prime = 7
    modulus = mod_trim(MINIMAL, prime)
    inverse = pow(modulus[-1], prime - 2, prime)
    modulus = [(entry * inverse) % prime for entry in modulus]
    x = [0, 1]
    if mod_power(x, prime**6, modulus, prime) != x:
        raise AssertionError("minimal polynomial fails Frobenius degree six")
    for exponent in (prime**3, prime**2):
        difference = add_mod(mod_power(x, exponent, modulus, prime), [0, -1], prime)
        if mod_gcd(modulus, difference, prime) != [1]:
            raise AssertionError("minimal polynomial has a proper finite-field factor")
    return tuple(modulus)


def add_mod(left, right, prime):
    answer = [0] * max(len(left), len(right))
    for index, entry in enumerate(left):
        answer[index] = (answer[index] + entry) % prime
    for index, entry in enumerate(right):
        answer[index] = (answer[index] + entry) % prime
    return mod_trim(answer, prime)


class NumberFieldElement:
    """An element of QQ[t]/(MINIMAL), stored in the power basis."""

    def __init__(self, coefficients=0):
        if isinstance(coefficients, NumberFieldElement):
            self.coefficients = coefficients.coefficients
            return
        if isinstance(coefficients, (int, Fraction)):
            coefficients = [Fraction(coefficients)]
        coefficients = [Fraction(value) for value in coefficients]
        for degree in range(len(coefficients) - 1, 5, -1):
            scale = coefficients[degree] / MINIMAL[6]
            if not scale:
                continue
            coefficients[degree] = 0
            shift = degree - 6
            for index in range(6):
                coefficients[index + shift] -= scale * MINIMAL[index]
        coefficients = clean(coefficients)
        coefficients.extend([Fraction(0)] * (6 - len(coefficients)))
        self.coefficients = tuple(coefficients)

    def __add__(self, other):
        other = NumberFieldElement(other)
        return NumberFieldElement(
            [left + right for left, right in zip(self.coefficients, other.coefficients)]
        )

    __radd__ = __add__

    def __neg__(self):
        return NumberFieldElement([-value for value in self.coefficients])

    def __sub__(self, other):
        return self + (-NumberFieldElement(other))

    def __rsub__(self, other):
        return NumberFieldElement(other) - self

    def __mul__(self, other):
        other = NumberFieldElement(other)
        return NumberFieldElement(multiply(self.coefficients, other.coefficients))

    __rmul__ = __mul__

    def __pow__(self, exponent):
        answer = NumberFieldElement(1)
        base = self
        while exponent:
            if exponent & 1:
                answer *= base
            base *= base
            exponent //= 2
        return answer

    def inverse(self):
        if not self:
            raise ZeroDivisionError("zero number-field element")
        columns = []
        generator = NumberFieldElement([0, 1])
        power = NumberFieldElement(1)
        for _index in range(6):
            columns.append((self * power).coefficients)
            power *= generator
        matrix = [
            [columns[column][row] for column in range(6)]
            + [Fraction(int(row == 0))]
            for row in range(6)
        ]
        pivot_row = 0
        for column in range(6):
            pivot = next(
                (row for row in range(pivot_row, 6) if matrix[row][column]), None
            )
            if pivot is None:
                raise AssertionError("minimal polynomial was not irreducible")
            matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
            scale = matrix[pivot_row][column]
            matrix[pivot_row] = [entry / scale for entry in matrix[pivot_row]]
            for row in range(6):
                if row == pivot_row or not matrix[row][column]:
                    continue
                scale = matrix[row][column]
                matrix[row] = [
                    left - scale * right
                    for left, right in zip(matrix[row], matrix[pivot_row])
                ]
            pivot_row += 1
        answer = NumberFieldElement([matrix[row][-1] for row in range(6)])
        if self * answer != 1:
            raise AssertionError("number-field inverse failed")
        return answer

    def __truediv__(self, other):
        return self * NumberFieldElement(other).inverse()

    def __bool__(self):
        return any(self.coefficients)

    def __eq__(self, other):
        return self.coefficients == NumberFieldElement(other).coefficients

    def __repr__(self):
        return repr(self.coefficients)


def evaluate(polynomial, coordinates):
    answer = NumberFieldElement(0)
    for monomial, coefficient in polynomial.items():
        term = NumberFieldElement(coefficient)
        for coordinate, exponent in zip(coordinates, monomial):
            if exponent:
                term *= coordinate**exponent
        answer += term
    return answer


def coefficients_in(polynomial, variable, maximum):
    answer = [dict() for _ in range(maximum + 1)]
    for monomial, coefficient in polynomial.items():
        exponent = monomial[variable]
        if exponent > maximum:
            raise AssertionError("unexpected polynomial degree")
        reduced = list(monomial)
        reduced[variable] = 0
        reduced = tuple(reduced)
        answer[exponent][reduced] = answer[exponent].get(reduced, 0) + coefficient
    return tuple(poly.clean(item) for item in answer)


def occurrence_from_labels(labels):
    return tuple(
        sorted(
            labeled.TRIPLE_INDEX[
                tuple(sorted(int(character) - 1 for character in label))
            ]
            for label in labels
        )
    )


def main():
    if gcd(*map(abs, MINIMAL)) != 1:
        raise AssertionError("minimal polynomial is not primitive")
    finite_field_polynomial = verify_irreducible_mod_seven()
    rational_polynomial = list(map(Fraction, MINIMAL))
    if root_count(rational_polynomial, LOWER, UPPER) != 1:
        raise AssertionError("algebraic root interval is not unique")
    endpoint_signs = (
        1 if value(rational_polynomial, LOWER) > 0 else -1,
        1 if value(rational_polynomial, UPPER) > 0 else -1,
    )
    if endpoint_signs[0] == endpoint_signs[1]:
        raise AssertionError("the algebraic root is not sign-changing")

    occurrences, occurrence_factor, factor_polynomial = labeled.factor_polynomials()
    selected_occurrences = tuple(
        occurrence_from_labels(labels) for labels in UNION4_OCCURRENCE_LABELS
    )
    if any(
        occurrence_factor[occurrence] != factor
        for factor, occurrence in zip(
            FACTOR_IDS, selected_occurrences, strict=True
        )
    ):
        raise AssertionError("union-four occurrence/factor assignment changed")
    incident_normals = tuple(
        frozenset(
            normal
            for normal in occurrence
            if UNION4_MOVING_LABEL in labeled.TRIPLES[normal]
        )
        for occurrence in selected_occurrences
    )
    incident_union = tuple(sorted(set().union(*incident_normals)))
    colors = tuple(
        sorted(
            sum(
                (normal in incident_normals[row]) << row
                for row in range(3)
            )
            for normal in incident_union
        )
    )
    if colors != EXPECTED_UNION4_COLORS:
        raise AssertionError("internal discriminant union-four core changed")
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    _representatives, _stabilizers, alignment, _factor_occurrence, _sizes = (
        labeled.factor_orbit_data(occurrences, occurrence_factor)
    )
    source_kind, source_mapping = alignment[SOURCE_TRIPLE[0]]
    transformed_source = tuple(
        labeled.transform_factor(
            factor, source_mapping, factor_occurrence, occurrence_factor
        )
        for factor in SOURCE_TRIPLE
    )
    if source_kind != 50 or transformed_source != (5_563, 19_284, 16_134):
        raise AssertionError("hard source triple no longer reaches this presentation")
    first, second, third = FACTOR_IDS
    pivot, second_pivot, quadratic = PIVOTS
    slope, constant = fibers.pivot_split(factor_polynomial[first], pivot)
    if poly.add(
        poly.multiply(slope, poly.variable(pivot)), constant
    ) != factor_polynomial[first]:
        raise AssertionError("anchor pivot normalization changed the equation")
    numerator = poly.negative(constant)
    second_restricted = fibers.graph_restrict(
        factor_polynomial[second], pivot, slope, numerator
    )
    second_slope = fibers.primitive(
        gradient.derivative(second_restricted, second_pivot)
    )
    second_constant = fibers.primitive(
        {
            monomial: coefficient
            for monomial, coefficient in second_restricted.items()
            if monomial[second_pivot] == 0
        }
    )
    raw_second_slope = gradient.derivative(second_restricted, second_pivot)
    raw_second_constant = {
        monomial: coefficient
        for monomial, coefficient in second_restricted.items()
        if monomial[second_pivot] == 0
    }
    if second_slope != raw_second_slope or second_constant != raw_second_constant:
        raise AssertionError("second pivot normalization changed the equation")
    third_once = fibers.graph_restrict(
        factor_polynomial[third], pivot, slope, numerator
    )
    final = fibers.graph_restrict(
        third_once,
        second_pivot,
        second_slope,
        poly.negative(second_constant),
    )
    constant_c, linear_c, quadratic_c = coefficients_in(final, quadratic, 2)
    discriminant = poly.subtract(
        poly.multiply(linear_c, linear_c),
        poly.multiply(poly.constant(4), quadratic_c, constant_c),
    )

    fixed = {4: -2, 5: -4, 6: 5, 7: -5, 8: 6}
    specialized = {}
    for monomial, coefficient in discriminant.items():
        term = coefficient
        for index, exponent in enumerate(monomial):
            if index == 1:
                continue
            if exponent:
                term *= fixed.get(index, 0) ** exponent
        specialized[monomial[1]] = specialized.get(monomial[1], 0) + term
    divisor = gcd(*(abs(value) for value in specialized.values()))
    primitive_discriminant = tuple(
        specialized.get(degree, 0) // divisor
        for degree in range(max(specialized) + 1)
    )
    if primitive_discriminant != MINIMAL or divisor != 576:
        raise AssertionError("specialized discriminant changed")

    generator = NumberFieldElement([0, 1])
    coordinates = [NumberFieldElement(0) for _ in range(9)]
    coordinates[1] = generator
    for index, entry in fixed.items():
        coordinates[index] = NumberFieldElement(entry)
    leading = evaluate(quadratic_c, coordinates)
    middle = evaluate(linear_c, coordinates)
    if not leading:
        raise AssertionError("quadratic leading coefficient vanished")
    coordinates[quadratic] = -middle / (2 * leading)
    second_slope_value = evaluate(second_slope, coordinates)
    if not second_slope_value:
        raise AssertionError("second graph slope vanished")
    coordinates[second_pivot] = -evaluate(second_constant, coordinates) / second_slope_value
    slope_value = evaluate(slope, coordinates)
    if not slope_value:
        raise AssertionError("anchor graph slope vanished")
    coordinates[pivot] = evaluate(numerator, coordinates) / slope_value

    residual_values = tuple(
        evaluate(factor_polynomial[factor], coordinates) for factor in FACTOR_IDS
    )
    if residual_values != (0, 0, 0):
        raise AssertionError("exact algebraic point missed the factor triple")
    first_derivative = evaluate(gradient.derivative(final, quadratic), coordinates)
    second_derivative = evaluate(
        gradient.derivative(gradient.derivative(final, quadratic), quadratic),
        coordinates,
    )
    if first_derivative or not second_derivative:
        raise AssertionError("the final quadratic is not exactly double")

    bracket_values = []
    for label, bracket, _sign in labeled.parent_bracket_factors():
        bracket_value = evaluate(bracket, coordinates)
        if not bracket_value:
            raise AssertionError(f"parent bracket {label} vanished")
        bracket_values.append((label, bracket_value.coefficients))

    semantic = (
        "diag3-internal-discriminant-wall-v1",
        SOURCE_TRIPLE,
        FACTOR_IDS,
        PIVOTS,
        MINIMAL,
        (LOWER, UPPER),
        endpoint_signs,
        primitive_discriminant,
        tuple(coordinate.coefficients for coordinate in coordinates),
        tuple(bracket_values),
        second_derivative.coefficients,
    )
    digest = hashlib.sha256(repr(semantic).encode("ascii")).hexdigest()
    if digest != EXPECTED_DIGEST:
        raise AssertionError(f"semantic digest changed: {digest}")
    print("PASS irreducible minimal polynomial mod 7:", finite_field_polynomial)
    print("PASS unique sign-changing root interval:", LOWER, UPPER)
    print("PASS specialized quadratic discriminant:", primitive_discriminant)
    print("PASS exact triple factors vanish:", FACTOR_IDS)
    print("PASS union-four incidence colors:", colors)
    print("PASS nonconstant parent brackets remain nonzero:", len(bracket_values))
    print("PASS final c-quadratic has an exact double root")
    print("SEMANTIC", digest)
    print("NO-GO the discriminant wall crosses the interior of one parent cell")


if __name__ == "__main__":
    main()
