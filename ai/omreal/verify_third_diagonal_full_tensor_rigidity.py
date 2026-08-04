#!/usr/bin/env python3
"""Exact full sparse-tensor rigidity check for the hard s=3 triple.

The existing triple-obstruction verifier proves only support-plane rigidity.
Here the three exact signed Gordan tensors themselves are retained.  We solve

    A.c_j = mu_j c_j,  j=1,2,3,

for ``A in gl(8)`` and one line-scaling ``mu_j`` per tensor.  Modular rank is
enough for an exact rational conclusion: the scalar solution is exhibited,
while rank ``number_of_variables-1`` modulo a prime bounds the rational
kernel by that same one dimension.

The first two tensors have one additional stabilizer direction, serving as a
positive control.  Adding the third leaves only scalar matrices.  This rules
out a simultaneous GL(8) sparse-tensor orbit as an escape for this exact
triple; it does not prove a compact component or nonzero cohomology.
"""

from itertools import combinations
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "seeat_parent2599_shatter8.npz"
PRIME = 1_000_000_007
BITS = (0, 4, 3)
# Certificate coordinates use colex order, not Python's lexicographic order.
# Keeping the ordering construction local makes this checker independent of
# the other verifier modules.
TRIPLES = tuple(
    sorted(combinations(range(8), 3), key=lambda triple: tuple(reversed(triple)))
)
TRIPLE_INDEX = {triple: index for index, triple in enumerate(TRIPLES)}
EXPECTED_SUPPORTS = (
    ("123", "134", "267", "258", "468"),
    ("123", "256", "127", "357", "478"),
    ("123", "256", "356", "127", "347"),
)


def modular_rank(matrix):
    rows = [[int(value) % PRIME for value in row] for row in matrix]
    rank = 0
    for column in range(len(rows[0])):
        pivot = next(
            (row for row in range(rank, len(rows)) if rows[row][column]),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        inverse = pow(rows[rank][column], PRIME - 2, PRIME)
        rows[rank] = [(value * inverse) % PRIME for value in rows[rank]]
        for row in range(len(rows)):
            if row == rank or not rows[row][column]:
                continue
            factor = rows[row][column]
            rows[row] = [
                (left - factor * right) % PRIME
                for left, right in zip(rows[row], rows[rank], strict=True)
            ]
        rank += 1
    return rank


def signed_tensor(certificate, bit):
    signature = int(certificate["signature"][bit])
    weights = certificate["gordan_weight"][0, bit]
    return tuple(
        int(weight) * (1 if (signature >> index) & 1 else -1)
        for index, weight in enumerate(weights)
    )


def action_matrix(tensors):
    variable_count = 64 + len(tensors)
    result = []
    for tensor_number, tensor in enumerate(tensors):
        rows = [[0] * variable_count for _ in range(56)]
        for triple_number, coefficient in enumerate(tensor):
            if not coefficient:
                continue
            triple = TRIPLES[triple_number]
            for position, source in enumerate(triple):
                for target in range(8):
                    image = list(triple)
                    image[position] = target
                    if len(set(image)) < 3:
                        continue
                    inversions = sum(
                        image[left] > image[right]
                        for left in range(3)
                        for right in range(left + 1, 3)
                    )
                    row = TRIPLE_INDEX[tuple(sorted(image))]
                    column = 8 * target + source
                    rows[row][column] += (
                        -coefficient if inversions & 1 else coefficient
                    )
            rows[triple_number][64 + tensor_number] -= coefficient
        result.extend(rows)
    return result


def scalar_solution(tensor_count):
    # The identity acts by multiplication by three on Lambda^3.
    vector = [0] * (64 + tensor_count)
    for index in range(8):
        vector[8 * index + index] = 1
    for index in range(tensor_count):
        vector[64 + index] = 3
    return vector


def pair_extra_solution():
    """Primitive non-scalar kernel vector for tensors 0 and 4."""
    vector = [0] * 66
    vector[12] = -973_183_176_868_447
    vector[16] = 1_760_938_244_530_212
    return vector


def multiply(matrix, vector):
    return tuple(
        sum(left * right for left, right in zip(row, vector, strict=True))
        for row in matrix
    )


def main():
    certificate = np.load(CERTIFICATE, allow_pickle=False)
    assert int(certificate["parent_index"].item()) == 2599
    tensors = tuple(signed_tensor(certificate, bit) for bit in BITS)
    assert tuple(sum(value != 0 for value in tensor) for tensor in tensors) == (5, 5, 5)
    displayed_supports = tuple(
        tuple(
            "".join(str(label + 1) for label in TRIPLES[index])
            for index, coefficient in enumerate(tensor)
            if coefficient
        )
        for tensor in tensors
    )
    assert displayed_supports == EXPECTED_SUPPORTS

    pair_matrix = action_matrix(tensors[:2])
    triple_matrix = action_matrix(tensors)
    assert not any(multiply(pair_matrix, scalar_solution(2)))
    assert not any(multiply(pair_matrix, pair_extra_solution()))
    assert pair_extra_solution() != scalar_solution(2)
    assert not any(multiply(triple_matrix, scalar_solution(3)))

    pair_variables = 64 + 2
    triple_variables = 64 + 3
    pair_rank = modular_rank(pair_matrix)
    triple_rank = modular_rank(triple_matrix)
    assert pair_rank == pair_variables - 2
    assert triple_rank == triple_variables - 1

    # Reduction modulo PRIME cannot increase integer/rational rank.  For the
    # pair, modular rank gives the lower bound 64 and the two displayed
    # independent kernels give the upper bound 64.  For the triple, modular
    # rank gives 66 and the scalar kernel gives the matching upper bound.
    # Thus no unproved lucky-prime assumption is present.
    print("PASS: exact pair line-stabilizer dimension is 2 (positive control)")
    print("PASS: exact triple line-stabilizer dimension is 1")
    print("THEOREM: the hard triple's common GL(8) stabilizer is scalar only")
    print("SCOPE: tensor rigidity is a strategy blocker, not a nonzero H_c^0 class")


if __name__ == "__main__":
    main()
