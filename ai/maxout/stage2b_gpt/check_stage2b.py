"""Standalone exact checker for the Stage 2b bundles.

This script intentionally imports only the Python standard library.  It
reconstructs chambers, incidence, valid sigmas, integral system matrices,
and then verifies every serialized Gordan identity using Python integers and
Fraction arithmetic.  No floating-point result is trusted or needed.
"""
from __future__ import annotations

import gzip
import itertools
import json
import math
import sys
import time
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
U_EXPECTED = (
    (-6, -13, 18),
    (-9, -12, 8),
    (-13, -4, 16),
    (4, -19, -8),
    (16, 15, -12),
)
PAIRS = tuple(itertools.combinations(range(5), 2))
MASK20 = (1 << 20) - 1


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


def exact_chambers_with_witnesses(U):
    witnesses = {}
    for i, j in PAIRS:
        ui, uj = U[i], U[j]
        r = cross(ui, uj)
        aa, ab, bb = dot(ui, ui), dot(ui, uj), dot(uj, uj)
        gram_det = aa * bb - ab * ab
        assert gram_det > 0
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
                    assert ray_dot != 0
                    ratio = abs(dot(U[t], p) / ray_dot)
                    ratios.append((ratio.numerator + ratio.denominator - 1)
                                  // ratio.denominator)
                M = 1 + max(ratios, default=0)
                for q in (-1, 1):
                    x = tuple(Fraction(q * M * r[d]) + p[d] for d in range(3))
                    products = [dot(U[t], x) for t in range(5)]
                    assert all(value != 0 for value in products)
                    eps = tuple(1 if value > 0 else -1 for value in products)
                    witnesses.setdefault(eps, x)
    return sorted(witnesses), witnesses


def exact_incidence(U, chambers):
    out = []
    for eps in chambers:
        sides = []
        for ci, (i, j) in enumerate(PAIRS):
            r = cross(U[i], U[j])
            products = [
                eps[t] * dot(U[t], r)
                for t in range(5) if t not in (i, j)
            ]
            if all(value > 0 for value in products):
                sides.append(2 * ci)
            elif all(value < 0 for value in products):
                sides.append(2 * ci + 1)
        assert len(sides) >= 3
        out.append(sides)
    return out


def chamber_masks(ch_rays):
    return [sum(1 << side for side in sides) for sides in ch_rays]


def enumerate_representatives(ch_rays):
    masks = chamber_masks(ch_rays)
    touches = [
        sum(bool(mask & (1 << side)) for mask in masks) for side in range(20)
    ]
    order = [0] + sorted(range(1, 20), key=lambda s: (-touches[s], s))
    out = []

    def rec(pos, assigned, ones):
        if pos == 20:
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


def determinant_table(U):
    return {
        (t, i, j): abs(det3(U[t], U[i], U[j]))
        for i, j in PAIRS for t in range(5) if t not in (i, j)
    }


def unsigned_side_rows(U, k):
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
        rows.append(list(-value for value in r) + weights)
    return rows


def system_rows(unsigned, bits):
    rows = []
    for side, row in enumerate(unsigned):
        sign = 1 if bits & (1 << side) else -1
        rows.append([sign * value for value in row])
    for t in range(5):
        rows.append([0, 0, 0] + [1 if q == t else 0 for q in range(5)])
    return rows


def check_sparse_certificate(B, certificate, ncolumns):
    assert certificate
    seen = set()
    divisor = 0
    for row, value in certificate:
        assert isinstance(row, int) and 0 <= row < len(B)
        assert isinstance(value, int) and value > 0
        assert row not in seen
        seen.add(row)
        divisor = math.gcd(divisor, value)
    assert divisor == 1
    totals = [
        sum(value * B[row][column] for row, value in certificate)
        for column in range(ncolumns)
    ]
    assert totals == [0] * ncolumns, totals


def load_gz(name):
    with gzip.open(HERE / name, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def check_structure():
    payload = json.loads(
        (HERE / "reference_structure.json").read_text(encoding="utf-8")
    )
    U = tuple(tuple(row) for row in payload["U_ints"])
    assert U == U_EXPECTED
    chambers, witnesses = exact_chambers_with_witnesses(U)
    assert len(chambers) == 22
    assert [list(eps) for eps in chambers] == payload["chambers"]
    serialized_witnesses = [
        [Fraction(value) for value in witness]
        for witness in payload["chamber_witnesses"]
    ]
    for eps, witness in zip(chambers, serialized_witnesses):
        products = [dot(U[t], witness) for t in range(5)]
        assert all(value != 0 for value in products)
        assert tuple(1 if value > 0 else -1 for value in products) == eps
    ch_rays = exact_incidence(U, chambers)
    assert ch_rays == payload["chamber_side_incidence"]
    representatives = enumerate_representatives(ch_rays)
    assert len(representatives) == 16570
    assert representatives == payload["global_flip_representatives"]
    assert payload["n_valid_labeled"] == 33140
    return U, ch_rays, representatives


def check_core(U, representatives):
    payload = load_gz("gordan_bundle.json.gz")
    assert payload["schema"] == 1
    assert payload["status"] == "complete"
    assert tuple(tuple(row) for row in payload["U_ints"]) == U
    assert payload["representatives"] == representatives
    assert payload["n_valid_labeled"] == 33140
    assert payload["splits"] == [1, 2]
    assert payload["n_systems"] == 66280
    certificates = payload["certificates"]
    assert len(certificates) == 66280
    rows_by_k = {k: unsigned_side_rows(U, k) for k in (1, 2)}
    cursor = 0
    for representative in representatives:
        for bits in (representative, representative ^ MASK20):
            for k in (1, 2):
                B = system_rows(rows_by_k[k], bits)
                check_sparse_certificate(B, certificates[cursor], 8)
                cursor += 1
                if cursor % 5000 == 0:
                    print(f"checked core {cursor}/66280", flush=True)
    assert cursor == 66280


def class_pattern(bits):
    markers = []
    for ci in range(10):
        a = 1 if bits & (1 << (2 * ci)) else -1
        b = 1 if bits & (1 << (2 * ci + 1)) else -1
        markers.append("+" if a == b == 1 else "-" if a == b == -1 else "x")
    return "".join(markers)


def symmetric_reduced_rows(U, bits, k):
    full = system_rows(unsigned_side_rows(U, k), bits)
    rows = []
    for ci, marker in enumerate(class_pattern(bits)):
        if marker != "x":
            rows.append([
                full[2 * ci][column] + full[2 * ci + 1][column]
                for column in range(8)
            ])
    for t in range(5):
        rows.append([0, 0, 0] + [1 if q == t else 0 for q in range(5)])
    return rows


def check_symmetric(U, representatives):
    payload = load_gz("symmetric_coverage.json.gz")
    assert payload["n_representatives"] == 16570
    rep_set = set(representatives)
    for k in (1, 2):
        split = payload["splits"][str(k)]
        covered = split["covered_bits"]
        residue = split["residue_bits"]
        assert set(covered).isdisjoint(residue)
        assert set(covered) | set(residue) == rep_set
        assert len(covered) == split["n_covered"]
        assert len(residue) == split["n_residue"]
        patterns = split["pattern_certificates"]
        residue_witnesses = split[
            "residue_pattern_strict_primal_witnesses"
        ]
        unsigned = unsigned_side_rows(U, k)
        for bits in covered:
            key = class_pattern(bits)
            assert key in patterns
            B = system_rows(unsigned, bits)
            certificate = patterns[key]
            check_sparse_certificate(B, certificate, 8)
            values = dict(certificate)
            for ci, marker in enumerate(key):
                assert values.get(2 * ci, 0) == values.get(2 * ci + 1, 0)
                if marker == "x":
                    assert values.get(2 * ci, 0) == 0
        checked_residue_patterns = set()
        for bits in residue:
            key = class_pattern(bits)
            assert key in residue_witnesses
            if key in checked_residue_patterns:
                continue
            checked_residue_patterns.add(key)
            witness = [Fraction(value) for value in residue_witnesses[key]]
            rows = symmetric_reduced_rows(U, bits, k)
            assert len(witness) == 8
            margins = [
                sum(Fraction(a) * b for a, b in zip(row, witness))
                for row in rows
            ]
            assert min(margins) > 0


def valid_t0_assignments(ch_rays):
    out = []
    for bits in range(1 << 10):
        signs = [1 if bits & (1 << ci) else -1 for ci in range(10)]
        if all(
            len({signs[side // 2] for side in sides}) > 1
            for sides in ch_rays
        ):
            out.append(bits)
    return out


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


def check_t0_k1(U, ch_rays):
    payload = load_gz("t0_k1_bundle.json.gz")
    valid = valid_t0_assignments(ch_rays)
    assert len(valid) == 200
    assert valid == payload["valid_class_bits"]
    assert payload["k"] == 1
    assert len(payload["certificates"]) == 200
    for bits, certificate in zip(valid, payload["certificates"]):
        check_sparse_certificate(t0_rows(U, bits, 1), certificate, 5)


def main():
    start = time.time()
    U, ch_rays, representatives = check_structure()
    print("checked exact reference structure and exhaustive sigma list", flush=True)
    check_core(U, representatives)
    print("checked all 66,280 core Gordan certificates", flush=True)
    check_symmetric(U, representatives)
    print("checked symmetric-support coverage certificates", flush=True)
    check_t0_k1(U, ch_rays)
    print("checked all 200 T=0 k=1 certificates", flush=True)
    print(
        f"PASS: all Stage 2b exact checks completed in {time.time() - start:.1f}s"
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise
