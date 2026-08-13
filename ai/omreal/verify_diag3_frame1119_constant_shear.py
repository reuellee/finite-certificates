#!/usr/bin/env python3
"""Exact replay of the 61 frame-1119 constant-coordinate shear minors."""

from __future__ import annotations

import hashlib
from itertools import permutations
import json
from pathlib import Path
import struct
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY as triples  # noqa: E402
import verify_residual_log_binomials as poly  # noqa: E402
import verify_diag3_projective_column_fiber_scan as column_scan  # noqa: E402


DATA = HERE / "data/DIAG3_frame1119_constant_shear.json"
OLD = HERE / "data/DIAG3_morse_unit_minor_certificates.bin"
DATA_SHA256 = "1cece61ff1a551faaeefc0062267e24266d264d9e19748d40fa5a74db9ce0be3"
OLD_MAGIC = b"D3MORSE1"
EXPECTED_PERMUTATION = (7, 3, 4, 5, 6, 0, 1, 2)
EXPECTED_RECORDS = 61
EXPECTED_SOURCE_COUNT = 1_819_850


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def old_originals() -> set[tuple[int, int, int]]:
    raw = OLD.read_bytes()
    header_format = "<8sIHHHIII"
    header_size = struct.calcsize(header_format)
    magic, count, *_rest = struct.unpack_from(header_format, raw)
    if magic != OLD_MAGIC or count != 65_550:
        raise AssertionError("old Morse certificate header changed")
    position = header_size
    result = set()
    fixed_format = "<HHHHHbB"
    fixed_size = struct.calcsize(fixed_format)
    for _ in range(count):
        first, second, third, _frame, _variables, _scalar, factor_count = (
            struct.unpack_from(fixed_format, raw, position)
        )
        position += fixed_size + factor_count
        result.add((first, second, third))
    if position != len(raw) or len(result) != count:
        raise AssertionError("old Morse certificate parsing changed")
    return result


def replay_source_membership(
    originals: set[tuple[int, int, int]],
    occurrences,
    occurrence_factor,
    polynomials,
    factor_occurrence,
) -> None:
    """Prove the 61 rows lie after every earlier positive layer.

    The original scanner's post-triangular source is not stored as a tracked
    multi-megabyte list.  For this 61-row positive artifact it is cheaper to
    replay its defining predicates directly: no common affine-three block in
    any S8 frame, minimum occurrence-union degree four, and failure of the
    exact triangular zero/unit feature test.
    """
    masks = column_scan.occurrence_complete_masks(
        occurrences, occurrence_factor, polynomials
    )
    unresolved = set(originals)
    unique_factors = tuple(sorted(set().union(*originals)))
    for permutation in permutations(range(8)):
        mapping = labeled.triple_map(permutation)
        transformed = {
            factor: labeled.transform_factor(
                factor, mapping, factor_occurrence, occurrence_factor
            )
            for factor in unique_factors
        }
        for original in tuple(unresolved):
            image = tuple(transformed[factor] for factor in original)
            if masks[image[0]] & masks[image[1]] & masks[image[2]]:
                raise AssertionError(
                    f"constant-shear row already affine in a reframe: {original}"
                )

    minimal = column_scan.minimal_incidence_masks(
        occurrences, occurrence_factor
    )
    feature_raw = column_scan.TRIANGULAR_FEATURES.read_bytes()
    if column_scan.sha256(column_scan.TRIANGULAR_FEATURES) != (
        column_scan.TRIANGULAR_FEATURE_DIGEST
    ):
        raise AssertionError("triangular-feature digest changed")
    factor_count, = struct.unpack_from("<I", feature_raw)
    if (
        factor_count != column_scan.FACTOR_COUNT
        or len(feature_raw) != 4 + 4 * factor_count
    ):
        raise AssertionError("bad triangular-feature artifact")
    features = tuple(
        struct.unpack_from("<HH", feature_raw, 4 + 4 * factor)
        for factor in range(factor_count)
    )
    for original in originals:
        degree, _partition = column_scan.best_union(original, minimal)
        if degree != 4:
            raise AssertionError(
                f"constant-shear row is not in union-degree four: {original}"
            )
        if column_scan.triangular_works(original, features):
            raise AssertionError(
                f"constant-shear row already has a triangular certificate: {original}"
            )
    print(
        "PASS post-triangular source predicates",
        len(originals),
        "all-reframe nonaffine/union4/nontriangular",
    )


def main() -> None:
    if sha256(DATA) != DATA_SHA256:
        raise AssertionError("constant-shear data digest changed")
    packed = json.loads(DATA.read_bytes())
    if packed.get("schema") != "diag3-frame1119-constant-shear-v1":
        raise AssertionError("bad constant-shear schema")
    permutation = tuple(packed["permutation"])
    records = packed["records"]
    if (
        permutation != EXPECTED_PERMUTATION
        or len(records) != EXPECTED_RECORDS
        or packed.get("source_live_count") != EXPECTED_SOURCE_COUNT
    ):
        raise AssertionError("constant-shear census changed")

    occurrences, occurrence_factor, polynomials = labeled.factor_polynomials()
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    mapping = labeled.triple_map(permutation)
    parents = labeled.parent_bracket_factors()
    original_parent = {
        label: poly.multiply(poly.constant(sign), factor)
        for label, factor, sign in parents
    }
    seen = set()
    total_terms = 0
    for record in records:
        original = tuple(record["original"])
        transformed = tuple(record["transformed"])
        left = tuple(record["left"])
        right = tuple(record["right"])
        sign = record["sign"]
        if original in seen or len(set(original)) != 3:
            raise AssertionError("duplicate constant-shear original")
        seen.add(original)
        replayed = tuple(
            labeled.transform_factor(
                factor, mapping, factor_occurrence, occurrence_factor
            )
            for factor in original
        )
        if replayed != transformed:
            raise AssertionError("constant-shear factor transport changed")
        if (
            tuple(sorted(set(left))) != left
            or tuple(sorted(set(right))) != right
            or len(set(left) & set(right)) != 2
            or sign not in (-1, 1)
        ):
            raise AssertionError("bad constant shear coordinates")
        residual = {
            row: polynomials[factor]
            for row, factor in enumerate(transformed)
        }
        left_minor = triples.jacobian_minor(
            residual, (0, 1, 2), left
        )
        right_minor = triples.jacobian_minor(
            residual, (0, 1, 2), right
        )
        shear_minor = poly.add(
            left_minor,
            right_minor if sign == 1 else poly.negative(right_minor),
        )
        product = poly.constant(record["scalar"])
        for label in record["brackets"]:
            product = poly.multiply(product, original_parent[label])
        if shear_minor != product:
            raise AssertionError("failed exact constant-shear identity")
        total_terms += len(shear_minor)

    overlap = seen & old_originals()
    if overlap:
        raise AssertionError(f"constant-shear records overlap old Morse set: {overlap}")
    replay_source_membership(
        seen, occurrences, occurrence_factor, polynomials, factor_occurrence
    )
    print("PASS frame1119 constant-shear exact identities", len(records))
    print("PASS distinct new original orbits", len(seen), "old overlap", len(overlap))
    print("PASS exact identity terms", total_terms)
    print("SAFE triple unit-minor count", 65_550 + len(seen))
    print("SCOPE one role frame and e_a+/-e_b shears; not an exhaustive GL9 scan")


if __name__ == "__main__":
    main()
