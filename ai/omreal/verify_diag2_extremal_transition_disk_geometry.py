#!/usr/bin/env python3
"""Exact geometry and link frontier for the parent-187 diagonal-two disk.

The complete standard ``d/e`` slice through catalog parent 187 is a bounded
convex hexagon.  Every primitive residual factor restricts to a polynomial of
total degree at most two on that hexagon.  This verifier constructs the
hexagon from all seventy parent brackets, checks the complete restriction
degree census, and identifies the finite link-determinant frontier attached
to the ten residual occurrences which change a tracked extremal record on
the central ``e`` line.

The link frontier is a reduction target, not residual-cell coverage.  It does
not assert that no other occurrence becomes relevant in a disk component
which is disjoint from the central line.
"""

from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
import hashlib
from itertools import combinations
from math import comb

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled
import DIAG2_PIVOT_REPRESENTATIVE_GRADIENT_VERIFY as representative
import DIAG9_GRAPH_global_factor_census as global_factors
import DIAG9_GRAPH_exact_topes as exact_topes
import verify_diag2_extremal_line_transition_census as line_census
import verify_diag2_extremal_safe_loss_edge as safe_loss
import verify_diag2_near_counterexample_separators as near_separators


PARENT_INDEX = 187
DISK_VARIABLES = (3, 4)  # d,e in the standard a,...,i chart
TRACKED_FACTORS = (
    8_421,
    10_115,
    11_045,
    13_869,
    16_242,
    19_971,
    22_118,
    23_559,
    23_604,
    23_979,
)

EXPECTED_NONCONSTANT_BRACKETS = 30
EXPECTED_VERTICES = {
    (
        ("1347", "2678"),
        Fraction(-47_253_591_589_205_960, 170_245_325_772_061_991),
        Fraction(
            -1_924_192_782_954_754_371_082_332,
            8_550_766_202_685_953_822_316_125,
        ),
    ),
    (
        ("2678", "4578"),
        Fraction(
            -1_030_325_606_505_045_830_575_354_447_080_044,
            4_119_955_780_999_804_748_117_189_157_570_025,
        ),
        Fraction(
            -1_924_192_782_954_754_371_082_332,
            8_550_766_202_685_953_822_316_125,
        ),
    ),
    (
        ("3678", "4578"),
        Fraction(
            195_804_388_564_043_918_859_688,
            15_215_876_029_135_822_618_464_425,
        ),
        Fraction(
            -533_038_856_440_436_369_519_509_201_941_656,
            7_182_909_684_448_130_189_570_634_010_861_625,
        ),
    ),
    (
        ("2567", "3678"),
        Fraction(
            195_804_388_564_043_918_859_688,
            15_215_876_029_135_822_618_464_425,
        ),
        Fraction(
            9_701_361_017_377_585_348_692_326,
            281_522_797_333_298_743_311_269_675,
        ),
    ),
    (
        ("1578", "2567"),
        Fraction(
            -4_582_480_763_211_930_247_067_700_309_910_734,
            23_023_469_384_511_973_614_793_377_145_451_545,
        ),
        Fraction(
            9_701_361_017_377_585_348_692_326,
            281_522_797_333_298_743_311_269_675,
        ),
    ),
    (
        ("1347", "1578"),
        Fraction(-47_253_591_589_205_960, 170_245_325_772_061_991),
        Fraction(
            -423_691_520_855_721_552_151_908,
            15_722_645_891_184_505_480_721_855,
        ),
    ),
}
EXPECTED_X_ZERO_CHORD = (
    (
        ("4578",),
        Fraction(-6_557_186_031_778_323_968_614_336, 80_367_163_670_274_882_423_315_095),
    ),
    (
        ("2567",),
        Fraction(9_701_361_017_377_585_348_692_326, 281_522_797_333_298_743_311_269_675),
    ),
)

