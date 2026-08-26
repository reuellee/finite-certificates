#!/usr/bin/env python3
"""Build an exact minimum cover of the known row-2599 wall crossings.

The source bank consists of the 105 already certified parent-safe segments.
This producer uses their exact endpoint factor signs to find the smallest
subbank retaining every one of the 10,844 certified full-support wall
crossings.  It also audits the theorem role of the latest proper-support
component-cosheaf target.
"""

from __future__ import annotations

from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUTPUT = DATA / "DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json"
PILOT = DATA / "DIAG3_COMPONENT_COSHEAF_PILOT.json"
ATLAS = DATA / "DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json"
FORMAT = "diag3-pair-fullsupport-segment-cover-v1"

sys.path.insert(0, str(HERE))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402
import verify_diag2_canonical_robust_edges as evaluator  # noqa: E402
import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def id_digest(domain: bytes, identifiers) -> str:
    payload = ",".join(map(str, sorted(identifiers))).encode("ascii")
    return sha256(domain + b"\0" + payload).hexdigest()


def load_signs():
    with np.load(transition.FACTOR_STATES, allow_pickle=False) as source:
        packed = np.asarray(source["chart_factor_sign_packed"], dtype=np.uint8)
    if packed.shape[0] != 178:
        raise AssertionError("row-2599 factor-state chart census changed")
    return np.unpackbits(packed, axis=1, bitorder="little")[:, :26_740]


def strict_parent_bank(points):
    records = [
        json.loads(line)
        for line in gate.CATALOG.read_text(encoding="utf-8").splitlines()
        if line
    ]
    parents, parent_digest = gate.parent_polynomials(records[gate.PARENT])
    for edge_index, (left, right) in enumerate(safe.EDGES):
        for label, target, polynomial, _terms in parents:
            restriction = [
                target * value
                for value in safe.segment_power(
                    polynomial, points[left], points[right]
                )
            ]
            if not safe.positive_unit(restriction):
                raise AssertionError(
                    f"parent bracket {label} failed on source edge {edge_index}"
                )
    return parent_digest


def exact_selected_crossings(selected, incidence, candidates, points, polynomials):
    witnesses = {}
    for candidate_index, factor_id in enumerate(candidates):
        edge_index = next(
            (
                edge
                for edge in selected
                if bool(incidence[edge, candidate_index])
            ),
            None,
        )
        if edge_index is None:
            continue
        left, right = safe.EDGES[edge_index]
        left_value = evaluator.evaluate(polynomials[factor_id], points[left])
        right_value = evaluator.evaluate(polynomials[factor_id], points[right])
        if left_value * right_value >= 0:
            raise AssertionError(
                f"packed sign crossing failed exact replay for factor {factor_id}"
            )
        witnesses[factor_id] = edge_index
    return witnesses


def relative_scope_audit():
    atlas = json.loads(ATLAS.read_text(encoding="utf-8"))
    pilot = json.loads(PILOT.read_text(encoding="utf-8"))
    divisors = {
        (int(row["moving_column"]), int(row["coordinate_row"])):
        str(row["parent_bracket"])
        for row in atlas["boundary_divisors"]
    }
    expected_keys = {
        (column, row)
        for column in (6, 7, 8)
        for row in (1, 2, 3, 4)
    }
    if set(divisors) != expected_keys:
        raise AssertionError("compactification boundary-divisor map changed")

    proper = 0
    full = []
    for support in product(range(1, 16), repeat=3):
        tags = {
            divisors[(6 + block, bit + 1)]
            for block, mask in enumerate(support)
            for bit in range(4)
            if not (mask >> bit) & 1
        }
        if tags:
            proper += 1
        else:
            full.append(support)
    if proper != 3_374 or full != [(15, 15, 15)]:
        raise AssertionError("relative support partition changed")

    supports = tuple(map(tuple, pilot["scope"]["pilot_supports"]))
    if supports != ((3, 1, 15), (3, 3, 7)):
        raise AssertionError("component-cosheaf pilot support scope changed")
    if any(support == (15, 15, 15) for support in supports):
        raise AssertionError("pilot unexpectedly acquired a nonrelative support")
    return {
        "compactification": "(Delta^3)^3",
        "proper_relative_supports": proper,
        "unique_possibly_nonrelative_support": list(full[0]),
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
    }


