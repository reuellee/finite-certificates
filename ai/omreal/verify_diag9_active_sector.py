#!/usr/bin/env python3
"""Exact audit for the diagonal-nine active-factor sector theorem.

This verifier transports the thirteen certified residual-wall circuit
templates to all 84,840 labeled occurrences and retains every transported
identity.  Conflicting fixed-unit circuit sign patterns certify factors whose
wall sections are empty in parent 2599.  After removing them, the checker
computes the remaining global factor literals forced by two committed proper
incomparable nine-families.

It proves only the finite counts and orientation consistency.  The active
sector theorem itself is the argument in DIAG9_ACTIVE_SECTOR_THEOREM.md.
"""

from __future__ import annotations

import contextlib
import hashlib
from collections import Counter, defaultdict
from io import StringIO
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
sys.path.insert(0, str(HERE))

PINNED_SHA256 = {
    "DIAG9_GRAPH_global_factor_census.npz":
        "3984ce87e11fd59d804e59568177248e218cd1c7bb07aae0a9f9f746858728bc",
    "DIAG9_GRAPH_row2599_factor_states.npz":
        "f44b1fccfb4e61273aeceb8796a18098d82c48473e257556ce3d2a22f99b0bcf",
    "seeat_parent2599_upper178.npz":
        "3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a",
    "ninth_candidate_12_37_antichain.npz":
        "11ca66549982ec40ce8425d2caed45b418edb73c4eb415a45b39d57e481bd1e4",
    "ninth_candidate_12_37_path.npz":
        "8db38e00d9bf8701558c27cd4ede3e024db8953ea3ef9873bf0b4fc65ad6bcda",
    "ninth_candidate_37_176_antichain.npz":
        "fe7bb166b5a151262c665875d32de49d7e8a330cf11b26609458af6b2661a59f",
    "ninth_candidate_37_176_path.npz":
        "3c37c3c0d5de159bec9d48eeaaf57bccbe07c2f3aeb0ede9d4b1ddbae2bd3507",
}

EXPECTED_FAMILY = {
    "12_37": {
        "per_signature": (791, 656, 628, 541, 548, 622, 647, 503, 510),
        "counts": (5_026, 3_539, 14_285, 5_198),
        "digest": "6de7ff2716b65853c04b9a08f44eb98ad8966e1f3525887ffafde0a3b805c154",
    },
    "37_176": {
        "per_signature": (684, 595, 689, 562, 591, 681, 587, 607, 785),
        "counts": (5_554, 3_638, 14_186, 3_320),
        "digest": "5cede059d413bffdd18e98ca8a261ec9b2174e558ea4c4bc51a27decaf40a3ee",
    },
}

# Importing this verifier replays the symbolic wall classification, all
# 13 circuit templates, and the exhaustive orbit-size checks.
with contextlib.redirect_stdout(StringIO()):
    import verify_derived_wall_sides as sides

import DIAG9_GRAPH_exact_topes as topes
import DIAG9_GRAPH_verify_row2599_slice as slice_verify


def sign(value: int) -> int:
    if value == 0:
        raise AssertionError("unexpected zero")
    return 1 if value > 0 else -1


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_pins() -> None:
    for name, expected in PINNED_SHA256.items():
        if sha256(DATA / name) != expected:
            raise AssertionError(f"pinned artifact changed: {name}")


TRIPLE_INDEX = {triple: index for index, triple in enumerate(topes.TRIPLES)}


def relabel(edge, permutation):
    return tuple(sorted(permutation[vertex] for vertex in edge))


