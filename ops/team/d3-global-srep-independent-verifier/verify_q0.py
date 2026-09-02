#!/usr/bin/env python3
"""Independent, standard-library-only verifier for the frozen SREP Q0 evidence."""

from __future__ import annotations

import copy
import hashlib
import itertools
import json
import sys
from fractions import Fraction
from pathlib import Path


FROZEN_COMMIT = "e18efbdea3ef00616f4a6cb83967f6bb267b1a5d"
ROOT = Path(__file__).resolve().parents[3]
INPUTS = {
    "producer_result": (
        "ops/team/d3-global-srep-formula-compiler/RESULT.json",
        "39ac5d04d9e043d13360d7bec31beb2144f5fa73aa6e590e86b5efadd2f7c213",
    ),
    "producer_formulas": (
        "ops/team/d3-global-srep-formula-compiler/FORMULAS.json",
        "0bddec6e60fbbdfbb5c1a3d16b8189d0447ec589033a4d5150cbb8cf8606b6ce",
    ),
    "producer_trace": (
        "ops/team/d3-global-srep-formula-compiler/TRACE.json",
        "b88e1baa9746b27762d6e3a572885d5e5135216e0299f5a3eb988ee3e85a69ba",
    ),
    "falsifier_result": (
        "ops/team/d3-global-srep-falsifier/RESULT.json",
        "c7e359b8290ad599bd8847bb7f6e5d75b0991e58d14aee8a9576507122eb9fd3",
    ),
    "falsifier_fixtures": (
        "ops/team/d3-global-srep-falsifier/FIXTURES.json",
        "75340c2c144680546f8db38612984c64b2333de683c8a5336086ed152d8e9e3c",
    ),
}


class Reject(Exception):
    pass


def require(condition: bool, code: str) -> None:
    if not condition:
        raise Reject(code)


def read_inputs() -> tuple[dict, dict]:
    payloads, hashes = {}, {}
    for name, (relative, expected) in INPUTS.items():
        raw = (ROOT / relative).read_bytes()
        actual = hashlib.sha256(raw).hexdigest()
        require(actual == expected, f"HASH_DRIFT:{name}")
        try:
            payloads[name] = json.loads(raw)
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise Reject(f"INVALID_JSON:{name}:{exc}") from exc
        hashes[name] = {"path": relative, "bytes": len(raw), "sha256": actual}
    return payloads, hashes


def frac(value) -> Fraction:
    if isinstance(value, int):
        return Fraction(value)
    return Fraction(str(value))


def eval_canonical_poly(poly: dict, point: tuple[Fraction, ...]) -> Fraction:
    require(poly.get("type") == "integer_polynomial", "BAD_CANONICAL_POLY_TYPE")
    total = Fraction(0)
    for term in poly.get("terms", []):
        exponents = term.get("exponents")
        require(isinstance(exponents, list) and len(exponents) == len(point), "BAD_EXPONENT_VECTOR")
        coefficient = term.get("coefficient")
        require(isinstance(coefficient, int), "NONINTEGER_COEFFICIENT")
        value = Fraction(coefficient)
        for coordinate, exponent in zip(point, exponents):
            require(isinstance(exponent, int) and exponent >= 0, "BAD_EXPONENT")
            value *= coordinate ** exponent
        total += value
    return total


def eval_inline(node: dict, point: tuple[Fraction, ...]) -> bool:
    op = node.get("op")
    if op in {"and", "or"}:
        values = [eval_inline(child, point) for child in node.get("args", [])]
        require(bool(values), "EMPTY_BOOLEAN_NODE")
        return all(values) if op == "and" else any(values)
    require(op in {"eq", "ge", "gt", "le", "lt", "ne"}, "UNKNOWN_INLINE_OP")
    value = eval_canonical_poly(node.get("poly", {}), point)
    return {"eq": value == 0, "ge": value >= 0, "gt": value > 0,
            "le": value <= 0, "lt": value < 0, "ne": value != 0}[op]


