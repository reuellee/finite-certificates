#!/usr/bin/env python3
"""Decide the sweep's OPEN classes.  Resumable; safe to re-run.

    python attack.py enumerate                  # snapshot the OPEN set
    python attack.py run  [--budget 60] [--limit N] [--fp] [--rows a,b,c]
    python attack.py report
    python attack.py validate [--n 40]          # the gates, on known classes
    python attack.py canaries                   # sabotage certificates

WHAT IT DOES, PER CLASS
=======================
    stage 0   Gordan vector over the three-term relations (level L0).  This
              is exactly what the sweep already tried; it is repeated
              because this file's implementation is independent of
              `ai/omreal/bfp.py` and a disagreement would matter.
    stage 1   WEAPON A: one-point completion over the nine deletions
              (`weaponA.py`), within a per-class time budget.
    stage 2   Gordan over the wider level L1 support, and -- whether or not
              that fires -- the EXACT rational witness u certifying that no
              Gordan certificate exists at L0 (no biquadratic final
              polynomial) and at L1.
    stage 3   WEAPON B2: general final polynomials of degree 2 and 3
              (`fpoly.py`), if --fp is given.

A class is written out with exactly one of

    REALIZABLE      an integer 4x9 matrix, in ai/omreal's schema, so that
                    `ai/omreal/checkcert.py` accepts it unchanged;
    NON_REALIZABLE  a Gordan or final-polynomial certificate, plus -- when
                    the class has no biquadratic final polynomial -- the
                    exact no-BFP witness, because THAT combination is a
                    counterexample to the sharpened conjecture of
                    ai/omminor/MINOR_THEORY.md s4.3 and must be flagged;
    STILL_OPEN      the exact no-BFP witness and a record of how far the
                    escalation got.  Never a guess.

RESUMING
========
`data/results.jsonl` is append-only and keyed by catalog row.  A row with a
terminal verdict is skipped on the next run; a STILL_OPEN row is retried
whenever the budget offered is larger than the one it survived.  So the
intended use -- run now against the 100 OPEN rows, run again when the sweep
finishes against the final set -- costs only the new rows plus the
escalation of the old ones.
"""

import argparse
import json
import os
import sys
import time

sys.dont_write_bytecode = True
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np                                          # noqa: E402

import catalog                                              # noqa: E402
import gordan                                               # noqa: E402
import weaponA                                              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
RESULTS = os.path.join(DATA, 'results.jsonl')
C_REAL = os.path.join(DATA, 'certs_realizable.jsonl')
C_NONREAL = os.path.join(DATA, 'certs_nonrealizable.jsonl')
C_NOBFP = os.path.join(DATA, 'certs_no_bfp.jsonl')
SNAPSHOT = os.path.join(DATA, 'open_set.txt')
N, R = 9, 4


def _append(path, rec):
    with open(path, 'a') as fh:
        fh.write(json.dumps(rec) + '\n')
        fh.flush()
        os.fsync(fh.fileno())


def load_results():
    out = {}
    if os.path.exists(RESULTS):
        with open(RESULTS) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    rec = json.loads(line)
                    out[int(rec['row'])] = rec
    return out


# ----------------------------------------------------------------------
# enumerate
# ----------------------------------------------------------------------

def cmd_enumerate(a):
    os.makedirs(DATA, exist_ok=True)
    rows = catalog.rows_with_status(catalog.OPEN)
    CHI = catalog.chi_of_rows(rows)
    dep = np.asarray(catalog.arrays()['depth'])
    with open(SNAPSHOT, 'w') as fh:
        for r, c in zip(rows, CHI):
            fh.write('%d %d %s\n' % (r, int(dep[r]), catalog.chi_string(c)))
    st = catalog.status_counts()
    done = catalog.NROWS - st[catalog.TODO]
    print('sweep progress %d/%d (%.2f%%)' % (done, catalog.NROWS,
                                             100.0 * done / catalog.NROWS))
    for k, v in sorted(st.items()):
        print('  %-22s %9d' % (catalog.STATUS[k], v))
    print('wrote %s (%d rows)' % (SNAPSHOT, len(rows)))


