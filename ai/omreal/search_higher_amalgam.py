#!/usr/bin/env python3
"""Exact bounded search for higher-order abstract amalgamation obstructions.

The input vertices are the 220 extension signatures stored in the row-2599
width-seven certificate.  A tested set must avoid every certified incompatible
pair.  The program asks whether its prescribed one-element restrictions extend
to a *uniform abstract* rank-4 chirotope on all old and new elements.

Every three-term Grassmann--Pluecker predicate is expanded to CNF and solved by
a deterministic exhaustive DPLL routine.  UNSAT is therefore a sound
real-chart incompatibility verdict when the search is replayed, but this pilot
does not yet emit a DRAT/LRAT proof artifact.  SAT is only a necessary
condition: the resulting oriented matroid need not be realizable over one
parent chart.

Run ``verify_seeat_width7.py`` first.  This program pins the NPZ by SHA-256 and
validates its basic schema, but deliberately does not duplicate that verifier's
exact realization and nonamalgamation checks.
"""

from __future__ import annotations

import argparse
import hashlib
from itertools import combinations
from pathlib import Path
import random
import time

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
CERTIFICATE = ROOT / "ai/omreal/data/seeat_parent2599_width7.npz"
CERTIFICATE_SHA256 = "ec7ef2ad9f37467e00a5ea739d67f90c4c53b304f4d82d47ac72591a58477dc7"


def colex_subsets(n: int, size: int) -> tuple[tuple[int, ...], ...]:
    """Return subsets in the colex order used by the OM catalog."""
    return tuple(
        sorted(
            combinations(range(1, n + 1), size),
            key=lambda subset: tuple(reversed(subset)),
        )
    )


BASES8 = colex_subsets(8, 4)
BASE8_INDEX = {basis: i for i, basis in enumerate(BASES8)}
TRIPLES8 = colex_subsets(8, 3)
TRIPLE8_INDEX = {triple: i for i, triple in enumerate(TRIPLES8)}


def parity_sort(values: tuple[int, ...]) -> tuple[tuple[int, ...], int]:
    """Sort a tuple and return the parity of the sorting permutation."""
    values = list(values)
    parity = 0
    for i in range(1, len(values)):
        j = i
        while j and values[j - 1] > values[j]:
            values[j - 1], values[j] = values[j], values[j - 1]
            parity ^= 1
            j -= 1
    return tuple(values), parity


def compile_relations(
    parent: np.ndarray, signatures: list[int]
) -> tuple[list[tuple[int, ...]], list[tuple[tuple[tuple[int, ...], int], ...]]]:
    """Compile all rank-4 GP relations for prescribed one-point restrictions.

    A sign is represented by a bit.  Bases containing zero or one new element
    are prescribed by the parent and child signatures.  Bases containing at
    least two new elements become Boolean variables.
    """
    number_new = len(signatures)
    number_elements = 8 + number_new
    unknown = [
        basis
        for basis in combinations(range(1, number_elements + 1), 4)
        if sum(element > 8 for element in basis) >= 2
    ]
    variable = {basis: i for i, basis in enumerate(unknown)}

    def bracket(basis: tuple[int, ...]) -> tuple[tuple[int, ...], int]:
        new = [element for element in basis if element > 8]
        if not new:
            return (), int(parent[BASE8_INDEX[basis]])
        if len(new) == 1:
            old = tuple(element for element in basis if element <= 8)
            bit = (int(signatures[new[0] - 9]) >> TRIPLE8_INDEX[old]) & 1
            return (), bit
        return (variable[basis],), 0

    relations = []
    for lam in combinations(range(1, number_elements + 1), 2):
        rest = [
            element
            for element in range(1, number_elements + 1)
            if element not in lam
        ]
        for a, b, c, d in combinations(rest, 4):
            terms = []
            # [lab][lcd] - [lac][lbd] + [lad][lbc]
            for pairs, minus in (
                (((a, b), (c, d)), 0),
                (((a, c), (b, d)), 1),
                (((a, d), (b, c)), 0),
            ):
                variables = []
                constant = minus
                for x, y in pairs:
                    basis, parity = parity_sort(lam + (x, y))
                    constant ^= parity
                    local_variables, local_constant = bracket(basis)
                    variables.extend(local_variables)
                    constant ^= local_constant
                odd_variables = tuple(
                    sorted(
                        value
                        for value in set(variables)
                        if variables.count(value) & 1
                    )
                )
                terms.append((odd_variables, constant))
            relations.append(tuple(terms))
    return unknown, relations


