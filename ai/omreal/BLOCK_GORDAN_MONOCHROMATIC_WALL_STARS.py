#!/usr/bin/env python3
"""Exact monochromatic residual-wall stars and row-2599 support tests.

For every residual orbit type this verifier gives an exact uniform rational
parent on the representative wall, two same-parent-cell transverse samples,
and one extension signature which is feasible on the negative side but has
the positive wall circuit.  Every fixed-unit auxiliary circuit is positive
on the bad side and absent on the feasible side.  All other one-auxiliary
supports are checked too; none is positive on the feasible side.

At the exact row-2599 transverse node, the verifier then performs a stronger
unsigned support census.  For one 65-occurrence branch it forms every
possible support P+u, including every non-unit auxiliary.  Every union of two
such supports has a known pencil/common-apex escape.  A displayed triple of
actual positive unit circuits is nevertheless pencil-rigid.  Thus this local
node removes no global triple-component obstruction.
"""

from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import lcm
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import BLOCK_GORDAN_RESIDUAL_ELIMINATION_CELLS as elimination  # noqa: E402
import BLOCK_GORDAN_RESIDUAL_MUTATION_MAP_NO_GO as mutation  # noqa: E402
import DIAG9_GRAPH_exact_topes as topes  # noqa: E402
import DIAG9_GRAPH_verify_row2599_node as node  # noqa: E402
import prototype_koszul_circuits as koszul  # noqa: E402


DELTA = Fraction(1, 1_000_000)

# Exact wall values (a,b,c,d,e,f,g,h,i) in the standard projective frame.
WALL_VALUES = {
    36: ("29/2", "2", "12", "10", "18", "8", "11", "23", "3"),
    37: ("-69", "20", "25", "29", "9", "7", "20", "26", "27"),
    38: ("3643/58", "17", "23", "16", "28", "22", "29", "10", "12"),
    39: ("-179", "24", "7", "20", "28", "11", "8", "18", "23"),
    41: ("231/23", "9", "14", "17", "24", "4", "23", "29", "11"),
    42: ("-1669/5", "24", "19", "24", "22", "16", "23", "17", "8"),
    44: ("25", "14", "23", "298/143", "2", "3", "24", "22", "9"),
    46: ("601/13", "27", "25", "27", "17", "13", "26", "29", "8"),
    47: ("-6", "3", "6", "14", "26", "8", "18", "22", "7"),
    48: ("-35", "3", "19", "22", "25", "21", "2", "11", "4"),
    49: ("5", "2", "26", "-14", "10", "16", "2", "27", "15"),
    50: ("16", "3", "7", "223/21", "28", "20", "11", "19", "21"),
    51: ("2", "22", "7", "25", "2", "-77/5", "13", "17", "6"),
}

PIVOT = {
    36: 0, 37: 0, 38: 0, 39: 0, 41: 0, 42: 0, 44: 3,
    46: 0, 47: 0, 48: 0, 49: 3, 50: 3, 51: 5,
}

# A strict extension witness on the negative side, and its exact sign bitset.
SIGNATURE = {
    36: 38373577122343460,
    37: 60045011436556087,
    38: 64407817740176164,
    39: 15985151365428698,
    41: 68772874607741220,
    42: 3189265163799333,
    44: 5498873177414252,
    46: 19820796010354139,
    47: 55860786667096613,
    48: 7693931016784421,
    49: 65537016483490341,
    50: 43676374293845338,
    51: 55673146004813147,
}

WITNESS = {
    36: (
        656101117801248079170349665700009,
        656102430003445206500007845599376,
        656101215002084405127201107199936,
        -34200155600165899993,
    ),
    37: (325542677067972042627000141, 325542685415220149565000504, -546000025, 10),
    38: (95815334455810087279983296, 95815410238462424465440749, 2939906672160013601, -112352111273),
    39: (-9779738725219666248537560960695229394, -303171900481809653702203358998350892304, -168818163701744470601623180653453128041, -2461030783201219873),
    41: (184342344368014156, 56104191764179162, 1300, -5019),
    42: (5544764646862845651735, 108677387078511774776853, 4605, 3185),
    44: (-13549705051033430412474560, 1231786187509096491476269, 2565323186912, -11609047170362),
    46: (-26495400060243599730001922, -793303588226703917929698809, -793303448862588139086086038, 3050946112487),
    47: (97029934303503775200105, 4463376977961170016005105, 4463376707453505045600184, 910799398),
    48: (23808558784046450252400329399998, 71425677674837060398803897000021, 71425676352139368253201582200001, 291599807399996),
    49: (486000097200005580000095999999, 972000226800017460000531000006, 972000194400013860000312000001, 179999930999997),
    50: (-7679999042814141521680882, -23039835848532604867468962, -23039997125604442267975173, -183957381289240),
    51: (-10754022069463697009999959, -169375840992812458468801769, -169375850594617214016004043, 3175204158),
}

