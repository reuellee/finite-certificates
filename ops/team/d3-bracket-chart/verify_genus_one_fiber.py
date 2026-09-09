"""Independent standard-library arithmetic for the genus-one fiber obstruction.

Reconstructs from the pinned original three equations; imports no producer,
CAS, or other repository arithmetic. The genus deduction is in REPORT.md.
This is not a proof of D3 or of noncompactness of the full source.
"""
from fractions import Fraction as Q
from itertools import combinations, permutations
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[3]
SOURCE = ROOT/'ai/omreal/data/DIAG3_triple_fullspace_critical_h1.json'
PIN = 'c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8'
ZERO = (0,)*9


def constant(k):
    return {ZERO:k} if k else {}


def variable(j):
    return {tuple(int(k == j) for k in range(9)):1}


def scale(p,k):
    return {m:v*k for m,v in p.items() if v*k}


def plus(*ps):
    answer = {}
    for p in ps:
        for m,v in p.items():
            answer[m] = answer.get(m,0)+v
    return {m:v for m,v in answer.items() if v}


def times(p,q):
    answer = {}
    for m,v in p.items():
        for n,w in q.items():
            t = tuple(x+y for x,y in zip(m,n))
            answer[t] = answer.get(t,0)+v*w
    return {m:v for m,v in answer.items() if v}


def product(ps):
    answer = constant(1)
    for p in ps:
        answer = times(answer,p)
    return answer


def coefficient(p,j,k):
    answer = {}
    for m,v in p.items():
        if m[j] == k:
            n = list(m)
            n[j] = 0
            answer[tuple(n)] = v
    return answer


def degree(p,j):
    return max((m[j] for m in p),default=-1)


def specialize(p,values):
    answer = {}
    for m,v in p.items():
        n = list(m)
        for j,value in values.items():
            v *= value**n[j]
            n[j] = 0
        key = tuple(n)
        answer[key] = answer.get(key,0)+v
    return {m:v for m,v in answer.items() if v}


def evaluate(p,point):
    return sum(v*product_numbers(x**k for x,k in zip(point,m)) for m,v in p.items())


def product_numbers(values):
    answer = Q(1)
    for x in values:
        answer *= x
    return answer


def det_poly(matrix):
    size = len(matrix)
    terms = []
    for perm in permutations(range(size)):
        parity = sum(perm[j] > perm[k] for j in range(size) for k in range(j+1,size))
        terms.append(scale(product(matrix[j][perm[j]] for j in range(size)),(-1)**parity))
    return plus(*terms)


def det_number(matrix):
    rows = [[Q(x) for x in row] for row in matrix]
    result = Q(1)
    for j in range(len(rows)):
        pivot = next((k for k in range(j,len(rows)) if rows[k][j]),None)
        if pivot is None:
            return Q(0)
        if pivot != j:
            rows[pivot],rows[j] = rows[j],rows[pivot]
            result = -result
        value = rows[j][j]
        result *= value
        for k in range(j+1,len(rows)):
            factor = rows[k][j]/value
            for l in range(j,len(rows)):
                rows[k][l] -= factor*rows[j][l]
    return result


def quartic_discriminant(coeffs):
    # Descending coefficients. A nonzero Sylvester determinant proves gcd=1.
    assert len(coeffs) == 5 and coeffs[0]
    derivative = [coeffs[j]*(4-j) for j in range(4)]
    matrix = []
    for shift in range(3):
        matrix.append([0]*shift+coeffs+[0]*(2-shift))
    for shift in range(4):
        matrix.append([0]*shift+derivative+[0]*(3-shift))
    return det_number(matrix)/coeffs[0]


def sign(x):
    return (x > 0)-(x < 0)


def expect_rejected(check):
    try:
        check()
    except AssertionError:
        return
    raise AssertionError('negative control was accepted')


def require_equal(left,right):
    assert left == right


def require_squarefree_quartic(coeffs):
    assert quartic_discriminant(coeffs) != 0


def require_uniform(walls,point):
    assert all(evaluate(w,point) for w in walls.values())


