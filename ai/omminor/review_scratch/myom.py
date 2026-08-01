#!/usr/bin/env python3
"""Independent re-implementation for the adversarial review (REVIEW_FABLE).

Written from the definitions only.  Shares no code with minorlib.py /
coverage_checker.py / bfp.py.  numpy+scipy used only for the LP search; every
verdict-bearing statement is re-verified in exact integer/Fraction
arithmetic before being trusted.

Conventions (must match checkcert.py, the neutral referee):
  * ground set {1..n}; bases are r-subsets in COLEX order (sorted by
    reversed tuple);
  * chirotope = string over {+,-}, one char per basis;
  * GP relation (L; a<b<c<d), |L| = r-2, L disjoint from {a,b,c,d}; the
    three signed terms of  [Lab][Lcd] - [Lac][Lbd] + [Lad][Lbc].
"""

from itertools import combinations
from fractions import Fraction

import numpy as np


def colex(n, r):
    return sorted(combinations(range(1, n + 1), r), key=lambda t: tuple(reversed(t)))


def sort_sign(t):
    a = list(t)
    sg = 1
    for i in range(1, len(a)):
        j = i
        while j > 0 and a[j - 1] > a[j]:
            a[j - 1], a[j] = a[j], a[j - 1]
            sg = -sg
            j -= 1
    return tuple(a), sg


def parse(s):
    return [1 if c == '+' else -1 for c in s.strip()]


def unparse(v):
    return ''.join('+' if x > 0 else '-' for x in v)


# ----------------------------------------------------------------------
# minors, straight from the definition (no index tables)
# ----------------------------------------------------------------------

def deletion(chi_str, n, r, e):
    """chi \\ e, relabelled to {1..n-1} order-preservingly."""
    chi = parse(chi_str)
    pos = {B: j for j, B in enumerate(colex(n, r))}
    phi_inv = [x for x in range(1, n + 1) if x != e]   # phi_inv[i-1] = original
    out = []
    for B in colex(n - 1, r):
        orig = tuple(sorted(phi_inv[x - 1] for x in B))
        out.append(chi[pos[orig]])
    return unparse(out)


def contraction(chi_str, n, r, e):
    """chi / e : rank r-1 on {1..n-1};  (chi/e)(x) = chi(e, x...)."""
    chi = parse(chi_str)
    pos = {B: j for j, B in enumerate(colex(n, r))}
    phi_inv = [x for x in range(1, n + 1) if x != e]
    out = []
    for B in colex(n - 1, r - 1):
        orig = tuple(phi_inv[x - 1] for x in B)        # ascending, e removed
        tup = (e,) + orig
        srt, sg = sort_sign(tup)
        out.append(sg * chi[pos[srt]])
    return unparse(out)


# ----------------------------------------------------------------------
# GP relations and the inequality system
# ----------------------------------------------------------------------

def gp_relations(n, r):
    """[(L, (a,b,c,d), [(pidx,qidx,coef)]x3)] over colex bases."""
    bas = colex(n, r)
    pos = {B: j for j, B in enumerate(bas)}
    rels = []
    for L in combinations(range(1, n + 1), r - 2):
        rest = [x for x in range(1, n + 1) if x not in L]
        for (a, b, c, d) in combinations(rest, 4):
            trip = []
            for (x, y, z, u, ex) in ((a, b, c, d, 1), (a, c, b, d, -1),
                                     (a, d, b, c, 1)):
                s1, g1 = sort_sign(L + (x, y))
                s2, g2 = sort_sign(L + (z, u))
                trip.append((pos[s1], pos[s2], ex * g1 * g2))
            rels.append((L, (a, b, c, d), trip))
    return rels


def term_signs(chi, trip):
    return [t[2] * chi[t[0]] * chi[t[1]] for t in trip]


def gp_valid(chi_str, n, r, rels=None):
    chi = parse(chi_str)
    for (_, _, trip) in (rels or gp_relations(n, r)):
        s = term_signs(chi, trip)
        if s[0] == s[1] == s[2]:
            return False
    return True


def build_system(chi_str, n, r, rels=None):
    """All BFP inequalities of chi.  Returns (rows, meta) where rows is a
    list of dicts basis->coef (+1/+1/-1/-1) and meta[i] = (L, abcd, big,
    small)."""
    chi = parse(chi_str)
    rels = rels or gp_relations(n, r)
    rows, meta = [], []
    for (L, abcd, trip) in rels:
        s = term_signs(chi, trip)
        if s[0] == s[1] == s[2]:
            raise ValueError('not a chirotope')
        big = 0 if s[0] != s[1] and s[0] != s[2] else (1 if s[1] != s[0] and s[1] != s[2] else 2)
        for small in range(3):
            if small == big:
                continue
            row = {}
            for k, sgn in ((big, 1), (small, -1)):
                row[trip[k][0]] = row.get(trip[k][0], 0) + sgn
                row[trip[k][1]] = row.get(trip[k][1], 0) + sgn
            rows.append(row)
            meta.append((L, abcd, big, small))
    return rows, meta


