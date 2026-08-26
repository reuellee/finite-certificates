#!/usr/bin/env python3
"""Separate exact checkpoint replay of the minimum full-support segment cover."""

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


def canonical_digest(value) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def semantic_seal(record) -> str:
    payload = deepcopy(record)
    payload.pop("semantic_sha256", None)
    return canonical_digest(payload)


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
    original_incidences = int(incidence.sum())
    retained_incidences = int(incidence[list(selected)].sum())
    require(
        (original_incidences, retained_incidences) == (412_093, 157_448),
        "edge-factor incidence accounting",
    )
    raw_optional = []
    for edge_index in range(len(safe.EDGES)):
        if edge_index in mandatory:
            continue
        mask = sum(
            1 << position
            for position, candidate_index in enumerate(remaining)
            if incidence[edge_index, candidate_index]
        )
        if mask:
            raw_optional.append((edge_index, mask))
    raw_minimum_covers = 0
    for choice in combinations(raw_optional, 6):
        union = 0
        for _edge_index, mask in choice:
            union |= mask
        raw_minimum_covers += union == full
    require(raw_minimum_covers == 28, "raw minimum optional-edge cover census")
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
        "original_incidences": original_incidences,
        "retained_incidences": retained_incidences,
        "raw_minimum_covers": raw_minimum_covers,
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


