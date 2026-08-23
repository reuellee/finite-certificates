#!/usr/bin/env python3
"""Standard-library replay of the ordered four-support t-root isolation."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from math import gcd, lcm
from pathlib import Path


HERE = Path(__file__).resolve().parent
SOURCE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz"
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ROOT_ISOLATION.json.gz"
FORMAT = "diag3-pair-global-row2599-four-support-root-isolation-v1"
SOURCE_FORMAT = "diag3-pair-global-row2599-four-support-base-projection-v1"


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def trim(polynomial):
    polynomial = list(polynomial)
    while len(polynomial) > 1 and not polynomial[-1]:
        polynomial.pop()
    return polynomial or [Fraction(0)]


def divide_over_q(dividend, divisor):
    dividend = trim([Fraction(value) for value in dividend])
    divisor = trim([Fraction(value) for value in divisor])
    require(divisor != [0], "division by zero polynomial")
    if len(dividend) < len(divisor):
        return [Fraction(0)], dividend
    quotient = [Fraction(0)] * (len(dividend) - len(divisor) + 1)
    while dividend != [0] and len(dividend) >= len(divisor):
        value = dividend[-1] / divisor[-1]
        offset = len(dividend) - len(divisor)
        quotient[offset] = value
        for index, divisor_value in enumerate(divisor):
            dividend[offset + index] -= value * divisor_value
        dividend = trim(dividend)
    return trim(quotient), dividend


def evaluate(polynomial, value):
    answer = Fraction(0)
    for coefficient in reversed(polynomial):
        answer = answer * value + coefficient
    return answer


def sturm_sequence(polynomial):
    polynomial = trim([Fraction(value) for value in polynomial])
    derivative = [index * polynomial[index] for index in range(1, len(polynomial))]
    sequence = [polynomial, trim(derivative)]
    while sequence[-1] != [0]:
        _quotient, remainder = divide_over_q(sequence[-2], sequence[-1])
        if remainder == [0]:
            break
        next_row = trim([-value for value in remainder])
        positive_scale = abs(next_row[-1])
        sequence.append([value / positive_scale for value in next_row])
    return sequence


def variations(sequence, value):
    values = [evaluate(polynomial, value) for polynomial in sequence]
    signs = [1 if item > 0 else -1 for item in values if item]
    return sum(left != right for left, right in zip(signs, signs[1:]))


def roots_between(sequence, left, right):
    require(left < right, "nonpositive isolation interval")
    require(evaluate(sequence[0], left) != 0, "left endpoint is a root")
    require(evaluate(sequence[0], right) != 0, "right endpoint is a root")
    return variations(sequence, left) - variations(sequence, right)


def source_catalog_digest(rows):
    return digest(rows)


def validate_claims(candidate, observed):
    require(candidate["format"] == FORMAT, "wrong certificate format")
    require(candidate["status"] == "PROVED", "wrong proof status")
    scope = candidate["scope"]
    require(scope["interior_t_root_isolation"] == "COMPLETE", "false isolation scope")
    require(scope["global_root_deduplication"] == "COMPLETE_BY_PAIRWISE_DISJOINT_RATIONAL_ENCLOSURES", "false deduplication scope")
    require(scope["global_root_order"] == "COMPLETE", "false ordering scope")
    require(scope["base_sign_invariant_cad"] == "NOT_YET_CONSTRUCTED", "false CAD claim")
    require(scope["global_parent_cell_coverage"] == "NOT_CLAIMED", "false global claim")
    require(scope["honest_9dvl_score"] == "2/9", "dishonest theorem score")
    require(candidate["source"]["semantic_sha256"] == observed["source_semantic"], "source semantic")
    require(candidate["source"]["univariate_factor_catalog_sha256"] == observed["source_catalog_digest"], "source catalog digest")
    isolation = candidate["root_isolation"]
    require(isolation["distinct_interior_t_sections"] == 1_693, "section count")
    require(isolation["rational_sections"] == 19, "rational section count")
    require(isolation["irrational_sections"] == 1_674, "irrational section count")
    require(isolation["factors_with_interior_sections"] == 1_442, "active factor count")
    require(isolation["minimum_certified_gap"] == observed["minimum_gap"], "minimum gap")
    require(isolation["maximum_endpoint_numerator_bits"] == observed["maximum_numerator_bits"], "numerator bits")
    require(isolation["maximum_endpoint_denominator_bits"] == observed["maximum_denominator_bits"], "denominator bits")
    require(isolation["sections_sha256"] == observed["sections_digest"], "sections digest")
    require(candidate["semantic_sha256"] == observed["semantic"], "semantic digest")
    require(candidate["resource_effect"]["actual_distinct_sections"] == 1_693, "resource count")
    require(candidate["resource_effect"]["ceiling_not_triggered"] is True, "section ceiling")


def main():
    source = json.loads(gzip.decompress(SOURCE.read_bytes()))
    stored = json.loads(gzip.decompress(CERTIFICATE.read_bytes()))
    require(source["format"] == SOURCE_FORMAT, "wrong source format")
    require(source["status"] == "PROVED", "unproved source")
    projection = source["second_projection"]
    factor_rows = projection["catalog"]
    require([row["id"] for row in factor_rows] == list(range(2_333)), "source factor IDs")
    require(source_catalog_digest(factor_rows) == projection["catalog_sha256"], "source factor catalog corruption")
    require(stored["source"]["format"] == source["format"], "source format pin")
    require(stored["source"]["factor_root_incidences"] == 1_693, "source incidence pin")

    sections = stored["root_isolation"]["sections"]
    require([row["id"] for row in sections] == list(range(1_693)), "section IDs")
    width_ceiling = Fraction(stored["root_isolation"]["requested_interval_width_ceiling"])
    require(width_ceiling == Fraction(1, 2**48), "isolation precision")

    factors = [row["coefficients_low_to_high"] for row in factor_rows]
    sequences = [sturm_sequence(polynomial) for polynomial in factors]
    factor_sections = Counter()
    rational_sections = 0
    endpoint_values = []
    parsed = []
    for row in sections:
        factor_id = row["factor_id"]
        require(0 <= factor_id < len(factors), "factor ID")
        left, right = Fraction(row["left"]), Fraction(row["right"])
        require(0 < left <= right < 1, "section outside square interior")
        polynomial = factors[factor_id]
        if left == right:
            require(evaluate(polynomial, left) == 0, "claimed rational point is not a root")
            derivative = [index * polynomial[index] for index in range(1, len(polynomial))]
            require(evaluate(derivative, left) != 0, "claimed rational root is not simple")
            rational_sections += 1
        else:
            require(right - left <= width_ceiling, "isolation interval too wide")
            require(roots_between(sequences[factor_id], left, right) == 1, "interval does not isolate one root")
        factor_sections[factor_id] += 1
        require(row["factor_root_index"] == factor_sections[factor_id] - 1, "within-factor root order")
        endpoint_values.extend((left, right))
        parsed.append((left, right))

    require(all(right < next_left for (_left, right), (next_left, _next_right) in zip(parsed, parsed[1:])), "sections are not globally disjoint and ordered")
    for factor, row, sequence in zip(factors, factor_rows, sequences, strict=True):
        require(evaluate(factor, 0) != 0 and evaluate(factor, 1) != 0, "source boundary root")
        full_count = roots_between(sequence, Fraction(0), Fraction(1))
        require(full_count == row["interior_root_count"], f"source Sturm count failed at factor {row['id']}")
        require(factor_sections[row["id"]] == full_count, f"incomplete isolation at factor {row['id']}")

    minimum_gap = min(
        next_left - right
        for (_left, right), (next_left, _next_right) in zip(parsed, parsed[1:])
    )
    observed = {
        "source_semantic": source["semantic_sha256"],
        "source_catalog_digest": digest(factor_rows),
        "minimum_gap": str(minimum_gap),
        "maximum_numerator_bits": max(abs(value.numerator).bit_length() for value in endpoint_values),
        "maximum_denominator_bits": max(value.denominator.bit_length() for value in endpoint_values),
        "sections_digest": digest(sections),
        "semantic": digest(
            {
                "source_semantic_sha256": source["semantic_sha256"],
                "source_univariate_catalog_sha256": projection["catalog_sha256"],
                "sections": sections,
            }
        ),
    }
    require(rational_sections == 19, "rational root census")
    require(sum(factor_sections.values()) == 1_693, "section total")
    validate_claims(stored, observed)

    mutations = (
        (("status",), "OPEN"),
        (("scope", "interior_t_root_isolation"), "PARTIAL"),
        (("scope", "global_root_deduplication"), "NOT_PROVED"),
        (("scope", "global_root_order"), "NOT_PROVED"),
        (("scope", "base_sign_invariant_cad"), "COMPLETE"),
        (("scope", "honest_9dvl_score"), "3/9"),
        (("source", "semantic_sha256"), "0" * 64),
        (("root_isolation", "distinct_interior_t_sections"), 1_692),
        (("root_isolation", "sections_sha256"), "0" * 64),
        (("semantic_sha256",), "0" * 64),
        (("resource_effect", "ceiling_not_triggered"), False),
    )
    rejected = 0
    for path, value in mutations:
        target = stored
        for key in path[:-1]:
            target = target[key]
        original = target[path[-1]]
        target[path[-1]] = value
        try:
            validate_claims(stored, observed)
        except AssertionError:
            rejected += 1
        finally:
            target[path[-1]] = original
    require(rejected == len(mutations), "a hostile root-isolation mutation survived")

    print("PASS 1693/1693 interior roots isolated over exact rational endpoints")
    print("PASS 1693 globally disjoint sections in strict order")
    print("PASS 19 rational + 1674 irrational sections; no cross-factor coincidences")
    print("PASS complete standard-library Sturm coverage of all 2333 source factors")
    print(f"PASS {rejected}/{len(mutations)} hostile mutations rejected")
    print("SCOPE ordered t-axis sections only; base lifting and global pair complex remain open; honest 9DVL 2/9")


if __name__ == "__main__":
    main()
