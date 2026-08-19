#!/usr/bin/env python3
"""Build the exact full-residue sequential two-coordinate affine census.

For each surviving union-degree-four factor triple, this verifier tries each
factor as the canonical parent-unit graph anchor, exhausts the stabilizer of
that anchor, and tests whether the other two graph-restricted equations are
jointly affine in the same pair of remaining coordinates.  Such a hit gives
a square affine two-variable fiber and hence excludes compact components.

The source is the pinned 1,897,733-row union-degree-four bucket.  The checker
removes the exact triangular, role-frame Morse, and frame-1119 constant-shear
closures before running the new test.  It can optionally export the exact
new residue for follow-up work.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from itertools import combinations
import json
import multiprocessing
from pathlib import Path
import struct
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as gradient  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY as triples  # noqa: E402
import verify_diag2_pivot_all_pair_fibers as fibers  # noqa: E402
import verify_diag3_frame1119_constant_shear as shear_scan  # noqa: E402
import verify_diag3_projective_column_fiber_scan as column_scan  # noqa: E402
import verify_residual_log_binomials as poly  # noqa: E402


CANONICAL_KINDS = (36, 37, 38, 39, 41, 42, 44, 46, 48, 49, 50, 51)
UNION4_COUNT = 1_897_733
UNION4_SHA256 = "54b03c31910de606b80f9dcc448ce3dde93063a8dbc3f2dbcaa7a02901df0303"
FINAL_INPUT_COUNT = 1_819_789
EXPECTED_GRAPH_CHARTS = 45
EXPECTED_NEW_CLOSED = 180_886
EXPECTED_NEW_RESIDUE = 1_638_903
EXPECTED_MASK_SEMANTIC = (
    "b5e5c3171da1acfd5c47d2ebb793ed1be8cced5f01275e05b68d9e51ef4c3f08"
)
EXPECTED_WITNESS_SEMANTIC = (
    "d27735abc8601c04b1114786d2a044af1acf8b99c253aee347ab101c4bb5368b"
)
EXPECTED_RESIDUE_SEMANTIC = (
    "d78a529cdb3e920b76b4b420114e24065c7e9e7cb2ef2a904b1a1e952c567270"
)
EXPECTED_RESIDUE_FILE_SHA256 = (
    "5ba2314c94ba115d5bf5e975e68412e3f4b44e2c65df51b757f6150a3352d4e1"
)
EXPECTED_CERTIFICATE_FILE_SHA256 = (
    "7e9ad80ae55c1f51dda7f7dc584dac8eefe41197124914cb83aab3cf0a2b719e"
)
EXPECTED_ANCHOR_COUNTS = {
    (36, 0): 134,
    (37, 0): 6,
    (39, 0): 535,
    (41, 0): 138,
    (42, 0): 1_314,
    (48, 0): 1_034,
    (49, 1): 77_360,
    (49, 5): 130,
    (50, 1): 91_831,
    (50, 3): 1_595,
    (51, 5): 6_470,
    (51, 6): 339,
}
MORSE = HERE / "data/DIAG3_morse_unit_minor_certificates.bin"
SHEAR = HERE / "data/DIAG3_frame1119_constant_shear.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def old_closures() -> set[tuple[int, int, int]]:
    if sha256(MORSE) != column_scan.MORSE_CERTIFICATE_DIGEST:
        raise AssertionError("Morse certificate digest changed")
    if sha256(SHEAR) != shear_scan.DATA_SHA256:
        raise AssertionError("constant-shear certificate digest changed")
    raw = MORSE.read_bytes()
    header_format = "<8sIHHHIII"
    position = struct.calcsize(header_format)
    magic, count, *_rest = struct.unpack_from(header_format, raw)
    if magic != column_scan.MORSE_MAGIC or count != column_scan.MORSE_CLOSED_COUNT:
        raise AssertionError("Morse header changed")
    fixed_format = "<HHHHHbB"
    fixed_size = struct.calcsize(fixed_format)
    result = set()
    for _ in range(count):
        first, second, third, _frame, _variables, _scalar, factor_count = (
            struct.unpack_from(fixed_format, raw, position)
        )
        position += fixed_size + factor_count
        result.add((first, second, third))
    if position != len(raw) or len(result) != count:
        raise AssertionError("Morse record parsing changed")
    packed = json.loads(SHEAR.read_text())
    result.update(tuple(record["original"]) for record in packed["records"])
    if len(result) != 65_611:
        raise AssertionError("old closure union changed")
    return result


def triangular_features() -> tuple[tuple[int, int], ...]:
    path = column_scan.TRIANGULAR_FEATURES
    if sha256(path) != column_scan.TRIANGULAR_FEATURE_DIGEST:
        raise AssertionError("triangular feature digest changed")
    raw = path.read_bytes()
    count, = struct.unpack_from("<I", raw)
    if count != column_scan.FACTOR_COUNT or len(raw) != 4 + 4 * count:
        raise AssertionError("bad triangular feature artifact")
    return tuple(
        struct.unpack_from("<HH", raw, 4 + 4 * factor)
        for factor in range(count)
    )


def jointly_affine_mask(polynomial, pivot: int) -> int:
    variables = tuple(index for index in range(9) if index != pivot)
    return sum(
        1 << bit
        for bit, (left, right) in enumerate(combinations(variables, 2))
        if all(monomial[left] + monomial[right] <= 1 for monomial in polynomial)
    )


_MASK_FACTOR_POLYNOMIAL = None


def _mask_worker(task):
    kind, pivot, slope, numerator = task
    row = []
    for polynomial in _MASK_FACTOR_POLYNOMIAL:
        restricted = fibers.graph_restrict(
            polynomial, pivot, slope, numerator
        )
        row.append(jointly_affine_mask(restricted, pivot))
    return kind, pivot, tuple(row)


def build_masks(factor_polynomial, canonical, workers: int | None):
    global _MASK_FACTOR_POLYNOMIAL
    parent_factors = labeled.parent_bracket_factors()
    masks = {}
    slopes = {}
    digest = hashlib.sha256(b"diag3-triple-sequential-affine-masks-v1\0")
    tasks = []
    for kind in CANONICAL_KINDS:
        anchor = factor_polynomial[canonical[kind]]
        pivots = []
        for pivot in range(9):
            if max((monomial[pivot] for monomial in anchor), default=0) > 1:
                continue
            if not gradient.derivative(anchor, pivot):
                continue
            slope, constant = fibers.pivot_split(anchor, pivot)
            certificate = triples.bracket_factorization(
                slope, parent_factors, depth=20
            )
            if certificate is None:
                continue
            if poly.add(
                poly.multiply(slope, poly.variable(pivot)), constant
            ) != anchor:
                raise AssertionError(f"type-{kind}/pivot-{pivot} graph split changed")
            pivots.append(pivot)
            slopes[(kind, pivot)] = certificate
            numerator = poly.negative(constant)
            tasks.append((kind, pivot, slope, numerator))
        if not pivots:
            raise AssertionError(f"type-{kind} has no parent-unit graph pivot")
    _MASK_FACTOR_POLYNOMIAL = factor_polynomial
    if len(tasks) != EXPECTED_GRAPH_CHARTS or len(slopes) != EXPECTED_GRAPH_CHARTS:
        raise AssertionError("canonical parent-unit graph chart count changed")
    if workers == 1:
        results = map(_mask_worker, tasks)
    else:
        process_count = workers or max(1, min(6, multiprocessing.cpu_count()))
        pool = multiprocessing.get_context("fork").Pool(process_count)
        results = pool.imap_unordered(_mask_worker, tasks)
    for kind, pivot, row in results:
        masks[(kind, pivot)] = row
        print(
            "MASK", kind, "pivot", pivot,
            "nonzero", sum(bool(mask) for mask in row),
            "bits", sum(mask.bit_count() for mask in row),
            flush=True,
        )
    if workers != 1:
        pool.close()
        pool.join()
    for kind, pivot in sorted(masks):
        for factor, mask in enumerate(masks[(kind, pivot)]):
            digest.update(struct.pack("<BBHI", kind, pivot, factor, mask))
    return masks, slopes, digest.hexdigest()


def transform_factor(factor, mapping, factor_occurrence, occurrence_factor):
    occurrence = factor_occurrence[factor]
    image = tuple(sorted(mapping[index] for index in occurrence))
    return occurrence_factor[image]


def find_witness(
    row,
    masks,
    canonical,
    stabilizers,
    anchor_alignments,
    factor_occurrence,
    occurrence_factor,
):
    for anchor_index, anchor in enumerate(row):
        others = tuple(row[index] for index in range(3) if index != anchor_index)
        for kind in CANONICAL_KINDS:
            mapping = anchor_alignments[kind].get(anchor)
            if mapping is None:
                continue
            if (
                transform_factor(
                    anchor, mapping, factor_occurrence, occurrence_factor
                )
                != canonical[kind]
            ):
                raise AssertionError("anchor alignment does not reach canonical factor")
            moved = tuple(
                transform_factor(
                    factor, mapping, factor_occurrence, occurrence_factor
                )
                for factor in others
            )
            for pivot in range(9):
                mask_row = masks.get((kind, pivot))
                if mask_row is None:
                    continue
                for symmetry_index, symmetry in enumerate(stabilizers[kind]):
                    targets = tuple(
                        transform_factor(
                            factor, symmetry, factor_occurrence, occurrence_factor
                        )
                        for factor in moved
                    )
                    common = mask_row[targets[0]] & mask_row[targets[1]]
                    if common:
                        pair_bit = (common & -common).bit_length() - 1
                        return (
                            anchor_index, kind, pivot, symmetry_index,
                            targets, pair_bit,
                        )
    return None


def coefficient_split(polynomial, left: int, right: int):
    """Return A_left, A_right, b for a jointly affine polynomial."""
    answer = [poly.constant(0), poly.constant(0), poly.constant(0)]
    for monomial, coefficient in polynomial.items():
        if monomial[left] + monomial[right] > 1:
            raise AssertionError("witness polynomial is not jointly affine")
        base = list(monomial)
        slot = 2
        if monomial[left]:
            base[left] = 0
            slot = 0
        elif monomial[right]:
            base[right] = 0
            slot = 1
        answer[slot] = poly.add(answer[slot], {tuple(base): coefficient})
    return tuple(answer)


def unit_determinant_certificate(polynomials, left: int, right: int, parents):
    first = coefficient_split(polynomials[0], left, right)
    second = coefficient_split(polynomials[1], left, right)
    determinant = poly.subtract(
        poly.multiply(first[0], second[1]),
        poly.multiply(first[1], second[0]),
    )
    return triples.bracket_factorization(determinant, parents, depth=30)


def scan(
    source: Path,
    export: Path | None,
    export_certificates: Path | None,
    workers: int | None,
    unit_determinant: bool,
):
    if sha256(source) != UNION4_SHA256:
        raise AssertionError(f"union-four source digest changed: {sha256(source)}")
    raw = source.read_bytes()
    count, = struct.unpack_from("<I", raw)
    if count != UNION4_COUNT or len(raw) != 4 + 6 * count:
        raise AssertionError("bad union-four source")

    occurrences, occurrence_factor, factor_polynomial = labeled.factor_polynomials()
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    canonical, anchor_alignments, stabilizers = labeled.canonical_anchor_alignments(
        occurrences, occurrence_factor, factor_occurrence
    )
    _representatives, _full_stabilizers, alignment, _factor_occurrence, _sizes = (
        labeled.factor_orbit_data(occurrences, occurrence_factor)
    )
    masks, slope_certificates, mask_digest = build_masks(
        factor_polynomial, canonical, workers
    )
    parent_factors = labeled.parent_bracket_factors()
    anchor_graph_data = {}
    for kind, pivot in slope_certificates:
        anchor = factor_polynomial[canonical[kind]]
        slope, constant = fibers.pivot_split(anchor, pivot)
        anchor_graph_data[(kind, pivot)] = slope, poly.negative(constant)
    features = triangular_features()
    closed = old_closures()

    final_input = 0
    new_closed = 0
    unit_determinant_closed = 0
    anchor_counts = Counter()
    kind_counts = Counter()
    residue_kind_counts = Counter()
    witness_digest = hashlib.sha256(b"diag3-triple-sequential-affine-witness-v1\0")
    unit_determinant_digest = hashlib.sha256(
        b"diag3-triple-sequential-affine-unit-determinant-v1\0"
    )
    residue_digest = hashlib.sha256()
    residue = []
    witness_records = []
    for index, unpacked in enumerate(struct.iter_unpack("<HHH", raw[4:]), 1):
        row = tuple(unpacked)
        if column_scan.triangular_works(row, features) or row in closed:
            continue
        final_input += 1
        row_kinds = tuple(sorted(alignment[factor][0] for factor in row))
        kind_counts[row_kinds] += 1
        witness = find_witness(
            row, masks, canonical, stabilizers, anchor_alignments,
            factor_occurrence, occurrence_factor,
        )
        if witness is None:
            residue.append(row)
            residue_kind_counts[row_kinds] += 1
            residue_digest.update(struct.pack("<HHH", *row))
        else:
            new_closed += 1
            anchor_index, kind, pivot, symmetry_index, targets, pair_bit = witness
            anchor_counts[(kind, pivot)] += 1
            witness_records.append((row, witness))
            if unit_determinant:
                variables = tuple(index for index in range(9) if index != pivot)
                coordinate_pairs = tuple(combinations(variables, 2))
                left, right = coordinate_pairs[pair_bit]
                slope, numerator = anchor_graph_data[(kind, pivot)]
                restricted = tuple(
                    fibers.graph_restrict(
                        factor_polynomial[target], pivot, slope, numerator
                    )
                    for target in targets
                )
                determinant_certificate = unit_determinant_certificate(
                    restricted, left, right, parent_factors
                )
                if determinant_certificate is not None:
                    unit_determinant_closed += 1
                    scalar, bracket_labels = determinant_certificate
                    unit_determinant_digest.update(
                        repr((row, witness, left, right, scalar, bracket_labels)).encode(
                            "ascii"
                        )
                    )
            witness_digest.update(
                struct.pack(
                    "<HHHBBBBHHB", *row, anchor_index, kind, pivot,
                    symmetry_index, *targets, pair_bit,
                )
            )
        if index % 250_000 == 0:
            print(
                "PROGRESS", index, "input", final_input,
                "closed", new_closed, "residue", len(residue),
                flush=True,
            )
    if final_input != FINAL_INPUT_COUNT:
        raise AssertionError(f"final input count changed: {final_input}")

    if export is not None:
        with export.open("wb") as output:
            output.write(struct.pack("<I", len(residue)))
            for row in residue:
                output.write(struct.pack("<HHH", *row))
        actual_residue = sha256(export)
        if actual_residue != EXPECTED_RESIDUE_FILE_SHA256:
            raise AssertionError(f"exported residue digest changed: {actual_residue}")
        print("WROTE", export, actual_residue)
    if export_certificates is not None:
        with export_certificates.open("wb") as output:
            output.write(b"D3SAFFN1")
            output.write(struct.pack("<I", len(witness_records)))
            for row, witness in witness_records:
                anchor_index, kind, pivot, symmetry_index, targets, pair_bit = witness
                output.write(
                    struct.pack(
                        "<HHHBBBBHHB", *row, anchor_index, kind, pivot,
                        symmetry_index, *targets, pair_bit,
                    )
                )
        actual_certificates = sha256(export_certificates)
        if actual_certificates != EXPECTED_CERTIFICATE_FILE_SHA256:
            raise AssertionError(
                f"exported certificate digest changed: {actual_certificates}"
            )
        print("WROTE_CERTIFICATES", export_certificates, actual_certificates)

    mask_semantic = mask_digest
    witness_semantic = witness_digest.hexdigest()
    residue_semantic = residue_digest.hexdigest()
    if (
        new_closed != EXPECTED_NEW_CLOSED
        or len(residue) != EXPECTED_NEW_RESIDUE
        or dict(anchor_counts) != EXPECTED_ANCHOR_COUNTS
        or mask_semantic != EXPECTED_MASK_SEMANTIC
        or witness_semantic != EXPECTED_WITNESS_SEMANTIC
        or residue_semantic != EXPECTED_RESIDUE_SEMANTIC
    ):
        raise AssertionError("sequential-affine census or semantic digest changed")

    print("PASS parent-unit graph slopes", slope_certificates)
    print("MASK_SEMANTIC", mask_semantic)
    print("FINAL_INPUT", final_input)
    print("NEW_SEQUENTIAL_AFFINE_CLOSED", new_closed)
    print(
        "UNIT_DETERMINANT_SUBSET",
        unit_determinant_closed if unit_determinant else "NOT_RUN",
    )
    print("NEW_RESIDUE", len(residue))
    print("ANCHOR_COUNTS", dict(sorted(anchor_counts.items())))
    print("INPUT_KIND_COUNTS", dict(sorted(kind_counts.items())))
    print("RESIDUE_KIND_COUNTS", dict(sorted(residue_kind_counts.items())))
    print("WITNESS_SEMANTIC", witness_semantic)
    if unit_determinant:
        print("UNIT_DETERMINANT_SEMANTIC", unit_determinant_digest.hexdigest())
    print("RESIDUE_SEMANTIC", residue_semantic)
    print(
        "THEOREM every newly closed row has a parent-unit graph anchor and "
        "a jointly affine two-equation/two-coordinate fiber"
    )
    print("CAVEAT any reported residue still requires another certificate")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--union4", type=Path, required=True)
    parser.add_argument("--export-residue", type=Path)
    parser.add_argument("--export-certificates", type=Path)
    parser.add_argument("--workers", type=int)
    parser.add_argument(
        "--unit-determinant", action="store_true",
        help="also compute the optional stronger parent-unit determinant subset",
    )
    arguments = parser.parse_args()
    scan(
        arguments.union4,
        arguments.export_residue,
        arguments.export_certificates,
        arguments.workers,
        arguments.unit_determinant,
    )


if __name__ == "__main__":
    main()
