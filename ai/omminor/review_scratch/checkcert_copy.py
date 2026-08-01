#!/usr/bin/env python3
"""INDEPENDENT checker for ai/omreal certificates.  Standard library only.

    python checkcert.py certs.jsonl [certs2.jsonl ...]
    python checkcert.py --selftest

This file imports NOTHING from this project and nothing from ai/omgamma --
no numpy, no scipy, no `omdecode`, no `realize`, no `bfp`.  It rederives
the colex basis order, the three-term Grassmann-Plucker relations and the
determinant signs from their definitions, with a different determinant
algorithm (plain cofactor expansion on Python ints) from the one the
producer uses (Laplace expansion by complementary 2x2 minors, int64).

WHAT IS CHECKED
---------------
REALIZABLE      the record carries an integer r x n matrix Z.  All C(n,r)
                brackets det Z_B are computed exactly; every one must be
                nonzero (uniformity) and its sign must equal the class's
                sign string, position by position, in colex order.

NON_REALIZABLE  the record carries a list of weighted inequalities, each
                naming a GP relation (L; a,b,c,d), which of its three
                terms is the BIG one and which is the SMALL one, and a
                positive integer weight.  For each, the checker recomputes
                the three signed term-signs from the class's own sign
                string and demands that BIG really is the odd one out (so
                |big| = |t1| + |t2| > |small| strictly for ANY realization)
                and that small != big.  It then forms
                    v = e_p + e_q - e_s - e_t   in Z^M
                and requires   sum_i w_i v_i = 0   with every w_i > 0 and
                at least one term.  That is a Gordan vector, and it makes
                the strict system unsatisfiable, so no realization exists.

RESIDUE         carries no claim; counted, never accepted as a verdict.

Anything else -- a wrong sign, a vanishing bracket, a zero or negative
weight, an empty term list, a "big" that is not the odd one out, a
combination that does not cancel -- is REJECTED.
"""

import json
import sys
from itertools import combinations


# ----------------------------------------------------------------------
# definitions, rebuilt
# ----------------------------------------------------------------------

def colex_bases(n, r):
    return sorted(combinations(range(1, n + 1), r), key=lambda t: tuple(reversed(t)))


def sort_sign(t):
    """Sort a tuple of distinct ints; return (sorted tuple, sign of perm)."""
    a = list(t)
    sg = 1
    for i in range(1, len(a)):
        j = i
        while j > 0 and a[j - 1] > a[j]:
            a[j - 1], a[j] = a[j], a[j - 1]
            sg = -sg
            j -= 1
    return tuple(a), sg


def det_int(m):
    """Exact determinant of a square matrix of Python ints, by cofactor
    expansion along the first row (deliberately not the producer's method)."""
    k = len(m)
    if k == 1:
        return m[0][0]
    if k == 2:
        return m[0][0] * m[1][1] - m[0][1] * m[1][0]
    tot = 0
    for c in range(k):
        if m[0][c] == 0:
            continue
        minor = [[m[i][j] for j in range(k) if j != c] for i in range(1, k)]
        term = m[0][c] * det_int(minor)
        tot += term if (c % 2 == 0) else -term
    return tot


