#!/usr/bin/env python3
"""Exact verifier for nonconvexity in a row-2599 deletion fiber.

Two positions of one deleted parent column support the same extension
signature.  Their vector midpoint preserves the parent chirotope but has a
positive Gordan dependence for that extension.  This rules out a proposed
fiberwise-convex proof of the Extension--Helly conjecture.
"""

from pathlib import Path

import numpy as np

import four_chart_gate as gate


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "seeat_parent2599_residence_nonconvex.npz"
FORMAT = "seeat-parent2599-residence-nonconvex-v1"
TRIPLES = gate.colex_subsets(8, 3)
BASES = gate.colex_subsets(8, 4)


def determinant(matrix):
    matrix = [[int(value) for value in row] for row in matrix]
    if len(matrix) == 1:
        return matrix[0][0]
    return sum(
        (-1 if column & 1 else 1)
        * value
        * determinant([row[:column] + row[column + 1 :] for row in matrix[1:]])
        for column, value in enumerate(matrix[0])
    )


def parent_signs_and_rows(matrix):
    parent_signs = []
    for basis in BASES:
        columns = matrix[:, np.asarray(basis) - 1]
        value = determinant(columns.tolist())
        if value == 0:
            raise AssertionError("parent chart is nonuniform")
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


def insert(fixed, deleted, point):
    return np.concatenate(
        (fixed[:, :deleted], point[:, None], fixed[:, deleted:]), axis=1
    )


def signed_rows(parent, signature):
    parent_signs, rows = parent_signs_and_rows(parent)
    return parent_signs, [
        tuple(value if (signature >> bit) & 1 else -value for value in row)
        for bit, row in enumerate(rows)
    ]


def strict_witness(rows, point):
    point = [int(value) for value in point]
    return all(
        sum(a * x for a, x in zip(row, point, strict=True)) > 0 for row in rows
    )


def gordan_witness(rows, weights):
    weights = [int(value) for value in weights]
    return (
        any(weights)
        and all(value >= 0 for value in weights)
        and all(
            sum(
                weight * row[coordinate]
                for weight, row in zip(weights, rows, strict=True)
            )
            == 0
            for coordinate in range(4)
        )
    )


def main():
    certificate = np.load(CERTIFICATE, allow_pickle=False)
    required = {
        "format",
        "parent_index",
        "deleted",
        "fixed",
        "left",
        "right",
        "midpoint",
        "signature",
        "left_point",
        "right_point",
        "midpoint_gordan",
    }
    if set(certificate.files) != required:
        raise AssertionError(f"wrong certificate fields: {sorted(certificate.files)}")
    if str(certificate["format"].item()) != FORMAT:
        raise AssertionError("wrong certificate format")
    if int(certificate["parent_index"].item()) != gate.PARENT_INDEX:
        raise AssertionError("wrong parent index")

    deleted = int(certificate["deleted"].item())
    fixed = certificate["fixed"]
    left = certificate["left"]
    right = certificate["right"]
    midpoint = certificate["midpoint"]
    signature = int(certificate["signature"].item())
    if not 0 <= deleted < 8 or fixed.shape != (4, 7):
        raise AssertionError("wrong deletion data")
    if not all(np.issubdtype(array.dtype, np.integer) for array in (fixed, left, right, midpoint)):
        raise AssertionError("configuration coordinates must be integral")
    if left.shape != (4,) or right.shape != (4,) or midpoint.shape != (4,):
        raise AssertionError("wrong residence point shape")
    if not np.array_equal(midpoint, left + right):
        raise AssertionError("stored midpoint is not the vector midpoint up to scale")
    if not 0 <= signature < 1 << 56:
        raise AssertionError("invalid extension signature")

    catalog = [
        line.strip()
        for line in gate.CATALOG_48.open(encoding="utf-8")
        if line.strip()
    ]
    expected_parent = catalog[gate.PARENT_INDEX]
    positions = (left, right, midpoint)
    systems = []
    for label, position in zip(("left", "right", "midpoint"), positions, strict=True):
        parent = insert(fixed, deleted, position)
        parent_signs, rows = signed_rows(parent, signature)
        if parent_signs != expected_parent:
            raise AssertionError(f"{label} does not realize parent 2599")
        systems.append(rows)

    if not strict_witness(systems[0], certificate["left_point"]):
        raise AssertionError("invalid left extension witness")
    if not strict_witness(systems[1], certificate["right_point"]):
        raise AssertionError("invalid right extension witness")
    if not gordan_witness(systems[2], certificate["midpoint_gordan"]):
        raise AssertionError("invalid midpoint Gordan certificate")

    print("PASS endpoints and midpoint are exact row-2599 parent charts")
    print("PASS the extension is feasible at both endpoints")
    print("PASS the extension is Gordan-infeasible at their midpoint")
    print("THEOREM: this extension-feasibility region is nonconvex in one deletion fiber")


if __name__ == "__main__":
    main()
