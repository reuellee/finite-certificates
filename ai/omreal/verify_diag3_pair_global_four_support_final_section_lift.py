#!/usr/bin/env python3
"""Independent exact replay of the final 28 algebraic t-section lifts.

No producer code or CAS is imported.  Each pinned t section defines a real
embedding of a degree-at-most-four number field.  Exact Sturm sequences over
that ordered field verify every proposed u-root box, every common-root owner
group, all boundary/vertical degeneracies, and complete root coverage.
"""

from __future__ import annotations

from collections import Counter
from copy import deepcopy
from fractions import Fraction
import gzip
from hashlib import sha256
import json
from math import prod
from pathlib import Path


HERE = Path(__file__).resolve().parent
BASE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz"
ROOTS = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_ROOT_ISOLATION.json.gz"
OPEN = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_OPEN_SECTOR_LIFT.json"
SIMPLE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_SIMPLE_SECTION_LIFT.json"
INVISIBLE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_INVISIBLE_SECTION_LIFT.json"
MULTI = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_MULTI_SECTION_LIFT.json"
REGULAR = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_REGULAR_RESIDUAL_SECTION_LIFT.json"
CERTIFICATE = HERE / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_FINAL_SECTION_LIFT.json"
FORMAT = "diag3-pair-global-row2599-four-support-final-section-lift-v1"
PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def digest(value):
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def clean(polynomial):
    polynomial = list(polynomial)
    while polynomial and not polynomial[-1]:
        polynomial.pop()
    return polynomial


def q_derivative(polynomial):
    return clean([degree * value for degree, value in enumerate(polynomial)][1:])


def q_value(polynomial, point):
    answer = Fraction(0)
    for coefficient in reversed(polynomial):
        answer = answer * point + coefficient
    return answer


def q_divmod(dividend, divisor):
    remainder = clean(map(Fraction, dividend))
    divisor = clean(map(Fraction, divisor))
    require(divisor, "zero rational polynomial divisor")
    quotient = [Fraction(0)] * max(0, len(remainder) - len(divisor) + 1)
    while remainder and len(remainder) >= len(divisor):
        shift = len(remainder) - len(divisor)
        scale = remainder[-1] / divisor[-1]
        quotient[shift] += scale
        for index, value in enumerate(divisor):
            remainder[index + shift] -= scale * value
        remainder = clean(remainder)
    return clean(quotient), remainder


def q_sturm(polynomial):
    polynomial = clean(map(Fraction, polynomial))
    sequence = [polynomial, q_derivative(polynomial)]
    while sequence[-1]:
        _quotient, remainder = q_divmod(sequence[-2], sequence[-1])
        if not remainder:
            break
        sequence.append([-value for value in remainder])
    return tuple(sequence)


def q_variations(sequence, point):
    signs = []
    for polynomial in sequence:
        value = q_value(polynomial, point)
        if value:
            signs.append(1 if value > 0 else -1)
    return sum(left != right for left, right in zip(signs, signs[1:]))


def q_root_count(polynomial, lower, upper):
    require(lower < upper, "bad rational root interval")
    require(q_value(polynomial, lower) and q_value(polynomial, upper), "rational Sturm endpoint root")
    sequence = q_sturm(polynomial)
    return q_variations(sequence, lower) - q_variations(sequence, upper)


def mod_clean(polynomial, prime):
    polynomial = [int(value) % prime for value in polynomial]
    while polynomial and not polynomial[-1]:
        polynomial.pop()
    return polynomial


def mod_divmod(dividend, divisor, prime):
    remainder = mod_clean(dividend, prime)
    divisor = mod_clean(divisor, prime)
    require(divisor, "zero finite-field divisor")
    quotient = [0] * max(0, len(remainder) - len(divisor) + 1)
    inverse = pow(divisor[-1], prime - 2, prime)
    while remainder and len(remainder) >= len(divisor):
        shift = len(remainder) - len(divisor)
        scale = remainder[-1] * inverse % prime
        quotient[shift] = scale
        for index, value in enumerate(divisor):
            remainder[index + shift] = (remainder[index + shift] - scale * value) % prime
        remainder = mod_clean(remainder, prime)
    return mod_clean(quotient, prime), remainder


