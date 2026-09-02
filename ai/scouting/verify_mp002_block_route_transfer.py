#!/usr/bin/env python3
"""Independent claim/provenance verifier for the preregistered MP-002 holdout.

The default verification does not trust the producer's verdicts.  It
reconstructs the registered selection frontier from the exact chart bank,
checks the two pre-observation Git commits, recomputes every finite identity
and dominance relation from pinned result records, and runs hostile claim
mutations.  ``--full-replay`` additionally regenerates all three exact label
histories in memory and compares the complete records byte-for-byte in their
semantic content.
"""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
from itertools import permutations
import json
import multiprocessing
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

import numpy as np


HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
OMREAL = HERE.parent / "omreal"
DATA = HERE / "data"
REGISTRATION = DATA / "MP002_BLOCK_ROUTE_TRANSFER_REGISTRATION.json"
PREDICTION = DATA / "MP002_BLOCK_ROUTE_TRANSFER_PREDICTION.json"
MANIFEST = DATA / "MP002_BLOCK_ROUTE_TRANSFER_MANIFEST.json"
HOLDOUT_HISTORY = DATA / "MP002_HOLDOUT_HISTORY.tar.gz"
ORDERS = ("102", "120", "210")
REGISTRATION_COMMIT = "c818dd8415ffa3c1286f2d3200f93276f10ce98b"
PREDICTION_COMMIT = "4ddd987d4f2cbc55459f557fc578ee7dec55806e"
HOLDOUT_HISTORY_SHA256 = "a469a9b35b800c471c47c3d32ca772f5bc8a27b1ef4684b0ce760bcea6001f5a"
FROZEN_PRODUCER_SHA256 = "f8973ac6214317450b7b11348238217c2a2357852554f50ec0a1b30de685f1c3"
FULL_MASK = (1 << 56) - 1
EXPECTED_TOPE_COUNT = 26_112


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def file_sha256(path: Path) -> str:
    value = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def digest(value) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def semantic_sha256(record: dict) -> str:
    payload = deepcopy(record)
    payload.pop("semantic_sha256", None)
    return digest(payload)


def reseal(record: dict) -> dict:
    record["semantic_sha256"] = semantic_sha256(record)
    return record


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args],
        cwd=REPO,
        check=check,
        capture_output=True,
    )


def git_file_sha256(commit: str, path: str, *, git_dir: Path | None = None) -> str:
    arguments = ([f"--git-dir={git_dir}"] if git_dir is not None else [])
    return sha256(git(*arguments, "show", f"{commit}:{path}").stdout).hexdigest()


def verify_holdout_chronology(registration: dict, prediction: dict) -> None:
    require(file_sha256(HOLDOUT_HISTORY) == HOLDOUT_HISTORY_SHA256, "holdout history archive hash mismatch")
    with tempfile.TemporaryDirectory() as temporary:
        git_dir = Path(temporary)
        with tarfile.open(HOLDOUT_HISTORY, "r:gz") as archive:
            members = archive.getmembers()
            require(
                all(
                    member.isfile()
                    and not Path(member.name).is_absolute()
                    and ".." not in Path(member.name).parts
                    for member in members
                ),
                "unsafe holdout history archive member",
            )
            for member in members:
                target = git_dir / member.name
                target.parent.mkdir(parents=True, exist_ok=True)
                source = archive.extractfile(member)
                require(source is not None, "missing holdout archive payload")
                target.write_bytes(source.read())
        require(
            git(
                f"--git-dir={git_dir}",
                "merge-base",
                "--is-ancestor",
                REGISTRATION_COMMIT,
                PREDICTION_COMMIT,
            ).returncode
            == 0,
            "registration commit does not precede prediction freeze",
        )
        require(
            git_file_sha256(
                REGISTRATION_COMMIT,
                REGISTRATION.relative_to(REPO).as_posix(),
                git_dir=git_dir,
            )
            == file_sha256(REGISTRATION),
            "registration commit/file mismatch",
        )
        require(
            git_file_sha256(
                PREDICTION_COMMIT,
                PREDICTION.relative_to(REPO).as_posix(),
                git_dir=git_dir,
            )
            == file_sha256(PREDICTION),
            "prediction freeze commit/file mismatch",
        )
        require(
            git_file_sha256(
                PREDICTION_COMMIT,
                "ai/scouting/explore_block_route_transfer.py",
                git_dir=git_dir,
            )
            == FROZEN_PRODUCER_SHA256,
            "freeze-time producer hash mismatch",
        )
        for order in ORDERS:
            path = f"ai/scouting/data/MP002_BLOCK_ROUTE_TRANSFER_ORDER_{order}.json"
            require(
                git(
                    f"--git-dir={git_dir}",
                    "cat-file",
                    "-e",
                    f"{PREDICTION_COMMIT}:{path}",
                    check=False,
                ).returncode
                != 0,
                f"holdout result {order} existed at prediction freeze",
            )
    require(
        prediction["registration_git_commit"] == REGISTRATION_COMMIT
        == registration.get("registration_git_commit", REGISTRATION_COMMIT),
        "prediction registration-commit link changed",
    )
    require(
        prediction["registration_sha256"] == file_sha256(REGISTRATION),
        "prediction registration hash changed",
    )


