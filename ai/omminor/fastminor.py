#!/usr/bin/env python3
"""The MINOR TEST as a production filter, and what it costs.

    python fastminor.py --n 800

THE TEST.  Given a uniform (4,9) chirotope chi, decide whether any of its
nine deletions is one of the 24 non-realizable (4,8) classes.  A hit is a
proof of non-realizability (Lemma D) and carries a certificate for free
(liftcert.py).

TWO STAGES, both exact.

  Stage 1 (cheap, vectorised).  Compute the mutable-basis mask of all nine
  deletions at once and from it

      deg(i)  = #mutable bases containing i
      m2(i,j) = #mutable bases containing both i and j
      comp(i) = ( deg(i), sorted multiset over j != i of (m2(i,j), deg(j)) )
      inv     = ( #mutable bases, sorted multiset of deg, sorted multiset
                  of comp )

  Mutability is unchanged by reorientation and by the global sign and is
  permuted by relabelling (OMGAMMA.md section 2 / canonical_convention item
  1), so deg and m2 are permuted and every sorted multiset above is an
  invariant of the G'-orbit.  If delta is one of the 24 then inv(delta) is
  one of THEIR invariant values; deletions whose invariant is not in that
  set are certified NOT to be one of the 24, with no canonicalization at
  all.  (`comp` is the first refinement round of the canonical convention's
  colouring, aggregated into a multiset; using only (#mutable, sorted deg)
  leaves 33% of deletions to stage 2, adding `comp` leaves 0.5%.)

  Stage 2 (exact, expensive).  Canonicalize the survivors and test the key
  against the 24 keys.

Stage 1 can only produce FALSE POSITIVES, never false negatives, so the
composition is exact.  What it buys is measured here: the survivor rate and
the resulting milliseconds per class, against the sweep's own 26-30 ms of
tree walking and ~250 ms of biquadratic-final-polynomial search.
"""

import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import minorlib as ml                                       # noqa: E402

OUT = os.path.join(HERE, 'data')


def invariants(bits, n=8, r=4, refine=True):
    """(B, M) sign bits -> list of hashable G'-invariants."""
    C = ml.cc()
    T = ml.tables(n, r)
    p1, p2, p3 = C.gp_parities(T, bits)
    mut = C.mutable_mask(T, p1, p2, p3)
    mi = mut.astype(np.int16)
    deg = mi @ T['INB']                            # (B, n)
    nm = mut.sum(axis=1)
    ds = np.sort(deg, axis=1)
    if not refine:
        return [(int(nm[i]), tuple(int(x) for x in ds[i]))
                for i in range(len(bits))]
    pr = mi @ T['PR']                              # (B, npairs)
    PI, PJ = T['PI'], T['PJ']
    out = []
    m2 = np.zeros((n, n), dtype=np.int32)
    for i in range(len(bits)):
        m2[:] = 0
        m2[PI, PJ] = pr[i]
        m2[PJ, PI] = pr[i]
        d = deg[i]
        comp = tuple(sorted(
            (int(d[a]),) + tuple(sorted((int(m2[a][b]), int(d[b]))
                                        for b in range(n) if b != a))
            for a in range(n)))
        out.append((int(nm[i]), tuple(int(x) for x in ds[i]), comp))
    return out


