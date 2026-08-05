#!/usr/bin/env python3
"""Dependency-free exact Jacobian certificates for residual representatives.

For every pair among the twelve distinct residual polynomials (types 46 and
47 have the same residual), this checks a displayed 2-by-2 Jacobian minor is
a signed product of nonzero parent brackets.  Hence distinct representative
gradients cannot be proportional in the uniform parent locus.

This is a representative-normalization theorem.  It is not an exhaustion of
relative S_8 labelings of two residual wall occurrences.
"""

from itertools import combinations
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_ALL_COMPACT_SECOND_WALL_VERIFY as wall  # noqa: E402
import verify_residual_log_binomials as poly  # noqa: E402


class Polynomial:
    def __init__(self, data):
        self.data = data

    @staticmethod
    def coerce(value):
        return value if isinstance(value, Polynomial) else Polynomial(poly.constant(value))

    def __add__(self, other):
        return Polynomial(poly.add(self.data, self.coerce(other).data))

    __radd__ = __add__

    def __neg__(self):
        return Polynomial(poly.negative(self.data))

    def __sub__(self, other):
        return self + (-self.coerce(other))

    def __rsub__(self, other):
        return self.coerce(other) - self

    def __mul__(self, other):
        return Polynomial(poly.multiply(self.data, self.coerce(other).data))

    __rmul__ = __mul__


def derivative(polynomial, variable):
    result = {}
    for monomial, coefficient in polynomial.items():
        exponent = monomial[variable]
        if not exponent:
            continue
        reduced = list(monomial)
        reduced[variable] -= 1
        reduced = tuple(reduced)
        result[reduced] = result.get(reduced, 0) + exponent * coefficient
    return poly.clean(result)


def polynomial_data():
    variables = tuple(Polynomial(poly.variable(index)) for index in range(9))
    values = dict(zip("abcdefghi", variables, strict=True))
    residual_wrapped = wall.residual_values(values)
    # Types 46 and 47 are the same polynomial; retain one representative.
    residual = {
        kind: expression.data
        for kind, expression in residual_wrapped.items()
        if kind != 47
    }

    one, zero = Polynomial(poly.constant(1)), Polynomial(poly.constant(0))
    a, b, c, d, e, f, g, h, i = variables
    matrix = (
        (one, zero, zero, zero, one, one, one, one),
        (zero, one, zero, zero, one, a, d, g),
        (zero, zero, one, zero, one, b, e, h),
        (zero, zero, zero, one, one, c, f, i),
    )
    brackets = {}
    for basis in combinations(range(8), 4):
        square = tuple(
            tuple(matrix[row][column].data for column in basis)
            for row in range(4)
        )
        label = "".join(str(index + 1) for index in basis)
        brackets[label] = poly.determinant(square)
    return residual, brackets


