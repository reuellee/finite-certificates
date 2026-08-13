#!/usr/bin/env python3
"""Exact proper tangential filler for the scoped diagonal-three ribbon.

This verifier does not claim a global pair atlas.  It proves that the unique
``E02`` class in ``verify_diag3_pair_tapered_ribbon.py`` is killed by one
genuine proper ambient column-shear strip attached along the complete
negative ``q0`` end.

There are two independent parts.

* Reconstruct every primitive-factor segment on the end.  On every segment,
  find exact positive Gordan circuits for blocks 0 and 2 and check that the
  same oriented shear ``8 -> 3, +`` transports both.  The complete factor
  subdivision and an occurrence check exclude a block-1 bad point isolated
  at a factor root.
* Replay ``verify_diag3_pair_tangential_frontier.py``.  Its complete
  bivariate active-factor scan proves that the parent residence component is
  a quadrilateral, block 1 is feasible in its interior, its left side is
  triple-relative, and its other two terminal sides are parent walls.
* Attach that proper relative product strip to the signed tapered-ribbon complex.
  After the vertical-edge unit pivots reduce ``N``, the reduced ``bar M`` is
  ``[d_E02^1; Q]``, where ``Q`` selects the 2,614 edges of the full ``q0``
  end.  Exact signed leaf elimination gives a 7,342 by 7,342 unit minor, so
  the combined middle complex is split exact over the integers.

The fixed shear is transverse to the whole stored normal plane.  The generic
first-exit warning in ``verify_diag3_tangential_first_exit_no_go.py`` remains
valid: pointwise intervals need not assemble properly.  The bivariate
frontier replay is the additional row-specific certificate which excludes
that failure here.
"""

from __future__ import annotations

from collections import Counter, deque
from fractions import Fraction
from hashlib import sha256
from pathlib import Path
import sys

import numpy as np
from scipy.sparse import csr_matrix, eye, hstack, vstack


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG9_GRAPH_exact_topes as exact_topes  # noqa: E402
import verify_diag2_moving_witness_shear as moving  # noqa: E402
import verify_diag3_pair_four_ray_refinement as refinement  # noqa: E402
import verify_diag3_pair_receiver_end_canary as receiver  # noqa: E402
import verify_diag3_pair_tangential_frontier as frontier  # noqa: E402
import verify_diag3_pair_tapered_ribbon as ribbon  # noqa: E402


PAIR_BLOCKS = (0, 2)
FIXED_ROOT = (8, 3, 1)
EXPECTED_COMMON_ROOTS = {
    (3, 2, -1),
    (6, 2, 1),
    (6, 4, -1),
    (6, 7, -1),
    (8, 3, 1),
}
EXPECTED_TRANSVERSE_DETERMINANT = -63_617
EXPECTED_SUPPORT_PAIRS = 50
EXPECTED_Q0_SEGMENTS = 2_614
EXPECTED_SURVIVOR_CUT_EDGES = 242
EXPECTED_COMBINED_SHAPES = ((9_955, 2_613), (7_342, 9_955))

# Filled after the complete exact support/root replay.  It pins the branch,
# segment, two circuit supports, and full compatible-root set at every row.
EXPECTED_SUPPORT_DIGEST = (
    "ea98122717e86efcfb875bea0662fafef7d3eb1e58119fe840afbf9d4389d900"
)


def update_digest(digest, value):
    if isinstance(value, (tuple, list)):
        digest.update(b"[")
        for item in value:
            update_digest(digest, item)
        digest.update(b"]")
    elif isinstance(value, str):
        digest.update(b"S" + value.encode("ascii") + b"\0")
    elif isinstance(value, bool):
        digest.update(b"T" if value else b"F")
    elif isinstance(value, (int, np.integer)):
        digest.update(b"I" + str(int(value)).encode("ascii") + b"\0")
    else:
        raise TypeError(type(value))


def exact_positive_supports(normals, blocks):
    supports = []
    statuses = []
    for block in blocks:
        bad, certificate = refinement.classify(
            normals, receiver.RECEIVER_SIGNATURES[block]
        )
        statuses.append(bad)
        if not bad or certificate[0] != "circuit":
            raise AssertionError(
                f"block {block} lacks an exact positive circuit: {certificate[0]}"
            )
        supports.append(tuple(certificate[1][0]))
    return tuple(statuses), tuple(supports)


