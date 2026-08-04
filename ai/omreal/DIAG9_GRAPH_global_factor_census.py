#!/usr/bin/env python3
"""Exact global factor census for all 84,840 residual-wall occurrences.

Work in the standard normalized rank-four, eight-column chart

    [ I_4 | 1  1  1  1 ]
    [     |    a  d  g ]
    [     |    b  e  h ]
    [     |    c  f  i ].

For every labeled residual four-set of derived normals, this program expands
its determinant over ZZ, divides every exact parent-bracket factor over QQ,
and primitive-normalizes the remaining polynomial.  Equal normalized
polynomials are precisely the residual walls that are identical in this
chart after localization at the 70 parent brackets.

The build mode writes every factor fingerprint, occurrence-to-factor map,
and stripped parent-bracket list.  Replay recomputes the complete polynomial
census from scratch and compares all arrays.  No floating point arithmetic
or external computer-algebra package is used.
"""

from __future__ import annotations

import argparse
import hashlib
from collections import Counter
from fractions import Fraction
from itertools import combinations, permutations
from math import gcd, lcm
from pathlib import Path

import numpy as np

import DIAG9_GRAPH_verify_row2599_slice as row2599


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "DIAG9_GRAPH_global_factor_census.npz"
FORMAT = "diag9-global-residual-factor-census-v1"
NVARIABLES = 9
ZERO_EXPONENT = (0,) * NVARIABLES
PERMUTATIONS = tuple(
    (
        permutation,
        -1
        if sum(
            permutation[left] > permutation[right]
            for left in range(len(permutation))
            for right in range(left + 1, len(permutation))
        )
        & 1
        else 1,
    )
    for permutation in permutations(range(4))
)

# Immutable digest of every exact sparse fingerprint and occurrence map.
EXPECTED_DIGEST = "8dd371e34f9af178c49d4d0152864a394a0b2defcf16e673ddf885feb6ec0071"


def clean(polynomial):
    return {monomial: value for monomial, value in polynomial.items() if value}


def constant(value):
    return {} if not value else {ZERO_EXPONENT: Fraction(value)}


def variable(index):
    exponent = [0] * NVARIABLES
    exponent[index] = 1
    return {tuple(exponent): Fraction(1)}


def add(left, right, scale=1):
    answer = dict(left)
    for monomial, coefficient in right.items():
        answer[monomial] = answer.get(monomial, 0) + scale * coefficient
        if not answer[monomial]:
            del answer[monomial]
    return answer


def multiply(left, right):
    if not left or not right:
        return {}
    answer = {}
    for first, first_coefficient in left.items():
        for second, second_coefficient in right.items():
            monomial = tuple(
                first[index] + second[index] for index in range(NVARIABLES)
            )
            answer[monomial] = (
                answer.get(monomial, 0)
                + first_coefficient * second_coefficient
            )
    return clean(answer)


def product(factors):
    answer = constant(1)
    for factor in factors:
        answer = multiply(answer, factor)
    return answer


def determinant(matrix):
    size = len(matrix)
    if size == 4:
        permutations_and_signs = PERMUTATIONS
    else:
        permutations_and_signs = []
        for permutation in permutations(range(size)):
            inversions = sum(
                permutation[left] > permutation[right]
                for left in range(size)
                for right in range(left + 1, size)
            )
            permutations_and_signs.append(
                (permutation, -1 if inversions & 1 else 1)
            )
    answer = {}
    for permutation, sign in permutations_and_signs:
        term = constant(sign)
        for row in range(size):
            term = multiply(term, matrix[row][permutation[row]])
            if not term:
                break
        answer = add(answer, term)
    return answer


