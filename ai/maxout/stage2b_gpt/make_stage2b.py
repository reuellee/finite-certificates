"""Generate the exact Stage 2b certificates for the fixed reference U.

All combinatorial data are rebuilt from U_INTS.  Floating-point LPs are used
only to suggest supports.  Every serialized multiplier is repaired over
Fraction, cleared to a primitive nonnegative integer vector, and checked
against the integral matrix before it is written.

Run from the repository root with the requested interpreter:

    E:/Projects/sae-identifiability/.venv/Scripts/python.exe \
        ai/maxout/stage2b_gpt/make_stage2b.py

The main bundle covers both labeled members of all 16,570 global-flip
classes and k=1,2: 66,280 strict systems in total.
"""
from __future__ import annotations

import argparse
import gzip
import itertools
import json
import math
import sys
import time
from fractions import Fraction
from pathlib import Path

import numpy as np
from scipy.optimize import linprog


HERE = Path(__file__).resolve().parent
MAXOUT = HERE.parent
sys.path.insert(0, str(MAXOUT))
import facet_lp  # noqa: E402


U_INTS = (
    (-6, -13, 18),
    (-9, -12, 8),
    (-13, -4, 16),
    (4, -19, -8),
    (16, 15, -12),
)
PAIRS = tuple(itertools.combinations(range(5), 2))
TRIPLES = tuple(itertools.combinations(range(5), 3))
MASK20 = (1 << 20) - 1
MASTER_SEED = 2026073002
SECONDARY_SEED = 2026073003


def dot(a, b):
    return sum(x * y for x, y in zip(a, b))


def cross(a, b):
    return (
        a[1] * b[2] - a[2] * b[1],
        a[2] * b[0] - a[0] * b[2],
        a[0] * b[1] - a[1] * b[0],
    )


def det3(a, b, c):
    return dot(a, cross(b, c))


