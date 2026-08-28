#!/usr/bin/env python3
"""Standalone exact referee for the row-2599 order-two triangle pilot.

This verifier does not import or execute the candidate producer.  It parses
the raw catalog, point bank, candidate-factor stream, factor-census arrays,
and accepted edge artifacts, then reconstructs every asserted finite fact
with local exact-rational routines.
"""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, permutations
import json
from math import comb, factorial, gcd, lcm
from pathlib import Path
import struct
import subprocess

import numpy as np


ROOT = Path(__file__).resolve().parents[3]
CANDIDATE = ROOT / "ops/team/triangle-certificate/ROW2599_ORDER2_TRIANGLE_PILOT.json"
MANIFEST = ROOT / "ops/team/triangle-certificate/MANIFEST.sha256"
CATALOG = ROOT / "ai/omreal/certs_4_8.jsonl"
POINT_BANK = ROOT / "ai/omreal/data/seeat_parent2599_upper178.npz"
FACTOR_CENSUS = ROOT / "ai/omreal/data/DIAG9_GRAPH_global_factor_census.npz"
CANDIDATES = ROOT / "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin"
EDGE27 = ROOT / "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON.json"
EDGE39 = ROOT / "ai/omreal/data/DIAG3_PAIR_PARENT_SOURCE_TRANSITION_EDGE39_0_113.json"
COMBINED = ROOT / "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON_EDGE27_EDGE39.json"

BASE = "ec362dba8a912bc4749c004641aee2da0a88dc05"
CANDIDATE_HEAD = "e3989d3f7099b245e31a3223acb02d948a9848af"
FORMAT = "diag3-pair-row2599-order2-triangle-pilot-v1"
PREFIX = b"diag3-pair-row2599-order2-triangle-pilot-v1\0"
TRIANGLE = (
    (Fraction(0), Fraction(0)),
    (Fraction(1), Fraction(0)),
    (Fraction(0), Fraction(1)),
)
EXPECTED_INPUTS = {
    "ai/omreal/certs_4_8.jsonl": "c55e805d60d8086bcb84a312f2103a9973fc2691d0fd97f3d9a1d9809d2b163b",
    "ai/omreal/data/seeat_parent2599_upper178.npz": "3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a",
    "ai/omreal/data/DIAG9_GRAPH_global_factor_census.npz": "3984ce87e11fd59d804e59568177248e218cd1c7bb07aae0a9f9f746858728bc",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin": "adb2e7257457f158e809450683c46fe7ecafdbdd4a7efdf9ac630e8a4f0fb03f",
    "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON.json": "5430bd79ae9ddee09ce9b393f018389be1210c250a7eb0d5486fab8e1294663d",
    "ai/omreal/data/DIAG3_PAIR_PARENT_SOURCE_TRANSITION_EDGE39_0_113.json": "cb6eebc0df9bfeae8055c81471f09d594f8116e002caf11f62f9e865b0936dd7",
    "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON_EDGE27_EDGE39.json": "dcb707220df3e61b1a94eeedcf8e46b6602f30d405f4a92fc542c0f52f672806",
    "ai/omreal/exact_semialgebraic/tensor_bernstein.py": "fe0274d19a27dc70707133c6bcaba9f976b7ba245568440b71b0c0275740272c",
}
EXPECTED_CANDIDATE_SHA = "578d86dd4e8e58d6150e88c209270259ba14e121db232dc41c913985ae89befd"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def file_sha(path):
    state = sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            state.update(block)
    return state.hexdigest()


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")


def fraction_text(value):
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def point_text(point):
    return [fraction_text(value) for value in point]


def qsign(value):
    return 1 if value > 0 else -1 if value < 0 else 0


def negative_parity(order):
    return sum(
        order[left] > order[right]
        for left in range(len(order))
        for right in range(left + 1, len(order))
    ) & 1


def determinant_numeric(matrix):
    size = len(matrix)
    answer = 0
    for order in permutations(range(size)):
        term = -1 if negative_parity(order) else 1
        for row, column in enumerate(order):
            term *= matrix[row][column]
        answer += term
    return answer


def minor_numeric(matrix, columns):
    return determinant_numeric([[matrix[row][column] for column in columns] for row in range(4)])


