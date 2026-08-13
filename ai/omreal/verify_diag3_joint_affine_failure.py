#!/usr/bin/env python3
"""Exact failure of the square joint-affine fiber test on four triples.

For each triple, choose every factor as the canonical graph anchor, exhaust
its stabilizer presentations, and test every pair of the eight graph
coordinates.  In no presentation are both remaining equations jointly
affine in the same two coordinates.  Hence the two-equation/two-variable
affine-system lemma cannot settle these triples.
"""

from __future__ import annotations

import hashlib
from itertools import combinations
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import verify_diag2_pivot_all_pair_fibers as fibers  # noqa: E402
import verify_residual_log_binomials as poly  # noqa: E402


PIVOT = {36: 0, 38: 0, 48: 0, 49: 3, 50: 3, 51: 5}
TRIPLES = (
    (12_985, 16_183, 7_196),
    (20_355, 5_442, 5_949),
    (9_667, 16_486, 26_315),
    (9_758, 24_338, 15_810),
)
EXPECTED_TRIED = (448, 336, 336, 3_136)
EXPECTED_DIGEST = "b0afc43dab23018d2d7be17b1f760bed94ed64e4c9183bebb41b511a18e54de3"


def jointly_affine(polynomial, left, right):
    return all(
        monomial[left] + monomial[right] <= 1 for monomial in polynomial
    )


def main():
    occurrences, occurrence_factor, factor_polynomial = labeled.factor_polynomials()
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    canonical, _anchor_alignments, stabilizers = labeled.canonical_anchor_alignments(
        occurrences, occurrence_factor, factor_occurrence
    )
    _representatives, _full_stabilizers, alignment, _factor_occurrence, _sizes = (
        labeled.factor_orbit_data(occurrences, occurrence_factor)
    )

    anchor_data = {}
    for kind, pivot in PIVOT.items():
        slope, constant = fibers.pivot_split(
            factor_polynomial[canonical[kind]], pivot
        )
        anchor_data[kind] = (pivot, slope, poly.negative(constant))

    reports = []
    for triple in TRIPLES:
        tried = 0
        presentations = 0
        hits = []
        anchor_counts = []
        for anchor_index, anchor in enumerate(triple):
            others = tuple(
                triple[index] for index in range(3) if index != anchor_index
            )
            kind, mapping = alignment[anchor]
            moved = tuple(
                labeled.transform_factor(
                    item, mapping, factor_occurrence, occurrence_factor
                )
                for item in others
            )
            pivot, slope, numerator = anchor_data[kind]
            seen = set()
            for symmetry in stabilizers[kind]:
                targets = tuple(
                    labeled.transform_factor(
                        item, symmetry, factor_occurrence, occurrence_factor
                    )
                    for item in moved
                )
                if targets in seen:
                    continue
                seen.add(targets)
                presentations += 1
                restricted = tuple(
                    fibers.graph_restrict(
                        factor_polynomial[item], pivot, slope, numerator
                    )
                    for item in targets
                )
                for left, right in combinations(
                    (index for index in range(9) if index != pivot), 2
                ):
                    tried += 1
                    if all(
                        jointly_affine(polynomial, left, right)
                        for polynomial in restricted
                    ):
                        hits.append((kind, targets, pivot, left, right))
            anchor_counts.append((kind, len(seen)))
        if hits:
            raise AssertionError(f"joint-affine presentation appeared: {hits[:3]}")
        report = (triple, tried, presentations, tuple(anchor_counts), tuple(hits))
        reports.append(report)
        print(
            "TRIPLE", triple,
            "presentations", presentations,
            "coordinate pairs", tried,
            "joint-affine", len(hits),
        )

    if tuple(report[1] for report in reports) != EXPECTED_TRIED:
        raise AssertionError("joint-affine candidate counts changed")
    semantic = ("diag3-joint-affine-failure-v1", tuple(reports))
    digest = hashlib.sha256(repr(semantic).encode("ascii")).hexdigest()
    if digest != EXPECTED_DIGEST:
        raise AssertionError(f"semantic digest changed: {digest}")
    print("SEMANTIC", digest)
    print("NO-GO square joint-affine fibers close none of the four triples")


if __name__ == "__main__":
    main()
