#!/usr/bin/env python3
"""Exact combinatorial verifier for ninth-diagonal tree certificates.

The geometric input is a *complete* labeled master-chamber graph.  This
program deliberately does not pretend to certify that geometric coverage;
it verifies the finite graph theorem once such data are supplied.

Rows of ``support`` are distinct proper feasibility regions and columns are
master chambers.  Inclusion of rows is therefore exactly inclusion of the
corresponding regions.  A size-nine 9DVL input is a nine-element antichain of
rows.  Its common support is the induced subgraph on columns containing all
nine rows.

Two tree tests are implemented.

``sharp_tree_certificate`` is the proof-safe pairwise test.  For vertices
u,v, put E_uv=T(u) intersect T(v).  Every vertex w on the tree path u--v must
contain every element d of E_uv which can occur in a nine-antichain of E_uv.
Equivalently, if w misses d, the elements of E_uv incomparable with d must
have width at most seven.

``coarse_union_cut_certificate`` implements the earlier proposed C_e test,
where C_e is the intersection of the unions of labels on the two sides of a
tree edge.  It is sufficient but strictly stronger.  The built-in exact
regression exhausts all spanning trees of a ten-vertex graph on which the
ninth conclusion holds but every spanning tree fails the coarse test.

No floating point arithmetic, LP, SAT heuristic, or hash-based verdict is
used.  The only potentially expensive primitive is exact Dilworth width,
computed by bipartite maximum matching on strict region inclusion.
"""

from __future__ import annotations

import argparse
from collections import deque
from itertools import combinations
from math import comb
from pathlib import Path

import numpy as np


FORMAT = "diag9-labeled-master-tree-v1"
TARGET = 9


def normalize_edges(edges, vertex_count, expected_count=None):
    answer = set()
    for raw_left, raw_right in np.asarray(edges).tolist():
        left, right = int(raw_left), int(raw_right)
        if left == right or not (0 <= left < vertex_count and 0 <= right < vertex_count):
            raise AssertionError(f"bad graph edge {(left, right)}")
        edge = (left, right) if left < right else (right, left)
        if edge in answer:
            raise AssertionError(f"duplicate graph edge {edge}")
        answer.add(edge)
    if expected_count is not None and len(answer) != expected_count:
        raise AssertionError(
            f"expected {expected_count} edges, found {len(answer)}"
        )
    return tuple(sorted(answer))


def adjacency(vertex_count, edges):
    result = [[] for _ in range(vertex_count)]
    for left, right in edges:
        result[left].append(right)
        result[right].append(left)
    return tuple(tuple(sorted(row)) for row in result)


def connected_vertices(graph, allowed=None, start=None):
    if allowed is None:
        allowed = set(range(len(graph)))
    else:
        allowed = set(allowed)
    if not allowed:
        return True
    if start is None:
        start = min(allowed)
    if start not in allowed:
        return False
    seen = {start}
    queue = deque([start])
    while queue:
        vertex = queue.popleft()
        for neighbor in graph[vertex]:
            if neighbor in allowed and neighbor not in seen:
                seen.add(neighbor)
                queue.append(neighbor)
    return seen == allowed


def support_masks(support):
    raw = np.asarray(support)
    if raw.ndim != 2 or raw.shape[0] == 0 or raw.shape[1] == 0:
        raise AssertionError("support must be a nonempty region-by-vertex matrix")
    if not np.all((raw == 0) | (raw == 1)):
        raise AssertionError("support matrix is not binary")
    region_count, vertex_count = raw.shape
    masks = []
    for region in range(region_count):
        mask = sum(int(raw[region, vertex]) << vertex for vertex in range(vertex_count))
        if mask == 0 or mask == (1 << vertex_count) - 1:
            raise AssertionError(f"region {region} is not nonempty and proper")
        masks.append(mask)
    if len(set(masks)) != len(masks):
        raise AssertionError(
            "duplicate support rows must be quotient-identified before verification"
        )
    return tuple(masks), vertex_count


def strict_less(left, right, masks):
    """Region left is a strict subset of region right."""
    return left != right and masks[left] & ~masks[right] == 0


def incomparable(left, right, masks):
    return not strict_less(left, right, masks) and not strict_less(right, left, masks)


