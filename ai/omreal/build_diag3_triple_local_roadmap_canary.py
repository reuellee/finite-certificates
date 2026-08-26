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
ROW2599_PARENT_CATALOG = HERE / "certs_4_8.jsonl"
OUTPUT = HERE / "data/DIAG3_TRIPLE_LOCAL_ROADMAP_CANARY.json"
SCHEMA = "diag3-triple-local-roadmap-canary-v1"
ZERO = (0,) * 9
REGISTRATION_SHA256 = "94224ab5f5f64d8a7e14e3d5d382c5cdc96292d9a455520c3c76e003b77eddb3"
REGISTRATION_SCHEMA = "diag3-triple-local-roadmap-registration-v1"
REGISTRATION_STATUS = "REGISTERED_BEFORE_FORMAL_CERTIFICATE_RUN"
CRITICAL_SYSTEM_SHA256 = "c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8"
SOURCE_GATE_RAW_SHA256 = "8ad62abdd3bd7d9bc14e5bfec3e407f3c07fd740a5475d1243e8dbb9e08d8692"
SOURCE_GATE_SEMANTIC_SHA256 = "874c4895ae17843c6827c1c3a8d528eac0b45fc35dedc9159e4f447786ed2ace"
SOURCE_GATE_VERIFY_COMMAND = (
    "PYTHONDONTWRITEBYTECODE=1 python "
    "ai/omreal/verify_diag3_triple_fullspace_feasibility_gate.py"
)
ROW2599_DIRECT_PARENT_SIGNS = tuple(
    1 if bit == "1" else -1
    for bit in "1111100000000011111111100001111111100000000111111000000000001000011111"
)
ROW2599_DIRECT_PARENT_SIGN_SHA256 = "da921eb7d3a24d2fb642d966c1c1a3eb0159e98e2e16583ed05089915e561e4d"
ROW2599_PARENT_CATALOG_SHA256 = "c55e805d60d8086bcb84a312f2103a9973fc2691d0fd97f3d9a1d9809d2b163b"
ROW2599_NORMALIZED_PARENT_SIGN_SHA256 = "1d9b940e2bb954b5c69bcee8b2346f9554b2e15589ea4c5b3c3f8e1e943de701"
ROW2599_PARENT_GATE_VERIFY_COMMAND = (
    "PYTHONDONTWRITEBYTECODE=1 python "
    "ai/omreal/verify_diag3_pair_global_parent_face_gate.py"
)
THEOREM_EFFECT = (
    "A nonvacuous smooth local triple-zero compiler fixture is proved in one "
    "uniform parent chamber distinct from row 2599, but only artificial "
    "box-boundary reach is shown; no complete orbit, genuine parent boundary, "
    "or invariant obligation is covered, so the honest 9DVL score remains 2/9."
)


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
    row2599_sign_digest = hashlib.sha256(
        b"diag3-row2599-direct-parent-signs-v1\0"
        + bytes(int(value > 0) for value in ROW2599_DIRECT_PARENT_SIGNS)
    ).hexdigest()
    if row2599_sign_digest != ROW2599_DIRECT_PARENT_SIGN_SHA256:
        raise AssertionError("row-2599 direct parent-sign pin changed")
    if sha256(ROW2599_PARENT_CATALOG) != ROW2599_PARENT_CATALOG_SHA256:
        raise AssertionError("row-2599 parent catalog changed")
    if sha256(REGISTRATION) != REGISTRATION_SHA256:
        raise AssertionError("preregistration raw digest changed")
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    if registration["schema"] != REGISTRATION_SCHEMA:
        raise AssertionError("preregistration schema changed")
    if registration["status"] != REGISTRATION_STATUS:
        raise AssertionError("preregistration status changed")
    if sha256(SYSTEM) != CRITICAL_SYSTEM_SHA256:
        raise AssertionError("critical-system raw digest changed")
    if registration["authenticated_inputs"]["critical_system_sha256"] != CRITICAL_SYSTEM_SHA256:
        raise AssertionError("critical-system source changed after registration")
    source_gate = json.loads(SOURCE_GATE.read_text(encoding="utf-8"))
    if sha256(SOURCE_GATE) != SOURCE_GATE_RAW_SHA256:
        raise AssertionError("source-mapping gate raw digest changed")
    if source_gate["semantic_sha256"] != SOURCE_GATE_SEMANTIC_SHA256:
        raise AssertionError("source-mapping gate semantic digest changed")
    if registration["authenticated_inputs"]["source_gate_semantic_sha256"] != SOURCE_GATE_SEMANTIC_SHA256:
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

    if len(ROW2599_DIRECT_PARENT_SIGNS) != len(brackets):
        raise AssertionError("row-2599 parent-sign reference changed")
    row2599_mismatches = [
        record["label"]
        for record, row2599_sign in zip(brackets, ROW2599_DIRECT_PARENT_SIGNS, strict=True)
        if record["sign"] != row2599_sign
    ]
    if len(row2599_mismatches) != 29:
        raise AssertionError("local box unexpectedly entered row-2599 parent cell")

    columns = tuple(registration["fixed_projection"]["fiber_columns_zero_based"])
    projection_minor = boundary.jacobian_minor(residuals, columns)
    projection_interval = direct_interval(projection_minor, center, radius)
    projection_sign = sign(projection_interval)
    if not projection_sign:
        raise AssertionError("registered projection minor is not sign-definite")

    certificate = {
        "schema": SCHEMA,
        "status": "PROVED_LOCAL_BOUNDARY_COVERAGE",
        "registration_sha256": REGISTRATION_SHA256,
        "authenticated_sources": {
            "critical_system_sha256": CRITICAL_SYSTEM_SHA256,
            "source_mapping_gate": {
                "path": "ai/omreal/data/DIAG3_triple_fullspace_feasibility_gate.json",
                "raw_sha256": SOURCE_GATE_RAW_SHA256,
                "semantic_sha256": SOURCE_GATE_SEMANTIC_SHA256,
                "verification_command": SOURCE_GATE_VERIFY_COMMAND,
                "accepted_dependency_scope": (
                    "named presentation to canonical unresolved-row mapping only"
                ),
            },
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
            "row2599_comparison": {
                "reference_parent_index": 2599,
                "reference_catalog_sha256": ROW2599_PARENT_CATALOG_SHA256,
                "reference_normalized_parent_sign_sha256": ROW2599_NORMALIZED_PARENT_SIGN_SHA256,
                "reference_direct_parent_sign_sha256": ROW2599_DIRECT_PARENT_SIGN_SHA256,
                "reference_verification_command": ROW2599_PARENT_GATE_VERIFY_COMMAND,
                "sign_mismatch_count": len(row2599_mismatches),
                "sign_mismatch_labels": row2599_mismatches,
                "same_uniform_parent_cell": False,
                "consequence": "the certified box is not in the row-2599 parent chamber",
            },
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
            "geometric_consequence": (
                "the triple-zero set is smooth of dimension six near its box "
                "intersection and projection to the six base variables is a local "
                "diffeomorphism there"
            ),
        },
        "topological_argument": {
            "boundary_avoiding_component_is_smooth": True,
            "boundary_avoiding_component_is_open_in_the_smooth_zero_set": True,
            "projected_component_image_is_nonempty": True,
            "projected_component_image_is_open_in_R6": True,
            "boundary_avoiding_component_is_compact": True,
            "projected_component_image_is_compact": True,
            "contradiction": "no nonempty subset of R6 is both open and compact",
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
            "face_classification": "ARTIFICIAL_SCOPE_BOUNDARY_ONLY",
        },
        "proof_consequence": registration["proof_consequence_if_accepted"],
        "non_consequences": registration["non_consequences"],
        "theorem_accounting": {
            "final_unresolved_triple_orbits_before": 1_162_302,
            "final_unresolved_triple_orbits_after": 1_162_302,
            "score_before": "2/9",
            "score_after": "2/9",
        },
        "theorem_effect": THEOREM_EFFECT,
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
            "parent_infinity_claim",
            "scope_orbit_transport",
            "coupled_registration_global_rewrite",
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
