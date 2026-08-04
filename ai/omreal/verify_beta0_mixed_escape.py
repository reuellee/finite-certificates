#!/usr/bin/env python3
"""Exact verifier for the two row-2599 beta-zero mixed escape lemmas.

The shatter certificate contains three pencil-rigid positive 4+5 occurrences
with beta=0.  There are only two distinct signed support pairs: patterns 4 and
102 use CASE_A, while pattern 217 uses CASE_B.  This checker verifies the
finite algebra used by ``BETA0_MIXED_ESCAPE.md``:

* both full support pairs have gauge rank seven;
* deleting any support triple destroys pencil rigidity;
* the displayed integer endomorphism projectively stabilizes both signed
  sparse three-vectors in each case;
* its projective common stabilizer has dimension two (the scalar direction
  and the displayed non-diagonal direction); and
* the listed eigenvectors form a basis with the claimed eigenvalues.

It also gives an exact combinatorial beta=0 pair whose projective common
infinitesimal stabilizer consists only of scalars.  Thus beta=0 by itself does
not imply the non-diagonal one-parameter escape used for the two realizable
row-2599 survivors.

Only integer and rational arithmetic is used.
"""

from fractions import Fraction
from itertools import combinations
from pathlib import Path

import numpy as np


VERTICES = tuple(range(1, 9))
TRIPLES = tuple(
    sorted(combinations(VERTICES, 3), key=lambda triple: tuple(reversed(triple)))
)
TRIPLE_INDEX = {triple: index for index, triple in enumerate(TRIPLES)}
WEDGE_BASIS = tuple(combinations(range(8), 3))
CERTIFICATE = Path(__file__).resolve().parent / "data" / "seeat_parent2599_shatter8.npz"


def parse_support(labels):
    return tuple(tuple(int(character) for character in label) for label in labels)


def incidence(triple):
    return tuple(int(vertex in triple) for vertex in VERTICES)


def gauge_matrix(first, second):
    rows = []
    for support in (first, second):
        base = incidence(support[0])
        for triple in support[1:]:
            rows.append(tuple(x - y for x, y in zip(incidence(triple), base)))
    return rows


