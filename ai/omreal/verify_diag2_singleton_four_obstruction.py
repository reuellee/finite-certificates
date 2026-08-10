#!/usr/bin/env python3
"""Exact GP obstruction for four-singleton diagonal-two covers.

Assume each of two bad extension signatures has exactly four complete-tope
neighbors at Hamming distance one and that these singleton disagreements are
its complete minimal-separator family.  If their escape masks were disjoint,
the eight mutation triples would form a linear 3-uniform 8_3 configuration.
There is one uncolored configuration orbit and three 4+4 color orbits.

This verifier classifies those finite configurations and directly refutes the
full shared-parent Grassmann--Pluecker system for every color orbit with a
dependency-free deterministic CDCL checker.  It proves the stated conditional
obstruction.  It does not prove that an arbitrary hypothetical diagonal-two
counterexample must lie in the four-singleton regime.
"""

from __future__ import annotations

from itertools import combinations, permutations
import hashlib
import json

import search_higher_amalgam as sat
import verify_diag2_moving_witness_shear as moving


FORMAT = "diag2-singleton-four-gp-formula-v1"
NUMBER_VARIABLES = 70 + 2 * 56
EXPECTED_CONFIGURATIONS = 840
EXPECTED_COLORED_CONFIGURATIONS = 29_400
EXPECTED_COLOR_ORBIT_SIZES = (2_520, 6_720, 20_160)
EXPECTED_RELATIONS = 2_576
EXPECTED_CLAUSES = 34_112
GAUGE_PIVOTS = (0, 1, 2, 3, 4, 5, 15, 35, 70, 126)
REPRESENTATIVES = (
    ((3, 10, 26, 53), (19, 32, 36, 42)),
    ((3, 10, 42, 53), (19, 26, 32, 36)),
    ((3, 10, 36, 42), (19, 26, 32, 53)),
)
EXPECTED_FORMULA_DIGESTS = (
    "f69aa665307c55909c8c80790be1e29ee6d9bef857f69dbfc74d0a068fa44da6",
    "5502fd73fca593c1536d2fbffcab527c82546e3ccfd043fd979a8e8aea0e0999",
    "8a9f94cb13808bff3e18a3aa33c3ba762c98bc824c38fd329e1eae282190899a",
)
EXPECTED_SOLVER_STATS = (
    (2_344, 2_470, 2_343, 6),
    (1_098, 1_221, 1_097, 4),
    (762, 972, 761, 3),
)

TRIPLES = moving.TRIPLES
TRIPLE_INDEX = {triple: index for index, triple in enumerate(TRIPLES)}
BASES8 = sat.colex_subsets(8, 4)
BASE8_INDEX = {basis: index for index, basis in enumerate(BASES8)}
TRIPLE8_INDEX = {triple: index for index, triple in enumerate(TRIPLES)}


def edge_pair_mask(edge):
    answer = 0
    for left, right in combinations(TRIPLES[edge], 2):
        left, right = sorted((left - 1, right - 1))
        answer |= 1 << (8 * left + right)
    return answer


EDGE_PAIR_MASKS = tuple(edge_pair_mask(edge) for edge in range(56))
EDGES_AT_VERTEX = {
    vertex: tuple(edge for edge, triple in enumerate(TRIPLES) if vertex in triple)
    for vertex in range(1, 9)
}


def enumerate_configurations():
    """Enumerate every labeled linear 3-uniform 8_3 configuration once."""
    answer = []

    def visit(vertex, degrees, used_pairs, chosen):
        while vertex <= 8 and degrees[vertex - 1] == 3:
            vertex += 1
        if vertex == 9:
            if len(chosen) == 8:
                answer.append(tuple(sorted(chosen)))
            return

        needed = 3 - degrees[vertex - 1]
        candidates = [
            edge
            for edge in EDGES_AT_VERTEX[vertex]
            if edge not in chosen
            and not (EDGE_PAIR_MASKS[edge] & used_pairs)
            and all(degrees[label - 1] < 3 for label in TRIPLES[edge])
        ]
        for additions in combinations(candidates, needed):
            new_degrees = list(degrees)
            new_pairs = used_pairs
            valid = True
            for edge in additions:
                if EDGE_PAIR_MASKS[edge] & new_pairs:
                    valid = False
                    break
                new_pairs |= EDGE_PAIR_MASKS[edge]
                for label in TRIPLES[edge]:
                    new_degrees[label - 1] += 1
                    if new_degrees[label - 1] > 3:
                        valid = False
                        break
                if not valid:
                    break
            if valid and len(chosen) + len(additions) <= 8:
                visit(
                    vertex + 1,
                    new_degrees,
                    new_pairs,
                    chosen | set(additions),
                )

    visit(1, [0] * 8, 0, set())
    answer = tuple(sorted(set(answer)))
    if len(answer) != EXPECTED_CONFIGURATIONS:
        raise AssertionError("linear 8_3 configuration count changed")
    return answer


