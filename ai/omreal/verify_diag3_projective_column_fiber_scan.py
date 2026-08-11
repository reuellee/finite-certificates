#!/usr/bin/env python3
"""Replay the diagonal-three projective-column compression census.

The expensive mode constructs the full S8 action and invokes the companion
OpenMP scanner.  It needs about 4 GiB of RAM.  A saved scanner residue can be
replayed with ``--residue``; this still reconstructs every occurrence support
and checks the exact union-degree buckets.

The structural replay deliberately stops at union degree four.  The optional
compact Morse replay then verifies 12,333 triangular and 65,550 exact
unit-minor closures inside that bucket; it leaves 1,819,850 triple orbits.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import hashlib
from itertools import combinations, permutations, product
import os
from pathlib import Path
import struct
import subprocess
import sys
import tempfile

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as gradient_verify  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY as triple_verify  # noqa: E402
import DIAG9_GRAPH_global_factor_census as global_factors  # noqa: E402
import verify_residual_log_binomials as sparse_poly  # noqa: E402


FACTOR_COUNT = 26_740
PAIR_COUNT = 9_476
TRIPLE_COUNT = 79_102_449
AFFINE_COUNT = 74_767_375
STANDARD_AFFINE_COUNT = 65_557_134
AFFINE_RESIDUE_COUNT = 4_335_074
UNION_COUNTS = {2: 26_927, 3: 2_410_414, 4: 1_897_733}
INPUT_DIGEST = "76956ac6ab5a9d67bf9ad74f46719a3f9612ebfed22696eae1e797f70f96bf63"
RESIDUE_DIGEST = "c8cac9809ceaea9438e0d5219f3bca0ed0173f544d6b53d8b33f8a8bce5ee754"
BUCKET_DIGESTS = {
    2: "0c5413d8fa0de835f3ba777c00d2c57527ff828faf8b1a4c7856384f66421616",
    3: "694cbdd93f49a0df5fb4f5c38b3a969286b56b914270ab8933dd765458699bd7",
    4: "54b03c31910de606b80f9dcc448ce3dde93063a8dbc3f2dbcaa7a02901df0303",
}
UNION3_PARTITIONS = {
    (1, 1, 2): 1_388_106,
    (1, 1, 6): 250_135,
    (1, 2, 3): 174_811,
    (1, 2, 5): 590_856,
    (1, 2, 7): 4_062,
    (1, 3, 6): 2_444,
}
UNION3_PERFECT_MATCHINGS = {
    (1, 2, 5),
    (1, 2, 7),
    (1, 3, 6),
}
COORDINATE_BLOCKS = tuple(combinations(range(9), 3))
MORSE_CERTIFICATE = HERE / "data" / "DIAG3_morse_unit_minor_certificates.bin"
TRIANGULAR_FEATURES = HERE / "data" / "DIAG3_triangular_features.bin"
MORSE_CERTIFICATE_DIGEST = (
    "afe01d6d94bc4b8ce133cbe0d14ceb01d9dd72514f9ed7a59b73d5f6b4299734"
)
MORSE_SOURCE_DIGEST = (
    "1c64017faad2173a3552dd70427d893c6ad4e39f31075ef9941c871f11184949"
)
MORSE_SOURCE_COUNT = 1_885_400
TRIANGULAR_FEATURE_DIGEST = (
    "7fae9da26cf7391d2dc3b00e55faabdf4556d4badc9a2f8c4ace3ecc29d7f136"
)
TRIANGULAR_CLOSED_COUNT = 12_333
MORSE_CLOSED_COUNT = 65_550
MORSE_EXHAUSTIVE_FRAMES = 1_120
MORSE_WITNESS_FRAMES = 79
MORSE_LAST_WITNESS_FRAME = 815
MORSE_MODULAR_CANDIDATES = 65_624
MORSE_MODULAR_FALSE = 74
MORSE_MAGIC = b"D3MORSE1"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def role_frames():
    """Represent S8/(S{2,3,4} x S{6,7,8}) exactly as in the full sweep."""
    frames = []
    labels = set(range(8))
    for first in range(8):
        for fifth in range(8):
            if fifth == first:
                continue
            available = sorted(labels - {first, fifth})
            for row_block in combinations(available, 3):
                variable_block = sorted(set(available) - set(row_block))
                permutation = [None] * 8
                permutation[0] = first
                permutation[1:4] = row_block
                permutation[4] = fifth
                permutation[5:8] = variable_block
                frames.append(tuple(permutation))
    priority = (
        tuple(range(8)),
        (1, 0, 2, 3, 4, 5, 6, 7),
        (0, 1, 2, 4, 3, 5, 6, 7),
        (0, 1, 2, 3, 5, 4, 6, 7),
    )
    result = priority + tuple(frame for frame in frames if frame not in priority)
    if len(result) != MORSE_EXHAUSTIVE_FRAMES or len(set(result)) != len(result):
        raise AssertionError("bad role-frame quotient")
    return result


def affinity_mask(polynomial) -> int:
    """Blocks on which a sparse polynomial has total degree at most one."""
    answer = 0
    for bit, block in enumerate(COORDINATE_BLOCKS):
        if all(sum(monomial[index] for index in block) <= 1 for monomial in polynomial):
            answer |= 1 << bit
    return answer


def census_data():
    occurrences, occurrence_factor, factor_polynomial = labeled.factor_polynomials()
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    representatives, _, _, _, _ = labeled.factor_orbit_data(
        occurrences, occurrence_factor
    )
    pair_keys, _, _ = labeled.pair_orbit_representatives(
        occurrences, occurrence_factor
    )
    pairs = tuple((representatives[kind], second) for kind, second in pair_keys)
    if tuple(sorted(factor_occurrence)) != tuple(range(FACTOR_COUNT)):
        raise AssertionError("factor numbering changed")
    if len(pairs) != PAIR_COUNT:
        raise AssertionError("pair-orbit count changed")
    return (
        occurrences,
        occurrence_factor,
        factor_polynomial,
        factor_occurrence,
        pairs,
    )


def occurrence_complete_masks(occurrences, occurrence_factor, factor_polynomial):
    """Aggregate all primitive and full-occurrence equations per factor.

    A full occurrence is the primitive localized factor multiplied by the
    exact parent-bracket units stripped in the global census.  The primitive
    equation is retained too because division by a parent unit is valid on
    the uniform cell.  The assertion records the census-specific fact that
    no full occurrence adds an affine block here; the proof does not assume
    this under a change of units.
    """
    masks = [affinity_mask(polynomial) for polynomial in factor_polynomial]
    primitive = tuple(masks)
    matrix = global_factors.normalized_matrix()
    brackets = global_factors.bracket_records(matrix)
    with np.load(global_factors.CERTIFICATE, allow_pickle=False) as certificate:
        offsets = tuple(map(int, certificate["occurrence_unit_offset"]))
        indices = tuple(map(int, certificate["occurrence_unit_index"]))
        stored = tuple(tuple(map(int, row)) for row in certificate["occurrence_fourset"])
    if stored != occurrences or len(offsets) != len(occurrences) + 1:
        raise AssertionError("global occurrence certificate changed")
    added = 0
    for number, occurrence in enumerate(occurrences):
        factor = occurrence_factor[occurrence]
        polynomial = factor_polynomial[factor]
        for unit in indices[offsets[number] : offsets[number + 1]]:
            polynomial = global_factors.multiply(polynomial, brackets[unit][1])
        raw = affinity_mask(polynomial)
        added += (raw & ~primitive[factor]).bit_count()
        masks[factor] |= raw
    if added:
        raise AssertionError(f"full occurrences added {added} unexpected affine blocks")
    return tuple(masks)


def export_scan_input(path: Path, data) -> None:
    occurrences, occurrence_factor, factor_polynomial, factor_occurrence, pairs = data
    masks = occurrence_complete_masks(
        occurrences, occurrence_factor, factor_polynomial
    )
    generators = []
    for index in range(7):
        permutation = list(range(8))
        permutation[index], permutation[index + 1] = (
            permutation[index + 1], permutation[index],
        )
        mapping = labeled.triple_map(tuple(permutation))
        generators.append(
            tuple(
                labeled.transform_factor(
                    factor, mapping, factor_occurrence, occurrence_factor
                )
                for factor in range(FACTOR_COUNT)
            )
        )
    with path.open("wb") as output:
        output.write(struct.pack("<III", FACTOR_COUNT, PAIR_COUNT, 7))
        for row in generators:
            output.write(struct.pack(f"<{FACTOR_COUNT}H", *row))
        for mask in masks:
            output.write(struct.pack("<QQ", mask & ((1 << 64) - 1), mask >> 64))
        for first, second in pairs:
            output.write(struct.pack("<HH", first, second))
    actual = sha256(path)
    if actual != INPUT_DIGEST:
        raise AssertionError(f"scanner-input digest changed: {actual}")
    print("PASS scanner input", actual)


def run_full_scan(residue: Path, data, workers: int | None) -> None:
    with tempfile.TemporaryDirectory(prefix="diag3-affine-scan-") as directory:
        directory = Path(directory)
        scan_input = directory / "input.bin"
        executable = directory / "scan"
        export_scan_input(scan_input, data)
        subprocess.run(
            [
                "g++", "-O3", "-std=c++17", "-fopenmp",
                str(HERE / "verify_diag3_projective_column_fiber_scan.cpp"),
                "-o", str(executable),
            ],
            check=True,
        )
        environment = dict(os.environ)
        if workers is not None:
            environment["OMP_NUM_THREADS"] = str(workers)
        subprocess.run(
            [str(executable), str(scan_input), str(residue)],
            check=True,
            env=environment,
        )


def minimal_incidence_masks(occurrences, occurrence_factor):
    by_factor = defaultdict(list)
    for occurrence in occurrences:
        by_factor[occurrence_factor[occurrence]].append(occurrence)
    incident_rows = tuple(
        tuple(index for index, triple in enumerate(labeled.TRIPLES) if label in triple)
        for label in range(8)
    )
    result = []
    for factor in range(FACTOR_COUNT):
        factor_rows = []
        for incident in incident_rows:
            position = {index: bit for bit, index in enumerate(incident)}
            masks = {
                sum(1 << position[index] for index in occurrence if index in position)
                for occurrence in by_factor[factor]
            }
            factor_rows.append(
                tuple(
                    sorted(
                        mask for mask in masks
                        if not any(
                            other != mask and other & ~mask == 0
                            for other in masks
                        )
                    )
                )
            )
        result.append(tuple(factor_rows))
    return tuple(result)


def canonical_partition(masks) -> tuple[int, ...]:
    union = masks[0] | masks[1] | masks[2]
    columns = tuple(
        sum(((masks[row] >> bit) & 1) << row for row in range(3))
        for bit in range(21)
        if union >> bit & 1
    )
    return min(
        tuple(
            sorted(
                sum(((column >> permutation[new]) & 1) << new for new in range(3))
                for column in columns
            )
        )
        for permutation in permutations(range(3))
    )


def partition_is_forest(partition: tuple[int, ...]) -> bool:
    """Check the three-factor/three-pencil incidence graph is acyclic."""
    parent = list(range(6))

    def root(vertex):
        while parent[vertex] != vertex:
            parent[vertex] = parent[parent[vertex]]
            vertex = parent[vertex]
        return vertex

    for column, mask in enumerate(partition):
        for row in range(3):
            if not (mask >> row) & 1:
                continue
            left, right = root(row), root(3 + column)
            if left == right:
                return False
            parent[left] = right
    return True


def partition_has_perfect_pencil_matching(partition: tuple[int, ...]) -> bool:
    """A matching covering all pencil columns necessarily uses all rows."""
    return any(
        all((partition[column] >> row) & 1 for column, row in enumerate(choice))
        for choice in permutations(range(3))
    )


def best_union(factors, minimal):
    best = 22
    partitions = set()
    for label in range(8):
        for masks in product(*(minimal[factor][label] for factor in factors)):
            degree = (masks[0] | masks[1] | masks[2]).bit_count()
            if degree < best:
                best = degree
                partitions.clear()
            if degree == best:
                partitions.add(canonical_partition(masks))
    return best, min(partitions)


def triangular_works(factors, features) -> bool:
    """Exact sequential zero/unit-slope graph test used before the role scan."""
    rows = [features[factor] for factor in factors]
    for first_row, second_row, third_row in permutations(range(3)):
        zero0, unit0 = rows[first_row]
        zero1, unit1 = rows[second_row]
        zero2, unit2 = rows[third_row]
        first = unit0 & zero1 & zero2
        second = unit1 & zero2
        third = unit2
        if not first or not second or not third:
            continue
        if (first | second).bit_count() < 2:
            continue
        if (first | third).bit_count() < 2:
            continue
        if (second | third).bit_count() < 2:
            continue
        if (first | second | third).bit_count() >= 3:
            return True
    return False


def replay_morse_certificates(
    path: Path, data, source: Path | None, union4: Path | None
) -> None:
    """Replay every exact unit-minor identity in the compact role artifact.

    The 79 witness frames suffice for the positive theorem count.  The claim
    that the unit-minor search found no further orbit uses the separate full
    1,120-frame scan; the compact artifact records its accounting but does
    not turn the 79 witnesses into a smaller group quotient.
    """
    actual = sha256(path)
    if actual != MORSE_CERTIFICATE_DIGEST:
        raise AssertionError(f"Morse-certificate digest changed: {actual}")
    raw = path.read_bytes()
    header_format = "<8sIHHHIII"
    header_size = struct.calcsize(header_format)
    (
        magic, count, exhaustive_frames, witness_frame_count,
        last_witness_frame, modular_candidates, modular_false, source_count,
    ) = struct.unpack_from(header_format, raw)
    expected_header = (
        MORSE_MAGIC, MORSE_CLOSED_COUNT, MORSE_EXHAUSTIVE_FRAMES,
        MORSE_WITNESS_FRAMES, MORSE_LAST_WITNESS_FRAME,
        MORSE_MODULAR_CANDIDATES, MORSE_MODULAR_FALSE, MORSE_SOURCE_COUNT,
    )
    if (
        magic, count, exhaustive_frames, witness_frame_count,
        last_witness_frame, modular_candidates, modular_false, source_count,
    ) != expected_header:
        raise AssertionError("Morse-certificate header changed")

    occurrences, occurrence_factor, factor_polynomial, factor_occurrence, _ = data
    frames = role_frames()
    parents = labeled.parent_bracket_factors()
    labels = tuple(label for label, _factor, _sign in parents)
    original_parent = tuple(
        sparse_poly.multiply(sparse_poly.constant(sign), factor)
        for _label, factor, sign in parents
    )
    if len(labels) != 62 or len(set(labels)) != 62:
        raise AssertionError("bad parent-bracket label order")

    position = header_size
    originals = []
    seen = set()
    witness_frames = set()
    fixed_format = "<HHHHHbB"
    fixed_size = struct.calcsize(fixed_format)
    for number in range(count):
        first, second, third, frame_index, variable_code, scalar, factor_count = (
            struct.unpack_from(fixed_format, raw, position)
        )
        position += fixed_size
        factor_indices = raw[position : position + factor_count]
        position += factor_count
        original = (first, second, third)
        if len(set(original)) != 3 or original in seen:
            raise AssertionError("duplicate or repeated-factor Morse certificate")
        seen.add(original)
        originals.append(original)
        if not 0 <= frame_index < len(frames):
            raise AssertionError("bad Morse role-frame index")
        witness_frames.add(frame_index)
        variables = (
            variable_code & 15,
            (variable_code >> 4) & 15,
            (variable_code >> 8) & 15,
        )
        if tuple(sorted(set(variables))) != variables or variables[-1] >= 9:
            raise AssertionError("bad Morse minor variables")
        mapping = labeled.triple_map(frames[frame_index])
        transformed = tuple(
            labeled.transform_factor(
                factor, mapping, factor_occurrence, occurrence_factor
            )
            for factor in original
        )
        minor = triple_verify.jacobian_minor(
            {
                row: factor_polynomial[factor]
                for row, factor in enumerate(transformed)
            },
            (0, 1, 2),
            variables,
        )
        product_polynomial = sparse_poly.constant(scalar)
        for factor_index in factor_indices:
            if factor_index >= len(original_parent):
                raise AssertionError("bad Morse parent-factor index")
            product_polynomial = sparse_poly.multiply(
                product_polynomial, original_parent[factor_index]
            )
        if minor != product_polynomial:
            raise AssertionError(f"failed Morse identity {number}")
        if (number + 1) % 5_000 == 0:
            print("PASS Morse identities", number + 1, "/", count)
    if position != len(raw):
        raise AssertionError("trailing Morse-certificate bytes")
    if len(witness_frames) != MORSE_WITNESS_FRAMES:
        raise AssertionError("Morse witness-frame count changed")
    if max(witness_frames) != MORSE_LAST_WITNESS_FRAME:
        raise AssertionError("Morse last witness frame changed")

    certificate_keys = np.fromiter(
        (
            first | (second << 16) | (third << 32)
            for first, second, third in originals
        ),
        dtype=np.uint64,
        count=len(originals),
    )
    provenance_replayed = False
    if source is not None:
        source_actual = sha256(source)
        if source_actual != MORSE_SOURCE_DIGEST:
            raise AssertionError(f"post-triangular source digest changed: {source_actual}")
        source_raw = source.read_bytes()
        stored_count, = struct.unpack_from("<I", source_raw)
        if stored_count != MORSE_SOURCE_COUNT or len(source_raw) != 4 + 6 * stored_count:
            raise AssertionError("bad post-triangular source")
        source_rows = np.frombuffer(source_raw, dtype="<u2", offset=4).reshape(-1, 3)
        source_keys = (
            source_rows[:, 0].astype(np.uint64)
            | (source_rows[:, 1].astype(np.uint64) << 16)
            | (source_rows[:, 2].astype(np.uint64) << 32)
        )
        if not np.all(np.isin(certificate_keys, source_keys, assume_unique=True)):
            raise AssertionError("Morse certificate outside post-triangular source")
        print("PASS Morse source membership", len(originals), MORSE_SOURCE_DIGEST)
        provenance_replayed = True
    if union4 is not None:
        union_actual = sha256(union4)
        if union_actual != BUCKET_DIGESTS[4]:
            raise AssertionError(f"union-four bucket digest changed: {union_actual}")
        feature_actual = sha256(TRIANGULAR_FEATURES)
        if feature_actual != TRIANGULAR_FEATURE_DIGEST:
            raise AssertionError(f"triangular-feature digest changed: {feature_actual}")
        feature_raw = TRIANGULAR_FEATURES.read_bytes()
        factor_count, = struct.unpack_from("<I", feature_raw)
        if factor_count != FACTOR_COUNT or len(feature_raw) != 4 + 4 * factor_count:
            raise AssertionError("bad triangular-feature artifact")
        features = tuple(
            struct.unpack_from("<HH", feature_raw, 4 + 4 * factor)
            for factor in range(factor_count)
        )
        unit_feature_count = 0
        zero_feature_count = 0
        for factor, (zero_mask, unit_mask) in enumerate(features):
            if zero_mask & unit_mask:
                raise AssertionError("overlapping triangular zero/unit feature")
            polynomial = factor_polynomial[factor]
            for variable in range(9):
                derivative = None
                if zero_mask >> variable & 1:
                    derivative = gradient_verify.derivative(polynomial, variable)
                    if derivative:
                        raise AssertionError("false triangular zero feature")
                    zero_feature_count += 1
                if unit_mask >> variable & 1:
                    if derivative is None:
                        derivative = gradient_verify.derivative(polynomial, variable)
                    if triple_verify.bracket_factorization(
                        derivative, parents, depth=20
                    ) is None:
                        raise AssertionError("false triangular unit feature")
                    unit_feature_count += 1
        print(
            "PASS exact triangular features",
            "zero", zero_feature_count, "unit", unit_feature_count,
        )
        union_raw = union4.read_bytes()
        union_count, = struct.unpack_from("<I", union_raw)
        if union_count != UNION_COUNTS[4] or len(union_raw) != 4 + 6 * union_count:
            raise AssertionError("bad union-four bucket")
        certificate_set = set(map(int, certificate_keys))
        found = set()
        closed = 0
        kept = 0
        source_digest = hashlib.sha256(struct.pack("<I", MORSE_SOURCE_COUNT))
        for index in range(union_count):
            factors = struct.unpack_from("<HHH", union_raw, 4 + 6 * index)
            if triangular_works(factors, features):
                closed += 1
                continue
            packed = struct.pack("<HHH", *factors)
            source_digest.update(packed)
            kept += 1
            key = factors[0] | (factors[1] << 16) | (factors[2] << 32)
            if key in certificate_set:
                found.add(key)
        if closed != TRIANGULAR_CLOSED_COUNT or kept != MORSE_SOURCE_COUNT:
            raise AssertionError("triangular union-four filter count changed")
        if source_digest.hexdigest() != MORSE_SOURCE_DIGEST:
            raise AssertionError("post-triangular source digest changed")
        if found != certificate_set:
            raise AssertionError("Morse certificate outside regenerated source")
        print(
            "PASS triangular filter", closed, "kept", kept,
            MORSE_SOURCE_DIGEST,
        )
        print("PASS Morse regenerated-source membership", len(found))
        provenance_replayed = True
    if not provenance_replayed:
        print(
            "PROVENANCE Morse source membership requires --morse-source or --morse-union4",
            MORSE_SOURCE_DIGEST,
        )
    print(
        "PASS Morse exact closures", count, actual,
        "witness_frames", len(witness_frames),
        "exhaustive_frames", exhaustive_frames,
    )
    print(
        "RECORDED full-sweep accounting (not compactly replayed)",
        "frames", exhaustive_frames,
        "modular", modular_candidates, "=", count, "+", modular_false,
    )
    print("MORSE_POST_TRIANGULAR_UNRESOLVED", MORSE_SOURCE_COUNT - count)
    print(
        "THEOREM_SAFE_WITH_TRIANGULAR_AND_MORSE",
        AFFINE_COUNT + UNION_COUNTS[2] + UNION_COUNTS[3]
        + TRIANGULAR_CLOSED_COUNT + count,
    )
    print("UNRESOLVED_AFTER_MORSE", TRIPLE_COUNT - (
        AFFINE_COUNT + UNION_COUNTS[2] + UNION_COUNTS[3]
        + TRIANGULAR_CLOSED_COUNT + count
    ))


def replay_residue(path: Path, data, bucket_directory: Path | None) -> None:
    actual = sha256(path)
    if actual != RESIDUE_DIGEST:
        raise AssertionError(f"affine residue digest changed: {actual}")
    occurrences, occurrence_factor, _, _, pairs = data
    minimal = minimal_incidence_masks(occurrences, occurrence_factor)
    raw = path.read_bytes()
    pair_count, = struct.unpack_from("<I", raw)
    if pair_count != PAIR_COUNT:
        raise AssertionError("bad residue header")

    digesters = {}
    files = {}
    for degree in (2, 3, 4):
        header = struct.pack("<I", UNION_COUNTS[degree])
        digesters[degree] = hashlib.sha256(header)
        if bucket_directory is not None:
            bucket_directory.mkdir(parents=True, exist_ok=True)
            target = bucket_directory / f"diag3_union_degree{degree}.bin"
            files[degree] = target.open("wb")
            files[degree].write(header)

    position = 4
    counts = Counter()
    partitions3 = Counter()
    for first, second in pairs:
        count, = struct.unpack_from("<I", raw, position)
        position += 4
        thirds = struct.unpack_from(f"<{count}H", raw, position) if count else ()
        position += 2 * count
        for third in thirds:
            factors = (first, second, third)
            degree, partition = best_union(factors, minimal)
            if degree not in (2, 3, 4):
                raise AssertionError(f"unexpected minimum union degree {degree}")
            packed = struct.pack("<HHH", *factors)
            digesters[degree].update(packed)
            if files:
                files[degree].write(packed)
            counts[degree] += 1
            if degree == 3:
                partitions3[partition] += 1
    for output in files.values():
        output.close()
    if position != len(raw):
        raise AssertionError("trailing residue bytes")
    if dict(counts) != UNION_COUNTS:
        raise AssertionError(f"union-degree census changed: {counts}")
    if dict(partitions3) != UNION3_PARTITIONS:
        raise AssertionError(f"union-three partitions changed: {partitions3}")
    if not all(partition_is_forest(partition) for partition in partitions3):
        raise AssertionError("a selected union-three partition is not a forest")
    matchings = {
        partition
        for partition in partitions3
        if partition_has_perfect_pencil_matching(partition)
    }
    if matchings != UNION3_PERFECT_MATCHINGS:
        raise AssertionError(f"union-three matching boundary changed: {matchings}")
    for degree in (2, 3, 4):
        digest = digesters[degree].hexdigest()
        if digest != BUCKET_DIGESTS[degree]:
            raise AssertionError(f"union-{degree} digest changed: {digest}")
        print("PASS union degree", degree, counts[degree], digest)
    print("PASS union-three forest partitions", dict(sorted(partitions3.items())))
    print("PASS union-three perfect pencil matchings", sorted(matchings))
    print("THEOREM_SAFE", AFFINE_COUNT + counts[2] + counts[3])
    print("UNRESOLVED_UNION4", counts[4])


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--residue", type=Path,
        help="replay a saved C++ affine-scan residue instead of rerunning it",
    )
    parser.add_argument(
        "--bucket-directory", type=Path,
        help="optionally export the three deterministic union-degree buckets",
    )
    parser.add_argument("--workers", type=int, help="OpenMP workers for full scan")
    parser.add_argument(
        "--skip-union-replay", action="store_true",
        help="stop after the memory-intensive affine scan",
    )
    parser.add_argument(
        "--morse-replay", action="store_true",
        help="replay the 65,550 compact exact role-frame minor identities",
    )
    parser.add_argument(
        "--morse-only", action="store_true",
        help="run only the compact exact Morse replay, not the affine census",
    )
    parser.add_argument(
        "--morse-source", type=Path,
        help=(
            "optionally verify the compact Morse records against the pinned "
            "1,885,400-row post-triangular union-four source"
        ),
    )
    parser.add_argument(
        "--morse-union4", type=Path,
        help=(
            "optionally regenerate the exact post-triangular source from a "
            "pinned union-degree-four bucket and verify Morse membership"
        ),
    )
    arguments = parser.parse_args()

    data = census_data()
    if arguments.morse_only:
        replay_morse_certificates(
            MORSE_CERTIFICATE, data,
            arguments.morse_source, arguments.morse_union4,
        )
        return
    if arguments.residue is None:
        temporary = tempfile.TemporaryDirectory(prefix="diag3-affine-residue-")
        residue = Path(temporary.name) / "residue.bin"
        run_full_scan(residue, data, arguments.workers)
    else:
        temporary = None
        residue = arguments.residue
    actual = sha256(residue)
    if actual != RESIDUE_DIGEST:
        raise AssertionError(f"affine residue digest changed: {actual}")
    print(
        "PASS affine/reframe census",
        TRIPLE_COUNT, AFFINE_COUNT, AFFINE_RESIDUE_COUNT,
        "standard", STANDARD_AFFINE_COUNT,
    )
    if not arguments.skip_union_replay:
        replay_residue(residue, data, arguments.bucket_directory)
    if (
        arguments.morse_replay
        or arguments.morse_source is not None
        or arguments.morse_union4 is not None
    ):
        replay_morse_certificates(
            MORSE_CERTIFICATE, data,
            arguments.morse_source, arguments.morse_union4,
        )
    if temporary is not None:
        temporary.cleanup()


if __name__ == "__main__":
    main()
