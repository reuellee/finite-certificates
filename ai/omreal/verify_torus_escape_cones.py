#!/usr/bin/env python3
"""Exact Hilbert--Mumford face-cone checks for two 9DVL residues.

Positive rescaling of the eight homogeneous parent columns by ``exp(t*u_e)``
acts on a Gordan circuit block by

    lambda_I -> lambda_I exp(-t <1_I,u>) / normalization.

The limiting support is the set of triples minimizing ``<1_I,u>``.  A
prescribed tuple of limiting faces is therefore feasible precisely when a
small rational system of homogeneous equalities and strict inequalities is
feasible.  This file decides those systems *exactly* with Gordan's theorem;
there is no floating-point LP.

Two displayed support tuples are exact positive, proper, incomparable,
pencil-rigid survivors from the row-2599 certificate.  The checker also scans
all 65 stored pencil-rigid occurrences (55 distinct support pairs) for proper
coherent faces which remain pencil-rigid.  This is a check of the toric
boundary fan, not a proof that a torus orbit moves the normalized parent
point: column rescaling is projective gauge and its orbit projects to a single
point of the realization space.
"""

from fractions import Fraction
from itertools import combinations
from pathlib import Path

import numpy as np


def triple(text):
    return tuple(int(character) for character in text)


SAMPLES = {
    "five+five beta=1": (
        tuple(map(triple, ("123", "134", "267", "258", "468"))),
        tuple(map(triple, ("123", "256", "127", "357", "478"))),
    ),
    "four+five beta=0": (
        tuple(map(triple, ("156", "456", "127", "347", "578"))),
        tuple(map(triple, ("134", "235", "238", "368"))),
    ),
}

# A stored 5+5 pair falsifying the stronger hope that every proper coherent
# toric face is pencil-prunable.  The one-parameter subgroup below keeps the
# first block full and deletes 123 only from the second block; because 123 is
# shared, the distinct-triple union remains pencil-rigid.
RIGID_BOUNDARY_SUPPORTS = (
    tuple(map(triple, ("123", "124", "256", "357", "478"))),
    tuple(map(triple, ("123", "145", "367", "468", "178"))),
)
RIGID_BOUNDARY_FACES = (
    RIGID_BOUNDARY_SUPPORTS[0],
    RIGID_BOUNDARY_SUPPORTS[1][1:],
)
RIGID_BOUNDARY_U = (0, 2, 1, 1, 1, 0, 1, 1)

HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "seeat_parent2599_shatter8.npz"
TRIPLES = tuple(
    sorted(
        combinations(range(1, 9), 3),
        key=lambda item: tuple(reversed(item)),
    )
)


def incidence(item):
    return tuple(int(vertex in item) for vertex in range(1, 9))


def subtract(left, right):
    return tuple(a - b for a, b in zip(left, right, strict=True))


def rref(matrix, columns=None):
    if matrix:
        columns = len(matrix[0])
    elif columns is None:
        columns = 0
    rows = [[Fraction(value) for value in row] for row in matrix]
    pivots = []
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, len(rows)) if rows[row][column]),
            None,
        )
        if pivot is None:
            continue
        rows[pivot_row], rows[pivot] = rows[pivot], rows[pivot_row]
        scale = rows[pivot_row][column]
        rows[pivot_row] = [value / scale for value in rows[pivot_row]]
        for row in range(len(rows)):
            if row == pivot_row or not rows[row][column]:
                continue
            scale = rows[row][column]
            rows[row] = [
                left - scale * right
                for left, right in zip(rows[row], rows[pivot_row], strict=True)
            ]
        pivots.append(column)
        pivot_row += 1
        if pivot_row == len(rows):
            break
    return rows, tuple(pivots)


def rank(matrix, columns=None):
    return len(rref(matrix, columns)[1])


def nullspace(matrix, columns=None):
    reduced, pivots = rref(matrix, columns)
    if matrix:
        columns = len(matrix[0])
    elif columns is None:
        columns = 0
    free = [column for column in range(columns) if column not in pivots]
    basis = []
    for current in free:
        vector = [Fraction(0)] * columns
        vector[current] = 1
        for row, pivot in enumerate(pivots):
            vector[pivot] = -reduced[row][current]
        basis.append(tuple(vector))
    return tuple(basis)


def transpose(matrix, columns=None):
    if matrix:
        return [tuple(column) for column in zip(*matrix, strict=True)]
    return [tuple() for _ in range(columns or 0)]


