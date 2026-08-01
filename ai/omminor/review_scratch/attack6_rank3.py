#!/usr/bin/env python3
"""Attack 6: independent FULL recomputation of the (3,10) closure fraction.

Their pipeline: canonicalize all 2420 deletions of the 242 certified
non-realizable (3,10) classes and look up the (3,9) catalog -> 183 classes
have the unique non-realizable (3,9) class as a deletion, 59 minor-minimal.

My route (no canonicalization, no shared code): a (3,9) deletion is the
unique non-realizable class IFF it has a Gordan vector [(3,9) catalog is
complete (omgamma / published 4382); 4381 classes carry checkcert-verified
realization matrices (=> no Gordan vector); the one non-realizable class
carries a checkcert-verified Gordan vector and BFP-existence is a class
invariant].  So decide each deletion by my exact LP and count.
"""
import json
import time
from collections import Counter

import myom

R = '../../omreal/'

rows = [json.loads(l) for l in open(R + 'certs_3_10_nonrealizable.jsonl')]
assert len(rows) == 242
chis = [r['chi'] for r in rows]
assert len(set(chis)) == 242

rels93 = myom.gp_relations(9, 3)
print('%d GP relations at (9,3)' % len(rels93))

# dedupe identical labelled deletions
dels = {}
for i, chi in enumerate(chis):
    for e in range(1, 11):
        d = myom.deletion(chi, 10, 3, e)
        dels.setdefault(d, []).append((i, e))
print('%d deletions, %d distinct labelled strings' % (10 * 242, len(dels)))

t0 = time.time()
verdict = {}
ng = nf = 0
for k, d in enumerate(dels):
    assert myom.gp_valid(d, 9, 3, rels93)
    kind, w = myom.decide_bfp(d, 9, 3, rels93)
    verdict[d] = kind
    if kind == 'GORDAN':
        ng += 1
    else:
        nf += 1
    if (k + 1) % 200 == 0:
        print('  %d/%d  (%.0f ms each)  GORDAN so far %d'
              % (k + 1, len(dels), 1000 * (time.time() - t0) / (k + 1), ng),
              flush=True)
print('LPs done in %.0f s: %d GORDAN, %d FEASIBLE (both sides exactly '
      'verified)' % (time.time() - t0, ng, nf))

hits = [0] * 242
for d, owners in dels.items():
    if verdict[d] == 'GORDAN':
        for (i, e) in owners:
            hits[i] += 1
withdel = sum(1 for h in hits if h)
hist = Counter(hits)
print('\nCLOSURE at (3,10), computed by me: %d of 242 (%.2f%%)'
      % (withdel, 100 * withdel / 242))
print('minor-minimal: %d' % (242 - withdel))
print('hist:', dict(sorted(hist.items())))
print('their claim: 183 of 242 (75.62%), 59 minor-minimal, hist {0:59, 1:155, 2:28}')
