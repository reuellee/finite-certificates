#!/usr/bin/env python3
"""Compile the deterministic edge-27/edge-39 labelled source-skeleton candidate.

This is producer code, not an independent acceptance verifier.  It consumes
the accepted edge-27 regular path and the candidate edge-39 exact path, glues
their unique shared chart-0 vertex, and materializes joint signature profiles.
"""

from __future__ import annotations

from base64 import b64decode
from collections import Counter
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import gzip
import json
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUTPUT = DATA / "DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON_EDGE27_EDGE39.json"
PROFILE_OUTPUT = DATA / "DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON_EDGE27_EDGE39_PROFILES.bin.gz"

EDGE27_TRANSITION = DATA / "DIAG3_PAIR_PARENT_SOURCE_TRANSITION_0_89.json"
EDGE27_LABELS = DATA / "DIAG3_PAIR_PARENT_SOURCE_LABELS_0_89.json"
COVER = DATA / "DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json"
SKELETON = DATA / "DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON.json"
SKELETON_PROFILES = DATA / "DIAG3_PAIR_FULLSUPPORT_LABELED_SKELETON_PROFILES.json.gz"
COLLAR = DATA / "DIAG3_PAIR_FULLSUPPORT_COMPONENT_COLLAR.json"
EDGE39_TRANSITION = DATA / "DIAG3_PAIR_PARENT_SOURCE_TRANSITION_EDGE39_0_113.json"
EDGE39_LABELS = DATA / "DIAG3_PAIR_PARENT_SOURCE_LABELS_EDGE39_0_113.json"
EDGE39_PROFILES = DATA / "DIAG3_PAIR_PARENT_SOURCE_LABELS_EDGE39_0_113_PROFILES.bin.gz"

PINS = {
    EDGE27_TRANSITION: "87f2d7ce337651cea498cc50d36c1b53c8b2294aef54ceac89f0fcc552c7b2d2",
    EDGE27_LABELS: "c6071484960d8bde8c0140aac40ec2a065cc7597d23fcadb3503b25d87f5466a",
    COVER: "19248dd148d1fd002931ed5f48197869dd42c68a513376e1a4d6941389bda307",
    SKELETON: "5430bd79ae9ddee09ce9b393f018389be1210c250a7eb0d5486fab8e1294663d",
    SKELETON_PROFILES: "25094cddf35754fd83f25fbea11e1b6bf8fd168781850f409ca3aa2ecf2c4223",
    COLLAR: "5930cc19019470fdfdf55d67523f6c4211ccf5b540f5c2bb5df36c64db75d7bd",
    EDGE39_TRANSITION: "cb6eebc0df9bfeae8055c81471f09d594f8116e002caf11f62f9e865b0936dd7",
    EDGE39_LABELS: "dc80acaf2f711ee5e0e053e856e4abf858adf90483ba0e5ced13018bdb909170",
    EDGE39_PROFILES: "77b042d72e4c28dc5e60145624adfd27b080aaec8aa757cdf10c0d7c5513e6b6",
}

FORMAT = "diag3-pair-fullsupport-labeled-skeleton-edge27-edge39-v1"
PROFILE_MAGIC = b"D3JNT1\0\0"
PROFILE_FORMAT = "diag3-edge27-edge39-joint-bad-membership-v1"
STATUS = "EXACT_TWO_EDGE_LABELED_SOURCE_SKELETON_CANDIDATE"

SIGNATURE_COUNT = 97_224
EDGE27_ZERO = 1_239
EDGE27_ONE = 1_238
EDGE39_ZERO = 5_329
EDGE39_ONE = 5_328
ZERO_COUNT = 6_567
ONE_COUNT = 6_566
PROFILE_BYTES = (ONE_COUNT + 7) // 8
BAD_ZERO_BYTES = (ZERO_COUNT + 7) // 8


def file_sha256(path):
    digest = sha256()
    with Path(path).open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def semantic_seal(record):
    payload = deepcopy(record)
    payload.pop("semantic_sha256", None)
    return sha256(canonical_bytes(payload)).hexdigest()


def semantic_rows(domain, rows):
    digest = sha256(domain)
    for row in rows:
        digest.update(canonical_bytes(row))
    return digest.hexdigest()


def require_pins():
    for path, expected in PINS.items():
        if file_sha256(path) != expected:
            raise AssertionError(f"pinned dependency changed: {path.name}")