def has_nonnegative_dual_dependency(rows):
    """Return whether nonzero y>=0 satisfies sum y_i rows_i=0.

    If such a vector exists, one with inclusion-minimal support is a positive
    circuit: its nullspace is one-dimensional and its unique dependence has
    one sign.  Enumerating supports is tiny here (at most eight inequalities)
    and keeps the decision rational and exact.
    """

    if not rows:
        return False
    dimension = len(rows[0])
    for size in range(1, len(rows) + 1):
        for chosen in combinations(range(len(rows)), size):
            selected = [rows[index] for index in chosen]
            transposed = transpose(selected, dimension)
            if rank(transposed, size) != size - 1:
                continue
            kernel = nullspace(transposed, size)
            assert len(kernel) == 1
            vector = kernel[0]
            if all(value > 0 for value in vector) or all(
                value < 0 for value in vector
            ):
                return True
    return False


def strict_cone_feasible(equalities, inequalities):
    """Decide E u=0, A u>0, modulo the diagonal label weight.

    The rows of E and A are differences of three-set incidence vectors, so
    the diagonal vector is always in ker(E) and annihilated by A.  If A is
    nonempty, Gordan's theorem decides strict feasibility after restricting
    to ker(E).  If A is empty, a nontrivial one-parameter subgroup exists iff
    ker(E) has dimension greater than the diagonal line.
    """

    kernel = nullspace(equalities, 8)
    if not inequalities:
        return len(kernel) > 1
    restricted = [
        tuple(sum(row[index] * vector[index] for index in range(8)) for vector in kernel)
        for row in inequalities
    ]
    return not has_nonnegative_dual_dependency(restricted)


def gauge_matrix(supports):
    rows = []
    for support in supports:
        base = incidence(support[0])
        rows.extend(subtract(incidence(item), base) for item in support[1:])
    return rows


def nonempty_subsets(items):
    for size in range(1, len(items) + 1):
        yield from combinations(items, size)


def face_cone_feasible(supports, faces):
    equalities = []
    inequalities = []
    for support, face in zip(supports, faces, strict=True):
        base = incidence(face[0])
        equalities.extend(subtract(incidence(item), base) for item in face[1:])
        face_set = set(face)
        inequalities.extend(
            subtract(incidence(item), base)
            for item in support
            if item not in face_set
        )
    return strict_cone_feasible(equalities, inequalities)


def limiting_face(support, label_weight):
    values = {
        item: sum(label_weight[vertex - 1] for vertex in item) for item in support
    }
    minimum = min(values.values())
    return tuple(item for item in support if values[item] == minimum)


def pencil_rigid(items):
    union = set(items)
    degrees = {
        vertex: sum(vertex in item for item in union) for vertex in range(1, 9)
    }
    if min(degrees.values()) < 3:
        return False
    for vertex in range(1, 9):
        incident = [item for item in union if vertex in item]
        if any(
            all(partner in item for item in incident)
            for partner in range(1, 9)
            if partner != vertex
        ):
            return False
    return True


def analyze(supports):
    matrix = gauge_matrix(supports)
    matrix_rank = rank(matrix, 8)
    beta = len(matrix) - matrix_rank
    stabilizer_dimension = 7 - matrix_rank
    distribution = {}
    proper = 0
    rigid_proper = 0
    vertex_tuples = 0
    for faces in (
        (left, right)
        for left in nonempty_subsets(supports[0])
        for right in nonempty_subsets(supports[1])
    ):
        if not face_cone_feasible(supports, faces):
            continue
        sizes = tuple(len(face) for face in faces)
        distribution[sizes] = distribution.get(sizes, 0) + 1
        is_proper = any(len(face) < len(support) for face, support in zip(
            faces, supports, strict=True
        ))
        if is_proper:
            proper += 1
            union = set(faces[0]) | set(faces[1])
            rigid_proper += int(pencil_rigid(union))
        vertex_tuples += int(sizes == (1, 1))
    return {
        "rank": matrix_rank,
        "beta": beta,
        "stabilizer": stabilizer_dimension,
        "distribution": distribution,
        "proper": proper,
        "rigid_proper": rigid_proper,
        "vertices": vertex_tuples,
    }


def stored_pencil_rigid_pairs():
    """Recover the 65 exact row-2599 occurrences as 55 support pairs."""

    certificate = np.load(CERTIFICATE, allow_pickle=False)
    if int(certificate["parent_index"].item()) != 2599:
        raise AssertionError("wrong parent certificate")
    weights = certificate["gordan_weight"]
    occurrences = 0
    pairs = set()
    for pattern in range(256):
        bad_bits = [bit for bit in range(8) if not ((pattern >> bit) & 1)]
        supports = {
            bit: tuple(
                index for index, value in enumerate(weights[pattern, bit])
                if int(value)
            )
            for bit in bad_bits
        }
        for position, left in enumerate(bad_bits):
            for right in bad_bits[position + 1:]:
                pair = (supports[left], supports[right])
                sizes = tuple(sorted(map(len, pair)))
                triple_union = {
                    TRIPLES[index] for current in pair for index in current
                }
                if sizes not in ((4, 5), (5, 5)) or not pencil_rigid(triple_union):
                    continue
                occurrences += 1
                pairs.add(tuple(sorted(pair)))
    return occurrences, tuple(sorted(pairs))


