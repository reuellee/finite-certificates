#!/usr/bin/env python3
"""Exact replay for the universal-D9 cut prover's fail-closed null result.

The replay checks four independent boundaries:

* all source files are hash-pinned to the opening state;
* the finite edge-cut theorem is labeled conditional, never universal;
* the smooth-wall polynomial model has exactly three common components and
  exact witnesses for all 72 ordered incomparability directions; and
* the first type-36 parent-boundary elimination polynomial is absent from
  both the normalized parent-bracket catalog and the 26,740-factor census.

It deliberately does not construct a global parent roadmap or claim D9.
"""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from functools import reduce
import hashlib
from itertools import combinations, permutations
import json
from math import gcd
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SCHEMA_PATH = HERE / "CUT_REDUCTION_SCHEMA.json"
MODEL_PATH = HERE / "ABSTRACT_DISCONNECTED_COUNTERMODEL.json"
MANIFEST_PATH = HERE / "SOURCE_MANIFEST.json"
RESULT_PATH = HERE / "RESULT.json"
NVARIABLES = 9
ZERO_EXPONENT = (0,) * NVARIABLES
EXPECTED_PROTOCOL_PINS = {
    "ops/research-team/cycles/2026-09-01-d9-universal-cut/CYCLE.md":
        "6a51420d70b8ce0a67d1a23b641a2bca211745211bbfdeb5cb3d71d7f8aeb1df",
    "ops/research-team/cycles/2026-09-01-d9-universal-cut/OPENING_AUDIT.json":
        "007fd5f83a9256c31f1851303fed00df7a7b5a83107333d5fc96b4e6477d7639",
    "ops/research-team/cycles/2026-09-01-d9-universal-cut/WORK_ORDERS.yaml":
        "f156ebc83849863da90373818d837e0f55c745e57bdbfb279d2e8a593b6d9e12",
}


class GateError(AssertionError):
    """A fail-closed schema or evidence gate did not hold."""


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(path: Path):
    with path.open("r", encoding="utf-8") as source:
        return json.load(source)


def check_source_manifest(manifest) -> None:
    if manifest.get("format") != "d9-universal-cut-prover-source-manifest-v1":
        raise GateError("wrong source manifest format")
    if manifest.get("opening_commit") != "6cbd1b4a7d3ed61bee268b6b54cbfadeece90f0e":
        raise GateError("opening commit drift")
    if manifest.get("mathematics_base_revision") != "cbe84ccd7273252c81fd4da17ee360a284d2a2a6":
        raise GateError("mathematics base drift")
    if manifest.get("protocol_repair_source_commit") != "d07c2a7b041f3a075d5e9294a0f3c63dbd87822f":
        raise GateError("protocol repair source commit drift")
    if manifest.get("protocol_repair_source_tree") != "4dfba8740a306d0e2468d23aba3ac3c4cfe68f66":
        raise GateError("protocol repair source tree drift")
    if manifest.get("protocol_input_commit") != "48592c6cf37b2d316ee34743e5fa525f899d3bda":
        raise GateError("protocol input commit drift")
    if manifest.get("protocol_input_tree") != "897b2253514e1d065ce59b1558d5b47c2ee3e272":
        raise GateError("protocol input tree drift")
    files = manifest.get("files")
    if not isinstance(files, dict) or not files:
        raise GateError("empty source manifest")
    for relative, expected in sorted(files.items()):
        path = ROOT / relative
        if not path.is_file():
            raise GateError(f"missing source: {relative}")
        actual = sha256(path)
        if actual != expected:
            raise GateError(f"source digest drift: {relative}")
    if {relative: files.get(relative) for relative in EXPECTED_PROTOCOL_PINS} != EXPECTED_PROTOCOL_PINS:
        raise GateError("protocol source pins are not bound to the repaired inputs")
    historical = manifest.get("unavailable_and_unused", {})
    if historical.get("historical_referee_object") != "ca730426cdd5847ae262ddc29c6f4ae98369eba3":
        raise GateError("historical-object guard drift")


def clean(polynomial):
    return {monomial: int(value) for monomial, value in polynomial.items() if value}


def constant(value):
    return {} if value == 0 else {ZERO_EXPONENT: int(value)}


def variable(index):
    exponent = [0] * NVARIABLES
    exponent[index] = 1
    return {tuple(exponent): 1}


def add(*polynomials):
    result = {}
    for polynomial in polynomials:
        for monomial, value in polynomial.items():
            result[monomial] = result.get(monomial, 0) + value
    return clean(result)


def negative(polynomial):
    return {monomial: -value for monomial, value in polynomial.items()}


