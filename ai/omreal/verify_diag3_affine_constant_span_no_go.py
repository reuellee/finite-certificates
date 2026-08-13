#!/usr/bin/env python3
"""Exact affine-linear constant-span symmetry no-go for three hard triples.

For V(x)=Ax+b and a constant 3 by 3 matrix M, solve coefficientwise

    V(q_i) = sum_j M_ij q_j.

The three exact systems all have zero kernel.  Thus no nonzero affine-linear
vector field carries the three displayed generators into their constant
linear span.  This is strictly weaker than preservation of their polynomial
ideal, which would allow polynomial coefficient multipliers.  The result
delimits one proof strategy; it neither exhibits a compact component nor
disproves 9DVL.
"""

from collections import defaultdict
from fractions import Fraction
import hashlib
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as gradient
import verify_residual_log_binomials as poly


TRIPLES = (
    (12985, 16183, 7196),
    (20355, 5442, 5949),
    (9667, 16486, 26315),
)
N = 9
K = 3
LETTERS = "abcdefghi"
ZERO_MONOMIAL = (0,) * N

A_COLUMNS = tuple(("A", row, column) for row in range(N) for column in range(N))
B_COLUMNS = tuple(("b", row) for row in range(N))
M_COLUMNS = tuple(("M", row, column) for row in range(K) for column in range(K))
COLUMNS = A_COLUMNS + B_COLUMNS + M_COLUMNS
COLUMN_INDEX = {label: index for index, label in enumerate(COLUMNS)}


def variable_times(polynomial, variable):
    answer = {}
    for monomial, coefficient in polynomial.items():
        exponent = list(monomial)
        exponent[variable] += 1
        answer[tuple(exponent)] = coefficient
    return answer


def system_rows(polynomials):
    """Rows for V(q_i)-sum_j M_ij*q_j=0, grouped by monomial."""
    equations = defaultdict(lambda: [0] * len(COLUMNS))
    derivatives = tuple(
        tuple(gradient.derivative(polynomial, row) for row in range(N))
        for polynomial in polynomials
    )
    for equation in range(K):
        for row in range(N):
            derivative = derivatives[equation][row]
            for column in range(N):
                index = COLUMN_INDEX[("A", row, column)]
                for monomial, coefficient in variable_times(derivative, column).items():
                    equations[(equation, monomial)][index] += coefficient
            index = COLUMN_INDEX[("b", row)]
            for monomial, coefficient in derivative.items():
                equations[(equation, monomial)][index] += coefficient
        for target in range(K):
            index = COLUMN_INDEX[("M", equation, target)]
            for monomial, coefficient in polynomials[target].items():
                equations[(equation, monomial)][index] -= coefficient
    rows = tuple(
        tuple(row)
        for _key, row in sorted(equations.items())
        if any(row)
    )
    return rows


