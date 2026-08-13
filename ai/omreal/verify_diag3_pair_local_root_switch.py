#!/usr/bin/env python3
"""Exact local ordered-root switch theorem for diagonal three.

For each of the thirteen nonstructural residual-wall incidence types, let P
be its active positive circuit support (four rows at an ordinary wall and
three rows at a localization wall).  For an arbitrary 56-bit signing sigma,
this verifier builds the graph whose vertices are the 112 oriented elementary
roots compatible with the selected P witness.  Two distinct root lines are
adjacent when at least one order of the two shears keeps every row of P in the
sigma-orthant under the full inverse third-exterior transport, including the
bilinear u*v term.

Connectivity is proved by contradiction.  A dependency-free exact CDCL
solver rejects a Boolean formula containing a nontrivial cut with no safe
ordered edge across it.  The universal phase uses no parent chirotope,
Grassmann--Pluecker, residual-chamber, or realizability assumption.

An optional slower audit reconstructs the thirteen canonical exact wall
points and checks the graph directly on every GP-valid extension signing for
which P is positive.  It is independent evidence, not the universal proof.
"""

from __future__ import annotations

import argparse
from collections import defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass
import hashlib
from itertools import combinations

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled
import DIAG9_GRAPH_exact_topes as exact_topes
import four_chart_gate as gate
import verify_diag2_canonical_robust_edges as robust
import verify_diag2_generic_birth_pattern_reduction as reduction
import verify_diag2_moving_witness_shear as moving
import verify_diag2_singleton_four_obstruction as singleton
import verify_diag2_escape_set_topes as escape
import verify_diag3_ordered_root_atlas178 as atlas_ordered


CANONICAL_KINDS = robust.CANONICAL_KINDS
FORMAT = "diag3-pair-local-root-switch-v1"

# Filled from the first complete exact replay.  Types 46 and 47 deliberately
# have the same active three-circuit and therefore the same universal formula.
EXPECTED_FORMULAS = {
    # kind: (variables, clauses, xor variables, conflicts, SHA-256)
    36: (12_956, 60_546, 132, 388, "098bf20e3cccd336ba6cb9119054040603d312ede40f197e59e06c20bae9e43e"),
    37: (13_000, 68_114, 176, 464, "7522cb2fbbb50fe2c9b41276086c12ff3d8cd97cfdc353ab83b359a0359d96c3"),
    38: (13_001, 68_094, 177, 382, "285412e82b10e8d9e71bcd3d898f007c1fc3cfb72ad61655645ef871a017b1a4"),
    39: (12_956, 60_546, 132, 348, "169bb13c074b24a5f03914b3d37bc1951c71de4a4349202068a9b90be6f60614"),
    41: (13_000, 68_118, 176, 387, "d126b7344a40ffac470cc6e2108eb1ebec301c020bf223c4a976b6b5dc0c2be2"),
    42: (13_001, 68_098, 177, 464, "eb2ae5bba5da10f873b97f5addf598b31f6772aba67ef97ea8183871caa4dd81"),
    44: (13_001, 68_102, 177, 419, "389941db37ed671a04ea73b0a8af4ba9747fb3382cc0397e63f96649aa0da797"),
    46: (12_956, 60_546, 132, 375, "4f1ed464f9f86d5229cd5ffd82c5d8c00fedc9e27de3bc9d16d2b4b04d9a541f"),
    47: (12_956, 60_546, 132, 375, "4f1ed464f9f86d5229cd5ffd82c5d8c00fedc9e27de3bc9d16d2b4b04d9a541f"),
    48: (12_998, 68_130, 174, 397, "0daf61ad1603369c8c02cd11aaa73c8b9d36d1a24eaac78cf6a7f32dfd1f2bf3"),
    49: (12_999, 68_118, 175, 406, "ecd2b6e5913ab18f1df576c72cea7aca1f20baeee31836ce15f26ac9ed4edbac"),
    50: (13_000, 68_102, 176, 638, "1d660d5545926f3604bcb03904572b9a795990663953f4b6734f9546095a16cd"),
    51: (13_000, 68_106, 176, 425, "ba10480b38acabee9d5c632b27145dea3fde4593d810f11aa997adcc3abbcf42"),
}

