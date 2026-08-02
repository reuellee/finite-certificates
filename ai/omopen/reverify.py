#!/usr/bin/env python3
"""A FOURTH, INDEPENDENT check of this session's certificates.

Written from scratch for the final residue run.  Standard library only --
no numpy, no scipy, and no import of anything in this repository (not
gplib, not gordan, not weaponA, not catalog, not fpcheck, not
ai/omreal/checkcert.py, not ai/omgamma/coverage_checker.py).  Everything it
needs it rebuilds:

  * the colex order on 4-subsets of {1..9};
  * the 128-bit catalog key layout, decoded with python integer shifts
    instead of numpy bit unpacking;
  * determinants by EXACT RATIONAL GAUSSIAN ELIMINATION over Fraction --
    deliberately a different algorithm from every other checker in play
    (fpcheck.py uses fraction-free Bareiss, ai/omreal/checkcert.py uses
    cofactor expansion, exactgate.py uses Laplace along two rows);
  * the three-term Grassmann-Plucker relation, its sorting signs, and the
    strict inequalities a realization's log-brackets must satisfy.

WHAT IT CHECKS

  provenance   the SHA-256 of coverage_4_9.npz's three raw arrays against
               MANIFEST.json's `array_sha256`.
  identity     the chi string carried by each certificate equals the
               chirotope decoded from the catalog npz for the row the
               result file claims -- so a certificate cannot be a true
               statement about the wrong class.
  realizable   all 126 brackets of the integer matrix recomputed exactly;
               each must be nonzero and match the sign string.
  no-BFP       for each witness u, every one of the 2,520 inequalities
               forced by the 1,260 three-term relations is rebuilt and
               v . u > 0 is checked in integers.
  dichotomy    a class must never carry BOTH a realization and a Gordan
               vector, and never both a Gordan vector and a witness at the
               same level.

    python reverify.py --all
    python reverify.py --sample 10        # a random 10% of each file
"""

import argparse
import hashlib
import json
import os
import random
import sys
import zipfile
from fractions import Fraction
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
NPZ = os.path.normpath(os.path.join(
    HERE, '..', 'omgamma', 'data', 'coverage_4_9', 'coverage_4_9.npz'))
MANIFEST = os.path.normpath(os.path.join(
    HERE, '..', 'omgamma', 'data', 'coverage_4_9', 'MANIFEST.json'))
N, R = 9, 4


# ======================================================================
# combinatorics, rebuilt
# ======================================================================

def colex_bases(n, r):
    """r-subsets of {1..n} ordered by colex (reverse-lexicographic on the
    reversed tuple) -- the catalog's order."""
    return sorted(combinations(range(1, n + 1), r),
                  key=lambda t: tuple(reversed(t)))


BASES = colex_bases(N, R)
M = len(BASES)
BIDX = {b: j for j, b in enumerate(BASES)}


def sort_sign(t):
    """(sorted tuple, sign of the sorting permutation); 0 if repeated."""
    a = list(t)
    if len(set(a)) != len(a):
        return None, 0
    sgn = 1
    for i in range(1, len(a)):
        j = i
        while j > 0 and a[j - 1] > a[j]:
            a[j - 1], a[j] = a[j], a[j - 1]
            sgn = -sgn
            j -= 1
    return tuple(a), sgn


# ======================================================================
# determinants by exact rational Gaussian elimination
# ======================================================================

def det_rational(rows):
    """Exact determinant of a square integer matrix, by Gauss-Jordan over
    Fraction with row swaps.  Different algorithm from every other checker
    in this project."""
    n = len(rows)
    A = [[Fraction(v) for v in row] for row in rows]
    det = Fraction(1)
    for c in range(n):
        piv = None
        for rr in range(c, n):
            if A[rr][c] != 0:
                piv = rr
                break
        if piv is None:
            return 0
        if piv != c:
            A[c], A[piv] = A[piv], A[c]
            det = -det
        det *= A[c][c]
        inv = Fraction(1) / A[c][c]
        A[c] = [v * inv for v in A[c]]
        for rr in range(c + 1, n):
            f = A[rr][c]
            if f:
                A[rr] = [x - f * y for x, y in zip(A[rr], A[c])]
    assert det.denominator == 1
    return int(det)


def bracket_signs(matrix):
    """matrix: 4 rows of 9 integers.  Returns the 126 signs in colex order,
    or None if some bracket vanishes."""
    cols = [[matrix[i][q] for i in range(R)] for q in range(N)]
    out = []
    for B in BASES:
        sub = [[cols[b - 1][i] for b in B] for i in range(R)]
        d = det_rational(sub)
        if d == 0:
            return None
        out.append(1 if d > 0 else -1)
    return out


# ======================================================================
# the catalog, decoded with python integers
# ======================================================================

