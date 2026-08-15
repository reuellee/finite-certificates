#!/usr/bin/env python3
"""Exact audit of the row-2599 labelled-closure globality gap.

The 178-chart certificate is a cover of extension *signatures*, not a cover
of the parent realization space.  This verifier reads only pinned exact
artifacts and proves the finite facts which prevent those records from being
decoded as a closure-complete regular master poset:

* the 178 generic factor-sign rows are pairwise distinct and no two are
  generic-wall adjacent (their minimum Hamming distance is 1,125);
* every stored slice/line/disk/node roadmap is sourced at chart zero;
* the complete line roadmap contributes 25 further chambers, but no second
  atlas chart, and has only its own 25 local incidences;
* the two long stress paths carry selected feasibility witnesses but no
  residual-wall event or closure ledger; and
* even every minimum-Hamming straight interpolation exits the parent cell,
  as certified by exact Sturm counts for the 70 parent brackets.

The companion JSON names the smallest proof-bearing object which is still
open: a coverage-certified compactified row-2599 master-cell universe with
its labelled strict closure pairs and triples.  A new deterministic CAD,
roadmap, or equivalent semialgebraic construction may produce that object;
this audit does not claim that the polynomial input makes construction
impossible.  It proves that the object is not already encoded by the point
bank and scoped roadmaps.
"""

from __future__ import annotations

import argparse
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, permutations
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
DEFAULT_MANIFEST = DATA / "DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json"

PINNED_SHA256 = {
    "seeat_parent2599_upper178.npz":
        "3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a",
    "DIAG9_GRAPH_global_factor_census.npz":
        "3984ce87e11fd59d804e59568177248e218cd1c7bb07aae0a9f9f746858728bc",
    "DIAG9_GRAPH_row2599_factor_states.npz":
        "f44b1fccfb4e61273aeceb8796a18098d82c48473e257556ce3d2a22f99b0bcf",
    "DIAG9_GRAPH_row2599_slice_roadmap.npz":
        "b982fdc600729306b545005ff059e2c6603b4603525745078fd85b630f36a575",
    "DIAG9_GRAPH_row2599_line_roadmap.npz":
        "29a4542941a322da6846fcfb2d7eb3d427ac9f7cc4becd95b4b5cd754f3ae16b",
    "DIAG9_GRAPH_row2599_disk_roadmap.npz":
        "8111a338e2169c4492ad0c5b7e03c9792d5c301c54f0f10a3ce20114db424486",
    "DIAG9_GRAPH_row2599_node_roadmap.npz":
        "ddec96b052b305d279b543be2af27e12f380f0dedc79ea434616c64b40cd8cea",
    "ninth_candidate_12_37_path.npz":
        "8db38e00d9bf8701558c27cd4ede3e024db8953ea3ef9873bf0b4fc65ad6bcda",
    "ninth_candidate_37_176_path.npz":
        "3c37c3c0d5de159bec9d48eeaaf57bccbe07c2f3aeb0ede9d4b1ddbae2bd3507",
}

EXPECTED_MINIMUM_PAIRS = (
    (36, 167),
    (163, 175),
    (164, 173),
    (165, 172),
    (166, 171),
    (169, 174),
)

# (left chart, right chart, parent brackets with an interior zero,
#  total distinct interior roots counted bracket-by-bracket).
EXPECTED_CLOSEST_SEGMENT_EXITS = (
    (36, 167, 38, 76),
    (163, 175, 38, 76),
    (164, 173, 38, 76),
    (165, 172, 38, 76),
    (166, 171, 38, 76),
    (169, 174, 32, 64),
)

EXPECTED_OBSERVATION_DIGEST = (
    "27e55460f7bb22f1ec278d67c7441fd06e6a455c32605d00a1bb57b294edf85b"
)

BASES = tuple(combinations(range(8), 4))
PERMUTATIONS = tuple(
    (
        permutation,
        -1
        if sum(
            permutation[left] > permutation[right]
            for left in range(4)
            for right in range(left + 1, 4)
        )
        & 1
        else 1,
    )
    for permutation in permutations(range(4))
)
BYTE_POPCOUNT = np.asarray([value.bit_count() for value in range(256)], dtype=np.uint8)


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def verify_pins() -> None:
    for name, expected in PINNED_SHA256.items():
        actual = file_sha256(DATA / name)
        if actual != expected:
            raise AssertionError(f"pinned artifact changed: {name}: {actual}")


def trim(polynomial):
    answer = list(map(Fraction, polynomial))
    while answer and not answer[-1]:
        answer.pop()
    return answer


