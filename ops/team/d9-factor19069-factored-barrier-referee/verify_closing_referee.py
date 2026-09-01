#!/usr/bin/env python3
"""Standalone frozen-head referee for the factor-19069 barrier null.

The mathematical candidate and the later coordination evidence are read from
two immutable Git objects.  This verifier imports no constructor, falsifier,
or certificate acceptance module.  It independently checks the stored
factored-circuit/null-envelope semantics, then executes the frozen replay
programs as separate processes.
"""

from __future__ import annotations

import ast
from copy import deepcopy
from hashlib import sha256
from itertools import combinations
import json
import os
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESULT_PATH = HERE / "RESULT.json"
REFEREE_REL = "ops/team/d9-factor19069-factored-barrier-referee"
CYCLE_REL = "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-factored-barrier-gate1"

CANDIDATE = "9a7e2a32b5a659372cbc435ae5404bc02141d37e"
CANDIDATE_TREE = "aa571b94aa1d9f281b032e3b362e370711d26916"
CLOSING_EVIDENCE = "9411e9c403fbf98b5e1e76c049a0d7fdb343b7ef"
CLOSING_EVIDENCE_TREE = "7024e26a67df73d91872783f08acd863fde4daad"
OPENING = "d12dbaf7cfb7312d9d603c8938dd8ad6ce62166e"
OPENING_TREE = "221e574fd705aff50f667ebc72345a36afc4f5d7"
BASE = "b71c139a3c64cde3442252f8f3d46f2d893978c5"
BASE_TREE = "7a9da9f02369831bd34bc22f39a0bbad57725522"

ENDPOINT = "HASH_PINNED_FACTORED_BARRIER_CRITICAL_COMPONENT_FRONTIER_WITH_FIRST_UNSAMPLED_COMPONENT"
CLASSIFICATION = "EXACT_FAIL_CLOSED_FACTORED_BARRIER_COMPONENT_NULL"
SUCCESSOR = "D9_ROW2599_FACTOR19069_FACTORED_CRITICAL_EQUIDIMENSIONAL_DECOMPOSITION_GATE1"
RETIRED = "BLIND_FACTORED_BARRIER_COMPONENT_SAMPLER_BUDGET_ESCALATION"
PYTHON = r"C:\Users\reuel\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe"

FRONTIER_REL = "ops/team/d9-factor19069-factored-barrier-constructor/FACTORED_BARRIER_FRONTIER.json"
CONSTRUCTOR_RESULT_REL = "ops/team/d9-factor19069-factored-barrier-constructor/RESULT.json"
CONSTRUCTOR_MANIFEST_REL = "ops/team/d9-factor19069-factored-barrier-constructor/SOURCE_MANIFEST.json"
FALSIFIER_RESULT_REL = "ops/team/d9-factor19069-factored-barrier-falsifier/RESULT.json"
FALSIFIER_MANIFEST_REL = "ops/team/d9-factor19069-factored-barrier-falsifier/SOURCE_MANIFEST.json"
CERTIFICATE_RESULT_REL = "ops/team/d9-factor19069-factored-barrier-certificate/RESULT.json"
CERTIFICATE_VERIFY_REL = "ops/team/d9-factor19069-factored-barrier-certificate/verify_factored_barrier_certificate.py"

CANDIDATE_PINS = {
    "ops/team/d9-factor19069-factored-barrier-certificate/FINDINGS.md": "9258ac04d180783440600b53c07ba66c97288d2cf37268987b21f09536f4df5a",
    CERTIFICATE_RESULT_REL: "c1a8a88cf117f34173925f436c131fc571a4efa4d946aeb3def2b2b984e04310",
    CERTIFICATE_VERIFY_REL: "d5a485610ecf1eea95c04782c518089477ea9cdf2078f81fed977149caa34db5",
    FRONTIER_REL: "3f75eeb2f7433234206292012c527604517b516ee904e2ab1d1969e49ed1e8ca",
    "ops/team/d9-factor19069-factored-barrier-constructor/FINDINGS.md": "51d898f19b8d7132e52a4cd7161b2aea2f98b9b81b74a6a3663e5e40d2c0766c",
    CONSTRUCTOR_RESULT_REL: "5d9357346077562824c4564829260d49b6fa62ceea38b7ae3f7fe5543dee029a",
    CONSTRUCTOR_MANIFEST_REL: "17bc476bfc78d629353f4fe73d24495de40de5a926aa5e8df4ed524131b3d303",
    "ops/team/d9-factor19069-factored-barrier-constructor/build_factored_barrier_frontier.py": "c1d4622ce35e07cc84d0cfa76a1d7760fca87fd234183101c790443b20938003",
    "ops/team/d9-factor19069-factored-barrier-constructor/verify_factored_barrier_frontier.py": "86245950996cfbc4b49d2c802f6c1ffeed9b789a64646a43bca013af01f1bdf7",
    "ops/team/d9-factor19069-factored-barrier-falsifier/FINDINGS.md": "b70e6a315f8e936941595a602c7c042ac53926305595d5be410d8e3d59a40df3",
    "ops/team/d9-factor19069-factored-barrier-falsifier/HOSTILE_TESTS.json": "e50b911ee8ebcff133fe37c7685bbc055635c8144573f5ac3e0836a11ffcbbb7",
    FALSIFIER_RESULT_REL: "9af35e89fafd73e71d940750d1f49ae166cc3e634a3f8ea2e02d3371f0ddf022",
    FALSIFIER_MANIFEST_REL: "5b8787839c2ac4d44850f05ab1e4fd3a47d80d47511a21020c13680872ca6172",
    "ops/team/d9-factor19069-factored-barrier-falsifier/verify_factored_barrier_falsifier.py": "8dc7adc67aef34651ac3ce3e97f4abaa3030fbc7732fd0e3922d95af64425965",
}