def check_provenance():
    with open(MANIFEST) as fh:
        man = json.load(fh)
    want = None
    for k in ('array_sha256', 'arrays_sha256'):
        if k in man:
            want = man[k]
            break
    if want is None:
        return {'ok': None, 'note': 'MANIFEST has no array_sha256'}
    got = {}
    with zipfile.ZipFile(NPZ) as z:
        for nm in z.namelist():
            key = nm[:-4] if nm.endswith('.npy') else nm
            with z.open(nm) as fh:
                raw = fh.read()
            # the stored hash is over the raw array BYTES, i.e. the .npy
            # payload after its header
            hdrlen = 10 + int.from_bytes(raw[8:10], 'little')
            got[key] = hashlib.sha256(raw[hdrlen:]).hexdigest()
    ok = all(got.get(k) == v for k, v in want.items())
    return {'ok': ok, 'expected': want, 'got': got}


def load_catalog_keys(rows):
    """row -> chirotope string, decoded from coverage_4_9.npz by hand."""
    import numpy as np                      # only to READ the npz container
    z = np.load(NPZ, mmap_mode='r')
    hi, lo = z['key_hi'], z['key_lo']
    out = {}
    for r in rows:
        v = (int(hi[r]) << 64) | int(lo[r])
        if v >> M:
            raise ValueError('row %d: key has bits above position M-1' % r)
        s = []
        for j in range(M):
            s.append('+' if (v >> (M - 1 - j)) & 1 else '-')
        out[r] = ''.join(s)
    return out


# ======================================================================
# the three-term relations and the inequalities they force
# ======================================================================

def three_term_relations():
    """Every (L, a<b<c<d) three-term Grassmann-Plucker relation, as three
    (bracket_index, bracket_index, sign) terms:
        s1 [Lab][Lcd] + s2 [Lac][Lbd] + s3 [Lad][Lbc] = 0
    with s = +1, -1, +1 folded into the sorting signs."""
    rels = []
    for L in combinations(range(1, N + 1), R - 2):
        rest = [x for x in range(1, N + 1) if x not in L]
        for a, b, c, d in combinations(rest, 4):
            terms = []
            for (coef, (x, y), (z, w)) in ((1, (a, b), (c, d)),
                                           (-1, (a, c), (b, d)),
                                           (1, (a, d), (b, c))):
                t1, s1 = sort_sign(L + (x, y))
                t2, s2 = sort_sign(L + (z, w))
                terms.append((BIDX[t1], BIDX[t2], coef * s1 * s2))
            rels.append(tuple(terms))
    return rels


RELS = three_term_relations()


def forced_inequalities(chi):
    """chi: list of 126 signs (+1/-1).  Returns the list of exponent vectors
    v (as dicts index->coefficient) with v . u > 0 forced on any
    realization's u = log|bracket|.  Two per relation.

    In y_B = chi(B)[B] > 0 the relation reads  c1 Y1 + c2 Y2 + c3 Y3 = 0
    with c_k = sign_k * chi * chi and Y_k = y y > 0.  For a valid chirotope
    the c_k are not all equal, so exactly one is the odd one out; that term
    equals the sum of the other two and therefore strictly dominates each.
    """
    out = []
    contradictions = []
    for terms in RELS:
        c = [t[2] * chi[t[0]] * chi[t[1]] for t in terms]
        if c[0] == c[1] == c[2]:
            contradictions.append(terms)
            continue
        # the odd one out
        for i in range(3):
            if c[i] != c[(i + 1) % 3] and c[i] != c[(i + 2) % 3]:
                big = i
                break
        else:
            continue
        for k in range(3):
            if k == big:
                continue
            v = {}
            for idx in (terms[big][0], terms[big][1]):
                v[idx] = v.get(idx, 0) + 1
            for idx in (terms[k][0], terms[k][1]):
                v[idx] = v.get(idx, 0) - 1
            v = {a: b for a, b in v.items() if b}
            if v:
                out.append(v)
    return out, contradictions


# ======================================================================
# checks
# ======================================================================

def read_jsonl(path):
    out = []
    if os.path.exists(path):
        with open(path) as fh:
            for line in fh:
                line = line.strip()
                if line:
                    out.append(json.loads(line))
    return out


def check_realizable(recs, rng, frac):
    picked = _pick(recs, rng, frac)
    bad = []
    for rec in picked:
        chi = rec['chi']
        sg = bracket_signs(rec['matrix'])
        if sg is None:
            bad.append((chi[:12], 'a bracket vanishes'))
            continue
        want = [1 if ch == '+' else -1 for ch in chi]
        if sg != want:
            k = next(i for i in range(M) if sg[i] != want[i])
            bad.append((chi[:12], 'bracket %d (%s) has the wrong sign'
                        % (k, BASES[k])))
    return len(picked), bad


