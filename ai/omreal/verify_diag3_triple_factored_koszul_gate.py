#!/usr/bin/env python3
"""Exact factored-Jacobian reduction and bounded unit-certificate gate.

On the hard-canary ``L=0`` branch, write

    E = H0 + e H1 + e^2 H2,       H2 = (i-f)L.

The five remaining critical equations are the five directional derivatives
of this expression.  Hence ``(1,e,e^2)`` annihilates the 3-by-5 directional
Jacobian of ``(H0,H1,H2)``.  This verifier checks that reduction exactly and
exhausts the ten individual 3-by-3 minors after parent-factor stripping.

It also replays a deliberately bounded degree-14 Macaulay search over F2 and
F3.  The targets are either transformed target wall multiplied by every
product of the four base localizers which still fits in degree 14.  Modular
misses are diagnostics, not characteristic-zero no-go theorems.
"""

from __future__ import annotations

from collections import Counter
from itertools import combinations, combinations_with_replacement, product
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import explore_diag3_triple_hypersurface_groebner as chart  # noqa: E402
import verify_diag3_triple_boundary_stratification as boundary  # noqa: E402
from verify_diag3_triple_quadratic_cover_no_go import (  # noqa: E402
    census,
    coefficients,
    exact_divide,
    strip_parent_factors,
)
from verify_diag3_triple_two_pivot_rank_drop import EXPECTED_P  # noqa: E402


DIRECTION_NAMES = ("c", "h", "V_f", "V_g", "V_i")
EXPECTED_H_CENSUS = ((235, 7, 10), (256, 6, 9), (103, 5, 8))
EXPECTED_MINORS = {
    (0, 1, 2): ((40_250, 16, 25), (34_203, 15, 24), ("2378",)),
    (0, 1, 3): ((33_426, 16, 25), (20_893, 15, 23), ("2357", "2378")),
    (0, 1, 4): ((39_682, 17, 26), (25_372, 16, 24), ("2357", "2378")),
    (0, 2, 3): ((44_865, 17, 26), (30_805, 16, 24), ("2378", "2458")),
    (0, 2, 4): ((51_187, 18, 27), (30_113, 16, 24), ("2378", "2378", "2458")),
    (0, 3, 4): (
        (42_265, 18, 27),
        (21_437, 16, 23),
        ("1238", "2357", "2378", "2458"),
    ),
    (1, 2, 3): ((43_718, 17, 26), (37_222, 16, 25), ("2378",)),
    (1, 2, 4): ((50_825, 18, 27), (37_084, 16, 25), ("2378", "2378")),
    (1, 3, 4): (
        (38_494, 18, 26),
        (18_459, 15, 22),
        ("1238", "2357", "2367", "2378"),
    ),
    (2, 3, 4): (
        (53_964, 19, 28),
        (31_378, 16, 24),
        ("1238", "2378", "2378", "2458"),
    ),
}

ACTIVE = (2, 3, 4, 5, 6, 7, 8)
MACAULAY_DEGREE = 14
EXPECTED_MONOMIALS = 116_280
EXPECTED_TARGETS = 88
EXPECTED_RANK = {2: 5_202, 3: 5_202}
EXPECTED_FIELD_SOLUTIONS = {2: 113, 3: 1_121}


def scale(polynomial, scalar):
    return {
        monomial: scalar * coefficient
        for monomial, coefficient in polynomial.items()
        if scalar * coefficient
    }


def direction(polynomial, index):
    d = boundary.coordinate(3)
    f = boundary.coordinate(5)
    g = boundary.coordinate(6)
    i = boundary.coordinate(8)
    t = boundary.subtract(i, f)
    if index == 0:
        return boundary.derivative(polynomial, 2)
    if index == 1:
        return boundary.derivative(polynomial, 7)
    if index == 2:
        return boundary.subtract(
            boundary.multiply(t, boundary.derivative(polynomial, 5)),
            boundary.multiply(
                boundary.subtract(d, g), boundary.derivative(polynomial, 3)
            ),
        )
    if index == 3:
        return boundary.add(
            boundary.multiply(i, boundary.derivative(polynomial, 6)),
            boundary.multiply(f, boundary.derivative(polynomial, 3)),
        )
    if index == 4:
        return boundary.subtract(
            boundary.multiply(
                boundary.multiply(i, t), boundary.derivative(polynomial, 8)
            ),
            boundary.multiply(
                boundary.multiply(f, boundary.subtract(g, d)),
                boundary.derivative(polynomial, 3),
            ),
        )
    raise ValueError(index)


