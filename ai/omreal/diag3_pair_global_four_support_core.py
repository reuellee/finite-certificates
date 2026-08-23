#!/usr/bin/env python3
"""Exact parent-domain and interior-wall gate for the two first 4D supports."""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import verify_diag3_pair_global_face_bernstein_atlas as bernstein  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402
from exact_semialgebraic import (  # noqa: E402
    affine_pullback,
    canonical_integer,
    evaluate,
    simplex_bernstein_control,
)


FORMAT = "diag3-pair-global-row2599-four-support-gate-v1"
SUPPORTS = ((3, 1, 15), (3, 3, 7))
PYRAMID_VERTICES = {
    "o": (0, 0, 0),
    "a": (1, 0, 0),
    "h": (0, 0, 1),
    "ah": (1, 0, 1),
    "top": (1, 1, 1),
}
PYRAMID_TETRAHEDRA = (
    (PYRAMID_VERTICES["o"], PYRAMID_VERTICES["a"], PYRAMID_VERTICES["ah"], PYRAMID_VERTICES["top"]),
    (PYRAMID_VERTICES["o"], PYRAMID_VERTICES["h"], PYRAMID_VERTICES["ah"], PYRAMID_VERTICES["top"]),
)
SHARED_TRIANGLE = (
    PYRAMID_VERTICES["o"],
    PYRAMID_VERTICES["ah"],
    PYRAMID_VERTICES["top"],
)
FACETS = (
    ("g=0", {(0, 1, 0): 1}, 1, 1),
    ("a=1", {(0, 0, 0): 1, (1, 0, 0): -1}, 0, -1),
    ("h=1", {(0, 0, 0): 1, (0, 0, 1): -1}, 2, -1),
    ("a=g", {(1, 0, 0): 1, (0, 1, 0): -1}, 0, 1),
    ("h=g", {(0, 0, 1): 1, (0, 1, 0): -1}, 2, 1),
)


def fraction_text(value):
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def canonical(polynomial):
    return {exponent: coefficient for exponent, coefficient in canonical_integer(polynomial)}


def polynomial_rows(polynomial):
    return [
        {"exponent": list(exponent), "coefficient": fraction_text(coefficient)}
        for exponent, coefficient in sorted(polynomial.items())
    ]


def degree(polynomial):
    return max(map(sum, polynomial)) if polynomial else -1


def restrict(polynomial, face):
    multidegree = tuple(
        max(sum(term[index] for index in variables) for term in polynomial)
        for variables in bernstein.GROUPS
    )
    return {
        exponent: coefficient
        for exponent, coefficient in polynomial.items()
        if all(
            mask & ~allowed == 0
            for mask, allowed in zip(
                bernstein.term_support(exponent, multidegree), face, strict=True
            )
        )
    }


def collapse_parent_equality(polynomial, face):
    answer = Counter()
    for exponent, coefficient in polynomial.items():
        exponent = list(exponent)
        if face == (3, 1, 15):
            exponent[6] += exponent[8]
            exponent[8] = 0
        elif face == (3, 3, 7):
            exponent[6] += exponent[3]
            exponent[3] = 0
        else:
            raise ValueError("unknown four-support face")
        answer[(exponent[0], exponent[6], exponent[7])] += coefficient
    return {exponent: coefficient for exponent, coefficient in answer.items() if coefficient}


def strip_monomial(polynomial):
    minimum = tuple(min(exponent[axis] for exponent in polynomial) for axis in range(3))
    stripped = {
        tuple(exponent[axis] - minimum[axis] for axis in range(3)): coefficient
        for exponent, coefficient in polynomial.items()
    }
    return canonical(stripped), minimum


def divide_linear(polynomial, factor, axis, leading):
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
            output = tuple(target[index] + exponent[index] for index in range(3))
            work[output] -= coefficient * value
            if not work[output]:
                del work[output]
    return dict(quotient), dict(work)


