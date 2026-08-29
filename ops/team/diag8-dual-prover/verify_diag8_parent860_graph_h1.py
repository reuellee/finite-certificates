#!/usr/bin/env python3
"""Pure-standard-library replay of the parent-860 diagonal-eight graph no-go."""

from __future__ import annotations

import argparse
import ast
import copy
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from pathlib import Path
import struct
import zipfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CERTIFICATE = HERE / "DIAG8_PARENT860_GRAPH_H1_CERTIFICATE.json"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def product(values):
    answer = 1
    for value in values:
        answer *= value
    return answer


def read_npy(raw):
    require(raw[:6] == b"\x93NUMPY", "bad NPY magic")
    major, minor = raw[6], raw[7]
    require((major, minor) in ((1, 0), (2, 0), (3, 0)), "unsupported NPY version")
    if major == 1:
        header_length = struct.unpack("<H", raw[8:10])[0]
        cursor = 10
    else:
        header_length = struct.unpack("<I", raw[8:12])[0]
        cursor = 12
    header = ast.literal_eval(raw[cursor : cursor + header_length].decode("latin1"))
    require(not header["fortran_order"], "Fortran-order NPY is outside replay scope")
    shape = tuple(header["shape"])
    count = product(shape) if shape else 1
    payload = raw[cursor + header_length :]
    descriptor = header["descr"]
    if descriptor.startswith("<U"):
        width = int(descriptor[2:])
        item_size = 4 * width
        require(len(payload) == count * item_size, "Unicode NPY byte count changed")
        values = []
        for offset in range(0, len(payload), item_size):
            values.append(payload[offset : offset + item_size].decode("utf-32-le").rstrip("\x00"))
    else:
        formats = {"|i1": "b", "|u1": "B", "<u1": "B", "<u2": "H", "<u4": "I", "<u8": "Q"}
        require(descriptor in formats, f"unsupported NPY dtype {descriptor}")
        code = formats[descriptor]
        item_size = struct.calcsize("<" + code)
        require(len(payload) == count * item_size, "numeric NPY byte count changed")
        values = list(struct.unpack("<" + code * count, payload))
    return shape, values


def npz_array(path, name):
    with zipfile.ZipFile(path) as archive:
        return read_npy(archive.read(name + ".npy"))


def rational(value):
    return Fraction(str(value))


def determinant(matrix):
    if len(matrix) == 1:
        return matrix[0][0]
    return sum(
        (-1 if column & 1 else 1)
        * value
        * determinant([row[:column] + row[column + 1 :] for row in matrix[1:]])
        for column, value in enumerate(matrix[0])
    )


def normalized_matrix(coordinates):
    a, b, c, d, e, f, g, h, i = map(Fraction, coordinates)
    return (
        (Fraction(1), 0, 0, 0, 1, 1, 1, 1),
        (0, 1, 0, 0, 1, a, d, g),
        (0, 0, 1, 0, 1, b, e, h),
        (0, 0, 0, 1, 1, c, f, i),
    )


def parent_brackets(matrix):
    answer = []
    for columns in combinations(range(8), 4):
        answer.append(determinant([[matrix[row][column] for column in columns] for row in range(4)]))
    return answer


def derived_rows(matrix):
    answer = []
    for columns in combinations(range(8), 3):
        values = [[matrix[row][column] for column in columns] for row in range(4)]
        answer.append(
            tuple(
                (-1) ** (coordinate + 3)
                * determinant([row for row_index, row in enumerate(values) if row_index != coordinate])
                for coordinate in range(4)
            )
        )
    # Canonical tope bits order triples by reversed tuple, not lexicographically.
    triples = sorted(combinations(range(8), 3), key=lambda subset: tuple(reversed(subset)))
    lookup = {columns: row for columns, row in zip(combinations(range(8), 3), answer)}
    return [lookup[columns] for columns in triples]


def matrix_rank(matrix):
    if not matrix:
        return 0
    work = [list(map(Fraction, row)) for row in matrix]
    rows = len(work)
    columns = len(work[0])
    require(all(len(row) == columns for row in work), "ragged matrix")
    rank = 0
    for column in range(columns):
        pivot = next((row for row in range(rank, rows) if work[row][column]), None)
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        scale = work[rank][column]
        work[rank] = [value / scale for value in work[rank]]
        for row in range(rows):
            if row == rank or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [left - scale * right for left, right in zip(work[row], work[rank])]
        rank += 1
        if rank == rows:
            break
    return rank