EXPECTED_RESIDUAL_DEGREES = {
    (0, 0, 0, 1): 1_990,
    (0, 1, 1, 2): 2_610,
    (1, 0, 1, 2): 2_610,
    (1, 1, 1, 3): 7_185,
    (1, 1, 2, 4): 4_170,
    (1, 2, 2, 5): 3_570,
    (2, 1, 2, 5): 3_570,
    (2, 2, 2, 6): 1_035,
}
EXPECTED_NONCONSTANT_RESIDUALS = 24_750
EXPECTED_TYPE_HISTOGRAM = {
    36: 705,
    38: 270,
    48: 315,
    49: 8_700,
    50: 9_840,
    51: 4_920,
}
EXPECTED_LINK_COUNTS = {
    8_421: 17,
    10_115: 17,
    11_045: 16,
    13_869: 16,
    16_242: 16,
    19_971: 16,
    22_118: 17,
    23_559: 16,
    23_604: 17,
    23_979: 16,
}
EXPECTED_LINK_MEMBERSHIPS = 164
EXPECTED_LINK_UNION = 142
EXPECTED_DISK_LINK_COUNTS = {
    8_421: 16,
    10_115: 16,
    11_045: 16,
    13_869: 16,
    16_242: 15,
    19_971: 16,
    22_118: 17,
    23_559: 15,
    23_604: 17,
    23_979: 16,
}
EXPECTED_DISK_LINK_MEMBERSHIPS = 160
EXPECTED_DISK_LINK_UNION = 139
EXPECTED_CONSTANT_LINKS = {
    8_421: (1_994,),
    10_115: (1_994,),
    11_045: (),
    13_869: (),
    16_242: (13_965,),
    19_971: (),
    22_118: (),
    23_559: (14_611,),
    23_604: (),
    23_979: (),
}
EXPECTED_DIGEST = "8c9a13c315c67da89f45b152b049cef05f71cb00502f592e24bddb69db27f869"

# factor: (unique four-row occurrence, chosen three-row link basis,
# fixed-unit external row for the four circuit coefficients).
LINK_CHARTS = {
    8_421: ((21, 31, 40, 49), (31, 40, 49), 32),
    10_115: ((1, 31, 40, 49), (31, 40, 49), 14),
    11_045: ((1, 28, 33, 49), (1, 28, 49), 19),
    13_869: ((1, 25, 31, 49), (1, 25, 49), 14),
    16_242: ((9, 16, 21, 51), (9, 16, 51), 5),
    19_971: ((1, 16, 31, 40), (16, 31, 40), 10),
    22_118: ((6, 10, 26, 33), (6, 26, 33), 4),
    23_559: ((15, 16, 21, 51), (15, 16, 51), 11),
    23_604: ((2, 28, 30, 49), (2, 30, 49), 5),
    23_979: ((11, 26, 33, 37), (26, 33, 37), 21),
}


def restrict_to_disk(polynomial, base):
    """Substitute d=d0+x and e=e0+y, retaining exact coefficients."""

    answer = {}
    for monomial, coefficient in polynomial.items():
        fixed = Fraction(coefficient)
        for variable, exponent in enumerate(monomial):
            if variable not in DISK_VARIABLES and exponent:
                fixed *= base[variable] ** exponent
        d_degree = monomial[DISK_VARIABLES[0]]
        e_degree = monomial[DISK_VARIABLES[1]]
        for x_degree in range(d_degree + 1):
            for y_degree in range(e_degree + 1):
                term = (
                    fixed
                    * comb(d_degree, x_degree)
                    * base[DISK_VARIABLES[0]] ** (d_degree - x_degree)
                    * comb(e_degree, y_degree)
                    * base[DISK_VARIABLES[1]] ** (e_degree - y_degree)
                )
                key = (x_degree, y_degree)
                answer[key] = answer.get(key, Fraction(0)) + term
    return {
        monomial: coefficient
        for monomial, coefficient in answer.items()
        if coefficient
    }


def degree_profile(polynomial):
    return (
        max((x for x, _y in polynomial), default=0),
        max((y for _x, y in polynomial), default=0),
        max((x + y for x, y in polynomial), default=0),
        len(polynomial),
    )


def evaluate(polynomial, x, y):
    return sum(
        coefficient * x**x_degree * y**y_degree
        for (x_degree, y_degree), coefficient in polynomial.items()
    )


def parent_halfspaces(brackets, base):
    halfspaces = []
    for label, polynomial in brackets.items():
        restriction = restrict_to_disk(polynomial, base)
        if any(x + y > 1 for x, y in restriction):
            raise AssertionError("a parent bracket is nonlinear on the d/e disk")
        constant = restriction.get((0, 0), Fraction(0))
        x_coefficient = restriction.get((1, 0), Fraction(0))
        y_coefficient = restriction.get((0, 1), Fraction(0))
        if not constant:
            raise AssertionError("the parent-187 base lies on a parent boundary")
        if not x_coefficient and not y_coefficient:
            continue
        orientation = 1 if constant > 0 else -1
        halfspaces.append(
            (
                label,
                orientation * constant,
                orientation * x_coefficient,
                orientation * y_coefficient,
            )
        )
    return tuple(halfspaces)


