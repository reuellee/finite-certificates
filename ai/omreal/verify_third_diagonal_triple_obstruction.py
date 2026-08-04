#!/usr/bin/env python3
"""Exact three-piece obstruction to termwise third-diagonal pruning.

At the parent-2599 pattern-zero chart, three *distinct geometric* cofinal
five-circuit pieces are simultaneously nonempty.  Their support union is
pencil-rigid, has no common-apex shear, and its incident support-plane normals
have rank three at every label.  Exact additional charts distinguish the
three semialgebraic pieces and prove that each underlying extension signature
is realizable elsewhere.

This blocks any proof that kills every E_1^{2,0} candidate using only the
current omission/fixed-partner/common-apex/support-plane tests.  It does not
prove a compact component or nonzero H_c^0 of the triple intersection.
"""

from itertools import combinations
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import prototype_koszul_circuits as koszul  # noqa: E402


CERTIFICATE = HERE / "data" / "seeat_parent2599_shatter8.npz"
BITS = (0, 4, 3)
EXPECTED_SUPPORTS = {
    0: ("123", "134", "267", "258", "468"),
    4: ("123", "256", "127", "357", "478"),
    3: ("123", "256", "356", "127", "347"),
}


def support(certificate, bit):
    return tuple(
        index
        for index, value in enumerate(certificate["gordan_weight"][0, bit])
        if int(value)
    )


def signed_columns(normals, signature, current):
    return [
        tuple(value if (signature >> index) & 1 else -value for value in normals[index])
        for index in current
    ]


def verify_positive(certificate, normals, bit, current):
    signature = int(certificate["signature"][bit])
    columns = signed_columns(normals, signature, current)
    weights = [int(certificate["gordan_weight"][0, bit, index]) for index in current]
    if not all(weight > 0 for weight in weights):
        raise AssertionError("stored circuit weights are not positive")
    if any(
        sum(weight * column[coordinate] for weight, column in zip(
            weights, columns, strict=True
        ))
        for coordinate in range(4)
    ):
        raise AssertionError("stored positive dependence is not exact")
    if koszul.matrix_rank(columns) != 4:
        raise AssertionError("five-circuit has wrong rank")
    if any(
        koszul.matrix_rank([columns[index] for index in subset]) != 4
        for subset in combinations(range(5), 4)
    ):
        raise AssertionError("stored dependence is not support-minimal")


def piece_contains(normals, signature, current):
    coefficients = []
    for omitted in range(5):
        columns = [
            normals[current[index]]
            for index in range(5)
            if index != omitted
        ]
        determinant = koszul.determinant(
            [[int(column[row]) for column in columns] for row in range(4)]
        )
        coefficient = (-1 if omitted & 1 else 1) * determinant
        if not ((signature >> current[omitted]) & 1):
            coefficient = -coefficient
        coefficients.append(coefficient)
    # The four distinguishing charts below are generic for all three chosen
    # supports.  Keeping this assertion explicit avoids treating an
    # all-zero cofactor vector (rank at most three) as a negative certificate.
    if not all(coefficients):
        raise AssertionError("piece-separation chart lies on a support wall")
    return all(value > 0 for value in coefficients) or all(
        value < 0 for value in coefficients
    )


def verify_feasible(certificate, bit):
    pattern = 1 << bit
    signature = int(certificate["signature"][bit])
    normals = koszul.parent_normals(certificate["pattern_chart"][pattern])
    point = [int(value) for value in certificate["feasible_point"][pattern, bit]]
    for index, normal in enumerate(normals):
        signed = normal if (signature >> index) & 1 else tuple(-x for x in normal)
        if sum(value * coordinate for value, coordinate in zip(
            signed, point, strict=True
        )) <= 0:
            raise AssertionError("one-bit chart does not realize the signature")


def main():
    certificate = np.load(CERTIFICATE, allow_pickle=False)
    if int(certificate["parent_index"].item()) != 2599:
        raise AssertionError("wrong parent certificate")
    normals = koszul.parent_normals(certificate["pattern_chart"][0])
    supports = {bit: support(certificate, bit) for bit in BITS}
    displayed = {
        bit: tuple("".join(map(str, koszul.TRIPLES[index])) for index in current)
        for bit, current in supports.items()
    }
    if displayed != EXPECTED_SUPPORTS:
        raise AssertionError(f"unexpected triple supports {displayed}")

    for bit in BITS:
        verify_positive(certificate, normals, bit, supports[bit])
        verify_feasible(certificate, bit)

    union = set().union(*map(set, supports.values()))
    degrees = tuple(
        sum(label in koszul.TRIPLES[index] for index in union)
        for label in range(1, 9)
    )
    if min(degrees) < 3:
        raise AssertionError("triple union is not minimum-degree rigid")
    for label in range(1, 9):
        incident = [set(koszul.TRIPLES[index]) for index in union if label in koszul.TRIPLES[index]]
        if set.intersection(*(edge - {label} for edge in incident)):
            raise AssertionError("triple union has a fixed partner")
        if koszul.matrix_rank([normals[index] for index in union if label in koszul.TRIPLES[index]]) != 3:
            raise AssertionError("incident support planes have a nontrivial motion")

    # Distinguish the geometric circuit pieces themselves, not merely their
    # (signature,support) indices.  The displayed exact charts witness both
    # directions for every pair.
    truth = {}
    for pattern in (1, 2, 7, 12):
        chart_normals = koszul.parent_normals(certificate["pattern_chart"][pattern])
        truth[pattern] = tuple(
            piece_contains(
                chart_normals,
                int(certificate["signature"][bit]),
                supports[bit],
            )
            for bit in BITS
        )
    expected_truth = {
        1: (False, True, False),
        2: (True, True, False),
        7: (False, False, True),
        12: (True, False, False),
    }
    if truth != expected_truth:
        raise AssertionError(f"wrong piece-separation truth table {truth}")

    print("PASS: three distinct cofinal circuit pieces meet at the exact bad chart")
    print("supports=" + " ; ".join("/".join(EXPECTED_SUPPORTS[bit]) for bit in BITS))
    print("union degree vector=" + str(degrees))
    print("PASS: union is pencil-rigid, common-apex-free, and support-plane rigid")
    print("PASS: exact charts distinguish all three pieces and realize all signatures")
    print("NOTE: no compact component or nonzero H_c^0 is claimed")


if __name__ == "__main__":
    main()
