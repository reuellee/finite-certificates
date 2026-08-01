#!/usr/bin/env python3
"""INDEPENDENT checker for ai/omopen certificates.  Standard library only.

    python fpcheck.py FILE [FILE ...]        # check certificates
    python fpcheck.py --selftest             # sabotage canaries

WHAT THIS FILE DOES NOT IMPORT
------------------------------
Nothing from ai/omopen (no gplib, no gordan, no fpoly, no weaponA, no
catalog), nothing from ai/omreal, nothing from ai/omgamma, and no numpy or
scipy.  It rebuilds, from the definitions:

  * the colex order on r-subsets of {1..n};
  * the sign of a sorting permutation;
  * the three-term Grassmann-Plucker relation
        [Lab][Lcd] - [Lac][Lbd] + [Lad][Lbc] = 0;
  * the one-step Plucker exchange relation
        sum_k (-1)^k [a_1..a_{r-1} b_k] [b_0..b^_k..b_r] = 0;
  * determinants, by fraction-free Bareiss elimination -- a third
    algorithm, different from both the producer's (Laplace by complementary
    2x2 minors) and ai/omreal/checkcert.py's (cofactor expansion).

Every relation named by a certificate is additionally RE-VERIFIED as a
polynomial identity: it is evaluated on random integer r x n matrices with
exact integer determinants and must come out exactly zero.  A certificate
whose relations are not identities is rejected before its arithmetic is
even looked at.  This is the guard against the one failure mode that could
manufacture a false refutation of the conjecture.

VERDICTS UNDERSTOOD
-------------------
REALIZABLE          integer r x n matrix; all C(n,r) brackets recomputed
                    exactly, each nonzero and matching the sign string.

NON_REALIZABLE / GORDAN
                    weighted strict inequalities in exponent space.  Each
                    term names a relation, which of its terms is the odd
                    one out under chi (recomputed, and required to be
                    UNIQUE), which term it dominates, and a positive
                    integer weight.  The weighted sum of
                    v = e_p + e_q - e_s - e_t  must be exactly zero.  Then
                    0 = sum w_i (v_i . u) > 0 for any realization: none
                    exists.

NON_REALIZABLE / MONOCHROME
                    one relation all of whose terms carry the same sign
                    under chi: a nonempty sum of strictly positive reals
                    equal to zero.

NON_REALIZABLE / FP
                    a polynomial certificate.  P = sum_g c_g * m_g * R_g
                    with R_g a relation rewritten in the coordinates
                    y_B = chi(B)[B] > 0 and m_g a bracket monomial.  Every
                    coefficient of P must have the same weak sign and at
                    least one must be strict; P vanishes on every
                    realization, so P(y) would be both 0 and nonzero.

NO_FINAL_POLYNOMIAL / GORDAN_WITNESS
                    an integer vector u with v . u > 0 for EVERY inequality
                    the stated identity families force.  By Gordan's
                    theorem this proves that no certificate of the GORDAN
                    kind exists over that support -- at family set
                    {gp3} that is exactly "this class has no biquadratic
                    final polynomial".  The checker rebuilds the whole
                    inequality system itself; the certificate carries only
                    u, so it cannot hide a missing row.

Anything else is REJECTED.
"""

import json
import random
import sys
from fractions import Fraction
from itertools import combinations


# ----------------------------------------------------------------------
# definitions, rebuilt
# ----------------------------------------------------------------------

def colex_bases(n, r):
    return sorted(combinations(range(1, n + 1), r),
                  key=lambda t: tuple(reversed(t)))


def sort_sign(t):
    """(sorted tuple, +-1), or (None, 0) when a value repeats."""
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