def hexagon_vertices(halfspaces):
    vertices = {}
    for left, right in combinations(halfspaces, 2):
        _left_label, left_constant, left_x, left_y = left
        _right_label, right_constant, right_x, right_y = right
        determinant = left_x * right_y - left_y * right_x
        if not determinant:
            continue
        x = (-left_constant * right_y + left_y * right_constant) / determinant
        y = (-left_x * right_constant + left_constant * right_x) / determinant
        if not all(
            constant + x_coefficient * x + y_coefficient * y >= 0
            for _label, constant, x_coefficient, y_coefficient in halfspaces
        ):
            continue
        active = tuple(
            sorted(
                label
                for label, constant, x_coefficient, y_coefficient in halfspaces
                if constant + x_coefficient * x + y_coefficient * y == 0
            )
        )
        vertices[(x, y)] = active
    return {
        (active, x, y)
        for (x, y), active in vertices.items()
    }


def recession_rays(halfspaces):
    """Return boundary directions in the homogeneous recession cone."""

    rays = set()
    for _label, _constant, x_coefficient, y_coefficient in halfspaces:
        for x, y in (
            (y_coefficient, -x_coefficient),
            (-y_coefficient, x_coefficient),
        ):
            if (x or y) and all(
                a * x + b * y >= 0
                for _other, _c, a, b in halfspaces
            ):
                rays.add((x, y))
    return rays


def x_zero_chord(halfspaces):
    candidates = []
    for label, constant, _x_coefficient, y_coefficient in halfspaces:
        if y_coefficient:
            y = -constant / y_coefficient
            if all(c + b * y >= 0 for _other, c, _a, b in halfspaces):
                active = tuple(
                    sorted(
                        other
                        for other, c, _a, b in halfspaces
                        if c + b * y == 0
                    )
                )
                candidates.append((active, y))
    return tuple(sorted(set(candidates), key=lambda item: item[1]))


def projective_key(polynomial):
    """Normalize a nonzero rational polynomial up to nonzero scale."""

    pivot = polynomial[max(polynomial)]
    return tuple(
        (monomial, coefficient / pivot)
        for monomial, coefficient in sorted(polynomial.items())
    )


def determinant3(matrix):
    return (
        matrix[0][0]
        * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1]
        * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2]
        * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def nonsingular_seed(polynomial):
    """Certify that a line or projective conic has no singular point."""

    degree = max(x + y for x, y in polynomial)
    if degree == 1:
        return bool(
            polynomial.get((1, 0), Fraction(0))
            or polynomial.get((0, 1), Fraction(0))
        )
    if degree != 2:
        return False
    xx = polynomial.get((2, 0), Fraction(0))
    xy = polynomial.get((1, 1), Fraction(0))
    yy = polynomial.get((0, 2), Fraction(0))
    x = polynomial.get((1, 0), Fraction(0))
    y = polynomial.get((0, 1), Fraction(0))
    constant = polynomial.get((0, 0), Fraction(0))
    return determinant3(
        (
            (2 * xx, xy, x),
            (xy, 2 * yy, y),
            (x, y, 2 * constant),
        )
    ) != 0


def substitute_linear(polynomial, variable, constant, slope):
    """Substitute variable=constant+slope*t in a bivariate quadratic."""

    answer = {}
    for (x_degree, y_degree), coefficient in polynomial.items():
        replaced = x_degree if variable == 0 else y_degree
        retained = y_degree if variable == 0 else x_degree
        for power in range(replaced + 1):
            value = (
                coefficient
                * comb(replaced, power)
                * constant ** (replaced - power)
                * slope**power
            )
            degree = retained + power
            answer[degree] = answer.get(degree, Fraction(0)) + value
    return {degree: value for degree, value in answer.items() if value}


