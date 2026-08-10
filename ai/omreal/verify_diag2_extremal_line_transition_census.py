#!/usr/bin/env python3
"""Exact wall-by-wall diagonal-two census on the critical parent-187 e-line.

The earlier coordinate survey sampled four points on each side of each axis.
This verifier instead covers every open residual chamber on the complete
``e``-coordinate interval through the normalized realization of catalog
parent 187, stopping only at the two parent-bracket boundaries.

All real roots of all 26,740 primitive residual factors are isolated by
exact Sturm arithmetic.  Starting from the exactly enumerated central tope
table, the 1,649 single-occurrence crossings are propagated by the rank-four
signed-circuit exchange rule.  The 72 compound destinations are independently
enumerated exactly.  Mutable source indexes then reconstruct the complete
minimal-separator profiles and 112-direction escape masks of the six
signatures in the three extremal overlap-six atlas pairs after every crossing.
Independent exact tope enumerations also certify both terminal chambers.

This is complete coverage of one one-dimensional slice, not of the parent
realization cell and not a proof of diagonal two.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction
import hashlib

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as representative
import DIAG9_GRAPH_exact_topes as exact_topes
import DIAG9_GRAPH_parent860_star as coordinate_star
import verify_diag2_escape_minimal_separators as minimal
import verify_diag2_extremal_coordinate_survey as survey
import verify_diag2_extremal_safe_loss_edge as safe_loss
import verify_diag2_near_counterexample_separators as near_separators


PARENT_INDEX = 187
VARIABLE = 4  # e in the standard a,...,i chart
EXPECTED_ROOTS = 1_721
EXPECTED_CELLS = 1_722
EXPECTED_BOTH_BAD = 4_159
EXPECTED_NOT_BOTH_BAD = 1_007
EXPECTED_MINIMUM_OVERLAP = 6
EXPECTED_NON_SINGLETON_MINIMUM = 9
EXPECTED_TYPE_HISTOGRAM = {36: 40, 38: 11, 48: 21, 49: 634, 50: 657, 51: 358}
EXPECTED_MUTATION_HISTOGRAM = {2: 1_649, 4: 21, 10: 11, 72: 40}
EXPECTED_TRANSITION_COUNTS = {
    "badness-status-change": 2,
    "both-bad-pair-change": 6,
    "pair-change": 8,
    "tracked-change": 10,
}
EXPECTED_PAIR_TRANSITIONS = {
    (49, 15, 9, 6): 2,
    (50, ("both-bad", 12, 56, 62, True), ("not-both-bad", True, False)): 1,
    (50, 12, 6, 6): 1,
    (50, 9, 6, 5): 2,
    (50, 9, 6, 6): 1,
    (51, ("both-bad", 9, 62, 56, True), ("not-both-bad", False, True)): 1,
}
EXPECTED_TRACKED_FACTORS = {
    (8_421, 51): 1,
    (10_115, 51): 1,
    (11_045, 50): 1,
    (13_869, 50): 1,
    (16_242, 50): 1,
    (19_971, 50): 1,
    (22_118, 49): 1,
    (23_559, 50): 1,
    (23_604, 49): 1,
    (23_979, 50): 1,
}
EXPECTED_DIGEST = "0302dcf1e4ce10980c6133966d42048b45209a0739ae823d67bf7ec891c6845a"

SIMPLE_KINDS = frozenset((49, 50, 51))
COMPOUND_KINDS = frozenset((36, 38, 48))
EXPECTED_EXCHANGE = {36: 72, 38: 10, 48: 4, 49: 2, 50: 2, 51: 2}

FULL_SIGNATURE_MASK = (1 << 56) - 1


def simple_between(left: Fraction, right: Fraction) -> Fraction:
    """Choose a small exact rational strictly inside an open interval."""

    midpoint = (left + right) / 2
    for bound in (10**6, 10**8, 10**10, 10**12, 10**14, 10**16):
        candidate = midpoint.limit_denominator(bound)
        if left < candidate < right:
            return candidate
    return midpoint


def mapped_pairs(by_index, active):
    base, multipliers = safe_loss.normalize_parent(
        by_index[PARENT_INDEX]["matrix"]
    )
    raw = tuple(
        tuple(pair) for pair in active[PARENT_INDEX]["pairs"] if pair[2] == 6
    )
    if len(raw) != 3:
        raise AssertionError("parent 187 no longer has three overlap-six pairs")
    pairs = tuple(
        (
            safe_loss.map_signature(left, multipliers),
            safe_loss.map_signature(right, multipliers),
            overlap,
        )
        for left, right, overlap in raw
    )
    return base, pairs


def mutable_source_indexes(topes):
    """Build minimal-separator indexes whose buckets support tope updates."""

    fixed = minimal.build_source_indexes(topes)
    answer = {}
    for source, (on_source, away, buckets) in fixed.items():
        answer[source] = (
            on_source,
            away,
            {key: set(values) for key, values in buckets.items()},
        )
    return answer


def update_source_indexes(indexes, removed, added):
    for tope in removed:
        for on_source, away, buckets in indexes.values():
            key = tope & away
            value = tope & on_source
            bucket = buckets.get(key)
            if bucket is None or value not in bucket:
                raise AssertionError("removed tope was absent from a source index")
            bucket.remove(value)
            if not bucket:
                del buckets[key]
    for tope in added:
        for on_source, away, buckets in indexes.values():
            key = tope & away
            value = tope & on_source
            bucket = buckets.setdefault(key, set())
            if value in bucket:
                raise AssertionError("added tope already existed in a source index")
            bucket.add(value)


def profile(signature, indexes):
    return tuple(
        tuple(
            tuple(minimal.support_indices(separator))
            for separator in minimal.minimal_separators(
                signature, indexes[source]
            )[1]
        )
        for source in range(1, 9)
    )


def records(topes, indexes, signatures):
    answer = {}
    for signature in signatures:
        if signature in topes:
            answer[signature] = ("tope",)
            continue
        reconstructed = minimal.escape_mask_from_minimal_separators(
            signature, indexes
        )[0]
        answer[signature] = (reconstructed, profile(signature, indexes))
    return answer


def observation(pair, by_signature):
    left, right, _base_overlap = pair
    first = by_signature[left]
    second = by_signature[right]
    if first[0] == "tope" or second[0] == "tope":
        return ("not-both-bad", first[0] == "tope", second[0] == "tope")
    left_mask, left_profile = first
    right_mask, right_profile = second
    non_singleton = any(
        len(separator) > 1
        for endpoint in (left_profile, right_profile)
        for family in endpoint
        for separator in family
    )
    return (
        "both-bad",
        (left_mask & right_mask).bit_count(),
        left_mask.bit_count(),
        right_mask.bit_count(),
        non_singleton,
    )


def canonical_half(tope):
    antipode = FULL_SIGNATURE_MASK ^ tope
    return min(tope, antipode)


def active_exchanges(topes, half_topes, support_patterns):
    """Return all antipodal simplicial-tope exchanges for one factor."""

    exchanges = []
    for support, circuit_pattern in support_patterns:
        support_mask = sum(1 << index for index in support)
        candidates = []
        for tope in half_topes:
            if tope ^ support_mask in topes:
                continue
            signs = tuple(1 if tope & (1 << index) else -1 for index in support)
            if signs != circuit_pattern and signs != tuple(
                -value for value in circuit_pattern
            ):
                continue
            if all(tope ^ (1 << index) in topes for index in support):
                candidates.append(tope)
                if len(candidates) > 1:
                    break
        if len(candidates) > 1:
            raise AssertionError(
                f"support {support} has multiple antipodal mutation candidates"
            )
        if not candidates:
            continue
        removed = candidates[0]
        added = removed ^ support_mask
        antipodal_removed = FULL_SIGNATURE_MASK ^ removed
        antipodal_added = FULL_SIGNATURE_MASK ^ added
        if not all(
            antipodal_removed ^ (1 << index) in topes for index in support
        ):
            raise AssertionError("mutation candidate lost antipodal symmetry")
        if antipodal_added in topes:
            raise AssertionError("antipodal mutation target already exists")
        exchanges.append(
            (
                support,
                (removed, antipodal_removed),
                (added, antipodal_added),
            )
        )
    return tuple(exchanges)


def circuit_pattern(
    support,
    selected_factor,
    base_rows,
    occurrence_factor,
    flipped_factors,
    cache,
):
    """Return the signed circuit at the selected wall from adjacent basis signs."""

    key = (selected_factor, support)
    geometry = cache.get(key)
    if geometry is None:
        geometry = None
        for external in range(56):
            if external in support:
                continue
            candidate = []
            valid = True
            for index in range(4):
                sequence = support[:index] + support[index + 1 :] + (external,)
                factor = occurrence_factor.get(tuple(sorted(sequence)))
                if factor == selected_factor:
                    valid = False
                    break
                determinant = exact_topes.determinant(
                    tuple(base_rows[row] for row in sequence)
                )
                if not determinant:
                    valid = False
                    break
                candidate.append((1 if determinant > 0 else -1, factor))
            if valid:
                geometry = tuple(candidate)
                break
        if geometry is None:
            # Some determinant occurrences inherit the primitive factor from
            # a nonminimal incidence: at the wall at least one triple inside
            # the four-row support is already dependent.  Such a support is
            # not a signed four-circuit and cannot bound a simplicial tope.
            cache[key] = ()
            return None
        cache[key] = geometry

    if not geometry:
        return None

    answer = []
    for index, (base_sign, factor) in enumerate(geometry):
        current = -base_sign if factor in flipped_factors else base_sign
        answer.append((-1 if index & 1 else 1) * current)
    if not all(answer):
        raise AssertionError("wall circuit acquired a zero coefficient")
    return tuple(answer)


def cross_factor(
    topes,
    half_topes,
    indexes,
    selected_factor,
    supports,
    base_rows,
    occurrence_factor,
    flipped_factors,
    circuit_cache,
):
    support_patterns = []
    for support in supports:
        pattern = circuit_pattern(
                support,
                selected_factor,
                base_rows,
                occurrence_factor,
                flipped_factors,
                circuit_cache,
            )
        if pattern is not None:
            support_patterns.append((support, pattern))
    support_patterns = tuple(support_patterns)
    original = set(topes)
    pending = list(support_patterns)
    rounds = []
    while pending:
        active = active_exchanges(topes, half_topes, tuple(pending))
        if not active:
            break
        removed_supports = {support for support, _old, _new in active}
        removed = tuple(value for _support, old, _new in active for value in old)
        added = tuple(value for _support, _old, new in active for value in new)
        if len(set(removed)) != len(removed) or len(set(added)) != len(added):
            raise AssertionError("compound mutation round has overlapping exchanges")
        if set(removed) & set(added):
            raise AssertionError("compound mutation round re-adds a removed tope")
        if not set(removed) <= topes or set(added) & topes:
            raise AssertionError("mutation round is inconsistent with current topes")
        topes.difference_update(removed)
        topes.update(added)
        for value in removed:
            half_topes.discard(canonical_half(value))
        for value in added:
            half_topes.add(canonical_half(value))
        rounds.append(active)
        pending = [
            item for item in pending if item[0] not in removed_supports
        ]

    exchanges = tuple(exchange for round_ in rounds for exchange in round_)
    removed = tuple(sorted(original - topes))
    added = tuple(sorted(topes - original))
    if not exchanges or not removed:
        raise AssertionError("residual crossing has no active tope mutation")
    update_source_indexes(indexes, removed, added)

    processed_supports = {
        support for round_ in rounds for support, _old, _new in round_
    }
    reverse_pending = [
        item for item in support_patterns if item[0] in processed_supports
    ]
    reverse_topes = set(topes)
    reverse_half = set(half_topes)
    while reverse_pending:
        reverse = active_exchanges(
            reverse_topes, reverse_half, tuple(reverse_pending)
        )
        if not reverse:
            break
        reversed_supports = {support for support, _old, _new in reverse}
        reverse_removed = {value for _support, old, _new in reverse for value in old}
        reverse_added = {value for _support, _old, new in reverse for value in new}
        if len(reverse_removed) != 2 * len(reverse):
            raise AssertionError("reverse compound round overlaps removed topes")
        if len(reverse_added) != 2 * len(reverse):
            raise AssertionError("reverse compound round overlaps added topes")
        reverse_topes.difference_update(reverse_removed)
        reverse_topes.update(reverse_added)
        for value in reverse_removed:
            reverse_half.discard(canonical_half(value))
        for value in reverse_added:
            reverse_half.add(canonical_half(value))
        reverse_pending = [
            item for item in reverse_pending
            if item[0] not in reversed_supports
        ]
    if reverse_pending:
        raise AssertionError(
            f"factor {selected_factor} compound crossing left "
            f"{len(reverse_pending)} supports irreversible"
        )
    if reverse_topes != original:
        raise AssertionError(
            f"factor {selected_factor} compound crossing failed global reversibility"
        )
    if len(topes) != 26_112 or len(half_topes) != 13_056:
        raise AssertionError("mutation propagation changed the tope count")
    return exchanges, len(rounds)


def line_roots(factor_polynomials, base, brackets):
    lower, upper = survey.boundary_interval(base, VARIABLE, brackets)
    previous_segment = coordinate_star.SEGMENT
    coordinate_star.SEGMENT = (lower, upper)
    try:
        roots, restrictions = coordinate_star.crossing_groups(
            factor_polynomials, VARIABLE, base
        )
    finally:
        coordinate_star.SEGMENT = previous_segment
    if any(len(root["factors"]) != 1 for root in roots):
        raise AssertionError("critical line has a simultaneous primitive-factor root")
    if any(root["lower"] <= 0 <= root["upper"] for root in roots):
        raise AssertionError("central chart lies on or inside an isolated root box")
    return lower, upper, roots, restrictions


def exact_topes_at(base, parameter, expected_parent, label):
    point = list(base)
    point[VARIABLE] += parameter
    matrix = safe_loss.integer_matrix(tuple(point))
    if exact_topes.parent_signs(matrix) != expected_parent:
        raise AssertionError(f"{label} left the parent realization cell")
    rows = exact_topes.derived_rows(matrix)
    enumerated = exact_topes.enumerate_topes(rows, dimension=4)
    exact_topes.verify_topes(rows, enumerated)
    if len(enumerated) != 26_112:
        raise AssertionError(f"{label} has the wrong tope count")
    return set(enumerated)


def destination_parameters(ordered_roots, boundary, side):
    """Return one exact point in the cell entered after every ordered root."""

    answer = []
    for index, root in enumerate(ordered_roots):
        following = ordered_roots[index + 1] if index + 1 < len(ordered_roots) else None
        if side < 0:
            left = following["upper"] if following is not None else boundary
            right = root["lower"]
        else:
            left = root["upper"]
            right = following["lower"] if following is not None else boundary
        answer.append(simple_between(left, right))
    return tuple(answer)


def exact_cell_task(task):
    side, ordinal, base, parameter, expected_parent = task
    topes = exact_topes_at(
        base,
        parameter,
        expected_parent,
        f"compound destination {side}:{ordinal}",
    )
    return side, ordinal, tuple(sorted(topes))


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    return parser.parse_args()


def semantic_digest(roots, transitions, cell_observations, summary):
    digest = hashlib.sha256()
    digest.update(b"diag2-extremal-parent187-e-line-v1\0")
    for root in roots:
        digest.update(int(root["factors"][0]).to_bytes(4, "little"))
        digest.update(str(root["lower"]).encode("ascii") + b"\0")
        digest.update(str(root["upper"]).encode("ascii") + b"\0")
    for transition in transitions:
        digest.update(repr(transition).encode("ascii") + b"\0")
    for item in cell_observations:
        digest.update(repr(item).encode("ascii") + b"\0")
    digest.update(repr(summary).encode("ascii") + b"\0")
    return digest.hexdigest()


def main():
    args = parse_args()
    if args.workers < 1:
        raise ValueError("--workers must be positive")
    _atlas, by_index, active = near_separators.load_atlas()
    base, pairs = mapped_pairs(by_index, active)
    signatures = tuple(sorted({signature for pair in pairs for signature in pair[:2]}))
    expected_parent = exact_topes.parent_signs(safe_loss.integer_matrix(base))

    occurrences, occurrence_factor, factor_polynomials = labeled.factor_polynomials()
    supports_by_factor = defaultdict(list)
    for support in occurrences:
        supports_by_factor[occurrence_factor[support]].append(support)
    _representatives, _stabilizers, alignment, _factor_occurrence, _sizes = (
        labeled.factor_orbit_data(occurrences, occurrence_factor)
    )
    _residual, brackets = representative.polynomial_data()
    lower, upper, roots, _restrictions = line_roots(
        factor_polynomials, base, brackets
    )
    print(f"isolated {len(roots)} exact residual roots", flush=True)
    if EXPECTED_ROOTS is not None and len(roots) != EXPECTED_ROOTS:
        raise AssertionError(f"critical-line root count changed: {len(roots)}")

    base_matrix = safe_loss.integer_matrix(base)
    base_rows = exact_topes.derived_rows(base_matrix)
    base_topes = exact_topes_at(base, Fraction(0), expected_parent, "central cell")
    base_indexes = mutable_source_indexes(base_topes)
    base_records = records(base_topes, base_indexes, signatures)

    root_positions = {id(root): index for index, root in enumerate(roots)}
    negative = tuple(
        reversed([root for root in roots if root["upper"] < 0])
    )
    positive = tuple(root for root in roots if root["lower"] > 0)
    if len(negative) + len(positive) != len(roots):
        raise AssertionError("a root was not assigned to a side of the base")

    ordered_by_side = {-1: negative, 1: positive}
    parameters_by_side = {
        -1: destination_parameters(negative, lower, -1),
        1: destination_parameters(positive, upper, 1),
    }
    compound_tasks = []
    for side, ordered_roots in ordered_by_side.items():
        for ordinal, (root, parameter) in enumerate(
            zip(ordered_roots, parameters_by_side[side], strict=True), 1
        ):
            factor = root["factors"][0]
            kind = alignment[factor][0]
            if kind in COMPOUND_KINDS:
                compound_tasks.append(
                    (side, ordinal, base, parameter, expected_parent)
                )
            elif kind not in SIMPLE_KINDS:
                raise AssertionError(f"unclassified line-crossing type {kind}")

    exact_compound = {}
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(exact_cell_task, task): task[:2]
            for task in compound_tasks
        }
        for completed, future in enumerate(as_completed(futures), 1):
            side, ordinal, topes = future.result()
            exact_compound[(side, ordinal)] = topes
            if completed % 6 == 0:
                print(
                    f"compound exact cells {completed}/{len(compound_tasks)}",
                    flush=True,
                )
    if len(exact_compound) != len(compound_tasks):
        raise AssertionError("compound destination census is incomplete")

    histogram = Counter()
    mutation_histogram = Counter()
    mutation_round_histogram = Counter()
    type_histogram = Counter()
    transition_counts = Counter()
    pair_transition_histogram = Counter()
    tracked_factor_histogram = Counter()
    transitions = []
    cell_observations = []

    def retain_cell(side, ordinal, by_signature):
        observed = tuple(observation(pair, by_signature) for pair in pairs)
        cell_observations.append((side, ordinal, observed))
        for item in observed:
            if item[0] == "not-both-bad":
                histogram[("not-both-bad",)] += 1
            else:
                histogram[("both-bad", item[1], item[4])] += 1
        return observed

    retain_cell(0, 0, base_records)

    terminal_states = {}
    circuit_cache = {}
    processed_roots = 0
    for side, ordered_roots in ((-1, negative), (1, positive)):
        topes = set(base_topes)
        half_topes = {canonical_half(tope) for tope in topes}
        indexes = mutable_source_indexes(topes)
        flipped_factors = set()
        before_records = records(topes, indexes, signatures)
        for ordinal, root in enumerate(ordered_roots, 1):
            factor = root["factors"][0]
            kind = alignment[factor][0]
            before_observations = tuple(
                observation(pair, before_records) for pair in pairs
            )
            if kind in SIMPLE_KINDS:
                if len(supports_by_factor[factor]) != 1:
                    raise AssertionError(
                        f"simple type {kind} factor has multiple occurrences"
                    )
                exchanges, mutation_rounds = cross_factor(
                    topes,
                    half_topes,
                    indexes,
                    factor,
                    supports_by_factor[factor],
                    base_rows,
                    occurrence_factor,
                    flipped_factors,
                    circuit_cache,
                )
                exchange_size = 2 * len(exchanges)
            else:
                target = set(exact_compound[(side, ordinal)])
                removed = tuple(sorted(topes - target))
                added = tuple(sorted(target - topes))
                if len(removed) != len(added):
                    raise AssertionError("compound crossing changes the tope count")
                update_source_indexes(indexes, removed, added)
                topes = target
                half_topes = {canonical_half(tope) for tope in topes}
                exchange_size = len(removed)
                mutation_rounds = 0
            if exchange_size != EXPECTED_EXCHANGE[kind]:
                raise AssertionError(
                    f"type {kind} exchange changed: {exchange_size}"
                )
            if factor in flipped_factors:
                flipped_factors.remove(factor)
            else:
                flipped_factors.add(factor)
            after_records = records(topes, indexes, signatures)
            after_observations = retain_cell(side, ordinal, after_records)

            type_histogram[kind] += 1
            mutation_histogram[exchange_size] += 1
            mutation_round_histogram[mutation_rounds] += 1
            changed_signatures = tuple(
                signature
                for signature in signatures
                if before_records[signature] != after_records[signature]
            )
            if changed_signatures:
                transition_counts["tracked-change"] += 1
                tracked_factor_histogram[(factor, kind)] += 1

            pair_changes = []
            for pair_index, pair in enumerate(pairs):
                old = before_observations[pair_index]
                new = after_observations[pair_index]
                if old == new:
                    continue
                transition_counts["pair-change"] += 1
                detail = [pair_index, old, new]
                if old[0] == new[0] == "both-bad":
                    transition_counts["both-bad-pair-change"] += 1
                    left, right = pair[:2]
                    old_left, old_right = before_records[left], before_records[right]
                    new_left, new_right = after_records[left], after_records[right]
                    if old[1] >= new[1]:
                        high_left, high_right = old_left, old_right
                        low_left, low_right = new_left, new_right
                        high_overlap, low_overlap = old[1], new[1]
                    else:
                        high_left, high_right = new_left, new_right
                        low_left, low_right = old_left, old_right
                        high_overlap, low_overlap = new[1], old[1]
                    loss_budget = (
                        (high_left[0] & ~low_left[0]).bit_count()
                        + (high_right[0] & ~low_right[0]).bit_count()
                    )
                    pair_transition_histogram[
                        (kind, high_overlap, low_overlap, loss_budget)
                    ] += 1
                    if new[1] < old[1]:
                        transition_counts["overlap-decrease"] += 1
                    if loss_budget >= high_overlap:
                        transition_counts["budget-eligible"] += 1
                    detail.append(loss_budget)
                else:
                    transition_counts["badness-status-change"] += 1
                    pair_transition_histogram[(kind, old, new)] += 1
                pair_changes.append(tuple(detail))

            transitions.append(
                (
                    side,
                    ordinal,
                    root_positions[id(root)],
                    factor,
                    kind,
                    exchange_size,
                    changed_signatures,
                    tuple(pair_changes),
                )
            )
            before_records = after_records
            processed_roots += 1
            if processed_roots % 100 == 0:
                print(f"line transitions {processed_roots}/{len(roots)}", flush=True)
        terminal_states[side] = set(topes)

    negative_sample = simple_between(lower, roots[0]["lower"])
    positive_sample = simple_between(roots[-1]["upper"], upper)
    exact_negative = exact_topes_at(
        base, negative_sample, expected_parent, "negative terminal cell"
    )
    exact_positive = exact_topes_at(
        base, positive_sample, expected_parent, "positive terminal cell"
    )
    if terminal_states[-1] != exact_negative:
        raise AssertionError("negative propagated terminal table is not exact")
    if terminal_states[1] != exact_positive:
        raise AssertionError("positive propagated terminal table is not exact")

    cells = len(roots) + 1
    if EXPECTED_CELLS is not None and cells != EXPECTED_CELLS:
        raise AssertionError(f"critical-line cell count changed: {cells}")
    both_bad = sum(
        count for key, count in histogram.items() if key[0] == "both-bad"
    )
    not_both_bad = histogram[("not-both-bad",)]
    overlaps = [
        key[1] for key, count in histogram.items()
        if count and key[0] == "both-bad"
    ]
    non_singleton_overlaps = [
        key[1] for key, count in histogram.items()
        if count and key[0] == "both-bad" and key[2]
    ]
    actual_scalars = (
        both_bad,
        not_both_bad,
        min(overlaps),
        min(non_singleton_overlaps),
    )
    expected_scalars = (
        EXPECTED_BOTH_BAD,
        EXPECTED_NOT_BOTH_BAD,
        EXPECTED_MINIMUM_OVERLAP,
        EXPECTED_NON_SINGLETON_MINIMUM,
    )
    if actual_scalars != expected_scalars:
        raise AssertionError(f"critical-line extrema changed: {actual_scalars}")
    if dict(type_histogram) != EXPECTED_TYPE_HISTOGRAM:
        raise AssertionError(f"critical-line type census changed: {type_histogram}")
    if dict(mutation_histogram) != EXPECTED_MUTATION_HISTOGRAM:
        raise AssertionError(
            f"critical-line mutation census changed: {mutation_histogram}"
        )
    if dict(transition_counts) != EXPECTED_TRANSITION_COUNTS:
        raise AssertionError(
            f"critical-line tracked transitions changed: {transition_counts}"
        )
    if dict(pair_transition_histogram) != EXPECTED_PAIR_TRANSITIONS:
        raise AssertionError(
            f"critical-line pair transitions changed: {pair_transition_histogram}"
        )
    if dict(tracked_factor_histogram) != EXPECTED_TRACKED_FACTORS:
        raise AssertionError(
            f"critical-line tracked factors changed: {tracked_factor_histogram}"
        )
    summary = (
        len(roots),
        cells,
        both_bad,
        not_both_bad,
        min(overlaps),
        min(non_singleton_overlaps),
        tuple(sorted(type_histogram.items())),
        tuple(sorted(mutation_histogram.items())),
        tuple(sorted(mutation_round_histogram.items())),
        tuple(sorted(transition_counts.items())),
        tuple(sorted(pair_transition_histogram.items(), key=repr)),
        tuple(sorted(tracked_factor_histogram.items())),
        tuple(sorted(histogram.items(), key=repr)),
    )
    digest = semantic_digest(roots, transitions, cell_observations, summary)
    if EXPECTED_DIGEST is not None and digest != EXPECTED_DIGEST:
        raise AssertionError(f"critical-line semantic digest changed: {digest}")

    print(f"PASS isolated all {len(roots)} residual roots and {cells} open cells")
    print("PASS all 1,649 simple crossings are reversible signed-circuit exchanges")
    print("PASS all 72 compound destinations have independent exact tope tables")
    print("PASS propagated tope tables equal both exact terminal enumerations")
    print(
        f"PASS {both_bad} pair-cells remain simultaneously bad; "
        f"{not_both_bad} lose an endpoint"
    )
    print(
        f"THEOREM minimum tracked overlap is {min(overlaps)}; "
        f"non-singleton minimum is {min(non_singleton_overlaps)}"
    )
    print("MUTATIONS", tuple(sorted(mutation_histogram.items())))
    print("MUTATION_ROUNDS", tuple(sorted(mutation_round_histogram.items())))
    print("TRANSITIONS", tuple(sorted(transition_counts.items())))
    print("PAIR_TRANSITIONS", tuple(sorted(pair_transition_histogram.items(), key=repr)))
    print("TRACKED_FACTORS", tuple(sorted(tracked_factor_histogram.items())))
    print("SEMANTIC", digest)
    print("SCOPE complete parent-187 e-line slice; no parent-cell coverage")


if __name__ == "__main__":
    main()
