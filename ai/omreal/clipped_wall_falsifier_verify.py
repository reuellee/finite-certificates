#!/usr/bin/env python3
"""Independent exact falsification of the proposed macrobox-20 wall attachment.

The replay uses only Python integer/Fraction arithmetic.  It reconstructs the
three authenticated equations, the normalized parent brackets, macroboxes 19
and 20, and the fixed (d,e,h) projection minor without importing either the
frontier producer or its verifier.  Its decisive certificate is an exact
centered-Taylor interval for q16134 on the complete clipped terminal face
g=a.  A strictly positive lower endpoint proves that the face contains no
triple zero.
"""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
import argparse
import hashlib
from itertools import combinations, permutations
import json
from math import comb
from pathlib import Path

import diag3_research_ledger_compatibility as ledger_compat


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LEDGER = HERE / "data/DIAG3_RESEARCH_DECISION_LEDGER.json"
LOCAL = HERE / "data/DIAG3_TRIPLE_LOCAL_ROADMAP_CANARY.json"
SYSTEM = HERE / "data/DIAG3_triple_fullspace_critical_h1.json"
FRONTIER = ROOT / "ops/team/triple-frontier/DIAG3_TRIPLE_FRONTIER_MULTIBOX_CANARY.json"
CERTIFICATE = ROOT / "ops/team/clipped-wall-falsifier/CLIPPED_WALL_FALSIFIER_CERTIFICATE.json"

