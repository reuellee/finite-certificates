#!/usr/bin/env python3
"""Produce the preregistered exact local triple-roadmap canary.

This is producer code.  The trust-boundary replay is deliberately implemented
without importing this module in ``verify_diag3_triple_local_roadmap_canary``.
All interval bounds use exact rational direct-monomial arithmetic; floating
point is never consulted.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG9_GRAPH_global_factor_census as factors  # noqa: E402
import verify_diag3_triple_boundary_stratification as boundary  # noqa: E402


REGISTRATION = HERE / "data/DIAG3_TRIPLE_LOCAL_ROADMAP_REGISTRATION.json"
SYSTEM = HERE / "data/DIAG3_triple_fullspace_critical_h1.json"
SOURCE_GATE = HERE / "data/DIAG3_triple_fullspace_feasibility_gate.json"
OUTPUT = HERE / "data/DIAG3_TRIPLE_LOCAL_ROADMAP_CANARY.json"
SCHEMA = "diag3-triple-local-roadmap-canary-v1"
ZERO = (0,) * 9


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def parse_fraction(value: str) -> Fraction:
    return Fraction(value)


def encode_fraction(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def evaluate(polynomial, point) -> Fraction:
    total = Fraction(0)
    for monomial, coefficient in polynomial.items():
        term = Fraction(coefficient)
        for value, exponent in zip(point, monomial):
            if exponent:
                term *= value**exponent
        total += term
    return total


def multiply_interval(left, right):
    products = (
        left[0] * right[0],
        left[0] * right[1],
        left[1] * right[0],
        left[1] * right[1],
    )
    return min(products), max(products)


def power_interval(lower: Fraction, upper: Fraction, exponent: int):
    if exponent == 0:
        return Fraction(1), Fraction(1)
    candidates = [lower**exponent, upper**exponent]
    if lower <= 0 <= upper and exponent % 2 == 0:
        candidates.append(Fraction(0))
    return min(candidates), max(candidates)


def direct_interval(polynomial, center, radius):
    lower = Fraction(0)
    upper = Fraction(0)
    for monomial, coefficient in polynomial.items():
        term = (Fraction(coefficient), Fraction(coefficient))
        for value, exponent in zip(center, monomial):
            term = multiply_interval(
                term,
                power_interval(value - radius, value + radius, exponent),
            )
        lower += term[0]
        upper += term[1]
    return lower, upper


def determinant(matrix):
    size = len(matrix)
    if size == 1:
        return matrix[0][0]
    answer = {}
    for column in range(size):
        minor = tuple(
            tuple(row[index] for index in range(size) if index != column)
            for row in matrix[1:]
        )
        term = factors.multiply(matrix[0][column], determinant(minor))
        answer = factors.add(answer, term, -1 if column & 1 else 1)
    return answer


def all_parent_brackets():
    matrix = factors.normalized_matrix()
    answer = []
    for columns in combinations(range(8), 4):
        polynomial = determinant(
            tuple(
                tuple(matrix[row][column] for column in columns)
                for row in range(4)
            )
        )
        answer.append(("".join(str(column + 1) for column in columns), polynomial))
    if len(answer) != 70:
        raise AssertionError("normalized parent bracket census changed")
    return tuple(answer)


def polynomial_digest(domain: bytes, polynomial) -> str:
    digest = hashlib.sha256(domain + b"\0")
    for monomial, coefficient in sorted(polynomial.items()):
        value = Fraction(coefficient)
        digest.update(bytes(monomial))
        digest.update(value.numerator.to_bytes((abs(value.numerator).bit_length() + 8) // 8, "big", signed=True))
        digest.update(b"/")
        digest.update(value.denominator.to_bytes((value.denominator.bit_length() + 7) // 8, "big"))
        digest.update(b";")
    return digest.hexdigest()


def sign(interval):
    lower, upper = interval
    if lower > 0:
        return 1
    if upper < 0:
        return -1
    return 0


def main():
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    if registration["schema"] != "diag3-triple-local-roadmap-registration-v1":
        raise AssertionError("registration schema changed")
    if sha256(SYSTEM) != registration["authenticated_inputs"]["critical_system_sha256"]:
        raise AssertionError("critical-system source changed after registration")
    source_gate = json.loads(SOURCE_GATE.read_text(encoding="utf-8"))
    if source_gate["semantic_sha256"] != registration["authenticated_inputs"]["source_gate_semantic_sha256"]:
        raise AssertionError("source gate changed after registration")

    source = json.loads(SYSTEM.read_text(encoding="ascii"))
    residuals = tuple(
        boundary.decode_terms(record["terms"])
        for record in source["equations"][:3]
    )
    center = tuple(parse_fraction(value) for value in registration["fixed_box"]["center"])
    radius = parse_fraction(registration["fixed_box"]["radius"])
    center_values = tuple(evaluate(polynomial, center) for polynomial in residuals)
    if center_values != (0, 0, 0):
        raise AssertionError("registered center is not an exact triple zero")

    brackets = []
    for label, polynomial in all_parent_brackets():
        interval = direct_interval(polynomial, center, radius)
        orientation = sign(interval)
        if not orientation:
            raise AssertionError(f"parent bracket {label} is not sign-definite")
        brackets.append(
            {
                "label": label,
                "terms": len(polynomial),
                "polynomial_sha256": polynomial_digest(b"diag3-local-parent-bracket-v1", polynomial),
                "interval": [encode_fraction(interval[0]), encode_fraction(interval[1])],
                "sign": orientation,
            }
        )

    columns = tuple(registration["fixed_projection"]["fiber_columns_zero_based"])
    projection_minor = boundary.jacobian_minor(residuals, columns)
    projection_interval = direct_interval(projection_minor, center, radius)
    projection_sign = sign(projection_interval)
    if not projection_sign:
        raise AssertionError("registered projection minor is not sign-definite")

    certificate = {
        "schema": SCHEMA,
        "status": "PROVED_LOCAL_BOUNDARY_COVERAGE",
        "registration_sha256": sha256(REGISTRATION),
        "authenticated_sources": {
            "critical_system_sha256": sha256(SYSTEM),
            "source_gate_semantic_sha256": source_gate["semantic_sha256"],
            "named_factor_presentation": source["named_presentation"],
            "canonical_unresolved_row": source_gate["canonical_row"],
        },
        "scope": registration["declared_scope"],
        "box": {
            **registration["fixed_box"],
            "closed": True,
            "all_coordinate_intervals_nonzero": all(
                not (value - radius <= 0 <= value + radius) for value in center
            ),
        },
        "exact_zero_witness": {
            "point": registration["fixed_box"]["center"],
            "residual_values": [encode_fraction(value) for value in center_values],
            "strictly_inside_box": True,
        },
        "parent_cell": {
            "normalized_brackets": len(brackets),
            "sign_definite_brackets": sum(record["sign"] != 0 for record in brackets),
            "records": brackets,
            "consequence": "the entire closed box lies in one uniform normalized parent cell",
        },
        "projection": {
            **registration["fixed_projection"],
            "jacobian_minor_terms": len(projection_minor),
            "jacobian_minor_sha256": polynomial_digest(b"diag3-local-projection-minor-v1", projection_minor),
            "jacobian_minor_at_center": encode_fraction(evaluate(projection_minor, center)),
            "jacobian_minor_interval": [
                encode_fraction(projection_interval[0]),
                encode_fraction(projection_interval[1]),
            ],
            "jacobian_minor_sign": projection_sign,
            "critical_points_in_box": 0,
        },
        "boundary_accounting": {
            "coordinate_faces": 18,
            "internal_seams": 0,
            "faces_accounted": [
                {"variable": variable, "side": side}
                for variable in registration["fixed_box"]["variables"]
                for side in ("lower", "upper")
            ],
            "claimed_parent_infinity_faces": 0,
            "claimed_parent_wall_faces": 0,
        },
        "proof_consequence": registration["proof_consequence_if_accepted"],
        "non_consequences": registration["non_consequences"],
        "theorem_accounting": {
            "final_unresolved_triple_orbits_before": 1_162_302,
            "final_unresolved_triple_orbits_after": 1_162_302,
            "score_before": "2/9",
            "score_after": "2/9",
        },
        "hostile_mutations": [
            "source_digest",
            "named_presentation",
            "canonical_row",
            "center_coordinate",
            "box_radius",
            "parent_bracket_count",
            "parent_bracket_interval",
            "parent_bracket_sign",
            "projection_columns",
            "projection_minor_digest",
            "projection_minor_interval",
            "boundary_face_count",
            "scope_orbit_transport",
            "theorem_score",
        ],
    }
    semantic_payload = dict(certificate)
    certificate["semantic_sha256"] = hashlib.sha256(
        json.dumps(semantic_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    OUTPUT.write_text(json.dumps(certificate, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print("PASS exact triple zero at registered rational center")
    print("PASS 70/70 parent brackets sign-definite on radius-1/128 box")
    print(
        "PASS projection minor",
        columns,
        "terms=",
        len(projection_minor),
        "interval=",
        tuple(map(encode_fraction, projection_interval)),
    )
    print("RESULT every restricted triple-zero component meets one of 18 box faces")
    print("SCOPE one box / one named presentation / no orbit transport / ledger 2/9")


if __name__ == "__main__":
    main()
