#!/usr/bin/env python3
"""Exact row-2599 ordered-sector residence and outer-cap audit.

This is deliberately local.  It computes the complete origin parent-sign
component for the five valid ordered singleton sectors in the joined
flow-triangle canary.  It tests whether the product of the two independently
first-wall-truncated rays is a relative-homology model of that component.
It does not construct a comparison three-cell or a global pair complex.
"""

from __future__ import annotations

from fractions import Fraction
from hashlib import sha256
from math import lcm
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
OMREAL = HERE.parent
sys.path.insert(0, str(OMREAL))

import verify_diag2_escape_set_topes as escape  # noqa: E402
import verify_diag2_moving_witness_shear as moving  # noqa: E402
import DIAG9_GRAPH_exact_topes as exact_topes  # noqa: E402
import verify_diag3_joined_flow_triangle as joined  # noqa: E402
import verify_diag3_ordered_root_atlas178 as ordered  # noqa: E402
import verify_diag3_pair_global_atlas_schema as atlas  # noqa: E402
import verify_diag3_row2599_common_proper_escape as common  # noqa: E402


SOURCE = OMREAL / "data/seeat_parent2599_upper178.npz"
SOURCE_SHA256 = "3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a"

# Root order is d01,d12,d20.  These are the exact positive first-parent-wall
# parameters of the three individual rays at chart zero.
ROOT_ENDPOINTS = (
    Fraction(1_221_971_981, 1_769_366_234),
    Fraction(42_214_994, 2_183_619_501),
    Fraction(425_791_163, 1_286_992_887),
)
ROOT_WALLS = ("1234", "1358", "1256")

# The five orders accepted by the exact ordered-root witness theorem.
VALID_ORDERS = (
    (0, (0, 2)),
    (0, (2, 0)),
    (1, (0, 1)),
    (2, (1, 2)),
    (2, (2, 1)),
)

# The H0 residence component has a larger cap.  In forward coordinates its
# additional constant upper wall is [1278], and [1256] switches to it at U*.
H0_OUTER_WALL = "1278"
H0_OUTER_HEIGHT = Fraction(2_076_877_735, 5_073_331_504)
H0_SWITCH = Fraction(
    2_563_735_753_704_858_965,
    18_122_074_711_096_100_794,
)

# Exact attempted parent-wall collar for the exceptional p01 wall.  The
# [1234] arc hits the block-0 witness wall before its first additional parent
# wall [1367].  At the pinned midpoint the displayed integer covector realizes
# signature 0, rigorously proving that block 0 is good there.
P01_WITNESS_WALL = Fraction(
    83_503_134_767_238_851_186_305_349_765_512_866,
    43_552_580_189_648_394_406_194_000_441_042_241,
)
P01_FIRST_PARENT_CORNER = Fraction(
    3_797_676_243_957_714,
    1_934_663_274_435_289,
)
P01_TARGET_WALL_PARAMETER = Fraction(
    150_232_380_670_800_142_796_191_902,
    36_368_055_566_722_865_061_946_027,
)
P01_1367_2467_ROOT = Fraction(
    74_520_518_780_897,
    5_145_156_267_709_928,
)
P01_GOOD_COVECTOR = (10_000, 177, -7_015, 368)

SAFE_SUPPORTS = {
    0: (2, 19, 21, 37, 38),
    1: (2, 9, 27, 30, 35),
    2: (0, 11, 17, 24, 40),
}
SAFE_SUPPORT_LABELS = {
    0: ("134", "456", "137", "238", "148"),
    1: ("134", "345", "257", "167", "128"),
    2: ("123", "136", "256", "247", "348"),
}

EXPECTED_ORDER_DIGEST = "5941481177b36052e3e59bf08fa44cddadaa415fe761e091a2e8d8b2299ffc1c"


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        while block := source.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def compact(value: Fraction) -> Fraction:
    """u -> x=u/(1+u)."""
    return value / (1 + value)


def signed(polynomial):
    sign = 1 if polynomial[(0, 0)] > 0 else -1
    return {monomial: sign * Fraction(value) for monomial, value in polynomial.items()}


def coefficient(polynomial, u_degree, v_degree):
    return polynomial.get((u_degree, v_degree), Fraction(0))


def evaluate(polynomial, u, v):
    return sum(
        value * u ** u_degree * v ** v_degree
        for (u_degree, v_degree), value in polynomial.items()
    )


def mp_restrict(polynomial, axis, value):
    """Restrict one variable of a sparse Q[s,x,y] polynomial exactly."""
    value = Fraction(value)
    answer = {}
    for exponent, coefficient_value in polynomial.items():
        restricted = list(exponent)
        power = restricted[axis]
        restricted[axis] = 0
        restricted = tuple(restricted)
        answer[restricted] = answer.get(restricted, Fraction(0)) + (
            coefficient_value * value**power
        )
    return {exponent: coefficient_value for exponent, coefficient_value in answer.items()
            if coefficient_value}


def mp_restrict_matrix(matrix, restrictions):
    answer = matrix
    for axis, value in restrictions:
        answer = [
            [mp_restrict(entry, axis, value) for entry in row]
            for row in answer
        ]
    return answer


def mp_matrix_equal(left, right):
    return all(
        left[row][column] == right[row][column]
        for row in range(4)
        for column in range(8)
    )


def compactify(polynomial):
    """Return (1-x)(1-y)q(x/(1-x),y/(1-y))."""
    c = coefficient(polynomial, 0, 0)
    a = coefficient(polynomial, 1, 0)
    b = coefficient(polynomial, 0, 1)
    d = coefficient(polynomial, 1, 1)
    answer = {
        (0, 0): c,
        (1, 0): a - c,
        (0, 1): b - c,
        (1, 1): c - a - b + d,
    }
    return {monomial: value for monomial, value in answer.items() if value}