def strip_facets(polynomial):
    current = canonical(polynomial)
    factors = Counter()
    changed = True
    while changed:
        changed = False
        for name, factor, axis, leading in FACETS:
            quotient, remainder = divide_linear(current, factor, axis, leading)
            if not remainder:
                current = canonical(quotient)
                factors[name] += 1
                changed = True
                break
    return current, dict(sorted(factors.items()))


def divide_polynomial(dividend, divisor):
    work = Counter({term: Fraction(value) for term, value in dividend.items()})
    quotient = Counter()
    remainder = Counter()
    divisor_lead = max(divisor)
    divisor_coefficient = Fraction(divisor[divisor_lead])
    while work:
        lead = max(work)
        coefficient = work[lead]
        if all(lead[index] >= divisor_lead[index] for index in range(3)):
            exponent = tuple(lead[index] - divisor_lead[index] for index in range(3))
            scale = coefficient / divisor_coefficient
            quotient[exponent] += scale
            for term, value in divisor.items():
                output = tuple(exponent[index] + term[index] for index in range(3))
                work[output] -= scale * value
                if not work[output]:
                    del work[output]
        else:
            remainder[lead] += coefficient
            del work[lead]
    return dict(quotient), dict(remainder)


def controls_on(polynomial, vertices):
    base = vertices[0]
    target_dimension = len(vertices) - 1
    rows = tuple(
        tuple(
            Fraction(vertices[target + 1][axis] - base[axis])
            for target in range(target_dimension)
        )
        for axis in range(3)
    )
    pulled = affine_pullback(polynomial, base, rows)
    if not pulled:
        return 0, "0" * 64
    controls, _degree = simplex_bernstein_control(pulled)
    signs = {1 if value > 0 else -1 if value < 0 else 0 for value in controls.values()}
    status = 1 if signs <= {0, 1} and 1 in signs else -1 if signs <= {0, -1} and -1 in signs else None
    digest = hashlib.sha256(
        b"diag3-four-support-simplex-controls-v1\0"
        + repr(tuple(sorted(controls.items()))).encode("ascii")
    ).hexdigest()
    return status, digest


def strict_grid():
    return tuple(
        (Fraction(a, 16), Fraction(g, 16), Fraction(h, 16))
        for g in range(1, 16)
        for a in range(g + 1, 16)
        for h in range(g + 1, 16)
    )


STRICT_GRID = strict_grid()


def interior_classification(polynomial):
    signs = {}
    zero = None
    for point in STRICT_GRID:
        value = evaluate(polynomial, point)
        sign = 1 if value > 0 else -1 if value < 0 else 0
        signs.setdefault(sign, point)
        if sign == 0:
            zero = point
            break
    if zero is not None:
        return {
            "status": "INTERIOR_NONEMPTY",
            "witness_kind": "EXACT_ZERO",
            "witness_points": [[fraction_text(value) for value in zero]],
        }
    if -1 in signs and 1 in signs:
        return {
            "status": "INTERIOR_NONEMPTY",
            "witness_kind": "OPPOSITE_SIGNS_ON_INTERIOR_SEGMENT",
            "witness_points": [
                [fraction_text(value) for value in signs[-1]],
                [fraction_text(value) for value in signs[1]],
            ],
        }

    tetra = tuple(controls_on(polynomial, vertices) for vertices in PYRAMID_TETRAHEDRA)
    shared = controls_on(polynomial, SHARED_TRIANGLE)
    statuses = tuple(row[0] for row in tetra) + (shared[0],)
    if None not in statuses and 0 not in statuses and len(set(statuses)) == 1:
        return {
            "status": "INTERIOR_EMPTY",
            "witness_kind": "ONE_SIDED_SIMPLEX_BERNSTEIN",
            "simplex_sign": statuses[0],
            "control_sha256": [row[1] for row in tetra] + [shared[1]],
        }
    raise AssertionError("four-support interior classifier exhausted its exact gates")


