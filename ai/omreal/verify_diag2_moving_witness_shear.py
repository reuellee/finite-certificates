#!/usr/bin/env python3
"""Exact finite checks for the diagonal-two moving-witness shear lemma.

The theorem proved in DIAG2_MOVING_WITNESS_SHEAR.md is algebraic.  This
checker audits its signs and its currently known finite evidence:

* the inverse-exterior transport identity and affine parent-bracket law;
* all 65 pencil-rigid 4+5 or 5+5 occurrences in the stable row-2599
  eight-shatter certificate;
* the exact parent-16 defect-two pair, which has 22 compatible shears; and
* an arbitrary-signing canary with the same active circuit signs but no
  compatible shear.  Exact GP relations certify that the canary is not an
  abstract oriented-matroid extension.

Only integer/rational arithmetic is used.  This script imports no search or
extension-enumeration module.  It is a scoped census, not a proof of the
second diagonal.
"""

from collections import Counter
from itertools import combinations
from pathlib import Path
from time import perf_counter

import numpy as np


HERE = Path(__file__).resolve().parent
CERTIFICATE = HERE / "data" / "seeat_parent2599_shatter8.npz"
EXPECTED_FORMAT = "seeat-parent2599-shatter8-v1"


def colex_subsets(n, size):
    return tuple(
        sorted(
            combinations(range(1, n + 1), size),
            key=lambda subset: tuple(reversed(subset)),
        )
    )


TRIPLES = colex_subsets(8, 3)
TRIPLE_INDEX = {triple: index for index, triple in enumerate(TRIPLES)}
BASES4 = colex_subsets(8, 4)

PARENT16 = (
    (8, 4, -3, -6, 1, 0, 8, 1),
    (1, 8, 8, 1, 2, -5, -1, -3),
    (3, -1, 5, -2, -8, 5, -1, -8),
    (-1, -1, 0, 8, 2, 8, 4, 5),
)
LEFT_SIGNATURE = 26988370886400909
RIGHT_SIGNATURE = 45348283816043521
LEFT_SUPPORT_TEXT = "123/124/134/235/567"
RIGHT_SUPPORT_TEXT = "126/247/158/468/378"

# These agree with the actual signatures on LEFT_SUPPORT and RIGHT_SUPPORT,
# respectively, but are deliberately invalid as full extension signings.
CANARY_LEFT = 36592014375624197
CANARY_RIGHT = 512238212525449
EXPECTED_CANARY_GP_VIOLATIONS = (182, 224)

EXPECTED_ROW_DISTRIBUTION = Counter(
    {
        10: 2,
        11: 1,
        12: 1,
        13: 1,
        14: 1,
        15: 6,
        16: 5,
        17: 7,
        18: 7,
        19: 7,
        20: 2,
        21: 7,
        22: 5,
        23: 4,
        24: 1,
        25: 2,
        26: 1,
        27: 4,
        29: 1,
    }
)


def parse_support(text):
    return tuple(
        TRIPLE_INDEX[tuple(int(character) for character in label)]
        for label in text.split("/")
    )


LEFT_SUPPORT = parse_support(LEFT_SUPPORT_TEXT)
RIGHT_SUPPORT = parse_support(RIGHT_SUPPORT_TEXT)


def det3(first, second, third):
    """Determinant of three row vectors of length three."""
    return (
        first[0] * (second[1] * third[2] - second[2] * third[1])
        - first[1] * (second[0] * third[2] - second[2] * third[0])
        + first[2] * (second[0] * third[1] - second[1] * third[0])
    )


def det4(first, second, third, fourth):
    """Determinant of four row vectors of length four."""
    return (
        first[0] * det3(second[1:], third[1:], fourth[1:])
        - second[0] * det3(first[1:], third[1:], fourth[1:])
        + third[0] * det3(first[1:], second[1:], fourth[1:])
        - fourth[0] * det3(first[1:], second[1:], third[1:])
    )


def orientation_sign(sequence):
    inversions = sum(
        sequence[left] > sequence[right]
        for left in range(len(sequence))
        for right in range(left + 1, len(sequence))
    )
    return -1 if inversions & 1 else 1


