#!/usr/bin/env python3
"""Exact verifier for nonconvexity in a row-2599 contraction-height fiber.

Two positions of one deleted parent column support the same extension
signature.  Their vector midpoint preserves the parent chirotope but has a
positive Gordan dependence for that extension.

The difference of the two positions is itself a uniform extension column.
After contracting that column, the endpoints and midpoint give the same
projective configuration.  Two further exact row-2599 charts prove that the
two extension regions involved are proper and incomparable.  Thus the
certificate rules out naively iterating the convex contraction-height proof;
it is not a counterexample to the Nine-Diagonal Vanishing Lemma.
"""

from pathlib import Path

import numpy as np

import four_chart_gate as gate


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "seeat_parent2599_residence_nonconvex.npz"
SHATTER_CERTIFICATE = HERE / "data" / "seeat_parent2599_shatter8.npz"
FORMAT = "seeat-parent2599-residence-nonconvex-v1"
TRIPLES = gate.colex_subsets(8, 3)
BASES = gate.colex_subsets(8, 4)

# Exact witnesses on two integer charts already stored in the eight-shatter
# artifact.  Chart 1 lies in F_sigma1 minus F_sigma2; chart 88 lies in the
# reverse difference.  Sparse Gordan vectors are stored as (row, weight).
INCOMPARABILITY = {
    1: {
        "sigma1_point": (
            -61149119555748,
            -80785760358979,
            -120671006459873,
            55173560531549,
        ),
        "sigma2_gordan": (
            (4, 241018253000),
            (10, 29089741073),
            (13, 80236960211),
            (36, 59033807700),
        ),
    },
    88: {
        "sigma2_point": (
            644964985917,
            -13121876984796,
            873653585795,
            -1362653890560,
        ),
        "sigma1_gordan": (
            (3, 1732912764808632),
            (5, 491211609776191),
            (14, 1358329733694120),
            (28, 802984201548558),
            (41, 6266627070618145),
        ),
    },
}


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


def extension_signature(parent, point):
    """Return the strict extension signature of ``point`` over ``parent``."""
    _, rows = parent_signs_and_rows(parent)
    values = [
        sum(int(a) * int(x) for a, x in zip(row, point, strict=True))
        for row in rows
    ]
    if any(value == 0 for value in values):
        raise AssertionError("extension column is not uniform")
    return sum(1 << bit for bit, value in enumerate(values) if value > 0)