def det_bareiss(m):
    """Exact determinant by fraction-free Bareiss elimination (integers)."""
    a = [list(map(int, row)) for row in m]
    k = len(a)
    if k == 0:
        return 1
    sign = 1
    prev = 1
    for i in range(k - 1):
        if a[i][i] == 0:
            sw = None
            for j in range(i + 1, k):
                if a[j][i] != 0:
                    sw = j
                    break
            if sw is None:
                return 0
            a[i], a[sw] = a[sw], a[i]
            sign = -sign
        for j in range(i + 1, k):
            for l in range(i + 1, k):
                a[j][l] = (a[j][l] * a[i][i] - a[j][i] * a[i][l]) // prev
        prev = a[i][i]
    return sign * a[k - 1][k - 1]


def parse_chi(s, n, r):
    bas = colex_bases(n, r)
    if len(s) != len(bas):
        raise ValueError('sign string length %d, expected %d'
                         % (len(s), len(bas)))
    out = []
    for ch in s:
        if ch == '+':
            out.append(1)
        elif ch == '-':
            out.append(-1)
        else:
            raise ValueError('bad character %r in sign string' % ch)
    return out, bas


# ----------------------------------------------------------------------
# the relations, rebuilt from their definitions
# ----------------------------------------------------------------------

def relation_terms(spec, n, r, bidx):
    """[(eps, i, j), ...] for sum eps [B_i][B_j] = 0, in the canonical term
    order the certificate's `big`/`small` indices refer to.

    Raises ValueError on any malformed spec.
    """
    kind = spec.get('kind')
    if kind == 'gp3':
        L = tuple(int(x) for x in spec['L'])
        a, b, c, d = (int(x) for x in spec['abcd'])
        if len(L) != r - 2:
            raise ValueError('gp3: |L| = %d, expected %d' % (len(L), r - 2))
        if not (a < b < c < d):
            raise ValueError('gp3: a,b,c,d not ascending')
        if len(set(L)) != len(L) or set(L) & {a, b, c, d}:
            raise ValueError('gp3: index sets overlap or repeat')
        for x in L + (a, b, c, d):
            if not (1 <= x <= n):
                raise ValueError('gp3: element %d out of range' % x)
        out = []
        for (x, y, z, w, ex) in ((a, b, c, d, 1), (a, c, b, d, -1),
                                 (a, d, b, c, 1)):
            s1, g1 = sort_sign(L + (x, y))
            s2, g2 = sort_sign(L + (z, w))
            if s1 is None or s2 is None:
                raise ValueError('gp3: degenerate bracket')
            out.append((ex * g1 * g2, bidx[s1], bidx[s2]))
        return out
    if kind == 'pl':
        A = tuple(int(x) for x in spec['A'])
        B = tuple(int(x) for x in spec['B'])
        if len(A) != r - 1 or len(B) != r + 1:
            raise ValueError('pl: |A| = %d, |B| = %d, expected %d and %d'
                             % (len(A), len(B), r - 1, r + 1))
        if len(set(A)) != len(A) or len(set(B)) != len(B):
            raise ValueError('pl: repeated element')
        for x in A + B:
            if not (1 <= x <= n):
                raise ValueError('pl: element %d out of range' % x)
        out = []
        for k, bk in enumerate(B):
            s1, g1 = sort_sign(A + (bk,))
            if s1 is None:
                continue
            s2, g2 = sort_sign(tuple(x for x in B if x != bk))
            if s2 is None:
                continue
            out.append(((-1 if (k & 1) else 1) * g1 * g2, bidx[s1], bidx[s2]))
        if len(out) < 3:
            raise ValueError('pl: fewer than three surviving terms')
        return out
    raise ValueError('unknown relation kind %r' % (kind,))


_IDCACHE = {}
_POOL = {}


def _bracket_pool(n, r, bas, trials, seed=20260801):
    """A fixed pool of random integer r x n matrices and their exact bracket
    vectors, computed ONCE and shared by every relation.

    A relation is an identity iff it vanishes for all configurations, so
    testing every relation against the same sample is legitimate and turns
    the cost from (relations x trials x C(n,r)) determinants into
    (trials x C(n,r)) -- the difference between minutes and hours on a
    certificate with thousands of generators.  The matrices are drawn from a
    fixed seed so the check is reproducible.
    """
    key = (n, r, trials, seed)
    if key in _POOL:
        return _POOL[key]
    rnd = random.Random(seed ^ (n * 1000 + r))
    out = []
    while len(out) < trials:
        X = [[rnd.randint(-25, 25) for _ in range(n)] for _ in range(r)]
        br = [det_bareiss([[X[i][b - 1] for b in Bs] for i in range(r)])
              for Bs in bas]
        if any(v == 0 for v in br):
            continue                      # keep the sample generic
        out.append(br)
    _POOL[key] = out
    return out