def exact_selection_frontier() -> list[list]:
    sys.path.insert(0, str(OMREAL))
    import diag3_pair_parent_source_block_bridge_core as bridge  # noqa: PLC0415
    import diag3_pair_parent_source_transition_core as transition  # noqa: PLC0415
    import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: PLC0415
    import verify_diag3_pair_global_parent_face_gate as gate  # noqa: PLC0415

    _matrices, points, _packed, states, _hamming, _multiplicity = transition.exact_inputs()
    records = [json.loads(line) for line in safe.CATALOG.read_text().splitlines() if line]
    parents, _parent_digest = gate.parent_polynomials(records[2599])

    def interior(vertex) -> bool:
        return all(
            target * bridge.evaluator.evaluate(polynomial, vertex) > Fraction(0)
            for _label, target, polynomial, _terms in parents
        )

    frontier = []
    for target_chart in range(len(points)):
        if target_chart in (0, 89, 152):
            continue
        valid = []
        for order in permutations(range(3)):
            vertices = bridge.bridge_vertices(points[0], points[target_chart], order)
            if all(interior(vertex) for vertex in vertices):
                valid.append("".join(map(str, order)))
        if len(valid) >= 2:
            frontier.append(
                [
                    int(np.count_nonzero(states[0] != states[target_chart])),
                    target_chart,
                    valid,
                ]
            )
    frontier.sort()
    return frontier


def verify_registration(registration: dict) -> None:
    require(
        registration["status"] == "REGISTERED_BEFORE_HOLDOUT_OBSERVATION",
        "registration status changed",
    )
    require(registration["honest_9dvl_score"] == "2/9", "registration score contamination")
    require(
        registration["resource_contract"]["exact_replays_per_route"] == 1
        and registration["resource_contract"]["worker_ceiling"] == 6,
        "registered replay resource contract changed",
    )
    for row in registration["pinned_inputs"]:
        require(file_sha256(REPO / row["path"]) == row["sha256"], f"input hash mismatch: {row['path']}")
    selection = registration["object_selection"]
    frontier = exact_selection_frontier()
    require(frontier == selection["eligible_endpoint_frontier"], "selection frontier changed")
    require(digest(frontier) == selection["eligible_endpoint_frontier_sha256"], "frontier digest changed")
    require(len(frontier) == selection["eligible_endpoint_count"] == 13, "eligible endpoint census changed")
    require(frontier[0] == [1812, 66, list(ORDERS)], "registered holdout was not selected mechanically")
    required_exclusions = {
        "all block-route classes",
        "all endpoints in the row-2599 parent cell",
        "all oriented matroids",
        "a general equivalence between wall-event count and alternation",
        "any change to the honest 9DVL score",
    }
    require(
        required_exclusions <= set(registration["claim_boundary"]["excluded_claims"]),
        "registered claim boundary was enlarged",
    )


def normalized_spectrum(record: dict) -> dict[int, int]:
    return {int(level): int(amount) for level, amount in record["transition_spectrum"].items()}


def tail_counts(spectrum: dict[int, int]) -> dict[str, int]:
    return {
        str(threshold): sum(amount for level, amount in spectrum.items() if level >= threshold)
        for threshold in range(1, max(spectrum) + 1)
    }


