#!/usr/bin/env python3
"""The full (4,9) sweep: walk the mutation tree over all 9 276 595 classes.

    python sweep49.py init                       # memmaps + the root
    python sweep49.py run --workers 4            # the long run (resumable)
    python sweep49.py report                     # split, residue, open set

DESIGN, and why each choice
===========================
*Wave order.* A class is realized by crossing one wall from its PARENT's
realization, so parents must be done first.  The tree has depth 27, so the
sweep is 27 waves; inside a wave every row is independent.  A barrier
between waves is the only synchronisation.

*Memmaps, not RAM.* The realizations live in `Z.dat`, an (N,4,9) int32
memmap (1.34 GB), and the per-row status in `st.dat` (N bytes).  Backing
them with disk rather than RAM is deliberate: this is the owner's 16 GB
working machine and it has been OOM-killed twice.  The OS pages what it
needs; four workers share one copy; and the status map IS the checkpoint,
so a kill costs at most the chunks in flight.

*Chunked, resumable.* Each wave is cut into chunks; a worker skips any row
whose status is already set.  Certificate shards are opened append-only and
truncated to their last complete line on resume, so a mid-write kill cannot
leave a half-JSON record for `checkcert.py` to trip over.

PER-CLASS LOGIC
===============
    parent realized?  -> cross one wall from it                (~16 ms)
    crossing failed   -> BFP first: a crossing failure is, empirically,
                         exactly a non-realizable class        (~250 ms)
    orphan (parent not realized) -> cheap direct search first, since
                         orphans are mostly realizable          (~75 ms)
    still open        -> mutation warm-start, then heavy warm-start
    nothing worked    -> OPEN, recorded and enumerated, never guessed at

Every settled class ends with a certificate in the JSONL schema
`checkcert.py` accepts.  No verdict is ever recorded without one.
"""

import argparse
import json
import os
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

# BLAS threads must be pinned BEFORE numpy loads: 4 workers each
# spawning 12 threads on 6 physical cores cost ~15x in an earlier run.
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import omdecode                                            # noqa: E402
import realize as rz                                       # noqa: E402
import bfp as bfpmod                                       # noqa: E402
import treewalk as tw                                      # noqa: E402

N, R = 9, 4
NROWS = 9276595
STATE = os.path.join(HERE, 'sweep_state')
CERTS = os.path.join(STATE, 'certs')

TODO, WALK, REPAIR, NONREAL, OPEN = 0, 1, 2, 3, 4
NAMES = {WALK: 'REALIZABLE(walk)', REPAIR: 'REALIZABLE(repair)',
         NONREAL: 'NON_REALIZABLE', OPEN: 'OPEN'}

# stage budgets for the repair path
A_KW = dict(tries=2, sweeps=15, rerolls=3, wall_budget=3)
C_KW = dict(tries=8, sweeps=40, rerolls=8, wall_budget=12)
E_KW = dict(kmax=30, attempts=3, tries=1, sweeps=15)
EH_KW = dict(kmax=30, attempts=10, tries=2, sweeps=30)


def _mm(mode):
    Z = np.memmap(os.path.join(STATE, 'Z.dat'), dtype=np.int32, mode=mode,
                  shape=(NROWS, R, N))
    st = np.memmap(os.path.join(STATE, 'st.dat'), dtype=np.uint8, mode=mode,
                   shape=(NROWS,))
    return Z, st


# ----------------------------------------------------------------------
# init
# ----------------------------------------------------------------------

