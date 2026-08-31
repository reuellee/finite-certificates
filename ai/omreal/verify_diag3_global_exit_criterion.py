#!/usr/bin/env python3
"""Exact finite replay for the diagonal-three global-exit criterion.

The checker deliberately separates two questions:

* H_c^0 / compact-component exclusion is certified when a component-faithful
  graph has every vertex reaching genuine parent infinity.  Failure is
  inconclusive because sound continuation or infinity edges may be omitted.
* A component graph cannot certify pair H1, because two relative CW complexes
  with the same graph and one-skeleton can differ only in two-cell incidence.

No discovery-side module is imported except the pinned historical 37/44
verifier, whose exact rational canary is replayed as source evidence.
"""

from __future__ import annotations

import hashlib
import importlib.util
import json
from collections import deque
from fractions import Fraction
from pathlib import Path

import diag3_research_ledger_compatibility as ledger_compat


REPO = Path(__file__).resolve().parents[2]
FIXTURES = REPO / "ops/team/global-exit/GLOBAL_EXIT_FIXTURES.json"
HISTORICAL_LEDGER_SHA256 = (
    "5841dfbb55aa0d8c580b394b50beff54d607ce86b77683985c2d977c03050e14"
)

PINNED_SHA256 = {
    "ai/omreal/data/DIAG3_COMPLETION_OPEN_OBJECT.json":
        "ea8808e8979603757dec928b1e9aeb266aa3eabcfb2e70c1f13e7aa5c4af6ece",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json":
        "707a96f19f471af041d02bf22fc4267ddd4bf6b78cffde4783f660b645aed833",
    "ai/omreal/data/DIAG3_COMPONENT_COSHEAF_PILOT.json":
        "2fa847a3f7edf206db225d3a184f90c00c54b319ad2cdeaca39cb9ed9d5b0854",
    "ai/omreal/DIAG2_PIVOT_ALL_COMPACT_SECOND_WALL_VERIFY.py":
        "7b79dc1a679143ffee31cd5ad892c6f9b33b561aab7fd1305723db92b24415c1",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def load_json(relative: str):
    return json.loads((REPO / relative).read_text(encoding="utf-8"))


def rank_f2(matrix: list[list[int]]) -> int:
    if not matrix:
        return 0
    width = len(matrix[0])
    if any(len(row) != width for row in matrix):
        raise AssertionError("ragged matrix")
    work = [[entry & 1 for entry in row] for row in matrix]
    pivot_row = 0
    for column in range(width):
        pivot = next(
            (row for row in range(pivot_row, len(work)) if work[row][column]),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        for row in range(len(work)):
            if row != pivot_row and work[row][column]:
                work[row] = [a ^ b for a, b in zip(work[row], work[pivot_row], strict=True)]
        pivot_row += 1
    return pivot_row


def matmul_f2(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    if not left:
        return []
    inner = len(left[0])
    if len(right) != inner:
        raise AssertionError("incompatible matrix dimensions")
    columns = len(right[0]) if right else 0
    return [
        [sum(left[row][k] * right[k][column] for k in range(inner)) & 1
         for column in range(columns)]
        for row in range(len(left))
    ]


def tarjan_scc(nodes: list[str], adjacency: dict[str, list[str]]) -> list[list[str]]:
    index = 0
    indices: dict[str, int] = {}
    lowlink: dict[str, int] = {}
    stack: list[str] = []
    on_stack: set[str] = set()
    components: list[list[str]] = []

    def visit(node: str) -> None:
        nonlocal index
        indices[node] = lowlink[node] = index
        index += 1
        stack.append(node)
        on_stack.add(node)
        for target in adjacency[node]:
            if target not in indices:
                visit(target)
                lowlink[node] = min(lowlink[node], lowlink[target])
            elif target in on_stack:
                lowlink[node] = min(lowlink[node], indices[target])
        if lowlink[node] == indices[node]:
            component = []
            while True:
                target = stack.pop()
                on_stack.remove(target)
                component.append(target)
                if target == node:
                    break
            components.append(sorted(component))

    for node in nodes:
        if node not in indices:
            visit(node)
    return components


def check_exit_graph(graph: dict) -> dict:
    reasons: list[str] = []
    for flag in ("coverage_complete", "component_faithful", "true_infinity_sound"):
        if graph.get(flag) is not True:
            reasons.append(flag.upper() + "_REQUIRED")

    nodes = [node["id"] for node in graph["nodes"]]
    if len(nodes) != len(set(nodes)) or not nodes:
        reasons.append("INVALID_NODE_UNIVERSE")
    node_set = set(nodes)
    true_boundary = {
        node["id"] for node in graph["nodes"]
        if node.get("boundary_kind") == "true_parent_infinity"
    }
    adjacency = {node: [] for node in nodes}
    reverse = {node: [] for node in nodes}
    for edge in graph["edges"]:
        source, target = edge["source"], edge["target"]
        if source not in node_set or target not in node_set:
            reasons.append("EDGE_OUTSIDE_NODE_UNIVERSE")
            continue
        if edge.get("same_component_continuation") is not True:
            reasons.append("UNSOUND_CONTINUATION_EDGE")
            continue
        adjacency[source].append(target)
        reverse[target].append(source)

    reachable = set(true_boundary)
    queue = deque(sorted(true_boundary))
    while queue:
        target = queue.popleft()
        for source in reverse[target]:
            if source not in reachable:
                reachable.add(source)
                queue.append(source)
    unproved_exit = sorted(node_set - reachable)
    if unproved_exit:
        reasons.append("NO_CERTIFIED_TRUE_INFINITY_PATH")

    sccs = tarjan_scc(nodes, adjacency) if node_set else []
    component_of = {
        node: index for index, component in enumerate(sccs) for node in component
    }
    sink_sccs = []
    for index, component in enumerate(sccs):
        outgoing = {
            component_of[target]
            for source in component
            for target in adjacency[source]
            if component_of[target] != index
        }
        if not outgoing:
            sink_sccs.append(component)
    sink_sccs_without_certified_infinity = [
        component for component in sink_sccs
        if not (set(component) & true_boundary)
    ]
    if bool(sink_sccs_without_certified_infinity) != bool(unproved_exit):
        raise AssertionError("reachability and sink-SCC formulations disagree")

    return {
        "accept": not reasons,
        "reasons": sorted(set(reasons)),
        "true_boundary": sorted(true_boundary),
        "vertices_without_certified_exit_path": unproved_exit,
        "sink_sccs": sink_sccs,
        "sink_sccs_without_certified_infinity": sink_sccs_without_certified_infinity,
    }


def replay_exact_44_37_cycle() -> dict:
    source = REPO / "ai/omreal/DIAG2_PIVOT_ALL_COMPACT_SECOND_WALL_VERIFY.py"
    spec = importlib.util.spec_from_file_location("diag2_two_wall_cycle", source)
    if spec is None or spec.loader is None:
        raise AssertionError("cannot load exact 37/44 verifier")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    points, derivatives = module.verify_canonical_two_wall_cycle()
    expected = {
        "p37_a": Fraction(3),
        "p37_d": Fraction(-2),
        "p44_a": Fraction(-6),
        "p44_d": Fraction(12),
    }
    if derivatives != expected or sorted(points) != ["A", "B", "C"]:
        raise AssertionError("exact 44->37->44 fixture changed")
    return {key: str(value) for key, value in sorted(derivatives.items())}


def replay_pair_countermodel(countermodel: dict) -> dict:
    boundary_1 = countermodel["boundary_1"]
    dim_c1 = len(countermodel["relative_C1_basis"])
    results = {}
    for name in ("unfilled", "filled"):
        model = countermodel[name]
        boundary_2 = model["boundary_2"]
        product = matmul_f2(boundary_1, boundary_2)
        if any(any(row) for row in product):
            raise AssertionError(f"{name} does not satisfy d1*d2=0")
        h1 = dim_c1 - rank_f2(boundary_1) - rank_f2(boundary_2)
        if h1 != model["expected_h1_f2"]:
            raise AssertionError(f"wrong H1 for {name}")
        results[name] = {
            "rank_d1": rank_f2(boundary_1),
            "rank_d2": rank_f2(boundary_2),
            "h1_f2": h1,
        }
    if results["unfilled"]["h1_f2"] == results["filled"]["h1_f2"]:
        raise AssertionError("pair countermodel failed to distinguish H1")
    return results


def replay_canonical_state() -> dict:
    # Keep the historical proof record bound to ledger v1, while separately
    # authenticating the current v2 ledger and unchanged obligations.
    ledger_compat.require_historical_ledger_binding(
        HISTORICAL_LEDGER_SHA256, "global-exit proof record"
    )
    ledger_compat.load_current_ledger(
        REPO / "ai/omreal/data/DIAG3_RESEARCH_DECISION_LEDGER.json"
    )
    for relative, expected in PINNED_SHA256.items():
        actual = sha256(REPO / relative)
        if actual != expected:
            raise AssertionError(f"source digest mismatch for {relative}: {actual}")

    completion = load_json("ai/omreal/data/DIAG3_COMPLETION_OPEN_OBJECT.json")
    pair = completion["pair_obligation"]
    triple = completion["triple_obligation"]
    current = pair["current_data"]
    if completion["ledger_score"] != "2/9":
        raise AssertionError("unexpected ledger score")
    if any(current[key] != 0 for key in (
        "certified_global_adjacencies",
        "certified_global_strict_closure_pairs",
        "certified_global_strict_closure_triples",
        "certified_parent_infinity_cells",
    )):
        raise AssertionError("global closure state changed; re-audit criterion application")
    if triple["unresolved_count"] != 1_162_302:
        raise AssertionError("triple residue changed; re-audit declared-family scope")

    pilot = load_json("ai/omreal/data/DIAG3_COMPONENT_COSHEAF_PILOT.json")
    audit = pilot["two_support_input_audit"]
    if not audit["all_inputs_missing_at_least_one_required_field"]:
        raise AssertionError("component-cosheaf input contract changed")
    required = {
        "complete strict closure pairs and strict three-cell chains",
        "true parent-infinity membership rather than local-scope boundary tags",
    }
    if not required.issubset(set(audit["blocking_contract"])):
        raise AssertionError("canonical missing-field audit changed")

    return {
        "ledger_score": completion["ledger_score"],
        "triple_unresolved": triple["unresolved_count"],
        "pair_global_adjacencies": current["certified_global_adjacencies"],
        "pair_global_strict_closure_pairs": current["certified_global_strict_closure_pairs"],
        "pair_global_strict_closure_triples": current["certified_global_strict_closure_triples"],
        "pair_parent_infinity_cells": current["certified_parent_infinity_cells"],
        "cosheaf_input_contract": audit["compiler_result"],
    }


def main() -> None:
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))
    canonical = replay_canonical_state()
    ledger_rejected = ledger_compat.verify_hostile_mutations()
    graph_results = {}
    for graph in fixtures["graphs"]:
        result = check_exit_graph(graph)
        if result["accept"] != graph["expected_accept"]:
            raise AssertionError(f"unexpected result for {graph['id']}: {result}")
        graph_results[graph["id"]] = result

    exact_cycle = replay_exact_44_37_cycle()
    cycle_result = graph_results["exact_wall_label_cycle_44_37_44"]
    if cycle_result["accept"]:
        raise AssertionError("component-free exact wall-label cycle was accepted")

    omitted = next(
        graph for graph in fixtures["graphs"]
        if graph["id"] == "omitted_edge_duplicate_component"
    )
    omitted_result = graph_results[omitted["id"]]
    component_ids = {node.get("global_component_id") for node in omitted["nodes"]}
    actual = omitted["actual_components"]["C"]
    if (
        omitted_result["accept"]
        or omitted["expected_interpretation"] != "INCONCLUSIVE_FALSE_NEGATIVE"
        or component_ids != {"C"}
        or actual["closure_meets_true_infinity"] is not True
        or set(actual["vertices"]) != {node["id"] for node in omitted["nodes"]}
    ):
        raise AssertionError("omitted-edge false-negative canary changed")

    pair = replay_pair_countermodel(fixtures["pair_countermodel"])
    pair_graph_id = fixtures["pair_countermodel"]["component_graph_id"]
    if not graph_results[pair_graph_id]["accept"]:
        raise AssertionError("pair countermodels must share an accepted exit graph")

    summary = {
        "status": "PASS",
        "criterion": fixtures["criterion"],
        "canonical": canonical,
        "graphs": {
            key: {
                "accept": value["accept"],
                "reasons": value["reasons"],
                "sink_sccs_without_certified_infinity":
                    value["sink_sccs_without_certified_infinity"],
            }
            for key, value in graph_results.items()
        },
        "exact_cycle_derivatives": exact_cycle,
        "omitted_edge_false_negative": {
            "graph_accept": omitted_result["accept"],
            "actual_component_noncompact":
                actual["closure_meets_true_infinity"],
            "interpretation": omitted["expected_interpretation"],
        },
        "pair_same_graph_countermodel": pair,
    }
    print(json.dumps(summary, indent=2, sort_keys=True))
    print("THEOREM graph acceptance is sufficient for noncompactness and equivalent to the sink-SCC predicate")
    print("INCONCLUSIVE graph rejection may be a false negative when sound edges are omitted")
    print("NO-GO component graph, even when exit-complete, does not determine pair H1")
    print(
        "PASS current ledger v2 authenticated with historical obligation semantics; "
        f"hostile mutations rejected {ledger_rejected}/{ledger_rejected}"
    )


if __name__ == "__main__":
    main()
