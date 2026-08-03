#!/usr/bin/env python3
"""Exact verifier for atlas_width(parent row 2599) >= 7.

An edge joins two realizable single-element signatures with no abstract uniform
two-element oriented-matroid amalgam.  If both occurred over one real parent
matrix, perturbing the second new column inside its open sign cone and away
from the 28 mixed-bracket hyperplanes would produce such a uniform amalgam.
Thus every realization chart is an independent set.  The certificate proves
that its 220-vertex incompatibility graph is not 6-colorable.
"""

from itertools import combinations
from pathlib import Path
import sys

import numpy as np

import verify_seeat_k6 as core


DEFAULT = Path(__file__).resolve().parent / "data" / "seeat_parent2599_width7.npz"


class ColoringProofVerifier:
    """Verify a preorder exhaustive 6-color finite-domain proof tree."""

    def __init__(self, adjacency, color_count, proof):
        self.adjacency = adjacency
        self.color_count = color_count
        self.domains = [(1 << color_count) - 1] * len(adjacency)
        self.trail = []
        self.proof = proof

    def reduce(self, vertex, new_domain):
        old_domain = self.domains[vertex]
        if old_domain == new_domain:
            return new_domain != 0
        self.trail.append((vertex, old_domain))
        self.domains[vertex] = new_domain
        return new_domain != 0

    def assign_and_propagate(self, vertex, color_bit):
        if not self.domains[vertex] & color_bit:
            return False
        if not self.reduce(vertex, color_bit):
            return False
        queue = [vertex]
        for assigned in queue:
            assigned_bit = self.domains[assigned]
            if not assigned_bit or assigned_bit & (assigned_bit - 1):
                raise AssertionError("propagation queue contains a non-singleton")
            for neighbor in self.adjacency[assigned]:
                domain = self.domains[neighbor]
                if domain == assigned_bit:
                    return False
                if domain & assigned_bit:
                    reduced = domain & ~assigned_bit
                    if not self.reduce(neighbor, reduced):
                        return False
                    if reduced & (reduced - 1) == 0:
                        queue.append(neighbor)
        return True

    def choose_vertex(self):
        best_vertex = -1
        best_key = None
        for vertex, domain in enumerate(self.domains):
            size = domain.bit_count()
            if size <= 1:
                continue
            singleton_colors = 0
            for neighbor in self.adjacency[vertex]:
                neighbor_domain = self.domains[neighbor]
                if neighbor_domain and neighbor_domain & (neighbor_domain - 1) == 0:
                    singleton_colors |= neighbor_domain
            key = (size, -singleton_colors.bit_count(), -len(self.adjacency[vertex]), vertex)
            if best_key is None or key < best_key:
                best_key = key
                best_vertex = vertex
        return best_vertex

    def parse(self, position=0):
        if position >= len(self.proof):
            raise AssertionError("color proof ended before all branches were covered")
        expected = self.choose_vertex()
        if expected < 0:
            raise AssertionError("color proof reached a valid six-coloring")
        vertex = int(self.proof[position])
        position += 1
        if vertex != expected:
            raise AssertionError("color proof names the wrong deterministic branch vertex")

        candidates = []
        remaining = self.domains[vertex]
        while remaining:
            color_bit = remaining & -remaining
            remaining -= color_bit
            impact = sum(
                self.domains[neighbor].bit_count() > 1
                and bool(self.domains[neighbor] & color_bit)
                for neighbor in self.adjacency[vertex]
            )
            candidates.append((impact, color_bit))

        # Every currently possible color is covered.  Immediate propagation
        # conflicts need no child; every surviving branch consumes one subtree.
        for _, color_bit in sorted(candidates):
            checkpoint = len(self.trail)
            if self.assign_and_propagate(vertex, color_bit):
                position = self.parse(position)
            while len(self.trail) > checkpoint:
                restored, old_domain = self.trail.pop()
                self.domains[restored] = old_domain
        return position


