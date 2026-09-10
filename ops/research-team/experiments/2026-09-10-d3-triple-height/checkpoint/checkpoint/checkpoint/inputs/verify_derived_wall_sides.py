#!/usr/bin/env python3
"""Exact verifier for one-sided tope loss at every UOM(4,8) derived wall.

``verify_derived_walls.py`` proves that the 4-by-4 determinants of the 56
derived normals have 14 structural-zero, 25 fixed parent-bracket, and 13
residual incidence orbits.  This checker supplies the additional circuit
certificate needed at every residual orbit.

For nine residual orbits there is a fifth normal ``z`` such that all four
cofactors obtained by replacing one wall normal by ``z`` are fixed and
nonzero.  The five-vector Grassmann identity then says that a tope aligned
with the wall circuit can occur on only one sign side of the residual.

The other four orbits are localization walls.  Write their four-set as
``C union {z}``, where ``|C|=3``.  There is a normal ``w`` for which
``det(C,w)`` is structurally zero while all three coefficients
``det(C-c+z+w)`` are fixed and nonzero.  The same five-vector identity gives

    sum_c coefficient[c] * v_c + det(C,z) * v_w = 0,

so a tope aligned with the three-circuit is again confined to one residual
side and is impossible on the wall.

All arithmetic and orbit tests are exact.  Orbit-stabilizer counts turn the
13 representative checks into an exhaustion of all 84,840 labeled residual
four-sets; no floating-point sampling is used.
"""

from contextlib import redirect_stdout
from io import StringIO
from itertools import permutations
from math import comb, factorial


# Importing the foundational checker executes all of its exact symbolic
# assertions.  Suppress its two success lines so this verifier has one concise
# report of its own.
with redirect_stdout(StringIO()):
    import verify_derived_walls as walls


def orbit_type(edges):
    """Return the stable 0..51 incidence-orbit index of four triples."""
    return ORBIT_INDEX[walls.orbit_key(tuple(edges))]


def relabel(edges, permutation):
    """Relabel a four-edge 3-graph by a permutation of its eight vertices."""
    return frozenset(
        tuple(sorted(permutation[vertex] for vertex in edge))
        for edge in edges
    )


def orbit_size(edges):
    """Compute an S_8 orbit size exactly by orbit-stabilizer."""
    target = frozenset(edges)
    stabilizer = sum(
        relabel(edges, permutation) == target
        for permutation in LABEL_PERMUTATIONS
    )
    assert stabilizer and factorial(8) % stabilizer == 0
    return factorial(8) // stabilizer


def four_row_certificate(edges):
    """Find an auxiliary normal making all four circuit cofactors fixed."""
    for auxiliary in walls.triples:
        if auxiliary in edges:
            continue
        cofactor_types = tuple(
            orbit_type(edges[:index] + edges[index + 1 :] + (auxiliary,))
            for index in range(4)
        )
        if all(kind in walls.FIXED for kind in cofactor_types):
            return auxiliary, cofactor_types
    return None


def parse_triple(label):
    return tuple(int(character) - 1 for character in label)


ORBIT_INDEX = {
    walls.orbit_key(representative): index
    for index, representative in enumerate(walls.representatives)
}
LABEL_PERMUTATIONS = tuple(permutations(range(8)))

# The imported checker already proves these categories by exact polynomial
# expansion.  Reassert the complete, disjoint 52-orbit partition here.
ZERO_TYPES = set(walls.ZERO)
FIXED_TYPES = set(walls.FIXED)
RESIDUAL_TYPES = set(walls.RESIDUAL)
assert len(ORBIT_INDEX) == len(walls.representatives) == 52
assert not (ZERO_TYPES & FIXED_TYPES)
assert not (ZERO_TYPES & RESIDUAL_TYPES)
assert not (FIXED_TYPES & RESIDUAL_TYPES)
assert ZERO_TYPES | FIXED_TYPES | RESIDUAL_TYPES == set(range(52))

