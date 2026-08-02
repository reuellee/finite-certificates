#!/usr/bin/env python3
"""PART A #4 -- adversarial review of omdecode.py's encode/decode round trip
and the colex basis ordering, using the reviewer's OWN from-scratch codec
(mycodec.py) as ground truth, cross-checked against the real pipeline.

Three tests:
 (1) random-pattern round trip: decode(encode(x)) == x, on MY OWN codec
     alone (already in mycodec.py's self-test) plus many more random keys.
 (2) MY decode of real catalog (hi,lo) rows agrees with
     omdecode.signs_from_keys (i.e. coverage_checker.decode_keys), AND
     encode(MY decode(hi,lo)) reproduces (hi,lo) exactly, for a large
     random sample of real rows.
 (3) realize.py's Geom(9,4).bases0 (0-based) matches, element for element,
     coverage_checker.build_tables(9,4)['bases'] (1-based) minus 1.  This is
     the load-bearing agreement `sweep49.do_chunk`'s `chk == chi` silently
     assumes: chi is decoded in coverage_checker's basis order but checked
     against a matrix verified in realize.py's OWN basis order.

Read-only.  Imports omdecode/coverage_checker/realize ONLY for comparison,
never as the source of truth for the review's own claims.
"""
import os
import sys
import time

sys.dont_write_bytecode = True
os.environ.setdefault('PYTHONDONTWRITEBYTECODE', '1')
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mycodec as mc                                        # noqa: E402

OMREAL = os.path.normpath(os.path.join(HERE, '..'))
sys.path.insert(0, OMREAL)

import numpy as np                                          # noqa: E402
import random

N, R, M = 9, 4, 126


def test1_random_roundtrip(trials=200000, seed=12345):
    rng = random.Random(seed)
    bad = 0
    t0 = time.time()
    for _ in range(trials):
        v = rng.getrandbits(M)
        s = ''.join('1' if (v >> (M - 1 - j)) & 1 else '0' for j in range(M))
        chi = s.replace('1', '+').replace('0', '-')
        hi, lo = mc.encode_key(chi)
        back = mc.decode_key(hi, lo, M)
        if back != chi:
            bad += 1
    print('[A4.1] random-pattern round trip (my own codec only): '
          '%d trials, %d mismatches (%.1fs)' % (trials, bad, time.time() - t0))
    return bad == 0


def test2_real_catalog_crosscheck(nsample=20000, seed=999):
    import omdecode
    hi_arr, lo_arr, stab = omdecode.load_coverage_4_9(verify=True)
    nrows = len(hi_arr)
    rng = random.Random(seed)
    rows = rng.sample(range(nrows), min(nsample, nrows))
    rows_np = np.array(sorted(rows))

    # ground truth via the project's own decoder (coverage_checker), for
    # cross-comparison only -- NOT used as this review's source of truth.
    CHI_theirs = omdecode.signs_from_keys(N, R, hi_arr[rows_np], lo_arr[rows_np])

    mismatches_decode = []
    mismatches_encode = []
    t0 = time.time()
    for k, r in enumerate(rows_np.tolist()):
        hi_i = int(hi_arr[r])
        lo_i = int(lo_arr[r])
        my_chi = mc.decode_key(hi_i, lo_i, M)
        their_chi = ''.join('+' if v > 0 else '-' for v in CHI_theirs[k])
        if my_chi != their_chi:
            mismatches_decode.append((r, my_chi[:20], their_chi[:20]))
        my_hi, my_lo = mc.encode_key(my_chi)
        if my_hi != hi_i or my_lo != lo_i:
            mismatches_encode.append((r, (my_hi, my_lo), (hi_i, lo_i)))
    dt = time.time() - t0
    print('[A4.2] cross-check vs omdecode/coverage_checker.py on %d real '
          'catalog rows (%.1fs):' % (len(rows_np), dt))
    print('   my decode(hi,lo) == coverage_checker decode  : %d/%d agree'
          % (len(rows_np) - len(mismatches_decode), len(rows_np)))
    print('   encode(my decode(hi,lo)) == (hi,lo)           : %d/%d agree'
          % (len(rows_np) - len(mismatches_encode), len(rows_np)))
    if mismatches_decode:
        print('   FIRST DECODE MISMATCHES:', mismatches_decode[:5])
    if mismatches_encode:
        print('   FIRST ENCODE MISMATCHES:', mismatches_encode[:5])
    return not mismatches_decode and not mismatches_encode


def test3_basis_order_agreement():
    import realize as rz
    geom = rz.Geom(N, R)
    mine_0based = geom.bases0                      # 0-based, length M list of tuples

    import omdecode
    T = omdecode._cc().build_tables(N, R)
    theirs_1based = T['bases']                     # 1-based tuples, from coverage_checker

    my_codec_1based = mc.colex_bases(N, R)          # my own from-scratch colex order

    mine_shifted = [tuple(x + 1 for x in t) for t in mine_0based]

    ok_a = (mine_shifted == list(theirs_1based))
    ok_b = (my_codec_1based == list(theirs_1based))
    ok_c = (my_codec_1based == mine_shifted)
    print('[A4.3] basis order agreement (M=%d bases each):' % len(theirs_1based))
    print('   realize.py Geom.bases0 (+1)  == coverage_checker build_tables : %s'
          % ok_a)
    print('   mycodec.py colex_bases       == coverage_checker build_tables : %s'
          % ok_b)
    print('   realize.py Geom.bases0 (+1)  == mycodec.py colex_bases        : %s'
          % ok_c)
    if not ok_a:
        for i, (a, b) in enumerate(zip(mine_shifted, theirs_1based)):
            if a != b:
                print('     first mismatch at index %d: realize=%s vs cc=%s'
                      % (i, a, b))
                break
    return ok_a and ok_b and ok_c


def main():
    r1 = test1_random_roundtrip()
    r2 = test2_real_catalog_crosscheck()
    r3 = test3_basis_order_agreement()
    print()
    print('A4 OVERALL: %s' % ('ALL PASS' if (r1 and r2 and r3) else '*** FAILURE ABOVE ***'))
    return 0 if (r1 and r2 and r3) else 1


if __name__ == '__main__':
    sys.exit(main())