def hopcroft_karp(adjacency_rows):
    """Maximum matching cardinality for a bipartite graph, exactly."""
    left_count = len(adjacency_rows)
    match_left = [-1] * left_count
    match_right = [-1] * left_count
    distance = [0] * left_count
    infinity = left_count + 1

    while True:
        queue = deque()
        for left in range(left_count):
            if match_left[left] < 0:
                distance[left] = 0
                queue.append(left)
            else:
                distance[left] = infinity
        found = False
        while queue:
            left = queue.popleft()
            for right in adjacency_rows[left]:
                mate = match_right[right]
                if mate < 0:
                    found = True
                elif distance[mate] == infinity:
                    distance[mate] = distance[left] + 1
                    queue.append(mate)
        if not found:
            break

        def augment(left):
            for right in adjacency_rows[left]:
                mate = match_right[right]
                if mate < 0 or (
                    distance[mate] == distance[left] + 1 and augment(mate)
                ):
                    match_left[left] = right
                    match_right[right] = left
                    return True
            distance[left] = infinity
            return False

        for left in range(left_count):
            if match_left[left] < 0:
                augment(left)

    return sum(right >= 0 for right in match_left)


def poset_width(elements, masks, stop_above=None):
    """Dilworth width of an induced finite inclusion poset."""
    elements = tuple(sorted(set(map(int, elements))))
    if len(elements) <= 1:
        return len(elements)
    rows = []
    for left in elements:
        rows.append(
            tuple(
                position
                for position, right in enumerate(elements)
                if strict_less(left, right, masks)
            )
        )
    width = len(elements) - hopcroft_karp(rows)
    if stop_above is not None and width > stop_above:
        return width
    return width


def vertex_labels(masks, vertex):
    bit = 1 << vertex
    return frozenset(region for region, mask in enumerate(masks) if mask & bit)


def validate_tree(graph, tree_edges):
    vertex_count = len(graph)
    edges = normalize_edges(tree_edges, vertex_count, vertex_count - 1)
    graph_edges = {
        (left, right) if left < right else (right, left)
        for left, row in enumerate(graph)
        for right in row
    }
    if any(edge not in graph_edges for edge in edges):
        raise AssertionError("tree contains an edge absent from the master graph")
    tree = adjacency(vertex_count, edges)
    if not connected_vertices(tree):
        raise AssertionError("claimed spanning tree is disconnected")
    return tree


def tree_path(tree, source, target):
    parent = {source: -1}
    queue = deque([source])
    while queue and target not in parent:
        vertex = queue.popleft()
        for neighbor in tree[vertex]:
            if neighbor not in parent:
                parent[neighbor] = vertex
                queue.append(neighbor)
    if target not in parent:
        raise AssertionError("tree path does not exist")
    path = []
    vertex = target
    while vertex >= 0:
        path.append(vertex)
        vertex = parent[vertex]
    return tuple(reversed(path))


def sharp_tree_certificate(graph, masks, tree_edges, target=TARGET):
    """Verify the pairwise antichain-aware tree condition.

    Returns ``(True, statistics)`` on success.  On failure it returns an exact
    obstruction ``(u,v,w,d,width)``; a width at least ``target-1`` means that
    d extends to a target-element antichain common to u and v but missing at
    w on their tree path.
    """
    tree = validate_tree(graph, tree_edges)
    labels = tuple(vertex_labels(masks, vertex) for vertex in range(len(graph)))
    queries = 0
    skipped_narrow_pairs = 0
    for source in range(len(graph)):
        for target_vertex in range(source + 1, len(graph)):
            common = labels[source] & labels[target_vertex]
            if poset_width(common, masks) < target:
                skipped_narrow_pairs += 1
                continue
            for waypoint in tree_path(tree, source, target_vertex):
                for missing in sorted(common - labels[waypoint]):
                    queries += 1
                    residue = [
                        region
                        for region in common
                        if region != missing and incomparable(region, missing, masks)
                    ]
                    width = poset_width(residue, masks)
                    if width >= target - 1:
                        return False, {
                            "source": source,
                            "target": target_vertex,
                            "waypoint": waypoint,
                            "missing": missing,
                            "residue_width": width,
                        }
    return True, {
        "vertex_pairs": comb(len(graph), 2),
        "narrow_pairs": skipped_narrow_pairs,
        "width_queries": queries,
    }


