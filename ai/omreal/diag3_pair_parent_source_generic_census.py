#!/usr/bin/env python3
"""Generate the exact all-cover-edge phase-A census and one pending pilot."""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor
from copy import deepcopy
from pathlib import Path
import json
import sys


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
DEFAULT_OUTPUT = REPO / "ops" / "team" / "generic-edge-compiler" / "DIAG3_PAIR_PARENT_SOURCE_GENERIC_PHASE_A.json"

sys.path.insert(0, str(HERE))
import diag3_pair_parent_source_generic_core as core  # noqa: E402


def build_record(workers: int, batch_size: int):
    inputs = core.load_inputs()
    selected = inputs["selected"]
    with ProcessPoolExecutor(max_workers=workers) as executor:
        rows = list(executor.map(core.compile_edge_worker, selected, chunksize=1))
    rows.sort(key=lambda row: row["edge_index"])

    compiled = {27, 39}
    pending_eligible = [
        row for row in rows
        if row["edge_index"] not in compiled and core.eligible_for_phase_b(row)
    ]
    pending_eligible.sort(key=core.selection_key)
    recommended = pending_eligible[:batch_size]
    if not recommended:
        raise AssertionError("no pending edge passed the fail-closed phase-B gate")
    pilot_index = recommended[0]["edge_index"]
    pilot_spec = next(spec for spec in selected if spec[0] == pilot_index)
    pilot = core.compile_edge(pilot_spec, include_events=True, progress=False)

    record = {
        "format": "diag3-pair-parent-source-generic-phase-a-v1",
        "status": "FINITE_EXACT_PARAMETERIZED_EDGE_CENSUS_AND_PENDING_PILOT",
        "base_revision": core.BASE_REVISION,
        "scope": {
            "parent_index": 2599,
            "support": [15, 15, 15],
            "selected_cover_edges": 40,
            "already_label_compiled_edges": [27, 39],
            "pending_edges": 38,
            "phase_a": "exact root-event/degeneracy and parent-residence census on every selected edge",
            "phase_b": "not materialized except roadmap pilot; no 97,224-signature bitmap generated",
            "global_parent_cell_coverage": "NOT_CLAIMED",
            "component_coverage": "NOT_CLAIMED",
            "honest_9dvl_score": "2/9_UNCHANGED",
        },
        "inputs": {
            str(path.relative_to(core.REPO)): digest
            for path, digest in sorted(core.PINNED.items(), key=lambda row: str(row[0]))
        },
        "compiler_contract": {
            "orientation": "preserve selected source-chart to target-chart order",
            "parent_residence": "require all 70 signed parent brackets strictly positive on the closed segment",
            "endpoint_roots": "inventory with exact multiplicity; exclude edge from automatic phase-B batch",
            "identically_zero_restrictions": "inventory; exclude edge from automatic phase-B batch",
            "repeated_or_tangential_roots": "preserve multiplicity/parity; force exact post-event label re-enumeration",
            "coincident_distinct_factors": "group only after exact polynomial-gcd proof; force exact post-event label re-enumeration",
            "multi_root_factors": "preserve a root index for each distinct interior root",
            "compound_label_events": "any coincident, repeated/tangential, or multi-occurrence event uses exact re-enumeration",
            "state_replay": "odd interior multiplicities must reconstruct the oriented target factor state",
        },
        "edge_census": rows,
        "selection_manifest": {
            "eligibility_gate": (
                "strict parent residence; no endpoint or identically-zero factor; exact target-state replay; "
                "pairwise ordered event boxes"
            ),
            "ranking_key": [
                "compound_label_event_count",
                "ordered_event_group_count",
                "multi_root_factor_count",
                "edge_index",
            ],
            "recommended_batch_size": len(recommended),
            "recommended_edge_indices": [row["edge_index"] for row in recommended],
            "recommended_edge_keys": [row["stable_edge_key"] for row in recommended],
            "pilot_edge_index": pilot_index,
            "excluded_pending_edges": [
                row["edge_index"] for row in rows
                if row["edge_index"] not in compiled and not core.eligible_for_phase_b(row)
            ],
        },
        "proof_producing_pending_edge_pilot": pilot,
        "resource_contract": {
            "parallel_workers_are_not_certificate_semantics": True,
            "maximum_supported_workers": 8,
            "profile_bitmap_materialized": False,
        },
        "theorem_effect": (
            "Establishes a deterministic exact phase-A compiler frontier and a full roadmap on one pending "
            "selected edge only.  It does not continue extension labels, prove source-skeleton coverage, "
            "classify wall components, or advance the 9DVL ledger."
        ),
    }
    record["semantic_sha256"] = core.semantic_seal(record)
    return record


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--batch-size", type=int, default=4)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    if not 1 <= args.workers <= 8:
        raise SystemExit("--workers must be in [1,8]")
    if not 1 <= args.batch_size <= 8:
        raise SystemExit("--batch-size must be in [1,8]")
    record = build_record(args.workers, args.batch_size)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n",
        encoding="utf-8",
    )
    print("WROTE", args.output.relative_to(REPO))
    print("PASS exact selected-edge census", len(record["edge_census"]))
    print("PASS pending pilot edge", record["selection_manifest"]["pilot_edge_index"])
    print("NEXT BATCH", record["selection_manifest"]["recommended_edge_indices"])
    print("SEMANTIC_SHA256", record["semantic_sha256"])


if __name__ == "__main__":
    main()
