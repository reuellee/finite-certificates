#!/usr/bin/env python3
"""Exact 216-chart separator-bifurcation survey at the hardest atlas parents.

Parents 187, 842, and 2612 are the only catalog representatives carrying
three antipodal overlap-six pair orbits apiece in the committed extremal
atlas.  For each parent, this verifier samples four exact rational points on
each side of all nine standard-coordinate axes, at 1%, 10%, 50%, and 90% of
the distance to the first parent-bracket boundary.  It reconstructs all
26,112 derived topes at every sample and tracks the three extremal pairs.

The survey is a deterministic finite falsification test, not realization-
chamber coverage.  It takes several minutes and is therefore explicit::

    python verify_diag2_extremal_coordinate_survey.py --workers 4
"""

from __future__ import annotations

import argparse
from collections import Counter
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction
import hashlib

import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as representative
import DIAG9_GRAPH_exact_topes as exact_topes
import DIAG9_GRAPH_parent860_star as coordinate_star
import verify_diag2_escape_minimal_separators as minimal
import verify_diag2_escape_set_topes as escape
import verify_diag2_extremal_safe_loss_edge as safe_loss
import verify_diag2_near_counterexample_separators as near_separators


PARENTS = (187, 842, 2612)
FRACTIONS = (Fraction(1, 100), Fraction(1, 10), Fraction(1, 2), Fraction(9, 10))
EXPECTED_SAMPLES = 216
EXPECTED_PAIR_CHECKS = 648
EXPECTED_BOTH_BAD = 495
EXPECTED_NOT_BOTH_BAD = 153
EXPECTED_HISTOGRAM = {
    (False, 6): 425,
    (False, 16): 5,
    (True, 9): 9,
    (True, 11): 1,
    (True, 12): 18,
    (True, 15): 8,
    (True, 16): 3,
    (True, 17): 11,
    (True, 18): 5,
    (True, 21): 1,
    (True, 22): 2,
    (True, 23): 2,
    (True, 28): 1,
    (True, 29): 1,
    (True, 53): 1,
    (True, 57): 2,
}
EXPECTED_PARENT_SUMMARIES = {
    187: (178, 38, 6, 9),
    842: (149, 67, 6, 11),
    2612: (168, 48, 6, 9),
}
EXPECTED_DIGEST = "c31db4fe4272c12d5d6001f5c47a323a95a2d20750c6d56da5d63505990aa177"


def sign(value):
    return (value > 0) - (value < 0)


def boundary_interval(coordinates, variable, brackets):
    negative = []
    positive = []
    for polynomial in brackets.values():
        restriction = coordinate_star.restrict_polynomial(
            polynomial, variable, coordinates
        )
        if len(restriction) == 1:
            continue
        if len(restriction) != 2:
            raise AssertionError("a parent bracket is nonlinear in one coordinate")
        root = -restriction[0] / restriction[1]
        (negative if root < 0 else positive).append(root)
    if not negative or not positive:
        raise AssertionError("a survey coordinate ray has no parent boundary")
    return max(negative), min(positive)


def separator_profile(signature, indexes):
    answer = []
    for source in range(1, 9):
        _raw, separators = minimal.minimal_separators(
            signature, indexes[source]
        )
        answer.append(
            tuple(
                tuple(minimal.support_indices(separator))
                for separator in separators
            )
        )
    return tuple(answer)


def sample_digest(matrix, topes, records, observations):
    digest = hashlib.sha256()
    digest.update(b"diag2-extremal-coordinate-sample-v1\0")
    for row in matrix:
        for value in row:
            digest.update(int(value).to_bytes(64, "little", signed=True))
    for tope in topes:
        digest.update(int(tope).to_bytes(8, "little"))
    for signature, is_tope, mask, profile in records:
        digest.update(int(signature).to_bytes(8, "little"))
        digest.update(bytes((is_tope,)))
        digest.update(int(mask).to_bytes(16, "little"))
        digest.update(repr(profile).encode("ascii") + b"\0")
    digest.update(repr(observations).encode("ascii") + b"\0")
    return digest.hexdigest()


