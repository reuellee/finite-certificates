#!/usr/bin/env python3
"""Modular Macaulay discovery for the diagonal-three parent-cell chart.

This is deliberately an exploratory tool, not a characteristic-zero proof.
It builds the exact eight-variable reduction of the hard canary, keeps the
21 parent-cell pivot minors, and adds one Rabinowitsch relation

    z * (di-fg) * (i-f) - 1.

The sparse row rank over a requested prime measures the truncated quotient.
Results are useful for choosing the next exact elimination order, but never
advance theorem accounting on their own.
"""

from __future__ import annotations

import argparse
from itertools import combinations, combinations_with_replacement
import json
from pathlib import Path
import sys
import time


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import verify_diag3_triple_boundary_stratification as boundary  # noqa: E402


ACTIVE = tuple(variable for variable in range(9) if variable != boundary.HEIGHT)
COMPACT_VARIABLES = tuple(boundary.VARIABLES[variable] for variable in ACTIVE) + ("z",)
COMPACT_ZERO = (0,) * len(COMPACT_VARIABLES)


def compact(polynomial):
    return {
        tuple(monomial[variable] for variable in ACTIVE) + (0,): coefficient
        for monomial, coefficient in polynomial.items()
    }


def compact_add(left, right):
    answer = dict(left)
    for monomial, coefficient in right.items():
        answer[monomial] = answer.get(monomial, 0) + coefficient
        if not answer[monomial]:
            del answer[monomial]
    return answer


def compact_multiply(left, right):
    answer = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial = tuple(
                x + y for x, y in zip(left_monomial, right_monomial)
            )
            answer[monomial] = answer.get(monomial, 0) + (
                left_coefficient * right_coefficient
            )
    return {monomial: coefficient for monomial, coefficient in answer.items() if coefficient}


def exact_degree(polynomial):
    return max(map(sum, polynomial), default=-1)


def monomials_of_degree(variable_count, degree):
    for chosen in combinations_with_replacement(range(variable_count), degree):
        exponent = [0] * variable_count
        for variable in chosen:
            exponent[variable] += 1
        yield tuple(exponent)


def monomial_table(variable_count, maximum_degree):
    monomials = []
    cumulative = []
    for degree in range(maximum_degree + 1):
        monomials.extend(monomials_of_degree(variable_count, degree))
        cumulative.append(tuple(monomials))
    # Within each degree use graded reverse lexicographic order.  Only the
    # order affects fill-in; the row rank is invariant.
    monomials.sort(key=lambda exponent: (sum(exponent), tuple(-value for value in reversed(exponent))))
    return tuple(monomials), tuple(cumulative)


def build_system():
    payload = json.loads(boundary.SYSTEM.read_text(encoding="ascii"))
    residual = tuple(
        boundary.decode_terms(record["terms"])
        for record in payload["equations"][:3]
    )
    t = boundary.subtract(boundary.coordinate(8), boundary.coordinate(5))
    u = boundary.subtract(
        boundary.multiply(boundary.coordinate(3), boundary.coordinate(8)),
        boundary.multiply(boundary.coordinate(5), boundary.coordinate(6)),
    )
    reduced = []
    for polynomial in residual[1:]:
        constant_part, coefficient = boundary.split_linear(
            polynomial, boundary.HEIGHT
        )
        reduced.append(
            boundary.add(
                boundary.multiply(t, constant_part),
                boundary.multiply(u, coefficient),
            )
        )
    reduced = tuple(reduced)
    height_numerator = tuple(
        boundary.subtract(
            boundary.multiply(t, boundary.derivative(u, variable)),
            boundary.multiply(u, boundary.derivative(t, variable)),
        )
        for variable in ACTIVE
    )
    pivot = ACTIVE.index(3)
    remaining = tuple(column for column in range(8) if column != pivot)
    pivot_minors = []
    for left, right in combinations(remaining, 2):
        chosen = (pivot, left, right)
        matrix = [[height_numerator[column] for column in chosen]]
        matrix.extend(
            [
                boundary.derivative(polynomial, ACTIVE[column])
                for column in chosen
            ]
            for polynomial in reduced
        )
        pivot_minors.append(boundary.determinant3(matrix))

    z = {(0,) * 8 + (1,): 1}
    inverse = compact_add(
        compact_multiply(z, compact(boundary.multiply(u, t))),
        {COMPACT_ZERO: -1},
    )
    generators = tuple(compact(polynomial) for polynomial in reduced)
    generators += (inverse,)
    generators += tuple(compact(polynomial) for polynomial in pivot_minors)
    return generators


def shifted_row(polynomial, shift, monomial_index, prime):
    row = {}
    for monomial, coefficient in polynomial.items():
        residue = coefficient % prime
        if not residue:
            continue
        shifted = tuple(left + right for left, right in zip(monomial, shift))
        column = monomial_index[shifted]
        row[column] = (row.get(column, 0) + residue) % prime
        if not row[column]:
            del row[column]
    return row


def insert_row(basis, row, prime):
    while row:
        pivot = max(row)
        coefficient = row[pivot]
        reducer = basis.get(pivot)
        if reducer is None:
            inverse = pow(coefficient, -1, prime)
            if inverse != 1:
                row = {
                    column: value * inverse % prime
                    for column, value in row.items()
                }
            basis[pivot] = row
            return True
        for column, value in reducer.items():
            reduced = (row.get(column, 0) - coefficient * value) % prime
            if reduced:
                row[column] = reduced
            else:
                row.pop(column, None)
    return False


def macaulay_rank(generators, degree, prime, progress=False):
    monomials, cumulative = monomial_table(len(COMPACT_VARIABLES), degree)
    monomial_index = {monomial: index for index, monomial in enumerate(monomials)}
    ordered = sorted(generators, key=lambda polynomial: (exact_degree(polynomial), len(polynomial)))
    basis = {}
    attempted = 0
    started = time.monotonic()
    for generator_index, polynomial in enumerate(ordered):
        generator_degree = exact_degree(polynomial)
        maximum_shift = degree - generator_degree
        if maximum_shift < 0:
            continue
        shifts = cumulative[maximum_shift]
        for shift in shifts:
            attempted += 1
            insert_row(
                basis,
                shifted_row(polynomial, shift, monomial_index, prime),
                prime,
            )
        if progress:
            print(
                "GEN",
                generator_index,
                "degree",
                generator_degree,
                "terms",
                len(polynomial),
                "shifts",
                len(shifts),
                "rank",
                len(basis),
                "seconds",
                f"{time.monotonic() - started:.2f}",
                flush=True,
            )
    return {
        "prime": prime,
        "degree": degree,
        "variables": len(COMPACT_VARIABLES),
        "monomials": len(monomials),
        "rows_attempted": attempted,
        "rank": len(basis),
        "quotient": len(monomials) - len(basis),
        "seconds": round(time.monotonic() - started, 3),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--degree", type=int, default=11)
    parser.add_argument("--prime", type=int, default=47)
    parser.add_argument("--progress", action="store_true")
    arguments = parser.parse_args()
    if arguments.prime < 2:
        raise ValueError("prime must be at least two")
    generators = build_system()
    census = tuple((exact_degree(polynomial), len(polynomial)) for polynomial in generators)
    print("VARIABLES", COMPACT_VARIABLES)
    print("GENERATORS", len(generators), "CENSUS", census)
    print("DISCOVERY_ONLY modular result; not a characteristic-zero certificate")
    print("RESULT", macaulay_rank(generators, arguments.degree, arguments.prime, arguments.progress))


if __name__ == "__main__":
    main()
