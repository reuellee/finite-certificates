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
ROW2599_PARENT_CATALOG = HERE / "certs_4_8.jsonl"
CERTIFICATE = HERE / "data/DIAG3_TRIPLE_LOCAL_ROADMAP_CANARY.json"
SCHEMA = "diag3-triple-local-roadmap-canary-v1"
VARIABLES = tuple("abcdefghi")
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
EXPECTED_DECLARED_SCOPE = {
    "kind": "one closed rational box in one normalized uniform-parent cell",
    "named_factor_presentation": [5563, 16134, 19284],
    "canonical_unresolved_row": [5563, 4373, 23221],
    "orbit_transport_claimed": False,
    "s8_sign_transport_claimed": False,
    "global_parent_cell_coverage_claimed": False,
}
EXPECTED_FINITE_ACCEPTANCE_CONTRACT = {
    "success_status": "PROVED_LOCAL_BOUNDARY_COVERAGE",
    "success_conditions": [
        "the three authenticated residual equations vanish exactly at the rational center",
        "all 70 normalized parent brackets have exact sign-definite direct-monomial interval enclosures on the full closed box",
        "the fixed 3-by-3 residual Jacobian minor has an exact sign-definite direct-monomial interval enclosure on the full closed box",
        "the independent verifier reconstructs the source equations, 70 parent brackets, Jacobian minor, intervals, semantic digest, and all 18 boundary faces without importing the producer",
        "every declared hostile mutation is rejected",
    ],
    "null_status": "BOUNDED_NO_GO",
    "null_conditions": [
        "the center is not an exact triple zero",
        "some parent bracket interval contains zero",
        "the fixed projection minor interval contains zero",
        "independent replay or a hostile mutation test fails",
    ],
    "fail_closed_policy": (
        "No adaptive radius reduction, pivot substitution, numerical tolerance, "
        "or orbit enlargement is allowed in the formal run."
    ),
    "resource_ceiling": (
        "300 wall-clock seconds and 1 GiB resident memory for each producer or verifier run"
    ),
}
EXPECTED_PROOF_CONSEQUENCE = (
    "Every connected component of the named triple-zero set restricted to the "
    "declared closed box meets one of its 18 boundary faces; the component "
    "through the center is nonvacuous."
)
EXPECTED_NON_CONSEQUENCES = [
    "no component is proved to reach a genuine parent wall or parent infinity",
    "no full parent cell is covered",
    "no second representative and no S8 orbit is covered",
    "the 1162302-row unresolved count is unchanged",
    "the independent pair H_c^1 obligation is unchanged",
    "the 9DVL score remains 2/9",
]
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
ROW2599_MISMATCH_LABELS = [
    "1236", "1237", "1246", "1247", "1256", "1257", "1258", "1267",
    "1278", "1346", "1347", "1348", "1357", "1358", "1368", "1378",
    "1457", "1467", "1468", "1478", "1567", "1568", "1578", "1678",
    "2358", "2458", "2568", "2578", "5678",
]
THEOREM_EFFECT = (
    "A nonvacuous smooth local triple-zero compiler fixture is proved in one "
    "uniform parent chamber distinct from row 2599, but only artificial "
    "box-boundary reach is shown; no complete orbit, genuine parent boundary, "
    "or invariant obligation is covered, so the honest 9DVL score remains 2/9."
)
HOSTILE_MUTATIONS = [
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
    "unknown_top_level_global_theorem",
    "unknown_projection_global_parent_component_coverage",
    "theorem_score",
]


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


def solve_square(matrix, right_hand_side):
    augmented = [
        [Fraction(value) for value in row] + [Fraction(right_hand_side[index])]
        for index, row in enumerate(matrix)
    ]
    size = len(augmented)
    for column in range(size):
        pivot = next(
            (row for row in range(column, size) if augmented[row][column]),
            None,
        )
        if pivot is None:
            raise AssertionError("row-2599 normalization basis became singular")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(size):
            if row == column or not augmented[row][column]:
                continue
            scale = augmented[row][column]
            augmented[row] = [
                left - scale * right
                for left, right in zip(
                    augmented[row], augmented[column], strict=True
                )
            ]
    return tuple(row[-1] for row in augmented)


