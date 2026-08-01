#!/usr/bin/env python3
"""Canaries for the minor pipeline: things that MUST fail, and things that
must be confirmed by a second, independent route.

    python canaries.py --all
    python canaries.py --quick        # everything except the brute-force group

Each canary prints PASS/FAIL and the script exits non-zero on any failure.

SABOTAGE CANARIES (must be caught)
  S1  a deletion index table with two entries swapped -> G1 (Grassmann-
      Plucker validity of the deletion) must fail.
  S2  a contraction sign table with one sign flipped -> G1 must fail.
  S3  a single corrupted sign in the 9-element class -> the deletions that
      see the corrupted basis must change class (or become invalid), and the
      deletion that does NOT see it must be unchanged.  This is the exact
      sensitivity the closure measurement depends on.
  S4  a random 70-bit string that is not a chirotope -> must be rejected as
      invalid, and its (meaningless) key must not be in the catalog.

CONFIRMATION CANARIES (must agree with a second route)
  C1  REALIZABLE classes have NO non-realizable minor.  This is Lemma D +
      Lemma C; a violation would mean the pipeline or a certificate is
      wrong.  Run over every REALIZABLE row available.
  C2  deletions identified as one of the 24 NON-realizable (4,8) classes:
      run the biquadratic-final-polynomial search DIRECTLY on the deletion
      and have ai/omreal/checkcert.py accept the result.  This confirms the
      semantic claim without going through canonicalization at all.
  C3  deletions identified as a REALIZABLE (4,8) class: realize the deletion
      DIRECTLY with ai/omreal/realize.py and have checkcert.py accept the
      matrix.  Same, in the other direction.
  C4  brute-force group canonicalization (bfcanon.py -- maximum over all
      8! * 2^8 * 2 group elements, no colour refinement, no shared code)
      puts each sampled deletion in the same class as the catalog row the
      pipeline assigned it, and in a different class from a catalog row it
      did not assign.
"""

import argparse
import collections
import json
import os
import random
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import minorlib as ml                                       # noqa: E402

OUT = os.path.join(HERE, 'data')
FAILS = []


def report(name, ok, detail=''):
    print('  [%s] %-58s %s' % ('PASS' if ok else 'FAIL', name, detail))
    if not ok:
        FAILS.append(name)


def load_corpus(tag, limit):
    rows = []
    p = os.path.join(OUT, 'minors_%s.jsonl' % tag)
    for line in open(p):
        rows.append(json.loads(line))
        if limit and len(rows) >= limit:
            break
    return rows


# ----------------------------------------------------------------------

def s1_bad_deletion_table(chis):
    M = ml.Minors(9, 4)
    S = np.array([ml.bits_from_string(c) for c in chis], dtype=np.uint8)
    good = ml.gp_ok(8, 4, M.deletions_bits(S).reshape(-1, 70))
    M.DEL[0, 3], M.DEL[0, 17] = M.DEL[0, 17], M.DEL[0, 3]
    bad = ml.gp_ok(8, 4, M.deletions_bits(S).reshape(-1, 70))
    report('S1 swapped deletion index -> GP validity fails',
           bool(good.all()) and not bool(bad.all()),
           'clean %d/%d valid, sabotaged %d/%d'
           % (int(good.sum()), len(good), int(bad.sum()), len(bad)))


def s2_bad_contraction_sign(chis):
    M = ml.Minors(9, 4)
    S = np.array([ml.bits_from_string(c) for c in chis], dtype=np.uint8)
    good = ml.gp_ok(8, 3, M.contractions_bits(S).reshape(-1, 56))
    M.CON_SGN[2, 5] = -M.CON_SGN[2, 5]
    bad = ml.gp_ok(8, 3, M.contractions_bits(S).reshape(-1, 56))
    report('S2 flipped contraction sign -> GP validity fails',
           bool(good.all()) and not bool(bad.all()),
           'clean %d/%d valid, sabotaged %d/%d'
           % (int(good.sum()), len(good), int(bad.sum()), len(bad)))


