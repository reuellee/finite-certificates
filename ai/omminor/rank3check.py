#!/usr/bin/env python3
"""The same question one rank down, where the answer is PUBLISHED.

    python rank3check.py

At rank 3 the ladder is completely known:

    (3,8)  135 classes, 0 non-realizable
    (3,9)  4382 classes, exactly 1 non-realizable  (the non-Pappus class)
    (3,10) 312 356 classes, 242 non-realizable     (FMM13 Table 1 - Table 2;
           reproduced in ai/omreal/SCOPING.md section 4.1, all 242
           certificates accepted by checkcert.py)

So the closure question -- what fraction of the non-realizable classes at
the top of the ladder have a non-realizable deletion one level down -- has a
completely determined answer at (3,10), against a one-element excluded
minor.  Measuring it is a check on the whole framework, at a rank where
nothing about the (4,9) sweep can influence the outcome, and it calibrates
how the closure fraction behaves when the (n-1)-level obstruction set is
tiny.

Contractions of a rank-3 OM on 10 elements have rank 2 on 9 elements; there
is exactly one uniform rank-2 class for each n and it is realizable, so
contractions cannot witness -- checked here as well.
"""

import collections
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import minorlib as ml                                       # noqa: E402

OUT = os.path.join(HERE, 'data')


def wilson(k, n, z=1.959963985):
    if n == 0:
        return (0.0, 1.0)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (max(0.0, c - h), min(1.0, c + h))


def main():
    # the (3,9) catalog and its single non-realizable class
    lines9, hi9, lo9, _na = ml.catalog_keys(9, 3)
    cat39 = {ml.key128(h, l): i for i, (h, l) in enumerate(zip(hi9, lo9))}
    v9 = {}
    for line in open(os.path.join(ml.OMREAL, 'certs_3_9.jsonl')):
        line = line.strip()
        if line:
            rec = json.loads(line)
            v9[rec['chi']] = rec['verdict']
    nr9 = set(i for i, s in enumerate(lines9) if v9[s] == 'NON_REALIZABLE')
    print('(3,9): %d classes, %d non-realizable (rows %s)'
          % (len(lines9), len(nr9), sorted(nr9)))
    if len(nr9) != 1:
        raise SystemExit('expected exactly one non-realizable (3,9) class')

    # the 242 non-realizable (3,10) classes
    rows = []
    for line in open(os.path.join(ml.OMREAL, 'certs_3_10_nonrealizable.jsonl')):
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    print('(3,10): %d certified non-realizable classes' % len(rows))

    # The (3,10) catalog was regenerated in a scratch copy (SCOPING.md 4.1)
    # and is not shipped, so check here that its rows really are canonical
    # keys in this convention -- otherwise "242 distinct classes" and the
    # minor-minimal count below would not be well defined.
    S10 = np.array([ml.bits_from_string(r['chi']) for r in rows], dtype=np.uint8)
    h10, l10, _n10, v10 = ml.canon_keys(10, 3, S10, batch=60)
    if not v10.all():
        raise SystemExit('a (3,10) input is not a valid chirotope')
    Dec = ml.cc().decode_keys(ml.tables(10, 3), h10, l10)
    nfix = int((Dec == S10).all(axis=1).sum())
    ndist = len(set(ml.key128(a, b) for a, b in zip(h10, l10)))
    print('  canonical fixed points: %d/%d ; distinct classes: %d'
          % (nfix, len(rows), ndist))
    if nfix != len(rows) or ndist != len(rows):
        raise SystemExit('the (3,10) inputs are not distinct canonical keys')

    M = ml.Minors(10, 3)
    S = np.array([ml.bits_from_string(r['chi']) for r in rows], dtype=np.uint8)
    D = np.ascontiguousarray(M.deletions_bits(S).reshape(len(S) * 10, -1))
    C = np.ascontiguousarray(M.contractions_bits(S).reshape(len(S) * 10, -1))
    if not ml.gp_ok(9, 3, D).all():
        raise SystemExit('G1 FAILED: a (3,10) deletion is not a chirotope')
    if not ml.gp_ok(9, 2, C).all():
        raise SystemExit('G1 FAILED: a (3,10) contraction is not a chirotope')
    print('G1 passed: all %d deletions and %d contractions valid'
          % (len(D), len(C)))

    hi, lo, _n, va = ml.canon_keys(9, 3, D, batch=400)
    cls = []
    for h, l in zip(hi, lo):
        k = cat39.get(ml.key128(h, l), -1)
        if k < 0:
            raise SystemExit('G2 FAILED: a (3,10) deletion is not in cat_3_9')
        cls.append(k)
    print('G2 passed: every deletion key is a (3,9) catalog key')
    cls = np.array(cls).reshape(len(S), 10)

    hits = [(cls[i] == list(nr9)[0]).sum() for i in range(len(S))]
    k = sum(1 for h in hits if h)
    lo_, hi_ = wilson(k, len(S))
    print('\nCLOSURE at (3,10): %d of %d non-realizable classes have the '
          'non-Pappus (3,9) class as a deletion (%.2f%%, 95%% CI [%.2f%%, '
          '%.2f%%])' % (k, len(S), 100 * k / len(S), 100 * lo_, 100 * hi_))
    print('  #non-realizable deletions histogram: %s'
          % dict(sorted(collections.Counter(int(h) for h in hits).items())))
    print('  MINOR-MINIMAL at (3,10): %d classes' % (len(S) - k))
    # Contractions land in rank 2, where there is exactly one uniform class
    # for each n (OMGAMMA.md section 5, "r = 2": one class at every n <= 9)
    # and it is realizable -- take n points on the moment curve.  So rank-2
    # contractions cannot witness, and the canonicalization is skipped: the
    # rank-2 canonicalizer costs ~66 s per chirotope because every
    # relabelling is admissible.  Three rows are done as a spot check.
    chi, clo, _cn, _cv = ml.canon_keys(9, 2, C[:3], batch=3)
    ncon = len(set(ml.key128(h, l) for h, l in zip(chi, clo)))
    print('  distinct rank-2 contraction classes in a 3-row spot check: %d '
          '(the unique uniform (2,9) class, realizable)' % ncon)

    json.dump({'n_nonrealizable_3_10': len(S), 'with_nonpappus_deletion': k,
               'minor_minimal_3_10': len(S) - k,
               'wilson95': [lo_, hi_],
               'hist': dict(sorted(collections.Counter(int(h) for h in hits).items()))},
              open(os.path.join(OUT, 'rank3check.json'), 'w'), indent=1)


if __name__ == '__main__':
    main()