def verify_prediction(prediction: dict, registration: dict) -> None:
    require(
        prediction["status"] == "PREDICTION_FROZEN_PRE_LABEL_CONTINUATION",
        "prediction was not frozen before labels",
    )
    require(prediction["holdout_alternation_observed"] is False, "holdout observation leak")
    require(semantic_sha256(prediction) == prediction["semantic_sha256"], "prediction semantic digest changed")
    summaries = prediction["event_summaries"]
    require([row["order"] for row in summaries] == list(ORDERS), "phase-a order class changed")
    require(sum(row["events"] for row in summaries) == prediction["total_events"] == 13_548, "phase-a event census changed")
    contract = registration["resource_contract"]
    require(all(row["events"] <= contract["maximum_events_per_route"] for row in summaries), "per-route ceiling violated")
    require(prediction["total_events"] <= contract["maximum_total_events"], "total event ceiling violated")
    selected = min(summaries, key=lambda row: (row["events"], row["order"]))
    require(selected["order"] == prediction["predicted_order"] == "102", "frozen predictor changed")


def verify_result(record: dict, expected: dict, prediction: dict) -> None:
    order = expected["order"]
    require(record["path_id"] == f"row2599-chart-0-to-66-order-{order}", "path identity mismatch")
    require("".join(map(str, record["block_order"])) == order, "block order mismatch")
    require(record["prediction_semantic_sha256"] == prediction["semantic_sha256"], "prediction link mismatch")
    summary = next(row for row in prediction["event_summaries"] if row["order"] == order)
    require(record["phase_a_event_summary"] == summary, "phase-a summary mismatch")
    spectrum = normalized_spectrum(record)
    require(sum(spectrum.values()) == record["signature_universe"] == 97_224, "signature census mismatch")
    require(sum(level * amount for level, amount in spectrum.items()) == record["transition_mass"], "transition-mass identity failed")
    require(sum(amount for level, amount in spectrum.items() if level & 1) == record["endpoint_symmetric_difference"], "endpoint parity identity failed")
    maximum = max(spectrum)
    maximizers = record["maximizers"]
    signatures = {row["signature"] for row in maximizers}
    require(record["maximum_alternation"] == maximum == expected["maximum_alternation"], "maximum mismatch")
    require(len(maximizers) == spectrum[maximum] == record["maximizer_count"] == expected["maximizer_count"], "maximizer census mismatch")
    require(len(signatures) == len(maximizers), "duplicate maximizer")
    require(all(row["antipode"] == (row["signature"] ^ FULL_MASK) for row in maximizers), "bad antipode field")
    require(all((signature ^ FULL_MASK) in signatures for signature in signatures), "maximizers are not antipode-closed")
    require(record["maximizers_antipode_closed"] is True, "false antipode closure verdict")
    require(
        all(
            len(row["event_indices"]) == maximum
            and row["event_indices"] == sorted(set(row["event_indices"]))
            and all(0 <= index < record["events"] for index in row["event_indices"])
            for row in maximizers
        ),
        "invalid maximizer history",
    )
    require(record["events"] == expected["events"] == summary["events"], "event count mismatch")
    require(record["transition_mass"] == expected["transition_mass"], "transition mass mismatch")
    require(record["transition_spectrum"] == expected["transition_spectrum"], "transition spectrum mismatch")
    require(tail_counts(spectrum) == expected["tail_counts"], "tail census mismatch")
    require(record["semantic_sha256"] == expected["semantic_sha256"], "semantic pin mismatch")
    require(semantic_sha256(record) == record["semantic_sha256"], "result semantic digest mismatch")


def dominates(left: dict[str, int], right: dict[str, int]) -> bool:
    weak = all(left[key] <= right[key] for key in left)
    strict = any(left[key] < right[key] for key in left)
    return weak and strict


