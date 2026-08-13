#!/usr/bin/env python3
"""Exact receiver/end plumbing canary for the diagonal-three pair complex.

This checker deliberately combines two separately scoped exact artifacts.

* The row-2599 transverse node supplies a complete four-chamber/four-wall
  local atlas.  We decorate every oriented wall germ for one three-signature
  family, choose exact receiver circuits on the four loss germs, continue
  all four factor rays to their first parent-bracket boundaries, and build
  the actual cellular blocks b_ij and the matrices N,M from (22)--(23) of
  DIAG3_PAIR_DIFFERENTIAL_ENDS.md.
* The complete parent-187 e-line supplies two genuine relative-infinity
  labels: its maximal parent-cell interval ends at the first two exact
  parent-bracket walls.

The stored boundary of the row-2599 square is only ``scope infinity`` and is
never relabeled as parent infinity.  The checker instead continues each
linear factor branch exactly beyond that boundary until a parent bracket
vanishes.  Intervening residual-factor crossings on those continuations are
not yet subdivided, so this remains an interface canary rather than a global
frontier proof.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from itertools import combinations_with_replacement, product
from math import lcm
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import BLOCK_GORDAN_MONOCHROMATIC_WALL_STARS as wall_stars  # noqa: E402
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as gradients  # noqa: E402
import DIAG9_GRAPH_exact_topes as exact_topes  # noqa: E402
import DIAG9_GRAPH_parent860_star as coordinate_star  # noqa: E402
import DIAG9_GRAPH_verify_row2599_node as node  # noqa: E402
import build_ninth_candidate_antichain as circuit_finder  # noqa: E402
import verify_diag2_canonical_robust_edges as robust  # noqa: E402
import verify_diag2_extremal_coordinate_survey as coordinate_survey  # noqa: E402
import verify_diag2_extremal_line_transition_census as full_line  # noqa: E402
import verify_diag2_extremal_safe_loss_edge as safe_loss  # noqa: E402
import verify_diag2_moving_witness_shear as moving  # noqa: E402
import verify_diag2_near_counterexample_separators as near_separators  # noqa: E402
import verify_diag3_pair_differential_ends as differential  # noqa: E402
import verify_diag3_pair_factor_root_switch as factor_roots  # noqa: E402


NODE_SHA256 = "ddec96b052b305d279b543be2af27e12f380f0dedc79ea434616c64b40cd8cea"
RECEIVER_SIGNATURES = (
    448_607_715_549_184,       # feasible mask 0011 = q0 > 0
    17_527_223_614_444,        # feasible mask 1001 = q1 > 0
    14_988_895_318_912,        # bad throughout the node disk
)
EXPECTED_RECEIVER_PATTERNS = (0b0011, 0b1001, 0)
ALL_DIE_SIGNATURES = (
    448_607_715_549_184,
    3_826_331_369_078_784,
    31_604_296_963_587_053,
)
ALL_DIE_SUPPORT = (0, 18, 40)

# wall order is the exact order stored by the node artifact:
# (q0=0,q1>0), (q0=0,q1<0), (q0<0,q1=0), (q0>0,q1=0).
WALL_ADJACENCY = ((0, 3), (1, 2), (2, 3), (0, 1))
WALL_BRANCH = (0, 0, 1, 1)
WALL_LABEL = ("0+", "0-", "-0", "+0")
EXPECTED_RECEIVER_SUPPORT = {
    0: (3, 19, 21, 37, 38),
    1: (2, 28, 32, 43),
    2: (0, 18, 29, 40, 48),
    3: (3, 19, 21, 37, 38),
}

EXPECTED_PARENT187_ENDS = {
    "negative": (
        Fraction(-6_557_186_031_778_323_968_614_336,
                 80_367_163_670_274_882_423_315_095),
        "4578",
    ),
    "positive": (
        Fraction(9_701_361_017_377_585_348_692_326,
                 281_522_797_333_298_743_311_269_675),
        "2567",
    ),
}

EXPECTED_NODE_BRANCH_ENDS = {
    0: {
        "negative": (
            Fraction(
                -3_386_331_729_708_487_859_761_591_605_293_272_179_109,
                146_113_907_578_351_369_199_466_310_207_349_541_494_335_544_458_936_320,
            ),
            (2, 4, 6, 7),
            "3578",
        ),
        "positive": (
            Fraction(
                443_717_795_991_681_806_712_634_740_259_246_573,
                738_316_398_476_524_037_564_859_486_998_585_944_906_241_305_804_800,
            ),
            (0, 2, 4, 7),
            "1358",
        ),
    },
    1: {
        "negative": (
            Fraction(
                -1_673_881_555_801_274_951_978_533_839_117_134_335_153,
                220_332_321_958_318_865_944_006_151_138_175_572_841_423_446_189_345_280,
            ),
            (2, 3, 6, 7),
            "3478",
        ),
        "positive": (
            Fraction(
                1_242_824_577_394_768_117_863_801_581_302_239_329,
                7_213_434_838_044_802_527_110_918_066_437_206_312_699_096_348_956_160,
            ),
            (0, 1, 5, 7),
            "1268",
        ),
    },
}
WALL_END = {
    0: (0, "negative"),
    1: (0, "positive"),
    2: (1, "negative"),
    3: (1, "positive"),
}

EXPECTED_ORDERED_SUPPORT_TUPLE_ORBITS = {
    36: (4, 54, 1_147),
    38: (2, 10, 83),
    48: (1, 2, 4),
    49: (1, 1, 1),
    50: (1, 1, 1),
    51: (1, 1, 1),
}
EXPECTED_GENERIC_COORIENTED_ROWS = 11_792
EXPECTED_GENERIC_DIRECTED_ROWS = 23_584
EXPECTED_SEMANTIC = "7ff91b35ac7f8902f893c89011d94254458d0b3344e6d994db85dc1c1f0021a0"


@dataclass(frozen=True)
class Matrix:
    rows: int
    columns: int
    entries: tuple[tuple[int, ...], ...]

    def __post_init__(self):
        if len(self.entries) != self.rows:
            raise AssertionError("matrix row count mismatch")
        if any(len(row) != self.columns for row in self.entries):
            raise AssertionError("matrix column count mismatch")

    def lists(self):
        return [list(row) for row in self.entries]


def zero(rows: int, columns: int) -> Matrix:
    return Matrix(rows, columns, tuple((0,) * columns for _ in range(rows)))


def from_rows(rows, columns: int | None = None) -> Matrix:
    rows = tuple(tuple(map(int, row)) for row in rows)
    if columns is None:
        columns = len(rows[0]) if rows else 0
    return Matrix(len(rows), columns, rows)


def negate(matrix: Matrix) -> Matrix:
    return Matrix(
        matrix.rows,
        matrix.columns,
        tuple(tuple(-value for value in row) for row in matrix.entries),
    )


def multiply(left: Matrix, right: Matrix) -> Matrix:
    if left.columns != right.rows:
        raise AssertionError("matrix product dimension mismatch")
    return Matrix(
        left.rows,
        right.columns,
        tuple(
            tuple(
                sum(
                    left.entries[row][middle] * right.entries[middle][column]
                    for middle in range(left.columns)
                )
                for column in range(right.columns)
            )
            for row in range(left.rows)
        ),
    )


def add(left: Matrix, right: Matrix) -> Matrix:
    if (left.rows, left.columns) != (right.rows, right.columns):
        raise AssertionError("matrix sum dimension mismatch")
    return Matrix(
        left.rows,
        left.columns,
        tuple(
            tuple(a + b for a, b in zip(lrow, rrow, strict=True))
            for lrow, rrow in zip(left.entries, right.entries, strict=True)
        ),
    )


def is_zero(matrix: Matrix) -> bool:
    return all(value == 0 for row in matrix.entries for value in row)


def assemble(row_dimensions, column_dimensions, blocks) -> Matrix:
    row_offsets = [0]
    column_offsets = [0]
    for dimension in row_dimensions:
        row_offsets.append(row_offsets[-1] + dimension)
    for dimension in column_dimensions:
        column_offsets.append(column_offsets[-1] + dimension)
    entries = [
        [0 for _ in range(column_offsets[-1])]
        for _ in range(row_offsets[-1])
    ]
    for (block_row, block_column), block in blocks.items():
        expected = (row_dimensions[block_row], column_dimensions[block_column])
        if (block.rows, block.columns) != expected:
            raise AssertionError(
                f"block {(block_row, block_column)} has "
                f"{(block.rows, block.columns)}, expected {expected}"
            )
        for row in range(block.rows):
            for column in range(block.columns):
                entries[row_offsets[block_row] + row][
                    column_offsets[block_column] + column
                ] = block.entries[row][column]
    return from_rows(entries, column_offsets[-1])


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        while block := source.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def pattern_map(certificate) -> dict[int, int]:
    return {
        int(signature): int(pattern)
        for signature, pattern in zip(
            certificate["signature"], certificate["signature_pattern"], strict=True
        )
    }


def signed_rows(matrix, signature):
    rows = exact_topes.derived_rows(matrix)
    return tuple(
        tuple(
            (1 if signature >> index & 1 else -1) * int(value)
            for value in rows[index]
        )
        for index in range(56)
    )


def exact_receiver_circuit(wall: int, signature: int):
    matrix = node.rational_parent(*node.wall_points()[wall])
    support, weights = circuit_finder.positive_circuit(
        signed_rows(matrix, signature)
    )
    if not 2 <= len(support) <= 5 or len(weights) != len(support):
        raise AssertionError("receiver finder returned a non-circuit")
    return tuple(support), tuple(map(int, weights))


def bad_set(pattern: int) -> tuple[int, ...]:
    return tuple(cell for cell in range(4) if not (pattern >> cell) & 1)


def receiver_table(certificate):
    patterns = pattern_map(certificate)
    actual = tuple(patterns.get(signature, 0) for signature in RECEIVER_SIGNATURES)
    if actual != EXPECTED_RECEIVER_PATTERNS:
        raise AssertionError(f"receiver signature patterns changed: {actual}")

    # The everywhere-bad signature is independently GP-valid, rather than a
    # fabricated zero pattern outside the node's union of feasible topes.
    center = node.rational_parent(Fraction(0), Fraction(0))
    if moving.extension_gp_violations(center, RECEIVER_SIGNATURES[2]):
        raise AssertionError("everywhere-bad receiver signature is not GP-valid")

    bad = tuple(set(bad_set(pattern)) for pattern in actual)
    rows = []
    loss_supports = {}
    for wall, adjacent in enumerate(WALL_ADJACENCY):
        for source, target in (adjacent, tuple(reversed(adjacent))):
            source_bad = tuple(block for block in range(3) if source in bad[block])
            target_bad = tuple(block for block in range(3) if target in bad[block])
            dying = tuple(block for block in source_bad if block not in target_bad)
            born = tuple(block for block in target_bad if block not in source_bad)
            receiver = min(target_bad) if dying and target_bad else None
            support = None
            if receiver is not None:
                support, _weights = exact_receiver_circuit(
                    wall, RECEIVER_SIGNATURES[receiver]
                )
                loss_supports[wall] = support
            action = (
                "receiver-transfer" if receiver is not None
                else "all-die" if dying
                else "birth/identity"
            )
            rows.append(
                (
                    wall,
                    WALL_BRANCH[wall],
                    source,
                    target,
                    source_bad,
                    target_bad,
                    dying,
                    born,
                    receiver,
                    support,
                    action,
                    "factor-intersection:node",
                    "scope-infinity:square-boundary",
                    False,  # this square boundary is not parent infinity
                )
            )
    if loss_supports != EXPECTED_RECEIVER_SUPPORT:
        raise AssertionError(f"receiver supports changed: {loss_supports}")
    return tuple(rows), actual


def branch_parent(branch: int, parameter: Fraction):
    matrix = [
        [Fraction(int(value)) for value in row]
        for row in node.slice_verify.source_parent()
    ]
    linear = node.CENTERED_BRANCHES[branch]
    coefficient_s = Fraction(linear[(1, 0)])
    coefficient_u = Fraction(linear[(0, 1)])
    matrix[node.disk.FIRST_POSITION[0]][node.disk.FIRST_POSITION[1]] += (
        node.CENTER_S + parameter * coefficient_u
    )
    matrix[node.disk.SECOND_POSITION[0]][node.disk.SECOND_POSITION[1]] += (
        node.CENTER_U - parameter * coefficient_s
    )
    return matrix


def integer_parent(matrix):
    denominator = 1
    for row in matrix:
        for value in row:
            denominator = lcm(denominator, value.denominator)
    return np.asarray(
        tuple(
            tuple(
                value.numerator * (denominator // value.denominator)
                for value in row
            )
            for row in matrix
        ),
        dtype=object,
    )


def bracket_value(matrix, basis):
    columns = tuple(
        tuple(matrix[row][column] for row in range(4))
        for column in basis
    )
    return moving.det4(*columns)


def node_branch_end_labels():
    result = {}
    for branch in (0, 1):
        center = branch_parent(branch, Fraction(0))
        unit = branch_parent(branch, Fraction(1))
        roots = []
        for basis in exact_topes.BASES:
            constant = bracket_value(center, basis)
            slope = bracket_value(unit, basis) - constant
            if not constant:
                raise AssertionError("node parent is nonuniform")
            if slope:
                roots.append((-constant / slope, basis))
        negative = max(
            (item for item in roots if item[0] < 0), key=lambda item: item[0]
        )
        positive = min(
            (item for item in roots if item[0] > 0), key=lambda item: item[0]
        )
        result[branch] = {
            "negative": (
                negative[0],
                negative[1],
                "".join(str(label + 1) for label in negative[1]),
            ),
            "positive": (
                positive[0],
                positive[1],
                "".join(str(label + 1) for label in positive[1]),
            ),
        }
    if result != EXPECTED_NODE_BRANCH_ENDS:
        raise AssertionError(f"node branch infinity labels changed: {result}")

    # On branch zero the three all-die wall circuits remain positive all the
    # way toward both parent-boundary ends.  Dependence is the branch factor
    # equation; positivity cannot change before a bracket coefficient does.
    for side in ("negative", "positive"):
        endpoint = result[0][side][0]
        sample = integer_parent(branch_parent(0, endpoint / 2))
        normals = exact_topes.derived_rows(sample, normalize=False)
        if not all(
            wall_stars.positive_circuit(normals, signature, ALL_DIE_SUPPORT)
            for signature in ALL_DIE_SIGNATURES
        ):
            raise AssertionError("all-die circuit failed along its factor ray")
    return result


def all_die_table(certificate, branch_ends):
    patterns = pattern_map(certificate)
    if tuple(patterns.get(signature, 0) for signature in ALL_DIE_SIGNATURES) != (
        3, 3, 3
    ):
        raise AssertionError("all-die signature masks changed")
    rows = []
    normals_by_wall = tuple(
        exact_topes.derived_rows(node.rational_parent(*point), normalize=False)
        for point in node.wall_points()[:2]
    )
    for wall, (source, target) in ((0, (3, 0)), (1, (2, 1))):
        normals = normals_by_wall[wall]
        if not all(
            wall_stars.positive_circuit(normals, signature, ALL_DIE_SUPPORT)
            for signature in ALL_DIE_SIGNATURES
        ):
            raise AssertionError("common branch-zero wall circuit lost positivity")
        branch, side = WALL_END[wall]
        endpoint, _basis, bracket = branch_ends[branch][side]
        rows.append(
            (
                wall,
                source,
                target,
                (0, 1, 2),
                (),
                ALL_DIE_SUPPORT,
                "global-factor-wall-escape",
                f"relative-infinity:parent-bracket-{bracket}",
                endpoint,
            )
        )
    return tuple(rows)


# Relative cellular model of the square cut by two transverse lines.  Every
# ray is oriented from the node to the square boundary.  Chamber orientations
# are induced by the q0,q1 plane orientation.  Boundary-only faces are in the
# relative scope-infinity subcomplex and hence omitted below.
CELLS = {
    0: ("v",),
    1: ("w0", "w1", "w2", "w3"),
    2: ("c0", "c1", "c2", "c3"),
}
BOUNDARY = {
    "w0": {"v": -1},
    "w1": {"v": -1},
    "w2": {"v": -1},
    "w3": {"v": -1},
    "c0": {"w3": +1, "w0": -1},
    "c1": {"w1": +1, "w3": -1},
    "c2": {"w2": +1, "w1": -1},
    "c3": {"w0": +1, "w2": -1},
}


def bad_cells(certificate, signature: int):
    cell_topes = tuple(set(map(int, row)) for row in certificate["cell_tope"])
    wall_topes = tuple(set(map(int, row)) for row in certificate["wall_tope"])
    node_topes = set(map(int, certificate["node_tope"]))
    return {
        0: tuple(("v",)) if signature not in node_topes else (),
        1: tuple(f"w{wall}" for wall in range(4) if signature not in wall_topes[wall]),
        2: tuple(f"c{cell}" for cell in range(4) if signature not in cell_topes[cell]),
    }


def intersect_cells(*families):
    return {
        dimension: tuple(
            cell for cell in CELLS[dimension]
            if all(cell in family[dimension] for family in families)
        )
        for dimension in range(3)
    }


def difference_cells(left, right):
    return {
        dimension: tuple(
            cell for cell in left[dimension] if cell not in right[dimension]
        )
        for dimension in range(3)
    }


def check_relative_subcomplex(cells):
    for dimension in (1, 2):
        for high in cells[dimension]:
            for low in BOUNDARY[high]:
                if low not in cells[dimension - 1]:
                    raise AssertionError(f"{high} has missing interior face {low}")


def cochain_matrix(low_cells, high_cells) -> Matrix:
    return from_rows(
        tuple(
            tuple(BOUNDARY[high].get(low, 0) for low in low_cells)
            for high in high_cells
        ),
        len(low_cells),
    )


def pair_blocks(pair_cells, triple_cells):
    exclusive = difference_cells(pair_cells, triple_cells)
    d_e0 = cochain_matrix(exclusive[0], exclusive[1])
    d_e1 = cochain_matrix(exclusive[1], exclusive[2])
    b0 = cochain_matrix(triple_cells[0], exclusive[1])
    b1 = cochain_matrix(triple_cells[1], exclusive[2])
    if not is_zero(multiply(d_e1, d_e0)):
        raise AssertionError("exclusive-pair differential does not square to zero")
    return d_e0, d_e1, b0, b1, exclusive


def assemble_nm(certificate):
    block_bad = tuple(bad_cells(certificate, signature) for signature in RECEIVER_SIGNATURES)
    for cells in block_bad:
        check_relative_subcomplex(cells)
    triple_cells = intersect_cells(*block_bad)
    pair_cells = (
        intersect_cells(block_bad[0], block_bad[1]),
        intersect_cells(block_bad[0], block_bad[2]),
        intersect_cells(block_bad[1], block_bad[2]),
    )
    check_relative_subcomplex(triple_cells)
    for cells in pair_cells:
        check_relative_subcomplex(cells)

    d_t0 = cochain_matrix(triple_cells[0], triple_cells[1])
    d_t1 = cochain_matrix(triple_cells[1], triple_cells[2])
    if not is_zero(multiply(d_t1, d_t0)):
        raise AssertionError("triple differential does not square to zero")

    pairs = tuple(pair_blocks(cells, triple_cells) for cells in pair_cells)
    for d_e0, d_e1, b0, b1, _exclusive in pairs:
        if not is_zero(add(multiply(d_e1, b0), multiply(b1, d_t0))):
            raise AssertionError("frontier identity d_E b+b d_T failed")

    t0, t1, t2 = map(lambda degree: len(triple_cells[degree]), range(3))
    e0 = [block[0].columns for block in pairs]
    e1 = [block[0].rows for block in pairs]
    e2 = [block[1].rows for block in pairs]
    c0_dimensions = [t0, t0] + e0
    c1_dimensions = [t1, t1] + e1
    c2_dimensions = [t2, t2] + e2

    (d01_0, d01_1, b01_0, b01_1, _), \
    (d02_0, d02_1, b02_0, b02_1, _), \
    (d12_0, d12_1, b12_0, b12_1, _) = pairs
    n_matrix = assemble(
        c1_dimensions,
        c0_dimensions,
        {
            (0, 0): d_t0,
            (1, 1): d_t0,
            (2, 0): negate(b01_0),
            (2, 2): d01_0,
            (3, 0): negate(b02_0),
            (3, 1): negate(b02_0),
            (3, 3): d02_0,
            (4, 1): negate(b12_0),
            (4, 4): d12_0,
        },
    )
    m_matrix = assemble(
        c2_dimensions,
        c1_dimensions,
        {
            (0, 0): d_t1,
            (1, 1): d_t1,
            (2, 0): b01_1,
            (2, 2): negate(d01_1),
            (3, 0): b02_1,
            (3, 1): b02_1,
            (3, 3): negate(d02_1),
            (4, 1): b12_1,
            (4, 4): negate(d12_1),
        },
    )
    if not is_zero(multiply(m_matrix, n_matrix)):
        raise AssertionError("assembled matrices do not satisfy MN=0")
    if (n_matrix.rows, n_matrix.columns) != (6, 2):
        raise AssertionError("unexpected N dimensions")
    if (m_matrix.rows, m_matrix.columns) != (4, 6):
        raise AssertionError("unexpected M dimensions")
    if differential.rank_q(n_matrix.lists()) != 2 or differential.rank_q(m_matrix.lists()) != 4:
        raise AssertionError("unexpected N/M ranks")
    if n_matrix.rows - differential.rank_q(n_matrix.lists()) - differential.rank_q(m_matrix.lists()):
        raise AssertionError("node receiver canary has nonzero middle cohomology")
    n_units, bar_units = differential.split_exact_replay(
        n_matrix.lists(), m_matrix.lists()
    )
    if (n_units, bar_units) != (2, 4):
        raise AssertionError("node receiver canary lost its unit contraction")
    return (
        n_matrix,
        m_matrix,
        triple_cells,
        tuple(block[4] for block in pairs),
        (n_units, bar_units),
    )


def parent187_end_labels():
    _atlas, by_index, active = near_separators.load_atlas()
    base, _pairs = full_line.mapped_pairs(by_index, active)
    _residual, brackets = gradients.polynomial_data()
    lower, upper = coordinate_survey.boundary_interval(
        base, full_line.VARIABLE, brackets
    )
    labels = {}
    for name, polynomial in brackets.items():
        restriction = coordinate_star.restrict_polynomial(
            polynomial, full_line.VARIABLE, base
        )
        if len(restriction) != 2:
            continue
        root = -restriction[0] / restriction[1]
        if root == lower:
            labels["negative"] = (root, name)
        if root == upper:
            labels["positive"] = (root, name)
    if labels != EXPECTED_PARENT187_ENDS:
        raise AssertionError(f"parent-187 infinity labels changed: {labels}")
    if (full_line.EXPECTED_ROOTS, full_line.EXPECTED_CELLS) != (1_721, 1_722):
        raise AssertionError("parent-187 full-line atlas counts changed")
    return labels


def transform_support(support, mapping):
    return tuple(sorted(mapping[index] for index in support))


def ordered_support_tuple_orbits():
    occurrences, occurrence_factor, factor_polynomials = labeled.factor_polynomials()
    factor_representatives, stabilizers, _alignment, _factor_occurrence, _sizes = (
        labeled.factor_orbit_data(occurrences, occurrence_factor)
    )
    factor_ids, canonical_polynomials = robust.canonical_data()
    if factor_polynomials != canonical_polynomials:
        raise AssertionError("factor polynomial order changed")
    counts = {}
    for kind in (36, 38, 48):
        if factor_ids[kind] != factor_representatives[kind]:
            raise AssertionError("factor representative changed")
        witness = robust.construct_witness(kind, factor_ids, factor_polynomials)
        normals = exact_topes.derived_rows(
            robust.integer_matrix(witness.center), normalize=False
        )
        members = tuple(
            occurrence
            for occurrence in occurrences
            if occurrence_factor[occurrence] == factor_ids[kind]
        )
        supports = tuple(
            sorted(
                {
                    wall_stars.node_wall_circuit(occurrence, normals)
                    for occurrence in members
                }
            )
        )
        row = []
        for arity in (1, 2, 3):
            universe = set(product(supports, repeat=arity))
            seen = set()
            number = 0
            for key in sorted(universe):
                if key in seen:
                    continue
                orbit = {
                    tuple(transform_support(support, mapping) for support in key)
                    for mapping in stabilizers[kind]
                }
                if not orbit.issubset(universe):
                    raise AssertionError("factor stabilizer left the support universe")
                seen.update(orbit)
                number += 1
            if seen != universe:
                raise AssertionError("support-tuple orbit coverage failed")
            row.append(number)
        counts[kind] = tuple(row)
    for kind in (49, 50, 51):
        counts[kind] = (1, 1, 1)
    if counts != EXPECTED_ORDERED_SUPPORT_TUPLE_ORBITS:
        raise AssertionError(f"ordered support-tuple orbit counts changed: {counts}")

    totals = tuple(sum(counts[kind][arity] for kind in counts) for arity in range(3))
    if totals != (10, 69, 1_237):
        raise AssertionError("wrong aggregate support-tuple orbit counts")

    # Each block status on a fixed cooriented wall is one of
    # inactive/persistent/dying/born.  Only dying or born blocks require a
    # selected occurrence of the crossed factor.  For k changing labeled
    # blocks there are C(3,k)*2^k*2^(3-k)=8*C(3,k) status words.
    cooriented = 24 * totals[0] + 24 * totals[1] + 8 * totals[2]
    directed = 2 * cooriented
    if (cooriented, directed) != (
        EXPECTED_GENERIC_COORIENTED_ROWS,
        EXPECTED_GENERIC_DIRECTED_ROWS,
    ):
        raise AssertionError("generic receiver-row estimate changed")
    return counts, totals, cooriented, directed


def semantic_digest(*objects) -> str:
    digest = sha256()
    digest.update(b"diag3-pair-receiver-end-canary-v1\0")
    for item in objects:
        digest.update(repr(item).encode("ascii") + b"\0")
    return digest.hexdigest()


def main():
    if file_sha256(node.ROADMAP) != NODE_SHA256:
        raise AssertionError("row-2599 node roadmap hash changed")
    branch_ends = node_branch_end_labels()
    with np.load(node.ROADMAP, allow_pickle=False) as certificate:
        table, patterns = receiver_table(certificate)
        all_die = all_die_table(certificate, branch_ends)
        n_matrix, m_matrix, triple_cells, exclusive_cells, unit_ranks = assemble_nm(
            certificate
        )
    ends = parent187_end_labels()
    orbit_counts, orbit_totals, cooriented, directed = ordered_support_tuple_orbits()
    digest = semantic_digest(
        table,
        patterns,
        all_die,
        n_matrix.entries,
        m_matrix.entries,
        triple_cells,
        exclusive_cells,
        tuple(
            (branch, side, *branch_ends[branch][side])
            for branch in sorted(branch_ends)
            for side in ("negative", "positive")
        ),
        tuple(sorted(ends.items())),
        tuple(sorted(orbit_counts.items())),
        orbit_totals,
        cooriented,
        directed,
    )
    if EXPECTED_SEMANTIC and digest != EXPECTED_SEMANTIC:
        raise AssertionError(f"receiver/end semantic digest changed: {digest}")

    print("PASS node receiver signatures/patterns", RECEIVER_SIGNATURES, patterns)
    for row in table:
        if row[10] == "receiver-transfer":
            print(
                "RECEIVER",
                f"w{row[0]}:{WALL_LABEL[row[0]]}",
                f"c{row[2]}->c{row[3]}",
                "dying", row[6],
                "receiver", row[8],
                "support", row[9],
            )
    for row in all_die:
        print(
            "ALL_DIE",
            f"w{row[0]}:{WALL_LABEL[row[0]]}",
            f"c{row[1]}->c{row[2]}",
            "support", row[5],
            "end", row[7],
        )
    print(
        "PASS node factor rays continue from scope boundary to parent-relative infinity",
        tuple(
            (f"w{wall}", branch_ends[branch][side][2])
            for wall, (branch, side) in sorted(WALL_END.items())
        ),
    )
    print(
        "PASS exact node N/M shapes/ranks/units",
        (n_matrix.rows, n_matrix.columns),
        (m_matrix.rows, m_matrix.columns),
        unit_ranks,
    )
    print(
        "PASS parent-187 genuine relative-infinity labels",
        tuple((side, str(value), bracket) for side, (value, bracket) in ends.items()),
    )
    print("PASS ordered changed-occurrence tuple orbits", orbit_totals)
    print("GENERIC receiver rows cooriented/directed", cooriented, directed)
    print("SEMANTIC", digest)
    print("SCOPE node receiver/NM canary, four exact factor-ray ends, and separate parent-187 end labels")
    print("GAP intervening factor intersections on the four continued rays are not yet chamber-decorated")


if __name__ == "__main__":
    main()
