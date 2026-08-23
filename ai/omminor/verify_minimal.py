#!/usr/bin/env python3
"""Falsification test for the MINOR-MINIMAL list, bypassing canonicalization.

    python verify_minimal.py --workers 2

A class is put on the minor-minimal list because all nine of its deletions
were IDENTIFIED, by canonicalization against the (4,8) catalog, as
realizable classes.  That identification is the one step in the pipeline
whose failure would silently inflate the list: if a deletion were really one
of the 24 but were assigned to a realizable catalog row, the class would be
called minor-minimal when it is not.

This script tests that claim without using canonicalization at all.  For
every deletion of every minor-minimal class it runs the biquadratic
final-polynomial search directly.  A realizable oriented matroid provably
has NO Gordan vector (the strict inequalities are satisfied by the logs of
its brackets), so:

    a single Gordan vector found here falsifies the minimal list.

Conversely a class that is one of the 24 always has one, since all 24 are
BFP-certified in `ai/omreal/certs_4_8.jsonl` and BFP-existence is a
G'-class invariant (MINOR_THEORY.md section 5.1).  So the test is sharp in
both directions: 0 hits confirms the list, >=1 hit refutes it and names the
offender.

Deduplication is by LABELED sign string, which can only save work.
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
sys.path.insert(0, ml.OMREAL)

OUT = os.path.join(HERE, 'data')


def _job(blob):
    import bfp as bfpmod
    S = np.frombuffer(blob, dtype=np.uint8).reshape(-1, 70)
    gp = bfpmod.GPSystem(8, 4)
    hits = []
    for i in range(len(S)):
        chi = np.where(S[i] == 1, np.int8(1), np.int8(-1))
        cert, _ = bfpmod.find_bfp(chi, gp)
        if cert is not None:
            hits.append((i, len(cert['terms'])))
    return len(S), hits


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--minimal', default=os.path.join(OUT, 'minimal_sweep.txt'))
    ap.add_argument('--workers', type=int, default=2)
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--positive-control', type=int, default=25,
                    help='also run on this many deletions KNOWN to be one of '
                         'the 24; every one must produce a Gordan vector')
    ap.add_argument('--report',
                    help='optional JSON report path; verification is read-only by default')
    a = ap.parse_args()

    keys = [l.strip() for l in open(a.minimal) if l.strip()]
    if a.limit:
        keys = keys[:a.limit]
    print('%d minor-minimal classes -> %d deletions' % (len(keys), 9 * len(keys)))
    M = ml.Minors(9, 4)
    S = np.array([ml.bits_from_string(k) for k in keys], dtype=np.uint8)
    D = np.ascontiguousarray(M.deletions_bits(S).reshape(-1, 70))
    if not ml.gp_ok(8, 4, D).all():
        raise SystemExit('a deletion of a minimal class is not a chirotope')

    seen = {}
    for i in range(len(D)):
        seen.setdefault(D[i].tobytes(), []).append(i)
    uniq = list(seen.keys())
    print('%d distinct labeled deletions' % len(uniq))
    U = np.frombuffer(b''.join(uniq), dtype=np.uint8).reshape(len(uniq), 70)

    blocks = [U[i:i + 200].tobytes() for i in range(0, len(U), 200)]
    t0 = time.time()
    done = 0
    allhits = []
    if a.workers > 1:
        from concurrent.futures import ProcessPoolExecutor
        with ProcessPoolExecutor(max_workers=a.workers) as ex:
            for k, (n, hits) in enumerate(ex.map(_job, blocks)):
                done += n
                allhits.extend((k * 200 + i, t) for i, t in hits)
                if k % 5 == 0:
                    print('  %d/%d  %.0f ms each  hits so far %d'
                          % (done, len(U), 1000 * (time.time() - t0) / max(done, 1),
                             len(allhits)), flush=True)
    else:
        for k, b in enumerate(blocks):
            n, hits = _job(b)
            done += n
            allhits.extend((k * 200 + i, t) for i, t in hits)
    el = time.time() - t0
    print('\n%d distinct deletions tested in %.0f s (%.0f ms each)'
          % (done, el, 1000 * el / max(done, 1)))
    print('GORDAN VECTORS FOUND: %d' % len(allhits))
    for j, t in allhits[:20]:
        owners = seen[uniq[j]]
        print('  FALSIFIED: deletion %d (of class %s, element %d) has a %d-term '
              'Gordan vector' % (j, keys[owners[0] // 9], owners[0] % 9 + 1, t))

    # positive control: deletions that ARE one of the 24 must give a vector.
    # Needs minors_sweep.jsonl, a large regenerable artifact that is
    # deliberately gitignored (see the artifact table in MINOR_THEORY.md);
    # skip cleanly rather than crash when it hasn't been regenerated.
    pos_ok = pos_n = 0
    minors_path = os.path.join(OUT, 'minors_sweep.jsonl')
    if a.positive_control and not os.path.exists(minors_path):
        print('positive control: SKIPPED (minors_sweep.jsonl not present — '
              'regenerable, gitignored; run the omminor pipeline to produce '
              'it locally). The falsification test above is unaffected.')
    elif a.positive_control:
        import bfp as bfpmod
        gp = bfpmod.GPSystem(8, 4)
        rows = []
        for line in open(minors_path):
            r = json.loads(line)
            if r['verdict'] == 'NON_REALIZABLE' and r['del_nonreal']:
                rows.append(r)
            if len(rows) >= a.positive_control:
                break
        for r in rows:
            Sx = ml.bits_from_string(r['chi'])[None, :]
            Dx = M.deletions_bits(Sx)[0]
            e = r['del_nonreal'][0]
            chi = np.where(Dx[e - 1] == 1, np.int8(1), np.int8(-1))
            cert, _ = bfpmod.find_bfp(chi, gp)
            pos_n += 1
            pos_ok += cert is not None
        print('positive control: %d/%d deletions known to be one of the 24 '
              'produced a Gordan vector' % (pos_ok, pos_n))

    res = {'source': os.path.basename(a.minimal),
           'minimal_classes': len(keys), 'deletions': 9 * len(keys),
           'distinct_deletions': len(U), 'gordan_vectors_found': len(allhits),
           'positive_control': [pos_ok, pos_n], 'wall_s': el}
    if a.report:
        with open(a.report, 'w') as output:
            json.dump(res, output, indent=1)
        print('wrote %s' % a.report)
    ok = len(allhits) == 0 and pos_ok == pos_n
    print('\n%s' % ('MINIMAL LIST CONFIRMED (no deletion of any minor-minimal '
                    'class has a biquadratic final polynomial)' if ok
                    else 'FALSIFIED'))
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
