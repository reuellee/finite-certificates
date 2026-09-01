#!/usr/bin/env python3
"""Independent exact replay of the row-2599 master-closure node canary.

Unlike the schema fixture, this verifier does not accept producer declarations
of coverage, regularity, boundary type, or signature labels.  It recomputes
the two-branch semialgebraic partition from the source parent matrix, checks
every residual occurrence and parent bracket, reconstructs the regular-CW
closure object, and replays the balanced pair complex on every local
signature-profile triple.
"""

from __future__ import annotations

from collections import Counter
import copy
from fractions import Fraction
from hashlib import sha256
from itertools import product
import json
from pathlib import Path

import diag3_research_ledger_compatibility as ledger_compat
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
CERTIFICATE = DATA / "DIAG3_PAIR_MASTER_CLOSURE_NODE_CANARY.json"
NODE = DATA / "DIAG9_GRAPH_row2599_node_roadmap.npz"
CANDIDATES = DATA / "DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin"
LEDGER = DATA / "DIAG3_RESEARCH_DECISION_LEDGER.json"
PARENT_GATE = DATA / "DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json"

sys.path.insert(0, str(HERE))
import DIAG9_GRAPH_verify_row2599_node as node  # noqa: E402
import four_chart_gate as extension_gate  # noqa: E402
import verify_diag3_pair_global_candidate_factors as candidate_input  # noqa: E402
import verify_diag3_pair_global_master_quotient as master  # noqa: E402


FORMAT = "diag3-pair-master-closure-certificate-v1"
STATUS = "LOCAL_EXACT_CANARY"
EXPECTED_NODE_SHA256 = (
    "ddec96b052b305d279b543be2af27e12f380f0dedc79ea434616c64b40cd8cea"
)
EXPECTED_CANDIDATE_SHA256 = (
    "adb2e7257457f158e809450683c46fe7ecafdbdd4a7efdf9ac630e8a4f0fb03f"
)
EXPECTED_PARENT_SIGN_SHA256 = (
    "1d9b940e2bb954b5c69bcee8b2346f9554b2e15589ea4c5b3c3f8e1e943de701"
)
EXPECTED_PROFILE_COUNTS = {0: 70_968, 3: 72, 6: 72, 9: 72, 12: 72, 15: 25_968}
CYCLIC_WALLS = ("w0", "w3", "w1", "w2")
CHAMBERS = ("c0", "c1", "c2", "c3")
BOUNDARY_VERTICES = ("p0", "p1", "p2", "p3")
SCOPE_ARCS = ("b0", "b1", "b2", "b3")


class CertificateError(AssertionError):
    pass


def require(condition, message):
    if not condition:
        raise CertificateError(message)


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_fraction(value: str) -> Fraction:
    return Fraction(value)


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def branch_endpoints():
    endpoints = []
    for linear in node.CENTERED_BRANCHES:
        coefficient_x = linear[(1, 0)]
        coefficient_y = linear[(0, 1)]
        scale = node.RADIUS / max(abs(coefficient_x), abs(coefficient_y))
        tangent = (scale * coefficient_y, -scale * coefficient_x)
        endpoints.extend(((-tangent[0], -tangent[1]), tangent))
    return {"w0": endpoints[0], "w1": endpoints[1], "w2": endpoints[2], "w3": endpoints[3]}


def expected_cells():
    endpoints = branch_endpoints()
    wall_incident = {
        "w0": ("c0", "c3"),
        "w1": ("c1", "c2"),
        "w2": ("c2", "c3"),
        "w3": ("c0", "c1"),
    }
    result = {
        "v": (0, "residual_node", (Fraction(0), Fraction(0)), (), CHAMBERS)
    }
    for index, wall in enumerate(CYCLIC_WALLS):
        result[BOUNDARY_VERTICES[index]] = (
            0,
            "scope_boundary_residual_endpoint",
            endpoints[wall],
            (),
            wall_incident[wall],
        )
        result[wall] = (
            1,
            "residual_wall_ray",
            (endpoints[wall][0] / 2, endpoints[wall][1] / 2),
            ("v", BOUNDARY_VERTICES[index]),
            wall_incident[wall],
        )
    corners = (
        (node.RADIUS, node.RADIUS),
        (node.RADIUS, -node.RADIUS),
        (-node.RADIUS, -node.RADIUS),
        (-node.RADIUS, node.RADIUS),
    )
    for index, chamber in enumerate(CHAMBERS):
        result[SCOPE_ARCS[index]] = (
            1,
            "scope_boundary_arc",
            corners[index],
            (BOUNDARY_VERTICES[index], BOUNDARY_VERTICES[(index + 1) % 4]),
            (chamber,),
        )
        result[chamber] = (
            2,
            "open_chamber",
            (corners[index][0] / 2, corners[index][1] / 2),
            (CYCLIC_WALLS[index], SCOPE_ARCS[index], CYCLIC_WALLS[(index + 1) % 4]),
            (chamber,),
        )
    return result