def read_snapshot():
    if not os.path.exists(SNAPSHOT):
        raise SystemExit('run `attack.py enumerate` first')
    out = []
    with open(SNAPSHOT) as fh:
        for line in fh:
            p = line.split()
            if len(p) == 3:
                out.append((int(p[0]), int(p[1]), p[2]))
    return out


# ----------------------------------------------------------------------
# run
# ----------------------------------------------------------------------

def _chi_array(s):
    return np.array([1 if c == '+' else -1 for c in s], dtype=np.int8)


def cmd_run(a):
    os.makedirs(DATA, exist_ok=True)
    todo = read_snapshot()
    if a.rows:
        want = {int(x) for x in a.rows.split(',')}
        todo = [t for t in todo if t[0] in want]
    done = load_results()
    sup0 = gordan.Support(N, R, 'L0', verify=a.verify_identities)
    sup1 = gordan.Support(N, R, 'L1', verify=a.verify_identities)
    if a.verify_identities:
        print('identity tables re-verified on random integer configurations')
    S = weaponA.Searcher(seed=a.seed, depth=a.walk_depth)
    arrays = catalog.arrays()
    kidx = None
    if not a.no_children:
        t0 = time.time()
        order, start = catalog.children_index()
        kidx = (order, start)
        print('child index built in %.1f s' % (time.time() - t0))
    fp = None
    if a.fp:
        import fpoly
        fp = fpoly
    n_run = 0
    tally = {}
    for (row, depth, chis) in todo:
        prev = done.get(row)
        if prev is not None:
            if prev['verdict'] in ('REALIZABLE', 'NON_REALIZABLE'):
                continue
            if prev.get('budget', 0) >= a.budget and not a.force:
                continue
        if a.limit and n_run >= a.limit:
            break
        n_run += 1
        chi = _chi_array(chis)
        rec = decide(row, depth, chi, chis, sup0, sup1, S, arrays, kidx,
                     a.budget, fp, a.fp_degree)
        _append(RESULTS, rec)
        tally[rec['verdict']] = tally.get(rec['verdict'], 0) + 1
        print('row %8d d%02d  %-12s %6.1f s  %s'
              % (row, depth, rec['verdict'], rec['seconds'],
                 rec.get('note', '')), flush=True)
    print('\nran %d rows: %s' % (n_run, tally))


