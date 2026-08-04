#!/usr/bin/env python3
"""Exact symbolic checker for the residual-wall log-binomial reduction.

In the standard nine-variable normalization of a UOM(4,8) realization,
twelve of the thirteen residual incidence-orbit types are signed differences
of two products of parent brackets.  On a fixed parent chirotope cell, taking
absolute values and logarithms therefore turns each of those wall equations
into the pullback of an ordinary linear hyperplane.

This dependency-free checker expands every bracket and residual over ZZ in a
small polynomial dictionary.  It verifies the twelve displayed identities.
It also exhausts all products of two of the 70 parent brackets and proves that
the remaining residual q_51 is not, up to sign, a difference of two such
products in this normalization.  It then verifies the shortest next identity
found by the same exact search: q_51 is a signed sum of three bracket products.

The identities do not assert that the log-bracket image of a realization cell
is convex.  ``verify_log_plucker_nonconvex.py`` gives an exact counterexample
to that additional premise.
"""

from itertools import combinations, permutations


NVARIABLES = 9
ZERO_EXPONENT = (0,) * NVARIABLES


def clean(polynomial):
    return {monomial: value for monomial, value in polynomial.items() if value}


def constant(value):
    return {} if value == 0 else {ZERO_EXPONENT: int(value)}


def variable(index):
    exponent = [0] * NVARIABLES
    exponent[index] = 1
    return {tuple(exponent): 1}


def add(*polynomials):
    result = {}
    for polynomial in polynomials:
        for monomial, value in polynomial.items():
            result[monomial] = result.get(monomial, 0) + value
    return clean(result)


def negative(polynomial):
    return {monomial: -value for monomial, value in polynomial.items()}


def subtract(left, right):
    return add(left, negative(right))


def multiply(*factors):
    result = constant(1)
    for factor in factors:
        next_result = {}
        for first, first_value in result.items():
            for second, second_value in factor.items():
                monomial = tuple(
                    first[index] + second[index] for index in range(NVARIABLES)
                )
                next_result[monomial] = (
                    next_result.get(monomial, 0) + first_value * second_value
                )
        result = clean(next_result)
    return clean(result)


def product(*factors):
    return multiply(*factors)


def permutation_sign(permutation):
    inversions = sum(
        permutation[left] > permutation[right]
        for left in range(len(permutation))
        for right in range(left + 1, len(permutation))
    )
    return -1 if inversions & 1 else 1


def determinant(matrix):
    size = len(matrix)
    result = {}
    for permutation in permutations(range(size)):
        term = product(
            *(matrix[row][permutation[row]] for row in range(size))
        )
        result = add(result, term if permutation_sign(permutation) > 0 else negative(term))
    return result


def polynomial_key(polynomial):
    return tuple(sorted(clean(polynomial).items()))


def bracket_label(indices):
    return "".join(str(index + 1) for index in indices)