def transform_edges(edges, permutation):
    return tuple(
        sorted(
            TRIPLE_INDEX[
                tuple(sorted(permutation[label - 1] for label in TRIPLES[edge]))
            ]
            for edge in edges
        )
    )


def coloring(left, right):
    return tuple(sorted((tuple(sorted(left)), tuple(sorted(right)))))


def coloring_orbit(representative, permutations8):
    left, right = representative
    return {
        coloring(
            transform_edges(left, permutation),
            transform_edges(right, permutation),
        )
        for permutation in permutations8
    }


def classify_colorings(representatives):
    configurations = enumerate_configurations()
    all_colorings = set()
    for configuration in configurations:
        for left in combinations(configuration, 4):
            right = tuple(sorted(set(configuration) - set(left)))
            all_colorings.add(coloring(left, right))
    if len(all_colorings) != EXPECTED_COLORED_CONFIGURATIONS:
        raise AssertionError("colored linear 8_3 count changed")

    permutations8 = tuple(permutations(range(1, 9)))
    orbits = [coloring_orbit(representative, permutations8) for representative in representatives]
    sizes = tuple(sorted(len(orbit) for orbit in orbits))
    if sizes != EXPECTED_COLOR_ORBIT_SIZES:
        raise AssertionError("colored linear 8_3 orbit sizes changed")
    if any(orbits[i] & orbits[j] for i in range(3) for j in range(i)):
        raise AssertionError("colored linear 8_3 orbits overlap")
    if set().union(*orbits) != all_colorings:
        raise AssertionError("three color orbits do not exhaust the configurations")
    return configurations, orbits


def bracket_variable(basis, side):
    if 9 in basis:
        triple = tuple(label for label in basis if label != 9)
        return (70 + 56 * side + TRIPLE8_INDEX[triple],), 0
    return (BASE8_INDEX[basis],), 0


def compile_gp_relations(side):
    relations = []
    for lam in combinations(range(1, 10), 2):
        rest = [label for label in range(1, 10) if label not in lam]
        for a, b, c, d in combinations(rest, 4):
            terms = []
            for pairs, explicit_minus in (
                (((a, b), (c, d)), 0),
                (((a, c), (b, d)), 1),
                (((a, d), (b, c)), 0),
            ):
                variables = []
                constant = explicit_minus
                for left, right in pairs:
                    basis, parity = sat.parity_sort(lam + (left, right))
                    local_variables, local_constant = bracket_variable(basis, side)
                    variables.extend(local_variables)
                    constant ^= parity ^ local_constant
                variables = tuple(
                    sorted(
                        variable
                        for variable in set(variables)
                        if variables.count(variable) & 1
                    )
                )
                terms.append((variables, constant))
            relations.append(tuple(terms))
    if len(relations) != 1_260:
        raise AssertionError("wrong symbolic rank-four GP relation count")
    return tuple(relations)


GP_RELATIONS = compile_gp_relations(0) + compile_gp_relations(1)


def alpha_term(side, edge, source, target):
    replacement, sorting_sign = moving.replacement(edge, source, target)
    if replacement is None:
        raise AssertionError("mutation triple does not define this transport")
    return (
        tuple(sorted((70 + 56 * side + edge, 70 + 56 * side + replacement))),
        int(sorting_sign < 0),
    )


def compile_cover_relations(representative):
    left, right = representative
    relations = []
    for source in range(1, 9):
        for target in range(1, 9):
            if source == target:
                continue
            terms = []
            for side, edges in enumerate((left, right)):
                for edge in edges:
                    triple = TRIPLES[edge]
                    if source in triple and target not in triple:
                        terms.append(alpha_term(side, edge, source, target))
            if len(terms) not in (2, 3):
                raise AssertionError("linear 8_3 coloring has the wrong candidate count")
            if len(terms) == 2:
                # The generic three-term NAE compiler represents inequality
                # by repeating the second term.
                terms.append(terms[1])
            relations.append(tuple(terms))
    if len(relations) != 56:
        raise AssertionError("wrong singleton-cover relation count")
    return tuple(relations)


def compile_groups(representative):
    return GP_RELATIONS + compile_cover_relations(representative)


