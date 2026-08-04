#!/usr/bin/env python3
"""Exact combinatorial audit of the block-plus-line three-shear filter.

The input is the stable list of 45 generic five-support orbit representatives
independently certified by the existing C++ and Python third-diagonal
censuses.  For each representative this checker:

* finds a domination witness consisting of a common-apex pair plus one
  further fixed-apex shear, or certifies by exhaustive search that none
  exists;
* computes the exact labeled orbit size under all 40,320 permutations;
* computes the centered-incidence rank over QQ and hence beta; and
* verifies the frozen 38/7 orbit and 669,480/90,720 labeled split; and
* finds a degree-one-plane plus degree-at-most-two pencil witness on all
  seven apparent survivors.

This certifies the finite application of the topological theorem in
``THREE_SHEAR_SINGLE_PIECE_REDUCTION.md``.  It does not certify the theorem's
topological proof or claim that the full third diagonal is proved.
"""

from fractions import Fraction
from itertools import combinations, permutations


REPRESENTATIVES = """
345/236/146/127/128
145/245/236/137/128
245/236/146/137/128
123/345/246/137/128
125/345/246/137/128
135/345/246/137/128
235/345/246/137/128
345/246/156/137/128
345/246/256/137/128
123/234/456/137/128
124/234/456/137/128
234/125/456/137/128
234/235/456/137/128
234/145/456/137/128
234/245/456/137/128
145/236/456/137/128
245/236/456/137/128
345/246/456/137/128
234/456/127/137/128
123/456/137/237/128
124/456/137/237/128
134/456/137/237/128
145/456/137/237/128
345/456/137/237/128
234/356/137/147/128
245/356/137/147/128
234/356/237/147/128
245/356/237/147/128
345/356/237/147/128
356/456/237/147/128
123/156/356/347/128
124/156/356/347/128
125/156/356/347/128
135/156/356/347/128
235/156/356/347/128
245/156/356/347/128
356/456/127/347/128
156/456/137/347/128
256/456/137/347/128
356/456/137/347/128
146/356/347/157/128
246/356/347/157/128
346/356/347/157/128
356/456/347/157/128
346/456/347/357/128
""".split()


EXPECTED_SURVIVORS = (
    "345/246/156/137/128",
    "245/356/237/147/128",
    "356/456/237/147/128",
    "245/156/356/347/128",
    "256/456/137/347/128",
    "146/356/347/157/128",
    "246/356/347/157/128",
)


def parse_support(text):
    return tuple(
        tuple(sorted(int(character) - 1 for character in token))
        for token in text.split("/")
    )


def dominated(support, moving, apex):
    return moving != apex and all(
        moving not in edge or apex in edge for edge in support
    )


def three_shear_witness(support):
    for common_apex in range(8):
        common = tuple(
            moving
            for moving in range(8)
            if dominated(support, moving, common_apex)
        )
        for first, second in combinations(common, 2):
            for third in range(8):
                for third_apex in range(8):
                    moving = {first, second, third}
                    if len(moving) != 3:
                        continue
                    if common_apex in moving or third_apex in moving:
                        continue
                    if dominated(support, third, third_apex):
                        return (
                            (first, common_apex),
                            (second, common_apex),
                            (third, third_apex),
                        )
    return None


def plane_plus_pencil_witness(support):
    """Return (degree-one label, its edge, pencil label) when available."""
    for moving in range(8):
        incident = tuple(edge for edge in support if moving in edge)
        if len(incident) != 1:
            continue
        unique_edge = incident[0]
        for pencil in range(8):
            if pencil in unique_edge:
                continue
            pencil_degree = sum(pencil in edge for edge in support)
            if 1 <= pencil_degree <= 2:
                return moving, unique_edge, pencil
    return None


def two_pencil_witness(support):
    degrees = [sum(vertex in edge for edge in support) for vertex in range(8)]
    light = [vertex for vertex, degree in enumerate(degrees) if degree <= 2]
    for first, second in combinations(light, 2):
        if not any(first in edge and second in edge for edge in support):
            return first, second
    return None


