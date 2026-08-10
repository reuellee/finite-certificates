#!/usr/bin/env python3
"""Exact signed reduction of diagonal-two support-drop pairs.

The companion C++ verifier classifies the unsigned low-source residue.  This
checker imposes the shared-parent rank-four Grassmann--Pluecker axioms and
forbids compatibility for all 56 ordered elementary shears.  At ordinary
walls it then adds every fixed-unit wall-circuit sign identity and every
fixed-unit partner-cofactor equality forced by a strict positive circuit.

The result is an exact necessary-condition filter: localization 3+5 births
are eliminated and 53 ordinary support-pair orbits reduce first to 23 and
then to ten.  The three source-hard ordinary 4+4 labeled pairs are also
eliminated directly by the shared-parent GP and shear-conflict formula.  All
ten surviving 4+5 supports are disjoint from the active wall circuit; this is
the finite input to the exchange-saturated support-drop theorem.

A surviving 4+5 SAT assignment is only an abstract signed support candidate.
It does not prove that the residual factor signs are jointly realizable on the
wall or that the selected witnesses themselves are compatible.
"""

from collections import Counter
import hashlib
from itertools import permutations
import json

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as lab
import verify_diag2_singleton_four_obstruction as singleton
import verify_diag9_parent_ranking as ranking


FORMAT = "diag2-generic-birth-pattern-reduction-v3"

LOCALIZATION_SEEDS = {
    36: ("123/345/367", "156/247/258/468/178"),
    39: ("123/356/378", "146/457/267/248/158"),
    46: ("123/145/167", "256/347/358/468/278"),
    47: ("123/145/167", "256/347/358/468/278"),
}

EXPECTED_LOCALIZATION_DECORATED = {
    36: ("124", (("146/257/248/568/178", 4), ("146/257/158/268/478", 4))),
    39: ("124", (("145/247/167/258/468", 8),)),
    46: ("246", (("246/357/348/568/278", 2), ("346/257/248/568/378", 6))),
    47: (
        "248",
        (
            ("246/357/348/568/278", 4),
            ("346/257/248/568/378", 2),
            ("346/257/358/268/478", 2),
        ),
    ),
}

EXPECTED_STAGE_COUNTS = {
    37: (1, 0, 0),
    38: (0, 0, 0),
    41: (2, 1, 1),
    42: (0, 0, 0),
    44: (1, 0, 0),
    48: (2, 0, 0),
    49: (27, 9, 4),
    50: (7, 3, 3),
    51: (13, 10, 2),
}

EXPECTED_FINAL_SURVIVORS = (
    "41:137/267/238/158/468",
    "49:247/167/148/258/368",
    "49:347/167/258/368/178",
    "49:347/167/138/568/278",
    "49:235/167/348/568/278",
    "50:356/247/167/148/258",
    "50:356/457/167/148/258",
    "50:346/147/567/258/168",
    "51:135/356/347/258/178",
    "51:356/347/157/258/178",
)

EXPECTED_PARTNER_FACTORS = (
    211, 1011, 1187, 1851, 1933, 2623, 4738, 6016, 6017, 6239,
    7807, 12110, 13863, 18201, 19852, 20014, 20050, 20227, 20274,
    20321, 21825, 22224, 22270, 22303, 22321, 22443, 22581, 23091,
    23357, 24225, 26180,
)
EXPECTED_WALL_FACTORS = (2267, 5563, 8543, 18606)
EXPECTED_SOURCE_HARD_FOUR_PARTNERS = (
    (49, "167/348/568/278", 1933),
    (49, "167/258/368/478", 1973),
    (51, "356/347/258/178", 6017),
)
EXPECTED_SOURCE_HARD_FOUR_FORMULA_DIGESTS = {
    (49, "167/348/568/278"): (
        "56db6f1ed30a94e52780001bba0468f9858aed11873f53940e926ad2b787e60f"
    ),
    (49, "167/258/368/478"): (
        "abab41549d57ce75f776048e6d3ede86ca21c4e9c9454d231c65c3dc80958ec5"
    ),
    (51, "356/347/258/178"): (
        "11d371417e70b30250110b3b249ec6c68ebf24049a20c63bcf2755b734a69a8b"
    ),
}
EXPECTED_SEMANTIC_DIGEST = (
    "4546a2e7ba03c1c9dd63abbe65195fc348accf9bf91ccaa773072f1fcae9df38"
)


