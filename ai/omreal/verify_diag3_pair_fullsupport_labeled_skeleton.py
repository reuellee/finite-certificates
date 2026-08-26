#!/usr/bin/env python3
"""Independent structural replay of the partial full-support labelled skeleton.

This verifier does not import the producer.  It authenticates the accepted
minimum-cover, exact roadmap, and exact label-continuation dependencies, then
independently rebuilds the one-dimensional cell/closure/incidence contract and
replays the materialized 97,224-signature profile map from its compact catalog.
"""

from __future__ import annotations

from base64 import b64decode, b64encode
from collections import Counter
from copy import deepcopy
from functools import lru_cache
from hashlib import sha256
import gzip
import json
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
CERTIFICATE = DATA / "DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON.json"
PROFILES = DATA / "DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON_PROFILES.json.gz"
COVER = DATA / "DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json"
TRANSITION = DATA / "DIAG3_PAIR_PARENT_SOURCE_TRANSITION_0_89.json"
LABELS = DATA / "DIAG3_PAIR_PARENT_SOURCE_LABELS_0_89.json"
COMPILED_EDGE_INDEX = 27
FORMAT = "diag3-pair-fullsupport-labeled-skeleton-v1"
PROFILE_FORMAT = "diag3-pair-fullsupport-labeled-skeleton-profiles-v1"
EXPECTED_COVER_SHA256 = "acb8c7a9a140bbb803172164c9a04c3581338dd285953b2e5eff234edc21c1ec"
EXPECTED_TRANSITION_SHA256 = "87f2d7ce337651cea498cc50d36c1b53c8b2294aef54ceac89f0fcc552c7b2d2"
EXPECTED_LABELS_SHA256 = "c6071484960d8bde8c0140aac40ec2a065cc7597d23fcadb3503b25d87f5466a"