def main():
    path = Path(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT
    if len(sys.argv) > 2:
        raise SystemExit(f"usage: {sys.argv[0]} [certificate.npz]")
    cert = np.load(path, allow_pickle=False)
    fields = {
        "format", "parent_index", "parent_bits", "source_index",
        "vertex_signature", "realization_matrix", "realization_point",
        "edge_uv", "trace_offset", "trace_var", "trace_value",
        "trace_relation", "final_relation", "clique_vertex",
        "color_proof_vertex", "coloring7", "positive_pair", "positive_mixed",
    }
    if set(cert.files) != fields:
        raise AssertionError(f"wrong fields: {sorted(cert.files)}")
    if str(cert["format"].item()) != "seeat-parent2599-width7-v1":
        raise AssertionError("wrong format")
    if int(cert["parent_index"].item()) != 2599:
        raise AssertionError("wrong parent index")

    parent = cert["parent_bits"]
    signatures = cert["vertex_signature"]
    matrices = cert["realization_matrix"]
    points = cert["realization_point"]
    if parent.shape != (70,) or set(parent.tolist()) - {0, 1}:
        raise AssertionError("bad parent bits")
    if signatures.shape != (220,) or len(set(map(int, signatures))) != 220:
        raise AssertionError("need 220 distinct signatures")
    if cert["source_index"].shape != (220,):
        raise AssertionError("bad source-index metadata")
    if matrices.shape != (220, 4, 8) or points.shape != (220, 4):
        raise AssertionError("bad realization witness shapes")
    if not core.generic_gp_valid(parent):
        raise AssertionError("parent is not a uniform chirotope")
    for i, (signature, matrix, point) in enumerate(zip(signatures, matrices, points)):
        if not core.generic_gp_valid(parent, int(signature)):
            raise AssertionError(f"vertex {i} is not an abstract uniform extension")
        got_parent, got_signature = core.parent_and_extension(matrix, point)
        if not np.array_equal(got_parent, parent) or got_signature != int(signature):
            raise AssertionError(f"vertex {i} exact realization has wrong signs")
    print("PASS 220 distinct exact realizable uniform extensions over parent 2599")

    edges = cert["edge_uv"]
    if edges.shape != (3472, 2):
        raise AssertionError("bad edge shape")
    edge_set = set()
    previous = None
    adjacency = [set() for _ in range(220)]
    for edge_index, (u0, v0) in enumerate(edges):
        u, v = int(u0), int(v0)
        if not 0 <= u < v < 220 or (u, v) in edge_set:
            raise AssertionError(f"bad edge {edge_index}")
        if previous is not None and (u, v) <= previous:
            raise AssertionError("edges are not in strict lexicographic order")
        previous = (u, v)
        edge_set.add((u, v))
        adjacency[u].add(v)
        adjacency[v].add(u)

    offsets = cert["trace_offset"].astype(int)
    if offsets.shape != (len(edges) + 1,) or offsets[0] != 0:
        raise AssertionError("bad trace offsets")
    if not (
        offsets[-1]
        == len(cert["trace_var"])
        == len(cert["trace_value"])
        == len(cert["trace_relation"])
    ):
        raise AssertionError("bad flattened trace arrays")
    if cert["final_relation"].shape != (len(edges),):
        raise AssertionError("bad final-relation array")
    templates = core.relation_templates(parent)
    sizes = []
    for edge_index, (u0, v0) in enumerate(edges):
        u, v = int(u0), int(v0)
        sigma, tau = int(signatures[u]), int(signatures[v])
        values = {}
        start, stop = offsets[edge_index : edge_index + 2]
        sizes.append(stop - start)
        for step in range(start, stop):
            variable = int(cert["trace_var"][step])
            value = int(cert["trace_value"][step])
            relation_id = int(cert["trace_relation"][step])
            if not (0 <= variable < 28 and value in (0, 1) and 0 <= relation_id < 3150):
                raise AssertionError(f"edge {edge_index}: malformed trace step")
            if variable in values:
                raise AssertionError(f"edge {edge_index}: variable forced twice")
            relation = core.resolve(templates[relation_id], sigma, tau)
            if core.unassigned(relation, values) != {variable}:
                raise AssertionError(f"edge {edge_index}: cited GP relation is not unit")
            choices = []
            for trial in (0, 1):
                values[variable] = trial
                choices.append(core.valid(relation, values))
                del values[variable]
            if choices.count(True) != 1 or not choices[value]:
                raise AssertionError(f"edge {edge_index}: wrong forced value")
            values[variable] = value
        final_id = int(cert["final_relation"][edge_index])
        if not 0 <= final_id < 3150:
            raise AssertionError(f"edge {edge_index}: bad final relation")
        final = core.resolve(templates[final_id], sigma, tau)
        if core.unassigned(final, values) or core.valid(final, values):
            raise AssertionError(f"edge {edge_index}: final GP relation is not contradictory")
    print(
        f"PASS 3,472 pairwise non-amalgamation certificates "
        f"({sum(sizes):,} propagation steps, {min(sizes)}..{max(sizes)} per edge)"
    )

    positive_pair = tuple(map(int, cert["positive_pair"]))
    if len(positive_pair) != 2 or positive_pair in edge_set:
        raise AssertionError("bad positive-control pair")
    positive = {i: int(value) for i, value in enumerate(cert["positive_mixed"])}
    if len(positive) != 28 or set(positive.values()) - {0, 1}:
        raise AssertionError("bad positive-control mixed signs")
    sigma, tau = (int(signatures[i]) for i in positive_pair)
    for relation_id, template in enumerate(templates):
        if not core.valid(core.resolve(template, sigma, tau), positive):
            raise AssertionError(f"positive control fails GP relation {relation_id}")
    print("PASS positive control: one full uniform two-element amalgam")

    clique = tuple(map(int, cert["clique_vertex"]))
    if len(clique) != 6 or len(set(clique)) != 6:
        raise AssertionError("bad K6 vertex list")
    if not all(tuple(sorted((u, v))) in edge_set for u, v in combinations(clique, 2)):
        raise AssertionError("fixed color-symmetry breaker is not a K6")
    proof = cert["color_proof_vertex"]
    coloring_verifier = ColoringProofVerifier(adjacency, 6, proof)
    for color, vertex in enumerate(clique):
        if not coloring_verifier.assign_and_propagate(vertex, 1 << color):
            raise AssertionError("fixed K6 color assignment contradicts itself")
    consumed = coloring_verifier.parse()
    if consumed != len(proof):
        raise AssertionError("color proof has trailing nodes")
    print(f"PASS exact 6-color UNSAT proof tree ({len(proof):,} CSP nodes)")

    colors = cert["coloring7"].astype(int)
    if colors.shape != (220,) or colors.min() < 0 or colors.max() != 6:
        raise AssertionError("bad seven-color witness")
    if any(colors[u] == colors[v] for u, v in edge_set):
        raise AssertionError("seven-color witness has a monochromatic edge")
    print("PASS explicit 7-coloring; incompatibility graph has chromatic number 7")
    print("THEOREM: atlas width(parent 2599) >= 7; neither five nor six charts suffice")


if __name__ == "__main__":
    main()