def closure_data(cells):
    immediate = {
        (identifier, face)
        for identifier, (_dimension, _kind, _witness, boundary, _incident) in cells.items()
        for face in boundary
    }
    closure = set(immediate)
    changed = True
    while changed:
        changed = False
        for high, middle in tuple(closure):
            for middle2, low in tuple(closure):
                if middle == middle2 and (high, low) not in closure:
                    closure.add((high, low))
                    changed = True
    chains = {
        (high, middle, low)
        for high, middle in immediate
        for middle2, low in immediate
        if middle == middle2
    }
    return immediate, closure, chains


def expected_integral_boundary():
    d1 = []
    for index, wall in enumerate(CYCLIC_WALLS):
        d1.extend((("v", wall, -1), (BOUNDARY_VERTICES[index], wall, 1)))
    for index, arc in enumerate(SCOPE_ARCS):
        d1.extend(
            (
                (BOUNDARY_VERTICES[index], arc, -1),
                (BOUNDARY_VERTICES[(index + 1) % 4], arc, 1),
            )
        )
    d2 = []
    for index, chamber in enumerate(CHAMBERS):
        d2.extend(
            (
                (CYCLIC_WALLS[index], chamber, 1),
                (SCOPE_ARCS[index], chamber, 1),
                (CYCLIC_WALLS[(index + 1) % 4], chamber, -1),
            )
        )
    return {
        "c0_basis": ("v", *BOUNDARY_VERTICES),
        "c1_basis": (*CYCLIC_WALLS, *SCOPE_ARCS),
        "c2_basis": CHAMBERS,
        "d1_entries": tuple(d1),
        "d2_entries": tuple(d2),
    }


def profile_map_from_exact_labels():
    cells, walls, exact_node = node.exact_labels()
    patterns = node.signature_patterns(cells)
    parents = [
        line.strip()
        for line in extension_gate.CATALOG_48.open(encoding="utf-8")
        if line.strip()
    ]
    _parent_bits, signatures = extension_gate.enumerate_extensions(
        parents[extension_gate.PARENT_INDEX]
    )
    require(len(signatures) == len(set(signatures)) == 97_224, "extension universe")
    require(set(patterns).issubset(signatures), "node label outside extension universe")
    digest = sha256(b"diag3-row2599-node-signature-profile-v1\0")
    counts = Counter()
    for signature in signatures:
        profile = patterns.get(signature, 0)
        counts[profile] += 1
        digest.update(int(signature).to_bytes(8, "little"))
        digest.update(bytes((profile,)))
    require(dict(sorted(counts.items())) == EXPECTED_PROFILE_COUNTS, "profile census")
    return cells, walls, exact_node, digest.hexdigest(), counts


def expected_bad_cells(cells, feasible_profile):
    bad_chambers = {
        chamber for index, chamber in enumerate(CHAMBERS)
        if not (feasible_profile >> index) & 1
    }
    return tuple(
        identifier
        for identifier, (_dimension, _kind, _witness, _boundary, incident) in cells.items()
        if bad_chambers.intersection(incident)
    )


def replay_sources():
    require(file_sha256(NODE) == EXPECTED_NODE_SHA256, "node roadmap SHA-256")
    require(file_sha256(CANDIDATES) == EXPECTED_CANDIDATE_SHA256, "candidate SHA-256")
    candidates = candidate_input.parse_artifact()
    require(len(candidates) == 17_824, "candidate factor count")

    parent_gate = json.loads(PARENT_GATE.read_text(encoding="utf-8"))
    require(
        parent_gate["normalized_parent_sign_sha256"] == EXPECTED_PARENT_SIGN_SHA256,
        "signed parent digest",
    )
    geometry = node.exact_geometry()
    labels = profile_map_from_exact_labels()
    return geometry, labels


