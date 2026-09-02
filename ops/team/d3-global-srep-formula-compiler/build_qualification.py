#!/usr/bin/env python3
"""Build the fail-closed Q0 formula/compiler producer handoff.

This module deliberately implements only an exact affine-simplex sublanguage.
It is capable of deriving the M3 triangle canaries from formulas, but it is
not an implementation of the Basu--Karisani simplicial-replacement algorithm.
The distinction is repeated in every generated result surface.
"""

from __future__ import annotations

import hashlib
import itertools
import json
import math
import os
import subprocess
import sys
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def dump_json(path: Path, payload: object) -> None:
    path.write_text(
        json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


# Polynomials are sparse integer polynomials.  Internal keys are exponent
# tuples in the formula's declared variable order.
def pclean(poly: dict[tuple[int, ...], int]) -> dict[tuple[int, ...], int]:
    return {key: int(value) for key, value in poly.items() if value}


def pconst(nvars: int, value: int) -> dict[tuple[int, ...], int]:
    return pclean({(0,) * nvars: value})


def pvar(nvars: int, index: int) -> dict[tuple[int, ...], int]:
    exponent = [0] * nvars
    exponent[index] = 1
    return {tuple(exponent): 1}


def padd(*polys: dict[tuple[int, ...], int]) -> dict[tuple[int, ...], int]:
    answer: dict[tuple[int, ...], int] = {}
    for poly in polys:
        for exponent, coefficient in poly.items():
            answer[exponent] = answer.get(exponent, 0) + coefficient
    return pclean(answer)


def pscale(poly: dict[tuple[int, ...], int], scale: int) -> dict[tuple[int, ...], int]:
    return pclean({key: scale * value for key, value in poly.items()})


def pmul(
    left: dict[tuple[int, ...], int], right: dict[tuple[int, ...], int]
) -> dict[tuple[int, ...], int]:
    answer: dict[tuple[int, ...], int] = {}
    for a, ca in left.items():
        for b, cb in right.items():
            exponent = tuple(x + y for x, y in zip(a, b, strict=True))
            answer[exponent] = answer.get(exponent, 0) + ca * cb
    return pclean(answer)


def pexternal(poly: dict[tuple[int, ...], int]) -> dict:
    terms = [
        {"coefficient": coefficient, "exponents": list(exponent)}
        for exponent, coefficient in sorted(poly.items())
    ]
    return {"type": "integer_polynomial", "terms": terms}


def pinternal(poly: dict) -> dict[tuple[int, ...], int]:
    if poly.get("type") != "integer_polynomial":
        raise ValueError("not an integer-polynomial AST")
    result: dict[tuple[int, ...], int] = {}
    width = None
    previous = None
    for term in poly.get("terms", []):
        coefficient = term.get("coefficient")
        exponent = tuple(term.get("exponents", []))
        if type(coefficient) is not int or not exponent:
            raise ValueError("noninteger coefficient or empty exponent vector")
        if any(type(value) is not int or value < 0 for value in exponent):
            raise ValueError("invalid exponent")
        width = len(exponent) if width is None else width
        if len(exponent) != width or (previous is not None and exponent <= previous):
            raise ValueError("noncanonical term order or arity")
        if not coefficient:
            raise ValueError("zero term in canonical polynomial")
        result[exponent] = coefficient
        previous = exponent
    return result


def pdegree(poly: dict[tuple[int, ...], int]) -> int:
    return max((sum(exponent) for exponent in poly), default=0)


def peval(poly: dict[tuple[int, ...], int], point: tuple[Fraction, ...]) -> Fraction:
    total = Fraction(0)
    for exponent, coefficient in poly.items():
        term = Fraction(coefficient)
        for value, power in zip(point, exponent, strict=True):
            term *= value**power
        total += term
    return total


def atom(op: str, poly: dict[tuple[int, ...], int]) -> dict:
    if op not in {"eq", "ge", "gt", "le", "lt"}:
        raise ValueError(op)
    return {"op": op, "poly": pexternal(poly)}


def junction(op: str, *args: dict) -> dict:
    if op not in {"and", "or"} or not args:
        raise ValueError(op)
    return {"op": op, "args": list(args)}


def eval_formula(formula: dict, point: tuple[Fraction, ...]) -> bool:
    op = formula["op"]
    if op in {"and", "or"}:
        values = [eval_formula(child, point) for child in formula["args"]]
        return all(values) if op == "and" else any(values)
    value = peval(pinternal(formula["poly"]), point)
    return {
        "eq": value == 0,
        "ge": value >= 0,
        "gt": value > 0,
        "le": value <= 0,
        "lt": value < 0,
    }[op]


def formula_atoms(formula: dict):
    if formula["op"] in {"and", "or"}:
        for child in formula["args"]:
            yield from formula_atoms(child)
    else:
        yield formula


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def m3_formulas() -> dict:
    nvars = 2
    x, y = pvar(nvars, 0), pvar(nvars, 1)
    l0 = padd(pconst(nvars, 1), pscale(x, -1), pscale(y, -1))
    l1, l2 = x, y
    simplex = junction("and", *(atom("ge", value) for value in (l0, l1, l2)))
    boundary = junction(
        "and",
        simplex,
        junction("or", *(atom("eq", value) for value in (l0, l1, l2))),
    )
    relative = junction("and", atom("eq", l1), atom("eq", l2))
    return {
        "format": "canonical-integer-polynomial-formula-v1",
        "variables": ["x", "y"],
        "simplex_barycentric_polynomials": [pexternal(value) for value in (l0, l1, l2)],
        "pairs": {
            "M3_UNFILLED": {"space": boundary, "relative": relative},
            "M3_FILLED": {"space": simplex, "relative": relative},
        },
    }


def compile_simplex_formula(formula: dict, relative: dict, barycentric: list[dict]) -> dict:
    allowed = {json.dumps(item, sort_keys=True) for item in barycentric}
    for current in (formula, relative):
        for current_atom in formula_atoms(current):
            if json.dumps(current_atom["poly"], sort_keys=True) not in allowed:
                raise ValueError("OUTSIDE_EXACT_AFFINE_SIMPLEX_SUBLANGUAGE")
            pinternal(current_atom["poly"])

    vertices = ((Fraction(0), Fraction(0)), (Fraction(1), Fraction(0)), (Fraction(0), Fraction(1)))
    accepted = []
    rel = []
    trace = []
    for cardinality in (1, 2, 3):
        for face in itertools.combinations(range(3), cardinality):
            sample = tuple(
                sum((vertices[index][coordinate] for index in face), Fraction(0)) / cardinality
                for coordinate in range(2)
            )
            in_space = eval_formula(formula, sample)
            in_relative = eval_formula(relative, sample)
            atom_values = [
                fraction_text(peval(pinternal(item["poly"]), sample))
                for item in formula_atoms(formula)
            ]
            trace.append(
                {
                    "face": [f"v{index}" for index in face],
                    "relative_interior_sample": [fraction_text(value) for value in sample],
                    "space_atom_values": atom_values,
                    "space_truth": in_space,
                    "relative_truth": in_relative,
                }
            )
            if in_space:
                accepted.append(face)
            if in_relative:
                rel.append(face)

    accepted_set, rel_set = set(accepted), set(rel)
    for face in accepted:
        for size in range(1, len(face)):
            if any(subface not in accepted_set for subface in itertools.combinations(face, size)):
                raise ValueError("FORMULA_SELECTION_IS_NOT_A_SUBCOMPLEX")
    if not rel_set <= accepted_set:
        raise ValueError("RELATIVE_FORMULA_NOT_A_SUBCOMPLEX")
    for face in rel:
        for size in range(1, len(face)):
            if any(subface not in rel_set for subface in itertools.combinations(face, size)):
                raise ValueError("RELATIVE_SELECTION_IS_NOT_DOWNWARD_CLOSED")
    return {
        "backend": "EXACT_AFFINE_SIMPLEX_FORMULA_COMPILER_V1",
        "backend_scope": "BOOLEAN_COMBINATIONS_OF_STANDARD_SIMPLEX_BARYCENTRIC_ATOMS_ONLY",
        "derivation": "FORMULA_TRUTH_ON_EACH_FACE_RELATIVE_INTERIOR_WITH_SIGN_INVARIANCE_BY_SUBLANGUAGE",
        "faces": [[f"v{index}" for index in face] for face in accepted],
        "relative_faces": [[f"v{index}" for index in face] for face in rel],
        "face_trace": trace,
    }


def face_tuples(compiled: dict, key: str) -> set[tuple[str, ...]]:
    return {tuple(face) for face in compiled[key]}


def boundary_matrix(compiled: dict, dimension: int) -> list[list[int]]:
    faces = face_tuples(compiled, "faces")
    relative = face_tuples(compiled, "relative_faces")
    source = sorted(face for face in faces - relative if len(face) == dimension + 1)
    target = sorted(face for face in faces - relative if len(face) == dimension)
    target_index = {face: index for index, face in enumerate(target)}
    matrix = [[0 for _ in source] for _ in target]
    for column, face in enumerate(source):
        for deleted in range(len(face)):
            subface = face[:deleted] + face[deleted + 1 :]
            if subface in relative:
                continue
            if subface not in target_index:
                raise ValueError("MISSING_SIMPLICIAL_FACE")
            matrix[target_index[subface]][column] += -1 if deleted % 2 else 1
    return matrix


def rank_q(matrix: list[list[int]]) -> int:
    if not matrix or not matrix[0]:
        return 0
    work = [[Fraction(value) for value in row] for row in matrix]
    pivot_row = 0
    for column in range(len(work[0])):
        pivot = next((row for row in range(pivot_row, len(work)) if work[row][column]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        value = work[pivot_row][column]
        work[pivot_row] = [entry / value for entry in work[pivot_row]]
        for row in range(len(work)):
            if row == pivot_row or not work[row][column]:
                continue
            value = work[row][column]
            work[row] = [
                a - value * b for a, b in zip(work[row], work[pivot_row], strict=True)
            ]
        pivot_row += 1
    return pivot_row


def relative_h1(compiled: dict) -> dict:
    d1, d2 = boundary_matrix(compiled, 1), boundary_matrix(compiled, 2)
    faces = face_tuples(compiled, "faces") - face_tuples(compiled, "relative_faces")
    c1 = sum(len(face) == 2 for face in faces)
    h1 = c1 - rank_q(d1) - rank_q(d2)
    return {"boundary_1": d1, "boundary_2": d2, "rank_d1": rank_q(d1), "rank_d2": rank_q(d2), "dim_c1": c1, "h1_q": h1}


def m2_formula() -> dict:
    nvars = 2
    s, u = pvar(nvars, 0), pvar(nvars, 1)
    one, two = pconst(nvars, 1), pconst(nvars, 2)
    ambient = junction(
        "and",
        atom("ge", padd(s, one)),
        atom("ge", padd(one, pscale(s, -1))),
        atom("ge", u),
        atom("ge", padd(two, pscale(u, -1))),
    )
    selected = junction(
        "and",
        ambient,
        junction(
            "or",
            junction("and", atom("eq", s), atom("lt", padd(u, pscale(one, -1)))),
            junction(
                "and",
                junction("or", atom("lt", s), atom("gt", s)),
                atom("lt", padd(u, pscale(two, -1))),
            ),
        ),
    )
    terminal = junction(
        "and",
        ambient,
        junction(
            "or",
            junction("and", atom("eq", s), atom("eq", padd(u, pscale(one, -1)))),
            atom("eq", padd(u, pscale(two, -1))),
        ),
    )
    return {
        "format": "canonical-integer-polynomial-formula-v1",
        "variables": ["s", "u"],
        "selected_strip": selected,
        "pointwise_terminal": terminal,
        "selected_plus_terminal": junction("or", selected, terminal),
    }


def analyze_m2(payload: dict) -> dict:
    union = payload["selected_plus_terminal"]
    sequence_checks = []
    for denominator in range(1, 33):
        point = (Fraction(1, denominator), Fraction(3, 2))
        if not eval_formula(union, point):
            raise AssertionError("M2 exact sequence point was rejected")
        sequence_checks.append([fraction_text(value) for value in point])
    limit = (Fraction(0), Fraction(3, 2))
    if eval_formula(union, limit):
        raise AssertionError("M2 excluded limit was accepted")
    return {
        "classification": "REJECT_NONCLOSED_SOURCE_EXPLICIT_CURVE_LIMIT_WITNESS",
        "complex_emitted": False,
        "witness_curve": {"parameter_domain": "0<t<=1", "map": {"s": "t", "u": "3/2"}},
        "symbolic_branch_certificate": [
            "s=t>0 selects the s!=0 branch",
            "-1<=t<=1",
            "0<=3/2<2",
            "therefore every (t,3/2), 0<t<=1, is selected",
            "the limit (0,3/2) is neither u<1 nor u=1 nor u=2",
        ],
        "finite_exact_sequence_crosscheck": sequence_checks,
        "excluded_limit": ["0", "3/2"],
        "blind_strict_to_weak_closure_allowed": False,
    }


def permutation_sign(permutation: tuple[int, ...]) -> int:
    inversions = sum(
        permutation[i] > permutation[j]
        for i in range(len(permutation))
        for j in range(i + 1, len(permutation))
    )
    return -1 if inversions % 2 else 1


def determinant(columns: list[list[dict[tuple[int, ...], int]]]) -> dict[tuple[int, ...], int]:
    size = len(columns)
    nvars = next(
        len(exponent)
        for column in columns
        for entry in column
        for exponent in entry
    )
    answer: dict[tuple[int, ...], int] = {}
    for permutation in itertools.permutations(range(size)):
        term = pconst(nvars, permutation_sign(permutation))
        for column, row in enumerate(permutation):
            term = pmul(term, columns[column][row])
        answer = padd(answer, term)
    return answer


def global_algebra_schema() -> dict:
    variables = ["a", "b", "c", "d", "e", "f", "g", "h", "i"]
    nvars = len(variables)
    zero, one = pconst(nvars, 0), pconst(nvars, 1)
    vs = [pvar(nvars, index) for index in range(nvars)]
    a, b, c, d, e, f, g, h, i = vs
    columns = [
        [one, zero, zero, zero],
        [zero, one, zero, zero],
        [zero, zero, one, zero],
        [zero, zero, zero, one],
        [one, one, one, one],
        [one, a, b, c],
        [one, d, e, f],
        [one, g, h, i],
    ]
    brackets = []
    for basis in itertools.combinations(range(8), 4):
        poly = determinant([columns[index] for index in basis])
        brackets.append({"basis_one_based": [index + 1 for index in basis], "poly": pexternal(poly), "degree": pdegree(poly)})
    normals = []
    for triple in itertools.combinations(range(8), 3):
        coefficients = []
        for row in range(4):
            unit = [zero, zero, zero, zero]
            unit[row] = one
            poly = determinant([columns[index] for index in triple] + [unit])
            coefficients.append(pexternal(poly))
        normals.append({"triple_one_based": [index + 1 for index in triple], "extension_linear_coefficients": coefficients})
    bracket_keys = {json.dumps(item["poly"], sort_keys=True) for item in brackets}
    normal_keys = {
        json.dumps(poly, sort_keys=True)
        for item in normals
        for poly in item["extension_linear_coefficients"]
    }
    return {
        "format": "9dvl-global-raw-algebra-template-v1",
        "variables": variables,
        "normalized_matrix_column_rule": "I4 | (1,1,1,1) | (1,a,b,c) | (1,d,e,f) | (1,g,h,i)",
        "parent_brackets": brackets,
        "derived_extension_normals": normals,
        "counts": {
            "parent_bracket_occurrences": len(brackets),
            "distinct_parent_bracket_polynomials_including_constants": len(bracket_keys),
            "derived_normal_rows": len(normals),
            "derived_normal_coefficient_occurrences": 4 * len(normals),
            "distinct_derived_normal_coefficient_polynomials_including_zero": len(normal_keys),
            "max_parent_bracket_degree": max(item["degree"] for item in brackets),
            "max_derived_normal_coefficient_degree": max(
                pdegree(pinternal(poly))
                for item in normals
                for poly in item["extension_linear_coefficients"]
            ),
        },
        "signature_action": "For signature bit rho_I, multiply all four coefficients of row I by +1 when the bit is 1 and -1 when it is 0.",
        "bad_locus_resolution": "lambda_I>=0; sum_I lambda_I=1; for each coordinate q, sum_I lambda_I*(-1)^(1-rho_I)*a_Iq(Y)=0",
        "claim_boundary": "Exact raw determinant/Gordan algebra only; no compact closure, properness, incomparability, or simplicial replacement is asserted.",
    }


def discrete_scope_accounting() -> dict:
    manifest_path = REPO / "ops/team/diag3-orbit5563-prover/TYPE_FRAME_S8_QUOTIENT_MANIFEST.json"
    extcount_path = REPO / "ai/omgamma/data/extcount_4_9.jsonl"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    parent_indices = [int(row[0]) for row in manifest["catalog"]["entries"]]
    extcounts = {}
    for line in extcount_path.read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        extcounts[int(record["i"])] = int(record["E"])
    if len(parent_indices) != 2604 or len(set(parent_indices)) != 2604:
        raise AssertionError("realizable parent denominator changed")
    missing = sorted(set(parent_indices) - set(extcounts))
    if missing:
        raise AssertionError(f"missing extension counts: {missing[:5]}")
    values = [extcounts[index] for index in parent_indices]
    ordered_distinct = [value * (value - 1) * (value - 2) for value in values]
    type_candidate_total = sum(ordered_distinct)
    return {
        "source_pins": {
            str(manifest_path.relative_to(REPO)).replace("\\", "/"): sha256(manifest_path),
            str(extcount_path.relative_to(REPO)).replace("\\", "/"): sha256(extcount_path),
        },
        "certified_finite_inputs": {
            "realizable_unlabelled_parent_types": len(parent_indices),
            "raw_labelled_frames_per_parent_type": 40320,
            "raw_parent_frame_presentations": len(parent_indices) * 40320,
            "sum_valid_abstract_extension_signatures_over_unlabelled_types": sum(values),
            "minimum_valid_signatures_on_a_type": min(values),
            "maximum_valid_signatures_on_a_type": max(values),
            "ordered_distinct_signature_triples_before_properness_or_incomparability_over_types": type_candidate_total,
            "ordered_distinct_signature_triples_before_properness_or_incomparability_over_raw_frames": type_candidate_total * 40320,
        },
        "first_missing_required_denominator": {
            "id": "ALL_PARENT_PROPER_REGION_AND_PAIRWISE_INCOMPARABILITY_CLASSIFICATION",
            "status": "MISSING",
            "reason": "The extension-count table enumerates abstract valid sign extensions only. It does not decide whether F_sigma is a proper subset of the full normalized realization space, equality/inclusion among F_sigma, or which ordered triples are pairwise incomparable, for every parent and realization component.",
            "consequence": "The required ordered proper pairwise-incomparable triple denominator, and therefore global N, cannot be stated exactly.",
        },
        "second_missing_formula_input": {
            "id": "QUANTIFIER_FREE_P_CLOSED_EXACT_PARENT_COMPACTIFICATION",
            "status": "MISSING",
            "reason": "A first-order closure predicate is uniform, but no exact quantifier-free P-closed formula for Xbar_M and genuine I_M has been generated and pinned for all parents. Replacing strict signs by weak signs is unsound.",
        },
    }


def replay_single_bad() -> dict:
    script = REPO / "ai/omreal/verify_diag3_single_bad_two_skeleton.py"
    theorem = REPO / "ai/omreal/DIAG3_SINGLE_BAD_TWO_SKELETON.md"
    process = subprocess.run(
        [sys.executable, "-B", str(script)],
        cwd=REPO,
        text=True,
        capture_output=True,
        timeout=300,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
    )
    if process.returncode != 0:
        raise AssertionError(f"single-bad replay failed: {process.stderr}")
    required = "THEOREM H_c^q(B_rho; R)=0 for q=0,1,2"
    if required not in process.stdout:
        raise AssertionError("single-bad replay lost theorem marker")
    return {
        "classification": "BOUND_REPLAY_OF_EXISTING_PROVED_CONTROL_NOT_A_NEW_DERIVATION",
        "command": f"{Path(sys.executable).name} -B ai/omreal/verify_diag3_single_bad_two_skeleton.py",
        "exit_code": process.returncode,
        "stdout": process.stdout.splitlines(),
        "source_pins": {
            "ai/omreal/verify_diag3_single_bad_two_skeleton.py": sha256(script),
            "ai/omreal/DIAG3_SINGLE_BAD_TWO_SKELETON.md": sha256(theorem),
        },
    }


def backend_inventory() -> dict:
    return {
        "as_of": "2026-09-02",
        "verdict": "NO_EXECUTABLE_BASU_KARISANI_REPLACEMENT_BACKEND_IDENTIFIED",
        "searches": [
            {"surface": "pinned papers", "queries": ["github", "software", "implementation", "source code", "package"], "hits": 0},
            {"surface": "GitHub repository API", "query": "\"Efficient simplicial replacement of semi-algebraic sets\"", "total_count": 0},
            {"surface": "GitHub repository API", "query": "\"Basu\" \"Karisani\" simplicial", "total_count": 0},
            {"surface": "GitHub code API", "query": "\"Efficient simplicial replacement\"", "total_count": 0},
            {"surface": "GitHub code API", "query": "\"Basu-Karisani\"", "total_count": 0},
            {"surface": "PyPI index", "query": "simplicial-replacement", "result": "NO_MATCHING_DISTRIBUTION"},
            {"surface": "PyPI index", "query": "semialgebraic-homology", "result": "NO_MATCHING_DISTRIBUTION"},
        ],
        "available_nonreplacement_tools": [
            "Wolfram exact RCF/QE primitives",
            "WSL Singular/SymPy exact algebra primitives",
            "narrow exact affine-simplex compiler in this package",
        ],
        "absence_claim_boundary": "This is a documented search failure, not a proof that no private or unpublished implementation exists.",
    }


def main() -> None:
    m3 = m3_formulas()
    m2 = m2_formula()
    dump_json(HERE / "FORMULAS.json", {"M3": m3, "M2": m2})

    compiled = {}
    homology = {}
    for name, pair in m3["pairs"].items():
        current = compile_simplex_formula(
            pair["space"], pair["relative"], m3["simplex_barycentric_polynomials"]
        )
        compiled[name] = current
        homology[name] = relative_h1(current)
    unfilled_1skeleton = sorted(face for face in compiled["M3_UNFILLED"]["faces"] if len(face) <= 2)
    filled_1skeleton = sorted(face for face in compiled["M3_FILLED"]["faces"] if len(face) <= 2)
    if unfilled_1skeleton != filled_1skeleton:
        raise AssertionError("M3 one-skeleta differ")
    if (homology["M3_UNFILLED"]["h1_q"], homology["M3_FILLED"]["h1_q"]) != (1, 0):
        raise AssertionError("M3 relative ranks changed")

    m2_result = analyze_m2(m2)
    single_bad = replay_single_bad()
    algebra = global_algebra_schema()
    scope = discrete_scope_accounting()
    inventory = backend_inventory()
    dump_json(HERE / "GLOBAL_SCHEMA.json", {"raw_algebra": algebra, "scope": scope})
    dump_json(HERE / "BACKEND_INVENTORY.json", inventory)

    trace = {
        "format": "d3-global-srep-formula-producer-trace-v1",
        "backend_identity": {
            "name": "EXACT_AFFINE_SIMPLEX_FORMULA_COMPILER_V1",
            "qualifies_as_general_simplicial_replacement": False,
            "classification": "CANARY_ONLY_NONQUALIFYING_SURROGATE",
            "ordered_infinitesimals": "ABSENT_NOT_NEEDED_IN_AFFINE_SIMPLEX_SUBLANGUAGE",
            "algebraic_numbers": "RATIONALS_ONLY_AS_REDUCED_NUMERATOR_DENOMINATOR_STRINGS",
        },
        "M3": {
            "compiled": compiled,
            "relative_homology_over_q": homology,
            "same_one_skeleton": True,
        },
        "M2": m2_result,
        "single_bad_control": single_bad,
    }
    dump_json(HERE / "TRACE.json", trace)

    partial_parameters = {
        "ell": 2,
        "N": None,
        "s": None,
        "d": None,
        "k": 178,
        "k_derivation": "10 compact parent coordinates (nine homogenized coordinates plus z) + 3*56 normalized Gordan weights",
        "raw_preclosure_occurrence_bound": {
            "polynomial_occurrences_for_three_witness_blocks_plus_parent_sphere_and_z": 255,
            "derivation": "70 parent brackets + 3*(56 nonnegative weights + 1 normalization + 4 Gordan equations) + sphere + z",
            "raw_max_degree": 4,
        },
        "why_N_s_d_are_null": "N depends on the missing proper incomparable triple denominator and a frozen diagram-node encoding; exact s and d depend on the missing quantifier-free P-closed compactification/QE output.",
        "only_honest_forecast": "(N*s*d)^(178^(O(2))) after the missing inputs exist; the hidden O(2) constant and null N,s,d prevent a numeric output, memory, or elapsed-time forecast.",
        "fixed_cycle_ceiling_fit": "NOT_DEMONSTRATED",
    }

    result = {
        "format": "d3-global-srep-formula-compiler-result-v1",
        "track": "d3-global-srep-formula-compiler",
        "q0_classification": "NULL_NO_EXECUTABLE_REPLACEMENT_BACKEND",
        "q0_pass": False,
        "q1_eligible": False,
        "theorem_credit": "NONE",
        "cloud_used": False,
        "producer_self_acceptance": False,
        "canaries": {
            "M3_UNFILLED_RELATIVE_H1_1": "PASS_EXACT_FORMULA_DERIVED_AFFINE_SIMPLEX_SURROGATE_ONLY",
            "M3_FILLED_RELATIVE_H1_0": "PASS_EXACT_FORMULA_DERIVED_AFFINE_SIMPLEX_SURROGATE_ONLY",
            "M3_SAME_ONE_SKELETON": "PASS_EXACT_SURROGATE_ONLY",
            "M2_NONCLOSED_TANGENTIAL_FIRST_EXIT": "PASS_REJECTED_BEFORE_COMPLEX",
            "SINGLE_BAD_LOW_DEGREE_CONTROL": "PASS_BOUND_EXISTING_REPLAY",
            "COMPLETE_GLOBAL_TAGGED_SCHEMA": "NULL_FIRST_MISSING_DENOMINATOR_PINNED",
        },
        "backend_inventory_verdict": inventory["verdict"],
        "global_scope": scope,
        "partial_basu_karisani_parameters": partial_parameters,
        "first_terminal_blocker": "No executable, independently traceable Basu--Karisani replacement backend is available; additionally, the exact required proper/incomparable triple denominator and P-closed compactification formula are missing.",
        "nonconsequences": [
            "NO_GENERAL_SIMPLICIAL_REPLACEMENT_IMPLEMENTATION",
            "NO_Q0_ACCEPTANCE",
            "NO_Q1_ACTIVATION",
            "NO_COMPLETE_GLOBAL_N_S_D_K",
            "NO_GLOBAL_DIAGRAM",
            "NO_PAIR_KERNEL_RESULT",
            "NO_DIAGONAL_OR_LEDGER_CHANGE",
        ],
        "replay_commands": [
            "python -B ops/team/d3-global-srep-formula-compiler/build_qualification.py",
            "python -B ops/team/d3-global-srep-formula-compiler/test_formula_compiler.py",
        ],
    }
    dump_json(HERE / "RESULT.json", result)

    input_paths = [
        "ops/research-team/cycles/2026-09-02-d3-global-semialgebraic-diagram-replacement-gate1/CYCLE.md",
        "ops/research-team/cycles/2026-09-02-d3-global-semialgebraic-diagram-replacement-gate1/WORK_ORDERS.yaml",
        "ops/research-team/cycles/2026-09-02-d3-global-semialgebraic-diagram-replacement-gate1/OPENING_STATE.json",
        "ops/research-team/cycles/2026-09-02-d3-global-semialgebraic-diagram-replacement-gate1/LITERATURE_MANIFEST.json",
        "ops/research-sources/basu-karisani/arxiv-2009.13365v3.pdf",
        "ops/research-sources/basu-karisani/arxiv-2207.10497v1.pdf",
        "ops/team/d3-mixed-carrier-falsifier/OBSTRUCTION_DOSSIER.md",
        "ai/omreal/verify_diag3_tangential_first_exit_no_go.py",
        "ai/omreal/DIAG3_SINGLE_BAD_TWO_SKELETON.md",
        "ai/omreal/verify_diag3_single_bad_two_skeleton.py",
        "ai/omreal/data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json",
        "ai/omgamma/data/extcount_4_9.jsonl",
        "ops/team/diag3-orbit5563-prover/TYPE_FRAME_S8_QUOTIENT_MANIFEST.json",
    ]
    output_names = [
        "build_qualification.py",
        "test_formula_compiler.py",
        "REPORT.md",
        "FORMULAS.json",
        "GLOBAL_SCHEMA.json",
        "BACKEND_INVENTORY.json",
        "TRACE.json",
        "RESULT.json",
    ]
    source_manifest = {
        "format": "d3-global-srep-formula-compiler-source-manifest-v1",
        "inputs": {
            relative: {"bytes": (REPO / relative).stat().st_size, "sha256": sha256(REPO / relative)}
            for relative in input_paths
        },
        "producer_outputs": {
            name: {"bytes": (HERE / name).stat().st_size, "sha256": sha256(HERE / name)}
            for name in output_names
        },
        "frozen_opening_revision": "c50da6c99d465c65b3e54427418d9efe6a3f037e",
        "cloud_used": False,
    }
    dump_json(HERE / "SOURCE_MANIFEST.json", source_manifest)
    print("PASS exact M3 affine-simplex formula surrogates: relative H1(Q)=1/0")
    print("PASS exact M2 nonclosure witness: no complex emitted")
    print("PASS bound replay of single-bad low-degree control")
    print("NULL required proper/incomparable global denominator and P-closed compactification")
    print("NULL_NO_EXECUTABLE_REPLACEMENT_BACKEND")


if __name__ == "__main__":
    main()