def eval_fixture_formula(section: dict, formula_name: str, point: tuple[Fraction, ...]) -> bool:
    atoms = section.get("atom_table", {})
    formulas = section.get("formula_ast", {})

    def walk(node: dict, stack: tuple[str, ...] = ()) -> bool:
        if "atom" in node:
            atom = atoms.get(node["atom"])
            require(atom is not None, "UNKNOWN_FIXTURE_ATOM")
            raw_poly = atom.get("polynomial")
            require(isinstance(raw_poly, list) and raw_poly, "BAD_FIXTURE_POLY")
            value = Fraction(0)
            for term in raw_poly:
                require(isinstance(term, list) and len(term) == len(point) + 1, "BAD_FIXTURE_TERM")
                coefficient, *exponents = term
                require(isinstance(coefficient, int), "BAD_FIXTURE_COEFFICIENT")
                monomial = Fraction(coefficient)
                for coordinate, exponent in zip(point, exponents):
                    require(isinstance(exponent, int) and exponent >= 0, "BAD_FIXTURE_EXPONENT")
                    monomial *= coordinate ** exponent
                value += monomial
            relation = atom.get("relation")
            require(relation in {"eq", "ge", "gt", "le", "lt", "ne"}, "BAD_FIXTURE_RELATION")
            return {"eq": value == 0, "ge": value >= 0, "gt": value > 0,
                    "le": value <= 0, "lt": value < 0, "ne": value != 0}[relation]
        if "formula" in node:
            name = node["formula"]
            require(name not in stack and name in formulas, "BAD_FIXTURE_FORMULA_REF")
            return walk(formulas[name], stack + (name,))
        op = node.get("op")
        require(op in {"and", "or"}, "BAD_FIXTURE_BOOLEAN_OP")
        values = [walk(child, stack) for child in node.get("args", [])]
        require(bool(values), "EMPTY_FIXTURE_BOOLEAN_NODE")
        return all(values) if op == "and" else any(values)

    require(formula_name in formulas, "MISSING_FIXTURE_FORMULA")
    return walk(formulas[formula_name], (formula_name,))


def rank_q(matrix: list[list[int]]) -> int:
    if not matrix:
        return 0
    width = len(matrix[0])
    require(all(len(row) == width for row in matrix), "RAGGED_MATRIX")
    rows = [[Fraction(value) for value in row] for row in matrix]
    rank = 0
    for column in range(width):
        pivot = next((r for r in range(rank, len(rows)) if rows[r][column]), None)
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        scale = rows[rank][column]
        rows[rank] = [value / scale for value in rows[rank]]
        for r in range(len(rows)):
            if r != rank and rows[r][column]:
                factor = rows[r][column]
                rows[r] = [a - factor * b for a, b in zip(rows[r], rows[rank])]
        rank += 1
        if rank == len(rows):
            break
    return rank


def matmul(a: list[list[int]], b: list[list[int]]) -> list[list[int]]:
    if not a:
        return []
    inner = len(a[0])
    require(all(len(row) == inner for row in a), "RAGGED_LEFT_MATRIX")
    require(len(b) == inner, "MATRIX_SHAPE_MISMATCH")
    width = len(b[0]) if b else 0
    require(all(len(row) == width for row in b), "RAGGED_RIGHT_MATRIX")
    return [[sum(a[i][k] * b[k][j] for k in range(inner))
             for j in range(width)] for i in range(len(a))]


def down_closure(maximal: list[list[int]]) -> set[tuple[int, ...]]:
    faces: set[tuple[int, ...]] = set()
    for raw in maximal:
        simplex = tuple(raw)
        require(simplex == tuple(sorted(set(simplex))) and simplex, "BAD_MAXIMAL_SIMPLEX")
        for size in range(1, len(simplex) + 1):
            faces.update(itertools.combinations(simplex, size))
    return faces