OPENING_PROTOCOL_PINS = {
    "ops/research-team/PROTOCOL.md": "54f1a15b7774085005707727780b266ffbd4a8edc4687fe14e1e6bc76d229031",
    "ops/research-team/verify_cycle_protocol.py": "4d9e16daed0de08af415e95c746803b512ea8b92c452df6df2c9e09fdcd3b7d1",
    f"{CYCLE_REL}/CYCLE.md": "32f38adfb370a4c82b33640863ac41674707cec2254cd0a80d0aa2f46829585f",
    f"{CYCLE_REL}/WORK_ORDERS.yaml": "7feb9e3ee717dd68f224886ce2e4fa1be78e869a9ee2ee708171988ac9eec6e0",
    f"{CYCLE_REL}/OPENING_AUDIT.json": "fa6338b7a42fa333e32c27916dbea0f1c9f50f0eeb4cbbe016cf04f59782cace",
    f"{CYCLE_REL}/verify_opening_audit.py": "454ad11ef6364d9902e1c1f677187c206d3b79f50636a63418c667bc64c2d1d2",
}

CLOSING_PINS = {
    f"{CYCLE_REL}/CLOSING_MANIFEST.json": "70d9ec0cb1935b769c812d6d2a663e414f65199a6f25c17805c4b252ca7cb11c",
    f"{CYCLE_REL}/CLEAN_REPLAY.json": "f5514e8ed740a5c35ddf1895e9fa774514105208567da1097729f262aa9bba7c",
    f"{CYCLE_REL}/CYCLE_REPORT.md": "c2fa71aa6d893a132a1fb1bec1dda1385409b6d792922c4bf19c6ddc96b3c433",
}

REPLAY_SCRIPTS = (
    "ai/omreal/verify_canonical_research_state_v6.py",
    f"{CYCLE_REL}/verify_opening_audit.py",
    "ops/team/d9-factor19069-factored-barrier-constructor/verify_factored_barrier_frontier.py",
    "ops/team/d9-factor19069-factored-barrier-falsifier/verify_factored_barrier_falsifier.py",
    CERTIFICATE_VERIFY_REL,
)


