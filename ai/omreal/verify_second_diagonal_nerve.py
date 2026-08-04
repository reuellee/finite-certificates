#!/usr/bin/env python3
"""Exact checks for the cofinal circuit cover and its exchange obstruction.

The accompanying note proves that the bad locus can be covered using only
five-support circuit pieces.  It also proves a same-signature exchange lemma
on pencil-rigid pair intersections.  This checker verifies the finite claims
used to delimit that lemma on the exact row-2599 pattern-zero survivor:

* supports of size at most five have many five-set paddings;
* signatures 0 and 4 have the stored strict minimal positive 5-circuits;
* their union is pencil-rigid;
* the signatures are proper and incomparable, using the one-bit charts; and
* their two signed witness rays span no additional positive ray for either
  reorientation, because the separation signs are mixed on both support
  differences.

The last item obstructs a cross-signature version of the elementary conic
circuit-exchange proof.  It does not assert a nonzero compact-support class
or disprove the second diagonal.  Only exact integer arithmetic is used.
"""

from itertools import combinations
from math import comb
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "seeat_parent2599_shatter8.npz"
sys.path.insert(0, str(HERE))

import prototype_koszul_circuits as koszul  # noqa: E402


TRIPLES = koszul.TRIPLES
LEFT = 0
RIGHT = 4
PATTERN = 0


def support(weights):
    return tuple(index for index, value in enumerate(weights) if int(value))


def signed_column(normal, signature, index):
    sign = 1 if (signature >> index) & 1 else -1
    return tuple(sign * int(value) for value in normal)


def verify_circuit(normals, signature, weights):
    current = support(weights)
    if len(current) != 5:
        raise AssertionError(f"expected a five-circuit, got {len(current)}")
    coefficients = tuple(int(weights[index]) for index in current)
    if not all(value > 0 for value in coefficients):
        raise AssertionError("circuit coefficient is not strictly positive")
    columns = tuple(
        signed_column(normals[index], signature, index) for index in current
    )
    for coordinate in range(4):
        if sum(
            coefficient * column[coordinate]
            for coefficient, column in zip(coefficients, columns, strict=True)
        ):
            raise AssertionError("stored dependence is not exact")
    if koszul.matrix_rank(columns) != 4:
        raise AssertionError("five-support dependence does not have rank four")
    for omitted in range(5):
        remaining = columns[:omitted] + columns[omitted + 1 :]
        if koszul.matrix_rank(remaining) != 4:
            raise AssertionError("stored dependence is not support-minimal")
    return current


def pencil_rigid(first, second):
    union = set(first) | set(second)
    for label in range(1, 9):
        incident = [set(TRIPLES[index]) for index in union if label in TRIPLES[index]]
        if len(incident) < 3:
            return False
        if set.intersection(*(triple - {label} for triple in incident)):
            return False
    return True


def parent_chirotope(matrix):
    signs = []
    for basis in combinations(range(8), 4):
        value = koszul.determinant(matrix[:, np.asarray(basis)].tolist())
        if not value:
            raise AssertionError("stored parent chart is nonuniform")
        signs.append(1 if value > 0 else -1)
    return tuple(signs)


def extension_signature(matrix, point):
    result = 0
    for index, normal in enumerate(koszul.parent_normals(matrix)):
        value = sum(int(left) * int(right) for left, right in zip(normal, point))
        if not value:
            raise AssertionError("stored extension point is nonuniform")
        if value > 0:
            result |= 1 << index
    return result