REPRESENTATIVES = """
37:146/247/258/368/178
41:137/267/348/258/168
41:137/267/238/158/468
44:145/347/267/248/168
48:257/367/348/268/178
48:257/467/348/268/178
49:247/167/148/258/368
49:256/467/248/368/178
49:347/167/258/368/178
49:347/567/258/368/178
49:156/147/458/368/278
49:347/167/138/568/278
49:136/147/348/568/278
49:123/167/348/568/278
49:124/167/348/568/278
49:134/167/348/568/278
49:234/167/348/568/278
49:125/167/348/568/278
49:235/167/348/568/278
49:126/167/348/568/278
49:136/167/348/568/278
49:236/167/348/568/278
49:146/167/348/568/278
49:246/167/348/568/278
49:346/167/348/568/278
49:156/167/348/568/278
49:256/167/348/568/278
49:356/167/348/568/278
49:456/167/348/568/278
49:167/267/348/568/278
49:167/367/348/568/278
49:136/127/348/258/678
49:156/127/348/258/678
50:356/247/167/148/258
50:356/457/167/148/258
50:345/147/567/258/168
50:346/147/567/258/168
50:356/257/467/458/168
50:347/567/258/368/178
50:257/367/358/168/478
51:356/347/157/138/258
51:123/356/347/258/178
51:124/356/347/258/178
51:134/356/347/258/178
51:234/356/347/258/178
51:135/356/347/258/178
51:235/356/347/258/178
51:346/356/347/258/178
51:356/347/157/258/178
51:234/136/357/258/178
51:234/356/357/258/178
51:356/347/357/258/178
51:256/247/367/358/178
""".strip().splitlines()


def parse_support(text):
    return tuple(
        sorted(
            singleton.TRIPLE_INDEX[tuple(map(int, triple))]
            for triple in text.split("/")
        )
    )


def support_text(support):
    return "/".join(
        "".join(map(str, singleton.TRIPLES[index])) for index in support
    )


def triple_map(permutation):
    return tuple(
        singleton.TRIPLE_INDEX[
            tuple(sorted(permutation[label - 1] + 1 for label in triple))
        ]
        for triple in singleton.TRIPLES
    )


def transform(support, mapping):
    return tuple(sorted(mapping[index] for index in support))


def orbit(seed, group):
    return {transform(seed, mapping) for mapping in group}


def quotient(items, group):
    remaining = set(items)
    representatives = []
    while remaining:
        seed = min(remaining)
        current = orbit(seed, group) & remaining
        representatives.append(min(current))
        remaining -= current
    return tuple(sorted(representatives))


def source_count(support, source, target):
    return sum(
        source in singleton.TRIPLES[index]
        and target not in singleton.TRIPLES[index]
        for index in support
    )


def source_hard(left, right):
    return all(
        source_count(left, source, target)
        + source_count(right, source, target)
        >= 2
        for source in range(1, 9)
        for target in range(1, 9)
        if source != target
    )


def all_shear_incompatibility(wall, partner):
    """NAE relation for every ordered shear source/target pair."""
    relations = []
    for source in range(1, 9):
        for target in range(1, 9):
            if source == target:
                continue
            terms = tuple(
                singleton.alpha_term(side, triple, source, target)
                for side, support in enumerate((wall, partner))
                for triple in support
                if source in singleton.TRIPLES[triple]
                and target not in singleton.TRIPLES[triple]
            )
            if len(terms) < 2:
                raise AssertionError(("not source-hard", source, target, terms))
            relations.append(terms)
    return relations


