#!/usr/bin/env python3
"""Exact checks for the numerical claims in SEEAT.md.

No floating point arithmetic and no third-party packages are used.  The
intersection lattice calculation is rank-specific but independent of the
realizability search code.
"""

from collections import Counter
from itertools import combinations, permutations, product
import json
from math import ceil, factorial, gcd
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CERTS = HERE / "certs_4_8.jsonl"
EXTCOUNTS = ROOT / "ai" / "omgamma" / "data" / "extcount_4_9.jsonl"
MASS_TARGET = ROOT / "ai" / "omgamma" / "data" / "mass_target_4_9.json"
CATALOG_48 = ROOT / "ai" / "omgamma" / "data" / "cat_4_8.txt"


def det3(a, b, c, cols):
    i, j, k = cols
    return (
        a[i] * (b[j] * c[k] - b[k] * c[j])
        - a[j] * (b[i] * c[k] - b[k] * c[i])
        + a[k] * (b[i] * c[j] - b[j] * c[i])
    )


def det4(a, b, c, d):
    return (
        a[0] * det3(b, c, d, (1, 2, 3))
        - a[1] * det3(b, c, d, (0, 2, 3))
        + a[2] * det3(b, c, d, (0, 1, 3))
        - a[3] * det3(b, c, d, (0, 1, 2))
    )


def colex_subsets(n, size):
    return tuple(
        sorted(
            combinations(range(1, n + 1), size),
            key=lambda subset: tuple(reversed(subset)),
        )
    )


def sort_with_sign(values):
    values = list(values)
    sign = 1
    for i in range(1, len(values)):
        j = i
        while j and values[j - 1] > values[j]:
            values[j - 1], values[j] = values[j], values[j - 1]
            sign = -sign
            j -= 1
    return tuple(values), sign


def gp3_conditions(n, r):
    """Compile the uniform three-term GP test into exact bit operations.

    Bit 1 means a positive chirotope value.  Each returned row encodes the
    three signed products, with parity 0 meaning a positive product.
    """
    bases = colex_subsets(n, r)
    index = {basis: i for i, basis in enumerate(bases)}
    rows = []
    for lam in combinations(range(1, n + 1), r - 2):
        rest = [element for element in range(1, n + 1) if element not in lam]
        for a, b, c, d in combinations(rest, 4):
            entries = []
            for (x, y), explicit_minus in (
                ((a, b), 0),
                ((c, d), 0),
                ((a, c), 1),
                ((b, d), 0),
                ((a, d), 0),
                ((b, c), 0),
            ):
                basis, sign = sort_with_sign(lam + (x, y))
                entries.append((index[basis], (sign < 0) ^ explicit_minus))
            rows.append(
                (
                    entries[0][0], entries[1][0], entries[0][1] ^ entries[1][1],
                    entries[2][0], entries[3][0], entries[2][1] ^ entries[3][1],
                    entries[4][0], entries[5][0], entries[4][1] ^ entries[5][1],
                )
            )
    return tuple(rows)


def is_uniform_chirotope(mask, conditions):
    for i1, i2, c1, i3, i4, c2, i5, i6, c3 in conditions:
        p1 = ((mask >> i1) ^ (mask >> i2) ^ c1) & 1
        p2 = ((mask >> i3) ^ (mask >> i4) ^ c2) & 1
        p3 = ((mask >> i5) ^ (mask >> i6) ^ c3) & 1
        if p1 == p2 == p3:
            return False
    return True


def lexicographic_signatures(parent):
    """Distinct uniform signatures [a1^e1,...,a4^e4] of a UOM(4,8)."""
    assert len(parent) == 70 and set(parent) <= {"+", "-"}
    bases = colex_subsets(8, 4)
    index = {basis: i for i, basis in enumerate(bases)}
    new_bases = colex_subsets(8, 3)
    signatures = set()
    for sequence in permutations(range(1, 9), 4):
        for epsilons in product((1, -1), repeat=4):
            signature = 0
            for variable, triple in enumerate(new_bases):
                for element, epsilon in zip(sequence, epsilons):
                    if element in triple:
                        continue
                    basis, alternating_sign = sort_with_sign(triple + (element,))
                    parent_sign = 1 if parent[index[basis]] == "+" else -1
                    if epsilon * alternating_sign * parent_sign > 0:
                        signature |= 1 << variable
                    break
            signatures.add(signature)
    return signatures


