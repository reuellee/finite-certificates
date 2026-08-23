#!/usr/bin/env python3
"""Exact sparse-polynomial and tensor-Bernstein certificate primitives.

Polynomials are dictionaries from exponent tuples to rational coefficients.
All decisions are fail-closed: a subdivision budget returns ``UNRESOLVED`` or
``False`` rather than guessing from floating-point data.
"""

from __future__ import annotations

from collections import defaultdict
from fractions import Fraction
from hashlib import sha256
from itertools import product
from math import comb, factorial, gcd, lcm


def clean(polynomial):
    """Remove zero coefficients without changing the coefficient domain."""

    return {monomial: value for monomial, value in polynomial.items() if value}


def multiply(left, right):
    """Multiply sparse polynomials of the same dimension exactly."""

    answer = {}
    for first_index, first in left.items():
        for second_index, second in right.items():
            if len(first_index) != len(second_index):
                raise ValueError("polynomial dimensions differ")
            index = tuple(a + b for a, b in zip(first_index, second_index))
            answer[index] = answer.get(index, Fraction(0)) + first * second
    return clean(answer)


def affine_pullback(polynomial, constants, linear_coefficients):
    """Pull back a sparse polynomial through an exact affine map.

    ``constants[j]`` and ``linear_coefficients[j]`` specify the affine form
    replacing source variable ``j``.  Every coefficient row has the target
    dimension.  This supports boxes, segments, block-hybrid cubes, and other
    affine parameterizations without problem-specific algebra.
    """

    constants = tuple(Fraction(value) for value in constants)
    rows = tuple(tuple(Fraction(value) for value in row) for row in linear_coefficients)
    if len(constants) != len(rows):
        raise ValueError("one affine form is required for each source variable")
    if not rows:
        raise ValueError("the affine map must have at least one source variable")
    target_dimension = len(rows[0])
    if not target_dimension or any(len(row) != target_dimension for row in rows):
        raise ValueError("affine coefficient rows must have one common positive dimension")

    zero = (0,) * target_dimension
    answer = {}
    for exponent, coefficient in polynomial.items():
        if len(exponent) != len(constants):
            raise ValueError("source exponent and affine-map dimensions differ")
        term = {zero: Fraction(coefficient)}
        for source_axis, power in enumerate(exponent):
            if not power:
                continue
            linear = {zero: constants[source_axis]}
            for target_axis, value in enumerate(rows[source_axis]):
                if value:
                    index = [0] * target_dimension
                    index[target_axis] = 1
                    linear[tuple(index)] = value
            for _ in range(power):
                term = multiply(term, linear)
        for monomial, value in term.items():
            answer[monomial] = answer.get(monomial, Fraction(0)) + value
    return clean(answer)


def evaluate(polynomial, values):
    """Evaluate a sparse polynomial exactly."""

    values = tuple(Fraction(value) for value in values)
    answer = Fraction(0)
    for exponent, coefficient in polynomial.items():
        if len(exponent) != len(values):
            raise ValueError("evaluation point has the wrong dimension")
        term = Fraction(coefficient)
        for coordinate, power in zip(values, exponent):
            term *= coordinate**power
        answer += term
    return answer


