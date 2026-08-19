#!/usr/bin/env python3
"""Exact no-go certificate for direct elimination through the ``L`` cover.

The hard diagonal-three hypersurface critical system has a primitive factor
``L`` which is quadratic in ``h`` with parent-unit leading coefficient.  This
checker exhausts the most immediate uses of that fact:

* intersect the transverse ``P=0`` graph with ``L=0`` exactly;
* test the resulting quadratic-in-``d`` discriminant on every stored
  realizable parent representative; and
* form the direct ``h`` resultant of ``L`` with each of the seven critical
  equations, stripping every nonconstant parent-bracket factor exactly.

The output is a method-local no-go.  It proves that the seven direct
pairwise-resultant routes are expansions rather than compressions and that
the reduced discriminant is not sign-definite on the stored parent atlas.
It does not prove that the critical ideal is nontrivial, nor does it exclude
a structured syzygy, a simultaneous elimination, or a topological argument.
"""

from __future__ import annotations

from collections import Counter
from functools import reduce
from fractions import Fraction
import hashlib
import heapq
from math import gcd
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import explore_diag3_triple_hypersurface_groebner as chart  # noqa: E402
import verify_diag3_triple_boundary_stratification as boundary  # noqa: E402
import verify_diag3_triple_rank_drop_parent_atlas as atlas  # noqa: E402
from verify_diag3_triple_two_pivot_rank_drop import EXPECTED_P  # noqa: E402


EXPECTED_S_CENSUS = (105, 5, 9)
EXPECTED_S_DEGREES = (0, 0, 0, 2, 0, 3, 4, 3, 3)
EXPECTED_S_SHA256 = "795e76f439f84d0cdb6cc3d0afc488dff819ef5baea3789da8abbb6956883431"
EXPECTED_D_CENSUS = (315, 6, 14)
EXPECTED_D_DEGREES = (0, 0, 0, 0, 0, 2, 6, 6, 5)
EXPECTED_D_SHA256 = "539a8feddc52d0e84ad09083390167a46a465c02a5fb3f03bb099b85bc4a75f1"
EXPECTED_SIGN_CENSUS = {-1: 442, 0: 0, 1: 2_162}
EXPECTED_SIGN_SHA256 = "bb697652bb4c85974e832af698a58c6861a46b7586e1c410585fb92ec9bbda91"

GENERATOR_NAMES = (
    "E",
    "E_c",
    "E_e",
    "E_h",
    "G_f",
    "G_g",
    "G_i",
)

# (raw resultant census, primitive census, parent-bracket factor multiset).
EXPECTED_RESULTANTS = (
    ((48_086, 18, 28), (19_806, 16, 24), ("2357", "2367", "2378", "3458")),
    ((50_655, 16, 26), (27_800, 14, 23), ("2378", "2378", "3458")),
    ((13_360, 18, 26), (5_320, 16, 22), ("2357", "2367", "2378", "3458")),
    ((22_938, 14, 23), (18_232, 13, 22), ("2378",)),
    ((83_413, 18, 28), (59_449, 17, 26), ("2378", "3458")),
    ((58_593, 18, 28), (38_653, 16, 26), ("2367", "2378")),
    ((87_712, 20, 30), (49_757, 18, 27), ("2367", "2378", "3458")),
)


def scale(polynomial, scalar):
    return {
        monomial: scalar * coefficient
        for monomial, coefficient in polynomial.items()
        if scalar * coefficient
    }


def coefficients(polynomial, variable):
    answer = {}
    for monomial, coefficient in polynomial.items():
        exponent = monomial[variable]
        reduced = list(monomial)
        reduced[variable] = 0
        answer.setdefault(exponent, {})[tuple(reduced)] = coefficient
    return answer


def census(polynomial):
    degrees = tuple(map(sum, polynomial))
    return len(polynomial), min(degrees), max(degrees)


def variable_degrees(polynomial):
    return tuple(
        max(monomial[index] for monomial in polynomial) for index in range(9)
    )


def polynomial_digest(polynomial):
    digest = hashlib.sha256()
    for monomial, coefficient in sorted(polynomial.items()):
        record = ",".join(map(str, monomial)) + ":" + str(coefficient) + "\n"
        digest.update(record.encode("ascii"))
    return digest.hexdigest()


