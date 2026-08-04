#!/usr/bin/env python3
"""Exact signed pruning for generic derived circuits of sizes three and four.

This checker supplies the first signed layer missing from
``verify_circuit_support_orbits.py``.  It proves, using integer arithmetic and
finite incidence enumeration, that

* a generic three-support circuit can never be positive for a valid uniform
  single-element extension;
* only two of the six generic four-support orbits can be positive for a
  realizable extension;
* the 73 unsigned shear-rigid ``4+4`` support-pair orbits consequently reduce
  to 39 under this signed-incidence filter; and
* every one of those 39 types nevertheless fails the stronger pencil-rigid
  minimum-degree condition, so no generic ``4+4`` pair reaches the
  second-diagonal compactness calculation.

The row-2599 pattern-zero chart has an exact shear-rigid pair of positive
generic four-circuits for two independently realizable extension signatures.
This shows why the pencil condition, rather than shear rigidity alone, is the
decisive final incidence obstruction in size ``4+4``.

The final census applies the unit-cofactor XOR clauses to the eight prescribed
signatures in ``seeat_parent2599_shatter8.npz``.  It is a finite sample, not a
universal pruning percentage.  No floating point arithmetic, LP, SAT search,
or enumeration of the parent's 97,224 extension signatures is used.
"""

from collections import Counter
from itertools import combinations, permutations
from math import factorial
from pathlib import Path
import sys

import numpy as np

import prototype_koszul_circuits as koszul


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "seeat_parent2599_shatter8.npz"
TRIPLES = koszul.TRIPLES
TRIPLE_INDEX = koszul.TRIPLE_INDEX
VERTICES = tuple(range(1, 9))

# A four-support with common hub is encoded by its four-edge graph on the
# other seven labels.  Components are recorded as (vertices, edges).
C3_P2 = ((2, 1), (3, 3))
C4 = ((4, 4),)
P5 = ((5, 4),)
P4_P2 = ((2, 1), (4, 3))
TWO_P3 = ((3, 2), (3, 2))
P3_TWO_P2 = ((2, 1), (2, 1), (3, 2))
GRAPH_NAMES = {
    C3_P2: "C3+P2",
    C4: "C4",
    P5: "P5",
    P4_P2: "P4+P2",
    TWO_P3: "2P3",
    P3_TWO_P2: "P3+2P2",
}
EXPECTED_GRAPH_COUNTS = {
    C3_P2: 1_680,
    C4: 840,
    P5: 10_080,
    P4_P2: 10_080,
    TWO_P3: 5_040,
    P3_TWO_P2: 2_520,
}
SURVIVING_TYPES = {P4_P2, P3_TWO_P2}


def sign(value):
    if not value:
        raise AssertionError("unexpected zero")
    return 1 if value > 0 else -1


def inversion_sign(sequence):
    inversions = sum(
        sequence[i] > sequence[j]
        for i in range(len(sequence))
        for j in range(i + 1, len(sequence))
    )
    return -1 if inversions & 1 else 1


def bracket(matrix, sequence):
    """Alternating bracket for an ordered sequence of four labels."""
    ordered = tuple(sorted(sequence))
    columns = matrix[:, np.asarray(ordered) - 1]
    return inversion_sign(sequence) * koszul.determinant(columns.tolist())


def oriented_normal(normals, sequence):
    """The normal representing det(y_i,y_j,y_k,-) in the given order."""
    ordered = tuple(sorted(sequence))
    parity = inversion_sign(sequence)
    return tuple(parity * value for value in normals[TRIPLE_INDEX[ordered]])


def determinant_columns(columns):
    return koszul.determinant(
        [[int(column[row]) for column in columns] for row in range(4)]
    )


