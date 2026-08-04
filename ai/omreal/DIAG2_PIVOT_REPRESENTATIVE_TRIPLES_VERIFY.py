#!/usr/bin/env python3
"""Exact rank classification for the currently settled residual triples.

This dependency-free verifier proves three deliberately limited statements
about the twelve distinct canonical residual polynomials:

* 170 of the 220 triples have a 3-by-3 Jacobian minor which is a signed
  product of nonzero parent brackets;
* the formerly first-open triple (36,38,42) also has rank three throughout
  the uniform parent locus, by a two-step exact ideal certificate; and
* four other triples have exact rational points in the uniform parent locus
  at which their Jacobian has rank exactly two.

This is not an enumeration of relative labeled S_8 occurrences and does not
settle the remaining 45 canonical triples.
"""

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as pair  # noqa: E402
import verify_residual_log_binomials as poly  # noqa: E402


ZERO_MONOMIAL = (0,) * 9
VARIABLE_NAMES = "abcdefghi"


def leading(polynomial):
    return max(polynomial) if polynomial else None


def exact_divide(dividend, divisor):
    """Return the exact lexicographic quotient, or None if not divisible."""

    quotient = {}
    remainder = dict(dividend)
    divisor_monomial = leading(divisor)
    divisor_coefficient = divisor[divisor_monomial]
    while remainder:
        remainder_monomial = leading(remainder)
        remainder_coefficient = remainder[remainder_monomial]
        if any(
            left < right
            for left, right in zip(remainder_monomial, divisor_monomial)
        ):
            return None
        if remainder_coefficient % divisor_coefficient:
            return None
        monomial = tuple(
            left - right
            for left, right in zip(remainder_monomial, divisor_monomial)
        )
        coefficient = remainder_coefficient // divisor_coefficient
        quotient[monomial] = quotient.get(monomial, 0) + coefficient
        remainder = poly.subtract(
            remainder,
            poly.multiply({monomial: coefficient}, divisor),
        )
    return poly.clean(quotient)


def normalized_bracket_factors(brackets):
    """Deduplicate nonconstant parent brackets up to sign."""

    result = []
    seen = set()
    for label, bracket in brackets.items():
        if len(bracket) == 1 and ZERO_MONOMIAL in bracket:
            continue
        sign = 1 if bracket[leading(bracket)] > 0 else -1
        normalized = poly.multiply(poly.constant(sign), bracket)
        key = tuple(sorted(normalized.items()))
        if key in seen:
            continue
        seen.add(key)
        result.append((label, normalized, sign))
    # Trying sparse factors first makes the exhaustive scan deterministic and
    # keeps its running time modest.  Every successful division lowers degree.
    result.sort(key=lambda item: (len(item[1]), item[0]))
    return tuple(result)


def bracket_factorization(polynomial, factors, depth=10):
    """Find an exact signed parent-bracket product, if one exists."""

    if not polynomial:
        return None
    if len(polynomial) == 1 and ZERO_MONOMIAL in polynomial:
        return polynomial[ZERO_MONOMIAL], ()
    if not depth:
        return None
    for label, factor, sign in factors:
        quotient = exact_divide(polynomial, factor)
        if quotient is None:
            continue
        tail = bracket_factorization(quotient, factors, depth - 1)
        if tail is not None:
            scalar, labels = tail
            return scalar * sign, (label,) + labels
    return None


def jacobian_minor(residual, kinds, variables):
    entries = tuple(
        tuple(pair.derivative(residual[kind], variable) for variable in variables)
        for kind in kinds
    )
    return poly.add(
        poly.multiply(entries[0][0], entries[1][1], entries[2][2]),
        poly.multiply(entries[0][1], entries[1][2], entries[2][0]),
        poly.multiply(entries[0][2], entries[1][0], entries[2][1]),
        poly.negative(poly.multiply(entries[0][2], entries[1][1], entries[2][0])),
        poly.negative(poly.multiply(entries[0][1], entries[1][0], entries[2][2])),
        poly.negative(poly.multiply(entries[0][0], entries[1][2], entries[2][1])),
    )


UNRESOLVED_BY_DIRECT_PRODUCT = (
    (36, 38, 42), (36, 38, 50), (36, 39, 51), (36, 42, 51),
    (36, 44, 51), (37, 38, 39), (37, 38, 42), (37, 38, 51),
    (37, 39, 51), (37, 41, 46), (37, 42, 50), (37, 42, 51),
    (37, 44, 51), (37, 46, 48), (37, 46, 49), (37, 50, 51),
    (38, 39, 41), (38, 39, 42), (38, 39, 49), (38, 39, 51),
    (38, 41, 42), (38, 41, 44), (38, 41, 50), (38, 41, 51),
    (38, 42, 44), (38, 42, 46), (38, 42, 49), (38, 42, 50),
    (38, 42, 51), (38, 44, 46), (38, 44, 51), (38, 46, 50),
    (38, 49, 51), (39, 41, 51), (39, 42, 51), (39, 44, 51),
    (39, 46, 51), (39, 48, 50), (39, 49, 51), (41, 44, 51),
    (41, 46, 49), (41, 50, 51), (42, 44, 51), (42, 46, 50),
    (42, 49, 51), (42, 50, 51), (44, 46, 51), (44, 49, 51),
    (44, 50, 51), (49, 50, 51),
)