def decide(row, depth, chi, chis, sup0, sup1, S, arrays, kidx, budget,
           fp=None, fp_degree=3):
    t0 = time.time()
    rec = {'row': row, 'depth': depth, 'chi': chis, 'budget': budget,
           'stages': {}}

    # ---- stage 0: the biquadratic final polynomial, independently ------
    sys0 = sup0.system(chi)
    if sys0.contradiction is not None:
        r = gordan.contradiction_record(N, R, chis, sys0.contradiction, sup0)
        _append(C_NONREAL, r)
        rec.update(verdict='NON_REALIZABLE', method='MONOCHROME',
                   seconds=time.time() - t0, note='monochrome relation at L0')
        return rec
    cert0, i0 = gordan.find_gordan(chi, sup0, sys=sys0)
    rec['stages']['L0_gordan'] = {'found': cert0 is not None,
                                  'rows': i0['nrows']}
    if cert0 is None:
        # THE HYPOTHESIS OF THE CONJECTURE, CERTIFIED.  Do this for every
        # class, not only for the ones weapon A fails on: "no biquadratic
        # final polynomial" is what makes an OPEN class evidence about the
        # sharpened conjecture at all, and it must be a proof rather than a
        # failed search.  ~0.3 s at L0, ~0.7 s at L1.
        u0, w0 = gordan.find_witness(chi, sup0, sys=sys0)
        rec['stages']['L0_witness'] = {'found': u0 is not None,
                                       'margin': w0.get('margin')}
        if u0 is not None:
            _append(C_NOBFP, gordan.witness_record(N, R, chis, u0, sup0))
        sys1 = sup1.system(chi)
        if sys1.contradiction is not None:
            r = gordan.contradiction_record(N, R, chis, sys1.contradiction,
                                            sup1)
            _append(C_NONREAL, r)
            rec.update(verdict='NON_REALIZABLE', method='MONOCHROME-L1',
                       seconds=time.time() - t0,
                       note='NO BIQUADRATIC FINAL POLYNOMIAL: '
                            'COUNTEREXAMPLE to the sharpened conjecture')
            return rec
        cert1, i1 = gordan.find_gordan(chi, sup1, sys=sys1)
        rec['stages']['L1_gordan'] = {'found': cert1 is not None,
                                      'rows': i1['nrows']}
        if cert1 is not None:
            _append(C_NONREAL, gordan.gordan_record(N, R, chis, cert1, sup1))
            rec.update(verdict='NON_REALIZABLE', method='GORDAN-L1',
                       seconds=time.time() - t0,
                       note='NO BIQUADRATIC FINAL POLYNOMIAL (u certified): '
                            'COUNTEREXAMPLE to the sharpened conjecture')
            return rec
        u1, w1 = gordan.find_witness(chi, sup1, sys=sys1)
        rec['stages']['L1_witness'] = {'found': u1 is not None,
                                       'margin': w1.get('margin')}
        if u1 is not None:
            _append(C_NOBFP, gordan.witness_record(N, R, chis, u1, sup1))
    if cert0 is not None:
        r = gordan.gordan_record(N, R, chis, cert0, sup0)
        _append(C_NONREAL, r)
        b = gordan.gordan_record_bfp(N, R, chis, cert0, sup0)
        if b is not None:
            _append(os.path.join(DATA, 'certs_nonrealizable_bfpschema.jsonl'), b)
        rec.update(verdict='NON_REALIZABLE', method='GORDAN-L0',
                   seconds=time.time() - t0,
                   note='biquadratic final polynomial (the sweep should have '
                        'found this: DISAGREEMENT)')
        return rec

    # ---- stage 1: weapon A --------------------------------------------
    kids = None
    if kidx is not None:
        order, start = kidx
        kids = order[start[row]:start[row + 1]]
    Z, log = S.attack(chi, budget=budget, row=row, arrays=arrays, kids=kids)
    rec['stages']['weaponA'] = {'found': log.get('found'),
                                'lp_feasible': log['lp_feasible'],
                                'lp_infeasible': log['lp_infeasible'],
                                'sources': log['sources'],
                                'seconds': round(log['time'], 2)}
    if Z is not None:
        r = weaponA.realizable_record(N, R, chis, Z)
        _append(C_REAL, r)
        rec.update(verdict='REALIZABLE', method='weaponA:' + str(log['found']),
                   seconds=time.time() - t0,
                   note='|entry| <= %d' % int(np.abs(np.asarray(Z)).max()))
        return rec

    # ---- stage 3: general final polynomials ---------------------------
    if fp is not None:
        plan = [(2, sup0), (2, sup1)]
        if fp_degree >= 3:
            plan += [(3, sup0), (3, sup1)]
        for (d, sp) in plan:
            tag = 'fp%d_%s' % (d, sp.level)
            cert, info = fp.find_fp(chi, degree=d, level=sp.level, sup=sp)
            rec['stages'][tag] = info
            if cert is not None:
                _append(C_NONREAL, fp.fp_record(N, R, chis, cert, d, sp))
                rec.update(verdict='NON_REALIZABLE', method=tag.upper(),
                           seconds=time.time() - t0,
                           note='NO BIQUADRATIC FINAL POLYNOMIAL (u '
                                'certified): COUNTEREXAMPLE to the sharpened '
                                'conjecture')
                return rec

    rec.update(verdict='STILL_OPEN', method=None, seconds=time.time() - t0,
               note='no BFP (certified), no realization found')
    return rec


# ----------------------------------------------------------------------
# witness backfill
# ----------------------------------------------------------------------

