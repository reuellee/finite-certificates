#!/usr/bin/env python3
"""Exact checks for simultaneous residence shears and their obstruction.

The common-apex simultaneous-shear lemma is proved in ``ATLAS_HELLY.md``.
This verifier checks the finite claims used to delimit that lemma:

* three column shears toward one common apex preserve a stored circuit
  support, and every parent bracket is affine jointly in the three shear
  parameters;
* shears toward two different apices need not have a convex joint parent-cell
  domain (an exact row-2599 midpoint certificate is checked); and
* nine distinct realizable extension signatures have simultaneous positive
  circuit pieces at one exact parent chart.  From the second piece onward,
  every prefix has a pencil-rigid support union, and the incident support-plane
  normals have rank three at every label.

The last assertion is deliberately only a support-plane obstruction at the
stored chart.  It does not assert that a circuit-piece intersection has a
compact component, that its compact-support cohomology is nonzero, or that
the nine feasibility regions are pairwise incomparable.

Only exact integer arithmetic is used.
"""

from itertools import combinations
from pathlib import Path
import sys

import numpy as np

import prototype_koszul_circuits as koszul


HERE = Path(__file__).resolve().parent
SHATTER = HERE / "data" / "seeat_parent2599_shatter8.npz"
WIDTH = HERE / "data" / "seeat_parent2599_width7.npz"
TRIPLES = koszul.TRIPLES


def support(certificate, signature_index):
    return frozenset(
        index
        for index, raw in enumerate(
            certificate["gordan_weight"][0, signature_index]
        )
        if int(raw)
    )


def weights(certificate, signature_index):
    return tuple(
        int(raw) for raw in certificate["gordan_weight"][0, signature_index]
    )


def parent_brackets(matrix):
    result = []
    for basis in combinations(range(8), 4):
        columns = matrix[:, np.asarray(basis)]
        result.append(koszul.determinant(columns.tolist()))
    if not all(result):
        raise AssertionError("nonuniform parent chart")
    return tuple(result)


def extension_signature(matrix, point):
    signature = 0
    for index, normal in enumerate(koszul.parent_normals(matrix)):
        value = sum(int(coefficient) * int(x) for coefficient, x in zip(normal, point))
        if not value:
            raise AssertionError("extension point lies on a derived hyperplane")
        if value > 0:
            signature |= 1 << index
    return signature


def transformed(matrix, shears):
    """Apply ``source -> source + parameter * target`` column shears."""
    result = np.asarray(matrix, dtype=object).copy()
    original = np.asarray(matrix, dtype=object)
    for source, target, parameter in shears:
        result[:, source] = result[:, source] + parameter * original[:, target]
    return result


def positive_dependence(normals, signature, coefficient_vector):
    active = [index for index, value in enumerate(coefficient_vector) if value]
    if not active or any(coefficient_vector[index] <= 0 for index in active):
        raise AssertionError("circuit weights are not strictly positive on support")
    for coordinate in range(4):
        value = sum(
            coefficient_vector[index]
            * (1 if (signature >> index) & 1 else -1)
            * normals[index][coordinate]
            for index in active
        )
        if value:
            raise AssertionError("claimed signed positive dependence is nonzero")


def pencil_rigid(union):
    for label in range(1, 9):
        incident = [set(TRIPLES[index]) for index in union if label in TRIPLES[index]]
        if len(incident) < 3:
            return False
        if set.intersection(*(edge - {label} for edge in incident)):
            return False
    return True


def common_apex_sources(union, apex):
    return tuple(
        label
        for label in range(1, 9)
        if label != apex
        and all(
            apex in TRIPLES[index]
            for index in union
            if label in TRIPLES[index]
        )
    )


def check_common_apex_affinity(certificate, matrix):
    # Q_7 = 123/124/235/147/368.  Labels 5,6,8 are all dominated by apex 3.
    union = support(certificate, 7)
    apex = 3
    moving = (5, 6, 8)
    if not set(moving) <= set(common_apex_sources(union, apex)):
        raise AssertionError("stored support lacks its claimed common apex")

    base_normals = koszul.parent_normals(matrix)
    for parameters in ((2, -3, 5), (-4, 1, 2), (7, -2, -1)):
        moved = transformed(
            matrix,
            tuple((label - 1, apex - 1, parameter) for label, parameter in zip(moving, parameters)),
        )
        moved_normals = koszul.parent_normals(moved)
        if any(moved_normals[index] != base_normals[index] for index in union):
            raise AssertionError("common-apex shear changed a support normal")

    bases = tuple(combinations(range(8), 4))
    base = parent_brackets(matrix)
    deltas = []
    for label in moving:
        once = transformed(matrix, ((label - 1, apex - 1, 1),))
        deltas.append(
            tuple(value - initial for value, initial in zip(parent_brackets(once), base))
        )
    for parameters in ((2, -3, 5), (-4, 1, 2), (7, -2, -1)):
        moved = transformed(
            matrix,
            tuple((label - 1, apex - 1, parameter) for label, parameter in zip(moving, parameters)),
        )
        actual = parent_brackets(moved)
        expected = tuple(
            initial
            + sum(parameter * deltas[column][row] for column, parameter in enumerate(parameters))
            for row, initial in enumerate(base)
        )
        if actual != expected:
            bad = next(basis for basis, left, right in zip(bases, actual, expected) if left != right)
            raise AssertionError(f"common-apex parent bracket is not affine at {bad}")
    print("PASS common-apex 3-shear preserves Q7 and all 70 brackets are jointly affine")


