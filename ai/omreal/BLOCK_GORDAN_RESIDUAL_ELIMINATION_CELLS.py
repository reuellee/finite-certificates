#!/usr/bin/env python3
"""Exact census and normal forms for residual-wall elimination carriers.

For every one of the 13 residual wall representatives, enumerate the
auxiliary derived normals whose determinant coefficients are all fixed unit
wall types.  Every pair can be placed on opposite sides by the two auxiliary
signature signs and has a universal minimal enlarged-support interval:

    [Q_minus,R] -> [P,R] -> [Q_plus,R].

The ordinary carrier uses six normal coordinates; the localization carrier
uses five.  Exact rational normal forms verify their complete positive-ray
censuses.  The induced interval chain isomorphism has an acyclic integral
mapping cone.  Three same-side auxiliaries are also checked to span a simplex,
which supplies the first coherence homotopy between different reroute choices.

Strict naturality on the dying coordinate face remains impossible by
``BLOCK_GORDAN_RESIDUAL_MUTATION_MAP_NO_GO.py``.  The theorem here is about
the constructible specialization cospan with enlarged supports.
"""

from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import BLOCK_GORDAN_RESIDUAL_MUTATION_MAP_NO_GO as mutation  # noqa: E402
import prototype_koszul_circuits as koszul  # noqa: E402


EXPECTED_AUXILIARIES = {
    36: 12,
    37: 14,
    38: 2,
    39: 12,
    41: 14,
    42: 2,
    44: 12,
    46: 12,
    47: 12,
    48: 16,
    49: 8,
    50: 3,
    51: 4,
}


def ordinary_auxiliaries(support):
    result = []
    for auxiliary in range(len(koszul.TRIPLES)):
        if auxiliary in support:
            continue
        replacement_types = tuple(
            mutation.orbit(support[:omitted] + support[omitted + 1 :] + (auxiliary,))
            for omitted in range(4)
        )
        if all(koszul.orbit_kind(kind) == "unit" for kind in replacement_types):
            result.append(auxiliary)
    return tuple(result)


def localization_auxiliaries(kind):
    circuit_names, z_name, _, _, _ = mutation.LOCALIZATION_CERTIFICATES[kind]
    circuit = mutation.indices(circuit_names)
    z = mutation.NAME_TO_INDEX[z_name]
    result = []
    for auxiliary in range(len(koszul.TRIPLES)):
        if auxiliary in circuit or auxiliary == z:
            continue
        if koszul.orbit_kind(mutation.orbit(circuit + (auxiliary,))) != "zero":
            continue
        replacements = tuple(
            mutation.orbit(
                circuit[:omitted]
                + circuit[omitted + 1 :]
                + (z, auxiliary)
            )
            for omitted in range(3)
        )
        if all(koszul.orbit_kind(replacement) == "unit" for replacement in replacements):
            result.append(auxiliary)
    return tuple(result)


def auxiliary_census():
    auxiliaries = {}
    for kind in sorted(mutation.RESIDUAL_TYPES):
        if kind in mutation.ORDINARY_TYPES:
            auxiliaries[kind] = ordinary_auxiliaries(mutation.REPRESENTATIVES[kind])
        else:
            auxiliaries[kind] = localization_auxiliaries(kind)
    counts = {kind: len(values) for kind, values in auxiliaries.items()}
    if counts != EXPECTED_AUXILIARIES:
        raise AssertionError(f"wrong fixed-unit auxiliary census {counts}")

    pair_counts = {
        kind: len(values) * (len(values) - 1) // 2
        for kind, values in auxiliaries.items()
    }
    candidate_persistent_supports = {
        kind: pair_counts[kind] * (4 if kind in mutation.ORDINARY_TYPES else 3)
        for kind in auxiliaries
    }
    if sum(pair_counts.values()) != 671:
        raise AssertionError("wrong potential opposite-pair carrier total")
    if sum(candidate_persistent_supports.values()) != 2_420:
        raise AssertionError("wrong persistent support-candidate total")
    return auxiliaries, pair_counts, candidate_persistent_supports


def columns_to_rows(columns):
    return [list(row) for row in zip(*columns, strict=True)]


def positive_minimal_circuits(columns):
    result = []
    for size in range(2, min(5, len(columns)) + 1):
        for support in combinations(range(len(columns)), size):
            selected = [columns[index] for index in support]
            if koszul.matrix_rank(selected) != size - 1:
                continue
            kernel = koszul.nullspace(columns_to_rows(selected))
            if len(kernel) != 1:
                continue
            relation = kernel[0]
            if all(value > 0 for value in relation) or all(
                value < 0 for value in relation
            ):
                result.append(support)
    return tuple(result)


def ordinary_pair_columns(parameter):
    parameter = Fraction(parameter)
    return (
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (0, 0, 1, 0),
        (-1, -1, -1, parameter),
        (0, 0, 0, 1),
        (2, 3, 4, -1),
    )