def q0_wall_only_audit(atlas, foursets, factor_occurrences):
    """Exclude a block-1 bad point supported only at an interior q0 root."""

    raw_normals = refinement.normal_polynomials(0)
    normals = tuple(
        refinement.integral_scaled_normal(normal, atlas["endpoint"])
        for normal in raw_normals
    )
    tested = 0
    isolated = []
    signature = receiver.RECEIVER_SIGNATURES[1]
    for root_index, (lower, upper, factors, _divisor) in enumerate(atlas["roots"]):
        for factor in factors:
            for occurrence_index in factor_occurrences[factor]:
                occurrence = foursets[occurrence_index]
                support, _kind = refinement.occurrence_circuit(occurrence)
                signs, _columns = refinement.relation_signs(
                    normals, support, lower, upper
                )
                tested += 1
                if refinement.circuit_positive(support, signs, signature):
                    isolated.append((root_index, factor, occurrence, support))
    if isolated:
        raise AssertionError(f"block 1 is bad only at q0 wall roots: {isolated[:5]}")
    if tested != 7_811:
        raise AssertionError(f"q0 wall occurrence count changed: {tested}")
    return tested


def support_root_atlas():
    foursets, factor_occurrences, offsets, units, labels = refinement.factor_data()
    ends = receiver.node_branch_end_labels()
    atlases = refinement.ray_factor_atlases(
        foursets, factor_occurrences, offsets, units, labels, ends
    )

    signatures = tuple(receiver.RECEIVER_SIGNATURES[block] for block in PAIR_BLOCKS)
    rows = []
    all_common = None
    q0_rows = 0
    cut_rows = 0
    support_pairs = set()

    # The full q0 end supplies the actual tangential half-strip.  The first
    # 241 q1 segments, together with the initial q0 segment, are the exact
    # supports met by the stored 242-edge cocycle and give an independent
    # seam check for the same root.
    tasks = (((0, "negative"), None), ((1, "negative"), 241))
    for key, limit in tasks:
        atlas = atlases[key]
        samples = refinement.segment_samples(atlas["roots"])
        if limit is not None:
            samples = samples[:limit]
        for segment, sample in enumerate(samples):
            parent = receiver.integer_parent(
                receiver.branch_parent(key[0], atlas["endpoint"] * sample)
            )
            normals = exact_topes.derived_rows(parent, normalize=False)

            if key == (0, "negative"):
                pair_statuses, supports = exact_positive_supports(
                    normals, PAIR_BLOCKS
                )
                middle_bad, middle_certificate = refinement.classify(
                    normals, receiver.RECEIVER_SIGNATURES[1]
                )
                if middle_bad or middle_certificate[0] != "witness":
                    raise AssertionError(
                        f"q0 segment {segment} lost its exact block-1 witness"
                    )
                statuses = (pair_statuses[0], middle_bad, pair_statuses[1])
                if statuses != (True, False, True):
                    raise AssertionError(
                        f"q0 segment {segment} status changed: {statuses}"
                    )
                q0_rows += 1
            else:
                statuses, supports = exact_positive_supports(normals, PAIR_BLOCKS)
                if statuses != (True, True):
                    raise AssertionError(
                        f"survivor seam segment {segment} lost blocks 0/2"
                    )
                cut_rows += 1

            compatible = tuple(
                (source, target, parameter_sign)
                for source, target, parameter_sign, _source_count
                in moving.compatible_shears(signatures, supports)
            )
            if FIXED_ROOT not in compatible:
                raise AssertionError(
                    f"fixed root fails on {key} segment {segment}: {supports}"
                )
            support_pairs.add(supports)
            common = set(compatible)
            all_common = common if all_common is None else all_common & common
            rows.append((key[0], key[1], segment, supports, compatible))

    if q0_rows != EXPECTED_Q0_SEGMENTS or cut_rows + 1 != EXPECTED_SURVIVOR_CUT_EDGES:
        raise AssertionError(
            f"wrong q0/cut row counts: {(q0_rows, cut_rows + 1)}"
        )
    if len(support_pairs) != EXPECTED_SUPPORT_PAIRS:
        raise AssertionError(f"support-pair count changed: {len(support_pairs)}")
    if all_common != EXPECTED_COMMON_ROOTS:
        raise AssertionError(f"global common roots changed: {sorted(all_common)}")

    wall_tests = q0_wall_only_audit(
        atlases[(0, "negative")], foursets, factor_occurrences
    )

    # Exact endpoint tags.  The center is in T; the other end is the first
    # parent wall 3578.  Classifying the nonuniform endpoint is used only to
    # pin the limiting bad/feasible statuses, not to put it back in X.
    center = receiver.integer_parent(receiver.branch_parent(0, Fraction(0)))
    center_normals = exact_topes.derived_rows(center, normalize=False)
    center_status = tuple(
        refinement.classify(center_normals, signature)[0]
        for signature in receiver.RECEIVER_SIGNATURES
    )
    endpoint = atlases[(0, "negative")]["endpoint"]
    endpoint_parent = receiver.integer_parent(receiver.branch_parent(0, endpoint))
    endpoint_normals = exact_topes.derived_rows(endpoint_parent, normalize=False)
    endpoint_status = tuple(
        refinement.classify(endpoint_normals, signature)[0]
        for signature in receiver.RECEIVER_SIGNATURES
    )
    if center_status != (True, True, True):
        raise AssertionError(f"node is no longer triple-relative: {center_status}")
    if (
        atlases[(0, "negative")]["endpoint_label"],
        endpoint_status,
    ) != ("3578", (True, False, True)):
        raise AssertionError(
            "q0 endpoint lost its parent-infinity label/status: "
            f"{atlases[(0, 'negative')]['endpoint_label']}/{endpoint_status}"
        )

    digest = sha256()
    digest.update(b"diag3-pair-atlas-tangential-fill-supports-v1\0")
    update_digest(digest, rows)
    semantic = digest.hexdigest()
    if EXPECTED_SUPPORT_DIGEST is not None and semantic != EXPECTED_SUPPORT_DIGEST:
        raise AssertionError(f"support/root digest changed: {semantic}")
    return semantic, wall_tests, len(support_pairs), tuple(sorted(all_common))


