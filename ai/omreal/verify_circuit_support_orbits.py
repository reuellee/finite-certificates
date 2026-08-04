#!/usr/bin/env python3
"""Exact incidence census for generic UOM(4,8) derived circuits.

The 56 derived normals are indexed by the triples of eight parent labels.
The derived-wall classification says that a four-set of normals is
structurally dependent exactly when either

* all four triples share a label, or
* some three triples share a pair of labels.

Away from the thirteen residual derived walls, every other four-set is
independent.  It follows that the unsigned support-minimal circuits have:

* size three: three triples with a common pair;
* size four: four triples with one common label, but no dependent triple;
* size five: every four-subset nonstructural, equivalently every label has
  degree at most three and every label-pair has codegree at most two.

This checker exhausts those supports, their S_8 orbits, and three incidence
filters on pairs of supports.  A label is ``light`` in a support when it
occurs at most once.  Pair counts include repeated supports and are reported
for unordered support multisets; cross-size pairs are already distinguished
by their sizes.  The same-size ordered counts are also checked internally.

A union of supports is called ``shear-rigid`` here when every label occurs at
least twice and no other label belongs to all triples incident with it.  This
is equivalent to requiring, for every ordered pair of unequal labels
``(e,f)``, some union triple which contains ``e`` and omits ``f``.  The
56-bit coverage masks below check exactly this equivalent condition.

IMPORTANT: this is an unsigned incidence calculation.  It does not test that
the circuit signs are positive after either prescribed reorientation, or
that those sign restrictions extend to the two prescribed single-element
extensions.  Those positivity/extension-compatibility tests are essential
additional filters in an application to the second diagonal.  The stronger
projective-plane-pencil lemma in ``ATLAS_HELLY.md`` also requires minimum
union degree three for a compact pair component; this older census deliberately
retains the coarser shear-rigid counts as a reproducible baseline.

Only exact integer arithmetic and the Python standard library are used.
"""

from collections import Counter
from functools import lru_cache
from itertools import combinations, permutations
from math import factorial


VERTICES = tuple(range(8))
FULL_VERTEX_MASK = (1 << 8) - 1
EDGES = tuple(combinations(VERTICES, 3))
EDGE_INDEX = {edge: index for index, edge in enumerate(EDGES)}
EDGE_MASKS = tuple(sum(1 << vertex for vertex in edge) for edge in EDGES)
FULL_SHEAR_MASK = (1 << (8 * 7)) - 1


def shear_bit(vertex, partner):
    """Index the ordered pair (vertex, partner), with unequal entries."""
    assert vertex != partner
    return 1 << (7 * vertex + partner - (partner > vertex))


EDGE_SHEAR_COVERAGE = tuple(
    sum(
        shear_bit(vertex, partner)
        for vertex in edge
        for partner in VERTICES
        if partner not in edge
    )
    for edge in EDGES
)


def support_mask(indices):
    result = 0
    for index in indices:
        result |= 1 << index
    return result


def support_indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask -= bit


def is_generic_circuit(indices):
    """Apply the exact generic incidence criterion for sizes three to five."""
    size = len(indices)
    masks = tuple(EDGE_MASKS[index] for index in indices)

    if size == 3:
        return (masks[0] & masks[1] & masks[2]).bit_count() == 2

    if size == 4:
        if (masks[0] & masks[1] & masks[2] & masks[3]).bit_count() != 1:
            return False
        return all(
            (masks[i] & masks[j] & masks[k]).bit_count() < 2
            for i, j, k in combinations(range(4), 3)
        )

    if size == 5:
        degrees = [0] * 8
        codegrees = Counter()
        for index in indices:
            edge = EDGES[index]
            for vertex in edge:
                degrees[vertex] += 1
                if degrees[vertex] == 4:
                    return False
            for pair in combinations(edge, 2):
                codegrees[pair] += 1
                if codegrees[pair] == 3:
                    return False
        return True

    raise ValueError(f"unsupported circuit size {size}")


def enumerate_supports(size):
    return {
        support_mask(indices)
        for indices in combinations(range(len(EDGES)), size)
        if is_generic_circuit(indices)
    }


PERMUTATIONS = tuple(permutations(VERTICES))
PERMUTATION_INDEX = {
    permutation: index for index, permutation in enumerate(PERMUTATIONS)
}
EDGE_MAPS = tuple(
    tuple(
        EDGE_INDEX[tuple(sorted(permutation[vertex] for vertex in edge))]
        for edge in EDGES
    )
    for permutation in PERMUTATIONS
)


