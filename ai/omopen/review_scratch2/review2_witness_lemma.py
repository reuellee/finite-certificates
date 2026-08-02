#!/usr/bin/env python3
"""REVIEW (Fable): independent verification of the inequality machinery.

Shares no code with the deliverable.  My own identity families are built
from the definitions, validated as exact polynomial identities on random
integer configurations, and then used to:

  W1  re-verify every one of the 252 NO_FINAL_POLYNOMIAL witnesses: rebuild
      the full inequality system for the record's stated families under its
      chi and demand v.u > 0 (exact ints) for every row.  Also demand no
      monochrome relation exists (else the witness would be meaningless).
  W2  verify the s0 Lemma exactly on real data: for every one of the 126
      certificate matrices, compute the exact integer brackets, and check
      that for every forced inequality the dominating product strictly
      exceeds the dominated product IN THE INTEGERS:
          |det P||det Q| > |det S||det T|.
      This is u = log|brackets| satisfying V u > 0, verified without logs.
  W3  every identity evaluates to exactly 0 on every certificate matrix
      (validates both my table and the realizations one more way).
  W4  count L0 rows (must be 2520 for every class) and the L1 row /
      distinct-exponent-vector ranges, against OPEN_ATTACK.md s7.1a.
  W5  the degree-2-over-gp3 incidence fact behind s5.2: each unordered
      bracket-pair monomial of a three-term relation determines the
      relation; count 3780 distinct monomials over 1260 relations, none
      shared.
"""
import json
import os
import random
import sys
from itertools import combinations, permutations

HERE = os.path.dirname(os.path.abspath(__file__))
OMOPEN = os.path.dirname(HERE)
DATA = os.path.join(OMOPEN, 'data')
N, R = 9, 4

fails = []


def ck(name, ok, detail=''):
    print('  [%s] %s %s' % ('ok ' if ok else 'FAIL', name, detail))
    if not ok:
        fails.append((name, detail))


BASES = sorted(combinations(range(1, N + 1), R), key=lambda t: t[::-1])
BIDX = {B: j for j, B in enumerate(BASES)}
M = len(BASES)

PERMS = [(p, (1 if sum(1 for i in range(4) for j in range(i + 1, 4)
                       if p[i] > p[j]) % 2 == 0 else -1))
         for p in permutations(range(4))]


def det4(cols):
    t = 0
    for p, s in PERMS:
        t += s * cols[0][p[0]] * cols[1][p[1]] * cols[2][p[2]] * cols[3][p[3]]
    return t


def perm_sign_and_sort(t):
    a = list(t)
    sg = 1
    for i in range(1, len(a)):
        j = i
        while j > 0 and a[j - 1] > a[j]:
            a[j - 1], a[j] = a[j], a[j - 1]
            sg = -sg
            j -= 1
    for i in range(1, len(a)):
        if a[i - 1] == a[i]:
            return None, 0
    return tuple(a), sg


# ---------------------------------------------------------------------
# my identity families
# ---------------------------------------------------------------------

def build_gp3():
    out = []
    for L in combinations(range(1, N + 1), R - 2):
        rest = [x for x in range(1, N + 1) if x not in L]
        for a, b, c, d in combinations(rest, 4):
            terms = []
            for (x, y, z, w, ex) in ((a, b, c, d, 1), (a, c, b, d, -1),
                                     (a, d, b, c, 1)):
                s1, g1 = perm_sign_and_sort(L + (x, y))
                s2, g2 = perm_sign_and_sort(L + (z, w))
                terms.append((ex * g1 * g2, BIDX[s1], BIDX[s2]))
            out.append(('gp3', terms))
    return out


def build_pl(inter_sizes):
    out = []
    seen = set()
    for A in combinations(range(1, N + 1), R - 1):
        sA = set(A)
        for B in combinations(range(1, N + 1), R + 1):
            if len(sA & set(B)) not in inter_sizes:
                continue
            terms = []
            for k, bk in enumerate(B):
                s1, g1 = perm_sign_and_sort(A + (bk,))
                if s1 is None:
                    continue
                s2, g2 = perm_sign_and_sort(tuple(x for x in B if x != bk))
                if s2 is None:
                    continue
                terms.append(((-1 if (k & 1) else 1) * g1 * g2,
                              BIDX[s1], BIDX[s2]))
            if len(terms) < 3:
                continue
            key = tuple(sorted((min(i, j), max(i, j), e) for (e, i, j)
                               in terms))
            if key[0][2] < 0:
                key = tuple((i, j, -e) for (i, j, e) in key)
            if key in seen:
                continue
            seen.add(key)
            out.append(('pl%d' % len(terms), terms))
    return out


GP3 = build_gp3()
PL45 = build_pl({0, 1})
ck('identity counts: gp3 1260, pl4 3780, pl5 504',
   len(GP3) == 1260 and
   sum(1 for k, _ in PL45 if k == 'pl4') == 3780 and
   sum(1 for k, _ in PL45 if k == 'pl5') == 504,
   'gp3 %d, pl4 %d, pl5 %d' % (len(GP3),
                               sum(1 for k, _ in PL45 if k == 'pl4'),
                               sum(1 for k, _ in PL45 if k == 'pl5')))
ALL = GP3 + PL45

# validate MY table on random integer configurations
rnd = random.Random(424242)
bad = 0
for trial in range(25):
    X = [[rnd.randint(-30, 30) for _ in range(N)] for _ in range(R)]
    cols = [[X[i][j] for i in range(R)] for j in range(N)]
    br = [det4([cols[b - 1] for b in Bs]) for Bs in BASES]
    if any(v == 0 for v in br):
        continue
    for kind, terms in ALL:
        s = 0
        for (e, i, j) in terms:
            s += e * br[i] * br[j]
        if s != 0:
            bad += 1
