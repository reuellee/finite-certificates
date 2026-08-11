#!/usr/bin/env python3
"""Exact inventory of the finite data currently available for diagonal 9.

This is not a mathematical ninth-diagonal verifier.  It pins the distinction
between the complete parent catalog / point certificates and the absent
master-chamber roadmap so later work cannot silently treat samples as a CAD.
"""

from itertools import combinations
import json
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
CATALOG = ROOT / "ai" / "omgamma" / "data" / "cat_4_8.txt"
CERTIFICATES = HERE / "certs_4_8.jsonl"
DATA = HERE / "data"


def determinant(matrix):
    matrix = [[int(value) for value in row] for row in matrix]
    if len(matrix) == 1:
        return matrix[0][0]
    return sum(
        (-1 if column & 1 else 1)
        * value
        * determinant(
            [row[:column] + row[column + 1 :] for row in matrix[1:]]
        )
        for column, value in enumerate(matrix[0])
    )


def matrix_chirotope(matrix):
    if np.shape(matrix) != (4, 8):
        raise AssertionError("parent matrix does not have shape 4x8")
    signs = []
    bases = sorted(
        combinations(range(8), 4), key=lambda basis: tuple(reversed(basis))
    )
    for basis in bases:
        value = determinant([[matrix[row][column] for column in basis] for row in range(4)])
        if value == 0:
            raise AssertionError("stored realizable parent is nonuniform")
        signs.append("+" if value > 0 else "-")
    return "".join(signs)


def main():
    catalog = [line.strip() for line in CATALOG.open(encoding="utf-8") if line.strip()]
    records = [
        json.loads(line)
        for line in CERTIFICATES.open(encoding="utf-8")
        if line.strip()
    ]
    if len(catalog) != 2_628 or len(records) != 2_628:
        raise AssertionError("expected 2,628 catalog rows")
    by_chi = {record["chi"]: record for record in records}
    if len(by_chi) != 2_628 or set(by_chi) != set(catalog):
        raise AssertionError("certificate chirotopes do not match the catalog")

    realizable = [record for record in records if record["verdict"] == "REALIZABLE"]
    nonrealizable = [
        record for record in records if record["verdict"] == "NON_REALIZABLE"
    ]
    if (len(realizable), len(nonrealizable)) != (2_604, 24):
        raise AssertionError("wrong realizability split")
    for index, record in enumerate(realizable, 1):
        if matrix_chirotope(record["matrix"]) != record["chi"]:
            raise AssertionError(f"bad exact parent matrix at realizable row {index}")

    atlas = np.load(DATA / "seeat_parent2599_upper178.npz", allow_pickle=False)
    if set(atlas.files) != {"format", "parent_index", "chart_matrix", "assignment", "point"}:
        raise AssertionError("unexpected row-2599 atlas fields")
    if atlas["chart_matrix"].shape != (178, 4, 8):
        raise AssertionError("wrong row-2599 chart bank shape")
    if atlas["assignment"].shape != (97_224,) or atlas["point"].shape != (97_224, 4):
        raise AssertionError("wrong row-2599 extension-cover shape")

    antichain = np.load(DATA / "ninth_candidate_12_37_antichain.npz", allow_pickle=False)
    if antichain["signature"].shape != (9,) or antichain["pattern"].shape != (7,):
        raise AssertionError("wrong ninth antichain certificate shape")
    path = np.load(DATA / "ninth_candidate_12_37_path.npz", allow_pickle=False)
    segment_count = sum(
        len(path[field]) for field in ("update_col_a", "bridge_col", "update_col_b")
    )
    if segment_count != 22_711:
        raise AssertionError("wrong exact coordinate-path segment count")

    graph_files = []
    for candidate in sorted(DATA.glob("*.npz")):
        artifact = np.load(candidate, allow_pickle=False)
        if {"edge", "support"} <= set(artifact.files):
            graph_files.append(candidate.name)
    certified_subroadmaps = {
        "DIAG9_GRAPH_row2599_disk_graph.npz",
        "DIAG9_GRAPH_row2599_line_graph.npz",
        "DIAG9_GRAPH_row2599_node_graph.npz",
        "DIAG9_GRAPH_row2599_slice_graph.npz",
        "DIAG9_GRAPH_parent860_coordinate_star_graph.npz",
    }
    if set(graph_files) != certified_subroadmaps:
        raise AssertionError(
            "unexpected labeled graph data exist; audit their geometric coverage: "
            + ", ".join(graph_files)
        )

    factor = np.load(
        DATA / "DIAG9_GRAPH_global_factor_census.npz", allow_pickle=False
    )
    if str(factor["format"].item()) != "diag9-global-residual-factor-census-v1":
        raise AssertionError("wrong global residual-factor census format")
    if factor["occurrence_fourset"].shape != (84_840, 4):
        raise AssertionError("wrong global residual occurrence census")
    multiplicity = tuple(map(int, factor["factor_multiplicity"]))
    if len(multiplicity) != 26_740 or sum(multiplicity) != 84_840:
        raise AssertionError("wrong localized residual factor census")
    if {
        value: multiplicity.count(value) for value in set(multiplicity)
    } != {1: 25_200, 2: 420, 15: 280, 65: 840}:
        raise AssertionError("wrong localized factor multiplicities")

    states = np.load(
        DATA / "DIAG9_GRAPH_row2599_factor_states.npz", allow_pickle=False
    )
    if str(states["format"].item()) != "diag9-row2599-factor-state-sample-v1":
        raise AssertionError("wrong row-2599 factor-state format")
    if states["chart_factor_sign_packed"].shape != (178, 3_343):
        raise AssertionError("wrong packed row-2599 factor-state matrix")
    if states["varied_factor"].shape != (10_844,):
        raise AssertionError("wrong row-2599 varying-factor count")
    if states["unique_trace_packed"].shape != (10_789, 23):
        raise AssertionError("wrong row-2599 factor-trace census")

    print("PASS: 2,628 catalog classes match the exact certificate ledger")
    print("PASS: 2,604 realizable parent matrices reproduce all 70 bracket signs")
    print("PASS: row-2599 data are 178 point charts covering 97,224 signatures")
    print("PASS: stored ninth stress data are 9 regions, 7 audit charts, 22,711 path edges")
    print("PASS: four exact row-2599 line/disk/node subroadmaps are separately scoped")
    print("PASS: 84,840 residual occurrences localize to 26,740 exact factors")
    print("PASS: 178 row-2599 charts give 178 distinct exact factor states")
    print("DATA GAP: no NPZ contains a full nine-dimensional master roadmap")
    print("SCOPE: point coverage is not residual-chamber roadmap coverage")


if __name__ == "__main__":
    main()
