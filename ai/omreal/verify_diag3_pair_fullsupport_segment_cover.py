#!/usr/bin/env python3
"""Independent exact replay of the minimum full-support segment cover."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
CERTIFICATE = DATA / "DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json"
PILOT = DATA / "DIAG3_COMPONENT_COSHEAF_PILOT.json"
ATLAS = DATA / "DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json"

sys.path.insert(0, str(HERE))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402
import verify_diag2_canonical_robust_edges as evaluator  # noqa: E402
import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


_REPLAY_CACHE = None


def digest_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def digest_ids(domain: bytes, identifiers) -> str:
    payload = ",".join(map(str, sorted(identifiers))).encode("ascii")
    return sha256(domain + b"\0" + payload).hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def exact_inputs():
    _matrices, points, _packed, _states, _hamming, _multiplicity = (
        transition.exact_inputs()
    )
    with np.load(transition.FACTOR_STATES, allow_pickle=False) as source:
        packed = np.asarray(source["chart_factor_sign_packed"], dtype=np.uint8)
    signs = np.unpackbits(packed, axis=1, bitorder="little")[:, :26_740]
    candidates = tuple(gate.parse_candidates())
    incidence = np.asarray(
        [
            signs[left, candidates] != signs[right, candidates]
            for left, right in safe.EDGES
        ],
        dtype=bool,
    )
    return points, candidates, incidence


def replay_parent_safety(points):
    records = [
        json.loads(line)
        for line in gate.CATALOG.read_text(encoding="utf-8").splitlines()
        if line
    ]
    parents, parent_digest = gate.parent_polynomials(records[2599])
    for edge_index, (left, right) in enumerate(safe.EDGES):
        for label, target, polynomial, _terms in parents:
            restricted = safe.segment_power(
                polynomial, points[left], points[right]
            )
            require(
                safe.positive_unit([target * value for value in restricted]),
                f"edge {edge_index} leaves parent at {label}",
            )
    return parent_digest


def replay_relative_scope():
    atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
    pilot = json.loads(PILOT.read_text(encoding="utf-8"))
    divisors = {
        (int(row["moving_column"]), int(row["coordinate_row"])):
        str(row["parent_bracket"])
        for row in atlas["boundary_divisors"]
    }
    require(
        set(divisors)
        == {
            (column, row)
            for column in (6, 7, 8)
            for row in (1, 2, 3, 4)
        },
        "boundary divisor map",
    )
    relative = {}
    full = []
    for support in product(range(1, 16), repeat=3):
        tags = tuple(
            sorted(
                {
                    divisors[(6 + block, bit + 1)]
                    for block, mask in enumerate(support)
                    for bit in range(4)
                    if not (mask >> bit) & 1
                }
            )
        )
        if tags:
            relative[support] = tags
        else:
            full.append(support)
    supports = tuple(map(tuple, pilot["scope"]["pilot_supports"]))
    require(len(relative) == 3_374, "proper support count")
    require(full == [(15, 15, 15)], "full support partition")
    require(supports == ((3, 1, 15), (3, 3, 7)), "pilot supports")
    require(all(support in relative for support in supports), "pilot is relative")
    return supports


def combinatorial_optimum(candidates, incidence):
    multiplicity = incidence.sum(axis=0)
    known = multiplicity > 0
    require(int(known.sum()) == 10_844, "known crossing count")
    mandatory = sorted(
        set(np.where(incidence[:, multiplicity == 1])[0].tolist())
    )
    require(len(mandatory) == 34, "mandatory edge count")
    mandatory_coverage = incidence[mandatory].any(axis=0)
    remaining = np.where(known & ~mandatory_coverage)[0].tolist()
    require(int(mandatory_coverage.sum()) == 10_815, "mandatory coverage")
    require(len(remaining) == 29, "remaining factor count")

    mandatory_rows = []
    for edge_index in mandatory:
        unique = [
            candidates[index]
            for index in np.where(
                incidence[edge_index] & (multiplicity == 1)
            )[0]
        ]
        require(unique, "mandatory witness")
        mandatory_rows.append(
            (
                edge_index,
                safe.EDGES[edge_index],
                min(unique),
                len(unique),
            )
        )

    raw = {}
    for edge_index in range(len(safe.EDGES)):
        if edge_index in mandatory:
            continue
        mask = 0
        for position, candidate_index in enumerate(remaining):
            if incidence[edge_index, candidate_index]:
                mask |= 1 << position
        if mask:
            raw.setdefault(mask, []).append(edge_index)
    maximal = sorted(
        (min(edges), mask, tuple(edges))
        for mask, edges in raw.items()
        if not any(mask != other and mask | other == other for other in raw)
    )
    require(len(raw) == 21 and len(maximal) == 7, "maximal pattern census")
    full = (1 << len(remaining)) - 1
    attempts = 0
    first_solutions = None
    for size in range(7):
        solutions = []
        for choice in combinations(maximal, size):
            attempts += 1
            union = 0
            for _edge, mask, _equivalent in choice:
                union |= mask
            if union == full:
                solutions.append(tuple(edge for edge, _mask, _same in choice))
        if solutions:
            first_solutions = solutions
            break
    require(size == 6, "optional optimum")
    require(len(first_solutions) == 3, "minimum solution census")
    optional = min(first_solutions)
    selected = tuple(sorted((*mandatory, *optional)))
    require(len(selected) == 40, "selected edge count")
    require(
        np.array_equal(incidence[list(selected)].any(axis=0), known),
        "cover equality",
    )
    return {
        "known": known,
        "multiplicity": multiplicity,
        "mandatory": mandatory,
        "mandatory_rows": mandatory_rows,
        "mandatory_coverage": mandatory_coverage,
        "remaining": remaining,
        "raw": raw,
        "maximal": maximal,
        "attempts": attempts,
        "solutions": first_solutions,
        "optional": optional,
        "selected": selected,
    }


def replay_exact_assignment(selected, known, candidates, incidence, points):
    _types, _terms, polynomials = labeled.factor_polynomials()
    assignment = {}
    for candidate_index in np.where(known)[0]:
        factor_id = candidates[candidate_index]
        edge_index = next(
            edge
            for edge in selected
            if incidence[edge, candidate_index]
        )
        left, right = safe.EDGES[edge_index]
        left_value = evaluator.evaluate(polynomials[factor_id], points[left])
        right_value = evaluator.evaluate(polynomials[factor_id], points[right])
        require(left_value * right_value < 0, f"exact crossing {factor_id}")
        assignment[factor_id] = edge_index
    return assignment


def verify_record(record):
    global _REPLAY_CACHE
    if _REPLAY_CACHE is None:
        points, candidates, incidence = exact_inputs()
        parent_digest = replay_parent_safety(points)
        supports = replay_relative_scope()
        proof = combinatorial_optimum(candidates, incidence)
        assignment = replay_exact_assignment(
            proof["selected"], proof["known"], candidates, incidence, points
        )
        _REPLAY_CACHE = candidates, parent_digest, supports, proof, assignment
    candidates, parent_digest, supports, proof, assignment = _REPLAY_CACHE

    require(
        record["format"] == "diag3-pair-fullsupport-segment-cover-v1",
        "format",
    )
    require(
        record["status"] == "EXACT_OPTIMAL_KNOWN_WALL_SEGMENT_COVER",
        "status",
    )
    require(record["scope"]["support"] == [15, 15, 15], "support")
    require(record["scope"]["component_coverage"] == "NOT_CLAIMED", "scope")
    require(record["scope"]["global_parent_cell_coverage"] == "NOT_CLAIMED", "scope")
    require(record["scope"]["honest_9dvl_score"] == "2/9", "score")

    require(
        record["inputs"]
        == {
            "factor_state_sha256": digest_file(transition.FACTOR_STATES),
            "candidate_factor_sha256": digest_file(gate.CANDIDATES),
            "parent_sign_sha256": parent_digest,
            "component_cosheaf_pilot_sha256": digest_file(PILOT),
            "compactification_atlas_sha256": digest_file(ATLAS),
        },
        "input pins",
    )
    audit = record["target_selection_audit"]
    require(audit["proper_relative_supports"] == 3_374, "relative support count")
    require(audit["unique_possibly_nonrelative_support"] == [15, 15, 15], "relative partition")
    require(audit["audited_pilot_supports"] == [list(row) for row in supports], "audit supports")
    require(audit["relative_chain_generator_contribution"] == 0, "relative contribution")
    require(audit["decision"] == "RETAIN_AS_COMPILER_STRESS_TESTS_ONLY", "target decision")

    source = record["source_bank"]
    require(source["original_edges"] == 105, "original edges")
    require(source["known_crossed_factors"] == 10_844, "known factors")
    require(source["selected_edges"] == 40, "selected edges")
    require(source["edge_reduction"] == 65, "edge reduction")
    require(source["edge_reduction_fraction"] == "13/21", "edge reduction fraction")
    require(source["selected_edge_indices"] == list(proof["selected"]), "selected indices")
    require(
        source["selected_chart_pairs"]
        == [list(safe.EDGES[index]) for index in proof["selected"]],
        "selected charts",
    )
    require(
        source["known_factor_ids_sha256"]
        == digest_ids(
            b"diag3-fullsupport-known-crossed-factors-v1",
            (candidates[index] for index in np.where(proof["known"])[0]),
        ),
        "known-factor digest",
    )
    require(
        source["selected_crossing_assignment_sha256"]
        == sha256(repr(tuple(sorted(assignment.items()))).encode("ascii")).hexdigest(),
        "assignment digest",
    )

    optimum = record["optimality"]
    require(optimum["mandatory_edges"] == 34, "mandatory edges")
    require(optimum["mandatory_edge_indices"] == proof["mandatory"], "mandatory indices")
    require(optimum["mandatory_unique_factor_count"] == 49, "unique factor count")
    require(optimum["mandatory_coverage"] == 10_815, "mandatory coverage")
    expected_witnesses = [
        {
            "edge_index": edge,
            "charts": list(charts),
            "least_unique_factor_id": factor,
            "unique_factor_count": count,
        }
        for edge, charts, factor, count in proof["mandatory_rows"]
    ]
    require(optimum["mandatory_witnesses"] == expected_witnesses, "mandatory witnesses")
    require(optimum["remaining_factor_count"] == 29, "remaining count")
    require(
        optimum["remaining_factor_ids"]
        == [candidates[index] for index in proof["remaining"]],
        "remaining factors",
    )
    require(optimum["nonempty_optional_patterns"] == 21, "optional patterns")
    require(
        optimum["subsets_of_at_most_five_exhausted"]
        == sum(len(tuple(combinations(proof["maximal"], size))) for size in range(6)),
        "exhausted subset census",
    )
    require(optimum["covers_with_five_optional_patterns"] == 0, "five-edge no-go")
    require(optimum["minimum_optional_edges"] == 6, "optional lower bound")
    require(optimum["six_pattern_cover_count"] == 3, "optimal cover census")
    require(optimum["canonical_optional_edge_indices"] == list(proof["optional"]), "canonical optional")

    maximal_rows = []
    for representative, mask, equivalent in proof["maximal"]:
        maximal_rows.append(
            {
                "representative_edge_index": representative,
                "equivalent_edge_indices": list(equivalent),
                "charts": list(safe.EDGES[representative]),
                "remaining_factor_ids": [
                    candidates[proof["remaining"][position]]
                    for position in range(len(proof["remaining"]))
                    if mask >> position & 1
                ],
            }
        )
    require(
        optimum["inclusion_maximal_optional_patterns"] == maximal_rows,
        "maximal pattern rows",
    )
    semantic_payload = {
        "mandatory": proof["mandatory"],
        "remaining": [candidates[index] for index in proof["remaining"]],
        "maximal_patterns": maximal_rows,
        "canonical_optional": list(proof["optional"]),
        "selected": list(proof["selected"]),
    }
    require(
        record["semantic_sha256"]
        == sha256(
            json.dumps(
                semantic_payload, sort_keys=True, separators=(",", ":")
            ).encode("ascii")
        ).hexdigest(),
        "semantic digest",
    )
    require(
        "40-edge full-support source cover"
        in record["decision"]["next_pair_action"],
        "next action",
    )
    require("2/9" in record["theorem_effect"], "honest theorem effect")


def main():
    stored = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    verify_record(stored)
    mutations = []
    for path, value in (
        (("format",), "corrupted"),
        (("status",), "PROVED_DIAGONAL_THREE"),
        (("scope", "component_coverage"), "GLOBAL"),
        (("scope", "honest_9dvl_score"), "3/9"),
        (("target_selection_audit", "relative_chain_generator_contribution"), 1),
        (("target_selection_audit", "decision"), "SCALE_GLOBALLY"),
        (("source_bank", "selected_edges"), 39),
        (("source_bank", "selected_edge_indices"), []),
        (("source_bank", "selected_crossing_assignment_sha256"), "0" * 64),
        (("optimality", "mandatory_edges"), 33),
        (("optimality", "covers_with_five_optional_patterns"), 1),
        (("optimality", "minimum_optional_edges"), 5),
        (("semantic_sha256",), "0" * 64),
        (("theorem_effect",), "diagonal three proved"),
    ):
        mutation = deepcopy(stored)
        target = mutation
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        mutations.append(mutation)
    rejected = 0
    for mutation in mutations:
        try:
            verify_record(mutation)
        except AssertionError:
            rejected += 1
    require(rejected == len(mutations), "hostile mutation rejection")
    print("PASS all 105 source edges independently remain in the strict parent cell")
    print("PASS 34 forced edges cover 10,815/10,844 known crossing factors")
    print("PASS seven maximal optional patterns exhaust the 29-factor residue")
    print("PASS no five-pattern cover; canonical six-pattern completion")
    print("PASS exact 40-edge cover is optimal and replays all endpoint crossings")
    print("PASS both proposed proper-support stars generate zero relative chains")
    print(f"PASS {rejected}/{len(mutations)} hostile corruptions rejected")
    print("SCOPE source-skeleton compression only; global components and triple branch open; honest 9DVL 2/9")


if __name__ == "__main__":
    main()
