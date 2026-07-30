"""Standalone exact checks for all Stage 2c-2 artifacts.

This checker intentionally reconstructs the row model from the reference
JSON and uses only exact integer/Fraction arithmetic for the coverage map.
Additional symbolic-artifact checks are added by later Stage 2c-2 phases.
"""
from __future__ import annotations

import gzip
import json
import math
import time
from fractions import Fraction

from common import (
    CHI,
    DET_ABS,
    HERE,
    MASK20,
    PAIRS,
    REFERENCE,
    REPRESENTATIVES,
    TRIPLES,
    U_INTS,
    VALID_BITS,
    check_sparse_kernel,
    class_pattern,
    full_system_rows,
    full_system_rows_for_split,
    lift_reduced_certificate,
    reduced_equal_pair_rows,
)


COVERAGE_PATH = HERE / "equal_pair_coverage.json.gz"
COEFFICIENTWISE_PATH = HERE / "coefficientwise_mechanisms.json.gz"
BOUNDARY_PATH = HERE / "coefficientwise_boundary.json.gz"
GP_PATH = HERE / "gp_degree3_results.json.gz"
CANARIES = ((10070, 1), (25998, 2))


def load_gz(path):
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def check_reference():
    assert len(REFERENCE["chambers"]) == 22
    assert REFERENCE["n_valid_labeled"] == 33140
    assert REFERENCE["n_global_flip_classes"] == 16570
    assert len(REPRESENTATIVES) == 16570
    assert len(VALID_BITS) == len(set(VALID_BITS)) == 33140
    assert all(
        representative ^ MASK20 in set(VALID_BITS)
        for representative in REPRESENTATIVES
    )
    assert tuple(tuple(pair) for pair in REFERENCE["pairs_in_class_order"]) == PAIRS


def check_coverage():
    payload = load_gz(COVERAGE_PATH)
    assert payload["schema"] == 1
    assert payload["status"] == "complete_exact_labeled_sweep"
    assert tuple(tuple(row) for row in payload["U_ints"]) == U_INTS
    assert payload["n_valid_labeled_sigmas"] == 33140
    assert payload["n_systems"] == 66280

    patterns = {class_pattern(bits) for bits in VALID_BITS}
    assert len(patterns) == payload["n_distinct_class_patterns"]
    assert set(payload["pattern_multiplicities"]) == patterns
    assert sum(payload["pattern_multiplicities"].values()) == 33140

    expected_order = [
        (bits, k)
        for bits in VALID_BITS
        for k in (1, 2)
    ]
    systems = payload["systems"]
    assert len(systems) == len(expected_order)
    counts = {
        "T_INDEPENDENTLY_COVERED": {"1": 0, "2": 0, "total": 0},
        "HARD": {"1": 0, "2": 0, "total": 0},
    }
    canary_set = set(CANARIES)
    for position, (bits, k, key, status) in enumerate(systems):
        assert (bits, k) == expected_order[position]
        pattern = class_pattern(bits)
        assert key == f"{k}:{pattern}"
        result = payload["pattern_results"][key]
        assert status == result["status"]
        assert status in counts
        counts[status][str(k)] += 1
        counts[status]["total"] += 1

        eligible, rows = reduced_equal_pair_rows(pattern, k)
        assert list(eligible) == result["eligible_classes"]
        if status == "T_INDEPENDENTLY_COVERED":
            certificate = tuple(
                (int(row), int(value))
                for row, value in result["reduced_certificate"]
            )
            assert check_sparse_kernel(rows, certificate)
            lifted = lift_reduced_certificate(bits, pattern, certificate)
            assert check_sparse_kernel(full_system_rows(bits, k), lifted)
            assert (bits, k) not in canary_set
        else:
            witness = [
                Fraction(value) for value in result["strict_primal_witness"]
            ]
            assert len(witness) == 5
            margins = [
                sum(Fraction(a) * b for a, b in zip(row, witness))
                for row in rows
            ]
            assert min(margins) > 0
            assert Fraction(result["minimum_margin"]) == min(margins)

        if (position + 1) % 10000 == 0:
            print(f"coverage exact checks {position + 1}/66280", flush=True)

    assert counts == payload["counts"]
    assert counts["T_INDEPENDENTLY_COVERED"]["total"] + counts["HARD"]["total"] == 66280
    recorded_canaries = {
        (item["sigma_bits"], item["k"]): item
        for item in payload["canaries"]
    }
    assert set(recorded_canaries) == canary_set
    for target in canary_set:
        assert recorded_canaries[target]["expected"] == "HARD"
        assert recorded_canaries[target]["outcome"] == "HARD"
    return counts


