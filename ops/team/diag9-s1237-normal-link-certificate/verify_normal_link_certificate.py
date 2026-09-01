#!/usr/bin/env python3
"""Producer-independent contract and replay for the D9 S12,37 normal link.

The shipped certificate is deliberately an incomplete template.  With no
arguments this program pins the sources, independently rebuilds the complete
3,539-class oriented literal census, proves that the template is rejected,
and runs hostile structural-kernel self tests.  ``--certificate PATH`` is the
acceptance entry point for a producer payload; it fails closed on every
missing artifact or unsupported witness kind.

This checker proves no collar, topology, global coverage, or theorem-ledger
claim.  Its acceptance scope is exactly D9_S1237_4SUPPORT_NORMAL_LINK_GATE1.
"""

from __future__ import annotations

import argparse
import contextlib
import copy
from fractions import Fraction
import hashlib
from io import StringIO
import itertools
import json
from pathlib import Path
import sys
from typing import Any, Iterable

import numpy as np


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[2]
OMREAL = REPOSITORY / "ai" / "omreal"
DATA = OMREAL / "data"
SOURCE_MANIFEST = HERE / "SOURCE_MANIFEST.json"
TEMPLATE = HERE / "NORMAL_LINK_CERTIFICATE.template.json"
SELF_TEST_FIXTURE = HERE / "SELF_TEST_FIXTURE.json"

FORMAT = "diag9-s1237-oriented-normal-link-certificate-v1"
TARGET = "D9_S1237_4SUPPORT_NORMAL_LINK_GATE1"
SOURCE_REVISION = "c55d896cc5c0370e993b793992a2f05d894e0095"
SOURCE_TREE = "17299e84397aae158a2111cbe01b52f5be24bfd5"
OPENING_COMMIT = "c6bd7a6afeda0888fc950710b941cac6f6c9bf95"
OPENING_TREE = "9c2dbe39a3ea0f36e9e9c8f845e6f72e98526421"
EXPECTED_ACTIVE_SECTOR_DIGEST = (
    "6de7ff2716b65853c04b9a08f44eb98ad8966e1f3525887ffafde0a3b805c154"
)
# Filled from the independent canonical stream below.  It deliberately does
# not reuse verify_diag9_active_sector.semantic_digest, whose domain is a
# different aggregate theorem record.
EXPECTED_LITERAL_CENSUS_DIGEST = (
    "a1b9d3d9da1e01df83621dc8f1c7959f86ae2e0d9bd3bc457124c561cbac245a"
)
EXPECTED_LITERAL_COUNT = 3_539
EXPECTED_OCCURRENCE_COUNT = 5_026
EXPECTED_UNIT_BRACKET_COUNT = 62
EXPECTED_PARENT_INEQUALITY_COUNT = 70

ENDPOINTS = {
    "COMPLETE_ORIENTED_NORMAL_LINK_GATE",
    "NORMAL_LINK_REDUCTION_NO_GO",
    "UNRESOLVED_NORMAL_LINK_STRATUM",
    "HASH_PINNED_NORMAL_LINK_FRONTIER",
}

PROHIBITED_CONSEQUENCES = [
    "TANGENTIAL_FILTER_IS_A_COLLAR",
    "BOUNDARY_FACES_GLUE_OPEN_X_COMPONENTS",
    "SAMPLED_LINK_COVERAGE_IS_COMPLETE",
    "GLOBAL_SEPARATOR_OR_ACTIVE_SECTOR_CONNECTIVITY",
    "DIAGONAL_9_PROOF_OR_COUNTEREXAMPLE",
    "THEOREM_LEDGER_PROMOTION",
]

SUPPORTS = {
    "S3115": {
        "support": [3, 1, 15],
        "normal_axes": [
            "c6_r3",
            "c6_r4",
            "c7_r2",
            "c7_r3",
            "c7_r4",
            "parent_transverse",
        ],
    },
    "S337": {
        "support": [3, 3, 7],
        "normal_axes": [
            "c6_r3",
            "c6_r4",
            "c7_r3",
            "c7_r4",
            "c8_r4",
            "parent_transverse",
        ],
    },
}

ARTIFACT_KEYS = {
    "literal_census",
    "normal_form_inventory",
    "recursive_strata",
    "link_sectors",
    "stabilization",
    "obstruction",
    "frontier",
}


