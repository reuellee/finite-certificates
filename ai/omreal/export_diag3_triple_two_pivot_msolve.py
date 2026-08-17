#!/usr/bin/env python3
"""Export the exact diagonal-three hard canary for ``msolve -S``.

The first eight polynomials are the two residual equations after eliminating
the height coordinate and the six ``M_da*`` critical minors.  The last
polynomial is the product of the six required localizers.  Consequently,
``msolve -S`` computes the saturation of the critical ideal by precisely the
base-cell units and the two target walls.

This script only prepares a modular discovery calculation.  A modular unit
ideal is not an exact characteristic-zero certificate by itself.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import explore_diag3_triple_two_pivot_groebner as pilot  # noqa: E402
import verify_diag3_triple_boundary_stratification as boundary  # noqa: E402


DEFAULT_ORDER = "aechdfgi"


def is_prime_32(value):
    if value < 2:
        return False
    if value % 2 == 0:
        return value == 2
    divisor = 3
    while divisor * divisor <= value:
        if value % divisor == 0:
            return False
        divisor += 2
    return True


def multiply_all(polynomials):
    answer = {boundary.ZERO: 1}
    for polynomial in polynomials:
        answer = boundary.multiply(answer, polynomial)
    return answer


def reorder(polynomial, variables):
    indices = tuple(boundary.VARIABLES.index(variable) for variable in variables)
    return {
        tuple(monomial[index] for index in indices): coefficient
        for monomial, coefficient in polynomial.items()
        if coefficient
    }


def term_key(item):
    monomial, _coefficient = item
    return (-sum(monomial), tuple(-exponent for exponent in monomial))


def format_polynomial(polynomial, variables, prime):
    terms = []
    for monomial, coefficient in sorted(polynomial.items(), key=term_key):
        coefficient %= prime
        if not coefficient:
            continue
        if coefficient > prime // 2:
            coefficient -= prime
        factors = []
        for variable, exponent in zip(variables, monomial):
            if exponent == 1:
                factors.append(variable)
            elif exponent:
                factors.append(f"{variable}^{exponent}")
        body = "*".join(factors)
        if not body:
            rendered = str(coefficient)
        elif coefficient == 1:
            rendered = body
        elif coefficient == -1:
            rendered = f"-{body}"
        else:
            rendered = f"{coefficient}*{body}"
        if terms and coefficient > 0:
            rendered = "+" + rendered
        terms.append(rendered)
    return "".join(terms) or "0"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prime", type=int, required=True)
    parser.add_argument("--order", default=DEFAULT_ORDER)
    parser.add_argument("--output", type=Path, required=True)
    arguments = parser.parse_args()

    variables = tuple(arguments.order)
    if sorted(variables) != sorted(pilot.VARIABLES):
        raise SystemExit(
            f"--order must be a permutation of {''.join(pilot.VARIABLES)}"
        )
    if (
        arguments.prime < 2**16
        or arguments.prime >= 2**31
        or not is_prime_32(arguments.prime)
    ):
        raise SystemExit(
            "--prime must be a prime in [2^16, 2^31) for msolve -S"
        )

    generators, units, census = pilot.build_exact_system()
    localizer = multiply_all(units)
    polynomials = generators + (localizer,)
    compact = tuple(reorder(polynomial, variables) for polynomial in polynomials)
    lines = [",".join(variables), str(arguments.prime)]
    lines.extend(
        format_polynomial(polynomial, variables, arguments.prime)
        + ("," if index + 1 < len(compact) else "")
        for index, polynomial in enumerate(compact)
    )
    payload = "\n".join(lines) + "\n"
    arguments.output.write_text(payload, encoding="ascii")

    print("OUTPUT", arguments.output)
    print("SHA256", hashlib.sha256(payload.encode("ascii")).hexdigest())
    print("PRIME", arguments.prime)
    print("ORDER", arguments.order)
    print("SYSTEM", census)
    print(
        "GENERATORS",
        tuple((max(map(sum, polynomial)), len(polynomial)) for polynomial in generators),
    )
    print("LOCALIZER", (max(map(sum, localizer)), len(localizer)))
    print("SCOPE discovery-only input for: msolve -S -g 2 -f INPUT")


if __name__ == "__main__":
    main()
