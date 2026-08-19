#!/usr/bin/env python3
"""Bounded Macaulay screens for diagonal-three height certificates.

For a residual triple q=(q0,q1,q2) and a coordinate height x_h, let M_J be
the 56 three-by-three Jacobian minors using variables other than x_h.  This
program tests, in the total-degree-D Macaulay piece, membership of short
parent-bracket products in

                 <q0,q1,q2, M_J : J subset {0,...,8}-{h}>.

The default profile uses every coordinate height and both F_2 and F_3.  Its
per-canary degree is the least of 9, 10, or 11 which both contains every
nonzero height minor and contains all parent products of length at most three.

A modular hit is only a candidate and needs exact rational replay.  A modular
miss is not a characteristic-zero no-go: the chosen prime can be exceptional.
The separately reported monomial-support rejections are exact at the stated
degree.  No result from this file is a full 1,819,789-row residue scan.
"""

from __future__ import annotations

import argparse
from collections import Counter
import gc
import hashlib
from itertools import combinations, combinations_with_replacement
import json
from pathlib import Path
import struct
import sys
import time


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY as triples  # noqa: E402
import verify_diag3_projective_column_fiber_scan as column_scan  # noqa: E402
import verify_residual_log_binomials as poly  # noqa: E402


ZERO = (0,) * 9
HARD = (
    (2_277, 390, 22_507),
    (5_563, 16_134, 19_284),
    (12_985, 16_183, 7_196),
    (20_355, 5_442, 5_949),
    (9_667, 16_486, 26_315),
    (9_758, 24_338, 15_810),
)

# Degree nine contains every length-at-most-three target.  Canaries 3 and 4
# need degrees ten and eleven respectively before all height minors occur.
DEFAULT_DEGREES = (9, 9, 9, 10, 11, 9)
DEFAULT_PRIMES = (2, 3)
EXPECTED_PARENT_FACTORS = 62
EXPECTED_TARGETS = 43_680

MORSE = HERE / "data/DIAG3_morse_unit_minor_certificates.bin"
SHEAR = HERE / "data/DIAG3_frame1119_constant_shear.json"
POST_TRIANGULAR_COUNT = 1_885_400
POST_TRIANGULAR_SHA256 = (
    "1c64017faad2173a3552dd70427d893c6ad4e39f31075ef9941c871f11184949"
)
FINAL_RESIDUE_COUNT = 1_819_789
FINAL_KIND_COUNTS = {
    (36, 49, 50): 1_342,
    (36, 49, 51): 748,
    (36, 50, 50): 1_820,
    (36, 50, 51): 1_851,
    (36, 51, 51): 443,
    (38, 50, 50): 2_473,
    (38, 50, 51): 2_731,
    (38, 51, 51): 750,
    (48, 48, 50): 85,
    (48, 48, 51): 70,
    (48, 49, 49): 1_760,
    (48, 49, 50): 5_086,
    (48, 49, 51): 2_838,
    (48, 50, 50): 3_685,
    (48, 50, 51): 4_224,
    (48, 51, 51): 1_463,
    (49, 49, 49): 33_525,
    (49, 49, 50): 147_535,
    (49, 49, 51): 85_032,
    (49, 50, 50): 271_709,
    (49, 50, 51): 309_380,
    (49, 51, 51): 86_593,
    (50, 50, 50): 233_155,
    (50, 50, 51): 387_200,
    (50, 51, 51): 200_916,
    (51, 51, 51): 33_375,
}

# Filled after the complete default profile is run.  A nonempty value makes
# the default invocation a pinned semantic regression, while custom profiles
# remain exploratory.
EXPECTED_DEFAULT_SEMANTIC_SHA256 = (
    "d8e9ad3900d3846ade58ca2fc23feccce1f158e27a46cb334b416fc9420dd38a"
)


def polynomial_degree(polynomial, prime=None):
    """Total degree, optionally after coefficient reduction modulo prime."""

    return max(
        (
            sum(exponent)
            for exponent, coefficient in polynomial.items()
            if prime is None or int(coefficient) % prime
        ),
        default=-1,
    )


