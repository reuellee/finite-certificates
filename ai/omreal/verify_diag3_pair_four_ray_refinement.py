#!/usr/bin/env python3
"""Exact four-ray refinement of the row-2599 pair receiver/end canary.

This is deliberately a one-dimensional restriction.  It attaches the four
primitive factor intervals through the exact row-2599 node, stops each at
its first parent-bracket wall, and treats those four endpoints as the
relative-infinity subcomplex.  Every localized primitive residual factor is
restricted to both node branches.  Exact Sturm boxes, polynomial gcds, and
signed occurrence circuits give a complete subdivision and status table for
the three signings in DIAG3_PAIR_RECEIVER_END_CANARY.md.

The resulting compactified factor star is an honest finite CW pair, but it
is not an ambient two-dimensional neighborhood and has no claim to compute
the nine-dimensional compact-support degrees.  Its explicit (22)--(23)
matrix has a primitive rank-three residue; this is the executable canary's
answer, not a counterexample to the global diagonal-three statement.
"""

from __future__ import annotations

from collections import Counter, defaultdict, deque
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from math import gcd, lcm
from pathlib import Path
import sys

import numpy as np
from scipy.optimize import linprog


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import BLOCK_GORDAN_RESIDUAL_MUTATION_MAP_NO_GO as mutation  # noqa: E402
import DIAG9_GRAPH_exact_topes as topes  # noqa: E402
import DIAG9_GRAPH_verify_node_factor_link as node_link  # noqa: E402
import DIAG9_GRAPH_verify_row2599_node as node  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402
import build_ninth_candidate_antichain as circuit_finder  # noqa: E402
import prototype_koszul_circuits as koszul  # noqa: E402
import verify_diag3_pair_receiver_end_canary as receiver  # noqa: E402
from DIAG9_GRAPH_verify_row2599_line import polynomial_gcd  # noqa: E402


GLOBAL = HERE / "data" / "DIAG9_GRAPH_global_factor_census.npz"
RAYS = (
    (0, "negative", "q0=0,q1>0"),
    (0, "positive", "q0=0,q1<0"),
    (1, "negative", "q1=0,q0<0"),
    (1, "positive", "q1=0,q0>0"),
)

EXPECTED_ROOT_DATA = {
    (0, "negative"): (2_641, 2_613, {1: 2_590, 2: 18, 3: 5}),
    (0, "positive"): (129, 128, {1: 127, 2: 1}),
    (1, "negative"): (1_773, 1_756, {1: 1_741, 2: 13, 3: 2}),
    (1, "positive"): (49, 49, {1: 49}),
}
EXPECTED_STATUS_COUNTS = {
    (0, "negative"): {(True, False, True): 2_614},
    (0, "positive"): {(True, True, True): 129},
    (1, "negative"): {
        (True, True, True): 241,
        (True, True, False): 1_516,
    },
    (1, "positive"): {(False, True, True): 50},
}
EXPECTED_WALL_OCCURRENCES = {
    (0, "negative"): 7_811,
    (0, "positive"): 0,
    (1, "negative"): 4_591,
    (1, "positive"): 49,
}
EXPECTED_TRANSITION = ((1, "negative", 240, 2, (13_063,)),)
EXPECTED_FACTOR_13063_OCCURRENCE = (19, 21, 37, 38)
EXPECTED_FACTOR_13063_RELATION = (-1, -1, 1, -1)
EXPECTED_ENDPOINT_STATUS = {
    (0, "negative"): (True, False, True),
    (0, "positive"): (True, True, True),
    (1, "negative"): (True, True, False),
    (1, "positive"): (False, True, True),
}
EXPECTED_NODE_STATUS = (True, True, True)
EXPECTED_COMPLEX_DIMS = {
    "T": (370, 370),
    "E01": (1_515, 1_516),
    "E02": (2_613, 2_614),
    "E12": (49, 50),
    "C": (4_917, 4_920, 0),
}
EXPECTED_MASS_COUNTS = {
    "relative_base_size2": 8_357,
    "relative_base_size3": 740,
    "relative_mass_faces": 30_251,
    "infinity_mass_faces": 16,
}
EXPECTED_SEMANTIC = "e8ee42d741c80497e1d9f89d7973e702765de405ae2b78420a2439a408bf0bf4"


def trim(polynomial):
    answer = list(polynomial)
    while answer and not answer[-1]:
        answer.pop()
    return tuple(answer)


def add(left, right, scale=1):
    answer = [0] * max(len(left), len(right))
    for index, value in enumerate(left):
        answer[index] += value
    for index, value in enumerate(right):
        answer[index] += scale * value
    return trim(answer)


def multiply(left, right):
    if not left or not right:
        return ()
    answer = [0] * (len(left) + len(right) - 1)
    for first, left_value in enumerate(left):
        for second, right_value in enumerate(right):
            answer[first + second] += left_value * right_value
    return trim(answer)


def determinant(matrix):
    if len(matrix) == 1:
        return tuple(matrix[0][0])
    answer = ()
    for column, value in enumerate(matrix[0]):
        minor = [row[:column] + row[column + 1 :] for row in matrix[1:]]
        answer = add(
            answer,
            multiply(value, determinant(minor)),
            -1 if column & 1 else 1,
        )
    return answer


