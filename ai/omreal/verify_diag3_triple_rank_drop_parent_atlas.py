#!/usr/bin/env python3
"""Exact sign-atlas audit for the diagonal-three rank-drop factor ``P``.

The two-pivot rank-drop calculation produces a primitive factor ``P``.
This verifier first checks the exact bracket decomposition

    P = -[1237][1378] F - [1236][2378] Q,
    F = [1248][3458] + [1258],
    Q = [1347][1258] + [1237][1248][3458].

It then exhausts the 2,604 realizable uniform rank-four oriented-matroid
parent types and all 40,320 S8 frames.  Every *unlabelled* parent type has a
frame in which both summands of ``F``, both summands of ``Q``, and finally
both summands of ``P`` have equal sign.  The bitset atlas is replayed
independently from every stored integer realization matrix.

That existential reframe is not a hard-canary orbit theorem: the selected
factor triple has trivial S8 stabilizer, so changing frame generally changes
the labelled parent/triple pair.  The full frame census pins this limitation
and leaves ``P=0`` as an open branch.  The calculation is an exact positive
sign subatlas and an exact no-go for promoting its union to a global proof.
"""

from __future__ import annotations

import hashlib
from itertools import combinations, permutations
import json
from fractions import Fraction
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY as triples  # noqa: E402
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import explore_diag3_triple_hypersurface_groebner as chart  # noqa: E402
import verify_diag3_triple_boundary_stratification as boundary  # noqa: E402
from verify_diag3_triple_two_pivot_rank_drop import (  # noqa: E402
    EXPECTED_P,
    scale,
)


CATALOG = HERE / "certs_4_8.jsonl"
EXPECTED_RECORDS = 2_628
EXPECTED_REALIZABLE = 2_604
EXPECTED_FRAMES_SCANNED = 199
EXPECTED_WITNESS_FRAMES = 123
EXPECTED_LAST_FRAME = (0, 1, 3, 6, 4, 2, 5, 7)
EXPECTED_ATLAS_DIGEST = "98eca8e101e69de8812879c1ccd566d2a14300ae07a597084e644e1ba8d601b0"
EXPECTED_RAW_PRESENTATIONS = 104_993_280
EXPECTED_SIGN_CERTIFIED = 17_105_952
EXPECTED_FRAME_MINIMUM = 233
EXPECTED_FRAME_MAXIMUM = 693
EXPECTED_BEST_FRAME = (1, 2, 3, 7, 4, 0, 5, 6)
EXPECTED_FRAME_CENSUS_DIGEST = (
    "88b75dc54f3c89bff71899b960534c0bd6199484c67c362917d74e393f97d4dd"
)
PRESENTATION = (5_563, 16_134, 19_284)

# The source catalog uses reverse-lexicographic (colexicographic) basis order.
BASES = tuple(
    sorted(combinations(range(8), 4), key=lambda basis: tuple(reversed(basis)))
)
BASIS_INDEX = {basis: index for index, basis in enumerate(BASES)}
NEEDED_LABELS = (
    "1236",
    "1237",
    "1248",
    "1258",
    "1347",
    "1378",
    "2378",
    "3458",
)


def negative_parity(values):
    return bool(
        sum(
            values[left] > values[right]
            for left in range(len(values))
            for right in range(left + 1, len(values))
        )
        & 1
    )


def determinant(matrix):
    size = len(matrix)
    answer = 0
    for order in permutations(range(size)):
        product = -1 if negative_parity(order) else 1
        for row, column in enumerate(order):
            product *= matrix[row][column]
        answer += product
    return answer


def ordered_minor(matrix, columns):
    return determinant(
        [[matrix[row][column] for column in columns] for row in range(4)]
    )


def raw_negative_bitset(negative_by_basis, ordered_columns):
    basis = tuple(sorted(ordered_columns))
    return negative_by_basis[BASIS_INDEX[basis]] ^ (
        ((1 << EXPECTED_REALIZABLE) - 1) if negative_parity(ordered_columns) else 0
    )


def normalized_sign_bitsets(negative_by_basis, frame):
    """Return negative-sign bitsets after normalizing ``frame[:5]``."""

    all_rows = (1 << EXPECTED_REALIZABLE) - 1
    d_sign = raw_negative_bitset(negative_by_basis, frame[:4])
    x_signs = tuple(
        raw_negative_bitset(
            negative_by_basis,
            frame[:column] + (frame[4],) + frame[column + 1 : 4],
        )
        ^ d_sign
        for column in range(4)
    )
    gauge_sign = d_sign
    for sign in x_signs:
        gauge_sign ^= sign

    answer = {}
    for label in NEEDED_LABELS:
        positions = tuple(int(character) - 1 for character in label)
        sign = gauge_sign ^ raw_negative_bitset(
            negative_by_basis, tuple(frame[position] for position in positions)
        )
        for position in positions:
            if position < 4:
                sign ^= x_signs[position]
        answer[label] = sign & all_rows
    return answer


