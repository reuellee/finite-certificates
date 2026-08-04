#!/usr/bin/env python3
"""Exact checks for the fourth-diagonal fivefold reduction.

This verifier checks three finite claims from ``FOURTH_DIAGONAL_FIVEFOLD.md``:

* every support of at most five triples on seven labels has a label of degree
  at most two, the finite Gordan premise in the direct parent-H_5 proof;
* among all 2,021,992 generic support-minimal five-circuits, exactly
  1,099,560 labeled supports in 66 S_8-orbits cover all eight labels; and
* four exact row-2599 shatter signatures are proper and pairwise incomparable,
  have positive support-minimal five-circuits at one common chart, and have a
  pencil-rigid support union from the second piece onward.

The script does not claim that a retained circuit-piece intersection has
nonzero compact-support cohomology.  It uses no floating-point arithmetic,
LP, SAT, or CAD.
"""

from collections import Counter
from itertools import combinations
from math import factorial
from pathlib import Path

import numpy as np

import prototype_koszul_circuits as koszul
import verify_seeat_shatter8 as shatter


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "seeat_parent2599_shatter8.npz"
VERTICES = tuple(range(8))
EDGES = tuple(combinations(VERTICES, 3))
EDGE_INDEX = {edge: index for index, edge in enumerate(EDGES)}
SELECTED_SIGNATURES = (0, 4, 3, 5)
DELETION_EDGES = tuple(combinations(range(7), 3))


def support_mask(indices):
    return sum(1 << index for index in indices)


def support_indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask -= bit


def generic_five(indices):
    """Every four-subset is nonstructural, in incidence form."""
    degrees = [0] * 8
    codegrees = Counter()
    for index in indices:
        edge = EDGES[index]
        for vertex in edge:
            degrees[vertex] += 1
            if degrees[vertex] == 4:
                return None
        for pair in combinations(edge, 2):
            codegrees[pair] += 1
            if codegrees[pair] == 3:
                return None
    return tuple(degrees)


def integer_partitions(total, maximum=None):
    if total == 0:
        yield ()
        return
    maximum = total if maximum is None else min(maximum, total)
    for first in range(maximum, 0, -1):
        for rest in integer_partitions(total - first, first):
            yield (first,) + rest


def permutation_of_cycle_type(parts):
    permutation = list(VERTICES)
    start = 0
    for length in parts:
        cycle = list(range(start, start + length))
        start += length
        for source, target in zip(cycle, cycle[1:] + cycle[:1], strict=True):
            permutation[source] = target
    return tuple(permutation)


def conjugacy_class_size(parts):
    denominator = 1
    for length, multiplicity in Counter(parts).items():
        denominator *= length**multiplicity * factorial(multiplicity)
    return factorial(8) // denominator


def edge_map(permutation):
    return tuple(
        EDGE_INDEX[tuple(sorted(permutation[vertex] for vertex in edge))]
        for edge in EDGES
    )


def invariant_five_sets(permutation):
    """Yield the five-edge subsets fixed by one vertex permutation."""
    mapping = edge_map(permutation)
    visited = set()
    cycles = []
    for edge_index in range(len(EDGES)):
        if edge_index in visited:
            continue
        cycle = []
        current = edge_index
        while current not in visited:
            visited.add(current)
            cycle.append(current)
            current = mapping[current]
        if len(cycle) <= 5:
            cycles.append(tuple(cycle))

    def choose(start, remaining, result):
        if remaining == 0:
            yield result
            return
        for cycle_index in range(start, len(cycles)):
            cycle = cycles[cycle_index]
            if len(cycle) <= remaining:
                yield from choose(
                    cycle_index + 1,
                    remaining - len(cycle),
                    result + cycle,
                )

    yield from choose(0, 5, ())


def generic_support_census():
    expected_labeled = {
        (1, 1, 1, 1, 2, 3, 3, 3): 144_480,
        (1, 1, 1, 2, 2, 2, 3, 3): 582_960,
        (1, 1, 2, 2, 2, 2, 2, 3): 341_880,
        (1, 2, 2, 2, 2, 2, 2, 2): 30_240,
    }
    expected_orbits = {
        (1, 1, 1, 1, 2, 3, 3, 3): 10,
        (1, 1, 1, 2, 2, 2, 3, 3): 30,
        (1, 1, 2, 2, 2, 2, 2, 3): 22,
        (1, 2, 2, 2, 2, 2, 2, 2): 4,
    }

    # Burnside over the 22 conjugacy classes avoids retaining the two-million
    # support set in memory.  The identity class simultaneously supplies the
    # exact labeled census.
    burnside = Counter()
    generic_burnside = 0
    labeled_cover = None
    generic_labeled = None
    for cycle_type in integer_partitions(8):
        fixed_cover = Counter()
        fixed_generic = 0
        for indices in invariant_five_sets(permutation_of_cycle_type(cycle_type)):
            degrees = generic_five(indices)
            if degrees is None:
                continue
            fixed_generic += 1
            if min(degrees):
                fixed_cover[tuple(sorted(degrees))] += 1
        class_size = conjugacy_class_size(cycle_type)
        generic_burnside += class_size * fixed_generic
        for degree_sequence, count in fixed_cover.items():
            burnside[degree_sequence] += class_size * count
        if cycle_type == (1,) * 8:
            labeled_cover = fixed_cover
            generic_labeled = fixed_generic

    if generic_labeled != 2_021_992 or labeled_cover != expected_labeled:
        raise AssertionError(
            f"wrong labeled support census: {generic_labeled}, {labeled_cover}"
        )
    if generic_burnside % factorial(8) or generic_burnside // factorial(8) != 117:
        raise AssertionError("wrong total generic-support Burnside count")
    orbit_cover = Counter()
    for degree_sequence, numerator in burnside.items():
        if numerator % factorial(8):
            raise AssertionError("nonintegral Burnside orbit count")
        orbit_cover[degree_sequence] = numerator // factorial(8)
    if orbit_cover != expected_orbits:
        raise AssertionError(f"wrong cover-all orbit census: {orbit_cover}")

    cover_total = sum(labeled_cover.values())
    cover_orbits = sum(orbit_cover.values())
    if (cover_total, cover_orbits) != (1_099_560, 66):
        raise AssertionError("wrong cover-all totals")
    print("PASS generic five-supports: 2021992 labeled / 117 orbits")
    print("PASS cover-all residue: 1099560 labeled / 66 orbits")
    print("PASS omitted-support deletion removes 922432 labeled / 51 orbits")