def primitive_polynomial(polynomial):
    polynomial = trim(tuple(map(Fraction, polynomial)))
    if not polynomial:
        return ()
    denominator = 1
    for value in polynomial:
        denominator = lcm(denominator, value.denominator)
    integers = [int(value * denominator) for value in polynomial]
    divisor = 0
    for value in integers:
        divisor = gcd(divisor, abs(value))
    integers = [value // divisor for value in integers]
    if integers[-1] < 0:
        integers = [-value for value in integers]
    return tuple(integers)


def divide_linear(polynomial, root):
    polynomial = tuple(map(Fraction, polynomial))
    quotient = [Fraction(0)] * max(0, len(polynomial) - 1)
    remainder = list(polynomial)
    for degree in range(len(polynomial) - 1, 0, -1):
        coefficient = remainder[degree]
        quotient[degree - 1] = coefficient
        remainder[degree] -= coefficient
        remainder[degree - 1] += coefficient * root
    if any(remainder):
        return None
    return primitive_polynomial(quotient)


def remove_root(polynomial, root):
    multiplicity = 0
    while polynomial and sturm.polynomial_value(polynomial, root) == 0:
        quotient = divide_linear(polynomial, root)
        if quotient is None:
            raise AssertionError("exact linear division failed")
        polynomial = quotient
        multiplicity += 1
    return polynomial, multiplicity


def polynomial_parent(branch):
    base = node.slice_verify.source_parent()
    scale = lcm(node.CENTER_S.denominator, node.CENTER_U.denominator)
    matrix = [
        [(scale * int(base[row, column]),) for column in range(8)]
        for row in range(4)
    ]
    first = node.disk.FIRST_POSITION
    second = node.disk.SECOND_POSITION
    coefficient_s = int(node.CENTERED_BRANCHES[branch][(1, 0)])
    coefficient_u = int(node.CENTERED_BRANCHES[branch][(0, 1)])
    matrix[first[0]][first[1]] = (
        matrix[first[0]][first[1]][0] + int(node.CENTER_S * scale),
        scale * coefficient_u,
    )
    matrix[second[0]][second[1]] = (
        matrix[second[0]][second[1]][0] + int(node.CENTER_U * scale),
        -scale * coefficient_s,
    )
    return matrix


def normal_polynomials(branch):
    matrix = polynomial_parent(branch)
    normals = []
    for triple in topes.TRIPLES:
        normal = []
        for omitted in range(4):
            rows = [row for row in range(4) if row != omitted]
            minor = [[matrix[row][column] for column in triple] for row in rows]
            value = determinant(minor)
            if (omitted + 3) & 1:
                value = tuple(-entry for entry in value)
            normal.append(value)
        normals.append(tuple(normal))
    return tuple(normals)


def occurrence_polynomial(normals, fourset):
    return primitive_polynomial(
        determinant([list(normals[index]) for index in fourset])
    )


def factor_data():
    with np.load(GLOBAL, allow_pickle=False) as source:
        if str(source["format"].item()) != "diag9-global-residual-factor-census-v1":
            raise AssertionError("wrong global factor-census format")
        foursets = tuple(
            tuple(map(int, row)) for row in source["occurrence_fourset"]
        )
        factors = tuple(map(int, source["occurrence_factor"]))
        offsets = tuple(map(int, source["occurrence_unit_offset"]))
        units = tuple(map(int, source["occurrence_unit_index"]))
        labels = tuple(
            "".join(str(int(value) + 1) for value in row)
            for row in source["parent_bracket_label"]
        )
    groups = [[] for _ in range(26_740)]
    for occurrence, factor in enumerate(factors):
        groups[factor].append(occurrence)
    if len(foursets) != 84_840 or any(not group for group in groups):
        raise AssertionError("wrong occurrence/factor census")
    return foursets, tuple(map(tuple, groups)), offsets, units, labels


def representatives(groups, offsets, units, avoided_unit):
    answer = []
    for group in groups:
        chosen = next(
            (
                occurrence
                for occurrence in group
                if avoided_unit
                not in units[offsets[occurrence] : offsets[occurrence + 1]]
            ),
            None,
        )
        if chosen is None:
            raise AssertionError("a factor has an unavoidable endpoint unit")
        answer.append(chosen)
    return tuple(answer)


def split_nonroot(polynomial, left, right):
    for denominator in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31):
        for numerator in range(1, denominator):
            candidate = (
                left * (denominator - numerator) + right * numerator
            ) / denominator
            if sturm.polynomial_value(polynomial, candidate):
                return candidate
    raise AssertionError("could not find a rational nonroot split")


def isolate_roots(polynomial, left=Fraction(0), right=Fraction(1)):
    total = sturm.root_count(polynomial, left, right)
    queue = deque(((left, right, total),))
    answer = []
    target_width = Fraction(1, 1 << 96)
    while queue:
        lower, upper, count = queue.popleft()
        if not count:
            continue
        if count == 1 and upper - lower <= target_width:
            answer.append((lower, upper))
            continue
        middle = split_nonroot(polynomial, lower, upper)
        first = sturm.root_count(polynomial, lower, middle)
        second = sturm.root_count(polynomial, middle, upper)
        if first + second != count:
            raise AssertionError("Sturm subdivision lost a root")
        queue.append((lower, middle, first))
        queue.append((middle, upper, second))
    return tuple(sorted(answer))


def scaled_polynomial(polynomial, endpoint):
    return primitive_polynomial(
        Fraction(coefficient) * endpoint**degree
        for degree, coefficient in enumerate(polynomial)
    )


