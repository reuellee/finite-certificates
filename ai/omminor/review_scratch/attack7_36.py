#!/usr/bin/env python3
"""Attack 7: the independent canonicalizer bfcanon.py and its (3,6) check.

1. MY OWN enumeration of all 2^20 sign vectors at (6,3): count the valid
   uniform chirotopes (their smoke test says 23,808).
2. MY OWN orbit count on those, by union-find over my own generator action
   (adjacent transpositions + one reorientation + global sign): published
   answer is 4.
3. Their bfcanon smoke test (copy) must print the same and exit 0.
4. Orbit-invariance attack on BF(8,4): my random G'-transforms of two (4,8)
   catalog reps (one obstruction, one realizable).  bfcanon must give the
   SAME form inside an orbit and DIFFERENT forms across the two.
"""
import random
import sys

import myom

G = '../../omgamma/data/'

# ---------- 1: enumerate ----------
n, r = 6, 3
rels = myom.gp_relations(n, r)
bas = myom.colex(n, r)
M = len(bas)
valid = []
import numpy as np
V = np.arange(1 << M, dtype=np.uint32)
chi_bits = ((V[:, None] >> np.arange(M)[None, :]) & 1).astype(np.int8)  # (2^20, 20)
chi = np.where(chi_bits == 1, 1, -1).astype(np.int8)
ok = np.ones(len(V), dtype=bool)
for (_, _, trip) in rels:
    s = [c * chi[:, p] * chi[:, q] for (p, q, c) in trip]
    bad = (s[0] == s[1]) & (s[1] == s[2])
    ok &= ~bad
nvalid = int(ok.sum())
print('1: valid uniform chirotopes at (6,3): %d  (their smoke test: 23808)' % nvalid)

# ---------- 2: orbit count by union-find with my own generators ----------
vstr = [myom.unparse(chi[i]) for i in np.flatnonzero(ok)]
index = {s: i for i, s in enumerate(vstr)}
parent = list(range(len(vstr)))


def find(x):
    while parent[x] != x:
        parent[x] = parent[parent[x]]
        x = parent[x]
    return x


def union(a, b):
    ra, rb = find(a), find(b)
    if ra != rb:
        parent[ra] = rb


gens = []
for k in range(1, n):                      # adjacent transpositions
    p = list(range(n + 1))
    p[k], p[k + 1] = p[k + 1], p[k]
    gens.append(('perm', p))
gens.append(('reor', frozenset([1])))
gens.append(('gsign', None))
for i, s in enumerate(vstr):
    for kind, g in gens:
        if kind == 'perm':
            t = myom.act(s, n, r, g)
        elif kind == 'reor':
            t = myom.act(s, n, r, None, g)
        else:
            t = myom.act(s, n, r, None, frozenset(), -1)
        union(i, index[t])
orbits = len(set(find(i) for i in range(len(vstr))))
print('2: my orbit count at (6,3): %d  (published: 4)' % orbits)

# ---------- 3: their smoke test ----------
import subprocess
p = subprocess.run([sys.executable, 'bfcanon_copy.py'], capture_output=True,
                   text=True)
print('3: bfcanon smoke test rc=%d' % p.returncode)
print('   ' + p.stdout.strip().replace('\n', '\n   '))

# ---------- 4: BF(8,4) invariance under my own transforms ----------
sys.path.insert(0, '.')
import bfcanon_copy as bfc
rng = random.Random(24680)
cat48 = [l.strip() for l in open(G + 'cat_4_8.txt') if l.strip()]
import json
verd = {}
for line in open('../../omreal/certs_4_8.jsonl'):
    rec = json.loads(line)
    verd[rec['chi']] = rec['verdict']
nrs = [s for s in cat48 if verd[s] == 'NON_REALIZABLE']
res = [s for s in cat48 if verd[s] == 'REALIZABLE']
rep_a = rng.choice(nrs)
rep_b = rng.choice(res)
bf = bfc.BF(8, 4)
print('4: building transforms...')
forms_a, forms_b = [], []
for t in range(2):
    body = list(range(1, 9))
    rng.shuffle(body)
    perm = [0] + body
    reor = frozenset(rng.sample(range(1, 9), rng.randrange(0, 9)))
    gs = rng.choice([1, -1])
    ta = myom.act(rep_a, 8, 4, perm, reor, gs)
    tb = myom.act(rep_b, 8, 4, perm, reor, gs)
    forms_a.append(bf.form(bfc.bits_from_string(ta)))
    forms_b.append(bf.form(bfc.bits_from_string(tb)))
fa0 = bf.form(bfc.bits_from_string(rep_a))
fb0 = bf.form(bfc.bits_from_string(rep_b))
same_a = all(f == fa0 for f in forms_a)
same_b = all(f == fb0 for f in forms_b)
print('4: obstruction rep: transforms give same brute-force form: %s' % same_a)
print('4: realizable rep:  transforms give same brute-force form: %s' % same_b)
print('4: the two reps get different forms: %s' % (fa0 != fb0))