EXPECTED_CANONICAL_COUNTS = {
    36: 1_426,
    37: 112,
    38: 370,
    39: 1_222,
    41: 80,
    42: 738,
    44: 340,
    46: 2_240,
    47: 2_224,
    48: 148,
    49: 818,
    50: 216,
    51: 314,
}
EXPECTED_CANONICAL_TOTAL = 10_248
EXPECTED_CANONICAL_DIGESTS = {
    36: "fe8cdf101ab03f9585c8b2b81db5096ca2a4ffa1ff7461fd4b20c1c6d0ceb635",
    37: "ac490e880baff6ab9ad74c777a672d9843b24f86e8ea9c6251dd92e396f5619e",
    38: "3dd8b7c3f2844ff57bd5a51951c9949c9502a8e9f58ca98251f617408251a12b",
    39: "3332f473f0552317051344ae8a9a39a3c699d38cdff24aa1a8e881d14933b3ac",
    41: "48e4cce040761ff5d377ac1f6d537e509b31609a1419cc4ce8711926a13bff19",
    42: "230f6011866c6c3765226ec03137e8b59e64c4b42fe3fe41db840e6444fa3105",
    44: "94ca1f0b0adb769a6520d3a466220843b46bc8c6cc31defad36f893d713eaf1b",
    46: "d0562dec67683e7541534aa2eea857e273384637ab4050b9477fe1e821be588a",
    47: "333c9e7ad743280d92a1ebcaf160a9e2afecc9d5c4516e696b8ad20283a7aa0b",
    48: "777e892fa8256305fa8dbebb54d42a63503c0d021c257daeb4b22c8d3f900789",
    49: "1b0d90e5939f2c5daf3a2d6a7f6c9e9493528d43b053d1aca68b71232f411ff6",
    50: "f4319bb99f5ad156781e5b27106349f35ec49f7521f6d58f892a77fccea93b32",
    51: "36cee25672fb53bc2e338ac31f44426acd1e0a88375402deadf2316ca8ceb537",
}


def active_support(kind):
    """Return the exact active small circuit, omitting localization padding."""

    if kind in reduction.LOCALIZATION_SEEDS:
        return reduction.parse_support(reduction.LOCALIZATION_SEEDS[kind][0])
    return labeled.occurrence_representatives()[kind]


def support_text(support):
    return "/".join(
        "".join(map(str, moving.TRIPLES[index])) for index in support
    )


def source_count_vertex_bound(support):
    """Universal lower bound from the 15 source-target incidences per row."""

    counts = []
    for source in range(1, 9):
        for target in range(1, 9):
            if source == target:
                continue
            counts.append(
                sum(
                    source in moving.TRIPLES[row]
                    and target not in moving.TRIPLES[row]
                    for row in support
                )
            )
    if len(counts) != 56 or sum(counts) != 15 * len(support):
        raise AssertionError("wrong source-target incidence count")
    # m=0 supplies both orientations, m=1 supplies its forced orientation,
    # and m>=2 is conservatively allowed to supply none.
    direct = 2 * counts.count(0) + counts.count(1)
    bound = 112 - 15 * len(support)
    if direct < bound:
        raise AssertionError("source-count vertex bound failed")
    return bound


def transformed_basis(label, first, second):
    """Expand g^-1 e_label for two ordered signed elementary shears."""

    terms = [(label, 0, 0, 1)]
    for (u_degree, v_degree), direction in (
        ((1, 0), first),
        ((0, 1), second),
    ):
        source, target, parameter_sign = direction
        expanded = list(terms)
        for current, old_u, old_v, coefficient in terms:
            if current == source:
                expanded.append(
                    (
                        target,
                        old_u + u_degree,
                        old_v + v_degree,
                        -parameter_sign * coefficient,
                    )
                )
        terms = expanded
    return tuple(terms)