def relations_to_cnf(
    number_variables: int,
    relations: list[tuple[tuple[tuple[int, ...], int], ...]],
) -> tuple[list[tuple[int, ...]], list[list[int]]] | None:
    """Expand the forbidden all-equal product signs into exact CNF."""
    clauses: set[tuple[int, ...]] = set()
    for terms in relations:
        local = tuple(sorted({value for values, _ in terms for value in values}))
        for mask in range(1 << len(local)):
            assignment = {
                value: (mask >> i) & 1 for i, value in enumerate(local)
            }
            product_signs = []
            for values, original_constant in terms:
                constant = original_constant
                for value in values:
                    constant ^= assignment[value]
                product_signs.append(constant)
            if product_signs[0] == product_signs[1] == product_signs[2]:
                clause = tuple(
                    value + 1 if not assignment[value] else -(value + 1)
                    for value in local
                )
                if not clause:
                    return None
                clauses.add(clause)

    ordered = sorted(clauses, key=lambda clause: (len(clause), clause))
    occurrences: list[list[int]] = [[] for _ in range(number_variables)]
    for clause_index, clause in enumerate(ordered):
        for literal in clause:
            occurrences[abs(literal) - 1].append(clause_index)
    return ordered, occurrences


class Solver:
    """Small deterministic DPLL solver, kept here to make the gate auditable."""

    def __init__(
        self,
        number_variables: int,
        clauses: list[tuple[int, ...]],
        occurrences: list[list[int]],
        node_limit: int,
    ) -> None:
        self.number_variables = number_variables
        self.clauses = clauses
        self.occurrences = occurrences
        self.assignment = [-1] * number_variables
        self.nodes = 0
        self.node_limit = node_limit
        self.hit_limit = False
        self.score = [len(items) for items in occurrences]

    def literal_true(self, literal: int) -> bool:
        value = self.assignment[abs(literal) - 1]
        return value >= 0 and value == (literal > 0)

    def propagate(self, queue: list[int], trail: list[int]) -> bool:
        pending: set[int] = set()
        while queue:
            variable = queue.pop()
            pending.update(self.occurrences[variable])
            while pending:
                clause = self.clauses[pending.pop()]
                if any(self.literal_true(literal) for literal in clause):
                    continue
                unset = [
                    literal
                    for literal in clause
                    if self.assignment[abs(literal) - 1] < 0
                ]
                if not unset:
                    return False
                if len(unset) == 1:
                    literal = unset[0]
                    implied = abs(literal) - 1
                    value = int(literal > 0)
                    if self.assignment[implied] >= 0:
                        if self.assignment[implied] != value:
                            return False
                    else:
                        self.assignment[implied] = value
                        trail.append(implied)
                        queue.append(implied)
        return True

    def dfs(self) -> list[int] | bool | None:
        self.nodes += 1
        if self.nodes > self.node_limit:
            self.hit_limit = True
            return None
        unset = [
            variable
            for variable, value in enumerate(self.assignment)
            if value < 0
        ]
        if not unset:
            return self.assignment.copy()
        variable = max(unset, key=lambda item: self.score[item])
        for value in (0, 1):
            trail = [variable]
            self.assignment[variable] = value
            consistent = self.propagate([variable], trail)
            answer = self.dfs() if consistent else False
            for item in reversed(trail):
                self.assignment[item] = -1
            if answer is None:
                return None
            if answer is not False:
                return answer
        return False

    def solve(self) -> list[int] | bool | None:
        trail = []
        for clause in self.clauses:
            if not clause:
                return False
            if len(clause) > 1:
                break
            literal = clause[0]
            variable = abs(literal) - 1
            value = int(literal > 0)
            if self.assignment[variable] >= 0 and self.assignment[variable] != value:
                return False
            if self.assignment[variable] < 0:
                self.assignment[variable] = value
                trail.append(variable)
        if not self.propagate(trail.copy(), trail):
            return False
        return self.dfs()


