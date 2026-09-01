#!/usr/bin/env python3
"""Fail-closed v1 envelope for the universal D9 component-cut gate.

The acceptance kernel is endpoint-neutral.  It validates exact structural and
arithmetic evidence for positive, negative, null, and timeout records, but v1
has no registered live mathematical adapter.  Consequently a live endpoint is
rejected until an independently reviewed adapter is added in a later schema
version.  The four bundled records are synthetic kernel self-tests only.
"""

from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE_MANIFEST = HERE / "SOURCE_MANIFEST.json"
SELF_TEST_FIXTURE = HERE / "SELF_TEST_FIXTURE.json"
RESULT_PATH = HERE / "RESULT.json"

FORMAT = "9dvl-d9-universal-cut-coverage-certificate-v1"
FIXTURE_FORMAT = "9dvl-d9-universal-cut-self-test-v1"
TARGET = "D9_UNIVERSAL_FEASIBLE_COMPONENT_CUT_GATE1"
OPENING_COMMIT = "6cbd1b4a7d3ed61bee268b6b54cbfadeece90f0e"
OPENING_TREE = "84eaf80b30e1f366b8f959bd6435a217762636b3"
CANONICAL_BASE = "cbe84ccd7273252c81fd4da17ee360a284d2a2a6"
CANONICAL_BASE_TREE = "da3cd6feca1052ea14ed5036413c72b8f7fadc2a"

ENDPOINTS = {
    "UNIVERSAL_D9_CUT_OBSTRUCTIONS_UNSAT": "positive",
    "EXACT_D9_TWO_COMPONENT_SEPARATOR": "negative",
    "UNIVERSAL_CUT_SCHEMA_COVERAGE_GAP": "null",
    "HASH_PINNED_D9_CUT_SCHEMA_FRONTIER": "timeout",
}
QUANTIFIERS = {
    "parents": "EVERY_REALIZABLE_UOM(4,8)_PARENT",
    "families": "EVERY_PROPER_PAIRWISE_INCOMPARABLE_NINE_FAMILY",
    "active_literals": "EVERY_CONSISTENT_ACTIVE_LITERAL_ASSIGNMENT",
    "cuts": "EVERY_PAIR_OF_DISTINCT_FEASIBLE_ACTIVE_SECTOR_COMPONENTS",
    "ends": "ALL_CHARTS_MULTIPLICITIES_MULTIWALLS_RECURSIVE_STRATA_AND_GENUINE_INFINITY",
}
GRAMMAR_KINDS = (
    "RESIDUAL_WALL_TYPE",
    "SUPPORT_MINIMAL_GORDAN_CIRCUIT",
    "SIGNED_MULTIWALL_INCIDENCE",
    "RECURSIVE_BOUNDARY_STRATUM",
    "GENUINE_INFINITY_END",
)
PRESERVED_STRUCTURE = (
    "SIGN",
    "DUPLICATE_OCCURRENCE",
    "CHART",
    "PROPERNESS",
    "MULTIWALL_INCIDENCE",
    "RECURSIVE_FACET",
    "GENUINE_INFINITY",
)
PROHIBITED = (
    "LOCAL_COORIENTATION_IMPLIES_GLOBAL_CONNECTIVITY",
    "ALL_STRATA_GLUING_IMPLIES_GLOBAL_CONNECTIVITY",
    "RECURSIVE_FACET_WALL_IS_STRICT_OPEN_PARENT_SEPARATOR",
    "FIXED_FAMILY_CONNECTIVITY_PROVES_DIAGONAL_9",
    "SAMPLED_GRAPH_IS_GLOBAL_COVERAGE",
    "CERTIFICATE_ENGINEER_MUTATES_THE_THEOREM_LEDGER",
)
MAX_TYPES = 10_000
MAX_INSTANCES = 250_000
LIVE_ADAPTERS: frozenset[tuple[str, int]] = frozenset()
FIXTURE_ADAPTER = ("SELF_TEST_EXACT_D9_CUT_ADAPTER", 1)