def determinant3(entries):
    positive = boundary.add(
        boundary.add(
            boundary.multiply(
                boundary.multiply(entries[0][0], entries[1][1]), entries[2][2]
            ),
            boundary.multiply(
                boundary.multiply(entries[0][1], entries[1][2]), entries[2][0]
            ),
        ),
        boundary.multiply(
            boundary.multiply(entries[0][2], entries[1][0]), entries[2][1]
        ),
    )
    negative = boundary.add(
        boundary.add(
            boundary.multiply(
                boundary.multiply(entries[0][2], entries[1][1]), entries[2][0]
            ),
            boundary.multiply(
                boundary.multiply(entries[0][1], entries[1][0]), entries[2][2]
            ),
        ),
        boundary.multiply(
            boundary.multiply(entries[0][0], entries[1][2]), entries[2][1]
        ),
    )
    return boundary.subtract(positive, negative)


def factored_system():
    generators, localizers = chart.build_exact_system(("1468", "5678"))
    e_coefficients = coefficients(generators[0], 4)
    if set(e_coefficients) != {0, 1, 2}:
        raise AssertionError("E is no longer quadratic in e")
    h_polynomials = tuple(e_coefficients[index] for index in range(3))
    if tuple(map(census, h_polynomials)) != EXPECTED_H_CENSUS:
        raise AssertionError("the H0,H1,H2 census changed")

    e = boundary.coordinate(4)
    rebuilt = boundary.add(
        boundary.add(h_polynomials[0], boundary.multiply(e, h_polynomials[1])),
        boundary.multiply(boundary.multiply(e, e), h_polynomials[2]),
    )
    if rebuilt != generators[0]:
        raise AssertionError("the exact E decomposition changed")

    critical = (generators[1], generators[3], *generators[4:])
    for index, expected in enumerate(critical):
        actual = boundary.add(
            boundary.add(
                direction(h_polynomials[0], index),
                boundary.multiply(e, direction(h_polynomials[1], index)),
            ),
            boundary.multiply(
                boundary.multiply(e, e), direction(h_polynomials[2], index)
            ),
        )
        if actual != expected:
            raise AssertionError(
                f"the {DIRECTION_NAMES[index]} directional identity changed"
            )
    return h_polynomials, critical, localizers


def minor_census(h_polynomials):
    jacobian = tuple(
        tuple(direction(polynomial, column) for column in range(5))
        for polynomial in h_polynomials
    )
    walls = boundary.parent_wall_map()
    rows = []
    for columns in combinations(range(5), 3):
        minor = determinant3(
            tuple(tuple(jacobian[row][column] for column in columns) for row in range(3))
        )
        primitive, factors = strip_parent_factors(minor, walls)
        raw_expected, primitive_expected, factor_expected = EXPECTED_MINORS[columns]
        if (
            census(minor) != raw_expected
            or census(primitive) != primitive_expected
            or Counter(factors) != Counter(factor_expected)
        ):
            raise AssertionError(f"directional minor {columns} changed")
        if any(exact_divide(primitive, wall) is not None for wall in walls.values()):
            raise AssertionError(f"minor {columns} retained a parent factor")
        if any(
            exact_divide(primitive, polynomial) is not None
            for polynomial in (*h_polynomials, EXPECTED_P)
        ):
            raise AssertionError(f"minor {columns} retained a named branch factor")
        rows.append((columns, raw_expected, primitive_expected, factors))
    return tuple(rows)


def compact(polynomial):
    answer = {}
    for monomial, coefficient in polynomial.items():
        if monomial[0] or monomial[1]:
            raise AssertionError("an eliminated a or b variable returned")
        reduced = tuple(monomial[index] for index in ACTIVE)
        answer[reduced] = answer.get(reduced, 0) + coefficient
        if not answer[reduced]:
            del answer[reduced]
    return answer


