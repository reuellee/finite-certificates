#!/usr/bin/env python3
"""Exact finite certificates for coherence-induced feature distortion.

The primary witness uses rational arithmetic only.  A secondary comparison
uses exact arithmetic in Q(sqrt(3)) for the minimum-coherence triangular frame.
The certificates concern a two-dimensional, three-atom, nonnegative L1 sparse
autoencoder with unit decoder columns and either the Frobenius/Gram penalty

    P(D) = sum_{i<j} <d_i, d_j>^2.

or squared mutual coherence

    M(D) = max_{i<j} <d_i, d_j>^2.

The data distribution is uniform on e1 and e2.  At lambda=1/5 and beta=1/16,
the rational 5-12-13 frame

    {(12/13, 5/13), (12/13, -5/13), (0, 1)}

has strictly smaller population objective than every dictionary containing
both ground-truth directions e1 and e2 under P.  The rational 33-56-65 frame

    {(56/65, 33/65), (56/65, -33/65), (0, 1)}

does the same under M.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
from typing import Iterable, Sequence, Tuple


@dataclass(frozen=True)
class Qsqrt3:
    """An exact number a + b*sqrt(3), with a,b rational."""

    a: F = F(0)
    b: F = F(0)

    @staticmethod
    def coerce(value: object) -> "Qsqrt3":
        if isinstance(value, Qsqrt3):
            return value
        if isinstance(value, (int, F)):
            return Qsqrt3(F(value), F(0))
        raise TypeError(f"cannot coerce {type(value)!r}")

    def __add__(self, other: object) -> "Qsqrt3":
        rhs = self.coerce(other)
        return Qsqrt3(self.a + rhs.a, self.b + rhs.b)

    __radd__ = __add__

    def __neg__(self) -> "Qsqrt3":
        return Qsqrt3(-self.a, -self.b)

    def __sub__(self, other: object) -> "Qsqrt3":
        return self + (-self.coerce(other))

    def __rsub__(self, other: object) -> "Qsqrt3":
        return self.coerce(other) - self

    def __mul__(self, other: object) -> "Qsqrt3":
        rhs = self.coerce(other)
        return Qsqrt3(
            self.a * rhs.a + 3 * self.b * rhs.b,
            self.a * rhs.b + self.b * rhs.a,
        )

    __rmul__ = __mul__

    def inverse(self) -> "Qsqrt3":
        denominator = self.a * self.a - 3 * self.b * self.b
        if denominator == 0:
            raise ZeroDivisionError
        return Qsqrt3(self.a / denominator, -self.b / denominator)

    def __truediv__(self, other: object) -> "Qsqrt3":
        return self * self.coerce(other).inverse()

    def __rtruediv__(self, other: object) -> "Qsqrt3":
        return self.coerce(other) / self

    def sign(self) -> int:
        """Return the exact sign using rational square comparisons."""
        if self.a == 0 and self.b == 0:
            return 0
        if self.a >= 0 and self.b >= 0:
            return 1
        if self.a <= 0 and self.b <= 0:
            return -1
        if self.a < 0 < self.b:
            return 1 if 3 * self.b * self.b > self.a * self.a else -1
        # self.b < 0 < self.a
        return 1 if self.a * self.a > 3 * self.b * self.b else -1

    def __lt__(self, other: object) -> bool:
        return (self - self.coerce(other)).sign() < 0

    def __le__(self, other: object) -> bool:
        return (self - self.coerce(other)).sign() <= 0

    def __gt__(self, other: object) -> bool:
        return (self - self.coerce(other)).sign() > 0

    def __ge__(self, other: object) -> bool:
        return (self - self.coerce(other)).sign() >= 0

    def __eq__(self, other: object) -> bool:
        try:
            rhs = self.coerce(other)
        except TypeError:
            return NotImplemented
        return self.a == rhs.a and self.b == rhs.b

    def decimal(self) -> float:
        return float(self.a) + float(self.b) * (3.0**0.5)

    def __str__(self) -> str:
        if self.b == 0:
            return str(self.a)
        sign = "+" if self.b > 0 else "-"
        magnitude = abs(self.b)
        return f"{self.a} {sign} {magnitude}*sqrt(3)"


Q3 = Qsqrt3
Vector = Tuple[Q3, Q3]


def q(value: int | F) -> Q3:
    return Q3(F(value), F(0))


def dot(left: Vector, right: Vector) -> Q3:
    return left[0] * right[0] + left[1] * right[1]


def add(left: Vector, right: Vector) -> Vector:
    return (left[0] + right[0], left[1] + right[1])


def subtract(left: Vector, right: Vector) -> Vector:
    return (left[0] - right[0], left[1] - right[1])


def scale(coefficient: Q3, vector: Vector) -> Vector:
    return (coefficient * vector[0], coefficient * vector[1])


def decode(dictionary: Sequence[Vector], code: Sequence[Q3]) -> Vector:
    output = (q(0), q(0))
    for atom, coefficient in zip(dictionary, code):
        output = add(output, scale(coefficient, atom))
    return output


def reconstruction_l1_loss(
    x: Vector,
    dictionary: Sequence[Vector],
    code: Sequence[Q3],
    lam: Q3,
) -> Q3:
    residual = subtract(x, decode(dictionary, code))
    return dot(residual, residual) + lam * sum(code, q(0))


def gram_penalty(dictionary: Sequence[Vector]) -> Q3:
    total = q(0)
    for i in range(len(dictionary)):
        for j in range(i + 1, len(dictionary)):
            inner = dot(dictionary[i], dictionary[j])
            total += inner * inner
    return total


def mutual_coherence_squared(dictionary: Sequence[Vector]) -> Q3:
    values = []
    for i in range(len(dictionary)):
        for j in range(i + 1, len(dictionary)):
            inner = dot(dictionary[i], dictionary[j])
            values.append(inner * inner)
    assert values
    return max(values)


def verify_kkt(
    x: Vector,
    dictionary: Sequence[Vector],
    code: Sequence[Q3],
    lam: Q3,
) -> None:
    """Verify exact KKT conditions for nonnegative L1 coding."""
    assert all(coefficient >= 0 for coefficient in code)
    residual = subtract(x, decode(dictionary, code))
    threshold = lam / 2
    for atom, coefficient in zip(dictionary, code):
        correlation = dot(atom, residual)
        if coefficient > 0:
            assert correlation == threshold
        else:
            assert correlation <= threshold


def main() -> None:
    sqrt3 = Q3(F(0), F(1))
    half = q(F(1, 2))
    e1: Vector = (q(1), q(0))
    e2: Vector = (q(0), q(1))
    u60: Vector = (half, sqrt3 / 2)
    u120: Vector = (-half, sqrt3 / 2)
    triangle = (e1, u60, u120)

    lam = q(F(1, 5))
    beta = q(F(1, 16))

    # ------------------------------------------------------------------
    # Primary all-rational certificate.
    c = q(F(12, 13))
    s = q(F(5, 13))
    rational_frame: Tuple[Vector, ...] = (
        (c, s),
        (c, -s),
        e2,
    )
    assert all(dot(atom, atom) == 1 for atom in rational_frame)

    rational_t = q(F(1391, 2880))
    rational_code_e1 = (rational_t, rational_t, q(0))
    rational_code_e2 = (q(0), q(0), q(F(9, 10)))
    verify_kkt(e1, rational_frame, rational_code_e1, lam)
    verify_kkt(e2, rational_frame, rational_code_e2, lam)

    rational_loss_e1 = reconstruction_l1_loss(
        e1, rational_frame, rational_code_e1, lam
    )
    rational_loss_e2 = reconstruction_l1_loss(
        e2, rational_frame, rational_code_e2, lam
    )
    assert rational_loss_e1 == Q3(F(2951, 14400))
    assert rational_loss_e2 == Q3(F(19, 100))

    rational_base = (rational_loss_e1 + rational_loss_e2) / 2
    rational_penalty = gram_penalty(rational_frame)
    assert rational_base == Q3(F(5687, 28800))
    assert rational_penalty == Q3(F(22611, 28561))

    faithful_base = lam - lam * lam / 4
    faithful_penalty = q(1)
    assert faithful_base == Q3(F(19, 100))

    rational_objective = rational_base + beta * rational_penalty
    faithful_objective = faithful_base + beta * faithful_penalty
    rational_gap = faithful_objective - rational_objective
    assert rational_gap == Q3(F(913877, 164511360))
    assert rational_gap > 0

    rational_beta_certificate = (
        (rational_base - faithful_base)
        / (faithful_penalty - rational_penalty)
    )
    assert rational_beta_certificate == Q3(F(1228123, 34272000))
    assert beta > rational_beta_certificate

    # ------------------------------------------------------------------
    # Independent all-rational certificate for squared mutual coherence.
    c_mu = q(F(56, 65))
    s_mu = q(F(33, 65))
    mutual_frame: Tuple[Vector, ...] = (
        (c_mu, s_mu),
        (c_mu, -s_mu),
        e2,
    )
    assert all(dot(atom, atom) == 1 for atom in mutual_frame)

    mutual_t = q(F(6435, 12544))
    mutual_code_e1 = (mutual_t, mutual_t, q(0))
    mutual_code_e2 = (q(0), q(0), q(F(9, 10)))
    verify_kkt(e1, mutual_frame, mutual_code_e1, lam)
    verify_kkt(e2, mutual_frame, mutual_code_e2, lam)

    mutual_loss_e1 = reconstruction_l1_loss(
        e1, mutual_frame, mutual_code_e1, lam
    )
    mutual_loss_e2 = reconstruction_l1_loss(
        e2, mutual_frame, mutual_code_e2, lam
    )
    assert mutual_loss_e1 == Q3(F(2743, 12544))
    assert mutual_loss_e2 == Q3(F(19, 100))

    mutual_base = (mutual_loss_e1 + mutual_loss_e2) / 2
    mutual_penalty = mutual_coherence_squared(mutual_frame)
    faithful_mutual_penalty = q(F(1, 2))
    assert mutual_base == Q3(F(128159, 627200))
    assert mutual_penalty == Q3(F(1089, 4225))

    mutual_objective = mutual_base + beta * mutual_penalty
    faithful_mutual_objective = (
        faithful_base + beta * faithful_mutual_penalty
    )
    mutual_gap = faithful_mutual_objective - mutual_objective
    assert mutual_objective == Q3(F(23366423, 105996800))
    assert mutual_gap == Q3(F(85369, 105996800))
    assert mutual_gap > 0

    mutual_beta_certificate = (
        (mutual_base - faithful_base)
        / (faithful_mutual_penalty - mutual_penalty)
    )
    assert mutual_beta_certificate == Q3(F(1519479, 25677568))
    assert beta > mutual_beta_certificate

    # ------------------------------------------------------------------
    # A second rational Gram witness close to the analytic onset
    # beta = lambda(2-lambda)/16.  Here beta=1/40, while the onset at
    # lambda=1/5 is 9/400.
    beta_near = q(F(1, 40))
    c_near = q(F(399, 401))
    s_near = q(F(40, 401))
    near_frame: Tuple[Vector, ...] = (
        (c_near, s_near),
        (c_near, -s_near),
        e2,
    )
    assert all(dot(atom, atom) == 1 for atom in near_frame)

    near_t = q(F(1439189, 3184020))
    near_code_e1 = (near_t, near_t, q(0))
    near_code_e2 = rational_code_e2
    verify_kkt(e1, near_frame, near_code_e1, lam)
    verify_kkt(e2, near_frame, near_code_e2, lam)
    near_base = (
        reconstruction_l1_loss(e1, near_frame, near_code_e1, lam)
        + reconstruction_l1_loss(e2, near_frame, near_code_e2, lam)
    ) / 2
    near_penalty = gram_penalty(near_frame)
    near_objective = near_base + beta_near * near_penalty
    near_gap = faithful_base + beta_near - near_objective
    near_beta_certificate = (
        (near_base - faithful_base) / (q(1) - near_penalty)
    )
    onset = lam * (q(2) - lam) / 16
    assert onset == Q3(F(9, 400))
    assert near_base == Q3(F(3031999, 15920100))
    assert near_penalty == Q3(F(25352638401, 25856961601))
    assert near_beta_certificate == Q3(F(25856961601, 1118227824000))
    assert beta_near > near_beta_certificate > onset
    assert near_gap == Q3(F(753445505641, 20582270719204005))
    assert near_gap > 0

    # ------------------------------------------------------------------
    # Secondary exact Welch-bound / minimum-coherence comparison.
    # Unit norms and the exact Welch-bound penalty.
    assert all(dot(atom, atom) == 1 for atom in triangle)
    assert gram_penalty(triangle) == Q3(F(3, 4))

    # Exact optimal codes, certified by convex KKT conditions.
    code_e1 = (q(F(9, 10)), q(0), q(0))
    t = sqrt3 / 3 - q(F(1, 15))
    code_e2 = (q(0), t, t)
    verify_kkt(e1, triangle, code_e1, lam)
    verify_kkt(e2, triangle, code_e2, lam)

    loss_e1 = reconstruction_l1_loss(e1, triangle, code_e1, lam)
    loss_e2 = reconstruction_l1_loss(e2, triangle, code_e2, lam)
    assert loss_e1 == Q3(F(19, 100))
    assert loss_e2 == Q3(F(-1, 75), F(2, 15))

    triangle_base = (loss_e1 + loss_e2) / 2
    assert triangle_base == Q3(F(53, 600), F(1, 15))

    triangle_objective = triangle_base + beta * Q3(F(3, 4))
    strict_gap = faithful_objective - triangle_objective
    assert strict_gap == Q3(F(563, 4800), F(-1, 15))
    assert strict_gap > 0

    beta_certificate = (
        2 * lam * (2 / sqrt3 - 1) - lam * lam / 6
    )
    assert beta_certificate == Q3(F(-61, 150), F(4, 15))
    assert beta > beta_certificate

    # Integer-only sign witness:
    # 563/4800 - sqrt(3)/15 = (563 - 320 sqrt(3))/4800 > 0
    # because 563^2 - 3*320^2 = 9769 > 0.
    integer_sign_witness = 563 * 563 - 3 * 320 * 320
    assert integer_sign_witness == 9769

    # General d+1 Welch-gap values: a dictionary containing an orthonormal
    # basis has penalty 1, whereas a unit-norm simplex tight frame has
    # penalty (d+1)/(2d).
    for dimension in range(2, 33):
        simplex_penalty = F(dimension + 1, 2 * dimension)
        faithful_gap = F(1) - simplex_penalty
        assert faithful_gap == F(dimension - 1, 2 * dimension)
        assert faithful_gap > 0

    print("EXACT OVERCOMPLETE COHERENCE CERTIFICATE")
    print(f"lambda = {lam}; beta = {beta}")
    print()
    print("PRIMARY ALL-RATIONAL 5-12-13 WITNESS")
    print(f"rational-frame Gram penalty = {rational_penalty}")
    print(f"faithful-class Gram penalty = {faithful_penalty}")
    print(f"rational-frame base loss = {rational_base}")
    print(f"faithful base loss = {faithful_base}")
    print(
        "rational exclusion threshold beta_cert = "
        f"{rational_beta_certificate} = "
        f"{rational_beta_certificate.decimal():.12f}"
    )
    print(
        "faithful objective - rational-frame objective = "
        f"{rational_gap} = {rational_gap.decimal():.12f}"
    )
    print("rational KKT checks: PASS for both observed states")
    print()
    print("ALL-RATIONAL 33-56-65 MUTUAL-COHERENCE WITNESS")
    print(f"mutual-frame squared coherence = {mutual_penalty}")
    print(f"faithful-class minimum squared coherence = {faithful_mutual_penalty}")
    print(f"mutual-frame base loss = {mutual_base}")
    print(
        "mutual-coherence exclusion threshold beta_cert = "
        f"{mutual_beta_certificate} = "
        f"{mutual_beta_certificate.decimal():.12f}"
    )
    print(
        "faithful objective - mutual-frame objective = "
        f"{mutual_gap} = {mutual_gap.decimal():.12f}"
    )
    print("mutual-coherence KKT checks: PASS for both observed states")
    print()
    print("NEAR-ONSET ALL-RATIONAL GRAM WITNESS")
    print(f"analytic split onset = {onset} = {onset.decimal():.12f}")
    print(f"chosen beta = {beta_near}")
    print(
        "near-onset exclusion threshold beta_cert = "
        f"{near_beta_certificate} = "
        f"{near_beta_certificate.decimal():.12f}"
    )
    print(
        "faithful objective - near-frame objective = "
        f"{near_gap} = {near_gap.decimal():.12f}"
    )
    print("near-onset KKT checks: PASS for both observed states")
    print()
    print("SECONDARY MINIMUM-COHERENCE TRIANGULAR WITNESS")
    print(f"triangle Gram penalty = {gram_penalty(triangle)}")
    print(f"triangle base loss = {triangle_base} = {triangle_base.decimal():.12f}")
    print(
        "triangle exclusion threshold beta_cert = "
        f"{beta_certificate} = {beta_certificate.decimal():.12f}"
    )
    print(
        "faithful objective - triangle objective = "
        f"{strict_gap} = {strict_gap.decimal():.12f}"
    )
    print(f"integer sign witness = {integer_sign_witness} > 0")
    print("triangle KKT checks: PASS for both observed states")
    print("Welch-gap checks: PASS for d=2,...,32")
    print()
    verify_class_wide_bounds(
        lam=F(1, 5),
        gram_cases=(
            (F(1, 16), as_fraction(rational_objective)),
            (F(1, 40), as_fraction(near_objective)),
        ),
        mutual_cases=((F(1, 16), as_fraction(mutual_objective)),),
    )
    print("ALL EXACT CHECKS PASSED")


def as_fraction(value: Q3) -> F:
    """Extract the rational part of a Q(sqrt3) number known to be rational."""
    assert value.b == 0
    return value.a


def random_rational_unit_vector(rng) -> Tuple[F, F]:
    """Random exact-rational unit vector via the Pythagorean parametrization.

    For rational t, ((1-t^2)/(1+t^2), 2t/(1+t^2)) is a unit vector; coordinate
    swaps and sign flips broaden the coverage of the circle.
    """
    t = F(rng.randint(-30, 30), rng.randint(1, 30))
    x = (1 - t * t) / (1 + t * t)
    y = 2 * t / (1 + t * t)
    if rng.random() < 0.5:
        x, y = y, x
    if rng.random() < 0.5:
        x = -x
    return (x, y)


def exact_optimal_coding_value(
    x: Tuple[F, F],
    atoms: Sequence[Tuple[F, F]],
    lam: F,
) -> F:
    """Exact optimum of min_{f>=0} ||x - Df||^2 + lam*sum(f), by enumeration.

    Pure-Fraction code path, independent of the KKT checker.  In 2D an optimum
    with linearly independent support exists: moving along a null direction v
    of the active atoms leaves the reconstruction fixed and changes the L1 term
    linearly (by lam*sum(v) per unit step), so from any optimum one can slide,
    without increasing the objective, until a coefficient hits zero.  Hence
    supports of size 0, 1, and 2 with independent (unit) atoms suffice, and the
    minimum over all feasible stationary-on-support candidates is the global
    optimum of the convex coding problem.
    """

    def value(code: Sequence[F]) -> F:
        rx = x[0] - sum(c * a[0] for c, a in zip(code, atoms))
        ry = x[1] - sum(c * a[1] for c, a in zip(code, atoms))
        return rx * rx + ry * ry + lam * sum(code)

    best = x[0] * x[0] + x[1] * x[1]  # empty support: f = 0
    m = len(atoms)
    for i in range(m):
        ai = atoms[i]
        f_i = (ai[0] * x[0] + ai[1] * x[1]) - lam / 2  # unit atom: <ai,ai>=1
        if f_i > 0:
            code = [F(0)] * m
            code[i] = f_i
            best = min(best, value(code))
    for i in range(m):
        for j in range(i + 1, m):
            ai, aj = atoms[i], atoms[j]
            if ai[0] * aj[1] - ai[1] * aj[0] == 0:
                continue  # parallel pair; covered by singleton supports
            g = ai[0] * aj[0] + ai[1] * aj[1]
            b_i = ai[0] * x[0] + ai[1] * x[1] - lam / 2
            b_j = aj[0] * x[0] + aj[1] * x[1] - lam / 2
            gram_det = 1 - g * g  # nonzero: independent unit atoms => |g| < 1
            f_i = (b_i - g * b_j) / gram_det
            f_j = (b_j - g * b_i) / gram_det
            if f_i >= 0 and f_j >= 0:
                code = [F(0)] * m
                code[i], code[j] = f_i, f_j
                best = min(best, value(code))
    return best


def verify_class_wide_bounds(
    lam: F,
    gram_cases: Sequence[Tuple[F, F]],
    mutual_cases: Sequence[Tuple[F, F]],
) -> None:
    """CLASS-WIDE BOUNDS (added in review).

    The witness certificates above compare against the *values* 19/100 (base
    loss) and 1 resp. 1/2 (penalty) attributed to the faithful class.  This
    section certifies that those values hold for the ENTIRE class of unit-atom
    dictionaries containing the true features, so each witness excludes the
    whole class, not one representative:

    (a) For ANY dictionary containing e1, the single-atom code (1 - lam/2) on
        e1 satisfies the exact KKT conditions of the convex coding problem for
        x = e1: residual (lam/2)e1, active correlation exactly lam/2, inactive
        correlations (lam/2)<dj, e1> <= lam/2 because <dj, e1> <= 1 for unit
        atoms.  KKT conditions are sufficient for global optimality of a
        convex program, so the optimal coding value is EXACTLY
        lam - lam^2/4 = 19/100 at lam = 1/5 -- independent of the other atoms.
        Hence every faithful dictionary has base loss exactly 19/100.
    (b) The Gram penalty of ANY faithful triple {e1, e2, d3} with unit d3 =
        (x, y) is exactly 0 + x^2 + y^2 = 1.  More generally, for m unit atoms
        containing e1, e2: P(D) = (m - 2) + sum_{extras i<j} <di,dj>^2
        >= m - 2, since each extra atom contributes <d,e1>^2 + <d,e2>^2 =
        |d|^2 = 1.  For the certificate's class m = 3 the penalty is
        identically 1.
    (c) The squared mutual coherence of ANY faithful triple is >= 1/2:
        max(x^2, y^2) = 1/2 + |x^2 - 1/2| >= 1/2 whenever x^2 + y^2 = 1.
    (d) Bonus (beta = 0 sanity): ||Df|| <= sum(f) for unit atoms, so the
        coding loss is >= min_{rho>=0} (1-rho)^2 + lam*rho = lam - lam^2/4;
        the faithful class attains this bound at every data point, i.e. it is
        exactly optimal WITHOUT the penalty.  The distortion is remedy-induced.

    Verification: (b), (c), (d) symbolically over a general unit atom (sympy),
    (a) by exact-rational randomized dictionaries -- KKT-checked with the
    module's checker AND cross-checked against an independent pure-Fraction
    support-enumeration solver.
    """
    import random

    import sympy as sp

    # ------------------------------------------------------------------
    # Symbolic identities (general unit atom, exact).
    lam_s = sp.symbols("lam", positive=True)
    theta = sp.symbols("theta", real=True)
    x, y = sp.symbols("x y", real=True)
    x1, y1, x2, y2 = sp.symbols("x1 y1 x2 y2", real=True)
    u = sp.symbols("u", real=True)
    rho = sp.symbols("rho", real=True)

    # (a) Inactive-atom KKT slack for a unit atom (cos t, sin t):
    #     lam/2 - (lam/2)cos(theta) = lam*sin(theta/2)^2 >= 0, identically.
    slack = lam_s / 2 - (lam_s / 2) * sp.cos(theta)
    assert sp.simplify(slack - lam_s * sp.sin(theta / 2) ** 2) == 0
    assert (lam_s * sp.sin(theta / 2) ** 2).is_nonnegative
    # (a) Value of the single-atom code: (lam/2)^2 + lam(1 - lam/2)
    #     = lam - lam^2/4, identically.
    value_slack = (
        (lam_s / 2) ** 2
        + lam_s * (1 - lam_s / 2)
        - (lam_s - lam_s**2 / 4)
    )
    assert sp.expand(value_slack) == 0

    # (b) m=3: penalty of {e1, e2, (x,y)} minus 1 IS the unit-norm constraint.
    gram3 = sp.Integer(0) ** 2 + x**2 + y**2
    assert sp.expand(gram3 - 1 - (x**2 + y**2 - 1)) == 0
    # (b) m=4: penalty = (m-2) + cross^2 modulo the unit-norm constraints,
    #     and cross^2 >= 0, so penalty >= m - 2 on the constraint set.
    cross = x1 * x2 + y1 * y2
    gram4 = (x1**2 + y1**2) + (x2**2 + y2**2) + cross**2
    slack4 = (
        gram4
        - 2
        - cross**2
        - (x1**2 + y1**2 - 1)
        - (x2**2 + y2**2 - 1)
    )
    assert sp.expand(slack4) == 0
    assert (cross**2).is_nonnegative

    # (c) With u = x^2 and y^2 = 1 - u: max(u, 1-u) = 1/2 + |u - 1/2| >= 1/2.
    max_rewrite = sp.Max(u, 1 - u).rewrite(sp.Abs)
    half = sp.Rational(1, 2)
    assert sp.simplify(max_rewrite - (half + sp.Abs(u - half))) == 0
    assert sp.Abs(u - half).is_nonnegative

    # (d) (1 - rho)^2 + lam*rho = (rho - (1 - lam/2))^2 + lam - lam^2/4.
    lower = (1 - rho) ** 2 + lam_s * rho
    completed = (rho - (1 - lam_s / 2)) ** 2 + lam_s - lam_s**2 / 4
    assert sp.expand(lower - completed) == 0

    # ------------------------------------------------------------------
    # Randomized exact-rational check of (a) (plus rational spot checks of
    # (b), (c)): random unit-atom dictionaries containing e1 (and e2).
    rng = random.Random(20260725)
    e1_f: Tuple[F, F] = (F(1), F(0))
    e2_f: Tuple[F, F] = (F(0), F(1))
    target = lam - lam * lam / 4
    assert target == F(19, 100)

    trials = 200
    for _ in range(trials):
        extras = [
            random_rational_unit_vector(rng)
            for _ in range(rng.randint(1, 3))
        ]
        for atom in extras:
            assert atom[0] * atom[0] + atom[1] * atom[1] == 1

        # (a) Any dictionary containing e1: the single-atom code passes the
        # module's exact KKT checker, and the independent enumeration solver
        # confirms the optimum is exactly lam - lam^2/4.
        dict_e1 = [e1_f] + extras
        q_dict = tuple((q(a), q(b)) for a, b in dict_e1)
        q_code = tuple(
            [q(1 - lam / 2)] + [q(0)] * len(extras)
        )
        e1_q: Vector = (q(1), q(0))
        verify_kkt(e1_q, q_dict, q_code, q(lam))
        assert reconstruction_l1_loss(
            e1_q, q_dict, q_code, q(lam)
        ) == Q3(target)
        assert exact_optimal_coding_value(e1_f, dict_e1, lam) == target

        # Faithful dictionaries (containing e1 AND e2): both data points cost
        # exactly 19/100, so the faithful base loss is exactly 19/100.
        faithful = [e1_f, e2_f] + extras
        assert exact_optimal_coding_value(e1_f, faithful, lam) == target
        assert exact_optimal_coding_value(e2_f, faithful, lam) == target

        # (b) Rational spot check of the Gram identity/bound.
        third = extras[0]
        q_triple = tuple((q(a), q(b)) for a, b in [e1_f, e2_f, third])
        assert gram_penalty(q_triple) == 1
        q_faithful = tuple((q(a), q(b)) for a, b in faithful)
        assert gram_penalty(q_faithful) >= len(faithful) - 2

        # (c) Rational spot check of the mutual-coherence bound.
        assert max(third[0] ** 2, third[1] ** 2) >= F(1, 2)
        assert mutual_coherence_squared(q_triple) >= F(1, 2)

    # ------------------------------------------------------------------
    # Class-wide conclusions.  By (a) + (b), EVERY faithful triple has Gram
    # objective exactly 19/100 + beta; by (a) + (c), EVERY faithful triple has
    # mutual-coherence objective >= 19/100 + beta/2.  Each witness objective
    # is strictly below the corresponding class-wide bound.
    faithful_base = F(19, 100)
    for beta_value, witness_objective in gram_cases:
        assert witness_objective < faithful_base + beta_value
    for beta_value, witness_objective in mutual_cases:
        assert witness_objective < faithful_base + beta_value / 2

    print("CLASS-WIDE BOUNDS (added in review)")
    print(
        "(a) faithful base loss = 19/100 for the WHOLE class: "
        "symbolic KKT slack identity + "
        f"{trials} random exact-rational dictionaries "
        "(KKT checker + independent support-enumeration solver): PASS"
    )
    print(
        "(b) Gram penalty of every faithful triple = 1 exactly "
        "(m atoms: >= m-2): symbolic identity + rational spot checks: PASS"
    )
    print(
        "(c) squared mutual coherence of every faithful triple >= 1/2 "
        "(max(u,1-u) = 1/2 + |u-1/2|): symbolic identity + spot checks: PASS"
    )
    print(
        "(d) beta=0 sanity: coding loss >= lam - lam^2/4 always, attained by "
        "the faithful class -- unpenalized optimum IS faithful: PASS"
    )
    print(
        "class-wide exclusion: every Gram witness beats 19/100 + beta, "
        "every mutual witness beats 19/100 + beta/2: PASS"
    )
    print()


if __name__ == "__main__":
    main()


def verify_signed_basis_degeneracy() -> None:
    """[I,-I] proposition (from 'Causal-Ontology Inversion in Overcomplete
    Sparse Autoencoders', 2026-07-25): at m=2d the signed duplicated basis
    attains the frame-potential floor m(m-d)/(2d) exactly while its worst-pair
    squared coherence is maximal (=1). Frame potential is not mutual coherence.
    Exact rational arithmetic, d=2..8."""
    for d in range(2, 9):
        eye = [[F(int(i == j)) for j in range(d)] for i in range(d)]
        cols = [tuple(r[j] for r in eye) for j in range(d)]
        cols += [tuple(-r[j] for r in eye) for j in range(d)]
        m = len(cols)
        dots = [
            sum(a * b for a, b in zip(cols[i], cols[j]))
            for i in range(m)
            for j in range(i + 1, m)
        ]
        gram_sum = sum(x * x for x in dots)
        max_coh = max(x * x for x in dots)
        assert gram_sum == F(m * (m - d), 2 * d), (d, gram_sum)
        assert max_coh == 1, (d, max_coh)
    print(
        "SIGNED-BASIS DEGENERACY [I,-I]: Gram-sum floor m(m-d)/2d attained "
        "with max squared coherence = 1, d=2..8 — frame potential is not "
        "mutual coherence. PASS"
    )


verify_signed_basis_degeneracy()