def row2599_direct_parent_signs():
    records = [
        json.loads(line)
        for line in ROW2599_PARENT_CATALOG.read_text(encoding="utf-8").splitlines()
        if line
    ]
    raw = records[2599]["matrix"]
    if len(raw) != 4 or any(len(row) != 8 for row in raw):
        raise AssertionError("row-2599 parent matrix shape changed")
    basis = tuple(tuple(raw[row][column] for column in range(4)) for row in range(4))

    def coordinates(column):
        return solve_square(basis, tuple(raw[row][column] for row in range(4)))

    anchor = coordinates(4)
    if any(not value for value in anchor):
        raise AssertionError("row-2599 anchor normalization changed")
    point = []
    for column in (5, 6, 7):
        moving = coordinates(column)
        gauge = moving[0] / anchor[0]
        if not gauge:
            raise AssertionError("row-2599 moving-column gauge changed")
        point.extend((moving[row] / anchor[row]) / gauge for row in (1, 2, 3))
    signs = tuple(
        1 if evaluate(polynomial, point) > 0 else -1
        for _label, polynomial in parent_brackets()
    )
    if any(not evaluate(polynomial, point) for _label, polynomial in parent_brackets()):
        raise AssertionError("row-2599 reference acquired a zero bracket")
    return signs


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


def verified_registration(registration_payload=None):
    payload = REGISTRATION.read_bytes() if registration_payload is None else registration_payload
    if hashlib.sha256(payload).hexdigest() != REGISTRATION_SHA256:
        raise AssertionError("preregistration raw digest changed")
    registration = json.loads(payload)
    if registration["schema"] != REGISTRATION_SCHEMA:
        raise AssertionError("preregistration schema changed")
    if registration["status"] != REGISTRATION_STATUS:
        raise AssertionError("preregistration status changed")
    if registration["declared_scope"] != EXPECTED_DECLARED_SCOPE:
        raise AssertionError("preregistered declared scope changed")
    if registration["authenticated_inputs"] != {
        "critical_system": "ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json",
        "critical_system_sha256": CRITICAL_SYSTEM_SHA256,
        "source_gate": "ai/omreal/data/DIAG3_triple_fullspace_feasibility_gate.json",
        "source_gate_semantic_sha256": SOURCE_GATE_SEMANTIC_SHA256,
    }:
        raise AssertionError("preregistered source contract changed")
    if registration["finite_acceptance_contract"] != EXPECTED_FINITE_ACCEPTANCE_CONTRACT:
        raise AssertionError("preregistered finite acceptance contract changed")
    if registration["proof_consequence_if_accepted"] != EXPECTED_PROOF_CONSEQUENCE:
        raise AssertionError("preregistered proof consequence changed")
    if registration["non_consequences"] != EXPECTED_NON_CONSEQUENCES:
        raise AssertionError("preregistered non-consequences changed")
    return registration