def parse_chi(s, n, r):
    bas = colex_bases(n, r)
    if len(s) != len(bas):
        raise ValueError('sign string has length %d, expected %d'
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
# the two certificate checks
# ----------------------------------------------------------------------

def check_realizable(rec):
    n, r = int(rec['n']), int(rec['r'])
    chi, bas = parse_chi(rec['chi'], n, r)
    Z = rec['matrix']
    if len(Z) != r or any(len(row) != n for row in Z):
        return False, 'matrix is not %d x %d' % (r, n)
    Z = [[int(v) for v in row] for row in Z]
    idx = {}
    for j, B in enumerate(bas):
        sub = [[Z[i][b - 1] for b in B] for i in range(r)]
        d = det_int(sub)
        if d == 0:
            return False, 'bracket %s vanishes: configuration is not uniform' % (B,)
        s = 1 if d > 0 else -1
        if s != chi[j]:
            return False, 'bracket %s has sign %+d, chirotope says %+d' % (B, s, chi[j])
        idx[B] = d
    return True, 'all %d brackets nonzero and correct' % len(bas)


def check_nonrealizable(rec):
    n, r = int(rec['n']), int(rec['r'])
    chi, bas = parse_chi(rec['chi'], n, r)
    bidx = {B: j for j, B in enumerate(bas)}
    M = len(bas)
    terms = rec['bfp']
    if not terms:
        return False, 'empty Gordan vector'
    acc = [0] * M
    seen = set()
    for t in terms:
        L = tuple(int(x) for x in t['L'])
        a, b, c, d = (int(x) for x in t['abcd'])
        big, small, w = int(t['big']), int(t['small']), int(t['w'])
        if w <= 0:
            return False, 'weight %d is not positive' % w
        if big == small or not (0 <= big < 3) or not (0 <= small < 3):
            return False, 'bad term indices (big=%d, small=%d)' % (big, small)
        if len(set(L)) != r - 2 or len({a, b, c, d}) != 4:
            return False, 'malformed relation'
        if set(L) & {a, b, c, d}:
            return False, 'relation index set overlaps L'
        if not (a < b < c < d):
            return False, 'a,b,c,d not ascending'
        for x in L + (a, b, c, d):
            if not (1 <= x <= n):
                return False, 'element %d out of range' % x
        key = (L, (a, b, c, d), big, small)
        if key in seen:
            return False, 'duplicate inequality %s' % (key,)
        seen.add(key)
        # rebuild the three signed terms of  [Lab][Lcd] - [Lac][Lbd] + [Lad][Lbc]
        trip = []
        for (x, y, z, u, ex) in ((a, b, c, d, 1), (a, c, b, d, -1), (a, d, b, c, 1)):
            s1, g1 = sort_sign(L + (x, y))
            s2, g2 = sort_sign(L + (z, u))
            if s1 not in bidx or s2 not in bidx:
                return False, 'relation names a non-basis'
            trip.append((bidx[s1], bidx[s2], ex * g1 * g2))
        sgn = [tr[2] * chi[tr[0]] * chi[tr[1]] for tr in trip]
        if sgn[0] == sgn[1] == sgn[2]:
            return False, 'the class violates a GP relation: not a chirotope'
        others = [k for k in range(3) if k != big]
        if sgn[others[0]] != sgn[others[1]] or sgn[big] == sgn[others[0]]:
            return False, ('term %d is not the odd one out of relation '
                           '(%s; %d %d %d %d)' % (big, L, a, b, c, d))
        acc[trip[big][0]] += w
        acc[trip[big][1]] += w
        acc[trip[small][0]] -= w
        acc[trip[small][1]] -= w
    if any(acc):
        nz = [i for i, v in enumerate(acc) if v]
        return False, ('the weighted combination does not cancel: %d nonzero '
                       'coordinates, first at basis %s (%d)'
                       % (len(nz), bas[nz[0]], acc[nz[0]]))
    return True, ('Gordan vector with %d terms, total weight %d'
                  % (len(terms), sum(int(t['w']) for t in terms)))


def check_record(rec):
    v = rec.get('verdict')
    if v == 'REALIZABLE':
        return check_realizable(rec)
    if v == 'NON_REALIZABLE':
        return check_nonrealizable(rec)
    if v == 'RESIDUE':
        return True, 'no claim'
    return False, 'unknown verdict %r' % v


def check_file(path, verbose=False):
    counts = {'REALIZABLE': 0, 'NON_REALIZABLE': 0, 'RESIDUE': 0}
    bad = []
    seen_chi = {}
    with open(path) as fh:
        for ln, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            rec = json.loads(line)
            ok, msg = check_record(rec)
            v = rec.get('verdict')
            if not ok:
                bad.append((ln, v, msg))
                continue
            counts[v] = counts.get(v, 0) + 1
            ch = rec.get('chi')
            if ch in seen_chi and seen_chi[ch] != v:
                bad.append((ln, v, 'class already recorded as %s' % seen_chi[ch]))
            seen_chi[ch] = v
            if verbose:
                print('  line %d  %-16s %s' % (ln, v, msg))
    return counts, bad, len(seen_chi)


# ----------------------------------------------------------------------
# self-test: the checker must reject deliberately broken certificates
# ----------------------------------------------------------------------

def selftest():
    fails = []

    def expect(name, rec, want):
        ok, msg = check_record(rec)
        tag = 'ok ' if ok == want else 'FAIL'
        if ok != want:
            fails.append(name)
        print('  [%s] %-46s %s' % (tag, name, msg))

    # a genuine rank-3, 4-element realization
    n, r = 4, 3
    Z = [[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1]]
    bas = colex_bases(n, r)
    chi = []
    for B in bas:
        d = det_int([[Z[i][b - 1] for b in B] for i in range(r)])
        chi.append('+' if d > 0 else '-')
    good = {'n': n, 'r': r, 'chi': ''.join(chi), 'verdict': 'REALIZABLE',
            'matrix': Z}
    expect('honest realization accepted', good, True)

    b1 = json.loads(json.dumps(good))
    b1['matrix'][0][3] = -1
    expect('corrupted matrix entry rejected', b1, False)

    b2 = json.loads(json.dumps(good))
    b2['chi'] = ('-' if good['chi'][0] == '+' else '+') + good['chi'][1:]
    expect('flipped chirotope bit rejected', b2, False)

    b3 = json.loads(json.dumps(good))
    b3['matrix'] = [[1, 0, 0, 1], [0, 1, 0, 1], [0, 0, 0, 0]]
    expect('degenerate (vanishing bracket) rejected', b3, False)

    return fails


if __name__ == '__main__':
    args = [a for a in sys.argv[1:]]
    if '--selftest' in args:
        print('checkcert self-test:')
        f = selftest()
        print('SELFTEST %s' % ('FAILED: ' + ', '.join(f) if f else 'PASSED'))
        sys.exit(1 if f else 0)
    verbose = '-v' in args
    args = [a for a in args if not a.startswith('-')]
    if not args:
        print(__doc__)
        sys.exit(2)
    rc = 0
    for path in args:
        counts, bad, nclasses = check_file(path, verbose)
        print('%s: %d distinct classes' % (path, nclasses))
        for k in ('REALIZABLE', 'NON_REALIZABLE', 'RESIDUE'):
            print('    %-16s %d' % (k, counts.get(k, 0)))
        if bad:
            rc = 1
            print('    REJECTED         %d' % len(bad))
            for ln, v, msg in bad[:20]:
                print('      line %d (%s): %s' % (ln, v, msg))
    print('ALL CERTIFICATES ACCEPTED' if rc == 0 else 'REJECTIONS PRESENT')
    sys.exit(rc)