def primitive(polynomial):
    """Return the unique lex-leading-positive primitive ZZ associate."""
    polynomial = clean(polynomial)
    if not polynomial:
        return {}
    denominator = 1
    for coefficient in polynomial.values():
        denominator = lcm(denominator, Fraction(coefficient).denominator)
    integers = {
        monomial: int(Fraction(coefficient) * denominator)
        for monomial, coefficient in polynomial.items()
    }
    divisor = 0
    for coefficient in integers.values():
        divisor = gcd(divisor, abs(coefficient))
    integers = {
        monomial: coefficient // divisor
        for monomial, coefficient in integers.items()
    }
    if integers[max(integers)] < 0:
        integers = {
            monomial: -coefficient
            for monomial, coefficient in integers.items()
        }
    return integers


def polynomial_key(polynomial):
    return tuple(sorted(primitive(polynomial).items()))


def total_degree(polynomial):
    return max((sum(monomial) for monomial in polynomial), default=-1)


def divides_monomial(dividend, divisor):
    return all(left >= right for left, right in zip(dividend, divisor))


def divide_exact(dividend, divisor):
    """Exact single-divisor multivariate division in lex order over QQ."""
    remainder = {
        monomial: Fraction(coefficient)
        for monomial, coefficient in dividend.items()
    }
    divisor = {
        monomial: Fraction(coefficient)
        for monomial, coefficient in divisor.items()
    }
    quotient = {}
    leading_divisor = max(divisor)
    leading_coefficient = divisor[leading_divisor]
    while remainder:
        leading_remainder = max(remainder)
        if not divides_monomial(leading_remainder, leading_divisor):
            return None
        shift = tuple(
            left - right
            for left, right in zip(leading_remainder, leading_divisor)
        )
        coefficient = remainder[leading_remainder] / leading_coefficient
        quotient[shift] = quotient.get(shift, 0) + coefficient
        for monomial, value in divisor.items():
            target = tuple(
                monomial[index] + shift[index]
                for index in range(NVARIABLES)
            )
            remainder[target] = remainder.get(target, 0) - coefficient * value
            if not remainder[target]:
                del remainder[target]
    return clean(quotient)


def normalized_matrix():
    one, zero = constant(1), constant(0)
    a, b, c, d, e, f, g, h, i = (
        variable(index) for index in range(NVARIABLES)
    )
    return (
        (one, zero, zero, zero, one, one, one, one),
        (zero, one, zero, zero, one, a, d, g),
        (zero, zero, one, zero, one, b, e, h),
        (zero, zero, zero, one, one, c, f, i),
    )


def square_minor(matrix, columns):
    return determinant(
        tuple(
            tuple(matrix[row][column] for column in columns)
            for row in range(4)
        )
    )


def normal(matrix, triple):
    answer = []
    for omitted in range(4):
        rows = tuple(row for row in range(4) if row != omitted)
        minor = tuple(
            tuple(matrix[row][column] for column in triple)
            for row in rows
        )
        cofactor = determinant(minor)
        if (omitted + 3) & 1:
            cofactor = {monomial: -value for monomial, value in cofactor.items()}
        answer.append(cofactor)
    return tuple(answer)


def derived(normals, fourset):
    return determinant(
        tuple(
            tuple(normals[column][row] for column in fourset)
            for row in range(4)
        )
    )


def bracket_records(matrix):
    records = []
    all_brackets = []
    for basis in combinations(range(8), 4):
        polynomial = primitive(square_minor(matrix, basis))
        if not polynomial:
            raise AssertionError("normalized chart has an identically zero bracket")
        all_brackets.append((basis, polynomial))
        if total_degree(polynomial) > 0:
            records.append((basis, polynomial))
    if len(all_brackets) != 70 or len(records) != 62:
        raise AssertionError("wrong normalized parent-bracket census")
    if len({polynomial_key(row[1]) for row in records}) != 62:
        raise AssertionError("nonconstant parent brackets are not distinct")
    # High degree first reduces the number of attempted divisions.
    records.sort(key=lambda row: (-total_degree(row[1]), row[0]))
    return tuple(records)


