#!/usr/bin/env python3
"""PART B #1 -- adversarial re-verification of REALIZABLE certificates with
a FRESH, from-scratch checker (mycodec.py: full Leibniz permutation-expansion
determinant, exact Python integers -- algorithmically unrelated to
realize.py's Laplace-by-2x2-minors, checkcert.py's cofactor recursion,
fpcheck.py's Bareiss, or reverify.py's Fraction Gauss-Jordan).

Input: the reservoir sample collected by shard_scan.py
(ai/omreal/review_scratch/sample_realizable.jsonl), drawn from the ACTUAL
sweep certificate shards by a full, independent json.loads pass (0 parse
failures found over all 9,276,454 lines -- see shard_scan.log).

For each sampled record: recompute all 126 determinants exactly (Python
bigints) from the stored matrix, in MY OWN colex order, and require every
one nonzero and sign-matching the stored chi string, position by position.
"""
import json
import os
import random
import sys
import time

sys.dont_write_bytecode = True
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')

HERE = os.path.dirname(os.path.abspath(__file__))
OMREAL_SCRATCH = os.path.normpath(os.path.join(HERE, '..', '..', 'omreal', 'review_scratch'))
sys.path.insert(0, OMREAL_SCRATCH)
import mycodec as mc                                        # noqa: E402

N, R, M = 9, 4, 126
SAMPLE_N = 2500


def main():
    src = os.path.join(OMREAL_SCRATCH, 'sample_realizable.jsonl')
    recs = []
    with open(src) as fh:
        for line in fh:
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    print('[B1] loaded %d reservoir-sampled REALIZABLE records' % len(recs))
    rng = random.Random(424242)
    if len(recs) > SAMPLE_N:
        recs = rng.sample(recs, SAMPLE_N)
    print('[B1] verifying %d of them with a FRESH Leibniz-expansion checker'
          % len(recs))

    bases = mc.colex_bases(N, R)
    assert len(bases) == M

    n_ok = n_bad = n_vanish = n_wrong_len = 0
    bad_examples = []
    max_entry_seen = 0
    t0 = time.time()
    for k, rec in enumerate(recs):
        chi = rec['chi']
        mat = rec['matrix']
        if len(chi) != M or len(mat) != R or any(len(row) != N for row in mat):
            n_wrong_len += 1
            bad_examples.append({'reason': 'shape', 'chi_prefix': chi[:20]})
            continue
        matp = [[int(v) for v in row] for row in mat]
        max_entry_seen = max(max_entry_seen, max(abs(v) for row in matp for v in row))
        sgs = mc.bracket_signs(matp, N, R, bases)
        want = [1 if c == '+' else -1 for c in chi]
        if sgs is None:
            n_vanish += 1
            bad_examples.append({'reason': 'vanishing bracket', 'chi_prefix': chi[:20]})
            continue
        if sgs != want:
            n_bad += 1
            j = next(i for i in range(M) if sgs[i] != want[i])
            bad_examples.append({'reason': 'sign mismatch', 'basis_index': j,
                                  'basis': bases[j], 'got': sgs[j], 'want': want[j],
                                  'chi_prefix': chi[:20]})
            continue
        n_ok += 1
        if (k + 1) % 500 == 0:
            print('  ... %d / %d checked (%.1f s)' % (k + 1, len(recs), time.time() - t0))

    dt = time.time() - t0
    print()
    print('[B1] RESULT over %d sampled REALIZABLE certificates (%.1f s, '
          '%.2f ms/record):' % (len(recs), dt, 1000 * dt / max(len(recs), 1)))
    print('   all 126 brackets nonzero & sign-correct : %d' % n_ok)
    print('   vanishing bracket (non-uniform!)          : %d' % n_vanish)
    print('   sign mismatch (WRONG CERTIFICATE!)         : %d' % n_bad)
    print('   malformed shape                            : %d' % n_wrong_len)
    print('   largest |matrix entry| encountered          : %d' % max_entry_seen)
    if bad_examples:
        print('\n   *** FAILURES ***')
        for b in bad_examples[:20]:
            print('    ', b)
    ok = (n_bad == 0 and n_vanish == 0 and n_wrong_len == 0)
    print('\n[B1] %s' % ('ALL ACCEPTED BY THE FRESH CHECKER' if ok
                          else '*** REJECTIONS FOUND -- SEE ABOVE ***'))

    out = {'n_sampled': len(recs), 'ok': n_ok, 'vanish': n_vanish,
           'wrong_sign': n_bad, 'malformed': n_wrong_len,
           'max_entry': max_entry_seen, 'seconds': round(dt, 1),
           'bad_examples': bad_examples[:50]}
    with open(os.path.join(HERE, 'verify_realizable_result.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
