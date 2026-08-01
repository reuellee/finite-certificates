#!/usr/bin/env python3
"""REVIEW (Fable): independent verification of the headline claim.

Checks, sharing NO code with ai/omopen, ai/omreal or ai/omgamma:
  H1  every certificate matrix realizes the chi it names: all C(9,4)=126
      determinant signs recomputed in pure Python by explicit 24-term
      permutation expansion (a 4th algorithm: producer uses Laplace-2x2,
      fpcheck uses Bareiss, checkcert uses cofactor expansion).
  H2  the 126 certificate chis are distinct and equal, as a set, to the 126
      chis of data/open_set.txt, and rows map 1:1.
  H3  the catalog npz (ai/omgamma/data/coverage_4_9/coverage_4_9.npz) is
      parsed with a hand-written stdlib npy reader; the raw array bytes are
      SHA-256'd against MANIFEST.json's array_sha256; the 126 rows' keys are
      decoded to sign strings with hand-written bit logic per the MANIFEST
      convention (bit M-1-j of the 126-bit int (hi<<64)|lo) and compared to
      the snapshot/certificate chis.
  H4  the sweep's own copy of the keys (sweep_state/hi.npy, lo.npy) agrees
      with the npz at those rows (parsed with the same stdlib reader).
  H5  st.dat (raw bytes, read with plain file I/O) says OPEN(=4) for every
      one of the 126 rows -- OPEN is terminal for the sweep, so this also
      certifies they were OPEN at snapshot time.  Also reports the sweep's
      current status counts vs. the snapshot in enumerate_final.txt.
  H6  depth column of open_set.txt vs sweep_state/depth.npy.
  H7  results.jsonl <-> certs: rows unique, chi agree, verdict REALIZABLE,
      and Appendix-B-level tallies (sources, timings, max|entry|).
"""
import ast
import hashlib
import json
import os
import struct
import sys
import zipfile
from itertools import combinations, permutations

HERE = os.path.dirname(os.path.abspath(__file__))
OMOPEN = os.path.dirname(HERE)
AI = os.path.dirname(OMOPEN)
DATA = os.path.join(OMOPEN, 'data')
COVDIR = os.path.join(AI, 'omgamma', 'data', 'coverage_4_9')
STATE = os.path.join(AI, 'omreal', 'sweep_state')
N, R, NROWS = 9, 4, 9276595

fails = []


def ck(name, ok, detail=''):
    print('  [%s] %s %s' % ('ok ' if ok else 'FAIL', name, detail))
    if not ok:
        fails.append((name, detail))


# ----- my own colex order and determinant ------------------------------
BASES = sorted(combinations(range(1, N + 1), R), key=lambda t: t[::-1])
assert len(BASES) == 126

PERMS = [(p, _s) for p in permutations(range(4))
         for _s in [(1 if sum(1 for i in range(4) for j in range(i + 1, 4)
                              if p[i] > p[j]) % 2 == 0 else -1)]]


def det4(cols):
    """cols: list of 4 columns, each 4 ints. Explicit permutation sum."""
    t = 0
    for p, s in PERMS:
        t += s * cols[0][p[0]] * cols[1][p[1]] * cols[2][p[2]] * cols[3][p[3]]
    return t


def chi_of_matrix(M):
    """M: 4x9 ints (rows). -> sign string over colex bases, or None if a
    bracket vanishes."""
    cols = [[M[i][j] for i in range(4)] for j in range(9)]
    out = []
    for B in BASES:
        d = det4([cols[b - 1] for b in B])
        if d == 0:
            return None
        out.append('+' if d > 0 else '-')
    return ''.join(out)


# ----- stdlib npy reader ----------------------------------------------
def read_npy_bytes(fh):
    """Parse a .npy stream; return (descr, shape, data_bytes)."""
    magic = fh.read(6)
    assert magic == b'\x93NUMPY', magic
    ver = fh.read(2)
    if ver[0] == 1:
        (hlen,) = struct.unpack('<H', fh.read(2))
    else:
        (hlen,) = struct.unpack('<I', fh.read(4))
    header = fh.read(hlen).decode('latin1')
    # npy headers are plain dict literals; literal_eval parses them safely
    d = ast.literal_eval(header.strip())
    assert not d['fortran_order']
    data = fh.read()
    return d['descr'], d['shape'], data


def npz_array(path, name):
    with zipfile.ZipFile(path) as z:
        with z.open(name + '.npy') as fh:
            return read_npy_bytes(fh)