def audit_sample(task):
    (
        parent_index,
        variable,
        side,
        fraction_index,
        coordinates,
        expected_parent,
        pairs,
    ) = task
    matrix = safe_loss.integer_matrix(coordinates)
    if exact_topes.parent_signs(matrix) != expected_parent:
        raise AssertionError(
            f"parent {parent_index} coordinate {variable}: sample left parent cell"
        )
    rows = exact_topes.derived_rows(matrix)
    enumerated = exact_topes.enumerate_topes(rows, dimension=4)
    exact_topes.verify_topes(rows, enumerated)
    topes = tuple(sorted(enumerated))
    if len(topes) != 26_112:
        raise AssertionError("survey sample is not a generic residual chamber")

    tope_set = set(topes)
    prepared = escape.prepare_directions(topes)
    indexes = minimal.build_source_indexes(topes)
    signatures = tuple(sorted({signature for pair in pairs for signature in pair[:2]}))
    records = []
    by_signature = {}
    for signature in signatures:
        is_tope = signature in tope_set
        if is_tope:
            mask = 0
            profile = ()
        else:
            mask = escape.escape_mask(signature, prepared)
            profile = separator_profile(signature, indexes)
            reconstructed = minimal.escape_mask_from_minimal_separators(
                signature, indexes
            )[0]
            if reconstructed != mask:
                raise AssertionError("survey separator mask disagrees with direct mask")
        record = (signature, is_tope, mask, profile)
        records.append(record)
        by_signature[signature] = record

    observations = []
    for left, right, _base_overlap in pairs:
        left_record = by_signature[left]
        right_record = by_signature[right]
        if left_record[1] or right_record[1]:
            observations.append(("not-both-bad", left_record[1], right_record[1]))
            continue
        left_mask, left_profile = left_record[2], left_record[3]
        right_mask, right_profile = right_record[2], right_record[3]
        non_singleton = any(
            len(separator) > 1
            for profile in (left_profile, right_profile)
            for family in profile
            for separator in family
        )
        observations.append(
            (
                "both-bad",
                (left_mask & right_mask).bit_count(),
                left_mask.bit_count(),
                right_mask.bit_count(),
                non_singleton,
            )
        )
    observations = tuple(observations)
    digest = sample_digest(matrix, topes, tuple(records), observations)
    return (
        parent_index,
        variable,
        side,
        fraction_index,
        tuple(observations),
        digest,
    )


def aggregate_digest(results):
    digest = hashlib.sha256()
    digest.update(b"diag2-extremal-coordinate-survey-v1\0")
    for result in sorted(results):
        parent, variable, side, fraction_index, observations, sample = result
        for value in (parent, variable, side, fraction_index):
            digest.update(int(value).to_bytes(8, "little", signed=True))
        digest.update(repr(observations).encode("ascii") + b"\0")
        digest.update(bytes.fromhex(sample))
    return digest.hexdigest()


def build_tasks():
    _atlas, by_index, active = near_separators.load_atlas()
    _residual, brackets = representative.polynomial_data()
    tasks = []
    for parent_index in PARENTS:
        task = by_index[parent_index]
        atlas_record = active[parent_index]
        raw_pairs = tuple(
            tuple(pair) for pair in atlas_record["pairs"] if pair[2] == 6
        )
        if len(raw_pairs) != 3:
            raise AssertionError(
                f"parent {parent_index} no longer has three overlap-six pairs"
            )
        base, multipliers = safe_loss.normalize_parent(task["matrix"])
        pairs = tuple(
            (
                safe_loss.map_signature(left, multipliers),
                safe_loss.map_signature(right, multipliers),
                overlap,
            )
            for left, right, overlap in raw_pairs
        )
        expected_parent = exact_topes.parent_signs(safe_loss.integer_matrix(base))
        base_bracket_signs = {
            label: sign(coordinate_star.evaluate(polynomial, base))
            for label, polynomial in brackets.items()
        }
        if not all(base_bracket_signs.values()):
            raise AssertionError("survey base lies on a parent boundary")

        for variable in range(9):
            lower, upper = boundary_interval(base, variable, brackets)
            for side, boundary in ((-1, lower), (1, upper)):
                for fraction_index, fraction in enumerate(FRACTIONS):
                    parameter = boundary * fraction
                    coordinates = list(base)
                    coordinates[variable] += parameter
                    coordinates = tuple(coordinates)
                    sample_signs = {
                        label: sign(coordinate_star.evaluate(polynomial, coordinates))
                        for label, polynomial in brackets.items()
                    }
                    if sample_signs != base_bracket_signs:
                        raise AssertionError("survey sample crossed a parent bracket")
                    tasks.append(
                        (
                            parent_index,
                            variable,
                            side,
                            fraction_index,
                            coordinates,
                            expected_parent,
                            pairs,
                        )
                    )
    if len(tasks) != EXPECTED_SAMPLES:
        raise AssertionError("wrong extremal coordinate-survey task count")
    return tuple(tasks)


