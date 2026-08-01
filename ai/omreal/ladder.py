#!/usr/bin/env python3
"""Residue-vs-effort measurement for the (4,9) realizability sweep.

The decision this exists to make: does the residue rate keep falling as we
spend more, or has it PLATEAUED?  A point estimate cannot answer that; a
curve can.

    python ladder.py sample  --n 60000 --seed 11 --out keys.npz
    python ladder.py harvest --keys keys.npz --shard I K --out harvest_I.jsonl
    python ladder.py ladder  --harvest "harvest_*.jsonl" --shard I K \
                             --out ladder_I.jsonl --certs certs_I.jsonl
    python ladder.py curve   --ladder "ladder_*.jsonl" --swept 60000
    python ladder.py profile --ladder "ladder_*.jsonl" --keys keys.npz

HARVEST is stages A+B only -- the cheap realizer and the biquadratic final
polynomial.  It settles ~90% of classes at ~0.12 s each, so it is by far
the cheapest way to accumulate a large set of genuinely hard classes.  (The
brief said A-C; C is folded into the ladder instead, which is strictly more
informative: we get C's conversion rate and cost as curve points rather
than baking them into the harvest.)

LADDER runs a fixed sequence of increasing-effort levels on each harvested
residue class, stopping at the first that succeeds, and records which level
that was and what each level cost.  Because the levels are ordered by cost
and each only sees what the previous ones failed on, the total is a funnel:
the expensive levels run on very few classes.

Levels, and why these knobs:
  L1 C-lite   direct search, small budget
  L2 C        direct search, the pipeline's stage-C budget
  L3 E-lite   mutation warm-start, few mutants
  L4 E        mutation warm-start, enough mutants to cover all mutable
              bases of a typical class (measured: 10-26, mostly 13-19)
  L5 E-heavy  same coverage, many more samples per mutant and a stronger
              inner search -- `attempts` is the real effort knob for E once
              kmax exceeds the mutable-basis count
  L6 D        direct search, the pipeline's heavy stage-D budget
  L7 D-heavy  direct search, 2.5x stage D

Every certificate produced is written out for checkcert.py.  Nothing here
decides non-realizability: BFP already ran in the harvest, so a class that
reaches the ladder has no biquadratic final polynomial, and failing every
level means UNDECIDED, never "non-realizable".
"""

import argparse
import glob
import json
import math
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import omdecode                                            # noqa: E402
import realize as rz                                       # noqa: E402
import bfp as bfpmod                                       # noqa: E402


# ----------------------------------------------------------------------
# the effort ladder
# ----------------------------------------------------------------------

LEVELS = [
    ('L1 C-lite',  'direct', dict(tries=4,  sweeps=20,  rerolls=5,  wall_budget=6)),
    ('L2 C',       'direct', dict(tries=8,  sweeps=40,  rerolls=8,  wall_budget=12)),
    ('L3 E-lite',  'mutant', dict(kmax=5,   attempts=2,  tries=1, sweeps=15)),
    ('L4 E',       'mutant', dict(kmax=30,  attempts=3,  tries=1, sweeps=15)),
    ('L5 E-heavy', 'mutant', dict(kmax=30,  attempts=10, tries=2, sweeps=30)),
    ('L6 D',       'direct', dict(tries=60, sweeps=120, rerolls=10, wall_budget=90)),
    ('L7 D-heavy', 'direct', dict(tries=150, sweeps=200, rerolls=12, wall_budget=200)),
]


def run_level(chi, geom, kind, kw, seed):
    if kind == 'direct':
        return rz.realize(chi, geom, seed=seed, **kw)
    return rz.realize_via_mutant(chi, geom, seed=seed, **kw)


# ----------------------------------------------------------------------
# sample / harvest
# ----------------------------------------------------------------------