def strict_subset(left, right):
    return left != right and left & ~right == 0


def incomparable(left, right):
    return not strict_subset(left, right) and not strict_subset(right, left) and left != right


def intersection(patterns, indices, vertex_count):
    answer = (1 << vertex_count) - 1
    for index in indices:
        answer &= patterns[index]
    return answer


def induced_graph(mask, edges, vertex_count):
    vertices = [vertex for vertex in range(vertex_count) if mask & (1 << vertex)]
    kept = [edge for edge in edges if mask & (1 << edge[0]) and mask & (1 << edge[1])]
    return vertices, kept


def graph_boundary(vertices, edges):
    row = {vertex: index for index, vertex in enumerate(vertices)}
    matrix = [[0 for _edge in edges] for _vertex in vertices]
    for column, (left, right) in enumerate(edges):
        require(left != right, "loop edge")
        matrix[row[left]][column] = -1
        matrix[row[right]][column] = 1
    return matrix


def h1_rank(vertices, edges, d2_columns):
    d1 = graph_boundary(vertices, edges)
    rank1 = matrix_rank(d1)
    if d2_columns:
        require(all(len(column) == len(edges) for column in d2_columns), "bad d2 column length")
        d2 = [[column[row] for column in d2_columns] for row in range(len(edges))]
        rank2 = matrix_rank(d2)
        for column in d2_columns:
            boundary = [sum(d1[row][edge] * column[edge] for edge in range(len(edges))) for row in range(len(vertices))]
            require(not any(boundary), "d1*d2 is nonzero")
    else:
        rank2 = 0
    return len(edges) - rank1 - rank2, rank1, rank2


def extract_source(source):
    path = ROOT / source["path"]
    require(path.is_file(), "source NPZ missing")
    require(hashlib.sha256(path.read_bytes()).hexdigest() == source["sha256"], "source NPZ digest changed")
    format_shape, format_values = npz_array(path, "format")
    require(format_shape == () and format_values == [source["format"]], "source format changed")
    edge_shape, edge_values = npz_array(path, "augmented_edge")
    require(len(edge_shape) == 2 and edge_shape[1] == 2, "source edge shape changed")
    edges = [edge_values[index : index + 2] for index in range(0, len(edge_values), 2)]
    pattern_shape, patterns = npz_array(path, "proper_pattern")
    require(pattern_shape == (len(patterns),), "source proper-pattern shape changed")
    signature_shape, signatures = npz_array(path, "signature")
    support_shape, supports = npz_array(path, "signature_pattern")
    require(signature_shape == support_shape == (len(signatures),), "source signature arrays changed")
    multiplicities = [supports.count(pattern) for pattern in patterns]
    representatives = [min(signature for signature, support in zip(signatures, supports) if support == pattern) for pattern in patterns]
    chord_shape, chord_values = npz_array(path, "chord")
    require(len(chord_shape) == 2 and chord_shape[1] == 2, "source chord shape changed")
    chords = [chord_values[index : index + 2] for index in range(0, len(chord_values), 2)]
    offset_shape, root_offsets = npz_array(path, "chord_root_offset")
    require(offset_shape == (len(chords) + 1,), "source chord offsets changed")
    support_accounting = {
        "full_signature_universe_size": len(signatures),
        "support_class_count": len(set(supports)),
        "proper_signature_count": sum(multiplicities),
        "universal_support_mask": (1 << 24) - 1,
        "universal_signature_count": supports.count((1 << 24) - 1),
    }
    return (
        edges,
        patterns,
        multiplicities,
        representatives,
        chords,
        root_offsets,
        support_accounting,
    )