def signature_sign(signature, index):
    return 1 if (signature >> index) & 1 else -1


def matrix_columns(matrix):
    return tuple(
        tuple(int(matrix[row][column]) for row in range(4))
        for column in range(8)
    )


def parent_brackets(matrix):
    columns = matrix_columns(matrix)
    return {
        basis: det4(*(columns[label - 1] for label in basis))
        for basis in BASES4
    }


def parent_normals(matrix):
    columns = matrix_columns(matrix)
    normals = []
    for triple in TRIPLES:
        selected = [columns[label - 1] for label in triple]
        normal = []
        for coordinate in range(4):
            rows = [
                tuple(value for index, value in enumerate(column) if index != coordinate)
                for column in selected
            ]
            normal.append((-1) ** (coordinate + 5) * det3(*rows))
        if not any(normal):
            raise AssertionError(f"zero derived normal on triple {triple}")
        normals.append(tuple(normal))
    return tuple(normals)


def three_vectors_independent(vectors):
    """Exact rank-three test for three vectors in four-space."""
    if len(vectors) != 3:
        raise AssertionError("rank-three minor test expects three vectors")
    return any(
        det3(
            *(tuple(vector[coordinate] for coordinate in coordinates) for vector in vectors)
        )
        for coordinates in combinations(range(4), 3)
    )


def verify_minimal_circuit_columns(columns):
    """Exact maximal-minor test for a four- or five-element circuit."""
    if len(columns) == 5:
        # Every deletion is a basis of four-space.  This simultaneously gives
        # total rank four and independence of every proper four-subset.
        if any(
            not det4(*(columns[index] for index in range(5) if index != omitted))
            for omitted in range(5)
        ):
            raise AssertionError("five-support dependence is not support-minimal")
    elif len(columns) == 4:
        # The positive relation already asserts dependence; check it again by
        # the top minor and then certify that every three-subset has rank three.
        if det4(*columns):
            raise AssertionError("four-support columns are unexpectedly independent")
        if any(
            not three_vectors_independent(
                [columns[index] for index in range(4) if index != omitted]
            )
            for omitted in range(4)
        ):
            raise AssertionError("four-support dependence is not support-minimal")
    else:
        raise AssertionError("this scoped verifier expects support size four or five")


def replacement(index, source, target):
    """Return (replacement index, wedge sorting sign), or None."""
    triple = TRIPLES[index]
    if source not in triple or target in triple:
        return None
    sequence = list(triple)
    sequence[sequence.index(source)] = target
    return TRIPLE_INDEX[tuple(sorted(sequence))], orientation_sign(sequence)


def transport_alpha(signature, index, source, target):
    result = replacement(index, source, target)
    if result is None:
        raise AssertionError("transport alpha requested on a nonsource triple")
    replacement_index, sorting_sign = result
    return (
        -sorting_sign
        * signature_sign(signature, index)
        * signature_sign(signature, replacement_index)
    )


def compatible_shears(signatures, supports):
    result = []
    for source in range(1, 9):
        for target in range(1, 9):
            if source == target:
                continue
            alphas = []
            for signature, support in zip(signatures, supports, strict=True):
                alphas.extend(
                    transport_alpha(signature, index, source, target)
                    for index in support
                    if replacement(index, source, target) is not None
                )
            if len(set(alphas)) <= 1:
                # Empty source sets allow either parameter sign.  Count the
                # ordered label shear once and choose +1 canonically.
                result.append(
                    (source, target, alphas[0] if alphas else 1, len(alphas))
                )
    return tuple(result)


def transport_coefficients(coefficients, source, target, parameter):
    """Coordinates of Lambda^3(g_parameter^-1)c in the triple basis."""
    transported = list(coefficients)
    for index, coefficient in enumerate(coefficients):
        result = replacement(index, source, target)
        if result is None or not coefficient:
            continue
        replacement_index, sorting_sign = result
        transported[replacement_index] -= parameter * sorting_sign * coefficient
    return tuple(transported)


