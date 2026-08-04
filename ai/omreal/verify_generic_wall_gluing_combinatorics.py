#!/usr/bin/env python3
"""Finite incidence checks used by the generic two-sided gluing lemma.

The geometric proof is in NINTH_DIAGONAL_SAFE_GRAPH.md and uses the exact
derived-wall rank and side theorems already checked elsewhere.  This script
isolates its only new finite incidence assertion.

For four triples of parent labels, the derived determinant is structurally
zero exactly when

* all four triples share a label, or
* some three triples share a pair.

A support-minimal structural four-circuit cannot have the second pattern,
because it contains a dependent three-subset.  A nonstructural three-circuit
Q can always be enlarged by a fourth triple J without creating either
structural pattern.  The exhaustive minimum number of choices is 35.
"""

from itertools import combinations


LABELS = tuple(range(8))
TRIPLES = tuple(frozenset(triple) for triple in combinations(LABELS, 3))


def structural_three(circuit):
    return len(set.intersection(*(set(triple) for triple in circuit))) >= 2


def structural_four(edges):
    if set.intersection(*(set(edge) for edge in edges)):
        return True
    return any(
        len(edges[first] & edges[second] & edges[third]) >= 2
        for first, second, third in combinations(range(4), 3)
    )


def main():
    number_three_sets = 0
    structural_three_sets = 0
    extension_counts = []

    for circuit in combinations(TRIPLES, 3):
        number_three_sets += 1
        if structural_three(circuit):
            structural_three_sets += 1
            continue

        choices = tuple(
            fourth
            for fourth in TRIPLES
            if fourth not in circuit and not structural_four(circuit + (fourth,))
        )
        assert choices
        extension_counts.append(len(choices))

    assert number_three_sets == 27_720
    assert structural_three_sets == 560
    assert len(extension_counts) == 27_160
    assert min(extension_counts) == 35

    # Check the minimal structural-four classification directly.
    structural_four_sets = 0
    minimal_structural_four_sets = 0
    for edges in combinations(TRIPLES, 4):
        if not structural_four(edges):
            continue
        structural_four_sets += 1
        has_structural_triple = any(
            structural_three(tuple(edges[index] for index in indices))
            for indices in combinations(range(4), 3)
        )
        if not has_structural_triple:
            minimal_structural_four_sets += 1
            assert set.intersection(*(set(edge) for edge in edges))

    assert structural_four_sets > minimal_structural_four_sets > 0

    print("PASS: 560/27,720 triple supports are structural common-pair circuits")
    print("PASS: every other triple support has >=35 nonstructural fourth triples")
    print("PASS: every minimal structural four-support has one common label")
    print("SCOPE: geometry still uses the derived-wall rank and side theorems")


if __name__ == "__main__":
    main()