def polynomial_add(left, right):
    answer = [Fraction(0)] * max(len(left), len(right))
    for index in range(len(answer)):
        answer[index] = (
            (left[index] if index < len(left) else 0)
            + (right[index] if index < len(right) else 0)
        )
    return trim(answer)


def polynomial_multiply(left, right):
    if not left or not right:
        return []
    answer = [Fraction(0)] * (len(left) + len(right) - 1)
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            answer[left_index + right_index] += left_value * right_value
    return trim(answer)


def polynomial_value(polynomial, value):
    answer = Fraction(0)
    for coefficient in reversed(polynomial):
        answer = answer * value + coefficient
    return answer


def polynomial_divrem(dividend, divisor):
    dividend = trim(dividend)
    divisor = trim(divisor)
    if not divisor:
        raise ZeroDivisionError
    while len(dividend) >= len(divisor):
        quotient = dividend[-1] / divisor[-1]
        shift = len(dividend) - len(divisor)
        for index, coefficient in enumerate(divisor):
            dividend[index + shift] -= quotient * coefficient
        dividend = trim(dividend)
    return dividend


def sturm_sequence(polynomial):
    polynomial = trim(polynomial)
    if len(polynomial) <= 1:
        return tuple(polynomial and (polynomial,))
    derivative = trim(
        index * polynomial[index] for index in range(1, len(polynomial))
    )
    sequence = [polynomial, derivative]
    while derivative:
        remainder = [-value for value in polynomial_divrem(polynomial, derivative)]
        if not remainder:
            break
        sequence.append(remainder)
        polynomial, derivative = derivative, remainder
    return tuple(sequence)


def sign_variations(sequence, value):
    signs = []
    for polynomial in sequence:
        evaluation = polynomial_value(polynomial, value)
        if evaluation:
            signs.append(1 if evaluation > 0 else -1)
    return sum(left != right for left, right in zip(signs, signs[1:]))


def root_count(polynomial, left=Fraction(0), right=Fraction(1)):
    if len(polynomial) <= 1:
        return 0
    if not polynomial_value(polynomial, left) or not polynomial_value(polynomial, right):
        raise AssertionError("a parent-bracket endpoint is degenerate")
    sequence = sturm_sequence(polynomial)
    return sign_variations(sequence, left) - sign_variations(sequence, right)


def affine_minor_polynomial(left, right, basis):
    """Exact det of the four selected columns of left+t(right-left)."""

    answer = []
    for permutation, sign in PERMUTATIONS:
        term = [Fraction(sign)]
        for row in range(4):
            column = basis[permutation[row]]
            constant = int(left[row, column])
            slope = int(right[row, column]) - constant
            term = polynomial_multiply(term, (constant, slope))
        answer = polynomial_add(answer, term)
    return tuple(answer)


def factor_state_audit():
    with np.load(DATA / "seeat_parent2599_upper178.npz", allow_pickle=False) as atlas:
        if str(atlas["format"].item()) != "seeat-parent2599-upper-cover-v1":
            raise AssertionError("wrong upper-cover format")
        if int(atlas["parent_index"].item()) != 2599:
            raise AssertionError("wrong upper-cover parent")
        charts = np.asarray(atlas["chart_matrix"], dtype=np.int64)
        assignment = np.asarray(atlas["assignment"], dtype=np.int64)
    if charts.shape != (178, 4, 8) or assignment.shape != (97_224,):
        raise AssertionError("wrong row-2599 point-bank shape")
    assignment_counts = np.bincount(assignment, minlength=178)
    if len(assignment_counts) != 178 or np.any(assignment_counts == 0):
        raise AssertionError("the stored signature assignment lost a chart")

    with np.load(
        DATA / "DIAG9_GRAPH_row2599_factor_states.npz", allow_pickle=False
    ) as states:
        if str(states["format"].item()) != "diag9-row2599-factor-state-sample-v1":
            raise AssertionError("wrong factor-state format")
        packed = np.asarray(states["chart_factor_sign_packed"], dtype=np.uint8)
        stored_hamming = np.asarray(states["chart_hamming"], dtype=np.int64)
        varied = np.asarray(states["varied_factor"], dtype=np.int64)
        chart_index = np.asarray(states["chart_index"], dtype=np.int64)
    if packed.shape != (178, 3343) or stored_hamming.shape != (178, 178):
        raise AssertionError("wrong factor-state array shape")
    # 26,740 coordinates leave four unused high bits in the final packed
    # byte.  Exclude padding from the independently recomputed distances.
    if np.any(packed[:, -1] & np.uint8(0xF0)):
        raise AssertionError("factor-state padding bits are nonzero")
    if not np.array_equal(chart_index, np.arange(178)):
        raise AssertionError("factor-state chart index is not canonical")
    if len({row.tobytes() for row in packed}) != 178:
        raise AssertionError("sample factor-sign states are no longer distinct")
    if varied.shape != (10_844,) or len(set(map(int, varied))) != 10_844:
        raise AssertionError("wrong varying-factor census")

    recomputed = np.zeros((178, 178), dtype=np.int64)
    for left in range(178):
        xor = np.bitwise_xor(packed[left], packed)
        recomputed[left] = BYTE_POPCOUNT[xor].sum(axis=1, dtype=np.int64)
    if not np.array_equal(recomputed, stored_hamming):
        raise AssertionError("stored chart Hamming matrix does not replay")
    off_diagonal = recomputed[np.triu_indices(178, 1)]
    minimum = int(off_diagonal.min())
    maximum = int(off_diagonal.max())
    minimum_pairs = tuple(
        tuple(map(int, row))
        for row in np.argwhere(np.triu(recomputed == minimum, 1))
    )
    if minimum != 1_125 or maximum != 5_600:
        raise AssertionError("sample factor-state distance range changed")
    if minimum_pairs != EXPECTED_MINIMUM_PAIRS:
        raise AssertionError(f"minimum-distance pairs changed: {minimum_pairs}")
    if np.any(off_diagonal <= 1):
        raise AssertionError("a point-bank pair unexpectedly became wall-adjacent")
    if int(recomputed[0, 1:].min()) != 1_197:
        raise AssertionError("chart-zero separation changed")
    return charts, assignment_counts, recomputed, minimum_pairs


