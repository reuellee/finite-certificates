#!/usr/bin/env python3
"""Exact replay for the universal D9 cut boundary/transport opening gate."""

from __future__ import annotations

import argparse
from copy import deepcopy
from fractions import Fraction
import hashlib
import json
import os
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
MANIFEST = HERE / "SOURCE_MANIFEST.json"
COUNTEREXAMPLE = HERE / "BOUNDARY_TRANSPORT_COUNTEREXAMPLE.json"
RESULT = HERE / "RESULT.json"
FINDINGS = HERE / "FINDINGS.md"
WORKING_BASE = "6cbd1b4a7d3ed61bee268b6b54cbfadeece90f0e"
WORKING_TREE = "84eaf80b30e1f366b8f959bd6435a217762636b3"
CYCLE_BASE = "cbe84ccd7273252c81fd4da17ee360a284d2a2a6"
CYCLE_TREE = "da3cd6feca1052ea14ed5036413c72b8f7fadc2a"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_digest(prefix: bytes, payload: dict) -> str:
    body = dict(payload)
    body.pop("semantic_sha256", None)
    encoded = json.dumps(body, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(prefix + encoded).hexdigest()


def parse_fraction(value: str) -> Fraction:
    return Fraction(value)


def validate_manifest() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(manifest["format"] == "d9-universal-cut-boundary-source-manifest-v1", "manifest format")
    require(manifest["track_id"] == "d9-universal-cut-boundary", "manifest track")
    require(manifest["working_base"] == {"commit": WORKING_BASE, "tree": WORKING_TREE}, "working base")
    require(manifest["cycle_math_base"] == {"commit": CYCLE_BASE, "tree": CYCLE_TREE}, "cycle base")
    for relative, expected in manifest["sources"].items():
        require(sha256(ROOT / relative) == expected, f"source drift: {relative}")
    transitive = manifest["transitive_source_accounting"]
    require(transitive["normal_link_falsifier_manifest_semantic_sha256"] ==
            "882ce789f936f4efd6e4572b7680669aeb6e51aa41f81f206d0b75bd418aa439",
            "transitive manifest semantic digest")
    require(transitive["normal_link_falsifier_manifest_validates_deep_sources"] is True,
            "deep source accounting")
    require(transitive["unavailable_historical_referee_commit_required"] is False,
            "historical referee dependency")
    require(manifest["semantic_sha256"] == canonical_digest(
        b"d9-universal-cut-boundary-source-manifest-v1\0", manifest
    ), "manifest semantic digest")
    return manifest


def validate_compactification() -> None:
    atlas = json.loads((ROOT / "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json").read_text())
    require(atlas["format"] == "diag3-pair-global-row2599-compactification-atlas-v1", "atlas format")
    require(atlas["parent_index"] == 2599, "atlas parent")
    require(atlas["model"] == "product_of_three_closed_positive_projective_3_simplices", "atlas model")
    require(atlas["chart_atlas"] == {
        "gauge_rows": [1, 2, 3, 4],
        "chart_count": 64,
        "ordered_transition_count": 4096,
        "ordered_triple_cocycle_count": 262144,
        "coordinates_per_chart": 9,
    }, "complete chart census")
    target = [row for row in atlas["boundary_divisors"] if row["parent_bracket"] == "1237"]
    require(target == [{
        "moving_column": 7,
        "coordinate_row": 4,
        "parent_bracket": "1237",
        "determinant_sign": 1,
    }], "1237 genuine divisor")
    require("genuine infinity labels" in atlas["scope"], "genuine infinity scope")

    attachment = json.loads((ROOT / "ai/omreal/data/DIAG3_PAIR_PARENT_BOUNDARY_ATTACHMENT_89_1237.json").read_text())
    parent = attachment["parent_residence"]
    require(attachment["status"] == "EXACT_GENUINE_PARENT_BOUNDARY_ATTACHMENT", "attachment status")
    require(parent["target_boundary_bracket"] == "1237", "attachment divisor")
    require(parent["target_boundary_is_genuine_parent_divisor"] is True, "genuine divisor tag")
    require(parent["strict_on_open_ray"] is True, "open-ray strictness")
    require(parent["endpoint_parent_sign_census"] == {"positive": 69, "zero": 1}, "endpoint census")


def validate_counterexample(candidate: dict, *, check_digest: bool = True) -> None:
    predecessor = json.loads((ROOT / "ops/team/diag9-s1237-normal-link-falsifier/RESULT.json").read_text())
    no_go = json.loads((ROOT / "ops/team/diag9-s1237-normal-link-prover/DIAG9_S1237_NORMAL_LINK_NO_GO.json").read_text())

    require(candidate["format"] == "d9-universal-cut-boundary-transport-counterexample-v1", "counterexample format")
    require(candidate["track_id"] == "d9-universal-cut-boundary", "counterexample track")
    require(candidate["classification"] == "finite-exact omitted strict-coface attachment", "classification")
    require(candidate["parent"] == {
        "catalog_index": 2599,
        "compactification": "product_of_three_closed_positive_projective_3_simplices",
        "chart_count": 64,
        "strict_parent_condition": "all 70 oriented parent brackets are positive",
    }, "parent metadata")
    require(candidate["family"] == {
        "name": "S12,37",
        "proper_pairwise_incomparable": True,
        "candidate_active_factor_count": 3539,
    }, "family metadata")

    factor = candidate["active_factor"]
    expected_factor = predecessor["factor"]
    for key in (
        "factor_id", "polynomial", "family_allowed_orientation", "family_allowed_side",
        "occurrence_index", "occurrence_fourset", "occurrence_multiplicity",
        "stripped_parent_unit_indices",
    ):
        require(factor[key] == expected_factor[key], f"active factor field: {key}")
    require(factor["family_allowed_orientation"] == -1, "active orientation")
    require(factor["occurrence_multiplicity"] == 1, "occurrence multiplicity")

    incidence = candidate["boundary_incidence"]
    require(incidence["support"] == [3, 1, 15], "support")
    require(incidence["recursive_parent_bracket"] == "1237", "recursive facet")
    require(incidence["standard_coordinate"] == "f", "standard coordinate")
    require(incidence["compactification_divisor"] == {
        "moving_column": 7,
        "coordinate_row": 4,
        "parent_bracket": "1237",
        "determinant_sign": 1,
    }, "compactification divisor transport")
    require(incidence["genuine_parent_boundary"] is True, "genuine boundary")
    require(incidence["artificial_work_boundary"] is False, "artificial boundary confusion")
    require(incidence["residual_parent_multiwall"] is True, "residual/parent multiwall")
    require(incidence["lowest_residual_normal_form"] == "d/4-e", "normal form")

    source_rays = {row["side"]: row for row in predecessor["obstruction"]["rays"]}
    require([row["side"] for row in candidate["exact_rays"]] == ["minus", "wall", "plus"], "ray order")
    computed_signs = []
    for row in candidate["exact_rays"]:
        source = source_rays[row["side"]]
        for key in (
            "normal_direction", "lowest_residual_form", "exact_lift_point",
            "exact_factor_value", "lift_parent_zero_profile", "strictly_positive_parent_brackets",
        ):
            require(row[key] == source[key], f"ray {row['side']} field: {key}")
        direction = tuple(map(parse_fraction, row["normal_direction"]))
        point = tuple(map(parse_fraction, row["exact_lift_point"]))
        require(len(direction) == 6 and len(point) == 9, f"ray shape: {row['side']}")
        require(sum(direction[:5]) == 1, f"projective normal normalization: {row['side']}")
        require(direction[4] == 0 and point[5] == 0, f"ray left recursive facet: {row['side']}")
        q1 = direction[2] / 4 - direction[3]
        q = point[3] * point[8] - point[4]
        require(q1 == parse_fraction(row["lowest_residual_form"]), f"q1 replay: {row['side']}")
        require(q == parse_fraction(row["exact_factor_value"]), f"q replay: {row['side']}")
        require(row["lift_parent_zero_profile"] == ["1237"], f"parent zero profile: {row['side']}")
        require(row["strictly_positive_parent_brackets"] == 69, f"positive parent count: {row['side']}")
        computed_signs.append((q > 0) - (q < 0))
        if row["side"] == "wall":
            require(point[4] == point[3] * point[8], "exact wall stabilization e=d*i")
    require(computed_signs == [-1, 0, 1], "two-sided exact factor signs")

    obstruction = candidate["singular_transport_obstruction"]
    singular = no_go["obstruction"]["singular_supports"][0]
    require(singular["support"] == [3, 1, 15], "no-go support")
    require(singular["positive_parent_label"] == "1237" and singular["negative_parent_label"] == "1367",
            "opposite parent labels")
    require(singular["positive_gordan_weights"] == [1, 1] and singular["weighted_sum"] == [],
            "parent Gordan certificate")
    require(obstruction == {
        "ordinary_common_radial_strict_parent_link": "EMPTY",
        "positive_parent_initial_form": "+n4",
        "negative_parent_initial_form": "-n4",
        "positive_gordan_weights": [1, 1],
        "forced_recursive_facet": "n4=0",
        "higher_weighted_orders_required": True,
        "strict_open_parent_lift_certified": False,
    }, "singular transport obstruction")

    gate = candidate["strict_parent_separator_gate"]
    require(gate["witness_contained_in_boundary"] is True, "boundary membership")
    require(gate["witness_separates_strict_parent"] is False, "strict separator overclaim")
    require(gate["recursive_facet_wall_promoted_to_global_separator"] is False, "global separator overclaim")
    require("bracket 1237>0" in gate["missing_load_bearing_attachment"], "missing strict coface")
    require("W alone cannot separate" in gate["lemma"], "separator lemma")

    scope = candidate["scope"]
    require(scope["refutes"] == "RECURSIVE_FACET_WALL_IMPLIES_STRICT_OPEN_PARENT_SEPARATOR", "refuted rule")
    require(scope["opening_gate_effect"] == "first fatal omitted transport mode", "opening gate effect")
    require(scope["does_not_refute"] == "existence of a richer finite schema carrying exact strict-coface attachments",
            "richer-schema nonconsequence")
    required_nonclaims = {
        "strict open-parent crossing", "collar or mincut", "global D9 separator",
        "coverage of every parent or family", "theorem-ledger change",
    }
    require(set(scope["does_not_claim"]) == required_nonclaims, "nonconsequences")
    if check_digest:
        require(candidate["semantic_sha256"] == canonical_digest(
            b"d9-universal-cut-boundary-transport-counterexample-v1\0", candidate
        ), "counterexample semantic digest")


def validate_result() -> dict:
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    require(result["format"] == "d9-universal-cut-boundary-result-v1", "result format")
    require(result["track_id"] == "d9-universal-cut-boundary", "result track")
    require(result["base_revision"] == WORKING_BASE and result["base_tree"] == WORKING_TREE, "result base")
    require(result["outcome"] == "inconclusive", "result classification")
    require(result["endpoint"] == "UNIVERSAL_CUT_SCHEMA_COVERAGE_GAP", "result endpoint")
    require(result["opening_gate_passed"] is False and result["main_census_authorized"] is False,
            "opening gate fail closed")
    require(result["ledger_change_recommended"] == "none", "ledger overclaim")
    require(result["coverage"]["excluded"] == [
        "strict open-parent coface transport at factor 8552",
        "weighted stabilization beyond the recursive facet",
        "all other parents, families, factors, charts, and multiwalls",
        "global separator or connectivity",
    ], "coverage exclusions")
    artifacts = {row["path"]: row["sha256"] for row in result["artifacts"]}
    expected_paths = (
        "ops/team/d9-universal-cut-boundary/BOUNDARY_TRANSPORT_COUNTEREXAMPLE.json",
        "ops/team/d9-universal-cut-boundary/FINDINGS.md",
        "ops/team/d9-universal-cut-boundary/SOURCE_MANIFEST.json",
        "ops/team/d9-universal-cut-boundary/verify_boundary_transport_gate.py",
    )
    require(set(artifacts) == set(expected_paths), "result artifact inventory")
    for relative in expected_paths:
        require(artifacts[relative] == sha256(ROOT / relative), f"artifact digest: {relative}")
    require(result["semantic_sha256"] == canonical_digest(
        b"d9-universal-cut-boundary-result-v1\0", result
    ), "result semantic digest")
    findings = FINDINGS.read_text(encoding="utf-8")
    for phrase in (
        "Strict-parent separator gate", "relative end only", "ledger remains `2/9`",
        "RECURSIVE_FACET_WALL_IMPLIES_STRICT_OPEN_PARENT_SEPARATOR",
    ):
        require(phrase in findings, f"findings scope phrase: {phrase}")
    return result


def hostile_canaries(stored: dict) -> int:
    paths_and_values = (
        (("active_factor", "family_allowed_orientation"), 1),
        (("active_factor", "occurrence_multiplicity"), 65),
        (("boundary_incidence", "recursive_parent_bracket"), "1367"),
        (("boundary_incidence", "genuine_parent_boundary"), False),
        (("boundary_incidence", "compactification_divisor", "coordinate_row"), 3),
        (("exact_rays", 0, "exact_factor_value"), "0"),
        (("exact_rays", 1, "exact_lift_point", 5), "1/100"),
        (("exact_rays", 2, "lift_parent_zero_profile"), []),
        (("singular_transport_obstruction", "ordinary_common_radial_strict_parent_link"), "NONEMPTY"),
        (("singular_transport_obstruction", "strict_open_parent_lift_certified"), True),
        (("strict_parent_separator_gate", "witness_separates_strict_parent"), True),
        (("strict_parent_separator_gate", "recursive_facet_wall_promoted_to_global_separator"), True),
        (("scope", "opening_gate_effect"), "OPENING_GATE_PASSED"),
    )
    rejected = 0
    for path, value in paths_and_values:
        candidate = deepcopy(stored)
        target = candidate
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            validate_counterexample(candidate, check_digest=False)
        except AssertionError:
            rejected += 1
    require(rejected == len(paths_and_values), "hostile mutation survived")
    return rejected


def run_upstream_replays() -> None:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    commands = (
        ["python", "ops/research-team/cycles/2026-09-01-d9-universal-cut/verify_opening_audit.py"],
        ["python", "ops/team/diag9-s1237-normal-link-prover/verify_normal_link_no_go.py"],
        ["python", "ops/team/diag9-s1237-normal-link-falsifier/verify_normal_link_falsifier.py"],
    )
    for command in commands:
        completed = subprocess.run(command, cwd=ROOT, env=env, text=True, capture_output=True)
        require(completed.returncode == 0, f"upstream replay failed: {' '.join(command)}\n{completed.stdout}\n{completed.stderr}")
        print("PASS upstream", command[-1])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-upstream", action="store_true", help="skip the three source replays; source hashes are still checked")
    args = parser.parse_args()

    validate_manifest()
    require(subprocess.check_output(["git", "rev-parse", f"{WORKING_BASE}^{{tree}}"], cwd=ROOT, text=True).strip()
            == WORKING_TREE, "working commit/tree drift")
    require(subprocess.check_output(["git", "rev-parse", f"{CYCLE_BASE}^{{tree}}"], cwd=ROOT, text=True).strip()
            == CYCLE_TREE, "cycle commit/tree drift")
    validate_compactification()
    stored = json.loads(COUNTEREXAMPLE.read_text(encoding="utf-8"))
    validate_counterexample(stored)
    result = validate_result()
    rejected = hostile_canaries(stored)
    if not args.skip_upstream:
        run_upstream_replays()

    print("PASS exact active orientation and multiplicity: factor 8552, q=d*i-e<0, multiplicity 1")
    print("PASS 64-chart genuine boundary transport: f=0 iff [1237]=0")
    print("PASS exact residual/parent multiwall: q signs -/0/+ with all three lifts confined to [1237]=0")
    print("PASS singular transport no-go: +n4 and -n4 force the ordinary strict link to n4=0")
    print(f"PASS {rejected}/{rejected} hostile mutations rejected")
    print("ENDPOINT", result["endpoint"], "(opening gate failed closed)")
    print("SCOPE recursive-facet wall is a relative end, not a strict-open-parent/global separator; ledger 2/9")
    print("SEMANTIC SHA256", result["semantic_sha256"])


if __name__ == "__main__":
    main()
