#!/usr/bin/env python3
"""Certify realizability of the 11 uniform rank-4 classes on 7 elements.

    python cert47.py

The classification statement in MINOR_THEORY.md is about rank 4 on n <= 9.
For the 24 non-realizable (4,8) classes to be MINOR-MINIMAL they need every
proper minor realizable: their nine... eight deletions land in (4,7) and
their eight contractions in (3,7).  (3,7) is covered by (3,8) -- every
(3,7) class is a deletion of a (3,8) class, all 135 of which are certified
realizable -- so the missing piece is (4,7), 11 classes.

The certificates are written in the schema `ai/omreal/checkcert.py` accepts
and are meant to be checked with it.
"""

import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import minorlib as ml                                       # noqa: E402
sys.path.insert(0, ml.OMREAL)


CELLS = [(4, 5), (4, 6), (4, 7), (3, 7)]


def certify(r, n):
    import realize as rz
    lines = [ln.strip() for ln in open(os.path.join(ml.DATA, 'cat_%d_%d.txt' % (r, n)))
             if ln.strip()]
    geom = rz.Geom(n, r)
    out = os.path.join(HERE, 'data', 'certs_%d_%d.jsonl' % (r, n))
    nok = 0
    with open(out, 'w') as fh:
        for i, s in enumerate(lines):
            chi = ml.signs_from_string(s)
            Z, _ = rz.realize(chi, geom, tries=8, sweeps=50, seed=i)
            if Z is None:
                print('  class %d UNREALIZED' % i)
                continue
            chk = rz.exact_bracket_signs(Z, geom)
            if chk is None or not np.array_equal(chk, chi):
                raise SystemExit('class %d: matrix does not realize it' % i)
            nok += 1
            fh.write(json.dumps({'n': n, 'r': r, 'chi': s,
                                 'verdict': 'REALIZABLE',
                                 'matrix': [[int(v) for v in row] for row in Z]}) + '\n')
    print('cat_%d_%d: %d/%d realized -> %s' % (r, n, nok, len(lines), out))
    return nok == len(lines)


def main():
    ok = True
    for r, n in CELLS:
        ok = certify(r, n) and ok
    return 0 if ok else 1


if __name__ == '__main__':
    sys.exit(main())
