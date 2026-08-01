#!/usr/bin/env python3
"""Pilot driver: decide realizability class by class and emit certificates.

    python pilot.py --cat 3 8  --out certs_3_8.jsonl
    python pilot.py --cat 4 8  --out certs_4_8.jsonl
    python pilot.py --sample49 3000 --seed 1 --out certs_4_9_sample.jsonl
    python pilot.py --sample49 2000 --stab-only --out certs_4_9_stab.jsonl

Per class:
    1. REALIZE   heuristic search, then exact integer verification.
    2. BFP       (only if 1 failed) biquadratic final polynomial / Gordan.
    3. RESIDUE   neither.

Every settled class is written as a self-contained record that
`checkcert.py` re-verifies without any of this code.
"""

import argparse
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import omdecode                                            # noqa: E402
import realize as rz                                       # noqa: E402
import bfp as bfpmod                                       # noqa: E402


def record_realizable(n, r, chi, Z):
    return {'n': n, 'r': r, 'chi': omdecode.string_from_signs(chi),
            'verdict': 'REALIZABLE',
            'matrix': [[int(v) for v in row] for row in Z]}


def record_nonrealizable(n, r, chi, cert, gp):
    terms = []
    for (ri, big, small, w) in cert['terms']:
        L, abcd, _ = gp.rel[ri]
        terms.append({'L': list(L), 'abcd': list(abcd),
                      'big': int(big), 'small': int(small), 'w': int(w)})
    return {'n': n, 'r': r, 'chi': omdecode.string_from_signs(chi),
            'verdict': 'NON_REALIZABLE', 'bfp': terms}


def record_residue(n, r, chi):
    return {'n': n, 'r': r, 'chi': omdecode.string_from_signs(chi),
            'verdict': 'RESIDUE'}


STAGE_A = dict(tries=2, sweeps=15, rerolls=3, wall_budget=3)
STAGE_C = dict(tries=8, sweeps=40, rerolls=8, wall_budget=12)
STAGE_D = dict(tries=60, sweeps=120, rerolls=10, wall_budget=90)
STAGE_E = dict(kmax=20, attempts=3)   # mutation warm-start