def parent_h5_pigeonhole_check():
    """Exhaust the finite support premise in the direct parent H_5 proof."""
    checked = 0
    for size in range(1, 6):
        for support in combinations(DELETION_EDGES, size):
            degrees = [0] * 7
            for edge in support:
                for vertex in edge:
                    degrees[vertex] += 1
            if min(degrees) > 2:
                raise AssertionError("a five-row Gordan support has no light label")
            checked += 1
    if checked != 384_167:
        raise AssertionError(f"wrong seven-label support total {checked}")
    print("PASS all 384167 supports of <=5 triples on 7 labels have degree <=2")
    print("THEOREM PREMISE: every deletion-bad point has a pencil exit")


def signed_rows(normals, signature):
    return [
        tuple(
            value if (signature >> index) & 1 else -value
            for value in normal
        )
        for index, normal in enumerate(normals)
    ]


def positive_minimal_circuit(rows, raw_weights):
    weights = tuple(int(value) for value in raw_weights)
    active = tuple(index for index, value in enumerate(weights) if value)
    if len(active) != 5 or any(weights[index] <= 0 for index in active):
        raise AssertionError("expected a strictly positive five-support")
    for coordinate in range(4):
        if sum(weights[index] * rows[index][coordinate] for index in active):
            raise AssertionError("stored Gordan dependence is nonzero")
    if koszul.matrix_rank([rows[index] for index in active]) != 4:
        raise AssertionError("stored five-circuit is not support-minimal")
    return frozenset(active)


def pencil_rigid(union):
    for label in range(1, 9):
        incident = [
            set(koszul.TRIPLES[index])
            for index in union
            if label in koszul.TRIPLES[index]
        ]
        if len(incident) < 3:
            return False
        if set.intersection(*(edge - {label} for edge in incident)):
            return False
    return True


def exact_four_signature_obstruction():
    certificate = np.load(CERTIFICATE, allow_pickle=False)
    signatures = tuple(int(value) for value in certificate["signature"])
    if len({signatures[index] for index in SELECTED_SIGNATURES}) != 4:
        raise AssertionError("selected signatures are not distinct")

    base_parent, base_normals = shatter.parent_signs_and_rows(
        certificate["pattern_chart"][0]
    )
    supports = []
    for signature_index in SELECTED_SIGNATURES:
        rows = signed_rows(base_normals, signatures[signature_index])
        supports.append(
            positive_minimal_circuit(
                rows, certificate["gordan_weight"][0, signature_index]
            )
        )

    union = set()
    for position, support in enumerate(supports, 1):
        union.update(support)
        if position >= 2 and not pencil_rigid(union):
            raise AssertionError(f"prefix {position} is not pencil-rigid")

    # Select the 16 global shatter patterns in which the four unused bits are
    # zero.  Exact good and Gordan witnesses certify every state of the chosen
    # four coordinates, hence properness and pairwise incomparability.
    for local_pattern in range(1 << len(SELECTED_SIGNATURES)):
        global_pattern = sum(
            ((local_pattern >> local_bit) & 1) << signature_index
            for local_bit, signature_index in enumerate(SELECTED_SIGNATURES)
        )
        parent, normals = shatter.parent_signs_and_rows(
            certificate["pattern_chart"][global_pattern]
        )
        if parent != base_parent:
            raise AssertionError("selected shatter pattern changed the parent")
        for local_bit, signature_index in enumerate(SELECTED_SIGNATURES):
            rows = signed_rows(normals, signatures[signature_index])
            if (local_pattern >> local_bit) & 1:
                shatter.verify_feasible(
                    rows,
                    certificate["feasible_point"][global_pattern, signature_index],
                )
            else:
                shatter.verify_infeasible(
                    rows,
                    certificate["gordan_weight"][global_pattern, signature_index],
                )

    labels = [
        "/".join("".join(map(str, koszul.TRIPLES[index])) for index in sorted(support))
        for support in supports
    ]
    print("PASS four exact row-2599 signatures realize all 16 support patterns")
    print("PASS their pattern-zero five-circuits are positive and support-minimal")
    print("PASS every 2..4 prefix is pencil-rigid")
    print("SUPPORTS " + " | ".join(labels))
    print("CAVEAT nonempty retained intersections do not certify nonzero H_c")


def main():
    parent_h5_pigeonhole_check()
    generic_support_census()
    exact_four_signature_obstruction()
    print("THEOREM CHECK: diagonal s uses at most (s+1)-fold circuit descent")
    print("THEOREM CHECK: fourth diagonal reduces to the retained fivefold complex")


if __name__ == "__main__":
    main()
