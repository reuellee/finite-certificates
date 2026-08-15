#!/usr/bin/env python3
"""Exact master-cell extraction for the diagonal-three pair complex.

The pair-end atlas may be replaced by one finite signature-labelled master
subdivision of the compactified parent cell.  For any three signatures this
script extracts the closed triple subcomplex and the three locally closed
exclusive-pair complexes, reconstructs all integral simplicial incidence
signs, and assembles the balanced matrices N,M from
``DIAG3_PAIR_DIFFERENTIAL_ENDS.md``.

Two coverage-certified local objects are used as regressions.

* The row-2599 transverse node is represented by a four-triangle fan with
  its outer circle relative.  Its exact chamber-label census reduces all
  97,224 signatures to six local membership profiles.  Every one of the
  216 ordered profile triples has an integral lift with MN=0.  Forty-eight
  profile triples retain one local middle class, protecting against the
  false claim that an integral lift alone proves exactness.
* The exact type-49 residual collar is triangulated into four triangles.
  The two persistent bad colors and the receiver birth recover a split-exact
  relative balanced complex, independently of the collar's square-cell
  presentation.

This is a structural quotient and an incidence compiler, not a global parent
subdivision and not a proof of pair middle exactness.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, permutations, product
from pathlib import Path

import numpy as np


HERE = Path(__file__).resolve().parent
NODE = HERE / "data" / "DIAG9_GRAPH_row2599_node_roadmap.npz"
EXPECTED_NODE_SHA256 = (
    "ddec96b052b305d279b543be2af27e12f380f0dedc79ea434616c64b40cd8cea"
)

EXPECTED_SIGNATURES = 97_224
EXPECTED_NODE_PROFILES = {
    0: 70_968,
    3: 72,
    6: 72,
    9: 72,
    12: 72,
    15: 25_968,
}
EXPECTED_NODE_RESULT_HISTOGRAM = {
    (0, 0, 0, 0): 16,
    (2, 1, 0, 1): 12,
    (2, 1, 1, 0): 24,
    (3, 1, 2, 0): 36,
    (4, 1, 3, 0): 3,
    (5, 2, 2, 1): 36,
    (5, 2, 3, 0): 24,
    (6, 2, 4, 0): 52,
    (7, 2, 5, 0): 12,
    (8, 2, 6, 0): 1,
}
EXPECTED_NODE_CLOSED_RESULT_HISTOGRAM = {
    (0, 0, 0, 0): 16,
    (2, 2, 0, 0): 12,
    (3, 2, 1, 0): 24,
    (5, 3, 2, 0): 36,
    (7, 5, 2, 0): 36,
    (8, 4, 4, 0): 3,
    (8, 5, 3, 0): 24,
    (10, 6, 4, 0): 52,
    (13, 7, 6, 0): 12,
    (16, 8, 8, 0): 1,
}
EXPECTED_NODE_NONEXACT_PROFILE_TRIPLES = 48
EXPECTED_NODE_NONEXACT_ORDERED_SIGNATURE_TRIPLES = 1_628_792_064
EXPECTED_NODE_NONEXACT_UNORDERED_SIGNATURE_TRIPLES = 271_465_344
EXPECTED_NODE_NONEXACT_SYMMETRY_ORBITS = (
    ((3, 3, 12), 12, 4_416_768),
    ((3, 6, 9), 24, 8_957_952),
    ((3, 12, 15), 12, 1_615_417_344),
)
EXPECTED_COLLAR_TRIANGULATION_RESULT = (14, 8, 6, 0)
EXPECTED_COLLAR_BARYCENTRIC_RESULT = (46, 22, 24, 0)

# Filled after the first exact replay.  This digest includes every ordered
# node profile triple, its integral N/M entries, ranks, and the collar block.
EXPECTED_SEMANTIC_DIGEST = (
    "3fa42824f50159521c1e7a38f9bb56952460a7e4e5f736f76c4403dbe9eb7214"
)


Matrix = np.ndarray
Simplex = tuple[int, ...]


def all_simplices(maximal: tuple[Simplex, ...]) -> tuple[Simplex, ...]:
    answer: set[Simplex] = set()
    for simplex in maximal:
        if tuple(sorted(simplex)) != simplex or len(set(simplex)) != len(simplex):
            raise AssertionError(f"noncanonical simplex {simplex}")
        for size in range(1, len(simplex) + 1):
            answer.update(combinations(simplex, size))
    return tuple(sorted(answer, key=lambda cell: (len(cell), cell)))


def is_subcomplex(cells: set[Simplex]) -> bool:
    return all(
        face in cells
        for cell in cells
        for index in range(len(cell))
        for face in (cell[:index] + cell[index + 1 :],)
        if face
    )


def incidence(lower: tuple[Simplex, ...], upper: tuple[Simplex, ...]) -> Matrix:
    """Integral simplicial coboundary: rows are upper cells."""

    positions = {cell: index for index, cell in enumerate(lower)}
    matrix = np.zeros((len(upper), len(lower)), dtype=np.int64)
    for row, cell in enumerate(upper):
        for omitted in range(len(cell)):
            face = cell[:omitted] + cell[omitted + 1 :]
            column = positions.get(face)
            if column is not None:
                matrix[row, column] += -1 if omitted & 1 else 1
    return matrix


def rank_f2(matrix: Matrix) -> int:
    rows, columns = matrix.shape
    words = [
        sum((int(matrix[row, column]) & 1) << column for column in range(columns))
        for row in range(rows)
    ]
    pivot = 0
    for column in range(columns):
        selected = next(
            (row for row in range(pivot, rows) if words[row] >> column & 1),
            None,
        )
        if selected is None:
            continue
        words[pivot], words[selected] = words[selected], words[pivot]
        for row in range(rows):
            if row != pivot and words[row] >> column & 1:
                words[row] ^= words[pivot]
        pivot += 1
        if pivot == rows:
            break
    return pivot


def rank_q(matrix: Matrix) -> int:
    rows, columns = matrix.shape
    work = [[Fraction(int(matrix[row, column])) for column in range(columns)] for row in range(rows)]
    pivot = 0
    for column in range(columns):
        selected = next(
            (row for row in range(pivot, rows) if work[row][column]), None
        )
        if selected is None:
            continue
        work[pivot], work[selected] = work[selected], work[pivot]
        scale = work[pivot][column]
        work[pivot] = [value / scale for value in work[pivot]]
        for row in range(rows):
            if row == pivot or not work[row][column]:
                continue
            scale = work[row][column]
            work[row] = [
                value - scale * basis
                for value, basis in zip(work[row], work[pivot])
            ]
        pivot += 1
        if pivot == rows:
            break
    return pivot


def block_matrix(
    row_dimensions: tuple[int, ...],
    column_dimensions: tuple[int, ...],
    blocks: dict[tuple[int, int], Matrix],
) -> Matrix:
    row_offsets = [0]
    column_offsets = [0]
    for dimension in row_dimensions:
        row_offsets.append(row_offsets[-1] + dimension)
    for dimension in column_dimensions:
        column_offsets.append(column_offsets[-1] + dimension)
    answer = np.zeros((row_offsets[-1], column_offsets[-1]), dtype=np.int64)
    for (block_row, block_column), matrix in blocks.items():
        expected = (row_dimensions[block_row], column_dimensions[block_column])
        if matrix.shape != expected:
            raise AssertionError(
                f"block {(block_row, block_column)} has {matrix.shape}, expected {expected}"
            )
        answer[
            row_offsets[block_row] : row_offsets[block_row + 1],
            column_offsets[block_column] : column_offsets[block_column + 1],
        ] = matrix
    return answer


@dataclass(frozen=True)
class PairExtraction:
    n_matrix: Matrix
    m_matrix: Matrix
    triple_dimensions: tuple[int, int, int]
    exclusive_dimensions: tuple[tuple[int, int, int], ...]

    def result(self) -> tuple[int, int, int, int]:
        middle = self.n_matrix.shape[0]
        rank_n = rank_f2(self.n_matrix)
        rank_m = rank_f2(self.m_matrix)
        return middle, rank_n, rank_m, middle - rank_n - rank_m


@dataclass(frozen=True)
class MasterComplex:
    maximal: tuple[Simplex, ...]
    infinity: frozenset[Simplex]

    def __post_init__(self):
        cells = set(self.cells)
        if not set(self.infinity).issubset(cells):
            raise AssertionError("infinity contains a cell outside the master complex")
        if not is_subcomplex(cells) or not is_subcomplex(set(self.infinity)):
            raise AssertionError("master or infinity is not a simplicial subcomplex")

    @property
    def cells(self) -> tuple[Simplex, ...]:
        return all_simplices(self.maximal)

    def extract(self, bad_sets: tuple[set[Simplex], set[Simplex], set[Simplex]]) -> PairExtraction:
        cells = set(self.cells)
        for bad in bad_sets:
            if not bad.issubset(cells) or not is_subcomplex(bad):
                raise AssertionError("a bad locus is not a closed subcomplex")

        triple = set.intersection(*bad_sets)
        pairs = ((0, 1), (0, 2), (1, 2))
        exclusive = [
            (bad_sets[left] & bad_sets[right]) - triple for left, right in pairs
        ]
        relative = set(self.infinity)

        def basis(source: set[Simplex], degree: int) -> tuple[Simplex, ...]:
            return tuple(
                cell
                for cell in self.cells
                if len(cell) == degree + 1 and cell in source and cell not in relative
            )

        triple_basis = tuple(basis(triple, degree) for degree in range(3))
        exclusive_basis = tuple(
            tuple(basis(source, degree) for degree in range(3))
            for source in exclusive
        )
        d_triple = (
            incidence(triple_basis[0], triple_basis[1]),
            incidence(triple_basis[1], triple_basis[2]),
        )
        if np.any(d_triple[1] @ d_triple[0]):
            raise AssertionError("triple simplicial coboundary does not square to zero")

        d_exclusive = []
        frontier = []
        for strata_basis in exclusive_basis:
            differentials = (
                incidence(strata_basis[0], strata_basis[1]),
                incidence(strata_basis[1], strata_basis[2]),
            )
            if np.any(differentials[1] @ differentials[0]):
                raise AssertionError("exclusive-pair coboundary does not square to zero")
            blocks = (
                incidence(triple_basis[0], strata_basis[1]),
                incidence(triple_basis[1], strata_basis[2]),
            )
            if np.any(differentials[1] @ blocks[0] + blocks[1] @ d_triple[0]):
                raise AssertionError("frontier identity d_E b + b d_T failed")
            d_exclusive.append(differentials)
            frontier.append(blocks)

        t_dimensions = tuple(len(cells_q) for cells_q in triple_basis)
        e_dimensions = tuple(
            tuple(len(cells_q) for cells_q in strata_basis)
            for strata_basis in exclusive_basis
        )
        c0_dimensions = (t_dimensions[0], t_dimensions[0]) + tuple(
            dimensions[0] for dimensions in e_dimensions
        )
        c1_dimensions = (t_dimensions[1], t_dimensions[1]) + tuple(
            dimensions[1] for dimensions in e_dimensions
        )
        c2_dimensions = (t_dimensions[2], t_dimensions[2]) + tuple(
            dimensions[2] for dimensions in e_dimensions
        )
        n_matrix = block_matrix(
            c1_dimensions,
            c0_dimensions,
            {
                (0, 0): d_triple[0],
                (1, 1): d_triple[0],
                (2, 0): -frontier[0][0],
                (2, 2): d_exclusive[0][0],
                (3, 0): -frontier[1][0],
                (3, 1): -frontier[1][0],
                (3, 3): d_exclusive[1][0],
                (4, 1): -frontier[2][0],
                (4, 4): d_exclusive[2][0],
            },
        )
        m_matrix = block_matrix(
            c2_dimensions,
            c1_dimensions,
            {
                (0, 0): d_triple[1],
                (1, 1): d_triple[1],
                (2, 0): frontier[0][1],
                (2, 2): -d_exclusive[0][1],
                (3, 0): frontier[1][1],
                (3, 1): frontier[1][1],
                (3, 3): -d_exclusive[1][1],
                (4, 1): frontier[2][1],
                (4, 4): -d_exclusive[2][1],
            },
        )
        if np.any(m_matrix @ n_matrix):
            raise AssertionError("assembled signed integral matrices have MN != 0")
        if rank_q(n_matrix) < rank_f2(n_matrix) or rank_q(m_matrix) < rank_f2(m_matrix):
            raise AssertionError("rational rank fell below mod-two rank")
        return PairExtraction(
            n_matrix,
            m_matrix,
            t_dimensions,
            e_dimensions,
        )


def digest_matrix(digest, matrix: Matrix):
    digest.update(int(matrix.shape[0]).to_bytes(4, "little"))
    digest.update(int(matrix.shape[1]).to_bytes(4, "little"))
    for value in matrix.flat:
        digest.update(int(value).to_bytes(2, "little", signed=True))


def node_master() -> tuple[MasterComplex, tuple[Simplex, ...]]:
    # Vertex 0 is the transverse node; vertices 1..4 lie on scope infinity.
    chambers = ((0, 1, 2), (0, 2, 3), (0, 3, 4), (0, 1, 4))
    cells = all_simplices(chambers)
    infinity = frozenset(cell for cell in cells if 0 not in cell)
    return MasterComplex(chambers, infinity), chambers


def bad_set_from_chamber_profile(
    master: MasterComplex, chambers: tuple[Simplex, ...], profile: int
) -> set[Simplex]:
    """Use the exact all-strata rule: a face is feasible iff every incident chamber is."""

    answer = set()
    for cell in master.cells:
        incident = tuple(
            index for index, chamber in enumerate(chambers) if set(cell) <= set(chamber)
        )
        if not incident:
            raise AssertionError(f"cell {cell} has no incident chamber")
        if any(not (profile >> index & 1) for index in incident):
            answer.add(cell)
    if not is_subcomplex(answer):
        raise AssertionError("profile-derived bad locus is not closed")
    return answer


def node_profile_counts() -> dict[int, int]:
    file_digest = sha256(NODE.read_bytes()).hexdigest()
    if file_digest != EXPECTED_NODE_SHA256:
        raise AssertionError(f"pinned node roadmap changed: {file_digest}")
    with np.load(NODE, allow_pickle=False) as certificate:
        patterns = Counter(map(int, certificate["signature_pattern"]))
    counts = dict(patterns)
    counts[0] = EXPECTED_SIGNATURES - sum(counts.values())
    if counts != EXPECTED_NODE_PROFILES:
        raise AssertionError(f"node signature profiles changed: {counts}")
    return counts


def distinct_ordered_ways(profiles: tuple[int, int, int], counts: dict[int, int]) -> int:
    used: dict[int, int] = {}
    answer = 1
    for profile in profiles:
        previous = used.get(profile, 0)
        answer *= counts[profile] - previous
        used[profile] = previous + 1
    return answer


def transform_profile(profile: int, permutation: tuple[int, ...]) -> int:
    return sum(
        1 << permutation[index]
        for index in range(4)
        if profile >> index & 1
    )


def node_symmetry_orbits(nonexact, counts):
    dihedral = []
    for shift in range(4):
        dihedral.append(tuple((index + shift) % 4 for index in range(4)))
        dihedral.append(tuple((shift - index) % 4 for index in range(4)))
    dihedral = tuple(dict.fromkeys(dihedral))
    signature_permutations = tuple(permutations(range(3)))
    source = set(nonexact)
    seen = set()
    records = []
    for profile_triple in sorted(source):
        if profile_triple in seen:
            continue
        orbit = {
            tuple(
                transform_profile(profile_triple[index], chamber_permutation)
                for index in signature_permutation
            )
            for chamber_permutation in dihedral
            for signature_permutation in signature_permutations
        }
        retained = source & orbit
        seen.update(retained)
        weight = sum(distinct_ordered_ways(row, counts) for row in retained)
        records.append((min(retained), len(retained), weight))
    records = tuple(records)
    if records != EXPECTED_NODE_NONEXACT_SYMMETRY_ORBITS:
        raise AssertionError(f"node residue symmetry orbits changed: {records}")
    return records


def node_audit(digest) -> tuple[Counter, Counter, int, int, tuple]:
    master, chambers = node_master()
    counts = node_profile_counts()
    profiles = tuple(sorted(counts))
    bad = {
        profile: bad_set_from_chamber_profile(master, chambers, profile)
        for profile in profiles
    }
    result_histogram = Counter()
    nonexact = []
    weighted = 0
    for profile_triple in product(profiles, repeat=3):
        extraction = master.extract(tuple(bad[profile] for profile in profile_triple))
        result = extraction.result()
        result_histogram[result] += 1
        digest.update(repr(profile_triple).encode("ascii") + b"\0")
        digest_matrix(digest, extraction.n_matrix)
        digest_matrix(digest, extraction.m_matrix)
        digest.update(repr(result).encode("ascii") + b"\0")
        if result[-1]:
            if result[-1] != 1:
                raise AssertionError("node profile triple has unexpected middle rank")
            nonexact.append(profile_triple)
            weighted += distinct_ordered_ways(profile_triple, counts)
    if dict(result_histogram) != EXPECTED_NODE_RESULT_HISTOGRAM:
        raise AssertionError(f"node result histogram changed: {result_histogram}")
    if len(nonexact) != EXPECTED_NODE_NONEXACT_PROFILE_TRIPLES:
        raise AssertionError("node nonexact profile count changed")
    if weighted != EXPECTED_NODE_NONEXACT_ORDERED_SIGNATURE_TRIPLES:
        raise AssertionError(f"weighted node residue changed: {weighted}")
    if weighted % 6 or weighted // 6 != EXPECTED_NODE_NONEXACT_UNORDERED_SIGNATURE_TRIPLES:
        raise AssertionError("ordered/unordered node residue accounting changed")
    symmetry_orbits = node_symmetry_orbits(nonexact, counts)
    digest.update(repr(symmetry_orbits).encode("ascii") + b"\0")

    # The outer four-cycle is only the boundary of the stored disk scope, not
    # parent infinity.  Retain it as ordinary cells and replay the same 216
    # profile triples.  Every local residue then fills inside the closed disk.
    # This pins that relative tagging, rather than MN=0 alone, changes the
    # answer and protects the global infinity ledger.
    closed_master = MasterComplex(master.maximal, frozenset())
    closed_bad = {
        profile: bad_set_from_chamber_profile(closed_master, chambers, profile)
        for profile in profiles
    }
    closed_histogram = Counter()
    for profile_triple in product(profiles, repeat=3):
        extraction = closed_master.extract(
            tuple(closed_bad[profile] for profile in profile_triple)
        )
        result = extraction.result()
        if result[-1]:
            raise AssertionError("closed node disk retained a middle class")
        closed_histogram[result] += 1
        digest.update(b"closed\0" + repr(profile_triple).encode("ascii") + b"\0")
        digest_matrix(digest, extraction.n_matrix)
        digest_matrix(digest, extraction.m_matrix)
    if dict(closed_histogram) != EXPECTED_NODE_CLOSED_RESULT_HISTOGRAM:
        raise AssertionError(f"closed node result histogram changed: {closed_histogram}")
    return (
        result_histogram,
        closed_histogram,
        len(nonexact),
        weighted,
        symmetry_orbits,
    )


def collar_audit(digest) -> tuple[tuple[int, int, int, int], tuple[int, int, int, int]]:
    # Two closed squares separated by the type-49 wall, triangulated with a
    # compatible diagonal.  Vertex order is BL,BW,BR,TL,TW,TR.
    maximal = ((0, 1, 4), (0, 3, 4), (1, 2, 5), (1, 4, 5))
    master = MasterComplex(maximal, frozenset())
    all_cells = set(master.cells)
    wall_and_right_vertices = {1, 2, 4, 5}
    receiver_bad = {
        cell for cell in master.cells if set(cell) <= wall_and_right_vertices
    }
    # A and B are bad throughout.  R is feasible on the left open square and
    # bad on the wall/right, exactly as certified by the collar verifier.
    extraction = master.extract((all_cells, all_cells, receiver_bad))
    triangulated_result = extraction.result()
    if triangulated_result != EXPECTED_COLLAR_TRIANGULATION_RESULT:
        raise AssertionError(f"triangulated collar result changed: {triangulated_result}")
    digest_matrix(digest, extraction.n_matrix)
    digest_matrix(digest, extraction.m_matrix)
    digest.update(repr(triangulated_result).encode("ascii") + b"\0")

    # Independently regenerate a canonical barycentric subdivision from the
    # original two-square regular-CW closure poset.  Original cells are
    # vertices 0..5, edges 6..12, and squares 13,14.  A barycentric simplex
    # is a strict face chain, so the maximal chains are vertex < edge < square.
    edge_vertices = {
        6: (0, 1),   # bL
        7: (1, 2),   # bR
        8: (3, 4),   # tL
        9: (4, 5),   # tR
        10: (0, 3),  # vL
        11: (1, 4),  # vW
        12: (2, 5),  # vR
    }
    square_edges = {
        13: (6, 8, 10, 11),
        14: (7, 9, 11, 12),
    }
    chains = tuple(
        tuple(sorted((vertex, edge, square)))
        for square, edges in square_edges.items()
        for edge in edges
        for vertex in edge_vertices[edge]
    )
    barycentric = MasterComplex(chains, frozenset())
    barycentric_cells = set(barycentric.cells)
    receiver_original_cells = {1, 2, 4, 5, 7, 9, 11, 12, 14}
    receiver_barycentric = {
        chain
        for chain in barycentric.cells
        if set(chain).issubset(receiver_original_cells)
    }
    barycentric_extraction = barycentric.extract(
        (barycentric_cells, barycentric_cells, receiver_barycentric)
    )
    barycentric_result = barycentric_extraction.result()
    if barycentric_result != EXPECTED_COLLAR_BARYCENTRIC_RESULT:
        raise AssertionError(f"barycentric collar result changed: {barycentric_result}")
    digest_matrix(digest, barycentric_extraction.n_matrix)
    digest_matrix(digest, barycentric_extraction.m_matrix)
    digest.update(repr(barycentric_result).encode("ascii") + b"\0")
    return triangulated_result, barycentric_result


def main():
    digest = sha256(b"diag3-pair-global-master-quotient-v1\0")
    histogram, closed_histogram, nonexact, weighted, symmetry_orbits = node_audit(digest)
    collar = collar_audit(digest)
    semantic = digest.hexdigest()
    if EXPECTED_SEMANTIC_DIGEST is not None and semantic != EXPECTED_SEMANTIC_DIGEST:
        raise AssertionError(f"master-quotient semantic digest changed: {semantic}")

    print("PASS node master profiles", EXPECTED_NODE_PROFILES)
    print("PASS all 216 node profile triples have canonical integral MN=0 lifts")
    print("NODE RESULT HISTOGRAM", dict(sorted(histogram.items())))
    print(
        "FALSIFICATION local nonexact profiles/signature triples",
        nonexact,
        weighted,
        "ordered /",
        weighted // 6,
        "unordered",
    )
    print("NODE NONEXACT D4xS3 ORBITS", symmetry_orbits)
    print("PASS closed-node all 216 profile triples exact", dict(sorted(closed_histogram.items())))
    print(
        "PASS type-49 collar direct/barycentric C1-rankN-rankM-H1",
        collar,
    )
    print("SEMANTIC", semantic)
    print(
        "THEOREM a closure-complete labelled master subdivision canonically "
        "produces the integral pair lift and MN=0"
    )
    print(
        "SCOPE exact quotient/extractor and two covered local regressions; "
        "no global parent subdivision or global middle-rank claim"
    )


if __name__ == "__main__":
    main()
