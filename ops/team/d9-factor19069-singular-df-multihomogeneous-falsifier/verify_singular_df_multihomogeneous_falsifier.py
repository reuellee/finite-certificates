#!/usr/bin/env python3
"""Producer-independent falsifier for the factor-19069 singular-df gate.

The verifier rebuilds factor 19069 from the pinned mathematical source, takes
all nine formal derivatives by sparse exponent arithmetic, and rejects the
cycle's affine multihomogeneous/multiaffine premise before any decomposition
claim can be accepted.  It deliberately imports no constructor code.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import struct
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OMREAL = ROOT / "ai" / "omreal"
DATA = OMREAL / "data"
MANIFEST = HERE / "SOURCE_MANIFEST.json"
RESULT = HERE / "RESULT.json"
HOSTILE = HERE / "HOSTILE_TESTS.json"

TARGET_FACTOR = 19069
TARGET_PARENT = 2599
VARIABLES = tuple("abcdefghi")
GROUPS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
EXPECTED_FACTOR_DIGEST = "041227c22bc01ca80df8a66a46099b2f703c53a310fe737dac3981bda5ee20c4"
EXPECTED_DERIVATIVE_DIGESTS = (
    "382f9a12ca2d88fa7c3c67c1c6b13c0b0bf91833978a482220b62eef2e175b3a",
    "247a25f59acfeca0e2492b9f53b2cd1541edafec8a882c57935edd69076bf7ac",
    "c6690d1c5fb151b0e71129ea26e92438e42e720326ed7b9a1b0e6c20a977d6d3",
    "2135c43e43123c23e490f778b7bf661d8c737387e4ba1cede5bd78bbf5302b4f",
    "bedfd41d243f619317d220f743a375850537a5b4057e193b6920296783d8116b",
    "feb633531b931c539632d64665d074effe200db0f58ed7eafc5e05495e0e6bfd",
    "0584e873bfa627a3d9d14c5358f2913d52b3b096ae00428d8039237727842723",
    "edc40934e6e7a48ebd07ce4c42516de5b91ee68e27e71836c729dd9569ca7b58",
    "e68f99acd149c071ddf98ec55766cd5812fc163fcd0d1eb095c7e61085d8d0a9",
)
EXPECTED_DERIVATIVE_TERMS = (54, 44, 54, 50, 50, 50, 36, 61, 36)
EXPECTED_PARENT_DIGEST = "1d9b940e2bb954b5c69bcee8b2346f9554b2e15589ea4c5b3c3f8e1e943de701"
OPENING_REVISION = "a2860f3f6436f573a913fc8ca6312b944212aadd"
HISTORICAL_CONTROL_PATHS = {
    "ops/research-team/PROTOCOL.md",
    "ops/research-team/verify_cycle_protocol.py",
}

sys.path.insert(0, str(OMREAL))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as parent_gate  # noqa: E402


class Reject(AssertionError):
    pass


def require(condition: bool, marker: str) -> None:
    if not condition:
        raise Reject(marker)


def digest_path(path: Path) -> str:
    state = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            state.update(block)
    return state.hexdigest()


def source_digest(relative: str) -> str:
    if relative in HISTORICAL_CONTROL_PATHS:
        frozen = subprocess.check_output(
            ["git", "show", f"{OPENING_REVISION}:{relative}"], cwd=ROOT
        )
        return sha256(frozen).hexdigest()
    return digest_path(ROOT / relative)


def sparse_digest(polynomial: dict[tuple[int, ...], int]) -> str:
    rows = sorted([list(exponents) + [coefficient] for exponents, coefficient in polynomial.items()])
    return sha256(json.dumps(rows, separators=(",", ":")).encode("ascii")).hexdigest()


def derivative(polynomial: dict[tuple[int, ...], int], variable: int) -> dict[tuple[int, ...], int]:
    answer = {}
    for exponents, coefficient in polynomial.items():
        power = exponents[variable]
        if power:
            lowered = exponents[:variable] + (power - 1,) + exponents[variable + 1 :]
            answer[lowered] = coefficient * power
    return answer


def candidate_ids() -> tuple[int, ...]:
    raw = (DATA / "DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin").read_bytes()
    header_size = struct.calcsize("<8sIII")
    magic, parent, universe, count = struct.unpack_from("<8sIII", raw)
    require((magic, parent, universe, count) == (b"D3PFC001", 2599, 26740, 17824), "candidate source header")
    require(len(raw) == header_size + 4 * count, "candidate source length")
    values = tuple(item[0] for item in struct.iter_unpack("<I", raw[header_size:]))
    require(values == tuple(sorted(set(values))), "candidate source ordering")
    return values


def reconstruct() -> dict:
    records = [
        json.loads(line)
        for line in (OMREAL / "certs_4_8.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    require(len(records) == 2628, "parent record census")
    require(records[TARGET_PARENT]["verdict"] == "REALIZABLE", "parent realizability")
    parent_sources, parent_digest = parent_gate.parent_polynomials(records[TARGET_PARENT])
    require(parent_digest == EXPECTED_PARENT_DIGEST, "parent source digest")
    require(len(parent_sources) == 70, "parent factor census")
    require(TARGET_FACTOR in candidate_ids(), "factor candidate membership")

    factor = labeled.factor_polynomials()[2][TARGET_FACTOR]
    require(len(factor) == 108, "factor term census")
    require(sparse_digest(factor) == EXPECTED_FACTOR_DIGEST, "factor sparse digest")
    total_degree_set = sorted({sum(exponents) for exponents in factor})
    block_degree_sets = [
        sorted({sum(exponents[index] for index in group) for exponents in factor})
        for group in GROUPS
    ]
    maximum_exponents = [max(exponents[index] for exponents in factor) for index in range(9)]
    derivatives = [derivative(factor, index) for index in range(9)]
    require(tuple(map(len, derivatives)) == EXPECTED_DERIVATIVE_TERMS, "derivative term census")
    require(tuple(map(sparse_digest, derivatives)) == EXPECTED_DERIVATIVE_DIGESTS, "derivative sparse digests")

    # Explicit witnesses prevent a maximum-degree tuple from being confused
    # with homogeneous affine support.
    require((0, 0, 1, 0, 1, 0, 0, 1, 1) in factor, "degree-four witness")
    require((0, 0, 2, 0, 2, 0, 0, 0, 0) in factor, "third-block-degree-zero witness")
    require((2, 0, 0, 0, 0, 1, 0, 1, 1) in factor, "non-multiaffine witness")
    require(total_degree_set == [4, 5, 6], "total degree support")
    require(block_degree_sets == [[1, 2], [1, 2], [0, 1, 2]], "block degree support")
    require(maximum_exponents == [2, 1, 2, 2, 2, 2, 1, 2, 1], "coordinate exponent bounds")
    return {
        "parent_digest": parent_digest,
        "factor": factor,
        "total_degree_set": total_degree_set,
        "block_degree_sets": block_degree_sets,
        "maximum_exponents": maximum_exponents,
        "derivatives": derivatives,
    }


def validate_manifest(candidate: dict) -> None:
    require(candidate["format"] == "d9-factor19069-singular-df-multihomogeneous-falsifier-source-manifest-v1", "manifest format")
    require(candidate["source_count"] == len(candidate["source_sha256"]), "manifest source count")
    for relative, expected in candidate["source_sha256"].items():
        require(source_digest(relative) == expected, f"source pin {relative}")
    require(candidate["producer_code_imported"] is False, "producer independence")
    require(candidate["network_or_connector_used"] is False, "network scope")
    require(candidate["drive_connector_used"] is False, "drive scope")
    require(candidate["github_write"] is False, "github scope")


def hostile_manifest_mutations(stored: dict) -> list[str]:
    mutations: list[tuple[str, dict]] = []

    def add(marker: str, edit) -> None:
        candidate = deepcopy(stored)
        edit(candidate)
        mutations.append((marker, candidate))

    add("manifest source count", lambda c: c.__setitem__("source_count", 13))
    add("source pin ops/research-team/PROTOCOL.md", lambda c: c["source_sha256"].__setitem__("ops/research-team/PROTOCOL.md", "0" * 64))
    add("source pin ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-singular-df-multihomogeneous-gate1/OPENING_AUDIT.json", lambda c: c["source_sha256"].__setitem__("ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-singular-df-multihomogeneous-gate1/OPENING_AUDIT.json", "0" * 64))
    add("producer independence", lambda c: c.__setitem__("producer_code_imported", True))
    add("drive scope", lambda c: c.__setitem__("drive_connector_used", True))

    rejected = []
    for marker, candidate in mutations:
        try:
            validate_manifest(candidate)
        except Reject as error:
            require(marker in str(error), f"hostile wrong rejection {marker}: {error}")
            rejected.append(marker)
        else:
            raise Reject(f"hostile mutation accepted: {marker}")
    require(len(rejected) == len(mutations) == 5, "hostile manifest mutation census")
    return rejected


def validate_claim(candidate: dict, replay: dict) -> None:
    require(candidate["format"] == "d9-factor19069-singular-df-multihomogeneous-falsifier-result-v1", "result format")
    require(candidate["track_id"] == "d9-factor19069-singular-df-multihomogeneous-falsifier", "track identity")
    require(candidate["outcome"] == "pass", "lane outcome")
    require(candidate["classification"] == "EXACT_AFFINE_BLOCK_STRUCTURE_PREMISE_REJECTED_FAIL_CLOSED", "endpoint classification")
    require(candidate["endpoint"] == "STOP_BEFORE_DECOMPOSITION_AT_FALSE_BLOCK_STRUCTURE_PREMISE", "endpoint selection")
    target = candidate["target"]
    require(target == {"parent_index": 2599, "factor_id": 19069, "ring": "Q[a,b,c,d,e,f,g,h,i]"}, "target identity")

    source = candidate["independent_source_reconstruction"]
    require(source["factor_sparse_terms"] == len(replay["factor"]) == 108, "factor term claim")
    require(source["factor_sparse_sha256"] == EXPECTED_FACTOR_DIGEST, "factor digest claim")
    require(source["total_degree_set"] == replay["total_degree_set"] == [4, 5, 6], "total degree claim")
    require(source["maximum_total_degree"] == 6, "maximum total degree claim")
    require(source["block_partition"] == [["a", "b", "c"], ["d", "e", "f"], ["g", "h", "i"]], "block partition")
    require(source["block_degree_sets"] == replay["block_degree_sets"], "block degree claim")
    require(source["block_multidegree_upper_bound"] == [2, 2, 2], "block upper bound")
    require(source["affine_total_homogeneous"] is False, "affine homogeneity rejection")
    require(source["affine_block_multihomogeneous"] is False, "block homogeneity rejection")
    require(source["coordinate_maximum_exponents"] == replay["maximum_exponents"], "coordinate exponent claim")
    require(source["coordinate_multiaffine"] is False, "multiaffinity rejection")
    require(source["parent_factor_count"] == 70, "parent factor claim")
    require(source["parent_sign_digest"] == replay["parent_digest"], "parent digest claim")

    ideal = candidate["singular_ideal_reconstruction"]
    require(ideal["generators"] == ["f_19069"] + [f"df_d{variable}" for variable in VARIABLES], "singular ideal generators")
    require(ideal["generator_count"] == 10, "singular ideal generator count")
    require(ideal["derivative_variables"] == list(VARIABLES), "derivative variable order")
    require(ideal["derivative_term_counts"] == list(EXPECTED_DERIVATIVE_TERMS), "derivative term claim")
    require(ideal["derivative_sparse_sha256"] == list(EXPECTED_DERIVATIVE_DIGESTS), "derivative digest claim")
    require(ideal["derivatives_rebuilt_by_sparse_exponent_arithmetic"] is True, "derivative reconstruction method")

    audit = candidate["downstream_fail_closed_audit"]
    require(audit["characteristic_zero_decomposition"] == "NOT_REACHED_AFTER_EXACT_PRECONDITION_REJECTION", "decomposition status")
    require(audit["component_equations"] is None, "component equation overclaim")
    require(audit["embedded_components_accounted"] is False, "embedded component overclaim")
    require(audit["dimensions"] is None, "dimension overclaim")
    require(audit["degrees"] is None, "degree overclaim")
    require(audit["multiplicities"] is None, "multiplicity overclaim")
    require(audit["componentwise_parent_factor_tests_completed"] == 0, "parent incidence overclaim")
    require(audit["parent_factor_tests_required_per_component"] == 70, "parent incidence scope")
    require(audit["strict_real_residence"] == "UNRESOLVED", "real residence overclaim")
    require(audit["connected_parent_tag"] == "UNRESOLVED", "connected parent overclaim")
    require(audit["singular_strata_discarded"] == 0, "singular stratum loss")
    require(audit["boundary_strata_discarded"] == 0, "boundary stratum loss")

    guards = candidate["scope_guards"]
    require(guards["seventy_inverse_variable_discovery_used"] is False, "inverse discovery prohibition")
    require(guards["numerical_or_modular_evidence_promoted"] is False, "numerical promotion prohibition")
    require(guards["sampled_or_projection_inference_used"] is False, "sampled route prohibition")
    require(guards["producer_acceptance_logic_imported"] is False, "producer logic prohibition")
    require(guards["homogenization_claimed_without_explicit_construction"] is False, "homogenization overclaim")

    resources = candidate["resource_accounting"]
    require(resources["wall_minutes_ceiling"] == 35, "wall resource ceiling")
    require(resources["cpu_hours_ceiling"] == 2, "cpu resource ceiling")
    require(resources["memory_gib_ceiling"] == 8, "memory resource ceiling")
    require(resources["hostile_mutations_minimum"] == 18, "hostile minimum")
    require(resources["hostile_mutations_executed"] == 59, "hostile resource accounting")
    require(resources["ceiling_crossed"] is False, "resource crossing")
    require(resources["external_compute_used"] is False, "external compute scope")

    endpoints = candidate["endpoint_accounting"]
    require(endpoints["positive"] is False, "positive endpoint overclaim")
    require(endpoints["negative"] is False, "negative endpoint overclaim")
    require(endpoints["null"] is True, "null endpoint missing")
    require(endpoints["timeout"] is False, "timeout endpoint mismatch")
    require(endpoints["first_unresolved_branch"] == "AFFINE_BLOCK_STRUCTURE_PRECONDITION", "first unresolved branch")
    require(candidate["ledger_delta"] == "none", "ledger delta")
    require(candidate["theorem_ledger"] == "2/9", "ledger scope")
    require(candidate["ledger_promotion_recommended"] is False, "ledger promotion")


def hostile_mutations(stored: dict, replay: dict) -> list[str]:
    mutations: list[tuple[str, dict]] = []

    def add(marker: str, edit) -> None:
        candidate = deepcopy(stored)
        edit(candidate)
        mutations.append((marker, candidate))

    add("track identity", lambda c: c.__setitem__("track_id", "constructor"))
    add("target identity", lambda c: c["target"].__setitem__("factor_id", 19068))
    add("factor term claim", lambda c: c["independent_source_reconstruction"].__setitem__("factor_sparse_terms", 107))
    add("factor digest claim", lambda c: c["independent_source_reconstruction"].__setitem__("factor_sparse_sha256", "0" * 64))
    add("total degree claim", lambda c: c["independent_source_reconstruction"].__setitem__("total_degree_set", [6]))
    add("maximum total degree claim", lambda c: c["independent_source_reconstruction"].__setitem__("maximum_total_degree", 5))
    add("block partition", lambda c: c["independent_source_reconstruction"]["block_partition"][0].reverse())
    add("block degree claim", lambda c: c["independent_source_reconstruction"].__setitem__("block_degree_sets", [[2], [2], [2]]))
    add("block upper bound", lambda c: c["independent_source_reconstruction"].__setitem__("block_multidegree_upper_bound", [2, 2, 1]))
    add("affine homogeneity rejection", lambda c: c["independent_source_reconstruction"].__setitem__("affine_total_homogeneous", True))
    add("block homogeneity rejection", lambda c: c["independent_source_reconstruction"].__setitem__("affine_block_multihomogeneous", True))
    add("coordinate exponent claim", lambda c: c["independent_source_reconstruction"].__setitem__("coordinate_maximum_exponents", [1] * 9))
    add("multiaffinity rejection", lambda c: c["independent_source_reconstruction"].__setitem__("coordinate_multiaffine", True))
    add("parent factor claim", lambda c: c["independent_source_reconstruction"].__setitem__("parent_factor_count", 69))
    add("parent digest claim", lambda c: c["independent_source_reconstruction"].__setitem__("parent_sign_digest", "0" * 64))
    add("singular ideal generators", lambda c: c["singular_ideal_reconstruction"]["generators"].pop())
    add("singular ideal generator count", lambda c: c["singular_ideal_reconstruction"].__setitem__("generator_count", 9))
    add("derivative variable order", lambda c: c["singular_ideal_reconstruction"]["derivative_variables"].reverse())
    add("derivative term claim", lambda c: c["singular_ideal_reconstruction"]["derivative_term_counts"].__setitem__(0, 53))
    add("derivative digest claim", lambda c: c["singular_ideal_reconstruction"]["derivative_sparse_sha256"].__setitem__(4, "0" * 64))
    add("derivative reconstruction method", lambda c: c["singular_ideal_reconstruction"].__setitem__("derivatives_rebuilt_by_sparse_exponent_arithmetic", False))
    add("decomposition status", lambda c: c["downstream_fail_closed_audit"].__setitem__("characteristic_zero_decomposition", "COMPLETE"))
    add("component equation overclaim", lambda c: c["downstream_fail_closed_audit"].__setitem__("component_equations", []))
    add("embedded component overclaim", lambda c: c["downstream_fail_closed_audit"].__setitem__("embedded_components_accounted", True))
    add("dimension overclaim", lambda c: c["downstream_fail_closed_audit"].__setitem__("dimensions", [0]))
    add("degree overclaim", lambda c: c["downstream_fail_closed_audit"].__setitem__("degrees", [1]))
    add("multiplicity overclaim", lambda c: c["downstream_fail_closed_audit"].__setitem__("multiplicities", [1]))
    add("parent incidence overclaim", lambda c: c["downstream_fail_closed_audit"].__setitem__("componentwise_parent_factor_tests_completed", 70))
    add("parent incidence scope", lambda c: c["downstream_fail_closed_audit"].__setitem__("parent_factor_tests_required_per_component", 69))
    add("real residence overclaim", lambda c: c["downstream_fail_closed_audit"].__setitem__("strict_real_residence", "EMPTY"))
    add("connected parent overclaim", lambda c: c["downstream_fail_closed_audit"].__setitem__("connected_parent_tag", "EXCLUDED"))
    add("singular stratum loss", lambda c: c["downstream_fail_closed_audit"].__setitem__("singular_strata_discarded", 1))
    add("boundary stratum loss", lambda c: c["downstream_fail_closed_audit"].__setitem__("boundary_strata_discarded", 1))
    add("inverse discovery prohibition", lambda c: c["scope_guards"].__setitem__("seventy_inverse_variable_discovery_used", True))
    add("numerical promotion prohibition", lambda c: c["scope_guards"].__setitem__("numerical_or_modular_evidence_promoted", True))
    add("sampled route prohibition", lambda c: c["scope_guards"].__setitem__("sampled_or_projection_inference_used", True))
    add("producer logic prohibition", lambda c: c["scope_guards"].__setitem__("producer_acceptance_logic_imported", True))
    add("homogenization overclaim", lambda c: c["scope_guards"].__setitem__("homogenization_claimed_without_explicit_construction", True))
    add("wall resource ceiling", lambda c: c["resource_accounting"].__setitem__("wall_minutes_ceiling", 36))
    add("cpu resource ceiling", lambda c: c["resource_accounting"].__setitem__("cpu_hours_ceiling", 3))
    add("memory resource ceiling", lambda c: c["resource_accounting"].__setitem__("memory_gib_ceiling", 16))
    add("hostile minimum", lambda c: c["resource_accounting"].__setitem__("hostile_mutations_minimum", 17))
    add("resource crossing", lambda c: c["resource_accounting"].__setitem__("ceiling_crossed", True))
    add("external compute scope", lambda c: c["resource_accounting"].__setitem__("external_compute_used", True))
    add("positive endpoint overclaim", lambda c: c["endpoint_accounting"].__setitem__("positive", True))
    add("negative endpoint overclaim", lambda c: c["endpoint_accounting"].__setitem__("negative", True))
    add("null endpoint missing", lambda c: c["endpoint_accounting"].__setitem__("null", False))
    add("timeout endpoint mismatch", lambda c: c["endpoint_accounting"].__setitem__("timeout", True))
    add("first unresolved branch", lambda c: c["endpoint_accounting"].__setitem__("first_unresolved_branch", "COMPONENT_0"))
    add("endpoint selection", lambda c: c.__setitem__("endpoint", "POSITIVE"))
    add("endpoint classification", lambda c: c.__setitem__("classification", "COMPLETE"))
    add("ledger delta", lambda c: c.__setitem__("ledger_delta", "+1"))
    add("ledger scope", lambda c: c.__setitem__("theorem_ledger", "3/9"))
    add("ledger promotion", lambda c: c.__setitem__("ledger_promotion_recommended", True))

    rejected = []
    for marker, candidate in mutations:
        try:
            validate_claim(candidate, replay)
        except Reject as error:
            require(marker in str(error), f"hostile wrong rejection {marker}: {error}")
            rejected.append(marker)
        else:
            raise Reject(f"hostile mutation accepted: {marker}")
    require(len(rejected) == len(mutations) == 54, "hostile mutation census")
    return rejected


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE.read_text(encoding="utf-8"))
    validate_manifest(manifest)
    replay = reconstruct()
    validate_claim(result, replay)
    rejected = hostile_manifest_mutations(manifest) + hostile_mutations(result, replay)
    require(hostile["total"] == hostile["rejected"] == len(rejected), "hostile manifest census")
    require(hostile["rejection_markers"] == rejected, "hostile manifest markers")
    print("PASS independent factor-19069 source reconstruction: 108 terms")
    print("PASS original singular ideal reconstruction: f plus 9 exact derivatives")
    print("REJECT affine homogeneity: total-degree support is [4, 5, 6]")
    print("REJECT block multihomogeneity: degree supports are [1,2], [1,2], [0,1,2]")
    print("REJECT coordinate multiaffinity: maximum exponents are [2,1,2,2,2,2,1,2,1]")
    print(f"PASS hostile_mutations={len(rejected)}/59 rejected")
    print("CLASSIFICATION EXACT_AFFINE_BLOCK_STRUCTURE_PREMISE_REJECTED_FAIL_CLOSED ledger=2/9")


if __name__ == "__main__":
    main()