def replay_record():
    points, candidates, incidence = exact_inputs()
    parent_digest = replay_parent_safety(points)
    supports = replay_relative_scope()
    proof = combinatorial_optimum(candidates, incidence)
    assignment = replay_exact_assignment(
        proof["selected"], proof["known"], candidates, incidence, points
    )
    mandatory_witnesses = [
        {
            "edge_index": edge,
            "charts": list(charts),
            "least_unique_factor_id": factor,
            "unique_factor_count": count,
        }
        for edge, charts, factor, count in proof["mandatory_rows"]
    ]
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
    expected = {
        "format": "diag3-pair-fullsupport-segment-cover-v1",
        "status": "EXACT_OPTIMAL_KNOWN_WALL_SEGMENT_COVER",
        "scope": {
            "parent_index": 2599,
            "support": [15, 15, 15],
            "source_bank": "105 exact strict-parent straight segments",
            "coverage_claim": "ONE_EXACT_RETAINED_WITNESS_FOR_EACH_OF_10844_CROSSED_FACTOR_CLASSES",
            "component_coverage": "NOT_CLAIMED",
            "global_parent_cell_coverage": "NOT_CLAIMED",
            "pair_branch_closed": False,
            "triple_branch_closed": False,
            "honest_9dvl_score": "2/9",
        },
        "inputs": {
            "point_bank_sha256": digest_file(transition.POINT_BANK),
            "factor_state_sha256": digest_file(transition.FACTOR_STATES),
            "factor_census_sha256": digest_file(transition.FACTOR_CENSUS),
            "factor_polynomial_source_sha256": digest_file(
                Path(labeled.__file__)
            ),
            "candidate_factor_sha256": digest_file(gate.CANDIDATES),
            "parent_catalog_sha256": digest_file(gate.CATALOG),
            "source_edge_bank_sha256": canonical_digest(
                [list(edge) for edge in safe.EDGES]
            ),
            "parent_sign_sha256": parent_digest,
            "component_cosheaf_pilot_sha256": digest_file(PILOT),
            "compactification_atlas_sha256": digest_file(ATLAS),
        },
        "trust_boundary": {
            "checkpoint_verifier": "SEPARATELY_WRITTEN_CHECKPOINT_LOGIC_WITH_SHARED_ACCEPTED_SOURCE_MODULES",
            "shared_accepted_dependencies": [
                "DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY.factor_polynomials",
                "diag3_pair_parent_source_transition_core.exact_inputs",
                "verify_diag2_canonical_robust_edges.evaluate",
                "verify_diag3_pair_fullsupport_safe_segment_walls.segment_power/positive_unit/EDGES",
                "verify_diag3_pair_global_parent_face_gate.parent_polynomials/parse_candidates",
            ],
            "upstream_exact_factor_state_replay": "PYTHONDONTWRITEBYTECODE=1 python ai/omreal/DIAG9_GRAPH_row2599_factor_states.py",
            "scope": "The checkpoint verifier independently reimplements cover optimality and record validation, but authenticates and consumes the accepted factor-state, point-bank, factor-polynomial, parent, and edge-bank sources rather than rederiving every source inside this verifier.",
        },
        "target_selection_audit": {
            "compactification": "(Delta^3)^3",
            "proper_relative_supports": 3_374,
            "unique_possibly_nonrelative_support": [15, 15, 15],
            "audited_pilot_supports": [list(row) for row in supports],
            "audited_stars": [
                "section-960 wall-(1,6) interior collision",
                "section-550 point-30 wall-21 endpoint tangency",
            ],
            "relative_chain_generator_contribution": 0,
            "decision": "RETAIN_AS_COMPILER_STRESS_TESTS_ONLY",
            "reason": (
                "Both stars lie wholly in proper product-simplex supports, hence "
                "inside the parent-boundary relative subspace; internal residual "
                "subdivision there generates zero in C_*(K,K_infinity)."
            ),
        },
        "source_bank": {
            "original_edges": 105,
            "known_crossed_factors": 10_844,
            "original_edge_factor_crossing_incidences": proof["original_incidences"],
            "selected_edges": 40,
            "retained_edge_factor_crossing_incidences": proof["retained_incidences"],
            "edge_reduction": 65,
            "edge_reduction_fraction": "13/21",
            "selected_edge_indices": list(proof["selected"]),
            "selected_chart_pairs": [
                list(safe.EDGES[index]) for index in proof["selected"]
            ],
            "known_factor_ids_sha256": digest_ids(
                b"diag3-fullsupport-known-crossed-factors-v1",
                (candidates[index] for index in np.where(proof["known"])[0]),
            ),
            "selected_crossing_assignment_sha256": sha256(
                repr(tuple(sorted(assignment.items()))).encode("ascii")
            ).hexdigest(),
        },
        "optimality": {
            "mandatory_edges": 34,
            "mandatory_edge_indices": proof["mandatory"],
            "mandatory_unique_factor_count": 49,
            "mandatory_coverage": 10_815,
            "mandatory_witnesses": mandatory_witnesses,
            "remaining_factor_count": 29,
            "remaining_factor_ids": [
                candidates[index] for index in proof["remaining"]
            ],
            "nonempty_optional_patterns": 21,
            "inclusion_maximal_optional_patterns": maximal_rows,
            "subsets_of_at_most_five_exhausted": sum(
                len(tuple(combinations(proof["maximal"], size)))
                for size in range(6)
            ),
            "covers_with_five_optional_patterns": 0,
            "minimum_optional_edges": 6,
            "six_maximal_pattern_cover_count": len(proof["solutions"]),
            "raw_six_edge_optional_cover_count": proof["raw_minimum_covers"],
            "canonical_optional_edge_indices": list(proof["optional"]),
            "proof": (
                "Unique-crossing factors force 34 distinct edges. Those edges "
                "leave 29 factors. Every optional edge is contained in one of "
                "seven maximal incidence patterns; exhaustive replay finds no "
                "cover using at most five patterns and three maximal-pattern "
                "covers using six. Direct raw-edge exhaustion finds 28 six-edge "
                "optional covers."
            ),
        },
        "decision": {
            "retired_as_proof_bearing_next_step": (
                "scale section-960/section-550 closure across the two proper supports"
            ),
            "retained_diagnostic": (
                "use the two stars only when a split/merge or endpoint-specialization "
                "compiler regression is specifically needed"
            ),
            "next_pair_action": (
                "continue labels and component/closure attachments on the exact "
                "40-edge full-support source cover, or replace it with a direct "
                "coverage-certified parent-cell roadmap"
            ),
            "supersedes_historical_next_action": (
                "DIAG3_COMPONENT_COSHEAF_PILOT.md section 'Evidence-selected next action'"
            ),
        },
        "theorem_effect": (
            "Removes 65 redundant edges from the exact known-wall source skeleton "
            "and prevents a proper-support diagnostic from being mistaken for a "
            "relative-chain advance. Global component coverage and the independent "
            "triple obligation remain open; honest 9DVL score remains 2/9."
        ),
    }
    expected["semantic_sha256"] = semantic_seal(expected)
    return expected