def common_root(left, right):
    lower = max(left["lower"], right["lower"])
    upper = min(left["upper"], right["upper"])
    if lower >= upper:
        return False
    divisor = polynomial_gcd(left["polynomial"], right["polynomial"])
    return len(divisor) > 1 and sturm.root_count(divisor, lower, upper) == 1


def refine_record(record):
    lower, upper = record["lower"], record["upper"]
    middle = split_nonroot(record["polynomial"], lower, upper)
    if sturm.root_count(record["polynomial"], lower, middle):
        record["upper"] = middle
    elif sturm.root_count(record["polynomial"], middle, upper):
        record["lower"] = middle
    else:
        raise AssertionError("root refinement lost its root")


def separate_distinct_roots(records):
    rounds = 0
    while True:
        records.sort(
            key=lambda record: (
                (record["lower"] + record["upper"]) / 2,
                record["lower"],
            )
        )
        conflict = None
        active = []
        for index, record in enumerate(records):
            active = [
                previous
                for previous in active
                if records[previous]["upper"] > record["lower"]
            ]
            for previous in active:
                if not common_root(record, records[previous]):
                    conflict = (record, records[previous])
                    break
            if conflict is not None:
                break
            active.append(index)
        if conflict is None:
            return rounds
        refine_record(conflict[0])
        refine_record(conflict[1])
        rounds += 1
        if rounds > 100_000:
            raise AssertionError("distinct algebraic roots did not separate")


class DisjointSet:
    def __init__(self, size):
        self.parent = list(range(size))

    def find(self, item):
        while self.parent[item] != item:
            self.parent[item] = self.parent[self.parent[item]]
            item = self.parent[item]
        return item

    def union(self, left, right):
        left, right = self.find(left), self.find(right)
        if left != right:
            self.parent[right] = left


def group_roots(records):
    by_polynomial = defaultdict(list)
    incidence_count = 0
    repeated = []
    for factor, polynomial, count in records:
        if not count:
            continue
        derivative = tuple(
            degree * polynomial[degree] for degree in range(1, len(polynomial))
        )
        divisor = polynomial_gcd(polynomial, derivative)
        if len(divisor) > 1 and sturm.root_count(divisor, 0, 1):
            repeated.append(factor)
        by_polynomial[polynomial].append(factor)
        incidence_count += count
    if repeated:
        raise AssertionError(f"multiple factor roots remain: {repeated[:20]}")

    roots = []
    for polynomial, factors in by_polynomial.items():
        for lower, upper in isolate_roots(polynomial):
            roots.append(
                {
                    "polynomial": polynomial,
                    "lower": lower,
                    "upper": upper,
                    "factors": tuple(factors),
                }
            )
    separation_rounds = separate_distinct_roots(roots)
    roots.sort(key=lambda record: (record["lower"] + record["upper"]) / 2)
    disjoint = DisjointSet(len(roots))
    active = []
    for index, record in enumerate(roots):
        active = [
            previous
            for previous in active
            if roots[previous]["upper"] > record["lower"]
        ]
        for previous in active:
            if common_root(record, roots[previous]):
                disjoint.union(index, previous)
        active.append(index)

    classes = defaultdict(list)
    for index, record in enumerate(roots):
        classes[disjoint.find(index)].append(record)
    answer = []
    for rows in classes.values():
        lower = max(row["lower"] for row in rows)
        upper = min(row["upper"] for row in rows)
        if lower >= upper:
            raise AssertionError("coincident root boxes have empty intersection")
        divisor = rows[0]["polynomial"]
        for row in rows[1:]:
            divisor = polynomial_gcd(divisor, row["polynomial"])
        if len(divisor) <= 1 or sturm.root_count(divisor, lower, upper) != 1:
            raise AssertionError("coincident factors lack a common algebraic root")
        factors = tuple(
            sorted(factor for row in rows for factor in row["factors"])
        )
        if len(factors) != len(set(factors)):
            raise AssertionError("one factor occurs twice at one grouped root")
        answer.append((lower, upper, factors, primitive_polynomial(divisor)))
    answer.sort(key=lambda row: (row[0] + row[1]) / 2)
    if any(left[1] >= right[0] for left, right in zip(answer, answer[1:])):
        raise AssertionError("grouped root boxes overlap")
    if sum(len(row[2]) for row in answer) != incidence_count:
        raise AssertionError("factor-root incidence count changed during grouping")
    return tuple(answer), incidence_count, separation_rounds


