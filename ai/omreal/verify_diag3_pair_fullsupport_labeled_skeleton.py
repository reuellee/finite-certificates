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
    require(catalog["format"] == PROFILE_FORMAT, "profile format")
    require(catalog["source_edge_index"] == COMPILED_EDGE_INDEX, "profile edge")
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
        catalog["bad_membership_semantic_sha256"] == bad_digest.hexdigest(),
        "bad-membership digest",
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


def validate(record, catalog, check_profile_file=True):
    cover = json.loads(COVER.read_text(encoding="utf-8"))
    transition = json.loads(TRANSITION.read_text(encoding="utf-8"))
    labels = json.loads(LABELS.read_text(encoding="utf-8"))
    selected = tuple(map(int, cover["source_bank"]["selected_edge_indices"]))
    pending = [index for index in selected if index != COMPILED_EDGE_INDEX]
    require(len(selected) == 40 and len(pending) == 39, "cover partition")
    require(COMPILED_EDGE_INDEX in selected, "compiled cover membership")
    require(tuple(safe.EDGES[COMPILED_EDGE_INDEX]) == (0, 89), "compiled chart pair")

    require(record["format"] == FORMAT, "format")
    require(
        record["status"] == "EXACT_PARTIAL_LABELED_SKELETON_BOUNDED_NO_GO",
        "status",
    )
    scope = record["scope"]
    require(scope["support"] == [15, 15, 15], "full support")
    require(scope["minimum_source_cover_edges"] == 40, "cover size")
    require(scope["fully_compiled_cover_edges"] == 1, "compiled edge count")
    require(scope["pending_cover_edges"] == 39, "pending edge count")
    require(
        scope["skeleton_coverage"] == "COMPLETE_ONLY_ON_SELECTED_EDGE_27_CHART_0_TO_89",
        "skeleton scope",
    )
    require(scope["parent_cell_component_coverage"] == "NOT_CLAIMED", "component scope")
    require(scope["global_parent_cell_coverage"] == "NOT_CLAIMED", "parent scope")
    require(scope["honest_9dvl_score"] == "2/9", "honest score")

    expected_inputs = {
        "minimum_cover_path": "ai/omreal/data/DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json",
        "minimum_cover_sha256": digest_file(COVER),
        "transition_path": "ai/omreal/data/DIAG3_PAIR_PARENT_SOURCE_TRANSITION_0_89.json",
        "transition_sha256": digest_file(TRANSITION),
        "labels_path": "ai/omreal/data/DIAG3_PAIR_PARENT_SOURCE_LABELS_0_89.json",
        "labels_sha256": digest_file(LABELS),
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

    events = transition["residual_roadmap"]["events"]
    require(len(events) == 1_237, "accepted roadmap event count")
    require(
        transition["parent_residence"]["strict_on_closed_segment"]
        and transition["parent_residence"]["parent_infinity_cells"] == [],
        "strict-parent dependency",
    )
    cells, zero, one, closure, incidence = exact_cell_contract(events)
    compiled = record["compiled_regular_subcomplex"]
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
    require(profile_source["extension_signature_universe"] == 97_224, "label universe")
    require(profile_source["generic_one_cells"] == len(one), "label chamber count")
    require(profile_source["distinct_profiles"] == 2_458, "label profile count")
    require(profile_source["source_semantic_sha256"] == accepted_semantic, "label source digest")
    require(profile_source["bad_membership_semantic_sha256"] == bad_digest, "bad profile digest")
    require(profile_source["all_bad_loci_closed_by_incidence_rule"] is True, "bad closure claim")

    audit = record["fail_closed_contract_audit"]
    require(audit["result"] == "BOUNDED_NO_GO_FOR_PROMOTING_THE_40_EDGE_COVER_AS_IS", "no-go result")
    require(audit["compiled_edge_indices"] == [COMPILED_EDGE_INDEX], "audit compiled")
    require(audit["pending_edge_indices"] == pending, "audit pending")
    require("ordered exact residual-root roadmap" in audit["minimal_missing_datum"], "minimal missing roadmap")
    require("97,224 extension-signature labels" in audit["minimal_missing_datum"], "minimal missing labels")
    require("EMPTY" in audit["parent_infinity_classification"], "infinity classification")

    semantic_payload = {
        "cover_semantic_sha256": cover["semantic_sha256"],
        "compiled_edge": COMPILED_EDGE_INDEX,
        "pending_edges": pending,
        "cell_sha256": compiled["cells_sha256"],
        "closure_sha256": compiled["strict_closure_pairs_sha256"],
        "incidence_sha256": boundary["d1_entries_sha256"],
        "profile_source_sha256": accepted_semantic,
        "bad_membership_sha256": bad_digest,
    }
    require(record["semantic_sha256"] == sha256(canonical_bytes(semantic_payload)).hexdigest(), "semantic digest")
    require("source-skeleton coverage, not parent-cell or component coverage" in record["theorem_effect"], "theorem scope")
    require("2/9" in record["theorem_effect"], "theorem score")


def expect_rejected(record, catalog, label, check_profile_file=True):
    try:
        validate(record, catalog, check_profile_file=check_profile_file)
    except (AssertionError, KeyError, ValueError, TypeError):
        return
    raise AssertionError(f"hostile corruption survived: {label}")


def main():
    record = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    catalog = read_gzip_json(PROFILES)
    validate(record, catalog)

    hostile = []
    corrupt = deepcopy(record)
    corrupt["status"] = "PROVED_DIAGONAL_THREE"
    hostile.append((corrupt, catalog, "promoted partial status", True))
    corrupt = deepcopy(record)
    corrupt["scope"]["parent_cell_component_coverage"] = "COMPLETE"
    hostile.append((corrupt, catalog, "skeleton as component cover", True))
    corrupt = deepcopy(record)
    corrupt["scope"]["honest_9dvl_score"] = "3/9"
    hostile.append((corrupt, catalog, "dishonest score", True))
    corrupt = deepcopy(record)
    corrupt["compiled_regular_subcomplex"]["cells"].pop()
    hostile.append((corrupt, catalog, "missing regular cell", True))
    corrupt = deepcopy(record)
    corrupt["compiled_regular_subcomplex"]["strict_closure_pairs"].pop()
    hostile.append((corrupt, catalog, "missing closure face", True))
    corrupt = deepcopy(record)
    corrupt["compiled_regular_subcomplex"]["integral_boundary"]["d1_entries"][0][2] = 1
    hostile.append((corrupt, catalog, "unsigned orientation flip", True))
    corrupt = deepcopy(record)
    corrupt["compiled_regular_subcomplex"]["parent_infinity_subcomplex"] = ["row2599:chart:0"]
    hostile.append((corrupt, catalog, "artificial endpoint as infinity", True))
    corrupt = deepcopy(record)
    corrupt["fail_closed_contract_audit"]["pending_edge_indices"].pop()
    hostile.append((corrupt, catalog, "erased pending edge", True))
    corrupt = deepcopy(record)
    next(row for row in corrupt["unrefined_minimum_source_graph"]["coarse_edges"] if row["edge_index"] != COMPILED_EDGE_INDEX)["label_compatible_regular_refinement"] = "COMPLETE"
    hostile.append((corrupt, catalog, "unlabelled edge marked complete", True))
    corrupt = deepcopy(record)
    corrupt["compiled_regular_subcomplex"]["integral_boundary"]["h1_rank"] = 1
    hostile.append((corrupt, catalog, "false path homology", True))
    corrupt_catalog = deepcopy(catalog)
    raw = bytearray(b64decode(corrupt_catalog["signature_profile_ids_base64"]))
    raw[:2] = (65_535).to_bytes(2, "little")
    corrupt_catalog["signature_profile_ids_base64"] = b64encode(raw).decode("ascii")
    hostile.append((record, corrupt_catalog, "out-of-range profile assignment", False))
    corrupt_catalog = deepcopy(catalog)
    raw = bytearray(b64decode(corrupt_catalog["profile_rows"][0]["bad_one_cells_base64"]))
    raw[0] ^= 1
    corrupt_catalog["profile_rows"][0]["bad_one_cells_base64"] = b64encode(raw).decode("ascii")
    hostile.append((record, corrupt_catalog, "corrupt bad one-cell label", False))
    corrupt_catalog = deepcopy(catalog)
    corrupt_catalog["profile_rows"][0]["signature_count"] += 1
    hostile.append((record, corrupt_catalog, "corrupt profile multiplicity", False))
    corrupt = deepcopy(record)
    corrupt["semantic_sha256"] = "0" * 64
    hostile.append((corrupt, catalog, "corrupt semantic commitment", True))

    for corrupt_record, corrupt_catalog, label, check_file in hostile:
        expect_rejected(corrupt_record, corrupt_catalog, label, check_file)
    require(len(hostile) == 14, "hostile census")
    print("PASS exact 1,237-event regular refinement of selected cover edge 27")
    print("PASS 1,239 zero-cells + 1,238 one-cells, 2,476 strict faces, signed d1")
    print("PASS parent infinity empty; path endpoints retained as ordinary interior cells")
    print("PASS 97,224 signatures -> 2,458 complete closed bad-membership profiles")
    print("PASS machine-readable 39-edge missing-roadmap/compound-label residue")
    print("PASS 14/14 hostile corruptions rejected")
    print("SCOPE one of forty source-skeleton edges; no parent-cell/component coverage; honest 9DVL 2/9")


if __name__ == "__main__":
    main()