def add_nae(clauses, terms):
    """Forbid all terms from having one common Boolean value."""
    gauge_actions = []
    for term_variables, _constant in terms:
        action = 0
        for variable in term_variables:
            action ^= singleton.GAUGE_ACTIONS[variable]
        gauge_actions.append(action)
    if len(set(gauge_actions)) != 1:
        raise AssertionError("NAE predicate is not gauge invariant")

    variables = tuple(sorted({v for values, _constant in terms for v in values}))
    positions = {variable: index for index, variable in enumerate(variables)}
    for mask in range(1 << len(variables)):
        values = [
            constant
            ^ (
                sum((mask >> positions[variable]) & 1 for variable in term_vars)
                & 1
            )
            for term_vars, constant in terms
        ]
        if len(set(values)) == 1:
            clauses.add(
                tuple(
                    variable + 1 if not ((mask >> index) & 1) else -(variable + 1)
                    for index, variable in enumerate(variables)
                )
            )


def add_xor_zero(clauses, variables, constant):
    multiplicities = Counter(variables)
    variables = tuple(
        sorted(variable for variable, count in multiplicities.items() if count & 1)
    )
    action = 0
    for variable in variables:
        action ^= singleton.GAUGE_ACTIONS[variable]
    if action:
        raise AssertionError("XOR predicate is not gauge invariant")
    for mask in range(1 << len(variables)):
        if constant ^ (mask.bit_count() & 1):
            clauses.add(
                tuple(
                    variable + 1 if not ((mask >> index) & 1) else -(variable + 1)
                    for index, variable in enumerate(variables)
                )
            )


def clause_digest(clauses):
    digest = hashlib.sha256()
    for clause in sorted(clauses, key=lambda item: (len(item), item)):
        digest.update(str(len(clause)).encode("ascii") + b":")
        digest.update(",".join(map(str, clause)).encode("ascii") + b"\n")
    return digest.hexdigest()


def normalized_clauses(clauses):
    answer = set(clauses)
    answer.update((-(variable + 1),) for variable in singleton.GAUGE_PIVOTS)
    return answer


def solve(clauses):
    # Preserve the established deterministic CDCL input order: structural
    # clauses first, then the ten gauge units.  The semantic digest below
    # canonicalizes the union independently of this performance-sensitive
    # branching order.
    normalized = sorted(clauses, key=lambda item: (len(item), item)) + [
        (-(variable + 1),) for variable in singleton.GAUGE_PIVOTS
    ]
    solver = singleton.ExactCDCL(
        singleton.NUMBER_VARIABLES,
        normalized,
        conflict_limit=300_000,
    )
    answer = solver.solve()
    status = "UNSAT" if answer is False else "LIMIT" if answer is None else "SAT"
    if status == "SAT" and not all(
        any((literal > 0) == answer[abs(literal) - 1] for literal in clause)
        for clause in normalized
    ):
        raise AssertionError("CDCL returned an invalid satisfying assignment")
    return status, solver, answer


def shared_parent_gp_formula():
    clauses = set()
    for relation in singleton.GP_RELATIONS:
        add_nae(clauses, relation)
    return frozenset(clauses)


def structural_formula(wall, partner, base_clauses=None):
    clauses = set(base_clauses if base_clauses is not None else shared_parent_gp_formula())
    for relation in all_shear_incompatibility(wall, partner):
        add_nae(clauses, relation)
    return clauses


def solver_record(status, solver, clauses):
    normalized = normalized_clauses(clauses)
    return {
        "status": status,
        "clauses": len(normalized),
        "formula_digest": clause_digest(normalized),
    }


def add_signed_circuit_necessities(clauses, wall, partner, forms, certificates):
    first = min(wall)

    # Every available fixed-unit certificate must encode the same ordinary
    # positive wall circuit in the first extension signature.
    for certificate in certificates[wall]:
        if certificate[0] != "ordinary":
            continue
        support, pattern = ranking.certificate_pattern(certificate, forms)
        for row, (constant, parent_mask) in zip(support, pattern, strict=True):
            add_xor_zero(
                clauses,
                [70 + row, 70 + first]
                + [index for index in range(70) if (parent_mask >> index) & 1],
                constant,
            )

    # Whenever two or more partner cofactors are fixed bracket units, their
    # cofactor signs must agree after twisting by the second signature.
    unit_cofactors = []
    for omitted, row in enumerate(partner):
        ordered = partner[:omitted] + partner[omitted + 1 :]
        four_triples = tuple(sorted(ranking.topes.TRIPLES[index] for index in ordered))
        if four_triples in forms:
            constant, parent_mask = ranking.formula_xor(
                (omitted & 1, 0),
                ranking.ordered_fixed_formula(ordered, forms),
            )
            unit_cofactors.append((row, constant, parent_mask))
    if len(unit_cofactors) > 1:
        first_row, first_constant, first_mask = unit_cofactors[0]
        for row, constant, parent_mask in unit_cofactors[1:]:
            delta_constant, delta_mask = ranking.formula_xor(
                (first_constant, first_mask),
                (constant, parent_mask),
            )
            add_xor_zero(
                clauses,
                [126 + first_row, 126 + row]
                + [index for index in range(70) if (delta_mask >> index) & 1],
                delta_constant,
            )
    return len(unit_cofactors)