def occurrence_factor_lookup():
    with np.load(
        DATA / "DIAG9_GRAPH_global_factor_census.npz", allow_pickle=False
    ) as certificate:
        if str(certificate["format"].item()) != "diag9-global-residual-factor-census-v1":
            raise AssertionError("wrong global-factor format")
        foursets = np.asarray(certificate["occurrence_fourset"], dtype=np.uint8)
        factors = np.asarray(certificate["occurrence_factor"], dtype=np.int64)
        offsets = np.asarray(certificate["factor_offset"], dtype=np.int64)
    if foursets.shape != (84_840, 4) or factors.shape != (84_840,):
        raise AssertionError("wrong global-factor occurrence universe")
    if offsets.shape != (26_741,):
        raise AssertionError("wrong global-factor fingerprint universe")
    answer = {
        tuple(map(int, fourset)): int(factor)
        for fourset, factor in zip(foursets, factors, strict=True)
    }
    if len(answer) != 84_840:
        raise AssertionError("duplicate residual occurrence four-set")
    return answer


def local_roadmap_audit():
    formats = {
        "slice": "diag9-row2599-r2c7-slice-v1",
        "line": "diag9-row2599-r2c7-line-v1",
        "disk": "diag9-row2599-r2c7-r1c7-disk-v1",
        "node": "diag9-row2599-transverse-node-v1",
    }
    source_charts = {}
    for name, expected_format in formats.items():
        with np.load(
            DATA / f"DIAG9_GRAPH_row2599_{name}_roadmap.npz", allow_pickle=False
        ) as certificate:
            if str(certificate["format"].item()) != expected_format:
                raise AssertionError(f"wrong {name} roadmap format")
            if int(certificate["parent_index"].item()) != 2599:
                raise AssertionError(f"wrong {name} parent")
            source_charts[name] = int(certificate["source_chart"].item())
            if any(
                key in certificate.files
                for key in (
                    "global_cell_id",
                    "global_closure_pair",
                    "global_closure_triple",
                    "parent_infinity_cell",
                )
            ):
                raise AssertionError(f"{name} unexpectedly changed to a global atlas")
    if set(source_charts.values()) != {0}:
        raise AssertionError(f"local roadmaps gained a second source: {source_charts}")

    factor_lookup = occurrence_factor_lookup()
    with np.load(
        DATA / "DIAG9_GRAPH_row2599_line_roadmap.npz", allow_pickle=False
    ) as line:
        offsets = np.asarray(line["wall_offset"], dtype=np.int64)
        foursets = np.asarray(line["wall_fourset"], dtype=np.uint8)
        box_lo_num = np.asarray(line["box_lo_num"], dtype=np.int64)
        box_lo_den = np.asarray(line["box_lo_den"], dtype=np.int64)
        box_hi_num = np.asarray(line["box_hi_num"], dtype=np.int64)
        box_hi_den = np.asarray(line["box_hi_den"], dtype=np.int64)
        cell_tope = np.asarray(line["cell_tope"], dtype=np.uint64)
    if offsets.shape != (26,) or offsets[0] != 0 or offsets[-1] != 89:
        raise AssertionError("wrong complete-line wall offsets")
    if cell_tope.shape != (26, 26_112):
        raise AssertionError("wrong complete-line chamber table")
    line_factors = []
    for index in range(25):
        group = {
            factor_lookup[tuple(map(int, row))]
            for row in foursets[offsets[index]:offsets[index + 1]]
        }
        if len(group) != 1:
            raise AssertionError("one line crossing has multiple primitive factors")
        line_factors.append(next(iter(group)))
    if len(set(line_factors)) != 25:
        raise AssertionError("complete line crosses one primitive factor twice")
    boxes = tuple(
        (
            Fraction(int(lo_num), int(lo_den)),
            Fraction(int(hi_num), int(hi_den)),
        )
        for lo_num, lo_den, hi_num, hi_den in zip(
            box_lo_num, box_lo_den, box_hi_num, box_hi_den, strict=True
        )
    )
    if any(not left < right for left, right in boxes):
        raise AssertionError("a complete-line root box is reversed")
    if any(left <= 0 <= right for left, right in boxes):
        raise AssertionError("chart zero lies in a complete-line wall box")
    zero_cell = sum(right < 0 for _left, right in boxes)
    if zero_cell != 11:
        raise AssertionError("chart zero moved to another complete-line cell")
    # Every line cell is at distance at most max(11,14)=14 from chart zero,
    # whereas every other stored atlas chart is at distance at least 1,197.
    # Hence only chart zero occurs among these 26 exact line chambers.
    maximum_line_distance_from_chart_zero = max(zero_cell, 25 - zero_cell)
    if maximum_line_distance_from_chart_zero >= 1_197:
        raise AssertionError("line/point separation argument lost its strict gap")
    known_chamber_lower_bound = 178 + 25
    return source_charts, tuple(line_factors), zero_cell, known_chamber_lower_bound


