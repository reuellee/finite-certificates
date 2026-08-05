#!/usr/bin/env python3
"""Proof-safe catalog-wide residual-wall ranking for diagonal 9.

The alternative-certificate lemma from DIAG9_ACTIVE_SECTOR_THEOREM.md says
that incompatible transported fixed-unit circuit sign patterns certify an
empty residual wall.  This checker evaluates that lemma simultaneously on
all 2,604 realizable UOM(4,8) catalog parents using chirotope bitsets.

The 25 fixed determinant orbit identities are completed to invariant
three-bracket monomials.  Their normalized forms are already proved
symbolically by verify_derived_walls.py; column multidegree gives the displayed
homogeneous completion, and one exact moment-curve evaluation pins its sign.
No sampled residual sign is used for the catalog ranking.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import hashlib
from itertools import permutations
import json
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent

import DIAG9_GRAPH_exact_topes as topes


DATA = HERE / "data"
CERTIFICATES = HERE / "certs_4_8.jsonl"
FACTOR_CERTIFICATE = DATA / "DIAG9_GRAPH_global_factor_census.npz"

TRIPLE_INDEX = {triple: index for index, triple in enumerate(topes.TRIPLES)}
BASIS_INDEX = {basis: index for index, basis in enumerate(topes.BASES)}
LABEL_PERMUTATIONS = tuple(permutations(range(8)))

# representative fourset, invariant three-bracket monomial, and the
# nonconstant factors left in the projective frame of verify_derived_walls.py
FIXED_SPECIFICATIONS = {
    9: ("123/124/134/234", "1234/1234/1234", ""),
    10: ("123/124/134/235", "1234/1234/1235", ""),
    11: ("123/124/134/256", "1234/1234/1256", "1256"),
    12: ("123/124/134/567", "1234/1234/1567", "1567"),
    16: ("123/124/135/236", "1234/1235/1236", "1236"),
    17: ("123/124/135/245", "1234/1235/1245", ""),
    18: ("123/124/135/246", "1234/1235/1246", "1246"),
    19: ("123/124/135/256", "1234/1235/1256", "1256"),
    20: ("123/124/135/267", "1234/1235/1267", "1267"),
    21: ("123/124/135/456", "1234/1235/1456", "1456"),
    22: ("123/124/135/467", "1234/1235/1467", "1467"),
    23: ("123/124/135/678", "1234/1235/1678", "1678"),
    26: ("123/124/156/256", "1234/1256/1256", "1256/1256"),
    27: ("123/124/156/257", "1234/1256/1257", "1256/1257"),
    28: ("123/124/156/278", "1234/1256/1278", "1256/1278"),
    29: ("123/124/156/345", "1234/1345/1256", "1256"),
    30: ("123/124/156/347", "1234/1256/1347", "1256/1347"),
    31: ("123/124/156/356", "1234/1256/1356", "1256/1356"),
    32: ("123/124/156/357", "1234/1256/1357", "1256/1357"),
    33: ("123/124/156/378", "1234/1256/1378", "1256/1378"),
    34: ("123/124/156/567", "1234/1256/1567", "1256/1567"),
    35: ("123/124/156/578", "1234/1256/1578", "1256/1578"),
    40: ("123/124/356/456", "1234/1256/3456", "3456/1256"),
    43: ("123/124/356/567", "1234/1256/3567", "1256/3567"),
    45: ("123/124/567/568", "1234/1256/5678", "1256/5678"),
}

# The nine ordinary residual templates and their fixed-unit auxiliary normal.
ORDINARY_SPECIFICATIONS = {
    37: ("123/124/345/567", "134"),
    38: ("123/124/345/678", "134"),
    41: ("123/124/356/457", "134"),
    42: ("123/124/356/478", "134"),
    44: ("123/124/356/578", "135"),
    48: ("123/145/246/356", "124"),
    49: ("123/145/246/357", "124"),
    50: ("123/145/246/378", "124"),
    51: ("123/145/267/468", "124"),
}

# circuit, residual normal, structural auxiliary normal
LOCALIZATION_SPECIFICATIONS = {
    36: ("123/345/367", "124", "134"),
    39: ("123/356/378", "124", "135"),
    46: ("123/145/167", "246", "124"),
    47: ("123/145/167", "248", "124"),
}

FRAME_CONSTANT_BASES = {
    (0, 1, 2, 3),
    (0, 1, 2, 4),
    (0, 1, 3, 4),
    (0, 2, 3, 4),
    (1, 2, 3, 4),
}

EXPECTED_RANKING_DIGEST = (
    "1d5c239bd64a59514bc20e4b09244bbab9b00898384f3d39d67b5cf147ff6f65"
)
EXPECTED_PARENT860_MATRIX = (
    (5, -4, 3, 8, 1, 4, 0, 8),
    (1, 8, -2, 4, 4, -5, 8, 1),
    (-8, -4, 5, 4, 8, 1, 1, -2),
    (-4, -3, -8, -5, 3, 8, 4, 3),
)


def parse_blocks(text: str, size: int) -> tuple[tuple[int, ...], ...]:
    if not text:
        return ()
    blocks = tuple(
        tuple(int(character) - 1 for character in block)
        for block in text.split("/")
    )
    if any(len(block) != size or tuple(sorted(block)) != block for block in blocks):
        raise AssertionError(f"malformed {size}-subset specification: {text}")
    return blocks


def parity(sequence) -> int:
    sequence = tuple(sequence)
    return sum(
        sequence[left] > sequence[right]
        for left in range(len(sequence))
        for right in range(left + 1, len(sequence))
    ) & 1


def sorted_parity(sequence) -> int:
    sequence = tuple(sequence)
    rank = {item: index for index, item in enumerate(sorted(sequence))}
    return parity(tuple(rank[item] for item in sequence))


def relabel(subset, permutation):
    return tuple(sorted(permutation[vertex] for vertex in subset))


def bracket(parent, basis):
    return topes.determinant(
        tuple(
            tuple(int(parent[row][column]) for column in basis)
            for row in range(4)
        )
    )


def fixed_representatives():
    moment_parent = tuple(
        tuple(parameter**degree for parameter in range(8))
        for degree in range(4)
    )
    moment_rows = {
        triple: row
        for triple, row in zip(
            topes.TRIPLES,
            topes.derived_rows(moment_parent, normalize=False),
            strict=True,
        )
    }
    answer = {}
    for kind, (fourset_text, factors_text, normalized_text) in (
        FIXED_SPECIFICATIONS.items()
    ):
        fourset = parse_blocks(fourset_text, 3)
        factors = parse_blocks(factors_text, 4)
        normalized = parse_blocks(normalized_text, 4)
        if len(fourset) != 4 or len(factors) != 3:
            raise AssertionError("fixed determinant must have four triples and three brackets")
        fourset_degree = tuple(
            sum(vertex in triple for triple in fourset) for vertex in range(8)
        )
        factor_degree = tuple(
            sum(vertex in basis for basis in factors) for vertex in range(8)
        )
        if fourset_degree != factor_degree:
            raise AssertionError(f"fixed type {kind} has wrong homogeneous completion")
        remaining = tuple(sorted(basis for basis in factors if basis not in FRAME_CONSTANT_BASES))
        if remaining != tuple(sorted(normalized)):
            raise AssertionError(f"fixed type {kind} disagrees with normalized identity")
        determinant = topes.determinant(tuple(moment_rows[triple] for triple in fourset))
        product = np.prod([bracket(moment_parent, basis) for basis in factors], dtype=object)
        if determinant != product or determinant <= 0:
            raise AssertionError(f"fixed type {kind} has wrong invariant orientation")
        answer[kind] = (fourset, factors, 0)
    return answer


def fixed_sorted_formulas():
    """Map each sorted fixed fourset to (negative parity, bracket XOR mask)."""
    answer = {}
    for kind, (representative, bracket_bases, base_constant) in (
        fixed_representatives().items()
    ):
        for permutation in LABEL_PERMUTATIONS:
            relabeled_in_order = tuple(
                relabel(edge, permutation) for edge in representative
            )
            fourset = tuple(sorted(relabeled_in_order))
            constant = base_constant
            constant ^= sum(
                parity(tuple(permutation[vertex] for vertex in edge))
                for edge in representative
            ) & 1
            constant ^= sorted_parity(relabeled_in_order)
            bracket_mask = 0
            for basis in bracket_bases:
                mapped = tuple(permutation[vertex] for vertex in basis)
                constant ^= parity(mapped)
                bracket_mask ^= 1 << BASIS_INDEX[tuple(sorted(mapped))]
            formula = (constant, bracket_mask)
            previous = answer.setdefault(fourset, formula)
            if previous != formula:
                raise AssertionError(f"inconsistent fixed formula transport at {fourset}")
    if len(answer) != 223_790:
        raise AssertionError(f"wrong fixed fourset coverage: {len(answer)}")
    return answer


def transported_certificates():
    answer = defaultdict(set)
    for kind, (circuit_text, auxiliary_text) in ORDINARY_SPECIFICATIONS.items():
        representative = parse_blocks(circuit_text, 3)
        auxiliary = parse_blocks(auxiliary_text, 3)[0]
        for permutation in LABEL_PERMUTATIONS:
            circuit_edges = tuple(relabel(edge, permutation) for edge in representative)
            auxiliary_edge = relabel(auxiliary, permutation)
            circuit = tuple(TRIPLE_INDEX[edge] for edge in circuit_edges)
            occurrence = tuple(sorted(circuit))
            answer[occurrence].add(
                ("ordinary", circuit, TRIPLE_INDEX[auxiliary_edge], kind)
            )
    for kind, (circuit_text, residual_text, structural_text) in (
        LOCALIZATION_SPECIFICATIONS.items()
    ):
        representative = parse_blocks(circuit_text, 3)
        residual = parse_blocks(residual_text, 3)[0]
        structural = parse_blocks(structural_text, 3)[0]
        for permutation in LABEL_PERMUTATIONS:
            circuit_edges = tuple(relabel(edge, permutation) for edge in representative)
            residual_edge = relabel(residual, permutation)
            structural_edge = relabel(structural, permutation)
            circuit = tuple(TRIPLE_INDEX[edge] for edge in circuit_edges)
            residual_index = TRIPLE_INDEX[residual_edge]
            occurrence = tuple(sorted(circuit + (residual_index,)))
            answer[occurrence].add(
                (
                    "localization",
                    circuit,
                    residual_index,
                    TRIPLE_INDEX[structural_edge],
                    kind,
                )
            )
    if len(answer) != 84_840:
        raise AssertionError(f"transport covers {len(answer)}, not 84,840 occurrences")
    multiplicity = Counter(map(len, answer.values()))
    if multiplicity != Counter({2: 40_320, 4: 29_400, 6: 6_720, 8: 7_560, 24: 840}):
        raise AssertionError("wrong transported-certificate multiplicity")
    return {
        occurrence: tuple(sorted(certificates, key=repr))
        for occurrence, certificates in answer.items()
    }


def formula_xor(left, right):
    return left[0] ^ right[0], left[1] ^ right[1]


def ordered_fixed_formula(ordered_indices, formulas):
    ordered = tuple(topes.TRIPLES[index] for index in ordered_indices)
    sorted_fourset = tuple(sorted(ordered))
    constant, mask = formulas[sorted_fourset]
    return constant ^ sorted_parity(ordered), mask


def certificate_pattern(certificate, formulas):
    if certificate[0] == "ordinary":
        circuit, auxiliary = certificate[1], certificate[2]
        columns = circuit + (auxiliary,)
        coefficient = {
            circuit[omitted]: formula_xor(
                (omitted & 1, 0),
                ordered_fixed_formula(
                    columns[:omitted] + columns[omitted + 1 :], formulas
                ),
            )
            for omitted in range(4)
        }
    else:
        circuit, residual, structural = certificate[1:4]
        columns = circuit + (residual, structural)
        coefficient = {
            circuit[omitted]: formula_xor(
                (omitted & 1, 0),
                ordered_fixed_formula(
                    columns[:omitted] + columns[omitted + 1 :], formulas
                ),
            )
            for omitted in range(3)
        }
    support = tuple(sorted(circuit))
    first = coefficient[support[0]]
    return support, tuple(formula_xor(coefficient[row], first) for row in support)


def evaluate_formula(formula, bracket_parent_bits, all_parents):
    constant, mask = formula
    answer = all_parents if constant else 0
    while mask:
        bit = mask & -mask
        answer ^= bracket_parent_bits[bit.bit_length() - 1]
        mask ^= bit
    return answer


def det3(a, b, c):
    return (
        a[0] * (b[1] * c[2] - b[2] * c[1])
        - a[1] * (b[0] * c[2] - b[2] * c[0])
        + a[2] * (b[0] * c[1] - b[1] * c[0])
    )


def det4(a, b, c, d):
    return (
        a[0] * det3(b[1:], c[1:], d[1:])
        - a[1]
        * det3((b[0], b[2], b[3]), (c[0], c[2], c[3]), (d[0], d[2], d[3]))
        + a[2]
        * det3((b[0], b[1], b[3]), (c[0], c[1], c[3]), (d[0], d[1], d[3]))
        - a[3] * det3(b[:3], c[:3], d[:3])
    )


def direct_parent_check(record, formulas, certificates, foursets, occurrence_factor):
    if tuple(tuple(map(int, row)) for row in record["matrix"]) != EXPECTED_PARENT860_MATRIX:
        raise AssertionError("stored parent-860 matrix changed")
    rows = topes.derived_rows(record["matrix"])
    expected = tuple(1 if symbol == "+" else -1 for symbol in record["chi"])
    if topes.parent_signs(record["matrix"]) != expected:
        raise AssertionError("parent-860 matrix does not reproduce its chirotope")
    sorted_sign = {}
    for fourset in formulas:
        identifiers = tuple(TRIPLE_INDEX[edge] for edge in fourset)
        value = det4(*(rows[index] for index in identifiers))
        if not value:
            raise AssertionError("a fixed determinant vanished at parent 860")
        sorted_sign[fourset] = int(value < 0)

    def ordered_sign(ordered_indices):
        ordered = tuple(topes.TRIPLES[index] for index in ordered_indices)
        return sorted_sign[tuple(sorted(ordered))] ^ sorted_parity(ordered)

    def direct_pattern(certificate):
        if certificate[0] == "ordinary":
            circuit, auxiliary = certificate[1], certificate[2]
            columns = circuit + (auxiliary,)
            coefficient = {
                circuit[omitted]: (omitted & 1)
                ^ ordered_sign(columns[:omitted] + columns[omitted + 1 :])
                for omitted in range(4)
            }
        else:
            circuit, residual, structural = certificate[1:4]
            columns = circuit + (residual, structural)
            coefficient = {
                circuit[omitted]: (omitted & 1)
                ^ ordered_sign(columns[:omitted] + columns[omitted + 1 :])
                for omitted in range(3)
            }
        support = tuple(sorted(circuit))
        first = coefficient[support[0]]
        return support, tuple(coefficient[row] ^ first for row in support)

    conflicting = set()
    empty_factors = set()
    for occurrence_index, occurrence in enumerate(foursets):
        alternatives = tuple(
            direct_pattern(certificate) for certificate in certificates[occurrence]
        )
        if any(alternative != alternatives[0] for alternative in alternatives[1:]):
            conflicting.add(occurrence_index)
            empty_factors.add(occurrence_factor[occurrence_index])
    if (len(conflicting), len(empty_factors)) != (31_380, 10_320):
        raise AssertionError("parent-860 direct determinant census changed")


def main():
    records = [
        json.loads(line)
        for line in CERTIFICATES.open(encoding="utf-8")
        if line.strip()
    ]
    if len(records) != 2_628:
        raise AssertionError("wrong catalog certificate count")
    realizable = [
        (catalog_index, record)
        for catalog_index, record in enumerate(records)
        if record["verdict"] == "REALIZABLE"
    ]
    if len(realizable) != 2_604:
        raise AssertionError("wrong realizable parent count")
    parent_position = {
        catalog_index: position
        for position, (catalog_index, _) in enumerate(realizable)
    }

    bracket_parent_bits = [0] * len(topes.BASES)
    for position, (_, record) in enumerate(realizable):
        if len(record["chi"]) != len(topes.BASES):
            raise AssertionError("wrong parent chirotope length")
        for basis_index, symbol in enumerate(record["chi"]):
            if symbol == "-":
                bracket_parent_bits[basis_index] |= 1 << position
            elif symbol != "+":
                raise AssertionError("bad chirotope symbol")
    all_parents = (1 << len(realizable)) - 1

    formulas = fixed_sorted_formulas()
    certificates = transported_certificates()
    with np.load(FACTOR_CERTIFICATE, allow_pickle=False) as source:
        if str(source["format"].item()) != "diag9-global-residual-factor-census-v1":
            raise AssertionError("wrong global factor certificate")
        foursets = tuple(tuple(map(int, row)) for row in source["occurrence_fourset"])
        occurrence_factor = tuple(map(int, source["occurrence_factor"]))
        factor_multiplicity = tuple(map(int, source["factor_multiplicity"]))
    if tuple(sorted(certificates)) != foursets or len(foursets) != 84_840:
        raise AssertionError("circuit transports disagree with factor census")
    if len(factor_multiplicity) != 26_740 or sum(factor_multiplicity) != 84_840:
        raise AssertionError("wrong primitive factor census")

    selected_positions = {
        index: parent_position[index] for index in (860, 2_599)
    }
    selected_conflicts = Counter()
    factor_conflict_bits = [0] * len(factor_multiplicity)
    for occurrence_index, occurrence in enumerate(foursets):
        alternatives = tuple(
            certificate_pattern(certificate, formulas)
            for certificate in certificates[occurrence]
        )
        if len({support for support, _ in alternatives}) != 1:
            raise AssertionError("alternative changed its circuit support")
        reference = alternatives[0][1]
        conflict_bits = 0
        for _, pattern in alternatives[1:]:
            for left, right in zip(reference, pattern, strict=True):
                conflict_bits |= evaluate_formula(
                    formula_xor(left, right), bracket_parent_bits, all_parents
                )
        factor_conflict_bits[occurrence_factor[occurrence_index]] |= conflict_bits
        for catalog_index, position in selected_positions.items():
            selected_conflicts[catalog_index] += (conflict_bits >> position) & 1

    byte_count = (len(realizable) + 7) // 8
    packed = np.empty((len(factor_conflict_bits), byte_count), dtype=np.uint8)
    for index, bits in enumerate(factor_conflict_bits):
        packed[index] = np.frombuffer(bits.to_bytes(byte_count, "little"), dtype=np.uint8)
    empty_counts = np.unpackbits(packed, axis=1, bitorder="little")[:, : len(realizable)].sum(
        axis=0, dtype=np.uint32
    )
    candidate_counts = len(factor_conflict_bits) - empty_counts

    if selected_conflicts != Counter({860: 31_380, 2_599: 27_944}):
        raise AssertionError(f"selected conflict counts changed: {selected_conflicts}")
    if int(empty_counts[parent_position[860]]) != 10_320:
        raise AssertionError("parent 860 empty-factor count changed")
    if int(empty_counts[parent_position[2_599]]) != 8_916:
        raise AssertionError("parent 2599 empty-factor count changed")

    ranking = sorted(
        (
            int(candidate_counts[position]),
            int(empty_counts[position]),
            catalog_index,
        )
        for position, (catalog_index, _) in enumerate(realizable)
    )
    if ranking[0] != (16_420, 10_320, 860):
        raise AssertionError(f"wrong unique best parent: {ranking[0]}")
    if [item[2] for item in ranking if item[0] == ranking[0][0]] != [860]:
        raise AssertionError("parent 860 is not the unique candidate minimum")
    if ranking[-4:] != [
        (17_824, 8_916, 2_599),
        (17_824, 8_916, 2_600),
        (17_824, 8_916, 2_601),
        (17_824, 8_916, 2_602),
    ]:
        raise AssertionError("wrong maximum-candidate parent block")

    digest = hashlib.sha256()
    digest.update(b"diag9-parent-empty-wall-ranking-v1\0")
    for position, (catalog_index, _) in enumerate(realizable):
        digest.update(int(catalog_index).to_bytes(4, "little"))
        digest.update(int(empty_counts[position]).to_bytes(4, "little"))
    ranking_digest = digest.hexdigest()
    if ranking_digest != EXPECTED_RANKING_DIGEST:
        raise AssertionError(f"ranking semantic digest changed: {ranking_digest}")

    direct_parent_check(
        records[860], formulas, certificates, foursets, occurrence_factor
    )

    print("PASS: 25 invariant fixed determinant identities cover 223,790 foursets")
    print("PASS: all 84,840 residual occurrences retain every transported identity")
    print("PASS: 2,604 realizable catalog chirotopes ranked by exact bitset evaluation")
    print("PASS: direct parent-860 determinant replay = 31,380 conflicts, 10,320 empty factors")
    print("THEOREM AUDIT: parent 860 uniquely minimizes candidates at 16,420")
    print("RANGE: 16,420--17,824 candidate residual factors across the catalog")
    print("SEMANTIC SHA256", ranking_digest)
    print("SCOPE: proof-safe roadmap ranking; no candidate wall is asserted nonempty")


if __name__ == "__main__":
    main()
