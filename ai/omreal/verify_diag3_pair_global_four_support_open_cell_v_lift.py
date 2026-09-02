#!/usr/bin/env python3
"""Standard-library replay of the open-base-cell v-lift certificate."""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from math import gcd, lcm
from pathlib import Path


HERE = Path(__file__).resolve().parent
PROJECTION = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_PROJECTION.json"
BASE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz"
ROOTS = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ROOT_ISOLATION.json.gz"
OPEN = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT.json"
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_CELL_V_LIFT.json"
FORMAT = "diag3-pair-global-row2599-four-support-open-cell-v-lift-v1"
SHARD_FORMAT = "diag3-pair-global-row2599-four-support-open-cell-v-lift-shard-v1"
OPEN_SHARD_FORMAT = "diag3-pair-global-row2599-four-support-open-sector-lift-shard-v1"
PROJECTION_FORMAT = "diag3-pair-global-row2599-four-support-projection-v1"
BASE_FORMAT = "diag3-pair-global-row2599-four-support-base-projection-v1"
ROOT_FORMAT = "diag3-pair-global-row2599-four-support-root-isolation-v1"
OPEN_FORMAT = "diag3-pair-global-row2599-four-support-open-sector-lift-v1"
SHARD_COUNT = 32
SECTOR_COUNT = 1_694
THEOREM_EFFECT = (
    "Every full-dimensional base cell over the 1694 open t sectors has a complete "
    "exact ordered v-root stack for all 22 walls; algebraic u-section fibers, "
    "algebraic t-section fibers, global gluing, labels, middle-rank replay, and "
    "the diagonal-three invariant remain open; honest 9DVL score remains 2/9."
)
NEXT_STAGE = (
    "lift the 132134 algebraic u-section fibers over open t sectors, then lift "
    "every algebraic t-section base cell"
)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def canonical_gzip_json(value):
    encoded = (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode(
        "ascii"
    )
    compressed = bytearray(gzip.compress(encoded, compresslevel=9, mtime=0))
    # zlib stamps byte 9 per host; these fixtures canonically pin the Unix value.
    compressed[9] = 0x03
    require(
        compressed[:10] == b"\x1f\x8b\x08\x00\x00\x00\x00\x00\x02\x03",
        "unexpected canonical gzip header",
    )
    return bytes(compressed)


def trim_multivariate(polynomial):
    return {exponent: value for exponent, value in polynomial.items() if value}


def multiply_multivariate(left, right):
    answer = Counter()
    for left_exponent, left_value in left.items():
        for right_exponent, right_value in right.items():
            exponent = tuple(a + b for a, b in zip(left_exponent, right_exponent))
            answer[exponent] += left_value * right_value
    return trim_multivariate(answer)


def canonical_multivariate(polynomial):
    polynomial = trim_multivariate({key: Fraction(value) for key, value in polynomial.items()})
    require(polynomial, "zero polynomial has no canonical form")
    denominator = 1
    for value in polynomial.values():
        denominator = lcm(denominator, value.denominator)
    integers = {key: int(value * denominator) for key, value in polynomial.items()}
    content = 0
    for value in integers.values():
        content = gcd(content, abs(value))
    integers = {key: value // content for key, value in integers.items()}
    first = sorted(integers, reverse=True)[0]
    if integers[first] < 0:
        integers = {key: -value for key, value in integers.items()}
    return tuple(sorted(integers.items()))


def parse_rows(rows, dimension):
    return {
        tuple(row["exponent"]): Fraction(row["coefficient"])
        for row in rows
        if Fraction(row["coefficient"])
    }


def parse_wall(row):
    coefficients = {}
    for term in row["polynomial"]:
        degree_u, degree_t, degree_v = term["exponent"]
        coefficients.setdefault(degree_v, []).append(
            (degree_u, degree_t, Fraction(term["coefficient"]))
        )
    return row["id"], row["fiber_degree"], coefficients


def evaluate_bivariate(terms, value_u, value_t):
    return sum(
        coefficient * value_u**degree_u * value_t**degree_t
        for degree_u, degree_t, coefficient in terms
    )


def compare_quadratic_root_to_rational(a, b, c, branch, value):
    require(a > 0 and b * b - 4 * a * c > 0, "bad quadratic comparison")
    vertex = -b / (2 * a)
    at_value = a * value * value + b * value + c
    if branch == 1:
        if value >= vertex:
            return -1
        if at_value == 0:
            return 0
        return -1 if at_value < 0 else 1
    require(branch == 2, "bad quadratic branch")
    if value <= vertex:
        return 1
    if at_value == 0:
        return 0
    return -1 if at_value > 0 else 1


def ordered_signature(walls, value_u, value_t):
    roots = []
    for wall_id, degree, coefficients in walls:
        values = {
            power: evaluate_bivariate(terms, value_u, value_t)
            for power, terms in coefficients.items()
        }
        if degree == 0:
            require(values.get(0, 0) != 0, "base-only wall on open cell")
            continue
        if degree == 1:
            leading = values.get(1, 0)
            constant = values.get(0, 0)
            require(leading != 0, "linear degree drop on open cell")
            root = -constant / leading
            require(root not in (0, 1), "linear v-boundary root on open cell")
            if 0 < root < 1:
                roots.append(("linear", wall_id, 0, root))
            continue
        a, b, c = values.get(2, 0), values.get(1, 0), values.get(0, 0)
        require(a != 0, "quadratic degree drop on open cell")
        if a < 0:
            a, b, c = -a, -b, -c
        discriminant = b * b - 4 * a * c
        require(discriminant != 0, "quadratic double root on open cell")
        if discriminant < 0:
            continue
        for branch in (1, 2):
            at_zero = compare_quadratic_root_to_rational(a, b, c, branch, Fraction(0))
            at_one = compare_quadratic_root_to_rational(a, b, c, branch, Fraction(1))
            require(at_zero and at_one, "quadratic v-boundary root on open cell")
            if at_zero > 0 and at_one < 0:
                roots.append(("quadratic", wall_id, branch, a, b, c))

    def less(left, right):
        if left[0] == right[0] == "linear":
            require(left[3] != right[3], "linear collision on open cell")
            return left[3] < right[3]
        if left[0] == "quadratic" and right[0] == "linear":
            comparison = compare_quadratic_root_to_rational(
                left[3], left[4], left[5], left[2], right[3]
            )
            require(comparison, "linear/quadratic collision on open cell")
            return comparison < 0
        if left[0] == "linear" and right[0] == "quadratic":
            comparison = compare_quadratic_root_to_rational(
                right[3], right[4], right[5], right[2], left[3]
            )
            require(comparison, "linear/quadratic collision on open cell")
            return comparison > 0
        require(left[1] == right[1], "two quadratic walls appeared")
        return left[2] < right[2]

    ordered = []
    for root in roots:
        index = 0
        while index < len(ordered) and not less(root, ordered[index]):
            index += 1
        ordered.insert(index, root)
    return tuple((root[1], root[2]) for root in ordered)


def sector_samples(root_record):
    sections = [
        (Fraction(row["left"]), Fraction(row["right"]))
        for row in root_record["root_isolation"]["sections"]
    ]
    return (
        [sections[0][0] / 2]
        + [(a[1] + b[0]) / 2 for a, b in zip(sections, sections[1:])]
        + [(sections[-1][1] + 1) / 2]
    )


def load_source_sectors(open_record):
    manifest = open_record["artifact_shards"]
    require(manifest["format"] == OPEN_SHARD_FORMAT, "source shard format")
    require(manifest["shard_count"] == SHARD_COUNT, "source shard count")
    rows = manifest["shards"]
    require(len(rows) == SHARD_COUNT, "source shard row count")
    require([row["index"] for row in rows] == list(range(SHARD_COUNT)), "source shard IDs")
    sectors = []
    for index, row in enumerate(rows):
        sector_start = SECTOR_COUNT * index // SHARD_COUNT
        sector_end = SECTOR_COUNT * (index + 1) // SHARD_COUNT
        expected_name = (
            "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT_"
            f"SHARD_{index:02d}_OF_{SHARD_COUNT}.json.gz"
        )
        require(row["path"] == expected_name, "source shard path")
        require(row["sector_start"] == sector_start, "source shard manifest start")
        require(row["sector_end"] == sector_end, "source shard manifest end")
        compressed = (OPEN.parent / expected_name).read_bytes()
        require(len(compressed) == row["bytes"], "source shard bytes")
        require(sha256(compressed).hexdigest() == row["sha256"], "source shard digest")
        shard = json.loads(gzip.decompress(compressed))
        require(canonical_gzip_json(shard) == compressed, "source shard is not canonical gzip JSON")
        require(shard["format"] == OPEN_SHARD_FORMAT, "source shard internal format")
        require(shard["shard_index"] == index, "source shard internal ID")
        require(shard["shard_count"] == SHARD_COUNT, "source shard internal count")
        require(shard["sector_start"] == sector_start == len(sectors), "source shard start")
        require(shard["sector_end"] == sector_end, "source shard end")
        sectors.extend(shard["sectors"])
        require(len(sectors) == sector_end, "source shard coverage")
    require(len(sectors) == SECTOR_COUNT, "source sector coverage")
    require(digest(sectors) == open_record["open_sector_lift"]["sectors_sha256"], "source sector digest")
    return sectors


def load_result_sector_ids(stored):
    manifest = stored["artifact_shards"]
    require(manifest["format"] == SHARD_FORMAT, "bad result shard format")
    require(manifest["shard_count"] == SHARD_COUNT, "bad result shard count")
    rows = manifest["shards"]
    require(len(rows) == SHARD_COUNT, "result shard row count")
    require([row["index"] for row in rows] == list(range(SHARD_COUNT)), "result shard IDs")
    sector_ids = []
    for index, row in enumerate(rows):
        sector_start = SECTOR_COUNT * index // SHARD_COUNT
        sector_end = SECTOR_COUNT * (index + 1) // SHARD_COUNT
        expected_name = (
            "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_CELL_V_LIFT_"
            f"SHARD_{index:02d}_OF_{SHARD_COUNT}.json.gz"
        )
        require(row["path"] == expected_name, "result shard path")
        require(row["sector_start"] == sector_start, "result shard manifest start")
        require(row["sector_end"] == sector_end, "result shard manifest end")
        compressed = (CERTIFICATE.parent / expected_name).read_bytes()
        require(len(compressed) == row["bytes"], "result shard bytes")
        require(sha256(compressed).hexdigest() == row["sha256"], "result shard digest")
        shard = json.loads(gzip.decompress(compressed))
        require(canonical_gzip_json(shard) == compressed, "result shard is not canonical gzip JSON")
        require(shard["format"] == SHARD_FORMAT, "result shard internal format")
        require(shard["shard_index"] == index, "result shard internal ID")
        require(shard["shard_count"] == SHARD_COUNT, "result shard internal count")
        require(shard["sector_start"] == sector_start == len(sector_ids), "result shard start")
        require(shard["sector_end"] == sector_end, "result shard end")
        sector_ids.extend(shard["strip_signature_ids"])
        require(len(sector_ids) == sector_end, "result shard coverage")
    require(len(sector_ids) == SECTOR_COUNT, "result sector signature coverage")
    return sector_ids, deepcopy(manifest)


def open_strip_samples(stack, denominator):
    if not stack:
        return [Fraction(1, 2)]
    return (
        [Fraction(stack[0][1], 2 * denominator)]
        + [
            Fraction(left[2] + right[1], 2 * denominator)
            for left, right in zip(stack, stack[1:])
        ]
        + [Fraction(stack[-1][2] + denominator, 2 * denominator)]
    )


def endpoint_polynomial(wall, endpoint):
    answer = Counter()
    for term in wall["polynomial"]:
        degree_u, degree_t, degree_v = term["exponent"]
        answer[(degree_u, degree_t)] += Fraction(term["coefficient"]) * endpoint**degree_v
    return trim_multivariate(answer)


def replay_endpoint_factorizations(projection, base, stored):
    walls = projection["fiber_walls"]["catalog"]
    base_polynomials = [
        parse_rows(row["polynomial"], 2)
        for row in base["base_factorization"]["catalog"]
    ]
    t_polynomials = [
        {(0, degree): Fraction(value) for degree, value in enumerate(row["coefficients_low_to_high"]) if value}
        for row in base["second_projection"]["catalog"]
    ]
    boundary = {
        "u=0": {(1, 0): Fraction(1)},
        "u=1": {(0, 0): Fraction(-1), (1, 0): Fraction(1)},
        "t=0": {(0, 1): Fraction(1)},
        "t=1": {(0, 0): Fraction(-1), (0, 1): Fraction(1)},
    }
    rows = stored["v_endpoint_audit"]["factorizations"]
    require(len(rows) == 44, "endpoint factorization count")
    by_key = {(row["wall_id"], row["endpoint"]): row for row in rows}
    require(len(by_key) == 44, "duplicate endpoint factorization")
    for wall in walls:
        for endpoint in (0, 1):
            row = by_key[(wall["id"], endpoint)]
            product = {(0, 0): Fraction(1)}
            for name, multiplicity in row["boundary_factors"].items():
                require(name in boundary and multiplicity > 0, "bad boundary factor")
                for _ in range(multiplicity):
                    product = multiply_multivariate(product, boundary[name])
            for factor_id, multiplicity in row["base_factors"]:
                require(0 <= factor_id < len(base_polynomials) and multiplicity > 0, "bad base factor")
                for _ in range(multiplicity):
                    product = multiply_multivariate(product, base_polynomials[factor_id])
            for factor_id, multiplicity in row["t_factors"]:
                require(0 <= factor_id < len(t_polynomials) and multiplicity > 0, "bad t factor")
                for _ in range(multiplicity):
                    product = multiply_multivariate(product, t_polynomials[factor_id])
            expected = endpoint_polynomial(wall, endpoint)
            require(expected, "zero endpoint polynomial")
            require(canonical_multivariate(product) == canonical_multivariate(expected), "endpoint factorization failed")
    return rows


def validate_claims(candidate, observed):
    require(candidate["format"] == FORMAT and candidate["status"] == "PROVED", "bad certificate header")
    scope = candidate["scope"]
    require(scope["v_endpoint_projection_audit"] == "COMPLETE", "endpoint scope")
    require(scope["open_t_open_u_base_cell_v_lift"] == "COMPLETE_BY_PROJECTION_INVARIANCE", "open-cell scope")
    require(scope["open_t_algebraic_u_section_v_lift"] == "NOT_YET_CONSTRUCTED", "false u-section claim")
    require(scope["algebraic_t_section_v_lift"] == "NOT_YET_CONSTRUCTED", "false t-section claim")
    require(scope["global_gluing_and_closure_data"] == "NOT_CLAIMED", "false global claim")
    require(scope["honest_9dvl_score"] == "2/9", "dishonest score")
    source = candidate["source"]
    require(source["projection_semantic_sha256"] == observed["projection_semantic"], "projection source")
    require(source["base_projection_semantic_sha256"] == observed["base_semantic"], "base source")
    require(source["root_isolation_semantic_sha256"] == observed["root_semantic"], "root source")
    require(source["open_sector_lift_semantic_sha256"] == observed["open_semantic"], "open source")
    require(source["fiber_wall_count"] == observed["fiber_wall_count"] == 22, "source wall count")
    require(source["open_t_sectors"] == observed["open_t_sectors"] == SECTOR_COUNT, "source sector count")
    require(source["open_u_strips"] == observed["open_u_strips"] == 133_828, "source strip count")
    endpoint = candidate["v_endpoint_audit"]
    require(endpoint["endpoint_evaluations"] == len(endpoint["factorizations"]) == 44, "endpoint count")
    require(endpoint["all_nonboundary_factors_present_in_base_or_t_projection"] is True, "endpoint coverage")
    require(endpoint["factorizations_sha256"] == observed["endpoint_digest"], "endpoint digest claim")
    require(digest(endpoint["factorizations"]) == observed["endpoint_digest"], "endpoint rows digest")
    lift = candidate["open_cell_v_lift"]
    require(lift["open_base_cells"] == observed["open_u_strips"] == 133_828, "open-cell count")
    require(lift["distinct_fiber_order_signatures"] == observed["signature_count"], "signature count")
    require(lift["minimum_interior_v_roots"] == observed["minimum_roots"], "minimum roots")
    require(lift["maximum_interior_v_roots"] == observed["maximum_roots"], "maximum roots")
    require(lift["interior_v_root_census"] == observed["root_census"], "root census")
    require(lift["interior_v_root_sections"] == observed["total_roots"], "root total")
    require(lift["open_v_strips"] == observed["open_v_strips"], "v-strip total")
    require(lift["lifted_cells"] == observed["lifted_cells"], "lifted-cell total")
    require(lift["wall_root_instance_census"] == observed["wall_census"], "wall census")
    require(lift["signature_catalog_sha256"] == observed["signature_digest"], "signature digest claim")
    require(digest(lift["signature_catalog"]) == observed["signature_digest"], "signature catalog digest")
    require(lift["sector_signature_ids_sha256"] == observed["sector_digest"], "sector digest")
    require(candidate["artifact_shards"] == observed["artifact_manifest"], "artifact shard manifest")
    require(candidate["semantic_sha256"] == observed["semantic"], "semantic digest")
    resource = candidate["resource_effect"]
    require(resource["open_cell_lift_ceiling"] == 20_000_000, "resource ceiling value")
    require(resource["actual_lifted_cells"] == observed["lifted_cells"], "resource cell count")
    require(resource["ceiling_not_triggered"] is True, "resource ceiling status")
    require(resource["next_stage"] == NEXT_STAGE, "resource next stage")
    require(
        candidate["generator_dependency"]["independent_verifier"]
        == "STANDARD_LIBRARY_EXACT_RATIONAL_REPLAY",
        "independent verifier claim",
    )
    require(candidate["theorem_effect"] == THEOREM_EFFECT, "theorem effect")


def main():
    projection = json.loads(PROJECTION.read_bytes())
    base = json.loads(gzip.decompress(BASE.read_bytes()))
    roots = json.loads(gzip.decompress(ROOTS.read_bytes()))
    open_record = json.loads(OPEN.read_bytes())
    stored = json.loads(CERTIFICATE.read_bytes())
    require(projection["format"] == PROJECTION_FORMAT, "bad projection format")
    require(base["format"] == BASE_FORMAT, "bad base format")
    require(roots["format"] == ROOT_FORMAT, "bad roots format")
    require(open_record["format"] == OPEN_FORMAT, "bad open-sector format")
    require(
        projection["status"] == base["status"] == roots["status"] == open_record["status"] == "PROVED",
        "bad source status",
    )
    require(base["source"]["semantic_sha256"] == projection["semantic_sha256"], "projection/base source chain")
    require(roots["source"]["semantic_sha256"] == base["semantic_sha256"], "base/roots source chain")
    require(
        open_record["source"]["base_projection_semantic_sha256"] == base["semantic_sha256"],
        "base/open source chain",
    )
    require(
        open_record["source"]["root_isolation_semantic_sha256"] == roots["semantic_sha256"],
        "roots/open source chain",
    )
    require(len(projection["fiber_walls"]["catalog"]) == 22, "source wall catalog count")
    require(open_record["open_sector_lift"]["open_t_sectors"] == SECTOR_COUNT, "source open-sector count")
    require(open_record["open_sector_lift"]["open_sector_u_strips"] == 133_828, "source open-strip count")
    endpoint_rows = replay_endpoint_factorizations(projection, base, stored)

    catalog = [tuple(map(tuple, signature)) for signature in stored["open_cell_v_lift"]["signature_catalog"]]
    require(catalog == sorted(set(catalog)), "signature catalog is not canonical")
    sector_ids, artifact_manifest = load_result_sector_ids(stored)

    sectors = load_source_sectors(open_record)
    samples_t = sector_samples(roots)
    require(len(sectors) == len(samples_t) == SECTOR_COUNT, "source sample count")
    denominator = 2 ** open_record["open_sector_lift"]["dyadic_endpoint_exponent"]
    walls = [parse_wall(row) for row in projection["fiber_walls"]["catalog"]]
    root_census = Counter()
    wall_census = Counter()
    total_roots = 0
    replayed_ids = []
    for sector_id, (stack, sample_t, expected_ids) in enumerate(
        zip(sectors, samples_t, sector_ids, strict=True)
    ):
        current = []
        samples_u = open_strip_samples(stack, denominator)
        require(len(expected_ids) == len(samples_u), "strip signature count")
        for sample_u, expected_id in zip(samples_u, expected_ids, strict=True):
            signature = ordered_signature(walls, sample_u, sample_t)
            require(0 <= expected_id < len(catalog), "signature ID")
            require(signature == catalog[expected_id], "fiber signature mismatch")
            current.append(expected_id)
            root_census[len(signature)] += 1
            wall_census.update(wall_id for wall_id, _branch in signature)
            total_roots += len(signature)
        replayed_ids.append(current)
        if sector_id % 200 == 0:
            print("PASS SECTOR", sector_id, "STRIPS", len(current), flush=True)

    open_cells = sum(len(row) for row in replayed_ids)
    open_v_strips = total_roots + open_cells
    lifted_cells = total_roots + open_v_strips
    require(
        {str(k): v for k, v in sorted(wall_census.items())}
        == stored["open_cell_v_lift"]["wall_root_instance_census"],
        "wall census",
    )
    semantic_payload = {
        "projection_semantic_sha256": projection["semantic_sha256"],
        "base_projection_semantic_sha256": base["semantic_sha256"],
        "root_isolation_semantic_sha256": roots["semantic_sha256"],
        "open_sector_lift_semantic_sha256": open_record["semantic_sha256"],
        "endpoint_factorizations": endpoint_rows,
        "signature_catalog": catalog,
        "sector_signature_ids_sha256": digest(replayed_ids),
    }
    observed = {
        "projection_semantic": projection["semantic_sha256"],
        "base_semantic": base["semantic_sha256"],
        "root_semantic": roots["semantic_sha256"],
        "open_semantic": open_record["semantic_sha256"],
        "fiber_wall_count": len(walls),
        "open_t_sectors": len(sectors),
        "open_u_strips": open_cells,
        "endpoint_digest": digest(endpoint_rows),
        "signature_count": len(catalog),
        "minimum_roots": min(root_census),
        "maximum_roots": max(root_census),
        "root_census": {str(k): v for k, v in sorted(root_census.items())},
        "total_roots": total_roots,
        "open_v_strips": open_v_strips,
        "lifted_cells": lifted_cells,
        "wall_census": {str(k): v for k, v in sorted(wall_census.items())},
        "signature_digest": digest(catalog),
        "sector_digest": digest(replayed_ids),
        "artifact_manifest": artifact_manifest,
        "semantic": digest(semantic_payload),
    }
    validate_claims(stored, observed)

    mutations = (
        (("status",), "OPEN"),
        (("scope", "v_endpoint_projection_audit"), "PARTIAL"),
        (("scope", "open_t_open_u_base_cell_v_lift"), "PARTIAL"),
        (("scope", "open_t_algebraic_u_section_v_lift"), "COMPLETE"),
        (("scope", "algebraic_t_section_v_lift"), "COMPLETE"),
        (("scope", "global_gluing_and_closure_data"), "COMPLETE"),
        (("scope", "honest_9dvl_score"), "3/9"),
        (("source", "projection_semantic_sha256"), "0" * 64),
        (("source", "base_projection_semantic_sha256"), "0" * 64),
        (("source", "root_isolation_semantic_sha256"), "0" * 64),
        (("source", "open_sector_lift_semantic_sha256"), "0" * 64),
        (("source", "fiber_wall_count"), 21),
        (("source", "open_t_sectors"), 1_693),
        (("source", "open_u_strips"), 133_827),
        (("v_endpoint_audit", "endpoint_evaluations"), 43),
        (("v_endpoint_audit", "all_nonboundary_factors_present_in_base_or_t_projection"), False),
        (("v_endpoint_audit", "factorizations_sha256"), "0" * 64),
        (("v_endpoint_audit", "factorizations"), []),
        (("open_cell_v_lift", "open_base_cells"), 133_827),
        (("open_cell_v_lift", "distinct_fiber_order_signatures"), len(catalog) - 1),
        (("open_cell_v_lift", "minimum_interior_v_roots"), min(root_census) - 1),
        (("open_cell_v_lift", "maximum_interior_v_roots"), max(root_census) + 1),
        (("open_cell_v_lift", "interior_v_root_census"), {}),
        (("open_cell_v_lift", "interior_v_root_sections"), total_roots - 1),
        (("open_cell_v_lift", "open_v_strips"), open_v_strips - 1),
        (("open_cell_v_lift", "lifted_cells"), lifted_cells - 1),
        (("open_cell_v_lift", "wall_root_instance_census"), {}),
        (("open_cell_v_lift", "signature_catalog_sha256"), "0" * 64),
        (("open_cell_v_lift", "signature_catalog"), []),
        (("open_cell_v_lift", "sector_signature_ids_sha256"), "0" * 64),
        (("artifact_shards", "shard_count"), 31),
        (("artifact_shards", "shards"), artifact_manifest["shards"][:-1]),
        (("artifact_shards", "shards", 0, "path"), "wrong.json.gz"),
        (("semantic_sha256",), "0" * 64),
        (("resource_effect", "open_cell_lift_ceiling"), 19_999_999),
        (("resource_effect", "actual_lifted_cells"), lifted_cells - 1),
        (("resource_effect", "ceiling_not_triggered"), False),
        (("resource_effect", "next_stage"), "COMPLETE"),
        (("generator_dependency", "independent_verifier"), "UNVERIFIED"),
        (("theorem_effect",), "The pair obligation is complete."),
    )
    rejected = 0
    for path, value in mutations:
        candidate = deepcopy(stored)
        target = candidate
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            validate_claims(candidate, observed)
        except AssertionError:
            rejected += 1
    require(rejected == len(mutations), "hostile mutation survived")

    print("PASS 44 v-endpoint factorizations through the bounded base/t projection")
    print("PASS 133828 open base cells over all 1694 open t sectors")
    print("PASS", len(catalog), "exact ordered fiber signatures")
    print("PASS", total_roots, "v-root sections +", open_v_strips, "v-strips =", lifted_cells, "lifted cells")
    print(f"PASS {rejected}/{len(mutations)} hostile mutations rejected")
    print("REMAINING 132134 algebraic u-section fibers plus every algebraic t-section base cell")
    print("SCOPE honest 9DVL score 2/9")


if __name__ == "__main__":
    main()