def path_audit():
    expected = {
        "ninth_candidate_12_37_path.npz": (12, 37),
        "ninth_candidate_37_176_path.npz": (37, 176),
    }
    endpoints = []
    forbidden = {
        "factor_root",
        "factor_id",
        "wall_fourset",
        "cell_tope",
        "closure_pair",
        "closure_triple",
        "infinity_cell",
    }
    for name, expected_endpoint in expected.items():
        with np.load(DATA / name, allow_pickle=False) as certificate:
            endpoint = tuple(map(int, certificate["endpoint"]))
            if endpoint != expected_endpoint:
                raise AssertionError(f"stress-path endpoint changed: {name}")
            if set(certificate.files) & forbidden:
                raise AssertionError(f"stress path unexpectedly gained closure data: {name}")
            if np.asarray(certificate["signature"]).shape != (9,):
                raise AssertionError(f"stress path lost its selected nine colors: {name}")
        endpoints.append(endpoint)
    return tuple(endpoints)


def closest_segment_audit(charts, minimum_pairs):
    answer = []
    for left_index, right_index in minimum_pairs:
        left = charts[left_index]
        right = charts[right_index]
        bracket_roots = []
        for basis in BASES:
            polynomial = affine_minor_polynomial(left, right, basis)
            left_value = polynomial_value(polynomial, Fraction(0))
            right_value = polynomial_value(polynomial, Fraction(1))
            if left_value * right_value <= 0:
                raise AssertionError("minimum-pair endpoints leave parent 2599")
            count = root_count(polynomial)
            if count:
                bracket_roots.append(count)
        answer.append(
            (left_index, right_index, len(bracket_roots), sum(bracket_roots))
        )
    answer = tuple(answer)
    if answer != EXPECTED_CLOSEST_SEGMENT_EXITS:
        raise AssertionError(f"closest straight-segment audit changed: {answer}")
    return answer


