#!/usr/bin/env python3
"""Exact undominated separator birth at extremal parent 187.

This verifier isolates the second relevant residual crossing on the standard
``e``-coordinate line through catalog parent 187.  Reversing the crossing
creates a singleton minimal separator while two size-two separators remain.
Thus the birth shrinks an escape mask without landing in the four-singleton
regime left to the universal obstruction.

The affected endpoint loses six escape directions, and its common overlap
with the paired extremal endpoint drops from 15 to 9.  This is one exact
labeled type-49 edge, not a classification of all undominated births and not
a proof of diagonal two.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled
import DIAG9_GRAPH_exact_topes as exact_topes
import DIAG9_GRAPH_parent860_star as coordinate_star
import verify_diag2_escape_minimal_separators as minimal
import verify_diag2_escape_set_topes as escape
import verify_diag2_extremal_safe_loss_edge as safe_loss
import verify_diag2_near_counterexample_separators as near_separators


PARENT_INDEX = 187
VARIABLE = 4  # e in the standard a,...,i chart
FACTOR_ID = 23_604
FACTOR_KIND = 49
FACTOR_OCCURRENCE = (2, 28, 30, 49)
EPSILON = Fraction(1, 10**12)
EXPECTED_ROOT = Fraction(
    -1_089_491_496_778_107_199_382_036_370_734_683_661_740_772,
    27_814_073_111_268_337_001_739_262_415_917_341_966_019_625,
)
EXPECTED_MAPPED_PAIRS = (
    (41_791_434_804_464_172, 69_849_397_930_972_629, 6),
    (41_224_216_731_022_549, 41_224_087_949_575_724, 6),
    (68_230_936_274_949_461, 70_482_716_760_692_055, 6),
)
EXPECTED_EXCHANGE = (2, 2)
EXPECTED_OBSERVATIONS = (
    ((15, 67, 56), (15, 56, 67), ("not-both-bad", True, False)),
    ((9, 61, 56), (15, 56, 67), ("not-both-bad", True, False)),
)
EXPECTED_LOST_DIRECTIONS = (
    (2, 3, -1),
    (2, 5, -1),
    (2, 6, -1),
    (2, 7, -1),
    (2, 8, -1),
    (4, 3, 1),
)
EXPECTED_SURVIVING_COMMON = (
    (1, 2, -1),
    (1, 4, -1),
    (1, 4, 1),
    (1, 5, -1),
    (3, 7, 1),
    (4, 1, -1),
    (6, 8, -1),
    (7, 3, -1),
    (8, 6, 1),
)
EXPECTED_DIGEST = "a121da97360beede1c54d956877b12fe52a374d686bc6a496923704ec41172e6"


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


def directions(mask):
    return tuple(
        escape.DIRECTIONS[index]
        for index in range(len(escape.DIRECTIONS))
        if mask & (1 << index)
    )


def observation(records, pairs):
    answer = []
    for left, right, _base_overlap in pairs:
        left_record = records[left]
        right_record = records[right]
        if left_record[0] == "tope" or right_record[0] == "tope":
            answer.append(
                (
                    "not-both-bad",
                    left_record[0] == "tope",
                    right_record[0] == "tope",
                )
            )
            continue
        left_mask, right_mask = left_record[0], right_record[0]
        answer.append(
            (
                (left_mask & right_mask).bit_count(),
                left_mask.bit_count(),
                right_mask.bit_count(),
            )
        )
    return tuple(answer)


def endpoint_records(topes, signatures):
    tope_set = set(topes)
    prepared = escape.prepare_directions(topes)
    indexes = minimal.build_source_indexes(topes)
    records = {}
    for signature in signatures:
        if signature in tope_set:
            records[signature] = ("tope",)
            continue
        mask = escape.escape_mask(signature, prepared)
        separator_profile = profile(signature, indexes)
        reconstructed = minimal.escape_mask_from_minimal_separators(
            signature, indexes
        )[0]
        if reconstructed != mask:
            raise AssertionError("minimal separators reconstructed a wrong mask")
        records[signature] = (mask, separator_profile)
    return records


def semantic_digest(center, endpoints, topes, records, observations):
    digest = hashlib.sha256()
    digest.update(b"diag2-extremal-undominated-birth-edge-v1\0")
    for value in (PARENT_INDEX, VARIABLE, FACTOR_ID, FACTOR_KIND):
        digest.update(int(value).to_bytes(8, "little", signed=True))
    for value in FACTOR_OCCURRENCE:
        digest.update(int(value).to_bytes(8, "little"))
    for point in (center,) + endpoints:
        for value in point:
            digest.update(str(value.numerator).encode("ascii") + b"/")
            digest.update(str(value.denominator).encode("ascii") + b"\0")
    for table in topes:
        for tope in table:
            digest.update(int(tope).to_bytes(8, "little"))
    for endpoint in records:
        for signature, record in sorted(endpoint.items()):
            digest.update(int(signature).to_bytes(8, "little"))
            digest.update(repr(record).encode("ascii") + b"\0")
    digest.update(repr(observations).encode("ascii") + b"\0")
    digest.update(repr(EXPECTED_LOST_DIRECTIONS).encode("ascii") + b"\0")
    digest.update(repr(EXPECTED_SURVIVING_COMMON).encode("ascii") + b"\0")
    return digest.hexdigest()


def main():
    _atlas, by_index, active = near_separators.load_atlas()
    coordinates, multipliers = safe_loss.normalize_parent(
        by_index[PARENT_INDEX]["matrix"]
    )
    raw_pairs = tuple(
        tuple(pair) for pair in active[PARENT_INDEX]["pairs"] if pair[2] == 6
    )
    pairs = tuple(
        (
            safe_loss.map_signature(left, multipliers),
            safe_loss.map_signature(right, multipliers),
            overlap,
        )
        for left, right, overlap in raw_pairs
    )
    if pairs != EXPECTED_MAPPED_PAIRS:
        raise AssertionError(f"mapped parent-187 pair atlas changed: {pairs}")

    occurrences, occurrence_factor, factor_polynomials = labeled.factor_polynomials()
    _representatives, _stabilizers, alignment, factor_occurrence, _sizes = (
        labeled.factor_orbit_data(occurrences, occurrence_factor)
    )
    if alignment[FACTOR_ID][0] != FACTOR_KIND:
        raise AssertionError("selected residual factor changed incidence type")
    if factor_occurrence[FACTOR_ID] != FACTOR_OCCURRENCE:
        raise AssertionError("selected residual factor occurrence changed")

    restrictions = tuple(
        coordinate_star.restrict_polynomial(polynomial, VARIABLE, coordinates)
        for polynomial in factor_polynomials
    )
    target = restrictions[FACTOR_ID]
    if len(target) != 2:
        raise AssertionError("selected type-49 restriction is not affine")
    root = -target[0]
    if root != EXPECTED_ROOT:
        raise AssertionError(f"selected residual root changed: {root}")

    center = list(coordinates)
    center[VARIABLE] += root
    center = tuple(center)
    before = list(center)
    after = list(center)
    before[VARIABLE] -= EPSILON
    after[VARIABLE] += EPSILON
    endpoints = (tuple(before), tuple(after))

    center_signs = tuple(
        safe_loss.sign(safe_loss.polynomial_value(polynomial, root))
        for polynomial in restrictions
    )
    zeros = tuple(index for index, value in enumerate(center_signs) if not value)
    if zeros != (FACTOR_ID,):
        raise AssertionError(f"wall center has residual zeros {zeros}")
    endpoint_signs = tuple(
        tuple(
            safe_loss.sign(
                safe_loss.polynomial_value(polynomial, root + direction * EPSILON)
            )
            for polynomial in restrictions
        )
        for direction in (-1, 1)
    )
    if any(not value for signs in endpoint_signs for value in signs):
        raise AssertionError("an endpoint lies on a residual wall")
    changed = tuple(
        index
        for index, values in enumerate(zip(*endpoint_signs, strict=True))
        if values[0] != values[1]
    )
    if changed != (FACTOR_ID,):
        raise AssertionError(f"endpoint perturbation flips factors {changed}")
    if any(
        center_signs[index] != endpoint_signs[0][index]
        or center_signs[index] != endpoint_signs[1][index]
        for index in range(len(restrictions))
        if index != FACTOR_ID
    ):
        raise AssertionError("a nonselected factor changes in the wall germ")

    expected_parent = exact_topes.parent_signs(safe_loss.integer_matrix(center))
    endpoint_topes = tuple(
        safe_loss.tope_table(point, expected_parent, label)
        for point, label in zip(endpoints, ("before", "after"), strict=True)
    )
    before_set, after_set = map(set, endpoint_topes)
    exchange = (len(before_set - after_set), len(after_set - before_set))
    if exchange != EXPECTED_EXCHANGE:
        raise AssertionError(f"residual tope exchange changed: {exchange}")

    signatures = tuple(sorted({value for pair in pairs for value in pair[:2]}))
    endpoint_data = tuple(
        endpoint_records(topes, signatures) for topes in endpoint_topes
    )
    observations = tuple(observation(records, pairs) for records in endpoint_data)
    if observations != EXPECTED_OBSERVATIONS:
        raise AssertionError(f"birth-edge observations changed: {observations}")

    target_signature = pairs[0][0]
    partner_signature = pairs[0][1]
    before_record = endpoint_data[0][target_signature]
    after_record = endpoint_data[1][target_signature]
    if before_record[0] == "tope" or after_record[0] == "tope":
        raise AssertionError("the affected signature ceased to be bad")
    before_mask, before_profile = before_record
    after_mask, after_profile = after_record
    if after_mask & ~before_mask:
        raise AssertionError("the undominated birth unexpectedly gains directions")
    lost = before_mask & ~after_mask
    if directions(lost) != EXPECTED_LOST_DIRECTIONS:
        raise AssertionError(f"wrong directions lost at the birth: {directions(lost)}")

    if after_profile[0] != ((1,),) or after_profile[1] != ((1,),):
        raise AssertionError("the expected singleton birth is missing at sources 1/2")
    if after_profile[3] != ((1,),):
        raise AssertionError("the expected singleton birth is missing at source 4")
    if any((1,) in source_family for source_family in before_profile):
        raise AssertionError("the singleton separator existed before its birth")
    retained_non_singletons = tuple(
        (source, separator)
        for source, family in enumerate(after_profile, 1)
        for separator in family
        if len(separator) > 1
    )
    if retained_non_singletons != ((6, (30, 33)), (7, (30, 33))):
        raise AssertionError(
            f"birth destination lost its pinned non-singletons: {retained_non_singletons}"
        )
    if safe_loss.dominates(before_profile, after_profile):
        raise AssertionError("the selected separator birth is actually dominated")

    for signature in signatures:
        if signature == target_signature:
            continue
        if endpoint_data[0][signature] != endpoint_data[1][signature]:
            raise AssertionError(f"untracked endpoint changed at signature {signature}")

    before_partner = endpoint_data[0][partner_signature][0]
    after_partner = endpoint_data[1][partner_signature][0]
    if before_partner == "tope" or after_partner == "tope":
        raise AssertionError("the extremal partner ceased to be bad")
    if before_partner != after_partner:
        raise AssertionError("the extremal partner changes across the birth")
    surviving_common = after_mask & after_partner
    if directions(surviving_common) != EXPECTED_SURVIVING_COMMON:
        raise AssertionError(
            f"wrong common directions survive: {directions(surviving_common)}"
        )
    common_lost = (before_mask & before_partner) & ~surviving_common
    if directions(common_lost) != EXPECTED_LOST_DIRECTIONS:
        raise AssertionError("the six lost endpoint directions were not all common")

    digest = semantic_digest(
        center, endpoints, endpoint_topes, endpoint_data, observations
    )
    if EXPECTED_DIGEST is not None and digest != EXPECTED_DIGEST:
        raise AssertionError(f"undominated-birth semantic digest changed: {digest}")

    print("PASS parent 187 has three mapped overlap-six pair orbits")
    print("PASS isolated type-49 factor 23604 at one exact rational wall root")
    print("PASS endpoint tope exchange is 2/2 and only one tracked mask changes")
    print("THEOREM reverse crossing births singleton row 1 at sources 1, 2, and 4")
    print("THEOREM destination retains size-two separator {30,33} at sources 6 and 7")
    print("THEOREM affected mask shrinks 67 -> 61; pair overlap shrinks 15 -> 9")
    print("PASS nine exact common shear directions survive the undominated birth")
    print("SEMANTIC", digest)
    print("SCOPE one exact labeled type-49 edge; diagonal two remains open")


if __name__ == "__main__":
    main()
