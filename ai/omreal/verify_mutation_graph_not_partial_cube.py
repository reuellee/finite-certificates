#!/usr/bin/env python3
"""Exact determinant-wall warning for the derived-chamber strategy.

The tope graph of one fixed oriented matroid is a partial cube.  The graph
whose vertices are *chirotopes* and whose edges are one-basis mutations is a
different graph, and it need not be a partial cube.  This checker gives the
smallest elementary warning needed by ``ATLAS_HELLY.md``.

We enumerate every signed uniform rank-3 chirotope on five labeled elements.
Both global signs are retained, as they are in a determinant-wall chamber
graph.  The three-term Grassmann--Pluecker axiom is checked directly, so no
catalog or floating-point computation is trusted.  The one-basis-flip graph
has 384 vertices and 960 edges.  Its Djokovic--Winkler relation is not
transitive, which proves that the graph is not a partial cube.  Six explicit
integer realizations also certify a length-five mutation path between two
chirotopes whose natural basis-sign Hamming distance is three.

This is deliberately not claimed to be a counterexample inside one fixed
UOM(4,8) parent realization cell.  It proves only that general mutation-graph
facts cannot establish the partial-cube premise for that much more special
master chamber graph.
"""

from collections import deque
from itertools import combinations


ELEMENTS = tuple(range(5))
BASES = tuple(combinations(ELEMENTS, 3))
BASIS_INDEX = {basis: index for index, basis in enumerate(BASES)}


def permutation_sign(sequence):
    inversions = sum(
        sequence[left] > sequence[right]
        for left in range(len(sequence))
        for right in range(left + 1, len(sequence))
    )
    return -1 if inversions & 1 else 1


def chirotope(mask, ordered_basis):
    """Evaluate an alternating chirotope encoded on increasing triples."""
    increasing = tuple(sorted(ordered_basis))
    permutation = tuple(increasing.index(element) for element in ordered_basis)
    value = 1 if mask & (1 << BASIS_INDEX[increasing]) else -1
    return permutation_sign(permutation) * value


def gp_failure(mask):
    """Return a same-sign GP triple, or ``None`` when every axiom holds."""
    for common in ELEMENTS:
        first, second, third, fourth = (
            element for element in ELEMENTS if element != common
        )
        products = (
            chirotope(mask, (common, first, second))
            * chirotope(mask, (common, third, fourth)),
            -chirotope(mask, (common, first, third))
            * chirotope(mask, (common, second, fourth)),
            chirotope(mask, (common, first, fourth))
            * chirotope(mask, (common, second, third)),
        )
        if products[0] == products[1] == products[2]:
            return common, products
    return None


def determinant_3(columns):
    first, second, third = columns
    return (
        first[0] * (second[1] * third[2] - second[2] * third[1])
        - second[0] * (first[1] * third[2] - first[2] * third[1])
        + third[0] * (first[1] * second[2] - first[2] * second[1])
    )


def realization_mask(last_two_columns):
    columns = (
        (1, 0, 0),
        (0, 1, 0),
        (0, 0, 1),
    ) + last_two_columns
    mask = 0
    for index, basis in enumerate(BASES):
        determinant = determinant_3(tuple(columns[element] for element in basis))
        assert determinant != 0
        if determinant > 0:
            mask |= 1 << index
    return mask


def distances(adjacency, source):
    result = {source: 0}
    queue = deque((source,))
    while queue:
        vertex = queue.popleft()
        for neighbor in adjacency[vertex]:
            if neighbor not in result:
                result[neighbor] = result[vertex] + 1
                queue.append(neighbor)
    return result


def theta(distance, first_edge, second_edge):
    """Djokovic--Winkler relation for two unoriented graph edges."""
    u, v = first_edge
    x, y = second_edge
    return (
        distance[u][x] + distance[v][y]
        != distance[u][y] + distance[v][x]
    )


def sign_string(mask):
    return "".join(
        "+" if mask & (1 << index) else "-" for index in range(len(BASES))
    )


def main():
    vertices = tuple(
        mask
        for mask in range(1 << len(BASES))
        if gp_failure(mask) is None
    )
    vertex_set = set(vertices)
    adjacency = {
        mask: tuple(
            neighbor
            for index in range(len(BASES))
            if (neighbor := mask ^ (1 << index)) in vertex_set
        )
        for mask in vertices
    }
    assert len(vertices) == 384
    assert sum(map(len, adjacency.values())) // 2 == 960

    distance = {source: distances(adjacency, source) for source in vertices}
    assert all(len(row) == len(vertices) for row in distance.values())

    # A direct nontransitivity certificate for the Djokovic--Winkler relation.
    first = (6, 7)
    middle = (0, 1)
    last = (74, 75)
    assert all(right in adjacency[left] for left, right in (first, middle, last))
    assert theta(distance, first, middle)
    assert theta(distance, middle, last)
    assert not theta(distance, first, last)

    # A transparent natural-coordinate metric obstruction.  The endpoints
    # differ only at bases 125, 134, and 234, but none can be the first flip:
    # each proposed intermediate violates one exact GP relation.
    source, target = 1, 77
    differing = tuple(
        index
        for index in range(len(BASES))
        if (source ^ target) & (1 << index)
    )
    assert tuple(BASES[index] for index in differing) == (
        (0, 1, 4),
        (0, 2, 3),
        (1, 2, 3),
    )
    assert all(gp_failure(source ^ (1 << index)) is not None for index in differing)
    assert distance[source][target] == 5 > len(differing) == 3

    path = (1, 3, 7, 15, 79, 77)
    assert all(right in adjacency[left] for left, right in zip(path, path[1:]))

    # Independent exact realizability witnesses for every vertex on the path.
    # Each matrix is [e1,e2,e3,u,v], represented here by its last two columns.
    realizations = {
        1: ((-1, 1, -1), (-1, 2, -4)),
        3: ((-1, 1, 1), (-1, 2, -1)),
        7: ((-1, 1, 2), (-1, 2, 1)),
        15: ((-1, -1, 2), (-1, 2, 1)),
        79: ((1, -1, 2), (-3, 1, 1)),
        77: ((1, -1, -1), (-2, 1, 3)),
    }
    assert tuple(realizations) == path
    assert all(
        realization_mask(realizations[mask]) == mask for mask in realizations
    )

    assert sign_string(source) == "+---------"
    assert sign_string(target) == "+-++--+---"
    print("PASS: 384 signed rank-3 chirotopes on 5 labels and 960 mutations")
    print("PASS: exact integer realizations certify the length-five path")
    print("PASS: Djokovic--Winkler relation is not transitive")
    print("THEOREM: the chirotope mutation graph is not a partial cube")
    print("SCOPE: this is not a fixed-UOM(4,8)-cell counterexample")


if __name__ == "__main__":
    main()
