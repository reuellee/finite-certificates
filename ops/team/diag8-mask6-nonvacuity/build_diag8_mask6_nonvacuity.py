#!/usr/bin/env python3
"""Build the exact parent-860 mask-6 nonvacuity certificate.

The seven rational charts were selected by a seeded discovery search, then
frozen below.  Publication depends only on exact parent signs, recursive tope
witnesses, and exact positive Gordan relations.
"""

from __future__ import annotations

from fractions import Fraction
from math import gcd, lcm
from pathlib import Path
import sys

import numpy as np
from scipy.optimize import linprog
import sympy as sp


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OMREAL = ROOT / "ai" / "omreal"
sys.path.insert(0, str(OMREAL))

import DIAG9_GRAPH_exact_topes as exact_topes  # noqa: E402
import DIAG9_GRAPH_parent860_star as star  # noqa: E402


OUTPUT = HERE / "DIAG8_MASK6_NONVACUITY_CERTIFICATE.npz"
FORMAT = "diag8-mask6-nonvacuity-v2"
FAMILY = (
    34_895_220_708_312_748,
    34_850_557_309_758_184,
    34_850_557_307_726_570,
    34_850_557_039_028_936,
    34_850_539_394_645_193,
    34_850_144_722_168_960,
    34_754_553_013_114_532,
    34_206_807_699_455_377,
)
LOOP = (4, 11, 12, 14, 13, 23)
CHART_INDEXES = (2, 3, 12, 23, 29, 33, 34)
PATTERNS = (
    "00110011",
    "11101111",
    "10101110",
    "01011101",
    "11010111",
    "10101001",
    "11110010",
)
CHARTS = tuple(
    tuple(map(Fraction, row.split()))
    for row in (
        "485973/38645000 51645027/55347500 -45238923/169645000 19183253/63646250 917245191/729235000 61554413/159655000 -9479377/39235000 51895407/112385000 4860711/12302500",
        "27729/3864500 103799251/110695000 -45374639/169645000 18775917/63646250 461904153/364617500 7570569/19956875 -947153/3923500 24857569/56192500 4900079/12302500",
        "165019/15458000 105437537/110695000 -90715349/339290000 39944933/127292500 925704317/729235000 2945207/7982750 -374153/1569400 99317891/224770000 10110181/24605000",
        "162851/3091600 106234541/110695000 -40896011/169645000 144250047/509170000 1915727161/1458470000 12834551/31931000 -18291759/78470000 24722707/56192500 2045657/4921000",
        "271/1545800 20874973/22139000 -4534071/16964500 1447083/5091700 368619071/291694000 4961393/12772400 -787541/3138800 1019477/2247700 995763/2460500",
        "74103/3864500 10426417/11069500 -1175929/4241125 14980/50917 184965847/145847000 11748897/31931000 -1933541/7847000 4782707/11238500 1917711/4921000",
        "2271/1932250 210365877/221390000 -88543893/339290000 154229779/509170000 366868907/291694000 7698293/19956875 -9008557/39235000 6321158/14048125 19526501/49210000",
    )
)