def shares_seed_component(seed, other):
    """Decide component sharing for a nonsingular line/conic seed."""

    seed_degree = max(x + y for x, y in seed)
    other_degree = max((x + y for x, y in other), default=0)
    if seed_degree == 2:
        return other_degree == 2 and projective_key(seed) == projective_key(other)
    x = seed.get((1, 0), Fraction(0))
    y = seed.get((0, 1), Fraction(0))
    constant = seed.get((0, 0), Fraction(0))
    if y:
        restricted = substitute_linear(other, 1, -constant / y, -x / y)
    else:
        restricted = substitute_linear(other, 0, -constant / x, -y / x)
    return not restricted


def link_frontier(
    occurrences,
    occurrence_factor,
    factor_polynomials,
    restrictions,
    base_rows,
):
    """Certify sparse global link charts for the ten line-seed circuits."""

    supports_by_factor = defaultdict(list)
    for support in occurrences:
        supports_by_factor[occurrence_factor[support]].append(support)

    symbolic_matrix = global_factors.normalized_matrix()
    parent_brackets = global_factors.bracket_records(symbolic_matrix)
    symbolic_rows = tuple(
        global_factors.normal(symbolic_matrix, triple)
        for triple in exact_topes.TRIPLES
    )
    factor_by_key = {
        global_factors.polynomial_key(polynomial): factor
        for factor, polynomial in enumerate(factor_polynomials)
    }
    if len(factor_by_key) != len(factor_polynomials):
        raise AssertionError("global residual factors are not projectively distinct")

    classification_cache = {}

    def classify(support):
        support = tuple(sorted(support))
        if support not in classification_cache:
            raw = global_factors.primitive(
                global_factors.derived(symbolic_rows, support)
            )
            if not raw:
                raise AssertionError(f"derived determinant {support} is identically zero")
            quotient, units = global_factors.strip_parent_units(
                raw, parent_brackets
            )
            key = global_factors.polynomial_key(quotient)
            unit_key = global_factors.polynomial_key(
                global_factors.constant(1)
            )
            if key == unit_key:
                classification_cache[support] = ("unit", None, units)
            else:
                linked = factor_by_key.get(key)
                if linked is None:
                    raise AssertionError(
                        f"derived determinant {support} has an unknown quotient"
                    )
                classification_cache[support] = ("residual", linked, units)
        return classification_cache[support]

    counts = {}
    disk_counts = {}
    link_sets = {}
    disk_link_sets = {}
    certificates = {}
    union = set()
    disk_union = set()
    for factor in TRACKED_FACTORS:
        supports = supports_by_factor[factor]
        if len(supports) != 1:
            raise AssertionError(
                f"tracked factor {factor} no longer has one labeled occurrence"
            )
        support, basis, external = LINK_CHARTS[factor]
        if supports[0] != support:
            raise AssertionError(f"tracked factor {factor} occurrence changed")
        if not set(basis) < set(support) or external in support:
            raise AssertionError(f"tracked factor {factor} has an invalid link chart")

        certificate = []

        # All four circuit coefficients are exact products of parent units.
        # Thus their signs, and hence the signed four-circuit, cannot change
        # in the uniform parent cell.
        for omitted in support:
            coefficient_support = tuple(
                sorted(tuple(row for row in support if row != omitted) + (external,))
            )
            kind, linked, units = classify(coefficient_support)
            if kind != "unit" or linked is not None:
                raise AssertionError(
                    f"factor {factor} circuit coefficient is not a parent unit"
                )
            value = exact_topes.determinant(
                tuple(base_rows[row] for row in coefficient_support)
            )
            if not value:
                raise AssertionError(f"factor {factor} circuit coefficient vanished")
            certificate.append(
                (
                    "coefficient",
                    coefficient_support,
                    kind,
                    linked,
                    units,
                    1 if value > 0 else -1,
                )
            )

        links = set()
        fixed_units = 0
        for outside in range(56):
            if outside in support:
                continue
            link_support = tuple(sorted(basis + (outside,)))
            kind, linked, units = classify(link_support)
            mapped = occurrence_factor.get(link_support)
            value = exact_topes.determinant(
                tuple(base_rows[row] for row in link_support)
            )
            if not value:
                raise AssertionError(f"factor {factor} link determinant vanished")
            if kind == "unit":
                if mapped is not None:
                    raise AssertionError(
                        f"unit link {link_support} appears in the residual map"
                    )
                fixed_units += 1
            else:
                if mapped != linked:
                    raise AssertionError(
                        f"link {link_support} quotient/map mismatch: {linked}/{mapped}"
                    )
                links.add(linked)
            certificate.append(
                (
                    "link",
                    link_support,
                    kind,
                    linked,
                    units,
                    1 if value > 0 else -1,
                )
            )
        if not fixed_units:
            raise AssertionError(f"factor {factor} link chart has no fixed rank witness")
        counts[factor] = len(links)
        link_sets[factor] = tuple(sorted(links))
        union.update(links)
        disk_links = tuple(
            sorted(
                linked
                for linked in links
                if any(monomial != (0, 0) for monomial in restrictions[linked])
            )
        )
        disk_counts[factor] = len(disk_links)
        disk_link_sets[factor] = disk_links
        disk_union.update(disk_links)
        certificates[factor] = tuple(certificate)
    return (
        counts,
        union,
        link_sets,
        disk_counts,
        disk_union,
        disk_link_sets,
        certificates,
    )