def monomial_tables(maximum_degree):
    exact = [[] for _ in range(maximum_degree + 1)]
    exact[0].append(ZERO)
    for degree in range(1, maximum_degree + 1):
        for chosen in combinations_with_replacement(range(9), degree):
            exponent = [0] * 9
            for variable in chosen:
                exponent[variable] += 1
            exact[degree].append(tuple(exponent))
    cumulative = []
    running = []
    for rows in exact:
        running.extend(rows)
        cumulative.append(tuple(running))
    all_monomials = cumulative[-1]
    return all_monomials, tuple(cumulative), {
        monomial: index for index, monomial in enumerate(all_monomials)
    }


def shifted_exponent(exponent, shift):
    return tuple(left + right for left, right in zip(exponent, shift))


def support_vector(polynomial, shift, monomial_index):
    answer = 0
    for exponent, coefficient in polynomial.items():
        if coefficient:
            answer |= 1 << monomial_index[shifted_exponent(exponent, shift)]
    return answer


def f2_vector(polynomial, shift, monomial_index):
    answer = 0
    for exponent, coefficient in polynomial.items():
        if int(coefficient) & 1:
            answer ^= 1 << monomial_index[shifted_exponent(exponent, shift)]
    return answer


def f2_insert(basis, vector):
    while vector:
        pivot = vector.bit_length() - 1
        row = basis.get(pivot)
        if row is None:
            basis[pivot] = vector
            return True
        vector ^= row
    return False


def f2_member(basis, vector):
    while vector:
        pivot = vector.bit_length() - 1
        row = basis.get(pivot)
        if row is None:
            return False
        vector ^= row
    return True


def f3_add(left, right):
    """Add two bit-sliced vectors over F_3.

    Each pair contains the bit positions with coefficients 1 and 2.  The two
    planes in a valid vector are disjoint.
    """

    left_one, left_two = left
    right_one, right_two = right
    left_used = left_one | left_two
    right_used = right_one | right_two
    one = (
        (right_one & ~left_used)
        | (left_one & ~right_used)
        | (left_two & right_two)
    )
    two = (
        (right_two & ~left_used)
        | (left_two & ~right_used)
        | (left_one & right_one)
    )
    return one, two


def f3_vector(polynomial, shift, monomial_index):
    one = 0
    two = 0
    for exponent, coefficient in polynomial.items():
        residue = int(coefficient) % 3
        if not residue:
            continue
        bit = 1 << monomial_index[shifted_exponent(exponent, shift)]
        if residue == 1:
            one |= bit
        else:
            two |= bit
    return one, two


def f3_insert(basis, vector):
    while vector[0] | vector[1]:
        pivot = (vector[0] | vector[1]).bit_length() - 1
        row = basis.get(pivot)
        if row is None:
            if vector[1] >> pivot & 1:
                vector = vector[1], vector[0]
            basis[pivot] = vector
            return True
        # Stored rows have pivot coefficient one.  Eliminate coefficient one
        # by adding -row, and coefficient two by adding row.
        if vector[0] >> pivot & 1:
            vector = f3_add(vector, (row[1], row[0]))
        else:
            vector = f3_add(vector, row)
    return False


def f3_member(basis, vector):
    while vector[0] | vector[1]:
        pivot = (vector[0] | vector[1]).bit_length() - 1
        row = basis.get(pivot)
        if row is None:
            return False
        if vector[0] >> pivot & 1:
            vector = f3_add(vector, (row[1], row[0]))
        else:
            vector = f3_add(vector, row)
    return True


def backend(prime):
    if prime == 2:
        return f2_vector, f2_insert, f2_member, lambda vector: not vector
    if prime == 3:
        return (
            f3_vector,
            f3_insert,
            f3_member,
            lambda vector: not (vector[0] | vector[1]),
        )
    raise ValueError("the bit-sliced verifier supports only primes 2 and 3")


def target_products(parent_records, maximum_factors, degree_bound):
    factors = tuple(record[1] for record in parent_records)
    yield (), {ZERO: 1}

    def recurse(polynomial, indices, start, remaining):
        if not remaining:
            yield indices, polynomial
            return
        for index in range(start, len(factors)):
            product = poly.multiply(polynomial, factors[index])
            if polynomial_degree(product) <= degree_bound:
                yield from recurse(
                    product, indices + (index,), index, remaining - 1
                )

    for length in range(1, maximum_factors + 1):
        yield from recurse({ZERO: 1}, (), 0, length)


