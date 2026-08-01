#!/usr/bin/env python3
"""Attack 3 + leftovers: Lemma C/D against real realization matrices, the
canonical fixed-point property of the catalogs, and the canonical-rep
property of the harvest chi strings."""
import json
import sys
from fractions import Fraction

import myom

sys.path.insert(0, '..')
import minorlib as ml                                        # their decoder, deliberately

# ---------- 1: Lemma D and Lemma C on real certified realizations ----------
recs = []
for line in open('../data/harvest_sweep.jsonl'):
    r = json.loads(line)
    if r['verdict'] == 'REALIZABLE' and 'matrix' in r:
        recs.append(r)
    if len(recs) >= 3:
        break
print('Lemma D/C test on %d certified realizable (4,9) records:' % len(recs))
for r in recs:
    Z = r['matrix']
    assert myom.chi_of_matrix(Z, 9, 4) == r['chi'], 'matrix does not realize chi!'
    for e in (2, 5, 9):
        # D: delete column e
        Zd = [[row[j] for j in range(9) if j != e - 1] for row in Z]
        assert myom.deletion(r['chi'], 9, 4, e) == myom.chi_of_matrix(Zd, 8, 4)
        # C, quotient form: project x_i (i != e) along x_e onto a coordinate
        # complement, in exact rationals; signs must equal chi/e up to ONE
        # global sign
        xe = [Fraction(Z[i][e - 1]) for i in range(4)]
        p = next(i for i in range(4) if xe[i] != 0)
        keep = [i for i in range(4) if i != p]
        cols = [j for j in range(9) if j != e - 1]
        P = []
        for i in keep:
            row = []
            for j in cols:
                v = Fraction(Z[i][j]) - xe[i] * Fraction(Z[p][j]) / xe[p]
                row.append(v)
            P.append(row)
        con = []
        for B in myom.colex(8, 3):
            sub = [[P[i][b - 1] for b in B] for i in range(3)]
            d = myom.det(sub)
            assert d != 0
            con.append(1 if d > 0 else -1)
        mycon = myom.parse(myom.contraction(r['chi'], 9, 4, e))
        same = all(a == b for a, b in zip(con, mycon))
        opp = all(a == -b for a, b in zip(con, mycon))
        assert same or opp, 'quotient projection does not match contraction!'
print('  all deletion columns and quotient projections agree (up to one '
      'global sign for contractions) -- Lemmas D and C verified on data')

# ---------- 2: catalog fixed-point property, re-asserted ----------
for (nn, rr) in ((8, 4), (8, 3)):
    lines, hi, lo, na = ml.catalog_keys(nn, rr)   # raises if any rep is not a fixed point
    print('catalog cat_%d_%d: %d rows, every row is its own canonical key' %
          (rr, nn, len(lines)))

# ---------- 3: harvest chi strings are canonical (4,9) keys ----------
import numpy as np
chis = []
for line in open('../data/harvest_sweep.jsonl'):
    chis.append(json.loads(line)['chi'])
    if len(chis) >= 25:
        break
S = np.array([ml.bits_from_string(c) for c in chis], dtype=np.uint8)
hi, lo, _na, va = ml.canon_keys(9, 4, S, batch=25)
D = ml.cc().decode_keys(ml.tables(9, 4), hi, lo)
print('harvest chi fixed-point check: %d/25 valid, %d/25 decode back to '
      'themselves' % (int(va.sum()), int((D == S).all(axis=1).sum())))
