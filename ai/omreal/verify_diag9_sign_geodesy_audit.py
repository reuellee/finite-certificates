#!/usr/bin/env python3
"""Scoped exact audit of evidence for the diagonal-nine sign-geodesy route.

This checker proves three finite statements and deliberately no global one:

* the already certified row-2599 line, disk, and node chamber graphs are
  isometric in their displayed active residual-factor coordinates;
* on the 178 exact row-2599 point charts, every one of the 97,224 exact
  extension-signature support traces is an intersection of sampled residual
  factor halfspaces;
* eliminating each canonical residual pivot against the parent brackets is
  not closed in the parent-bracket plus 26,740-residual-factor catalog.

The point sample has no adjacency or coverage assertion.  Consequently none
of these checks proves residual sign-geodesy, a partial-cube master graph, or
the ninth diagonal.
"""

from __future__ import annotations

import argparse
from collections import Counter, deque
from contextlib import redirect_stdout
from functools import reduce
import hashlib
from io import StringIO
from math import gcd
import multiprocessing as mp
import os
from pathlib import Path
import sys
import time

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
sys.path.insert(0, str(HERE))

import DIAG9_GRAPH_exact_topes as exact_topes


PINNED_SHA256 = {
    "seeat_parent2599_upper178.npz":
        "3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a",
    "DIAG9_GRAPH_global_factor_census.npz":
        "3984ce87e11fd59d804e59568177248e218cd1c7bb07aae0a9f9f746858728bc",
    "DIAG9_GRAPH_row2599_factor_states.npz":
        "f44b1fccfb4e61273aeceb8796a18098d82c48473e257556ce3d2a22f99b0bcf",
    "DIAG9_GRAPH_row2599_line_roadmap.npz":
        "29a4542941a322da6846fcfb2d7eb3d427ac9f7cc4becd95b4b5cd754f3ae16b",
    "DIAG9_GRAPH_row2599_line_graph.npz":
        "e1c2b82b4da6b2180d1de7e5837d2a58da4dadf159b4631fa4b2810e42df52a5",
    "DIAG9_GRAPH_row2599_disk_roadmap.npz":
        "8111a338e2169c4492ad0c5b7e03c9792d5c301c54f0f10a3ce20114db424486",
    "DIAG9_GRAPH_row2599_disk_graph.npz":
        "c0521f59aac563a4d7cbcd0405e90a3d4ae26fcf7b9239c9bfce296c6e031b1b",
    "DIAG9_GRAPH_row2599_node_roadmap.npz":
        "ddec96b052b305d279b543be2af27e12f380f0dedc79ea434616c64b40cd8cea",
    "DIAG9_GRAPH_row2599_node_graph.npz":
        "b7f48c4f4f421ba88cf551a2ba16cbd024d63d0910ada701118c88e2e2b7e19f",
}

EXPECTED_SUPPORT_DIGEST = (
    "95c2e2f520e0c3e2535846513e85b1b6b8388efba18ff53380d212bbf9decbb5"
)