def frac_text(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else str(value)


def exact_chambers_with_witnesses(U):
    """Enumerate topes from exact perturbations of every arrangement ray.

    At r=U_i x U_j the other three signs are nonzero.  A rational vector p
    with <U_i,p>,<U_j,p> independently prescribed as +/-1 exists.  Taking
    x=q*M*r+p with M large enough realizes each of the four adjacent topes
    while preserving the other three ray signs.  Every chamber is adjacent
    to an arrangement ray, so the deduplicated set is exhaustive.
    """
    witnesses = {}
    for i, j in PAIRS:
        ui, uj = U[i], U[j]
        r = cross(ui, uj)
        aa, ab, bb = dot(ui, ui), dot(ui, uj), dot(uj, uj)
        gram_det = aa * bb - ab * ab
        if gram_det == 0:
            raise ValueError(f"parallel directions {i},{j}")
        for si in (-1, 1):
            for sj in (-1, 1):
                ca = Fraction(si * bb - sj * ab, gram_det)
                cb = Fraction(aa * sj - ab * si, gram_det)
                p = tuple(ca * ui[d] + cb * uj[d] for d in range(3))
                assert dot(ui, p) == si and dot(uj, p) == sj
                ratios = []
                for t in range(5):
                    if t in (i, j):
                        continue
                    ray_dot = dot(U[t], r)
                    if ray_dot == 0:
                        raise ValueError(f"nongeneric triple {t},{i},{j}")
                    ratio = abs(dot(U[t], p) / ray_dot)
                    ratios.append((ratio.numerator + ratio.denominator - 1)
                                  // ratio.denominator)
                M = 1 + max(ratios, default=0)
                for q in (-1, 1):
                    x = tuple(Fraction(q * M * r[d]) + p[d] for d in range(3))
                    products = [dot(U[t], x) for t in range(5)]
                    if any(v == 0 for v in products):
                        raise AssertionError("constructed chamber witness is not strict")
                    eps = tuple(1 if v > 0 else -1 for v in products)
                    witnesses.setdefault(eps, x)
    chambers = sorted(witnesses)
    if len(chambers) != 22:
        raise AssertionError(f"expected 22 exact chambers, got {len(chambers)}")
    return chambers, [witnesses[eps] for eps in chambers]


def exact_incidence(U, chambers):
    ch_rays = []
    crosses = [cross(U[i], U[j]) for i, j in PAIRS]
    for eps in chambers:
        sides = []
        for ci, (i, j) in enumerate(PAIRS):
            values = [
                eps[t] * dot(U[t], crosses[ci])
                for t in range(5) if t not in (i, j)
            ]
            if all(v > 0 for v in values):
                sides.append(2 * ci)
            elif all(v < 0 for v in values):
                sides.append(2 * ci + 1)
        if len(sides) < 3:
            raise AssertionError(f"bad exact incidence for chamber {eps}: {sides}")
        ch_rays.append(sides)
    return ch_rays


def chamber_masks(ch_rays):
    return [sum(1 << side for side in sides) for sides in ch_rays]


def enumerate_representatives_vectorized(ch_rays):
    assignments = np.arange(1 << 20, dtype=np.uint32)
    valid = np.ones(len(assignments), dtype=bool)
    for mask_int in chamber_masks(ch_rays):
        mask = np.uint32(mask_int)
        selected = assignments & mask
        valid &= (selected != 0) & (selected != mask)
    return assignments[valid & ((assignments & 1) == 0)].astype(np.uint32)


def enumerate_representatives_dfs(ch_rays):
    masks = chamber_masks(ch_rays)
    touches = [
        sum(bool(mask & (1 << side)) for mask in masks) for side in range(20)
    ]
    order = [0] + sorted(range(1, 20), key=lambda s: (-touches[s], s))
    out = []

    def rec(pos, assigned, ones):
        if pos == len(order):
            out.append(ones)
            return
        side = order[pos]
        if side == 0:
            rec(pos + 1, assigned, ones)
            return
        bit = 1 << side
        for value in (0, 1):
            new_assigned = assigned | bit
            new_ones = ones | bit if value else ones
            okay = True
            for mask in masks:
                if (new_assigned & mask) == mask:
                    selected = new_ones & mask
                    if selected == 0 or selected == mask:
                        okay = False
                        break
            if okay:
                rec(pos + 1, new_assigned, new_ones)

    rec(0, 1, 0)
    return sorted(out)


def cross_check_facet_build(U, exact_chambers, exact_rays, seed):
    """Retry the stochastic legacy builder, then compare literal labels."""
    unit = np.asarray(U, dtype=float)
    unit /= np.linalg.norm(unit, axis=1, keepdims=True)
    facet_lp.rng = np.random.default_rng(seed)
    built = None
    attempts = 0
    for attempts in range(1, 101):
        candidate = facet_lp.build(unit, 2)
        if candidate is not None and len(candidate[1]) == 22:
            built = candidate
            break
    if built is None:
        raise AssertionError("facet_lp.build did not recover 22 chambers")
    _, float_chambers, float_rays = built
    exact_lookup = {
        tuple(eps): tuple(sorted(sides))
        for eps, sides in zip(exact_chambers, exact_rays)
    }
    float_lookup = {
        tuple(map(int, eps)): tuple(sorted(sides))
        for eps, sides in zip(float_chambers, float_rays)
    }
    if float_lookup != exact_lookup:
        raise AssertionError("facet_lp.build incidence disagrees with exact incidence")
    return attempts


def determinant_table(U):
    return {
        (t, i, j): abs(det3(U[t], U[i], U[j]))
        for i, j in PAIRS for t in range(5) if t not in (i, j)
    }


def unsigned_side_rows(U, k):
    """Integral rows after positive row and positive-weight rescaling."""
    split = [1] * k + [-1] * (5 - k)
    dmap = determinant_table(U)
    rows = []
    for i, j in PAIRS:
        r = cross(U[i], U[j])
        weights = [
            0 if t in (i, j) else split[t] * dmap[(t, i, j)]
            for t in range(5)
        ]
        rows.append(list(r) + weights)
        rows.append(list(-x for x in r) + weights)
    return rows


def system_rows(unsigned_rows, sigma_bits):
    rows = []
    for side, row in enumerate(unsigned_rows):
        sign = 1 if sigma_bits & (1 << side) else -1
        rows.append([sign * value for value in row])
    for t in range(5):
        rows.append([0, 0, 0] + [1 if q == t else 0 for q in range(5)])
    return rows


def solve_exact_on_support(B, support):
    """Solve B_support^T y=0, sum(y)=1 exactly when support is a basis."""
    m = len(support)
    ncolumns = len(B[0])
    matrix = [
        [Fraction(B[row][column]) for row in support] + [Fraction(0)]
        for column in range(ncolumns)
    ]
    matrix.append([Fraction(1)] * m + [Fraction(1)])
    nrows = len(matrix)
    pivot_row = 0
    pivots = {}
    for column in range(m):
        chosen = next(
            (row for row in range(pivot_row, nrows)
             if matrix[row][column] != 0),
            None,
        )
        if chosen is None:
            continue
        matrix[pivot_row], matrix[chosen] = matrix[chosen], matrix[pivot_row]
        pivot = matrix[pivot_row][column]
        matrix[pivot_row] = [value / pivot for value in matrix[pivot_row]]
        for row in range(nrows):
            if row != pivot_row and matrix[row][column] != 0:
                factor = matrix[row][column]
                matrix[row] = [
                    a - factor * b
                    for a, b in zip(matrix[row], matrix[pivot_row])
                ]
        pivots[column] = pivot_row
        pivot_row += 1
    for row in range(nrows):
        if all(matrix[row][column] == 0 for column in range(m)):
            if matrix[row][m] != 0:
                return None
    if len(pivots) != m:
        return None
    solution = [matrix[pivots[column]][m] for column in range(m)]
    if any(value <= 0 for value in solution):
        return None
    return solution


def primitive_certificate(B, support, values):
    denominators = [value.denominator for value in values]
    common = 1
    for denominator in denominators:
        common = math.lcm(common, denominator)
    integers = [value.numerator * (common // value.denominator)
                for value in values]
    divisor = 0
    for value in integers:
        divisor = math.gcd(divisor, abs(value))
    integers = [value // divisor for value in integers]
    sparse = [[int(row), int(value)]
              for row, value in zip(support, integers) if value]
    if not sparse or any(value <= 0 for _, value in sparse):
        return None
    totals = [
        sum(value * B[row][column] for row, value in sparse)
        for column in range(len(B[0]))
    ]
    if totals != [0] * len(B[0]):
        return None
    return sparse


def exact_dual_certificate(B, rng, max_attempts=8):
    """Use HiGHS for a support hint and repair it in exact arithmetic."""
    Bf = np.asarray(B, dtype=float)
    equalities = np.vstack([Bf.T, np.ones(len(B))])
    rhs = np.r_[np.zeros(Bf.shape[1]), 1.0]
    scales = np.maximum(np.max(np.abs(equalities), axis=1), 1.0)
    equalities_scaled = equalities / scales[:, None]
    rhs_scaled = rhs / scales
    objectives = [np.zeros(len(B))]
    objectives.extend(rng.normal(size=len(B)) for _ in range(max_attempts - 1))
    last_status = None
    for objective in objectives:
        result = linprog(
            objective,
            A_eq=equalities_scaled,
            b_eq=rhs_scaled,
            bounds=[(0, None)] * len(B),
            method="highs",
        )
        last_status = result.status
        if result.status != 0:
            continue
        maximum = max(float(np.max(result.x)), 1.0)
        for tolerance in (1e-8, 1e-10, 1e-12):
            support = [
                index for index, value in enumerate(result.x)
                if value > tolerance * maximum
            ]
            values = solve_exact_on_support(B, support)
            if values is None:
                continue
            certificate = primitive_certificate(B, support, values)
            if certificate is not None:
                return certificate
    return None, last_status


def exact_primal_hint(B):
    """Look for Bx>=1 only if the dual search unexpectedly fails."""
    result = linprog(
        np.zeros(len(B[0])),
        A_ub=-np.asarray(B, dtype=float),
        b_ub=-np.ones(len(B)),
        bounds=[(None, None)] * len(B[0]),
        method="highs",
    )
    if result.status != 0:
        return None
    for bound in (10**5, 10**7, 10**9):
        x = [Fraction(float(value)).limit_denominator(bound) for value in result.x]
        margins = [sum(Fraction(a) * b for a, b in zip(row, x)) for row in B]
        if min(margins) > 0:
            return x
    return None


def hull_verify_discovery(U, sigma_bits, k, x):
    """Float hull cross-check using the established counter pattern."""
    sys.path.insert(0, str(MAXOUT))
    import search_maxout67

    unit = np.asarray(U, dtype=float)
    norms = np.linalg.norm(unit, axis=1)
    unit /= norms[:, None]
    T = np.asarray([float(value) for value in x[:3]])
    weights = np.asarray([float(value) for value in x[3:]]) * norms
    midpoints = np.zeros((5, 3))
    midpoints[0] = T / weights[0]
    a = np.r_[2 * weights[:k], weights[k:]]
    b = np.r_[weights[:k], 2 * weights[k:]]
    count = search_maxout67.nverts(midpoints, unit, a, b)
    payload = {
        "status": "strict_side_system_feasible",
        "sigma_bits": sigma_bits,
        "k": k,
        "x_fraction": [frac_text(value) for value in x],
        "hull_vertex_count": int(count),
        "M": midpoints.tolist(),
        "U_unit": unit.tolist(),
        "a": a.tolist(),
        "b": b.tolist(),
    }
    path = HERE / "discovery_44.json"
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return count, path


def generate_core(U, representatives, rng, limit=None):
    rows_by_k = {k: unsigned_side_rows(U, k) for k in (1, 2)}
    certificates = []
    failures = []
    start = time.time()
    total = len(representatives) * 4
    if limit is not None:
        total = min(total, limit)
    processed = 0
    support_histogram = {}
    largest_coefficient = 0
    for representative in representatives:
        for sigma_bits in (int(representative), int(representative) ^ MASK20):
            for k in (1, 2):
                if limit is not None and processed >= limit:
                    return certificates, failures, {
                        "processed": processed,
                        "support_histogram": support_histogram,
                        "largest_coefficient": largest_coefficient,
                        "elapsed_seconds": time.time() - start,
                    }
                B = system_rows(rows_by_k[k], sigma_bits)
                certificate = exact_dual_certificate(B, rng)
                if isinstance(certificate, tuple):
                    primal = exact_primal_hint(B)
                    if primal is not None:
                        count, path = hull_verify_discovery(
                            U, sigma_bits, k, primal
                        )
                        raise RuntimeError(
                            f"strict feasible system at bits={sigma_bits}, k={k}; "
                            f"hull count={count}; saved {path}"
                        )
                    failures.append({
                        "sigma_bits": sigma_bits,
                        "k": k,
                        "dual_status": certificate[1],
                    })
                    certificates.append([])
                else:
                    certificates.append(certificate)
                    size = len(certificate)
                    support_histogram[str(size)] = (
                        support_histogram.get(str(size), 0) + 1
                    )
                    largest_coefficient = max(
                        largest_coefficient,
                        max(value for _, value in certificate),
                    )
                processed += 1
                if processed % 1000 == 0 or processed == total:
                    print(
                        f"core: {processed}/{total} exact certificates "
                        f"({time.time() - start:.1f}s)",
                        flush=True,
                    )
    return certificates, failures, {
        "processed": processed,
        "support_histogram": support_histogram,
        "largest_coefficient": largest_coefficient,
        "elapsed_seconds": time.time() - start,
    }


def class_pattern(bits):
    pattern = []
    for ci in range(10):
        a = 1 if bits & (1 << (2 * ci)) else -1
        b = 1 if bits & (1 << (2 * ci + 1)) else -1
        pattern.append("+" if a == b == 1 else "-" if a == b == -1 else "x")
    return "".join(pattern)


def symmetric_reduced_rows(U, bits, k):
    full = system_rows(unsigned_side_rows(U, k), bits)
    eligible = []
    rows = []
    for ci, marker in enumerate(class_pattern(bits)):
        if marker != "x":
            eligible.append(ci)
            rows.append([
                full[2 * ci][column] + full[2 * ci + 1][column]
                for column in range(8)
            ])
    for t in range(5):
        rows.append([0, 0, 0] + [1 if q == t else 0 for q in range(5)])
    return full, eligible, rows


def lift_symmetric_certificate(full_B, eligible, reduced_certificate):
    lifted = {}
    nclasses = len(eligible)
    for reduced_row, value in reduced_certificate:
        if reduced_row < nclasses:
            ci = eligible[reduced_row]
            lifted[2 * ci] = lifted.get(2 * ci, 0) + value
            lifted[2 * ci + 1] = lifted.get(2 * ci + 1, 0) + value
        else:
            row = 20 + (reduced_row - nclasses)
            lifted[row] = lifted.get(row, 0) + value
    sparse = sorted([[row, value] for row, value in lifted.items() if value])
    totals = [
        sum(value * full_B[row][column] for row, value in sparse)
        for column in range(8)
    ]
    if totals != [0] * 8 or any(value <= 0 for _, value in sparse):
        raise AssertionError("bad lifted symmetric certificate")
    for ci in range(10):
        a = dict(sparse).get(2 * ci, 0)
        b = dict(sparse).get(2 * ci + 1, 0)
        if a != b:
            raise AssertionError("symmetric certificate has unequal pair weights")
        if a and class_pattern_from_full(full_B, ci) is False:
            raise AssertionError("symmetric certificate uses a nonsymmetric class")
    return sparse


def class_pattern_from_full(full_B, ci):
    """The T blocks are opposite exactly when the two sigma signs agree."""
    return all(
        full_B[2 * ci][d] == -full_B[2 * ci + 1][d]
        for d in range(3)
    )


def generate_symmetric_coverage(U, representatives, rng):
    caches = {1: {}, 2: {}}
    residue_witnesses = {1: {}, 2: {}}
    covered = {1: [], 2: []}
    residues = {1: [], 2: []}
    starts = time.time()
    for position, representative in enumerate(representatives):
        bits = int(representative)
        key = class_pattern(bits)
        for k in (1, 2):
            if key not in caches[k]:
                full, eligible, reduced = symmetric_reduced_rows(U, bits, k)
                cert = exact_dual_certificate(reduced, rng)
                if isinstance(cert, tuple):
                    witness = exact_primal_hint(reduced)
                    if witness is None:
                        raise RuntimeError(
                            f"could neither certify nor exactly refute symmetric "
                            f"pattern {key} at k={k}"
                        )
                    caches[k][key] = None
                    residue_witnesses[k][key] = [
                        frac_text(value) for value in witness
                    ]
                else:
                    caches[k][key] = lift_symmetric_certificate(
                        full, eligible, cert
                    )
            if caches[k][key] is None:
                residues[k].append(bits)
            else:
                covered[k].append(bits)
        if (position + 1) % 2000 == 0:
            print(
                f"symmetric: {position + 1}/{len(representatives)} classes "
                f"({time.time() - starts:.1f}s)",
                flush=True,
            )
    both = sorted(set(covered[1]) & set(covered[2]))
    either = sorted(set(covered[1]) | set(covered[2]))
    representative_set = set(representatives.astype(int).tolist())
    not_both = sorted(representative_set - set(both))
    neither = sorted(representative_set - set(either))
    return {
        "schema": 1,
        "meaning": (
            "A covered representative has an exact Gordan certificate using "
            "only classes whose two sigma side signs agree, with equal "
            "multipliers on the two sides; hence its T block cancels identically."
        ),
        "n_representatives": len(representatives),
        "splits": {
            str(k): {
                "n_covered": len(covered[k]),
                "n_residue": len(residues[k]),
                "covered_bits": covered[k],
                "residue_bits": residues[k],
                "pattern_certificates": {
                    key: cert for key, cert in caches[k].items()
                    if cert is not None
                },
                "residue_pattern_strict_primal_witnesses": (
                    residue_witnesses[k]
                ),
                "n_distinct_patterns_tested": len(caches[k]),
                "n_distinct_patterns_certified": sum(
                    cert is not None for cert in caches[k].values()
                ),
            }
            for k in (1, 2)
        },
        "n_classes_covered_for_both_splits": len(both),
        "n_classes_covered_for_at_least_one_split": len(either),
        "n_classes_not_covered_for_both_splits": len(not_both),
        "classes_not_covered_for_both_splits_bits": not_both,
        "n_classes_covered_for_neither_split": len(neither),
        "classes_covered_for_neither_split_bits": neither,
        "elapsed_seconds": time.time() - starts,
    }


def valid_t0_assignments(ch_rays):
    out = []
    for bits in range(1 << 10):
        signs = [1 if bits & (1 << ci) else -1 for ci in range(10)]
        if all(
            len({signs[side // 2] for side in sides}) > 1
            for sides in ch_rays
        ):
            out.append(bits)
    if len(out) != 200:
        raise AssertionError(f"expected 200 T=0 assignments, got {len(out)}")
    return sorted(out)


def t0_rows(U, bits, k):
    split = [1] * k + [-1] * (5 - k)
    dmap = determinant_table(U)
    rows = []
    for ci, (i, j) in enumerate(PAIRS):
        sign = 1 if bits & (1 << ci) else -1
        rows.append([
            0 if t in (i, j)
            else sign * split[t] * dmap[(t, i, j)]
            for t in range(5)
        ])
    for t in range(5):
        rows.append([1 if q == t else 0 for q in range(5)])
    return rows


def generate_t0_k1(U, ch_rays, rng):
    valid = valid_t0_assignments(ch_rays)
    certificates = []
    for bits in valid:
        cert = exact_dual_certificate(t0_rows(U, bits, 1), rng)
        if isinstance(cert, tuple):
            raise RuntimeError(f"no exact T=0 k=1 certificate for bits={bits}")
        certificates.append(cert)
    return {
        "schema": 1,
        "U_ints": [list(row) for row in U],
        "valid_class_bits": valid,
        "k": 1,
        "certificates": certificates,
        "note": (
            "Each sparse primitive integer vector is y>=0, y!=0 and "
            "A^T y=0 for the 10 signed class rows plus five positivity rows."
        ),
    }


def make_second_configuration(seed):
    rng = np.random.default_rng(seed)
    for attempt in range(1, 1001):
        U = tuple(
            tuple(map(int, row))
            for row in rng.integers(-20, 21, size=(5, 3))
        )
        if any(dot(row, row) == 0 for row in U):
            continue
        if any(det3(U[i], U[j], U[k]) == 0 for i, j, k in TRIPLES):
            continue
        chambers, witnesses = exact_chambers_with_witnesses(U)
        if len(chambers) == 22:
            return U, attempt, chambers, witnesses
    raise RuntimeError("failed to construct a second generic integer configuration")


def cross_validate_second(seed, rng, sample_systems=200):
    U, attempt, chambers, _ = make_second_configuration(seed)
    rays = exact_incidence(U, chambers)
    reps_a = enumerate_representatives_vectorized(rays)
    reps_b = enumerate_representatives_dfs(rays)
    if reps_a.astype(int).tolist() != reps_b:
        raise AssertionError("second-configuration enumerators disagree")
    exact_sample = []
    cursor = 0
    for representative in reps_a:
        for bits in (int(representative), int(representative) ^ MASK20):
            for k in (1, 2):
                if cursor >= sample_systems:
                    break
                B = system_rows(unsigned_side_rows(U, k), bits)
                cert = exact_dual_certificate(B, rng)
                if isinstance(cert, tuple):
                    exact_sample.append({
                        "sigma_bits": bits, "k": k, "certified": False
                    })
                else:
                    exact_sample.append({
                        "sigma_bits": bits, "k": k, "certified": True,
                        "certificate": cert,
                    })
                cursor += 1
            if cursor >= sample_systems:
                break
        if cursor >= sample_systems:
            break
    return {
        "schema": 1,
        "purpose": (
            "Cross-validation only. No structure or certificate from this "
            "configuration is used in the reference theorem."
        ),
        "seed": seed,
        "integer_draw_attempt": attempt,
        "U_ints": [list(row) for row in U],
        "n_chambers": len(chambers),
        "degree_multiset": sorted(map(len, rays)),
        "n_valid_labeled": 2 * len(reps_a),
        "n_global_flip_classes": len(reps_a),
        "independent_enumerators_agree": True,
        "sample_system_count": len(exact_sample),
        "sample_exact_certificate_count": sum(
            item["certified"] for item in exact_sample
        ),
        "sample": exact_sample,
    }


def write_json_gz(path, payload):
    with gzip.open(path, "wt", encoding="utf-8", compresslevel=9) as handle:
        json.dump(payload, handle, separators=(",", ":"))
        handle.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="development-only cap on core systems; omitting it is required for the theorem",
    )
    parser.add_argument(
        "--skip-secondary", action="store_true",
        help="skip symmetric coverage, T=0 k=1, and second-U cross-validation",
    )
    parser.add_argument(
        "--secondary-only", action="store_true",
        help="reuse an already generated core bundle and run only secondary work",
    )
    args = parser.parse_args()
    HERE.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(MASTER_SEED)

    chambers, witnesses = exact_chambers_with_witnesses(U_INTS)
    ch_rays = exact_incidence(U_INTS, chambers)
    facet_attempts = cross_check_facet_build(
        U_INTS, chambers, ch_rays, MASTER_SEED
    )
    representatives_vector = enumerate_representatives_vectorized(ch_rays)
    representatives_dfs = enumerate_representatives_dfs(ch_rays)
    if representatives_vector.astype(int).tolist() != representatives_dfs:
        raise AssertionError("reference sigma enumerators disagree")
    if len(representatives_vector) != 16570:
        raise AssertionError(
            f"expected 16,570 classes, got {len(representatives_vector)}"
        )
    print(
        f"reference structure: 22 chambers, {2 * len(representatives_vector)} "
        f"valid labeled sigmas; facet_lp retry count={facet_attempts}",
        flush=True,
    )

    structure = {
        "schema": 1,
        "U_ints": [list(row) for row in U_INTS],
        "pairs_in_class_order": [list(pair) for pair in PAIRS],
        "chambers": [list(eps) for eps in chambers],
        "chamber_witnesses": [
            [frac_text(value) for value in witness] for witness in witnesses
        ],
        "chamber_side_incidence": ch_rays,
        "chamber_masks": chamber_masks(ch_rays),
        "n_valid_labeled": 2 * len(representatives_vector),
        "n_global_flip_classes": len(representatives_vector),
        "global_flip_representatives": representatives_vector.astype(int).tolist(),
        "exact_enumeration": (
            "Exact rational ray perturbations give all chambers; literal side "
            "incidence uses integer determinant signs. Vectorized exhaustive "
            "scan and an independent constraint-pruned DFS agree."
        ),
        "facet_lp_build_cross_check_seed": MASTER_SEED,
        "facet_lp_build_attempts_until_22": facet_attempts,
    }
    (HERE / "reference_structure.json").write_text(
        json.dumps(structure, indent=2) + "\n", encoding="utf-8"
    )

    if not args.secondary_only:
        certificates, failures, statistics = generate_core(
            U_INTS, representatives_vector, rng, args.limit
        )
        if failures:
            (HERE / "core_failures.json").write_text(
                json.dumps(failures, indent=2) + "\n", encoding="utf-8"
            )
            raise RuntimeError(
                f"{len(failures)} core systems lack exact certificates"
            )
        expected = len(representatives_vector) * 4
        complete = args.limit is None and len(certificates) == expected
        bundle = {
            "schema": 1,
            "status": "complete" if complete else "development_partial",
            "U_ints": [list(row) for row in U_INTS],
            "row_model": (
                "Rows 0..19 are sigma_side*(+/- cross(U_i,U_j), "
                "s_t*abs(det(U_t,U_i,U_j))); rows 20..24 are the five positive "
                "weight coordinate rows. Variables are (T0,T1,T2,w0,...,w4)."
            ),
            "representatives": representatives_vector.astype(int).tolist(),
            "system_order": (
                "For each representative in ascending order: sigma=rep then "
                "sigma=rep xor (2^20-1); within each sigma k=1 then k=2."
            ),
            "n_valid_labeled": 2 * len(representatives_vector),
            "splits": [1, 2],
            "n_systems": len(certificates),
            "expected_complete_systems": expected,
            "certificates": certificates,
            "certificate_format": (
                "Sparse [row_index,positive_integer] pairs; omitted rows have "
                "multiplier zero. Every vector is primitive and satisfies B^T y=0."
            ),
            "statistics": statistics,
            "seed_for_float_support_hints": MASTER_SEED,
            "exactness": (
                "Every serialized certificate was support-repaired over Fraction, "
                "cleared to primitive integers, and checked against the integral B."
            ),
        }
        write_json_gz(HERE / "gordan_bundle.json.gz", bundle)
        print(
            f"wrote core bundle with {len(certificates)} exact certificates",
            flush=True,
        )

    if not args.skip_secondary:
        symmetric = generate_symmetric_coverage(
            U_INTS, representatives_vector, rng
        )
        write_json_gz(HERE / "symmetric_coverage.json.gz", symmetric)
        t0_payload = generate_t0_k1(U_INTS, ch_rays, rng)
        write_json_gz(HERE / "t0_k1_bundle.json.gz", t0_payload)
        second = cross_validate_second(SECONDARY_SEED, rng)
        (HERE / "second_configuration_crosscheck.json").write_text(
            json.dumps(second, indent=2) + "\n", encoding="utf-8"
        )
        print(
            "secondary: symmetric k=1 "
            f"{symmetric['splits']['1']['n_covered']}/16570, k=2 "
            f"{symmetric['splits']['2']['n_covered']}/16570; "
            "T=0 k=1 200/200; second-U sample "
            f"{second['sample_exact_certificate_count']}/"
            f"{second['sample_system_count']}",
            flush=True,
        )


if __name__ == "__main__":
    main()
