#!/usr/bin/env python3
"""Independent exact replay of the hard-canary full-space critical gate.

The tracked artifact contains three residual equations and all 56 formal
height-b Jacobian minors in the normalized nine-variable parent chart.  This
checker recomputes every determinant with its own sparse determinant code,
finds the maximal coordinate subspaces contained in the raw critical ideal,
and pins the parent walls containing those boundary components.

``--modular`` additionally replays the bounded F2/F3 Macaulay diagnostics.
Those ranks are exact finite-field facts but are not characteristic-zero
component or noncompactness certificates.
"""

from __future__ import annotations

import argparse
import hashlib
from itertools import combinations, permutations
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import verify_diag3_polynomial_multivector_height_screen as screen  # noqa: E402


SYSTEM = HERE / "data/DIAG3_triple_fullspace_critical_h1.json"
MANIFEST = HERE / "data/DIAG3_triple_fullspace_critical_h1_manifest.json"
SCHEMA = "diag3-triple-fullspace-critical-system-v1"
MANIFEST_SCHEMA = "diag3-triple-fullspace-critical-gate-v1"
VARIABLES = tuple("abcdefghi")
ZERO = (0,) * 9
HEIGHT = 1
PRESENTATION = (5_563, 16_134, 19_284)
CANONICAL = (5_563, 4_373, 23_221)
PERMUTATION = (6, 2, 5, 8, 3, 4, 1, 7)
EXPECTED_IMAGE = (4_373, 5_563, 23_221)


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def add(left, right):
    answer = dict(left)
    for monomial, coefficient in right.items():
        answer[monomial] = answer.get(monomial, 0) + coefficient
        if not answer[monomial]:
            del answer[monomial]
    return answer


def scale(polynomial, scalar):
    return {
        monomial: scalar * coefficient
        for monomial, coefficient in polynomial.items()
        if scalar * coefficient
    }


def multiply(left, right):
    answer = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial = tuple(
                x + y for x, y in zip(left_monomial, right_monomial)
            )
            answer[monomial] = answer.get(monomial, 0) + (
                left_coefficient * right_coefficient
            )
    return {key: value for key, value in answer.items() if value}


def derivative(polynomial, variable):
    answer = {}
    for monomial, coefficient in polynomial.items():
        if not monomial[variable]:
            continue
        derived = list(monomial)
        scalar = derived[variable]
        derived[variable] -= 1
        answer[tuple(derived)] = coefficient * scalar
    return answer


def determinant3(matrix):
    answer = {}
    for permutation in permutations(range(3)):
        inversions = sum(
            permutation[left] > permutation[right]
            for left in range(3)
            for right in range(left + 1, 3)
        )
        term = {ZERO: -1 if inversions & 1 else 1}
        for row in range(3):
            term = multiply(term, matrix[row][permutation[row]])
        answer = add(answer, term)
    return answer


def independent_minor(residual, columns):
    return determinant3(
        [
            [derivative(residual[row], column) for column in columns]
            for row in range(3)
        ]
    )


def decode_terms(raw):
    answer = {}
    for coefficient, exponent in raw:
        monomial = tuple(int(value) for value in exponent)
        if len(monomial) != 9 or monomial in answer or not coefficient:
            raise AssertionError("noncanonical sparse polynomial encoding")
        answer[monomial] = int(coefficient)
    return answer


def vanishes_on_coordinate_subspace(polynomial, zero_variables):
    zero_variables = set(zero_variables)
    return all(
        any(monomial[variable] for variable in zero_variables)
        for monomial in polynomial
    )


def maximum_dimension_coordinate_subspaces(generators):
    for size in range(10):
        hits = tuple(
            chosen
            for chosen in combinations(range(9), size)
            if all(
                vanishes_on_coordinate_subspace(polynomial, chosen)
                for polynomial in generators
            )
        )
        if hits:
            return hits
    raise AssertionError("coordinate-component search failed")


def factor_map(occurrences, occurrence_factor):
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    mapping = labeled.triple_map(tuple(label - 1 for label in PERMUTATION))
    return tuple(
        labeled.transform_factor(
            factor, mapping, factor_occurrence, occurrence_factor
        )
        for factor in PRESENTATION
    )


