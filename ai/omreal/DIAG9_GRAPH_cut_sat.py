#!/usr/bin/env python3
"""Complete exact cut-SAT test for a labeled ninth-diagonal master graph.

For a pair of chamber vertices u,v, selection variables choose exactly nine
proper pairwise-incomparable regions supported by both endpoints.  Cut
variables put u and v on opposite sides.  Every master-graph edge crossing
the cut must have an endpoint removed by a selected region.  The CNF is
satisfiable exactly when those nine regions disconnect u from v.

The built-in dependency-free DPLL solver is exact.  A node limit returns
UNKNOWN and is never promoted to UNSAT.  Every satisfying assignment is
independently checked by the graph/poset routines before it is reported.
For large real instances the same clauses may be exported as DIMACS, but an
external UNSAT verdict is not trusted without an independently checked proof.

As with DIAG9_GRAPH_verify_tree_certificate.py, this program verifies the
finite labeled graph.  It does not certify that a supplied graph is a complete
semialgebraic master-chamber roadmap.
"""

from __future__ import annotations

import argparse
from collections import Counter
import importlib.util
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
TREE_VERIFIER = HERE / "DIAG9_GRAPH_verify_tree_certificate.py"
SPEC = importlib.util.spec_from_file_location("diag9_tree", TREE_VERIFIER)
tree = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(tree)
GRAPH_FORMAT = "diag9-labeled-master-graph-v1"


class CNF:
    def __init__(self):
        self.variable_count = 0
        self.clauses = []
        self.names = {}

    def variable(self, name):
        self.variable_count += 1
        self.names[self.variable_count] = tuple(name)
        return self.variable_count

    def clause(self, *literals):
        normalized = []
        seen = set()
        for raw in literals:
            literal = int(raw)
            if literal == 0:
                raise AssertionError("zero is not a CNF literal")
            if -literal in seen:
                return
            if literal not in seen:
                seen.add(literal)
                normalized.append(literal)
        self.clauses.append(tuple(normalized))


def exactly_nine_counter(cnf, variables):
    """Tseitin encode that exactly nine input variables are true."""
    variables = tuple(variables)
    if len(variables) < 9:
        cnf.clause()
        return

    # counter[i,j] means at least j of the first i inputs are true.  Tracking
    # j through 10 lets the two final units enforce >=9 and not >=10.
    counter = {}
    for index in range(len(variables) + 1):
        for level in range(11):
            counter[index, level] = cnf.variable(("counter", index, level))
    for index in range(len(variables) + 1):
        cnf.clause(counter[index, 0])
    for level in range(1, 11):
        cnf.clause(-counter[0, level])

    for index, selected in enumerate(variables, 1):
        for level in range(1, 11):
            current = counter[index, level]
            old_same = counter[index - 1, level]
            old_lower = counter[index - 1, level - 1]
            # current <-> old_same OR (old_lower AND selected)
            cnf.clause(-old_same, current)
            cnf.clause(-old_lower, -selected, current)
            cnf.clause(-current, old_same, old_lower)
            cnf.clause(-current, old_same, selected)

    cnf.clause(counter[len(variables), 9])
    cnf.clause(-counter[len(variables), 10])


def build_pair_cnf(graph, masks, source, target):
    if not (0 <= source < target < len(graph)):
        raise AssertionError("pair must satisfy 0 <= source < target < |G|")
    labels_source = tree.vertex_labels(masks, source)
    labels_target = tree.vertex_labels(masks, target)
    candidates = tuple(sorted(labels_source & labels_target))

    cnf = CNF()
    selected = {region: cnf.variable(("selected", region)) for region in candidates}
    exactly_nine_counter(cnf, selected.values())

    for left_index, left in enumerate(candidates):
        for right in candidates[left_index + 1 :]:
            if not tree.incomparable(left, right, masks):
                cnf.clause(-selected[left], -selected[right])

    side = [cnf.variable(("side", vertex)) for vertex in range(len(graph))]
    cnf.clause(-side[source])
    cnf.clause(side[target])

    for left in range(len(graph)):
        for right in graph[left]:
            if left > right:
                continue
            removed = tuple(
                selected[region]
                for region in candidates
                if not (masks[region] & (1 << left))
                or not (masks[region] & (1 << right))
            )
            # If the edge crosses the cut in either direction, at least one
            # selected region removes one of its endpoints.
            cnf.clause(side[left], -side[right], *removed)
            cnf.clause(-side[left], side[right], *removed)

    metadata = {
        "source": source,
        "target": target,
        "candidate_regions": candidates,
        "selected_variables": selected,
        "side_variables": tuple(side),
    }
    return cnf, metadata