def permuted_support(support, permutation):
    return tuple(sorted(
        tuple(sorted(permutation[vertex] for vertex in edge))
        for edge in support
    ))


def orbit_size(support):
    return len({
        permuted_support(support, permutation)
        for permutation in permutations(range(8))
    })


def rational_rank(rows):
    matrix = [[Fraction(value) for value in row] for row in rows]
    rank = 0
    for column in range(len(matrix[0])):
        pivot = next(
            (row for row in range(rank, len(matrix)) if matrix[row][column]),
            None,
        )
        if pivot is None:
            continue
        matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
        value = matrix[rank][column]
        matrix[rank] = [entry / value for entry in matrix[rank]]
        for row in range(len(matrix)):
            if row == rank or not matrix[row][column]:
                continue
            factor = matrix[row][column]
            matrix[row] = [
                left - factor * right
                for left, right in zip(matrix[row], matrix[rank], strict=True)
            ]
        rank += 1
    return rank


def beta(support):
    base = set(support[0])
    rows = [
        [int(vertex in edge) - int(vertex in base) for vertex in range(8)]
        for edge in support[1:]
    ]
    return 4 - rational_rank(rows)


def fnv64(lines):
    value = 14_695_981_039_346_656_037
    for line in sorted(lines):
        for byte in (line + "\n").encode("ascii"):
            value = ((value ^ byte) * 1_099_511_628_211) & ((1 << 64) - 1)
    return value


def main():
    assert len(REPRESENTATIVES) == len(set(REPRESENTATIVES)) == 45
    assert fnv64(REPRESENTATIVES) == 0x2B0DACE2B3066B2E

    killed = []
    survivors = []
    for text in REPRESENTATIVES:
        support = parse_support(text)
        witness = three_shear_witness(support)
        size = orbit_size(support)
        plane_pencil = plane_plus_pencil_witness(support)
        record = (text, size, beta(support), witness, plane_pencil)
        (killed if witness else survivors).append(record)

    assert tuple(record[0] for record in survivors) == EXPECTED_SURVIVORS
    assert len(killed) == 38 and len(survivors) == 7
    assert sum(record[1] for record in killed) == 669_480
    assert sum(record[1] for record in survivors) == 90_720
    assert all(record[2] == 0 for record in survivors)
    assert all(record[4] is not None for record in survivors)
    # The counting proof in the note is stronger than the 45-orbit audit:
    # every cover-all support of at most five triples has such a witness.
    assert all(record[4] is not None for record in killed + survivors)
    assert sum(record[1] for record in killed + survivors) == 760_200

    print("PASS: stable 45-orbit input fingerprint checked")
    print("PASS: exhaustive domination search kills 38 orbits / 669480 supports")
    print("RESIDUE: 7 orbits / 90720 supports, all beta=0")
    for text, size, current_beta, _witness, plane_pencil in survivors:
        print(f"  orbit={size:5d} beta={current_beta} support={text}")
        print(f"    plane+pencil={plane_pencil}")
    print("THEOREM CHECK: every former survivor has a plane-plus-pencil 3-shear")
    print("CONSEQUENCE: the full single-piece E1^(0,2) column vanishes")

    # Sharp regressions for the multi-piece propagation.  The exact supports
    # are independently tied to row 2599 by the existing common-light and
    # triple-obstruction verifiers.
    pair = set(parse_support(
        "134/234/156/267/258/125/246/147/358/468"
    ))
    triple = set(parse_support(
        "123/134/267/258/468/256/127/357/478/356/347"
    ))
    pair_degrees = tuple(
        sum(vertex in edge for edge in pair) for vertex in range(8)
    )
    triple_degrees = tuple(
        sum(vertex in edge for edge in triple) for vertex in range(8)
    )
    assert pair_degrees == (4, 5, 3, 5, 4, 4, 2, 3)
    assert triple_degrees == (3, 5, 5, 4, 4, 4, 5, 3)
    assert two_pencil_witness(pair) is None
    assert min(triple_degrees) >= 3
    print("REGRESSION: hard pair fails P2 and hard triple fails P1, as required")
    print("SCOPE: pair H_c^1 and triple H_c^0 columns remain open")


if __name__ == "__main__":
    main()