def cmd_sample(a):
    hi, lo, stab = omdecode.load_coverage_4_9(verify=True)
    rng = np.random.default_rng(a.seed)
    idx = np.sort(rng.choice(len(hi), size=a.n, replace=False))
    np.savez_compressed(a.out, key_hi=hi[idx], key_lo=lo[idx],
                        stab=stab[idx], row=idx.astype(np.int64))
    print('wrote %s: %d keys sampled from %d (seed %d), %.1f MB'
          % (a.out, a.n, len(hi), a.seed, os.path.getsize(a.out) / 1e6))
    print('Extracting once means the harvest workers never touch the 62 MB '
          'coverage npz -- each holds < 50 MB, so 4 of them are safe on a '
          '16 GB laptop.')


def _load_keys(path, shard=None):
    z = np.load(path)
    hi, lo, stab, row = z['key_hi'], z['key_lo'], z['stab'], z['row']
    if shard:
        i, k = shard
        hi, lo, stab, row = hi[i::k], lo[i::k], stab[i::k], row[i::k]
    return hi, lo, stab, row


def cmd_harvest(a):
    hi, lo, stab, row = _load_keys(a.keys, a.shard)
    CHI = omdecode.signs_from_keys(9, 4, hi, lo)
    ok = omdecode.gp_check(9, 4, CHI)
    if not ok.all():
        raise SystemExit('decoder sanity failed: %d invalid chirotopes'
                         % (~ok).sum())
    geom = rz.Geom(9, 4)
    gp = bfpmod.GPSystem(9, 4)
    done = set()
    if a.resume and os.path.exists(a.out):
        for line in open(a.out):
            try:
                done.add(json.loads(line)['chi'])
            except Exception:
                pass
        print('resuming: %d classes already recorded' % len(done))
    fh = open(a.out, 'a' if a.resume else 'w')
    t0 = time.time()
    n = {'R': 0, 'N': 0, '?': 0}
    for i, chi in enumerate(CHI):
        s = omdecode.string_from_signs(chi)
        if s in done:
            continue
        Z, _ = rz.realize(chi, geom, seed=int(row[i]), **HARVEST_A)
        if Z is not None:
            n['R'] += 1
            rec = {'n': 9, 'r': 4, 'chi': s, 'verdict': 'REALIZABLE',
                   'matrix': [[int(v) for v in rr] for rr in Z]}
        else:
            cert, _ = bfpmod.find_bfp(chi, gp)
            if cert is not None:
                n['N'] += 1
                terms = []
                for (ri, big, small, w) in cert['terms']:
                    L, abcd, _ = gp.rel[ri]
                    terms.append({'L': list(L), 'abcd': list(abcd),
                                  'big': int(big), 'small': int(small),
                                  'w': int(w)})
                rec = {'n': 9, 'r': 4, 'chi': s,
                       'verdict': 'NON_REALIZABLE', 'bfp': terms}
            else:
                n['?'] += 1
                rec = {'n': 9, 'r': 4, 'chi': s, 'verdict': 'RESIDUE',
                       'stab': int(stab[i]), 'row': int(row[i])}
        fh.write(json.dumps(rec) + '\n')
        if (i + 1) % 500 == 0:
            fh.flush()
            el = time.time() - t0
            print('  %6d/%d  R=%d N=%d ?=%d  %.0fs  (%.0f ms/class)'
                  % (i + 1, len(CHI), n['R'], n['N'], n['?'], el,
                     1000 * el / (i + 1)), flush=True)
    fh.close()
    print('HARVEST shard done: %d classes, R=%d N=%d RESIDUE=%d, %.0f s'
          % (len(CHI), n['R'], n['N'], n['?'], time.time() - t0), flush=True)


HARVEST_A = dict(tries=2, sweeps=15, rerolls=3, wall_budget=3)


# ----------------------------------------------------------------------
# the ladder
# ----------------------------------------------------------------------

