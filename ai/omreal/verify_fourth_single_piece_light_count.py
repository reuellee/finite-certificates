#!/usr/bin/env python3
"""Exhaustive light-label audit for the fourth single-piece column.

This checker enumerates every set of at most five distinct triples on eight
labels.  It verifies the two incidence claims used in
``THREE_SHEAR_SINGLE_PIECE_REDUCTION.md``:

* an omitted-label support always has a second label of degree at most two;
* a cover-all support has a degree-one label whose unique triple leaves at
  least two distinct degree-at-most-two labels outside it.

The first statement feeds the proved omitted-label-plus-pencil four-fiber
theorem.  The second is intentionally reported only as a parameter count:
the top-component-sheaf obstruction means that it does not prove the
cover-all H_c^3 vanishing.
"""

from itertools import combinations


TRIPLES = tuple(combinations(range(8), 3))
ALL_LABELS = (1 << 8) - 1
EXPECTED_COUNTS = {
    "total": 4_216_422,
    "omitted": 2_500_442,
    "cover_all": 1_715_980,
    "cover_all_three": 840,
    "cover_all_four": 72_380,
    "cover_all_five": 1_642_760,
}


def degree_data(support):
    degrees = [0] * 8
    covered = 0
    for triple in support:
        for label in triple:
            degrees[label] += 1
            covered |= 1 << label
    return tuple(degrees), covered


def cover_all_witness(support, degrees):
    for label, degree in enumerate(degrees):
        if degree != 1:
            continue
        unique = next(triple for triple in support if label in triple)
        light_outside = tuple(
            other
            for other, other_degree in enumerate(degrees)
            if other not in unique and other_degree <= 2
        )
        if len(light_outside) >= 2:
            return label, unique, light_outside[:2]
    return None


def main():
    counts = {
        "total": 0,
        "omitted": 0,
        "cover_all": 0,
        "cover_all_three": 0,
        "cover_all_four": 0,
        "cover_all_five": 0,
    }
    for size in range(1, 6):
        for support in combinations(TRIPLES, size):
            counts["total"] += 1
            degrees, covered = degree_data(support)
            if covered != ALL_LABELS:
                counts["omitted"] += 1
                omitted = next(
                    label for label, degree in enumerate(degrees) if degree == 0
                )
                assert any(
                    label != omitted and degree <= 2
                    for label, degree in enumerate(degrees)
                )
                continue

            counts["cover_all"] += 1
            key = {
                3: "cover_all_three",
                4: "cover_all_four",
                5: "cover_all_five",
            }[size]
            counts[key] += 1
            assert cover_all_witness(support, degrees) is not None

    assert counts == EXPECTED_COUNTS
    print("PASS: exhaustively checked every support of one through five triples")
    print(f"TOTAL={counts['total']}")
    print(f"OMITTED={counts['omitted']}")
    print(f"COVER_ALL={counts['cover_all']}")
    print(f"COVER_ALL_SIZE3={counts['cover_all_three']}")
    print(f"COVER_ALL_SIZE4={counts['cover_all_four']}")
    print(f"COVER_ALL_SIZE5={counts['cover_all_five']}")
    print("THEOREM INPUT: every omitted support has a second light label")
    print("COUNT ONLY: every cover-all support has plane + two-pencil data")
    print("CAVEAT: the cover-all H_c^3 top-component sheaf remains unresolved")


if __name__ == "__main__":
    main()