def u64_list(descr, data):
    assert descr in ('<u8', '|u8', '<i8'), descr
    n = len(data) // 8
    return list(struct.unpack('<%d%s' % (n, 'Q' if 'u' in descr else 'q'),
                              data))


def npy_file(path):
    with open(path, 'rb') as fh:
        return read_npy_bytes(fh)


# ----- load the deliverable -------------------------------------------
open_rows = []
for line in open(os.path.join(DATA, 'open_set.txt')):
    p = line.split()
    if len(p) == 3:
        open_rows.append((int(p[0]), int(p[1]), p[2]))
ck('open_set.txt has 126 rows', len(open_rows) == 126, str(len(open_rows)))

certs = [json.loads(l) for l in open(os.path.join(DATA,
                                                  'certs_realizable.jsonl'))]
ck('126 realization certificates', len(certs) == 126, str(len(certs)))

results = [json.loads(l) for l in open(os.path.join(DATA, 'results.jsonl'))]
final = {}
for r in results:
    final[r['row']] = r          # later lines win (resume semantics)

# ----- H1: recompute every chirotope ----------------------------------
bad = 0
maxent = []
for c in certs:
    M = c['matrix']
    ok = (len(M) == 4 and all(len(r) == 9 for r in M))
    s = chi_of_matrix(M) if ok else None
    if s != c['chi']:
        bad += 1
        print('    H1 MISMATCH for chi %s...' % c['chi'][:20])
    maxent.append(max(abs(int(v)) for row in M for v in row))
ck('H1: all 126 matrices realize their stated chi (my determinants)',
   bad == 0, '%d mismatches' % bad)
ck('H1b: largest |entry| = 262144, and 8 certs exceed 16384',
   max(maxent) == 262144 and sum(1 for v in maxent if v > 16384) == 8,
   'max=%d, >16384: %d' % (max(maxent), sum(1 for v in maxent if v > 16384)))

# ----- H2: certs <-> open set -----------------------------------------
cert_chis = [c['chi'] for c in certs]
snap_chis = [t[2] for t in open_rows]
ck('H2: certificate chis all distinct', len(set(cert_chis)) == 126)
ck('H2b: cert chi set == snapshot chi set',
   set(cert_chis) == set(snap_chis))
chi2row = {t[2]: t[0] for t in open_rows}

# results.jsonl agreement
ok = all(final[chi2row[c]]['chi'] == c and
         final[chi2row[c]]['verdict'] == 'REALIZABLE'
         for c in cert_chis)
ck('H2c: results.jsonl row<->chi<->REALIZABLE agree for all 126', ok)

# ----- H3: catalog npz, hashed and decoded by me ----------------------
man = json.load(open(os.path.join(COVDIR, 'MANIFEST.json')))
want = man['array_sha256']
arrays = {}
for name in ('key_hi', 'key_lo', 'stab'):
    descr, shape, data = npz_array(os.path.join(COVDIR, 'coverage_4_9.npz'),
                                   name)
    got = hashlib.sha256(data).hexdigest()
    ck('H3: sha256(%s) matches MANIFEST' % name, got == want[name],
       got[:16])
    arrays[name] = (descr, shape, data)

def key_at(name, row):
    descr, shape, data = arrays[name]
    return struct.unpack_from('<Q', data, row * 8)[0]

def chi_from_key(hi, lo):
    key = (int(hi) << 64) | int(lo)
    out = []
    for j in range(126):
        out.append('+' if (key >> (125 - j)) & 1 else '-')
    return ''.join(out)

bad = 0
for (row, dep, s) in open_rows:
    if chi_from_key(key_at('key_hi', row), key_at('key_lo', row)) != s:
        bad += 1
ck('H3b: my key decode of the npz == snapshot chi, 126/126', bad == 0,
   '%d mismatches' % bad)

# ----- H4: sweep_state copies of the keys -----------------------------
dh, sh, hb = npy_file(os.path.join(STATE, 'hi.npy'))
dl, sl, lb = npy_file(os.path.join(STATE, 'lo.npy'))
bad = 0
for (row, dep, s) in open_rows:
    h = struct.unpack_from('<Q', hb, row * 8)[0]
    l = struct.unpack_from('<Q', lb, row * 8)[0]
    if h != key_at('key_hi', row) or l != key_at('key_lo', row):
        bad += 1
ck('H4: sweep_state hi/lo == catalog npz keys at the 126 rows', bad == 0,
   '%d mismatches' % bad)

