#!/usr/bin/env python3
"""Build the exact fixed-domain symmetry and low-degree projection preflight.

This producer never solves a roadmap critical system.  It computes the exact
subgroup of S8 preserving the complete row-2599 S12,37 active-factor set,
uses Burnside on that proved subgroup to count admissible pair quotients, and
screens every active factor of degree at most two for the pinned projection.
"""

from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import permutations
import json
from math import comb
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OM = ROOT / "ai/omreal"
PRIOR = ROOT / "ops/team/diag9-s1237-normal-link-prover"
CYCLE = ROOT / "ops/research-team/cycles/2026-09-01-d9-fixed-domain-incidence-gate2"
OUTPUT = HERE / "FIXED_DOMAIN_INCIDENCE_PREFLIGHT.json"

BASE_REVISION = "32e2b37bf54c53982cb58a3b8d026734f9ab1113"
BASE_TREE = "689d1a5fb981fd2d52f7adb88721d9c7d3a01228"
PROJECTION = tuple(1 << index for index in range(9))
SYSTEM_CEILING = 100_000
PAIR_BUDGET = SYSTEM_CEILING - 3_539

SOURCE_PATHS = (
    "ops/research-team/cycles/2026-09-01-d9-fixed-domain-incidence-gate2/OPENING_AUDIT.json",
    "ops/team/d9-component-roadmap-constructor/RESULT.json",
    "ops/team/d9-component-roadmap-constructor/PROJECTION_STRATIFICATION_PREFLIGHT.json",
    "ops/team/diag9-s1237-normal-link-prover/ACTIVE_LITERAL_INVENTORY.json",
    "ai/omreal/DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY.py",
    "ai/omreal/verify_diag2_pivot_all_pair_fibers.py",
    "ai/omreal/data/DIAG2_PIVOT_pair_classification.npz",
    "ai/omreal/data/DIAG9_GRAPH_global_factor_census.npz",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def polynomial_degree(polynomial: dict[tuple[int, ...], int]) -> int:
    return max(map(sum, polynomial))


def derivative(polynomial: dict[tuple[int, ...], int], variable: int) -> dict:
    answer = {}
    for monomial, coefficient in polynomial.items():
        exponent = monomial[variable]
        if not exponent:
            continue
        reduced = list(monomial)
        reduced[variable] -= 1
        key = tuple(reduced)
        answer[key] = answer.get(key, 0) + coefficient * exponent
    return {key: value for key, value in answer.items() if value}


def add_scaled(left: dict, right: dict, scale: int) -> dict:
    answer = dict(left)
    for monomial, coefficient in right.items():
        answer[monomial] = answer.get(monomial, 0) + scale * coefficient
        if not answer[monomial]:
            del answer[monomial]
    return answer


def affine_row(polynomial: dict) -> tuple[list[Fraction], Fraction]:
    coefficients = [Fraction(0) for _ in range(9)]
    constant = Fraction(0)
    for monomial, coefficient in polynomial.items():
        degree = sum(monomial)
        require(degree <= 1, "low-degree Lagrange equation is not affine")
        if degree == 0:
            constant += coefficient
        else:
            variable = monomial.index(1)
            require(monomial.count(1) == 1, "nonlinear affine monomial")
            coefficients[variable] += coefficient
    return coefficients, -constant


def rref(rows: list[tuple[list[Fraction], Fraction]]):
    matrix = [list(coefficients) + [rhs] for coefficients, rhs in rows]
    pivot_columns = []
    pivot_row = 0
    for column in range(9):
        selected = next(
            (row for row in range(pivot_row, len(matrix)) if matrix[row][column]),
            None,
        )
        if selected is None:
            continue
        matrix[pivot_row], matrix[selected] = matrix[selected], matrix[pivot_row]
        pivot = matrix[pivot_row][column]
        matrix[pivot_row] = [value / pivot for value in matrix[pivot_row]]
        for row in range(len(matrix)):
            if row == pivot_row or not matrix[row][column]:
                continue
            scale = matrix[row][column]
            matrix[row] = [
                left - scale * right
                for left, right in zip(matrix[row], matrix[pivot_row], strict=True)
            ]
        pivot_columns.append(column)
        pivot_row += 1
        if pivot_row == len(matrix):
            break
    inconsistent = any(
        not any(row[:9]) and bool(row[9]) for row in matrix
    )
    return matrix, tuple(pivot_columns), inconsistent


def parameter_add(left: dict, right: dict) -> dict:
    answer = dict(left)
    for monomial, coefficient in right.items():
        answer[monomial] = answer.get(monomial, Fraction(0)) + coefficient
        if not answer[monomial]:
            del answer[monomial]
    return answer


def parameter_multiply(left: dict, right: dict) -> dict:
    answer = {}
    for first, first_coefficient in left.items():
        for second, second_coefficient in right.items():
            monomial = tuple(
                first[index] + second[index] for index in range(len(first))
            )
            answer[monomial] = (
                answer.get(monomial, Fraction(0))
                + first_coefficient * second_coefficient
            )
    return {key: value for key, value in answer.items() if value}


def restrict_to_solution(polynomial: dict, matrix, pivots: tuple[int, ...]) -> dict:
    free = tuple(column for column in range(9) if column not in pivots)
    dimension = len(free)
    zero = (0,) * dimension
    forms = [None] * 9
    for parameter, column in enumerate(free):
        exponent = [0] * dimension
        exponent[parameter] = 1
        forms[column] = {tuple(exponent): Fraction(1)}
    for row_index, column in enumerate(pivots):
        form = {zero: matrix[row_index][9]} if matrix[row_index][9] else {}
        for parameter, free_column in enumerate(free):
            coefficient = -matrix[row_index][free_column]
            if coefficient:
                exponent = [0] * dimension
                exponent[parameter] = 1
                form[tuple(exponent)] = coefficient
        forms[column] = form

    result = {}
    for monomial, coefficient in polynomial.items():
        term = {zero: Fraction(coefficient)}
        for variable, exponent in enumerate(monomial):
            for _ in range(exponent):
                term = parameter_multiply(term, forms[variable])
        result = parameter_add(result, term)
    return result


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def classify_low_degree(factor_id: int, polynomial: dict) -> dict:
    gradients = [derivative(polynomial, variable) for variable in range(9)]
    equations = [
        add_scaled(gradients[variable], gradients[0], -PROJECTION[variable])
        for variable in range(1, 9)
    ]
    rows = [affine_row(equation) for equation in equations]
    matrix, pivots, inconsistent = rref(rows)
    degree = polynomial_degree(polynomial)
    if inconsistent:
        restricted = {}
        free_dimension = None
        status = "GENERIC_EMPTY"
        critical_count = 0
        discriminant = None
    else:
        free_dimension = 9 - len(pivots)
        restricted = restrict_to_solution(polynomial, matrix, pivots)
        restricted_degree = max(map(sum, restricted), default=-1)
        if free_dimension == 0:
            if restricted:
                status = "GENERIC_EMPTY"
                critical_count = 0
            else:
                status = "GENERIC_SIMPLE"
                critical_count = 1
            discriminant = None
        elif not restricted:
            status = "NONGENERIC_POSITIVE_DIMENSION"
            critical_count = None
            discriminant = None
        elif restricted_degree == 0:
            status = "GENERIC_EMPTY"
            critical_count = 0
            discriminant = None
        elif free_dimension >= 2:
            status = "NONGENERIC_POSITIVE_DIMENSION"
            critical_count = None
            discriminant = None
        else:
            coefficients = {
                exponent[0]: value for exponent, value in restricted.items()
            }
            if restricted_degree == 1:
                status = "GENERIC_SIMPLE"
                critical_count = 1
                discriminant = None
            else:
                a = coefficients.get(2, Fraction(0))
                b = coefficients.get(1, Fraction(0))
                c = coefficients.get(0, Fraction(0))
                discriminant_value = b * b - 4 * a * c
                discriminant = fraction_text(discriminant_value)
                if discriminant_value:
                    status = "GENERIC_SIMPLE"
                    critical_count = 2
                else:
                    status = "NONGENERIC_REPEATED_CRITICAL_POINT"
                    critical_count = 1
    serialized = [
        [list(exponent), fraction_text(coefficient)]
        for exponent, coefficient in sorted(restricted.items())
    ]
    return {
        "factor_id": factor_id,
        "factor_degree": degree,
        "lagrange_rank": None if inconsistent else len(pivots),
        "lagrange_inconsistent": inconsistent,
        "free_dimension_before_wall_equation": free_dimension,
        "restricted_wall_polynomial": serialized,
        "restricted_discriminant": discriminant,
        "critical_count_over_algebraic_closure": critical_count,
        "status": status,
    }


def semantic_digest(domain_rows, projection_rows) -> str:
    digest = hashlib.sha256()
    digest.update(b"d9-fixed-domain-incidence-gate2-preflight-v1\0")
    digest.update(repr(domain_rows).encode("ascii"))
    digest.update(repr(projection_rows).encode("ascii"))
    return digest.hexdigest()


def build() -> dict:
    sys.path.insert(0, str(OM))
    import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled

    inventory = json.loads(
        (PRIOR / "ACTIVE_LITERAL_INVENTORY.json").read_text(encoding="utf-8")
    )
    active = tuple(row["factor_id"] for row in inventory["literal_rows"])
    active_set = frozenset(active)
    require(len(active) == len(active_set) == 3_539, "active factor census")

    print("loading exact 26,740-factor action", flush=True)
    occurrences, occurrence_factor, factor_polynomials = labeled.factor_polynomials()
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    require(len(factor_occurrence) == 26_740, "global factor action census")

    print("enumerating all 40,320 active-set relabelings", flush=True)
    stabilizer = []
    rejection_probes = Counter()
    domain_rows = []
    action_digest = hashlib.sha256()
    for permutation in permutations(range(8)):
        mapping = labeled.triple_map(permutation)
        preserved = True
        witness_factor = None
        witness_image = None
        probes = 0
        for factor in active:
            probes += 1
            image = labeled.transform_factor(
                factor, mapping, factor_occurrence, occurrence_factor
            )
            if image not in active_set:
                preserved = False
                witness_factor = factor
                witness_image = image
                break
        if preserved:
            stabilizer.append(permutation)
        else:
            rejection_probes[probes] += 1
        row = (permutation, preserved, witness_factor, witness_image, probes)
        action_digest.update(repr(row).encode("ascii"))
        domain_rows.append(row)
    require(stabilizer, "identity missing from active-set stabilizer")

    fixed_pair_sum = 0
    burnside_rows = []
    for permutation in stabilizer:
        mapping = labeled.triple_map(permutation)
        square = tuple(permutation[permutation[index]] for index in range(8))
        square_mapping = labeled.triple_map(square)
        fixed = sum(
            labeled.transform_factor(
                factor, mapping, factor_occurrence, occurrence_factor
            )
            == factor
            for factor in active
        )
        fixed_square = sum(
            labeled.transform_factor(
                factor, square_mapping, factor_occurrence, occurrence_factor
            )
            == factor
            for factor in active
        )
        fixed_pairs = comb(fixed, 2) + (fixed_square - fixed) // 2
        fixed_pair_sum += fixed_pairs
        burnside_rows.append(
            {
                "permutation": list(permutation),
                "fixed_factors": fixed,
                "fixed_factors_under_square": fixed_square,
                "fixed_unordered_pairs": fixed_pairs,
            }
        )
    require(
        fixed_pair_sum % len(stabilizer) == 0,
        "nonintegral fixed-domain Burnside quotient",
    )
    pair_orbits = fixed_pair_sum // len(stabilizer)

    low_degree = tuple(
        factor for factor in active if polynomial_degree(factor_polynomials[factor]) <= 2
    )
    require(len(low_degree) == 83, "low-degree active factor census")
    print("screening 83 exact low-degree projection systems", flush=True)
    projection_rows = [
        classify_low_degree(factor, factor_polynomials[factor])
        for factor in low_degree
    ]
    status_census = dict(sorted(Counter(row["status"] for row in projection_rows).items()))
    nongeneric = [
        row["factor_id"]
        for row in projection_rows
        if row["status"].startswith("NONGENERIC")
    ]

    pair_gate_pass = pair_orbits <= PAIR_BUDGET
    low_degree_pass = not nongeneric
    complete_projection = len(projection_rows) == len(active)
    authorization = pair_gate_pass and low_degree_pass and complete_projection
    if nongeneric:
        endpoint = "LOW_DEGREE_PROJECTION_SPECIALIZATION_IS_NONGENERIC"
        classification = "EXACT_NEGATIVE_PROJECTION_ENDPOINT"
    elif not pair_gate_pass:
        endpoint = "FIXED_DOMAIN_SYMMETRY_QUOTIENT_EXCEEDS_PAIR_SYSTEM_BUDGET"
        classification = "EXACT_FAIL_CLOSED_SYMMETRY_NULL"
    else:
        endpoint = "LOW_DEGREE_PROJECTION_SCREEN_PASSES_BUT_COMPLETE_SPECIALIZATION_IS_OPEN"
        classification = "EXACT_FAIL_CLOSED_PARTIAL_PROJECTION_NULL"

    result = {
        "format": "d9-fixed-domain-incidence-gate2-preflight-v1",
        "track_id": "d9-fixed-domain-incidence-constructor",
        "base_revision": BASE_REVISION,
        "base_tree": BASE_TREE,
        "source_pins": {relative: sha256(ROOT / relative) for relative in SOURCE_PATHS},
        "fixed_domain": {
            "parent_index": inventory["parent_index"],
            "family": inventory["family"],
            "active_factors": len(active),
            "active_factor_semantic_sha256": inventory["semantic_sha256"],
            "label_permutations_checked": 40_320,
            "active_set_stabilizer_order": len(stabilizer),
            "active_set_stabilizer": [list(permutation) for permutation in stabilizer],
            "active_set_orbit_size": 40_320 // len(stabilizer),
            "rejected_permutations": 40_320 - len(stabilizer),
            "rejection_probe_census": {
                str(key): value for key, value in sorted(rejection_probes.items())
            },
            "action_witness_semantic_sha256": action_digest.hexdigest(),
        },
        "pair_frontier": {
            "unfiltered_active_pairs": comb(len(active), 2),
            "fixed_domain_stabilizer_pair_orbits": pair_orbits,
            "burnside_rows": burnside_rows,
            "global_s8_ambient_pair_orbits": 9_476,
            "global_s8_preserves_fixed_active_set": len(stabilizer) == 40_320,
            "global_9476_quotient_authorized_for_fixed_domain": False,
            "pair_system_budget": PAIR_BUDGET,
            "pair_gate_pass": pair_gate_pass,
            "complete_source_derived_nonemptiness_filter": "ABSENT",
        },
        "projection_screen": {
            "vector": list(PROJECTION),
            "active_degree_census": dict(
                sorted(Counter(polynomial_degree(factor_polynomials[factor]) for factor in active).items())
            ),
            "screened_degrees": [1, 2],
            "screened_factor_count": len(projection_rows),
            "unscreened_factor_count": len(active) - len(projection_rows),
            "status_census": status_census,
            "nongeneric_factor_ids": nongeneric,
            "rows": projection_rows,
            "low_degree_specialization_pass": low_degree_pass,
            "complete_projection_specialization_certificate": complete_projection,
        },
        "semantic_sha256": semantic_digest(domain_rows, projection_rows),
        "endpoint": endpoint,
        "classification": classification,
        "critical_systems_solved": 0,
        "critical_enumeration_authorized": authorization,
        "theorem_ledger": "2/9",
        "nonconsequences": [
            "NO_COMPLETE_FIXED_DOMAIN_MULTIWALL_INCIDENCE_FILTER",
            "NO_PROJECTION_CERTIFICATE_FOR_DEGREES_THREE_THROUGH_SIX",
            "NO_FIXED_DOMAIN_ROADMAP",
            "NO_FIXED_DOMAIN_CONNECTIVITY_OR_DISCONNECTION",
            "NO_DIAGONAL_9_RESULT",
            "NO_9DVL_SCORE_CHANGE",
        ],
        "next_action": (
            "Apply the mandatory closing anti-stagnation gate: pivot away from "
            "another symmetry-only or unfiltered pair enumeration unless an "
            "independently complete parent-residence incidence theorem is supplied."
        ),
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    result = build()
    if arguments.write:
        HERE.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(
            (json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8")
        )
        print(f"wrote {OUTPUT.relative_to(ROOT)}", flush=True)
    print("endpoint", result["endpoint"])
    print("stabilizer", result["fixed_domain"]["active_set_stabilizer_order"])
    print("pair_orbits", result["pair_frontier"]["fixed_domain_stabilizer_pair_orbits"])
    print("projection", result["projection_screen"]["status_census"])
    print("critical_enumeration=DENIED ledger=2/9")


if __name__ == "__main__":
    main()