def extract_geometry(record):
    source = record["coordinate_source"]
    path = ROOT / source["path"]
    require(path.is_file(), "coordinate-source NPZ missing")
    require(hashlib.sha256(path.read_bytes()).hexdigest() == source["sha256"], "coordinate-source NPZ digest changed")
    shape, values = npz_array(path, "format")
    require(shape == () and values == [source["format"]], "coordinate-source format changed")
    variable_shape, variables = npz_array(path, "vertex_variable")
    numerator_shape, numerators = npz_array(path, "vertex_parameter_numerator")
    denominator_shape, denominators = npz_array(path, "vertex_parameter_denominator")
    require(variable_shape == numerator_shape == denominator_shape, "coordinate-source vertex arrays changed")
    edge_shape, edge_values = npz_array(path, "edge")
    require(len(edge_shape) == 2 and edge_shape[1] == 2, "coordinate-source edge shape changed")
    edges = [edge_values[index : index + 2] for index in range(0, len(edge_values), 2)]
    return variables, [Fraction(int(numerator), int(denominator)) for numerator, denominator in zip(numerators, denominators)], edges


def verify(record, source_check=True):
    require(record["format"] == "diag8-parent860-graph-h1-no-go-v1", "certificate format changed")
    require(record["base_revision"] == "5393b03fda623dc6b4552130d13467fae71d31bc", "base revision changed")
    require(record["base_tree"] == "06cc3363a021b8adc59e66865f44bf8eafa66029", "base tree changed")
    graph = record["extracted_graph"]
    poset = record["local_support_poset"]
    if source_check:
        (
            edges,
            patterns,
            multiplicities,
            representatives,
            chords,
            root_offsets,
            support_accounting,
        ) = extract_source(record["source"])
        variables, parameters, coordinate_edges = extract_geometry(record)
    else:
        edges = record["extracted_graph"]["edges"]
        patterns = record["local_support_poset"]["patterns"]
        multiplicities = record["local_support_poset"]["multiplicities"]
        representatives = record["local_support_poset"]["representative_signatures"]
        variables = [-1] * 24
        parameters = [Fraction(0)] * 24
        support_accounting = {
            name: poset[name]
            for name in (
                "full_signature_universe_size",
                "support_class_count",
                "proper_signature_count",
                "universal_support_mask",
                "universal_signature_count",
            )
        }
    vertex_count = graph["vertex_count"]
    require(edges == graph["edges"], "extracted edge list changed")
    require(patterns == poset["patterns"], "extracted proper patterns changed")
    require(multiplicities == poset["multiplicities"], "pattern multiplicities changed")
    require(representatives == poset["representative_signatures"], "pattern representatives changed")
    require(
        all(poset[name] == value for name, value in support_accounting.items()),
        "support-class accounting changed",
    )
    require(
        poset["full_signature_universe_size"] == 26_264
        and poset["support_class_count"] == 13
        and poset["proper_signature_count"] == 304
        and poset["universal_support_mask"] == (1 << vertex_count) - 1
        and poset["universal_signature_count"] == 25_960
        and poset["proper_signature_count"] + poset["universal_signature_count"]
        == poset["full_signature_universe_size"],
        "unexpected proper/universal support census",
    )
    require(len(set(patterns)) == len(patterns) == 12, "proper-pattern quotient changed")
    require(len(edges) == len({tuple(edge) for edge in edges}) == 39, "edge census changed")
    require(all(0 <= endpoint < vertex_count for edge in edges for endpoint in edge), "edge endpoint out of range")

    width_witness = poset["width_witness_pattern_indices"]
    require(len(width_witness) == poset["width"] == 6, "width witness size changed")
    require(all(incomparable(patterns[left], patterns[right]) for left, right in combinations(width_witness, 2)), "width lower-bound witness is comparable")
    chains = poset["six_chain_cover_pattern_indices"]
    require(len(chains) == 6, "chain-cover upper bound changed")
    require(sorted(index for chain in chains for index in chain) == list(range(len(patterns))), "chain cover is not a partition")
    for chain in chains:
        require(all(strict_subset(patterns[left], patterns[right]) for left, right in zip(chain, chain[1:])), "invalid inclusion chain")

    antichains = {}
    for size in (5, 6, 8):
        antichains[size] = [candidate for candidate in combinations(range(len(patterns)), size) if all(incomparable(patterns[left], patterns[right]) for left, right in combinations(candidate, 2))]
    require(len(antichains[6]) == poset["size_six_antichain_count"] == 9, "size-six antichain count changed")
    require(sum(bool(intersection(patterns, candidate, vertex_count)) for candidate in antichains[6]) == poset["size_six_nonempty_intersection_count"] == 0, "size-six intersections changed")
    require(len(antichains[8]) == poset["size_eight_antichain_count"] == 0, "size-eight antichain count changed")

    cycle = record["cycle_obstruction"]
    witness = cycle["pairwise_incomparable_pattern_indices"]
    require(tuple(witness) in antichains[5], "cycle family is not a five-antichain")
    require([representatives[index] for index in witness] == cycle["representative_signatures"], "cycle representatives changed")
    mask = intersection(patterns, witness, vertex_count)
    require(mask == cycle["common_support_mask"], "cycle support mask changed")
    vertices, retained_edges = induced_graph(mask, edges, vertex_count)
    require(vertices == cycle["vertices"] and retained_edges == cycle["edges"], "induced triangle changed")
    unfilled = h1_rank(vertices, retained_edges, [])
    require(unfilled == (cycle["unfilled_h1_rank_over_q"], 2, cycle["unfilled_c2_rank"]), "unfilled H1 changed")
    filled = h1_rank(vertices, retained_edges, [cycle["filled_triangle_boundary_on_ordered_edges"]])
    require(filled == (cycle["filled_h1_rank_over_q"], 2, cycle["filled_c2_rank"]), "filled H1 changed")
    filling = record["geometric_triangle_filling"]
    require(filling["vertex_ids"] == cycle["vertices"], "filling vertices changed")
    base = tuple(map(rational, filling["normalized_base_coordinates"]))
    offsets = [[rational(value) for value in row] for row in filling["vertex_offsets"]]
    if source_check:
        require(variables[0] == -1 and parameters[0] == 0, "central vertex changed")
        require(variables[4] == 0 and parameters[4] == offsets[1][0], "a-axis vertex changed")
        require(variables[11] == 3 and parameters[11] == offsets[2][1], "d-axis vertex changed")
        require([0, 4] in coordinate_edges and [0, 11] in coordinate_edges, "coordinate triangle edges changed")
        chord_index = chords.index([4, 11])
        require(root_offsets[chord_index] == root_offsets[chord_index + 1], "triangle chord is no longer residual-free")
    coordinate_points = []
    for a_offset, d_offset in offsets + [[offsets[1][0], offsets[2][1]]]:
        coordinates = list(base)
        coordinates[0] += a_offset
        coordinates[3] += d_offset
        coordinate_points.append(tuple(coordinates))
    matrices = [normalized_matrix(coordinates) for coordinates in coordinate_points]
    bracket_controls = [parent_brackets(matrix) for matrix in matrices]
    base_signs = [1 if value > 0 else -1 for value in bracket_controls[0]]
    require(all(value for row in bracket_controls for value in row), "triangle meets a parent wall")
    require(all((value > 0) == (sign > 0) for row in bracket_controls[:3] for value, sign in zip(row, base_signs)), "parent sign changes at a triangle vertex")
    parent_mixed = [bracket_controls[3][index] - bracket_controls[1][index] - bracket_controls[2][index] + bracket_controls[0][index] for index in range(70)]
    require(not any(parent_mixed), "parent brackets are not affine on the triangle plane")
    require(3 * 70 == filling["positive_parent_vertex_controls"], "parent-control census changed")

    rows = [derived_rows(matrix) for matrix in matrices]
    signature_control_count = 0
    mixed_count = 0
    for signature_text, witness in filling["fixed_witnesses_by_signature"].items():
        signature = int(signature_text)
        require(signature in cycle["representative_signatures"], "unregistered filling signature")
        margins = []
        for vertex_rows in rows:
            margins.append(
                [
                    (1 if signature & (1 << index) else -1)
                    * sum(coefficient * coordinate for coefficient, coordinate in zip(row, witness))
                    for index, row in enumerate(vertex_rows)
                ]
            )
        require(all(value > 0 for row in margins[:3] for value in row), f"fixed witness fails on triangle vertices: {signature}")
        mixed = [margins[3][index] - margins[1][index] - margins[2][index] + margins[0][index] for index in range(56)]
        require(not any(mixed), f"signed margins are not affine: {signature}")
        observed_minimum = min(value for row in margins[:3] for value in row)
        require(observed_minimum == rational(filling["minimum_signed_margin_by_signature"][signature_text]), f"minimum signed margin changed: {signature}")
        signature_control_count += 3 * 56
        mixed_count += 56
    require(len(filling["fixed_witnesses_by_signature"]) == len(cycle["representative_signatures"]) == 5, "filling family changed")
    require(signature_control_count == filling["positive_signature_vertex_controls"], "signature-control census changed")
    require(mixed_count + len(parent_mixed) == filling["zero_mixed_affine_checks"], "affine-check census changed")

    require(record["decision"]["outcome"] == "BOUNDED_PROVED_AND_NO_GO", "dishonest outcome")
    require("2/9" in record["decision"]["ledger_recommendation"] and "OPEN" in record["decision"]["ledger_recommendation"], "dishonest ledger recommendation")
    return {
        "width": poset["width"],
        "size_six_antichains": len(antichains[6]),
        "size_eight_antichains": len(antichains[8]),
        "unfilled_h1": unfilled[0],
        "filled_h1": filled[0],
        "parent_controls": filling["positive_parent_vertex_controls"],
        "signature_controls": filling["positive_signature_vertex_controls"],
    }