def semantic_digest(
    vertices,
    restrictions,
    link_sets,
    disk_link_sets,
    certificates,
):
    digest = hashlib.sha256()
    digest.update(b"diag2-parent187-de-disk-frontier-v1\0")
    for active, x, y in sorted(vertices, key=repr):
        digest.update(repr((active, x, y)).encode("ascii") + b"\0")
    for factor, polynomial in enumerate(restrictions):
        digest.update(factor.to_bytes(4, "little"))
        for monomial, coefficient in sorted(polynomial.items()):
            digest.update(bytes(monomial))
            digest.update(str(coefficient.numerator).encode("ascii") + b"/")
            digest.update(str(coefficient.denominator).encode("ascii") + b"\0")
    for factor in TRACKED_FACTORS:
        digest.update(repr((factor, LINK_CHARTS[factor])).encode("ascii") + b"\0")
        digest.update(repr(link_sets[factor]).encode("ascii") + b"\0")
        digest.update(repr(disk_link_sets[factor]).encode("ascii") + b"\0")
        digest.update(repr(certificates[factor]).encode("ascii") + b"\0")
    return digest.hexdigest()


def main():
    line_factors = tuple(
        sorted(factor for factor, _kind in line_census.EXPECTED_TRACKED_FACTORS)
    )
    if TRACKED_FACTORS != line_factors:
        raise AssertionError("disk seeds no longer match the complete line census")

    _atlas, by_index, _active = near_separators.load_atlas()
    base, _multipliers = safe_loss.normalize_parent(
        by_index[PARENT_INDEX]["matrix"]
    )
    _residual_representatives, brackets = representative.polynomial_data()
    if len(brackets) != 70:
        raise AssertionError("wrong complete parent-bracket count")

    halfspaces = parent_halfspaces(brackets, base)
    if len(halfspaces) != EXPECTED_NONCONSTANT_BRACKETS:
        raise AssertionError(
            f"wrong nonconstant parent-bracket count: {len(halfspaces)}"
        )
    vertices = hexagon_vertices(halfspaces)
    if vertices != EXPECTED_VERTICES:
        raise AssertionError(f"parent-187 d/e hexagon changed: {vertices}")
    if recession_rays(halfspaces):
        raise AssertionError("parent-187 d/e parent cell is unbounded")
    chord = x_zero_chord(halfspaces)
    if chord != EXPECTED_X_ZERO_CHORD:
        raise AssertionError(f"x=0 chord endpoints changed: {chord}")

    occurrences, occurrence_factor, factor_polynomials = (
        labeled.factor_polynomials()
    )
    _representatives, _stabilizers, alignment, _factor_occurrence, _sizes = (
        labeled.factor_orbit_data(occurrences, occurrence_factor)
    )
    restrictions = tuple(
        restrict_to_disk(polynomial, base) for polynomial in factor_polynomials
    )
    degree_histogram = Counter(map(degree_profile, restrictions))
    if dict(degree_histogram) != EXPECTED_RESIDUAL_DEGREES:
        raise AssertionError(
            f"parent-187 d/e residual degree census changed: {degree_histogram}"
        )
    if len({tuple(sorted(polynomial.items())) for polynomial in restrictions}) != 26_740:
        raise AssertionError("two primitive residual factors acquired one disk restriction")
    nonconstant = tuple(
        factor
        for factor, polynomial in enumerate(restrictions)
        if any(monomial != (0, 0) for monomial in polynomial)
    )
    if len(nonconstant) != EXPECTED_NONCONSTANT_RESIDUALS:
        raise AssertionError("wrong nonconstant residual restriction count")
    if len({projective_key(restrictions[factor]) for factor in nonconstant}) != len(
        nonconstant
    ):
        raise AssertionError("two nonconstant residual equations became proportional")
    type_histogram = Counter(alignment[factor][0] for factor in nonconstant)
    if dict(type_histogram) != EXPECTED_TYPE_HISTOGRAM:
        raise AssertionError(
            f"parent-187 d/e type census changed: {type_histogram}"
        )

    base_rows = exact_topes.derived_rows(safe_loss.integer_matrix(base))
    (
        link_counts,
        link_union,
        link_sets,
        disk_link_counts,
        disk_link_union,
        disk_link_sets,
        certificates,
    ) = link_frontier(
        occurrences,
        occurrence_factor,
        factor_polynomials,
        restrictions,
        base_rows,
    )
    if link_counts != EXPECTED_LINK_COUNTS:
        raise AssertionError(f"tracked link counts changed: {link_counts}")
    if sum(link_counts.values()) != EXPECTED_LINK_MEMBERSHIPS:
        raise AssertionError("tracked link membership count changed")
    if len(link_union) != EXPECTED_LINK_UNION:
        raise AssertionError(
            f"tracked all-triple link union changed: {len(link_union)}"
        )
    if disk_link_counts != EXPECTED_DISK_LINK_COUNTS:
        raise AssertionError(f"tracked disk-link counts changed: {disk_link_counts}")
    if sum(disk_link_counts.values()) != EXPECTED_DISK_LINK_MEMBERSHIPS:
        raise AssertionError("tracked disk-link membership count changed")
    if len(disk_link_union) != EXPECTED_DISK_LINK_UNION:
        raise AssertionError(
            f"tracked nonconstant disk-link union changed: {len(disk_link_union)}"
        )
    constant_links = {
        factor: tuple(sorted(set(link_sets[factor]) - set(disk_link_sets[factor])))
        for factor in TRACKED_FACTORS
    }
    if constant_links != EXPECTED_CONSTANT_LINKS:
        raise AssertionError(f"constant disk-link factors changed: {constant_links}")

    for factor in TRACKED_FACTORS:
        seed = restrictions[factor]
        if not nonsingular_seed(seed):
            raise AssertionError(f"tracked seed {factor} is singular")
        for linked in link_sets[factor]:
            if shares_seed_component(seed, restrictions[linked]):
                raise AssertionError(
                    f"tracked seed {factor} shares a component with link {linked}"
                )

    digest = semantic_digest(
        vertices,
        restrictions,
        link_sets,
        disk_link_sets,
        certificates,
    )
    if EXPECTED_DIGEST is not None and digest != EXPECTED_DIGEST:
        raise AssertionError(f"transition-disk frontier digest changed: {digest}")

    print("PASS parent-187 d/e parent cell is the pinned convex hexagon")
    print("PASS the parent-cell closure is bounded and x=0 has the pinned chord")
    print("PASS all 70 parent brackets are affine or constant on the disk")
    print("PASS 26,740 distinct residual restrictions have total degree at most two")
    print("PASS 24,750 restrictions are nonconstant on the disk")
    print("PASS all 24,750 nonconstant residual equations are nonproportional")
    print("RESIDUAL_DEGREES", tuple(sorted(degree_histogram.items())))
    print("RESIDUAL_TYPES", tuple(sorted(type_histogram.items())))
    print("PASS ten central-line changing factors have one occurrence each")
    print("PASS chosen link bases and circuit signs have exact parent-unit certificates")
    print("PASS seed curves are nonsingular and share no component with a link factor")
    print("GLOBAL_LINK_COUNTS", tuple(sorted(link_counts.items())))
    print("GLOBAL_LINK_UNION", len(link_union))
    print("DISK_LINK_COUNTS", tuple(sorted(disk_link_counts.items())))
    print("DISK_LINK_UNION", len(disk_link_union))
    print("SEMANTIC", digest)
    print("SCOPE exact disk geometry and line-seeded link frontier; no cell coverage")


if __name__ == "__main__":
    main()
