#!/usr/bin/env python3
"""Turn data/minors_<tag>.jsonl into the numbers MINOR_THEORY.md quotes.

    python analyze.py --tag sweep

Reports, for the prefix of the sweep actually consumed:

  * the CLOSURE FRACTION: of the certified non-realizable (4,9) classes, how
    many have at least one non-realizable single-element deletion;
  * the MINOR-MINIMAL RESIDUE: the classes with none, listed by canonical
    key (these are the generative set at n = 9);
  * which of the 24 non-realizable (4,8) classes actually occur, and how
    often;
  * whether the minor test settles any class the sweep left OPEN;
  * structure of the minimal set: |Stab|, tree depth, number of mutable
    bases, and the shape of the (4,9) deletion-class multiset.

All (4,9) metadata is read READ-ONLY from ai/omreal/sweep_state/*.npy and
ai/omgamma/data/coverage_4_9 -- the sweep may still be running.
"""

import argparse
import collections
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import minorlib as ml                                       # noqa: E402

OUT = os.path.join(HERE, 'data')
SWEEP_STATE = os.path.join(ml.OMREAL, 'sweep_state')
COV = os.path.join(ml.DATA, 'coverage_4_9')


def wilson(k, n, z=1.959963985):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def locate(chis):
    """chi strings -> row indices in the (4,9) catalog order (memmapped)."""
    S = np.array([ml.bits_from_string(c) for c in chis], dtype=np.uint8)
    qh, ql = ml.cc().encode_keys(ml.tables(9, 4), S)
    want = {(int(h), int(l)): i for i, (h, l) in enumerate(zip(qh, ql))}
    hi = np.load(os.path.join(SWEEP_STATE, 'hi.npy'), mmap_mode='r')
    lo = np.load(os.path.join(SWEEP_STATE, 'lo.npy'), mmap_mode='r')
    qhs = np.unique(qh)
    rows = np.full(len(chis), -1, dtype=np.int64)
    B = 1 << 20
    for a in range(0, len(hi), B):
        b = min(a + B, len(hi))
        ch = np.asarray(hi[a:b])
        m = np.isin(ch, qhs)
        if not m.any():
            continue
        idx = np.flatnonzero(m)
        cl = np.asarray(lo[a:b])[idx]
        for j, k in zip(idx, cl):
            t = want.get((int(ch[j]), int(k)))
            if t is not None:
                rows[t] = a + int(j)
    return rows


