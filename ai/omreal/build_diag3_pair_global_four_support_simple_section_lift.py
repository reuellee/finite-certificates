#!/usr/bin/env python3
"""Build exact lifts for the simple-crossing four-support t sections."""

from __future__ import annotations

from collections import Counter, defaultdict
import gzip
from hashlib import sha256
import json
from math import gcd, lcm
from pathlib import Path
import sys

import sympy as sp


HERE = Path(__file__).resolve().parent
BASE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz"
ROOTS = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ROOT_ISOLATION.json.gz"
OPEN = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT.json"
OUTPUT = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_SIMPLE_SECTION_LIFT.json"
FORMAT = "diag3-pair-global-row2599-four-support-simple-section-lift-v1"
u, t = sp.symbols("u t")


def digest(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def primitive_coefficients(polynomial):
    polynomial = sp.Poly(polynomial, t, domain=sp.QQ)
    coefficients = list(reversed(polynomial.all_coeffs()))
    denominator = 1
    for value in coefficients:
        denominator = lcm(denominator, int(value.q))
    integers = [int(value * denominator) for value in coefficients]
    content = 0
    for value in integers:
        content = gcd(content, abs(value))
    integers = [value // content for value in integers]
    if integers[-1] < 0:
        integers = [-value for value in integers]
    return tuple(integers)


def strip_t_boundary_squarefree(polynomial):
    polynomial = sp.Poly(polynomial, t, domain=sp.QQ)
    if polynomial.is_zero or polynomial.degree() <= 0:
        return None
    while polynomial.eval(0) == 0:
        polynomial = sp.div(polynomial, sp.Poly(t, t, domain=sp.QQ))[0]
    while polynomial.eval(1) == 0:
        polynomial = sp.div(polynomial, sp.Poly(t - 1, t, domain=sp.QQ))[0]
    if polynomial.degree() <= 0:
        return None
    return sp.Poly(sp.sqf_part(polynomial.as_expr(), t), t, domain=sp.QQ)


def strip_t_boundary(polynomial):
    polynomial = sp.Poly(polynomial, t, domain=sp.QQ)
    if polynomial.is_zero or polynomial.degree() <= 0:
        return None
    while polynomial.eval(0) == 0:
        polynomial = sp.div(polynomial, sp.Poly(t, t, domain=sp.QQ))[0]
    while polynomial.eval(1) == 0:
        polynomial = sp.div(polynomial, sp.Poly(t - 1, t, domain=sp.QQ))[0]
    return polynomial


def factor_ids(polynomial, catalog):
    polynomial = strip_t_boundary_squarefree(polynomial)
    if polynomial is None:
        return []
    _scalar, factors = sp.factor_list(polynomial.as_expr(), gens=(t,))
    answer = []
    for factor, multiplicity in factors:
        key = primitive_coefficients(factor)
        if key not in catalog:
            raise AssertionError("projection factor missing from source catalog")
        answer.append((catalog[key], int(multiplicity)))
    return answer


def load_sector_sequences(manifest):
    sectors = []
    for row in manifest["artifact_shards"]["shards"]:
        compressed = (OPEN.parent / row["path"]).read_bytes()
        if len(compressed) != row["bytes"] or sha256(compressed).hexdigest() != row["sha256"]:
            raise AssertionError("open-sector shard changed")
        shard = json.loads(gzip.decompress(compressed))
        if shard["sector_start"] != len(sectors):
            raise AssertionError("open-sector shard coverage changed")
        sectors.extend(shard["sectors"])
    return [[entry[0] for entry in sector] for sector in sectors]


def transition_window(left, right):
    prefix = 0
    while prefix < min(len(left), len(right)) and left[prefix] == right[prefix]:
        prefix += 1
    suffix = 0
    while (
        suffix < min(len(left) - prefix, len(right) - prefix)
        and left[-1 - suffix] == right[-1 - suffix]
    ):
        suffix += 1
    left_window = left[prefix : len(left) - suffix if suffix else len(left)]
    right_window = right[prefix : len(right) - suffix if suffix else len(right)]
    return prefix, left_window, right_window


def main():
    base = json.loads(gzip.decompress(BASE.read_bytes()))
    roots = json.loads(gzip.decompress(ROOTS.read_bytes()))
    open_lift = json.loads(OPEN.read_bytes())
    if roots["source"]["semantic_sha256"] != base["semantic_sha256"]:
        raise AssertionError("root source changed")
    if open_lift["source"]["root_isolation_semantic_sha256"] != roots["semantic_sha256"]:
        raise AssertionError("open-sector source changed")

    base_polynomials = [
        sum(
            sp.Integer(term["coefficient"])
            * u ** term["exponent"][0]
            * t ** term["exponent"][1]
            for term in row["polynomial"]
        )
        for row in base["base_factorization"]["catalog"]
    ]
    projection_catalog = {
        tuple(row["coefficients_low_to_high"]): row["id"]
        for row in base["second_projection"]["catalog"]
    }
    projection_polynomials = {
        row["id"]: sp.Poly(
            sum(
                sp.Integer(coefficient) * t**degree
                for degree, coefficient in enumerate(
                    row["coefficients_low_to_high"]
                )
            ),
            t,
            domain=sp.QQ,
        )
        for row in base["second_projection"]["catalog"]
    }

    exceptional_kinds = defaultdict(set)
    for base_id, polynomial in enumerate(base_polynomials):
        coefficients = list(reversed(sp.Poly(polynomial, u).all_coeffs()))
        for coefficient in coefficients:
            for factor_id, _multiplicity in factor_ids(coefficient, projection_catalog):
                exceptional_kinds[factor_id].add("coefficient")
        if sp.degree(polynomial, u) >= 2:
            for factor_id, _multiplicity in factor_ids(
                sp.discriminant(polynomial, u), projection_catalog
            ):
                exceptional_kinds[factor_id].add("discriminant")
    for row in open_lift["bounded_u_boundary_audit"]["factorizations"]:
        for factor in row["factors"]:
            exceptional_kinds[factor["id"]].add("u1_boundary")

    sequences = load_sector_sequences(open_lift)
    section_rows = roots["root_isolation"]["sections"]
    crossings = []
    remaining_census = Counter()
    total_section_root_points = 0
    total_section_strips = 0
    resultant_cache = {}
    for section_id, (section, left, right) in enumerate(
        zip(section_rows, sequences[:-1], sequences[1:], strict=True)
    ):
        position, left_window, right_window = transition_window(left, right)
        simple = (
            len(left_window) == len(right_window) == 2
            and left_window == list(reversed(right_window))
            and left_window[0] != left_window[1]
        )
        if not simple:
            if left == right:
                remaining_census["no_visible_stack_change"] += 1
            elif len(left) == len(right):
                remaining_census["complex_same_count_transition"] += 1
            else:
                remaining_census["root_count_change"] += 1
            continue

        pair = tuple(sorted(left_window))
        if pair not in resultant_cache:
            resultant_cache[pair] = strip_t_boundary(
                sp.resultant(
                    base_polynomials[pair[0]], base_polynomials[pair[1]], u
                )
            )
        projection_factor_id = section["factor_id"]
        quotient = resultant_cache[pair]
        projection_factor = projection_polynomials[projection_factor_id]
        multiplicity = 0
        while True:
            next_quotient, remainder = sp.div(quotient, projection_factor)
            if not remainder.is_zero:
                break
            quotient = next_quotient
            multiplicity += 1
        if multiplicity != 1:
            raise AssertionError("swapped-pair resultant is not simple")
        if exceptional_kinds[projection_factor_id]:
            raise AssertionError("simple crossing has a nonresultant event")
        root_count = len(left)
        section_root_points = root_count - 1
        section_strips = root_count
        total_section_root_points += section_root_points
        total_section_strips += section_strips
        crossings.append(
            [
                section_id,
                projection_factor_id,
                section["factor_root_index"],
                position,
                left_window[0],
                left_window[1],
                root_count,
            ]
        )

    if len(crossings) != 1_022:
        raise AssertionError("simple-crossing count changed")
    semantic_payload = {
        "base_projection_semantic_sha256": base["semantic_sha256"],
        "root_isolation_semantic_sha256": roots["semantic_sha256"],
        "open_sector_lift_semantic_sha256": open_lift["semantic_sha256"],
        "crossings": crossings,
    }
    record = {
        "format": FORMAT,
        "status": "PROVED",
        "scope": {
            "simple_transversal_algebraic_t_section_lifts": "COMPLETE",
            "remaining_algebraic_t_section_lifts": "NOT_YET_CONSTRUCTED",
            "v_fiber_lift": "NOT_YET_CONSTRUCTED",
            "global_parent_cell_coverage": "NOT_CLAIMED",
            "honest_9dvl_score": "2/9",
        },
        "source": {
            "base_projection_semantic_sha256": base["semantic_sha256"],
            "root_isolation_semantic_sha256": roots["semantic_sha256"],
            "open_sector_lift_semantic_sha256": open_lift["semantic_sha256"],
            "ordered_t_sections": len(section_rows),
        },
        "simple_section_lift": {
            "simple_transversal_crossing_sections": len(crossings),
            "resultant_multiplicity_one_sections": len(crossings),
            "sections_with_nonresultant_event": 0,
            "section_u_root_points": total_section_root_points,
            "section_u_strips": total_section_strips,
            "section_base_cells": total_section_root_points + total_section_strips,
            "minimum_adjacent_sector_root_count": min(row[6] for row in crossings),
            "maximum_adjacent_sector_root_count": max(row[6] for row in crossings),
            "crossings_sha256": digest(crossings),
            "crossings": crossings,
        },
        "remaining_frontier": {
            "remaining_algebraic_t_sections": len(section_rows) - len(crossings),
            "census": dict(sorted(remaining_census.items())),
        },
        "semantic_sha256": digest(semantic_payload),
        "resource_effect": {
            "simple_section_cell_ceiling": 500_000,
            "actual_simple_section_cells": total_section_root_points + total_section_strips,
            "ceiling_not_triggered": total_section_root_points + total_section_strips < 500_000,
            "next_stage": "resolve the remaining 671 algebraic t sections: 406 with no visible stack change, 251 complex same-count transitions, and 14 root-count changes",
        },
        "generator_dependency": {
            "python": sys.version.split()[0],
            "sympy": sp.__version__,
            "independent_verifier": "STANDARD_LIBRARY_ONLY",
        },
        "theorem_effect": "Exact algebraic-section fibers and local crossing attachments are complete for 1022 simple transversal resultant events; 671 algebraic sections, v lifting, global gluing, and the diagonal-three invariant remain open; honest 9DVL score remains 2/9.",
    }
    OUTPUT.write_text(
        json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="ascii",
    )
    print("WROTE", OUTPUT)
    print("CROSSINGS", len(crossings), "REMAINING", len(section_rows) - len(crossings))
    print("SECTION_CELLS", total_section_root_points, "+", total_section_strips, "=", total_section_root_points + total_section_strips)
    print("REMAINING_CENSUS", dict(sorted(remaining_census.items())))


if __name__ == "__main__":
    main()
