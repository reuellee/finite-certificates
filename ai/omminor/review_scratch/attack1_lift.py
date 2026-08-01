#!/usr/bin/env python3
"""Attack 1: Proposition R / the certificate lift.

A. For every (8-elt, 9-elt) pair in data/lifted_certs.jsonl verify with MY
   OWN deletion code that chi8 really is the e-deletion of chi9, and that
   the term lists are related by MY OWN relabelling.
B. Fresh end-to-end lift on 5 rows liftcert.py never touched (different
   seed, different witness element when available): my deletion, my LP, my
   lift, checked by checkcert.py.
C. My own 5 sabotages of one of my own lifted certificates -> checkcert
   must reject every one.
"""
import json
import random
import subprocess
import sys

import myom

CC = 'checkcert_copy.py'


def phi_inv(e):
    return lambda x: x if x < e else x + 1


def run_checkcert(path):
    p = subprocess.run([sys.executable, CC, path], capture_output=True, text=True)
    return p.returncode, p.stdout


# ---------------- A ----------------
pairs = []
prev = None
for line in open('../data/lifted_certs.jsonl'):
    rec = json.loads(line)
    if rec['n'] == 8:
        prev = rec
    else:
        pairs.append((prev, rec))
        prev = None
print('A: %d pairs in lifted_certs.jsonl' % len(pairs))
badA = 0
for c8, c9 in pairs:
    e = c9['lifted_from_deletion']
    if myom.deletion(c9['chi'], 9, 4, e) != c8['chi']:
        badA += 1
        print('  PAIR MISMATCH at e=%d chi9=%s...' % (e, c9['chi'][:20]))
    # and the 9-element terms must be exactly my relabelling of the 8-element ones
    f = phi_inv(e)
    lift = [{'L': [f(x) for x in t['L']], 'abcd': [f(x) for x in t['abcd']],
             'big': t['big'], 'small': t['small'], 'w': t['w']} for t in c8['bfp']]
    if lift != c9['bfp']:
        badA += 1
        print('  TERM-LIST MISMATCH at e=%d' % e)
print('A: %d defects' % badA)

# ---------------- B ----------------
rows = []
for line in open('../data/minors_sweep.jsonl'):
    r = json.loads(line)
    if r['verdict'] == 'NON_REALIZABLE' and r['del_nonreal']:
        rows.append(r)
rng = random.Random(987654321)          # NOT their seed
sel = rng.sample(rows, 5)
rels84 = myom.gp_relations(8, 4)
out = []
mine = []
for r in sel:
    e = r['del_nonreal'][-1]            # they used [0]; take the last
    delta = myom.deletion(r['chi'], 9, 4, e)
    kind, terms = myom.decide_bfp(delta, 8, 4, rels84)
    assert kind == 'GORDAN', 'claimed non-realizable deletion has NO Gordan vector!'
    assert myom.verify_gordan(delta, 8, 4, terms)
    f = phi_inv(e)
    lift = [{'L': [f(x) for x in t['L']], 'abcd': [f(x) for x in t['abcd']],
             'big': t['big'], 'small': t['small'], 'w': t['w']} for t in terms]
    out.append({'n': 8, 'r': 4, 'chi': delta, 'verdict': 'NON_REALIZABLE',
                'bfp': terms})
    out.append({'n': 9, 'r': 4, 'chi': r['chi'], 'verdict': 'NON_REALIZABLE',
                'bfp': lift, 'lifted_from_deletion': e})
    mine.append((r, e, terms, lift))
with open('my_lifted.jsonl', 'w') as fh:
    for rec in out:
        fh.write(json.dumps(rec) + '\n')
rc, so = run_checkcert('my_lifted.jsonl')
print('B: checkcert on my 5 fresh end-to-end lifts (10 records): rc=%d' % rc)
print('   ' + so.strip().replace('\n', '\n   '))

# ---------------- C ----------------
r, e, terms, lift = mine[0]
chi9 = r['chi']
sab = []
wrong = [x for x in range(1, 10) if x != e][0]
f2 = phi_inv(wrong)
sab.append({'n': 9, 'r': 4, 'chi': chi9, 'verdict': 'NON_REALIZABLE',
            'bfp': [{'L': [f2(x) for x in t['L']],
                     'abcd': [f2(x) for x in t['abcd']],
                     'big': t['big'], 'small': t['small'], 'w': t['w']}
                    for t in terms], 'sab': 'wrong element'})
b = json.loads(json.dumps(lift)); b[0]['w'] += 3
sab.append({'n': 9, 'r': 4, 'chi': chi9, 'verdict': 'NON_REALIZABLE', 'bfp': b,
            'sab': 'weight corrupted'})
b = json.loads(json.dumps(lift)); b[0]['big'], b[0]['small'] = b[0]['small'], b[0]['big']
sab.append({'n': 9, 'r': 4, 'chi': chi9, 'verdict': 'NON_REALIZABLE', 'bfp': b,
            'sab': 'big/small swapped'})
sab.append({'n': 9, 'r': 4, 'chi': chi9, 'verdict': 'NON_REALIZABLE',
            'bfp': json.loads(json.dumps(lift))[1:], 'sab': 'term dropped'})
other = next(q for q in rows if q['chi'] != chi9)
sab.append({'n': 9, 'r': 4, 'chi': other['chi'], 'verdict': 'NON_REALIZABLE',
            'bfp': lift, 'sab': 'attached to another class'})
with open('my_sabotage.jsonl', 'w') as fh:
    for rec in sab:
        fh.write(json.dumps(rec) + '\n')
rc, so = run_checkcert('my_sabotage.jsonl')
nrej = so.count('line ')
print('C: checkcert on my 5 sabotages: rc=%d (must be 1), rejected lines listed=%d (must be 5)' % (rc, nrej))
print('   ' + so.strip().replace('\n', '\n   '))
