#!/usr/bin/env python3
"""Exact compactification-atlas certificate for the row-2599 parent cell.

After fixing the first five projective columns, the remaining three columns
are positive projective 3-space coordinates.  Their closed sign orthants are
three simplices, so the ambient compactification is ``Delta^3 x Delta^3 x
Delta^3``.  Four gauge charts cover each simplex and give 64 product charts.

This verifier checks the parent chirotope signs, all stored exact samples,
the 64-chart transition cocycles, and the identification of every coordinate
boundary divisor with a genuine parent-bracket wall.  It does not construct
the residual-factor master subdivision inside this ambient atlas.
"""

from __future__ import annotations

import hashlib
from itertools import combinations, product
import json
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
sys.path.insert(0, str(HERE))

import DIAG9_GRAPH_exact_topes as topes  # noqa: E402
import verify_diag3_triple_rank_drop_parent_atlas as normalization  # noqa: E402


MANIFEST = DATA / "DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json"
CATALOG = HERE / "certs_4_8.jsonl"
POINT_BANK = DATA / "seeat_parent2599_upper178.npz"
PARENT = 2_599
EXPECTED_SEMANTIC = "3ea49efc628a88fda99e4070cbf43317b78cc45813beaba753c4404e961fa769"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_digest(payload):
    semantic = dict(payload)
    expected = semantic.pop("semantic_sha256")
    actual = hashlib.sha256(
        json.dumps(semantic, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    if expected != actual or actual != EXPECTED_SEMANTIC:
        raise AssertionError("compactification manifest semantic digest changed")
    return actual


def chirotope_coordinate_signs(record):
    basis_index = {basis: index for index, basis in enumerate(topes.BASES)}

    def sign(basis):
        return 1 if record["chi"][basis_index[basis]] == "+" else -1

    answer = []
    for moving in (5, 6, 7):
        row_signs = []
        for row in range(4):
            moving_basis = tuple(index for index in range(4) if index != row) + (
                moving,
            )
            fifth_basis = tuple(index for index in range(4) if index != row) + (4,)
            moving_zero = (1, 2, 3, moving)
            fifth_zero = (1, 2, 3, 4)
            # Normalize column five to (1,1,1,1), then normalize the moving
            # column's row-zero coordinate to one.  Determinant parities and
            # the frame determinant occur twice and cancel.
            row_signs.append(
                sign(moving_basis)
                * sign(fifth_basis)
                * sign(moving_zero)
                * sign(fifth_zero)
            )
        answer.append(tuple(row_signs))
    return tuple(answer)


def verify_sources(payload):
    for relative, expected in payload["source_sha256"].items():
        path = HERE.parent.parent / relative
        if sha256(path) != expected:
            raise AssertionError(f"compactification source changed: {relative}")
    records = [
        json.loads(line)
        for line in CATALOG.read_text(encoding="utf-8").splitlines()
        if line
    ]
    if len(records) != 2_628 or records[PARENT]["verdict"] != "REALIZABLE":
        raise AssertionError("parent-2599 catalog record changed")
    signs = chirotope_coordinate_signs(records[PARENT])
    expected_signs = tuple(
        tuple(row) for row in payload["normalized_coordinate_signs"]
    )
    if signs != expected_signs or signs != ((1, 1, 1, 1),) * 3:
        raise AssertionError("row-2599 is not the positive projective orthant")

    with np.load(POINT_BANK, allow_pickle=False) as source:
        matrices = np.asarray(source["chart_matrix"], dtype=np.int64)
    if matrices.shape != (178, 4, 8):
        raise AssertionError("row-2599 point-bank shape changed")
    identity = tuple(range(8))
    for matrix in matrices:
        normalized = normalization.normalized_matrix(matrix.tolist(), identity)
        for column in (5, 6, 7):
            gauge = normalized[column][0]
            coordinates = tuple(value / gauge for value in normalized[column])
            if coordinates[0] != 1 or not all(value > 0 for value in coordinates):
                raise AssertionError("a stored point left the positive simplex chart")
    return len(matrices), signs


def local_vector(row, source_gauge):
    answer = [0] * 4
    if row != source_gauge:
        answer[row] = 1
    return tuple(answer)


def transition_exponent(source_gauge, target_gauge, row):
    numerator = local_vector(row, source_gauge)
    denominator = local_vector(target_gauge, source_gauge)
    return tuple(
        left - right
        for left, right in zip(numerator, denominator, strict=True)
    )


def composed_exponent(source_gauge, middle_gauge, target_gauge, row):
    expression = transition_exponent(middle_gauge, target_gauge, row)
    answer = [0] * 4
    for middle_row, power in enumerate(expression):
        if not power:
            continue
        substitution = transition_exponent(
            source_gauge, middle_gauge, middle_row
        )
        for index, exponent in enumerate(substitution):
            answer[index] += power * exponent
    return tuple(answer)


def verify_atlas(payload):
    charts = tuple(product(range(4), repeat=3))
    atlas = payload["chart_atlas"]
    if (
        len(charts) != atlas["chart_count"]
        or len(charts) ** 2 != atlas["ordered_transition_count"]
        or len(charts) ** 3 != atlas["ordered_triple_cocycle_count"]
        or atlas["coordinates_per_chart"] != 9
    ):
        raise AssertionError("compactification chart census changed")

    cocycles = 0
    for source in charts:
        for middle in charts:
            for target in charts:
                for column in range(3):
                    for row in range(4):
                        if row == target[column]:
                            continue
                        direct = transition_exponent(
                            source[column], target[column], row
                        )
                        composed = composed_exponent(
                            source[column], middle[column], target[column], row
                        )
                        if direct != composed:
                            raise AssertionError("a chart transition cocycle failed")
                cocycles += 1
    if cocycles != 262_144:
        raise AssertionError("ordered chart-triple census changed")

    faces = payload["face_supports"]
    if faces != {
        "one_simplex_nonempty_supports": 15,
        "product_support_strata": 3_375,
        "standard_affine_infinity_support_strata": 2_863,
    }:
        raise AssertionError("simplex support-face census changed")
    if 15**3 != 3_375 or 15**3 - 8**3 != 2_863:
        raise AssertionError("simplex infinity count identity failed")
    return len(charts), cocycles


def expected_boundary_divisors():
    answer = []
    for moving_column in (6, 7, 8):
        for row in range(4):
            basis = tuple(
                index for index in (1, 2, 3, 4) if index != row + 1
            ) + (moving_column,)
            answer.append(
                {
                    "moving_column": moving_column,
                    "coordinate_row": row + 1,
                    "parent_bracket": "".join(map(str, basis)),
                    "determinant_sign": -1 if (3 - row) & 1 else 1,
                }
            )
    return answer


def verify_boundary(payload):
    expected = expected_boundary_divisors()
    if payload["boundary_divisors"] != expected:
        raise AssertionError("coordinate-divisor parent-bracket map changed")
    parent_labels = {
        "".join(str(index + 1) for index in basis)
        for basis in combinations(range(8), 4)
    }
    if any(record["parent_bracket"] not in parent_labels for record in expected):
        raise AssertionError("an atlas divisor is not a parent bracket")
    infinity = [
        record["parent_bracket"]
        for record in expected
        if record["coordinate_row"] == 1
    ]
    if payload["standard_chart"] != {
        "gauge_rows": [1, 1, 1],
        "infinity_parent_brackets": infinity,
    }:
        raise AssertionError("standard-chart infinity labels changed")
    return tuple(infinity)


def main():
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if payload["format"] != "diag3-pair-global-row2599-compactification-atlas-v1":
        raise AssertionError("wrong compactification manifest format")
    semantic = canonical_digest(payload)
    samples, signs = verify_sources(payload)
    charts, cocycles = verify_atlas(payload)
    infinity = verify_boundary(payload)
    print("PASS row-2599 normalized coordinate signs", signs)
    print("PASS exact positive-simplex normalization of", samples, "stored points")
    print("PASS compactification (Delta^3)^3 with", charts, "gauge charts")
    print("PASS all", cocycles, "ordered product-chart cocycles")
    print("PASS all 12 coordinate divisors are genuine parent-bracket walls")
    print("STANDARD_INFINITY", infinity)
    print("SEMANTIC_SHA256", semantic)
    print("SCOPE ambient atlas only; residual master-cell subdivision remains open")


if __name__ == "__main__":
    main()
