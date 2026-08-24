#!/usr/bin/env python3
"""Build the exact v-lift over every open (t,u) base cell.

The completed base CAD has two kinds of cells.  This checkpoint handles the
133,828 full-dimensional cells lying over open t sectors and open u strips.
Every sample is rational, while the only nonlinear fiber wall is quadratic,
so the complete ordered v-root stack can be compared with exact rational
arithmetic.  Algebraic u-section and t-section fibers are intentionally left
for subsequent checkpoints.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from math import gcd, lcm
from pathlib import Path
import sys

import sympy as sp


HERE = Path(__file__).resolve().parent
PROJECTION = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_PROJECTION.json"
BASE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz"
ROOTS = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ROOT_ISOLATION.json.gz"
OPEN = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT.json"
OUTPUT = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_CELL_V_LIFT.json"
FORMAT = "diag3-pair-global-row2599-four-support-open-cell-v-lift-v1"
SHARD_FORMAT = "diag3-pair-global-row2599-four-support-open-cell-v-lift-shard-v1"
SHARD_COUNT = 32
u_symbol, t_symbol, v_symbol = sp.symbols("u t v")


def digest(value) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


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


def parse_wall(row):
    coefficients = {}
    for term in row["polynomial"]:
        degree_u, degree_t, degree_v = term["exponent"]
        coefficients.setdefault(degree_v, []).append(
            (degree_u, degree_t, Fraction(term["coefficient"]))
        )
    return row["id"], row["fiber_degree"], coefficients


def evaluate_bivariate(terms, value_u, value_t):
    return sum(
        coefficient * value_u**degree_u * value_t**degree_t
        for degree_u, degree_t, coefficient in terms
    )


def compare_quadratic_root_to_rational(a, b, c, branch, value):
    """Compare one root of a positive-leading quadratic with a rational.

    Return -1, 0, or +1 according as the selected root is less than, equal
    to, or greater than ``value``.  ``branch`` is 1 for the lower root and 2
    for the upper root.  The discriminant must be strictly positive.
    """

    if not a > 0 or not b * b - 4 * a * c > 0:
        raise AssertionError("quadratic comparison outside the two-root case")
    vertex = -b / (2 * a)
    at_value = a * value * value + b * value + c
    if branch == 1:
        if value >= vertex:
            return -1
        if at_value == 0:
            return 0
        return -1 if at_value < 0 else 1
    if branch == 2:
        if value <= vertex:
            return 1
        if at_value == 0:
            return 0
        return -1 if at_value > 0 else 1
    raise AssertionError("unknown quadratic branch")


def ordered_signature(walls, value_u, value_t):
    roots = []
    for wall_id, degree, coefficients in walls:
        values = {
            power: evaluate_bivariate(terms, value_u, value_t)
            for power, terms in coefficients.items()
        }
        if degree == 0:
            if values.get(0, Fraction(0)) == 0:
                raise AssertionError("base-only wall vanished on an open base cell")
            continue
        if degree == 1:
            leading = values.get(1, Fraction(0))
            constant = values.get(0, Fraction(0))
            if leading == 0:
                raise AssertionError("linear leading coefficient vanished on an open base cell")
            root = -constant / leading
            if root in (0, 1):
                raise AssertionError("linear root hit the v boundary inside an open base cell")
            if 0 < root < 1:
                roots.append(("linear", wall_id, 0, root))
            continue

        a = values.get(2, Fraction(0))
        b = values.get(1, Fraction(0))
        c = values.get(0, Fraction(0))
        if a == 0:
            raise AssertionError("quadratic leading coefficient vanished on an open base cell")
        if a < 0:
            a, b, c = -a, -b, -c
        discriminant = b * b - 4 * a * c
        if discriminant == 0:
            raise AssertionError("quadratic discriminant vanished on an open base cell")
        if discriminant < 0:
            continue
        for branch in (1, 2):
            at_zero = compare_quadratic_root_to_rational(a, b, c, branch, Fraction(0))
            at_one = compare_quadratic_root_to_rational(a, b, c, branch, Fraction(1))
            if at_zero == 0 or at_one == 0:
                raise AssertionError("quadratic root hit the v boundary inside an open base cell")
            if at_zero > 0 and at_one < 0:
                roots.append(("quadratic", wall_id, branch, a, b, c))

    def less(left, right):
        if left[0] == right[0] == "linear":
            if left[3] == right[3]:
                raise AssertionError("two linear roots collide on an open base cell")
            return left[3] < right[3]
        if left[0] == "quadratic" and right[0] == "linear":
            comparison = compare_quadratic_root_to_rational(
                left[3], left[4], left[5], left[2], right[3]
            )
            if comparison == 0:
                raise AssertionError("linear/quadratic collision on an open base cell")
            return comparison < 0
        if left[0] == "linear" and right[0] == "quadratic":
            comparison = compare_quadratic_root_to_rational(
                right[3], right[4], right[5], right[2], left[3]
            )
            if comparison == 0:
                raise AssertionError("linear/quadratic collision on an open base cell")
            return comparison > 0
        if left[1] != right[1]:
            raise AssertionError("unexpected comparison between two quadratic walls")
        return left[2] < right[2]

    ordered = []
    for root in roots:
        index = 0
        while index < len(ordered) and not less(root, ordered[index]):
            index += 1
        ordered.insert(index, root)
    return tuple((root[1], root[2]) for root in ordered)


def sector_samples(root_record):
    sections = [
        (Fraction(row["left"]), Fraction(row["right"]))
        for row in root_record["root_isolation"]["sections"]
    ]
    return (
        [sections[0][0] / 2]
        + [
            (left[1] + right[0]) / 2
            for left, right in zip(sections, sections[1:])
        ]
        + [(sections[-1][1] + 1) / 2]
    )


def load_sectors(open_record):
    sectors = []
    for row in open_record["artifact_shards"]["shards"]:
        shard = json.loads(gzip.decompress((OPEN.parent / row["path"]).read_bytes()))
        sectors.extend(shard["sectors"])
    return sectors


def open_strip_samples(stack, denominator):
    if not stack:
        return [Fraction(1, 2)]
    return (
        [Fraction(stack[0][1], 2 * denominator)]
        + [
            Fraction(left[2] + right[1], 2 * denominator)
            for left, right in zip(stack, stack[1:])
        ]
        + [Fraction(stack[-1][2] + denominator, 2 * denominator)]
    )


def endpoint_factorizations(projection, base):
    base_keys = {
        canonical_terms(
            sum(
                sp.Integer(term["coefficient"])
                * u_symbol ** term["exponent"][0]
                * t_symbol ** term["exponent"][1]
                for term in row["polynomial"]
            ),
            (u_symbol, t_symbol),
        ): row["id"]
        for row in base["base_factorization"]["catalog"]
    }
    t_keys = {
        canonical_terms(
            sum(
                sp.Integer(value) * t_symbol**degree
                for degree, value in enumerate(row["coefficients_low_to_high"])
            ),
            (t_symbol,),
        ): row["id"]
        for row in base["second_projection"]["catalog"]
    }
    boundary_keys = {
        canonical_terms(u_symbol, (u_symbol, t_symbol)): "u=0",
        canonical_terms(u_symbol - 1, (u_symbol, t_symbol)): "u=1",
        canonical_terms(t_symbol, (u_symbol, t_symbol)): "t=0",
        canonical_terms(t_symbol - 1, (u_symbol, t_symbol)): "t=1",
    }
    rows = []
    for wall in projection["fiber_walls"]["catalog"]:
        expression = sum(
            sp.Integer(term["coefficient"])
            * u_symbol ** term["exponent"][0]
            * t_symbol ** term["exponent"][1]
            * v_symbol ** term["exponent"][2]
            for term in wall["polynomial"]
        )
        for endpoint in (0, 1):
            specialized = sp.expand(expression.subs(v_symbol, endpoint))
            _scalar, factors = sp.factor_list(specialized, gens=(u_symbol, t_symbol))
            boundary = Counter()
            base_factors = []
            t_factors = []
            for factor, multiplicity in factors:
                bivariate_key = canonical_terms(factor, (u_symbol, t_symbol))
                if bivariate_key in boundary_keys:
                    boundary[boundary_keys[bivariate_key]] += int(multiplicity)
                    continue
                if bivariate_key in base_keys:
                    base_factors.append([base_keys[bivariate_key], int(multiplicity)])
                    continue
                if sp.degree(factor, u_symbol) == 0:
                    univariate_key = canonical_terms(factor, (t_symbol,))
                    if univariate_key in t_keys:
                        t_factors.append([t_keys[univariate_key], int(multiplicity)])
                        continue
                raise AssertionError(
                    f"uncovered v={endpoint} factor for wall {wall['id']}: {factor}"
                )
            rows.append(
                {
                    "wall_id": wall["id"],
                    "endpoint": endpoint,
                    "boundary_factors": dict(sorted(boundary.items())),
                    "base_factors": sorted(base_factors),
                    "t_factors": sorted(t_factors),
                }
            )
    return rows


def main():
    projection = json.loads(PROJECTION.read_bytes())
    base = json.loads(gzip.decompress(BASE.read_bytes()))
    roots = json.loads(gzip.decompress(ROOTS.read_bytes()))
    open_record = json.loads(OPEN.read_bytes())
    if not projection["status"] == base["status"] == roots["status"] == open_record["status"] == "PROVED":
        raise AssertionError("bad source status")
    if open_record["source"]["base_projection_semantic_sha256"] != base["semantic_sha256"]:
        raise AssertionError("open/base source link changed")

    walls = [parse_wall(row) for row in projection["fiber_walls"]["catalog"]]
    endpoint_rows = endpoint_factorizations(projection, base)
    sectors = load_sectors(open_record)
    samples_t = sector_samples(roots)
    if not (len(sectors) == len(samples_t) == 1_694):
        raise AssertionError("open-sector source count changed")
    exponent = open_record["open_sector_lift"]["dyadic_endpoint_exponent"]
    denominator = 2**exponent

    raw_signatures = []
    sector_signatures = []
    root_census = Counter()
    wall_root_instances = Counter()
    total_roots = 0
    for sector_id, (stack, sample_t) in enumerate(zip(sectors, samples_t, strict=True)):
        current = []
        for sample_u in open_strip_samples(stack, denominator):
            signature = ordered_signature(walls, sample_u, sample_t)
            raw_signatures.append(signature)
            current.append(signature)
            root_census[len(signature)] += 1
            wall_root_instances.update(wall_id for wall_id, _branch in signature)
            total_roots += len(signature)
        sector_signatures.append(current)
        if sector_id % 100 == 0:
            print("SECTOR", sector_id, "STRIPS", len(current), flush=True)

    signature_catalog = sorted(set(raw_signatures))
    signature_id = {signature: index for index, signature in enumerate(signature_catalog)}
    sector_ids = [
        [signature_id[signature] for signature in sector]
        for sector in sector_signatures
    ]
    shard_rows = []
    for shard_index in range(SHARD_COUNT):
        sector_start = len(sector_ids) * shard_index // SHARD_COUNT
        sector_end = len(sector_ids) * (shard_index + 1) // SHARD_COUNT
        shard = {
            "format": SHARD_FORMAT,
            "shard_index": shard_index,
            "shard_count": SHARD_COUNT,
            "sector_start": sector_start,
            "sector_end": sector_end,
            "strip_signature_ids": sector_ids[sector_start:sector_end],
        }
        encoded = (json.dumps(shard, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
        compressed = gzip.compress(encoded, compresslevel=9, mtime=0)
        name = (
            "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_CELL_V_LIFT_"
            f"SHARD_{shard_index:02d}_OF_{SHARD_COUNT}.json.gz"
        )
        (OUTPUT.parent / name).write_bytes(compressed)
        shard_rows.append(
            {
                "index": shard_index,
                "path": name,
                "sector_start": sector_start,
                "sector_end": sector_end,
                "bytes": len(compressed),
                "sha256": sha256(compressed).hexdigest(),
            }
        )

    open_base_cells = len(raw_signatures)
    open_v_strips = total_roots + open_base_cells
    lifted_cells = total_roots + open_v_strips
    semantic_payload = {
        "projection_semantic_sha256": projection["semantic_sha256"],
        "base_projection_semantic_sha256": base["semantic_sha256"],
        "root_isolation_semantic_sha256": roots["semantic_sha256"],
        "open_sector_lift_semantic_sha256": open_record["semantic_sha256"],
        "endpoint_factorizations": endpoint_rows,
        "signature_catalog": signature_catalog,
        "sector_signature_ids_sha256": digest(sector_ids),
    }
    record = {
        "format": FORMAT,
        "status": "PROVED",
        "scope": {
            "v_endpoint_projection_audit": "COMPLETE",
            "open_t_open_u_base_cell_v_lift": "COMPLETE_BY_PROJECTION_INVARIANCE",
            "open_t_algebraic_u_section_v_lift": "NOT_YET_CONSTRUCTED",
            "algebraic_t_section_v_lift": "NOT_YET_CONSTRUCTED",
            "global_gluing_and_closure_data": "NOT_CLAIMED",
            "honest_9dvl_score": "2/9",
        },
        "source": {
            "projection_semantic_sha256": projection["semantic_sha256"],
            "base_projection_semantic_sha256": base["semantic_sha256"],
            "root_isolation_semantic_sha256": roots["semantic_sha256"],
            "open_sector_lift_semantic_sha256": open_record["semantic_sha256"],
            "fiber_wall_count": len(walls),
            "open_t_sectors": len(sectors),
            "open_u_strips": open_base_cells,
        },
        "v_endpoint_audit": {
            "endpoint_evaluations": len(endpoint_rows),
            "all_nonboundary_factors_present_in_base_or_t_projection": True,
            "factorizations_sha256": digest(endpoint_rows),
            "factorizations": endpoint_rows,
        },
        "open_cell_v_lift": {
            "open_base_cells": open_base_cells,
            "distinct_fiber_order_signatures": len(signature_catalog),
            "minimum_interior_v_roots": min(root_census),
            "maximum_interior_v_roots": max(root_census),
            "interior_v_root_census": {
                str(count): amount for count, amount in sorted(root_census.items())
            },
            "interior_v_root_sections": total_roots,
            "open_v_strips": open_v_strips,
            "lifted_cells": lifted_cells,
            "wall_root_instance_census": {
                str(wall_id): count for wall_id, count in sorted(wall_root_instances.items())
            },
            "signature_catalog_sha256": digest(signature_catalog),
            "signature_catalog": [
                [[wall_id, branch] for wall_id, branch in signature]
                for signature in signature_catalog
            ],
            "sector_signature_ids_sha256": digest(sector_ids),
        },
        "artifact_shards": {
            "format": SHARD_FORMAT,
            "shard_count": SHARD_COUNT,
            "shards": shard_rows,
        },
        "semantic_sha256": digest(semantic_payload),
        "resource_effect": {
            "open_cell_lift_ceiling": 20_000_000,
            "actual_lifted_cells": lifted_cells,
            "ceiling_not_triggered": lifted_cells < 20_000_000,
            "next_stage": "lift the 132134 algebraic u-section fibers over open t sectors, then lift every algebraic t-section base cell",
        },
        "generator_dependency": {
            "python": sys.version.split()[0],
            "sympy": sp.__version__,
            "independent_verifier": "STANDARD_LIBRARY_EXACT_RATIONAL_REPLAY",
        },
        "theorem_effect": "Every full-dimensional base cell over the 1694 open t sectors has a complete exact ordered v-root stack for all 22 walls; algebraic u-section fibers, algebraic t-section fibers, global gluing, labels, middle-rank replay, and the diagonal-three invariant remain open; honest 9DVL score remains 2/9.",
    }
    OUTPUT.write_text(
        json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="ascii",
    )
    print("WROTE", OUTPUT)
    print("OPEN_BASE_CELLS", open_base_cells)
    print("SIGNATURES", len(signature_catalog))
    print("V_ROOTS", total_roots, "V_STRIPS", open_v_strips, "CELLS", lifted_cells)


if __name__ == "__main__":
    main()