def relative_chain(faces: set[tuple[int, ...]], relative: set[tuple[int, ...]]) -> dict:
    require(relative <= faces, "RELATIVE_NOT_SUBCOMPLEX")
    require(down_closure([list(face) for face in relative]) == relative, "RELATIVE_NOT_DOWN_CLOSED")
    bases = {dimension: sorted(face for face in faces - relative if len(face) == dimension + 1)
             for dimension in range(3)}
    indices = {dimension: {face: i for i, face in enumerate(bases[dimension])}
               for dimension in range(3)}

    def boundary(dimension: int) -> list[list[int]]:
        rows = [[0 for _ in bases[dimension]] for _ in bases[dimension - 1]]
        for column, face in enumerate(bases[dimension]):
            for removed in range(len(face)):
                facet = face[:removed] + face[removed + 1:]
                if facet in indices[dimension - 1]:
                    rows[indices[dimension - 1][facet]][column] += -1 if removed % 2 else 1
        return rows

    d1, d2 = boundary(1), boundary(2)
    require(all(value == 0 for row in matmul(d1, d2) for value in row), "D_SQUARED_NONZERO")
    r1, r2 = rank_q(d1), rank_q(d2)
    return {
        "dim_c0": len(bases[0]), "dim_c1": len(bases[1]), "dim_c2": len(bases[2]),
        "rank_d1": r1, "rank_d2": r2,
        "h1_q": len(bases[1]) - r1 - r2,
        "d_squared_zero": True,
    }


def named_faces(raw_faces: list[list[str]]) -> set[tuple[int, ...]]:
    result = set()
    for face in raw_faces:
        require(all(isinstance(v, str) and v.startswith("v") and v[1:].isdigit() for v in face),
                "BAD_NAMED_FACE")
        result.add(tuple(int(v[1:]) for v in face))
    return result


def verify_producer_m3(formulas: dict, trace: dict) -> dict:
    m3 = formulas.get("M3", {})
    require(m3.get("variables") == ["x", "y"], "PRODUCER_M3_VARIABLE_DRIFT")
    expected_barycentric = [
        {(0, 0): 1, (1, 0): -1, (0, 1): -1},
        {(1, 0): 1},
        {(0, 1): 1},
    ]
    actual_barycentric = []
    for poly in m3.get("simplex_barycentric_polynomials", []):
        actual_barycentric.append({tuple(t["exponents"]): t["coefficient"] for t in poly.get("terms", [])})
    require(actual_barycentric == expected_barycentric, "PRODUCER_M3_BARYCENTRIC_DRIFT")
    all_faces = [face for size in range(1, 4) for face in itertools.combinations(range(3), size)]
    samples = {
        face: (sum(Fraction(1, len(face)) if vertex == 1 else 0 for vertex in face),
               sum(Fraction(1, len(face)) if vertex == 2 else 0 for vertex in face))
        for face in all_faces
    }
    expected = {
        "M3_UNFILLED": (set(all_faces) - {(0, 1, 2)}, {(0,)},
                        {"dim_c0": 2, "dim_c1": 3, "dim_c2": 0, "rank_d1": 2, "rank_d2": 0, "h1_q": 1}),
        "M3_FILLED": (set(all_faces), {(0,)},
                      {"dim_c0": 2, "dim_c1": 3, "dim_c2": 1, "rank_d1": 2, "rank_d2": 1, "h1_q": 0}),
    }
    output = {}
    for model, (expected_space, expected_relative, expected_stats) in expected.items():
        pair = m3.get("pairs", {}).get(model, {})
        space = {face for face in all_faces if eval_inline(pair.get("space", {}), samples[face])}
        relative = {face for face in all_faces if eval_inline(pair.get("relative", {}), samples[face])}
        require(space == expected_space, f"PRODUCER_{model}_SPACE_DRIFT")
        require(relative == expected_relative, f"PRODUCER_{model}_RELATIVE_DRIFT")
        stats = relative_chain(space, relative)
        require(all(stats[key] == value for key, value in expected_stats.items()),
                f"PRODUCER_{model}_HOMOLOGY_DRIFT")
        compiled = trace.get("M3", {}).get("compiled", {}).get(model, {})
        require(named_faces(compiled.get("faces", [])) == space, f"PRODUCER_{model}_TRACE_FACE_DRIFT")
        require(named_faces(compiled.get("relative_faces", [])) == relative,
                f"PRODUCER_{model}_TRACE_RELATIVE_DRIFT")
        reported = trace.get("M3", {}).get("relative_homology_over_q", {}).get(model, {})
        require(all(reported.get(key) == stats[key] for key in ("dim_c1", "rank_d1", "rank_d2", "h1_q")),
                f"PRODUCER_{model}_REPORTED_HOMOLOGY_DRIFT")
        output[model] = stats
    require(trace.get("M3", {}).get("same_one_skeleton") is True,
            "PRODUCER_M3_ONE_SKELETON_CLAIM_DRIFT")
    return output


