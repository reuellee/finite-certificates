#!/usr/bin/env python3
"""Independent exact replay of the row-2599 3x3 multi-box canary."""

from __future__ import annotations

from collections import Counter
import copy
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
CERTIFICATE = DATA / "DIAG3_PAIR_MASTER_CLOSURE_MULTIBOX_CANARY.json"
NODE = DATA / "DIAG9_GRAPH_row2599_node_roadmap.npz"
CANDIDATES = DATA / "DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin"
LEDGER = DATA / "DIAG3_RESEARCH_DECISION_LEDGER.json"
PARENT_GATE = DATA / "DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json"

sys.path.insert(0, str(HERE))
import DIAG9_GRAPH_verify_row2599_node as node  # noqa: E402
import four_chart_gate as extension_gate  # noqa: E402
import verify_diag3_pair_global_candidate_factors as candidate_input  # noqa: E402
import verify_diag3_pair_global_master_quotient as master  # noqa: E402


FORMAT = "diag3-pair-master-closure-multibox-certificate-v1"
STATUS = "LOCAL_EXACT_MULTIBOX_CANARY"
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
EXPECTED_RANK_HISTOGRAM = {
    (0, 0, 0, 0): 16,
    (8, 8, 0, 0): 12,
    (56, 24, 32, 0): 24,
    (108, 44, 64, 0): 36,
    (116, 52, 64, 0): 36,
    (164, 68, 96, 0): 24,
    (208, 80, 128, 0): 3,
    (216, 88, 128, 0): 52,
    (316, 124, 192, 0): 12,
    (416, 160, 256, 0): 1,
}

AXIS_SCALE = 10**12
BOX_LEVELS = (-3 * AXIS_SCALE, -AXIS_SCALE, AXIS_SCALE, 3 * AXIS_SCALE)
CELL_LEVELS = (-3 * AXIS_SCALE, -AXIS_SCALE, 0, AXIS_SCALE, 3 * AXIS_SCALE)
CHAMBER_SIGNS = ((1, 1), (1, -1), (-1, -1), (-1, 1))
SIGN_TO_CHAMBER = {signs: index for index, signs in enumerate(CHAMBER_SIGNS)}


class CertificateError(AssertionError):
    pass


def require(condition, message):
    if not condition:
        raise CertificateError(message)


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def sign(value):
    return 1 if value > 0 else -1 if value < 0 else 0


def branch_matrix():
    return tuple(
        (int(linear[(1, 0)]), int(linear[(0, 1)]))
        for linear in node.CENTERED_BRANCHES
    )


def determinant():
    matrix = branch_matrix()
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def to_cell_coordinates(q0, q1):
    matrix = branch_matrix()
    det = determinant()
    return (
        Fraction(matrix[1][1] * q0 - matrix[0][1] * q1, det),
        Fraction(-matrix[1][0] * q0 + matrix[0][0] * q1, det),
    )


def chamber_index(q0, q1):
    return SIGN_TO_CHAMBER[(sign(q0), sign(q1))]


def raw_cells():
    cells = {}
    for i, q0 in enumerate(CELL_LEVELS):
        for j, q1 in enumerate(CELL_LEVELS):
            cells[f"p{i}_{j}"] = (0, (), ((q0, q1),))
    for i in range(4):
        for j, q1 in enumerate(CELL_LEVELS):
            cells[f"h{i}_{j}"] = (
                1,
                (f"p{i}_{j}", f"p{i + 1}_{j}"),
                ((CELL_LEVELS[i], q1), (CELL_LEVELS[i + 1], q1)),
            )
    for i, q0 in enumerate(CELL_LEVELS):
        for j in range(4):
            cells[f"v{i}_{j}"] = (
                1,
                (f"p{i}_{j}", f"p{i}_{j + 1}"),
                ((q0, CELL_LEVELS[j]), (q0, CELL_LEVELS[j + 1])),
            )
    for i in range(4):
        for j in range(4):
            cells[f"f{i}_{j}"] = (
                2,
                (f"h{i}_{j}", f"v{i + 1}_{j}", f"h{i}_{j + 1}", f"v{i}_{j}"),
                (
                    (CELL_LEVELS[i], CELL_LEVELS[j]),
                    (CELL_LEVELS[i + 1], CELL_LEVELS[j]),
                    (CELL_LEVELS[i + 1], CELL_LEVELS[j + 1]),
                    (CELL_LEVELS[i], CELL_LEVELS[j + 1]),
                ),
            )
    return cells


