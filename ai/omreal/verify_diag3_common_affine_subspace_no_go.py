#!/usr/bin/env python3
"""Exact no-go for common three-dimensional affine fibers in hard triples.

For three explicit relative-label residual-factor triples, expand every
coefficient matrix of every polynomial Hessian.  If all three equations were
affine on every coset of a three-plane V, then Sym^2(V) would lie in the
annihilator of those coefficient matrices.  Exact rational row reduction
bounds V by dimension two in all three cases.

This is a regression against an overly broad affine-fiber proof strategy.
It is not a compact component and does not disprove the third diagonal.
"""

from collections import defaultdict
from fractions import Fraction
import hashlib
from itertools import combinations_with_replacement
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled

TRIPLES = (
    (12985, 16183, 7196),
    (20355, 5442, 5949),
    (9667, 16486, 26315),
)
N = 9
LETTERS = "abcdefghi"
SYMMETRIC_COORDINATES = tuple(combinations_with_replacement(range(N), 2))


def coefficient_hessians(polynomial):
    """Return coefficient matrices H_alpha of the polynomial Hessian."""
    forms = defaultdict(lambda: [[0] * N for _ in range(N)])
    for monomial, coefficient in polynomial.items():
        for i in range(N):
            if not monomial[i]:
                continue
            for j in range(i, N):
                if not monomial[j]:
                    continue
                if i == j and monomial[i] < 2:
                    continue
                exponent = list(monomial)
                exponent[i] -= 1
                exponent[j] -= 1
                multiplier = monomial[i] * (monomial[j] - (1 if i == j else 0))
                value = coefficient * multiplier
                exponent = tuple(exponent)
                forms[exponent][i][j] += value
                if i != j:
                    forms[exponent][j][i] += value
    return tuple((exponent, tuple(tuple(row) for row in matrix)) for exponent, matrix in sorted(forms.items()))


def rref(rows, ncols=N):
    rows = [[Fraction(value) for value in row] for row in rows if any(row)]
    pivot_columns = []
    pivot_row = 0
    for column in range(ncols):
        selected = next((r for r in range(pivot_row, len(rows)) if rows[r][column]), None)
        if selected is None:
            continue
        rows[pivot_row], rows[selected] = rows[selected], rows[pivot_row]
        value = rows[pivot_row][column]
        rows[pivot_row] = [entry / value for entry in rows[pivot_row]]
        for r in range(len(rows)):
            if r == pivot_row or not rows[r][column]:
                continue
            value = rows[r][column]
            rows[r] = [left - value * right for left, right in zip(rows[r], rows[pivot_row])]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return tuple(tuple(row) for row in rows), tuple(pivot_columns)


def nullspace(rows, ncols=N):
    reduced, pivots = rref(rows, ncols)
    free = tuple(i for i in range(ncols) if i not in pivots)
    basis = []
    for column in free:
        vector = [Fraction(0)] * ncols
        vector[column] = 1
        for row_index, pivot in enumerate(pivots):
            vector[pivot] = -reduced[row_index][column]
        basis.append(tuple(vector))
    return tuple(basis), pivots


def matrix_vector(matrix, vector):
    return tuple(sum(a * b for a, b in zip(row, vector)) for row in matrix)


def bilinear(left, matrix, right):
    return sum(a * b for a, b in zip(left, matrix_vector(matrix, right)))


def quadratic_coefficient_row(matrix):
    """Coefficients pairing with x_i^2 and x_i*x_j (i<j)."""
    return tuple(
        matrix[i][j] * (1 if i == j else 2)
        for i, j in SYMMETRIC_COORDINATES
    )


def named_support(vector):
    return tuple(
        (LETTERS[i] + LETTERS[j], value)
        for (i, j), value in zip(SYMMETRIC_COORDINATES, vector)
        if value
    )