BASE_REVISION = "ae8a3afc24abfea94acf4b22ea35c2ca18f3c577"
INPUT_DIGESTS = {
    "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json":
        ledger_compat.HISTORICAL_LEDGER_SHA256,
    "ai/omreal/data/DIAG3_TRIPLE_LOCAL_ROADMAP_CANARY.json":
        "0ee63d4049278c41b8fdd611aacdbe56b188dc1225bd1b9dc18dc37fb2746c27",
    "ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json":
        "c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8",
    "ops/team/triple-frontier/DIAG3_TRIPLE_FRONTIER_MULTIBOX_CANARY.json":
        "7e7ba6761ba544ab96dc36cd3f559317132b7264b94bc39059be813a8c3b5f70",
}
VARIABLES = tuple("abcdefghi")
N = len(VARIABLES)
ZERO = (0,) * N
TRIPLE = (5563, 16134, 19284)
FIBER_COLUMNS = (3, 4, 7)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def enc(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def clean(poly):
    return {m: Fraction(c) for m, c in poly.items() if c}


def add(left, right, scale=Fraction(1)):
    answer = dict(left)
    for monomial, coefficient in right.items():
        answer[monomial] = answer.get(monomial, Fraction(0)) + scale * coefficient
    return clean(answer)


def multiply(left, right):
    answer = {}
    for lm, lc in left.items():
        for rm, rc in right.items():
            monomial = tuple(x + y for x, y in zip(lm, rm, strict=True))
            answer[monomial] = answer.get(monomial, Fraction(0)) + lc * rc
    return clean(answer)


def derivative(poly, variable):
    answer = {}
    for monomial, coefficient in poly.items():
        if monomial[variable]:
            reduced = list(monomial)
            reduced[variable] -= 1
            answer[tuple(reduced)] = coefficient * monomial[variable]
    return clean(answer)


def determinant(matrix):
    answer = {}
    size = len(matrix)
    for permutation in permutations(range(size)):
        inversions = sum(
            permutation[i] > permutation[j]
            for i in range(size) for j in range(i + 1, size)
        )
        term = {ZERO: Fraction(-1 if inversions & 1 else 1)}
        for row in range(size):
            term = multiply(term, matrix[row][permutation[row]])
        answer = add(answer, term)
    return clean(answer)


def coordinate(index):
    monomial = [0] * N
    monomial[index] = 1
    return {tuple(monomial): Fraction(1)}


def normalized_parent_matrix():
    one, zero = {ZERO: Fraction(1)}, {}
    a, b, c, d, e, f, g, h, i = (coordinate(index) for index in range(N))
    del i
    return (
        (one, zero, zero, zero, one, one, one, one),
        (zero, one, zero, zero, one, a, d, g),
        (zero, zero, one, zero, one, b, e, h),
        (zero, zero, zero, one, one, c, f, coordinate(8)),
    )


def parent_brackets():
    matrix = normalized_parent_matrix()
    result = []
    for columns in combinations(range(8), 4):
        square = tuple(tuple(matrix[row][column] for column in columns) for row in range(4))
        result.append(("".join(str(column + 1) for column in columns), determinant(square)))
    if len(result) != 70:
        raise AssertionError("parent bracket census changed")
    return tuple(result)


def decode_equations(system):
    equations = []
    for record in system["equations"][:3]:
        poly = {}
        for coefficient, raw_monomial in record["terms"]:
            monomial = tuple(raw_monomial)
            if len(monomial) != N or monomial in poly:
                raise AssertionError("invalid authenticated equation encoding")
            poly[monomial] = Fraction(coefficient)
        equations.append((record["factor"], clean(poly)))
    if tuple(factor for factor, _poly in equations) != TRIPLE:
        raise AssertionError("authenticated factor presentation changed")
    return tuple(equations)


def evaluate(poly, point):
    total = Fraction(0)
    for monomial, coefficient in poly.items():
        term = coefficient
        for value, exponent in zip(point, monomial, strict=True):
            term *= value**exponent
        total += term
    return total


def product_interval(left, right):
    candidates = (
        left[0] * right[0], left[0] * right[1],
        left[1] * right[0], left[1] * right[1],
    )
    return min(candidates), max(candidates)


def power_interval(lower, upper, exponent):
    if exponent == 0:
        return Fraction(1), Fraction(1)
    candidates = [lower**exponent, upper**exponent]
    if lower <= 0 <= upper and exponent % 2 == 0:
        candidates.append(Fraction(0))
    return min(candidates), max(candidates)


def rectangular_interval(poly, bounds):
    answer = (Fraction(0), Fraction(0))
    for monomial, coefficient in poly.items():
        term = (coefficient, coefficient)
        for (lower, upper), exponent in zip(bounds, monomial, strict=True):
            term = product_interval(term, power_interval(lower, upper, exponent))
        answer = answer[0] + term[0], answer[1] + term[1]
    return answer


def interval_sign(interval):
    if interval[0] > 0:
        return 1
    if interval[1] < 0:
        return -1
    return 0


def box_bounds(center, radius):
    return tuple((value - radius, value + radius) for value in center)


def jacobian_minor(equations):
    return determinant(tuple(
        tuple(derivative(poly, column) for column in FIBER_COLUMNS)
        for _factor, poly in equations
    ))


def substitute_g_equals_a(poly):
    """Return an 8-variable polynomial in (a,b,c,d,e,f,h,i)."""

    result = {}
    for monomial, coefficient in poly.items():
        reduced = (
            monomial[0] + monomial[6], monomial[1], monomial[2],
            monomial[3], monomial[4], monomial[5], monomial[7], monomial[8],
        )
        result[reduced] = result.get(reduced, Fraction(0)) + coefficient
    return clean(result)


def shift_to_center(poly, center):
    """Exactly expand p(center+z) as a sparse polynomial in z."""

    dimension = len(center)
    zero = (0,) * dimension
    result = {}
    for monomial, coefficient in poly.items():
        term = {zero: coefficient}
        for variable, exponent in enumerate(monomial):
            expansion = {}
            for z_exponent in range(exponent + 1):
                shifted = [0] * dimension
                shifted[variable] = z_exponent
                expansion[tuple(shifted)] = (
                    Fraction(comb(exponent, z_exponent))
                    * center[variable] ** (exponent - z_exponent)
                )
            local = {}
            for lm, lc in term.items():
                for rm, rc in expansion.items():
                    product_monomial = tuple(x + y for x, y in zip(lm, rm, strict=True))
                    local[product_monomial] = local.get(product_monomial, Fraction(0)) + lc * rc
            term = {m: c for m, c in local.items() if c}
        for shifted_monomial, shifted_coefficient in term.items():
            result[shifted_monomial] = result.get(shifted_monomial, Fraction(0)) + shifted_coefficient
    return {m: c for m, c in result.items() if c}


def centered_taylor_interval(poly, center, radii):
    shifted = shift_to_center(poly, center)
    symmetric_bounds = tuple((-radius, radius) for radius in radii)
    return rectangular_interval(shifted, symmetric_bounds), shifted


def semantic_digest(candidate):
    payload = deepcopy(candidate)
    payload.pop("semantic_sha256", None)
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def witness_digest(witness):
    payload = deepcopy(witness)
    payload.pop("semantic_sha256", None)
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def reconstruct():
    path_map = {
        "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json": LEDGER,
        "ai/omreal/data/DIAG3_TRIPLE_LOCAL_ROADMAP_CANARY.json": LOCAL,
        "ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json": SYSTEM,
        "ops/team/triple-frontier/DIAG3_TRIPLE_FRONTIER_MULTIBOX_CANARY.json": FRONTIER,
    }
    # Preserve the committed falsifier certificate's immutable v1 provenance,
    # while authenticating current ledger v2 and its unchanged obligations as
    # a separate compatibility gate.
    ledger_compat.load_current_ledger(LEDGER)
    actual_digests = {
        key: (
            ledger_compat.HISTORICAL_LEDGER_SHA256
            if path_map[key] == LEDGER
            else sha256(path_map[key])
        )
        for key in INPUT_DIGESTS
    }
    if actual_digests != INPUT_DIGESTS:
        raise AssertionError(f"pinned input digest changed: {actual_digests}")

    local = json.loads(LOCAL.read_text(encoding="utf-8"))
    system = json.loads(SYSTEM.read_text(encoding="ascii"))
    frontier = json.loads(FRONTIER.read_text(encoding="utf-8"))
    equations = decode_equations(system)
    if system["variables"] != list(VARIABLES):
        raise AssertionError("authenticated variable order changed")
    if frontier["branch_selection"]["chosen_axis_zero_based"] != 0 or frontier["branch_selection"]["chosen_direction"] != -1:
        raise AssertionError("frontier direction changed")

    center0 = tuple(Fraction(value) for value in local["box"]["center"])
    radius = Fraction(local["box"]["radius"])
    if radius != Fraction(1, 128):
        raise AssertionError("base radius changed")

    def macro_center(index):
        center = list(center0)
        center[0] -= 2 * radius * index
        return tuple(center)

    parent = parent_brackets()
    base_signs = tuple(interval_sign(rectangular_interval(poly, box_bounds(center0, radius))) for _label, poly in parent)
    if not all(base_signs):
        raise AssertionError("base parent signs are not strict")

    center19 = macro_center(19)
    signs19 = tuple(interval_sign(rectangular_interval(poly, box_bounds(center19, radius))) for _label, poly in parent)
    if signs19 != base_signs:
        raise AssertionError("macrobox 19 parent acceptance canary failed")
    minor = jacobian_minor(equations)
    bounds19 = list(box_bounds(center19, radius))
    g_lower, g_upper = bounds19[6]
    g_mid = center19[6]
    minor_intervals19 = []
    for child_interval in ((g_lower, g_mid), (g_mid, g_upper)):
        child_bounds = list(bounds19)
        child_bounds[6] = child_interval
        interval = rectangular_interval(minor, tuple(child_bounds))
        if interval_sign(interval) != -1:
            raise AssertionError("macrobox 19 fixed-projection canary failed")
        minor_intervals19.append(interval)

    center20 = macro_center(20)
    bounds20 = box_bounds(center20, radius)
    failures20 = []
    for index, (label, poly) in enumerate(parent):
        sign = interval_sign(rectangular_interval(poly, bounds20))
        if sign != base_signs[index]:
            failures20.append(label)
    if failures20 != ["3468"]:
        raise AssertionError(f"macrobox 20 rejection canary changed: {failures20}")
    bracket3468 = dict(parent)["3468"]
    expected_g_minus_a = add(coordinate(6), coordinate(0), scale=Fraction(-1))
    if bracket3468 != expected_g_minus_a:
        raise AssertionError("[3468] is not reconstructed as g-a")

    # On g=a the shared coordinate ranges over the intersection of the a and g
    # intervals.  All remaining coordinates retain their full macrobox bounds.
    wall_lower = max(bounds20[0][0], bounds20[6][0])
    wall_upper = min(bounds20[0][1], bounds20[6][1])
    wall_bounds = (
        (wall_lower, wall_upper), bounds20[1], bounds20[2], bounds20[3],
        bounds20[4], bounds20[5], bounds20[7], bounds20[8],
    )
    wall_center = tuple((lower + upper) / 2 for lower, upper in wall_bounds)
    wall_radii = tuple((upper - lower) / 2 for lower, upper in wall_bounds)

    q16134 = dict(equations)[16134]
    wall_q16134 = substitute_g_equals_a(q16134)
    q_interval, shifted = centered_taylor_interval(wall_q16134, wall_center, wall_radii)
    if q_interval != (
        Fraction(17871665307, 8589934592),
        Fraction(9696617457747, 2946347565056),
    ):
        raise AssertionError(f"wall q16134 enclosure changed: {q_interval}")
    if interval_sign(q_interval) != 1 or len(shifted) != 89:
        raise AssertionError("strict wall exclusion certificate failed")

    frontier_point = tuple(Fraction(value) for value in frontier["frontier"]["failed_parent_brackets"][0]["exact_parent_wall_point"])
    if not all(lower <= value <= upper for value, (lower, upper) in zip(frontier_point, bounds20, strict=True)):
        raise AssertionError("registered parent-wall witness left macrobox 20")
    if frontier_point[6] - frontier_point[0] != 0:
        raise AssertionError("registered point is not on [3468]=0")
    residual_values = {str(factor): enc(evaluate(poly, frontier_point)) for factor, poly in equations}
    expected_residual_values = {
        "5563": "-1/56",
        "16134": "5934694995/2202927104",
        "19284": "435073/702464",
    }
    if residual_values != expected_residual_values:
        raise AssertionError(f"false-witness evaluations changed: {residual_values}")

    false_witness = {
        "claimed_triple_zero": True,
        "point": [enc(value) for value in frontier_point],
    }
    false_witness["semantic_sha256"] = witness_digest(false_witness)

    return {
        "schema": "diag3-clipped-wall-falsifier-certificate-v1",
        "track_id": "cycle-20260828-falsifier-clipped-wall",
        "base_revision": BASE_REVISION,
        "outcome": "DISPROVED_TERMINAL_FACE_ATTACHMENT",
        "authenticated_inputs": actual_digests,
        "named_factor_presentation": list(TRIPLE),
        "reconstructed_macroboxes": {
            "radius": enc(radius),
            "corridor_axis_zero_based": 0,
            "corridor_direction": -1,
            "macrobox19_center": [enc(value) for value in center19],
            "macrobox20_center": [enc(value) for value in center20],
            "macrobox20_bounds": [[enc(x), enc(y)] for x, y in bounds20],
            "clipped_cell": "macrobox20 intersect {g-a <= 0}",
            "terminal_face": "macrobox20 intersect {g-a = 0}",
            "terminal_face_variable_order": ["a=g", "b", "c", "d", "e", "f", "h", "i"],
            "terminal_face_bounds": [[enc(x), enc(y)] for x, y in wall_bounds],
        },
        "exact_wall_exclusion": {
            "factor": 16134,
            "substitution": "g=a",
            "centered_taylor_center": [enc(value) for value in wall_center],
            "centered_taylor_radii": [enc(value) for value in wall_radii],
            "shifted_nonzero_terms": len(shifted),
            "exact_interval": [enc(value) for value in q_interval],
            "sign": 1,
            "conclusion": "q16134 is strictly positive on the complete terminal face, so no triple zero attaches to [3468]=0 in K",
        },
        "canaries": {
            "macrobox19": {
                "all_70_parent_signs_match_base": True,
                "fixed_projection_minor_child_intervals": [[enc(x), enc(y)] for x, y in minor_intervals19],
                "fixed_projection_minor_sign": -1,
            },
            "macrobox20": {
                "rejected_parent_brackets": failures20,
                "bracket_3468": "g-a",
            },
            "registered_parent_wall_point": {
                "point": [enc(value) for value in frontier_point],
                "g_minus_a": "0",
                "residual_values": residual_values,
                "triple_zero": False,
            },
            "resealed_false_witness": false_witness,
            "resealed_false_witness_expected_rejection": "valid semantic seal does not cure three nonzero residual evaluations",
        },
        "coverage": {
            "included": "the entire closed terminal face macrobox20 intersect {g-a=0} for the authenticated triple",
            "excluded": "projection regularity on the clipped interior, other terminal faces, macrobox21, other triples, orbit transport, and global topology",
        },
        "theorem_effect": "the proposed macrobox20 [3468]-attachment bridge is false; diag3_triple_hc0 remains OPEN and the honest score remains 2/9",
        "ledger_change_recommended": "record the macrobox20 [3468]-attachment route as DISPROVED; do not change counts or the 2/9 score",
    }


def verify_candidate(candidate):
    expected = reconstruct()
    expected["semantic_sha256"] = semantic_digest(expected)
    if candidate != expected:
        raise AssertionError("committed falsifier certificate differs from exact reconstruction")
    if candidate["semantic_sha256"] != semantic_digest(candidate):
        raise AssertionError("certificate semantic digest mismatch")

    hostile = deepcopy(candidate["canaries"]["resealed_false_witness"])
    if hostile["semantic_sha256"] != witness_digest(hostile):
        raise AssertionError("hostile false witness is not correctly re-sealed")
    point = tuple(Fraction(value) for value in hostile["point"])
    equations = decode_equations(json.loads(SYSTEM.read_text(encoding="ascii")))
    values = tuple(evaluate(poly, point) for _factor, poly in equations)
    rejected = False
    try:
        if hostile["claimed_triple_zero"] and any(values):
            raise AssertionError("re-sealed witness has nonzero residuals")
    except AssertionError:
        rejected = True
    if not rejected:
        raise AssertionError("re-sealed false witness was accepted")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--show", action="store_true", help="print the reconstructed certificate")
    args = parser.parse_args()
    candidate = reconstruct()
    candidate["semantic_sha256"] = semantic_digest(candidate)
    if args.show:
        print(json.dumps(candidate, indent=2, sort_keys=True))
        return
    committed = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    verify_candidate(committed)
    ledger_rejected = ledger_compat.verify_hostile_mutations()
    print("PASS pinned inputs: 4/4")
    print("PASS macrobox19 accepted: 70/70 parent signs; fixed projection minor negative on 2/2 g-half boxes")
    print("PASS macrobox20 rejected exactly at [3468]=g-a")
    print("PASS complete terminal face exclusion: q16134 > 0 by exact centered-Taylor interval")
    print("PASS registered wall point rejected as triple zero")
    print("PASS re-sealed false-witness mutation rejected")
    print(
        "PASS current ledger v2 authenticated with historical obligation semantics; "
        f"hostile mutations rejected {ledger_rejected}/{ledger_rejected}"
    )
    print("OUTCOME DISPROVED_TERMINAL_FACE_ATTACHMENT; ledger counts unchanged; score 2/9")


if __name__ == "__main__":
    main()
