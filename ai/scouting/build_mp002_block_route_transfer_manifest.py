#!/usr/bin/env python3
"""Build the exact MP-002 held-out transfer/refutation manifest."""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
REGISTRATION = DATA / "MP002_BLOCK_ROUTE_TRANSFER_REGISTRATION.json"
PREDICTION = DATA / "MP002_BLOCK_ROUTE_TRANSFER_PREDICTION.json"
OUTPUT = DATA / "MP002_BLOCK_ROUTE_TRANSFER_MANIFEST.json"
HOLDOUT_HISTORY = DATA / "MP002_HOLDOUT_HISTORY.tar.gz"
ORDERS = ("102", "120", "210")
REGISTRATION_COMMIT = "c818dd8415ffa3c1286f2d3200f93276f10ce98b"
PREDICTION_COMMIT = "4ddd987d4f2cbc55459f557fc578ee7dec55806e"
FROZEN_PRODUCER_SHA256 = "f8973ac6214317450b7b11348238217c2a2357852554f50ec0a1b30de685f1c3"


def digest(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def file_digest(path):
    value = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def semantic(record):
    payload = deepcopy(record)
    payload.pop("semantic_sha256", None)
    return digest(payload)


def tail(record):
    spectrum = {
        int(level): amount
        for level, amount in record["transition_spectrum"].items()
    }
    return {
        str(threshold): sum(
            amount for level, amount in spectrum.items() if level >= threshold
        )
        for threshold in range(1, max(spectrum) + 1)
    }


def dominates(left, right):
    thresholds = sorted(map(int, left))
    weak = all(left[str(k)] <= right[str(k)] for k in thresholds)
    strict = any(left[str(k)] < right[str(k)] for k in thresholds)
    return weak and strict


def main():
    registration = json.loads(REGISTRATION.read_text())
    prediction = json.loads(PREDICTION.read_text())
    records = {
        order: json.loads(
            (DATA / f"MP002_BLOCK_ROUTE_TRANSFER_ORDER_{order}.json").read_text()
        )
        for order in ORDERS
    }
    if registration["status"] != "REGISTERED_BEFORE_HOLDOUT_OBSERVATION":
        raise AssertionError("registration status changed")
    if prediction["status"] != "PREDICTION_FROZEN_PRE_LABEL_CONTINUATION":
        raise AssertionError("prediction was not frozen")
    if prediction["predicted_order"] != "102":
        raise AssertionError("prediction changed")
    if any(semantic(record) != record["semantic_sha256"] for record in records.values()):
        raise AssertionError("result semantic digest changed")

    tails = {order: tail(record) for order, record in records.items()}
    success = all(
        all(
            tails["102"][threshold] <= tails[order][threshold]
            for threshold in tails["102"]
        )
        for order in ("120", "210")
    ) and any(
        tails["102"][threshold] < tails[order][threshold]
        for order in ("120", "210")
        for threshold in tails["102"]
    )
    if success:
        raise AssertionError("registered transfer unexpectedly passed")
    if not (
        tails["120"]["3"] == 476
        and tails["102"]["3"] == 824
        and records["102"]["events"] == 4_228
        and records["120"]["events"] == 4_362
    ):
        raise AssertionError("refuting witness changed")

    result_rows = []
    for order in ORDERS:
        record = records[order]
        path = DATA / f"MP002_BLOCK_ROUTE_TRANSFER_ORDER_{order}.json"
        result_rows.append(
            {
                "order": order,
                "path": str(path.relative_to(HERE.parents[1])),
                "sha256": file_digest(path),
                "semantic_sha256": record["semantic_sha256"],
                "events": record["events"],
                "transition_mass": record["transition_mass"],
                "maximum_alternation": record["maximum_alternation"],
                "maximizer_count": record["maximizer_count"],
                "transition_spectrum": record["transition_spectrum"],
                "tail_counts": tails[order],
            }
        )

    record = {
        "format": "mp002-block-route-transfer-manifest-v1",
        "expedition_id": "MP-002",
        "title": "Block-route event-count transfer",
        "status": "REFUTED",
        "honest_9dvl_score": "2/9",
        "claim": {
            "registered_candidate": (
                "the minimum exact wall-event route weakly minimizes every "
                "nonzero extension-membership alternation tail in the held-out "
                "three-route class"
            ),
            "verdict": "REFUTED_BY_EXACT_HELD_OUT_COUNTEREXAMPLE",
            "counterexample": {
                "predicted_order": "102",
                "predicted_order_events": 4_228,
                "rival_order": "120",
                "rival_order_events": 4_362,
                "threshold": 3,
                "predicted_order_tail": 824,
                "rival_order_tail": 476,
                "tail_gap": 348,
            },
        },
        "finite_class": {
            "parent": 2_599,
            "source_chart": 0,
            "target_chart": 66,
            "endpoint_factor_state_hamming_distance": 1_812,
            "registered_valid_orders": list(ORDERS),
            "results": result_rows,
            "restricted_minimax_alternation": 5,
            "tail_dominance": {
                "102_over_120": dominates(tails["102"], tails["120"]),
                "120_over_102": dominates(tails["120"], tails["102"]),
                "102_over_210": dominates(tails["102"], tails["210"]),
                "120_over_210": dominates(tails["120"], tails["210"]),
            },
            "tail_pareto_frontier": ["102", "120"],
            "event_count_order": ["102", "120", "210"],
            "transition_mass_order": ["102", "120", "210"],
        },
        "holdout_protocol": {
            "registration_git_commit": REGISTRATION_COMMIT,
            "registration_sha256": file_digest(REGISTRATION),
            "prediction_freeze_git_commit": PREDICTION_COMMIT,
            "prediction_sha256": file_digest(PREDICTION),
            "prediction_semantic_sha256": prediction["semantic_sha256"],
            "phase_a_total_events": prediction["total_events"],
            "phase_b_result_paths_absent_at_prediction_freeze": True,
            "resource_accounting": {
                "observational_exact_continuations_per_route": 1,
                "independent_verification_replay_outside_discovery_budget": 1,
                "worker_ceiling": 6,
            },
            "history_archive": {
                "path": str(HOLDOUT_HISTORY.relative_to(HERE.parents[1])),
                "sha256": file_digest(HOLDOUT_HISTORY),
                "format": "minimal-shallow-git-object-store-v1",
            },
        },
        "application": {
            "certificate_route_selection": (
                "wall-event count remains a useful replay-cost proxy and matches "
                "transition-mass order here, but it cannot replace the alternation "
                "tail vector when exceptional-history compression matters"
            ),
            "recommended_objective": (
                "retain event count and alternation tails as separate Pareto "
                "coordinates instead of scalarizing route quality by event count"
            ),
        },
        "scope": {
            "result": "exact refutation on one preregistered held-out finite route class",
            "excluded_claims": registration["claim_boundary"]["excluded_claims"],
            "novelty": "NOT_CLAIMED; the contribution is the exact counterexample and certificate-design consequence",
            "9dvl_theorem_effect": "NONE",
        },
        "provenance": {
            "registration": {
                "path": str(REGISTRATION.relative_to(HERE.parents[1])),
                "sha256": file_digest(REGISTRATION),
            },
            "prediction": {
                "path": str(PREDICTION.relative_to(HERE.parents[1])),
                "sha256": file_digest(PREDICTION),
            },
            "producer_at_prediction_freeze": {
                "path": "ai/scouting/explore_block_route_transfer.py",
                "git_commit": PREDICTION_COMMIT,
                "sha256": FROZEN_PRODUCER_SHA256,
            },
            "current_reproducer": {
                "path": "ai/scouting/explore_block_route_transfer.py",
                "sha256": file_digest(HERE / "explore_block_route_transfer.py"),
                "post_result_change": "worker-ceiling validation only",
            },
        },
        "semantic_sha256": None,
    }
    record["semantic_sha256"] = semantic(record)
    OUTPUT.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="ascii"
    )
    print("WROTE", OUTPUT)
    print("VERDICT", record["status"])
    print("COUNTEREXAMPLE", record["claim"]["counterexample"])
    print("PARETO", record["finite_class"]["tail_pareto_frontier"])


if __name__ == "__main__":
    main()
