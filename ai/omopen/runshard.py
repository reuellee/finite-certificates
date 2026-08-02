#!/usr/bin/env python3
"""Run `attack.decide` over a SHARD of the OPEN snapshot, in its own files.

`attack.py run` is single-process and appends to one `data/results.jsonl`.
With 659 OPEN rows and a finished sweep no longer competing for cores, the
sensible thing is four workers -- but four processes appending to one file
is a corruption hazard, so each shard writes its own set of files and
`merge` folds them back into the canonical ones afterwards.

    python runshard.py run --shard 0 --nshards 4 [--budget 60] [--fp] ...
    python runshard.py merge
    python runshard.py todo            # rows still lacking a terminal verdict

Everything else -- the decision logic, the certificate schemas, the resume
rule -- is `attack.py`'s, imported unchanged.  This file only handles which
rows a worker takes and where it writes.

Two deliberate departures from `attack.cmd_run`:

  * the child index is memmapped from `data/child_*.npy` (built once by the
    caller) instead of rebuilt per process, which costs ~300 MB each;
  * `gordan.Support` is constructed with verify=False, because the identity
    tables are verified once in preflight (`python gplib.py`) and paying
    5,544 relations x 60 configurations per process per pass is waste.
"""

import argparse
import glob
import json
import os
import sys
import time

sys.dont_write_bytecode = True
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np                                          # noqa: E402

import attack                                               # noqa: E402
import catalog                                              # noqa: E402
import gordan                                               # noqa: E402
import weaponA                                              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
SHARDS = os.path.join(DATA, 'shards')
N, R = 9, 4

TERMINAL = ('REALIZABLE', 'NON_REALIZABLE')


# ----------------------------------------------------------------------
# results, merged across the canonical file and every shard file
# ----------------------------------------------------------------------

def _read_jsonl(path):
    out = []
    if os.path.exists(path):
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    try:
                        out.append(json.loads(line))
                    except ValueError:
                        # a torn last line from a killed worker; ignore it
                        pass
    return out


def all_results():
    """row -> best record seen, over data/results.jsonl and all shard files."""
    best = {}

    def take(rec):
        r = int(rec['row'])
        old = best.get(r)
        if old is None:
            best[r] = rec
            return
        if old['verdict'] in TERMINAL:
            return
        if rec['verdict'] in TERMINAL or \
                rec.get('budget', 0) > old.get('budget', 0):
            best[r] = rec

    for rec in _read_jsonl(attack.RESULTS):
        take(rec)
    for p in sorted(glob.glob(os.path.join(SHARDS, 'results_*.jsonl'))):
        for rec in _read_jsonl(p):
            take(rec)
    return best


def pending(budget):
    """Snapshot rows that still deserve work at this budget."""
    todo = attack.read_snapshot()
    done = all_results()
    out = []
    for (row, depth, chis) in todo:
        prev = done.get(row)
        if prev is not None:
            if prev['verdict'] in TERMINAL:
                continue
            if prev.get('budget', 0) >= budget:
                continue
        out.append((row, depth, chis))
    return out


# ----------------------------------------------------------------------
# run
# ----------------------------------------------------------------------

def read_todo(path):
    out = []
    with open(path) as fh:
        for line in fh:
            p = line.split()
            if len(p) == 3:
                out.append((int(p[0]), int(p[1]), p[2]))
    return out


def cmd_run(a):
    os.makedirs(SHARDS, exist_ok=True)
    # A FIXED todo file is mandatory for >1 shard: if each worker recomputed
    # `pending()` it would see a different set (the other workers are already
    # writing results), the i % nshards assignment would shift under them, and
    # rows would be silently DROPPED.  `runshard.py todo --out FILE` freezes it.
    if a.todo:
        todo = read_todo(a.todo)
    elif a.nshards > 1:
        raise SystemExit('--todo FILE is required when --nshards > 1')
    else:
        todo = pending(a.budget)
    todo = [t for i, t in enumerate(todo) if i % a.nshards == a.shard]
    if a.limit:
        todo = todo[:a.limit]
    tag = '%s_s%d' % (a.tag, a.shard)
    attack.RESULTS = os.path.join(SHARDS, 'results_%s.jsonl' % tag)
    attack.C_REAL = os.path.join(SHARDS, 'certs_realizable_%s.jsonl' % tag)
    attack.C_NONREAL = os.path.join(SHARDS,
                                    'certs_nonrealizable_%s.jsonl' % tag)
    attack.C_NOBFP = os.path.join(SHARDS, 'certs_no_bfp_%s.jsonl' % tag)

    print('shard %d/%d  %d rows  budget %.0f s  walk-depth %d  fp=%s'
          % (a.shard, a.nshards, len(todo), a.budget, a.walk_depth, a.fp),
          flush=True)
    if not todo:
        print('nothing to do')
        return

    sup0 = gordan.Support(N, R, 'L0', verify=False)
    sup1 = gordan.Support(N, R, 'L1', verify=False)
    S = weaponA.Searcher(seed=a.seed + 1000 * a.shard, depth=a.walk_depth)
    arrays = catalog.arrays()
    kidx = None
    if not a.no_children:
        op = os.path.join(DATA, 'child_order.npy')
        sp = os.path.join(DATA, 'child_start.npy')
        if os.path.exists(op) and os.path.exists(sp):
            kidx = (np.load(op, mmap_mode='r'), np.load(sp, mmap_mode='r'))
        else:
            kidx = catalog.children_index()
    fp = None
    if a.fp:
        import fpoly
        fp = fpoly

    tally = {}
    t_start = time.time()
    for k, (row, depth, chis) in enumerate(todo):
        chi = attack._chi_array(chis)
        # attack.decide slices `kids` out of kidx itself; the memmapped
        # arrays slice exactly like the in-memory ones did.
        rec = attack.decide(row, depth, chi, chis, sup0, sup1, S, arrays,
                            kidx, a.budget, fp, a.fp_degree)
        attack._append(attack.RESULTS, rec)
        tally[rec['verdict']] = tally.get(rec['verdict'], 0) + 1
        print('[s%d %3d/%3d] row %8d d%02d  %-14s %7.1f s  %s'
              % (a.shard, k + 1, len(todo), row, depth, rec['verdict'],
                 rec['seconds'], rec.get('note', '')), flush=True)
    print('\nshard %d done in %.0f s: %s'
          % (a.shard, time.time() - t_start, tally), flush=True)


