#!/usr/bin/env python3
"""Independent exact replay of the type-49/pivots-1,3,5 double-graph layer."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import struct
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY as triples  # noqa: E402
import verify_diag2_pivot_all_pair_fibers as fibers  # noqa: E402
import verify_residual_log_binomials as poly  # noqa: E402


CERTIFICATE = (
    HERE / "data/DIAG3_triple_double_graph_type49_pivot3_certificates.bin"
)
EXTENSION_CERTIFICATE = (
    HERE / "data/DIAG3_triple_double_graph_type49_extension_certificates.bin"
)
MAGIC = b"D3DGRAPH"
KIND = 49
PIVOT = 3
COUNT = 107_778
CERTIFICATE_SHA256 = (
    "52c9fec437378098e06a37c74396230b8e501b22bf8c7c5df07ef131e9aaa9c0"
)
SEMANTIC_SHA256 = (
    "98619fff126cc4e10331735fe691cde7f8e3a4f4983b31c63fbf5cd50616c5c9"
)
SOURCE_COUNT = 1_638_903
SOURCE_SHA256 = (
    "5ba2314c94ba115d5bf5e975e68412e3f4b44e2c65df51b757f6150a3352d4e1"
)
EXTENSION_MAGIC = b"D3DGEXT1"
EXTENSION_COUNT = 1_086
EXTENSION_SHA256 = (
    "1dc677cd3d46d774c7ba629606ec9b9483e1fda8c97e048033989f4498787873"
)
EXTENSION_SEMANTIC_SHA256 = (
    "a00a00cb16f238abecc8c625fa6334fc907f088e8906bada529384a59f5589e3"
)
EXTENSION_FORMAT = "<HHHBBBBBHHBbB"
GENERIC_CERTIFICATE = HERE / "data/DIAG3_triple_double_graph_generic_certificates.bin"
GENERIC_MAGIC = b"D3DGGEN1"
GENERIC_COUNT = 308_964
GENERIC_SHA256 = (
    "8a61846547b6a8ab1984a7ebe8273fd7326316c8a83c040af377a6251b21937c"
)
GENERIC_SEMANTIC_SHA256 = (
    "b82343d4aaf5225a6c1efaa454f5a8bad2622e4cd24f9d75603456393cbe0a1f"
)
GENERIC_FORMAT = "<HHHBBBBBBHHBbB"
COMBINED_DOUBLE_COUNT = 417_828
ALL_FAMILY_UNION_COUNT = 417_848
ALL_FAMILY_RESIDUE_COUNT = 1_221_055
ALL_FAMILY_RESIDUE_SEMANTIC = (
    "432854b7f00b57c5cf0009033e3ddfd3f4cb702bafed8fad2e5e69b369f30597"
)
FIXED_FORMAT = "<HHHBBBBHHBbB"
HEADER_FORMAT = "<BBHI"


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


def source_membership(path: Path, certificate_rows):
    actual = sha256(path)
    if actual != SOURCE_SHA256:
        raise AssertionError(f"sequential-residue SHA-256 changed: {actual}")
    raw = path.read_bytes()
    count, = struct.unpack_from("<I", raw)
    if count != SOURCE_COUNT or len(raw) != 4 + 6 * count:
        raise AssertionError("bad sequential-residue layout")
    rows = set()
    for row in struct.iter_unpack("<HHH", raw[4:]):
        if row in rows or len(set(row)) != 3:
            raise AssertionError(f"bad sequential-residue row {row}")
        rows.add(row)
    if not certificate_rows <= rows:
        raise AssertionError(
            f"certificate has {len(certificate_rows - rows)} rows outside its source"
        )
    print(
        "PASS source membership", len(certificate_rows), "of", len(rows), actual
    )
    return rows


def extension_replay(
    factor_polynomial,
    factor_occurrence,
    occurrence_factor,
    canonical,
    anchor_alignments,
    stabilizers,
    parent_factors,
    prior_rows,
):
    actual = sha256(EXTENSION_CERTIFICATE)
    if actual != EXTENSION_SHA256:
        raise AssertionError(f"extension certificate SHA-256 changed: {actual}")
    raw = EXTENSION_CERTIFICATE.read_bytes()
    count, = struct.unpack_from("<I", raw, len(EXTENSION_MAGIC))
    if raw[: len(EXTENSION_MAGIC)] != EXTENSION_MAGIC or count != EXTENSION_COUNT:
        raise AssertionError("bad extension certificate header")

    position = len(EXTENSION_MAGIC) + 4
    fixed_size = struct.calcsize(EXTENSION_FORMAT)
    semantic = hashlib.sha256(
        b"diag3-triple-double-graph-type49-extension-v1\0"
    )
    chart_cache = {}
    seen = set()
    slope_keys = set()
    independence_keys = set()
    affinity_keys = set()
    final_samples = set()
    for number in range(count):
        start = position
        (
            first,
            second,
            third,
            anchor_index,
            first_pivot,
            symmetry_index,
            order,
            second_pivot,
            second_factor,
            third_factor,
            final_coordinate,
            scalar,
            label_count,
        ) = struct.unpack_from(EXTENSION_FORMAT, raw, position)
        position += fixed_size
        labels = tuple(
            raw[position + 4 * index : position + 4 * index + 4].decode("ascii")
            for index in range(label_count)
        )
        position += 4 * label_count
        semantic.update(raw[start:position])
        row = first, second, third
        if row in seen or row in prior_rows or len(set(row)) != 3:
            raise AssertionError(f"bad/disallowed extension row at certificate {number}")
        seen.add(row)
        if (
            first_pivot not in (1, 5)
            or not 0 <= anchor_index < 3
            or not 0 <= symmetry_index < len(stabilizers[KIND])
            or order not in (0, 1)
            or not 0 <= second_pivot < 9
            or not 0 <= final_coordinate < 9
            or len({first_pivot, second_pivot, final_coordinate}) != 3
        ):
            raise AssertionError(f"bad extension metadata at certificate {number}")
        alignment = anchor_alignments[KIND].get(row[anchor_index])
        if alignment is None or transform_factor(
            row[anchor_index], alignment, factor_occurrence, occurrence_factor
        ) != canonical[KIND]:
            raise AssertionError(f"bad extension anchor at certificate {number}")
        moved = tuple(
            transform_factor(factor, alignment, factor_occurrence, occurrence_factor)
            for index, factor in enumerate(row)
            if index != anchor_index
        )
        symmetry = stabilizers[KIND][symmetry_index]
        targets = tuple(
            transform_factor(factor, symmetry, factor_occurrence, occurrence_factor)
            for factor in moved
        )
        if (second_factor, third_factor) != (
            targets[order], targets[1 - order]
        ):
            raise AssertionError(f"bad extension transport at certificate {number}")

        if first_pivot not in chart_cache:
            anchor = factor_polynomial[canonical[KIND]]
            first_slope, first_constant = fibers.pivot_split(anchor, first_pivot)
            if triples.bracket_factorization(
                first_slope, parent_factors, depth=20
            ) is None:
                raise AssertionError("extension first slope is not a parent unit")
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
                        f"parent bracket {label} vanishes in extension chart"
                    )
                if len(restricted) == 1 and poly.ZERO_EXPONENT in restricted:
                    continue
                restricted_parents[label] = restricted
            chart_cache[first_pivot] = restricted_factors, restricted_parents
        restricted_factors, restricted_parents = chart_cache[first_pivot]

        second = restricted_factors[second_factor]
        second_slope, second_constant = fibers.pivot_split(second, second_pivot)
        if (
            poly.add(
                poly.multiply(second_slope, poly.variable(second_pivot)),
                second_constant,
            )
            != second
        ):
            raise AssertionError(
                f"extension second graph reconstruction at certificate {number}"
            )
        slope_key = first_pivot, second_factor, second_pivot, scalar, labels
        if slope_key not in slope_keys:
            product = poly.constant(scalar)
            for label in labels:
                if label not in restricted_parents:
                    raise AssertionError(f"bad extension parent label {label}")
                product = poly.multiply(product, restricted_parents[label])
            if product != second_slope:
                raise AssertionError(f"false extension slope at certificate {number}")
            slope_keys.add(slope_key)
        independence_key = (
            first_pivot, second_factor, second_pivot, final_coordinate
        )
        if independence_key not in independence_keys:
            if any(
                monomial[final_coordinate] for monomial in second_slope
            ) or any(
                monomial[final_coordinate] for monomial in second_constant
            ):
                raise AssertionError(
                    f"false extension independence at certificate {number}"
                )
            independence_keys.add(independence_key)
        affinity_key = first_pivot, third_factor, final_coordinate
        third = restricted_factors[third_factor]
        if affinity_key not in affinity_keys:
            if any(monomial[final_coordinate] > 1 for monomial in third):
                raise AssertionError(f"false extension affinity at certificate {number}")
            affinity_keys.add(affinity_key)
        sample_key = first_pivot, second_pivot, final_coordinate
        if sample_key not in final_samples:
            final = fibers.graph_restrict(
                third,
                second_pivot,
                second_slope,
                poly.negative(second_constant),
            )
            if any(monomial[final_coordinate] > 1 for monomial in final):
                raise AssertionError(
                    f"extension final affinity failed at certificate {number}"
                )
            final_samples.add(sample_key)

    if position != len(raw) or semantic.hexdigest() != EXTENSION_SEMANTIC_SHA256:
        raise AssertionError("extension EOF or semantic changed")
    print("PASS exact extension certificates", len(seen), actual)
    print("PASS extension slope identities", len(slope_keys))
    print("PASS extension z-independence keys", len(independence_keys))
    print("PASS extension q3-affinity keys", len(affinity_keys))
    print("PASS extension final-substitution regressions", len(final_samples))
    print("EXTENSION_SEMANTIC", semantic.hexdigest())
    return seen


def generic_certificate_rows():
    """Return pinned generic rows for independent overlap consumers."""
    raw = GENERIC_CERTIFICATE.read_bytes()
    if sha256(GENERIC_CERTIFICATE) != GENERIC_SHA256:
        raise AssertionError("generic certificate SHA-256 changed")
    count, = struct.unpack_from("<I", raw, len(GENERIC_MAGIC))
    if raw[: len(GENERIC_MAGIC)] != GENERIC_MAGIC or count != GENERIC_COUNT:
        raise AssertionError("bad generic certificate header")
    position = len(GENERIC_MAGIC) + 4
    size = struct.calcsize(GENERIC_FORMAT)
    rows = set()
    for _ in range(count):
        record = struct.unpack_from(GENERIC_FORMAT, raw, position)
        position += size + 4 * record[-1]
        if record[:3] in rows:
            raise AssertionError("duplicate generic certificate row")
        rows.add(record[:3])
    if position != len(raw):
        raise AssertionError("generic certificate EOF changed")
    return rows


def generic_replay(
    factor_polynomial, factor_occurrence, occurrence_factor, canonical,
    anchor_alignments, stabilizers, parent_factors, prior_rows,
):
    actual = sha256(GENERIC_CERTIFICATE)
    if actual != GENERIC_SHA256:
        raise AssertionError(f"generic certificate SHA-256 changed: {actual}")
    raw = GENERIC_CERTIFICATE.read_bytes()
    count, = struct.unpack_from("<I", raw, len(GENERIC_MAGIC))
    if raw[: len(GENERIC_MAGIC)] != GENERIC_MAGIC or count != GENERIC_COUNT:
        raise AssertionError("bad generic certificate header")
    position = len(GENERIC_MAGIC) + 4
    size = struct.calcsize(GENERIC_FORMAT)
    semantic = hashlib.sha256(b"diag3-triple-double-graph-generic-v1\0")
    chart_cache = {}
    seen = set()
    slope_keys, independence_keys, affinity_keys, final_samples = set(), set(), set(), set()
    kind_counts = {}
    for number in range(count):
        start = position
        (
            first, second, third, anchor_index, kind, first_pivot,
            symmetry_index, order, second_pivot, second_factor, third_factor,
            final_coordinate, scalar, label_count,
        ) = struct.unpack_from(GENERIC_FORMAT, raw, position)
        position += size
        labels = tuple(
            raw[position + 4 * index : position + 4 * index + 4].decode("ascii")
            for index in range(label_count)
        )
        position += 4 * label_count
        semantic.update(raw[start:position])
        row = first, second, third
        if row in seen or row in prior_rows or len(set(row)) != 3:
            raise AssertionError(f"bad/disallowed generic row {number}")
        seen.add(row)
        kind_counts[kind] = kind_counts.get(kind, 0) + 1
        if (
            kind not in canonical or not 0 <= anchor_index < 3
            or not 0 <= symmetry_index < len(stabilizers[kind])
            or order not in (0, 1) or not 0 <= first_pivot < 9
            or not 0 <= second_pivot < 9 or not 0 <= final_coordinate < 9
            or len({first_pivot, second_pivot, final_coordinate}) != 3
            or scalar == 0
        ):
            raise AssertionError(f"bad generic metadata {number}")
        alignment = anchor_alignments[kind].get(row[anchor_index])
        if alignment is None or transform_factor(
            row[anchor_index], alignment, factor_occurrence, occurrence_factor
        ) != canonical[kind]:
            raise AssertionError(f"bad generic anchor {number}")
        moved = tuple(
            transform_factor(factor, alignment, factor_occurrence, occurrence_factor)
            for index, factor in enumerate(row) if index != anchor_index
        )
        symmetry = stabilizers[kind][symmetry_index]
        targets = tuple(
            transform_factor(factor, symmetry, factor_occurrence, occurrence_factor)
            for factor in moved
        )
        if (second_factor, third_factor) != (targets[order], targets[1 - order]):
            raise AssertionError(f"bad generic transport {number}")
        chart = kind, first_pivot
        if chart not in chart_cache:
            anchor = factor_polynomial[canonical[kind]]
            first_slope, first_constant = fibers.pivot_split(anchor, first_pivot)
            if poly.add(
                poly.multiply(first_slope, poly.variable(first_pivot)),
                first_constant,
            ) != anchor:
                raise AssertionError(f"generic first reconstruction {chart}")
            if triples.bracket_factorization(first_slope, parent_factors, 20) is None:
                raise AssertionError(f"generic first slope is not a unit {chart}")
            numerator = poly.negative(first_constant)
            restricted_factors = tuple(
                fibers.graph_restrict(p, first_pivot, first_slope, numerator)
                for p in factor_polynomial
            )
            restricted_parents = {}
            for label, parent, _sign in parent_factors:
                restricted = fibers.graph_restrict(
                    parent, first_pivot, first_slope, numerator
                )
                if not restricted:
                    raise AssertionError(f"parent {label} vanishes in {chart}")
                if len(restricted) == 1 and poly.ZERO_EXPONENT in restricted:
                    continue
                restricted_parents[label] = restricted
            chart_cache[chart] = restricted_factors, restricted_parents
        restricted_factors, restricted_parents = chart_cache[chart]
        second = restricted_factors[second_factor]
        second_slope, second_constant = fibers.pivot_split(second, second_pivot)
        if poly.add(
            poly.multiply(second_slope, poly.variable(second_pivot)), second_constant
        ) != second:
            raise AssertionError(f"generic second reconstruction {number}")
        slope_key = chart, second_factor, second_pivot, scalar, labels
        if slope_key not in slope_keys:
            product = poly.constant(scalar)
            for label in labels:
                if label not in restricted_parents:
                    raise AssertionError(f"bad generic parent label {label}")
                product = poly.multiply(product, restricted_parents[label])
            if product != second_slope:
                raise AssertionError(f"false generic slope {number}")
            slope_keys.add(slope_key)
        independence_key = chart, second_factor, second_pivot, final_coordinate
        if independence_key not in independence_keys:
            if any(m[final_coordinate] for m in second_slope) or any(
                m[final_coordinate] for m in second_constant
            ):
                raise AssertionError(f"false generic independence {number}")
            independence_keys.add(independence_key)
        third = restricted_factors[third_factor]
        affinity_key = chart, third_factor, final_coordinate
        if affinity_key not in affinity_keys:
            if any(m[final_coordinate] > 1 for m in third):
                raise AssertionError(f"false generic affinity {number}")
            affinity_keys.add(affinity_key)
        sample_key = kind, first_pivot, second_pivot, final_coordinate
        if sample_key not in final_samples:
            final = fibers.graph_restrict(
                third, second_pivot, second_slope, poly.negative(second_constant)
            )
            if any(m[final_coordinate] > 1 for m in final):
                raise AssertionError(f"generic final affinity {number}")
            final_samples.add(sample_key)
        if (number + 1) % 50_000 == 0:
            print("PASS generic certificates", number + 1, "/", count, flush=True)
    if position != len(raw) or semantic.hexdigest() != GENERIC_SEMANTIC_SHA256:
        raise AssertionError("generic EOF or semantic changed")
    print("PASS exact generic certificates", len(seen), actual)
    print("PASS generic kind counts", dict(sorted(kind_counts.items())))
    print("PASS generic slope identities", len(slope_keys))
    print("PASS generic z-independence keys", len(independence_keys))
    print("PASS generic q3-affinity keys", len(affinity_keys))
    print("PASS generic final-substitution regressions", len(final_samples))
    print("GENERIC_SEMANTIC", semantic.hexdigest())
    return seen


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sequential-residue",
        type=Path,
        help="optionally replay subset membership in the regenerable pinned residue",
    )
    arguments = parser.parse_args()

    actual = sha256(CERTIFICATE)
    if actual != CERTIFICATE_SHA256:
        raise AssertionError(f"double-graph certificate SHA-256 changed: {actual}")
    raw = CERTIFICATE.read_bytes()
    position = len(MAGIC)
    kind, pivot, reserved, count = struct.unpack_from(
        HEADER_FORMAT, raw, position
    )
    position += struct.calcsize(HEADER_FORMAT)
    if (
        raw[: len(MAGIC)] != MAGIC
        or (kind, pivot, reserved, count) != (KIND, PIVOT, 0, COUNT)
    ):
        raise AssertionError("bad double-graph certificate header")

    occurrences, occurrence_factor, factor_polynomial = labeled.factor_polynomials()
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    canonical, anchor_alignments, stabilizers = labeled.canonical_anchor_alignments(
        occurrences, occurrence_factor, factor_occurrence
    )
    parent_factors = labeled.parent_bracket_factors()

    anchor = factor_polynomial[canonical[KIND]]
    first_slope, first_constant = fibers.pivot_split(anchor, PIVOT)
    first_numerator = poly.negative(first_constant)
    if (
        poly.add(
            poly.multiply(first_slope, poly.variable(PIVOT)), first_constant
        )
        != anchor
    ):
        raise AssertionError("first graph reconstruction changed")
    if triples.bracket_factorization(first_slope, parent_factors, depth=20) is None:
        raise AssertionError("first graph slope is not a parent unit")

    restricted_factors = tuple(
        fibers.graph_restrict(
            polynomial, PIVOT, first_slope, first_numerator
        )
        for polynomial in factor_polynomial
    )
    restricted_parents = {}
    for label, parent, _sign in parent_factors:
        restricted = fibers.graph_restrict(
            parent, PIVOT, first_slope, first_numerator
        )
        if not restricted:
            raise AssertionError(f"parent bracket {label} vanishes on first graph")
        if len(restricted) == 1 and poly.ZERO_EXPONENT in restricted:
            continue
        restricted_parents[label] = restricted

    seen = set()
    semantic = hashlib.sha256(
        b"diag3-triple-double-graph-type49-pivot3-v1\0"
    )
    slope_cache = set()
    independence_cache = set()
    affinity_cache = set()
    final_samples = set()
    fixed_size = struct.calcsize(FIXED_FORMAT)
    for number in range(count):
        start = position
        (
            first,
            second,
            third,
            anchor_index,
            symmetry_index,
            order,
            second_pivot,
            second_factor,
            third_factor,
            final_coordinate,
            scalar,
            label_count,
        ) = struct.unpack_from(FIXED_FORMAT, raw, position)
        position += fixed_size
        labels = tuple(
            raw[position + 4 * index : position + 4 * index + 4].decode("ascii")
            for index in range(label_count)
        )
        position += 4 * label_count
        semantic.update(raw[start:position])

        row = first, second, third
        if row in seen or len(set(row)) != 3:
            raise AssertionError(f"bad source row at certificate {number}")
        seen.add(row)
        if (
            not 0 <= anchor_index < 3
            or not 0 <= symmetry_index < len(stabilizers[KIND])
            or order not in (0, 1)
            or not 0 <= second_pivot < 9
            or not 0 <= final_coordinate < 9
            or second_pivot == final_coordinate
            or PIVOT in (second_pivot, final_coordinate)
        ):
            raise AssertionError(f"bad transport metadata at certificate {number}")
        alignment = anchor_alignments[KIND].get(row[anchor_index])
        if alignment is None or transform_factor(
            row[anchor_index], alignment, factor_occurrence, occurrence_factor
        ) != canonical[KIND]:
            raise AssertionError(f"bad anchor alignment at certificate {number}")
        moved = tuple(
            transform_factor(factor, alignment, factor_occurrence, occurrence_factor)
            for index, factor in enumerate(row)
            if index != anchor_index
        )
        symmetry = stabilizers[KIND][symmetry_index]
        targets = tuple(
            transform_factor(factor, symmetry, factor_occurrence, occurrence_factor)
            for factor in moved
        )
        expected = targets[order], targets[1 - order]
        if (second_factor, third_factor) != expected:
            raise AssertionError(f"bad factor transport at certificate {number}")

        second = restricted_factors[second_factor]
        if any(monomial[second_pivot] > 1 for monomial in second):
            raise AssertionError(f"second factor is not affine at certificate {number}")
        second_slope, second_constant = fibers.pivot_split(second, second_pivot)
        if (
            poly.add(
                poly.multiply(second_slope, poly.variable(second_pivot)),
                second_constant,
            )
            != second
        ):
            raise AssertionError(f"second graph reconstruction at certificate {number}")

        slope_key = second_factor, second_pivot, scalar, labels
        if slope_key not in slope_cache:
            product = poly.constant(scalar)
            for label in labels:
                if label not in restricted_parents:
                    raise AssertionError(
                        f"bad restricted-parent label at certificate {number}"
                    )
                product = poly.multiply(product, restricted_parents[label])
            if product != second_slope:
                raise AssertionError(f"false second-unit identity at certificate {number}")
            slope_cache.add(slope_key)

        independence_key = second_factor, second_pivot, final_coordinate
        if independence_key not in independence_cache:
            if any(
                monomial[final_coordinate]
                for monomial in second_slope
            ) or any(
                monomial[final_coordinate]
                for monomial in second_constant
            ):
                raise AssertionError(f"false z-independence at certificate {number}")
            independence_cache.add(independence_key)

        third = restricted_factors[third_factor]
        affinity_key = third_factor, final_coordinate
        if affinity_key not in affinity_cache:
            if any(monomial[final_coordinate] > 1 for monomial in third):
                raise AssertionError(f"false third affinity at certificate {number}")
            affinity_cache.add(affinity_key)

        # One exact regression per coordinate pair explicitly checks the degree
        # transfer. For every other row it follows identically from the exact
        # z-independence and affinity checks above.
        sample_key = second_pivot, final_coordinate
        if sample_key not in final_samples:
            final = fibers.graph_restrict(
                third,
                second_pivot,
                second_slope,
                poly.negative(second_constant),
            )
            if any(monomial[final_coordinate] > 1 for monomial in final):
                raise AssertionError(f"final affinity failed at certificate {number}")
            final_samples.add(sample_key)

        if (number + 1) % 20_000 == 0:
            print("PASS exact certificates", number + 1, "/", count, flush=True)

    if position != len(raw) or len(seen) != COUNT:
        raise AssertionError("certificate EOF or unique-row count changed")
    actual_semantic = semantic.hexdigest()
    if actual_semantic != SEMANTIC_SHA256:
        raise AssertionError(f"certificate semantic changed: {actual_semantic}")
    extension_rows = extension_replay(
        factor_polynomial,
        factor_occurrence,
        occurrence_factor,
        canonical,
        anchor_alignments,
        stabilizers,
        parent_factors,
        seen,
    )
    generic_rows = generic_replay(
        factor_polynomial,
        factor_occurrence,
        occurrence_factor,
        canonical,
        anchor_alignments,
        stabilizers,
        parent_factors,
        seen | extension_rows,
    )
    combined_rows = seen | extension_rows | generic_rows
    if len(combined_rows) != COMBINED_DOUBLE_COUNT:
        raise AssertionError("combined double-graph count changed")
    if arguments.sequential_residue is not None:
        source_rows = source_membership(arguments.sequential_residue, combined_rows)
        # The separate unit-minor verifier pins its 117 rows and the exact
        # 97-row overlap. The resulting full-family residue is independently
        # hashed here by filtering the source in its canonical order.
        unit_module = __import__("verify_diag3_triple_unit_minor_after_graph")
        records = unit_module.parse_certificate(unit_module.CERTIFICATE)
        occurrences, occurrence_factor, factor_polynomial = labeled.factor_polynomials()
        factor_occurrence = labeled.factor_action_is_well_defined(
            occurrences, occurrence_factor
        )
        canonical, anchor_alignments, stabilizers = labeled.canonical_anchor_alignments(
            occurrences, occurrence_factor, factor_occurrence
        )
        parents = {label: polynomial for label, polynomial, _ in parent_factors}
        pair_witnesses, _lengths, _semantic = unit_module.replay_pairs(
            records, factor_polynomial, canonical[unit_module.KIND], parents
        )
        unit_minor_rows = set()
        for row in source_rows:
            witness = False
            for anchor_index, anchor in enumerate(row):
                mapping = anchor_alignments[unit_module.KIND].get(anchor)
                if mapping is None:
                    continue
                others = tuple(row[index] for index in range(3) if index != anchor_index)
                moved = tuple(
                    labeled.transform_factor(
                        factor, mapping, factor_occurrence, occurrence_factor
                    ) for factor in others
                )
                for symmetry in stabilizers[unit_module.KIND]:
                    targets = tuple(
                        labeled.transform_factor(
                            factor, symmetry, factor_occurrence, occurrence_factor
                        ) for factor in moved
                    )
                    if tuple(sorted(targets)) in pair_witnesses:
                        witness = True
                        break
                if witness:
                    break
            if witness:
                unit_minor_rows.add(row)
        if len(unit_minor_rows) != unit_module.EXPECTED_ROW_COUNT:
            raise AssertionError("unit-minor row reconstruction changed")
        all_closed = combined_rows | unit_minor_rows
        if len(all_closed) != ALL_FAMILY_UNION_COUNT:
            raise AssertionError("all-family union count changed")
        digest = hashlib.sha256()
        source_raw = arguments.sequential_residue.read_bytes()
        for row in struct.iter_unpack("<HHH", source_raw[4:]):
            if row not in all_closed:
                digest.update(struct.pack("<HHH", *row))
        if (
            len(source_rows - all_closed) != ALL_FAMILY_RESIDUE_COUNT
            or digest.hexdigest() != ALL_FAMILY_RESIDUE_SEMANTIC
        ):
            raise AssertionError("all-family residue pin changed")
        print("PASS all-family union/residue", len(all_closed), len(source_rows-all_closed))

    print("PASS independent double-graph certificates", count, actual)
    print("PASS exact slope identities", len(slope_cache))
    print("PASS exact z-independence keys", len(independence_cache))
    print("PASS exact q3-affinity keys", len(affinity_cache))
    print("PASS explicit final-substitution regressions", len(final_samples))
    print("SEMANTIC", actual_semantic)
    print("PASS combined double-graph rows", len(combined_rows))
    print(
        "THEOREM each record has two exact unit graphs followed by an "
        "affine one-equation fiber"
    )
    if arguments.sequential_residue is None:
        print("CAVEAT pass --sequential-residue to replay source membership")


if __name__ == "__main__":
    main()