def row_order_constraints(row, first, second):
    """XOR conditions making one row safe under the complete two-root order.

    A condition ``(i,j,c)`` means ``sigma_i XOR sigma_j = c``, with ``+``
    encoded by one.  ``None`` denotes an impossible order.
    """

    coefficients = {}
    factors = [
        transformed_basis(label, first, second)
        for label in moving.TRIPLES[row]
    ]
    for left in factors[0]:
        for middle in factors[1]:
            for right in factors[2]:
                sequence = (left[0], middle[0], right[0])
                if len(set(sequence)) != 3:
                    continue
                target = moving.TRIPLE_INDEX[tuple(sorted(sequence))]
                monomial = (
                    left[1] + middle[1] + right[1],
                    left[2] + middle[2] + right[2],
                )
                coefficient = (
                    left[3]
                    * middle[3]
                    * right[3]
                    * moving.orientation_sign(sequence)
                )
                key = (target, monomial)
                coefficients[key] = coefficients.get(key, 0) + coefficient

    constraints = []
    for (target, monomial), coefficient in coefficients.items():
        if monomial == (0, 0) or coefficient == 0:
            continue
        if target == row:
            if coefficient < 0:
                return None
            continue
        constraints.append((row, target, int(coefficient < 0)))
    return tuple(constraints)


def normalize_constraints(constraints):
    """Canonicalize XOR equations and detect contradictory duplicates."""

    equations = {}
    for left, right, constant in constraints:
        if left > right:
            left, right = right, left
        if left == right:
            if constant:
                return None
            continue
        previous = equations.setdefault((left, right), constant)
        if previous != constant:
            return None
    return tuple(
        (left, right, equations[left, right]) for left, right in sorted(equations)
    )


def compatibility_constraints(support, direction):
    """XOR conditions for one oriented root to transport the P witness."""

    source, target, parameter_sign = direction
    constraints = []
    for row in support:
        replacement = moving.replacement(row, source, target)
        if replacement is None:
            continue
        new_row, sorting_sign = replacement
        # -sorting_sign * sigma_row * sigma_new_row = parameter_sign.
        constraints.append(
            (row, new_row, int((-parameter_sign * sorting_sign) < 0))
        )
    answer = normalize_constraints(constraints)
    if answer is None:
        raise AssertionError("one-root compatibility constraints contradicted")
    return answer


def ordered_constraints(support, first, second):
    constraints = []
    for row in support:
        local = row_order_constraints(row, first, second)
        if local is None:
            return None
        constraints.extend(local)
    return normalize_constraints(constraints)


def constraints_hold(signature, constraints):
    if constraints is None:
        return False
    return all(
        (((signature >> left) ^ (signature >> right)) & 1) == constant
        for left, right, constant in constraints
    )


def vertex_mask_for_support(signature, support):
    answer = 0
    for index, direction in enumerate(escape.DIRECTIONS):
        if constraints_hold(
            signature, compatibility_constraints(support, direction)
        ):
            answer |= 1 << index
    return answer


@dataclass
class RootPredicates:
    support: tuple[int, ...]
    compatibility: tuple[tuple[tuple[int, int, int], ...], ...]
    ordered: dict[tuple[int, int], tuple[tuple[int, int, int], ...] | None]

    @classmethod
    def build(cls, support):
        support = tuple(support)
        compatibility = tuple(
            compatibility_constraints(support, direction)
            for direction in escape.DIRECTIONS
        )
        ordered = {}
        for first_index, first in enumerate(escape.DIRECTIONS):
            for second_index, second in enumerate(escape.DIRECTIONS):
                if first_index == second_index or first[:2] == second[:2]:
                    continue
                ordered[first_index, second_index] = ordered_constraints(
                    support, first, second
                )
        return cls(support, compatibility, ordered)

    def vertex_mask(self, signature):
        answer = 0
        for index, constraints in enumerate(self.compatibility):
            if constraints_hold(signature, constraints):
                answer |= 1 << index
        return answer

    def edge(self, signature, left, right):
        if escape.DIRECTIONS[left][:2] == escape.DIRECTIONS[right][:2]:
            return False
        return constraints_hold(signature, self.ordered[left, right]) or constraints_hold(
            signature, self.ordered[right, left]
        )