# ----------------------------------------------------------------------
# merge
# ----------------------------------------------------------------------

def cmd_merge(a):
    # HAZARD, learned the hard way: this renames shard files out from under
    # any worker still running.  No record is lost (`attack._append` opens,
    # writes, fsyncs and closes per record, and the next append simply
    # recreates the file), but the MERGED VIEW IS THEN PARTIAL and anything
    # reasoned from it is wrong.  Merge only when every shard has printed
    # its "shard N done" line.
    stamp = time.strftime('%Y%m%dT%H%M%S')

    def _retire(p):
        """Rename with a unique suffix; a fixed '.merged' collides when a
        pass is merged twice (and the first collision aborted a merge
        half-way, which is how this was found)."""
        q = p + '.merged.' + stamp
        k = 0
        while os.path.exists(q):
            k += 1
            q = '%s.merged.%s.%d' % (p, stamp, k)
        os.rename(p, q)

    def _fold(pattern, dest):
        """Append every shard record not already in dest.  Line-level dedup
        makes merge IDEMPOTENT, so a half-finished merge can simply be
        re-run."""
        have = set()
        if os.path.exists(dest):
            with open(dest) as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        have.add(line)
        n = 0
        for p in sorted(glob.glob(os.path.join(SHARDS, pattern))):
            recs = _read_jsonl(p)
            if recs:
                with open(dest, 'a') as fh:
                    for rec in recs:
                        s = json.dumps(rec)
                        if s in have:
                            continue
                        have.add(s)
                        fh.write(s + '\n')
                        n += 1
            _retire(p)
        return n

    n_res = _fold('results_*.jsonl', attack.RESULTS)
    for kind, dest in (('certs_realizable', attack.C_REAL),
                       ('certs_nonrealizable', attack.C_NONREAL),
                       ('certs_no_bfp', attack.C_NOBFP)):
        n = _fold(kind + '_*.jsonl', dest)
        print('merged %-22s %6d new records -> %s'
              % (kind, n, os.path.basename(dest)))
    print('merged results               %6d new records' % n_res)
    res = all_results()
    by = {}
    for r in res.values():
        by[r['verdict']] = by.get(r['verdict'], 0) + 1
    print('now decided: %s (%d rows)' % (by, len(res)))


def cmd_todo(a):
    p = pending(a.budget)
    print('%d rows pending at budget %.0f' % (len(p), a.budget))
    for (row, depth, chis) in p[:60]:
        print('  %8d d%02d' % (row, depth))
    if a.out:
        with open(a.out, 'w') as fh:
            for (row, depth, chis) in p:
                fh.write('%d %d %s\n' % (row, depth, chis))
        print('wrote %s' % a.out)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    r = sub.add_parser('run')
    r.add_argument('--shard', type=int, default=0)
    r.add_argument('--nshards', type=int, default=4)
    r.add_argument('--tag', default='p1')
    r.add_argument('--budget', type=float, default=60.0)
    r.add_argument('--limit', type=int, default=0)
    r.add_argument('--seed', type=int, default=20260802)
    r.add_argument('--walk-depth', type=int, default=8)
    r.add_argument('--fp', action='store_true')
    r.add_argument('--fp-degree', type=int, default=3)
    r.add_argument('--no-children', action='store_true')
    r.add_argument('--todo', default=None,
                   help='frozen row list from `runshard.py todo --out`; '
                        'required when --nshards > 1')
    r.set_defaults(fn=cmd_run)
    m = sub.add_parser('merge')
    m.set_defaults(fn=cmd_merge)
    t = sub.add_parser('todo')
    t.add_argument('--budget', type=float, default=1e18)
    t.add_argument('--out', default=None)
    t.set_defaults(fn=cmd_todo)
    a = ap.parse_args()
    a.fn(a)


if __name__ == '__main__':
    main()
