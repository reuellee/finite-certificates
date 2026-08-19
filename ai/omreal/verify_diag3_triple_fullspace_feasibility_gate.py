#!/usr/bin/env python3
"""Dependency-free fail-closed gate for the canonical hard triple upgrade.

The existing exact certificate studies a five-variable pinned concurrence
curve.  This checker distinguishes that system from both valid full-space
presentations: three equations in a nine-variable parent chart, or four
bilinear equations in the ten-variable concurrence chart.  It recomputes the
coordinate-height determinantal counts, pins the slice CAS ring, verifies the
named-to-canonical S8 factor map, and rejects a slice-to-orbit promotion until
the full critical census and frontier attachments exist.
"""

from __future__ import annotations

import hashlib
from itertools import combinations
import json
from math import comb
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / "data"))

import DIAG3_concurrence_ramification_rur as certificate  # noqa: E402
import verify_diag3_concurrence_normal_form as concurrence  # noqa: E402


MANIFEST = HERE / "data/DIAG3_triple_fullspace_feasibility_gate.json"
MSOLVE = HERE / "data/DIAG3_concurrence_ramification_complete.msolve"
SCHEMA = "diag3-triple-fullspace-feasibility-gate-v1"
PRESENTATION = (5_563, 16_134, 19_284)
CANONICAL = (5_563, 4_373, 23_221)
PERMUTATION = (6, 2, 5, 8, 3, 4, 1, 7)
EXPECTED_IMAGE = (4_373, 5_563, 23_221)
EXPECTED_SEMANTIC = "874c4895ae17843c6827c1c3a8d528eac0b45fc35dedc9159e4f447786ed2ace"


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def verify_factor_map():
    occurrences, occurrence_factor, _polynomials = (
        concurrence.labeled.factor_polynomials()
    )
    factor_occurrence = concurrence.labeled.factor_action_is_well_defined(
        occurrences, occurrence_factor
    )
    mapping = concurrence.labeled.triple_map(
        tuple(label - 1 for label in PERMUTATION)
    )
    image = tuple(
        concurrence.labeled.transform_factor(
            factor, mapping, factor_occurrence, occurrence_factor
        )
        for factor in PRESENTATION
    )
    if image != EXPECTED_IMAGE or set(image) != set(CANONICAL):
        raise AssertionError(f"named-to-canonical factor map changed: {image}")
    return image


def verify_msolve_ring(manifest):
    lines = MSOLVE.read_text(encoding="ascii").splitlines()
    variables = tuple(lines[0].split(","))
    expected = (
        "vr", "vs", "wr", "ws", "sat", "denominator_saturation", "t"
    )
    if variables != expected or lines[1] != "0":
        raise AssertionError(f"pinned slice CAS ring changed: {variables}")
    equations = lines[2:]
    if len(equations) != 7 or any(
        not line.endswith(",") for line in equations[:-1]
    ):
        raise AssertionError("pinned slice CAS equation census changed")
    stored = manifest["existing_slice"]
    if len(variables) != stored["msolve_variables"]:
        raise AssertionError("manifest slice variable count changed")
    if len(equations) != stored["msolve_equations"]:
        raise AssertionError("manifest slice equation count changed")
    if tuple(stored["msolve_inverse_variables"]) != variables[4:6]:
        raise AssertionError("manifest slice inverse variables changed")
    if len(certificate.SYSTEM) != 5:
        raise AssertionError("stored slice RUR system count changed")
    if any(
        len(monomial) != 5
        for polynomial in certificate.SYSTEM
        for monomial, _coefficient in polynomial
    ):
        raise AssertionError("stored RUR is no longer five-variable")
    return variables, len(equations)


