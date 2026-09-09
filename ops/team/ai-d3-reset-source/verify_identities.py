#!/usr/bin/env python3
"""Exact algebra supporting the source audit; this is not a D3 acceptance test.

The symbolic check certifies the universal 4-dimensional cofactor covariance
identity, by polynomial expansion. Rational checks exercise the quotient
normalization, including a negative-determinant frame change, and the joined
weight rescaling at zero blocks. No triangulation or topological claim is
inferred from passing these tests. Requires SymPy; no input from active lanes.
"""

from itertools import combinations
from math import prod
import json
import sympy as sp


def normal(columns):
    """a satisfies a.T*p = det([columns, p]), with columns a 4 by 3 matrix."""
    return sp.Matrix([
        (-1) ** (row + 3) * columns.extract(
            [i for i in range(4) if i != row], range(3)
        ).det()
        for row in range(4)
    ])


def normalize(parent):
    basis = parent[:, :4]
    coordinates = basis.inv() * parent[:, 4]
    if any(value == 0 for value in coordinates):
        raise ValueError("The fifth label is not a projective frame point")
    transform = sp.diag(*[1 / abs(value) for value in coordinates]) * basis.inv()
    columns = [sp.eye(4)[:, i] for i in range(4)]
    columns.append(sp.Matrix([sp.sign(value) for value in coordinates]))
    for j in range(5, 8):
        image = transform * parent[:, j]
        columns.append(image / sum(abs(value) for value in image))
    return sp.Matrix.hstack(*columns)


def check_universal_covariance():
    g = sp.Matrix(4, 4, sp.symbols("g0:16"))
    y = sp.Matrix(4, 3, sp.symbols("y0:12"))
    left = normal(g * y)
    right = g.cofactor_matrix() * normal(y)
    expanded = [sp.Poly(sp.expand(a - b), *g, *y) for a, b in zip(left, right)]
    if not all(p.is_zero for p in expanded):
        raise AssertionError("Universal cofactor covariance failed")
    d = sp.symbols("d0:3")
    scaled = normal(y * sp.diag(*d))
    if any(sp.expand(a - prod(d) * b) != 0 for a, b in zip(scaled, normal(y))):
        raise AssertionError("Triple column homogeneity failed")
    p = sp.Matrix(sp.symbols("p0:4"))
    if sp.expand((normal(y).T * p)[0] - y.row_join(p).det()) != 0:
        raise AssertionError("Normal convention has the wrong orientation")
    return {"covariance_polynomial_identities": 4, "triple_homogeneity_identities": 4,
            "determinant_orientation_identity": 1}


def check_frame_quotient():
    # A rational moment curve supplies 70 nonzero Vandermonde brackets.
    parent = sp.Matrix([[sp.Integer(t) ** power for t in range(1, 9)] for power in range(4)])
    if any(parent[:, list(indices)].det() == 0 for indices in combinations(range(8), 4)):
        raise AssertionError("The rational fixture is not uniform")
    base = normalize(parent)
    scales = sp.diag(2, 3, 5, 7, 11, 13, 17, 19)
    positive = sp.Matrix([[1, 2, 0, 1], [0, 1, 3, 0], [0, 0, 1, 4], [0, 0, 0, 1]])
    negative = sp.diag(-1, 1, 1, 1) * positive
    transforms = [sp.eye(4), positive, negative]
    for transform in transforms:
        transformed = transform * parent * scales
        if normalize(transformed) != base:
            raise AssertionError("Canonical normalization changed on a quotient orbit")
    if normalize(base) != base:
        raise AssertionError("Canonical normalization is not idempotent")
    for j in range(5, 8):
        if sum(abs(value) for value in base[:, j]) != 1:
            raise AssertionError("Simplex normalization failed")
    # Independent negative column scaling is deliberately outside the quotient.
    flipped = parent * sp.diag(1, 1, 1, 1, 1, -1, 1, 1)
    if normalize(flipped) == base:
        raise AssertionError("An independent reorientation was incorrectly quotiented")
    return {"uniform_parent_brackets_checked": 70, "positive_column_scale_cases": 3,
            "negative_determinant_case": True, "independent_reorientation_distinguished": True}


def check_joined_weight_gauge():
    # Actual parent cofactors, with a known five-normal linear dependence.
    parent = sp.Matrix([[sp.Integer(t) ** power for t in range(1, 9)] for power in range(4)])
    triples = list(combinations(range(8), 3))
    all_normals = sp.Matrix.hstack(*[normal(parent[:, list(t)]) for t in triples])
    indices = []
    for i in range(len(triples)):
        if all_normals[:, indices + [i]].rank() > len(indices):
            indices.append(i)
        if len(indices) == 4:
            break
    extra = next(i for i in range(len(triples)) if i not in indices)
    support = indices + [extra]
    relation = all_normals[:, support].nullspace()[0]
    # Reorient this finite support to make the dependence nonnegative.
    signs = [sp.sign(value) if value else sp.Integer(1) for value in relation]
    signed = all_normals[:, support] * sp.diag(*signs)
    weights = sp.Matrix([abs(value) for value in relation])
    weights /= sum(weights)
    if signed * weights != sp.zeros(4, 1):
        raise AssertionError("Fixture is not an exact nonnegative dependence")
    parent_scales = [sp.Integer(v) for v in [2, 3, 5, 7, 11, 13, 17, 19]]
    factors = [prod(parent_scales[j] for j in triples[i]) for i in support]
    transform = sp.Matrix([[1, 2, 0, 1], [0, 1, 3, 0], [0, 0, 1, 4], [0, 0, 0, 1]])
    new_parent = transform * parent * sp.diag(*parent_scales)
    new_signed = sp.Matrix.hstack(*[normal(new_parent[:, list(triples[i])]) for i in support]) * sp.diag(*signs)
    old_blocks = [weights / 3, sp.zeros(len(support), 1), weights * sp.Rational(2, 3)]
    raw_blocks = [sp.Matrix([block[i] / factors[i] for i in range(len(support))]) for block in old_blocks]
    normalization = sum(sum(block) for block in raw_blocks)
    new_blocks = [block / normalization for block in raw_blocks]
    if sum(sum(block) for block in new_blocks) != 1:
        raise AssertionError("Joined total mass was not preserved")
    for old, new in zip(old_blocks, new_blocks):
        if new_signed * new != sp.zeros(4, 1):
            raise AssertionError("Scaled block is not in the actual normal kernel")
        if [bool(v) for v in old] != [bool(v) for v in new]:
            raise AssertionError("A witness coordinate zero face was lost")
    reverse_raw = [sp.Matrix([block[i] * factors[i] for i in range(len(support))]) for block in new_blocks]
    denominator = sum(sum(block) for block in reverse_raw)
    if [block / denominator for block in reverse_raw] != old_blocks:
        raise AssertionError("Joined weight gauge did not invert")
    return {"actual_parent_normals_used": 56, "joined_blocks": 3,
            "zero_block_retained": True, "exact_inverse_verified": True,
            "extension_signature_validity_claimed": False}


def main():
    result = {"universal_algebra": check_universal_covariance(),
              "rational_quotient_cases": check_frame_quotient(),
              "rational_joined_weight_gauge": check_joined_weight_gauge(),
              "scope": "ALGEBRA_ONLY_NO_D3_OR_GLOBAL_TRIANGULATION_CERTIFICATE"}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
