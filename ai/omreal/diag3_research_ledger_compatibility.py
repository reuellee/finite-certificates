#!/usr/bin/env python3
"""Fail-closed compatibility gate for historical D3 certificates and ledger v2.

The certificates produced before the post-PR44 canonical reconciliation bind
the exact v1 decision-ledger bytes.  That provenance is immutable.  Replays in
the current tree must additionally authenticate ledger v2 and prove that the
obligations used by those certificates are unchanged; they must never replace
the historical digest in a committed certificate with the current file hash.
"""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
LEDGER = HERE / "data/DIAG3_RESEARCH_DECISION_LEDGER.json"

HISTORICAL_LEDGER_SHA256 = (
    "5841dfbb55aa0d8c580b394b50beff54d607ce86b77683985c2d977c03050e14"
)
HISTORICAL_LEDGER_GIT_BLOB = "fe877050ae3942254bef54f23d6f3790480d698c"
CURRENT_LEDGER_SHA256 = (
    "73b0b742d6336d754ae99b7054858a3a3c96b3aaf1601b2228c076a732903d6e"
)
INVARIANT_OBLIGATIONS_SEMANTIC_SHA256 = (
    "219bf46f82e0c5ff127d956b78acc600539482a867c9a767acde1d43f32eab1a"
)
THEOREM_SEMANTIC_SHA256 = (
    "6bb5676e25169ea7124dd26977b487caafe2390afeacf162894bc63301d85c56"
)
HISTORICAL_ROW2599_SEMANTIC_SHA256 = (
    "428b58a56b789701a59b3b8cfa9809abd378b551b3c6f543f5654c7b050c8f4e"
)


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def semantic_sha256(value) -> str:
    return hashlib.sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def require_historical_ledger_binding(value: str, label: str) -> None:
    """Authenticate an immutable v1 binding recorded by a historical artifact."""

    if value != HISTORICAL_LEDGER_SHA256:
        raise AssertionError(f"historical v1 decision-ledger binding changed: {label}")


def verify_current_payload(ledger: dict) -> None:
    """Check the exact reconciled state and the obligation-preserving v1->v2 lift."""

    if ledger.get("format") != "diag3-research-decision-ledger-v2":
        raise AssertionError("current decision-ledger format changed")
    if (ledger.get("status"), ledger.get("as_of"), ledger.get("selected_target")) != (
        "PIVOT_REQUIRED",
        "2026-08-31",
        None,
    ):
        raise AssertionError("current decision-ledger selection state changed")

    repository = ledger.get("repository")
    if repository != {
        "full_name": "reuellee/finite-certificates",
        "default_branch": "main",
        "audited_commit": "e666990f5b0cf07fef4a639bbb6596ddc9c4515a",
        "audited_tree": "444f8a7e50ec58e4d97a71744090d7ed60330f19",
        "merged_pull_request": 44,
    }:
        raise AssertionError("current decision-ledger repository provenance changed")

    if semantic_sha256(ledger.get("theorem")) != THEOREM_SEMANTIC_SHA256:
        raise AssertionError("9DVL theorem identity changed")
    if (
        semantic_sha256(ledger.get("invariant_obligations"))
        != INVARIANT_OBLIGATIONS_SEMANTIC_SHA256
    ):
        raise AssertionError("historical invariant-obligation semantics changed")

    reconciliation = ledger.get("canonical_reconciliation")
    if not isinstance(reconciliation, dict):
        raise AssertionError("canonical reconciliation record missing")
    if (
        reconciliation.get("precedence"),
        reconciliation.get("theorem_score"),
        reconciliation.get("proved_diagonals"),
    ) != ("CURRENT_THROUGH_MERGED_PR_44", "2/9", [1, 2]):
        raise AssertionError("canonical theorem score changed")
    if reconciliation.get("d4_accounting") != {
        "domain_labeled": 1_715_980,
        "domain_orbits": 130,
        "proved_labeled": 915_740,
        "proved_orbits": 77,
        "survivor_labeled": 800_240,
        "survivor_orbits": 53,
        "identity": "1715980/130=915740/77+800240/53",
        "survivor_delta_after_pr43": {"labeled": 0, "orbits": 0},
    }:
        raise AssertionError("canonical D4 accounting changed")
    if reconciliation.get("d3_accounting") != {
        "unresolved_residue": 1_162_302,
        "quotient_classes": 100_086_840,
        "raw_frame_presentations": 104_993_280,
        "quotient_multiplicity_sum": 104_993_280,
        "row_delta_after_pr44": 0,
    }:
        raise AssertionError("canonical D3 accounting changed")
    if reconciliation.get("first_missing_global_object") != {
        "id": "Q3_COMPLETE_PARENT_BOUNDARY_ATLAS",
        "status": "MISSING",
        "equivalent": "all_parent_closure_stratum_transport_and_attachment_atlas",
    }:
        raise AssertionError("canonical D3 missing-global-object gate changed")
    if reconciliation.get("retired_continuations") != [
        "D4_S53_CONTINUATION",
        "ORBIT_5563_LOCAL_ROADMAP_CONTINUATION",
        "ORBIT_5563_LOCAL_BOX_CONTINUATION",
        "ORBIT_5563_LOCAL_COLLAR_CONTINUATION",
        "ORBIT_5563_MACROBOX_CONTINUATION",
        "ORBIT_5563_CLIPPED_WALL_CONTINUATION",
    ]:
        raise AssertionError("canonical retired-route semantics changed")
    if reconciliation.get("conditional_route_dispositions") != {
        "D4_ALTERNATING_TOTAL_COMPLEX": {
            "status": "RETIRED_UNTIL_GLOBAL_INPUTS",
            "distinct_from": "D4_S53_CONTINUATION",
            "required_global_inputs": [
                "THEOREM_READY_GLOBAL_COMPACTIFICATION",
                "SIGNED_FACE_POSET",
                "RESTRICTION_MATRICES",
            ],
            "incomplete_successor_input_gate": "STOP_FAIL_CLOSED",
            "reactivation_requires_all_inputs": True,
        }
    }:
        raise AssertionError("canonical conditional-route semantics changed")
    if (
        reconciliation.get("selected_mathematical_target"),
        reconciliation.get("target_selection"),
    ) != (None, "PENDING_FRESH_INDEPENDENT_OPENING_AUDIT"):
        raise AssertionError("canonical target-selection gate changed")
    if reconciliation.get("historical_pointer_policy") != {
        "ledger_v1_git_blob": HISTORICAL_LEDGER_GIT_BLOB,
        "preserve_exact_historical_artifacts": True,
        "historical_continuation_text_is_current": False,
    }:
        raise AssertionError("historical v1 decision-ledger pointer changed")

    historical_row = ledger.get("historical_row2599_fullsupport_ledger")
    if semantic_sha256(historical_row) != HISTORICAL_ROW2599_SEMANTIC_SHA256:
        raise AssertionError("historical row-2599 ledger semantics changed")