def transported_certificates():
    """Return every transported circuit certificate for each occurrence."""
    specifications = {}
    for kind in sides.FOUR_ROW_TYPES:
        auxiliary, _ = sides.four_row_certificates[kind]
        specifications[kind] = (
            "ordinary",
            sides.walls.representatives[kind],
            auxiliary,
        )
    for kind, (c_labels, z_label, w_label, *_) in (
        sides.LOCALIZATION_CERTIFICATES.items()
    ):
        specifications[kind] = (
            "localization",
            tuple(sides.parse_triple(label) for label in c_labels),
            sides.parse_triple(z_label),
            sides.parse_triple(w_label),
        )

    answer = defaultdict(set)
    for kind, specification in specifications.items():
        for permutation in sides.LABEL_PERMUTATIONS:
            if specification[0] == "ordinary":
                circuit_edges = tuple(
                    relabel(edge, permutation) for edge in specification[1]
                )
                auxiliary_edge = relabel(specification[2], permutation)
                circuit = tuple(TRIPLE_INDEX[edge] for edge in circuit_edges)
                occurrence = tuple(sorted(circuit))
                certificate = (
                    "ordinary",
                    circuit,
                    TRIPLE_INDEX[auxiliary_edge],
                    kind,
                )
            else:
                circuit_edges = tuple(
                    relabel(edge, permutation) for edge in specification[1]
                )
                residual_edge = relabel(specification[2], permutation)
                structural_edge = relabel(specification[3], permutation)
                circuit = tuple(TRIPLE_INDEX[edge] for edge in circuit_edges)
                residual = TRIPLE_INDEX[residual_edge]
                occurrence = tuple(sorted(circuit + (residual,)))
                certificate = (
                    "localization",
                    circuit,
                    residual,
                    TRIPLE_INDEX[structural_edge],
                    kind,
                )
            answer[occurrence].add(certificate)
    if len(answer) != 84_840:
        raise AssertionError("transport did not cover 84,840 residual occurrences")
    multiplicities = Counter(len(certificates) for certificates in answer.values())
    if multiplicities != Counter({2: 40_320, 4: 29_400, 6: 6_720,
                                  8: 7_560, 24: 840}):
        raise AssertionError("wrong transported-certificate multiplicities")
    return {
        occurrence: tuple(sorted(certificates, key=repr))
        for occurrence, certificates in answer.items()
    }


def det4(rows, identifiers):
    return slice_verify.det4(tuple(rows[index] for index in identifiers))


def oriented_certificate(occurrence, certificate, rows):
    """Orient one circuit certificate and its stored determinant order."""
    raw_value = det4(rows, occurrence)
    if raw_value == 0:
        raise AssertionError("generic chart lies on a residual wall")

    if certificate[0] == "ordinary":
        circuit, auxiliary = certificate[1], certificate[2]
        columns = circuit + (auxiliary,)
        coefficients = tuple(
            (-1) ** omitted
            * det4(rows, columns[:omitted] + columns[omitted + 1 :])
            for omitted in range(4)
        )
        if not all(coefficients):
            raise AssertionError("ordinary fixed coefficient vanished")
        ordered_determinant = det4(rows, circuit)
        certificate_data = (
            circuit,
            tuple(map(sign, coefficients)),
            auxiliary,
            sign(ordered_determinant) * sign(raw_value),
        )
    else:
        circuit, residual, structural = (
            certificate[1],
            certificate[2],
            certificate[3],
        )
        columns = circuit + (residual, structural)
        coefficients = tuple(
            (-1) ** omitted
            * det4(rows, columns[:omitted] + columns[omitted + 1 :])
            for omitted in range(5)
        )
        if not all(coefficients[index] for index in range(3)):
            raise AssertionError("localization fixed coefficient vanished")
        if coefficients[3] != 0 or coefficients[4] == 0:
            raise AssertionError("localization identity has wrong zero pattern")
        ordered_determinant = det4(rows, circuit + (residual,))
        certificate_data = (
            circuit,
            tuple(sign(coefficients[index]) for index in range(3)),
            structural,
            sign(ordered_determinant) * sign(raw_value),
        )
    # Last entry translates the determinant in the certificate ordering to
    # the lexically sorted occurrence ordering.
    return certificate_data, sign(raw_value)


def normalized_circuit_pattern(certificate_data):
    """Circuit coefficient signs in sorted support order, modulo scale."""
    circuit, coefficients = certificate_data[:2]
    ordered = tuple(
        coefficient
        for _, coefficient in sorted(zip(circuit, coefficients, strict=True))
    )
    if ordered[0] < 0:
        ordered = tuple(-coefficient for coefficient in ordered)
    return tuple(sorted(circuit)), ordered