def verify_candidate(candidate, registration_payload=None):
    registration = verified_registration(registration_payload)
    reconstructed_row2599_signs = row2599_direct_parent_signs()
    if reconstructed_row2599_signs != ROW2599_DIRECT_PARENT_SIGNS:
        raise AssertionError("row-2599 direct parent signs changed")
    row2599_sign_digest = hashlib.sha256(
        b"diag3-row2599-direct-parent-signs-v1\0"
        + bytes(int(value > 0) for value in reconstructed_row2599_signs)
    ).hexdigest()
    if row2599_sign_digest != ROW2599_DIRECT_PARENT_SIGN_SHA256:
        raise AssertionError("row-2599 direct parent-sign pin changed")
    if sha256(ROW2599_PARENT_CATALOG) != ROW2599_PARENT_CATALOG_SHA256:
        raise AssertionError("row-2599 parent catalog changed")
    source = json.loads(SYSTEM.read_text(encoding="ascii"))
    source_gate = json.loads(SOURCE_GATE.read_text(encoding="utf-8"))
    if candidate["schema"] != SCHEMA or candidate["status"] != "PROVED_LOCAL_BOUNDARY_COVERAGE":
        raise AssertionError("certificate schema or status changed")
    if candidate["registration_sha256"] != REGISTRATION_SHA256:
        raise AssertionError("registration digest changed")
    if sha256(SYSTEM) != CRITICAL_SYSTEM_SHA256:
        raise AssertionError("critical source no longer matches registration")
    if sha256(SOURCE_GATE) != SOURCE_GATE_RAW_SHA256:
        raise AssertionError("source-mapping gate raw digest changed")
    if source_gate["semantic_sha256"] != SOURCE_GATE_SEMANTIC_SHA256:
        raise AssertionError("source gate no longer matches registration")
    authenticated = candidate["authenticated_sources"]
    expected_authenticated = {
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
    }
    if authenticated != expected_authenticated:
        raise AssertionError("authenticated source accounting changed")
    if source["schema"] != "diag3-triple-fullspace-critical-system-v1":
        raise AssertionError("critical-system schema changed")
    if source_gate["schema"] != "diag3-triple-fullspace-feasibility-gate-v1":
        raise AssertionError("source-mapping gate schema changed")
    if source["named_presentation"] != EXPECTED_DECLARED_SCOPE["named_factor_presentation"]:
        raise AssertionError("named presentation no longer matches registration")
    if source["canonical_row"] != EXPECTED_DECLARED_SCOPE["canonical_unresolved_row"]:
        raise AssertionError("critical-system canonical row changed")
    if source_gate["named_presentation"] != EXPECTED_DECLARED_SCOPE["named_factor_presentation"]:
        raise AssertionError("source gate named presentation changed")
    if source_gate["canonical_row"] != EXPECTED_DECLARED_SCOPE["canonical_unresolved_row"]:
        raise AssertionError("canonical row no longer matches registration")
    if candidate["scope"] != EXPECTED_DECLARED_SCOPE:
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
    if len(ROW2599_DIRECT_PARENT_SIGNS) != len(expected_records):
        raise AssertionError("row-2599 parent-sign reference changed")
    row2599_mismatches = [
        record["label"]
        for record, row2599_sign in zip(
            expected_records, reconstructed_row2599_signs, strict=True
        )
        if record["sign"] != row2599_sign
    ]
    if row2599_mismatches != ROW2599_MISMATCH_LABELS:
        raise AssertionError("row-2599 parent-cell comparison changed")
    if parent_summary["row2599_comparison"] != {
        "reference_parent_index": 2599,
        "reference_catalog_sha256": ROW2599_PARENT_CATALOG_SHA256,
        "reference_normalized_parent_sign_sha256": ROW2599_NORMALIZED_PARENT_SIGN_SHA256,
        "reference_direct_parent_sign_sha256": ROW2599_DIRECT_PARENT_SIGN_SHA256,
        "reference_verification_command": ROW2599_PARENT_GATE_VERIFY_COMMAND,
        "sign_mismatch_count": 29,
        "sign_mismatch_labels": ROW2599_MISMATCH_LABELS,
        "same_uniform_parent_cell": False,
        "consequence": "the certified box is not in the row-2599 parent chamber",
    }:
        raise AssertionError("row-2599 comparison accounting changed")

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
        "geometric_consequence": (
            "the triple-zero set is smooth of dimension six near its box "
            "intersection and projection to the six base variables is a local "
            "diffeomorphism there"
        ),
    }
    for key, value in expected_projection_fields.items():
        if projection[key] != value:
            raise AssertionError(f"projection replay changed: {key}")

    if candidate["topological_argument"] != {
        "boundary_avoiding_component_is_smooth": True,
        "boundary_avoiding_component_is_open_in_the_smooth_zero_set": True,
        "projected_component_image_is_nonempty": True,
        "projected_component_image_is_open_in_R6": True,
        "boundary_avoiding_component_is_compact": True,
        "projected_component_image_is_compact": True,
        "contradiction": "no nonempty subset of R6 is both open and compact",
    }:
        raise AssertionError("topological implication changed")

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
        "face_classification": "ARTIFICIAL_SCOPE_BOUNDARY_ONLY",
    }:
        raise AssertionError("boundary accounting changed")
    if candidate["proof_consequence"] != EXPECTED_PROOF_CONSEQUENCE:
        raise AssertionError("proof consequence changed")
    if candidate["non_consequences"] != EXPECTED_NON_CONSEQUENCES:
        raise AssertionError("scope exclusions changed")
    if candidate["theorem_accounting"] != {
        "final_unresolved_triple_orbits_before": 1_162_302,
        "final_unresolved_triple_orbits_after": 1_162_302,
        "score_before": "2/9",
        "score_after": "2/9",
    }:
        raise AssertionError("theorem accounting changed")
    if candidate["theorem_effect"] != THEOREM_EFFECT:
        raise AssertionError("theorem effect changed")
    if candidate["semantic_sha256"] != semantic_digest(candidate):
        raise AssertionError("certificate semantic digest changed")

    expected_candidate = {
        "schema": SCHEMA,
        "status": "PROVED_LOCAL_BOUNDARY_COVERAGE",
        "registration_sha256": REGISTRATION_SHA256,
        "authenticated_sources": expected_authenticated,
        "scope": EXPECTED_DECLARED_SCOPE,
        "box": expected_box,
        "exact_zero_witness": {
            "point": expected_box["center"],
            "residual_values": ["0", "0", "0"],
            "strictly_inside_box": True,
        },
        "parent_cell": {
            "normalized_brackets": 70,
            "sign_definite_brackets": 70,
            "records": expected_records,
            "consequence": (
                "the entire closed box lies in one uniform normalized parent cell"
            ),
            "row2599_comparison": {
                "reference_parent_index": 2599,
                "reference_catalog_sha256": ROW2599_PARENT_CATALOG_SHA256,
                "reference_normalized_parent_sign_sha256": (
                    ROW2599_NORMALIZED_PARENT_SIGN_SHA256
                ),
                "reference_direct_parent_sign_sha256": (
                    ROW2599_DIRECT_PARENT_SIGN_SHA256
                ),
                "reference_verification_command": (
                    ROW2599_PARENT_GATE_VERIFY_COMMAND
                ),
                "sign_mismatch_count": 29,
                "sign_mismatch_labels": ROW2599_MISMATCH_LABELS,
                "same_uniform_parent_cell": False,
                "consequence": (
                    "the certified box is not in the row-2599 parent chamber"
                ),
            },
        },
        "projection": {**fixed_projection, **expected_projection_fields},
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
            "faces_accounted": faces,
            "claimed_parent_infinity_faces": 0,
            "claimed_parent_wall_faces": 0,
            "face_classification": "ARTIFICIAL_SCOPE_BOUNDARY_ONLY",
        },
        "proof_consequence": EXPECTED_PROOF_CONSEQUENCE,
        "non_consequences": EXPECTED_NON_CONSEQUENCES,
        "theorem_accounting": {
            "final_unresolved_triple_orbits_before": 1_162_302,
            "final_unresolved_triple_orbits_after": 1_162_302,
            "score_before": "2/9",
            "score_after": "2/9",
        },
        "theorem_effect": THEOREM_EFFECT,
        "hostile_mutations": HOSTILE_MUTATIONS,
    }
    expected_candidate["semantic_sha256"] = semantic_digest(expected_candidate)
    if candidate != expected_candidate:
        raise AssertionError("certificate exact schema or full reconstruction changed")