def polynomial_degree(polynomial, prime=None):
    return max(
        (
            sum(monomial)
            for monomial, coefficient in polynomial.items()
            if prime is None or coefficient % prime
        ),
        default=-1,
    )


def multiply(left, right):
    answer = {}
    for left_monomial, left_value in left.items():
        for right_monomial, right_value in right.items():
            monomial = tuple(
                x + y
                for x, y in zip(left_monomial, right_monomial, strict=True)
            )
            answer[monomial] = answer.get(monomial, 0) + left_value * right_value
            if not answer[monomial]:
                del answer[monomial]
    return answer


def short_targets(localizers):
    base = tuple(map(compact, localizers[:4]))
    answer = []
    for target_index in (4, 5):
        root = compact(localizers[target_index])
        seen = {tuple(sorted(root.items())): ((), root)}
        frontier = [((), root)]
        while frontier:
            exponents, polynomial = frontier.pop()
            for base_index, factor in enumerate(base):
                candidate = multiply(polynomial, factor)
                if polynomial_degree(candidate) > MACAULAY_DEGREE:
                    continue
                key = tuple(sorted(candidate.items()))
                if key in seen:
                    continue
                record = exponents + (base_index,), candidate
                seen[key] = record
                frontier.append(record)
        answer.extend(
            (target_index, exponents, polynomial)
            for exponents, polynomial in seen.values()
        )
    if len(answer) != EXPECTED_TARGETS:
        raise AssertionError("the bounded localized-target census changed")
    return tuple(answer)


def monomial_tables():
    exact = [[] for _ in range(MACAULAY_DEGREE + 1)]
    for degree in range(MACAULAY_DEGREE + 1):
        for chosen in combinations_with_replacement(range(7), degree):
            exponent = [0] * 7
            for variable in chosen:
                exponent[variable] += 1
            exact[degree].append(tuple(exponent))
    all_monomials = []
    cumulative = []
    for rows in exact:
        all_monomials.extend(rows)
        cumulative.append(tuple(all_monomials))
    all_monomials.sort(
        key=lambda exponent: (
            sum(exponent),
            tuple(-value for value in reversed(exponent)),
        )
    )
    if len(all_monomials) != EXPECTED_MONOMIALS:
        raise AssertionError("the degree-14 monomial census changed")
    return tuple(cumulative), {
        monomial: index for index, monomial in enumerate(all_monomials)
    }


def f3_add(left, right):
    left_one, left_two = left
    right_one, right_two = right
    left_used = left_one | left_two
    right_used = right_one | right_two
    return (
        (right_one & ~left_used) | (left_one & ~right_used) | (left_two & right_two),
        (right_two & ~left_used) | (left_two & ~right_used) | (left_one & right_one),
    )


def vector(polynomial, shift, monomial_index, prime):
    if prime == 2:
        answer = 0
        for monomial, coefficient in polynomial.items():
            if coefficient & 1:
                target = tuple(
                    x + y for x, y in zip(monomial, shift, strict=True)
                )
                answer ^= 1 << monomial_index[target]
        return answer
    one = two = 0
    for monomial, coefficient in polynomial.items():
        residue = coefficient % 3
        if not residue:
            continue
        target = tuple(x + y for x, y in zip(monomial, shift, strict=True))
        bit = 1 << monomial_index[target]
        if residue == 1:
            one |= bit
        else:
            two |= bit
    return one, two


def insert(basis, row, prime):
    if prime == 2:
        while row:
            pivot = row.bit_length() - 1
            reducer = basis.get(pivot)
            if reducer is None:
                basis[pivot] = row
                return
            row ^= reducer
        return
    while row[0] | row[1]:
        pivot = (row[0] | row[1]).bit_length() - 1
        reducer = basis.get(pivot)
        if reducer is None:
            if row[1] >> pivot & 1:
                row = row[1], row[0]
            basis[pivot] = row
            return
        if row[0] >> pivot & 1:
            row = f3_add(row, (reducer[1], reducer[0]))
        else:
            row = f3_add(row, reducer)