def load_current_ledger(path: Path = LEDGER) -> dict:
    actual = file_sha256(path)
    if actual != CURRENT_LEDGER_SHA256:
        raise AssertionError(f"current v2 decision-ledger digest changed: {actual}")
    ledger = json.loads(path.read_text(encoding="utf-8"))
    verify_current_payload(ledger)
    return ledger


def historical_row2599(ledger: dict | None = None) -> dict:
    if ledger is None:
        ledger = load_current_ledger()
    verify_current_payload(ledger)
    return ledger["historical_row2599_fullsupport_ledger"]


def verify_hostile_mutations() -> int:
    """Prove semantic gates reject mutations even if a payload is re-serialized."""

    source = load_current_ledger()
    mutations = []

    def add(label, mutate):
        candidate = deepcopy(source)
        mutate(candidate)
        mutations.append((label, candidate))

    add("format", lambda row: row.__setitem__("format", "diag3-research-decision-ledger-v3"))
    add("score", lambda row: row["canonical_reconciliation"].__setitem__("theorem_score", "3/9"))
    add("d3_count", lambda row: row["canonical_reconciliation"]["d3_accounting"].__setitem__("unresolved_residue", 1_162_301))
    add("d4_count", lambda row: row["canonical_reconciliation"]["d4_accounting"].__setitem__("survivor_orbits", 52))
    add("q3_gate", lambda row: row["canonical_reconciliation"]["first_missing_global_object"].__setitem__("status", "COMPLETE"))
    add("retired_route", lambda row: row["canonical_reconciliation"]["retired_continuations"].pop())
    add("target", lambda row: row.__setitem__("selected_target", "orbit_5563_local_roadmap"))
    add("obligation", lambda row: row["invariant_obligations"][0].__setitem__("unresolved_count", 1_162_301))
    add("historical_pointer", lambda row: row["canonical_reconciliation"]["historical_pointer_policy"].__setitem__("ledger_v1_git_blob", "0" * 40))

    for label, candidate in mutations:
        try:
            verify_current_payload(candidate)
        except (AssertionError, KeyError, TypeError, ValueError):
            continue
        raise AssertionError(f"hostile ledger compatibility mutation accepted: {label}")
    return len(mutations)
