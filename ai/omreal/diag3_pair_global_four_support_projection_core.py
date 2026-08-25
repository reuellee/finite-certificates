#!/usr/bin/env python3
"""Exact cube/fiber projection preflight for the 22 four-support walls."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import diag3_pair_global_four_support_core as gate_core  # noqa: E402
from exact_semialgebraic import canonical_integer, multiply  # noqa: E402


FORMAT = "diag3-pair-global-row2599-four-support-projection-v1"
SOURCE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_GATE.json"
CUBE_FORMS = (
    {(1, 0, 0): Fraction(1), (0, 1, 0): Fraction(1), (1, 1, 0): Fraction(-1)},
    {(0, 1, 0): Fraction(1)},
    {(0, 0, 1): Fraction(1), (0, 1, 0): Fraction(1), (0, 1, 1): Fraction(-1)},
)
CUBE_FACETS = (
    ("u=0", {(1, 0, 0): 1}, 0, 1),
    ("u=1", {(0, 0, 0): 1, (1, 0, 0): -1}, 0, -1),
    ("t=0", {(0, 1, 0): 1}, 1, 1),
    ("t=1", {(0, 0, 0): 1, (0, 1, 0): -1}, 1, -1),
    ("v=0", {(0, 0, 1): 1}, 2, 1),
    ("v=1", {(0, 0, 0): 1, (0, 0, 1): -1}, 2, -1),
)
SQUARE_FACETS = (
    ("u=0", {(1, 0): 1}, 0, 1),
    ("u=1", {(0, 0): 1, (1, 0): -1}, 0, -1),
    ("t=0", {(0, 1): 1}, 1, 1),
    ("t=1", {(0, 0): 1, (0, 1): -1}, 1, -1),
)


def canonical(polynomial):
    return {exponent: coefficient for exponent, coefficient in canonical_integer(polynomial)}


def compose(polynomial):
    answer = Counter()
    for exponent, coefficient in polynomial.items():
        term = {(0, 0, 0): Fraction(coefficient)}
        for axis, power in enumerate(exponent):
            for _ in range(power):
                term = multiply(term, CUBE_FORMS[axis])
        answer.update(term)
    return {exponent: coefficient for exponent, coefficient in answer.items() if coefficient}


def divide_linear(polynomial, factor, axis, leading):
    dimension = len(next(iter(polynomial)))
    work = Counter({term: Fraction(value) for term, value in polynomial.items()})
    quotient = Counter()
    while work:
        candidates = [term for term in work if term[axis]]
        if not candidates:
            break
        term = max(candidates, key=lambda exponent: (exponent[axis], exponent))
        target = list(term)
        target[axis] -= 1
        target = tuple(target)
        coefficient = work[term] / leading
        quotient[target] += coefficient
        for exponent, value in factor.items():
            output = tuple(target[index] + exponent[index] for index in range(dimension))
            work[output] -= coefficient * value
            if not work[output]:
                del work[output]
    return dict(quotient), dict(work)


def reduce_boundary(polynomial, facets):
    if not polynomial:
        return {}, {}
    dimension = len(next(iter(polynomial)))
    minimum = tuple(min(exponent[axis] for exponent in polynomial) for axis in range(dimension))
    current = canonical({
        tuple(exponent[axis] - minimum[axis] for axis in range(dimension)): coefficient
        for exponent, coefficient in polynomial.items()
    })
    factors = Counter({facets[2 * axis][0]: minimum[axis] for axis in range(dimension) if minimum[axis]})
    changed = True
    while changed:
        changed = False
        for name, factor, axis, leading in facets:
            quotient, remainder = divide_linear(current, factor, axis, leading)
            if not remainder:
                current = canonical(quotient)
                factors[name] += 1
                changed = True
                break
    return current, dict(sorted(factors.items()))


def add(*terms):
    answer = Counter()
    for polynomial, scale in terms:
        for exponent, coefficient in polynomial.items():
            answer[exponent] += scale * coefficient
    return {exponent: coefficient for exponent, coefficient in answer.items() if coefficient}


def coefficients_in_v(polynomial):
    answer = {}
    for exponent, coefficient in polynomial.items():
        answer.setdefault(exponent[2], Counter())[(exponent[0], exponent[1])] += coefficient
    return {degree: dict(values) for degree, values in answer.items()}


def degree_census(polynomials):
    answer = Counter()
    for polynomial in polynomials:
        answer[tuple(max(exponent[axis] for exponent in polynomial) for axis in range(len(next(iter(polynomial)))))] += 1
    return {",".join(map(str, degree)): count for degree, count in sorted(answer.items())}


def build_record(*, include_catalog=False):
    source = json.loads(SOURCE.read_text())
    if source["format"] != gate_core.FORMAT or source["status"] != "PROVED":
        raise AssertionError("four-support source gate changed")
    if source["combined_compression"]["distinct_active_walls_after_positive_quotient"] != 22:
        raise AssertionError("active wall source count changed")

    transformed = {}
    cube_factor_census = Counter()
    for row in source["active_wall_catalog"]:
        polynomial = {
            tuple(term["exponent"]): Fraction(term["coefficient"])
            for term in row["polynomial"]
        }
        reduced, factors = reduce_boundary(compose(polynomial), CUBE_FACETS)
        cube_factor_census.update(factors)
        key = tuple(sorted(reduced.items()))
        transformed.setdefault(key, []).append(row["id"])
    if len(transformed) != 22:
        raise AssertionError("cube map identified two active walls")

    base_only = []
    linear = []
    quadratic = []
    catalog = []
    for index, (key, source_ids) in enumerate(sorted(transformed.items())):
        polynomial = dict(key)
        coefficients = coefficients_in_v(polynomial)
        degree = max(coefficients)
        (base_only if degree == 0 else linear if degree == 1 else quadratic if degree == 2 else []).append(coefficients)
        if degree not in (0, 1, 2):
            raise AssertionError("unexpected fiber degree")
        catalog.append({
            "id": index,
            "source_active_wall_ids": source_ids,
            "fiber_degree": degree,
            "polynomial": gate_core.polynomial_rows(polynomial),
        })
    if len(base_only) != 1 or len(linear) != 20 or len(quadratic) != 1:
        raise AssertionError("fiber degree census changed")

    projection_rows = []
    raw_kind_census = Counter()

    def append(kind, polynomial):
        reduced, _factors = reduce_boundary(polynomial, SQUARE_FACETS)
        if reduced:
            projection_rows.append((kind, tuple(sorted(reduced.items()))))
            raw_kind_census[kind] += 1

    for coefficients in base_only + linear + quadratic:
        for polynomial in coefficients.values():
            append("coefficient", polynomial)

    zero_resultants = 0
    for left in range(len(linear)):
        for right in range(left + 1, len(linear)):
            first_a, first_b = linear[left].get(1, {}), linear[left].get(0, {})
            second_a, second_b = linear[right].get(1, {}), linear[right].get(0, {})
            resultant = add(
                (multiply(first_a, second_b), 1),
                (multiply(second_a, first_b), -1),
            )
            if resultant:
                append("linear_linear_resultant", resultant)
            else:
                zero_resultants += 1

    quadratic_coefficients = quadratic[0]
    q0 = quadratic_coefficients.get(0, {})
    q1 = quadratic_coefficients.get(1, {})
    q2 = quadratic_coefficients.get(2, {})
    append("quadratic_discriminant", add((multiply(q1, q1), 1), (multiply(q2, q0), -4)))
    for coefficients in linear:
        a, b = coefficients.get(1, {}), coefficients.get(0, {})
        resultant = add(
            (multiply(q2, multiply(b, b)), 1),
            (multiply(q1, multiply(a, b)), -1),
            (multiply(q0, multiply(a, a)), 1),
        )
        if resultant:
            append("linear_quadratic_resultant", resultant)
        else:
            zero_resultants += 1

    unique = {key: dict(key) for _kind, key in projection_rows}
    projection_catalog = [
        {"id": index, "polynomial": gate_core.polynomial_rows(polynomial)}
        for index, (_key, polynomial) in enumerate(sorted(unique.items()))
    ]
    term_census = Counter(len(polynomial) for polynomial in unique.values())
    semantic = hashlib.sha256(
        b"diag3-four-support-projection-v1\0"
        + json.dumps(
            {"walls": catalog, "projection": projection_catalog},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest()

    record = {
        "format": FORMAT,
        "status": "PROVED",
        "scope": {
            "source_parent_domains": "BOTH_COVERED_SQUARE_PYRAMIDS",
            "cube_parameterization": "INTERIOR_BIJECTION_WITH_TOP_FACE_COLLAPSED_TO_APEX",
            "fiber_projection_family": "COMPLETE_FOR_THE_22_ACTIVE_WALL_POLYNOMIALS",
            "base_sign_invariant_cad": "NOT_YET_CONSTRUCTED",
            "global_parent_cell_coverage": "NOT_CLAIMED",
            "honest_9dvl_score": "2/9",
        },
        "source": {
            "format": source["format"],
            "active_wall_catalog_sha256": source["combined_compression"]["active_wall_catalog_sha256"],
            "active_wall_count": 22,
        },
        "cube_map": {
            "coordinates": ["u", "t", "v"],
            "forward": ["a=t+(1-t)u", "g=t", "h=t+(1-t)v"],
            "interior_inverse": ["u=(a-g)/(1-g)", "t=g", "v=(h-g)/(1-g)"],
            "boundary_factor_census": dict(sorted(cube_factor_census.items())),
            "distinct_transformed_walls": len(transformed),
            "transformed_wall_degree_census": degree_census(map(dict, transformed)),
        },
        "fiber_walls": {
            "independent_of_v": len(base_only),
            "linear_in_v": len(linear),
            "quadratic_in_v": len(quadratic),
            "higher_degree_in_v": 0,
            "catalog": catalog,
        },
        "projection": {
            "raw_nonzero_polynomial_count": len(projection_rows),
            "raw_kind_census": dict(sorted(raw_kind_census.items())),
            "identically_zero_pair_resultants": zero_resultants,
            "distinct_boundary_reduced_polynomial_count": len(unique),
            "degree_census_u_t": degree_census(unique.values()),
            "term_count_census": {str(terms): count for terms, count in sorted(term_census.items())},
            "catalog_sha256": hashlib.sha256(
                json.dumps(projection_catalog, sort_keys=True, separators=(",", ":")).encode("ascii")
            ).hexdigest(),
        },
        "semantic_sha256": semantic,
        "resource_effect": {
            "projection_polynomial_ceiling": source["resource_contract"]["maximum_unique_projection_polynomials"],
            "actual_distinct_projection_polynomials": len(unique),
            "ceiling_not_triggered": len(unique) < source["resource_contract"]["maximum_unique_projection_polynomials"],
            "next_stage": f"construct an exact sign-invariant CAD/roadmap for the {len(unique)} (u,t) projection polynomials, then lift the 22 degree-at-most-two v fibers",
        },
        "theorem_effect": "The 22-wall square-pyramid arrangement admits a bounded exact fiber architecture: one base-only wall, 20 v-linear walls, one v-quadratic wall, and a finite boundary-reduced base projection family; this passes the projection ceiling but does not yet construct the base CAD or global master complex; honest 9DVL score remains 2/9.",
    }
    if include_catalog:
        record["projection"]["catalog"] = projection_catalog
    return record