def exact_divide(dividend, divisor):
    """Sparse exact integer division in lexicographic monomial order."""

    if not divisor:
        raise ZeroDivisionError("zero polynomial divisor")
    remainder = dict(dividend)
    quotient = {}
    divisor_monomial = max(divisor)
    divisor_coefficient = divisor[divisor_monomial]
    pending = [tuple(-exponent for exponent in monomial) for monomial in remainder]
    heapq.heapify(pending)

    while pending:
        monomial = tuple(-exponent for exponent in heapq.heappop(pending))
        coefficient = remainder.get(monomial, 0)
        if not coefficient:
            continue
        if any(
            left < right
            for left, right in zip(monomial, divisor_monomial, strict=True)
        ) or coefficient % divisor_coefficient:
            return None

        shift = tuple(
            left - right
            for left, right in zip(monomial, divisor_monomial, strict=True)
        )
        scalar = coefficient // divisor_coefficient
        quotient[shift] = quotient.get(shift, 0) + scalar
        for divisor_term, divisor_value in divisor.items():
            target = tuple(
                left + right
                for left, right in zip(shift, divisor_term, strict=True)
            )
            previous = remainder.get(target, 0)
            value = previous - scalar * divisor_value
            if value:
                remainder[target] = value
                if not previous:
                    heapq.heappush(pending, tuple(-entry for entry in target))
            elif previous:
                del remainder[target]
    return {monomial: value for monomial, value in quotient.items() if value}


def square(polynomial):
    return boundary.multiply(polynomial, polynomial)


def resultant_with_quadratic(quadratic, polynomial, variable=7):
    """Return the exact resultant for degrees two and at most two."""

    left = coefficients(quadratic, variable)
    right = coefficients(polynomial, variable)
    if set(left) != {0, 1, 2}:
        raise AssertionError("the cover is no longer exactly quadratic")
    a, b, c = left[2], left[1], left[0]
    degree = max(right)
    if degree == 1:
        e, f = right[1], right[0]
        return boundary.add(
            boundary.subtract(
                boundary.multiply(a, square(f)),
                boundary.multiply(b, boundary.multiply(e, f)),
            ),
            boundary.multiply(c, square(e)),
        )
    if degree == 2:
        d, e, f = right[2], right[1], right[0]
        af_cd = boundary.subtract(
            boundary.multiply(a, f), boundary.multiply(c, d)
        )
        ae_bd = boundary.subtract(
            boundary.multiply(a, e), boundary.multiply(b, d)
        )
        bf_ce = boundary.subtract(
            boundary.multiply(b, f), boundary.multiply(c, e)
        )
        return boundary.subtract(square(af_cd), boundary.multiply(ae_bd, bf_ce))
    raise AssertionError(f"unexpected h degree {degree}")


def strip_parent_factors(polynomial, walls):
    factors = []
    while True:
        for label, wall in walls.items():
            quotient = exact_divide(polynomial, wall)
            if quotient is not None:
                polynomial = quotient
                factors.append(label)
                break
        else:
            return polynomial, tuple(factors)


def reconstruct_l(generators):
    i_minus_f = boundary.subtract(boundary.coordinate(8), boundary.coordinate(5))
    e_slope = coefficients(generators[2], 4)[1]
    primitive = exact_divide(e_slope, scale(i_minus_f, 2))
    if primitive is None or census(primitive) != (60, 4, 7):
        raise AssertionError("the primitive L factor changed")
    return primitive