def matrix_rank(matrix):
    """Exact rational rank of a small integer matrix."""
    work = [[Fraction(value) for value in row] for row in matrix]
    if not work:
        return 0
    rows, columns = len(work), len(work[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        value = work[pivot_row][column]
        work[pivot_row] = [entry / value for entry in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row or not work[row][column]:
                continue
            value = work[row][column]
            work[row] = [
                left - value * right
                for left, right in zip(work[row], work[pivot_row], strict=True)
            ]
        pivot_row += 1
    return pivot_row


def mat_vec(matrix, vector):
    return tuple(
        sum(value * vector[column] for column, value in enumerate(row))
        for row in matrix
    )


def verify_signed_cone_boundary_table():
    """Pin the exact leftover comparison cycle of the seven raw sweeps."""
    # Rows e01,e12,e20,r0a,r1a,r1b,r2b,r2c,r0c; columns
    # T,S01,S12,S20,H0,H1,H2.
    relative_boundary_2 = (
        (+1, +1, 0, 0, 0, 0, 0),
        (+1, 0, +1, 0, 0, 0, 0),
        (+1, 0, 0, +1, 0, 0, 0),
        (0, -1, 0, 0, +1, 0, 0),
        (0, +1, 0, 0, 0, -1, 0),
        (0, 0, -1, 0, 0, +1, 0),
        (0, 0, +1, 0, 0, 0, -1),
        (0, 0, 0, -1, 0, 0, +1),
        (0, 0, 0, +1, -1, 0, 0),
    )
    relation = (-1, +1, +1, +1, +1, +1, +1)
    if mat_vec(relative_boundary_2, relation) != (0,) * 9:
        raise AssertionError("joined flow relation changed")

    # Absolute parent-frontier rows p01,p12,p20,h0,h1,h2.  Orient p_ij
    # from its first block endpoint to its second, and h0:w0a->w0c,
    # h1:w1a->w1b, h2:w2b->w2c.  These signs are forced by the displayed
    # relative boundaries of S_ij and H_i.
    parent_frontier = (
        (0, -1, 0, 0, 0, 0, 0),
        (0, 0, -1, 0, 0, 0, 0),
        (0, 0, 0, -1, 0, 0, 0),
        (0, 0, 0, 0, +1, 0, 0),
        (0, 0, 0, 0, 0, -1, 0),
        (0, 0, 0, 0, 0, 0, -1),
    )
    frontier_cycle = mat_vec(parent_frontier, relation)
    expected_cycle = (-1, -1, -1, +1, -1, -1)
    if frontier_cycle != expected_cycle:
        raise AssertionError(f"wrong swept-frontier cycle: {frontier_cycle}")

    # Rows w0a,w1a,w1b,w2b,w2c,w0c; same six edge columns.  Each column is
    # endpoint minus source.
    frontier_boundary = (
        (-1, 0, 0, -1, 0, 0),
        (+1, 0, 0, 0, -1, 0),
        (0, -1, 0, 0, +1, 0),
        (0, +1, 0, 0, 0, -1),
        (0, 0, -1, 0, 0, +1),
        (0, 0, +1, +1, 0, 0),
    )
    if mat_vec(frontier_boundary, frontier_cycle) != (0,) * 6:
        raise AssertionError("the comparison hexagon is not a cycle")
    if matrix_rank(frontier_boundary) != 5:
        raise AssertionError("the comparison hexagon boundary rank changed")
    if matrix_rank([list(frontier_cycle)]) != 1 or 1 not in map(abs, frontier_cycle):
        raise AssertionError("the comparison hexagon generator is not primitive")

    # For K(C), use dK(C)=C-K(d_rel C)-K(d_parent C).  The signed sum of
    # seven certified raw sweeps therefore has exactly the desired top
    # relation and the negative comparison hexagon as its only extra face.
    raw_top = relation
    raw_lateral = tuple(-value for value in mat_vec(relative_boundary_2, relation))
    raw_comparison = tuple(-value for value in frontier_cycle)
    if raw_lateral != (0,) * 9:
        raise AssertionError("raw sweep lateral faces do not cancel")

    # One additional relative 3-chain J with boundary K(frontier_cycle)
    # would cancel the six extra faces.  Its column is the unique primitive
    # kernel generator: rank(d2)+rank(d3)=5+1=6.
    if matrix_rank(frontier_boundary) + matrix_rank([list(frontier_cycle)]) != 6:
        raise AssertionError("one comparison filler would not close the local kernel")
    closed_comparison = tuple(
        left + right for left, right in zip(raw_comparison, frontier_cycle, strict=True)
    )
    if closed_comparison != (0,) * 6:
        raise AssertionError("formal comparison filler has wrong orientation")
    return {
        "relation": relation,
        "frontier_edge_order": ("p01", "p12", "p20", "h0", "h1", "h2"),
        "frontier_cycle": frontier_cycle,
        "raw_cone_boundary": {
            "top": raw_top,
            "lateral": raw_lateral,
            "comparison": raw_comparison,
        },
        "missing_filler_boundary": frontier_cycle,
        "ranks_without_with_filler": ((5, 0, 1), (5, 1, 0)),
    }


def relative_betti(cells, boundary_1, boundary_2):
    c0, c1, c2 = cells
    rank_1 = matrix_rank(boundary_1)
    rank_2 = matrix_rank(boundary_2)
    # Matrices are C0 x C1 and C1 x C2.
    for row in range(c0):
        for column in range(c2):
            if sum(
                boundary_1[row][middle] * boundary_2[middle][column]
                for middle in range(c1)
            ):
                raise AssertionError("relative cellular boundary does not square to zero")
    return (c0 - rank_1, c1 - rank_1 - rank_2, c2 - rank_2)


def verify_relative_models():
    # Rectangle relative to its connected top/right parent-boundary arc.
    rectangle = relative_betti(
        (1, 2, 1),
        [[-1, -1]],
        [[1], [-1]],
    )
    # H0 first-wall square: its right parent edge and isolated upper-left
    # parent point leave a primitive interface cycle.
    first_square = relative_betti(
        (1, 3, 1),
        [[-1, -1, 0]],
        [[1], [-1], [-1]],
    )
    # Attach the exact outer cap.  Its only nonrelative boundary is the old
    # first-square top interface, so it kills that primitive H1 class.
    full_cap = relative_betti(
        (1, 3, 2),
        [[-1, -1, 0]],
        [[1, 0], [-1, 0], [-1, 1]],
    )
    if rectangle != (0, 0, 0):
        raise AssertionError(f"rectangle relative homology changed: {rectangle}")
    if first_square != (0, 1, 0):
        raise AssertionError(f"H0 first-square relative homology changed: {first_square}")
    if full_cap != (0, 0, 0):
        raise AssertionError(f"H0 capped relative homology changed: {full_cap}")
    return rectangle, first_square, full_cap


def barrier_root(polynomial, axis):
    other = 1 - axis
    if any(monomial[other] for monomial in polynomial):
        return None
    linear = (1, 0) if axis == 0 else (0, 1)
    slope = polynomial.get(linear, Fraction(0))
    if not slope:
        return None
    return -polynomial[(0, 0)] / slope


def verify_rectangle(polynomials, order):
    limits = (ROOT_ENDPOINTS[order[0]], ROOT_ENDPOINTS[order[1]])
    walls = (ROOT_WALLS[order[0]], ROOT_WALLS[order[1]])
    by_label = dict(zip(atlas.BRACKET_LABELS, polynomials, strict=True))
    for axis in range(2):
        if barrier_root(by_label[walls[axis]], axis) != limits[axis]:
            raise AssertionError(f"{order}: wrong global barrier {walls[axis]}")

    x_limit, y_limit = map(compact, limits)
    zero_labels = []
    for label, polynomial in by_label.items():
        transformed = compactify(polynomial)
        values = tuple(
            evaluate(transformed, x, y)
            for x, y in (
                (Fraction(0), Fraction(0)),
                (x_limit, Fraction(0)),
                (Fraction(0), y_limit),
                (x_limit, y_limit),
            )
        )
        if min(values) < 0:
            raise AssertionError(f"{order}: signed compact bracket {label} fails")
        if min(values) == 0:
            zero_labels.append(label)
    if tuple(zero_labels) != tuple(sorted(walls)):
        raise AssertionError(f"{order}: rectangle wall labels changed: {zero_labels}")
    return limits, walls


def verify_h0_cap(polynomials, order):
    # Canonically put d01 on the u axis and d20 on the v axis.  The reverse
    # order is exactly the coordinate swap and is checked before reuse.
    if order == (2, 0):
        polynomials = tuple(
            {(v_degree, u_degree): value for (u_degree, v_degree), value in item.items()}
            for item in polynomials
        )
    by_label = dict(zip(atlas.BRACKET_LABELS, polynomials, strict=True))
    u_limit = ROOT_ENDPOINTS[0]
    first_height = ROOT_ENDPOINTS[2]
    outer_height = H0_OUTER_HEIGHT

    if barrier_root(by_label["1234"], 0) != u_limit:
        raise AssertionError("H0 lost its [1234] vertical barrier")
    if barrier_root(by_label[H0_OUTER_WALL], 1) != outer_height:
        raise AssertionError("H0 lost its [1278] outer barrier")

    switch_wall = by_label["1256"]
    c = coefficient(switch_wall, 0, 0)
    a = coefficient(switch_wall, 1, 0)
    b = coefficient(switch_wall, 0, 1)
    d = coefficient(switch_wall, 1, 1)
    if -c / b != first_height:
        raise AssertionError("H0 [1256] axis wall changed")
    if b >= 0 or b + d * u_limit >= 0:
        raise AssertionError("H0 [1256] does not remain an upper graph")
    derivative_numerator = a * (-b) - (-d) * c
    if derivative_numerator <= 0:
        raise AssertionError("H0 [1256] upper graph is not increasing")
    switch = -(c + b * outer_height) / (a + d * outer_height)
    if switch != H0_SWITCH or not 0 < switch < u_limit:
        raise AssertionError(f"H0 switch changed: {switch}")

    # Apart from the three displayed walls, every signed parent bracket is
    # strictly positive on the larger bounding rectangle.  Multiaffinity
    # makes the four exact vertex values an exhaustive certificate.
    x_limit, y_limit = compact(u_limit), compact(outer_height)
    for label, polynomial in by_label.items():
        if label in ("1234", "1256", H0_OUTER_WALL):
            continue
        transformed = compactify(polynomial)
        values = tuple(
            evaluate(transformed, x, y)
            for x, y in (
                (Fraction(0), Fraction(0)),
                (x_limit, Fraction(0)),
                (Fraction(0), y_limit),
                (x_limit, y_limit),
            )
        )
        if min(values) <= 0:
            raise AssertionError(f"H0 bounding rectangle acquired wall {label}")

    # The switch wall lies above the first square except at its upper-left
    # corner; its graph meets [1278] once at U*.  These signs pin the cap.
    if evaluate(switch_wall, 0, first_height) != 0:
        raise AssertionError("H0 cap does not start at the first-wall corner")
    if evaluate(switch_wall, switch, outer_height) != 0:
        raise AssertionError("H0 cap switch is not on both walls")
    if evaluate(switch_wall, u_limit, outer_height) <= 0:
        raise AssertionError("H0 outer horizontal wall does not reach [1234]")

    return {
        "u_limit": u_limit,
        "first_height": first_height,
        "outer_height": outer_height,
        "switch": switch,
        "walls": ("1256", H0_OUTER_WALL, "1234"),
    }


def verify_safe_tapered_witness(matrix, block, order, roots):
    """Check ordered-root safety and one strict exact tapered circuit."""
    support = SAFE_SUPPORTS[block]
    labels = tuple("".join(map(str, moving.TRIPLES[index])) for index in support)
    if labels != SAFE_SUPPORT_LABELS[block]:
        raise AssertionError(f"block {block}: safe support labels changed: {labels}")

    safe_mask = ordered.safe_rows(
        joined.SIGNATURES[block], roots[order[0]], roots[order[1]]
    )
    if any(not ((safe_mask >> index) & 1) for index in support):
        raise AssertionError(f"block {block}/{order}: support is not transport-safe")
    # This verifies exact positivity, dependence, and support-minimality at
    # the source matrix independently of the bivariate safe-row screen.
    moving.positive_circuit_cofactors(
        matrix, joined.SIGNATURES[block], support
    )

    target = common.tapered_matrix(
        matrix,
        common.EXPECTED_DIRECTION,
        order,
    )
    normals = common.mp_normals(target)
    coefficients = common.mp_circuit(
        normals, joined.SIGNATURES[block], support
    )
    circuit_sign = 1 if common.mp_at_origin(coefficients[0]) > 0 else -1
    for coefficient in coefficients:
        if min(
            circuit_sign * value for value in common.mp_bernstein(coefficient)
        ) <= 0:
            raise AssertionError(f"block {block}/{order}: tapered circuit lost strictness")

    # Replay the four polynomial kernel coordinates, rather than relying only
    # on the alternating-cofactor construction.
    for coordinate in range(4):
        total = {}
        for index, coefficient in zip(support, coefficients, strict=True):
            term = common.mp_multiply(coefficient, normals[index][coordinate])
            total = common.mp_add(
                total,
                common.mp_scale(
                    term,
                    moving.signature_sign(joined.SIGNATURES[block], index),
                ),
            )
        if total:
            raise AssertionError(f"block {block}/{order}: tapered kernel identity failed")
    return labels


def pair_sweep_matrix(matrix, root_index):
    """Common-ray sweep of one first-wall root, with radial parameter x."""
    target = [
        [common.mp_constant(int(matrix[row, column])) for column in range(8)]
        for row in range(4)
    ]
    s = {(1, 0, 0): Fraction(1)}
    x = {(0, 1, 0): Fraction(1)}
    one_minus_s = {(0, 0, 0): Fraction(1), (1, 0, 0): Fraction(-1)}
    for row in range(4):
        target[row][common.MOVING_COLUMN] = common.mp_add(
            target[row][common.MOVING_COLUMN],
            common.mp_scale(
                s,
                common.ENDPOINT * common.EXPECTED_DIRECTION[row],
            ),
        )
    source, destination, sign = common.PAIR_ROOTS[root_index]
    amplitude = common.mp_scale(
        common.mp_multiply(one_minus_s, x),
        sign * ROOT_ENDPOINTS[root_index],
    )
    for row in range(4):
        target[row][source - 1] = common.mp_add(
            target[row][source - 1],
            common.mp_multiply(amplitude, target[row][destination - 1]),
        )
    return target


def circuit_coefficients(target, block):
    return common.mp_circuit(
        common.mp_normals(target), joined.SIGNATURES[block], SAFE_SUPPORTS[block]
    )


def verify_strict_polynomial_circuit(target, block, name):
    coefficients = circuit_coefficients(target, block)
    circuit_sign = 1 if common.mp_at_origin(coefficients[0]) > 0 else -1
    minimums = tuple(
        min(circuit_sign * value for value in common.mp_bernstein(coefficient_value))
        for coefficient_value in coefficients
    )
    if min(minimums) <= 0:
        raise AssertionError(f"{name}: block {block} circuit lost strictness")
    normals = common.mp_normals(target)
    for coordinate in range(4):
        total = {}
        for index, coefficient_value in zip(
            SAFE_SUPPORTS[block], coefficients, strict=True
        ):
            total = common.mp_add(
                total,
                common.mp_scale(
                    common.mp_multiply(coefficient_value, normals[index][coordinate]),
                    moving.signature_sign(joined.SIGNATURES[block], index),
                ),
            )
        if total:
            raise AssertionError(f"{name}: block {block} kernel identity failed")
    return coefficients


def verify_frontier_witness_cospan(matrix):
    """Certify the six pair/singleton seams and the common apex sections.

    This is a witness-face theorem only.  It proves that the six surfaces in
    K(F) have compatible normalized Gordan sections.  It deliberately does
    not assert that the resulting relative two-cycle bounds a base-space
    mixed three-chain.
    """
    pair_blocks = ((0, 1), (1, 2), (2, 0))
    singleton_orders = ((0, 2), (0, 1), (1, 2))
    cubes = tuple(
        common.tapered_matrix(matrix, common.EXPECTED_DIRECTION, order)
        for order in singleton_orders
    )
    pairs = tuple(pair_sweep_matrix(matrix, root) for root in range(3))

    # p01 is the first-root face of H0 and H1; p12 is the second-root
    # face of H1 and first-root face of H2; p20 is the second-root face of
    # H2 and H0.  Set the unused root parameter to zero and the retained one
    # to its first-wall value (normalized cube coordinate one).
    seam_specs = (
        (0, 0, ((1, 1), (2, 0))),
        (0, 1, ((1, 1), (2, 0))),
        (1, 1, ((1, 0), (2, 1))),
        (1, 2, ((1, 1), (2, 0))),
        (2, 2, ((1, 0), (2, 1))),
        (2, 0, ((1, 0), (2, 1))),
    )
    pair_faces = tuple(mp_restrict_matrix(target, ((1, 1),)) for target in pairs)
    seam_report = []
    for pair_index, block, restrictions in seam_specs:
        singleton = mp_restrict_matrix(cubes[block], restrictions)
        if not mp_matrix_equal(singleton, pair_faces[pair_index]):
            raise AssertionError(
                f"p{pair_index}/H{block}: base-matrix seam is not literal"
            )
        singleton_coefficients = circuit_coefficients(singleton, block)
        pair_coefficients = circuit_coefficients(pair_faces[pair_index], block)
        if singleton_coefficients != pair_coefficients:
            raise AssertionError(
                f"p{pair_index}/H{block}: cofactor witness seam changed"
            )
        seam_report.append((pair_index, block))

    # Each pair face has both adjacent strict block sections.  Normalizing
    # either positive cofactor vector and multiplying them by lambda and
    # 1-lambda therefore gives the entire joined pair edge, with the above
    # singleton sections as its literal endpoints.
    pair_reports = []
    for pair_index, blocks in enumerate(pair_blocks):
        reports = tuple(
            tuple(
                min(value for value in common.mp_bernstein(coefficient_value))
                for coefficient_value in verify_strict_polynomial_circuit(
                    pair_faces[pair_index], block, f"p{pair_index}"
                )
            )
            for block in blocks
        )
        pair_reports.append((pair_index, blocks, reports))

    # At s=1 every root amplitude is zero.  The two appearances of each
    # block on its incident pair faces must therefore give exactly the same
    # endpoint matrix and the same cofactor section.  The only surviving
    # parameter on p_ij is block mass, so the three apex pair edges are the
    # literal boundary of the block-mass triangle.
    apex_matrices = tuple(mp_restrict_matrix(target, ((0, 1),)) for target in pair_faces)
    if not all(mp_matrix_equal(apex_matrices[0], item) for item in apex_matrices[1:]):
        raise AssertionError("pair sweeps do not share one common endpoint base")
    common_apex = apex_matrices[0]
    endpoint_zeros = tuple(
        "".join(map(str, basis))
        for basis in moving.BASES4
        if not common.mp_determinant(
            [[common_apex[row][label - 1] for label in basis] for row in range(4)]
        )
    )
    if endpoint_zeros != ("2467",):
        raise AssertionError(f"common endpoint wall changed: {endpoint_zeros}")
    apex_sections = []
    for block in range(3):
        incident = tuple(
            pair_index
            for pair_index, blocks in enumerate(pair_blocks)
            if block in blocks
        )
        sections = tuple(
            circuit_coefficients(apex_matrices[pair_index], block)
            for pair_index in incident
        )
        if sections[0] != sections[1]:
            raise AssertionError(f"block {block}: common-apex witness mismatch")
        apex_sections.append((block, incident, sections[0]))

    mass_boundary = ((-1, 0, +1), (+1, -1, 0), (0, +1, -1))
    if matrix_rank(mass_boundary) != 2:
        raise AssertionError("common-apex mass triangle boundary changed")
    if mat_vec(mass_boundary, (1, 1, 1)) != (0, 0, 0):
        raise AssertionError("common-apex mass edges do not close")
    return {
        "literal_pair_singleton_seams": tuple(seam_report),
        "strict_pair_blocks": tuple(
            (pair_index, blocks) for pair_index, blocks, _report in pair_reports
        ),
        "common_endpoint_wall": endpoint_zeros,
        "common_apex_block_incidence": tuple(
            (block, incident) for block, incident, _section in apex_sections
        ),
        "mass_edge_kernel": (1, 1, 1),
    }


def verify_scalar_radial_filler_no_go(matrix):
    """Rule out the tempting scalar radial cone on the comparison cycle.

    On the p01 source face, scaling the first-wall root parameter by h lies
    on the parent boundary only at h=1.  A scalar contraction which keeps
    the s=0 face relative must therefore have h(0,r)=1.  Collapsing all root
    amplitudes to the common-ray mass triangle requires h(s,1)=0 for every
    s>0.  Those two boundary conditions have incompatible limits at (0,1).
    """
    radial = mp_restrict_matrix(pair_sweep_matrix(matrix, 0), ((0, 0),))
    base_brackets = moving.parent_brackets(matrix)
    endpoint_walls = []
    wall_polynomial = None
    for basis in moving.BASES4:
        polynomial = common.mp_determinant(
            [[radial[row][label - 1] for label in basis] for row in range(4)]
        )
        sign = 1 if base_brackets[basis] > 0 else -1
        signed_polynomial = common.mp_scale(polynomial, sign)
        bernstein = common.mp_bernstein(signed_polynomial)
        if min(bernstein) < 0:
            raise AssertionError(f"p01 radial segment leaves parent closure: {basis}")
        if min(bernstein) == 0:
            endpoint_walls.append("".join(map(str, basis)))
            if basis == (1, 2, 3, 4):
                wall_polynomial = signed_polynomial
        elif min(bernstein) <= 0:
            raise AssertionError(f"p01 radial nonwall bracket is not strict: {basis}")
    if tuple(endpoint_walls) != ("1234",):
        raise AssertionError(f"p01 radial endpoint wall changed: {endpoint_walls}")
    constant = wall_polynomial.get((0, 0, 0), Fraction(0))
    linear = wall_polynomial.get((0, 1, 0), Fraction(0))
    if constant <= 0 or linear != -constant or len(wall_polynomial) != 2:
        raise AssertionError(f"p01 radial wall is not c(1-h): {wall_polynomial}")
    return {
        "source_test_edge": "p01",
        "unique_relative_scalar": 1,
        "signed_wall": ("1234", constant, linear),
        "required_corner_limits": (1, 0),
        "conclusion": "no continuous scalar radial common-apex filler",
    }


def untapered_root_matrix(matrix, root_index, common_parameter, root_parameter):
    """Two-parameter common-column/root family without radial tapering."""
    target = [
        [common.mp_constant(int(matrix[row, column])) for column in range(8)]
        for row in range(4)
    ]
    for row in range(4):
        target[row][common.MOVING_COLUMN] = common.mp_add(
            target[row][common.MOVING_COLUMN],
            common.mp_scale(
                common_parameter,
                common.ENDPOINT * common.EXPECTED_DIRECTION[row],
            ),
        )
    source, destination, sign = common.PAIR_ROOTS[root_index]
    for row in range(4):
        target[row][source - 1] = common.mp_add(
            target[row][source - 1],
            common.mp_scale(
                common.mp_multiply(root_parameter, target[row][destination - 1]),
                sign,
            ),
        )
    return target


def linear_root(polynomial, axis=0):
    constant = polynomial.get((0, 0, 0), Fraction(0))
    exponent = [0, 0, 0]
    exponent[axis] = 1
    slope = polynomial.get(tuple(exponent), Fraction(0))
    if not slope:
        return None
    allowed = {(0, 0, 0), tuple(exponent)}
    if any(exponent_value not in allowed for exponent_value in polynomial):
        raise AssertionError(f"polynomial is not univariate affine: {polynomial}")
    return -constant / slope


def verify_parent_path(matrix, target, expected_weak_walls, name):
    base_brackets = moving.parent_brackets(matrix)
    weak_walls = []
    for basis in moving.BASES4:
        polynomial = common.mp_determinant(
            [[target[row][label - 1] for label in basis] for row in range(4)]
        )
        sign = 1 if base_brackets[basis] > 0 else -1
        bernstein = tuple(sign * value for value in common.mp_bernstein(polynomial))
        if min(bernstein) < 0:
            raise AssertionError(f"{name}: parent sign failed at {basis}")
        if min(bernstein) == 0:
            weak_walls.append("".join(map(str, basis)))
    if tuple(sorted(weak_walls)) != tuple(sorted(expected_weak_walls)):
        raise AssertionError(f"{name}: wall census changed: {weak_walls}")
    return tuple(sorted(weak_walls))


def verify_two_circuit(target, block, support, name):
    normals = common.mp_normals(target)
    left, right = support
    signed = tuple(
        tuple(
            common.mp_scale(
                value, moving.signature_sign(joined.SIGNATURES[block], index)
            )
            for value in normals[index]
        )
        for index in support
    )
    for first in range(4):
        for second in range(first + 1, 4):
            cross = common.mp_add(
                common.mp_multiply(signed[0][first], signed[1][second]),
                common.mp_scale(
                    common.mp_multiply(signed[0][second], signed[1][first]), -1
                ),
            )
            if cross:
                raise AssertionError(f"{name}: two-circuit proportionality failed")
    coordinate = next(
        coordinate
        for coordinate in range(4)
        if common.mp_at_origin(signed[0][coordinate])
        and common.mp_at_origin(signed[1][coordinate])
    )
    left_coefficient = common.mp_scale(signed[1][coordinate], -1)
    right_coefficient = signed[0][coordinate]
    common_sign = 1 if common.mp_at_origin(left_coefficient) > 0 else -1
    for coefficient_value in (left_coefficient, right_coefficient):
        if min(
            common_sign * value
            for value in common.mp_bernstein(coefficient_value)
        ) <= 0:
            raise AssertionError(f"{name}: two-circuit weight lost positivity")
    return tuple("".join(map(str, moving.TRIPLES[index])) for index in support)


def verify_parent_wall_collar_attempt(matrix):
    """Test the nonradial parent-wall collar to the common [2467] face.

    The p12 and p20 wall edges admit exact two-stage collars.  The analogous
    p01 collar is obstructed before its first codimension-two parent corner:
    block 0 becomes good on the [1234] arc.  This rules out this wall-slide
    architecture, not every possible higher-dimensional parent-boundary cap.
    """
    t = {(1, 0, 0): Fraction(1)}
    one_minus_t = {(0, 0, 0): Fraction(1), (1, 0, 0): Fraction(-1)}
    pair_blocks = ((0, 1), (1, 2), (2, 0))
    successful = []
    for root_index in (1, 2):
        # Stage one keeps the original first-root wall fixed while moving the
        # common column to [2467].
        wall_slide = untapered_root_matrix(
            matrix,
            root_index,
            t,
            common.mp_constant(ROOT_ENDPOINTS[root_index]),
        )
        wall_labels = verify_parent_path(
            matrix,
            wall_slide,
            (ROOT_WALLS[root_index], "2467"),
            f"p{root_index} wall slide",
        )
        for block in pair_blocks[root_index]:
            verify_strict_polynomial_circuit(
                wall_slide, block, f"p{root_index} wall slide"
            )

        # Stage two stays on [2467] and removes the root amplitude, ending at
        # the shared common-ray base.  Both joined block sections stay strict.
        endpoint_cone = untapered_root_matrix(
            matrix,
            root_index,
            common.mp_constant(1),
            common.mp_scale(one_minus_t, ROOT_ENDPOINTS[root_index]),
        )
        cone_labels = verify_parent_path(
            matrix,
            endpoint_cone,
            (ROOT_WALLS[root_index], "2467"),
            f"p{root_index} endpoint cone",
        )
        for block in pair_blocks[root_index]:
            verify_strict_polynomial_circuit(
                endpoint_cone, block, f"p{root_index} endpoint cone"
            )
        successful.append((root_index, wall_labels, cone_labels, pair_blocks[root_index]))

    # Exceptional p01: derive all three critical parameters from the exact
    # polynomials rather than trusting the displayed constants.
    general = untapered_root_matrix(
        matrix, 0, t, common.mp_constant(ROOT_ENDPOINTS[0])
    )
    polynomials = {
        "".join(map(str, basis)): common.mp_determinant(
            [[general[row][label - 1] for label in basis] for row in range(4)]
        )
        for basis in moving.BASES4
    }
    if polynomials["1234"]:
        raise AssertionError("p01 wall slide left [1234]")
    first_parent_corner = linear_root(polynomials["1367"])
    target_wall_parameter = linear_root(polynomials["2467"])
    if first_parent_corner != P01_FIRST_PARENT_CORNER:
        raise AssertionError(f"p01 [1367] corner changed: {first_parent_corner}")
    if target_wall_parameter != P01_TARGET_WALL_PARAMETER:
        raise AssertionError(f"p01 [2467] target changed: {target_wall_parameter}")

    block0_coefficients = circuit_coefficients(general, 0)
    block0_sign = 1 if common.mp_at_origin(block0_coefficients[0]) > 0 else -1
    witness_wall = linear_root(common.mp_scale(block0_coefficients[0], block0_sign))
    if witness_wall != P01_WITNESS_WALL:
        raise AssertionError(f"p01 block-0 witness wall changed: {witness_wall}")
    if not 0 < witness_wall < first_parent_corner < target_wall_parameter:
        raise AssertionError("p01 obstruction parameters lost their strict order")

    source_to_corner = untapered_root_matrix(
        matrix,
        0,
        common.mp_scale(t, first_parent_corner),
        common.mp_constant(ROOT_ENDPOINTS[0]),
    )
    source_corner_walls = verify_parent_path(
        matrix,
        source_to_corner,
        ("1234", "1367"),
        "p01 source-to-corner wall slide",
    )
    verify_strict_polynomial_circuit(source_to_corner, 1, "p01 block-1 wall slide")

    # At an exact point between the witness wall and the parent corner,
    # positively rescale each projective column to an integer matrix.  The
    # pinned integer covector realizes all 56 signs of signature 0, proving
    # by strict Gordan duality that block 0 is good there.
    good_parameter = (witness_wall + first_parent_corner) / 2
    good_matrix_polynomial = mp_restrict_matrix(general, ((0, good_parameter),))
    good_matrix = [
        [good_matrix_polynomial[row][column].get((0, 0, 0), Fraction(0))
         for column in range(8)]
        for row in range(4)
    ]
    integer_columns = []
    column_scales = []
    for column in range(8):
        scale = lcm(*(good_matrix[row][column].denominator for row in range(4)))
        column_scales.append(scale)
        integer_columns.append(
            tuple(int(good_matrix[row][column] * scale) for row in range(4))
        )
    integer_matrix = tuple(
        tuple(integer_columns[column][row] for column in range(8))
        for row in range(4)
    )
    derived = exact_topes.derived_rows(integer_matrix, normalize=True)
    signed_dots = tuple(
        moving.signature_sign(joined.SIGNATURES[0], index)
        * sum(value * P01_GOOD_COVECTOR[coordinate]
              for coordinate, value in enumerate(row))
        for index, row in enumerate(derived)
    )
    if min(signed_dots) != 5_966_575 or min(signed_dots) <= 0:
        raise AssertionError(f"p01 exact good covector changed: {min(signed_dots)}")

    # The parent geometry itself can continue: at [1367], vary the root to
    # the exact [2467] intersection.  Block 0 is again bad there by a strict
    # polynomial two-circuit, emphasizing that the failure is the intervening
    # good interval rather than a missing endpoint.
    corner_root = common.mp_add(
        common.mp_constant(ROOT_ENDPOINTS[0]),
        common.mp_scale(t, P01_1367_2467_ROOT - ROOT_ENDPOINTS[0]),
    )
    corner_to_target = untapered_root_matrix(
        matrix,
        0,
        common.mp_constant(first_parent_corner),
        corner_root,
    )
    corner_target_walls = verify_parent_path(
        matrix,
        corner_to_target,
        ("1234", "1367", "2467"),
        "p01 [1367]-to-[2467] slide",
    )
    block0_two_circuit = verify_two_circuit(
        corner_to_target, 0, (11, 30), "p01 [1367] block-0 circuit"
    )
    verify_strict_polynomial_circuit(
        corner_to_target, 1, "p01 [1367] block-1 circuit"
    )

    return {
        "successful_relative_collars": tuple(successful),
        "exceptional_edge": "p01",
        "critical_order": (
            ("block0_witness_wall", witness_wall),
            ("first_parent_corner_1367", first_parent_corner),
            ("fixed_root_target_2467", target_wall_parameter),
        ),
        "exact_good_point": (good_parameter, P01_GOOD_COVECTOR, min(signed_dots)),
        "source_corner_walls": source_corner_walls,
        "corner_target": (
            P01_1367_2467_ROOT,
            corner_target_walls,
            block0_two_circuit,
        ),
        "conclusion": "natural three-edge parent-wall cospan fails on p01",
    }


def verify_h0_cap_comparison(matrix, roots):
    """Exact H0 cap swept to the common proper ray.

    The lower patch is the graph strip between v=U20 and [1256]=0 for
    0<=u<=U*, written with a positive denominator D(u).  Scaling labelled
    column 1 by D is a positive projective-column gauge, so it preserves the
    represented configuration and every parent/circuit sign.  The upper
    patch is the rectangle U*<=u<=U01, U20<=v<=W.
    """
    u_limit = ROOT_ENDPOINTS[0]
    first_height = ROOT_ENDPOINTS[2]
    switch = H0_SWITCH
    outer_height = H0_OUTER_HEIGHT
    support = SAFE_SUPPORTS[0]

    s = {(1, 0, 0): Fraction(1)}
    one_minus_s = {(0, 0, 0): Fraction(1), (1, 0, 0): Fraction(-1)}
    x = {(0, 1, 0): Fraction(1)}
    y = {(0, 0, 1): Fraction(1)}

    def affine(left, right, variable):
        return common.mp_add(
            common.mp_constant(left), common.mp_scale(variable, right - left)
        )

    def base_with_common_ray():
        answer = [
            [common.mp_constant(int(matrix[row, column])) for column in range(8)]
            for row in range(4)
        ]
        for row in range(4):
            answer[row][common.MOVING_COLUMN] = common.mp_add(
                answer[row][common.MOVING_COLUMN],
                common.mp_scale(
                    s,
                    common.ENDPOINT * common.EXPECTED_DIRECTION[row],
                ),
            )
        return answer

    def add_d01(answer, u):
        amplitude = common.mp_scale(common.mp_multiply(one_minus_s, u), -1)
        for row in range(4):
            answer[row][1] = common.mp_add(
                answer[row][1],
                common.mp_multiply(amplitude, answer[row][7]),
            )

    # Upper rectangular patch.
    upper = base_with_common_ray()
    u_upper = affine(switch, u_limit, x)
    v_upper = affine(first_height, outer_height, y)
    add_d01(upper, u_upper)
    amplitude = common.mp_scale(common.mp_multiply(one_minus_s, v_upper), +1)
    for row in range(4):
        upper[row][0] = common.mp_add(
            upper[row][0], common.mp_multiply(amplitude, upper[row][2])
        )

    # Lower graph strip.  Signed [1256] is
    # C(u)-D(u)v with C=2128955815+4988347216u and
    # D=6434964435+3459743562u.  Interpolate v between U20 and C/D and
    # multiply column 1 by the positive gauge D.
    lower = base_with_common_ray()
    u_lower = common.mp_scale(x, switch)
    denominator = common.mp_add(
        common.mp_constant(6_434_964_435),
        common.mp_scale(u_lower, 3_459_743_562),
    )
    numerator_top = common.mp_add(
        common.mp_constant(2_128_955_815),
        common.mp_scale(u_lower, 4_988_347_216),
    )
    numerator = common.mp_add(
        common.mp_scale(denominator, first_height),
        common.mp_multiply(
            y,
            common.mp_add(
                numerator_top,
                common.mp_scale(denominator, -first_height),
            ),
        ),
    )
    add_d01(lower, u_lower)
    # Starting column 1 is unchanged by d01, so D*P1 +(1-s)N*P3 is the
    # positive-gauge version of P1 +(1-s)(N/D)P3.
    for row in range(4):
        lower[row][0] = common.mp_add(
            common.mp_scale(denominator, int(matrix[row, 0])),
            common.mp_scale(
                common.mp_multiply(one_minus_s, numerator),
                int(matrix[row, 2]),
            ),
        )

    def verify_positive_column_gauge(left, right, factor, name):
        """Compare cofactor sections across a positive labelled-column gauge."""
        for row in range(4):
            for column in range(8):
                expected = (
                    common.mp_multiply(factor, right[row][column])
                    if column == 0
                    else right[row][column]
                )
                if left[row][column] != expected:
                    raise AssertionError(f"H0 {name}: projective gauge matrix mismatch")
        left_coefficients = circuit_coefficients(left, 0)
        right_coefficients = circuit_coefficients(right, 0)
        scaled_rows = tuple(
            int(1 in moving.TRIPLES[index]) for index in support
        )
        total_scaled = sum(scaled_rows)
        common_factor = common.mp_constant(1)
        for _ in range(total_scaled):
            common_factor = common.mp_multiply(common_factor, factor)
        for scaled, left_value, right_value in zip(
            scaled_rows, left_coefficients, right_coefficients, strict=True
        ):
            left_value = (
                common.mp_multiply(left_value, factor) if scaled else left_value
            )
            right_value = common.mp_multiply(right_value, common_factor)
            if left_value != right_value:
                raise AssertionError(f"H0 {name}: normalized cofactor gauge mismatch")
        return total_scaled

    # The lower patch is written in a positive column-1 gauge.  Check its
    # two nonrelative gluing interfaces literally, including the induced
    # inverse gauge on normalized Gordan weights.
    lower_unscaled_bottom = base_with_common_ray()
    add_d01(lower_unscaled_bottom, u_lower)
    for row in range(4):
        lower_unscaled_bottom[row][0] = common.mp_add(
            lower_unscaled_bottom[row][0],
            common.mp_scale(
                common.mp_multiply(one_minus_s, common.mp_constant(first_height)),
                int(matrix[row, 2]),
            ),
        )
    bottom_gauge_rank = verify_positive_column_gauge(
        mp_restrict_matrix(lower, ((2, 0),)),
        lower_unscaled_bottom,
        denominator,
        "lower/first-square interface",
    )

    lower_upper_factor = mp_restrict(denominator, 1, 1)
    lower_upper_rank = verify_positive_column_gauge(
        mp_restrict_matrix(lower, ((1, 1),)),
        mp_restrict_matrix(upper, ((1, 0),)),
        lower_upper_factor,
        "lower/upper interface",
    )
    if (bottom_gauge_rank, lower_upper_rank) != (3, 3):
        raise AssertionError("H0 cap support gauge census changed")

    base_brackets = moving.parent_brackets(matrix)
    reports = []
    for name, target, expected_zero in (
        ("lower", lower, ("1256", "2467", "1278")),
        ("upper", upper, ("1234", "1256", "2467", "1278")),
    ):
        zero_labels = []
        for basis in moving.BASES4:
            polynomial = common.mp_determinant(
                [[target[row][label - 1] for label in basis] for row in range(4)]
            )
            sign = 1 if base_brackets[basis] > 0 else -1
            values = tuple(sign * value for value in common.mp_bernstein(polynomial))
            if min(values) < 0:
                raise AssertionError(f"H0 {name} cap parent sign failed: {basis}")
            if min(values) == 0:
                zero_labels.append("".join(map(str, basis)))
        if tuple(sorted(zero_labels)) != tuple(sorted(expected_zero)):
            raise AssertionError(f"H0 {name} cap wall census changed: {zero_labels}")

        normals = common.mp_normals(target)
        coefficients = common.mp_circuit(
            normals, joined.SIGNATURES[0], support
        )
        circuit_sign = 1 if common.mp_at_origin(coefficients[0]) > 0 else -1
        minimums = tuple(
            min(circuit_sign * value for value in common.mp_bernstein(coefficient))
            for coefficient in coefficients
        )
        if min(minimums) <= 0:
            raise AssertionError(f"H0 {name} cap circuit lost strictness")
        reports.append((name, tuple(sorted(zero_labels))))

    return tuple(reports), (bottom_gauge_rank, lower_upper_rank)


def verify_swept_frontiers_are_not_relative(matrix):
    """Give one exact parent-interior point on each of the six swept faces."""
    midpoint = Fraction(1, 2)
    h0_u = (H0_SWITCH + ROOT_ENDPOINTS[0]) / 2
    cases = (
        ("p01", ((0, ROOT_ENDPOINTS[0]),)),
        ("p12", ((1, ROOT_ENDPOINTS[1]),)),
        ("p20", ((2, ROOT_ENDPOINTS[2]),)),
        ("h0", ((0, h0_u), (2, H0_OUTER_HEIGHT))),
        ("h1", ((0, ROOT_ENDPOINTS[0] / 2), (1, ROOT_ENDPOINTS[1]))),
        ("h2", ((1, ROOT_ENDPOINTS[1] / 2), (2, ROOT_ENDPOINTS[2]))),
    )

    def determinant4(target, basis):
        columns = [
            tuple(target[row][label - 1] for row in range(4)) for label in basis
        ]
        return moving.det4(*columns)

    reports = []
    for name, root_parameters in cases:
        target = [
            [Fraction(int(matrix[row, column])) for column in range(8)]
            for row in range(4)
        ]
        for row in range(4):
            target[row][common.MOVING_COLUMN] += (
                midpoint * common.ENDPOINT * common.EXPECTED_DIRECTION[row]
            )
        for root_index, parameter in root_parameters:
            source, destination, sign = common.PAIR_ROOTS[root_index]
            amplitude = (1 - midpoint) * parameter * sign
            for row in range(4):
                target[row][source - 1] += amplitude * target[row][destination - 1]
        zeros = tuple(
            "".join(map(str, basis))
            for basis in moving.BASES4
            if determinant4(target, basis) == 0
        )
        if zeros:
            raise AssertionError(f"{name} midpoint unexpectedly remains relative: {zeros}")
        reports.append(name)
    return tuple(reports)


def main():
    actual_sha = file_sha256(SOURCE)
    if actual_sha != SOURCE_SHA256:
        raise AssertionError(f"row2599 source changed: {actual_sha}")
    with np.load(SOURCE, allow_pickle=False) as source:
        matrix = source["chart_matrix"][0]

    roots = tuple(
        escape.DIRECTIONS[escape.DIRECTION_INDEX[root]]
        for root in joined.PAIR_ROOTS
    )
    records = []
    safe_support_records = []
    h0_forward = None
    for block, order in VALID_ORDERS:
        raw = atlas.parent_polynomials(matrix, roots[order[0]], roots[order[1]])
        polynomials = tuple(signed(value) for value in raw)
        if block == 0:
            record = verify_h0_cap(polynomials, order)
            if order == (0, 2):
                h0_forward = polynomials
            else:
                swapped = tuple(
                    {(v, u): value for (u, v), value in item.items()}
                    for item in polynomials
                )
                if swapped != h0_forward:
                    raise AssertionError("H0 reverse order is not the exact coordinate swap")
        else:
            record = {
                "limits": verify_rectangle(polynomials, order)[0],
                "walls": verify_rectangle(polynomials, order)[1],
            }
        records.append((block, order, record, polynomials))
        safe_support_records.append(
            (block, order, verify_safe_tapered_witness(matrix, block, order, roots))
        )

    digest = sha256(b"diag3-row2599-ordered-sector-roadmap-v1\0")
    for block, order, record, polynomials in records:
        digest.update(repr((block, order, record)).encode("ascii"))
        for label, polynomial in zip(atlas.BRACKET_LABELS, polynomials, strict=True):
            digest.update(label.encode("ascii") + b"\0")
            digest.update(repr(tuple(sorted(polynomial.items()))).encode("ascii"))
    digest.update(repr(tuple(safe_support_records)).encode("ascii"))
    rectangle, first_square, full_cap = verify_relative_models()
    h0_cap_comparison = verify_h0_cap_comparison(matrix, roots)
    signed_table = verify_signed_cone_boundary_table()
    nonrelative_faces = verify_swept_frontiers_are_not_relative(matrix)
    witness_cospan = verify_frontier_witness_cospan(matrix)
    radial_no_go = verify_scalar_radial_filler_no_go(matrix)
    wall_collar = verify_parent_wall_collar_attempt(matrix)
    digest.update(repr(h0_cap_comparison).encode("ascii"))
    digest.update(repr(signed_table).encode("ascii"))
    digest.update(repr(nonrelative_faces).encode("ascii"))
    digest.update(repr(witness_cospan).encode("ascii"))
    digest.update(repr(radial_no_go).encode("ascii"))
    digest.update(repr(wall_collar).encode("ascii"))
    semantic = digest.hexdigest()
    if EXPECTED_ORDER_DIGEST != "TO_BE_PINNED" and semantic != EXPECTED_ORDER_DIGEST:
        raise AssertionError(f"ordered-sector semantic changed: {semantic}")
    print("PASS pinned row2599 source", actual_sha)
    print("PASS H1-forward and both H2 origin components are exact first-wall rectangles")
    print("PASS both H0 origin components are exact first-square plus bounded outer cap")
    print("PASS five ordered-safe strict tapered witnesses", tuple(safe_support_records))
    print("PASS H0 outer cap swept exactly to common ray", h0_cap_comparison)
    print("PASS signed raw-cone boundary table", signed_table)
    print("PASS six swept-frontier parent-interior canaries", nonrelative_faces)
    print("PASS exact six-seam joined-witness cospan", witness_cospan)
    print("NO-GO scalar radial common-apex filler", radial_no_go)
    print("NO-GO three-edge parent-wall collar", wall_collar)
    print("H0_SWITCH", H0_SWITCH.numerator, H0_SWITCH.denominator)
    print("H0_OUTER_HEIGHT", H0_OUTER_HEIGHT.numerator, H0_OUTER_HEIGHT.denominator)
    print("RELATIVE_BETTI rectangle/first-square/capped", rectangle, first_square, full_cap)
    print("SEMANTIC", semantic)
    print(
        "NO-GO the H0 first-wall square inclusion is not a relative-homology "
        "equivalence; its primitive H1 is killed by the exact outer cap"
    )
    print(
        "SCOPE five local ordered singleton sectors only; no comparison d3 "
        "column or global face-naturality theorem"
    )


if __name__ == "__main__":
    main()