def variable_gauge_actions():
    """Return each bracket variable's old-label/new-label/global action."""
    answer = []
    for basis in BASES8:
        action = 1  # simultaneous global chirotope sign reversal
        for label in basis:
            action |= 1 << label
        answer.append(action)
    for side in range(2):
        for triple in TRIPLES:
            action = 1 | (1 << (9 + side))
            for label in triple:
                action |= 1 << label
            answer.append(action)
    if len(answer) != NUMBER_VARIABLES:
        raise AssertionError("wrong bracket gauge-action count")
    return tuple(answer)


GAUGE_ACTIONS = variable_gauge_actions()


def gf2_rank(rows):
    pivots = {}
    for row in rows:
        while row:
            pivot = row.bit_length() - 1
            if pivot in pivots:
                row ^= pivots[pivot]
            else:
                pivots[pivot] = row
                break
    return len(pivots)


def verify_gauge_invariance(relations):
    # Reorienting all eight old labels together is the same action as
    # reorienting both new elements, so the eleven displayed generators have
    # rank ten.  The selected coordinates meet every gauge orbit exactly once.
    if gf2_rank(GAUGE_ACTIONS) != 10:
        raise AssertionError("bracket gauge rank changed")
    if gf2_rank(GAUGE_ACTIONS[index] for index in GAUGE_PIVOTS) != 10:
        raise AssertionError("gauge-normalization coordinates lost full rank")
    for relation in relations:
        for generator in range(11):
            shifts = [
                sum((GAUGE_ACTIONS[variable] >> generator) & 1 for variable in values)
                & 1
                for values, _ in relation
            ]
            if shifts[0] != shifts[1] or shifts[1] != shifts[2]:
                raise AssertionError("GP/cover predicate is not gauge invariant")


def formula_digest(representative, clauses):
    digest = hashlib.sha256()
    digest.update(FORMAT.encode("ascii") + b"\0")
    payload = {
        "representative": representative,
        "relations": EXPECTED_RELATIONS,
        "variables": NUMBER_VARIABLES,
        "clauses": clauses,
    }
    digest.update(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    )
    return digest.hexdigest()