class CNFBuilder:
    """Small deterministic Tseitin compiler with zero-based variables."""

    def __init__(self):
        self.number_variables = 56
        self.clauses = []
        self.xor_variables = {}

    def new_variable(self):
        variable = self.number_variables
        self.number_variables += 1
        return variable

    def add_clause(self, *literals):
        self.clauses.append(tuple(literals))

    def xor_variable(self, left, right):
        if left > right:
            left, right = right, left
        if left == right:
            raise AssertionError("diagonal XOR does not need a variable")
        key = (left, right)
        if key in self.xor_variables:
            return self.xor_variables[key]
        result = self.new_variable()
        self.xor_variables[key] = result
        a, b, q = left + 1, right + 1, result + 1
        # q <=> a XOR b.
        self.add_clause(-q, a, b)
        self.add_clause(-q, -a, -b)
        self.add_clause(q, -a, b)
        self.add_clause(q, a, -b)
        return result

    def condition_literal(self, left, right, constant):
        if left == right:
            return None if constant else 0
        variable = self.xor_variable(left, right) + 1
        return variable if constant else -variable

    def and_variable(self, constraints):
        if constraints is None:
            result = self.new_variable()
            self.add_clause(-(result + 1))
            return result
        literals = []
        for left, right, constant in constraints:
            literal = self.condition_literal(left, right, constant)
            if literal is None:
                result = self.new_variable()
                self.add_clause(-(result + 1))
                return result
            if literal:
                literals.append(literal)
        if any(-literal in literals for literal in literals):
            result = self.new_variable()
            self.add_clause(-(result + 1))
            return result
        literals = tuple(sorted(set(literals), key=lambda item: (abs(item), item)))
        result = self.new_variable()
        q = result + 1
        if not literals:
            self.add_clause(q)
        else:
            for literal in literals:
                self.add_clause(-q, literal)
            self.add_clause(q, *(-literal for literal in literals))
        return result


def disconnected_cut_formula(support, include_edges=True):
    """Compile existence of a nontrivial union of graph components."""

    predicates = RootPredicates.build(support)
    builder = CNFBuilder()
    compatible = tuple(
        builder.and_variable(constraints)
        for constraints in predicates.compatibility
    )
    cut = tuple(builder.new_variable() for _ in escape.DIRECTIONS)

    if include_edges:
        for left in range(len(escape.DIRECTIONS)):
            for right in range(left + 1, len(escape.DIRECTIONS)):
                if escape.DIRECTIONS[left][:2] == escape.DIRECTIONS[right][:2]:
                    continue
                for order in ((left, right), (right, left)):
                    safe = builder.and_variable(predicates.ordered[order]) + 1
                    c_left = compatible[left] + 1
                    c_right = compatible[right] + 1
                    x_left = cut[left] + 1
                    x_right = cut[right] + 1
                    # A safe edge between two graph vertices cannot cross the cut.
                    builder.add_clause(
                        -safe, -c_left, -c_right, -x_left, x_right
                    )
                    builder.add_clause(
                        -safe, -c_left, -c_right, x_left, -x_right
                    )

    side_zero = []
    side_one = []
    for root in range(len(escape.DIRECTIONS)):
        compatible_literal = compatible[root] + 1
        cut_literal = cut[root] + 1
        zero = builder.new_variable() + 1
        one = builder.new_variable() + 1
        # zero <=> compatible AND NOT cut.
        builder.add_clause(-zero, compatible_literal)
        builder.add_clause(-zero, -cut_literal)
        builder.add_clause(zero, -compatible_literal, cut_literal)
        # one <=> compatible AND cut.
        builder.add_clause(-one, compatible_literal)
        builder.add_clause(-one, cut_literal)
        builder.add_clause(one, -compatible_literal, -cut_literal)
        side_zero.append(zero)
        side_one.append(one)
    builder.add_clause(*side_zero)
    builder.add_clause(*side_one)

    clauses = tuple(
        sorted(set(builder.clauses), key=lambda clause: (len(clause), clause))
    )
    return predicates, builder, clauses