EXPECTED_CERTIFIED = {
    36: 12, 37: 14, 38: 2, 39: 12, 41: 14, 42: 2, 44: 12,
    46: 12, 47: 12, 48: 16, 49: 8, 50: 3, 51: 4,
}

TRIPLE_SIGNATURE_SUPPORTS = (
    (68231279848521727, (0, 19, 34, 37, 40)),
    (62614156573450111, (0, 18, 47, 48, 53)),
    (40418078342512640, (4, 5, 18, 20, 40)),
)
EXPECTED_TRIPLE_DEGREE = (4, 4, 6, 4, 5, 5, 3, 5)


def residual(kind, values):
    a, b, c, d, e, f, g, h, i = values
    formulas = {
        36: a*f-c*d+c-f,
        37: a*e-a*f-b*d+b+c*d-c-e+f,
        38: a*e*i-a*f*h-b*d*i+b*f*g-b*f+b*i+c*d*h-c*e*g+c*e-c*h-e*i+f*h,
        39: a*f-a*i-c*d*i+c*f*g-c*f+c*i+d*i-f*g,
        41: a*e-a-c*d+c+d-e,
        42: a*e-a*h-c*d*h+c*e*g-c*e+c*h+d*h-e*g,
        44: a*e*i-a*e-a*f*h+a*f+a*h-a*i+c*d*h-c*d*i-c*e*g+c*e+c*f*g-c*f-c*h+c*i-d*h+d*i+e*g-e*i-f*g+f*h,
        46: a*f-b*f-c*d+c*e,
        47: a*f-b*f-c*d+c*e,
        48: a+b*c-b-c,
        49: b*f-b+d-f,
        50: b*f-b*i+d*i-f*g,
        51: a*b*f-a*c*e+a*c*h-a*f*h-b*b*f+b*c*e-b*c*g+b*f*h+c*e*g-c*e*h,
    }
    return formulas[kind]


def integer_parent(values):
    a, b, c, d, e, f, g, h, i = values
    matrix = [
        [1, 0, 0, 0, 1, 1, 1, 1],
        [0, 1, 0, 0, 1, a, d, g],
        [0, 0, 1, 0, 1, b, e, h],
        [0, 0, 0, 1, 1, c, f, i],
    ]
    for column in range(8):
        denominator = 1
        for row in range(4):
            denominator = lcm(
                denominator, Fraction(matrix[row][column]).denominator
            )
        for row in range(4):
            matrix[row][column] = int(
                Fraction(matrix[row][column]) * denominator
            )
    return np.asarray(matrix, dtype=object)


def signed_columns(normals, signature, support):
    return tuple(
        tuple(
            (1 if signature & (1 << index) else -1) * coordinate
            for coordinate in normals[index]
        )
        for index in support
    )


def positive_circuit(normals, signature, support):
    columns = signed_columns(normals, signature, support)
    if koszul.matrix_rank(columns) != len(support) - 1:
        return False
    kernel = koszul.nullspace([list(row) for row in zip(*columns, strict=True)])
    return len(kernel) == 1 and (
        all(value > 0 for value in kernel[0])
        or all(value < 0 for value in kernel[0])
    )


def wall_circuit(kind):
    if kind in mutation.ORDINARY_TYPES:
        return tuple(mutation.REPRESENTATIVES[kind])
    return mutation.indices(mutation.LOCALIZATION_CERTIFICATES[kind][0])


def certified_auxiliaries(kind, circuit):
    if kind in mutation.ORDINARY_TYPES:
        return elimination.ordinary_auxiliaries(circuit)
    return elimination.localization_auxiliaries(kind)


def verify_strict_witness(normals, signature, witness):
    for index, normal in enumerate(normals):
        value = sum(x * y for x, y in zip(normal, witness, strict=True))
        prescribed = 1 if signature & (1 << index) else -1
        if prescribed * value <= 0:
            raise AssertionError("stored extension witness is not strict")