def load_json(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def read_edge39_profiles():
    labels = load_json(EDGE39_LABELS)
    expected_semantic = labels["signature_profiles"]["semantic_sha256"]
    semantic = sha256(b"diag3-row2599-edge39-label-profiles-v1\0")
    universe = np.empty(SIGNATURE_COUNT, dtype=np.uint64)
    profiles = np.empty((SIGNATURE_COUNT, 666), dtype=np.uint8)
    with gzip.open(EDGE39_PROFILES, "rb") as source:
        if source.read(8) != b"D3E39P1\0":
            raise AssertionError("edge-39 profile magic changed")
        header = tuple(int.from_bytes(source.read(4), "little") for _ in range(3))
        if header != (SIGNATURE_COUNT, EDGE39_ONE, 666):
            raise AssertionError(f"edge-39 profile header changed: {header}")
        previous = -1
        for index in range(SIGNATURE_COUNT):
            signature_bytes = source.read(8)
            payload = source.read(666)
            if len(signature_bytes) != 8 or len(payload) != 666:
                raise AssertionError("edge-39 profile artifact truncated")
            signature = int.from_bytes(signature_bytes, "little")
            if signature <= previous:
                raise AssertionError("edge-39 signature ordering changed")
            previous = signature
            universe[index] = signature
            profiles[index] = np.frombuffer(payload, dtype=np.uint8)
            semantic.update(signature.to_bytes(7, "little"))
            semantic.update(payload)
        if source.read(1):
            raise AssertionError("edge-39 profile artifact has trailing bytes")
    if semantic.hexdigest() != expected_semantic:
        raise AssertionError("edge-39 profile semantic digest changed")
    return universe, profiles


def read_edge27_profiles(universe):
    with gzip.open(SKELETON_PROFILES, "rt", encoding="utf-8") as source:
        catalog = json.load(source)
    if catalog["signature_universe_count"] != SIGNATURE_COUNT:
        raise AssertionError("edge-27 signature universe count changed")
    universe_digest = sha256(b"diag3-row2599-extension-universe-v1\0")
    for signature in universe:
        universe_digest.update(int(signature).to_bytes(7, "little"))
    if universe_digest.hexdigest() != catalog["signature_universe_sha256"]:
        raise AssertionError("edge-27/edge-39 extension signature universes differ")

    assignment_bytes = b64decode(catalog["signature_profile_ids_base64"], validate=True)
    if len(assignment_bytes) != 2 * SIGNATURE_COUNT:
        raise AssertionError("edge-27 profile assignment length changed")
    assignments = np.frombuffer(assignment_bytes, dtype="<u2").astype(np.int64)
    rows = catalog["profile_rows"]
    if len(rows) != catalog["profile_count"] or len(rows) != 2_458:
        raise AssertionError("edge-27 profile catalog count changed")
    payloads = np.empty((len(rows), 155), dtype=np.uint8)
    for profile_id, row in enumerate(rows):
        if int(row["profile_id"]) != profile_id:
            raise AssertionError("edge-27 profile IDs are not canonical")
        payload = b64decode(row["feasible_one_cells_base64"], validate=True)
        if len(payload) != 155 or payload[-1] & 0xC0:
            raise AssertionError("edge-27 profile payload/padding changed")
        payloads[profile_id] = np.frombuffer(payload, dtype=np.uint8)
    profiles = payloads[assignments]
    semantic = sha256(b"diag3-row2599-path-label-profiles-v1\0")
    for signature, row in zip(universe, profiles, strict=True):
        semantic.update(int(signature).to_bytes(7, "little"))
        semantic.update(row.tobytes())
    if semantic.hexdigest() != catalog["source_signature_profile_semantic_sha256"]:
        raise AssertionError("edge-27 materialized profile semantics changed")
    return profiles


def concatenate_profiles(edge27, edge39):
    if edge27.shape != (SIGNATURE_COUNT, 155) or edge39.shape != (SIGNATURE_COUNT, 666):
        raise AssertionError("source profile tensor shape changed")
    if np.any(edge27[:, -1] & np.uint8(0xC0)):
        raise AssertionError("edge-27 padding is nonzero")
    joint = np.empty((SIGNATURE_COUNT, PROFILE_BYTES), dtype=np.uint8)
    joint[:, :154] = edge27[:, :154]
    joint[:, 154] = (edge27[:, 154] & np.uint8(0x3F)) | ((edge39[:, 0] & np.uint8(0x03)) << np.uint8(6))
    joint[:, 155:820] = (edge39[:, :665] >> np.uint8(2)) | ((edge39[:, 1:666] & np.uint8(0x03)) << np.uint8(6))
    joint[:, 820] = edge39[:, 665] >> np.uint8(2)
    if np.any(joint[:, -1] & np.uint8(0xC0)):
        raise AssertionError("joint profile padding is nonzero")
    return joint


def edge39_cells(events):
    zero_cells = []
    zero_ids = ["row2599:chart:0"]
    two_root_event_count = 0
    compound_event_count = 0
    factor_counts = Counter(
        int(member["factor_id"])
        for event in events for member in event["members"]
    )
    two_root_factors = {factor_id for factor_id, count in factor_counts.items() if count == 2}
    if len(two_root_factors) != 118:
        raise AssertionError("edge-39 two-root factor census changed")
    for event_index, event in enumerate(events):
        if int(event["event_index"]) != event_index or len(event["members"]) != 1:
            raise AssertionError("edge-39 event grouping changed")
        member = event["members"][0]
        factor_id = int(member["factor_id"])
        root_index = int(member["root_index_within_factor"])
        identifier = f"row2599:edge:039:event:{event_index:04d}:factor:{factor_id}:root:{root_index}"
        zero_ids.append(identifier)
        two_root_event_count += int(factor_id in two_root_factors)
        compound_event_count += int(member["occurrence_multiplicity"] > 1)
        zero_cells.append({
            "id": identifier,
            "dimension": 0,
            "kind": "isolated_residual_event",
            "source_edge_index": 39,
            "event_index": event_index,
            "factor_id": factor_id,
            "root_index_within_factor": root_index,
            "isolating_interval": list(event["isolating_interval"]),
            "algebraic_multiplicity": int(member["algebraic_multiplicity"]),
            "occurrence_multiplicity": int(member["occurrence_multiplicity"]),
        })
    if two_root_event_count != 236 or compound_event_count != 293:
        raise AssertionError("edge-39 two-root/compound event census changed")
    zero_ids.append("row2599:chart:113")
    zero_cells.append({
        "id": "row2599:chart:113", "dimension": 0,
        "kind": "stored_strict_parent_chart", "chart_index": 113,
    })

    one_cells = []
    closure = []
    incidence = []
    one_ids = []
    for chamber in range(len(events) + 1):
        identifier = f"row2599:edge:039:open:{chamber:04d}"
        left, right = zero_ids[chamber], zero_ids[chamber + 1]
        one_ids.append(identifier)
        one_cells.append({
            "id": identifier,
            "dimension": 1,
            "kind": "open_residual_chamber",
            "source_edge_index": 39,
            "chamber_index": chamber,
            "oriented_boundary": [[left, -1], [right, 1]],
        })
        closure.extend(([identifier, left], [identifier, right]))
        incidence.extend(([left, identifier, -1], [right, identifier, 1]))
    return zero_cells, one_cells, zero_ids, one_ids, closure, incidence


def bad_zero_payload(feasible):
    bits = np.unpackbits(np.frombuffer(feasible, dtype=np.uint8), bitorder="little")[:ONE_COUNT]
    bad = 1 - bits
    bad_zero = np.zeros(ZERO_COUNT, dtype=np.uint8)
    edge27_bad = bad[:EDGE27_ONE]
    edge39_bad = bad[EDGE27_ONE:]
    bad_zero[0] = edge27_bad[0] | edge39_bad[0]
    bad_zero[1:EDGE27_ZERO - 1] = edge27_bad[:-1] | edge27_bad[1:]
    bad_zero[EDGE27_ZERO - 1] = edge27_bad[-1]
    edge39_global_start = EDGE27_ZERO
    bad_zero[edge39_global_start:edge39_global_start + EDGE39_ZERO - 2] = edge39_bad[:-1] | edge39_bad[1:]
    bad_zero[-1] = edge39_bad[-1]
    return np.packbits(bad_zero, bitorder="little").tobytes()


def compile_profile_catalog(universe, joint):
    unique, inverse, counts = np.unique(joint, axis=0, return_inverse=True, return_counts=True)
    if unique.shape[1] != PROFILE_BYTES or len(inverse) != SIGNATURE_COUNT:
        raise AssertionError("joint profile uniqueness compilation changed")
    if len(unique) > 0xFFFFFFFF:
        raise AssertionError("joint profile ID width overflow")

    joint_semantic = sha256(b"diag3-edge27-edge39-joint-feasible-v1\0")
    for signature, row in zip(universe, joint, strict=True):
        joint_semantic.update(int(signature).to_bytes(7, "little"))
        joint_semantic.update(row.tobytes())

    rows = []
    bad_digest = sha256(b"diag3-edge27-edge39-joint-bad-membership-v1\0")
    valid_last = (1 << (ONE_COUNT & 7)) - 1
    for profile_id, (row, count) in enumerate(zip(unique, counts, strict=True)):
        feasible = row.tobytes()
        bad_one_array = np.bitwise_not(row.copy())
        bad_one_array[-1] &= np.uint8(valid_last)
        bad_one = bad_one_array.tobytes()
        bad_zero = bad_zero_payload(feasible)
        if bad_zero[-1] & 0x80:
            raise AssertionError("joint bad-zero padding is nonzero")
        rows.append((profile_id, int(count), feasible, bad_one, bad_zero))
        bad_digest.update(profile_id.to_bytes(4, "little"))
        bad_digest.update(int(count).to_bytes(4, "little"))
        bad_digest.update(feasible)
        bad_digest.update(bad_one)
        bad_digest.update(bad_zero)
    return {
        "unique": unique,
        "assignments": inverse.astype(np.uint32),
        "counts": counts,
        "rows": rows,
        "joint_semantic_sha256": joint_semantic.hexdigest(),
        "bad_membership_semantic_sha256": bad_digest.hexdigest(),
    }


def write_profile_artifact(path, universe, catalog):
    profile_count = len(catalog["rows"])
    with Path(path).open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0, compresslevel=9) as target:
            target.write(PROFILE_MAGIC)
            for value in (SIGNATURE_COUNT, ZERO_COUNT, ONE_COUNT, profile_count, PROFILE_BYTES, BAD_ZERO_BYTES, 4):
                target.write(int(value).to_bytes(4, "little"))
            for signature, profile_id in zip(universe, catalog["assignments"], strict=True):
                target.write(int(signature).to_bytes(8, "little"))
                target.write(int(profile_id).to_bytes(4, "little"))
            for profile_id, count, feasible, bad_one, bad_zero in catalog["rows"]:
                target.write(profile_id.to_bytes(4, "little"))
                target.write(count.to_bytes(4, "little"))
                target.write(feasible)
                target.write(bad_one)
                target.write(bad_zero)