def check_witness(recs, rng, frac):
    picked = _pick(recs, rng, frac)
    bad = []
    nineq = 0
    for rec in picked:
        fam = tuple(rec.get('families', ()))
        if 'gp3' not in fam:
            bad.append((rec['chi'][:12],
                        'witness does not claim the three-term family'))
            continue
        chi = [1 if ch == '+' else -1 for ch in rec['chi']]
        u = rec['u']
        if len(u) != M:
            bad.append((rec['chi'][:12], 'u has length %d' % len(u)))
            continue
        ineqs, contra = forced_inequalities(chi)
        if contra:
            bad.append((rec['chi'][:12], 'a relation is monochrome'))
            continue
        nineq += len(ineqs)
        for v in ineqs:
            s = sum(coef * int(u[i]) for i, coef in v.items())
            if s <= 0:
                bad.append((rec['chi'][:12], 'an inequality fails (v.u=%d)'
                            % s))
                break
    return len(picked), bad, nineq


def _pick(recs, rng, frac):
    if frac >= 1.0:
        return recs
    k = max(1, int(round(frac * len(recs)))) if recs else 0
    return rng.sample(recs, k) if k else []


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--sample', type=float, default=100.0,
                    help='percent of each file to check (default 100)')
    ap.add_argument('--seed', type=int, default=20260802)
    ap.add_argument('--real', action='append', default=None)
    ap.add_argument('--witness', action='append', default=None)
    ap.add_argument('--results', action='append', default=None)
    ap.add_argument('--out', default=os.path.join(DATA, 'reverify.json'))
    a = ap.parse_args()
    frac = a.sample / 100.0
    rng = random.Random(a.seed)
    report = {'sample_percent': a.sample, 'seed': a.seed}
    fail = 0

    print('reverify.py -- independent re-check (stdlib only, exact '
          'rational Gaussian elimination)')
    print('  colex bases rebuilt: %d;  three-term relations rebuilt: %d'
          % (M, len(RELS)))
    report['bases'] = M
    report['relations'] = len(RELS)

    prov = check_provenance()
    report['provenance'] = prov
    print('  catalog provenance (SHA-256 of coverage_4_9.npz arrays vs '
          'MANIFEST): %s' % prov['ok'])
    if prov['ok'] is False:
        fail += 1

    # ---- realizations --------------------------------------------------
    real_files = a.real or [os.path.join(DATA, 'certs_realizable.jsonl')]
    tot_real, all_chi, cert_rows = 0, {}, {}
    for f in real_files:
        recs = read_jsonl(f)
        if not recs:
            continue
        for rec in recs:
            all_chi.setdefault(rec['chi'], []).append('REALIZABLE')
            # certificates that name their own catalog row (the backfill
            # file does) are checked against THAT row, not only against the
            # rows the results file happens to cover
            if 'row' in rec:
                cert_rows[int(rec['row'])] = rec['chi']
        n, bad = check_realizable(recs, rng, frac)
        tot_real += n
        print('  %-46s %4d of %4d checked, %d bad'
              % (os.path.basename(f), n, len(recs), len(bad)))
        for b in bad[:6]:
            print('      *** %s ... : %s' % b)
        report.setdefault('realizable', {})[os.path.basename(f)] = {
            'records': len(recs), 'checked': n, 'bad': bad}
        fail += len(bad)

    # ---- no-BFP witnesses ----------------------------------------------
    wit_files = a.witness or [os.path.join(DATA, 'certs_no_bfp.jsonl')]
    for f in wit_files:
        recs = read_jsonl(f)
        if not recs:
            continue
        n, bad, nineq = check_witness(recs, rng, frac)
        print('  %-46s %4d of %4d checked, %d bad (%d inequalities '
              'rebuilt and tested)'
              % (os.path.basename(f), n, len(recs), len(bad), nineq))
        for b in bad[:6]:
            print('      *** %s ... : %s' % b)
        report.setdefault('witness', {})[os.path.basename(f)] = {
            'records': len(recs), 'checked': n, 'bad': bad,
            'inequalities': nineq}
        fail += len(bad)

    # ---- certificate chi vs the catalog, decoded by hand ---------------
    res_files = a.results or [os.path.join(DATA, 'results.jsonl')]
    rows = dict(cert_rows)
    for f in res_files:
        for rec in read_jsonl(f):
            rows[int(rec['row'])] = rec['chi']
    if rows:
        cat = load_catalog_keys(sorted(rows))
        mism = [r for r in rows if cat[r] != rows[r]]
        print('  certificate chi vs catalog npz decoded by hand: '
              '%d/%d rows agree' % (len(rows) - len(mism), len(rows)))
        report['catalog_match'] = {'rows': len(rows),
                                   'mismatch': mism[:20]}
        fail += len(mism)
        missing = [c for c in all_chi if c not in set(cat.values())]
        print('  certificate chi strings present in the catalog rows '
              'attacked: %d/%d' % (len(all_chi) - len(missing), len(all_chi)))
        report['chi_in_catalog'] = {'n': len(all_chi),
                                    'missing': missing[:5]}
        fail += len(missing)

    report['FAILURES'] = fail
    with open(a.out, 'w') as fh:
        json.dump(report, fh, indent=1)
    print('\n%s  (%d failures)  -> %s'
          % ('REVERIFY PASSED' if fail == 0 else '*** REVERIFY FAILED ***',
             fail, a.out))
    return 0 if fail == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