def parent_domain(face, parents):
    equality_labels = ("1358", "3578") if face == (3, 1, 15) else ("3478", "3578")
    audits = []
    zero = 0
    for label, target, polynomial, _terms in parents:
        collapsed = collapse_parent_equality(
            {exponent: target * coefficient for exponent, coefficient in restrict(polynomial, face).items()},
            face,
        )
        if not collapsed:
            zero += 1
            audits.append((label, 0))
            continue
        statuses = tuple(controls_on(collapsed, vertices)[0] for vertices in PYRAMID_TETRAHEDRA)
        if any(status not in (0, 1) for status in statuses):
            raise AssertionError(f"parent bracket lacks a nonnegative pyramid certificate: {face} {label}")
        audits.append((label, 1))
    stream = hashlib.sha256(
        b"diag3-four-support-parent-domain-v1\0" + repr((face, audits)).encode("ascii")
    ).hexdigest()
    return {
        "support": list(face),
        "ambient_dimension": 4,
        "parent_dimension": 3,
        "equality": "g=i" if face == (3, 1, 15) else "d=g",
        "opposite_parent_brackets": list(equality_labels),
        "coordinates": ["a", "g", "h"],
        "domain": "0<=g<=a<=1 and 0<=g<=h<=1",
        "parent_brackets_replayed": len(parents),
        "identically_zero_parent_restrictions": zero,
        "nonnegative_parent_restrictions": len(parents) - zero,
        "parent_control_stream_sha256": stream,
    }


def residual_groups(face, polynomials, candidate_ids):
    state = Counter()
    groups = defaultdict(list)
    for factor_id in candidate_ids:
        restricted = restrict(polynomials[factor_id], face)
        if len({1 if value > 0 else -1 for value in restricted.values()}) < 2:
            continue
        collapsed = collapse_parent_equality(restricted, face)
        if not collapsed:
            state["IDENTICALLY_ZERO_ON_PARENT_DOMAIN"] += 1
            continue
        if len({1 if value > 0 else -1 for value in collapsed.values()}) == 1:
            state["ONE_SIGNED_AFTER_PARENT_EQUALITY"] += 1
            continue
        stripped, _monomial = strip_monomial(collapsed)
        groups[tuple(sorted(stripped.items()))].append(factor_id)
        state["MIXED_AFTER_PARENT_EQUALITY"] += 1

    reports = {}
    facet_census = Counter()
    factor_status = Counter()
    for key, factor_ids in sorted(groups.items()):
        reduced, facets = strip_facets(dict(key))
        facet_census.update(facets)
        classification = interior_classification(reduced)
        classification["factor_count"] = len(factor_ids)
        classification["factor_ids"] = factor_ids
        classification["parent_reduced_polynomial"] = polynomial_rows(dict(key))
        classification["facet_factors"] = facets
        classification["interior_remainder"] = polynomial_rows(reduced)
        reports[key] = (reduced, classification)
        factor_status[classification["status"]] += len(factor_ids)

    state.update(factor_status)
    if sum(state[name] for name in (
        "IDENTICALLY_ZERO_ON_PARENT_DOMAIN",
        "ONE_SIGNED_AFTER_PARENT_EQUALITY",
        "INTERIOR_EMPTY",
        "INTERIOR_NONEMPTY",
    )) != sum(state.values()) - state["MIXED_AFTER_PARENT_EQUALITY"]:
        raise AssertionError("four-support state accounting changed")
    return state, reports, dict(sorted(facet_census.items()))


def positive_factor_quotient(polynomial, empty_polynomials):
    current = canonical(polynomial)
    removed = []
    changed = True
    while changed:
        changed = False
        for divisor in empty_polynomials:
            if degree(divisor) <= 0 or degree(divisor) > degree(current):
                continue
            quotient, remainder = divide_polynomial(current, divisor)
            if not remainder and degree(quotient) < degree(current):
                current = canonical(quotient)
                removed.append(tuple(sorted(divisor.items())))
                changed = True
                break
    return current, removed


def factor_digest(values, domain):
    payload = b"".join(int(value).to_bytes(4, "little") for value in sorted(values))
    return hashlib.sha256(domain + b"\0" + payload).hexdigest()