def graph_intersection(l_polynomial, walls):
    one = {boundary.ZERO: 1}
    c = boundary.coordinate(2)
    d = boundary.coordinate(3)
    f = boundary.coordinate(5)
    g = boundary.coordinate(6)
    h = boundary.coordinate(7)
    i = boundary.coordinate(8)
    i_minus_f = boundary.subtract(i, f)
    h_minus_i = boundary.subtract(h, i)
    g_minus_one = boundary.subtract(g, one)
    factor_f = boundary.subtract(boundary.multiply(g, h), i)
    factor_q = boundary.add(
        boundary.multiply(d, h_minus_i),
        boundary.multiply(boundary.multiply(f, h), g_minus_one),
    )
    p_polynomial = boundary.add(
        scale(boundary.multiply(boundary.multiply(f, walls["1378"]), factor_f), -1),
        boundary.multiply(boundary.multiply(c, i_minus_f), factor_q),
    )
    if p_polynomial != EXPECTED_P:
        raise AssertionError("the transverse P graph changed")

    p_coefficients = coefficients(p_polynomial, 2)
    l_coefficients = coefficients(l_polynomial, 2)
    if set(p_coefficients) != {0, 1} or set(l_coefficients) != {0, 1, 2}:
        raise AssertionError("the c degrees of P or L changed")
    p_zero, p_one = p_coefficients[0], p_coefficients[1]
    numerator = boundary.add(
        boundary.subtract(
            boundary.multiply(l_coefficients[0], square(p_one)),
            boundary.multiply(
                l_coefficients[1], boundary.multiply(p_zero, p_one)
            ),
        ),
        boundary.multiply(l_coefficients[2], square(p_zero)),
    )

    s_polynomial = numerator
    for divisor in (
        walls["1237"],
        walls["1378"],
        walls["2378"],
        factor_f,
    ):
        s_polynomial = exact_divide(s_polynomial, divisor)
        if s_polynomial is None:
            raise AssertionError("the exact P-L intersection factorization changed")
    rebuilt = s_polynomial
    for divisor in (
        walls["1237"],
        walls["1378"],
        walls["2378"],
        factor_f,
    ):
        rebuilt = boundary.multiply(rebuilt, divisor)
    if rebuilt != numerator:
        raise AssertionError("the exact P-L intersection did not rebuild")
    if (
        census(s_polynomial) != EXPECTED_S_CENSUS
        or variable_degrees(s_polynomial) != EXPECTED_S_DEGREES
        or polynomial_digest(s_polynomial) != EXPECTED_S_SHA256
    ):
        raise AssertionError("the primitive P-L intersection polynomial changed")
    if any(exact_divide(s_polynomial, wall) is not None for wall in walls.values()):
        raise AssertionError("S retained a parent-bracket factor")

    leading_g = coefficients(s_polynomial, 6)[4]
    expected_g = scale(
        boundary.multiply(
            square(walls["1237"]),
            boundary.multiply(
                boundary.multiply(walls["1248"], walls["2357"]),
                walls["2458"],
            ),
        ),
        -1,
    )
    leading_i = coefficients(s_polynomial, 8)[3]
    expected_i = boundary.multiply(
        square(walls["1347"]),
        boundary.multiply(
            boundary.multiply(walls["2357"], walls["2458"]),
            walls["3458"],
        ),
    )
    if leading_g != expected_g or leading_i != expected_i:
        raise AssertionError("a unit-leading coefficient of S changed")
    return s_polynomial, factor_f


def reduced_discriminant(s_polynomial, factor_f, walls):
    d_coefficients = coefficients(s_polynomial, 3)
    if set(d_coefficients) != {0, 1, 2}:
        raise AssertionError("S is no longer quadratic in d")
    discriminant = boundary.subtract(
        square(d_coefficients[1]),
        scale(boundary.multiply(d_coefficients[0], d_coefficients[2]), 4),
    )
    raw = discriminant
    for _ in range(2):
        discriminant = exact_divide(discriminant, walls["1237"])
        if discriminant is None:
            raise AssertionError("the discriminant lost its [1237]^2 factor")
    if boundary.multiply(discriminant, square(walls["1237"])) != raw:
        raise AssertionError("the reduced discriminant did not rebuild")
    if (
        census(discriminant) != EXPECTED_D_CENSUS
        or variable_degrees(discriminant) != EXPECTED_D_DEGREES
        or polynomial_digest(discriminant) != EXPECTED_D_SHA256
    ):
        raise AssertionError("the reduced discriminant changed")
    if any(exact_divide(discriminant, wall) is not None for wall in walls.values()):
        raise AssertionError("the reduced discriminant retained a parent factor")
    if exact_divide(discriminant, factor_f) is not None:
        raise AssertionError("the reduced discriminant acquired an F factor")
    return discriminant