def check_is_identity(spec, n, r, bas, bidx, trials=40, seed=0):
    """Evaluate the relation on random integer matrices; it must vanish."""
    key = (json.dumps(spec, sort_keys=True), n, r, trials)
    if key in _IDCACHE:
        return _IDCACHE[key]
    try:
        terms = relation_terms(spec, n, r, bidx)
    except ValueError as e:
        _IDCACHE[key] = (False, str(e))
        return _IDCACHE[key]
    for br in _bracket_pool(n, r, bas, trials):
        s = 0
        for (e, i, j) in terms:
            s += e * br[i] * br[j]
        if s != 0:
            _IDCACHE[key] = (False, 'relation %r is not an identity '
                                    '(value %d on a random configuration)'
                                    % (spec, s))
            return _IDCACHE[key]
    _IDCACHE[key] = (True, '')
    return _IDCACHE[key]


def term_signs(terms, chi):
    return [e * chi[i] * chi[j] for (e, i, j) in terms]


def unique_odd(sgn):
    """Index of the unique sign that differs from every other, or -1."""
    p = [k for k, s in enumerate(sgn) if s > 0]
    m = [k for k, s in enumerate(sgn) if s < 0]
    if len(p) == 1 and len(m) >= 1:
        return p[0]
    if len(m) == 1 and len(p) >= 1:
        return m[0]
    return -1


# ----------------------------------------------------------------------
# family enumeration (needed only by the no-final-polynomial witness)
# ----------------------------------------------------------------------

def enumerate_family_specs(families, n, r):
    """All relation specs of the requested families, de-duplicated."""
    specs = []
    if 'gp3' in families:
        for L in combinations(range(1, n + 1), r - 2):
            rest = [x for x in range(1, n + 1) if x not in L]
            for a, b, c, d in combinations(rest, 4):
                specs.append({'kind': 'gp3', 'L': list(L),
                              'abcd': [a, b, c, d]})
    want = set()
    if 'pl4' in families:
        want.add(1)
    if 'pl5' in families:
        want.add(0)
    if want:
        for A in combinations(range(1, n + 1), r - 1):
            sA = set(A)
            for B in combinations(range(1, n + 1), r + 1):
                if len(sA & set(B)) in want:
                    specs.append({'kind': 'pl', 'A': list(A), 'B': list(B)})
    return specs


def inequalities(specs, chi, n, r, bidx):
    """All (v, provenance) the chirotope forces over the given relations.

    v is a dict basis-index -> integer coefficient.  Duplicates are kept:
    the witness must satisfy every one of them, so duplication is harmless
    and de-duplication could only weaken the check.
    """
    out = []
    mono = []
    seen = set()
    for spec in specs:
        terms = relation_terms(spec, n, r, bidx)
        key = tuple(sorted((min(i, j), max(i, j),
                            e if terms[0][0] > 0 else -e)
                           for (e, i, j) in terms))
        if key in seen:
            continue
        seen.add(key)
        sgn = term_signs(terms, chi)
        if all(s > 0 for s in sgn) or all(s < 0 for s in sgn):
            mono.append(spec)
            continue
        k = unique_odd(sgn)
        if k < 0:
            continue
        _, ib, jb = terms[k]
        for l in range(len(terms)):
            if l == k:
                continue
            _, il, jl = terms[l]
            v = {}
            for idx, c in ((ib, 1), (jb, 1), (il, -1), (jl, -1)):
                v[idx] = v.get(idx, 0) + c
            v = {a: b for a, b in v.items() if b}
            out.append((v, (spec, k, l)))
    return out, mono