def observations():
    charts, assignment_counts, hamming, minimum_pairs = factor_state_audit()
    source_charts, line_factors, zero_cell, chamber_lower_bound = local_roadmap_audit()
    endpoints = path_audit()
    exits = closest_segment_audit(charts, minimum_pairs)
    off_diagonal = hamming[np.triu_indices(178, 1)]
    return {
        "parent_index": 2599,
        "atlas_chart_count": 178,
        "atlas_assignment_count": 97_224,
        "atlas_assignment_nonempty_chart_count": int(np.count_nonzero(assignment_counts)),
        "residual_factor_count": 26_740,
        "varying_factor_count_on_sample": 10_844,
        "distinct_sample_factor_sign_states": 178,
        "sample_hamming_minimum": int(off_diagonal.min()),
        "sample_hamming_maximum": int(off_diagonal.max()),
        "sample_hamming_zero_or_one_pairs": int(np.count_nonzero(off_diagonal <= 1)),
        "minimum_hamming_pairs": [list(pair) for pair in minimum_pairs],
        "chart_zero_minimum_other_hamming": int(hamming[0, 1:].min()),
        "local_roadmap_source_charts": source_charts,
        "complete_line_cell_count": 26,
        "complete_line_wall_count": 25,
        "complete_line_source_cell": zero_cell,
        "complete_line_distinct_factor_count": len(set(line_factors)),
        "known_generic_chamber_lower_bound_after_line": chamber_lower_bound,
        "stress_path_endpoints": [list(endpoint) for endpoint in endpoints],
        "stress_path_selected_signature_count_each": 9,
        "minimum_hamming_straight_segment_parent_exits": [
            {
                "left_chart": left,
                "right_chart": right,
                "parent_brackets_with_internal_zero": brackets,
                "total_internal_parent_bracket_roots": roots,
            }
            for left, right, brackets, roots in exits
        ],
        "certified_adjacency_edges_between_distinct_atlas_charts": 0,
        "certified_parent_infinity_cells": 0,
        "certified_global_strict_closure_pairs": 0,
        "certified_global_strict_closure_triples": 0,
    }


def canonical_digest(value) -> str:
    encoded = json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("ascii")
    return sha256(encoded).hexdigest()