def cmd_init(a):
    os.makedirs(CERTS, exist_ok=True)
    hi, lo, stab, w, man = tw.load(verify_hashes=True)
    root = man['witness']['root_row']
    if len(hi) != NROWS:
        raise SystemExit('row count %d != %d' % (len(hi), NROWS))
    Zp = os.path.join(STATE, 'Z.dat')
    fresh = not os.path.exists(Zp)
    Z, st = _mm('w+' if fresh else 'r+')
    if fresh:
        st[:] = TODO
        print('allocated Z.dat (%.2f GB) and st.dat' % (Z.nbytes / 1e9))
    # depth order, computed once and cached
    op = os.path.join(STATE, 'order.npy')
    if not os.path.exists(op):
        d = w['depth']
        order = np.argsort(d.astype(np.int64) * (NROWS + 1) +
                           np.arange(NROWS, dtype=np.int64), kind='stable')
        np.save(op, order.astype(np.int64))
        np.save(os.path.join(STATE, 'depth.npy'), d.astype(np.int16))
        print('cached wave order, max depth %d' % d.max())
    geom = rz.Geom(N, R)
    if st[root] == TODO:
        chi = omdecode.signs_from_keys(N, R, hi[root:root + 1], lo[root:root + 1])[0]
        Z0, _ = rz.realize(chi, geom, tries=8, sweeps=50)
        if Z0 is None:
            raise SystemExit('could not realize the root')
        Z[root] = Z0
        st[root] = WALK
        with open(os.path.join(CERTS, 'shard_root.jsonl'), 'w') as fh:
            fh.write(json.dumps({'n': N, 'r': R,
                                 'chi': omdecode.string_from_signs(chi),
                                 'verdict': 'REALIZABLE',
                                 'matrix': [[int(v) for v in r] for r in Z0]}) + '\n')
        print('root row %d realized, |entry| <= %d' % (root, np.abs(Z0).max()))
    # Flatten the per-row arrays to .npy so workers can MEMMAP them.  Four
    # workers each np.load-ing the npz cost ~305 MB of PRIVATE memory apiece
    # (~1.2 GB); memmapped they share one copy through the page cache, which
    # matters because this is the owner's 16 GB working machine.
    need = {'hi': hi, 'lo': lo, 'parent': w['parent'], 'flip': w['flip'],
            'sigma': w['sigma'], 'eps': w['eps'], 'gsgn': w['gsgn']}
    for k, v in need.items():
        q = os.path.join(STATE, k + '.npy')
        if not os.path.exists(q):
            np.save(q, np.ascontiguousarray(v))
    print('shared arrays written (%.0f MB total)'
          % (sum(os.path.getsize(os.path.join(STATE, k + '.npy'))
                 for k in need) / 1e6))
    Z.flush()
    st.flush()
    print('init done. %d rows todo' % int((st[:] == TODO).sum()))


# ----------------------------------------------------------------------
# worker
# ----------------------------------------------------------------------

_G = {}


def _ctx():
    if not _G:
        L = lambda k: np.load(os.path.join(STATE, k + '.npy'), mmap_mode='r')
        _G['hi'], _G['lo'] = L('hi'), L('lo')
        _G['parent'], _G['flip'] = L('parent'), L('flip')
        _G['sig'], _G['eps'], _G['gsg'] = L('sigma'), L('eps'), L('gsgn')
        _G['act'] = tw.Action()
        _G['geom'] = rz.Geom(N, R)
        _G['gp'] = bfpmod.GPSystem(N, R)
        _G['Z'], _G['st'] = _mm('r+')
        _G['rng'] = np.random.default_rng(20260801)
    return _G


def _truncate_partial(path):
    """Drop a trailing half-written JSON line left by a kill."""
    if not os.path.exists(path) or os.path.getsize(path) == 0:
        return
    with open(path, 'rb+') as fh:
        fh.seek(0, os.SEEK_END)
        size = fh.tell()
        back = min(size, 1 << 16)
        fh.seek(size - back)
        tail = fh.read()
        nl = tail.rfind(b'\n')
        if nl < 0:
            fh.truncate(0)
        else:
            fh.truncate(size - back + nl + 1)


def _bfp_record(chi, gp):
    cert, _ = bfpmod.find_bfp(chi, gp)
    if cert is None:
        return None
    terms = []
    for (ri, big, small, ww) in cert['terms']:
        L, abcd, _ = gp.rel[ri]
        terms.append({'L': list(L), 'abcd': list(abcd), 'big': int(big),
                      'small': int(small), 'w': int(ww)})
    return {'n': N, 'r': R, 'chi': omdecode.string_from_signs(chi),
            'verdict': 'NON_REALIZABLE', 'bfp': terms}


