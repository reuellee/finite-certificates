#!/usr/bin/env python3
"""Exact no-go for transporting extension loci through reducible deletion.

The parent is the alternating matroid A(4,8).  Its eighth element is the
lexicographic extension [7+,6-,5+,4-] of A(4,7), hence is reducible: every
realization of the deletion admits the prescribed insertion.

We construct a realizable proper extension signature sigma of this parent.
After deleting the reducible parent element, two exact extension columns p0
and p1 realize the same restricted signature tau.  The incidence (N,p0)
lifts back to sigma, while a five-row positive Gordan circuit proves that
(N,p1) cannot lift.  Thus reducibility is not hereditary under even one
proper extension, and the natural convex insertion-incidence map is not
surjective.
"""

from __future__ import annotations

from itertools import combinations


N_PARAMETERS = (-3, -2, -1, 0, 1, 2, 3)
E_PARAMETER = 4
P0 = (-12, -12, 6, 18)
P1 = (-142_669, -427_153, 430_203, -419_833)
PROPER_PARAMETERS = (-47, -39, -25, -23, -21, 14, 21, 27)
SIGMA_BITS = 0xF07FE1FFFC
TAU_BITS = 0xE7FBFFC

# Rows are ordered as 35 parent-insertion triple rows followed by 21
# sigma-insertion pair rows.
INCIDENCE_SUPPORT = (13, 18, 33, 38, 46)
INCIDENCE_WEIGHTS = (
    86_484_824,
    552_946_456,
    1_460_613_280,
    1_403,
    7_867_472,
)
INCIDENCE_ROWS = (
    (432, -432, -48, 48),
    (-120, -140, 0, 20),
    (0, 36, -30, 6),
    (20_664_384, -13_823_104, -6_856_896, 15_616),
    (0, 10_370, 7_320, -3_050),
)

PROPER_SUPPORT = (1, 17, 36, 44, 55)
PROPER_WEIGHTS = (
    9_817_415_335,
    244_690_537,
    3_688_327_422_780,
    202_820_352,
    1_665_426_048,
)
PROPER_ROWS = (
    (-129_512_448, -11_707_392, -334_848, -3_072),
    (2_461_088_448, 78_406_848, -3_786_432, -92_352),
    (193_200, 25_328, 1_104, 16),
    (-249_139_800, 17_057_508, 421_824, -26_364),
    (4_334_148, -676_494, 33_852, -546),
)


def moment(parameter):
    return (1, parameter, parameter * parameter, parameter * parameter * parameter)


def determinant(matrix):
    matrix = tuple(tuple(map(int, row)) for row in matrix)
    if len(matrix) == 1:
        return matrix[0][0]
    return sum(
        (-1 if column & 1 else 1)
        * matrix[0][column]
        * determinant(
            tuple(
                row[:column] + row[column + 1 :] for row in matrix[1:]
            )
        )
        for column in range(len(matrix))
    )


def column_determinant(columns):
    return determinant(
        tuple(
            tuple(columns[column][row] for column in range(len(columns)))
            for row in range(len(columns))
        )
    )


def coefficient_row(columns, variable_slot):
    """Coefficients of a four-column determinant in one variable column."""
    answer = []
    for coordinate in range(4):
        basis = tuple(1 if row == coordinate else 0 for row in range(4))
        substituted = tuple(
            basis if column == variable_slot else columns[column]
            for column in range(4)
        )
        answer.append(column_determinant(substituted))
    return tuple(answer)


def dot(left, right):
    return sum(int(x) * int(y) for x, y in zip(left, right))


def sign(value):
    if not value:
        raise AssertionError("uniform sign evaluation vanished")
    return 1 if value > 0 else -1


def positive_sign_bits(signature):
    return sum((value > 0) << index for index, value in enumerate(signature))


def chirotope(matrix):
    return tuple(
        sign(column_determinant(tuple(matrix[index] for index in basis)))
        for basis in combinations(range(len(matrix)), 4)
    )


def extension_rows(parent):
    triples = tuple(combinations(range(len(parent)), 3))
    return tuple(
        coefficient_row(tuple(parent[index] for index in triple) + (None,), 3)
        for triple in triples
    )


def extension_signature(parent, point):
    return tuple(sign(dot(row, point)) for row in extension_rows(parent))


def signed_extension_rows(parent, signature):
    rows = extension_rows(parent)
    if len(rows) != len(signature):
        raise AssertionError("signature has wrong length")
    return tuple(
        tuple(prescribed * value for value in row)
        for prescribed, row in zip(signature, rows)
    )


def joint_insertion_rows(deletion, point, joint_signs):
    pairs = tuple(combinations(range(len(deletion)), 2))
    if len(pairs) != len(joint_signs):
        raise AssertionError("joint signature has wrong length")
    answer = []
    for pair, prescribed in zip(pairs, joint_signs):
        columns = (
            deletion[pair[0]], deletion[pair[1]], None, point
        )
        row = coefficient_row(columns, 2)
        answer.append(tuple(prescribed * value for value in row))
    return tuple(answer)