def s3_corrupt_one_sign(rows, cat48, rng):
    """Flip one basis sign of a 9-element class; the deletions that contain
    that basis must be unaffected and the others must move or break."""
    M = ml.Minors(9, 4)
    bas9 = ml.colex(9, 4)
    ok_moved = ok_fixed = 0
    trials = 0
    for r in rows[:25]:
        S = ml.bits_from_string(r['chi'])[None, :].copy()
        j = rng.randrange(126)
        B = bas9[j]
        S2 = S.copy()
        S2[0, j] ^= 1
        D1 = M.deletions_bits(S)[0]
        D2 = M.deletions_bits(S2)[0]
        for e in range(1, 10):
            same = np.array_equal(D1[e - 1], D2[e - 1])
            if e in B:
                # basis j does not survive the deletion of e
                ok_fixed += 1 if same else 0
            else:
                ok_moved += 1 if not same else 0
            trials += 1
    report('S3 one corrupted sign moves exactly the deletions that see it',
           ok_fixed + ok_moved == trials,
           '%d/%d deletions behaved as required' % (ok_fixed + ok_moved, trials))


def s4_not_a_chirotope(cat48, rng):
    bad = np.array([[rng.randrange(2) for _ in range(70)] for _ in range(200)],
                   dtype=np.uint8)
    v = ml.gp_ok(8, 4, bad)
    nvalid = int(v.sum())
    hi, lo, na, va = ml.canon_keys(8, 4, bad[~v][:20]) if (~v).any() else (
        [], [], [], [])
    inside = sum(1 for h, l in zip(hi, lo) if ml.key128(h, l) in cat48)
    report('S4 random sign strings are not chirotopes and miss the catalog',
           nvalid == 0 and inside == 0,
           '%d/200 passed GP; %d/%d invalid keys landed in cat_4_8'
           % (nvalid, inside, len(hi)))


# ----------------------------------------------------------------------

def c1_realizable_clean(tags):
    n = bad = 0
    for tag in tags:
        p = os.path.join(OUT, 'minors_%s.jsonl' % tag)
        if not os.path.exists(p):
            continue
        for line in open(p):
            r = json.loads(line)
            if r['verdict'] != 'REALIZABLE':
                continue
            n += 1
            if r['del_nonreal'] or r['con_nonreal']:
                bad += 1
    report('C1 no REALIZABLE class has a non-realizable minor', bad == 0,
           '%d realizable rows checked, %d violations' % (n, bad))


def _checkcert(records):
    fd, path = tempfile.mkstemp(suffix='.jsonl')
    os.close(fd)
    with open(path, 'w') as fh:
        for rec in records:
            fh.write(json.dumps(rec) + '\n')
    p = subprocess.run([sys.executable,
                        os.path.join(ml.OMREAL, 'checkcert.py'), path],
                       capture_output=True, text=True)
    os.unlink(path)
    return p.returncode, p.stdout


def c2_bfp_on_deletions(rows, rng, k=25):
    sys.path.insert(0, ml.OMREAL)
    import bfp as bfpmod
    gp = bfpmod.GPSystem(8, 4)
    M = ml.Minors(9, 4)
    pool = [r for r in rows if r['verdict'] == 'NON_REALIZABLE' and r['del_nonreal']]
    if not pool:
        report('C2 direct BFP on the identified non-realizable deletions',
               False, 'no such rows in the corpus')
        return
    sel = rng.sample(pool, min(k, len(pool)))
    recs = []
    misses = 0
    for r in sel:
        S = ml.bits_from_string(r['chi'])[None, :]
        D = M.deletions_bits(S)[0]
        e = r['del_nonreal'][0]
        chi8 = np.where(D[e - 1] == 1, np.int8(1), np.int8(-1))
        cert, _ = bfpmod.find_bfp(chi8, gp)
        if cert is None:
            misses += 1
            continue
        terms = []
        for (ri, big, small, w) in cert['terms']:
            L, abcd, _ = gp.rel[ri]
            terms.append({'L': list(L), 'abcd': list(abcd), 'big': int(big),
                          'small': int(small), 'w': int(w)})
        recs.append({'n': 8, 'r': 4, 'chi': ml.string_from_signs(chi8),
                     'verdict': 'NON_REALIZABLE', 'bfp': terms})
    rc, outp = _checkcert(recs)
    report('C2 direct BFP on the identified non-realizable deletions',
           misses == 0 and rc == 0 and len(recs) == len(sel),
           '%d/%d got a Gordan vector, checkcert rc=%d' % (len(recs), len(sel), rc))