def verify_all_thirteen_examples():
    all_auxiliary_counts = {}
    for kind in sorted(WALL_VALUES):
        values = tuple(Fraction(value) for value in WALL_VALUES[kind])
        if residual(kind, values) != 0:
            raise AssertionError(f"type {kind} point misses its residual wall")
        negative_values = list(values)
        positive_values = list(values)
        negative_values[PIVOT[kind]] -= DELTA
        positive_values[PIVOT[kind]] += DELTA
        wall_parent = integer_parent(values)
        negative_parent = integer_parent(negative_values)
        positive_parent = integer_parent(positive_values)
        signs = topes.parent_signs(wall_parent)
        if topes.parent_signs(negative_parent) != signs or topes.parent_signs(positive_parent) != signs:
            raise AssertionError(f"type {kind} transverse samples leave the parent cell")

        wall_normals = topes.derived_rows(wall_parent, normalize=False)
        negative_normals = topes.derived_rows(negative_parent, normalize=False)
        positive_normals = topes.derived_rows(positive_parent, normalize=False)
        signature = SIGNATURE[kind]
        verify_strict_witness(negative_normals, signature, WITNESS[kind])
        circuit = wall_circuit(kind)
        if not positive_circuit(wall_normals, signature, circuit):
            raise AssertionError(f"type {kind} lacks its positive wall circuit")

        certified = certified_auxiliaries(kind, circuit)
        if len(certified) != EXPECTED_CERTIFIED[kind]:
            raise AssertionError(f"type {kind} certified count changed")
        for auxiliary in certified:
            support = tuple(sorted(circuit + (auxiliary,)))
            if positive_circuit(negative_normals, signature, support):
                raise AssertionError("certified circuit appears on the feasible side")
            if not positive_circuit(positive_normals, signature, support):
                raise AssertionError("certified circuit is missing on the bad side")

        bad_auxiliaries = 0
        feasible_auxiliaries = 0
        for auxiliary in range(56):
            if auxiliary in circuit:
                continue
            support = tuple(sorted(circuit + (auxiliary,)))
            bad_auxiliaries += positive_circuit(
                positive_normals, signature, support
            )
            feasible_auxiliaries += positive_circuit(
                negative_normals, signature, support
            )
        if feasible_auxiliaries:
            raise AssertionError("a non-unit auxiliary survives on the feasible side")
        all_auxiliary_counts[kind] = bad_auxiliaries
    return all_auxiliary_counts


def node_wall_circuit(fourset, node_normals):
    kind = koszul.wall_orbit(tuple(sorted(fourset)))
    if kind in mutation.ORDINARY_TYPES:
        return tuple(fourset)
    rank_two = tuple(
        support
        for support in combinations(fourset, 3)
        if koszul.matrix_rank([node_normals[index] for index in support]) == 2
    )
    if len(rank_two) != 1:
        raise AssertionError("localization occurrence has no unique wall circuit")
    return tuple(rank_two[0])


def is_certified_occurrence_support(occurrence, circuit, support):
    if not set(circuit) < set(support) or len(support) != len(circuit) + 1:
        return False
    auxiliary = next(iter(set(support) - set(circuit)))
    kind = koszul.wall_orbit(tuple(sorted(occurrence)))
    if kind in mutation.ORDINARY_TYPES:
        return all(
            koszul.orbit_kind(
                mutation.orbit(
                    circuit[:omitted]
                    + circuit[omitted + 1 :]
                    + (auxiliary,)
                )
            )
            == "unit"
            for omitted in range(4)
        )
    residual_auxiliary = next(index for index in occurrence if index not in circuit)
    return (
        koszul.orbit_kind(mutation.orbit(circuit + (auxiliary,))) == "zero"
        and all(
            koszul.orbit_kind(
                mutation.orbit(
                    circuit[:omitted]
                    + circuit[omitted + 1 :]
                    + (residual_auxiliary, auxiliary)
                )
            )
            == "unit"
            for omitted in range(3)
        )
    )


def support_degree(support):
    degree = [0] * 8
    for normal in support:
        for label in koszul.TRIPLES[normal]:
            degree[label - 1] += 1
    return tuple(degree)


