#!/usr/bin/env python3
"""Modular Gröbner discovery for the regular diagonal-three critical locus.

The 21-minor parent-cell system is replaced by Lagrange multiplier equations
on the exact eight-variable chart.  This describes the critical locus on
the smooth part of the two-residual complete intersection.  A separate
singular-locus calculation is still required before any global conclusion.

All output is discovery-only.  A finite-field result is not a rational
certificate and does not change theorem accounting.
"""

from __future__ import annotations

import argparse
import heapq
import json
from pathlib import Path
import sys
import time


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import verify_diag3_triple_boundary_stratification as boundary  # noqa: E402


ACTIVE = tuple(variable for variable in range(9) if variable != boundary.HEIGHT)
Y_NAMES = tuple(boundary.VARIABLES[variable] for variable in ACTIVE)
VARIABLES = ()
ZERO = ()
Z_INDEX = -1
Z_INDICES = ()
LAMBDA_INDEX = -1
MU_INDEX = -1
Y_INDICES = ()
UNIT_FACTORS = ()


def configure_order(order, separate_inverse_count=0):
    global VARIABLES, ZERO, Z_INDEX, Z_INDICES, LAMBDA_INDEX, MU_INDEX, Y_INDICES
    z_names = (
        tuple(f"z{index}" for index in range(separate_inverse_count))
        if separate_inverse_count
        else ("z",)
    )
    if order == "aux-first":
        VARIABLES = z_names + ("lambda", "mu") + Y_NAMES
    elif order == "aux-last":
        VARIABLES = Y_NAMES + ("lambda", "mu") + z_names
    else:
        raise ValueError(f"unknown variable order {order}")
    ZERO = (0,) * len(VARIABLES)
    Z_INDICES = tuple(VARIABLES.index(name) for name in z_names)
    Z_INDEX = Z_INDICES[0]
    LAMBDA_INDEX = VARIABLES.index("lambda")
    MU_INDEX = VARIABLES.index("mu")
    Y_INDICES = tuple(VARIABLES.index(name) for name in Y_NAMES)


def add(left, right, prime):
    answer = dict(left)
    for monomial, coefficient in right.items():
        value = (answer.get(monomial, 0) + coefficient) % prime
        if value:
            answer[monomial] = value
        else:
            answer.pop(monomial, None)
    return answer


def subtract(left, right, prime):
    return add(
        left,
        {monomial: -coefficient for monomial, coefficient in right.items()},
        prime,
    )


def multiply(left, right, prime):
    answer = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial = tuple(
                x + y for x, y in zip(left_monomial, right_monomial)
            )
            answer[monomial] = (
                answer.get(monomial, 0)
                + left_coefficient * right_coefficient
            ) % prime
    return {monomial: coefficient for monomial, coefficient in answer.items() if coefficient}


def variable(index):
    monomial = [0] * len(VARIABLES)
    monomial[index] = 1
    return {tuple(monomial): 1}


def lift_y(polynomial, prime):
    answer = {}
    for monomial, coefficient in polynomial.items():
        residue = coefficient % prime
        if not residue:
            continue
        lifted = [0] * len(VARIABLES)
        for target, source in zip(Y_INDICES, ACTIVE):
            lifted[target] = monomial[source]
        answer[tuple(lifted)] = residue
    return answer


def build_system(
    prime,
    mode,
    excluded_walls=(),
    localized_units=False,
    separate_inverses=False,
):
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
            boundary.multiply(t, boundary.derivative(u, coordinate)),
            boundary.multiply(u, boundary.derivative(t, coordinate)),
        )
        for coordinate in ACTIVE
    )

    lifted_reduced = tuple(lift_y(polynomial, prime) for polynomial in reduced)
    lam = variable(LAMBDA_INDEX)
    mu = variable(MU_INDEX)
    equations = list(lifted_reduced)
    for coordinate, height_entry in zip(ACTIVE, height_numerator):
        lambda_gradient = multiply(
            lam,
            lift_y(boundary.derivative(reduced[0], coordinate), prime),
            prime,
        )
        mu_gradient = multiply(
            mu,
            lift_y(boundary.derivative(reduced[1], coordinate), prime),
            prime,
        )
        if mode == "critical":
            equation = subtract(
                lift_y(height_entry, prime), lambda_gradient, prime
            )
            equation = subtract(equation, mu_gradient, prime)
        else:
            equation = add(lambda_gradient, mu_gradient, prime)
        equations.append(equation)
    if mode == "singular-lambda":
        equations.append(subtract(lam, {ZERO: 1}, prime))
    elif mode == "singular-mu":
        equations.append(subtract(mu, {ZERO: 1}, prime))
    elif mode != "critical":
        raise ValueError(f"unknown system mode {mode}")
    localizer_factors = [u, t]
    walls = boundary.parent_wall_map()
    for label in excluded_walls:
        wall_constant, wall_coefficient = boundary.split_linear(
            walls[label], boundary.HEIGHT
        )
        wall_numerator = boundary.add(
            boundary.multiply(t, wall_constant),
            boundary.multiply(u, wall_coefficient),
        )
        localizer_factors.append(wall_numerator)
    lifted_units = tuple(lift_y(factor, prime) for factor in localizer_factors)
    if not localized_units:
        if separate_inverses:
            if len(Z_INDICES) != len(lifted_units):
                raise AssertionError("wrong separate-inverse variable count")
            equations.extend(
                subtract(
                    multiply(variable(index), factor, prime),
                    {ZERO: 1},
                    prime,
                )
                for index, factor in zip(Z_INDICES, lifted_units)
            )
        else:
            localizer = {ZERO: 1}
            for factor in lifted_units:
                localizer = multiply(localizer, factor, prime)
            inverse = subtract(
                multiply(variable(Z_INDEX), localizer, prime),
                {ZERO: 1},
                prime,
            )
            equations.append(inverse)
    return tuple(equations), lifted_units


