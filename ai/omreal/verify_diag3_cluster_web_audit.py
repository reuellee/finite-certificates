#!/usr/bin/env python3
"""Dependency-free exact cluster-web audit for the hard diagonal-3 cores.

The three full homogeneous four-normal occurrence determinants of support
types 49, 50, and 51 are compared with the three quadratic and fourteen
cubic Gr(4,8) cluster-variable representatives printed in Tables 3--4 of

  Zhang--Tang--Zhao, Web Diagrams of Cluster Variables for Grassmannian
  Gr(4,8), arXiv:2507.18432.

For negative tests we deliberately enlarge the published dihedral orbits to
all S_8 relabelings.  Failure in this larger set is therefore decisive.  The
positive type-51 identity, and all three displayed homogeneous occurrence
formulas, are replayed by direct determinant expansion on a fully generic
4-by-8 matrix.  No floating point or external package is used.
"""

from itertools import combinations, permutations
from math import gcd
import hashlib


def clean(polynomial):
    return {monomial: value for monomial, value in polynomial.items() if value}


def add(*polynomials):
    answer = {}
    for polynomial in polynomials:
        for monomial, value in polynomial.items():
            answer[monomial] = answer.get(monomial, 0) + value
            if not answer[monomial]:
                del answer[monomial]
    return answer


def negative(polynomial):
    return {monomial: -value for monomial, value in polynomial.items()}


def scale(polynomial, value):
    return clean({monomial: value * coefficient for monomial, coefficient in polynomial.items()})


def multiply(left, right):
    if not left or not right:
        return {}
    answer = {}
    for first, first_value in left.items():
        for second, second_value in right.items():
            monomial = tuple(a + b for a, b in zip(first, second))
            answer[monomial] = answer.get(monomial, 0) + first_value * second_value
            if not answer[monomial]:
                del answer[monomial]
    return answer


def product(*polynomials):
    if not polynomials:
        raise ValueError("the number of variables is needed for an empty product")
    answer = polynomials[0]
    for polynomial in polynomials[1:]:
        answer = multiply(answer, polynomial)
    return answer


def constant(number_variables, value):
    return {(0,) * number_variables: value} if value else {}


def variable(number_variables, index):
    exponent = [0] * number_variables
    exponent[index] = 1
    return {tuple(exponent): 1}