def verify_record(record):
    global _REPLAY_CACHE
    if _REPLAY_CACHE is None:
        _REPLAY_CACHE = replay_record()
    require(record == _REPLAY_CACHE, "full exact record/schema replay")
    require(
        record["semantic_sha256"] == semantic_seal(record),
        "full-record semantic seal",
    )


def reseal(record):
    """Seal a hostile record so rejection exercises semantics, not a stale hash."""
    record["semantic_sha256"] = semantic_seal(record)
    return record


def main():
    stored = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    verify_record(stored)
    mutations = []
    for path, value in (
        (("format",), "corrupted"),
        (("status",), "PROVED_DIAGONAL_THREE"),
        (("scope", "component_coverage"), "GLOBAL"),
        (("scope", "pair_branch_closed"), True),
        (("scope", "triple_branch_closed"), True),
        (
            ("scope", "coverage_claim"),
            "GLOBAL_PARENT_CELL_COMPONENT_COVERAGE",
        ),
        (("scope", "honest_9dvl_score"), "3/9"),
        (("target_selection_audit", "relative_chain_generator_contribution"), 1),
        (("target_selection_audit", "decision"), "SCALE_GLOBALLY"),
        (("target_selection_audit", "audited_stars"), []),
        (("target_selection_audit", "reason"), "Both stars prove a new chain."),
        (("source_bank", "selected_edges"), 39),
        (("source_bank", "selected_edge_indices"), []),
        (("source_bank", "selected_crossing_assignment_sha256"), "0" * 64),
        (("optimality", "mandatory_edges"), 33),
        (("optimality", "covers_with_five_optional_patterns"), 1),
        (("optimality", "minimum_optional_edges"), 5),
        (
            ("decision", "retired_as_proof_bearing_next_step"),
            "scale section-960/section-550 as a proof-bearing next step",
        ),
        (
            ("decision", "retained_diagnostic"),
            "use the stars as pair-branch generators",
        ),
        (
            ("theorem_effect",),
            "Diagonal three proved; archival honest score remains 2/9.",
        ),
    ):
        mutation = deepcopy(stored)
        target = mutation
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        mutations.append(reseal(mutation))
    stale_seal = deepcopy(stored)
    stale_seal["semantic_sha256"] = "0" * 64
    mutations.append(stale_seal)
    rejected = 0
    for mutation in mutations:
        try:
            verify_record(mutation)
        except AssertionError:
            rejected += 1
    require(rejected == len(mutations), "hostile mutation rejection")
    print("PASS all 105 source edges independently remain in the strict parent cell")
    print("PASS 34 forced edges cover 10,815/10,844 crossed factor classes")
    print("PASS seven maximal optional patterns exhaust the 29-factor residue")
    print("PASS no five-pattern cover; 3 maximal-pattern and 28 raw six-edge covers")
    print("PASS 412,093 original and 157,448 retained edge-factor incidences")
    print("PASS exact 40-edge cover is optimal; one exact endpoint witness per class")
    print("PASS both proposed proper-support stars generate zero relative chains")
    print(f"PASS {rejected}/{len(mutations)} hostile corruptions rejected")
    print("SCOPE source-skeleton compression only; global components and triple branch open; honest 9DVL 2/9")


if __name__ == "__main__":
    main()
