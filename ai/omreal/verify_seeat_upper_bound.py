#!/usr/bin/env python3
"""Exact, search-free verifier for the parent-2599 chart upper bound.

The search that selected the charts is outside the trust boundary.  This
verifier checks, using integer arithmetic only, that every stored chart
realizes catalog parent 2599 and that the assigned integer point realizes the
claimed extension signature over that chart.
"""

from pathlib import Path

import numpy as np

import four_chart_gate as gate


HERE = Path(__file__).resolve().parent
EXPECTED_CHARTS = 178


def determinant(matrix):
    """Recursive exact determinant for the 3x3 and 4x4 matrices used here."""
    matrix = [[int(value) for value in row] for row in matrix]
    if len(matrix) == 1:
        return matrix[0][0]
    total = 0
    for column, value in enumerate(matrix[0]):
        minor = [row[:column] + row[column + 1 :] for row in matrix[1:]]
        total += (-1 if column & 1 else 1) * value * determinant(minor)
    return total


def chart_rows_and_parent(matrix):
    """Return the parent signs and the 56 derived hyperplane rows."""
    parent_signs = []
    for basis in gate.colex_subsets(8, 4):
        submatrix = matrix[:, np.asarray(basis) - 1]
        value = determinant(submatrix.tolist())
        if value == 0:
            raise RuntimeError("chart parent matrix is not uniform")
        parent_signs.append(1 if value > 0 else 0)

    rows = []
    for triple in gate.colex_subsets(8, 3):
        columns = matrix[:, np.asarray(triple) - 1]
        row = []
        for coordinate in range(4):
            minor = np.delete(columns, coordinate, axis=0)
            value = (-1) ** (coordinate + 5) * determinant(minor.tolist())
            row.append(value)
        rows.append(tuple(row))
    return np.asarray(parent_signs, dtype=np.uint8), rows


def main():
    certificate_path = HERE / "data" / "seeat_parent2599_upper178.npz"
    certificate = np.load(certificate_path, allow_pickle=False)
    required = {"format", "parent_index", "chart_matrix", "assignment", "point"}
    if set(certificate.files) != required:
        raise SystemExit(f"wrong certificate fields: {sorted(certificate.files)}")
    if str(certificate["format"].item()) != "seeat-parent2599-upper-cover-v1":
        raise SystemExit("wrong certificate format")
    if int(certificate["parent_index"].item()) != gate.PARENT_INDEX:
        raise SystemExit("wrong parent index")

    parents = [
        line.strip() for line in gate.CATALOG_48.open(encoding="utf-8")
        if line.strip()
    ]
    parent_bits, signatures = gate.enumerate_extensions(parents[gate.PARENT_INDEX])
    charts = certificate["chart_matrix"]
    assignment = certificate["assignment"]
    points = certificate["point"]
    if charts.shape != (EXPECTED_CHARTS, 4, 8):
        raise SystemExit(f"wrong chart shape {charts.shape}")
    if assignment.shape != (len(signatures),):
        raise SystemExit(f"wrong assignment shape {assignment.shape}")
    if points.shape != (len(signatures), 4):
        raise SystemExit(f"wrong point shape {points.shape}")
    if int(assignment.max()) >= len(charts):
        raise SystemExit("assignment references a missing chart")
    if not np.issubdtype(charts.dtype, np.integer):
        raise SystemExit("chart matrices must be integral")
    if not np.issubdtype(points.dtype, np.integer):
        raise SystemExit("extension points must be integral")

    derived_rows = []
    for index, matrix in enumerate(charts):
        got_parent, rows = chart_rows_and_parent(matrix)
        if not np.array_equal(got_parent, parent_bits):
            raise SystemExit(f"chart {index} does not realize parent 2599")
        derived_rows.append(rows)
    print(f"PASS {EXPECTED_CHARTS} exact parent realization matrices")

    for index, (signature, chart_index, point) in enumerate(
        zip(signatures, assignment.astype(int), points), 1
    ):
        got_signature = 0
        for bit, row in enumerate(derived_rows[chart_index]):
            value = sum(int(coefficient) * int(x) for coefficient, x in zip(row, point))
            if value == 0:
                raise SystemExit(
                    f"signature {index - 1}: point lies on derived hyperplane {bit}"
                )
            if value > 0:
                got_signature |= 1 << bit
        if got_signature != signature:
            raise SystemExit(f"signature {index - 1}: exact point has the wrong signs")
        if index % 10_000 == 0:
            print(f"  exact extension witnesses {index}/{len(signatures)}")

    print("PASS all 97,224 extension signatures assigned with exact integer points")
    print("THEOREM: atlas width(parent 2599) <= 178")
    print("COMBINED WITH LOWER BOUND: 5 <= atlas width(parent 2599) <= 178")


if __name__ == "__main__":
    main()