def main():
    one, zero = constant(1), constant(0)
    a, b, c, d, e, f, g, h, i = (variable(index) for index in range(9))
    matrix = (
        (one, zero, zero, zero, one, one, one, one),
        (zero, one, zero, zero, one, a, d, g),
        (zero, zero, one, zero, one, b, e, h),
        (zero, zero, zero, one, one, c, f, i),
    )
    brackets = {}
    for basis in combinations(range(8), 4):
        square = tuple(
            tuple(matrix[row][column] for column in basis) for row in range(4)
        )
        brackets[bracket_label(basis)] = determinant(square)
    assert len(brackets) == 70 and all(brackets.values())

    residual = {
        36: add(subtract(subtract(multiply(a, f), multiply(c, d)), f), c),
        37: add(
            add(
                add(subtract(multiply(a, e), multiply(a, f)), subtract(b, multiply(b, d))),
                subtract(multiply(c, d), c),
            ),
            subtract(f, e),
        ),
        38: add(
            add(
                add(
                    add(
                        add(multiply(a, e, i), negative(multiply(a, f, h))),
                        add(negative(multiply(b, d, i)), multiply(b, f, g)),
                    ),
                    add(negative(multiply(b, f)), multiply(b, i)),
                ),
                add(
                    add(multiply(c, d, h), negative(multiply(c, e, g))),
                    add(multiply(c, e), negative(multiply(c, h))),
                ),
            ),
            add(negative(multiply(e, i)), multiply(f, h)),
        ),
        39: add(
            add(
                add(subtract(multiply(a, f), multiply(a, i)), negative(multiply(c, d, i))),
                add(multiply(c, f, g), negative(multiply(c, f))),
            ),
            add(add(multiply(c, i), multiply(d, i)), negative(multiply(f, g))),
        ),
        41: add(
            add(subtract(multiply(a, e), a), subtract(c, multiply(c, d))),
            subtract(d, e),
        ),
        42: add(
            add(
                add(subtract(multiply(a, e), multiply(a, h)), negative(multiply(c, d, h))),
                add(multiply(c, e, g), negative(multiply(c, e))),
            ),
            add(add(multiply(c, h), multiply(d, h)), negative(multiply(e, g))),
        ),
        44: add(
            add(
                add(
                    add(
                        add(multiply(a, e, i), negative(multiply(a, e))),
                        add(negative(multiply(a, f, h)), multiply(a, f)),
                    ),
                    subtract(multiply(a, h), multiply(a, i)),
                ),
                add(
                    add(multiply(c, d, h), negative(multiply(c, d, i))),
                    add(negative(multiply(c, e, g)), multiply(c, e)),
                ),
            ),
            add(
                add(
                    add(multiply(c, f, g), negative(multiply(c, f))),
                    subtract(multiply(c, i), multiply(c, h)),
                ),
                add(
                    add(subtract(multiply(d, i), multiply(d, h)), subtract(multiply(e, g), multiply(e, i))),
                    subtract(multiply(f, h), multiply(f, g)),
                ),
            ),
        ),
        46: add(subtract(multiply(a, f), multiply(b, f)), subtract(multiply(c, e), multiply(c, d))),
        47: add(subtract(multiply(a, f), multiply(b, f)), subtract(multiply(c, e), multiply(c, d))),
        48: add(add(a, multiply(b, c)), negative(add(b, c))),
        49: add(add(multiply(b, f), d), negative(add(b, f))),
        50: add(add(multiply(b, f), multiply(d, i)), negative(add(multiply(b, i), multiply(f, g)))),
        51: add(
            add(
                add(
                    add(multiply(a, b, f), negative(multiply(a, c, e))),
                    subtract(multiply(a, c, h), multiply(a, f, h)),
                ),
                add(negative(multiply(b, b, f)), multiply(b, c, e)),
            ),
            add(
                add(negative(multiply(b, c, g)), multiply(b, f, h)),
                subtract(multiply(c, e, g), multiply(c, e, h)),
            ),
        ),
    }

    identities = {
        36: ("1245", "2367", "1234", "1367"),
        37: ("1234", "1567", "1245", "2567"),
        38: ("1234", "1678", "1245", "2678"),
        39: ("1234", "3678", "1236", "3578"),
        41: ("1234", "3567", "1257", "3456"),
        42: ("1356", "2478", "1478", "2356"),
        44: ("1234", "5678", "1256", "3578"),
        46: ("1245", "1367", "1234", "1267"),
        47: ("1245", "1367", "1234", "1267"),
        48: ("1234", "1356", "1246", "2356"),
        49: ("1234", "1357", "1246", "2357"),
        50: ("1246", "2378", "1234", "1378"),
    }
    assert set(identities) == set(residual) - {51}
    for kind, (first, second, third, fourth) in identities.items():
        right = subtract(
            multiply(brackets[first], brackets[second]),
            multiply(brackets[third], brackets[fourth]),
        )
        assert residual[kind] == right

    # Exhaust every difference of two bracket products, with repetitions.
    labels = tuple(brackets)
    bracket_products = {}
    for left_index, left in enumerate(labels):
        for right in labels[left_index:]:
            value = multiply(brackets[left], brackets[right])
            bracket_products.setdefault(polynomial_key(value), (left, right))
    assert len(bracket_products) <= 70 * 71 // 2

    q51 = residual[51]
    q51_negative = negative(q51)
    representations = []
    for key, first_pair in bracket_products.items():
        first_product = dict(key)
        for target in (subtract(first_product, q51), subtract(first_product, q51_negative)):
            second_pair = bracket_products.get(polynomial_key(target))
            if second_pair is not None:
                representations.append((first_pair, second_pair))
    assert not representations

    q51_trinomial = subtract(
        subtract(
            multiply(brackets["1236"], brackets["4678"]),
            multiply(brackets["1267"], brackets["2468"]),
        ),
        multiply(brackets["1367"], brackets["2468"]),
    )
    assert q51 == q51_trinomial

    print("PASS: 12/13 residual orbit types have exact bracket-binomial identities")
    print("PASS: exhaustive two-bracket-product search excludes residual type 51")
    print("PASS: q51=[1236][4678]-[1267][2468]-[1367][2468]")
    print("THEOREM: the 12 binomial walls pull back log-bracket hyperplanes")
    print("SCOPE: log-image convexity is false and must not be inferred")


if __name__ == "__main__":
    main()