def expect_rejection(record, label):
    try:
        verify(record, source_check=False)
    except (AssertionError, KeyError, TypeError, ValueError):
        return
    raise AssertionError(f"hostile canary accepted: {label}")


def run_canaries(record):
    summary = verify(record)
    require(summary["unfilled_h1"] == 1, "positive canary lost graph cycle")
    require(summary["filled_h1"] == 0, "negative canary failed to kill graph cycle")
    require(summary["size_eight_antichains"] == 0, "null canary became nonvacuous")
    corrupt = copy.deepcopy(record)
    corrupt["extracted_graph"]["edges"][27] = [4, 12]
    expect_rejection(corrupt, "tampered triangle edge")
    corrupt = copy.deepcopy(record)
    corrupt["local_support_poset"]["width"] = 8
    expect_rejection(corrupt, "inflated local width")
    corrupt = copy.deepcopy(record)
    corrupt["decision"]["ledger_recommendation"] = "Promote to 3/9"
    expect_rejection(corrupt, "inflated theorem ledger")
    corrupt = copy.deepcopy(record)
    corrupt["geometric_triangle_filling"]["fixed_witnesses_by_signature"]["14206879704843884"][0] *= -1
    expect_rejection(corrupt, "hostile fixed witness")
    corrupt = copy.deepcopy(record)
    corrupt["local_support_poset"]["proper_signature_count"] += 1
    expect_rejection(corrupt, "inflated proper-signature count")
    print("CANARY positive PASS unfilled five-antichain triangle has H1_Q=1")
    print("CANARY negative PASS one exact triangle filling changes H1_Q to 0")
    print("CANARY null PASS local support quotient has zero size-eight antichains")
    print("CANARY hostile PASS edge, width, ledger, witness, and support-count mutations rejected 5/5")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path, default=CERTIFICATE)
    parser.add_argument("--skip-canaries", action="store_true")
    args = parser.parse_args()
    record = json.loads(args.certificate.read_text())
    summary = verify(record)
    if not args.skip_canaries:
        run_canaries(record)
    print("PASS source NPZ byte digest and pure-stdlib NPY extraction")
    print("PASS exact local dominance width:", summary["width"])
    print("PASS exact support accounting: 26264 signatures = 304 proper + 25960 universal in 13 classes")
    print("PASS exact size-six antichains:", summary["size_six_antichains"], "all with empty common support")
    print("PASS exact size-eight local antichains:", summary["size_eight_antichains"])
    print("THEOREM exact a/d triangle filling controls:", summary["parent_controls"], "parent and", summary["signature_controls"], "signed feasibility")
    print("NO-GO same certified graph and labels admit H1_Q ranks", summary["unfilled_h1"], "and", summary["filled_h1"])
    print("NEXT DISCRIMINATOR exact a/g polygon filling, then relative two-cell and true-infinity incidence")
    print("SCOPE finite parent-860 embedded network only; no global roadmap, diagonal-eight proof, or ledger change")


if __name__ == "__main__":
    main()