def formula_digest(number_variables, clauses):
    digest = hashlib.sha256()
    digest.update(FORMAT.encode("ascii") + b"\0")
    digest.update(int(number_variables).to_bytes(4, "little"))
    for clause in clauses:
        digest.update(len(clause).to_bytes(2, "little"))
        for literal in clause:
            digest.update(int(literal).to_bytes(4, "little", signed=True))
    return digest.hexdigest()


def verify_predicate_canaries(predicates):
    """Cross-check the symbolic compiler against direct exterior expansion."""

    for sample in range(16):
        payload = hashlib.sha256(
            f"diag3-local-root-switch-canary:{support_text(predicates.support)}:{sample}".encode(
                "ascii"
            )
        ).digest()
        signature = int.from_bytes(payload[:7], "little")
        symbolic_mask = predicates.vertex_mask(signature)
        direct_mask = 0
        for index, (source, target, parameter_sign) in enumerate(escape.DIRECTIONS):
            values = tuple(
                moving.transport_alpha(signature, row, source, target)
                for row in predicates.support
                if moving.replacement(row, source, target) is not None
            )
            if not values or (len(set(values)) == 1 and values[0] == parameter_sign):
                direct_mask |= 1 << index
        if symbolic_mask != direct_mask:
            raise AssertionError("symbolic one-root predicate disagrees with direct signs")

        vertices = tuple(
            index for index in range(len(escape.DIRECTIONS))
            if (symbolic_mask >> index) & 1
        )
        checked_edges = 0
        for offset, left in enumerate(vertices):
            for right in vertices[offset + 1 :]:
                symbolic = predicates.edge(signature, left, right)
                support_mask = sum(1 << row for row in predicates.support)
                first = escape.DIRECTIONS[left]
                second = escape.DIRECTIONS[right]
                direct = (
                    first[:2] != second[:2]
                    and (
                        support_mask
                        & ~atlas_ordered.safe_rows(signature, first, second)
                        == 0
                        or support_mask
                        & ~atlas_ordered.safe_rows(signature, second, first)
                        == 0
                    )
                )
                if symbolic != direct:
                    raise AssertionError("symbolic ordered edge predicate changed")
                checked_edges += 1
                if checked_edges == 64:
                    break
            if checked_edges == 64:
                break
        if checked_edges != 64:
            raise AssertionError("too few ordered-edge predicate canaries")


def universal_audit(kind):
    support = active_support(kind)
    vertex_bound = source_count_vertex_bound(support)
    predicates, builder, clauses = disconnected_cut_formula(support)
    verify_predicate_canaries(predicates)
    digest = formula_digest(builder.number_variables, clauses)
    expected = EXPECTED_FORMULAS.get(kind)
    if expected is not None:
        expected_variables, expected_clauses, expected_xors, _, expected_digest = expected
        actual = (
            builder.number_variables,
            len(clauses),
            len(builder.xor_variables),
            digest,
        )
        if actual != (
            expected_variables,
            expected_clauses,
            expected_xors,
            expected_digest,
        ):
            raise AssertionError(f"type {kind}: universal formula changed: {actual}")

    conflict_limit = expected[3] if expected is not None else 2_000_000
    solver = singleton.ExactCDCL(
        builder.number_variables,
        clauses,
        conflict_limit=conflict_limit,
    )
    answer = solver.solve()
    if answer is None:
        raise AssertionError(f"type {kind}: exact CDCL hit its conflict limit")
    if answer is not False:
        signature = sum(
            1 << index for index in range(56) if answer[index]
        )
        raise AssertionError(
            f"type {kind}: disconnected root graph at signing {signature}"
        )
    if expected is not None and solver.conflicts != expected[3]:
        raise AssertionError(
            f"type {kind}: conflict count changed: {solver.conflicts}"
        )
    return {
        "kind": kind,
        "support": support_text(support),
        "vertex_bound": vertex_bound,
        "variables": builder.number_variables,
        "clauses": len(clauses),
        "xors": len(builder.xor_variables),
        "conflicts": solver.conflicts,
        "digest": digest,
    }


