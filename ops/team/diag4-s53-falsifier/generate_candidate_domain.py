#!/usr/bin/env python3
"""Generate the exact row-2599 four-parameter null certificate.

This is discovery/generation code.  The independent replay in
``verify_candidate_domain.py`` does not import it.
"""

from __future__ import annotations

from fractions import Fraction
from itertools import combinations, product
import hashlib
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
SOURCE = REPO / "ai" / "omreal" / "data" / "seeat_parent2599_shatter8.npz"
OUTPUT = HERE / "CANDIDATE_DOMAIN.json"
ZERO = (0, 0, 0, 0)
TRIPLES = tuple(
    sorted(combinations(range(1, 9), 3), key=lambda item: tuple(reversed(item)))
)


def determinant(matrix):
    rows = [[int(value) for value in row] for row in matrix]
    if not rows:
        return 1
    if len(rows) == 1:
        return rows[0][0]
    return sum(
        (-1 if column & 1 else 1)
        * value
        * determinant([row[:column] + row[column + 1 :] for row in rows[1:]])
        for column, value in enumerate(rows[0])
    )


def add(left, right):
    answer = dict(left)
    for monomial, coefficient in right.items():
        answer[monomial] = answer.get(monomial, 0) + coefficient
    return {key: value for key, value in answer.items() if value}


def scale(polynomial, scalar):
    return {key: scalar * value for key, value in polynomial.items() if scalar * value}


def multiply(left, right):
    answer = {}
    for left_key, left_value in left.items():
        for right_key, right_value in right.items():
            key = tuple(a + b for a, b in zip(left_key, right_key, strict=True))
            answer[key] = answer.get(key, 0) + left_value * right_value
    return {key: value for key, value in answer.items() if value}


def polynomial_determinant(matrix):
    if not matrix:
        return {ZERO: 1}
    if len(matrix) == 1:
        return matrix[0][0]
    answer = {}
    for column, entry in enumerate(matrix[0]):
        minor = [row[:column] + row[column + 1 :] for row in matrix[1:]]
        term = multiply(entry, polynomial_determinant(minor))
        answer = add(answer, scale(term, -1 if column & 1 else 1))
    return answer


def evaluate(polynomial, point):
    return sum(
        Fraction(coefficient)
        * product_value([point[index] ** degree for index, degree in enumerate(monomial)])
        for monomial, coefficient in polynomial.items()
    )


def product_value(values):
    answer = Fraction(1)
    for value in values:
        answer *= value
    return answer


def fraction_record(value):
    value = Fraction(value)
    return [value.numerator, value.denominator]


def polynomial_record(basis, polynomial):
    return {
        "basis": basis,
        "terms": [
            [list(monomial), coefficient]
            for monomial, coefficient in sorted(polynomial.items())
        ],
    }