def verify_falsifier_m3(fixtures: dict, result: dict) -> dict:
    m3 = fixtures.get("m3", {})
    require(m3.get("variables") == ["x", "y", "z"], "FALSIFIER_M3_VARIABLE_DRIFT")
    require(m3.get("source_mode") == "POLYNOMIAL_FORMULA_DERIVED", "FALSIFIER_M3_SOURCE_MODE_DRIFT")
    infinity = m3.get("true_infinity", {})
    require(infinity.get("kind") == "true_parent_infinity" and infinity.get("vertex") == 3,
            "FALSIFIER_M3_INFINITY_DRIFT")
    relative = {(3,)}
    expected = {
        "unfilled": ({(0, 1, 2), (0, 1, 3), (2, 3)},
                     {"dim_c0": 3, "dim_c1": 6, "dim_c2": 2, "rank_d1": 3, "rank_d2": 2, "h1_q": 1}),
        "filled": ({(0, 1, 2), (0, 1, 3), (0, 2, 3)},
                   {"dim_c0": 3, "dim_c1": 6, "dim_c2": 3, "rank_d1": 3, "rank_d2": 3, "h1_q": 0}),
    }
    output, skeletons = {}, []
    for name, (expected_maximal, expected_stats) in expected.items():
        model = m3.get("models", {}).get(name, {})
        maximal = {tuple(face) for face in model.get("maximal_simplices", [])}
        require(maximal == expected_maximal, f"FALSIFIER_M3_{name.upper()}_MAXIMAL_DRIFT")
        faces = down_closure(model.get("maximal_simplices", []))
        skeletons.append({face for face in faces if len(face) <= 2})
        stats = relative_chain(faces, relative)
        require(all(stats[key] == value for key, value in expected_stats.items()),
                f"FALSIFIER_M3_{name.upper()}_HOMOLOGY_DRIFT")
        require(all(model.get("reported_relative_chain", {}).get(key) == stats[key]
                    for key in ("dim_c0", "dim_c1", "dim_c2", "rank_d1", "rank_d2", "h1_q")),
                f"FALSIFIER_M3_{name.upper()}_REPORTED_DRIFT")
        expected_trace = {f"f_{''.join(map(str, face))}": face for face in maximal if len(face) == 3}
        actual_trace = {cell.get("id"): tuple(cell.get("vertices", []))
                        for cell in model.get("two_cell_trace", [])}
        require(actual_trace == expected_trace, f"FALSIFIER_M3_{name.upper()}_TRACE_DRIFT")
        for cell in model.get("two_cell_trace", []):
            face = tuple(cell["vertices"])
            canonical = [(1 if removed % 2 == 0 else -1,
                          f"e_{''.join(map(str, face[:removed] + face[removed + 1:]))}")
                         for removed in range(3)]
            require([tuple(item) for item in cell.get("boundary", [])] == canonical,
                    f"FALSIFIER_M3_{name.upper()}_INCIDENCE_DRIFT")
        reported = result.get("baseline", {}).get("m3", {}).get(name, {})
        require(all(reported.get(key) == stats[key] for key in expected_stats),
                f"FALSIFIER_M3_{name.upper()}_RESULT_DRIFT")
        output[name] = stats
    require(skeletons[0] == skeletons[1] and len([f for f in skeletons[0] if len(f) == 2]) == 6,
            "FALSIFIER_M3_ONE_SKELETON_DRIFT")
    require(result.get("baseline", {}).get("m3", {}).get("same_one_skeleton") is True,
            "FALSIFIER_M3_ONE_SKELETON_REPORT_DRIFT")
    return output


