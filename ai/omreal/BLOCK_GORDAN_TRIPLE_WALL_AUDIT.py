#!/usr/bin/env python3
"""Exact wall and escape audit for the hard row-2599 three-pivot cube.

This verifier complements ``BLOCK_GORDAN_HARD_TRIPLE_PIVOT.py``.  It proves
two deliberately separate statements.

Local theorem.  The distinguished Q-to-R product cube, including all of its
zero-block and zero-weight faces in the block-Gordan compactification, lies in
a noncompact component.  The cube contracts blockwise to its R corner and a
single exact pencil motion then reaches the parent boundary at [1467] = 0
while every active R circuit remains strict.

Global obstruction.  The six circuit vertices have 19 distinct residual
cofactor walls.  Three are shared Q/R edge-collapse walls, but 16 are
endpoint-specific.  A second exact realization of the same parent chirotope
has R4 strict while Q4 has disappeared across one of those endpoint-specific
walls.  Thus this particular cube cannot itself define a global matching.

Only exact integer and rational arithmetic is used.
"""

from collections import defaultdict
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import BLOCK_GORDAN_HARD_TRIPLE_PIVOT as pivot  # noqa: E402
import prototype_koszul_circuits as koszul  # noqa: E402


UPPER_CERTIFICATE = HERE / "data" / "seeat_parent2599_upper178.npz"
PENCIL_DIRECTION = (-48_680_481, 163_290_694, 329_496_695, 0)
EXIT_TIME = Fraction(17_036, 420_822_576_313)
EXIT_BRACKET = (1, 4, 6, 7)
PENCIL_NORMAL_SCALES = {
    "134": -8_365_328,
    "127": -11_992_469,
}
EXPECTED_SHARED_WALLS = {
    0: (("134", "267", "258", "468"), 50),
    4: (("256", "127", "357", "478"), 47),
    3: (("256", "356", "127", "347"), 41),
}
EXPECTED_CHART7_Q4_RAW = (
    -578_582_431_137_700_472,
    -70_253_942_367_169_540,
    336_425_478_039_445_424,
    -54_963_867_325_648_880,
    -46_201_975_207_436_930,
)
EXPECTED_CHART7_R4_RAW = (
    -578_582_431_137_700_472,
    -908_594_655_031_293_132,
    -349_727_606_339_858_544,
    -742_528_912_103_169_852,
    -685_978_694_109_578_506,
)


def bracket(matrix, labels):
    """The exact ordered 4-by-4 bracket on increasing one-based labels."""
    return koszul.determinant([
        [int(matrix[row, label - 1]) for label in labels]
        for row in range(4)
    ])


def sign(value):
    if value == 0:
        return 0
    return 1 if value > 0 else -1


def parent_chirotope(matrix):
    return tuple(
        sign(bracket(matrix, labels))
        for labels in combinations(range(1, 9), 4)
    )


def raw_cofactors(normals, signature, support):
    """Alternating maximal minors before a common sign normalization."""
    columns = pivot.signed_columns(normals, signature, support)
    values = []
    for omitted in range(5):
        selected = [
            columns[index]
            for index in range(5)
            if index != omitted
        ]
        determinant = koszul.determinant([
            [column[row] for column in selected]
            for row in range(4)
        ])
        values.append((-1 if omitted & 1 else 1) * determinant)
    return tuple(values)


def strict_circuit(raw):
    return all(value > 0 for value in raw) or all(value < 0 for value in raw)


def normalized_circuit(normals, signature, support):
    coefficients = pivot.circuit_coefficients(normals, signature, support)
    if coefficients is None:
        raise AssertionError("expected strict circuit")
    total = sum(coefficients)
    vector = [Fraction(0) for _ in koszul.TRIPLES]
    for index, coefficient in zip(support, coefficients, strict=True):
        vector[index] = Fraction(coefficient, total)
    return tuple(vector)


def kernel_residual(normals, signature, vector):
    return tuple(
        sum(
            vector[index]
            * (normals[index][row] if (signature >> index) & 1 else -normals[index][row])
            for index in range(len(koszul.TRIPLES))
        )
        for row in range(4)
    )