def mod_gcd(left, right, prime):
    left, right = mod_clean(left, prime), mod_clean(right, prime)
    while right:
        left, right = right, mod_divmod(left, right, prime)[1]
    if not left:
        return []
    inverse = pow(left[-1], prime - 2, prime)
    return [(value * inverse) % prime for value in left]


def mod_add(left, right, prime):
    answer = [0] * max(len(left), len(right))
    for index, value in enumerate(left):
        answer[index] = (answer[index] + value) % prime
    for index, value in enumerate(right):
        answer[index] = (answer[index] + value) % prime
    return mod_clean(answer, prime)


def mod_multiply(left, right, modulus, prime):
    product_values = [0] * max(0, len(left) + len(right) - 1)
    for i, x in enumerate(left):
        for j, y in enumerate(right):
            product_values[i + j] = (product_values[i + j] + x * y) % prime
    return mod_divmod(product_values, modulus, prime)[1]


def mod_power(base, exponent, modulus, prime):
    answer = [1]
    while exponent:
        if exponent & 1:
            answer = mod_multiply(answer, base, modulus, prime)
        base = mod_multiply(base, base, modulus, prime)
        exponent //= 2
    return answer


def prime_divisors(number):
    answer = []
    divisor = 2
    while divisor * divisor <= number:
        if number % divisor == 0:
            answer.append(divisor)
            while number % divisor == 0:
                number //= divisor
        divisor += 1
    if number > 1:
        answer.append(number)
    return answer