def validate(record, sources):
    geometry, labels = sources
    require(
        set(record) == {
            "format", "status", "scope", "inputs", "generator",
            "coverage_evidence", "cells", "strict_closure_pairs",
            "strict_three_cell_chains", "scope_boundary_subcomplex",
            "parent_infinity_subcomplex", "signature_profile_source",
            "integral_boundary", "verifier",
        },
        "top-level fields",
    )
    require(record["format"] == FORMAT and record["status"] == STATUS, "format/status")

    scope = record["scope"]
    require(scope["parent_index"] == 2599, "parent")
    require(scope["compactification"] == "(Delta^3)^3", "compactification")
    require(scope["support"] == [15, 15, 15], "full support")
    require(scope["local_parameter_coverage"] == "COMPLETE", "local coverage claim")
    require(scope["global_parameter_coverage"] == "NOT_CLAIMED", "global scope")
    require(
        scope["scope_boundary_policy"] == "ordinary cells; never parent infinity",
        "scope boundary policy",
    )

    inputs = record["inputs"]
    require(inputs["node_roadmap_sha256"] == EXPECTED_NODE_SHA256, "node digest pin")
    require(inputs["candidate_factor_sha256"] == EXPECTED_CANDIDATE_SHA256, "candidate digest pin")
    require(inputs["target_signed_parent_digest"] == EXPECTED_PARENT_SIGN_SHA256, "parent digest pin")
    ledger = ledger_compat.historical_row2599(
        ledger_compat.load_current_ledger(LEDGER)
    )
    require(
        (
            inputs["candidate_factor_count"],
            inputs["exact_interior_nonempty_count"],
            inputs["exact_empty_count"],
            inputs["unresolved_feasibility_count"],
            inputs["active_wall_upper_bound"],
        )
        == (17_824, 10_844, 1_177, 5_803, 16_647),
        "factor accounting",
    )
    require(inputs["exact_empty_factor_digest"] == ledger["digests"]["empty_factor_ids"], "empty digest")
    require(inputs["unresolved_factor_digest"] == ledger["digests"]["unresolved_factor_ids"], "residue digest")

    require(record["generator"]["backend"] == "pinned_transverse_node_to_regular_cw_v1", "backend")
    require("transport" not in record and "transport_gate" not in record, "unproved transport gate")

    evidence = record["coverage_evidence"]
    require(evidence["kind"] == "exact_two_affine_branch_partition", "coverage kind")
    require(evidence["labelled_residual_occurrence_universe"] == 84_840, "residual universe")
    require(evidence["parent_bracket_count"] == 70, "parent bracket universe")
    stored_geometry = evidence["geometry"]
    require(
        stored_geometry["cell_coordinate_system"]
        == "x=s-center_s, y=u-center_u",
        "cell coordinate system",
    )
    require(
        stored_geometry["branch_coordinate_system"]
        == "original affine parameters s,u",
        "branch coordinate system",
    )
    require(stored_geometry["domain"] == {"kind": "closed_square", "radius": "1/1000"}, "disk domain")
    require(
        tuple(tuple(map(int, row)) for row in stored_geometry["branch_affine"])
        == tuple(
            (branch[(0, 0)], branch[(1, 0)], branch[(0, 1)])
            for branch in node.BRANCHES
        ),
        "branch equations",
    )
    require(stored_geometry["branch_occurrence_counts"] == [65, 65], "branch counts")
    require(stored_geometry["branch_quotient_degree_counts"] == [[32, 33], [32, 33]], "quotient census")
    require(int(stored_geometry["transverse_jacobian"]) == geometry["jacobian"], "Jacobian")
    for prefix, value in (
        ("other_margin", geometry["other_margin"]),
        ("branch0_margin", geometry["branch_margins"][0]),
        ("branch1_margin", geometry["branch_margins"][1]),
        ("bracket_margin", geometry["bracket_margin"]),
    ):
        require(parse_fraction(stored_geometry["dominance_margins"][prefix]) == value, f"{prefix}")

    # The exact determinant replay gives two transverse affine branches, no
    # other residual zero, no parent wall, and no corner hit.  Verify their
    # four boundary endpoints and chamber signs explicitly.  These facts make
    # the claimed fan a complete regular-CW partition of the entire square.
    endpoints = branch_endpoints()
    require(len(set(endpoints.values())) == 4, "distinct branch endpoints")
    expected_endpoint_signs = {
        "w0": (0, 1), "w1": (0, -1), "w2": (-1, 0), "w3": (1, 0)
    }
    for wall, point in endpoints.items():
        require(node.sign_pair(point) == expected_endpoint_signs[wall], f"endpoint {wall}")
    corners = (
        (node.RADIUS, node.RADIUS),
        (node.RADIUS, -node.RADIUS),
        (-node.RADIUS, -node.RADIUS),
        (-node.RADIUS, node.RADIUS),
    )
    require(tuple(node.sign_pair(point) for point in corners) == node.CELL_SIGNS, "corner chamber order")

    expected = expected_cells()
    stored_cells = record["cells"]
    by_id = {cell["id"]: cell for cell in stored_cells}
    require(len(by_id) == len(stored_cells) == len(expected) == 17, "cell census/IDs")
    require(set(by_id) == set(expected), "cell ID universe")
    for identifier, (dimension, kind, witness, boundary, incident) in expected.items():
        cell = by_id[identifier]
        require(set(cell) == {"id", "dimension", "kind", "witness", "boundary", "incident_chambers"}, f"cell fields {identifier}")
        require((cell["dimension"], cell["kind"]) == (dimension, kind), f"cell type {identifier}")
        require(tuple(map(parse_fraction, cell["witness"])) == witness, f"witness {identifier}")
        require(tuple(cell["boundary"]) == boundary, f"boundary {identifier}")
        require(tuple(cell["incident_chambers"]) == incident, f"incidence {identifier}")
        if dimension == 2:
            require(node.sign_pair(witness) == node.CELL_SIGNS[int(identifier[1:])], f"chamber witness {identifier}")

    immediate, closure, chains = closure_data(expected)
    require({tuple(row) for row in record["strict_closure_pairs"]} == closure, "strict closure")
    require({tuple(row) for row in record["strict_three_cell_chains"]} == chains, "strict three-chains")

    scope_boundary = set(record["scope_boundary_subcomplex"])
    require(scope_boundary == set(BOUNDARY_VERTICES + SCOPE_ARCS), "scope boundary")
    for high, low in closure:
        if high in scope_boundary:
            require(low in scope_boundary, "scope boundary is not a subcomplex")
    # All 70 parent brackets are certified nonzero on the disk.  Therefore no
    # cell in this local object can truthfully be tagged parent infinity.
    require(record["parent_infinity_subcomplex"] == [], "false parent infinity")

    _exact_cells, _walls, _exact_node, profile_digest, profile_counts = labels
    source = record["signature_profile_source"]
    require(source["universe_count"] == 97_224, "signature universe")
    require(source["semantic_sha256"] == profile_digest, "signature profile digest")
    profiles = {row["feasible_chamber_mask"]: row for row in source["profiles"]}
    require(tuple(profiles) == tuple(sorted(EXPECTED_PROFILE_COUNTS)), "profile order")
    for profile, count in EXPECTED_PROFILE_COUNTS.items():
        row = profiles[profile]
        require(row["signature_count"] == profile_counts[profile] == count, f"profile count {profile}")
        expected_bad = expected_bad_cells(expected, profile)
        require(
            set(row["bad_cells"]) == set(expected_bad)
            and len(row["bad_cells"]) == len(expected_bad),
            f"bad membership {profile}",
        )
        bad = set(expected_bad)
        for high, low in closure:
            if high in bad:
                require(low in bad, f"bad profile {profile} is not closed")

    boundary = record["integral_boundary"]
    expected_boundary = expected_integral_boundary()
    for key in ("c0_basis", "c1_basis", "c2_basis"):
        require(tuple(boundary[key]) == expected_boundary[key], f"{key}")
    d1_entries = tuple(tuple(row) for row in boundary["d1_entries"])
    d2_entries = tuple(tuple(row) for row in boundary["d2_entries"])
    require(d1_entries == expected_boundary["d1_entries"], "d1 entries")
    require(d2_entries == expected_boundary["d2_entries"], "d2 entries")
    d1 = {(row, column): int(value) for row, column, value in d1_entries}
    d2 = {(row, column): int(value) for row, column, value in d2_entries}
    for vertex in expected_boundary["c0_basis"]:
        for chamber in expected_boundary["c2_basis"]:
            total = sum(
                d1.get((vertex, edge), 0) * d2.get((edge, chamber), 0)
                for edge in expected_boundary["c1_basis"]
            )
            require(total == 0, "integral d_squared")

    # The outer square boundary is ordinary, not relative.  Reconstruct the
    # simplicial fan and replay every ordered profile triple.  This is the
    # first end-to-end local master-closure object: geometry -> closure ->
    # signature labels -> integral lift -> mod-two middle rank.
    fan, chamber_simplices = master.node_master()
    closed_fan = master.MasterComplex(fan.maximal, frozenset())
    bad_sets = {
        profile: master.bad_set_from_chamber_profile(
            closed_fan, chamber_simplices, profile
        )
        for profile in sorted(EXPECTED_PROFILE_COUNTS)
    }
    histogram = Counter()
    for profile_triple in product(sorted(EXPECTED_PROFILE_COUNTS), repeat=3):
        extraction = closed_fan.extract(
            tuple(bad_sets[profile] for profile in profile_triple)
        )
        result = extraction.result()
        require(result[-1] == 0, f"local middle residue {profile_triple}")
        histogram[result] += 1
    require(dict(histogram) == master.EXPECTED_NODE_CLOSED_RESULT_HISTOGRAM, "closed-disk rank histogram")
    return histogram


