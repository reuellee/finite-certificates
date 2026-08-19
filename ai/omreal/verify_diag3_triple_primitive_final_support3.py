#!/usr/bin/env python3
"""Independent exact replay of support-three primitive final directions."""

from __future__ import annotations

import argparse
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
import verify_diag3_triple_primitive_final_direction as support2  # noqa: E402
import verify_residual_log_binomials as poly  # noqa: E402


CERTIFICATE = (
    HERE / "data/DIAG3_triple_primitive_final_support3_certificates.bin"
)
MAGIC = b"D3PFD3V1"
RECORD_FORMAT = "<HHHBBBBBBBBBbbHHbB"
COUNT = 57
CERTIFICATE_BYTES = 1_771
CERTIFICATE_SHA256 = (
    "c900dd68143d6228847124e4bc5891f440e0d116e2aabbaf2f0e28647f9fdbb3"
)
SEMANTIC_SHA256 = (
    "71df56d10ebd93be6f4c59f626d38d9a992264b2cbaf74fe0070618fed4a0de0"
)
ROW_SEMANTIC_SHA256 = (
    "4aa31365ba2f8dd9f429b5dd5ffbbc735f161c68dc5605372a597892da65965b"
)
DIRECT_CERTIFICATE_SHA256 = (
    "6ed192d1dd2f814ae914349ec2dbcc654ffb663669b85f1b289fa37feb147f26"
)
SUPPORT2_CERTIFICATE_SHA256 = (
    "af0d1964840975e324d2c0181e732142ccd4e35c88ab4fc2702b6c70e6389bde"
)
PRIOR_UNION_COUNT = 58_696
COMBINED_UNION_COUNT = 58_753
EXPECTED_SLOPE_KEYS = 34
EXPECTED_FINAL_KEYS = 57
EXPECTED_FIRST_SLOPE = (-1, ("1236", "2467"))
SOURCE_COUNT = 1_221_055
SOURCE_BYTES = 7_326_334
SOURCE_SHA256 = (
    "bdd29e7647a99429f38c7bc20e9e5b9b514dccf7cbf57f9cd9b1b36fec7e7d92"
)
RESIDUE_COUNT = 1_162_302
RESIDUE_SEMANTIC = (
    "a76a7c2cd6631c2d9724b450540bec7f3be6c106a41ae41f1736bbd2755a5ca4"
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
    """Return the pinned support-three records and row set."""

    if CERTIFICATE.stat().st_size != CERTIFICATE_BYTES:
        raise AssertionError("support-three certificate byte count changed")
    actual = sha256(CERTIFICATE)
    if actual != CERTIFICATE_SHA256:
        raise AssertionError(f"support-three certificate SHA-256 changed: {actual}")
    raw = CERTIFICATE.read_bytes()
    if raw[: len(MAGIC)] != MAGIC:
        raise AssertionError("bad support-three certificate magic")
    count, = struct.unpack_from("<I", raw, len(MAGIC))
    if count != COUNT:
        raise AssertionError("support-three certificate count changed")
    position = len(MAGIC) + 4
    fixed_size = struct.calcsize(RECORD_FORMAT)
    semantic = hashlib.sha256(
        b"diag3-triple-primitive-final-support3-v1\0"
    )
    rows = set()
    records = []
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
            raise AssertionError(f"bad support-three row at record {number}")
        rows.add(row)
        records.append((fields, labels))
    if position != len(raw):
        raise AssertionError("trailing support-three certificate bytes")
    if semantic.hexdigest() != SEMANTIC_SHA256:
        raise AssertionError("support-three certificate semantic changed")
    row_semantic = hashlib.sha256(
        b"".join(struct.pack("<HHH", *row) for row in sorted(rows))
    ).hexdigest()
    if row_semantic != ROW_SEMANTIC_SHA256:
        raise AssertionError("support-three row semantic changed")
    return tuple(records), rows


def directional(polynomial, variables, signs):
    return poly.add(*(
        gradient.derivative(polynomial, variable)
        if sign == 1
        else poly.negative(gradient.derivative(polynomial, variable))
        for variable, sign in zip(variables, signs, strict=True)
    ))


def replay_exact(records):
    occurrences, occurrence_factor, factor_polynomial = labeled.factor_polynomials()
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    canonical, alignments, stabilizers = labeled.canonical_anchor_alignments(
        occurrences, occurrence_factor, factor_occurrence
    )
    parent_factors = labeled.parent_bracket_factors()
    raw_parents = {
        label: poly.multiply(poly.constant(sign), factor)
        for label, factor, sign in parent_factors
    }

    anchor = factor_polynomial[canonical[51]]
    first_slope, first_constant = fibers.pivot_split(anchor, 6)
    if poly.add(
        poly.multiply(first_slope, poly.variable(6)), first_constant
    ) != anchor:
        raise AssertionError("support-three first graph reconstruction changed")
    first_certificate = triples.bracket_factorization(
        first_slope, parent_factors, depth=20
    )
    if first_certificate != EXPECTED_FIRST_SLOPE:
        raise AssertionError("support-three first slope changed")
    first_product = poly.constant(first_certificate[0])
    for label in first_certificate[1]:
        first_product = poly.multiply(first_product, raw_parents[label])
    if first_product != first_slope:
        raise AssertionError("false support-three first-slope product")
    first_numerator = poly.negative(first_constant)
    restricted_factors = tuple(
        fibers.graph_restrict(polynomial, 6, first_slope, first_numerator)
        for polynomial in factor_polynomial
    )
    restricted_parents = {}
    for label, parent, _sign in parent_factors:
        restricted = fibers.graph_restrict(
            parent, 6, first_slope, first_numerator
        )
        if not restricted:
            raise AssertionError(f"parent {label} vanishes on first graph")
        if len(restricted) == 1 and poly.ZERO_EXPONENT in restricted:
            continue
        restricted_parents[label] = restricted

    slope_keys = set()
    final_keys = set()
    for number, (fields, labels) in enumerate(records):
        (
            first, second, third, anchor_index, kind, first_pivot,
            symmetry_index, order, second_pivot, direction_first,
            direction_second, direction_third, sign_second, sign_third,
            second_factor, third_factor, scalar, label_count,
        ) = fields
        row = first, second, third
        if (
            (kind, first_pivot) != (51, 6)
            or not 0 <= anchor_index < 3
            or not 0 <= symmetry_index < len(stabilizers[51])
            or order not in (0, 1)
            or not 0 <= second_pivot < 9
            or not direction_first < direction_second < direction_third < 9
            or sign_second not in (-1, 1)
            or sign_third not in (-1, 1)
            or len(
                {
                    first_pivot, second_pivot, direction_first,
                    direction_second, direction_third,
                }
            ) != 5
            or not 0 <= second_factor < len(factor_polynomial)
            or not 0 <= third_factor < len(factor_polynomial)
            or second_factor == third_factor
            or scalar == 0
            or label_count != len(labels)
        ):
            raise AssertionError(f"bad support-three metadata at record {number}")

        alignment = alignments[51].get(row[anchor_index])
        if alignment is None or transform_factor(
            row[anchor_index], alignment, factor_occurrence, occurrence_factor
        ) != canonical[51]:
            raise AssertionError(f"bad support-three anchor at record {number}")
        moved = tuple(
            transform_factor(
                factor, alignment, factor_occurrence, occurrence_factor
            )
            for index, factor in enumerate(row) if index != anchor_index
        )
        symmetry = stabilizers[51][symmetry_index]
        targets = tuple(
            transform_factor(
                factor, symmetry, factor_occurrence, occurrence_factor
            )
            for factor in moved
        )
        if (second_factor, third_factor) != (
            targets[order], targets[1 - order]
        ):
            raise AssertionError(f"bad support-three transport at record {number}")

        second_polynomial = restricted_factors[second_factor]
        second_slope, second_constant = fibers.pivot_split(
            second_polynomial, second_pivot
        )
        if poly.add(
            poly.multiply(second_slope, poly.variable(second_pivot)),
            second_constant,
        ) != second_polynomial:
            raise AssertionError(f"second graph reconstruction at record {number}")
        slope_key = second_factor, second_pivot, scalar, labels
        if slope_key not in slope_keys:
            product = poly.constant(scalar)
            for label in labels:
                if label not in restricted_parents:
                    raise AssertionError(
                        f"bad restricted-parent label at record {number}"
                    )
                product = poly.multiply(product, restricted_parents[label])
            if product != second_slope:
                raise AssertionError(f"false second slope at record {number}")
            slope_keys.add(slope_key)

        variables = direction_first, direction_second, direction_third
        signs = 1, sign_second, sign_third
        final_key = (
            second_factor, third_factor, second_pivot,
            variables, signs,
        )
        if final_key not in final_keys:
            final = fibers.graph_restrict(
                restricted_factors[third_factor],
                second_pivot,
                second_slope,
                poly.negative(second_constant),
            )
            first_derivative = directional(final, variables, signs)
            if directional(first_derivative, variables, signs):
                raise AssertionError(
                    f"false support-three final identity at record {number}"
                )
            final_keys.add(final_key)

    if len(slope_keys) != EXPECTED_SLOPE_KEYS:
        raise AssertionError("support-three slope-key count changed")
    if len(final_keys) != EXPECTED_FINAL_KEYS:
        raise AssertionError("support-three final-key count changed")
    return len(slope_keys), len(final_keys)


def source_replay(path: Path, support3_rows, prior_rows):
    if path.stat().st_size != SOURCE_BYTES or sha256(path) != SOURCE_SHA256:
        raise AssertionError("post-double source artifact changed")
    raw = path.read_bytes()
    count, = struct.unpack_from("<I", raw)
    if count != SOURCE_COUNT or len(raw) != 4 + 6 * count:
        raise AssertionError("bad post-double source layout")
    closed = prior_rows | support3_rows
    if len(closed) != COMBINED_UNION_COUNT:
        raise AssertionError("combined primitive union changed")
    seen = set()
    digest = hashlib.sha256()
    remaining = 0
    for row in struct.iter_unpack("<HHH", raw[4:]):
        if row in seen or len(set(row)) != 3:
            raise AssertionError("bad row in post-double source")
        seen.add(row)
        if row not in closed:
            digest.update(struct.pack("<HHH", *row))
            remaining += 1
    if not support3_rows <= seen:
        raise AssertionError("support-three row outside post-double source")
    if remaining != RESIDUE_COUNT or digest.hexdigest() != RESIDUE_SEMANTIC:
        raise AssertionError("support-three residue pin changed")
    print(
        "PASS support-three source/residue",
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

    records, support3_rows = parse_certificate()
    if direct.CERTIFICATE_SHA256 != DIRECT_CERTIFICATE_SHA256:
        raise AssertionError("direct-final dependency pin changed")
    if support2.CERTIFICATE_SHA256 != SUPPORT2_CERTIFICATE_SHA256:
        raise AssertionError("support-two dependency pin changed")
    _blocks, direct_rows, _increments = direct.parse_certificate()
    _support2_records, support2_rows = support2.parse_certificate()
    prior_rows = direct_rows | support2_rows
    if len(prior_rows) != PRIOR_UNION_COUNT:
        raise AssertionError("prior primitive union changed")
    overlap = support3_rows & prior_rows
    if overlap:
        raise AssertionError(f"support-three overlap changed: {len(overlap)}")
    slope_keys, final_keys = replay_exact(records)
    if arguments.post_double_residue is not None:
        source_replay(arguments.post_double_residue, support3_rows, prior_rows)

    print("PASS exact support-three primitive rows", len(support3_rows))
    print("PASS prior-family disjointness", len(prior_rows), len(overlap))
    print("PASS exact second-slope products", slope_keys)
    print("PASS exact cleared-final support-three identities", final_keys)
    print("CERTIFICATE_SHA256", CERTIFICATE_SHA256)
    print("SEMANTIC", SEMANTIC_SHA256)
    print(
        "THEOREM the determinant-one change z_i=u, "
        "z_j=sign_j*u+s, z_k=sign_k*u+t makes the final equation affine in u"
    )
    if arguments.post_double_residue is None:
        print("CAVEAT pass --post-double-residue for exhaustive source replay")


if __name__ == "__main__":
    main()