def verify_dimension_gate(manifest):
    factor = manifest["full_factor_chart"]
    concurrence_chart = manifest["full_concurrence_chart"]
    slice_chart = manifest["existing_slice"]

    expected_factor = {
        "variables": 9,
        "equations": 3,
        "expected_dimension": 6,
        "coordinate_height_kernel_columns": 8,
        "coordinate_height_rank_minors": comb(8, 3),
    }
    for key, value in expected_factor.items():
        if factor[key] != value:
            raise AssertionError(f"full factor-chart count changed: {key}")

    expected_concurrence = {
        "variables": 10,
        "equations": 4,
        "expected_dimension": 6,
        "jacobian_columns": 10,
        "jacobian_maximal_minors": comb(10, 4),
        "coordinate_height_kernel_columns": 9,
        "coordinate_height_rank_minors": comb(9, 4),
        "all_six_base_height_tests": 6 * comb(9, 4),
    }
    for key, value in expected_concurrence.items():
        if concurrence_chart[key] != value:
            raise AssertionError(f"full concurrence-chart count changed: {key}")

    expected_slice = {
        "geometric_variables": 5,
        "geometric_equations": 4,
        "geometric_dimension": 1,
        "fixed_base_coordinates": 5,
        "ramification_minors": 1,
    }
    for key, value in expected_slice.items():
        if slice_chart[key] != value:
            raise AssertionError(f"pinned-slice count changed: {key}")

    # Materialize the column subsets rather than trusting only the binomial
    # formula.  A coordinate-height rank drop uses all maximal minors that
    # exclude the height column.
    factor_minors = tuple(combinations(range(8), 3))
    concurrence_minors = tuple(combinations(range(9), 4))
    if len(factor_minors) != 56 or len(concurrence_minors) != 126:
        raise AssertionError("coordinate-height minor enumeration changed")
    return len(factor_minors), len(concurrence_minors)


def main():
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if manifest["schema"] != SCHEMA:
        raise AssertionError("full-space gate schema changed")
    if tuple(manifest["named_presentation"]) != PRESENTATION:
        raise AssertionError("named presentation changed")
    if tuple(manifest["canonical_row"]) != CANONICAL:
        raise AssertionError("canonical row changed")

    sources = {
        "verify_diag3_concurrence_normal_form.py": HERE
        / "verify_diag3_concurrence_normal_form.py",
        "DIAG3_CONCURRENCE_NORMAL_FORM.md": HERE
        / "DIAG3_CONCURRENCE_NORMAL_FORM.md",
        "verify_diag3_triple_concurrence_local_fold_cell.py": HERE
        / "verify_diag3_triple_concurrence_local_fold_cell.py",
        "DIAG3_TRIPLE_CONCURRENCE_LOCAL_FOLD_CELL.md": HERE
        / "DIAG3_TRIPLE_CONCURRENCE_LOCAL_FOLD_CELL.md",
        "DIAG3_concurrence_ramification_complete.msolve": MSOLVE,
    }
    for name, path in sources.items():
        if sha256(path) != manifest["source_sha256"][name]:
            raise AssertionError(f"gate source changed: {name}")

    image = verify_factor_map()
    variables, equation_count = verify_msolve_ring(manifest)
    factor_minors, concurrence_minors = verify_dimension_gate(manifest)

    decision = manifest["decision"]
    if decision != {
        "accepted": False,
        "comparison": "slice_to_fullspace",
        "reason": (
            "the pinned fiber determinant is not a full-space "
            "coordinate-height critical system"
        ),
        "status": "FAIL_CLOSED",
    }:
        raise AssertionError("full-space gate decision changed")
    accounting = manifest["theorem_accounting"]
    if (
        accounting["score_before"] != "2/9"
        or accounting["score_after"] != "2/9"
    ):
        raise AssertionError("invalid theorem score accounting")
    if accounting["comparison_incidences_before"] != (
        accounting["comparison_incidences_after"]
    ):
        raise AssertionError("invalid comparison-incidence accounting")
    if accounting["final_unresolved_triple_orbits"] != 1_162_302:
        raise AssertionError("unresolved triple count changed")

    semantic_payload = dict(manifest)
    semantic_payload.pop("semantic_sha256")
    digest = hashlib.sha256(
        json.dumps(
            semantic_payload, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
    ).hexdigest()
    if EXPECTED_SEMANTIC != "TO_BE_PINNED" and digest != EXPECTED_SEMANTIC:
        raise AssertionError(f"full-space gate semantic changed: {digest}")
    if manifest["semantic_sha256"] not in ("TO_BE_PINNED", digest):
        raise AssertionError("manifest semantic digest changed")

    print("PASS named presentation maps to canonical row", image)
    print(
        "PASS pinned slice CAS ring",
        variables,
        f"equations={equation_count}",
    )
    print(
        "PASS full coordinate-height minor census",
        {"factor_chart": factor_minors, "concurrence_chart": concurrence_minors},
    )
    print("SEMANTIC", digest)
    print("GATE FAIL_CLOSED: the five-coordinate slice has no component lift")
    print("OPEN full-space critical census plus frontier attachment and S8 orbit")
    print("LEDGER 1,162,302 triple orbits unresolved; theorem score remains 2/9")


if __name__ == "__main__":
    main()