def verify_proper_incomparable(certificate, left_signature, right_signature):
    base_parent = parent_chirotope(certificate["pattern_chart"][PATTERN])
    # Pattern 1 realizes LEFT while retaining a bad witness for RIGHT;
    # pattern 16 does the reverse.
    for pattern, good_bit, bad_bit in ((1, LEFT, RIGHT), (16, RIGHT, LEFT)):
        matrix = certificate["pattern_chart"][pattern]
        if parent_chirotope(matrix) != base_parent:
            raise AssertionError("one-bit chart realizes the wrong parent")
        point = certificate["feasible_point"][pattern, good_bit]
        expected = left_signature if good_bit == LEFT else right_signature
        if extension_signature(matrix, point) != expected:
            raise AssertionError("one-bit chart realizes the wrong extension")
        normals = koszul.parent_normals(matrix)
        bad_signature = right_signature if bad_bit == RIGHT else left_signature
        verify_circuit(
            normals,
            bad_signature,
            certificate["gordan_weight"][pattern, bad_bit],
        )


def main():
    # A k-support has C(56-k,5-k) maximal paddings.  Even at k=4 there
    # are 52 choices, enough to avoid any two prescribed five-sets.
    padding_counts = tuple(comb(56 - size, 5 - size) for size in range(1, 6))
    if padding_counts != (341055, 24804, 1378, 52, 1):
        raise AssertionError(f"wrong five-set padding counts {padding_counts}")

    certificate = np.load(CERTIFICATE, allow_pickle=False)
    if int(certificate["parent_index"].item()) != 2599:
        raise AssertionError("wrong parent certificate")
    matrix = certificate["pattern_chart"][PATTERN]
    normals = koszul.parent_normals(matrix)
    left_signature = int(certificate["signature"][LEFT])
    right_signature = int(certificate["signature"][RIGHT])
    left_weights = certificate["gordan_weight"][PATTERN, LEFT]
    right_weights = certificate["gordan_weight"][PATTERN, RIGHT]
    left_support = verify_circuit(normals, left_signature, left_weights)
    right_support = verify_circuit(normals, right_signature, right_weights)

    expected_left = ("123", "134", "267", "258", "468")
    expected_right = ("123", "256", "127", "357", "478")
    if tuple("".join(map(str, TRIPLES[index])) for index in left_support) != expected_left:
        raise AssertionError("wrong left support")
    if tuple("".join(map(str, TRIPLES[index])) for index in right_support) != expected_right:
        raise AssertionError("wrong right support")
    if set(left_support) & set(right_support) != {koszul.TRIPLE_INDEX[(1, 2, 3)]}:
        raise AssertionError("the two supports should meet only in 123")
    if not pencil_rigid(left_support, right_support):
        raise AssertionError("stored support pair is not pencil-rigid")

    separation = left_signature ^ right_signature
    left_difference = tuple(index for index in left_support if index not in right_support)
    right_difference = tuple(index for index in right_support if index not in left_support)
    left_bits = tuple((separation >> index) & 1 for index in left_difference)
    right_bits = tuple((separation >> index) & 1 for index in right_difference)
    if set(left_bits) != {0, 1} or set(right_bits) != {0, 1}:
        raise AssertionError("separation signs are not mixed on both differences")

    # Mixed signs prove the two-ray statement without division or numerical
    # cone computations: in alpha*u+beta*v, rho_LEFT-nonnegativity on
    # R\\Q forces beta to be both >=0 and <=0, hence beta=0.  The symmetric
    # argument on Q\\R forces alpha=0 for rho_RIGHT-nonnegativity.
    verify_proper_incomparable(certificate, left_signature, right_signature)

    degrees = tuple(
        sum(label in TRIPLES[index] for index in set(left_support) | set(right_support))
        for label in range(1, 9)
    )
    if degrees != (3, 5, 3, 3, 3, 3, 4, 3):
        raise AssertionError(f"wrong union degrees {degrees}")

    print("PASS cofinal cover: supports of size <=4 have at least 52 maximal paddings")
    print("PASS exact row-2599 circuits Q0,Q4 are positive, minimal, and pencil-rigid")
    print("PASS one-bit charts certify the two regions are proper and incomparable")
    print("PASS separation signs are mixed on Q0\\Q4 and Q4\\Q0")
    print("THEOREM CHECK: their witness span has no third positive ray for either signature")
    print("CAVEAT this obstructs cross-signature exchange; it does not disprove d1 injectivity")


if __name__ == "__main__":
    main()
