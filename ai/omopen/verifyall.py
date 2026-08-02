#!/usr/bin/env python3
"""Re-verify EVERY certificate the (4,9) sweep wrote, with an independent
checker, streaming.

`certaudit.py` counts the sweep's certificates and reconciles them against
the status array.  It does not check that any of them is TRUE.  This does.

Why it matters for the conjecture rather than only for tidiness: a
counterexample to "a uniform rank-4 OM on 9 elements with no biquadratic
final polynomial is realizable" is a class that is non-realizable and has no
BFP.  Ruling one out over the whole catalogue needs every class to be either
demonstrably realizable or to carry a BFP.  A *bogus* realization
certificate would leave a class in neither bucket -- the sweep would have
stopped looking at it, and it would never have been tested for a BFP at all.
So the realizable side is load-bearing, not just the refuted side.

Reuses `ai/omreal/checkcert.py`'s `check_record` -- stdlib only, no numpy,
its own colex order, its own cofactor determinants, no shared code with the
sweep's producer.  Streams the shards in place: no 4 GB copy.

    python verifyall.py --worker 0 --nworkers 8
    python verifyall.py --report
"""

import argparse
import glob
import json
import os
import sys
import time

sys.dont_write_bytecode = True

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
OMREAL = os.path.normpath(os.path.join(HERE, '..', 'omreal'))
CERTS = os.path.join(OMREAL, 'sweep_state', 'certs')
OUT = os.path.join(DATA, 'verifyall')

if OMREAL not in sys.path:
    sys.path.insert(0, OMREAL)
import checkcert                                            # noqa: E402


def run(worker, nworkers, kinds):
    os.makedirs(OUT, exist_ok=True)
    counts = {'REALIZABLE': 0, 'NON_REALIZABLE': 0, 'RESIDUE': 0}
    bad = []
    n = 0
    t0 = time.time()
    for p in sorted(glob.glob(os.path.join(CERTS, '*.jsonl'))):
        with open(p) as fh:
            for ln, line in enumerate(fh):
                if ln % nworkers != worker:
                    continue
                line = line.strip()
                if not line:
                    continue
                rec = json.loads(line)
                v = rec.get('verdict')
                if kinds and v not in kinds:
                    continue
                ok, msg = checkcert.check_record(rec)
                n += 1
                if not ok:
                    bad.append({'shard': os.path.basename(p), 'line': ln,
                                'verdict': v, 'why': msg,
                                'chi': rec.get('chi')})
                else:
                    counts[v] = counts.get(v, 0) + 1
                if n % 100000 == 0:
                    print('  [w%d] %d checked, %d bad, %.0f s'
                          % (worker, n, len(bad), time.time() - t0),
                          flush=True)
        print('  [w%d] finished %s: %d checked, %d bad, %.0f s'
              % (worker, os.path.basename(p), n, len(bad),
                 time.time() - t0), flush=True)
    res = {'worker': worker, 'nworkers': nworkers, 'checked': n,
           'counts': counts, 'bad': bad[:200], 'n_bad': len(bad),
           'seconds': round(time.time() - t0, 1)}
    with open(os.path.join(OUT, 'w%02d.json' % worker), 'w') as fh:
        json.dump(res, fh, indent=1)
    print('[w%d] DONE %d checked, %s, %d bad, %.0f s'
          % (worker, n, counts, len(bad), time.time() - t0), flush=True)


def report():
    tot = {'REALIZABLE': 0, 'NON_REALIZABLE': 0, 'RESIDUE': 0}
    n = nbad = 0
    ws = sorted(glob.glob(os.path.join(OUT, 'w*.json')))
    bad = []
    for p in ws:
        with open(p) as fh:
            r = json.load(fh)
        n += r['checked']
        nbad += r['n_bad']
        bad.extend(r['bad'])
        for k, v in r['counts'].items():
            tot[k] = tot.get(k, 0) + v
    print('workers reporting : %d' % len(ws))
    print('certificates checked : %d' % n)
    for k in sorted(tot):
        print('   %-16s %9d' % (k, tot[k]))
    print('REJECTED : %d' % nbad)
    for b in bad[:10]:
        print('   *** %s line %d (%s): %s'
              % (b['shard'], b['line'], b['verdict'], b['why']))
    out = {'workers': len(ws), 'checked': n, 'counts': tot, 'rejected': nbad,
           'bad': bad[:50]}
    with open(os.path.join(DATA, 'verifyall.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
    print('\n%s -> data/verifyall.json'
          % ('ALL CERTIFICATES ACCEPTED' if nbad == 0
             else '*** %d REJECTED ***' % nbad))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--worker', type=int, default=0)
    ap.add_argument('--nworkers', type=int, default=8)
    ap.add_argument('--kinds', default=None,
                    help='comma-separated verdicts to check (default all)')
    ap.add_argument('--report', action='store_true')
    a = ap.parse_args()
    if a.report:
        report()
    else:
        run(a.worker, a.nworkers,
            set(a.kinds.split(',')) if a.kinds else None)


if __name__ == '__main__':
    main()
