#!/usr/bin/env python3
"""Corrected full-occurrence Gale audit for the six hard factor triples.

This is a no-go verifier, not a diagonal-three proof.  It evaluates a full
homogeneous residual occurrence on the unnormalized Gale kernel matrix
``[-A^T | I]``.  It deliberately does not complement the gauge-normalized
bracket formulas for primitive factors.
"""

from __future__ import annotations

import argparse
from collections import Counter
import hashlib
from itertools import combinations, permutations
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
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as gradient  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY as triples  # noqa: E402
import DIAG9_GRAPH_global_factor_census as global_factors  # noqa: E402
import verify_diag3_projective_column_fiber_scan as column_scan  # noqa: E402


FACTOR_COUNT = 26_740
CANARY_FRAME_COUNT = 241_920
POLYDB_DIGEST = "9b508dcbcadca9029d86866844ef33698ab256d2aeea37f63fadaf2bad802f50"
CANARY_DIGEST = "fd688604376a65eddc8adac7dd1f1ad8bbc82444e3499e2ee7bf551f91d5da38"
FEATURE_DIGEST = "5b510bb9aeb0229e7ab201b2cab8abef910d3b8c9dbb3f762eca729ed8bd0d56"
EXPECTED_FACTOR_TERMS = 637_044
EXPECTED_PARENT_TERMS = 201
EXPECTED_UNIT_HISTOGRAM = {0: 25_620, 1: 1_120}
EXPECTED_AFFINE_NONZERO = 26_128
EXPECTED_AFFINE_BITS = 429_696
EXPECTED_FEATURE_CLASSES = 3_001
EXPECTED_UNIT_FACTORS = 23_436
EXPECTED_UNIT_BITS = 64_260
EXPECTED_ZERO_BITS = 41_400

HARD = (
    (2_277, 390, 22_507),
    (5_563, 16_134, 19_284),
    (12_985, 16_183, 7_196),
    (20_355, 5_442, 5_949),
    (9_667, 16_486, 26_315),
    (9_758, 24_338, 15_810),
)

CPP = HERE / "verify_diag3_triple_gale_canary_no_go.cpp"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def pack_exponent(exponent):
    if len(exponent) != 9 or any(value < 0 or value > 3 for value in exponent):
        raise AssertionError(f"exponent does not fit two-bit encoding: {exponent}")
    return sum(value << (2 * index) for index, value in enumerate(exponent))


def write_family(output, polynomials):
    offsets = [0]
    terms = []
    for polynomial in polynomials:
        terms.extend(
            (pack_exponent(exponent), int(coefficient))
            for exponent, coefficient in sorted(polynomial.items())
        )
        offsets.append(len(terms))
    output.write(struct.pack("<II", len(polynomials), len(terms)))
    output.write(struct.pack(f"<{len(offsets)}I", *offsets))
    for exponent, coefficient in terms:
        if not -127 <= coefficient <= 127:
            raise AssertionError(f"coefficient does not fit int8: {coefficient}")
        output.write(struct.pack("<Ib", exponent, coefficient))
    return len(terms)


def gale_kernel(matrix):
    """Return [-A^T|I] for M=[I|A], without rational renormalization."""
    one, zero = global_factors.constant(1), global_factors.constant(0)
    right = tuple(
        tuple(matrix[row][4 + column] for column in range(4))
        for row in range(4)
    )
    answer = tuple(
        tuple(
            (
                {monomial: -coefficient for monomial, coefficient in right[column][row].items()}
                if column < 4
                else one if column - 4 == row
                else zero
            )
            for column in range(8)
        )
        for row in range(4)
    )
    for row in range(4):
        for dual_row in range(4):
            product = {}
            for column in range(8):
                product = global_factors.add(
                    product,
                    global_factors.multiply(matrix[row][column], answer[dual_row][column]),
                )
            if product:
                raise AssertionError("M times Gale-kernel transpose is nonzero")
    return answer


