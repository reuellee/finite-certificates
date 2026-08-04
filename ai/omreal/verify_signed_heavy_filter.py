#!/usr/bin/env python3
"""Exact signed structural filter for the pencil-rigid 4+5 and 5+5 residue.

The common-light exit lemma reduces the generic second-diagonal calculation
to pencil-rigid pairs.  This checker supplies the exact size-five cofactor
classification used before the exhaustive pair-orbit Burnside calculation.
It proves that

* 24 of the 117 generic five-support orbits have only parent-bracket-unit
  cofactors and hence cannot be positive for a realizable extension;
* the remaining 93 orbit types comprise 1,651,440 labeled supports, stratified
  exactly by their number of residual cofactors; and
* exact row-2599 charts contain surviving pencil-rigid positive pairs of both
  size types, so incidence and unary extension signs cannot finish the second
  diagonal.

The script also reports the unit-XOR support pruning for the eight prescribed
row-2599 shatter signatures.  That is explicitly a finite sample.  The full
pencil-rigid pair-orbit and beta census is performed by
``verify_signed_pencil_orbits.cpp``.  No floating point arithmetic, LP, SAT
search, CAD, or enumeration of the 97,224 single-element extension signatures
is used here.
"""

from collections import Counter
from itertools import combinations, permutations
from pathlib import Path
import sys

import numpy as np

import prototype_koszul_circuits as koszul
import verify_signed_circuit_filter as signed


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "seeat_parent2599_shatter8.npz"
TRIPLES = koszul.TRIPLES
TRIPLE_INDEX = koszul.TRIPLE_INDEX
FULL_SHEAR_MASK = (1 << 56) - 1


def support_indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask -= bit


def support_mask(indices):
    return sum(1 << index for index in indices)


def generic_five(indices):
    """Every four-subset is nonstructural, in incidence form."""
    degrees = [0] * 8
    codegrees = Counter()
    for index in indices:
        triple = TRIPLES[index]
        for vertex in triple:
            degrees[vertex - 1] += 1
            if degrees[vertex - 1] == 4:
                return False
        for pair in combinations(triple, 2):
            codegrees[pair] += 1
            if codegrees[pair] == 3:
                return False
    return True


def support_degree_defect(mask):
    """Return the eight degrees and the fixed-partner defect mask."""
    degrees = [0] * 8
    shear_coverage = 0
    for index in support_indices(mask):
        triple = TRIPLES[index]
        for vertex in triple:
            degrees[vertex - 1] += 1
            for partner in range(1, 9):
                if partner in triple:
                    continue
                bit = 7 * (vertex - 1) + (partner - 1) - (partner > vertex)
                shear_coverage |= 1 << bit
    return tuple(degrees), FULL_SHEAR_MASK ^ shear_coverage


def pencil_rigid_pair(first, second):
    """Minimum union degree three and no common fixed shear partner."""
    union = first | second
    degrees = [0] * 8
    for index in support_indices(union):
        for vertex in TRIPLES[index]:
            degrees[vertex - 1] += 1
    _, first_defect = support_degree_defect(first)
    _, second_defect = support_degree_defect(second)
    return min(degrees) >= 3 and not first_defect & second_defect


def transform_support(mask, edge_map):
    result = 0
    for index in support_indices(mask):
        result |= 1 << edge_map[index]
    return result


def positive_stored_circuit(certificate, pattern, signature_index):
    weights = [int(value) for value in certificate["gordan_weight"][pattern, signature_index]]
    support = tuple(index for index, value in enumerate(weights) if value)
    matrix = certificate["pattern_chart"][pattern]
    normals = koszul.parent_normals(matrix)
    signature = int(certificate["signature"][signature_index])
    columns = signed.signed_normal_columns(normals, signature, support)
    rank, cofactors = koszul.circuit_cofactors(columns)
    witness = koszul.primitive([weights[index] for index in support])
    if cofactors != witness:
        raise AssertionError("stored Gordan witness is not the circuit cofactor")
    return support_mask(support), rank, tuple(witness)