class CertificateError(AssertionError):
    """A fail-closed contract or replay rejection."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CertificateError(message)


def exact_keys(value: Any, keys: set[str], context: str) -> None:
    require(isinstance(value, dict), f"{context}: expected object")
    require(set(value) == keys, f"{context}: wrong fields")


def is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def semantic_digest(domain: bytes, values: Iterable[Any]) -> str:
    digest = hashlib.sha256(domain + b"\0")
    for value in values:
        digest.update(canonical_json(value))
        digest.update(b"\n")
    return digest.hexdigest()


def safe_artifact_path(relative: Any) -> Path:
    require(isinstance(relative, str) and relative, "artifact path: empty")
    path = (HERE / relative).resolve()
    try:
        path.relative_to(HERE)
    except ValueError as error:
        raise CertificateError("artifact path escapes track directory") from error
    require(path.is_file(), f"artifact missing: {relative}")
    return path


def verify_source_manifest() -> dict:
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    exact_keys(
        manifest,
        {
            "format",
            "track_id",
            "target_id",
            "source_revision",
            "source_tree",
            "opening_commit",
            "opening_tree",
            "used_sha256",
            "trust_boundary",
            "scope_exclusions",
        },
        "source manifest",
    )
    require(manifest["format"] == "diag9-s1237-normal-link-source-manifest-v1", "source manifest: format")
    require(manifest["target_id"] == TARGET, "source manifest: target")
    require(manifest["source_revision"] == SOURCE_REVISION, "source manifest: revision")
    require(manifest["source_tree"] == SOURCE_TREE, "source manifest: tree")
    require(manifest["opening_commit"] == OPENING_COMMIT, "source manifest: opening commit")
    require(manifest["opening_tree"] == OPENING_TREE, "source manifest: opening tree")
    used = manifest["used_sha256"]
    require(isinstance(used, dict) and used, "source manifest: empty pins")
    for relative, expected in sorted(used.items()):
        require(is_sha256(expected), f"source manifest: malformed digest {relative}")
        path = (REPOSITORY / relative).resolve()
        try:
            path.relative_to(REPOSITORY)
        except ValueError as error:
            raise CertificateError("source manifest: escaping path") from error
        require(path.is_file(), f"source manifest: missing {relative}")
        require(sha256_path(path) == expected, f"source manifest: drift {relative}")
    return manifest


def _load_active_module():
    sys.path.insert(0, str(OMREAL))
    with contextlib.redirect_stdout(StringIO()):
        import verify_diag9_active_sector as active  # type: ignore
    return active


def rebuild_literal_census() -> tuple[list[dict], str, int]:
    """Rebuild every active class and occurrence from pinned repository data."""

    active = _load_active_module()
    active.verify_pins()
    certificates = active.transported_certificates()

    with np.load(DATA / "DIAG9_GRAPH_global_factor_census.npz", allow_pickle=False) as source:
        require(str(source["format"].item()) == "diag9-global-residual-factor-census-v1", "factor census: format")
        foursets_array = np.asarray(source["occurrence_fourset"], dtype=np.uint8)
        occurrence_factor = np.asarray(source["occurrence_factor"], dtype=np.uint32)
        factor_offsets = np.asarray(source["factor_offset"], dtype=np.uint32)
        factor_exponents = np.asarray(source["factor_exponent"], dtype=np.uint8)
        factor_coefficients = np.asarray(source["factor_coefficient"], dtype=np.int64)
        parent_bracket_label = np.asarray(source["parent_bracket_label"], dtype=np.uint8)
        unit_offsets = np.asarray(source["occurrence_unit_offset"], dtype=np.uint32)
        unit_indices = np.asarray(source["occurrence_unit_index"], dtype=np.uint8)

    foursets = tuple(tuple(map(int, row)) for row in foursets_array)
    require(foursets_array.shape == (84_840, 4), "factor census: occurrence shape")
    require(len(parent_bracket_label) == EXPECTED_UNIT_BRACKET_COUNT, "factor census: stripped unit bracket count")

    charts = np.load(DATA / "seeat_parent2599_upper178.npz", allow_pickle=False)["chart_matrix"]
    rows = active.topes.derived_rows(charts[0])
    oriented, conflicting_occurrences = active.oriented_occurrences(foursets, certificates, rows)
    empty_factors = {int(occurrence_factor[index]) for index in conflicting_occurrences}
    require(len(empty_factors) == 8_916, "literal census: empty factor count")

    factor_count = len(factor_offsets) - 1
    representative = np.full(factor_count, -1, dtype=np.int64)
    factor_occurrences: list[list[int]] = [[] for _ in range(factor_count)]
    for occurrence_index, factor in enumerate(map(int, occurrence_factor)):
        factor_occurrences[factor].append(occurrence_index)
        if representative[factor] < 0:
            representative[factor] = occurrence_index
    require(np.all(representative >= 0), "literal census: missing representative")
    representative_raw_sign = np.asarray(
        [oriented[index][1] for index in representative], dtype=np.int8
    )

    with np.load(DATA / "ninth_candidate_12_37_antichain.npz", allow_pickle=False) as antichain:
        signatures = tuple(map(int, antichain["signature"]))
    require(len(signatures) == 9, "literal census: family size")

    per_signature_literals: list[dict[int, int]] = []
    per_signature_occurrences: list[set[int]] = []
    per_occurrence_sides: list[list[tuple[int, int, int]]] = [[] for _ in foursets]
    for signature_index, signature in enumerate(signatures):
        literals: dict[int, int] = {}
        occurrences: set[int] = set()
        for occurrence_index, ((certificate_data, raw_sign), factor) in enumerate(
            zip(oriented, map(int, occurrence_factor), strict=True)
        ):
            if factor in empty_factors:
                continue
            allowed_raw = active.aligned_literal(signature, certificate_data)
            if allowed_raw is None:
                continue
            occurrences.add(occurrence_index)
            relative_unit_sign = raw_sign * int(representative_raw_sign[factor])
            allowed_representative = allowed_raw * relative_unit_sign
            previous = literals.setdefault(factor, allowed_representative)
            require(previous == allowed_representative, "literal census: within-signature orientation conflict")
            per_occurrence_sides[occurrence_index].append(
                (signature_index, int(allowed_raw), int(allowed_representative))
            )
        per_signature_literals.append(literals)
        per_signature_occurrences.append(occurrences)

    family_literals: dict[int, int] = {}
    active_signature_indices: dict[int, list[int]] = {}
    for signature_index, literals in enumerate(per_signature_literals):
        for factor, orientation in literals.items():
            previous = family_literals.setdefault(factor, orientation)
            require(previous == orientation, "literal census: family orientation conflict")
            active_signature_indices.setdefault(factor, []).append(signature_index)

    active_occurrence_union = set().union(*per_signature_occurrences)
    require(len(family_literals) == EXPECTED_LITERAL_COUNT, "literal census: active class count")
    require(len(active_occurrence_union) == EXPECTED_OCCURRENCE_COUNT, "literal census: active occurrence count")
    require(
        {int(occurrence_factor[index]) for index in active_occurrence_union} == set(family_literals),
        "literal census: class/occurrence mismatch",
    )

    records: list[dict] = []
    for factor in sorted(family_literals):
        start, stop = int(factor_offsets[factor]), int(factor_offsets[factor + 1])
        polynomial = [
            {
                "exponent": list(map(int, factor_exponents[index])),
                "coefficient": int(factor_coefficients[index]),
            }
            for index in range(start, stop)
        ]
        polynomial.sort(key=lambda row: row["exponent"])
        representative_index = int(representative[factor])
        occurrences = []
        for occurrence_index in factor_occurrences[factor]:
            unit_start, unit_stop = int(unit_offsets[occurrence_index]), int(unit_offsets[occurrence_index + 1])
            bracket_indices = list(map(int, unit_indices[unit_start:unit_stop]))
            raw_sign = int(oriented[occurrence_index][1])
            occurrences.append(
                {
                    "occurrence_index": occurrence_index,
                    "fourset": list(foursets[occurrence_index]),
                    "raw_sign_at_chart0": raw_sign,
                    "unit_bracket_indices": bracket_indices,
                    "unit_bracket_labels": [
                        list(map(int, parent_bracket_label[index])) for index in bracket_indices
                    ],
                    "unit_sign_to_representative": raw_sign * int(representative_raw_sign[factor]),
                    "aligned_family_sides": [
                        {
                            "signature_index": signature_index,
                            "allowed_raw_sign": allowed_raw,
                            "allowed_representative_sign": allowed_representative,
                        }
                        for signature_index, allowed_raw, allowed_representative in per_occurrence_sides[occurrence_index]
                    ],
                }
            )
        records.append(
            {
                "factor_id": factor,
                "allowed_representative_sign": int(family_literals[factor]),
                "active_signature_indices": active_signature_indices[factor],
                "primitive_factor": polynomial,
                "representative": {
                    "occurrence_index": representative_index,
                    "fourset": list(foursets[representative_index]),
                    "raw_sign_at_chart0": int(representative_raw_sign[factor]),
                },
                "occurrences": occurrences,
            }
        )

    digest = semantic_digest(b"9dvl-d9-s1237-literal-census-v1", records)
    return records, digest, len(active_occurrence_union)


def parse_fraction(value: Any, context: str) -> Fraction:
    require(isinstance(value, str) and value, f"{context}: rational string")
    try:
        answer = Fraction(value)
    except (ValueError, ZeroDivisionError) as error:
        raise CertificateError(f"{context}: invalid rational") from error
    require(str(answer) == value, f"{context}: noncanonical rational")
    return answer


def validate_polynomial(polynomial: Any, variable_count: int, context: str) -> dict[tuple[int, ...], Fraction]:
    require(isinstance(polynomial, list) and polynomial, f"{context}: empty polynomial")
    answer: dict[tuple[int, ...], Fraction] = {}
    previous: tuple[int, ...] | None = None
    for index, term in enumerate(polynomial):
        exact_keys(term, {"coefficient", "exponent"}, f"{context}[{index}]")
        exponent = term["exponent"]
        require(
            isinstance(exponent, list)
            and len(exponent) == variable_count
            and all(isinstance(value, int) and value >= 0 for value in exponent),
            f"{context}[{index}]: exponent",
        )
        exponent_tuple = tuple(exponent)
        require(previous is None or previous < exponent_tuple, f"{context}: term order/duplicate")
        previous = exponent_tuple
        coefficient = parse_fraction(term["coefficient"], f"{context}[{index}]")
        require(coefficient != 0, f"{context}[{index}]: zero coefficient")
        answer[exponent_tuple] = coefficient
    return answer


def polynomial_add(
    left: dict[tuple[int, ...], Fraction],
    right: dict[tuple[int, ...], Fraction],
) -> dict[tuple[int, ...], Fraction]:
    answer = dict(left)
    for exponent, coefficient in right.items():
        answer[exponent] = answer.get(exponent, Fraction(0)) + coefficient
        if answer[exponent] == 0:
            del answer[exponent]
    return answer


def polynomial_multiply(
    left: dict[tuple[int, ...], Fraction],
    right: dict[tuple[int, ...], Fraction],
) -> dict[tuple[int, ...], Fraction]:
    answer: dict[tuple[int, ...], Fraction] = {}
    for left_exponent, left_coefficient in left.items():
        for right_exponent, right_coefficient in right.items():
            exponent = tuple(
                first + second
                for first, second in zip(left_exponent, right_exponent, strict=True)
            )
            answer[exponent] = answer.get(exponent, Fraction(0)) + left_coefficient * right_coefficient
            if answer[exponent] == 0:
                del answer[exponent]
    return answer


def polynomial_power(
    polynomial: dict[tuple[int, ...], Fraction], power: int, variable_count: int
) -> dict[tuple[int, ...], Fraction]:
    answer = {(0,) * variable_count: Fraction(1)}
    base = polynomial
    exponent = power
    while exponent:
        if exponent & 1:
            answer = polynomial_multiply(answer, base)
        exponent >>= 1
        if exponent:
            base = polynomial_multiply(base, base)
    return answer


def polynomial_compose(
    source: dict[tuple[int, ...], Fraction],
    substitution: list[dict[tuple[int, ...], Fraction]],
    variable_count: int,
) -> dict[tuple[int, ...], Fraction]:
    answer: dict[tuple[int, ...], Fraction] = {}
    powers: dict[tuple[int, int], dict[tuple[int, ...], Fraction]] = {}
    for source_exponent, source_coefficient in source.items():
        term = {(0,) * variable_count: source_coefficient}
        for axis, power in enumerate(source_exponent):
            if not power:
                continue
            key = (axis, power)
            if key not in powers:
                powers[key] = polynomial_power(substitution[axis], power, variable_count)
            term = polynomial_multiply(term, powers[key])
        answer = polynomial_add(answer, term)
    return answer


def source_polynomial_digest(polynomial: dict[tuple[int, ...], Fraction]) -> str:
    rows = [
        {"exponent": list(exponent), "coefficient": str(coefficient)}
        for exponent, coefficient in sorted(polynomial.items())
    ]
    return sha256_bytes(b"9dvl-d9-source-polynomial-v1\0" + canonical_json(rows))


def literal_source_polynomials(records: list[dict]) -> dict[int, tuple[dict[tuple[int, ...], Fraction], int]]:
    answer = {}
    for record in records:
        polynomial = {
            tuple(term["exponent"]): Fraction(term["coefficient"])
            for term in record["primitive_factor"]
        }
        answer[record["factor_id"]] = (polynomial, record["allowed_representative_sign"])
    return answer


def parent_source_polynomials() -> dict[int, tuple[dict[tuple[int, ...], Fraction], int]]:
    sys.path.insert(0, str(OMREAL))
    with contextlib.redirect_stdout(StringIO()):
        import verify_diag3_pair_global_parent_face_gate as gate  # type: ignore
    records = [json.loads(line) for line in gate.CATALOG.read_text().splitlines() if line]
    parents, _digest = gate.parent_polynomials(records[gate.PARENT])
    require(len(parents) == EXPECTED_PARENT_INEQUALITY_COUNT, "parent sources: inequality count")
    return {
        index: (
            {tuple(map(int, exponent)): Fraction(coefficient) for exponent, coefficient in polynomial.items()},
            int(target),
        )
        for index, (_label, target, polynomial, _terms) in enumerate(parents)
    }


def evaluate_polynomial(polynomial: dict[tuple[int, ...], Fraction], point: list[Fraction]) -> Fraction:
    return sum(
        coefficient
        * np.prod([point[index] ** power for index, power in enumerate(exponent)], dtype=object)
        for exponent, coefficient in polynomial.items()
    )


def validate_artifact_ref(record: Any, name: str, required: bool) -> tuple[Path, dict | list] | None:
    if record is None:
        require(not required, f"artifacts.{name}: required")
        return None
    exact_keys(record, {"path", "sha256", "semantic_sha256", "record_count"}, f"artifacts.{name}")
    require(is_sha256(record["sha256"]), f"artifacts.{name}: bad byte digest")
    require(is_sha256(record["semantic_sha256"]), f"artifacts.{name}: bad semantic digest")
    require(isinstance(record["record_count"], int) and record["record_count"] >= 0, f"artifacts.{name}: record count")
    path = safe_artifact_path(record["path"])
    require(sha256_path(path) == record["sha256"], f"artifacts.{name}: byte digest mismatch")
    if path.suffix == ".ndjson":
        values = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
    else:
        values = json.loads(path.read_text(encoding="utf-8"))
        require(isinstance(values, dict), f"artifacts.{name}: expected JSON object")
        require("records" in values and isinstance(values["records"], list), f"artifacts.{name}: records")
        values = values["records"]
    require(len(values) == record["record_count"], f"artifacts.{name}: record count mismatch")
    actual_semantic = semantic_digest(f"9dvl-d9-s1237-{name}-v1".encode("ascii"), values)
    require(actual_semantic == record["semantic_sha256"], f"artifacts.{name}: semantic digest mismatch")
    return path, values


def validate_literal_artifact(values: list[dict], expected: list[dict]) -> None:
    require(len(values) == EXPECTED_LITERAL_COUNT, "literal artifact: class count")
    require(values == expected, "literal artifact: does not equal independent source reconstruction")


def validate_strata(values: list[dict], positive: bool) -> dict[str, dict]:
    by_id: dict[str, dict] = {}
    seen_axis_supports = {support: set() for support in SUPPORTS}
    for index, record in enumerate(values):
        exact_keys(
            record,
            {
                "id",
                "support_id",
                "kind",
                "dimension",
                "normal_axis_support",
                "parent_ids",
                "boundary_ids",
                "coface_ids",
                "chart_variable_count",
                "chart_map",
                "coverage_witness",
            },
            f"strata[{index}]",
        )
        identifier = record["id"]
        require(isinstance(identifier, str) and identifier and identifier not in by_id, f"strata[{index}]: id")
        support = record["support_id"]
        require(support in SUPPORTS, f"strata[{index}]: support")
        axes = record["normal_axis_support"]
        require(
            isinstance(axes, list)
            and axes
            and axes == sorted(set(axes), key=SUPPORTS[support]["normal_axes"].index)
            and set(axes) <= set(SUPPORTS[support]["normal_axes"]),
            f"strata[{index}]: normal axes",
        )
        seen_axis_supports[support].add(tuple(axes))
        require(record["kind"] in {"INTERIOR", "FACET", "BASE", "APEX", "SEAM", "COFACE", "COEFFICIENT_ZERO"}, f"strata[{index}]: kind")
        require(isinstance(record["dimension"], int) and record["dimension"] >= 0, f"strata[{index}]: dimension")
        for field in ("parent_ids", "boundary_ids", "coface_ids"):
            require(isinstance(record[field], list) and len(record[field]) == len(set(record[field])), f"strata[{index}]: {field}")
        count = record["chart_variable_count"]
        require(isinstance(count, int) and count >= 1, f"strata[{index}]: chart variable count")
        require(isinstance(record["chart_map"], list) and len(record["chart_map"]) == 9, f"strata[{index}]: chart map")
        for axis, polynomial in enumerate(record["chart_map"]):
            validate_polynomial(polynomial, count, f"strata[{index}].chart_map[{axis}]")
        witness = record["coverage_witness"]
        exact_keys(
            witness,
            {"kind", "ambient_dimension", "source_cell_ids", "partition_records", "exact_partition_sha256"},
            f"strata[{index}].coverage",
        )
        require(witness["kind"] == "EXACT_RATIONAL_SIMPLICIAL_PARTITION", f"strata[{index}]: unsupported coverage")
        ambient = witness["ambient_dimension"]
        require(isinstance(ambient, int) and ambient >= 0, f"strata[{index}]: partition dimension")
        require(isinstance(witness["source_cell_ids"], list) and witness["source_cell_ids"] and len(witness["source_cell_ids"]) == len(set(witness["source_cell_ids"])), f"strata[{index}]: source cells")
        partitions = witness["partition_records"]
        require(isinstance(partitions, list) and partitions, f"strata[{index}]: missing materialized partition")
        partition_ids = set()
        for offset, partition in enumerate(partitions):
            exact_keys(partition, {"id", "source_cell_id", "vertices", "orientation", "boundary"}, f"strata[{index}].partition[{offset}]")
            require(isinstance(partition["id"], str) and partition["id"] and partition["id"] not in partition_ids, f"strata[{index}]: partition id")
            partition_ids.add(partition["id"])
            require(partition["source_cell_id"] in witness["source_cell_ids"], f"strata[{index}]: partition source")
            require(partition["orientation"] in {-1, 1}, f"strata[{index}]: partition orientation")
            require(isinstance(partition["vertices"], list) and len(partition["vertices"]) == ambient + 1, f"strata[{index}]: simplex vertices")
            for vertex in partition["vertices"]:
                require(isinstance(vertex, list) and len(vertex) == ambient, f"strata[{index}]: vertex dimension")
                for value in vertex:
                    parse_fraction(value, f"strata[{index}].partition vertex")
            require(isinstance(partition["boundary"], list), f"strata[{index}]: partition boundary")
        require(is_sha256(witness["exact_partition_sha256"]), f"strata[{index}]: partition digest")
        require(
            witness["exact_partition_sha256"]
            == semantic_digest(b"9dvl-d9-s1237-exact-partition-v1", partitions),
            f"strata[{index}]: partition semantic mismatch",
        )
        by_id[identifier] = record

    for identifier, record in by_id.items():
        for field in ("parent_ids", "boundary_ids", "coface_ids"):
            require(all(target in by_id for target in record[field]), f"stratum {identifier}: dangling {field}")
        require(all(by_id[target]["support_id"] == record["support_id"] for target in record["parent_ids"] + record["boundary_ids"] + record["coface_ids"]), f"stratum {identifier}: cross-support incidence")

    if positive:
        for support, definition in SUPPORTS.items():
            required = {
                tuple(definition["normal_axes"][index] for index in range(6) if (mask >> index) & 1)
                for mask in range(1, 1 << 6)
            }
            require(required <= seen_axis_supports[support], f"strata: incomplete projective normal-axis closure for {support}")
    return by_id


def validate_normal_forms(
    values: list[dict],
    strata: dict[str, dict],
    positive: bool,
    literal_sources: dict[int, tuple[dict[tuple[int, ...], Fraction], int]],
    parent_sources: dict[int, tuple[dict[tuple[int, ...], Fraction], int]],
) -> None:
    seen: set[tuple[str, str, str, int]] = set()
    literal_ids: set[int] = set()
    parent_ids: set[int] = set()
    for index, record in enumerate(values):
        exact_keys(
            record,
            {
                "support_id",
                "stratum_id",
                "source_kind",
                "source_id",
                "required_orientation",
                "lowest_normal_degree",
                "variable_count",
                "lowest_normal_form",
                "pullback_identity",
            },
            f"normal_forms[{index}]",
        )
        require(record["support_id"] in SUPPORTS, f"normal_forms[{index}]: support")
        require(record["stratum_id"] in strata, f"normal_forms[{index}]: stratum")
        require(strata[record["stratum_id"]]["support_id"] == record["support_id"], f"normal_forms[{index}]: support/stratum")
        require(record["source_kind"] in {"ACTIVE_LITERAL", "PARENT_BRACKET"}, f"normal_forms[{index}]: source kind")
        require(isinstance(record["source_id"], int) and record["source_id"] >= 0, f"normal_forms[{index}]: source id")
        require(record["required_orientation"] in {-1, 1}, f"normal_forms[{index}]: orientation")
        require(isinstance(record["lowest_normal_degree"], int) and record["lowest_normal_degree"] >= 0, f"normal_forms[{index}]: degree")
        stratum = strata[record["stratum_id"]]
        variable_count = record["variable_count"]
        require(
            isinstance(variable_count, int)
            and variable_count >= 1
            and stratum["chart_variable_count"] == variable_count + 1,
            f"normal_forms[{index}]: variable count",
        )
        lowest = validate_polynomial(record["lowest_normal_form"], variable_count, f"normal_forms[{index}].polynomial")
        source_table = literal_sources if record["source_kind"] == "ACTIVE_LITERAL" else parent_sources
        require(record["source_id"] in source_table, f"normal_forms[{index}]: unknown source")
        source_polynomial, source_orientation = source_table[record["source_id"]]
        require(record["required_orientation"] == source_orientation, f"normal_forms[{index}]: source orientation mismatch")

        identity = record["pullback_identity"]
        exact_keys(
            identity,
            {
                "source_polynomial_sha256",
                "substitution_map_sha256",
                "radial_variable_index",
                "pulled_polynomial",
            },
            f"normal_forms[{index}].identity",
        )
        require(identity["source_polynomial_sha256"] == source_polynomial_digest(source_polynomial), f"normal_forms[{index}]: source polynomial digest")
        require(
            identity["substitution_map_sha256"]
            == sha256_bytes(b"9dvl-d9-s1237-substitution-map-v1\0" + canonical_json(stratum["chart_map"])),
            f"normal_forms[{index}]: substitution map digest",
        )
        pulled_count = stratum["chart_variable_count"]
        radial = identity["radial_variable_index"]
        require(isinstance(radial, int) and 0 <= radial < pulled_count, f"normal_forms[{index}]: radial index")
        pulled = validate_polynomial(identity["pulled_polynomial"], pulled_count, f"normal_forms[{index}].pulled")
        substitution = [
            validate_polynomial(polynomial, pulled_count, f"normal_forms[{index}].substitution[{axis}]")
            for axis, polynomial in enumerate(stratum["chart_map"])
        ]
        require(polynomial_compose(source_polynomial, substitution, pulled_count) == pulled, f"normal_forms[{index}]: false pullback identity")
        degree = record["lowest_normal_degree"]
        require(min(exponent[radial] for exponent in pulled) == degree, f"normal_forms[{index}]: false lowest radial degree")
        extracted: dict[tuple[int, ...], Fraction] = {}
        for exponent, coefficient in pulled.items():
            if exponent[radial] != degree:
                continue
            reduced = exponent[:radial] + exponent[radial + 1 :]
            extracted[reduced] = extracted.get(reduced, Fraction(0)) + coefficient
            if extracted[reduced] == 0:
                del extracted[reduced]
        require(extracted == lowest, f"normal_forms[{index}]: lowest normal form mismatch")
        key = (record["support_id"], record["stratum_id"], record["source_kind"], record["source_id"])
        require(key not in seen, f"normal_forms[{index}]: duplicate source/stratum")
        seen.add(key)
        if record["source_kind"] == "ACTIVE_LITERAL":
            require(record["source_id"] < 26_740, f"normal_forms[{index}]: literal id range")
            literal_ids.add(record["source_id"])
        else:
            require(record["source_id"] < EXPECTED_PARENT_INEQUALITY_COUNT, f"normal_forms[{index}]: parent id range")
            parent_ids.add(record["source_id"])
    if positive:
        require(len(literal_ids) == EXPECTED_LITERAL_COUNT, "normal forms: not all active literals occur")
        require(parent_ids == set(range(EXPECTED_PARENT_INEQUALITY_COUNT)), "normal forms: not all parent inequalities occur")
        for stratum in strata:
            support = strata[stratum]["support_id"]
            literal_count = sum(key[:2] == (support, stratum) and key[2] == "ACTIVE_LITERAL" for key in seen)
            parent_count = sum(key[:2] == (support, stratum) and key[2] == "PARENT_BRACKET" for key in seen)
            require(literal_count == EXPECTED_LITERAL_COUNT, f"normal forms: literal gap on {stratum}")
            require(parent_count == EXPECTED_PARENT_INEQUALITY_COUNT, f"normal forms: parent gap on {stratum}")


def _linear_coefficients(polynomial: dict[tuple[int, ...], Fraction], variable_count: int, context: str) -> list[Fraction]:
    answer = [Fraction(0) for _ in range(variable_count)]
    for exponent, coefficient in polynomial.items():
        require(sum(exponent) == 1, f"{context}: Gordan witness requires homogeneous linear forms")
        axis = exponent.index(1)
        require(exponent.count(1) == 1, f"{context}: malformed linear monomial")
        answer[axis] += coefficient
    return answer


def validate_sectors(values: list[dict], strata: dict[str, dict], positive: bool) -> None:
    seen: set[str] = set()
    covered_strata: set[str] = set()
    for index, record in enumerate(values):
        exact_keys(
            record,
            {"id", "stratum_id", "status", "variable_count", "constraints", "witness", "adjacent_sector_ids"},
            f"sectors[{index}]",
        )
        identifier = record["id"]
        require(isinstance(identifier, str) and identifier and identifier not in seen, f"sectors[{index}]: duplicate id")
        seen.add(identifier)
        require(record["stratum_id"] in strata, f"sectors[{index}]: stratum")
        count = record["variable_count"]
        require(isinstance(count, int) and count >= 1, f"sectors[{index}]: variables")
        constraints = record["constraints"]
        require(isinstance(constraints, list) and constraints, f"sectors[{index}]: constraints")
        parsed = []
        for offset, constraint in enumerate(constraints):
            exact_keys(constraint, {"relation", "polynomial"}, f"sectors[{index}].constraints[{offset}]")
            require(constraint["relation"] in {"GT0", "EQ0"}, f"sectors[{index}]: relation")
            parsed.append((constraint["relation"], validate_polynomial(constraint["polynomial"], count, f"sectors[{index}].constraint[{offset}]")))
        require(record["status"] in {"FEASIBLE", "INFEASIBLE"}, f"sectors[{index}]: status")
        witness = record["witness"]
        if record["status"] == "FEASIBLE":
            exact_keys(witness, {"kind", "point"}, f"sectors[{index}].witness")
            require(witness["kind"] == "EXACT_RATIONAL_POINT", f"sectors[{index}]: unsupported feasible witness")
            require(isinstance(witness["point"], list) and len(witness["point"]) == count, f"sectors[{index}]: point")
            point = [parse_fraction(value, f"sectors[{index}].point") for value in witness["point"]]
            for relation, polynomial in parsed:
                value = evaluate_polynomial(polynomial, point)
                require(value > 0 if relation == "GT0" else value == 0, f"sectors[{index}]: point violates constraint")
            covered_strata.add(record["stratum_id"])
        else:
            exact_keys(witness, {"kind", "multipliers"}, f"sectors[{index}].witness")
            require(witness["kind"] == "GORDAN_STRICT_LINEAR", f"sectors[{index}]: unsupported infeasible witness")
            require(all(relation == "GT0" for relation, _ in parsed), f"sectors[{index}]: Gordan cannot discharge equations")
            multipliers = [parse_fraction(value, f"sectors[{index}].multipliers") for value in witness["multipliers"]]
            require(len(multipliers) == len(parsed) and all(value >= 0 for value in multipliers) and any(value > 0 for value in multipliers), f"sectors[{index}]: Gordan multipliers")
            combination = [Fraction(0) for _ in range(count)]
            for multiplier, (_relation, polynomial) in zip(multipliers, parsed, strict=True):
                coefficients = _linear_coefficients(polynomial, count, f"sectors[{index}]")
                combination = [left + multiplier * right for left, right in zip(combination, coefficients, strict=True)]
            require(not any(combination), f"sectors[{index}]: invalid Gordan identity")
        require(isinstance(record["adjacent_sector_ids"], list) and len(record["adjacent_sector_ids"]) == len(set(record["adjacent_sector_ids"])), f"sectors[{index}]: adjacency")
    require(all(target in seen for record in values for target in record["adjacent_sector_ids"]), "sectors: dangling adjacency")
    if positive:
        require(covered_strata == set(strata), "sectors: every stratum needs an exact feasible sector")


def validate_stabilization(values: list[dict], strata: dict[str, dict], positive: bool) -> None:
    seen: set[tuple[str, int]] = set()
    for index, record in enumerate(values):
        exact_keys(
            record,
            {
                "stratum_id",
                "factor_id",
                "radius",
                "leading_margin",
                "tail_bound",
                "radial_gap",
                "bound_witness",
            },
            f"stabilization[{index}]",
        )
        require(record["stratum_id"] in strata, f"stabilization[{index}]: stratum")
        require(isinstance(record["factor_id"], int) and 0 <= record["factor_id"] < 26_740, f"stabilization[{index}]: factor")
        radius = parse_fraction(record["radius"], f"stabilization[{index}].radius")
        margin = parse_fraction(record["leading_margin"], f"stabilization[{index}].margin")
        tail = parse_fraction(record["tail_bound"], f"stabilization[{index}].tail")
        gap = record["radial_gap"]
        require(radius > 0 and margin > 0 and tail >= 0, f"stabilization[{index}]: sign bounds")
        require(isinstance(gap, int) and gap >= 1, f"stabilization[{index}]: radial gap")
        witness = record["bound_witness"]
        exact_keys(witness, {"leading_bernstein_controls", "tail_bernstein_abs_controls"}, f"stabilization[{index}].witness")
        require(isinstance(witness["leading_bernstein_controls"], list) and witness["leading_bernstein_controls"], f"stabilization[{index}]: leading controls")
        leading_controls = [parse_fraction(value, f"stabilization[{index}].leading control") for value in witness["leading_bernstein_controls"]]
        require(all(value > 0 for value in leading_controls) or all(value < 0 for value in leading_controls), f"stabilization[{index}]: leading controls are not sign definite")
        require(margin == min(map(abs, leading_controls)), f"stabilization[{index}]: false leading margin")
        require(isinstance(witness["tail_bernstein_abs_controls"], list) and witness["tail_bernstein_abs_controls"], f"stabilization[{index}]: tail controls")
        tail_controls = [parse_fraction(value, f"stabilization[{index}].tail control") for value in witness["tail_bernstein_abs_controls"]]
        require(all(value >= 0 for value in tail_controls), f"stabilization[{index}]: negative absolute tail control")
        require(tail == max(tail_controls), f"stabilization[{index}]: false tail bound")
        require((radius ** gap) * tail < margin, f"stabilization[{index}]: domination inequality")
        key = (record["stratum_id"], record["factor_id"])
        require(key not in seen, f"stabilization[{index}]: duplicate")
        seen.add(key)
    if positive:
        for stratum in strata:
            count = sum(item[0] == stratum for item in seen)
            require(count == EXPECTED_LITERAL_COUNT, f"stabilization: literal gap on {stratum}")


def validate_endpoint_record(values: list[dict], endpoint: str, name: str) -> None:
    require(len(values) == 1, f"{name}: exactly one endpoint record required")
    record = values[0]
    if name == "obstruction":
        exact_keys(record, {"kind", "support_id", "stratum_id", "source_ids", "exact_witness", "consequence"}, "obstruction")
        require(endpoint == "NORMAL_LINK_REDUCTION_NO_GO", "obstruction: wrong endpoint")
        require(record["kind"] in {"EXTRA_LINK_WALL", "SINGULAR_LINK", "MISSING_COFACE", "UNSTABLE_HIGHER_ORDER", "SOURCE_CONTRACT_CONTRADICTION"}, "obstruction: kind")
        require(record["consequence"] == "NORMAL_LINK_REDUCTION_NO_GO_ONLY", "obstruction: overclaim")
        require(isinstance(record["exact_witness"], dict) and record["exact_witness"], "obstruction: exact witness")
    else:
        exact_keys(record, {"endpoint", "processed_semantic_sha256", "processed_obligations", "pending_obligations", "resume_command", "ceiling"}, "frontier")
        require(record["endpoint"] == endpoint, "frontier: endpoint mismatch")
        require(is_sha256(record["processed_semantic_sha256"]), "frontier: digest")
        require(isinstance(record["processed_obligations"], list) and isinstance(record["pending_obligations"], list) and record["pending_obligations"], "frontier: obligation partition")
        require(not (set(record["processed_obligations"]) & set(record["pending_obligations"])), "frontier: overlapping partition")
        require(isinstance(record["resume_command"], str) and record["resume_command"], "frontier: resume command")


def validate_certificate(certificate: dict, expected_census: list[dict], census_digest: str) -> str:
    exact_keys(
        certificate,
        {"format", "target_id", "endpoint", "scope", "source_binding", "artifacts", "claims", "semantic_digests"},
        "certificate",
    )
    require(certificate["format"] == FORMAT, "certificate: format")
    require(certificate["target_id"] == TARGET, "certificate: target")
    endpoint = certificate["endpoint"]
    require(endpoint in ENDPOINTS, "certificate: endpoint")

    exact_keys(certificate["scope"], {"parent_index", "family", "supports", "ledger_before", "ledger_after", "projective_normal_dimension"}, "scope")
    require(certificate["scope"] == {
        "parent_index": 2599,
        "family": "S12,37",
        "supports": [SUPPORTS["S3115"]["support"], SUPPORTS["S337"]["support"]],
        "ledger_before": "2/9",
        "ledger_after": "2/9",
        "projective_normal_dimension": 5,
    }, "certificate: scope changed")

    binding = certificate["source_binding"]
    exact_keys(binding, {"source_revision", "source_tree", "opening_commit", "opening_tree", "source_manifest_sha256", "active_sector_semantic_sha256", "literal_census_semantic_sha256", "literal_class_count", "active_occurrence_count"}, "source binding")
    require(binding["source_revision"] == SOURCE_REVISION and binding["source_tree"] == SOURCE_TREE, "source binding: canonical base")
    require(binding["opening_commit"] == OPENING_COMMIT and binding["opening_tree"] == OPENING_TREE, "source binding: opening")
    require(binding["source_manifest_sha256"] == sha256_path(SOURCE_MANIFEST), "source binding: manifest")
    require(binding["active_sector_semantic_sha256"] == EXPECTED_ACTIVE_SECTOR_DIGEST, "source binding: active theorem digest")
    require(binding["literal_census_semantic_sha256"] == census_digest, "source binding: literal census digest")
    require(binding["literal_class_count"] == EXPECTED_LITERAL_COUNT and binding["active_occurrence_count"] == EXPECTED_OCCURRENCE_COUNT, "source binding: census counts")

    claims = certificate["claims"]
    exact_keys(claims, {"sample_only", "complete_recursive_strata", "complete_parent_safe_projective_link", "exact_stabilization", "ledger_consequence", "prohibited_consequences"}, "claims")
    require(claims["sample_only"] is False, "claims: sample-only payload")
    require(claims["ledger_consequence"] == "NO_LEDGER_CHANGE", "claims: false ledger consequence")
    require(claims["prohibited_consequences"] == PROHIBITED_CONSEQUENCES, "claims: scope mutation")

    artifacts = certificate["artifacts"]
    exact_keys(artifacts, ARTIFACT_KEYS, "artifacts")
    literal_loaded = validate_artifact_ref(artifacts["literal_census"], "literal_census", True)
    assert literal_loaded is not None
    validate_literal_artifact(literal_loaded[1], expected_census)

    positive = endpoint == "COMPLETE_ORIENTED_NORMAL_LINK_GATE"
    strata_loaded = validate_artifact_ref(artifacts["recursive_strata"], "recursive_strata", positive)
    normal_loaded = validate_artifact_ref(artifacts["normal_form_inventory"], "normal_form_inventory", positive)
    sectors_loaded = validate_artifact_ref(artifacts["link_sectors"], "link_sectors", positive)
    stabilization_loaded = validate_artifact_ref(artifacts["stabilization"], "stabilization", positive)
    obstruction_loaded = validate_artifact_ref(artifacts["obstruction"], "obstruction", endpoint == "NORMAL_LINK_REDUCTION_NO_GO")
    frontier_loaded = validate_artifact_ref(artifacts["frontier"], "frontier", endpoint in {"UNRESOLVED_NORMAL_LINK_STRATUM", "HASH_PINNED_NORMAL_LINK_FRONTIER"})

    require((artifacts["obstruction"] is not None) == (endpoint == "NORMAL_LINK_REDUCTION_NO_GO"), "endpoint: obstruction presence")
    require((artifacts["frontier"] is not None) == (endpoint in {"UNRESOLVED_NORMAL_LINK_STRATUM", "HASH_PINNED_NORMAL_LINK_FRONTIER"}), "endpoint: frontier presence")
    if positive:
        require(claims["complete_recursive_strata"] is True and claims["complete_parent_safe_projective_link"] is True and claims["exact_stabilization"] is True, "positive endpoint: incomplete claims")
    else:
        require(not all((claims["complete_recursive_strata"], claims["complete_parent_safe_projective_link"], claims["exact_stabilization"])), "nonpositive endpoint: false complete gate")

    strata = validate_strata(strata_loaded[1], positive) if strata_loaded else {}
    if normal_loaded:
        validate_normal_forms(
            normal_loaded[1],
            strata,
            positive,
            literal_source_polynomials(expected_census),
            parent_source_polynomials(),
        )
    if sectors_loaded:
        validate_sectors(sectors_loaded[1], strata, positive)
    if stabilization_loaded:
        validate_stabilization(stabilization_loaded[1], strata, positive)
    if obstruction_loaded:
        validate_endpoint_record(obstruction_loaded[1], endpoint, "obstruction")
    if frontier_loaded:
        validate_endpoint_record(frontier_loaded[1], endpoint, "frontier")

    digests = certificate["semantic_digests"]
    exact_keys(digests, {"literal_census", "normal_forms", "strata", "sectors", "stabilization", "endpoint", "certificate"}, "semantic digests")
    require(digests["literal_census"] == census_digest, "semantic digests: literal census")
    for field in digests:
        require(is_sha256(digests[field]), f"semantic digests: {field}")
    zero_digest = "0" * 64
    artifact_digest_fields = {
        "normal_forms": "normal_form_inventory",
        "strata": "recursive_strata",
        "sectors": "link_sectors",
        "stabilization": "stabilization",
    }
    for digest_field, artifact_field in artifact_digest_fields.items():
        expected_digest = (
            artifacts[artifact_field]["semantic_sha256"]
            if artifacts[artifact_field] is not None
            else zero_digest
        )
        require(digests[digest_field] == expected_digest, f"semantic digests: {digest_field} binding")
    if obstruction_loaded:
        endpoint_digest = artifacts["obstruction"]["semantic_sha256"]
    elif frontier_loaded:
        endpoint_digest = artifacts["frontier"]["semantic_sha256"]
    else:
        endpoint_digest = sha256_bytes(
            b"9dvl-d9-s1237-positive-endpoint-v1\0"
            + canonical_json({"endpoint": endpoint, "claims": claims})
        )
    require(digests["endpoint"] == endpoint_digest, "semantic digests: endpoint binding")
    semantic = copy.deepcopy(certificate)
    semantic["semantic_digests"]["certificate"] = "0" * 64
    actual = sha256_bytes(b"9dvl-d9-s1237-certificate-v1\0" + canonical_json(semantic))
    require(digests["certificate"] == actual, "semantic digests: certificate")
    require(
        endpoint in {"UNRESOLVED_NORMAL_LINK_STRATUM", "HASH_PINNED_NORMAL_LINK_FRONTIER"},
        "v1 envelope is fail-closed for mathematical endpoints until a materialized producer payload supplies a versioned exact partition/obstruction replay adapter",
    )
    return endpoint


def _structural_fixture_validator(record: dict) -> None:
    """Small exact kernel used only to prove hostile mutation sensitivity."""

    exact_keys(record, {"source", "literals", "strata", "sectors", "stabilization", "claims"}, "self-test")
    require(record["source"] == "pinned", "self-test: missing source")
    literals = record["literals"]
    require([row["id"] for row in literals] == [0, 1], "self-test: literal omission/order")
    require(literals[0]["occurrences"] == [0, 2] and literals[1]["occurrences"] == [1], "self-test: occurrence omission")
    require([row["orientation"] for row in literals] == [1, -1], "self-test: orientation")
    strata = record["strata"]
    require(strata == ["root", "facet"], "self-test: stratum omission")
    sectors = record["sectors"]
    require(sectors == ["root:+-", "facet:++"], "self-test: sector duplicate/order")
    radius = parse_fraction(record["stabilization"]["radius"], "self-test.radius")
    margin = parse_fraction(record["stabilization"]["margin"], "self-test.margin")
    tail = parse_fraction(record["stabilization"]["tail"], "self-test.tail")
    require(radius * tail < margin, "self-test: false stabilization")
    require(record["claims"] == {"collar": False, "topology": False, "ledger": "2/9"}, "self-test: false consequence")


def run_self_tests() -> int:
    fixture = json.loads(SELF_TEST_FIXTURE.read_text(encoding="utf-8"))
    exact_keys(fixture, {"format", "valid_kernel_record", "hostile_mutations"}, "fixture")
    require(fixture["format"] == "diag9-normal-link-certificate-self-test-v1", "fixture: format")
    base = fixture["valid_kernel_record"]
    _structural_fixture_validator(base)
    mutations = fixture["hostile_mutations"]
    expected = {
        "missing_source",
        "missing_literal",
        "missing_occurrence",
        "reordered_literal",
        "orientation_flip",
        "missing_stratum",
        "duplicate_sector",
        "false_stabilization",
        "false_collar",
        "false_topology",
        "false_ledger_consequence",
    }
    require(set(mutations) == expected, "fixture: hostile mutation catalog")
    accepted = 0
    for name, instructions in mutations.items():
        hostile = copy.deepcopy(base)
        operation = instructions["operation"]
        if operation == "delete":
            target = hostile
            for key in instructions["path"][:-1]:
                target = target[key]
            del target[instructions["path"][-1]]
        elif operation == "set":
            target = hostile
            for key in instructions["path"][:-1]:
                target = target[key]
            target[instructions["path"][-1]] = instructions["value"]
        elif operation == "append":
            target = hostile
            for key in instructions["path"]:
                target = target[key]
            target.append(instructions["value"])
        else:
            raise CertificateError(f"fixture: unknown mutation operation {operation}")
        try:
            _structural_fixture_validator(hostile)
        except (CertificateError, KeyError, IndexError):
            accepted += 1
        else:
            raise CertificateError(f"hostile mutation accepted: {name}")
    return accepted


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path)
    parser.add_argument("--emit-literal-census", type=Path)
    parser.add_argument("--self-test-only", action="store_true")
    arguments = parser.parse_args()

    if arguments.self_test_only:
        count = run_self_tests()
        print(f"PASS hostile structural-kernel mutations rejected {count}/{count}")
        return

    verify_source_manifest()
    records, census_digest, occurrence_count = rebuild_literal_census()
    require(census_digest == EXPECTED_LITERAL_CENSUS_DIGEST, f"literal census: semantic drift {census_digest}")
    require(occurrence_count == EXPECTED_OCCURRENCE_COUNT, "literal census: occurrence drift")

    if arguments.emit_literal_census is not None:
        target = arguments.emit_literal_census.resolve()
        try:
            target.relative_to(HERE)
        except ValueError as error:
            raise CertificateError("emitted census must stay in certificate track") from error
        target.write_text("".join(json.dumps(row, sort_keys=True, separators=(",", ":")) + "\n" for row in records), encoding="utf-8")
        print(f"WROTE exact literal census {target}")

    hostile_count = run_self_tests()

    if arguments.certificate is not None:
        certificate_path = arguments.certificate.resolve()
        certificate = json.loads(certificate_path.read_text(encoding="utf-8"))
        endpoint = validate_certificate(certificate, records, census_digest)
        print(f"ACCEPT {endpoint}")
    else:
        template = json.loads(TEMPLATE.read_text(encoding="utf-8"))
        template["source_binding"]["source_manifest_sha256"] = sha256_path(SOURCE_MANIFEST)
        template["source_binding"]["literal_census_semantic_sha256"] = census_digest
        try:
            validate_certificate(template, records, census_digest)
        except CertificateError as error:
            require(str(error) == "claims: sample-only payload", "template did not fail at the sample-only gate")
        else:
            raise CertificateError("incomplete shipped template was accepted")
        print("PASS incomplete/sample-only producer template rejected")

    print(f"PASS pinned source manifest ({len(json.loads(SOURCE_MANIFEST.read_text())['used_sha256'])} artifacts)")
    print(f"PASS exact S12,37 literal census {len(records)} classes / {occurrence_count} active occurrences")
    print(f"LITERAL CENSUS SEMANTIC SHA256 {census_digest}")
    print(f"PASS hostile structural-kernel mutations rejected {hostile_count}/{hostile_count}")
    print("SCOPE normal-link certificate contract only; no collar, topology, D9, or ledger claim")


if __name__ == "__main__":
    main()
