#!/usr/bin/env python3
"""Coverage-accounted seed schema for the diagonal-three pair-end atlas.

This verifier starts from the one pinned minimum-overlap bad-signature pair
at each of the 178 exact row-2599 charts.  It materializes three finite local
cell layers:

* selected pair point germs;
* common elementary-root ray germs with exact parent terminals; and
* ordered two-root sector germs with their complete parent-bracket
  bivariate polynomials.

It also builds the universal fixed-parent-unit wall-circuit classifier for
all 84,840 labeled residual occurrences, attaches the exact 97,224 receiver
assignment cover, and replays the conditional local signed integral and
mod-two incidence ranks.  A deterministic spanning forest gives the smallest
local choice complex and an explicit unit-pivot transcript.

Every coverage deficit is counted explicitly.  In particular, the 178
matrices are point germs, not a chamber atlas; no chart adjacency, sector
CAD, receiver-factor frontier, simultaneous-factor incidence, or global
relative boundary matrix is inferred from the point bank.  Therefore this
is a replayable atlas *schema*, not a proof of pair H_c^1 vanishing.
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
import json
from math import comb
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG9_GRAPH_exact_topes as exact_topes  # noqa: E402
import DIAG9_GRAPH_global_factor_census as global_factors  # noqa: E402
import DIAG9_GRAPH_row2599_factor_states as factor_states  # noqa: E402
import four_chart_gate as gate  # noqa: E402
import prototype_koszul_circuits as koszul  # noqa: E402
import verify_diag2_escape_set_topes as escape  # noqa: E402
import verify_diag2_moving_witness_shear as moving  # noqa: E402
import verify_diag3_ordered_root_atlas178 as ordered  # noqa: E402
import verify_diag3_pair_four_ray_refinement as refinement  # noqa: E402
import verify_diag3_pair_tangential_frontier as frontier  # noqa: E402
import verify_seeat_upper_bound as upper  # noqa: E402


FORMAT = "diag3-pair-global-atlas-seed-schema-v2"
ATLAS = HERE / "data" / "seeat_parent2599_upper178.npz"
SUMMARY = HERE / "data" / "DIAG2_ESCAPE_SET_atlas178_summary.json"
GLOBAL = HERE / "data" / "DIAG9_GRAPH_global_factor_census.npz"
FACTOR_STATES = HERE / "data" / "DIAG9_GRAPH_row2599_factor_states.npz"

EXPECTED_CHARTS = 178
EXPECTED_VALID_SIGNATURES = 97_224
EXPECTED_BAD_SIGNATURES_PER_CHART = 71_112
EXPECTED_TOPES_PER_CHART = 26_112
EXPECTED_PAIR_GERMS = 178
EXPECTED_ROOT_GERMS = 1_471
EXPECTED_SECTOR_GERMS = 4_959
EXPECTED_CANDIDATE_ROOT_PAIRS = 5_477
EXPECTED_TREE_SECTOR_GERMS = EXPECTED_ROOT_GERMS - EXPECTED_PAIR_GERMS
EXPECTED_FIXED_UNIT_OCCURRENCES = 84_840
EXPECTED_FACTORS = 26_740
EXPECTED_VARYING_FACTORS = 10_844
EXPECTED_FACTOR_STATE_DIGEST = factor_states.EXPECTED_DIGEST
EXPECTED_ORDERED_DIGEST = ordered.EXPECTED_SEMANTIC_DIGEST
EXPECTED_CONDITIONAL_MOD2_RANKS = (178, 1_293)
EXPECTED_CONDITIONAL_INTEGRAL_RANKS = (178, 1_293)
EXPECTED_RECEIVER_TREE_SECTOR_REQUESTS = 753_218
EXPECTED_RECEIVER_NONTREE_SECTOR_REQUESTS = 2_272_730

EXPECTED_KIND_HISTOGRAM = {
    36: 10_080,
    37: 5_040,
    38: 1_680,
    39: 2_520,
    41: 10_080,
    42: 2_520,
    44: 10_080,
    46: 6_720,
    47: 10_080,
    48: 840,
    49: 10_080,
    50: 10_080,
    51: 5_040,
}
EXPECTED_FACTOR_MULTIPLICITY_HISTOGRAM = {
    1: 25_200,
    2: 420,
    15: 280,
    65: 840,
}
EXPECTED_UNIT_COUNT_HISTOGRAM = {0: 32_760, 1: 52_080}

# Pinned after complete exact replays of the indicated schema layers.
EXPECTED_FIXED_UNIT_DIGEST = (
    "db5a59d51ca0c5d894fc7688ee83440c004c4742c6b90197020004f1c8c28a17"
)
EXPECTED_SELECTED_PAIR_ACTIVE_DIGEST = (
    "9772baa6fdad287691c9e5000d58c29a87f3b102ce24cadcfaca90b326e54383"
)
EXPECTED_RECEIVER_ASSIGNMENT_DIGEST = (
    "9c65caecfd062c44e7a62a3081cc63af1892290fd98dcc423c6d78826034a2c7"
)
EXPECTED_TRANSPORT_DIGEST = (
    "b1c2678eab2ca750a5453611303a752d50eb9e6522112a2923997122c45c5105"
)
EXPECTED_SEMANTIC_DIGEST = (
    "f7abd2825d6cf28270350bd587fafd988e3154c48110189629eb9e2590328e11"
)


BASES = tuple(combinations(range(8), 4))
BRACKET_LABELS = tuple("".join(str(value + 1) for value in basis) for basis in BASES)


def det4_columns(matrix, basis):
    return frontier.determinant_integer(
        [[int(matrix[row][column]) for column in basis] for row in range(4)]
    )


def load_seed_pairs():
    payload = json.loads(SUMMARY.read_text(encoding="utf-8"))
    records = tuple(sorted(payload["results"], key=lambda row: int(row["chart"])))
    if len(records) != EXPECTED_CHARTS:
        raise AssertionError("stored minimum-pair summary lost a chart")
    answer = []
    for chart, record in enumerate(records):
        if int(record["chart"]) != chart:
            raise AssertionError("minimum-pair summary is not in chart order")
        if int(record["bad"]) != EXPECTED_BAD_SIGNATURES_PER_CHART:
            raise AssertionError("bad-signature chart census changed")
        answer.append(
            (
                chart,
                int(record["overlap_left"]),
                int(record["overlap_right"]),
            )
        )
    return tuple(answer)


def poly_add_scaled(target, source, monomial_shift, scale):
    answer = dict(target)
    for (u_degree, v_degree), coefficient in source.items():
        monomial = (
            u_degree + monomial_shift[0],
            v_degree + monomial_shift[1],
        )
        answer[monomial] = answer.get(monomial, 0) + scale * coefficient
        if not answer[monomial]:
            del answer[monomial]
    return answer


def ordered_family(matrix, first, second):
    """Return Y (1+uN_first) (1+vN_second) as polynomial entries."""

    family = [
        [{(0, 0): int(matrix[row, column])} for column in range(8)]
        for row in range(4)
    ]
    for parameter, direction in (((1, 0), first), ((0, 1), second)):
        source, target, sign = direction
        source -= 1
        target -= 1
        target_entries = [dict(family[row][target]) for row in range(4)]
        for row in range(4):
            family[row][source] = poly_add_scaled(
                family[row][source], target_entries[row], parameter, sign
            )
    return tuple(tuple(row) for row in family)


def parent_polynomials(matrix, first, second):
    family = ordered_family(matrix, first, second)
    values = []
    for basis in BASES:
        value = frontier.polynomial.determinant(
            [[family[row][column] for column in basis] for row in range(4)]
        )
        values.append(global_factors.primitive(value))
    return tuple(values)


def ray_terminal(matrix, root_index):
    source, target, sign = escape.DIRECTIONS[root_index]
    source -= 1
    target -= 1
    shifted = np.asarray(matrix, dtype=object).copy()
    shifted[:, source] += sign * shifted[:, target]
    candidates = []
    affine = 0
    for bracket, basis in enumerate(BASES):
        constant = det4_columns(matrix, basis)
        at_one = det4_columns(shifted, basis)
        coefficient = at_one - constant
        if coefficient:
            affine += 1
            root = Fraction(-constant, coefficient)
            if root > 0:
                candidates.append((root, bracket))
    if affine != 20:
        raise AssertionError("an elementary shear lost its 20 affine brackets")
    if not candidates:
        return (root_index, 0, 0, ())
    terminal = min(root for root, _bracket in candidates)
    labels = tuple(
        bracket for root, bracket in candidates if root == terminal
    )
    return (root_index, terminal.numerator, terminal.denominator, labels)


def axis_terminal(polynomials, axis):
    candidates = []
    for bracket, value in enumerate(polynomials):
        if axis == 0:
            constant = value.get((0, 0), 0)
            coefficient = value.get((1, 0), 0)
        else:
            constant = value.get((0, 0), 0)
            coefficient = value.get((0, 1), 0)
        if coefficient:
            root = Fraction(-constant, coefficient)
            if root > 0:
                candidates.append((root, bracket))
    if not candidates:
        return (0, 0, ())
    terminal = min(root for root, _bracket in candidates)
    return (
        terminal.numerator,
        terminal.denominator,
        tuple(bracket for root, bracket in candidates if root == terminal),
    )


def sector_parent_record(matrix, left_root, right_root, forward, reverse):
    if not (forward or reverse):
        raise AssertionError("ordered sector has no working order")
    if forward:
        first_index, second_index, selected_order = left_root, right_root, 0
    else:
        first_index, second_index, selected_order = right_root, left_root, 1
    first = escape.DIRECTIONS[first_index]
    second = escape.DIRECTIONS[second_index]
    polynomials = parent_polynomials(matrix, first, second)

    first_terminal = ray_terminal(matrix, first_index)
    second_terminal = ray_terminal(matrix, second_index)
    if axis_terminal(polynomials, 0) != first_terminal[1:]:
        raise AssertionError("sector u-axis disagrees with its root ray")
    if axis_terminal(polynomials, 1) != second_terminal[1:]:
        raise AssertionError("sector v-axis disagrees with its root ray")

    support_histogram = tuple(
        sorted(Counter(tuple(sorted(value)) for value in polynomials).items())
    )
    uv_brackets = sum((1, 1) in value for value in polynomials)
    digest = sha256()
    digest.update(b"diag3-pair-sector-parent-polynomials-v1\0")
    for label, value in zip(BRACKET_LABELS, polynomials, strict=True):
        digest.update(label.encode("ascii") + b"\0")
        digest.update(repr(tuple(sorted(value.items()))).encode("ascii"))
    truth = int(forward) | (int(reverse) << 1)
    return (
        left_root,
        right_root,
        truth,
        selected_order,
        uv_brackets,
        support_histogram,
        digest.hexdigest(),
    )


def chart_transport_audit(chart):
    seed = load_seed_pairs()[chart]
    _chart, left_signature, right_signature = seed
    with np.load(ATLAS, allow_pickle=False) as source:
        matrix = np.asarray(source["chart_matrix"][chart], dtype=np.int64)

    rows = exact_topes.derived_rows(matrix)
    enumerated = exact_topes.enumerate_topes(rows, dimension=4)
    exact_topes.verify_topes(rows, enumerated)
    topes = tuple(enumerated)
    if len(topes) != EXPECTED_TOPES_PER_CHART:
        raise AssertionError(f"chart {chart}: wrong complete-tope count")
    prepared = escape.prepare_directions(topes)
    masks = (
        escape.escape_mask(left_signature, prepared),
        escape.escape_mask(right_signature, prepared),
    )
    common_mask = masks[0] & masks[1]
    roots = tuple(index for index in range(112) if (common_mask >> index) & 1)

    candidates = []
    sectors = []
    graph_edges = []
    for offset, left_root in enumerate(roots):
        for right_root in roots[offset + 1 :]:
            if not ordered.independent(
                escape.DIRECTIONS[left_root], escape.DIRECTIONS[right_root]
            ):
                continue
            candidates.append((left_root, right_root))
            forward = ordered.order_works(
                (left_signature, right_signature), left_root, right_root, topes
            )
            reverse = ordered.order_works(
                (left_signature, right_signature), right_root, left_root, topes
            )
            if forward or reverse:
                graph_edges.append((left_root, right_root))
                sectors.append(
                    sector_parent_record(
                        matrix, left_root, right_root, forward, reverse
                    )
                )
    components, adjacency = ordered.components(roots, graph_edges)
    if len(components) != 1:
        raise AssertionError(f"chart {chart}: ordered root graph disconnected")
    rays = tuple(ray_terminal(matrix, root) for root in roots)
    return {
        "chart": chart,
        "left": left_signature,
        "right": right_signature,
        "common_mask": common_mask,
        "roots": roots,
        "candidate_edges": len(candidates),
        "edges": tuple(graph_edges),
        "sectors": tuple(sectors),
        "minimum_degree": min(len(adjacency[root]) for root in roots),
        "maximum_degree": max(len(adjacency[root]) for root in roots),
        "rays": rays,
    }


def ordered_compatibility_record(record):
    return {
        "chart": record["chart"],
        "left": record["left"],
        "right": record["right"],
        "common_mask": record["common_mask"],
        "edges": record["edges"],
    }


def transport_digest(records):
    digest = sha256()
    digest.update(b"diag3-pair-global-atlas-transport-v1\0")
    for record in records:
        digest.update(repr((record["chart"], record["rays"])).encode("ascii"))
        digest.update(repr(record["sectors"]).encode("ascii"))
    return digest.hexdigest()


def fixed_unit_classifier(charts):
    factor_data = refinement.factor_data()
    foursets, _factor_occurrences, _offsets, _units, _labels = factor_data
    table = frontier.fixed_unit_relation_table(foursets)
    with np.load(GLOBAL, allow_pickle=False) as source:
        occurrence_factor = tuple(map(int, source["occurrence_factor"]))
        stored_foursets = tuple(
            tuple(map(int, row)) for row in source["occurrence_fourset"]
        )
        multiplicities = tuple(map(int, source["factor_multiplicity"]))
        unit_offsets = tuple(map(int, source["occurrence_unit_offset"]))
    if tuple(map(tuple, foursets)) != stored_foursets:
        raise AssertionError("factor occurrence order changed")
    if (
        dict(sorted(Counter(multiplicities).items()))
        != EXPECTED_FACTOR_MULTIPLICITY_HISTOGRAM
    ):
        raise AssertionError("global factor multiplicity histogram changed")
    unit_histogram = dict(
        sorted(
            Counter(
                unit_offsets[i + 1] - unit_offsets[i]
                for i in range(len(foursets))
            ).items()
        )
    )
    if unit_histogram != EXPECTED_UNIT_COUNT_HISTOGRAM:
        raise AssertionError("parent-unit occurrence histogram changed")

    normals0 = exact_topes.derived_rows(charts[0], normalize=False)
    normals1 = exact_topes.derived_rows(charts[-1], normalize=False)
    records = []
    for occurrence, fourset in enumerate(map(tuple, foursets)):
        kind, circuit, coefficient_supports = table[fourset]
        signs0 = frontier.certified_relation_signs(
            normals0, circuit, coefficient_supports
        )
        signs1 = frontier.certified_relation_signs(
            normals1, circuit, coefficient_supports
        )
        if signs0 != signs1:
            raise AssertionError("fixed parent-unit signs changed between charts")
        ordered_signs = sorted(zip(circuit, signs0, strict=True))
        if ordered_signs[0][1] < 0:
            ordered_signs = [(index, -value) for index, value in ordered_signs]
        support_mask = sum(1 << index for index, _value in ordered_signs)
        pattern_mask = sum(
            1 << index for index, value in ordered_signs if value > 0
        )
        records.append(
            (
                occurrence,
                occurrence_factor[occurrence],
                kind,
                support_mask,
                pattern_mask,
                tuple(circuit),
                tuple(tuple(support) for support in coefficient_supports),
            )
        )
    kind_histogram = dict(sorted(Counter(record[2] for record in records).items()))
    if kind_histogram != EXPECTED_KIND_HISTOGRAM:
        raise AssertionError(f"fixed-unit kind histogram changed: {kind_histogram}")
    digest = sha256()
    digest.update(b"diag3-pair-fixed-unit-classifier-v1\0")
    digest.update(repr(tuple(records)).encode("ascii"))
    semantic = digest.hexdigest()
    if EXPECTED_FIXED_UNIT_DIGEST is not None and semantic != EXPECTED_FIXED_UNIT_DIGEST:
        raise AssertionError(f"fixed-unit classifier digest changed: {semantic}")
    return tuple(records), semantic, kind_histogram


def circuit_positive_from_record(signature, support_mask, pattern_mask):
    restriction = signature & support_mask
    return restriction == pattern_mask or restriction == (support_mask ^ pattern_mask)


def selected_pair_active_census(seeds, classifier):
    signatures = tuple(sorted({value for _chart, left, right in seeds for value in (left, right)}))
    active = {}
    positive_occurrences = {}
    for signature in signatures:
        factors = set()
        occurrence_count = 0
        for (
            _occurrence,
            factor,
            _kind,
            support_mask,
            pattern_mask,
            _circuit,
            _coefficient_supports,
        ) in classifier:
            if circuit_positive_from_record(signature, support_mask, pattern_mask):
                factors.add(factor)
                occurrence_count += 1
        active[signature] = tuple(sorted(factors))
        positive_occurrences[signature] = occurrence_count

    records = []
    digest = sha256()
    digest.update(b"diag3-pair-selected-germ-active-factors-v1\0")
    for chart, left, right in seeds:
        left_factors = active[left]
        right_factors = active[right]
        union = tuple(sorted(set(left_factors) | set(right_factors)))
        intersection = tuple(sorted(set(left_factors) & set(right_factors)))
        record = (
            chart,
            left,
            right,
            len(left_factors),
            len(right_factors),
            len(union),
            len(intersection),
            positive_occurrences[left],
            positive_occurrences[right],
        )
        records.append(record)
        digest.update(repr((record, left_factors, right_factors)).encode("ascii"))
    semantic = digest.hexdigest()
    if (
        EXPECTED_SELECTED_PAIR_ACTIVE_DIGEST is not None
        and semantic != EXPECTED_SELECTED_PAIR_ACTIVE_DIGEST
    ):
        raise AssertionError(f"selected-pair active digest changed: {semantic}")
    histograms = {
        "left_factors": dict(sorted(Counter(record[3] for record in records).items())),
        "right_factors": dict(sorted(Counter(record[4] for record in records).items())),
        "union_factors": dict(sorted(Counter(record[5] for record in records).items())),
        "intersection_factors": dict(sorted(Counter(record[6] for record in records).items())),
        "left_occurrences": dict(sorted(Counter(record[7] for record in records).items())),
        "right_occurrences": dict(sorted(Counter(record[8] for record in records).items())),
    }
    return tuple(records), semantic, histograms


def receiver_assignment_census(seeds, charts):
    parents = [
        line.strip() for line in gate.CATALOG_48.open(encoding="utf-8")
        if line.strip()
    ]
    parent_bits, signatures = gate.enumerate_extensions(parents[gate.PARENT_INDEX])
    signatures = tuple(map(int, signatures))
    with np.load(ATLAS, allow_pickle=False) as source:
        assignment = np.asarray(source["assignment"], dtype=np.uint16)
        points = np.asarray(source["point"], dtype=np.int64)
    if len(signatures) != EXPECTED_VALID_SIGNATURES:
        raise AssertionError("row-2599 extension census changed")
    if assignment.shape != (len(signatures),) or points.shape != (len(signatures), 4):
        raise AssertionError("receiver assignment certificate shape changed")

    derived_rows = []
    for chart, matrix in enumerate(charts):
        got_parent, rows = upper.chart_rows_and_parent(matrix)
        if not np.array_equal(got_parent, parent_bits):
            raise AssertionError(f"chart {chart} left parent 2599")
        derived_rows.append(rows)

    digest = sha256()
    digest.update(b"diag3-pair-receiver-assignment-seed-v1\0")
    counts = Counter()
    for signature, chart_value, point in zip(
        signatures, assignment, points, strict=True
    ):
        chart = int(chart_value)
        got_signature = 0
        for bit, row in enumerate(derived_rows[chart]):
            value = sum(
                int(coefficient) * int(x)
                for coefficient, x in zip(row, point)
            )
            if not value:
                raise AssertionError("assigned receiver point lies on a derived wall")
            if value > 0:
                got_signature |= 1 << bit
        if got_signature != signature:
            raise AssertionError("assigned receiver point has the wrong signature")
        _seed_chart, left, right = seeds[chart]
        digest.update(
            repr(
                (signature, chart, left, right, tuple(map(int, point)))
            ).encode("ascii")
        )
        counts[chart] += 1
    semantic = digest.hexdigest()
    if (
        EXPECTED_RECEIVER_ASSIGNMENT_DIGEST is not None
        and semantic != EXPECTED_RECEIVER_ASSIGNMENT_DIGEST
    ):
        raise AssertionError(f"receiver assignment digest changed: {semantic}")
    return semantic, tuple(counts[chart] for chart in range(EXPECTED_CHARTS))


def factor_state_coverage():
    with np.load(FACTOR_STATES, allow_pickle=False) as source:
        payload = {name: source[name] for name in source.files}
    semantic = factor_states.semantic_digest(payload)
    if semantic != EXPECTED_FACTOR_STATE_DIGEST:
        raise AssertionError("stored factor-state semantic digest changed")
    varied = tuple(map(int, payload["varied_factor"]))
    hamming = np.asarray(payload["chart_hamming"], dtype=np.uint16)
    upper_triangle = hamming[np.triu_indices(EXPECTED_CHARTS, 1)]
    if len(varied) != EXPECTED_VARYING_FACTORS:
        raise AssertionError("varying-factor sample census changed")
    if (int(upper_triangle.min()), int(upper_triangle.max())) != (1_125, 5_600):
        raise AssertionError("chart factor-state Hamming range changed")
    if np.count_nonzero(upper_triangle == 1):
        raise AssertionError("a stored point pair unexpectedly became wall-adjacent")
    return semantic, varied, (int(upper_triangle.min()), int(upper_triangle.max()))


def gf2_rank(columns):
    pivots = {}
    for value in columns:
        value = int(value)
        while value:
            pivot = value.bit_length() - 1
            if pivot in pivots:
                value ^= pivots[pivot]
            else:
                pivots[pivot] = value
                break
    return len(pivots)


def deterministic_spanning_tree(roots, edges):
    """Return a lexicographic tree and replay its integral unit pivots.

    This tree belongs only to the conditional point-germ choice complex.  A
    receiver wall can subdivide a selected sector, so it is not asserted to
    survive in the missing global atlas.
    """

    roots = tuple(sorted(roots))
    if not roots:
        raise AssertionError("ordered-root graph lost every vertex")
    adjacency = {root: [] for root in roots}
    normalized_edges = set()
    for left, right in edges:
        if left == right or left not in adjacency or right not in adjacency:
            raise AssertionError("ordered-root edge has an invalid endpoint")
        edge = (min(left, right), max(left, right))
        if edge in normalized_edges:
            raise AssertionError("ordered-root graph acquired a duplicate edge")
        normalized_edges.add(edge)
        adjacency[left].append(right)
        adjacency[right].append(left)
    for root in adjacency:
        adjacency[root].sort()

    anchor = roots[0]
    visited = {anchor}
    queue = [anchor]
    tree = []
    for root in queue:
        for neighbor in adjacency[root]:
            if neighbor in visited:
                continue
            visited.add(neighbor)
            queue.append(neighbor)
            tree.append((root, neighbor))
    if visited != set(roots) or len(tree) != len(roots) - 1:
        raise AssertionError("ordered-root graph is not connected")

    # Delete non-anchor leaves.  At each step the selected column has one
    # coefficient +/-1, giving an explicit unit-Smith transcript for the
    # reduced signed tree-incidence block.
    active_vertices = set(roots)
    active_edges = {tuple(sorted(edge)) for edge in tree}
    pivots = []
    while len(active_vertices) > 1:
        degrees = Counter(
            vertex
            for edge in active_edges
            for vertex in edge
            if vertex in active_vertices
        )
        leaf = next(
            (
                vertex
                for vertex in sorted(active_vertices)
                if vertex != anchor and degrees[vertex] == 1
            ),
            None,
        )
        if leaf is None:
            raise AssertionError("tree incidence lost its unit leaf pivot")
        edge = next(edge for edge in active_edges if leaf in edge)
        sign = -1 if leaf == edge[0] else 1
        pivots.append((leaf, edge, sign))
        active_edges.remove(edge)
        active_vertices.remove(leaf)
    if active_edges or len(pivots) != len(roots) - 1:
        raise AssertionError("tree unit-pivot replay stopped early")
    return tuple(tree), tuple(pivots)


def conditional_local_incidence(records, receiver_counts):
    """Replay the selected-germ cochain over both Z and F2.

    In cochain notation ``N`` sends each chart germ to all of its root rays,
    while each row of ``M`` is the signed difference of the two rays bounding
    one sector.  Consequently ``MN=0`` over the integers.  A deterministic
    spanning forest supplies all complementary unit pivots.

    The result remains conditional on the aggregate point-germ assumptions;
    it is not the balanced global pair-end complex.
    """

    root_offsets = []
    root_index = {}
    total = 0
    for record in records:
        root_offsets.append(total)
        for root in record["roots"]:
            root_index[(record["chart"], root)] = total
            total += 1
    d1_columns = []
    d2_columns = []
    signed_rows = []
    tree_sector_count = 0
    unit_tree_pivots = 0
    receiver_tree_sector_requests = 0
    for record in records:
        chart = record["chart"]
        for _root in record["roots"]:
            d1_columns.append(1 << chart)
        for left, right in record["edges"]:
            d2_columns.append(
                (1 << root_index[(chart, left)])
                | (1 << root_index[(chart, right)])
            )
            signed_rows.append(
                (
                    root_index[(chart, left)],
                    -1,
                    root_index[(chart, right)],
                    1,
                )
            )
        tree, pivots = deterministic_spanning_tree(
            record["roots"], record["edges"]
        )
        if len(tree) != len(record["roots"]) - 1 or len(pivots) != len(tree):
            raise AssertionError("local spanning-tree unit rank changed")
        tree_sector_count += len(tree)
        unit_tree_pivots += len(pivots)
        receiver_tree_sector_requests += receiver_counts[chart] * len(tree)

    # Each signed sector has one -1 and one +1 in the same chart block, so
    # composing M with N is literally zero over Z.
    for left, left_sign, right, right_sign in signed_rows:
        left_chart = (d1_columns[left] & -d1_columns[left]).bit_length() - 1
        right_chart = (d1_columns[right] & -d1_columns[right]).bit_length() - 1
        if left_chart != right_chart or left_sign + right_sign != 0:
            raise AssertionError("signed local cochain product MN is nonzero")
    if any(
        (d1_columns[(column & -column).bit_length() - 1]
         ^ d1_columns[(column ^ (column & -column)).bit_length() - 1])
        for column in d2_columns
    ):
        raise AssertionError("conditional local mod-two incidence does not square")
    ranks = (gf2_rank(d1_columns), gf2_rank(d2_columns))
    if ranks != EXPECTED_CONDITIONAL_MOD2_RANKS:
        raise AssertionError(f"conditional local mod-two ranks changed: {ranks}")
    integral_ranks = (len(records), unit_tree_pivots)
    if integral_ranks != EXPECTED_CONDITIONAL_INTEGRAL_RANKS:
        raise AssertionError(
            f"conditional local integral ranks changed: {integral_ranks}"
        )
    if tree_sector_count != EXPECTED_TREE_SECTOR_GERMS:
        raise AssertionError(
            f"conditional local spanning-forest size changed: {tree_sector_count}"
        )
    if receiver_tree_sector_requests != EXPECTED_RECEIVER_TREE_SECTOR_REQUESTS:
        raise AssertionError(
            "receiver-weighted local spanning-forest workload changed: "
            f"{receiver_tree_sector_requests}"
        )
    middle = len(d1_columns) - sum(ranks)
    if middle:
        raise AssertionError("connected local root graphs acquired conditional H1")
    if len(d1_columns) - sum(integral_ranks):
        raise AssertionError("conditional local integral H1 is nonzero")
    return {
        "integral_MN_zero": True,
        "integral_ranks": integral_ranks,
        "mod2_ranks": ranks,
        "middle_h1": middle,
        "tree_sector_germs": tree_sector_count,
        "tree_unit_pivots": unit_tree_pivots,
        "receiver_tree_sector_requests": receiver_tree_sector_requests,
    }


def aggregate_transport(records, receiver_counts):
    vertex_histogram = dict(sorted(Counter(len(record["roots"]) for record in records).items()))
    edge_histogram = dict(sorted(Counter(len(record["edges"]) for record in records).items()))
    candidate_total = sum(record["candidate_edges"] for record in records)
    root_total = sum(len(record["roots"]) for record in records)
    sector_total = sum(len(record["sectors"]) for record in records)
    if (len(records), root_total, sector_total, candidate_total) != (
        EXPECTED_PAIR_GERMS,
        EXPECTED_ROOT_GERMS,
        EXPECTED_SECTOR_GERMS,
        EXPECTED_CANDIDATE_ROOT_PAIRS,
    ):
        raise AssertionError("transport seed cell census changed")

    ordered_digest = ordered.semantic_digest(
        tuple(ordered_compatibility_record(record) for record in records)
    )
    if ordered_digest != EXPECTED_ORDERED_DIGEST:
        raise AssertionError(f"ordered-root compatibility digest changed: {ordered_digest}")
    semantic = transport_digest(records)
    if EXPECTED_TRANSPORT_DIGEST is not None and semantic != EXPECTED_TRANSPORT_DIGEST:
        raise AssertionError(f"transport digest changed: {semantic}")

    finite_rays = sum(record[1] != 0 for row in records for record in row["rays"])
    infinity_rays = root_total - finite_rays
    simultaneous_parent = Counter(
        len(ray[3]) for row in records for ray in row["rays"] if ray[1] != 0
    )
    order_truth = Counter(
        sector[2] for row in records for sector in row["sectors"]
    )
    selected_order = Counter(
        sector[3] for row in records for sector in row["sectors"]
    )
    uv_histogram = Counter(
        sector[4] for row in records for sector in row["sectors"]
    )
    receiver_ray_requests = sum(
        receiver_counts[row["chart"]] * len(row["roots"]) for row in records
    )
    receiver_sector_requests = sum(
        receiver_counts[row["chart"]] * len(row["sectors"]) for row in records
    )
    return {
        "ordered_digest": ordered_digest,
        "transport_digest": semantic,
        "vertex_histogram": vertex_histogram,
        "edge_histogram": edge_histogram,
        "finite_rays": finite_rays,
        "infinity_rays": infinity_rays,
        "simultaneous_parent_terminal_histogram": dict(sorted(simultaneous_parent.items())),
        "order_truth_histogram": dict(sorted(order_truth.items())),
        "selected_order_histogram": dict(sorted(selected_order.items())),
        "uv_bracket_histogram": dict(sorted(uv_histogram.items())),
        "receiver_ray_requests": receiver_ray_requests,
        "receiver_sector_requests": receiver_sector_requests,
    }


def semantic_digest(global_record):
    digest = sha256()
    digest.update(FORMAT.encode("ascii") + b"\0")
    digest.update(repr(global_record).encode("ascii"))
    return digest.hexdigest()


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--limit", type=int, default=EXPECTED_CHARTS)
    parser.add_argument(
        "--transport-only",
        action="store_true",
        help="skip the fixed-unit and receiver classifiers for a quick transport smoke replay",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    if not 1 <= args.workers <= 4:
        raise ValueError("--workers must lie in 1..4")
    if not 1 <= args.limit <= EXPECTED_CHARTS:
        raise ValueError("--limit must lie in 1..178")

    seeds = load_seed_pairs()
    with np.load(ATLAS, allow_pickle=False) as source:
        charts = np.asarray(source["chart_matrix"], dtype=np.int64)
    records = []
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(chart_transport_audit, chart): chart
            for chart in range(args.limit)
        }
        for future in as_completed(futures):
            records.append(future.result())
    records.sort(key=lambda row: row["chart"])
    print("PASS exact selected-pair transport germs", len(records), flush=True)

    if args.limit != EXPECTED_CHARTS:
        print("SCOPE smoke prefix only; global schema pins not applied")
        return

    factor_state_semantic, varied, hamming_range = factor_state_coverage()
    receiver_semantic, receiver_counts = receiver_assignment_census(seeds, charts)
    transport = aggregate_transport(records, receiver_counts)
    local_complex = conditional_local_incidence(records, receiver_counts)
    receiver_nontree_sector_requests = (
        transport["receiver_sector_requests"]
        - local_complex["receiver_tree_sector_requests"]
    )
    if receiver_nontree_sector_requests != EXPECTED_RECEIVER_NONTREE_SECTOR_REQUESTS:
        raise AssertionError(
            "receiver-weighted non-tree sector workload changed: "
            f"{receiver_nontree_sector_requests}"
        )
    local_complex["receiver_nontree_sector_requests"] = (
        receiver_nontree_sector_requests
    )

    if args.transport_only:
        print("TRANSPORT", transport)
        print("RECEIVER_ASSIGNMENT_DIGEST", receiver_semantic)
        print("CONDITIONAL_LOCAL_COMPLEX", local_complex)
        print("SCOPE transport schema only; fixed-unit classifier skipped")
        return

    classifier, fixed_unit_semantic, kind_histogram = fixed_unit_classifier(charts)
    active_records, active_semantic, active_histograms = selected_pair_active_census(
        seeds, classifier
    )

    missing = {
        "stored_chart_adjacencies_certified": 0,
        "stored_chart_pairs": comb(EXPECTED_CHARTS, 2),
        "known_two_sided_factor_walls_without_adjacency": len(varied),
        "known_two_sided_simultaneous_factor_candidates": comb(len(varied), 2),
        "ordered_sector_parent_CAD_missing": EXPECTED_SECTOR_GERMS,
        "receiver_ray_frontiers_missing": transport["receiver_ray_requests"],
        "receiver_sector_frontiers_missing": transport["receiver_sector_requests"],
        "unselected_bad_pairs_at_stored_charts": EXPECTED_CHARTS
        * (comb(EXPECTED_BAD_SIGNATURES_PER_CHART, 2) - 1),
        "global_relative_incidence_matrices": 1,
    }
    coverage = {
        "selected_pair_point_germs": EXPECTED_PAIR_GERMS,
        "root_ray_germs": EXPECTED_ROOT_GERMS,
        "ordered_sector_germs": EXPECTED_SECTOR_GERMS,
        "canonical_receiver_assignments": EXPECTED_VALID_SIGNATURES,
        "all_chart_receiver_occurrences": EXPECTED_CHARTS * EXPECTED_TOPES_PER_CHART,
        "fixed_unit_occurrence_rules": EXPECTED_FIXED_UNIT_OCCURRENCES,
        "primitive_factor_classes": EXPECTED_FACTORS,
        "conditional_tree_sector_germs": local_complex["tree_sector_germs"],
        "conditional_receiver_tree_sector_requests": local_complex[
            "receiver_tree_sector_requests"
        ],
    }
    completion_gates = {
        "bad_pair_family_cover": False,
        "parent_chamber_cover": False,
        "frontier_closure_cover": False,
        "relative_face_tag_cover": False,
        "integral_signed_global_lift": False,
        "global_mod2_middle_rank": False,
    }
    if all(completion_gates.values()):
        raise AssertionError("a local point schema cannot pass every global gate")
    global_record = (
        tuple(sorted(coverage.items())),
        tuple(sorted(missing.items())),
        tuple(sorted(completion_gates.items())),
        factor_state_semantic,
        hamming_range,
        fixed_unit_semantic,
        active_semantic,
        receiver_semantic,
        tuple(sorted(transport.items())),
        tuple(
            sorted(
                (key, value)
                for key, value in local_complex.items()
                if key != "receiver_nontree_sector_requests"
            )
        ),
        tuple(active_records),
        tuple(sorted(kind_histogram.items())),
        tuple(
            (name, tuple(sorted(value.items())))
            for name, value in sorted(active_histograms.items())
        ),
    )
    semantic = semantic_digest(global_record)
    if EXPECTED_SEMANTIC_DIGEST is not None and semantic != EXPECTED_SEMANTIC_DIGEST:
        raise AssertionError(f"global pair-atlas schema digest changed: {semantic}")

    print("PASS fixed-unit labeled occurrence classifier", len(classifier))
    print("PASS selected-pair active-factor census on", len(active_records), "germs")
    print("PASS exact canonical receiver assignments", sum(receiver_counts))
    active_ranges = {
        name: (
            min(histogram),
            max(histogram),
            len(histogram),
            sum(histogram.values()),
        )
        for name, histogram in active_histograms.items()
    }
    print("PAIR_ACTIVE_RANGES min/max/distinct/germs", active_ranges)
    print("TRANSPORT", transport)
    print("COVERAGE", coverage)
    print("MISSING", missing)
    print("GLOBAL_COMPLETION_GATES", completion_gates)
    print("FIXED_UNIT_DIGEST", fixed_unit_semantic)
    print("SELECTED_PAIR_ACTIVE_DIGEST", active_semantic)
    print("RECEIVER_ASSIGNMENT_DIGEST", receiver_semantic)
    print("TRANSPORT_DIGEST", transport["transport_digest"])
    print("CONDITIONAL_LOCAL_COMPLEX", local_complex)
    print("SEMANTIC_SHA256", semantic)
    print("SCHEMA exact point-germ seed and missing-block ledger")
    print("NO-CLAIM no chamber coverage, global frontier atlas, or pair H_c^1 theorem")


if __name__ == "__main__":
    main()