def main():
    certificate = np.load(CERTIFICATE, allow_pickle=False)
    if int(certificate["parent_index"].item()) != 2599:
        raise AssertionError("wrong parent")
    matrix = certificate["pattern_chart"][0]
    normals = koszul.parent_normals(matrix)
    signatures = tuple(int(value) for value in certificate["signature"])

    # Classify every four-normal determinant once.  Unit signs are evaluated
    # on the exact pattern-zero chart; their sign is constant on the parent
    # realization chamber by the derived-wall theorem.
    residual_four = set()
    unit_four_sign = {}
    for four_set in combinations(range(len(TRIPLES)), 4):
        mask = support_mask(four_set)
        orbit = koszul.wall_orbit(four_set)
        if orbit in koszul.ZERO:
            continue
        if orbit in koszul.RESIDUAL:
            residual_four.add(mask)
            continue
        determinant = signed.determinant_columns(
            [normals[index] for index in four_set]
        )
        unit_four_sign[mask] = signed.sign(determinant)
    if (len(residual_four), len(unit_four_sign)) != (84_840, 223_790):
        raise AssertionError("wrong derived four-set classification")

    all_five = set()
    residual_distribution = Counter()
    row_eligible = [0] * len(signatures)
    row_eligible_by_residual = [Counter() for _ in signatures]
    for support_tuple in combinations(range(len(TRIPLES)), 5):
        if not generic_five(support_tuple):
            continue
        mask = support_mask(support_tuple)
        all_five.add(mask)
        residual_indices = []
        unit_indices = []
        for omitted, index in enumerate(support_tuple):
            cofactor_mask = mask ^ (1 << index)
            if cofactor_mask in residual_four:
                residual_indices.append(omitted)
            elif cofactor_mask in unit_four_sign:
                unit_indices.append(
                    (omitted, ((-1) ** omitted) * unit_four_sign[cofactor_mask])
                )
            else:
                raise AssertionError("generic five-support has a zero cofactor")
        number_residual = len(residual_indices)
        residual_distribution[number_residual] += 1

        # A realizable signature cannot align an all-unit circuit: it would
        # then be positive on every parent chart, including one realizing the
        # signature.  For the eight exact signatures, verify the same fact
        # directly from their five known signs.
        if number_residual == 0:
            for signature in signatures:
                products = {
                    unit_sign
                    * (1 if (signature >> support_tuple[index]) & 1 else -1)
                    for index, unit_sign in unit_indices
                }
                if len(products) == 1:
                    raise AssertionError("realizable signature aligns an all-unit circuit")
            continue

        for signature_index, signature in enumerate(signatures):
            products = {
                unit_sign
                * (1 if (signature >> support_tuple[index]) & 1 else -1)
                for index, unit_sign in unit_indices
            }
            # With no unit cofactor, eta is free.  Otherwise all unit products
            # must equal the one common eta in the circuit XOR equations.
            if len(products) <= 1:
                row_eligible[signature_index] += 1
                row_eligible_by_residual[signature_index][number_residual] += 1

    expected_distribution = {
        0: 370_552,
        1: 485_520,
        2: 567_840,
        3: 433_440,
        4: 30_240,
        5: 134_400,
    }
    if residual_distribution != expected_distribution:
        raise AssertionError(f"wrong residual distribution {residual_distribution}")
    number_variable_five = sum(
        count for residuals, count in residual_distribution.items() if residuals
    )
    if (len(all_five), number_variable_five) != (2_021_992, 1_651_440):
        raise AssertionError("wrong generic five-support totals")
    expected_row_eligible = (
        436_254, 434_110, 440_998, 442_502,
        433_503, 436_051, 437_702, 436_587,
    )
    if tuple(row_eligible) != expected_row_eligible:
        raise AssertionError(f"wrong row-sample unit-XOR counts {row_eligible}")
    print(
        "PASS: generic five-supports by residual cofactors = "
        "0:370552, 1:485520, 2:567840, 3:433440, 4:30240, 5:134400"
    )
    del unit_four_sign

    # Build S_8 maps and extract all 117 five-support orbits.  Residual count
    # is invariant, so this simultaneously proves the orbit distribution.
    permutations8 = tuple(permutations(range(8)))
    edge_maps = tuple(
        tuple(
            TRIPLE_INDEX[tuple(sorted(permutation[label - 1] + 1 for label in triple))]
            for triple in TRIPLES
        )
        for permutation in permutations8
    )
    remaining = set(all_five)
    orbit_residual_distribution = Counter()
    while remaining:
        representative = remaining.pop()
        orbit = {
            transform_support(representative, edge_map) for edge_map in edge_maps
        }
        remaining.difference_update(orbit)
        number_residual = sum(
            (representative ^ (1 << index)) in residual_four
            for index in support_indices(representative)
        )
        orbit_residual_distribution[number_residual] += 1
    expected_orbit_distribution = {0: 24, 1: 25, 2: 30, 3: 21, 4: 6, 5: 11}
    if orbit_residual_distribution != expected_orbit_distribution:
        raise AssertionError(
            f"wrong five-support orbit distribution {orbit_residual_distribution}"
        )
    print("PASS: five-support orbits by residual cofactors = 0:24,1:25,2:30,3:21,4:6,5:11")

    # Exact pencil-rigid survivors.  Pattern zero supplies a generic 5+5 pair;
    # pattern four supplies a generic 5+4 pair.  Each stored dependence is
    # support-minimal and positive after the prescribed reorientation.
    five_first, rank_first, coefficients_first = positive_stored_circuit(
        certificate, 0, 0
    )
    five_second, rank_second, coefficients_second = positive_stored_circuit(
        certificate, 0, 4
    )
    if not (
        rank_first == rank_second == 4
        and generic_five(tuple(support_indices(five_first)))
        and generic_five(tuple(support_indices(five_second)))
        and pencil_rigid_pair(five_first, five_second)
    ):
        raise AssertionError("pattern-zero 5+5 survivor failed")
    union_degrees = [0] * 8
    for index in support_indices(five_first | five_second):
        for vertex in TRIPLES[index]:
            union_degrees[vertex - 1] += 1
    if (five_first | five_second).bit_count() != 9 or union_degrees != [3, 5, 3, 3, 3, 3, 4, 3]:
        raise AssertionError("wrong pencil-rigid survivor incidence")

    mixed_five, mixed_five_rank, mixed_five_coefficients = positive_stored_circuit(
        certificate, 4, 3
    )
    mixed_four, mixed_four_rank, mixed_four_coefficients = positive_stored_circuit(
        certificate, 4, 7
    )
    mixed_four_tuple = tuple(support_indices(mixed_four))
    if not (
        mixed_five_rank == 4
        and mixed_four_rank == 3
        and generic_five(tuple(support_indices(mixed_five)))
        and signed.generic_four_data(mixed_four_tuple) is not None
        and pencil_rigid_pair(mixed_five, mixed_four)
    ):
        raise AssertionError("pattern-four 4+5 survivor failed")

    # Independently recheck exact realizability of the two prescribed
    # signatures on their one-bit charts.  The opposite signature is
    # infeasible on each of those two charts, so the regions are proper and
    # incomparable, not merely abstractly realizable.
    zero_parent = signed.parent_signs(matrix)
    opposite_signature = {0: 4, 4: 0, 3: 7, 7: 3}
    for signature_index in opposite_signature:
        pattern = 1 << signature_index
        feasible_matrix = certificate["pattern_chart"][pattern]
        if signed.parent_signs(feasible_matrix) != zero_parent:
            raise AssertionError("feasible chart changed the parent")
        point = [
            int(value)
            for value in certificate["feasible_point"][pattern, signature_index]
        ]
        signed.check_strict_extension(
            feasible_matrix, point, signatures[signature_index]
        )
        opposite = opposite_signature[signature_index]
        opposite_mask, _, _ = positive_stored_circuit(
            certificate, pattern, opposite
        )
        if not opposite_mask:
            raise AssertionError("missing exact incomparability witness")
    if not all(
        coefficients
        for coefficients in (
            coefficients_first,
            coefficients_second,
            mixed_five_coefficients,
            mixed_four_coefficients,
        )
    ):
        raise AssertionError("empty positive-circuit coefficient vector")
    print("PASS: exact row-2599 pencil-rigid survivors exist in both 4+5 and 5+5")
    print(
        "PASS (row-2599 sample): unit-XOR leaves "
        f"{min(row_eligible):,}..{max(row_eligible):,} of "
        f"{number_variable_five:,} variable-cofactor five-supports"
    )
    print("THEOREM: signed structural pruning is substantial but leaves both generic size types")
    print("CAVEAT: the complete derived-sign SAT filter is necessary, not sufficient for realizability")


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    main()