def transform_support(mask, edge_map):
    result = 0
    for index in support_indices(mask):
        result |= 1 << edge_map[index]
    return result


def support_orbits(supports):
    """Consume ``supports`` and return representatives and labeled sizes."""
    representatives = []
    while supports:
        representative = supports.pop()
        orbit = {
            transform_support(representative, edge_map)
            for edge_map in EDGE_MAPS
        }
        supports.difference_update(orbit)
        representatives.append((representative, len(orbit)))
    return representatives


def degree_masks(support):
    degrees = [0] * 8
    for index in support_indices(support):
        for vertex in EDGES[index]:
            degrees[vertex] += 1
    heavy = sum((degree >= 2) << vertex for vertex, degree in enumerate(degrees))
    omitted = sum((degree == 0) << vertex for vertex, degree in enumerate(degrees))
    return heavy, omitted


def shear_defect_mask(support):
    """Ordered pairs (e,f) for which every e-triple also contains f."""
    coverage = 0
    for index in support_indices(support):
        coverage |= EDGE_SHEAR_COVERAGE[index]
    return FULL_SHEAR_MASK ^ coverage


EXPECTED_LABELED_SUPPORTS = {3: 560, 4: 30_240, 5: 2_021_992}
EXPECTED_SUPPORT_ORBITS = {3: 1, 4: 6, 5: 117}
EXPECTED_FIVE_ORBIT_SIZES = {
    40_320: 17,
    20_160: 46,
    10_080: 32,
    5_040: 13,
    3_360: 4,
    2_520: 2,
    1_680: 1,
    672: 1,
    280: 1,
}


# Orbit extraction consumes each support set.  Regenerate the finite census
# afterwards; this avoids holding two two-million-element sets at once.
SUPPORT_ORBITS = {}
for circuit_size in (3, 4, 5):
    generic_supports = enumerate_supports(circuit_size)
    assert len(generic_supports) == EXPECTED_LABELED_SUPPORTS[circuit_size]
    SUPPORT_ORBITS[circuit_size] = support_orbits(generic_supports)
    assert len(SUPPORT_ORBITS[circuit_size]) == EXPECTED_SUPPORT_ORBITS[circuit_size]
    assert sum(size for _, size in SUPPORT_ORBITS[circuit_size]) == (
        EXPECTED_LABELED_SUPPORTS[circuit_size]
    )

assert Counter(size for _, size in SUPPORT_ORBITS[5]) == EXPECTED_FIVE_ORBIT_SIZES

SUPPORTS = {size: enumerate_supports(size) for size in (3, 4, 5)}


# Burnside with the stabilizer of a first support counts diagonal S_8-orbits
# of ordered support pairs without constructing the quadratic pair set.
STABILIZERS = {
    representative: tuple(
        index
        for index, edge_map in enumerate(EDGE_MAPS)
        if transform_support(representative, edge_map) == representative
    )
    for orbits in SUPPORT_ORBITS.values()
    for representative, _ in orbits
}
for orbits in SUPPORT_ORBITS.values():
    for representative, orbit_size in orbits:
        assert len(STABILIZERS[representative]) * orbit_size == factorial(8)


GLOBAL_COUNTERS = {}
for circuit_size, supports in SUPPORTS.items():
    heavy_counter = Counter()
    omitted_counter = Counter()
    shear_counter = Counter()
    for support in supports:
        heavy, omitted = degree_masks(support)
        heavy_counter[heavy] += 1
        omitted_counter[omitted] += 1
        shear_counter[shear_defect_mask(support)] += 1
    GLOBAL_COUNTERS[circuit_size] = (
        heavy_counter,
        omitted_counter,
        shear_counter,
    )


def invariant_support_masks(permutation_index, size):
    """Yield edge subsets of cardinality ``size`` fixed by a permutation."""
    edge_map = EDGE_MAPS[permutation_index]
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
            current = edge_map[current]
        if len(cycle) <= size:
            cycles.append((len(cycle), support_mask(cycle)))

    def choose(start, remaining, result):
        if remaining == 0:
            yield result
            return
        for cycle_index in range(start, len(cycles)):
            cycle_size, cycle_mask = cycles[cycle_index]
            if cycle_size <= remaining:
                yield from choose(
                    cycle_index + 1,
                    remaining - cycle_size,
                    result | cycle_mask,
                )

    yield from choose(0, size, 0)