def propagate(clauses, assignment):
    """Exact repeated unit propagation; return False on a conflict."""
    while True:
        changed = False
        for clause in clauses:
            unassigned = []
            satisfied = False
            for literal in clause:
                value = assignment[abs(literal)]
                if value < 0:
                    unassigned.append(literal)
                elif bool(value) == (literal > 0):
                    satisfied = True
                    break
            if satisfied:
                continue
            if not unassigned:
                return False
            if len(unassigned) == 1:
                literal = unassigned[0]
                variable = abs(literal)
                wanted = int(literal > 0)
                old = assignment[variable]
                if old >= 0 and old != wanted:
                    return False
                if old < 0:
                    assignment[variable] = wanted
                    changed = True
        if not changed:
            return True


def choose_variable(clauses, assignment):
    frequency = Counter()
    for clause in clauses:
        if any(
            assignment[abs(literal)] >= 0
            and bool(assignment[abs(literal)]) == (literal > 0)
            for literal in clause
        ):
            continue
        for literal in clause:
            if assignment[abs(literal)] < 0:
                frequency[abs(literal)] += 1
    return max(frequency, key=lambda variable: (frequency[variable], -variable), default=None)


def solve_exact(cnf, node_limit=None):
    """Return ('SAT', assignment), ('UNSAT', None), or ('UNKNOWN', None)."""
    nodes = 0
    hit_limit = False

    def search(assignment):
        nonlocal nodes, hit_limit
        if node_limit is not None and nodes >= node_limit:
            hit_limit = True
            return None
        nodes += 1
        assignment = assignment.copy()
        if not propagate(cnf.clauses, assignment):
            return False
        variable = choose_variable(cnf.clauses, assignment)
        if variable is None:
            return assignment
        for value in (1, 0):
            branch = assignment.copy()
            branch[variable] = value
            result = search(branch)
            if result is not False and result is not None:
                return result
            if hit_limit:
                return None
        return False

    initial = [-1] * (cnf.variable_count + 1)
    result = search(initial)
    if isinstance(result, list):
        return "SAT", result, nodes
    if hit_limit:
        return "UNKNOWN", None, nodes
    return "UNSAT", None, nodes


def selected_family(metadata, assignment):
    return tuple(
        region
        for region, variable in metadata["selected_variables"].items()
        if assignment[variable] == 1
    )


def verify_counterexample(graph, masks, metadata, assignment):
    family = selected_family(metadata, assignment)
    if len(family) != 9:
        raise AssertionError(f"SAT assignment selects {len(family)}, not nine, regions")
    if any(
        not tree.incomparable(left, right, masks)
        for left, right in __import__("itertools").combinations(family, 2)
    ):
        raise AssertionError("SAT assignment is not an antichain")
    source, target = metadata["source"], metadata["target"]
    if any(
        not (masks[region] & (1 << source) and masks[region] & (1 << target))
        for region in family
    ):
        raise AssertionError("SAT family is not supported at both endpoints")
    allowed = tuple(
        vertex
        for vertex in range(len(graph))
        if all(masks[region] & (1 << vertex) for region in family)
    )
    if tree.connected_vertices(graph, allowed, source):
        raise AssertionError("SAT assignment does not disconnect its endpoints")
    if target not in allowed:
        raise AssertionError("target unexpectedly removed")
    return {"family": family, "source": source, "target": target, "allowed": allowed}


def write_dimacs(cnf, path):
    with path.open("w", encoding="ascii") as handle:
        handle.write(f"p cnf {cnf.variable_count} {len(cnf.clauses)}\n")
        for clause in cnf.clauses:
            handle.write(" ".join(map(str, clause)) + " 0\n")


