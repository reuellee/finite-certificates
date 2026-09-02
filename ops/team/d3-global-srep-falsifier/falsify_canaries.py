#!/usr/bin/env python3
"""Independent exact checker and hostile mutation suite for Q0 canaries.

This lane owns the canary formulas.  It neither imports nor certifies the
formula/replacement producer.  All chain arithmetic is over Q and all sample
coordinates used for formula checks are Fractions.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import itertools
import json
import subprocess
import sys
from collections import deque
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
DEFAULT_FIXTURE = HERE / "FIXTURES.json"
OPENING = "c50da6c99d465c65b3e54427418d9efe6a3f037e"


class Rejected(ValueError):
    def __init__(self, code: str, detail: str = "") -> None:
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code
        self.detail = detail


def require(condition: bool, code: str, detail: str = "") -> None:
    if not condition:
        raise Rejected(code, detail)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def atom(relation: str, polynomial: list[list[int]]) -> dict:
    return {"relation": relation, "polynomial": polynomial}


def aref(name: str) -> dict:
    return {"atom": name}


def fref(name: str) -> dict:
    return {"formula": name}


def conjunction(*args: dict) -> dict:
    return {"op": "and", "args": list(args)}


def disjunction(*args: dict) -> dict:
    return {"op": "or", "args": list(args)}


def simplex_id(vertices: tuple[int, ...]) -> str:
    prefix = {1: "v", 2: "e", 3: "f"}[len(vertices)]
    return prefix + "_" + "".join(str(value) for value in vertices)


def expected_m3_atoms() -> dict:
    lambdas = {
        0: [[1, 0, 0, 0], [-1, 1, 0, 0], [-1, 0, 1, 0], [-1, 0, 0, 1]],
        1: [[1, 1, 0, 0]],
        2: [[1, 0, 1, 0]],
        3: [[1, 0, 0, 1]],
    }
    result = {}
    for index in range(4):
        result[f"lambda_{index}_ge"] = atom("ge", lambdas[index])
        result[f"lambda_{index}_eq"] = atom("eq", lambdas[index])
    return result


def face_formula(vertices: tuple[int, ...]) -> dict:
    args = [aref(f"lambda_{index}_ge") for index in range(4)]
    args.extend(
        aref(f"lambda_{index}_eq")
        for index in range(4)
        if index not in vertices
    )
    return conjunction(*args)


def expected_m3_face_formulas() -> dict:
    faces = (
        tuple((index,)) for index in range(4)
    )
    edges = itertools.combinations(range(4), 2)
    triangles = ((0, 1, 2), (0, 1, 3), (0, 2, 3))
    return {
        simplex_id(face): face_formula(face)
        for face in itertools.chain(faces, edges, triangles)
    }


def canonical_boundary(vertices: tuple[int, ...]) -> list[list[object]]:
    if len(vertices) == 1:
        return []
    if len(vertices) == 2:
        return [[-1, simplex_id((vertices[0],))], [1, simplex_id((vertices[1],))]]
    return [
        [(-1) ** index, simplex_id(vertices[:index] + vertices[index + 1 :])]
        for index in range(len(vertices))
    ]


def expected_trace_cell(vertices: tuple[int, ...]) -> dict:
    name = simplex_id(vertices)
    return {
        "id": name,
        "dimension": len(vertices) - 1,
        "vertices": list(vertices),
        "formula_id": name,
        "boundary": canonical_boundary(vertices),
    }


def rank_q(matrix: list[list[int]]) -> int:
    if not matrix:
        return 0
    width = len(matrix[0])
    require(all(len(row) == width for row in matrix), "RAGGED_MATRIX")
    work = [[Fraction(value) for value in row] for row in matrix]
    pivot_row = 0
    for column in range(width):
        pivot = next(
            (row for row in range(pivot_row, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        divisor = work[pivot_row][column]
        work[pivot_row] = [value / divisor for value in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row or work[row][column] == 0:
                continue
            multiple = work[row][column]
            work[row] = [
                value - multiple * pivot_value
                for value, pivot_value in zip(work[row], work[pivot_row], strict=True)
            ]
        pivot_row += 1
    return pivot_row


def multiply(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    if not left:
        return []
    require(len(left[0]) == len(right), "MATRIX_DIMENSION_MISMATCH")
    width = len(right[0]) if right else 0
    return [
        [sum(left[i][k] * right[k][j] for k in range(len(right))) for j in range(width)]
        for i in range(len(left))
    ]


def eval_polynomial(polynomial: list[list[int]], point: tuple[Fraction, ...]) -> Fraction:
    total = Fraction(0)
    for term in polynomial:
        require(len(term) == len(point) + 1, "POLYNOMIAL_ARITY")
        value = Fraction(term[0])
        for coordinate, power in zip(point, term[1:], strict=True):
            require(isinstance(power, int) and power >= 0, "POLYNOMIAL_POWER")
            value *= coordinate ** power
        total += value
    return total


def eval_formula(
    expression: dict,
    atoms: dict,
    formulas: dict,
    point: tuple[Fraction, ...],
    stack: tuple[str, ...] = (),
) -> bool:
    if set(expression) == {"atom"}:
        name = expression["atom"]
        require(name in atoms, "UNKNOWN_ATOM", str(name))
        entry = atoms[name]
        value = eval_polynomial(entry["polynomial"], point)
        return {
            "eq": value == 0,
            "ge": value >= 0,
            "gt": value > 0,
            "ne": value != 0,
        }[entry["relation"]]
    if set(expression) == {"formula"}:
        name = expression["formula"]
        require(name in formulas, "UNKNOWN_FORMULA", str(name))
        require(name not in stack, "FORMULA_REFERENCE_CYCLE", str(name))
        return eval_formula(formulas[name], atoms, formulas, point, stack + (name,))
    require(set(expression) == {"op", "args"}, "MALFORMED_FORMULA_AST")
    values = [eval_formula(item, atoms, formulas, point, stack) for item in expression["args"]]
    if expression["op"] == "and":
        return all(values)
    if expression["op"] == "or":
        return any(values)
    raise Rejected("UNKNOWN_BOOLEAN_OPERATOR", str(expression["op"]))


def boundary_matrix(
    lower: list[dict], upper: list[dict], relative_ids: set[str]
) -> list[list[int]]:
    rows = [cell for cell in lower if cell["id"] not in relative_ids]
    row_index = {cell["id"]: index for index, cell in enumerate(rows)}
    matrix = [[0 for _ in upper] for _ in rows]
    for column, cell in enumerate(upper):
        for coefficient, target in cell["boundary"]:
            if target in row_index:
                matrix[row_index[target]][column] += coefficient
    return matrix


def faces_from_maximal(maximal: list[list[int]]) -> set[tuple[int, ...]]:
    result: set[tuple[int, ...]] = set()
    for raw in maximal:
        vertices = tuple(raw)
        require(tuple(sorted(vertices)) == vertices, "M3_UNSORTED_SIMPLEX")
        require(len(set(vertices)) == len(vertices), "M3_DEGENERATE_SIMPLEX")
        for size in range(1, len(vertices) + 1):
            result.update(itertools.combinations(vertices, size))
    return result


def verify_m3(m3: dict) -> dict:
    require(m3.get("source_mode") == "POLYNOMIAL_FORMULA_DERIVED", "M3_NOT_FORMULA_DERIVED")
    require(m3.get("variables") == ["x", "y", "z"], "M3_VARIABLE_SCHEMA")
    require(m3.get("atom_table") == expected_m3_atoms(), "M3_ATOM_TABLE_DRIFT")
    expected_faces = expected_m3_face_formulas()
    require(m3.get("face_formula_ast") == expected_faces, "M3_FACE_FORMULA_DRIFT")

    edges = list(itertools.combinations(range(4), 2))
    expected_skeleton_formula = disjunction(*(fref(simplex_id(edge)) for edge in edges))
    require(
        m3.get("common_one_skeleton_formula") == expected_skeleton_formula,
        "M3_ONE_SKELETON_FORMULA_MISMATCH",
    )
    require(
        m3.get("true_infinity")
        == {"kind": "true_parent_infinity", "vertex": 3, "formula": fref("v_3")},
        "M3_TRUE_INFINITY_TAG",
    )
    expected_graph = {
        "vertices": [0, 1, 2, 3],
        "edges": [list(edge) for edge in edges],
        "true_infinity_vertices": [3],
        "coverage_complete": True,
        "all_vertices_reach_true_infinity": True,
    }
    require(m3.get("reported_exit_graph") == expected_graph, "M3_EXIT_GRAPH_DRIFT")

    common = m3.get("common_trace")
    require(isinstance(common, list), "M3_COMMON_TRACE_MISSING")
    common_ids = [cell.get("id") for cell in common]
    require(len(common_ids) == len(set(common_ids)), "M3_DUPLICATE_SIMPLEX_ID")
    expected_common_vertices = [tuple((index,)) for index in range(4)]
    expected_common = [expected_trace_cell(face) for face in expected_common_vertices + edges]
    common_shapes = [(cell.get("id"), cell.get("dimension"), cell.get("vertices"), cell.get("formula_id")) for cell in common]
    expected_shapes = [(cell["id"], cell["dimension"], cell["vertices"], cell["formula_id"]) for cell in expected_common]
    require(common_shapes == expected_shapes, "M3_COMMON_TRACE_FACE_OMITTED_OR_DRIFTED")

    # The standard barycentric formula binds each cell to exactly its named
    # tetrahedron vertices; this catches a detached formula/complex trace.
    vertex_points = (
        (Fraction(0), Fraction(0), Fraction(0)),
        (Fraction(1), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(1), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(1)),
    )
    for name, formula in expected_faces.items():
        named = tuple(int(char) for char in name.split("_")[1])
        actual_members = tuple(
            index
            for index, point in enumerate(vertex_points)
            if eval_formula(formula, m3["atom_table"], expected_faces, point)
        )
        require(actual_members == named, "M3_FORMULA_COMPLEX_DISCONNECT", name)

    results = {}
    expected_models = {
        "unfilled": {
            "maximal": [[0, 1, 2], [0, 1, 3], [2, 3]],
            "formula": disjunction(fref("f_012"), fref("f_013"), fref("e_23")),
            "faces": [(0, 1, 2), (0, 1, 3)],
            "h1": 1,
        },
        "filled": {
            "maximal": [[0, 1, 2], [0, 1, 3], [0, 2, 3]],
            "formula": disjunction(fref("f_012"), fref("f_013"), fref("f_023")),
            "faces": [(0, 1, 2), (0, 1, 3), (0, 2, 3)],
            "h1": 0,
        },
    }
    models = m3.get("models", {})
    require(set(models) == set(expected_models), "M3_MODEL_SET")
    for model_name in ("unfilled", "filled"):
        model = models[model_name]
        contract = expected_models[model_name]
        require(model.get("maximal_simplices") == contract["maximal"], f"M3_{model_name.upper()}_MAXIMAL_SCHEMA")
        require(model.get("formula") == contract["formula"], "M3_MODEL_FORMULA_COMPLEX_DISCONNECT", model_name)
        two_cells = model.get("two_cell_trace")
        require(isinstance(two_cells, list), "M3_TWO_CELL_TRACE_MISSING", model_name)
        all_cells = common + two_cells
        ids = [cell.get("id") for cell in all_cells]
        require(len(ids) == len(set(ids)), "M3_DUPLICATE_SIMPLEX_ID", model_name)

        expected_face_set = faces_from_maximal(contract["maximal"])
        actual_face_set = {
            tuple(cell.get("vertices", [])) for cell in all_cells
            if isinstance(cell, dict)
        }
        require(actual_face_set == expected_face_set, "M3_TRACE_FACE_OMITTED_OR_EXTRA", model_name)
        expected_two = [expected_trace_cell(face) for face in contract["faces"]]
        two_shapes = [(cell.get("id"), cell.get("dimension"), cell.get("vertices"), cell.get("formula_id")) for cell in two_cells]
        expected_two_shapes = [(cell["id"], cell["dimension"], cell["vertices"], cell["formula_id"]) for cell in expected_two]
        require(two_shapes == expected_two_shapes, "M3_TWO_CELL_TRACE_DRIFT", model_name)

        by_dimension = {
            dimension: [cell for cell in all_cells if cell.get("dimension") == dimension]
            for dimension in range(3)
        }
        relative_ids = {"v_3"}
        d1 = boundary_matrix(by_dimension[0], by_dimension[1], relative_ids)
        d2 = boundary_matrix(by_dimension[1], by_dimension[2], relative_ids)
        product = multiply(d1, d2)
        require(not any(any(value for value in row) for row in product), "M3_D_SQUARED_NONZERO", model_name)

        for actual, expected in zip(common, expected_common, strict=True):
            require(actual.get("boundary") == expected["boundary"], "M3_INCIDENCE_MISMATCH", actual["id"])
        for actual, expected in zip(two_cells, expected_two, strict=True):
            require(actual.get("boundary") == expected["boundary"], "M3_INCIDENCE_MISMATCH", actual["id"])

        dim_c0 = len(by_dimension[0]) - 1
        dim_c1 = len(by_dimension[1])
        dim_c2 = len(by_dimension[2])
        rank_d1 = rank_q(d1)
        rank_d2 = rank_q(d2)
        h1 = dim_c1 - rank_d1 - rank_d2
        reported = model.get("reported_relative_chain", {})
        expected_report = {
            "dim_c0": dim_c0,
            "dim_c1": dim_c1,
            "dim_c2": dim_c2,
            "rank_d1": rank_d1,
            "rank_d2": rank_d2,
            "h1_q": h1,
        }
        require(reported == expected_report, "M3_REPORTED_RANK_OR_HOMOLOGY", model_name)
        require(h1 == contract["h1"], "M3_H1_WRONG", model_name)
        results[model_name] = expected_report

    require(
        results["unfilled"]["h1_q"] == 1 and results["filled"]["h1_q"] == 0,
        "M3_FILLED_UNFILLED_CONFLATION",
    )

    adjacency = {vertex: set() for vertex in range(4)}
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    reached = {3}
    queue = deque([3])
    while queue:
        vertex = queue.popleft()
        for neighbor in sorted(adjacency[vertex]):
            if neighbor not in reached:
                reached.add(neighbor)
                queue.append(neighbor)
    require(reached == set(range(4)), "M3_EXIT_GRAPH_NOT_ACCEPTED")

    return {
        "status": "PASS",
        "compact_closed_formula": True,
        "same_one_skeleton": True,
        "same_accepted_exit_graph": True,
        "relative_h1_q": {name: result["h1_q"] for name, result in results.items()},
        "relative_ranks": results,
    }


def expected_m2_atoms() -> dict:
    return {
        "s_plus_one_ge": atom("ge", [[1, 0, 0], [1, 1, 0]]),
        "one_minus_s_ge": atom("ge", [[1, 0, 0], [-1, 1, 0]]),
        "u_ge": atom("ge", [[1, 0, 1]]),
        "two_minus_u_ge": atom("ge", [[2, 0, 0], [-1, 0, 1]]),
        "s_eq_zero": atom("eq", [[1, 1, 0]]),
        "s_ne_zero": atom("ne", [[1, 1, 0]]),
        "one_minus_u_gt": atom("gt", [[1, 0, 0], [-1, 0, 1]]),
        "two_minus_u_gt": atom("gt", [[2, 0, 0], [-1, 0, 1]]),
        "u_minus_one_eq": atom("eq", [[-1, 0, 0], [1, 0, 1]]),
        "two_minus_u_eq": atom("eq", [[2, 0, 0], [-1, 0, 1]]),
        "u_minus_one_gt": atom("gt", [[-1, 0, 0], [1, 0, 1]]),
    }


def expected_m2_formulas() -> dict:
    ambient = conjunction(
        aref("s_plus_one_ge"), aref("one_minus_s_ge"),
        aref("u_ge"), aref("two_minus_u_ge"),
    )
    selected = conjunction(
        fref("ambient_rectangle"),
        disjunction(
            conjunction(aref("s_eq_zero"), aref("one_minus_u_gt")),
            conjunction(aref("s_ne_zero"), aref("two_minus_u_gt")),
        ),
    )
    terminal = conjunction(
        fref("ambient_rectangle"),
        disjunction(
            conjunction(aref("s_eq_zero"), aref("u_minus_one_eq")),
            aref("two_minus_u_eq"),
        ),
    )
    return {
        "ambient_rectangle": ambient,
        "selected_strip": selected,
        "pointwise_terminal": terminal,
        "pointwise_union": disjunction(fref("selected_strip"), fref("pointwise_terminal")),
        "true_parent_infinity": conjunction(fref("ambient_rectangle"), aref("two_minus_u_eq")),
        "artificial_jump_frontier": conjunction(
            fref("ambient_rectangle"), aref("s_eq_zero"),
            aref("u_minus_one_gt"), aref("two_minus_u_gt"),
        ),
        "central_closed_fiber": conjunction(fref("ambient_rectangle"), aref("s_eq_zero")),
        "central_relative_subset": conjunction(
            fref("central_closed_fiber"),
            disjunction(aref("u_minus_one_eq"), aref("two_minus_u_eq")),
        ),
    }


def verify_m2(m2: dict) -> dict:
    require(m2.get("source_mode") == "POLYNOMIAL_FORMULA_DERIVED", "M2_NOT_FORMULA_DERIVED")
    require(m2.get("variables") == ["s", "u"], "M2_VARIABLE_SCHEMA")
    require(m2.get("atom_table") == expected_m2_atoms(), "M2_ATOM_TABLE_DRIFT")
    expected_formulas = expected_m2_formulas()
    actual_formulas = m2.get("formula_ast")
    require(isinstance(actual_formulas, dict), "M2_FORMULA_TABLE_MISSING")
    for name in expected_formulas:
        require(name in actual_formulas, "M2_FORMULA_TAG_OMITTED", name)
        require(actual_formulas[name] == expected_formulas[name], f"M2_{name.upper()}_FORMULA_MISMATCH")
    require(set(actual_formulas) == set(expected_formulas), "M2_FORMULA_TAG_SET_DRIFT")

    witness = m2.get("nonclosure_witness")
    require(
        witness == {"family": ["1/n", "3/2"], "n_domain": "POSITIVE_INTEGERS", "limit": ["0", "3/2"]},
        "M2_NONCLOSURE_WITNESS_DRIFT",
    )
    atoms = m2["atom_table"]
    for denominator in range(1, 65):
        point = (Fraction(1, denominator), Fraction(3, 2))
        require(eval_formula(actual_formulas["pointwise_union"], atoms, actual_formulas, point), "M2_APPROACH_POINT_MISSING", str(denominator))
    limit = (Fraction(0), Fraction(3, 2))
    require(eval_formula(actual_formulas["ambient_rectangle"], atoms, actual_formulas, limit), "M2_LIMIT_OUTSIDE_AMBIENT")
    require(not eval_formula(actual_formulas["pointwise_union"], atoms, actual_formulas, limit), "M2_FALSE_WEAK_CLOSURE")
    require(eval_formula(actual_formulas["artificial_jump_frontier"], atoms, actual_formulas, limit), "M2_ARTIFICIAL_FRONTIER_MISSING")
    require(not eval_formula(actual_formulas["true_parent_infinity"], atoms, actual_formulas, limit), "M2_FALSE_INFINITY")
    require(eval_formula(actual_formulas["pointwise_terminal"], atoms, actual_formulas, (Fraction(0), Fraction(1))), "M2_CENTRAL_TERMINAL_MISSING")
    require(eval_formula(actual_formulas["true_parent_infinity"], atoms, actual_formulas, (Fraction(0), Fraction(2))), "M2_TRUE_INFINITY_MISSING")

    expected_trace = {
        "vertices": [
            {"id": "u_0", "coordinate": "0", "relative": False},
            {"id": "u_1", "coordinate": "1", "relative": True},
            {"id": "u_2", "coordinate": "2", "relative": True},
        ],
        "edges": [
            {"id": "e_01", "boundary": [[-1, "u_0"], [1, "u_1"]]},
            {"id": "e_12", "boundary": [[-1, "u_1"], [1, "u_2"]]},
        ],
        "reported_h1_q": 1,
    }
    trace = m2.get("closure_relative_trace")
    require(trace == expected_trace, "M2_CLOSURE_RELATIVE_TRACE_DRIFT")
    relative = {vertex["id"] for vertex in trace["vertices"] if vertex["relative"]}
    d1 = boundary_matrix(
        [{"id": vertex["id"]} for vertex in trace["vertices"]],
        trace["edges"],
        relative,
    )
    h1 = len(trace["edges"]) - rank_q(d1)
    require(h1 == 1, "M2_CLOSURE_RELATIVE_H1_WRONG")
    expected_report = {
        "pointwise_union_closed": False,
        "projection_proper": False,
        "artificial_jump_frontier_is_true_infinity": False,
        "ambient_closure_formula": "ambient_rectangle",
        "central_closure_relative_h1_q": 1,
    }
    require(m2.get("reported") == expected_report, "M2_REPORTED_SEMANTICS_DRIFT")
    return {
        "status": "PASS",
        "pointwise_union_closed": False,
        "exact_limit_witness": ["(1/n,3/2)", "(0,3/2)"],
        "artificial_frontier_rejected_as_true_infinity": True,
        "central_closure_relative_h1_q": h1,
    }


def bounded_compositions(total: int, length: int, maximum: int):
    if length == 0:
        if total == 0:
            yield ()
        return
    for first in range(min(total, maximum) + 1):
        for tail in bounded_compositions(total - first, length - 1, maximum):
            yield (first,) + tail


def control_motion(face_dimension: int, support_size: int) -> int:
    if face_dimension == 0:
        return 3
    minimum = 99
    for degrees in bounded_compositions(3 * support_size, 8, support_size):
        if 0 in degrees:
            motion = 3
        elif 1 in degrees:
            motion = 2
        elif face_dimension == 1 and sum(value == 2 for value in degrees) >= 2:
            motion = 2
        elif 2 in degrees:
            motion = 1
        else:
            motion = 0
        minimum = min(minimum, motion)
    return minimum


def verify_single_bad(control: dict, run_control: bool) -> dict:
    expected = {
        "verifier_path": "ai/omreal/verify_diag3_single_bad_two_skeleton.py",
        "verifier_sha256": "0ae6a9d54abcddbeb68be882083c52e1e6a9735941cea42eebacdf91ef77bda4",
        "theorem_path": "ai/omreal/DIAG3_SINGLE_BAD_TWO_SKELETON.md",
        "theorem_sha256": "141da1b6d9fcd4f601e79871aaa5d06cb98721ece928a0d0d5af83518bddf71f",
        "target_degree": 2,
        "max_augmented_equality_rank": 5,
        "expected_table": [
            {"face_dimension": 0, "maximum_support": 5, "forced_motion_dimension": 3, "required_motion_dimension": 3},
            {"face_dimension": 1, "maximum_support": 6, "forced_motion_dimension": 2, "required_motion_dimension": 2},
            {"face_dimension": 2, "maximum_support": 7, "forced_motion_dimension": 1, "required_motion_dimension": 1},
        ],
        "expected_stdout_markers": [
            "PASS augmented face bounds: k=0/1/2 use at most 5/6/7 coordinates",
            "PASS forced motion dimensions: 3/2/1",
            "THEOREM H_c^q(B_rho; R)=0 for q=0,1,2",
            "CAVEAT pair/triple terms and the third diagonal remain open",
        ],
        "binding_only": True,
        "extends_to_pair_or_triple": False,
    }
    for key, value in expected.items():
        require(control.get(key) == value, f"SINGLE_BAD_{key.upper()}_DRIFT")
    verifier = REPO / control["verifier_path"]
    theorem = REPO / control["theorem_path"]
    require(verifier.is_file() and sha256(verifier) == control["verifier_sha256"], "SINGLE_BAD_VERIFIER_SOURCE_PIN")
    require(theorem.is_file() and sha256(theorem) == control["theorem_sha256"], "SINGLE_BAD_THEOREM_SOURCE_PIN")
    independently_replayed = []
    for face_dimension, support in ((0, 5), (1, 6), (2, 7)):
        independently_replayed.append(control_motion(face_dimension, support))
    require(independently_replayed == [3, 2, 1], "SINGLE_BAD_COMBINATORIAL_REPLAY")
    stdout = "NOT_RUN_IN_MUTATION"
    if run_control:
        completed = subprocess.run(
            [sys.executable, "-B", str(verifier)],
            cwd=REPO,
            capture_output=True,
            text=True,
            timeout=180,
            check=False,
        )
        require(completed.returncode == 0, "SINGLE_BAD_CONTROL_EXECUTION", completed.stderr[-500:])
        stdout = completed.stdout
        for marker in control["expected_stdout_markers"]:
            require(marker in stdout, "SINGLE_BAD_OUTPUT_MARKER_MISSING", marker)
    return {
        "status": "PASS",
        "verifier_sha256": control["verifier_sha256"],
        "theorem_sha256": control["theorem_sha256"],
        "independent_motion_dimensions": independently_replayed,
        "canonical_control_executed": run_control,
        "binding_scope": "SINGLE_BAD_ONLY_NOT_PAIR_OR_TRIPLE",
    }


def verify_package(package: dict, run_control: bool = True) -> dict:
    require(package.get("format") == "d3-global-srep-polynomial-canaries-v1", "PACKAGE_FORMAT")
    require(package.get("opening_revision") == OPENING, "OPENING_PIN_DRIFT")
    require(package.get("scope") == "Q0_TOPOLOGY_FALSIFIER_ONLY", "PACKAGE_SCOPE")
    require(package.get("theorem_credit") == "NONE", "THEOREM_CREDIT_FORBIDDEN")
    return {
        "m3": verify_m3(package.get("m3", {})),
        "m2": verify_m2(package.get("m2", {})),
        "single_bad_control": verify_single_bad(package.get("single_bad_control", {}), run_control),
    }


def hostile_mutations() -> list[tuple[str, str, object]]:
    def set_path(data, path, value):
        target = data
        for item in path[:-1]:
            target = target[item]
        target[path[-1]] = value

    def delete_path(data, path):
        target = data
        for item in path[:-1]:
            target = target[item]
        del target[path[-1]]

    def copy_filled_into_unfilled(data):
        data["m3"]["models"]["unfilled"] = copy.deepcopy(data["m3"]["models"]["filled"])

    def flip_incidence(data):
        data["m3"]["models"]["filled"]["two_cell_trace"][2]["boundary"][0][0] = -1

    def omit_face(data):
        data["m3"]["common_trace"] = [cell for cell in data["m3"]["common_trace"] if cell["id"] != "e_02"]

    def duplicate_id(data):
        data["m3"]["common_trace"][6]["id"] = "e_02"

    return [
        ("m2_weak_closure_u_lt_1", "weak_closure", lambda d: set_path(d, ["m2", "atom_table", "one_minus_u_gt", "relation"], "ge")),
        ("m2_weak_closure_u_lt_2", "weak_closure", lambda d: set_path(d, ["m2", "atom_table", "two_minus_u_gt", "relation"], "ge")),
        ("m2_false_infinity_vertical_frontier", "false_infinity", lambda d: set_path(d, ["m2", "formula_ast", "true_parent_infinity"], fref("artificial_jump_frontier"))),
        ("m2_limit_falsely_selected_by_ambient", "weak_closure", lambda d: set_path(d, ["m2", "formula_ast", "pointwise_union"], fref("ambient_rectangle"))),
        ("m2_omit_central_terminal", "omitted_tag", lambda d: set_path(d, ["m2", "formula_ast", "pointwise_terminal"], conjunction(fref("ambient_rectangle"), aref("two_minus_u_eq")))),
        ("m2_claim_artificial_frontier_is_infinity", "false_infinity", lambda d: set_path(d, ["m2", "reported", "artificial_jump_frontier_is_true_infinity"], True)),
        ("m2_omit_artificial_frontier_formula_tag", "omitted_tag", lambda d: delete_path(d, ["m2", "formula_ast", "artificial_jump_frontier"])),
        ("m3_unfilled_formula_complex_disconnect", "formula_complex_disconnect", lambda d: set_path(d, ["m3", "models", "unfilled", "formula"], disjunction(fref("f_012"), fref("f_013"), fref("f_023")))),
        ("m3_filled_formula_complex_disconnect", "formula_complex_disconnect", lambda d: set_path(d, ["m3", "models", "filled", "formula"], disjunction(fref("f_012"), fref("f_013"), fref("e_23")))),
        ("m3_omit_edge_23_formula", "omitted_face", lambda d: set_path(d, ["m3", "common_one_skeleton_formula", "args"], d["m3"]["common_one_skeleton_formula"]["args"][:-1])),
        ("m3_omit_true_infinity_tag", "omitted_tag", lambda d: set_path(d, ["m3", "true_infinity"], {})),
        ("m3_false_infinity_vertex_0", "false_infinity", lambda d: set_path(d, ["m3", "true_infinity", "vertex"], 0)),
        ("m3_filled_unfilled_conflation", "filled_unfilled_conflation", copy_filled_into_unfilled),
        ("m3_report_rank_d2_as_three", "rank_error", lambda d: set_path(d, ["m3", "models", "unfilled", "reported_relative_chain", "rank_d2"], 3)),
        ("m3_report_h1_as_zero", "rank_error", lambda d: set_path(d, ["m3", "models", "unfilled", "reported_relative_chain", "h1_q"], 0)),
        ("m3_flip_face_incidence", "incidence_error", flip_incidence),
        ("m3_omit_required_trace_face", "omitted_face", omit_face),
        ("m3_duplicate_simplex_id", "incidence_error", duplicate_id),
        ("m3_hand_authored_complex_substitution", "hand_authored_complex", lambda d: set_path(d, ["m3", "source_mode"], "HAND_AUTHORED_COMPLEX")),
        ("m3_polynomial_coefficient_drift", "formula_complex_disconnect", lambda d: set_path(d, ["m3", "atom_table", "lambda_0_ge", "polynomial", 0, 0], 2)),
        ("single_bad_verifier_sha_drift", "control_binding", lambda d: set_path(d, ["single_bad_control", "verifier_sha256"], "0" * 64)),
        ("single_bad_rank_support_table_swap", "rank_error", lambda d: set_path(d, ["single_bad_control", "expected_table", 1, "maximum_support"], 7)),
        ("single_bad_illicit_pair_extension", "omitted_scope_tag", lambda d: set_path(d, ["single_bad_control", "extends_to_pair_or_triple"], True)),
    ]


def run_mutations(package: dict) -> list[dict]:
    results = []
    for name, category, mutate in hostile_mutations():
        candidate = copy.deepcopy(package)
        mutate(candidate)
        try:
            verify_package(candidate, run_control=False)
        except Rejected as failure:
            results.append({
                "id": name,
                "category": category,
                "rejected": True,
                "reason": failure.code,
            })
        else:
            results.append({
                "id": name,
                "category": category,
                "rejected": False,
                "reason": "MUTATION_ACCEPTED",
            })
    return results


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--fixture", type=Path, default=DEFAULT_FIXTURE)
    parser.add_argument("--json", action="store_true", help="emit the complete result as JSON")
    args = parser.parse_args()
    try:
        package = json.loads(args.fixture.read_text(encoding="utf-8"))
        baseline = verify_package(package, run_control=True)
        mutations = run_mutations(package)
        rejected = sum(item["rejected"] for item in mutations)
        require(rejected == len(mutations), "HOSTILE_MUTATION_SURVIVED")
        categories = sorted({item["category"] for item in mutations})
        result = {
            "format": "d3-global-srep-falsifier-result-v1",
            "status": "PASS",
            "verdict": "CANARY_PACKAGE_SOUND_PRODUCER_NOT_YET_REVIEWED",
            "opening_revision": OPENING,
            "q0_theorem_credit": "NONE",
            "baseline": baseline,
            "hostile_mutations": {
                "rejected": rejected,
                "total": len(mutations),
                "categories": categories,
                "results": mutations,
            },
            "scope_limits": [
                "These fixtures do not implement Basu-Karisani replacement.",
                "They do not certify a producer backend or the complete global schema.",
                "The single-bad result is bound only to its proved one-block scope.",
                "No theorem or ledger credit is claimed."
            ],
        }
    except (Rejected, OSError, json.JSONDecodeError, subprocess.SubprocessError) as failure:
        code = failure.code if isinstance(failure, Rejected) else type(failure).__name__
        result = {"status": "FAIL", "reason": code, "detail": str(failure)}
        if args.json:
            print(json.dumps(result, indent=2, sort_keys=True))
        else:
            print(f"FAIL {code}: {failure}")
        return 1
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("PASS exact polynomial M3 distinguishes relative H1_Q 1/0 with the same K4 one-skeleton and exit graph")
        print("PASS exact M2 nonclosure witness rejects the artificial jump frontier as true infinity")
        print("PASS pinned single-bad control and independent 3/2/1 motion table")
        print(f"PASS hostile mutations rejected {rejected}/{len(mutations)} across {len(categories)} categories")
        print("VERDICT CANARY_PACKAGE_SOUND_PRODUCER_NOT_YET_REVIEWED; theorem credit NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