def midpoint(vertices):
    return (
        sum(Fraction(point[0]) for point in vertices) / len(vertices),
        sum(Fraction(point[1]) for point in vertices) / len(vertices),
    )


def incident_chambers(cells):
    incident = {identifier: set() for identifier in cells}
    for identifier, (dimension, boundary, vertices) in cells.items():
        if dimension != 2:
            continue
        chamber = chamber_index(*midpoint(vertices))
        incident[identifier].add(chamber)
        for edge in boundary:
            incident[edge].add(chamber)
            for vertex in cells[edge][1]:
                incident[vertex].add(chamber)
    require(all(incident.values()), "grid cell incidence")
    return incident


def expected_kind(dimension, vertices):
    q0_values = {point[0] for point in vertices}
    q1_values = {point[1] for point in vertices}
    on_q0_wall = q0_values == {0}
    on_q1_wall = q1_values == {0}
    on_scope = all(
        abs(q0) == 3 * AXIS_SCALE or abs(q1) == 3 * AXIS_SCALE
        for q0, q1 in vertices
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


def expected_cells():
    source = raw_cells()
    incident = incident_chambers(source)
    result = {}
    for identifier, (dimension, boundary, vertices) in source.items():
        q_witness = midpoint(vertices)
        result[identifier] = {
            "dimension": dimension,
            "kind": expected_kind(dimension, vertices),
            "q_witness": q_witness,
            "x_witness": to_cell_coordinates(*q_witness),
            "boundary": boundary,
            "incident": tuple(sorted(incident[identifier])),
        }
    return result


def closure_data(cells):
    immediate = {
        (identifier, face)
        for identifier, cell in cells.items()
        for face in cell["boundary"]
    }
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
    return immediate, closure, chains


def expected_integral_boundary():
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
        "c0_basis": tuple(f"p{i}_{j}" for i in range(5) for j in range(5)),
        "c1_basis": (
            *(f"h{i}_{j}" for i in range(4) for j in range(5)),
            *(f"v{i}_{j}" for i in range(5) for j in range(4)),
        ),
        "c2_basis": tuple(f"f{i}_{j}" for i in range(4) for j in range(4)),
        "d1_entries": tuple(d1),
        "d2_entries": tuple(d2),
    }


def box_index_for_atomic_interval(index):
    return 0 if index == 0 else 1 if index in (1, 2) else 2


def expected_segments():
    result = {}
    for boundary_index, fixed in enumerate(BOX_LEVELS):
        for interval_index in range(4):
            low, high = CELL_LEVELS[interval_index : interval_index + 2]
            box_row = box_index_for_atomic_interval(interval_index)
            incidents = []
            if boundary_index:
                incidents.append((f"box_{boundary_index - 1}_{box_row}", "right", 1))
            if boundary_index < 3:
                incidents.append((f"box_{boundary_index}_{box_row}", "left", -1))
            result[f"seg_v_{boundary_index}_{interval_index}"] = (
                "vertical", fixed, (low, high), (sign(fixed), sign(low + high)), tuple(incidents)
            )
    for boundary_index, fixed in enumerate(BOX_LEVELS):
        for interval_index in range(4):
            low, high = CELL_LEVELS[interval_index : interval_index + 2]
            box_column = box_index_for_atomic_interval(interval_index)
            incidents = []
            if boundary_index:
                incidents.append((f"box_{box_column}_{boundary_index - 1}", "top", -1))
            if boundary_index < 3:
                incidents.append((f"box_{box_column}_{boundary_index}", "bottom", 1))
            result[f"seg_h_{boundary_index}_{interval_index}"] = (
                "horizontal", fixed, (low, high), (sign(low + high), sign(fixed)), tuple(incidents)
            )
    return result