def verify_manifest(manifest: dict, registration: dict, prediction: dict, records: dict[str, dict]) -> None:
    require(semantic_sha256(manifest) == manifest["semantic_sha256"], "manifest semantic digest changed")
    require(manifest["status"] == "REFUTED", "refuted candidate was falsely promoted")
    require(manifest["honest_9dvl_score"] == "2/9", "manifest score contamination")
    require(manifest["scope"]["9dvl_theorem_effect"] == "NONE", "false 9DVL theorem effect")
    require(manifest["scope"]["novelty"].startswith("NOT_CLAIMED"), "false novelty claim")
    require(
        manifest["scope"]["excluded_claims"] == registration["claim_boundary"]["excluded_claims"],
        "claim exclusions changed after observation",
    )
    require(manifest["holdout_protocol"]["registration_git_commit"] == REGISTRATION_COMMIT, "manifest registration commit changed")
    require(manifest["holdout_protocol"]["prediction_freeze_git_commit"] == PREDICTION_COMMIT, "manifest prediction commit changed")
    require(
        manifest["holdout_protocol"]["phase_b_result_paths_absent_at_prediction_freeze"]
        is True,
        "phase chronology evidence changed",
    )
    require(
        manifest["holdout_protocol"]["resource_accounting"]
        == {
            "observational_exact_continuations_per_route": 1,
            "independent_verification_replay_outside_discovery_budget": 1,
            "worker_ceiling": 6,
        },
        "holdout resource accounting changed",
    )
    require(
        manifest["holdout_protocol"]["history_archive"]
        == {
            "path": "ai/scouting/data/MP002_HOLDOUT_HISTORY.tar.gz",
            "sha256": HOLDOUT_HISTORY_SHA256,
            "format": "minimal-shallow-git-object-store-v1",
        },
        "holdout history provenance changed",
    )
    require(
        manifest["provenance"]["producer_at_prediction_freeze"]
        == {
            "path": "ai/scouting/explore_block_route_transfer.py",
            "git_commit": PREDICTION_COMMIT,
            "sha256": FROZEN_PRODUCER_SHA256,
        },
        "freeze-time producer provenance changed",
    )
    require(
        manifest["provenance"]["current_reproducer"]
        == {
            "path": "ai/scouting/explore_block_route_transfer.py",
            "sha256": file_sha256(HERE / "explore_block_route_transfer.py"),
            "post_result_change": "worker-ceiling validation only",
        },
        "current reproducer provenance changed",
    )

    tails = {order: tail_counts(normalized_spectrum(records[order])) for order in ORDERS}
    violations = [
        (order, int(threshold), tails["102"][threshold], tails[order][threshold])
        for order in ("120", "210")
        for threshold in tails["102"]
        if tails[order][threshold] < tails["102"][threshold]
    ]
    require(violations == [("120", 3, 824, 476)], "exact refuting witness changed")
    witness = manifest["claim"]["counterexample"]
    require(
        witness
        == {
            "predicted_order": "102",
            "predicted_order_events": 4_228,
            "rival_order": "120",
            "rival_order_events": 4_362,
            "threshold": 3,
            "predicted_order_tail": 824,
            "rival_order_tail": 476,
            "tail_gap": 348,
        },
        "manifest counterexample changed",
    )
    require(witness["predicted_order_tail"] - witness["rival_order_tail"] == witness["tail_gap"], "counterexample gap identity failed")
    finite = manifest["finite_class"]
    require(finite["registered_valid_orders"] == list(ORDERS), "finite route class changed")
    require(finite["restricted_minimax_alternation"] == min(records[o]["maximum_alternation"] for o in ORDERS) == 5, "restricted minimax changed")
    require(finite["event_count_order"] == sorted(ORDERS, key=lambda o: records[o]["events"]), "event-count order changed")
    require(finite["transition_mass_order"] == sorted(ORDERS, key=lambda o: records[o]["transition_mass"]), "mass order changed")
    expected_dominance = {
        "102_over_120": dominates(tails["102"], tails["120"]),
        "120_over_102": dominates(tails["120"], tails["102"]),
        "102_over_210": dominates(tails["102"], tails["210"]),
        "120_over_210": dominates(tails["120"], tails["210"]),
    }
    require(finite["tail_dominance"] == expected_dominance, "tail-dominance matrix changed")
    frontier = [
        order
        for order in ORDERS
        if not any(dominates(tails[rival], tails[order]) for rival in ORDERS if rival != order)
    ]
    require(frontier == finite["tail_pareto_frontier"] == ["102", "120"], "tail Pareto frontier changed")
    require("separate Pareto coordinates" in manifest["application"]["recommended_objective"], "application boundary changed")


def rejection(action, fragment: str) -> None:
    try:
        action()
    except AssertionError as error:
        require(fragment in str(error), f"canary failed for wrong reason: {error}")
    else:
        raise AssertionError(f"hostile mutation survived: {fragment}")


