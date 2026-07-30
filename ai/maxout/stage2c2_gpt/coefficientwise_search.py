"""Enumerate coefficientwise-positive equal-pair mechanisms.

For a fixed labeled class pattern and split, write a homogeneous polynomial
multiplier

    y_e(D) = sum_m c[e,m] D^m,  c[e,m] >= 0

on every eligible equal-side class e.  The weight-row multiplier at vertex
t is coefficientwise nonnegative exactly when every coefficient of

    sum_{e not containing t} 2*q_e*s_t*D_{t,e}*y_e(D)

is nonpositive.  This script builds that finite +/-1 cone in each
homogeneous degree.  A success is stored as an exact primitive integer
coefficient vector.  A failure is stored with an exact nonnegative dual
functional whose value is strictly positive on every multiplier variable.

The two mandatory residue canaries are searched first at every degree.
"""
from __future__ import annotations

import argparse
import gzip
import io
import itertools
import json
import math
import time
from fractions import Fraction

import numpy as np
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

from common import (
    HERE,
    PAIRS,
    TRIPLES,
    TRIPLE_INDEX,
    VALID_BITS,
    class_pattern,
    fraction_text,
    primitive_integer_vector,
    split_signs,
)


COVERAGE_PATH = HERE / "equal_pair_coverage.json.gz"
OUTPUT = HERE / "coefficientwise_mechanisms.json.gz"
SEED = 2026073102
CANARIES = ((10070, 1), (25998, 2))


def load_gz(path):
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def write_json_gz(path, payload):
    with path.open("wb") as raw:
        with gzip.GzipFile(
            filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0
        ) as zipped:
            with io.TextIOWrapper(zipped, encoding="utf-8") as text:
                json.dump(payload, text, separators=(",", ":"), sort_keys=True)
                text.write("\n")


def monomials_of_degree(degree):
    out = []
    for factors in itertools.combinations_with_replacement(range(10), degree):
        exponent = [0] * 10
        for factor in factors:
            exponent[factor] += 1
        out.append(tuple(exponent))
    if degree == 0:
        return ((0,) * 10,)
    return tuple(out)


def add_unit(exponent, variable):
    out = list(exponent)
    out[variable] += 1
    return tuple(out)


def coefficient_cone(pattern, k, degree):
    """Return a sparse +/-1 matrix A for A*c <= 0."""
    split = split_signs(k)
    monomials = monomials_of_degree(degree)
    eligible = tuple(
        class_index
        for class_index, marker in enumerate(pattern)
        if marker != "x"
    )
    variables = tuple(
        (class_index, monomial)
        for class_index in eligible
        for monomial in monomials
    )
    terms = []
    constraint_set = set()
    for variable_index, (class_index, monomial) in enumerate(variables):
        i, j = PAIRS[class_index]
        q = 1 if pattern[class_index] == "+" else -1
        for t in range(5):
            if t in (i, j):
                continue
            triple = tuple(sorted((t, i, j)))
            output = (t, add_unit(monomial, TRIPLE_INDEX[triple]))
            sign = q * split[t]
            terms.append((output, variable_index, sign))
            constraint_set.add(output)
    constraints = tuple(sorted(constraint_set))
    constraint_index = {
        constraint: index for index, constraint in enumerate(constraints)
    }
    row_indices = []
    column_indices = []
    data = []
    for output, variable_index, sign in terms:
        row_indices.append(constraint_index[output])
        column_indices.append(variable_index)
        data.append(sign)
    matrix = coo_matrix(
        (data, (row_indices, column_indices)),
        shape=(len(constraints), len(variables)),
        dtype=float,
    ).tocsr()
    return eligible, variables, constraints, matrix


def sparse_exact_products(matrix, values):
    """Compute integer/rational A*x from a SciPy CSR +/-1 matrix."""
    products = [Fraction(0) for _ in range(matrix.shape[0])]
    for row in range(matrix.shape[0]):
        start, stop = matrix.indptr[row], matrix.indptr[row + 1]
        products[row] = sum(
            Fraction(int(matrix.data[position])) * values[matrix.indices[position]]
            for position in range(start, stop)
        )
    return products


