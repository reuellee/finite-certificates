#!/usr/bin/env python3
"""Producer-independent falsifier for the factor-19069 barrier frontier.

The constructor and its verifier are treated only as frozen data.  This file
does not import either of them.  It reconstructs the signed parent factors and
factor 19069 from the pinned mathematical sources, rebuilds the derivative
provenance checks, enumerates every compactification support, and uses its own
exact univariate arithmetic for path and skeleton attacks.
"""

from __future__ import annotations

import ast
from collections import Counter
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from math import comb, gcd, lcm
from pathlib import Path
import struct
import subprocess
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OMREAL = ROOT / "ai" / "omreal"
DATA = OMREAL / "data"
CONSTRUCTOR_DIR = ROOT / "ops" / "team" / "d9-factor19069-factored-barrier-constructor"
FRONTIER = CONSTRUCTOR_DIR / "FACTORED_BARRIER_FRONTIER.json"
CONSTRUCTOR_MANIFEST = CONSTRUCTOR_DIR / "SOURCE_MANIFEST.json"
CONSTRUCTOR_RESULT = CONSTRUCTOR_DIR / "RESULT.json"
MANIFEST = HERE / "SOURCE_MANIFEST.json"

REVIEWED_REVISION = "2878addcc5d9c863ed5b2d518552b0298f08a64c"
REVIEWED_TREE = "3b6b3e563ca85782d76acfa0e3a48fc8aa031ec6"
OPENING_REVISION = "d12dbaf7cfb7312d9d603c8938dd8ad6ce62166e"
OPENING_TREE = "221e574fd705aff50f667ebc72345a36afc4f5d7"
BASE_REVISION = "b71c139a3c64cde3442252f8f3d46f2d893978c5"
BASE_TREE = "7a9da9f02369831bd34bc22f39a0bbad57725522"
EXPECTED_FRONTIER_SHA256 = "3f75eeb2f7433234206292012c527604517b516ee904e2ab1d1969e49ed1e8ca"
EXPECTED_CONSTRUCTOR_MANIFEST_SHA256 = "17bc476bfc78d629353f4fe73d24495de40de5a926aa5e8df4ed524131b3d303"
EXPECTED_CONSTRUCTOR_RESULT_SHA256 = "5d9357346077562824c4564829260d49b6fa62ceea38b7ae3f7fe5543dee029a"
EXPECTED_MANIFEST_SEMANTIC_SHA256 = "c6bbbf78f12f5740cd8966f0d530007abe13e68826ae5fd62abdddd94ca1e2ce"
TARGET_FACTOR = 19069
VARIABLES = tuple("abcdefghi")
FULL_SUPPORT = (15, 15, 15)
GROUPS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))

sys.path.insert(0, str(OMREAL))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


