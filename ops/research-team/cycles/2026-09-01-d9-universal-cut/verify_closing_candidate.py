#!/usr/bin/env python3
"""Fail-closed coordinator replay for the universal D9 cut null candidate."""

from __future__ import annotations

import copy
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
CANDIDATE = HERE / "CLOSING_CANDIDATE.json"
EVIDENCE_COMMIT = "9cb3652b00c0a07901b6fa32dd3f7d03987cfb66"
EVIDENCE_TREE = "37f605949a2fbfdf8be8983b6ea24121eea4a177"
BASE_COMMIT = "cbe84ccd7273252c81fd4da17ee360a284d2a2a6"
BASE_TREE = "da3cd6feca1052ea14ed5036413c72b8f7fadc2a"


class Reject(AssertionError):
    """A fail-closed candidate rejection."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def validate(candidate: dict, check_files: bool = True) -> None:
    require(candidate["format"] == "9dvl-d9-universal-cut-closing-candidate-v1", "format")
    require(candidate["cycle_id"] == "2026-09-01-d9-universal-cut", "cycle")
    require(candidate["evidence_integration"] == {
        "commit": EVIDENCE_COMMIT, "tree": EVIDENCE_TREE
    }, "evidence binding")
    require(candidate["opening_base"] == {
        "commit": BASE_COMMIT, "tree": BASE_TREE
    }, "base binding")
    require(candidate["opening_gate"] == "FAILED_CLOSED", "opening gate")
    require(
        candidate["mathematical_endpoint"] == "UNIVERSAL_CUT_SCHEMA_COVERAGE_GAP",
        "endpoint",
    )
    require(
        candidate["classification"] == "EXACT_NULL_GLOBAL_COVERAGE_AND_ATTACHMENT_NO_GO",
        "classification",
    )
    require(candidate["theorem"] == {
        "id": "9DVL", "opening_score": "2/9", "closing_score": "2/9",
        "promotion": "NONE",
    }, "ledger")
    require(candidate["main_census"] == {"authorized": False, "started": False}, "census")
    require(set(candidate["failure_reasons"]) == {
        "NO_COMPLETE_COMPACTIFIED_COMPONENT_FAITHFUL_INCIDENCE_OBJECT",
        "THIRTEEN_LOCAL_TYPES_NOT_PROJECTION_CLOSED",
        "MEMORYLESS_LOCAL_GRAMMAR_CANNOT_DETERMINE_GLOBAL_CUTS",
        "NO_STRICT_COFACE_ATTACHMENT_FOR_RECURSIVE_FACET_WALL",
        "NO_PROVED_D9_GLOBAL_PROPERTY_REJECTS_COUNTERMODEL_MECHANISM",
        "NO_CERTIFIED_10000_TYPE_OR_250000_INSTANCE_BOUND",
    }, "failure reasons")
    require(candidate["exact_counts"] == {
        "local_wall_types": 13,
        "opposite_partner_pairs": 671,
        "persistent_support_candidates": 2420,
        "abstract_counterpair_chambers": 16,
        "first_layer_new_irreducibles": 142,
        "parent_brackets_checked": 70,
        "global_residual_factors_checked": 26740,
        "boundary_charts_checked": 64,
        "certificate_hostile_mutations_rejected": 32,
        "falsifier_ordered_noninclusions": 72,
    }, "count ledger")
    require(candidate["first_exact_projection_gap"] == {
        "source_type": 36,
        "source_polynomial": "a*f-c*d+c-f",
        "facet": "a=[1346]=0",
        "new_polynomial": "c*d-c+f",
    }, "projection gap")
    require(candidate["boundary_canary"] == {
        "factor_id": 8552, "factor": "d*i-e",
        "recursive_parent_facet": "1237", "strict_open_parent_crossing": False,
    }, "boundary canary")
    require(
        candidate["route_disposition"] ==
        "RETIRED_UNTIL_GLOBAL_ATTACHMENT_AND_PROJECTION_CLOSURE_INPUTS",
        "route disposition",
    )
    require(candidate["selected_successor"] is None, "successor")
    require(candidate["next_state"] == "PIVOT_REQUIRED", "next state")
    require(set(candidate["nonconsequences"]) == {
        "NO_SOURCE_REALIZED_D9_COUNTEREXAMPLE",
        "NO_UNIVERSAL_D9_CUT_COVERAGE_THEOREM",
        "NO_EXHAUSTIVE_OBSTRUCTION_UNSAT_RESULT",
        "NO_STRICT_OPEN_PARENT_SEPARATOR",
        "NO_WEIGHTED_RECURSIVE_LINK_CLASSIFICATION",
        "NO_DIAGONAL_9_RESULT",
        "NO_9DVL_SCORE_CHANGE",
    }, "nonconsequences")
    require(candidate["referee"] == {
        "status": "PENDING_FROZEN_HEAD_REVIEW",
        "owned_surface": "ops/team/d9-universal-cut-referee",
    }, "referee gate")

    if check_files:
        require(git("rev-parse", f"{EVIDENCE_COMMIT}^{{tree}}") == EVIDENCE_TREE, "evidence tree")
        require(git("rev-parse", f"{BASE_COMMIT}^{{tree}}") == BASE_TREE, "base tree")
        for relative, digest in candidate["artifacts"].items():
            require(sha256(ROOT / relative) == digest, f"artifact drift {relative}")


def hostile_canaries(candidate: dict) -> tuple[str, ...]:
    cases = []

    def mutated(callback):
        value = copy.deepcopy(candidate)
        callback(value)
        return value

    cases.extend((
        ("score", mutated(lambda x: x["theorem"].__setitem__("closing_score", "3/9"))),
        ("promotion", mutated(lambda x: x["theorem"].__setitem__("promotion", "D9"))),
        ("gate", mutated(lambda x: x.__setitem__("opening_gate", "PASSED"))),
        ("census", mutated(lambda x: x["main_census"].__setitem__("authorized", True))),
        ("counterexample", mutated(lambda x: x["nonconsequences"].remove("NO_SOURCE_REALIZED_D9_COUNTEREXAMPLE"))),
        ("separator", mutated(lambda x: x["boundary_canary"].__setitem__("strict_open_parent_crossing", True))),
        ("successor", mutated(lambda x: x.__setitem__("selected_successor", "D9_TYPE36_CLOSURE"))),
        ("referee", mutated(lambda x: x["referee"].__setitem__("status", "ACCEPT"))),
    ))
    rejected = []
    for name, value in cases:
        try:
            validate(value, check_files=False)
        except (KeyError, Reject):
            rejected.append(name)
        else:
            raise Reject(f"hostile canary accepted: {name}")
    return tuple(rejected)


def replay(relative: str, markers: tuple[str, ...]) -> None:
    result = subprocess.run(
        [sys.executable, str(ROOT / relative)], cwd=ROOT, check=False,
        capture_output=True, text=True, timeout=600,
        env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"},
    )
    require(result.returncode == 0, f"replay failed {relative}: {result.stderr[-1000:]}")
    for marker in markers:
        require(marker in result.stdout, f"missing replay marker {relative}: {marker}")


def main() -> None:
    candidate = json.loads(CANDIDATE.read_text(encoding="utf-8"))
    validate(candidate)
    rejected = hostile_canaries(candidate)
    replay(
        "ops/research-team/cycles/2026-09-01-d9-universal-cut/verify_opening_audit.py",
        ("PASS universal D9 cut opening audit",),
    )
    replay("ops/research-team/verify_cycle_protocol.py", ("PASS research-cycle",))
    replay("ops/team/d9-universal-cut-prover/verify_cut_reduction_gap.py", (
        "NULL UNIVERSAL_CUT_SCHEMA_COVERAGE_GAP", "hostile mutations: 5/5",
    ))
    replay("ops/team/d9-universal-cut-circuits/verify_cut_grammar_frontier.py", (
        "local-only separator grammar disproved", "theorem ledger remains 2/9",
    ))
    replay("ops/team/d9-universal-cut-boundary/verify_boundary_transport_gate.py", (
        "ENDPOINT UNIVERSAL_CUT_SCHEMA_COVERAGE_GAP", "13/13 hostile mutations rejected",
    ))
    replay("ops/team/d9-universal-cut-falsifier/verify_d9_universal_cut_falsifier.py", (
        "ENDPOINT UNIVERSAL_CUT_SCHEMA_COVERAGE_GAP", "15/15 hostile mutations rejected",
    ))
    replay("ops/team/d9-universal-cut-certificate/verify_universal_cut_certificate.py", (
        "exact endpoint fixtures 4/4", "mathematical endpoint absent",
    ))
    replay("ops/team/d9-universal-cut-certificate/run_hostile_mutations.py", (
        "hostile mutations rejected 32/32", "cannot be promoted to a global separator",
    ))
    replay("ops/team/d9-universal-cut-certificate/verify_portable_predecessor.py", (
        "ACCEPT PORTABLE_PREDECESSOR_REPLAY", "ca730426 is recorded as absent",
    ))
    print("PASS universal D9 cut closing candidate")
    print("PASS exact evidence bindings and hostile candidate canaries:", len(rejected), "/", len(rejected))
    print("NULL UNIVERSAL_CUT_SCHEMA_COVERAGE_GAP; main census not authorized")
    print("SCOPE no D9 result; theorem ledger remains 2/9; next state PIVOT_REQUIRED")


if __name__ == "__main__":
    main()
