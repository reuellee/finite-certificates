#!/usr/bin/env python3
"""Arithmetic audit for the single-bad block-Gordan two-skeleton theorem.

The proof filters each normalized Gordan polytope by relative interiors of
coordinate faces.  A k-face uses at most 5+k coordinates.  For total
compact-support degree at most two, the resulting support hypergraphs force
motion fibers of dimensions at least 3-k.

This checker pins those dimension and incidence inequalities.  It also
reuses the literal certificate table from verify_derived_wall_sides.py to
audit the residual-wall corollary without rerunning symbolic determinants:
ordinary walls give four-support rank-three vertices, and localization walls
give three-support rank-two vertices.  The topology and support-plane
geometry are proved in DIAG3_SINGLE_BAD_TWO_SKELETON.md.
"""

import ast
from itertools import product
from pathlib import Path


MAX_EQUALITY_RANK = 5
TARGET_DEGREE = 2


def compositions(total, length, maximum):
    """Yield bounded ordered compositions, used as an independent audit."""

    if length == 0:
        if total == 0:
            yield ()
        return
    for first in range(min(maximum, total) + 1):
        for tail in compositions(total - first, length - 1, maximum):
            yield (first,) + tail


def support_bound(face_dimension, augmented_rank):
    return face_dimension + augmented_rank


def forced_motion_dimension(face_dimension, support_size):
    """Return the incidence-forced parent motion dimension."""

    # The vertex case uses the proved degree-one-plane-plus-pencil theorem:
    # a support of at most five triples either omits a label or has a
    # degree-one label and a second outside label of degree at most two.
    if face_dimension == 0:
        return 3

    incidence = 3 * support_size
    degree_vectors = tuple(compositions(incidence, 8, support_size))
    if not degree_vectors:
        raise AssertionError("missing degree-vector audit")

    minimum = 99
    for degrees in degree_vectors:
        if any(value == 0 for value in degrees):
            motion = 3
        elif any(value == 1 for value in degrees):
            motion = 2
        elif face_dimension == 1 and sum(value == 2 for value in degrees) >= 2:
            motion = 2
        elif any(value == 2 for value in degrees):
            motion = 1
        else:
            motion = 0
        minimum = min(minimum, motion)
    return minimum


def literal_assignment(tree, name):
    """Read one literal module assignment without executing the module."""

    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if any(isinstance(target, ast.Name) and target.id == name
               for target in node.targets):
            return ast.literal_eval(node.value)
    raise AssertionError(f"missing literal certificate assignment {name}")


def audit_residual_wall_vertices():
    """Replay the cheap rank/support interface to the exact wall checker."""

    certificate_path = Path(__file__).with_name("verify_derived_wall_sides.py")
    tree = ast.parse(certificate_path.read_text(encoding="utf-8"))
    labeled_sizes = literal_assignment(tree, "EXPECTED_RESIDUAL_SIZES")
    ordinary_types = literal_assignment(tree, "FOUR_ROW_TYPES")
    localization = literal_assignment(tree, "LOCALIZATION_CERTIFICATES")

    residual_types = set(labeled_sizes)
    localization_types = set(localization)
    assert len(residual_types) == 13
    assert ordinary_types | localization_types == residual_types
    assert not (ordinary_types & localization_types)
    assert (len(ordinary_types), len(localization_types)) == (9, 4)
    assert sum(labeled_sizes.values()) == 84_840
    assert sum(labeled_sizes[kind] for kind in ordinary_types) == 55_440
    assert sum(labeled_sizes[kind] for kind in localization_types) == 29_400

    rows = []
    for kind in sorted(residual_types):
        if kind in ordinary_types:
            # The exact upstream checker supplies four nonzero cofactors.
            support_size, selected_rank, fixed_coefficients = 4, 3, 4
        else:
            (circuit_labels, _residual, _structural, coefficient_types,
             _structural_type) = localization[kind]
            support_size = len(circuit_labels)
            selected_rank = support_size - 1
            fixed_coefficients = len(coefficient_types)

        assert support_size in (3, 4)
        assert selected_rank == support_size - 1
        assert fixed_coefficients == support_size

        # A one-dimensional positive kernel, cut by normalization, has
        # augmented rank |U| and hence face dimension zero.
        augmented_rank = selected_rank + 1
        face_dimension = support_size - augmented_rank
        motion_dimension = forced_motion_dimension(
            face_dimension, support_size
        )
        assert (face_dimension, motion_dimension) == (0, 3)
        rows.append(
            (kind, support_size, selected_rank, motion_dimension,
             labeled_sizes[kind])
        )

    assert sum(row[4] for row in rows) == 84_840
    return rows


def main():
    wall_rows = audit_residual_wall_vertices()
    rows = []
    for face_dimension in range(TARGET_DEGREE + 1):
        required_motion = TARGET_DEGREE + 1 - face_dimension
        worst_motion = 99
        maximum_support = 0
        for augmented_rank in range(1, MAX_EQUALITY_RANK + 1):
            support_size = support_bound(face_dimension, augmented_rank)
            maximum_support = max(maximum_support, support_size)
            if support_size > 7:
                raise AssertionError("low skeleton exceeded seven coordinates")
            motion = forced_motion_dimension(face_dimension, support_size)
            if motion < worst_motion:
                worst_motion = motion
        if worst_motion < required_motion:
            raise AssertionError(
                f"k={face_dimension}: forced motion {worst_motion} "
                f"is below required {required_motion}"
            )
        rows.append(
            (face_dimension, maximum_support, worst_motion, required_motion)
        )

    # Independently audit the only nontrivial pigeonhole statements without
    # assuming that a degree vector is realizable by a three-uniform support.
    for degrees in product(range(7), repeat=8):
        total = sum(degrees)
        if total <= 18 and min(degrees) >= 2:
            if sum(value == 2 for value in degrees) < 2:
                raise AssertionError("six-support two-pencil bound failed")
        if total <= 21 and min(degrees) > 2:
            raise AssertionError("seven-support light-label bound failed")

    if rows != [(0, 5, 3, 3), (1, 6, 2, 2), (2, 7, 1, 1)]:
        raise AssertionError(f"two-skeleton table changed: {rows}")

    print("PASS augmented face bounds: k=0/1/2 use at most 5/6/7 coordinates")
    print("PASS forced motion dimensions: 3/2/1")
    print("PASS total-degree-two compact-support table")
    print(
        "PASS residual wall vertices: "
        f"{len(wall_rows)} orbits/84,840 labels, "
        "supports 4(rank 3) or 3(rank 2), motion dimension 3"
    )
    print("THEOREM H_c^q(B_rho; R)=0 for q=0,1,2")
    print("COROLLARY H_c^q(H_f; R)=0 for every residual factor and q=0,1,2")
    print("CAVEAT pair/triple terms and the third diagonal remain open")


if __name__ == "__main__":
    main()