def self_test_f3():
    """Cross-check bit-sliced F_3 elimination against dense arithmetic."""

    vectors = (
        (1, 0, 2, 1, 0, 0, 2),
        (0, 1, 1, 2, 0, 1, 0),
        (2, 1, 0, 0, 1, 2, 1),
        (1, 1, 0, 0, 1, 2, 0),
        (0, 0, 1, 1, 2, 0, 2),
    )

    def packed(row):
        one = sum(1 << index for index, value in enumerate(row) if value == 1)
        two = sum(1 << index for index, value in enumerate(row) if value == 2)
        return one, two

    def dense_rank(rows):
        matrix = [list(row) for row in rows]
        rank = 0
        for column in reversed(range(7)):
            pivot = next(
                (index for index in range(rank, len(matrix)) if matrix[index][column]),
                None,
            )
            if pivot is None:
                continue
            matrix[rank], matrix[pivot] = matrix[pivot], matrix[rank]
            inverse = 1 if matrix[rank][column] == 1 else 2
            matrix[rank] = [(inverse * value) % 3 for value in matrix[rank]]
            for index in range(len(matrix)):
                if index == rank or not matrix[index][column]:
                    continue
                scalar = matrix[index][column]
                matrix[index] = [
                    (left - scalar * right) % 3
                    for left, right in zip(matrix[index], matrix[rank])
                ]
            rank += 1
        return rank

    for prefix in range(len(vectors) + 1):
        basis = {}
        for row in vectors[:prefix]:
            f3_insert(basis, packed(row))
        if len(basis) != dense_rank(vectors[:prefix]):
            raise AssertionError("F3 bit-sliced rank self-test failed")
        for candidate in vectors:
            expected = dense_rank(vectors[:prefix] + (candidate,)) == len(basis)
            if f3_member(basis, packed(candidate)) != expected:
                raise AssertionError("F3 bit-sliced membership self-test failed")


def height_generators(residual, omitted):
    variables = tuple(variable for variable in range(9) if variable != omitted)
    minors = tuple(
        triples.jacobian_minor(residual, (0, 1, 2), chosen)
        for chosen in combinations(variables, 3)
    )
    return tuple(residual.values()), minors


def screen_height(
    residual,
    omitted,
    degree,
    prime,
    targets,
    parent_labels,
    cumulative_monomials,
    monomial_index,
):
    vectorize, insert, member, is_zero = backend(prime)
    q_generators, minors = height_generators(residual, omitted)
    generators = q_generators + tuple(minor for minor in minors if minor)
    exact_support = 0
    row_counts = Counter()
    included_degrees = Counter()
    omitted_degrees = Counter()

    # The support layer is over Z.  Its rejection is therefore exact and is
    # independent of the modular coefficient cancellations below.
    for generator_index, generator in enumerate(generators):
        degree_over_z = polynomial_degree(generator)
        kind = "q" if generator_index < 3 else "minor"
        if degree_over_z > degree:
            omitted_degrees[(kind, degree_over_z)] += 1
            continue
        included_degrees[(kind, degree_over_z)] += 1
        for shift in cumulative_monomials[degree - degree_over_z]:
            exact_support |= support_vector(generator, shift, monomial_index)

    basis = {}
    for generator_index, generator in enumerate(generators):
        degree_mod_prime = polynomial_degree(generator, prime)
        kind = "q" if generator_index < 3 else "minor"
        if degree_mod_prime < 0 or degree_mod_prime > degree:
            continue
        for shift in cumulative_monomials[degree - degree_mod_prime]:
            row_counts[kind] += 1
            insert(basis, vectorize(generator, shift, monomial_index))

    exact_support_rejections = 0
    modular_tests = 0
    modular_zero_targets = 0
    hits = []
    target_counts = Counter()
    for indices, target in targets:
        target_counts[len(indices)] += 1
        target_support = support_vector(target, ZERO, monomial_index)
        if target_support & ~exact_support:
            exact_support_rejections += 1
            continue
        modular_tests += 1
        vector = vectorize(target, ZERO, monomial_index)
        if is_zero(vector):
            modular_zero_targets += 1
            continue
        if member(basis, vector):
            hits.append(
                "1" if not indices else "*".join(
                    parent_labels[index] for index in indices
                )
            )

    minor_degrees = Counter(
        polynomial_degree(minor) for minor in minors if minor
    )
    return {
        "height": omitted,
        "prime": prime,
        "rank": len(basis),
        "rows_q": row_counts["q"],
        "rows_minor": row_counts["minor"],
        "nonzero_minors": sum(minor_degrees.values()),
        "minor_degrees": tuple(sorted(minor_degrees.items())),
        "included": tuple(sorted(included_degrees.items())),
        "omitted": tuple(sorted(omitted_degrees.items())),
        "target_counts": tuple(sorted(target_counts.items())),
        "support_reject": exact_support_rejections,
        "modular_tests": modular_tests,
        "modular_zero": modular_zero_targets,
        "hits": tuple(hits),
    }


