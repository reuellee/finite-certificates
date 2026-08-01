#!/usr/bin/env python3
"""Canary battery: deliberately broken inputs that MUST be caught.

    python canaries.py

Project discipline: no computation is trusted until the machinery has been
shown to fail on things it is supposed to fail on.  Three families:

  A. CLASSIFICATION canaries -- classes whose answer is known from the
     literature must come back with that answer:
       A1  a random integer point configuration's own chirotope  -> REALIZABLE
       A2  the non-Pappus class, the unique non-realizable uniform rank-3
           OM on 9 elements                                      -> NON_REALIZABLE
       A3  all 24 non-realizable uniform (4,8) classes            -> NON_REALIZABLE
       A4  the 135 uniform (3,8) classes, all stretchable         -> REALIZABLE

  B. CERTIFICATE-REJECTION canaries -- checkcert must REJECT:
       B1  a realization with one matrix entry changed
       B2  a realization whose chirotope string has one bit flipped
       B3  a rank-deficient matrix (a bracket vanishes)
       B4  a Gordan vector with one term dropped
       B5  a Gordan vector with one weight set to 0
       B6  a Gordan vector with one weight negated
       B7  a Gordan vector with all weights zeroed
       B8  a Gordan vector with a term's "big" index moved to a term that
           is NOT the odd one out
       B9  a Gordan vector attached to a DIFFERENT class's sign string

  C. DECODER canaries -- a sign string that violates a Grassmann-Plucker
     relation must be rejected as not a chirotope at all.
"""

import copy
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import checkcert                                           # noqa: E402
import omdecode                                            # noqa: E402
import realize as rz                                       # noqa: E402
import bfp as bfpmod                                       # noqa: E402
import pilot                                               # noqa: E402

FAILS = []


def report(name, ok, detail=''):
    print('  [%s] %-52s %s' % ('ok  ' if ok else 'FAIL', name, detail))
    if not ok:
        FAILS.append(name)


def expect_reject(name, rec):
    ok, msg = checkcert.check_record(rec)
    report(name, not ok, ('WRONGLY ACCEPTED' if ok else 'rejected: ' + msg[:70]))