@lru_cache(maxsize=None)
def fixed_counters(permutation_index, circuit_size):
    """Count fixed circuit supports by heavy and omitted vertex masks."""
    if permutation_index == 0:
        return GLOBAL_COUNTERS[circuit_size]

    heavy_counter = Counter()
    omitted_counter = Counter()
    shear_counter = Counter()
    supports = SUPPORTS[circuit_size]
    for support in invariant_support_masks(permutation_index, circuit_size):
        if support not in supports:
            continue
        heavy, omitted = degree_masks(support)
        heavy_counter[heavy] += 1
        omitted_counter[omitted] += 1
        shear_counter[shear_defect_mask(support)] += 1
    assert sum(heavy_counter.values()) == sum(omitted_counter.values())
    assert sum(heavy_counter.values()) == sum(shear_counter.values())
    return heavy_counter, omitted_counter, shear_counter


def ordered_pair_orbits(first_size, second_size):
    no_common_light = 0
    jointly_omitting = 0
    shear_rigid = 0
    for first, _ in SUPPORT_ORBITS[first_size]:
        first_heavy, first_omitted = degree_masks(first)
        first_shear_defect = shear_defect_mask(first)
        stabilizer = STABILIZERS[first]
        no_light_numerator = 0
        omitted_numerator = 0
        shear_numerator = 0
        for permutation_index in stabilizer:
            heavy_counter, omitted_counter, shear_counter = fixed_counters(
                permutation_index, second_size
            )
            no_light_numerator += sum(
                count
                for heavy, count in heavy_counter.items()
                if (first_heavy | heavy) == FULL_VERTEX_MASK
            )
            omitted_numerator += sum(
                count
                for omitted, count in omitted_counter.items()
                if first_omitted & omitted
            )
            shear_numerator += sum(
                count
                for defect, count in shear_counter.items()
                if not first_shear_defect & defect
            )
        assert no_light_numerator % len(stabilizer) == 0
        assert omitted_numerator % len(stabilizer) == 0
        assert shear_numerator % len(stabilizer) == 0
        no_common_light += no_light_numerator // len(stabilizer)
        jointly_omitting += omitted_numerator // len(stabilizer)
        shear_rigid += shear_numerator // len(stabilizer)
    return no_common_light, jointly_omitting, shear_rigid


EXPECTED_ORDERED_PAIR_ORBITS = {
    (3, 3): (0, 25),
    (3, 4): (0, 291),
    (3, 5): (942, 5_929),
    (4, 3): (0, 291),
    (4, 4): (157, 5_628),
    (4, 5): (153_408, 132_978),
    (5, 3): (942, 5_929),
    (5, 4): (153_408, 132_978),
    (5, 5): (33_749_811, 3_238_259),
}


ORDERED_PAIR_RESULTS = {
    (first_size, second_size): ordered_pair_orbits(first_size, second_size)
    for first_size in (3, 4, 5)
    for second_size in (3, 4, 5)
}
ORDERED_PAIR_ORBITS = {
    sizes: result[:2] for sizes, result in ORDERED_PAIR_RESULTS.items()
}
ORDERED_SHEAR_ORBITS = {
    sizes: result[2] for sizes, result in ORDERED_PAIR_RESULTS.items()
}
assert ORDERED_PAIR_ORBITS == EXPECTED_ORDERED_PAIR_ORBITS
assert all(
    ORDERED_SHEAR_ORBITS[first_size, second_size]
    == ORDERED_SHEAR_ORBITS[second_size, first_size]
    for first_size in (3, 4, 5)
    for second_size in (3, 4, 5)
)


# For equal support sizes, quotient ordered pairs by the coordinate swap too.
# Burnside for S_8 x C_2 has a swap term indexed only by the 22 conjugacy
# classes of S_8.  A pair fixed by (g, swap) has the form (A, gA), with
# g^2 A=A.
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
        for source, target in zip(cycle, cycle[1:] + cycle[:1]):
            permutation[source] = target
    return tuple(permutation)


def compose(left, right):
    return tuple(left[right[vertex]] for vertex in VERTICES)


def conjugacy_class_size(parts):
    denominator = 1
    for length, multiplicity in Counter(parts).items():
        denominator *= length**multiplicity * factorial(multiplicity)
    return factorial(8) // denominator


CONJUGACY_CLASSES = []
for cycle_type in integer_partitions(8):
    permutation = permutation_of_cycle_type(cycle_type)
    square = compose(permutation, permutation)
    CONJUGACY_CLASSES.append(
        (
            conjugacy_class_size(cycle_type),
            PERMUTATION_INDEX[permutation],
            PERMUTATION_INDEX[square],
        )
    )
assert len(CONJUGACY_CLASSES) == 22
assert sum(size for size, _, _ in CONJUGACY_CLASSES) == factorial(8)