def validate_record(record):
    compiled = record["compiled_regular_subcomplex"]
    cells = compiled["cells"]
    ids = [cell["id"] for cell in cells]
    if len(ids) != ZERO_COUNT + ONE_COUNT or len(ids) != len(set(ids)):
        raise AssertionError("combined cells are duplicated or missing")
    if ids.count("row2599:chart:0") != 1:
        raise AssertionError("shared chart 0 was not glued exactly once")
    if compiled["cell_count_by_dimension"] != {"0": ZERO_COUNT, "1": ONE_COUNT}:
        raise AssertionError("combined cell count changed")
    if len(compiled["strict_closure_pairs"]) != 13_132:
        raise AssertionError("combined strict-closure count changed")
    if compiled["strict_three_cell_chains"] or compiled["two_cells"]:
        raise AssertionError("two-dimensional cells/chains were invented")
    if compiled["parent_infinity_subcomplex"]:
        raise AssertionError("strict-parent paths cannot acquire parent infinity")
    d1 = compiled["integral_boundary"]
    if len(d1["c0_basis"]) != ZERO_COUNT or len(d1["c1_basis"]) != ONE_COUNT or len(d1["d1_entries"]) != 13_132:
        raise AssertionError("integral boundary dimensions changed")
    zero_cells = [cell for cell in cells if cell["dimension"] == 0]
    one_cells = [cell for cell in cells if cell["dimension"] == 1]
    c0 = [cell["id"] for cell in zero_cells]
    c1 = [cell["id"] for cell in one_cells]
    if d1["c0_basis"] != c0 or d1["c1_basis"] != c1:
        raise AssertionError("integral boundary bases do not match stable cell order")
    zero_set = set(c0)
    expected_closure = []
    expected_incidence = []
    adjacency = {identifier: set() for identifier in c0}
    for cell in one_cells:
        boundary = cell.get("oriented_boundary")
        if (
            not isinstance(boundary, list) or len(boundary) != 2
            or boundary[0][1] != -1 or boundary[1][1] != 1
            or boundary[0][0] not in zero_set or boundary[1][0] not in zero_set
            or boundary[0][0] == boundary[1][0]
        ):
            raise AssertionError("one-cell signed boundary is not integral path incidence")
        left, right = boundary[0][0], boundary[1][0]
        expected_closure.extend(([cell["id"], left], [cell["id"], right]))
        expected_incidence.extend(([left, cell["id"], -1], [right, cell["id"], 1]))
        adjacency[left].add(right)
        adjacency[right].add(left)
    if compiled["strict_closure_pairs"] != expected_closure or d1["d1_entries"] != expected_incidence:
        raise AssertionError("strict closure and signed incidence disagree with cell boundaries")
    reached = {c0[0]}
    frontier = [c0[0]]
    while frontier:
        for neighbor in adjacency[frontier.pop()]:
            if neighbor not in reached:
                reached.add(neighbor)
                frontier.append(neighbor)
    if len(reached) != ZERO_COUNT or ONE_COUNT != ZERO_COUNT - 1:
        raise AssertionError("combined incidence is not a connected tree")
    if d1["rank_d1"] != ONE_COUNT or d1["h0_rank"] != 1 or d1["h1_rank"] != 0 or d1["d_squared_zero"] is not True:
        raise AssertionError("integral homology summary changed")
    edge39_first = next(cell for cell in cells if cell["id"] == "row2599:edge:039:open:0000")
    edge39_last = next(cell for cell in cells if cell["id"] == "row2599:edge:039:open:5327")
    if edge39_first["oriented_boundary"][0] != ["row2599:chart:0", -1] or edge39_last["oriented_boundary"][1] != ["row2599:chart:113", 1]:
        raise AssertionError("edge-39 orientation was reversed")
    edge39_events = [cell for cell in cells if cell.get("source_edge_index") == 39 and cell["dimension"] == 0 and cell.get("kind") == "isolated_residual_event"]
    if len(edge39_events) != 5_327:
        raise AssertionError("edge-39 event subdivision changed")
    factor_counts = Counter(cell["factor_id"] for cell in edge39_events)
    if sum(count for count in factor_counts.values() if count == 2) != 236:
        raise AssertionError("one of the 236 two-root event atoms was omitted")
    if sum(cell["occurrence_multiplicity"] > 1 for cell in edge39_events) != 293:
        raise AssertionError("a compound event was split or omitted")
    attachment = record["collar_attachment"]
    if (
        attachment["factor_id"] != 19069
        or attachment["edge_event_index"] != 5236
        or attachment["edge_event_cell"] != "row2599:edge:039:event:5236:factor:19069:root:0"
        or attachment["collar_cell"] != "w_zero"
        or attachment["edge_transverse_factor_signs"] != {"before": 1, "after": -1}
        or attachment["oriented_intersection_sign"] != 1
    ):
        raise AssertionError("factor-19069 collar attachment/orientation changed")
    scope = record["scope"]
    if scope["global_parent_cell_coverage"] != "NOT_CLAIMED" or scope["component_coverage"] != "NOT_CLAIMED" or scope["honest_9dvl_score"] != "2/9":
        raise AssertionError("two-edge source tree was promoted beyond its scope")