def check_distinct_apex_nonconvexity(matrix):
    # y_3 -> y_3 + t y_8 and y_6 -> y_6 + s y_2.
    # Both (t,s)=(0,0) and (-1,4) retain the parent chirotope, while their
    # midpoint (-1/2,2) reverses bracket [3456].
    base = parent_brackets(matrix)
    endpoint = parent_brackets(transformed(matrix, ((2, 7, -1), (5, 1, 4))))
    if any(left * right <= 0 for left, right in zip(base, endpoint)):
        raise AssertionError("claimed distinct-apex endpoint leaves the parent cell")

    midpoint_numerators = []
    coefficients = []
    for basis, initial in zip(combinations(range(8), 4), base):
        def value(t, s):
            moved = transformed(matrix, ((2, 7, t), (5, 1, s)))
            return koszul.determinant(moved[:, np.asarray(basis)].tolist())

        b = value(1, 0) - initial
        c = value(0, 1) - initial
        d = value(1, 1) - initial - b - c
        # Twice the value at (-1/2,2).
        midpoint_numerator = 2 * initial - b + 4 * c - 2 * d
        midpoint_numerators.append(midpoint_numerator)
        coefficients.append((initial, b, c, d))

    bad = [
        (basis, coefficient, numerator)
        for basis, coefficient, numerator, initial in zip(
            combinations(range(1, 9), 4), coefficients, midpoint_numerators, base
        )
        if numerator * initial <= 0
    ]
    expected = [
        ((3, 4, 5, 6), (355_617, -594_661, -480_549, -253_190), -109_921)
    ]
    if bad != expected:
        raise AssertionError(f"wrong distinct-apex midpoint obstruction: {bad}")
    print("PASS distinct-apex shear slice is nonconvex: [3456] flips at the midpoint")


def check_nine_piece_obstruction(certificate, width, matrix):
    signatures = tuple(int(value) for value in certificate["signature"])
    normals = koszul.parent_normals(matrix)
    base_parent = tuple(1 if value > 0 else -1 for value in parent_brackets(matrix))

    # Order matters: the first two supports are Q0,Q4, whose union is already
    # pencil-rigid and plane-rigid.  Later supports can only add constraints.
    entries = [
        ("shatter-0", signatures[0], 0, certificate["pattern_chart"][1], certificate["feasible_point"][1, 0]),
        ("shatter-4", signatures[4], 4, certificate["pattern_chart"][16], certificate["feasible_point"][16, 4]),
    ]
    for width_index, reference in ((79, 0), (84, 0), (159, 0), (162, 0), (0, 4)):
        entries.append(
            (
                f"width-{width_index}",
                int(width["vertex_signature"][width_index]),
                reference,
                width["realization_matrix"][width_index],
                width["realization_point"][width_index],
            )
        )
    for signature_index in (3, 5):
        pattern = 1 << signature_index
        entries.append(
            (
                f"shatter-{signature_index}",
                signatures[signature_index],
                signature_index,
                certificate["pattern_chart"][pattern],
                certificate["feasible_point"][pattern, signature_index],
            )
        )

    if len(entries) != 9 or len({signature for _, signature, *_ in entries}) != 9:
        raise AssertionError("need nine distinct extension signatures")

    union = set()
    for position, (name, signature, reference, feasible_matrix, point) in enumerate(entries, 1):
        feasible_parent = tuple(
            1 if value > 0 else -1 for value in parent_brackets(feasible_matrix)
        )
        if feasible_parent != base_parent:
            raise AssertionError(f"{name}: feasible matrix has the wrong parent")
        if extension_signature(feasible_matrix, point) != signature:
            raise AssertionError(f"{name}: exact point realizes the wrong signature")

        coefficient_vector = weights(certificate, reference)
        positive_dependence(normals, signature, coefficient_vector)
        union.update(index for index, value in enumerate(coefficient_vector) if value)

        if position >= 2:
            if not pencil_rigid(union):
                raise AssertionError(f"prefix {position} is not pencil-rigid")
            if any(common_apex_sources(union, apex) for apex in range(1, 9)):
                raise AssertionError(f"prefix {position} has a common-apex shear")
            for label in range(1, 9):
                incident_normals = [
                    normals[index] for index in union if label in TRIPLES[index]
                ]
                if koszul.matrix_rank(incident_normals) != 3:
                    raise AssertionError(
                        f"prefix {position}, label {label}: support planes are not rigid"
                    )

    first_union = support(certificate, 0) | support(certificate, 4)
    degrees = tuple(
        sum(label in TRIPLES[index] for index in first_union)
        for label in range(1, 9)
    )
    if degrees != (3, 5, 3, 3, 3, 3, 4, 3):
        raise AssertionError(f"wrong Q0/Q4 union degrees {degrees}")

    print("PASS nine distinct realizable signatures are proper via exact good and bad charts")
    print("PASS every 2..9 prefix has a nonempty pencil-rigid circuit-piece intersection")
    print("PASS at the bad chart every such prefix is support-plane rigid at all eight labels")
    print("CAVEAT no compact component, nonzero H_c group, or nine-way incomparability is claimed")


def main():
    certificate = np.load(SHATTER, allow_pickle=False)
    width = np.load(WIDTH, allow_pickle=False)
    if int(certificate["parent_index"].item()) != 2599:
        raise AssertionError("wrong shatter parent")
    if int(width["parent_index"].item()) != 2599:
        raise AssertionError("wrong width parent")
    matrix = certificate["pattern_chart"][0]

    check_common_apex_affinity(certificate, matrix)
    check_distinct_apex_nonconvexity(matrix)
    check_nine_piece_obstruction(certificate, width, matrix)
    print("THEOREM CHECK: common-apex shears are convex, while distinct-apex additivity fails")


if __name__ == "__main__":
    main()
