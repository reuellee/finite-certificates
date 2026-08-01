#!/usr/bin/env python3
"""Shard runner for spot_sweep.sh -- the piece the launcher calls.

    python3 ops/run_shards.py --job omreal-residue --lo 0 --hi 300 \
            --workers $(nproc) --state /opt/state --out gs://bucket/job

Contract with spot_sweep.sh
---------------------------
* Shards [lo, hi) are INDEPENDENT units of work.  A shard is complete when
  its marker file exists in --state; on restart, complete shards are
  skipped.  That is the whole preemption story: a spot VM that dies mid
  shard loses at most that shard.
* Results and state are both mirrored to --out (a gs:// prefix) as each
  shard finishes, so a preemption in the final minute cannot lose the run
  and `spot_sweep.sh collect` works whether or not the VM still exists.
* Exit code 0 means "every shard in range is complete".

The actual work is `ai/omreal/ladder.py`: harvest a shard of sampled (4,9)
classes with stages A+B, then run the effort ladder on whatever neither
stage settled.  Both phases live in one shard so a shard needs nothing
from any other shard -- there is no canonicalisation and no shared state
anywhere in this pipeline, which is what makes it embarrassingly parallel.

Runs identically on a laptop (--out a local directory) and on the VM.
"""

import argparse
import json
import os
import subprocess
import sys
import time
from concurrent.futures import ProcessPoolExecutor, as_completed

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OMREAL = os.path.join(ROOT, 'ai', 'omreal')


def _sync(src, dst):
    """Mirror a directory to gs:// (or a local path) if possible."""
    if not dst:
        return
    if dst.startswith('gs://'):
        for tool in (['gsutil', '-q', '-m', 'rsync', '-r', src, dst],
                     ['gcloud', 'storage', 'rsync', '-r', src, dst]):
            try:
                subprocess.run(tool, check=True,
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            except (OSError, subprocess.CalledProcessError):
                continue
        print('[run_shards] WARNING: could not sync to %s' % dst, flush=True)
    else:
        os.makedirs(dst, exist_ok=True)
        for f in os.listdir(src):
            s, d = os.path.join(src, f), os.path.join(dst, f)
            if os.path.isfile(s) and (not os.path.exists(d)
                                      or os.path.getmtime(s) > os.path.getmtime(d)):
                with open(s, 'rb') as a, open(d, 'wb') as b:
                    b.write(a.read())


def run_one(args):
    shard, nsh, keys, state, py = args
    env = dict(os.environ)
    env.update(OMP_NUM_THREADS='1', MKL_NUM_THREADS='1',
               OPENBLAS_NUM_THREADS='1', NUMEXPR_NUM_THREADS='1')
    hv = os.path.join(state, 'harvest_%05d.jsonl' % shard)
    ld = os.path.join(state, 'ladder_%05d.jsonl' % shard)
    ce = os.path.join(state, 'certs_%05d.jsonl' % shard)
    done = os.path.join(state, 'done_%05d' % shard)
    if os.path.exists(done):
        return shard, 0.0, 'skipped'
    t0 = time.time()
    lad = os.path.join(OMREAL, 'ladder.py')
    r = subprocess.run([py, lad, 'harvest', '--keys', keys,
                        '--shard', str(shard), str(nsh), '--out', hv,
                        '--resume'], env=env, capture_output=True, text=True)
    if r.returncode != 0:
        return shard, time.time() - t0, 'HARVEST FAILED: ' + r.stderr[-400:]
    r = subprocess.run([py, lad, 'ladder', '--harvest', hv,
                        '--out', ld, '--certs', ce, '--resume'],
                       env=env, capture_output=True, text=True)
    if r.returncode != 0:
        return shard, time.time() - t0, 'LADDER FAILED: ' + r.stderr[-400:]
    # Self-verify on the spot: every certificate this shard produced is
    # re-checked by checkcert.py (standard library only, shares no code with
    # the producer) BEFORE the shard is marked complete.  A shard that emits
    # a bad certificate fails here instead of landing silently in the
    # results -- and this is what lets the bulky harvest files stay in the
    # bucket rather than being downloaded just to be re-checked.
    chk = os.path.join(OMREAL, 'checkcert.py')
    v = subprocess.run([py, chk, hv, ce], env=env, capture_output=True, text=True)
    counts = {'REALIZABLE': 0, 'NON_REALIZABLE': 0, 'RESIDUE': 0}
    for line in v.stdout.splitlines():
        for k in counts:
            if line.strip().startswith(k):
                counts[k] += int(line.split()[-1])
    passed = v.returncode == 0 and 'ALL CERTIFICATES ACCEPTED' in v.stdout
    total = solved = 0
    for line in open(ld):
        total += 1
        if '"solved_at": null' not in line:
            solved += 1
    json.dump({'shard': shard, 'seconds': round(time.time() - t0, 1),
               'harvest': counts, 'ladder_total': total,
               'ladder_solved': solved, 'checkcert_passed': passed,
               'checkcert_tail': '' if passed else v.stdout[-400:]},
              open(os.path.join(state, 'summary_%05d.json' % shard), 'w'))
    if not passed:
        return shard, time.time() - t0, 'CHECKCERT REJECTED: ' + v.stdout[-300:]
    open(done, 'w').write('%.1f\n' % (time.time() - t0))
    return shard, time.time() - t0, 'ok'


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--job', required=True)
    ap.add_argument('--lo', type=int, required=True)
    ap.add_argument('--hi', type=int, required=True)
    ap.add_argument('--nshards', type=int, default=0,
                    help='total shard count the key file is split into '
                         '(default: --hi)')
    ap.add_argument('--workers', type=int, default=4)
    ap.add_argument('--state', required=True)
    ap.add_argument('--out', default='')
    ap.add_argument('--keys', default='')
    ap.add_argument('--python', default=sys.executable)
    a = ap.parse_args()

    os.makedirs(a.state, exist_ok=True)
    keys = a.keys or os.path.join(a.state, 'keys.npz')
    if not os.path.exists(keys):
        cand = os.path.join(OMREAL, 'keys.npz')
        if os.path.exists(cand):
            keys = cand
        else:
            raise SystemExit('key file not found: %s' % keys)
    nsh = a.nshards or a.hi
    todo = [(s, nsh, keys, a.state, a.python) for s in range(a.lo, a.hi)]
    print('[run_shards] job=%s shards %d..%d of %d, %d workers, keys=%s'
          % (a.job, a.lo, a.hi, nsh, a.workers, keys), flush=True)
    t0 = time.time()
    ok = fail = 0
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        futs = {ex.submit(run_one, t): t[0] for t in todo}
        for i, f in enumerate(as_completed(futs), 1):
            shard, dt, msg = f.result()
            if msg.startswith('ok') or msg == 'skipped':
                ok += 1
            else:
                fail += 1
                print('[run_shards] shard %d: %s' % (shard, msg), flush=True)
            print('[run_shards] %d/%d done (shard %d, %.0f s, %s) elapsed %.0f s'
                  % (i, len(todo), shard, dt, msg[:40], time.time() - t0), flush=True)
            if i % 5 == 0:
                _sync(a.state, a.out)
    _sync(a.state, a.out)
    print('[run_shards] complete: %d ok, %d failed, %.0f s'
          % (ok, fail, time.time() - t0), flush=True)
    return 0 if fail == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