def swap_burnside_term(circuit_size):
    no_common_light = 0
    jointly_omitting = 0
    shear_rigid = 0
    supports = SUPPORTS[circuit_size]
    for class_size, permutation_index, square_index in CONJUGACY_CLASSES:
        if square_index == 0:
            square_fixed = supports
        else:
            square_fixed = (
                support
                for support in invariant_support_masks(square_index, circuit_size)
                if support in supports
            )
        no_light_fixed = 0
        omitted_fixed = 0
        shear_fixed = 0
        edge_map = EDGE_MAPS[permutation_index]
        for first in square_fixed:
            second = transform_support(first, edge_map)
            first_heavy, first_omitted = degree_masks(first)
            second_heavy, second_omitted = degree_masks(second)
            no_light_fixed += (
                first_heavy | second_heavy
            ) == FULL_VERTEX_MASK
            omitted_fixed += bool(first_omitted & second_omitted)
            shear_fixed += not (
                shear_defect_mask(first) & shear_defect_mask(second)
            )
        no_common_light += class_size * no_light_fixed
        jointly_omitting += class_size * omitted_fixed
        shear_rigid += class_size * shear_fixed

    assert no_common_light % factorial(8) == 0
    assert jointly_omitting % factorial(8) == 0
    assert shear_rigid % factorial(8) == 0
    return (
        no_common_light // factorial(8),
        jointly_omitting // factorial(8),
        shear_rigid // factorial(8),
    )


EXPECTED_UNORDERED_PAIR_ORBITS = {
    (3, 3): (0, 19),
    (3, 4): (0, 291),
    (3, 5): (942, 5_929),
    (4, 4): (85, 2_939),
    (4, 5): (153_408, 132_978),
    (5, 5): (16_879_909, 1_622_096),
}
EXPECTED_UNORDERED_SHEAR_ORBITS = {
    (3, 3): 0,
    (3, 4): 0,
    (3, 5): 599,
    (4, 4): 73,
    (4, 5): 128_944,
    (5, 5): 15_392_537,
}


UNORDERED_PAIR_ORBITS = {}
UNORDERED_SHEAR_ORBITS = {}
for first_size in (3, 4, 5):
    for second_size in range(first_size, 6):
        if second_size not in (3, 4, 5):
            continue
        ordered = ORDERED_PAIR_ORBITS[first_size, second_size]
        if first_size != second_size:
            UNORDERED_PAIR_ORBITS[first_size, second_size] = ordered
            UNORDERED_SHEAR_ORBITS[first_size, second_size] = (
                ORDERED_SHEAR_ORBITS[first_size, second_size]
            )
            continue
        swap_term = swap_burnside_term(first_size)
        assert all((ordered[i] + swap_term[i]) % 2 == 0 for i in (0, 1))
        UNORDERED_PAIR_ORBITS[first_size, second_size] = tuple(
            (ordered[i] + swap_term[i]) // 2 for i in (0, 1)
        )
        assert (ORDERED_SHEAR_ORBITS[first_size, second_size] + swap_term[2]) % 2 == 0
        UNORDERED_SHEAR_ORBITS[first_size, second_size] = (
            ORDERED_SHEAR_ORBITS[first_size, second_size] + swap_term[2]
        ) // 2

assert UNORDERED_PAIR_ORBITS == EXPECTED_UNORDERED_PAIR_ORBITS
assert UNORDERED_SHEAR_ORBITS == EXPECTED_UNORDERED_SHEAR_ORBITS
assert sum(value[0] for value in UNORDERED_PAIR_ORBITS.values()) == 17_034_344
assert sum(value[1] for value in UNORDERED_PAIR_ORBITS.values()) == 1_764_252
assert sum(UNORDERED_SHEAR_ORBITS.values()) == 15_522_153


print(
    "PASS: generic circuit supports (labeled/S8 orbits) = "
    "3:560/1, 4:30240/6, 5:2021992/117"
)
print(
    "PASS: unordered no-common-light pair orbits = "
    "0,0,942,85,153408,16879909 (total 17034344)"
)
print(
    "PASS: unordered jointly-omitting pair orbits = "
    "19,291,5929,2939,132978,1622096 (total 1764252)"
)
print(
    "PASS: unordered shear-rigid pair orbits = "
    + ",".join(
        str(UNORDERED_SHEAR_ORBITS[sizes])
        for sizes in ((3, 3), (3, 4), (3, 5), (4, 4), (4, 5), (5, 5))
    )
    + " (total 15522153)"
)
print(
    "CAVEAT: coarse unsigned baseline only; positivity, extension compatibility, "
    "and minimum-union-degree-three pencil pruning are untested"
)