def strip_parent_units(polynomial, brackets):
    raw = primitive(polynomial)
    quotient = dict(raw)
    stripped = []
    while True:
        degree = total_degree(quotient)
        leading = max(quotient)
        found = False
        for index, (_, bracket) in enumerate(brackets):
            if total_degree(bracket) > degree:
                continue
            if not divides_monomial(leading, max(bracket)):
                continue
            candidate = divide_exact(quotient, bracket)
            if candidate is None:
                continue
            quotient = primitive(candidate)
            stripped.append(index)
            found = True
            break
        if not found:
            break

    # Exact reconstruction is an internal check independent of the quotient
    # normalization choices made after each division.
    reconstructed = product(
        [quotient] + [brackets[index][1] for index in stripped]
    )
    if polynomial_key(reconstructed) != polynomial_key(raw):
        raise AssertionError("parent-unit stripping failed reconstruction")
    for _, bracket in brackets:
        if divide_exact(quotient, bracket) is not None:
            raise AssertionError("a parent bracket remains in a residual factor")
    return primitive(quotient), tuple(stripped)


def expected_crossing_factor():
    def exponent(*indices):
        answer = [0] * NVARIABLES
        for index in indices:
            answer[index] += 1
        return tuple(answer)

    # Display associate: -bdi+bfg+cdh-ceg+cei-cfh.
    return primitive(
        {
            exponent(1, 3, 8): -1,
            exponent(1, 5, 6): 1,
            exponent(2, 3, 7): 1,
            exponent(2, 4, 6): -1,
            exponent(2, 4, 8): 1,
            exponent(2, 5, 7): -1,
        }
    )


def flatten_keys(keys):
    offsets = [0]
    exponents = []
    coefficients = []
    for key in keys:
        for exponent, coefficient in key:
            exponents.append(exponent)
            coefficients.append(int(coefficient))
        offsets.append(len(exponents))
    if any(abs(value) >= 2**63 for value in coefficients):
        raise AssertionError("factor coefficient exceeds int64 certificate format")
    return (
        np.asarray(offsets, dtype=np.uint32),
        np.asarray(exponents, dtype=np.uint8).reshape((-1, NVARIABLES)),
        np.asarray(coefficients, dtype=np.int64),
    )


def unflatten_keys(offsets, exponents, coefficients):
    keys = []
    for index in range(len(offsets) - 1):
        start, stop = int(offsets[index]), int(offsets[index + 1])
        keys.append(
            tuple(
                (
                    tuple(map(int, exponents[position])),
                    int(coefficients[position]),
                )
                for position in range(start, stop)
            )
        )
    return tuple(keys)


def count_distribution(counter):
    distribution = Counter(counter.values())
    values = np.asarray(sorted(distribution), dtype=np.uint32)
    counts = np.asarray([distribution[value] for value in values], dtype=np.uint32)
    return values, counts


