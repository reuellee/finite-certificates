#!/usr/bin/env python3
"""Exact all-residue no-go for common diagonal scaling escapes.

For a polynomial q and exponent vectors alpha, a positive diagonal action

    x_j -> exp(t*w_j) x_j

preserves Z(q) when all alpha have one common w-weight.  Equivalently, w is
annihilated by every exponent difference of q.  This checker proves that the
combined exponent-difference matrix has rank nine already over F_2 for every
row of the pinned final diagonal-three residue.  Rank over Q is therefore
nine too, so no nonzero common weight exists.

The regenerable residue is deliberately an explicit argument: a no-go must
cover the whole 1,162,302-row source rather than a sample of hard rows.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from pathlib import Path
import struct
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402


SOURCE_COUNT = 1_162_302
SOURCE_BYTES = 6_973_816
SOURCE_SHA256 = (
    "34eee303b7981594805958f5dda79058880af66b54f685035ff9c16ee0073cd9"
)
SOURCE_SEMANTIC = (
    "a76a7c2cd6631c2d9724b450540bec7f3be6c106a41ae41f1736bbd2755a5ca4"
)
EXPECTED_FACTOR_RANKS = {
    1: 330,
    3: 936,
    4: 3_600,
    5: 2_448,
    6: 6_240,
    7: 4_944,
    8: 4_912,
    9: 3_330,
}
EXPECTED_SEMANTIC = (
    "d83b42d9a5bd05536829e75e3dd507efa8c2855962a18eed85080c7048e63b9e"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def insert(basis: list[int], vector: int) -> None:
    """Insert one nine-bit vector in an F_2 row-echelon basis."""

    while vector:
        pivot = vector.bit_length() - 1
        if basis[pivot]:
            vector ^= basis[pivot]
        else:
            basis[pivot] = vector
            return


def polynomial_basis(polynomial) -> tuple[int, ...]:
    exponents = tuple(polynomial)
    anchor = exponents[0]
    basis = [0] * 9
    for exponent in exponents[1:]:
        vector = 0
        for index, (left, right) in enumerate(
            zip(exponent, anchor, strict=True)
        ):
            vector |= ((left - right) & 1) << index
        insert(basis, vector)
    return tuple(value for value in basis if value)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("residue", type=Path)
    arguments = parser.parse_args()

    if (
        arguments.residue.stat().st_size != SOURCE_BYTES
        or sha256(arguments.residue) != SOURCE_SHA256
    ):
        raise AssertionError("final-residue file pin changed")
    raw = arguments.residue.read_bytes()
    count, = struct.unpack_from("<I", raw)
    rows = tuple(struct.iter_unpack("<HHH", raw[4:]))
    if count != SOURCE_COUNT or len(rows) != count:
        raise AssertionError("bad final-residue layout")
    source_semantic = hashlib.sha256(raw[4:]).hexdigest()
    if source_semantic != SOURCE_SEMANTIC:
        raise AssertionError("final-residue row semantic changed")

    _occurrences, _occurrence_factor, polynomials = labeled.factor_polynomials()
    factor_bases = tuple(polynomial_basis(polynomial) for polynomial in polynomials)
    factor_ranks = Counter(map(len, factor_bases))
    if dict(sorted(factor_ranks.items())) != EXPECTED_FACTOR_RANKS:
        raise AssertionError("factor exponent-rank census changed")

    semantic = hashlib.sha256(b"diag3-common-scaling-full-rank-f2-v1\0")
    for number, row in enumerate(rows):
        basis = [0] * 9
        for factor in row:
            for vector in factor_bases[factor]:
                insert(basis, vector)
        rank = sum(value != 0 for value in basis)
        if rank != 9:
            raise AssertionError(
                f"common scaling survived at row {number}: {row}, rank {rank}"
            )
        semantic.update(struct.pack("<HHHB", *row, rank))
    digest = semantic.hexdigest()
    if digest != EXPECTED_SEMANTIC:
        raise AssertionError(f"scaling semantic changed: {digest}")

    print("PASS pinned final residue", count, SOURCE_SHA256)
    print("PASS factor exponent ranks", dict(sorted(factor_ranks.items())))
    print("PASS full exponent-difference rank over F2", count)
    print("SEMANTIC", digest)
    print("NO-GO no final-residue row admits a nontrivial common diagonal scaling")
    print("CAVEAT this retires one escape language; it does not close the residue")


if __name__ == "__main__":
    main()
