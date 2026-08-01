#!/usr/bin/env python3
"""Identify every single-element minor of a corpus of (4,9) classes.

    python minorsweep.py --in data/harvest_sweep.jsonl --tag sweep --workers 2
    python minorsweep.py --in data/harvest_sweep.jsonl --tag sweep --extend

For each input class chi (a canonical (4,9) key as a 126-character sign
string) this computes

  * the 9 deletions chi\\e  -- uniform rank-4 chirotopes on 8 elements -- and
    identifies each against the 2628-class (4,8) catalog;
  * the 9 contractions chi/e -- uniform rank-3 chirotopes on 8 elements --
    and identifies each against the 135-class (3,8) catalog.

Both catalogs carry a certified realizability verdict from ai/omreal
(`certs_4_8.jsonl`: 2604 REALIZABLE + 24 NON_REALIZABLE; `certs_3_8.jsonl`:
all 135 REALIZABLE), so the output says, per class, exactly which
single-element minors are non-realizable.

THREE GLOBAL CHECKS, asserted on every row (not sampled):
  G1  every deletion and every contraction is a VALID uniform chirotope
      (all 3-term Grassmann-Plucker conditions).  An index-table error
      would break this immediately and almost everywhere.
  G2  every canonical key produced lands IN the corresponding catalog.
      The catalogs are complete (2628 and 135 are the published counts,
      reproduced by omgamma), so a canonicalization that were not an orbit
      invariant would fall outside them constantly.
  G3  no REALIZABLE input class has a non-realizable minor (Lemma D/C).
      Violation means the pipeline, one of the certificates, or the lemma
      is wrong.  Feed the run a corpus containing REALIZABLE rows.

IDENTIFICATION CACHE.  Canonicalizing an (8,4) chirotope costs 1-40 ms
depending on how far the colour refinement splits its ground set, and the
same labeled 8-element chirotope shows up as a deletion of many different
9-element classes.  `data/idcache_4_8.npz` / `idcache_3_8.npz` memoise
labeled sign string -> catalog row, so `--extend` only pays for genuinely
new strings.  The cache is keyed by the LABELED string, so it can only ever
save work, never change an answer.

Resumable: `--extend` continues from the number of input lines already
consumed, so re-running after the sweep has grown extends the measurement.
"""

import argparse
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import minorlib as ml                                       # noqa: E402

OUT = os.path.join(HERE, 'data')
N, R = 9, 4

_G = {}


def load_catalogs():
    if 'cat48' in _G:
        return _G
    lines8, hi8, lo8, na8 = ml.catalog_keys(8, 4)
    lines3, hi3, lo3, na3 = ml.catalog_keys(8, 3)
    _G['cat48'] = {ml.key128(h, l): i for i, (h, l) in enumerate(zip(hi8, lo8))}
    _G['cat38'] = {ml.key128(h, l): i for i, (h, l) in enumerate(zip(hi3, lo3))}
    _G['lines8'], _G['lines3'] = lines8, lines3
    _G['na8'], _G['na3'] = na8, na3

    def verdicts(path, lines):
        v = {}
        for line in open(path):
            line = line.strip()
            if line:
                rec = json.loads(line)
                v[rec['chi']] = rec['verdict']
        return set(i for i, s in enumerate(lines) if v[s] == 'NON_REALIZABLE')

    _G['nr48'] = verdicts(os.path.join(ml.OMREAL, 'certs_4_8.jsonl'), lines8)
    _G['nr38'] = verdicts(os.path.join(ml.OMREAL, 'certs_3_8.jsonl'), lines3)
    if len(_G['nr48']) != 24:
        raise SystemExit('expected 24 non-realizable (4,8) classes, got %d'
                         % len(_G['nr48']))
    if len(_G['nr38']) != 0:
        raise SystemExit('expected 0 non-realizable (3,8) classes, got %d'
                         % len(_G['nr38']))
    return _G


# ----------------------------------------------------------------------
# worker: canonical keys of a block of distinct labeled strings
# ----------------------------------------------------------------------

def _keys_job(job):
    n, r, blob, m = job
    S = np.frombuffer(blob, dtype=np.uint8).reshape(-1, m)
    hi, lo, _na, va = ml.canon_keys(n, r, S, batch=400)
    if not va.all():
        raise SystemExit('G1 FAILED (canon): invalid chirotope in a (%d,%d) '
                         'minor block' % (r, n))
    return hi, lo