def replay_system(manifest):
    if sha256(SYSTEM) != manifest["system_sha256"]:
        raise AssertionError("critical-system artifact digest changed")
    payload = json.loads(SYSTEM.read_text(encoding="ascii"))
    if payload["schema"] != SCHEMA:
        raise AssertionError("critical-system schema changed")
    if tuple(payload["variables"]) != VARIABLES:
        raise AssertionError("normalized variables changed")
    if payload["height_index"] != HEIGHT or payload["height_variable"] != "b":
        raise AssertionError("selected coordinate height changed")
    if tuple(payload["named_presentation"]) != PRESENTATION:
        raise AssertionError("named presentation changed")
    if tuple(payload["canonical_row"]) != CANONICAL:
        raise AssertionError("canonical row changed")
    if tuple(payload["named_to_canonical_permutation"]) != PERMUTATION:
        raise AssertionError("factor-map permutation changed")

    occurrences, occurrence_factor, factor_polynomials = (
        labeled.factor_polynomials()
    )
    if factor_map(occurrences, occurrence_factor) != EXPECTED_IMAGE:
        raise AssertionError("named-to-canonical factor map changed")
    residual = {
        row: factor_polynomials[factor]
        for row, factor in enumerate(PRESENTATION)
    }
    records = payload["equations"]
    if len(records) != 59:
        raise AssertionError("critical equation count changed")
    generators = []
    for row, factor in enumerate(PRESENTATION):
        record = records[row]
        if record["kind"] != "factor" or record["factor"] != factor:
            raise AssertionError("factor equation ordering changed")
        stored = decode_terms(record["terms"])
        if stored != residual[row]:
            raise AssertionError(f"factor equation {factor} changed")
        generators.append(stored)

    formal_columns = tuple(
        combinations(tuple(index for index in range(9) if index != HEIGHT), 3)
    )
    nonzero = 0
    term_count = 0
    degrees = set()
    zero_columns = []
    for record, columns in zip(records[3:], formal_columns):
        if record["kind"] != "height_minor":
            raise AssertionError("height-minor tag changed")
        if tuple(record["columns"]) != columns:
            raise AssertionError("height-minor column ordering changed")
        stored = decode_terms(record["terms"])
        recomputed = independent_minor(residual, columns)
        if stored != recomputed:
            raise AssertionError(f"independent minor mismatch at {columns}")
        generators.append(stored)
        if stored:
            nonzero += 1
            term_count += len(stored)
            degrees.add(max(map(sum, stored)))
        else:
            zero_columns.append(columns)
    report = {
        "formal_minors": len(formal_columns),
        "nonzero_minors": nonzero,
        "zero_minor_columns": [list(columns) for columns in zero_columns],
        "nonzero_minor_terms": term_count,
        "minor_degrees": sorted(degrees),
    }
    if report != manifest["system_census"]:
        raise AssertionError(f"critical-system census changed: {report}")
    height_census = []
    for height in range(9):
        columns = tuple(variable for variable in range(9) if variable != height)
        minors = tuple(
            independent_minor(residual, chosen)
            for chosen in combinations(columns, 3)
        )
        height_census.append(
            {
                "height_index": height,
                "height_variable": VARIABLES[height],
                "nonzero_minors": sum(bool(polynomial) for polynomial in minors),
                "nonzero_minor_terms": sum(len(polynomial) for polynomial in minors),
            }
        )
    if height_census != manifest["coordinate_height_census"]:
        raise AssertionError("coordinate-height census changed")
    minimum = min(row["nonzero_minor_terms"] for row in height_census)
    if [row["height_index"] for row in height_census if row["nonzero_minor_terms"] == minimum] != [HEIGHT]:
        raise AssertionError("height b is no longer the unique leanest coordinate chart")
    return factor_polynomials, tuple(generators)


