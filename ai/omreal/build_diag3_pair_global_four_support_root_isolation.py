#!/usr/bin/env python3
"""Build exact, globally ordered isolating data for the four-support t roots."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

import sympy as sp


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz"
OUTPUT = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ROOT_ISOLATION.json.gz"
FORMAT = "diag3-pair-global-row2599-four-support-root-isolation-v1"
SOURCE_FORMAT = "diag3-pair-global-row2599-four-support-base-projection-v1"
WIDTH_CEILING = sp.Rational(1, 2**48)
t = sp.symbols("t")


def digest(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def fraction_text(value):
    value = sp.Rational(value)
    if value.q == 1:
        return str(value.p)
    return f"{value.p}/{value.q}"


def main():
    source = json.loads(gzip.decompress(SOURCE.read_bytes()))
    if source["format"] != SOURCE_FORMAT or source["status"] != "PROVED":
        raise AssertionError("second-projection source changed")
    projection = source["second_projection"]
    if projection["distinct_factor_count"] != 2_333:
        raise AssertionError("univariate factor catalog changed")
    if projection["factor_interior_root_incidences"] != 1_693:
        raise AssertionError("root-incidence frontier changed")

    sections = []
    for factor in projection["catalog"]:
        expected = factor["interior_root_count"]
        if not expected:
            continue
        polynomial = sp.Poly(
            sum(
                sp.Integer(coefficient) * t**degree
                for degree, coefficient in enumerate(
                    factor["coefficients_low_to_high"]
                )
            ),
            t,
            domain=sp.QQ,
        )
        interior = []
        for (left, right), multiplicity in sp.intervals(
            polynomial, eps=WIDTH_CEILING
        ):
            if right <= 0 or left >= 1:
                continue
            if not (0 <= left <= right <= 1):
                raise AssertionError("root interval straddles the square boundary")
            if multiplicity != 1:
                raise AssertionError("source factor is not squarefree")
            interior.append((left, right))
        if len(interior) != expected:
            raise AssertionError(f"root count changed at factor {factor['id']}")
        for factor_root_index, (left, right) in enumerate(interior):
            sections.append(
                {
                    "factor_id": factor["id"],
                    "factor_root_index": factor_root_index,
                    "left": fraction_text(left),
                    "right": fraction_text(right),
                }
            )

    sections.sort(
        key=lambda row: (
            Fraction(row["left"]),
            Fraction(row["right"]),
            row["factor_id"],
        )
    )
    for index, row in enumerate(sections):
        row["id"] = index
    if len(sections) != 1_693:
        raise AssertionError("root-section count changed")

    intervals = [
        (Fraction(row["left"]), Fraction(row["right"])) for row in sections
    ]
    if not all(right < next_left for (_left, right), (next_left, _next_right) in zip(intervals, intervals[1:])):
        raise AssertionError("the requested isolation precision did not separate all roots")
    minimum_gap = min(
        next_left - right
        for (_left, right), (next_left, _next_right) in zip(
            intervals, intervals[1:]
        )
    )
    rational_sections = sum(left == right for left, right in intervals)
    endpoint_values = [value for interval in intervals for value in interval]
    maximum_numerator_bits = max(abs(value.numerator).bit_length() for value in endpoint_values)
    maximum_denominator_bits = max(value.denominator.bit_length() for value in endpoint_values)
    factor_section_census = Counter(row["factor_id"] for row in sections)
    semantic_payload = {
        "source_semantic_sha256": source["semantic_sha256"],
        "source_univariate_catalog_sha256": projection["catalog_sha256"],
        "sections": sections,
    }

    record = {
        "format": FORMAT,
        "status": "PROVED",
        "scope": {
            "interior_t_root_isolation": "COMPLETE",
            "global_root_deduplication": "COMPLETE_BY_PAIRWISE_DISJOINT_RATIONAL_ENCLOSURES",
            "global_root_order": "COMPLETE",
            "base_sign_invariant_cad": "NOT_YET_CONSTRUCTED",
            "global_parent_cell_coverage": "NOT_CLAIMED",
            "honest_9dvl_score": "2/9",
        },
        "source": {
            "format": source["format"],
            "semantic_sha256": source["semantic_sha256"],
            "univariate_factor_catalog_sha256": projection["catalog_sha256"],
            "univariate_factors": projection["distinct_factor_count"],
            "factor_root_incidences": projection["factor_interior_root_incidences"],
        },
        "root_isolation": {
            "distinct_interior_t_sections": len(sections),
            "rational_sections": rational_sections,
            "irrational_sections": len(sections) - rational_sections,
            "factors_with_interior_sections": len(factor_section_census),
            "requested_interval_width_ceiling": fraction_text(WIDTH_CEILING),
            "minimum_certified_gap": str(minimum_gap),
            "maximum_endpoint_numerator_bits": maximum_numerator_bits,
            "maximum_endpoint_denominator_bits": maximum_denominator_bits,
            "sections_sha256": digest(sections),
            "sections": sections,
        },
        "semantic_sha256": digest(semantic_payload),
        "resource_effect": {
            "section_ceiling": 10_000,
            "actual_distinct_sections": len(sections),
            "ceiling_not_triggered": len(sections) < 10_000,
            "next_stage": "lift the 114 base curve factors in u over 1694 open t sectors and 1693 algebraic t sections, then lift the 22 original v walls",
        },
        "generator_dependency": {
            "python": sys.version.split()[0],
            "sympy": sp.__version__,
            "independent_verifier": "STANDARD_LIBRARY_ONLY",
        },
        "theorem_effect": "The former upper bound of 1693 factor-root incidences is exact: all 1693 interior t roots have pairwise disjoint rational point/interval certificates and a global order; base lifting and the global master complex remain open; honest 9DVL score remains 2/9.",
    }
    encoded = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    OUTPUT.write_bytes(gzip.compress(encoded, compresslevel=9, mtime=0))
    print("WROTE", OUTPUT)
    print("SECTIONS", len(sections), "=", rational_sections, "rational +", len(sections) - rational_sections, "irrational")
    print("MINIMUM_GAP", minimum_gap)
    print("ENDPOINT_BITS", maximum_numerator_bits, maximum_denominator_bits)


if __name__ == "__main__":
    main()