def cmd_witness(a):
    """Certify "no biquadratic final polynomial" for every class in the
    snapshot, whatever verdict it ended up with.

    A class that weapon A realizes is still a data point about the sharpened
    conjecture -- in fact it is THE data point -- and it only counts if the
    hypothesis "has no BFP" is proved rather than assumed.  Runs are appended
    idempotently: a class already carrying a witness for a given family set
    is skipped.
    """
    have = set()
    if os.path.exists(C_NOBFP):
        with open(C_NOBFP) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    r = json.loads(line)
                    have.add((r['chi'], tuple(r.get('families', ()))))
    sup = {lv: gordan.Support(N, R, lv, verify=False) for lv in ('L0', 'L1')}
    todo = read_snapshot()
    n = {'L0': 0, 'L1': 0}
    miss = []
    for (row, depth, chis) in todo:
        chi = _chi_array(chis)
        for lv in ('L0', 'L1'):
            key = (chis, tuple(gordan.LEVELS[lv]))
            if key in have:
                n[lv] += 1
                continue
            u, info = gordan.find_witness(chi, sup[lv])
            if u is None:
                miss.append((row, lv, info))
                continue
            _append(C_NOBFP, gordan.witness_record(N, R, chis, u, sup[lv]))
            have.add(key)
            n[lv] += 1
    print('classes with a CERTIFIED "no final polynomial" witness:')
    for lv in ('L0', 'L1'):
        print('  %s (%s): %d / %d' % (lv, '+'.join(gordan.LEVELS[lv]),
                                      n[lv], len(todo)))
    if miss:
        print('  *** %d classes have NO witness -- they carry a final '
              'polynomial and are NON-REALIZABLE:' % len(miss))
        for row, lv, info in miss[:20]:
            print('      row %d at %s (%s)' % (row, lv, info))


# ----------------------------------------------------------------------
# report
# ----------------------------------------------------------------------

def cmd_report(a):
    res = load_results()
    if not res:
        print('no results yet')
        return
    by = {}
    for r in res.values():
        by.setdefault(r['verdict'], []).append(r)
    print('%d rows attacked' % len(res))
    for k in sorted(by):
        print('  %-14s %5d' % (k, len(by[k])))
    ok = by.get('REALIZABLE', [])
    if ok:
        meth = {}
        for r in ok:
            meth[r['method']] = meth.get(r['method'], 0) + 1
        print('  realizable by source: %s' % meth)
        t = [r['seconds'] for r in ok]
        print('  realization time: median %.2f s, max %.2f s'
              % (float(np.median(t)), max(t)))
    so = by.get('STILL_OPEN', [])
    if so:
        nob = sum(1 for r in so
                  if r['stages'].get('L0_witness', {}).get('found'))
        print('  STILL_OPEN with a CERTIFIED no-BFP witness: %d/%d'
              % (nob, len(so)))
    bad = [r for r in res.values() if r['verdict'] == 'NON_REALIZABLE']
    if bad:
        print('\n  *** NON_REALIZABLE OPEN classes: %d' % len(bad))
        for r in bad:
            print('      row %d  %s  %s' % (r['row'], r['method'],
                                            r.get('note')))


# ----------------------------------------------------------------------
# entry point
# ----------------------------------------------------------------------

def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    e = sub.add_parser('enumerate')
    e.set_defaults(fn=cmd_enumerate)
    r = sub.add_parser('run')
    r.add_argument('--budget', type=float, default=60.0)
    r.add_argument('--limit', type=int, default=0)
    r.add_argument('--rows', default=None)
    r.add_argument('--seed', type=int, default=20260801)
    r.add_argument('--walk-depth', type=int, default=8)
    r.add_argument('--fp', action='store_true')
    r.add_argument('--fp-degree', type=int, default=3)
    r.add_argument('--force', action='store_true')
    r.add_argument('--no-children', action='store_true')
    r.add_argument('--verify-identities', action='store_true')
    r.set_defaults(fn=cmd_run)
    w = sub.add_parser('witness')
    w.set_defaults(fn=cmd_witness)
    p = sub.add_parser('report')
    p.set_defaults(fn=cmd_report)
    v = sub.add_parser('validate')
    v.add_argument('--n', type=int, default=40)
    v.add_argument('--budget', type=float, default=60.0)
    v.set_defaults(fn=lambda a: __import__('validate').run(a))
    c = sub.add_parser('canaries')
    c.set_defaults(fn=lambda a: __import__('canaries').run(a))
    a = ap.parse_args()
    a.fn(a)


if __name__ == '__main__':
    main()