def mutable_counts(chis):
    C = ml.cc()
    T = ml.tables(9, 4)
    S = np.array([ml.bits_from_string(c) for c in chis], dtype=np.uint8)
    out = np.empty(len(S), dtype=np.int32)
    for a in range(0, len(S), 500):
        b = min(a + 500, len(S))
        p1, p2, p3 = C.gp_parities(T, S[a:b])
        out[a:b] = C.mutable_mask(T, p1, p2, p3).sum(axis=1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--tag', default='sweep')
    ap.add_argument('--bfp-sample', type=int, default=250)
    a = ap.parse_args()

    rows = [json.loads(l) for l in open(os.path.join(OUT, 'minors_%s.jsonl' % a.tag))]
    hstate = json.load(open(os.path.join(OUT, 'harvest_%s.state.json' % a.tag)))
    mstate = json.load(open(os.path.join(OUT, 'minors_%s.state.json' % a.tag)))

    rep = {'tag': a.tag, 'harvest': hstate, 'minors_consumed': mstate['consumed']}
    print('=' * 72)
    print('DATA PREFIX')
    print('  sweep certificate lines consumed : %d' % hstate['total_lines'])
    print('  verdicts in that prefix          : %s' % hstate['counts'])
    print('  rows put through the minor test  : %d' % len(rows))
    for ln in hstate.get('sweep_log_tail', []):
        print('  sweep log tail: %s' % ln)

    byv = collections.defaultdict(list)
    for r in rows:
        byv[r['verdict']].append(r)

    print('\n' + '=' * 72)
    print('CLOSURE FRACTION')
    res = {}
    for v in ('NON_REALIZABLE', 'RESIDUE', 'REALIZABLE'):
        sub = byv.get(v, [])
        if not sub:
            continue
        k = sum(1 for r in sub if r['del_nonreal'])
        kc = sum(1 for r in sub if r['con_nonreal'])
        lo_, hi_ = wilson(k, len(sub))
        print('  %-15s %6d rows | %6d with a non-realizable DELETION '
              '(%.3f%%, 95%% CI [%.3f%%, %.3f%%]) | %d with a non-realizable '
              'CONTRACTION' % (v, len(sub), k, 100 * k / len(sub),
                               100 * lo_, 100 * hi_, kc))
        h = collections.Counter(len(r['del_nonreal']) for r in sub)
        print('      #non-realizable deletions: %s' % dict(sorted(h.items())))
        res[v] = {'n': len(sub), 'with_nr_deletion': k,
                  'with_nr_contraction': kc, 'wilson95': [lo_, hi_],
                  'hist': dict(sorted(h.items()))}
    rep['closure'] = res

    nr = byv.get('NON_REALIZABLE', [])
    minimal = [r for r in nr if not r['del_nonreal'] and not r['con_nonreal']]
    print('\n' + '=' * 72)
    print('MINOR-MINIMAL RESIDUE at n = 9 (all 9 deletions AND all 9 '
          'contractions realizable)')
    print('  %d of %d certified non-realizable classes' % (len(minimal), len(nr)))
    mp = os.path.join(OUT, 'minimal_%s.txt' % a.tag)
    with open(mp, 'w') as fh:
        for r in sorted(minimal, key=lambda r: r['chi']):
            fh.write(r['chi'] + '\n')
    print('  listed by canonical key -> %s' % mp)
    rep['minimal_count'] = len(minimal)

    # which (4,8) non-realizable classes occur, and how often
    lines8 = [l.strip() for l in open(os.path.join(OUT, 'cat48_lines.txt')) if l.strip()]
    occ = collections.Counter()
    for r in nr:
        for e in r['del_nonreal']:
            occ[r['del_cls'][e - 1]] += 1
    z = np.load(os.path.join(OUT, 'cat48_keys.npz'))
    nr48 = sorted(int(x) for x in z['nonreal'])
    print('\n' + '=' * 72)
    print('WHICH OF THE 24 NON-REALIZABLE (4,8) CLASSES OCCUR AS DELETIONS')
    for c in nr48:
        print('  cat_4_8 row %4d : %6d occurrences' % (c, occ.get(c, 0)))
    print('  distinct (4,8) witnesses used: %d of 24' % sum(1 for c in nr48 if occ.get(c)))
    rep['witness_occurrences'] = {str(c): occ.get(c, 0) for c in nr48}

    # residue / OPEN rows settled by the minor test
    resid = byv.get('RESIDUE', [])
    settled = [r for r in resid if r['del_nonreal'] or r['con_nonreal']]
    print('\n' + '=' * 72)
    print('SWEEP RESIDUE (OPEN) ROWS')
    print('  %d OPEN rows in the prefix; %d SETTLED non-realizable by the '
          'minor test' % (len(resid), len(settled)))
    if settled:
        sp = os.path.join(OUT, 'settled_by_minor_%s.txt' % a.tag)
        with open(sp, 'w') as fh:
            for r in settled:
                fh.write('%s  del_nonreal=%s\n' % (r['chi'], r['del_nonreal']))
        print('  -> %s' % sp)
    rep['open_rows'] = len(resid)
    rep['open_settled_by_minor'] = len(settled)

    # ---------------- closure fraction against tree depth ----------------
    print('\n' + '=' * 72)
    print('CLOSURE FRACTION BY TREE DEPTH (is the prefix biased?)')
    depth_all = np.load(os.path.join(SWEEP_STATE, 'depth.npy'), mmap_mode='r')
    idx_nr = locate([r['chi'] for r in nr])
    rep['depth_bands'] = {}
    if (idx_nr < 0).any():
        print('  WARNING: %d rows not located' % int((idx_nr < 0).sum()))
    d_nr = np.asarray(depth_all[idx_nr[idx_nr >= 0]])
    has = np.array([bool(r['del_nonreal']) for r in nr])[idx_nr >= 0]
    for d in sorted(set(int(x) for x in d_nr)):
        m = d_nr == d
        k = int(has[m].sum())
        n_ = int(m.sum())
        lo_, hi_ = wilson(k, n_)
        print('  depth %2d : %6d non-realizable, %6d with a witness (%.2f%%, '
              'CI [%.2f%%, %.2f%%])' % (d, n_, k, 100 * k / n_, 100 * lo_, 100 * hi_))
        rep['depth_bands'][str(d)] = {'n': n_, 'with_witness': k}

    # ---------------- structure of the minimal set ----------------
    print('\n' + '=' * 72)
    print('STRUCTURE')
    import random
    rng = random.Random(20260801)
    nonmin = [r for r in nr if r['del_nonreal']]
    comp = rng.sample(nonmin, min(len(minimal), len(nonmin)))

    groups = [('minor-minimal', minimal), ('has a witness', comp)]
    stab = None
    try:
        zz = np.load(os.path.join(COV, 'coverage_4_9.npz'))
        stab = zz['stab']
    except Exception as exc:                                    # pragma: no cover
        print('  (stab unavailable: %s)' % exc)
    depth = np.load(os.path.join(SWEEP_STATE, 'depth.npy'), mmap_mode='r')

    rep['structure'] = {}
    for name, grp in groups:
        if not grp:
            continue
        chis = [r['chi'] for r in grp]
        idx = locate(chis)
        if (idx < 0).any():
            print('  WARNING: %d of %d rows not located in the catalog'
                  % (int((idx < 0).sum()), len(idx)))
        ok = idx >= 0
        d = np.asarray(depth[idx[ok]])
        mb = mutable_counts(chis)
        st = np.asarray(stab[idx[ok]]) if stab is not None else None
        # distinct (4,8) deletion classes per row
        dd = [len(set(r['del_cls'])) for r in grp]
        info = {
            'n': len(grp),
            'depth': {'mean': float(d.mean()), 'min': int(d.min()),
                      'max': int(d.max())},
            'mutable_bases': {'mean': float(mb.mean()), 'min': int(mb.min()),
                              'max': int(mb.max())},
            'distinct_deletion_classes': dict(sorted(collections.Counter(dd).items())),
        }
        if st is not None:
            info['stab'] = dict(sorted(collections.Counter(int(x) for x in st).items()))
        print('  %-14s n=%d  depth %.1f [%d,%d]  mutable bases %.1f [%d,%d]'
              % (name, len(grp), info['depth']['mean'], info['depth']['min'],
                 info['depth']['max'], info['mutable_bases']['mean'],
                 info['mutable_bases']['min'], info['mutable_bases']['max']))
        if st is not None:
            print('      |Stab| histogram: %s' % info['stab'])
        print('      distinct (4,8) deletion classes per row: %s'
              % info['distinct_deletion_classes'])
        rep['structure'][name] = info

    # ---------------- BFP certificate shape ----------------
    if a.bfp_sample:
        sys.path.insert(0, ml.OMREAL)
        import bfp as bfpmod
        gp = bfpmod.GPSystem(9, 4)
        print('\n  BFP certificate shape (support = #terms, weight = total):')
        rep['bfp'] = {}
        for name, grp in groups:
            sel = grp if len(grp) <= a.bfp_sample else rng.sample(grp, a.bfp_sample)
            sup, wt = [], []
            for r in sel:
                chi = ml.signs_from_string(r['chi'])
                cert, info = bfpmod.find_bfp(chi, gp)
                if cert is None:
                    sup.append(-1)
                    continue
                sup.append(len(cert['terms']))
                wt.append(sum(t[3] for t in cert['terms']))
            good = [s for s in sup if s > 0]
            print('    %-14s n=%d  found %d  support mean %.1f median %d '
                  'range [%d,%d]  weight mean %.1f'
                  % (name, len(sel), len(good),
                     float(np.mean(good)) if good else 0,
                     int(np.median(good)) if good else 0,
                     min(good) if good else 0, max(good) if good else 0,
                     float(np.mean(wt)) if wt else 0))
            rep['bfp'][name] = {
                'n': len(sel), 'found': len(good),
                'support_mean': float(np.mean(good)) if good else None,
                'support_median': int(np.median(good)) if good else None,
                'support_min': min(good) if good else None,
                'support_max': max(good) if good else None,
                'weight_mean': float(np.mean(wt)) if wt else None,
                'support_hist': dict(sorted(collections.Counter(good).items())),
            }

    json.dump(rep, open(os.path.join(OUT, 'report_%s.json' % a.tag), 'w'), indent=1)
    print('\nwrote %s' % os.path.join(OUT, 'report_%s.json' % a.tag))


if __name__ == '__main__':
    main()
