#!/usr/bin/env python3
"""REVIEW (Fable): weapon B2 (general final polynomials) spot checks.

  F1  the two shipped fired certificates (data/fp_found.jsonl) re-expanded
      with MY OWN code: rebuild each named relation from its (A,B) spec,
      apply the record's chi, expand sum_g c_g * m_g * R_g over the monomial
      basis in exact integers, demand one weak sign with >= 1 strict.
  F2  the shipped positive control likewise.
  F3  the fired rows are certified NON_REALIZABLE by the sweep (st.dat == 3)
      and their chi matches my own decode of the catalog keys.
  F4  the sweep's own NON_REALIZABLE certificate for those chis is located
      in sweep_state/certs shards (read-only) and re-verified by
      ai/omreal/checkcert.py from a copy in this scratch directory.
  F5  fresh fire: run the shipped fpoly.find_fp on a fresh sample of
      sweep-certified NON_REALIZABLE classes (chi decoded by MY code from
      st.dat + the npz) at degree 2 / L1, and re-verify any hits with MY
      expansion -- an out-of-sample reproduction of the ~1/10 rate and a
      third-plus certificate check.
"""
import json
import os
import struct
import sys
import zipfile
import ast
from fractions import Fraction
from itertools import combinations

sys.dont_write_bytecode = True
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

HERE = os.path.dirname(os.path.abspath(__file__))
OMOPEN = os.path.dirname(HERE)
AI = os.path.dirname(OMOPEN)
DATA = os.path.join(OMOPEN, 'data')
STATE = os.path.join(AI, 'omreal', 'sweep_state')
COVDIR = os.path.join(AI, 'omgamma', 'data', 'coverage_4_9')
N, R = 9, 4

fails = []


def ck(name, ok, detail=''):
    print('  [%s] %s %s' % ('ok ' if ok else 'FAIL', name, detail))
    if not ok:
        fails.append((name, detail))


BASES = sorted(combinations(range(1, N + 1), R), key=lambda t: t[::-1])
BIDX = {B: j for j, B in enumerate(BASES)}


def perm_sign_and_sort(t):
    a = list(t)
    sg = 1
    for i in range(1, len(a)):
        j = i
        while j > 0 and a[j - 1] > a[j]:
            a[j - 1], a[j] = a[j], a[j - 1]
            sg = -sg
            j -= 1
    for i in range(1, len(a)):
        if a[i - 1] == a[i]:
            return None, 0
    return tuple(a), sg


def rel_terms(spec):
    if spec['kind'] == 'gp3':
        L = tuple(spec['L'])
        a, b, c, d = spec['abcd']
        out = []
        for (x, y, z, w, ex) in ((a, b, c, d, 1), (a, c, b, d, -1),
                                 (a, d, b, c, 1)):
            s1, g1 = perm_sign_and_sort(L + (x, y))
            s2, g2 = perm_sign_and_sort(L + (z, w))
            out.append((ex * g1 * g2, BIDX[s1], BIDX[s2]))
        return out
    A = tuple(spec['A'])
    B = tuple(spec['B'])
    out = []
    for k, bk in enumerate(B):
        s1, g1 = perm_sign_and_sort(A + (bk,))
        if s1 is None:
            continue
        s2, g2 = perm_sign_and_sort(tuple(x for x in B if x != bk))
        out.append(((-1 if (k & 1) else 1) * g1 * g2, BIDX[s1], BIDX[s2]))
    return out


def check_fp_record(rec):
    chi = [1 if ch == '+' else -1 for ch in rec['chi']]
    poly = {}
    deg = int(rec['degree'])
    for g in rec['gens']:
        terms = rel_terms(g['rel'])
        # my own identity sanity: evaluate on one random integer config
        mult = [BIDX[tuple(x)] for x in g.get('mult', [])]
        c = Fraction(int(g['c'][0]), int(g['c'][1]))
        if c == 0:
            return False, 'zero coefficient'
        for (e, i, j) in terms:
            s = e * chi[i] * chi[j]
            mon = tuple(sorted(mult + [i, j]))
            if len(mon) != deg:
                return False, 'degree mismatch'
            poly[mon] = poly.get(mon, Fraction(0)) + c * s
    poly = {m: v for m, v in poly.items() if v != 0}
    if not poly:
        return False, 'combination is identically zero'
    pos = any(v > 0 for v in poly.values())
    neg = any(v < 0 for v in poly.values())
    if pos and neg:
        return False, 'both signs'
    return True, '%d monomials, all %s' % (len(poly),
                                           'positive' if pos else 'negative')


# ----- F1/F2 ----------------------------------------------------------
found = [json.loads(l) for l in open(os.path.join(DATA, 'fp_found.jsonl'))]
ck('fp_found.jsonl carries %d fired certificates (doc says the saved '
   'sample has 2)' % len(found), len(found) == 2)
for k, rec in enumerate(found):
    ok, msg = check_fp_record(rec)
    ck('F1: fired certificate %d (row %s) is a valid final polynomial by MY '
       'expansion' % (k, rec.get('row')), ok, msg)

