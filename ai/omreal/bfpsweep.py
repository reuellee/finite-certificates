#!/usr/bin/env python3
"""BFP-only sweep: how many classes of a catalogue have a biquadratic
final polynomial?

    python bfpsweep.py <r> <n> <catdir> <shard> <nshards> <out.jsonl>

Why this is the right shape for the (3,10) completeness test.  A Gordan
vector PROVES non-realizability, and a realizable class provably cannot
have one (cross-checked on 1500+ classes, 0 false hits).  So if the number
of BFP hits over a whole catalogue equals the published non-realizable
count, BFP is complete on that catalogue -- and no realization search is
needed to establish it.  That is 4x cheaper than running the full cascade.
"""
import json
import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import omdecode                                            # noqa: E402
import bfp as bfpmod                                       # noqa: E402


def main():
    r, n, catdir, shard, nsh, out = (int(sys.argv[1]), int(sys.argv[2]),
                                     sys.argv[3], int(sys.argv[4]),
                                     int(sys.argv[5]), sys.argv[6])
    lines = [ln.strip() for ln in
             open(os.path.join(catdir, 'cat_%d_%d.txt' % (r, n))) if ln.strip()]
    lines = lines[shard::nsh]
    gp = bfpmod.GPSystem(n, r)
    fh = open(out, 'w')
    hits = 0
    t0 = time.time()
    print('shard %d/%d: %d classes, %d GP relations'
          % (shard, nsh, len(lines), len(gp.rel)), flush=True)
    for i, ln in enumerate(lines):
        chi = omdecode.signs_from_string(ln)
        cert, _ = bfpmod.find_bfp(chi, gp)
        if cert is not None:
            hits += 1
            terms = []
            for (ri, big, small, w) in cert['terms']:
                L, abcd, _ = gp.rel[ri]
                terms.append({'L': list(L), 'abcd': list(abcd),
                              'big': int(big), 'small': int(small), 'w': int(w)})
            fh.write(json.dumps({'n': n, 'r': r, 'chi': ln,
                                 'verdict': 'NON_REALIZABLE',
                                 'bfp': terms}) + '\n')
            fh.flush()
        if (i + 1) % 2000 == 0:
            el = time.time() - t0
            print('  %6d/%d  bfp hits %d  %.0fs  (%.0f ms/class)'
                  % (i + 1, len(lines), hits, el, 1000 * el / (i + 1)), flush=True)
    fh.close()
    print('DONE shard %d: %d classes, %d BFP hits, %.0f s'
          % (shard, len(lines), hits, time.time() - t0), flush=True)


if __name__ == '__main__':
    main()
