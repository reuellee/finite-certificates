#!/usr/bin/env python3
"""Exact block-Gordan pivot audit at the saved hard third-diagonal triple.

The three circuit pieces in ``verify_third_diagonal_triple_obstruction.py``
are rigid if their displayed supports are frozen.  This checker retains the
whole positive-dependence polytope for each signature instead.  It proves:

* the three displayed circuit vertices have respectively 51, 33, and 51
  strict one-exchange neighbours (52, 34, and 52 vertices when the original
  vertex is included);
* no one- or two-block change makes the support union pencil-flexible;
* 18,480 three-block pivot corners do make it flexible, always by lowering
  the degree of label 1 to two; and
* one explicit choice of three pivot edges forms a literal 3-cube in the
  product of the three normalized Gordan polytopes whose opposite corner is
  killed by the degree-two pencil lemma.

This is a local exact cancellation candidate, not a global Morse matching:
the chosen pivot vertices can disappear at cofactor walls as the parent
realization moves.
"""

from collections import Counter
from itertools import product
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import prototype_koszul_circuits as koszul  # noqa: E402


CERTIFICATE = HERE / "data" / "seeat_parent2599_shatter8.npz"
BITS = (0, 4, 3)
EXPECTED_ORIGINAL = {
    0: ("123", "134", "267", "258", "468"),
    4: ("123", "256", "127", "357", "478"),
    3: ("123", "256", "356", "127", "347"),
}
DISTINGUISHED_PIVOT = {
    0: ("134", "234", "267", "258", "468"),
    4: ("134", "256", "127", "357", "478"),
    3: ("134", "256", "356", "127", "347"),
}
EXPECTED_VERTEX_COUNTS = {0: 52, 4: 34, 3: 52}
EXPECTED_CORNER_STRATA = Counter({
    (2, False): 18_480,
    (3, False): 49_376,
    (4, False): 23_963,
    (5, False): 117,
})


def name(index):
    return "".join(map(str, koszul.TRIPLES[index]))


def indices(names):
    lookup = {
        "".join(map(str, triple)): index
        for index, triple in enumerate(koszul.TRIPLES)
    }
    return tuple(sorted(lookup[value] for value in names))


def stored_support(certificate, bit):
    return tuple(
        index
        for index, value in enumerate(certificate["gordan_weight"][0, bit])
        if int(value)
    )


def signed_columns(normals, signature, support):
    return [
        tuple(
            value if (signature >> index) & 1 else -value
            for value in normals[index]
        )
        for index in support
    ]


def circuit_coefficients(normals, signature, support):
    """Return exact positive primitive cofactors, or ``None``."""
    if len(support) != 5 or len(set(support)) != 5:
        return None
    columns = signed_columns(normals, signature, support)
    cofactors = []
    for omitted in range(5):
        selected = [
            columns[index]
            for index in range(5)
            if index != omitted
        ]
        determinant = koszul.determinant([
            [column[row] for column in selected]
            for row in range(4)
        ])
        cofactors.append((-1 if omitted & 1 else 1) * determinant)
    if all(value < 0 for value in cofactors):
        cofactors = [-value for value in cofactors]
    if not all(value > 0 for value in cofactors):
        return None
    return tuple(koszul.primitive(cofactors))


def one_exchange_vertices(normals, signature, original):
    vertices = {original}
    for removed in original:
        retained = set(original) - {removed}
        for added in range(len(koszul.TRIPLES)):
            candidate = tuple(sorted(retained | {added}))
            if (
                len(candidate) == 5
                and candidate != original
                and circuit_coefficients(normals, signature, candidate) is not None
            ):
                vertices.add(candidate)
    return tuple(sorted(vertices))


def union_statistics(supports):
    union = set().union(*map(set, supports))
    degrees = tuple(
        sum(label in koszul.TRIPLES[index] for index in union)
        for label in range(1, 9)
    )
    fixed_partner = False
    for label in range(1, 9):
        incident = [
            set(koszul.TRIPLES[index])
            for index in union
            if label in koszul.TRIPLES[index]
        ]
        if not incident:
            fixed_partner = True
            continue
        if set.intersection(*(triple - {label} for triple in incident)):
            fixed_partner = True
    return degrees, fixed_partner