def verify_direct_product_scan(residual, brackets):
    factors = normalized_bracket_factors(brackets)
    direct = {}
    unresolved = []
    for triple in combinations(sorted(residual), 3):
        certificate = None
        for variables in combinations(range(9), 3):
            minor = jacobian_minor(residual, triple, variables)
            factorization = bracket_factorization(minor, factors)
            if factorization is not None:
                certificate = variables, factorization
                break
        if certificate is None:
            unresolved.append(triple)
        else:
            direct[triple] = certificate
    if len(direct) != 170:
        raise AssertionError(f"expected 170 direct triples, found {len(direct)}")
    if tuple(unresolved) != UNRESOLVED_BY_DIRECT_PRODUCT:
        raise AssertionError("the exact direct-product boundary changed")
    return direct


def verify_36_38_42_certificate(residual, brackets):
    variables = tuple(pair.Polynomial(poly.variable(index)) for index in range(9))
    a, b, c, d, e, f, _g, _h, _i = variables
    auxiliary = a * e - b * d + b - e
    q36 = pair.Polynomial(residual[36])

    minor_agi = pair.Polynomial(
        jacobian_minor(residual, (36, 38, 42), (0, 6, 8))
    )
    minor_agh = pair.Polynomial(
        jacobian_minor(residual, (36, 38, 42), (0, 6, 7))
    )
    first_unit = pair.Polynomial(
        poly.multiply(brackets["1237"], brackets["1247"], brackets["2356"])
    )
    if minor_agi.data != (first_unit * auxiliary).data:
        raise AssertionError("wrong M_agi identity for (36,38,42)")

    coefficient = c * f * f + c * f - f * f
    if minor_agh.data != (coefficient * auxiliary - b * f * q36).data:
        raise AssertionError("wrong M_agh reduction for (36,38,42)")

    final_identity = f * auxiliary - e * q36
    final_unit = pair.Polynomial(
        poly.negative(poly.multiply(brackets["3457"], brackets["1267"]))
    )
    if final_identity.data != final_unit.data:
        raise AssertionError("wrong terminal bracket identity for (36,38,42)")


RANK_DROP_WITNESSES = {
    (37, 41, 46): (
        Fraction(-14, 3), Fraction(-2), Fraction(2), Fraction(83, 15),
        Fraction(43, 15), Fraction(-32, 15), Fraction(-23, 25),
        Fraction(-29, 30), Fraction(38, 21),
    ),
    (37, 46, 49): (
        Fraction(47, 12), Fraction(6), Fraction(35, 12), Fraction(-3, 2),
        Fraction(-4), Fraction(-2), Fraction(1, 5), Fraction(-65, 27),
        Fraction(3, 19),
    ),
    (39, 48, 50): (
        Fraction(-1), Fraction(2), Fraction(3), Fraction(4), Fraction(-5),
        Fraction(2), Fraction(7), Fraction(-4), Fraction(5),
    ),
    (41, 46, 49): (
        Fraction(2), Fraction(17, 16), Fraction(-3), Fraction(59, 64),
        Fraction(11, 16), Fraction(15, 16), Fraction(79, 29),
        Fraction(-13, 4), Fraction(166, 43),
    ),
}


def evaluate(polynomial, point):
    total = Fraction(0)
    for monomial, coefficient in polynomial.items():
        term = Fraction(coefficient)
        for value, exponent in zip(point, monomial):
            if exponent:
                term *= value ** exponent
        total += term
    return total


def determinant2(matrix, rows, columns):
    return (
        matrix[rows[0]][columns[0]] * matrix[rows[1]][columns[1]]
        - matrix[rows[0]][columns[1]] * matrix[rows[1]][columns[0]]
    )


def verify_rank_drop_witnesses(residual, brackets):
    for triple, point in RANK_DROP_WITNESSES.items():
        if any(evaluate(bracket, point) == 0 for bracket in brackets.values()):
            raise AssertionError(f"rank-drop witness {triple} is not uniform")
        jacobian = tuple(
            tuple(
                evaluate(pair.derivative(residual[kind], variable), point)
                for variable in range(9)
            )
            for kind in triple
        )
        if any(
            evaluate(jacobian_minor(residual, triple, variables), point) != 0
            for variables in combinations(range(9), 3)
        ):
            raise AssertionError(f"witness {triple} does not have rank at most two")
        if not any(
            determinant2(jacobian, rows, columns) != 0
            for rows in combinations(range(3), 2)
            for columns in combinations(range(9), 2)
        ):
            raise AssertionError(f"witness {triple} has rank below two")


def main():
    residual, brackets = pair.polynomial_data()
    direct = verify_direct_product_scan(residual, brackets)
    verify_36_38_42_certificate(residual, brackets)
    verify_rank_drop_witnesses(residual, brackets)
    print("PASS exact bracket-product 3-minors for", len(direct), "canonical triples")
    print("PASS sequential uniform-rank certificate for (36,38,42)")
    print("PASS exact uniform rank-two witnesses for", tuple(RANK_DROP_WITNESSES))
    print("STATUS 171 rank-three, 4 rank-drop, 45 open among 220 canonical triples")
    print("CAVEAT no relative labeled S_8 classification and no diagonal-two proof")


if __name__ == "__main__":
    main()
