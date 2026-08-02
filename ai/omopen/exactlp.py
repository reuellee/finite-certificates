"""Exact certificates for the strict homogeneous system ``A x > 0``.

Gordan's theorem of the alternative says that exactly one of the following
systems has a solution::

    A x > 0
    lambda >= 0, lambda != 0, A.T lambda = 0

``exact_feasible`` decides between them using rational arithmetic only and
returns an integer certificate for the system that holds.  Every certificate
is checked again with exact integer dot products before it is returned.

This module exists because the max-margin floating-point LP used elsewhere is
a complete *mathematical reformulation*, but a float64 solver is not a
complete decision procedure near zero (and large integer coefficients make
that distinction important).  No float is used in this module's decision
path.

The implementation observes that a Gordan certificate can be normalized so
that its entries sum to one.  Thus it asks whether zero is in the convex hull
of the rows of ``A``.  A small exact Phase-I simplex, with Bland's anti-cycling
rule, solves that standard-form feasibility problem.  If Phase I has positive
optimum, its exact dual vector strictly separates the rows from zero and gives
the desired ``x``.

Callers should pass the integer rows they already built directly, for example
``status, certificate = exact_feasible(A)``.  There is deliberately no import
from ``weaponA`` or any other project module.
"""

from __future__ import annotations

from fractions import Fraction
from math import gcd, lcm
import operator
import random
import sys
import traceback
from typing import Iterable, Sequence


__all__ = ["exact_feasible"]

_DIMENSION = 4
_AUGMENTED_DIMENSION = _DIMENSION + 1


def _coerce_rows(A: Iterable[Sequence[int]]) -> list[tuple[int, ...]]:
    """Copy and validate a four-column matrix without lossy coercions."""

    rows: list[tuple[int, ...]] = []
    try:
        iterator = iter(A)
    except TypeError as exc:
        raise TypeError("A must be an iterable of integer row vectors") from exc

    for row_number, row in enumerate(iterator):
        try:
            values = tuple(operator.index(value) for value in row)
        except TypeError as exc:
            raise TypeError(
                f"row {row_number} must contain exact integers"
            ) from exc
        if len(values) != _DIMENSION:
            raise ValueError(
                f"row {row_number} has length {len(values)}; expected 4"
            )
        rows.append(values)
    return rows


def _inverse(matrix: Sequence[Sequence[int | Fraction]]) -> list[list[Fraction]]:
    """Return the exact inverse of a small square matrix."""

    size = len(matrix)
    augmented = [
        [Fraction(value) for value in matrix[row]]
        + [Fraction(int(row == column)) for column in range(size)]
        for row in range(size)
    ]

    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if augmented[row][column]),
            None,
        )
        if pivot is None:
            raise AssertionError("simplex basis unexpectedly became singular")
        if pivot != column:
            augmented[column], augmented[pivot] = (
                augmented[pivot],
                augmented[column],
            )

        pivot_value = augmented[column][column]
        augmented[column] = [value / pivot_value for value in augmented[column]]

        for row in range(size):
            if row == column:
                continue
            multiplier = augmented[row][column]
            if multiplier:
                augmented[row] = [
                    old - multiplier * pivot_entry
                    for old, pivot_entry in zip(
                        augmented[row], augmented[column], strict=True
                    )
                ]

    return [row[size:] for row in augmented]


def _matrix_vector(
    matrix: Sequence[Sequence[Fraction]], vector: Sequence[int | Fraction]
) -> list[Fraction]:
    return [
        sum((entry * value for entry, value in zip(row, vector, strict=True)),
            Fraction(0))
        for row in matrix
    ]


