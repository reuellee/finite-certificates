#!/usr/bin/env python3
"""Exact interior-wall witness search on the row-2599 full support.

Discovery uses floating-point samples only to choose candidate straight segments.
Every accepted segment is then certified with exact rational Bernstein
coefficients for all seventy signed parent brackets, and every residual-wall
crossing is rechecked by exact rational endpoint evaluation.  Thus floating
point can only cause a missed witness, never a false certificate.
"""
from __future__ import annotations

from fractions import Fraction
from math import comb
import json
from pathlib import Path
import sys

import numpy as np

HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import verify_diag2_canonical_robust_edges as evaluator  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402

CATALOG = HERE / "certs_4_8.jsonl"
MAX_DEPTH = 8
SAMPLE_T = (0.25, 0.5, 0.75)


def mul_linear(poly, a, b):
    out = [Fraction(0)] * (len(poly) + 1)
    for k, c in enumerate(poly):
        out[k] += c * a
        out[k + 1] += c * b
    return out


def segment_power(polynomial, x0, x1):
    degree = max(sum(m) for m in polynomial)
    out = [Fraction(0)] * (degree + 1)
    dx = tuple(b - a for a, b in zip(x0, x1, strict=True))
    for monomial, coefficient in polynomial.items():
        term = [Fraction(coefficient)]
        for index, exponent in enumerate(monomial):
            for _ in range(exponent):
                term = mul_linear(term, x0[index], dx[index])
        for k, value in enumerate(term):
            out[k] += value
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def restrict_power(coeffs, lo, hi):
    scale = hi - lo
    out = [Fraction(0)] * len(coeffs)
    for k, c in enumerate(coeffs):
        for j in range(k + 1):
            out[j] += c * comb(k, j) * lo ** (k - j) * scale ** j
    while len(out) > 1 and out[-1] == 0:
        out.pop()
    return out


def bernstein_coeffs(power):
    d = len(power) - 1
    if d == 0:
        return tuple(power)
    return tuple(
        sum(power[k] * Fraction(comb(j, k), comb(d, k)) for k in range(j + 1))
        for j in range(d + 1)
    )


def positive_on_unit(power, depth=MAX_DEPTH):
    stack = [(Fraction(0), Fraction(1), 0)]
    while stack:
        lo, hi, level = stack.pop()
        b = bernstein_coeffs(restrict_power(power, lo, hi))
        if all(value > 0 for value in b):
            continue
        if any(value < 0 for value in b) or level >= depth:
            return False
        mid = (lo + hi) / 2
        stack.append((lo, mid, level + 1))
        stack.append((mid, hi, level + 1))
    return True


def eval_float(polynomial, x):
    total = 0.0
    for monomial, coefficient in polynomial.items():
        term = float(coefficient)
        for index, exponent in enumerate(monomial):
            if exponent:
                term *= x[index] ** exponent
        total += term
    return total


def exact_safe_edge(i, j, points, parents):
    x0, x1 = points[i], points[j]
    for _label, target, polynomial, _terms in parents:
        signed = [target * c for c in segment_power(polynomial, x0, x1)]
        if not positive_on_unit(signed):
            return False
    return True


def main():
    records = [json.loads(line) for line in CATALOG.read_text().splitlines() if line]
    record = records[2_599]
    parents, _digest = gate.parent_polynomials(record)
    with np.load(gate.POINT_BANK, allow_pickle=False) as source:
        matrices = np.asarray(source["chart_matrix"], dtype=np.int64)
    points = tuple(gate.normalized_values(matrix.tolist()) for matrix in matrices)
    fpoints = np.asarray([[float(v) for v in point] for point in points], dtype=float)

    # Cheap floating-point prefilter; exact Bernstein replay decides acceptance.
    parent_polys = tuple((target, poly) for _label, target, poly, _terms in parents)
    candidate_pairs = []
    for i in range(len(points)):
        for j in range(i + 1, len(points)):
            ok = True
            for t in SAMPLE_T:
                x = (1.0 - t) * fpoints[i] + t * fpoints[j]
                if any(target * eval_float(poly, x) <= 1e-10 for target, poly in parent_polys):
                    ok = False
                    break
            if ok:
                candidate_pairs.append((i, j))

    safe = []
    for i, j in candidate_pairs:
        if exact_safe_edge(i, j, points, parents):
            safe.append((i, j))
    if not safe:
        raise AssertionError("no exact parent-safe point-bank segments found")

    candidate_ids = gate.parse_candidates()
    _occurrences, _occurrence_factor, factor_polynomials = labeled.factor_polynomials()
    unresolved = []
    witnesses = []
    for factor_id in candidate_ids:
        poly = factor_polynomials[factor_id]
        vals = np.asarray([eval_float(poly, x) for x in fpoints])
        witness = None
        for i, j in safe:
            if vals[i] * vals[j] < 0.0:
                ei = evaluator.evaluate(poly, points[i])
                ej = evaluator.evaluate(poly, points[j])
                if ei * ej < 0:
                    witness = (i, j)
                    break
        if witness is None:
            # Exact fallback avoids treating floating-point ambiguity as absence.
            exact_vals = [evaluator.evaluate(poly, point) for point in points]
            for i, j in safe:
                if exact_vals[i] * exact_vals[j] < 0:
                    witness = (i, j)
                    break
        if witness is None:
            unresolved.append(factor_id)
        else:
            witnesses.append((factor_id, *witness))

    if unresolved:
        raise AssertionError(
            "FULLSUPPORT_SAFE_SEGMENT_RESIDUE "
            + json.dumps({
                "candidate_pairs": len(candidate_pairs),
                "exact_safe_edges": len(safe),
                "certified_crossing_factors": len(witnesses),
                "unresolved_count": len(unresolved),
                "first_unresolved": unresolved[:80],
            }, sort_keys=True)
        )

    print("PASS", len(safe), "exact parent-safe straight segments")
    print("PASS all", len(witnesses), "candidate residual walls have exact interior crossings")
    print("SCOPE nonemptiness only; this does not construct the chamber complex")


if __name__ == "__main__":
    main()
