#!/usr/bin/env python3
"""Attack 4 (+3 +5.1): the minor-minimal list, via my own code only.

A. FALSE INCLUSIONS: 10 random minimal_ext entries; all 9 deletions each,
   computed by MY deletion code; decide Gordan-vector existence by MY LP
   with exact verification.  A minimal class must have NO deletion with a
   Gordan vector (all 24 obstructions have one; BFP-existence is a class
   invariant).  Any GORDAN here = false inclusion = defect.
   Also: all 9 contractions must be valid uniform rank-3 chirotopes (my GP
   code); with (3,8) complete and all-135-realizable this settles the
   contraction side.
B. FALSE EXCLUSIONS: 5 random witnessed NR rows; the flagged deletion must
   HAVE a Gordan vector by my LP (=> genuinely non-realizable => correctly
   excluded from the minimal list).
C. PER-ELEMENT AGREEMENT: 6 witnessed + 6 unwitnessed NR rows; for each of
   their 9 deletions my LP verdict (GORDAN/FEASIBLE) must match the
   pipeline's del_nonreal element list exactly.
D. THE 24 THEMSELVES: my LP must find a Gordan vector on each of the 24
   catalog reps (checks 'all 24 carry a BFP' without their certs).
E. INVARIANCE (5.1): random G'-transforms of an obstruction rep stay
   GORDAN; random transforms of a realizable rep stay FEASIBLE.
"""
import json
import random

import myom

D = '../data/'
R = '../../omreal/'
G = '../../omgamma/data/'

rng = random.Random(1234567)
rels84 = myom.gp_relations(8, 4)

cat48 = [l.strip() for l in open(G + 'cat_4_8.txt') if l.strip()]
verd = {}
for line in open(R + 'certs_4_8.jsonl'):
    rec = json.loads(line)
    verd[rec['chi']] = rec['verdict']
nr48 = [i for i, s in enumerate(cat48) if verd[s] == 'NON_REALIZABLE']

# ---------------- A ----------------
minimal = [l.strip() for l in open(D + 'minimal_ext.txt') if l.strip()]
pick = rng.sample(minimal, 10)
gordan_hits = 0
lp_calls = 0
for kk, chi in enumerate(pick):
    for e in range(1, 10):
        dele = myom.deletion(chi, 9, 4, e)
        assert myom.gp_valid(dele, 8, 4, rels84), 'deletion not a chirotope!'
        kind, w = myom.decide_bfp(dele, 8, 4, rels84)
        lp_calls += 1
        if kind == 'GORDAN':
            gordan_hits += 1
            print('  FALSE INCLUSION: %s e=%d has a Gordan vector!' % (chi, e))
        con = myom.contraction(chi, 9, 4, e)
        assert myom.gp_valid(con, 8, 3), 'contraction not a chirotope!'
    print('A: class %d/10 done' % (kk + 1), flush=True)
print('A: %d deletions decided, GORDAN hits = %d (must be 0); all 90 '
      'contractions valid rank-3 chirotopes' % (lp_calls, gordan_hits))

# ---------------- B ----------------
rows = [json.loads(l) for l in open(D + 'minors_ext.jsonl')]
nrrows = [r for r in rows if r['verdict'] == 'NON_REALIZABLE']
witnessed = [r for r in nrrows if r['del_nonreal']]
selB = rng.sample(witnessed, 5)
okB = 0
for r in selB:
    e = rng.choice(r['del_nonreal'])
    dele = myom.deletion(r['chi'], 9, 4, e)
    kind, terms = myom.decide_bfp(dele, 8, 4, rels84)
    if kind == 'GORDAN' and myom.verify_gordan(dele, 8, 4, terms):
        okB += 1
    else:
        print('  EXCLUSION UNSUPPORTED: %s e=%d -> %s' % (r['chi'][:30], e, kind))
print('B: %d/5 flagged deletions have a verified Gordan vector' % okB)

# ---------------- C ----------------
selC = rng.sample(witnessed, 6) + rng.sample(
    [r for r in nrrows if not r['del_nonreal']], 6)
mism = 0
for r in selC:
    mine = []
    for e in range(1, 10):
        dele = myom.deletion(r['chi'], 9, 4, e)
        kind, _ = myom.decide_bfp(dele, 8, 4, rels84)
        if kind == 'GORDAN':
            mine.append(e)
    if mine != r['del_nonreal']:
        mism += 1
        print('  PER-ELEMENT MISMATCH: %s mine=%s theirs=%s'
              % (r['chi'][:30], mine, r['del_nonreal']))
print('C: per-element witness agreement on 12 NR rows (108 deletions): '
      '%d mismatches (must be 0)' % mism)

# ---------------- D ----------------
okD = 0
for i in nr48:
    kind, terms = myom.decide_bfp(cat48[i], 8, 4, rels84)
    if kind == 'GORDAN' and myom.verify_gordan(cat48[i], 8, 4, terms):
        okD += 1
print('D: %d/24 obstruction reps have a verified Gordan vector by my LP' % okD)

# ---------------- E ----------------
okE_g = okE_f = 0
rep_nr = cat48[nr48[rng.randrange(24)]]
re_r = cat48[rng.choice([i for i in range(2628) if i not in set(nr48)])]
for trial in range(3):
    perm = list(range(9))
    body = list(range(1, 9))
    rng.shuffle(body)
    perm = [0] + body
    reor = frozenset(rng.sample(range(1, 9), rng.randrange(0, 9)))
    gs = rng.choice([1, -1])
    t1 = myom.act(rep_nr, 8, 4, perm, reor, gs)
    k1, _ = myom.decide_bfp(t1, 8, 4, rels84)
    okE_g += (k1 == 'GORDAN')
    t2 = myom.act(re_r, 8, 4, perm, reor, gs)
    k2, _ = myom.decide_bfp(t2, 8, 4, rels84)
    okE_f += (k2 == 'FEASIBLE')
print('E: transformed obstruction stayed GORDAN %d/3; transformed realizable '
      'stayed FEASIBLE %d/3' % (okE_g, okE_f))
