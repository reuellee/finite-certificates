#!/usr/bin/env python3
"""Hostile exact replay of the row-2599 64-box first-event certificate."""

from __future__ import annotations

from collections import Counter
import copy
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_MASTER_CLOSURE_FIRST_EVENT.json"
sys.path.insert(0, str(HERE))
import diag3_pair_first_event_core as core  # noqa: E402


EXPECTED_NODE_SHA256 = "ddec96b052b305d279b543be2af27e12f380f0dedc79ea434616c64b40cd8cea"
EXPECTED_CANDIDATE_SHA256 = "adb2e7257457f158e809450683c46fe7ecafdbdd4a7efdf9ac630e8a4f0fb03f"
EXPECTED_PARENT_SIGN_SHA256 = "1d9b940e2bb954b5c69bcee8b2346f9554b2e15589ea4c5b3c3f8e1e943de701"


class CertificateError(AssertionError):
    pass


def require(condition, message):
    if not condition:
        raise CertificateError(message)


def validate(record, expected):
    require(record == expected, "certificate differs from exact source replay")
    require(core.file_sha256(core.NODE) == EXPECTED_NODE_SHA256, "node source digest")
    require(core.file_sha256(core.CANDIDATES) == EXPECTED_CANDIDATE_SHA256, "candidate source digest")
    parent_gate = json.loads(core.PARENT_GATE.read_text(encoding="utf-8"))
    require(parent_gate["normalized_parent_sign_sha256"] == EXPECTED_PARENT_SIGN_SHA256, "parent sign digest")

    require(record["format"] == core.FORMAT and record["status"] == core.STATUS, "format/status")
    require(record["scope"]["local_parameter_coverage"] == "COMPLETE", "local coverage")
    require(record["scope"]["global_parameter_coverage"] == "NOT_CLAIMED", "honest global scope")
    require(record["parent_infinity_subcomplex"] == [], "false parent infinity")

    cells = {row["id"]: row for row in record["cells"]}
    require(len(cells) == len(record["cells"]) == 399, "cell IDs/census")
    require(Counter(row["dimension"] for row in cells.values()) == {0: 110, 1: 199, 2: 90}, "cell dimensions")
    immediate = {(identifier, face) for identifier, row in cells.items() for face in row["boundary"]}
    closure = {tuple(row) for row in record["strict_closure_pairs"]}
    chains = {tuple(row) for row in record["strict_three_cell_chains"]}
    require(len(closure) == 1118 and len(chains) == 720, "closure/chain census")
    require(immediate <= closure, "immediate closure missing")
    require(all(cells[high]["dimension"] > cells[low]["dimension"] for high, low in closure), "closure dimension")
    for high, middle in immediate:
        for middle2, low in immediate:
            if middle == middle2:
                require((high, low) in closure and (high, middle, low) in chains, "closure transitivity")

    segments = record["boundary_word_segments"]
    require(len(segments) == 171, "boundary-word census")
    require(sum(len(row["incidents"]) == 2 for row in segments) == 133, "shared boundary census")
    for row in segments:
        require(0 not in row["open_segment_sign_word"], f"unsplit boundary word {row['id']}")
        require(len(row["incidents"]) in (1, 2), f"boundary incidence {row['id']}")
        if len(row["incidents"]) == 2:
            require(row["incidents"][0]["orientation"] == -row["incidents"][1]["orientation"], f"shared orientation {row['id']}")

    boxes = record["boxes"]
    require(len(boxes) == 64, "box ceiling/census")
    require(Counter(row["classification"] for row in boxes) == {"no_wall": 42, "one_wall": 20, "transverse_two_wall": 2}, "box classes")
    cover = Counter()
    for row in boxes:
        box_cells = set(row["closure_cells"])
        cover.update(box_cells)
        for high, low in closure:
            if high in box_cells:
                require(low in box_cells, f"box is not a subcomplex: {row['id']}")
    require(set(cover) == set(cells), "box cover misses a cell")
    require(all(cover[identifier] == 1 for identifier, row in cells.items() if row["dimension"] == 2), "box interiors overlap")

    for field in ("scope_boundary_subcomplex", "atlas_seam_subcomplex", "residual_wall_subcomplex"):
        subcomplex = set(record[field])
        for high, low in closure:
            if high in subcomplex:
                require(low in subcomplex, f"{field} is not closed")

    boundary = record["integral_boundary"]
    d1 = {(row, column): int(value) for row, column, value in boundary["d1_entries"]}
    d2 = {(row, column): int(value) for row, column, value in boundary["d2_entries"]}
    for vertex in boundary["c0_basis"]:
        for face in boundary["c2_basis"]:
            require(
                sum(d1.get((vertex, edge), 0) * d2.get((edge, face), 0) for edge in boundary["c1_basis"]) == 0,
                "integral d_squared",
            )

    source = record["signature_profile_source"]
    require(source["universe_count"] == 97_224, "signature universe")
    require(sum(row["signature_count"] for row in source["profiles"]) == 97_224, "signature accounting")
    require({row["feasible_chamber_mask"] for row in source["profiles"]} == set(core.EXPECTED_PROFILE_COUNTS), "profile masks")
    for row in source["profiles"]:
        bad = set(row["bad_cells"])
        for high, low in closure:
            if high in bad:
                require(low in bad, f"profile bad locus not closed: {row['feasible_chamber_mask']}")

    replay = record["rank_replay"]
    require(replay["barycentric_cell_census"] == {"0": 399, "1": 1118, "2": 720}, "barycentric census")
    require(replay["unordered_profile_multisets"] == 120, "profile multiset census")
    require(replay["ordered_profile_triples"] == 512, "ordered profile census")
    require(sum(row["profile_triple_count"] for row in replay["rank_histogram"]) == 512, "rank histogram accounting")
    require(all(row["dim_h1"] == 0 for row in replay["rank_histogram"]), "nonzero middle rank")
    require(replay["nonzero_middle_profile_triples"] == [], "hidden nonzero triples")
    return replay


