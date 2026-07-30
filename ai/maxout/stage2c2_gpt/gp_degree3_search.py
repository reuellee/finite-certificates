"""Degree <= 3 T-carrying search modulo the Pluecker ideal.

Side multiplier polynomials have homogeneous degree d.  The five
positive-weight-row multipliers have degree d+1.  Every coefficient is
constrained nonnegative.  Both the three T equations and five weight
equations are imposed in the signed-D quotient ring of the authoritative
reference chirotope.

Float HiGHS calls are discovery aids only.  A success is accepted only
after exact quotient-matrix kernel verification.  An infeasible cone is
reported as exact when a rational separating functional is recovered and
checked with strictly positive value on every multiplier coefficient.
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
import sympy
from scipy.optimize import linprog
from scipy.sparse import coo_matrix, csr_matrix, vstack

from common import (
    CHI,
    HERE,
    MASK20,
    PAIRS,
    REPRESENTATIVES,
    TRIPLES,
    TRIPLE_INDEX,
    U_INTS,
    VALID_BITS,
    class_pattern,
    fraction_text,
    full_system_rows,
    permutation_sign,
    primitive_integer_vector,
)
from coefficientwise_search import monomials_of_degree


COVERAGE_PATH = HERE / "equal_pair_coverage.json.gz"
FAILED100_PATH = HERE.parent / "stage2b_gpt" / "symbolic_gp_results.json"
OUTPUT = HERE / "gp_degree3_results.json.gz"
CHECKPOINT = HERE / "gp_degree3_checkpoint.json.gz"
SEED = 2026073103

# A deliberately invalid side coloring with an exact strict full-system
# primal witness.  No Gordan certificate can exist even at the reference
# point, so any symbolic success is a fatal verifier failure.
NEGATIVE_CANARY = {
    "id": "NEGATIVE_CANARY_BITS0_K1",
    "sigma_bits": 0,
    "split": [1, -1, -1, -1, -1],
    "exact_strict_primal_witness": [
        "0", "0", "0", "1", "1619/440", "447/88", "1201/440", "1"
    ],
}


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


D_VARS = sympy.symbols(" ".join(
    "D" + "".join(map(str, triple)) for triple in TRIPLES
))
D_BY_TRIPLE = dict(zip(TRIPLES, D_VARS))


def signed_d(indices):
    if len(set(indices)) < 3:
        return sympy.Integer(0)
    ordered = tuple(sorted(indices))
    return (
        permutation_sign(indices)
        * CHI[ordered]
        * D_BY_TRIPLE[ordered]
    )


def gp_relations_d():
    relations = []
    for a in range(5):
        b, c, d, e = [index for index in range(5) if index != a]
        relations.append(sympy.expand(
            signed_d((a, b, c)) * signed_d((a, d, e))
            - signed_d((a, b, d)) * signed_d((a, c, e))
            + signed_d((a, b, e)) * signed_d((a, c, d))
        ))
    return tuple(relations)


GP_RELATIONS_D = gp_relations_d()
GP_GB_D = sympy.groebner(GP_RELATIONS_D, *D_VARS, order="grevlex")


def exponent_expr(exponent):
    return sympy.prod(
        variable ** power
        for variable, power in zip(D_VARS, exponent)
        if power
    )


def add_unit(exponent, variable):
    out = list(exponent)
    out[variable] += 1
    return tuple(out)


def normal_forms(degree):
    """Normal forms of every D monomial of one homogeneous degree."""
    forms = {}
    for exponent in monomials_of_degree(degree):
        remainder = GP_GB_D.reduce(exponent_expr(exponent))[1]
        poly = sympy.Poly(remainder, *D_VARS)
        terms = {}
        for monomial, coefficient in poly.terms():
            coefficient = Fraction(coefficient)
            if coefficient.denominator != 1:
                raise AssertionError("nonintegral signed-D normal form")
            terms[tuple(monomial)] = coefficient.numerator
        forms[exponent] = terms
    return forms


def exact_matrix_products(matrix, values):
    products = [Fraction(0) for _ in range(matrix.shape[0])]
    for row in range(matrix.shape[0]):
        start, stop = matrix.indptr[row], matrix.indptr[row + 1]
        products[row] = sum(
            Fraction(int(matrix.data[position]))
            * values[matrix.indices[position]]
            for position in range(start, stop)
        )
    return products


def quotient_matrix(bits, split, degree, forms):
    """Build E with E*c=0 for all eight quotient-ring equations."""
    side_monoms = monomials_of_degree(degree)
    weight_monoms = monomials_of_degree(degree + 1)
    variables = []
    for side in range(20):
        for monomial in side_monoms:
            variables.append(("side", side, monomial))
    for t in range(5):
        for monomial in weight_monoms:
            variables.append(("weight", t, monomial))

    entries = []
    row_keys = set()
    for column, variable in enumerate(variables):
        kind, index, monomial = variable
        if kind == "weight":
            t = index
            for quotient_monomial, coefficient in forms[monomial].items():
                key = ("W", t, quotient_monomial)
                entries.append((key, column, coefficient))
                row_keys.add(key)
            continue

        side = index
        class_index = side // 2
        i, j = PAIRS[class_index]
        sigma = 1 if bits & (1 << side) else -1
        ray = 1 if side % 2 == 0 else -1
        for t in range(5):
            if t in (i, j):
                continue
            triple = tuple(sorted((t, i, j)))
            combined = add_unit(monomial, TRIPLE_INDEX[triple])
            normal = forms[combined]

            # T block: sigma * ray * p_(t,i,j), expressed in positive D.
            t_scalar = (
                sigma
                * ray
                * permutation_sign((t, i, j))
                * CHI[triple]
            )
            for quotient_monomial, coefficient in normal.items():
                key = ("T", t, quotient_monomial)
                entries.append((key, column, t_scalar * coefficient))
                row_keys.add(key)

            # Weight block: sigma * split_t * D_tij.
            w_scalar = sigma * split[t]
            for quotient_monomial, coefficient in normal.items():
                key = ("W", t, quotient_monomial)
                entries.append((key, column, w_scalar * coefficient))
                row_keys.add(key)

    row_keys = tuple(sorted(row_keys))
    row_index = {key: index for index, key in enumerate(row_keys)}
    row_indices = [row_index[key] for key, _, _ in entries]
    columns = [column for _, column, _ in entries]
    data = [coefficient for _, _, coefficient in entries]
    matrix = coo_matrix(
        (data, (row_indices, columns)),
        shape=(len(row_keys), len(variables)),
        dtype=float,
    ).tocsr()
    matrix.sum_duplicates()
    matrix.eliminate_zeros()
    return variables, row_keys, matrix


def solve_exact_support(matrix, support):
    """Exact RREF of E_support*y=0, sum(y)=1."""
    support = list(support)
    m = len(support)
    equations = []
    csc = matrix[:, support].tocsr()
    for row in range(csc.shape[0]):
        start, stop = csc.indptr[row], csc.indptr[row + 1]
        if start == stop:
            continue
        equation = [Fraction(0)] * (m + 1)
        for position in range(start, stop):
            equation[csc.indices[position]] = Fraction(
                int(csc.data[position])
            )
        equations.append(equation)
    equations.append([Fraction(1)] * m + [Fraction(1)])

    pivot_row = 0
    pivots = {}
    for column in range(m):
        chosen = next(
            (
                row
                for row in range(pivot_row, len(equations))
                if equations[row][column] != 0
            ),
            None,
        )
        if chosen is None:
            continue
        equations[pivot_row], equations[chosen] = (
            equations[chosen],
            equations[pivot_row],
        )
        pivot = equations[pivot_row][column]
        equations[pivot_row] = [
            value / pivot for value in equations[pivot_row]
        ]
        for row in range(len(equations)):
            if row == pivot_row or equations[row][column] == 0:
                continue
            factor = equations[row][column]
            equations[row] = [
                a - factor * b
                for a, b in zip(equations[row], equations[pivot_row])
            ]
        pivots[column] = pivot_row
        pivot_row += 1
    for equation in equations:
        if all(equation[column] == 0 for column in range(m)):
            if equation[m] != 0:
                return None
    if len(pivots) != m:
        return None
    solution = [equations[pivots[column]][m] for column in range(m)]
    if any(value <= 0 for value in solution):
        return None
    return solution


def primitive_sparse(support, values):
    common = 1
    for value in values:
        common = math.lcm(common, value.denominator)
    integers = [
        value.numerator * (common // value.denominator)
        for value in values
    ]
    divisor = 0
    for value in integers:
        divisor = math.gcd(divisor, abs(value))
    return [
        [int(index), int(value // divisor)]
        for index, value in zip(support, integers)
        if value
    ]


def find_exact_kernel(matrix, rng, attempts=6):
    nvariables = matrix.shape[1]
    equality = vstack([
        matrix,
        csr_matrix(np.ones((1, nvariables))),
    ], format="csr")
    rhs = np.r_[np.zeros(matrix.shape[0]), 1.0]
    objectives = [np.zeros(nvariables)]
    objectives.extend(rng.normal(size=nvariables) for _ in range(attempts - 1))
    statuses = []
    for objective in objectives:
        result = linprog(
            objective,
            A_eq=equality,
            b_eq=rhs,
            bounds=[(0, None)] * nvariables,
            method="highs",
        )
        statuses.append(int(result.status))
        if result.status != 0:
            if result.status == 2:
                break
            continue
        maximum = max(float(np.max(result.x)), 1.0)
        for tolerance in (1e-7, 1e-9, 1e-11, 1e-13):
            support = [
                index
                for index, value in enumerate(result.x)
                if value > tolerance * maximum
            ]
            values = solve_exact_support(matrix, support)
            if values is None:
                continue
            sparse = primitive_sparse(support, values)
            full = [Fraction(0)] * nvariables
            for index, value in sparse:
                full[index] = Fraction(value)
            if any(exact_matrix_products(matrix, full)):
                continue
            return sparse, statuses
    return None, statuses


def exactify_signed(values, predicate):
    maximum = max((abs(float(value)) for value in values), default=0.0)
    if maximum == 0:
        return None
    for bound in (100, 10_000, 1_000_000, 100_000_000):
        rational = [
            Fraction(float(value)).limit_denominator(bound)
            for value in values
        ]
        if predicate(rational):
            return primitive_integer_vector(rational)
    return None


def find_exact_separator(matrix):
    """Find unrestricted lambda with E^T*lambda > 0."""
    transpose = matrix.transpose().tocsr()
    result = linprog(
        np.zeros(matrix.shape[0]),
        A_ub=-transpose,
        b_ub=-np.ones(matrix.shape[1]),
        bounds=[(None, None)] * matrix.shape[0],
        method="highs",
    )
    if result.status != 0:
        return None, int(result.status)

    def predicate(rational):
        return all(
            value > 0 for value in exact_matrix_products(transpose, rational)
        )

    exact = exactify_signed(result.x, predicate)
    if exact is None:
        return None, int(result.status)
    sparse = [
        [index, int(value)]
        for index, value in enumerate(exact)
        if value
    ]
    return sparse, int(result.status)


def select_targets():
    coverage = load_gz(COVERAGE_PATH)
    system_status = {
        (bits, k): status
        for bits, k, _, status in coverage["systems"]
    }
    representative_set = set(REPRESENTATIVES)
    canonical_hard = {1: [], 2: []}
    for bits, k, _, status in coverage["systems"]:
        if (
            status == "HARD"
            and bits in representative_set
            and len(canonical_hard[k]) < 10
        ):
            canonical_hard[k].append(bits)

    targets = []
    seen = set()

    def add(target):
        key = (target["sigma_bits"], tuple(target["split"]))
        if key not in seen:
            seen.add(key)
            targets.append(target)

    for k in (1, 2):
        split = [1 if t < k else -1 for t in range(5)]
        for rank, bits in enumerate(canonical_hard[k], 1):
            add({
                "id": f"CANONICAL_HARD_K{k}_{rank:02d}",
                "sigma_bits": bits,
                "split": split,
                "source": "objective1 canonical representative HARD",
                "objective1_status": system_status[(bits, k)],
            })

    failed = json.loads(FAILED100_PATH.read_text(encoding="utf-8"))
    for entry in failed["results"]:
        bits = int(entry["mapped_sigma_bits"])
        split = list(map(int, entry["mapped_split"]))
        objective1_status = "not_in_k12_prefix_scope"
        if split == [1, -1, -1, -1, -1]:
            objective1_status = system_status[(bits, 1)]
        elif split == [1, 1, -1, -1, -1]:
            objective1_status = system_status[(bits, 2)]
        add({
            "id": f"FAILED100_RANK_{entry['rank']:03d}",
            "sigma_bits": bits,
            "split": split,
            "source": "stage2b_gpt/symbolic_gp_results.json",
            "failed100_rank": entry["rank"],
            "objective1_status": objective1_status,
        })
    return targets


def positive_control():
    coverage = load_gz(COVERAGE_PATH)
    for bits, k, _, status in coverage["systems"]:
        if status != "T_INDEPENDENTLY_COVERED":
            continue
        pattern = class_pattern(bits)
        split = [1 if t < k else -1 for t in range(5)]
        for class_index, ((i, j), marker) in enumerate(zip(PAIRS, pattern)):
            if marker == "x":
                continue
            q = 1 if marker == "+" else -1
            if all(q * split[t] == -1 for t in range(5) if t not in (i, j)):
                return {
                    "id": "POSITIVE_SINGLE_CLASS_CONTROL",
                    "sigma_bits": bits,
                    "split": split,
                }
    raise AssertionError("no positive control found")


def check_negative_canary_primal():
    witness = [
        Fraction(value) for value in NEGATIVE_CANARY["exact_strict_primal_witness"]
    ]
    rows = full_system_rows(0, 1)
    margins = [
        sum(Fraction(a) * b for a, b in zip(row, witness))
        for row in rows
    ]
    if min(margins) <= 0:
        raise AssertionError("negative canary witness is not strict")
    return fraction_text(min(margins))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--degrees", default="0,1,2,3",
        help="comma-separated side-multiplier degrees",
    )
    parser.add_argument("--limit-targets", type=int)
    args = parser.parse_args()
    degrees = tuple(int(value) for value in args.degrees.split(","))
    if any(degree < 0 or degree > 3 for degree in degrees):
        raise ValueError("degrees must lie in 0..3")

    start = time.time()
    rng = np.random.default_rng(SEED)
    canary_margin = check_negative_canary_primal()
    targets = select_targets()
    if args.limit_targets is not None:
        targets = targets[:args.limit_targets]
    controls = [NEGATIVE_CANARY, positive_control()]
    all_targets = controls + targets
    results = []
    degree_metadata = {}

    for degree in degrees:
        forms = normal_forms(degree + 1)
        degree_metadata[str(degree)] = {
            "n_side_monomials": len(monomials_of_degree(degree)),
            "n_weight_monomials": len(monomials_of_degree(degree + 1)),
            "n_quotient_input_monomials": len(forms),
        }
        print(
            f"degree {degree}: normal forms ready "
            f"({len(forms)} degree-{degree + 1} monomials)",
            flush=True,
        )
        for position, target in enumerate(all_targets, 1):
            bits = int(target["sigma_bits"])
            split = tuple(int(value) for value in target["split"])
            variables, row_keys, matrix = quotient_matrix(
                bits, split, degree, forms
            )
            certificate, lp_statuses = find_exact_kernel(matrix, rng)
            if certificate is not None:
                outcome = {
                    "status": "EXACT_CELLWIDE_CERTIFICATE",
                    "certificate": certificate,
                    "support_size": len(certificate),
                    "n_variables": len(variables),
                    "n_quotient_rows": len(row_keys),
                    "lp_statuses": lp_statuses,
                }
            else:
                separator, separator_status = find_exact_separator(matrix)
                outcome = {
                    "status": (
                        "EXACT_DEGREE_NO_GO"
                        if separator is not None
                        else "EMPIRICAL_NO_GO"
                    ),
                    "separator": separator,
                    "n_variables": len(variables),
                    "n_quotient_rows": len(row_keys),
                    "lp_statuses": lp_statuses,
                    "separator_lp_status": separator_status,
                }
            if target["id"] == NEGATIVE_CANARY["id"]:
                if outcome["status"] == "EXACT_CELLWIDE_CERTIFICATE":
                    raise RuntimeError(
                        f"CANARY FAILURE: negative control passed at degree {degree}"
                    )
                print(
                    f"degree {degree} negative canary PASS "
                    f"({outcome['status']})",
                    flush=True,
                )
            if target["id"] == "POSITIVE_SINGLE_CLASS_CONTROL":
                if outcome["status"] != "EXACT_CELLWIDE_CERTIFICATE":
                    raise RuntimeError(
                        f"positive control failed at degree {degree}"
                    )
                print(
                    f"degree {degree} positive control PASS "
                    f"(support {outcome['support_size']})",
                    flush=True,
                )

            results.append({
                "target": target,
                "degree": degree,
                "outcome": outcome,
            })
            if position % 10 == 0 or position == len(all_targets):
                successes = sum(
                    item["degree"] == degree
                    and item["outcome"]["status"] == "EXACT_CELLWIDE_CERTIFICATE"
                    and item["target"]["id"] not in {
                        "POSITIVE_SINGLE_CLASS_CONTROL",
                        NEGATIVE_CANARY["id"],
                    }
                    for item in results
                )
                print(
                    f"degree {degree}: {position}/{len(all_targets)}, "
                    f"research successes={successes}, "
                    f"elapsed={time.time() - start:.1f}s",
                    flush=True,
                )

        checkpoint = {
            "schema": 1,
            "status": "checkpoint",
            "completed_degrees": [
                value for value in degrees if value <= degree
            ],
            "U_ints": [list(row) for row in U_INTS],
            "negative_canary_minimum_margin": canary_margin,
            "degree_metadata": degree_metadata,
            "results": results,
        }
        write_json_gz(CHECKPOINT, checkpoint)

    payload = {
        "schema": 1,
        "status": "complete",
        "searched_degrees": list(degrees),
        "U_ints": [list(row) for row in U_INTS],
        "chirotope_signs": [CHI[triple] for triple in TRIPLES],
        "gp_relations_signed_D": [str(relation) for relation in GP_RELATIONS_D],
        "target_selection": (
            "First ten canonical objective-1 HARD representatives at each "
            "split, then all 100 mapped failed targets; duplicates removed. "
            "A strict-feasible invalid-sigma negative canary and a known "
            "single-class positive control are run first at every degree."
        ),
        "n_research_targets": len(targets),
        "negative_canary_minimum_margin": canary_margin,
        "degree_metadata": degree_metadata,
        "results": results,
        "seed_for_float_support_hints": SEED,
        "elapsed_seconds": time.time() - start,
    }
    write_json_gz(OUTPUT, payload)
    summary = {}
    for degree in degrees:
        subset = [
            item for item in results
            if item["degree"] == degree
            and item["target"]["id"] not in {
                "POSITIVE_SINGLE_CLASS_CONTROL",
                NEGATIVE_CANARY["id"],
            }
        ]
        summary[str(degree)] = {
            status: sum(item["outcome"]["status"] == status for item in subset)
            for status in (
                "EXACT_CELLWIDE_CERTIFICATE",
                "EXACT_DEGREE_NO_GO",
                "EMPIRICAL_NO_GO",
            )
        }
    print(json.dumps(summary, indent=2), flush=True)
    print(f"wrote {OUTPUT} ({OUTPUT.stat().st_size} bytes)", flush=True)


if __name__ == "__main__":
    main()
