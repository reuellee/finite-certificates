#!/usr/bin/env python3
"""Exact factored rank-drop branch for the diagonal-three hard canary.

This verifier starts from the stored integer residual equations.  It checks
the smallest ``ae`` residual-Jacobian minor before and after the two exact
graph eliminations.  The output is a component-decorated next branch, not a
unit-ideal or noncompactness certificate.
"""

from __future__ import annotations

import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY as triples  # noqa: E402
import verify_diag3_triple_boundary_stratification as boundary  # noqa: E402


def scale(polynomial, coefficient):
    return {
        monomial: coefficient * value
        for monomial, value in polynomial.items()
        if coefficient * value
    }


def term(coefficient, **powers):
    monomial = [0] * len(boundary.VARIABLES)
    for variable, exponent in powers.items():
        monomial[boundary.VARIABLES.index(variable)] = exponent
    return {tuple(monomial): coefficient}


def sum_terms(terms):
    answer = {}
    for polynomial in terms:
        answer = boundary.add(answer, polynomial)
    return answer


EXPECTED_P = sum_terms(
    (
        term(-1, c=1, d=1, f=1, h=1),
        term(1, c=1, d=1, f=1, i=1),
        term(1, c=1, d=1, h=1, i=1),
        term(-1, c=1, d=1, i=2),
        term(-1, c=1, f=2, g=1, h=1),
        term(1, c=1, f=2, h=1),
        term(1, c=1, f=1, g=1, h=1, i=1),
        term(-1, c=1, f=1, h=1, i=1),
        term(-1, d=1, f=1, g=1, h=1, i=1),
        term(1, d=1, f=1, i=2),
        term(1, f=2, g=2, h=1),
        term(-1, f=2, g=1, i=1),
    )
)


def census(polynomial):
    return len(polynomial), min(map(sum, polynomial)), max(map(sum, polynomial))