def decide_bfp(chi_str, n, r, rels=None):
    """Rigorously decide whether chi has a Gordan vector.

    Returns ('GORDAN', terms)  with integer-weight terms verified exactly, or
            ('FEASIBLE', yint) with an exact integer strict-feasibility
                               witness (proves NO Gordan vector exists), or
            raises RuntimeError if neither side could be verified.
    """
    from scipy.optimize import linprog
    M = len(colex(n, r))
    rows, meta = build_system(chi_str, n, r, rels)
    K = len(rows)
    A = np.zeros((K, M))
    for i, row in enumerate(rows):
        for j, v in row.items():
            A[i, j] = v

    # primal side: max t  s.t.  A y >= t, -1 <= y <= 1, t <= 1
    c = np.zeros(M + 1)
    c[-1] = -1.0
    Aub = np.hstack([-A, np.ones((K, 1))])
    bub = np.zeros(K)
    bounds = [(-1e3, 1e3)] * M + [(None, 1.0)]
    res = linprog(c, A_ub=Aub, b_ub=bub, bounds=bounds, method='highs')
    if res.status == 0 and res.x is not None and res.x[-1] > 1e-7:
        y = res.x[:M]
        scale = 10 ** 7
        yint = [int(round(v * scale)) for v in y]
        ok = True
        for row in rows:
            tot = sum(v * yint[j] for j, v in row.items())
            if tot <= 0:
                ok = False
                break
        if ok:
            return ('FEASIBLE', yint)
    # dual side: find w >= 0, A^T w = 0, sum w = 1
    Aeq = np.vstack([A.T, np.ones((1, K))])
    beq = np.zeros(M + 1)
    beq[-1] = 1.0
    res2 = linprog(np.zeros(K), A_eq=Aeq, b_eq=beq,
                   bounds=[(0, None)] * K, method='highs')
    if res2.status == 0 and res2.x is not None:
        w = res2.x
        supp = [i for i in range(K) if w[i] > 1e-9]
        wexact = _exact_nullvector(rows, supp, M)
        if wexact is not None:
            terms = []
            for i, wi in zip(supp, wexact):
                if wi == 0:
                    continue
                L, abcd, big, small = meta[i]
                terms.append({'L': list(L), 'abcd': list(abcd),
                              'big': big, 'small': small, 'w': int(wi)})
            if terms and verify_gordan(chi_str, n, r, terms):
                return ('GORDAN', terms)
    raise RuntimeError('could not verify either side for %s' % chi_str[:20])


def _exact_nullvector(rows, supp, M):
    """Exact nonnegative rational solution of sum_i w_i rows[i] = 0,
    sum w = 1, restricted to the support; returns integer weights or None."""
    cols = supp
    eqs = []
    for j in range(M):
        eq = [Fraction(rows[i].get(j, 0)) for i in cols]
        if any(eq):
            eqs.append(eq + [Fraction(0)])
    eqs.append([Fraction(1)] * len(cols) + [Fraction(1)])
    # Gaussian elimination
    nr_, nc = len(eqs), len(cols) + 1
    rank_rows = []
    piv_of_col = {}
    r_ = 0
    for c_ in range(len(cols)):
        p = None
        for i in range(r_, nr_):
            if eqs[i][c_] != 0:
                p = i
                break
        if p is None:
            continue
        eqs[r_], eqs[p] = eqs[p], eqs[r_]
        pv = eqs[r_][c_]
        eqs[r_] = [v / pv for v in eqs[r_]]
        for i in range(nr_):
            if i != r_ and eqs[i][c_] != 0:
                f = eqs[i][c_]
                eqs[i] = [a - f * b for a, b in zip(eqs[i], eqs[r_])]
        piv_of_col[c_] = r_
        rank_rows.append(c_)
        r_ += 1
        if r_ == nr_:
            break
    for i in range(r_, nr_):
        if eqs[i][-1] != 0:
            return None                      # inconsistent
    w = [Fraction(0)] * len(cols)
    for c_, rr in piv_of_col.items():
        w[c_] = eqs[rr][-1]                  # free vars = 0
    if any(v < 0 for v in w):
        return None
    from math import lcm
    den = 1
    for v in w:
        den = lcm(den, v.denominator)
    return [int(v * den) for v in w]


