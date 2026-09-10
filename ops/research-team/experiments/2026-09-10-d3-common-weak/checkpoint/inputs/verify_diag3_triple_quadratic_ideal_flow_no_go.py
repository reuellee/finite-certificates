#!/usr/bin/env python3
"""Exact no-go for low-degree ideal-preserving flows on hard triples.

For a polynomial vector field V of coordinate degree at most two and a
3-by-3 matrix L of affine-linear polynomials, solve coefficientwise

    V(q_i) = sum_j L_ij q_j.

Five hard triple systems have full column rank already modulo 1,000,003.
The corresponding rational systems therefore have zero kernel.  This is a
bounded strategy regression, not a compactness theorem.
"""

from __future__ import annotations

from collections import defaultdict
import hashlib
from itertools import combinations_with_replacement
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402


TRIPLES = (
    (12_985, 16_183, 7_196),
    (20_355, 5_442, 5_949),
    (9_667, 16_486, 26_315),
    (9_758, 24_338, 15_810),
    (5_563, 4_373, 23_221),
)
PRIME = 1_000_003
NVARIABLES = 9
VECTOR_MONOMIALS = (
    ((0,) * NVARIABLES,)
    + tuple(
        tuple(int(index == variable) for index in range(NVARIABLES))
        for variable in range(NVARIABLES)
    )
    + tuple(
        tuple(
            int(index == left) + int(index == right)
            for index in range(NVARIABLES)
        )
        for left, right in combinations_with_replacement(range(NVARIABLES), 2)
    )
)
VECTOR_COLUMNS = NVARIABLES * len(VECTOR_MONOMIALS)
MULTIPLIER_COLUMNS = 3 * 3 * (1 + NVARIABLES)
NCOLUMNS = VECTOR_COLUMNS + MULTIPLIER_COLUMNS
EXPECTED = (
    ((12_985, 16_183, 7_196), 2_771, 585),
    ((20_355, 5_442, 5_949), 4_338, 585),
    ((9_667, 16_486, 26_315), 5_450, 585),
    ((9_758, 24_338, 15_810), 4_439, 585),
    ((5_563, 4_373, 23_221), 4_855, 585),
)
EXPECTED_SEMANTIC = (
    "c5eb24d2f574e65d848f5238d895fc38fc7baaa2a84ec6c3bed402d49bda51a0"
)


def system(polynomials):
    equations = defaultdict(dict)

    # V(q_i), with V_j an arbitrary polynomial of total degree at most two.
    for equation, polynomial in enumerate(polynomials):
        for exponent, coefficient in polynomial.items():
            for variable, power in enumerate(exponent):
                if not power:
                    continue
                derivative = list(exponent)
                derivative[variable] -= 1
                for monomial_index, vector_monomial in enumerate(VECTOR_MONOMIALS):
                    output = tuple(
                        derivative[index] + vector_monomial[index]
                        for index in range(NVARIABLES)
                    )
                    column = len(VECTOR_MONOMIALS) * variable + monomial_index
                    row = equations[equation, output]
                    row[column] = row.get(column, 0) + coefficient * power

    # -L_ij*q_j, with each multiplier affine-linear.
    for equation in range(3):
        for target, polynomial in enumerate(polynomials):
            offset = VECTOR_COLUMNS + (3 * equation + target) * 10
            for exponent, coefficient in polynomial.items():
                row = equations[equation, exponent]
                row[offset] = row.get(offset, 0) - coefficient
                for variable in range(NVARIABLES):
                    output = list(exponent)
                    output[variable] += 1
                    row = equations[equation, tuple(output)]
                    column = offset + 1 + variable
                    row[column] = row.get(column, 0) - coefficient
    return tuple(
        {column: value for column, value in row.items() if value}
        for _key, row in sorted(equations.items())
        if any(row.values())
    )


def rank_mod_prime(rows):
    basis = {}
    for source in rows:
        vector = {
            column: value % PRIME
            for column, value in source.items()
            if value % PRIME
        }
        while vector:
            pivot = min(vector)
            if pivot not in basis:
                inverse = pow(vector[pivot], PRIME - 2, PRIME)
                basis[pivot] = {
                    column: value * inverse % PRIME
                    for column, value in vector.items()
                }
                break
            scale = vector[pivot]
            for column, value in basis[pivot].items():
                result = (vector.get(column, 0) - scale * value) % PRIME
                if result:
                    vector[column] = result
                else:
                    vector.pop(column, None)
    return len(basis)


def main():
    if len(VECTOR_MONOMIALS) != 55 or NCOLUMNS != 585:
        raise AssertionError("bounded flow language changed")
    _occurrences, _occurrence_factor, factor_polynomials = labeled.factor_polynomials()
    reports = []
    semantic = hashlib.sha256(b"diag3-quadratic-ideal-flow-no-go-v1\0")
    for triple in TRIPLES:
        rows = system(tuple(factor_polynomials[factor] for factor in triple))
        rank = rank_mod_prime(rows)
        report = triple, len(rows), rank
        reports.append(report)
        semantic.update(repr(report).encode("ascii"))
        print("TRIPLE", triple, "SYSTEM", len(rows), "x", NCOLUMNS, "RANK", rank)
    if tuple(reports) != EXPECTED:
        raise AssertionError("hard-triple rank census changed")
    digest = semantic.hexdigest()
    if digest != EXPECTED_SEMANTIC:
        raise AssertionError(f"semantic changed: {digest}")
    print("SEMANTIC", digest)
    print("NO-GO all five bounded ideal-flow systems have zero rational kernel")
    print("CAVEAT higher-degree/nonalgebraic proper escapes remain untested")


if __name__ == "__main__":
    main()