def summarize(results):
    histogram = Counter()
    parent_counts = {parent: [0, 0, []] for parent in PARENTS}
    pair_checks = 0
    for result in results:
        parent = result[0]
        for observation in result[4]:
            pair_checks += 1
            if observation[0] == "not-both-bad":
                parent_counts[parent][1] += 1
                continue
            overlap = observation[1]
            non_singleton = observation[4]
            histogram[(non_singleton, overlap)] += 1
            parent_counts[parent][0] += 1
            parent_counts[parent][2].append((non_singleton, overlap))
    if pair_checks != EXPECTED_PAIR_CHECKS:
        raise AssertionError("wrong coordinate-survey pair-check count")
    both_bad = sum(values[0] for values in parent_counts.values())
    not_both_bad = sum(values[1] for values in parent_counts.values())
    if (both_bad, not_both_bad) != (EXPECTED_BOTH_BAD, EXPECTED_NOT_BOTH_BAD):
        raise AssertionError("coordinate-survey badness summary changed")
    if dict(histogram) != EXPECTED_HISTOGRAM:
        raise AssertionError(f"coordinate-survey histogram changed: {histogram}")
    for parent, (both, not_both, values) in parent_counts.items():
        minimum = min(overlap for _non_singleton, overlap in values)
        non_singleton_minimum = min(
            overlap for non_singleton, overlap in values if non_singleton
        )
        actual = (both, not_both, minimum, non_singleton_minimum)
        if actual != EXPECTED_PARENT_SUMMARIES[parent]:
            raise AssertionError(f"parent {parent} survey summary changed: {actual}")
    return histogram


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    return parser.parse_args()


def main():
    args = parse_args()
    if args.workers < 1:
        raise ValueError("--workers must be positive")
    tasks = build_tasks()
    results = []
    if args.workers == 1:
        for index, task in enumerate(tasks, 1):
            results.append(audit_sample(task))
            if index % 12 == 0:
                print(f"survey {index}/{len(tasks)}", flush=True)
    else:
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            futures = {executor.submit(audit_sample, task): task for task in tasks}
            for index, future in enumerate(as_completed(futures), 1):
                results.append(future.result())
                if index % 12 == 0:
                    print(f"survey {index}/{len(tasks)}", flush=True)

    histogram = summarize(results)
    digest = aggregate_digest(results)
    if digest != EXPECTED_DIGEST:
        raise AssertionError(f"coordinate-survey semantic digest changed: {digest}")
    non_singleton = sum(count for (flag, _overlap), count in histogram.items() if flag)
    print("PASS 216 exact charts and 648 tracked extremal-pair observations")
    print("PASS 495 observations remain simultaneously bad; 153 lose an endpoint")
    print("PASS no tracked overlap falls below the catalog minimum six")
    print(
        f"PASS all {non_singleton} non-singleton observations have overlap at least nine"
    )
    print("SEMANTIC", digest)
    print("SCOPE deterministic three-parent coordinate survey; no chamber coverage")


if __name__ == "__main__":
    main()