def expected_boxes(cells, segments):
    raw = raw_cells()
    result = {}
    for i in range(3):
        for j in range(3):
            q0_bounds = BOX_LEVELS[i : i + 2]
            q1_bounds = BOX_LEVELS[j : j + 2]
            events = tuple(
                branch
                for branch, bounds in enumerate((q0_bounds, q1_bounds))
                if bounds[0] < 0 < bounds[1]
            )
            classification = "no_wall" if not events else "one_wall" if len(events) == 1 else "transverse_two_wall"
            identifier = f"box_{i}_{j}"
            closure = tuple(
                sorted(
                    (
                        cell_id
                        for cell_id, (_dimension, _boundary, vertices) in raw.items()
                        if all(
                            q0_bounds[0] <= q0 <= q0_bounds[1]
                            and q1_bounds[0] <= q1 <= q1_bounds[1]
                            for q0, q1 in vertices
                        )
                    ),
                    key=lambda key: (cells[key]["dimension"], key),
                )
            )
            words = {side: [] for side in ("bottom", "right", "top", "left")}
            for segment_id, (_axis, _fixed, _interval, _word, incidents) in segments.items():
                for box, side, orientation in incidents:
                    if box == identifier:
                        words[side].append((segment_id, orientation))
            result[identifier] = (q0_bounds, q1_bounds, classification, events, closure, words)
    return result


def expected_subcomplex(cells, predicate):
    raw = raw_cells()
    return {
        identifier
        for identifier in cells
        if predicate(raw[identifier][2])
    }


def exact_profile_data():
    exact_cells, _walls, _node = node.exact_labels()
    patterns = node.signature_patterns(exact_cells)
    parents = [
        line.strip()
        for line in extension_gate.CATALOG_48.open(encoding="utf-8")
        if line.strip()
    ]
    _parent_bits, signatures = extension_gate.enumerate_extensions(
        parents[extension_gate.PARENT_INDEX]
    )
    require(len(signatures) == len(set(signatures)) == 97_224, "extension universe")
    require(set(patterns).issubset(signatures), "profile signature universe")
    digest = sha256(b"diag3-row2599-multibox-signature-profile-v1\0")
    counts = Counter()
    for signature in signatures:
        profile = patterns.get(signature, 0)
        counts[profile] += 1
        digest.update(int(signature).to_bytes(8, "little"))
        digest.update(bytes((profile,)))
    require(dict(sorted(counts.items())) == EXPECTED_PROFILE_COUNTS, "profile census")
    return digest.hexdigest(), counts


def expected_bad_cells(cells, profile):
    return {
        identifier
        for identifier, cell in cells.items()
        if any(not (profile >> chamber & 1) for chamber in cell["incident"])
    }


def barycentric_master(cells, chains):
    ordered = sorted(cells, key=lambda key: (cells[key]["dimension"], key))
    indices = {identifier: index for index, identifier in enumerate(ordered)}
    maximal = tuple(
        sorted(
            {
                tuple(sorted((indices[high], indices[middle], indices[low])))
                for high, middle, low in chains
            }
        )
    )
    return master.MasterComplex(maximal, frozenset()), indices