def oriented_occurrences(foursets, certificates, rows):
    """Choose certificates and detect globally empty wall occurrences."""
    chosen = []
    conflicting = set()
    conflict_kinds = Counter()
    for occurrence_index, occurrence in enumerate(foursets):
        alternatives = [
            oriented_certificate(occurrence, certificate, rows)
            for certificate in certificates[occurrence]
        ]
        raw_signs = {raw_sign for _, raw_sign in alternatives}
        if len(raw_signs) != 1:
            raise AssertionError("one determinant occurrence has two raw signs")
        patterns = {
            normalized_circuit_pattern(certificate_data)
            for certificate_data, _ in alternatives
        }
        kinds = {certificate[0] for certificate in certificates[occurrence]}
        if len(kinds) != 1:
            raise AssertionError("one occurrence has mixed certificate kinds")
        kind = next(iter(kinds))
        circuit_supports = {pattern[0] for pattern in patterns}
        if kind == "ordinary" and circuit_supports != {occurrence}:
            raise AssertionError("ordinary alternative changed its circuit")
        if kind == "localization" and len(circuit_supports) != 1:
            raise AssertionError("localization alternatives changed circuit support")
        if len(patterns) > 1:
            conflict_kinds[kind] += 1
            conflicting.add(occurrence_index)
        chosen.append(alternatives[0])
    if len(conflicting) != 27_944:
        raise AssertionError("wrong conflicting-certificate occurrence count")
    if conflict_kinds != Counter({"ordinary": 20_112, "localization": 7_832}):
        raise AssertionError("wrong conflicting-certificate kind split")
    return chosen, conflicting


def aligned_literal(signature, certificate_data):
    """Return the allowed sorted raw-determinant sign, or None if inactive."""
    circuit, coefficients, auxiliary, order_orientation = certificate_data
    signed_coefficients = tuple(
        coefficients[position]
        * (1 if (signature >> row_index) & 1 else -1)
        for position, row_index in enumerate(circuit)
    )
    if len(set(signed_coefficients)) != 1:
        return None
    common_sign = signed_coefficients[0]
    auxiliary_sign = 1 if (signature >> auxiliary) & 1 else -1
    allowed_ordered = -common_sign * auxiliary_sign
    return allowed_ordered * order_orientation


def semantic_digest(
    name, signatures, factor_literals, active_occurrences, empty_factors
):
    digest = hashlib.sha256()
    digest.update(b"active-sector-nonempty-v2\0")
    digest.update(name.encode("ascii"))
    digest.update(np.asarray(signatures, dtype=np.uint64).tobytes())
    digest.update(np.asarray(sorted(empty_factors), dtype=np.uint32).tobytes())
    digest.update(b"|")
    for literals, occurrences in zip(
        factor_literals, active_occurrences, strict=True
    ):
        for factor, orientation in sorted(literals.items()):
            digest.update(int(factor).to_bytes(4, "little"))
            digest.update(bytes((orientation > 0,)))
        digest.update(b"|")
        digest.update(np.asarray(sorted(occurrences), dtype=np.uint32).tobytes())
    return digest.hexdigest()