def main():
    if singleton.gf2_rank(singleton.GAUGE_ACTIONS) != 10:
        raise AssertionError("the shared-parent gauge rank changed")
    if singleton.gf2_rank(
        singleton.GAUGE_ACTIONS[index] for index in singleton.GAUGE_PIVOTS
    ) != 10:
        raise AssertionError("the ten gauge pivots lost full rank")

    wall_table = lab.occurrence_representatives()
    forms = ranking.fixed_sorted_formulas()
    certificates = ranking.transported_certificates()
    base_clauses = shared_parent_gp_formula()

    listed_by_type = Counter(int(line.split(":")[0]) for line in REPRESENTATIVES)
    if {
        kind: listed_by_type[kind] for kind in EXPECTED_STAGE_COUNTS
    } != {
        kind: counts[0] for kind, counts in EXPECTED_STAGE_COUNTS.items()
    }:
        raise AssertionError("the 53 unsigned representatives changed")

    maps = tuple(triple_map(permutation) for permutation in permutations(range(8)))
    if len(set(maps)) != 40320:
        raise AssertionError("the S8 action on triples is not faithful")

    localization_records = []
    localization_unsat = 0
    for wall_type, (wall_text, seed_text) in LOCALIZATION_SEEDS.items():
        wall = parse_support(wall_text)
        seed = parse_support(seed_text)
        full_wall = wall_table[wall_type]
        dropped = tuple(sorted(set(full_wall) - set(wall)))
        if len(dropped) != 1 or tuple(sorted(set(wall) | set(dropped))) != full_wall:
            raise AssertionError((wall_type, "wrong active localization circuit"))

        wall_stabilizer = tuple(
            mapping for mapping in maps if transform(wall, mapping) == wall
        )
        decorated_stabilizer = tuple(
            mapping
            for mapping in wall_stabilizer
            if transform(dropped, mapping) == dropped
        )
        raw = tuple(sorted(orbit(seed, wall_stabilizer)))
        if len(raw) != 8 or not all(source_hard(wall, partner) for partner in raw):
            raise AssertionError((wall_type, "wrong localization source-hard orbit"))
        decorated = quotient(raw, decorated_stabilizer)
        actual_decorated = tuple(
            (
                support_text(partner),
                len(orbit(partner, decorated_stabilizer) & set(raw)),
            )
            for partner in decorated
        )
        expected_dropped, expected_decorated = EXPECTED_LOCALIZATION_DECORATED[
            wall_type
        ]
        if support_text(dropped) != expected_dropped:
            raise AssertionError((wall_type, "dropped localization normal changed"))
        if actual_decorated != expected_decorated:
            raise AssertionError((wall_type, "decorated localization orbits changed"))

        decorated_records = []
        for partner, (partner_text, orbit_size) in zip(
            decorated, actual_decorated, strict=True
        ):
            clauses = structural_formula(wall, partner, base_clauses)
            status, solver, _answer = solve(clauses)
            if status != "UNSAT":
                raise AssertionError(
                    f"localization type {wall_type} survived the shared-parent GP filter"
                )
            localization_unsat += 1
            decorated_records.append(
                {
                    "partner": partner_text,
                    "orbit_size": orbit_size,
                    "structural": solver_record(status, solver, clauses),
                }
            )
            print(
                "PASS localization",
                wall_type,
                partner_text,
                "decorated orbit",
                orbit_size,
                "UNSAT clauses",
                len(normalized_clauses(clauses)),
                "conflicts",
                solver.conflicts,
            )
        localization_records.append(
            {
                "type": wall_type,
                "active_wall": wall_text,
                "dropped": support_text(dropped),
                "labeled_partners": len(raw),
                "decorated": decorated_records,
            }
        )
    if localization_unsat != 8:
        raise AssertionError("wrong decorated localization UNSAT census")

    first_survivors = []
    final_survivors = []
    first_status = Counter()
    final_status = Counter()
    ordinary_records = []
    stage_counts = {
        kind: [listed_by_type[kind], 0, 0] for kind in EXPECTED_STAGE_COUNTS
    }
    for number, line in enumerate(REPRESENTATIVES, 1):
        wall_type_text, partner_text = line.split(":")
        wall_type = int(wall_type_text)
        wall = wall_table[wall_type]
        partner = parse_support(partner_text)

        clauses = structural_formula(wall, partner, base_clauses)
        status, solver, _answer = solve(clauses)
        if status == "LIMIT":
            raise AssertionError("structural CDCL hit its conflict limit")
        first_status[status] += 1
        record = {
            "number": number,
            "representative": line,
            "structural": solver_record(status, solver, clauses),
        }
        if status != "SAT":
            ordinary_records.append(record)
            continue
        first_survivors.append(line)
        stage_counts[wall_type][1] += 1

        unit_count = add_signed_circuit_necessities(
            clauses, wall, partner, forms, certificates
        )
        status, solver, _answer = solve(clauses)
        if status == "LIMIT":
            raise AssertionError("signed CDCL hit its conflict limit")
        final_status[status] += 1
        record["unit_cofactors"] = unit_count
        record["signed"] = solver_record(status, solver, clauses)
        if status == "SAT":
            final_survivors.append(line)
            stage_counts[wall_type][2] += 1
        ordinary_records.append(record)

    actual_stage_counts = {
        kind: tuple(counts) for kind, counts in stage_counts.items()
    }
    if actual_stage_counts != EXPECTED_STAGE_COUNTS:
        raise AssertionError(f"53 -> 23 -> 10 stage counts changed: {actual_stage_counts}")
    if first_status != Counter({"UNSAT": 30, "SAT": 23}):
        raise AssertionError("wrong structural SAT status census")
    if final_status != Counter({"UNSAT": 13, "SAT": 10}):
        raise AssertionError("wrong signed SAT status census")
    if tuple(final_survivors) != EXPECTED_FINAL_SURVIVORS:
        raise AssertionError("the ten signed support survivors changed")

    exchange_disjoint_records = []
    for line in final_survivors:
        wall_type_text, partner_text = line.split(":")
        wall_type = int(wall_type_text)
        wall = wall_table[wall_type]
        partner = parse_support(partner_text)
        overlap = tuple(sorted(set(wall) & set(partner)))
        if overlap:
            raise AssertionError(
                f"exchange residue {line} meets its wall on {support_text(overlap)}"
            )
        exchange_disjoint_records.append(
            {
                "representative": line,
                "wall": support_text(wall),
                "overlap": "",
            }
        )

    _occurrences, occurrence_factor, _polynomials = lab.factor_polynomials()
    source_hard_four_records = []
    source_hard_four_signed_records = []
    seen_source_hard_four = set()
    for wall_type, support, expected_factor in EXPECTED_SOURCE_HARD_FOUR_PARTNERS:
        partner = parse_support(support)
        key = (wall_type, partner)
        if key in seen_source_hard_four:
            raise AssertionError("duplicate source-hard four-partner record")
        seen_source_hard_four.add(key)
        if not source_hard(wall_table[wall_type], partner):
            raise AssertionError("listed four-partner is not source-hard")
        factor = occurrence_factor.get(partner)
        wall_factor = occurrence_factor[wall_table[wall_type]]
        if factor != expected_factor:
            raise AssertionError("a source-hard four-partner factor changed")
        if factor == wall_factor:
            raise AssertionError("a source-hard four-partner is not a second wall")
        if set(wall_table[wall_type]) & set(partner):
            raise AssertionError("a source-hard four-partner meets its wall support")

        four_clauses = structural_formula(
            wall_table[wall_type], partner, base_clauses
        )
        four_status, four_solver, _four_answer = solve(four_clauses)
        if four_status != "UNSAT":
            raise AssertionError(
                f"ordinary 4+4 pair {wall_type}:{support} survived the signed filter"
            )
        four_record = solver_record(four_status, four_solver, four_clauses)
        if four_record["formula_digest"] != (
            EXPECTED_SOURCE_HARD_FOUR_FORMULA_DIGESTS[(wall_type, support)]
        ):
            raise AssertionError("an ordinary 4+4 formula digest changed")
        source_hard_four_signed_records.append(
            {
                "type": wall_type,
                "support": support,
                "structural": four_record,
            }
        )
        source_hard_four_records.append(
            {
                "type": wall_type,
                "support": support,
                "factor": factor,
                "wall_factor": wall_factor,
            }
        )
    partner_factors = set()
    fixed_cofactors = 0
    residual_cofactor_occurrences = 0
    for line in final_survivors:
        _wall_type_text, partner_text = line.split(":")
        partner = parse_support(partner_text)
        for omitted in range(5):
            cofactor = tuple(sorted(partner[:omitted] + partner[omitted + 1 :]))
            factor = occurrence_factor.get(cofactor)
            if factor is None:
                fixed_cofactors += 1
            else:
                residual_cofactor_occurrences += 1
                partner_factors.add(factor)
    wall_factors = {
        occurrence_factor[wall_table[int(line.split(":")[0])]]
        for line in final_survivors
    }
    selected_cofactor_footprint = partner_factors | wall_factors
    if (residual_cofactor_occurrences, fixed_cofactors) != (43, 7):
        raise AssertionError("the partner cofactor census changed")
    if tuple(sorted(partner_factors)) != EXPECTED_PARTNER_FACTORS:
        raise AssertionError("the 31 partner factor IDs changed")
    if tuple(sorted(wall_factors)) != EXPECTED_WALL_FACTORS:
        raise AssertionError("the four wall factor IDs changed")
    if len(selected_cofactor_footprint) != 35:
        raise AssertionError("the selected-pair cofactor footprint is no longer 35 factors")

    payload = {
        "format": FORMAT,
        "localization": localization_records,
        "ordinary": ordinary_records,
        "stage_counts": actual_stage_counts,
        "final_survivors": final_survivors,
        "exchange_disjoint": exchange_disjoint_records,
        "partner_cofactors": {
            "residual_occurrences": residual_cofactor_occurrences,
            "fixed_occurrences": fixed_cofactors,
            "factor_ids": sorted(partner_factors),
        },
        "wall_factor_ids": sorted(wall_factors),
        "selected_cofactor_footprint": sorted(selected_cofactor_footprint),
        "source_hard_four_partners": source_hard_four_records,
        "source_hard_four_signed": source_hard_four_signed_records,
    }
    digest = hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    if EXPECTED_SEMANTIC_DIGEST is not None and digest != EXPECTED_SEMANTIC_DIGEST:
        raise AssertionError("support-drop semantic digest changed")

    print(
        "PASS localization source-hard 3+5 residue:",
        "32 labeled partners / 8 decorated formulas, all UNSAT",
    )
    print("PASS ordinary source-hard orbits: 53 -> 23 -> 10")
    for kind in EXPECTED_STAGE_COUNTS:
        print("  type", kind, "counts", actual_stage_counts[kind])
    for line in final_survivors:
        print("  survivor", line)
    print("PASS exchange residue: all ten 4+5 survivors are wall-disjoint")
    print(
        "PASS partner cofactors: 43 residual occurrences / 7 fixed;",
        "selected-pair cofactor footprint",
        len(selected_cofactor_footprint),
        "factors",
    )
    print(
        "PASS ordinary 4+4 source-hard residue:",
        "3 labeled supports / 2 orbits, all signed formulas UNSAT",
    )
    print("SEMANTIC DIGEST", digest)
    print("SCOPE necessary signed support pairs; not wall realizability or full masks")


if __name__ == "__main__":
    main()
