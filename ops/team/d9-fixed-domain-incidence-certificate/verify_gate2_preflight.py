#!/usr/bin/env python3
"""Independent replay of the D9 fixed-domain incidence gate-2 preflight.

The verifier reads the primitive-factor NPZ directly, rebuilds the S8 action
from 3-subsets, and uses an affine quadratic-form calculation for the
low-degree polar loci.  It does not import the producer or its row-reduction
helpers.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction
import hashlib
from itertools import combinations, permutations
import json
from math import comb
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CANDIDATE_PATH = (
    ROOT
    / "ops/team/d9-fixed-domain-incidence-constructor/FIXED_DOMAIN_INCIDENCE_PREFLIGHT.json"
)
INVENTORY_PATH = (
    ROOT / "ops/team/diag9-s1237-normal-link-prover/ACTIVE_LITERAL_INVENTORY.json"
)
FACTOR_PATH = ROOT / "ai/omreal/data/DIAG9_GRAPH_global_factor_census.npz"
EXPECTED_BASE = "32e2b37bf54c53982cb58a3b8d026734f9ab1113"
EXPECTED_TREE = "689d1a5fb981fd2d52f7adb88721d9c7d3a01228"
PROJECTION = tuple(1 << index for index in range(9))
# The factor certificate indexes derived triples in colexicographic order.
# Reconstruct that ordering directly instead of importing the source helper.
TRIPLES = tuple(
    sorted(combinations(range(8), 3), key=lambda subset: tuple(reversed(subset)))
)
TRIPLE_INDEX = {triple: index for index, triple in enumerate(TRIPLES)}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def triple_map(permutation: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        TRIPLE_INDEX[tuple(sorted(permutation[value] for value in triple))]
        for triple in TRIPLES
    )


def transform_occurrence(occurrence, mapping):
    return tuple(sorted(mapping[index] for index in occurrence))


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def matrix_rref(matrix: list[list[Fraction]], coefficient_columns: int):
    rows = [list(map(Fraction, row)) for row in matrix]
    pivots = []
    target_row = 0
    for column in range(coefficient_columns):
        selected = next(
            (row for row in range(target_row, len(rows)) if rows[row][column]),
            None,
        )
        if selected is None:
            continue
        rows[target_row], rows[selected] = rows[selected], rows[target_row]
        divisor = rows[target_row][column]
        rows[target_row] = [value / divisor for value in rows[target_row]]
        for row in range(len(rows)):
            if row == target_row:
                continue
            multiplier = rows[row][column]
            if multiplier:
                rows[row] = [
                    left - multiplier * right
                    for left, right in zip(rows[row], rows[target_row], strict=True)
                ]
        pivots.append(column)
        target_row += 1
        if target_row == len(rows):
            break
    return rows, tuple(pivots)


def quadratic_data(polynomial: dict[tuple[int, ...], int]):
    constant = Fraction(0)
    linear = [Fraction(0) for _ in range(9)]
    hessian = [[Fraction(0) for _ in range(9)] for _ in range(9)]
    for monomial, coefficient in polynomial.items():
        degree = sum(monomial)
        require(degree <= 2, "non-low-degree factor in projection replay")
        coefficient = Fraction(coefficient)
        if degree == 0:
            constant += coefficient
        elif degree == 1:
            linear[monomial.index(1)] += coefficient
        else:
            support = [index for index, exponent in enumerate(monomial) if exponent]
            if len(support) == 1:
                index = support[0]
                require(monomial[index] == 2, "bad square monomial")
                hessian[index][index] += 2 * coefficient
            else:
                left, right = support
                require(monomial[left] == monomial[right] == 1, "bad cross monomial")
                hessian[left][right] += coefficient
                hessian[right][left] += coefficient
    return constant, linear, hessian


def matvec(matrix, vector):
    return [
        sum((matrix[row][column] * vector[column] for column in range(9)), Fraction(0))
        for row in range(9)
    ]


def dot(left, right):
    return sum((a * b for a, b in zip(left, right, strict=True)), Fraction(0))


def classify_factor(factor_id: int, polynomial: dict) -> dict:
    constant, linear, hessian = quadratic_data(polynomial)
    # grad(q) = H*x + linear.  The eight polar equations are
    # grad_j - lambda_j*grad_0 = 0.
    augmented = []
    for variable in range(1, 9):
        coefficients = [
            hessian[variable][column]
            - PROJECTION[variable] * hessian[0][column]
            for column in range(9)
        ]
        rhs = -(linear[variable] - PROJECTION[variable] * linear[0])
        augmented.append(coefficients + [rhs])
    reduced, pivots = matrix_rref(augmented, 9)
    inconsistent = any(not any(row[:9]) and row[9] for row in reduced)
    degree = max(map(sum, polynomial))
    if inconsistent:
        return {
            "factor_id": factor_id,
            "factor_degree": degree,
            "lagrange_rank": None,
            "lagrange_inconsistent": True,
            "free_dimension_before_wall_equation": None,
            "restricted_wall_polynomial": [],
            "restricted_discriminant": None,
            "critical_count_over_algebraic_closure": 0,
            "status": "GENERIC_EMPTY",
        }

    free = tuple(column for column in range(9) if column not in pivots)
    particular = [Fraction(0) for _ in range(9)]
    for row_index, pivot in enumerate(pivots):
        particular[pivot] = reduced[row_index][9]
    basis = []
    for free_column in free:
        vector = [Fraction(0) for _ in range(9)]
        vector[free_column] = 1
        for row_index, pivot in enumerate(pivots):
            vector[pivot] = -reduced[row_index][free_column]
        basis.append(vector)

    h_particular = matvec(hessian, particular)
    restricted = {}
    zero = (0,) * len(free)
    restricted_constant = constant + dot(linear, particular) + dot(particular, h_particular) / 2
    if restricted_constant:
        restricted[zero] = restricted_constant
    gradient_at_particular = [
        h_particular[index] + linear[index] for index in range(9)
    ]
    for index, vector in enumerate(basis):
        coefficient = dot(gradient_at_particular, vector)
        if coefficient:
            exponent = [0] * len(free)
            exponent[index] = 1
            restricted[tuple(exponent)] = coefficient
    for left, first in enumerate(basis):
        h_first = matvec(hessian, first)
        for right in range(left, len(basis)):
            second = basis[right]
            coefficient = dot(h_first, second)
            if left == right:
                coefficient /= 2
            if coefficient:
                exponent = [0] * len(free)
                exponent[left] += 1
                exponent[right] += 1
                restricted[tuple(exponent)] = (
                    restricted.get(tuple(exponent), Fraction(0)) + coefficient
                )

    restricted = {key: value for key, value in restricted.items() if value}
    restricted_degree = max(map(sum, restricted), default=-1)
    dimension = len(free)
    discriminant = None
    if dimension == 0:
        if restricted:
            status, critical_count = "GENERIC_EMPTY", 0
        else:
            status, critical_count = "GENERIC_SIMPLE", 1
    elif not restricted:
        status, critical_count = "NONGENERIC_POSITIVE_DIMENSION", None
    elif restricted_degree == 0:
        status, critical_count = "GENERIC_EMPTY", 0
    elif dimension >= 2:
        status, critical_count = "NONGENERIC_POSITIVE_DIMENSION", None
    elif restricted_degree == 1:
        status, critical_count = "GENERIC_SIMPLE", 1
    else:
        coefficients = {exponent[0]: value for exponent, value in restricted.items()}
        a = coefficients.get(2, Fraction(0))
        b = coefficients.get(1, Fraction(0))
        c = coefficients.get(0, Fraction(0))
        value = b * b - 4 * a * c
        discriminant = fraction_text(value)
        if value:
            status, critical_count = "GENERIC_SIMPLE", 2
        else:
            status, critical_count = "NONGENERIC_REPEATED_CRITICAL_POINT", 1
    serialized = [
        [list(exponent), fraction_text(coefficient)]
        for exponent, coefficient in sorted(restricted.items())
    ]
    return {
        "factor_id": factor_id,
        "factor_degree": degree,
        "lagrange_rank": len(pivots),
        "lagrange_inconsistent": False,
        "free_dimension_before_wall_equation": dimension,
        "restricted_wall_polynomial": serialized,
        "restricted_discriminant": discriminant,
        "critical_count_over_algebraic_closure": critical_count,
        "status": status,
    }


def load_source():
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    active = tuple(row["factor_id"] for row in inventory["literal_rows"])
    occurrences_by_factor = defaultdict(list)
    with np.load(FACTOR_PATH, allow_pickle=False) as source:
        occurrences = tuple(tuple(map(int, row)) for row in source["occurrence_fourset"])
        occurrence_ids = tuple(map(int, source["occurrence_factor"]))
        offsets = tuple(map(int, source["factor_offset"]))
        exponents = source["factor_exponent"]
        coefficients = source["factor_coefficient"]
    occurrence_factor = {}
    for occurrence, factor in zip(occurrences, occurrence_ids, strict=True):
        require(occurrence not in occurrence_factor, "duplicate occurrence")
        occurrence_factor[occurrence] = factor
        occurrences_by_factor[factor].append(occurrence)
    require(len(occurrences_by_factor) == 26_740, "global factor census")
    factor_occurrence = {
        factor: members[0] for factor, members in occurrences_by_factor.items()
    }
    polynomials = {}
    for factor in active:
        start, stop = offsets[factor], offsets[factor + 1]
        polynomials[factor] = {
            tuple(map(int, exponents[position])): int(coefficients[position])
            for position in range(start, stop)
        }
    return inventory, active, occurrence_factor, occurrences_by_factor, factor_occurrence, polynomials


def exact_replay():
    (
        inventory,
        active,
        occurrence_factor,
        occurrences_by_factor,
        factor_occurrence,
        polynomials,
    ) = load_source()
    active_set = frozenset(active)
    require(len(active_set) == len(active) == 3_539, "active factor census")

    # Independently verify that factor equality descends under adjacent label
    # transpositions on every active occurrence before using representatives.
    for adjacent in range(7):
        permutation = list(range(8))
        permutation[adjacent], permutation[adjacent + 1] = (
            permutation[adjacent + 1], permutation[adjacent]
        )
        mapping = triple_map(tuple(permutation))
        for factor in active:
            images = {
                occurrence_factor[transform_occurrence(member, mapping)]
                for member in occurrences_by_factor[factor]
            }
            require(len(images) == 1, "active factor action is not well-defined")

    stabilizer = []
    rejection_probes = Counter()
    domain_rows = []
    witness_digest = hashlib.sha256()
    for permutation in permutations(range(8)):
        mapping = triple_map(permutation)
        preserved = True
        witness_factor = None
        witness_image = None
        probes = 0
        for factor in active:
            probes += 1
            image = occurrence_factor[
                transform_occurrence(factor_occurrence[factor], mapping)
            ]
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
        witness_digest.update(repr(row).encode("ascii"))
        domain_rows.append(row)
    require(stabilizer == [tuple(range(8))], "active-set stabilizer")

    low_degree = tuple(
        factor for factor in active if max(map(sum, polynomials[factor])) <= 2
    )
    require(len(low_degree) == 83, "low-degree factor census")
    projection_rows = [classify_factor(factor, polynomials[factor]) for factor in low_degree]
    return {
        "inventory": inventory,
        "stabilizer": stabilizer,
        "rejection_probe_census": {
            str(key): value for key, value in sorted(rejection_probes.items())
        },
        "witness_digest": witness_digest.hexdigest(),
        "domain_rows": domain_rows,
        "projection_rows": projection_rows,
        "status_census": dict(sorted(Counter(row["status"] for row in projection_rows).items())),
        "nongeneric": [
            row["factor_id"]
            for row in projection_rows
            if row["status"].startswith("NONGENERIC")
        ],
    }


def validate(candidate: dict, exact: dict) -> None:
    require(candidate["format"] == "d9-fixed-domain-incidence-gate2-preflight-v1", "format")
    require(candidate["base_revision"] == EXPECTED_BASE, "base revision")
    require(candidate["base_tree"] == EXPECTED_TREE, "base tree")
    for relative, expected in candidate["source_pins"].items():
        path = ROOT / relative
        require(path.is_file(), f"missing source {relative}")
        require(sha256(path) == expected, f"source drift {relative}")

    domain = candidate["fixed_domain"]
    require(domain["parent_index"] == exact["inventory"]["parent_index"] == 2_599, "parent")
    require(domain["family"] == exact["inventory"]["family"] == "S12,37", "family")
    require(domain["active_factors"] == 3_539, "active factors")
    require(domain["label_permutations_checked"] == 40_320, "permutation census")
    require(domain["active_set_stabilizer_order"] == len(exact["stabilizer"]) == 1, "stabilizer order")
    require(domain["active_set_stabilizer"] == [list(exact["stabilizer"][0])], "stabilizer elements")
    require(domain["active_set_orbit_size"] == 40_320, "active-set orbit")
    require(domain["rejected_permutations"] == 40_319, "rejected permutations")
    require(domain["rejection_probe_census"] == exact["rejection_probe_census"], "rejection probes")
    require(domain["action_witness_semantic_sha256"] == exact["witness_digest"], "action witness digest")

    pairs = candidate["pair_frontier"]
    require(pairs["unfiltered_active_pairs"] == comb(3_539, 2) == 6_260_491, "unfiltered pair count")
    require(pairs["fixed_domain_stabilizer_pair_orbits"] == 6_260_491, "pair orbit count")
    require(pairs["global_s8_ambient_pair_orbits"] == 9_476, "ambient pair census")
    require(pairs["global_s8_preserves_fixed_active_set"] is False, "global quotient preservation")
    require(pairs["global_9476_quotient_authorized_for_fixed_domain"] is False, "global quotient authorization")
    require(pairs["pair_system_budget"] == 96_461, "pair budget")
    require(pairs["pair_gate_pass"] is False, "pair gate")
    require(pairs["complete_source_derived_nonemptiness_filter"] == "ABSENT", "incidence filter")
    require(
        pairs["burnside_rows"]
        == [{
            "permutation": list(range(8)),
            "fixed_factors": 3_539,
            "fixed_factors_under_square": 3_539,
            "fixed_unordered_pairs": 6_260_491,
        }],
        "Burnside rows",
    )

    projection = candidate["projection_screen"]
    require(projection["vector"] == list(PROJECTION), "projection vector")
    require(projection["screened_degrees"] == [1, 2], "screened degrees")
    require(projection["screened_factor_count"] == 83, "screened factor count")
    require(projection["unscreened_factor_count"] == 3_456, "unscreened factor count")
    require(projection["rows"] == exact["projection_rows"], "projection rows")
    require(projection["status_census"] == exact["status_census"], "projection status census")
    require(projection["nongeneric_factor_ids"] == exact["nongeneric"], "nongeneric factors")
    require(projection["low_degree_specialization_pass"] is False, "low-degree projection gate")
    require(projection["complete_projection_specialization_certificate"] is False, "complete projection certificate")

    digest = hashlib.sha256()
    digest.update(b"d9-fixed-domain-incidence-gate2-preflight-v1\0")
    digest.update(repr(exact["domain_rows"]).encode("ascii"))
    digest.update(repr(exact["projection_rows"]).encode("ascii"))
    require(candidate["semantic_sha256"] == digest.hexdigest(), "semantic digest")
    require(candidate["endpoint"] == "LOW_DEGREE_PROJECTION_SPECIALIZATION_IS_NONGENERIC", "endpoint")
    require(candidate["classification"] == "EXACT_NEGATIVE_PROJECTION_ENDPOINT", "classification")
    require(candidate["critical_systems_solved"] == 0, "critical systems solved")
    require(candidate["critical_enumeration_authorized"] is False, "critical authorization")
    require(candidate["theorem_ledger"] == "2/9", "ledger")


def hostile_mutations(stored: dict, exact: dict) -> None:
    mutations = []
    candidate = deepcopy(stored); candidate["fixed_domain"]["active_set_stabilizer_order"] = 2; mutations.append((candidate, "stabilizer order"))
    candidate = deepcopy(stored); candidate["pair_frontier"]["fixed_domain_stabilizer_pair_orbits"] = 9_476; mutations.append((candidate, "pair orbit count"))
    candidate = deepcopy(stored); candidate["pair_frontier"]["global_9476_quotient_authorized_for_fixed_domain"] = True; mutations.append((candidate, "global quotient authorization"))
    candidate = deepcopy(stored); candidate["projection_screen"]["rows"][0]["status"] = "GENERIC_EMPTY"; mutations.append((candidate, "projection rows"))
    candidate = deepcopy(stored); candidate["projection_screen"]["nongeneric_factor_ids"].pop(); mutations.append((candidate, "nongeneric factors"))
    candidate = deepcopy(stored); candidate["projection_screen"]["complete_projection_specialization_certificate"] = True; mutations.append((candidate, "complete projection certificate"))
    candidate = deepcopy(stored); candidate["critical_enumeration_authorized"] = True; mutations.append((candidate, "critical authorization"))
    candidate = deepcopy(stored); candidate["theorem_ledger"] = "3/9"; mutations.append((candidate, "ledger"))
    rejected = 0
    for candidate, expected in mutations:
        try:
            validate(candidate, exact)
        except ValueError as error:
            require(expected in str(error), f"wrong hostile rejection: {error}")
            rejected += 1
            continue
        raise ValueError(f"hostile mutation accepted: {expected}")
    require(rejected == 8, "hostile rejection census")


def main() -> None:
    stored = json.loads(CANDIDATE_PATH.read_text(encoding="utf-8"))
    print("independently rebuilding active factor action", flush=True)
    exact = exact_replay()
    validate(stored, exact)
    hostile_mutations(stored, exact)
    print("PASS D9 fixed-domain incidence gate-2 preflight")
    print("stabilizer=1 pair_orbits=6260491 pair_budget=96461")
    print("projection", exact["status_census"])
    print("hostile_mutations=8 critical_enumeration=DENIED ledger=2/9")


if __name__ == "__main__":
    main()