def exhaustive_boundary_residue():
    """Count coherent proper faces which remain pencil-rigid in the sample."""

    occurrences, index_pairs = stored_pencil_rigid_pairs()
    candidates = 0
    coherent = 0
    coherent_pairs = 0
    size_distribution = {}
    type_distribution = {}
    for index_pair in index_pairs:
        supports = tuple(
            tuple(TRIPLES[index] for index in current) for current in index_pair
        )
        pair_candidates = 0
        pair_coherent = 0
        for faces in (
            (left, right)
            for left in nonempty_subsets(supports[0])
            for right in nonempty_subsets(supports[1])
        ):
            if all(
                len(face) == len(support)
                for face, support in zip(faces, supports, strict=True)
            ):
                continue
            if not pencil_rigid(set(faces[0]) | set(faces[1])):
                continue
            pair_candidates += 1
            if not face_cone_feasible(supports, faces):
                continue
            pair_coherent += 1
            sizes = tuple(sorted(map(len, faces)))
            size_distribution[sizes] = size_distribution.get(sizes, 0) + 1
        candidates += pair_candidates
        coherent += pair_coherent
        coherent_pairs += int(pair_coherent > 0)
        pair_type = tuple(sorted(map(len, supports)))
        previous = type_distribution.get(pair_type, (0, 0, 0))
        type_distribution[pair_type] = (
            previous[0] + 1,
            previous[1] + pair_candidates,
            previous[2] + pair_coherent,
        )
    return {
        "occurrences": occurrences,
        "distinct": len(index_pairs),
        "candidates": candidates,
        "coherent": coherent,
        "coherent_pairs": coherent_pairs,
        "sizes": size_distribution,
        "types": type_distribution,
    }


def main():
    expected = {
        # Exact rational face-fan summaries.  These values make later changes
        # to either the support data or the inequality signs visible.
        "five+five beta=1": (784, 25, 0),
        "four+five beta=0": (464, 20, 0),
    }
    results = {name: analyze(supports) for name, supports in SAMPLES.items()}

    # Structural assertions independent of the enumerated fan f-vectors.
    assert results["five+five beta=1"]["rank"] == 7
    assert results["five+five beta=1"]["beta"] == 1
    assert results["five+five beta=1"]["stabilizer"] == 0
    assert results["four+five beta=0"]["rank"] == 7
    assert results["four+five beta=0"]["beta"] == 0
    assert results["four+five beta=0"]["stabilizer"] == 0
    for result in results.values():
        # A generic label weight has a unique minimum in every block.
        assert result["vertices"] > 0
        # No proper limiting face union survives the existing pencil test in
        # these two exact examples.  This is deliberately *not* interpreted as
        # a path in the normalized bad locus; the torus direction is gauge.
        assert result["rigid_proper"] == 0
    for name, result in results.items():
        assert (
            result["proper"], result["vertices"], result["rigid_proper"]
        ) == expected[name]
    assert tuple(
        limiting_face(support, RIGID_BOUNDARY_U)
        for support in RIGID_BOUNDARY_SUPPORTS
    ) == RIGID_BOUNDARY_FACES
    assert pencil_rigid(
        set(RIGID_BOUNDARY_FACES[0]) | set(RIGID_BOUNDARY_FACES[1])
    )

    for name, result in results.items():
        print(name)
        print(
            f"  rank(D)={result['rank']} beta={result['beta']} "
            f"support-preserving stabilizer/Tdiag={result['stabilizer']}"
        )
        print(
            f"  coherent proper face tuples={result['proper']}; "
            f"vertex tuples={result['vertices']}; "
            f"pencil-rigid proper tuples={result['rigid_proper']}"
        )
        print(f"  face-size distribution={sorted(result['distribution'].items())}")
    exhaustive = exhaustive_boundary_residue()
    assert exhaustive == {
        "occurrences": 65,
        "distinct": 55,
        "candidates": 137,
        "coherent": 39,
        "coherent_pairs": 28,
        "sizes": {(4, 5): 28, (3, 5): 7, (4, 4): 4},
        "types": {(4, 5): (2, 0, 0), (5, 5): (53, 137, 39)},
    }
    print(
        "all 65 stored occurrences (55 distinct): "
        "137 proper pencil-rigid face candidates, 39 coherent on 28 pairs"
    )
    print(f"  coherent boundary size distribution={sorted(exhaustive['sizes'].items())}")
    print("  no stored 4+5 pair has a pencil-rigid proper face")
    print(
        "  exact surviving-boundary witness u=(0,2,1,1,1,0,1,1): "
        "first 5-support stays full, shared 123 drops from the second"
    )
    print("PASS: every face-cone decision used exact rational Gordan duality")
    print("CAVEAT: all column-scaling one-parameter subgroups project to a point in X")


if __name__ == "__main__":
    main()