def exactify_nonnegative(values, predicate):
    """Rationalize a float vector and retain it only after exact checking."""
    maximum = max((abs(float(value)) for value in values), default=0.0)
    if maximum == 0:
        return None
    for tolerance in (1e-9, 1e-11, 1e-13):
        cleaned = [
            0.0 if abs(float(value)) <= tolerance * maximum else float(value)
            for value in values
        ]
        for bound in (100, 10_000, 1_000_000, 100_000_000):
            rational = [
                Fraction(value).limit_denominator(bound)
                for value in cleaned
            ]
            if any(value < 0 for value in rational) or not any(rational):
                continue
            if predicate(rational):
                return primitive_integer_vector(rational)
    return None


def find_exact_certificate(matrix, rng, attempts=8):
    nvariables = matrix.shape[1]
    if nvariables == 0:
        return None
    equality = np.ones((1, nvariables))
    objectives = [np.zeros(nvariables)]
    objectives.extend(rng.normal(size=nvariables) for _ in range(attempts - 1))
    for objective in objectives:
        result = linprog(
            objective,
            A_ub=matrix,
            b_ub=np.zeros(matrix.shape[0]),
            A_eq=equality,
            b_eq=np.ones(1),
            bounds=[(0, None)] * nvariables,
            method="highs",
        )
        if result.status != 0:
            continue

        def predicate(rational):
            return all(value <= 0 for value in sparse_exact_products(matrix, rational))

        exact = exactify_nonnegative(result.x, predicate)
        if exact is not None:
            return exact
    return None


def find_exact_no_go(matrix):
    """Find lambda>=0 with A^T*lambda strictly positive."""
    nconstraints, nvariables = matrix.shape
    if nvariables == 0:
        return []
    transpose = matrix.transpose().tocsr()
    result = linprog(
        np.zeros(nconstraints),
        A_ub=-transpose,
        b_ub=-np.ones(nvariables),
        bounds=[(0, None)] * nconstraints,
        method="highs",
    )
    if result.status != 0:
        return None

    def predicate(rational):
        return all(
            value > 0 for value in sparse_exact_products(transpose, rational)
        )

    return exactify_nonnegative(result.x, predicate)


def serialize_sparse(values):
    return [
        [index, int(value)]
        for index, value in enumerate(values)
        if value
    ]


def check_certificate(matrix, sparse):
    values = [Fraction(0)] * matrix.shape[1]
    for index, value in sparse:
        values[index] = Fraction(value)
    return bool(sparse) and all(
        product <= 0 for product in sparse_exact_products(matrix, values)
    )


def check_no_go(matrix, sparse):
    if matrix.shape[1] == 0:
        return sparse == []
    values = [Fraction(0)] * matrix.shape[0]
    for index, value in sparse:
        values[index] = Fraction(value)
    return all(
        product > 0
        for product in sparse_exact_products(matrix.transpose().tocsr(), values)
    )


def run_one(pattern, k, degree, rng):
    eligible, variables, constraints, matrix = coefficient_cone(
        pattern, k, degree
    )
    certificate = find_exact_certificate(matrix, rng)
    if certificate is not None:
        sparse = serialize_sparse(certificate)
        if not check_certificate(matrix, sparse):
            raise AssertionError("internal exact certificate failure")
        return {
            "status": "COEFFICIENTWISE_CERTIFICATE",
            "degree": degree,
            "n_variables": len(variables),
            "n_constraints": len(constraints),
            "eligible_classes": list(eligible),
            "coefficient_vector": sparse,
        }
    no_go = find_exact_no_go(matrix)
    if no_go is None:
        raise RuntimeError(
            f"could not exactly classify coefficient cone "
            f"pattern={pattern}, k={k}, degree={degree}"
        )
    sparse = serialize_sparse(no_go)
    if not check_no_go(matrix, sparse):
        raise AssertionError("internal exact no-go failure")
    return {
        "status": "EXACT_DEGREE_NO_GO",
        "degree": degree,
        "n_variables": len(variables),
        "n_constraints": len(constraints),
        "eligible_classes": list(eligible),
        "dual_functional": sparse,
    }


