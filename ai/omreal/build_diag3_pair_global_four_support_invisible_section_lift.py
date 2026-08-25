#!/usr/bin/env python3
"""Build exact constant-stack lifts for raw-simple invisible t events."""

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
SIMPLE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_SIMPLE_SECTION_LIFT.json"
OUTPUT = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_INVISIBLE_SECTION_LIFT.json"
FORMAT = "diag3-pair-global-row2599-four-support-invisible-section-lift-v1"
u, t = sp.symbols("u t")
KIND_CODE = {"coefficient": 0, "discriminant": 1, "resultant": 2}


def digest(value):
    return sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")).hexdigest()


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


def strip_boundary(polynomial):
    polynomial = sp.Poly(polynomial, t, domain=sp.QQ)
    if polynomial.is_zero or polynomial.degree() <= 0:
        return None
    while polynomial.eval(0) == 0:
        polynomial = sp.div(polynomial, sp.Poly(t, t, domain=sp.QQ))[0]
    while polynomial.eval(1) == 0:
        polynomial = sp.div(polynomial, sp.Poly(t - 1, t, domain=sp.QQ))[0]
    return polynomial if polynomial.degree() > 0 else None


def add_event(incidence, catalog, kind, owner, polynomial):
    polynomial = strip_boundary(polynomial)
    if polynomial is None:
        return
    _scalar, factors = sp.factor_list(polynomial.as_expr(), gens=(t,))
    for factor, multiplicity in factors:
        factor_id = catalog.get(primitive_coefficients(factor))
        if factor_id is None:
            raise AssertionError("raw event factor missing from projection catalog")
        incidence[factor_id].append((kind, owner, int(multiplicity)))


def load_sequences(manifest):
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


def main():
    base = json.loads(gzip.decompress(BASE.read_bytes()))
    roots = json.loads(gzip.decompress(ROOTS.read_bytes()))
    open_lift = json.loads(OPEN.read_bytes())
    simple = json.loads(SIMPLE.read_bytes())
    if simple["source"]["open_sector_lift_semantic_sha256"] != open_lift["semantic_sha256"]:
        raise AssertionError("simple-section source changed")

    polynomials = [
        sum(
            sp.Integer(term["coefficient"])
            * u ** term["exponent"][0]
            * t ** term["exponent"][1]
            for term in row["polynomial"]
        )
        for row in base["base_factorization"]["catalog"]
    ]
    catalog = {
        tuple(row["coefficients_low_to_high"]): row["id"]
        for row in base["second_projection"]["catalog"]
    }
    incidence = defaultdict(list)
    for base_id, polynomial in enumerate(polynomials):
        coefficient_rows = list(reversed(sp.Poly(polynomial, u).all_coeffs()))
        for degree_u, coefficient in enumerate(coefficient_rows):
            add_event(incidence, catalog, "coefficient", (base_id, degree_u), coefficient)
        if sp.degree(polynomial, u) >= 2:
            add_event(
                incidence,
                catalog,
                "discriminant",
                (base_id, -1),
                sp.discriminant(polynomial, u),
            )
    for left in range(len(polynomials)):
        for right in range(left + 1, len(polynomials)):
            add_event(
                incidence,
                catalog,
                "resultant",
                (left, right),
                sp.resultant(polynomials[left], polynomials[right], u),
            )
    boundary_factors = defaultdict(list)
    for row in open_lift["bounded_u_boundary_audit"]["factorizations"]:
        for factor in row["factors"]:
            boundary_factors[factor["id"]].append((row["base_factor_id"], factor["multiplicity"]))

    sequences = load_sequences(open_lift)
    sections = roots["root_isolation"]["sections"]
    completed = []
    kind_census = Counter()
    root_points = 0
    strips = 0
    unchanged_complex = 0
    for section_id, (section, left, right) in enumerate(
        zip(sections, sequences[:-1], sequences[1:], strict=True)
    ):
        if left != right:
            continue
        factor_id = section["factor_id"]
        events = incidence[factor_id]
        boundary = boundary_factors[factor_id]
        eligible = (
            len(events) == 1
            and events[0][2] == 1
            and not boundary
            and not (events[0][0] == "coefficient" and events[0][1][1] == 0)
        )
        if not eligible:
            unchanged_complex += 1
            continue
        kind, owner, multiplicity = events[0]
        root_count = len(left)
        completed.append(
            [
                section_id,
                factor_id,
                section["factor_root_index"],
                KIND_CODE[kind],
                owner[0],
                owner[1],
                root_count,
            ]
        )
        kind_census[kind] += 1
        root_points += root_count
        strips += root_count + 1

    if len(completed) != 363 or unchanged_complex != 43:
        raise AssertionError("invisible-section frontier changed")
    semantic_payload = {
        "open_sector_lift_semantic_sha256": open_lift["semantic_sha256"],
        "simple_section_lift_semantic_sha256": simple["semantic_sha256"],
        "completed": completed,
    }
    record = {
        "format": FORMAT,
        "status": "PROVED",
        "scope": {
            "raw_simple_constant_stack_algebraic_t_section_lifts": "COMPLETE",
            "remaining_algebraic_t_section_lifts": "NOT_YET_CONSTRUCTED",
            "v_fiber_lift": "NOT_YET_CONSTRUCTED",
            "global_parent_cell_coverage": "NOT_CLAIMED",
            "honest_9dvl_score": "2/9",
        },
        "source": {
            "base_projection_semantic_sha256": base["semantic_sha256"],
            "root_isolation_semantic_sha256": roots["semantic_sha256"],
            "open_sector_lift_semantic_sha256": open_lift["semantic_sha256"],
            "simple_section_lift_semantic_sha256": simple["semantic_sha256"],
        },
        "invisible_section_lift": {
            "completed_constant_stack_sections": len(completed),
            "raw_event_kind_census": dict(sorted(kind_census.items())),
            "raw_event_multiplicity_one_sections": len(completed),
            "u_boundary_event_sections": 0,
            "section_u_root_points": root_points,
            "section_u_strips": strips,
            "section_base_cells": root_points + strips,
            "completed_sha256": digest(completed),
            "completed": completed,
        },
        "remaining_frontier": {
            "remaining_algebraic_t_sections": 308,
            "census": {
                "complex_unchanged_stack": 43,
                "complex_same_count_transition": 251,
                "root_count_change": 14,
            },
        },
        "semantic_sha256": digest(semantic_payload),
        "resource_effect": {
            "constant_stack_section_cell_ceiling": 100_000,
            "actual_constant_stack_section_cells": root_points + strips,
            "ceiling_not_triggered": root_points + strips < 100_000,
            "next_stage": "resolve 43 complex unchanged-stack sections, 251 complex same-count transitions, and 14 root-count changes",
        },
        "generator_dependency": {
            "python": sys.version.split()[0],
            "sympy": sp.__version__,
            "independent_verifier": "STANDARD_LIBRARY_ONLY",
        },
        "theorem_effect": "Exact constant-stack algebraic fibers are complete for 363 raw-simple nonboundary events; 308 algebraic sections, v lifting, global gluing, and the diagonal-three invariant remain open; honest 9DVL score remains 2/9.",
    }
    OUTPUT.write_text(
        json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="ascii",
    )
    print("WROTE", OUTPUT)
    print("COMPLETED", len(completed), "KIND_CENSUS", dict(sorted(kind_census.items())))
    print("SECTION_CELLS", root_points, "+", strips, "=", root_points + strips)
    print("REMAINING 43 + 251 + 14 = 308")


if __name__ == "__main__":
    main()