def order_key(monomial):
    return sum(monomial), tuple(-value for value in reversed(monomial))


def leading_monomial(polynomial):
    return max(polynomial, key=order_key)


def divides(left, right):
    return all(x <= y for x, y in zip(left, right))


def quotient(right, left):
    return tuple(y - x for x, y in zip(left, right))


def lcm(left, right):
    return tuple(max(x, y) for x, y in zip(left, right))


def relatively_prime(left, right):
    return all(not (x and y) for x, y in zip(left, right))


def multiply_monomial(polynomial, monomial, coefficient, prime):
    return {
        tuple(x + y for x, y in zip(exponent, monomial)): value * coefficient % prime
        for exponent, value in polynomial.items()
        if value * coefficient % prime
    }


def monic(polynomial, prime):
    if not polynomial:
        return {}
    lead = leading_monomial(polynomial)
    inverse = pow(polynomial[lead], -1, prime)
    return {
        monomial: coefficient * inverse % prime
        for monomial, coefficient in polynomial.items()
        if coefficient * inverse % prime
    }


def normal_form(polynomial, basis, prime):
    polynomial = dict(polynomial)
    remainder = {}
    while polynomial:
        lead = leading_monomial(polynomial)
        reducers = tuple(
            reducer
            for reducer in basis
            if divides(leading_monomial(reducer), lead)
        )
        if not reducers:
            remainder[lead] = polynomial.pop(lead)
            continue
        # A sparse reducer is usually much cheaper than the first matching
        # row and sharply limits fill-in for these dense derivative systems.
        reducer = min(reducers, key=len)
        reducer_lead = leading_monomial(reducer)
        multiple = multiply_monomial(
            reducer,
            quotient(lead, reducer_lead),
            polynomial[lead],
            prime,
        )
        polynomial = subtract(polynomial, multiple, prime)
    return monic(remainder, prime)


def exact_quotient(dividend, divisor, prime):
    quotient_polynomial = {}
    remainder = dict(dividend)
    divisor_lead = leading_monomial(divisor)
    divisor_coefficient = divisor[divisor_lead]
    inverse = pow(divisor_coefficient, -1, prime)
    while remainder:
        remainder_lead = leading_monomial(remainder)
        if not divides(divisor_lead, remainder_lead):
            return None
        coefficient = remainder[remainder_lead] * inverse % prime
        monomial = quotient(remainder_lead, divisor_lead)
        quotient_polynomial[monomial] = (
            quotient_polynomial.get(monomial, 0) + coefficient
        ) % prime
        remainder = subtract(
            remainder,
            multiply_monomial(divisor, monomial, coefficient, prime),
            prime,
        )
    return monic(quotient_polynomial, prime)


def localized_normal_form(polynomial, basis, prime):
    polynomial = normal_form(polynomial, basis, prime)
    changed = True
    while polynomial and changed:
        changed = False
        for factor in UNIT_FACTORS:
            quotient_polynomial = exact_quotient(polynomial, factor, prime)
            if quotient_polynomial is None:
                continue
            polynomial = normal_form(quotient_polynomial, basis, prime)
            changed = True
            break
    return polynomial


def s_polynomial(left, right, prime):
    left_lead = leading_monomial(left)
    right_lead = leading_monomial(right)
    common = lcm(left_lead, right_lead)
    return subtract(
        multiply_monomial(left, quotient(common, left_lead), 1, prime),
        multiply_monomial(right, quotient(common, right_lead), 1, prime),
        prime,
    )


def dimension_upper_bound(basis):
    supports = tuple(
        frozenset(index for index, value in enumerate(leading_monomial(poly)) if value)
        for poly in basis
    )
    best = 0
    for mask in range(1 << len(VARIABLES)):
        size = mask.bit_count()
        if size <= best:
            continue
        chosen = frozenset(
            index for index in range(len(VARIABLES)) if mask >> index & 1
        )
        if not any(support <= chosen for support in supports):
            best = size
    return best