class Reject(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def git(*arguments: str, binary: bool = False):
    value = subprocess.check_output(["git", *arguments], cwd=ROOT, text=not binary)
    return value if binary else value.strip()


def frozen(revision: str, path: str) -> bytes:
    return git("show", f"{revision}:{path}", binary=True)


def digest(value: bytes) -> str:
    return sha256(value).hexdigest()


def canonical_digest(value) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return digest(encoded)


def semantic_digest(candidate: dict) -> str:
    unsealed = deepcopy(candidate)
    unsealed.pop("semantic_sha256", None)
    return canonical_digest(unsealed)


def load_frozen_json(revision: str, path: str) -> dict:
    return json.loads(frozen(revision, path).decode("utf-8"))


def decode_sparse(rows: list[dict], marker: str) -> dict[tuple[int, ...], int]:
    require(all(set(row) == {"exponents", "coefficient"} for row in rows), f"{marker} sparse schema")
    keys = [tuple(row["exponents"]) for row in rows]
    require(len(keys) == len(set(keys)), f"{marker} sparse uniqueness")
    require(all(len(key) == 9 and all(isinstance(x, int) and x >= 0 for x in key) for key in keys), f"{marker} exponents")
    require(all(isinstance(row["coefficient"], int) and row["coefficient"] for row in rows), f"{marker} coefficients")
    return {key: row["coefficient"] for key, row in zip(keys, rows, strict=True)}


def differentiate(polynomial: dict[tuple[int, ...], int], coordinate: int) -> dict[tuple[int, ...], int]:
    answer = {}
    for exponents, coefficient in polynomial.items():
        power = exponents[coordinate]
        if power:
            reduced = list(exponents)
            reduced[coordinate] -= 1
            answer[tuple(reduced)] = coefficient * power
    return answer


def validate_frozen_revisions() -> None:
    require(git("rev-parse", f"{CANDIDATE}^{{commit}}") == CANDIDATE, "candidate revision moved")
    require(git("rev-parse", f"{CANDIDATE}^{{tree}}") == CANDIDATE_TREE, "candidate tree moved")
    require(git("rev-parse", f"{CLOSING_EVIDENCE}^{{commit}}") == CLOSING_EVIDENCE, "closing evidence revision moved")
    require(git("rev-parse", f"{CLOSING_EVIDENCE}^{{tree}}") == CLOSING_EVIDENCE_TREE, "closing evidence tree moved")
    require(git("rev-parse", f"{CLOSING_EVIDENCE}^") == CANDIDATE, "closing evidence parent")
    require(git("rev-parse", f"{OPENING}^{{tree}}") == OPENING_TREE, "opening tree")
    require(git("rev-parse", f"{BASE}^{{tree}}") == BASE_TREE, "base tree")
    changed = git("diff", "--name-only", CANDIDATE, CLOSING_EVIDENCE).splitlines()
    require(set(changed) == set(CLOSING_PINS), "candidate/closing evidence scope")
    ancestor = subprocess.run(["git", "merge-base", "--is-ancestor", CLOSING_EVIDENCE, "HEAD"], cwd=ROOT)
    require(ancestor.returncode == 0, "review branch does not descend from closing evidence")


def validate_pins() -> None:
    for revision, pins, marker in (
        (CANDIDATE, OPENING_PROTOCOL_PINS, "opening/protocol pin"),
        (CANDIDATE, CANDIDATE_PINS, "candidate artifact pin"),
        (CLOSING_EVIDENCE, CLOSING_PINS, "closing evidence pin"),
    ):
        for path, expected in pins.items():
            data = frozen(revision, path)
            require(digest(data) == expected, f"{marker} {path}")
            require((ROOT / path).read_bytes() == data, f"post-frozen drift {path}")

    changed = set(git("diff", "--name-only", CLOSING_EVIDENCE, "--").splitlines())
    require(all(path == REFEREE_REL or path.startswith(f"{REFEREE_REL}/") for path in changed), "edits outside referee surface")
    untracked = set(git("ls-files", "--others", "--exclude-standard").splitlines())
    require(all(path.startswith(f"{REFEREE_REL}/") for path in untracked), "untracked file outside referee surface")


def validate_frontier(candidate: dict) -> None:
    require(candidate["semantic_sha256"] == semantic_digest(candidate), "frontier semantic digest")
    require(candidate["format"] == "d9-factor19069-factored-barrier-frontier-v1", "frontier format")
    require(candidate["classification"] == CLASSIFICATION, "frontier classification")
    require(candidate["endpoint"] == ENDPOINT, "frontier endpoint")
    require(candidate["target"] == {
        "ambient_parameter_dimension": 9,
        "factor_id": 19069,
        "fixed_skeleton_edges": 40,
        "parent_index": 2599,
        "parent_sign_digest": "1d9b940e2bb954b5c69bcee8b2346f9554b2e15589ea4c5b3c3f8e1e943de701",
        "parent_sign_factors": 70,
    }, "target inventory")
    require(candidate["producer_independent_certificate_present"] is False, "premature producer certificate")
    require(candidate["ledger_change_recommended"] == "none" and candidate["theorem_ledger"] == "2/9", "frontier ledger")

    circuit = candidate["factor_circuit"]
    require(candidate["factor_circuit_semantic_sha256"] == canonical_digest(circuit), "factor circuit digest")
    require(circuit["format"] == "factor-circuit-dB-wedge-df-v1" and circuit["coordinates"] == list("abcdefghi"), "factor circuit format")
    parents = circuit["parent_factor_nodes"]
    require(len(parents) == 70, "factor circuit parent factor nodes")
    ids = [node["node_id"] for node in parents]
    require(len(ids) == len(set(ids)) == 70, "factor circuit factor identities")
    parent_polynomials = []
    for index, node in enumerate(parents):
        require(node["node_id"].startswith(f"H_{index:02d}_") and node["node_id"].endswith(node["label"]), "factor circuit parent ordering")
        require(node["source_target_sign"] in (-1, 1), "factor circuit source sign")
        polynomial = decode_sparse(node["sparse_polynomial"], f"factor circuit parent {index}")
        require(node["term_count"] == len(polynomial), "factor circuit parent term census")
        require(node["degree"] == max(map(sum, polynomial)), "factor circuit parent degree")
        parent_polynomials.append(polynomial)
    require(sum(len(poly) for poly in parent_polynomials) == 209, "factor circuit parent sparse terms")

    barrier = circuit["barrier"]
    require(set(barrier) == {"node_id", "operation", "ordered_factor_node_ids", "factor_count", "total_degree", "expanded_polynomial_present"}, "factor circuit expanded payload")
    require(barrier["node_id"] == "B" and barrier["operation"] == "PRODUCT", "factor circuit product")
    require(barrier["ordered_factor_node_ids"] == ids and barrier["factor_count"] == 70, "factor circuit factor provenance")
    require(barrier["total_degree"] == 90 and barrier["expanded_polynomial_present"] is False, "factor circuit factored barrier")

    derivatives = circuit["barrier_derivative_nodes"]
    require(len(derivatives) == 9, "factor circuit dB coordinates")
    for coordinate, node in enumerate(derivatives):
        require(node["coordinate_index"] == coordinate and node["node_id"] == f"dB_d{'abcdefghi'[coordinate]}", "factor circuit dB ordering")
        require(len(node["summands"]) == 70, "factor circuit dB summands")
        for index, summand in enumerate(node["summands"]):
            require(summand["differentiated_factor_index"] == index, "factor circuit differentiated provenance")
            require(summand["multiply_all_factor_indices_except"] == index, "factor circuit complementary provenance")
            stored = decode_sparse(summand["derivative_sparse_polynomial"], f"factor circuit dB {coordinate}:{index}")
            require(stored == differentiate(parent_polynomials[index], coordinate), "factor circuit derivative membership")
    require(sum(len(node["summands"]) for node in derivatives) == 630, "factor circuit derivative census")

    wall = circuit["wall_polynomial"]
    wall_polynomial = decode_sparse(wall["sparse_polynomial"], "factor circuit wall")
    require((wall["node_id"], wall["degree"], wall["multidegree"], wall["term_count"]) == ("f_19069", 6, [2, 2, 2], 108), "factor circuit wall census")
    require(len(wall_polynomial) == 108, "factor circuit wall terms")
    wall_derivatives = circuit["wall_derivative_nodes"]
    require(len(wall_derivatives) == 9, "factor circuit df coordinates")
    for coordinate, node in enumerate(wall_derivatives):
        require(node["node_id"] == f"df_d{'abcdefghi'[coordinate]}" and node["coordinate_index"] == coordinate, "factor circuit df ordering")
        require(decode_sparse(node["sparse_polynomial"], f"factor circuit df {coordinate}") == differentiate(wall_polynomial, coordinate), "factor circuit df membership")
    wedges = circuit["wedge_equation_nodes"]
    require(len(wedges) == 36, "factor circuit wedge census")
    for node, (left, right) in zip(wedges, combinations(range(9), 2), strict=True):
        lvar, rvar = "abcdefghi"[left], "abcdefghi"[right]
        require(node["coordinate_pair"] == [left, right], "factor circuit wedge order")
        require(node["inputs"] == [f"dB_d{lvar}", f"df_d{rvar}", f"dB_d{rvar}", f"df_d{lvar}"], "factor circuit wedge membership")

    interior = candidate["strict_interior_critical_frontier"]
    require(interior["systems_constructed"] == len(interior["systems"]) == 1, "critical system count")
    require(interior["connected_components_sampled"] == 0 and interior["zero_dimensional_components_sampled"] == 0 and interior["positive_dimensional_components_sampled"] == 0, "critical component samples")
    require(interior["singular_pieces_discarded"] == 0, "critical singular scope")
    system = interior["systems"][0]
    require(system["semantic_sha256"] == canonical_digest({key: value for key, value in system.items() if key != "semantic_sha256"}), "critical system digest")
    require(system["stratum_id"] == "FB-C0-STRICT-INTERIOR-FULL-SUPPORT" and system["support"] == [15, 15, 15], "critical first unsampled stratum")
    require(system["equalities"] == ["f_19069=0", "all_36_coefficients_of_dB_wedge_df=0"], "critical equations")
    require(system["strict_inequalities"] == [f"{node}>0" for node in ids], "critical parent inventory")
    require(system["possible_component_dimensions"] == list(range(9)) and system["positive_dimensional_pieces_required"] is True, "critical positive-dimensional scope")
    require(system["singular_wall_pieces_included"] is True, "critical singular pieces")
    require(system["connected_parent_selector"] == "EXACT_PATH_IN_STRICT_PARENT_SIGN_SET_TO_PINNED_SAMPLE_REQUIRED", "critical connected-parent selector")
    require(system["component_decomposition_status"] == "UNSAMPLED_FAIL_CLOSED", "critical decomposition status")
    first = interior["first_unsampled_component_or_stratum"]
    require(first["stratum_id"] == system["stratum_id"] and first["stratum_semantic_sha256"] == system["semantic_sha256"], "critical first-unsampled binding")

    boundary = candidate["true_boundary_frontier"]
    expected_supports = [[1, 1, 1], [1, 1, 5], [3, 1, 1], [3, 1, 5], [3, 1, 15], [3, 3, 7], [3, 3, 15], [7, 7, 7], [15, 1, 15], [15, 7, 15]]
    require((boundary["ambient_product_support_strata"], boundary["parent_bernstein_excluded_support_strata"], boundary["proper_nonexcluded_candidate_strata"]) == (3375, 3364, 10), "boundary support census")
    require([record["support"] for record in boundary["records"]] == expected_supports, "boundary support completeness")
    require(all(record["wall_component_residence"] == "UNCLASSIFIED_FAIL_CLOSED" for record in boundary["records"]), "boundary wall residence")
    certified = [record for record in boundary["records"] if record["parent_component_closure_path"]["status"].startswith("CERTIFIED")]
    require(len(certified) == boundary["certified_witness_paths_to_pinned_parent_closure"] == 1 and certified[0]["support"] == [15, 7, 15], "boundary certified path")
    require(boundary["records"][0]["parent_component_closure_path"]["first_rejection"]["label"] == "2578", "boundary first rejected path")
    require(boundary["wall_component_residence_classified_strata"] == 0, "boundary classification count")
    first_boundary = boundary["first_unclassified_boundary_stratum"]
    require(first_boundary["support"] == [1, 1, 1] and first_boundary["record_semantic_sha256"] == canonical_digest(boundary["records"][0]), "boundary first unclassified binding")
    require(boundary["true_parent_boundary_kept_distinct_from"] == ["SOLVER_BOUNDARY", "BOX_BOUNDARY", "COLLAR_BOUNDARY", "SKELETON_EDGE_ENDPOINT"], "boundary artificial-boundary separation")

    skeleton = candidate["fixed_skeleton_accounting"]
    require(skeleton["all_40_edges_retain_all_70_parent_tags"] is True and skeleton["parent_path_tag_checks"] == 2800, "skeleton parent tags")
    roots = skeleton["factor19069_open_root_counts_by_edge"]
    require(len(roots) == 40 and [edge for edge, count in roots.items() if count] == ["39"] and roots["39"] == 1, "skeleton root census")
    anchor = skeleton["exact_attached_wall_anchor"]
    require(anchor["edge_index"] == 39 and anchor["attachment"] == "LIES_ON_FIXED_SKELETON_EDGE_39", "edge39 anchor")
    require(anchor["barrier_critical_sample"] is False, "collar globalization")
    require(skeleton["global_wall_component_count"] is None and skeleton["global_attached_component_count"] is None and skeleton["global_unattached_component_count"] is None, "attachment global counts")
    require(skeleton["attachment_classification_complete"] is False, "attachment completeness")
    resources = candidate["resource_accounting"]
    require(resources["exact_solver_component_nodes_used"] == 0 and resources["max_exact_solver_component_nodes"] == 500000, "resource accounting")
    require(resources["paid_or_external_compute"] is False, "external compute scope")


def validate_handoffs(frontier: dict) -> None:
    constructor = load_frozen_json(CANDIDATE, CONSTRUCTOR_RESULT_REL)
    falsifier = load_frozen_json(CANDIDATE, FALSIFIER_RESULT_REL)
    certificate = load_frozen_json(CANDIDATE, CERTIFICATE_RESULT_REL)
    require(constructor["classification"] == CLASSIFICATION and constructor["endpoint"] == ENDPOINT, "constructor endpoint")
    require(constructor["frontier_sha256"] == CANDIDATE_PINS[FRONTIER_REL], "constructor frontier pin")
    require(constructor["critical_frontier"]["connected_components_sampled"] == 0, "constructor component scope")
    require(constructor["true_boundary"]["wall_component_residence_classified_strata"] == 0, "constructor boundary scope")
    require(constructor["fixed_skeleton"]["attachment_classification_complete"] is False, "constructor attachment scope")
    require(constructor["theorem_ledger"] == "2/9" and constructor["ledger_change_recommended"] == "none", "constructor ledger")
    require(falsifier["classification"] == "EXACT_SCOPE_REJECTION_CONFIRMS_FACTORED_BARRIER_NULL" and falsifier["retained_endpoint"] == ENDPOINT, "falsifier endpoint")
    require(falsifier["constructor_certified"] is False and falsifier["cycle_certificate_issued"] is False, "falsifier scope")
    require(falsifier["hostile_mutations"] == {"rejected": 25, "total": 25}, "falsifier hostile mutations")
    require(certificate["verdict"] == "ACCEPT" and certificate["accepted_endpoint"] == ENDPOINT, "certificate verdict")
    require(certificate["producer_imported"] is False and certificate["falsifier_imported"] is False, "certificate independence")
    require(certificate["component_samples_certified"] == 0 and certificate["attachment_completeness_certified"] is False, "certificate scope")
    require(certificate["hostile_mutations"] == {"rejected": 22, "total": 22}, "certificate hostile mutations")
    require(certificate["theorem_ledger"] == "2/9" and certificate["ledger_change_recommended"] == "none", "certificate ledger")
    for path, expected in certificate["frozen_pins"].items():
        require(path in CANDIDATE_PINS and expected == CANDIDATE_PINS[path], f"certificate frozen pin {path}")

    syntax = ast.parse(frozen(CANDIDATE, CERTIFICATE_VERIFY_REL).decode("utf-8"))
    imports = []
    for node in ast.walk(syntax):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    require(not any("factored_barrier" in name or "falsifier" in name for name in imports), "certificate imports producer acceptance logic")
    require(frontier["endpoint"] == certificate["accepted_endpoint"], "frontier/certificate endpoint binding")


def validate_closing_evidence(manifest: dict, clean: dict) -> None:
    require(manifest["reviewed_revision"] == CANDIDATE and manifest["reviewed_tree"] == CANDIDATE_TREE, "closing manifest reviewed head")
    require(manifest["accepted_classification"] == CLASSIFICATION and manifest["accepted_endpoint"] == ENDPOINT, "closing manifest endpoint")
    expected_manifest_pins = {
        FRONTIER_REL: CANDIDATE_PINS[FRONTIER_REL],
        CONSTRUCTOR_RESULT_REL: CANDIDATE_PINS[CONSTRUCTOR_RESULT_REL],
        FALSIFIER_RESULT_REL: CANDIDATE_PINS[FALSIFIER_RESULT_REL],
        "ops/team/d9-factor19069-factored-barrier-falsifier/verify_factored_barrier_falsifier.py": CANDIDATE_PINS["ops/team/d9-factor19069-factored-barrier-falsifier/verify_factored_barrier_falsifier.py"],
        CERTIFICATE_RESULT_REL: CANDIDATE_PINS[CERTIFICATE_RESULT_REL],
        CERTIFICATE_VERIFY_REL: CANDIDATE_PINS[CERTIFICATE_VERIFY_REL],
    }
    require(manifest["pins"] == expected_manifest_pins, "closing manifest candidate pins")
    require(manifest["clean_replay"] == {"candidate_revision": CANDIDATE, "candidate_tree": CANDIDATE_TREE, "worktree_clean": True, "verdict": "PASS"}, "closing manifest clean replay")
    require(manifest["ledger_delta"] == "none" and manifest["theorem_ledger"] == "2/9" and manifest["diagonal_nine"] == "OPEN", "closing manifest ledger")
    require(manifest["closing_strategy_verdict"] == "PIVOT" and manifest["retired_route"] == RETIRED, "closing manifest strategy")
    require(manifest["precise_successor"] == SUCCESSOR, "closing manifest successor")
    storage = manifest["storage"]
    require(storage["durable_project_root"] == r"E:\Projects\9DVL Research", "closing storage root")
    require(storage["drive_connector_used"] is False, "closing Drive scope")
    require(storage["github_write"] is False, "closing GitHub scope")

    require(clean["candidate_revision"] == CANDIDATE and clean["candidate_tree"] == CANDIDATE_TREE, "clean replay frozen head")
    require(clean["clone_mode"] == "git clone --no-hardlinks --no-local followed by detached exact checkout", "clean replay clone mode")
    require(clean["python"] == PYTHON, "clean replay bundled Python")
    require(clean["commands"] == list(REPLAY_SCRIPTS), "clean replay commands")
    require(clean["results"] == {
        "canonical_v6": "PASS_10_HOSTILE_MUTATIONS",
        "opening_audit": "PASS_13_HOSTILE_MUTATIONS",
        "constructor": "PASS_BYTE_EXACT_REBUILD_19_HOSTILE_MUTATIONS",
        "falsifier": "PASS_25_HOSTILE_MUTATIONS",
        "producer_independent_certificate": "PASS_22_HOSTILE_MUTATIONS",
        "git_diff_check": "PASS",
        "worktree_clean": True,
    }, "clean replay results")
    require(clean["classification"] == "CLEAN_REPLAY_ACCEPTS_EXACT_FACTORED_BARRIER_NULL_ENVELOPE", "clean replay classification")

    report = frozen(CLOSING_EVIDENCE, f"{CYCLE_REL}/CYCLE_REPORT.md").decode("utf-8")
    for snippet in (
        CANDIDATE,
        CANDIDATE_TREE,
        "Closing ledger: `2/9`",
        "zero sampled components",
        "Ledger delta: **none**",
        RETIRED.replace("_", " ").lower().split(" budget ")[0],
        SUCCESSOR,
        "GitHub remained read-only",
    ):
        if snippet == "blind factored barrier component sampler":
            require("larger blind solver budget" in report, "closing report retirement")
        else:
            require(snippet in report, f"closing report field {snippet}")


def validate_result(candidate: dict) -> None:
    require(candidate["format"] == "d9-factor19069-factored-barrier-referee-result-v1", "result format")
    require(candidate["reviewed_revision"] == CANDIDATE, "result reviewed revision")
    require(candidate["reviewed_tree"] == CANDIDATE_TREE, "result reviewed tree")
    require(candidate["closing_evidence_revision"] == CLOSING_EVIDENCE and candidate["closing_evidence_tree"] == CLOSING_EVIDENCE_TREE, "result closing evidence head")
    require(candidate["verdict"] == "ACCEPT", "result verdict")
    require(candidate["accepted_classification"] == CLASSIFICATION, "result classification")
    require(candidate["accepted_endpoint"] == ENDPOINT, "result accepted endpoint")
    require(candidate["opening_and_protocol_pins"] == OPENING_PROTOCOL_PINS, "result opening pins")
    require(candidate["candidate_artifact_pins"] == CANDIDATE_PINS, "result candidate pins")
    require(candidate["closing_evidence_pins"] == CLOSING_PINS, "result closing pins")
    require(all(candidate["gates"].values()), "result gates")
    require(candidate["closing_hostile_mutations"] == {"rejected": 15, "total": 15}, "result hostile mutations")
    require(candidate["component_samples"] == 0 and candidate["boundary_wall_residences_classified"] == 0, "result component samples")
    require(candidate["attachment_classification_complete"] is False, "result attachment scope")
    require(candidate["ledger_delta"] == "none" and candidate["theorem_ledger"] == "2/9" and candidate["diagonal_nine"] == "OPEN", "result ledger")
    require(candidate["closing_strategy_verdict"] == "PIVOT" and candidate["retired_route"] == RETIRED, "result strategy")
    require(candidate["precise_successor"] == SUCCESSOR, "result successor")
    assessment = candidate["successor_assessment"]
    require(assessment["non_repetition"] is True and assessment["blind_budget_escalation"] is False, "result successor non-repetition")
    require(assessment["attacks_first_unsampled_stratum"] == "FB-C0-STRICT-INTERIOR-FULL-SUPPORT", "result successor first stratum")
    require(assessment["structural_attack"] == "SATURATED_JACOBIAN_HILBERT_EQUIDIMENSIONAL_DECOMPOSITION", "result successor structural attack")
    require(candidate["storage"] == {"drive_connector_used": False, "github_write": False, "durable_project_root": r"E:\Projects\9DVL Research"}, "result storage/GitHub scope")


def reseal_frontier(candidate: dict) -> dict:
    circuit_digest = canonical_digest(candidate["factor_circuit"])
    candidate["factor_circuit_semantic_sha256"] = circuit_digest
    for system in candidate["strict_interior_critical_frontier"]["systems"]:
        system["factor_circuit_semantic_sha256"] = circuit_digest
        system["semantic_sha256"] = canonical_digest({key: value for key, value in system.items() if key != "semantic_sha256"})
    systems = candidate["strict_interior_critical_frontier"]["systems"]
    if systems:
        candidate["strict_interior_critical_frontier"]["first_unsampled_component_or_stratum"]["stratum_semantic_sha256"] = systems[0]["semantic_sha256"]
    records = candidate["true_boundary_frontier"]["records"]
    if records:
        candidate["true_boundary_frontier"]["first_unclassified_boundary_stratum"]["record_semantic_sha256"] = canonical_digest(records[0])
    candidate["semantic_sha256"] = semantic_digest(candidate)
    return candidate


def hostile_mutations(frontier: dict, manifest: dict, clean: dict, result: dict) -> list[str]:
    mutations = []

    def add(marker: str, edit) -> None:
        bundle = [deepcopy(frontier), deepcopy(manifest), deepcopy(clean), deepcopy(result)]
        edit(*bundle)
        bundle[0] = reseal_frontier(bundle[0])
        mutations.append((marker, bundle))

    add("reviewed revision", lambda f, m, c, r: r.__setitem__("reviewed_revision", "0" * 40))
    add("parent factor nodes", lambda f, m, c, r: f["factor_circuit"]["parent_factor_nodes"].pop())
    add("component samples", lambda f, m, c, r: f["strict_interior_critical_frontier"].__setitem__("connected_components_sampled", 1))
    add("positive-dimensional scope", lambda f, m, c, r: f["strict_interior_critical_frontier"]["systems"][0].__setitem__("positive_dimensional_pieces_required", False))
    add("boundary certified path", lambda f, m, c, r: f["true_boundary_frontier"]["records"][-1]["parent_component_closure_path"].__setitem__("status", "TESTED_LINEAR_PATH_REJECTED_NO_ALTERNATIVE_EXACT_PATH_CERTIFIED"))
    add("collar globalization", lambda f, m, c, r: f["fixed_skeleton_accounting"]["exact_attached_wall_anchor"].__setitem__("barrier_critical_sample", True))
    add("attachment completeness", lambda f, m, c, r: f["fixed_skeleton_accounting"].__setitem__("attachment_classification_complete", True))
    add("ledger", lambda f, m, c, r: r.__setitem__("theorem_ledger", "3/9"))
    add("strategy", lambda f, m, c, r: r.__setitem__("closing_strategy_verdict", "CONTINUE"))
    add("successor", lambda f, m, c, r: r.__setitem__("precise_successor", "D9_REPEAT_BLIND_BARRIER_SAMPLER"))
    add("Drive scope", lambda f, m, c, r: m["storage"].__setitem__("drive_connector_used", True))
    add("GitHub scope", lambda f, m, c, r: m["storage"].__setitem__("github_write", True))
    add("clean replay results", lambda f, m, c, r: c["results"].__setitem__("producer_independent_certificate", "FAIL"))
    add("accepted endpoint", lambda f, m, c, r: r.__setitem__("accepted_endpoint", "COMPLETE_FACTORED_BARRIER_COMPONENT_TO_SKELETON_ATTACHMENT_CERTIFICATE"))
    add("artificial-boundary separation", lambda f, m, c, r: f["true_boundary_frontier"]["true_parent_boundary_kept_distinct_from"].pop())

    rejected = []
    for marker, (mutated_frontier, mutated_manifest, mutated_clean, mutated_result) in mutations:
        try:
            validate_frontier(mutated_frontier)
            validate_closing_evidence(mutated_manifest, mutated_clean)
            validate_result(mutated_result)
        except Reject as error:
            require(marker in str(error), f"hostile mutation wrong rejection {marker}: {error}")
            rejected.append(marker)
        else:
            raise Reject(f"hostile mutation accepted: {marker}")
    require(len(rejected) == len(mutations) == 15, "hostile mutation census")
    return rejected


def replay(script: str) -> None:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run(
        [sys.executable, "-u", script],
        cwd=ROOT,
        env=environment,
        text=True,
        capture_output=True,
    )
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    require(completed.returncode == 0 and "PASS" in completed.stdout, f"frozen replay {script}")


def independence_audit() -> None:
    syntax = ast.parse(Path(__file__).read_text(encoding="utf-8"))
    imports = []
    for node in ast.walk(syntax):
        if isinstance(node, ast.Import):
            imports.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.append(node.module or "")
    require(not any("factored_barrier" in name or "falsifier" in name for name in imports), "referee imports producer acceptance logic")


def main() -> None:
    require(Path(sys.executable).resolve() == Path(PYTHON).resolve(), "referee must use bundled Python")
    independence_audit()
    validate_frozen_revisions()
    validate_pins()
    frontier = load_frozen_json(CANDIDATE, FRONTIER_REL)
    manifest = load_frozen_json(CLOSING_EVIDENCE, f"{CYCLE_REL}/CLOSING_MANIFEST.json")
    clean = load_frozen_json(CLOSING_EVIDENCE, f"{CYCLE_REL}/CLEAN_REPLAY.json")
    result = json.loads(RESULT_PATH.read_text(encoding="utf-8"))
    validate_frontier(frontier)
    validate_handoffs(frontier)
    validate_closing_evidence(manifest, clean)
    validate_result(result)
    rejected = hostile_mutations(frontier, manifest, clean, result)
    for script in REPLAY_SCRIPTS:
        replay(script)
    print("PASS frozen-head factored-barrier closing referee")
    print(f"PASS candidate={CANDIDATE[:7]} tree={CANDIDATE_TREE[:7]} closing={CLOSING_EVIDENCE[:7]} tree={CLOSING_EVIDENCE_TREE[:7]}")
    print(f"PASS hostile_mutations={len(rejected)}/15; no producer acceptance imports")
    print(f"ACCEPT exact null only; ledger=2/9 diagonal9=OPEN strategy=PIVOT successor={SUCCESSOR}")


if __name__ == "__main__":
    main()