def _phase_one(
    rows: Sequence[Sequence[int]],
) -> tuple[Fraction, list[Fraction], list[Fraction]]:
    """Solve convex-hull membership and return optimum, primal, and dual.

    The standard-form equations are

        [A.T; 1 ... 1] lambda + artificial = (0, 0, 0, 0, 1),
        lambda, artificial >= 0,

    and the objective minimizes the sum of the five artificial variables.
    """

    row_count = len(rows)
    size = _AUGMENTED_DIMENSION
    right_hand_side = [0, 0, 0, 0, 1]

    columns: list[tuple[int, ...]] = [
        tuple(row) + (1,) for row in rows
    ]
    columns.extend(
        tuple(int(row == column) for row in range(size))
        for column in range(size)
    )
    costs = [0] * row_count + [1] * size

    # The artificial identity is an initial feasible basis.  Zero right-hand
    # sides make it degenerate, so Bland's rule is used for both choices.
    basis = list(range(row_count, row_count + size))

    while True:
        basis_matrix = [
            [columns[basis[column]][row] for column in range(size)]
            for row in range(size)
        ]
        inverse = _inverse(basis_matrix)
        basic_values = _matrix_vector(inverse, right_hand_side)
        assert all(value >= 0 for value in basic_values)

        basic_costs = [costs[index] for index in basis]
        dual = [
            sum(
                (Fraction(basic_costs[row]) * inverse[row][column]
                 for row in range(size)),
                Fraction(0),
            )
            for column in range(size)
        ]

        basis_set = set(basis)
        entering = None
        for index, column in enumerate(columns):
            if index in basis_set:
                continue
            reduced_cost = Fraction(costs[index]) - sum(
                (dual[row] * column[row] for row in range(size)),
                Fraction(0),
            )
            if reduced_cost < 0:
                entering = index
                break  # smallest index: Bland's entering rule

        if entering is None:
            primal = [Fraction(0) for _ in columns]
            for position, index in enumerate(basis):
                primal[index] = basic_values[position]
            optimum = sum(
                (Fraction(cost) * value for cost, value in zip(
                    costs, primal, strict=True
                )),
                Fraction(0),
            )

            # Exact primal/dual consistency and optimality checks.
            assert optimum == sum(
                (dual[row] * right_hand_side[row] for row in range(size)),
                Fraction(0),
            )
            assert optimum >= 0
            for index, column in enumerate(columns):
                reduced_cost = Fraction(costs[index]) - sum(
                    (dual[row] * column[row] for row in range(size)),
                    Fraction(0),
                )
                assert reduced_cost >= 0
            return optimum, primal[:row_count], dual

        direction = _matrix_vector(inverse, columns[entering])
        candidates = [
            (basic_values[position] / value, basis[position], position)
            for position, value in enumerate(direction)
            if value > 0
        ]
        # The Phase-I objective is bounded below by zero.  Therefore a
        # negative-reduced-cost direction must have a leaving variable.
        assert candidates, "bounded Phase-I problem appeared unbounded"
        _, _, leaving_position = min(candidates)
        basis[leaving_position] = entering