def buchberger(generators, prime, maximum_basis, maximum_pairs, progress):
    basis = []
    for generator in sorted(generators, key=lambda poly: (max(map(sum, poly)), len(poly))):
        reduced = localized_normal_form(generator, basis, prime)
        if reduced:
            basis.append(reduced)
            if set(reduced) == {ZERO}:
                return basis, 0, True

    queue = []
    serial = 0
    for right in range(len(basis)):
        for left in range(right):
            left_lead = leading_monomial(basis[left])
            right_lead = leading_monomial(basis[right])
            if relatively_prime(left_lead, right_lead):
                continue
            common = lcm(left_lead, right_lead)
            heapq.heappush(queue, (sum(common), serial, left, right))
            serial += 1

    processed = 0
    started = time.monotonic()
    known_leads = {leading_monomial(polynomial) for polynomial in basis}
    while queue and len(basis) < maximum_basis and processed < maximum_pairs:
        sugar, _serial, left, right = heapq.heappop(queue)
        processed += 1
        candidate = localized_normal_form(
            s_polynomial(basis[left], basis[right], prime), basis, prime
        )
        if not candidate:
            continue
        lead = leading_monomial(candidate)
        if lead in known_leads:
            continue
        known_leads.add(lead)
        index = len(basis)
        basis.append(candidate)
        if progress:
            print(
                "NEW",
                index,
                "pair",
                processed,
                "sugar",
                sugar,
                "degree",
                max(map(sum, candidate)),
                "terms",
                len(candidate),
                "queue",
                len(queue),
                "seconds",
                f"{time.monotonic() - started:.2f}",
                flush=True,
            )
        if set(candidate) == {ZERO}:
            return basis, processed, True
        for old in range(index):
            old_lead = leading_monomial(basis[old])
            if relatively_prime(old_lead, lead):
                continue
            common = lcm(old_lead, lead)
            heapq.heappush(queue, (sum(common), serial, old, index))
            serial += 1
    return basis, processed, not queue


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prime", type=int, default=47)
    parser.add_argument("--maximum-basis", type=int, default=120)
    parser.add_argument("--maximum-pairs", type=int, default=1000)
    parser.add_argument(
        "--order", choices=("aux-first", "aux-last"), default="aux-first"
    )
    parser.add_argument(
        "--system",
        choices=("critical", "singular-lambda", "singular-mu"),
        default="critical",
    )
    parser.add_argument(
        "--exclude-walls",
        default="",
        help="comma-separated parent walls multiplied into the inverse localizer",
    )
    parser.add_argument(
        "--localized-units",
        action="store_true",
        help="strip exact unit factors during reduction instead of adding an inverse variable",
    )
    parser.add_argument(
        "--separate-inverses",
        action="store_true",
        help="use one low-degree inverse relation per localized factor",
    )
    parser.add_argument("--progress", action="store_true")
    arguments = parser.parse_args()
    excluded_walls = tuple(
        label for label in arguments.exclude_walls.split(",") if label
    )
    if arguments.localized_units and arguments.separate_inverses:
        raise ValueError("choose localized-unit division or separate inverses")
    separate_inverse_count = (
        2 + len(excluded_walls) if arguments.separate_inverses else 0
    )
    configure_order(arguments.order, separate_inverse_count)
    generators, unit_factors = build_system(
        arguments.prime,
        arguments.system,
        excluded_walls,
        arguments.localized_units,
        arguments.separate_inverses,
    )
    global UNIT_FACTORS
    UNIT_FACTORS = tuple(monic(factor, arguments.prime) for factor in unit_factors) if arguments.localized_units else ()
    print("VARIABLES", VARIABLES)
    print(
        "GENERATORS",
        len(generators),
        tuple((max(map(sum, poly)), len(poly)) for poly in generators),
    )
    print("SYSTEM", arguments.system)
    print("EXCLUDED_WALLS", excluded_walls)
    print("LOCALIZED_UNITS", len(UNIT_FACTORS))
    print("SEPARATE_INVERSES", len(Z_INDICES) if arguments.separate_inverses else 0)
    print("DISCOVERY_ONLY modular system; not a characteristic-zero certificate")
    basis, processed, complete = buchberger(
        generators,
        arguments.prime,
        arguments.maximum_basis,
        arguments.maximum_pairs,
        arguments.progress,
    )
    report = {
        "prime": arguments.prime,
        "basis": len(basis),
        "pairs_processed": processed,
        "complete": complete,
        "unit_ideal": any(set(polynomial) == {ZERO} for polynomial in basis),
        "leading_dimension_upper_bound": dimension_upper_bound(basis),
        "maximum_degree": max(max(map(sum, polynomial)) for polynomial in basis),
        "maximum_terms": max(map(len, basis)),
    }
    print("RESULT", report)


if __name__ == "__main__":
    main()
