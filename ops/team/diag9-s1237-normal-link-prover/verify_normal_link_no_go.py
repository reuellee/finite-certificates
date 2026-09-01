#!/usr/bin/env python3
"""Exact replay and hostile audit of the S12,37 singular-link endpoint."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from fractions import Fraction
from functools import reduce
import json
from math import gcd
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build_normal_link_no_go as producer  # noqa: E402


STORED = {
    "manifest": HERE / "SOURCE_MANIFEST.json",
    "literals": HERE / "ACTIVE_LITERAL_INVENTORY.json",
    "normal_forms": HERE / "NORMAL_FORM_INVENTORY.json",
    "result": HERE / "DIAG9_S1237_NORMAL_LINK_NO_GO.json",
    "canaries": HERE / "CANARIES.json",
}


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def primitive_vector(values):
    denominator = 1
    for value in values:
        denominator = denominator * value.denominator // gcd(
            denominator, value.denominator
        )
    integers = [int(value * denominator) for value in values]
    common = reduce(gcd, (abs(value) for value in integers if value), 0)
    require(common, "zero derivative vector")
    return tuple(value // common for value in integers)


def evaluate_monomial(exponent, point):
    value = Fraction(1)
    for coordinate, power in zip(point, exponent, strict=True):
        value *= coordinate ** power
    return value


def independent_first_derivative(polynomial, target, support):
    """Differentiate the pinned parent polynomial without producer expansion."""

    a, g, h = producer.TANGENT_POINT
    if support == (3, 1, 15):
        base = (a, 0, 0, 0, 0, 0, g, h, g)
        source_by_normal = (1, 2, 3, 4, 5, 8)
    elif support == (3, 3, 7):
        base = (a, 0, 0, g, 0, 0, g, h, 0)
        source_by_normal = (1, 2, 4, 5, 8, 3)
    else:
        raise ValueError(support)

    tangential = sum(
        target * coefficient * evaluate_monomial(exponent, base)
        for exponent, coefficient in polynomial.items()
    )
    require(tangential == 0, "claimed parent form is not tangentially zero")
    derivative = []
    for variable in source_by_normal:
        value = Fraction(0)
        for exponent, coefficient in polynomial.items():
            power = exponent[variable]
            if not power:
                continue
            reduced = list(exponent)
            reduced[variable] -= 1
            value += (
                target
                * coefficient
                * power
                * evaluate_monomial(tuple(reduced), base)
            )
        derivative.append(value)
    return primitive_vector(derivative)


def independent_gordan_replay(result):
    records = [
        json.loads(line)
        for line in producer.parent_gate.CATALOG.read_text().splitlines()
        if line
    ]
    parents, _digest = producer.parent_gate.parent_polynomials(
        records[producer.parent_gate.PARENT]
    )
    by_label = {
        label: (target, polynomial)
        for label, target, polynomial, _terms in parents
    }
    expected = (
        ((3, 1, 15), "1237", "1367", 4, "n4=0"),
        ((3, 3, 7), "1237", "1278", 3, "n3=0"),
    )
    rows = result["obstruction"]["singular_supports"]
    require(len(rows) == len(expected), "singular support census drift")
    for row, (support, positive_label, negative_label, axis, facet) in zip(
        rows, expected, strict=True
    ):
        require(tuple(row["support"]) == support, "Gordan support mutation")
        require(row["positive_parent_label"] == positive_label, "positive label mutation")
        require(row["negative_parent_label"] == negative_label, "negative label mutation")
        positive = independent_first_derivative(
            by_label[positive_label][1], by_label[positive_label][0], support
        )
        negative = independent_first_derivative(
            by_label[negative_label][1], by_label[negative_label][0], support
        )
        expected_positive = tuple(int(index == axis) for index in range(6))
        expected_negative = tuple(-value for value in expected_positive)
        require(positive == expected_positive, "positive source orientation changed")
        require(negative == expected_negative, "negative source orientation changed")
        stored_positive = tuple(
            int(entry["coefficient"])
            if tuple(entry["exponent"]) == expected_positive else 0
            for entry in row["positive_initial_form"]
        )
        stored_negative = tuple(
            int(entry["coefficient"])
            if tuple(entry["exponent"]) == expected_positive else 0
            for entry in row["negative_initial_form"]
        )
        require(stored_positive == (1,), "stored positive initial form mutation")
        require(stored_negative == (-1,), "stored negative initial form mutation")
        weights = tuple(map(int, row["positive_gordan_weights"]))
        require(weights == (1, 1), "Gordan weight mutation")
        weighted = tuple(
            weights[0] * positive[index] + weights[1] * negative[index]
            for index in range(6)
        )
        require(weighted == (0,) * 6, "Gordan relation is nonzero")
        require(row["weighted_sum"] == [], "stored Gordan sum is not zero")
        require(row["strict_first_order_parent_link_feasible"] is False, "false strict feasibility")
        require(row["forced_recursive_facet"] == facet, "forced facet mutation")
    return len(rows)


def validate_result(candidate, expected):
    require(candidate == expected, "stored result does not exactly rebuild")
    require(candidate["endpoint"] == "NORMAL_LINK_REDUCTION_NO_GO", "endpoint mutation")
    require(candidate["classification"] == "FINITE_EXACT_COMPUTATION", "classification mutation")
    scope = candidate["scope"]
    require(scope["result"] == "FIRST_ORDER_PARENT_NORMAL_LINK_SINGULAR_ON_BOTH_SUPPORTS", "scope mutation")
    require(scope["honest_9dvl_score"] == "2/9", "false ledger promotion")
    require(scope["tangential_filter_is_not_a_collar"] is True, "tangential promotion")
    require(scope["diagonal_9_proof_or_counterexample"] == "NOT_CLAIMED", "false D9 claim")
    obstruction = candidate["obstruction"]
    require(obstruction["ordinary_projectivized_strict_parent_link"] == "EMPTY", "strict link mutation")
    require(obstruction["higher_weighted_orders_required"] is True, "weighted frontier dropped")
    require(
        obstruction["stabilization_status"]
        == "ORDINARY_FIRST_ORDER_LINK_INVALID_BEFORE_RADIUS_STAGE",
        "fake ordinary stabilization",
    )
    require("does not exclude weighted parent-safe arcs" in candidate["nonconsequence"], "false no-arc claim")
    return independent_gordan_replay(candidate)


def hostile_canaries(stored, expected):
    mutations = []

    candidate = deepcopy(stored["result"])
    candidate["obstruction"]["singular_supports"][0]["support"] = [3, 3, 7]
    mutations.append(("support", "result", candidate))
    candidate = deepcopy(stored["result"])
    candidate["obstruction"]["singular_supports"][0]["negative_parent_label"] = "1278"
    mutations.append(("label", "result", candidate))
    candidate = deepcopy(stored["result"])
    candidate["obstruction"]["singular_supports"][0]["negative_initial_form"][0]["coefficient"] = 1
    mutations.append(("orientation", "result", candidate))
    candidate = deepcopy(stored["result"])
    candidate["obstruction"]["singular_supports"][1]["positive_gordan_weights"] = [1, 2]
    mutations.append(("Gordan weight", "result", candidate))
    candidate = deepcopy(stored["result"])
    candidate["obstruction"]["stabilization_status"] = "RADIUS_1"
    mutations.append(("fake radius", "result", candidate))
    candidate = deepcopy(stored["result"])
    candidate["nonconsequence"] = "No inward arcs exist."
    mutations.append(("false no-arc claim", "result", candidate))
    candidate = deepcopy(stored["result"])
    candidate["scope"]["honest_9dvl_score"] = "3/9"
    mutations.append(("ledger", "result", candidate))

    candidate = deepcopy(stored["literals"])
    candidate["literal_rows"].pop()
    mutations.append(("drop literal", "literals", candidate))
    candidate = deepcopy(stored["literals"])
    candidate["literal_rows"][0]["allowed_primitive_sign"] *= -1
    mutations.append(("flip literal", "literals", candidate))
    candidate = deepcopy(stored["literals"])
    candidate["literal_rows"][0]["occurrences"].pop()
    mutations.append(("drop occurrence", "literals", candidate))
    unit_row = next(
        occurrence
        for literal in stored["literals"]["literal_rows"]
        for occurrence in literal["occurrences"]
        if occurrence["unit_bracket_label"] is not None
    )
    candidate = deepcopy(stored["literals"])
    located = next(
        occurrence
        for literal in candidate["literal_rows"]
        for occurrence in literal["occurrences"]
        if occurrence["occurrence_index"] == unit_row["occurrence_index"]
    )
    located["unit_sign_in_parent"] *= -1
    mutations.append(("flip unit", "literals", candidate))

    candidate = deepcopy(stored["normal_forms"])
    candidate["supports"][0]["factor_initial_forms"].pop()
    mutations.append(("drop factor normal form", "normal_forms", candidate))
    candidate = deepcopy(stored["normal_forms"])
    candidate["supports"][1]["parent_initial_forms"].pop()
    mutations.append(("drop parent normal form", "normal_forms", candidate))

    rejected = 0
    for label, kind, candidate in mutations:
        try:
            if kind == "result":
                validate_result(candidate, expected["result"])
            else:
                require(candidate == expected[kind], f"{kind} does not rebuild")
        except (AssertionError, KeyError, TypeError, ValueError):
            rejected += 1
            continue
        raise AssertionError(f"hostile mutation accepted: {label}")
    require(rejected == len(mutations), "hostile rejection census drift")
    return rejected


def main():
    stored = {name: load(path) for name, path in STORED.items()}
    rebuilt_values = producer.build_all()
    expected = dict(zip(
        ("manifest", "literals", "normal_forms", "result", "canaries"),
        rebuilt_values,
        strict=True,
    ))
    for name in expected:
        require(stored[name] == expected[name], f"stored artifact does not rebuild: {name}")
    gordan = validate_result(stored["result"], expected["result"])
    rejected = hostile_canaries(stored, expected)

    require(stored["literals"]["factor_count"] == 3_539, "literal count drift")
    require(stored["literals"]["occurrence_count"] == 6_167, "occurrence count drift")
    require(sum(
        len(row["factor_initial_forms"])
        for row in stored["normal_forms"]["supports"]
    ) == 7_078, "factor initial-form count drift")
    require(sum(
        len(row["parent_initial_forms"])
        for row in stored["normal_forms"]["supports"]
    ) == 140, "parent initial-form count drift")
    print(
        "PASS D9 S12,37 normal-link producer:",
        "3539 oriented literals / 6167 occurrences / 7078 factor forms / 140 parent forms;",
        gordan, "exact source-derived Gordan obstructions;",
        f"{rejected}/{rejected} hostile mutations rejected;",
        "endpoint NORMAL_LINK_REDUCTION_NO_GO; ledger 2/9",
    )
    print(
        "SCOPE ordinary common-radial strict parent link is empty;",
        "weighted blow-ups remain required; no collar, no no-arc theorem, no D9 result",
    )


if __name__ == "__main__":
    main()
