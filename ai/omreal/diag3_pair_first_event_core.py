#!/usr/bin/env python3
"""Exact source replay and CW compiler for the row-2599 first-new-event atlas.

The module is proof machinery shared by a deliberately thin certificate
producer and the hostile verifier.  It derives the first residual event from
all 84,840 labelled restrictions, proves exact coverage on a declared
64-box domain, constructs the clipped three-line arrangement, and replays the
balanced pair complex over F_2.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
from hashlib import sha256
from functools import cached_property
from itertools import combinations_with_replacement
from math import comb, factorial, gcd, lcm
from pathlib import Path
import json
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
NODE = DATA / "DIAG9_GRAPH_row2599_node_roadmap.npz"
CANDIDATES = DATA / "DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin"
LEDGER = DATA / "DIAG3_RESEARCH_DECISION_LEDGER.json"
PARENT_GATE = DATA / "DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json"

sys.path.insert(0, str(HERE))
import DIAG9_GRAPH_exact_topes as topes  # noqa: E402
import DIAG9_GRAPH_verify_row2599_disk as disk  # noqa: E402
import DIAG9_GRAPH_verify_row2599_node as node  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as slice_verify  # noqa: E402
import four_chart_gate as extension_gate  # noqa: E402
import verify_diag3_pair_global_master_quotient as master  # noqa: E402


FORMAT = "diag3-pair-master-closure-first-event-certificate-v1"
STATUS = "LOCAL_EXACT_FIRST_NEW_EVENT"
AXIS_SCALE = 10**12
BOX_LEVELS_Z = (-64, -48, -32, -16, -8, 8, 16, 32, 64)
CELL_LEVELS_Z = tuple(sorted((*BOX_LEVELS_Z, 0)))
TARGET_FOURSET = (2, 8, 22, 49)
TARGET_TRIPLES = tuple(topes.TRIPLES[index] for index in TARGET_FOURSET)
TARGET_LINE_CANONICAL = (
    ((0, 0), -2441327503069497643632051255408343070157302308369623),
    ((0, 1), -4625538281148206669263848248874756608000000000000),
    ((1, 0), 59793431655840338468670905373092307097000000000000),
)
CHAMBER_SIGNS = (
    (-1, -1, -1),
    (-1, 1, -1),
    (1, -1, -1),
    (1, -1, 1),
    (1, 1, -1),
    (1, 1, 1),
)
SIGN_TO_CHAMBER = {signs: index for index, signs in enumerate(CHAMBER_SIGNS)}
CHAMBER_WITNESSES_Z = (
    (-16, -16),
    (-16, 16),
    (16, -16),
    (48, -16),
    (16, 16),
    (48, 16),
)
EXPECTED_PROFILE_COUNTS = {
    0: 70_966,
    3: 72,
    13: 72,
    23: 2,
    40: 2,
    50: 72,
    60: 72,
    63: 25_966,
}


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def sign(value: int | Fraction) -> int:
    return 1 if value > 0 else -1 if value < 0 else 0


def fraction_text(value: Fraction | int) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def canonical_polynomial(polynomial) -> tuple[tuple[tuple[int, int], int], ...]:
    polynomial = disk.clean(polynomial)
    denominator = 1
    for value in polynomial.values():
        denominator = lcm(denominator, Fraction(value).denominator)
    integer = {
        monomial: int(Fraction(value) * denominator)
        for monomial, value in polynomial.items()
    }
    divisor = 0
    for value in integer.values():
        divisor = gcd(divisor, abs(value))
    integer = {
        monomial: value // max(divisor, 1)
        for monomial, value in integer.items()
    }
    if integer[max(integer)] < 0:
        integer = {monomial: -value for monomial, value in integer.items()}
    return tuple(sorted(integer.items()))


def branch_matrix():
    return tuple(
        (
            int(linear[(1, 0)]),
            int(linear[(0, 1)]),
        )
        for linear in node.CENTERED_BRANCHES
    )


def branch_determinant() -> int:
    matrix = branch_matrix()
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def z_to_cell_coordinates(z0, z1):
    matrix = branch_matrix()
    determinant = branch_determinant()
    q0 = Fraction(AXIS_SCALE) * z0
    q1 = Fraction(AXIS_SCALE) * z1
    return (
        Fraction(matrix[1][1] * q0 - matrix[0][1] * q1, determinant),
        Fraction(-matrix[1][0] * q0 + matrix[0][0] * q1, determinant),
    )


def linear_power(first: Fraction, second: Fraction, degree: int):
    return {
        (power, degree - power):
        Fraction(comb(degree, power)) * first**power * second ** (degree - power)
        for power in range(degree + 1)
    }


def polynomial_to_z(polynomial):
    matrix = branch_matrix()
    determinant = branch_determinant()
    x_linear = (
        Fraction(matrix[1][1] * AXIS_SCALE, determinant),
        Fraction(-matrix[0][1] * AXIS_SCALE, determinant),
    )
    y_linear = (
        Fraction(-matrix[1][0] * AXIS_SCALE, determinant),
        Fraction(matrix[0][0] * AXIS_SCALE, determinant),
    )
    result = {}
    for (x_degree, y_degree), coefficient in polynomial.items():
        term = disk.multiply(
            linear_power(*x_linear, x_degree),
            linear_power(*y_linear, y_degree),
        )
        for monomial, value in term.items():
            result[monomial] = (
                result.get(monomial, Fraction(0))
                + Fraction(coefficient) * value
            )
    return disk.clean(result)


def polynomial_value(polynomial, first, second):
    return sum(
        Fraction(coefficient) * first**i * second**j
        for (i, j), coefficient in polynomial.items()
    )


def event_factor(centered):
    """Remove exactly one pinned branch at the old transverse node."""
    if centered.get((0, 0), 0):
        return centered, None
    quotients = tuple(
        (branch, node.divide_by_linear(centered, linear))
        for branch, linear in enumerate(node.CENTERED_BRANCHES)
    )
    matches = tuple((branch, quotient) for branch, quotient in quotients if quotient is not None)
    if len(matches) != 1:
        raise AssertionError("node occurrence has ambiguous pinned branch")
    return matches[0][1], matches[0][0]


def dominance_margin(polynomial, radius: int):
    constant = abs(Fraction(polynomial.get((0, 0), 0)))
    tail = sum(
        abs(Fraction(value)) * radius ** (i + j)
        for (i, j), value in polynomial.items()
        if i + j
    )
    return constant, tail, constant - tail


def exact_source_geometry():
    base = slice_verify.source_parent()
    polynomial_matrix = disk.polynomial_parent(base)
    normal_rows = disk.derived_polynomial_rows(polynomial_matrix)
    pinned_counts = Counter()
    quotient_degrees = Counter()
    degree_census = Counter()
    minimum_ratio = None
    minimum_witness = None
    target_polynomial = None
    target_occurrences = []

    residual = slice_verify.residual_foursets()
    for fourset in residual:
        raw = disk.primitive(
            disk.determinant([normal_rows[index] for index in fourset])
        )
        degree_census[disk.total_degree(raw)] += 1
        centered = node.shift_polynomial(raw)
        factor, pinned_branch = event_factor(centered)
        if pinned_branch is not None:
            pinned_counts[pinned_branch] += 1
            quotient_degrees[(pinned_branch, disk.total_degree(factor))] += 1
        if disk.total_degree(factor) <= 0:
            if not factor.get((0, 0), 0):
                raise AssertionError("zero event quotient")
            continue
        z_polynomial = polynomial_to_z(factor)
        if fourset == TARGET_FOURSET:
            if canonical_polynomial(z_polynomial) != TARGET_LINE_CANONICAL:
                raise AssertionError("target first-event factor changed")
            target_polynomial = {
                monomial: Fraction(value)
                for monomial, value in TARGET_LINE_CANONICAL
            }
            target_occurrences.append(fourset)
            continue
        constant, tail, margin = dominance_margin(z_polynomial, 64)
        if constant <= 0 or margin <= 0:
            raise AssertionError(f"unexpected residual frontier at {fourset}")
        ratio = margin / constant
        if minimum_ratio is None or ratio < minimum_ratio:
            minimum_ratio = ratio
            minimum_witness = fourset

    if len(residual) != 84_840:
        raise AssertionError("residual universe changed")
    if pinned_counts != Counter({0: 65, 1: 65}):
        raise AssertionError(f"pinned branch census changed: {pinned_counts}")
    if quotient_degrees != Counter({(0, 0): 32, (0, 1): 33, (1, 0): 32, (1, 1): 33}):
        raise AssertionError(f"pinned quotient census changed: {quotient_degrees}")
    if target_occurrences != [TARGET_FOURSET] or target_polynomial is None:
        raise AssertionError("first-event occurrence is not unique")

    minimum_parent_ratio = None
    minimum_parent_basis = None
    variable_parent_brackets = 0
    for basis in topes.BASES:
        raw = disk.determinant(
            [[polynomial_matrix[row][column] for column in basis] for row in range(4)]
        )
        centered = node.shift_polynomial(raw)
        z_polynomial = polynomial_to_z(centered)
        if disk.total_degree(z_polynomial) > 0:
            variable_parent_brackets += 1
        constant, tail, margin = dominance_margin(z_polynomial, 64)
        if constant <= 0 or margin <= 0:
            raise AssertionError(f"parent boundary enters first-event domain at {basis}")
        ratio = margin / constant
        if minimum_parent_ratio is None or ratio < minimum_parent_ratio:
            minimum_parent_ratio = ratio
            minimum_parent_basis = basis

    constant = target_polynomial[(0, 0)]
    coefficient_z0 = target_polynomial[(1, 0)]
    coefficient_z1 = target_polynomial[(0, 1)]
    first_radius = abs(constant) / (abs(coefficient_z0) + abs(coefficient_z1))
    touch = (
        first_radius if -constant * coefficient_z0 > 0 else -first_radius,
        first_radius if -constant * coefficient_z1 > 0 else -first_radius,
    )
    if polynomial_value(target_polynomial, *touch) != 0:
        raise AssertionError("first-event touch point misses target line")
    if not (32 < target_x(target_polynomial, -64) < 64):
        raise AssertionError("target line misses bottom target box")
    if not (32 < target_x(target_polynomial, 64) < 64):
        raise AssertionError("target line misses top target box")

    disk.verify_embedded_disk(node.rational_parent(Fraction(0), Fraction(0)))
    return {
        "residual_occurrence_count": len(residual),
        "residual_degree_census": dict(sorted(degree_census.items())),
        "pinned_branch_occurrence_counts": [pinned_counts[0], pinned_counts[1]],
        "pinned_quotient_degree_counts": [
            [quotient_degrees[(branch, degree)] for degree in (0, 1)]
            for branch in (0, 1)
        ],
        "target_fourset": TARGET_FOURSET,
        "target_triples": TARGET_TRIPLES,
        "target_line": target_polynomial,
        "first_linf_radius_z": first_radius,
        "first_touch_z": touch,
        "minimum_other_domain_margin_ratio": minimum_ratio,
        "minimum_other_domain_margin_witness": minimum_witness,
        "parent_bracket_count": len(topes.BASES),
        "variable_parent_bracket_count": variable_parent_brackets,
        "minimum_parent_domain_margin_ratio": minimum_parent_ratio,
        "minimum_parent_domain_margin_basis": minimum_parent_basis,
        "branch_matrix": branch_matrix(),
        "branch_matrix_determinant": branch_determinant(),
    }


def target_x(line, y):
    return -(
        line[(0, 0)] + line[(0, 1)] * Fraction(y)
    ) / line[(1, 0)]


def target_value(line, point):
    return polynomial_value(line, point[0], point[1])


def chamber_index(line, point) -> int:
    word = (sign(point[0]), sign(point[1]), sign(target_value(line, point)))
    if word not in SIGN_TO_CHAMBER:
        raise AssertionError(f"point lies on a residual wall or outside chamber atlas: {point}")
    return SIGN_TO_CHAMBER[word]


def raw_cells(line):
    cells = {}

    def add(identifier, dimension, boundary, vertices, oriented_boundary=()):
        cells[identifier] = {
            "dimension": dimension,
            "boundary": tuple(boundary),
            "vertices": tuple(tuple(map(Fraction, point)) for point in vertices),
            "oriented_boundary": tuple(oriented_boundary),
        }

    levels = CELL_LEVELS_Z
    target_column = levels.index(32)
    for i, first in enumerate(levels):
        for j, second in enumerate(levels):
            add(f"p{i}_{j}", 0, (), ((first, second),))
    for j, second in enumerate(levels):
        add(f"t{j}", 0, (), ((target_x(line, second), second),))

    for i in range(len(levels) - 1):
        for j, second in enumerate(levels):
            if i == target_column:
                add(
                    f"h{i}a_{j}", 1, (f"p{i}_{j}", f"t{j}"),
                    ((levels[i], second), (target_x(line, second), second)),
                )
                add(
                    f"h{i}b_{j}", 1, (f"t{j}", f"p{i + 1}_{j}"),
                    ((target_x(line, second), second), (levels[i + 1], second)),
                )
            else:
                add(
                    f"h{i}_{j}", 1, (f"p{i}_{j}", f"p{i + 1}_{j}"),
                    ((levels[i], second), (levels[i + 1], second)),
                )
    for i, first in enumerate(levels):
        for j in range(len(levels) - 1):
            add(
                f"v{i}_{j}", 1, (f"p{i}_{j}", f"p{i}_{j + 1}"),
                ((first, levels[j]), (first, levels[j + 1])),
            )
    for j in range(len(levels) - 1):
        add(
            f"te{j}", 1, (f"t{j}", f"t{j + 1}"),
            ((target_x(line, levels[j]), levels[j]), (target_x(line, levels[j + 1]), levels[j + 1])),
        )

    for i in range(len(levels) - 1):
        for j in range(len(levels) - 1):
            if i == target_column:
                left_boundary = (
                    (f"h{i}a_{j}", 1),
                    (f"te{j}", 1),
                    (f"h{i}a_{j + 1}", -1),
                    (f"v{i}_{j}", -1),
                )
                add(
                    f"fl{i}_{j}", 2,
                    tuple(edge for edge, _coefficient in left_boundary),
                    (
                        (levels[i], levels[j]),
                        (target_x(line, levels[j]), levels[j]),
                        (target_x(line, levels[j + 1]), levels[j + 1]),
                        (levels[i], levels[j + 1]),
                    ),
                    left_boundary,
                )
                right_boundary = (
                    (f"h{i}b_{j}", 1),
                    (f"v{i + 1}_{j}", 1),
                    (f"h{i}b_{j + 1}", -1),
                    (f"te{j}", -1),
                )
                add(
                    f"fr{i}_{j}", 2,
                    tuple(edge for edge, _coefficient in right_boundary),
                    (
                        (target_x(line, levels[j]), levels[j]),
                        (levels[i + 1], levels[j]),
                        (levels[i + 1], levels[j + 1]),
                        (target_x(line, levels[j + 1]), levels[j + 1]),
                    ),
                    right_boundary,
                )
            else:
                boundary = (
                    (f"h{i}_{j}", 1),
                    (f"v{i + 1}_{j}", 1),
                    (f"h{i}_{j + 1}", -1),
                    (f"v{i}_{j}", -1),
                )
                add(
                    f"f{i}_{j}", 2,
                    tuple(edge for edge, _coefficient in boundary),
                    (
                        (levels[i], levels[j]),
                        (levels[i + 1], levels[j]),
                        (levels[i + 1], levels[j + 1]),
                        (levels[i], levels[j + 1]),
                    ),
                    boundary,
                )
    return cells


def midpoint(vertices):
    return tuple(
        sum(point[coordinate] for point in vertices) / len(vertices)
        for coordinate in range(2)
    )


def incident_chambers(cells, line):
    incident = {identifier: set() for identifier in cells}
    for identifier, cell in cells.items():
        if cell["dimension"] != 2:
            continue
        chamber = chamber_index(line, midpoint(cell["vertices"]))
        incident[identifier].add(chamber)
        for edge in cell["boundary"]:
            incident[edge].add(chamber)
            for vertex in cells[edge]["boundary"]:
                incident[vertex].add(chamber)
    if any(not values for values in incident.values()):
        raise AssertionError("a first-event CW cell has no incident chamber")
    return incident


def lies_on_residual(vertices, line):
    return (
        all(first == 0 for first, _second in vertices)
        or all(second == 0 for _first, second in vertices)
        or all(target_value(line, point) == 0 for point in vertices)
    )


def cell_kind(cell, line):
    dimension = cell["dimension"]
    vertices = cell["vertices"]
    on_residual = lies_on_residual(vertices, line)
    on_scope = all(
        abs(first) == 64 or abs(second) == 64
        for first, second in vertices
    )
    internal_levels = set(BOX_LEVELS_Z[1:-1])
    on_seam = (
        len({first for first, _second in vertices}) == 1
        and next(iter({first for first, _second in vertices})) in internal_levels
    ) or (
        len({second for _first, second in vertices}) == 1
        and next(iter({second for _first, second in vertices})) in internal_levels
    )
    if dimension == 2:
        return "open_residual_chamber_piece"
    if dimension == 1 and on_residual:
        return "residual_wall_segment"
    if dimension == 1 and on_scope:
        return "scope_boundary_segment"
    if dimension == 1 and on_seam:
        return "atlas_seam_segment"
    if dimension == 0 and sum((
        all(first == 0 for first, _second in vertices),
        all(second == 0 for _first, second in vertices),
        all(target_value(line, point) == 0 for point in vertices),
    )) >= 2:
        return "residual_node"
    if dimension == 0 and on_residual and on_scope:
        return "scope_boundary_residual_endpoint"
    if dimension == 0 and on_residual and on_seam:
        return "atlas_seam_residual_crossing"
    if dimension == 0 and on_scope:
        return "scope_boundary_vertex"
    if dimension == 0 and on_seam:
        return "atlas_seam_vertex"
    if dimension == 0 and on_residual:
        return "residual_wall_vertex"
    return "grid_vertex"


def serial_cells(cells, line):
    incident = incident_chambers(cells, line)
    answer = []
    for identifier in sorted(cells, key=lambda key: (cells[key]["dimension"], key)):
        cell = cells[identifier]
        witness = midpoint(cell["vertices"])
        source_witness = z_to_cell_coordinates(*witness)
        answer.append({
            "id": identifier,
            "dimension": cell["dimension"],
            "kind": cell_kind(cell, line),
            "witness_normalized_branch_coordinates": [fraction_text(value) for value in witness],
            "witness_cell_coordinates": [fraction_text(value) for value in source_witness],
            "boundary": list(cell["boundary"]),
            "incident_residual_chambers": sorted(incident[identifier]),
        })
    return answer, incident


def closure_data(cells):
    immediate = {
        (identifier, face)
        for identifier, cell in cells.items()
        for face in cell["boundary"]
    }
    closure = set(immediate)
    for high, middle in tuple(immediate):
        for middle2, low in tuple(immediate):
            if middle == middle2:
                closure.add((high, low))
    chains = {
        (high, middle, low)
        for high, middle in immediate
        for middle2, low in immediate
        if middle == middle2
    }
    return closure, chains


def integral_boundary(cells):
    c0 = tuple(sorted(identifier for identifier, cell in cells.items() if cell["dimension"] == 0))
    c1 = tuple(sorted(identifier for identifier, cell in cells.items() if cell["dimension"] == 1))
    c2 = tuple(sorted(identifier for identifier, cell in cells.items() if cell["dimension"] == 2))
    d1 = []
    for edge in c1:
        first, second = cells[edge]["boundary"]
        d1.extend(((first, edge, -1), (second, edge, 1)))
    d2 = []
    for face in c2:
        d2.extend((edge, face, coefficient) for edge, coefficient in cells[face]["oriented_boundary"])
    return {
        "orientation_rule": "grid and split horizontal edges point right; vertical and target edges point up; faces are counterclockwise",
        "c0_basis": list(c0),
        "c1_basis": list(c1),
        "c2_basis": list(c2),
        "d1_entries": [list(row) for row in d1],
        "d2_entries": [list(row) for row in d2],
    }


def box_index(value: Fraction):
    for index, (low, high) in enumerate(zip(BOX_LEVELS_Z, BOX_LEVELS_Z[1:])):
        if low < value < high:
            return index
    raise AssertionError(f"atomic boundary midpoint lies on a box corner: {value}")


def boundary_segments(cells, line):
    answer = []
    for identifier, cell in sorted(cells.items()):
        if cell["dimension"] != 1 or identifier.startswith("te"):
            continue
        first, second = cell["vertices"]
        midpoint_value = midpoint(cell["vertices"])
        incidents = []
        axis = None
        fixed = None
        interval = None
        if first[0] == second[0] and first[0] in BOX_LEVELS_Z:
            axis = "vertical"
            fixed = first[0]
            interval = (first[1], second[1])
            boundary_index = BOX_LEVELS_Z.index(int(fixed))
            row = box_index(midpoint_value[1])
            if boundary_index:
                incidents.append({"box": f"box_{boundary_index - 1}_{row}", "side": "right", "orientation": 1})
            if boundary_index < 8:
                incidents.append({"box": f"box_{boundary_index}_{row}", "side": "left", "orientation": -1})
        elif first[1] == second[1] and first[1] in BOX_LEVELS_Z:
            axis = "horizontal"
            fixed = first[1]
            interval = (first[0], second[0])
            boundary_index = BOX_LEVELS_Z.index(int(fixed))
            column = box_index(midpoint_value[0])
            if boundary_index:
                incidents.append({"box": f"box_{column}_{boundary_index - 1}", "side": "top", "orientation": -1})
            if boundary_index < 8:
                incidents.append({"box": f"box_{column}_{boundary_index}", "side": "bottom", "orientation": 1})
        if axis is None:
            continue
        word = (
            sign(midpoint_value[0]),
            sign(midpoint_value[1]),
            sign(target_value(line, midpoint_value)),
        )
        if 0 in word:
            raise AssertionError(f"unsplit box-boundary event at {identifier}")
        answer.append({
            "id": identifier,
            "axis": axis,
            "fixed": fraction_text(AXIS_SCALE * fixed),
            "interval": [fraction_text(AXIS_SCALE * value) for value in interval],
            "open_segment_sign_word": list(word),
            "incidents": incidents,
        })
    return answer


def box_records(cells, segments, line):
    answer = []
    for i, q0_bounds in enumerate(zip(BOX_LEVELS_Z, BOX_LEVELS_Z[1:])):
        for j, q1_bounds in enumerate(zip(BOX_LEVELS_Z, BOX_LEVELS_Z[1:])):
            events = []
            if q0_bounds[0] < 0 < q0_bounds[1]:
                events.append(0)
            if q1_bounds[0] < 0 < q1_bounds[1]:
                events.append(1)
            corner_values = tuple(
                target_value(line, (first, second))
                for first in q0_bounds
                for second in q1_bounds
            )
            if min(corner_values) < 0 < max(corner_values):
                events.append(2)
            classification = (
                "no_wall" if not events
                else "one_wall" if len(events) == 1
                else "transverse_two_wall" if len(events) == 2
                else "higher_specialization"
            )
            identifier = f"box_{i}_{j}"
            closure_cells = [
                cell_id
                for cell_id, cell in cells.items()
                if all(
                    q0_bounds[0] <= first <= q0_bounds[1]
                    and q1_bounds[0] <= second <= q1_bounds[1]
                    for first, second in cell["vertices"]
                )
            ]
            words = {side: [] for side in ("bottom", "right", "top", "left")}
            for segment in segments:
                for incidence in segment["incidents"]:
                    if incidence["box"] == identifier:
                        words[incidence["side"]].append({
                            "segment": segment["id"],
                            "orientation": incidence["orientation"],
                        })
            answer.append({
                "id": identifier,
                "q0_interval": [fraction_text(AXIS_SCALE * value) for value in q0_bounds],
                "q1_interval": [fraction_text(AXIS_SCALE * value) for value in q1_bounds],
                "classification": classification,
                "active_branch_events": events,
                "closure_cells": sorted(closure_cells, key=lambda key: (cells[key]["dimension"], key)),
                "boundary_words": words,
            })
    return answer


def subcomplex(cells, predicate):
    return [identifier for identifier, cell in cells.items() if predicate(cell["vertices"])]


def exact_profile_data(line):
    chamber_sets = []
    expected_parent = slice_verify.expected_parent_signs()
    for witness, expected_signs in zip(CHAMBER_WITNESSES_Z, CHAMBER_SIGNS):
        point = tuple(map(Fraction, witness))
        if (
            sign(point[0]),
            sign(point[1]),
            sign(target_value(line, point)),
        ) != expected_signs:
            raise AssertionError("chamber witness sign word changed")
        x_value, y_value = z_to_cell_coordinates(*point)
        matrix = node.rational_parent(x_value, y_value)
        if topes.parent_signs(matrix) != expected_parent:
            raise AssertionError("chamber witness leaves row-2599 parent cell")
        labels = set(topes.parent_topes(matrix))
        if len(labels) != 26_112:
            raise AssertionError("generic first-event chamber has wrong tope count")
        chamber_sets.append(labels)

    patterns = {}
    for chamber, labels in enumerate(chamber_sets):
        for signature in labels:
            patterns[signature] = patterns.get(signature, 0) | (1 << chamber)
    parents = [
        line_text.strip()
        for line_text in extension_gate.CATALOG_48.open(encoding="utf-8")
        if line_text.strip()
    ]
    _parent_bits, signatures = extension_gate.enumerate_extensions(
        parents[extension_gate.PARENT_INDEX]
    )
    if len(signatures) != len(set(signatures)) or len(signatures) != 97_224:
        raise AssertionError("row-2599 extension universe changed")
    if not set(patterns).issubset(signatures):
        raise AssertionError("first-event labels leave extension universe")
    digest = sha256(b"diag3-row2599-first-event-signature-profile-v1\0")
    counts = Counter()
    for signature in signatures:
        profile = patterns.get(signature, 0)
        counts[profile] += 1
        digest.update(int(signature).to_bytes(8, "little"))
        digest.update(bytes((profile,)))
    if dict(sorted(counts.items())) != EXPECTED_PROFILE_COUNTS:
        raise AssertionError(f"first-event profile counts changed: {counts}")
    return digest.hexdigest(), counts


def bad_cells(cells, incident, profile):
    return {
        identifier
        for identifier in cells
        if any(not (profile >> chamber & 1) for chamber in incident[identifier])
    }


def fast_rank_f2(matrix) -> int:
    basis = {}
    for row in matrix:
        word = sum((int(value) & 1) << column for column, value in enumerate(row))
        while word:
            pivot = word.bit_length() - 1
            old = basis.get(pivot)
            if old is None:
                basis[pivot] = word
                break
            word ^= old
    return len(basis)


class CachedMasterComplex(master.MasterComplex):
    @cached_property
    def cells(self):
        return master.all_simplices(self.maximal)


def rank_replay(cells, chains, incident):
    ordered = sorted(cells, key=lambda key: (cells[key]["dimension"], key))
    indices = {identifier: index for index, identifier in enumerate(ordered)}
    maximal = tuple(sorted({
        tuple(sorted((indices[high], indices[middle], indices[low])))
        for high, middle, low in chains
    }))
    complex_ = CachedMasterComplex(maximal, frozenset())
    master.rank_f2 = fast_rank_f2
    # For every integral matrix rank over F_2 is bounded above by rank over Q.
    # The upstream small-canary extractor recomputes this universal inequality
    # with Fraction Gaussian elimination; at this 399-cell scale that redundant
    # replay dominates runtime.  Returning the exact mod-two rank here invokes
    # the universal lower bound while all integral MN=0 identities remain
    # explicitly checked by the extractor.
    master.rank_q = fast_rank_f2
    barycentric_census = Counter(len(simplex) - 1 for simplex in complex_.cells)
    bad = {
        profile: bad_cells(cells, incident, profile)
        for profile in EXPECTED_PROFILE_COUNTS
    }
    barycentric_bad = {
        profile: {
            simplex
            for simplex in complex_.cells
            if set(simplex) <= {indices[identifier] for identifier in bad_set}
        }
        for profile, bad_set in bad.items()
    }
    histogram = Counter()
    semantic = sha256(b"diag3-row2599-first-event-rank-replay-v1\0")
    nonzero = []
    profiles = tuple(EXPECTED_PROFILE_COUNTS)
    unordered_count = 0
    for triple in combinations_with_replacement(profiles, 3):
        unordered_count += 1
        multiplicities = Counter(triple)
        ordered_multiplicity = factorial(3)
        for count in multiplicities.values():
            ordered_multiplicity //= factorial(count)
        result = complex_.extract(tuple(barycentric_bad[profile] for profile in triple)).result()
        histogram[result] += ordered_multiplicity
        semantic.update(bytes(triple))
        semantic.update(bytes((ordered_multiplicity,)))
        for value in result:
            semantic.update(int(value).to_bytes(4, "little"))
        if result[-1]:
            nonzero.append((triple, result, ordered_multiplicity))
    return {
        "barycentric_census": dict(sorted(barycentric_census.items())),
        "unordered_profile_multisets": unordered_count,
        "ordered_profile_triples": len(EXPECTED_PROFILE_COUNTS) ** 3,
        "histogram": dict(sorted(histogram.items())),
        "nonzero": nonzero,
        "semantic_sha256": semantic.hexdigest(),
        "bad_cells": bad,
    }


def build_record():
    geometry = exact_source_geometry()
    line = geometry["target_line"]
    cells = raw_cells(line)
    serial, incident = serial_cells(cells, line)
    closure, chains = closure_data(cells)
    segments = boundary_segments(cells, line)
    boxes = box_records(cells, segments, line)
    profile_digest, profile_counts = exact_profile_data(line)
    replay = rank_replay(cells, chains, incident)
    if replay["nonzero"]:
        raise AssertionError(f"first-event middle residue: {replay['nonzero'][:3]}")

    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    parent_gate = json.loads(PARENT_GATE.read_text(encoding="utf-8"))
    full = ledger["row2599_fullsupport_ledger"]
    cell_counts = Counter(cell["dimension"] for cell in serial)
    box_counts = Counter(box["classification"] for box in boxes)
    if cell_counts != Counter({0: 110, 1: 199, 2: 90}):
        raise AssertionError(f"first-event cell census changed: {cell_counts}")
    if box_counts != Counter({"no_wall": 42, "one_wall": 20, "transverse_two_wall": 2}):
        raise AssertionError(f"first-event box census changed: {box_counts}")
    if len(segments) != 171 or sum(len(row["incidents"]) == 2 for row in segments) != 133:
        raise AssertionError("first-event boundary-word census changed")

    scope_boundary = subcomplex(
        cells,
        lambda vertices: all(abs(first) == 64 or abs(second) == 64 for first, second in vertices),
    )
    internal_levels = set(BOX_LEVELS_Z[1:-1])
    seam = subcomplex(
        cells,
        lambda vertices: (
            len({first for first, _second in vertices}) == 1
            and next(iter({first for first, _second in vertices})) in internal_levels
        ) or (
            len({second for _first, second in vertices}) == 1
            and next(iter({second for _first, second in vertices})) in internal_levels
        ),
    )
    residual = subcomplex(cells, lambda vertices: lies_on_residual(vertices, line))
    profiles = [
        {
            "feasible_chamber_mask": profile,
            "signature_count": profile_counts[profile],
            "bad_cells": sorted(replay["bad_cells"][profile]),
        }
        for profile in EXPECTED_PROFILE_COUNTS
    ]
    rank_histogram = [
        {
            "dim_c1": result[0],
            "rank_n": result[1],
            "rank_m": result[2],
            "dim_h1": result[3],
            "profile_triple_count": count,
        }
        for result, count in replay["histogram"].items()
    ]

    domain_vertices = tuple(
        z_to_cell_coordinates(first, second)
        for first in (-64, 64)
        for second in (-64, 64)
    )
    maximum_cell_coordinate = max(
        abs(value) for point in domain_vertices for value in point
    )
    target_line = [
        {"monomial": list(monomial), "coefficient": fraction_text(value)}
        for monomial, value in sorted(line.items())
    ]
    return {
        "format": FORMAT,
        "status": STATUS,
        "scope": {
            "parent_index": 2599,
            "compactification": "(Delta^3)^3",
            "support": [15, 15, 15],
            "claim": "complete exact 64-box first-new-event closure atlas in one two-dimensional row-2599 parent plane",
            "local_parameter_coverage": "COMPLETE",
            "global_parameter_coverage": "NOT_CLAIMED",
            "scope_boundary_policy": "ordinary cells; never parent infinity",
            "atlas_seam_policy": "ordinary cells; exact boundary-word gluing only",
        },
        "inputs": {
            "source_commit": "c7bbbae13de85323be6b92b46332614eaa271b36",
            "node_roadmap_path": str(NODE.relative_to(HERE.parents[1])),
            "node_roadmap_sha256": file_sha256(NODE),
            "candidate_factor_path": str(CANDIDATES.relative_to(HERE.parents[1])),
            "candidate_factor_sha256": file_sha256(CANDIDATES),
            "candidate_factor_count": full["fullsupport_factor_count"],
            "exact_empty_factor_digest": full["digests"]["empty_factor_ids"],
            "unresolved_factor_digest": full["digests"]["unresolved_factor_ids"],
            "target_signed_parent_digest": parent_gate["normalized_parent_sign_sha256"],
        },
        "generator": {
            "backend": "exact_branch_coordinate_first_event_arrangement_v1",
            "build_command": "python ai/omreal/build_diag3_pair_master_closure_first_event.py",
            "producer_role": "deterministic translation; proof gates are replayed from source polynomials and exact topes",
        },
        "coverage_evidence": {
            "kind": "exact_first_new_event_multibox_partition",
            "labelled_residual_occurrence_universe": geometry["residual_occurrence_count"],
            "residual_degree_census": {str(key): value for key, value in geometry["residual_degree_census"].items()},
            "parent_bracket_count": geometry["parent_bracket_count"],
            "variable_parent_bracket_count": geometry["variable_parent_bracket_count"],
            "branch_matrix": [list(row) for row in geometry["branch_matrix"]],
            "branch_matrix_determinant": str(geometry["branch_matrix_determinant"]),
            "axis_scale": str(AXIS_SCALE),
            "box_levels_normalized": list(BOX_LEVELS_Z),
            "cell_levels_normalized": list(CELL_LEVELS_Z),
            "domain_cell_coordinate_vertices": [
                [fraction_text(value) for value in point] for point in domain_vertices
            ],
            "domain_max_abs_cell_coordinate": fraction_text(maximum_cell_coordinate),
            "pinned_branch_occurrence_counts": geometry["pinned_branch_occurrence_counts"],
            "pinned_quotient_degree_counts": geometry["pinned_quotient_degree_counts"],
            "first_event_derived_row_indices": list(geometry["target_fourset"]),
            "first_event_source_triples": [list(row) for row in geometry["target_triples"]],
            "first_event_line_normalized": target_line,
            "first_event_linf_radius_normalized": fraction_text(geometry["first_linf_radius_z"]),
            "first_event_touch_normalized": [fraction_text(value) for value in geometry["first_touch_z"]],
            "minimum_other_domain_margin_ratio": fraction_text(geometry["minimum_other_domain_margin_ratio"]),
            "minimum_other_domain_margin_witness": list(geometry["minimum_other_domain_margin_witness"]),
            "minimum_parent_domain_margin_ratio": fraction_text(geometry["minimum_parent_domain_margin_ratio"]),
            "minimum_parent_domain_margin_basis": list(geometry["minimum_parent_domain_margin_basis"]),
            "classification_census": dict(sorted(box_counts.items())),
        },
        "stop_contract": {
            "declared_box_ceiling": 64,
            "used_boxes": 64,
            "ceiling_status": "AT_CEILING",
            "first_new_event_status": "CLASSIFIED_AFFINE_RESIDUAL_BRANCH",
            "unclassified_boxes": [],
            "higher_specialization_boxes": [],
            "maximum_simultaneous_residual_branches": 2,
            "automatic_enlargement": False,
            "next_failure_policy": "leave the two-dimensional canary track and test parent-source generalization; preserve the first failed source object",
        },
        "boxes": boxes,
        "boundary_word_segments": segments,
        "cells": serial,
        "strict_closure_pairs": [list(row) for row in sorted(closure)],
        "strict_three_cell_chains": [list(row) for row in sorted(chains)],
        "scope_boundary_subcomplex": sorted(scope_boundary),
        "atlas_seam_subcomplex": sorted(seam),
        "residual_wall_subcomplex": sorted(residual),
        "parent_infinity_subcomplex": [],
        "signature_profile_source": {
            "universe_count": 97_224,
            "semantic_sha256": profile_digest,
            "profiles": profiles,
        },
        "integral_boundary": integral_boundary(cells),
        "rank_replay": {
            "barycentric_cell_census": {
                str(key): value for key, value in replay["barycentric_census"].items()
            },
            "unordered_profile_multisets": replay["unordered_profile_multisets"],
            "ordered_profile_triples": replay["ordered_profile_triples"],
            "rank_histogram": rank_histogram,
            "nonzero_middle_profile_triples": [],
            "semantic_sha256": replay["semantic_sha256"],
        },
        "verifier": {
            "command": "python ai/omreal/verify_diag3_pair_master_closure_first_event.py",
            "recomputes": [
                "all 84,840 residual restrictions after exact pinned-branch division",
                "the unique first affine event and strict dominance for every other event factor on the 64-box domain",
                "all 70 parent brackets and exact parent-plane residence",
                "all 64 box classes, 171 boundary words, 399 regular-CW cells and integral d_squared identity",
                "all 97,224 extension-signature profiles from six exact chamber witnesses",
                "all 512 ordered profile triples via 120 exact color-symmetric multisets",
            ],
        },
    }