# Verify the universal five-vector determinant identity over a generic 4-by-5
# matrix.  Both certificate forms in the module docstring are specializations
# of this single polynomial syzygy.
generic_entries = walls.sp.symbols("x0:20")
generic = walls.sp.Matrix(4, 5, generic_entries)
relation = walls.sp.zeros(4, 1)
for omitted in range(5):
    remaining = [column for column in range(5) if column != omitted]
    relation += (-1) ** omitted * generic[:, remaining].det() * generic[:, omitted]
assert all(walls.sp.expand(entry) == 0 for entry in relation)

# Exact labeled exhaustion.  The representatives have distinct complete
# orbit keys, and their orbit sizes sum to all C(56,4) four-sets.
ORBIT_SIZES = tuple(orbit_size(edges) for edges in walls.representatives)
assert sum(ORBIT_SIZES) == comb(56, 4) == 367_290

EXPECTED_RESIDUAL_SIZES = {
    36: 10_080,
    37: 5_040,
    38: 1_680,
    39: 2_520,
    41: 10_080,
    42: 2_520,
    44: 10_080,
    46: 6_720,
    47: 10_080,
    48: 840,
    49: 10_080,
    50: 10_080,
    51: 5_040,
}
assert RESIDUAL_TYPES == set(EXPECTED_RESIDUAL_SIZES)
assert {
    kind: ORBIT_SIZES[kind] for kind in RESIDUAL_TYPES
} == EXPECTED_RESIDUAL_SIZES
assert sum(EXPECTED_RESIDUAL_SIZES.values()) == 84_840

# Nine orbit representatives have ordinary four-row circuit certificates.
FOUR_ROW_TYPES = {37, 38, 41, 42, 44, 48, 49, 50, 51}
four_row_certificates = {
    kind: four_row_certificate(walls.representatives[kind])
    for kind in RESIDUAL_TYPES
}
assert {
    kind for kind, certificate in four_row_certificates.items()
    if certificate is not None
} == FOUR_ROW_TYPES
assert sum(EXPECTED_RESIDUAL_SIZES[kind] for kind in FOUR_ROW_TYPES) == 55_440

# The four exceptional representatives have exact three-row localization
# certificates.  Lists are one-based only for readability; parse_triple turns
# them into the zero-based triples used by the foundational checker.
LOCALIZATION_CERTIFICATES = {
    36: (("123", "345", "367"), "124", "134", (20, 11, 10), 15),
    39: (("123", "356", "378"), "124", "135", (33, 20, 18), 15),
    46: (("123", "145", "167"), "246", "124", (19, 19, 16), 15),
    47: (("123", "145", "167"), "248", "124", (20, 20, 16), 15),
}
assert set(LOCALIZATION_CERTIFICATES) == RESIDUAL_TYPES - FOUR_ROW_TYPES

for kind, (c_labels, z_label, w_label, expected_coefficients,
           expected_structural) in LOCALIZATION_CERTIFICATES.items():
    circuit = tuple(parse_triple(label) for label in c_labels)
    residual_normal = parse_triple(z_label)
    structural_normal = parse_triple(w_label)
    representative = walls.representatives[kind]

    assert frozenset(circuit + (residual_normal,)) == frozenset(representative)
    assert orbit_type(circuit + (residual_normal,)) == kind

    structural_type = orbit_type(circuit + (structural_normal,))
    assert structural_type == expected_structural
    assert structural_type in walls.ZERO

    coefficient_types = tuple(
        orbit_type(
            circuit[:index] + circuit[index + 1 :]
            + (residual_normal, structural_normal)
        )
        for index in range(3)
    )
    assert coefficient_types == expected_coefficients
    assert all(coefficient in walls.FIXED for coefficient in coefficient_types)

assert sum(
    EXPECTED_RESIDUAL_SIZES[kind] for kind in LOCALIZATION_CERTIFICATES
) == 29_400

print("PASS: all 13 residual orbits have fixed-sign circuit certificates")
print("PASS: 84,840 labeled walls = 55,440 four-row + 29,400 localization")
print("THEOREM: every circuit-aligned signature is wall-infeasible and one-sided")
