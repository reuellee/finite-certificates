#!/usr/bin/env python3
"""Independent exact audit of the parent-860 plane projection certificate.

This verifier imports neither the projection producer, Bernstein cover, nor
the closed-form resultant implementation.  It reconstructs all 26,740 plane
restrictions directly from the global factor census, proves every nonconstant
restriction is an irreducible line or nonsingular conic, rebuilds the parent
triangle from all parent brackets, and independently classifies which factors
meet its closure or interior by exact quadratic optimization.

The large resultant frontier is then checked as a fail-closed, hash-pinned
engineering object.  Its full deterministic replay remains the producer's
responsibility; no atlas or diagonal-nine theorem is inferred from it.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from math import gcd, lcm
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as representative  # noqa: E402
import DIAG9_GRAPH_parent860_star as star  # noqa: E402


ARTIFACT = HERE / "data" / "DIAG9_GRAPH_parent860_plane_projection_frontier.json"
EXPECTED_SEMANTIC_SHA256 = "cbcee4e0e7a7e757b9751f06349337d14206e102e4afaffd5abdd3833718a0fd"
VARIABLES = (7, 8)
EXPECTED_VERTICES = (
    (Fraction(12_164, 31_931), Fraction(12_164, 31_931)),
    (Fraction(1_858_210, 2_854_579), Fraction(12_164, 31_931)),
    (Fraction(1_858_210, 2_854_579), Fraction(1_858_210, 2_854_579)),
)


def restrict_plane(polynomial, base):
    answer = defaultdict(Fraction)
    for exponent, coefficient in polynomial.items():
        value = Fraction(coefficient)
        for axis in range(9):
            if axis not in VARIABLES and exponent[axis]:
                value *= base[axis] ** exponent[axis]
        answer[(exponent[7], exponent[8])] += value
    return {monomial: value for monomial, value in answer.items() if value}


def primitive(polynomial):
    if not polynomial:
        return ()
    denominator = 1
    for value in polynomial.values():
        denominator = lcm(denominator, Fraction(value).denominator)
    integer = {
        monomial: int(Fraction(value) * denominator)
        for monomial, value in polynomial.items()
    }
    divisor = 0
    for value in integer.values():
        divisor = gcd(divisor, abs(value))
    integer = {monomial: value // divisor for monomial, value in integer.items()}
    leading = max(integer)
    if integer[leading] < 0:
        integer = {monomial: -value for monomial, value in integer.items()}
    return tuple(sorted(integer.items()))


def determinant3(matrix):
    (a, b, c), (d, e, f), (g, h, i) = matrix
    return a * (e * i - f * h) - b * (d * i - f * g) + c * (d * h - e * g)


def total_degree(polynomial):
    return max((sum(monomial) for monomial, _coefficient in polynomial), default=0)


def bidegree(polynomial):
    return tuple(max(monomial[axis] for monomial, _coefficient in polynomial) for axis in range(2))


def conic_determinant(polynomial):
    values = dict(polynomial)
    return determinant3(
        (
            (2 * values.get((2, 0), 0), values.get((1, 1), 0), values.get((1, 0), 0)),
            (values.get((1, 1), 0), 2 * values.get((0, 2), 0), values.get((0, 1), 0)),
            (values.get((1, 0), 0), values.get((0, 1), 0), 2 * values.get((0, 0), 0)),
        )
    )


def evaluate(polynomial, point):
    h, i = point
    return sum(Fraction(coefficient) * h**monomial[0] * i**monomial[1] for monomial, coefficient in polynomial)


def segment_point(left, right, parameter):
    return tuple(first + parameter * (second - first) for first, second in zip(left, right))


def edge_stationary(polynomial, left, right):
    p0 = evaluate(polynomial, left)
    p1 = evaluate(polynomial, right)
    pm = evaluate(polynomial, segment_point(left, right, Fraction(1, 2)))
    quadratic = 2 * (p1 + p0 - 2 * pm)
    linear = p1 - p0 - quadratic
    if not quadratic:
        return None
    parameter = -linear / (2 * quadratic)
    return segment_point(left, right, parameter) if 0 < parameter < 1 else None


def inside(point, halfspaces):
    h, i = point
    return all(a * h + b * i + c >= 0 for a, b, c in halfspaces)


def stationary(polynomial):
    values = dict(polynomial)
    h = Fraction(values.get((1, 0), 0))
    i = Fraction(values.get((0, 1), 0))
    hh = Fraction(values.get((2, 0), 0))
    hi = Fraction(values.get((1, 1), 0))
    ii = Fraction(values.get((0, 2), 0))
    determinant = 4 * hh * ii - hi * hi
    if not determinant:
        return None
    return ((hi * i - 2 * ii * h) / determinant, (hi * h - 2 * hh * i) / determinant)


def exact_range(polynomial, vertices, halfspaces):
    candidates = list(vertices)
    for left, right in combinations(vertices, 2):
        point = edge_stationary(polynomial, left, right)
        if point is not None:
            candidates.append(point)
    point = stationary(polynomial)
    if point is not None and inside(point, halfspaces):
        candidates.append(point)
    values = tuple(evaluate(polynomial, point) for point in candidates)
    return min(values), max(values)


def affine_halfspace(polynomial, base):
    values = dict(polynomial)
    if set(values) - {(0, 0), (1, 0), (0, 1)}:
        raise AssertionError("nonaffine parent bracket restriction")
    row = [Fraction(values.get((1, 0), 0)), Fraction(values.get((0, 1), 0)), Fraction(values.get((0, 0), 0))]
    if row[0] * base[7] + row[1] * base[8] + row[2] < 0:
        row = [-value for value in row]
    denominator = lcm(*(value.denominator for value in row))
    integer = [int(value * denominator) for value in row]
    divisor = gcd(gcd(abs(integer[0]), abs(integer[1])), abs(integer[2]))
    return tuple(value // divisor for value in integer)


def line_intersection(left, right):
    a, b, c = left
    d, e, f = right
    determinant = a * e - b * d
    if not determinant:
        return None
    return (Fraction(b * f - c * e, determinant), Fraction(c * d - a * f, determinant))


def vertices(halfspaces):
    answer = set()
    for left, right in combinations(halfspaces, 2):
        point = line_intersection(left, right)
        if point is not None and inside(point, halfspaces):
            answer.add(point)
    return tuple(sorted(answer))


def digest_rows(rows):
    digest = hashlib.sha256()
    for row in rows:
        values = row if isinstance(row, (tuple, list)) else (row,)
        digest.update(",".join(map(str, values)).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def main():
    stored = json.loads(ARTIFACT.read_text())
    semantic = stored.pop("semantic_sha256")
    replay_semantic = hashlib.sha256(json.dumps(stored, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    stored["semantic_sha256"] = semantic
    if semantic != replay_semantic or semantic != EXPECTED_SEMANTIC_SHA256:
        raise AssertionError("projection-frontier semantic digest changed")

    base = star.normalized_parent()
    _residual, brackets = representative.polynomial_data()
    halfspaces = tuple(sorted({affine_halfspace(primitive(restrict_plane(polynomial, base)), base) for polynomial in brackets.values()}))
    if len(halfspaces) != 31 or vertices(halfspaces) != EXPECTED_VERTICES:
        raise AssertionError("parent-860 plane triangle changed")

    _occurrences, _occurrence_factor, factors = labeled.factor_polynomials()
    restrictions = set()
    classification = []
    open_factor_ids = []
    degree = Counter()
    bidegrees = Counter()
    excluded_sign = Counter()
    for factor, polynomial in enumerate(factors):
        restricted = primitive(restrict_plane(polynomial, base))
        if total_degree(restricted) == 0:
            classification.append("constant")
            continue
        if total_degree(restricted) > 2:
            raise AssertionError("plane restriction degree grew")
        if total_degree(restricted) == 2 and not conic_determinant(restricted):
            raise AssertionError("plane conic became reducible")
        if restricted in restrictions:
            raise AssertionError("distinct global factors collapsed on the plane")
        restrictions.add(restricted)
        degree[total_degree(restricted)] += 1
        bidegrees[bidegree(restricted)] += 1
        minimum, maximum = exact_range(restricted, EXPECTED_VERTICES, halfspaces)
        if minimum < 0 < maximum:
            classification.append("interior")
            open_factor_ids.append(factor)
        elif minimum <= 0 <= maximum:
            classification.append("boundary_only")
        else:
            classification.append("excluded")
            excluded_sign[1 if minimum > 0 else -1] += 1

    projection = stored["plane_projection"]
    if len(restrictions) != projection["distinct_irreducible_restrictions"]:
        raise AssertionError("distinct plane restriction count changed")
    if dict(sorted((str(key), value) for key, value in degree.items())) != projection["degree_census"]:
        raise AssertionError("plane degree census changed")
    if Counter(classification) != Counter({"constant": 1990, "interior": 1553, "boundary_only": 192, "excluded": 23005}):
        raise AssertionError("plane factor classification changed")
    if {str(key): value for key, value in sorted(excluded_sign.items())} != projection["exact_constant_sign_exclusions"]:
        raise AssertionError("constant-sign exclusion census changed")
    if digest_rows(enumerate(classification)) != projection["classification_sha256"]:
        raise AssertionError("factor-classification digest changed")
    if digest_rows((factor,) for factor in open_factor_ids) != projection["open_factor_ids_sha256"]:
        raise AssertionError("open-factor digest changed")

    # Hostile in-memory mutations must be rejected by the same trust checks.
    hostile = dict(stored)
    hostile["plane_projection"] = dict(stored["plane_projection"])
    hostile["plane_projection"]["open_triangle_factors"] += 1
    hostile_digest = hashlib.sha256(json.dumps({key: value for key, value in hostile.items() if key != "semantic_sha256"}, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if hostile_digest == semantic:
        raise AssertionError("hostile summary mutation was not rejected")
    corrupted = list(classification)
    corrupted[open_factor_ids[0]] = "excluded"
    if digest_rows(enumerate(corrupted)) == projection["classification_sha256"]:
        raise AssertionError("hostile factor-class mutation was not rejected")

    frontier = stored["resultant_frontier"]
    if frontier["distinct_primitive_resultants"] != 396_369 or frontier["total_open_horizontal_roots_by_polynomial"] != 402_031:
        raise AssertionError("resultant frontier accounting changed")
    if stored["scope"]["coverage_certified_atlas"] is not False or stored["scope"]["honest_9dvl_score"] != "2/9":
        raise AssertionError("frontier scope was promoted")

    print("PASS independent reconstruction of 31-halfspace parent triangle")
    print("PASS 26,740 restrictions -> 1,990 constants + 24,750 distinct irreducible lines/conics")
    print("PASS exact triangle range classification: 1,553 interior + 192 boundary-only + 23,005 excluded")
    print("PASS hash-pinned Bernstein/resultant frontier and two hostile mutations")
    print("SCOPE projection frontier only; score remains 2/9")


if __name__ == "__main__":
    main()