def normalized_point(matrix):
    basis = (0, 1, 2, 3)
    replacements = tuple(
        minor_numeric(matrix, basis[:row] + (4,) + basis[row + 1 :])
        for row in range(4)
    )
    require(all(replacements), "nonuniform normalization frame")
    normalized = []
    for column in range(8):
        if column < 4:
            value = [Fraction(0)] * 4
            value[column] = Fraction(1)
        elif column == 4:
            value = [Fraction(1)] * 4
        else:
            value = [
                Fraction(
                    minor_numeric(matrix, basis[:row] + (column,) + basis[row + 1 :] ),
                    replacements[row],
                )
                for row in range(4)
            ]
        normalized.append(value)
    answer = []
    for column in (5, 6, 7):
        gauge = normalized[column][0]
        require(gauge > 0 and all(value / gauge > 0 for value in normalized[column]), "positive chart")
        answer.extend(normalized[column][row] / gauge for row in (1, 2, 3))
    return tuple(answer)


def clean(poly):
    return {index: Fraction(value) for index, value in poly.items() if value}


def poly_add(left, right, scale=1):
    answer = dict(left)
    for index, value in right.items():
        answer[index] = answer.get(index, Fraction(0)) + Fraction(scale) * value
        if not answer[index]:
            del answer[index]
    return answer


def poly_mul(left, right):
    if not left or not right:
        return {}
    answer = {}
    for first, a in left.items():
        for second, b in right.items():
            index = tuple(x + y for x, y in zip(first, second, strict=True))
            answer[index] = answer.get(index, Fraction(0)) + a * b
    return clean(answer)


def poly_det(matrix, dimension):
    size = len(matrix)
    zero = (0,) * dimension
    answer = {}
    for order in permutations(range(size)):
        term = {zero: Fraction(-1 if negative_parity(order) else 1)}
        for row, column in enumerate(order):
            term = poly_mul(term, matrix[row][column])
        answer = poly_add(answer, term)
    return answer


