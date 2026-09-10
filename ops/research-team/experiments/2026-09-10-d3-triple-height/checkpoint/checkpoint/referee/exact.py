"""Independent referee arithmetic. No producer imports; Python standard library only."""
from fractions import Fraction as Q
from itertools import combinations, permutations


def q(x):
    if isinstance(x, float):
        raise ValueError('floating input is not an exact certificate')
    return Q(x)


def matrix(rows):
    return [[q(x) for x in row] for row in rows]


def det(a):
    n = len(a)
    assert all(len(row) == n for row in a)
    out = Q(0)
    for p in permutations(range(n)):
        term = Q((-1) ** sum(p[i] > p[j] for i in range(n) for j in range(i+1,n)))
        for i,j in enumerate(p):
            term *= a[i][j]
        out += term
    return out


def rank(a):
    a = matrix(a)
    if not a:
        return 0
    r = 0
    for j in range(len(a[0])):
        pivot = next((k for k in range(r, len(a)) if a[k][j]), None)
        if pivot is None:
            continue
        a[r], a[pivot] = a[pivot], a[r]
        v = a[r][j]
        a[r] = [x/v for x in a[r]]
        for k in range(len(a)):
            if k != r:
                v = a[k][j]
                a[k] = [x-v*y for x,y in zip(a[k],a[r])]
        r += 1
        if r == len(a):
            break
    return r


def colex(n,k):
    return sorted(combinations(range(n),k),key=lambda t:tuple(reversed(t)))


def normals(y,signature=None):
    """a_I p = det(y_i,y_j,y_k,p); bit 1 is positive, bit 0 negative."""
    y = matrix(y)
    rows = []
    for index, support in enumerate(colex(8,3)):
        normal = []
        for j in range(4):
            a = [[y[r][i] for i in support] + [Q(r == j)] for r in range(4)]
            normal.append(det(a))
        if signature is not None and not ((signature >> index) & 1):
            normal = [-v for v in normal]
        rows.append(normal)
    return rows


def brackets(y):
    y = matrix(y)
    return [det([[y[r][i] for i in support] for r in range(4)])
            for support in colex(8,4)]


def sign(x):
    return (x > 0) - (x < 0)


def verify_witness(y, signature, support, weights, expected_signs=None, expected_rank=None):
    assert len(y) == 4 and all(len(r) == 8 for r in y)
    if expected_signs is not None:
        assert [sign(x) for x in brackets(y)] == expected_signs, 'parent chamber mismatch'
    assert len(set(support)) == len(support), 'duplicate support'
    assert len(support) == len(weights) and all(0 <= i < 56 for i in support)
    weights = [q(x) for x in weights]
    assert all(x >= 0 for x in weights) and sum(weights) > 0, 'not positive normalized dependence'
    a = normals(y,signature)
    assert all(sum(weights[k]*a[i][j] for k,i in enumerate(support)) == 0
               for j in range(4)), 'dependence residual'
    r = rank([a[i] for i in support])
    if expected_rank is not None:
        assert r == expected_rank, 'rank mismatch'
    return {'rank':r,'normalized_weights':[str(x/sum(weights)) for x in weights]}


def affine_rank(y,signature,support):
    return rank([normal+[Q(1)] for i,normal in enumerate(normals(y,signature)) if i in support])


def reject(thunk):
    try:
        thunk()
    except (AssertionError,ValueError):
        return True
    raise AssertionError('hostile control was accepted')
