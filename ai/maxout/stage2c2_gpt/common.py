"""Shared exact conventions for Stage 2c-2.

The only source of labels and directions is Stage 2b's
``reference_structure.json``.  In particular, nothing in this directory
imports the historically inconsistent hard-coded realization from the
Stage 2c-1 scripts.
"""
from __future__ import annotations

import itertools
import json
import math
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
MAXOUT = HERE.parent
REFERENCE_PATH = MAXOUT / "stage2b_gpt" / "reference_structure.json"
REFERENCE = json.loads(REFERENCE_PATH.read_text(encoding="utf-8"))

PAIRS = tuple(itertools.combinations(range(5), 2))
TRIPLES = tuple(itertools.combinations(range(5), 3))
PAIR_INDEX = {pair: index for index, pair in enumerate(PAIRS)}
TRIPLE_INDEX = {triple: index for index, triple in enumerate(TRIPLES)}
MASK20 = (1 << 20) - 1

U_INTS = tuple(tuple(int(value) for value in row)
               for row in REFERENCE["U_ints"])
REPRESENTATIVES = tuple(
    int(bits) for bits in REFERENCE["global_flip_representatives"]
)
VALID_BITS = tuple(sorted(
    bits
    for representative in REPRESENTATIVES
    for bits in (representative, representative ^ MASK20)
))

if tuple(tuple(pair) for pair in REFERENCE["pairs_in_class_order"]) != PAIRS:
    raise AssertionError("reference pair order does not match lexicographic order")
if len(VALID_BITS) != 33140 or len(set(VALID_BITS)) != 33140:
    raise AssertionError("reference does not contain 33,140 labeled sigmas")


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def det3(a, b, c):
    return dot(a, cross(b, c))


def permutation_sign(values):
    inversions = sum(
        values[i] > values[j]
        for i in range(len(values))
        for j in range(i + 1, len(values))
    )
    return -1 if inversions % 2 else 1


def signed_det(indices, values=None):
    """Return det(U_a,U_b,U_c), or its sign when values is omitted."""
    if len(set(indices)) < 3:
        return 0
    ordered = tuple(sorted(indices))
    sign = permutation_sign(indices)
    if values is None:
        raw = det3(*(U_INTS[index] for index in ordered))
        if raw == 0:
            raise AssertionError("reference configuration is not uniform")
        return sign * (1 if raw > 0 else -1)
    return sign * values[ordered]


DET_ABS = {
    triple: abs(det3(*(U_INTS[index] for index in triple)))
    for triple in TRIPLES
}
CHI = {
    triple: 1 if det3(*(U_INTS[index] for index in triple)) > 0 else -1
    for triple in TRIPLES
}


def sigma_sign(bits, side):
    return 1 if bits & (1 << side) else -1


def class_pattern(bits):
    """Ten symbols in PAIRS order: +, -, or x for unequal side signs."""
    symbols = []
    for class_index in range(10):
        plus = sigma_sign(bits, 2 * class_index)
        minus = sigma_sign(bits, 2 * class_index + 1)
        if plus == minus == 1:
            symbols.append("+")
        elif plus == minus == -1:
            symbols.append("-")
        else:
            symbols.append("x")
    return "".join(symbols)


def split_signs(k):
    if k not in (1, 2):
        raise ValueError("Stage 2c-2 core sweep uses k in {1,2}")
    return tuple(1 if index < k else -1 for index in range(5))


def reduced_equal_pair_rows(pattern, k):
    """Return (eligible class indices, exact five-column reduced rows).

    An eligible class has equal sigma signs.  Its row is the sum of the
    two full side rows, hence its T block is identically zero and its
    weight entries are 2*q_ij*s_t*D_tij.  The final five rows are the
    positive-weight coordinate rows.
    """
    if len(pattern) != 10 or any(marker not in "+-x" for marker in pattern):
        raise ValueError("invalid class pattern")
    split = split_signs(k)
    eligible = []
    rows = []
    for class_index, ((i, j), marker) in enumerate(zip(PAIRS, pattern)):
        if marker == "x":
            continue
        eligible.append(class_index)
        q = 1 if marker == "+" else -1
        rows.append([
            0 if t in (i, j)
            else 2 * q * split[t] * DET_ABS[tuple(sorted((t, i, j)))]
            for t in range(5)
        ])
    rows.extend([
        [1 if q == t else 0 for q in range(5)]
        for t in range(5)
    ])
    return tuple(eligible), tuple(tuple(row) for row in rows)


def full_system_rows_for_split(bits, split):
    """The authoritative 25 by 8 row model for an explicit +/- split."""
    split = tuple(int(value) for value in split)
    if len(split) != 5 or any(value not in (-1, 1) for value in split):
        raise ValueError("split must contain five +/-1 entries")
    rows = []
    for class_index, (i, j) in enumerate(PAIRS):
        normal = cross(U_INTS[i], U_INTS[j])
        weights = [
            0 if t in (i, j)
            else split[t] * DET_ABS[tuple(sorted((t, i, j)))]
            for t in range(5)
        ]
        for side_in_class, ray_sign in ((0, 1), (1, -1)):
            side = 2 * class_index + side_in_class
            sigma = sigma_sign(bits, side)
            rows.append([
                sigma * ray_sign * value for value in normal
            ] + [
                sigma * value for value in weights
            ])
    rows.extend([
        [0, 0, 0] + [1 if q == t else 0 for q in range(5)]
        for t in range(5)
    ])
    return tuple(tuple(row) for row in rows)


def full_system_rows(bits, k):
    """The authoritative 25 by 8 Stage 2b row model."""
    return full_system_rows_for_split(bits, split_signs(k))


def lift_reduced_certificate(bits, pattern, certificate):
    """Lift reduced sparse multipliers to the 25 full rows."""
    eligible = [
        class_index
        for class_index, marker in enumerate(pattern)
        if marker != "x"
    ]
    lifted = {}
    for reduced_row, value in certificate:
        if reduced_row < len(eligible):
            class_index = eligible[reduced_row]
            lifted[2 * class_index] = value
            lifted[2 * class_index + 1] = value
        else:
            weight = reduced_row - len(eligible)
            lifted[20 + weight] = value
    return tuple(sorted(
        (int(row), int(value))
        for row, value in lifted.items()
        if value
    ))


def check_sparse_kernel(rows, certificate):
    if not certificate:
        return False
    if any(
        not isinstance(row, int)
        or not isinstance(value, int)
        or row < 0
        or row >= len(rows)
        or value <= 0
        for row, value in certificate
    ):
        return False
    if len({row for row, _ in certificate}) != len(certificate):
        return False
    totals = [
        sum(value * rows[row][column] for row, value in certificate)
        for column in range(len(rows[0]))
    ]
    return totals == [0] * len(rows[0])


def parse_fraction(text):
    return Fraction(text)


def fraction_text(value):
    value = Fraction(value)
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def primitive_integer_vector(values):
    values = [Fraction(value) for value in values]
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
    return [value // divisor for value in integers]