def run_screen(canaries, degree_override, heights, primes, maximum_factors):
    self_test_f3()
    _occurrences, _occurrence_factor, factor_polynomials = (
        labeled.factor_polynomials()
    )
    parent_records = labeled.parent_bracket_factors()
    if len(parent_records) != EXPECTED_PARENT_FACTORS:
        raise AssertionError("parent-factor count changed")
    parent_labels = tuple(record[0] for record in parent_records)
    reports = []

    for canary in canaries:
        degree = degree_override if degree_override is not None else DEFAULT_DEGREES[canary]
        all_monomials, cumulative, monomial_index = monomial_tables(degree)
        targets = tuple(target_products(parent_records, maximum_factors, degree))
        if maximum_factors == 3 and degree >= 9 and len(targets) != EXPECTED_TARGETS:
            raise AssertionError("length-three target count changed")
        factors = HARD[canary]
        residual = {
            row: factor_polynomials[factor] for row, factor in enumerate(factors)
        }
        print(
            "CANARY", canary, factors, "degree", degree,
            "monomials", len(all_monomials), "targets", len(targets),
            flush=True,
        )
        for omitted in heights:
            for prime in primes:
                started = time.monotonic()
                report = screen_height(
                    residual,
                    omitted,
                    degree,
                    prime,
                    targets,
                    parent_labels,
                    cumulative,
                    monomial_index,
                )
                report["canary"] = canary
                report["degree"] = degree
                reports.append(report)
                print(
                    "HEIGHT", omitted, "p", prime,
                    "minor_degrees", dict(report["minor_degrees"]),
                    "omitted", dict(report["omitted"]),
                    "rows", {"q": report["rows_q"], "minor": report["rows_minor"]},
                    "rank", report["rank"],
                    "support_reject", report["support_reject"],
                    "modular_tests", report["modular_tests"],
                    "modular_zero", report["modular_zero"],
                    "hits", report["hits"][:20],
                    "hit_count", len(report["hits"]),
                    "seconds", f"{time.monotonic() - started:.3f}",
                    flush=True,
                )
                gc.collect()
        del targets, monomial_index, cumulative, all_monomials
        gc.collect()

    semantic = tuple(
        (
            report["canary"], report["degree"], report["height"],
            report["prime"], report["rank"], report["rows_q"],
            report["rows_minor"], report["nonzero_minors"],
            report["minor_degrees"], report["omitted"],
            report["support_reject"], report["modular_tests"],
            report["modular_zero"], report["hits"],
        )
        for report in reports
    )
    digest = hashlib.sha256(repr(semantic).encode("ascii")).hexdigest()
    print("SEMANTIC_SHA256", digest)
    print("TOTAL_HITS", sum(len(report["hits"]) for report in reports))
    print(
        "SCOPE bounded Macaulay pieces over F2/F3; modular misses are not a Q no-go",
    )
    return reports, digest


def old_closures():
    raw = MORSE.read_bytes()
    header_format = "<8sIHHHIII"
    position = struct.calcsize(header_format)
    magic, count, *_rest = struct.unpack_from(header_format, raw)
    if magic != column_scan.MORSE_MAGIC or count != column_scan.MORSE_CLOSED_COUNT:
        raise AssertionError("Morse header changed")
    fixed_format = "<HHHHHbB"
    fixed_size = struct.calcsize(fixed_format)
    result = set()
    for _ in range(count):
        first, second, third, _frame, _variables, _scalar, factor_count = (
            struct.unpack_from(fixed_format, raw, position)
        )
        position += fixed_size + factor_count
        result.add((first, second, third))
    if position != len(raw) or len(result) != count:
        raise AssertionError("Morse record parsing changed")
    packed = json.loads(SHEAR.read_text())
    result.update(tuple(record["original"]) for record in packed["records"])
    if len(result) != 65_611:
        raise AssertionError("old closure union changed")
    return result