def rref(rows, ncols):
    rows = [[Fraction(value) for value in row] for row in rows if any(row)]
    pivots = []
    pivot_row = 0
    for column in range(ncols):
        selected = next(
            (row for row in range(pivot_row, len(rows)) if rows[row][column]),
            None,
        )
        if selected is None:
            continue
        rows[pivot_row], rows[selected] = rows[selected], rows[pivot_row]
        value = rows[pivot_row][column]
        rows[pivot_row] = [entry / value for entry in rows[pivot_row]]
        # Fraction-free sparsity is unavailable, but only 99 columns occur here.
        for row in range(len(rows)):
            if row == pivot_row or not rows[row][column]:
                continue
            value = rows[row][column]
            rows[row] = [
                left - value * right
                for left, right in zip(rows[row], rows[pivot_row])
            ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return tuple(tuple(row) for row in rows), tuple(pivots)


def nullspace(rows, ncols):
    reduced, pivots = rref(rows, ncols)
    free = tuple(column for column in range(ncols) if column not in pivots)
    basis = []
    for free_column in free:
        vector = [Fraction(0)] * ncols
        vector[free_column] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = -reduced[row][free_column]
        basis.append(tuple(vector))
    return tuple(basis), pivots


def matmul(left, right):
    return tuple(
        tuple(
            sum(left[i][middle] * right[middle][j] for middle in range(N))
            for j in range(N)
        )
        for i in range(N)
    )


def identity():
    return tuple(
        tuple(Fraction(int(i == j)) for j in range(N)) for i in range(N)
    )


def zero_matrix(matrix):
    return all(not value for row in matrix for value in row)


def matrix_rank(matrix):
    _reduced, pivots = rref(matrix, len(matrix[0]))
    return len(pivots)


def nilpotency_index(matrix):
    power = identity()
    for exponent in range(1, N + 1):
        power = matmul(power, matrix)
        if zero_matrix(power):
            return exponent
    return None


def unpack(vector):
    A = tuple(
        tuple(vector[COLUMN_INDEX[("A", row, column)]] for column in range(N))
        for row in range(N)
    )
    b = tuple(vector[COLUMN_INDEX[("b", row)]] for row in range(N))
    M = tuple(
        tuple(vector[COLUMN_INDEX[("M", row, column)]] for column in range(K))
        for row in range(K)
    )
    return A, b, M


def sparse_matrix(matrix, row_names, column_names):
    return tuple(
        (row_names[row], column_names[column], value)
        for row in range(len(matrix))
        for column in range(len(matrix[row]))
        if (value := matrix[row][column])
    )


def sparse_vector(vector, names):
    return tuple((names[index], value) for index, value in enumerate(vector) if value)


def verify_kernel(rows, basis):
    for basis_index, vector in enumerate(basis):
        for row_index, row in enumerate(rows):
            if sum(left * right for left, right in zip(row, vector)):
                raise AssertionError(
                    f"kernel verification failed at basis {basis_index}, row {row_index}"
                )


def projected_vector_field_rank(basis):
    rows = tuple(tuple(vector[column] for column in range(90)) for vector in basis)
    return matrix_rank(rows) if rows else 0


def pure_translation_kernel(rows):
    """Solve with A=0; unknowns are b and M."""
    columns = tuple(range(81, 99))
    reduced_rows = tuple(tuple(row[column] for column in columns) for row in rows)
    basis, _pivots = nullspace(reduced_rows, len(columns))
    translations = []
    for vector in basis:
        b = vector[:9]
        M = tuple(tuple(vector[9 + 3 * i + j] for j in range(3)) for i in range(3))
        translations.append((b, M))
    return tuple(translations)


def main():
    _occurrences, _occurrence_factor, factor_polynomial = labeled.factor_polynomials()
    reports = []
    for triple in TRIPLES:
        polynomials = tuple(factor_polynomial[factor] for factor in triple)
        rows = system_rows(polynomials)
        basis, pivots = nullspace(rows, len(COLUMNS))
        verify_kernel(rows, basis)
        projection_rank = projected_vector_field_rank(basis)
        if projection_rank != len(basis):
            raise AssertionError("pure M-symmetry unexpectedly present")
        translations = pure_translation_kernel(rows)
        basis_reports = []
        for index, vector in enumerate(basis):
            A, b, M = unpack(vector)
            basis_reports.append(
                (
                    index,
                    matrix_rank(A),
                    sum(A[i][i] for i in range(N)),
                    nilpotency_index(A),
                    sparse_matrix(A, LETTERS, LETTERS),
                    sparse_vector(b, LETTERS),
                    sparse_matrix(M, "123", "123"),
                )
            )
        translation_reports = tuple(
            (
                sparse_vector(b, LETTERS),
                sparse_matrix(M, "123", "123"),
            )
            for b, M in translations
        )
        report = (
            triple,
            len(rows),
            len(pivots),
            len(basis),
            projection_rank,
            tuple(basis_reports),
            translation_reports,
        )
        reports.append(report)
        print("TRIPLE", triple)
        print(
            " SYSTEM", len(rows), "x", len(COLUMNS),
            "rank", len(pivots), "nullity", len(basis),
            "vector_field_projection_rank", projection_rank,
        )
        print(" PURE_TRANSLATION_NULLITY", len(translations), translation_reports)
        for basis_report in basis_reports:
            print(" BASIS", basis_report)
    semantic = ("affine-constant-span-symmetries-v1", tuple(reports))
    digest = hashlib.sha256(repr(semantic).encode("ascii")).hexdigest()
    expected = "3c3f61c66255e820dee121984ca91e823c01674e7ac52862088fd65aea8c75f3"
    if digest != expected:
        raise AssertionError(f"semantic digest changed: {digest}")
    print("SEMANTIC_SHA256", digest)
    print("SEMANTIC_REPR", repr(semantic))
    print("NO-GO no hard triple has an affine-linear constant-span symmetry")


if __name__ == "__main__":
    main()
