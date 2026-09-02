#!/usr/bin/env python3
"""Build the exact factor-19069 homogenizer-boundary constructor frontier.

The implementation deliberately uses only integer sparse-polynomial
arithmetic.  It restricts the pinned 108-term trihomogeneous source before
differentiating for stratum singularity, while separately restricting all
twelve ambient derivatives.  It does not run a whole-chart Groebner basis.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
from time import perf_counter


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PREDECESSOR = ROOT / "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-constructor/PROJECTIVE_CHART_FRONTIER.json"
FRONTIER = HERE / "HOMOGENIZER_BOUNDARY_TYPE_FRONTIER.json"
MANIFEST = HERE / "SOURCE_MANIFEST.json"
RESULT = HERE / "RESULT.json"

BASE = "0ffb0295d74e6c50a3c198b67c9821d2fe2e2760"
BASE_TREE = "d01cfbbe04f721496a91d13f85d3688262869ac0"
OPENING = "aad8e1efa5a45e47c9f924dce5263a07996a10e9"
OPENING_TREE = "8b8fcd6652a0245df9b2a7f262f4c48bb5fdc883"
CYCLE_ID = "2026-09-01-d9-row2599-factor19069-homogenizer-boundary-type-stratification-gate1"
TRACK_ID = "d9-factor19069-homogenizer-boundary-constructor"
ORDER = ("a", "b", "c", "u", "d", "e", "f", "v", "g", "h", "i", "w")
TYPES = (("u", "v", "w"), ("u", "v"), ("u", "w"), ("v", "w"), ("u",), ("v",), ("w",))
EXPECTED_TERMS = (11, 37, 23, 23, 64, 69, 47)
PREDECESSOR_SHA256 = "815edf97a68a049f8fb6749adf948cc406ec7a258de480cf3ada3e301ca6de67"

Poly = dict[tuple[int, ...], int]


def canonical(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")


def pretty(value: object) -> bytes:
    return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + "\n").encode("utf-8")


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def semantic(value: dict) -> str:
    item = deepcopy(value)
    item.pop("semantic_sha256", None)
    return digest(canonical(item))


def sparse(terms: list[dict]) -> Poly:
    out: Poly = {}
    for term in terms:
        exponent = tuple(int(x) for x in term["exponents"])
        coefficient = int(term["coefficient"])
        out[exponent] = out.get(exponent, 0) + coefficient
    return {m: c for m, c in out.items() if c}


def terms(poly: Poly) -> list[dict]:
    return [
        {"coefficient": coefficient, "exponents": list(monomial)}
        for monomial, coefficient in sorted(poly.items())
    ]


def add(*polynomials: Poly) -> Poly:
    out: Poly = {}
    for poly in polynomials:
        for monomial, coefficient in poly.items():
            out[monomial] = out.get(monomial, 0) + coefficient
    return {m: c for m, c in out.items() if c}


def scale(poly: Poly, coefficient: int) -> Poly:
    return {m: coefficient * c for m, c in poly.items() if coefficient * c}


def multiply(left: Poly, right: Poly) -> Poly:
    out: Poly = {}
    for lm, lc in left.items():
        for rm, rc in right.items():
            monomial = tuple(a + b for a, b in zip(lm, rm))
            out[monomial] = out.get(monomial, 0) + lc * rc
    return {m: c for m, c in out.items() if c}


def derivative(poly: Poly, variable: str) -> Poly:
    index = ORDER.index(variable)
    out: Poly = {}
    for monomial, coefficient in poly.items():
        if monomial[index]:
            reduced = list(monomial)
            power = reduced[index]
            reduced[index] -= 1
            key = tuple(reduced)
            out[key] = out.get(key, 0) + coefficient * power
    return {m: c for m, c in out.items() if c}


def restrict(poly: Poly, zero_variables: tuple[str, ...]) -> Poly:
    zero_indices = {ORDER.index(name) for name in zero_variables}
    return {
        monomial: coefficient
        for monomial, coefficient in poly.items()
        if all(monomial[index] == 0 for index in zero_indices)
    }


def mono(coefficient: int = 1, **powers: int) -> Poly:
    exponent = tuple(int(powers.get(name, 0)) for name in ORDER)
    return {exponent: coefficient} if coefficient else {}


def poly_record(node_id: str, poly: Poly) -> dict:
    record = {
        "node_id": node_id,
        "coordinate_order": list(ORDER),
        "coefficient_field": "Q",
        "term_count": len(poly),
        "sparse_polynomial": terms(poly),
    }
    record["semantic_sha256"] = semantic(record)
    return record


def monomial_divide(poly: Poly, variable: str) -> Poly:
    index = ORDER.index(variable)
    assert all(monomial[index] >= 1 for monomial in poly)
    out: Poly = {}
    for monomial, coefficient in poly.items():
        reduced = list(monomial)
        reduced[index] -= 1
        out[tuple(reduced)] = coefficient
    return out


def lift_affine_parent(record: dict) -> Poly:
    """Embed a pinned Q[a,b,c,d,e,f,g,h,i] parent factor in ORDER."""
    affine_order = ("a", "b", "c", "d", "e", "f", "g", "h", "i")
    out: Poly = {}
    for term in record["sparse_polynomial"]:
        exponent = [0] * len(ORDER)
        for name, power in zip(affine_order, term["exponents"]):
            exponent[ORDER.index(name)] = int(power)
        out[tuple(exponent)] = int(term["coefficient"])
    return out


def git_bytes(revision: str, path: str) -> bytes:
    return subprocess.check_output(
        ["git", "-c", f"safe.directory={ROOT.as_posix()}", "show", f"{revision}:{path}"],
        cwd=ROOT,
    )


def make_deepest_data(source: Poly, deepest: Poly, parent_frontier: dict) -> tuple[dict, int]:
    h = mono(h=1)
    linear_minor = add(mono(a=1, f=1), mono(-1, c=1, d=1))
    determinant = add(
        mono(a=1, e=1, i=1),
        mono(-1, a=1, f=1, h=1),
        mono(-1, b=1, d=1, i=1),
        mono(b=1, f=1, g=1),
        mono(c=1, d=1, h=1),
        mono(-1, c=1, e=1, g=1),
    )
    assert deepest == scale(multiply(multiply(h, linear_minor), determinant), -1)

    parent_records = parent_frontier["records"]
    parent_h = parent_records[8]
    parent_l = parent_records[22]
    parent_c = parent_records[34]
    assert parent_h["factor_node_id"] == "H_08_1248"
    assert parent_l["factor_node_id"] == "H_22_1367"
    assert parent_c["factor_node_id"] == "H_34_1678"
    assert lift_affine_parent(parent_h) == h
    assert lift_affine_parent(parent_l) == scale(linear_minor, -1)
    assert lift_affine_parent(parent_c) == determinant
    parent_matches = [
        {
            "source_factor": "h",
            "parent_factor_index": 8,
            "parent_factor_node_id": parent_h["factor_node_id"],
            "parent_record_semantic_sha256": parent_h["semantic_sha256"],
            "relationship": "EXACT_SPARSE_EQUALITY",
        },
        {
            "source_factor": "L=a*f-c*d",
            "parent_factor_index": 22,
            "parent_factor_node_id": parent_l["factor_node_id"],
            "parent_record_semantic_sha256": parent_l["semantic_sha256"],
            "relationship": "EXACT_SPARSE_NEGATIVE_EQUALITY_PARENT_EQUALS_MINUS_L",
        },
        {
            "source_factor": "C=det([[a,b,c],[d,e,f],[g,h,i]])",
            "parent_factor_index": 34,
            "parent_factor_node_id": parent_c["factor_node_id"],
            "parent_record_semantic_sha256": parent_c["semantic_sha256"],
            "relationship": "EXACT_SPARSE_EQUALITY",
        },
    ]

    substitutions = ("u", "v", "w")
    normal = {name: restrict(derivative(source, name), substitutions) for name in substitutions}
    d_minus_f = add(mono(d=1), mono(-1, f=1))
    s_factor = add(
        mono(a=1, h=1), mono(-1, a=1, i=1), mono(-1, b=1, g=1),
        mono(b=1, i=1), mono(c=1, g=1), mono(-1, c=1, h=1),
    )
    assert normal["u"] == scale(multiply(multiply(h, d_minus_f), determinant), -1)
    assert normal["v"] == scale(multiply(multiply(h, linear_minor), s_factor), -1)

    q = add(
        mono(a=2, e=1, i=1), mono(-1, a=1, b=1, d=1, i=1),
        mono(-1, a=1, c=1, e=1, g=1), mono(-1, a=1, c=1, e=1, i=1),
        mono(b=1, c=1, d=1, g=1), mono(b=1, c=1, d=1, i=1),
        mono(-1, b=1, c=1, f=1, g=1), mono(c=2, e=1, g=1),
    )
    quotient_l = add(
        mono(-1, a=1, f=1, h=1), mono(-1, b=1, d=1, i=1),
        mono(b=1, e=1, i=1), mono(b=1, f=1, g=1), mono(c=1, d=1, h=1),
    )
    normal_w_identity = add(multiply(quotient_l, linear_minor), multiply(mono(e=1), q))
    assert normal["w"] == normal_w_identity

    tangent_derivatives = {name: derivative(deepest, name) for name in ORDER if name not in substitutions}
    for name, value in tangent_derivatives.items():
        delta_h = mono() if name == "h" else {}
        rhs = add(
            scale(multiply(multiply(delta_h, linear_minor), determinant), -1),
            scale(multiply(multiply(h, derivative(linear_minor, name)), determinant), -1),
            scale(multiply(multiply(h, linear_minor), derivative(determinant, name)), -1),
        )
        assert value == rhs

    seed_h_l = {
        "branch_id": "B-UVW-01-h-L",
        "source_factor_branch": ["h", "a*f-c*d"],
        "equations": [poly_record("EQ-h", h), poly_record("EQ-L", linear_minor)],
        "stratum_singular_membership": "PROVED_BY_EXACT_PRODUCT_RULE_IDENTITY_IN_IDEAL_h_L",
        "ambient_normal_transfer": {
            "dF_du": "ZERO_MOD_h_L_BY_EXACT_FACTOR_h",
            "dF_dv": "ZERO_MOD_h_L_BY_EXACT_FACTOR_h_L",
            "dF_dw_remainder": poly_record("REM-Nw-mod-h-L", multiply(mono(e=1), q)),
            "dF_dw_quotient_by_L": poly_record("QUO-Nw-by-L", quotient_l),
            "identity": "dF_dw = (QUO-Nw-by-L)*L + e*Q",
        },
        "ambient_cover_identity": "V(h,L,e*Q)=V(h,L,e) union V(h,L,Q)",
        "ambient_children": [
            {
                "branch_id": "B-UVW-01a-h-L-e",
                "equations": ["h", "a*f-c*d", "e"],
                "ambient_singular_membership": "PROVED_BY_EXACT_NORMAL_REMAINDER_IDENTITY",
                "projective_infinity_only": True,
                "affine_pullback": "EMPTY_BECAUSE_u=v=w=0_IS_DISJOINT_FROM_u=v=w=1",
                "parent_factor_tests_required": 0,
                "parent_exclusion": ["H_08_1248", "H_22_1367"],
                "dimension": 3,
                "dimension_certificate": "IN_P2xP2xP2: h=e=0 LEAVES_P2xP1xP1_AND_NONZERO_BIDEGREE_(1,1)_EQUATION_L_HAS_PURE_CODIMENSION_ONE",
                "degree": None,
                "multiplicity": None,
                "invariant_nonclaims": ["NO_DEGREE_ASSERTION", "NO_SCHEME_MULTIPLICITY_ASSERTION"],
                "status": "COMPLETED_PROJECTIVE_INFINITY_AND_STRICT_PARENT_EXCLUSION",
            },
            {
                "branch_id": "B-UVW-01b-h-L-Q",
                "equations": ["h", "a*f-c*d", "Q"],
                "Q": poly_record("EQ-Q", q),
                "ambient_singular_membership": "PROVED_BY_EXACT_NORMAL_REMAINDER_IDENTITY",
                "projective_infinity_only": True,
                "affine_pullback": "EMPTY_BECAUSE_u=v=w=0_IS_DISJOINT_FROM_u=v=w=1",
                "parent_factor_tests_required": 0,
                "parent_exclusion": ["H_08_1248", "H_22_1367"],
                "dimension": None,
                "degree": None,
                "multiplicity": None,
                "status": "COMPLETED_PROJECTIVE_INFINITY_AND_STRICT_PARENT_EXCLUSION;NO_COMPONENT_INVARIANTS_ASSERTED",
            },
        ],
        "strict_parent_exclusion": {
            "status": "PROVED",
            "parent_factor_node_ids": ["H_08_1248", "H_22_1367"],
            "reason": "EVERY_POINT_ON_THIS_BRANCH_HAS_h=L=0",
        },
    }
    for child in seed_h_l["ambient_children"]:
        child["semantic_sha256"] = semantic(child)
    seed_h_l["semantic_sha256"] = semantic(seed_h_l)

    other_seeds = [
        {
            "branch_id": "B-UVW-02-h-C",
            "equations": ["h", "C"],
            "stratum_singular_membership": "PROVED_BY_EXACT_PRODUCT_RULE_IDENTITY",
        },
        {
            "branch_id": "B-UVW-03-L-C",
            "equations": ["a*f-c*d", "C"],
            "stratum_singular_membership": "PROVED_BY_EXACT_PRODUCT_RULE_IDENTITY",
        },
        {
            "branch_id": "B-UVW-04-SingL",
            "equations": ["a", "c", "d", "f"],
            "stratum_singular_membership": "PROVED_FROM_EXACT_GRADIENT_OF_L",
        },
        {
            "branch_id": "B-UVW-05-SingC",
            "equations": ["ALL_NINE_2x2_MINORS_OF_MATRIX_[[a,b,c],[d,e,f],[g,h,i]]"],
            "stratum_singular_membership": "PROVED_FROM_EXACT_GRADIENT_OF_DETERMINANT_C",
        },
    ]
    exclusions = {
        "B-UVW-02-h-C": ["H_08_1248", "H_34_1678"],
        "B-UVW-03-L-C": ["H_22_1367", "H_34_1678"],
        "B-UVW-04-SingL": ["H_22_1367"],
        "B-UVW-05-SingC": ["H_34_1678"],
    }
    for item in other_seeds:
        item.update(
            {
                "ambient_normal_transfer": "ANY_AMBIENT_SUBBRANCH_REMAINS_IN_THE_SOURCE_FACTOR_BRANCH",
                "projective_infinity_only_if_ambient": True,
                "affine_pullback_if_ambient": "EMPTY_BECAUSE_u=v=w=0_IS_DISJOINT_FROM_u=v=w=1",
                "strict_parent_exclusion": {
                    "status": "PROVED",
                    "parent_factor_node_ids": exclusions[item["branch_id"]],
                    "reason": "EXACT_CONTAINMENT_IN_A_PINNED_ZERO_PARENT_FACTOR",
                },
                "status": "COMPLETED_PROJECTIVE_INFINITY_AND_STRICT_PARENT_EXCLUSION",
            }
        )
        item["semantic_sha256"] = semantic(item)

    data = {
        "factorization": {
            "identity": "F|u=v=w=0=-h*L*C",
            "h": poly_record("FAC-h", h),
            "L": poly_record("FAC-L", linear_minor),
            "C": poly_record("FAC-C", determinant),
            "exact_sparse_identity": True,
            "factor_irreducibility_asserted": False,
            "scheme_multiplicity_asserted": False,
            "parent_factor_matches": parent_matches,
            "entire_deepest_source_excluded_from_strict_parent": True,
            "exclusion_cover_identity": "V(F|uvw)=V(H_08_1248) union V(H_22_1367) union V(H_34_1678)",
        },
        "stratum_singular_set_cover": {
            "identity": "Sing(h*L*C)=V(h,L) union V(h,C) union V(L,C) union Sing(L) union Sing(C)",
            "scope": "SET_THEORETIC_COVER_IN_CHARACTERISTIC_ZERO;_NO_PRIMARY_DECOMPOSITION_CLAIM",
            "seed_count": 5,
        },
        "processed_seed": seed_h_l,
        "queued_seed_branches": other_seeds,
        "completed_source_factor_seed_count": 5,
        "completed_ambient_child_count": 2,
        "type_classification": "COMPLETE_PROJECTIVE_INFINITY_AND_STRICT_PARENT_EXCLUSION",
    }
    return data, sum(len(value) for value in normal.values()) + len(deepest)


def build(elapsed_seconds: float | None = None) -> tuple[dict, dict, dict]:
    started = perf_counter()
    raw = PREDECESSOR.read_bytes()
    assert digest(raw) == PREDECESSOR_SHA256
    predecessor = json.loads(raw)
    assert predecessor["outcome"] == "pass"
    assert predecessor["endpoint"] == "HASH_PIN_ALL_COMPLETED_CHART_BRANCHES_AND_FIRST_PENDING_BRANCH"
    assert predecessor["theorem_ledger"] == "2/9"
    source_record = predecessor["trihomogeneous_source"]["polynomial"]
    assert tuple(source_record["coordinate_order"]) == ORDER
    source = sparse(source_record["sparse_polynomial"])
    assert len(source) == 108
    assert all(sum(m[0:4]) == sum(m[4:8]) == sum(m[8:12]) == 2 for m in source)

    type_records = []
    operation_nodes = 108
    deepest_poly: Poly | None = None
    for position, (zero_variables, expected_terms) in enumerate(zip(TYPES, EXPECTED_TERMS)):
        restricted = restrict(source, zero_variables)
        assert len(restricted) == expected_terms
        if position == 0:
            deepest_poly = restricted
        tangent_variables = tuple(name for name in ORDER if name not in zero_variables)
        ambient_derivatives = {name: restrict(derivative(source, name), zero_variables) for name in ORDER}
        stratum_derivatives = {name: derivative(restricted, name) for name in tangent_variables}
        assert all(stratum_derivatives[name] == ambient_derivatives[name] for name in tangent_variables)
        incidences = []
        for chart in predecessor["chart_atlas"]["charts"]:
            for stratum in chart["boundary_strata"]:
                if tuple(stratum["zero_homogenizers"]) == zero_variables:
                    incidences.append(
                        {
                            "chart_index": chart["chart_index"],
                            "chart_id": chart["chart_id"],
                            "pivots": chart["pivots"],
                            "zero_homogenizers": stratum["zero_homogenizers"],
                            "stratum_tag": stratum["stratum_tag"],
                            "source_stratum_semantic_sha256": semantic(stratum),
                        }
                    )
        expected_incidences = 3 ** len(zero_variables) * 4 ** (3 - len(zero_variables))
        assert len(incidences) == expected_incidences

        factorization_status = "NO_NONTRIVIAL_FACTOR_IDENTITY_ASSERTED"
        factor_records: list[dict] = []
        if zero_variables == ("u", "v", "w"):
            factorization_status = "EXACT_FACTOR_IDENTITY_MINUS_h_TIMES_L_TIMES_C"
        elif zero_variables == ("u", "w"):
            h = mono(h=1)
            l_factor = add(mono(a=1, f=1), mono(-1, c=1, d=1))
            # Build the third factor by exact division of -restricted by h*L.
            # Its explicit formula is C + v*(a*h-a*i-b*g+b*i+c*g-c*h).
            c0 = add(
                mono(a=1, e=1, i=1), mono(-1, a=1, f=1, h=1), mono(-1, b=1, d=1, i=1),
                mono(b=1, f=1, g=1), mono(c=1, d=1, h=1), mono(-1, c=1, e=1, g=1),
                mono(a=1, h=1, v=1), mono(-1, a=1, i=1, v=1), mono(-1, b=1, g=1, v=1),
                mono(b=1, i=1, v=1), mono(c=1, g=1, v=1), mono(-1, c=1, h=1, v=1),
            )
            assert restricted == scale(multiply(multiply(h, l_factor), c0), -1)
            factorization_status = "EXACT_FACTOR_IDENTITY_MINUS_h_TIMES_L_TIMES_Cv"
            factor_records = [poly_record("FAC-UW-h", h), poly_record("FAC-UW-L", l_factor), poly_record("FAC-UW-Cv", c0)]
        elif zero_variables == ("v", "w"):
            h = mono(h=1)
            lu = add(mono(a=1, f=1), mono(-1, c=1, d=1), mono(d=1, u=1), mono(-1, f=1, u=1))
            c0 = add(
                mono(a=1, e=1, i=1), mono(-1, a=1, f=1, h=1), mono(-1, b=1, d=1, i=1),
                mono(b=1, f=1, g=1), mono(c=1, d=1, h=1), mono(-1, c=1, e=1, g=1),
            )
            assert restricted == scale(multiply(multiply(h, lu), c0), -1)
            factorization_status = "EXACT_FACTOR_IDENTITY_MINUS_h_TIMES_Lu_TIMES_C"
            factor_records = [poly_record("FAC-VW-h", h), poly_record("FAC-VW-Lu", lu), poly_record("FAC-VW-C", c0)]
        elif zero_variables == ("w",):
            h = mono(h=1)
            quotient = scale(monomial_divide(restricted, "h"), -1)
            assert restricted == scale(multiply(h, quotient), -1)
            factorization_status = "EXACT_FACTOR_IDENTITY_MINUS_h_TIMES_Pw_WITH_NO_IRREDUCIBILITY_CLAIM"
            factor_records = [poly_record("FAC-W-h", h), poly_record("FAC-W-Pw", quotient)]

        record = {
            "type_index": position,
            "type_id": "_".join(zero_variables),
            "zero_homogenizers": list(zero_variables),
            "processing_status": "EXACT_SOURCE_AND_JACOBIAN_DATA_COMPLETE",
            "restricted_source": poly_record(f"R-{position}-{'-'.join(zero_variables)}", restricted),
            "ambient_singularity": {
                "definition": "RESTRICT_ALL_TWELVE_PARTIALS_OF_FULL_F_AFTER_DIFFERENTIATION",
                "derivative_count": 12,
                "restricted_derivatives": [
                    {"variable": name, "polynomial": poly_record(f"AD-{position}-{name}", ambient_derivatives[name])}
                    for name in ORDER
                ],
            },
            "stratum_singularity": {
                "definition": "DIFFERENTIATE_RESTRICTED_SOURCE_ONLY_IN_TANGENT_COORDINATES",
                "tangent_variables": list(tangent_variables),
                "derivative_count": len(tangent_variables),
                "derivatives": [
                    {"variable": name, "polynomial": poly_record(f"SD-{position}-{name}", stratum_derivatives[name])}
                    for name in tangent_variables
                ],
                "tangent_transfer_exact_sparse_equality": True,
                "normal_derivatives_are_not_stratum_generators": True,
            },
            "factorization_status": factorization_status,
            "factor_records": factor_records,
            "chart_incidence_count": len(incidences),
            "chart_incidences": incidences,
            "overlap_deduplication": {
                "representatives_quotiented": 0,
                "overlap_unit_certificates": [],
                "status": "NO_DEDUPLICATION_PERFORMED_OR_CLAIMED",
            },
            "branch_propagation_status": (
                "COMPLETE_STRICT_PARENT_EXCLUSION"
                if position == 0
                else "FIRST_PENDING_AMBIENT_BRANCH_DECOMPOSITION"
                if position == 1
                else "QUEUED_AFTER_FIRST_UNRESOLVED_u_v_BRANCH"
            ),
        }
        record["semantic_sha256"] = semantic(record)
        type_records.append(record)
        operation_nodes += 108 + 12 * 108 + len(restricted) * len(tangent_variables)

    assert deepest_poly is not None
    deepest, deep_nodes = make_deepest_data(
        source, deepest_poly, predecessor["parent_factor_incidence_frontier"]
    )
    operation_nodes += deep_nodes
    assert sum(item["chart_incidence_count"] for item in type_records) == 279
    uv_family_zeros = ("u", "v", "b", "c", "e", "f")
    uv_ambient = {
        item["variable"]: sparse(item["polynomial"]["sparse_polynomial"])
        for item in type_records[1]["ambient_singularity"]["restricted_derivatives"]
    }
    assert all(restrict(poly, uv_family_zeros) == {} for poly in uv_ambient.values())
    parent_h22 = predecessor["parent_factor_incidence_frontier"]["records"][22]
    assert restrict(lift_affine_parent(parent_h22), uv_family_zeros) == {}
    uv_known_branch = {
        "branch_id": "B-UV-00-linear-P3-family",
        "global_homogeneous_equations": ["u", "v", "b", "c", "e", "f"],
        "standard_chart_witness": {
            "pivots": ["a", "d", "w"],
            "pivot_values": {"a": 1, "d": 1, "w": 1},
            "free_parameters": ["g", "h", "i"],
            "fixed_zero_coordinates": ["u", "v", "b", "c", "e", "f"],
        },
        "ambient_singular_membership": "ALL_TWELVE_RESTRICTED_FULL_DERIVATIVES_SUBSTITUTE_TO_EXACT_ZERO",
        "positive_dimensional": True,
        "dimension": 3,
        "dimension_certificate": "FIRST_AND_SECOND_PROJECTIVE_BLOCKS_ARE_FIXED_POINTS;THIRD_BLOCK_IS_P3",
        "degree": 1,
        "degree_certificate": "LINEAR_P3_IN_THE_PRODUCT_PROJECTIVE_AMBIENT",
        "multiplicity": None,
        "multiplicity_nonclaim": "NO_SCHEME_MULTIPLICITY_ASSERTION",
        "strict_parent_exclusion": {
            "status": "PROVED",
            "parent_factor_node_id": "H_22_1367",
            "parent_record_semantic_sha256": parent_h22["semantic_sha256"],
            "relationship": "H_22_1367=c*d-a*f_SUBSTITUTES_TO_ZERO",
        },
        "affine_pullback": "NOT_ACCEPTED;STRICT_PARENT_EXCLUSION_PRECEDES_ANY_PARENT_INTERIOR_CLASSIFICATION",
        "status": "COMPLETED_EXACT_POSITIVE_DIMENSIONAL_STRICT_PARENT_EXCLUDED_BRANCH",
    }
    uv_known_branch["semantic_sha256"] = semantic(uv_known_branch)
    operation_nodes += sum(len(poly) for poly in uv_ambient.values())
    first_pending = {
        "branch_id": "B-UV-01-unclassified-ambient-components",
        "type_id": "u_v",
        "restricted_source_semantic_sha256": type_records[1]["restricted_source"]["semantic_sha256"],
        "ambient_equation_node_ids": [
            item["polynomial"]["node_id"]
            for item in type_records[1]["ambient_singularity"]["restricted_derivatives"]
        ],
        "ambient_equation_count": 12,
        "stratum_equation_count": 10,
        "factorization_status": "NO_NONTRIVIAL_FACTOR_IDENTITY_ASSERTED",
        "completed_known_branch_semantic_sha256": uv_known_branch["semantic_sha256"],
        "known_branch_exhausts_ambient_ideal": False,
        "unresolved_obligations": [
            "CHARACTERISTIC_ZERO_AMBIENT_COMPONENT_CENSUS",
            "AMBIENT_COMPONENT_CLOSURE_VERSUS_STRATUM_ONLY_BRANCH",
            "EXPLICIT_OVERLAP_UNIT_DEDUPLICATION_IF_ANY",
            "EXACT_AFFINE_PULLBACK_BEFORE_PARENT_TESTS",
            "ALL_70_PARENT_FACTOR_TESTS_FOR_ANY_ACCEPTED_AFFINE_PULLBACK",
        ],
        "status": "FIRST_SOURCE_PINNED_UNRESOLVED_BRANCH_FAIL_CLOSED",
    }
    first_pending["semantic_sha256"] = semantic(first_pending)

    frontier = {
        "format": "d9-factor19069-homogenizer-boundary-type-constructor-frontier-v1",
        "cycle_id": CYCLE_ID,
        "track_id": TRACK_ID,
        "base_revision": BASE,
        "base_tree": BASE_TREE,
        "opening_revision": OPENING,
        "opening_tree": OPENING_TREE,
        "outcome": "pass",
        "classification": "DEEPEST_TYPE_EXCLUDED_BY_PINNED_PARENT_FACTORS_THEN_FIRST_u_v_BRANCH_UNRESOLVED_FAIL_CLOSED",
        "endpoint": "FIRST_SOURCE_PINNED_UNRESOLVED_TYPE_OR_BRANCH_CLASSIFICATION",
        "theorem_ledger": "2/9",
        "ledger_change_recommended": "none",
        "source_binding": {
            "predecessor_frontier_sha256": PREDECESSOR_SHA256,
            "predecessor_frontier_semantic_sha256": predecessor["semantic_sha256"],
            "source_semantic_sha256": source_record["semantic_sha256"],
            "term_count": len(source),
            "ring": "Q[a,b,c,u,d,e,f,v,g,h,i,w]",
            "multidegree": [2, 2, 2],
            "reconstructed_from_pinned_source": True,
        },
        "boundary_type_order": ["_".join(item) for item in TYPES],
        "boundary_type_count": len(type_records),
        "boundary_type_records": type_records,
        "boundary_stratum_chart_incidence_count": 279,
        "deepest_branch_frontier": deepest,
        "u_v_branch_frontier": {
            "completed_known_branches": [uv_known_branch],
            "completed_known_branch_count": 1,
            "component_completeness_proved": False,
            "first_pending_branch_id": first_pending["branch_id"],
            "first_pending_branch_semantic_sha256": first_pending["semantic_sha256"],
        },
        "first_pending_branch": first_pending,
        "parent_factor_frontier": {
            "ordered_parent_factor_count": predecessor["parent_factor_incidence_frontier"]["ordered_factor_count"],
            "source_semantic_sha256": predecessor["parent_factor_incidence_frontier"]["semantic_sha256"],
            "accepted_affine_branch_count": 0,
            "completed_branch_parent_factor_pairs": 0,
            "policy": "PULLBACK_TO_AFFINE_SINGULAR_IDEAL_BEFORE_ALL_70_PARENT_TESTS",
            "status": "NO_AFFINE_BRANCH_ACCEPTED;PROJECTIVE_ONLY_CHILD_REQUIRES_ZERO_PARENT_TESTS;FIRST_PENDING_PRESERVED_FAIL_CLOSED",
        },
        "overlap_accounting": {
            "inherited_directed_overlap_records": predecessor["chart_atlas"]["directed_overlap_record_count"],
            "representatives_quotiented": 0,
            "explicit_overlap_unit_certificates": 0,
            "unsupported_deduplications": 0,
        },
        "endpoint_accounting": {
            "positive": "NOT_REACHED;COMPLETE_SEVEN_TYPE_BRANCH_CLASSIFICATION_NOT_PROVED",
            "negative": "NOT_REACHED;NO_EXACT_STRICT_REAL_AFFINE_SURVIVOR",
            "null": "REACHED;FIRST_SOURCE_PINNED_UNRESOLVED_u_v_AMBIENT_BRANCH",
            "timeout": "NOT_REACHED;NO_RESOURCE_CEILING_HIT",
            "completed_boundary_types": 1,
            "completed_deepest_source_factor_seeds": 5,
            "completed_u_v_known_branches": 1,
            "first_pending_branch_id": first_pending["branch_id"],
            "first_pending_branch_semantic_sha256": first_pending["semantic_sha256"],
        },
        "resource_accounting": {
            "constructor_wall_seconds_ceiling": 4200,
            "exact_algebra_branch_node_ceiling": 350000,
            "exact_algebra_branch_nodes": operation_nodes,
            "node_definition": "SPARSE_MONOMIAL_VISITS_IN_SOURCE_RESTRICTION_DERIVATIVE_AND_RECORDED_DEEPEST_IDENTITIES",
            "first_build_elapsed_seconds": elapsed_seconds,
            "elapsed_measurement_policy": "PINNED_FIRST_BUILD_PERF_COUNTER;EXCLUDED_FROM_SEMANTIC_HASH_AND_REUSED_BY_CHECK_MODE",
            "ceiling_hit": False,
            "network_or_connector_used": False,
            "numerical_or_modular_probe_used": False,
            "whole_atlas_groebner_retry_used": False,
            "sympy_used_by_deterministic_builder": False,
        },
        "nonconsequences": [
            "NO_COMPLETE_SEVEN_TYPE_BRANCH_CLASSIFICATION",
            "NO_COMPLETE_CHARACTERISTIC_ZERO_COMPONENT_CENSUS",
            "NO_UNSUPPORTED_RADICALITY_DEGREE_OR_MULTIPLICITY_CLAIM",
            "NO_OVERLAP_DEDUPLICATION",
            "NO_ACCEPTED_AFFINE_SINGULAR_BRANCH",
            "NO_70_PARENT_FACTOR_CENSUS_FOR_AN_AFFINE_BRANCH",
            "NO_STRICT_REAL_RESIDENCE_OR_CONNECTED_PARENT_TAG",
            "NO_THEOREM_LEVEL_COUNTEREXAMPLE",
            "NO_DIAGONAL_9_PROOF_OR_COUNTEREXAMPLE",
            "NO_9DVL_SCORE_CHANGE",
        ],
    }
    semantic_projection = deepcopy(frontier)
    semantic_projection.pop("semantic_sha256", None)
    semantic_projection["resource_accounting"].pop("first_build_elapsed_seconds", None)
    frontier["semantic_sha256"] = digest(canonical(semantic_projection))

    manifest = {
        "format": "d9-factor19069-homogenizer-boundary-type-constructor-source-manifest-v1",
        "cycle_id": CYCLE_ID,
        "track_id": TRACK_ID,
        "canonical_base_revision": BASE,
        "canonical_base_tree": BASE_TREE,
        "cycle_opening_revision": OPENING,
        "cycle_opening_tree": OPENING_TREE,
        "pins": {
            "ops/research-team/PROTOCOL.md": digest(git_bytes(BASE, "ops/research-team/PROTOCOL.md")),
            "ops/research-team/verify_cycle_protocol.py": digest(git_bytes(BASE, "ops/research-team/verify_cycle_protocol.py")),
            "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-homogenizer-boundary-type-stratification-gate1/CYCLE.md": digest(git_bytes(OPENING, "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-homogenizer-boundary-type-stratification-gate1/CYCLE.md")),
            "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-homogenizer-boundary-type-stratification-gate1/WORK_ORDERS.yaml": digest(git_bytes(OPENING, "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-homogenizer-boundary-type-stratification-gate1/WORK_ORDERS.yaml")),
            "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-homogenizer-boundary-type-stratification-gate1/OBLIGATION_GRAPH.json": digest(git_bytes(OPENING, "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-homogenizer-boundary-type-stratification-gate1/OBLIGATION_GRAPH.json")),
            "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-homogenizer-boundary-type-stratification-gate1/OPENING_AUDIT.json": digest(git_bytes(OPENING, "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-homogenizer-boundary-type-stratification-gate1/OPENING_AUDIT.json")),
            "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-constructor/PROJECTIVE_CHART_FRONTIER.json": PREDECESSOR_SHA256,
            "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-constructor/SOURCE_MANIFEST.json": "9d4c69493f1ebb0a7a3e1f1bf8832ab56bace65a9841c4700af713322bd4658c",
            "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-certificate/RESULT.json": "ab9e4aa1591e425b210b98442ae22803b99a8974311022088561c1ac708ec375",
            "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-falsifier/RESULT.json": "12ac0d8da67d58720b5ff6f06d30760de8fc78382ff5a856e4976351af94cb57",
            "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-referee/RESULT.json": "e4088338d86d05442fe72289211500be187e6b99acd02c37a4fead51a07edc0f",
            "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin": "adb2e7257457f158e809450683c46fe7ecafdbdd4a7efdf9ac630e8a4f0fb03f",
            "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json": "956fbe7e5c7b1e04c8873ed9c0f3de9cb5420e3e06f1d5fae4c60f4e0571b364",
            "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json": "cc279d125605b45d25a3a01f462ad051038102f2bf12574f494a9d261bfc7401",
            "ai/omreal/data/DIAG9_GRAPH_row2599_factor_states.npz": "f44b1fccfb4e61273aeceb8796a18098d82c48473e257556ce3d2a22f99b0bcf",
            "ai/omreal/certs_4_8.jsonl": "c55e805d60d8086bcb84a312f2103a9973fc2691d0fd97f3d9a1d9809d2b163b",
        },
        "source_policy": {
            "predecessor_json_is_only_polynomial_source": True,
            "all_seven_boundary_types_reconstructed": True,
            "restrict_then_differentiate_semantics": True,
            "ambient_normal_derivatives_retained_separately": True,
            "whole_atlas_groebner_retry_used": False,
            "numerical_or_modular_probe_used": False,
            "network_or_connector_used": False,
            "unsupported_overlap_quotient_used": False,
        },
    }
    manifest["semantic_sha256"] = semantic(manifest)

    result = {
        "format": "d9-factor19069-homogenizer-boundary-type-constructor-result-v1",
        "cycle_id": CYCLE_ID,
        "track_id": TRACK_ID,
        "opening_revision": OPENING,
        "opening_tree": OPENING_TREE,
        "outcome": "pass",
        "classification": frontier["classification"],
        "endpoint": frontier["endpoint"],
        "theorem_ledger": "2/9",
        "ledger_change_recommended": "none",
        "source_manifest_semantic_sha256": manifest["semantic_sha256"],
        "boundary_type_frontier_semantic_sha256": frontier["semantic_sha256"],
        "boundary_type_count": 7,
        "restricted_source_term_counts": list(EXPECTED_TERMS),
        "boundary_stratum_chart_incidence_count": 279,
        "deepest_restriction_factorization_proved": True,
        "ambient_stratum_derivative_distinction_preserved": True,
        "completed_boundary_types": 1,
        "completed_deepest_source_factor_seeds": 5,
        "completed_u_v_known_branches": 1,
        "first_pending_branch_id": first_pending["branch_id"],
        "first_pending_branch_semantic_sha256": first_pending["semantic_sha256"],
        "accepted_affine_branch_count": 0,
        "parent_factor_records_retained": 70,
        "completed_affine_branch_parent_factor_pairs": 0,
        "overlap_representatives_quotiented": 0,
        "exact_algebra_branch_nodes": operation_nodes,
        "nonconsequences": frontier["nonconsequences"],
    }
    return manifest, frontier, result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    arguments = parser.parse_args()
    elapsed = None
    if arguments.check and FRONTIER.exists():
        elapsed = json.loads(FRONTIER.read_text(encoding="utf-8"))["resource_accounting"]["first_build_elapsed_seconds"]
    started = perf_counter()
    manifest, frontier, result = build(elapsed)
    if elapsed is None:
        frontier["resource_accounting"]["first_build_elapsed_seconds"] = round(perf_counter() - started, 6)
    payloads = {MANIFEST: pretty(manifest), FRONTIER: pretty(frontier), RESULT: pretty(result)}
    if arguments.check:
        for path, payload in payloads.items():
            assert path.read_bytes() == payload, f"byte drift: {path.name}"
        print("PASS byte-exact homogenizer boundary constructor rebuild")
    else:
        HERE.mkdir(parents=True, exist_ok=True)
        for path, payload in payloads.items():
            path.write_bytes(payload)
        print("WROTE exact homogenizer boundary constructor frontier")
    print(
        f"types=7 terms={list(EXPECTED_TERMS)} incidences=279 nodes={result['exact_algebra_branch_nodes']} "
        f"pending={result['first_pending_branch_id']} ledger=2/9"
    )


if __name__ == "__main__":
    main()