def primitive(polynomial):
    if not polynomial:
        return {}
    divisor = 0
    for value in polynomial.values():
        divisor = gcd(divisor, abs(value))
    answer = {monomial: value // divisor for monomial, value in polynomial.items()}
    if answer[max(answer)] < 0:
        answer = negative(answer)
    return answer


def polynomial_key(polynomial):
    return tuple(sorted(primitive(polynomial).items()))


def determinant(matrix):
    size = len(matrix)
    if size == 1:
        return matrix[0][0]
    terms = []
    for column in range(size):
        minor = tuple(
            row[:column] + row[column + 1 :]
            for row in matrix[1:]
        )
        term = multiply(matrix[0][column], determinant(minor))
        terms.append(term if not (column & 1) else negative(term))
    return add(*terms)


def normalized_matrix():
    number_variables = 9
    one = constant(number_variables, 1)
    zero = {}
    a, b, c, d, e, f, g, h, i = (
        variable(number_variables, index) for index in range(number_variables)
    )
    return (
        (one, zero, zero, zero, one, one, one, one),
        (zero, one, zero, zero, one, a, d, g),
        (zero, zero, one, zero, one, b, e, h),
        (zero, zero, zero, one, one, c, f, i),
    )


def generic_matrix():
    return tuple(
        tuple(variable(32, 8 * row + column) for column in range(8))
        for row in range(4)
    )


def square_minor(matrix, columns):
    return determinant(
        tuple(tuple(matrix[row][column] for column in columns) for row in range(4))
    )


def bracket_table(matrix):
    return {
        columns: square_minor(matrix, columns)
        for columns in combinations(range(8), 4)
    }


def normal(matrix, triple):
    answer = []
    for omitted in range(4):
        rows = tuple(row for row in range(4) if row != omitted)
        minor = tuple(
            tuple(matrix[row][column] for column in triple)
            for row in rows
        )
        cofactor = determinant(minor)
        if (omitted + 3) & 1:
            cofactor = negative(cofactor)
        answer.append(cofactor)
    return tuple(answer)


def occurrence_determinant(matrix, support):
    normals = tuple(
        normal(matrix, tuple(int(label) - 1 for label in edge))
        for edge in support
    )
    return determinant(
        tuple(tuple(normals[column][row] for column in range(4)) for row in range(4))
    )


def inversion_sign(values):
    inversions = sum(
        values[left] > values[right]
        for left in range(len(values))
        for right in range(left + 1, len(values))
    )
    return -1 if inversions & 1 else 1


def parse_formula(text):
    text = text.replace(" ", "")
    sign = 1
    index = 0
    if text.startswith("+"):
        index = 1
    elif text.startswith("-"):
        sign = -1
        index = 1
    start = index
    chunks = []
    while index <= len(text):
        if index == len(text) or text[index] in "+-":
            chunks.append((sign, tuple(text[start:index].split("*"))))
            if index < len(text):
                sign = 1 if text[index] == "+" else -1
                start = index + 1
        index += 1
    return tuple(chunks)


def boundary(formula):
    expected = None
    for _, factors in formula:
        degree = [0] * 8
        for factor in factors:
            for label in factor:
                degree[int(label) - 1] += 1
        degree = tuple(degree)
        if expected is None:
            expected = degree
        elif degree != expected:
            raise AssertionError(f"inhomogeneous printed formula: {formula}")
    return expected


IDENTITY = tuple(range(8))


def evaluate_formula(formula, brackets, relabeling=IDENTITY):
    answer = {}
    for coefficient, factors in formula:
        term = None
        sign = coefficient
        for factor in factors:
            moved = tuple(relabeling[int(label) - 1] for label in factor)
            sign *= inversion_sign(moved)
            value = brackets[tuple(sorted(moved))]
            term = value if term is None else multiply(term, value)
        answer = add(answer, term if sign == 1 else negative(term))
    return answer


QUADRATICS = (
    parse_formula("+1235*1467-1234*1567"),
    parse_formula("+1256*1347-1234*1567"),
    parse_formula("+1234*5678-1235*4678+1236*4578"),
)


CUBICS = (
    parse_formula("+1238*1234*4567-1238*1456*2347-1248*1234*3567+1248*1356*2347"),
    parse_formula("-4567*1246*1238-4567*1234*1268+1456*1248*2367-2456*1467*1238"),
    parse_formula("+5678*1235*1234-3567*1258*1234-1256*3578*1234+1356*1257*2348-2356*1578*1234"),
    parse_formula("-4567*1246*1238-4567*1234*1268-2456*1467*1238+1458*2467*1236"),
    parse_formula("-1278*1235*3456-1378*1256*2345+2378*1256*1345"),
    parse_formula("+4567*1234*1268-4568*1234*1267-3456*1246*1278+1246*3478*1256-1246*1234*5678"),
    parse_formula("+5678*1236*1234-3567*1268*1234-1256*3678*1234+1356*1267*2348-2356*1678*1234"),
    parse_formula("-2345*1247*1678-2345*1278*1467-1234*2457*1678+2367*1245*1478"),
    parse_formula("+1234*1236*5678-1234*1567*2368-1235*1236*4678+1235*1467*2368"),
    parse_formula("-4567*1256*1238-4567*1235*1268-2456*1567*1238+1458*2567*1236"),
    parse_formula("+1234*1245*5678-1234*1256*4578-1234*1258*4567-1234*1578*2456+1257*1456*2348"),
    parse_formula("-1234*1357*5678-1234*1578*3567+1235*1567*3478-1237*1345*5678"),
    parse_formula("-1234*1245*5678-1234*1256*4578+1235*1245*4678-1236*1245*4578-1245*1245*3678+1245*1246*3578"),
    parse_formula("-2345*1357*1678-2345*1378*1567+2357*1367*1458-1235*3457*1678"),
)


SUPPORTS = {
    49: ("123", "145", "246", "357"),
    50: ("123", "145", "246", "378"),
    51: ("123", "145", "267", "468"),
}


OCCURRENCE_FORMULAS = {
    49: parse_formula("+2346*1245*1357-1345*1246*2357"),
    50: parse_formula("+2346*1245*1378-1345*1246*2378"),
    51: parse_formula("-1245*1236*4678-1345*1267*2468+1245*1367*2468"),
}


TYPE51_CLUSTER_RELABELING = (5, 1, 2, 0, 4, 3, 7, 6)


def support_boundary(support):
    answer = [0] * 8
    for edge in support:
        for label in edge:
            answer[int(label) - 1] += 1
    return tuple(answer)


def permute_boundary(degree, relabeling):
    answer = [0] * 8
    for old, new in enumerate(relabeling):
        answer[new] = degree[old]
    return tuple(answer)


def matching_relabelings(source, target):
    source_groups = {}
    target_groups = {}
    for index, value in enumerate(source):
        source_groups.setdefault(value, []).append(index)
    for index, value in enumerate(target):
        target_groups.setdefault(value, []).append(index)
    if {value: len(group) for value, group in source_groups.items()} != {
        value: len(group) for value, group in target_groups.items()
    }:
        return
    values = tuple(sorted(source_groups))

    def recurse(depth, relabeling):
        if depth == len(values):
            yield tuple(relabeling)
            return
        value = values[depth]
        for targets in permutations(target_groups[value]):
            candidate = list(relabeling)
            for old, new in zip(source_groups[value], targets):
                candidate[old] = new
            yield from recurse(depth + 1, candidate)

    yield from recurse(0, [-1] * 8)


def cubic_matches(target, degree, brackets):
    tested = 0
    hits = []
    target_key = polynomial_key(target)
    for formula_index, formula in enumerate(CUBICS):
        for relabeling in matching_relabelings(boundary(formula), degree):
            tested += 1
            if polynomial_key(evaluate_formula(formula, brackets, relabeling)) == target_key:
                hits.append((formula_index, relabeling))
    return tested, tuple(hits)


def unit_quadratic_matches(target, degree, brackets):
    tested = 0
    hits = []
    target_key = polynomial_key(target)
    for formula_index, formula in enumerate(QUADRATICS):
        source_degree = boundary(formula)
        for relabeling in permutations(range(8)):
            moved_degree = permute_boundary(source_degree, relabeling)
            difference = tuple(a - b for a, b in zip(degree, moved_degree))
            if sorted(difference) != [0, 0, 0, 0, 1, 1, 1, 1]:
                continue
            unit = tuple(index for index, value in enumerate(difference) if value)
            tested += 1
            candidate = multiply(
                evaluate_formula(formula, brackets, relabeling),
                brackets[unit],
            )
            if polynomial_key(candidate) == target_key:
                hits.append((formula_index, relabeling, unit))
    return tested, tuple(hits)


def dihedral_relabelings():
    for shift in range(8):
        yield tuple((label + shift) % 8 for label in range(8))
        yield tuple((shift - label) % 8 for label in range(8))


def verify_generic_occurrence_identities():
    matrix = generic_matrix()
    brackets = bracket_table(matrix)
    for kind, support in SUPPORTS.items():
        raw = occurrence_determinant(matrix, support)
        displayed = evaluate_formula(OCCURRENCE_FORMULAS[kind], brackets)
        if polynomial_key(raw) != polynomial_key(displayed):
            raise AssertionError(f"generic occurrence formula failed for type {kind}")

    raw51 = occurrence_determinant(matrix, SUPPORTS[51])
    cluster51 = evaluate_formula(
        CUBICS[1], brackets, TYPE51_CLUSTER_RELABELING
    )
    if polynomial_key(raw51) != polynomial_key(cluster51):
        raise AssertionError("type-51 generic cluster identity failed")


def main():
    if tuple(map(boundary, QUADRATICS)) != (
        (2, 1, 1, 1, 1, 1, 1, 0),
        (2, 1, 1, 1, 1, 1, 1, 0),
        (1, 1, 1, 1, 1, 1, 1, 1),
    ):
        raise AssertionError("quadratic source formulas changed")
    if len(CUBICS) != 14 or any(sorted(boundary(formula)) != [1, 1, 1, 1, 2, 2, 2, 2] for formula in CUBICS):
        raise AssertionError("cubic source formulas changed")

    normalized = normalized_matrix()
    brackets = bracket_table(normalized)
    expected = {
        49: (0, 7_200, 0, 0),
        50: (8_064, 63_360, 0, 0),
        51: (8_064, 63_360, 72, 0),
    }
    records = []
    for kind, support in SUPPORTS.items():
        raw = occurrence_determinant(normalized, support)
        displayed = evaluate_formula(OCCURRENCE_FORMULAS[kind], brackets)
        if polynomial_key(raw) != polynomial_key(displayed):
            raise AssertionError(f"normalized occurrence formula failed for type {kind}")
        degree = support_boundary(support)
        cubic_tested, cubic_hits = cubic_matches(raw, degree, brackets)
        quadratic_tested, quadratic_hits = unit_quadratic_matches(raw, degree, brackets)
        direct_hits = sum(
            polynomial_key(evaluate_formula(formula, brackets, relabeling))
            == polynomial_key(raw)
            for formula in CUBICS
            for relabeling in dihedral_relabelings()
        )
        observed = (
            cubic_tested,
            quadratic_tested,
            len(cubic_hits),
            len(quadratic_hits),
        )
        if observed != expected[kind] or direct_hits:
            raise AssertionError(
                f"type-{kind} cluster census changed: {observed}, direct={direct_hits}"
            )
        records.append((kind, degree, observed))

    verify_generic_occurrence_identities()

    semantic = hashlib.sha256(repr((records, TYPE51_CLUSTER_RELABELING)).encode()).hexdigest()
    print("PASS: exact generic 4x8 determinant expansions give F49, F50, F51")
    print("PASS: type 49 has 0 cubic candidates and 0/7200 unit-quadratic matches")
    print("PASS: type 50 has 0/8064 cubic and 0/63360 unit-quadratic matches")
    print("PASS: type 51 has 72/8064 cubic and 0/63360 unit-quadratic matches")
    print("PASS: no canonical core is a dihedral image of a printed cubic representative")
    print("PASS: generic Pluecker replay proves the non-dihedral type-51 cluster identity")
    print("TYPE51_RELABELING", tuple(value + 1 for value in TYPE51_CLUSTER_RELABELING))
    print("SEMANTIC_SHA256", semantic)
    print("NO-GO: types 49 and 50 are not cluster variables even in the arbitrary-S8 superset")


if __name__ == "__main__":
    main()
