#!/usr/bin/env python3
"""Exact genuine survivor of the third-diagonal single-piece filter.

The generic cofinal five-support census has one S_8 orbit with nonzero
weight-gauge modulus after omission and common-apex pruning.  This checker
exhibits that orbit at the exact parent-2599 pattern-zero chart, proves that
its five signed derived normals form a support-minimal positive circuit for a
realizable extension signature, and constructs its primitive gauge invariant.

This proves nonemptiness/properness of the residual support type.  It does not
claim nonzero H_c^2 of the full circuit piece.
"""

from itertools import combinations, permutations
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import prototype_koszul_circuits as koszul  # noqa: E402
import verify_gordan_weight_gauge as gauge  # noqa: E402


CERTIFICATE = HERE / "data" / "seeat_parent2599_shatter8.npz"
SUPPORT_TEXT = ("145", "356", "147", "258", "278")
CANONICAL_TEXT = ("156", "456", "137", "347", "128")
PATTERN = 0
SIGNATURE_INDEX = 1
GOOD_PATTERN = 1 << SIGNATURE_INDEX


def support_from_text(words):
    return tuple(
        koszul.TRIPLE_INDEX[tuple(sorted(map(int, word)))]
        for word in words
    )


def support_mask(support):
    return sum(1 << index for index in support)


def canonical_mask(support):
    result = None
    for permutation in permutations(range(1, 9)):
        image = support_mask(
            koszul.TRIPLE_INDEX[
                tuple(sorted(permutation[vertex - 1] for vertex in koszul.TRIPLES[index]))
            ]
            for index in support
        )
        result = image if result is None else min(result, image)
    return result


def circuit_coefficients(normals, support):
    coefficients = []
    for omitted in range(5):
        columns = [
            normals[support[index]]
            for index in range(5)
            if index != omitted
        ]
        determinant = koszul.determinant(
            [[int(column[row]) for column in columns] for row in range(4)]
        )
        coefficients.append((-1 if omitted & 1 else 1) * determinant)
    return tuple(coefficients)


def signed_rows(normals, signature):
    return [
        tuple(value if (signature >> index) & 1 else -value for value in row)
        for index, row in enumerate(normals)
    ]


def main():
    certificate = np.load(CERTIFICATE, allow_pickle=False)
    if int(certificate["parent_index"].item()) != 2599:
        raise AssertionError("wrong parent certificate")

    support = support_from_text(SUPPORT_TEXT)
    canonical = support_from_text(CANONICAL_TEXT)
    if canonical_mask(support) != support_mask(canonical):
        raise AssertionError("support is not in the unique beta-one orbit")

    # The support covers all labels and has common-apex rank exactly two.
    degrees = {
        vertex: sum(vertex in koszul.TRIPLES[index] for index in support)
        for vertex in range(1, 9)
    }
    if min(degrees.values()) == 0:
        raise AssertionError("support omits a parent label")
    dominated = {
        apex: tuple(
            moving
            for moving in range(1, 9)
            if moving != apex
            and all(
                moving not in koszul.TRIPLES[index]
                or apex in koszul.TRIPLES[index]
                for index in support
            )
        )
        for apex in range(1, 9)
    }
    if max(map(len, dominated.values())) != 2:
        raise AssertionError("wrong common-apex rank")

    matrix, _ = gauge.gauge_matrix((support,))
    if gauge.rank(matrix) != 3:
        raise AssertionError("wrong centered-incidence rank")
    invariant_basis = gauge.nullspace(gauge.transpose(matrix))
    if invariant_basis != ((0, 1, 1, -1),):
        raise AssertionError(f"wrong ratio invariant {invariant_basis}")
    exponents = gauge.full_block_exponents((support,), invariant_basis[0])
    if exponents != ((-1, 0, 1, 1, -1),):
        raise AssertionError(f"wrong full exponents {exponents}")
    gauge.verify_balanced((support,), exponents)

    normals = koszul.parent_normals(certificate["pattern_chart"][PATTERN])
    signature = int(certificate["signature"][SIGNATURE_INDEX])
    coefficients = circuit_coefficients(normals, support)
    positive = tuple(
        coefficient if (signature >> index) & 1 else -coefficient
        for coefficient, index in zip(coefficients, support, strict=True)
    )
    if not all(value > 0 for value in positive):
        raise AssertionError("displayed signed circuit is not positive")
    columns = [signed_rows(normals, signature)[index] for index in support]
    if any(
        sum(weight * column[coordinate] for weight, column in zip(
            positive, columns, strict=True
        ))
        for coordinate in range(4)
    ):
        raise AssertionError("positive weights do not annihilate the normals")
    if koszul.matrix_rank(columns) != 4:
        raise AssertionError("five-normal circuit has wrong rank")
    if any(
        koszul.matrix_rank([columns[index] for index in subset]) != 4
        for subset in combinations(range(5), 4)
    ):
        raise AssertionError("positive circuit is not support-minimal")

    # The same signature is genuinely realizable on the exact one-bit chart,
    # so the positive circuit piece belongs to a proper feasibility region.
    good_normals = koszul.parent_normals(certificate["pattern_chart"][GOOD_PATTERN])
    good_rows = signed_rows(good_normals, signature)
    point = [
        int(value)
        for value in certificate["feasible_point"][GOOD_PATTERN, SIGNATURE_INDEX]
    ]
    if not all(
        sum(value * coordinate for value, coordinate in zip(row, point, strict=True)) > 0
        for row in good_rows
    ):
        raise AssertionError("one-bit chart does not realize the signature")

    primitive = koszul.primitive(positive)
    print("PASS: exact positive proper beta-one five-circuit survivor")
    print("support=" + "/".join(SUPPORT_TEXT))
    print("degree vector=" + str(tuple(degrees.values())))
    print("gauge invariant=lambda_147*lambda_258/(lambda_145*lambda_278)")
    print("primitive positive weights=" + str(tuple(primitive)))
    print("NOTE: nonempty/proper does not imply nonzero H_c^2")


if __name__ == "__main__":
    main()
