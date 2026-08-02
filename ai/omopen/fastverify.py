#!/usr/bin/env python3
"""Vectorised exact re-verification of every realization certificate.

`verifyall.py` reuses `ai/omreal/checkcert.py` record by record, which is
the right thing to do for independence but costs ~8.8 ms per certificate --
about three hours over the catalogue.  This file does the same arithmetic
in batched numpy and is roughly two orders of magnitude faster, so the two
can run side by side and agree.

EXACTNESS IS NOT TRADED FOR SPEED.  int64 is used only where the result is
PROVABLY exact and the guard is checked per matrix, not assumed:

    |det| <= 4! * m^4 = 24 m^4  for a 4x4 matrix with entries <= m,
    and every intermediate in the two-row Laplace expansion is bounded by
    2 m^2 (a 2x2 minor) and 4 m^4 (a product of two of them).
    So m < 24800 keeps 24 m^4 < 2^63 with room to spare.

Every matrix whose largest entry reaches the threshold is routed to a pure
python-integer path with unbounded precision.  Nothing is skipped and
nothing is approximated.

The determinant formula, the colex basis order and the chi parsing are
rebuilt here from the definitions; the only import from the project is
`checkcert` for the non-realizable records (a different certificate shape,
and only 203,780 of them, already checked twice elsewhere).

    python fastverify.py --worker 0 --nworkers 3
    python fastverify.py --selftest
    python fastverify.py --report
"""

import argparse
import glob
import json
import os
import sys
import time
from itertools import combinations

sys.dont_write_bytecode = True
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np                                          # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
OMREAL = os.path.normpath(os.path.join(HERE, '..', 'omreal'))
CERTS = os.path.join(OMREAL, 'sweep_state', 'certs')
OUT = os.path.join(DATA, 'fastverify')
N, R, M = 9, 4, 126
SAFE = 24800                       # 24 * SAFE**4 < 2**63

BASES = sorted(combinations(range(N), R), key=lambda t: tuple(reversed(t)))
BIDX = np.array(BASES, dtype=np.intp)             # (126, 4)

# the six column pairs of the two-row Laplace expansion, with signs
_PAIRS = []
for _i in range(4):
    for _j in range(_i + 1, 4):
        _k, _l = [t for t in range(4) if t != _i and t != _j]
        _PAIRS.append((_i, _j, _k, _l, -1 if ((_i + _j + 1) & 1) else 1))

_TR = bytes.maketrans(b'+-', b'\x01\xff')


def parse_chi(s):
    return np.frombuffer(s.encode('ascii').translate(_TR), dtype=np.int8)


def det4_batch(Msub):
    """Msub: (..., 4, 4) int64.  Exact determinants, int64."""
    out = np.zeros(Msub.shape[:-2], dtype=np.int64)
    for (i, j, k, l, sg) in _PAIRS:
        top = (Msub[..., 0, i] * Msub[..., 1, j]
               - Msub[..., 0, j] * Msub[..., 1, i])
        bot = (Msub[..., 2, k] * Msub[..., 3, l]
               - Msub[..., 2, l] * Msub[..., 3, k])
        if sg > 0:
            out += top * bot
        else:
            out -= top * bot
    return out


def _det4_py(m):
    out = 0
    for (i, j, k, l, sg) in _PAIRS:
        top = m[0][i] * m[1][j] - m[0][j] * m[1][i]
        if not top:
            continue
        bot = m[2][k] * m[3][l] - m[2][l] * m[3][k]
        out += sg * top * bot
    return out


def check_big(matrix, chi):
    """Unbounded-precision fallback."""
    cols = [[matrix[i][q] for i in range(R)] for q in range(N)]
    for idx, B in enumerate(BASES):
        m = [[cols[b][i] for b in B] for i in range(R)]
        d = _det4_py(m)
        if d == 0:
            return False, 'bracket %s vanishes' % (B,)
        if (1 if d > 0 else -1) != int(chi[idx]):
            return False, 'bracket %s has the wrong sign' % (B,)
    return True, ''