def complete_graph_test(graph, masks, node_limit=None, dimacs_prefix=None):
    total_nodes = 0
    tested = 0
    narrow = 0
    for source in range(len(graph)):
        for target in range(source + 1, len(graph)):
            common = tree.vertex_labels(masks, source) & tree.vertex_labels(masks, target)
            if tree.poset_width(common, masks) < 9:
                narrow += 1
                continue
            cnf, metadata = build_pair_cnf(graph, masks, source, target)
            if dimacs_prefix is not None:
                write_dimacs(cnf, Path(f"{dimacs_prefix}_{source}_{target}.cnf"))
            status, assignment, nodes = solve_exact(cnf, node_limit=node_limit)
            total_nodes += nodes
            tested += 1
            if status == "SAT":
                return "COUNTEREXAMPLE", verify_counterexample(
                    graph, masks, metadata, assignment
                ), {"pairs_tested": tested, "dpll_nodes": total_nodes}
            if status == "UNKNOWN":
                return "UNKNOWN", {"pair": (source, target)}, {
                    "pairs_tested": tested,
                    "dpll_nodes": total_nodes,
                }
    return "PROVED", {"narrow_pairs": narrow}, {
        "pairs_tested": tested,
        "dpll_nodes": total_nodes,
    }


def run_self_test():
    vacuous_graph, vacuous_masks, _ = tree.no_go_fixture()
    verdict, detail, stats = complete_graph_test(vacuous_graph, vacuous_masks)
    assert verdict == "PROVED"
    assert detail["narrow_pairs"] == 45

    good_graph, good_masks, _ = tree.connected_core_fixture()
    verdict, detail, stats = complete_graph_test(good_graph, good_masks)
    assert verdict == "PROVED"
    assert stats["pairs_tested"] == 3
    assert stats["dpll_nodes"] > 0

    bad_graph, bad_masks, _ = tree.disconnected_fixture()
    verdict, witness, stats_bad = complete_graph_test(bad_graph, bad_masks)
    assert verdict == "COUNTEREXAMPLE"
    assert witness["family"] == tuple(range(9))
    assert witness["source"] == 0 and witness["target"] == 2
    assert witness["allowed"] == (0, 2)

    # Canary the cardinality counter independently for n=9 and n=10.
    for size, expected in ((9, "SAT"), (10, "SAT"), (8, "UNSAT")):
        cnf = CNF()
        variables = [cnf.variable(("x", index)) for index in range(size)]
        exactly_nine_counter(cnf, variables)
        status, assignment, _ = solve_exact(cnf)
        assert status == expected
        if status == "SAT":
            assert sum(assignment[variable] for variable in variables) == 9

    print("PASS: exact-nine Tseitin counter (8/9/10-variable canaries)")
    print("PASS: complete cut-SAT proves a nontrivial connected three-vertex core")
    print("PASS: cut-SAT returns and independently verifies the disconnected fixture")
    print("THEOREM: pair CNF is SAT iff a proper nine-antichain disconnects the pair")


def load_graph(path):
    data = np.load(path, allow_pickle=False)
    fields = set(data.files)
    file_format = str(data["format"].item()) if "format" in fields else None
    valid = (
        (fields == {"format", "edge", "support"} and file_format == GRAPH_FORMAT)
        or (
            fields == {"format", "edge", "support", "tree_edge"}
            and file_format == tree.FORMAT
        )
    )
    if not valid:
        raise AssertionError(
            "expected diag9-labeled-master-graph-v1 or "
            "diag9-labeled-master-tree-v1"
        )
    masks, vertex_count = tree.support_masks(data["support"])
    edges = tree.normalize_edges(data["edge"], vertex_count)
    graph = tree.adjacency(vertex_count, edges)
    if not tree.connected_vertices(graph):
        raise AssertionError("master graph is disconnected")
    return graph, masks


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("certificate", nargs="?", type=Path)
    parser.add_argument("--node-limit", type=int)
    parser.add_argument("--dimacs-prefix")
    args = parser.parse_args()
    run_self_test()
    if args.certificate is None:
        return
    graph, masks = load_graph(args.certificate)
    verdict, detail, stats = complete_graph_test(
        graph,
        masks,
        node_limit=args.node_limit,
        dimacs_prefix=args.dimacs_prefix,
    )
    print(verdict, detail, stats)
    if verdict == "PROVED":
        print("CONDITIONAL THEOREM: every proper nine-antichain has connected support")
        print("TRUST BOUNDARY: geometric master-chamber coverage remains external")
    elif verdict == "UNKNOWN":
        print("SCOPE: node limit reached; no mathematical verdict")


if __name__ == "__main__":
    main()