def transversality_audit():
    matrix = np.asarray(receiver.node.slice_verify.source_parent(), dtype=object)
    source_column = tuple(map(int, matrix[:, 7]))
    target_column = tuple(map(int, matrix[:, 2]))
    first = [0, 0, 0, 0]
    second = [0, 0, 0, 0]
    first[receiver.node.disk.FIRST_POSITION[0]] = 1
    second[receiver.node.disk.SECOND_POSITION[0]] = 1
    determinant = moving.det4(
        source_column, tuple(first), tuple(second), target_column
    )
    if determinant != EXPECTED_TRANSVERSE_DETERMINANT:
        raise AssertionError(f"tangential determinant changed: {determinant}")
    return determinant


def unit_leaf_elimination(d_e1, q0_columns):
    """Prove det([d_E02^1;Q])=+/-1 by signed row expansion."""

    row_entries = []
    for row in range(d_e1.shape[0]):
        begin, end = d_e1.indptr[row : row + 2]
        row_entries.append(
            {
                int(column): int(value)
                for column, value in zip(
                    d_e1.indices[begin:end], d_e1.data[begin:end]
                )
                if value
            }
        )
    row_entries.extend({column: 1} for column in q0_columns)
    if len(row_entries) != d_e1.shape[1]:
        raise AssertionError("reduced bar-M is not square")

    column_rows = [set() for _ in range(d_e1.shape[1])]
    for row, entries in enumerate(row_entries):
        for column in entries:
            column_rows[column].add(row)
    active_rows = set(range(len(row_entries)))
    active_columns = set(range(d_e1.shape[1]))
    queue = deque(row for row, entries in enumerate(row_entries) if len(entries) == 1)
    pivots = []
    while queue:
        row = queue.popleft()
        if row not in active_rows:
            continue
        columns = set(row_entries[row]) & active_columns
        if len(columns) != 1:
            continue
        column = next(iter(columns))
        value = row_entries[row][column]
        if abs(value) != 1:
            raise AssertionError(f"nonunit leaf pivot: {value}")
        pivots.append((row, column, value))
        active_rows.remove(row)
        active_columns.remove(column)
        for neighbor in column_rows[column]:
            if neighbor in active_rows and len(
                set(row_entries[neighbor]) & active_columns
            ) == 1:
                queue.append(neighbor)

    if active_rows or active_columns:
        histogram = Counter(
            len(set(row_entries[row]) & active_columns) for row in active_rows
        )
        raise AssertionError(
            f"unit leaf elimination stopped early: "
            f"{len(active_rows)}/{len(active_columns)} {histogram}"
        )
    return len(pivots)


