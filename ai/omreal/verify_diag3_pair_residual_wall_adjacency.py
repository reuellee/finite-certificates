#!/usr/bin/env python3
"""First exact residual-wall adjacency collar for the diagonal-three pair end.

This checker constructs a literal two-parameter collar around the canonical
type-49 wall.  In normalized coordinates the family is

    a -> a + u,       d -> d + t,
    -1/32 <= t <= 1/32,       0 <= u <= 1/128.

Tensor-product Bernstein coefficients prove that all 70 parent brackets and
all 26,739 nonselected primitive residual factors are strict on the closed
rectangle.  Factor 2267 restricts exactly to ``t``.  Thus the vertical edge
``t=0`` is the only residual wall, with no hidden simultaneous crossing.

The selected pair is bad on both sides.  The receiver is feasible on the
left and becomes bad on the wall/right.  Exact alternating cofactors replay
the five-normal witnesses and their four-normal zero-weight specializations.
Finally, the checker writes the signed absolute and pair-relative cellular
matrices of the two-square collar, verifies the integral/cochain ``MN=0``
identity, and checks the same ranks over F2.

This is one genuine local adjacency block.  It is not a chamber atlas and it
does not claim coverage of the row-2599 receiver assignments.  Pass
``--full-selection`` to replay the more expensive complete-tope calculation
which selects the pinned active pair and common root from the whole wall.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, permutations
from math import comb, gcd, lcm
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG9_GRAPH_exact_topes as topes  # noqa: E402
import four_chart_gate as gate  # noqa: E402
import prototype_koszul_circuits as koszul  # noqa: E402
import verify_diag2_canonical_robust_edges as robust  # noqa: E402
import verify_diag2_escape_set_atlas178 as escape_atlas  # noqa: E402
import verify_diag2_escape_set_topes as escape  # noqa: E402
import verify_diag3_pair_four_ray_refinement as refinement  # noqa: E402
import verify_diag3_pair_global_atlas_schema as atlas_schema  # noqa: E402
import verify_diag3_pair_local_root_switch as local_switch  # noqa: E402
import verify_diag3_pair_tangential_frontier as frontier  # noqa: E402
from DIAG2_PIVOT_ALL_COMPACT_SECOND_WALL_VERIFY import (  # noqa: E402
    standard_columns,
)


FORMAT = "diag3-pair-residual-wall-adjacency-v1"
KIND = 49
FACTOR = 2_267
OCCURRENCE_INDEX = 633
P = (0, 7, 14, 28)
PAIR = (31_021_161_137_927_844, 31_302_644_972_992_037)
RECEIVER = 31_021_169_996_281_381
ROOT = 73
ROOT_DIRECTION = (6, 2, 1)
EPSILON = Fraction(1, 32)
COLLAR_HEIGHT = Fraction(1, 128)
RAY_TERMINAL = (ROOT, 203, 8, (23,))
RAY_TERMINAL_LABEL = "1368"
RELATION_SIGNS = (-1, 1, 1, -1)
WALL_WEIGHTS = {
    Fraction(0): (112, 8, 8, 1),
    COLLAR_HEIGHT: (1_792, 128, 1, 16),
}
RECEIVER_LEFT_VECTOR = (
    41_230_745_460_380_018,
    618_622_239_402_628_941,
    618_461_184_826_892_161,
    7_313_520,
)

# A positive five-circuit at each nonrelative side.  The entries are
# (signature, side, auxiliary normal, primitive positive cofactor vector).
ENDPOINT_CIRCUITS = (
    (PAIR[0], "left", 1, (53_775, 1, 3_840, 3_841, 15)),
    (PAIR[0], "right", 33, (24_651_040, 1_762_656, 1_758_465, 6_880, 1)),
    (PAIR[1], "left", 48, (125_475, 8_953, 8_900, 35, 1)),
    (PAIR[1], "right", 1, (53_745, 1, 3_840, 3_839, 15)),
    (RECEIVER, "right", 1, (53_745, 1, 3_840, 3_839, 15)),
)

EXPECTED_ACTIVE_SIGNATURES = 814
EXPECTED_ACTIVE_MINIMUM = (20, (PAIR[1], PAIR[0], 58, 62))
EXPECTED_COMMON_ROOTS = (
    14, 15, 16, 17, 73, 76, 77, 80, 82, 88,
    93, 98, 101, 103, 104, 105, 106, 108, 109, 110,
)
EXPECTED_WALL_COMPATIBLE_COMMON_ROOTS = (
    73, 76, 77, 88, 93, 98, 101, 103, 104, 105, 106, 108, 109, 110,
)
EXPECTED_EXCHANGED_LEFT = (RECEIVER, 41_036_424_041_646_554)
EXPECTED_ORBIT = {
    "source_records": 40_320,
    "receiver_signatures": 40_320,
    "wall_occurrences": 10_080,
    "primitive_factors": 10_080,
    "two_sided_factor_identity_overlap": 3_720,
    "row2599_parent_hits": 0,
    "canonical_receiver_assignments_covered": 0,
}

# Pinned after the exact core and complete-selection replays.
EXPECTED_SEMANTIC_DIGEST = (
    "b46be52d472acba6aecc168d26de8faef37e2e68bb4ca1457ce0c9a21307a6c2"
)
EXPECTED_FULL_SEMANTIC_DIGEST = (
    "13f27e194bed826cb184cab678df017066f7193b0442be251e9d1c68e454b6a6"
)


def sign(value):
    return (value > 0) - (value < 0)


def polynomial_multiply(left, right):
    answer = {}
    for (left_t, left_u), left_value in left.items():
        for (right_t, right_u), right_value in right.items():
            monomial = (left_t + right_t, left_u + right_u)
            answer[monomial] = answer.get(monomial, 0) + left_value * right_value
    return {monomial: value for monomial, value in answer.items() if value}


def affine_power(constant, variable, exponent):
    answer = {(0, 0): Fraction(1)}
    monomial = (1, 0) if variable == "t" else (0, 1)
    factor = {(0, 0): Fraction(constant), monomial: Fraction(1)}
    for _ in range(exponent):
        answer = polynomial_multiply(answer, factor)
    return answer


def restrict_normalized_polynomial(polynomial, center):
    """Substitute a=a0+u and d=d0+t into a nine-variable polynomial."""

    answer = {}
    for monomial, coefficient in polynomial.items():
        term = {(0, 0): Fraction(coefficient)}
        for variable, exponent in enumerate(monomial):
            if not exponent:
                continue
            if variable == 0:
                term = polynomial_multiply(
                    term, affine_power(center[variable], "u", exponent)
                )
            elif variable == 3:
                term = polynomial_multiply(
                    term, affine_power(center[variable], "t", exponent)
                )
            else:
                scale = center[variable] ** exponent
                term = {key: value * scale for key, value in term.items()}
        for key, value in term.items():
            answer[key] = answer.get(key, 0) + value
    return {monomial: value for monomial, value in answer.items() if value}


def unit_square_polynomial(polynomial, epsilon, height):
    """Pull back t=-epsilon+2*epsilon*x, u=height*y to [0,1]^2."""

    answer = {}
    for (t_degree, u_degree), coefficient in polynomial.items():
        for x_degree in range(t_degree + 1):
            value = (
                coefficient
                * comb(t_degree, x_degree)
                * (-epsilon) ** (t_degree - x_degree)
                * (2 * epsilon) ** x_degree
                * height ** u_degree
            )
            key = (x_degree, u_degree)
            answer[key] = answer.get(key, 0) + value
    return {monomial: value for monomial, value in answer.items() if value}


def bidegree(polynomial):
    if not polynomial:
        return (-1, -1)
    return (
        max(monomial[0] for monomial in polynomial),
        max(monomial[1] for monomial in polynomial),
    )


def bernstein_coefficients(polynomial):
    """Power-to-Bernstein conversion on the unit square over QQ."""

    t_degree, u_degree = bidegree(polynomial)
    if t_degree < 0:
        return ()
    answer = []
    for t_index in range(t_degree + 1):
        for u_index in range(u_degree + 1):
            value = Fraction(0)
            for (left, right), coefficient in polynomial.items():
                if left <= t_index and right <= u_index:
                    value += (
                        coefficient
                        * Fraction(comb(t_index, left), comb(t_degree, left))
                        * Fraction(comb(u_index, right), comb(u_degree, right))
                    )
            answer.append(value)
    return tuple(answer)


def strict_bernstein_sign(polynomial, epsilon=EPSILON, height=COLLAR_HEIGHT):
    coefficients = bernstein_coefficients(
        unit_square_polynomial(polynomial, epsilon, height)
    )
    if coefficients and all(value > 0 for value in coefficients):
        return 1
    if coefficients and all(value < 0 for value in coefficients):
        return -1
    return 0


def family_integer_matrix(witness, t, u):
    values = list(witness.center)
    values[witness.pivot] += t
    columns = [
        [Fraction(value) for value in column]
        for column in standard_columns(
            dict(zip(robust.VARIABLES, values, strict=True))
        )
    ]
    source, target, direction_sign = ROOT_DIRECTION
    source -= 1
    target -= 1
    for row in range(4):
        columns[source][row] += direction_sign * u * columns[target][row]

    integral_columns = []
    for column in columns:
        denominator = 1
        for value in column:
            denominator = lcm(denominator, value.denominator)
        integral_columns.append(tuple(int(value * denominator) for value in column))
    return tuple(
        tuple(integral_columns[column][row] for column in range(8))
        for row in range(4)
    )


def primitive_vector(vector):
    divisor = 0
    for value in vector:
        divisor = gcd(divisor, abs(int(value)))
    if not divisor:
        raise AssertionError("zero cofactor vector")
    answer = [int(value) // divisor for value in vector]
    if next(value for value in answer if value) < 0:
        answer = [-value for value in answer]
    return tuple(answer)


def signed_normal_columns(matrix, signature, support):
    normals = topes.derived_rows(matrix, normalize=False)
    return tuple(
        tuple(
            (1 if signature & (1 << index) else -1) * coordinate
            for coordinate in normals[index]
        )
        for index in support
    )


def alternating_cofactors(columns):
    size = len(columns)
    if size == 5:
        selected_rows = tuple(range(4))
    elif size == 4:
        selected_rows = next(
            rows
            for rows in combinations(range(4), 3)
            if koszul.matrix_rank(
                [[columns[column][row] for column in range(4)] for row in rows]
            )
            == 3
        )
    else:
        raise AssertionError("only four- and five-normal circuits are expected")
    values = []
    for omitted in range(size):
        minor = [
            [columns[column][row] for column in range(size) if column != omitted]
            for row in selected_rows
        ]
        values.append((-1 if omitted & 1 else 1) * koszul.determinant(minor))
    return primitive_vector(values)


def circuit_vector(matrix, signature, support):
    support = tuple(sorted(support))
    return alternating_cofactors(signed_normal_columns(matrix, signature, support))


def verify_zero_weight_specialization(matrix, signature, auxiliary, wall_weights):
    support = tuple(sorted(P + (auxiliary,)))
    vector = circuit_vector(matrix, signature, support)
    auxiliary_position = support.index(auxiliary)
    if vector[auxiliary_position] != 0:
        raise AssertionError("wall auxiliary did not acquire zero weight")
    projected = tuple(vector[support.index(index)] for index in P)
    if projected != wall_weights:
        raise AssertionError(
            f"wrong four-circuit specialization {projected} != {wall_weights}"
        )
    return support, vector


def realized_signature(matrix, vector):
    signature = 0
    for index, row in enumerate(topes.derived_rows(matrix)):
        value = topes.dot(row, vector)
        if not value:
            raise AssertionError("purported receiver witness lies on a derived wall")
        if value > 0:
            signature |= 1 << index
    return signature


def matrix_multiply(left, right):
    if not left or not right:
        return []
    return [
        [
            sum(left[row][inner] * right[inner][column] for inner in range(len(right)))
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def transpose(matrix):
    return [list(row) for row in zip(*matrix, strict=True)]


def rational_rank(matrix):
    work = [[Fraction(value) for value in row] for row in matrix]
    if not work:
        return 0
    pivot_row = 0
    for column in range(len(work[0])):
        pivot = next(
            (row for row in range(pivot_row, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        value = work[pivot_row][column]
        work[pivot_row] = [entry / value for entry in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row or not work[row][column]:
                continue
            value = work[row][column]
            work[row] = [
                left - value * right
                for left, right in zip(work[row], work[pivot_row], strict=True)
            ]
        pivot_row += 1
    return pivot_row


def mod2_rank(matrix):
    rows = []
    for row in matrix:
        value = sum((int(entry) & 1) << column for column, entry in enumerate(row))
        rows.append(value)
    pivots = {}
    for value in rows:
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def incidence_audit():
    # Vertices BL,BW,BR,TL,TW,TR.  Edges bL,bR,tL,tR,vL,vW,vR.
    absolute_d1 = [
        [-1, 0, 0, 0, -1, 0, 0],
        [1, -1, 0, 0, 0, -1, 0],
        [0, 1, 0, 0, 0, 0, -1],
        [0, 0, -1, 0, 1, 0, 0],
        [0, 0, 1, -1, 0, 1, 0],
        [0, 0, 0, 1, 0, 0, 1],
    ]
    # qL = bL-tL-vL+vW; qR = bR-tR-vW+vR.
    absolute_d2 = [
        [1, 0],
        [0, 1],
        [-1, 0],
        [0, -1],
        [-1, 0],
        [1, -1],
        [0, 1],
    ]
    if matrix_multiply(absolute_d1, absolute_d2) != [[0, 0] for _ in range(6)]:
        raise AssertionError("absolute collar boundary does not square to zero")
    absolute_ranks = (
        rational_rank(absolute_d1), rational_rank(absolute_d2),
        mod2_rank(absolute_d1), mod2_rank(absolute_d2),
    )
    if absolute_ranks != (5, 2, 5, 2):
        raise AssertionError(f"absolute collar ranks changed: {absolute_ranks}")

    # Quotient by the triple-relative right square, including its wall edge.
    # Remaining bases are C0=(BL,TL), C1=(bL,tL,vL), C2=(qL).
    relative_d1 = [[-1, 0, -1], [0, -1, 1]]
    relative_d2 = [[1], [-1], [-1]]
    if matrix_multiply(relative_d1, relative_d2) != [[0], [0]]:
        raise AssertionError("relative collar boundary does not square to zero")

    # Schema convention: C0 --N--> C1 --M--> C2 is the transpose cochain.
    N = transpose(relative_d1)
    M = transpose(relative_d2)
    MN = matrix_multiply(M, N)
    if MN != [[0, 0]]:
        raise AssertionError(f"signed integral MN is nonzero: {MN}")
    ranks = (
        rational_rank(N), rational_rank(M), mod2_rank(N), mod2_rank(M)
    )
    if ranks != (2, 1, 2, 1) or ranks[2] + ranks[3] != len(N):
        raise AssertionError(f"relative collar ranks changed: {ranks}")
    # Columns bL,tL give -I_2 in d1 and qL has a unit coefficient in d2.
    # These are explicit unit Smith pivots, so the exactness is integral.
    return absolute_d1, absolute_d2, relative_d1, relative_d2, N, M, ranks


def orientation_sign(sequence):
    inversions = sum(
        sequence[left] > sequence[right]
        for left in range(len(sequence))
        for right in range(left + 1, len(sequence))
    )
    return -1 if inversions & 1 else 1


def transform_bits(signature, bases, basis_index, permutation):
    answer = 0
    for old_index, basis in enumerate(bases):
        sequence = tuple(permutation[value] for value in basis)
        new_index = basis_index[tuple(sorted(sequence))]
        old_sign = 1 if signature & (1 << old_index) else -1
        if orientation_sign(sequence) * old_sign > 0:
            answer |= 1 << new_index
    return answer


def transform_parent(parent, permutation):
    basis_index = {basis: index for index, basis in enumerate(topes.BASES)}
    signs = sum((value == "+") << index for index, value in enumerate(parent))
    transformed = transform_bits(signs, topes.BASES, basis_index, permutation)
    return "".join(
        "+" if transformed & (1 << index) else "-"
        for index in range(len(topes.BASES))
    )


def orbit_accounting(witness, occurrences, occurrence_factor):
    triple_index = {triple: index for index, triple in enumerate(topes.TRIPLES)}
    receiver_orbit = set()
    support_orbit = set()
    row2599_parent = [
        line.strip() for line in gate.CATALOG_48.open(encoding="utf-8")
        if line.strip()
    ][gate.PARENT_INDEX]
    row2599_hits = 0
    for permutation in permutations(range(8)):
        receiver_orbit.add(
            transform_bits(RECEIVER, topes.TRIPLES, triple_index, permutation)
        )
        mapping = labeled.triple_map(permutation)
        support_orbit.add(labeled.transform(P, mapping))
        transformed_parent = transform_parent(witness.parent, permutation)
        # Chirotopes are recorded with basis 1234 positive.  Normalize the
        # harmless global sign before comparing to the row-2599 catalog row.
        if transformed_parent[0] == "-":
            transformed_parent = "".join(
                "+" if value == "-" else "-" for value in transformed_parent
            )
        if transformed_parent == row2599_parent:
            row2599_hits += 1

    # The receiver is part of the source record.  Its free S8 orbit proves
    # that the complete labeled collar source records are all distinct.
    source_records = len(receiver_orbit)
    factor_orbit = {occurrence_factor[support] for support in support_orbit}
    with np.load(atlas_schema.FACTOR_STATES, allow_pickle=False) as source:
        two_sided = set(map(int, source["varied_factor"]))
    answer = {
        "source_records": source_records,
        "receiver_signatures": len(receiver_orbit),
        "wall_occurrences": len(support_orbit),
        "primitive_factors": len(factor_orbit),
        "two_sided_factor_identity_overlap": len(factor_orbit & two_sided),
        "row2599_parent_hits": row2599_hits,
        # A factor identity overlap is not a row-2599 geometric adjacency.
        "canonical_receiver_assignments_covered": 0 if not row2599_hits else -1,
    }
    if answer != EXPECTED_ORBIT:
        raise AssertionError(f"S8/source accounting changed: {answer}")
    return answer


def full_selection_audit(witness, relation_signs):
    left_topes = robust.enumerate_tope_table(
        family_integer_matrix(witness, -EPSILON, 0), witness.parent, "collar-left"
    )
    right_topes = robust.enumerate_tope_table(
        family_integer_matrix(witness, EPSILON, 0), witness.parent, "collar-right"
    )
    _parent, signatures = gate.enumerate_extensions(witness.parent)
    left_bad, right_bad = robust.valid_bad_partition(
        signatures, set(left_topes), set(right_topes), "type-49-collar"
    )
    common_bad = sorted(left_bad & right_bad)
    left_prepared = escape.prepare_directions(left_topes)
    right_prepared = escape.prepare_directions(right_topes)
    active = []
    for signature in common_bad:
        if refinement.circuit_positive(P, relation_signs, signature):
            active.append(
                (
                    signature,
                    escape.escape_mask(signature, left_prepared)
                    & escape.escape_mask(signature, right_prepared),
                )
            )
    if len(active) != EXPECTED_ACTIVE_SIGNATURES:
        raise AssertionError(f"wall-active signature count changed: {len(active)}")
    minimum = escape_atlas.minimum_pair_overlap(active)
    if minimum != EXPECTED_ACTIVE_MINIMUM:
        raise AssertionError(f"wall-active minimum pair changed: {minimum}")
    masks = dict(active)
    common_roots = tuple(
        index for index in range(len(escape.DIRECTIONS))
        if (masks[PAIR[0]] & masks[PAIR[1]]) & (1 << index)
    )
    if common_roots != EXPECTED_COMMON_ROOTS or ROOT not in common_roots:
        raise AssertionError(f"pinned common-root set changed: {common_roots}")
    exchanged_left = tuple(sorted(set(left_topes) - set(right_topes)))
    if exchanged_left != EXPECTED_EXCHANGED_LEFT or RECEIVER != min(exchanged_left):
        raise AssertionError(f"left-only receiver exchange changed: {exchanged_left}")
    if not all(
        refinement.circuit_positive(P, relation_signs, signature)
        for signature in exchanged_left
    ):
        raise AssertionError("an exchanged receiver lost the selected wall circuit")
    return len(common_bad), len(active), minimum, common_roots, exchanged_left


def semantic_digest(records):
    digest = sha256()
    digest.update(FORMAT.encode("ascii") + b"\0")
    digest.update(repr(records).encode("ascii"))
    return digest.hexdigest()


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--full-selection",
        action="store_true",
        help="re-enumerate both complete tope tables and reselect the pair/root",
    )
    parser.add_argument(
        "--skip-orbit",
        action="store_true",
        help="skip the exact 40,320-permutation source-accounting replay",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    factor_ids, factor_polynomials = robust.canonical_data()
    if FACTOR != min(set(factor_ids.values())) or factor_ids[KIND] != FACTOR:
        raise AssertionError("type 49 is no longer the smallest canonical factor ID")
    witness = robust.construct_witness(KIND, factor_ids, factor_polynomials)
    if witness.epsilon != EPSILON or witness.pivot != 3:
        raise AssertionError("canonical type-49 wall witness changed")
    if escape.DIRECTIONS[ROOT] != ROOT_DIRECTION:
        raise AssertionError("root 73 direction changed")
    predicates = local_switch.RootPredicates.build(P)
    compatible_common_roots = tuple(
        root
        for root in EXPECTED_COMMON_ROOTS
        if all(
            predicates.vertex_mask(signature) & (1 << root)
            for signature in PAIR + (RECEIVER,)
        )
    )
    if compatible_common_roots != EXPECTED_WALL_COMPATIBLE_COMMON_ROOTS:
        raise AssertionError(
            f"wall-compatible common roots changed: {compatible_common_roots}"
        )
    if ROOT != min(compatible_common_roots):
        raise AssertionError("root 73 is no longer the smallest wall-compatible choice")

    occurrences, occurrence_factor, _same_polynomials = labeled.factor_polynomials()
    if (
        labeled.occurrence_representatives()[KIND] != P
        or occurrences[OCCURRENCE_INDEX] != P
        or occurrence_factor[P] != FACTOR
    ):
        raise AssertionError("type-49 occurrence/factor identity changed")

    restrictions = tuple(
        restrict_normalized_polynomial(polynomial, witness.center)
        for polynomial in factor_polynomials
    )
    if restrictions[FACTOR] != {(1, 0): Fraction(1)}:
        raise AssertionError(
            f"selected factor does not restrict exactly to t: {restrictions[FACTOR]}"
        )
    factor_signs = []
    for factor, polynomial in enumerate(restrictions):
        if factor == FACTOR:
            continue
        factor_sign = strict_bernstein_sign(polynomial)
        if not factor_sign:
            raise AssertionError(f"factor {factor} is not isolated on the collar")
        factor_signs.append((factor, factor_sign))
    wide_failures = tuple(
        factor
        for factor, polynomial in enumerate(restrictions)
        if factor != FACTOR
        and not strict_bernstein_sign(polynomial, height=Fraction(1, 64))
    )
    if wide_failures != (15_226,):
        raise AssertionError(f"1/64 Bernstein canary changed: {wide_failures}")

    bracket_restrictions = {
        label: restrict_normalized_polynomial(polynomial, witness.center)
        for label, polynomial in robust.bracket_polynomials().items()
    }
    bracket_signs = {
        label: strict_bernstein_sign(polynomial)
        for label, polynomial in bracket_restrictions.items()
    }
    if len(bracket_signs) != 70 or not all(bracket_signs.values()):
        raise AssertionError("a parent bracket is not strict on the collar")

    bottom_wall = family_integer_matrix(witness, 0, 0)
    top_wall = family_integer_matrix(witness, 0, COLLAR_HEIGHT)
    relation_table = frontier.fixed_unit_relation_table(occurrences)
    relation = relation_table[P]
    expected_relation = (
        KIND,
        P,
        ((7, 14, 28, 1), (0, 14, 28, 1), (0, 7, 28, 1), (0, 7, 14, 1)),
    )
    if relation != expected_relation:
        raise AssertionError(f"fixed-unit relation changed: {relation}")
    relation_signs = []
    for matrix in (bottom_wall, top_wall):
        got = frontier.certified_relation_signs(
            topes.derived_rows(matrix, normalize=False), relation[1], relation[2]
        )
        if got != RELATION_SIGNS:
            raise AssertionError(f"fixed-unit relation signs changed: {got}")
        relation_signs.append(got)
    for signature in PAIR + (RECEIVER,):
        if not refinement.circuit_positive(P, RELATION_SIGNS, signature):
            raise AssertionError(f"signature {signature} lost the wall circuit")

    # At u=0 the exact endpoint circuits give the bad colors directly.
    circuit_records = []
    side_matrix = {
        "left": family_integer_matrix(witness, -EPSILON, 0),
        "right": family_integer_matrix(witness, EPSILON, 0),
    }
    if side_matrix["left"] != robust.integer_matrix(witness.left):
        raise AssertionError("left collar corner left the canonical path")
    if side_matrix["right"] != robust.integer_matrix(witness.right):
        raise AssertionError("right collar corner left the canonical path")
    for signature, side, auxiliary, expected in ENDPOINT_CIRCUITS:
        support = tuple(sorted(P + (auxiliary,)))
        got = circuit_vector(side_matrix[side], signature, support)
        if got != expected or not all(value > 0 for value in got):
            raise AssertionError(
                f"wrong {side} circuit for {signature}: {support}, {got}"
            )
        # The same support stays positive at the top corner of that chamber.
        top_side = family_integer_matrix(
            witness, -EPSILON if side == "left" else EPSILON, COLLAR_HEIGHT
        )
        top_vector = circuit_vector(top_side, signature, support)
        if not all(value > 0 for value in top_vector):
            raise AssertionError("an endpoint circuit did not transport up the collar")
        circuit_records.append((signature, side, support, got, top_vector))

    # The receiver is genuinely feasible in the left chamber.
    if realized_signature(side_matrix["left"], RECEIVER_LEFT_VECTOR) != RECEIVER:
        raise AssertionError("the exact receiver feasibility witness changed")

    zero_weight_records = []
    auxiliaries = tuple(sorted(set(row[2] for row in ENDPOINT_CIRCUITS)))
    for u, matrix in ((Fraction(0), bottom_wall), (COLLAR_HEIGHT, top_wall)):
        wall_weights = circuit_vector(matrix, PAIR[0], P)
        if wall_weights != WALL_WEIGHTS[u] or not all(value > 0 for value in wall_weights):
            raise AssertionError(f"wall weights changed at u={u}: {wall_weights}")
        for signature in PAIR + (RECEIVER,):
            if circuit_vector(matrix, signature, P) != wall_weights:
                raise AssertionError("wall circuit depends on the selected color")
            for auxiliary in auxiliaries:
                zero_weight_records.append(
                    (u, signature) + verify_zero_weight_specialization(
                        matrix, signature, auxiliary, wall_weights
                    )
                )

    ray_terminals = tuple(
        atlas_schema.ray_terminal(family_integer_matrix(witness, t, 0), ROOT)
        for t in (-EPSILON, Fraction(0), EPSILON)
    )
    if ray_terminals != (RAY_TERMINAL,) * 3:
        raise AssertionError(f"root-73 parent terminals changed: {ray_terminals}")
    if atlas_schema.BRACKET_LABELS[RAY_TERMINAL[3][0]] != RAY_TERMINAL_LABEL:
        raise AssertionError("root-73 terminal label changed")

    incidence = incidence_audit()
    orbit = None if args.skip_orbit else orbit_accounting(
        witness, occurrences, occurrence_factor
    )
    selection = None
    if args.full_selection:
        selection = full_selection_audit(witness, RELATION_SIGNS)

    degree_histogram = dict(sorted(Counter(map(bidegree, restrictions)).items()))
    sign_histogram = dict(sorted(Counter(value for _factor, value in factor_signs).items()))
    records = (
        witness.center,
        witness.left,
        witness.right,
        P,
        PAIR,
        RECEIVER,
        ROOT_DIRECTION,
        EPSILON,
        COLLAR_HEIGHT,
        restrictions[FACTOR],
        degree_histogram,
        sign_histogram,
        tuple(sorted(bracket_signs.items())),
        relation,
        tuple(relation_signs),
        tuple(circuit_records),
        tuple(zero_weight_records),
        ray_terminals,
        incidence,
        orbit,
        selection,
    )
    semantic = semantic_digest(records)
    expected_semantic = (
        EXPECTED_FULL_SEMANTIC_DIGEST
        if args.full_selection else EXPECTED_SEMANTIC_DIGEST
    )
    if not args.skip_orbit and semantic != expected_semantic:
        raise AssertionError(f"residual-wall collar semantic changed: {semantic}")

    print(
        "PASS isolated collar: factor 2267=t; 26739 other factors and "
        "70 parent brackets strict"
    )
    print(
        "PASS colors: pair bad on both chambers; receiver feasible left and "
        "triple-relative on wall/right"
    )
    print(
        "PASS zero weights: wall P=(0,7,14,28), weights "
        "(112,8,8,1)->(1792,128,1,16)"
    )
    print(
        "PASS incidence: absolute ranks Z/F2=(5,2); relative cochain "
        "ranks Z/F2=(2,1); integral MN=0"
    )
    if orbit is not None:
        print(
            "PASS S8 accounting: source=40320 occurrence/factor=10080/10080 "
            "two-sided-ID-overlap=3720 row2599-parent-hits=0 assignments=0"
        )
    if selection is not None:
        print(
            "PASS full selection: 814 active common-bad signatures, minimum "
            "overlap 20, pinned pair/root 73 and receiver exchange"
        )
    print(f"SEMANTIC {semantic}")
    print(
        "SCOPE one exact local type-49 adjacency collar; no row-2599 chamber "
        "coverage and no global pair H_c^1 conclusion"
    )


if __name__ == "__main__":
    main()