EXPECTED_RESULTANT_CLASSIFICATION = {
    36: {"new": 9, "bracket": 10, "global": 7},
    37: {"new": 9, "bracket": 10, "global": 7},
    38: {"new": 15, "bracket": 5, "global": 4},
    39: {"new": 9, "bracket": 13, "global": 7},
    41: {"new": 9, "bracket": 12, "global": 7},
    42: {"new": 15, "bracket": 6, "global": 4},
    44: {"new": 9, "bracket": 13, "global": 7},
    46: {"new": 9, "bracket": 10, "global": 7},
    47: {"new": 9, "bracket": 10, "global": 7},
    48: {"new": 13, "bracket": 10, "global": 4},
    49: {"new": 14, "bracket": 6, "global": 4},
    50: {"new": 16, "bracket": 6, "global": 3},
    51: {"new": 15, "bracket": 11, "global": 4},
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_pins(names) -> None:
    for name in names:
        actual = sha256(DATA / name)
        if actual != PINNED_SHA256[name]:
            raise AssertionError(f"pinned artifact changed: {name}")


def graph_distances(vertex_count, edges):
    adjacency = [[] for _ in range(vertex_count)]
    for left, right in edges:
        left, right = int(left), int(right)
        if left == right or not (0 <= left < vertex_count and 0 <= right < vertex_count):
            raise AssertionError("invalid graph edge")
        adjacency[left].append(right)
        adjacency[right].append(left)
    distances = np.full((vertex_count, vertex_count), -1, dtype=np.int16)
    for source in range(vertex_count):
        distances[source, source] = 0
        queue = deque([source])
        while queue:
            vertex = queue.popleft()
            for target in adjacency[vertex]:
                if distances[source, target] < 0:
                    distances[source, target] = distances[source, vertex] + 1
                    queue.append(target)
        if np.any(distances[source] < 0):
            raise AssertionError("graph is disconnected")
    return distances


def assert_isometric_labeled_graph(vertex_signs, labeled_edges) -> None:
    """Check an explicitly factor-labeled graph against Hamming distance."""
    vertex_signs = tuple(map(int, vertex_signs))
    edges = []
    for left, right, coordinate in labeled_edges:
        left, right, coordinate = int(left), int(right), int(coordinate)
        if vertex_signs[left] ^ vertex_signs[right] != 1 << coordinate:
            raise AssertionError("edge does not flip exactly its displayed factor")
        edges.append((left, right))
    distances = graph_distances(len(vertex_signs), edges)
    for left in range(len(vertex_signs)):
        for right in range(len(vertex_signs)):
            hamming = (vertex_signs[left] ^ vertex_signs[right]).bit_count()
            if int(distances[left, right]) != hamming:
                raise AssertionError("displayed factor embedding is not isometric")


def occurrence_factor_map(global_data):
    foursets = np.asarray(global_data["occurrence_fourset"], dtype=np.uint8)
    occurrence_factor = np.asarray(global_data["occurrence_factor"], dtype=np.uint32)
    if foursets.shape != (84_840, 4) or occurrence_factor.shape != (84_840,):
        raise AssertionError("wrong global occurrence arrays")
    lookup = {tuple(map(int, row)): index for index, row in enumerate(foursets)}
    if len(lookup) != 84_840:
        raise AssertionError("duplicate labeled residual occurrence")

    def factors(rows):
        return {
            int(occurrence_factor[lookup[tuple(map(int, row))]])
            for row in rows
        }

    return factors


def verify_local_isometry() -> None:
    names = [
        "DIAG9_GRAPH_global_factor_census.npz",
        "DIAG9_GRAPH_row2599_line_roadmap.npz",
        "DIAG9_GRAPH_row2599_line_graph.npz",
        "DIAG9_GRAPH_row2599_disk_roadmap.npz",
        "DIAG9_GRAPH_row2599_disk_graph.npz",
        "DIAG9_GRAPH_row2599_node_roadmap.npz",
        "DIAG9_GRAPH_row2599_node_graph.npz",
    ]
    verify_pins(names)
    with np.load(DATA / names[0], allow_pickle=False) as global_data:
        factor_ids = occurrence_factor_map(global_data)

        with np.load(DATA / names[1], allow_pickle=False) as line, np.load(
            DATA / names[2], allow_pickle=False
        ) as line_graph:
            if str(line["format"].item()) != "diag9-row2599-r2c7-line-v1":
                raise AssertionError("wrong line roadmap format")
            offsets = np.asarray(line["wall_offset"], dtype=np.int64)
            wall_foursets = np.asarray(line["wall_fourset"], dtype=np.uint8)
            if offsets.shape != (26,) or offsets[0] != 0 or offsets[-1] != 89:
                raise AssertionError("wrong line wall offsets")
            line_factors = []
            for index in range(25):
                group = factor_ids(wall_foursets[offsets[index]:offsets[index + 1]])
                if len(group) != 1:
                    raise AssertionError("one line root has multiple global factors")
                line_factors.append(next(iter(group)))
            if len(set(line_factors)) != 25:
                raise AssertionError("the line crosses one global factor twice")
            if Counter(np.diff(offsets)) != Counter({1: 24, 65: 1}):
                raise AssertionError("wrong line duplicate-label census")
            graph_edges = np.asarray(line_graph["edge"], dtype=np.int64)
            expected_edges = np.asarray([(j, j + 1) for j in range(25)])
            if not np.array_equal(graph_edges, expected_edges):
                raise AssertionError("line graph is not the certified path ordering")
            line_states = [0]
            for coordinate in range(25):
                line_states.append(line_states[-1] ^ (1 << coordinate))
            assert_isometric_labeled_graph(
                line_states, [(j, j + 1, j) for j in range(25)]
            )

        with np.load(DATA / names[3], allow_pickle=False) as disk, np.load(
            DATA / names[4], allow_pickle=False
        ) as disk_graph:
            if str(disk["format"].item()) != "diag9-row2599-r2c7-r1c7-disk-v1":
                raise AssertionError("wrong disk roadmap format")
            disk_factors = factor_ids(disk["wall_fourset"])
            if disk_factors != {16_392}:
                raise AssertionError("wrong disk global factor")
            if not np.array_equal(disk_graph["edge"], np.asarray([[0, 1]])):
                raise AssertionError("disk graph is not one edge")
            assert_isometric_labeled_graph((0, 1), ((0, 1, 0),))

        with np.load(DATA / names[5], allow_pickle=False) as node, np.load(
            DATA / names[6], allow_pickle=False
        ) as node_graph:
            if str(node["format"].item()) != "diag9-row2599-transverse-node-v1":
                raise AssertionError("wrong node roadmap format")
            offsets = np.asarray(node["branch_offset"], dtype=np.int64)
            rows = np.asarray(node["branch_fourset"], dtype=np.uint8)
            branches = [
                factor_ids(rows[offsets[j]:offsets[j + 1]])
                for j in range(2)
            ]
            if branches != [{1_657}, {12_874}]:
                raise AssertionError("wrong node factor IDs")
            expected_edges = np.asarray(((0, 1), (1, 2), (2, 3), (0, 3)))
            if not np.array_equal(node_graph["edge"], expected_edges):
                raise AssertionError("node graph is not the certified four-cycle")
            # (++), (+-), (--), (-+) in branch-coordinate order.
            node_states = (0b11, 0b01, 0b00, 0b10)
            node_edges = ((0, 1, 1), (1, 2, 0), (2, 3, 1), (0, 3, 0))
            assert_isometric_labeled_graph(node_states, node_edges)

    # Negative metric canary: a repeated coordinate on a two-edge path gives
    # equal endpoint signs at graph distance two and must be rejected.
    try:
        assert_isometric_labeled_graph((0, 1, 0), ((0, 1, 0), (1, 2, 0)))
    except AssertionError:
        pass
    else:
        raise AssertionError("non-isometric repeated-factor canary was accepted")


def enumerate_chart_topes(task):
    chart_index, chart = task
    topes = exact_topes.parent_topes(chart, verify=True)
    if len(topes) != 26_112:
        raise AssertionError(f"chart {chart_index} has {len(topes)} topes")
    return chart_index, tuple(sorted(map(int, topes)))


def exact_support_masks(workers: int):
    verify_pins(("seeat_parent2599_upper178.npz",))
    with np.load(DATA / "seeat_parent2599_upper178.npz", allow_pickle=False) as source:
        if int(source["parent_index"].item()) != 2_599:
            raise AssertionError("wrong chart-bank parent")
        charts = np.asarray(source["chart_matrix"], dtype=np.int64)
    if charts.shape != (178, 4, 8):
        raise AssertionError("wrong row-2599 chart bank")
    parent_signs = exact_topes.parent_signs(charts[0])
    if any(exact_topes.parent_signs(chart) != parent_signs for chart in charts[1:]):
        raise AssertionError("stored charts do not share one parent chirotope")

    support_masks = {}
    tasks = tuple(enumerate(charts))
    if workers == 1:
        results = map(enumerate_chart_topes, tasks)
        pool = None
    else:
        pool = mp.get_context().Pool(workers)
        results = pool.imap_unordered(enumerate_chart_topes, tasks)
    try:
        for chart_index, signatures in results:
            chart_bit = 1 << int(chart_index)
            for signature in signatures:
                support_masks[signature] = support_masks.get(signature, 0) | chart_bit
    finally:
        if pool is not None:
            pool.close()
            pool.join()

    if len(support_masks) != 97_224 or any(mask == 0 for mask in support_masks.values()):
        raise AssertionError("wrong exact signature union on 178 charts")
    if len(set(support_masks.values())) != 39_366:
        raise AssertionError("wrong exact support-trace count")
    if min(map(int.bit_count, support_masks.values())) != 1:
        raise AssertionError("sample unexpectedly lacks a singleton support")
    if max(map(int.bit_count, support_masks.values())) != 178:
        raise AssertionError("sample unexpectedly lacks a full support")

    digest = hashlib.sha256()
    for signature, mask in sorted(support_masks.items()):
        digest.update(int(signature).to_bytes(8, "little"))
        digest.update(int(mask).to_bytes(23, "little"))
    if digest.hexdigest() != EXPECTED_SUPPORT_DIGEST:
        raise AssertionError("exact row-2599 support digest changed")
    return support_masks


def factor_traces_from_certificate():
    verify_pins(("DIAG9_GRAPH_row2599_factor_states.npz",))
    with np.load(
        DATA / "DIAG9_GRAPH_row2599_factor_states.npz", allow_pickle=False
    ) as source:
        if str(source["format"].item()) != "diag9-row2599-factor-state-sample-v1":
            raise AssertionError("wrong factor-state format")
        packed = np.asarray(source["chart_factor_sign_packed"], dtype=np.uint8)
        stored_unique = np.asarray(source["unique_trace_packed"], dtype=np.uint8)
    if packed.shape != (178, 3_343) or stored_unique.shape != (10_789, 23):
        raise AssertionError("wrong factor-state array shapes")

    full = (1 << 178) - 1
    traces = set()
    for factor in range(26_740):
        byte, bit = divmod(factor, 8)
        trace = 0
        for chart in range(178):
            if int(packed[chart, byte]) & (1 << bit):
                trace |= 1 << chart
        traces.add(trace)
    stored = {
        int.from_bytes(row.tobytes(), "little") & full
        for row in stored_unique
    }
    if traces != stored or len(traces) != 10_789:
        raise AssertionError("stored factor traces do not match the sign matrix")
    return traces


def factor_closure_failures(supports, factor_traces, universe_size):
    """Return supports not closed by the sampled +/- factor halfspaces."""
    full = (1 << universe_size) - 1
    supports = tuple(set(map(int, supports)))
    halfspaces = tuple(sorted(
        set(map(int, factor_traces))
        | {full ^ int(trace) for trace in factor_traces}
    ))
    chart_literals = [0] * universe_size
    for literal, halfspace in enumerate(halfspaces):
        literal_bit = 1 << literal
        remaining = halfspace
        while remaining:
            bit = remaining & -remaining
            chart_literals[bit.bit_length() - 1] |= literal_bit
            remaining ^= bit
    all_literals = (1 << len(halfspaces)) - 1

    failures = []
    for support in supports:
        if support & ~full:
            raise AssertionError("support leaves the declared universe")
        containing = all_literals
        remaining = support
        while remaining:
            bit = remaining & -remaining
            containing &= chart_literals[bit.bit_length() - 1]
            remaining ^= bit
        missing = full ^ support
        forced = 0
        while missing:
            bit = missing & -missing
            chart = bit.bit_length() - 1
            # Some containing halfspace excludes chart exactly when this is
            # nonzero.  Otherwise chart belongs to the halfspace closure.
            if not (containing & ~chart_literals[chart]):
                forced |= bit
            missing ^= bit
        if forced:
            failures.append((support, forced))
    return failures, len(halfspaces)


def verify_sample_factor_closure(workers: int) -> None:
    support_masks = exact_support_masks(workers)
    factor_traces = factor_traces_from_certificate()
    failures, halfspace_count = factor_closure_failures(
        support_masks.values(), factor_traces, 178
    )
    if failures or halfspace_count != 21_526:
        raise AssertionError("an exact sample support is not factor-halfspace closed")

    # Closure canaries: {0,1} is closed by the displayed factor halfspace,
    # whereas {0,2} is not an intersection of its two sides.
    good, _ = factor_closure_failures((0b011,), (0b011,), 3)
    bad, _ = factor_closure_failures((0b101,), (0b011,), 3)
    if good or bad != [(0b101, 0b010)]:
        raise AssertionError("factor-closure canaries failed")


def primitive_sympy_key(expression, walls):
    polynomial = walls.sp.Poly(
        walls.sp.expand(expression), *walls.variables, domain=walls.sp.QQ
    )
    if polynomial.is_zero:
        return ()
    denominator = 1
    for coefficient in polynomial.coeffs():
        denominator = walls.sp.ilcm(denominator, int(coefficient.q))
    integers = [
        (tuple(monomial), int(coefficient * denominator))
        for monomial, coefficient in polynomial.terms()
    ]
    divisor = reduce(gcd, (abs(value) for _, value in integers), 0)
    integers = [(monomial, value // divisor) for monomial, value in integers]
    leading = max(monomial for monomial, _ in integers)
    if dict(integers)[leading] < 0:
        integers = [(monomial, -value) for monomial, value in integers]
    return tuple(sorted(integers))


def global_polynomial_keys(global_data):
    offsets = np.asarray(global_data["factor_offset"], dtype=np.int64)
    exponents = np.asarray(global_data["factor_exponent"], dtype=np.int64)
    coefficients = np.asarray(global_data["factor_coefficient"], dtype=np.int64)
    if offsets.shape != (26_741,) or offsets[0] != 0 or offsets[-1] != len(exponents):
        raise AssertionError("wrong flattened global factors")
    keys = []
    for factor in range(26_740):
        keys.append(tuple(
            (tuple(map(int, exponents[index])), int(coefficients[index]))
            for index in range(offsets[factor], offsets[factor + 1])
        ))
    if len(set(keys)) != 26_740:
        raise AssertionError("global factor keys are not distinct")
    return keys


def verify_resultant_no_go() -> None:
    verify_pins(("DIAG9_GRAPH_global_factor_census.npz",))
    # Importing this foundational checker replays its complete 52-orbit exact
    # symbolic verification.  Suppress only its two success lines.
    with redirect_stdout(StringIO()):
        import verify_derived_walls as walls

    with np.load(
        DATA / "DIAG9_GRAPH_global_factor_census.npz", allow_pickle=False
    ) as source:
        global_keys = global_polynomial_keys(source)
    global_index = {key: index for index, key in enumerate(global_keys)}
    bracket_keys = {
        primitive_sympy_key(parent_bracket, walls)
        for parent_bracket in walls.brackets.values()
    }
    if len(bracket_keys) != 63:
        raise AssertionError("wrong normalized parent-bracket key count")

    classifications = {}
    new_factors = {}
    pair_factors = {}
    for residual_type in sorted(walls.RESIDUAL):
        residual = walls.RESIDUAL[residual_type]
        pivot = walls.PIVOT[residual_type][0]
        counts = Counter()
        type_new = set()
        for label, parent_bracket in walls.brackets.items():
            if walls.sp.degree(parent_bracket, pivot) <= 0:
                continue
            resultant = walls.sp.resultant(residual, parent_bracket, pivot)
            if resultant == 0:
                raise AssertionError("residual and parent bracket share a factor")
            _, factors = walls.sp.factor_list(resultant, *walls.variables)
            pair_factors[(residual_type, label)] = []
            for factor, multiplicity in factors:
                key = primitive_sympy_key(factor, walls)
                if key in bracket_keys:
                    kind = "bracket"
                elif key in global_index:
                    kind = "global"
                else:
                    kind = "new"
                    type_new.add(key)
                    new_factors.setdefault(key, factor)
                counts[kind] += int(multiplicity)
                pair_factors[(residual_type, label)].append((kind, key))
        if dict(counts) != EXPECTED_RESULTANT_CLASSIFICATION[residual_type]:
            raise AssertionError(f"wrong resultant census for type {residual_type}")
        if len(type_new) != EXPECTED_RESULTANT_CLASSIFICATION[residual_type]["new"]:
            raise AssertionError(f"repeated new resultant within type {residual_type}")
        classifications[residual_type] = dict(counts)

    degrees = Counter(
        int(walls.sp.Poly(factor, *walls.variables).total_degree())
        for factor in new_factors.values()
    )
    if len(new_factors) != 142 or degrees != Counter({2: 23, 3: 71, 4: 43, 5: 5}):
        raise AssertionError("wrong first-layer new resultant census")

    example = walls.c * walls.d - walls.c + walls.f
    example_key = primitive_sympy_key(example, walls)
    if example_key not in new_factors:
        raise AssertionError("type-36/[1346] new-factor canary disappeared")
    if primitive_sympy_key(-2 * example, walls) != example_key:
        raise AssertionError("primitive associate normalization canary failed")
    known_global = pair_factors[(36, "1467")]
    if len(known_global) != 1 or known_global[0][0] != "global":
        raise AssertionError("known global-resultant canary failed")
    if global_index[known_global[0][1]] != 10_519:
        raise AssertionError("known global-resultant ID changed")
    if {kind for kind, _ in pair_factors[(36, "1367")]} != {"bracket"}:
        raise AssertionError("known bracket-resultant canary failed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--workers",
        type=int,
        default=min(7, os.cpu_count() or 1),
        help="exact chart-tope workers (default: min(7, CPU count))",
    )
    args = parser.parse_args()
    if args.workers < 1:
        raise SystemExit("--workers must be positive")

    started = time.perf_counter()
    phase = started
    verify_local_isometry()
    local_seconds = time.perf_counter() - phase
    print("PASS: certified local chamber graphs P26, K2, and Q2 are factor-isometric")

    phase = time.perf_counter()
    verify_sample_factor_closure(args.workers)
    sample_seconds = time.perf_counter() - phase
    print("PASS: exact topes = 178 charts x 26112; union = 97224 signatures")
    print("PASS: all 39366 exact support traces are intersections of sampled factor halfspaces")
    print(f"SUPPORT SEMANTIC SHA256: {EXPECTED_SUPPORT_DIGEST}")

    phase = time.perf_counter()
    verify_resultant_no_go()
    resultant_seconds = time.perf_counter() - phase
    print("PASS: first pivot-boundary resultant layer has 142 new irreducibles")
    print("PASS: new-resultant degree census = 2:23, 3:71, 4:43, 5:5")
    print("NO-GO: pivot elimination is not closed in brackets plus 26740 residual factors")

    total_seconds = time.perf_counter() - started
    print(
        "RUNTIME seconds: "
        f"local={local_seconds:.1f} sample={sample_seconds:.1f} "
        f"resultants={resultant_seconds:.1f} total={total_seconds:.1f}"
    )
    print("TRUST: local geometry and stored factor signs are hash-pinned prior certificates")
    print("SCOPE: 178 points have no chamber coverage or adjacency certificate")
    print("SCOPE: this proves neither sign-geodesy, a global partial cube, nor diagonal 9")


if __name__ == "__main__":
    main()