def single_class_criterion(pattern, k):
    split = tuple(1 if t < k else -1 for t in range(5))
    favorable = []
    for class_index, ((i, j), marker) in enumerate(zip(PAIRS, pattern)):
        if marker == "x":
            continue
        q = 1 if marker == "+" else -1
        if all(q * split[t] == -1 for t in range(5) if t not in (i, j)):
            favorable.append(class_index)
    return favorable


def check_coefficientwise_boundary():
    coverage = load_gz(COVERAGE_PATH)
    boundary = load_gz(BOUNDARY_PATH)
    assert boundary["schema"] == 1
    assert boundary["status"] == "complete_exact_all_degree_boundary"
    assert boundary["formal_D_order"] == [
        "D" + "".join(map(str, triple)) for triple in TRIPLES
    ]
    counts = {
        "SINGLE_CLASS_IF_AND_ONLY_IF": {"1": 0, "2": 0, "total": 0},
        "ALL_DEGREES_IMPOSSIBLE": {"1": 0, "2": 0, "total": 0},
    }
    for bits, k, key, _ in coverage["systems"]:
        pattern = class_pattern(bits)
        result = boundary["pattern_results"][key]
        favorable = single_class_criterion(pattern, k)
        if favorable:
            assert result["status"] == "SINGLE_CLASS_IF_AND_ONLY_IF"
            assert result["favorable_classes"] == favorable
            # Direct ordinary-polynomial sign check of the template.
            split = tuple(1 if t < k else -1 for t in range(5))
            class_index = favorable[0]
            i, j = PAIRS[class_index]
            q = 1 if pattern[class_index] == "+" else -1
            assert all(
                -2 * q * split[t] > 0
                for t in range(5) if t not in (i, j)
            )
        else:
            assert result["status"] == "ALL_DEGREES_IMPOSSIBLE"
            eligible = result["eligible_classes"]
            formal_d = [
                Fraction(value)
                for value in result["formal_D_strict_primal_witness"]
            ]
            assert len(formal_d) == 10 and min(formal_d) > 0
            split = tuple(1 if t < k else -1 for t in range(5))
            margins = []
            for class_index in eligible:
                i, j = PAIRS[class_index]
                q = 1 if pattern[class_index] == "+" else -1
                margin = sum(
                    q * split[t] * formal_d[TRIPLES.index(tuple(sorted((t, i, j))))]
                    for t in range(5) if t not in (i, j)
                )
                margins.append(margin)
            margins.extend(formal_d)
            assert min(margins) > 0
            assert Fraction(result["minimum_margin"]) == min(margins)
        status = result["status"]
        counts[status][str(k)] += 1
        counts[status]["total"] += 1
    assert counts == boundary["labeled_counts"]
    assert counts["SINGLE_CLASS_IF_AND_ONLY_IF"]["total"] == 33437

    # The explicit low-degree enumeration is an independent finite-cone
    # cross-check of the theorem: degree one adds no system.
    mechanisms = load_gz(COEFFICIENTWISE_PATH)
    assert mechanisms["status"] == "complete"
    assert mechanisms["max_degree"] == 1
    assert mechanisms["labeled_system_cumulative_coverage"]["0"]["total"] == 33437
    assert mechanisms["labeled_system_cumulative_coverage"]["1"]["total"] == 33437
    assert set(mechanisms["first_degrees"].values()) == {0}
    return counts


def exponent_value(exponent):
    value = 1
    for triple, power in zip(TRIPLES, exponent):
        value *= DET_ABS[triple] ** power
    return value