def factor_kinds():
    occurrences, occurrence_factor, _polynomials = labeled.factor_polynomials()
    factor_occurrence = labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    _representatives, _stabilizers, alignment, _maps, _inverse_maps = (
        labeled.factor_orbit_data(occurrences, occurrence_factor)
    )
    if tuple(sorted(alignment)) != tuple(range(column_scan.FACTOR_COUNT)):
        raise AssertionError("factor-kind alignment changed")
    return tuple(alignment[factor][0] for factor in range(column_scan.FACTOR_COUNT))


def replay_residue_counts(source):
    actual = hashlib.sha256(source.read_bytes()).hexdigest()
    if actual != POST_TRIANGULAR_SHA256:
        raise AssertionError(f"post-triangular source digest changed: {actual}")
    raw = source.read_bytes()
    count, = struct.unpack_from("<I", raw)
    if count != POST_TRIANGULAR_COUNT or len(raw) != 4 + 6 * count:
        raise AssertionError("bad post-triangular source")
    closed = old_closures()
    kinds = factor_kinds()
    counts = Counter()
    kept = 0
    for first, second, third in struct.iter_unpack("<HHH", raw[4:]):
        row = first, second, third
        if row in closed:
            continue
        counts[tuple(sorted((kinds[first], kinds[second], kinds[third])))] += 1
        kept += 1
    if kept != FINAL_RESIDUE_COUNT or dict(counts) != FINAL_KIND_COUNTS:
        raise AssertionError("final residue kind census changed")
    print("PASS final residue rows", kept, "kind_triples", len(counts))
    for kind, number in sorted(counts.items()):
        print("RESIDUE_KIND", kind, number)
    print("SCOPE census only; no polynomial-multivector closure scan of these rows")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--canary", type=int, nargs="*")
    parser.add_argument("--degree", type=int)
    parser.add_argument("--height", type=int, nargs="*", default=list(range(9)))
    parser.add_argument("--prime", type=int, nargs="*", default=list(DEFAULT_PRIMES))
    parser.add_argument("--max-factors", type=int, default=3)
    parser.add_argument("--skip-screen", action="store_true")
    parser.add_argument(
        "--residue-source", type=Path,
        help="optional pinned 1,885,400-row post-triangular source for the 26-kind census",
    )
    arguments = parser.parse_args()

    if arguments.degree is not None and arguments.degree < 0:
        raise ValueError("degree must be nonnegative")
    if arguments.max_factors < 0:
        raise ValueError("max-factors must be nonnegative")
    if any(prime not in DEFAULT_PRIMES for prime in arguments.prime):
        raise ValueError("supported primes are 2 and 3")
    if any(not 0 <= height < 9 for height in arguments.height):
        raise ValueError("bad height")
    canaries = tuple(range(len(HARD))) if arguments.canary is None else tuple(arguments.canary)
    if any(not 0 <= canary < len(HARD) for canary in canaries):
        raise ValueError("bad canary")

    default_profile = (
        canaries == tuple(range(len(HARD)))
        and arguments.degree is None
        and tuple(arguments.height) == tuple(range(9))
        and tuple(arguments.prime) == DEFAULT_PRIMES
        and arguments.max_factors == 3
        and not arguments.skip_screen
    )
    if not arguments.skip_screen:
        reports, digest = run_screen(
            canaries,
            arguments.degree,
            tuple(arguments.height),
            tuple(arguments.prime),
            arguments.max_factors,
        )
        if default_profile:
            if any(report["omitted"] for report in reports):
                raise AssertionError("default profile omitted a generator")
            if any(report["hits"] for report in reports):
                raise AssertionError("default bounded no-hit boundary changed")
            if (
                EXPECTED_DEFAULT_SEMANTIC_SHA256
                and digest != EXPECTED_DEFAULT_SEMANTIC_SHA256
            ):
                raise AssertionError("default semantic digest changed")

    if len(FINAL_KIND_COUNTS) != 26 or sum(FINAL_KIND_COUNTS.values()) != FINAL_RESIDUE_COUNT:
        raise AssertionError("pinned final kind counts are inconsistent")
    print(
        "RECORDED_RESIDUE_COUNTS", FINAL_RESIDUE_COUNT,
        "across", len(FINAL_KIND_COUNTS), "kind triples",
    )
    if arguments.residue_source is not None:
        replay_residue_counts(arguments.residue_source)
    else:
        print(
            "PROVENANCE residue kind replay requires --residue-source",
            POST_TRIANGULAR_SHA256,
        )


if __name__ == "__main__":
    main()