def tree_edge_sides(tree, left, right):
    side = {left}
    queue = deque([left])
    while queue:
        vertex = queue.popleft()
        for neighbor in tree[vertex]:
            if (vertex == left and neighbor == right) or (
                vertex == right and neighbor == left
            ):
                continue
            if neighbor not in side:
                side.add(neighbor)
                queue.append(neighbor)
    other = set(range(len(tree))) - side
    if not other:
        raise AssertionError("tree-edge deletion did not split the tree")
    return side, other


def coarse_union_cut_certificate(graph, masks, tree_edges, target=TARGET):
    """Verify the sufficient but over-strong union-cut C_e condition."""
    tree = validate_tree(graph, tree_edges)
    labels = tuple(vertex_labels(masks, vertex) for vertex in range(len(graph)))
    for left in range(len(tree)):
        for right in tree[left]:
            if left > right:
                continue
            first, second = tree_edge_sides(tree, left, right)
            union_first = frozenset().union(*(labels[v] for v in first))
            union_second = frozenset().union(*(labels[v] for v in second))
            common = union_first & union_second
            for endpoint in (left, right):
                for missing in sorted(common - labels[endpoint]):
                    residue = [
                        region
                        for region in common
                        if region != missing and incomparable(region, missing, masks)
                    ]
                    width = poset_width(residue, masks)
                    if width >= target - 1:
                        return False, {
                            "tree_edge": (left, right),
                            "endpoint": endpoint,
                            "missing": missing,
                            "residue_width": width,
                            "first_side": tuple(sorted(first)),
                            "second_side": tuple(sorted(second)),
                        }
    return True, {"tree_edges": len(tree) - 1}


def direct_ninth_check(graph, masks, maximum_families=1_000_000):
    """Exhaust all nine-antichains when the finite instance is small."""
    region_count = len(masks)
    family_bound = comb(region_count, TARGET) if region_count >= TARGET else 0
    if family_bound > maximum_families:
        raise RuntimeError(
            f"direct audit would inspect {family_bound} families; use a tree certificate"
        )
    checked = 0
    for family in combinations(range(region_count), TARGET):
        if any(not incomparable(left, right, masks) for left, right in combinations(family, 2)):
            continue
        checked += 1
        allowed = [
            vertex
            for vertex in range(len(graph))
            if all(masks[region] & (1 << vertex) for region in family)
        ]
        if not connected_vertices(graph, allowed):
            return False, {"family": family, "allowed": tuple(allowed)}
    return True, {"antichains_checked": checked}


def no_go_fixture():
    """A target-true graph on which every coarse C_e tree test fails.

    Vertices 0,...,8 form a 9-cycle; vertex 9 is a leaf at vertex 0.  Region
    i is supported at every vertex except cycle vertex i.  The nine regions
    are proper and pairwise incomparable, and their common support is the
    singleton {9}.  Hence the only ninth-diagonal instance is connected.

    Every spanning tree deletes one cycle edge.  Its cycle part is a path and
    has an internal edge whose two sides each contain at least two cycle
    vertices.  Every region occurs on both sides of that cut, while each
    endpoint misses one region.  Thus the coarse union-cut test fails.
    """
    vertex_count = 10
    cycle = tuple((vertex, (vertex + 1) % 9) for vertex in range(9))
    graph_edges = normalize_edges(cycle + ((0, 9),), vertex_count)
    graph = adjacency(vertex_count, graph_edges)
    support = np.ones((9, vertex_count), dtype=np.uint8)
    for region in range(9):
        support[region, region] = 0
    masks, _ = support_masks(support)
    return graph, masks, cycle


def disconnected_fixture():
    """A nine-antichain whose common support is exactly two nonadjacent points."""
    vertex_count = 12
    edges = ((0, 1), (1, 2)) + tuple((1, 3 + index) for index in range(9))
    graph = adjacency(vertex_count, normalize_edges(edges, vertex_count))
    support = np.zeros((9, vertex_count), dtype=np.uint8)
    for region in range(9):
        support[region, 0] = support[region, 2] = 1
        support[region, 3:] = 1
        support[region, 3 + region] = 0
        if region:
            support[region, 1] = 1
    masks, _ = support_masks(support)
    return graph, masks, edges