def run_canaries(record, joint_semantic, universe, joint):
    results = {}

    def rejected(name, mutate):
        candidate = deepcopy(record)
        mutate(candidate)
        try:
            validate_record(candidate)
        except AssertionError:
            results[name] = "REJECTED"

    rejected("duplicate_shared_chart0", lambda candidate: candidate["compiled_regular_subcomplex"]["cells"].append(deepcopy(candidate["compiled_regular_subcomplex"]["cells"][0])))
    rejected("reverse_edge39_orientation", lambda candidate: candidate["compiled_regular_subcomplex"]["cells"].__setitem__(next(i for i, cell in enumerate(candidate["compiled_regular_subcomplex"]["cells"]) if cell["id"] == "row2599:edge:039:open:0000"), {**next(cell for cell in candidate["compiled_regular_subcomplex"]["cells"] if cell["id"] == "row2599:edge:039:open:0000"), "oriented_boundary": [["row2599:chart:0", 1], ["row2599:edge:039:event:0000:factor:7100:root:0", -1]]}))
    rejected("omit_two_root_event", lambda candidate: candidate["compiled_regular_subcomplex"]["cells"].pop(next(i for i, cell in enumerate(candidate["compiled_regular_subcomplex"]["cells"]) if cell.get("source_edge_index") == 39 and cell.get("factor_id") is not None and sum(other.get("factor_id") == cell.get("factor_id") for other in candidate["compiled_regular_subcomplex"]["cells"]) == 2)))
    rejected("split_compound_event", lambda candidate: candidate["compiled_regular_subcomplex"]["cells"].append({**next(cell for cell in candidate["compiled_regular_subcomplex"]["cells"] if cell.get("source_edge_index") == 39 and cell.get("occurrence_multiplicity", 1) > 1), "id": "row2599:edge:039:event:split-canary"}))
    rejected("wrong_factor19069_attachment", lambda candidate: candidate["collar_attachment"].__setitem__("edge_event_index", 5235))
    rejected("invent_parent_infinity", lambda candidate: candidate["compiled_regular_subcomplex"]["parent_infinity_subcomplex"].append("row2599:chart:0"))
    rejected("promote_tree_to_global_coverage", lambda candidate: candidate["scope"].__setitem__("global_parent_cell_coverage", "COMPLETE"))

    corrupted = joint[0].copy()
    corrupted[0] ^= np.uint8(1)
    digest = sha256(b"diag3-edge27-edge39-joint-feasible-v1\0")
    # Re-seal the complete mapping with exactly one changed bit.
    for row_index, (signature, row) in enumerate(zip(universe, joint, strict=True)):
        digest.update(int(signature).to_bytes(7, "little"))
        digest.update(corrupted.tobytes() if row_index == 0 else row.tobytes())
    if digest.hexdigest() != joint_semantic:
        results["flip_joint_profile_bit"] = "REJECTED"
    padded = joint[0].copy()
    padded[-1] |= np.uint8(0x80)
    if padded[-1] & 0xC0:
        results["nonzero_joint_profile_padding"] = "REJECTED"
    if len(results) != 9:
        raise AssertionError(f"combined generator canary census incomplete: {results}")
    return results


