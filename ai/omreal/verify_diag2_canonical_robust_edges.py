#!/usr/bin/env python3
"""Exact robust-edge common-shear audit for canonical residual mutations.

For each of the thirteen canonical residual incidence types, this checker
constructs a deterministic exact rational point on its primitive global
residual wall.  The construction solves the residual for the canonical
affine pivot whose coefficient is a signed product of parent brackets.  It
then verifies, over exact arithmetic, that:

* all seventy parent brackets are nonzero at the wall point;
* no primitive global residual factor other than the selected one vanishes;
* the two exact pivot perturbations preserve every parent-bracket sign and
  every other global-residual sign, while reversing the selected factor;
* both complete derived-arrangement tope tables are correct; and
* the robust masks E_left(rho) & E_right(rho), for signatures bad on both
  sides, are pairwise intersecting.

The no-argument replay audits all types in parallel.  A resource-conservative
selected replay remains available with ``--types``::

    python ai/omreal/verify_diag2_canonical_robust_edges.py --types 36

This is one generic normalized edge per canonical incidence type.  It is not
an audit of all relative-label walls, all chambers, or all parent cells.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
from fractions import Fraction
import hashlib
from itertools import combinations
from math import lcm

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled
import DIAG9_GRAPH_exact_topes as exact_topes
import DIAG9_GRAPH_global_factor_census as global_factors
import four_chart_gate as gate
import verify_diag2_escape_set_atlas178 as atlas178
import verify_diag2_escape_set_topes as escape
from DIAG2_PIVOT_ALL_COMPACT_SECOND_WALL_VERIFY import (
    column_determinant,
    standard_columns,
)


VARIABLES = "abcdefghi"
CANONICAL_KINDS = (36, 37, 38, 39, 41, 42, 44, 46, 47, 48, 49, 50, 51)

# Types 46 and 47 are distinct incidence supports for the same primitive
# localization wall.  Keeping both is essential to the promised scope.
EXPECTED_FACTOR_IDS = {
    36: 2277,
    37: 2342,
    38: 3811,
    39: 5552,
    41: 8543,
    42: 9559,
    44: 3487,
    46: 18102,
    47: 18102,
    48: 13950,
    49: 2267,
    50: 5563,
    51: 18606,
}

# (pivot variable index, coefficient as a product of parent brackets).
# Equality is up to a global sign, since the census primitive-normalizes each
# residual independently.
PIVOT_UNITS = {
    36: (0, ("1237",)),
    37: (0, ("1257",)),
    38: (0, ("1278",)),
    39: (0, ("2378",)),
    41: (0, ("2457",)),
    42: (0, ("2478",)),
    44: (3, ("2356", "1258")),
    46: (0, ("1237",)),
    47: (0, ("1237",)),
    48: (0, ()),
    49: (3, ()),
    50: (3, ("1238",)),
    51: (5, ("2468", "1456")),
}

# Each center is reconstructed, rather than stored: hash the eight nonpivot
# coordinates at this pinned attempt, then solve the residual's affine pivot
# equation exactly.  The attempts were selected by deterministic enumeration.
WITNESS_ATTEMPT = {
    36: 1,
    37: 7,
    38: 1,
    39: 1,
    41: 3,
    42: 1,
    44: 0,
    46: 2,
    47: 14,
    48: 9,
    49: 1,
    50: 5,
    51: 6,
}

# Exact perturbation 2**(-exponent).  These are deliberately well inside the
# first parent/global-factor crossing found from the deterministic centers.
PERTURBATION_EXPONENT = {
    36: 11,
    37: 13,
    38: 11,
    39: 0,
    41: 9,
    42: 0,
    44: 5,
    46: 8,
    47: 8,
    48: 4,
    49: 5,
    50: 9,
    51: 9,
}

EXPECTED_TOPES = 26_112

# Immutable semantic digests from the complete four-worker exact replay.
EXPECTED_EDGE_DIGESTS = {
    36: "2b140df44cda49fd34463e24fad724f5a5011060ab8401af1b7582bd2357b8c6",
    37: "23a9ec75cdef3c733207e084fd6913bd18b4c1b60e533b578af1dacda4b6f4c1",
    38: "92148e87c8cefde59863fa6d7b910278a3e95d3481c37f3887b2189120a1f224",
    39: "e79d1156f42a56914606907784190dab2d2ebf96c8d93a4ddee38d708f31b15e",
    41: "74e1ff86866634dc1fcf17257213e4fc0ece04ac30689a9a2f8994054d02e447",
    42: "41d8d2bb635d98595e7c140f0019e9771bb8fe6a8c02e23b5cfcca5b969c1431",
    44: "8d2cf02aa3a115d01c47cc2d0cb52d014cdbab4282e35f4d778d3908e6ad4f1b",
    46: "9bb7ddc900ac8099d83d3b69e95e2b6c2f4dc7de9c1b7bb2713e9671ef9fed41",
    47: "89e70fb8500c5fbcd25aa382c4f885d3c4d565c84f8095dc8474e549ed5e0ddf",
    48: "7707831a2bb5914efad5ad661ef56335437841f2ecc59357d016d48e2af2905c",
    49: "c24d123836af150fa196362a1e0c578b1c48a354f44ecf813933686fbf52dc44",
    50: "f8822a2931b53195956bed370718ec6f634c46b3f92297b17e154c31140cd65f",
    51: "11d16355dd2103e7bed4d1e3decdb764dc7bc930beea377666a947fc727c2cae",
}


@dataclass(frozen=True)
class WallWitness:
    kind: int
    factor_id: int
    pivot: int
    attempt: int
    epsilon: Fraction
    center: tuple[Fraction, ...]
    left: tuple[Fraction, ...]
    right: tuple[Fraction, ...]
    parent: str


@dataclass(frozen=True)
class EdgeReport:
    kind: int
    factor_id: int
    valid_extensions: int
    topes_left: int
    topes_right: int
    removed_topes: int
    added_topes: int
    bad_left: int
    bad_right: int
    common_bad: int
    minimum_robust_escape: int
    minimum_robust_overlap: int
    overlap_witness: tuple[int, int, int, int]
    digest: str


def evaluate(polynomial, values):
    """Evaluate a sparse nine-variable polynomial over QQ."""

    answer = Fraction(0)
    for monomial, coefficient in polynomial.items():
        term = Fraction(coefficient)
        for index, exponent in enumerate(monomial):
            if exponent:
                term *= values[index] ** exponent
        answer += term
    return answer


def affine_parts(polynomial, pivot):
    """Return U,V with polynomial = U*x_pivot + V."""

    coefficient = {}
    constant = {}
    for monomial, value in polynomial.items():
        exponent = monomial[pivot]
        if exponent not in (0, 1):
            raise AssertionError("canonical residual is not affine in its pivot")
        reduced = list(monomial)
        reduced[pivot] = 0
        reduced = tuple(reduced)
        target = coefficient if exponent else constant
        target[reduced] = target.get(reduced, 0) + value
        if not target[reduced]:
            del target[reduced]
    if not coefficient:
        raise AssertionError("canonical residual lost its pivot")
    return coefficient, constant


def bracket_polynomials():
    matrix = global_factors.normalized_matrix()
    return {
        "".join(str(index + 1) for index in basis):
            global_factors.square_minor(matrix, basis)
        for basis in combinations(range(8), 4)
    }


def canonical_data():
    expected_kinds = set(CANONICAL_KINDS)
    for label, table in (
        ("factor IDs", EXPECTED_FACTOR_IDS),
        ("pivot units", PIVOT_UNITS),
        ("witness attempts", WITNESS_ATTEMPT),
        ("perturbations", PERTURBATION_EXPONENT),
        ("semantic digests", EXPECTED_EDGE_DIGESTS),
    ):
        if set(table) != expected_kinds:
            raise AssertionError(f"incomplete canonical {label} table")
    occurrences, occurrence_factor, factor_polynomials = labeled.factor_polynomials()
    del occurrences
    representatives = labeled.occurrence_representatives()
    factor_ids = {
        kind: occurrence_factor[representatives[kind]] for kind in CANONICAL_KINDS
    }
    if factor_ids != EXPECTED_FACTOR_IDS:
        raise AssertionError(f"canonical factor IDs changed: {factor_ids}")
    if factor_ids[46] != factor_ids[47]:
        raise AssertionError("types 46/47 no longer share their primitive factor")
    if len(set(factor_ids.values())) != 12:
        raise AssertionError("thirteen incidence types must give twelve factors")
    return factor_ids, factor_polynomials


def candidate_coordinate(kind, attempt, variable):
    payload = f"diag2-canonical-edge-v1:{kind}:{attempt}:{variable}".encode("ascii")
    raw = int.from_bytes(hashlib.sha256(payload).digest()[:4], "big")
    value = raw % 67 - 33
    if value in (-1, 0, 1):
        value += 7
    return Fraction(value)


def sign(value):
    return (value > 0) - (value < 0)


def factor_signs_at(factor_polynomials, values, pivot):
    """Evaluate all 26,740 factors exactly with one rational coordinate.

    Clearing the pivot denominator separately in each polynomial avoids the
    much slower creation of hundreds of thousands of Fraction temporaries.
    Every nonpivot coordinate in this construction is integral.
    """

    for index, value in enumerate(values):
        if index != pivot and value.denominator != 1:
            raise AssertionError("factor evaluator expects integral nonpivots")
    numerator = values[pivot].numerator
    denominator = values[pivot].denominator
    answer = []
    for polynomial in factor_polynomials:
        pivot_degree = max(monomial[pivot] for monomial in polynomial)
        total = 0
        for monomial, coefficient in polynomial.items():
            exponent = monomial[pivot]
            term = (
                int(coefficient)
                * numerator ** exponent
                * denominator ** (pivot_degree - exponent)
            )
            for index, power in enumerate(monomial):
                if index != pivot and power:
                    term *= values[index].numerator ** power
            total += term
        answer.append(sign(total))
    return tuple(answer)


def parent_brackets(values):
    columns = standard_columns(dict(zip(VARIABLES, values, strict=True)))
    return tuple(
        column_determinant(columns, basis)
        for basis in combinations(range(8), 4)
    )


def integer_matrix(values):
    columns = []
    for column in standard_columns(dict(zip(VARIABLES, values, strict=True))):
        denominator = 1
        for value in column:
            denominator = lcm(denominator, Fraction(value).denominator)
        columns.append(tuple(int(Fraction(value) * denominator) for value in column))
    return tuple(
        tuple(columns[column][row] for column in range(8)) for row in range(4)
    )


def verify_canonical_incidence_crossing(kind, center, left, right):
    """Directly check the selected four-normal determinant at all points."""

    support = labeled.occurrence_representatives()[kind]
    determinants = []
    for values in (center, left, right):
        rows = exact_topes.derived_rows(integer_matrix(values), normalize=False)
        square = tuple(rows[index] for index in support)
        determinants.append(exact_topes.determinant(square))
    if determinants[0] != 0:
        raise AssertionError(f"type {kind}: canonical incidence misses its wall")
    if not determinants[1] or not determinants[2] or determinants[1] * determinants[2] >= 0:
        raise AssertionError(f"type {kind}: canonical incidence did not reverse sign")


def construct_witness(kind, factor_ids, factor_polynomials):
    if kind not in CANONICAL_KINDS:
        raise ValueError(f"unknown canonical residual type {kind}")
    factor_id = factor_ids[kind]
    polynomial = factor_polynomials[factor_id]
    pivot, unit_labels = PIVOT_UNITS[kind]
    coefficient, constant = affine_parts(polynomial, pivot)

    brackets = bracket_polynomials()
    claimed_unit = global_factors.product([brackets[label] for label in unit_labels])
    if global_factors.primitive(coefficient) != global_factors.primitive(claimed_unit):
        raise AssertionError(f"type {kind}: wrong bracket-unit pivot identity")

    attempt = WITNESS_ATTEMPT[kind]
    center = [candidate_coordinate(kind, attempt, index) for index in range(9)]
    center[pivot] = Fraction(0)
    coefficient_value = evaluate(coefficient, center)
    if not coefficient_value:
        raise AssertionError(f"type {kind}: pivot bracket unit vanished")
    center[pivot] = -evaluate(constant, center) / coefficient_value
    center = tuple(center)
    if evaluate(polynomial, center):
        raise AssertionError(f"type {kind}: affine solve missed the residual wall")

    center_brackets = parent_brackets(center)
    if len(center_brackets) != 70 or not all(center_brackets):
        raise AssertionError(f"type {kind}: wall center is not parent-uniform")

    center_factor_signs = factor_signs_at(factor_polynomials, center, pivot)
    center_zeros = tuple(
        index for index, factor_sign in enumerate(center_factor_signs)
        if factor_sign == 0
    )
    if center_zeros != (factor_id,):
        raise AssertionError(
            f"type {kind}: wall center has residual zeros {center_zeros}"
        )

    epsilon = Fraction(1, 1 << PERTURBATION_EXPONENT[kind])
    left = list(center)
    right = list(center)
    left[pivot] -= epsilon
    right[pivot] += epsilon
    left, right = tuple(left), tuple(right)

    left_brackets = parent_brackets(left)
    right_brackets = parent_brackets(right)
    center_bracket_signs = tuple(map(sign, center_brackets))
    if tuple(map(sign, left_brackets)) != center_bracket_signs:
        raise AssertionError(f"type {kind}: left endpoint changed parent cell")
    if tuple(map(sign, right_brackets)) != center_bracket_signs:
        raise AssertionError(f"type {kind}: right endpoint changed parent cell")

    left_factor_signs = factor_signs_at(factor_polynomials, left, pivot)
    right_factor_signs = factor_signs_at(factor_polynomials, right, pivot)
    if any(value == 0 for value in left_factor_signs + right_factor_signs):
        raise AssertionError(f"type {kind}: an endpoint lies on a residual wall")
    changed = tuple(
        index
        for index, (left_sign, right_sign) in enumerate(
            zip(left_factor_signs, right_factor_signs, strict=True)
        )
        if left_sign != right_sign
    )
    if changed != (factor_id,):
        raise AssertionError(f"type {kind}: perturbation flips factors {changed}")
    if any(
        center_factor_signs[index] != left_factor_signs[index]
        or center_factor_signs[index] != right_factor_signs[index]
        for index in range(len(factor_polynomials))
        if index != factor_id
    ):
        raise AssertionError(f"type {kind}: endpoint crossed an unselected factor")

    verify_canonical_incidence_crossing(kind, center, left, right)

    # four_chart_gate uses the repository's colex basis order, whereas the
    # seventy-bracket isolation checks above deliberately use combinations()
    # in lexicographic order.  Recover the gate string from its canonical
    # exact colex implementation instead of silently conflating the orders.
    parent_signs = exact_topes.parent_signs(integer_matrix(center))
    parent = "".join("+" if value > 0 else "-" for value in parent_signs)
    return WallWitness(
        kind=kind,
        factor_id=factor_id,
        pivot=pivot,
        attempt=attempt,
        epsilon=epsilon,
        center=center,
        left=left,
        right=right,
        parent=parent,
    )


def enumerate_tope_table(matrix, parent, label):
    expected_parent = tuple(1 if value == "+" else -1 for value in parent)
    if exact_topes.parent_signs(matrix) != expected_parent:
        raise AssertionError(f"{label}: integerization changed parent signs")
    rows = exact_topes.derived_rows(matrix)
    enumerated = exact_topes.enumerate_topes(rows, dimension=4)
    exact_topes.verify_topes(rows, enumerated)
    topes = tuple(enumerated)
    if len(topes) != EXPECTED_TOPES or len(set(topes)) != EXPECTED_TOPES:
        raise AssertionError(f"{label}: wrong complete-tope table size")
    return topes


def semantic_digest(witness, left_topes, right_topes, records, fields):
    digest = hashlib.sha256()
    digest.update(b"diag2-canonical-robust-edge-v1\0")
    digest.update(int(witness.kind).to_bytes(2, "little"))
    digest.update(int(witness.factor_id).to_bytes(4, "little"))
    digest.update(witness.parent.encode("ascii") + b"\0")
    for point in (witness.center, witness.left, witness.right):
        for value in point:
            digest.update(str(value.numerator).encode("ascii") + b"/")
            digest.update(str(value.denominator).encode("ascii") + b"\0")
    for label, topes in ((b"left\0", left_topes), (b"right\0", right_topes)):
        digest.update(label)
        for tope in sorted(map(int, topes)):
            digest.update(tope.to_bytes(8, "little"))
    digest.update(b"robust\0")
    for signature, mask in records:
        digest.update(int(signature).to_bytes(8, "little"))
        digest.update(int(mask).to_bytes(16, "little"))
    digest.update(repr(fields).encode("ascii"))
    return digest.hexdigest()


def valid_bad_partition(signatures, left_topes, right_topes, label):
    """Certify that both exact tope tables partition the GP-valid universe."""

    valid = set(map(int, signatures))
    if len(valid) != len(signatures):
        raise AssertionError(f"{label}: GP-valid signature enumeration has duplicates")
    answer = []
    for side, topes in (("left", left_topes), ("right", right_topes)):
        invalid_topes = set(topes) - valid
        if invalid_topes:
            witness = min(invalid_topes)
            raise AssertionError(
                f"{label}-{side}: complete tope {witness} is not GP-valid"
            )
        bad = valid - set(topes)
        if len(bad) + len(topes) != len(valid):
            raise AssertionError(
                f"{label}-{side}: bad and tope sets do not partition GP-valid signatures"
            )
        answer.append(bad)
    return tuple(answer)


def invalid_tope_canary():
    """Ensure the partition check rejects a tope outside the valid universe."""

    try:
        valid_bad_partition((1, 2, 3), {1, 4}, {2, 3}, "invalid-tope-canary")
    except AssertionError as error:
        if "not GP-valid" not in str(error):
            raise
    else:
        raise AssertionError("invalid-tope canary was accepted")


def audit_kind(kind):
    factor_ids, factor_polynomials = canonical_data()
    witness = construct_witness(kind, factor_ids, factor_polynomials)
    left_topes = enumerate_tope_table(
        integer_matrix(witness.left), witness.parent, f"type-{kind}-left"
    )
    right_topes = enumerate_tope_table(
        integer_matrix(witness.right), witness.parent, f"type-{kind}-right"
    )
    left_set, right_set = set(left_topes), set(right_topes)

    _, signatures = gate.enumerate_extensions(witness.parent)
    signatures = tuple(map(int, signatures))
    left_bad, right_bad = valid_bad_partition(
        signatures, left_set, right_set, f"type-{kind}"
    )
    common_bad = tuple(sorted(left_bad & right_bad))
    if len(common_bad) < 2:
        raise AssertionError(f"type {kind}: fewer than two common-bad signatures")

    left_prepared = escape.prepare_directions(left_set)
    right_prepared = escape.prepare_directions(right_set)
    records = []
    for signature in common_bad:
        robust = (
            escape.escape_mask(signature, left_prepared)
            & escape.escape_mask(signature, right_prepared)
        )
        records.append((signature, robust))
    if any(mask == 0 for _, mask in records):
        raise AssertionError(f"type {kind}: an edge-robust escape mask is empty")
    disjoint = escape.prove_pairwise_intersection(records)
    if disjoint is not None:
        raise AssertionError(
            f"type {kind}: disjoint edge-robust masks at signatures {disjoint}"
        )
    minimum_escape = min(mask.bit_count() for _, mask in records)
    minimum_overlap, overlap_witness = atlas178.minimum_pair_overlap(records)

    fields = (
        len(signatures),
        len(left_topes),
        len(right_topes),
        len(left_set - right_set),
        len(right_set - left_set),
        len(left_bad),
        len(right_bad),
        len(common_bad),
        minimum_escape,
        minimum_overlap,
        overlap_witness,
    )
    digest = semantic_digest(
        witness, left_topes, right_topes, tuple(records), fields
    )
    expected_digest = EXPECTED_EDGE_DIGESTS.get(kind)
    if expected_digest is not None and digest != expected_digest:
        raise AssertionError(
            f"type {kind}: robust-edge semantic digest changed: {digest}"
        )
    return witness, EdgeReport(
        kind=kind,
        factor_id=witness.factor_id,
        valid_extensions=len(signatures),
        topes_left=len(left_topes),
        topes_right=len(right_topes),
        removed_topes=len(left_set - right_set),
        added_topes=len(right_set - left_set),
        bad_left=len(left_bad),
        bad_right=len(right_bad),
        common_bad=len(common_bad),
        minimum_robust_escape=minimum_escape,
        minimum_robust_overlap=minimum_overlap,
        overlap_witness=overlap_witness,
        digest=digest,
    )


def witness_only(kind):
    factor_ids, factor_polynomials = canonical_data()
    return construct_witness(kind, factor_ids, factor_polynomials)


def fraction_text(value):
    return str(value.numerator) if value.denominator == 1 else str(value)


def print_witness(witness):
    center = ",".join(
        f"{name}={fraction_text(value)}"
        for name, value in zip(VARIABLES, witness.center, strict=True)
    )
    print(
        f"PASS type {witness.kind} factor {witness.factor_id}: "
        f"unique exact wall zero; pivot {VARIABLES[witness.pivot]}; "
        f"epsilon {witness.epsilon}",
        flush=True,
    )
    print(f"CENTER type {witness.kind} {center}", flush=True)


def print_report(report):
    decorations = report.common_bad * (report.common_bad - 1) // 2
    print(
        f"THEOREM type {report.kind}: {report.common_bad} common-bad signatures, "
        f"{decorations} pairs, all edge-robust masks intersect",
        flush=True,
    )
    print(
        f"PASS type {report.kind}: valid={report.valid_extensions} "
        f"topes={report.topes_left}/{report.topes_right} "
        f"exchange={report.removed_topes}/{report.added_topes} "
        f"bad={report.bad_left}/{report.bad_right} "
        f"min-robust={report.minimum_robust_escape} "
        f"min-overlap={report.minimum_robust_overlap}",
        flush=True,
    )
    print(f"SEMANTIC type-{report.kind} {report.digest}", flush=True)


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    selection = parser.add_mutually_exclusive_group()
    selection.add_argument(
        "--all",
        action="store_true",
        help="audit all thirteen canonical incidence types",
    )
    selection.add_argument(
        "--types",
        type=int,
        nargs="+",
        help="audit only these canonical types (default: all thirteen)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=4,
        help="parallel type workers (default: 4)",
    )
    parser.add_argument(
        "--witnesses-only",
        action="store_true",
        help="verify exact wall points and perturbations without tope audits",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    invalid_tope_canary()
    if args.workers < 1:
        raise ValueError("--workers must be positive")
    kinds = CANONICAL_KINDS if args.all or args.types is None else tuple(args.types)
    if len(set(kinds)) != len(kinds) or any(kind not in CANONICAL_KINDS for kind in kinds):
        raise ValueError(f"types must be distinct members of {CANONICAL_KINDS}")

    worker = witness_only if args.witnesses_only else audit_kind
    results = []
    if args.workers == 1 or len(kinds) == 1:
        for kind in kinds:
            results.append(worker(kind))
    else:
        with ProcessPoolExecutor(max_workers=min(args.workers, len(kinds))) as executor:
            futures = {executor.submit(worker, kind): kind for kind in kinds}
            for future in as_completed(futures):
                result = future.result()
                results.append(result)
                witness = result if args.witnesses_only else result[0]
                print_witness(witness)

    def result_kind(result):
        witness = result if args.witnesses_only else result[0]
        return witness.kind

    for result in sorted(results, key=result_kind):
        witness = result if args.witnesses_only else result[0]
        if args.workers == 1 or len(kinds) == 1:
            print_witness(witness)
        if not args.witnesses_only:
            print_report(result[1])

    if args.witnesses_only:
        print(
            f"THEOREM {len(kinds)} exact generic wall witnesses have one primitive "
            "residual zero and isolated two-sided perturbations"
        )
    else:
        print(
            f"THEOREM {len(kinds)} canonical robust edges passed the exact "
            "pairwise common-shear test"
        )
    print(
        "SCOPE canonical incidence types at one generic normalized edge each; "
        "no relative-label, chamber, or parent-cell coverage"
    )


if __name__ == "__main__":
    main()