def hostile_canaries(manifest: dict, registration: dict, prediction: dict, records: dict[str, dict]) -> int:
    expected = {row["order"]: row for row in manifest["finite_class"]["results"]}

    bad = deepcopy(records["102"])
    bad["transition_spectrum"]["3"] -= 1
    rejection(lambda: verify_result(bad, expected["102"], prediction), "signature census mismatch")

    bad = deepcopy(records["102"])
    bad["maximizers"].pop()
    rejection(lambda: verify_result(bad, expected["102"], prediction), "maximizer census mismatch")

    bad = deepcopy(records["120"])
    bad["prediction_semantic_sha256"] = "0" * 64
    rejection(lambda: verify_result(bad, expected["120"], prediction), "prediction link mismatch")

    bad_manifest = deepcopy(manifest)
    bad_manifest["status"] = "EXACT_FINITE_FACT"
    reseal(bad_manifest)
    rejection(lambda: verify_manifest(bad_manifest, registration, prediction, records), "falsely promoted")

    bad_manifest = deepcopy(manifest)
    bad_manifest["honest_9dvl_score"] = "3/9"
    reseal(bad_manifest)
    rejection(lambda: verify_manifest(bad_manifest, registration, prediction, records), "score contamination")

    bad_manifest = deepcopy(manifest)
    bad_manifest["scope"]["novelty"] = "NOVEL"
    reseal(bad_manifest)
    rejection(lambda: verify_manifest(bad_manifest, registration, prediction, records), "false novelty claim")

    bad_manifest = deepcopy(manifest)
    bad_manifest["scope"]["excluded_claims"].remove("all oriented matroids")
    reseal(bad_manifest)
    rejection(lambda: verify_manifest(bad_manifest, registration, prediction, records), "claim exclusions changed")

    bad_manifest = deepcopy(manifest)
    bad_manifest["claim"]["counterexample"]["rival_order_tail"] = 825
    reseal(bad_manifest)
    rejection(lambda: verify_manifest(bad_manifest, registration, prediction, records), "counterexample changed")

    bad_manifest = deepcopy(manifest)
    bad_manifest["finite_class"]["tail_pareto_frontier"] = ["102"]
    reseal(bad_manifest)
    rejection(lambda: verify_manifest(bad_manifest, registration, prediction, records), "Pareto frontier changed")

    bad_manifest = deepcopy(manifest)
    bad_manifest["holdout_protocol"]["resource_accounting"][
        "observational_exact_continuations_per_route"
    ] = 2
    reseal(bad_manifest)
    rejection(lambda: verify_manifest(bad_manifest, registration, prediction, records), "resource accounting changed")

    bad_prediction = deepcopy(prediction)
    bad_prediction["holdout_alternation_observed"] = True
    reseal(bad_prediction)
    rejection(lambda: verify_prediction(bad_prediction, registration), "holdout observation leak")

    bad_prediction = deepcopy(prediction)
    bad_prediction["predicted_order"] = "120"
    reseal(bad_prediction)
    rejection(lambda: verify_prediction(bad_prediction, registration), "frozen predictor changed")

    bad_registration = deepcopy(registration)
    bad_registration["claim_boundary"]["excluded_claims"].remove("all block-route classes")
    rejection(lambda: verify_registration(bad_registration), "claim boundary was enlarged")
    return 13


def _compound_topes(parent):
    sys.path.insert(0, str(OMREAL))
    import DIAG9_GRAPH_exact_topes as topes  # noqa: PLC0415

    return set(topes.parent_topes(parent))


def replay_event_summary(order, points, states, multiplicity):
    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(OMREAL))
    import diag3_pair_parent_source_block_bridge_core as bridge  # noqa: PLC0415
    import diag3_pair_parent_source_block_labels_core as block_labels  # noqa: PLC0415
    import explore_extension_path_alternation as mp1  # noqa: PLC0415

    vertices = bridge.bridge_vertices(points[0], points[66], order)
    events, root_census = mp1.generated_block_events(vertices, multiplicity, progress=True)
    state = states[0].copy()
    for event in events:
        state[event["factor_id"]] ^= np.uint8(1)
    require(np.array_equal(state, states[66]), "full replay factor-state endpoint mismatch")
    grouped = block_labels.event_groups(events, len(vertices) - 1)
    summary = {
        "order": "".join(map(str, order)),
        "events": len(events),
        "segment_event_census": list(map(len, grouped)),
        "compound_event_count": sum(
            int(event["occurrence_multiplicity"]) != 1 for event in events
        ),
        "segment_factor_root_count_census": root_census,
        "events_sha256": digest(events),
    }
    return events, vertices, grouped, summary


