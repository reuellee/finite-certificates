#!/usr/bin/env python3
"""Exact no-go for a generic mutation-connectivity shortcut.

The realizable mutation graph is connected, but fixing only a subset of
bracket signs can disconnect both the induced mutation graph and the actual
partial realization space.  This checker gives a smallest transparent model:
rank three on five labeled columns.

Fix the four signs

    [012] > 0,  [013] < 0,  [024] < 0,  [034] < 0.

After normalizing columns 0,1,2 to the standard basis and writing

    y_3=(a,b,c),  y_4=(d,e,f),

the conditions are exactly

    c < 0,  e > 0,  b*f-c*e < 0.

They force b*f < 0.  The sign of b therefore separates two components.  In
each component, after putting C=-c, E=e, B=|b|, F=|f|, the last inequality is
BF>CE; logarithms turn this into an open halfspace.  Hence there are exactly
two components, each an open cell.

Independently, the script enumerates all signed uniform rank-three
chirotopes on five labels directly from the Grassmann--Pluecker axiom.  The
fixed-sign fiber has 16 realizable vertices and its induced one-basis mutation
graph has two components of size eight.  A bounded integer search supplies an
exact realization of every vertex, so no catalog or floating point is used.

This is not a UOM(4,8) counterexample and does not disprove any diagonal.  It
only proves that global realizable-mutation connectivity, or the freedom of
unspecified brackets, cannot by itself prove the ninth diagonal.
"""

from itertools import product

import verify_mutation_graph_not_partial_cube as mutation


FIXED_BASES = ((0, 1, 2), (0, 1, 3), (0, 2, 4), (0, 3, 4))
FIXED_INDICES = tuple(mutation.BASIS_INDEX[basis] for basis in FIXED_BASES)
FIXED_COORDINATE_MASK = sum(1 << index for index in FIXED_INDICES)
FIXED_SIGN_MASK = 1 << FIXED_INDICES[0]


def components(vertices, adjacency):
    remaining = set(vertices)
    answer = []
    while remaining:
        start = min(remaining)
        remaining.remove(start)
        component = {start}
        stack = [start]
        while stack:
            current = stack.pop()
            for neighbor in adjacency[current]:
                if neighbor in remaining:
                    remaining.remove(neighbor)
                    component.add(neighbor)
                    stack.append(neighbor)
        answer.append(frozenset(component))
    return tuple(answer)


def partial_signs(last_two_columns):
    """Check the four fixed minors from their exact normalized formulas."""
    (_, b, c), (_, e, f) = last_two_columns
    return c > 0, c < 0, -e < 0, b * f - c * e < 0


def main():
    vertices = tuple(
        mask
        for mask in range(1 << len(mutation.BASES))
        if mutation.gp_failure(mask) is None
    )
    vertex_set = set(vertices)
    adjacency = {
        mask: tuple(
            neighbor
            for index in range(len(mutation.BASES))
            if (neighbor := mask ^ (1 << index)) in vertex_set
        )
        for mask in vertices
    }
    assert len(vertices) == 384

    fiber = tuple(
        mask
        for mask in vertices
        if mask & FIXED_COORDINATE_MASK == FIXED_SIGN_MASK
    )
    assert len(fiber) == 16
    fiber_set = set(fiber)
    fiber_adjacency = {
        mask: tuple(neighbor for neighbor in adjacency[mask] if neighbor in fiber_set)
        for mask in fiber
    }
    fiber_components = components(fiber, fiber_adjacency)
    assert tuple(sorted(map(len, fiber_components))) == (8, 8)
    assert {min(component) for component in fiber_components} == {1, 77}

    # Supply an exact normalized integer realization for all 16 fiber
    # chirotopes.  Zero coordinates are unnecessary, so this finite box is
    # enough and keeps the certificate reproducible.
    witnesses = {}
    coordinate_values = (-4, -3, -2, -1, 1, 2, 3, 4)
    for coordinates in product(coordinate_values, repeat=6):
        last_two = (coordinates[:3], coordinates[3:])
        try:
            mask = mutation.realization_mask(last_two)
        except AssertionError:  # a free bracket is zero, hence nongeneric
            continue
        if mask in fiber_set and mask not in witnesses:
            witnesses[mask] = last_two
            if len(witnesses) == len(fiber):
                break
    assert set(witnesses) == fiber_set

    # Recheck the fixed signs from the three displayed determinant formulas,
    # independently of the bit encoding.  The first entry [012]>0 is fixed by
    # the standard-basis normalization.
    for mask, last_two in witnesses.items():
        c_positive, c_negative, minus_e_negative, last_negative = partial_signs(
            last_two
        )
        assert not c_positive and c_negative and minus_e_negative and last_negative
        (_, b, c), (_, e, f) = last_two
        assert c * e < 0
        assert b * f < c * e < 0
        assert (b > 0) != (f > 0)
        assert mutation.realization_mask(last_two) == mask

    # The two graph components agree with the analytic invariant sign(b).
    sign_classes = {
        positive: {
            mask
            for mask, ((_, b, _), _) in witnesses.items()
            if (b > 0) == positive
        }
        for positive in (False, True)
    }
    assert set(map(frozenset, sign_classes.values())) == set(fiber_components)

    print("PASS: fixed-sign fiber has 16 exact realizable chirotopes")
    print("PASS: its free-mutation graph has two components of size 8")
    print("THEOREM: the partial realization space has exactly two open-cell components")
    print("SEPARATOR: sign(b)=-sign(f), with b*f < c*e < 0")
    print("SCOPE: generic mutation connectivity does not prove the UOM(4,8) ninth diagonal")


if __name__ == "__main__":
    main()