def ray_factor_atlases(foursets, groups, offsets, units, labels, ends):
    label_index = {label: index for index, label in enumerate(labels)}
    ray_specs = []
    occurrence_by_branch = defaultdict(set)
    for branch, side, name in RAYS:
        endpoint, _basis, label = ends[branch][side]
        selected = representatives(
            groups, offsets, units, label_index[label]
        )
        ray_specs.append((branch, side, name, endpoint, label, selected))
        occurrence_by_branch[branch].update(selected)

    restrictions = {}
    for branch in (0, 1):
        normals = normal_polynomials(branch)
        for occurrence in sorted(occurrence_by_branch[branch]):
            restrictions[(branch, occurrence)] = occurrence_polynomial(
                normals, foursets[occurrence]
            )

    answer = {}
    for branch, side, name, endpoint, label, selected in ray_specs:
        raw_records = []
        identical = []
        center = []
        outer = []
        for factor, occurrence in enumerate(selected):
            polynomial = restrictions[(branch, occurrence)]
            if not polynomial:
                identical.append(factor)
                continue
            polynomial, center_multiplicity = remove_root(polynomial, Fraction(0))
            polynomial, outer_multiplicity = remove_root(polynomial, endpoint)
            if center_multiplicity:
                center.append((factor, center_multiplicity))
            if outer_multiplicity:
                outer.append((factor, outer_multiplicity))
            scaled = scaled_polynomial(polynomial, endpoint)
            count = sturm.root_count(scaled, Fraction(0), Fraction(1))
            raw_records.append((factor, scaled, count))

        expected_own = node_link.EXPECTED_FACTOR_IDS[branch]
        expected_other = node_link.EXPECTED_FACTOR_IDS[1 - branch]
        if identical != [expected_own]:
            raise AssertionError(f"wrong branch-contained factors: {identical}")
        if center != [(expected_other, 1)]:
            raise AssertionError(f"wrong transverse center factors: {center}")
        if outer:
            raise AssertionError(f"a primitive factor hits parent infinity: {outer}")

        roots, incidences, separation_rounds = group_roots(raw_records)
        histogram = dict(Counter(len(row[2]) for row in roots))
        expected = EXPECTED_ROOT_DATA[(branch, side)]
        if (incidences, len(roots), histogram) != expected:
            raise AssertionError(
                f"wrong root census on {(branch, side)}: "
                f"{(incidences, len(roots), histogram)}"
            )
        if separation_rounds:
            raise AssertionError("the pinned 96-bit boxes unexpectedly overlap")
        answer[(branch, side)] = {
            "name": name,
            "endpoint": endpoint,
            "endpoint_label": label,
            "roots": roots,
            "incidences": incidences,
        }
    return answer