def build_record():
    matrices, points, _packed, _states, _hamming, _multiplicity = (
        transition.exact_inputs()
    )
    if matrices.shape != (178, 4, 8) or len(safe.EDGES) != 105:
        raise AssertionError("source bank census changed")
    parent_digest = strict_parent_bank(points)
    candidates = tuple(gate.parse_candidates())
    signs = load_signs()
    incidence = np.asarray(
        [
            signs[left, candidates] != signs[right, candidates]
            for left, right in safe.EDGES
        ],
        dtype=bool,
    )
    multiplicity = incidence.sum(axis=0)
    known = multiplicity > 0
    if int(known.sum()) != safe.EXPECTED_CROSSED:
        raise AssertionError("known wall-crossing census changed")

    mandatory = sorted(
        set(np.where(incidence[:, multiplicity == 1])[0].tolist())
    )
    mandatory_coverage = incidence[mandatory].any(axis=0)
    remaining_columns = np.where(known & ~mandatory_coverage)[0].tolist()
    if (
        len(mandatory) != 34
        or int(mandatory_coverage.sum()) != 10_815
        or len(remaining_columns) != 29
    ):
        raise AssertionError("mandatory-edge reduction changed")

    mandatory_witnesses = []
    for edge_index in mandatory:
        unique = [
            candidates[index]
            for index in np.where(
                incidence[edge_index] & (multiplicity == 1)
            )[0]
        ]
        if not unique:
            raise AssertionError("mandatory edge lacks a unique-factor witness")
        mandatory_witnesses.append(
            {
                "edge_index": edge_index,
                "charts": list(safe.EDGES[edge_index]),
                "least_unique_factor_id": min(unique),
                "unique_factor_count": len(unique),
            }
        )

    patterns = {}
    for edge_index in range(len(safe.EDGES)):
        if edge_index in mandatory:
            continue
        mask = sum(
            1 << position
            for position, candidate_index in enumerate(remaining_columns)
            if incidence[edge_index, candidate_index]
        )
        if mask:
            patterns.setdefault(mask, []).append(edge_index)
    maximal = [
        (min(edges), mask, tuple(edges))
        for mask, edges in patterns.items()
        if not any(
            mask != other and mask | other == other
            for other in patterns
        )
    ]
    maximal.sort()
    if len(patterns) != 21 or len(maximal) != 7:
        raise AssertionError("optional-edge pattern reduction changed")

    full = (1 << len(remaining_columns)) - 1
    covers_by_size = {}
    for size in range(len(maximal) + 1):
        solutions = []
        for choice in combinations(maximal, size):
            union = 0
            for _edge, mask, _equivalent in choice:
                union |= mask
            if union == full:
                solutions.append(tuple(edge for edge, _mask, _same in choice))
        covers_by_size[size] = solutions
        if solutions:
            break
    minimum_optional = next(size for size, rows in covers_by_size.items() if rows)
    if minimum_optional != 6 or len(covers_by_size[6]) != 3:
        raise AssertionError("optional cover optimum changed")
    canonical_optional = min(covers_by_size[minimum_optional])
    selected = tuple(sorted((*mandatory, *canonical_optional)))
    if len(selected) != 40 or not np.all(
        incidence[list(selected)].any(axis=0) == known
    ):
        raise AssertionError("selected source bank is not the exact known-wall cover")

    _types, _terms, polynomials = labeled.factor_polynomials()
    witnesses = exact_selected_crossings(
        selected, incidence, candidates, points, polynomials
    )
    if len(witnesses) != 10_844:
        raise AssertionError("selected edge bank lost an exact crossing")

    maximal_rows = []
    for representative, mask, equivalent in maximal:
        maximal_rows.append(
            {
                "representative_edge_index": representative,
                "equivalent_edge_indices": list(equivalent),
                "charts": list(safe.EDGES[representative]),
                "remaining_factor_ids": [
                    candidates[remaining_columns[position]]
                    for position in range(len(remaining_columns))
                    if mask >> position & 1
                ],
            }
        )

    semantic_payload = {
        "mandatory": mandatory,
        "remaining": [candidates[index] for index in remaining_columns],
        "maximal_patterns": maximal_rows,
        "canonical_optional": list(canonical_optional),
        "selected": list(selected),
    }
    semantic = sha256(
        json.dumps(
            semantic_payload, sort_keys=True, separators=(",", ":")
        ).encode("ascii")
    ).hexdigest()

    return {
        "format": FORMAT,
        "status": "EXACT_OPTIMAL_KNOWN_WALL_SEGMENT_COVER",
        "scope": {
            "parent_index": 2599,
            "support": [15, 15, 15],
            "source_bank": "105 exact strict-parent straight segments",
            "coverage_claim": "ALL_10844_ALREADY_CERTIFIED_FACTOR_ZERO_SETS",
            "component_coverage": "NOT_CLAIMED",
            "global_parent_cell_coverage": "NOT_CLAIMED",
            "pair_branch_closed": False,
            "triple_branch_closed": False,
            "honest_9dvl_score": "2/9",
        },
        "inputs": {
            "factor_state_sha256": file_sha256(transition.FACTOR_STATES),
            "candidate_factor_sha256": file_sha256(gate.CANDIDATES),
            "parent_sign_sha256": parent_digest,
            "component_cosheaf_pilot_sha256": file_sha256(PILOT),
            "compactification_atlas_sha256": file_sha256(ATLAS),
        },
        "target_selection_audit": relative_scope_audit(),
        "source_bank": {
            "original_edges": len(safe.EDGES),
            "known_crossed_factors": int(known.sum()),
            "selected_edges": len(selected),
            "edge_reduction": len(safe.EDGES) - len(selected),
            "edge_reduction_fraction": "13/21",
            "selected_edge_indices": list(selected),
            "selected_chart_pairs": [list(safe.EDGES[index]) for index in selected],
            "known_factor_ids_sha256": id_digest(
                b"diag3-fullsupport-known-crossed-factors-v1",
                (candidates[index] for index in np.where(known)[0]),
            ),
            "selected_crossing_assignment_sha256": sha256(
                repr(tuple(sorted(witnesses.items()))).encode("ascii")
            ).hexdigest(),
        },
        "optimality": {
            "mandatory_edges": len(mandatory),
            "mandatory_edge_indices": mandatory,
            "mandatory_unique_factor_count": int((multiplicity == 1).sum()),
            "mandatory_coverage": int(mandatory_coverage.sum()),
            "mandatory_witnesses": mandatory_witnesses,
            "remaining_factor_count": len(remaining_columns),
            "remaining_factor_ids": [
                candidates[index] for index in remaining_columns
            ],
            "nonempty_optional_patterns": len(patterns),
            "inclusion_maximal_optional_patterns": maximal_rows,
            "subsets_of_at_most_five_exhausted": sum(
                len(tuple(combinations(maximal, size))) for size in range(6)
            ),
            "covers_with_five_optional_patterns": 0,
            "minimum_optional_edges": minimum_optional,
            "six_pattern_cover_count": len(covers_by_size[6]),
            "canonical_optional_edge_indices": list(canonical_optional),
            "proof": (
                "Unique-crossing factors force 34 distinct edges. Those edges "
                "leave 29 factors. Every optional edge is contained in one of "
                "seven maximal incidence patterns; exhaustive replay finds no "
                "cover using at most five patterns and three covers using six."
            ),
        },
        "semantic_sha256": semantic,
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
        },
        "theorem_effect": (
            "Removes 65 redundant edges from the exact known-wall source skeleton "
            "and prevents a proper-support diagnostic from being mistaken for a "
            "relative-chain advance. Global component coverage and the independent "
            "triple obligation remain open; honest 9DVL score remains 2/9."
        ),
    }


def main():
    record = build_record()
    OUTPUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print("WROTE", OUTPUT)


if __name__ == "__main__":
    main()
