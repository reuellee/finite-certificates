#!/usr/bin/env python3
"""Build exact-data candidates for all final four-support algebraic sections.

SymPy is used only to propose the point ordering and ownership over the real
embedding selected by each pinned t-isolating interval.  The committed result
is accepted only by the separate standard-library number-field Sturm replay.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from pathlib import Path
import sys

import sympy as sp


HERE = Path(__file__).resolve().parent
BASE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz"
ROOTS = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ROOT_ISOLATION.json.gz"
OPEN = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT.json"
SIMPLE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_SIMPLE_SECTION_LIFT.json"
INVISIBLE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_INVISIBLE_SECTION_LIFT.json"
MULTI = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_MULTI_SECTION_LIFT.json"
REGULAR = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_REGULAR_RESIDUAL_SECTION_LIFT.json"
OUTPUT = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_FINAL_SECTION_LIFT.json"
FORMAT = "diag3-pair-global-row2599-four-support-final-section-lift-v1"
INTERVAL_BITS = 70
u, t = sp.symbols("u t")


def digest(value) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def selected_root(polynomial, lower: Fraction, upper: Fraction):
    if lower == upper:
        if sp.Poly(polynomial, t).eval(sp.Rational(lower.numerator, lower.denominator)) != 0:
            raise AssertionError("rational section missed its factor")
        return sp.Rational(lower.numerator, lower.denominator)
    roots = sp.Poly(polynomial, t).all_roots(radicals=False)
    selected = []
    for root in roots:
        approximation = sp.re(sp.N(root, 100))
        imaginary = abs(sp.im(sp.N(root, 100)))
        if imaginary < sp.Rational(1, 10**80) and sp.Rational(lower) < approximation < sp.Rational(upper):
            selected.append(root)
    if len(selected) != 1:
        raise AssertionError("t interval did not select one real algebraic root")
    return selected[0]


def rational_box(value, bits=INTERVAL_BITS) -> tuple[Fraction, Fraction]:
    scaled = sp.floor(sp.re(value) * (1 << bits))
    return (
        Fraction(int(scaled) - 1, 1 << bits),
        Fraction(int(scaled) + 2, 1 << bits),
    )


def sympy_interior_roots(polynomial):
    if polynomial.is_zero or polynomial.degree() <= 0:
        return []
    squarefree = polynomial.sqf_part()
    roots = []
    for root in squarefree.nroots(n=100, maxsteps=1_000):
        value = sp.N(root, 100)
        if abs(sp.im(value)) >= sp.Rational(1, 10**75):
            continue
        real = sp.re(value)
        if 0 < real < 1:
            roots.append(real)
    roots.sort(key=lambda value: float(value))
    return roots


def source_data():
    sys.path.insert(0, str(HERE))
    import build_diag3_pair_global_four_support_invisible_section_lift as event_builder

    base = json.loads(gzip.decompress(BASE.read_bytes()))
    roots = json.loads(gzip.decompress(ROOTS.read_bytes()))
    open_lift = json.loads(OPEN.read_bytes())
    simple = json.loads(SIMPLE.read_bytes())
    invisible = json.loads(INVISIBLE.read_bytes())
    multi = json.loads(MULTI.read_bytes())
    regular = json.loads(REGULAR.read_bytes())
    sequences = event_builder.load_sequences(open_lift)
    completed = {
        row[0] for row in simple["simple_section_lift"]["crossings"]
    } | {
        row[0] for row in invisible["invisible_section_lift"]["completed"]
    } | {
        row[0] for row in multi["multi_section_lift"]["completed"]
    } | {
        row[0] for key in ("unchanged", "same_count")
        for row in regular["regular_residual_section_lift"][key]
    }
    return base, roots, open_lift, simple, invisible, multi, regular, sequences, completed


def main() -> None:
    (
        base,
        roots,
        open_lift,
        simple,
        invisible,
        multi,
        regular,
        sequences,
        completed,
    ) = source_data()
    base_polynomials = [
        sum(
            sp.Integer(term["coefficient"])
            * u ** term["exponent"][0]
            * t ** term["exponent"][1]
            for term in row["polynomial"]
        )
        for row in base["base_factorization"]["catalog"]
    ]
    factor_catalog = base["second_projection"]["catalog"]
    section_rows = roots["root_isolation"]["sections"]
    answer = []
    kind_census = Counter()
    degree_census = Counter()
    total_points = total_strips = 0
    vertical_zero_total = boundary_zero_total = 0
    for section_id, (section, left, right) in enumerate(
        zip(section_rows, sequences[:-1], sequences[1:], strict=True)
    ):
        if section_id in completed:
            continue
        if left == right:
            kind = "unchanged"
        elif len(left) == len(right):
            kind = "same_count"
        else:
            kind = "count_change"
        q_coefficients = factor_catalog[section["factor_id"]]["coefficients_low_to_high"]
        q = sum(sp.Integer(value) * t**degree for degree, value in enumerate(q_coefficients))
        lower, upper = Fraction(section["left"]), Fraction(section["right"])
        alpha = selected_root(q, lower, upper)
        specialized = []
        root_instances = []
        vertical_zero = []
        boundary_zero = {"u=0": [], "u=1": []}
        for base_id, polynomial in enumerate(base_polynomials):
            current = sp.Poly(polynomial.subs(t, alpha), u, extension=alpha)
            specialized.append(current)
            if current.is_zero:
                vertical_zero.append(base_id)
                continue
            if current.eval(0) == 0:
                boundary_zero["u=0"].append(base_id)
            if current.eval(1) == 0:
                boundary_zero["u=1"].append(base_id)
            for root in sympy_interior_roots(current):
                root_instances.append((root, base_id))

        root_instances.sort(key=lambda row: float(row[0]))
        clusters = []
        threshold = sp.Rational(1, 1 << 60)
        for root, base_id in root_instances:
            if not clusters or abs(root - clusters[-1][0][0]) > threshold:
                clusters.append([])
            clusters[-1].append((root, base_id))
        points = []
        for cluster in clusters:
            owners = sorted(base_id for _root, base_id in cluster)
            if len(owners) != len(set(owners)):
                raise AssertionError("one base factor contributed two roots to one cluster")
            common = specialized[owners[0]].sqf_part()
            for owner in owners[1:]:
                common = sp.gcd(common, specialized[owner].sqf_part())
            if common.degree() <= 0:
                raise AssertionError("numerical cluster lacked an exact common divisor")
            candidate = sum((root for root, _owner in cluster), sp.Integer(0)) / len(cluster)
            common_roots = sympy_interior_roots(common)
            if sum(bool(abs(candidate - root) < threshold) for root in common_roots) != 1:
                raise AssertionError("common divisor did not identify the clustered root")
            point_lower, point_upper = rational_box(candidate)
            if not (0 < point_lower < point_upper < 1):
                raise AssertionError("interior point box left the bounded u interval")
            points.append(
                {
                    "lower": fraction_text(point_lower),
                    "upper": fraction_text(point_upper),
                    "owners": owners,
                }
            )
        if any(Fraction(left["upper"]) >= Fraction(right["lower"]) for left, right in zip(points, points[1:])):
            raise AssertionError("proposed point intervals are not disjoint")

        row = {
            "section_id": section_id,
            "factor_id": section["factor_id"],
            "factor_root_index": section["factor_root_index"],
            "minimal_degree": len(q_coefficients) - 1,
            "kind": kind,
            "left_open_root_instances": len(left),
            "right_open_root_instances": len(right),
            "vertical_zero_factors": vertical_zero,
            "boundary_zero_factors": boundary_zero,
            "section_root_points": len(points),
            "section_u_strips": len(points) + 1,
            "points": points,
        }
        answer.append(row)
        kind_census[kind] += 1
        degree_census[row["minimal_degree"]] += 1
        total_points += len(points)
        total_strips += len(points) + 1
        vertical_zero_total += len(vertical_zero)
        boundary_zero_total += sum(map(len, boundary_zero.values()))
        print(
            "SECTION",
            section_id,
            kind,
            "DEGREE",
            row["minimal_degree"],
            "OPEN",
            len(left),
            len(right),
            "POINTS",
            len(points),
            "VERTICAL",
            len(vertical_zero),
            "BOUNDARY",
            sum(map(len, boundary_zero.values())),
            flush=True,
        )

    if len(answer) != 28 or kind_census != {
        "unchanged": 7,
        "same_count": 7,
        "count_change": 14,
    }:
        raise AssertionError("final section census changed")
    semantic_payload = {
        "regular_residual_section_lift_semantic_sha256": regular["semantic_sha256"],
        "sections": answer,
    }
    record = {
        "format": FORMAT,
        "status": "PROVED",
        "scope": {
            "all_1693_algebraic_t_section_base_lifts": "COMPLETE",
            "final_28_algebraic_t_section_base_lifts": "COMPLETE",
            "v_fiber_lift": "NOT_YET_CONSTRUCTED",
            "global_parent_cell_coverage": "NOT_CLAIMED",
            "honest_9dvl_score": "2/9",
        },
        "source": {
            "base_projection_semantic_sha256": base["semantic_sha256"],
            "root_isolation_semantic_sha256": roots["semantic_sha256"],
            "open_sector_lift_semantic_sha256": open_lift["semantic_sha256"],
            "simple_section_lift_semantic_sha256": simple["semantic_sha256"],
            "invisible_section_lift_semantic_sha256": invisible["semantic_sha256"],
            "multi_section_lift_semantic_sha256": multi["semantic_sha256"],
            "regular_residual_section_lift_semantic_sha256": regular["semantic_sha256"],
        },
        "final_section_lift": {
            "completed_sections": len(answer),
            "section_kind_census": dict(sorted(kind_census.items())),
            "minimal_degree_census": {str(key): value for key, value in sorted(degree_census.items())},
            "vertical_zero_factor_incidences": vertical_zero_total,
            "boundary_zero_factor_incidences": boundary_zero_total,
            "section_u_root_points": total_points,
            "section_u_strips": total_strips,
            "section_base_cells": total_points + total_strips,
            "interval_bits": INTERVAL_BITS,
            "sections_sha256": digest(answer),
            "sections": answer,
        },
        "remaining_frontier": {
            "remaining_algebraic_t_sections": 0,
            "next_pair_obligations": [
                "lift the 22 original walls: one base-only, 20 linear in v, and one quadratic in v",
                "glue both covered square-pyramid supports to completed faces",
                "attach signature labels and replay middle-rank exactness",
            ],
        },
        "semantic_sha256": digest(semantic_payload),
        "resource_effect": {
            "final_section_cell_ceiling": 10_000,
            "actual_final_section_cells": total_points + total_strips,
            "ceiling_not_triggered": total_points + total_strips < 10_000,
            "next_stage": "lift the 22 original walls (one base-only, 20 linear in v, and one quadratic in v) over the complete 1693-section plus 1694-sector base CAD",
        },
        "generator_dependency": {
            "python": sys.version.split()[0],
            "sympy": sp.__version__,
            "independent_verifier": "STANDARD_LIBRARY_NUMBER_FIELD_STURM",
        },
        "theorem_effect": "All 1,693 algebraic t-section base lifts are complete, including the final 28 higher-multiplicity and count-changing fibers; v lifting, global gluing, signature labels, middle-rank replay, and the diagonal-three invariant remain open; honest 9DVL score remains 2/9.",
    }
    OUTPUT.write_text(
        json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="ascii",
    )
    print("WROTE", OUTPUT)
    print("COMPLETED", len(answer), dict(sorted(kind_census.items())))
    print("SECTION_CELLS", total_points, "+", total_strips, "=", total_points + total_strips)
    print("REMAINING_ALGEBRAIC_T_SECTIONS 0")


if __name__ == "__main__":
    main()
