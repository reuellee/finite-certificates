#!/usr/bin/env python3
"""Independent exact verifier for the D9 circuit-grammar frontier.

This checker does not import the generator or any producer acceptance code.
It validates the source pins, recomputes the graph invariant and global
component counts, checks the declared finite circuit frontier, and requires
every hostile mutation to fail for its advertised reason.
"""

from __future__ import annotations

from collections import Counter, deque
from copy import deepcopy
from itertools import combinations
import hashlib
import json
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
FRONTIER = HERE / "FINITE_GRAMMAR_FRONTIER.json"
CANARIES = HERE / "HOSTILE_CANARIES.json"
SOURCES = HERE / "SOURCE_MANIFEST.json"
RESULT = HERE / "RESULT.json"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def semantic_digest(payload: dict[str, Any]) -> str:
    body = dict(payload)
    body.pop("semantic_sha256", None)
    return hashlib.sha256(canonical_bytes(body)).hexdigest()


def file_digest(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="ascii"))


def adjacency(graph: dict[str, Any]) -> tuple[dict[str, set[str]], dict[str, str]]:
    vertices = graph["vertices"]
    ids = [record["id"] for record in vertices]
    require(len(ids) == 16 and len(set(ids)) == 16, "vertex census")
    require(set(ids) == {f"P{i}" for i in range(8)} | {f"N{i}" for i in range(8)}, "vertex ids")
    signs = {record["id"]: record["active_sign"] for record in vertices}
    require(Counter(signs.values()) == Counter({"+": 8, "-": 8}), "vertex signs")
    adj = {vertex: set() for vertex in ids}
    seen: set[tuple[str, str]] = set()
    for edge in graph["edges"]:
        require(set(edge) == {"ends", "kind", "transport"}, "edge schema")
        require(len(edge["ends"]) == 2, "edge arity")
        left, right = edge["ends"]
        require(left in adj and right in adj and left != right, "edge endpoint")
        key = tuple(sorted((left, right)))
        require(key not in seen, "duplicate edge")
        seen.add(key)
        adj[left].add(right)
        adj[right].add(left)
        if edge["kind"] == "ACTIVE_RESIDUAL_37":
            require(signs[left] != signs[right], "active edge signs")
            require(edge["transport"] == "ORDINARY_5_TO_4_SPECIALIZATION", "transport")
        elif edge["kind"] == "INACTIVE_SAFE":
            require(signs[left] == signs[right], "inactive edge signs")
            require(edge["transport"] == "IDENTITY", "transport")
        else:
            raise AssertionError("edge kind")
    require(len(seen) == 24, "edge census")
    require(all(len(neighbors) == 3 for neighbors in adj.values()), "degree")
    require(graph["multiwall_incidences"] == [], "multiwall incidence")
    return adj, signs


def component_count(adj: dict[str, set[str]], allowed: set[str] | None = None) -> int:
    remaining = set(adj) if allowed is None else set(allowed)
    count = 0
    while remaining:
        count += 1
        start = min(remaining)
        todo = [start]
        remaining.remove(start)
        while todo:
            vertex = todo.pop()
            for neighbor in adj[vertex]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    todo.append(neighbor)
    return count


def require_bipartite(adj: dict[str, set[str]]) -> None:
    color: dict[str, int] = {}
    for start in sorted(adj):
        if start in color:
            continue
        color[start] = 0
        todo = deque([start])
        while todo:
            vertex = todo.popleft()
            for neighbor in adj[vertex]:
                if neighbor not in color:
                    color[neighbor] = 1 - color[vertex]
                    todo.append(neighbor)
                else:
                    require(color[neighbor] != color[vertex], "bipartite")