def sparse_weights(entries):
    """Expand a sparse list of Gordan weights in the 56-row ordering."""
    weights = [0] * len(TRIPLES)
    for row, weight in entries:
        if not 0 <= row < len(weights) or weights[row] or weight <= 0:
            raise AssertionError("invalid sparse Gordan vector")
        weights[row] = weight
    return weights


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
    sigma2 = int(certificate["signature"].item())
    if not 0 <= deleted < 8 or fixed.shape != (4, 7):
        raise AssertionError("wrong deletion data")
    if not all(np.issubdtype(array.dtype, np.integer) for array in (fixed, left, right, midpoint)):
        raise AssertionError("configuration coordinates must be integral")
    if left.shape != (4,) or right.shape != (4,) or midpoint.shape != (4,):
        raise AssertionError("wrong residence point shape")
    if not np.array_equal(midpoint, left + right):
        raise AssertionError("stored midpoint is not the vector midpoint up to scale")
    if not 0 <= sigma2 < 1 << 56:
        raise AssertionError("invalid extension signature")

    catalog = [
        line.strip()
        for line in gate.CATALOG_48.open(encoding="utf-8")
        if line.strip()
    ]
    expected_parent = catalog[gate.PARENT_INDEX]
    positions = (left, right, midpoint)
    systems = []
    parents = []
    for label, position in zip(("left", "right", "midpoint"), positions, strict=True):
        parent = insert(fixed, deleted, position)
        parent_signs, rows = signed_rows(parent, sigma2)
        if parent_signs != expected_parent:
            raise AssertionError(f"{label} does not realize parent 2599")
        parents.append(parent)
        systems.append(rows)

    if not strict_witness(systems[0], certificate["left_point"]):
        raise AssertionError("invalid left extension witness")
    if not strict_witness(systems[1], certificate["right_point"]):
        raise AssertionError("invalid right extension witness")
    if not gordan_witness(systems[2], certificate["midpoint_gordan"]):
        raise AssertionError("invalid midpoint Gordan certificate")

    # The first extension column is the endpoint difference.  Its brackets
    # are strict and have one common signature over the endpoints and their
    # projective midpoint.
    contraction_column = left - right
    sigma1_values = [
        extension_signature(parent, contraction_column) for parent in parents
    ]
    if len(set(sigma1_values)) != 1:
        raise AssertionError("endpoint difference changes extension signature")
    sigma1 = sigma1_values[0]
    if sigma1 == sigma2:
        raise AssertionError("the two extension signatures must be distinct")

    # Modulo the line spanned by contraction_column, left and right agree,
    # while midpoint has the same oriented projective image with scale two.
    # Since midpoint/2=(left+right)/2, it is literally the affine midpoint of
    # the two normalized lift heights over this one contracted configuration.
    if not np.array_equal(left, right + contraction_column):
        raise AssertionError("left and right do not agree after contraction")
    if not np.array_equal(midpoint, 2 * right + contraction_column):
        raise AssertionError("midpoint has a different contracted image")

    shatter = np.load(SHATTER_CERTIFICATE, allow_pickle=False)
    if "pattern_chart" not in shatter.files:
        raise AssertionError("shatter artifact has no chart array")
    charts = shatter["pattern_chart"]
    if charts.shape != (256, 4, 8) or not np.issubdtype(charts.dtype, np.integer):
        raise AssertionError("wrong shatter chart array")

    chart1 = charts[1]
    chart1_parent, chart1_sigma1 = signed_rows(chart1, sigma1)
    _, chart1_sigma2 = signed_rows(chart1, sigma2)
    if chart1_parent != expected_parent:
        raise AssertionError("incomparability chart 1 is not parent 2599")
    if not strict_witness(
        chart1_sigma1, INCOMPARABILITY[1]["sigma1_point"]
    ):
        raise AssertionError("chart 1 does not realize sigma1")
    if not gordan_witness(
        chart1_sigma2,
        sparse_weights(INCOMPARABILITY[1]["sigma2_gordan"]),
    ):
        raise AssertionError("chart 1 does not exclude sigma2")

    chart88 = charts[88]
    chart88_parent, chart88_sigma1 = signed_rows(chart88, sigma1)
    _, chart88_sigma2 = signed_rows(chart88, sigma2)
    if chart88_parent != expected_parent:
        raise AssertionError("incomparability chart 88 is not parent 2599")
    if not strict_witness(
        chart88_sigma2, INCOMPARABILITY[88]["sigma2_point"]
    ):
        raise AssertionError("chart 88 does not realize sigma2")
    if not gordan_witness(
        chart88_sigma1,
        sparse_weights(INCOMPARABILITY[88]["sigma1_gordan"]),
    ):
        raise AssertionError("chart 88 does not exclude sigma1")

    print("PASS endpoints and midpoint are exact row-2599 parent charts")
    print("PASS sigma2 is feasible at both endpoints and Gordan-infeasible at midpoint")
    print("PASS the endpoint difference realizes one common uniform sigma1")
    print("PASS all three charts have one identical contraction by the sigma1 column")
    print("PASS exact charts prove F_sigma1 and F_sigma2 proper and incomparable")
    print("THEOREM: extra-extension feasibility is nonconvex in one contraction-height fiber")
    print("NOTE: this obstructs naive iteration; it is not a counterexample to 9DVL")


if __name__ == "__main__":
    main()