def canonical_digest(payload):
    semantic = {key: value for key, value in payload.items() if key != "semantic_sha256"}
    encoded = json.dumps(semantic, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def main():
    source_sha256 = hashlib.sha256(SOURCE.read_bytes()).hexdigest()
    certificate = np.load(SOURCE, allow_pickle=False)
    matrix = certificate["pattern_chart"][0]

    polynomial_matrix = [
        [{ZERO: int(matrix[row, column])} for column in range(8)]
        for row in range(4)
    ]
    movements = (
        (4, 1, (1, 0, 0, 0)),
        (4, 7, (0, 1, 0, 0)),
        (0, 2, (0, 0, 1, 0)),
        (6, 1, (0, 0, 0, 1)),
    )
    for target, source, monomial in movements:
        for row in range(4):
            polynomial_matrix[row][target] = add(
                polynomial_matrix[row][target],
                {monomial: int(matrix[row, source])},
            )

    support_indices = (0, 2, 31, 42, 48)
    for support_index in support_indices:
        triple = tuple(label - 1 for label in TRIPLES[support_index])
        for omitted_row in range(4):
            retained_rows = [row for row in range(4) if row != omitted_row]
            polynomial = polynomial_determinant(
                [
                    [polynomial_matrix[row][column] for column in triple]
                    for row in retained_rows
                ]
            )
            expected = determinant(
                [[matrix[row, column] for column in triple] for row in retained_rows]
            )
            if polynomial != {ZERO: expected}:
                raise AssertionError("support normal moved")

    polynomials = []
    polynomial_map = {}
    for basis_zero in combinations(range(8), 4):
        basis = "".join(str(index + 1) for index in basis_zero)
        polynomial = polynomial_determinant(
            [
                [polynomial_matrix[row][column] for column in basis_zero]
                for row in range(4)
            ]
        )
        polynomial = scale(polynomial, 1 if polynomial[ZERO] > 0 else -1)
        if any(any(degree > 1 for degree in monomial) for monomial in polynomial):
            raise AssertionError("bracket is not multi-affine")
        polynomial_map[basis] = polynomial
        polynomials.append(polynomial_record(basis, polynomial))

    predecessor_fingerprint = hashlib.sha256(
        json.dumps(
            [
                {
                    "basis": item["basis"],
                    "terms": [
                        ["".join(str(degree) for degree in monomial), coefficient]
                        for monomial, coefficient in [
                            (tuple(term[0]), term[1]) for term in item["terms"]
                        ]
                    ],
                }
                for item in polynomials
            ],
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest()

    radius = Fraction(1, 84)
    minimum = None
    for basis, polynomial in polynomial_map.items():
        for signs in product((-1, 1), repeat=4):
            value = evaluate(polynomial, tuple(Fraction(sign, 84) for sign in signs))
            record = (value, basis, signs)
            if minimum is None or record < minimum:
                minimum = record
    if minimum is None or minimum[0] <= 0:
        raise AssertionError("declared local cube is not parent-safe")

    predecessor_failures = []
    for denominator in range(2, 84):
        local_minimum = None
        for basis, polynomial in polynomial_map.items():
            for signs in product((-1, 1), repeat=4):
                value = evaluate(
                    polynomial,
                    tuple(Fraction(sign, denominator) for sign in signs),
                )
                record = (value, basis, signs)
                if local_minimum is None or record < local_minimum:
                    local_minimum = record
        if local_minimum is None or local_minimum[0] >= 0:
            raise AssertionError("a larger reciprocal cube unexpectedly passed")
        predecessor_failures.append(
            {
                "denominator": denominator,
                "minimum": fraction_record(local_minimum[0]),
                "basis": local_minimum[1],
                "corner": list(local_minimum[2]),
            }
        )

    s_upper = Fraction(172497, 203756)
    t_upper = (Fraction(355617) + Fraction(651761) * s_upper) / Fraction(83738)
    bounding_box = {
        "s": [fraction_record(Fraction(-245451, 336697)), fraction_record(s_upper)],
        "t": [fraction_record(Fraction(-485532, 203756)), fraction_record(t_upper)],
        "u": [fraction_record(Fraction(-342093, 37757)), fraction_record(Fraction(145151, 241453))],
        "v": [fraction_record(Fraction(-284598, 369836)), fraction_record(Fraction(333089, 651761))],
    }

    payload = {
        "schema": "diag4-s53-row2599-candidate-null-v1",
        "canonical_base_revision": "aa784af939b55d3503e4782a9d65a9b06cf81ce0",
        "opening_revision": "eb88516411d54403f7b274624bd2c44918678cab",
        "source": {
            "path": "ai/omreal/data/seeat_parent2599_shatter8.npz",
            "sha256": source_sha256,
            "parent_row": 2599,
            "pattern": 0,
        },
        "tuple": {
            "signature_indices": [0, 4, 5, 6],
            "rho_index": 0,
            "rho_signature": int(certificate["signature"][0]),
            "support": "123/134/267/258/468",
            "support_indices": list(support_indices),
            "motion": "y5+=s*y2+t*y8; y1+=u*y3; y7+=v*y2",
        },
        "domain": {
            "definition": "D={(s,t,u,v) in R^4: p_I(s,t,u,v)>0 for every listed parent basis I}",
            "inequality_count": len(polynomials),
            "nonconstant_count": sum(len(polynomial_map[item["basis"]]) > 1 for item in polynomials),
            "nonlinear_count": sum(
                any(sum(monomial) >= 2 for monomial in polynomial_map[item["basis"]])
                for item in polynomials
            ),
            "all_multi_affine": True,
            "predecessor_polynomial_sha256": predecessor_fingerprint,
            "signed_polynomials": polynomials,
        },
        "bounded_compactification_gate": {
            "status": "REACHED_EXACT_OUTER_ENCLOSURE_ONLY",
            "open_rational_bounding_box": bounding_box,
            "proof_brackets": {
                "s_lower": "3458",
                "s_upper": "1358",
                "t_lower": "1235",
                "t_upper": "3456 combined with s_upper",
                "u_lower": "1268",
                "u_upper": "1278",
                "v_lower": "1367",
                "v_upper": "3467",
            },
            "boundary": "the actual parent boundary is the union of p_I=0 inside the box, not the box boundary",
        },
        "certified_local_cube": {
            "domain": "U=(-1/84,1/84)^4",
            "radius": fraction_record(radius),
            "corner_count": 16,
            "minimum_corner_value": fraction_record(minimum[0]),
            "minimum_basis": minimum[1],
            "minimum_corner": list(minimum[2]),
            "larger_reciprocal_denominators_checked": [2, 83],
            "larger_reciprocal_cube_failure_count": len(predecessor_failures),
            "nearest_failure": predecessor_failures[-1],
            "topology": "open 4-cube; relative CW pair ([−1/84,1/84]^4,boundary)",
            "relative_cell_counts_degrees_0_to_4": [0, 0, 0, 0, 1],
            "hc_ranks_degrees_0_to_4": [0, 0, 0, 0, 1],
        },
        "global_gates": {
            "whole_domain_cell_decomposition": "UNREACHED",
            "whole_domain_hc3": "UNREACHED",
            "full_closed_piece_inclusion_map": "UNREACHED",
            "counterexample": "NOT_CLAIMED",
        },
        "cubical_route_stop": {
            "reason": "A finite union of vertex-positive closed cubes is a compact subset of the open domain D. It cannot cover D, which contains the origin and has sequences tending to a parent-wall zero. A wall-adapted exact decomposition, not further finite inner boxes, is required.",
            "transfer_reason": "Cohomology of a subset does not inject into the full piece without a checked inclusion map; the verifier includes an annulus-to-disk hostile canary.",
        },
    }
    payload["semantic_sha256"] = canonical_digest(payload)
    OUTPUT.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {OUTPUT}")
    print(f"semantic_sha256 {payload['semantic_sha256']}")
    print(f"local cube minimum {minimum[0]} at {minimum[1]} {minimum[2]}")


if __name__ == "__main__":
    main()