def system_counts(coverage, first_degrees, max_degree):
    counts = {
        str(degree): {"1": 0, "2": 0, "total": 0}
        for degree in range(max_degree + 1)
    }
    for bits, k, key, _ in coverage["systems"]:
        degree = first_degrees.get(key)
        if degree is None:
            continue
        for threshold in range(degree, max_degree + 1):
            counts[str(threshold)][str(k)] += 1
            counts[str(threshold)]["total"] += 1
    return counts


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-degree", type=int, default=3)
    parser.add_argument("--limit", type=int)
    args = parser.parse_args()
    if args.max_degree < 0 or args.max_degree > 3:
        raise ValueError("supported degree range is 0..3")

    start = time.time()
    rng = np.random.default_rng(SEED)
    coverage = load_gz(COVERAGE_PATH)
    patterns = sorted(coverage["pattern_multiplicities"])
    numeric_status = {
        key: result["status"]
        for key, result in coverage["pattern_results"].items()
    }
    first_degrees = {}
    certificates = {}
    degree_no_gos = {}
    canary_ledger = []
    searches = 0

    canary_keys = [
        f"{k}:{class_pattern(bits)}" for bits, k in CANARIES
    ]
    for degree in range(args.max_degree + 1):
        # Mandatory canary-first search at every degree, even though the
        # reference strict-primal witnesses already imply the answer.
        for (bits, k), key in zip(CANARIES, canary_keys):
            pattern = key.split(":", 1)[1]
            result = run_one(pattern, k, degree, rng)
            if result["status"] != "EXACT_DEGREE_NO_GO":
                raise RuntimeError(
                    f"CANARY FAILURE at degree {degree}: bits={bits}, k={k}"
                )
            canary_ledger.append({
                "sigma_bits": bits,
                "k": k,
                "degree": degree,
                "outcome": result,
            })
            print(
                f"degree {degree} canary PASS: bits={bits}, k={k}",
                flush=True,
            )

        search_keys = [
            f"{k}:{pattern}"
            for pattern in patterns
            for k in (1, 2)
            if numeric_status[f"{k}:{pattern}"] == "T_INDEPENDENTLY_COVERED"
            and f"{k}:{pattern}" not in first_degrees
        ]
        if args.limit is not None:
            search_keys = search_keys[: max(0, args.limit - searches)]
        for position, key in enumerate(search_keys, 1):
            k_text, pattern = key.split(":", 1)
            k = int(k_text)
            result = run_one(pattern, k, degree, rng)
            searches += 1
            if result["status"] == "COEFFICIENTWISE_CERTIFICATE":
                first_degrees[key] = degree
                certificates[key] = result
            else:
                degree_no_gos.setdefault(key, {})[str(degree)] = result
            if position % 250 == 0 or position == len(search_keys):
                print(
                    f"degree {degree}: {position}/{len(search_keys)}; "
                    f"new={sum(value == degree for value in first_degrees.values())}; "
                    f"total={len(first_degrees)}; elapsed={time.time() - start:.1f}s",
                    flush=True,
                )
            if args.limit is not None and searches >= args.limit:
                break
        if args.limit is not None and searches >= args.limit:
            break

    complete = args.limit is None
    payload = {
        "schema": 1,
        "status": "complete" if complete else "partial",
        "max_degree": args.max_degree,
        "homogeneous_multiplier_degrees": list(range(args.max_degree + 1)),
        "reference_coverage_artifact": COVERAGE_PATH.name,
        "n_distinct_patterns": len(patterns),
        "n_numeric_covered_pattern_systems": sum(
            status == "T_INDEPENDENTLY_COVERED"
            for status in numeric_status.values()
        ),
        "n_numeric_hard_pattern_systems": sum(
            status == "HARD" for status in numeric_status.values()
        ),
        "first_degrees": first_degrees,
        "certificates": certificates,
        "degree_no_gos": degree_no_gos,
        "canaries": canary_ledger,
        "labeled_system_cumulative_coverage": system_counts(
            coverage, first_degrees, args.max_degree
        ),
        "method": (
            "Exact coefficient cone for homogeneous coefficientwise-nonnegative "
            "equal-pair multiplier polynomials. Success vectors and separating "
            "dual functionals are primitive integers and are checked exactly."
        ),
        "seed_for_float_support_hints": SEED,
        "elapsed_seconds": time.time() - start,
    }
    write_json_gz(OUTPUT, payload)
    print(
        json.dumps(payload["labeled_system_cumulative_coverage"], indent=2),
        flush=True,
    )
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size} bytes)", flush=True)


if __name__ == "__main__":
    main()
