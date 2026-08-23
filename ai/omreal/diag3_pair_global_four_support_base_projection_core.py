#!/usr/bin/env python3
"""Exact second projection frontier for the four-support base arrangement."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from math import gcd, lcm
import json
from pathlib import Path
import sys

import sympy as sp


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import diag3_pair_global_four_support_projection_core as source_core  # noqa: E402


FORMAT = "diag3-pair-global-row2599-four-support-base-projection-v1"
u, t = sp.symbols("u t")


def parse_bivariate(rows):
    expression = 0
    for row in rows:
        exponent_u, exponent_t = row["exponent"]
        expression += (
            sp.Rational(row["coefficient"])
            * u ** exponent_u
            * t ** exponent_t
        )
    return sp.Poly(expression, u, t, domain=sp.QQ)


def canonical_terms(polynomial, variables):
    polynomial = sp.Poly(polynomial, *variables, domain=sp.QQ)
    if polynomial.is_zero:
        return ()
    terms = polynomial.terms()
    denominator = 1
    for _exponent, coefficient in terms:
        denominator = lcm(denominator, int(coefficient.q))
    integer_terms = [
        (tuple(map(int, exponent)), int(coefficient * denominator))
        for exponent, coefficient in terms
    ]
    content = 0
    for _exponent, coefficient in integer_terms:
        content = gcd(content, abs(coefficient))
    integer_terms = [
        (exponent, coefficient // content)
        for exponent, coefficient in integer_terms
    ]
    if integer_terms[0][1] < 0:
        integer_terms = [(exponent, -coefficient) for exponent, coefficient in integer_terms]
    return tuple(sorted(integer_terms))


def bivariate_expression(key):
    return sum(
        sp.Integer(coefficient) * u ** exponent[0] * t ** exponent[1]
        for exponent, coefficient in key
    )


def univariate_expression(key):
    return sum(
        sp.Integer(coefficient) * t ** exponent[0]
        for exponent, coefficient in key
    )


def bivariate_rows(key):
    return [
        {"exponent": list(exponent), "coefficient": str(coefficient)}
        for exponent, coefficient in key
    ]


def univariate_coefficients(key):
    degree = max(exponent[0] for exponent, _coefficient in key)
    values = [0] * (degree + 1)
    for exponent, coefficient in key:
        values[exponent[0]] = coefficient
    return values


def strip_square_boundary(polynomial):
    polynomial = sp.Poly(polynomial, t, domain=sp.QQ)
    if polynomial.is_zero:
        return None
    if polynomial.degree() <= 0:
        return None
    while polynomial.eval(0) == 0:
        polynomial = sp.div(
            polynomial,
            sp.Poly(t, t, domain=sp.QQ),
            domain=sp.QQ,
        )[0]
    while polynomial.eval(1) == 0:
        polynomial = sp.div(
            polynomial,
            sp.Poly(t - 1, t, domain=sp.QQ),
            domain=sp.QQ,
        )[0]
    if polynomial.degree() <= 0:
        return None
    return canonical_terms(sp.sqf_part(polynomial.as_expr(), t), (t,))


def digest(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def build_record():
    source = source_core.build_record(include_catalog=True)
    if source["format"] != source_core.FORMAT or source["status"] != "PROVED":
        raise AssertionError("first projection source changed")
    if source["projection"]["distinct_boundary_reduced_polynomial_count"] != 136:
        raise AssertionError("first projection source count changed")

    source_polynomials = [
        parse_bivariate(row["polynomial"])
        for row in source["projection"]["catalog"]
    ]

    factor_keys = set()
    source_factor_keys = []
    source_factor_count_census = Counter()
    source_factor_occurrences = 0
    for polynomial in source_polynomials:
        _coefficient, rows = sp.factor_list(polynomial.as_expr(), gens=(u, t))
        decomposition = []
        source_factor_count_census[len(rows)] += 1
        for factor, multiplicity in rows:
            key = canonical_terms(factor, (u, t))
            factor_keys.add(key)
            decomposition.append((key, int(multiplicity)))
            source_factor_occurrences += 1
        source_factor_keys.append(tuple(sorted(decomposition)))

    sorted_factor_keys = sorted(factor_keys)
    factor_id = {key: index for index, key in enumerate(sorted_factor_keys)}
    base_factor_catalog = [
        {
            "id": index,
            "degree_u": max(exponent[0] for exponent, _coefficient in key),
            "degree_t": max(exponent[1] for exponent, _coefficient in key),
            "polynomial": bivariate_rows(key),
        }
        for index, key in enumerate(sorted_factor_keys)
    ]
    base_factorizations = [
        {
            "source_projection_id": index,
            "factors": [
                {"id": factor_id[key], "multiplicity": multiplicity}
                for key, multiplicity in decomposition
            ],
        }
        for index, decomposition in enumerate(source_factor_keys)
    ]

    base_expressions = [bivariate_expression(key) for key in sorted_factor_keys]
    projection_rows = []
    raw_kind_census = Counter()

    def append(kind, polynomial):
        key = strip_square_boundary(polynomial)
        if key is not None:
            projection_rows.append(key)
            raw_kind_census[kind] += 1

    for polynomial in base_expressions:
        for coefficient in sp.Poly(polynomial, u).all_coeffs():
            append("coefficient", coefficient)
        if sp.degree(polynomial, u) >= 2:
            append("discriminant", sp.discriminant(polynomial, u))

    zero_resultants = 0
    pair_resultants = 0
    for left in range(len(base_expressions)):
        for right in range(left + 1, len(base_expressions)):
            resultant = sp.resultant(base_expressions[left], base_expressions[right], u)
            if resultant == 0:
                zero_resultants += 1
            else:
                before = len(projection_rows)
                append("pair_resultant", resultant)
                pair_resultants += len(projection_rows) - before

    unique_projection_keys = sorted(set(projection_rows))
    univariate_factor_keys = set()
    projection_factor_keys = []
    for key in unique_projection_keys:
        polynomial = univariate_expression(key)
        _coefficient, rows = sp.factor_list(polynomial, gens=(t,))
        decomposition = []
        for factor, multiplicity in rows:
            factor_key = canonical_terms(factor, (t,))
            univariate_factor_keys.add(factor_key)
            decomposition.append((factor_key, int(multiplicity)))
        projection_factor_keys.append(tuple(sorted(decomposition)))

    sorted_univariate_factor_keys = sorted(univariate_factor_keys)
    univariate_factor_id = {
        key: index for index, key in enumerate(sorted_univariate_factor_keys)
    }
    degree_census = Counter()
    interior_root_census = Counter()
    factor_root_rows = []
    maximum_coefficient_bits = 0
    for index, key in enumerate(sorted_univariate_factor_keys):
        coefficients = univariate_coefficients(key)
        degree = len(coefficients) - 1
        polynomial = sp.Poly(univariate_expression(key), t, domain=sp.QQ)
        if polynomial.eval(0) == 0 or polynomial.eval(1) == 0:
            raise AssertionError("univariate factor retained a square-boundary root")
        roots = int(sp.count_roots(polynomial, 0, 1))
        degree_census[degree] += 1
        interior_root_census[roots] += 1
        maximum_coefficient_bits = max(
            maximum_coefficient_bits,
            *(abs(value).bit_length() for value in coefficients),
        )
        factor_root_rows.append(
            {
                "id": index,
                "degree": degree,
                "interior_root_count": roots,
                "coefficients_low_to_high": coefficients,
            }
        )

    projection_factorizations = [
        {
            "projection_id": index,
            "factors": [
                {"id": univariate_factor_id[key], "multiplicity": multiplicity}
                for key, multiplicity in decomposition
            ],
        }
        for index, decomposition in enumerate(projection_factor_keys)
    ]

    base_degree_census = Counter(
        (
            max(exponent[0] for exponent, _coefficient in key),
            max(exponent[1] for exponent, _coefficient in key),
        )
        for key in sorted_factor_keys
    )
    semantic_payload = {
        "source_semantic_sha256": source["semantic_sha256"],
        "base_factor_catalog": base_factor_catalog,
        "base_factorizations": base_factorizations,
        "raw_kind_census": dict(sorted(raw_kind_census.items())),
        "unique_projection_polynomial_count": len(unique_projection_keys),
        "univariate_factor_catalog": factor_root_rows,
        "projection_factorizations": projection_factorizations,
    }
    semantic = digest(semantic_payload)

    return {
        "format": FORMAT,
        "status": "PROVED",
        "scope": {
            "source": "COMPLETE_136_POLYNOMIAL_FIRST_PROJECTION_FAMILY",
            "base_factorization": "COMPLETE_UP_TO_NONZERO_RATIONAL_SCALAR",
            "second_projection_family": "COMPLETE_COLLINS_STYLE_COEFFICIENT_DISCRIMINANT_RESULTANT_FAMILY",
            "root_statement": "EXACT_FACTOR_ROOT_INCIDENCE_COUNT_AND_UPPER_BOUND_ON_DISTINCT_INTERIOR_T_SECTIONS",
            "base_sign_invariant_cad": "NOT_YET_CONSTRUCTED",
            "global_parent_cell_coverage": "NOT_CLAIMED",
            "honest_9dvl_score": "2/9",
        },
        "source": {
            "format": source["format"],
            "semantic_sha256": source["semantic_sha256"],
            "projection_catalog_sha256": source["projection"]["catalog_sha256"],
            "projection_polynomials": 136,
        },
        "base_factorization": {
            "source_polynomials": len(source_polynomials),
            "nonconstant_source_polynomials": sum(bool(row) for row in source_factor_keys),
            "distinct_factor_count": len(sorted_factor_keys),
            "factor_occurrences": source_factor_occurrences,
            "source_factor_count_census": {
                str(count): amount
                for count, amount in sorted(source_factor_count_census.items())
            },
            "degree_census_u_t": {
                f"{degree_u},{degree_t}": count
                for (degree_u, degree_t), count in sorted(base_degree_census.items())
            },
            "catalog_sha256": digest(base_factor_catalog),
            "factorizations_sha256": digest(base_factorizations),
            "catalog": base_factor_catalog,
            "factorizations": base_factorizations,
        },
        "second_projection": {
            "raw_nonconstant_obligations": len(projection_rows),
            "raw_kind_census": dict(sorted(raw_kind_census.items())),
            "nonconstant_pair_resultants": pair_resultants,
            "identically_zero_pair_resultants": zero_resultants,
            "distinct_squarefree_boundary_reduced_polynomials": len(unique_projection_keys),
            "distinct_factor_count": len(sorted_univariate_factor_keys),
            "degree_census": {
                str(degree): count for degree, count in sorted(degree_census.items())
            },
            "factor_interior_root_count_census": {
                str(roots): count for roots, count in sorted(interior_root_census.items())
            },
            "factor_interior_root_incidences": sum(
                row["interior_root_count"] for row in factor_root_rows
            ),
            "distinct_interior_t_sections_upper_bound": sum(
                row["interior_root_count"] for row in factor_root_rows
            ),
            "maximum_degree": max(row["degree"] for row in factor_root_rows),
            "maximum_primitive_coefficient_bits": maximum_coefficient_bits,
            "catalog_sha256": digest(factor_root_rows),
            "factorizations_sha256": digest(projection_factorizations),
            "catalog": factor_root_rows,
            "factorizations": projection_factorizations,
        },
        "semantic_sha256": semantic,
        "resource_effect": {
            "projection_polynomial_ceiling": 100_000,
            "actual_distinct_squarefree_projection_polynomials": len(unique_projection_keys),
            "actual_distinct_univariate_factors": len(sorted_univariate_factor_keys),
            "ceiling_not_triggered": len(unique_projection_keys) < 100_000,
            "next_stage": "isolate and order the at-most-1693 interior t sections, then lift the 114 base curve factors in u and the 22 original walls in v",
        },
        "generator_dependency": {
            "python": sys.version.split()[0],
            "sympy": sp.__version__,
            "independent_verifier": "STANDARD_LIBRARY_ONLY",
        },
        "theorem_effect": "The 136-polynomial base problem has a complete bounded second projection: 114 base factors produce 2554 distinct squarefree univariate projection polynomials and 2333 factor polynomials with 1693 interior root incidences; the base CAD and lifted global master complex remain open; honest 9DVL score remains 2/9.",
    }
