#!/usr/bin/env python3
"""Independent exact replay of the primitive final-direction triple layer.

After two graph substitutions whose slopes are products of parent-bracket
units, the last equation is affine along a primitive direction
``e_i + sign*e_j``.  The checker reconstructs the full cleared last
polynomial over Z and proves this by an exact vanishing second directional
derivative.  The corresponding two-coordinate change is unimodular.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from pathlib import Path
import struct
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as gradient  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY as triples  # noqa: E402
import verify_diag2_pivot_all_pair_fibers as fibers  # noqa: E402
import verify_diag3_triple_direct_final_affinity as direct  # noqa: E402
import verify_residual_log_binomials as poly  # noqa: E402


CERTIFICATE = (
    HERE / "data/DIAG3_triple_primitive_final_direction_certificates.bin"
)
MAGIC = b"D3PFDIR1"
RECORD_FORMAT = "<HHHBBBBBBBBbHHbB"
COUNT = 23
CERTIFICATE_BYTES = 711
CERTIFICATE_SHA256 = (
    "af0d1964840975e324d2c0181e732142ccd4e35c88ab4fc2702b6c70e6389bde"
)
SEMANTIC_SHA256 = (
    "8917815ae6b4c65c83b74e09d5ee8f3f18f237d9bd493fce04094ca3d8f0f055"
)
ROW_SEMANTIC_SHA256 = (
    "a1af2ac4e6ff2b9e9037ebc8f9bf969485acda4ce5f50adaeb0ab24f96a4e971"
)
DIRECT_CERTIFICATE_SHA256 = (
    "6ed192d1dd2f814ae914349ec2dbcc654ffb663669b85f1b289fa37feb147f26"
)
DIRECT_UNION_COUNT = 58_673
EXPECTED_PIVOT_COUNTS = {5: 6, 6: 17}
EXPECTED_FIRST_SLOPES = {
    5: (1, ("1456", "2468")),
    6: (-1, ("1236", "2467")),
}
EXPECTED_SLOPE_KEYS = 8
EXPECTED_FINAL_KEYS = 23
SOURCE_COUNT = 1_221_055
SOURCE_BYTES = 7_326_334
SOURCE_SHA256 = (
    "bdd29e7647a99429f38c7bc20e9e5b9b514dccf7cbf57f9cd9b1b36fec7e7d92"
)
AFTER_DIRECT_AND_PRIMITIVE_COUNT = 1_162_359
AFTER_DIRECT_AND_PRIMITIVE_SEMANTIC = (
    "6c477d76ec0173ab340db4c9f5b783d3638393d0714e58440bae35b143b02b6a"
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def transform_factor(factor, mapping, factor_occurrence, occurrence_factor):
    occurrence = factor_occurrence[factor]
    image = tuple(sorted(mapping[index] for index in occurrence))
    return occurrence_factor[image]


def parse_certificate():
    """Return the pinned rows and decoded records for overlap consumers."""

    if CERTIFICATE.stat().st_size != CERTIFICATE_BYTES:
        raise AssertionError("primitive-final certificate byte count changed")
    actual = sha256(CERTIFICATE)
    if actual != CERTIFICATE_SHA256:
        raise AssertionError(
            f"primitive-final certificate SHA-256 changed: {actual}"
        )
    raw = CERTIFICATE.read_bytes()
    if raw[: len(MAGIC)] != MAGIC:
        raise AssertionError("bad primitive-final certificate magic")
    count, = struct.unpack_from("<I", raw, len(MAGIC))
    if count != COUNT:
        raise AssertionError("primitive-final certificate count changed")
    fixed_size = struct.calcsize(RECORD_FORMAT)
    position = len(MAGIC) + 4
    semantic = hashlib.sha256(
        b"diag3-triple-primitive-final-direction-v1\0"
    )
    records = []
    rows = set()
    for number in range(count):
        start = position
        fields = struct.unpack_from(RECORD_FORMAT, raw, position)
        position += fixed_size
        label_count = fields[-1]
        labels = tuple(
            raw[position + 4 * index:position + 4 * (index + 1)].decode(
                "ascii"
            )
            for index in range(label_count)
        )
        position += 4 * label_count
        semantic.update(raw[start:position])
        row = fields[:3]
        if row in rows or len(set(row)) != 3:
            raise AssertionError(f"bad row at primitive record {number}")
        rows.add(row)
        records.append((fields, labels))
    if position != len(raw):
        raise AssertionError("trailing primitive-final certificate bytes")
    if semantic.hexdigest() != SEMANTIC_SHA256:
        raise AssertionError("primitive-final semantic changed")
    row_digest = hashlib.sha256(
        b"".join(struct.pack("<HHH", *row) for row in sorted(rows))
    ).hexdigest()
    if row_digest != ROW_SEMANTIC_SHA256:
        raise AssertionError("primitive-final row semantic changed")
    return tuple(records), rows


def second_directional(polynomial, first, second, sign):
    """Return ``(D_first + sign D_second)^2 polynomial`` exactly over Z."""

    derivative = poly.add(
        gradient.derivative(polynomial, first),
        gradient.derivative(polynomial, second)
        if sign == 1
        else poly.negative(gradient.derivative(polynomial, second)),
    )
    return poly.add(
        gradient.derivative(derivative, first),
        gradient.derivative(derivative, second)
        if sign == 1
        else poly.negative(gradient.derivative(derivative, second)),
    )


def replay_exact(records):
    occurrences, occurrence_factor, factor_polynomial = labeled.factor_polynomials()
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    canonical, anchor_alignments, stabilizers = labeled.canonical_anchor_alignments(
        occurrences, occurrence_factor, factor_occurrence
    )
    parent_factors = labeled.parent_bracket_factors()
    raw_parents = {
        label: poly.multiply(poly.constant(sign), factor)
        for label, factor, sign in parent_factors
    }
    chart_cache = {}
    slope_keys = set()
    final_keys = set()
    pivot_counts = Counter()

    for number, (fields, labels) in enumerate(records):
        (
            first, second, third, anchor_index, kind, first_pivot,
            symmetry_index, order, second_pivot, direction_first,
            direction_second, direction_sign, second_factor, third_factor,
            scalar, label_count,
        ) = fields
        row = first, second, third
        pivot_counts[first_pivot] += 1
        if (
            kind != 51
            or first_pivot not in (5, 6)
            or not 0 <= anchor_index < 3
            or not 0 <= symmetry_index < len(stabilizers[kind])
            or order not in (0, 1)
            or not 0 <= second_pivot < 9
            or not 0 <= direction_first < direction_second < 9
            or direction_sign not in (-1, 1)
            or len(
                {
                    first_pivot, second_pivot,
                    direction_first, direction_second,
                }
            ) != 4
            or not 0 <= second_factor < len(factor_polynomial)
            or not 0 <= third_factor < len(factor_polynomial)
            or second_factor == third_factor
            or scalar == 0
            or label_count != len(labels)
        ):
            raise AssertionError(f"bad metadata at primitive record {number}")

        alignment = anchor_alignments[kind].get(row[anchor_index])
        if alignment is None or transform_factor(
            row[anchor_index], alignment, factor_occurrence, occurrence_factor
        ) != canonical[kind]:
            raise AssertionError(f"bad anchor transport at primitive record {number}")
        moved = tuple(
            transform_factor(
                factor, alignment, factor_occurrence, occurrence_factor
            )
            for index, factor in enumerate(row)
            if index != anchor_index
        )
        symmetry = stabilizers[kind][symmetry_index]
        targets = tuple(
            transform_factor(
                factor, symmetry, factor_occurrence, occurrence_factor
            )
            for factor in moved
        )
        if (second_factor, third_factor) != (
            targets[order], targets[1 - order]
        ):
            raise AssertionError(f"bad partner transport at primitive record {number}")

        chart = kind, first_pivot
        if chart not in chart_cache:
            anchor = factor_polynomial[canonical[kind]]
            first_slope, first_constant = fibers.pivot_split(
                anchor, first_pivot
            )
            if poly.add(
                poly.multiply(first_slope, poly.variable(first_pivot)),
                first_constant,
            ) != anchor:
                raise AssertionError(f"first graph reconstruction changed {chart}")
            first_certificate = triples.bracket_factorization(
                first_slope, parent_factors, depth=20
            )
            if first_certificate != EXPECTED_FIRST_SLOPES[first_pivot]:
                raise AssertionError(f"first slope is not a parent unit {chart}")
            first_product = poly.constant(first_certificate[0])
            for label in first_certificate[1]:
                first_product = poly.multiply(first_product, raw_parents[label])
            if first_product != first_slope:
                raise AssertionError(f"false first-slope product {chart}")
            first_numerator = poly.negative(first_constant)
            restricted_factors = tuple(
                fibers.graph_restrict(
                    polynomial, first_pivot, first_slope, first_numerator
                )
                for polynomial in factor_polynomial
            )
            restricted_parents = {}
            for label, parent, _sign in parent_factors:
                restricted = fibers.graph_restrict(
                    parent, first_pivot, first_slope, first_numerator
                )
                if not restricted:
                    raise AssertionError(
                        f"parent {label} vanishes on first graph {chart}"
                    )
                if len(restricted) == 1 and poly.ZERO_EXPONENT in restricted:
                    continue
                restricted_parents[label] = restricted
            chart_cache[chart] = restricted_factors, restricted_parents
        restricted_factors, restricted_parents = chart_cache[chart]

        second_polynomial = restricted_factors[second_factor]
        second_slope, second_constant = fibers.pivot_split(
            second_polynomial, second_pivot
        )
        if poly.add(
            poly.multiply(second_slope, poly.variable(second_pivot)),
            second_constant,
        ) != second_polynomial:
            raise AssertionError(f"second graph reconstruction at record {number}")
        slope_key = (
            chart, second_factor, second_pivot, scalar, labels,
        )
        if slope_key not in slope_keys:
            product = poly.constant(scalar)
            for label in labels:
                if label not in restricted_parents:
                    raise AssertionError(
                        f"unknown restricted parent {label} at record {number}"
                    )
                product = poly.multiply(product, restricted_parents[label])
            if product != second_slope:
                raise AssertionError(f"false second-slope unit at record {number}")
            slope_keys.add(slope_key)

        final_key = (
            chart, second_factor, third_factor, second_pivot,
            direction_first, direction_second, direction_sign,
        )
        if final_key not in final_keys:
            final = fibers.graph_restrict(
                restricted_factors[third_factor],
                second_pivot,
                second_slope,
                poly.negative(second_constant),
            )
            if second_directional(
                final, direction_first, direction_second, direction_sign
            ):
                raise AssertionError(
                    f"false primitive final affinity at record {number}"
                )
            final_keys.add(final_key)

    if dict(sorted(pivot_counts.items())) != EXPECTED_PIVOT_COUNTS:
        raise AssertionError("primitive pivot counts changed")
    if len(slope_keys) != EXPECTED_SLOPE_KEYS:
        raise AssertionError("primitive slope-key count changed")
    if len(final_keys) != EXPECTED_FINAL_KEYS:
        raise AssertionError("primitive final-key count changed")
    return dict(sorted(pivot_counts.items())), len(slope_keys), len(final_keys)


def source_replay(path: Path, primitive_rows, direct_rows):
    if path.stat().st_size != SOURCE_BYTES or sha256(path) != SOURCE_SHA256:
        raise AssertionError("post-double source artifact changed")
    raw = path.read_bytes()
    count, = struct.unpack_from("<I", raw)
    if count != SOURCE_COUNT or len(raw) != 4 + 6 * count:
        raise AssertionError("bad post-double source layout")
    seen = set()
    digest = hashlib.sha256()
    remaining = 0
    closed = direct_rows | primitive_rows
    for row in struct.iter_unpack("<HHH", raw[4:]):
        if row in seen or len(set(row)) != 3:
            raise AssertionError("bad row in post-double source")
        seen.add(row)
        if row not in closed:
            digest.update(struct.pack("<HHH", *row))
            remaining += 1
    if not primitive_rows <= seen:
        raise AssertionError("primitive certificate row outside post-double source")
    if remaining != AFTER_DIRECT_AND_PRIMITIVE_COUNT:
        raise AssertionError("primitive residual count changed")
    if digest.hexdigest() != AFTER_DIRECT_AND_PRIMITIVE_SEMANTIC:
        raise AssertionError("primitive residual semantic changed")
    print(
        "PASS post-double source/residue",
        len(seen), len(closed), remaining, digest.hexdigest(),
    )


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--post-double-residue",
        type=Path,
        help="optional pinned 1,221,055-row source for subset/residue replay",
    )
    arguments = parser.parse_args()

    records, primitive_rows = parse_certificate()
    if direct.CERTIFICATE_SHA256 != DIRECT_CERTIFICATE_SHA256:
        raise AssertionError("direct-final dependency pin changed")
    _blocks, direct_rows, _increments = direct.parse_certificate()
    if len(direct_rows) != DIRECT_UNION_COUNT:
        raise AssertionError("direct-final dependency count changed")
    overlap = primitive_rows & direct_rows
    if overlap:
        raise AssertionError(
            f"primitive certificate overlaps direct-final layer: {len(overlap)}"
        )
    pivot_counts, slope_keys, final_keys = replay_exact(records)
    if arguments.post_double_residue is not None:
        source_replay(
            arguments.post_double_residue, primitive_rows, direct_rows
        )

    print("PASS exact primitive-final rows", len(primitive_rows), pivot_counts)
    print("PASS direct-final disjointness", len(direct_rows), len(overlap))
    print("PASS exact second-slope products", slope_keys)
    print("PASS exact cleared-final directional identities", final_keys)
    print("CERTIFICATE_SHA256", CERTIFICATE_SHA256)
    print("SEMANTIC", SEMANTIC_SHA256)
    print(
        "THEOREM the unimodular change z_i=u, z_j=sign*u+w makes the "
        "cleared final equation affine in u"
    )
    if arguments.post_double_residue is None:
        print("CAVEAT pass --post-double-residue for exhaustive source replay")


if __name__ == "__main__":
    main()
