"""Computational verification of certificate transport under the group
action g = (pi, eps) in S_5 x {+-1}^5 (exact arithmetic throughout).

The capstone's equivariance argument transports a certificate for the
labeled system (chi_ref, sigma, s) to one for (g.chi_ref, g.sigma, pi.s).
The bookkeeping being verified here is exactly where an error would hide:

  - C_{lo,hi}(U') = tau * C_{ij}(U) with tau = (+-1) * eps_lo * eps_hi
    (the sign tau decides which RAY of the transported class each original
    side maps to, hence how the sigma bits move);
  - weight rows and split entries permute by pi;
  - D-monomial evaluations are invariant (D'_{T'} = D_{pi^-1 T'}), so the
    transported multiplier vector y' is a re-indexing of y.

Checks:
  1. TRANSPORT: for random g and random certificates from every bundle
     (family closed-form, k=0, prefix sweeps, split02 sweep), specialize
     the certificate to exact row multipliers y at U_ints, transport to
     y', build the transported configuration's 25-row system B' with an
     independent row builder, and verify y' >= 0, y' != 0, B'^T y' = 0.
  2. VALIDITY CLOSURE: for all 10 stabilizer elements of chi_ref, the
     induced sigma-transport maps the 33,140 valid labeled sigmas
     bijectively onto themselves.
  3. FAMILY EQUIVARIANCE: the single-class family criterion is preserved
     by transport (checked on every sampled family item).

Usage: python check_transport.py [--n-group 60] [--n-certs 25] [--seed 7]
"""
from __future__ import annotations

import argparse
import gzip
import itertools
import json
import random
import sys
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
S2 = HERE.parent / "stage2c2_gpt"
sys.path.insert(0, str(S2))

U_INTS = [(-6, -13, 18), (-9, -12, 8), (-13, -4, 16), (4, -19, -8),
          (16, 15, -12)]
PAIRS = list(itertools.combinations(range(5), 2))
TRIPLES = list(itertools.combinations(range(5), 3))


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def det3(a, b, c):
    return sum(x * y for x, y in zip(a, cross(b, c)))


def dabs_of(U):
    return {t: abs(det3(U[t[0]], U[t[1]], U[t[2]])) for t in TRIPLES}


def rows_for(U, bits, split):
    """The 25-row labeled system for configuration U (independent builder)."""
    D = dabs_of(U)
    rows = []
    for ci, (i, j) in enumerate(PAIRS):
        C = cross(U[i], U[j])
        for side, orient in ((2 * ci, 1), (2 * ci + 1, -1)):
            sg = 1 if bits >> side & 1 else -1
            wrow = [0 if t in (i, j) else split[t] * D[tuple(sorted((t, i, j)))]
                    for t in range(5)]
            rows.append([sg * orient * c for c in C] + [sg * w for w in wrow])
    for t in range(5):
        rows.append([0] * 3 + [1 if x == t else 0 for x in range(5)])
    return rows


def apply_g(pi, eps, U):
    """U' with u'_i = eps_i * u_{pi^-1(i)}."""
    inv = [pi.index(i) for i in range(5)]
    return [tuple(eps[i] * c for c in U[inv[i]]) for i in range(5)]


def side_map(pi, eps):
    """side index in B(U,...) -> side index in B(U',...), from
    C_{lo,hi}(U') = tau * C_{ij}(U)."""
    mapping = {}
    for ci, (i, j) in enumerate(PAIRS):
        a, b = pi[i], pi[j]
        lo, hi = min(a, b), max(a, b)
        ci2 = PAIRS.index((lo, hi))
        tau = eps[lo] * eps[hi] * (1 if a < b else -1)
        if tau == 1:
            mapping[2 * ci] = 2 * ci2          # + ray -> + ray
            mapping[2 * ci + 1] = 2 * ci2 + 1
        else:
            mapping[2 * ci] = 2 * ci2 + 1      # + ray -> - ray
            mapping[2 * ci + 1] = 2 * ci2
    return mapping

def transport_bits(pi, eps, bits):
    smap = side_map(pi, eps)
    out = 0
    for side in range(20):
        if bits >> side & 1:
            out |= 1 << smap[side]
    return out


def transport_split(pi, split):
    inv = [pi.index(i) for i in range(5)]
    return tuple(split[inv[t]] for t in range(5))