def replay_boundary_components(manifest, factor_polynomials, generators):
    components = maximum_dimension_coordinate_subspaces(generators)
    stored = tuple(
        tuple(component["zero_variable_indices"])
        for component in manifest["raw_coordinate_boundary_components"]
    )
    if components != stored:
        raise AssertionError(f"raw coordinate components changed: {components}")
    parent_records = labeled.parent_bracket_factors()
    for chosen, record in zip(components, manifest["raw_coordinate_boundary_components"]):
        free = tuple(index for index in range(9) if index not in chosen)
        if tuple(record["free_variable_indices"]) != free:
            raise AssertionError("free-coordinate list changed")
        walls = tuple(
            label
            for label, polynomial, *_rest in parent_records
            if vanishes_on_coordinate_subspace(polynomial, chosen)
        )
        if walls != tuple(record["identically_zero_parent_brackets"]):
            raise AssertionError(f"boundary-wall list changed for {chosen}")
        if len(walls) != 23:
            raise AssertionError("boundary component lost its parent-wall support")
    return components


def modular_report(factor_polynomials):
    residual = {
        row: factor_polynomials[factor]
        for row, factor in enumerate(PRESENTATION)
    }
    parent_records = labeled.parent_bracket_factors()
    result = {}
    for degree, maximum_factors in ((8, 0), (9, 3), (10, 0)):
        _all, cumulative, monomial_index = screen.monomial_tables(degree)
        targets = tuple(
            screen.target_products(parent_records, maximum_factors, degree)
        )
        prime_reports = {}
        for prime in (2, 3):
            report = screen.screen_height(
                residual,
                HEIGHT,
                degree,
                prime,
                targets,
                tuple(record[0] for record in parent_records),
                cumulative,
                monomial_index,
            )
            prime_reports[str(prime)] = {
                "rank": report["rank"],
                "rows_q": report["rows_q"],
                "rows_minor": report["rows_minor"],
                "support_reject": report["support_reject"],
                "modular_tests": report["modular_tests"],
                "hit_count": len(report["hits"]),
            }
        result[str(degree)] = {
            "monomials": len(monomial_index),
            "target_count": len(targets),
            "primes": prime_reports,
        }
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--modular", action="store_true")
    arguments = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["schema"] != MANIFEST_SCHEMA:
        raise AssertionError("critical-gate manifest schema changed")
    for relative, expected in manifest["source_sha256"].items():
        path = HERE / relative
        if sha256(path) != expected:
            raise AssertionError(f"critical-gate source changed: {relative}")
    semantic_payload = dict(manifest)
    expected_semantic = semantic_payload.pop("semantic_sha256")
    actual_semantic = hashlib.sha256(
        json.dumps(
            semantic_payload, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()
    if actual_semantic != expected_semantic:
        raise AssertionError(f"manifest semantic changed: {actual_semantic}")
    factor_polynomials, generators = replay_system(manifest)
    components = replay_boundary_components(
        manifest, factor_polynomials, generators
    )
    decision = manifest["decision"]
    if decision["status"] != "FAIL_CLOSED" or decision["accepted"]:
        raise AssertionError("raw critical-system gate was promoted")
    accounting = manifest["theorem_accounting"]
    if accounting != {
        "final_unresolved_triple_orbits": 1_162_302,
        "score_after": "2/9",
        "score_before": "2/9",
    }:
        raise AssertionError("invalid theorem accounting")
    print("PASS exact 59-equation height-b critical system")
    print("PASS independent sparse determinant replay", manifest["system_census"])
    print("PASS raw ideal contains two maximum-dimensional coordinate four-spaces", components)
    print("PASS each stored four-space lies on 23 pinned parent walls")
    if arguments.modular:
        actual = modular_report(factor_polynomials)
        if actual != manifest["modular_feasibility"]:
            raise AssertionError(f"modular feasibility changed: {actual}")
        print("PASS F2/F3 bounded Macaulay feasibility", actual)
    print("SEMANTIC", actual_semantic)
    print("GATE FAIL_CLOSED: raw critical ideal is not zero-dimensional")
    print("OPEN saturated component-decorated frontier roadmap")
    print("LEDGER 1,162,302 triple orbits unresolved; theorem score remains 2/9")


if __name__ == "__main__":
    main()