def main():
    print('== A. classification canaries ==')

    g49 = rz.Geom(9, 4)
    gp49 = bfpmod.GPSystem(9, 4)
    rng = np.random.default_rng(20260801)
    Z = rng.integers(-60, 61, size=(4, 9))
    chi = rz.exact_bracket_signs(Z, g49)
    while chi is None:
        Z = rng.integers(-60, 61, size=(4, 9))
        chi = rz.exact_bracket_signs(Z, g49)
    st = pilot.run(np.array([chi]), 9, 4, None, quiet=True, progress=0)
    report('A1 chirotope of an explicit point set -> REALIZABLE',
           st['REALIZABLE'] == 1, str({k: st[k] for k in
                                       ('REALIZABLE', 'NON_REALIZABLE', 'RESIDUE')}))

    np9 = [json.loads(l) for l in open(os.path.join(HERE, 'certs_3_9.jsonl'))
           if '"NON_REALIZABLE"' in l]
    report('A2a exactly one non-realizable class in (3,9)', len(np9) == 1,
           '%d found (literature: 1, the non-Pappus arrangement)' % len(np9))
    if np9:
        chi3 = omdecode.signs_from_string(np9[0]['chi'])
        st = pilot.run(np.array([chi3]), 9, 3, None, quiet=True, progress=0)
        report('A2b non-Pappus re-classified -> NON_REALIZABLE',
               st['NON_REALIZABLE'] == 1)

    n48 = [json.loads(l) for l in open(os.path.join(HERE, 'certs_4_8.jsonl'))
           if '"NON_REALIZABLE"' in l]
    report('A3a exactly 24 non-realizable classes in (4,8)', len(n48) == 24,
           '%d found (Bokowski-Richter 1990: 24)' % len(n48))
    if n48:
        CH = np.array([omdecode.signs_from_string(r['chi']) for r in n48])
        st = pilot.run(CH, 8, 4, None, quiet=True, progress=0)
        report('A3b all 24 re-classified -> NON_REALIZABLE',
               st['NON_REALIZABLE'] == len(n48),
               '%d/%d' % (st['NON_REALIZABLE'], len(n48)))

    c38 = omdecode.load_catalog_txt(8, 3)
    st = pilot.run(c38, 8, 3, None, quiet=True, progress=0)
    report('A4 all 135 uniform (3,8) classes -> REALIZABLE',
           st['REALIZABLE'] == 135, '%d/135' % st['REALIZABLE'])

    print('== B. certificate-rejection canaries ==')
    good_r = [json.loads(l) for l in open(os.path.join(HERE, 'certs_4_8.jsonl'))
              if '"REALIZABLE"' in l][0]
    ok, msg = checkcert.check_record(good_r)
    report('B0a an honest realization is accepted', ok, msg)
    good_n = n48[0]
    ok, msg = checkcert.check_record(good_n)
    report('B0b an honest Gordan vector is accepted', ok, msg)

    # NB: a +-1 nudge of a well-conditioned integer realization usually
    # lands on ANOTHER valid realization of the same class -- the
    # realization space is open -- so it is not a corruption at all and
    # must be accepted.  A corruption canary has to be one that provably
    # leaves the cell, and the canary itself checks that it does.
    g48 = rz.Geom(8, 4)
    chi_r = omdecode.signs_from_string(good_r['chi'])
    base = np.array(good_r['matrix'], dtype=np.int64)
    for tag, mut in (('one point reflected through the origin',
                      lambda M: (M.__setitem__((slice(None), 2), -M[:, 2]), M)[1]),
                     ('two points exchanged',
                      lambda M: M[:, [1, 0, 2, 3, 4, 5, 6, 7]]),
                     ('one entry scaled by 1000',
                      lambda M: (M.__setitem__((0, 5), M[0, 5] * 1000 + 1), M)[1])):
        M = mut(base.copy())
        s = rz.exact_bracket_signs(M, g48)
        if s is None or not np.array_equal(s, chi_r):
            b = copy.deepcopy(good_r)
            b['matrix'] = [[int(v) for v in row] for row in M]
            expect_reject('B1 corrupted realization (%s)' % tag, b)
            break
    else:
        report('B1 corrupted realization', False,
               'no attempted corruption actually left the cell')
    b = copy.deepcopy(good_r)
    i = 3
    b['chi'] = b['chi'][:i] + ('-' if b['chi'][i] == '+' else '+') + b['chi'][i + 1:]
    expect_reject('B2 one chirotope bit flipped', b)
    b = copy.deepcopy(good_r)
    b['matrix'][0] = list(b['matrix'][1])
    expect_reject('B3 rank-deficient matrix', b)

    b = copy.deepcopy(good_n)
    b['bfp'] = b['bfp'][:-1]
    expect_reject('B4 one Gordan term dropped', b)
    b = copy.deepcopy(good_n)
    b['bfp'][0]['w'] = 0
    expect_reject('B5 one weight zeroed', b)
    b = copy.deepcopy(good_n)
    b['bfp'][0]['w'] = -b['bfp'][0]['w']
    expect_reject('B6 one weight negated', b)
    b = copy.deepcopy(good_n)
    for t in b['bfp']:
        t['w'] = 0
    expect_reject('B7 all weights zeroed (the lambda != 0 check)', b)
    b = copy.deepcopy(good_n)
    t = b['bfp'][0]
    t['big'], t['small'] = t['small'], t['big']
    expect_reject('B8 "big" moved to a term that is not the odd one out', b)
    b = copy.deepcopy(good_n)
    b['chi'] = good_r['chi']
    expect_reject('B9 Gordan vector attached to another class', b)

    print('== C. decoder canaries ==')
    bad = chi.copy()
    C, P = omdecode.gp_parity_table(9, 4, bad)
    i0, i1, c1, i2, i3, c2, i4, i5, c3 = (int(v) for v in C[0])
    # force all three terms of relation 0 to agree by flipping one basis
    for j in (i0, i1, i2, i3, i4, i5):
        t = bad.copy()
        t[j] = -t[j]
        if not omdecode.gp_check(9, 4, t[None, :])[0]:
            report('C1 a GP-violating sign string is rejected as a chirotope',
                   True, 'flipping basis %d breaks a GP relation, as it must' % j)
            bad = t
            break
    else:
        report('C1 a GP-violating sign string is rejected as a chirotope', False)
    try:
        gp49.inequalities(bad)
        report('C2 BFP refuses to run on a non-chirotope', False, 'no error raised')
    except ValueError as e:
        report('C2 BFP refuses to run on a non-chirotope', True, str(e)[:60])

    print('== D. ladder canaries (ladder.py) ==')
    import ladder as ld

    # D1 THE critical one.  If any effort level ever "solves" a class that
    # carries a Gordan vector, the whole residue-vs-effort curve is
    # meaningless -- and worse, the sweep would emit contradictory
    # certificates.  Feed the ladder classes we have PROVED non-realizable.
    nr = []
    for f in ('certs_49_u_0.jsonl', 'certs_49_u_1.jsonl', 'certs_49_u_2.jsonl'):
        if os.path.exists(f):
            nr += [json.loads(l) for l in open(f) if '"NON_REALIZABLE"' in l]
    nr = nr[:8]
    bad = 0
    for rec in nr:
        chi = omdecode.signs_from_string(rec['chi'])
        for name, kind, kw in ld.LEVELS[:5]:
            Z, _ = ld.run_level(chi, g49, kind, kw, seed=4242)
            if Z is not None:
                bad += 1
                break
    report('D1 no ladder level realizes a BFP-certified class',
           bad == 0 and len(nr) > 0,
           '%d classes x 5 levels -> %d spurious realizations' % (len(nr), bad))

    # D2 the ladder must solve easy classes at its cheapest level
    easy = [json.loads(l) for l in open('certs_49_u_0.jsonl')
            if '"REALIZABLE"' in l][:8] if os.path.exists('certs_49_u_0.jsonl') else []
    at1 = 0
    for rec in easy:
        chi = omdecode.signs_from_string(rec['chi'])
        name, kind, kw = ld.LEVELS[0]
        Z, _ = ld.run_level(chi, g49, kind, kw, seed=7)
        if Z is not None and np.array_equal(rz.exact_bracket_signs(Z, g49), chi):
            at1 += 1
    report('D2 easy classes solved at L1, matrices exact',
           at1 == len(easy) and easy, '%d/%d' % (at1, len(easy)))

    # D3 sample-extraction must decode identically to the full artifact
    hi, lo, stab = omdecode.load_coverage_4_9(verify=True)
    take = np.array([3, 5000, 999999, 4000000, 9276594])
    direct = omdecode.signs_from_keys(9, 4, hi[take], lo[take])
    np.savez_compressed('_canary_keys.npz', key_hi=hi[take], key_lo=lo[take],
                        stab=stab[take], row=take.astype(np.int64))
    h2, l2, s2, r2 = ld._load_keys('_canary_keys.npz')
    viaext = omdecode.signs_from_keys(9, 4, h2, l2)
    report('D3 extracted key file decodes identically to the artifact',
           np.array_equal(direct, viaext) and np.array_equal(r2, take))
    os.remove('_canary_keys.npz')

    # D4 curve arithmetic, on synthetic rows with a known answer
    import tempfile
    rows = ([{'chi': 'a%d' % i, 'solved_at': 'L1 C-lite',
              'times': {'L1 C-lite': 1.0}} for i in range(60)]
            + [{'chi': 'b%d' % i, 'solved_at': None,
                'times': {'L1 C-lite': 1.0}} for i in range(40)])
    fn = os.path.join(tempfile.gettempdir(), '_canary_ladder.jsonl')
    with open(fn, 'w') as fh:
        for r in rows:
            fh.write(json.dumps(r) + chr(10))
    import io as _io
    import contextlib
    buf = _io.StringIO()

    class A:
        ladder = fn
        swept = 1000
    with contextlib.redirect_stdout(buf):
        ld.cmd_curve(A())
    txt = buf.getvalue()
    os.remove(fn)
    report('D4 curve arithmetic: 100 residue of 1000 swept, 60 solved -> 4.0000%',
           'FINAL residue 40/1000 = 4.0000%' in txt,
           [l for l in txt.splitlines() if l.startswith('FINAL')][:1])

    print('')
    if FAILS:
        print('CANARIES FAILED: ' + ', '.join(FAILS))
        return 1
    print('ALL CANARIES PASSED')
    return 0


if __name__ == '__main__':
    sys.exit(main())