def equality_rows(left, right, all_rows):
    return all_rows ^ (left ^ right)


def certified_rows(signs, all_rows):
    f_left = signs["1248"] ^ signs["3458"]
    f_right = signs["1258"]
    q_left = signs["1347"] ^ signs["1258"]
    q_right = signs["1237"] ^ signs["1248"] ^ signs["3458"]
    first_p = signs["1237"] ^ signs["1378"] ^ f_left
    second_p = signs["1236"] ^ signs["2378"] ^ q_left
    return (
        equality_rows(f_left, f_right, all_rows)
        & equality_rows(q_left, q_right, all_rows)
        & equality_rows(first_p, second_p, all_rows)
    )


def sign(value):
    if not value:
        raise AssertionError("uniform catalog acquired a zero determinant")
    return value < 0


def normalized_matrix(matrix, frame):
    """Construct the exact frame chart independently by Cramer's rule."""

    basis = frame[:4]
    replacements = tuple(
        ordered_minor(
            matrix,
            basis[:column] + (frame[4],) + basis[column + 1 :],
        )
        for column in range(4)
    )
    if any(value == 0 for value in replacements):
        raise AssertionError("the first five frame columns are not uniform")

    columns = []
    for position, actual_column in enumerate(frame):
        if position < 4:
            column = [Fraction(0) for _ in range(4)]
            column[position] = Fraction(1)
        elif position == 4:
            column = [Fraction(1) for _ in range(4)]
        else:
            column = [
                Fraction(
                    ordered_minor(
                        matrix,
                        basis[:row] + (actual_column,) + basis[row + 1 :],
                    ),
                    replacements[row],
                )
                for row in range(4)
            ]
        columns.append(column)
    return tuple(tuple(column) for column in columns)


def chart_minor(normalized, label):
    positions = tuple(int(character) - 1 for character in label)
    return determinant(
        [[normalized[column][row] for column in positions] for row in range(4)]
    )


def verify_polynomial_identities():
    walls = boundary.parent_wall_map()
    one = {boundary.ZERO: 1}
    c = boundary.coordinate(2)
    d = boundary.coordinate(3)
    f = boundary.coordinate(5)
    g = boundary.coordinate(6)
    h = boundary.coordinate(7)
    i = boundary.coordinate(8)
    g_minus_one = boundary.subtract(g, one)
    h_minus_i = boundary.subtract(h, i)
    i_minus_f = boundary.subtract(i, f)

    factor_f = boundary.add(
        boundary.multiply(walls["1248"], walls["3458"]),
        walls["1258"],
    )
    coordinate_f = boundary.add(boundary.multiply(h, g_minus_one), h_minus_i)
    if factor_f != coordinate_f:
        raise AssertionError("the subtraction-free F bracket identity changed")

    factor_q = boundary.add(
        boundary.multiply(walls["1347"], walls["1258"]),
        boundary.multiply(
            boundary.multiply(walls["1237"], walls["1248"]),
            walls["3458"],
        ),
    )
    coordinate_q = boundary.add(
        boundary.multiply(d, h_minus_i),
        boundary.multiply(boundary.multiply(f, h), g_minus_one),
    )
    if factor_q != coordinate_q:
        raise AssertionError("the subtraction-free Q bracket identity changed")
    if boundary.subtract(factor_q, boundary.multiply(f, factor_f)) != (
        boundary.multiply(walls["1357"], walls["1258"])
    ):
        raise AssertionError("the P=0 transversality identity changed")

    reconstructed_p = boundary.add(
        scale(
            boundary.multiply(
                boundary.multiply(f, walls["1378"]), factor_f
            ),
            -1,
        ),
        boundary.multiply(boundary.multiply(c, i_minus_f), factor_q),
    )
    factor_p = boundary.add(
        scale(
            boundary.multiply(
                boundary.multiply(walls["1237"], walls["1378"]),
                factor_f,
            ),
            -1,
        ),
        scale(
            boundary.multiply(
                boundary.multiply(walls["1236"], walls["2378"]),
                factor_q,
            ),
            -1,
        ),
    )
    if reconstructed_p != EXPECTED_P or factor_p != EXPECTED_P:
        raise AssertionError("the exact P decomposition changed")

    generators, _unit_factors = chart.build_exact_system(())
    _constant, slope = boundary.split_linear(generators[2], 4)
    if any(coefficient % 2 for coefficient in slope.values()):
        raise AssertionError("the E_e slope lost its content two")
    half_slope = {
        monomial: coefficient // 2 for monomial, coefficient in slope.items()
    }
    primitive_l = triples.exact_divide(half_slope, i_minus_f)
    if primitive_l is None:
        raise AssertionError("the primitive L factor changed")
    coefficients_h = boundary.split_by_degree(primitive_l, 7)
    if len(coefficients_h) != 3:
        raise AssertionError("L is no longer quadratic in h")
    expected_leading = scale(
        boundary.multiply(
            boundary.multiply(
                boundary.multiply(walls["1236"], walls["1348"]),
                boundary.multiply(walls["2356"], walls["1357"]),
            ),
            walls["2378"],
        ),
        -1,
    )
    if coefficients_h[2] != expected_leading:
        raise AssertionError("the parent-unit leading coefficient of L changed")