def transport_y(pi, eps, y):
    """y (dict row->Fraction over 20 sides + 5 weight rows) -> y'."""
    smap = side_map(pi, eps)
    out = {}
    for row, v in y.items():
        if row < 20:
            out[smap[row]] = v
        else:
            out[20 + pi[row - 20]] = v
    return out


def flip_bits(bits):
    """The global flip on sigma: negate AND swap the two rays per class,
    so that Row(flip sigma, -s; ci, r) = Row(sigma, s; ci, -r)."""
    out = 0
    for ci in range(10):
        if not (bits >> (2 * ci + 1) & 1):
            out |= 1 << (2 * ci)
        if not (bits >> (2 * ci) & 1):
            out |= 1 << (2 * ci + 1)
    return out


def flip_y(y):
    """Transport of multipliers under the flip: swap rays, keep weights."""
    out = {}
    for row, v in y.items():
        if row < 20:
            out[row ^ 1] = v
        else:
            out[row] = v
    return out


def family_class(bits, split):
    for ci, (i, j) in enumerate(PAIRS):
        sp = 1 if bits >> (2 * ci) & 1 else -1
        sm = 1 if bits >> (2 * ci + 1) & 1 else -1
        if sp == sm and all(sp * split[t] == -1
                            for t in range(5) if t not in (i, j)):
            return ci
    return None


def specialize(cert, table, D):
    """Certificate [(var_idx, coeff), ...] -> exact row multipliers y."""
    y = {}
    for vi, c in cert:
        kind, idx, mono = table[int(vi)]
        val = Fraction(str(c))
        for tix, e in enumerate(mono):
            if e:
                val *= Fraction(D[TRIPLES[tix]]) ** e
        row = idx if kind == "side" else 20 + idx
        y[row] = y.get(row, Fraction(0)) + val
    return y


def family_y(bits, split, D):
    ci = family_class(bits, split)
    i, j = PAIRS[ci]
    y = {2 * ci: Fraction(1), 2 * ci + 1: Fraction(1)}
    for t in range(5):
        if t not in (i, j):
            y[20 + t] = 2 * Fraction(D[tuple(sorted((t, i, j)))])
    return y


def load_gz(path):
    with gzip.open(path, "rt", encoding="utf-8") as h:
        return json.load(h)