def cofactor_wall_audit(originals, distinguished):
    occurrences = defaultdict(list)
    for bit in pivot.BITS:
        for endpoint, support in (
            ("Q", originals[bit]),
            ("R", distinguished[bit]),
        ):
            for omitted, omitted_index in enumerate(support):
                four_support = tuple(
                    index for index in support if index != omitted_index
                )
                occurrences[four_support].append(
                    (bit, endpoint, pivot.name(omitted_index), omitted)
                )

    if sum(map(len, occurrences.values())) != 30 or len(occurrences) != 27:
        raise AssertionError("wrong cofactor occurrence/unique-wall count")

    by_kind = defaultdict(list)
    for support, witnesses in occurrences.items():
        orbit = koszul.wall_orbit(support)
        by_kind[koszul.orbit_kind(orbit)].append((support, orbit, witnesses))
    if {kind: len(values) for kind, values in by_kind.items()} != {
        "residual": 19,
        "unit": 8,
    }:
        raise AssertionError("wrong residual/unit cofactor partition")

    shared = []
    endpoint_specific = []
    for support, orbit, witnesses in by_kind["residual"]:
        endpoints = {(bit, endpoint) for bit, endpoint, _, _ in witnesses}
        if len(witnesses) == 2:
            bits = {bit for bit, _, _, _ in witnesses}
            tags = {endpoint for _, endpoint, _, _ in witnesses}
            if len(bits) != 1 or tags != {"Q", "R"}:
                raise AssertionError("unexpected repeated residual cofactor")
            bit = next(iter(bits))
            names = tuple(pivot.name(index) for index in support)
            if (names, orbit) != EXPECTED_SHARED_WALLS[bit]:
                raise AssertionError("wrong shared Q/R wall")
            shared.append((support, orbit, witnesses))
        elif len(witnesses) == 1 and len(endpoints) == 1:
            endpoint_specific.append((support, orbit, witnesses))
        else:
            raise AssertionError("unexpected residual-wall multiplicity")
    if len(shared) != 3 or len(endpoint_specific) != 16:
        raise AssertionError("wrong shared/endpoint-specific residual split")
    return by_kind, shared, endpoint_specific


def pencil_audit(matrix, normals, signatures, distinguished):
    vector = PENCIL_DIRECTION
    y1 = tuple(int(value) for value in matrix[:, 0])
    if koszul.matrix_rank([y1, vector]) != 2:
        raise AssertionError("pencil direction is only projective rescaling")

    moving_matrix = matrix.astype(object).copy()
    moving_matrix[:, 0] = np.asarray(vector, dtype=object)
    replacement_normals = koszul.parent_normals(moving_matrix)
    derivative_normals = [
        replacement if 1 in koszul.TRIPLES[index] else (0, 0, 0, 0)
        for index, replacement in enumerate(replacement_normals)
    ]

    for name, scale in PENCIL_NORMAL_SCALES.items():
        index = pivot.indices((name,))[0]
        normal = normals[index]
        derivative = derivative_normals[index]
        if sum(a * b for a, b in zip(normal, vector, strict=True)) != 0:
            raise AssertionError(f"direction is not in plane {name}")
        if derivative != tuple(scale * value for value in normal):
            raise AssertionError(f"wrong normal scale for {name}")
        if 1 + EXIT_TIME * scale <= 0:
            raise AssertionError(f"normal {name} reverses before the exit")

    # Find every finite parent-bracket root under y_1(t)=y_1+t v.
    roots = []
    for labels in combinations(range(1, 9), 4):
        constant = bracket(matrix, labels)
        derivative = bracket(moving_matrix, labels) if 1 in labels else 0
        if derivative:
            roots.append((Fraction(-constant, derivative), labels))
    positive = sorted(item for item in roots if item[0] > 0)
    negative = [item for item in roots if item[0] < 0]
    if negative:
        raise AssertionError("chosen direction unexpectedly has a negative root")
    if positive[0] != (EXIT_TIME, EXIT_BRACKET):
        raise AssertionError(f"wrong first parent wall {positive[0]}")
    if sum(root == EXIT_TIME for root, _ in positive) != 1:
        raise AssertionError("first parent wall is not unique")

    # Directly check sign preservation in the open interval and unique exit.
    midpoint = EXIT_TIME / 2
    for labels in combinations(range(1, 9), 4):
        constant = bracket(matrix, labels)
        derivative = bracket(moving_matrix, labels) if 1 in labels else 0
        if sign(constant + midpoint * derivative) != sign(constant):
            raise AssertionError("parent sign changed before the certified exit")
        endpoint = constant + EXIT_TIME * derivative
        if labels == EXIT_BRACKET:
            if endpoint != 0:
                raise AssertionError("certified exit bracket is nonzero")
        elif sign(endpoint) != sign(constant):
            raise AssertionError("another parent bracket reaches zero at the exit")

    # At the far corner, only normals 134 and 127 move, and only by positive
    # scale.  Hence inverse scaling transports each strict positive circuit.
    moving_names = {"134", "127"}
    for bit, support in distinguished.items():
        initial = normalized_circuit(normals, signatures[bit], support)
        if kernel_residual(normals, signatures[bit], initial) != (0, 0, 0, 0):
            raise AssertionError("bad initial circuit equation")
        for index in support:
            name = pivot.name(index)
            derivative = derivative_normals[index]
            if name not in moving_names and any(derivative):
                raise AssertionError("a supposedly fixed R normal moves")
        # Exact midpoint transport, representative of the symbolic formula
        # c_i(t)=c_i(0)/lambda_i(t), followed by normalization.
        transported = []
        for index, coefficient in enumerate(initial):
            name = pivot.name(index)
            factor = 1 + midpoint * PENCIL_NORMAL_SCALES.get(name, 0)
            transported.append(coefficient / factor)
        total = sum(transported)
        transported = tuple(value / total for value in transported)
        midpoint_normals = []
        for normal, derivative in zip(normals, derivative_normals, strict=True):
            midpoint_normals.append(tuple(
                Fraction(value) + midpoint * delta
                for value, delta in zip(normal, derivative, strict=True)
            ))
        if kernel_residual(midpoint_normals, signatures[bit], transported) != (0, 0, 0, 0):
            raise AssertionError("inverse scaling did not transport R circuit")
        if any(value < 0 for value in transported) or sum(transported) != 1:
            raise AssertionError("transported R circuit left its simplex")