def main():
    verify_pins()
    certificates = transported_certificates()
    with np.load(DATA / "DIAG9_GRAPH_global_factor_census.npz", allow_pickle=False) as source:
        if str(source["format"].item()) != "diag9-global-residual-factor-census-v1":
            raise AssertionError("wrong global factor certificate")
        foursets_array = np.asarray(source["occurrence_fourset"], dtype=np.uint8)
        occurrence_factor = np.asarray(source["occurrence_factor"], dtype=np.uint32)
        factor_multiplicity = np.asarray(
            source["factor_multiplicity"], dtype=np.uint32
        )
        factor_count = len(factor_multiplicity)
        factor_offsets = np.asarray(source["factor_offset"], dtype=np.uint32)
        factor_exponents = np.asarray(source["factor_exponent"], dtype=np.uint8)
        factor_coefficients = np.asarray(
            source["factor_coefficient"], dtype=np.int64
        )
        parent_bracket_label = np.asarray(
            source["parent_bracket_label"], dtype=np.uint8
        )
        unit_offsets = np.asarray(
            source["occurrence_unit_offset"], dtype=np.uint32
        )
        unit_indices = np.asarray(
            source["occurrence_unit_index"], dtype=np.uint8
        )
    foursets = tuple(tuple(map(int, row)) for row in foursets_array)
    if foursets_array.shape != (84_840, 4) or len(set(foursets)) != 84_840:
        raise AssertionError("wrong residual occurrence census")
    if foursets != tuple(sorted(foursets)) or set(foursets) != set(certificates):
        raise AssertionError("occurrences are not the complete sorted transport")
    if occurrence_factor.shape != (84_840,) or factor_count != 26_740:
        raise AssertionError("factor census and circuit transport disagree")
    if (
        int(occurrence_factor.min()) != 0
        or int(occurrence_factor.max()) != factor_count - 1
    ):
        raise AssertionError("factor IDs are not a complete zero-based range")
    actual_multiplicity = np.bincount(
        occurrence_factor.astype(np.int64), minlength=factor_count
    )
    if not np.array_equal(actual_multiplicity, factor_multiplicity):
        raise AssertionError("factor multiplicities disagree with assignments")
    if Counter(map(int, factor_multiplicity)) != Counter(
        {1: 25_200, 2: 420, 15: 280, 65: 840}
    ):
        raise AssertionError("wrong global-factor multiplicity distribution")
    if (
        factor_offsets.shape != (factor_count + 1,)
        or int(factor_offsets[0]) != 0
        or np.any(np.diff(factor_offsets.astype(np.int64)) < 0)
        or int(factor_offsets[-1]) != len(factor_exponents)
        or factor_exponents.shape != (len(factor_coefficients), 9)
        or np.any(factor_coefficients == 0)
    ):
        raise AssertionError("malformed primitive-factor polynomial arrays")
    if (
        parent_bracket_label.shape != (62, 4)
        or np.any(parent_bracket_label > 7)
        or any(
            tuple(map(int, row)) != tuple(sorted(map(int, row)))
            for row in parent_bracket_label
        )
        or len({tuple(map(int, row)) for row in parent_bracket_label}) != 62
    ):
        raise AssertionError("malformed parent-bracket label table")
    if (
        unit_offsets.shape != (84_841,)
        or int(unit_offsets[0]) != 0
        or np.any(np.diff(unit_offsets.astype(np.int64)) < 0)
        or int(unit_offsets[-1]) != len(unit_indices)
        or np.any(unit_indices >= len(parent_bracket_label))
    ):
        raise AssertionError("malformed occurrence-unit incidence arrays")
    unit_count = np.diff(unit_offsets)
    if Counter(map(int, unit_count)) != Counter({0: 32_760, 1: 52_080}):
        raise AssertionError("wrong stripped parent-unit distribution")
    if Counter(map(int, unit_indices)) != Counter(
        {index: 840 for index in range(62)}
    ):
        raise AssertionError("wrong stripped parent-bracket incidence")

    charts = np.load(
        DATA / "seeat_parent2599_upper178.npz", allow_pickle=False
    )["chart_matrix"]
    if charts.shape != (178, 4, 8):
        raise AssertionError("wrong orientation-chart array shape")
    for basis in parent_bracket_label:
        matrix = tuple(
            tuple(int(charts[0, row, column]) for column in basis)
            for row in range(4)
        )
        if topes.determinant(matrix) == 0:
            raise AssertionError("a stripped parent unit vanishes in chart 0")
    rows = topes.derived_rows(charts[0])
    oriented, conflicting_occurrences = oriented_occurrences(
        foursets, certificates, rows
    )
    empty_factors = {
        int(occurrence_factor[index]) for index in conflicting_occurrences
    }
    if len(empty_factors) != 8_916:
        raise AssertionError("wrong certified-empty factor count")
    # On an ordinary wall the four-row circuit kernel is one-dimensional;
    # on a localization wall the designated three-row kernel is likewise
    # one-dimensional.  All transported fixed-unit relations would therefore
    # have proportional coefficient signs.  A normalized sign disagreement
    # proves the occurrence has no zero in this parent cell.  Since its raw
    # determinant differs from the primitive factor by a nowhere-zero unit,
    # the entire factor wall is empty.

    # One fixed orientation per global factor: the raw determinant of its
    # lexically first occurrence.  The ratio between any occurrence and this
    # representative is a nowhere-zero parent-bracket unit and is recovered
    # exactly from chart 0.
    representative = np.full(factor_count, -1, dtype=np.int64)
    for occurrence_index, factor in enumerate(map(int, occurrence_factor)):
        if representative[factor] < 0:
            representative[factor] = occurrence_index
    if np.any(representative < 0):
        raise AssertionError("global factor without representative")
    representative_raw_sign = np.asarray(
        [oriented[index][1] for index in representative], dtype=np.int8
    )

    with np.load(
        DATA / "DIAG9_GRAPH_row2599_factor_states.npz", allow_pickle=False
    ) as source:
        if str(source["format"].item()) != (
            "diag9-row2599-factor-state-sample-v1"
        ):
            raise AssertionError("wrong factor-state artifact format")
        if int(source["parent_index"].item()) != 2599:
            raise AssertionError("wrong factor-state parent")
        stored_representative = np.asarray(
            source["representative_occurrence_index"], dtype=np.uint32
        )
        stored_foursets = np.asarray(
            source["representative_fourset"], dtype=np.uint8
        )
        packed_states = np.asarray(
            source["chart_factor_sign_packed"], dtype=np.uint8
        )
    if (
        stored_representative.shape != (factor_count,)
        or not np.array_equal(stored_representative, representative)
        or stored_foursets.shape != (factor_count, 4)
        or not np.array_equal(stored_foursets, foursets_array[representative])
        or packed_states.shape != (178, (factor_count + 7) // 8)
    ):
        raise AssertionError("factor-state representative schema mismatch")
    factor_states = np.unpackbits(
        packed_states, axis=1, bitorder="little"
    )[:, :factor_count]
    empty_ids = np.asarray(sorted(empty_factors), dtype=np.int64)
    if np.any(factor_states[:, empty_ids] != factor_states[0, empty_ids]):
        raise AssertionError("a certified-empty factor changes sign in the sample")

    family_files = {
        "12_37": (
            DATA / "ninth_candidate_12_37_antichain.npz",
            DATA / "ninth_candidate_12_37_path.npz",
        ),
        "37_176": (
            DATA / "ninth_candidate_37_176_antichain.npz",
            DATA / "ninth_candidate_37_176_path.npz",
        ),
    }

    for name, (antichain_path, path_path) in family_files.items():
        antichain = np.load(antichain_path, allow_pickle=False)
        path = np.load(path_path, allow_pickle=False)
        expected_endpoints = {
            "12_37": (12, 37),
            "37_176": (37, 176),
        }[name]
        if str(antichain["format"].item()) != (
            f"ninth-candidate-{name.replace('_', '-')}-antichain-v1"
        ):
            raise AssertionError("wrong antichain artifact format")
        if str(path["format"].item()) != (
            f"ninth-candidate-{name.replace('_', '-')}-coordinate-path-v1"
        ):
            raise AssertionError("wrong path artifact format")
        if int(antichain["parent_index"].item()) != 2599 or int(
            path["parent_index"].item()
        ) != 2599:
            raise AssertionError("family artifact has the wrong parent")
        signatures = tuple(map(int, antichain["signature"]))
        endpoints = tuple(map(int, path["endpoint"]))
        if (
            signatures != tuple(map(int, path["signature"]))
            or len(signatures) != 9
            or endpoints != expected_endpoints
        ):
            raise AssertionError("family artifacts disagree")

        per_signature_literals = []
        per_signature_occurrences = []
        for signature in signatures:
            literals = {}
            occurrences = set()
            for occurrence_index, ((certificate_data, raw_sign), factor) in enumerate(
                zip(oriented, map(int, occurrence_factor), strict=True)
            ):
                if factor in empty_factors:
                    continue
                allowed_raw = aligned_literal(signature, certificate_data)
                if allowed_raw is None:
                    continue
                occurrences.add(occurrence_index)
                # D_occurrence / D_representative has this fixed sign.
                relative_orientation = raw_sign * int(
                    representative_raw_sign[factor]
                )
                allowed_representative = allowed_raw * relative_orientation
                previous = literals.setdefault(factor, allowed_representative)
                if previous != allowed_representative:
                    raise AssertionError(
                        "one nonempty signature receives conflicting factor sides"
                    )
            per_signature_literals.append(literals)
            per_signature_occurrences.append(occurrences)

        family_literals = {}
        for literals in per_signature_literals:
            for factor, orientation in literals.items():
                previous = family_literals.setdefault(factor, orientation)
                if previous != orientation:
                    raise AssertionError(
                        "committed nonempty family receives conflicting factor sides"
                    )

        # The committed path artifacts independently certify feasibility at
        # both endpoints.  Here we check that the exact factor-state artifact
        # realizes every forced literal at both of them.
        for endpoint in endpoints:
            for factor, orientation in family_literals.items():
                state_orientation = 1 if factor_states[endpoint, factor] else -1
                if state_orientation != orientation:
                    raise AssertionError("endpoint violates an aligned wall literal")

        active_occurrence_union = set().union(*per_signature_occurrences)
        active_factor_union = set(family_literals)
        if {
            int(occurrence_factor[index]) for index in active_occurrence_union
        } != active_factor_union:
            raise AssertionError("active occurrence/factor union mismatch")
        if active_factor_union & empty_factors:
            raise AssertionError("a certified-empty factor survived filtering")
        active_ids = np.asarray(sorted(active_factor_union), dtype=np.int64)
        if np.any(
            factor_states[endpoints[0], active_ids]
            != factor_states[endpoints[1], active_ids]
        ):
            raise AssertionError("feasible endpoints differ on an active factor")

        total_hamming = int(
            np.count_nonzero(
                factor_states[endpoints[0]] != factor_states[endpoints[1]]
            )
        )
        per_signature_counts = [len(literals) for literals in per_signature_literals]
        actual_counts = (
            len(active_occurrence_union),
            len(active_factor_union),
            factor_count - len(empty_factors) - len(active_factor_union),
            total_hamming,
        )
        expected = EXPECTED_FAMILY[name]
        if tuple(per_signature_counts) != expected["per_signature"]:
            raise AssertionError(f"{name} per-signature census changed")
        if actual_counts != expected["counts"]:
            raise AssertionError(f"{name} family census changed: {actual_counts}")

        print(name, "per-signature candidate active factors", per_signature_counts)
        print(
            name,
            "active occurrences/factors/effective inactive factors",
            len(active_occurrence_union),
            len(active_factor_union),
            factor_count - len(empty_factors) - len(active_factor_union),
        )
        print(
            name,
            "endpoint full-factor Hamming / active-factor Hamming",
            total_hamming,
            0,
        )
        digest = semantic_digest(
            name,
            signatures,
            per_signature_literals,
            per_signature_occurrences,
            empty_factors,
        )
        if digest != expected["digest"]:
            raise AssertionError(f"{name} semantic digest changed: {digest}")
        print(name, "SEMANTIC SHA256", digest)

    # Negative orientation canary: changing the auxiliary signature bit for
    # an aligned circuit reverses its allowed determinant side.
    for certificate_data, _ in oriented:
        circuit, coefficients, auxiliary, _ = certificate_data
        signature = 0
        for row_index, coefficient in zip(circuit, coefficients):
            if coefficient > 0:
                signature |= 1 << row_index
        first = aligned_literal(signature, certificate_data)
        second = aligned_literal(signature ^ (1 << auxiliary), certificate_data)
        if first is not None and second == -first:
            break
    else:
        raise AssertionError("aligned-side orientation canary failed")

    print("PASS: all seven input artifacts match their pinned SHA256 digests")
    print("PASS: all 84,840 occurrences retain every transported circuit identity")
    print("THEOREM: 8,916 row-2599 factors have certified-empty wall sections")
    print("PASS: remaining candidate factor universe has size 17,824")
    print("PASS: factor assignment, polynomial, unit, and state schemas")
    print("PASS: duplicate occurrences induce consistent global-factor orientations")
    print("THEOREM AUDIT: hard families need at most 3,539 and 3,638 candidate factors")
    print("SCOPE: exact active-sector input; no sector-connectivity claim")


if __name__ == "__main__":
    main()
