#!/usr/bin/env python3
"""Exact robust-common-shear audit on two residual mutation squares.

For a signature ``rho`` which is bad in every chamber of a mutation square,
put

    E_square(rho) = intersection_c E_c(rho).

This verifier proves that the robust masks are pairwise intersecting on two
independent exact four-cycles:

* the generic canonical type-37/type-44 square reconstructed by
  ``verify_diag2_escape_set_mutation_square.py``; and
* the coverage-certified transverse Q2 node stored for parent 2599.

The result is a finite mutation-stability theorem for these two nodes.  It is
not residual-chamber coverage and not a universal decorated-cycle theorem.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import hashlib
from itertools import combinations
from pathlib import Path

import numpy as np

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled
import DIAG9_GRAPH_exact_topes as exact_topes
import four_chart_gate as gate
import verify_diag2_escape_set_atlas178 as atlas178
import verify_diag2_escape_set_mutation_square as mutation
import verify_diag2_escape_set_topes as escape
from DIAG2_PIVOT_ALL_COMPACT_SECOND_WALL_VERIFY import column_determinant


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
NODE_ROADMAP = DATA / "DIAG9_GRAPH_row2599_node_roadmap.npz"
NODE_GRAPH = DATA / "DIAG9_GRAPH_row2599_node_graph.npz"

NODE_SHA256 = {
    NODE_ROADMAP.name:
        "ddec96b052b305d279b543be2af27e12f380f0dedc79ea434616c64b40cd8cea",
    NODE_GRAPH.name:
        "b7f48c4f4f421ba88cf551a2ba16cbd024d63d0910ada701118c88e2e2b7e19f",
}

EXPECTED_GENERIC_DIGEST = (
    "ad40add5ed1ad5502d57250bdbef4d6ce7873f81958f619531e6b6af516908f6"
)
EXPECTED_PARENT2599_DIGEST = (
    "f4db21ca8a6fc00f8819988bddab600c54102cb261db8b5a1085ab2258c90455"
)


@dataclass(frozen=True)
class RobustReport:
    cells: int
    bad_per_cell: int
    common_all: int
    minimum_robust_escape: int
    minimum_robust_overlap: int
    overlap_witness: tuple[int, int, int, int]
    edge_reports: tuple[tuple[int, int, int, int, int], ...]
    digest: str


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def evaluate(polynomial, values):
    answer = Fraction(0)
    for monomial, coefficient in polynomial.items():
        term = Fraction(coefficient)
        for variable, exponent in zip(mutation.VARIABLES, monomial, strict=True):
            term *= values[variable] ** exponent
        answer += term
    return answer


def semantic_digest(label, cell_records, robust_records, report_fields):
    digest = hashlib.sha256()
    digest.update(b"diag2-robust-mutation-square-v1\0")
    digest.update(label.encode("ascii") + b"\0")
    for cell in sorted(cell_records):
        digest.update(int(cell).to_bytes(2, "little"))
        for signature, mask in sorted(cell_records[cell].items()):
            digest.update(int(signature).to_bytes(8, "little"))
            digest.update(int(mask).to_bytes(16, "little"))
    digest.update(b"robust\0")
    for signature, mask in robust_records:
        digest.update(int(signature).to_bytes(8, "little"))
        digest.update(int(mask).to_bytes(16, "little"))
    digest.update(repr(report_fields).encode("ascii"))
    return digest.hexdigest()


def records_from_topes(topes, signatures):
    tope_values = tuple(map(int, topes))
    signature_values = tuple(map(int, signatures))
    tope_set = set(tope_values)
    signature_set = set(signature_values)
    if len(tope_set) != len(tope_values):
        raise AssertionError("supplied complete-tope table contains duplicates")
    if len(signature_set) != len(signature_values):
        raise AssertionError("supplied valid-extension table contains duplicates")
    if not tope_set <= signature_set:
        raise AssertionError("a supplied complete tope is not a GP-valid extension")
    prepared = escape.prepare_directions(tope_set)
    records = {
        int(signature): escape.escape_mask(int(signature), prepared)
        for signature in signature_values
        if int(signature) not in tope_set
    }
    if len(records) + len(tope_set) != len(signature_set):
        raise AssertionError("bad, tope, and valid-extension counts are inconsistent")
    return records


def robust_records(cell_records, cells):
    common = set.intersection(*(set(cell_records[cell]) for cell in cells))
    answer = []
    for signature in sorted(common):
        mask = (1 << len(escape.DIRECTIONS)) - 1
        for cell in cells:
            mask &= cell_records[cell][signature]
        answer.append((signature, mask))
    return answer


def audit_robust_square(label, cell_records, edges, expected):
    cells = tuple(sorted(cell_records))
    bad_counts = {len(cell_records[cell]) for cell in cells}
    if len(bad_counts) != 1:
        raise AssertionError(f"{label}: chamber bad counts differ")
    bad_per_cell = next(iter(bad_counts))

    square_records = robust_records(cell_records, cells)
    if escape.prove_pairwise_intersection(square_records) is not None:
        raise AssertionError(f"{label}: square-robust masks have a disjoint pair")
    minimum_robust_escape = min(mask.bit_count() for _, mask in square_records)
    minimum_robust_overlap, overlap_witness = atlas178.minimum_pair_overlap(
        square_records
    )

    edge_reports = []
    for left, right in edges:
        left, right = int(left), int(right)
        records = robust_records(cell_records, (left, right))
        if escape.prove_pairwise_intersection(records) is not None:
            raise AssertionError(
                f"{label}: edge {left}-{right} robust masks have a disjoint pair"
            )
        minimum_escape = min(mask.bit_count() for _, mask in records)
        minimum_overlap, _witness = atlas178.minimum_pair_overlap(records)
        edge_reports.append(
            (left, right, len(records), minimum_escape, minimum_overlap)
        )

    report_fields = (
        len(cells),
        bad_per_cell,
        len(square_records),
        minimum_robust_escape,
        minimum_robust_overlap,
        overlap_witness,
        tuple(edge_reports),
    )
    digest = semantic_digest(label, cell_records, square_records, report_fields)
    report = RobustReport(
        cells=len(cells),
        bad_per_cell=bad_per_cell,
        common_all=len(square_records),
        minimum_robust_escape=minimum_robust_escape,
        minimum_robust_overlap=minimum_robust_overlap,
        overlap_witness=overlap_witness,
        edge_reports=tuple(edge_reports),
        digest=digest,
    )
    if expected is not None and report != expected:
        raise AssertionError(f"{label}: robust report changed: {report}")
    return report


def generic_37_44_square():
    occurrences, occurrence_factor, factor_polynomials = labeled.factor_polynomials()
    del occurrences
    representatives = labeled.occurrence_representatives()
    factor_ids = (
        occurrence_factor[representatives[37]],
        occurrence_factor[representatives[44]],
    )
    if factor_ids != mutation.EXPECTED_FACTOR_IDS:
        raise AssertionError("canonical 37/44 factor IDs changed")
    factors = tuple(factor_polynomials[index] for index in factor_ids)
    center_zeros = tuple(
        index
        for index, polynomial in enumerate(factor_polynomials)
        if evaluate(polynomial, mutation.CENTER) == 0
    )
    if center_zeros != factor_ids:
        raise AssertionError("the generic 37/44 center has extra residual zeros")

    center_brackets = tuple(
        column_determinant(mutation.standard_columns(mutation.CENTER), basis)
        for basis in combinations(range(8), 4)
    )
    if not all(center_brackets):
        raise AssertionError("the generic 37/44 center lies on a parent wall")

    sign_pairs = {0: (1, 1), 1: (1, -1), 2: (-1, -1), 3: (-1, 1)}
    values = {
        cell: mutation.adjacent_point(first, second, factors)
        for cell, (first, second) in sign_pairs.items()
    }
    germ_report = mutation.verify_local_germ_segments(
        factor_polynomials, factor_ids, values, sign_pairs
    )
    print(
        "PASS generic-37-44 exact local-germ segments",
        germ_report,
        flush=True,
    )
    matrices = {
        cell: mutation.integer_matrix(point) for cell, point in values.items()
    }
    parent_signs = exact_topes.parent_signs(matrices[0])
    factor_signs = {
        cell: tuple(
            evaluate(polynomial, point) > 0
            for polynomial in factor_polynomials
        )
        for cell, point in values.items()
    }
    edges = (
        (0, 1, factor_ids[1]),
        (1, 2, factor_ids[0]),
        (2, 3, factor_ids[1]),
        (3, 0, factor_ids[0]),
    )
    for left, right, expected_factor in edges:
        if exact_topes.parent_signs(matrices[right]) != parent_signs:
            raise AssertionError("a generic-square chamber changed parent chirotope")
        changed = tuple(
            index
            for index, (first, second) in enumerate(
                zip(factor_signs[left], factor_signs[right], strict=True)
            )
            if first != second
        )
        if changed != (expected_factor,):
            raise AssertionError(f"generic-square edge flips factors {changed}")

    parent = "".join("+" if sign > 0 else "-" for sign in parent_signs)
    _, signatures = gate.enumerate_extensions(parent)
    if len(signatures) != mutation.EXPECTED_VALID:
        raise AssertionError("generic-square extension count changed")

    cell_records = {}
    for cell in range(4):
        rows = exact_topes.derived_rows(matrices[cell])
        topes = exact_topes.enumerate_topes(rows, dimension=4)
        exact_topes.verify_topes(rows, topes)
        if len(topes) != 26_112:
            raise AssertionError("generic-square tope count changed")
        cell_records[cell] = records_from_topes(topes, signatures)
        print("BUILT generic-37-44 cell", cell, "bad", len(cell_records[cell]), flush=True)

    expected = RobustReport(
        cells=4,
        bad_per_cell=48_914,
        common_all=48_770,
        minimum_robust_escape=52,
        minimum_robust_overlap=8,
        overlap_witness=(
            33_578_357_495_277_228,
            34_704_257_403_170_476,
            54,
            54,
        ),
        edge_reports=(
            (0, 1, 48_842, 52, 8),
            (1, 2, 48_842, 52, 8),
            (2, 3, 48_842, 52, 8),
            (3, 0, 48_842, 52, 8),
        ),
        digest=EXPECTED_GENERIC_DIGEST,
    ) if EXPECTED_GENERIC_DIGEST is not None else None
    return audit_robust_square(
        "generic-37-44", cell_records, tuple((a, b) for a, b, _ in edges), expected
    )


def parent2599_node_square():
    for path in (NODE_ROADMAP, NODE_GRAPH):
        if sha256(path) != NODE_SHA256[path.name]:
            raise AssertionError(f"pinned node artifact changed: {path.name}")

    with np.load(NODE_ROADMAP, allow_pickle=False) as source:
        if str(source["format"].item()) != "diag9-row2599-transverse-node-v1":
            raise AssertionError("wrong parent-2599 node-roadmap format")
        if int(source["parent_index"].item()) != gate.PARENT_INDEX:
            raise AssertionError("wrong parent-2599 node parent")
        topes_by_cell = np.asarray(source["cell_tope"], dtype=np.uint64)
    with np.load(NODE_GRAPH, allow_pickle=False) as source:
        if str(source["format"].item()) != "diag9-labeled-master-tree-v1":
            raise AssertionError("wrong parent-2599 node-graph format")
        edges_array = np.asarray(source["edge"], dtype=np.int64)

    expected_edges = np.asarray(((0, 1), (1, 2), (2, 3), (0, 3)))
    if topes_by_cell.shape != (4, 26_112):
        raise AssertionError("wrong parent-2599 node cell-tope table")
    if not np.array_equal(edges_array, expected_edges):
        raise AssertionError("parent-2599 node graph is not Q2")
    if any(len(set(map(int, row))) != 26_112 for row in topes_by_cell):
        raise AssertionError("a parent-2599 node cell has duplicate topes")

    parents = [line.strip() for line in gate.CATALOG_48.open() if line.strip()]
    _, signatures = gate.enumerate_extensions(parents[gate.PARENT_INDEX])
    if len(signatures) != atlas178.EXPECTED_VALID:
        raise AssertionError("parent-2599 extension count changed")

    cell_records = {}
    for cell in range(4):
        cell_records[cell] = records_from_topes(topes_by_cell[cell], signatures)
        print(
            "BUILT parent2599-certified-node cell",
            cell,
            "bad",
            len(cell_records[cell]),
            flush=True,
        )
    expected = RobustReport(
        cells=4,
        bad_per_cell=71_112,
        common_all=70_968,
        minimum_robust_escape=53,
        minimum_robust_overlap=11,
        overlap_witness=(
            17_531_516_482_543,
            31_638_416_184_377_343,
            53,
            57,
        ),
        edge_reports=(
            (0, 1, 71_040, 53, 11),
            (1, 2, 71_040, 53, 11),
            (2, 3, 71_040, 53, 11),
            (0, 3, 71_040, 53, 11),
        ),
        digest=EXPECTED_PARENT2599_DIGEST,
    ) if EXPECTED_PARENT2599_DIGEST is not None else None
    return audit_robust_square(
        "parent2599-certified-node",
        cell_records,
        tuple(map(tuple, edges_array)),
        expected,
    )


def print_report(label, report):
    pair_decorations = report.common_all * (report.common_all - 1) // 2
    print(
        "PASS",
        label,
        "common-bad signatures",
        report.common_all,
        "cycle decorations",
        pair_decorations,
    )
    print(
        "PASS",
        label,
        "minimum robust escape",
        report.minimum_robust_escape,
        "minimum robust pair overlap",
        report.minimum_robust_overlap,
    )
    print("PASS", label, "edge reports", report.edge_reports)
    print("SEMANTIC", label, report.digest)


def main():
    generic = generic_37_44_square()
    print_report("generic-37-44", generic)
    parent2599 = parent2599_node_square()
    print_report("parent2599-certified-node", parent2599)
    print("THEOREM both exact Q2 mutation cycles admit robust common shears")
    print("SCOPE two exact nodes; no residual-chamber or parent-cell coverage")


if __name__ == "__main__":
    main()