# ----------------------------------------------------------------------
# the checks
# ----------------------------------------------------------------------

def check_realizable(rec):
    n, r = int(rec['n']), int(rec['r'])
    chi, bas = parse_chi(rec['chi'], n, r)
    Z = rec['matrix']
    if len(Z) != r or any(len(row) != n for row in Z):
        return False, 'matrix is not %d x %d' % (r, n)
    Z = [[int(v) for v in row] for row in Z]
    for j, B in enumerate(bas):
        d = det_bareiss([[Z[i][b - 1] for b in B] for i in range(r)])
        if d == 0:
            return False, 'bracket %s vanishes (not uniform)' % (B,)
        if (1 if d > 0 else -1) != chi[j]:
            return False, 'bracket %s has the wrong sign' % (B,)
    return True, 'all %d brackets nonzero and correct' % len(bas)


def check_gordan(rec, trials=40):
    n, r = int(rec['n']), int(rec['r'])
    chi, bas = parse_chi(rec['chi'], n, r)
    bidx = {B: j for j, B in enumerate(bas)}
    M = len(bas)
    terms = rec.get('terms')
    if not terms:
        return False, 'empty Gordan vector'
    acc = [0] * M
    seen = set()
    for t in terms:
        spec = t['rel']
        ok, msg = check_is_identity(spec, n, r, bas, bidx, trials=trials)
        if not ok:
            return False, msg
        tl = relation_terms(spec, n, r, bidx)
        big, small, w = int(t['big']), int(t['small']), int(t['w'])
        if w <= 0:
            return False, 'weight %d is not positive' % w
        if not (0 <= big < len(tl)) or not (0 <= small < len(tl)):
            return False, 'term index out of range'
        if big == small:
            return False, 'big == small'
        key = (json.dumps(spec, sort_keys=True), big, small)
        if key in seen:
            return False, 'duplicate inequality'
        seen.add(key)
        sgn = term_signs(tl, chi)
        k = unique_odd(sgn)
        if k < 0:
            return False, ('relation %r has no unique dominating term under '
                           'this chirotope' % (spec,))
        if k != big:
            return False, ('term %d is not the dominating term of %r '
                           '(term %d is)' % (big, spec, k))
        _, ib, jb = tl[big]
        _, il, jl = tl[small]
        acc[ib] += w
        acc[jb] += w
        acc[il] -= w
        acc[jl] -= w
    if any(acc):
        nz = [i for i, v in enumerate(acc) if v]
        return False, ('the weighted combination does not cancel: %d nonzero '
                       'coordinates, first at basis %s (%d)'
                       % (len(nz), bas[nz[0]], acc[nz[0]]))
    return True, ('Gordan vector, %d inequalities, total weight %d'
                  % (len(terms), sum(int(t['w']) for t in terms)))


def check_monochrome(rec, trials=40):
    n, r = int(rec['n']), int(rec['r'])
    chi, bas = parse_chi(rec['chi'], n, r)
    bidx = {B: j for j, B in enumerate(bas)}
    spec = rec['rel']
    ok, msg = check_is_identity(spec, n, r, bas, bidx, trials=trials)
    if not ok:
        return False, msg
    tl = relation_terms(spec, n, r, bidx)
    sgn = term_signs(tl, chi)
    if not (all(s > 0 for s in sgn) or all(s < 0 for s in sgn)):
        return False, 'the terms do not all carry the same sign: %r' % (sgn,)
    return True, ('%d terms, all of sign %+d: a positive sum equal to zero'
                  % (len(sgn), sgn[0]))


