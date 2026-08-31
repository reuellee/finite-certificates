#!/usr/bin/env python3
"""Independent exact replay of the D8 mask-6 nonvacuity certificate."""

from __future__ import annotations

import copy
from fractions import Fraction
import hashlib
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OMREAL = ROOT / "ai" / "omreal"
DATA = OMREAL / "data"
sys.path.insert(0, str(OMREAL))

import DIAG9_GRAPH_exact_topes as exact_topes  # noqa: E402
import DIAG9_GRAPH_parent860_star as star  # noqa: E402


CERTIFICATE = HERE / "DIAG8_MASK6_NONVACUITY_CERTIFICATE.npz"
REPAIR = DATA / "DIAG9_GRAPH_parent860_star_repair.npz"
FORMAT = "diag8-mask6-nonvacuity-v2"
CERTIFICATE_SHA256 = "ac86ed2966cf4646dd2241caee4d938aefb9ec70b27a91df8795ad992993c7c5"
REPAIR_SHA256 = "f3ebf1f3a9b458663a12b042e68194aa24c4b55689cf85344e2d98f81aec3d11"
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
MASK6_CYCLE = (4, 11, 12, 14, 13, 23)
REQUIRED = {
    "format",
    "parent_index",
    "loop_vertex",
    "signature",
    "chart_index",
    "pattern",
    "coordinate_numerator",
    "coordinate_denominator",
    "feasible_point",
    "gordan_support",
    "gordan_weight",
}


class Reject(AssertionError):
    """Fail-closed certificate rejection."""


def require(condition, message):
    if not condition:
        raise Reject(message)


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def load(path=CERTIFICATE):
    with np.load(path, allow_pickle=False) as source:
        return {name: source[name] for name in source.files}


def validate_source(family, cycle):
    require(sha256(REPAIR) == REPAIR_SHA256, "parent-860 repair bytes moved")
    with np.load(REPAIR, allow_pickle=False) as source:
        support_by_signature = dict(
            zip(map(int, source["signature"]), map(int, source["signature_pattern"]))
        )
    cycle_mask = sum(1 << vertex for vertex in cycle)
    for signature in family:
        require(signature in support_by_signature, "family signature absent")
        require(
            support_by_signature[signature] & cycle_mask == cycle_mask,
            "family is not common on the complete loop",
        )


def validate(payload, check_certificate_digest=False):
    if check_certificate_digest:
        require(sha256(CERTIFICATE) == CERTIFICATE_SHA256, "certificate bytes moved")
    require(set(payload) == REQUIRED, "certificate field census")
    require(str(payload["format"].item()) == FORMAT, "format")
    require(int(payload["parent_index"].item()) == 860, "parent")
    cycle = tuple(map(int, payload["loop_vertex"]))
    family = tuple(map(int, payload["signature"]))
    patterns = tuple(map(str, payload["pattern"]))
    require(cycle == MASK6_CYCLE, "loop")
    require(family == FAMILY and len(set(family)) == 8, "family")
    require(tuple(map(int, payload["chart_index"])) == CHART_INDEXES, "charts")
    require(patterns == PATTERNS, "patterns")
    validate_source(family, cycle)

    numerators = payload["coordinate_numerator"]
    denominators = payload["coordinate_denominator"]
    points = payload["feasible_point"]
    supports = payload["gordan_support"]
    weights = payload["gordan_weight"]
    chart_count = len(PATTERNS)
    require(numerators.shape == denominators.shape == (chart_count, 9), "coordinates")
    require(points.shape == (chart_count, 8, 4), "feasible points")
    require(supports.shape == weights.shape == (chart_count, 8, 5), "Gordan arrays")

    base = star.normalized_parent()
    expected_parent = exact_topes.parent_signs(star.matrix_from_coordinates(base))
    witness_count = 0
    for chart_position, pattern in enumerate(patterns):
        coordinates = tuple(
            Fraction(int(numerator), int(denominator))
            for numerator, denominator in zip(
                numerators[chart_position], denominators[chart_position]
            )
        )
        matrix = star.matrix_from_coordinates(coordinates)
        require(exact_topes.parent_signs(matrix) == expected_parent, "chart left parent 860")
        rows = exact_topes.derived_rows(matrix)
        for signature_position, (signature, expected) in enumerate(zip(family, pattern)):
            signed = tuple(
                tuple((1 if signature >> bit & 1 else -1) * value for value in row)
                for bit, row in enumerate(rows)
            )
            point = tuple(map(int, points[chart_position, signature_position]))
            support = tuple(
                int(index)
                for index in supports[chart_position, signature_position]
                if int(index) >= 0
            )
            weight = tuple(
                int(value)
                for index, value in zip(
                    supports[chart_position, signature_position],
                    weights[chart_position, signature_position],
                )
                if int(index) >= 0
            )
            if expected == "1":
                require(any(point), "zero feasible ray")
                require(not support, "feasible entry stores a Gordan support")
                require(
                    all(sum(a * x for a, x in zip(row, point)) > 0 for row in signed),
                    "invalid strict feasible ray",
                )
            else:
                require(not any(point), "infeasible entry stores a ray")
                require(
                    2 <= len(support) <= 5 and len(set(support)) == len(support),
                    "invalid Gordan support",
                )
                require(len(weight) == len(support) and all(x > 0 for x in weight), "weights")
                require(
                    all(
                        sum(
                            weight[position] * signed[index][coordinate]
                            for position, index in enumerate(support)
                        )
                        == 0
                        for coordinate in range(4)
                    ),
                    "invalid Gordan relation",
                )
            witness_count += 1

    for signature_position in range(8):
        require(
            {pattern[signature_position] for pattern in patterns} == {"0", "1"},
            "region not proved nonempty and proper",
        )
    missing = [
        (left, right)
        for left in range(8)
        for right in range(8)
        if left != right
        and not any(pattern[left] == "1" and pattern[right] == "0" for pattern in patterns)
    ]
    require(not missing, "ordered noncontainment witness missing")
    return witness_count