sys.path.insert(0, str(HERE))
import four_chart_gate as extension_gate  # noqa: E402
import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: E402


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def canonical_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def digest_file(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def semantic_seal(record) -> str:
    payload = deepcopy(record)
    payload.pop("semantic_sha256", None)
    return sha256(canonical_bytes(payload)).hexdigest()


def reseal(record):
    record["semantic_sha256"] = semantic_seal(record)
    return record


def live_dependencies():
    return {
        "cover": json.loads(COVER.read_text(encoding="utf-8")),
        "transition": json.loads(TRANSITION.read_text(encoding="utf-8")),
        "labels": json.loads(LABELS.read_text(encoding="utf-8")),
        "cover_sha256": digest_file(COVER),
        "transition_sha256": digest_file(TRANSITION),
        "labels_sha256": digest_file(LABELS),
    }


def validate_dependencies(dependencies):
    cover = dependencies["cover"]
    transition = dependencies["transition"]
    labels = dependencies["labels"]
    require(dependencies["cover_sha256"] == EXPECTED_COVER_SHA256, "accepted cover pin")
    require(
        dependencies["transition_sha256"] == EXPECTED_TRANSITION_SHA256,
        "accepted transition pin",
    )
    require(dependencies["labels_sha256"] == EXPECTED_LABELS_SHA256, "accepted labels pin")
    require(
        labels["inputs"]["transition_certificate_sha256"]
        == dependencies["transition_sha256"],
        "label/transition digest cross-pin",
    )
    require(
        labels["inputs"]["transition_certificate"]
        == "ai/omreal/data/DIAG3_PAIR_PARENT_SOURCE_TRANSITION_0_89.json",
        "label/transition path cross-pin",
    )
    transition_events = transition["residual_roadmap"]["events"]
    label_events = labels["continuation"]["event_records"]
    require(len(transition_events) == len(label_events) == 1_237, "cross-pinned event census")
    for event_index, (transition_event, label_event) in enumerate(
        zip(transition_events, label_events, strict=True)
    ):
        require(
            (
                int(label_event["event_index"]),
                int(label_event["factor_id"]),
                int(label_event["occurrence_multiplicity"]),
            )
            == (
                event_index,
                int(transition_event["factor_id"]),
                int(transition_event["occurrence_multiplicity"]),
            ),
            f"transition/label event identity {event_index}",
        )
    return cover, transition, labels


def read_gzip_json(path: Path):
    with gzip.open(path, "rt", encoding="ascii") as source:
        return json.load(source)


def bit_payload(bits) -> bytes:
    return np.packbits(np.asarray(bits, dtype=np.uint8), bitorder="little").tobytes()


def exact_cell_contract(events):
    zero = ["row2599:chart:0"]
    cells = [{
        "id": zero[0],
        "dimension": 0,
        "kind": "stored_strict_parent_chart",
        "chart_index": 0,
    }]
    for event_index, event in enumerate(events):
        identifier = (
            f"row2599:edge:{COMPILED_EDGE_INDEX:03d}:event:{event_index:04d}:"
            f"factor:{int(event['factor_id'])}:root:{int(event['root_index_within_factor'])}"
        )
        zero.append(identifier)
        cells.append({
            "id": identifier,
            "dimension": 0,
            "kind": "isolated_residual_event",
            "event_index": event_index,
            "factor_id": int(event["factor_id"]),
            "root_index_within_factor": int(event["root_index_within_factor"]),
            "isolating_interval": list(event["isolating_interval"]),
            "occurrence_multiplicity": int(event["occurrence_multiplicity"]),
        })
    zero.append("row2599:chart:89")
    cells.append({
        "id": zero[-1],
        "dimension": 0,
        "kind": "stored_strict_parent_chart",
        "chart_index": 89,
    })
    one, closure, incidence = [], [], []
    for chamber in range(len(events) + 1):
        identifier = f"row2599:edge:{COMPILED_EDGE_INDEX:03d}:open:{chamber:04d}"
        one.append(identifier)
        left, right = zero[chamber], zero[chamber + 1]
        cells.append({
            "id": identifier,
            "dimension": 1,
            "kind": "open_residual_chamber",
            "chamber_index": chamber,
            "oriented_boundary": [[left, -1], [right, 1]],
        })
        closure.extend(([identifier, left], [identifier, right]))
        incidence.extend(([left, identifier, -1], [right, identifier, 1]))
    return cells, zero, one, closure, incidence


@lru_cache(maxsize=1)
def exact_extension_universe():
    parents = [
        line.strip()
        for line in extension_gate.CATALOG_48.open(encoding="utf-8")
        if line.strip()
    ]
    _parent, signatures = extension_gate.enumerate_extensions(
        parents[extension_gate.PARENT_INDEX]
    )
    answer = tuple(sorted(map(int, signatures)))
    require(len(answer) == len(set(answer)) == 97_224, "extension universe")
    return answer


def validate_profiles(catalog, zero_count, one_count, accepted_semantic):
    require(set(catalog) == {
        "format",
        "source_edge_index",
        "signature_order",
        "signature_universe_count",
        "signature_universe_sha256",
        "signature_profile_id_width_bytes",
        "signature_profile_ids_base64",
        "profile_count",
        "profile_rows",
        "bad_membership_rule",
        "bad_membership_semantic_sha256",
        "source_signature_profile_semantic_sha256",
    }, "profile catalog schema")
    require(catalog["format"] == PROFILE_FORMAT, "profile format")
    require(catalog["source_edge_index"] == COMPILED_EDGE_INDEX, "profile edge")
    require(
        catalog["signature_order"]
        == "ascending unsigned 56-bit row-2599 extension signature",
        "signature order",
    )
    require(catalog["signature_universe_count"] == 97_224, "profile universe count")
    require(catalog["signature_profile_id_width_bytes"] == 2, "profile ID width")
    require(catalog["profile_count"] == 2_458, "profile count")
    rows = catalog["profile_rows"]
    require(len(rows) == 2_458, "profile rows")

    universe = exact_extension_universe()
    universe_digest = sha256(b"diag3-row2599-extension-universe-v1\0")
    for signature in universe:
        universe_digest.update(signature.to_bytes(7, "little"))
    require(
        catalog["signature_universe_sha256"] == universe_digest.hexdigest(),
        "signature universe digest",
    )

    raw_assignments = b64decode(catalog["signature_profile_ids_base64"], validate=True)
    require(len(raw_assignments) == 2 * len(universe), "assignment byte count")
    assignments = tuple(
        int.from_bytes(raw_assignments[offset : offset + 2], "little")
        for offset in range(0, len(raw_assignments), 2)
    )
    require(max(assignments) < len(rows), "assignment profile range")
    counts = Counter(assignments)

    profile_bytes = (one_count + 7) // 8
    zero_bytes = (zero_count + 7) // 8
    feasible_payloads = []
    bad_digest = sha256(b"diag3-fullsupport-labeled-skeleton-bad-membership-v1\0")
    for identifier, row in enumerate(rows):
        require(
            set(row)
            == {
                "profile_id",
                "signature_count",
                "feasible_one_cells_base64",
                "bad_one_cells_base64",
                "bad_zero_cells_base64",
            },
            "exact profile-row schema",
        )
        require(row["profile_id"] == identifier, "ordered profile ID")
        require(row["signature_count"] == counts[identifier] > 0, "profile count map")
        feasible = b64decode(row["feasible_one_cells_base64"], validate=True)
        bad_one = b64decode(row["bad_one_cells_base64"], validate=True)
        bad_zero = b64decode(row["bad_zero_cells_base64"], validate=True)
        require(len(feasible) == len(bad_one) == profile_bytes, "one-cell bitmap width")
        require(len(bad_zero) == zero_bytes, "zero-cell bitmap width")
        feasible_bits = np.unpackbits(
            np.frombuffer(feasible, dtype=np.uint8), bitorder="little"
        )
        bad_one_bits = np.unpackbits(
            np.frombuffer(bad_one, dtype=np.uint8), bitorder="little"
        )
        bad_zero_bits = np.unpackbits(
            np.frombuffer(bad_zero, dtype=np.uint8), bitorder="little"
        )
        require(not np.any(feasible_bits[one_count:]), "feasible padding")
        require(not np.any(bad_one_bits[one_count:]), "bad-one padding")
        require(not np.any(bad_zero_bits[zero_count:]), "bad-zero padding")
        expected_bad_one = 1 - feasible_bits[:one_count]
        expected_bad_zero = np.zeros(zero_count, dtype=np.uint8)
        expected_bad_zero[:-1] |= expected_bad_one
        expected_bad_zero[1:] |= expected_bad_one
        require(
            np.array_equal(bad_one_bits[:one_count], expected_bad_one),
            "bad one-cell complement",
        )
        require(
            np.array_equal(bad_zero_bits[:zero_count], expected_bad_zero),
            "closed bad zero-cell incidence",
        )
        # Every bad open edge has both faces in the bad subcomplex.
        bad_indices = np.flatnonzero(expected_bad_one)
        require(
            all(expected_bad_zero[index] and expected_bad_zero[index + 1] for index in bad_indices),
            "bad-locus closure",
        )
        feasible_payloads.append(feasible)
        bad_digest.update(identifier.to_bytes(2, "little"))
        bad_digest.update(counts[identifier].to_bytes(4, "little"))
        bad_digest.update(feasible)
        bad_digest.update(bad_one)
        bad_digest.update(bad_zero)
    require(
        feasible_payloads == sorted(set(feasible_payloads)),
        "canonical lexicographic profile-ID materialization",
    )
    require(
        catalog["bad_membership_semantic_sha256"] == bad_digest.hexdigest(),
        "bad-membership digest",
    )
    require(
        catalog["bad_membership_rule"]
        == (
            "an open one-cell is bad iff its chamber is infeasible; a zero-cell "
            "is bad iff at least one incident open one-cell is bad"
        ),
        "exact bad-membership rule",
    )

    semantic = sha256(b"diag3-row2599-path-label-profiles-v1\0")
    for signature, profile in zip(universe, assignments, strict=True):
        semantic.update(signature.to_bytes(7, "little"))
        semantic.update(feasible_payloads[profile])
    require(semantic.hexdigest() == accepted_semantic, "accepted label semantic replay")
    require(
        catalog["source_signature_profile_semantic_sha256"] == accepted_semantic,
        "catalog source semantic",
    )
    return bad_digest.hexdigest()


def reseal_bad_membership(catalog):
    raw_assignments = b64decode(catalog["signature_profile_ids_base64"], validate=True)
    assignments = tuple(
        int.from_bytes(raw_assignments[offset : offset + 2], "little")
        for offset in range(0, len(raw_assignments), 2)
    )
    counts = Counter(assignments)
    digest = sha256(b"diag3-fullsupport-labeled-skeleton-bad-membership-v1\0")
    for identifier, row in enumerate(catalog["profile_rows"]):
        digest.update(identifier.to_bytes(2, "little"))
        digest.update(counts[identifier].to_bytes(4, "little"))
        digest.update(b64decode(row["feasible_one_cells_base64"], validate=True))
        digest.update(b64decode(row["bad_one_cells_base64"], validate=True))
        digest.update(b64decode(row["bad_zero_cells_base64"], validate=True))
    catalog["bad_membership_semantic_sha256"] = digest.hexdigest()
    return catalog


def validate(record, catalog, check_profile_file=True, dependencies=None):
    dependencies = live_dependencies() if dependencies is None else dependencies
    cover, transition, labels = validate_dependencies(dependencies)
    selected = tuple(map(int, cover["source_bank"]["selected_edge_indices"]))
    pending = [index for index in selected if index != COMPILED_EDGE_INDEX]
    require(len(selected) == 40 and len(pending) == 39, "cover partition")
    require(COMPILED_EDGE_INDEX in selected, "compiled cover membership")
    require(tuple(safe.EDGES[COMPILED_EDGE_INDEX]) == (0, 89), "compiled chart pair")

    require(
        set(record)
        == {
            "format",
            "status",
            "scope",
            "inputs",
            "unrefined_minimum_source_graph",
            "compiled_regular_subcomplex",
            "fail_closed_contract_audit",
            "theorem_effect",
            "verifier",
            "semantic_sha256",
        },
        "exact skeleton schema",
    )
    require(record["format"] == FORMAT, "format")
    require(
        record["status"] == "EXACT_PARTIAL_LABELED_SKELETON_BOUNDED_NO_GO",
        "status",
    )
    scope = record["scope"]
    require(
        scope
        == {
            "parent_index": 2599,
            "support": [15, 15, 15],
            "minimum_source_cover_edges": 40,
            "fully_compiled_cover_edges": 1,
            "pending_cover_edges": 39,
            "skeleton_coverage": "COMPLETE_ONLY_ON_SELECTED_EDGE_27_CHART_0_TO_89",
            "parent_cell_component_coverage": "NOT_CLAIMED",
            "global_parent_cell_coverage": "NOT_CLAIMED",
            "pair_branch_closed": False,
            "triple_branch_closed": False,
            "honest_9dvl_score": "2/9",
        },
        "exact fail-closed scope",
    )

    expected_inputs = {
        "minimum_cover_path": "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json",
        "minimum_cover_sha256": dependencies["cover_sha256"],
        "transition_path": "ai/omreal/data/DIAG3_PAIR_PARENT_SOURCE_TRANSITION_0_89.json",
        "transition_sha256": dependencies["transition_sha256"],
        "labels_path": "ai/omreal/data/DIAG3_PAIR_PARENT_SOURCE_LABELS_0_89.json",
        "labels_sha256": dependencies["labels_sha256"],
        "profile_catalog_path": "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON_PROFILES.json.gz",
        "profile_catalog_sha256": digest_file(PROFILES),
    }
    if check_profile_file:
        require(record["inputs"] == expected_inputs, "accepted dependency pins")
    else:
        for key, value in expected_inputs.items():
            if key != "profile_catalog_sha256":
                require(record["inputs"][key] == value, f"accepted dependency pin {key}")

    graph = record["unrefined_minimum_source_graph"]
    pairs = [tuple(map(int, safe.EDGES[index])) for index in selected]
    charts = sorted({chart for pair in pairs for chart in pair})
    require(graph["chart_vertex_count"] == len(charts), "coarse vertex count")
    require(graph["chart_indices"] == charts, "coarse chart indices")
    require(graph["coarse_edge_count"] == 40, "coarse edge count")
    expected_edges = [
        {
            "edge_index": index,
            "id": f"row2599:source-edge:{index:03d}",
            "endpoint_chart_indices": list(safe.EDGES[index]),
            "label_compatible_regular_refinement": (
                "COMPLETE" if index == COMPILED_EDGE_INDEX else "MISSING"
            ),
        }
        for index in selected
    ]
    require(graph["coarse_edges"] == expected_edges, "machine-readable edge residue")
    require(
        graph["warning"]
        == (
            "These coarse source edges are exact parent-resident segments, "
            "but an unsubdivided edge is not a label-compatible master cell."
        ),
        "coarse-edge warning",
    )
    require(
        set(graph)
        == {
            "chart_vertex_count",
            "chart_indices",
            "coarse_edge_count",
            "coarse_edges",
            "warning",
        },
        "exact coarse graph schema",
    )

    events = transition["residual_roadmap"]["events"]
    require(len(events) == 1_237, "accepted roadmap event count")
    require(
        transition["parent_residence"]["strict_on_closed_segment"]
        and transition["parent_residence"]["parent_infinity_cells"] == [],
        "strict-parent dependency",
    )
    cells, zero, one, closure, incidence = exact_cell_contract(events)
    compiled = record["compiled_regular_subcomplex"]
    require(
        set(compiled)
        == {
            "compiled_source_edge_index",
            "compiled_chart_pair",
            "cells",
            "cell_count_by_dimension",
            "cells_sha256",
            "strict_closure_pairs",
            "strict_closure_pairs_sha256",
            "strict_three_cell_chains",
            "scope_endpoint_cells",
            "parent_infinity_subcomplex",
            "integral_boundary",
            "signature_profile_source",
        },
        "exact compiled-subcomplex schema",
    )
    require(compiled["compiled_source_edge_index"] == COMPILED_EDGE_INDEX, "compiled edge")
    require(compiled["compiled_chart_pair"] == [0, 89], "compiled endpoints")
    require(compiled["cells"] == cells, "stable regular cells")
    require(compiled["cell_count_by_dimension"] == {"0": len(zero), "1": len(one)}, "cell census")
    require(compiled["cells_sha256"] == sha256(canonical_bytes(cells)).hexdigest(), "cell digest")
    require(compiled["strict_closure_pairs"] == closure, "closure pairs")
    require(compiled["strict_closure_pairs_sha256"] == sha256(canonical_bytes(closure)).hexdigest(), "closure digest")
    require(compiled["strict_three_cell_chains"] == [], "one-dimensional chain census")
    require(compiled["scope_endpoint_cells"] == [zero[0], zero[-1]], "scope endpoints")
    require(compiled["parent_infinity_subcomplex"] == [], "true parent infinity")
    boundary = compiled["integral_boundary"]
    require(
        set(boundary)
        == {
            "c0_basis",
            "c1_basis",
            "d1_entries",
            "d1_entries_sha256",
            "d_squared_zero",
            "rank_d1",
            "h0_rank",
            "h1_rank",
        },
        "exact boundary schema",
    )
    require(boundary["c0_basis"] == zero and boundary["c1_basis"] == one, "chain bases")
    require(boundary["d1_entries"] == incidence, "signed incidence")
    require(boundary["d1_entries_sha256"] == sha256(canonical_bytes(incidence)).hexdigest(), "incidence digest")
    require(boundary["d_squared_zero"] is True, "d squared")
    require((boundary["rank_d1"], boundary["h0_rank"], boundary["h1_rank"]) == (len(one), 1, 0), "path homology")
    # Each column has one -1 and one +1, and ordering vertices by path position
    # makes the first n columns triangular after deleting the last row.
    by_edge = Counter(entry[1] for entry in incidence)
    require(set(by_edge.values()) == {2}, "two faces per edge")
    require(all(incidence[2 * index] == [zero[index], one[index], -1] and incidence[2 * index + 1] == [zero[index + 1], one[index], 1] for index in range(len(one))), "oriented path columns")

    accepted_semantic = labels["signature_profiles"]["semantic_sha256"]
    bad_digest = validate_profiles(catalog, len(zero), len(one), accepted_semantic)
    profile_source = compiled["signature_profile_source"]
    require(
        set(profile_source)
        == {
            "extension_signature_universe",
            "generic_one_cells",
            "distinct_profiles",
            "source_semantic_sha256",
            "bad_membership_semantic_sha256",
            "all_bad_loci_closed_by_incidence_rule",
        },
        "exact profile-source schema",
    )
    require(profile_source["extension_signature_universe"] == 97_224, "label universe")
    require(profile_source["generic_one_cells"] == len(one), "label chamber count")
    require(profile_source["distinct_profiles"] == 2_458, "label profile count")
    require(profile_source["source_semantic_sha256"] == accepted_semantic, "label source digest")
    require(profile_source["bad_membership_semantic_sha256"] == bad_digest, "bad profile digest")
    require(profile_source["all_bad_loci_closed_by_incidence_rule"] is True, "bad closure claim")

    audit = record["fail_closed_contract_audit"]
    require(
        audit
        == {
            "result": "BOUNDED_NO_GO_FOR_PROMOTING_THE_40_EDGE_COVER_AS_IS",
            "compiled_edge_indices": [COMPILED_EDGE_INDEX],
            "pending_edge_indices": pending,
            "minimal_missing_datum": (
                "For each pending source edge: the complete ordered exact residual-root "
                "roadmap, including coincident-event groups, plus exact continuation of "
                "the 97,224 extension-signature labels across every compound event."
            ),
            "fields_already_complete_on_edge_27": [
                "globally stable regular cell IDs",
                "strict closure pairs",
                "strict three-cell chains (empty by dimension)",
                "signed integral incidence",
                "complete extension-signature bad-membership profiles",
                "true parent-infinity membership",
            ],
            "parent_infinity_classification": (
                "EMPTY: the exact signed-parent Bernstein certificate keeps the whole "
                "closed segment strictly inside row 2599; its two path endpoints are "
                "ordinary stored interior chart vertices, not parent infinity."
            ),
        },
        "exact bounded no-go audit",
    )

    theorem_effect = (
        "Produces a complete labelled regular-CW contract on one of the forty "
        "optimal full-support cover edges and identifies the exact missing datum on "
        "the other thirty-nine. This is source-skeleton coverage, not parent-cell or "
        "component coverage; both diagonal-three obligations remain open and the "
        "honest 9DVL score remains 2/9."
    )
    require(record["theorem_effect"] == theorem_effect, "exact theorem scope")
    require(
        record["verifier"]
        == {
            "command": "python ai/omreal/verify_diag3_pair_fullsupport_labeled_skeleton.py",
            "hostile_corruptions": 16,
            "trust_boundary": (
                "independent structural and profile-digest replay; the exact cover, path "
                "roadmap, and path labels are hard-pinned accepted dependencies with "
                "event-by-event transition/label cross-checking"
            ),
        },
        "exact verifier contract",
    )
    require(
        record["semantic_sha256"] == semantic_seal(record),
        "full-record semantic seal",
    )


def expect_rejected(
    record,
    catalog,
    label,
    check_profile_file=True,
    dependencies=None,
):
    try:
        validate(
            record,
            catalog,
            check_profile_file=check_profile_file,
            dependencies=dependencies,
        )
    except (AssertionError, KeyError, ValueError, TypeError):
        return
    raise AssertionError(f"hostile corruption survived: {label}")


def main():
    record = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    catalog = read_gzip_json(PROFILES)
    dependencies = live_dependencies()
    validate(record, catalog, dependencies=dependencies)

    hostile = []
    corrupt = deepcopy(record)
    corrupt["status"] = "PROVED_DIAGONAL_THREE"
    hostile.append(
        (reseal(corrupt), catalog, "re-sealed promoted partial status", True, None)
    )
    corrupt = deepcopy(record)
    corrupt["scope"]["parent_cell_component_coverage"] = "COMPLETE"
    hostile.append(
        (reseal(corrupt), catalog, "re-sealed skeleton as component cover", True, None)
    )
    corrupt = deepcopy(record)
    corrupt["scope"]["honest_9dvl_score"] = "3/9"
    hostile.append(
        (reseal(corrupt), catalog, "re-sealed dishonest score", True, None)
    )
    corrupt = deepcopy(record)
    corrupt["compiled_regular_subcomplex"]["cells"].pop()
    hostile.append(
        (reseal(corrupt), catalog, "re-sealed missing regular cell", True, None)
    )
    corrupt = deepcopy(record)
    corrupt["compiled_regular_subcomplex"]["strict_closure_pairs"].pop()
    hostile.append(
        (reseal(corrupt), catalog, "re-sealed missing closure face", True, None)
    )
    corrupt = deepcopy(record)
    corrupt["compiled_regular_subcomplex"]["integral_boundary"]["d1_entries"][0][2] = 1
    hostile.append(
        (reseal(corrupt), catalog, "re-sealed orientation flip", True, None)
    )
    corrupt = deepcopy(record)
    corrupt["compiled_regular_subcomplex"]["parent_infinity_subcomplex"] = ["row2599:chart:0"]
    hostile.append(
        (
            reseal(corrupt),
            catalog,
            "re-sealed artificial endpoint as infinity",
            True,
            None,
        )
    )
    corrupt = deepcopy(record)
    corrupt["fail_closed_contract_audit"]["pending_edge_indices"].pop()
    hostile.append(
        (reseal(corrupt), catalog, "re-sealed erased pending edge", True, None)
    )
    corrupt = deepcopy(record)
    next(
        row
        for row in corrupt["unrefined_minimum_source_graph"]["coarse_edges"]
        if row["edge_index"] != COMPILED_EDGE_INDEX
    )["label_compatible_regular_refinement"] = "COMPLETE"
    hostile.append(
        (
            reseal(corrupt),
            catalog,
            "re-sealed unlabelled edge marked complete",
            True,
            None,
        )
    )
    corrupt = deepcopy(record)
    corrupt["compiled_regular_subcomplex"]["integral_boundary"]["h1_rank"] = 1
    hostile.append(
        (reseal(corrupt), catalog, "re-sealed false path homology", True, None)
    )
    corrupt_catalog = deepcopy(catalog)
    raw = bytearray(b64decode(corrupt_catalog["signature_profile_ids_base64"]))
    raw[:2] = (65_535).to_bytes(2, "little")
    corrupt_catalog["signature_profile_ids_base64"] = b64encode(raw).decode("ascii")
    hostile.append(
        (record, corrupt_catalog, "out-of-range profile assignment", False, None)
    )
    corrupt_catalog = deepcopy(catalog)
    raw = bytearray(b64decode(corrupt_catalog["profile_rows"][0]["bad_one_cells_base64"]))
    raw[0] ^= 1
    corrupt_catalog["profile_rows"][0]["bad_one_cells_base64"] = b64encode(raw).decode("ascii")
    hostile.append(
        (record, corrupt_catalog, "corrupt bad one-cell label", False, None)
    )
    corrupt_catalog = deepcopy(catalog)
    corrupt_catalog["profile_rows"][0]["signature_count"] += 1
    hostile.append(
        (record, corrupt_catalog, "corrupt profile multiplicity", False, None)
    )
    corrupt = deepcopy(record)
    corrupt["semantic_sha256"] = "0" * 64
    hostile.append((corrupt, catalog, "corrupt semantic commitment", True, None))

    # The replacement transition and labels agree with each other and the outer
    # record is re-sealed.  Only the independent accepted dependency pins can
    # distinguish this coupled substitution from the accepted proof objects.
    corrupt_dependencies = deepcopy(dependencies)
    corrupt_transition = corrupt_dependencies["transition"]
    corrupt_labels = corrupt_dependencies["labels"]
    corrupt_transition["residual_roadmap"]["events"][0]["factor_id"] += 1
    corrupt_labels["continuation"]["event_records"][0]["factor_id"] += 1
    corrupt_dependencies["transition_sha256"] = sha256(
        canonical_bytes(corrupt_transition)
    ).hexdigest()
    corrupt_labels["inputs"]["transition_certificate_sha256"] = corrupt_dependencies[
        "transition_sha256"
    ]
    corrupt_dependencies["labels_sha256"] = sha256(
        canonical_bytes(corrupt_labels)
    ).hexdigest()
    corrupt = deepcopy(record)
    corrupt["inputs"]["transition_sha256"] = corrupt_dependencies["transition_sha256"]
    corrupt["inputs"]["labels_sha256"] = corrupt_dependencies["labels_sha256"]
    hostile.append(
        (
            reseal(corrupt),
            catalog,
            "re-sealed coupled transition substitution and label cross-pin",
            True,
            corrupt_dependencies,
        )
    )

    # Preserve the represented signature->profile semantics, counts, and bad
    # digest while swapping IDs 0 and 1.  Canonical lexicographic materialization
    # must reject this internally re-sealed but non-canonical catalog.
    corrupt_catalog = deepcopy(catalog)
    corrupt_catalog["profile_rows"][0], corrupt_catalog["profile_rows"][1] = (
        corrupt_catalog["profile_rows"][1],
        corrupt_catalog["profile_rows"][0],
    )
    corrupt_catalog["profile_rows"][0]["profile_id"] = 0
    corrupt_catalog["profile_rows"][1]["profile_id"] = 1
    raw = bytearray(b64decode(corrupt_catalog["signature_profile_ids_base64"]))
    for offset in range(0, len(raw), 2):
        identifier = int.from_bytes(raw[offset : offset + 2], "little")
        if identifier in (0, 1):
            raw[offset : offset + 2] = (1 - identifier).to_bytes(2, "little")
    corrupt_catalog["signature_profile_ids_base64"] = b64encode(raw).decode("ascii")
    reseal_bad_membership(corrupt_catalog)
    hostile.append(
        (
            record,
            corrupt_catalog,
            "re-sealed profile 0/1 identifier permutation",
            False,
            None,
        )
    )

    for corrupt_record, corrupt_catalog, label, check_file, corrupt_dependencies in hostile:
        expect_rejected(
            corrupt_record,
            corrupt_catalog,
            label,
            check_file,
            dependencies=corrupt_dependencies,
        )
    require(len(hostile) == 16, "hostile census")
    print("PASS exact 1,237-event regular refinement of selected cover edge 27")
    print("PASS 1,239 zero-cells + 1,238 one-cells, 2,476 strict faces, signed d1")
    print("PASS parent infinity empty; path endpoints retained as ordinary interior cells")
    print("PASS 97,224 signatures -> 2,458 complete closed bad-membership profiles")
    print("PASS machine-readable 39-edge missing-roadmap/compound-label residue")
    print("PASS 16/16 hostile corruptions rejected")
    print("SCOPE one of forty source-skeleton edges; no parent-cell/component coverage; honest 9DVL 2/9")


if __name__ == "__main__":
    main()