def shear_matrix(matrix, source, target, parameter):
    result = [list(map(int, row)) for row in matrix]
    for row in range(4):
        result[row][source - 1] += parameter * result[row][target - 1]
    return tuple(tuple(row) for row in result)


def verify_transport_identity(matrix):
    """Exhaust the exterior identity on a basis, including both signs."""
    original_normals = parent_normals(matrix)
    for source in range(1, 9):
        for target in range(1, 9):
            if source == target:
                continue
            for parameter in (-1, 1):
                sheared_normals = parent_normals(
                    shear_matrix(matrix, source, target, parameter)
                )
                for index in range(len(TRIPLES)):
                    unit = [0] * len(TRIPLES)
                    unit[index] = 1
                    transported = transport_coefficients(
                        unit, source, target, parameter
                    )
                    image = tuple(
                        sum(
                            coefficient * sheared_normals[triple][coordinate]
                            for triple, coefficient in enumerate(transported)
                        )
                        for coordinate in range(4)
                    )
                    if image != original_normals[index]:
                        raise AssertionError(
                            "inverse-exterior transport identity has wrong sign"
                        )


def verify_affine_bracket_law(matrix):
    base = parent_brackets(matrix)
    if not all(base.values()):
        raise AssertionError("parent is nonuniform")
    for source in range(1, 9):
        for target in range(1, 9):
            if source == target:
                continue
            for parameter in (-2, -1, 1, 2):
                actual = parent_brackets(
                    shear_matrix(matrix, source, target, parameter)
                )
                for basis in BASES4:
                    if source not in basis or target in basis:
                        expected = base[basis]
                    else:
                        sequence = list(basis)
                        sequence[sequence.index(source)] = target
                        replacement_basis = tuple(sorted(sequence))
                        expected = (
                            base[basis]
                            + parameter
                            * orientation_sign(sequence)
                            * base[replacement_basis]
                        )
                    if actual[basis] != expected:
                        raise AssertionError("parent bracket is not the claimed affine form")


def first_boundary(base_brackets, source, target, direction):
    """Least positive root as an exact numerator/denominator pair, or None."""
    endpoint = None
    affine_data = []
    for basis in BASES4:
        constant = base_brackets[basis]
        if not constant:
            raise AssertionError("first-boundary test started at a parent wall")
        if source not in basis or target in basis:
            slope = 0
        else:
            sequence = list(basis)
            sequence[sequence.index(source)] = target
            replacement_basis = tuple(sorted(sequence))
            slope = (
                direction
                * orientation_sign(sequence)
                * base_brackets[replacement_basis]
            )
            if not slope:
                raise AssertionError("uniform parent gave a zero shear slope")
        affine_data.append((constant, slope))
        if slope and constant * slope < 0:
            candidate = (abs(constant), abs(slope))
            if endpoint is None or (
                candidate[0] * endpoint[1] < endpoint[0] * candidate[1]
            ):
                endpoint = candidate
    if endpoint is None:
        return None
    numerator, denominator = endpoint
    if not any(
        constant * denominator + slope * numerator == 0
        for constant, slope in affine_data
    ):
        raise AssertionError("reported finite endpoint is not a wall")
    if any(
        constant * (2 * denominator * constant + numerator * slope) <= 0
        for constant, slope in affine_data
    ):
        raise AssertionError("a parent sign changed before the first wall")
    return endpoint


def support(weights):
    return tuple(index for index, value in enumerate(weights) if int(value))


def pencil_rigid(first, second):
    union = set(first) | set(second)
    for label in range(1, 9):
        incident = [TRIPLES[index] for index in union if label in TRIPLES[index]]
        if len(incident) < 3:
            return False
        for partner in range(1, 9):
            if partner != label and all(partner in triple for triple in incident):
                return False
    return True


def verify_positive_circuit(normals, signature, full_weights):
    coefficients = tuple(int(value) for value in full_weights)
    if any(value < 0 for value in coefficients) or not any(coefficients):
        raise AssertionError("Gordan weight is not nonnegative and nonzero")
    current = support(coefficients)
    signed_columns = [
        tuple(signature_sign(signature, index) * value for value in normals[index])
        for index in current
    ]
    positive_weights = [coefficients[index] for index in current]
    if not all(value > 0 for value in positive_weights):
        raise AssertionError("active Gordan weight is not positive")
    if any(
        sum(
            weight * column[coordinate]
            for weight, column in zip(positive_weights, signed_columns, strict=True)
        )
        for coordinate in range(4)
    ):
        raise AssertionError("stored Gordan dependence is not exact")
    verify_minimal_circuit_columns(signed_columns)
    return current