def assert_rejected(record, expected, label):
    try:
        validate(record, expected)
    except (CertificateError, KeyError, ValueError, TypeError):
        return
    raise AssertionError(f"hostile canary was accepted: {label}")


def main():
    record = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    expected = core.build_record()
    replay = validate(record, expected)

    hostile = []
    corrupt = copy.deepcopy(record)
    corrupt["coverage_evidence"]["kind"] = "sample_bank"
    hostile.append((corrupt, "sample bank as coverage"))
    corrupt = copy.deepcopy(record)
    corrupt["coverage_evidence"]["first_event_derived_row_indices"] = [2, 8, 22, 48]
    hostile.append((corrupt, "wrong first-event factor"))
    corrupt = copy.deepcopy(record)
    corrupt["coverage_evidence"]["minimum_other_domain_margin_ratio"] = "0"
    hostile.append((corrupt, "lost residual dominance"))
    corrupt = copy.deepcopy(record)
    corrupt["boxes"].pop()
    hostile.append((corrupt, "missing box"))
    corrupt = copy.deepcopy(record)
    corrupt["boxes"][0]["classification"] = "no_wall" if corrupt["boxes"][0]["classification"] != "no_wall" else "one_wall"
    hostile.append((corrupt, "false box classification"))
    corrupt = copy.deepcopy(record)
    corrupt["boundary_word_segments"][0]["open_segment_sign_word"][0] *= -1
    hostile.append((corrupt, "corrupt boundary word"))
    corrupt = copy.deepcopy(record)
    corrupt["strict_closure_pairs"].pop()
    hostile.append((corrupt, "incomplete closure"))
    corrupt = copy.deepcopy(record)
    corrupt["parent_infinity_subcomplex"] = corrupt["scope_boundary_subcomplex"][:2]
    hostile.append((corrupt, "scope boundary as parent infinity"))
    corrupt = copy.deepcopy(record)
    corrupt["signature_profile_source"]["profiles"][0]["signature_count"] -= 1
    hostile.append((corrupt, "incomplete signatures"))
    corrupt = copy.deepcopy(record)
    corrupt["integral_boundary"]["d2_entries"][0][2] *= -1
    hostile.append((corrupt, "nonzero d_squared"))
    corrupt = copy.deepcopy(record)
    corrupt["rank_replay"]["rank_histogram"][0]["dim_h1"] = 1
    hostile.append((corrupt, "dishonest middle rank"))
    corrupt = copy.deepcopy(record)
    corrupt["stop_contract"]["used_boxes"] = 63
    hostile.append((corrupt, "dishonest stop ledger"))
    corrupt = copy.deepcopy(record)
    corrupt["inputs"]["candidate_factor_sha256"] = "0" * 64
    hostile.append((corrupt, "corrupt active-factor digest"))
    for corrupt, label in hostile:
        assert_rejected(corrupt, expected, label)

    print("PASS exact row-2599 64-box first-new-event atlas")
    print("PASS unique first affine residual event at derived rows (2,8,22,49)")
    print("PASS all other 84,839 event factors and all 70 parent brackets avoid the domain")
    print("PASS 64 boxes: 42 no-wall + 20 one-wall + 2 transverse two-wall")
    print("PASS 171 boundary words, 133 shared gluings, and 399-cell regular CW atlas")
    print("PASS barycentric 399/1118/720 cells and all 512 ordered profile triples have H1=0")
    print("RANK_SEMANTIC_SHA256", replay["semantic_sha256"])
    print("PASS 13/13 hostile corruptions rejected")
    print("SCOPE complete on one bounded 2D first-event atlas; no full row-2599 or 9D coverage claim")


if __name__ == "__main__":
    main()