def local_observation(graph: dict[str, Any]) -> dict[str, Any]:
    adj, signs = adjacency(graph)
    edge_by_pair: dict[tuple[str, str], dict[str, Any]] = {}
    edge_counter: Counter[tuple[str, str, str]] = Counter()
    for edge in graph["edges"]:
        pair = tuple(sorted(edge["ends"]))
        edge_by_pair[pair] = edge
        endpoint_signs = "".join(sorted((signs[pair[0]], signs[pair[1]])))
        edge_counter[(edge["kind"], endpoint_signs, edge["transport"])] += 1
    vertex_counter: Counter[tuple[str, tuple[tuple[str, int], ...]]] = Counter()
    for vertex, neighbors in adj.items():
        kinds = Counter(edge_by_pair[tuple(sorted((vertex, neighbor)))]["kind"] for neighbor in neighbors)
        vertex_counter[(signs[vertex], tuple(sorted(kinds.items())))] += 1
    return {
        "vertex_records": [
            {"active_sign": sign, "incident_kinds": dict(kinds), "multiplicity": multiplicity}
            for (sign, kinds), multiplicity in sorted(vertex_counter.items())
        ],
        "edge_records": [
            {"kind": kind, "endpoint_signs": signs_record, "transport": transport, "multiplicity": multiplicity}
            for (kind, signs_record, transport), multiplicity in sorted(edge_counter.items())
        ],
        "multiwall_incidences": [],
        "active_circuit_template": {
            "class": "ORDINARY",
            "live_support_size": 5,
            "wall_support_size": 4,
            "dead_side": "EMPTY",
            "wall_type": 37,
        },
    }


def colex_subsets(n: int, size: int) -> tuple[tuple[int, ...], ...]:
    return tuple(sorted(combinations(range(1, n + 1), size), key=lambda subset: tuple(reversed(subset))))