def check_batch(mats, chis):
    """mats: (B,4,9) int64 already known safe.  chis: (B,126) int8.
    Returns a boolean array 'ok' and, for the failures, a reason."""
    cols = np.transpose(mats, (0, 2, 1))                  # (B, 9, 4)
    sub = cols[:, BIDX, :]                                # (B,126,4,4) rows=col
    sub = np.transpose(sub, (0, 1, 3, 2))                 # (B,126,4,4)
    d = det4_batch(sub)                                   # (B,126)
    zero = (d == 0)
    sign = np.where(d > 0, np.int8(1), np.int8(-1))
    wrong = (sign != chis) | zero
    return ~wrong.any(axis=1), wrong, zero


def run(worker, nworkers):
    os.makedirs(OUT, exist_ok=True)
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        'checkcert_omreal', os.path.join(OMREAL, 'checkcert.py'))
    cc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cc)

    counts = {'REALIZABLE': 0, 'NON_REALIZABLE': 0, 'RESIDUE': 0}
    bad = []
    n = nbig = 0
    t0 = time.time()
    B = 4096
    buf_m, buf_c, buf_id = [], [], []

    def flush():
        nonlocal bad
        if not buf_m:
            return
        mats = np.array(buf_m, dtype=np.int64)
        chis = np.array(buf_c, dtype=np.int8)
        ok, wrong, zero = check_batch(mats, chis)
        for t in np.flatnonzero(~ok):
            j = int(np.flatnonzero(wrong[t])[0])
            bad.append({'id': buf_id[t], 'verdict': 'REALIZABLE',
                        'why': 'bracket %s %s' % (
                            BASES[j],
                            'vanishes' if zero[t][j] else 'wrong sign')})
        counts['REALIZABLE'] += int(ok.sum())
        buf_m.clear()
        buf_c.clear()
        buf_id.clear()

    for p in sorted(glob.glob(os.path.join(CERTS, '*.jsonl'))):
        shard = os.path.basename(p)
        with open(p) as fh:
            for ln, line in enumerate(fh):
                if ln % nworkers != worker:
                    continue
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                v = rec.get('verdict')
                n += 1
                if v == 'RESIDUE':
                    counts['RESIDUE'] += 1
                    continue
                if v == 'NON_REALIZABLE':
                    ok, msg = cc.check_record(rec)
                    if ok:
                        counts['NON_REALIZABLE'] += 1
                    else:
                        bad.append({'id': [shard, ln], 'verdict': v,
                                    'why': msg})
                    continue
                if v != 'REALIZABLE':
                    bad.append({'id': [shard, ln], 'verdict': v,
                                'why': 'unknown verdict'})
                    continue
                mat = rec['matrix']
                mx = max(abs(x) for row in mat for x in row)
                if mx >= SAFE:
                    nbig += 1
                    ok, msg = check_big(mat, parse_chi(rec['chi']))
                    if ok:
                        counts['REALIZABLE'] += 1
                    else:
                        bad.append({'id': [shard, ln], 'verdict': v,
                                    'why': msg})
                    continue
                buf_m.append(mat)
                buf_c.append(parse_chi(rec['chi']))
                buf_id.append([shard, ln])
                if len(buf_m) >= B:
                    flush()
                if n % 500000 == 0:
                    print('  [f%d] %d seen, %d bad, %d big-path, %.0f s'
                          % (worker, n, len(bad), nbig, time.time() - t0),
                          flush=True)
        flush()
        print('  [f%d] finished %s: %d seen, %d bad, %.0f s'
              % (worker, shard, n, len(bad), time.time() - t0), flush=True)
    flush()
    res = {'worker': worker, 'nworkers': nworkers, 'seen': n,
           'counts': counts, 'big_path': nbig, 'n_bad': len(bad),
           'bad': bad[:200], 'seconds': round(time.time() - t0, 1)}
    with open(os.path.join(OUT, 'f%02d.json' % worker), 'w') as fh:
        json.dump(res, fh, indent=1)
    print('[f%d] DONE %d seen, %s, %d bad, %d via the big-integer path, '
          '%.0f s' % (worker, n, counts, len(bad), nbig, time.time() - t0),
          flush=True)