def verify_gordan(chi_str, n, r, terms):
    """My own exact certificate check (mirrors the definition, not checkcert)."""
    chi = parse(chi_str)
    bas = colex(n, r)
    pos = {B: j for j, B in enumerate(bas)}
    acc = [0] * len(bas)
    if not terms:
        return False
    for t in terms:
        L = tuple(t['L'])
        a, b, c, d = t['abcd']
        big, small, w = t['big'], t['small'], t['w']
        if w <= 0 or big == small or not (a < b < c < d):
            return False
        if set(L) & {a, b, c, d} or len(set(L)) != r - 2:
            return False
        trip = []
        for (x, y, z, u, ex) in ((a, b, c, d, 1), (a, c, b, d, -1),
                                 (a, d, b, c, 1)):
            s1, g1 = sort_sign(L + (x, y))
            s2, g2 = sort_sign(L + (z, u))
            trip.append((pos[s1], pos[s2], ex * g1 * g2))
        s = term_signs(chi, trip)
        if s[0] == s[1] == s[2]:
            return False
        others = [k for k in range(3) if k != big]
        if s[others[0]] != s[others[1]] or s[big] == s[others[0]]:
            return False
        acc[trip[big][0]] += w
        acc[trip[big][1]] += w
        acc[trip[small][0]] -= w
        acc[trip[small][1]] -= w
    return not any(acc)


# ----------------------------------------------------------------------
# exact determinants (for realization checks)
# ----------------------------------------------------------------------

def det(m):
    k = len(m)
    if k == 1:
        return m[0][0]
    tot = 0
    sign = 1
    # expansion along the first COLUMN (checkcert uses the first row)
    for i in range(k):
        if m[i][0]:
            minor = [row[1:] for j, row in enumerate(m) if j != i]
            tot += sign * m[i][0] * det(minor)
        sign = -sign
    return tot


def chi_of_matrix(Z, n, r):
    out = []
    for B in colex(n, r):
        sub = [[Z[i][b - 1] for b in B] for i in range(r)]
        d = det(sub)
        if d == 0:
            return None
        out.append(1 if d > 0 else -1)
    return unparse(out)


# ----------------------------------------------------------------------
# G' action (for orbit tests) -- my own implementation
# ----------------------------------------------------------------------

def act(chi_str, n, r, perm=None, reor=frozenset(), gsign=1):
    """(sigma, eps, s) . chi  with  (sigma.chi)(X) = chi(sigma^{-1} X)."""
    chi = parse(chi_str)
    bas = colex(n, r)
    pos = {B: j for j, B in enumerate(bas)}
    if perm is None:
        perm = list(range(n + 1))            # identity, 1-indexed
    inv = [0] * (n + 1)
    for i in range(1, n + 1):
        inv[perm[i]] = i
    out = []
    for B in bas:
        img = tuple(inv[b] for b in B)
        srt, sg = sort_sign(img)
        v = sg * chi[pos[srt]]
        if len(reor & set(B)) % 2:
            v = -v
        out.append(gsign * v)
    return unparse(out)


if __name__ == '__main__':
    # self-tests
    import random
    rng = random.Random(4711)
    n, r = 8, 4
    # random integer configuration -> chirotope -> must satisfy GP; and my
    # deletion/contraction of it must equal the minor of the configuration
    while True:
        Z = [[rng.randint(-9, 9) for _ in range(n)] for _ in range(r)]
        s = chi_of_matrix(Z, n, r)
        if s is not None:
            break
    rels = gp_relations(n, r)
    assert gp_valid(s, n, r, rels), 'realizable chirotope violates GP?!'
    e = 3
    dele = deletion(s, n, r, e)
    Zd = [[row[j] for j in range(n) if j != e - 1] for row in Z]
    assert dele == chi_of_matrix(Zd, n - 1, r), 'deletion != column deletion'
    con = contraction(s, n, r, e)
    # contraction signs must equal det(Z_e, Z_i1..Z_i3) directly
    outc = []
    keep = [x for x in range(1, n + 1) if x != e]
    for B in colex(n - 1, r - 1):
        cols = [e] + [keep[x - 1] for x in B]
        sub = [[Z[i][c - 1] for c in cols] for i in range(r)]
        d = det(sub)
        assert d != 0
        outc.append(1 if d > 0 else -1)
    assert con == unparse(outc), 'contraction != bracket definition'
    # group action: acting must preserve GP-validity and orbit realizability
    perm = list(range(n + 1))
    body = perm[1:]
    rng.shuffle(body)
    perm[1:] = body
    reor = frozenset(rng.sample(range(1, n + 1), 3))
    s2 = act(s, n, r, perm, reor, -1)
    assert gp_valid(s2, n, r, rels)
    # a Gordan vector must exist for NO realizable chirotope: quick check via
    # decide_bfp on the (cheap) rank-3 6-element case
    Z6 = [[1, 0, 0, 1, 2, 3], [0, 1, 0, 1, 5, 1], [0, 0, 1, 1, 1, 7]]
    s6 = chi_of_matrix(Z6, 6, 3)
    kind, _ = decide_bfp(s6, 6, 3)
    assert kind == 'FEASIBLE', kind
    print('myom self-tests PASSED')