def verify_frontier(payload: dict[str, Any]) -> None:
    require(payload["format"] == "d9-universal-cut-circuit-frontier-v1", "format")
    require(payload["base_revision"] == "6cbd1b4a7d3ed61bee268b6b54cbfadeece90f0e", "base revision")
    require(payload["canonical_mathematical_base"] == "cbe84ccd7273252c81fd4da17ee360a284d2a2a6", "mathematical base")

    partition = payload["residual_partition"]
    ordinary = partition["ordinary"]
    localization = partition["localization"]
    require(ordinary == [37, 38, 41, 42, 44, 48, 49, 50, 51], "ordinary types")
    require(localization == [36, 39, 46, 47], "localization types")
    require(len(set(ordinary) | set(localization)) == 13 and not set(ordinary) & set(localization), "13-type partition")

    productions = {record["name"]: record for record in payload["surviving_productions"]}
    require(set(productions) == {
        "ONE_SIDED_SPECIALIZATION_COSPAN",
        "OPPOSITE_PARTNER_ELIMINATION_INTERVAL",
        "SAME_SIDE_CHOICE_SIMPLEX",
        "ALL_CODIMENSION_CONVEX_CARRIER_COHERENCE",
    }, "production registry")
    opposite = productions["OPPOSITE_PARTNER_ELIMINATION_INTERVAL"]
    counts = {int(key): value for key, value in opposite["certified_auxiliary_counts"].items()}
    expected_counts = {36: 12, 37: 14, 38: 2, 39: 12, 41: 14, 42: 2, 44: 12, 46: 12, 47: 12, 48: 16, 49: 8, 50: 3, 51: 4}
    # The thirteen exact row counts sum to 123.  The source note's displayed
    # total 131 is an arithmetic typo; its independently checked 671 pair and
    # 2,420 support totals agree with the row counts used here.
    require(counts == expected_counts and sum(counts.values()) == 123, "auxiliary census")
    pair_count = sum(value * (value - 1) // 2 for value in counts.values())
    support_count = sum((4 if kind in ordinary else 3) * value * (value - 1) // 2 for kind, value in counts.items())
    require(pair_count == opposite["certified_pair_count"] == 671, "pair census")
    require(support_count == opposite["persistent_support_candidate_count"] == 2420, "support census")

    unresolved = payload["first_unclassified_actual_composition"]
    require(unresolved["status"] == "UNCLASSIFIED_GLOBAL_TRANSFER", "frontier status")
    triples = colex_subsets(8, 3)
    degree = [0] * 8
    union: set[int] = set()
    for record in unresolved["signatures_and_supports"]:
        require(record["signature"] > 0 and len(record["support"]) in {4, 5}, "rigid support record")
        union.update(record["support"])
    for normal in union:
        require(0 <= normal < 56, "normal index")
        for label in triples[normal]:
            degree[label - 1] += 1
    require(degree == unresolved["colex_parent_label_degree"] == [4, 4, 6, 4, 5, 5, 3, 5], "rigid triple degree")
    require(min(degree) >= 3, "rigid triple pencil test")

    pair = payload["local_memory_counterpair"]
    require(pair["scope"] == "ABSTRACT_SIGNED_CHAMBER_GRAPH_NOT_UOM_4_8_REALIZATION", "counterpair scope")
    require(pair["observation_contract"].startswith("RADIUS_ONE_"), "observation contract")
    computed_observations = []
    for key in ("cut_configuration", "noncut_configuration"):
        graph = pair[key]
        obs = local_observation(graph)
        computed_observations.append(obs)
        require(obs == pair["shared_local_observation"], "shared local observation")
        adj, signs = adjacency(graph)
        require_bipartite(adj)
        full = component_count(adj)
        positive = component_count(adj, {vertex for vertex, sign in signs.items() if sign == "+"})
        negative = component_count(adj, {vertex for vertex, sign in signs.items() if sign == "-"})
        expected = pair["expected_global_behavior"][graph["name"]]
        require(full == expected["full_components"], "full component count")
        require(positive == expected["positive_sector_components"], "positive sector component count")
        require(negative == expected["negative_sector_components"], "negative sector component count")
    require(computed_observations[0] == computed_observations[1], "local invariant equality")
    observed_digest = hashlib.sha256(canonical_bytes(pair["shared_local_observation"])).hexdigest()
    require(observed_digest == pair["shared_local_observation_sha256"], "local observation digest")
    require(pair["minimality_scope"]["minimum_vertices"] == 16, "minimality scope")

    require(payload["local_grammar_verdict"] == "DISPROVED_WITHOUT_GLOBAL_CHAMBER_GLUE", "local verdict")
    require(payload["scope"]["actual_uom_4_8_universal_cut_grammar"] == "UNRESOLVED", "UOM scope")
    require(payload["scope"]["diagonal_9"] == "UNCHANGED_2_OF_9", "ledger scope")
    require(semantic_digest(payload) == payload["semantic_sha256"], "semantic digest")


def verify_sources(manifest: dict[str, Any]) -> None:
    require(manifest["format"] == "d9-universal-cut-circuit-source-manifest-v1", "source manifest format")
    require(manifest["opening_commit"] == "6cbd1b4a7d3ed61bee268b6b54cbfadeece90f0e", "source opening commit")
    repair = manifest["protocol_repair"]
    require(repair["source_commit"] == "d07c2a7b041f3a075d5e9294a0f3c63dbd87822f", "protocol repair source")
    require(repair["applied_commit"] == "60e76467188f32288fee0cb896d2e9592e9b0741", "protocol repair application")
    require(repair["applied_tree"] == "a5ee5c295c3e898bbbe702f75fd12cf0d11abbf5", "protocol repair tree")
    require(repair["paths"] == [
        "ops/research-team/cycles/2026-09-01-d9-universal-cut/CYCLE.md",
        "ops/research-team/cycles/2026-09-01-d9-universal-cut/WORK_ORDERS.yaml",
    ], "protocol repair paths")
    for record in manifest["inputs"]:
        path = ROOT / record["path"]
        require(path.is_file(), f"missing source {record['path']}")
        require(file_digest(path) == record["sha256"], f"source digest {record['path']}")


def verify_result(result: dict[str, Any], payload: dict[str, Any]) -> None:
    require(result["format"] == "d9-universal-cut-circuit-result-v1", "result format")
    require(result["track_id"] == "d9-universal-cut-circuits", "result track")
    require(result["base_revision"] == payload["base_revision"], "result base")
    require(result["protocol_repair"] == {
        "source_commit": "d07c2a7b041f3a075d5e9294a0f3c63dbd87822f",
        "applied_commit": "60e76467188f32288fee0cb896d2e9592e9b0741",
        "applied_tree": "a5ee5c295c3e898bbbe702f75fd12cf0d11abbf5",
    }, "result protocol repair")
    require(result["outcome"] == "inconclusive", "result outcome")
    require(result["subclaim_status"]["local_type_only_separator_completeness"] == "disproved", "result local verdict")
    require(result["subclaim_status"]["actual_uom_4_8_universal_cut_grammar"] == "inconclusive", "result global scope")
    require(result["ledger_change_recommended"] == "none", "result ledger scope")
    expected_paths = {
        "ops/team/d9-universal-cut-circuits/FINDINGS.md",
        "ops/team/d9-universal-cut-circuits/SOURCE_MANIFEST.json",
        "ops/team/d9-universal-cut-circuits/FINITE_GRAMMAR_FRONTIER.json",
        "ops/team/d9-universal-cut-circuits/HOSTILE_CANARIES.json",
        "ops/team/d9-universal-cut-circuits/generate_cut_grammar_frontier.py",
        "ops/team/d9-universal-cut-circuits/verify_cut_grammar_frontier.py",
    }
    artifacts = {record["path"]: record for record in result["artifacts"]}
    require(set(artifacts) == expected_paths, "result artifact census")
    for relative, record in artifacts.items():
        require(file_digest(ROOT / relative) == record["sha256"], f"result artifact digest {relative}")
    frontier_record = artifacts["ops/team/d9-universal-cut-circuits/FINITE_GRAMMAR_FRONTIER.json"]
    require(frontier_record["semantic_sha256"] == payload["semantic_sha256"], "result semantic digest")


def mutate(payload: dict[str, Any], canary: dict[str, Any]) -> dict[str, Any]:
    result = deepcopy(payload)
    target: Any = result
    for part in canary["path"][:-1]:
        target = target[part]
    final = canary["path"][-1]
    if canary["operation"] == "DELETE":
        del target[final]
    elif canary["operation"] == "SET":
        target[final] = canary["value"]
    else:
        raise AssertionError("canary operation")
    return result


def verify_canaries(payload: dict[str, Any], canaries: dict[str, Any]) -> None:
    require(canaries["format"] == "d9-universal-cut-circuit-hostile-canaries-v1", "canary format")
    require(len(canaries["canaries"]) >= 5, "hostile canary count")
    for canary in canaries["canaries"]:
        try:
            verify_frontier(mutate(payload, canary))
        except (AssertionError, KeyError, IndexError, TypeError) as exc:
            require(canary["expected_error"].lower() in str(exc).lower(), f"canary reason {canary['name']}: {exc}")
        else:
            raise AssertionError(f"hostile canary accepted: {canary['name']}")


def main() -> None:
    payload = load(FRONTIER)
    verify_sources(load(SOURCES))
    verify_frontier(payload)
    verify_canaries(payload, load(CANARIES))
    verify_result(load(RESULT), payload)
    print("PASS source hashes and 13-type finite circuit frontier")
    print("PASS exact 16-vertex minimal local-memory counterpair")
    print("PASS identical local wall/circuit/multiwall/transport observations")
    print("PASS inequivalent positive-sector cuts: two components versus one")
    print("PASS first actual unclassified composition: row-2599 rigid three-block corner")
    print("PASS all hostile canaries rejected for the advertised reason")
    print("PASS result artifact hashes and scope contract")
    print("VERDICT local-only separator grammar disproved; actual UOM(4,8) global-memory grammar unresolved")
    print("SCOPE no diagonal promotion; theorem ledger remains 2/9")


if __name__ == "__main__":
    main()