def load_catalog():
    records = [
        json.loads(line)
        for line in CATALOG.read_text(encoding="ascii").splitlines()
        if line
    ]
    if len(records) != EXPECTED_RECORDS:
        raise AssertionError("the rank-four catalog size changed")
    realizable = []
    negative_by_basis = [0] * len(BASES)
    for source_index, record in enumerate(records):
        if record.get("n") != 8 or record.get("r") != 4:
            raise AssertionError("the catalog rank or ground-set size changed")
        chirotope = record.get("chi", "")
        if len(chirotope) != len(BASES) or set(chirotope) - {"+", "-"}:
            raise AssertionError("the catalog is no longer uniform rank four")
        if record.get("verdict") != "REALIZABLE":
            continue
        matrix = record.get("matrix")
        if (
            not isinstance(matrix, list)
            or len(matrix) != 4
            or any(not isinstance(row, list) or len(row) != 8 for row in matrix)
        ):
            raise AssertionError("a realizable record lost its 4x8 matrix")
        parent_index = len(realizable)
        realizable.append((source_index, chirotope, matrix))
        for basis_index, character in enumerate(chirotope):
            if character == "-":
                negative_by_basis[basis_index] |= 1 << parent_index
    if len(realizable) != EXPECTED_REALIZABLE:
        raise AssertionError("the realizable parent census changed")
    return realizable, tuple(negative_by_basis)


def verify_matrix_chirotopes(realizable):
    for _source_index, chirotope, matrix in realizable:
        actual = "".join(
            "-" if sign(ordered_minor(matrix, basis)) else "+" for basis in BASES
        )
        if actual != chirotope:
            raise AssertionError("a stored integer matrix no longer realizes chi")


def build_atlas(negative_by_basis):
    all_rows = (1 << EXPECTED_REALIZABLE) - 1
    covered = 0
    first_witness = [None] * EXPECTED_REALIZABLE
    frames_scanned = 0
    for frame in permutations(range(8)):
        frames_scanned += 1
        signs = normalized_sign_bitsets(negative_by_basis, frame)
        newly = certified_rows(signs, all_rows) & (all_rows ^ covered)
        while newly:
            low_bit = newly & -newly
            parent_index = low_bit.bit_length() - 1
            first_witness[parent_index] = frame
            newly ^= low_bit
        covered |= certified_rows(signs, all_rows)
        if covered == all_rows:
            last_frame = frame
            break
    else:
        raise AssertionError("the frame atlas no longer covers every parent")

    if (
        EXPECTED_FRAMES_SCANNED is not None
        and frames_scanned != EXPECTED_FRAMES_SCANNED
    ) or (EXPECTED_LAST_FRAME is not None and last_frame != EXPECTED_LAST_FRAME):
        raise AssertionError("the lexicographic frame stopping point changed")
    witness_frames = len(set(first_witness))
    if (
        EXPECTED_WITNESS_FRAMES is not None
        and witness_frames != EXPECTED_WITNESS_FRAMES
    ):
        raise AssertionError("the number of witness frames changed")
    if any(frame is None for frame in first_witness):
        raise AssertionError("a realizable parent has no witness frame")
    return tuple(first_witness), frames_scanned, witness_frames


def atlas_digest(realizable, first_witness):
    digest = hashlib.sha256(b"diag3-rank-drop-parent-atlas-v1\0")
    for (source_index, _chi, _matrix), frame in zip(realizable, first_witness):
        digest.update(f"{source_index}:".encode("ascii"))
        digest.update(bytes(frame))
    return digest.hexdigest()


def verify_triple_stabilizer():
    occurrences, occurrence_factor, _polynomials = labeled.factor_polynomials()
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    target = set(PRESENTATION)
    stabilizer = []
    for frame in permutations(range(8)):
        mapping = labeled.triple_map(frame)
        image = {
            labeled.transform_factor(
                factor, mapping, factor_occurrence, occurrence_factor
            )
            for factor in PRESENTATION
        }
        if image == target:
            stabilizer.append(frame)
    identity = tuple(range(8))
    if stabilizer != [identity]:
        raise AssertionError("the hard presentation stabilizer changed")