def validate(record, sources):
    geometry, profile_digest, profile_counts = sources
    require(
        set(record) == {
            "format", "status", "scope", "inputs", "generator", "coverage_evidence",
            "stop_contract", "boxes", "boundary_word_segments", "cells",
            "strict_closure_pairs", "strict_three_cell_chains", "scope_boundary_subcomplex",
            "atlas_seam_subcomplex", "residual_wall_subcomplex", "parent_infinity_subcomplex",
            "signature_profile_source", "integral_boundary", "verifier",
        },
        "top-level fields",
    )
    require(record["format"] == FORMAT and record["status"] == STATUS, "format/status")
    scope = record["scope"]
    require(scope["parent_index"] == 2599 and scope["support"] == [15, 15, 15], "scope parent/support")
    require(scope["local_parameter_coverage"] == "COMPLETE", "local coverage")
    require(scope["global_parameter_coverage"] == "NOT_CLAIMED", "global scope")
    require(scope["scope_boundary_policy"] == "ordinary cells; never parent infinity", "scope boundary policy")
    require(scope["atlas_seam_policy"] == "ordinary cells; exact boundary-word gluing only", "seam policy")

    inputs = record["inputs"]
    require(file_sha256(NODE) == inputs["node_roadmap_sha256"] == EXPECTED_NODE_SHA256, "node digest")
    require(file_sha256(CANDIDATES) == inputs["candidate_factor_sha256"] == EXPECTED_CANDIDATE_SHA256, "candidate digest")
    require(inputs["target_signed_parent_digest"] == EXPECTED_PARENT_SIGN_SHA256, "parent digest")
    require(len(candidate_input.parse_artifact()) == inputs["candidate_factor_count"] == 17_824, "factor count")
    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))["row2599_fullsupport_ledger"]
    require(inputs["exact_empty_factor_digest"] == ledger["digests"]["empty_factor_ids"], "empty digest")
    require(inputs["unresolved_factor_digest"] == ledger["digests"]["unresolved_factor_ids"], "unresolved digest")
    parent_gate = json.loads(PARENT_GATE.read_text(encoding="utf-8"))
    require(parent_gate["normalized_parent_sign_sha256"] == EXPECTED_PARENT_SIGN_SHA256, "replayed parent digest")
    require(record["generator"]["backend"] == "exact_branch_coordinate_3x3_grid_v1", "backend")

    evidence = record["coverage_evidence"]
    require(evidence["kind"] == "exact_branch_coordinate_multibox_partition", "coverage kind")
    require(evidence["labelled_residual_occurrence_universe"] == 84_840, "residual universe")
    require(evidence["parent_bracket_count"] == 70, "parent bracket universe")
    require(tuple(tuple(map(int, row)) for row in evidence["branch_matrix"]) == branch_matrix(), "branch matrix")
    require(int(evidence["branch_matrix_determinant"]) == determinant() == geometry["jacobian"], "branch determinant")
    require(int(evidence["axis_scale"]) == AXIS_SCALE, "axis scale")
    require(tuple(map(int, evidence["box_levels"])) == BOX_LEVELS, "box levels")
    require(tuple(map(int, evidence["cell_levels"])) == CELL_LEVELS, "cell levels")
    require(Fraction(evidence["source_disk_radius"]) == node.RADIUS, "source disk radius")
    domain_vertices = tuple(
        to_cell_coordinates(q0, q1)
        for q0 in (-3 * AXIS_SCALE, 3 * AXIS_SCALE)
        for q1 in (-3 * AXIS_SCALE, 3 * AXIS_SCALE)
    )
    require(
        tuple(tuple(map(Fraction, row)) for row in evidence["domain_cell_coordinate_vertices"])
        == domain_vertices,
        "domain inverse vertices",
    )
    max_abs = max(abs(value) for point in domain_vertices for value in point)
    require(Fraction(evidence["domain_max_abs_cell_coordinate"]) == max_abs < node.RADIUS, "domain containment")
    require(evidence["classification_census"] == {"no_wall": 4, "one_wall": 4, "transverse_two_wall": 1}, "classification census")

    stop = record["stop_contract"]
    require(stop == {
        "declared_box_ceiling": 9,
        "used_boxes": 9,
        "ceiling_status": "WITHIN_CEILING",
        "unclassified_boxes": [],
        "higher_specialization_boxes": [],
        "maximum_simultaneous_residual_branches": 2,
        "automatic_enlargement": False,
        "next_failure_policy": "preserve the first unclassified box or projection-growth frontier",
    }, "stop contract")

    cells = expected_cells()
    stored_cells = record["cells"]
    by_id = {cell["id"]: cell for cell in stored_cells}
    require(len(by_id) == len(stored_cells) == len(cells) == 81, "cell census/IDs")
    require(Counter(cell["dimension"] for cell in stored_cells) == {0: 25, 1: 40, 2: 16}, "cell dimensions")
    for identifier, expected in cells.items():
        stored = by_id[identifier]
        require(stored["dimension"] == expected["dimension"] and stored["kind"] == expected["kind"], f"cell type {identifier}")
        require(tuple(map(Fraction, stored["witness_branch_coordinates"])) == expected["q_witness"], f"q witness {identifier}")
        require(tuple(map(Fraction, stored["witness_cell_coordinates"])) == expected["x_witness"], f"x witness {identifier}")
        require(tuple(stored["boundary"]) == expected["boundary"], f"boundary {identifier}")
        require(tuple(stored["incident_residual_chambers"]) == expected["incident"], f"incidence {identifier}")

    immediate, closure, chains = closure_data(cells)
    require({tuple(row) for row in record["strict_closure_pairs"]} == closure, "strict closure")
    require({tuple(row) for row in record["strict_three_cell_chains"]} == chains, "strict three-chains")
    require(len(chains) == 128, "barycentric triangle census")

    segments = expected_segments()
    stored_segments = {row["id"]: row for row in record["boundary_word_segments"]}
    require(len(stored_segments) == len(record["boundary_word_segments"]) == len(segments) == 32, "boundary segment census")
    for identifier, (axis, fixed, interval, word, incidents) in segments.items():
        row = stored_segments[identifier]
        require(row["axis"] == axis and int(row["fixed"]) == fixed, f"segment geometry {identifier}")
        require(tuple(map(int, row["interval"])) == interval, f"segment interval {identifier}")
        require(tuple(row["open_segment_sign_word"]) == word, f"segment word {identifier}")
        stored_incidents = tuple((item["box"], item["side"], item["orientation"]) for item in row["incidents"])
        require(stored_incidents == incidents, f"segment incidence {identifier}")
        require(len(incidents) in (1, 2), f"segment incidence count {identifier}")
        if len(incidents) == 2:
            require(incidents[0][2] == -incidents[1][2], f"shared orientation {identifier}")

    boxes = expected_boxes(cells, segments)
    stored_boxes = {row["id"]: row for row in record["boxes"]}
    require(len(stored_boxes) == len(record["boxes"]) == len(boxes) == 9, "box census")
    require(Counter(row["classification"] for row in record["boxes"]) == {"no_wall": 4, "one_wall": 4, "transverse_two_wall": 1}, "box classes")
    cover_multiplicity = Counter()
    for identifier, (q0_bounds, q1_bounds, classification, events, box_closure, words) in boxes.items():
        row = stored_boxes[identifier]
        require(tuple(map(int, row["q0_interval"])) == q0_bounds, f"box q0 {identifier}")
        require(tuple(map(int, row["q1_interval"])) == q1_bounds, f"box q1 {identifier}")
        require(row["classification"] == classification and tuple(row["active_branch_events"]) == events, f"box class {identifier}")
        require(tuple(row["closure_cells"]) == box_closure, f"box closure {identifier}")
        cover_multiplicity.update(box_closure)
        box_cell_set = set(box_closure)
        for high, low in closure:
            if high in box_cell_set:
                require(low in box_cell_set, f"box closure subcomplex {identifier}")
        for side, expected_word in words.items():
            stored_word = tuple((item["segment"], item["orientation"]) for item in row["boundary_words"][side])
            require(stored_word == tuple(expected_word), f"box boundary word {identifier}/{side}")
    require(set(cover_multiplicity) == set(cells), "box cover cell universe")
    require(
        all(cover_multiplicity[identifier] == 1 for identifier, cell in cells.items() if cell["dimension"] == 2),
        "box interiors are not disjoint",
    )

    scope_boundary = expected_subcomplex(
        cells,
        lambda vertices: all(abs(q0) == 3 * AXIS_SCALE or abs(q1) == 3 * AXIS_SCALE for q0, q1 in vertices),
    )
    seam = expected_subcomplex(
        cells,
        lambda vertices: (
            len({q0 for q0, _q1 in vertices}) == 1 and next(iter({q0 for q0, _q1 in vertices})) in (-AXIS_SCALE, AXIS_SCALE)
        ) or (
            len({q1 for _q0, q1 in vertices}) == 1 and next(iter({q1 for _q0, q1 in vertices})) in (-AXIS_SCALE, AXIS_SCALE)
        ),
    )
    residual = expected_subcomplex(
        cells,
        lambda vertices: (
            len({q0 for q0, _q1 in vertices}) == 1 and next(iter({q0 for q0, _q1 in vertices})) == 0
        ) or (
            len({q1 for _q0, q1 in vertices}) == 1 and next(iter({q1 for _q0, q1 in vertices})) == 0
        ),
    )
    for field, expected in (
        ("scope_boundary_subcomplex", scope_boundary),
        ("atlas_seam_subcomplex", seam),
        ("residual_wall_subcomplex", residual),
    ):
        actual = set(record[field])
        require(actual == expected, field)
        for high, low in closure:
            if high in actual:
                require(low in actual, f"{field} closure")
    require(record["parent_infinity_subcomplex"] == [], "false parent infinity")

    source = record["signature_profile_source"]
    require(source["universe_count"] == 97_224 and source["semantic_sha256"] == profile_digest, "signature source")
    profiles = {row["feasible_chamber_mask"]: row for row in source["profiles"]}
    require(tuple(profiles) == tuple(EXPECTED_PROFILE_COUNTS), "profile order")
    bad_by_profile = {}
    for profile, count in EXPECTED_PROFILE_COUNTS.items():
        expected_bad = expected_bad_cells(cells, profile)
        row = profiles[profile]
        require(row["signature_count"] == profile_counts[profile] == count, f"profile count {profile}")
        require(set(row["bad_cells"]) == expected_bad and len(row["bad_cells"]) == len(expected_bad), f"profile bad cells {profile}")
        for high, low in closure:
            if high in expected_bad:
                require(low in expected_bad, f"profile closure {profile}")
        bad_by_profile[profile] = expected_bad

    boundary = record["integral_boundary"]
    expected_boundary = expected_integral_boundary()
    for key in ("c0_basis", "c1_basis", "c2_basis"):
        require(tuple(boundary[key]) == expected_boundary[key], key)
    d1_entries = tuple(tuple(row) for row in boundary["d1_entries"])
    d2_entries = tuple(tuple(row) for row in boundary["d2_entries"])
    require(d1_entries == expected_boundary["d1_entries"], "d1 entries")
    require(d2_entries == expected_boundary["d2_entries"], "d2 entries")
    d1 = {(row, column): int(value) for row, column, value in d1_entries}
    d2 = {(row, column): int(value) for row, column, value in d2_entries}
    for vertex in expected_boundary["c0_basis"]:
        for face in expected_boundary["c2_basis"]:
            require(sum(d1.get((vertex, edge), 0) * d2.get((edge, face), 0) for edge in expected_boundary["c1_basis"]) == 0, "integral d_squared")

    barycentric, indices = barycentric_master(cells, chains)
    require(Counter(len(cell) - 1 for cell in barycentric.cells) == {0: 81, 1: 208, 2: 128}, "barycentric census")
    bary_bad = {
        profile: {
            simplex
            for simplex in barycentric.cells
            if set(simplex) <= {indices[identifier] for identifier in bad_by_profile[profile]}
        }
        for profile in EXPECTED_PROFILE_COUNTS
    }
    histogram = Counter()
    for profile_triple in product(EXPECTED_PROFILE_COUNTS, repeat=3):
        extraction = barycentric.extract(tuple(bary_bad[profile] for profile in profile_triple))
        result = extraction.result()
        require(result[-1] == 0, f"multibox middle residue {profile_triple}")
        histogram[result] += 1
    require(dict(histogram) == EXPECTED_RANK_HISTOGRAM, "multibox rank histogram")
    return histogram