def verify_manifest(path: Path, observed) -> dict:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("format") != "diag3-pair-global-closure-open-object-v1":
        raise AssertionError("wrong closure-gap manifest format")
    if payload.get("status") != "OPEN":
        raise AssertionError("closure gap was marked closed without a candidate")
    if payload.get("relevant_commit") != "dcdc3f809758bce15ebd20e580c9f27d9ad699a9":
        raise AssertionError("closure-gap source commit changed")
    if payload.get("observations") != observed:
        raise AssertionError("machine-readable observations do not replay")
    digest = canonical_digest(observed)
    if payload.get("observation_digest") != digest:
        raise AssertionError("manifest observation digest changed")
    if EXPECTED_OBSERVATION_DIGEST is not None and digest != EXPECTED_OBSERVATION_DIGEST:
        raise AssertionError(f"pinned closure-gap observations changed: {digest}")
    open_object = payload.get("smallest_open_object", {})
    if open_object.get("id") != "row2599_compactified_labelled_order2_v1":
        raise AssertionError("smallest open object changed")
    if open_object.get("first_missing_block") != "coverage_certified_global_cell_universe":
        raise AssertionError("first missing global block changed")
    preflight = payload.get("global_generator_preflight", {})
    if (
        preflight.get("status") != "NO_COVERAGE_GENERATOR_OR_COMPACTIFICATION_ATLAS"
        or preflight.get("universal_residual_factor_count") != 26_740
        or preflight.get("row2599_certified_empty_factor_count") != 8_916
        or preflight.get("row2599_candidate_factor_count") != 17_824
        or preflight.get("inventory_verifier")
        != "ai/omreal/DIAG9_GRAPH_inventory.py"
        or preflight.get("empty_wall_verifier")
        != "ai/omreal/verify_diag9_active_sector.py"
        or preflight.get("hostile_temporary_dependency_replay") != {
            "diagnostic_only": True,
            "python": "3.12.13",
            "sympy": "1.13.3",
            "mpmath": "1.3.0",
            "result": "PASS 8916 certified-empty and 17824 candidate row-2599 factors",
        }
    ):
        raise AssertionError("global generator preflight changed")
    local_d3 = payload.get("row2599_flow_triangle_mixed_d3", {})
    if local_d3.get("status") != "OPEN":
        raise AssertionError("row2599 mixed d3 was marked closed without a cell")
    if local_d3.get("primitive_required_d3_column") != [-1, 1, 1, 1, 1, 1, 1]:
        raise AssertionError("row2599 primitive d3 column changed")
    if local_d3.get("certified_boundary_faces") != [
        "T", "S01", "S12", "S20", "H0", "H1", "H2"
    ]:
        raise AssertionError("row2599 flow-triangle boundary basis changed")
    comparisons = local_d3.get("comparison_incidences", [])
    expected_comparison_status = {
        "S01_to_common_ray": (
            "SINGULAR_COMPARISON_PRISM_CERTIFIED_WITH_NAMED_LATERALS"
        ),
        "S12_to_common_ray": (
            "SINGULAR_COMPARISON_PRISM_CERTIFIED_WITH_NAMED_LATERALS"
        ),
        "S20_to_common_ray": (
            "SINGULAR_COMPARISON_PRISM_CERTIFIED_WITH_NAMED_LATERALS"
        ),
        "H0_to_common_ray": "MISSING",
        "H1_to_common_ray": "MISSING",
        "H2_to_common_ray": (
            "SINGULAR_COMPARISON_PRISM_CERTIFIED_WITH_LITERAL_PAIR_LATERALS"
        ),
    }
    if (
        len(comparisons) != 6
        or {record.get("id"): record.get("status") for record in comparisons}
        != expected_comparison_status
        or local_d3.get("certified_comparison_incidence_count") != 4
        or local_d3.get("certified_relative_pair_wall_collar_count") != 3
        or local_d3.get("required_comparison_incidence_count") != 6
        or local_d3.get("certified_mixed_d3_cell_count") != 0
    ):
        raise AssertionError("row2599 mixed comparison ledger changed")
    ray = local_d3.get("certified_common_proper_ray", {})
    if (
        ray.get("direction") != [81, -262, 91, 86]
        or ray.get("endpoint_parameter") != [23_597_311, 105_015_122]
        or ray.get("relative_endpoint") != "parent:2467"
        or ray.get("mathematical_role")
        != "proper local H_c^0/component generator, not a d3 cell"
    ):
        raise AssertionError("row2599 common proper-ray record changed")
    bounded = local_d3.get("bounded_tapered_cube_checkpoint", {})
    if (
        bounded.get("status")
        != "EXACT_POSITIVE_BUT_NOT_A_COMPARISON_INCIDENCE"
        or bounded.get("root_endpoint_parameters") != [
            [1_221_971_981, 1_769_366_234],
            [42_214_994, 2_183_619_501],
            [425_791_163, 1_286_992_887],
        ]
        or bounded.get("ordered_root_pairs") != [
            [0, 2], [2, 0], [0, 1], [1, 0], [1, 2], [2, 1]
        ]
        or len(bounded.get("uncertified_statements", [])) != 3
        or bounded.get("verifiers") != [
            "ai/omreal/verify_diag3_row2599_common_proper_escape.py",
            "ai/omreal/review_scratch/DIAG3_HOSTILE_VERIFY_ROW2599_ORDERED_SECTOR_ROADMAP.py",
        ]
        or bounded.get("ordered_sector_semantic_digest")
        != "5941481177b36052e3e59bf08fa44cddadaa415fe761e091a2e8d8b2299ffc1c"
    ):
        raise AssertionError("row2599 bounded tapered-cube record changed")
    falsified = local_d3.get("falsified_common_root_shortcut", {})
    if (
        falsified.get("candidate_root") != [1, 3, 1]
        or falsified.get("status") != "FALSE_FOR_THE_FIXED_BLOCK1_WITNESS"
        or falsified.get("transport_alpha_conflict") != [
            {"derived_row_index": 30, "label": "167", "alpha": -1},
            {"derived_row_index": 35, "label": "128", "alpha": 1},
        ]
    ):
        raise AssertionError("row2599 false-common-root regression changed")
    tangent_collar = local_d3.get("p01_tangent_collar", {})
    if (
        tangent_collar.get("status")
        != "RELATIVE_PAIR_WALL_COLLAR_CERTIFIED_BUT_FULL_INCIDENCE_MISSING"
        or tangent_collar.get("verifier")
        != "ai/omreal/verify_diag3_row2599_p01_tangent_collar.py"
        or tangent_collar.get("semantic_digest")
        != "e3df18c1a98ccca9e022832e3656c7e2ae3a9c7c822a153c7fc40e9519e08016"
        or tangent_collar.get("independent_verifier")
        != "ai/omreal/review_scratch/DIAG3_HOSTILE_VERIFY_ROW2599_P01_TANGENT_COLLAR.py"
        or tangent_collar.get("independent_semantic_digest")
        != "82dda129bef8f52ce4c41fbc8b31e9a316419953bb89a9eaaf8983f9ab1379f8"
        or tangent_collar.get("incident_blocks") != [0, 1]
        or tangent_collar.get("offplane_entry")
        != {"row_zero_based": 0, "column_label": 6}
        or tangent_collar.get("tangent_advance") != [9, 160]
        or len(tangent_collar.get("stages", [])) != 4
        or len(tangent_collar.get("certified_statements", [])) != 6
    ):
        raise AssertionError("row2599 p01 tangent-collar record changed")
    comparison_prism = local_d3.get("p01_comparison_prism", {})
    if (
        comparison_prism.get("status")
        != "SINGULAR_COMPARISON_PRISM_CERTIFIED_WITH_NAMED_LATERALS"
        or comparison_prism.get("verifier")
        != "ai/omreal/verify_diag3_row2599_p01_comparison_prism.py"
        or comparison_prism.get("semantic_digest")
        != "0b015361e1c75007f025e90921fa5f295616b0e3e8d4bbf941e5161545e433c7"
        or comparison_prism.get("independent_verifier")
        != "ai/omreal/review_scratch/DIAG3_HOSTILE_VERIFY_ROW2599_P01_COMPARISON_PRISM.py"
        or comparison_prism.get("independent_semantic_digest")
        != "acca3573a369139c9a142592febcaa55ce453eeb10c1d52631ac5b226129127b"
        or comparison_prism.get("patch_count") != 5
        or comparison_prism.get("incident_blocks") != [0, 1]
        or comparison_prism.get("ordinary_boundary")
        != {"K(p01)": 1, "Q(p01,block0)": -1, "Q(p01,block1)": 1}
        or comparison_prism.get("relative_collar_face_count") != 5
        or comparison_prism.get("internal_face_pair_count") != 4
        or comparison_prism.get("collapsed_relative_endpoint_face_count") != 2
        or len(comparison_prism.get("certified_statements", [])) != 6
    ):
        raise AssertionError("row2599 p01 comparison-prism record changed")
    pair_prisms = local_d3.get("p12_p20_comparison_prisms", {})
    if (
        pair_prisms.get("status")
        != "TWO_SINGULAR_COMPARISON_PRISMS_CERTIFIED_WITH_NAMED_LATERALS"
        or pair_prisms.get("verifier")
        != "ai/omreal/verify_diag3_row2599_p12_p20_comparison_prisms.py"
        or pair_prisms.get("semantic_digest")
        != "48871bfbc021051f4f672eaf6372ecd5d1d0f0324005648b8d471e130b60e8f8"
        or pair_prisms.get("independent_verifier")
        != "ai/omreal/review_scratch/DIAG3_HOSTILE_VERIFY_ROW2599_P12_P20_COMPARISON_PRISMS.py"
        or pair_prisms.get("independent_semantic_digest")
        != "930d28e2fbc1990cb68e403b034b3ec7aa440a455b5017a13aa1426e1336dba4"
        or pair_prisms.get("patches_per_prism") != 2
        or pair_prisms.get("ordinary_boundaries") != {
            "p12": {"K(p12)": 1, "Q(p12,block1)": -1, "Q(p12,block2)": 1},
            "p20": {"K(p20)": 1, "Q(p20,block2)": -1, "Q(p20,block0)": 1},
        }
    ):
        raise AssertionError("row2599 p12/p20 comparison-prism record changed")
    h2_prism = local_d3.get("h2_comparison_prism", {})
    if (
        h2_prism.get("status")
        != "SINGULAR_COMPARISON_PRISM_CERTIFIED_WITH_LITERAL_PAIR_LATERALS"
        or h2_prism.get("verifier")
        != "ai/omreal/verify_diag3_row2599_h2_comparison_prism.py"
        or h2_prism.get("semantic_digest")
        != "4027e41a519953200e205f4e7ab2453a83122822d6ca2ed60bb649cd60afc7a7"
        or h2_prism.get("independent_verifier")
        != "ai/omreal/review_scratch/DIAG3_HOSTILE_VERIFY_ROW2599_H2_COMPARISON_PRISM.py"
        or h2_prism.get("independent_semantic_digest")
        != "55539702e53abdcf15a1173a549699d87427f85881d66db881ff33c98586934b"
        or h2_prism.get("patch_count") != 4
        or h2_prism.get("incident_block") != 2
        or h2_prism.get("ordinary_boundary")
        != {"K(h2)": 1, "Q(p12,block2)": -1, "Q(p20,block2)": 1}
        or h2_prism.get("literal_pair_laterals")
        != ["Q(p12,block2)", "Q(p20,block2)"]
    ):
        raise AssertionError("row2599 H2 comparison-prism record changed")
    wall_collar = local_d3.get("parent_wall_collar_attempt", {})
    if (
        wall_collar.get("status") != "FALSE_AS_A_THREE_EDGE_COMMON_COSPAN"
        or wall_collar.get("successful_edges") != ["p12", "p20"]
        or wall_collar.get("exceptional_edge") != "p01"
        or wall_collar.get("p01_source_wall") != "1234"
        or wall_collar.get("p01_critical_parameters") != {
            "block0_witness_wall": [
                83_503_134_767_238_851_186_305_349_765_512_866,
                43_552_580_189_648_394_406_194_000_441_042_241,
            ],
            "first_additional_parent_corner_1367": [
                3_797_676_243_957_714,
                1_934_663_274_435_289,
            ],
            "fixed_root_target_2467": [
                150_232_380_670_800_142_796_191_902,
                36_368_055_566_722_865_061_946_027,
            ],
        }
        or wall_collar.get("exact_block0_good_point") != {
            "common_parameter": [
                6_927_675_939_086_631_471_463_822_597_403_349_151_993_134,
                3_570_727_927_424_046_863_174_470_630_365_553_354_928_359,
            ],
            "strict_tope_covector": [10_000, 177, -7_015, 368],
            "minimum_signed_dot": 5_966_575,
        }
        or wall_collar.get("later_relative_corner") != {
            "walls": ["1234", "1367", "2467"],
            "root_parameter": [74_520_518_780_897, 5_145_156_267_709_928],
            "block0_strict_two_circuit": ["136", "167"],
        }
    ):
        raise AssertionError("row2599 parent-wall collar audit changed")
    resume = payload.get("resumption", {})
    expected_command = (
        "PYTHONDONTWRITEBYTECODE=1 python "
        "ai/omreal/verify_diag3_pair_global_closure_gap.py --manifest "
        "ai/omreal/data/DIAG3_PAIR_GLOBAL_CLOSURE_OPEN_OBJECT.json"
    )
    if resume.get("command") != expected_command:
        raise AssertionError("resumption command changed")
    expected_dependency_command = (
        "python -m pip install --target /tmp/diag3_sympy_1_13_3 sympy==1.13.3 "
        "&& PYTHONPATH=/tmp/diag3_sympy_1_13_3 PYTHONDONTWRITEBYTECODE=1 "
        "python ai/omreal/verify_diag9_active_sector.py"
    )
    if resume.get("dependency_preflight_command") != expected_dependency_command:
        raise AssertionError("global generator dependency preflight changed")
    return payload


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument(
        "--json", action="store_true", help="print the replayed observations as JSON"
    )
    args = parser.parse_args()

    verify_pins()
    observed = observations()
    payload = verify_manifest(args.manifest, observed)
    digest = canonical_digest(observed)
    if args.json:
        print(json.dumps(observed, indent=2, sort_keys=True))
    print("PASS pinned row2599 point/local/path inventory")
    print(
        "PASS 178 sampled chambers have zero generic adjacency pairs; Hamming range",
        observed["sample_hamming_minimum"],
        observed["sample_hamming_maximum"],
    )
    print(
        "PASS all six minimum-Hamming straight segments exit parent 2599",
        [
            (row["parent_brackets_with_internal_zero"], row["total_internal_parent_bracket_roots"])
            for row in observed["minimum_hamming_straight_segment_parent_exits"]
        ],
    )
    print(
        "PASS scoped roadmaps all source chart zero; complete line raises the exact",
        "generic-chamber lower bound to",
        observed["known_generic_chamber_lower_bound_after_line"],
    )
    print("OBSERVATION_DIGEST", digest)
    print(
        "OPEN",
        payload["smallest_open_object"]["id"],
        payload["smallest_open_object"]["first_missing_block"],
    )
    preflight = payload["global_generator_preflight"]
    print(
        "PASS global generator preflight: row2599 candidate walls",
        preflight["row2599_candidate_factor_count"],
        "after",
        preflight["row2599_certified_empty_factor_count"],
        "certified-empty walls; compactification atlas/export still missing",
    )
    local_d3 = payload["row2599_flow_triangle_mixed_d3"]
    print(
        "OPEN row2599 mixed d3:",
        len(local_d3["certified_boundary_faces"]),
        "boundary faces + one proper ray;",
        local_d3["certified_comparison_incidence_count"],
        "of",
        local_d3["required_comparison_incidence_count"],
        "comparison incidences certified",
    )
    print(
        "PASS bounded sectors, H0 cap, and witness cospan recorded;",
        "mixed base-space filler remains open",
    )
    wall_collar = local_d3["parent_wall_collar_attempt"]
    print(
        "PASS all three relative pair collars and all three pair-edge comparison prisms pinned; direct p01 wall slide false at",
        wall_collar["p01_critical_parameters"]["block0_witness_wall"],
        "with exact good covector",
        wall_collar["exact_block0_good_point"]["strict_tope_covector"],
    )
    print("PASS false common-root transport-alpha conflict pinned at rows 30/35")
    print("RESUME", payload["resumption"]["command"])
    print(
        "SCOPE the exact factor polynomials can seed a new deterministic CAD or roadmap; "
        "no unique/global regular closure poset is encoded by the existing records"
    )


if __name__ == "__main__":
    main()