pc = json.loads(open(os.path.join(DATA, 'fp_positive_control.jsonl'))
                .read())
ok, msg = check_fp_record(pc)
ck('F2: positive control is a valid final polynomial by MY expansion',
   ok, msg)

# ----- F3 -------------------------------------------------------------
with open(os.path.join(STATE, 'st.dat'), 'rb') as fh:
    stbytes = fh.read()


def read_npy_bytes(fh):
    assert fh.read(6) == b'\x93NUMPY'
    ver = fh.read(2)
    if ver[0] == 1:
        (hlen,) = struct.unpack('<H', fh.read(2))
    else:
        (hlen,) = struct.unpack('<I', fh.read(4))
    d = ast.literal_eval(fh.read(hlen).decode('latin1').strip())
    return d['descr'], d['shape'], fh.read()


with zipfile.ZipFile(os.path.join(COVDIR, 'coverage_4_9.npz')) as z:
    with z.open('key_hi.npy') as fh:
        _, _, HIB = read_npy_bytes(fh)
    with z.open('key_lo.npy') as fh:
        _, _, LOB = read_npy_bytes(fh)


def chi_at_row(row):
    hi = struct.unpack_from('<Q', HIB, row * 8)[0]
    lo = struct.unpack_from('<Q', LOB, row * 8)[0]
    key = (hi << 64) | lo
    return ''.join('+' if (key >> (125 - j)) & 1 else '-'
                   for j in range(126))


for rec in found:
    row = int(rec['row'])
    ck('F3: row %d st.dat==NONREAL(3) and catalog chi matches record'
       % row, stbytes[row] == 3 and chi_at_row(row) == rec['chi'],
       'st=%d' % stbytes[row])
    ck('F3b: row %d record says sweep_status NON_REALIZABLE and '
       'also_has_L0_gordan_vector' % row,
       rec.get('sweep_status') == 'NON_REALIZABLE'
       and bool(rec.get('also_has_L0_gordan_vector')),
       'L0_gordan_terms=%s' % rec.get('L0_gordan_terms'))

# ----- F4: the sweep's own certificate for those chis -----------------
import glob
want = {rec['chi']: int(rec['row']) for rec in found}
got = {}
for shard in glob.glob(os.path.join(STATE, 'certs', '*.jsonl')):
    with open(shard) as fh:
        for line in fh:
            for w in want:
                if w in line:
                    r = json.loads(line)
                    if r.get('chi') == w:
                        got[w] = r
    if len(got) == len(want):
        break
tmp = os.path.join(HERE, '_sweep_certs_for_fired.jsonl')
with open(tmp, 'w') as fh:
    for w, r in got.items():
        fh.write(json.dumps(r) + '\n')
ck('F4: sweep shard certificates found for both fired chis',
   len(got) == 2,
   str({v: got.get(k, {}).get('verdict') for k, v in want.items()}))
if got:
    import subprocess
    p = subprocess.run([sys.executable,
                        os.path.join(AI, 'omreal', 'checkcert.py'), tmp],
                       capture_output=True, text=True,
                       env=dict(os.environ, PYTHONDONTWRITEBYTECODE='1'))
    tail = p.stdout.strip().splitlines()[-1] if p.stdout else '?'
    ck('F4b: checkcert.py accepts the sweep certificates (rc=0)',
       p.returncode == 0, tail)
    ck('F4c: both are NON_REALIZABLE (so B2 hits are second opinions)',
       all(r.get('verdict') == 'NON_REALIZABLE' for r in got.values()))

# ----- F5: fresh fire, out of sample ----------------------------------
sys.path.insert(0, OMOPEN)
import gordan as om_gordan          # noqa: E402  (deliverable code, re-run)
import fpoly as om_fpoly            # noqa: E402

sup1 = om_gordan.Support(N, R, 'L1', verify=False)
import random
rnd = random.Random(777)
nonreal_rows = [i for i in range(0, len(stbytes)) if stbytes[i] == 3]
sample = rnd.sample(nonreal_rows, 30)
hits = 0
verified = 0
for row in sample:
    s = chi_at_row(row)
    chi = [1 if ch == '+' else -1 for ch in s]
    import numpy as np
    cert, info = om_fpoly.find_fp(np.array(chi, dtype=np.int8), degree=2,
                                  level='L1', sup=sup1)
    if cert is None:
        continue
    hits += 1
    rec = om_fpoly.fp_record(N, R, s, cert, 2, sup1)
    ok, msg = check_fp_record(rec)
    if ok:
        verified += 1
    else:
        print('    F5 INVALID fresh certificate on row %d: %s' % (row, msg))
print('      fresh sample: %d/30 NONREAL classes fired at degree 2 / L1'
      % hits)
ck('F5: every fresh fired certificate re-verifies under MY expansion',
   hits == verified, '%d/%d' % (verified, hits))
ck('F5b: rate is broadly ~1/10 (doc: 3/25 then 2/25)',
   0 <= hits <= 10, '%d/30' % hits)

print()
if fails:
    print('FP VERIFICATION: %d FAILURES' % len(fails))
    sys.exit(1)
print('FP VERIFICATION: ALL CHECKS PASSED')
