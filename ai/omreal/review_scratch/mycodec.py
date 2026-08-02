#!/usr/bin/env python3
"""ADVERSARIAL REVIEW -- a FIFTH, from-scratch independent implementation.

Written by the reviewer, not the producer.  Standard library only (no numpy
anywhere in the decision path).  Imports NOTHING from ai/omreal, ai/omopen or
ai/omgamma.  Every fact this module needs -- the colex basis order, the
128-bit key layout, the determinant of an integer matrix, the three-term
Grassmann-Plucker relation and which of its terms is forced to be the odd
one out -- is rebuilt here directly from the mathematical definition, in a
style deliberately different from every implementation already in the repo:

  - determinant: full Leibniz permutation expansion (sum over all r!
    permutations), not Laplace-by-minors (realize.py, fastverify.py),
    not cofactor recursion (checkcert.py), not Bareiss (fpcheck.py),
    not Fraction Gauss-Jordan (reverify.py, bfp.py's kernel solver).
  - key codec: big-integer bit shifts, written independently of both
    coverage_checker.py's numpy bit-packing and reverify.py's version
    (though it should, and will be checked to, agree with both).

This file is read-only tooling for the review.  It is never imported by
anything under ai/omreal or ai/omopen, and nothing here writes to sweep_state
or any existing data file.
"""
import itertools


def colex_bases(n, r):
    """1-based r-subsets of {1..n}, colex order (compare tuples reversed)."""
    return sorted(itertools.combinations(range(1, n + 1), r),
                  key=lambda t: tuple(reversed(t)))


def decode_key(hi, lo, M):
    """(hi, lo) uint64 pair -> length-M string of '+'/'-'.

    bit (M-1-j) of the 128-bit integer (hi<<64)|lo is 1 iff character j
    is '+'.  Top (128-M) bits must be zero.
    """
    v = (int(hi) << 64) | int(lo)
    if v >> M:
        raise ValueError('key has set bits above position M-1 (top %d bits '
                          'not zero)' % (128 - M))
    out = []
    for j in range(M):
        out.append('+' if (v >> (M - 1 - j)) & 1 else '-')
    return ''.join(out)


def encode_key(chi_str):
    """length-M string of '+'/'-' -> (hi, lo) uint64 pair."""
    M = len(chi_str)
    v = 0
    for ch in chi_str:
        v <<= 1
        if ch == '+':
            v |= 1
        elif ch == '-':
            pass
        else:
            raise ValueError('bad character %r' % ch)
    hi = v >> 64
    lo = v & 0xFFFFFFFFFFFFFFFF
    return hi, lo


def det_leibniz(rows):
    """Exact determinant of a square integer matrix by the full Leibniz
    permutation-expansion formula:  det(A) = sum_perm sign(perm) * prod_i A[i][perm[i]].

    O(k! * k) -- fine for k=4 (24 permutations).  Deliberately the least
    algorithmically related of any exact determinant routine in this
    project: no elimination, no minors, no recursion.
    """
    k = len(rows)
    idx = list(range(k))
    total = 0
    for perm in itertools.permutations(idx):
        # sign of the permutation by counting inversions
        sg = 1
        p = list(perm)
        for a in range(k):
            for b in range(a + 1, k):
                if p[a] > p[b]:
                    sg = -sg
        term = sg
        for i in range(k):
            term *= rows[i][perm[i]]
            if term == 0:
                break
        total += term
    return total


def bracket_signs(matrix, n, r, bases=None):
    """matrix: r rows of n integers (python ints).  Returns the len(bases)
    signs (+1/-1) in colex order, or None if some bracket vanishes.
    1-based basis elements, matrix columns 0-indexed (column b-1 for
    ground-set element b)."""
    if bases is None:
        bases = colex_bases(n, r)
    cols = [[matrix[i][q] for i in range(r)] for q in range(n)]
    out = []
    for B in bases:
        sub = [[cols[b - 1][i] for b in B] for i in range(r)]
        d = det_leibniz(sub)
        if d == 0:
            return None
        out.append(1 if d > 0 else -1)
    return out


def sort_sign(t):
    """Sort a tuple of distinct ints; (sorted tuple, sign of permutation),
    or (None, 0) if a value repeats."""
    a = list(t)
    if len(set(a)) != len(a):
        return None, 0
    sg = 1
    for i in range(1, len(a)):
        j = i
        while j > 0 and a[j - 1] > a[j]:
            a[j - 1], a[j] = a[j], a[j - 1]
            sg = -sg
            j -= 1
    return tuple(a), sg


def gp3_terms(L, a, b, c, d, bidx):
    """The three signed terms of the three-term GP relation on (L; a,b,c,d),
    a<b<c<d, |L| = r-2:
        +[Lab][Lcd]  -[Lac][Lbd]  +[Lad][Lbc]
    Returns [(sign, basis_i, basis_j), ...] len 3, indices into `bidx`.
    """
    out = []
    for (x, y, z, w, ex) in ((a, b, c, d, 1), (a, c, b, d, -1),
                             (a, d, b, c, 1)):
        s1, g1 = sort_sign(L + (x, y))
        s2, g2 = sort_sign(L + (z, w))
        if s1 is None or s2 is None:
            raise ValueError('degenerate bracket in gp3_terms')
        out.append((ex * g1 * g2, bidx[s1], bidx[s2]))
    return out


def gp3_big_index(chi_signs, terms):
    """Given the three (sign,i,j) terms and the chirotope's +-1 sign list,
    return the index (0,1,2) of the term whose value-sign disagrees with the
    OTHER two (the forced "big" term), or -1 if the relation is monochrome
    (all three agree -- not a valid chirotope) or otherwise not a clean
    2-vs-1 split (should not happen for a valid uniform chirotope)."""
    sgn = [ex * chi_signs[i] * chi_signs[j] for (ex, i, j) in terms]
    if sgn[0] == sgn[1] == sgn[2]:
        return -1, sgn
    for i in range(3):
        others = [sgn[k] for k in range(3) if k != i]
        if others[0] == others[1] and others[0] != sgn[i]:
            return i, sgn
    return -1, sgn


if __name__ == '__main__':
    # tiny self-check: colex order for n=4,r=2 must be
    # (1,2)(1,3)(2,3)(1,4)(2,4)(3,4)
    got = colex_bases(4, 2)
    want = [(1, 2), (1, 3), (2, 3), (1, 4), (2, 4), (3, 4)]
    assert got == want, (got, want)
    # encode/decode round trip
    s = '+-+-' * 31 + '+-'   # 126 chars
    assert len(s) == 126
    hi, lo = encode_key(s)
    back = decode_key(hi, lo, 126)
    assert back == s, (back, s)
    # det sanity: identity-like
    assert det_leibniz([[1, 0], [0, 1]]) == 1
    assert det_leibniz([[2, 0, 0], [0, 3, 0], [0, 0, 5]]) == 30
    assert det_leibniz([[1, 2], [3, 4]]) == 1 * 4 - 2 * 3
    print('mycodec.py self-check: PASS')