def subtract(left, right):
    return add(left, negative(right))


def multiply(*factors):
    result = constant(1)
    for factor in factors:
        product = {}
        for left, left_value in result.items():
            for right, right_value in factor.items():
                monomial = tuple(left[index] + right[index] for index in range(NVARIABLES))
                product[monomial] = product.get(monomial, 0) + left_value * right_value
        result = clean(product)
    return result


def permutation_sign(permutation):
    inversions = sum(
        permutation[left] > permutation[right]
        for left in range(len(permutation))
        for right in range(left + 1, len(permutation))
    )
    return -1 if inversions & 1 else 1


def determinant(matrix):
    result = {}
    for permutation in permutations(range(len(matrix))):
        term = multiply(*(matrix[row][permutation[row]] for row in range(len(matrix))))
        result = add(result, term if permutation_sign(permutation) > 0 else negative(term))
    return result


def primitive_key(polynomial):
    polynomial = clean(polynomial)
    if not polynomial:
        return ()
    divisor = reduce(gcd, (abs(value) for value in polynomial.values()), 0)
    terms = [(monomial, value // divisor) for monomial, value in polynomial.items()]
    leading = max(monomial for monomial, _ in terms)
    if dict(terms)[leading] < 0:
        terms = [(monomial, -value) for monomial, value in terms]
    return tuple(sorted(terms))


def normalized_parent_brackets():
    one, zero = constant(1), constant(0)
    a, b, c, d, e, f, g, h, i = (variable(index) for index in range(9))
    matrix = (
        (one, zero, zero, zero, one, one, one, one),
        (zero, one, zero, zero, one, a, d, g),
        (zero, zero, one, zero, one, b, e, h),
        (zero, zero, zero, one, one, c, f, i),
    )
    brackets = {}
    for basis in combinations(range(8), 4):
        square = tuple(tuple(matrix[row][column] for column in basis) for row in range(4))
        label = "".join(str(index + 1) for index in basis)
        brackets[label] = determinant(square)
    if len(brackets) != 70 or any(not value for value in brackets.values()):
        raise GateError("normalized parent bracket reconstruction failed")
    if brackets["1346"] != a:
        raise GateError("the type-36 boundary bracket [1346]=a was not reconstructed")
    return brackets


def global_factor_keys():
    source_path = ROOT / "ai/omreal/data/DIAG9_GRAPH_global_factor_census.npz"
    with np.load(source_path, allow_pickle=False) as source:
        offsets = np.asarray(source["factor_offset"], dtype=np.int64)
        exponents = np.asarray(source["factor_exponent"], dtype=np.int64)
        coefficients = np.asarray(source["factor_coefficient"], dtype=np.int64)
    if offsets.shape != (26_741,) or offsets[0] != 0 or offsets[-1] != len(exponents):
        raise GateError("global factor census shape drift")
    keys = set()
    for factor in range(26_740):
        polynomial = {
            tuple(map(int, exponents[index])): int(coefficients[index])
            for index in range(offsets[factor], offsets[factor + 1])
        }
        keys.add(primitive_key(polynomial))
    if len(keys) != 26_740:
        raise GateError("global factors are not primitive-distinct")
    return keys


def check_type36_boundary_gap() -> None:
    brackets = normalized_parent_brackets()
    a, _, c, d, _, f, _, _, _ = (variable(index) for index in range(9))
    q36 = add(multiply(a, f), negative(multiply(c, d)), c, negative(f))
    expected_q36 = {
        (1, 0, 0, 0, 0, 1, 0, 0, 0): 1,
        (0, 0, 1, 1, 0, 0, 0, 0, 0): -1,
        (0, 0, 1, 0, 0, 0, 0, 0, 0): 1,
        (0, 0, 0, 0, 0, 1, 0, 0, 0): -1,
    }
    if q36 != expected_q36:
        raise GateError("type-36 residual reconstruction failed")

    # Since the boundary polynomial is the pivot a itself, the resultant
    # Res_a(q36,a) is q36|_(a=0), up to the conventional global sign.
    restricted = {
        monomial: coefficient
        for monomial, coefficient in q36.items()
        if monomial[0] == 0
    }
    p = add(multiply(c, d), negative(c), f)
    if primitive_key(restricted) != primitive_key(p):
        raise GateError("wrong type-36 boundary elimination factor")

    p_key = primitive_key(p)
    bracket_keys = {primitive_key(value) for value in brackets.values()}
    if len(bracket_keys) != 63:
        raise GateError("normalized bracket key count drift")
    if p_key in bracket_keys:
        raise GateError("new boundary factor was misclassified as a parent bracket")
    if p_key in global_factor_keys():
        raise GateError("new boundary factor was misclassified as a global residual factor")


def quartic(x: Fraction) -> Fraction:
    return (x * x - 1) * (x * x - 4)


def evaluate_countermodel(point):
    x, y, *z = point
    return (y, quartic(x) - y, *z)


def ordered_incomparability_witness(left: int, right: int):
    point = [Fraction(0) for _ in range(9)]
    if left == 0 and right == 1:
        point[1] = Fraction(5)
    elif left == 1 and right == 0:
        point[1] = Fraction(-1)
    elif left == 0 and right >= 2:
        point[1] = Fraction(1)
        point[right] = Fraction(-1)
    elif left >= 2 and right == 0:
        point[left] = Fraction(1)
        point[1] = Fraction(-1)
    elif left == 1 and right >= 2:
        point[1] = Fraction(1)
        point[right] = Fraction(-1)
    elif left >= 2 and right == 1:
        point[left] = Fraction(1)
        point[1] = Fraction(5)
    else:
        point[left] = Fraction(1)
        point[right] = Fraction(-1)
    return tuple(point)


def check_countermodel(model) -> None:
    if model.get("format") != "d9-universal-cut-abstract-countermodel-v1":
        raise GateError("wrong abstract countermodel format")
    if model.get("component_count") != 3:
        raise GateError("countermodel component count drift")
    exact = model.get("exact_properties", {})
    if not exact.get("smooth_cooriented_walls"):
        raise GateError("smooth/cooriented wall guard missing")
    roots = (-2, -1, 1, 2)
    if any(quartic(Fraction(root)) != 0 for root in roots):
        raise GateError("quartic root factorization failed")
    test_points = (-3, Fraction(-3, 2), 0, Fraction(3, 2), 3)
    signs = tuple(1 if quartic(Fraction(value)) > 0 else -1 for value in test_points)
    if signs != (1, -1, 1, -1, 1):
        raise GateError("quartic interval-sign pattern failed")
    derivatives = tuple(4 * root**3 - 10 * root for root in roots)
    if derivatives != (-12, 6, -6, 12):
        raise GateError("multiwall transversality failed")
    stored = tuple(item["transverse_derivative"] for item in exact["q1_q2_multiwalls"])
    if stored != derivatives:
        raise GateError("stored multiwall derivative drift")

    witness_count = 0
    for left in range(9):
        for right in range(9):
            if left == right:
                continue
            values = evaluate_countermodel(ordered_incomparability_witness(left, right))
            if not (values[left] > 0 and values[right] < 0):
                raise GateError(f"ordered incomparability witness failed: {left},{right}")
            witness_count += 1
    if witness_count != 72:
        raise GateError("wrong incomparability witness count")
    infinity = model.get("infinity_profile", {})
    if infinity.get("unbounded_x_components") != 2 or infinity.get("bounded_x_components") != 1:
        raise GateError("countermodel infinity profile drift")


def check_schema(schema) -> None:
    if schema.get("format") != "d9-universal-cut-conditional-reduction-v1":
        raise GateError("wrong reduction schema format")
    theorem = schema.get("conditional_theorem", {})
    if theorem.get("status") != "PROVED_CONDITIONAL_ON_GLOBAL_STRATIFIED_COVERAGE":
        raise GateError("conditional theorem was silently changed")
    coverage = schema.get("global_stratified_coverage", {})
    if coverage.get("status") != "MISSING" or coverage.get("certificate") is not None:
        raise GateError("unmaterialized global coverage was promoted")
    grammar = schema.get("schema_grammar", {})
    residual_types = grammar.get("residual_orbit_types")
    if residual_types != [36, 37, 38, 39, 41, 42, 44, 46, 47, 48, 49, 50, 51]:
        raise GateError("residual orbit grammar drift")
    if grammar.get("record_type_count") != len(grammar.get("record_types", [])):
        raise GateError("schema record-type count drift")
    if grammar.get("record_type_count") >= 10_000:
        raise GateError("opening obstruction-type ceiling exceeded")
    boundary = grammar.get("boundary_policy", {})
    if boundary.get("recursive_parent_strata") != "REQUIRED_AND_DELETED_FROM_INTERIOR_ADJACENCY":
        raise GateError("recursive-facet policy missing")
    if boundary.get("genuine_infinity") != "REQUIRED_AND_DELETED_FROM_INTERIOR_ADJACENCY":
        raise GateError("genuine-infinity policy missing")
    if boundary.get("artificial_scope_boundary") != "NEVER_GENUINE_INFINITY":
        raise GateError("artificial infinity guard missing")
    if boundary.get("true_infinity_creates_interior_adjacency") is not False:
        raise GateError("infinity was incorrectly glued into the open parent")
    countermodel = schema.get("abstract_countermodel_gate", {})
    if countermodel.get("status") != "FORMALLY_OUT_OF_DOMAIN_BUT_NOT_REJECTED_AS_A_LOCAL_TO_GLOBAL_IMPLICATION_COUNTERMODEL":
        raise GateError("abstract countermodel scope guard drift")
    if not countermodel.get("formal_domain_rejection", "").startswith("PASS:"):
        raise GateError("abstract countermodel was not formally excluded from the D9 domain")
    if schema.get("opening_gate_verdict") != "STOP_UNIVERSAL_CUT_SCHEMA_COVERAGE_GAP":
        raise GateError("opening gate was silently promoted")


def check_result(result) -> None:
    if result.get("outcome") != "inconclusive":
        raise GateError("null result was promoted")
    if result.get("endpoint") != "UNIVERSAL_CUT_SCHEMA_COVERAGE_GAP":
        raise GateError("wrong null endpoint")
    if result.get("ledger_change_recommended") != "none":
        raise GateError("unauthorized ledger change recommended")
    expected_repair = {
        "source_commit": "d07c2a7b041f3a075d5e9294a0f3c63dbd87822f",
        "source_tree": "4dfba8740a306d0e2468d23aba3ac3c4cfe68f66",
        "cherry_pick_commit": "48592c6cf37b2d316ee34743e5fa525f899d3bda",
        "cherry_pick_tree": "897b2253514e1d065ce59b1558d5b47c2ee3e272",
    }
    if result.get("protocol_integration_repair") != expected_repair:
        raise GateError("result is not bound to the repaired protocol input")
    artifacts = result.get("artifacts", [])
    expected_paths = {
        "ops/team/d9-universal-cut-prover/ABSTRACT_DISCONNECTED_COUNTERMODEL.json",
        "ops/team/d9-universal-cut-prover/CUT_REDUCTION_SCHEMA.json",
        "ops/team/d9-universal-cut-prover/FINDINGS.md",
        "ops/team/d9-universal-cut-prover/SOURCE_MANIFEST.json",
        "ops/team/d9-universal-cut-prover/verify_cut_reduction_gap.py",
    }
    if {item.get("path") for item in artifacts} != expected_paths:
        raise GateError("result artifact manifest drift")
    for item in artifacts:
        path = ROOT / item["path"]
        if sha256(path) != item.get("sha256"):
            raise GateError(f"result artifact digest drift: {item['path']}")


def expect_rejected(schema, model, mutation) -> None:
    candidate_schema = deepcopy(schema)
    candidate_model = deepcopy(model)
    mutation(candidate_schema, candidate_model)
    try:
        check_schema(candidate_schema)
        check_countermodel(candidate_model)
    except GateError:
        return
    raise GateError("hostile mutation was accepted")


def main() -> None:
    manifest = load_json(MANIFEST_PATH)
    schema = load_json(SCHEMA_PATH)
    model = load_json(MODEL_PATH)
    result = load_json(RESULT_PATH)
    check_source_manifest(manifest)
    check_schema(schema)
    check_countermodel(model)
    check_type36_boundary_gap()
    check_result(result)

    mutations = (
        lambda s, m: s.__setitem__("opening_gate_verdict", "PASS"),
        lambda s, m: s["global_stratified_coverage"].__setitem__("status", "PROVED"),
        lambda s, m: s["schema_grammar"]["boundary_policy"].__setitem__("true_infinity_creates_interior_adjacency", True),
        lambda s, m: s["schema_grammar"]["boundary_policy"].__setitem__("recursive_parent_strata", "OMITTED"),
        lambda s, m: m.__setitem__("component_count", 2),
    )
    for mutation in mutations:
        expect_rejected(schema, model, mutation)

    print("PASS source pins: portable opening inputs, historical referee object unused")
    print("PASS conditional reduction schema: 9 record types, 13 residual orbit types")
    print("PASS abstract model: 72 incomparability witnesses, 4 transverse multiwalls, 3 components")
    print("PASS type-36 recursive-facet gap: cd-c+f absent from 70 brackets and 26740 residual factors")
    print("PASS hostile mutations: 5/5 rejected")
    print("NULL UNIVERSAL_CUT_SCHEMA_COVERAGE_GAP")
    print("SCOPE no global roadmap, separator census, UNSAT result, counterexample, or diagonal-nine claim")


if __name__ == "__main__":
    main()