def cmd_ladder(a):
    recs = []
    for p in sorted(glob.glob(a.harvest)):
        for line in open(p):
            r = json.loads(line)
            if r['verdict'] == 'RESIDUE':
                recs.append(r)
    seen, uniq = set(), []
    for r in recs:
        if r['chi'] not in seen:
            seen.add(r['chi'])
            uniq.append(r)
    recs = uniq
    if a.shard:
        i, k = a.shard
        recs = recs[i::k]
    if a.limit:
        recs = recs[:a.limit]
    geom = rz.Geom(9, 4)
    done = set()
    if a.resume and os.path.exists(a.out):
        for line in open(a.out):
            try:
                done.add(json.loads(line)['chi'])
            except Exception:
                pass
        print('resuming: %d already laddered' % len(done))
    fh = open(a.out, 'a' if a.resume else 'w')
    cf = open(a.certs, 'a' if a.resume else 'w')
    t0 = time.time()
    solved = 0
    for i, r in enumerate(recs):
        if r['chi'] in done:
            continue
        chi = omdecode.signs_from_string(r['chi'])
        times, at = {}, None
        for li, (name, kind, kw) in enumerate(LEVELS):
            if a.maxlevel and li >= a.maxlevel:
                break
            t1 = time.perf_counter()
            Z, info = run_level(chi, geom, kind, kw, seed=1_000_000 + int(r.get('row', i)))
            dt = time.perf_counter() - t1
            times[name] = round(dt, 3)
            if Z is not None:
                s = rz.exact_bracket_signs(Z, geom)
                if s is None or not np.array_equal(s, chi):
                    raise SystemExit('level %s returned a matrix that does '
                                     'not realize the class' % name)
                at = name
                cf.write(json.dumps({'n': 9, 'r': 4, 'chi': r['chi'],
                                     'verdict': 'REALIZABLE',
                                     'matrix': [[int(v) for v in rr] for rr in Z]}) + '\n')
                solved += 1
                break
        out = {'chi': r['chi'], 'solved_at': at, 'times': times,
               'stab': r.get('stab'), 'row': r.get('row')}
        if at is None:
            out['best_wrong'] = int(info.get('best_wrong', -1)) if info else -1
        fh.write(json.dumps(out) + '\n')
        fh.flush()
        cf.flush()
        if (i + 1) % 25 == 0:
            print('  %5d/%d  solved %d  (%.0f s elapsed)'
                  % (i + 1, len(recs), solved, time.time() - t0), flush=True)
    fh.close()
    cf.close()
    print('LADDER shard done: %d classes, %d solved, %d survive, %.0f s'
          % (len(recs), solved, len(recs) - solved, time.time() - t0), flush=True)


# ----------------------------------------------------------------------
# the curve
# ----------------------------------------------------------------------

