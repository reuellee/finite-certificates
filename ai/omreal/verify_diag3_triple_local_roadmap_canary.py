#!/usr/bin/env python3
"""Independent exact replay of the local triple-roadmap canary.

The verifier parses the authenticated residual source, reconstructs the
normalized 4-by-8 parent matrix and all 70 brackets, differentiates the three
residuals, forms the fixed projection minor, and recomputes every rational
interval.  It does not import the producer or any producer-side polynomial
implementation.
"""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import hashlib
from itertools import combinations, permutations
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
REGISTRATION = HERE / "data/DIAG3_TRIPLE_LOCAL_ROADMAP_REGISTRATION.json"
SYSTEM = HERE / "data/DIAG3_triple_fullspace_critical_h1.json"
SOURCE_GATE = HERE / "data/DIAG3_triple_fullspace_feasibility_gate.json"
CERTIFICATE = HERE / "data/DIAG3_TRIPLE_LOCAL_ROADMAP_CANARY.json"
SCHEMA = "diag3-triple-local-roadmap-canary-v1"
VARIABLES = tuple("abcdefghi")
ZERO = (0,) * 9


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def fraction(value) -> Fraction:
    return Fraction(value)


def encoded(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def clean(polynomial):
    return {monomial: coefficient for monomial, coefficient in polynomial.items() if coefficient}


def add(left, right, right_scale=1):
    answer = dict(left)
    for monomial, coefficient in right.items():
        answer[monomial] = answer.get(monomial, Fraction(0)) + right_scale * coefficient
        if not answer[monomial]:
            del answer[monomial]
    return answer


def multiply(left, right):
    answer = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial = tuple(x + y for x, y in zip(left_monomial, right_monomial))
            answer[monomial] = answer.get(monomial, Fraction(0)) + left_coefficient * right_coefficient
    return clean(answer)


def derivative(polynomial, variable):
    answer = {}
    for monomial, coefficient in polynomial.items():
        exponent = monomial[variable]
        if exponent:
            derived = list(monomial)
            derived[variable] -= 1
            answer[tuple(derived)] = coefficient * exponent
    return clean(answer)


def determinant(matrix):
    size = len(matrix)
    answer = {}
    for permutation in permutations(range(size)):
        inversions = sum(
            permutation[left] > permutation[right]
            for left in range(size)
            for right in range(left + 1, size)
        )
        term = {ZERO: Fraction(-1 if inversions & 1 else 1)}
        for row in range(size):
            term = multiply(term, matrix[row][permutation[row]])
        answer = add(answer, term)
    return clean(answer)


def decode_polynomial(raw_terms):
    answer = {}
    for coefficient, exponent in raw_terms:
        monomial = tuple(map(int, exponent))
        if len(monomial) != 9 or monomial in answer or not coefficient:
            raise AssertionError("invalid source polynomial encoding")
        answer[monomial] = Fraction(coefficient)
    return answer


def coordinate(index):
    monomial = [0] * 9
    monomial[index] = 1
    return {tuple(monomial): Fraction(1)}


def normalized_matrix():
    one = {ZERO: Fraction(1)}
    zero = {}
    a, b, c, d, e, f, g, h, i = tuple(coordinate(index) for index in range(9))
    return (
        (one, zero, zero, zero, one, one, one, one),
        (zero, one, zero, zero, one, a, d, g),
        (zero, zero, one, zero, one, b, e, h),
        (zero, zero, zero, one, one, c, f, i),
    )


def parent_brackets():
    matrix = normalized_matrix()
    answer = []
    for columns in combinations(range(8), 4):
        square = tuple(tuple(matrix[row][column] for column in columns) for row in range(4))
        answer.append(("".join(str(column + 1) for column in columns), determinant(square)))
    if len(answer) != 70 or len({label for label, _ in answer}) != 70:
        raise AssertionError("independent parent-bracket census changed")
    return tuple(answer)


def jacobian_minor(residuals, columns):
    return determinant(
        tuple(
            tuple(derivative(residual, column) for column in columns)
            for residual in residuals
        )
    )


def evaluate(polynomial, point):
    total = Fraction(0)
    for monomial, coefficient in polynomial.items():
        term = coefficient
        for value, exponent in zip(point, monomial):
            if exponent:
                term *= value**exponent
        total += term
    return total


def product_interval(left, right):
    candidates = (
        left[0] * right[0], left[0] * right[1],
        left[1] * right[0], left[1] * right[1],
    )
    return min(candidates), max(candidates)


def power_interval(lower, upper, exponent):
    if not exponent:
        return Fraction(1), Fraction(1)
    candidates = [lower**exponent, upper**exponent]
    if lower <= 0 <= upper and exponent % 2 == 0:
        candidates.append(Fraction(0))
    return min(candidates), max(candidates)


def direct_interval(polynomial, center, radius):
    result = (Fraction(0), Fraction(0))
    for monomial, coefficient in polynomial.items():
        term = (coefficient, coefficient)
        for value, exponent in zip(center, monomial):
            term = product_interval(term, power_interval(value - radius, value + radius, exponent))
        result = result[0] + term[0], result[1] + term[1]
    return result


def interval_sign(interval):
    if interval[0] > 0:
        return 1
    if interval[1] < 0:
        return -1
    return 0


def polynomial_digest(domain: bytes, polynomial):
    digest = hashlib.sha256(domain + b"\0")
    for monomial, coefficient in sorted(polynomial.items()):
        value = Fraction(coefficient)
        digest.update(bytes(monomial))
        digest.update(value.numerator.to_bytes((abs(value.numerator).bit_length() + 8) // 8, "big", signed=True))
        digest.update(b"/")
        digest.update(value.denominator.to_bytes((value.denominator.bit_length() + 7) // 8, "big"))
        digest.update(b";")
    return digest.hexdigest()


def semantic_digest(candidate):
    payload = dict(candidate)
    payload.pop("semantic_sha256", None)
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def verify_candidate(candidate):
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    source = json.loads(SYSTEM.read_text(encoding="ascii"))
    source_gate = json.loads(SOURCE_GATE.read_text(encoding="utf-8"))
    if candidate["schema"] != SCHEMA or candidate["status"] != "PROVED_LOCAL_BOUNDARY_COVERAGE":
        raise AssertionError("certificate schema or status changed")
    if candidate["registration_sha256"] != sha256(REGISTRATION):
        raise AssertionError("registration digest changed")
    if sha256(SYSTEM) != registration["authenticated_inputs"]["critical_system_sha256"]:
        raise AssertionError("critical source no longer matches registration")
    if source_gate["semantic_sha256"] != registration["authenticated_inputs"]["source_gate_semantic_sha256"]:
        raise AssertionError("source gate no longer matches registration")
    authenticated = candidate["authenticated_sources"]
    expected_authenticated = {
        "critical_system_sha256": sha256(SYSTEM),
        "source_gate_semantic_sha256": source_gate["semantic_sha256"],
        "named_factor_presentation": source["named_presentation"],
        "canonical_unresolved_row": source_gate["canonical_row"],
    }
    if authenticated != expected_authenticated:
        raise AssertionError("authenticated source accounting changed")
    if source["named_presentation"] != registration["declared_scope"]["named_factor_presentation"]:
        raise AssertionError("named presentation no longer matches registration")
    if source_gate["canonical_row"] != registration["declared_scope"]["canonical_unresolved_row"]:
        raise AssertionError("canonical row no longer matches registration")
    if candidate["scope"] != registration["declared_scope"]:
        raise AssertionError("declared scope changed")
    if candidate["scope"]["orbit_transport_claimed"] or candidate["scope"]["s8_sign_transport_claimed"]:
        raise AssertionError("local certificate was promoted across an unaudited orbit")

    residuals = tuple(decode_polynomial(record["terms"]) for record in source["equations"][:3])
    expected_box = {**registration["fixed_box"], "closed": True, "all_coordinate_intervals_nonzero": True}
    if candidate["box"] != expected_box:
        raise AssertionError("registered box changed")
    center = tuple(fraction(value) for value in candidate["box"]["center"])
    radius = fraction(candidate["box"]["radius"])
    if len(center) != 9 or radius <= 0:
        raise AssertionError("invalid box dimensions")
    if any(value - radius <= 0 <= value + radius for value in center):
        raise AssertionError("a coordinate interval crosses zero")
    residual_values = tuple(evaluate(polynomial, center) for polynomial in residuals)
    if residual_values != (0, 0, 0):
        raise AssertionError("center is not an exact triple-zero witness")
    witness = candidate["exact_zero_witness"]
    if witness != {
        "point": candidate["box"]["center"],
        "residual_values": ["0", "0", "0"],
        "strictly_inside_box": True,
    }:
        raise AssertionError("zero witness accounting changed")

    records = candidate["parent_cell"]["records"]
    if candidate["parent_cell"]["normalized_brackets"] != 70 or len(records) != 70:
        raise AssertionError("parent bracket count changed")
    expected_records = []
    for label, polynomial in parent_brackets():
        interval = direct_interval(polynomial, center, radius)
        sign = interval_sign(interval)
        if not sign:
            raise AssertionError(f"parent bracket {label} interval contains zero")
        expected_records.append(
            {
                "label": label,
                "terms": len(polynomial),
                "polynomial_sha256": polynomial_digest(b"diag3-local-parent-bracket-v1", polynomial),
                "interval": [encoded(interval[0]), encoded(interval[1])],
                "sign": sign,
            }
        )
    if records != expected_records:
        raise AssertionError("parent bracket replay changed")
    parent_summary = candidate["parent_cell"]
    if parent_summary["sign_definite_brackets"] != 70 or parent_summary["consequence"] != "the entire closed box lies in one uniform normalized parent cell":
        raise AssertionError("parent-cell consequence changed")

    fixed_projection = registration["fixed_projection"]
    projection = candidate["projection"]
    for key, value in fixed_projection.items():
        if projection[key] != value:
            raise AssertionError(f"fixed projection changed: {key}")
    columns = tuple(projection["fiber_columns_zero_based"])
    if columns != (3, 4, 7) or set(columns) & set(projection["base_columns_zero_based"]):
        raise AssertionError("projection column partition changed")
    minor = jacobian_minor(residuals, columns)
    minor_interval = direct_interval(minor, center, radius)
    minor_sign = interval_sign(minor_interval)
    if not minor_sign:
        raise AssertionError("projection minor interval contains zero")
    expected_projection_fields = {
        "jacobian_minor_terms": len(minor),
        "jacobian_minor_sha256": polynomial_digest(b"diag3-local-projection-minor-v1", minor),
        "jacobian_minor_at_center": encoded(evaluate(minor, center)),
        "jacobian_minor_interval": [encoded(minor_interval[0]), encoded(minor_interval[1])],
        "jacobian_minor_sign": minor_sign,
        "critical_points_in_box": 0,
    }
    for key, value in expected_projection_fields.items():
        if projection[key] != value:
            raise AssertionError(f"projection replay changed: {key}")

    faces = [
        {"variable": variable, "side": side}
        for variable in VARIABLES
        for side in ("lower", "upper")
    ]
    if candidate["boundary_accounting"] != {
        "coordinate_faces": 18,
        "internal_seams": 0,
        "faces_accounted": faces,
        "claimed_parent_infinity_faces": 0,
        "claimed_parent_wall_faces": 0,
    }:
        raise AssertionError("boundary accounting changed")
    if candidate["proof_consequence"] != registration["proof_consequence_if_accepted"]:
        raise AssertionError("proof consequence changed")
    if candidate["non_consequences"] != registration["non_consequences"]:
        raise AssertionError("scope exclusions changed")
    if candidate["theorem_accounting"] != {
        "final_unresolved_triple_orbits_before": 1_162_302,
        "final_unresolved_triple_orbits_after": 1_162_302,
        "score_before": "2/9",
        "score_after": "2/9",
    }:
        raise AssertionError("theorem accounting changed")
    if candidate["semantic_sha256"] != semantic_digest(candidate):
        raise AssertionError("certificate semantic digest changed")


def resign(candidate):
    candidate["semantic_sha256"] = semantic_digest(candidate)
    return candidate


def verify_hostile_mutations(certificate):
    mutations = []

    def add(name, mutate):
        candidate = deepcopy(certificate)
        mutate(candidate)
        resign(candidate)
        mutations.append((name, candidate))

    add("source_digest", lambda row: row["authenticated_sources"].__setitem__("critical_system_sha256", "0" * 64))
    add("named_presentation", lambda row: row["authenticated_sources"].__setitem__("named_factor_presentation", [5563, 16134, 19285]))
    add("canonical_row", lambda row: row["authenticated_sources"].__setitem__("canonical_unresolved_row", [5563, 4373, 23222]))
    add("center_coordinate", lambda row: row["box"]["center"].__setitem__(0, "-5/7"))
    add("box_radius", lambda row: row["box"].__setitem__("radius", "1/64"))
    add("parent_bracket_count", lambda row: row["parent_cell"].__setitem__("normalized_brackets", 69))
    add("parent_bracket_interval", lambda row: row["parent_cell"]["records"][0].__setitem__("interval", ["-1", "1"]))
    add("parent_bracket_sign", lambda row: row["parent_cell"]["records"][1].__setitem__("sign", 0))
    add("projection_columns", lambda row: row["projection"].__setitem__("fiber_columns_zero_based", [3, 4, 8]))
    add("projection_minor_digest", lambda row: row["projection"].__setitem__("jacobian_minor_sha256", "f" * 64))
    add("projection_minor_interval", lambda row: row["projection"].__setitem__("jacobian_minor_interval", ["-1", "1"]))
    add("boundary_face_count", lambda row: row["boundary_accounting"].__setitem__("coordinate_faces", 17))
    add("scope_orbit_transport", lambda row: row["scope"].__setitem__("orbit_transport_claimed", True))
    add("theorem_score", lambda row: row["theorem_accounting"].__setitem__("score_after", "3/9"))

    declared = certificate["hostile_mutations"]
    if declared != [name for name, _candidate in mutations]:
        raise AssertionError("hostile mutation declaration changed")
    for name, candidate in mutations:
        try:
            verify_candidate(candidate)
        except (AssertionError, KeyError, TypeError, ValueError):
            continue
        raise AssertionError(f"hostile mutation accepted: {name}")
    return len(mutations)


def verify_compact_sphere_negative_canary():
    # On [-1,1]^3, the sphere x^2+y^2+z^2=1/4 is compact and interior.
    # Its x-projection pivot derivative 2x must not receive a sign certificate.
    x_squared = {(2, 0, 0): Fraction(1)}
    y_squared = {(0, 2, 0): Fraction(1)}
    z_squared = {(0, 0, 2): Fraction(1)}
    sphere = add(add(x_squared, y_squared), z_squared)
    sphere = add(sphere, {(0, 0, 0): Fraction(-1, 4)})
    pivot = {(1, 0, 0): Fraction(2)}
    center = (Fraction(0), Fraction(0), Fraction(0))
    interval = direct_interval(pivot, center, Fraction(1))
    if interval != (Fraction(-2), Fraction(2)) or interval_sign(interval):
        raise AssertionError("compact-sphere negative canary was falsely certified")
    if evaluate(sphere, (Fraction(1, 2), Fraction(0), Fraction(0))) != 0:
        raise AssertionError("compact-sphere canary lost its exact zero")


def main():
    certificate = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    verify_candidate(certificate)
    rejected = verify_hostile_mutations(certificate)
    verify_compact_sphere_negative_canary()
    interval = certificate["projection"]["jacobian_minor_interval"]
    print("PASS independent exact residual, parent-bracket, and projection reconstruction")
    print("PASS exact nonzero projection minor on the entire closed box", interval)
    print("PASS all 70 parent brackets retain sign; exact center lies on all three walls")
    print("PASS boundary accounting: 18 box faces / 0 seams / 0 parent-infinity claims")
    print("PASS compact-sphere negative canary refused projection certification")
    print(f"PASS hostile mutations rejected {rejected}/{rejected}")
    print("THEOREM each restricted component meets the declared box boundary")
    print("SCOPE one hard-canary box only; no S8 transport; unresolved=1162302; score=2/9")


if __name__ == "__main__":
    main()