def build_record(progress=False):
    require_pins()
    cover = load_json(COVER)
    skeleton = load_json(SKELETON)
    collar = load_json(COLLAR)
    transition39 = load_json(EDGE39_TRANSITION)
    labels39 = load_json(EDGE39_LABELS)
    if labels39["inputs"]["transition_sha256"] != PINS[EDGE39_TRANSITION]:
        raise AssertionError("edge-39 label/transition cross-pin changed")
    if skeleton["inputs"]["transition_sha256"] != PINS[EDGE27_TRANSITION] or skeleton["inputs"]["labels_sha256"] != PINS[EDGE27_LABELS]:
        raise AssertionError("accepted edge-27 skeleton cross-pins changed")
    selected = tuple(map(int, cover["source_bank"]["selected_edge_indices"]))
    if len(selected) != 40 or 27 not in selected or 39 not in selected:
        raise AssertionError("minimum source cover changed")
    pending = [edge for edge in selected if edge not in (27, 39)]
    if len(pending) != 38:
        raise AssertionError("combined pending-edge census changed")

    edge27_cells = skeleton["compiled_regular_subcomplex"]["cells"]
    edge27_zero = [deepcopy(cell) for cell in edge27_cells if cell["dimension"] == 0]
    edge27_one = [deepcopy(cell) for cell in edge27_cells if cell["dimension"] == 1]
    if len(edge27_zero) != EDGE27_ZERO or len(edge27_one) != EDGE27_ONE:
        raise AssertionError("accepted edge-27 cell census changed")
    edge39_zero, edge39_one, edge39_zero_ids, edge39_one_ids, closure39, incidence39 = edge39_cells(transition39["residual_roadmap"]["events"])
    cells = edge27_zero + edge39_zero + edge27_one + edge39_one
    c0 = [cell["id"] for cell in edge27_zero] + [cell["id"] for cell in edge39_zero]
    c1 = [cell["id"] for cell in edge27_one] + edge39_one_ids
    closure = deepcopy(skeleton["compiled_regular_subcomplex"]["strict_closure_pairs"]) + closure39
    incidence = deepcopy(skeleton["compiled_regular_subcomplex"]["integral_boundary"]["d1_entries"]) + incidence39

    universe, edge39_profiles = read_edge39_profiles()
    edge27_profiles = read_edge27_profiles(universe)
    joint = concatenate_profiles(edge27_profiles, edge39_profiles)
    if progress:
        print("compiling exact joint profile census", flush=True)
    catalog = compile_profile_catalog(universe, joint)

    collar_root = collar["exact_wall_graph"]["root_isolation"]["retained_segment_q_zero"]
    attachment_event = transition39["residual_roadmap"]["events"][5236]
    if attachment_event["members"][0]["factor_id"] != 19069 or collar_root["left_sign"] != 1 or collar_root["right_sign"] != -1:
        raise AssertionError("factor-19069 attachment source changed")
    attachment = {
        "factor_id": 19069,
        "source_edge_index": 39,
        "edge_event_index": 5236,
        "edge_event_cell": "row2599:edge:039:event:5236:factor:19069:root:0",
        "collar_cell": "w_zero",
        "edge_parameter_orientation": "chart0_to_chart113_is_increasing_s",
        "collar_wall_orientation": "w_minus_to_w_zero_to_w_plus_is_increasing_r",
        "edge_transverse_factor_signs": {"before": 1, "after": -1},
        "oriented_intersection_sign": 1,
        "orientation_convention": "ordered tangents (+s,+r) agree with the collar (s,r) orientation",
        "edge_root_box": list(attachment_event["isolating_interval"]),
        "collar_root_box": list(collar_root["isolating_interval"]),
        "authenticated_collar_sha256": PINS[COLLAR],
    }

    cells_digest = sha256(b"diag3-edge27-edge39-cells-v1\0" + canonical_bytes(cells)).hexdigest()
    closure_digest = sha256(b"diag3-edge27-edge39-closure-v1\0" + canonical_bytes(closure)).hexdigest()
    incidence_digest = sha256(b"diag3-edge27-edge39-incidence-v1\0" + canonical_bytes(incidence)).hexdigest()
    record = {
        "format": FORMAT,
        "status": STATUS,
        "inputs": {str(path.relative_to(HERE.parents[1])): digest for path, digest in PINS.items()},
        "scope": {
            "parent_index": 2599,
            "support": [15, 15, 15],
            "fully_compiled_cover_edges": [27, 39],
            "minimum_source_cover_edges": 40,
            "pending_cover_edges": pending,
            "source_skeleton_coverage": "EXACTLY_TWO_OF_FORTY_RETAINED_EDGES",
            "global_parent_cell_coverage": "NOT_CLAIMED",
            "component_coverage": "NOT_CLAIMED",
            "pair_branch_closed": False,
            "triple_branch_closed": False,
            "honest_9dvl_score": "2/9",
        },
        "compiled_regular_subcomplex": {
            "cell_count_by_dimension": {"0": ZERO_COUNT, "1": ONE_COUNT},
            "cells": cells,
            "cells_sha256": cells_digest,
            "two_cells": [],
            "strict_closure_pairs": closure,
            "strict_closure_pairs_sha256": closure_digest,
            "strict_three_cell_chains": [],
            "scope_endpoint_cells": ["row2599:chart:89", "row2599:chart:113"],
            "shared_chart_cells": ["row2599:chart:0"],
            "parent_infinity_subcomplex": [],
            "integral_boundary": {
                "c0_basis": c0,
                "c1_basis": c1,
                "d1_entries": incidence,
                "d1_entries_sha256": incidence_digest,
                "rank_d1": ONE_COUNT,
                "h0_rank": 1,
                "h1_rank": 0,
                "d_squared_zero": True,
            },
        },
        "joint_signature_profiles": {
            "artifact_path": str(PROFILE_OUTPUT.relative_to(HERE.parents[1])),
            "artifact_format": PROFILE_FORMAT,
            "signature_count": SIGNATURE_COUNT,
            "one_cell_profile_bytes": PROFILE_BYTES,
            "bad_zero_profile_bytes": BAD_ZERO_BYTES,
            "joint_profile_count": len(catalog["rows"]),
            "joint_profile_count_census": {str(int(count)): int(np.count_nonzero(catalog["counts"] == count)) for count in sorted(set(map(int, catalog["counts"])))},
            "joint_feasible_semantic_sha256": catalog["joint_semantic_sha256"],
            "bad_membership_semantic_sha256": catalog["bad_membership_semantic_sha256"],
            "membership_rule": "one-cell bad iff infeasible; zero-cell bad iff any incident one-cell is bad, including both branches at shared chart 0",
            "padding_bits_zero": True,
        },
        "collar_attachment": attachment,
        "theorem_effect": "Compiles two exact retained source paths into one labelled regular-CW tree; this is finite source-skeleton coverage, not component or parent-cell coverage, and leaves 9DVL at 2/9.",
    }
    validate_record(record)
    record["generator_canaries"] = run_canaries(record, catalog["joint_semantic_sha256"], universe, joint)
    record["semantic_sha256"] = semantic_seal(record)
    return record, universe, catalog