def wilson(k, n, z=1.96):
    if n == 0:
        return (0.0, 0.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


TOTAL_49 = 9276595


def cmd_curve(a):
    rows = []
    for p in sorted(glob.glob(a.ladder)):
        for line in open(p):
            rows.append(json.loads(line))
    seen, uniq = set(), []
    for r in rows:
        if r['chi'] not in seen:
            seen.add(r['chi'])
            uniq.append(r)
    rows = uniq
    nres = len(rows)
    swept = a.swept
    harvest_rate = nres / swept
    print('swept (stages A+B)      %d classes' % swept)
    print('harvested residue       %d  (%.3f%% of swept)' % (nres, 100 * harvest_rate))
    print('')
    print('%-11s %7s %7s %9s %9s   %-22s %s'
          % ('level', 'entered', 'solved', 's/class', 'core-h/9.28M',
             'residue after, of all', '95% CI'))
    remaining = nres
    cum_cost = 0.0
    order = [nm for nm, _, _ in LEVELS]
    for name in order:
        ent = [r for r in rows if name in r['times']]
        if not ent:
            continue
        sol = [r for r in ent if r.get('solved_at') == name]
        tt = sum(r['times'][name] for r in ent)
        per = tt / len(ent)
        remaining -= len(sol)
        # cost of running this level over the whole catalogue, given that
        # only the classes that reached it pay for it
        frac_entering = len(ent) / nres * harvest_rate
        cum_cost += per * frac_entering * TOTAL_49 / 3600.0
        lo, hi = wilson(remaining, swept)
        print('%-11s %7d %7d %9.2f %9.1f   %8d   %8.4f%%   [%.4f%%, %.4f%%]'
              % (name, len(ent), len(sol), per, cum_cost,
                 round(TOTAL_49 * remaining / swept), 100 * remaining / swept,
                 100 * lo, 100 * hi))
    print('')
    lo, hi = wilson(remaining, swept)
    print('FINAL residue %d/%d = %.4f%%  95%% CI [%.4f%%, %.4f%%]'
          % (remaining, swept, 100 * remaining / swept, 100 * lo, 100 * hi))
    print('  implied over 9 276 595 classes: %d  [%d, %d]'
          % (round(TOTAL_49 * remaining / swept), round(TOTAL_49 * lo),
             round(TOTAL_49 * hi)))
    # marginal conversion, the plateau test
    print('')
    print('MARGINAL conversion per level (the plateau test):')
    for name in order:
        ent = [r for r in rows if name in r['times']]
        if not ent:
            continue
        sol = [r for r in ent if r.get('solved_at') == name]
        lo2, hi2 = wilson(len(sol), len(ent))
        print('  %-11s %4d/%-5d = %5.1f%%  95%% CI [%.1f%%, %.1f%%]'
              % (name, len(sol), len(ent), 100 * len(sol) / len(ent),
                 100 * lo2, 100 * hi2))


def cmd_profile(a):
    rows = []
    for p in sorted(glob.glob(a.ladder)):
        for line in open(p):
            rows.append(json.loads(line))
    surv = [r for r in rows if r.get('solved_at') is None]
    solv = [r for r in rows if r.get('solved_at') is not None]
    print('%d survivors, %d solved' % (len(surv), len(solv)))
    if not surv:
        return
    geom = rz.Geom(9, 4)

    def mutable(chi):
        c = 0
        for j in range(geom.M):
            t = chi.copy()
            t[j] = -t[j]
            if rz._gp_ok(t, geom):
                c += 1
        return c

    import collections
    for tag, group in (('SURVIVORS', surv), ('SOLVED (control)', solv[:len(surv)])):
        mut, st, bw = [], collections.Counter(), collections.Counter()
        for r in group:
            chi = omdecode.signs_from_string(r['chi'])
            mut.append(mutable(chi))
            st[r.get('stab')] += 1
            if 'best_wrong' in r:
                bw[r['best_wrong']] += 1
        print('\n%s (n=%d)' % (tag, len(group)))
        print('  mutable bases: min %d  median %d  mean %.1f  max %d'
              % (min(mut), int(np.median(mut)), float(np.mean(mut)), max(mut)))
        print('  |Stab| histogram: %s' % dict(sorted(st.items(), key=lambda t: -t[1])))
        if bw:
            print('  best_wrong at the end: %s' % dict(sorted(bw.items())))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('sample')
    s.add_argument('--n', type=int, required=True)
    s.add_argument('--seed', type=int, default=11)
    s.add_argument('--out', required=True)
    s.set_defaults(fn=cmd_sample)
    h = sub.add_parser('harvest')
    h.add_argument('--keys', required=True)
    h.add_argument('--shard', nargs=2, type=int)
    h.add_argument('--out', required=True)
    h.add_argument('--resume', action='store_true')
    h.set_defaults(fn=cmd_harvest)
    l = sub.add_parser('ladder')
    l.add_argument('--harvest', required=True)
    l.add_argument('--shard', nargs=2, type=int)
    l.add_argument('--out', required=True)
    l.add_argument('--certs', required=True)
    l.add_argument('--limit', type=int, default=0)
    l.add_argument('--maxlevel', type=int, default=0)
    l.add_argument('--resume', action='store_true')
    l.set_defaults(fn=cmd_ladder)
    c = sub.add_parser('curve')
    c.add_argument('--ladder', required=True)
    c.add_argument('--swept', type=int, required=True)
    c.set_defaults(fn=cmd_curve)
    p = sub.add_parser('profile')
    p.add_argument('--ladder', required=True)
    p.add_argument('--keys', default=None)
    p.set_defaults(fn=cmd_profile)
    a = ap.parse_args()
    a.fn(a)


if __name__ == '__main__':
    main()
