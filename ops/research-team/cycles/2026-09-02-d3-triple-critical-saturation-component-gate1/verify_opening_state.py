#!/usr/bin/env python3
"""Verify the governed opening of the D3 critical-saturation cycle."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess


ROOT = Path(__file__).resolve().parents[4]
CYCLE_DIR = Path(__file__).resolve().parent
OPENING_PATH = CYCLE_DIR / "OPENING_STATE.json"
BASE = "ba87af7b1ac58d22c0622c908e31dc8ec03d24fa"
BASE_TREE = "54bcab4da2eaa441a4d4c3823a8d4593d89e6bda"
BRANCH = "research/local-d3-triple-critical-saturation-gate1-20260902"
TARGET = "D3_TRIPLE_ORBIT5563_COMPONENT_DECORATED_CRITICAL_SATURATION_GATE1"
VECTOR = [
    "2/9", 1, ["diag3_pair_hc1", "diag3_triple_hc0"], 7,
    "UNKNOWN", "UNKNOWN", 7, 10,
]
ALLOWED_ATTACHMENTS = [
    "PARENT_WALL",
    "CHART_OR_NORMALIZATION_DIVISOR",
    "OCCURRENCE_OR_CONCURRENCE_RANK_STRATUM",
    "EXTRA_RESIDUAL_FACTOR_FRONTIER",
    "PROJECTIVE_INFINITY",
]
REQUIRED_Q0 = [
    "EXACT_SOURCE_IDEAL_AND_DIGESTS",
    "FINITE_ORDERED_SATURATOR_LEDGER",
    "CONTAINMENT_IDENTITY_AND_ATTACHMENT_CLASS_PER_REMOVED_COMPONENT",
    "SINGULAR_LOCUS_RETENTION_OR_PROVED_ATTACHMENT",
    "KNOWN_FOURSPACE_PARENT_WALL_CANARY",
    "ARTIFICIAL_BOUNDARY_REJECTION_CANARY",
    "EXACT_JOB_SIZE_COUNTS",
    "NUMERIC_LOCAL_RESOURCE_FORECAST",
]
PROHIBITED = [
    "AUTHOR_CONTACT",
    "NETWORK_RESEARCH",
    "GITHUB_WRITE",
    "CLOUD_OR_PAID_COMPUTE",
    "REPEAT_SREP_BACKEND_SEARCH",
    "PAIR_CAD_OR_MASTER_ATLAS_REVIVAL",
    "TRIPLE_BOX_COLLAR_MACROBOX_SOURCE_OR_SAMPLING_GROWTH",
    "RAW_GROEBNER_OR_RUR_BEFORE_Q0",
    "ARTIFICIAL_BOUNDARY_AS_TRUE_INFINITY",
    "THEOREM_PROMOTION_FROM_MODULAR_OR_LOCAL_EVIDENCE",
]


class AuditError(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def reject_duplicate_keys(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        require(key not in result, f"duplicate JSON key: {key}")
        result[key] = value
    return result


def parse_json(payload: str | bytes) -> dict:
    return json.loads(payload, object_pairs_hook=reject_duplicate_keys)


def git_text(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, text=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout.strip()


def frozen(path: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{BASE}:{path}"], cwd=ROOT, check=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    ).stdout


def validate(opening: dict) -> None:
    require(opening["format"] == "d3-triple-critical-saturation-opening-v1", "format")
    require(opening["cycle_id"] == "2026-09-02-d3-triple-critical-saturation-component-gate1", "cycle id")

    base = opening["base"]
    require(base["commit"] == BASE and base["tree"] == BASE_TREE, "base identity")
    require(base["canonical_state"] == "ai/omreal/data/CANONICAL_RESEARCH_STATE_V10.json", "canonical state")
    require(base["canonical_status"] == "STOPPED" and base["ledger"] == "2/9", "canonical status")

    authority = opening["user_authority"]
    require(authority == {
        "new_governed_cycle": True,
        "contact_authors": False,
        "github_write": False,
        "network_research": False,
        "cloud_use": False,
    }, "user authority")

    measure = opening["opening_measure"]
    require(measure["proved_diagonals"] == [1, 2], "proved diagonals")
    require(measure["load_bearing_obligations"] == 7, "obligation count")
    require(measure["pair_residual"] == measure["pair_coverage"] == "UNKNOWN", "pair scope")
    require(measure["triple_source_total"] == 79_102_449, "triple total")
    require(measure["triple_source_settled"] == 77_940_147, "triple settled")
    require(measure["triple_source_residual"] == 1_162_302, "triple residual")
    require(measure["triple_source_total"] - measure["triple_source_settled"] == measure["triple_source_residual"], "triple arithmetic")
    require(measure["triple_source_is_component_denominator"] is False, "component denominator scope")
    require(measure["proof_distance_vector"] == VECTOR, "opening vector")

    tournament = opening["strategy_tournament"]
    require(len(tournament) == 5, "tournament size")
    require(sum(row["disposition"] == "SELECT" for row in tournament) == 1, "one selected route")
    require(tournament[0]["id"] == "TRIPLE_COMPONENT_DECORATED_CRITICAL_SATURATION", "selected route")
    require(tournament[0]["scores"] == [5, 4, 4, 5, 3, 5, 5, 3], "selected scores")

    target = opening["selected_target"]
    require(target["id"] == TARGET, "target id")
    require(target["named_presentation"] == [5563, 16134, 19284], "named presentation")
    require(target["canonical_row"] == [5563, 4373, 23221], "canonical row")
    require(target["height_coordinate"] == "b", "height")
    require(target["source_equations"] == 59, "equation count")
    require(target["residual_equations"] == 3, "residual equation count")
    require(target["formal_critical_minors"] == 56, "formal minors")
    require(target["nonzero_critical_minors"] == 52, "nonzero minors")
    require(target["known_parent_boundary_components"] == 2, "known components")
    require(type(target["selected_successor_count"]) is int and target["selected_successor_count"] == 1, "successor count")

    q0 = opening["q0"]
    require(q0["status"] == "OPEN" and q0["q1_activated"] is False, "Q0 state")
    require(q0["required_outputs"] == REQUIRED_Q0, "Q0 outputs")
    require(q0["allowed_attachment_classes"] == ALLOWED_ATTACHMENTS, "attachment classes")
    q1 = opening["q1"]
    require(q1["status"] == "DENIED_PENDING_Q0", "Q1 state")
    require(q1["positive_endpoint"] == "COMPLETE_ORBIT5563_ROW_REMOVAL", "Q1 positive")

    decrease = opening["strict_decrease"]
    require(decrease["measure"] == "triple_source_residual", "decrease measure")
    require(decrease["opening"] == 1_162_302 and decrease["positive_ceiling"] == 1_162_301, "decrease values")
    require(decrease["ledger_promotion_from_one_row"] is False, "ledger scope")
    require(decrease["pair_branch_closed"] is False, "pair scope")

    resources = opening["resources"]
    require(resources == {
        "wall_clock_hours": 4,
        "peak_ram_gib": 32,
        "new_scratch_gib": 10,
        "constructor_handoffs": 1,
        "verifier_directed_repairs": 1,
        "cloud_workers": 0,
        "external_spend_usd": 0,
    }, "resources")
    require(opening["prohibited"] == PROHIBITED, "prohibited routes")


def validate_frozen_sources(opening: dict) -> None:
    require(git_text("rev-parse", f"{BASE}^{{tree}}") == BASE_TREE, "base tree")
    require(git_text("merge-base", "--is-ancestor", BASE, "HEAD") == "", "base ancestry")
    require(git_text("branch", "--show-current") == BRANCH, "opening branch")
    for path, expected in opening["source_pins"].items():
        require(sha256(frozen(path)).hexdigest() == expected, f"source pin {path}")

    v10 = parse_json(frozen("ai/omreal/data/CANONICAL_RESEARCH_STATE_V10.json"))
    require(v10["status"] == "STOPPED", "V10 status")
    require(v10["theorem"]["score"] == "2/9", "V10 ledger")
    require(v10["proof_distance"]["closing_vector"] == VECTOR, "V10 vector")
    require(v10["predecessor"]["user_reopening_authority_received_after_close"] is True, "V10 user authority")
    require(v10["process_gates"]["author_contact_prohibited_by_latest_user_instruction"] is True, "V10 author-contact gate")

    critical = parse_json(frozen("ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json"))
    require(critical["schema"] == "diag3-triple-fullspace-critical-system-v1", "critical schema")
    require(critical["variables"] == list("abcdefghi"), "critical variables")
    require(critical["height_variable"] == "b" and critical["height_index"] == 1, "critical height")
    require(critical["named_presentation"] == [5563, 16134, 19284], "critical presentation")
    require(critical["canonical_row"] == [5563, 4373, 23221], "critical row")
    require(len(critical["equations"]) == 59, "critical equations")
    require(sum(row["kind"] == "factor" for row in critical["equations"]) == 3, "critical factors")
    minors = [row for row in critical["equations"] if row["kind"] == "height_minor"]
    require(len(minors) == 56, "critical minor count")
    require(sum(bool(row["terms"]) for row in minors) == 52, "critical nonzero minors")

    naturality = parse_json(frozen("ops/team/d3-mixed-carrier-naturality/RESULT.json"))
    require(naturality["program_status"]["C"]["first_missing_edge"] == "C-COMP-01", "C first missing edge")
    require(naturality["program_status"]["C"]["status"] == "DECISIVE_NULL", "C predecessor status")


def validate_text_contracts() -> None:
    cycle = (CYCLE_DIR / "CYCLE.md").read_text(encoding="utf-8")
    orders = (CYCLE_DIR / "WORK_ORDERS.yaml").read_text(encoding="utf-8")
    combined = cycle + "\n" + orders
    for needle in (
        BASE,
        BASE_TREE,
        TARGET,
        "1,162,302 -> at most 1,162,301",
        "no contact with Basu, Karisani, or other authors",
        "no raw Groebner or RUR solve before independent Q0 acceptance",
        "no artificial boundary may be relabeled as true parent infinity",
    ):
        require(needle in combined, f"text contract: {needle}")


def hostile_mutations(stored: dict) -> int:
    changes = [
        (("base", "commit"), "0" * 40),
        (("base", "ledger"), "3/9"),
        (("user_authority", "contact_authors"), True),
        (("user_authority", "github_write"), True),
        (("user_authority", "network_research"), True),
        (("user_authority", "cloud_use"), True),
        (("opening_measure", "load_bearing_obligations"), 6),
        (("opening_measure", "pair_residual"), 0),
        (("opening_measure", "triple_source_residual"), 0),
        (("opening_measure", "triple_source_is_component_denominator"), True),
        (("selected_target", "id"), "REPEAT_GLOBAL_SREP_Q0"),
        (("selected_target", "source_equations"), 55),
        (("selected_target", "known_parent_boundary_components"), 0),
        (("q0", "status"), "PASS"),
        (("q0", "q1_activated"), True),
        (("q0", "allowed_attachment_classes"), ALLOWED_ATTACHMENTS + ["BOX_FACE"]),
        (("q1", "status"), "ACTIVE"),
        (("strict_decrease", "positive_ceiling"), 1_162_302),
        (("strict_decrease", "ledger_promotion_from_one_row"), True),
        (("resources", "cloud_workers"), 1),
        (("resources", "external_spend_usd"), 5),
        (("prohibited",), []),
    ]
    rejected = 0
    for path, value in changes:
        candidate = deepcopy(stored)
        cursor = candidate
        for key in path[:-1]:
            cursor = cursor[key]
        cursor[path[-1]] = value
        try:
            validate(candidate)
        except AuditError:
            rejected += 1
    try:
        parse_json('{"q0":"OPEN","q0":"PASS"}')
    except AuditError:
        rejected += 1
    require(rejected == len(changes) + 1, "hostile mutation accepted")
    return rejected


def main() -> None:
    opening = parse_json(OPENING_PATH.read_text(encoding="utf-8"))
    validate(opening)
    validate_frozen_sources(opening)
    validate_text_contracts()
    subprocess.run(
        ["python", "-B", "ai/omreal/verify_canonical_research_state_v10.py"],
        cwd=ROOT, check=True,
    )
    rejected = hostile_mutations(opening)
    print(
        "PASS D3 triple critical-saturation opening; Q0 OPEN; Q1 DENIED; "
        f"residual 1162302; {rejected}/{rejected} hostiles rejected"
    )


if __name__ == "__main__":
    main()
