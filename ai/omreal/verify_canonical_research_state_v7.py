#!/usr/bin/env python3
"""Verify the canonical post factored-barrier 9DVL research state V7."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
STATE_PATH = HERE / "data" / "CANONICAL_RESEARCH_STATE_V7.json"
REFEREE = "ba98554cf20edb7897beea975c70af5041036160"
REFEREE_TREE = "cf844293a8bd73c4949bdc10d2460511c14ca696"
SUCCESSOR = "D9_ROW2599_FACTOR19069_FACTORED_CRITICAL_EQUIDIMENSIONAL_DECOMPOSITION_GATE1"


class Reject(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def git(*arguments: str, binary: bool = False):
    result = subprocess.check_output(["git", *arguments], cwd=ROOT, text=not binary)
    return result if binary else result.strip()


def frozen(path: str) -> bytes:
    return git("show", f"{REFEREE}:{path}", binary=True)


def validate(candidate: dict) -> None:
    require(candidate["format"] == "9dvl-canonical-research-state-v7", "format")
    require(candidate["status"] == "PIVOT_REQUIRED", "status")
    repository = candidate["repository"]
    require(repository["branch"] == "research/local-d9-factor19069-factored-barrier-gate1-20260901", "branch")
    require(repository["integrated_referee_commit"] == REFEREE, "referee revision")
    require(repository["integrated_referee_tree"] == REFEREE_TREE, "referee tree")
    require(repository["saved_project_root"] == r"E:\Projects\9DVL Research", "project root")
    require(repository["mounted_recovery_status"] == "UNAVAILABLE_ACCESS_DENIED_NONBLOCKING", "recovery status")
    require(repository["drive_connector_used"] is False, "Drive connector")
    require(repository["github_mode"].startswith("READ_ONLY"), "GitHub mode")
    theorem = candidate["theorem"]
    require(theorem["score"] == "2/9" and theorem["proved_diagonals"] == [1, 2], "ledger")
    require(theorem["diagonal_nine"] == "OPEN", "diagonal nine")
    require(theorem["promotion"] == "NONE" and theorem["theorem_level_counterexample"] == "NOT_FOUND", "theorem disposition")
    cycle = candidate["completed_cycle"]
    require(cycle["selected_count"] == 1, "selected count")
    barrier = cycle["factored_barrier"]
    require(barrier["parent_factor_nodes"] == 70 and barrier["barrier_total_degree"] == 90, "barrier census")
    require(barrier["expanded_product_used"] is False, "expanded barrier")
    require(barrier["factored_derivative_summands"] == 630 and barrier["wedge_equations"] == 36, "critical circuit")
    critical = cycle["critical_frontier"]
    require(critical["first_unsampled_stratum"] == "FB-C0-STRICT-INTERIOR-FULL-SUPPORT", "first stratum")
    require(critical["possible_dimensions"] == list(range(9)) and critical["singular_pieces_retained"] is True, "critical scope")
    require(critical["connected_components_sampled"] == critical["zero_dimensional_components_sampled"] == critical["positive_dimensional_components_sampled"] == 0, "component samples")
    boundary = cycle["boundary_frontier"]
    require(boundary["proper_nonexcluded_candidates"] == 10 and boundary["certified_parent_closure_paths"] == 1, "boundary frontier")
    require(boundary["certified_path_support"] == [15, 7, 15], "certified support")
    require(boundary["classified_boundary_wall_residences"] == 0 and boundary["first_unclassified_support"] == [1, 1, 1], "boundary scope")
    skeleton = cycle["skeleton"]
    require(skeleton["rooted_edges"] == [39] and skeleton["edge39_open_roots"] == 1, "skeleton roots")
    require(skeleton["barrier_critical_samples"] == 0 and skeleton["attachment_classification_complete"] is False, "attachment scope")
    certificate = cycle["certificate_gate"]
    require(certificate["verdict"] == "ACCEPT" and certificate["hostile_mutations_rejected"] == 22, "certificate")
    require(certificate["producer_imported"] is False and certificate["falsifier_imported"] is False, "certificate independence")
    referee = cycle["referee_gate"]
    require(referee["verdict"] == "ACCEPT" and referee["closing_hostile_mutations_rejected"] == 15, "referee")
    require(referee["clean_replay"] is True and referee["closing_strategy_verdict"] == "PIVOT", "closing gates")
    require(cycle["route_disposition"] == "BLIND_FACTORED_BARRIER_COMPONENT_SAMPLER_BUDGET_ESCALATION_RETIRED", "retired route")
    successor = candidate["selected_successor"]
    require(successor["id"] == SUCCESSOR, "successor")
    require(successor["strategy"] == "PROJECTION_FREE_SATURATED_JACOBIAN_HILBERT_EQUIDIMENSIONAL_DECOMPOSITION", "successor strategy")
    require(len(successor["prohibited"]) == 6, "prohibited routes")
    require(candidate["process_gates"]["ledger_promotion_requires_independently_replayed_universal_diagonal_certificate"] is True, "promotion gate")


def hostile_mutations(stored: dict) -> None:
    mutations = []
    candidate = deepcopy(stored); candidate["status"] = "COMPLETE"; mutations.append((candidate, "status"))
    candidate = deepcopy(stored); candidate["repository"]["integrated_referee_commit"] = "0" * 40; mutations.append((candidate, "referee revision"))
    candidate = deepcopy(stored); candidate["repository"]["drive_connector_used"] = True; mutations.append((candidate, "Drive connector"))
    candidate = deepcopy(stored); candidate["theorem"]["score"] = "3/9"; mutations.append((candidate, "ledger"))
    candidate = deepcopy(stored); candidate["theorem"]["diagonal_nine"] = "PROVED"; mutations.append((candidate, "diagonal nine"))
    candidate = deepcopy(stored); candidate["completed_cycle"]["selected_count"] = 2; mutations.append((candidate, "selected count"))
    candidate = deepcopy(stored); candidate["completed_cycle"]["factored_barrier"]["expanded_product_used"] = True; mutations.append((candidate, "expanded barrier"))
    candidate = deepcopy(stored); candidate["completed_cycle"]["critical_frontier"]["connected_components_sampled"] = 1; mutations.append((candidate, "component samples"))
    candidate = deepcopy(stored); candidate["completed_cycle"]["boundary_frontier"]["classified_boundary_wall_residences"] = 1; mutations.append((candidate, "boundary scope"))
    candidate = deepcopy(stored); candidate["completed_cycle"]["skeleton"]["attachment_classification_complete"] = True; mutations.append((candidate, "attachment scope"))
    candidate = deepcopy(stored); candidate["completed_cycle"]["route_disposition"] = "CONTINUE_BLIND_SAMPLER"; mutations.append((candidate, "retired route"))
    candidate = deepcopy(stored); candidate["selected_successor"]["id"] = "SAMPLE_ANOTHER_SEPARATOR"; mutations.append((candidate, "successor"))
    for candidate, marker in mutations:
        try:
            validate(candidate)
        except Reject as error:
            require(marker in str(error), f"wrong hostile rejection {marker}: {error}")
            continue
        raise Reject(f"hostile mutation accepted: {marker}")


def main() -> None:
    require(git("rev-parse", f"{REFEREE}^{{tree}}") == REFEREE_TREE, "referee tree")
    state = json.loads(STATE_PATH.read_text(encoding="utf-8"))
    validate(state)
    require(sha256(frozen(state["predecessor"]["path"])).hexdigest() == state["predecessor"]["sha256"], "predecessor pin")
    predecessor = json.loads(frozen(state["predecessor"]["path"]).decode("utf-8"))
    require(predecessor["status"] == "PIVOT_REQUIRED" and predecessor["theorem"]["score"] == "2/9", "predecessor state")
    for path, expected in state["pins"].items():
        require(sha256(frozen(path)).hexdigest() == expected, f"referee pin {path}")
    referee = json.loads(frozen("ops/team/d9-factor19069-factored-barrier-referee/RESULT.json").decode("utf-8"))
    require(referee["verdict"] == "ACCEPT" and referee["theorem_ledger"] == "2/9", "referee disposition")
    require(referee["precise_successor"] == SUCCESSOR, "referee successor")
    hostile_mutations(state)
    print("PASS canonical 9DVL research state V7")
    print("referee=ba98554 ledger=2/9 diagonal9=OPEN verdict=PIVOT")
    print("hostile_mutations=12 successor=FACTORED_CRITICAL_EQUIDIMENSIONAL_DECOMPOSITION")


if __name__ == "__main__":
    main()