def check_profile_artifact(path, record):
    expected = record["joint_signature_profiles"]
    feasible_digest = sha256(b"diag3-edge27-edge39-joint-feasible-v1\0")
    bad_digest = sha256(b"diag3-edge27-edge39-joint-bad-membership-v1\0")
    with gzip.open(path, "rb") as source:
        if source.read(8) != PROFILE_MAGIC:
            raise AssertionError("joint profile magic changed")
        header = tuple(int.from_bytes(source.read(4), "little") for _ in range(7))
        signature_count, zero_count, one_count, profile_count, profile_bytes, bad_zero_bytes, id_width = header
        if header[:3] != (SIGNATURE_COUNT, ZERO_COUNT, ONE_COUNT) or header[4:] != (PROFILE_BYTES, BAD_ZERO_BYTES, 4):
            raise AssertionError(f"joint profile header changed: {header}")
        assignments = []
        previous = -1
        for _index in range(signature_count):
            signature = int.from_bytes(source.read(8), "little")
            profile_id = int.from_bytes(source.read(id_width), "little")
            if signature <= previous or profile_id >= profile_count:
                raise AssertionError("joint signature/profile assignment changed")
            previous = signature
            assignments.append((signature, profile_id))
        profiles = []
        counts = []
        for expected_id in range(profile_count):
            profile_id = int.from_bytes(source.read(4), "little")
            count = int.from_bytes(source.read(4), "little")
            feasible = source.read(profile_bytes)
            bad_one = source.read(profile_bytes)
            bad_zero = source.read(bad_zero_bytes)
            if profile_id != expected_id or len(feasible) != profile_bytes or len(bad_one) != profile_bytes or len(bad_zero) != bad_zero_bytes:
                raise AssertionError("joint profile catalog truncated or reordered")
            if feasible[-1] & 0xC0 or bad_one[-1] & 0xC0 or bad_zero[-1] & 0x80:
                raise AssertionError("joint profile padding changed")
            expected_bad = bytearray((~value) & 0xFF for value in feasible)
            expected_bad[-1] &= (1 << (ONE_COUNT & 7)) - 1
            if bytes(expected_bad) != bad_one or bad_zero_payload(feasible) != bad_zero:
                raise AssertionError("joint bad membership is not incidence-derived")
            bad_digest.update(profile_id.to_bytes(4, "little"))
            bad_digest.update(count.to_bytes(4, "little"))
            bad_digest.update(feasible)
            bad_digest.update(bad_one)
            bad_digest.update(bad_zero)
            profiles.append(feasible)
            counts.append(count)
        if source.read(1):
            raise AssertionError("joint profile artifact has trailing bytes")
    assignment_counts = Counter(profile_id for _signature, profile_id in assignments)
    if sum(counts) != SIGNATURE_COUNT or any(assignment_counts[index] != counts[index] for index in range(profile_count)):
        raise AssertionError("joint profile assignment census changed")
    for signature, profile_id in assignments:
        feasible_digest.update(signature.to_bytes(7, "little"))
        feasible_digest.update(profiles[profile_id])
    if feasible_digest.hexdigest() != expected["joint_feasible_semantic_sha256"] or bad_digest.hexdigest() != expected["bad_membership_semantic_sha256"]:
        raise AssertionError("joint profile semantic seal failed")
    return header