def exact_census(progress=True):
    matrix = normalized_matrix()
    brackets = bracket_records(matrix)
    normals = tuple(normal(matrix, triple) for triple in row2599.topes.TRIPLES)
    if len(normals) != 56:
        raise AssertionError("wrong derived-normal census")
    foursets = row2599.residual_foursets()

    with np.load(row2599.ROADMAP, allow_pickle=False) as certificate:
        crossing = frozenset(
            tuple(map(int, row)) for row in certificate["wall_fourset"]
        )
    if len(crossing) != 65 or not crossing <= frozenset(foursets):
        raise AssertionError("wrong row-2599 crossing occurrence set")

    raw_counter = Counter()
    factor_occurrence_keys = []
    unit_offsets = [0]
    unit_indices = []
    crossing_raw_counter = Counter()
    crossing_factor_counter = Counter()
    crossing_unit_counter = Counter()
    crossing_occurrence_indices = []

    for occurrence_index, fourset in enumerate(foursets):
        raw = primitive(derived(normals, fourset))
        if not raw:
            raise AssertionError("a residual occurrence vanished identically")
        raw_key = polynomial_key(raw)
        raw_counter[raw_key] += 1
        factor, units = strip_parent_units(raw, brackets)
        factor_key = polynomial_key(factor)
        factor_occurrence_keys.append(factor_key)
        unit_indices.extend(units)
        unit_offsets.append(len(unit_indices))

        if fourset in crossing:
            crossing_occurrence_indices.append(occurrence_index)
            crossing_raw_counter[raw_key] += 1
            crossing_factor_counter[factor_key] += 1
            crossing_unit_counter[len(units)] += 1

        if progress and (occurrence_index + 1) % 5_000 == 0:
            print(
                f"expanded {occurrence_index + 1}/{len(foursets)} residual occurrences",
                flush=True,
            )

    if len(factor_occurrence_keys) != 84_840:
        raise AssertionError("wrong global residual occurrence count")
    expected_q = polynomial_key(expected_crossing_factor())
    if len(crossing_raw_counter) != 57:
        raise AssertionError("wrong 65-crossing raw proportionality census")
    if Counter(crossing_raw_counter.values()) != Counter({1: 53, 2: 3, 6: 1}):
        raise AssertionError("wrong 65-crossing raw class multiplicities")
    if crossing_factor_counter != Counter({expected_q: 65}):
        raise AssertionError("the 65 crossing occurrences do not share q")
    if crossing_unit_counter != Counter({1: 59, 0: 6}):
        raise AssertionError("wrong 65-crossing bracket-unit census")
    if crossing_raw_counter[expected_q] != 6:
        raise AssertionError("six unit-free occurrences do not equal q")

    factor_keys = tuple(sorted(set(factor_occurrence_keys)))
    factor_index = {key: index for index, key in enumerate(factor_keys)}
    occurrence_factor = np.asarray(
        [factor_index[key] for key in factor_occurrence_keys], dtype=np.uint32
    )
    factor_counter = Counter(occurrence_factor.tolist())
    factor_multiplicity = np.asarray(
        [factor_counter[index] for index in range(len(factor_keys))],
        dtype=np.uint32,
    )
    if len(raw_counter) != 76_498:
        raise AssertionError("wrong raw proportionality class count")
    if Counter(raw_counter.values()) != Counter(
        {1: 72_906, 2: 2_652, 3: 70, 5: 72, 6: 174,
         7: 174, 8: 270, 9: 162, 10: 18}
    ):
        raise AssertionError("wrong raw proportionality multiplicities")
    if len(factor_keys) != 26_740:
        raise AssertionError("wrong localized residual factor count")
    if Counter(factor_counter.values()) != Counter(
        {1: 25_200, 2: 420, 15: 280, 65: 840}
    ):
        raise AssertionError("wrong localized factor multiplicities")
    if Counter(np.diff(np.asarray(unit_offsets))) != Counter(
        {0: 32_760, 1: 52_080}
    ):
        raise AssertionError("wrong stripped-unit count distribution")
    if Counter(unit_indices) != Counter({index: 840 for index in range(62)}):
        raise AssertionError("parent-bracket units are not uniformly distributed")

    factor_offset, factor_exponent, factor_coefficient = flatten_keys(factor_keys)
    crossing_raw_keys = tuple(sorted(crossing_raw_counter))
    (
        crossing_raw_offset,
        crossing_raw_exponent,
        crossing_raw_coefficient,
    ) = flatten_keys(crossing_raw_keys)
    crossing_raw_multiplicity = np.asarray(
        [crossing_raw_counter[key] for key in crossing_raw_keys], dtype=np.uint8
    )
    raw_values, raw_counts = count_distribution(raw_counter)
    factor_values, factor_counts = count_distribution(
        Counter({index: int(value) for index, value in enumerate(factor_multiplicity)})
    )

    return {
        "format": np.asarray(FORMAT),
        "occurrence_fourset": np.asarray(foursets, dtype=np.uint8),
        "parent_bracket_label": np.asarray(
            [basis for basis, _ in brackets], dtype=np.uint8
        ),
        "factor_offset": factor_offset,
        "factor_exponent": factor_exponent,
        "factor_coefficient": factor_coefficient,
        "factor_multiplicity": factor_multiplicity,
        "occurrence_factor": occurrence_factor,
        "occurrence_unit_offset": np.asarray(unit_offsets, dtype=np.uint32),
        "occurrence_unit_index": np.asarray(unit_indices, dtype=np.uint8),
        "raw_class_count": np.asarray(len(raw_counter), dtype=np.uint32),
        "raw_multiplicity_value": raw_values,
        "raw_multiplicity_class_count": raw_counts,
        "factor_multiplicity_value": factor_values,
        "factor_multiplicity_class_count": factor_counts,
        "crossing_occurrence_index": np.asarray(
            crossing_occurrence_indices, dtype=np.uint32
        ),
        "crossing_raw_offset": crossing_raw_offset,
        "crossing_raw_exponent": crossing_raw_exponent,
        "crossing_raw_coefficient": crossing_raw_coefficient,
        "crossing_raw_multiplicity": crossing_raw_multiplicity,
        "crossing_common_factor": np.asarray(
            factor_index[expected_q], dtype=np.uint32
        ),
    }


