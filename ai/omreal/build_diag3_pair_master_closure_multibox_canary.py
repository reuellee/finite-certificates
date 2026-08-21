#!/usr/bin/env python3
"""Build the exact row-2599 3x3 multi-box master-closure canary.

The producer refines the pinned transverse-node disk in the two exact branch
coordinates.  It emits nine declared boxes, atomic boundary sign words and a
global regular-CW grid.  Coverage, gluing, parent residence and pair ranks are
recomputed by the independent verifier.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUTPUT = DATA / "DIAG3_PAIR_MASTER_CLOSURE_MULTIBOX_CANARY.json"
NODE = DATA / "DIAG9_GRAPH_row2599_node_roadmap.npz"
CANDIDATES = DATA / "DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin"
LEDGER = DATA / "DIAG3_RESEARCH_DECISION_LEDGER.json"
PARENT_GATE = DATA / "DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json"

sys.path.insert(0, str(HERE))
import DIAG9_GRAPH_verify_row2599_node as node  # noqa: E402
import four_chart_gate as extension_gate  # noqa: E402


FORMAT = "diag3-pair-master-closure-multibox-certificate-v1"
STATUS = "LOCAL_EXACT_MULTIBOX_CANARY"
SOURCE_COMMIT = "0e3195ff7d0b672c5693b168e43c44ae9306da57"
EXPECTED_NODE_SHA256 = (
    "ddec96b052b305d279b543be2af27e12f380f0dedc79ea434616c64b40cd8cea"
)
EXPECTED_CANDIDATE_SHA256 = (
    "adb2e7257457f158e809450683c46fe7ecafdbdd4a7efdf9ac630e8a4f0fb03f"
)
EXPECTED_PARENT_SIGN_SHA256 = (
    "1d9b940e2bb954b5c69bcee8b2346f9554b2e15589ea4c5b3c3f8e1e943de701"
)
EXPECTED_PROFILE_COUNTS = {0: 70_968, 3: 72, 6: 72, 9: 72, 12: 72, 15: 25_968}

AXIS_SCALE = 10**12
BOX_LEVELS = (-3 * AXIS_SCALE, -AXIS_SCALE, AXIS_SCALE, 3 * AXIS_SCALE)
CELL_LEVELS = (-3 * AXIS_SCALE, -AXIS_SCALE, 0, AXIS_SCALE, 3 * AXIS_SCALE)
CHAMBER_SIGNS = ((1, 1), (1, -1), (-1, -1), (-1, 1))
SIGN_TO_CHAMBER = {signs: index for index, signs in enumerate(CHAMBER_SIGNS)}


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def sign(value: int | Fraction) -> int:
    return 1 if value > 0 else -1 if value < 0 else 0


def branch_matrix():
    return tuple(
        (
            int(linear[(1, 0)]),
            int(linear[(0, 1)]),
        )
        for linear in node.CENTERED_BRANCHES
    )


def to_cell_coordinates(q0: int | Fraction, q1: int | Fraction):
    matrix = branch_matrix()
    determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
    return (
        Fraction(matrix[1][1] * q0 - matrix[0][1] * q1, determinant),
        Fraction(-matrix[1][0] * q0 + matrix[0][0] * q1, determinant),
    )


def chamber_index(q0: int | Fraction, q1: int | Fraction) -> int:
    return SIGN_TO_CHAMBER[(sign(q0), sign(q1))]


def raw_cells():
    cells = {}
    for i, q0 in enumerate(CELL_LEVELS):
        for j, q1 in enumerate(CELL_LEVELS):
            cells[f"p{i}_{j}"] = {
                "dimension": 0,
                "boundary": [],
                "branch_vertices": ((q0, q1),),
            }
    for i in range(4):
        for j, q1 in enumerate(CELL_LEVELS):
            cells[f"h{i}_{j}"] = {
                "dimension": 1,
                "boundary": [f"p{i}_{j}", f"p{i + 1}_{j}"],
                "branch_vertices": (
                    (CELL_LEVELS[i], q1),
                    (CELL_LEVELS[i + 1], q1),
                ),
            }
    for i, q0 in enumerate(CELL_LEVELS):
        for j in range(4):
            cells[f"v{i}_{j}"] = {
                "dimension": 1,
                "boundary": [f"p{i}_{j}", f"p{i}_{j + 1}"],
                "branch_vertices": (
                    (q0, CELL_LEVELS[j]),
                    (q0, CELL_LEVELS[j + 1]),
                ),
            }
    for i in range(4):
        for j in range(4):
            cells[f"f{i}_{j}"] = {
                "dimension": 2,
                "boundary": [
                    f"h{i}_{j}",
                    f"v{i + 1}_{j}",
                    f"h{i}_{j + 1}",
                    f"v{i}_{j}",
                ],
                "branch_vertices": (
                    (CELL_LEVELS[i], CELL_LEVELS[j]),
                    (CELL_LEVELS[i + 1], CELL_LEVELS[j]),
                    (CELL_LEVELS[i + 1], CELL_LEVELS[j + 1]),
                    (CELL_LEVELS[i], CELL_LEVELS[j + 1]),
                ),
            }
    return cells


def midpoint(vertices):
    return (
        sum(Fraction(point[0]) for point in vertices) / len(vertices),
        sum(Fraction(point[1]) for point in vertices) / len(vertices),
    )


def incident_chambers(cells):
    incident = {identifier: set() for identifier in cells}
    for identifier, cell in cells.items():
        if cell["dimension"] != 2:
            continue
        q0, q1 = midpoint(cell["branch_vertices"])
        chamber = chamber_index(q0, q1)
        incident[identifier].add(chamber)
        for edge in cell["boundary"]:
            incident[edge].add(chamber)
            for vertex in cells[edge]["boundary"]:
                incident[vertex].add(chamber)
    if any(not values for values in incident.values()):
        raise AssertionError("a grid cell has no incident residual chamber")
    return incident


def cell_kind(identifier, cell):
    vertices = cell["branch_vertices"]
    dimension = cell["dimension"]
    q0_values = {point[0] for point in vertices}
    q1_values = {point[1] for point in vertices}
    on_q0_wall = q0_values == {0}
    on_q1_wall = q1_values == {0}
    on_scope = any(
        abs(point[0]) == 3 * AXIS_SCALE or abs(point[1]) == 3 * AXIS_SCALE
        for point in vertices
    ) and all(
        abs(point[0]) == 3 * AXIS_SCALE or abs(point[1]) == 3 * AXIS_SCALE
        for point in vertices
    )
    on_seam = (
        q0_values in ({-AXIS_SCALE}, {AXIS_SCALE})
        or q1_values in ({-AXIS_SCALE}, {AXIS_SCALE})
    )
    if dimension == 2:
        return "open_residual_chamber_piece"
    if dimension == 1 and (on_q0_wall or on_q1_wall):
        return "residual_wall_segment"
    if dimension == 1 and on_scope:
        return "scope_boundary_segment"
    if dimension == 1 and on_seam:
        return "atlas_seam_segment"
    if dimension == 0 and q0_values == {0} and q1_values == {0}:
        return "residual_node"
    if dimension == 0 and (on_q0_wall or on_q1_wall) and on_scope:
        return "scope_boundary_residual_endpoint"
    if dimension == 0 and (on_q0_wall or on_q1_wall) and on_seam:
        return "atlas_seam_residual_crossing"
    if dimension == 0 and on_scope:
        return "scope_boundary_vertex"
    if dimension == 0 and on_seam:
        return "atlas_seam_vertex"
    return "grid_vertex"


def build_cells():
    source = raw_cells()
    incident = incident_chambers(source)
    answer = []
    for identifier in sorted(source, key=lambda key: (source[key]["dimension"], key)):
        cell = source[identifier]
        q_witness = midpoint(cell["branch_vertices"])
        x_witness = to_cell_coordinates(*q_witness)
        answer.append(
            {
                "id": identifier,
                "dimension": cell["dimension"],
                "kind": cell_kind(identifier, cell),
                "witness_branch_coordinates": [fraction_text(value) for value in q_witness],
                "witness_cell_coordinates": [fraction_text(value) for value in x_witness],
                "boundary": list(cell["boundary"]),
                "incident_residual_chambers": sorted(incident[identifier]),
            }
        )
    return answer


def closure_data(cells):
    immediate = {(cell["id"], face) for cell in cells for face in cell["boundary"]}
    closure = set(immediate)
    changed = True
    while changed:
        changed = False
        for high, middle in tuple(closure):
            for middle2, low in tuple(closure):
                if middle == middle2 and (high, low) not in closure:
                    closure.add((high, low))
                    changed = True
    chains = {
        (high, middle, low)
        for high, middle in immediate
        for middle2, low in immediate
        if middle == middle2
    }
    return [list(row) for row in sorted(closure)], [list(row) for row in sorted(chains)]


def integral_boundary():
    d1 = []
    for i in range(4):
        for j in range(5):
            edge = f"h{i}_{j}"
            d1.extend(((f"p{i}_{j}", edge, -1), (f"p{i + 1}_{j}", edge, 1)))
    for i in range(5):
        for j in range(4):
            edge = f"v{i}_{j}"
            d1.extend(((f"p{i}_{j}", edge, -1), (f"p{i}_{j + 1}", edge, 1)))
    d2 = []
    for i in range(4):
        for j in range(4):
            face = f"f{i}_{j}"
            d2.extend(
                (
                    (f"h{i}_{j}", face, 1),
                    (f"v{i + 1}_{j}", face, 1),
                    (f"h{i}_{j + 1}", face, -1),
                    (f"v{i}_{j}", face, -1),
                )
            )
    return {
        "orientation_rule": "horizontal and vertical edges point in increasing q0 and q1; each rectangle is counterclockwise",
        "c0_basis": [f"p{i}_{j}" for i in range(5) for j in range(5)],
        "c1_basis": [
            *[f"h{i}_{j}" for i in range(4) for j in range(5)],
            *[f"v{i}_{j}" for i in range(5) for j in range(4)],
        ],
        "c2_basis": [f"f{i}_{j}" for i in range(4) for j in range(4)],
        "d1_entries": [list(row) for row in d1],
        "d2_entries": [list(row) for row in d2],
    }


def box_index_for_atomic_interval(index: int) -> int:
    return 0 if index == 0 else 1 if index in (1, 2) else 2


def boundary_segments():
    segments = []
    for boundary_index, fixed in enumerate(BOX_LEVELS):
        for interval_index in range(4):
            low, high = CELL_LEVELS[interval_index : interval_index + 2]
            box_row = box_index_for_atomic_interval(interval_index)
            incidents = []
            if boundary_index:
                incidents.append(
                    {"box": f"box_{boundary_index - 1}_{box_row}", "side": "right", "orientation": 1}
                )
            if boundary_index < 3:
                incidents.append(
                    {"box": f"box_{boundary_index}_{box_row}", "side": "left", "orientation": -1}
                )
            segments.append(
                {
                    "id": f"seg_v_{boundary_index}_{interval_index}",
                    "axis": "vertical",
                    "fixed": str(fixed),
                    "interval": [str(low), str(high)],
                    "open_segment_sign_word": [sign(fixed), sign(low + high)],
                    "incidents": incidents,
                }
            )
    for boundary_index, fixed in enumerate(BOX_LEVELS):
        for interval_index in range(4):
            low, high = CELL_LEVELS[interval_index : interval_index + 2]
            box_column = box_index_for_atomic_interval(interval_index)
            incidents = []
            if boundary_index:
                incidents.append(
                    {"box": f"box_{box_column}_{boundary_index - 1}", "side": "top", "orientation": -1}
                )
            if boundary_index < 3:
                incidents.append(
                    {"box": f"box_{box_column}_{boundary_index}", "side": "bottom", "orientation": 1}
                )
            segments.append(
                {
                    "id": f"seg_h_{boundary_index}_{interval_index}",
                    "axis": "horizontal",
                    "fixed": str(fixed),
                    "interval": [str(low), str(high)],
                    "open_segment_sign_word": [sign(low + high), sign(fixed)],
                    "incidents": incidents,
                }
            )
    return segments


def box_records(cells, segments):
    answer = []
    cell_source = raw_cells()
    for i in range(3):
        for j in range(3):
            q0_bounds = BOX_LEVELS[i : i + 2]
            q1_bounds = BOX_LEVELS[j : j + 2]
            events = [
                branch
                for branch, bounds in enumerate((q0_bounds, q1_bounds))
                if bounds[0] < 0 < bounds[1]
            ]
            classification = (
                "no_wall" if not events
                else "one_wall" if len(events) == 1
                else "transverse_two_wall"
            )
            identifier = f"box_{i}_{j}"
            closure_cells = []
            for cell_id, cell in cell_source.items():
                if all(
                    q0_bounds[0] <= q0 <= q0_bounds[1]
                    and q1_bounds[0] <= q1 <= q1_bounds[1]
                    for q0, q1 in cell["branch_vertices"]
                ):
                    closure_cells.append(cell_id)
            words = {side: [] for side in ("bottom", "right", "top", "left")}
            for segment in segments:
                for incidence in segment["incidents"]:
                    if incidence["box"] == identifier:
                        words[incidence["side"]].append(
                            {"segment": segment["id"], "orientation": incidence["orientation"]}
                        )
            answer.append(
                {
                    "id": identifier,
                    "q0_interval": list(map(str, q0_bounds)),
                    "q1_interval": list(map(str, q1_bounds)),
                    "classification": classification,
                    "active_branch_events": events,
                    "closure_cells": sorted(
                        closure_cells,
                        key=lambda key: (cell_source[key]["dimension"], key),
                    ),
                    "boundary_words": words,
                }
            )
    return answer


def boundary_subcomplex(cells, predicate):
    raw = raw_cells()
    return [
        cell["id"]
        for cell in cells
        if predicate(raw[cell["id"]]["branch_vertices"])
    ]


def signature_profile_data():
    with np.load(NODE, allow_pickle=False) as source:
        stored = {
            int(signature): int(pattern)
            for signature, pattern in zip(source["signature"], source["signature_pattern"])
        }
    parents = [
        line.strip()
        for line in extension_gate.CATALOG_48.open(encoding="utf-8")
        if line.strip()
    ]
    _parent_bits, signatures = extension_gate.enumerate_extensions(
        parents[extension_gate.PARENT_INDEX]
    )
    if len(signatures) != len(set(signatures)) or len(signatures) != 97_224:
        raise AssertionError("row-2599 extension enumeration changed")
    digest = sha256(b"diag3-row2599-multibox-signature-profile-v1\0")
    counts = Counter()
    for signature in signatures:
        profile = stored.get(signature, 0)
        counts[profile] += 1
        digest.update(int(signature).to_bytes(8, "little"))
        digest.update(bytes((profile,)))
    if dict(sorted(counts.items())) != EXPECTED_PROFILE_COUNTS:
        raise AssertionError(f"profile counts changed: {counts}")
    return digest.hexdigest(), counts


def bad_cells(cells, feasible_profile):
    return [
        cell["id"]
        for cell in cells
        if any(
            not (feasible_profile >> chamber & 1)
            for chamber in cell["incident_residual_chambers"]
        )
    ]


def build_record():
    if file_sha256(NODE) != EXPECTED_NODE_SHA256:
        raise AssertionError("pinned node roadmap changed")
    if file_sha256(CANDIDATES) != EXPECTED_CANDIDATE_SHA256:
        raise AssertionError("pinned candidate-factor input changed")
    parent_gate = json.loads(PARENT_GATE.read_text(encoding="utf-8"))
    if parent_gate["normalized_parent_sign_sha256"] != EXPECTED_PARENT_SIGN_SHA256:
        raise AssertionError("signed parent-cell digest changed")
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    full = ledger["row2599_fullsupport_ledger"]

    cells = build_cells()
    closure, chains = closure_data(cells)
    segments = boundary_segments()
    boxes = box_records(cells, segments)
    profile_digest, profile_counts = signature_profile_data()
    coordinate_vertices = [
        to_cell_coordinates(q0, q1)
        for q0 in (-3 * AXIS_SCALE, 3 * AXIS_SCALE)
        for q1 in (-3 * AXIS_SCALE, 3 * AXIS_SCALE)
    ]
    max_abs = max(abs(value) for point in coordinate_vertices for value in point)
    matrix = branch_matrix()
    determinant = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]

    scope_boundary = boundary_subcomplex(
        cells,
        lambda vertices: all(
            abs(q0) == 3 * AXIS_SCALE or abs(q1) == 3 * AXIS_SCALE
            for q0, q1 in vertices
        ),
    )
    seam = boundary_subcomplex(
        cells,
        lambda vertices: (
            len({q0 for q0, _q1 in vertices}) == 1
            and next(iter({q0 for q0, _q1 in vertices})) in (-AXIS_SCALE, AXIS_SCALE)
        ) or (
            len({q1 for _q0, q1 in vertices}) == 1
            and next(iter({q1 for _q0, q1 in vertices})) in (-AXIS_SCALE, AXIS_SCALE)
        ),
    )
    residual = boundary_subcomplex(
        cells,
        lambda vertices: (
            len({q0 for q0, _q1 in vertices}) == 1
            and next(iter({q0 for q0, _q1 in vertices})) == 0
        ) or (
            len({q1 for _q0, q1 in vertices}) == 1
            and next(iter({q1 for _q0, q1 in vertices})) == 0
        ),
    )

    profiles = [
        {
            "feasible_chamber_mask": profile,
            "signature_count": profile_counts[profile],
            "bad_cells": bad_cells(cells, profile),
        }
        for profile in sorted(profile_counts)
    ]

    return {
        "format": FORMAT,
        "status": STATUS,
        "scope": {
            "parent_index": 2599,
            "compactification": "(Delta^3)^3",
            "support": [15, 15, 15],
            "claim": "complete exact 3x3 multi-box regular-CW closure atlas inside one two-dimensional row-2599 full-support disk",
            "local_parameter_coverage": "COMPLETE",
            "global_parameter_coverage": "NOT_CLAIMED",
            "scope_boundary_policy": "ordinary cells; never parent infinity",
            "atlas_seam_policy": "ordinary cells; exact boundary-word gluing only",
        },
        "inputs": {
            "source_commit": SOURCE_COMMIT,
            "node_roadmap_path": str(NODE.relative_to(HERE.parents[1])),
            "node_roadmap_sha256": EXPECTED_NODE_SHA256,
            "candidate_factor_path": str(CANDIDATES.relative_to(HERE.parents[1])),
            "candidate_factor_sha256": EXPECTED_CANDIDATE_SHA256,
            "candidate_factor_count": full["fullsupport_factor_count"],
            "exact_empty_factor_digest": full["digests"]["empty_factor_ids"],
            "unresolved_factor_digest": full["digests"]["unresolved_factor_ids"],
            "target_signed_parent_digest": EXPECTED_PARENT_SIGN_SHA256,
        },
        "generator": {
            "backend": "exact_branch_coordinate_3x3_grid_v1",
            "build_command": "python ai/omreal/build_diag3_pair_master_closure_multibox_canary.py",
            "producer_role": "deterministic translation; all proof gates are independently replayed",
        },
        "coverage_evidence": {
            "kind": "exact_branch_coordinate_multibox_partition",
            "labelled_residual_occurrence_universe": 84_840,
            "parent_bracket_count": 70,
            "branch_matrix": [list(row) for row in matrix],
            "branch_matrix_determinant": str(determinant),
            "axis_scale": str(AXIS_SCALE),
            "box_levels": list(map(str, BOX_LEVELS)),
            "cell_levels": list(map(str, CELL_LEVELS)),
            "source_disk_radius": fraction_text(node.RADIUS),
            "domain_cell_coordinate_vertices": [
                [fraction_text(value) for value in point] for point in coordinate_vertices
            ],
            "domain_max_abs_cell_coordinate": fraction_text(max_abs),
            "classification_census": dict(
                sorted(Counter(box["classification"] for box in boxes).items())
            ),
        },
        "stop_contract": {
            "declared_box_ceiling": 9,
            "used_boxes": 9,
            "ceiling_status": "WITHIN_CEILING",
            "unclassified_boxes": [],
            "higher_specialization_boxes": [],
            "maximum_simultaneous_residual_branches": 2,
            "automatic_enlargement": False,
            "next_failure_policy": "preserve the first unclassified box or projection-growth frontier",
        },
        "boxes": boxes,
        "boundary_word_segments": segments,
        "cells": cells,
        "strict_closure_pairs": closure,
        "strict_three_cell_chains": chains,
        "scope_boundary_subcomplex": scope_boundary,
        "atlas_seam_subcomplex": seam,
        "residual_wall_subcomplex": residual,
        "parent_infinity_subcomplex": [],
        "signature_profile_source": {
            "universe_count": 97_224,
            "semantic_sha256": profile_digest,
            "profiles": profiles,
        },
        "integral_boundary": integral_boundary(),
        "verifier": {
            "command": "python ai/omreal/verify_diag3_pair_master_closure_multibox_canary.py",
            "recomputes": [
                "all 84,840 residual restrictions and 70 parent brackets",
                "exact branch-coordinate containment in the certified source disk",
                "all nine box classifications and every atomic shared-boundary sign word",
                "the 81-cell regular-CW closure and integral d_squared identity",
                "all 97,224 extension-signature profiles",
                "all 216 ordered profile-triple ranks on the barycentric two-skeleton",
            ],
        },
    }


def main():
    record = build_record()
    OUTPUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print("WROTE", OUTPUT)


if __name__ == "__main__":
    main()