def full_frame_census(negative_by_basis):
    all_rows = (1 << EXPECTED_REALIZABLE) - 1
    byte_width = (EXPECTED_REALIZABLE + 7) // 8
    digest = hashlib.sha256(b"diag3-p-sign-frame-census-v1\0")
    certified_total = 0
    minimum = EXPECTED_REALIZABLE + 1
    maximum = -1
    best_frames = []
    frame_count = 0
    for frame in permutations(range(8)):
        frame_count += 1
        certified = certified_rows(
            normalized_sign_bitsets(negative_by_basis, frame), all_rows
        )
        digest.update(certified.to_bytes(byte_width, "little"))
        count = certified.bit_count()
        certified_total += count
        minimum = min(minimum, count)
        if count > maximum:
            maximum = count
            best_frames = [frame]
        elif count == maximum:
            best_frames.append(frame)

    raw_presentations = frame_count * EXPECTED_REALIZABLE
    semantic = digest.hexdigest()
    if (
        raw_presentations != EXPECTED_RAW_PRESENTATIONS
        or certified_total != EXPECTED_SIGN_CERTIFIED
        or minimum != EXPECTED_FRAME_MINIMUM
        or maximum != EXPECTED_FRAME_MAXIMUM
        or best_frames != [EXPECTED_BEST_FRAME]
        or semantic != EXPECTED_FRAME_CENSUS_DIGEST
    ):
        raise AssertionError("the full P sign-frame census changed")
    return raw_presentations, certified_total, minimum, maximum, semantic


def replay_witnesses(realizable, negative_by_basis, first_witness):
    all_rows = (1 << EXPECTED_REALIZABLE) - 1
    cached_signs = {}
    for parent_index, ((_source_index, _chi, matrix), frame) in enumerate(
        zip(realizable, first_witness)
    ):
        normalized = normalized_matrix(matrix, frame)
        direct_signs = {
            label: sign(chart_minor(normalized, label)) for label in NEEDED_LABELS
        }
        if frame not in cached_signs:
            cached_signs[frame] = normalized_sign_bitsets(negative_by_basis, frame)
        bit_signs = {
            label: bool(cached_signs[frame][label] & (1 << parent_index))
            for label in NEEDED_LABELS
        }
        if direct_signs != bit_signs:
            raise AssertionError("integer-matrix frame replay disagrees with chi")
        singleton = {
            label: all_rows if value else 0 for label, value in direct_signs.items()
        }
        if certified_rows(singleton, all_rows) != all_rows:
            raise AssertionError("a stored witness frame lost the P sign certificate")


def main():
    verify_polynomial_identities()
    realizable, negative_by_basis = load_catalog()
    verify_matrix_chirotopes(realizable)
    first_witness, frames_scanned, witness_frames = build_atlas(negative_by_basis)
    digest = atlas_digest(realizable, first_witness)
    if EXPECTED_ATLAS_DIGEST is not None and digest != EXPECTED_ATLAS_DIGEST:
        raise AssertionError("the parent-atlas semantic digest changed")
    replay_witnesses(realizable, negative_by_basis, first_witness)
    verify_triple_stabilizer()
    raw, certified, minimum, maximum, frame_digest = full_frame_census(
        negative_by_basis
    )

    print("PASS P = -[1237][1378]F - [1236][2378]Q")
    print("PASS F and Q are two-term subtraction-free bracket sums")
    print("PASS Q-fF=[1357][1258], so P=0 is a transverse c graph")
    print("PASS L is quadratic in h with parent-unit leading coefficient")
    print(f"PASS {len(realizable)} realizable UOM(4,8) parent types covered")
    print(
        f"PASS {frames_scanned} lexicographic frames scanned; "
        f"{witness_frames} first-witness frames"
    )
    print(f"ATLAS_SHA256 {digest}")
    print("PASS all witnesses replayed from the stored integer matrices")
    print("PASS the hard presentation has trivial S8 stabilizer")
    print(
        f"CENSUS {certified}/{raw} raw frame-parent presentations certified; "
        f"per-frame range {minimum}..{maximum}"
    )
    print(f"FRAME_CENSUS_SHA256 {frame_digest}")
    print("NO-GO existential parent reframing does not eliminate P=0 globally")
    print("FRONTIER P=0 and quadratic L=0 rank-drop branches remain")
    print("SCOPE exact positive sign subatlas; no triple orbit is closed")


if __name__ == "__main__":
    main()