def determinant_relation(columns):
    """Return a nonzero circuit relation on three, four, or five 4-vectors."""

    size = len(columns)
    for coordinates in combinations(range(4), size - 1):
        relation = []
        for omitted in range(size):
            selected = [
                columns[index]
                for index in range(size)
                if index != omitted
            ]
            if size - 1 == 2:
                left, right = selected
                value = (
                    left[coordinates[0]] * right[coordinates[1]]
                    - left[coordinates[1]] * right[coordinates[0]]
                )
            elif size - 1 == 3:
                rows = [
                    tuple(vector[coordinate] for coordinate in coordinates)
                    for vector in selected
                ]
                value = moving.det3(*rows)
            elif size - 1 == 4:
                value = moving.det4(*selected)
            else:
                raise AssertionError("circuit must have size three, four, or five")
            relation.append((-1 if omitted & 1 else 1) * value)
        if any(relation):
            if any(
                sum(
                    relation[index] * columns[index][coordinate]
                    for index in range(size)
                )
                for coordinate in range(4)
            ):
                raise AssertionError("cofactor vector is not a dependence")
            return tuple(relation)
    raise AssertionError("active wall support has rank below circuit rank")


def positive_circuit_signing(signature, support, normals):
    relation = determinant_relation(tuple(normals[index] for index in support))
    if not all(relation):
        return False
    twisted = tuple(
        coefficient * moving.signature_sign(signature, row)
        for coefficient, row in zip(relation, support, strict=True)
    )
    return all(value > 0 for value in twisted) or all(
        value < 0 for value in twisted
    )


def positive_wall_signing(signature, support, normals):
    if not positive_circuit_signing(signature, support, normals):
        return False
    relation = determinant_relation(tuple(normals[index] for index in support))
    if not all(relation):
        raise AssertionError("canonical active wall circuit has a zero coefficient")
    return True


def graph_record(predicates, signature):
    vertex_mask = predicates.vertex_mask(signature)
    vertices = tuple(
        index for index in range(len(escape.DIRECTIONS))
        if (vertex_mask >> index) & 1
    )
    adjacency = {vertex: set() for vertex in vertices}
    edge_count = 0
    for offset, left in enumerate(vertices):
        for right in vertices[offset + 1 :]:
            if predicates.edge(signature, left, right):
                adjacency[left].add(right)
                adjacency[right].add(left)
                edge_count += 1
    remaining = set(vertices)
    components = 0
    while remaining:
        components += 1
        stack = [next(iter(remaining))]
        while stack:
            current = stack.pop()
            if current not in remaining:
                continue
            remaining.remove(current)
            stack.extend(adjacency[current] & remaining)
    return vertex_mask, edge_count, components


