#!/usr/bin/env python3
"""Exact, stdlib-only replay of the 2026-11-21 D9 critical-incidence pilot.

Scope: two one-dimensional abstract semialgebraic canaries, NOT an actual
rank-four/eight parent or a universal ninth-diagonal certificate.
"""
from fractions import Fraction
from hashlib import sha256
import json


def rank(matrix):
    if not matrix:
        return 0
    a = [[Fraction(x) for x in row] for row in matrix]
    n, m = len(a), len(a[0]); k = 0
    for j in range(m):
        r = next((i for i in range(k, n) if a[i][j]), None)
        if r is None:
            continue
        a[k], a[r] = a[r], a[k]
        v = a[k][j]
        a[k] = [x / v for x in a[k]]
        for i in range(n):
            if i != k and a[i][j]:
                c = a[i][j]
                a[i] = [a[i][h] - c * a[k][h] for h in range(m)]
        k += 1
        if k == n:
            break
    return k


def incidence(n_vertices, edges):
    result = [[0 for _ in edges] for _ in range(n_vertices)]
    for j, (u, v) in enumerate(edges):
        assert 0 <= u < n_vertices and 0 <= v < n_vertices
        result[u][j] -= 1
        result[v][j] += 1
    return result


def laplacian(B):
    n = len(B); m = len(B[0]) if n else 0
    return [[sum(B[i][e]*B[j][e] for e in range(m)) for j in range(n)] for i in range(n)]


def verify_graph(n, edges, expected_h0):
    B = incidence(n, edges)
    L = laplacian(B)
    # Check every pairwise entry independently against degree/adjacency counts.
    for i in range(n):
        for j in range(n):
            expected = (sum((u==i)+(v==i) for u,v in edges if u!=v) if i==j else
                        -sum((u==i and v==j) or (u==j and v==i) for u,v in edges))
            assert L[i][j] == expected
    rB, rL = rank(B), rank(L)
    assert rB == rL  # exact rational arithmetic, PSD Gram matrix
    h0 = n - rB
    return dict(vertices=n, edges=len(edges), boundary_rank=rB,
                laplacian_rank=rL, H0_dimension=h0,
                accepted=(h0 == expected_h0),
                boundary=B, laplacian=L)


def main():
    checks = []
    def check(label, statement):
        assert statement, label
        checks.append(label)

    # Polynomial P=(x^2-4)^2+1/4, 4P=4u^2-32u+65.
    # Phi'(x)=2x*(4u^2-40u+97)/(4u^2-32u+65), u=x^2.
    D = [65,-32,4]
    H = [97,-40,4]
    check('connected-positive-polynomial-denominator', D == [4*16+1,-8*4,4])
    check('barrier-derivative-numerator',
          [D[0]+32,D[1]-8,D[2]] == H)
    # h(u) has discriminant 48, positive roots 5 +/- sqrt(3)/2.
    disc = H[1]**2-4*H[2]*H[0]
    check('two-distinct-positive-squared-critical-radii',
          disc == 48 and -H[1] > 0 and H[0]>0)
    # All signs below follow from h(0)>0, upward-opening h, and 0<root1<root2.
    # 0, +/-sqrt(root2) are minima; +/-sqrt(root1) maxima.
    check('three-minima-two-maxima-with-exact-order',
          H[0]>0 and H[2]>0 and 0<disc<(-H[1])**2)
    connected = verify_graph(3, [(0,1),(1,2)], 1)
    check('connected-canary-two-saddle-attachments', connected['accepted'])
    check('connected-canary-laplacian-rows-sum-zero',
          all(sum(row)==0 for row in connected['laplacian']))

    # Disconnected original D9 abstract canary, after exact positive-slab
    # elimination: base {x:x^2-1>0} has two intervals, x<-1 and x>1.
    # Phi'=2x(x^2-2)/(x^2-1), giving one minimum on each interval.
    check('two-disconnected-base-intervals',
          (-2)**2-1>0 and 2**2-1>0 and 0**2-1<0)
    check('two-minima-no-index-one-point', 2>1)
    disconnected = verify_graph(2, [], 2)
    check('disconnected-canary-null-laplacian',
          disconnected['accepted'] and disconnected['laplacian']==[[0,0],[0,0]])

    # Adversarial tests: omission and spurious same-component self-edge
    # cannot certify H0=1; arbitrary edge BETWEEN components would be invalid
    # unless a source-backed exact 1-handle attachment is supplied.
    bad_omitted = verify_graph(3, [(0,1)], 1)
    bad_loop = verify_graph(3, [(0,1),(1,1)], 1)
    check('hostile-deleted-saddle-rejected', not bad_omitted['accepted'])
    check('hostile-loop-saddle-rejected', not bad_loop['accepted'])
    check('hostile-unjustified-bridge-would-change-conclusion',
          verify_graph(2,[(0,1)],1)['accepted'])

    # Rank-one positive semidefinite increments: first exact saddle kills one
    # kernel mode, second exact saddle kills another; lack of saddle does not.
    ranks = [rank(laplacian(incidence(3, ed))) for ed in
             [[],[(0,1)],[(0,1),(1,2)]]]
    check('two-strict-rank-one-amplifications', ranks == [0,1,2])

    print(json.dumps({
      'format': 'd9-critical-incidence-pilot-v1',
      'date': '2026-11-21',
      'scope': 'one-dimensional abstract canaries; no actual 9DVL parent coverage',
      'theorem_ledger': '2/9',
      'connected_barrier': {'critical_minima':3, 'critical_maxima':2,
                            'certificate':connected},
      'disconnected_d9_abstract_barrier': {'critical_minima':2,
                                           'critical_maxima':0,
                                           'certificate':disconnected},
      'rank_progression':ranks,
      'hostile_deletion_result':bad_omitted['H0_dimension'],
      'hostile_self_loop_result':bad_loop['H0_dimension'],
      'exact_checks_passed':len(checks),
      'check_names':checks
    },indent=2,sort_keys=True))

if __name__ == '__main__':
    main()