def generic_four_data(support):
    triples = [set(TRIPLES[index]) for index in support]
    common = set.intersection(*triples)
    if len(common) != 1:
        return None
    if any(
        len(triples[i] & triples[j] & triples[k]) >= 2
        for i, j, k in combinations(range(4), 3)
    ):
        return None

    hub = next(iter(common))
    edges = tuple(
        tuple(label for label in TRIPLES[index] if label != hub)
        for index in support
    )
    adjacency = {label: set() for edge in edges for label in edge}
    for first, second in edges:
        adjacency[first].add(second)
        adjacency[second].add(first)

    components = []
    remaining = set(adjacency)
    while remaining:
        stack = [next(iter(remaining))]
        component = set()
        while stack:
            vertex = stack.pop()
            if vertex in component:
                continue
            component.add(vertex)
            stack.extend(adjacency[vertex] - component)
        remaining.difference_update(component)
        components.append(
            (
                len(component),
                sum(len(adjacency[vertex]) for vertex in component) // 2,
            )
        )
    graph_type = tuple(sorted(components))
    if graph_type not in GRAPH_NAMES:
        raise AssertionError(f"unknown four-edge graph type {graph_type}")
    return hub, edges, graph_type


def matching_cofactor(edges, omitted):
    """Whether the other three graph edges form a matching on six labels."""
    labels = {
        label
        for index, edge in enumerate(edges)
        if index != omitted
        for label in edge
    }
    return len(labels) == 6


def shear_defect(support):
    """Bit mask of ordered pairs (e,f) fixed by all e-incident triples."""
    triples = [set(TRIPLES[index]) for index in support]
    result = 0
    bit = 0
    for vertex in VERTICES:
        incident = [triple for triple in triples if vertex in triple]
        for partner in VERTICES:
            if partner == vertex:
                continue
            if all(partner in triple for triple in incident):
                result |= 1 << bit
            bit += 1
    return result


def shear_rigid(first, second):
    return not (shear_defect(first) & shear_defect(second))


def union_degrees(first, second):
    degrees = [0] * 8
    for index in first | second:
        for vertex in TRIPLES[index]:
            degrees[vertex - 1] += 1
    return tuple(degrees)


def pencil_rigid(first, second):
    return shear_rigid(first, second) and min(union_degrees(first, second)) >= 3


def transform_support(support, edge_map):
    return frozenset(edge_map[index] for index in support)


def integer_partitions(total, maximum=None):
    if total == 0:
        yield ()
        return
    maximum = total if maximum is None else min(total, maximum)
    for first in range(maximum, 0, -1):
        for rest in integer_partitions(total - first, first):
            yield (first,) + rest


def permutation_of_cycle_type(parts):
    permutation = list(range(8))
    start = 0
    for length in parts:
        cycle = list(range(start, start + length))
        start += length
        for source, target in zip(cycle, cycle[1:] + cycle[:1]):
            permutation[source] = target
    return tuple(permutation)


def compose(left, right):
    return tuple(left[right[vertex]] for vertex in range(8))


def conjugacy_class_size(parts):
    denominator = 1
    for length, multiplicity in Counter(parts).items():
        denominator *= length**multiplicity * factorial(multiplicity)
    return factorial(8) // denominator


def parent_signs(matrix):
    return tuple(
        sign(koszul.determinant(matrix[:, np.asarray(basis) - 1].tolist()))
        for basis in combinations(VERTICES, 4)
    )


def signed_normal_columns(normals, signature, support):
    return [
        tuple(
            value if (signature >> index) & 1 else -value
            for value in normals[index]
        )
        for index in support
    ]


def check_strict_extension(matrix, point, signature):
    normals = koszul.parent_normals(matrix)
    for index, normal in enumerate(normals):
        value = sum(int(left) * int(right) for left, right in zip(normal, point))
        if sign(value) != (1 if (signature >> index) & 1 else -1):
            raise AssertionError("stored point has the wrong extension sign")


def pair_count(first, second):
    """Ordered labeled shear-rigid pairs, using defect-mask multiplicities."""
    counter = Counter(defect for defect, *_ in second)
    return sum(
        count
        for defect, *_ in first
        for other, count in counter.items()
        if not defect & other
    )


