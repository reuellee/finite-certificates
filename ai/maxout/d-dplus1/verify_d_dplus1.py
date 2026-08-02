#!/usr/bin/env python3
"""Exact verifier for the (d,d+1)-zonoboxtope construction.

The script checks, using Fraction arithmetic only:
  * the direction configuration and its positive circuit;
  * the rational realization of the prescribed p_i and q_i values;
  * every chamber's ray signs;
  * that exactly two chambers are monocolored; and
  * the resulting vertex count 2^(d+2)-6.

It verifies any requested finite set of dimensions.  The accompanying proof
establishes the formula symbolically for every d >= 2.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
from itertools import combinations


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    """Return an exact determinant by fraction-preserving elimination."""
    a = [row[:] for row in matrix]
    n = len(a)
    det = Fraction(1)
    for col in range(n):
        pivot = next((r for r in range(col, n) if a[r][col]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != col:
            a[col], a[pivot] = a[pivot], a[col]
            det = -det
        pivot_value = a[col][col]
        det *= pivot_value
        for j in range(col, n):
            a[col][j] /= pivot_value
        for r in range(col + 1, n):
            factor = a[r][col]
            if factor:
                for j in range(col, n):
                    a[r][j] -= factor * a[col][j]
    return det


def add_scaled(target: list[Fraction], scalar: Fraction,
               vector: list[Fraction]) -> None:
    for k, value in enumerate(vector):
        target[k] += scalar * value


def format_subset(mask: int, n: int) -> str:
    members = [str(i) for i in range(n) if mask & (1 << i)]
    return "{" + ",".join(members) + "}"


def verify_dimension(d: int) -> dict[str, object]:
    if d < 2:
        raise ValueError("d must be at least 2")
    n = d + 1

    # u_0,...,u_{n-2} are the standard basis; u_{n-1} is -1.
    directions: list[list[Fraction]] = []
    for i in range(d):
        row = [Fraction(0) for _ in range(d)]
        row[i] = Fraction(1)
        directions.append(row)
    directions.append([Fraction(-1) for _ in range(d)])

    # The circuit is (1,...,1), and every d-row minor is nonzero.
    circuit_sum = [Fraction(0) for _ in range(d)]
    for row in directions:
        add_scaled(circuit_sum, Fraction(1), row)
    assert circuit_sum == [Fraction(0) for _ in range(d)]
    minors = [
        determinant([directions[i] for i in rows])
        for rows in combinations(range(n), d)
    ]
    assert all(value != 0 for value in minors)

    p = [Fraction(2 * i) for i in range(n)]
    q = [Fraction(2 * i + 3) for i in range(n - 1)] + [Fraction(1)]
    t = [(p[i] + q[i]) / 2 for i in range(n)]
    delta = [(p[i] - q[i]) / 2 for i in range(n)]
    b = [Fraction(2 * n) for _ in range(n)]
    a = [b[i] + delta[i] for i in range(n)]
    assert all(value > 0 for value in a + b)

    # T = U^T t, and m_0 = T/delta_0 realizes sum(delta_i m_i)=T.
    translation = [Fraction(0) for _ in range(d)]
    for scalar, row in zip(t, directions):
        add_scaled(translation, scalar, row)
    expected_translation = [Fraction(2 * k + 2 - n) for k in range(d)]
    assert translation == expected_translation

    midpoints = [[Fraction(0) for _ in range(d)] for _ in range(n)]
    midpoints[0] = [value / delta[0] for value in translation]
    recovered_translation = [Fraction(0) for _ in range(d)]
    for scalar, midpoint in zip(delta, midpoints):
        add_scaled(recovered_translation, scalar, midpoint)
    assert recovered_translation == translation
    assert [t[i] + delta[i] for i in range(n)] == p
    assert [t[i] - delta[i] for i in range(n)] == q

    monocolored: list[tuple[int, str]] = []
    bicolored = 0
    for mask in range(1, (1 << n) - 1):
        values = [
            p[i] - q[j]
            for i in range(n) if mask & (1 << i)
            for j in range(n) if not mask & (1 << j)
        ]
        assert values and all(value != 0 for value in values)
        if all(value < 0 for value in values):
            monocolored.append((mask, "negative"))
        elif all(value > 0 for value in values):
            monocolored.append((mask, "positive"))
        else:
            assert any(value < 0 for value in values)
            assert any(value > 0 for value in values)
            bicolored += 1

    expected_masks = {
        1,  # P={0}
        ((1 << n) - 1) ^ (1 << (n - 2)),  # P=[n]\{n-2}
    }
    assert {mask for mask, _ in monocolored} == expected_masks
    assert all(sign == "negative" for _, sign in monocolored)

    chambers = (1 << n) - 2
    assert bicolored == chambers - 2
    vertex_count = chambers + bicolored
    claimed = (1 << (d + 2)) - 6
    assert vertex_count == claimed

    return {
        "d": d,
        "n": n,
        "chambers": chambers,
        "monocolored": [format_subset(mask, n) for mask, _ in monocolored],
        "vertices": vertex_count,
        "old_conjecture": (1 << (d + 2)) - 4,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-d", type=int, default=2)
    parser.add_argument("--max-d", type=int, default=10)
    args = parser.parse_args()
    if args.min_d < 2 or args.max_d < args.min_d:
        parser.error("require 2 <= min-d <= max-d")

    print(" d   n   chambers   monocolored chambers              vertices   old")
    print("--  --  --------   --------------------------------  --------   ---")
    for d in range(args.min_d, args.max_d + 1):
        result = verify_dimension(d)
        mono = ", ".join(result["monocolored"])
        print(
            f"{result['d']:2d}  {result['n']:2d}  {result['chambers']:8d}   "
            f"{mono:<32}  {result['vertices']:8d}   {result['old_conjecture']}"
        )
    print("\nAll exact checks passed.")


if __name__ == "__main__":
    main()