def primitive(values):
    values = tuple(map(int, values))
    divisor = 0
    for value in values:
        divisor = gcd(divisor, abs(value))
    divisor = max(divisor, 1)
    return tuple(value // divisor for value in values)


def signed_rows(rows, signature):
    return tuple(
        tuple((1 if signature >> bit & 1 else -1) * value for value in row)
        for bit, row in enumerate(rows)
    )


def positive_gordan_relation(rows):
    matrix = np.asarray(rows, dtype=float)
    scale = np.linalg.norm(matrix, axis=1)
    normalized = matrix / scale[:, None]
    equality = np.vstack((normalized.T, np.ones(len(rows))))
    target = np.asarray((0.0, 0.0, 0.0, 0.0, 1.0))
    result = linprog(
        np.linspace(0.0, 1e-7, len(rows)),
        A_eq=equality,
        b_eq=target,
        bounds=(0.0, None),
        method="highs",
    )
    if not result.success:
        raise AssertionError("infeasible signature lacks a numerical Gordan seed")
    support = tuple(index for index, value in enumerate(result.x) if value > 1e-8)
    if not 2 <= len(support) <= 5:
        raise AssertionError(f"nonbasic Gordan support: {len(support)}")
    kernel = sp.Matrix([rows[index] for index in support]).T.nullspace()
    if len(kernel) != 1:
        raise AssertionError("Gordan seed is not support-minimal")
    vector = tuple(Fraction(value) for value in kernel[0])
    if all(value < 0 for value in vector):
        vector = tuple(-value for value in vector)
    if not all(value > 0 for value in vector):
        raise AssertionError("Gordan kernel is not positive")
    denominator = 1
    for value in vector:
        denominator = lcm(denominator, value.denominator)
    weights = primitive(value * denominator for value in vector)
    if not all(value > 0 for value in weights):
        raise AssertionError("nonpositive exact Gordan weight")
    if any(
        sum(weight * rows[index][coordinate] for index, weight in zip(support, weights))
        for coordinate in range(4)
    ):
        raise AssertionError("exact Gordan relation failed")
    return support, weights


def string_array(values):
    return np.asarray(values, dtype=str)


def build():
    expected_parent = exact_topes.parent_signs(
        star.matrix_from_coordinates(star.normalized_parent())
    )
    feasible_points = []
    gordan_supports = []
    gordan_weights = []
    for chart, expected_pattern in zip(CHARTS, PATTERNS):
        matrix = star.matrix_from_coordinates(chart)
        if exact_topes.parent_signs(matrix) != expected_parent:
            raise AssertionError("frozen chart left parent 860")
        rows = exact_topes.derived_rows(matrix)
        topes = exact_topes.enumerate_topes(rows, dimension=4)
        exact_topes.verify_topes(rows, topes)
        observed = "".join("1" if signature in topes else "0" for signature in FAMILY)
        if observed != expected_pattern:
            raise AssertionError(f"frozen chart pattern moved: {observed}")
        chart_points = []
        chart_supports = []
        chart_weights = []
        for signature in FAMILY:
            if signature in topes:
                chart_points.append(topes[signature])
                chart_supports.append((-1,) * 5)
                chart_weights.append((0,) * 5)
            else:
                support, weights = positive_gordan_relation(signed_rows(rows, signature))
                chart_points.append((0,) * 4)
                chart_supports.append(support + (-1,) * (5 - len(support)))
                chart_weights.append(weights + (0,) * (5 - len(weights)))
        feasible_points.append(chart_points)
        gordan_supports.append(chart_supports)
        gordan_weights.append(chart_weights)

    payload = {
        "format": np.asarray(FORMAT),
        "parent_index": np.asarray(860, dtype=np.int64),
        "loop_vertex": np.asarray(LOOP, dtype=np.int64),
        "signature": np.asarray(FAMILY, dtype=np.uint64),
        "chart_index": np.asarray(CHART_INDEXES, dtype=np.int64),
        "pattern": string_array(PATTERNS),
        "coordinate_numerator": string_array(
            [[value.numerator for value in chart] for chart in CHARTS]
        ),
        "coordinate_denominator": string_array(
            [[value.denominator for value in chart] for chart in CHARTS]
        ),
        "feasible_point": string_array(feasible_points),
        "gordan_support": np.asarray(gordan_supports, dtype=np.int64),
        "gordan_weight": string_array(gordan_weights),
    }
    np.savez_compressed(OUTPUT, **payload)
    return payload


def main():
    build()
    print("WROTE", OUTPUT)
    print("CHARTS", len(CHARTS), "EXACT ALTERNATIVES", len(CHARTS) * len(FAMILY))


if __name__ == "__main__":
    main()
