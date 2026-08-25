#!/usr/bin/env python3
"""Build the exact open-t-sector base lift for the four-support arrangement."""

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
BASE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz"
ROOTS = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ROOT_ISOLATION.json.gz"
OUTPUT = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT.json"
FORMAT = "diag3-pair-global-row2599-four-support-open-sector-lift-v1"
SHARD_FORMAT = "diag3-pair-global-row2599-four-support-open-sector-lift-shard-v1"
BASE_FORMAT = "diag3-pair-global-row2599-four-support-base-projection-v1"
ROOT_FORMAT = "diag3-pair-global-row2599-four-support-root-isolation-v1"
ISOLATION_WIDTH = sp.Rational(1, 2**40)
DYADIC_EXPONENT = 48
DYADIC_DENOMINATOR = 2**DYADIC_EXPONENT
SHARD_COUNT = 32
u, t = sp.symbols("u t")


def digest(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def fraction_text(value):
    value = sp.Rational(value)
    if value.q == 1:
        return str(value.p)
    return f"{value.p}/{value.q}"


def parse_bivariate(rows):
    return sp.Poly(
        sum(
            sp.Integer(row["coefficient"])
            * u ** row["exponent"][0]
            * t ** row["exponent"][1]
            for row in rows
        ),
        u,
        t,
        domain=sp.QQ,
    )


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


def strip_t_boundary(polynomial):
    polynomial = sp.Poly(polynomial, t, domain=sp.QQ)
    if polynomial.is_zero or polynomial.degree() <= 0:
        return None
    while polynomial.eval(0) == 0:
        polynomial = sp.div(polynomial, sp.Poly(t, t, domain=sp.QQ))[0]
    while polynomial.eval(1) == 0:
        polynomial = sp.div(polynomial, sp.Poly(t - 1, t, domain=sp.QQ))[0]
    if polynomial.degree() <= 0:
        return None
    return polynomial


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


def dyadic_enclosure(left, right):
    left = sp.Rational(left)
    right = sp.Rational(right)
    left_numerator = int(sp.floor(left * DYADIC_DENOMINATOR))
    right_numerator = int(sp.ceiling(right * DYADIC_DENOMINATOR))
    if left_numerator == right_numerator:
        left_numerator -= 1
        right_numerator += 1
    if not 0 < left_numerator < right_numerator < DYADIC_DENOMINATOR:
        raise AssertionError("dyadic enclosure left the open u interval")
    return left_numerator, right_numerator


def main():
    base = json.loads(gzip.decompress(BASE.read_bytes()))
    roots = json.loads(gzip.decompress(ROOTS.read_bytes()))
    if base["format"] != BASE_FORMAT or base["status"] != "PROVED":
        raise AssertionError("base-projection source changed")
    if roots["format"] != ROOT_FORMAT or roots["status"] != "PROVED":
        raise AssertionError("root-isolation source changed")
    if roots["source"]["semantic_sha256"] != base["semantic_sha256"]:
        raise AssertionError("projection/root source link changed")

    base_rows = base["base_factorization"]["catalog"]
    base_polynomials = [parse_bivariate(row["polynomial"]) for row in base_rows]
    univariate_rows = base["second_projection"]["catalog"]
    univariate_id = {
        tuple(row["coefficients_low_to_high"]): row["id"]
        for row in univariate_rows
    }

    # The Collins family already contains every nonconstant factor from u=1,
    # but the original record did not make that bounded-boundary fact explicit.
    right_boundary_factorizations = []
    right_boundary_factor_ids = set()
    right_boundary_factor_occurrences = 0
    for base_id, polynomial in enumerate(base_polynomials):
        boundary = strip_t_boundary(polynomial.as_expr().subs(u, 1))
        if boundary is None:
            continue
        _scalar, factors = sp.factor_list(boundary.as_expr(), gens=(t,))
        decomposition = []
        for factor, multiplicity in factors:
            key = primitive_coefficients(factor)
            if key not in univariate_id:
                raise AssertionError(f"u=1 boundary factor missing at base factor {base_id}")
            factor_id = univariate_id[key]
            decomposition.append({"id": factor_id, "multiplicity": int(multiplicity)})
            right_boundary_factor_ids.add(factor_id)
            right_boundary_factor_occurrences += 1
        right_boundary_factorizations.append(
            {"base_factor_id": base_id, "factors": decomposition}
        )

    samples = sector_samples(roots)
    sectors = []
    specialization_root_census = Counter()
    sector_root_census = Counter()
    total_roots = 0
    minimum_gap = None
    maximum_span_numerator = 0

    for sector_id, sample in enumerate(samples):
        sample_sympy = sp.Rational(sample.numerator, sample.denominator)
        sector_roots = []
        for base_id, polynomial in enumerate(base_polynomials):
            specialized = sp.Poly(
                polynomial.as_expr().subs(t, sample_sympy), u, domain=sp.QQ
            )
            interior = []
            for (left, right), multiplicity in sp.intervals(
                specialized, eps=ISOLATION_WIDTH
            ):
                if right <= 0 or left >= 1:
                    continue
                if not bool(0 <= left <= right <= 1):
                    raise AssertionError("specialized root straddles the u boundary")
                if multiplicity != 1:
                    raise AssertionError("specialized base factor is not squarefree")
                interior.append((left, right))
            specialization_root_census[len(interior)] += 1
            for left, right in interior:
                left_numerator, right_numerator = dyadic_enclosure(left, right)
                sector_roots.append(
                    [
                        base_id,
                        left_numerator,
                        right_numerator,
                    ]
                )

        sector_roots.sort(
            key=lambda row: (row[1], row[2], row[0])
        )
        parsed = [(row[1], row[2]) for row in sector_roots]
        if not all(
            right <= next_left
            for (_left, right), (next_left, _next_right) in zip(
                parsed, parsed[1:]
            )
        ):
            raise AssertionError(f"u-root intervals overlap in sector {sector_id}")
        for (_left, right), (next_left, _next_right) in zip(parsed, parsed[1:]):
            gap = next_left - right
            minimum_gap = gap if minimum_gap is None else min(minimum_gap, gap)
        for left, right in parsed:
            maximum_span_numerator = max(maximum_span_numerator, right - left)
        sector_root_census[len(sector_roots)] += 1
        total_roots += len(sector_roots)
        sectors.append(sector_roots)
        if sector_id % 100 == 0:
            print("SECTOR", sector_id, "ROOTS", len(sector_roots), flush=True)

    open_strips = total_roots + len(sectors)
    open_sector_cells = total_roots + open_strips
    sectors_digest = digest(sectors)
    shard_rows = []
    for shard_index in range(SHARD_COUNT):
        sector_start = len(sectors) * shard_index // SHARD_COUNT
        sector_end = len(sectors) * (shard_index + 1) // SHARD_COUNT
        shard_record = {
            "format": SHARD_FORMAT,
            "shard_index": shard_index,
            "shard_count": SHARD_COUNT,
            "sector_start": sector_start,
            "sector_end": sector_end,
            "sectors": sectors[sector_start:sector_end],
        }
        shard_encoded = (
            json.dumps(shard_record, sort_keys=True, separators=(",", ":")) + "\n"
        ).encode("ascii")
        shard_compressed = gzip.compress(shard_encoded, compresslevel=9, mtime=0)
        shard_name = (
            "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT_"
            f"SHARD_{shard_index:02d}_OF_{SHARD_COUNT}.json.gz"
        )
        (OUTPUT.parent / shard_name).write_bytes(shard_compressed)
        shard_rows.append(
            {
                "index": shard_index,
                "path": shard_name,
                "sector_start": sector_start,
                "sector_end": sector_end,
                "bytes": len(shard_compressed),
                "sha256": sha256(shard_compressed).hexdigest(),
            }
        )

    semantic_payload = {
        "base_semantic_sha256": base["semantic_sha256"],
        "root_isolation_semantic_sha256": roots["semantic_sha256"],
        "right_boundary_factorizations": right_boundary_factorizations,
        "sectors_sha256": sectors_digest,
    }
    record = {
        "format": FORMAT,
        "status": "PROVED",
        "scope": {
            "bounded_u_boundary_projection_audit": "COMPLETE",
            "open_t_sector_base_lift": "COMPLETE_BY_PROJECTION_INVARIANCE",
            "algebraic_t_section_base_lift": "NOT_YET_CONSTRUCTED",
            "v_fiber_lift": "NOT_YET_CONSTRUCTED",
            "global_parent_cell_coverage": "NOT_CLAIMED",
            "honest_9dvl_score": "2/9",
        },
        "source": {
            "base_projection_format": base["format"],
            "base_projection_semantic_sha256": base["semantic_sha256"],
            "root_isolation_format": roots["format"],
            "root_isolation_semantic_sha256": roots["semantic_sha256"],
            "base_curve_factors": len(base_polynomials),
            "ordered_t_sections": roots["root_isolation"]["distinct_interior_t_sections"],
        },
        "bounded_u_boundary_audit": {
            "base_factor_evaluations": len(base_polynomials),
            "nonconstant_boundary_evaluations_after_t_boundary_reduction": len(right_boundary_factorizations),
            "distinct_projection_factors_used": len(right_boundary_factor_ids),
            "factor_occurrences": right_boundary_factor_occurrences,
            "all_factors_present_in_second_projection_catalog": True,
            "factorizations_sha256": digest(right_boundary_factorizations),
            "factorizations": right_boundary_factorizations,
        },
        "open_sector_lift": {
            "open_t_sectors": len(sectors),
            "specialized_base_factor_instances": len(sectors) * len(base_polynomials),
            "specialization_interior_root_count_census": {
                str(count): amount
                for count, amount in sorted(specialization_root_census.items())
            },
            "open_sector_u_root_sections": total_roots,
            "open_sector_u_strips": open_strips,
            "open_sector_base_cells": open_sector_cells,
            "minimum_roots_in_one_t_sector": min(map(len, sectors)),
            "maximum_roots_in_one_t_sector": max(map(len, sectors)),
            "sector_root_count_census": {
                str(count): amount for count, amount in sorted(sector_root_census.items())
            },
            "dyadic_endpoint_exponent": DYADIC_EXPONENT,
            "maximum_interval_span_numerator": maximum_span_numerator,
            "maximum_interval_width": str(Fraction(maximum_span_numerator, DYADIC_DENOMINATOR)),
            "minimum_within_sector_certified_gap": str(Fraction(minimum_gap, DYADIC_DENOMINATOR)),
            "sectors_sha256": sectors_digest,
        },
        "artifact_shards": {
            "format": SHARD_FORMAT,
            "shard_count": SHARD_COUNT,
            "shards": shard_rows,
        },
        "semantic_sha256": digest(semantic_payload),
        "resource_effect": {
            "open_sector_base_cell_ceiling": 1_000_000,
            "actual_open_sector_base_cells": open_sector_cells,
            "ceiling_not_triggered": open_sector_cells < 1_000_000,
            "next_stage": "lift the 114 base factors over the 1693 algebraic t sections and construct their incident closure maps to the certified open-sector stacks",
        },
        "generator_dependency": {
            "python": sys.version.split()[0],
            "sympy": sp.__version__,
            "independent_verifier": "STANDARD_LIBRARY_ONLY",
        },
        "theorem_effect": "The complete bounded projection and ordered t sections lift to exact ordered u-root stacks on every open t sector; algebraic t-section fibers, v lifting, global gluing, and the diagonal-three invariant remain open; honest 9DVL score remains 2/9.",
    }
    encoded = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    OUTPUT.write_bytes(encoded)
    print("WROTE", OUTPUT)
    print("SHARDS", SHARD_COUNT, "BYTES", sum(row["bytes"] for row in shard_rows))
    print("SPECIALIZATIONS", len(sectors) * len(base_polynomials))
    print("ROOTS", total_roots, "STRIPS", open_strips, "CELLS", open_sector_cells)
    print("BOUNDARY_FACTORIZATIONS", len(right_boundary_factorizations), len(right_boundary_factor_ids))


if __name__ == "__main__":
    main()
