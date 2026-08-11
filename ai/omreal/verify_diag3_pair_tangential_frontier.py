#!/usr/bin/env python3
"""Exact two-parameter frontier for the row-2599 E02 tangential strip.

Use ``s`` on the complete negative q0 branch, normalized so that ``s=0``
is the transverse node and ``s=1`` is the parent wall 3578.  Use ``u>=0``
for the elementary column shear ``8 -> 3,+``.  This checker constructs the
exact bivariate parent and residual polynomials on that affine plane.

The full residual census is reduced to the factors whose fixed-unit wall
circuit is positive for receiver block 1.  Tensor-product Bernstein
coefficients on the exact parent quadrilateral prove that every such factor
is strict in the open strip.  Factor 12874 is exactly ``s``; six other
factors vanish only where the two parent facets meet.  Thus block 1 is
feasible in the open strip and bad on its whole ``s=0`` side; the other
three sides are the attaching q0 edge and the two genuine parent walls
3578/1268.  This supplies the two-dimensional frontier audit which a
pointwise first-exit argument alone cannot provide.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations
from itertools import permutations
from math import comb, lcm
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
REPO_MODULES = (
    HERE
    if (HERE / "DIAG9_GRAPH_exact_topes.py").exists()
    else HERE.parent / "finite-certificates-disk" / "ai" / "omreal"
)
sys.path.insert(0, str(REPO_MODULES))

import DIAG9_GRAPH_exact_topes as topes  # noqa: E402
import DIAG9_GRAPH_global_factor_census as global_factors  # noqa: E402
import DIAG9_GRAPH_verify_row2599_disk as polynomial  # noqa: E402
import BLOCK_GORDAN_RESIDUAL_MUTATION_MAP_NO_GO as mutation  # noqa: E402
import prototype_koszul_circuits as koszul  # noqa: E402
import verify_diag2_moving_witness_shear as moving  # noqa: E402
import verify_diag3_pair_four_ray_refinement as refinement  # noqa: E402
import verify_diag3_pair_receiver_end_canary as receiver  # noqa: E402

FORMAT = "diag3-pair-tangential-frontier-v2"
PAIR_ROOT = (8, 3, 1)
SPECIAL_TRIPLE_FACTOR = 12_874
IDENTICALLY_ZERO_Q0_FACTOR = 1_657
EXPECTED_TRANSVERSE_DETERMINANT = -63_617
EXPECTED_PARENT_VERTICES = (
    (Fraction(0), Fraction(0)),
    (
        Fraction(0),
        Fraction(
            1_242_824_577_394_768_117_863_801_581_302_239_329,
            238_485_905_530_905_664_425_242_932_573_216_734_720,
        ),
    ),
    (Fraction(1), Fraction(0)),
    (
        Fraction(1),
        Fraction(
            1_746_971_392_373_005_778_516_384_650_301,
            15_118_891_458_698_563_990_413_056_881_280,
        ),
    ),
)
EXPECTED_ALL_FACTOR_DEGREES = {-1: 1, 0: 1_470, 1: 10_959, 2: 14_286, 3: 24}
EXPECTED_DISTINCT_RESTRICTIONS = 24_515
EXPECTED_ACTIVE_FACTOR_COUNT = 1_707
EXPECTED_ACTIVE_FACTOR_DIGEST = (
    "bf392d7227d6fc2d90542d6c59d92b51731458f222d54281c29617ab9e527af4"
)
EXPECTED_POSITIVE_RECORD_DIGEST = (
    "13b8b8589a0bd8fad48fe6900e2aa944ba8c6310d83b8109ab184e8a1c96b7f5"
)
EXPECTED_ACTIVE_DEGREES = {0: 84, 1: 823, 2: 787, 3: 13}
EXPECTED_ACTIVE_POSITIVE_OCCURRENCES = 5_551
EXPECTED_ACTIVE_KIND_COUNTS = {
    36: 1_118,
    37: 174,
    38: 77,
    39: 151,
    41: 333,
    42: 101,
    44: 333,
    46: 736,
    47: 1_338,
    48: 22,
    49: 351,
    50: 598,
    51: 219,
}
EXPECTED_OCCURRENCES_PER_FACTOR = {
    1: 1_224, 2: 30, 3: 62, 4: 66, 5: 29, 6: 37, 7: 27, 8: 29,
    9: 36, 10: 29, 11: 15, 12: 23, 13: 21, 14: 8, 15: 9, 16: 8,
    17: 6, 18: 6, 19: 6, 21: 10, 22: 5, 23: 2, 25: 1, 26: 1,
    28: 2, 29: 1, 30: 1, 31: 2, 32: 1, 35: 5, 39: 2, 41: 3,
}
EXPECTED_ACTIVE_DISTINCT_RESTRICTIONS = 1_579
EXPECTED_PARENT_CORNER_FACTORS = (14_658, 14_798, 16_735, 16_850, 17_313, 17_314)
EXPECTED_BERNSTEIN_HISTOGRAM = {
    (0, 0, 0, (1,)): 84,
    (1, 1, 0, (-1,)): 57,
    (1, 1, 0, (0, 1)): 1,
    (1, 1, 0, (1,)): 113,
    (1, 1, 1, (-1,)): 513,
    (1, 1, 1, (1,)): 139,
    (2, 2, 0, (1,)): 1,
    (2, 2, 1, (-1,)): 286,
    (2, 2, 1, (0, 1)): 3,
    (2, 2, 1, (1,)): 165,
    (2, 2, 2, (-1,)): 170,
    (2, 2, 2, (-1, 0)): 1,
    (2, 2, 2, (0, 1)): 2,
    (2, 2, 2, (1,)): 159,
    (3, 3, 1, (-1,)): 5,
    (3, 3, 1, (1,)): 5,
    (3, 3, 2, (-1,)): 1,
    (3, 3, 2, (1,)): 2,
}

# Pinned after the complete exact replay.
EXPECTED_SEMANTIC_DIGEST = (
    "f9788b5785e68c62e77d8c355554730e0ab39581c4325c58c65e3f2b7373345e"
)


def determinant_integer(matrix):
    if len(matrix) == 1:
        return matrix[0][0]
    return sum(
        (-1 if column & 1 else 1)
        * value
        * determinant_integer(
            [row[:column] + row[column + 1 :] for row in matrix[1:]]
        )
        for column, value in enumerate(matrix[0])
    )


def exact_divide(left, right):
    """Exact two-variable lexicographic division over QQ."""

    remainder = {monomial: Fraction(value) for monomial, value in left.items()}
    divisor = {monomial: Fraction(value) for monomial, value in right.items()}
    quotient = {}
    leading_divisor = max(divisor)
    leading_coefficient = divisor[leading_divisor]
    while remainder:
        leading_remainder = max(remainder)
        if any(
            left_degree < right_degree
            for left_degree, right_degree in zip(
                leading_remainder, leading_divisor, strict=True
            )
        ):
            return None
        shift = tuple(
            left_degree - right_degree
            for left_degree, right_degree in zip(
                leading_remainder, leading_divisor, strict=True
            )
        )
        coefficient = remainder[leading_remainder] / leading_coefficient
        quotient[shift] = quotient.get(shift, 0) + coefficient
        for monomial, value in divisor.items():
            target = tuple(
                degree + offset
                for degree, offset in zip(monomial, shift, strict=True)
            )
            remainder[target] = remainder.get(target, 0) - coefficient * value
            if not remainder[target]:
                del remainder[target]
    return quotient


def family_matrix():
    """Return an integral polynomial matrix for Y(s,u)."""

    endpoint = receiver.node_branch_end_labels()[0]["negative"][0]
    node = receiver.branch_parent(0, Fraction(0))
    outer = receiver.branch_parent(0, endpoint)
    coefficients = []
    denominator = 1
    for row in range(4):
        coefficient_row = []
        for column in range(8):
            entry = (
                node[row][column],
                outer[row][column] - node[row][column],
                node[row][2] if column == 7 else Fraction(0),
            )
            for value in entry:
                denominator = lcm(denominator, value.denominator)
            coefficient_row.append(entry)
        coefficients.append(coefficient_row)

    matrix = []
    for row in range(4):
        polynomial_row = []
        for column in range(8):
            constant, s_coefficient, u_coefficient = coefficients[row][column]
            entry = {}
            for monomial, value in zip(
                ((0, 0), (1, 0), (0, 1)),
                (constant, s_coefficient, u_coefficient),
                strict=True,
            ):
                if value:
                    entry[monomial] = int(value * denominator)
            polynomial_row.append(entry)
        matrix.append(polynomial_row)
    return endpoint, denominator, tuple(tuple(row) for row in matrix)


def embedding_audit(matrix):
    """Certify that the affine (s,u)-family is an embedded two-plane."""

    s_direction = []
    u_direction = []
    for row in matrix:
        for entry in row:
            s_direction.append(entry.get((1, 0), 0))
            u_direction.append(entry.get((0, 1), 0))
            if any(sum(monomial) > 1 for monomial in entry):
                raise AssertionError("the parameter family is no longer affine")

    nonzero_minors = []
    for first, second in combinations(range(len(s_direction)), 2):
        minor = (
            s_direction[first] * u_direction[second]
            - s_direction[second] * u_direction[first]
        )
        if minor:
            nonzero_minors.append((first, second, minor))
    if not nonzero_minors:
        raise AssertionError("the q0 and shear parameter directions are dependent")

    source = receiver.node.slice_verify.source_parent()
    source_column = tuple(int(source[row, 7]) for row in range(4))
    target_column = tuple(int(source[row, 2]) for row in range(4))
    first_normal = [0, 0, 0, 0]
    second_normal = [0, 0, 0, 0]
    first_normal[receiver.node.disk.FIRST_POSITION[0]] = 1
    second_normal[receiver.node.disk.SECOND_POSITION[0]] = 1
    transverse = moving.det4(
        source_column, tuple(first_normal), tuple(second_normal), target_column
    )
    if transverse != EXPECTED_TRANSVERSE_DETERMINANT:
        raise AssertionError(f"tangential transversality changed: {transverse}")

    # Linear independence makes the affine parameter map injective.  Its
    # restriction from the compact quadrilateral into the ambient matrix
    # space is therefore a homeomorphism onto its (closed) image.
    return transverse, nonzero_minors[0]


def parent_brackets(matrix):
    answer = {}
    for basis in combinations(range(8), 4):
        label = "".join(str(column + 1) for column in basis)
        answer[label] = global_factors.primitive(
            polynomial.determinant(
                [[matrix[row][column] for column in basis] for row in range(4)]
            )
        )
    degrees = Counter(global_factors.total_degree(value) for value in answer.values())
    if degrees != {0: 35, 1: 35}:
        raise AssertionError(f"parent bracket degree census changed: {degrees}")
    return answer


def derived_normals(matrix):
    normals = []
    for triple in topes.TRIPLES:
        normal = []
        for omitted in range(4):
            rows = [row for row in range(4) if row != omitted]
            value = polynomial.determinant(
                [[matrix[row][column] for column in triple] for row in rows]
            )
            if (omitted + 3) & 1:
                value = {monomial: -coefficient for monomial, coefficient in value.items()}
            normal.append(value)
        normals.append(tuple(normal))
    degrees = Counter(
        global_factors.total_degree(coordinate)
        for normal in normals
        for coordinate in normal
    )
    if degrees != {0: 140, 1: 84}:
        raise AssertionError(f"derived-normal degree census changed: {degrees}")
    return tuple(normals)


def restriction_polynomials(normals, brackets, factor_data):
    foursets, factor_occurrences, offsets, units, labels = factor_data
    records = []
    for factor, occurrences in enumerate(factor_occurrences):
        occurrence = min(
            occurrences,
            key=lambda item: (offsets[item + 1] - offsets[item], item),
        )
        value = global_factors.primitive(
            polynomial.determinant(
                [
                    [normals[index][coordinate] for coordinate in range(4)]
                    for index in foursets[occurrence]
                ]
            )
        )
        for unit in units[offsets[occurrence] : offsets[occurrence + 1]]:
            quotient = exact_divide(value, brackets[labels[unit]])
            if quotient is None:
                raise AssertionError(
                    f"factor {factor}: parent unit {labels[unit]} did not divide"
                )
            value = global_factors.primitive(quotient)
        records.append(value)

    degrees = dict(
        sorted(Counter(global_factors.total_degree(value) for value in records).items())
    )
    if degrees != EXPECTED_ALL_FACTOR_DEGREES:
        raise AssertionError(f"full bivariate factor degrees changed: {degrees}")
    distinct = len({tuple(sorted(value.items())) for value in records})
    if distinct != EXPECTED_DISTINCT_RESTRICTIONS:
        raise AssertionError(f"restricted factor coincidence census changed: {distinct}")
    zero_factors = tuple(index for index, value in enumerate(records) if not value)
    if zero_factors != (IDENTICALLY_ZERO_Q0_FACTOR,):
        raise AssertionError(
            f"the q0 plane has the wrong identically zero factors: {zero_factors}"
        )
    return tuple(records)


TRIPLE_INDEX = {tuple(triple): index for index, triple in enumerate(koszul.TRIPLES)}


def relabel_normal(index, permutation):
    triple = koszul.TRIPLES[index]
    image = tuple(sorted(permutation[label - 1] + 1 for label in triple))
    return TRIPLE_INDEX[image]


def fixed_unit_relation_table(foursets):
    """Cover all labeled occurrences by relabeled fixed-unit certificates.

    Each coefficient support below is a four-normal determinant in one of
    the fixed parent-bracket-unit orbits.  Therefore its sign cannot change
    inside a uniform parent cell.  Evaluating it at the q0 midpoint gives the
    wall-circuit color globally on this parent cell, rather than only at a
    sampled wall point.
    """

    mutation.verify_wall_certificate_partition()
    table = {}
    for kind in sorted(mutation.RESIDUAL_TYPES):
        occurrence = tuple(mutation.REPRESENTATIVES[kind])
        if kind in mutation.ORDINARY_TYPES:
            circuit = occurrence
            certificate = mutation.ordinary_certificate(circuit)
            if certificate is None:
                raise AssertionError(f"ordinary type {kind} lost its unit auxiliary")
            auxiliary, replacement_types = certificate
            if not all(koszul.orbit_kind(value) == "unit" for value in replacement_types):
                raise AssertionError("ordinary coefficient is not a parent unit")
            coefficient_supports = tuple(
                circuit[:omitted] + circuit[omitted + 1 :] + (auxiliary,)
                for omitted in range(4)
            )
        else:
            circuit_names, z_name, w_name, _types, _zero = (
                mutation.LOCALIZATION_CERTIFICATES[kind]
            )
            circuit = mutation.indices(circuit_names)
            residual = mutation.NAME_TO_INDEX[z_name]
            auxiliary = mutation.NAME_TO_INDEX[w_name]
            coefficient_supports = tuple(
                circuit[:omitted]
                + circuit[omitted + 1 :]
                + (residual, auxiliary)
                for omitted in range(3)
            )
            if frozenset(circuit + (residual,)) != frozenset(occurrence):
                raise AssertionError("localization occurrence/circuit mismatch")
            if not all(
                koszul.orbit_kind(mutation.orbit(support)) == "unit"
                for support in coefficient_supports
            ):
                raise AssertionError("localization coefficient is not a parent unit")

        for permutation in permutations(range(8)):
            moved_occurrence = tuple(
                sorted(relabel_normal(index, permutation) for index in occurrence)
            )
            table.setdefault(
                moved_occurrence,
                (
                    kind,
                    tuple(relabel_normal(index, permutation) for index in circuit),
                    tuple(
                        tuple(relabel_normal(index, permutation) for index in support)
                        for support in coefficient_supports
                    ),
                ),
            )

    universe = set(map(tuple, foursets))
    if set(table) != universe or len(universe) != 84_840:
        raise AssertionError(
            f"fixed-unit labeled coverage changed: table={len(table)} "
            f"universe={len(universe)}"
        )
    return table


def certified_relation_signs(normals, circuit, coefficient_supports):
    signs = []
    for omitted, support in enumerate(coefficient_supports):
        value = determinant_integer(
            [[int(coordinate) for coordinate in normals[index]] for index in support]
        )
        if omitted & 1:
            value = -value
        signs.append((value > 0) - (value < 0))
    if not all(signs) or len(signs) != len(circuit):
        raise AssertionError("a fixed parent-unit circuit coefficient vanished")
    return tuple(signs)


def active_factor_scan(endpoint, factor_data, u0, u1):
    """Find every factor carrying a positive block-1 wall circuit."""

    midpoint = receiver.integer_parent(receiver.branch_parent(0, endpoint / 2))
    normals = topes.derived_rows(midpoint, normalize=False)

    # A second exact point lies strictly inside the parent quadrilateral.
    # Agreement there is a direct replay check of the fixed-parent-unit
    # assertion used to transport every wall-circuit color.
    second_s = Fraction(1, 3)
    second_u = Fraction(1, 100)
    if not (0 < second_u < u0 + (u1 - u0) * second_s):
        raise AssertionError("the second fixed-unit sample left the quadrilateral")
    second_parent = receiver.branch_parent(0, endpoint * second_s)
    node_parent = receiver.branch_parent(0, Fraction(0))
    for row in range(4):
        second_parent[row][7] += second_u * node_parent[row][2]
    second_normals = topes.derived_rows(
        receiver.integer_parent(second_parent), normalize=False
    )

    signature = receiver.RECEIVER_SIGNATURES[1]
    foursets, factor_occurrences, _offsets, _units, _labels = factor_data
    if len(foursets) != 84_840 or sum(map(len, factor_occurrences)) != 84_840:
        raise AssertionError("global labeled residual occurrence census changed")
    relation_table = fixed_unit_relation_table(foursets)
    active = []
    positive_records = []
    for factor, occurrences in enumerate(factor_occurrences):
        local = []
        for occurrence in occurrences:
            fourset = tuple(foursets[occurrence])
            kind, circuit, coefficient_supports = relation_table[fourset]
            expected_support, expected_kind = refinement.occurrence_circuit(fourset)
            if kind != expected_kind or frozenset(circuit) != frozenset(expected_support):
                raise AssertionError("fixed-unit table disagrees with occurrence circuit")
            signs = certified_relation_signs(normals, circuit, coefficient_supports)
            if signs != certified_relation_signs(
                second_normals, circuit, coefficient_supports
            ):
                raise AssertionError("a certified parent-unit coefficient changed sign")
            if refinement.circuit_positive(circuit, signs, signature):
                ordered = sorted(zip(circuit, signs, strict=True))
                if ordered[0][1] < 0:
                    ordered = [(index, -value) for index, value in ordered]
                support = tuple(index for index, _value in ordered)
                normalized_signs = tuple(value for _index, value in ordered)
                local.append((occurrence, support, kind, normalized_signs))
        if local:
            active.append(factor)
            positive_records.extend((factor,) + row for row in local)

    active_digest = sha256(repr(tuple(active)).encode("ascii")).hexdigest()
    if len(active) != EXPECTED_ACTIVE_FACTOR_COUNT:
        raise AssertionError(f"active block-1 factor count changed: {len(active)}")
    if active_digest != EXPECTED_ACTIVE_FACTOR_DIGEST:
        raise AssertionError(f"active block-1 factor list changed: {active_digest}")
    if len(positive_records) != EXPECTED_ACTIVE_POSITIVE_OCCURRENCES:
        raise AssertionError("active block-1 occurrence count changed")
    by_factor = Counter(row[0] for row in positive_records)
    occurrence_histogram = dict(sorted(Counter(by_factor.values()).items()))
    if occurrence_histogram != EXPECTED_OCCURRENCES_PER_FACTOR:
        raise AssertionError(
            f"positive occurrences/factor changed: {occurrence_histogram}"
        )
    kinds = dict(sorted(Counter(row[3] for row in positive_records).items()))
    if kinds != EXPECTED_ACTIVE_KIND_COUNTS:
        raise AssertionError(f"active occurrence-type census changed: {kinds}")
    record_digest = sha256(repr(tuple(positive_records)).encode("ascii")).hexdigest()
    if record_digest != EXPECTED_POSITIVE_RECORD_DIGEST:
        raise AssertionError(f"positive labeled occurrence records changed: {record_digest}")
    return tuple(active), tuple(positive_records), normals, active_digest


def evaluate(value, s, u):
    return sum(
        Fraction(coefficient) * s**s_degree * u**u_degree
        for (s_degree, u_degree), coefficient in value.items()
    )


def parent_polygon(brackets):
    vertices = EXPECTED_PARENT_VERTICES
    bottom_sample = (Fraction(1, 2), Fraction(0))
    for label, value in brackets.items():
        if global_factors.total_degree(value) <= 0:
            continue
        orientation = 1 if evaluate(value, *bottom_sample) > 0 else -1
        vertex_values = tuple(
            orientation * evaluate(value, *vertex) for vertex in vertices
        )
        expected_zero_vertices = {
            "3578": {2, 3},
            "1268": {1, 3},
        }.get(label, set())
        actual_zero_vertices = {
            index for index, entry in enumerate(vertex_values) if not entry
        }
        if actual_zero_vertices != expected_zero_vertices:
            raise AssertionError(
                f"parent bracket {label} has wrong polygon zeros: {actual_zero_vertices}"
            )
        if any(entry < 0 for entry in vertex_values) or any(
            not entry for index, entry in enumerate(vertex_values)
            if index not in expected_zero_vertices
        ):
            raise AssertionError(f"parent bracket {label} cuts the claimed polygon")

    u0 = vertices[1][1]
    u1 = vertices[3][1]
    if not (u0 > 0 and u1 > 0):
        raise AssertionError("parent top height is not strictly positive")
    return u0, u1


def substitute_top(value, u0, u1):
    """Substitute u=v*(u0+(u1-u0)*s)."""

    delta = u1 - u0
    answer = {}
    for (s_degree, u_degree), coefficient in value.items():
        for added_s_degree in range(u_degree + 1):
            monomial = (s_degree + added_s_degree, u_degree)
            answer[monomial] = answer.get(monomial, Fraction(0)) + (
                Fraction(coefficient)
                * comb(u_degree, added_s_degree)
                * u0 ** (u_degree - added_s_degree)
                * delta**added_s_degree
            )
    return {monomial: coefficient for monomial, coefficient in answer.items() if coefficient}


def bernstein_coefficients(value):
    max_s = max(s_degree for s_degree, _ in value)
    max_v = max(v_degree for _, v_degree in value)
    answer = {}
    for i in range(max_s + 1):
        for j in range(max_v + 1):
            coefficient = Fraction(0)
            for (s_degree, v_degree), value_coefficient in value.items():
                if s_degree <= i and v_degree <= j:
                    coefficient += (
                        value_coefficient
                        * Fraction(comb(i, s_degree), comb(max_s, s_degree))
                        * Fraction(comb(j, v_degree), comb(max_v, v_degree))
                    )
            answer[i, j] = coefficient
    return max_s, max_v, answer


def frontier_certificate(active, restrictions, u0, u1):
    active_records = tuple((factor, restrictions[factor]) for factor in active)
    degrees = dict(
        sorted(
            Counter(global_factors.total_degree(value) for _, value in active_records).items()
        )
    )
    if degrees != EXPECTED_ACTIVE_DEGREES:
        raise AssertionError(f"active-factor degrees changed: {degrees}")
    distinct = len({tuple(sorted(value.items())) for _, value in active_records})
    if distinct != EXPECTED_ACTIVE_DISTINCT_RESTRICTIONS:
        raise AssertionError(f"active restricted-factor count changed: {distinct}")

    histogram = Counter()
    boundary_zeros = {}
    for factor, value in active_records:
        square_value = substitute_top(value, u0, u1)
        max_s, max_v, coefficients = bernstein_coefficients(square_value)
        signs = tuple(sorted({(entry > 0) - (entry < 0) for entry in coefficients.values()}))
        histogram[(global_factors.total_degree(value), max_s, max_v, signs)] += 1
        if factor == SPECIAL_TRIPLE_FACTOR:
            if square_value != {(1, 0): Fraction(1)}:
                raise AssertionError("the unique triple factor is no longer exactly s")
            if {
                index for index, entry in coefficients.items() if not entry
            } != {(0, 0)} or any(
                entry <= 0 for index, entry in coefficients.items() if index != (0, 0)
            ):
                raise AssertionError("the factor-s Bernstein boundary changed")
            boundary_zeros[factor] = "left-side"
        elif factor in EXPECTED_PARENT_CORNER_FACTORS:
            zero_indices = {
                index for index, entry in coefficients.items() if not entry
            }
            if zero_indices != {(max_s, max_v)} or signs not in ((-1, 0), (0, 1)):
                raise AssertionError(
                    f"active factor {factor} lost its unique parent-corner zero"
                )
            # At a non-corner square point at least one of the strictly signed
            # Bernstein basis terms is positive.  Hence this single zero
            # coefficient gives a zero only at (s,v)=(1,1), the intersection
            # of the two parent-infinity facets.
            boundary_zeros[factor] = "parent-top-right-corner"
        elif signs not in ((-1,), (1,)):
            raise AssertionError(
                f"active factor {factor} is not Bernstein sign-definite: {signs}"
            )

    if dict(sorted(histogram.items())) != EXPECTED_BERNSTEIN_HISTOGRAM:
        raise AssertionError(f"Bernstein sign histogram changed: {dict(histogram)}")
    expected_boundary_zeros = {
        SPECIAL_TRIPLE_FACTOR: "left-side",
        **{
            factor: "parent-top-right-corner"
            for factor in EXPECTED_PARENT_CORNER_FACTORS
        },
    }
    if boundary_zeros != expected_boundary_zeros:
        raise AssertionError(f"active boundary-zero census changed: {boundary_zeros}")
    return active_records, dict(sorted(histogram.items())), boundary_zeros


def boundary_status(endpoint, u0):
    bottom = receiver.integer_parent(receiver.branch_parent(0, endpoint / 2))
    bottom_normals = topes.derived_rows(bottom, normalize=False)
    bottom_status = tuple(
        refinement.classify(bottom_normals, signature)[0]
        for signature in receiver.RECEIVER_SIGNATURES
    )
    if bottom_status != (True, False, True):
        raise AssertionError(f"bottom strip status changed: {bottom_status}")

    # At s=0 use half the exact 1268 parent height.  In matrix coordinates
    # this is the node parent with column 8 sheared toward column 3.
    left_parent = receiver.branch_parent(0, Fraction(0))
    for row in range(4):
        left_parent[row][7] += (u0 / 2) * left_parent[row][2]
    left_integer = receiver.integer_parent(left_parent)
    left_normals = topes.derived_rows(left_integer, normalize=False)
    left_status = tuple(
        refinement.classify(left_normals, signature)[0]
        for signature in receiver.RECEIVER_SIGNATURES
    )
    if left_status != (True, True, True):
        raise AssertionError(f"left relative side is not triple-bad: {left_status}")

    node = receiver.integer_parent(receiver.branch_parent(0, Fraction(0)))
    node_normals = topes.derived_rows(node, normalize=False)
    bad, certificate = refinement.classify(
        node_normals, receiver.RECEIVER_SIGNATURES[1]
    )
    if not bad or certificate[0] != "circuit":
        raise AssertionError("node block 1 lost its exact positive circuit")
    support = tuple(certificate[1][0])
    directions = {
        direction[:3]
        for direction in moving.compatible_shears(
            (receiver.RECEIVER_SIGNATURES[1],), (support,)
        )
    }
    if PAIR_ROOT not in directions:
        raise AssertionError("8->3,+ no longer transports block 1 on the left side")
    return bottom_status, left_status, support


def semantic_digest(endpoint, scale, brackets, positive_records, active_records, histogram):
    digest = sha256()
    digest.update(FORMAT.encode("ascii") + b"\0")
    payload = (
        endpoint,
        scale,
        tuple((label, tuple(sorted(value.items()))) for label, value in sorted(brackets.items())),
        positive_records,
        tuple((factor, tuple(sorted(value.items()))) for factor, value in active_records),
        tuple(sorted(histogram.items())),
    )
    digest.update(repr(payload).encode("ascii"))
    return digest.hexdigest()


def audit(verbose=True):
    endpoint, scale, matrix = family_matrix()
    transverse, injective_minor = embedding_audit(matrix)
    brackets = parent_brackets(matrix)
    normals = derived_normals(matrix)
    factor_data = refinement.factor_data()
    restrictions = restriction_polynomials(normals, brackets, factor_data)
    u0, u1 = parent_polygon(brackets)
    active, positive_records, _midpoint_normals, active_digest = active_factor_scan(
        endpoint, factor_data, u0, u1
    )
    active_records, histogram, boundary_zeros = frontier_certificate(
        active, restrictions, u0, u1
    )
    bottom_status, left_status, node_support = boundary_status(endpoint, u0)
    semantic = semantic_digest(
        endpoint, scale, brackets, positive_records, active_records, histogram
    )
    if EXPECTED_SEMANTIC_DIGEST is not None and semantic != EXPECTED_SEMANTIC_DIGEST:
        raise AssertionError(f"tangential-frontier semantic digest changed: {semantic}")

    result = {
        "semantic": semantic,
        "all_degrees": EXPECTED_ALL_FACTOR_DEGREES,
        "distinct_restrictions": EXPECTED_DISTINCT_RESTRICTIONS,
        "active_factors": len(active),
        "active_factor_digest": active_digest,
        "active_occurrences": len(positive_records),
        "active_degrees": EXPECTED_ACTIVE_DEGREES,
        "active_distinct": EXPECTED_ACTIVE_DISTINCT_RESTRICTIONS,
        "special_factor": SPECIAL_TRIPLE_FACTOR,
        "vertices": EXPECTED_PARENT_VERTICES,
        "bottom_status": bottom_status,
        "left_status": left_status,
        "node_support": node_support,
        "boundary_zeros": boundary_zeros,
        "transverse": transverse,
        "injective_minor": injective_minor,
    }
    if verbose:
        print("PASS exact q0 x (8->3,+) parent quadrilateral facets s=0/u=0/3578/1268")
        print(
            "PASS embedded affine strip: independent parameter directions; transverse determinant",
            transverse,
        )
        print(
            "PASS all 26,740 bivariate factor degrees",
            EXPECTED_ALL_FACTOR_DEGREES,
            "distinct", EXPECTED_DISTINCT_RESTRICTIONS,
        )
        print(
            "PASS block-1 active factors/occurrences",
            len(active), len(positive_records),
            "degrees", EXPECTED_ACTIVE_DEGREES,
        )
        print(
            "PASS exact Bernstein frontier: factor",
            SPECIAL_TRIPLE_FACTOR,
            "= s on the left; six further zeros only at the parent top-right corner",
        )
        print("PASS status BFB on bottom and BBB on the complete left relative side")
        print("SEMANTIC_SHA256", semantic)
        print("THEOREM actual row-2599 tangential strip is the proper relative product quadrilateral")
        print("SCOPE one exact E02 end; no global pair atlas or diagonal-three claim")
    return result


def main():
    audit(verbose=True)


if __name__ == "__main__":
    main()
