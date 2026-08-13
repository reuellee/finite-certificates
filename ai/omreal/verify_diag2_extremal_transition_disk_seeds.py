#!/usr/bin/env python3
"""Exact four-sector checks at ten parent-187 d/e transition nodes.

The complete parent-187 e-line census has ten residual factors which change
one of the six tracked extremal endpoint records.  This verifier checks ten
selected candidate intersections involving six of those factors in the d/e
plane.  For each pair it isolates a unique transverse common zero in a
pinned rational box, excludes every other residual wall from that box, and
pins one exact rational point in every sign sector.  It then evaluates all
26,740 residual factors exactly and enumerates the complete 26,112-tope table
in all forty sample chambers.

The result is an exact forty-chamber seed audit.  It does not prove that the
ten nodes are the nearest intersections, cover a collar, enumerate a
two-dimensional residual disk, or prove diagonal two.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from fractions import Fraction
import hashlib
from math import comb

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as representative
import DIAG9_GRAPH_exact_topes as exact_topes
import verify_diag2_extremal_line_transition_census as line
import verify_diag2_extremal_safe_loss_edge as safe_loss
import verify_diag2_near_counterexample_separators as near_separators


PARENT_INDEX = 187
VARIABLES = (3, 4)  # d/e in the standard a,...,i chart
# (tracked factor, partner factor, display x approximation, display y approximation,
#  tracked kind, partner kind, expected partner exchange per side)
NODE_SPECS = (
    (10_115, 21_582, "+1.055352659e-5", "+0.02164554014", 51, 49, 2),
    (22_118, 5_849, "-1.362728980e-5", "-0.0306133442", 49, 38, 10),
    (22_118, 7_562, "+1.749063675e-5", "-0.0305671243", 49, 51, 2),
    (23_559, 25_433, "-2.014729315e-5", "+0.0128998099", 50, 49, 2),
    (8_421, 5_326, "+2.348030579e-5", "-0.0430619524", 51, 50, 2),
    (22_118, 12_307, "+2.840210356e-5", "-0.0305509174", 49, 49, 2),
    (13_869, 22_792, "-3.203636702e-5", "-0.0672466779", 50, 50, 2),
    (23_559, 26_286, "-3.955106466e-5", "+0.0128934540", 50, 50, 2),
    (8_421, 16_080, "-4.218696268e-5", "-0.0430202130", 51, 51, 2),
    (23_979, 2_598, "-4.686387491e-5", "-0.0200683814", 50, 49, 2),
)

# Exact rational sample coordinates discovered once by Newton and then
# frozen here.  Runtime verification uses no floating-point geometry.
PINNED_SECTORS = (
    (
        ((-1, -1), ("1.054986732908538e-05", "0.0216455381416508011")),
        ((-1, 1), ("1.05538673290853803e-05", "0.0216455381416508011")),
        ((1, -1), ("1.05531858525536436e-05", "0.021645542141650799")),
        ((1, 1), ("1.05571858525536439e-05", "0.021645542141650799")),
    ),
    (
        ((-1, -1), ("-1.36409847483623383e-05", "-0.0306133615640795456")),
        ((-1, 1), ("-1.36292145077521806e-05", "-0.030613344081506965")),
        ((1, -1), ("-1.36253651591754472e-05", "-0.0306133442485161146")),
        ((1, 1), ("-1.36135949185652894e-05", "-0.030613326765943534")),
    ),
    (
        ((-1, -1), ("1.74897339254940732e-05", "-0.0305671226760666805")),
        ((-1, 1), ("1.748642659925476e-05", "-0.0305671275884642109")),
        ((1, -1), ("1.7494846907711626e-05", "-0.0305671209662744144")),
        ((1, 1), ("1.74915395814723128e-05", "-0.0305671258786719448")),
    ),
    (
        ((-1, -1), ("-2.01496604955021363e-05", "0.0128998071177374267")),
        ((-1, 1), ("-2.01338821717836091e-05", "0.0128998122860763242")),
        ((1, -1), ("-2.01607041203887107e-05", "0.0128998075002649207")),
        ((1, 1), ("-2.01449257966701835e-05", "0.0128998126686038182")),
    ),
    (
        ((-1, -1), ("2.34821022244722374e-05", "-0.043061949563586048")),
        ((-1, 1), ("2.34779143502487091e-05", "-0.0430619469020405155")),
        ((1, -1), ("2.34826972382615113e-05", "-0.0430619579929291674")),
        ((1, 1), ("2.34785093640379829e-05", "-0.0430619553313836348")),
    ),
    (
        ((-1, -1), ("2.840718828100923e-05", "-0.0305509069188403745")),
        ((-1, 1), ("2.83926529421126146e-05", "-0.0305509285082313717")),
        ((1, -1), ("2.84115541698908365e-05", "-0.0305509063187431526")),
        ((1, 1), ("2.83970188309942211e-05", "-0.0305509279081341498")),
    ),
    (
        ((-1, -1), ("-3.20353163908143325e-05", "-0.0672466794432658166")),
        ((-1, 1), ("-3.20409041475964917e-05", "-0.0672466819879566358")),
        ((1, -1), ("-3.20318298839444406e-05", "-0.0672466738554565735")),
        ((1, 1), ("-3.20374176407265998e-05", "-0.0672466764001473927")),
    ),
    (
        ((-1, -1), ("-3.95493082669383128e-05", "0.012893452624205614")),
        ((-1, 1), ("-3.95541271100745083e-05", "0.0128934510457700251")),
        ((1, -1), ("-3.95480022170789728e-05", "0.0128934570519518652")),
        ((1, 1), ("-3.95528210602151683e-05", "0.0128934554735162764")),
    ),
    (
        ((-1, -1), ("-4.21852097629608566e-05", "-0.0430202100946591934")),
        ((-1, 1), ("-4.21817491438221935e-05", "-0.0430202122945893273")),
        ((1, -1), ("-4.21921762095908964e-05", "-0.0430202137183144234")),
        ((1, 1), ("-4.21887155904522332e-05", "-0.0430202159182445573")),
    ),
    (
        ((-1, -1), ("-4.68645406707208313e-05", "-0.0200683794821741451")),
        ((-1, 1), ("-4.68674884652252826e-05", "-0.0200683837601510241")),
        ((1, -1), ("-4.68602613494898421e-05", "-0.0200683790786343637")),
        ((1, 1), ("-4.68632091439942933e-05", "-0.0200683833566112427")),
    ),
)

NOT_LEFT = ("not-both-bad", True, False)
NOT_RIGHT = ("not-both-bad", False, True)
B6 = ("both-bad", 6, 56, 56, False)

OBS_10115_NEG = (B6, B6, ("both-bad", 9, 62, 56, True))
OBS_10115_POS = (B6, B6, NOT_RIGHT)
OBS_22118_NEG = (
    ("both-bad", 9, 61, 56, True),
    ("both-bad", 9, 56, 61, True),
    NOT_LEFT,
)
OBS_22118_POS = (
    ("both-bad", 9, 61, 56, True),
    ("both-bad", 15, 56, 67, True),
    NOT_LEFT,
)
OBS_23559_NEG = (B6, B6, B6)
OBS_23559_POS = (B6, B6, ("both-bad", 9, 62, 56, True))
OBS_STATIC_15 = (
    ("both-bad", 15, 67, 56, True),
    ("both-bad", 15, 56, 67, True),
    NOT_LEFT,
)
OBS_23979_NEG = (
    ("both-bad", 9, 61, 56, True),
    B6,
    ("both-bad", 12, 56, 62, True),
)
OBS_23979_POS = (
    ("both-bad", 9, 61, 56, True),
    ("both-bad", 9, 56, 61, True),
    ("both-bad", 12, 56, 62, True),
)

# Each item is (observations on tracked-factor negative side,
# observations on tracked-factor positive side).
EXPECTED_NODE_OBSERVATIONS = (
    (OBS_10115_NEG, OBS_10115_POS),
    (OBS_22118_NEG, OBS_22118_POS),
    (OBS_22118_NEG, OBS_22118_POS),
    (OBS_23559_NEG, OBS_23559_POS),
    (OBS_STATIC_15, OBS_STATIC_15),
    (OBS_22118_NEG, OBS_22118_POS),
    (OBS_STATIC_15, OBS_STATIC_15),
    (OBS_23559_NEG, OBS_23559_POS),
    (OBS_STATIC_15, OBS_STATIC_15),
    (OBS_23979_NEG, OBS_23979_POS),
)

EXPECTED_CHANGED_SIGNATURES = (
    (70_482_716_760_692_055,),
    (41_224_087_949_575_724,),
    (41_224_087_949_575_724,),
    (68_230_936_274_949_461,),
    (70_482_716_760_692_055,),
    (41_224_087_949_575_724,),
    (70_482_716_760_692_055,),
    (68_230_936_274_949_461,),
    (70_482_716_760_692_055,),
    (41_224_087_949_575_724,),
)

# Common-direction counts which survive the tracked-factor edge.  None means
# that one endpoint is a tope on at least one side, so no two-sided common
# mask exists for that pair.
EXPECTED_TRACKED_SURVIVORS = (
    (6, 6, None),
    (9, 9, None),
    (9, 9, None),
    (6, 6, 6),
    (15, 15, None),
    (9, 9, None),
    (15, 15, None),
    (6, 6, 6),
    (15, 15, None),
    (9, 6, 12),
)

EXPECTED_CHARTS = 40
EXPECTED_MINIMUM_OVERLAP = 6
EXPECTED_DIGEST = "105f9aae5248889363155ec518c7a54110f06760b724d6ac8188c199f5189aba"


def restrict_two(polynomial, base):
    """Substitute d=base_d+x and e=base_e+y using exact arithmetic."""

    answer = {}
    first, second = VARIABLES
    for monomial, coefficient in polynomial.items():
        fixed = Fraction(coefficient)
        for variable, exponent in enumerate(monomial):
            if variable not in VARIABLES and exponent:
                fixed *= base[variable] ** exponent
        first_exponent = monomial[first]
        second_exponent = monomial[second]
        for i in range(first_exponent + 1):
            first_term = (
                comb(first_exponent, i)
                * base[first] ** (first_exponent - i)
            )
            for j in range(second_exponent + 1):
                value = (
                    fixed
                    * first_term
                    * comb(second_exponent, j)
                    * base[second] ** (second_exponent - j)
                )
                answer[(i, j)] = answer.get((i, j), Fraction(0)) + value
    return {monomial: value for monomial, value in answer.items() if value}


def exact_value(polynomial, x, y):
    return sum(
        value * x**first * y**second
        for (first, second), value in polynomial.items()
    )


def interval_multiply(left, right):
    values = (
        left[0] * right[0],
        left[0] * right[1],
        left[1] * right[0],
        left[1] * right[1],
    )
    return min(values), max(values)


def interval_power(interval, exponent):
    answer = (Fraction(1), Fraction(1))
    for _index in range(exponent):
        answer = interval_multiply(answer, interval)
    return answer


def interval_add(left, right):
    return left[0] + right[0], left[1] + right[1]


def interval_scale(interval, scalar):
    values = scalar * interval[0], scalar * interval[1]
    return min(values), max(values)


def interval_divide(numerator, denominator):
    if denominator[0] <= 0 <= denominator[1]:
        raise AssertionError("interval division by a possible zero")
    reciprocal = (
        min(Fraction(1, 1) / denominator[0], Fraction(1, 1) / denominator[1]),
        max(Fraction(1, 1) / denominator[0], Fraction(1, 1) / denominator[1]),
    )
    return interval_multiply(numerator, reciprocal)


def interval_value(polynomial, x_interval, y_interval):
    answer = (Fraction(0), Fraction(0))
    for (first, second), coefficient in polynomial.items():
        term = interval_multiply(
            interval_power(x_interval, first),
            interval_power(y_interval, second),
        )
        answer = interval_add(answer, interval_scale(term, coefficient))
    return answer


def polynomial_add(left, right, scale=1):
    answer = dict(left)
    for monomial, coefficient in right.items():
        answer[monomial] = answer.get(monomial, Fraction(0)) + scale * coefficient
        if not answer[monomial]:
            del answer[monomial]
    return answer


def polynomial_multiply(left, right):
    answer = {}
    for (left_x, left_y), left_value in left.items():
        for (right_x, right_y), right_value in right.items():
            monomial = left_x + right_x, left_y + right_y
            answer[monomial] = (
                answer.get(monomial, Fraction(0)) + left_value * right_value
            )
    return {monomial: value for monomial, value in answer.items() if value}


def derivative_two(polynomial, variable):
    answer = {}
    for monomial, coefficient in polynomial.items():
        exponent = monomial[variable]
        if not exponent:
            continue
        target = list(monomial)
        target[variable] -= 1
        answer[tuple(target)] = exponent * coefficient
    return answer


def univariate_clean(polynomial):
    return {degree: value for degree, value in polynomial.items() if value}


def univariate_add(left, right, scale=1):
    answer = dict(left)
    for degree, value in right.items():
        answer[degree] = answer.get(degree, Fraction(0)) + scale * value
    return univariate_clean(answer)


def univariate_multiply(left, right):
    answer = {}
    for first, first_value in left.items():
        for second, second_value in right.items():
            degree = first + second
            answer[degree] = (
                answer.get(degree, Fraction(0)) + first_value * second_value
            )
    return univariate_clean(answer)


def univariate_power(polynomial, exponent):
    answer = {0: Fraction(1)}
    for _index in range(exponent):
        answer = univariate_multiply(answer, polynomial)
    return answer


def univariate_derivative(polynomial):
    return {
        degree - 1: degree * value
        for degree, value in polynomial.items()
        if degree
    }


def univariate_value(polynomial, value):
    return sum(coefficient * value**degree for degree, coefficient in polynomial.items())


def univariate_divmod(dividend, divisor):
    remainder = dict(dividend)
    quotient = {}
    divisor_degree = max(divisor)
    divisor_lead = divisor[divisor_degree]
    while remainder and max(remainder) >= divisor_degree:
        remainder_degree = max(remainder)
        degree = remainder_degree - divisor_degree
        coefficient = remainder[remainder_degree] / divisor_lead
        quotient[degree] = quotient.get(degree, Fraction(0)) + coefficient
        for source_degree, source_value in divisor.items():
            target = source_degree + degree
            remainder[target] = (
                remainder.get(target, Fraction(0)) - coefficient * source_value
            )
            if not remainder[target]:
                del remainder[target]
    return univariate_clean(quotient), univariate_clean(remainder)


def sturm_sequence(polynomial):
    polynomial = univariate_clean(polynomial)
    if not polynomial:
        raise AssertionError("zero polynomial has no finite Sturm sequence")
    sequence = [polynomial, univariate_derivative(polynomial)]
    if not sequence[1]:
        return tuple(sequence[:1])
    while sequence[-1]:
        _quotient, remainder = univariate_divmod(sequence[-2], sequence[-1])
        if not remainder:
            break
        sequence.append({degree: -value for degree, value in remainder.items()})
    return tuple(sequence)


def sign_variations(sequence, value):
    signs = []
    for polynomial in sequence:
        evaluation = univariate_value(polynomial, value)
        if evaluation:
            signs.append(1 if evaluation > 0 else -1)
    return sum(left != right for left, right in zip(signs, signs[1:]))


def root_count(polynomial, lower, upper):
    if lower >= upper:
        raise AssertionError("invalid root-isolation interval")
    if not univariate_value(polynomial, lower) or not univariate_value(polynomial, upper):
        raise AssertionError("root-isolation endpoint lies on the polynomial")
    sequence = sturm_sequence(polynomial)
    return sign_variations(sequence, lower) - sign_variations(sequence, upper)


def isolate_unique_root(polynomial, lower, upper, rounds=40):
    if root_count(polynomial, lower, upper) != 1:
        raise AssertionError("root interval is not isolating")
    for _round in range(rounds):
        midpoint = (lower + upper) / 2
        midpoint_value = univariate_value(polynomial, midpoint)
        if not midpoint_value:
            return midpoint, midpoint
        if root_count(polynomial, lower, midpoint):
            upper = midpoint
        else:
            lower = midpoint
    return lower, upper


def x_coefficients(polynomial):
    answer = {}
    for (x_degree, y_degree), value in polynomial.items():
        coefficient = answer.setdefault(x_degree, {})
        coefficient[y_degree] = coefficient.get(y_degree, Fraction(0)) + value
    return {degree: univariate_clean(value) for degree, value in answer.items()}


def elimination_polynomial(anchor, other):
    """Eliminate x when anchor=A(y)+x*B(y), returning the numerator."""

    anchor_x = x_coefficients(anchor)
    if max(anchor_x) != 1 or not anchor_x.get(1):
        raise AssertionError("node anchor is not genuinely linear in x")
    a = anchor_x.get(0, {})
    b = anchor_x[1]
    negative_a = {degree: -value for degree, value in a.items()}
    other_x = x_coefficients(other)
    degree = max(other_x)
    resultant = {}
    for power, coefficient in other_x.items():
        term = univariate_multiply(
            coefficient,
            univariate_multiply(
                univariate_power(negative_a, power),
                univariate_power(b, degree - power),
            ),
        )
        resultant = univariate_add(resultant, term)
    if not resultant:
        raise AssertionError("candidate factors share an eliminated component")
    return a, b, resultant


def univariate_interval(polynomial, interval):
    answer = (Fraction(0), Fraction(0))
    for degree, coefficient in polynomial.items():
        answer = interval_add(
            answer,
            interval_scale(interval_power(interval, degree), coefficient),
        )
    return answer


def segment_polynomial(polynomial, start, stop):
    answer = {}
    dx = stop[0] - start[0]
    dy = stop[1] - start[1]
    for (x_degree, y_degree), coefficient in polynomial.items():
        for first in range(x_degree + 1):
            x_term = (
                comb(x_degree, first)
                * start[0] ** (x_degree - first)
                * dx**first
            )
            for second in range(y_degree + 1):
                degree = first + second
                value = (
                    coefficient
                    * x_term
                    * comb(y_degree, second)
                    * start[1] ** (y_degree - second)
                    * dy**second
                )
                answer[degree] = answer.get(degree, Fraction(0)) + value
    return univariate_clean(answer)


def pinned_sectors(node_index, spec, restrictions):
    tracked, partner = spec[:2]
    answer = {
        sector: (Fraction(x), Fraction(y))
        for sector, (x, y) in PINNED_SECTORS[node_index]
    }
    if tuple(sorted(answer)) != ((-1, -1), (-1, 1), (1, -1), (1, 1)):
        raise AssertionError("a transition node is missing a pinned sign sector")
    for expected, (x, y) in answer.items():
        actual = (
            safe_loss.sign(exact_value(restrictions[tracked], x, y)),
            safe_loss.sign(exact_value(restrictions[partner], x, y)),
        )
        if actual != expected:
            raise AssertionError(
                f"node {tracked}/{partner} selected wrong sector {actual}"
            )
    return answer


def certify_node_box(node_index, spec, sectors, restrictions, parent_restrictions):
    tracked, partner = spec[:2]
    x_interval = (
        min(x for x, _y in sectors.values()),
        max(x for x, _y in sectors.values()),
    )
    y_interval = (
        min(y for _x, y in sectors.values()),
        max(y for _x, y in sectors.values()),
    )
    display_point = Fraction(spec[2]), Fraction(spec[3])
    if not (
        x_interval[0] <= display_point[0] <= x_interval[1]
        and y_interval[0] <= display_point[1] <= y_interval[1]
    ):
        raise AssertionError(f"node {node_index} display approximation left its box")

    parent_signs = []
    for label, polynomial in parent_restrictions:
        interval = interval_value(polynomial, x_interval, y_interval)
        if interval[0] <= 0 <= interval[1]:
            raise AssertionError(
                f"node {node_index} box meets parent boundary {label}"
            )
        parent_signs.append((label, 1 if interval[0] > 0 else -1))

    excluded_signs = []
    for factor, polynomial in enumerate(restrictions):
        if factor in (tracked, partner):
            continue
        interval = interval_value(polynomial, x_interval, y_interval)
        if interval[0] <= 0 <= interval[1]:
            raise AssertionError(
                f"node {node_index} box may meet extra residual factor {factor}"
            )
        excluded_signs.append(1 if interval[0] > 0 else -1)

    pair = (restrictions[tracked], restrictions[partner])
    anchor_side = next(
        (
            side
            for side, polynomial in enumerate(pair)
            if max(x for x, _y in polynomial) == 1
            and any(x == 1 for x, _y in polynomial)
        ),
        None,
    )
    if anchor_side is None:
        raise AssertionError(f"node {node_index} has no linear-in-x anchor")
    anchor = pair[anchor_side]
    other = pair[1 - anchor_side]
    a, b, resultant = elimination_polynomial(anchor, other)
    if root_count(resultant, *y_interval) != 1:
        raise AssertionError(f"node {node_index} does not isolate one common y-root")
    root_interval = isolate_unique_root(resultant, *y_interval)
    a_interval = univariate_interval(a, root_interval)
    b_interval = univariate_interval(b, root_interval)
    x_image = interval_divide(interval_scale(a_interval, -1), b_interval)
    if x_image[0] < x_interval[0] or x_image[1] > x_interval[1]:
        raise AssertionError(f"node {node_index} common x-root leaves its box")

    first_dx = derivative_two(pair[0], 0)
    first_dy = derivative_two(pair[0], 1)
    second_dx = derivative_two(pair[1], 0)
    second_dy = derivative_two(pair[1], 1)
    jacobian = polynomial_add(
        polynomial_multiply(first_dx, second_dy),
        polynomial_multiply(first_dy, second_dx),
        scale=-1,
    )
    jacobian_interval = interval_value(jacobian, x_interval, y_interval)
    if jacobian_interval[0] <= 0 <= jacobian_interval[1]:
        raise AssertionError(f"node {node_index} transversality is not certified")

    segment_counts = []
    for fixed_partner in (-1, 1):
        start = sectors[(-1, fixed_partner)]
        stop = sectors[(1, fixed_partner)]
        counts = tuple(
            root_count(segment_polynomial(restrictions[factor], start, stop), 0, 1)
            for factor in (tracked, partner)
        )
        if counts != (1, 0):
            raise AssertionError(
                f"node {node_index} tracked segment has root counts {counts}"
            )
        segment_counts.append(("tracked", fixed_partner, counts))
    for fixed_tracked in (-1, 1):
        start = sectors[(fixed_tracked, -1)]
        stop = sectors[(fixed_tracked, 1)]
        counts = tuple(
            root_count(segment_polynomial(restrictions[factor], start, stop), 0, 1)
            for factor in (tracked, partner)
        )
        if counts != (0, 1):
            raise AssertionError(
                f"node {node_index} partner segment has root counts {counts}"
            )
        segment_counts.append(("partner", fixed_tracked, counts))

    return (
        x_interval,
        y_interval,
        display_point,
        root_interval,
        anchor_side,
        tuple(sorted(resultant.items())),
        jacobian_interval,
        tuple(parent_signs),
        tuple(excluded_signs),
        tuple(segment_counts),
    )


def exact_cell_task(task):
    key, coordinates, expected_parent = task
    return key, safe_loss.tope_table(coordinates, expected_parent, repr(key))


def pair_common_mask(pair, records):
    left, right = pair[:2]
    if records[left][0] == "tope" or records[right][0] == "tope":
        return None
    return records[left][0] & records[right][0]


def semantic_digest(
    samples,
    signs,
    topes,
    records,
    observations,
    box_certificates,
    summaries,
):
    digest = hashlib.sha256()
    digest.update(b"diag2-extremal-parent187-de-transition-seeds-v1\0")
    for node_index, spec in enumerate(NODE_SPECS):
        for value in (node_index, spec[0], spec[1], spec[4], spec[5], spec[6]):
            digest.update(int(value).to_bytes(8, "little", signed=True))
        for value in spec[2:4]:
            digest.update(value.encode("ascii") + b"\0")
        for sector in ((-1, -1), (-1, 1), (1, -1), (1, 1)):
            key = (node_index,) + sector
            x, y = samples[key]
            for value in (x, y):
                digest.update(str(value.numerator).encode("ascii") + b"/")
                digest.update(str(value.denominator).encode("ascii") + b"\0")
            digest.update(bytes(1 if value > 0 else 0 for value in signs[key]))
            for tope in topes[key]:
                digest.update(int(tope).to_bytes(8, "little"))
            digest.update(repr(tuple(sorted(records[key].items()))).encode("ascii") + b"\0")
            digest.update(repr(observations[key]).encode("ascii") + b"\0")
        digest.update(repr(box_certificates[node_index]).encode("ascii") + b"\0")
    digest.update(repr(tuple(summaries)).encode("ascii") + b"\0")
    return digest.hexdigest()


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    return parser.parse_args()


def main():
    args = parse_args()
    if args.workers < 1:
        raise ValueError("--workers must be positive")

    _atlas, by_index, active = near_separators.load_atlas()
    base, pairs = line.mapped_pairs(by_index, active)
    signatures = tuple(sorted({value for pair in pairs for value in pair[:2]}))
    expected_parent = exact_topes.parent_signs(safe_loss.integer_matrix(base))

    occurrences, occurrence_factor, factor_polynomials = labeled.factor_polynomials()
    _representatives, _stabilizers, alignment, _factor_occurrence, _sizes = (
        labeled.factor_orbit_data(occurrences, occurrence_factor)
    )
    restrictions = tuple(
        restrict_two(polynomial, base) for polynomial in factor_polynomials
    )
    if any(max(first + second for first, second in polynomial) > 2 for polynomial in restrictions):
        raise AssertionError("a d/e residual restriction exceeds total degree two")
    _representatives, brackets = representative.polynomial_data()
    if len(brackets) != 70:
        raise AssertionError("wrong parent-bracket count")
    parent_restrictions = tuple(
        (label, restrict_two(polynomial, base))
        for label, polynomial in sorted(brackets.items())
    )

    samples = {}
    factor_signs = {}
    coordinates = {}
    box_certificates = {}
    for node_index, spec in enumerate(NODE_SPECS):
        tracked, partner, _x, _y, tracked_kind, partner_kind, _exchange = spec
        if (alignment[tracked][0], alignment[partner][0]) != (
            tracked_kind,
            partner_kind,
        ):
            raise AssertionError(f"node {node_index} incidence kinds changed")
        sectors = pinned_sectors(node_index, spec, restrictions)
        box_certificates[node_index] = certify_node_box(
            node_index,
            spec,
            sectors,
            restrictions,
            parent_restrictions,
        )
        node_signs = {}
        for sector, (x, y) in sectors.items():
            key = (node_index,) + sector
            samples[key] = (x, y)
            signs = tuple(
                safe_loss.sign(exact_value(polynomial, x, y))
                for polynomial in restrictions
            )
            if not all(signs):
                zeros = tuple(index for index, value in enumerate(signs) if not value)
                raise AssertionError(f"node {node_index} sample has residual zeros {zeros}")
            factor_signs[key] = signs
            node_signs[sector] = signs
            point = list(base)
            point[VARIABLES[0]] += x
            point[VARIABLES[1]] += y
            coordinates[key] = tuple(point)

        changed = tuple(
            factor
            for factor, values in enumerate(zip(*node_signs.values(), strict=True))
            if len(set(values)) > 1
        )
        if changed != tuple(sorted((tracked, partner))):
            raise AssertionError(
                f"node {node_index} four-sector box changes factors {changed}"
            )
        for sector, signs in node_signs.items():
            if (signs[tracked], signs[partner]) != sector:
                raise AssertionError("exact all-factor signs disagree with sector key")
    if len(samples) != EXPECTED_CHARTS:
        raise AssertionError("wrong transition-seed chart count")

    enumerated = {}
    tasks = tuple(
        (key, point, expected_parent) for key, point in coordinates.items()
    )
    with ProcessPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(exact_cell_task, task) for task in tasks]
        for completed, future in enumerate(as_completed(futures), 1):
            key, topes = future.result()
            enumerated[key] = topes
            if completed % 4 == 0:
                print(f"exact transition sectors {completed}/{len(tasks)}", flush=True)

    records = {}
    observations = {}
    for key, table in enumerated.items():
        tope_set = set(table)
        indexes = line.mutable_source_indexes(tope_set)
        records[key] = line.records(tope_set, indexes, signatures)
        observations[key] = tuple(
            line.observation(pair, records[key]) for pair in pairs
        )

    minimum_overlap = 112
    summaries = []
    for node_index, spec in enumerate(NODE_SPECS):
        tracked, partner, _x, _y, _first_kind, _second_kind, partner_exchange = spec
        expected_negative, expected_positive = EXPECTED_NODE_OBSERVATIONS[node_index]
        for first_sign, expected in ((-1, expected_negative), (1, expected_positive)):
            for second_sign in (-1, 1):
                key = (node_index, first_sign, second_sign)
                if observations[key] != expected:
                    raise AssertionError(
                        f"node {node_index} sector {key[1:]} observations changed: "
                        f"{observations[key]}"
                    )
                for item in observations[key]:
                    if item[0] == "both-bad":
                        minimum_overlap = min(minimum_overlap, item[1])

        # The partner edge is exactly transparent on both sides of the
        # tracked factor, including profiles rather than merely mask sizes.
        partner_edges = []
        for first_sign in (-1, 1):
            negative = (node_index, first_sign, -1)
            positive = (node_index, first_sign, 1)
            if records[negative] != records[positive]:
                raise AssertionError(
                    f"node {node_index} partner factor {partner} changes a tracked record"
                )
            exchange = (
                len(set(enumerated[negative]) - set(enumerated[positive])),
                len(set(enumerated[positive]) - set(enumerated[negative])),
            )
            if exchange != (partner_exchange, partner_exchange):
                raise AssertionError(
                    f"node {node_index} partner exchange changed: {exchange}"
                )
            partner_edges.append(exchange)

        tracked_edges = []
        survivor_masks = []
        for second_sign in (-1, 1):
            negative = (node_index, -1, second_sign)
            positive = (node_index, 1, second_sign)
            exchange = (
                len(set(enumerated[negative]) - set(enumerated[positive])),
                len(set(enumerated[positive]) - set(enumerated[negative])),
            )
            if exchange != (2, 2):
                raise AssertionError(
                    f"node {node_index} tracked exchange changed: {exchange}"
                )
            changed = tuple(
                signature
                for signature in signatures
                if records[negative][signature] != records[positive][signature]
            )
            if changed != EXPECTED_CHANGED_SIGNATURES[node_index]:
                raise AssertionError(
                    f"node {node_index} tracked records changed: {changed}"
                )

            counts = []
            masks = []
            for pair in pairs:
                first_mask = pair_common_mask(pair, records[negative])
                second_mask = pair_common_mask(pair, records[positive])
                if first_mask is None or second_mask is None:
                    counts.append(None)
                    masks.append(None)
                    continue
                surviving = first_mask & second_mask
                if not surviving:
                    raise AssertionError(
                        f"node {node_index} tracked edge loses every common direction"
                    )
                counts.append(surviving.bit_count())
                masks.append(surviving)
            if tuple(counts) != EXPECTED_TRACKED_SURVIVORS[node_index]:
                raise AssertionError(
                    f"node {node_index} survivor counts changed: {counts}"
                )
            tracked_edges.append((exchange, changed, tuple(counts)))
            survivor_masks.append(tuple(masks))

        # Both transverse routes have the same exact endpoints and survivor
        # masks: the partner crossing cannot reroute the tracked transition.
        if tracked_edges[0] != tracked_edges[1] or survivor_masks[0] != survivor_masks[1]:
            raise AssertionError(
                f"node {node_index} tracked transition depends on partner side"
            )
        summaries.append(
            (
                node_index,
                tracked,
                partner,
                tuple(partner_edges),
                tracked_edges[0],
                survivor_masks[0],
            )
        )

    if minimum_overlap != EXPECTED_MINIMUM_OVERLAP:
        raise AssertionError(
            f"transition-seed minimum overlap changed: {minimum_overlap}"
        )

    digest = semantic_digest(
        samples,
        factor_signs,
        enumerated,
        records,
        observations,
        box_certificates,
        summaries,
    )
    if EXPECTED_DIGEST and digest != EXPECTED_DIGEST:
        raise AssertionError(f"transition-seed semantic digest changed: {digest}")

    print("PASS 10 unique transverse d/e nodes in wall-exclusive rational boxes")
    print("PASS 40 exact rational chambers joined by certified single-wall segments")
    print("PASS every partner wall is transparent to all six tracked records")
    print("PASS tracked transitions agree on both routes and retain common directions")
    print(f"PASS minimum tracked simultaneously-bad overlap remains {minimum_overlap}")
    print("SEMANTIC", digest)
    print("SCOPE ten isolated seed boxes using six tracked factors; no disk/collar coverage")


if __name__ == "__main__":
    main()
