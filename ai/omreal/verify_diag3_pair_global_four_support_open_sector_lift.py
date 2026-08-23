#!/usr/bin/env python3
"""Standard-library replay of the four-support open-t-sector base lift."""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from math import gcd, lcm
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz"
ROOTS = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ROOT_ISOLATION.json.gz"
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT.json"
FORMAT = "diag3-pair-global-row2599-four-support-open-sector-lift-v1"
SHARD_FORMAT = "diag3-pair-global-row2599-four-support-open-sector-lift-shard-v1"
BASE_FORMAT = "diag3-pair-global-row2599-four-support-base-projection-v1"
ROOT_FORMAT = "diag3-pair-global-row2599-four-support-root-isolation-v1"


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


def primitive(polynomial):
    polynomial = trim([Fraction(value) for value in polynomial])
    require(polynomial != [0], "zero polynomial has no primitive form")
    denominator = 1
    for value in polynomial:
        denominator = lcm(denominator, value.denominator)
    integers = [int(value * denominator) for value in polynomial]
    content = 0
    for value in integers:
        content = gcd(content, abs(value))
    integers = [value // content for value in integers]
    if integers[-1] < 0:
        integers = [-value for value in integers]
    return trim(integers)


def multiply(left, right):
    if trim(left) == [0] or trim(right) == [0]:
        return [0]
    answer = [Fraction(0)] * (len(left) + len(right) - 1)
    for left_degree, left_value in enumerate(left):
        for right_degree, right_value in enumerate(right):
            answer[left_degree + right_degree] += left_value * right_value
    return trim(answer)


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
    require(left < right, "nonpositive interval")
    require(evaluate(sequence[0], left) != 0, "left endpoint is a root")
    require(evaluate(sequence[0], right) != 0, "right endpoint is a root")
    return variations(sequence, left) - variations(sequence, right)


def parse_bivariate(rows):
    return {
        tuple(row["exponent"]): Fraction(row["coefficient"])
        for row in rows
        if Fraction(row["coefficient"])
    }


def specialize_in_t(polynomial, sample):
    degree_u = max(exponent[0] for exponent in polynomial)
    answer = [Fraction(0)] * (degree_u + 1)
    for (degree_u, degree_t), coefficient in polynomial.items():
        answer[degree_u] += coefficient * sample**degree_t
    return trim(answer)


def evaluate_at_u_one(polynomial):
    maximum_t = max(exponent[1] for exponent in polynomial)
    answer = [Fraction(0)] * (maximum_t + 1)
    for (_degree_u, degree_t), coefficient in polynomial.items():
        answer[degree_t] += coefficient
    answer = trim(answer)
    while len(answer) > 1 and answer[0] == 0:
        answer = answer[1:]
    while len(answer) > 1 and sum(answer) == 0:
        quotient, remainder = divide_over_q(answer, [-1, 1])
        require(remainder == [0], "failed t=1 boundary division")
        answer = trim(quotient)
    return None if len(answer) <= 1 else primitive(answer)


def sector_samples(root_record):
    sections = [
        (Fraction(row["left"]), Fraction(row["right"]))
        for row in root_record["root_isolation"]["sections"]
    ]
    return (
        [sections[0][0] / 2]
        + [
            (left[1] + right[0]) / 2
            for left, right in zip(sections, sections[1:])
        ]
        + [(sections[-1][1] + 1) / 2]
    )


def validate_claims(candidate, observed):
    require(candidate["format"] == FORMAT, "wrong certificate format")
    require(candidate["status"] == "PROVED", "wrong proof status")
    scope = candidate["scope"]
    require(scope["bounded_u_boundary_projection_audit"] == "COMPLETE", "false boundary scope")
    require(scope["open_t_sector_base_lift"] == "COMPLETE_BY_PROJECTION_INVARIANCE", "false sector scope")
    require(scope["algebraic_t_section_base_lift"] == "NOT_YET_CONSTRUCTED", "false section scope")
    require(scope["v_fiber_lift"] == "NOT_YET_CONSTRUCTED", "false fiber scope")
    require(scope["global_parent_cell_coverage"] == "NOT_CLAIMED", "false global claim")
    require(scope["honest_9dvl_score"] == "2/9", "dishonest theorem score")
    require(candidate["source"]["base_projection_semantic_sha256"] == observed["base_semantic"], "base source semantic")
    require(candidate["source"]["root_isolation_semantic_sha256"] == observed["root_semantic"], "root source semantic")
    boundary = candidate["bounded_u_boundary_audit"]
    require(boundary["base_factor_evaluations"] == 114, "boundary evaluations")
    require(boundary["nonconstant_boundary_evaluations_after_t_boundary_reduction"] == 28, "nonconstant boundary count")
    require(boundary["all_factors_present_in_second_projection_catalog"] is True, "missing boundary factor")
    require(boundary["factorizations_sha256"] == observed["boundary_digest"], "boundary digest")
    lift = candidate["open_sector_lift"]
    require(lift["open_t_sectors"] == 1_694, "t-sector count")
    require(lift["specialized_base_factor_instances"] == 193_116, "specialization count")
    require(lift["open_sector_u_root_sections"] == 132_134, "u-root count")
    require(lift["open_sector_u_strips"] == 133_828, "u-strip count")
    require(lift["open_sector_base_cells"] == 265_962, "base-cell count")
    require(lift["minimum_roots_in_one_t_sector"] == 54, "minimum sector roots")
    require(lift["maximum_roots_in_one_t_sector"] == 109, "maximum sector roots")
    require(lift["dyadic_endpoint_exponent"] == 48, "dyadic precision")
    require(lift["minimum_within_sector_certified_gap"] == observed["minimum_gap"], "minimum gap")
    require(lift["maximum_interval_span_numerator"] == observed["maximum_span_numerator"], "maximum span")
    require(lift["maximum_interval_width"] == observed["maximum_width"], "maximum width")
    require(lift["sectors_sha256"] == observed["sectors_digest"], "sector digest")
    require(candidate["semantic_sha256"] == observed["semantic"], "semantic digest")
    require(candidate["resource_effect"]["ceiling_not_triggered"] is True, "cell ceiling")


def main():
    base = json.loads(gzip.decompress(BASE.read_bytes()))
    roots = json.loads(gzip.decompress(ROOTS.read_bytes()))
    stored = json.loads(CERTIFICATE.read_bytes())
    require(base["format"] == BASE_FORMAT and base["status"] == "PROVED", "bad base source")
    require(roots["format"] == ROOT_FORMAT and roots["status"] == "PROVED", "bad root source")
    require(roots["source"]["semantic_sha256"] == base["semantic_sha256"], "source chain")

    base_rows = base["base_factorization"]["catalog"]
    factor_rows = base["second_projection"]["catalog"]
    base_polynomials = [parse_bivariate(row["polynomial"]) for row in base_rows]
    univariate_factors = [row["coefficients_low_to_high"] for row in factor_rows]
    require(len(base_polynomials) == 114 and len(univariate_factors) == 2_333, "source counts")

    boundary_rows = stored["bounded_u_boundary_audit"]["factorizations"]
    boundary_by_base = {row["base_factor_id"]: row for row in boundary_rows}
    require(len(boundary_by_base) == len(boundary_rows) == 28, "boundary row IDs")
    used_boundary_factors = set()
    boundary_occurrences = 0
    for base_id, polynomial in enumerate(base_polynomials):
        observed_boundary = evaluate_at_u_one(polynomial)
        if observed_boundary is None:
            require(base_id not in boundary_by_base, "spurious boundary factorization")
            continue
        require(base_id in boundary_by_base, "missing boundary factorization")
        product = [1]
        for factor in boundary_by_base[base_id]["factors"]:
            factor_id = factor["id"]
            require(0 <= factor_id < len(univariate_factors), "boundary factor ID")
            for _ in range(factor["multiplicity"]):
                product = multiply(product, univariate_factors[factor_id])
            used_boundary_factors.add(factor_id)
            boundary_occurrences += 1
        require(primitive(product) == observed_boundary, f"u=1 factorization failed at base {base_id}")
    require(len(used_boundary_factors) == stored["bounded_u_boundary_audit"]["distinct_projection_factors_used"], "boundary factor census")
    require(boundary_occurrences == stored["bounded_u_boundary_audit"]["factor_occurrences"], "boundary occurrences")

    expected_samples = sector_samples(roots)
    shard_manifest = stored["artifact_shards"]
    require(shard_manifest["format"] == SHARD_FORMAT, "wrong shard format")
    require(shard_manifest["shard_count"] == 32, "wrong shard count")
    shard_rows = shard_manifest["shards"]
    require([row["index"] for row in shard_rows] == list(range(32)), "shard IDs")
    sectors = []
    for row in shard_rows:
        expected_name = (
            "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT_"
            f"SHARD_{row['index']:02d}_OF_32.json.gz"
        )
        require(row["path"] == expected_name, "shard path")
        shard_path = CERTIFICATE.parent / expected_name
        compressed = shard_path.read_bytes()
        require(len(compressed) == row["bytes"], "shard byte count")
        require(sha256(compressed).hexdigest() == row["sha256"], "shard digest")
        shard = json.loads(gzip.decompress(compressed))
        require(shard["format"] == SHARD_FORMAT, "shard internal format")
        require(shard["shard_index"] == row["index"], "shard internal ID")
        require(shard["shard_count"] == 32, "shard internal count")
        require(shard["sector_start"] == row["sector_start"] == len(sectors), "shard sector start")
        require(shard["sector_end"] == row["sector_end"], "shard sector end")
        sectors.extend(shard["sectors"])
        require(len(sectors) == row["sector_end"], "shard sector coverage")
    require(digest(sectors) == stored["open_sector_lift"]["sectors_sha256"], "full sector digest")
    require(len(sectors) == 1_694, "sector count")
    dyadic_exponent = stored["open_sector_lift"]["dyadic_endpoint_exponent"]
    require(dyadic_exponent == 48, "dyadic endpoint exponent")
    dyadic_denominator = 2**dyadic_exponent
    specialization_census = Counter()
    sector_census = Counter()
    total_roots = 0
    minimum_gap = None
    maximum_span_numerator = 0

    for sector_id, (sector, sample) in enumerate(zip(sectors, expected_samples, strict=True)):
        entries_by_factor = {base_id: [] for base_id in range(len(base_polynomials))}
        parsed = []
        for entry in sector:
            require(len(entry) == 3, "wrong root row shape")
            base_id, left_numerator, right_numerator = entry
            require(0 <= base_id < len(base_polynomials), "base factor ID")
            require(0 < left_numerator < right_numerator < dyadic_denominator, "bad dyadic endpoint")
            left = Fraction(left_numerator, dyadic_denominator)
            right = Fraction(right_numerator, dyadic_denominator)
            require(0 < left <= right < 1, "u root outside open interval")
            entries_by_factor[base_id].append((left, right))
            parsed.append((left_numerator, right_numerator, base_id))
        require(parsed == sorted(parsed), f"unordered root stack at sector {sector_id}")
        for (_left, right, _base_id), (next_left, _next_right, _next_base_id) in zip(parsed, parsed[1:]):
            require(right <= next_left, f"overlapping root stack at sector {sector_id}")
            gap = next_left - right
            minimum_gap = gap if minimum_gap is None else min(minimum_gap, gap)

        observed_sector_roots = 0
        for base_id, polynomial in enumerate(base_polynomials):
            specialized = specialize_in_t(polynomial, sample)
            require(evaluate(specialized, 0) != 0, "u=0 sample root")
            require(evaluate(specialized, 1) != 0, "u=1 sample root")
            sequence = sturm_sequence(specialized)
            full_count = roots_between(sequence, Fraction(0), Fraction(1))
            entries = entries_by_factor[base_id]
            require(entries == sorted(entries), "within-factor root order")
            require(len(entries) == full_count, f"incomplete roots at sector {sector_id} factor {base_id}")
            for left, right in entries:
                require(roots_between(sequence, left, right) == 1, "u interval does not isolate one root")
                maximum_span_numerator = max(
                    maximum_span_numerator,
                    (right - left).numerator * dyadic_denominator // (right - left).denominator,
                )
            specialization_census[full_count] += 1
            observed_sector_roots += full_count
        require(observed_sector_roots == len(parsed), "sector root total")
        sector_census[observed_sector_roots] += 1
        total_roots += observed_sector_roots

    lift = stored["open_sector_lift"]
    require({str(k): v for k, v in sorted(specialization_census.items())} == lift["specialization_interior_root_count_census"], "specialization census")
    require({str(k): v for k, v in sorted(sector_census.items())} == lift["sector_root_count_census"], "sector census")
    observed = {
        "base_semantic": base["semantic_sha256"],
        "root_semantic": roots["semantic_sha256"],
        "boundary_digest": digest(boundary_rows),
        "minimum_gap": str(Fraction(minimum_gap, dyadic_denominator)),
        "maximum_span_numerator": maximum_span_numerator,
        "maximum_width": str(Fraction(maximum_span_numerator, dyadic_denominator)),
        "sectors_digest": digest(sectors),
        "semantic": digest(
            {
                "base_semantic_sha256": base["semantic_sha256"],
                "root_isolation_semantic_sha256": roots["semantic_sha256"],
                "right_boundary_factorizations": boundary_rows,
                "sectors_sha256": digest(sectors),
            }
        ),
    }
    validate_claims(stored, observed)

    mutations = (
        (("status",), "OPEN"),
        (("scope", "bounded_u_boundary_projection_audit"), "PARTIAL"),
        (("scope", "open_t_sector_base_lift"), "PARTIAL"),
        (("scope", "algebraic_t_section_base_lift"), "COMPLETE"),
        (("scope", "honest_9dvl_score"), "3/9"),
        (("source", "base_projection_semantic_sha256"), "0" * 64),
        (("bounded_u_boundary_audit", "all_factors_present_in_second_projection_catalog"), False),
        (("open_sector_lift", "open_t_sectors"), 1_693),
        (("open_sector_lift", "open_sector_u_root_sections"), 132_133),
        (("open_sector_lift", "sectors_sha256"), "0" * 64),
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
    require(rejected == len(mutations), "a hostile open-sector mutation survived")

    print("PASS bounded u=1 audit: all 28 nonconstant evaluations factor through the projection catalog")
    print("PASS 193116 specialized base factors over all 1694 open t sectors")
    print("PASS 132134 ordered u-root sections + 133828 strips = 265962 open-sector base cells")
    print("PASS standard-library Sturm coverage and rational interval order in every sector")
    print(f"PASS {rejected}/{len(mutations)} hostile mutations rejected")
    print("SCOPE open t sectors only; algebraic t-section fibers and global pair complex remain open; honest 9DVL 2/9")


if __name__ == "__main__":
    main()