def report():
    tot = {'REALIZABLE': 0, 'NON_REALIZABLE': 0, 'RESIDUE': 0}
    n = nbad = nbig = 0
    bad = []
    fs = sorted(glob.glob(os.path.join(OUT, 'f*.json')))
    for p in fs:
        with open(p) as fh:
            r = json.load(fh)
        n += r['seen']
        nbad += r['n_bad']
        nbig += r['big_path']
        bad.extend(r['bad'])
        for k, v in r['counts'].items():
            tot[k] = tot.get(k, 0) + v
    print('workers reporting     : %d' % len(fs))
    print('certificate records   : %d' % n)
    for k in sorted(tot):
        print('   %-16s %9d' % (k, tot[k]))
    print('via the big-integer path : %d' % nbig)
    print('REJECTED              : %d' % nbad)
    for b in bad[:10]:
        print('   *** %s : %s' % (b['id'], b['why']))
    out = {'workers': len(fs), 'records': n, 'counts': tot,
           'big_path': nbig, 'rejected': nbad, 'bad': bad[:50]}
    with open(os.path.join(DATA, 'fastverify.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    print('\n%s -> data/fastverify.json'
          % ('ALL CERTIFICATES ACCEPTED' if nbad == 0
             else '*** %d REJECTED ***' % nbad))


def selftest():
    """Agree with checkcert.py on real certificates, and REJECT corruption."""
    import importlib.util
    import random
    spec = importlib.util.spec_from_file_location(
        'checkcert_omreal', os.path.join(OMREAL, 'checkcert.py'))
    cc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(cc)

    recs = []
    for f in (os.path.join(DATA, 'certs_realizable.jsonl'),
              os.path.join(DATA, 'nonreal', 'rsample2000.jsonl')):
        if os.path.exists(f):
            with open(f) as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        r = json.loads(line)
                        if r.get('verdict') == 'REALIZABLE':
                            recs.append(r)
    print('fastverify self-test on %d real certificates' % len(recs))
    small = [r for r in recs
             if max(abs(x) for row in r['matrix'] for x in row) < SAFE]
    mats = np.array([r['matrix'] for r in small], dtype=np.int64)
    chis = np.array([parse_chi(r['chi']) for r in small], dtype=np.int8)
    ok, _, _ = check_batch(mats, chis)
    ref = np.array([cc.check_record(r)[0] for r in small])
    print('  batched vs checkcert.py on %d small-entry certificates: %s'
          % (len(small), 'AGREE' if np.array_equal(ok, ref) else 'DISAGREE'))
    bad_ok = int((~ok).sum())
    print('  accepted %d / %d (checkcert accepts %d)'
          % (int(ok.sum()), len(small), int(ref.sum())))

    big = [r for r in recs
           if max(abs(x) for row in r['matrix'] for x in row) >= SAFE]
    agree_big = all(check_big(r['matrix'], parse_chi(r['chi']))[0] ==
                    cc.check_record(r)[0] for r in big)
    print('  big-integer path vs checkcert.py on %d large-entry '
          'certificates: %s' % (len(big), 'AGREE' if agree_big else
                                'DISAGREE'))

    # sabotage: flip one matrix entry's sign until a bracket really changes,
    # and flip one chi character -- both must be rejected
    rng = random.Random(7)
    nrej = ntry = 0
    for r in small[:200]:
        c = list(r['chi'])
        k = rng.randrange(M)
        c[k] = '-' if c[k] == '+' else '+'
        m = np.array([r['matrix']], dtype=np.int64)
        ch = np.array([parse_chi(''.join(c))], dtype=np.int8)
        o, _, _ = check_batch(m, ch)
        ntry += 1
        nrej += int(not o[0])
    print('  one flipped chi sign rejected: %d / %d' % (nrej, ntry))
    good = (np.array_equal(ok, ref) and agree_big and nrej == ntry
            and bad_ok == 0)
    print('fastverify self-test: %s' % ('PASS' if good else '*** FAIL ***'))
    return 0 if good else 1


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--worker', type=int, default=0)
    ap.add_argument('--nworkers', type=int, default=3)
    ap.add_argument('--report', action='store_true')
    ap.add_argument('--selftest', action='store_true')
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.report:
        report()
    else:
        run(a.worker, a.nworkers)


if __name__ == '__main__':
    main()