def irreducible_prime(polynomial):
    integers = [int(value) for value in polynomial]
    degree = len(integers) - 1
    if degree == 1:
        return 0
    for prime in PRIMES:
        if integers[-1] % prime == 0:
            continue
        modulus = mod_clean(integers, prime)
        inverse = pow(modulus[-1], prime - 2, prime)
        modulus = [(value * inverse) % prime for value in modulus]
        x = [0, 1]
        if mod_power(x, prime**degree, modulus, prime) != x:
            continue
        if all(
            mod_gcd(
                modulus,
                mod_add(mod_power(x, prime ** (degree // divisor), modulus, prime), [0, -1], prime),
                prime,
            )
            == [1]
            for divisor in prime_divisors(degree)
        ):
            return prime
    raise AssertionError("no bounded irreducibility witness")


def interval_multiply(left, right):
    products = (
        left[0] * right[0],
        left[0] * right[1],
        left[1] * right[0],
        left[1] * right[1],
    )
    return min(products), max(products)


def interval_value(polynomial, lower, upper):
    answer = (Fraction(0), Fraction(0))
    argument = (lower, upper)
    for coefficient in reversed(polynomial):
        answer = interval_multiply(answer, argument)
        answer = answer[0] + coefficient, answer[1] + coefficient
    return answer


class NumberField:
    def __init__(self, polynomial, lower, upper):
        polynomial = clean(map(Fraction, polynomial))
        require(len(polynomial) >= 2, "constant number-field modulus")
        self.source_polynomial = tuple(polynomial)
        self.degree = len(polynomial) - 1
        leading = polynomial[-1]
        self.modulus = tuple(value / leading for value in polynomial)
        self.lower = Fraction(lower)
        self.upper = Fraction(upper)
        self.irreducibility_prime = irreducible_prime(polynomial)
        if self.lower == self.upper:
            require(self.degree == 1 and q_value(polynomial, self.lower) == 0, "bad rational field embedding")
        else:
            require(q_root_count(polynomial, self.lower, self.upper) == 1, "t interval does not select one root")

    def element(self, coefficients=0):
        return NumberFieldElement(self, coefficients)

    def generator(self):
        return self.element([0, 1])

    def refine(self):
        require(self.lower < self.upper, "cannot refine rational field embedding")
        middle = (self.lower + self.upper) / 2
        value = q_value(self.source_polynomial, middle)
        if value == 0:
            raise AssertionError("irreducible non-linear modulus acquired a rational root")
        left_count = q_root_count(self.source_polynomial, self.lower, middle)
        if left_count == 1:
            self.upper = middle
        else:
            require(left_count == 0, "t refinement found multiple roots")
            self.lower = middle

    def sign(self, element):
        element = self.element(element)
        if not element:
            return 0
        if self.lower == self.upper:
            value = q_value(element.coefficients, self.lower)
            require(value, "nonzero field element vanished at rational embedding")
            return 1 if value > 0 else -1
        for _round in range(640):
            lower, upper = interval_value(element.coefficients, self.lower, self.upper)
            if lower > 0:
                return 1
            if upper < 0:
                return -1
            self.refine()
        raise AssertionError("ordered-field sign refinement ceiling reached")


class NumberFieldElement:
    def __init__(self, field, coefficients=0):
        self.field = field
        if isinstance(coefficients, NumberFieldElement):
            require(coefficients.field is field, "mixed number fields")
            self.coefficients = coefficients.coefficients
            return
        if isinstance(coefficients, (int, Fraction)):
            coefficients = [Fraction(coefficients)]
        coefficients = clean(map(Fraction, coefficients))
        while len(coefficients) > field.degree:
            degree = len(coefficients) - 1
            scale = coefficients[-1]
            shift = degree - field.degree
            for index, value in enumerate(field.modulus):
                coefficients[shift + index] -= scale * value
            coefficients = clean(coefficients)
        coefficients.extend([Fraction(0)] * (field.degree - len(coefficients)))
        self.coefficients = tuple(coefficients)

    def _coerce(self, other):
        return self.field.element(other)

    def __add__(self, other):
        other = self._coerce(other)
        return self.field.element(
            [left + right for left, right in zip(self.coefficients, other.coefficients)]
        )

    __radd__ = __add__

    def __neg__(self):
        return self.field.element([-value for value in self.coefficients])

    def __sub__(self, other):
        return self + (-self._coerce(other))

    def __rsub__(self, other):
        return self._coerce(other) - self

    def __mul__(self, other):
        other = self._coerce(other)
        product_values = [Fraction(0)] * (2 * self.field.degree - 1)
        for i, x in enumerate(self.coefficients):
            for j, y in enumerate(other.coefficients):
                product_values[i + j] += x * y
        return self.field.element(product_values)

    __rmul__ = __mul__

    def __pow__(self, exponent):
        require(exponent >= 0, "negative field power")
        answer = self.field.element(1)
        base = self
        while exponent:
            if exponent & 1:
                answer *= base
            base *= base
            exponent //= 2
        return answer

    def inverse(self):
        require(self, "zero number-field inverse")
        degree = self.field.degree
        generator = self.field.generator()
        columns = []
        power = self.field.element(1)
        for _index in range(degree):
            columns.append((self * power).coefficients)
            power *= generator
        matrix = [
            [columns[column][row] for column in range(degree)]
            + [Fraction(int(row == 0))]
            for row in range(degree)
        ]
        pivot_row = 0
        for column in range(degree):
            pivot = next((row for row in range(pivot_row, degree) if matrix[row][column]), None)
            require(pivot is not None, "reducible number-field modulus")
            matrix[pivot_row], matrix[pivot] = matrix[pivot], matrix[pivot_row]
            scale = matrix[pivot_row][column]
            matrix[pivot_row] = [value / scale for value in matrix[pivot_row]]
            for row in range(degree):
                if row == pivot_row or not matrix[row][column]:
                    continue
                scale = matrix[row][column]
                matrix[row] = [
                    left - scale * right for left, right in zip(matrix[row], matrix[pivot_row])
                ]
            pivot_row += 1
        answer = self.field.element([matrix[row][-1] for row in range(degree)])
        require(self * answer == 1, "number-field inverse check")
        return answer

    def __truediv__(self, other):
        return self * self._coerce(other).inverse()

    def __bool__(self):
        return any(self.coefficients)

    def __eq__(self, other):
        try:
            other = self._coerce(other)
        except (AssertionError, TypeError):
            return False
        return self.coefficients == other.coefficients


def kclean(polynomial):
    polynomial = list(polynomial)
    while polynomial and not polynomial[-1]:
        polynomial.pop()
    return polynomial


def k_derivative(polynomial):
    return kclean([degree * value for degree, value in enumerate(polynomial)][1:])


def k_value(polynomial, point):
    require(polynomial, "evaluate zero field polynomial without field")
    answer = polynomial[0].field.element(0)
    for coefficient in reversed(polynomial):
        answer = answer * point + coefficient
    return answer


def k_divmod(dividend, divisor):
    remainder = kclean(dividend)
    divisor = kclean(divisor)
    require(divisor, "zero field-polynomial divisor")
    field = divisor[0].field
    quotient = [field.element(0) for _ in range(max(0, len(remainder) - len(divisor) + 1))]
    while remainder and len(remainder) >= len(divisor):
        shift = len(remainder) - len(divisor)
        scale = remainder[-1] / divisor[-1]
        quotient[shift] += scale
        for index, value in enumerate(divisor):
            remainder[index + shift] -= scale * value
        remainder = kclean(remainder)
    return kclean(quotient), remainder


def k_monic(polynomial):
    polynomial = kclean(polynomial)
    if not polynomial:
        return []
    leading = polynomial[-1]
    return [value / leading for value in polynomial]


def k_gcd(left, right):
    left, right = kclean(left), kclean(right)
    while right:
        left, right = right, k_divmod(left, right)[1]
    return k_monic(left)


def k_squarefree(polynomial):
    polynomial = kclean(polynomial)
    if len(polynomial) <= 1:
        return polynomial
    divisor = k_gcd(polynomial, k_derivative(polynomial))
    quotient, remainder = k_divmod(polynomial, divisor)
    require(not remainder, "squarefree quotient remainder")
    return k_monic(quotient)


def k_remove_boundaries(polynomial):
    polynomial = k_squarefree(polynomial)
    if len(polynomial) <= 1:
        return polynomial
    if not k_value(polynomial, Fraction(0)):
        polynomial = polynomial[1:]
    if len(polynomial) > 1 and not k_value(polynomial, Fraction(1)):
        field = polynomial[0].field
        quotient, remainder = k_divmod(polynomial, [field.element(-1), field.element(1)])
        require(not remainder, "u=1 boundary quotient")
        polynomial = quotient
    return k_monic(polynomial)


def k_sturm(polynomial):
    polynomial = k_monic(polynomial)
    require(len(polynomial) >= 2, "constant field Sturm polynomial")
    sequence = [polynomial, k_derivative(polynomial)]
    while sequence[-1]:
        _quotient, remainder = k_divmod(sequence[-2], sequence[-1])
        if not remainder:
            break
        sequence.append([-value for value in remainder])
    return tuple(sequence)


def k_variations(sequence, point):
    field = sequence[0][0].field
    signs = []
    for polynomial in sequence:
        value = k_value(polynomial, point)
        sign = field.sign(value)
        if sign:
            signs.append(sign)
    return sum(left != right for left, right in zip(signs, signs[1:]))


def k_roots_between(sequence, lower, upper):
    require(lower < upper, "bad field root interval")
    require(k_value(sequence[0], lower) and k_value(sequence[0], upper), "field Sturm endpoint root")
    return k_variations(sequence, lower) - k_variations(sequence, upper)


def load_sequences(open_lift):
    sectors = []
    for row in open_lift["artifact_shards"]["shards"]:
        compressed = (HERE / "data" / row["path"]).read_bytes()
        require(len(compressed) == row["bytes"], "open-sector shard byte count")
        require(sha256(compressed).hexdigest() == row["sha256"], "open-sector shard hash")
        shard = json.loads(gzip.decompress(compressed))
        require(shard["sector_start"] == len(sectors), "open-sector shard order")
        sectors.extend(shard["sectors"])
    return [[entry[0] for entry in sector] for sector in sectors]


def completed_sections(simple, invisible, multi, regular):
    groups = [
        {
        row[0] for row in simple["simple_section_lift"]["crossings"]
        },
        {
        row[0] for row in invisible["invisible_section_lift"]["completed"]
        },
        {
        row[0] for row in multi["multi_section_lift"]["completed"]
        },
        {
        row[0] for key in ("unchanged", "same_count")
        for row in regular["regular_residual_section_lift"][key]
        },
    ]
    answer = set().union(*groups)
    require(sum(map(len, groups)) == len(answer), "predecessor section overlap")
    return answer


def specialize_base_polynomials(base_catalog, field):
    generator = field.generator()
    powers = [field.element(1)]
    maximum_t_degree = max(
        term["exponent"][1] for row in base_catalog for term in row["polynomial"]
    )
    for _degree in range(maximum_t_degree):
        powers.append(powers[-1] * generator)
    answer = []
    for row in base_catalog:
        degree_u = max(term["exponent"][0] for term in row["polynomial"])
        coefficients = [field.element(0) for _ in range(degree_u + 1)]
        for term in row["polynomial"]:
            exponent_u, exponent_t = term["exponent"]
            coefficients[exponent_u] += Fraction(term["coefficient"]) * powers[exponent_t]
        answer.append(kclean(coefficients))
    return answer


def verify_section(candidate, section_source, left, right, base, expected_id):
    require(candidate["section_id"] == section_source["id"] == expected_id, "section id")
    require(candidate["factor_id"] == section_source["factor_id"], "section factor")
    require(candidate["factor_root_index"] == section_source["factor_root_index"], "factor root index")
    q_coefficients = base["second_projection"]["catalog"][section_source["factor_id"]][
        "coefficients_low_to_high"
    ]
    require(candidate["minimal_degree"] == len(q_coefficients) - 1 <= 4, "minimal degree")
    field = NumberField(q_coefficients, Fraction(section_source["left"]), Fraction(section_source["right"]))
    polynomials = specialize_base_polynomials(base["base_factorization"]["catalog"], field)
    actual_vertical = [index for index, polynomial in enumerate(polynomials) if not polynomial]
    actual_boundary = {"u=0": [], "u=1": []}
    interior = []
    sequences = []
    total_roots = []
    for base_id, polynomial in enumerate(polynomials):
        if not polynomial:
            interior.append([])
            sequences.append(None)
            total_roots.append(0)
            continue
        if not k_value(polynomial, Fraction(0)):
            actual_boundary["u=0"].append(base_id)
        if not k_value(polynomial, Fraction(1)):
            actual_boundary["u=1"].append(base_id)
        bounded = k_remove_boundaries(polynomial)
        interior.append(bounded)
        if len(bounded) <= 1:
            sequences.append(None)
            total_roots.append(0)
        else:
            sequence = k_sturm(bounded)
            sequences.append(sequence)
            total_roots.append(k_roots_between(sequence, Fraction(0), Fraction(1)))
    require(candidate["vertical_zero_factors"] == actual_vertical, "vertical-zero factors")
    require(candidate["boundary_zero_factors"] == actual_boundary, "boundary-zero factors")

    if left == right:
        kind = "unchanged"
    elif len(left) == len(right):
        kind = "same_count"
    else:
        kind = "count_change"
    require(candidate["kind"] == kind, "section kind")
    require(candidate["left_open_root_instances"] == len(left), "left open count")
    require(candidate["right_open_root_instances"] == len(right), "right open count")
    points = candidate["points"]
    require(candidate["section_root_points"] == len(points), "section point count")
    require(candidate["section_u_strips"] == len(points) + 1, "section strip count")
    claimed = Counter()
    previous = Fraction(0)
    multi_owner_points = 0
    for point in points:
        lower, upper = Fraction(point["lower"]), Fraction(point["upper"])
        require(previous < lower < upper < 1, "point interval order")
        previous = upper
        owners = point["owners"]
        require(owners and owners == sorted(set(owners)), "point owner set")
        require(all(0 <= owner < len(polynomials) and sequences[owner] is not None for owner in owners), "point owner range")
        for owner in owners:
            require(k_roots_between(sequences[owner], lower, upper) == 1, "owner root box")
            claimed[owner] += 1
        if len(owners) > 1:
            common = interior[owners[0]]
            for owner in owners[1:]:
                common = k_gcd(common, interior[owner])
            require(len(common) >= 2, "owner group lacks common divisor")
            require(k_roots_between(k_sturm(common), lower, upper) == 1, "owner group lacks one common root")
            multi_owner_points += 1
    require(
        all(claimed[base_id] == count for base_id, count in enumerate(total_roots)),
        "incomplete section root ownership",
    )
    return {
        "points": len(points),
        "strips": len(points) + 1,
        "vertical": len(actual_vertical),
        "boundary": sum(map(len, actual_boundary.values())),
        "degree": field.degree,
        "prime": field.irreducibility_prime,
        "multi_owner_points": multi_owner_points,
    }


def validate_metadata(candidate, sources, observed):
    require(candidate["format"] == FORMAT and candidate["status"] == "PROVED", "format/status")
    scope = candidate["scope"]
    require(scope["all_1693_algebraic_t_section_base_lifts"] == "COMPLETE", "all-section scope")
    require(scope["final_28_algebraic_t_section_base_lifts"] == "COMPLETE", "final-section scope")
    require(scope["v_fiber_lift"] == "NOT_YET_CONSTRUCTED", "v scope")
    require(scope["global_parent_cell_coverage"] == "NOT_CLAIMED", "global scope")
    require(scope["honest_9dvl_score"] == "2/9", "dishonest score")
    for key, value in sources.items():
        require(candidate["source"][key] == value, f"{key} source")
    lift = candidate["final_section_lift"]
    require(lift["completed_sections"] == 28, "completed count")
    require(lift["section_kind_census"] == {"count_change": 14, "same_count": 7, "unchanged": 7}, "kind census")
    require(lift["minimal_degree_census"] == observed["degree_census"], "degree census")
    require(lift["vertical_zero_factor_incidences"] == observed["vertical"], "vertical census")
    require(lift["boundary_zero_factor_incidences"] == observed["boundary"], "boundary census")
    require(lift["section_u_root_points"] == observed["points"] == 1_862, "root-point census")
    require(lift["section_u_strips"] == observed["strips"] == 1_890, "strip census")
    require(lift["section_base_cells"] == observed["points"] + observed["strips"] == 3_752, "cell census")
    require(lift["interval_bits"] == 70, "interval precision")
    require(lift["sections_sha256"] == digest(lift["sections"]), "sections digest")
    require(candidate["semantic_sha256"] == digest({
        "regular_residual_section_lift_semantic_sha256": candidate["source"]["regular_residual_section_lift_semantic_sha256"],
        "sections": lift["sections"],
    }), "semantic digest")
    require(candidate["remaining_frontier"]["remaining_algebraic_t_sections"] == 0, "remaining section frontier")
    require(candidate["resource_effect"]["ceiling_not_triggered"] is True, "resource ceiling")


def rejection(action, fragment):
    try:
        action()
    except AssertionError as error:
        require(fragment in str(error), f"canary failed for wrong reason: {error}")
    else:
        raise AssertionError(f"hostile mutation survived: {fragment}")


def hostile_canaries(stored, sources, observed, section_source, left, right, base):
    bad = deepcopy(stored)
    bad["status"] = "OBSERVATION"
    rejection(lambda: validate_metadata(bad, sources, observed), "format/status")
    bad = deepcopy(stored)
    bad["scope"]["honest_9dvl_score"] = "3/9"
    rejection(lambda: validate_metadata(bad, sources, observed), "dishonest score")
    bad = deepcopy(stored)
    bad["scope"]["v_fiber_lift"] = "COMPLETE"
    rejection(lambda: validate_metadata(bad, sources, observed), "v scope")
    bad = deepcopy(stored)
    bad["scope"]["global_parent_cell_coverage"] = "PROVED"
    rejection(lambda: validate_metadata(bad, sources, observed), "global scope")
    bad = deepcopy(stored)
    bad["source"]["base_projection_semantic_sha256"] = "0" * 64
    rejection(lambda: validate_metadata(bad, sources, observed), "base_projection_semantic_sha256 source")
    bad = deepcopy(stored)
    bad["final_section_lift"]["completed_sections"] = 27
    rejection(lambda: validate_metadata(bad, sources, observed), "completed count")
    bad = deepcopy(stored)
    bad["final_section_lift"]["section_u_root_points"] -= 1
    rejection(lambda: validate_metadata(bad, sources, observed), "root-point census")
    bad = deepcopy(stored)
    bad["remaining_frontier"]["remaining_algebraic_t_sections"] = 1
    rejection(lambda: validate_metadata(bad, sources, observed), "remaining section frontier")

    first = stored["final_section_lift"]["sections"][0]
    bad_section = deepcopy(first)
    bad_section["points"][1]["lower"] = bad_section["points"][0]["lower"]
    rejection(lambda: verify_section(bad_section, section_source, left, right, base, 175), "point interval order")
    bad_section = deepcopy(first)
    multi_owner = next(point for point in bad_section["points"] if len(point["owners"]) > 1)
    multi_owner["owners"].pop()
    rejection(lambda: verify_section(bad_section, section_source, left, right, base, 175), "incomplete section root ownership")
    bad_section = deepcopy(first)
    bad_section["vertical_zero_factors"] = [0]
    rejection(lambda: verify_section(bad_section, section_source, left, right, base, 175), "vertical-zero factors")
    bad_section = deepcopy(first)
    bad_section["boundary_zero_factors"]["u=1"] = [0]
    rejection(lambda: verify_section(bad_section, section_source, left, right, base, 175), "boundary-zero factors")
    return 12


def main():
    base = json.loads(gzip.decompress(BASE.read_bytes()))
    roots = json.loads(gzip.decompress(ROOTS.read_bytes()))
    open_lift = json.loads(OPEN.read_bytes())
    simple = json.loads(SIMPLE.read_bytes())
    invisible = json.loads(INVISIBLE.read_bytes())
    multi = json.loads(MULTI.read_bytes())
    regular = json.loads(REGULAR.read_bytes())
    stored = json.loads(CERTIFICATE.read_bytes())
    require(
        all(source["status"] == "PROVED" for source in (simple, invisible, multi, regular)),
        "predecessor proof status",
    )
    require(
        simple["source"]["open_sector_lift_semantic_sha256"] == open_lift["semantic_sha256"]
        and invisible["source"]["simple_section_lift_semantic_sha256"] == simple["semantic_sha256"]
        and multi["source"]["invisible_section_lift_semantic_sha256"] == invisible["semantic_sha256"]
        and regular["source"]["multi_section_lift_semantic_sha256"] == multi["semantic_sha256"],
        "predecessor semantic chain",
    )
    sequences = load_sequences(open_lift)
    complete = completed_sections(simple, invisible, multi, regular)
    require(len(complete) == 1_665 and all(0 <= item < 1_693 for item in complete), "predecessor exact union")
    frontier_ids = [index for index in range(len(roots["root_isolation"]["sections"])) if index not in complete]
    require(len(frontier_ids) == 28, "derived final frontier")
    candidate_rows = stored["final_section_lift"]["sections"]
    require([row["section_id"] for row in candidate_rows] == frontier_ids, "certificate frontier order")

    reports = []
    degree_census = Counter()
    prime_census = Counter()
    for expected_id, candidate in zip(frontier_ids, candidate_rows, strict=True):
        report = verify_section(
            candidate,
            roots["root_isolation"]["sections"][expected_id],
            sequences[expected_id],
            sequences[expected_id + 1],
            base,
            expected_id,
        )
        reports.append(report)
        degree_census[report["degree"]] += 1
        prime_census[report["prime"]] += 1
        print(
            "PASS SECTION",
            expected_id,
            candidate["kind"],
            "POINTS",
            report["points"],
            "MULTI_OWNER",
            report["multi_owner_points"],
            flush=True,
        )
    observed = {
        "degree_census": {str(key): value for key, value in sorted(degree_census.items())},
        "points": sum(row["points"] for row in reports),
        "strips": sum(row["strips"] for row in reports),
        "vertical": sum(row["vertical"] for row in reports),
        "boundary": sum(row["boundary"] for row in reports),
    }
    sources = {
        "base_projection_semantic_sha256": base["semantic_sha256"],
        "root_isolation_semantic_sha256": roots["semantic_sha256"],
        "open_sector_lift_semantic_sha256": open_lift["semantic_sha256"],
        "simple_section_lift_semantic_sha256": simple["semantic_sha256"],
        "invisible_section_lift_semantic_sha256": invisible["semantic_sha256"],
        "multi_section_lift_semantic_sha256": multi["semantic_sha256"],
        "regular_residual_section_lift_semantic_sha256": regular["semantic_sha256"],
    }
    validate_metadata(stored, sources, observed)
    canaries = hostile_canaries(
        stored,
        sources,
        observed,
        roots["root_isolation"]["sections"][175],
        sequences[175],
        sequences[176],
        base,
    )
    print("PASS 28/28 final algebraic t-section lifts")
    print("PASS exact irreducibility witnesses", dict(sorted(prime_census.items())))
    print("PASS 1862 section root points + 1890 strips = 3752 base cells")
    print("PASS vertical/boundary degeneracies", observed["vertical"], observed["boundary"])
    print(f"PASS {canaries}/{canaries} hostile mutations rejected")
    print("REMAINING algebraic t sections 0; v lifting and global gluing remain open")
    print("SCOPE honest 9DVL score 2/9")


if __name__ == "__main__":
    main()