def canonical_audit(kind):
    factor_ids, factor_polynomials = robust.canonical_data()
    witness = robust.construct_witness(kind, factor_ids, factor_polynomials)
    support = active_support(kind)
    normals = exact_topes.derived_rows(
        robust.integer_matrix(witness.center), normalize=False
    )
    if not all(
        determinant_relation(tuple(normals[index] for index in support))
    ):
        raise AssertionError("canonical active wall circuit has a zero coefficient")
    _, signatures = gate.enumerate_extensions(witness.parent)
    signatures = tuple(
        int(signature)
        for signature in signatures
        if positive_wall_signing(int(signature), support, normals)
    )
    expected_count = EXPECTED_CANONICAL_COUNTS[kind]
    if len(signatures) != expected_count:
        raise AssertionError(
            f"type {kind}: canonical positive-signing count changed: {len(signatures)}"
        )

    predicates = RootPredicates.build(support)
    digest = hashlib.sha256()
    digest.update(b"diag3-pair-local-root-switch-canonical-v1\0")
    digest.update(int(kind).to_bytes(2, "little"))
    minimum_vertices = 113
    minimum_edges = None
    for signature in signatures:
        vertex_mask, edge_count, components = graph_record(predicates, signature)
        if components != 1:
            raise AssertionError(
                f"type {kind}: canonical signing {signature} has {components} components"
            )
        minimum_vertices = min(minimum_vertices, vertex_mask.bit_count())
        minimum_edges = edge_count if minimum_edges is None else min(
            minimum_edges, edge_count
        )
        digest.update(int(signature).to_bytes(8, "little"))
        digest.update(int(vertex_mask).to_bytes(16, "little"))
        digest.update(int(edge_count).to_bytes(2, "little"))
    semantic = digest.hexdigest()
    expected_digest = EXPECTED_CANONICAL_DIGESTS.get(kind)
    if expected_digest is not None and semantic != expected_digest:
        raise AssertionError(
            f"type {kind}: canonical semantic digest changed: {semantic}"
        )
    return {
        "kind": kind,
        "signatures": len(signatures),
        "minimum_vertices": minimum_vertices,
        "minimum_edges": minimum_edges,
        "digest": semantic,
    }


def same_root_loss_canary():
    """Replay the exact type-37 example showing why a root switch is needed."""

    kind = 37
    signature = 70_109_424_330_912_456
    factor_ids, factor_polynomials = robust.canonical_data()
    witness = robust.construct_witness(kind, factor_ids, factor_polynomials)
    normals_left, normals_center, normals_right = (
        exact_topes.derived_rows(robust.integer_matrix(point), normalize=False)
        for point in (witness.left, witness.center, witness.right)
    )
    _, signatures = gate.enumerate_extensions(witness.parent)
    if signature not in set(map(int, signatures)):
        raise AssertionError("same-root-loss signing is no longer GP-valid")

    wall = active_support(kind)
    incoming = reduction.parse_support("123/124/134/345/567")
    outgoing = reduction.parse_support("123/124/345/567/148")
    persistent = reduction.parse_support("123/134/345/567/148")
    if not positive_circuit_signing(signature, wall, normals_center):
        raise AssertionError("same-root-loss wall circuit is not positive")
    if not positive_circuit_signing(signature, incoming, normals_left):
        raise AssertionError("same-root-loss incoming circuit is not positive")
    if not positive_circuit_signing(signature, outgoing, normals_right):
        raise AssertionError("same-root-loss outgoing circuit is not positive")
    if not all(
        positive_circuit_signing(signature, persistent, normals)
        for normals in (normals_left, normals_center, normals_right)
    ):
        raise AssertionError("same-root-loss persistent circuit stopped persisting")

    masks = tuple(
        vertex_mask_for_support(signature, support)
        for support in (incoming, outgoing, persistent)
    )
    lost = masks[0] & ~(masks[1] | masks[2])
    common = masks[0] & (masks[1] | masks[2])
    first = (lost & -lost).bit_length() - 1
    if (
        tuple(mask.bit_count() for mask in masks) != (55, 52, 51)
        or lost.bit_count() != 7
        or common.bit_count() != 48
        or escape.DIRECTIONS[first] != (1, 2, 1)
    ):
        raise AssertionError("same-root-loss mask census changed")
    if graph_record(RootPredicates.build(wall), signature)[2] != 1:
        raise AssertionError("same-root-loss wall graph is disconnected")
    return {
        "signature": signature,
        "incoming": masks[0].bit_count(),
        "outgoing": masks[1].bit_count(),
        "persistent": masks[2].bit_count(),
        "lost": lost.bit_count(),
        "common": common.bit_count(),
        "first": escape.DIRECTIONS[first],
    }


