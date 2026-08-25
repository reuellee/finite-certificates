#!/usr/bin/env python3
"""Build the exact row-2599 transverse-node master-closure canary.

The producer is intentionally a translator.  It consumes the already pinned
transverse-node roadmap and emits a compact regular-CW closure object.  It
does not decide coverage, regularity, parent residence, or rank.  The
independent verifier recomputes those facts from the source matrices and
polynomials.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha256
import json
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
OUTPUT = DATA / "DIAG3_PAIR_MASTER_CLOSURE_NODE_CANARY.json"
NODE = DATA / "DIAG9_GRAPH_row2599_node_roadmap.npz"
CANDIDATES = DATA / "DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin"
LEDGER = DATA / "DIAG3_RESEARCH_DECISION_LEDGER.json"
PARENT_GATE = DATA / "DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json"

sys.path.insert(0, str(HERE))
import four_chart_gate as extension_gate  # noqa: E402


FORMAT = "diag3-pair-master-closure-certificate-v1"
STATUS = "LOCAL_EXACT_CANARY"
SOURCE_COMMIT = "e4ca567f829bd0e887e98efb05a3ed9437ba69d5"
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

# The cyclic order of the four residual rays around the exact node.  The
# source roadmap numbers them q0+, q0-, q1-, q1+ as w0,w1,w2,w3.  Around the
# boundary of the square their order is w0,w3,w1,w2.
CYCLIC_WALLS = ("w0", "w3", "w1", "w2")
CHAMBERS = ("c0", "c1", "c2", "c3")
BOUNDARY_VERTICES = ("p0", "p1", "p2", "p3")
SCOPE_ARCS = ("b0", "b1", "b2", "b3")


def file_sha256(path: Path) -> str:
    digest = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fraction_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def load_fraction(source, prefix: str) -> Fraction:
    return Fraction(
        int(source[f"{prefix}_num"].item()),
        int(source[f"{prefix}_den"].item()),
    )


def branch_endpoints(branch_affine, radius: Fraction):
    endpoints = []
    for _constant, coefficient_x, coefficient_y in branch_affine:
        scale = radius / max(abs(int(coefficient_x)), abs(int(coefficient_y)))
        tangent = (scale * int(coefficient_y), -scale * int(coefficient_x))
        endpoints.extend(((-tangent[0], -tangent[1]), tangent))
    # Source order is w0,w1,w2,w3.  Boundary order is w0,w3,w1,w2.
    return {
        "w0": endpoints[0],
        "w1": endpoints[1],
        "w2": endpoints[2],
        "w3": endpoints[3],
    }


def cell_record(identifier, dimension, kind, witness, boundary, incident):
    return {
        "id": identifier,
        "dimension": dimension,
        "kind": kind,
        "witness": [fraction_text(value) for value in witness],
        "boundary": list(boundary),
        "incident_chambers": list(incident),
    }


def build_cells(branch_affine, radius: Fraction):
    endpoints = branch_endpoints(branch_affine, radius)
    cells = [cell_record("v", 0, "residual_node", (Fraction(0), Fraction(0)), (), CHAMBERS)]

    wall_incident = {
        "w0": ("c0", "c3"),
        "w1": ("c1", "c2"),
        "w2": ("c2", "c3"),
        "w3": ("c0", "c1"),
    }
    for index, wall in enumerate(CYCLIC_WALLS):
        cells.append(
            cell_record(
                BOUNDARY_VERTICES[index],
                0,
                "scope_boundary_residual_endpoint",
                endpoints[wall],
                (),
                wall_incident[wall],
            )
        )

    for index, wall in enumerate(CYCLIC_WALLS):
        endpoint = endpoints[wall]
        cells.append(
            cell_record(
                wall,
                1,
                "residual_wall_ray",
                (endpoint[0] / 2, endpoint[1] / 2),
                ("v", BOUNDARY_VERTICES[index]),
                wall_incident[wall],
            )
        )

    corner_witnesses = (
        (radius, radius),
        (radius, -radius),
        (-radius, -radius),
        (-radius, radius),
    )
    chamber_witnesses = tuple(
        (x / 2, y / 2) for x, y in corner_witnesses
    )
    for index, arc in enumerate(SCOPE_ARCS):
        cells.append(
            cell_record(
                arc,
                1,
                "scope_boundary_arc",
                corner_witnesses[index],
                (
                    BOUNDARY_VERTICES[index],
                    BOUNDARY_VERTICES[(index + 1) % 4],
                ),
                (CHAMBERS[index],),
            )
        )

    for index, chamber in enumerate(CHAMBERS):
        cells.append(
            cell_record(
                chamber,
                2,
                "open_chamber",
                chamber_witnesses[index],
                (
                    CYCLIC_WALLS[index],
                    SCOPE_ARCS[index],
                    CYCLIC_WALLS[(index + 1) % 4],
                ),
                (chamber,),
            )
        )
    return cells


def closure_data(cells):
    immediate = {
        (cell["id"], face) for cell in cells for face in cell["boundary"]
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
    return (
        [list(row) for row in sorted(closure)],
        [list(row) for row in sorted(chains)],
    )


def integral_boundary():
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
        "orientation_rule": "spokes point from v to p_i; scope arcs point p_i to p_(i+1); chamber boundary is spoke_i + arc_i - spoke_(i+1)",
        "c0_basis": ["v", *BOUNDARY_VERTICES],
        "c1_basis": [*CYCLIC_WALLS, *SCOPE_ARCS],
        "c2_basis": list(CHAMBERS),
        "d1_entries": [list(row) for row in d1],
        "d2_entries": [list(row) for row in d2],
    }


def bad_cells(cells, feasible_profile: int):
    bad_chambers = {
        chamber for index, chamber in enumerate(CHAMBERS)
        if not (feasible_profile >> index) & 1
    }
    return [
        cell["id"]
        for cell in cells
        if bad_chambers.intersection(cell["incident_chambers"])
    ]


def signature_profile_data(source):
    stored = {
        int(signature): int(pattern)
        for signature, pattern in zip(source["signature"], source["signature_pattern"])
    }
    parents = [
        line.strip()
        for line in extension_gate.CATALOG_48.open(encoding="utf-8")
        if line.strip()
    ]
    _parent_bits, signatures = extension_gate.enumerate_extensions(
        parents[extension_gate.PARENT_INDEX]
    )
    if len(signatures) != 97_224 or len(set(signatures)) != len(signatures):
        raise AssertionError("row-2599 extension enumeration changed")
    if not set(stored).issubset(signatures):
        raise AssertionError("node roadmap contains a nonextension signature")
    digest = sha256(b"diag3-row2599-node-signature-profile-v1\0")
    counts = Counter()
    for signature in signatures:
        profile = stored.get(signature, 0)
        counts[profile] += 1
        digest.update(int(signature).to_bytes(8, "little"))
        digest.update(bytes((profile,)))
    if dict(sorted(counts.items())) != EXPECTED_PROFILE_COUNTS:
        raise AssertionError(f"node profile counts changed: {counts}")
    return digest.hexdigest(), counts


def build_record():
    if file_sha256(NODE) != EXPECTED_NODE_SHA256:
        raise AssertionError("pinned node roadmap changed")
    if file_sha256(CANDIDATES) != EXPECTED_CANDIDATE_SHA256:
        raise AssertionError("pinned candidate-factor input changed")

    ledger = json.loads(LEDGER.read_text(encoding="utf-8"))
    full = ledger["row2599_fullsupport_ledger"]
    parent_gate = json.loads(PARENT_GATE.read_text(encoding="utf-8"))
    if parent_gate["normalized_parent_sign_sha256"] != EXPECTED_PARENT_SIGN_SHA256:
        raise AssertionError("signed parent-cell digest changed")

    with np.load(NODE, allow_pickle=False) as source:
        if str(source["format"].item()) != "diag9-row2599-transverse-node-v1":
            raise AssertionError("wrong source-node format")
        radius = load_fraction(source, "radius")
        branch_affine = tuple(
            tuple(map(int, row)) for row in source["branch_affine"]
        )
        cells = build_cells(branch_affine, radius)
        closure, chains = closure_data(cells)
        profile_digest, profile_counts = signature_profile_data(source)
        offsets = tuple(map(int, source["branch_offset"]))
        branch_counts = tuple(
            offsets[index + 1] - offsets[index]
            for index in range(len(offsets) - 1)
        )
        geometry = {
            "cell_coordinate_system": "x=s-center_s, y=u-center_u",
            "branch_coordinate_system": "original affine parameters s,u",
            "domain": {
                "kind": "closed_square",
                "radius": fraction_text(radius),
            },
            "center": {
                "s": fraction_text(load_fraction(source, "center_s")),
                "u": fraction_text(load_fraction(source, "center_u")),
            },
            "branch_affine": [list(row) for row in branch_affine],
            "branch_occurrence_counts": list(branch_counts),
            "branch_quotient_degree_counts": [
                list(map(int, row)) for row in source["quotient_degree_count"]
            ],
            "transverse_jacobian": str(source["jacobian"].item()),
            "dominance_margins": {
                prefix: fraction_text(load_fraction(source, prefix))
                for prefix in (
                    "other_margin",
                    "branch0_margin",
                    "branch1_margin",
                    "bracket_margin",
                )
            },
        }

    profiles = [
        {
            "feasible_chamber_mask": profile,
            "signature_count": profile_counts[profile],
            "bad_cells": bad_cells(cells, profile),
        }
        for profile in sorted(profile_counts)
    ]

    return {
        "format": FORMAT,
        "status": STATUS,
        "scope": {
            "parent_index": 2599,
            "compactification": "(Delta^3)^3",
            "support": [15, 15, 15],
            "claim": "complete labelled regular-CW closure object on one exact two-dimensional full-support disk",
            "local_parameter_coverage": "COMPLETE",
            "global_parameter_coverage": "NOT_CLAIMED",
            "scope_boundary_policy": "ordinary cells; never parent infinity",
        },
        "inputs": {
            "source_commit": SOURCE_COMMIT,
            "node_roadmap_path": str(NODE.relative_to(HERE.parents[1])),
            "node_roadmap_sha256": EXPECTED_NODE_SHA256,
            "candidate_factor_path": str(CANDIDATES.relative_to(HERE.parents[1])),
            "candidate_factor_sha256": EXPECTED_CANDIDATE_SHA256,
            "candidate_factor_count": full["fullsupport_factor_count"],
            "exact_interior_nonempty_count": full["exact_interior_nonempty_count"],
            "exact_empty_count": full["exact_empty_count"],
            "unresolved_feasibility_count": full["unresolved_feasibility_count"],
            "active_wall_upper_bound": full["master_generator_active_wall_upper_bound"],
            "exact_empty_factor_digest": full["digests"]["empty_factor_ids"],
            "unresolved_factor_digest": full["digests"]["unresolved_factor_ids"],
            "target_signed_parent_digest": EXPECTED_PARENT_SIGN_SHA256,
        },
        "generator": {
            "backend": "pinned_transverse_node_to_regular_cw_v1",
            "build_command": "python ai/omreal/build_diag3_pair_master_closure_node_canary.py",
            "producer_role": "translation only; theorem gates are replayed by the independent verifier",
        },
        "coverage_evidence": {
            "kind": "exact_two_affine_branch_partition",
            "labelled_residual_occurrence_universe": 84_840,
            "parent_bracket_count": 70,
            "geometry": geometry,
        },
        "cells": cells,
        "strict_closure_pairs": closure,
        "strict_three_cell_chains": chains,
        "scope_boundary_subcomplex": [*BOUNDARY_VERTICES, *SCOPE_ARCS],
        "parent_infinity_subcomplex": [],
        "signature_profile_source": {
            "universe_count": 97_224,
            "semantic_sha256": profile_digest,
            "profiles": profiles,
        },
        "integral_boundary": integral_boundary(),
        "verifier": {
            "command": "python ai/omreal/verify_diag3_pair_master_closure_node_canary.py",
            "recomputes": [
                "all 84,840 restricted residual determinants",
                "all 70 parent brackets",
                "both branch quotients and the transverse Jacobian",
                "all 97,224 extension-signature profiles",
                "the regular-CW closure and integral d_squared identity",
                "all 216 ordered profile-triple middle ranks with scope boundary retained",
            ],
        },
    }


def main():
    record = build_record()
    OUTPUT.write_text(
        json.dumps(record, indent=2, sort_keys=False) + "\n",
        encoding="utf-8",
    )
    print("WROTE", OUTPUT)


if __name__ == "__main__":
    main()