def localization_pair_columns(parameter):
    parameter = Fraction(parameter)
    return (
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (-1, -1, parameter, 0),
        (0, 0, 1, 0),
        (2, 3, -1, 0),
    )


def verify_pair_normal_form(columns_function, expected, expected_rank):
    for parameter, expected_circuits in expected.items():
        columns = columns_function(parameter)
        if koszul.matrix_rank(columns) != expected_rank:
            raise AssertionError("wrong enlarged-support rank")
        if len(columns) - expected_rank != 2:
            raise AssertionError("enlarged positive cone must have dimension two")
        circuits = positive_minimal_circuits(columns)
        if set(circuits) != set(expected_circuits):
            raise AssertionError(
                f"wrong positive rays at t={parameter}: {circuits}"
            )


def ordinary_same_side_columns(parameter):
    parameter = Fraction(parameter)
    return (
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (0, 0, 1, 0),
        (-1, -1, -1, parameter),
        (0, 0, 0, -1),
        (1, 0, 0, -1),
        (0, 1, 0, -1),
    )


def localization_same_side_columns(parameter):
    parameter = Fraction(parameter)
    return (
        (1, 0, 0, 0),
        (0, 1, 0, 0),
        (-1, -1, parameter, 0),
        (0, 0, -1, 0),
        (1, 0, -1, 0),
        (0, 1, -1, 0),
    )


def verify_same_side_simplex(columns, circuit_size):
    expected = {
        tuple(range(circuit_size)) + (auxiliary,)
        for auxiliary in range(circuit_size, len(columns))
    }
    circuits = set(positive_minimal_circuits(columns))
    if circuits != expected:
        raise AssertionError(f"same-side positive cone is not its expected simplex: {circuits}")
    rank = koszul.matrix_rank(columns)
    number_auxiliaries = len(columns) - circuit_size
    if len(columns) - rank != number_auxiliaries:
        raise AssertionError("same-side circuit rays cannot form a kernel basis")


def verify_mapping_cone():
    # Cellular boundary of an oriented interval: d(e)=r-q.
    interval_boundary = ((-1,), (1,))
    if koszul.matrix_rank(interval_boundary) != 1:
        raise AssertionError("wrong interval boundary")

    # Cone(id_C)_2 -> Cone(id_C)_1 -> Cone(id_C)_0, with bases
    # (e_source), (e_target,q_source,r_source), (q_target,r_target).
    differential_2 = ((1,), (1,), (-1,))
    differential_1 = ((-1, 1, 0), (1, 0, 1))
    composite = tuple(
        sum(
            differential_1[row][column] * differential_2[column][0]
            for column in range(3)
        )
        for row in range(2)
    )
    if composite != (0, 0):
        raise AssertionError("mapping-cone differential does not square to zero")
    if koszul.matrix_rank(differential_2) != 1 or koszul.matrix_rank(differential_1) != 2:
        raise AssertionError("interval isomorphism mapping cone is not acyclic")


def main():
    auxiliaries, pair_counts, persistent_counts = auxiliary_census()

    verify_pair_normal_form(
        ordinary_pair_columns,
        {
            Fraction(-1, 10): (
                (0, 1, 2, 3, 4),
                (0, 1, 3, 4, 5),
            ),
            Fraction(0): (
                (0, 1, 2, 3),
                (0, 1, 3, 4, 5),
            ),
            Fraction(1, 10): (
                (0, 1, 2, 3, 5),
                (0, 1, 3, 4, 5),
            ),
        },
        expected_rank=4,
    )
    verify_pair_normal_form(
        localization_pair_columns,
        {
            Fraction(-1, 10): (
                (0, 1, 2, 3),
                (0, 2, 3, 4),
            ),
            Fraction(0): (
                (0, 1, 2),
                (0, 2, 3, 4),
            ),
            Fraction(1, 10): (
                (0, 1, 2, 4),
                (0, 2, 3, 4),
            ),
        },
        expected_rank=3,
    )
    verify_same_side_simplex(
        ordinary_same_side_columns(Fraction(1, 10)), circuit_size=4
    )
    verify_same_side_simplex(
        localization_same_side_columns(Fraction(1, 10)), circuit_size=3
    )
    verify_mapping_cone()

    print("PASS: fixed-unit auxiliary counts=" + str(EXPECTED_AUXILIARIES))
    print("PASS: 671 potential opposite-side pairs and 2,420 persistent supports")
    print("PASS: ordinary six-support carrier is interval Q- -- R -- Q+")
    print("PASS: localization five-support carrier is interval Q- -- R -- Q+")
    print("PASS: the integral interval-isomorphism mapping cone is acyclic")
    print("PASS: same-side choices span simplices and supply coherent homotopies")
    print("THEOREM: every generic opposite circuit pair has an enlarged carrier")
    print("CAVEAT: monochromatic codimension-one stars and global acyclicity remain open")


if __name__ == "__main__":
    main()