def corrected_pullbacks():
    occurrences, occurrence_factor, _primal = labeled.factor_polynomials()
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    matrix = global_factors.normalized_matrix()
    gale = gale_kernel(matrix)
    normals = tuple(
        global_factors.normal(gale, support) for support in labeled.TRIPLES
    )
    parents = global_factors.bracket_records(matrix)
    polynomials = []
    unit_histogram = Counter()
    for factor in range(FACTOR_COUNT):
        full_occurrence = global_factors.primitive(
            global_factors.derived(normals, factor_occurrence[factor])
        )
        quotient, units = global_factors.strip_parent_units(
            full_occurrence, parents
        )
        if not quotient:
            raise AssertionError(f"zero corrected Gale pullback at factor {factor}")
        polynomials.append(quotient)
        unit_histogram[len(units)] += 1
    if dict(unit_histogram) != EXPECTED_UNIT_HISTOGRAM:
        raise AssertionError(f"Gale occurrence-unit histogram changed: {unit_histogram}")
    print(
        "PASS corrected full-occurrence Gale pullbacks", len(polynomials),
        "unit_histogram", dict(sorted(unit_histogram.items())),
    )
    return (
        occurrences, occurrence_factor, factor_occurrence,
        tuple(polynomials), tuple(polynomial for _label, polynomial, _sign in labeled.parent_bracket_factors()),
    )


def canary_frames(occurrences, occurrence_factor, factor_occurrence):
    rows = set()
    for permutation in permutations(range(8)):
        mapping = labeled.triple_map(permutation)
        for canary in HARD:
            rows.add(tuple(
                labeled.transform_factor(
                    factor, mapping, factor_occurrence, occurrence_factor
                )
                for factor in canary
            ))
    rows = tuple(sorted(rows))
    if len(rows) != CANARY_FRAME_COUNT:
        raise AssertionError(f"corrected Gale canary-frame count changed: {len(rows)}")
    return rows


def write_polydb(path: Path, polynomials, parent_polynomials):
    with path.open("wb") as output:
        output.write(b"D3MWPOL1")
        factor_terms = write_family(output, polynomials)
        parent_terms = write_family(output, parent_polynomials)
    if (
        factor_terms != EXPECTED_FACTOR_TERMS
        or parent_terms != EXPECTED_PARENT_TERMS
        or sha256(path) != POLYDB_DIGEST
    ):
        raise AssertionError(
            f"corrected Gale polynomial database changed: "
            f"{factor_terms}/{parent_terms}/{sha256(path)}"
        )
    print("PASS corrected Gale polynomial database", sha256(path))


def write_canaries(path: Path, rows):
    with path.open("wb") as output:
        output.write(struct.pack("<I", len(rows)))
        for row in rows:
            output.write(struct.pack("<HHH", *row))
    if sha256(path) != CANARY_DIGEST:
        raise AssertionError(f"corrected Gale canary rows changed: {sha256(path)}")
    print("PASS six-canary all-S8 rows", len(rows), sha256(path))


def affinity_no_go(polynomials, rows):
    masks = np.asarray(
        tuple(column_scan.affinity_mask(polynomial) for polynomial in polynomials),
        dtype=object,
    )
    if (
        sum(bool(mask) for mask in masks) != EXPECTED_AFFINE_NONZERO
        or sum(mask.bit_count() for mask in masks) != EXPECTED_AFFINE_BITS
    ):
        raise AssertionError("corrected Gale affinity-mask census changed")
    packed_rows = np.asarray(rows, dtype=np.uint16)
    common = masks[packed_rows[:, 0]] & masks[packed_rows[:, 1]] & masks[packed_rows[:, 2]]
    survivors = sum(bool(mask) for mask in common)
    if survivors:
        raise AssertionError(f"corrected Gale square-affine canary survivor: {survivors}")
    print(
        "PASS corrected Gale square-affine no-go", len(rows),
        "factor_masks", EXPECTED_AFFINE_NONZERO, "bits", EXPECTED_AFFINE_BITS,
    )