def replay_summarize(path_id, universe, initial, final, counts, histories, event_deltas):
    spectrum = Counter(counts.get(signature, 0) for signature in universe)
    maximum = max(spectrum)
    maximizers = sorted(
        signature for signature in universe if counts.get(signature, 0) == maximum
    )
    endpoint_difference = initial ^ final
    odd_signatures = {
        signature for signature in universe if counts.get(signature, 0) & 1
    }
    require(
        odd_signatures == endpoint_difference,
        "full replay endpoint parity identity failed",
    )
    require(
        sum(level * amount for level, amount in spectrum.items())
        == sum(event_deltas),
        "full replay transition-mass identity failed",
    )
    return {
        "path_id": path_id,
        "segments": 3,
        "signature_universe": len(universe),
        "events": len(event_deltas),
        "transition_mass": sum(event_deltas),
        "endpoint_symmetric_difference": len(endpoint_difference),
        "transition_spectrum": {
            str(key): value for key, value in sorted(spectrum.items())
        },
        "maximum_alternation": maximum,
        "maximizer_count": len(maximizers),
        "maximizers": [
            {
                "signature": signature,
                "hex": f"{signature:014x}",
                "antipode": signature ^ FULL_MASK,
                "event_indices": histories[signature],
            }
            for signature in maximizers
        ],
        "maximizers_antipode_closed": all(
            (signature ^ FULL_MASK) in maximizers for signature in maximizers
        ),
        "identities": {
            "transition_mass_equals_sum_of_event_symmetric_differences": True,
            "odd_alternation_signatures_equal_endpoint_symmetric_difference": True,
        },
    }


def replay_factor_occurrences(events):
    sys.path.insert(0, str(OMREAL))
    import diag3_pair_parent_source_transition_core as transition  # noqa: PLC0415

    with np.load(transition.FACTOR_CENSUS, allow_pickle=False) as source:
        occurrence_factor = np.asarray(
            source["occurrence_factor"], dtype=np.uint32
        )
        occurrence_fourset = np.asarray(
            source["occurrence_fourset"], dtype=np.uint8
        )
    return {
        factor_id: tuple(
            tuple(map(int, row))
            for row in occurrence_fourset[
                np.flatnonzero(occurrence_factor == factor_id)
            ]
        )
        for factor_id in {int(event["factor_id"]) for event in events}
    }


def replay_one(order, matrices, points, states, multiplicity, expected_summary, workers):
    sys.path.insert(0, str(HERE))
    sys.path.insert(0, str(OMREAL))
    import DIAG9_GRAPH_exact_topes as topes  # noqa: PLC0415
    import diag3_pair_parent_source_block_labels_core as block_labels  # noqa: PLC0415
    import diag3_pair_parent_source_labels_core as source_labels  # noqa: PLC0415

    events, vertices, grouped, summary = replay_event_summary(
        order, points, states, multiplicity
    )
    require(summary == expected_summary, "full replay phase-a summary mismatch")
    compound_parents = block_labels.compound_tasks(vertices, grouped)
    pool = multiprocessing.get_context("fork").Pool(workers)
    compound_results = pool.imap(_compound_topes, compound_parents, chunksize=1)

    normalized_zero = block_labels.segment_parent(vertices, 0, Fraction(0))
    raw_zero = matrices[0].tolist()
    reorientation = source_labels.solve_reorientation_mask(
        topes.parent_signs(normalized_zero), topes.parent_signs(raw_zero)
    )
    labels = {
        signature ^ reorientation
        for signature in topes.parent_topes(normalized_zero)
    }
    initial = set(labels)
    occurrences = replay_factor_occurrences(events)
    universe = source_labels.raw_extension_universe()
    counts = Counter()
    histories = defaultdict(list)
    event_deltas = []
    event_index = 0
    try:
        for segment_index, segment_events in enumerate(grouped):
            for event in segment_events:
                factor_id = int(event["factor_id"])
                before = labels
                if int(event["occurrence_multiplicity"]) == 1:
                    labels, _preliminary = source_labels.simple_mutation(
                        labels, occurrences[factor_id][0]
                    )
                else:
                    normalized = next(compound_results)
                    labels = {
                        signature ^ reorientation for signature in normalized
                    }
                changed = before ^ labels
                for signature in changed:
                    counts[signature] += 1
                    histories[signature].append(event_index)
                event_deltas.append(len(changed))
                event_index += 1
                require(
                    len(labels) == EXPECTED_TOPE_COUNT,
                    "full replay tope-cardinality drift",
                )
            expected_endpoint = {
                signature ^ reorientation
                for signature in topes.parent_topes(
                    block_labels.segment_parent(
                        vertices, segment_index, Fraction(1)
                    )
                )
            }
            require(labels == expected_endpoint, "full replay segment endpoint mismatch")
    except BaseException:
        pool.terminate()
        pool.join()
        raise
    else:
        pool.close()
        pool.join()

    require(
        labels == set(topes.parent_topes(matrices[66].tolist())),
        "full replay target endpoint mismatch",
    )
    require(set(counts) <= set(universe), "full replay left the signature universe")
    result = replay_summarize(
        f"row2599-chart-0-to-66-order-{''.join(map(str, order))}",
        universe,
        initial,
        labels,
        counts,
        histories,
        event_deltas,
    )
    result["block_order"] = list(order)
    result["phase_a_event_summary"] = summary
    return result