def _integerize(values: Sequence[Fraction]) -> tuple[int, ...]:
    """Clear denominators and return the primitive integer vector."""

    denominator = 1
    for value in values:
        denominator = lcm(denominator, value.denominator)
    integers = [value.numerator * (denominator // value.denominator) for value in values]

    common = 0
    for value in integers:
        common = gcd(common, abs(value))
    if common:
        integers = [value // common for value in integers]
    return tuple(integers)


def _verify_feasible(rows: Sequence[Sequence[int]], x: Sequence[int]) -> None:
    if len(x) != _DIMENSION or not all(isinstance(value, int) for value in x):
        raise AssertionError("FEASIBLE certificate is not an integer 4-vector")
    for row in rows:
        dot_product = sum(
            (coefficient * value for coefficient, value in zip(row, x, strict=True)),
            0,
        )
        if dot_product <= 0:
            raise AssertionError("invalid FEASIBLE certificate")


def _verify_infeasible(
    rows: Sequence[Sequence[int]], lam: Sequence[int]
) -> None:
    if len(lam) != len(rows):
        raise AssertionError("INFEASIBLE certificate has the wrong length")
    if not all(isinstance(value, int) and value >= 0 for value in lam):
        raise AssertionError("INFEASIBLE certificate is not nonnegative integral")
    if not any(value != 0 for value in lam):
        raise AssertionError("INFEASIBLE certificate is zero")
    for column in range(_DIMENSION):
        coordinate = sum(
            (lam[row] * rows[row][column] for row in range(len(rows))), 0
        )
        if coordinate != 0:
            raise AssertionError("invalid INFEASIBLE certificate")


def exact_feasible(
    A: Iterable[Sequence[int]],
) -> tuple[str, tuple[int, ...]]:
    """Decide ``A x > 0`` exactly and return a checked integer certificate.

    Parameters
    ----------
    A:
        An iterable of integer row vectors, each of length four.  Integer-like
        scalar types implementing ``__index__`` (including NumPy integers) are
        accepted; floats are rejected even when they have integral values.

    Returns
    -------
    (``'FEASIBLE'``, x)
        ``x`` is a primitive integer 4-vector and every integer dot product
        ``A[i] . x`` is strictly positive.
    (``'INFEASIBLE'``, lam)
        ``lam`` is a primitive, nonzero, nonnegative integer vector with one
        entry per row and ``A.T lam == 0`` exactly.
    """

    rows = _coerce_rows(A)
    optimum, convex_weights, phase_one_dual = _phase_one(rows)

    if optimum == 0:
        # Sum(lambda) == 1 in the Phase-I equations, so integerization cannot
        # produce the zero vector.
        lam = _integerize(convex_weights)
        _verify_infeasible(rows, lam)
        return "INFEASIBLE", lam

    # At the positive Phase-I optimum, dual optimality gives
    #     row . y[:4] + y[4] <= 0  and  y[4] = optimum > 0.
    # Therefore x = -y[:4] has row . x >= y[4] > 0 for every row.
    assert optimum > 0
    assert phase_one_dual[4] == optimum
    rational_x = tuple(-value for value in phase_one_dual[:_DIMENSION])
    x = _integerize(rational_x)
    _verify_feasible(rows, x)
    return "FEASIBLE", x


def _random_feasible_instance(
    rng: random.Random, row_count: int, coefficient_bound: int = 100
) -> tuple[list[tuple[int, ...]], tuple[int, ...]]:
    while True:
        target = tuple(rng.randint(-7, 7) for _ in range(_DIMENSION))
        if any(target):
            break

    rows: list[tuple[int, ...]] = []
    while len(rows) < row_count:
        row = tuple(
            rng.randint(-coefficient_bound, coefficient_bound)
            for _ in range(_DIMENSION)
        )
        if sum((a * b for a, b in zip(row, target, strict=True)), 0) > 0:
            rows.append(row)
    return rows, target


def _check_result(rows: Sequence[Sequence[int]], result: tuple[str, tuple[int, ...]]) -> None:
    status, certificate = result
    if status == "FEASIBLE":
        _verify_feasible(rows, certificate)
    elif status == "INFEASIBLE":
        _verify_infeasible(rows, certificate)
    else:
        raise AssertionError(f"unknown status {status!r}")


def _self_test() -> int:
    print("exactlp self-test (exact rational/integer decision path)")
    try:
        rng = random.Random(0xE1AC7)

        for _ in range(20):
            rows, known_x = _random_feasible_instance(rng, rng.randint(1, 56))
            result = exact_feasible(rows)
            _check_result(rows, result)
            assert result[0] == "FEASIBLE"
            _verify_feasible(rows, known_x)
        print("  (a) random known-feasible instances: PASS (20 cases)")

        for _ in range(20):
            r = tuple(rng.randint(-10**6, 10**6) for _ in range(_DIMENSION))
            if not any(r):
                r = (1, 0, 0, 0)
            rows = [r, tuple(-value for value in r)]
            rows.extend(
                tuple(rng.randint(-1000, 1000) for _ in range(_DIMENSION))
                for _ in range(rng.randint(0, 20))
            )
            result = exact_feasible(rows)
            _check_result(rows, result)
            assert result[0] == "INFEASIBLE"
        print("  (b) rows containing r and -r: PASS (20 cases)")

        huge = 2**60
        pathological = [
            (0, 1, 0, 0),
            (1, -huge, 0, 0),
            (-1, huge + 1, 0, 0),
        ]
        result = exact_feasible(pathological)
        _check_result(pathological, result)
        assert result[0] == "FEASIBLE"
        explicit_x = (2 * huge + 1, 2, 0, 0)
        _verify_feasible(pathological, explicit_x)
        print("  (c) 2**60 cancellation case: PASS")
        print(
            "      exact witness exists (x2=2, x1=2H+1); "
            "float64 would wrongly report margin 0 here"
        )

        feasible_count = 0
        infeasible_count = 0
        for case in range(100):
            if case % 2 == 0:
                rows, known_x = _random_feasible_instance(
                    rng, rng.randint(1, 56), coefficient_bound=10**5
                )
                result = exact_feasible(rows)
                _check_result(rows, result)
                # If an INFEASIBLE certificate were returned, dotting its
                # zero row-combination with known_x would be both zero and a
                # positive sum.  This is the explicit "not both" cross-check.
                assert result[0] == "FEASIBLE"
                _verify_feasible(rows, known_x)
                feasible_count += 1
            else:
                r = tuple(rng.randint(-10**9, 10**9) for _ in range(_DIMENSION))
                if not any(r):
                    r = (0, 0, 0, 1)
                rows = [r, tuple(-value for value in r)]
                rows.extend(
                    tuple(rng.randint(-10**5, 10**5) for _ in range(_DIMENSION))
                    for _ in range(rng.randint(0, 54))
                )
                result = exact_feasible(rows)
                _check_result(rows, result)
                # The known lambda=(1,1,0,...) rules out every strict x.
                assert result[0] == "INFEASIBLE"
                _verify_infeasible(rows, (1, 1) + (0,) * (len(rows) - 2))
                infeasible_count += 1

        # Unconditioned random matrices exercise either branch; exact
        # certificate checks are independent of the simplex termination test.
        for _ in range(20):
            rows = [
                tuple(rng.randint(-10**4, 10**4) for _ in range(_DIMENSION))
                for _ in range(rng.randint(1, 24))
            ]
            result = exact_feasible(rows)
            _check_result(rows, result)
            if result[0] == "FEASIBLE":
                feasible_count += 1
            else:
                infeasible_count += 1

        print(
            "  (d) random stress and mutually-exclusive witness checks: "
            f"PASS (120 cases: {feasible_count} feasible, "
            f"{infeasible_count} infeasible)"
        )
        print("exactlp self-test: PASS")
        return 0
    except Exception:
        print("exactlp self-test: FAIL")
        traceback.print_exc(file=sys.stdout)
        return 1


if __name__ == "__main__":
    raise SystemExit(_self_test())