def check(
    indices: tuple[int, ...],
    parent: np.ndarray,
    signatures: np.ndarray,
    node_limit: int,
) -> tuple[list[int] | bool | None, int, int, int, int, bool]:
    """Return answer, DPLL nodes, variables, relations, clauses, limit flag."""
    unknown, relations = compile_relations(
        parent, [int(signatures[index]) for index in indices]
    )
    compiled = relations_to_cnf(len(unknown), relations)
    if compiled is None:
        return False, 0, len(unknown), len(relations), 0, False
    clauses, occurrences = compiled
    solver = Solver(len(unknown), clauses, occurrences, node_limit)
    answer = solver.solve()
    return (
        answer,
        solver.nodes,
        len(unknown),
        len(relations),
        len(clauses),
        solver.hit_limit,
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--k", type=int, default=3)
    parser.add_argument("--tests", type=int, default=100)
    parser.add_argument("--seed", type=int, default=2599)
    parser.add_argument("--node-limit", type=int, default=2_000_000)
    parser.add_argument("--systematic", action="store_true")
    parser.add_argument("--quiet", action="store_true")
    parser.add_argument(
        "--color",
        type=int,
        choices=range(7),
        default=None,
        help="restrict candidates to one stored seven-color class",
    )
    parser.add_argument(
        "--sanity",
        action="store_true",
        help="first check one certified negative and one positive pair",
    )
    args = parser.parse_args()

    if args.k < 3:
        parser.error("--k must be at least 3; pairs are covered by the stored certificate")
    if args.tests < 1:
        parser.error("--tests must be positive")
    if args.node_limit < 1:
        parser.error("--node-limit must be positive")

    digest = hashlib.sha256(CERTIFICATE.read_bytes()).hexdigest()
    if digest != CERTIFICATE_SHA256:
        raise SystemExit(
            f"certificate SHA-256 mismatch: expected {CERTIFICATE_SHA256}, got {digest}"
        )

    certificate = np.load(CERTIFICATE, allow_pickle=False)
    if str(certificate["format"]) != "seeat-parent2599-width7-v1":
        raise SystemExit("unexpected certificate format")
    if int(certificate["parent_index"]) != 2599:
        raise SystemExit("unexpected parent index")
    parent = certificate["parent_bits"]
    signatures = certificate["vertex_signature"]
    edges_array = certificate["edge_uv"]
    if parent.shape != (70,) or signatures.shape != (220,):
        raise SystemExit("unexpected parent or vertex shape")
    if edges_array.shape != (3472, 2):
        raise SystemExit("unexpected certified-edge shape")
    if len(set(map(int, signatures))) != len(signatures):
        raise SystemExit("duplicate stored signatures")
    number_vertices = len(signatures)
    universe = (
        list(np.flatnonzero(certificate["coloring7"] == args.color))
        if args.color is not None
        else list(range(number_vertices))
    )
    if args.k > len(universe):
        parser.error(f"--k={args.k} exceeds the selected universe size {len(universe)}")
    edges = {tuple(map(int, edge)) for edge in edges_array}

    def avoids_certified_edges(candidate: tuple[int, ...]) -> bool:
        return all(
            tuple(sorted(pair)) not in edges for pair in combinations(candidate, 2)
        )

    if args.sanity:
        for pair, expected in (((156, 146), False), ((0, 1), True)):
            answer, nodes, *_ = check(pair, parent, signatures, args.node_limit)
            state = "LIMIT" if answer is None else ("UNSAT" if answer is False else "SAT")
            print(f"SANITY {pair} {state} nodes={nodes} expected={'SAT' if expected else 'UNSAT'}")
            if answer is None or (answer is not False) != expected:
                raise SystemExit("sanity check failed")

    rng = random.Random(args.seed)
    if args.systematic:
        candidates = (
            candidate
            for candidate in combinations(universe, args.k)
            if avoids_certified_edges(candidate)
        )
    else:

        def random_candidates():
            seen = set()
            failed_draws = 0
            while len(seen) < args.tests:
                candidate = tuple(sorted(rng.sample(universe, args.k)))
                if candidate not in seen and avoids_certified_edges(candidate):
                    seen.add(candidate)
                    failed_draws = 0
                    yield candidate
                else:
                    failed_draws += 1
                    if failed_draws > 1_000_000:
                        raise RuntimeError("could not draw another compatible candidate")

        candidates = random_candidates()

    started = time.time()
    sat = unsat = limited = 0
    for test_number, candidate in enumerate(candidates, 1):
        if test_number > args.tests:
            break
        answer, nodes, variables, relations, clauses, _hit_limit = check(
            candidate, parent, signatures, args.node_limit
        )
        state = "LIMIT" if answer is None else ("UNSAT" if answer is False else "SAT")
        if answer is None:
            limited += 1
        elif answer is False:
            unsat += 1
        else:
            sat += 1
        if not args.quiet or answer is False or answer is None:
            print(
                f"{test_number:5d} {candidate} {state} nodes={nodes} "
                f"vars={variables} rels={relations} clauses={clauses} "
                f"elapsed={time.time() - started:.2f}",
                flush=True,
            )
        if answer is False:
            print("UNSAT-HIGHER-CANDIDATE", candidate, flush=True)
            break

    print(
        f"SUMMARY tested={sat + unsat + limited} sat={sat} unsat={unsat} "
        f"limit={limited} seconds={time.time() - started:.3f}"
    )


if __name__ == "__main__":
    main()
