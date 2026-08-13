#!/usr/bin/env python3
"""Universal two-block ordered-root switches on one primitive factor wall.

For every pair of active small circuits attached to occurrences of the same
global residual factor, and for two independent arbitrary 56-bit signings,
form the common ordered-root graph.  A vertex is a root compatible with both
signed circuits.  An edge requires one *common order* of the two elementary
shears to be safe for both circuits.

The global factor census and the exact canonical walls reduce all labeled
support pairs to finitely many factor-stabilizer orbits.  Exact CDCL then
rejects both an empty common graph and a nontrivial component cut.

A second exact audit fixes either shear-parameter sign and, on canonical
representatives, the numerically descending half of the root directions.  It
rejects absence of a compatible root for all active single supports and all
same-factor support pairs.  Only the fixed parameter sign, not numeric
descent, is relabeling invariant.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from hashlib import sha256
from itertools import combinations_with_replacement

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled
import DIAG9_GRAPH_exact_topes as exact_topes
import BLOCK_GORDAN_MONOCHROMATIC_WALL_STARS as wall_stars
import verify_diag2_canonical_robust_edges as robust
import verify_diag2_escape_set_topes as escape
import verify_diag2_singleton_four_obstruction as singleton
import verify_diag3_pair_local_root_switch as local


FORMAT = "diag3-pair-factor-root-switch-v1"
MULTIPLE_FACTOR_KINDS = (36, 38, 48)
SINGLE_FACTOR_KINDS = (49, 50, 51)
EXPECTED_SUPPORT_COUNTS = {
    36: (65, 31, {3: 1, 4: 30}, 35),
    38: (15, 15, {4: 15}, 8),
    48: (2, 2, {4: 2}, 2),
}
EXPECTED_PAIR_ORBITS = 48
EXPECTED_RESTRICTED_ROOTS = 28
EXPECTED_ORIENTATION_FORMULAS = (26, 96)  # single-support, support-pair

# Filled after the first complete exact replay.  The digest covers the stable
# ordered list of factor kind, support pair, both CNF sizes and hashes, and
# both exact-CDCL conflict counts.
EXPECTED_SEMANTIC_DIGEST = (
    "7196d312dbcb473dadfa9b00f2a9491d0c4171784c7b0bbd0d8d20bdfca20104"
)


class TwoSigningCNF(local.CNFBuilder):
    """The first 112 variables are two independent signing bit-vectors."""

    def __init__(self):
        self.number_variables = 112
        self.clauses = []
        self.xor_variables = {}


def shifted(constraints, offset):
    if constraints is None:
        return None
    return tuple(
        (left + offset, right + offset, constant)
        for left, right, constant in constraints
    )


def joint_constraints(first, second):
    if first is None or second is None:
        return None
    return tuple(first) + shifted(second, 56)


def common_predicates(first_support, second_support):
    first = local.RootPredicates.build(first_support)
    second = local.RootPredicates.build(second_support)
    builder = TwoSigningCNF()
    compatible = tuple(
        builder.and_variable(
            joint_constraints(
                first.compatibility[root], second.compatibility[root]
            )
        )
        for root in range(len(escape.DIRECTIONS))
    )
    return first, second, builder, compatible


def canonical_clauses(builder):
    return tuple(
        sorted(set(builder.clauses), key=lambda clause: (len(clause), clause))
    )


def empty_formula(first_support, second_support):
    _, _, builder, compatible = common_predicates(first_support, second_support)
    for variable in compatible:
        builder.add_clause(-(variable + 1))
    return builder, canonical_clauses(builder)


def cut_formula(first_support, second_support):
    first, second, builder, compatible = common_predicates(
        first_support, second_support
    )
    cut = tuple(builder.new_variable() for _ in escape.DIRECTIONS)

    for left in range(len(escape.DIRECTIONS)):
        for right in range(left + 1, len(escape.DIRECTIONS)):
            if escape.DIRECTIONS[left][:2] == escape.DIRECTIONS[right][:2]:
                continue
            for source, target in ((left, right), (right, left)):
                # The order cannot be chosen independently in the two blocks.
                safe = builder.and_variable(
                    joint_constraints(
                        first.ordered[source, target],
                        second.ordered[source, target],
                    )
                ) + 1
                c_left = compatible[left] + 1
                c_right = compatible[right] + 1
                x_left = cut[left] + 1
                x_right = cut[right] + 1
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
        builder.add_clause(-zero, compatible_literal)
        builder.add_clause(-zero, -cut_literal)
        builder.add_clause(zero, -compatible_literal, cut_literal)
        builder.add_clause(-one, compatible_literal)
        builder.add_clause(-one, cut_literal)
        builder.add_clause(one, -compatible_literal, -cut_literal)
        side_zero.append(zero)
        side_one.append(one)
    builder.add_clause(*side_zero)
    builder.add_clause(*side_one)
    return builder, canonical_clauses(builder)


def formula_digest(number_variables, clauses, tag):
    digest = sha256()
    digest.update(FORMAT.encode("ascii") + b"\0" + tag.encode("ascii") + b"\0")
    digest.update(int(number_variables).to_bytes(4, "little"))
    for clause in clauses:
        digest.update(len(clause).to_bytes(2, "little"))
        for literal in clause:
            digest.update(int(literal).to_bytes(4, "little", signed=True))
    return digest.hexdigest()


def solve_unsat(builder, clauses, limit):
    solver = singleton.ExactCDCL(
        builder.number_variables, clauses, conflict_limit=limit
    )
    answer = solver.solve()
    if answer is None:
        raise AssertionError("exact CDCL reached its conflict limit")
    if answer is not False:
        first = sum(1 << index for index in range(56) if answer[index])
        second = sum(
            1 << index for index in range(56) if answer[56 + index]
        )
        raise AssertionError(
            f"common ordered-root theorem false at signings {first}/{second}"
        )
    return solver.conflicts


def transform_support(support, mapping):
    return tuple(sorted(mapping[index] for index in support))


def factor_support_pair_orbits():
    occurrences, occurrence_factor, factor_polynomials = labeled.factor_polynomials()
    (
        factor_representatives,
        stabilizers,
        _alignment,
        _factor_occurrence,
        _orbit_sizes,
    ) = labeled.factor_orbit_data(occurrences, occurrence_factor)
    factor_ids, canonical_polynomials = robust.canonical_data()
    if factor_polynomials != canonical_polynomials:
        raise AssertionError("global factor polynomial order changed")
    if any(factor_ids[kind] != factor_representatives[kind] for kind in MULTIPLE_FACTOR_KINDS):
        raise AssertionError("multiple-occurrence factor representative changed")

    records = []
    for kind in MULTIPLE_FACTOR_KINDS:
        witness = robust.construct_witness(kind, factor_ids, factor_polynomials)
        normals = exact_topes.derived_rows(
            robust.integer_matrix(witness.center), normalize=False
        )
        members = tuple(
            occurrence
            for occurrence in occurrences
            if occurrence_factor[occurrence] == factor_ids[kind]
        )
        supports = tuple(
            sorted(
                {
                    wall_stars.node_wall_circuit(occurrence, normals)
                    for occurrence in members
                }
            )
        )
        size_count = {}
        for support in supports:
            size_count[len(support)] = size_count.get(len(support), 0) + 1

        seen = set()
        representatives = []
        for first, second in combinations_with_replacement(supports, 2):
            key = tuple(sorted((first, second)))
            if key in seen:
                continue
            orbit = {
                tuple(
                    sorted(
                        (
                            transform_support(first, mapping),
                            transform_support(second, mapping),
                        )
                    )
                )
                for mapping in stabilizers[kind]
            }
            if not orbit.issubset(
                set(combinations_with_replacement(supports, 2))
            ):
                raise AssertionError("factor stabilizer left its active supports")
            seen.update(orbit)
            representatives.append(key)
        expected_occurrences, expected_supports, expected_sizes, expected_orbits = (
            EXPECTED_SUPPORT_COUNTS[kind]
        )
        if (
            len(members),
            len(supports),
            size_count,
            len(representatives),
        ) != (
            expected_occurrences,
            expected_supports,
            expected_sizes,
            expected_orbits,
        ):
            raise AssertionError(f"type {kind} support-pair census changed")
        if len(seen) != len(supports) * (len(supports) + 1) // 2:
            raise AssertionError("factor support-pair orbit coverage is incomplete")
        records.extend((kind, first, second) for first, second in representatives)

    # The remaining three factor orbits have one occurrence.  Their one
    # self-pair is not represented in the multiple-occurrence list above.
    records.extend(
        (kind, local.active_support(kind), local.active_support(kind))
        for kind in SINGLE_FACTOR_KINDS
    )
    records = tuple(sorted(records))
    if len(records) != EXPECTED_PAIR_ORBITS:
        raise AssertionError("wrong number of same-factor support-pair orbits")
    return records


def audit_pair(record):
    kind, first, second = record
    empty_builder, empty_clauses = empty_formula(first, second)
    empty_conflicts = solve_unsat(empty_builder, empty_clauses, 100_000)
    cut_builder, cut_clauses = cut_formula(first, second)
    cut_conflicts = solve_unsat(cut_builder, cut_clauses, 2_000_000)
    return {
        "kind": kind,
        "first": first,
        "second": second,
        "empty_variables": empty_builder.number_variables,
        "empty_clauses": len(empty_clauses),
        "empty_xors": len(empty_builder.xor_variables),
        "empty_conflicts": empty_conflicts,
        "empty_digest": formula_digest(
            empty_builder.number_variables, empty_clauses, "empty"
        ),
        "cut_variables": cut_builder.number_variables,
        "cut_clauses": len(cut_clauses),
        "cut_xors": len(cut_builder.xor_variables),
        "cut_conflicts": cut_conflicts,
        "cut_digest": formula_digest(
            cut_builder.number_variables, cut_clauses, "cut"
        ),
    }


def parameter_orientation_audit(pairs):
    """Prove existence after fixing either shear-parameter orientation.

    The SAT formulas use the numerically descending source/target half of the
    roots as a stronger canonical-representative test.  Numeric descent is
    not S8-invariant; parameter sign is.
    """

    single_formulas = 0
    pair_formulas = 0
    conflicts = 0
    for parameter_sign in (-1, 1):
        restricted = tuple(
            root
            for root, (source, target, sign) in enumerate(escape.DIRECTIONS)
            if source > target and sign == parameter_sign
        )
        if len(restricted) != EXPECTED_RESTRICTED_ROOTS:
            raise AssertionError("wrong descending fixed-sign root count")

        for kind in local.CANONICAL_KINDS:
            predicates = local.RootPredicates.build(local.active_support(kind))
            builder = local.CNFBuilder()
            compatible = tuple(
                builder.and_variable(constraints)
                for constraints in predicates.compatibility
            )
            for root in restricted:
                builder.add_clause(-(compatible[root] + 1))
            clauses = canonical_clauses(builder)
            solver = singleton.ExactCDCL(
                builder.number_variables, clauses, conflict_limit=10_000
            )
            answer = solver.solve()
            if answer is not False:
                raise AssertionError(
                    f"type {kind}: no fixed-sign descending root at "
                    f"sign {parameter_sign}"
                )
            single_formulas += 1
            conflicts += solver.conflicts

        for kind, first, second in pairs:
            _first, _second, builder, compatible = common_predicates(first, second)
            for root in restricted:
                builder.add_clause(-(compatible[root] + 1))
            clauses = canonical_clauses(builder)
            solver = singleton.ExactCDCL(
                builder.number_variables, clauses, conflict_limit=10_000
            )
            answer = solver.solve()
            if answer is not False:
                raise AssertionError(
                    f"type {kind}: two signings have no common fixed-sign "
                    f"descending root at sign {parameter_sign}"
                )
            pair_formulas += 1
            conflicts += solver.conflicts

    if (single_formulas, pair_formulas) != EXPECTED_ORIENTATION_FORMULAS:
        raise AssertionError("wrong fixed-parameter orientation formula census")
    if conflicts:
        raise AssertionError("fixed-parameter orientation lost unit propagation")
    return single_formulas, pair_formulas, conflicts


def semantic_digest(records):
    digest = sha256()
    digest.update(FORMAT.encode("ascii") + b"\0")
    for record in records:
        digest.update(repr(tuple(sorted(record.items()))).encode("ascii") + b"\n")
    return digest.hexdigest()


def common_graph_cycle_canary():
    """Pin a connected common graph with a large surviving cycle module."""

    support = (0, 7, 8, 32)
    signatures = (65_112_642_768_982_744, 23_589_210_603_315_253)
    predicates = local.RootPredicates.build(support)
    vertex_mask = predicates.vertex_mask(signatures[0]) & predicates.vertex_mask(
        signatures[1]
    )
    vertices = tuple(
        root
        for root in range(len(escape.DIRECTIONS))
        if vertex_mask >> root & 1
    )
    adjacency = {root: set() for root in vertices}
    edges = 0
    for offset, left in enumerate(vertices):
        for right in vertices[offset + 1 :]:
            # Opposite orientations of one root line are distinct vertices,
            # but there is no two-root ordered shear between them.
            if escape.DIRECTIONS[left][:2] == escape.DIRECTIONS[right][:2]:
                continue
            common_order = any(
                local.constraints_hold(
                    signatures[0], predicates.ordered[source, target]
                )
                and local.constraints_hold(
                    signatures[1], predicates.ordered[source, target]
                )
                for source, target in ((left, right), (right, left))
            )
            if common_order:
                adjacency[left].add(right)
                adjacency[right].add(left)
                edges += 1
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
    cycle_rank = edges - len(vertices) + components
    if (len(vertices), edges, components, cycle_rank) != (43, 860, 1, 818):
        raise AssertionError("common-root cycle canary changed")
    return len(vertices), edges, cycle_rank


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    return parser.parse_args()


def main():
    args = parse_args()
    if args.workers < 1:
        raise ValueError("--workers must be positive")
    canary_vertices, canary_edges, canary_cycles = common_graph_cycle_canary()
    pairs = factor_support_pair_orbits()
    orientation_counts = parameter_orientation_audit(pairs)
    if args.workers == 1:
        records = [audit_pair(pair) for pair in pairs]
    else:
        records = []
        with ProcessPoolExecutor(max_workers=args.workers) as executor:
            futures = {executor.submit(audit_pair, pair): pair for pair in pairs}
            for future in as_completed(futures):
                records.append(future.result())
        records.sort(key=lambda record: (record["kind"], record["first"], record["second"]))

    digest = semantic_digest(records)
    if EXPECTED_SEMANTIC_DIGEST is not None and digest != EXPECTED_SEMANTIC_DIGEST:
        raise AssertionError("two-signing factor-root semantic digest changed")
    by_kind = {}
    for record in records:
        by_kind[record["kind"]] = by_kind.get(record["kind"], 0) + 1
    print("UNSAT empty/common-cut formulas for", len(records), "support-pair orbits")
    print("PAIR_ORBITS_BY_FACTOR_KIND", dict(sorted(by_kind.items())))
    print("TOTAL_CUT_CONFLICTS", sum(record["cut_conflicts"] for record in records))
    print(
        "FIXED_PARAMETER_ORIENTATION",
        "single/pair/conflicts", orientation_counts,
    )
    print(
        "COMMON_GRAPH_CANARY",
        "vertices", canary_vertices,
        "edges", canary_edges,
        "cycle-rank", canary_cycles,
    )
    print("SEMANTIC_SHA256", digest)
    print("THEOREM every same-factor two-signing common ordered-root graph is nonempty and connected")
    print("THEOREM either parameter sign has a common root; numeric descent is only a canonical SAT strengthening")
    print("SCOPE local factor-wall theorem; no global frontier rank or beta injectivity")


if __name__ == "__main__":
    main()