def identify(n, r, S, cachepath, workers, catmap, label):
    """S: (K, M) uint8 sign bits -> (K,) int32 catalog rows.  Memoised."""
    M = S.shape[1]
    cache = {}
    if os.path.exists(cachepath):
        z = np.load(cachepath)
        keys, vals = z['keys'], z['vals']
        for b, v in zip(keys, vals):
            cache[b.tobytes()] = int(v)
    hits = 0
    need = {}
    order = np.empty(len(S), dtype=np.int32)
    for i in range(len(S)):
        b = S[i].tobytes()
        got = cache.get(b)
        if got is not None:
            order[i] = got
            hits += 1
        else:
            order[i] = -1
            need.setdefault(b, []).append(i)
    print('  %s: %d minors, %d cached, %d distinct new'
          % (label, len(S), hits, len(need)), flush=True)
    if need:
        newb = list(need.keys())
        NS = np.frombuffer(b''.join(newb), dtype=np.uint8).reshape(len(newb), M)
        blocks = [NS[a:a + 400] for a in range(0, len(NS), 400)]
        jobs = [(n, r, bl.tobytes(), M) for bl in blocks]
        res = []
        t0 = time.time()
        if workers > 1:
            from concurrent.futures import ProcessPoolExecutor
            with ProcessPoolExecutor(max_workers=workers) as ex:
                for k, out in enumerate(ex.map(_keys_job, jobs)):
                    res.append(out)
                    if k % 5 == 0:
                        done = sum(len(h) for h, _ in res)
                        print('    canon %d/%d  %.1f ms each'
                              % (done, len(NS), 1000 * (time.time() - t0) / max(done, 1)),
                              flush=True)
        else:
            for k, j in enumerate(jobs):
                res.append(_keys_job(j))
                if k % 5 == 0:
                    done = sum(len(h) for h, _ in res)
                    print('    canon %d/%d  %.1f ms each'
                          % (done, len(NS), 1000 * (time.time() - t0) / max(done, 1)),
                          flush=True)
        hi = np.concatenate([h for h, _ in res])
        lo = np.concatenate([l for _, l in res])
        for j, b in enumerate(newb):
            k = catmap.get(ml.key128(hi[j], lo[j]), -1)
            if k < 0:
                raise SystemExit('G2 FAILED: a (%d,%d) minor canonicalises to '
                                 'a key outside the catalog' % (r, n))
            cache[b] = k
            for i in need[b]:
                order[i] = k
        # persist
        kb = list(cache.keys())
        keys = np.frombuffer(b''.join(kb), dtype=np.uint8).reshape(len(kb), M)
        vals = np.array([cache[b] for b in kb], dtype=np.int32)
        np.savez_compressed(cachepath, keys=keys, vals=vals)
    if (order < 0).any():
        raise SystemExit('internal: unresolved minor')
    return order


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--in', dest='inp', required=True)
    ap.add_argument('--tag', required=True)
    ap.add_argument('--extend', action='store_true')
    ap.add_argument('--workers', type=int, default=1)
    ap.add_argument('--limit', type=int, default=0)
    a = ap.parse_args()

    os.makedirs(OUT, exist_ok=True)
    statep = os.path.join(OUT, 'minors_%s.state.json' % a.tag)
    outp = os.path.join(OUT, 'minors_%s.jsonl' % a.tag)
    st = {'consumed': 0, 'src': os.path.abspath(a.inp)}
    if a.extend and os.path.exists(statep):
        st = json.load(open(statep))

    rows = []
    with open(a.inp) as fh:
        for i, line in enumerate(fh):
            line = line.strip()
            if not line or i < st['consumed']:
                continue
            rec = json.loads(line)
            rows.append((rec['chi'], rec['verdict']))
            if a.limit and len(rows) >= a.limit:
                break
    print('%d new rows (already consumed %d)' % (len(rows), st['consumed']))
    if not rows:
        return

    g = load_catalogs()
    Mi = ml.Minors(N, R)
    t0 = time.time()
    S = np.array([ml.bits_from_string(c) for c, _ in rows], dtype=np.uint8)
    B = len(S)
    D = np.ascontiguousarray(Mi.deletions_bits(S).reshape(B * N, -1))
    C = np.ascontiguousarray(Mi.contractions_bits(S).reshape(B * N, -1))
    del S

    # G1 -- validity of every minor, vectorised, no sampling
    if not ml.gp_ok(8, 4, D).all():
        raise SystemExit('G1 FAILED: a deletion is not a valid chirotope')
    if not ml.gp_ok(8, 3, C).all():
        raise SystemExit('G1 FAILED: a contraction is not a valid chirotope')
    print('G1 passed: all %d deletions and %d contractions are valid uniform '
          'chirotopes' % (len(D), len(C)), flush=True)

    dk = identify(8, 4, D, os.path.join(OUT, 'idcache_4_8.npz'), a.workers,
                  g['cat48'], 'deletions  (8,4)').reshape(B, N)
    del D
    ck = identify(8, 3, C, os.path.join(OUT, 'idcache_3_8.npz'), a.workers,
                  g['cat38'], 'contractions (8,3)').reshape(B, N)
    del C
    print('G2 passed: every minor key is a catalog key', flush=True)

    nr48, nr38 = g['nr48'], g['nr38']
    nviol = 0
    with open(outp, 'a' if a.extend else 'w') as fh:
        for b in range(B):
            chi, verdict = rows[b]
            dn = [e + 1 for e in range(N) if int(dk[b, e]) in nr48]
            cn = [e + 1 for e in range(N) if int(ck[b, e]) in nr38]
            if verdict == 'REALIZABLE' and (dn or cn):
                nviol += 1
                print('G3 VIOLATION: realizable %s has non-realizable minors '
                      'del=%s con=%s' % (chi, dn, cn))
            fh.write(json.dumps({'chi': chi, 'verdict': verdict,
                                 'del_cls': [int(x) for x in dk[b]],
                                 'con_cls': [int(x) for x in ck[b]],
                                 'del_nonreal': dn, 'con_nonreal': cn}) + '\n')
    if nviol:
        raise SystemExit('G3 FAILED on %d rows' % nviol)
    nreal = sum(1 for _, v in rows if v == 'REALIZABLE')
    print('G3 passed: none of the %d REALIZABLE rows in this batch has a '
          'non-realizable minor' % nreal)

    st['consumed'] += B
    st['wall_s'] = st.get('wall_s', 0.0) + (time.time() - t0)
    st['when'] = time.strftime('%Y-%m-%dT%H:%M:%S')
    json.dump(st, open(statep, 'w'), indent=1)
    print('wrote %s (%d rows consumed in total, %.1f s)'
          % (outp, st['consumed'], time.time() - t0))


if __name__ == '__main__':
    main()