def primitive_poly(poly):
    poly = clean(poly)
    if not poly:
        return {}
    denominator = 1
    for value in poly.values():
        denominator = lcm(denominator, value.denominator)
    integers = {index: int(value * denominator) for index, value in poly.items()}
    divisor = 0
    for value in integers.values():
        divisor = gcd(divisor, abs(value))
    integers = {index: value // divisor for index, value in integers.items()}
    if integers[max(integers)] < 0:
        integers = {index: -value for index, value in integers.items()}
    return {index: Fraction(value) for index, value in integers.items()}


def evaluate(poly, point):
    answer = Fraction(0)
    for exponent, coefficient in poly.items():
        term = coefficient
        for value, power in zip(point, exponent, strict=True):
            term *= value**power
        answer += term
    return answer


def pullback(poly, constants, rows):
    target_dimension = len(rows[0])
    zero = (0,) * target_dimension
    powers = []
    maximum_powers = tuple(
        max((exponent[axis] for exponent in poly), default=0)
        for axis in range(len(constants))
    )
    for source_axis, (constant, row) in enumerate(zip(constants, rows, strict=True)):
        linear = {zero: constant}
        for axis, value in enumerate(row):
            if value:
                index = [0] * target_dimension
                index[axis] = 1
                linear[tuple(index)] = value
        table = [{zero: Fraction(1)}]
        for _ in range(maximum_powers[source_axis]):
            table.append(poly_mul(table[-1], linear))
        powers.append(tuple(table))
    answer = {}
    for exponent, coefficient in poly.items():
        term = {zero: Fraction(coefficient)}
        for axis, power in enumerate(exponent):
            term = poly_mul(term, powers[axis][power])
        answer = poly_add(answer, term)
    return clean(answer)


def weak_compositions(total, length):
    if length == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in weak_compositions(total - first, length - 1):
            yield (first,) + tail


def simplex_controls(poly):
    require(poly, "zero polynomial has no sign controls")
    dimension = len(next(iter(poly)))
    degree = max(map(sum, poly))
    homogeneous = defaultdict(Fraction)
    for exponent, coefficient in poly.items():
        deficit = degree - sum(exponent)
        for addition in weak_compositions(deficit, dimension + 1):
            alpha = (addition[0],) + tuple(
                exponent[axis] + addition[axis + 1]
                for axis in range(dimension)
            )
            weight = factorial(deficit)
            for value in addition:
                weight //= factorial(value)
            homogeneous[alpha] += coefficient * weight
    controls = {}
    for alpha in weak_compositions(degree, dimension + 1):
        divisor = factorial(degree)
        for value in alpha:
            divisor //= factorial(value)
        controls[alpha] = homogeneous[alpha] / divisor
    return controls, degree


def symbolic_parent_polynomials():
    dimension = 9
    zero_index = (0,) * dimension
    zero = {}
    one = {zero_index: Fraction(1)}
    variables = []
    for axis in range(dimension):
        index = [0] * dimension
        index[axis] = 1
        variables.append({tuple(index): Fraction(1)})
    a, b, c, d, e, f, g, h, i = variables
    matrix = (
        (one, zero, zero, zero, one, one, one, one),
        (zero, one, zero, zero, one, a, d, g),
        (zero, zero, one, zero, one, b, e, h),
        (zero, zero, zero, one, one, c, f, i),
    )
    answer = []
    for basis in combinations(range(8), 4):
        square = tuple(tuple(matrix[row][column] for column in basis) for row in range(4))
        answer.append(("".join(str(column + 1) for column in basis), primitive_poly(poly_det(square, dimension))))
    return answer


def parse_sources():
    candidate_bytes = CANDIDATE.read_bytes()
    require(sha256(candidate_bytes).hexdigest() == EXPECTED_CANDIDATE_SHA, "candidate byte digest")
    for relative, expected in EXPECTED_INPUTS.items():
        require(file_sha(ROOT / relative) == expected, f"input digest {relative}")

    manifest_rows = {}
    for line in MANIFEST.read_text(encoding="utf-8").splitlines():
        digest, relative = line.split("  ", 1)
        manifest_rows[relative] = digest
        require(file_sha(ROOT / relative) == digest, f"manifest digest {relative}")
    require(manifest_rows["ops/team/triangle-certificate/ROW2599_ORDER2_TRIANGLE_PILOT.json"] == EXPECTED_CANDIDATE_SHA, "manifest candidate")

    raw = CANDIDATES.read_bytes()
    header_size = struct.calcsize("<8sIII")
    magic, parent, factor_count, candidate_count = struct.unpack_from("<8sIII", raw)
    require((magic, parent, factor_count, candidate_count) == (b"D3PFC001", 2599, 26740, 17824), "candidate header")
    require(len(raw) == header_size + 4 * candidate_count, "candidate exact EOF")
    candidate_ids = tuple(map(int, np.frombuffer(raw, dtype="<u4", offset=header_size)))
    require(candidate_ids == tuple(sorted(set(candidate_ids))), "canonical candidate IDs")

    with np.load(FACTOR_CENSUS, allow_pickle=False) as source:
        require(str(source["format"]) == "diag9-global-residual-factor-census-v1", "factor format")
        offsets = np.asarray(source["factor_offset"], dtype=np.uint32)
        exponents = np.asarray(source["factor_exponent"], dtype=np.uint8)
        coefficients = np.asarray(source["factor_coefficient"], dtype=np.int64)
    require(len(offsets) == 26741 and len(exponents) == len(coefficients) == int(offsets[-1]), "factor arrays")
    factors = []
    for factor_id in range(26740):
        start, stop = int(offsets[factor_id]), int(offsets[factor_id + 1])
        factors.append({tuple(map(int, exponents[pos])): Fraction(int(coefficients[pos])) for pos in range(start, stop)})

    records = [json.loads(line) for line in CATALOG.read_text(encoding="utf-8").splitlines() if line]
    require(len(records) > 2599, "catalog row")
    catalog_record = records[2599]
    catalog_matrix = catalog_record["matrix"]
    raw_signs = []
    catalog_basis_order = tuple(
        sorted(combinations(range(8), 4), key=lambda subset: tuple(reversed(subset)))
    )
    for basis in catalog_basis_order:
        value = minor_numeric(catalog_matrix, basis)
        require(value, "catalog nonuniform")
        raw_signs.append("+" if value > 0 else "-")
    require("".join(raw_signs) == catalog_record["chi"], "catalog matrix/chirotope")

    with np.load(POINT_BANK, allow_pickle=False) as source:
        require(str(source["format"]) == "seeat-parent2599-upper-cover-v1", "point-bank format")
        require(int(source["parent_index"]) == 2599, "point-bank parent")
        matrices = np.asarray(source["chart_matrix"], dtype=np.int64)
    require(matrices.shape == (178, 4, 8), "point-bank shape")
    points = tuple(normalized_point(matrix.tolist()) for matrix in matrices)
    return candidate_bytes, candidate_ids, factors, catalog_record, points


def parent_certificate(catalog_record, points):
    sample = normalized_point(catalog_record["matrix"])
    parents = symbolic_parent_polynomials()
    targets = []
    for _label, polynomial in parents:
        value = evaluate(polynomial, sample)
        require(value, "zero normalized parent bracket")
        targets.append(qsign(value))
    target_digest = sha256(
        b"diag3-row2599-normalized-parent-signs-v1\0" + bytes(int(sign > 0) for sign in targets)
    ).hexdigest()
    base = points[0]
    rows = tuple((points[89][axis] - base[axis], points[113][axis] - base[axis]) for axis in range(9))
    records = []
    aggregate = sha256(b"diag3-row2599-order2-triangle-parent-controls-v1\0")
    for (label, polynomial), target in zip(parents, targets, strict=True):
        signed = {index: target * value for index, value in polynomial.items()}
        restricted = pullback(signed, base, rows)
        controls, degree = simplex_controls(restricted)
        require(all(value > 0 for value in controls.values()), f"strict parent bracket {label}")
        serial = [[list(index), fraction_text(value)] for index, value in sorted(controls.items())]
        digest = sha256(canonical(serial)).hexdigest()
        aggregate.update(label.encode("ascii") + b"\0" + bytes.fromhex(digest))
        records.append({
            "parent_bracket": label,
            "target_sign": target,
            "total_degree": degree,
            "control_count": len(controls),
            "minimum_positive_control": fraction_text(min(controls.values())),
            "controls_sha256": digest,
        })
    return base, rows, {
        "method": "exact triangular simplex-Bernstein controls on the whole closed triangle",
        "signed_parent_bracket_count": 70,
        "all_controls_strictly_positive": True,
        "normalized_parent_signs_sha256": target_digest,
        "aggregate_controls_sha256": aggregate.hexdigest(),
        "brackets": records,
    }


def barycentric(point):
    s, t = point
    return Fraction(1) - s - t, s, t


def strictly_interior(point):
    return all(value > 0 for value in barycentric(point))


def open_segment_interior(left, right):
    return all(not (a == 0 and b == 0) for a, b in zip(barycentric(left), barycentric(right), strict=True))


def find_witness(poly, vertices):
    values = [evaluate(poly, point) for point in vertices]
    for point, value in zip(vertices, values, strict=True):
        if value == 0 and strictly_interior(point):
            return {"kind": "EXACT_INTERIOR_POINT", "point": point_text(point)}
    for left in range(len(vertices)):
        for right in range(left + 1, len(vertices)):
            if values[left] * values[right] < 0 and open_segment_interior(vertices[left], vertices[right]):
                return {
                    "kind": "OPPOSITE_SIGNS_ON_INTERIOR_OPEN_SEGMENT",
                    "left": point_text(vertices[left]),
                    "right": point_text(vertices[right]),
                    "left_sign": qsign(values[left]),
                    "right_sign": qsign(values[right]),
                }
    return None


def probes():
    answer = [(Fraction(1, 3), Fraction(1, 3))]
    for exponent in (4, 8, 12):
        epsilon = Fraction(1, 1 << exponent)
        answer.extend(((epsilon, epsilon), (1 - 2 * epsilon, epsilon), (epsilon, 1 - 2 * epsilon)))
    require(all(strictly_interior(point) for point in answer), "probe bank interior")
    return tuple(answer)


def longest_edge(vertices):
    rows = []
    for left in range(3):
        for right in range(left + 1, 3):
            squared = sum((vertices[left][axis] - vertices[right][axis])**2 for axis in range(2))
            rows.append((squared, -left, -right, left, right))
    return max(rows)[-2:]


def classify(poly, max_depth=3):
    if not poly:
        return "INTERIOR_ZERO", {"kind": "IDENTICALLY_ZERO_RESTRICTION", "point": ["1/3", "1/3"]}, 0, 1
    witness = find_witness(poly, probes())
    if witness is not None:
        witness["source"] = "fixed_strict_interior_probe_bank"
        return "INTERIOR_ZERO", witness, 0, 1
    stack = [(TRIANGLE, 0)]
    unresolved = visited = deepest = 0
    while stack:
        vertices, depth = stack.pop()
        visited += 1
        deepest = max(deepest, depth)
        witness = find_witness(poly, vertices)
        if witness is not None:
            witness["source"] = "deterministic_longest_edge_subdivision"
            return "INTERIOR_ZERO", witness, deepest, visited
        base = vertices[0]
        rows = tuple(tuple(vertices[target + 1][axis] - base[axis] for target in range(2)) for axis in range(2))
        local = pullback(poly, base, rows)
        if not local:
            centroid = tuple(sum(vertex[axis] for vertex in vertices) / 3 for axis in range(2))
            return "INTERIOR_ZERO", {
                "kind": "IDENTICALLY_ZERO_SUBTRIANGLE",
                "point": point_text(centroid),
                "source": "deterministic_longest_edge_subdivision",
            }, deepest, visited
        controls, _degree = simplex_controls(local)
        signs = {qsign(value) for value in controls.values()}
        if 0 not in signs and len(signs) == 1:
            continue
        if depth >= max_depth:
            unresolved += 1
            continue
        left, right = longest_edge(vertices)
        midpoint = tuple((vertices[left][axis] + vertices[right][axis]) / 2 for axis in range(2))
        first, second = list(vertices), list(vertices)
        first[left] = midpoint
        second[right] = midpoint
        stack.append((tuple(first), depth + 1))
        stack.append((tuple(second), depth + 1))
    if unresolved:
        return "UNRESOLVED", {
            "reason_code": "MIXED_SIMPLEX_BERNSTEIN_AT_DEPTH_LIMIT",
            "unresolved_leaf_count": unresolved,
        }, deepest, visited
    return "EMPTY_CLOSED_TRIANGLE", None, deepest, visited


def edge_factor_sets():
    edge27 = json.loads(EDGE27.read_text(encoding="utf-8"))
    edge39 = json.loads(EDGE39.read_text(encoding="utf-8"))
    combined = json.loads(COMBINED.read_text(encoding="utf-8"))
    require(edge27["scope"]["skeleton_coverage"] == "COMPLETE_ONLY_ON_SELECTED_EDGE_27_CHART_0_TO_89", "edge27 identity")
    require(edge39["edge_interface"]["orientation"] == "chart_0_to_chart_113", "edge39 identity")
    require(edge39["scope"]["source_chart"] == 0 and edge39["scope"]["target_chart"] == 113, "edge39 charts")
    require(combined["scope"]["fully_compiled_cover_edges"] == [27, 39], "combined edge identity")
    result = {27: set(), 39: set()}
    for cell in combined["compiled_regular_subcomplex"]["cells"]:
        if cell.get("kind") != "isolated_residual_event":
            continue
        cell_id = cell["id"]
        for edge in result:
            if f":edge:{edge:03d}:" in cell_id:
                result[edge].add(int(cell["factor_id"]))
                break
    require((len(result[27]), len(result[39]), len(result[27] | result[39])) == (1217, 5209, 5616), "edge factor census")
    raw27 = {
        int(cell["factor_id"])
        for cell in edge27["compiled_regular_subcomplex"]["cells"]
        if cell.get("kind") == "isolated_residual_event"
    }
    raw39 = {
        int(member["factor_id"])
        for event in edge39["residual_roadmap"]["events"]
        for member in event["members"]
    }
    require(raw27 == result[27] and raw39 == result[39], "combined/accepted edge event equality")
    return result


def reconstruct_classification(candidate_ids, factors, base, rows, edge_sets):
    witness_catalog = []
    witness_ids = {}
    interior_groups = {}
    empty_groups = {}
    unresolved_groups = {}
    deepest_census = {}
    total_visited = 0
    absent = []
    for position, factor_id in enumerate(candidate_ids, 1):
        restricted = pullback(factors[factor_id], base, rows)
        status, proof, deepest, visited = classify(restricted, 3)
        deepest_census[deepest] = deepest_census.get(deepest, 0) + 1
        total_visited += visited
        if status == "INTERIOR_ZERO":
            key = canonical(proof)
            witness_id = witness_ids.get(key)
            if witness_id is None:
                witness_id = len(witness_catalog)
                witness_ids[key] = witness_id
                witness_catalog.append({"witness_id": witness_id, "proof": proof})
            interior_groups.setdefault(witness_id, []).append(factor_id)
            if factor_id not in edge_sets[27] and factor_id not in edge_sets[39]:
                absent.append(factor_id)
        elif status == "EMPTY_CLOSED_TRIANGLE":
            empty_groups.setdefault((deepest, visited), []).append(factor_id)
        else:
            unresolved_groups.setdefault(proof["reason_code"], []).append([
                factor_id, deepest, visited, proof["unresolved_leaf_count"]
            ])
        if position % 2000 == 0:
            print(f"REPLAY_FACTORS {position}/{len(candidate_ids)}", flush=True)
    interior_count = sum(map(len, interior_groups.values()))
    empty_count = sum(map(len, empty_groups.values()))
    unresolved_count = sum(map(len, unresolved_groups.values()))
    require((interior_count, empty_count, unresolved_count) == (5665, 12096, 63), "factor classification census")
    classification = {
        "candidate_factor_count": len(candidate_ids),
        "interior_zero_count": interior_count,
        "empty_closed_triangle_count": empty_count,
        "unresolved_count": unresolved_count,
        "witness_catalog": witness_catalog,
        "interior_zero_witness_groups": [
            {"witness_id": witness_id, "factor_ids": factor_ids}
            for witness_id, factor_ids in sorted(interior_groups.items())
        ],
        "empty_closed_triangle_proof_groups": [
            {"deepest_subdivision": key[0], "subtriangles_visited": key[1], "factor_ids": factor_ids}
            for key, factor_ids in sorted(empty_groups.items())
        ],
        "unresolved_by_reason": [
            {"reason_code": code, "records": values}
            for code, values in sorted(unresolved_groups.items())
        ],
        "deepest_subdivision_census": {str(key): value for key, value in sorted(deepest_census.items())},
        "total_subtriangles_visited": total_visited,
    }
    return classification, absent


def validate_scope(record):
    require(record["format"] == FORMAT and record["status"] == "EXACT_BOUNDED_TRIANGLE_CLASSIFICATION", "format/status")
    require(record["base_revision"] == BASE, "mathematical base")
    require(record["inputs"] == EXPECTED_INPUTS, "declared inputs")
    scope = record["scope"]
    require(scope["parameterization"] == "x(s,t)=chart0+s(chart89-chart0)+t(chart113-chart0)", "parameterization")
    require(scope["parameter_domain"] == "s>=0,t>=0,s+t<=1", "barycentric domain")
    require(scope["compiled_boundary_edges"] == {"s=0": 39, "t=0": 27}, "triangle boundary edges")
    require(scope["third_boundary_edge"] == "chart89_to_chart113_NOT_COMPILED", "third boundary")
    require(scope["affine_square_promotion"] is False, "unsafe square")
    require(scope["triangle_boundary_is_parent_infinity"] is False, "false infinity")
    require(scope["global_parent_cell_coverage"] == "NOT_CLAIMED", "global parent coverage")
    require(scope["global_component_coverage"] == "NOT_CLAIMED", "global component coverage")
    require(scope["pair_branch_closed"] is False, "pair closure")
    require(scope["honest_9dvl_score"] == "2/9_UNCHANGED", "score")
    method = record["classification_method"]
    require(method["max_depth"] == 3 and method["arithmetic"] == "EXACT_RATIONAL", "classification method")
    require(method["empty_rule"] == "one-signed nonzero simplex-Bernstein controls cover every leaf", "empty rule")
    require(method["interior_zero_rule"] == "exact interior point zero or opposite endpoint signs on a segment whose open part lies in the triangle interior", "interior rule")


def semantic_seal(record):
    payload = deepcopy(record)
    payload.pop("semantic_sha256", None)
    return sha256(PREFIX + canonical(payload)).hexdigest()


def verify_record(record, expected_parent, expected_classification, absent, edge_sets):
    require(record.get("semantic_sha256") == semantic_seal(record), "semantic seal")
    validate_scope(record)
    require(record["exact_parent_residence"] == expected_parent, "complete parent certificate")
    require(record["factor_classification"] == expected_classification, "complete factor classification")
    require(record["classification_method"]["interior_probe_points"] == [point_text(point) for point in probes()], "probe bank")
    edge = record["compiled_edge_accounting"]
    digest27 = sha256(",".join(map(str, sorted(edge_sets[27]))).encode("ascii")).hexdigest()
    digest39 = sha256(",".join(map(str, sorted(edge_sets[39]))).encode("ascii")).hexdigest()
    require(edge == {
        "edge27_distinct_factor_count": 1217,
        "edge39_distinct_factor_count": 5209,
        "union_distinct_factor_count": 5616,
        "edge27_factor_ids_sha256": digest27,
        "edge39_factor_ids_sha256": digest39,
    }, "edge accounting")
    missing = record["interior_zero_absent_from_edges_27_39"]
    require(missing["count"] == 77 and missing["factor_ids"] == absent and len(set(absent)) == 77, "77 interior factors")
    require(not (set(absent) & (edge_sets[27] | edge_sets[39])), "77 absent from both roadmaps")
    unresolved_ids = {
        row[0]
        for group in expected_classification["unresolved_by_reason"]
        for row in group["records"]
    }
    interior_ids = {
        factor_id
        for group in expected_classification["interior_zero_witness_groups"]
        for factor_id in group["factor_ids"]
    }
    empty_ids = {
        factor_id
        for group in expected_classification["empty_closed_triangle_proof_groups"]
        for factor_id in group["factor_ids"]
    }
    require(len(unresolved_ids) == 63 and not (unresolved_ids & interior_ids) and not (unresolved_ids & empty_ids), "no unresolved promotion")
    require(record["theorem_effect"] == "Exact bounded order-two triangle pilot only; it does not certify global parent-cell or wall-component coverage, does not close diag3_pair_hc1, and leaves the honest 9DVL score at 2/9.", "theorem effect")


def hostile_replay(record, expected_parent, expected_classification, absent, edge_sets):
    cases = []
    mutations = (
        ("unsafe square", lambda row: row["scope"].__setitem__("affine_square_promotion", True)),
        ("false infinity", lambda row: row["scope"].__setitem__("triangle_boundary_is_parent_infinity", True)),
        ("global coverage", lambda row: row["scope"].__setitem__("global_parent_cell_coverage", "COMPLETE")),
        ("pair closure", lambda row: row["scope"].__setitem__("pair_branch_closed", True)),
        ("score 3/9", lambda row: row["scope"].__setitem__("honest_9dvl_score", "3/9")),
        ("factor id", lambda row: row["interior_zero_absent_from_edges_27_39"]["factor_ids"].__setitem__(0, 0)),
        ("witness sign", lambda row: row["factor_classification"]["witness_catalog"][0]["proof"].__setitem__("left_sign", -row["factor_classification"]["witness_catalog"][0]["proof"]["left_sign"])),
        ("count", lambda row: row["factor_classification"].__setitem__("interior_zero_count", 5664)),
        ("input digest", lambda row: row["inputs"].__setitem__(next(iter(EXPECTED_INPUTS)), "0" * 64)),
        ("parent digest", lambda row: row["exact_parent_residence"].__setitem__("aggregate_controls_sha256", "0" * 64)),
    )
    for name, mutation in mutations:
        changed = deepcopy(record)
        mutation(changed)
        changed["semantic_sha256"] = semantic_seal(changed)
        try:
            verify_record(changed, expected_parent, expected_classification, absent, edge_sets)
        except AssertionError:
            cases.append(name)
        else:
            raise AssertionError(f"hostile mutation accepted: {name}")
    require(len(cases) == 10, "hostile mutation census")
    return cases


def main():
    head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=ROOT, check=True, text=True, capture_output=True).stdout.strip()
    require(head == CANDIDATE_HEAD or subprocess.run(["git", "merge-base", "--is-ancestor", CANDIDATE_HEAD, head], cwd=ROOT).returncode == 0, "candidate head ancestry")
    candidate_bytes, candidate_ids, factors, catalog_record, points = parse_sources()
    record = json.loads(candidate_bytes)
    validate_scope(record)
    base, rows, parent = parent_certificate(catalog_record, points)
    require(parent["signed_parent_bracket_count"] == 70, "70 parent brackets")
    edge_sets = edge_factor_sets()
    classification, absent = reconstruct_classification(candidate_ids, factors, base, rows, edge_sets)
    verify_record(record, parent, classification, absent, edge_sets)
    rejected = hostile_replay(record, parent, classification, absent, edge_sets)
    print("PASS raw inputs and manifest pinned; charts=(0,89,113); exact closed triangle")
    print("PASS 70/70 strict parent signs by complete simplex-Bernstein controls")
    print("PASS factor accounting interior=5665 empty=12096 unresolved=63 total=17824")
    print("PASS 77 interior-zero factors have exact witnesses and are absent from edges 27/39")
    print("PASS no unresolved factor promoted; empty and interior rules are exact sufficient conditions")
    print(f"PASS hostile mutations rejected {len(rejected)}/10")
    print("SCOPE bounded triangle only; third edge uncompiled; no infinity/global coverage/pair closure/3-of-9")


if __name__ == "__main__":
    main()