def primitive_vector(vector):
    vector = tuple(map(int, vector))
    divisor = 0
    for value in vector:
        divisor = gcd(divisor, abs(value))
    if not divisor:
        return vector
    return tuple(value // divisor for value in vector)


def signed_rows(normals, signature):
    return tuple(
        tuple(
            (1 if signature & (1 << index) else -1) * int(value)
            for value in normal
        )
        for index, normal in enumerate(normals)
    )


def normalized_rows(rows):
    answer = []
    for row in rows:
        scale = max(abs(value) for value in row)
        answer.append([float(Fraction(value, scale)) for value in row])
    return np.asarray(answer, dtype=float)


def exact_positive_circuit(rows, normalized):
    result = linprog(
        np.zeros(len(rows)),
        A_eq=np.vstack((normalized.T, np.ones(len(rows)))),
        b_eq=np.r_[np.zeros(4), 1.0],
        bounds=(0, None),
        method="highs-ds",
    )
    if not result.success:
        return None
    active = tuple(int(index) for index in np.where(result.x > 1e-9)[0])
    if len(active) > 8:
        active = tuple(
            int(index)
            for index in np.argsort(result.x)[-8:]
            if result.x[index] > 1e-12
        )
    for size in range(2, min(5, len(active)) + 1):
        for support in combinations(active, size):
            matrix = [[rows[index][coordinate] for index in support] for coordinate in range(4)]
            for vector in circuit_finder.nullspace(matrix):
                if not (
                    all(value > 0 for value in vector)
                    or all(value < 0 for value in vector)
                ):
                    continue
                if vector[0] < 0:
                    vector = [-value for value in vector]
                denominator = 1
                for value in vector:
                    denominator = lcm(denominator, value.denominator)
                weights = primitive_vector(
                    value.numerator * (denominator // value.denominator)
                    for value in vector
                )
                if all(value > 0 for value in weights) and all(
                    sum(
                        weights[position] * rows[index][coordinate]
                        for position, index in enumerate(support)
                    )
                    == 0
                    for coordinate in range(4)
                ):
                    return tuple(support), tuple(weights)
    return None


def classify(normals, signature):
    rows = signed_rows(normals, signature)
    normalized = normalized_rows(rows)
    result = linprog(
        np.zeros(4),
        A_ub=-normalized,
        b_ub=-np.ones(len(rows)),
        bounds=[(None, None)] * 4,
        method="highs-ds",
    )
    if result.success:
        for scale in (10**6, 10**9, 10**12, 10**15, 10**18):
            witness = primitive_vector(round(float(value) * scale) for value in result.x)
            if any(witness) and all(
                sum(row[index] * witness[index] for index in range(4)) > 0
                for row in rows
            ):
                return False, ("witness", witness)
        raise AssertionError("floating feasible point lacks an exact witness")
    circuit = exact_positive_circuit(rows, normalized)
    if circuit is None:
        raise AssertionError("infeasible LP lacks an exact Gordan circuit")
    return True, ("circuit", circuit)


def segment_samples(roots):
    if not roots:
        return (Fraction(1, 2),)
    return (
        (roots[0][0] / 2,)
        + tuple((left[1] + right[0]) / 2 for left, right in zip(roots, roots[1:]))
        + ((roots[-1][1] + 1) / 2,)
    )


def status_atlases(atlases):
    transitions = []
    for key, atlas in atlases.items():
        branch, side = key
        samples = segment_samples(atlas["roots"])
        statuses = []
        certificates = []
        for sample in samples:
            parent = receiver.integer_parent(
                receiver.branch_parent(branch, atlas["endpoint"] * sample)
            )
            normals = topes.derived_rows(parent, normalize=False)
            row = []
            row_certificates = []
            for signature in receiver.RECEIVER_SIGNATURES:
                bad, certificate = classify(normals, signature)
                row.append(bad)
                row_certificates.append(certificate)
            statuses.append(tuple(row))
            certificates.append(tuple(row_certificates))
        actual_counts = dict(Counter(statuses))
        if actual_counts != EXPECTED_STATUS_COUNTS[key]:
            raise AssertionError(f"wrong segment statuses on {key}: {actual_counts}")
        for root, (left, right) in enumerate(zip(statuses, statuses[1:])):
            for block in range(3):
                if left[block] != right[block]:
                    transitions.append(
                        (branch, side, root, block, atlas["roots"][root][2])
                    )
        atlas["samples"] = samples
        atlas["statuses"] = tuple(statuses)
        atlas["certificates"] = tuple(certificates)

    if tuple(transitions) != EXPECTED_TRANSITION:
        raise AssertionError(f"wrong status transitions: {transitions}")

    ends = receiver.node_branch_end_labels()
    endpoint_status = {}
    for branch, side, _name in RAYS:
        endpoint = ends[branch][side][0]
        parent = receiver.integer_parent(receiver.branch_parent(branch, endpoint))
        normals = topes.derived_rows(parent, normalize=False)
        endpoint_status[(branch, side)] = tuple(
            classify(normals, signature)[0]
            for signature in receiver.RECEIVER_SIGNATURES
        )
    if endpoint_status != EXPECTED_ENDPOINT_STATUS:
        raise AssertionError(f"wrong endpoint statuses: {endpoint_status}")

    center = node.rational_parent(Fraction(0), Fraction(0))
    center_normals = topes.derived_rows(center, normalize=False)
    node_rows = tuple(
        classify(center_normals, signature)
        for signature in receiver.RECEIVER_SIGNATURES
    )
    node_status = tuple(row[0] for row in node_rows)
    if node_status != EXPECTED_NODE_STATUS:
        raise AssertionError(f"wrong node statuses: {node_status}")
    return endpoint_status, node_rows


def integral_scaled_normal(normal, endpoint):
    polynomials = [
        tuple(Fraction(coefficient) * endpoint**degree for degree, coefficient in enumerate(polynomial))
        for polynomial in normal
    ]
    denominator = 1
    for polynomial in polynomials:
        for coefficient in polynomial:
            denominator = lcm(denominator, coefficient.denominator)
    integers = [
        tuple(int(coefficient * denominator) for coefficient in polynomial)
        for polynomial in polynomials
    ]
    divisor = 0
    for polynomial in integers:
        for coefficient in polynomial:
            divisor = gcd(divisor, abs(coefficient))
    return tuple(
        tuple(coefficient // divisor for coefficient in polynomial)
        for polynomial in integers
    )


def polynomial_interval(polynomial, lower, upper):
    minimum = maximum = Fraction(polynomial[-1])
    for coefficient in reversed(polynomial[:-1]):
        products = (
            minimum * lower,
            minimum * upper,
            maximum * lower,
            maximum * upper,
        )
        minimum = min(products) + coefficient
        maximum = max(products) + coefficient
    return minimum, maximum


def localization_circuit(occurrence):
    candidates = []
    for support in combinations(occurrence, 3):
        triples = [set(koszul.TRIPLES[index]) for index in support]
        common = set.intersection(*triples)
        if len(common) != 1:
            continue
        apex = next(iter(common))
        complements = [triple - {apex} for triple in triples]
        if len(set.union(*complements)) == 6 and sum(map(len, complements)) == 6:
            candidates.append(tuple(support))
    if len(candidates) != 1:
        raise AssertionError("localization occurrence has no unique circuit")
    return candidates[0]


def occurrence_circuit(occurrence):
    kind = koszul.wall_orbit(tuple(occurrence))
    if kind in mutation.ORDINARY_TYPES:
        return tuple(occurrence), kind
    if kind in mutation.LOCALIZATION_TYPES:
        return localization_circuit(occurrence), kind
    raise AssertionError("factor occurrence has a nonresidual orbit kind")


def relation_signs(normals, support, lower, upper):
    size = len(support)
    for columns in combinations(range(4), size - 1):
        signs = []
        for omitted in range(size):
            rows = [
                [normals[index][column] for column in columns]
                for position, index in enumerate(support)
                if position != omitted
            ]
            polynomial = determinant(rows)
            if omitted & 1:
                polynomial = tuple(-value for value in polynomial)
            minimum, maximum = polynomial_interval(polynomial, lower, upper)
            signs.append(1 if minimum > 0 else -1 if maximum < 0 else 0)
        if all(signs):
            return tuple(signs), columns
    raise AssertionError("a wall-circuit cofactor sign is not separated")


def circuit_positive(support, signs, signature):
    signed = tuple(
        sign * (1 if signature & (1 << index) else -1)
        for index, sign in zip(support, signs)
    )
    return all(value == signed[0] for value in signed)


def wall_status_audit(atlases, foursets, factor_occurrences):
    isolated_bad = []
    occurrence_counts = {}
    transition_relation = None
    for key, atlas in atlases.items():
        branch, side = key
        raw_normals = normal_polynomials(branch)
        normals = tuple(
            integral_scaled_normal(normal, atlas["endpoint"])
            for normal in raw_normals
        )
        tested = 0
        for root, (lower, upper, factors, _divisor) in enumerate(atlas["roots"]):
            left = atlas["statuses"][root]
            right = atlas["statuses"][root + 1]
            feasible_blocks = tuple(
                block
                for block in range(3)
                if not left[block] and not right[block]
            )
            circuits = []
            if feasible_blocks or (key == (1, "negative") and root == 240):
                for factor in factors:
                    for occurrence_index in factor_occurrences[factor]:
                        occurrence = foursets[occurrence_index]
                        support, kind = occurrence_circuit(occurrence)
                        signs, columns = relation_signs(
                            normals, support, lower, upper
                        )
                        circuits.append(
                            (support, signs, kind, occurrence_index, columns)
                        )
                        if feasible_blocks:
                            tested += 1
            for block in feasible_blocks:
                positive = tuple(
                    circuit
                    for circuit in circuits
                    if circuit_positive(
                        circuit[0], circuit[1], receiver.RECEIVER_SIGNATURES[block]
                    )
                )
                if positive:
                    isolated_bad.append((key, root, block, positive))

            if key == (1, "negative") and root == 240:
                matching = tuple(
                    circuit
                    for circuit in circuits
                    if foursets[circuit[3]] == EXPECTED_FACTOR_13063_OCCURRENCE
                )
                if len(matching) != 1:
                    raise AssertionError("factor 13063 occurrence circuit changed")
                circuit = matching[0]
                transition_relation = (
                    circuit[0],
                    circuit[1],
                    circuit[2],
                    tuple(
                        circuit_positive(
                            circuit[0], circuit[1], signature
                        )
                        for signature in receiver.RECEIVER_SIGNATURES
                    ),
                )
        occurrence_counts[key] = tested

    if isolated_bad:
        raise AssertionError(f"feasible-side isolated bad walls exist: {isolated_bad[:5]}")
    if occurrence_counts != EXPECTED_WALL_OCCURRENCES:
        raise AssertionError(f"wrong wall occurrence audit: {occurrence_counts}")
    expected_transition_relation = (
        EXPECTED_FACTOR_13063_OCCURRENCE,
        EXPECTED_FACTOR_13063_RELATION,
        50,
        (False, False, True),
    )
    if transition_relation != expected_transition_relation:
        raise AssertionError(
            f"factor 13063 relation changed: {transition_relation}"
        )
    return occurrence_counts, transition_relation


def graph_complex(atlases, endpoint_status, node_rows):
    center = ("node",)
    infinity = {("infinity", key) for key in atlases}
    vertices = [center]
    edges = []
    boundary = {}
    block_vertices = [set() for _ in range(3)]
    block_edges = [set() for _ in range(3)]
    for block, row in enumerate(node_rows):
        if row[0]:
            block_vertices[block].add(center)

    for key, atlas in atlases.items():
        roots = atlas["roots"]
        ray_vertices = [("root", key, index) for index in range(len(roots))]
        ray_edges = [("segment", key, index) for index in range(len(roots) + 1)]
        endpoint = ("infinity", key)
        vertices.extend(ray_vertices)
        edges.extend(ray_edges)
        for index, edge in enumerate(ray_edges):
            source = center if index == 0 else ray_vertices[index - 1]
            target = endpoint if index == len(roots) else ray_vertices[index]
            boundary[edge] = {source: -1, target: 1}
            for block in range(3):
                if atlas["statuses"][index][block]:
                    block_edges[block].add(edge)
        for index, vertex in enumerate(ray_vertices):
            for block in range(3):
                if (
                    atlas["statuses"][index][block]
                    or atlas["statuses"][index + 1][block]
                ):
                    block_vertices[block].add(vertex)
        for block in range(3):
            if endpoint_status[key][block]:
                block_vertices[block].add(endpoint)

    # Bad sets are closed subcomplexes, including the exact parent endpoints.
    for block in range(3):
        for edge in block_edges[block]:
            if not set(boundary[edge]) <= block_vertices[block]:
                raise AssertionError("bad edge has a missing closure vertex")

    relative_vertices = tuple(vertices)
    relative_edges = tuple(edges)
    bad = tuple(
        {
            0: set(block_vertices[block]) - infinity,
            1: set(block_edges[block]),
        }
        for block in range(3)
    )
    triple = {
        degree: set.intersection(*(space[degree] for space in bad))
        for degree in (0, 1)
    }
    pairs = (
        {degree: bad[0][degree] & bad[1][degree] for degree in (0, 1)},
        {degree: bad[0][degree] & bad[2][degree] for degree in (0, 1)},
        {degree: bad[1][degree] & bad[2][degree] for degree in (0, 1)},
    )
    exclusives = tuple(
        {degree: pair[degree] - triple[degree] for degree in (0, 1)}
        for pair in pairs
    )

    actual_dims = {
        "T": (len(triple[0]), len(triple[1])),
        "E01": (len(exclusives[0][0]), len(exclusives[0][1])),
        "E02": (len(exclusives[1][0]), len(exclusives[1][1])),
        "E12": (len(exclusives[2][0]), len(exclusives[2][1])),
    }
    t0, t1 = actual_dims["T"]
    e0 = [actual_dims[name][0] for name in ("E01", "E02", "E12")]
    e1 = [actual_dims[name][1] for name in ("E01", "E02", "E12")]
    actual_dims["C"] = (2 * t0 + sum(e0), 2 * t1 + sum(e1), 0)
    if actual_dims != EXPECTED_COMPLEX_DIMS:
        raise AssertionError(f"wrong factor-star complex dimensions: {actual_dims}")

    def order_key(cell):
        return repr(cell)

    triple_orders = {
        degree: tuple(sorted(triple[degree], key=order_key)) for degree in (0, 1)
    }
    exclusive_orders = tuple(
        {
            degree: tuple(sorted(space[degree], key=order_key))
            for degree in (0, 1)
        }
        for space in exclusives
    )

    def cochain_entries(low, high):
        low_index = {cell: index for index, cell in enumerate(low)}
        answer = []
        for row, edge in enumerate(high):
            for vertex, value in boundary[edge].items():
                if vertex in low_index:
                    answer.append((row, low_index[vertex], value))
        return tuple(answer)

    d_t = cochain_entries(triple_orders[0], triple_orders[1])
    pair_blocks = []
    attachment_edges = []
    for orders in exclusive_orders:
        d_e = cochain_entries(orders[0], orders[1])
        t_index = {cell: index for index, cell in enumerate(triple_orders[0])}
        b = []
        attached = []
        for row, edge in enumerate(orders[1]):
            row_attached = False
            for vertex, value in boundary[edge].items():
                if vertex in t_index:
                    b.append((row, t_index[vertex], value))
                    row_attached = True
            if row_attached:
                attached.append(edge)
        if len(attached) != 1:
            raise AssertionError("exclusive pair does not have one T attachment edge")
        pair_blocks.append((d_e, tuple(b)))
        attachment_edges.append(attached[0])

    c0_dimensions = [t0, t0] + e0
    c1_dimensions = [t1, t1] + e1
    c0_offsets = np.cumsum([0] + c0_dimensions)
    c1_offsets = np.cumsum([0] + c1_dimensions)
    n_entries = []

    def place(entries, block_row, block_column, scale=1):
        for row, column, value in entries:
            n_entries.append(
                (
                    int(c1_offsets[block_row] + row),
                    int(c0_offsets[block_column] + column),
                    scale * value,
                )
            )

    place(d_t, 0, 0)
    place(d_t, 1, 1)
    place(pair_blocks[0][1], 2, 0, -1)
    place(pair_blocks[0][0], 2, 2)
    place(pair_blocks[1][1], 3, 0, -1)
    place(pair_blocks[1][1], 3, 1, -1)
    place(pair_blocks[1][0], 3, 3)
    place(pair_blocks[2][1], 4, 1, -1)
    place(pair_blocks[2][0], 4, 4)
    n_entries = tuple(sorted(n_entries))

    # A full unit minor: d_T is the incidence of a tree with one infinity
    # vertex.  Each d_E becomes the same after deleting its T-attachment row.
    def unit_tree(vertices_subset, edges_subset):
        remaining_vertices = set(vertices_subset)
        remaining_edges = set(edges_subset)
        incidence = {
            vertex: {edge for edge in remaining_edges if vertex in boundary[edge]}
            for vertex in remaining_vertices
        }
        if len(remaining_vertices) != len(remaining_edges):
            raise AssertionError("proposed incidence minor is not square")
        pivots = 0
        while remaining_vertices:
            leaf = next(
                (
                    vertex
                    for vertex in remaining_vertices
                    if len(incidence[vertex] & remaining_edges) == 1
                ),
                None,
            )
            if leaf is None:
                raise AssertionError("incidence minor has a cycle/no unit leaf")
            edge = next(iter(incidence[leaf] & remaining_edges))
            if abs(boundary[edge][leaf]) != 1:
                raise AssertionError("incidence pivot is not a unit")
            remaining_vertices.remove(leaf)
            remaining_edges.remove(edge)
            pivots += 1
        if remaining_edges:
            raise AssertionError("unit leaf elimination left extra edges")
        return pivots

    t_units = unit_tree(triple_orders[0], triple_orders[1])
    e_units = []
    for orders, attachment in zip(exclusive_orders, attachment_edges):
        pivot_edges = tuple(edge for edge in orders[1] if edge != attachment)
        # All signed frontier b entries lie on the deleted attachment row, so
        # the combined N minor is block diagonal in these pivot rows.
        if any(edge != attachment for edge in orders[1] if any(
            vertex in triple[0] for vertex in boundary[edge]
        )):
            raise AssertionError("a retained E pivot row carries frontier b")
        e_units.append(unit_tree(orders[0], pivot_edges))
    unit_rank = 2 * t_units + sum(e_units)
    c0, c1, _c2 = actual_dims["C"]
    if unit_rank != c0 or c1 - unit_rank != 3:
        raise AssertionError("wrong unit rank/cokernel of N")

    # M has zero rows because the factor star is one-dimensional.  Therefore
    # its reduced bar-M has three columns and rank zero: split exactness fails
    # by a primitive free Z^3, represented by the three attachment-edge rows.
    matrix = {
        "N_shape": (c1, c0),
        "N_entries": n_entries,
        "M_shape": (0, c1),
        "N_unit_rank": unit_rank,
        "residue_rank": 3,
        "residue_tags": tuple(attachment_edges),
    }

    relative_cardinality = Counter()
    for vertex in relative_vertices:
        active = sum(vertex in bad[block][0] for block in range(3))
        relative_cardinality[active] += 1
    for edge in relative_edges:
        active = sum(edge in bad[block][1] for block in range(3))
        relative_cardinality[active] += 1
    infinity_cardinality = Counter(
        sum(endpoint in block_vertices[block] for block in range(3))
        for endpoint in infinity
    )
    mass_counts = {
        "relative_base_size2": relative_cardinality[2],
        "relative_base_size3": relative_cardinality[3],
        "relative_mass_faces": sum(
            count * ((1 << active) - 1)
            for active, count in relative_cardinality.items()
        ),
        "infinity_mass_faces": sum(
            count * ((1 << active) - 1)
            for active, count in infinity_cardinality.items()
        ),
    }
    if mass_counts != EXPECTED_MASS_COUNTS:
        raise AssertionError(f"wrong zero-mass face count: {mass_counts}")
    return actual_dims, matrix, mass_counts


def receiver_actions(atlases, node_rows):
    actions = []
    # At the node, blocks 1 and 0 respectively die along the two rays on
    # which their transverse defining factor becomes positive.
    first = atlases[(0, "negative")]
    actions.append(
        (
            "node:q0=0,q1>0",
            (1,),
            0,
            node_link.EXPECTED_FACTOR_IDS[1],
            node_link.EXPECTED_FACTOR_IDS[0],
            node_rows[1][1][1][0],
            first["certificates"][0][0][1][0],
        )
    )
    fourth = atlases[(1, "positive")]
    actions.append(
        (
            "node:q1=0,q0>0",
            (0,),
            1,
            node_link.EXPECTED_FACTOR_IDS[0],
            node_link.EXPECTED_FACTOR_IDS[1],
            node_rows[0][1][1][0],
            fourth["certificates"][0][1][1][0],
        )
    )
    third = atlases[(1, "negative")]
    actions.append(
        (
            "factor:13063",
            (2,),
            1,
            13_063,
            node_link.EXPECTED_FACTOR_IDS[1],
            EXPECTED_FACTOR_13063_OCCURRENCE,
            third["certificates"][241][1][1][0],
        )
    )
    expected = (
        (
            "node:q0=0,q1>0",
            (1,),
            0,
            12_874,
            1_657,
            (2, 32, 43),
            (0, 18, 40),
        ),
        (
            "node:q1=0,q0>0",
            (0,),
            1,
            1_657,
            12_874,
            (0, 18, 40),
            (2, 32, 43),
        ),
        (
            "factor:13063",
            (2,),
            1,
            13_063,
            12_874,
            (19, 21, 37, 38),
            (2, 32, 43),
        ),
    )
    if tuple(actions) != expected:
        raise AssertionError(f"receiver action table changed: {actions}")
    if any(not action[1] or action[2] is None for action in actions):
        raise AssertionError("receiver table contains an all-die loss")
    if any(action[3] == action[4] for action in actions):
        raise AssertionError("a loss unexpectedly became a same-factor switch")
    return tuple(actions)


def semantic_digest(atlases, endpoint_status, wall_counts, relation, matrix, mass, actions):
    digest = sha256()

    def update(value):
        if isinstance(value, Fraction):
            digest.update(b"F")
            update(value.numerator)
            update(value.denominator)
        elif isinstance(value, (tuple, list)):
            digest.update(b"[")
            for item in value:
                update(item)
            digest.update(b"]")
        elif isinstance(value, dict):
            digest.update(b"{")
            for key in sorted(value, key=repr):
                update(key)
                update(value[key])
            digest.update(b"}")
        elif isinstance(value, str):
            digest.update(b"S" + value.encode("ascii") + b"\0")
        elif isinstance(value, bool):
            digest.update(b"T" if value else b"f")
        elif isinstance(value, (int, np.integer)):
            encoded = str(int(value)).encode("ascii")
            digest.update(b"I" + encoded + b"\0")
        else:
            raise TypeError(type(value))

    root_semantics = {
        key: (
            atlas["endpoint"],
            atlas["endpoint_label"],
            tuple((row[0], row[1], row[2], row[3]) for row in atlas["roots"]),
            atlas["statuses"],
        )
        for key, atlas in atlases.items()
    }
    update(root_semantics)
    update(endpoint_status)
    update(wall_counts)
    update(relation)
    update(matrix)
    update(mass)
    update(actions)
    return digest.hexdigest()


def main():
    foursets, factor_occurrences, offsets, units, labels = factor_data()
    ends = receiver.node_branch_end_labels()
    atlases = ray_factor_atlases(
        foursets, factor_occurrences, offsets, units, labels, ends
    )
    endpoint_status, node_rows = status_atlases(atlases)
    wall_counts, relation = wall_status_audit(
        atlases, foursets, factor_occurrences
    )
    dimensions, matrix, mass_counts = graph_complex(
        atlases, endpoint_status, node_rows
    )
    actions = receiver_actions(atlases, node_rows)
    digest = semantic_digest(
        atlases,
        endpoint_status,
        wall_counts,
        relation,
        matrix,
        mass_counts,
        actions,
    )
    if EXPECTED_SEMANTIC is not None and digest != EXPECTED_SEMANTIC:
        raise AssertionError("four-ray semantic digest changed")

    print("PASS exact primitive-factor root incidences/groups:", {
        key: (atlas["incidences"], len(atlas["roots"]))
        for key, atlas in atlases.items()
    })
    print("PASS 39 simultaneous groups, maximum three factors; all factor roots simple")
    print("PASS exact segment status transition:", EXPECTED_TRANSITION[0])
    print("PASS feasible-wall signed occurrence audit:", sum(wall_counts.values()))
    print("PASS receiver losses/all-die:", len(actions), 0)
    print("PASS zero-mass relative/infinity face tags:", mass_counts)
    print("N/M SHAPES", matrix["N_shape"], matrix["M_shape"])
    print("N UNIT RANK", matrix["N_unit_rank"])
    print("EXACT OBSTRUCTION primitive free middle residue Z^", matrix["residue_rank"], sep="")
    print("SEMANTIC SHA256", digest)
    print("SCOPE compactified one-dimensional factor star; not an ambient 2-complex")


if __name__ == "__main__":
    main()