def run(CHI, n, r, out, cross=0, quiet=False, progress=250,
        stage_a=None, stage_c=None, stage_d=None, no_stage_c=False,
        no_stage_d=False, stage_e=None, no_stage_e=False):
    """Three-stage cascade, cheapest first:

        A  cheap realization search          -> REALIZABLE
        B  biquadratic final polynomial      -> NON_REALIZABLE
        C  medium realization search         -> REALIZABLE
        D  heavy realization search          -> REALIZABLE
        E  mutation warm-start               -> REALIZABLE
        -  otherwise                         -> RESIDUE

    A and C are the same algorithm at different budgets; B is exact-ish and
    cheap, so it is worth interposing before paying for C.  Timings are kept
    per stage and per outcome, which is what the extrapolation needs.
    """
    sa = dict(STAGE_A, **(stage_a or {}))
    sc = dict(STAGE_C, **(stage_c or {}))
    sd = dict(STAGE_D, **(stage_d or {}))
    se = dict(STAGE_E, **(stage_e or {}))
    geom = rz.Geom(n, r)
    gp = bfpmod.GPSystem(n, r)
    S = {'n': n, 'r': r, 'total': len(CHI), 'REALIZABLE': 0,
         'NON_REALIZABLE': 0, 'RESIDUE': 0,
         'by_stage': {'A': 0, 'C': 0, 'D': 0, 'E': 0},
         't_A_hit': 0.0, 't_A_miss': 0.0, 't_B_hit': 0.0, 't_B_miss': 0.0,
         't_C_hit': 0.0, 't_C_miss': 0.0, 't_D_hit': 0.0, 't_D_miss': 0.0, 't_E_hit': 0.0, 't_E_miss': 0.0,
         'n_A_hit': 0, 'n_A_miss': 0, 'n_B_hit': 0, 'n_B_miss': 0,
         'n_C_hit': 0, 'n_C_miss': 0, 'n_D_hit': 0, 'n_D_miss': 0, 'n_E_hit': 0, 'n_E_miss': 0,
         'bfp_support': [], 'denoms': {}, 'stage_a': sa, 'stage_c': sc,
         'stage_d': sd, 'stage_e': se, 'dur_C': [], 'dur_D': [], 'dur_E': [],
         'cross_checked': 0, 'cross_bfp_on_realizable': 0,
         'cross_realize_on_nonrealizable': 0, 'residue_chi': []}
    fh = open(out, 'w') if out else None
    t0 = time.time()
    for i, chi in enumerate(CHI):
        chi = np.asarray(chi, dtype=np.int8)
        ta = time.perf_counter()
        Z, info = rz.realize(chi, geom, seed=i, **sa)
        dt = time.perf_counter() - ta
        if Z is not None:
            S['t_A_hit'] += dt
            S['n_A_hit'] += 1
            S['by_stage']['A'] += 1
        else:
            S['t_A_miss'] += dt
            S['n_A_miss'] += 1
            tb = time.perf_counter()
            cert, _ = bfpmod.find_bfp(chi, gp)
            db = time.perf_counter() - tb
            if cert is not None:
                S['t_B_hit'] += db
                S['n_B_hit'] += 1
                S['NON_REALIZABLE'] += 1
                S['bfp_support'].append(len(cert['terms']))
                rec = record_nonrealizable(n, r, chi, cert, gp)
                if cross and S['cross_checked'] < cross:
                    Z2, _ = rz.realize(chi, geom, seed=7 + i, **sc)
                    if Z2 is not None:
                        S['cross_realize_on_nonrealizable'] += 1
                if fh:
                    fh.write(json.dumps(rec) + '\n')
                continue
            S['t_B_miss'] += db
            S['n_B_miss'] += 1
            if not no_stage_c:
                tc = time.perf_counter()
                Z, info = rz.realize(chi, geom, seed=1000003 + i, **sc)
                dc = time.perf_counter() - tc
                S['dur_C'].append(round(dc, 3))
                if Z is not None:
                    S['t_C_hit'] += dc
                    S['n_C_hit'] += 1
                    S['by_stage']['C'] += 1
                else:
                    S['t_C_miss'] += dc
                    S['n_C_miss'] += 1
                    if not no_stage_d:
                        td = time.perf_counter()
                        Z, info = rz.realize(chi, geom, seed=31337 + i, **sd)
                        dd = time.perf_counter() - td
                        S['dur_D'].append(round(dd, 3))
                        if Z is not None:
                            S['t_D_hit'] += dd
                            S['n_D_hit'] += 1
                            S['by_stage']['D'] += 1
                        else:
                            S['t_D_miss'] += dd
                            S['n_D_miss'] += 1
                            if not no_stage_e:
                                te = time.perf_counter()
                                Z, info = rz.realize_via_mutant(
                                    chi, geom, seed=90001 + i, **se)
                                de = time.perf_counter() - te
                                S['dur_E'].append(round(de, 3))
                                if Z is not None:
                                    S['t_E_hit'] += de
                                    S['n_E_hit'] += 1
                                    S['by_stage']['E'] += 1
                                else:
                                    S['t_E_miss'] += de
                                    S['n_E_miss'] += 1
        if Z is not None:
            S['REALIZABLE'] += 1
            S['denoms'][info['denom']] = S['denoms'].get(info['denom'], 0) + 1
            rec = record_realizable(n, r, chi, Z)
            if cross and S['cross_checked'] < cross:
                S['cross_checked'] += 1
                c2, _ = bfpmod.find_bfp(chi, gp)
                if c2 is not None:
                    S['cross_bfp_on_realizable'] += 1
        else:
            S['RESIDUE'] += 1
            if len(S['residue_chi']) < 500:
                S['residue_chi'].append(omdecode.string_from_signs(chi))
            rec = record_residue(n, r, chi)
        if fh:
            fh.write(json.dumps(rec) + '\n')
        if not quiet and progress and (i + 1) % progress == 0:
            el = time.time() - t0
            print('  %7d/%d  R=%d N=%d ?=%d  %.1fs  (%.0f ms/class)'
                  % (i + 1, len(CHI), S['REALIZABLE'], S['NON_REALIZABLE'],
                     S['RESIDUE'], el, 1000 * el / (i + 1)), flush=True)
    if fh:
        fh.close()
    S['wall'] = time.time() - t0
    return S