def triangular_no_go(path: Path, polynomials, rows):
    parent_factors = labeled.parent_bracket_factors()
    features = []
    classes = Counter()
    for polynomial in polynomials:
        zero_mask = 0
        unit_mask = 0
        for variable in range(9):
            derivative = gradient.derivative(polynomial, variable)
            if not derivative:
                zero_mask |= 1 << variable
            elif triples.bracket_factorization(
                derivative, parent_factors, depth=20
            ) is not None:
                unit_mask |= 1 << variable
        features.append((zero_mask, unit_mask))
        classes[(zero_mask, unit_mask)] += 1
    with path.open("wb") as output:
        output.write(struct.pack("<I", len(features)))
        for feature in features:
            output.write(struct.pack("<HH", *feature))
    accounting = (
        len(classes),
        sum(bool(unit) for _zero, unit in features),
        sum(unit.bit_count() for _zero, unit in features),
        sum(zero.bit_count() for zero, _unit in features),
    )
    expected = (
        EXPECTED_FEATURE_CLASSES, EXPECTED_UNIT_FACTORS,
        EXPECTED_UNIT_BITS, EXPECTED_ZERO_BITS,
    )
    if accounting != expected or sha256(path) != FEATURE_DIGEST:
        raise AssertionError(
            f"corrected Gale triangular features changed: {accounting}/{sha256(path)}"
        )
    survivors = [
        row for row in rows if column_scan.triangular_works(row, features)
    ]
    if survivors:
        raise AssertionError(f"corrected Gale triangular canary survivors: {survivors[:3]}")
    print(
        "PASS corrected Gale triangular no-go", len(rows),
        "feature_digest", sha256(path),
    )


def modular_minor_no_go(polydb: Path, canaries: Path, workers: int | None):
    with tempfile.TemporaryDirectory(prefix="diag3-gale-canary-cpp-") as directory_name:
        directory = Path(directory_name)
        executable = directory / "screen"
        output = directory / "candidates.bin"
        subprocess.run(
            [
                "g++", "-O3", "-std=c++17", "-fopenmp",
                str(CPP), "-o", str(executable),
            ],
            check=True,
        )
        environment = dict(os.environ)
        if workers is not None:
            environment["OMP_NUM_THREADS"] = str(workers)
        subprocess.run(
            [str(executable), str(polydb), str(canaries), str(output)],
            check=True, env=environment,
        )
        raw = output.read_bytes()
        count, = struct.unpack_from("<Q", raw)
        if count or len(raw) != 8:
            raise AssertionError("corrected Gale modular no-go produced a candidate")
    print("PASS corrected Gale coordinate-minor no-go", 20_321_280)
    print("PASS corrected Gale decomposable-shear no-go", 365_783_040)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, help="OpenMP workers for the modular screens")
    parser.add_argument(
        "--fast", action="store_true",
        help="skip exact triangular features and the modular minor/shear screens",
    )
    arguments = parser.parse_args()

    with tempfile.TemporaryDirectory(prefix="diag3-corrected-gale-") as directory_name:
        directory = Path(directory_name)
        occurrences, occurrence_factor, factor_occurrence, polynomials, parents = (
            corrected_pullbacks()
        )
        rows = canary_frames(occurrences, occurrence_factor, factor_occurrence)
        polydb = directory / "polynomials.bin"
        canaries = directory / "canaries.bin"
        write_polydb(polydb, polynomials, parents)
        write_canaries(canaries, rows)
        affinity_no_go(polynomials, rows)
        if arguments.fast:
            print("SCOPE fast mode skips triangular and modular minor/shear no-go screens")
            return
        triangular_no_go(directory / "features.bin", polynomials, rows)
        modular_minor_no_go(polydb, canaries, arguments.workers)
    print("NO_GO corrected Gale plus S8 closes none of the six hard canaries")


if __name__ == "__main__":
    main()
