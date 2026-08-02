#!/usr/bin/env python3
"""PART B #3 -- a THIRD independent implementation re-verifying sampled
NON_REALIZABLE (BFP / Gordan) certificates.

checkcert.py and fpcheck.py have already checked all 203,780 of these
(twice, per FINAL_RESIDUE.md).  This is a THIRD, freshly written exact
Gordan check, built from mycodec.py (which itself is independent of both:
its determinant is Leibniz expansion, unrelated to checkcert's cofactor
recursion or fpcheck's Bareiss elimination -- not that a determinant is
even needed here, since a BFP certificate is checked combinatorially from
the chirotope's sign string alone).

For each sampled record (schema: {'n','r','chi','verdict':'NON_REALIZABLE',
'bfp':[{'L','abcd','big','small','w'}, ...]}):
  - rebuild the three signed terms of each named three-term GP relation
    (L; a,b,c,d) FROM THE CLASS'S OWN chi STRING;
  - independently determine which term is forced to be BIG (the one whose
    sign disagrees with the other two) and confirm it equals the record's
    claimed `big`, and that `small != big`;
  - accumulate  v = e_big1 + e_big2 - e_small1 - e_small2, weighted by the
    record's own integer w > 0;
  - require the accumulated vector to be EXACTLY the zero vector over all
    126 basis coordinates, with at least one term and every weight > 0.

This is precisely Gordan's theorem: sum_i w_i (v_i . u) = 0 while every
v_i . u > 0 is forced by validity, for ANY u -- so no u (hence no
realization) can exist.
"""
import json
import os
import sys
import time

sys.dont_write_bytecode = True
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')

HERE = os.path.dirname(os.path.abspath(__file__))
OMREAL_SCRATCH = os.path.normpath(os.path.join(HERE, '..', '..', 'omreal', 'review_scratch'))
sys.path.insert(0, OMREAL_SCRATCH)
import mycodec as mc                                        # noqa: E402

N, R, M = 9, 4, 126
SAMPLE_N = 600


def check_one(rec, bases, bidx):
    """Returns (ok: bool, reason: str)."""
    chi_str = rec['chi']
    if len(chi_str) != M:
        return False, 'chi length %d != %d' % (len(chi_str), M)
    chi = [1 if c == '+' else -1 for c in chi_str]
    terms = rec.get('bfp')
    if not terms:
        return False, 'empty/missing bfp terms'
    acc = [0] * M
    seen = set()
    for t in terms:
        try:
            L = tuple(int(x) for x in t['L'])
            a, b, c, d = (int(x) for x in t['abcd'])
            big_claimed = int(t['big'])
            small_claimed = int(t['small'])
            w = int(t['w'])
        except (KeyError, TypeError, ValueError) as e:
            return False, 'malformed term: %s' % e
        if w <= 0:
            return False, 'weight %d is not positive' % w
        if not (0 <= big_claimed < 3) or not (0 <= small_claimed < 3):
            return False, 'big/small index out of range'
        if big_claimed == small_claimed:
            return False, 'big == small'
        if len(set(L)) != R - 2 or len({a, b, c, d}) != 4:
            return False, 'malformed relation index sets'
        if set(L) & {a, b, c, d}:
            return False, 'L overlaps {a,b,c,d}'
        if not (a < b < c < d):
            return False, 'a,b,c,d not ascending'
        for x in L + (a, b, c, d):
            if not (1 <= x <= N):
                return False, 'element %d out of range' % x
        key = (L, (a, b, c, d), big_claimed, small_claimed)
        if key in seen:
            return False, 'duplicate inequality %r' % (key,)
        seen.add(key)

        try:
            trip = mc.gp3_terms(L, a, b, c, d, bidx)
        except ValueError as e:
            return False, 'degenerate relation: %s' % e
        big_indep, sgn = mc.gp3_big_index(chi, trip)
        if big_indep < 0:
            return False, ('relation (%r;%d,%d,%d,%d) is monochrome under '
                           'this chirotope: not a valid chirotope, or the '
                           'certificate is bogus' % (L, a, b, c, d))
        if big_indep != big_claimed:
            return False, ('INDEPENDENTLY computed BIG term is %d, '
                           'certificate claims %d, for relation '
                           '(%r;%d,%d,%d,%d) -- signs were %r'
                           % (big_indep, big_claimed, L, a, b, c, d, sgn))
        _, ib, jb = trip[big_claimed]
        _, isr, jsr = trip[small_claimed]
        acc[ib] += w
        acc[jb] += w
        acc[isr] -= w
        acc[jsr] -= w
    nz = [i for i, v in enumerate(acc) if v]
    if nz:
        return False, ('weighted combination does NOT cancel: %d nonzero '
                       'coords, first basis %s value %d'
                       % (len(nz), bases[nz[0]], acc[nz[0]]))
    return True, 'Gordan vector OK: %d terms, total weight %d' % (
        len(terms), sum(int(t['w']) for t in terms))


def main():
    src = os.path.join(OMREAL_SCRATCH, 'sample_nonrealizable.jsonl')
    recs = []
    with open(src) as fh:
        for line in fh:
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    print('[B3] loaded %d reservoir-sampled NON_REALIZABLE records' % len(recs))
    import random
    rng = random.Random(31337)
    if len(recs) > SAMPLE_N:
        recs = rng.sample(recs, SAMPLE_N)
    print('[B3] verifying %d of them with a THIRD independent Gordan checker'
          % len(recs))

    bases = mc.colex_bases(N, R)
    bidx = {B: j for j, B in enumerate(bases)}

    n_ok = n_bad = 0
    bad_examples = []
    n_terms_total = 0
    t0 = time.time()
    for k, rec in enumerate(recs):
        ok, msg = check_one(rec, bases, bidx)
        if ok:
            n_ok += 1
            n_terms_total += len(rec['bfp'])
        else:
            n_bad += 1
            bad_examples.append({'chi_prefix': rec.get('chi', '?')[:20], 'why': msg})
        if (k + 1) % 100 == 0:
            print('  ... %d / %d checked (%.1f s)' % (k + 1, len(recs), time.time() - t0))

    dt = time.time() - t0
    print()
    print('[B3] RESULT over %d sampled NON_REALIZABLE certificates (%.1f s, '
          '%.2f ms/record, %d total inequality terms rebuilt):'
          % (len(recs), dt, 1000 * dt / max(len(recs), 1), n_terms_total))
    print('   Gordan vector independently verified : %d' % n_ok)
    print('   REJECTED                              : %d' % n_bad)
    if bad_examples:
        print('\n   *** FAILURES ***')
        for b in bad_examples[:20]:
            print('    ', b)
    ok = (n_bad == 0)
    print('\n[B3] %s' % ('ALL ACCEPTED BY THE THIRD INDEPENDENT CHECKER' if ok
                          else '*** REJECTIONS FOUND -- SEE ABOVE ***'))

    out = {'n_sampled': len(recs), 'ok': n_ok, 'bad': n_bad,
           'terms_rebuilt': n_terms_total, 'seconds': round(dt, 1),
           'bad_examples': bad_examples[:50]}
    with open(os.path.join(HERE, 'verify_nonrealizable_result.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