# ----- H5: st.dat says OPEN -------------------------------------------
with open(os.path.join(STATE, 'st.dat'), 'rb') as fh:
    stbytes = fh.read()
ck('H5: st.dat has %d bytes' % NROWS, len(stbytes) == NROWS,
   str(len(stbytes)))
bad = [row for (row, dep, s) in open_rows if stbytes[row] != 4]
ck('H5b: all 126 snapshot rows are status OPEN(4) in the live sweep',
   not bad, str(bad[:5]))
from collections import Counter
cnt = Counter(stbytes)
done_now = NROWS - cnt[0]
print('      current sweep: TODO %d, WALK %d, REPAIR %d, NONREAL %d, '
      'OPEN %d (done %.2f%%)'
      % (cnt[0], cnt[1], cnt[2], cnt[3], cnt[4], 100.0 * done_now / NROWS))
ck('H5c: snapshot (2,426,068 done, 126 OPEN) is <= current state',
   done_now >= 2426068 and cnt[4] >= 126,
   'done_now=%d open_now=%d' % (done_now, cnt[4]))
new_open = cnt[4] - 126
print('      OPEN rows added since the snapshot: %d' % new_open)

# ----- H6: depth ------------------------------------------------------
dd, ds, db = npy_file(os.path.join(STATE, 'depth.npy'))
# depth.npy is int16
bad = 0
depth_hist = Counter()
for (row, dep, s) in open_rows:
    d = struct.unpack_from('<h', db, row * 2)[0]
    depth_hist[d] += 1
    if d != dep:
        bad += 1
ck('H6: snapshot depth column == sweep depth.npy, 126/126', bad == 0)
ck('H6b: depth histogram is {13:1, 14:4, 15:32, 16:54, 17:35}',
   dict(depth_hist) == {13: 1, 14: 4, 15: 32, 16: 54, 17: 35},
   str(dict(sorted(depth_hist.items()))))

# ----- H7: results tallies vs OPEN_ATTACK.md s8 -----------------------
fin = [final[t[0]] for t in open_rows]
ck('H7: all 126 final verdicts REALIZABLE',
   all(r['verdict'] == 'REALIZABLE' for r in fin))
src = Counter(r['method'].split(':', 1)[1] for r in fin)
ck('H7b: sources walk 103 / store_walk 14 / store 5 / fresh 4 / control 0',
   dict(src) == {'walk': 103, 'store_walk': 14, 'store': 5, 'fresh': 4},
   str(dict(src)))
secs = sorted(r['seconds'] for r in fin)
med = 0.5 * (secs[62] + secs[63])
tot = sum(secs)
ck('H7c: median 3.4 s, max 45.3 s, total ~934 s',
   abs(med - 3.4) < 0.15 and abs(secs[-1] - 45.3) < 0.15
   and abs(tot - 934) < 3,
   'median %.2f max %.2f total %.1f' % (med, secs[-1], tot))
inf = sum(r['stages']['weaponA']['lp_infeasible'] for r in fin)
infmax = max(r['stages']['weaponA']['lp_infeasible'] for r in fin)
ck('H7d: 47,723 infeasible completion LPs, max 2,938 on one class',
   inf == 47723 and infmax == 2938, 'total %d max %d' % (inf, infmax))
still = [r for r in results if r['verdict'] == 'STILL_OPEN']
ck('H7e: 13 first-pass STILL_OPEN records, later re-decided',
   len(still) == 13 and
   all(final[r['row']]['verdict'] == 'REALIZABLE' for r in still))
tot_open = sum(r['seconds'] for r in still)
print('      time burned by the 13 first-pass failures: %.0f s '
      '(doc says ~670 s)' % tot_open)

# no-BFP witness bookkeeping
wit = [json.loads(l) for l in open(os.path.join(DATA, 'certs_no_bfp.jsonl'))]
byfam = Counter(tuple(w['families']) for w in wit)
wchis = {}
for w in wit:
    wchis.setdefault(w['chi'], set()).add(tuple(w['families']))
ck('H7f: 252 witnesses = 126 chi x {L0, L1 family sets}',
   len(wit) == 252 and byfam == Counter({('gp3',): 126,
                                         ('gp3', 'pl4', 'pl5'): 126})
   and set(wchis) == set(cert_chis)
   and all(len(v) == 2 for v in wchis.values()))

print()
if fails:
    print('HEADLINE VERIFICATION: %d FAILURES' % len(fails))
    for f in fails:
        print('   ', f)
    sys.exit(1)
print('HEADLINE VERIFICATION: ALL CHECKS PASSED')