def do_chunk(job):
    wid, rows = job
    g = _ctx()
    Z, st, geom, gp, act = g['Z'], g['st'], g['geom'], g['gp'], g['act']
    hi, lo, parent, flip = g['hi'], g['lo'], g['parent'], g['flip']
    sig, eps, gsg, rng = g['sig'], g['eps'], g['gsg'], g['rng']
    rows = np.asarray(rows)
    todo = rows[st[rows] == TODO]
    if len(todo) == 0:
        return wid, 0, {}, 0.0
    path = os.path.join(CERTS, 'shard_%02d.jsonl' % wid)
    fh = open(path, 'a')
    CHI = omdecode.signs_from_keys(N, R, hi[todo], lo[todo])
    counts = {}
    t0 = time.time()
    for k, i in enumerate(todo):
        i = int(i)
        chi = CHI[k]
        Zi = None
        how = None
        p = int(parent[i])
        crossed_attempted = False
        if st[p] in (WALK, REPAIR):
            crossed_attempted = True
            mut = act.on_chi(chi, sig[i], int(eps[i]), int(gsg[i]))
            X = tw.cross_from(np.asarray(Z[p]), mut, geom, rng, int(flip[i]))
            if X is not None:
                s2, e2, g2 = act.inverse_params(sig[i], int(eps[i]), int(gsg[i]))
                Zi, _D = rz._rationalise(act.on_matrix(X, s2, e2, g2), chi, geom)
                if Zi is not None:
                    how = WALK
        if Zi is None and not crossed_attempted:
            # ORPHAN: no parent realization.  Orphans are mostly realizable,
            # so a cheap direct search beats paying for BFP first.
            Zi, _ = rz.realize(chi, geom, seed=i, **A_KW)
            if Zi is not None:
                how = REPAIR
        rec = None
        if Zi is None:
            # A crossing failure is, on every sample measured, exactly a
            # non-realizable class -- so BFP is the cheapest next question.
            rec = _bfp_record(chi, gp)
            if rec is not None:
                how = NONREAL
        if Zi is None and rec is None:
            for kw in (C_KW, E_KW, EH_KW):
                if 'kmax' in kw:
                    Zi, _ = rz.realize_via_mutant(chi, geom, seed=i, **kw)
                else:
                    Zi, _ = rz.realize(chi, geom, seed=i, **kw)
                if Zi is not None:
                    how = REPAIR
                    break
        if Zi is not None:
            chk = rz.exact_bracket_signs(Zi, geom)
            if chk is None or not np.array_equal(chk, chi):
                raise SystemExit('row %d: produced matrix does not realize '
                                 'the class' % i)
            Z[i] = Zi
            rec = {'n': N, 'r': R, 'chi': omdecode.string_from_signs(chi),
                   'verdict': 'REALIZABLE',
                   'matrix': [[int(v) for v in r] for r in Zi]}
        elif rec is None:
            how = OPEN
            rec = {'n': N, 'r': R, 'chi': omdecode.string_from_signs(chi),
                   'verdict': 'RESIDUE', 'row': i}
        fh.write(json.dumps(rec) + '\n')
        st[i] = how
        counts[how] = counts.get(how, 0) + 1
    fh.flush()
    os.fsync(fh.fileno())
    fh.close()
    st.flush()
    Z.flush()
    return wid, len(todo), counts, time.time() - t0


# ----------------------------------------------------------------------
# run
# ----------------------------------------------------------------------