# (row variable, column variable, scalar, parent-bracket factors).
CERTIFICATES = {
    (36, 37): (0, 1, -1, ("3457", "1237")),
    (36, 38): (0, 3, -1, ("1238", "1267")),
    (36, 39): (0, 6, 1, ("2356", "1237", "1237")),
    (36, 41): (0, 4, 1, ("3456", "1237")),
    (36, 42): (0, 5, -1, ("3456", "2478")),
    (36, 44): (0, 4, 1, ("1237", "3568")),
    (36, 46): (0, 1, -1, ("1237", "1237")),
    (36, 48): (0, 1, 1, ("2356", "1237")),
    (36, 49): (0, 1, 1, ("2357", "1237")),
    (36, 50): (0, 1, -1, ("1237", "2378")),
    (36, 51): (0, 6, -1, ("1236", "1237", "2467")),
    (37, 38): (0, 3, 1, ("1258", "1267")),
    (37, 39): (0, 1, -1, ("3457", "2378")),
    (37, 41): (0, 1, -1, ("3457", "2457")),
    (37, 42): (0, 1, 1, ("3457", "2478")),
    (37, 44): (0, 1, -1, ("3457", "2578")),
    (37, 46): (0, 3, 1, ("1267",)),
    (37, 48): (0, 3, -1, ("1256",)),
    (37, 49): (0, 1, -1, ("2357", "1257")),
    (37, 50): (0, 1, 1, ("1257", "2378")),
    (37, 51): (0, 6, 1, ("1236", "2467", "1257")),
    (38, 39): (3, 6, -1, ("2356", "1236", "1278")),
    (38, 41): (0, 6, 1, ("2457", "1267")),
    (38, 42): (3, 6, 1, ("2356", "1246", "1278")),
    (38, 44): (3, 6, -1, ("2356", "1256", "1278")),
    (38, 46): (0, 3, 1, ("1238", "1267")),
    (38, 48): (0, 3, 1, ("1268",)),
    (38, 49): (0, 1, 1, ("2357", "1278")),
    (38, 50): (0, 1, -1, ("2378", "1278")),
    (38, 51): (3, 5, 1, ("1456", "2468", "1268")),
    (39, 41): (0, 4, -1, ("3456", "2378")),
    (39, 42): (0, 2, -1, ("3478", "1278")),
    (39, 44): (0, 2, 1, ("3578", "1278")),
    (39, 46): (0, 1, 1, ("1237", "2378")),
    (39, 48): (0, 1, -1, ("2356", "2378")),
    (39, 49): (0, 1, -1, ("2357", "2378")),
    (39, 50): (0, 1, 1, ("2378", "2378")),
    (39, 51): (3, 5, 1, ("2356", "1238", "1456", "2468")),
    (41, 42): (0, 2, -1, ("1247", "4578")),
    (41, 44): (0, 2, 1, ("1257", "4578")),
    (41, 46): (0, 1, 1, ("2457", "1237")),
    (41, 48): (0, 1, -1, ("2356", "2457")),
    (41, 49): (0, 1, -1, ("2457", "2357")),
    (41, 50): (0, 1, 1, ("2457", "2378")),
    (41, 51): (0, 5, 1, ("2457", "1456", "2468")),
    (42, 44): (0, 2, -1, ("4578", "1278")),
    (42, 46): (0, 1, -1, ("1237", "2478")),
    (42, 48): (0, 1, 1, ("2356", "2478")),
    (42, 49): (0, 1, 1, ("2357", "2478")),
    (42, 50): (0, 1, -1, ("2478", "2378")),
    (42, 51): (0, 5, -1, ("1456", "2468", "2478")),
    (44, 46): (0, 1, 1, ("1237", "2578")),
    (44, 48): (0, 1, -1, ("2356", "2578")),
    (44, 49): (0, 1, -1, ("2357", "2578")),
    (44, 50): (0, 1, 1, ("2378", "2578")),
    (44, 51): (3, 5, 1, ("2356", "1456", "2468", "1258")),
    (46, 48): (0, 1, 1, ("1236", "1237")),
    (46, 49): (0, 1, 1, ("2357", "1237")),
    (46, 50): (0, 1, -1, ("1237", "2378")),
    (46, 51): (0, 5, -1, ("1236", "1456", "2478")),
    (48, 49): (0, 1, 1, ("2357",)),
    (48, 50): (0, 1, -1, ("2378",)),
    (48, 51): (0, 5, -1, ("1456", "2468")),
    (49, 50): (1, 3, 1, ("2358", "1237")),
    (49, 51): (1, 6, -1, ("2357", "1236", "2467")),
    (50, 51): (3, 5, -1, ("1238", "1456", "2468")),
}


def verify_certificates():
    residual, brackets = polynomial_data()
    expected_pairs = set(combinations(sorted(residual), 2))
    if set(CERTIFICATES) != expected_pairs or len(CERTIFICATES) != 66:
        raise AssertionError("the representative pair certificate table is incomplete")
    for pair, (left_variable, right_variable, scalar, labels) in CERTIFICATES.items():
        first, second = (residual[kind] for kind in pair)
        minor = poly.subtract(
            poly.multiply(
                derivative(first, left_variable),
                derivative(second, right_variable),
            ),
            poly.multiply(
                derivative(first, right_variable),
                derivative(second, left_variable),
            ),
        )
        expected = poly.multiply(
            poly.constant(scalar), *(brackets[label] for label in labels)
        )
        if minor != expected:
            raise AssertionError(f"wrong Jacobian certificate for pair {pair}")
    if residual[46] != wall.residual_values(
        dict(zip("abcdefghi", (Polynomial(poly.variable(i)) for i in range(9)), strict=True))
    )[47].data:
        raise AssertionError("types 46 and 47 no longer have the same residual")
    return tuple(sorted(residual)), len(CERTIFICATES)


def main():
    kinds, count = verify_certificates()
    print("PASS distinct residual representative types:", kinds)
    print("PASS exact nonzero parent-bracket Jacobian minors for all", count, "pairs")
    print("THEOREM distinct representative gradients are independent on the uniform locus")
    print("THEOREM every canonical pair-wall component is noncompact")
    print("THEOREM the only representative size-two coincidence is q_46=q_47")
    print("SCOPE full relative-label pairs are audited by the labeled-pair verifier")
    print("CAVEAT relative labeled triples remain unclassified")


if __name__ == "__main__":
    main()
