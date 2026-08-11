#!/usr/bin/env python3
"""Exact Burnside count for unordered distinct residual-factor triples.

The global residual certificate localizes 84,840 labeled determinant
occurrences to 26,740 primitive factors.  This verifier reconstructs the
induced S_8 action from occurrence equivariance and counts its orbits on
one-, two-, and three-element subsets by Burnside's lemma.  The triple count
is the finite endpoint of the conditional support-drop reduction in
``DIAG3_TRIPLE_FACTOR_REDUCTION.md``; it is not a noncompactness proof for
those triple strata.
"""

from collections import Counter
import hashlib
from itertools import permutations
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402


GROUP_ORDER = 40_320
EXPECTED_ORBITS = (6, 9_476, 79_102_449)
EXPECTED_LABELED_TRIPLES = 3_186_282_165_780
EXPECTED_SEMANTIC_DIGEST = (
    "9dc473537e87e509031d4843d960f5ea4bfefb8508262cd1ebb5d44e1a49913d"
)


def fixed_factor_count(
    permutation, factors, factor_occurrence, occurrence_factor
):
    """Count primitive factors fixed by one label permutation."""

    mapping = labeled.triple_map(permutation)
    return sum(
        labeled.transform_factor(
            factor, mapping, factor_occurrence, occurrence_factor
        )
        == factor
        for factor in factors
    )


def main():
    occurrences, occurrence_factor, _factor_polynomials = labeled.factor_polynomials()
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    factors = tuple(factor_occurrence)
    if len(factors) != 26_740:
        raise AssertionError("wrong residual-factor count")

    classes = Counter()
    representatives = {}
    for permutation in permutations(range(8)):
        cycle_type = labeled.cycle_type(permutation)
        classes[cycle_type] += 1
        representatives.setdefault(cycle_type, permutation)
    if len(classes) != 22 or sum(classes.values()) != GROUP_ORDER:
        raise AssertionError("wrong S_8 conjugacy-class census")

    burnside_sums = [0, 0, 0]
    rows = []
    for cycle_type in sorted(classes):
        multiplicity = classes[cycle_type]
        permutation = representatives[cycle_type]
        square = tuple(permutation[permutation[index]] for index in range(8))
        cube = tuple(permutation[square[index]] for index in range(8))
        fixed1 = fixed_factor_count(
            permutation, factors, factor_occurrence, occurrence_factor
        )
        fixed2 = fixed_factor_count(
            square, factors, factor_occurrence, occurrence_factor
        )
        fixed3 = fixed_factor_count(
            cube, factors, factor_occurrence, occurrence_factor
        )

        # A g-invariant two-subset is either two fixed points or one 2-cycle.
        # A g-invariant three-subset is either three fixed points, one fixed
        # point plus one 2-cycle, or one 3-cycle.
        if (fixed2 - fixed1) % 2 or (fixed3 - fixed1) % 3:
            raise AssertionError("nonintegral factor-cycle count")
        two_cycles = (fixed2 - fixed1) // 2
        three_cycles = (fixed3 - fixed1) // 3
        fixed_subsets = (
            fixed1,
            fixed1 * (fixed1 - 1) // 2 + two_cycles,
            fixed1 * (fixed1 - 1) * (fixed1 - 2) // 6
            + fixed1 * two_cycles
            + three_cycles,
        )
        for index, value in enumerate(fixed_subsets):
            burnside_sums[index] += multiplicity * value
        rows.append(
            (cycle_type, multiplicity, fixed1, fixed2, fixed3, fixed_subsets)
        )

    if any(value % GROUP_ORDER for value in burnside_sums):
        raise AssertionError("nonintegral Burnside quotient")
    orbits = tuple(value // GROUP_ORDER for value in burnside_sums)
    if orbits != EXPECTED_ORBITS:
        raise AssertionError(
            f"factor/pair/triple orbit counts changed: {orbits}"
        )

    labeled_triples = len(factors) * (len(factors) - 1) * (len(factors) - 2) // 6
    if labeled_triples != EXPECTED_LABELED_TRIPLES:
        raise AssertionError("wrong labeled distinct-factor triple count")

    digest = hashlib.sha256()
    digest.update(b"diag3-residual-factor-triple-burnside-v1\0")
    digest.update(repr(tuple(rows)).encode("ascii"))
    semantic_digest = digest.hexdigest()
    if semantic_digest != EXPECTED_SEMANTIC_DIGEST:
        raise AssertionError(
            f"triple-factor Burnside digest changed: {semantic_digest}"
        )

    print(
        "PASS residual-factor subset orbits: "
        "factors=6 pairs=9476 triples=79102449"
    )
    print(f"PASS labeled distinct triples: {labeled_triples}")
    print(f"SEMANTIC {semantic_digest}")
    print(
        "CAVEAT finite endpoint only; triple-factor component "
        "noncompactness is not proved"
    )


if __name__ == "__main__":
    main()
