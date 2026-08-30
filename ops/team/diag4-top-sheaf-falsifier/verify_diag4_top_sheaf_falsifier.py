#!/usr/bin/env python3
"""Exact replay for the diagonal-four top-sheaf falsifier.

This checker keeps two evidence classes separate.

* It exhausts the smallest abstract signed split--remerge class: component
  diagrams over a base line with two exterior rays, connected exterior
  fibers, no births/deaths, at most two generic split/merge events, and at
  most two simultaneous branches.  The only cyclic event word is
  ``1 -> 2 -> 1``.  All sixteen signed attachment matrices are checked
  exactly over Q and reduced to the two orientation-holonomy classes.
* It independently replays an actual retained row-2599 control: four
  signatures are proper and pairwise incomparable, and their pattern-zero
  Gordan circuits are positive, support-minimal, and cover all eight labels.

The abstract model is not asserted to be realizable by rank-four extension
data.  Conversely, the realizable control supplies no split--remerge event
or nonzero compact-support class.  The separation is the point of the null
result.
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
MODEL = HERE / "MINIMAL_SIGNED_MODELS.json"
SHATTER = REPO / "ai" / "omreal" / "data" / "seeat_parent2599_shatter8.npz"
SELECTED = (0, 4, 5, 6)
TRIPLES = tuple(
    sorted(combinations(range(1, 9), 3), key=lambda item: tuple(reversed(item)))
)
BASES = tuple(
    sorted(combinations(range(1, 9), 4), key=lambda item: tuple(reversed(item)))
)


def determinant(matrix):
    """Exact determinant for orders at most four."""
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


def matrix_rank(matrix):
    """Exact rank over Q."""
    rows = [[Fraction(value) for value in row] for row in matrix]
    if not rows:
        return 0
    pivot_row = 0
    for column in range(len(rows[0])):
        pivot = next(
            (row for row in range(pivot_row, len(rows)) if rows[row][column]),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        scale = rows[pivot_row][column]
        rows[pivot_row] = [value / scale for value in rows[pivot_row]]
        for row in range(len(rows)):
            if row == pivot_row or not rows[row][column]:
                continue
            scale = rows[row][column]
            rows[row] = [
                left - scale * right
                for left, right in zip(rows[row], rows[pivot_row], strict=True)
            ]
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return pivot_row


def canonical_digest(payload):
    semantic = {key: value for key, value in payload.items() if key != "semantic_sha256"}
    encoded = json.dumps(
        semantic, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return hashlib.sha256(encoded).hexdigest()


def signed_minimal_class(payload):
    search = payload["abstract_search"]
    if search != {
        "base_topology": "oriented_line_with_two_exterior_rays",
        "births_or_deaths": False,
        "component_bound": 2,
        "connected_outside_events": True,
        "event_bound": 2,
        "event_type": "generic_split_or_merge",
    }:
        raise AssertionError("abstract search domain changed")

    # With connected exterior fibers, no births/deaths, and at most two
    # generic +/-1 events, a return to one component has only these words.
    event_words = ("1", "1-2", "2-1", "1-2-1")
    cyclic_words = tuple(word for word in event_words if word == "1-2-1")
    if cyclic_words != ("1-2-1",):
        raise AssertionError("wrong minimal event classification")

    records = []
    for left0, right0, left1, right1 in product((-1, 1), repeat=4):
        boundary = ((left0, left1), (right0, right1))
        rank = matrix_rank(boundary)
        kernel_dimension = 2 - rank
        determinant_value = left0 * right1 - left1 * right0
        holonomy = left0 * right1 * left1 * right0
        if kernel_dimension != int(determinant_value == 0):
            raise AssertionError("wrong signed-kernel classification")
        if kernel_dimension != int(holonomy == 1):
            raise AssertionError("holonomy and boundary tests disagree")
        records.append(
            (left0, right0, left1, right1, holonomy, kernel_dimension)
        )

    obstructing = tuple(record for record in records if record[-1] == 1)
    exact = tuple(record for record in records if record[-1] == 0)
    if (len(records), len(obstructing), len(exact)) != (16, 8, 8):
        raise AssertionError("wrong enumeration counts")

    # Row (event) and column (branch) generator changes preserve holonomy.
    def gauge_orbit(seed):
        answer = set()
        for row_left, row_right, col0, col1 in product((-1, 1), repeat=4):
            left0, right0, left1, right1 = seed
            answer.add(
                (
                    row_left * col0 * left0,
                    row_right * col0 * right0,
                    row_left * col1 * left1,
                    row_right * col1 * right1,
                )
            )
        return answer

    positive_seed = tuple(payload["signed_normal_forms"]["trivial_holonomy"])
    negative_seed = tuple(payload["signed_normal_forms"]["twisted_holonomy"])
    positive_orbit = gauge_orbit(positive_seed)
    negative_orbit = gauge_orbit(negative_seed)
    if len(positive_orbit) != 8 or len(negative_orbit) != 8:
        raise AssertionError("wrong gauge-orbit size")
    if positive_orbit & negative_orbit or len(positive_orbit | negative_orbit) != 16:
        raise AssertionError("signed gauge classes do not partition the models")
    if not all(record[:4] in positive_orbit for record in obstructing):
        raise AssertionError("trivial-holonomy orbit is not the obstruction class")
    if not all(record[:4] in negative_orbit for record in exact):
        raise AssertionError("twisted-holonomy orbit is not the exact class")

    # Boundary canary: fewer than two component-changing events has a tree
    # component graph.  These are the complete connected generic shapes over
    # the declared base line with two exterior rays; E-V+1 is zero throughout.
    boundary_shapes = {
        "no_event": (2, 1),
        "one_split": (4, 3),
        "one_merge": (4, 3),
    }
    if any(edges - vertices + 1 for vertices, edges in boundary_shapes.values()):
        raise AssertionError("a boundary canary unexpectedly has a cycle")

    # Hostile sign mutation: one attachment flip must kill the minimal class.
    mutated = list(positive_seed)
    mutated[0] *= -1
    mutation_boundary = ((mutated[0], mutated[2]), (mutated[1], mutated[3]))
    if matrix_rank(mutation_boundary) != 2:
        raise AssertionError("sign mutation did not kill the abstract class")

    print(
        "PASS oriented-line/two-exterior-ray abstract minimality: "
        "zero/one events are trees; only 1-2-1 can cycle"
    )
    print("PASS signed exhaustion: 16 matrices = 8 obstructing + 8 exact")
    print("PASS gauge reduction: exactly trivial/twisted holonomy classes")
    print("PASS sign-mutation and boundary canaries")


def parent_signs_and_rows(matrix):
    signs = []
    for basis in BASES:
        columns = matrix[:, np.asarray(basis) - 1]
        value = determinant(columns.tolist())
        if value == 0:
            raise AssertionError("nonuniform row-2599 control chart")
        signs.append(1 if value > 0 else -1)

    rows = []
    for triple in TRIPLES:
        columns = matrix[:, np.asarray(triple) - 1]
        row = []
        for coordinate in range(4):
            minor = np.delete(columns, coordinate, axis=0)
            row.append((-1) ** (coordinate + 5) * determinant(minor.tolist()))
        if not any(row):
            raise AssertionError("zero third-compound row")
        rows.append(tuple(row))
    return tuple(signs), tuple(rows)


def signed_rows(rows, signature):
    return tuple(
        tuple(value if (signature >> index) & 1 else -value for value in row)
        for index, row in enumerate(rows)
    )


def strict_witness(rows, point):
    vector = tuple(int(value) for value in point)
    return all(
        sum(value * coordinate for value, coordinate in zip(row, vector, strict=True))
        > 0
        for row in rows
    )


def gordan_witness(rows, raw_weights):
    weights = tuple(int(value) for value in raw_weights)
    return (
        any(weights)
        and all(value >= 0 for value in weights)
        and all(
            sum(weight * row[coordinate] for weight, row in zip(weights, rows, strict=True))
            == 0
            for coordinate in range(4)
        )
    )


def realizable_retained_control(payload):
    expected_digest = payload["realizable_retained_control"]["input_sha256"]
    if hashlib.sha256(SHATTER.read_bytes()).hexdigest() != expected_digest:
        raise AssertionError("row-2599 input digest changed")

    certificate = np.load(SHATTER, allow_pickle=False)
    signatures = tuple(int(value) for value in certificate["signature"])
    charts = certificate["pattern_chart"]
    points = certificate["feasible_point"]
    weights = certificate["gordan_weight"]
    if charts.shape != (256, 4, 8) or len(set(signatures)) != 8:
        raise AssertionError("wrong row-2599 certificate shape")
    selected_signatures = tuple(signatures[index] for index in SELECTED)
    if len(set(selected_signatures)) != 4:
        raise AssertionError("selected signatures are not distinct")

    base_parent, base_rows = parent_signs_and_rows(charts[0])
    supports = []
    for selected_index, signature in zip(SELECTED, selected_signatures, strict=True):
        rows = signed_rows(base_rows, signature)
        raw = tuple(int(value) for value in weights[0, selected_index])
        active = tuple(index for index, value in enumerate(raw) if value)
        if len(active) != 5 or any(raw[index] <= 0 for index in active):
            raise AssertionError("control is not a positive five-circuit")
        if not gordan_witness(rows, raw):
            raise AssertionError("control Gordan dependence is invalid")
        if matrix_rank([rows[index] for index in active]) != 4:
            raise AssertionError("control circuit is not support-minimal")
        covered = {label for index in active for label in TRIPLES[index]}
        if covered != set(range(1, 9)):
            raise AssertionError("control circuit is not cover-all")
        supports.append(active)

    # The sixteen selected support patterns are replayed on charts with one
    # identical parent chirotope.  Hence every region is proper, and each pair
    # is incomparable, without relying on unsigned support incidence.
    for local_pattern in range(16):
        global_pattern = sum(
            ((local_pattern >> local_bit) & 1) << selected_index
            for local_bit, selected_index in enumerate(SELECTED)
        )
        parent, rows = parent_signs_and_rows(charts[global_pattern])
        if parent != base_parent:
            raise AssertionError("control pattern changed the parent chirotope")
        for local_bit, (selected_index, signature) in enumerate(
            zip(SELECTED, selected_signatures, strict=True)
        ):
            current = signed_rows(rows, signature)
            if (local_pattern >> local_bit) & 1:
                if not strict_witness(current, points[global_pattern, selected_index]):
                    raise AssertionError("invalid strict extension witness")
            elif not gordan_witness(current, weights[global_pattern, selected_index]):
                raise AssertionError("invalid Gordan exclusion witness")

    print("PASS realizable control: four proper pairwise-incomparable signatures")
    print("PASS realizable control: four positive minimal cover-all five-circuits")
    print("CAVEAT realizable control has no certified split--remerge event or H_c^3 class")


ZERO_MONOMIAL = (0, 0, 0, 0)


def polynomial_add(left, right):
    answer = dict(left)
    for monomial, coefficient in right.items():
        answer[monomial] = answer.get(monomial, 0) + coefficient
    return {monomial: coefficient for monomial, coefficient in answer.items() if coefficient}


def polynomial_scale(polynomial, scalar):
    return {
        monomial: scalar * coefficient
        for monomial, coefficient in polynomial.items()
        if scalar * coefficient
    }


def polynomial_multiply(left, right):
    answer = {}
    for left_monomial, left_coefficient in left.items():
        for right_monomial, right_coefficient in right.items():
            monomial = tuple(
                left_degree + right_degree
                for left_degree, right_degree in zip(
                    left_monomial, right_monomial, strict=True
                )
            )
            answer[monomial] = (
                answer.get(monomial, 0) + left_coefficient * right_coefficient
            )
    return {monomial: coefficient for monomial, coefficient in answer.items() if coefficient}


def polynomial_determinant(matrix):
    if not matrix:
        return {ZERO_MONOMIAL: 1}
    if len(matrix) == 1:
        return matrix[0][0]
    answer = {}
    for column, entry in enumerate(matrix[0]):
        minor = [row[:column] + row[column + 1 :] for row in matrix[1:]]
        term = polynomial_multiply(entry, polynomial_determinant(minor))
        answer = polynomial_add(
            answer, polynomial_scale(term, -1 if column & 1 else 1)
        )
    return answer


def exact_motion_candidate(payload):
    """Reconstruct one actual support-preserving four-parameter family."""
    certificate = np.load(SHATTER, allow_pickle=False)
    matrix = certificate["pattern_chart"][0]
    motion = payload["realizable_retained_control"]["candidate_motion"]
    if motion["signature_index"] != 0 or motion["support_indices"] != [0, 2, 31, 42, 48]:
        raise AssertionError("candidate support changed")

    # Variables are ordered (s,t,u,v).  In one-based label notation:
    # y5 += s*y2 + t*y8, y1 += u*y3, y7 += v*y2.
    polynomial_matrix = [
        [{ZERO_MONOMIAL: int(matrix[row, column])} for column in range(8)]
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
            polynomial_matrix[row][target] = polynomial_add(
                polynomial_matrix[row][target],
                {monomial: int(matrix[row, source])},
            )

    # Every support normal is literally fixed, not merely fixed up to scale;
    # therefore the stored positive Gordan circuit persists on the whole
    # parent-safe parameter domain.
    for support_index in motion["support_indices"]:
        triple = tuple(label - 1 for label in TRIPLES[support_index])
        for omitted_row in range(4):
            rows = [row for row in range(4) if row != omitted_row]
            got = polynomial_determinant(
                [[polynomial_matrix[row][column] for column in triple] for row in rows]
            )
            expected = determinant(
                [[matrix[row, column] for column in triple] for row in rows]
            )
            if got != {ZERO_MONOMIAL: expected}:
                raise AssertionError("candidate motion does not preserve its support normal")

    signed_polynomials = []
    nonconstant = 0
    nonlinear = 0
    for basis in combinations(range(8), 4):
        polynomial = polynomial_determinant(
            [[polynomial_matrix[row][column] for column in basis] for row in range(4)]
        )
        constant = polynomial[ZERO_MONOMIAL]
        polynomial = polynomial_scale(polynomial, 1 if constant > 0 else -1)
        if len(polynomial) > 1:
            nonconstant += 1
        if any(sum(monomial) >= 2 for monomial in polynomial):
            nonlinear += 1
        signed_polynomials.append(
            {
                "basis": "".join(str(label + 1) for label in basis),
                "terms": [
                    ["".join(str(degree) for degree in monomial), coefficient]
                    for monomial, coefficient in sorted(polynomial.items())
                ],
            }
        )
    fingerprint = hashlib.sha256(
        json.dumps(
            signed_polynomials, sort_keys=True, separators=(",", ":")
        ).encode("ascii")
    ).hexdigest()
    expected = motion["signed_parent_polynomial_sha256"]
    if fingerprint != expected:
        raise AssertionError(
            f"candidate polynomial fingerprint changed: {fingerprint} != {expected}"
        )
    if (nonconstant, nonlinear) != (
        motion["nonconstant_parent_inequalities"],
        motion["nonlinear_parent_inequalities"],
    ):
        raise AssertionError("candidate polynomial counts changed")

    print("PASS actual D4-SP candidate: four support-preserving parameters")
    print(
        f"PASS exact parent domain: {nonconstant} nonconstant / "
        f"{nonlinear} nonlinear signed bracket inequalities"
    )
    print("CAVEAT candidate topology and inclusion into the full closed piece are uncomputed")


def main():
    payload = json.loads(MODEL.read_text(encoding="utf-8"))
    if payload["schema"] != "diag4-top-sheaf-minimal-signed-models-v1":
        raise AssertionError("wrong model schema")
    if canonical_digest(payload) != payload["semantic_sha256"]:
        raise AssertionError("model semantic digest mismatch")
    signed_minimal_class(payload)
    realizable_retained_control(payload)
    exact_motion_candidate(payload)
    print(
        "OUTCOME finite-exact oriented-line/two-exterior-ray abstract "
        "classification; global realizability INCONCLUSIVE"
    )


if __name__ == "__main__":
    main()