def main():
    certificate = np.load(CERTIFICATE, allow_pickle=False)
    if int(certificate["parent_index"].item()) != 2599:
        raise AssertionError("wrong parent")
    matrix = certificate["pattern_chart"][0]
    normals = koszul.parent_normals(matrix)
    signatures = [int(value) for value in certificate["signature"]]

    # The common-pair syzygy is exactly the forbidden GP-sign pattern for a
    # single-element extension.  Check all 28*C(6,3)=560 labeled supports in
    # exact arithmetic on the certificate chart; the displayed identity in
    # ATLAS_HELLY.md proves it polynomially for every chart.
    size_three = 0
    for first, second in combinations(VERTICES, 2):
        others = [value for value in VERTICES if value not in (first, second)]
        for third, fourth, fifth in combinations(others, 3):
            vectors = (
                oriented_normal(normals, (first, second, third)),
                oriented_normal(normals, (first, second, fourth)),
                oriented_normal(normals, (first, second, fifth)),
            )
            coefficients = (
                bracket(matrix, (first, second, fourth, fifth)),
                -bracket(matrix, (first, second, third, fifth)),
                bracket(matrix, (first, second, third, fourth)),
            )
            if any(
                sum(coefficients[i] * vectors[i][row] for i in range(3))
                for row in range(4)
            ):
                raise AssertionError("common-pair syzygy failed")

            # For any proposed signs s_c,s_d,s_e, the signed circuit aligns
            # iff the three GP terms T3,T2,T1 all have one sign.  The uniform
            # chirotope axiom excludes exactly those two of eight patterns.
            bad_patterns = 0
            coefficient_signs = tuple(sign(value) for value in coefficients)
            for local_bits in range(8):
                products = tuple(
                    coefficient_signs[i]
                    * (1 if (local_bits >> i) & 1 else -1)
                    for i in range(3)
                )
                bad_patterns += len(set(products)) == 1
            if bad_patterns != 2:
                raise AssertionError("GP/circuit sign correspondence failed")
            size_three += 1
    if size_three != 560:
        raise AssertionError(f"got {size_three} size-three supports")
    print("PASS: all 560 generic size-three supports are GP-forbidden")

    # Enumerate every generic structural four-circuit and classify each
    # anchored cofactor.  A residual occurs exactly when the other three
    # graph edges form a matching; all other nonzero cofactors are units in
    # the localization at the parent brackets.
    supports_by_type = {graph_type: set() for graph_type in GRAPH_NAMES}
    four_data = []
    for support_tuple in combinations(range(len(TRIPLES)), 4):
        data = generic_four_data(support_tuple)
        if data is None:
            continue
        hub, edges, graph_type = data
        support = frozenset(support_tuple)
        supports_by_type[graph_type].add(support)
        anchor = next(
            index for index, triple in enumerate(TRIPLES) if hub not in triple
        )
        residual_indices = set()
        for omitted in range(4):
            four_set = tuple(
                support_tuple[index] for index in range(4) if index != omitted
            ) + (anchor,)
            orbit = koszul.wall_orbit(four_set)
            if orbit in koszul.ZERO:
                raise AssertionError("minimal four-circuit has a zero cofactor")
            is_residual = orbit in koszul.RESIDUAL
            is_matching = matching_cofactor(edges, omitted)
            if is_residual != is_matching:
                raise AssertionError("wall classification disagrees with localization")
            if is_residual:
                residual_indices.add(omitted)
        expected_residuals = {
            C3_P2: 0,
            C4: 0,
            P5: 0,
            P4_P2: 1,
            TWO_P3: 0,
            P3_TWO_P2: 2,
        }[graph_type]
        if len(residual_indices) != expected_residuals:
            raise AssertionError("wrong number of localization cofactors")
        four_data.append(
            (support_tuple, support, hub, edges, graph_type, residual_indices)
        )

    graph_counts = {
        graph_type: len(supports) for graph_type, supports in supports_by_type.items()
    }
    if graph_counts != EXPECTED_GRAPH_COUNTS or len(four_data) != 30_240:
        raise AssertionError(f"wrong four-support census: {graph_counts}")
    print(
        "PASS: 30,240 generic four-supports -> "
        "17,640 fixed-circuit + 12,600 localization-variable"
    )

    # Burnside/stabilizer calculation for the surviving support types.
    permutations8 = tuple(permutations(range(8)))
    edge_maps = tuple(
        tuple(
            TRIPLE_INDEX[tuple(sorted(permutation[label - 1] + 1 for label in triple))]
            for triple in TRIPLES
        )
        for permutation in permutations8
    )
    representatives = {
        graph_type: min(supports_by_type[graph_type])
        for graph_type in SURVIVING_TYPES
    }
    ordered_counts = {}
    for first_type in (P4_P2, P3_TWO_P2):
        first = representatives[first_type]
        stabilizer = tuple(
            edge_map
            for edge_map in edge_maps
            if transform_support(first, edge_map) == first
        )
        for second_type in (P4_P2, P3_TWO_P2):
            candidates = {
                support
                for support in supports_by_type[second_type]
                if shear_rigid(first, support)
            }
            number_orbits = 0
            while candidates:
                second = candidates.pop()
                candidates.difference_update(
                    transform_support(second, edge_map) for edge_map in stabilizer
                )
                number_orbits += 1
            ordered_counts[first_type, second_type] = number_orbits
    expected_ordered = {
        (P4_P2, P4_P2): 30,
        (P4_P2, P3_TWO_P2): 13,
        (P3_TWO_P2, P4_P2): 13,
        (P3_TWO_P2, P3_TWO_P2): 7,
    }
    if ordered_counts != expected_ordered:
        raise AssertionError(f"wrong ordered orbit counts {ordered_counts}")

    swap_terms = {}
    for graph_type in (P4_P2, P3_TWO_P2):
        supports = supports_by_type[graph_type]
        numerator = 0
        for parts in integer_partitions(8):
            permutation = permutation_of_cycle_type(parts)
            square = compose(permutation, permutation)
            edge_map = tuple(
                TRIPLE_INDEX[
                    tuple(sorted(permutation[label - 1] + 1 for label in triple))
                ]
                for triple in TRIPLES
            )
            square_map = tuple(
                TRIPLE_INDEX[
                    tuple(sorted(square[label - 1] + 1 for label in triple))
                ]
                for triple in TRIPLES
            )
            fixed = sum(
                transform_support(support, square_map) == support
                and shear_rigid(support, transform_support(support, edge_map))
                for support in supports
            )
            numerator += conjugacy_class_size(parts) * fixed
        if numerator % factorial(8):
            raise AssertionError("nonintegral swap Burnside term")
        swap_terms[graph_type] = numerator // factorial(8)
    if swap_terms != {P4_P2: 10, P3_TWO_P2: 5}:
        raise AssertionError(f"wrong swap terms {swap_terms}")
    unordered = {
        "AA": (ordered_counts[P4_P2, P4_P2] + swap_terms[P4_P2]) // 2,
        "AB": ordered_counts[P4_P2, P3_TWO_P2],
        "BB": (
            ordered_counts[P3_TWO_P2, P3_TWO_P2]
            + swap_terms[P3_TWO_P2]
        )
        // 2,
    }
    if unordered != {"AA": 20, "AB": 13, "BB": 6}:
        raise AssertionError(f"wrong unordered orbit counts {unordered}")
    print("PASS: signed structural filter reduces shear-rigid 4+4 orbits 73 -> 39")

    # Each structural four-support has a hub in all four triples.  The union
    # of two such supports has at most eight triples, hence total incidence at
    # most 24.  Minimum union degree three would force total incidence at
    # least 8*3=24 and therefore every degree to equal three, contradicting
    # the degree-four hub.  The census has already checked the hypotheses for
    # all 30,240 supports; the following representative-level check guards
    # the implementation of the pencil predicate as well.
    for first_type in SURVIVING_TYPES:
        first = representatives[first_type]
        if any(
            pencil_rigid(first, second)
            for second_type in SURVIVING_TYPES
            for second in supports_by_type[second_type]
        ):
            raise AssertionError("a structural 4+4 pair passed pencil rigidity")
    print("PASS: the pencil minimum-degree argument kills all generic 4+4 pairs")

    # Exact surviving B+B pair on the pattern-zero row-2599 chart.
    survivor_specs = (
        (1, ("145", "356", "157", "258"),
         (221_601_476_670, 380_827_220_000, 90_848_922_285, 319_059_375_744)),
        (2, ("124", "345", "347", "468"),
         (22_119_895_128, 82_096_061_557, 5_377_382_637, 57_911_448_192)),
    )
    survivor_supports = []
    for signature_index, labels, expected_coefficients in survivor_specs:
        support = tuple(
            TRIPLE_INDEX[tuple(int(value) for value in label)] for label in labels
        )
        data = generic_four_data(support)
        if data is None or data[2] != P3_TWO_P2:
            raise AssertionError("survivor is not a generic B-type support")
        signed_columns = signed_normal_columns(
            normals, signatures[signature_index], support
        )
        rank, coefficients = koszul.circuit_cofactors(signed_columns)
        if rank != 3 or tuple(coefficients) != expected_coefficients:
            raise AssertionError("wrong exact positive-circuit coefficients")
        survivor_supports.append(frozenset(support))
    if not shear_rigid(*survivor_supports):
        raise AssertionError("exact surviving pair is not shear-rigid")
    if pencil_rigid(*survivor_supports):
        raise AssertionError("the shear-rigid witness unexpectedly passed the pencil test")

    # The same certificate gives an exact realization of each prescribed
    # signature on a different chart.  Recheck it here rather than relying on
    # the extension catalog or its 97,224-signature enumeration.
    zero_parent_signs = parent_signs(matrix)
    for signature_index, *_ in survivor_specs:
        pattern = 1 << signature_index
        feasible_matrix = certificate["pattern_chart"][pattern]
        if parent_signs(feasible_matrix) != zero_parent_signs:
            raise AssertionError("feasible chart changed the parent chirotope")
        point = [
            int(value) for value in certificate["feasible_point"][pattern, signature_index]
        ]
        check_strict_extension(
            feasible_matrix, point, signatures[signature_index]
        )
    print("PASS: exact row-2599 chart has a realizable shear-rigid B+B survivor")

    # Apply only the unit-cofactor XOR equations to the eight stored
    # signatures.  A matching cofactor is left as a free localization atom;
    # consequently these are sound rejection counts, not feasibility counts.
    candidate_records = []
    for support_tuple, support, hub, edges, graph_type, residual_indices in four_data:
        if graph_type not in SURVIVING_TYPES:
            continue
        anchor = next(
            index for index, triple in enumerate(TRIPLES) if hub not in triple
        )
        coefficient_signs = []
        for omitted in range(4):
            columns = [
                normals[support_tuple[index]]
                for index in range(4)
                if index != omitted
            ] + [normals[anchor]]
            coefficient_signs.append(
                sign(((-1) ** omitted) * determinant_columns(columns))
            )
        candidate_records.append(
            (
                shear_defect(support),
                support_tuple,
                graph_type,
                frozenset(residual_indices),
                tuple(coefficient_signs),
            )
        )

    eligible = []
    for signature in signatures:
        records = []
        for defect, support, graph_type, residual_indices, coefficient_signs in candidate_records:
            unit_products = {
                coefficient_signs[index]
                * (1 if (signature >> support[index]) & 1 else -1)
                for index in range(4)
                if index not in residual_indices
            }
            if len(unit_products) == 1:
                records.append((defect, support, graph_type))
        eligible.append(records)
    eligible_counts = tuple(len(records) for records in eligible)
    if eligible_counts != (2_184, 2_190, 2_260, 2_270, 2_204, 2_196, 2_220, 2_226):
        raise AssertionError(f"wrong unit-XOR support counts {eligible_counts}")

    all_records = [(record[0],) for record in candidate_records]
    unsigned_allowed_pairs = pair_count(all_records, all_records)
    if unsigned_allowed_pairs != 2_429_280:
        raise AssertionError("wrong labeled allowed-type pair count")
    signed_pair_counts = tuple(
        pair_count(eligible[first], eligible[second])
        for first, second in combinations(range(8), 2)
    )
    expected_signed_pair_counts = (
        105_224, 107_760, 108_992, 105_962, 105_206, 106_618, 106_082,
        107_726, 108_942, 106_094, 105_726, 107_272, 106_294,
        111_232, 109_280, 108_078, 109_474, 109_942,
        109_590, 108_710, 110_170, 110_910,
        106_058, 107_390, 107_522,
        106_910, 107_000,
        107_588,
    )
    if signed_pair_counts != expected_signed_pair_counts:
        raise AssertionError("wrong row-2599 signed pair census")
    print(
        "PASS (row-2599 sample): unit-XOR filter leaves "
        f"{min(signed_pair_counts):,}..{max(signed_pair_counts):,} of "
        f"{unsigned_allowed_pairs:,} labeled allowed-type pairs"
    )
    print("THEOREM: generic 3+5 is empty and every generic 4+4 pair is pencil-flexible")
    print("CAVEAT: the row-2599 pruning percentage is a finite prescribed-signature sample")


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    main()