class MinorTest(object):
    def __init__(self):
        z = np.load(os.path.join(OUT, 'cat48_keys.npz'))
        lines = [l.strip() for l in open(os.path.join(OUT, 'cat48_lines.txt'))
                 if l.strip()]
        nr = [int(x) for x in z['nonreal']]
        self.K24 = set(ml.key128(z['hi'][i], z['lo'][i]) for i in nr)
        S = np.array([ml.bits_from_string(lines[i]) for i in nr], dtype=np.uint8)
        self.INV24 = set(invariants(S))
        self.M = ml.Minors(9, 4)
        self.stage1 = 0
        self.stage2 = 0

    def test(self, chis):
        """chis: list of 126-char strings -> list of lists of witnessing e."""
        S = np.array([ml.bits_from_string(c) for c in chis], dtype=np.uint8)
        B = len(S)
        D = np.ascontiguousarray(self.M.deletions_bits(S).reshape(B * 9, -1))
        inv = invariants(D)
        cand = [i for i, v in enumerate(inv) if v in self.INV24]
        self.stage1 += B * 9
        self.stage2 += len(cand)
        out = [[] for _ in range(B)]
        if cand:
            hi, lo, _na, _va = ml.canon_keys(8, 4, D[cand], batch=400)
            for j, i in enumerate(cand):
                if ml.key128(hi[j], lo[j]) in self.K24:
                    out[i // 9].append(i % 9 + 1)
        return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--n', type=int, default=800)
    ap.add_argument('--corpus', default=os.path.join(OUT, 'harvest_uniform.jsonl'))
    ap.add_argument('--minors', default=os.path.join(OUT, 'minors_sweep.jsonl'))
    a = ap.parse_args()

    mt = MinorTest()
    print('the 24 non-realizable (4,8) classes take %d distinct invariant '
          'values' % len(mt.INV24))

    # ---- workload 1: a realistic population (mostly realizable) ----
    pool = []
    for line in open(a.corpus):
        r = json.loads(line)
        pool.append((r['chi'], r['verdict']))
    pool = pool[:a.n]
    t0 = time.time()
    res = []
    for i in range(0, len(pool), 100):
        res.extend(mt.test([c for c, _ in pool[i:i + 100]]))
    el = time.time() - t0
    hits = sum(1 for x in res if x)
    print('\nWORKLOAD 1: %d classes from %s (%s)'
          % (len(pool), os.path.basename(a.corpus),
             ', '.join('%s=%d' % (k, sum(1 for _, v in pool if v == k))
                       for k in sorted(set(v for _, v in pool)))))
    print('  %.2f ms/class  |  stage-1 survivors %d/%d (%.2f%%)  |  %d classes '
          'with a witness' % (1000 * el / len(pool), mt.stage2, mt.stage1,
                              100 * mt.stage2 / max(mt.stage1, 1), hits))
    w1 = {'n': len(pool), 'ms_per_class': 1000 * el / len(pool),
          'stage1': mt.stage1, 'stage2': mt.stage2, 'hits': hits}

    # ---- agreement with the full pipeline on the non-realizable corpus ----
    mt2 = MinorTest()
    rows = []
    for line in open(a.minors):
        rows.append(json.loads(line))
        if len(rows) >= a.n:
            break
    t0 = time.time()
    out = []
    for i in range(0, len(rows), 100):
        out.extend(mt2.test([r['chi'] for r in rows[i:i + 100]]))
    el2 = time.time() - t0
    dis = sum(1 for r, o in zip(rows, out) if sorted(o) != sorted(r['del_nonreal']))
    print('\nWORKLOAD 2: %d rows of %s (non-realizable-heavy)'
          % (len(rows), os.path.basename(a.minors)))
    print('  %.2f ms/class  |  stage-1 survivors %d/%d (%.2f%%)  |  '
          'disagreements with the full pipeline: %d'
          % (1000 * el2 / len(rows), mt2.stage2, mt2.stage1,
             100 * mt2.stage2 / max(mt2.stage1, 1), dis))
    w2 = {'n': len(rows), 'ms_per_class': 1000 * el2 / len(rows),
          'stage1': mt2.stage1, 'stage2': mt2.stage2, 'disagreements': dis}

    json.dump({'workload_population': w1, 'workload_nonrealizable': w2,
               'n_invariants_24': len(mt.INV24)},
              open(os.path.join(OUT, 'fastminor.json'), 'w'), indent=1)
    return 1 if dis else 0


if __name__ == '__main__':
    sys.exit(main())