def semantic_digest(payload):
    digest = hashlib.sha256()
    for name in sorted(payload):
        array = np.asarray(payload[name])
        digest.update(name.encode("ascii"))
        digest.update(str(array.dtype).encode("ascii"))
        digest.update(repr(array.shape).encode("ascii"))
        digest.update(array.tobytes())
    return digest.hexdigest()


def compare_payload(left, right):
    if set(left) != set(right):
        raise AssertionError("certificate field set differs from exact replay")
    for name in sorted(left):
        if not np.array_equal(np.asarray(left[name]), np.asarray(right[name])):
            raise AssertionError(f"certificate field mismatch: {name}")


def summary(payload):
    multiplicity = np.asarray(payload["factor_multiplicity"], dtype=np.uint32)
    unit_offsets = np.asarray(payload["occurrence_unit_offset"], dtype=np.uint32)
    unit_counts = np.diff(unit_offsets)
    return {
        "occurrences": int(len(payload["occurrence_fourset"])),
        "raw_classes": int(payload["raw_class_count"]),
        "residual_factor_classes": int(len(multiplicity)),
        "largest_factor_class": int(multiplicity.max()),
        "unit_count_distribution": dict(
            sorted(Counter(map(int, unit_counts)).items())
        ),
        "factor_multiplicity_distribution": dict(
            zip(
                map(int, payload["factor_multiplicity_value"]),
                map(int, payload["factor_multiplicity_class_count"]),
            )
        ),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--build", action="store_true", help="write the exact NPZ certificate"
    )
    args = parser.parse_args()

    replay = exact_census(progress=True)
    digest = semantic_digest(replay)
    if EXPECTED_DIGEST is not None and digest != EXPECTED_DIGEST:
        raise AssertionError("global factor semantic digest changed")

    if args.build:
        CERTIFICATE.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(CERTIFICATE, **replay)
        print(f"WROTE {CERTIFICATE}")
    else:
        with np.load(CERTIFICATE, allow_pickle=False) as stored:
            certificate = {name: stored[name] for name in stored.files}
        compare_payload(certificate, replay)

    # The serialized sparse fingerprints must round-trip exactly.
    factor_keys = unflatten_keys(
        replay["factor_offset"],
        replay["factor_exponent"],
        replay["factor_coefficient"],
    )
    if len(factor_keys) != len(replay["factor_multiplicity"]):
        raise AssertionError("factor fingerprint round-trip failed")
    crossing_keys = unflatten_keys(
        replay["crossing_raw_offset"],
        replay["crossing_raw_exponent"],
        replay["crossing_raw_coefficient"],
    )
    if len(crossing_keys) != 57:
        raise AssertionError("crossing raw fingerprint round-trip failed")

    print("PASS:", summary(replay))
    print("PASS: 65 center occurrences have raw class sizes 6,2,2,2,1x53")
    print("PASS: their exact QQ gcd is -bdi+bfg+cdh-ceg+cei-cfh up to sign")
    print(f"SEMANTIC SHA256: {digest}")
    print("THEOREM: equal factor IDs are identical localized residual walls")
    print("SCOPE: this is an equation census, not a chamber-coverage theorem")


if __name__ == "__main__":
    main()