def resign(candidate):
    candidate["semantic_sha256"] = semantic_digest(candidate)
    return candidate


def verify_hostile_mutations(certificate):
    mutations = []

    def add(name, mutate):
        candidate = deepcopy(certificate)
        mutate(candidate)
        resign(candidate)
        mutations.append((name, candidate, None))

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
    add("parent_infinity_claim", lambda row: row["boundary_accounting"].__setitem__("claimed_parent_infinity_faces", 18))
    add("scope_orbit_transport", lambda row: row["scope"].__setitem__("orbit_transport_claimed", True))
    registration = json.loads(REGISTRATION.read_text(encoding="utf-8"))
    registration["declared_scope"]["global_parent_cell_coverage_claimed"] = True
    registration["proof_consequence_if_accepted"] = (
        "Every component reaches true parent infinity and the full parent cell is covered."
    )
    registration["non_consequences"] = [
        "the local box boundary is true parent infinity"
    ]
    coupled = deepcopy(certificate)
    coupled["scope"] = registration["declared_scope"]
    coupled["proof_consequence"] = registration["proof_consequence_if_accepted"]
    coupled["non_consequences"] = registration["non_consequences"]
    coupled["boundary_accounting"]["claimed_parent_infinity_faces"] = 18
    coupled["boundary_accounting"]["face_classification"] = "TRUE_PARENT_INFINITY"
    resign(coupled)
    mutations.append(
        (
            "coupled_registration_global_rewrite",
            coupled,
            json.dumps(registration, sort_keys=True).encode("utf-8"),
        )
    )
    add(
        "unknown_top_level_global_theorem",
        lambda row: row.__setitem__(
            "global_theorem", "ALL_UNRESOLVED_TRIPLE_ORBITS_CLOSED"
        ),
    )
    add(
        "unknown_projection_global_parent_component_coverage",
        lambda row: row["projection"].__setitem__(
            "global_parent_component_coverage", "COMPLETE"
        ),
    )
    add("theorem_score", lambda row: row["theorem_accounting"].__setitem__("score_after", "3/9"))

    declared = certificate["hostile_mutations"]
    if declared != HOSTILE_MUTATIONS:
        raise AssertionError("hostile mutation schema changed")
    if declared != [name for name, _candidate, _registration in mutations]:
        raise AssertionError("hostile mutation declaration changed")
    for name, candidate, registration_payload in mutations:
        try:
            verify_candidate(candidate, registration_payload=registration_payload)
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
