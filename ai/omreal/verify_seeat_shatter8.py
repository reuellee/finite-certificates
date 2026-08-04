#!/usr/bin/env python3
"""Arithmetic-only verifier for the parent-2599 exact eight-shatter.

The certificate supplies one parent chart for every binary pattern on eight
extension signatures.  A supported bit has an integer point in its strict
extension cone.  An unsupported bit has nonnegative integer Gordan weights
whose weighted signed normals sum to zero.  The verifier only evaluates
determinants, dot products, and these two kinds of certificates; it performs
no feasibility search and uses no floating-point arithmetic.
"""

from pathlib import Path

import numpy as np

import four_chart_gate as gate


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "seeat_parent2599_shatter8.npz"
EXPECTED_FORMAT = "seeat-parent2599-shatter8-v1"
SIGNATURES = 8
PATTERNS = 1 << SIGNATURES
TRIPLES = gate.colex_subsets(8, 3)
BASES = gate.colex_subsets(8, 4)


def determinant(matrix):
    """Recursive exact determinant, independent of the certificate producer."""
    matrix = [[int(value) for value in row] for row in matrix]
    if len(matrix) == 1:
        return matrix[0][0]
    total = 0
    for column, value in enumerate(matrix[0]):
        minor = [row[:column] + row[column + 1 :] for row in matrix[1:]]
        total += (-1 if column & 1 else 1) * value * determinant(minor)
    return total


def parent_signs_and_rows(matrix):
    parent_signs = []
    for basis in BASES:
        columns = matrix[:, np.asarray(basis) - 1]
        value = determinant(columns.tolist())
        if value == 0:
            raise AssertionError("stored parent chart is nonuniform")
        parent_signs.append("+" if value > 0 else "-")

    rows = []
    for triple in TRIPLES:
        columns = matrix[:, np.asarray(triple) - 1]
        row = []
        for coordinate in range(4):
            minor = np.delete(columns, coordinate, axis=0)
            row.append((-1) ** (coordinate + 5) * determinant(minor.tolist()))
        if not any(row):
            raise AssertionError("zero derived normal")
        rows.append(tuple(row))
    return "".join(parent_signs), rows


def verify_feasible(signed_rows, point):
    point = [int(value) for value in point]
    if not all(sum(a * x for a, x in zip(row, point, strict=True)) > 0
               for row in signed_rows):
        raise AssertionError("invalid strict-cone witness")


def verify_infeasible(signed_rows, weights):
    weights = [int(value) for value in weights]
    if not any(weights) or any(value < 0 for value in weights):
        raise AssertionError("invalid nonnegative Gordan weights")
    for coordinate in range(4):
        value = sum(
            weight * row[coordinate]
            for weight, row in zip(weights, signed_rows, strict=True)
        )
        if value != 0:
            raise AssertionError("Gordan weights do not annihilate the normals")


def main():
    certificate = np.load(CERTIFICATE, allow_pickle=False)
    required = {
        "format",
        "parent_index",
        "signature",
        "pattern_chart",
        "feasible_point",
        "gordan_weight",
    }
    if set(certificate.files) != required:
        raise AssertionError(f"wrong certificate fields: {sorted(certificate.files)}")
    if str(certificate["format"].item()) != EXPECTED_FORMAT:
        raise AssertionError("wrong certificate format")
    if int(certificate["parent_index"].item()) != gate.PARENT_INDEX:
        raise AssertionError("wrong parent index")

    signatures = certificate["signature"]
    charts = certificate["pattern_chart"]
    points = certificate["feasible_point"]
    weights = certificate["gordan_weight"]
    if signatures.shape != (SIGNATURES,) or len(set(map(int, signatures))) != SIGNATURES:
        raise AssertionError("need eight distinct extension signatures")
    if any(int(signature) >= 1 << len(TRIPLES) for signature in signatures):
        raise AssertionError("extension signature uses a nonexistent coordinate")
    if charts.shape != (PATTERNS, 4, 8) or not np.issubdtype(charts.dtype, np.integer):
        raise AssertionError(f"wrong chart array {charts.shape} {charts.dtype}")
    if points.shape != (PATTERNS, SIGNATURES, 4):
        raise AssertionError("wrong feasible-witness array")
    if weights.shape != (PATTERNS, SIGNATURES, len(TRIPLES)):
        raise AssertionError("wrong Gordan-witness array")
    if points.dtype.kind != "U" or weights.dtype.kind != "U":
        raise AssertionError("large integer certificates must be decimal strings")

    catalog = [
        line.strip()
        for line in gate.CATALOG_48.open(encoding="utf-8")
        if line.strip()
    ]
    expected_parent = catalog[gate.PARENT_INDEX]

    for pattern, matrix in enumerate(charts):
        got_parent, rows = parent_signs_and_rows(matrix)
        if got_parent != expected_parent:
            raise AssertionError(f"pattern {pattern}: chart is not parent 2599")

        for bit, signature_value in enumerate(signatures):
            signature = int(signature_value)
            signed_rows = [
                tuple(
                    coefficient if ((signature >> row_index) & 1) else -coefficient
                    for coefficient in row
                )
                for row_index, row in enumerate(rows)
            ]
            supported = bool((pattern >> bit) & 1)
            if supported:
                verify_feasible(signed_rows, points[pattern, bit])
                if any(int(value) for value in weights[pattern, bit]):
                    raise AssertionError("supported bit carries a negative certificate")
            else:
                verify_infeasible(signed_rows, weights[pattern, bit])
                if any(int(value) for value in points[pattern, bit]):
                    raise AssertionError("unsupported bit carries a positive witness")

        if (pattern + 1) % 32 == 0:
            print(f"  exact support patterns {pattern + 1}/{PATTERNS}")

    print("PASS eight realizable extension coordinates realize all 256 patterns")
    print("THEOREM: row 2599 chart supports shatter eight extension signatures")
    print("COROLLARY: the raw chart-support concept class has VC dimension >= 8")
    print("NOTE: this does not lower-bound a feasible COM completion that omits these states")


if __name__ == "__main__":
    main()
