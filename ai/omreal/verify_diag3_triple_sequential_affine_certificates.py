#!/usr/bin/env python3
"""Independent exact replay of sequential-affine triple certificates.

This verifier consumes the compact witness stream produced by
``build_diag3_triple_sequential_affine_scan.py``.  It does not use that
scanner's precomputed masks.  For every record it independently reconstructs
the label action, aligns the stated factor to the stated canonical occurrence
formula, checks the exact parent-unit graph slope, performs the graph
substitution over Z, and verifies joint affinity of both residual equations
in the recorded two-coordinate fiber.
"""

from __future__ import annotations

import argparse
import hashlib
from itertools import combinations, permutations
import json
from pathlib import Path
import struct
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
DEFAULT_CERTIFICATE = (
    HERE / "data" / "DIAG3_triple_sequential_affine_certificates.bin"
)

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY as triples  # noqa: E402
import verify_diag2_pivot_all_pair_fibers as fibers  # noqa: E402
import verify_residual_log_binomials as poly  # noqa: E402


MAGIC = b"D3SAFFN1"
EXPECTED_COUNT = 180_886
EXPECTED_SHA256 = "7e9ad80ae55c1f51dda7f7dc584dac8eefe41197124914cb83aab3cf0a2b719e"
EXPECTED_SEMANTIC = "d27735abc8601c04b1114786d2a044af1acf8b99c253aee347ab101c4bb5368b"
RECORD_FORMAT = "<HHHBBBBHHB"
UNION4_COUNT = 1_897_733
UNION4_SHA256 = "54b03c31910de606b80f9dcc448ce3dde93063a8dbc3f2dbcaa7a02901df0303"
FINAL_INPUT_COUNT = 1_819_789
FINAL_RESIDUE_COUNT = 1_638_903
TRIANGULAR_SHA256 = "7fae9da26cf7391d2dc3b00e55faabdf4556d4badc9a2f8c4ace3ecc29d7f136"
MORSE_SHA256 = "afe01d6d94bc4b8ce133cbe0d14ceb01d9dd72514f9ed7a59b73d5f6b4299734"
SHEAR_SHA256 = "1cece61ff1a551faaeefc0062267e24266d264d9e19748d40fa5a74db9ce0be3"
TRIANGULAR = HERE / "data" / "DIAG3_triangular_features.bin"
MORSE = HERE / "data" / "DIAG3_morse_unit_minor_certificates.bin"
SHEAR = HERE / "data" / "DIAG3_frame1119_constant_shear.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def transform_factor(factor, mapping, factor_occurrence, occurrence_factor):
    occurrence = factor_occurrence[factor]
    image = tuple(sorted(mapping[index] for index in occurrence))
    return occurrence_factor[image]


def triangular_features() -> tuple[tuple[int, int], ...]:
    if sha256(TRIANGULAR) != TRIANGULAR_SHA256:
        raise AssertionError("triangular-feature SHA-256 changed")
    raw = TRIANGULAR.read_bytes()
    count, = struct.unpack_from("<I", raw)
    if count != 26_740 or len(raw) != 4 + 4 * count:
        raise AssertionError("bad triangular-feature artifact")
    return tuple(
        struct.unpack_from("<HH", raw, 4 + 4 * factor)
        for factor in range(count)
    )


def triangular_works(row, features) -> bool:
    rows = [features[factor] for factor in row]
    for first_row, second_row, third_row in permutations(range(3)):
        zero0, unit0 = rows[first_row]
        zero1, unit1 = rows[second_row]
        zero2, unit2 = rows[third_row]
        first = unit0 & zero1 & zero2
        second = unit1 & zero2
        third = unit2
        if not first or not second or not third:
            continue
        if (
            (first | second).bit_count() >= 2
            and (first | third).bit_count() >= 2
            and (second | third).bit_count() >= 2
            and (first | second | third).bit_count() >= 3
        ):
            return True
    return False