def build_record():
    records = [json.loads(line) for line in gate.CATALOG.read_text().splitlines() if line]
    parents, parent_sign_digest = gate.parent_polynomials(records[gate.PARENT])
    candidate_ids = gate.parse_candidates()
    _occurrences, _occurrence_factor, polynomials = labeled.factor_polynomials()

    domains = [parent_domain(face, parents) for face in SUPPORTS]
    analyses = []
    all_reports = {}
    for face in SUPPORTS:
        state, reports, facet_census = residual_groups(face, polynomials, candidate_ids)
        all_reports[face] = reports
        analyses.append((face, state, reports, facet_census))

    empty_polynomials = {
        tuple(sorted(reduced.items())): reduced
        for reports in all_reports.values()
        for reduced, report in reports.values()
        if report["status"] == "INTERIOR_EMPTY"
    }
    empty_order = [
        empty_polynomials[key]
        for key in sorted(empty_polynomials, key=lambda item: (degree(dict(item)), item))
    ]

    support_rows = []
    global_active = {}
    active_factor_union = set()
    classification_stream = hashlib.sha256(b"diag3-four-support-factor-classification-v1\0")
    for face, state, reports, facet_census in analyses:
        final = defaultdict(list)
        active_factors = set()
        group_status = Counter()
        for source_key, (reduced, report) in reports.items():
            group_status[report["status"]] += 1
            for factor_id in report["factor_ids"]:
                classification_stream.update(bytes(face))
                classification_stream.update(factor_id.to_bytes(4, "little"))
                classification_stream.update(report["status"].encode("ascii") + b"\0")
            if report["status"] != "INTERIOR_NONEMPTY":
                continue
            quotient, removed = positive_factor_quotient(reduced, empty_order)
            key = tuple(sorted(quotient.items()))
            final[key].append({
                "source_polynomial": polynomial_rows(dict(source_key)),
                "positive_factors_removed": len(removed),
                "factor_ids": report["factor_ids"],
            })
            global_active[key] = quotient
            active_factors.update(report["factor_ids"])
        active_factor_union.update(active_factors)
        support_rows.append({
            "support": list(face),
            "ambient_mixed_residual_restrictions": sum(state[name] for name in (
                "IDENTICALLY_ZERO_ON_PARENT_DOMAIN",
                "ONE_SIGNED_AFTER_PARENT_EQUALITY",
                "MIXED_AFTER_PARENT_EQUALITY",
            )),
            "parent_equality_state_census": {
                "identically_zero": state["IDENTICALLY_ZERO_ON_PARENT_DOMAIN"],
                "one_signed": state["ONE_SIGNED_AFTER_PARENT_EQUALITY"],
                "mixed": state["MIXED_AFTER_PARENT_EQUALITY"],
            },
            "distinct_parent_reduced_zero_sets": len(reports),
            "interior_class_census": {
                "empty": group_status["INTERIOR_EMPTY"],
                "nonempty": group_status["INTERIOR_NONEMPTY"],
                "unresolved": 0,
            },
            "interior_factor_census": {
                "empty": state["INTERIOR_EMPTY"],
                "nonempty": state["INTERIOR_NONEMPTY"],
            },
            "facet_factor_census": facet_census,
            "active_interior_factor_ids_sha256": factor_digest(active_factors, b"diag3-four-support-active" + bytes(face)),
            "distinct_active_remainders_before_positive_quotient": group_status["INTERIOR_NONEMPTY"],
            "distinct_active_walls_after_positive_quotient": len(final),
        })

    active_catalog = [
        {"id": index, "polynomial": polynomial_rows(polynomial)}
        for index, (_key, polynomial) in enumerate(sorted(global_active.items()))
    ]
    catalog_digest = hashlib.sha256(
        b"diag3-four-support-active-wall-catalog-v1\0"
        + json.dumps(active_catalog, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    common_parent_reduced = len(set(all_reports[SUPPORTS[0]]) & set(all_reports[SUPPORTS[1]]))
    common_active = len({
        tuple(sorted(positive_factor_quotient(reduced, empty_order)[0].items()))
        for reduced, report in all_reports[SUPPORTS[0]].values()
        if report["status"] == "INTERIOR_NONEMPTY"
    } & {
        tuple(sorted(positive_factor_quotient(reduced, empty_order)[0].items()))
        for reduced, report in all_reports[SUPPORTS[1]].values()
        if report["status"] == "INTERIOR_NONEMPTY"
    })

    return {
        "format": FORMAT,
        "status": "PROVED",
        "scope": {
            "parent_index": gate.PARENT,
            "compactification": "(Delta^3)^3",
            "parent_parameter_coverage": "COMPLETE_ON_BOTH_FIRST_FOUR_SUPPORT_PARENT_CLOSURES",
            "residual_interior_feasibility": "COMPLETE_ON_BOTH_SQUARE_PYRAMIDS",
            "residual_arrangement_cellulation": "NOT_YET_CONSTRUCTED",
            "global_parent_cell_coverage": "NOT_CLAIMED",
            "honest_9dvl_score": "2/9",
        },
        "inputs": {
            "candidate_factor_count": len(candidate_ids),
            "candidate_factor_sha256": gate.CANDIDATE_SHA256,
            "normalized_parent_sign_sha256": parent_sign_digest,
            "parent_face_gate_semantic_sha256": gate.EXPECTED_SEMANTIC,
        },
        "common_square_pyramid": {
            "coordinates": ["a", "g", "h"],
            "domain": "0<=g<=a<=1 and 0<=g<=h<=1",
            "vertices": {name: list(values) for name, values in PYRAMID_VERTICES.items()},
            "tetrahedra": [
                [[fraction_text(value) for value in vertex] for vertex in tetrahedron]
                for tetrahedron in PYRAMID_TETRAHEDRA
            ],
            "tetrahedron_count": len(PYRAMID_TETRAHEDRA),
            "shared_interior_triangle": [list(vertex) for vertex in SHARED_TRIANGLE],
            "boundary_facets": [name for name, _factor, _axis, _leading in FACETS],
            "common_inherited_base": "g=0 is the completed (3,1,5) square split by a=h",
        },
        "parent_domains": domains,
        "support_residual_analyses": support_rows,
        "combined_compression": {
            "ambient_mixed_restrictions": sum(row["ambient_mixed_residual_restrictions"] for row in support_rows),
            "distinct_parent_reduced_zero_sets": len(set(all_reports[SUPPORTS[0]]) | set(all_reports[SUPPORTS[1]])),
            "common_parent_reduced_zero_sets": common_parent_reduced,
            "distinct_active_remainders_before_positive_quotient": len({
                tuple(sorted(reduced.items()))
                for reports in all_reports.values()
                for reduced, report in reports.values()
                if report["status"] == "INTERIOR_NONEMPTY"
            }),
            "distinct_active_walls_after_positive_quotient": len(active_catalog),
            "common_active_walls_after_positive_quotient": common_active,
            "active_interior_factor_union_count": len(active_factor_union),
            "active_interior_factor_union_sha256": factor_digest(active_factor_union, b"diag3-four-support-active-union"),
            "classification_stream_sha256": classification_stream.hexdigest(),
            "active_wall_catalog_sha256": catalog_digest,
            "unresolved_interior_zero_sets": 0,
        },
        "active_wall_catalog": active_catalog,
        "resource_contract": {
            "next_stage": "face-compatible exact arrangement of 22 walls on two tetrahedra per support",
            "maximum_unique_projection_polynomials": 100_000,
            "maximum_atomic_tetrahedra": 1_000_000,
            "stop_rule": "emit BOUNDED_NO_GO with exact growth frontier before either ceiling; do not fall back to sample adjacency or the retired single-source cube",
        },
        "theorem_effect": "The first two nominally four-dimensional support tasks are coverage-certified three-dimensional square pyramids; 8017 mixed restrictions reduce to 22 exact interior wall equations, but their arrangement and the global pair complex remain open; honest 9DVL score remains 2/9.",
    }