def hostile_canaries(payload):
    mutations = []
    candidate = copy.deepcopy(payload)
    candidate["pattern"] = candidate["pattern"].copy()
    candidate["pattern"][0] = "10110011"
    mutations.append(("pattern", candidate))
    candidate = copy.deepcopy(payload)
    candidate["feasible_point"] = candidate["feasible_point"].copy()
    candidate["feasible_point"][0, 2] = 0
    mutations.append(("feasible_ray", candidate))
    candidate = copy.deepcopy(payload)
    candidate["gordan_weight"] = candidate["gordan_weight"].copy()
    candidate["gordan_weight"][0, 0, 0] = "0"
    mutations.append(("gordan_weight", candidate))
    candidate = copy.deepcopy(payload)
    candidate["signature"] = candidate["signature"].copy()
    candidate["signature"][0] ^= np.uint64(1)
    mutations.append(("signature", candidate))
    candidate = copy.deepcopy(payload)
    candidate["loop_vertex"] = candidate["loop_vertex"].copy()
    candidate["loop_vertex"][0] = 0
    mutations.append(("loop", candidate))
    candidate = copy.deepcopy(payload)
    candidate["coordinate_denominator"] = candidate["coordinate_denominator"].copy()
    candidate["coordinate_denominator"][0, 0] = "0"
    mutations.append(("chart", candidate))
    candidate = copy.deepcopy(payload)
    del candidate["parent_index"]
    mutations.append(("field", candidate))
    rejected = []
    for name, candidate in mutations:
        try:
            validate(candidate)
        except (Reject, ValueError, ZeroDivisionError):
            rejected.append(name)
        else:
            raise Reject(f"hostile canary accepted: {name}")
    return tuple(rejected)


def main():
    payload = load()
    witnesses = validate(payload, check_certificate_digest=True)
    rejected = hostile_canaries(payload)
    print("PASS exact parent-860 mask-6 nonvacuity certificate")
    print("PASS loop-common signatures:", len(FAMILY))
    print("PASS exact feasibility/Gordan witnesses:", witnesses)
    print("PASS directed noncontainment witnesses: 56/56")
    print("PASS hostile canaries:", len(rejected), "/", len(rejected))
    print("THEOREM eight loop-common regions are proper and pairwise incomparable")
    print("SCOPE parent 860 mask-6 loop; no diagonal-eight promotion")


if __name__ == "__main__":
    main()