def evaluate(polynomial, point):
    answer = Fraction(0)
    for monomial, coefficient in polynomial.items():
        value = Fraction(coefficient)
        for exponent, coordinate in zip(monomial, point, strict=True):
            if exponent:
                value *= coordinate**exponent
        answer += value
    return answer


def parent_sign_census(discriminant):
    realizable, _negative_by_basis = atlas.load_catalog()
    identity = tuple(range(8))
    counts = Counter()
    digest = hashlib.sha256(b"diag3-quadratic-cover-discriminant-signs-v1\0")
    for source_index, _chirotope, matrix in realizable:
        normalized = atlas.normalized_matrix(matrix, identity)
        point = []
        for column in (5, 6, 7):
            gauge = normalized[column][0]
            if not gauge:
                raise AssertionError("a uniform parent left the affine chart")
            point.extend(
                normalized[column][row] / gauge for row in (1, 2, 3)
            )
        value = evaluate(discriminant, tuple(point))
        sign = (value > 0) - (value < 0)
        counts[sign] += 1
        digest.update(source_index.to_bytes(4, "little"))
        digest.update(bytes((sign + 1,)))
    if (
        counts != Counter(EXPECTED_SIGN_CENSUS)
        or digest.hexdigest() != EXPECTED_SIGN_SHA256
    ):
        raise AssertionError("the exact parent discriminant-sign census changed")
    return len(realizable), counts, digest.hexdigest()


def direct_resultant_census(l_polynomial, generators, walls):
    rows = []
    for name, generator, expected in zip(
        GENERATOR_NAMES, generators, EXPECTED_RESULTANTS, strict=True
    ):
        raw = resultant_with_quadratic(l_polynomial, generator)
        primitive, factors = strip_parent_factors(raw, walls)
        raw_expected, primitive_expected, factors_expected = expected
        if (
            census(raw) != raw_expected
            or census(primitive) != primitive_expected
            or Counter(factors) != Counter(factors_expected)
        ):
            raise AssertionError(f"the {name} resultant census changed")
        if reduce(gcd, map(abs, primitive.values())) != 1:
            raise AssertionError(f"the {name} resultant retained integer content")
        if any(exact_divide(primitive, wall) is not None for wall in walls.values()):
            raise AssertionError(
                f"the primitive {name} resultant retained a parent factor"
            )
        rows.append(
            (name, census(generator), raw_expected, primitive_expected, factors)
        )
    return tuple(rows)


def main():
    generators, _localizers = chart.build_exact_system(())
    walls = boundary.parent_wall_map()
    if len(generators) != 7 or len(walls) != 62:
        raise AssertionError("the hard-canary system or parent wall count changed")
    l_polynomial = reconstruct_l(generators)
    s_polynomial, factor_f = graph_intersection(l_polynomial, walls)
    discriminant = reduced_discriminant(s_polynomial, factor_f, walls)
    parent_count, signs, sign_digest = parent_sign_census(discriminant)
    resultants = direct_resultant_census(l_polynomial, generators, walls)

    print("PASS P=0 and L=0 reduce exactly to a primitive 105-term S=0")
    print("PASS S is unit-leading of degree four in g and degree three in i")
    print("PASS disc_d(S)=[1237]^2 D with primitive 315-term D")
    print(
        f"PASS D signs on {parent_count} exact parent representatives: "
        f"{signs[1]} positive, {signs[-1]} negative, {signs[0]} zero"
    )
    print(f"SIGN_SHA256 {sign_digest}")
    for name, source, raw, primitive, factors in resultants:
        factor_text = "*".join(f"[{label}]" for label in factors) or "1"
        print(
            f"RESULTANT {name}: source={source[0]} raw={raw[0]} "
            f"primitive={primitive[0]} parent_factors={factor_text}"
        )
    print(
        "NO-GO all seven direct L-resultant routes expand after "
        "parent-factor stripping"
    )
    print("NO-GO the reduced discriminant has no universal sign on the parent atlas")
    print("SCOPE method-local only; the hard canary and theorem ledger remain open")


if __name__ == "__main__":
    main()