def positive_circuit_cofactors(matrix, signature, current):
    normals = parent_normals(matrix)
    columns = [
        tuple(signature_sign(signature, index) * value for value in normals[index])
        for index in current
    ]
    if len(columns) != 5:
        raise AssertionError("parent-16 support is not a five-circuit")
    cofactors = [
        (-1 if omitted & 1 else 1)
        * det4(*(columns[index] for index in range(5) if index != omitted))
        for omitted in range(5)
    ]
    if all(value < 0 for value in cofactors):
        cofactors = [-value for value in cofactors]
    if not all(value > 0 for value in cofactors):
        raise AssertionError(f"parent-16 circuit is not positive: {cofactors}")
    verify_minimal_circuit_columns(columns)
    if any(
        sum(
            weight * column[coordinate]
            for weight, column in zip(cofactors, columns, strict=True)
        )
        for coordinate in range(4)
    ):
        raise AssertionError("parent-16 cofactors do not annihilate the circuit")
    return tuple(cofactors)


def verify_orthant_transport(signature, weights, shear):
    source, target, direction, _ = shear
    coefficients = tuple(
        signature_sign(signature, index) * int(weights[index])
        for index in range(len(TRIPLES))
    )
    transported = transport_coefficients(
        coefficients, source, target, direction
    )
    reoriented = tuple(
        signature_sign(signature, index) * value
        for index, value in enumerate(transported)
    )
    if any(value < 0 for value in reoriented) or not any(reoriented):
        raise AssertionError("compatible shear left the signed nonnegative orthant")


def extension_gp_violations(parent, signature):
    """Uniform rank-four GP sign violations for adjoining label nine."""
    parent_signs = {
        basis: 1 if value > 0 else -1
        for basis, value in parent_brackets(parent).items()
    }
    if len(parent_signs) != 70 or any(
        not value for value in parent_brackets(parent).values()
    ):
        raise AssertionError("GP checker requires a uniform parent")

    def chirotope(sequence):
        sorting_sign = orientation_sign(sequence)
        basis = tuple(sorted(sequence))
        if 9 in basis:
            triple = tuple(label for label in basis if label != 9)
            value = signature_sign(signature, TRIPLE_INDEX[triple])
        else:
            value = parent_signs[basis]
        return sorting_sign * value

    violations = []
    for lam in combinations(range(1, 10), 2):
        remaining = [label for label in range(1, 10) if label not in lam]
        for first, second, third, fourth in combinations(remaining, 4):
            terms = (
                chirotope(lam + (first, second))
                * chirotope(lam + (third, fourth)),
                -chirotope(lam + (first, third))
                * chirotope(lam + (second, fourth)),
                chirotope(lam + (first, fourth))
                * chirotope(lam + (second, third)),
            )
            if terms[0] == terms[1] == terms[2]:
                violations.append((lam, (first, second, third, fourth), terms))
    return tuple(violations)