def full_replay(records: dict[str, dict], prediction: dict, workers: int) -> None:
    sys.path.insert(0, str(OMREAL))
    import diag3_pair_parent_source_transition_core as transition  # noqa: PLC0415

    matrices, points, _packed, states, _hamming, multiplicity = transition.exact_inputs()
    summaries = {row["order"]: row for row in prediction["event_summaries"]}
    for order_text in ORDERS:
        replay = replay_one(
            tuple(map(int, order_text)),
            matrices,
            points,
            states,
            multiplicity,
            summaries[order_text],
            workers,
        )
        replay["prediction_semantic_sha256"] = prediction["semantic_sha256"]
        replay["semantic_sha256"] = semantic_sha256(replay)
        require(replay == records[order_text], f"full replay mismatch: {order_text}")
        print(f"FULL_REPLAY {order_text} PASS semantic_sha256={replay['semantic_sha256']}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--skip-canaries", action="store_true")
    parser.add_argument("--full-replay", action="store_true")
    parser.add_argument("--workers", type=int, default=6)
    args = parser.parse_args()

    registration = json.loads(REGISTRATION.read_text())
    prediction = json.loads(PREDICTION.read_text())
    manifest = json.loads(MANIFEST.read_text())
    require(
        1 <= args.workers <= registration["resource_contract"]["worker_ceiling"],
        "verification worker ceiling",
    )
    require(file_sha256(REGISTRATION) == manifest["holdout_protocol"]["registration_sha256"], "manifest registration hash mismatch")
    require(file_sha256(PREDICTION) == manifest["holdout_protocol"]["prediction_sha256"], "manifest prediction hash mismatch")
    require(
        file_sha256(HERE / "explore_block_route_transfer.py")
        == manifest["provenance"]["current_reproducer"]["sha256"],
        "current reproducer hash mismatch",
    )
    verify_holdout_chronology(registration, prediction)
    verify_registration(registration)
    verify_prediction(prediction, registration)

    expected = {row["order"]: row for row in manifest["finite_class"]["results"]}
    records = {}
    for order in ORDERS:
        path = REPO / expected[order]["path"]
        require(file_sha256(path) == expected[order]["sha256"], f"result file hash mismatch: {order}")
        records[order] = json.loads(path.read_text())
        verify_result(records[order], expected[order], prediction)
    verify_manifest(manifest, registration, prediction, records)
    canaries = 0 if args.skip_canaries else hostile_canaries(manifest, registration, prediction, records)
    if args.full_replay:
        full_replay(records, prediction, args.workers)
    print(
        "PASS MP-002 exact held-out refutation: routes=3 "
        f"hostile_canaries={canaries} full_replay={args.full_replay} "
        "counterexample=(102 events 4228, tail>=3 824) vs "
        "(120 events 4362, tail>=3 476) status=REFUTED "
        "honest_9dvl_score=2/9"
    )


if __name__ == "__main__":
    main()