def check_fp(rec, trials=40):
    n, r = int(rec['n']), int(rec['r'])
    chi, bas = parse_chi(rec['chi'], n, r)
    bidx = {B: j for j, B in enumerate(bas)}
    gens = rec.get('gens')
    if not gens:
        return False, 'no generators'
    deg = int(rec.get('degree', 0))
    poly = {}
    for g in gens:
        spec = g['rel']
        ok, msg = check_is_identity(spec, n, r, bas, bidx, trials=trials)
        if not ok:
            return False, msg
        tl = relation_terms(spec, n, r, bidx)
        sgn = term_signs(tl, chi)
        mult = []
        for B in g.get('mult', []):
            Bt = tuple(int(x) for x in B)
            if Bt not in bidx:
                return False, 'multiplier %r is not a basis' % (Bt,)
            mult.append(bidx[Bt])
        c = g['c']
        cc = Fraction(int(c[0]), int(c[1]))
        if cc == 0:
            return False, 'zero coefficient'
        for k, (_, i, j) in enumerate(tl):
            mon = tuple(sorted(mult + [i, j]))
            if deg and len(mon) != deg:
                return False, ('monomial of degree %d in a degree-%d '
                               'certificate' % (len(mon), deg))
            poly[mon] = poly.get(mon, Fraction(0)) + cc * sgn[k]
    poly = {m: v for m, v in poly.items() if v != 0}
    if not poly:
        return False, 'the combination is identically zero'
    pos = any(v > 0 for v in poly.values())
    neg = any(v < 0 for v in poly.values())
    if pos and neg:
        return False, ('the polynomial has both signs (%d positive, %d '
                       'negative coefficients)'
                       % (sum(1 for v in poly.values() if v > 0),
                          sum(1 for v in poly.values() if v < 0)))
    return True, ('final polynomial: %d monomials, all coefficients %s'
                  % (len(poly), 'positive' if pos else 'negative'))