def verify_parent16_and_canary():
    base_brackets = parent_brackets(PARENT16)
    if not all(base_brackets.values()):
        raise AssertionError("parent 16 is nonuniform")
    if extension_gp_violations(PARENT16, LEFT_SIGNATURE):
        raise AssertionError("left parent-16 signature violates GP")
    if extension_gp_violations(PARENT16, RIGHT_SIGNATURE):
        raise AssertionError("right parent-16 signature violates GP")

    left_weights = positive_circuit_cofactors(
        PARENT16, LEFT_SIGNATURE, LEFT_SUPPORT
    )
    right_weights = positive_circuit_cofactors(
        PARENT16, RIGHT_SIGNATURE, RIGHT_SUPPORT
    )
    if not pencil_rigid(LEFT_SUPPORT, RIGHT_SUPPORT):
        raise AssertionError("parent-16 support pair is not pencil-rigid")

    actual_shears = compatible_shears(
        (LEFT_SIGNATURE, RIGHT_SIGNATURE), (LEFT_SUPPORT, RIGHT_SUPPORT)
    )
    if len(actual_shears) != 22:
        raise AssertionError(
            f"expected 22 parent-16 compatible shears, got {len(actual_shears)}"
        )
    if (2, 1, -1, 2) not in actual_shears:
        raise AssertionError("known parent-16 shear 2 -> 1 has the wrong sign")

    left_full = [0] * len(TRIPLES)
    right_full = [0] * len(TRIPLES)
    for index, weight in zip(LEFT_SUPPORT, left_weights, strict=True):
        left_full[index] = weight
    for index, weight in zip(RIGHT_SUPPORT, right_weights, strict=True):
        right_full[index] = weight
    for shear in actual_shears:
        verify_orthant_transport(LEFT_SIGNATURE, left_full, shear)
        verify_orthant_transport(RIGHT_SIGNATURE, right_full, shear)
    finite_endpoints = sum(
        first_boundary(base_brackets, source, target, direction) is not None
        for source, target, direction, _ in actual_shears
    )
    if finite_endpoints != 22:
        raise AssertionError("a parent-16 compatible ray unexpectedly ends at infinity")

    if any(
        signature_sign(CANARY_LEFT, index)
        != signature_sign(LEFT_SIGNATURE, index)
        for index in LEFT_SUPPORT
    ) or any(
        signature_sign(CANARY_RIGHT, index)
        != signature_sign(RIGHT_SIGNATURE, index)
        for index in RIGHT_SUPPORT
    ):
        raise AssertionError("negative canary changed an active circuit sign")
    positive_circuit_cofactors(PARENT16, CANARY_LEFT, LEFT_SUPPORT)
    positive_circuit_cofactors(PARENT16, CANARY_RIGHT, RIGHT_SUPPORT)
    canary_shears = compatible_shears(
        (CANARY_LEFT, CANARY_RIGHT), (LEFT_SUPPORT, RIGHT_SUPPORT)
    )
    if canary_shears:
        raise AssertionError(
            "deliberately incompatible arbitrary-signing canary found a shear"
        )
    violation_counts = (
        len(extension_gp_violations(PARENT16, CANARY_LEFT)),
        len(extension_gp_violations(PARENT16, CANARY_RIGHT)),
    )
    if violation_counts != EXPECTED_CANARY_GP_VIOLATIONS:
        raise AssertionError(
            f"wrong canary GP violation counts {violation_counts}"
        )
    return len(actual_shears), finite_endpoints, violation_counts


