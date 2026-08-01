#!/usr/bin/env python3
"""Attack 2 (+ pieces of 4, 7, 8): recount every headline number from the
data files themselves, with my own Wilson-CI implementation, and check the
prefix/subset/consistency properties the doc asserts."""
import json
import math
from collections import Counter

import numpy as np

D = '../data/'
R = '../../omreal/'
G = '../../omgamma/data/'


def wilson(k, n, z=1.959963985):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return 100 * (c - h), 100 * (c + h)


# my own list of which catalog rows are the 24, built from certs + catalog
cat48 = [l.strip() for l in open(G + 'cat_4_8.txt') if l.strip()]
verd = {}
for line in open(R + 'certs_4_8.jsonl'):
    rec = json.loads(line)
    verd[rec['chi']] = rec['verdict']
my_nr48 = set(i for i, s in enumerate(cat48) if verd[s] == 'NON_REALIZABLE')
print('my 24-row index set size:', len(my_nr48))
z = np.load(D + 'cat48_keys.npz')
npz_nr = set(int(x) for x in z['nonreal'])
print('cat48_keys.npz nonreal == my set:', npz_nr == my_nr48)
lines_txt = [l.strip() for l in open(D + 'cat48_lines.txt') if l.strip()]
print('cat48_lines.txt == omgamma cat_4_8.txt:', lines_txt == cat48)


def scan(tag):
    rows = [json.loads(l) for l in open(D + 'minors_%s.jsonl' % tag)]
    out = {}
    for v in ('NON_REALIZABLE', 'RESIDUE', 'REALIZABLE'):
        sub = [r for r in rows if r['verdict'] == v]
        k = sum(1 for r in sub if r['del_nonreal'])
        kc = sum(1 for r in sub if r['con_nonreal'])
        out[v] = (len(sub), k, kc)
    nr = [r for r in rows if r['verdict'] == 'NON_REALIZABLE']
    hist = Counter(len(r['del_nonreal']) for r in nr)
    minimal = sorted(r['chi'] for r in nr if not r['del_nonreal'] and not r['con_nonreal'])
    # per-element consistency: del_nonreal must equal positions with del_cls in the 24
    incons = 0
    for r in rows:
        want = [e + 1 for e in range(9) if r['del_cls'][e] in my_nr48]
        if want != r['del_nonreal']:
            incons += 1
    occ = Counter()
    for r in nr:
        for e in r['del_nonreal']:
            occ[r['del_cls'][e - 1]] += 1
    return rows, out, hist, minimal, incons, occ


for tag, exp in (('sweep', (14396, 13117, 1279, 60, 715)),
                 ('ext', (18944, 17186, 1758, 84, None)),
                 ('uniform', (116, 105, 11, 391, 4893))):
    rows, out, hist, minimal, incons, occ = scan(tag)
    nrn, nrk, nrkc = out['NON_REALIZABLE']
    resn, resk, _ = out['RESIDUE']
    ren, rek, rekc = out['REALIZABLE']
    lo, hi = wilson(nrk, nrn)
    print('\n[%s] rows=%d  NR=%d withdel=%d (%.2f%% CI [%.2f, %.2f])  '
          'NRcontr=%d  RES=%d withdel=%d  REAL=%d withdel=%d'
          % (tag, len(rows), nrn, nrk, 100 * nrk / nrn, lo, hi, nrkc,
             resn, resk, ren, rek))
    print('   hist:', dict(sorted(hist.items())),
          ' minimal:', len(minimal), ' per-elem inconsistencies:', incons)
    listed = sorted(l.strip() for l in open(D + 'minimal_%s.txt' % tag) if l.strip())
    print('   minimal recomputed == minimal_%s.txt: %s' % (tag, minimal == listed))
    if tag == 'sweep':
        top = occ.most_common(4)
        print('   witness occ total=%d top4=%s sum(top4)=%d used=%d  row2597=%d'
              % (sum(occ.values()), top, sum(v for _, v in top), len(occ),
                 occ.get(2597, 0)))
        # distinct deletion multisets + union of (4,8) classes over minimal rows
        nrrows = [r for r in rows if r['verdict'] == 'NON_REALIZABLE']
        mins = [r for r in nrrows if not r['del_nonreal']]
        msets = set(tuple(sorted(r['del_cls'])) for r in mins)
        union = set()
        for r in mins:
            union.update(r['del_cls'])
        print('   minimal: distinct del-class multisets=%d (of %d), distinct (4,8) classes used=%d'
              % (len(msets), len(mins), len(union)))

# subset/prefix properties
ms = [l.strip() for l in open(D + 'minimal_sweep.txt') if l.strip()]
me = set(l.strip() for l in open(D + 'minimal_ext.txt') if l.strip())
print('\nminimal_sweep subset of minimal_ext:', set(ms) <= me, '(%d of %d)' % (len(ms), len(me)))

a = open(D + 'minors_sweep.jsonl', 'rb').read()
b = open(D + 'minors_ext.jsonl', 'rb').read()
print('minors_sweep is byte-prefix of minors_ext:', b.startswith(a))
a = open(D + 'harvest_sweep.jsonl', 'rb').read()
b = open(D + 'harvest_ext.jsonl', 'rb').read()
print('harvest_sweep is byte-prefix of harvest_ext:', b.startswith(a))

# harvest chi distinctness + verdict agreement with minors files
hs = [json.loads(l) for l in open(D + 'harvest_sweep.jsonl')]
print('harvest_sweep rows=%d distinct chi=%d' % (len(hs), len(set(r['chi'] for r in hs))))
mv = {}
for l in open(D + 'minors_sweep.jsonl'):
    r = json.loads(l)
    mv[r['chi']] = r['verdict']
dis = sum(1 for r in hs if mv.get(r['chi']) != r['verdict'])
print('harvest vs minors verdict disagreements:', dis)
hu = [json.loads(l) for l in open(D + 'harvest_uniform.jsonl')]
print('harvest_uniform rows=%d distinct chi=%d' % (len(hu), len(set(r['chi'] for r in hu))))
first2000 = Counter(r['verdict'] for r in hu[:2000])
print('fastminor workload-1 corpus (first 2000 of uniform):', dict(first2000))

# certs_minimal_* really certify the minimal lists
for tag in ('sweep', 'ext'):
    cm = [json.loads(l) for l in open(D + 'certs_minimal_%s.jsonl' % tag)]
    chis = set(r['chi'] for r in cm)
    listed = set(l.strip() for l in open(D + 'minimal_%s.txt' % tag) if l.strip())
    print('certs_minimal_%s: %d records, chis==list: %s, all NON_REALIZABLE: %s'
          % (tag, len(cm), chis == listed,
             all(r['verdict'] == 'NON_REALIZABLE' for r in cm)))