def check_gp_search():
    # Importing the generator's quotient construction is not the only check:
    # each accepted symbolic vector is also evaluated independently against
    # the authoritative full numeric row matrix below.
    from gp_degree3_search import (
        GP_GB_D,
        GP_RELATIONS_D,
        NEGATIVE_CANARY,
        normal_forms,
        quotient_matrix,
    )

    payload = load_gz(GP_PATH)
    assert payload["schema"] == 1 and payload["status"] == "complete"
    assert tuple(tuple(row) for row in payload["U_ints"]) == U_INTS
    assert payload["chirotope_signs"] == [CHI[triple] for triple in TRIPLES]
    for relation in GP_RELATIONS_D:
        assert GP_GB_D.reduce(relation)[1] == 0

    forms_by_degree = {}
    research_summary = {}
    negative_seen = set()
    positive_seen = set()
    for item in payload["results"]:
        target = item["target"]
        degree = item["degree"]
        outcome = item["outcome"]
        if degree not in forms_by_degree:
            forms_by_degree[degree] = normal_forms(degree + 1)
        forms = forms_by_degree[degree]
        variables, row_keys, matrix = quotient_matrix(
            int(target["sigma_bits"]),
            tuple(target["split"]),
            degree,
            forms,
        )
        assert outcome["n_variables"] == len(variables)
        assert outcome["n_quotient_rows"] == len(row_keys)

        if outcome["status"] == "EXACT_CELLWIDE_CERTIFICATE":
            certificate = outcome["certificate"]
            assert certificate and len(certificate) == outcome["support_size"]
            coefficients = [Fraction(0)] * len(variables)
            seen = set()
            for index, value in certificate:
                assert index not in seen
                seen.add(index)
                assert 0 <= index < len(variables)
                assert isinstance(value, int) and value > 0
                coefficients[index] = Fraction(value)
            for row in range(matrix.shape[0]):
                start, stop = matrix.indptr[row], matrix.indptr[row + 1]
                total = sum(
                    Fraction(int(matrix.data[position]))
                    * coefficients[matrix.indices[position]]
                    for position in range(start, stop)
                )
                assert total == 0

            # Independent specialization at the exact reference D values:
            # decode every polynomial coefficient, evaluate it, place it on
            # the corresponding full row, and check all eight dot products.
            row_multipliers = {}
            for index, coefficient in certificate:
                kind, row_index, exponent = variables[index]
                value = coefficient * exponent_value(exponent)
                full_row = row_index if kind == "side" else 20 + row_index
                row_multipliers[full_row] = (
                    row_multipliers.get(full_row, 0) + value
                )
            assert row_multipliers and min(row_multipliers.values()) > 0
            full = full_system_rows_for_split(
                int(target["sigma_bits"]), tuple(target["split"])
            )
            totals = [
                sum(
                    row_multipliers.get(row, 0) * full[row][column]
                    for row in row_multipliers
                )
                for column in range(8)
            ]
            assert totals == [0] * 8
        elif outcome["status"] == "EXACT_DEGREE_NO_GO":
            separator = outcome["separator"]
            assert separator is not None
            values = [Fraction(0)] * matrix.shape[0]
            for index, value in separator:
                assert 0 <= index < matrix.shape[0]
                assert isinstance(value, int) and value != 0
                values[index] = Fraction(value)
            transpose = matrix.transpose().tocsr()
            products = []
            for row in range(transpose.shape[0]):
                start, stop = transpose.indptr[row], transpose.indptr[row + 1]
                products.append(sum(
                    Fraction(int(transpose.data[position]))
                    * values[transpose.indices[position]]
                    for position in range(start, stop)
                ))
            assert min(products) > 0
        else:
            raise AssertionError(f"unexpected GP outcome {outcome['status']}")

        if target["id"] == NEGATIVE_CANARY["id"]:
            assert outcome["status"] == "EXACT_DEGREE_NO_GO"
            negative_seen.add(degree)
        elif target["id"] == "POSITIVE_SINGLE_CLASS_CONTROL":
            assert outcome["status"] == "EXACT_CELLWIDE_CERTIFICATE"
            positive_seen.add(degree)
        else:
            key = (degree, outcome["status"])
            research_summary[key] = research_summary.get(key, 0) + 1

    assert negative_seen == positive_seen == set(payload["searched_degrees"])
    witness = [
        Fraction(value)
        for value in NEGATIVE_CANARY["exact_strict_primal_witness"]
    ]
    margins = [
        sum(Fraction(a) * b for a, b in zip(row, witness))
        for row in full_system_rows(0, 1)
    ]
    assert min(margins) > 0
    return research_summary


def main():
    start = time.time()
    check_reference()
    print("checked authoritative reference and labeled sigma set", flush=True)
    counts = check_coverage()
    print(json.dumps(counts, indent=2), flush=True)
    boundary_counts = check_coefficientwise_boundary()
    print("checked all-degree coefficientwise boundary", flush=True)
    print(json.dumps(boundary_counts, indent=2), flush=True)
    gp_summary = check_gp_search()
    print("checked exact GP search certificates and no-go functionals", flush=True)
    print({
        f"degree_{degree}:{status}": count
        for (degree, status), count in sorted(gp_summary.items())
    }, flush=True)
    print(
        f"PASS: all available Stage 2c-2 exact checks completed "
        f"in {time.time() - start:.1f}s",
        flush=True,
    )


if __name__ == "__main__":
    main()