def assert_rejected(record, sources, label):
    try:
        validate(record, sources)
    except (CertificateError, KeyError, ValueError, TypeError):
        return
    raise AssertionError(f"hostile canary was accepted: {label}")


def main():
    record = json.loads(CERTIFICATE.read_text(encoding="utf-8"))
    sources = replay_sources()
    histogram = validate(record, sources)

    corrupt = copy.deepcopy(record)
    corrupt["coverage_evidence"]["kind"] = "sample_bank"
    assert_rejected(corrupt, sources, "sample bank as coverage")

    corrupt = copy.deepcopy(record)
    corrupt["parent_infinity_subcomplex"] = ["b0", "p0", "p1"]
    assert_rejected(corrupt, sources, "scope boundary as parent infinity")

    corrupt = copy.deepcopy(record)
    corrupt["strict_closure_pairs"].pop()
    assert_rejected(corrupt, sources, "incomplete strict closure")

    corrupt = copy.deepcopy(record)
    corrupt["signature_profile_source"]["profiles"][0]["signature_count"] -= 1
    assert_rejected(corrupt, sources, "incomplete signature accounting")

    corrupt = copy.deepcopy(record)
    corrupt["inputs"]["candidate_factor_sha256"] = "0" * 64
    assert_rejected(corrupt, sources, "corrupt active-factor input")

    corrupt = copy.deepcopy(record)
    corrupt["coverage_evidence"]["geometry"]["branch_affine"][0][1] *= -1
    assert_rejected(corrupt, sources, "unsigned branch transport")

    corrupt = copy.deepcopy(record)
    corrupt["integral_boundary"]["d2_entries"][0][2] *= -1
    assert_rejected(corrupt, sources, "nonzero d_squared")

    print("PASS exact row-2599 full-support 2D master-closure canary")
    print("PASS 84,840 residual occurrences and 70 parent brackets replayed")
    print("PASS 17-cell regular-CW disk: 5 vertices, 8 edges, 4 chambers")
    print("PASS scope boundary retained as ordinary; parent infinity is empty")
    print("PASS complete 97,224-signature profile map", EXPECTED_PROFILE_COUNTS)
    print("PASS all 216 ordered profile triples have local H1=0 over F2")
    print("RANK_HISTOGRAM", dict(sorted(histogram.items())))
    print("PASS 7/7 hostile corruptions rejected")
    print("SCOPE complete on one exact 2D disk; no full 9D parent coverage claim")


if __name__ == "__main__":
    main()