def has_known_escape(support):
    triples = tuple(set(koszul.TRIPLES[index]) for index in support)
    for label in range(1, 9):
        incident = tuple(triple for triple in triples if label in triple)
        if len(incident) <= 2:
            return True
        if set.intersection(*(triple - {label} for triple in incident)):
            return True
    return False


def verify_all_representative_same_wall_pairs():
    counts = {}
    for kind in sorted(koszul.RESIDUAL):
        circuit = wall_circuit(kind)
        auxiliaries = tuple(index for index in range(56) if index not in circuit)
        tested = 0
        for first, second in combinations(auxiliaries, 2):
            support = set(circuit + (first, second))
            # The stronger conclusion holds: degree <=2 already, without
            # invoking the common-apex alternative.
            if min(support_degree(support)) > 2:
                raise AssertionError(
                    f"type {kind} has a same-wall pair without a light label"
                )
            tested += 1
        expected = 1_326 if len(circuit) == 4 else 1_378
        if tested != expected:
            raise AssertionError("wrong same-wall auxiliary-pair count")
        counts[kind] = tested
    return counts


def verify_row2599_pair_and_triple():
    certificate = np.load(node.ROADMAP, allow_pickle=False)
    offsets = tuple(map(int, certificate["branch_offset"]))
    occurrences = tuple(
        tuple(map(int, row))
        for row in certificate["branch_fourset"][offsets[0] : offsets[1]]
    )
    node_parent = node.rational_parent(Fraction(0), Fraction(0))
    node_normals = topes.derived_rows(node_parent, normalize=False)

    possible_supports = set()
    for occurrence in occurrences:
        circuit = node_wall_circuit(occurrence, node_normals)
        for auxiliary in range(56):
            if auxiliary not in circuit:
                possible_supports.add(tuple(sorted(circuit + (auxiliary,))))
    if len(possible_supports) != 1_553 or Counter(map(len, possible_supports)) != Counter({5: 1500, 4: 53}):
        raise AssertionError("wrong all-auxiliary node support census")
    supports = tuple(possible_supports)
    for left_index, left in enumerate(supports):
        for right in supports[left_index + 1 :]:
            if not has_known_escape(set(left) | set(right)):
                raise AssertionError("row-2599 branch has a pencil-rigid pair")

    patterns = {
        int(signature): int(pattern)
        for signature, pattern in zip(
            certificate["signature"], certificate["signature_pattern"], strict=True
        )
    }
    bad_parent = node.rational_parent(*node.cell_points()[3])
    bad_normals = topes.derived_rows(bad_parent, normalize=False)
    union = set()
    for signature, support in TRIPLE_SIGNATURE_SUPPORTS:
        if patterns.get(signature) != 3:
            raise AssertionError("triple signature does not have the certified half-disk pattern")
        if not positive_circuit(bad_normals, signature, support):
            raise AssertionError("displayed triple support is not a strict positive circuit")
        if not any(
            is_certified_occurrence_support(
                occurrence,
                node_wall_circuit(occurrence, node_normals),
                support,
            )
            for occurrence in occurrences
        ):
            raise AssertionError("displayed triple support is not a certified unit padding")
        union.update(support)
    if support_degree(union) != EXPECTED_TRIPLE_DEGREE:
        raise AssertionError("wrong triple support degree")
    if has_known_escape(union):
        raise AssertionError("displayed triple unexpectedly has a known pencil escape")
    return len(possible_supports)


def main():
    counts = verify_all_thirteen_examples()
    pair_counts = verify_all_representative_same_wall_pairs()
    support_count = verify_row2599_pair_and_triple()
    print("PASS: exact uniform monochromatic wall-star example for all 13 types")
    print("PASS: certified auxiliary counts=" + str(EXPECTED_CERTIFIED))
    print("PASS: no unit or non-unit auxiliary circuit survives on a feasible side")
    print("PASS: bad-side all-auxiliary counts=" + str(counts))
    print("PASS: every all-13 same-wall pair has a degree-at-most-two label")
    print("PASS: same-wall pair counts=" + str(pair_counts))
    print(f"PASS: all pairs among {support_count:,} row-2599 supports have a known escape")
    print("PASS: exact proper three-block occurrence is pencil-rigid")
    print("NO-GO: persistent-circuit or pencil escape is not a universal trichotomy")
    print("SCOPE: the pair result is local; the triple E1 term remains open")


if __name__ == "__main__":
    main()
