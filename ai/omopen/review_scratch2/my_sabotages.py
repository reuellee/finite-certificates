#!/usr/bin/env python3
"""REVIEW (Fable): three fresh sabotages of my own design, fed to BOTH
shipped checkers.  Each corruption is first PROVEN corrupting with my own
determinant code (the builder documented that a small nudge can fail to
corrupt), then both checkers must reject it.

  S1  one matrix entry corrupted (delta grown until MY recompute shows the
      chirotope changed) -- certificate keeps the original chi.
  S2  the chi string relabelled by a permutation of the 9 elements; the
      matrix left alone.
  S3  two certificates' payloads swapped: chi of cert A with matrix of
      cert B.
  S4  (bonus) a witness record with u rotated by one position.
Controls: the uncorrupted records must be accepted.
"""
import json
import os
import subprocess
import sys
from itertools import combinations, permutations

HERE = os.path.dirname(os.path.abspath(__file__))
OMOPEN = os.path.dirname(HERE)
AI = os.path.dirname(OMOPEN)
DATA = os.path.join(OMOPEN, 'data')
N, R = 9, 4

BASES = sorted(combinations(range(1, N + 1), R), key=lambda t: t[::-1])
PERMS4 = [(p, (1 if sum(1 for i in range(4) for j in range(i + 1, 4)
                        if p[i] > p[j]) % 2 == 0 else -1))
          for p in permutations(range(4))]


def det4(cols):
    t = 0
    for p, s in PERMS4:
        t += s * cols[0][p[0]] * cols[1][p[1]] * cols[2][p[2]] * cols[3][p[3]]
    return t


def chi_of_matrix(M):
    cols = [[M[i][j] for i in range(4)] for j in range(9)]
    out = []
    for B in BASES:
        d = det4([cols[b - 1] for b in B])
        if d == 0:
            return None
        out.append('+' if d > 0 else '-')
    return ''.join(out)


certs = [json.loads(l) for l in open(os.path.join(DATA,
                                                  'certs_realizable.jsonl'))]
wit = [json.loads(l) for l in open(os.path.join(DATA, 'certs_no_bfp.jsonl'))]

A = json.loads(json.dumps(certs[0]))
B = json.loads(json.dumps(certs[1]))
assert A['chi'] != B['chi']

# --- S1: grow a corruption until MY code confirms the chirotope changed ---
S1 = json.loads(json.dumps(A))
delta = 1
corrupted = False
base = int(S1['matrix'][0][0])
while delta < (1 << 40):
    S1['matrix'][0][0] = base + delta
    s = chi_of_matrix(S1['matrix'])
    if s is None or s != A['chi']:
        corrupted = True
        break
    delta *= 2
assert corrupted, 'could not corrupt?'
print('S1: entry (0,0) %d -> %d; my recompute confirms the chirotope %s'
      % (base, base + delta,
         'changed' if s else 'degenerated (a bracket vanished)'))

# --- S2: relabel the chi, not the matrix ---
perm = [2, 3, 4, 5, 6, 7, 8, 9, 1]          # element e -> perm[e-1]
old = {B_: j for j, B_ in enumerate(BASES)}
S2 = json.loads(json.dumps(A))
newchi = [None] * 126
for j, B_ in enumerate(BASES):
    img = tuple(sorted(perm[b - 1] for b in B_))
    # forget the sorting sign on purpose: this is the classic half-applied
    # relabelling bug
    newchi[old[img]] = A['chi'][j]
S2['chi'] = ''.join(newchi)
assert chi_of_matrix(S2['matrix']) != S2['chi']
print('S2: chi relabelled by a 9-cycle, matrix untouched; my recompute '
      'confirms the mismatch')

# --- S3: swapped payloads ---
S3 = {'n': 9, 'r': 4, 'chi': A['chi'], 'verdict': 'REALIZABLE',
      'matrix': B['matrix']}
assert chi_of_matrix(S3['matrix']) != S3['chi']
print('S3: chi of cert A with matrix of cert B; mismatch confirmed')

# --- S4: witness u rotated ---
w = json.loads(json.dumps(wit[0]))
w['u'] = w['u'][1:] + w['u'][:1]
S4 = w

controls = [A, B]
sab = [S1, S2, S3]

fp_file = os.path.join(HERE, '_sab_fp.jsonl')
with open(fp_file, 'w') as fh:
    for r in controls:
        fh.write(json.dumps(r) + '\n')
    for r in sab + [S4]:
        fh.write(json.dumps(r) + '\n')
cc_file = os.path.join(HERE, '_sab_cc.jsonl')
with open(cc_file, 'w') as fh:
    for r in controls + sab:
        fh.write(json.dumps(r) + '\n')

env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
print('\n--- fpcheck.py on 2 controls + 4 sabotages (expect: accept 2, '
      'reject 4) ---')
p = subprocess.run([sys.executable, os.path.join(OMOPEN, 'fpcheck.py'),
                    '--trials=12', '-v', fp_file],
                   capture_output=True, text=True, env=env)
print(p.stdout)
print('\n--- checkcert.py on 2 controls + 3 sabotages (expect: accept 2, '
      'reject 3) ---')
p2 = subprocess.run([sys.executable,
                     os.path.join(AI, 'omreal', 'checkcert.py'), '-v',
                     cc_file],
                    capture_output=True, text=True, env=env)
print(p2.stdout)