def combined_unit_complex():
    cells, statuses, differences = ribbon.build()
    _n_ribbon, _m_ribbon, blocks = ribbon.matrices(cells, statuses, differences)
    e02_cells, d_e0, d_e1 = blocks["E"][(0, 2)]
    _vertices, edges, _faces = cells
    edge_position = {edge: index for index, edge in enumerate(e02_cells[1])}
    q0_columns = []
    for global_index, name in enumerate(edges):
        if name[0] == "q" and name[1] == (0, "negative"):
            if global_index not in edge_position:
                raise AssertionError(f"q0 end edge is absent from E02: {name}")
            q0_columns.append(edge_position[global_index])
    if len(q0_columns) != EXPECTED_Q0_SEGMENTS:
        raise AssertionError(f"q0 end edge count changed: {len(q0_columns)}")

    # The pinned E02 cocycle meets the full q0 end only on its first segment,
    # with unit coefficient.  All other 241 support edges are transverse
    # factor half-edges on the q1 side.
    survivor_q0 = [
        name
        for name in edges
        if name == ("q", (0, "negative"), 0)
    ]
    if survivor_q0 != [("q", (0, "negative"), 0)]:
        raise AssertionError("the survivor lost its unit q0 intersection")

    vertices = d_e0.shape[1]
    vertical = -eye(vertices, dtype=np.int64, format="csr")
    n_combined = vstack((d_e0, vertical), format="csr")

    q_rows = np.arange(len(q0_columns), dtype=np.int64)
    q_selector = csr_matrix(
        (
            np.ones(len(q0_columns), dtype=np.int64),
            (q_rows, np.asarray(q0_columns, dtype=np.int64)),
        ),
        shape=(len(q0_columns), d_e0.shape[0]),
        dtype=np.int64,
    )
    strip_vertical = q_selector @ d_e0
    m_combined = vstack(
        (
            hstack(
                (d_e1, csr_matrix((d_e1.shape[0], vertices), dtype=np.int64)),
                format="csr",
            ),
            hstack((q_selector, strip_vertical), format="csr"),
        ),
        format="csr",
    )
    product = m_combined @ n_combined
    product.eliminate_zeros()
    if product.nnz:
        raise AssertionError(f"combined strip complex has MN != 0: {product.nnz}")
    if (n_combined.shape, m_combined.shape) != EXPECTED_COMBINED_SHAPES:
        raise AssertionError(
            f"combined complex shapes changed: {n_combined.shape}/{m_combined.shape}"
        )

    # The vertical -I block is a unit minor of N.  Clearing the original-edge
    # entries by these pivots identifies C1/im(N) with the original E02 edge
    # basis.  In that basis bar-M is exactly [d_E02^1; Q].
    bar_units = unit_leaf_elimination(d_e1, q0_columns)
    if bar_units != d_e0.shape[0]:
        raise AssertionError(f"bar-M unit rank changed: {bar_units}")

    rank_n = ribbon.rank2(n_combined)
    rank_m = ribbon.rank2(m_combined)
    middle = n_combined.shape[0] - rank_n - rank_m
    if (rank_n, rank_m, middle) != (2_613, 7_342, 0):
        raise AssertionError(
            f"combined F2/Q middle ranks changed: {(rank_n, rank_m, middle)}"
        )
    return n_combined.shape, m_combined.shape, rank_n, rank_m, bar_units


def main():
    frontier_result = frontier.audit(verbose=False)
    semantic, wall_tests, supports, roots = support_root_atlas()
    determinant = transversality_audit()
    n_shape, m_shape, rank_n, rank_m, bar_units = combined_unit_complex()

    print("PASS exact q0 support/root atlas pairs", supports)
    print("PASS common oriented roots", roots)
    print("PASS q0 feasible-wall isolated-circuit audit", wall_tests)
    print("PASS transverse root 8->3,+ determinant", determinant)
    print("PASS relative endpoint tags node=T / parent=3578")
    print("COMBINED N/M", n_shape, m_shape, "ranks", rank_n, rank_m)
    print("PASS unit ranks N/barM", rank_n, bar_units)
    print(
        "PASS complete 2D frontier: proper quadrilateral, active factors",
        frontier_result["active_factors"],
    )
    print("FRONTIER SEMANTIC SHA256", frontier_result["semantic"])
    print("PASS coefficient-universal E02 middle contraction")
    print("SUPPORT SEMANTIC SHA256", semantic)
    print("THEOREM genuine proper row-2599 E02 tangential filler")
    print("SCOPE one exact ribbon end; no global pair atlas or diagonal-three claim")


if __name__ == "__main__":
    main()