def primitive_plane_normal(a, b, c):
    """Primitive normal n with n.x = +/-det(a,b,c,x)."""
    n = [
        -det3(a, b, c, (1, 2, 3)),
        det3(a, b, c, (0, 2, 3)),
        -det3(a, b, c, (0, 1, 3)),
        det3(a, b, c, (0, 1, 2)),
    ]
    divisor = 0
    for value in n:
        divisor = gcd(divisor, abs(value))
    assert divisor
    n = [value // divisor for value in n]
    for value in n:
        if value:
            if value < 0:
                n = [-entry for entry in n]
            break
    return tuple(n)


def characteristic_data(points):
    """Möbius sums and regions of the 56-plane central arrangement."""
    assert len(points) == 8 and all(len(point) == 4 for point in points)
    assert all(
        det4(points[i], points[j], points[k], points[l])
        for i, j, k, l in combinations(range(8), 4)
    ), "base configuration is not uniform"

    normals = [
        primitive_plane_normal(points[i], points[j], points[k])
        for i, j, k in combinations(range(8), 3)
    ]
    assert len(normals) == 56
    assert len(set(normals)) == 56, "derived arrangement is not simple in rank one"

    # Rank-two flats of the normal matroid.  A simple rank-two flat containing
    # k atoms has Möbius value k-1.
    rank_two = {}
    for i, j in combinations(range(56), 2):
        a, b = normals[i], normals[j]
        parallel = all(
            a[u] * b[v] == a[v] * b[u]
            for u, v in combinations(range(4), 2)
        )
        assert not parallel
        flat = frozenset(
            h
            for h, c in enumerate(normals)
            if all(
                det3(a, b, c, cols) == 0
                for cols in combinations(range(4), 3)
            )
        )
        rank_two[flat] = len(flat) - 1

    # Rank-three flats, closed using one exact 4x4 determinant.  The Möbius
    # recursion uses all rank-two flats contained in the closure.
    rank_three = {}
    for i, j, k in combinations(range(56), 3):
        a, b, c = normals[i], normals[j], normals[k]
        if all(
            det3(a, b, c, cols) == 0
            for cols in combinations(range(4), 3)
        ):
            continue
        flat = frozenset(
            h for h, d in enumerate(normals) if det4(a, b, c, d) == 0
        )
        if flat in rank_three:
            continue
        mu = -(
            1
            - len(flat)
            + sum(value for lower, value in rank_two.items() if lower <= flat)
        )
        rank_three[flat] = mu

    mu_sums = (
        1,
        -56,
        sum(rank_two.values()),
        sum(rank_three.values()),
    )
    mu_top = -sum(mu_sums)
    characteristic = mu_sums + (mu_top,)
    regions = sum(abs(value) for value in characteristic)
    return {
        "characteristic": characteristic,
        "regions": regions,
        "flat_counts": (1, 56, len(rank_two), len(rank_three), 1),
    }


def first_catalog_matrix():
    with CERTS.open(encoding="utf-8") as handle:
        for line in handle:
            record = json.loads(line)
            if record["verdict"] == "REALIZABLE":
                matrix = record["matrix"]
                return [
                    tuple(matrix[row][column] for row in range(4))
                    for column in range(8)
                ]
    raise AssertionError("no realizable (4,8) certificate found")


def check_arrangement():
    generic = characteristic_data(first_catalog_matrix())
    expected_characteristic = (1, -56, 1260, -13000, 11795)
    assert generic["characteristic"] == expected_characteristic
    assert generic["regions"] == 26112
    assert generic["flat_counts"] == (1, 56, 1148, 9808, 1)

    # Canary: the moment curve is a uniform base configuration but is special
    # for the derived arrangement.  A checker that silently substitutes the
    # generic answer will miss this 1,440-tope drop.
    moment_curve = [tuple((1, t, t * t, t * t * t)) for t in range(1, 9)]
    special = characteristic_data(moment_curve)
    assert special["characteristic"] == (1, -56, 1244, -12280, 11091)
    assert special["regions"] == 24672
    assert special["regions"] < generic["regions"]
    print("PASS exact derived arrangements: generic 26112; canary 24672")


def check_census_arithmetic():
    with EXTCOUNTS.open(encoding="utf-8") as handle:
        rows = [json.loads(line) for line in handle if line.strip()]
    target = json.loads(MASS_TARGET.read_text(encoding="utf-8"))

    assert len(rows) == 2628
    assert {row["i"] for row in rows} == set(range(2628))

    group_8 = factorial(8) * (1 << 9)
    labeled_parents = 0
    labeled_children = 0
    for row in rows:
        stabilizer = row["stab"]
        assert stabilizer > 0 and group_8 % stabilizer == 0
        orbit = group_8 // stabilizer
        labeled_parents += orbit
        labeled_children += orbit * row["E"]

    assert sum(row["E"] for row in rows) == target["sum_E_over_reps"]
    assert labeled_children == int(target["N_chi"])
    assert labeled_parents == 25_703_946_240

    topes = 26_112
    raw_widths = Counter(ceil(row["E"] / topes) for row in rows)
    assert raw_widths == Counter({2: 5, 3: 2525, 4: 98})
    assert min(row["E"] for row in rows) == 50_358
    assert max(row["E"] for row in rows) == 97_224

    one_chart_capacity = labeled_parents * topes
    assert one_chart_capacity == 671_181_444_218_880
    assert ceil(labeled_children / one_chart_capacity) == 3
    print(
        "PASS exact census arithmetic: widths 2/3/4 = 5/2525/98; "
        "fixed-deletion raw capacity needs 3 chart layers"
    )


def check_four_chart_gate():
    parents = [line.strip() for line in CATALOG_48.open() if line.strip()]
    certificates = [json.loads(line) for line in CERTS.open() if line.strip()]
    with EXTCOUNTS.open(encoding="utf-8") as handle:
        counts = {row["i"]: row for row in map(json.loads, handle)}

    parent_index = 2599
    parent = parents[parent_index]
    assert len(parents) == len(certificates) == 2628
    assert parent == certificates[parent_index]["chi"]
    assert certificates[parent_index]["verdict"] == "REALIZABLE"
    assert counts[parent_index] == {"i": parent_index, "E": 97_224, "stab": 16}

    signatures = lexicographic_signatures(parent)
    assert len(signatures) == 2_624

    # The first C(8,4)=70 bases of a rank-4 chirotope on [9] avoid element
    # 9; the last C(8,3)=56 contain it.  Check every distinct lexicographic
    # signature against all three-term GP relations, independently of the
    # extension enumerator that produced extcount_4_9.jsonl.
    parent_mask = sum(1 << i for i, sign in enumerate(parent) if sign == "+")
    conditions = gp3_conditions(9, 4)
    assert len(conditions) == 1_260
    assert all(
        is_uniform_chirotope(parent_mask | (signature << 70), conditions)
        for signature in signatures
    )

    one_chart = 26_112
    four_capacity = 4 * one_chart - 3 * len(signatures)
    assert four_capacity == 96_576
    assert counts[parent_index]["E"] - four_capacity == 648
    assert four_capacity + 1 == 96_577
    print(
        "PASS four-chart gate: parent 2599 has E=97224, lex core=2624, "
        "four-chart capacity=96576; <=647 nonreal extensions refutes four"
    )


def main():
    check_arrangement()
    check_census_arithmetic()
    check_four_chart_gate()
    print("ALL SEEAT CHECKS PASSED")


if __name__ == "__main__":
    main()