def cube_and_zero_block_audit(normals, signatures, originals, distinguished):
    q_vectors = {
        bit: normalized_circuit(normals, signatures[bit], originals[bit])
        for bit in pivot.BITS
    }
    r_vectors = {
        bit: normalized_circuit(normals, signatures[bit], distinguished[bit])
        for bit in pivot.BITS
    }
    for bit in pivot.BITS:
        for vector in (q_vectors[bit], r_vectors[bit]):
            if sum(vector) != 1 or min(vector) < 0:
                raise AssertionError("endpoint is not in normalized witness fiber")
            if kernel_residual(normals, signatures[bit], vector) != (0, 0, 0, 0):
                raise AssertionError("endpoint fails Gordan equation")

    # Check the closed formula H_a(w_sigma)=(1-a)w_sigma+a t_sigma r_sigma
    # on an exact join point, including a zero block.  Linearity then proves
    # it on the entire closed cube/join, not merely this sample.
    masses = {0: Fraction(2, 5), 4: Fraction(3, 5), 3: Fraction(0)}
    edge_parameters = {0: Fraction(1, 3), 4: Fraction(3, 7), 3: Fraction(1, 2)}
    homotopy_parameter = Fraction(5, 11)
    for bit in pivot.BITS:
        mass = masses[bit]
        edge = edge_parameters[bit]
        witness = tuple(
            mass * ((1 - edge) * q + edge * r)
            for q, r in zip(q_vectors[bit], r_vectors[bit], strict=True)
        )
        collapsed = tuple(
            (1 - homotopy_parameter) * value
            + homotopy_parameter * mass * r
            for value, r in zip(witness, r_vectors[bit], strict=True)
        )
        if sum(collapsed) != mass or min(collapsed) < 0:
            raise AssertionError("block-mass preserving collapse failed")
        if kernel_residual(normals, signatures[bit], collapsed) != (0, 0, 0, 0):
            raise AssertionError("cube collapse left the Gordan kernel")
        if mass == 0 and any(collapsed):
            raise AssertionError("zero block was not fixed")

    # Every nonempty zero-block face reaches the same label-1 pencil: all
    # active R supports meet label 1 only in planes 134 and 127.
    for mask in range(1, 1 << len(pivot.BITS)):
        active = [
            bit for position, bit in enumerate(pivot.BITS)
            if (mask >> position) & 1
        ]
        union = set().union(*(set(distinguished[bit]) for bit in active))
        incident = {
            pivot.name(index)
            for index in union
            if 1 in koszul.TRIPLES[index]
        }
        if not incident or not incident <= {"134", "127"}:
            raise AssertionError("a zero-block face lacks the common pencil")