def summarise(S):
    R, N, Q = S['REALIZABLE'], S['NON_REALIZABLE'], S['RESIDUE']
    tot = S['total']
    print('')
    print('  classes            %d' % tot)
    print('  REALIZABLE         %-9d (%.3f%%)   [stage A %d, stage C %d]'
          % (R, 100.0 * R / tot, S['by_stage']['A'],
             S['by_stage']['C'] + S['by_stage']['D'] + S['by_stage']['E']))
    print('  NON_REALIZABLE     %-9d (%.3f%%)' % (N, 100.0 * N / tot))
    print('  RESIDUE            %-9d (%.3f%%)' % (Q, 100.0 * Q / tot))
    print('  wall               %.1f s   (%.0f ms/class)'
          % (S['wall'], 1000 * S['wall'] / max(tot, 1)))
    print('  stage timings (ms per class ENTERING that stage):')
    for st, hit, miss in (('A realize cheap', 'A_hit', 'A_miss'),
                          ('B bfp', 'B_hit', 'B_miss'),
                          ('C realize medium', 'C_hit', 'C_miss'),
                          ('D realize heavy', 'D_hit', 'D_miss'),
                          ('E mutant warm', 'E_hit', 'E_miss')):
        nh, nm = S['n_' + hit], S['n_' + miss]
        th, tm = S['t_' + hit], S['t_' + miss]
        print('    %-16s hit %6d @ %8.1f ms   miss %6d @ %8.1f ms'
              % (st, nh, 1000 * th / max(nh, 1), nm, 1000 * tm / max(nm, 1)))
    for tag in ('C', 'D', 'E'):
        d = sorted(S.get('dur_' + tag) or [])
        if d:
            q = lambda f: d[min(len(d) - 1, int(f * len(d)))]
            print('  stage %s seconds   n=%d  median %.2f  p90 %.2f  p99 %.2f'
                  '  MAX %.2f  total %.0f s'
                  % (tag, len(d), q(.5), q(.9), q(.99), d[-1], sum(d)))
    if S['bfp_support']:
        s = S['bfp_support']
        print('  bfp terms          min %d  median %d  max %d'
              % (min(s), int(np.median(s)), max(s)))
    if S['denoms']:
        print('  rounding denominators %s'
              % sorted((k, v) for k, v in S['denoms'].items()))
    if S['cross_checked']:
        print('  CANARY  %d realizable classes fed to BFP -> %d spurious '
              'non-realizability certificates (must be 0)'
              % (S['cross_checked'], S['cross_bfp_on_realizable']))
    if S['n_B_hit'] and S['cross_realize_on_nonrealizable'] is not None:
        print('  CANARY  BFP-certified classes fed to the hard realizer -> '
              '%d realized (must be 0)'
              % S['cross_realize_on_nonrealizable'])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cat', nargs=2, type=int, metavar=('R', 'N'))
    ap.add_argument('--sample49', type=int)
    ap.add_argument('--stab-only', action='store_true',
                    help='sample only from classes with |Stab| > 2')
    ap.add_argument('--seed', type=int, default=0)
    ap.add_argument('--out', default=None)
    ap.add_argument('--no-stage-c', action='store_true')
    ap.add_argument('--no-stage-d', action='store_true')
    ap.add_argument('--no-stage-e', action='store_true')
    ap.add_argument('--cross', type=int, default=0)
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--shard', nargs=2, type=int, metavar=('I', 'K'),
                    help='process only classes with index %% K == I')
    ap.add_argument('--catdir', default=None,
                    help='directory holding cat_<r>_<n>.txt (default: omgamma data)')
    ap.add_argument('--stats-out', default=None)
    a = ap.parse_args()

    if a.cat:
        r, n = a.cat
        if a.catdir:
            path = os.path.join(a.catdir, 'cat_%d_%d.txt' % (r, n))
            lines = [ln.strip() for ln in open(path) if ln.strip()]
            CHI = np.array([omdecode.signs_from_string(ln) for ln in lines],
                           dtype=np.int8)
        else:
            CHI = omdecode.load_catalog_txt(n, r)
        label = 'catalog (%d,%d)' % (r, n)
    elif a.sample49:
        n, r = 9, 4
        hi, lo, stab = omdecode.load_coverage_4_9(verify=True)
        pool = np.flatnonzero(stab > 2) if a.stab_only else None
        rng = np.random.default_rng(a.seed)
        if pool is not None:
            k = min(a.sample49, len(pool))
            idx = rng.choice(pool, size=k, replace=False)
            label = '(4,9) sample of %d from the %d classes with |Stab|>2' % (k, len(pool))
        else:
            idx = rng.choice(len(hi), size=a.sample49, replace=False)
            label = '(4,9) uniform sample of %d from %d' % (a.sample49, len(hi))
        idx = np.sort(idx)
        CHI = omdecode.signs_from_keys(n, r, hi[idx], lo[idx])
        ok = omdecode.gp_check(n, r, CHI)
        if not ok.all():
            raise SystemExit('decoder sanity check failed: %d of %d decoded '
                             'keys are not valid chirotopes'
                             % ((~ok).sum(), len(CHI)))
        print('decoder sanity: all %d sampled keys are valid uniform '
              'chirotopes' % len(CHI))
    else:
        raise SystemExit('need --cat or --sample49')

    if a.shard:
        i, k = a.shard
        CHI = CHI[i::k]
        label += ' [shard %d/%d]' % (i, k)
    if a.limit:
        CHI = CHI[:a.limit]
    print('=== %s : %d classes ===' % (label, len(CHI)), flush=True)
    st = run(CHI, n, r, a.out, cross=a.cross, no_stage_c=a.no_stage_c,
             no_stage_d=a.no_stage_d, no_stage_e=a.no_stage_e)
    st['label'] = label
    summarise(st)
    if a.stats_out:
        json.dump(st, open(a.stats_out, 'w'), indent=1, default=str)


if __name__ == '__main__':
    main()