def verify_row2599():
    certificate = np.load(CERTIFICATE, allow_pickle=False)
    if str(certificate["format"].item()) != EXPECTED_FORMAT:
        raise AssertionError("wrong row-2599 certificate format")
    if int(certificate["parent_index"].item()) != 2599:
        raise AssertionError("wrong row-2599 parent index")
    # NpzFile indexing decompresses an array on every access.  Materialize the
    # three repeatedly used certificate arrays exactly once.
    signatures = tuple(int(value) for value in certificate["signature"])
    pattern_charts = certificate["pattern_chart"]
    gordan_weights = certificate["gordan_weight"]
    if len(signatures) != 8:
        raise AssertionError("row-2599 certificate does not contain eight signatures")
    if any(
        extension_gp_violations(pattern_charts[0], signature)
        for signature in signatures
    ):
        raise AssertionError("a stored row-2599 signature violates GP")

    records = []
    checked_circuits = set()
    normal_cache = {}
    bracket_cache = {}
    finite_endpoints = 0
    infinite_endpoints = 0

    for pattern in range(256):
        bad = [bit for bit in range(8) if not ((pattern >> bit) & 1)]
        supports = {
            bit: support(gordan_weights[pattern, bit])
            for bit in bad
        }
        for position, left in enumerate(bad):
            for right in bad[position + 1 :]:
                pair = (supports[left], supports[right])
                sizes = tuple(sorted(map(len, pair)))
                if sizes not in ((4, 5), (5, 5)) or not pencil_rigid(*pair):
                    continue
                if pattern not in normal_cache:
                    normal_cache[pattern] = parent_normals(
                        pattern_charts[pattern]
                    )
                for bit in (left, right):
                    key = (pattern, bit)
                    if key in checked_circuits:
                        continue
                    current = verify_positive_circuit(
                        normal_cache[pattern],
                        signatures[bit],
                        gordan_weights[pattern, bit],
                    )
                    if current != supports[bit]:
                        raise AssertionError("support changed during circuit verification")
                    checked_circuits.add(key)

                shears = compatible_shears(
                    (signatures[left], signatures[right]), pair
                )
                if not shears:
                    raise AssertionError(
                        f"row-2599 occurrence {pattern}/{left},{right} has no shear"
                    )
                if any(source_count == 0 for *_, source_count in shears):
                    raise AssertionError("pencil-rigid occurrence had an empty source set")
                for shear in shears:
                    verify_orthant_transport(
                        signatures[left],
                        gordan_weights[pattern, left],
                        shear,
                    )
                    verify_orthant_transport(
                        signatures[right],
                        gordan_weights[pattern, right],
                        shear,
                    )
                if pattern not in bracket_cache:
                    bracket_cache[pattern] = parent_brackets(
                        pattern_charts[pattern]
                    )
                for source, target, direction, _ in shears:
                    endpoint = first_boundary(
                        bracket_cache[pattern], source, target, direction
                    )
                    if endpoint is None:
                        infinite_endpoints += 1
                    else:
                        finite_endpoints += 1
                records.append((pattern, left, right, pair, len(shears)))

    if len(records) != 65:
        raise AssertionError(
            f"expected 65 row-2599 pencil-rigid occurrences, got {len(records)}"
        )
    distinct_pairs = {
        tuple(sorted(sum(1 << index for index in current) for current in pair))
        for _, _, _, pair, _ in records
    }
    if len(distinct_pairs) != 55:
        raise AssertionError(
            f"expected 55 distinct row-2599 support pairs, got {len(distinct_pairs)}"
        )
    distribution = Counter(count for *_, count in records)
    if distribution != EXPECTED_ROW_DISTRIBUTION:
        raise AssertionError(f"wrong row-2599 shear distribution {distribution}")
    total_shears = sum(distribution.elements())
    if total_shears != 1244:
        raise AssertionError(f"expected 1244 compatible occurrence/shears, got {total_shears}")
    if finite_endpoints != 1244 or infinite_endpoints:
        raise AssertionError(
            "wrong row-2599 endpoint split "
            f"finite={finite_endpoints}, infinity={infinite_endpoints}"
        )
    return len(records), len(distinct_pairs), distribution, total_shears


def main():
    started = perf_counter()
    verify_transport_identity(PARENT16)
    verify_affine_bracket_law(PARENT16)
    parent_count, parent_finite, canary_violations = verify_parent16_and_canary()
    row_count, distinct_count, distribution, total_shears = verify_row2599()
    elapsed = perf_counter() - started

    print("PASS inverse-exterior coefficient signs and affine bracket law are exact")
    print(
        "PASS parent 16: exact positive defect-two pair has "
        f"{parent_count} compatible shears ({parent_finite} finite first walls)"
    )
    print(
        "PASS arbitrary-signing canary: 0 compatible shears; GP violations "
        f"{canary_violations[0]}/{canary_violations[1]}"
    )
    print(
        "PASS row 2599: "
        f"{row_count} occurrences, {distinct_count} distinct support pairs, "
        f"{total_shears} compatible occurrence/shears"
    )
    print(f"PASS row-2599 compatible-shear distribution = {dict(sorted(distribution.items()))}")
    print("PASS row-2599 endpoint split = finite 1244, infinity 0")
    print("THEOREM CHECK: every sign-compatible witness pair has a proper shear escape")
    print("CAVEAT: the census is finite and does not prove diagonal two")
    print(f"runtime={elapsed:.3f}s")


if __name__ == "__main__":
    main()