def replay_sources():
    require(file_sha256(NODE) == EXPECTED_NODE_SHA256, "source node hash")
    geometry = node.exact_geometry()
    profile_digest, profile_counts = exact_profile_data()
    return geometry, profile_digest, profile_counts


def assert_rejected(record, sources, label):
    try:
        validate(record, sources)
    except (CertificateError, KeyError, ValueError, TypeError):
        return
    raise AssertionError(f"hostile canary was accepted: {label}")


def main():
    record = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    sources = replay_sources()
    histogram = validate(record, sources)

    corrupt = copy.deepcopy(record)
    corrupt["coverage_evidence"]["kind"] = "sample_bank"
    assert_rejected(corrupt, sources, "sample bank as coverage")

    corrupt = copy.deepcopy(record)
    corrupt["coverage_evidence"]["axis_scale"] = str(100 * AXIS_SCALE)
    assert_rejected(corrupt, sources, "unsigned domain expansion")

    corrupt = copy.deepcopy(record)
    corrupt["boxes"].pop()
    assert_rejected(corrupt, sources, "missing atlas box")

    corrupt = copy.deepcopy(record)
    corrupt["boundary_word_segments"][0]["open_segment_sign_word"][0] *= -1
    assert_rejected(corrupt, sources, "corrupt boundary sign word")

    corrupt = copy.deepcopy(record)
    corrupt["parent_infinity_subcomplex"] = corrupt["scope_boundary_subcomplex"][:3]
    assert_rejected(corrupt, sources, "scope boundary as parent infinity")

    corrupt = copy.deepcopy(record)
    corrupt["strict_closure_pairs"].pop()
    assert_rejected(corrupt, sources, "incomplete strict closure")

    corrupt = copy.deepcopy(record)
    corrupt["signature_profile_source"]["profiles"][0]["signature_count"] -= 1
    assert_rejected(corrupt, sources, "incomplete signature accounting")

    corrupt = copy.deepcopy(record)
    corrupt["inputs"]["candidate_factor_sha256"] = "0" * 64
    assert_rejected(corrupt, sources, "corrupt active-factor input")

    corrupt = copy.deepcopy(record)
    corrupt["integral_boundary"]["d2_entries"][0][2] *= -1
    assert_rejected(corrupt, sources, "nonzero d_squared")

    corrupt = copy.deepcopy(record)
    corrupt["stop_contract"]["used_boxes"] = 8
    assert_rejected(corrupt, sources, "dishonest stop ledger")

    print("PASS exact row-2599 3x3 full-support multi-box canary")
    print("PASS 9 boxes: 4 no-wall + 4 one-wall + 1 transverse two-wall")
    print("PASS 32 atomic boundary words and 16 shared-segment gluings")
    print("PASS 81-cell regular CW atlas: 25 vertices, 40 edges, 16 chambers")
    print("PASS 81/208/128 barycentric cells and all 216 profile triples have H1=0")
    print("RANK_HISTOGRAM", dict(sorted(histogram.items())))
    print("PASS 10/10 hostile corruptions rejected")
    print("SCOPE complete on one bounded 2D multibox atlas; no full 9D coverage claim")


if __name__ == "__main__":
    main()