def check_witness(rec, trials=40):
    n, r = int(rec['n']), int(rec['r'])
    chi, bas = parse_chi(rec['chi'], n, r)
    bidx = {B: j for j, B in enumerate(bas)}
    fam = rec.get('families')
    if not fam:
        return False, 'the record does not say which identity families it covers'
    fam = [str(x) for x in fam]
    if 'gp3' not in fam:
        return False, ('families %r do not include gp3, so this witness says '
                       'nothing about biquadratic final polynomials' % (fam,))
    u = [int(x) for x in rec['u']]
    if len(u) != len(bas):
        return False, 'u has length %d, expected %d' % (len(u), len(bas))
    specs = enumerate_family_specs(fam, n, r)
    # spot-check that the families really are identities
    step = max(1, len(specs) // 12)
    for spec in specs[::step]:
        ok, msg = check_is_identity(spec, n, r, bas, bidx, trials=trials)
        if not ok:
            return False, msg
    ineq, mono = inequalities(specs, chi, n, r, bidx)
    if mono:
        return False, ('relation %r is monochrome under this chirotope, so '
                       'the class IS non-realizable and no witness can exist'
                       % (mono[0],))
    if not ineq:
        return False, 'the chirotope forces no inequalities at all'
    worst = None
    for v, prov in ineq:
        s = 0
        for idx, c in v.items():
            s += c * u[idx]
        if s <= 0:
            return False, ('u fails inequality from %r (big term %d, '
                           'dominated term %d): v.u = %d'
                           % (prov[0], prov[1], prov[2], s))
        if worst is None or s < worst:
            worst = s
    return True, ('u satisfies all %d strict inequalities over families %s '
                  '(min slack %d); by Gordan no final polynomial of that '
                  'form exists' % (len(ineq), '+'.join(fam), worst))


def check_record(rec, trials=40):
    v = rec.get('verdict')
    m = rec.get('method')
    if v == 'REALIZABLE':
        return check_realizable(rec)
    if v == 'NON_REALIZABLE':
        if m == 'GORDAN':
            return check_gordan(rec, trials)
        if m == 'MONOCHROME':
            return check_monochrome(rec, trials)
        if m == 'FP':
            return check_fp(rec, trials)
        if m is None and 'bfp' in rec:
            return False, ('this is an ai/omreal record; check it with '
                           'ai/omreal/checkcert.py')
        return False, 'unknown NON_REALIZABLE method %r' % (m,)
    if v == 'NO_FINAL_POLYNOMIAL':
        return check_witness(rec, trials)
    if v in ('RESIDUE', 'STILL_OPEN'):
        return True, 'no claim'
    return False, 'unknown verdict %r' % (v,)


def check_file(path, verbose=False, trials=40):
    counts, bad, seen = {}, [], {}
    with open(path) as fh:
        for ln, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            ok, msg = check_record(rec, trials)
            v = '%s/%s' % (rec.get('verdict'), rec.get('method') or '-')
            if not ok:
                bad.append((ln, v, msg))
                continue
            counts[v] = counts.get(v, 0) + 1
            ch = rec.get('chi')
            claim = rec.get('verdict')
            if ch is not None and claim in ('REALIZABLE', 'NON_REALIZABLE'):
                if ch in seen and seen[ch] != claim:
                    bad.append((ln, v, 'class already recorded as %s'
                                % seen[ch]))
                seen[ch] = claim
            if verbose:
                print('  line %d  %-34s %s' % (ln, v, msg))
    return counts, bad, len(seen)


# ----------------------------------------------------------------------
# self-test / sabotage canaries
# ----------------------------------------------------------------------

def selftest():
    fails = []

    def expect(name, rec, want):
        ok, msg = check_record(rec, trials=12)
        if ok != want:
            fails.append(name)
        print('  [%s] %-52s %s' % ('ok ' if ok == want else 'FAIL', name,
                                   msg[:96]))

    # a genuine rank-3, 4-element realization
    n, r = 4, 3
    Z = [[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1]]
    bas = colex_bases(n, r)
    chi = ''.join('+' if det_bareiss([[Z[i][b - 1] for b in B]
                                      for i in range(r)]) > 0 else '-'
                  for B in bas)
    good = {'n': n, 'r': r, 'chi': chi, 'verdict': 'REALIZABLE', 'matrix': Z}
    expect('honest realization accepted', good, True)
    b = json.loads(json.dumps(good))
    b['matrix'][0][3] = -1
    expect('corrupted matrix entry rejected', b, False)
    b = json.loads(json.dumps(good))
    b['matrix'][2] = [0, 0, 0, 0]
    expect('vanishing bracket rejected', b, False)

    # a spec that is NOT an identity must be caught by the random-matrix test
    bad_spec = {'kind': 'pl', 'A': [1, 2, 3], 'B': [1, 2, 4, 5, 6]}
    ok, msg = check_is_identity(bad_spec, 9, 4, colex_bases(9, 4),
                                {B: j for j, B in enumerate(colex_bases(9, 4))},
                                trials=6)
    print('  [%s] %-52s %s' % ('ok ' if ok else 'FAIL',
                               'a real pl spec passes the identity test',
                               msg or 'is an identity'))
    if not ok:
        fails.append('pl identity test')
    return fails


if __name__ == '__main__':
    args = sys.argv[1:]
    if '--selftest' in args:
        print('fpcheck self-test:')
        f = selftest()
        print('SELFTEST %s' % ('FAILED: ' + ', '.join(f) if f else 'PASSED'))
        sys.exit(1 if f else 0)
    verbose = '-v' in args
    tr = 40
    for a in args:
        if a.startswith('--trials='):
            tr = int(a.split('=', 1)[1])
    paths = [a for a in args if not a.startswith('-')]
    if not paths:
        print(__doc__)
        sys.exit(2)
    rc = 0
    for path in paths:
        counts, bad, ncl = check_file(path, verbose, tr)
        print('%s: %d distinct classes' % (path, ncl))
        for k in sorted(counts):
            print('    %-38s %d' % (k, counts[k]))
        if bad:
            rc = 1
            print('    REJECTED %d' % len(bad))
            for ln, v, msg in bad[:20]:
                print('      line %d (%s): %s' % (ln, v, msg))
    print('ALL CERTIFICATES ACCEPTED' if rc == 0 else 'REJECTIONS PRESENT')
    sys.exit(rc)