def maximum_allowed_clique(annihilator):
    """For a coordinate-monomial K, bound V from Sym^2(V) subset K."""
    supports = tuple(named_support(vector) for vector in annihilator)
    if any(len(support) != 1 or support[0][1] != 1 for support in supports):
        return None
    allowed = frozenset(support[0][0] for support in supports)
    best = ()
    for mask in range(1 << N):
        subset = tuple(index for index in range(N) if mask >> index & 1)
        if all(
            LETTERS[i] + LETTERS[j] in allowed
            for position, i in enumerate(subset)
            for j in subset[position:]
        ) and len(subset) > len(best):
            best = subset
    return tuple(LETTERS[index] for index in best), tuple(sorted(allowed))


def main():
    _occurrences, _occurrence_factor, factor_polynomial = labeled.factor_polynomials()
    reports = []
    for triple in TRIPLES:
        per_factor = tuple(coefficient_hessians(factor_polynomial[factor]) for factor in triple)
        all_forms = tuple(matrix for forms in per_factor for _exponent, matrix in forms)
        stacked = tuple(row for matrix in all_forms for row in matrix)
        radical, pivots = nullspace(stacked)
        if any(matrix_vector(matrix, vector) != (0,) * N for matrix in all_forms for vector in radical):
            raise AssertionError("radical computation failed")
        form_rows = tuple(quadratic_coefficient_row(matrix) for matrix in all_forms)
        _form_rref, form_pivots = rref(form_rows, len(SYMMETRIC_COORDINATES))
        annihilator, _ = nullspace(form_rows, len(SYMMETRIC_COORDINATES))
        if len(form_pivots) + len(annihilator) != len(SYMMETRIC_COORDINATES):
            raise AssertionError("form span / annihilator dimensions disagree")
        clique = maximum_allowed_clique(annihilator)
        if len(annihilator) < 6:
            dimension_bound = 2
            obstruction = (
                "symmetric-square-dimension",
                len(annihilator),
                "<",
                6,
            )
        elif clique is not None:
            dimension_bound = len(clique[0])
            obstruction = ("coordinate-annihilator-clique", clique)
        else:
            dimension_bound = None
            obstruction = ("unresolved",)
        reports.append(
            (
                triple,
                tuple(map(len, per_factor)),
                len(all_forms),
                len(pivots),
                radical,
                len(form_pivots),
                tuple(named_support(vector) for vector in annihilator),
                dimension_bound,
                obstruction,
            )
        )
        print("TRIPLE", triple)
        print(" HESSIAN_COEFFICIENT_FORMS", tuple(map(len, per_factor)), "total", len(all_forms))
        print(" COMMON_RADICAL_RANK", N-len(pivots), "basis", radical)
        print(
            " FORM_SPAN_RANK", len(form_pivots),
            "SYMMETRIC_ANNIHILATOR_DIMENSION", len(annihilator),
        )
        print(" ANNIHILATOR_BASIS", tuple(named_support(vector) for vector in annihilator))
        print(" AFFINE_DIRECTION_DIMENSION_BOUND", dimension_bound, obstruction)

    expected_ranks = (35, 40, 41)
    if tuple(report[5] for report in reports) != expected_ranks:
        raise AssertionError("coefficient-Hessian span ranks changed")
    if tuple(report[7] for report in reports) != (2, 2, 2):
        raise AssertionError("a three-dimensional affine direction survived")
    expected_first_annihilator = (
        (("aa", Fraction(1)),),
        (("ac", Fraction(1)),),
        (("ad", Fraction(1)),),
        (("bb", Fraction(1)),),
        (("cc", Fraction(1)),),
        (("dd", Fraction(1)),),
        (("ee", Fraction(1)),),
        (("gg", Fraction(1)),),
        (("hh", Fraction(1)),),
        (("ii", Fraction(1)),),
    )
    if reports[0][6] != expected_first_annihilator:
        raise AssertionError("first-triple monomial annihilator changed")
    semantic = ("common-affine-subspace-no-go-v1", tuple(reports))
    digest = hashlib.sha256(repr(semantic).encode("ascii")).hexdigest()
    expected = "09651bcd297be400bfc1f49859bb2091dbacda8ebc8d5e30ed241711ea07b623"
    if digest != expected:
        raise AssertionError(f"semantic digest changed: {digest}")
    print("SEMANTIC_SHA256", digest)
    print("NO-GO no hard triple has a common three-dimensional affine direction")


if __name__ == "__main__":
    main()