def verify():
    raw = SOURCE.read_bytes()
    assert hashlib.sha256(raw).hexdigest() == PIN
    payload = json.loads(raw)
    assert payload['named_presentation'] == [5563,16134,19284]
    q = [{tuple(m):int(v) for v,m in rec['terms']} for rec in payload['equations'][:3]]
    a,b,c,d,e,f,g,h,i = [variable(j) for j in range(9)]
    one = constant(1)
    d_numerator = plus(times(b,plus(i,scale(f,-1))),times(f,g))
    assert q[0] == plus(times(i,d),scale(d_numerator,-1))
    assert all(degree(p,3) == 1 for p in q[1:])
    reduced = [plus(times(i,coefficient(p,3,0)),times(d_numerator,coefficient(p,3,1))) for p in q[1:]]
    assert all(degree(p,0) == 1 for p in reduced)
    B,A = coefficient(reduced[0],0,0),coefficient(reduced[0],0,1)
    D,C = coefficient(reduced[1],0,0),coefficient(reduced[1],0,1)
    unit = product([plus(f,scale(one,-1)),plus(h,scale(one,-1)),plus(times(b,f),scale(times(c,e),-1))])
    assert A == times(i,unit)
    N = plus(times(A,D),scale(times(C,B),-1))
    assert len(N) == 389
    assert degree(N,0) == degree(N,3) == 0
    assert (degree(N,2),degree(N,4)) == (2,2)
    C0,C1,C2 = [coefficient(N,4,k) for k in range(3)]
    delta = plus(times(C1,C1),scale(times(C0,C2),-4))
    assert degree(delta,2) == 4
    assert len(delta) == 3257
    # The global double-cover identity needs no inversion of C2 here.
    left = plus(times(plus(scale(times(C2,e),2),C1),plus(scale(times(C2,e),2),C1)),scale(delta,-1))
    assert left == scale(times(C2,N),4)

    base = {1:Q(-23,7),5:Q(-3),6:Q(-1),7:Q(2),8:Q(4)}
    def ce_term(value,c_power,e_power):
        m = list(ZERO)
        m[2],m[4] = c_power,e_power
        return {tuple(m):value}
    F = plus(*(ce_term(*term) for term in [
        (539,2,2),(1323,2,1),(-2156,2,0),(-28,1,2),
        (-8092,1,1),(-27076,1,0),(1449,0,2),(8901,0,1),(17388,0,0)]))
    assert specialize(N,base) == scale(F,Q(64,49))
    W_desc = [6398665,36722952,61007646,14826168,-21553047]
    W = plus(*(ce_term(value,4-j,0) for j,value in enumerate(W_desc)))
    assert specialize(delta,base) == scale(W,Q(4096,2401))
    F0,F1,F2 = [coefficient(F,4,k) for k in range(3)]
    assert plus(times(F1,F1),scale(times(F0,F2),-4)) == W
    discriminant = quartic_discriminant(W_desc)
    assert discriminant == 4649793772367457417206802405651256329633792
    assert discriminant != 0
    assert 28**2-4*539*1449 == -3123260

    parent = [[constant(int(row == col)) for col in range(4)]+[one]+[
        one if row == 0 else variable(3*col+row-1) for col in range(3)] for row in range(4)]
    walls = {''.join(str(j+1) for j in inds):det_poly([[row[j] for j in inds] for row in parent]) for inds in combinations(range(8),4)}
    assert walls['1238'] == i
    assert walls['2357'] == plus(f,scale(one,-1))
    assert walls['2458'] == plus(one,scale(h,-1))
    assert walls['1267'] == plus(times(b,f),scale(times(c,e),-1))
    assert walls['1346'] == a
    point = [Q(-19,28),Q(-23,7),Q(-27,14),Q(-5),Q(-4),Q(-3),Q(-1),Q(2),Q(4)]
    assert all(evaluate(p,point) == 0 for p in q)
    require_uniform(walls,point)
    Fe = plus(F1,scale(times(e,F2),2))
    assert evaluate(Fe,point) == Q(5463,4)
    assert evaluate(W,point) == Q(29844369,16)

    # Four disjoint sign-changing intervals exhaust all real roots by degree.
    intervals = [(Q(-1189,445),Q(-171,64)),(Q(-347,158),Q(-459,209)),
                 (Q(-55,42),Q(-347,265)),(Q(32,73),Q(153,349))]
    last = None
    for lo,hi in intervals:
        assert lo < hi and (last is None or last < lo)
        x,y = list(point),list(point)
        x[2],y[2] = lo,hi
        assert evaluate(W,x)*evaluate(W,y) < 0
        last = hi
    assert intervals[1][1] < point[2] < intervals[2][0]
    # The opposite sheet at the same c also lies on the compact real oval.
    conjugate = list(point)
    conjugate[0],conjugate[4] = Q(90,91),Q(-6843,1559)
    assert all(evaluate(p,conjugate) == 0 for p in q)
    assert evaluate(F,conjugate) == 0
    assert conjugate[4] != point[4]
    assert evaluate(F2,point)*(conjugate[4]+point[4]) == -evaluate(F1,point)
    require_uniform(walls,conjugate)
    assert evaluate(walls['1346'],point)*evaluate(walls['1346'],conjugate) < 0

    expect_rejected(lambda:require_equal(specialize(N,base),scale(plus(F,one),Q(64,49))))
    expect_rejected(lambda:require_squarefree_quartic([1,0,-2,0,1]))
    bad_point = list(point)
    bad_point[2] = 0
    expect_rejected(lambda:require_uniform(walls,bad_point))
    return {
        'result':'PASS_EXACT_GENUS_ONE_FIBER_ARITHMETIC',
        'source_sha256':PIN,'generic_numerator_terms':len(N),
        'generic_bidegree_ce':[2,2],'generic_discriminant_c_degree':4,
        'generic_discriminant_terms':len(delta),
        'sample_quartic_discriminant':str(discriminant),
        'sample_real_roots':4,'source_point':[str(x) for x in point],
        'source_point_parent_nonzero_brackets':len(walls),
        'source_point_F_e':str(evaluate(Fe,point)),
        'opposite_sheet_point':[str(x) for x in conjugate],
        'opposite_sheet_parent_nonzero_brackets':len(walls),
        'opposite_parent_bracket':'1346',
        'parent_signs':''.join('+' if evaluate(w,point)>0 else '-' for w in walls.values()),
        'negative_controls_rejected':3,
        'geometric_inference':'REPORT.md applies Riemann-Hurwitz to the squarefree quartic; not machine-formalized.',
        'independent_ai_referee':'NOT_PERFORMED; separate arithmetic implementation by coordinator',
        'full_source_noncompactness':'NOT_PROVED','pair_injectivity':'NOT_PROVED',
        'triple_source_residual':1162302,'ledger':'2/9'}


if __name__ == '__main__':
    print(json.dumps(verify(),indent=2))