class ExactCDCL:
    """Small deterministic watched-literal CDCL checker.

    Learned clauses are first-UIP resolvents of an existing conflict and its
    recorded implication reasons.  Restarts and deletion of unlocked learned
    clauses change only search cost, never the represented formula.
    """

    def __init__(self, number_variables, initial_clauses, conflict_limit):
        self.number_variables = number_variables
        self.clauses = []
        self.active = []
        self.is_learned = []
        self.lbd = []
        self.watches = [[] for _ in range(2 * number_variables)]
        self.value = [0] * (number_variables + 1)
        self.level = [0] * (number_variables + 1)
        self.reason = [-1] * (number_variables + 1)
        self.phase = [1] * (number_variables + 1)
        self.trail = []
        self.trail_limits = []
        self.queue_head = 0
        self.units = []
        self.activity = [0.0] * (number_variables + 1)
        self.variable_increment = 1.0
        self.conflicts = 0
        self.decisions = 0
        self.restarts = 0
        self.conflict_limit = conflict_limit
        self.hit_limit = False
        self.seen = [False] * (number_variables + 1)
        self.touched = []
        self.initial_clause_count = len(initial_clauses)
        for clause in initial_clauses:
            self.add_clause(list(clause), learned=False)

    @staticmethod
    def literal_index(literal):
        return 2 * (abs(literal) - 1) + int(literal < 0)

    def literal_value(self, literal):
        value = self.value[abs(literal)]
        return value if literal > 0 else -value

    def add_clause(self, clause, *, learned=True, lbd=0):
        if not clause or any(
            type(literal) is not int
            or literal == 0
            or abs(literal) > self.number_variables
            for literal in clause
        ):
            raise AssertionError("CDCL received a malformed clause")
        if len({abs(literal) for literal in clause}) != len(clause):
            raise AssertionError("CDCL received a repeated-variable clause")
        clause_index = len(self.clauses)
        self.clauses.append(clause)
        self.active.append(True)
        self.is_learned.append(learned)
        self.lbd.append(lbd)
        for literal in clause:
            self.activity[abs(literal)] += 0.01 if learned else 1.0
        if len(clause) == 1:
            self.units.append(clause_index)
        else:
            self.watches[self.literal_index(clause[0])].append(clause_index)
            self.watches[self.literal_index(clause[1])].append(clause_index)
        return clause_index

    def enqueue(self, literal, reason):
        variable = abs(literal)
        wanted = 1 if literal > 0 else -1
        if self.value[variable]:
            return self.value[variable] == wanted
        self.value[variable] = wanted
        self.level[variable] = len(self.trail_limits)
        self.reason[variable] = reason
        self.phase[variable] = wanted
        self.trail.append(literal)
        return True

    def propagate(self):
        while self.queue_head < len(self.trail):
            false_literal = -self.trail[self.queue_head]
            self.queue_head += 1
            watched = self.watches[self.literal_index(false_literal)]
            read = write = 0
            while read < len(watched):
                clause_index = watched[read]
                read += 1
                if not self.active[clause_index]:
                    continue
                clause = self.clauses[clause_index]
                if clause[0] == false_literal:
                    clause[0], clause[1] = clause[1], clause[0]
                if clause[1] != false_literal:
                    raise AssertionError("watched-literal index is inconsistent")
                other = clause[0]
                if self.literal_value(other) > 0:
                    watched[write] = clause_index
                    write += 1
                    continue
                replacement = 0
                for position in range(2, len(clause)):
                    if self.literal_value(clause[position]) >= 0:
                        replacement = position
                        break
                if replacement:
                    clause[1], clause[replacement] = (
                        clause[replacement],
                        clause[1],
                    )
                    self.watches[self.literal_index(clause[1])].append(clause_index)
                    continue
                watched[write] = clause_index
                write += 1
                if self.literal_value(other) < 0:
                    watched[write:] = watched[read:]
                    return clause_index
                if not self.enqueue(other, clause_index):
                    watched[write:] = watched[read:]
                    return clause_index
            del watched[write:]
        return -1

    def analyze(self, conflict):
        learned = [0]
        current_level_paths = 0
        pivot_literal = 0
        trail_index = len(self.trail) - 1
        clause_index = conflict
        self.touched.clear()
        while True:
            for literal in self.clauses[clause_index]:
                variable = abs(literal)
                if (
                    variable == abs(pivot_literal)
                    or self.seen[variable]
                    or self.level[variable] == 0
                ):
                    continue
                self.seen[variable] = True
                self.touched.append(variable)
                self.activity[variable] += self.variable_increment
                if self.level[variable] == len(self.trail_limits):
                    current_level_paths += 1
                else:
                    learned.append(literal)
            while True:
                pivot_literal = self.trail[trail_index]
                trail_index -= 1
                if self.seen[abs(pivot_literal)]:
                    break
            self.seen[abs(pivot_literal)] = False
            current_level_paths -= 1
            if current_level_paths == 0:
                break
            clause_index = self.reason[abs(pivot_literal)]
            if clause_index < 0:
                raise AssertionError("conflict analysis crossed a decision")
        learned[0] = -pivot_literal
        if len(learned) > 1:
            second = max(
                range(1, len(learned)),
                key=lambda index: self.level[abs(learned[index])],
            )
            learned[1], learned[second] = learned[second], learned[1]
            backtrack = self.level[abs(learned[1])]
        else:
            backtrack = 0
        lbd = len({self.level[abs(literal)] for literal in learned})
        for variable in self.touched:
            self.seen[variable] = False
        self.variable_increment /= 0.95
        if self.variable_increment > 1e100:
            for variable in range(1, self.number_variables + 1):
                self.activity[variable] *= 1e-100
            self.variable_increment *= 1e-100
        return learned, backtrack, lbd

    def cancel_until(self, target_level):
        if len(self.trail_limits) <= target_level:
            return
        start = self.trail_limits[target_level]
        for literal in reversed(self.trail[start:]):
            variable = abs(literal)
            self.value[variable] = 0
            self.level[variable] = 0
            self.reason[variable] = -1
        del self.trail[start:]
        del self.trail_limits[target_level:]
        self.queue_head = len(self.trail)

    def reduce_database(self):
        locked = {reason for reason in self.reason if reason >= 0}
        candidates = [
            clause_index
            for clause_index, clause in enumerate(self.clauses)
            if self.active[clause_index]
            and self.is_learned[clause_index]
            and clause_index not in locked
            and len(clause) > 3
        ]
        candidates.sort(
            key=lambda index: (
                self.lbd[index],
                len(self.clauses[index]),
                index,
            ),
            reverse=True,
        )
        for clause_index in candidates[: len(candidates) // 2]:
            self.active[clause_index] = False

    def decide(self):
        candidates = [
            variable
            for variable in range(1, self.number_variables + 1)
            if not self.value[variable]
        ]
        if not candidates:
            return False
        variable = max(
            candidates,
            key=lambda item: (self.activity[item], -item),
        )
        self.trail_limits.append(len(self.trail))
        self.decisions += 1
        literal = variable if self.phase[variable] > 0 else -variable
        if not self.enqueue(literal, -1):
            raise AssertionError("decision contradicted an unassigned variable")
        return True

    def solve(self):
        for clause_index in self.units:
            if not self.enqueue(self.clauses[clause_index][0], clause_index):
                return False
        if self.propagate() >= 0:
            return False
        restart_limit = 100
        conflicts_since_restart = 0
        while True:
            conflict = self.propagate()
            if conflict >= 0:
                self.conflicts += 1
                conflicts_since_restart += 1
                if self.conflicts > self.conflict_limit:
                    self.hit_limit = True
                    return None
                if not self.trail_limits:
                    return False
                learned, backtrack, lbd = self.analyze(conflict)
                self.cancel_until(backtrack)
                if self.literal_value(learned[0]) != 0 or any(
                    self.literal_value(literal) >= 0 for literal in learned[1:]
                ):
                    raise AssertionError("learned clause is not asserting")
                clause_index = self.add_clause(learned, lbd=lbd)
                if not self.enqueue(learned[0], clause_index):
                    raise AssertionError("asserting clause did not propagate")
                if conflicts_since_restart >= restart_limit:
                    self.cancel_until(0)
                    self.restarts += 1
                    conflicts_since_restart = 0
                    restart_limit = int(restart_limit * 1.5) + 1
                if self.conflicts % 5_000 == 0:
                    self.cancel_until(0)
                    self.reduce_database()
            elif not self.decide():
                return tuple(
                    self.value[variable] > 0
                    for variable in range(1, self.number_variables + 1)
                )

    @property
    def learned_clauses(self):
        return len(self.clauses) - self.initial_clause_count


def replay_orbit(orbit_index, representative):
    representative = coloring(*representative)
    if representative != REPRESENTATIVES[orbit_index]:
        raise AssertionError("singleton-four representative is not canonical")
    relations = compile_groups(representative)
    if len(relations) != EXPECTED_RELATIONS:
        raise AssertionError("wrong combined GP/cover relation count")
    verify_gauge_invariance(relations)
    compiled = sat.relations_to_cnf(NUMBER_VARIABLES, relations)
    if compiled is None:
        raise AssertionError("singleton-four formula contains an empty predicate")
    clauses, _ = compiled
    if len(clauses) != EXPECTED_CLAUSES:
        raise AssertionError("singleton-four CNF clause count changed")
    digest = formula_digest(representative, clauses)
    expected_digest = EXPECTED_FORMULA_DIGESTS[orbit_index]
    if expected_digest is not None and digest != expected_digest:
        raise AssertionError("singleton-four formula digest changed")

    normalized = list(clauses) + [(-(variable + 1),) for variable in GAUGE_PIVOTS]
    expected = EXPECTED_SOLVER_STATS[orbit_index]
    solver = ExactCDCL(
        NUMBER_VARIABLES,
        normalized,
        conflict_limit=expected[0],
    )
    answer = solver.solve()
    if answer is not False or solver.hit_limit:
        if type(answer) is tuple and not all(
            any((literal > 0) == answer[abs(literal) - 1] for literal in clause)
            for clause in normalized
        ):
            raise AssertionError("CDCL returned an invalid satisfying assignment")
        raise AssertionError(f"singleton-four orbit {orbit_index} is not UNSAT")
    actual = (
        solver.conflicts,
        solver.decisions,
        solver.learned_clauses,
        solver.restarts,
    )
    if actual != expected:
        raise AssertionError("singleton-four deterministic CDCL trace changed")
    return representative, digest, actual


def main():
    representatives = tuple(coloring(*representative) for representative in REPRESENTATIVES)
    configurations, orbits = classify_colorings(representatives)
    print(
        "PASS classified",
        len(configurations),
        "labeled linear 8_3 configurations into color-orbit sizes",
        tuple(sorted(len(orbit) for orbit in orbits)),
    )
    for orbit_index, representative in enumerate(representatives):
        representative, digest, stats = replay_orbit(orbit_index, representative)
        print(
            "PASS color orbit",
            orbit_index,
            "representative",
            representative,
            "full formula UNSAT clauses",
            EXPECTED_CLAUSES,
            "digest",
            digest,
            "CDCL conflicts/decisions/learned/restarts",
            stats,
        )
    print("THEOREM no four-singleton minimal-separator pair has disjoint escapes")
    print("SCOPE conditional four-singleton regime; diagonal two remains open")


if __name__ == "__main__":
    main()
