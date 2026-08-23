#!/usr/bin/env python3
"""Standard-library replay of the four-support second projection frontier."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from math import gcd, lcm
import gzip
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import diag3_pair_global_four_support_projection_core as source_core  # noqa: E402


CERTIFICATE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz"
FORMAT = "diag3-pair-global-row2599-four-support-base-projection-v1"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def parse_bivariate(rows):
    return {
        tuple(row["exponent"]): Fraction(row["coefficient"])
        for row in rows
        if Fraction(row["coefficient"])
    }


def canonical_bivariate(polynomial):
    polynomial = {key: Fraction(value) for key, value in polynomial.items() if value}
    if not polynomial:
        return ()
    denominator = 1
    for value in polynomial.values():
        denominator = lcm(denominator, value.denominator)
    rows = [(key, int(value * denominator)) for key, value in polynomial.items()]
    content = 0
    for _key, value in rows:
        content = gcd(content, abs(value))
    rows = [(key, value // content) for key, value in rows]
    leading = max(rows)[1]
    if leading < 0:
        rows = [(key, -value) for key, value in rows]
    return tuple(sorted(rows))


def multiply_bivariate(left, right):
    answer = Counter()
    for left_exponent, left_value in left.items():
        for right_exponent, right_value in right.items():
            exponent = tuple(
                left_exponent[index] + right_exponent[index]
                for index in range(2)
            )
            answer[exponent] += left_value * right_value
    return {key: value for key, value in answer.items() if value}


def trim(polynomial):
    polynomial = list(polynomial)
    while len(polynomial) > 1 and not polynomial[-1]:
        polynomial.pop()
    return polynomial or [0]


def polynomial_add(left, right):
    answer = [Fraction(0)] * max(len(left), len(right))
    for index, value in enumerate(left):
        answer[index] += value
    for index, value in enumerate(right):
        answer[index] += value
    return trim(answer)


def polynomial_negate(polynomial):
    return [-value for value in polynomial]


def polynomial_multiply(left, right):
    left, right = trim(left), trim(right)
    if left == [0] or right == [0]:
        return [0]
    answer = [Fraction(0)] * (len(left) + len(right) - 1)
    for left_degree, left_value in enumerate(left):
        for right_degree, right_value in enumerate(right):
            answer[left_degree + right_degree] += left_value * right_value
    return trim(answer)


def polynomial_scale(polynomial, scalar):
    return trim([scalar * value for value in polynomial])


def divide_over_q(dividend, divisor):
    dividend = trim([Fraction(value) for value in dividend])
    divisor = trim([Fraction(value) for value in divisor])
    require(divisor != [0], "division by zero polynomial")
    if len(dividend) < len(divisor):
        return [Fraction(0)], dividend
    quotient = [Fraction(0)] * (len(dividend) - len(divisor) + 1)
    while dividend != [0] and len(dividend) >= len(divisor):
        value = dividend[-1] / divisor[-1]
        offset = len(dividend) - len(divisor)
        quotient[offset] = value
        for index, divisor_value in enumerate(divisor):
            dividend[offset + index] -= value * divisor_value
        dividend = trim(dividend)
    return trim(quotient), dividend


def polynomial_divide_exact(dividend, divisor):
    quotient, remainder = divide_over_q(dividend, divisor)
    require(remainder == [0], "nonzero polynomial remainder")
    return quotient


def polynomial_gcd(left, right):
    left = trim([Fraction(value) for value in left])
    right = trim([Fraction(value) for value in right])
    while right != [0]:
        _quotient, remainder = divide_over_q(left, right)
        left, right = right, remainder
    if left == [0]:
        return [Fraction(0)]
    scale = abs(left[-1])
    return trim([value / scale for value in left])


def primitive_univariate(polynomial):
    polynomial = trim([Fraction(value) for value in polynomial])
    require(polynomial != [0], "zero polynomial has no primitive form")
    denominator = 1
    for value in polynomial:
        denominator = lcm(denominator, value.denominator)
    integers = [int(value * denominator) for value in polynomial]
    content = 0
    for value in integers:
        content = gcd(content, abs(value))
    integers = [value // content for value in integers]
    if integers[-1] < 0:
        integers = [-value for value in integers]
    return trim(integers)


def univariate_key(polynomial):
    return tuple(((index,), value) for index, value in enumerate(primitive_univariate(polynomial)) if value)


def coefficients_in_u(polynomial):
    maximum_u = max(exponent[0] for exponent in polynomial)
    answer = [[Fraction(0)] for _ in range(maximum_u + 1)]
    for (degree_u, degree_t), coefficient in polynomial.items():
        if len(answer[degree_u]) <= degree_t:
            answer[degree_u].extend(
                [Fraction(0)] * (degree_t + 1 - len(answer[degree_u]))
            )
        answer[degree_u][degree_t] += coefficient
    return [trim(row) for row in answer]


def sylvester_resultant(first, second):
    first = [trim(row) for row in first]
    second = [trim(row) for row in second]
    first_degree = len(first) - 1
    second_degree = len(second) - 1
    if first_degree == 0 and second_degree == 0:
        return [1]
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
        if trim(matrix[pivot_index][pivot_index]) == [0]:
            swap = next(
                row
                for row in range(pivot_index + 1, size)
                if trim(matrix[row][pivot_index]) != [0]
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
    degree = len(coefficients) - 1
    derivative = [
        polynomial_scale(coefficients[index], index)
        for index in range(1, len(coefficients))
    ]
    resultant = sylvester_resultant(coefficients, derivative)
    answer = polynomial_divide_exact(resultant, coefficients[-1])
    if degree * (degree - 1) // 2 % 2:
        answer = polynomial_negate(answer)
    return answer


def strip_square_boundary_squarefree(polynomial):
    polynomial = primitive_univariate(polynomial)
    if len(polynomial) <= 1:
        return None
    while polynomial[0] == 0:
        polynomial = polynomial[1:]
    while sum(polynomial) == 0:
        polynomial = primitive_univariate(
            polynomial_divide_exact(polynomial, [-1, 1])
        )
    if len(polynomial) <= 1:
        return None
    derivative = [index * polynomial[index] for index in range(1, len(polynomial))]
    common = polynomial_gcd(polynomial, derivative)
    squarefree = polynomial_divide_exact(polynomial, common)
    return univariate_key(squarefree)


def evaluate_univariate(polynomial, value):
    answer = Fraction(0)
    for coefficient in reversed(polynomial):
        answer = answer * value + coefficient
    return answer


def sign_variations(values):
    signs = [1 if value > 0 else -1 for value in values if value]
    return sum(left != right for left, right in zip(signs, signs[1:]))


def sturm_root_count(polynomial):
    polynomial = trim([Fraction(value) for value in polynomial])
    require(evaluate_univariate(polynomial, 0) != 0, "root at t=0")
    require(evaluate_univariate(polynomial, 1) != 0, "root at t=1")
    derivative = [index * polynomial[index] for index in range(1, len(polynomial))]
    sequence = [polynomial, trim(derivative)]
    while sequence[-1] != [0]:
        _quotient, remainder = divide_over_q(sequence[-2], sequence[-1])
        if remainder == [0]:
            break
        next_row = polynomial_negate(remainder)
        positive_scale = abs(next_row[-1])
        sequence.append([value / positive_scale for value in next_row])
    left = sign_variations(evaluate_univariate(row, 0) for row in sequence)
    right = sign_variations(evaluate_univariate(row, 1) for row in sequence)
    return left - right


def reconstruct_projection(base_catalog):
    coefficients = [coefficients_in_u(polynomial) for polynomial in base_catalog]
    rows = []
    kinds = Counter()

    def append(kind, polynomial):
        key = strip_square_boundary_squarefree(polynomial)
        if key is not None:
            rows.append(key)
            kinds[kind] += 1

    for coefficient_rows in coefficients:
        for coefficient in coefficient_rows:
            append("coefficient", coefficient)
        if len(coefficient_rows) >= 3:
            append("discriminant", discriminant(coefficient_rows))

    zero_resultants = 0
    pair_resultants = 0
    for left in range(len(coefficients)):
        for right in range(left + 1, len(coefficients)):
            resultant = sylvester_resultant(coefficients[left], coefficients[right])
            if trim(resultant) == [0]:
                zero_resultants += 1
            else:
                before = len(rows)
                append("pair_resultant", resultant)
                pair_resultants += len(rows) - before
    return sorted(set(rows)), dict(sorted(kinds.items())), pair_resultants, zero_resultants


def validate_claims(candidate, observed):
    require(candidate["format"] == FORMAT, "wrong certificate format")
    require(candidate["status"] == "PROVED", "wrong proof status")
    scope = candidate["scope"]
    require(scope["base_sign_invariant_cad"] == "NOT_YET_CONSTRUCTED", "false CAD claim")
    require(scope["global_parent_cell_coverage"] == "NOT_CLAIMED", "false global claim")
    require(scope["honest_9dvl_score"] == "2/9", "dishonest theorem score")
    require(candidate["source"]["semantic_sha256"] == observed["source_semantic"], "source semantic")
    require(candidate["base_factorization"]["distinct_factor_count"] == 114, "base factor count")
    require(candidate["base_factorization"]["catalog_sha256"] == observed["base_catalog_digest"], "base catalog digest")
    require(candidate["base_factorization"]["factorizations_sha256"] == observed["base_factorizations_digest"], "base factorization digest")
    projection = candidate["second_projection"]
    require(projection["raw_nonconstant_obligations"] == 6_061, "raw projection count")
    require(projection["distinct_squarefree_boundary_reduced_polynomials"] == 2_554, "squarefree projection count")
    require(projection["distinct_factor_count"] == 2_333, "univariate factor count")
    require(projection["factor_interior_root_incidences"] == 1_693, "root incidence count")
    require(projection["maximum_degree"] == 10, "maximum univariate degree")
    require(projection["catalog_sha256"] == observed["univariate_catalog_digest"], "univariate catalog digest")
    require(projection["factorizations_sha256"] == observed["projection_factorizations_digest"], "projection factorization digest")
    require(candidate["semantic_sha256"] == observed["semantic"], "semantic digest")
    require(candidate["resource_effect"]["ceiling_not_triggered"] is True, "projection ceiling")


def main():
    stored = json.loads(gzip.decompress(CERTIFICATE.read_bytes()))
    source = source_core.build_record(include_catalog=True)
    require(source["semantic_sha256"] == stored["source"]["semantic_sha256"], "first projection source changed")
    require(source["projection"]["catalog_sha256"] == stored["source"]["projection_catalog_sha256"], "first projection catalog changed")

    source_polynomials = [
        parse_bivariate(row["polynomial"])
        for row in source["projection"]["catalog"]
    ]
    base_rows = stored["base_factorization"]
    require([row["id"] for row in base_rows["catalog"]] == list(range(114)), "base IDs")
    base_catalog = [parse_bivariate(row["polynomial"]) for row in base_rows["catalog"]]
    require(len(base_rows["factorizations"]) == len(source_polynomials) == 136, "base factorization coverage")
    for index, row in enumerate(base_rows["factorizations"]):
        require(row["source_projection_id"] == index, "base source order")
        product = {(0, 0): Fraction(1)}
        for factor in row["factors"]:
            require(0 <= factor["id"] < len(base_catalog), "base factor ID")
            for _ in range(factor["multiplicity"]):
                product = multiply_bivariate(product, base_catalog[factor["id"]])
        require(
            canonical_bivariate(product) == canonical_bivariate(source_polynomials[index]),
            f"base factorization failed at source {index}",
        )

    unique_projection, kind_census, pair_resultants, zero_resultants = reconstruct_projection(base_catalog)
    projection = stored["second_projection"]
    require(kind_census == projection["raw_kind_census"], "projection kind census")
    require(pair_resultants == projection["nonconstant_pair_resultants"], "pair resultant count")
    require(zero_resultants == projection["identically_zero_pair_resultants"] == 0, "zero resultant count")
    require(len(unique_projection) == 2_554, "unique squarefree projection count")

    factor_rows = projection["catalog"]
    require([row["id"] for row in factor_rows] == list(range(2_333)), "univariate factor IDs")
    univariate_factors = [row["coefficients_low_to_high"] for row in factor_rows]
    require(len(projection["factorizations"]) == len(unique_projection), "projection factorization coverage")
    for index, row in enumerate(projection["factorizations"]):
        require(row["projection_id"] == index, "projection factorization order")
        product = [1]
        for factor in row["factors"]:
            require(0 <= factor["id"] < len(univariate_factors), "univariate factor ID")
            for _ in range(factor["multiplicity"]):
                product = polynomial_multiply(product, univariate_factors[factor["id"]])
        require(univariate_key(product) == unique_projection[index], f"univariate factorization failed at {index}")

    degree_census = Counter()
    root_census = Counter()
    root_incidences = 0
    for row, polynomial in zip(factor_rows, univariate_factors, strict=True):
        roots = sturm_root_count(polynomial)
        require(roots == row["interior_root_count"], f"Sturm count failed at factor {row['id']}")
        require(len(polynomial) - 1 == row["degree"], "stored factor degree")
        degree_census[row["degree"]] += 1
        root_census[roots] += 1
        root_incidences += roots
    require(root_incidences == 1_693, "root incidence total")
    require(
        {str(key): value for key, value in sorted(degree_census.items())}
        == projection["degree_census"],
        "degree census",
    )
    require(
        {str(key): value for key, value in sorted(root_census.items())}
        == projection["factor_interior_root_count_census"],
        "root census",
    )

    semantic_payload = {
        "source_semantic_sha256": source["semantic_sha256"],
        "base_factor_catalog": base_rows["catalog"],
        "base_factorizations": base_rows["factorizations"],
        "raw_kind_census": kind_census,
        "unique_projection_polynomial_count": len(unique_projection),
        "univariate_factor_catalog": factor_rows,
        "projection_factorizations": projection["factorizations"],
    }
    observed = {
        "source_semantic": source["semantic_sha256"],
        "base_catalog_digest": digest(base_rows["catalog"]),
        "base_factorizations_digest": digest(base_rows["factorizations"]),
        "univariate_catalog_digest": digest(factor_rows),
        "projection_factorizations_digest": digest(projection["factorizations"]),
        "semantic": digest(semantic_payload),
    }
    validate_claims(stored, observed)

    mutations = (
        (("status",), "OPEN"),
        (("scope", "base_sign_invariant_cad"), "COMPLETE"),
        (("scope", "global_parent_cell_coverage"), "COMPLETE"),
        (("scope", "honest_9dvl_score"), "3/9"),
        (("base_factorization", "distinct_factor_count"), 113),
        (("base_factorization", "catalog_sha256"), "0" * 64),
        (("second_projection", "raw_nonconstant_obligations"), 6_060),
        (("second_projection", "distinct_squarefree_boundary_reduced_polynomials"), 2_553),
        (("second_projection", "distinct_factor_count"), 2_332),
        (("second_projection", "factor_interior_root_incidences"), 1_692),
        (("semantic_sha256",), "0" * 64),
        (("resource_effect", "ceiling_not_triggered"), False),
    )
    rejected = 0
    for path, value in mutations:
        target = stored
        for key in path[:-1]:
            target = target[key]
        original = target[path[-1]]
        target[path[-1]] = value
        try:
            validate_claims(stored, observed)
        except AssertionError:
            rejected += 1
        finally:
            target[path[-1]] = original
    require(rejected == len(mutations), "a hostile second-projection mutation survived")

    print("PASS 136 source polynomials -> 114 exact base factors")
    print("PASS 6061 obligations -> 2554 distinct squarefree projection polynomials")
    print("PASS 2333 factor polynomials / maximum degree 10")
    print("PASS standard-library Sturm replay: 1693 interior root incidences")
    print("PASS projection ceiling not triggered")
    print(f"PASS {rejected}/{len(mutations)} hostile mutations rejected")
    print("SCOPE second projection only; base CAD, lifted cells, and global pair complex remain open; honest 9DVL 2/9")


if __name__ == "__main__":
    main()