def member(basis, row, prime):
    if prime == 2:
        while row:
            pivot = row.bit_length() - 1
            reducer = basis.get(pivot)
            if reducer is None:
                return False
            row ^= reducer
        return True
    while row[0] | row[1]:
        pivot = (row[0] | row[1]).bit_length() - 1
        reducer = basis.get(pivot)
        if reducer is None:
            return False
        if row[0] >> pivot & 1:
            row = f3_add(row, (reducer[1], reducer[0]))
        else:
            row = f3_add(row, reducer)
    return True


def macaulay_gate(h_polynomials, critical, localizers):
    generators = tuple(map(compact, (*h_polynomials, *critical)))
    targets = short_targets(localizers)
    cumulative, monomial_index = monomial_tables()
    zero = (0,) * 7
    reports = {}
    for prime in (2, 3):
        basis = {}
        attempted = 0
        for polynomial in sorted(
            generators,
            key=lambda item: (polynomial_degree(item, prime), len(item)),
        ):
            degree = polynomial_degree(polynomial, prime)
            for shift in cumulative[MACAULAY_DEGREE - degree]:
                attempted += 1
                insert(
                    basis,
                    vector(polynomial, shift, monomial_index, prime),
                    prime,
                )
        hits = tuple(
            (target, exponents)
            for target, exponents, polynomial in targets
            if member(
                basis, vector(polynomial, zero, monomial_index, prime), prime
            )
        )
        if len(basis) != EXPECTED_RANK[prime] or hits:
            raise AssertionError(f"the F{prime} bounded Macaulay gate changed")
        reports[prime] = len(basis), attempted, len(hits)
    return reports


def evaluate_mod(polynomial, point, prime):
    total = 0
    for monomial, coefficient in polynomial.items():
        term = coefficient
        for index, value in zip(ACTIVE, point, strict=True):
            term *= pow(value, monomial[index], prime)
        total += term
    return total % prime


def finite_field_gate(h_polynomials, critical, localizers):
    reports = {}
    equations = (*h_polynomials, *critical)
    for prime in (2, 3):
        solutions = 0
        localized = 0
        for point in product(range(prime), repeat=7):
            if not all(
                evaluate_mod(polynomial, point, prime) == 0
                for polynomial in equations
            ):
                continue
            solutions += 1
            if all(
                evaluate_mod(polynomial, point, prime) != 0
                for polynomial in localizers
            ):
                localized += 1
        if solutions != EXPECTED_FIELD_SOLUTIONS[prime] or localized:
            raise AssertionError(f"the F{prime} exhaustive point census changed")
        reports[prime] = solutions, localized
    return reports


def main():
    h_polynomials, critical, localizers = factored_system()
    minors = minor_census(h_polynomials)
    macaulay = macaulay_gate(h_polynomials, critical, localizers)
    fields = finite_field_gate(h_polynomials, critical, localizers)

    print("PASS E=H0+eH1+e^2H2 and all five directional identities over Z")
    for columns, raw, primitive, factors in minors:
        labels = "*".join(f"[{label}]" for label in factors) or "1"
        names = tuple(DIRECTION_NAMES[index] for index in columns)
        print(
            f"MINOR {names}: raw={raw[0]} primitive={primitive[0]} "
            f"parent_factors={labels}"
        )
    print("NO-GO none of the ten individual minors is a parent-unit product")
    for prime in (2, 3):
        rank, rows, hits = macaulay[prime]
        print(
            f"MACAULAY F{prime}: degree=14 rank={rank} rows={rows} "
            f"targets={EXPECTED_TARGETS} hits={hits}"
        )
        solutions, localized = fields[prime]
        print(
            f"POINTS F{prime}: solutions={solutions} localized={localized}"
        )
    print("GATE bounded short unit-minor/Koszul search exhausted without a hit")
    print("SCOPE exact identities plus bounded modular diagnostics; no Q no-go")
    print("DECISION pivot active effort to the global master closure object")


if __name__ == "__main__":
    main()