def c3_realize_deletions(rows, rng, k=25):
    sys.path.insert(0, ml.OMREAL)
    import realize as rz
    geom = rz.Geom(8, 4)
    M = ml.Minors(9, 4)
    pool = [r for r in rows if r['verdict'] == 'NON_REALIZABLE']
    sel = rng.sample(pool, min(k, len(pool)))
    recs = []
    misses = 0
    for r in sel:
        S = ml.bits_from_string(r['chi'])[None, :]
        D = M.deletions_bits(S)[0]
        cand = [e for e in range(1, 10) if e not in r['del_nonreal']]
        if not cand:
            continue
        e = rng.choice(cand)
        chi8 = np.where(D[e - 1] == 1, np.int8(1), np.int8(-1))
        Z, _ = rz.realize(chi8, geom, tries=8, sweeps=50, seed=hash(r['chi']) % 10 ** 6)
        if Z is None:
            misses += 1
            continue
        recs.append({'n': 8, 'r': 4, 'chi': ml.string_from_signs(chi8),
                     'verdict': 'REALIZABLE',
                     'matrix': [[int(v) for v in row] for row in Z]})
    rc, outp = _checkcert(recs)
    report('C3 direct realization of the deletions called realizable',
           misses == 0 and rc == 0,
           '%d/%d realized, checkcert rc=%d' % (len(recs), len(sel), rc))


def c4_bruteforce(rows, rng, k=12):
    import bfcanon
    bf = bfcanon.BF(8, 4)
    lines8 = [l.strip() for l in open(os.path.join(OUT, 'cat48_lines.txt'))
              if l.strip()]
    M = ml.Minors(9, 4)
    pool_nr = [r for r in rows if r['del_nonreal']]
    pool_r = [r for r in rows if not r['del_nonreal']]
    sel = (rng.sample(pool_nr, min(k // 2, len(pool_nr)))
           + rng.sample(pool_r, min(k - k // 2, len(pool_r))))
    cache = {}

    def form_of_line(i):
        if i not in cache:
            cache[i] = bf.form(bfcanon.bits_from_string(lines8[i]))
        return cache[i]

    agree = disagree = 0
    sep_ok = sep_bad = 0
    for r in sel:
        S = ml.bits_from_string(r['chi'])[None, :]
        D = M.deletions_bits(S)[0]
        e = rng.randrange(1, 10)
        bits = D[e - 1]
        f = bf.form(bits)
        assigned = r['del_cls'][e - 1]
        if f == form_of_line(assigned):
            agree += 1
        else:
            disagree += 1
        other = assigned
        while other == assigned:
            other = rng.randrange(len(lines8))
        if f != form_of_line(other):
            sep_ok += 1
        else:
            sep_bad += 1
    report('C4 brute-force group canonicalization agrees with the pipeline',
           disagree == 0 and sep_bad == 0,
           '%d/%d agree with the assigned class, %d/%d separated from a '
           'random other class' % (agree, agree + disagree, sep_ok, sep_ok + sep_bad))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', default='sweep')
    ap.add_argument('--limit', type=int, default=3000)
    ap.add_argument('--all', action='store_true')
    ap.add_argument('--quick', action='store_true')
    ap.add_argument('--seed', type=int, default=20260801)
    a = ap.parse_args()

    rng = random.Random(a.seed)
    rows = load_corpus(a.tag, a.limit)
    chis = [r['chi'] for r in rows[:120]]
    z = np.load(os.path.join(OUT, 'cat48_keys.npz'))
    cat48 = {ml.key128(h, l): i for i, (h, l) in enumerate(zip(z['hi'], z['lo']))}

    print('SABOTAGE CANARIES (must be caught)')
    s1_bad_deletion_table(chis)
    s2_bad_contraction_sign(chis)
    s3_corrupt_one_sign(rows, cat48, rng)
    s4_not_a_chirotope(cat48, rng)

    print('CONFIRMATION CANARIES (second route must agree)')
    c1_realizable_clean(['sweep', 'uniform', 'realizable'])
    c2_bfp_on_deletions(rows, rng)
    c3_realize_deletions(rows, rng)
    if a.all and not a.quick:
        c4_bruteforce(rows, rng)
    else:
        print('  [skip] C4 brute-force group canonicalization (use --all)')

    print('\n%s' % ('ALL CANARIES PASSED' if not FAILS
                    else 'FAILURES: ' + ', '.join(FAILS)))
    return 1 if FAILS else 0


if __name__ == '__main__':
    sys.exit(main())