def verify_m2(formulas: dict, trace: dict, fixtures: dict, result: dict) -> dict:
    producer = formulas.get("M2", {})
    require(producer.get("variables") == ["s", "u"], "PRODUCER_M2_VARIABLE_DRIFT")
    p_limit = (Fraction(0), Fraction(3, 2))
    for n in range(1, 65):
        point = (Fraction(1, n), Fraction(3, 2))
        require(eval_inline(producer.get("selected_strip", {}), point), "PRODUCER_M2_WITNESS_NOT_SELECTED")
        require(eval_inline(producer.get("selected_plus_terminal", {}), point), "PRODUCER_M2_WITNESS_NOT_IN_UNION")
    require(not eval_inline(producer.get("selected_plus_terminal", {}), p_limit),
            "PRODUCER_M2_LIMIT_NOT_EXCLUDED")
    require(trace.get("M2", {}).get("excluded_limit") == ["0", "3/2"], "PRODUCER_M2_TRACE_LIMIT_DRIFT")
    require(trace.get("M2", {}).get("complex_emitted") is False, "PRODUCER_M2_COMPLEX_SHOULD_NOT_EXIST")

    m2 = fixtures.get("m2", {})
    require(m2.get("variables") == ["s", "u"], "FALSIFIER_M2_VARIABLE_DRIFT")
    require(m2.get("nonclosure_witness", {}).get("family") == ["1/n", "3/2"],
            "FALSIFIER_M2_FAMILY_DRIFT")
    require(m2.get("nonclosure_witness", {}).get("limit") == ["0", "3/2"],
            "FALSIFIER_M2_LIMIT_DRIFT")
    for n in range(1, 65):
        point = (Fraction(1, n), Fraction(3, 2))
        require(eval_fixture_formula(m2, "selected_strip", point), "FALSIFIER_M2_WITNESS_NOT_SELECTED")
        require(eval_fixture_formula(m2, "pointwise_union", point), "FALSIFIER_M2_WITNESS_NOT_IN_UNION")
    require(not eval_fixture_formula(m2, "pointwise_union", p_limit), "FALSIFIER_M2_LIMIT_NOT_EXCLUDED")
    require(not eval_fixture_formula(m2, "true_parent_infinity", p_limit), "FALSIFIER_M2_FALSE_INFINITY")
    require(eval_fixture_formula(m2, "artificial_jump_frontier", p_limit),
            "FALSIFIER_M2_ARTIFICIAL_FRONTIER_MISSING")
    # Exact Archimedean witness recipe: n=floor(1/epsilon)+1 implies 0<1/n<epsilon.
    for epsilon in (Fraction(1), Fraction(2, 3), Fraction(1, 10), Fraction(7, 113)):
        n = (epsilon.denominator // epsilon.numerator) + 1
        require(Fraction(0) < Fraction(1, n) < epsilon, "M2_EXACT_CONVERGENCE_RECIPE_FAILED")
    reported = m2.get("reported", {})
    require(reported.get("pointwise_union_closed") is False, "FALSIFIER_M2_CLOSEDNESS_REPORT_DRIFT")
    require(reported.get("projection_proper") is False, "FALSIFIER_M2_PROPERNESS_REPORT_DRIFT")
    require(reported.get("artificial_jump_frontier_is_true_infinity") is False,
            "FALSIFIER_M2_INFINITY_REPORT_DRIFT")
    require(result.get("baseline", {}).get("m2", {}).get("pointwise_union_closed") is False,
            "FALSIFIER_RESULT_M2_CLOSEDNESS_DRIFT")
    require(result.get("baseline", {}).get("m2", {}).get("excluded_limit") == "(0,3/2)",
            "FALSIFIER_RESULT_M2_LIMIT_DRIFT")
    return {
        "family": "(1/n,3/2), n>=1", "limit": "(0,3/2)",
        "all_terms_in_pointwise_union": True, "limit_excluded": True,
        "limit_not_true_parent_infinity": True, "exact_convergence_recipe_checked": True,
    }


def verify_payloads(payloads: dict) -> dict:
    pr = payloads["producer_result"]
    require(pr.get("q0_pass") is False, "PRODUCER_Q0_MUST_BE_FALSE")
    require(pr.get("producer_self_acceptance") is False, "PRODUCER_SELF_ACCEPTANCE_MUST_BE_FALSE")
    require(pr.get("q1_eligible") is False, "PRODUCER_Q1_MUST_BE_FALSE")
    require(pr.get("cloud_used") is False, "PRODUCER_CLOUD_MUST_BE_FALSE")
    require(pr.get("theorem_credit") == "NONE", "PRODUCER_THEOREM_CREDIT_MUST_BE_NONE")
    parameters = pr.get("partial_basu_karisani_parameters", {})
    for key in ("N", "s", "d"):
        require(key in parameters and parameters[key] is None, f"PRODUCER_{key.upper()}_MUST_BE_NULL")
    require(pr.get("q0_classification") == "NULL_NO_EXECUTABLE_REPLACEMENT_BACKEND",
            "PRODUCER_Q0_CLASSIFICATION_DRIFT")
    fr = payloads["falsifier_result"]
    require(fr.get("status") == "PASS", "FALSIFIER_STATUS_DRIFT")
    require(fr.get("q0_theorem_credit") == "NONE", "FALSIFIER_THEOREM_CREDIT_DRIFT")
    require(fr.get("baseline", {}).get("m3", {}).get("relative_h1_q") == {"unfilled": 1, "filled": 0},
            "FALSIFIER_M3_SUMMARY_DRIFT")
    producer_m3 = verify_producer_m3(payloads["producer_formulas"], payloads["producer_trace"])
    falsifier_m3 = verify_falsifier_m3(payloads["falsifier_fixtures"], fr)
    m2 = verify_m2(payloads["producer_formulas"], payloads["producer_trace"],
                   payloads["falsifier_fixtures"], fr)
    return {"producer_m3": producer_m3, "falsifier_m3": falsifier_m3, "m2": m2}


def mutation_suite(payloads: dict) -> list[dict]:
    mutations = []

    def add(name, mutate):
        candidate = copy.deepcopy(payloads)
        mutate(candidate)
        try:
            verify_payloads(candidate)
        except Reject as exc:
            mutations.append({"id": name, "rejected": True, "reason": str(exc)})
        else:
            mutations.append({"id": name, "rejected": False, "reason": "ACCEPTED"})

    add("producer_q0_true", lambda p: p["producer_result"].__setitem__("q0_pass", True))
    add("producer_self_acceptance_true", lambda p: p["producer_result"].__setitem__("producer_self_acceptance", True))
    add("producer_q1_true", lambda p: p["producer_result"].__setitem__("q1_eligible", True))
    add("producer_cloud_true", lambda p: p["producer_result"].__setitem__("cloud_used", True))
    add("producer_theorem_credit", lambda p: p["producer_result"].__setitem__("theorem_credit", "CLAIMED"))
    add("producer_N_fabricated", lambda p: p["producer_result"]["partial_basu_karisani_parameters"].__setitem__("N", 1))
    add("producer_s_fabricated", lambda p: p["producer_result"]["partial_basu_karisani_parameters"].__setitem__("s", 1))
    add("producer_d_fabricated", lambda p: p["producer_result"]["partial_basu_karisani_parameters"].__setitem__("d", 1))
    add("producer_unfilled_conflated", lambda p: p["producer_formulas"]["M3"]["pairs"]["M3_UNFILLED"].__setitem__(
        "space", copy.deepcopy(p["producer_formulas"]["M3"]["pairs"]["M3_FILLED"]["space"])))
    add("producer_relative_vertex_changed", lambda p: p["producer_formulas"]["M3"]["pairs"]["M3_FILLED"].__setitem__(
        "relative", copy.deepcopy(p["producer_formulas"]["M3"]["pairs"]["M3_FILLED"]["space"])))
    add("producer_trace_face_omitted", lambda p: p["producer_trace"]["M3"]["compiled"]["M3_FILLED"]["faces"].pop())
    add("producer_rank_falsified", lambda p: p["producer_trace"]["M3"]["relative_homology_over_q"]["M3_UNFILLED"].__setitem__("rank_d2", 1))
    add("producer_m2_limit_claim_changed", lambda p: p["producer_trace"]["M2"].__setitem__("excluded_limit", ["0", "1"]))
    add("producer_m2_union_replaced", lambda p: p["producer_formulas"]["M2"].__setitem__(
        "selected_plus_terminal", copy.deepcopy(p["producer_formulas"]["M2"]["pointwise_terminal"])))
    add("falsifier_status_failed", lambda p: p["falsifier_result"].__setitem__("status", "FAIL"))
    add("falsifier_unfilled_face_added", lambda p: p["falsifier_fixtures"]["m3"]["models"]["unfilled"]["maximal_simplices"].append([0, 2, 3]))
    add("falsifier_filled_face_removed", lambda p: p["falsifier_fixtures"]["m3"]["models"]["filled"]["maximal_simplices"].pop())
    add("falsifier_incidence_flipped", lambda p: p["falsifier_fixtures"]["m3"]["models"]["filled"]["two_cell_trace"][0]["boundary"][0].__setitem__(0, -1))
    add("falsifier_h1_falsified", lambda p: p["falsifier_result"]["baseline"]["m3"]["unfilled"].__setitem__("h1_q", 0))
    add("falsifier_infinity_relabelled", lambda p: p["falsifier_fixtures"]["m3"]["true_infinity"].__setitem__("vertex", 0))
    add("falsifier_m2_limit_changed", lambda p: p["falsifier_fixtures"]["m2"]["nonclosure_witness"].__setitem__("limit", ["0", "1"]))
    add("falsifier_m2_false_infinity", lambda p: p["falsifier_fixtures"]["m2"]["reported"].__setitem__("artificial_jump_frontier_is_true_infinity", True))
    require(len(mutations) >= 16 and all(item["rejected"] for item in mutations), "HOSTILE_MUTATION_ESCAPED")
    return mutations


def main() -> int:
    try:
        payloads, hashes = read_inputs()
        recomputation = verify_payloads(payloads)
        mutations = mutation_suite(payloads)
        result = {
            "format": "d3-global-srep-independent-q0-verification-v1",
            "status": "PASS",
            "verdict": "Q0_NULL_INDEPENDENTLY_CONFIRMED",
            "frozen_evidence_commit": FROZEN_COMMIT,
            "inputs": hashes,
            "independent_recomputation": recomputation,
            "producer_gate_assertions": {
                "q0_pass": False, "q1_eligible": False, "cloud_used": False,
                "theorem_credit": "NONE", "N": None, "s": None, "d": None,
            },
            "hostile_mutations": {
                "rejected": len(mutations), "total": len(mutations), "results": mutations,
            },
            "scope": [
                "Independent machine verification, not human review.",
                "Confirms a sound Q0 null/stop classification and its canaries only.",
                "Does not implement Basu--Karisani replacement or earn theorem/ledger credit.",
            ],
        }
    except Reject as exc:
        result = {
            "format": "d3-global-srep-independent-q0-verification-v1",
            "status": "FAIL", "verdict": "REJECTED", "reason": str(exc),
            "frozen_evidence_commit": FROZEN_COMMIT,
        }
        print(json.dumps(result, indent=2, sort_keys=True))
        return 1
    if "--json" in sys.argv:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS input SHA-256 pins: 5/5")
        print("PASS producer Q0/Q1/cloud/theorem and N/s/d null assertions")
        print("PASS producer M3 filled/unfilled rational ranks and d^2=0")
        print("PASS falsifier M3 filled/unfilled rational ranks and d^2=0")
        print("PASS M2 exact family (1/n,3/2) converges to excluded non-infinity limit")
        print(f"PASS hostile mutations rejected: {len(mutations)}/{len(mutations)}")
        print("VERDICT Q0_NULL_INDEPENDENTLY_CONFIRMED; THEOREM_CREDIT=NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