def disconnected_cut_canary():
    """Deleting every graph edge must make the nontrivial-cut formula SAT."""

    support = active_support(37)
    _, builder, clauses = disconnected_cut_formula(support, include_edges=False)
    solver = singleton.ExactCDCL(
        builder.number_variables, clauses, conflict_limit=100
    )
    answer = solver.solve()
    if answer is None or answer is False:
        raise AssertionError("disconnected-cut canary was not satisfiable")


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--types",
        nargs="+",
        type=int,
        help="selected incidence types (default: all thirteen)",
    )
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--canonical-audit",
        action="store_true",
        help="also replay all GP-valid P-positive signings at the exact canonical walls",
    )
    return parser.parse_args()


def run_parallel(worker, kinds, workers):
    if workers == 1 or len(kinds) == 1:
        return [worker(kind) for kind in kinds]
    records = []
    with ProcessPoolExecutor(max_workers=min(workers, len(kinds))) as executor:
        futures = {executor.submit(worker, kind): kind for kind in kinds}
        for future in as_completed(futures):
            records.append(future.result())
    return sorted(records, key=lambda record: record["kind"])


def main():
    args = parse_args()
    kinds = CANONICAL_KINDS if args.types is None else tuple(args.types)
    if (
        not kinds
        or len(set(kinds)) != len(kinds)
        or any(kind not in CANONICAL_KINDS for kind in kinds)
    ):
        raise ValueError(f"types must be distinct members of {CANONICAL_KINDS}")
    if args.workers < 1:
        raise ValueError("--workers must be positive")

    disconnected_cut_canary()
    universal = run_parallel(universal_audit, kinds, args.workers)
    for record in universal:
        print(
            "UNSAT type",
            record["kind"],
            "support",
            record["support"],
            "vars",
            record["variables"],
            "clauses",
            record["clauses"],
            "xors",
            record["xors"],
            "conflicts",
            record["conflicts"],
            "vertex-bound",
            record["vertex_bound"],
        )
        print("FORMULA_DIGEST type-" + str(record["kind"]), record["digest"])
    print(
        "THEOREM all",
        len(kinds),
        "wall incidences have connected ordered-root graphs for every 56-bit signing",
    )
    print("SCOPE universal sign-combinatorial UNSAT proof; no chart sampling")

    if args.canonical_audit:
        canary = same_root_loss_canary()
        print(
            "SAME_ROOT_LOSS",
            canary["signature"],
            "masks",
            canary["incoming"],
            canary["outgoing"],
            canary["persistent"],
            "lost",
            canary["lost"],
            "common",
            canary["common"],
            "first",
            canary["first"],
        )
        canonical = run_parallel(canonical_audit, kinds, args.workers)
        total = sum(record["signatures"] for record in canonical)
        for record in canonical:
            print(
                "CANONICAL type",
                record["kind"],
                "signatures",
                record["signatures"],
                "min-vertices",
                record["minimum_vertices"],
                "min-edges",
                record["minimum_edges"],
            )
            print(
                "CANONICAL_DIGEST type-" + str(record["kind"]),
                record["digest"],
            )
        if kinds == CANONICAL_KINDS and total != EXPECTED_CANONICAL_TOTAL:
            raise AssertionError("canonical positive-signing total changed")
        print(
            "AUDIT",
            total,
            "GP-valid P-positive canonical-wall signings have connected graphs",
        )
        print("SCOPE optional exact-wall regression; not used by the universal proof")


if __name__ == "__main__":
    main()