def global_obstruction_audit(base_matrix, signatures, originals, distinguished):
    upper = np.load(UPPER_CERTIFICATE, allow_pickle=False)
    if int(upper["parent_index"].item()) != 2599:
        raise AssertionError("wrong upper-certificate parent")
    chart = upper["chart_matrix"][7]
    base_signs = parent_chirotope(base_matrix)
    chart_signs = parent_chirotope(chart)
    if 0 in base_signs or chart_signs != base_signs:
        raise AssertionError("chart 7 is not in the same uniform parent cell")

    chart_normals = koszul.parent_normals(chart)
    bit = 4
    q_raw = raw_cofactors(chart_normals, signatures[bit], originals[bit])
    r_raw = raw_cofactors(chart_normals, signatures[bit], distinguished[bit])
    if q_raw != EXPECTED_CHART7_Q4_RAW or r_raw != EXPECTED_CHART7_R4_RAW:
        raise AssertionError("chart-7 cofactor certificate changed")
    if strict_circuit(q_raw) or not strict_circuit(r_raw):
        raise AssertionError("chart 7 does not kill Q4 while retaining R4")
    if [sign(value) for value in q_raw] != [-1, -1, 1, -1, -1]:
        raise AssertionError("wrong endpoint-specific Q4 wall")

    # The changed coefficient omits 127, hence is the residual four-support
    # 123/256/357/478 of orbit 50.  It occurs only at Q4 among the six cube
    # vertices, so the failure cannot be repaired by declaring the Q/R edge
    # to collapse at a shared four-circuit.
    q4 = originals[bit]
    omitted = next(index for index, item in enumerate(q4) if pivot.name(item) == "127")
    wall = tuple(item for index, item in enumerate(q4) if index != omitted)
    if tuple(pivot.name(index) for index in wall) != ("123", "256", "357", "478"):
        raise AssertionError("wrong chart-7 endpoint-specific wall support")
    if koszul.wall_orbit(wall) != 50 or koszul.orbit_kind(50) != "residual":
        raise AssertionError("wrong chart-7 endpoint-specific wall orbit")


def main():
    certificate = np.load(pivot.CERTIFICATE, allow_pickle=False)
    matrix = certificate["pattern_chart"][0]
    normals = koszul.parent_normals(matrix)
    signatures = {bit: int(certificate["signature"][bit]) for bit in pivot.BITS}
    originals = {
        bit: pivot.stored_support(certificate, bit)
        for bit in pivot.BITS
    }
    distinguished = {
        bit: pivot.indices(pivot.DISTINGUISHED_PIVOT[bit])
        for bit in pivot.BITS
    }

    by_kind, shared, endpoint_specific = cofactor_wall_audit(
        originals, distinguished
    )
    pencil_audit(matrix, normals, signatures, distinguished)
    cube_and_zero_block_audit(
        normals, signatures, originals, distinguished
    )
    global_obstruction_audit(matrix, signatures, originals, distinguished)

    print("PASS: 30 cofactor occurrences give 27 distinct walls")
    print(
        "PASS: walls split as 8 fixed-unit and 19 residual "
        f"({len(shared)} shared, {len(endpoint_specific)} endpoint-specific)"
    )
    print("PASS: the exact three-cube collapse respects zero weights and zero blocks")
    print(
        "PASS: one pencil preserves every far-corner face until the unique "
        "parent exit [1467]=0"
    )
    print(f"exit time={EXIT_TIME}")
    print("PASS: the hard triple component through row-2599 pattern 0 is noncompact")
    print(
        "PASS: exact chart 7 retains R4 but kills Q4 at endpoint-specific "
        "residual orbit 50"
    )
    print("NOTE: this local cancellation does not define a global cubical matching")


if __name__ == "__main__":
    main()