class CertificateError(AssertionError):
    """Fail-closed certificate rejection."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CertificateError(message)


def exact_keys(value: Any, expected: set[str], label: str) -> None:
    require(isinstance(value, dict), f"{label}: expected object")
    require(set(value) == expected, f"{label}: wrong fields")


def is_sha256(value: Any) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def object_digest(domain: bytes, value: dict[str, Any]) -> str:
    candidate = copy.deepcopy(value)
    candidate["semantic_sha256"] = "0" * 64
    return sha256_bytes(domain + b"\0" + canonical_json(candidate))


def parse_fraction(value: Any, label: str) -> Fraction:
    require(isinstance(value, str), f"{label}: rational must be a string")
    try:
        rational = Fraction(value)
    except (ValueError, ZeroDivisionError) as error:
        raise CertificateError(f"{label}: malformed rational") from error
    require(str(rational) == value, f"{label}: rational is not reduced canonical text")
    return rational


def verify_source_manifest() -> dict[str, Any]:
    manifest = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    exact_keys(
        manifest,
        {
            "format", "track_id", "target_id", "opening", "canonical_base",
            "used_sha256", "portable_predecessor", "trust_boundary",
            "scope_exclusions", "semantic_sha256",
        },
        "source manifest",
    )
    require(
        manifest["format"] == "9dvl-d9-universal-cut-certificate-source-manifest-v1",
        "source manifest: format",
    )
    require(manifest["track_id"] == "d9-universal-cut-certificate", "source manifest: track")
    require(manifest["target_id"] == TARGET, "source manifest: target")
    require(manifest["opening"] == {"commit": OPENING_COMMIT, "tree": OPENING_TREE}, "source manifest: opening")
    require(
        manifest["canonical_base"] == {"commit": CANONICAL_BASE, "tree": CANONICAL_BASE_TREE},
        "source manifest: canonical base",
    )
    used = manifest["used_sha256"]
    require(isinstance(used, dict) and len(used) >= 15, "source manifest: incomplete source census")
    for relative, expected in sorted(used.items()):
        require(is_sha256(expected), f"source manifest: malformed digest {relative}")
        path = (ROOT / relative).resolve()
        try:
            path.relative_to(ROOT)
        except ValueError as error:
            raise CertificateError("source manifest: path escape") from error
        require(path.is_file(), f"source manifest: missing {relative}")
        require(sha256_path(path) == expected, f"source manifest: drift {relative}")
    require(
        manifest["portable_predecessor"] == {
            "historical_referee_commit": "ca730426cdd5847ae262ddc29c6f4ae98369eba3",
            "availability_at_opening": "ABSENT",
            "dereference_policy": "NEVER_REQUIRED",
            "source_derived_adapter": "PORTABLE_PREDECESSOR_ADAPTER.json",
        },
        "source manifest: portable predecessor policy",
    )
    require(
        manifest["trust_boundary"]
        == "Certificate acceptance is implemented only by this track's exact field/arithmetic kernel and a future versioned independent coverage adapter. Predecessor portability uses the byte-pinned independent referee kernel's source-reconstruction entrypoints, never its mutable wrapper, a producer verdict, or the absent historical referee object.",
        "source manifest: trust boundary",
    )
    require(manifest["scope_exclusions"] == [
        "discovery-side acceptance logic",
        "sampled or fixed-family promotion",
        "recursive-facet wall promoted to a strict-open-parent separator",
        "unproved boundary or infinity attachment",
        "unregistered live mathematical endpoint",
        "theorem-ledger mutation",
    ], "source manifest: scope exclusions")
    require(
        manifest["semantic_sha256"]
        == object_digest(b"9dvl-d9-universal-cut-source-manifest-v1", manifest),
        "source manifest: semantic digest",
    )
    return manifest


def validate_source_binding(binding: Any, mode: str) -> None:
    exact_keys(
        binding,
        {
            "opening_commit", "opening_tree", "canonical_base_commit",
            "canonical_base_tree", "source_manifest_sha256",
        },
        "source binding",
    )
    require(binding["opening_commit"] == OPENING_COMMIT, "source binding: opening commit")
    require(binding["opening_tree"] == OPENING_TREE, "source binding: opening tree")
    require(binding["canonical_base_commit"] == CANONICAL_BASE, "source binding: base commit")
    require(binding["canonical_base_tree"] == CANONICAL_BASE_TREE, "source binding: base tree")
    require(is_sha256(binding["source_manifest_sha256"]), "source binding: manifest digest")
    expected = "0" * 64 if mode == "SELF_TEST" else sha256_path(SOURCE_MANIFEST)
    require(binding["source_manifest_sha256"] == expected, "source binding: manifest drift")


def validate_grammar(grammar: Any) -> tuple[list[str], list[str], list[str]]:
    exact_keys(
        grammar,
        {
            "format", "residual_wall_type_count", "atoms", "covered_atom_ids",
            "pending_atom_ids", "preserved_structure", "max_obstruction_types",
            "max_exact_instances", "boundary_contract",
        },
        "grammar",
    )
    require(grammar["format"] == "d9-universal-cut-obstruction-grammar-v1", "grammar: format")
    require(grammar["residual_wall_type_count"] == 13, "grammar: residual wall type count")
    require(grammar["max_obstruction_types"] == MAX_TYPES, "grammar: type ceiling")
    require(grammar["max_exact_instances"] == MAX_INSTANCES, "grammar: instance ceiling")
    require(tuple(grammar["preserved_structure"]) == PRESERVED_STRUCTURE, "grammar: preserved structure")
    require(grammar["boundary_contract"] == {
        "residence": "EXACT_STRICT_PARENT_OR_NAMED_BOUNDARY_STRATUM_REQUIRED",
        "attachment": "EXACT_COFACE_OR_EXPLICIT_UNRESOLVED_ATTACHMENT_REQUIRED",
        "recursive_facet_default": "BOUNDARY_ONLY_NOT_A_GLOBAL_SEPARATOR",
        "strict_coface": "REQUIRES_SEPARATE_EXACT_WITNESS",
    }, "grammar: boundary residence/attachment contract")
    atoms = grammar["atoms"]
    require(isinstance(atoms, list) and atoms, "grammar: empty atoms")
    require(len(atoms) <= MAX_TYPES, "grammar: type ceiling crossed")
    ids: list[str] = []
    kinds: list[str] = []
    for index, atom in enumerate(atoms):
        exact_keys(atom, {"id", "kind", "source_ref"}, f"grammar atom {index}")
        require(isinstance(atom["id"], str) and atom["id"], f"grammar atom {index}: id")
        require(atom["kind"] in GRAMMAR_KINDS, f"grammar atom {index}: kind")
        require(isinstance(atom["source_ref"], str) and atom["source_ref"], f"grammar atom {index}: source")
        ids.append(atom["id"])
        kinds.append(atom["kind"])
    require(ids == sorted(set(ids)), "grammar: atom ids must be unique and sorted")
    require(set(kinds) == set(GRAMMAR_KINDS), "grammar: all five generator kinds required")
    covered = grammar["covered_atom_ids"]
    pending = grammar["pending_atom_ids"]
    require(covered == sorted(set(covered)), "grammar: covered ids order/duplicate")
    require(pending == sorted(set(pending)), "grammar: pending ids order/duplicate")
    require(not set(covered) & set(pending), "grammar: processed/pending overlap")
    require(set(covered) | set(pending) == set(ids), "grammar: atom partition incomplete")
    return ids, covered, pending


def validate_adapter(adapter: Any, mode: str) -> None:
    exact_keys(adapter, {"id", "version", "status", "evidence_sha256"}, "coverage adapter")
    require(isinstance(adapter["id"], str) and adapter["id"], "coverage adapter: id")
    require(isinstance(adapter["version"], int) and adapter["version"] > 0, "coverage adapter: version")
    require(is_sha256(adapter["evidence_sha256"]), "coverage adapter: digest")
    key = (adapter["id"], adapter["version"])
    if mode == "SELF_TEST":
        require(key == FIXTURE_ADAPTER and adapter["status"] == "FIXTURE_ONLY", "coverage adapter: fixture boundary")
    else:
        require(key in LIVE_ADAPTERS, "v1 has no registered live mathematical endpoint adapter")
        require(adapter["status"] == "INDEPENDENTLY_REPLAYED", "coverage adapter: live status")


def validate_gordan(record: Any, label: str) -> None:
    exact_keys(record, {"id", "type_id", "linear_forms", "positive_multipliers"}, label)
    forms = record["linear_forms"]
    multipliers = record["positive_multipliers"]
    require(isinstance(forms, list) and len(forms) >= 2, f"{label}: forms")
    require(isinstance(multipliers, list) and len(multipliers) == len(forms), f"{label}: multipliers")
    width = len(forms[0])
    require(width > 0 and all(isinstance(row, list) and len(row) == width for row in forms), f"{label}: matrix")
    matrix = [[parse_fraction(value, f"{label}.form") for value in row] for row in forms]
    weights = [parse_fraction(value, f"{label}.multiplier") for value in multipliers]
    require(all(value > 0 for value in weights), f"{label}: multipliers must be positive")
    require(
        all(sum(weights[row] * matrix[row][column] for row in range(len(forms))) == 0 for column in range(width)),
        f"{label}: Gordan weighted sum is nonzero",
    )


def evaluate_polynomial(coefficients: list[Any], point: list[Fraction], label: str) -> Fraction:
    parsed = [parse_fraction(value, label) for value in coefficients]
    require(len(parsed) == len(point) + 1, f"{label}: coefficient dimension")
    return parsed[0] + sum(coefficient * value for coefficient, value in zip(parsed[1:], point, strict=True))


def validate_positive(evidence: Any, atom_ids: list[str]) -> int:
    exact_keys(evidence, {"kind", "instances", "coverage_theorem_sha256", "obstruction_registry_sha256"}, "positive evidence")
    require(evidence["kind"] == "ALL_COVERED_OBSTRUCTIONS_EXACT_UNSAT", "positive evidence: kind")
    require(is_sha256(evidence["coverage_theorem_sha256"]), "positive evidence: theorem digest")
    require(is_sha256(evidence["obstruction_registry_sha256"]), "positive evidence: registry digest")
    instances = evidence["instances"]
    require(isinstance(instances, list) and instances, "positive evidence: empty instance registry")
    require(len(instances) <= MAX_INSTANCES, "positive evidence: instance ceiling")
    ids = []
    for index, record in enumerate(instances):
        validate_gordan(record, f"positive instance {index}")
        require(record["type_id"] in atom_ids, f"positive instance {index}: unknown type")
        ids.append(record["id"])
    require(ids == sorted(set(ids)), "positive evidence: instance ids order/duplicate")
    return len(instances)


def validate_negative(evidence: Any) -> int:
    exact_keys(
        evidence,
        {"kind", "parent_id", "family_id", "active_constraints", "feasible_witnesses", "separator"},
        "negative evidence",
    )
    require(evidence["kind"] == "EXACT_COVERAGE_CERTIFIED_TWO_COMPONENT_SEPARATOR", "negative evidence: kind")
    constraints = evidence["active_constraints"]
    require(isinstance(constraints, list) and constraints, "negative evidence: constraints")
    witnesses = evidence["feasible_witnesses"]
    require(isinstance(witnesses, list) and len(witnesses) == 2, "negative evidence: two witnesses required")
    points: list[list[Fraction]] = []
    for index, witness in enumerate(witnesses):
        exact_keys(witness, {"component_id", "point"}, f"negative witness {index}")
        point = [parse_fraction(value, f"negative witness {index}") for value in witness["point"]]
        require(point, f"negative witness {index}: empty point")
        points.append(point)
    require(witnesses[0]["component_id"] != witnesses[1]["component_id"], "negative evidence: component labels coincide")
    require(len(points[0]) == len(points[1]), "negative evidence: point dimensions")
    for index, constraint in enumerate(constraints):
        exact_keys(constraint, {"id", "coefficients", "relation"}, f"active constraint {index}")
        require(constraint["relation"] == ">0", f"active constraint {index}: only strict exact constraints")
        for witness_index, point in enumerate(points):
            require(
                evaluate_polynomial(constraint["coefficients"], point, f"active constraint {index}") > 0,
                f"negative evidence: witness {witness_index} infeasible",
            )
    separator = evidence["separator"]
    exact_keys(separator, {"coefficients", "left_sign", "right_sign", "coverage_certificate_sha256"}, "separator")
    require(is_sha256(separator["coverage_certificate_sha256"]), "separator: coverage digest")
    values = [evaluate_polynomial(separator["coefficients"], point, "separator") for point in points]
    require(values[0] < 0 < values[1], "separator: exact opposite sides not witnessed")
    require((separator["left_sign"], separator["right_sign"]) == (-1, 1), "separator: sign labels")
    return 2


def validate_null(evidence: Any, pending: list[str]) -> int:
    exact_keys(evidence, {"kind", "first_uncovered", "survivors", "next_discriminator", "resume_argv"}, "null evidence")
    require(evidence["kind"] == "FIRST_EXACT_UNCOVERED_MODE", "null evidence: kind")
    gap = evidence["first_uncovered"]
    exact_keys(gap, {"atom_id", "mode", "exact_witness_sha256"}, "null evidence: first gap")
    require(gap["atom_id"] in pending, "null evidence: first gap is not pending")
    require(gap["mode"] in {"CUT", "MULTIWALL", "TRANSPORT", "RECURSIVE_FACET", "INFINITY"}, "null evidence: gap mode")
    require(is_sha256(gap["exact_witness_sha256"]), "null evidence: witness digest")
    survivors = evidence["survivors"]
    require(isinstance(survivors, list) and survivors == sorted(set(survivors)) and survivors, "null evidence: survivor manifest")
    require(isinstance(evidence["next_discriminator"], str) and evidence["next_discriminator"], "null evidence: next discriminator")
    require(isinstance(evidence["resume_argv"], list) and evidence["resume_argv"] and all(isinstance(x, str) and x for x in evidence["resume_argv"]), "null evidence: resume argv")
    return len(survivors)


def validate_timeout(evidence: Any, covered: list[str], pending: list[str]) -> int:
    exact_keys(evidence, {"kind", "processed", "pending", "ceiling", "checkpoint_sha256", "resume_argv"}, "timeout evidence")
    require(evidence["kind"] == "DETERMINISTIC_HASH_PINNED_FRONTIER", "timeout evidence: kind")
    require(evidence["processed"] == covered and evidence["pending"] == pending, "timeout evidence: frontier binding")
    require(pending, "timeout evidence: pending frontier must be nonempty")
    ceiling = evidence["ceiling"]
    exact_keys(ceiling, {"kind", "limit", "observed"}, "timeout evidence: ceiling")
    limits = {"WALL_HOURS": 12, "CPU_HOURS": 64, "MEMORY_GIB": 16, "OBSTRUCTION_TYPES": MAX_TYPES, "EXACT_INSTANCES": MAX_INSTANCES}
    require(ceiling["kind"] in limits, "timeout evidence: ceiling kind")
    require(ceiling["limit"] == limits[ceiling["kind"]], "timeout evidence: ceiling limit")
    require(isinstance(ceiling["observed"], int) and ceiling["observed"] >= ceiling["limit"], "timeout evidence: ceiling not reached")
    require(is_sha256(evidence["checkpoint_sha256"]), "timeout evidence: checkpoint digest")
    require(isinstance(evidence["resume_argv"], list) and evidence["resume_argv"], "timeout evidence: resume argv")
    return len(covered)


def validate_certificate(certificate: dict[str, Any], *, allow_fixture: bool = False) -> tuple[str, int]:
    exact_keys(
        certificate,
        {
            "format", "schema_version", "target_id", "mode", "source_binding",
            "quantifiers", "grammar", "coverage", "endpoint", "evidence",
            "scope", "prohibited_consequences", "semantic_sha256",
        },
        "certificate",
    )
    require(certificate["format"] == FORMAT and certificate["schema_version"] == 1, "certificate: format/version")
    require(certificate["target_id"] == TARGET, "certificate: target")
    mode = certificate["mode"]
    require(mode in {"SELF_TEST", "LIVE"}, "certificate: mode")
    require(mode != "SELF_TEST" or allow_fixture, "certificate: fixture mode is not a live endpoint")
    validate_source_binding(certificate["source_binding"], mode)
    require(certificate["quantifiers"] == QUANTIFIERS, "certificate: quantifiers")
    require(tuple(certificate["prohibited_consequences"]) == PROHIBITED, "certificate: prohibited consequences")
    atom_ids, covered, pending = validate_grammar(certificate["grammar"])
    coverage = certificate["coverage"]
    exact_keys(coverage, {"status", "adapter", "proof_object_sha256"}, "coverage")
    require(is_sha256(coverage["proof_object_sha256"]), "coverage: proof digest")
    validate_adapter(coverage["adapter"], mode)
    endpoint = certificate["endpoint"]
    require(endpoint in ENDPOINTS, "certificate: endpoint")
    expected_class = ENDPOINTS[endpoint]
    scope = certificate["scope"]
    exact_keys(scope, {"classification", "coverage", "diagonal_9", "ledger_before", "ledger_after", "ledger_change_recommended", "sample_only"}, "scope")
    require(scope["classification"] == expected_class, "scope: endpoint classification")
    require(scope["ledger_before"] == scope["ledger_after"] == "2/9", "scope: certificate cannot mutate ledger")
    require(scope["sample_only"] is False, "scope: sampled evidence")

    if expected_class in {"positive", "negative"}:
        require(coverage["status"] == "COMPLETE" and covered == atom_ids and not pending, "coverage: mathematical endpoint requires completeness")
        require(scope["coverage"] == "PROVED", "scope: coverage theorem")
        if expected_class == "positive":
            require(scope["diagonal_9"] == "PROVED_PENDING_COORDINATOR_INTEGRATION", "scope: positive D9 consequence")
            require(scope["ledger_change_recommended"] == "PROMOTE_DIAGONAL_9_AFTER_INDEPENDENT_REPLAY", "scope: positive recommendation")
            count = validate_positive(certificate["evidence"], atom_ids)
        else:
            require(scope["diagonal_9"] == "DISPROVED_PENDING_COORDINATOR_INTEGRATION", "scope: negative D9 consequence")
            require(scope["ledger_change_recommended"] == "RECORD_EXACT_D9_COUNTEREXAMPLE", "scope: negative recommendation")
            count = validate_negative(certificate["evidence"])
    elif expected_class == "null":
        require(coverage["status"] == "GAP" and pending, "coverage: null requires gap")
        require(scope["coverage"] == "GAP" and scope["diagonal_9"] == "OPEN", "scope: null")
        require(scope["ledger_change_recommended"] == "NONE", "scope: null recommendation")
        count = validate_null(certificate["evidence"], pending)
    else:
        require(coverage["status"] == "PARTIAL" and pending, "coverage: timeout requires partial frontier")
        require(scope["coverage"] == "PARTIAL" and scope["diagonal_9"] == "OPEN", "scope: timeout")
        require(scope["ledger_change_recommended"] == "NONE", "scope: timeout recommendation")
        count = validate_timeout(certificate["evidence"], covered, pending)

    require(is_sha256(certificate["semantic_sha256"]), "certificate: semantic digest")
    require(
        certificate["semantic_sha256"] == object_digest(b"9dvl-d9-universal-cut-certificate-v1", certificate),
        "certificate: semantic digest mismatch",
    )
    return endpoint, count


def load_fixtures() -> list[dict[str, Any]]:
    fixture = json.loads(SELF_TEST_FIXTURE.read_text(encoding="utf-8"))
    exact_keys(fixture, {"format", "certificates"}, "self-test fixture")
    require(fixture["format"] == FIXTURE_FORMAT, "self-test fixture: format")
    certificates = fixture["certificates"]
    require(isinstance(certificates, list) and len(certificates) == 4, "self-test fixture: endpoint census")
    require({row["endpoint"] for row in certificates} == set(ENDPOINTS), "self-test fixture: endpoint coverage")
    return certificates


def verify_result() -> dict[str, Any]:
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    exact_keys(
        result,
        {
            "format", "track_id", "base_revision", "opening_revision", "outcome",
            "summary", "mathematical_endpoint", "artifacts", "replay", "coverage",
            "canaries", "source_accounting", "portability", "open_defects",
            "next_action", "ledger_change_recommended", "semantic_sha256",
        },
        "result",
    )
    require(result["format"] == "9dvl-d9-universal-cut-certificate-result-v1", "result: format")
    require(result["track_id"] == "d9-universal-cut-certificate", "result: track")
    require(result["base_revision"] == CANONICAL_BASE, "result: base")
    require(result["opening_revision"] == OPENING_COMMIT, "result: opening")
    require(result["outcome"] == "finite-exact", "result: outcome")
    require(
        result["summary"]
        == "A versioned endpoint-neutral universal-cut contract, exact four-endpoint preflight kernel, 32-case hostile harness, and successor-portable source replay are complete; no live universal coverage proof object is claimed.",
        "result: summary",
    )
    require(result["mathematical_endpoint"] is None, "result: mathematical overclaim")
    artifact_paths = {
        "SCHEMA.md", "SOURCE_MANIFEST.json", "SELF_TEST_FIXTURE.json",
        "PORTABLE_PREDECESSOR_ADAPTER.json", "HOSTILE_MUTATIONS.json",
        "verify_universal_cut_certificate.py", "verify_portable_predecessor.py",
        "run_hostile_mutations.py",
    }
    artifacts = result["artifacts"]
    require(isinstance(artifacts, list) and {row["path"] for row in artifacts} == artifact_paths, "result: artifact census")
    for row in artifacts:
        exact_keys(row, {"path", "sha256"}, "result artifact")
        require(is_sha256(row["sha256"]), f"result: malformed artifact digest {row['path']}")
        path = (HERE / row["path"]).resolve()
        try:
            path.relative_to(HERE)
        except ValueError as error:
            raise CertificateError("result: artifact path escape") from error
        require(path.is_file() and sha256_path(path) == row["sha256"], f"result: artifact drift {row['path']}")
    require(result["replay"] == {
        "command": "PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python ops/team/d9-universal-cut-certificate/verify_universal_cut_certificate.py && PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python ops/team/d9-universal-cut-certificate/run_hostile_mutations.py && PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python ops/team/d9-universal-cut-certificate/verify_portable_predecessor.py",
        "result": "PASS contract/result; 4/4 exact endpoint fixtures; 4/4 fixture adapters rejected as live; 32/32 hostile mutations rejected; source-derived predecessor replay returns NORMAL_LINK_REDUCTION_NO_GO without ca730426",
    }, "result: replay")
    require(result["coverage"] == {
        "included": "VERSIONED_ENDPOINT_NEUTRAL_SCHEMA_AND_EXACT_STRUCTURAL_ARITHMETIC_PREFLIGHT_FOR_ALL_FOUR_ENDPOINTS",
        "excluded": "NO_LIVE_UNIVERSAL_COVERAGE_ADAPTER_OR_MATHEMATICAL_D9_ENDPOINT",
        "boundary_rule": "RECURSIVE_FACET_IS_BOUNDARY_ONLY_UNLESS_A_SEPARATE_STRICT_COFACE_WITNESS_IS_REPLAYED",
    }, "result: coverage")
    require(result["canaries"] == {
        "positive": "PASS_SYNTHETIC_EXACT_GORDAN_PREFLIGHT",
        "negative": "PASS_SYNTHETIC_EXACT_TWO_WITNESS_SEPARATOR_PREFLIGHT",
        "null": "PASS_SYNTHETIC_COMPLETE_SURVIVOR_GAP_PREFLIGHT",
        "timeout": "PASS_SYNTHETIC_HASH_PINNED_FRONTIER_PREFLIGHT",
        "hostile": "PASS_32_OF_32_REJECTED",
    }, "result: canaries")
    require(result["portability"] == {
        "historical_referee": "ca730426cdd5847ae262ddc29c6f4ae98369eba3",
        "availability": "ABSENT_AND_NOT_REQUIRED",
        "replacement": "PINNED_SOURCE_DERIVED_REPLAY_OF_REVIEWED_HEAD_5EFBD07",
        "predecessor_endpoint": "NORMAL_LINK_REDUCTION_NO_GO",
        "scope": "LOCAL_ROUTE_NO_GO_ONLY",
    }, "result: portability")
    require(result["source_accounting"] == {
        "used": "22 SHA-256-pinned opening, canonical V3, predecessor exact-result, independent-referee, schema, fixture, and verifier inputs",
        "unused_or_missing": "Historical referee object ca730426cdd5847ae262ddc29c6f4ae98369eba3 is absent, is recorded only as an immutable identifier, and is never dereferenced. No producer-side acceptance logic is used.",
    }, "result: source accounting")
    require(result["ledger_change_recommended"] == "none", "result: ledger recommendation")
    require(isinstance(result["open_defects"], list) and result["open_defects"] == [
        "No live universal-cut coverage adapter or producer proof object is materialized.",
        "The universal cut theorem and diagonal nine remain open.",
    ], "result: open defects")
    require(
        result["next_action"]
        == "At a frozen integrated head, register only a producer-independent adapter that replays a materialized universal coverage proof or returns the first exact coverage gap; otherwise stop fail-closed.",
        "result: next action",
    )
    require(
        result["semantic_sha256"]
        == object_digest(b"9dvl-d9-universal-cut-result-v1", result),
        "result: semantic digest",
    )
    return result


def run_self_tests() -> tuple[int, int]:
    accepted = 0
    live_rejected = 0
    for certificate in load_fixtures():
        validate_certificate(certificate, allow_fixture=True)
        accepted += 1
        hostile = copy.deepcopy(certificate)
        hostile["mode"] = "LIVE"
        hostile["source_binding"]["source_manifest_sha256"] = sha256_path(SOURCE_MANIFEST)
        hostile["semantic_sha256"] = object_digest(b"9dvl-d9-universal-cut-certificate-v1", hostile)
        try:
            validate_certificate(hostile)
        except CertificateError as error:
            require("no registered live" in str(error), "self-test: live record failed at wrong gate")
            live_rejected += 1
        else:
            raise CertificateError("self-test: fixture adapter accepted as live")
    return accepted, live_rejected


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--certificate", type=Path)
    parser.add_argument("--self-test-only", action="store_true")
    arguments = parser.parse_args()

    if not arguments.self_test_only:
        manifest = verify_source_manifest()
        print(f"PASS source manifest {len(manifest['used_sha256'])} pinned inputs")
    accepted, live_rejected = run_self_tests()
    print(f"PASS exact endpoint fixtures {accepted}/{accepted}")
    print(f"PASS fixture-only adapters rejected as live {live_rejected}/{live_rejected}")
    if arguments.certificate is not None:
        path = arguments.certificate.resolve()
        try:
            path.relative_to(HERE)
        except ValueError as error:
            raise CertificateError("certificate path escapes owned track") from error
        endpoint, records = validate_certificate(json.loads(path.read_text(encoding="utf-8")))
        print(f"ACCEPT {endpoint} records={records}")
    if not arguments.self_test_only:
        result = verify_result()
        print(f"PASS result handoff {result['outcome']}; mathematical endpoint absent")
    print("SCOPE contract kernel only; v1 registers no live mathematical adapter and changes no theorem ledger")


if __name__ == "__main__":
    main()