def verify_edge(normals, signature, left, right):
    if len(set(left) & set(right)) != 4:
        raise AssertionError("distinguished pivot is not a one-exchange move")
    union = tuple(sorted(set(left) | set(right)))
    columns = signed_columns(normals, signature, union)
    rank = koszul.matrix_rank(columns)
    if (len(union), rank, len(union) - rank - 1) != (6, 4, 1):
        raise AssertionError("pivot vertices do not span a one-dimensional face")
    if circuit_coefficients(normals, signature, left) is None:
        raise AssertionError("left endpoint is not a strict positive circuit")
    if circuit_coefficients(normals, signature, right) is None:
        raise AssertionError("right endpoint is not a strict positive circuit")


def main():
    certificate = np.load(CERTIFICATE, allow_pickle=False)
    if int(certificate["parent_index"].item()) != 2599:
        raise AssertionError("wrong parent certificate")
    normals = koszul.parent_normals(certificate["pattern_chart"][0])

    originals = {bit: stored_support(certificate, bit) for bit in BITS}
    displayed = {
        bit: tuple(name(index) for index in support)
        for bit, support in originals.items()
    }
    if displayed != EXPECTED_ORIGINAL:
        raise AssertionError(f"unexpected original supports {displayed}")

    signatures = {
        bit: int(certificate["signature"][bit])
        for bit in BITS
    }
    vertices = {
        bit: one_exchange_vertices(normals, signatures[bit], originals[bit])
        for bit in BITS
    }
    counts = {bit: len(vertices[bit]) for bit in BITS}
    if counts != EXPECTED_VERTEX_COUNTS:
        raise AssertionError(f"wrong one-exchange vertex counts {counts}")

    corner_strata = Counter()
    flexible = 0
    minimum_changed = len(BITS) + 1
    flexible_light_labels = Counter()
    for corner in product(*(vertices[bit] for bit in BITS)):
        degrees, fixed_partner = union_statistics(corner)
        corner_strata[min(degrees), fixed_partner] += 1
        if min(degrees) <= 2 or fixed_partner:
            flexible += 1
            changed = sum(
                support != originals[bit]
                for bit, support in zip(BITS, corner, strict=True)
            )
            minimum_changed = min(minimum_changed, changed)
            for label, degree in enumerate(degrees, start=1):
                if degree <= 2:
                    flexible_light_labels[label] += 1

    if corner_strata != EXPECTED_CORNER_STRATA:
        raise AssertionError(f"wrong pivot-corner strata {corner_strata}")
    if flexible != 18_480 or minimum_changed != 3:
        raise AssertionError(
            f"wrong flexible count/minimum change {(flexible, minimum_changed)}"
        )
    if flexible_light_labels != Counter({1: 18_480}):
        raise AssertionError(
            f"unexpected flexible light-label distribution {flexible_light_labels}"
        )

    distinguished = {
        bit: indices(DISTINGUISHED_PIVOT[bit])
        for bit in BITS
    }
    for bit in BITS:
        if distinguished[bit] not in vertices[bit]:
            raise AssertionError("distinguished pivot missing from exact vertex list")
        verify_edge(
            normals,
            signatures[bit],
            originals[bit],
            distinguished[bit],
        )
    far_degrees, far_fixed = union_statistics(
        tuple(distinguished[bit] for bit in BITS)
    )
    if far_degrees != (2, 5, 5, 5, 4, 4, 5, 3) or far_fixed:
        raise AssertionError("distinguished far corner is not the expected pencil exit")

    print("PASS: exact one-exchange Gordan vertices are 52/34/52")
    print("PASS: their product has 91,936 pivot corners in the audited strata")
    print("PASS: exactly 18,480 corners are pencil-flexible, all at label 1")
    print("PASS: every flexible corner changes all three witness blocks")
    print("PASS: the distinguished three pivot edges form a local 3-cube")
    print("far-corner degree vector=" + str(far_degrees))
    print("NOTE: local strict pivots are not a global wall-compatible matching")


if __name__ == "__main__":
    main()