def positive_dependence(rows, support, weights, expected_rows):
    selected = tuple(rows[index] for index in support)
    if selected != expected_rows:
        raise AssertionError("stored Gordan rows changed")
    if len(weights) != len(selected) or any(weight <= 0 for weight in weights):
        raise AssertionError("Gordan weights are not strictly positive")
    total = tuple(
        sum(weight * row[coordinate] for weight, row in zip(weights, selected))
        for coordinate in range(4)
    )
    if total != (0, 0, 0, 0):
        raise AssertionError("stored positive dependence is not zero")


def verify_lexicographic_reducibility(deletion, parent):
    # The alternating endpoint has all increasing brackets positive.
    if set(chirotope(deletion)) != {1} or set(chirotope(parent)) != {1}:
        raise AssertionError("moment configurations are not alternating")

    # In the lexicographic extension [7+,6-,5+,4-], the first listed element
    # outside a triple determines its extension sign.
    sequence = ((6, 1), (5, -1), (4, 1), (3, -1))
    endpoint = parent[-1]
    for triple in combinations(range(7), 3):
        desired = sign(
            column_determinant(
                tuple(deletion[index] for index in triple) + (endpoint,)
            )
        )
        for element, prescribed in sequence:
            if element not in triple:
                lexicographic = prescribed * sign(
                    column_determinant(
                        tuple(deletion[index] for index in triple)
                        + (deletion[element],)
                    )
                )
                break
        else:
            raise AssertionError("lexicographic sequence missed a triple")
        if desired != lexicographic or desired != 1:
            raise AssertionError("endpoint is not [7+,6-,5+,4-]")


def main():
    deletion = tuple(moment(parameter) for parameter in N_PARAMETERS)
    e0 = moment(E_PARAMETER)
    parent = deletion + (e0,)
    verify_lexicographic_reducibility(deletion, parent)

    # The full extension sigma is realized at (parent,p0).
    sigma = extension_signature(parent, P0)
    sigma_rows = signed_extension_rows(parent, sigma)
    if len(sigma) != 56 or min(dot(row, P0) for row in sigma_rows) <= 0:
        raise AssertionError("p0 does not strictly realize sigma")
    if positive_sign_bits(sigma) != SIGMA_BITS:
        raise AssertionError("documented sigma bitset changed")

    # A second alternating realization of the same parent excludes sigma.
    proper_parent = tuple(moment(parameter) for parameter in PROPER_PARAMETERS)
    if chirotope(proper_parent) != chirotope(parent):
        raise AssertionError("properness chart is not the same alternating parent")
    proper_rows = signed_extension_rows(proper_parent, sigma)
    positive_dependence(
        proper_rows, PROPER_SUPPORT, PROPER_WEIGHTS, PROPER_ROWS
    )

    # Restrict sigma by deleting e.  Both p0 and p1 realize the same tau.
    tau0 = extension_signature(deletion, P0)
    tau1 = extension_signature(deletion, P1)
    if tau0 != tau1 or len(tau0) != 35:
        raise AssertionError("p0 and p1 have different restricted signatures")
    if positive_sign_bits(tau0) != TAU_BITS:
        raise AssertionError("documented tau bitset changed")

    # Parent insertion constraints for e, followed by the 21 constraints
    # involving two deletion labels, e, and p.
    parent_e_signature = extension_signature(deletion, e0)
    parent_rows = signed_extension_rows(deletion, parent_e_signature)
    pairs = tuple(combinations(range(7), 2))
    joint_signs = tuple(
        sign(
            column_determinant(
                (deletion[left], deletion[right], e0, P0)
            )
        )
        for left, right in pairs
    )
    p0_rows = parent_rows + joint_insertion_rows(deletion, P0, joint_signs)
    if len(p0_rows) != 56 or min(dot(row, e0) for row in p0_rows) <= 0:
        raise AssertionError("e0 does not lift (deletion,p0) to sigma")

    p1_rows = parent_rows + joint_insertion_rows(deletion, P1, joint_signs)
    positive_dependence(
        p1_rows,
        INCIDENCE_SUPPORT,
        INCIDENCE_WEIGHTS,
        INCIDENCE_ROWS,
    )

    print("PASS: M=A(4,8) is the reducible lex extension [7+,6-,5+,4-]")
    print("PASS: p0 realizes a uniform extension sigma of M")
    print("PASS: an exact A(4,8) chart has a positive circuit excluding sigma")
    print("THEOREM: sigma is nonempty and proper")
    print("PASS: p0 and p1 realize one restricted signature tau over A(4,7)")
    print("PASS: e0 lifts p0; a five-row positive circuit forbids every lift of p1")
    print("THEOREM: reducibility is not hereditary under one proper extension")
    print("NO-GO: reducible-parent deletion does not surject on extension incidence")
    print("SCOPE: this blocks naive induction; it is not a ninth-diagonal counterexample")


if __name__ == "__main__":
    main()