def canonical_integer(polynomial):
    """Return a primitive, sign-normalized integer representation."""

    polynomial = clean(polynomial)
    if not polynomial:
        return ()
    denominator = 1
    for value in polynomial.values():
        denominator = lcm(denominator, Fraction(value).denominator)
    integer = {
        monomial: int(Fraction(value) * denominator)
        for monomial, value in polynomial.items()
    }
    divisor = 0
    for value in integer.values():
        divisor = gcd(divisor, abs(value))
    divisor = max(divisor, 1)
    integer = {monomial: value // divisor for monomial, value in integer.items()}
    if integer[max(integer)] < 0:
        integer = {monomial: -value for monomial, value in integer.items()}
    return tuple(sorted(integer.items()))


def derivative(polynomial, axis):
    """Differentiate a sparse polynomial in one coordinate."""

    answer = {}
    for index, coefficient in polynomial.items():
        if not 0 <= axis < len(index):
            raise ValueError("derivative axis is out of range")
        if index[axis]:
            target = list(index)
            target[axis] -= 1
            answer[tuple(target)] = coefficient * index[axis]
    return clean(answer)


def bernstein_control(polynomial):
    """Convert power-basis coefficients on the unit box to Bernstein control values."""

    polynomial = clean(polynomial)
    if not polynomial:
        raise ValueError("the zero polynomial has no sign certificate")
    dimension = len(next(iter(polynomial)))
    if not dimension or any(len(index) != dimension for index in polynomial):
        raise ValueError("polynomial exponent tuples must have one common positive dimension")
    degrees = tuple(max(index[axis] for index in polynomial) for axis in range(dimension))
    control = {}
    for target_index in product(*(range(degree + 1) for degree in degrees)):
        value = Fraction(0)
        for source_index, coefficient in polynomial.items():
            if all(source_index[axis] <= target_index[axis] for axis in range(dimension)):
                weight = Fraction(1)
                for axis in range(dimension):
                    weight *= Fraction(
                        comb(target_index[axis], source_index[axis]),
                        comb(degrees[axis], source_index[axis]),
                    )
                value += coefficient * weight
        control[target_index] = value
    return control, tuple(degree + 1 for degree in degrees)


def _weak_compositions(total, length):
    if length == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for tail in _weak_compositions(total - first, length - 1):
            yield (first,) + tail


def simplex_bernstein_control(polynomial, degree=None):
    """Convert a power-basis polynomial to Bernstein controls on a simplex.

    The domain is ``t_j >= 0`` and ``sum(t_j) <= 1``.  Controls are indexed
    by ``(alpha_0,...,alpha_d)`` with total ``degree``; ``alpha_0`` belongs to
    the slack barycentric coordinate.  The conversion is exact and works in
    arbitrary positive dimension.
    """

    polynomial = clean(polynomial)
    if not polynomial:
        raise ValueError("the zero polynomial has no sign certificate")
    dimension = len(next(iter(polynomial)))
    if not dimension or any(len(index) != dimension for index in polynomial):
        raise ValueError("polynomial exponent tuples must have one common positive dimension")
    minimum_degree = max(map(sum, polynomial))
    degree = minimum_degree if degree is None else int(degree)
    if degree < minimum_degree:
        raise ValueError("simplex Bernstein degree is below polynomial total degree")

    homogeneous = defaultdict(Fraction)
    for exponent, coefficient in polynomial.items():
        deficit = degree - sum(exponent)
        for addition in _weak_compositions(deficit, dimension + 1):
            alpha = (addition[0],) + tuple(
                exponent[axis] + addition[axis + 1]
                for axis in range(dimension)
            )
            multinomial = factorial(deficit)
            for value in addition:
                multinomial //= factorial(value)
            homogeneous[alpha] += Fraction(coefficient) * multinomial

    controls = {}
    for alpha in _weak_compositions(degree, dimension + 1):
        multinomial = factorial(degree)
        for value in alpha:
            multinomial //= factorial(value)
        controls[alpha] = homogeneous[alpha] / multinomial
    return controls, degree


def _longest_simplex_edge(vertices):
    best = None
    for left in range(len(vertices)):
        for right in range(left + 1, len(vertices)):
            squared = sum(
                (vertices[left][axis] - vertices[right][axis]) ** 2
                for axis in range(len(vertices[left]))
            )
            candidate = (squared, -left, -right)
            if best is None or candidate > best[0]:
                best = candidate, left, right
    return best[1], best[2]


def classify_simplex_zero_set(polynomial, vertices, max_depth=8):
    """Certify zero-set emptiness/nonemptiness on a rational simplex.

    Ambiguous simplices are bisected along their deterministic longest edge.
    A one-signed Bernstein hull proves emptiness; opposite or zero vertex
    values prove nonemptiness by continuity.  Exhausting ``max_depth`` returns
    ``UNRESOLVED`` rather than inferring a result numerically.
    """

    polynomial = clean(polynomial)
    if not polynomial:
        return "IDENTICALLY_ZERO", 0, 1
    source_dimension = len(next(iter(polynomial)))
    vertices = tuple(tuple(Fraction(value) for value in vertex) for vertex in vertices)
    if len(vertices) != source_dimension + 1:
        raise ValueError("a full simplex needs dimension + 1 vertices")
    if any(len(vertex) != source_dimension for vertex in vertices):
        raise ValueError("simplex vertices have the wrong dimension")

    stack = [(vertices, 0)]
    deepest = 0
    visited = 0
    while stack:
        current, depth = stack.pop()
        visited += 1
        values = tuple(evaluate(polynomial, vertex) for vertex in current)
        vertex_signs = sign_set(values)
        if 0 in vertex_signs or {-1, 1} <= vertex_signs:
            return "NONEMPTY_VERTEX", depth, visited

        base = current[0]
        rows = tuple(
            tuple(current[target + 1][axis] - base[axis] for target in range(source_dimension))
            for axis in range(source_dimension)
        )
        pulled = affine_pullback(polynomial, base, rows)
        controls, _degree = simplex_bernstein_control(pulled)
        control_signs = sign_set(controls.values())
        if 0 not in control_signs and len(control_signs) == 1:
            continue
        deepest = max(deepest, depth)
        if depth >= max_depth:
            return "UNRESOLVED", deepest, visited
        left, right = _longest_simplex_edge(current)
        midpoint = tuple(
            (current[left][axis] + current[right][axis]) / 2
            for axis in range(source_dimension)
        )
        first = list(current)
        second = list(current)
        first[left] = midpoint
        second[right] = midpoint
        stack.append((tuple(first), depth + 1))
        stack.append((tuple(second), depth + 1))
    return "EMPTY_BERNSTEIN", deepest, visited


def _split_curve(values):
    rows = [list(values)]
    while len(rows[-1]) > 1:
        rows.append(
            [(left + right) / 2 for left, right in zip(rows[-1], rows[-1][1:])]
        )
    return (
        tuple(row[0] for row in rows),
        tuple(row[-1] for row in reversed(rows)),
    )


def split_axis(control, shape, axis):
    """Apply exact de Casteljau subdivision at 1/2 along one tensor axis."""

    if not 0 <= axis < len(shape):
        raise ValueError("split axis is out of range")
    groups = defaultdict(dict)
    for index, value in control.items():
        fixed = index[:axis] + index[axis + 1 :]
        groups[fixed][index[axis]] = value
    left = {}
    right = {}
    for fixed, row in groups.items():
        values = tuple(row[position] for position in range(shape[axis]))
        first, second = _split_curve(values)
        for position, value in enumerate(first):
            index = fixed[:axis] + (position,) + fixed[axis:]
            left[index] = value
        for position, value in enumerate(second):
            index = fixed[:axis] + (position,) + fixed[axis:]
            right[index] = value
    return left, right


def bernstein_children(control, shape):
    """Subdivide once at the midpoint of every tensor axis."""

    pieces = [control]
    for axis in range(len(shape)):
        pieces = [half for piece in pieces for half in split_axis(piece, shape, axis)]
    return tuple(pieces)


def sign_set(values):
    return {1 if value > 0 else -1 if value < 0 else 0 for value in values}


def classify_zero_set(control, shape, max_depth=8):
    """Certify empty or corner-witnessed nonempty zero set on a unit box.

    ``NONEMPTY_CORNER`` follows from continuity on a subbox edge/diagonal
    between corner values of opposite signs (or a zero corner).
    ``EMPTY_BERNSTEIN`` follows when every live subbox has strictly one-signed
    Bernstein control values.  Anything beyond the budget is ``UNRESOLVED``.
    """

    stack = [(control, 0)]
    maximum_depth = 0
    visited = 0
    vertices = tuple(
        product(*((0, length - 1) if length > 1 else (0,) for length in shape))
    )
    while stack:
        current, depth = stack.pop()
        visited += 1
        control_signs = sign_set(current.values())
        if 0 not in control_signs and len(control_signs) == 1:
            continue
        corner_signs = sign_set(current[index] for index in vertices)
        if 0 in corner_signs or {-1, 1} <= corner_signs:
            return "NONEMPTY_CORNER", depth, visited
        maximum_depth = max(maximum_depth, depth)
        if depth >= max_depth:
            return "UNRESOLVED", maximum_depth, visited
        stack.extend((child, depth + 1) for child in bernstein_children(current, shape))
    return "EMPTY_BERNSTEIN", maximum_depth, visited


def exclude_system(polynomials, max_depth=5):
    """Prove that polynomial equations have no common zero on a unit box.

    Returns ``(proved_empty, deepest_subdivision, boxes_visited)``.  A false
    result is deliberately only ``UNRESOLVED``; it is not a nonemptiness claim.
    """

    polynomials = tuple(polynomials)
    if not polynomials:
        raise ValueError("an equation system may not be empty")
    if any(not clean(polynomial) for polynomial in polynomials):
        return False, 0, 1
    initial = tuple(bernstein_control(polynomial) for polynomial in polynomials)
    dimension = len(initial[0][1])
    if any(len(shape) != dimension for _control, shape in initial):
        raise ValueError("equations have different dimensions")
    stack = [(initial, 0)]
    deepest = 0
    visited = 0
    while stack:
        system, depth = stack.pop()
        visited += 1
        if any(
            0 not in sign_set(control.values())
            and len(sign_set(control.values())) == 1
            for control, _shape in system
        ):
            continue
        deepest = max(deepest, depth)
        if depth >= max_depth:
            return False, deepest, visited
        children = [bernstein_children(control, shape) for control, shape in system]
        for child_index in range(2**dimension):
            stack.append(
                (
                    tuple(
                        (family[child_index], system[equation][1])
                        for equation, family in enumerate(children)
                    ),
                    depth + 1,
                )
            )
    return True, deepest, visited


def adaptive_critical_exclusion(polynomial, axis_sets, max_depth=5):
    """Try derivative-axis systems until one excludes interior compact components."""

    attempts = []
    total_visited = 0
    for axes in axis_sets:
        axes = tuple(axes)
        system = (polynomial, *(derivative(polynomial, axis) for axis in axes))
        empty, depth, visited = exclude_system(system, max_depth=max_depth)
        total_visited += visited
        attempts.append(
            {
                "axes": axes,
                "proved_empty": empty,
                "depth": depth,
                "visited": visited,
            }
        )
        if empty:
            return {
                "proved_empty": True,
                "selected_axes": axes,
                "selected_depth": depth,
                "total_visited": total_visited,
                "attempts": tuple(attempts),
            }
    return {
        "proved_empty": False,
        "selected_axes": None,
        "selected_depth": None,
        "total_visited": total_visited,
        "attempts": tuple(attempts),
    }


def id_digest(domain, identifiers):
    """Hash an ordered list of nonnegative 32-bit identifiers with domain separation."""

    digest = sha256(domain + b"\0")
    for identifier in identifiers:
        digest.update(int(identifier).to_bytes(4, "little"))
    return digest.hexdigest()