def old_closures() -> set[tuple[int, int, int]]:
    if sha256(MORSE) != MORSE_SHA256 or sha256(SHEAR) != SHEAR_SHA256:
        raise AssertionError("prerequisite closure artifact changed")
    raw = MORSE.read_bytes()
    header_format = "<8sIHHHIII"
    position = struct.calcsize(header_format)
    magic, count, *_rest = struct.unpack_from(header_format, raw)
    if magic != b"D3MORSE1" or count != 65_550:
        raise AssertionError("Morse header changed")
    fixed_format = "<HHHHHbB"
    fixed_size = struct.calcsize(fixed_format)
    answer = set()
    for _ in range(count):
        first, second, third, _frame, _variables, _scalar, factor_count = (
            struct.unpack_from(fixed_format, raw, position)
        )
        position += fixed_size + factor_count
        answer.add((first, second, third))
    if position != len(raw) or len(answer) != count:
        raise AssertionError("Morse record parsing changed")
    packed = json.loads(SHEAR.read_text())
    answer.update(tuple(record["original"]) for record in packed["records"])
    if len(answer) != 65_611:
        raise AssertionError("old closure union changed")
    return answer


def verify_source_membership(source: Path, certified) -> None:
    if sha256(source) != UNION4_SHA256:
        raise AssertionError("union-degree-four SHA-256 changed")
    raw = source.read_bytes()
    count, = struct.unpack_from("<I", raw)
    if count != UNION4_COUNT or len(raw) != 4 + 6 * count:
        raise AssertionError("bad union-degree-four source")
    features = triangular_features()
    closed = old_closures()
    final_count = found = 0
    source_rows = set()
    for row in struct.iter_unpack("<HHH", raw[4:]):
        if row in source_rows:
            raise AssertionError("union-degree-four source contains a duplicate")
        source_rows.add(row)
        if triangular_works(row, features) or row in closed:
            continue
        final_count += 1
        found += row in certified
    if len(source_rows) != UNION4_COUNT:
        raise AssertionError("union-degree-four source uniqueness changed")
    if final_count != FINAL_INPUT_COUNT or found != len(certified):
        raise AssertionError(
            f"source partition changed: final={final_count}, certified={found}"
        )
    if final_count - found != FINAL_RESIDUE_COUNT:
        raise AssertionError("sequential-affine complement count changed")
    print(
        "PASS independent exact source membership/partition",
        UNION4_COUNT, final_count, found, final_count - found,
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "certificate",
        type=Path,
        nargs="?",
        default=DEFAULT_CERTIFICATE,
        help="compact witness stream (defaults to the tracked certificate)",
    )
    parser.add_argument(
        "--union4",
        type=Path,
        help="optional pinned union-degree-four source for independent partition replay",
    )
    arguments = parser.parse_args()
    actual = sha256(arguments.certificate)
    if actual != EXPECTED_SHA256:
        raise AssertionError(f"certificate SHA-256 changed: {actual}")
    raw = arguments.certificate.read_bytes()
    magic = raw[:8]
    count, = struct.unpack_from("<I", raw, 8)
    record_size = struct.calcsize(RECORD_FORMAT)
    if (
        magic != MAGIC
        or count != EXPECTED_COUNT
        or len(raw) != 12 + record_size * count
    ):
        raise AssertionError("bad sequential-affine certificate header")

    occurrences, occurrence_factor, factor_polynomial = labeled.factor_polynomials()
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    canonical, anchor_alignments, stabilizers = labeled.canonical_anchor_alignments(
        occurrences, occurrence_factor, factor_occurrence
    )
    parent_factors = labeled.parent_bracket_factors()
    graph_cache = {}
    semantic = hashlib.sha256(b"diag3-triple-sequential-affine-witness-v1\0")
    seen = set()
    anchor_counts = {}
    position = 12
    for number in range(count):
        (
            first, second, third, anchor_index, kind, pivot,
            symmetry_index, target0, target1, pair_bit,
        ) = struct.unpack_from(RECORD_FORMAT, raw, position)
        position += record_size
        row = first, second, third
        if row in seen or len(set(row)) != 3:
            raise AssertionError(f"bad source row at certificate {number}")
        seen.add(row)
        if not 0 <= anchor_index < 3 or kind not in canonical:
            raise AssertionError(f"bad anchor metadata at certificate {number}")
        mapping = anchor_alignments[kind].get(row[anchor_index])
        if mapping is None:
            raise AssertionError(f"anchor does not lie in type-{kind} orbit")
        if (
            transform_factor(
                row[anchor_index], mapping, factor_occurrence, occurrence_factor
            )
            != canonical[kind]
        ):
            raise AssertionError(
                f"anchor alignment does not reach canonical factor at certificate {number}"
            )
        others = tuple(row[index] for index in range(3) if index != anchor_index)
        moved = tuple(
            transform_factor(factor, mapping, factor_occurrence, occurrence_factor)
            for factor in others
        )
        if not 0 <= symmetry_index < len(stabilizers[kind]):
            raise AssertionError(f"bad stabilizer index at certificate {number}")
        symmetry = stabilizers[kind][symmetry_index]
        targets = tuple(
            transform_factor(factor, symmetry, factor_occurrence, occurrence_factor)
            for factor in moved
        )
        if targets != (target0, target1):
            raise AssertionError(f"target transport changed at certificate {number}")

        key = kind, pivot
        if key not in graph_cache:
            anchor = factor_polynomial[canonical[kind]]
            if max((monomial[pivot] for monomial in anchor), default=0) > 1:
                raise AssertionError(f"type-{kind} is not affine in pivot {pivot}")
            slope, constant = fibers.pivot_split(anchor, pivot)
            if poly.add(poly.multiply(slope, poly.variable(pivot)), constant) != anchor:
                raise AssertionError(f"type-{kind} graph reconstruction changed")
            slope_certificate = triples.bracket_factorization(
                slope, parent_factors, depth=20
            )
            if slope_certificate is None:
                raise AssertionError(f"type-{kind}/pivot-{pivot} slope is not a unit")
            graph_cache[key] = slope, poly.negative(constant)
        slope, numerator = graph_cache[key]
        variables = tuple(index for index in range(9) if index != pivot)
        coordinate_pairs = tuple(combinations(variables, 2))
        if not 0 <= pair_bit < len(coordinate_pairs):
            raise AssertionError(f"bad coordinate-pair bit at certificate {number}")
        left, right = coordinate_pairs[pair_bit]
        for target in targets:
            restricted = fibers.graph_restrict(
                factor_polynomial[target], pivot, slope, numerator
            )
            if not restricted or any(
                monomial[left] + monomial[right] > 1
                for monomial in restricted
            ):
                raise AssertionError(
                    f"false sequential-affine witness at certificate {number}"
                )
        witness = (
            anchor_index, kind, pivot, symmetry_index, targets, pair_bit
        )
        semantic.update(
            struct.pack(
                RECORD_FORMAT, *row, anchor_index, kind, pivot,
                symmetry_index, *targets, pair_bit,
            )
        )
        anchor_counts[key] = anchor_counts.get(key, 0) + 1
        if (number + 1) % 20_000 == 0:
            print("PASS exact certificates", number + 1, "/", count, flush=True)

    digest = semantic.hexdigest()
    if digest != EXPECTED_SEMANTIC:
        raise AssertionError(f"witness semantic digest changed: {digest}")
    if arguments.union4 is not None:
        verify_source_membership(arguments.union4, seen)
    else:
        print("PROVENANCE source membership replay requires optional --union4")
    print("PASS independent sequential-affine certificates", count, actual)
    print("PASS exact parent-unit graph anchors", len(graph_cache), sorted(graph_cache))
    print("PASS anchor counts", dict(sorted(anchor_counts.items())))
    print("SEMANTIC", digest)
    print(
        "THEOREM each record gives an open parent-unit graph domain and an "
        "exact two-equation/two-coordinate affine fiber"
    )


if __name__ == "__main__":
    main()