def cmd_run(a):
    order = np.load(os.path.join(STATE, 'order.npy'))
    depth = np.load(os.path.join(STATE, 'depth.npy'))
    Z, st = _mm('r+')
    for wid in range(a.workers):
        _truncate_partial(os.path.join(CERTS, 'shard_%02d.jsonl' % wid))
    total = {}
    t00 = time.time()
    ndone = int((st[:] != TODO).sum())
    print('[sweep] %d/%d rows already done; %d workers, chunk %d'
          % (ndone, NROWS, a.workers, a.chunk), flush=True)
    dmax = int(depth.max())
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for d in range(dmax + 1):
            wave = order[depth[order] == d]
            wave = wave[st[wave] == TODO]
            if len(wave) == 0:
                continue
            chunks = [wave[s:s + a.chunk] for s in range(0, len(wave), a.chunk)]
            jobs = [(j % a.workers, c) for j, c in enumerate(chunks)]
            t0 = time.time()
            got = 0
            futs = {ex.submit(do_chunk, j): j for j in jobs}
            for f in as_completed(futs):
                wid, n, counts, dt = f.result()
                got += n
                for k, v in counts.items():
                    total[k] = total.get(k, 0) + v
                ndone += n
            el = time.time() - t00
            rate = 1000.0 * el * a.workers / max(ndone, 1)
            left = (NROWS - ndone) * rate / 1000.0 / a.workers / 3600.0
            print('[sweep] depth %2d: %8d rows in %6.0f s | total %8d/%d '
                  '| %.1f ms/class/core | eta %.1f h | %s'
                  % (d, got, time.time() - t0, ndone, NROWS, rate, left,
                     {NAMES.get(k, k): v for k, v in sorted(total.items())}),
                  flush=True)
    print('[sweep] COMPLETE in %.1f h; %s'
          % ((time.time() - t00) / 3600.0,
             {NAMES.get(k, k): v for k, v in sorted(total.items())}), flush=True)


# ----------------------------------------------------------------------
# report
# ----------------------------------------------------------------------

def cmd_report(a):
    import math
    Z, st = _mm('r')
    s = np.asarray(st)
    n = {k: int((s == k).sum()) for k in (TODO, WALK, REPAIR, NONREAL, OPEN)}
    done = NROWS - n[TODO]
    real = n[WALK] + n[REPAIR]
    print('rows            %d of %d done (%.3f%%)' % (done, NROWS, 100.0 * done / NROWS))
    print('  REALIZABLE    %9d   (walk %d, repair %d)' % (real, n[WALK], n[REPAIR]))
    print('  NON_REALIZABLE%9d' % n[NONREAL])
    print('  OPEN          %9d' % n[OPEN])
    if done:
        print('  split so far  realizable %.4f%%  non-realizable %.4f%%'
              % (100.0 * real / done, 100.0 * n[NONREAL] / done))
        k = n[OPEN]
        z = 1.96
        p = k / done
        dd = 1 + z * z / done
        c = (p + z * z / (2 * done)) / dd
        h = z * math.sqrt(p * (1 - p) / done + z * z / (4 * done * done)) / dd
        print('  OPEN rate     %.6f%%  95%% CI [%.6f%%, %.6f%%]'
              % (100 * p, 100 * max(0, c - h), 100 * min(1, c + h)))
    if n[OPEN] and a.enumerate_open:
        rows = np.flatnonzero(s == OPEN)
        hi, lo, stab = omdecode.load_coverage_4_9(verify=False)
        CHI = omdecode.signs_from_keys(N, R, hi[rows], lo[rows])
        path = os.path.join(STATE, 'open_classes.txt')
        with open(path, 'w') as fh:
            for r, chi in zip(rows, CHI):
                fh.write('%d %d %s\n' % (r, stab[r],
                                         omdecode.string_from_signs(chi)))
        print('  enumerated %d OPEN classes -> %s' % (len(rows), path))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    i = sub.add_parser('init'); i.set_defaults(fn=cmd_init)
    r = sub.add_parser('run')
    r.add_argument('--workers', type=int, default=4)
    r.add_argument('--chunk', type=int, default=8000)
    r.set_defaults(fn=cmd_run)
    p = sub.add_parser('report')
    p.add_argument('--enumerate-open', action='store_true')
    p.set_defaults(fn=cmd_report)
    a = ap.parse_args()
    a.fn(a)


if __name__ == '__main__':
    main()