ck('my identity table: exact zero on 25 random integer configs', bad == 0,
   '%d failures' % bad)


def system_rows(idents, chi):
    """[(big_i, big_j, small_i, small_j)] forced by chi; also monochrome
    detection.  chi: list of +-1."""
    rows = []
    mono = 0
    for kind, terms in idents:
        sgn = [e * chi[i] * chi[j] for (e, i, j) in terms]
        pos = [k for k, s in enumerate(sgn) if s > 0]
        neg = [k for k, s in enumerate(sgn) if s < 0]
        if not pos or not neg:
            mono += 1
            continue
        if len(pos) == 1:
            big = pos[0]
        elif len(neg) == 1:
            big = neg[0]
        else:
            continue
        _, ib, jb = terms[big]
        for l in range(len(terms)):
            if l == big:
                continue
            _, il, jl = terms[l]
            rows.append((ib, jb, il, jl))
    return rows, mono


def chi_list(s):
    return [1 if ch == '+' else -1 for ch in s]


# ---------------------------------------------------------------------
# W1: the 252 witnesses
# ---------------------------------------------------------------------
wit = [json.loads(l) for l in open(os.path.join(DATA, 'certs_no_bfp.jsonl'))]
fam_map = {('gp3',): GP3, ('gp3', 'pl4', 'pl5'): ALL}
badw = 0
monos = 0
l0_rows = set()
l1_rows = []
l1_distinct = []
for w in wit:
    chi = chi_list(w['chi'])
    idents = fam_map[tuple(w['families'])]
    rows, mono = system_rows(idents, chi)
    if mono:
        monos += 1
    u = [int(x) for x in w['u']]
    ok = len(u) == M
    for (ib, jb, il, jl) in rows:
        if u[ib] + u[jb] - u[il] - u[jl] <= 0:
            ok = False
            break
    if not ok:
        badw += 1
        print('    W1 FAILURE on chi %s... families %s'
              % (w['chi'][:20], w['families']))
    if tuple(w['families']) == ('gp3',):
        l0_rows.add(len(rows))
    else:
        l1_rows.append(len(rows))
        l1_distinct.append(len({(ib, jb, il, jl) if (ib, jb) <= (il, jl)
                                else (ib, jb, il, jl)
                                for (ib, jb, il, jl) in
                                [(min(a, b), max(a, b), min(c, d), max(c, d))
                                 for (a, b, c, d) in rows]}))
ck('W1: all 252 witnesses satisfy every forced inequality (exact ints)',
   badw == 0, '%d failures' % badw)
ck('W1b: no monochrome relation on any of the 126 classes', monos == 0)
ck('W4: L0 row count is 2520 for every class', l0_rows == {2520},
   str(sorted(l0_rows)))
print('      L1 rows range [%d, %d] (doc, on 6 classes: 8172-8644); '
      'distinct [%d, %d] (doc: 7082-7476)'
      % (min(l1_rows), max(l1_rows), min(l1_distinct), max(l1_distinct)))

# ---------------------------------------------------------------------
# W2/W3: the Lemma, on the actual certificates
# ---------------------------------------------------------------------
certs = [json.loads(l) for l in open(os.path.join(DATA,
                                                  'certs_realizable.jsonl'))]
bad2 = bad3 = 0
for c in certs:
    Mx = c['matrix']
    cols = [[int(Mx[i][j]) for i in range(R)] for j in range(N)]
    br = [det4([cols[b - 1] for b in Bs]) for Bs in BASES]
    assert all(v != 0 for v in br)
    chi = chi_list(c['chi'])
    y = [abs(v) for v in br]
    # W3: identities vanish on the realization
    for kind, terms in ALL:
        s = 0
        for (e, i, j) in terms:
            s += e * br[i] * br[j]
        if s != 0:
            bad3 += 1
            break
    # W2: every forced inequality holds in the integers
    rows, mono = system_rows(ALL, chi)
    if mono:
        bad2 += 1
        continue
    for (ib, jb, il, jl) in rows:
        if not (y[ib] * y[jb] > y[il] * y[jl]):
            bad2 += 1
            print('    W2 FAILURE chi %s...' % c['chi'][:20])
            break
ck('W3: all 5544 identities vanish exactly on every certificate matrix',
   bad3 == 0, '%d failures' % bad3)
ck('W2: Lemma verified -- |det P||det Q| > |det S||det T| for every forced '
   'inequality (L1 support), on all 126 realizations', bad2 == 0,
   '%d failures' % bad2)

# ---------------------------------------------------------------------
# W5: the degree-2 / L0 incidence fact
# ---------------------------------------------------------------------
mon_owner = {}
shared = 0
nmon = 0
for q, (kind, terms) in enumerate(GP3):
    for (e, i, j) in terms:
        mon = (min(i, j), max(i, j))
        if mon in mon_owner and mon_owner[mon] != q:
            shared += 1
        mon_owner[mon] = q
nmon = len(mon_owner)
ck('W5: 3780 distinct pair-monomials over the 1260 gp3 relations, none '
   'shared between relations', nmon == 3780 and shared == 0,
   'monomials %d shared %d' % (nmon, shared))

print()
if fails:
    print('WITNESS/LEMMA VERIFICATION: %d FAILURES' % len(fails))
    sys.exit(1)
print('WITNESS/LEMMA VERIFICATION: ALL CHECKS PASSED')