class Reject(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def digest_bytes(value: bytes) -> str:
    return sha256(value).hexdigest()


def digest_path(path: Path) -> str:
    state = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            state.update(block)
    return state.hexdigest()


def canonical_digest(value) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def git(*arguments: str, binary: bool = False):
    answer = subprocess.check_output(["git", *arguments], cwd=ROOT, text=not binary)
    return answer if binary else answer.strip()


def source_digest(relative: str) -> str:
    if relative == "ops/research-team/PROTOCOL.md":
        return digest_bytes(git("show", f"{REVIEWED_REVISION}:{relative}", binary=True))
    return digest_path(ROOT / relative)


def literal_assignment(path: Path, name: str):
    syntax = ast.parse(path.read_text(encoding="utf-8"))
    for node in syntax.body:
        if isinstance(node, ast.Assign) and any(
            isinstance(target, ast.Name) and target.id == name for target in node.targets
        ):
            return ast.literal_eval(node.value)
    raise Reject(f"missing literal assignment {name}")


def parse_fraction(value) -> Fraction:
    return value if isinstance(value, Fraction) else Fraction(str(value))


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def polynomial_degree(polynomial: dict) -> int:
    return max(map(sum, polynomial))


def evaluate_multivariate(polynomial: dict, point) -> Fraction:
    answer = Fraction(0)
    for exponents, coefficient in polynomial.items():
        term = Fraction(coefficient)
        for value, exponent in zip(point, exponents, strict=True):
            term *= value**exponent
        answer += term
    return answer


def derivative(polynomial: dict, coordinate: int) -> dict:
    answer = {}
    for exponents, coefficient in polynomial.items():
        power = exponents[coordinate]
        if power:
            reduced = list(exponents)
            reduced[coordinate] -= 1
            answer[tuple(reduced)] = answer.get(tuple(reduced), 0) + coefficient * power
    return {key: value for key, value in answer.items() if value}


def sparse_polynomial(polynomial: dict) -> list[dict]:
    return [
        {"exponents": list(exponents), "coefficient": int(coefficient)}
        for exponents, coefficient in sorted(polynomial.items())
        if coefficient
    ]


def decode_sparse(records: list[dict], marker: str) -> dict:
    require(all(set(row) == {"exponents", "coefficient"} for row in records), f"{marker} sparse schema")
    keys = [tuple(row["exponents"]) for row in records]
    require(len(keys) == len(set(keys)), f"{marker} duplicate sparse exponent")
    require(all(len(key) == 9 and all(isinstance(value, int) and value >= 0 for value in key) for key in keys), f"{marker} exponent")
    require(all(isinstance(row["coefficient"], int) and row["coefficient"] for row in records), f"{marker} coefficient")
    return {key: row["coefficient"] for key, row in zip(keys, records, strict=True)}


def multiply_linear(polynomial, constant: Fraction, slope: Fraction):
    answer = [Fraction(0)] * (len(polynomial) + 1)
    for index, coefficient in enumerate(polynomial):
        answer[index] += coefficient * constant
        answer[index + 1] += coefficient * slope
    return answer


def segment_polynomial(polynomial: dict, left, right):
    degree = polynomial_degree(polynomial)
    answer = [Fraction(0)] * (degree + 1)
    differences = tuple(r - l for l, r in zip(left, right, strict=True))
    for exponents, coefficient in polynomial.items():
        term = [Fraction(coefficient)]
        for coordinate, exponent in enumerate(exponents):
            for _ in range(exponent):
                term = multiply_linear(term, left[coordinate], differences[coordinate])
        for index, value in enumerate(term):
            answer[index] += value
    return trim(answer)


def trim(polynomial):
    answer = list(map(Fraction, polynomial))
    while len(answer) > 1 and answer[-1] == 0:
        answer.pop()
    return answer


def univariate_value(polynomial, value: Fraction) -> Fraction:
    answer = Fraction(0)
    for coefficient in reversed(polynomial):
        answer = answer * value + coefficient
    return answer


def polynomial_divrem(dividend, divisor):
    dividend = trim(dividend)
    divisor = trim(divisor)
    require(bool(divisor) and any(divisor), "zero Sturm divisor")
    while len(dividend) >= len(divisor) and any(dividend):
        quotient = dividend[-1] / divisor[-1]
        shift = len(dividend) - len(divisor)
        for index, coefficient in enumerate(divisor):
            dividend[index + shift] -= quotient * coefficient
        dividend = trim(dividend)
        if len(dividend) == 1 and dividend[0] == 0:
            return []
    return dividend


def sturm_sequence(polynomial):
    polynomial = trim(polynomial)
    if len(polynomial) <= 1:
        return (polynomial,)
    differentiated = trim(index * polynomial[index] for index in range(1, len(polynomial)))
    sequence = [polynomial, differentiated]
    while differentiated:
        remainder = [-value for value in polynomial_divrem(polynomial, differentiated)]
        if not remainder:
            break
        sequence.append(remainder)
        polynomial, differentiated = differentiated, remainder
    return tuple(sequence)


def sign_variations(sequence, value: Fraction) -> int:
    signs = []
    for polynomial in sequence:
        evaluated = univariate_value(polynomial, value)
        if evaluated:
            signs.append(1 if evaluated > 0 else -1)
    return sum(left != right for left, right in zip(signs, signs[1:]))


def open_root_count(polynomial, left=Fraction(0), right=Fraction(1)) -> int:
    polynomial = trim(polynomial)
    require(univariate_value(polynomial, left) != 0, "Sturm left endpoint root")
    require(univariate_value(polynomial, right) != 0, "Sturm right endpoint root")
    sequence = sturm_sequence(polynomial)
    return sign_variations(sequence, left) - sign_variations(sequence, right)


def divide_one_minus_t(polynomial):
    polynomial = trim(polynomial)
    require(len(polynomial) >= 2, "constant endpoint-zero polynomial")
    quotient = [polynomial[0]]
    for index in range(1, len(polynomial) - 1):
        quotient.append(polynomial[index] + quotient[-1])
    require(polynomial[-1] == -quotient[-1], "nonexact endpoint division")
    return trim(quotient)


def strict_open_path_certificate(polynomial):
    polynomial = trim(polynomial)
    require(univariate_value(polynomial, Fraction(0)) > 0, "path start sign")
    multiplicity = 0
    reduced = polynomial
    while univariate_value(reduced, Fraction(1)) == 0:
        reduced = divide_one_minus_t(reduced)
        multiplicity += 1
    require(univariate_value(reduced, Fraction(0)) > 0, "reduced start sign")
    require(univariate_value(reduced, Fraction(1)) > 0, "reduced endpoint sign")
    roots = open_root_count(reduced)
    require(roots == 0, "parent factor changes sign on boundary path")
    return {"endpoint_zero_multiplicity": multiplicity, "reduced_open_root_count": roots}


def positive_closed_segment(polynomial) -> None:
    polynomial = trim(polynomial)
    require(univariate_value(polynomial, Fraction(0)) > 0, "skeleton start sign")
    require(univariate_value(polynomial, Fraction(1)) > 0, "skeleton end sign")
    require(open_root_count(polynomial) == 0, "skeleton parent path")


def primitive_integer(polynomial):
    coefficients = trim(polynomial)
    denominator = 1
    for coefficient in coefficients:
        denominator = lcm(denominator, coefficient.denominator)
    integers = [int(coefficient * denominator) for coefficient in coefficients]
    divisor = 0
    for coefficient in integers:
        divisor = gcd(divisor, abs(coefficient))
    integers = [coefficient // max(divisor, 1) for coefficient in integers]
    if integers[-1] < 0:
        integers = [-coefficient for coefficient in integers]
    return integers


def multidegree(polynomial: dict) -> tuple[int, int, int]:
    return tuple(
        max(sum(exponents[index] for index in variables) for exponents in polynomial)
        for variables in GROUPS
    )


def term_support(exponents, degrees) -> tuple[int, int, int]:
    answer = []
    for variables, degree in zip(GROUPS, degrees, strict=True):
        affine = tuple(exponents[index] for index in variables)
        homogeneous = (degree - sum(affine),) + affine
        require(homogeneous[0] >= 0 and sum(homogeneous) == degree, "homogenization")
        answer.append(sum((power > 0) << row for row, power in enumerate(homogeneous)))
    return tuple(answer)


def restriction_signs(polynomial: dict, degrees, face):
    return {
        1 if coefficient > 0 else -1
        for exponents, coefficient in polynomial.items()
        if all(
            support & ~allowed == 0
            for support, allowed in zip(term_support(exponents, degrees), face, strict=True)
        )
    }


def parent_restriction_state(polynomial: dict, degrees, face) -> str:
    signs = restriction_signs(polynomial, degrees, face)
    if not signs:
        return "ZERO"
    if signs == {1}:
        return "RIGHT"
    if signs == {-1}:
        return "WRONG"
    require(signs == {-1, 1}, "parent restriction state")
    return "MIXED"


def factor_restriction_state(polynomial: dict, degrees, face) -> str:
    signs = restriction_signs(polynomial, degrees, face)
    if not signs:
        return "IDENTICALLY_ZERO"
    if signs == {1}:
        return "BERNSTEIN_POSITIVE"
    if signs == {-1}:
        return "BERNSTEIN_NEGATIVE"
    require(signs == {-1, 1}, "factor restriction state")
    return "BERNSTEIN_MIXED_UNRESOLVED"


def face_dimension(face) -> int:
    return sum(mask.bit_count() - 1 for mask in face)


def candidate_ids() -> tuple[int, ...]:
    raw = (DATA / "DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin").read_bytes()
    header_size = struct.calcsize("<8sIII")
    magic, parent, factor_count, count = struct.unpack_from("<8sIII", raw)
    require((magic, parent, factor_count, count) == (b"D3PFC001", 2599, 26740, 17824), "candidate header")
    require(len(raw) == header_size + 4 * count, "candidate byte length")
    identifiers = tuple(value[0] for value in struct.iter_unpack("<I", raw[header_size:]))
    require(identifiers == tuple(sorted(set(identifiers))), "candidate ordering")
    return identifiers


def source_replay() -> dict:
    records = [
        json.loads(line)
        for line in (OMREAL / "certs_4_8.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    require(len(records) == 2628 and records[2599]["verdict"] == "REALIZABLE", "parent record")
    parent_sources, parent_digest = gate.parent_polynomials(records[2599])
    require(len(parent_sources) == 70, "parent source count")
    signed_parents = tuple(
        (label, {exponents: target * coefficient for exponents, coefficient in polynomial.items()})
        for label, target, polynomial, _terms in parent_sources
    )
    require(len({label for label, _polynomial in signed_parents}) == 70, "parent labels")

    require(TARGET_FACTOR in candidate_ids(), "factor membership")
    _occurrences, _occurrence_factor, factors = labeled.factor_polynomials()
    factor = factors[TARGET_FACTOR]
    require(polynomial_degree(factor) == 6, "factor degree")
    require(multidegree(factor) == (2, 2, 2), "factor multidegree")
    require(len(factor) == 108, "factor term count")

    parent_degrees = tuple(multidegree(polynomial) for _label, polynomial in signed_parents)
    nonexcluded = []
    excluded = 0
    for face in product(range(1, 16), repeat=3):
        states = tuple(
            parent_restriction_state(polynomial, degrees, face)
            for (_label, polynomial), degrees in zip(signed_parents, parent_degrees, strict=True)
        )
        if "WRONG" in states:
            excluded += 1
        else:
            nonexcluded.append(
                {
                    "support": face,
                    "dimension": face_dimension(face),
                    "classification": "AMBIGUOUS" if "MIXED" in states else "CONTAINED",
                }
            )
    require(excluded == 3364 and len(nonexcluded) == 11, "parent support census")
    expected_supports = (
        (1, 1, 1), (1, 1, 5), (3, 1, 1), (3, 1, 5), (3, 1, 15),
        (3, 3, 7), (3, 3, 15), (7, 7, 7), (15, 1, 15), (15, 7, 15),
        FULL_SUPPORT,
    )
    require(tuple(row["support"] for row in nonexcluded) == expected_supports, "nonexcluded support identities")

    parent_face = json.loads(
        (DATA / "DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json").read_text(encoding="utf-8")
    )
    source_rows = {tuple(row["support"]): row for row in parent_face["nonexcluded_support_faces"]}
    require(set(source_rows) == set(expected_supports), "parent-face witness support coverage")
    pinned_sample = gate.normalized_values(records[2599]["matrix"])
    boundary = []
    for summary in nonexcluded[:-1]:
        support = summary["support"]
        source_row = source_rows[support]
        witness = tuple(parse_fraction(value) for value in source_row["witness"])
        require(all(support[index] & 1 for index in range(3)), "affine witness chart")
        for block, mask in enumerate(support):
            for row in (1, 2, 3):
                require((witness[3 * block + row - 1] > 0) == bool(mask & (1 << row)), "witness support")
        values = tuple(evaluate_multivariate(polynomial, witness) for _label, polynomial in signed_parents)
        require(all(value >= 0 for value in values), "weak-sign witness")
        zero_count = sum(value == 0 for value in values)
        path_proofs = []
        rejection = None
        for label, polynomial in signed_parents:
            restricted = segment_polynomial(polynomial, pinned_sample, witness)
            try:
                path_proofs.append({"label": label, **strict_open_path_certificate(restricted)})
            except Reject as error:
                rejection = {
                    "label": label,
                    "reason": str(error),
                    "restricted_signed_parent_polynomial_coefficients_ascending": [
                        fraction_text(value) for value in restricted
                    ],
                    "tested_parent_factors_before_rejection": len(path_proofs),
                }
                break
        boundary.append(
            {
                **summary,
                "witness": tuple(map(fraction_text, witness)),
                "witness_zero_parent_factors": zero_count,
                "factor19069_restriction": factor_restriction_state(factor, (2, 2, 2), support),
                "path_proofs": path_proofs,
                "path_rejection": rejection,
            }
        )

    require(Counter(row["factor19069_restriction"] for row in boundary) == {
        "IDENTICALLY_ZERO": 8,
        "BERNSTEIN_MIXED_UNRESOLVED": 2,
    }, "factor boundary census")
    boundary_by_support = {row["support"]: row for row in boundary}
    require(boundary_by_support[(15, 7, 15)]["path_rejection"] is None, "[15,7,15] path")
    require(len(boundary_by_support[(15, 7, 15)]["path_proofs"]) == 70, "[15,7,15] proof count")
    require(boundary_by_support[(1, 1, 1)]["path_rejection"]["label"] == "2578", "[1,1,1] rejection label")
    require(boundary_by_support[(1, 1, 1)]["path_rejection"]["reason"] == "reduced endpoint sign", "[1,1,1] rejection reason")

    edges = tuple(literal_assignment(OMREAL / "verify_diag3_pair_fullsupport_safe_segment_walls.py", "EDGES"))
    cover = json.loads((DATA / "DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json").read_text(encoding="utf-8"))
    selected = tuple(cover["source_bank"]["selected_edge_indices"])
    require(len(edges) == 105 and len(selected) == len(set(selected)) == 40, "skeleton source")
    with np.load(gate.POINT_BANK, allow_pickle=False) as source:
        matrices = np.asarray(source["chart_matrix"], dtype=np.int64)
    require(matrices.shape == (178, 4, 8), "point-bank shape")
    points = tuple(gate.normalized_values(matrix.tolist()) for matrix in matrices)
    root_counts = {}
    path_checks = 0
    for edge_index in selected:
        left_index, right_index = edges[edge_index]
        for _label, polynomial in signed_parents:
            positive_closed_segment(segment_polynomial(polynomial, points[left_index], points[right_index]))
            path_checks += 1
        restricted = segment_polynomial(factor, points[left_index], points[right_index])
        require(univariate_value(restricted, Fraction(0)) != 0, "wall edge start")
        require(univariate_value(restricted, Fraction(1)) != 0, "wall edge end")
        root_counts[str(edge_index)] = open_root_count(restricted)
    require(path_checks == 2800, "skeleton path checks")
    require([int(edge) for edge, count in root_counts.items() if count] == [39], "rooted skeleton edge")
    require(root_counts["39"] == 1, "edge-39 root count")
    edge39_vertices = edges[39]
    edge39_polynomial = primitive_integer(
        segment_polynomial(factor, points[edge39_vertices[0]], points[edge39_vertices[1]])
    )
    coordinate_map = [
        {
            "constant": fraction_text(points[edge39_vertices[0]][coordinate]),
            "linear": fraction_text(points[edge39_vertices[1]][coordinate] - points[edge39_vertices[0]][coordinate]),
        }
        for coordinate in range(9)
    ]
    return {
        "parent_digest": parent_digest,
        "signed_parents": signed_parents,
        "factor": factor,
        "boundary": boundary,
        "root_counts": root_counts,
        "path_checks": path_checks,
        "edge39_vertices": list(edge39_vertices),
        "edge39_polynomial": edge39_polynomial,
        "edge39_coordinate_map": coordinate_map,
    }


def validate_manifest(candidate: dict) -> None:
    semantic = dict(candidate)
    stored = semantic.pop("semantic_sha256")
    require(canonical_digest(semantic) == stored == EXPECTED_MANIFEST_SEMANTIC_SHA256, "falsifier manifest semantic digest")
    require(candidate["format"] == "d9-factor19069-factored-barrier-falsifier-source-manifest-v1", "manifest format")
    require(candidate["reviewed_revision"] == REVIEWED_REVISION, "manifest reviewed revision")
    require(candidate["reviewed_tree"] == REVIEWED_TREE, "manifest reviewed tree")
    require(candidate["opening_revision"] == OPENING_REVISION and candidate["opening_tree"] == OPENING_TREE, "manifest opening pin")
    require(candidate["base_revision"] == BASE_REVISION and candidate["base_tree"] == BASE_TREE, "manifest base pin")
    require(candidate["source_count"] == len(candidate["source_sha256"]), "manifest source count")
    for relative, expected in candidate["source_sha256"].items():
        require(source_digest(relative) == expected, f"source pin {relative}")
    expected_artifacts = {
        "ops/team/d9-factor19069-factored-barrier-constructor/FACTORED_BARRIER_FRONTIER.json": EXPECTED_FRONTIER_SHA256,
        "ops/team/d9-factor19069-factored-barrier-constructor/SOURCE_MANIFEST.json": EXPECTED_CONSTRUCTOR_MANIFEST_SHA256,
        "ops/team/d9-factor19069-factored-barrier-constructor/RESULT.json": EXPECTED_CONSTRUCTOR_RESULT_SHA256,
    }
    require(candidate["reviewed_artifact_sha256"] == expected_artifacts, "reviewed artifact pins")
    require(candidate["drive_connector_used"] is False and candidate["github_write"] is False, "manifest authority")


def validate_circuit(candidate: dict, replay: dict) -> None:
    circuit = candidate["factor_circuit"]
    require(canonical_digest(circuit) == candidate["factor_circuit_semantic_sha256"], "factor circuit semantic digest")
    require(circuit["format"] == "factor-circuit-dB-wedge-df-v1", "circuit format")
    require(circuit["coordinates"] == list(VARIABLES), "circuit coordinates")
    wall = circuit["wall_polynomial"]
    require(wall["node_id"] == "f_19069", "wall node")
    require((wall["degree"], wall["multidegree"], wall["term_count"]) == (6, [2, 2, 2], 108), "wall census")
    require(decode_sparse(wall["sparse_polynomial"], "wall") == replay["factor"], "wall source polynomial")

    expected_parent_ids = []
    parent_nodes = circuit["parent_factor_nodes"]
    require(len(parent_nodes) == 70, "parent node count")
    for index, (node, (label, polynomial)) in enumerate(zip(parent_nodes, replay["signed_parents"], strict=True)):
        expected_id = f"H_{index:02d}_{label}"
        expected_parent_ids.append(expected_id)
        require(node["node_id"] == expected_id and node["label"] == label, "parent factor ordering")
        require(node["degree"] == polynomial_degree(polynomial), "parent factor degree")
        require(node["term_count"] == len(polynomial), "parent factor term count")
        require(decode_sparse(node["sparse_polynomial"], f"parent {index}") == polynomial, "parent factor source polynomial")
    require(len(set(expected_parent_ids)) == 70, "parent node uniqueness")
    barrier = circuit["barrier"]
    require(set(barrier) == {"node_id", "operation", "ordered_factor_node_ids", "factor_count", "total_degree", "expanded_polynomial_present"}, "barrier schema")
    require(barrier["node_id"] == "B" and barrier["operation"] == "PRODUCT", "barrier operation")
    require(barrier["ordered_factor_node_ids"] == expected_parent_ids, "barrier factor provenance")
    require(barrier["factor_count"] == 70 and barrier["total_degree"] == 90, "barrier census")
    require(barrier["expanded_polynomial_present"] is False, "expanded barrier")

    derivative_nodes = circuit["barrier_derivative_nodes"]
    require(len(derivative_nodes) == 9, "dB coordinate count")
    nonzero_counts = {}
    for coordinate, (variable, node) in enumerate(zip(VARIABLES, derivative_nodes, strict=True)):
        require(node["node_id"] == f"dB_d{variable}" and node["coordinate_index"] == coordinate, "dB coordinate ordering")
        require(node["operation"] == "SUM_OVER_ALL_70_FACTORS_OF_DH_I_TIMES_PRODUCT_J_NE_I_H_J", "dB operation")
        require(len(node["summands"]) == 70, "dB summand count")
        nonzero_counts[variable] = 0
        for index, (summand, (_label, polynomial)) in enumerate(zip(node["summands"], replay["signed_parents"], strict=True)):
            expected_derivative = derivative(polynomial, coordinate)
            nonzero_counts[variable] += bool(expected_derivative)
            require(summand["differentiated_factor_index"] == index, "dB differentiated factor provenance")
            require(summand["multiply_all_factor_indices_except"] == index, "dB complementary factor provenance")
            require(decode_sparse(summand["derivative_sparse_polynomial"], f"dB {coordinate}:{index}") == expected_derivative, "dB derivative membership")

    wall_derivatives = circuit["wall_derivative_nodes"]
    require(len(wall_derivatives) == 9, "df coordinate count")
    for coordinate, (variable, node) in enumerate(zip(VARIABLES, wall_derivatives, strict=True)):
        require(node["node_id"] == f"df_d{variable}" and node["coordinate_index"] == coordinate, "df coordinate ordering")
        require(decode_sparse(node["sparse_polynomial"], f"df {coordinate}") == derivative(replay["factor"], coordinate), "df derivative membership")

    expected_pairs = [(left, right) for left in range(9) for right in range(left + 1, 9)]
    wedges = circuit["wedge_equation_nodes"]
    require(len(wedges) == 36, "wedge equation count")
    for node, (left, right) in zip(wedges, expected_pairs, strict=True):
        lvar, rvar = VARIABLES[left], VARIABLES[right]
        require(node["node_id"] == f"wedge_{lvar}_{rvar}", "wedge ordering")
        require(node["coordinate_pair"] == [left, right], "wedge pair coverage")
        require(node["operation"] == "dB_left*df_right-dB_right*df_left", "wedge operation")
        require(node["inputs"] == [f"dB_d{lvar}", f"df_d{rvar}", f"dB_d{rvar}", f"df_d{lvar}"], "wedge provenance")
    require(circuit["equation_contract"] == "f_19069=0 AND all_36_coefficients_of_dB_wedge_df=0", "equation contract")

    census = candidate["circuit_census"]
    require(census["parent_factor_nodes"] == 70, "circuit parent census")
    require(census["parent_sparse_terms"] == 209, "circuit parent terms")
    require(census["barrier_total_degree"] == 90, "circuit barrier degree")
    require(census["dB_coordinate_nodes"] == 9 and census["dB_summands"] == 630, "circuit dB census")
    require(census["nonzero_dH_factors_by_coordinate"] == nonzero_counts, "circuit nonzero derivative census")
    require(census["df_coordinate_nodes"] == 9 and census["wedge_equation_nodes"] == 36, "circuit wedge census")
    require(census["expanded_barrier_monomials"] is None and census["expanded_product_used"] is False, "expanded product dependence")


def validate_boundary(candidate: dict, replay: dict) -> None:
    boundary = candidate["true_boundary_frontier"]
    require(boundary["compactification_model"] == "(Delta^3)^3" and boundary["atlas_charts"] == 64, "boundary model")
    require(boundary["ambient_product_support_strata"] == 3375, "boundary ambient support census")
    require(boundary["parent_bernstein_excluded_support_strata"] == 3364, "boundary excluded support census")
    require(boundary["proper_nonexcluded_candidate_strata"] == len(boundary["records"]) == 10, "boundary candidate census")
    require([tuple(record["support"]) for record in boundary["records"]] == [row["support"] for row in replay["boundary"]], "boundary support completeness")

    certified = 0
    for record, expected in zip(boundary["records"], replay["boundary"], strict=True):
        require(record["dimension"] == expected["dimension"], "boundary dimension")
        require(record["parent_support_gate_classification"] == expected["classification"], "boundary parent classification")
        require(tuple(record["witness"]) == expected["witness"], "boundary witness")
        require(record["witness_zero_parent_factors"] == expected["witness_zero_parent_factors"], "boundary weak-sign provenance")
        require(record["factor19069_restriction"] == expected["factor19069_restriction"], "boundary factor restriction")
        path = record["parent_component_closure_path"]
        require(path["path"] == "x(t)=(1-t)*pinned_parent_sample+t*witness" and path["parameter_domain"] == "0<=t<1", "boundary path provenance")
        require(path["parent_factor_proof_count"] == len(expected["path_proofs"]), "boundary path proof count")
        require(path["parent_factor_proof_semantic_sha256"] == canonical_digest(expected["path_proofs"]), "boundary path proof digest")
        if expected["path_rejection"] is None:
            certified += 1
            require(path["status"] == "CERTIFIED_LINEAR_PATH_FROM_PINNED_SAMPLE_IN_P_FOR_0_LE_T_LT_1", "boundary certified path status")
            require(path["first_rejection"] is None, "boundary false path rejection")
        else:
            require(path["status"] == "TESTED_LINEAR_PATH_REJECTED_NO_ALTERNATIVE_EXACT_PATH_CERTIFIED", "boundary rejected path scope")
            require(path["first_rejection"] == expected["path_rejection"], "boundary first rejection provenance")
        require(record["wall_component_residence"] == "UNCLASSIFIED_FAIL_CLOSED", "boundary wall residence")
    require(certified == boundary["certified_witness_paths_to_pinned_parent_closure"] == 1, "boundary certified path census")
    require(boundary["wall_component_residence_classified_strata"] == 0, "boundary classified residence census")
    first = boundary["first_unclassified_boundary_stratum"]
    require(first["support"] == [1, 1, 1], "first unclassified boundary support")
    require(first["factor19069_restriction"] == "IDENTICALLY_ZERO", "first unclassified boundary restriction")
    require(first["obligation"] == "DECOMPOSE_PARENT_RESIDENT_BOUNDARY_WALL_GERM_AND_ATTACH_IT_TO_AN_INTERIOR_WALL_COMPONENT", "first unclassified boundary obligation")
    require(first["record_semantic_sha256"] == canonical_digest(boundary["records"][0]), "first unclassified boundary digest")
    require(set(boundary["true_parent_boundary_kept_distinct_from"]) == {
        "SOLVER_BOUNDARY", "BOX_BOUNDARY", "COLLAR_BOUNDARY", "SKELETON_EDGE_ENDPOINT"
    }, "true/artificial boundary separation")


def validate_skeleton(candidate: dict, replay: dict) -> None:
    skeleton = candidate["fixed_skeleton_accounting"]
    require(skeleton["all_40_edges_retain_all_70_parent_tags"] is True, "skeleton parent tag claim")
    require(skeleton["parent_path_tag_checks"] == replay["path_checks"] == 2800, "skeleton parent tag census")
    require(skeleton["factor19069_open_root_counts_by_edge"] == replay["root_counts"], "skeleton root census")
    anchor = skeleton["exact_attached_wall_anchor"]
    require(anchor["sample_id"] == "WALL_ANCHOR_EDGE39_ROOT0", "edge-39 anchor id")
    require(anchor["kind"] == "RATIONAL_UNIVARIATE_POINT_ON_FIXED_SKELETON", "edge-39 anchor kind")
    require(anchor["edge_index"] == 39 and anchor["edge_source_vertices"] == replay["edge39_vertices"], "edge-39 anchor provenance")
    require(anchor["parameter_minimal_polynomial_coefficients_ascending"] == replay["edge39_polynomial"], "edge-39 anchor polynomial")
    interval = tuple(parse_fraction(value) for value in anchor["parameter_isolating_interval"])
    require(Fraction(0) < interval[0] < interval[1] < Fraction(1), "edge-39 isolating interval")
    require(open_root_count(replay["edge39_polynomial"], interval[0], interval[1]) == 1, "edge-39 isolated root")
    require(anchor["coordinate_map"] == replay["edge39_coordinate_map"], "edge-39 coordinate map")
    require(anchor["attachment"] == "LIES_ON_FIXED_SKELETON_EDGE_39", "edge-39 local attachment")
    require(anchor["barrier_critical_sample"] is False, "edge-39 critical overreach")
    require(skeleton["global_wall_component_count"] is None, "global wall component count")
    require(skeleton["global_attached_component_count"] is None, "global attached component count")
    require(skeleton["global_unattached_component_count"] is None, "global unattached component count")
    require(skeleton["attachment_classification_complete"] is False, "attachment completeness")


def validate_frontier(candidate: dict, replay: dict) -> None:
    semantic = dict(candidate)
    stored_digest = semantic.pop("semantic_sha256")
    require(canonical_digest(semantic) == stored_digest, "frontier semantic digest")
    require(candidate["format"] == "d9-factor19069-factored-barrier-frontier-v1", "frontier format")
    require(candidate["track_id"] == "d9-factor19069-factored-barrier-constructor", "frontier track")
    require(candidate["opening_revision"] == OPENING_REVISION and candidate["opening_tree"] == OPENING_TREE, "frontier opening pin")
    require(candidate["base_revision"] == BASE_REVISION and candidate["base_tree"] == BASE_TREE, "frontier base pin")
    target = candidate["target"]
    require(target == {
        "ambient_parameter_dimension": 9,
        "factor_id": 19069,
        "fixed_skeleton_edges": 40,
        "parent_index": 2599,
        "parent_sign_digest": replay["parent_digest"],
        "parent_sign_factors": 70,
    }, "target scope")
    validate_circuit(candidate, replay)

    interior = candidate["strict_interior_critical_frontier"]
    require(interior["systems_constructed"] == len(interior["systems"]) == 1, "critical system count")
    require(interior["connected_components_sampled"] == 0, "generic/component sample count")
    require(interior["zero_dimensional_components_sampled"] == 0, "zero-dimensional component count")
    require(interior["positive_dimensional_components_sampled"] == 0, "positive-dimensional component count")
    require(interior["singular_pieces_discarded"] == 0, "singular piece scope")
    system = interior["systems"][0]
    system_semantic = dict(system)
    system_digest = system_semantic.pop("semantic_sha256")
    require(canonical_digest(system_semantic) == system_digest, "critical system digest")
    require(system["stratum_id"] == "FB-C0-STRICT-INTERIOR-FULL-SUPPORT" and system["support"] == [15, 15, 15], "critical stratum identity")
    require(system["ambient_dimension"] == 9, "critical ambient dimension")
    require(system["equalities"] == ["f_19069=0", "all_36_coefficients_of_dB_wedge_df=0"], "critical equality membership")
    expected_inequalities = [f"H_{index:02d}_{label}>0" for index, (label, _polynomial) in enumerate(replay["signed_parents"])]
    require(system["strict_inequalities"] == expected_inequalities, "critical parent factor membership")
    require(system["connected_parent_selector"] == "EXACT_PATH_IN_STRICT_PARENT_SIGN_SET_TO_PINNED_SAMPLE_REQUIRED", "critical parent-component selector")
    require(system["factor_circuit_semantic_sha256"] == candidate["factor_circuit_semantic_sha256"], "critical circuit binding")
    require(system["possible_component_dimensions"] == list(range(9)), "generic-only component omission")
    require(system["singular_wall_pieces_included"] is True, "singular wall omission")
    require(system["positive_dimensional_pieces_required"] is True, "positive-dimensional omission")
    require(system["component_decomposition_status"] == "UNSAMPLED_FAIL_CLOSED", "critical decomposition status")
    first = interior["first_unsampled_component_or_stratum"]
    require(first["kind"] == "EXACT_SEMIALGEBRAIC_STRATUM_PENDING_CONNECTED_COMPONENT_DECOMPOSITION", "first unsampled kind")
    require(first["stratum_id"] == system["stratum_id"] and first["stratum_semantic_sha256"] == system_digest, "first unsampled binding")
    require(first["reason"] == "NO_PRODUCER_INDEPENDENT_EXACT_CONNECTED_COMPONENT_DECOMPOSITION_OR_THOM_ENCODING_WAS_COMPLETED_UNDER_THE_CEILING", "first unsampled reason")

    validate_boundary(candidate, replay)
    validate_skeleton(candidate, replay)
    resources = candidate["resource_accounting"]
    require(resources["max_exact_solver_component_nodes"] == 500000, "resource ceiling")
    require(resources["exact_solver_component_nodes_used"] == 0 and resources["ceiling_crossed"] is False, "resource accounting")
    require(resources["stop_trigger"] == "MISSING_EXACT_CRITICAL_LOCUS_COMPONENT_DECOMPOSITION_AND_PATH_CERTIFICATE", "stop trigger")
    require(resources["paid_or_external_compute"] is False, "compute authority")
    require(candidate["endpoint"] == "HASH_PINNED_FACTORED_BARRIER_CRITICAL_COMPONENT_FRONTIER_WITH_FIRST_UNSAMPLED_COMPONENT", "null endpoint")
    require(candidate["classification"] == "EXACT_FAIL_CLOSED_FACTORED_BARRIER_COMPONENT_NULL", "null classification")
    require(candidate["producer_independent_certificate_present"] is False, "certificate scope")
    require(candidate["ledger_change_recommended"] == "none" and candidate["theorem_ledger"] == "2/9", "ledger scope")
    require("NO_COMPLETE_COMPONENT_TO_SKELETON_ATTACHMENT_CLASSIFICATION" in candidate["nonconsequences"], "attachment nonconsequence")
    require("NO_9DVL_SCORE_CHANGE" in candidate["nonconsequences"], "ledger nonconsequence")


def validate_result(candidate: dict, frontier: dict, manifest: dict) -> None:
    require(candidate["format"] == "d9-factor19069-factored-barrier-constructor-result-v1", "result format")
    require(candidate["opening_revision"] == OPENING_REVISION and candidate["opening_tree"] == OPENING_TREE, "result opening pin")
    require(candidate["outcome"] == "pass", "constructor result outcome")
    require(candidate["classification"] == frontier["classification"] and candidate["endpoint"] == frontier["endpoint"], "result endpoint binding")
    require(candidate["frontier_sha256"] == EXPECTED_FRONTIER_SHA256, "result frontier byte pin")
    require(candidate["frontier_semantic_sha256"] == frontier["semantic_sha256"], "result frontier semantic pin")
    require(candidate["source_manifest_sha256"] == EXPECTED_CONSTRUCTOR_MANIFEST_SHA256, "result source manifest pin")
    require(candidate["factor_circuit_semantic_sha256"] == frontier["factor_circuit_semantic_sha256"], "result circuit pin")
    require(candidate["critical_frontier"]["connected_components_sampled"] == 0, "result component scope")
    require(candidate["critical_frontier"]["positive_dimensional_components_sampled"] == 0, "result positive-dimensional scope")
    require(candidate["true_boundary"]["wall_component_residence_classified_strata"] == 0, "result boundary residence")
    require(candidate["true_boundary"]["first_unclassified_support"] == [1, 1, 1], "result boundary obstruction")
    require(candidate["fixed_skeleton"]["global_component_inference_from_anchor"] is False, "result edge-39 scope")
    require(candidate["fixed_skeleton"]["attachment_classification_complete"] is False, "result attachment scope")
    require(candidate["producer_independent_certificate_present"] is False, "result independent certificate scope")
    require(candidate["ledger_change_recommended"] == "none" and candidate["theorem_ledger"] == "2/9", "result ledger")
    require(manifest["semantic_sha256"] == frontier["source_manifest_semantic_sha256"], "constructor manifest/frontier binding")


def reseal(candidate: dict) -> dict:
    circuit_digest = canonical_digest(candidate["factor_circuit"])
    candidate["factor_circuit_semantic_sha256"] = circuit_digest
    systems = candidate["strict_interior_critical_frontier"]["systems"]
    for system in systems:
        system["factor_circuit_semantic_sha256"] = circuit_digest
        system["semantic_sha256"] = canonical_digest({key: value for key, value in system.items() if key != "semantic_sha256"})
    if systems:
        candidate["strict_interior_critical_frontier"]["first_unsampled_component_or_stratum"]["stratum_semantic_sha256"] = systems[0]["semantic_sha256"]
    records = candidate["true_boundary_frontier"]["records"]
    if records:
        candidate["true_boundary_frontier"]["first_unclassified_boundary_stratum"]["record_semantic_sha256"] = canonical_digest(records[0])
    candidate["semantic_sha256"] = canonical_digest({key: value for key, value in candidate.items() if key != "semantic_sha256"})
    return candidate


def hostile_mutations(stored: dict, replay: dict) -> list[str]:
    mutations = []

    def add(marker: str, edit) -> None:
        candidate = deepcopy(stored)
        edit(candidate)
        mutations.append((marker, reseal(candidate)))

    add("barrier factor provenance", lambda c: c["factor_circuit"]["barrier"]["ordered_factor_node_ids"].pop())
    add("parent factor ordering", lambda c: c["factor_circuit"]["parent_factor_nodes"].__setitem__(slice(0, 2), list(reversed(c["factor_circuit"]["parent_factor_nodes"][:2]))))
    add("barrier schema", lambda c: c["factor_circuit"]["barrier"].__setitem__("expanded_polynomial", [1]))
    add("parent factor source polynomial", lambda c: c["factor_circuit"]["parent_factor_nodes"][0]["sparse_polynomial"][0].__setitem__("coefficient", 99))
    add("dB summand count", lambda c: c["factor_circuit"]["barrier_derivative_nodes"][0]["summands"].pop())
    add("dB complementary factor provenance", lambda c: c["factor_circuit"]["barrier_derivative_nodes"][0]["summands"][0].__setitem__("multiply_all_factor_indices_except", 1))
    add("dB derivative membership", lambda c: c["factor_circuit"]["barrier_derivative_nodes"][1]["summands"][3]["derivative_sparse_polynomial"].append({"exponents": [0] * 9, "coefficient": 1}))
    add("wedge equation count", lambda c: c["factor_circuit"]["wedge_equation_nodes"].pop())
    add("wedge provenance", lambda c: c["factor_circuit"]["wedge_equation_nodes"][0]["inputs"].__setitem__(1, "df_da"))
    add("generic-only component omission", lambda c: c["strict_interior_critical_frontier"]["systems"][0].__setitem__("possible_component_dimensions", [0]))
    add("positive-dimensional omission", lambda c: c["strict_interior_critical_frontier"]["systems"][0].__setitem__("positive_dimensional_pieces_required", False))
    add("singular wall omission", lambda c: c["strict_interior_critical_frontier"]["systems"][0].__setitem__("singular_wall_pieces_included", False))
    add("critical parent-component selector", lambda c: c["strict_interior_critical_frontier"]["systems"][0].__setitem__("connected_parent_selector", "SIGNS_ONLY"))
    add("generic/component sample count", lambda c: c["strict_interior_critical_frontier"].__setitem__("connected_components_sampled", 1))
    add("boundary support completeness", lambda c: c["true_boundary_frontier"]["records"].__setitem__(0, deepcopy(c["true_boundary_frontier"]["records"][1])))
    add("boundary support completeness", lambda c: c["true_boundary_frontier"]["records"].__setitem__(-1, deepcopy(c["true_boundary_frontier"]["records"][-2])))
    add("boundary rejected path scope", lambda c: c["true_boundary_frontier"]["records"][0]["parent_component_closure_path"].__setitem__("status", "CERTIFIED_LINEAR_PATH_FROM_PINNED_SAMPLE_IN_P_FOR_0_LE_T_LT_1"))
    add("boundary certified path status", lambda c: c["true_boundary_frontier"]["records"][-1]["parent_component_closure_path"].__setitem__("status", "TESTED_LINEAR_PATH_REJECTED_NO_ALTERNATIVE_EXACT_PATH_CERTIFIED"))
    add("boundary factor restriction", lambda c: c["true_boundary_frontier"]["records"][7].__setitem__("factor19069_restriction", "IDENTICALLY_ZERO"))
    add("true/artificial boundary separation", lambda c: c["true_boundary_frontier"]["true_parent_boundary_kept_distinct_from"].pop())
    add("edge-39 critical overreach", lambda c: c["fixed_skeleton_accounting"]["exact_attached_wall_anchor"].__setitem__("barrier_critical_sample", True))
    add("global wall component count", lambda c: c["fixed_skeleton_accounting"].__setitem__("global_wall_component_count", 1))
    add("attachment completeness", lambda c: c["fixed_skeleton_accounting"].__setitem__("attachment_classification_complete", True))
    add("null endpoint", lambda c: c.__setitem__("endpoint", "COMPLETE_FACTORED_BARRIER_COMPONENT_TO_SKELETON_ATTACHMENT_CERTIFICATE"))
    add("ledger scope", lambda c: c.__setitem__("theorem_ledger", "3/9"))

    rejected = []
    for marker, candidate in mutations:
        try:
            validate_frontier(candidate, replay)
        except Reject as error:
            require(marker in str(error), f"hostile mutation wrong rejection: {marker}: {error}")
            rejected.append(marker)
        else:
            raise Reject(f"hostile mutation accepted: {marker}")
    require(len(rejected) == len(mutations) == 25, "hostile mutation census")
    return rejected


def main() -> None:
    require(git("rev-parse", f"{REVIEWED_REVISION}^{{tree}}") == REVIEWED_TREE, "reviewed tree")
    require(git("rev-parse", f"{OPENING_REVISION}^{{tree}}") == OPENING_TREE, "opening tree")
    require(git("rev-parse", f"{BASE_REVISION}^{{tree}}") == BASE_TREE, "base tree")
    stored_manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    validate_manifest(stored_manifest)
    artifacts = {
        "ops/team/d9-factor19069-factored-barrier-constructor/FACTORED_BARRIER_FRONTIER.json": FRONTIER,
        "ops/team/d9-factor19069-factored-barrier-constructor/SOURCE_MANIFEST.json": CONSTRUCTOR_MANIFEST,
        "ops/team/d9-factor19069-factored-barrier-constructor/RESULT.json": CONSTRUCTOR_RESULT,
    }
    for relative, path in artifacts.items():
        frozen = git("show", f"{REVIEWED_REVISION}:{relative}", binary=True)
        require(path.read_bytes() == frozen, f"worktree drift {relative}")
        require(digest_bytes(frozen) == stored_manifest["reviewed_artifact_sha256"][relative], f"frozen artifact pin {relative}")

    constructor_manifest = json.loads(CONSTRUCTOR_MANIFEST.read_text(encoding="utf-8"))
    frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
    result = json.loads(CONSTRUCTOR_RESULT.read_text(encoding="utf-8"))
    require(constructor_manifest["source_sha256"] == {
        key: value for key, value in stored_manifest["source_sha256"].items()
        if key != "ops/research-team/PROTOCOL.md"
    }, "constructor/falsifier source pins")
    replay = source_replay()
    validate_frontier(frontier, replay)
    validate_result(result, frontier, constructor_manifest)
    rejected = hostile_mutations(frontier, replay)
    print("PASS frozen constructor revision/tree and 24 immutable source/artifact pins")
    print("PASS independent 70-factor circuit, 630 dB summands, and 36 dB-wedge-df provenance checks")
    print("PASS all 3375 supports: 3364 excluded, 10 proper candidates retained")
    print("PASS [15,7,15] exact path; [1,1,1] linear path rejected first at factor 2578")
    print("PASS skeleton 2800 parent tags; only edge 39 has one open wall root, local only")
    print(f"PASS hostile_mutations={len(rejected)}/25 rejected")
    print("CLASSIFICATION EXACT_SCOPE_REJECTION_CONFIRMS_FACTORED_BARRIER_NULL ledger=2/9")


if __name__ == "__main__":
    main()
