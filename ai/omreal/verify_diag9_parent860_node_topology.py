#!/usr/bin/env python3
"""Independent fail-closed audit of the parent-860 transverse-node artifact.

This verifier deliberately does not import the artifact producer.  It checks
the stored exact geometry, incidence identities, support-pattern census,
intersection closure, and graph connectivity directly from the NPZ payload.
Hostile in-memory mutations must be rejected before the certificate passes.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "DIAG9_GRAPH_parent860_node_roadmap.npz"
FORMAT = "diag9-parent860-transverse-node-v1"
EXPECTED_DIGEST = "b7080a332d7b80127ae362bbfa2d5806fbe153d24245ef002d4867df6e1e274d"
EXPECTED_KEYS = {
    "format",
    "parent_index",
    "variable",
    "active_factor",
    "active_factor_type",
    "active_factor_multiplicity",
    "branch_normal",
    "jacobian",
    "other_worst_factor",
    "bracket_worst",
    "cell_sign",
    "wall_target",
    "wall_adjacency",
    "edge",
    "tree_edge",
    "cell_tope",
    "wall_tope_offset",
    "wall_tope",
    "node_tope",
    "signature",
    "signature_pattern",
    "proper_pattern",
    "intersection_closure",
    "disconnected_closure",
    "center_h_numerator",
    "center_h_denominator",
    "center_i_numerator",
    "center_i_denominator",
    "radius_numerator",
    "radius_denominator",
    "other_margin_numerator",
    "other_margin_denominator",
    "bracket_margin_numerator",
    "bracket_margin_denominator",
    "cell_point_numerator",
    "cell_point_denominator",
    "wall_point_numerator",
    "wall_point_denominator",
}

CENTER = (
    Fraction(3_727_672_351_519_660, 8_405_164_123_084_547),
    Fraction(5_135_974_949_766_124, 12_881_287_028_869_217),
)
RADIUS = Fraction(1, 1_000_000)
NORMALS = ((16_648, 60_347), (-145_429_401, 303_924_845))
JACOBIAN = 13_835_968_881_707
CELL_SIGNS = ((1, 1), (1, -1), (-1, -1), (-1, 1))
WALL_TARGETS = ((0, 1), (0, -1), (-1, 0), (1, 0))
WALL_ADJACENCY = ((0, 3), (1, 2), (2, 3), (0, 1))
EDGES = ((0, 1), (1, 2), (2, 3), (0, 3))
TREE_EDGES = ((0, 1), (1, 2), (2, 3))
EXPECTED_COUNTS = (26_112, 26_112, 26_112, 26_112)
EXPECTED_WALL_COUNTS = (26_110, 26_110, 26_040, 26_040)
EXPECTED_NODE_COUNT = 26_038
EXPECTED_MULTIPLICITY = Counter({15: 26_038, 9: 72, 6: 72, 3: 2, 12: 2})
EXPECTED_PROPER = (3, 6, 9, 12)
EXPECTED_CLOSURE = (0, 1, 2, 3, 4, 6, 8, 9, 12, 15)


def scalar(value):
    array = np.asarray(value)
    if array.shape != ():
        raise AssertionError("expected scalar certificate field")
    return array.item()


def integer_tuple(value):
    return tuple(map(int, np.asarray(value).tolist()))


def integer_rows(value):
    return tuple(tuple(map(int, row)) for row in np.asarray(value).tolist())


def fraction(payload, prefix):
    numerator = int(scalar(payload[f"{prefix}_numerator"]))
    denominator = int(scalar(payload[f"{prefix}_denominator"]))
    if denominator <= 0:
        raise AssertionError(f"{prefix} denominator is not positive")
    return Fraction(numerator, denominator)


def fraction_rows(payload, prefix):
    numerators = np.asarray(payload[f"{prefix}_numerator"])
    denominators = np.asarray(payload[f"{prefix}_denominator"])
    if numerators.shape != denominators.shape or len(numerators.shape) != 2:
        raise AssertionError(f"malformed rational point field: {prefix}")
    answer = []
    for numerator_row, denominator_row in zip(numerators, denominators):
        row = []
        for numerator, denominator in zip(numerator_row, denominator_row):
            denominator = int(denominator)
            if denominator <= 0:
                raise AssertionError(f"{prefix} denominator is not positive")
            row.append(Fraction(int(numerator), denominator))
        answer.append(tuple(row))
    return tuple(answer)


def semantic_digest(payload):
    digest = hashlib.sha256()
    for name in sorted(payload):
        array = np.asarray(payload[name])
        digest.update(name.encode("ascii"))
        digest.update(str(array.dtype).encode("ascii"))
        digest.update(repr(array.shape).encode("ascii"))
        digest.update(array.tobytes())
    return digest.hexdigest()


def sign(value):
    return 1 if value > 0 else -1 if value < 0 else 0


def branch_signs(point, normals=NORMALS):
    return tuple(sign(a * point[0] + b * point[1]) for a, b in normals)


def intersection_closure(patterns):
    answer = {15}
    for pattern in sorted(set(patterns)):
        answer |= {old & pattern for old in tuple(answer)}
    return tuple(sorted(answer))


def connected(mask, edges=EDGES):
    vertices = [vertex for vertex in range(4) if mask & (1 << vertex)]
    if not vertices:
        return True
    neighbors = [[] for _ in range(4)]
    for left, right in edges:
        neighbors[left].append(right)
        neighbors[right].append(left)
    seen = {vertices[0]}
    stack = vertices[:1]
    while stack:
        vertex = stack.pop()
        for neighbor in neighbors[vertex]:
            if mask & (1 << neighbor) and neighbor not in seen:
                seen.add(neighbor)
                stack.append(neighbor)
    return len(seen) == len(vertices)


def sorted_unique(row):
    values = tuple(map(int, row))
    return values == tuple(sorted(set(values)))


def audit(payload, *, check_digest=True):
    if set(payload) != EXPECTED_KEYS:
        raise AssertionError("certificate field set changed")
    if str(scalar(payload["format"])) != FORMAT:
        raise AssertionError("certificate format changed")
    if check_digest and semantic_digest(payload) != EXPECTED_DIGEST:
        raise AssertionError("certificate semantic digest changed")

    if int(scalar(payload["parent_index"])) != 860:
        raise AssertionError("parent index changed")
    if integer_tuple(payload["variable"]) != (7, 8):
        raise AssertionError("coordinate plane changed")
    if integer_tuple(payload["active_factor"]) != (15_250, 19_721):
        raise AssertionError("active factor pair changed")
    if integer_tuple(payload["active_factor_type"]) != (49, 36):
        raise AssertionError("active factor types changed")
    if integer_tuple(payload["active_factor_multiplicity"]) != (1, 65):
        raise AssertionError("active factor multiplicities changed")
    if int(scalar(payload["other_worst_factor"])) != 16_249:
        raise AssertionError("other-factor frontier witness changed")
    if str(scalar(payload["bracket_worst"])) != "2378":
        raise AssertionError("bracket frontier witness changed")

    if (fraction(payload, "center_h"), fraction(payload, "center_i")) != CENTER:
        raise AssertionError("node center changed")
    if fraction(payload, "radius") != RADIUS:
        raise AssertionError("node radius changed")
    if fraction(payload, "other_margin") <= 1:
        raise AssertionError("other factors are not excluded on the whole disk")
    if fraction(payload, "bracket_margin") <= 1:
        raise AssertionError("parent brackets are not fixed on the whole disk")

    normals = integer_rows(payload["branch_normal"])
    if normals != NORMALS:
        raise AssertionError("branch normals changed")
    determinant = normals[0][0] * normals[1][1] - normals[0][1] * normals[1][0]
    if determinant != JACOBIAN or int(scalar(payload["jacobian"])) != determinant:
        raise AssertionError("branches are not the pinned transverse crossing")

    cell_points = fraction_rows(payload, "cell_point")
    wall_points = fraction_rows(payload, "wall_point")
    if len(cell_points) != 4 or len(wall_points) != 4:
        raise AssertionError("wrong number of stratum samples")
    for point, target in zip(cell_points, CELL_SIGNS):
        if max(map(abs, point)) >= RADIUS or branch_signs(point, normals) != target:
            raise AssertionError("invalid chamber sample")
    for point, target in zip(wall_points, WALL_TARGETS):
        if max(map(abs, point)) >= RADIUS or branch_signs(point, normals) != target:
            raise AssertionError("invalid wall sample")
    if integer_rows(payload["cell_sign"]) != CELL_SIGNS:
        raise AssertionError("cell sign order changed")
    if integer_rows(payload["wall_target"]) != WALL_TARGETS:
        raise AssertionError("wall target order changed")
    if integer_rows(payload["wall_adjacency"]) != WALL_ADJACENCY:
        raise AssertionError("wall adjacency changed")
    if integer_rows(payload["edge"]) != EDGES:
        raise AssertionError("cell graph changed")
    if integer_rows(payload["tree_edge"]) != TREE_EDGES:
        raise AssertionError("spanning tree changed")

    cells_array = np.asarray(payload["cell_tope"])
    if cells_array.shape != (4, 26_112):
        raise AssertionError("chamber tope array shape changed")
    cells = tuple(tuple(map(int, row)) for row in cells_array)
    if tuple(map(len, cells)) != EXPECTED_COUNTS or not all(map(sorted_unique, cells)):
        raise AssertionError("invalid chamber labels")

    offsets = integer_tuple(payload["wall_tope_offset"])
    flat_walls = tuple(map(int, np.asarray(payload["wall_tope"])))
    if offsets != (0, 26_110, 52_220, 78_260, 104_300):
        raise AssertionError("wall label offsets changed")
    walls = tuple(
        flat_walls[offsets[index] : offsets[index + 1]] for index in range(4)
    )
    if tuple(map(len, walls)) != EXPECTED_WALL_COUNTS or not all(map(sorted_unique, walls)):
        raise AssertionError("invalid wall labels")

    node = tuple(map(int, np.asarray(payload["node_tope"])))
    if len(node) != EXPECTED_NODE_COUNT or not sorted_unique(node):
        raise AssertionError("invalid node labels")
    cell_sets = tuple(map(set, cells))
    wall_sets = tuple(map(set, walls))
    for wall, (left, right) in zip(wall_sets, WALL_ADJACENCY):
        if wall != cell_sets[left] & cell_sets[right]:
            raise AssertionError("wall is not its adjacent-chamber intersection")
    if set(node) != set.intersection(*cell_sets):
        raise AssertionError("node is not the four-chamber intersection")
    for left, right in combinations(wall_sets, 2):
        if set(node) != left & right:
            raise AssertionError("node is not every two-wall intersection")

    reconstructed = {}
    for cell, labels in enumerate(cells):
        for label in labels:
            reconstructed[label] = reconstructed.get(label, 0) | (1 << cell)
    signatures = tuple(map(int, np.asarray(payload["signature"])))
    patterns = integer_tuple(payload["signature_pattern"])
    if signatures != tuple(sorted(reconstructed)):
        raise AssertionError("signature universe changed")
    if patterns != tuple(reconstructed[label] for label in signatures):
        raise AssertionError("stored support pattern disagrees with chamber labels")
    if Counter(patterns) != EXPECTED_MULTIPLICITY:
        raise AssertionError("support-pattern multiplicity changed")
    proper = tuple(sorted(set(patterns) - {0, 15}))
    if proper != EXPECTED_PROPER or integer_tuple(payload["proper_pattern"]) != proper:
        raise AssertionError("proper supports are not the four cyclic halfspaces")
    closure = intersection_closure(patterns)
    if closure != EXPECTED_CLOSURE:
        raise AssertionError("intersection closure changed")
    if integer_tuple(payload["intersection_closure"]) != closure:
        raise AssertionError("stored intersection closure is stale")
    disconnected = tuple(mask for mask in closure if not connected(mask))
    if disconnected or np.asarray(payload["disconnected_closure"]).size:
        raise AssertionError("a common-feasibility support is disconnected")


def hostile_canaries(payload):
    mutations = []

    broken = {name: np.array(value, copy=True) for name, value in payload.items()}
    broken["jacobian"] = np.asarray(0, dtype=broken["jacobian"].dtype)
    mutations.append(("zero Jacobian", broken))

    broken = {name: np.array(value, copy=True) for name, value in payload.items()}
    broken["other_margin_numerator"] = np.asarray("1")
    broken["other_margin_denominator"] = np.asarray("2")
    mutations.append(("subunit isolation margin", broken))

    broken = {name: np.array(value, copy=True) for name, value in payload.items()}
    broken["wall_tope"][0] = np.iinfo(broken["wall_tope"].dtype).max
    mutations.append(("corrupted wall gluing", broken))

    broken = {name: np.array(value, copy=True) for name, value in payload.items()}
    broken["proper_pattern"][1] = 5
    mutations.append(("disconnected diagonal support", broken))

    for label, broken in mutations:
        try:
            audit(broken, check_digest=False)
        except AssertionError:
            continue
        raise AssertionError(f"hostile canary accepted: {label}")
    return tuple(label for label, _broken in mutations)


def main():
    with np.load(CERTIFICATE, allow_pickle=False) as source:
        payload = {name: source[name] for name in source.files}
    audit(payload)
    canaries = hostile_canaries(payload)
    print("PASS independent exact geometry and transverse-node audit")
    print("PASS chamber/wall/node incidence and tope-label gluing")
    print("PASS support intersection closure is connected on the four-cycle")
    print("PASS hostile canaries rejected:", ", ".join(canaries))
    print("THEOREM every finite common-feasibility locus on the disk is empty or convex")
    print("SCOPE local parent-860 disk only; no global 9DVL diagonal is claimed")


if __name__ == "__main__":
    main()