def main():
    if boundary.sha256(boundary.SYSTEM) != boundary.SYSTEM_SHA256:
        raise AssertionError("stored critical system hash changed")
    payload = json.loads(boundary.SYSTEM.read_text(encoding="ascii"))
    residual = tuple(
        boundary.decode_terms(record["terms"])
        for record in payload["equations"][:3]
    )
    walls = boundary.parent_wall_map()
    t = boundary.subtract(boundary.coordinate(8), boundary.coordinate(5))
    u = walls[boundary.PARENT_LOCALIZER]

    def eliminate_b(polynomial):
        constant_part, coefficient = boundary.split_linear(
            polynomial, boundary.HEIGHT
        )
        return boundary.add(
            boundary.multiply(t, constant_part),
            boundary.multiply(u, coefficient),
        )

    reduced_two, reduced_three = tuple(
        eliminate_b(polynomial) for polynomial in residual[1:]
    )
    a_two, b_two = boundary.split_linear(reduced_two, 0)
    a_three, b_three = boundary.split_linear(reduced_three, 0)
    expected_b_two = boundary.multiply(
        boundary.multiply(walls["2357"], walls["2458"]),
        eliminate_b(walls["1267"]),
    )
    if b_two != expected_b_two:
        raise AssertionError("the parent-unit a pivot changed")

    rank_drop = boundary.subtract(
        boundary.multiply(
            boundary.derivative(reduced_two, 0),
            boundary.derivative(reduced_three, 4),
        ),
        boundary.multiply(
            boundary.derivative(reduced_two, 4),
            boundary.derivative(reduced_three, 0),
        ),
    )
    rank_constant, rank_a = boundary.split_linear(rank_drop, 0)
    expected_rank_a = boundary.multiply(
        boundary.multiply(
            boundary.multiply(walls["2357"], walls["2458"]), t
        ),
        EXPECTED_P,
    )
    if rank_a != expected_rank_a:
        raise AssertionError("the factored ae rank-drop coefficient changed")
    if census(rank_drop) != (341, 6, 9):
        raise AssertionError("the ae rank-drop census changed")
    if census(EXPECTED_P) != (12, 4, 5):
        raise AssertionError("the primitive P census changed")
    if any(
        monomial[index]
        for monomial in EXPECTED_P
        for index in (0, boundary.HEIGHT, 4)
    ):
        raise AssertionError("P unexpectedly depends on a, b, or e")

    parent_divisors_p = tuple(
        label
        for label, wall in walls.items()
        if triples.exact_divide(EXPECTED_P, wall) is not None
    )
    if parent_divisors_p:
        raise AssertionError(f"P gained parent-wall divisors: {parent_divisors_p}")

    one = {boundary.ZERO: 1}
    c = boundary.coordinate(2)
    d = boundary.coordinate(3)
    f = boundary.coordinate(5)
    g = boundary.coordinate(6)
    h = boundary.coordinate(7)
    i = boundary.coordinate(8)
    factor_f = boundary.subtract(boundary.multiply(g, h), i)
    factor_q = boundary.add(
        boundary.multiply(d, boundary.subtract(h, i)),
        boundary.multiply(
            boundary.multiply(f, h), boundary.subtract(g, one)
        ),
    )
    reconstructed_p = boundary.add(
        scale(
            boundary.multiply(boundary.multiply(f, u), factor_f), -1
        ),
        boundary.multiply(boundary.multiply(c, t), factor_q),
    )
    if reconstructed_p != EXPECTED_P:
        raise AssertionError("the transverse P graph identity changed")
    transverse_unit = boundary.subtract(
        factor_q, boundary.multiply(f, factor_f)
    )
    expected_transverse_unit = boundary.multiply(
        walls["1357"], walls["1258"]
    )
    if transverse_unit != expected_transverse_unit:
        raise AssertionError("the P graph transversality identity changed")

    hypersurface = boundary.subtract(
        boundary.multiply(b_two, a_three),
        boundary.multiply(b_three, a_two),
    )
    hypersurface_e = boundary.derivative(hypersurface, 4)
    graph_rank_drop = boundary.subtract(
        boundary.multiply(b_two, rank_constant),
        boundary.multiply(a_two, rank_a),
    )
    expected_graph_rank_drop = boundary.subtract(
        boundary.multiply(b_two, hypersurface_e),
        boundary.multiply(boundary.derivative(b_two, 4), hypersurface),
    )
    if graph_rank_drop != expected_graph_rank_drop:
        raise AssertionError("the graph/rank-drop compatibility identity changed")

    hypersurface_e_constant, hypersurface_e_slope = boundary.split_linear(
        hypersurface_e, 4
    )
    if any(value % 2 for value in hypersurface_e_slope.values()):
        raise AssertionError("the E_e slope lost its content two")
    half_slope = {
        monomial: value // 2
        for monomial, value in hypersurface_e_slope.items()
    }
    primitive_l = triples.exact_divide(half_slope, t)
    if primitive_l is None:
        raise AssertionError("the E_e slope lost its parent-unit i-f factor")
    if census(primitive_l) != (60, 4, 7):
        raise AssertionError("the primitive L census changed")
    if any(
        monomial[index]
        for monomial in primitive_l
        for index in (0, boundary.HEIGHT, 4)
    ):
        raise AssertionError("L unexpectedly depends on a, b, or e")
    reconstructed_e = boundary.add(
        hypersurface_e_constant,
        boundary.multiply(
            boundary.coordinate(4),
            scale(boundary.multiply(t, primitive_l), 2),
        ),
    )
    if reconstructed_e != hypersurface_e:
        raise AssertionError("the factored E_e graph equation changed")
    parent_divisors_l = tuple(
        label
        for label, wall in walls.items()
        if triples.exact_divide(primitive_l, wall) is not None
    )
    if parent_divisors_l:
        raise AssertionError(f"L gained parent-wall divisors: {parent_divisors_l}")

    print("PASS exact ae rank-drop branch from the stored integer residuals")
    print("PASS coefficient_a(K_ae) = [2357][2458](i-f) P")
    print("PASS P: 12 terms, degrees 4..5, independent of a,b,e")
    print("PASS P=-f[1378]F+c(i-f)Q and Q-fF=[1357][1258]")
    print("BRANCH P=0 is a transverse c graph; Q cannot vanish there")
    print("PASS B*K0-A*K1 = B*E_e-B_e*E as an integer identity")
    print("PASS E_e = C + 2e(i-f)L with primitive 60-term L")
    print("BRANCH P!=0 gives the a graph; P=0 gives the transverse c graph")
    print("BRANCH L!=0 gives the e graph; L=0 is an extra-factor frontier")
    print("SCOPE component decoration only; no unit ideal or orbit is closed")


if __name__ == "__main__":
    main()