def rational_rank(matrix):
    rows = [[Fraction(value) for value in row] for row in matrix]
    if not rows:
        return 0
    pivot_row = 0
    for column in range(len(rows[0])):
        pivot = next(
            (row for row in range(pivot_row, len(rows)) if rows[row][column]),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        scale = rows[pivot_row][column]
        rows[pivot_row] = [entry / scale for entry in rows[pivot_row]]
        for row in range(len(rows)):
            if row == pivot_row or not rows[row][column]:
                continue
            scale = rows[row][column]
            rows[row] = [
                left - scale * right
                for left, right in zip(rows[row], rows[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def subsets(support):
    for size in range(1, len(support) + 1):
        yield from combinations(support, size)


def pencil_rigid(first, second):
    union = set(first) | set(second)
    degrees = {
        vertex: sum(vertex in triple for triple in union) for vertex in VERTICES
    }
    if min(degrees.values()) < 3:
        return False
    for vertex in VERTICES:
        incident = [triple for triple in union if vertex in triple]
        if any(
            all(partner in triple for triple in incident)
            for partner in VERTICES
            if partner != vertex
        ):
            return False
    return True


def signed_tensor(support, signs):
    return {
        tuple(vertex - 1 for vertex in triple): sign
        for triple, sign in zip(support, signs)
    }


def permutation_sign(sequence):
    inversions = sum(
        sequence[left] > sequence[right]
        for left in range(len(sequence))
        for right in range(left + 1, len(sequence))
    )
    return -1 if inversions % 2 else 1


def exterior_derivation(matrix, tensor):
    """Infinitesimal GL(8) action on a sparse element of Lambda^3."""
    result = {triple: 0 for triple in WEDGE_BASIS}
    for triple, coefficient in tensor.items():
        for position, source in enumerate(triple):
            for target in range(8):
                entry = matrix[target][source]
                if not entry:
                    continue
                sequence = list(triple)
                sequence[position] = target
                if len(set(sequence)) < 3:
                    continue
                output = tuple(sorted(sequence))
                result[output] += coefficient * entry * permutation_sign(sequence)
    return {triple: value for triple, value in result.items() if value}


def scaled_tensor(tensor, scale):
    return {
        triple: scale * value
        for triple, value in tensor.items()
        if scale * value
    }


def matvec(matrix, vector):
    return tuple(
        sum(entry * coordinate for entry, coordinate in zip(row, vector))
        for row in matrix
    )


def standard_vector(index):
    return tuple(int(coordinate == index) for coordinate in range(8))


def add(*vectors):
    return tuple(sum(entries) for entries in zip(*vectors))


def scale(value, vector):
    return tuple(value * entry for entry in vector)


def rank_mod_prime(matrix, prime=1_000_003):
    rows = [[value % prime for value in row] for row in matrix]
    if not rows:
        return 0
    pivot_row = 0
    for column in range(len(rows[0])):
        pivot = next(
            (row for row in range(pivot_row, len(rows)) if rows[row][column]),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        inverse = pow(rows[pivot_row][column], prime - 2, prime)
        rows[pivot_row] = [(value * inverse) % prime for value in rows[pivot_row]]
        for row in range(len(rows)):
            if row == pivot_row or not rows[row][column]:
                continue
            multiplier = rows[row][column]
            rows[row] = [
                (left - multiplier * right) % prime
                for left, right in zip(rows[row], rows[pivot_row])
            ]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def projective_stabilizer_rank(tensors):
    """Rank of A.c_j = mu_j c_j in 64+len(tensors) unknowns."""
    rows = []
    for block, tensor in enumerate(tensors):
        for output in WEDGE_BASIS:
            row = [0] * (64 + len(tensors))
            for triple, coefficient in tensor.items():
                for position, source in enumerate(triple):
                    for target in range(8):
                        sequence = list(triple)
                        sequence[position] = target
                        if len(set(sequence)) < 3:
                            continue
                        if tuple(sorted(sequence)) != output:
                            continue
                        row[8 * target + source] += (
                            coefficient * permutation_sign(sequence)
                        )
            row[64 + block] -= tensor.get(output, 0)
            rows.append(row)
    return rank_mod_prime(rows)


def check_case(case):
    first, second = case["supports"]
    first_tensor = signed_tensor(first, case["signs"][0])
    second_tensor = signed_tensor(second, case["signs"][1])
    tensors = (first_tensor, second_tensor)

    full_gauge = gauge_matrix(first, second)
    assert len(full_gauge) == rational_rank(full_gauge) == 7
    assert pencil_rigid(first, second)
    degrees = tuple(
        sum(vertex in triple for triple in set(first) | set(second))
        for vertex in VERTICES
    )
    assert degrees == case["degrees"] and len(set(first) | set(second)) == 9

    # Full row independence makes beta=0 hereditary on every support face.
    # More importantly for topology, every proper face loses pencil rigidity.
    face_count = 0
    for first_face in subsets(first):
        for second_face in subsets(second):
            rows = gauge_matrix(first_face, second_face)
            assert rational_rank(rows) == len(rows)
            if first_face != first or second_face != second:
                assert not pencil_rigid(first_face, second_face)
            face_count += 1
    assert face_count == (2 ** len(first) - 1) * (2 ** len(second) - 1) == 465

    matrix = case["matrix"]
    assert exterior_derivation(matrix, first_tensor) == scaled_tensor(
        first_tensor, case["multipliers"][0]
    )
    assert exterior_derivation(matrix, second_tensor) == scaled_tensor(
        second_tensor, case["multipliers"][1]
    )

    eigenvectors = case["eigenvectors"]
    assert rational_rank([tuple(vector) for vector, _ in eigenvectors]) == 8
    for vector, eigenvalue in eigenvectors:
        assert matvec(matrix, vector) == scale(eigenvalue, vector)

    # A modular rank of 64 is an exact rational-rank certificate: the scalar
    # and displayed A give two independent nullvectors, hence rank_Q <= 64,
    # while rank modulo a prime is a lower bound for rank_Q.
    assert projective_stabilizer_rank(tensors) == 64
    return face_count


E = tuple(standard_vector(index) for index in range(8))

CASE_A = {
    "supports": (
        parse_support(("156", "456", "127", "347", "578")),
        parse_support(("134", "235", "238", "368")),
    ),
    "signs": ((-1, -1, -1, +1, +1), (-1, +1, -1, +1)),
    "degrees": (3, 3, 5, 3, 4, 3, 3, 3),
    "matrix": (
        (-2, 0, 0, 9, 0, 0, 0, 0),
        (0, 4, 0, 0, 0, 0, 0, 0),
        (0, -9, -5, 0, 0, 0, 0, 0),
        (0, 0, 0, 7, 0, 0, 0, 0),
        (0, 0, 0, 0, 1, 0, 0, 0),
        (0, 0, 0, 0, 0, 4, 0, 0),
        (0, 0, 0, 0, 0, 0, 10, 0),
        (0, 0, 0, 0, 0, 0, 0, 1),
    ),
    "multipliers": (12, 0),
    "eigenvectors": (
        (E[0], -2),
        (add(E[0], E[3]), 7),
        (add(E[1], scale(-1, E[2])), 4),
        (E[5], 4),
        (E[2], -5),
        (E[4], 1),
        (E[7], 1),
        (E[6], 10),
    ),
}

CASE_B = {
    "supports": (
        parse_support(("147", "157", "367", "258", "468")),
        parse_support(("123", "345", "237", "368")),
    ),
    "signs": ((+1, -1, +1, -1, -1), (-1, +1, -1, +1)),
    "degrees": (3, 3, 5, 3, 3, 3, 4, 3),
    "matrix": (
        (-1, 0, 0, 0, 0, 0, 0, 0),
        (0, 5, 0, 0, 0, 0, 0, 0),
        (0, 0, -4, 0, 0, 0, 0, 0),
        (0, 0, 0, 2, 0, 0, 0, 0),
        (0, 0, 0, 0, 2, 0, 0, 0),
        (0, 0, 0, 0, 0, 5, 0, 0),
        (-6, 0, 0, 0, 0, 0, 5, 0),
        (0, 0, 0, 0, 0, 0, 0, -1),
    ),
    "multipliers": (6, 0),
    "eigenvectors": (
        (add(E[0], E[6]), -1),
        (E[7], -1),
        (E[1], 5),
        (E[5], 5),
        (E[6], 5),
        (E[2], -4),
        (E[3], 2),
        (E[4], 2),
    ),
}


def check_beta_zero_no_go():
    """Beta=0 does not force a non-diagonal infinitesimal stabilizer."""
    first = parse_support(("136", "147", "257", "348", "358"))
    second = parse_support(("126", "246", "467", "568"))
    assert pencil_rigid(first, second)
    matrix = gauge_matrix(first, second)
    assert len(matrix) == rational_rank(matrix) == 7
    tensors = (
        signed_tensor(first, (+1,) * 5),
        signed_tensor(second, (+1,) * 4),
    )
    # 66 unknowns and rank 65 leave exactly the scalar direction.
    assert projective_stabilizer_rank(tensors) == 65


def support_from_certificate(certificate, pattern, bit):
    return tuple(
        TRIPLES[index]
        for index, value in enumerate(certificate["gordan_weight"][pattern, bit])
        if int(value)
    )


def signs_from_certificate(certificate, bit, support):
    signature = int(certificate["signature"][bit])
    return tuple(
        +1 if (signature >> TRIPLE_INDEX[triple]) & 1 else -1
        for triple in support
    )


def check_certificate_occurrences():
    certificate = np.load(CERTIFICATE, allow_pickle=False)
    assert int(certificate["parent_index"].item()) == 2599
    occurrences = []
    for pattern in range(256):
        bad = [bit for bit in range(8) if not (pattern >> bit) & 1]
        supports = {
            bit: support_from_certificate(certificate, pattern, bit) for bit in bad
        }
        for position, left in enumerate(bad):
            for right in bad[position + 1 :]:
                first, second = supports[left], supports[right]
                if sorted((len(first), len(second))) != [4, 5]:
                    continue
                if not pencil_rigid(first, second):
                    continue
                rows = gauge_matrix(first, second)
                if len(rows) - rational_rank(rows) == 0:
                    occurrences.append((pattern, left, right))
    assert occurrences == [(4, 3, 7), (102, 3, 7), (217, 2, 5)]

    expected = {
        (4, 3): (CASE_A["supports"][0], CASE_A["signs"][0]),
        (4, 7): (CASE_A["supports"][1], CASE_A["signs"][1]),
        (102, 3): (CASE_A["supports"][0], CASE_A["signs"][0]),
        (102, 7): (CASE_A["supports"][1], CASE_A["signs"][1]),
        (217, 2): (CASE_B["supports"][1], CASE_B["signs"][1]),
        (217, 5): (CASE_B["supports"][0], CASE_B["signs"][0]),
    }
    for key, (support, signs) in expected.items():
        pattern, bit = key
        assert support_from_certificate(certificate, pattern, bit) == support
        assert signs_from_certificate(certificate, bit, support) == signs
        assert all(
            int(certificate["gordan_weight"][pattern, bit, TRIPLE_INDEX[triple]]) > 0
            for triple in support
        )


def main():
    assert check_case(CASE_A) == 465
    assert check_case(CASE_B) == 465
    check_certificate_occurrences()
    check_beta_zero_no_go()
    print("PASS: both exact row-2599 beta=0 mixed support pairs have gauge rank 7")
    print("PASS: all 928 proper witness-face pairs are pencil-flexible")
    print("PASS: both full signed tensor pairs have a non-diagonal shear stabilizer")
    print("THEOREM: all three exact row-2599 mixed occurrences have H_c^0 = 0")
    print("CAVEAT: beta=0 alone need not give a non-diagonal 1-parameter stabilizer")


if __name__ == "__main__":
    main()