def collect_items(rng, n_certs):
    """Sample (bits, split, cert-or-None) items across all bundles."""
    from gp_degree3_search import monomials_of_degree
    table = []
    for side in range(20):
        for m in monomials_of_degree(2):
            table.append(("side", side, m))
    for t in range(5):
        for m in monomials_of_degree(3):
            table.append(("weight", t, m))
    # degree-3 table for split02 escalations, if any
    table3 = []
    for side in range(20):
        for m in monomials_of_degree(3):
            table3.append(("side", side, m))
    for t in range(5):
        for m in monomials_of_degree(4):
            table3.append(("weight", t, m))

    pools = []
    for si in range(4):
        d = load_gz(S2 / f"gp_all_d2_shard_0{si}_of_04.json.gz")
        pools += [(int(r["sigma_bits"]),
                   tuple(1 if t < r["k"] else -1 for t in range(5)),
                   r["outcome"]["certificate"], table) for r in d["results"]]
    d = load_gz(S2 / "k0_cellwide_shard_00_of_01.json.gz")
    for r in d["results"]:
        if r["outcome"]["status"] == "EXACT_CELLWIDE_CERTIFICATE":
            pools.append((int(r["sigma_bits"]), (-1,) * 5,
                          r["outcome"]["certificate"], table))
        else:
            pools.append((int(r["sigma_bits"]), (-1,) * 5, None, None))
    for si in range(4):
        p = HERE / f"split02_cellwide_shard_0{si}_of_04.json.gz"
        if p.exists():
            d = load_gz(p)
            for r in d["results"]:
                o = r["outcome"]
                if o["status"] == "EXACT_CELLWIDE_CERTIFICATE":
                    tb = table3 if o.get("degree") == 3 else table
                    pools.append((int(r["sigma_bits"]), tuple(r["split"]),
                                  o["certificate"], tb))
                else:
                    pools.append((int(r["sigma_bits"]), tuple(r["split"]),
                                  None, None))
    # family-only items (k=1,2 prefix): sample some VALID_BITS with criterion
    from common import VALID_BITS
    fam = []
    for k in (1, 2):
        split = tuple(1 if t < k else -1 for t in range(5))
        for bits in rng.sample(list(VALID_BITS), 400):
            if family_class(bits, split) is not None:
                fam.append((bits, split, None, None))
    return rng.sample(pools, n_certs) + rng.sample(fam, min(len(fam),
                                                            n_certs // 2))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-group", type=int, default=60)
    ap.add_argument("--n-certs", type=int, default=25)
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    rng = random.Random(args.seed)

    D_ref = dabs_of(U_INTS)
    items = collect_items(rng, args.n_certs)
    print(f"sampled {len(items)} certificates/family items", flush=True)

    # group elements: all 10 stabilizer elements + random ones
    from check_split_orbits import chirotope, act
    chi_ref = chirotope(U_INTS)
    stab = []
    for pi in itertools.permutations(range(5)):
        for eb in range(32):
            eps = tuple(1 if eb >> i & 1 else -1 for i in range(5))
            if act(pi, eps, chi_ref) == chi_ref:
                stab.append((pi, eps))
    assert len(stab) == 10
    gs = list(stab)
    while len(gs) < args.n_group:
        pi = tuple(rng.sample(range(5), 5))
        eps = tuple(rng.choice((1, -1)) for _ in range(5))
        gs.append((pi, eps))

    # 1. TRANSPORT
    checked = fam_checked = 0
    for (pi, eps) in gs:
        U2 = apply_g(pi, eps, U_INTS)
        for (bits, split, cert, table) in items:
            y = (specialize(cert, table, D_ref) if cert is not None
                 else family_y(bits, split, D_ref))
            if any(v < 0 for v in y.values()) or not any(
                    v > 0 for v in y.values()):
                raise SystemExit(f"BAD y at source ({bits}, {split})")
            bits2 = transport_bits(pi, eps, bits)
            split2 = transport_split(pi, split)
            y2 = transport_y(pi, eps, y)
            B2 = rows_for(U2, bits2, split2)
            for col in range(8):
                if sum(v * B2[r][col] for r, v in y2.items()) != 0:
                    raise SystemExit(
                        f"TRANSPORT FAIL: g=({pi},{eps}) system ({bits},"
                        f"{split}) column {col}")
            checked += 1
            if cert is None and family_class(bits, split) is not None:
                if family_class(bits2, split2) is None:
                    raise SystemExit(
                        f"FAMILY EQUIVARIANCE FAIL: g=({pi},{eps}) "
                        f"({bits},{split})")
                fam_checked += 1

    # 1b. FLIP: the same certificates kill (flip sigma, -s) via ray swap
    flip_checked = 0
    for (bits, split, cert, table) in items:
        y = (specialize(cert, table, D_ref) if cert is not None
             else family_y(bits, split, D_ref))
        bitsF = flip_bits(bits)
        splitF = tuple(-x for x in split)
        yF = flip_y(y)
        BF = rows_for(U_INTS, bitsF, splitF)
        for col in range(8):
            if sum(v * BF[r][col] for r, v in yF.items()) != 0:
                raise SystemExit(f"FLIP FAIL: system ({bits},{split}) "
                                 f"column {col}")
        flip_checked += 1
    print(f"FLIP OK: {flip_checked} certificates re-verified on their "
          f"flip partners", flush=True)
    print(f"TRANSPORT OK: {checked} (g, certificate) pairs verified "
          f"exactly ({fam_checked} family-criterion transports)", flush=True)

    # 2. VALIDITY CLOSURE under the stabilizer
    from common import VALID_BITS
    valid = set(VALID_BITS)
    for (pi, eps) in stab:
        image = {transport_bits(pi, eps, b) for b in valid}
        if image != valid:
            raise SystemExit(f"VALIDITY CLOSURE FAIL at stabilizer element "
                             f"({pi}, {eps})")
    print(f"VALIDITY CLOSURE OK: all {len(stab)} stabilizer elements map "
          f"the {len(valid)} valid sigmas onto themselves", flush=True)
    print("ALL TRANSPORT CHECKS PASS")


if __name__ == "__main__":
    main()
