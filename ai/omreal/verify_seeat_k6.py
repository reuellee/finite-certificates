#!/usr/bin/env python3
"""Standalone exact verifier for a six-chart lower bound at parent row 2599.

The certificate contains six exact realizable extension signatures.  Every one
of their 15 pairs has a branch-free contradiction in the 28 unknown mixed
rank-4 brackets of a putative uniform two-element amalgam.  Hence one parent
chart contains at most one of the six signatures.
"""

from itertools import combinations
from pathlib import Path
import sys

import numpy as np


DEFAULT = Path(__file__).resolve().parent / "data" / "seeat_parent2599_k6.npz"


def colex_subsets(n, size):
    return tuple(
        sorted(combinations(range(1, n + 1), size), key=lambda x: tuple(reversed(x)))
    )


BASES8 = colex_subsets(8, 4)
BASE8_INDEX = {b: i for i, b in enumerate(BASES8)}
TRIPLES8 = colex_subsets(8, 3)
TRIPLE_INDEX = {b: i for i, b in enumerate(TRIPLES8)}
PAIRS8 = colex_subsets(8, 2)
PAIR_INDEX = {b: i for i, b in enumerate(PAIRS8)}


def sort_with_parity(values):
    values = list(values)
    parity = 0
    for i in range(1, len(values)):
        j = i
        while j and values[j - 1] > values[j]:
            values[j - 1], values[j] = values[j], values[j - 1]
            parity ^= 1
            j -= 1
    return tuple(values), parity


def bracket_template(basis, parent):
    new_count = (9 in basis) + (10 in basis)
    if new_count == 0:
        return int(parent[BASE8_INDEX[basis]]), None, None, None
    if new_count == 1:
        new_element = 9 if 9 in basis else 10
        triple = tuple(x for x in basis if x != new_element)
        bit = TRIPLE_INDEX[triple]
        return 0, bit if new_element == 9 else None, bit if new_element == 10 else None, None
    pair = tuple(x for x in basis if x <= 8)
    return 0, None, None, PAIR_INDEX[pair]


def relation_templates(parent):
    relations = []
    for lam in combinations(range(1, 11), 2):
        rest = [x for x in range(1, 11) if x not in lam]
        for a, b, c, d in combinations(rest, 4):
            terms = []
            for pairsets, explicit_minus in (
                (((a, b), (c, d)), 0),
                (((a, c), (b, d)), 1),
                (((a, d), (b, c)), 0),
            ):
                constant = explicit_minus
                pbits, qbits, variables = [], [], []
                for x, y in pairsets:
                    basis, parity = sort_with_parity(lam + (x, y))
                    constant ^= parity
                    known, pbit, qbit, variable = bracket_template(basis, parent)
                    constant ^= known
                    if pbit is not None:
                        pbits.append(pbit)
                    if qbit is not None:
                        qbits.append(qbit)
                    if variable is not None:
                        variables.append(variable)
                terms.append((tuple(variables), constant, tuple(pbits), tuple(qbits)))
            relations.append(tuple(terms))
    assert len(relations) == 3150
    return tuple(relations)


def resolve(template, sigma, tau):
    relation = []
    for variables, constant, pbits, qbits in template:
        for bit in pbits:
            constant ^= (sigma >> bit) & 1
        for bit in qbits:
            constant ^= (tau >> bit) & 1
        relation.append((variables, constant))
    return tuple(relation)


def unassigned(relation, values):
    return {v for variables, _ in relation for v in variables if v not in values}


def parities(relation, values):
    answer = []
    for variables, constant in relation:
        for variable in variables:
            constant ^= values[variable]
        answer.append(constant)
    return tuple(answer)


def valid(relation, values):
    p = parities(relation, values)
    return not (p[0] == p[1] == p[2])


def generic_gp_valid(parent, sigma=None):
    n = 8 if sigma is None else 9
    bases = colex_subsets(n, 4)
    index = {basis: i for i, basis in enumerate(bases)}
    signs = []
    for basis in bases:
        if 9 not in basis:
            signs.append(int(parent[BASE8_INDEX[basis]]))
        else:
            triple = tuple(x for x in basis if x != 9)
            signs.append((int(sigma) >> TRIPLE_INDEX[triple]) & 1)
    for lam in combinations(range(1, n + 1), 2):
        rest = [x for x in range(1, n + 1) if x not in lam]
        for a, b, c, d in combinations(rest, 4):
            products = []
            for pairsets, explicit_minus in (
                (((a, b), (c, d)), 0),
                (((a, c), (b, d)), 1),
                (((a, d), (b, c)), 0),
            ):
                product = explicit_minus
                for x, y in pairsets:
                    basis, alternating = sort_with_parity(lam + (x, y))
                    product ^= alternating ^ signs[index[basis]]
                products.append(product)
            if products[0] == products[1] == products[2]:
                return False
    return True


def determinant(matrix):
    matrix = [[int(value) for value in row] for row in matrix]
    if len(matrix) == 1:
        return matrix[0][0]
    total = 0
    for column, value in enumerate(matrix[0]):
        minor = [row[:column] + row[column + 1 :] for row in matrix[1:]]
        total += (-1 if column & 1 else 1) * value * determinant(minor)
    return total


def parent_and_extension(matrix, point):
    parent = []
    for basis in BASES8:
        value = determinant(matrix[:, np.asarray(basis) - 1].tolist())
        if not value:
            raise AssertionError(f"zero parent bracket {basis}")
        parent.append(int(value > 0))
    signature = 0
    for bit, triple in enumerate(TRIPLES8):
        columns = matrix[:, np.asarray(triple) - 1]
        row = []
        for coordinate in range(4):
            minor = np.delete(columns, coordinate, axis=0)
            row.append(((-1) ** (coordinate + 5)) * determinant(minor.tolist()))
        value = sum(int(a) * int(x) for a, x in zip(row, point))
        if not value:
            raise AssertionError(f"zero extension bracket {triple}")
        signature |= int(value > 0) << bit
    return np.asarray(parent, dtype=np.uint8), signature


def main():
    path = Path(sys.argv[1]) if len(sys.argv) == 2 else DEFAULT
    if len(sys.argv) > 2:
        raise SystemExit(f"usage: {sys.argv[0]} [certificate.npz]")
    cert = np.load(path, allow_pickle=False)
    fields = {
        "format", "parent_index", "parent_bits", "vertex_signature",
        "realization_matrix", "realization_point", "edge_uv", "trace_offset",
        "trace_var", "trace_value", "trace_relation", "final_relation",
        "positive_mixed",
    }
    if set(cert.files) != fields:
        raise AssertionError(f"wrong fields: {sorted(cert.files)}")
    if str(cert["format"].item()) != "seeat-parent2599-k6-v1":
        raise AssertionError("wrong format")
    if int(cert["parent_index"].item()) != 2599:
        raise AssertionError("wrong parent index")
    parent = cert["parent_bits"]
    signatures = cert["vertex_signature"]
    matrices = cert["realization_matrix"]
    points = cert["realization_point"]
    if parent.shape != (70,) or set(parent.tolist()) - {0, 1}:
        raise AssertionError("bad parent")
    if signatures.shape != (6,) or len(set(map(int, signatures))) != 6:
        raise AssertionError("need six distinct signatures")
    if matrices.shape != (6, 4, 8) or points.shape != (6, 4):
        raise AssertionError("bad realization witness shapes")
    if not generic_gp_valid(parent):
        raise AssertionError("parent is not a uniform chirotope")
    for i, (signature, matrix, point) in enumerate(zip(signatures, matrices, points)):
        if not generic_gp_valid(parent, int(signature)):
            raise AssertionError(f"vertex {i} is not an abstract uniform extension")
        got_parent, got_signature = parent_and_extension(matrix, point)
        if not np.array_equal(got_parent, parent) or got_signature != int(signature):
            raise AssertionError(f"vertex {i} exact realization has wrong signs")
    print("PASS six distinct realizable uniform extensions over parent 2599")

    edges = cert["edge_uv"]
    expected_edges = np.asarray(list(combinations(range(6), 2)), dtype=np.uint8)
    if not np.array_equal(edges, expected_edges):
        raise AssertionError("edge list is not K6")
    offsets = cert["trace_offset"].astype(int)
    if offsets.shape != (16,) or offsets[0] != 0:
        raise AssertionError("bad trace offsets")
    if not (
        offsets[-1]
        == len(cert["trace_var"])
        == len(cert["trace_value"])
        == len(cert["trace_relation"])
    ):
        raise AssertionError("bad flattened trace arrays")
    if cert["final_relation"].shape != (15,):
        raise AssertionError("bad final-relation array")
    templates = relation_templates(parent)
    sizes = []
    for edge_index, (u0, v0) in enumerate(edges):
        u, v = int(u0), int(v0)
        sigma, tau = int(signatures[u]), int(signatures[v])
        values = {}
        start, stop = offsets[edge_index : edge_index + 2]
        sizes.append(stop - start)
        for step in range(start, stop):
            variable = int(cert["trace_var"][step])
            value = int(cert["trace_value"][step])
            relation_id = int(cert["trace_relation"][step])
            if not (0 <= variable < 28 and value in (0, 1) and 0 <= relation_id < 3150):
                raise AssertionError(f"edge {edge_index}: malformed trace step")
            if variable in values:
                raise AssertionError(f"edge {edge_index}: variable forced twice")
            relation = resolve(templates[relation_id], sigma, tau)
            if unassigned(relation, values) != {variable}:
                raise AssertionError(f"edge {edge_index}: cited GP relation is not unit")
            choices = []
            for trial in (0, 1):
                values[variable] = trial
                choices.append(valid(relation, values))
                del values[variable]
            if choices.count(True) != 1 or not choices[value]:
                raise AssertionError(f"edge {edge_index}: wrong forced value")
            values[variable] = value
        final_id = int(cert["final_relation"][edge_index])
        if not 0 <= final_id < 3150:
            raise AssertionError(f"edge {edge_index}: bad final relation")
        final = resolve(templates[final_id], sigma, tau)
        if unassigned(final, values) or valid(final, values):
            raise AssertionError(f"edge {edge_index}: final GP relation is not contradictory")
    print(
        f"PASS all 15 pairwise non-amalgamation certificates "
        f"({sum(sizes)} propagation steps, {min(sizes)}..{max(sizes)} per edge)"
    )

    positive = {i: int(value) for i, value in enumerate(cert["positive_mixed"])}
    if len(positive) != 28 or set(positive.values()) - {0, 1}:
        raise AssertionError("bad positive control")
    sigma = int(signatures[0])
    for relation_id, template in enumerate(templates):
        relation = resolve(template, sigma, sigma)
        if not valid(relation, positive):
            raise AssertionError(f"positive control fails GP relation {relation_id}")
    print("PASS positive control: a full uniform amalgam of vertex 0 with itself")
    print("THEOREM: atlas width(parent 2599) >= 6; no five-chart atlas exists")


if __name__ == "__main__":
    main()
