#!/usr/bin/env python3
"""Exact tiny geometry discriminator; no signature or cohomology claim."""
import itertools
import json
from fractions import Fraction
from pathlib import Path


def det(matrix):
    a = [[Fraction(x) for x in row] for row in matrix]
    value = Fraction(1)
    for i in range(len(a)):
        pivot = next((j for j in range(i, len(a)) if a[j][i]), None)
        if pivot is None:
            return Fraction(0)
        if pivot != i:
            a[i], a[pivot] = a[pivot], a[i]
            value = -value
        value *= a[i][i]
        scale = a[i][i]
        a[i] = [x / scale for x in a[i]]
        for j in range(i + 1, len(a)):
            scale = a[j][i]
            a[j] = [x - scale * y for x, y in zip(a[j], a[i])]
    return value


def normal(parent, support):
    rows = [parent[i - 1] for i in support]
    return tuple((-1) ** j * det([[row[k] for k in range(4) if k != j]
                                 for row in rows]) for j in range(4))


def proportional(a, b):
    return all(a[i] * b[j] == a[j] * b[i]
               for i, j in itertools.combinations(range(4), 2))


def main():
    parent = [tuple(Fraction(t) ** k for k in range(4)) for t in range(8)]
    moved = list(parent)
    moved[0] = tuple(a + b for a, b in zip(parent[0], parent[1]))
    brackets = list(itertools.combinations(range(8), 4))
    assert all(det([parent[i] for i in b]) > 0 for b in brackets)
    assert all(det([moved[i] for i in b]) > 0 for b in brackets)
    # All six selected planes through parent line 12 are literally fixed.
    selected = [(1, 2, k) for k in range(3, 9)]
    assert all(normal(parent, u) == normal(moved, u) for u in selected)
    before = normal(parent, (1, 4, 5))
    after = normal(moved, (1, 4, 5))
    added = normal(parent, (2, 4, 5))
    assert after == tuple(a + b for a, b in zip(before, added))
    assert not proportional(before, after)
    assert not proportional(before, added)
    # The deliberately false extrapolation must fail on the same exact data.
    try:
        assert proportional(before, after), "omitted normal is not a fixed ray"
    except AssertionError:
        hostile = "rejected"
    else:
        raise AssertionError("false all-normal-scaling extrapolation accepted")
    result = {
        "classification": "finite exact geometry only",
        "parent": "eight rational moment-curve columns (1,t,t^2,t^3), t=0,...,7",
        "motion": "column 1 replaced by column 1 + column 2",
        "positive_parent_brackets_before_and_after": len(brackets),
        "selected_unchanged_normal_rays": len(selected),
        "normal_145_before": [int(x) for x in before],
        "normal_145_after": [int(x) for x in after],
        "normal_245": [int(x) for x in added],
        "omitted_normal_rotates": True,
        "false_all_normal_scaling_control": hostile,
        "valid_extension_signature_asserted": False,
        "positive_gordan_support_asserted": False,
        "feasibility_change_asserted": False,
        "original_obligation_closed": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