def connected_core_fixture():
    """A nontrivial connected nine-antichain with a three-vertex core."""
    vertex_count = 12
    edges = ((0, 1), (1, 2)) + tuple((1, 3 + index) for index in range(9))
    graph = adjacency(vertex_count, normalize_edges(edges, vertex_count))
    support = np.ones((9, vertex_count), dtype=np.uint8)
    for region in range(9):
        support[region, 3 + region] = 0
    masks, _ = support_masks(support)
    return graph, masks, edges


def run_self_test():
    graph, masks, cycle = no_go_fixture()
    direct_ok, direct_stats = direct_ninth_check(graph, masks)
    assert direct_ok and direct_stats == {"antichains_checked": 1}

    coarse_failures = []
    sharp_passes = 0
    # Every spanning tree of a cycle with one forced leaf edge is obtained by
    # deleting exactly one of the nine cycle edges.
    full_edges = {
        (min(left, right), max(left, right))
        for left, row in enumerate(graph)
        for right in row
        if left < right
    }
    for deleted in cycle:
        deleted = (min(deleted), max(deleted))
        tree_edges = tuple(sorted(full_edges - {deleted}))
        coarse_ok, obstruction = coarse_union_cut_certificate(graph, masks, tree_edges)
        assert not coarse_ok and obstruction["residue_width"] == 8
        coarse_failures.append((deleted, obstruction["tree_edge"]))
        sharp_ok, _ = sharp_tree_certificate(graph, masks, tree_edges)
        assert sharp_ok
        sharp_passes += 1

    bad_graph, bad_masks, bad_tree = disconnected_fixture()
    bad_direct, bad_witness = direct_ninth_check(bad_graph, bad_masks)
    assert not bad_direct and bad_witness["allowed"] == (0, 2)
    bad_sharp, bad_obstruction = sharp_tree_certificate(
        bad_graph, bad_masks, bad_tree
    )
    assert not bad_sharp
    assert bad_obstruction == {
        "source": 0,
        "target": 2,
        "waypoint": 1,
        "missing": 0,
        "residue_width": 8,
    }

    core_graph, core_masks, core_tree = connected_core_fixture()
    core_direct, core_stats = direct_ninth_check(core_graph, core_masks)
    assert core_direct and core_stats == {"antichains_checked": 1}
    core_sharp, _ = sharp_tree_certificate(core_graph, core_masks, core_tree)
    assert core_sharp

    print("PASS: exact Dilworth widths and graph connectivity")
    print("PASS: fixture has one proper nine-antichain with connected common support")
    print("PASS: all 9 spanning trees fail the coarse union-cut C_e condition")
    print("PASS: all 9 spanning trees pass the sharp pairwise E_uv condition")
    print("PASS: negative control detects an exact disconnected nine-antichain")
    print("PASS: nontrivial three-vertex common core passes direct and tree tests")
    print("THEOREM: the pairwise tree certificate is proof-safe for s=9")
    print("NO-GO: the union-cut C_e certificate is sufficient but not complete")
    return coarse_failures, sharp_passes


def load_and_verify(path):
    data = np.load(path, allow_pickle=False)
    required = {"format", "edge", "support", "tree_edge"}
    if set(data.files) != required:
        raise AssertionError(f"wrong certificate fields: {sorted(data.files)}")
    if str(data["format"].item()) != FORMAT:
        raise AssertionError("wrong certificate format")
    masks, vertex_count = support_masks(data["support"])
    graph_edges = normalize_edges(data["edge"], vertex_count)
    graph = adjacency(vertex_count, graph_edges)
    if not connected_vertices(graph):
        raise AssertionError("master graph is disconnected")
    ok, result = sharp_tree_certificate(graph, masks, data["tree_edge"])
    if not ok:
        raise AssertionError(f"sharp tree certificate fails: {result}")
    print(f"PASS: sharp tree certificate for {vertex_count} vertices, {len(masks)} regions")
    print(f"PASS: {result}")
    print("CONDITIONAL THEOREM: every proper nine-antichain has connected support graph")
    print("TRUST BOUNDARY: geometric master-chamber coverage is not encoded by this file")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "certificate",
        nargs="?",
        type=Path,
        help="optional diag9-labeled-master-tree-v1 NPZ certificate",
    )
    args = parser.parse_args()
    run_self_test()
    if args.certificate is not None:
        load_and_verify(args.certificate)


if __name__ == "__main__":
    main()
