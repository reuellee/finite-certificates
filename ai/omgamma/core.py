"""Core library for uniform oriented matroids (UOMs) as chirotopes.

Conventions (fixed project-wide, matching Finschi's OM database):
  * Ground set E = {1, ..., n}; rank r.
  * Bases = r-subsets of E, ordered in COLEX order (Finschi "RevLex-Index"
    basis order): A < B  iff  max(A xor B) in B.  Equivalently sort by the
    reversed sorted tuple.  For (n,r)=(7,4): 1234,1235,1245,1345,2345,1236,...
  * A uniform chirotope is stored as an int bitmask `b` over M = C(n,r) bits:
    bit i is 1  iff  chi(BASES[i]) = +1  (evaluated on the ascending tuple).
  * Finschi string: s[i] = '+' or '-' for basis index i (colex order).
  * Validity (uniform): all values nonzero (automatic) + all 3-term
    Grassmann-Pluecker conditions, following Richter-Gebert & Ziegler,
    Handbook of Discrete and Computational Geometry, 3rd ed., Chapter 6,
    Definition in 6.2.3 (CHI2) + Theorem 6.2.3:
      for every (r-2)-subset lam and a<b<c<d disjoint from lam, the set
      { chi(lam,a,b)chi(lam,c,d), -chi(lam,a,c)chi(lam,b,d),
        chi(lam,a,d)chi(lam,b,c) }
      contains {-1,+1}  (for uniform: it cannot be {0}, so validity = the
      three terms are not all equal).
    (CHI1) is automatic for uniform (the uniform matroid U_{r,n}).
  * Group G(n) = S_n x {0,1}^n x {0,1} acting on chirotopes by
      ((sig,eps,s).chi)(x_1..x_r) =
          (-1)^s * (-1)^{|eps cap {x_1..x_r}|} * chi(sig^{-1}x_1,...,sig^{-1}x_r),
    a LEFT action.  Composition (verified in tests):
      (sig1,eps1,s1)*(sig2,eps2,s2) = (sig1 o sig2, eps1 + sig1(eps2), s1+s2)
    where sig(eps)_i = eps_{sig^{-1}(i)}.
  * A mutation flips the sign of one basis such that the result is again a
    valid uniform chirotope (Bjoerner et al., Oriented Matroids, Sec. 7.3;
    equals the tope-graph mutation of Knauer-Marc arXiv:2002.11403 Sec. 4 --
    verified computationally in tests via simplicial topes).

Everything is pure stdlib Python, exact integer arithmetic.
"""
from itertools import combinations, permutations
from functools import lru_cache


# ----------------------------------------------------------------------
# bases and indexing
# ----------------------------------------------------------------------

@lru_cache(maxsize=None)
def bases_colex(n, r):
    """All r-subsets of {1..n} as ascending tuples, in colex order."""
    bs = sorted(combinations(range(1, n + 1), r),
                key=lambda t: tuple(reversed(t)))
    return tuple(bs)


@lru_cache(maxsize=None)
def basis_index(n, r):
    """dict: ascending r-tuple -> colex index."""
    return {B: i for i, B in enumerate(bases_colex(n, r))}


def sort_sign(tup):
    """Return (sorted_tuple, sign) where sign is the parity (+1/-1) of the
    permutation sorting `tup`; sign 0 if repeated entries."""
    t = list(tup)
    if len(set(t)) != len(t):
        return tuple(sorted(t)), 0
    sign = 1
    # insertion sort counting swaps (tuples are tiny)
    for i in range(1, len(t)):
        j = i
        while j > 0 and t[j - 1] > t[j]:
            t[j - 1], t[j] = t[j], t[j - 1]
            sign = -sign
            j -= 1
    return tuple(t), sign


def chi_eval(n, r, b, tup):
    """Evaluate chirotope bitmask b on an arbitrary r-tuple (+1/-1/0)."""
    st, sg = sort_sign(tup)
    if sg == 0:
        return 0
    i = basis_index(n, r)[st]
    v = 1 if (b >> i) & 1 else -1
    return v * sg


# ----------------------------------------------------------------------
# Grassmann-Pluecker 3-term machinery (uniform case)
# ----------------------------------------------------------------------

@lru_cache(maxsize=None)
def gp3_conditions(n, r):
    """Precompute all 3-term GP conditions.

    Each condition is a tuple (i1,i2,c1, i3,i4,c2, i5,i6,c3) of basis
    indices and constant bits, encoding the three signs
       s_k = (-1)^{c_k} * chi[i_{2k-1}] * chi[i_{2k}]
    with s_1 = chi(lam,a,b)chi(lam,c,d), s_2 = -chi(lam,a,c)chi(lam,b,d),
    s_3 = chi(lam,a,d)chi(lam,b,c).
    In bit arithmetic (bit=1 means +): p_k = b[i]^b[j]^c_k with p_k=0
    meaning s_k=+1.  Condition satisfied iff not (p1 == p2 == p3).
    """
    idx = basis_index(n, r)
    E = range(1, n + 1)
    conds = []
    for lam in combinations(E, r - 2):
        rest = [x for x in E if x not in lam]
        for a, bb, c, d in combinations(rest, 4):
            entries = []
            for (x, y), extra_neg in (((a, bb), 0), ((c, d), 0),
                                      ((a, c), 1), ((bb, d), 0),
                                      ((a, d), 0), ((bb, c), 0)):
                st, sg = sort_sign(lam + (x, y))
                # value = sg * chi[st]; bit contribution: (bit==0 -> minus)
                # sign -1 contributes constant 1
                cbit = (1 if sg < 0 else 0) ^ extra_neg
                entries.append((idx[st], cbit))
            (i1, c1a), (i2, c1b), (i3, c2a), (i4, c2b), (i5, c3a), (i6, c3b) \
                = entries
            conds.append((i1, i2, c1a ^ c1b,
                          i3, i4, c2a ^ c2b,
                          i5, i6, c3a ^ c3b))
    return tuple(conds)


@lru_cache(maxsize=None)
def gp3_by_basis(n, r):
    """dict: basis index -> tuple of condition indices involving it."""
    conds = gp3_conditions(n, r)
    by = {}
    for k, (i1, i2, _, i3, i4, _, i5, i6, _) in enumerate(conds):
        for i in (i1, i2, i3, i4, i5, i6):
            by.setdefault(i, []).append(k)
    return {i: tuple(v) for i, v in by.items()}


def is_uniform_chirotope(n, r, b):
    """Full validity check of bitmask b (all 3-term GP conditions)."""
    for (i1, i2, c1, i3, i4, c2, i5, i6, c3) in gp3_conditions(n, r):
        p1 = ((b >> i1) ^ (b >> i2) ^ c1) & 1
        p2 = ((b >> i3) ^ (b >> i4) ^ c2) & 1
        p3 = ((b >> i5) ^ (b >> i6) ^ c3) & 1
        if p1 == p2 == p3:
            return False
    return True


def mutable_bases(n, r, b):
    """Indices i such that flipping bit i keeps validity.

    Assumes b is valid.  Only conditions involving i are rechecked.
    """
    conds = gp3_conditions(n, r)
    by = gp3_by_basis(n, r)
    out = []
    for i in range(len(bases_colex(n, r))):
        b2 = b ^ (1 << i)
        ok = True
        for k in by.get(i, ()):
            (i1, i2, c1, i3, i4, c2, i5, i6, c3) = conds[k]
            p1 = ((b2 >> i1) ^ (b2 >> i2) ^ c1) & 1
            p2 = ((b2 >> i3) ^ (b2 >> i4) ^ c2) & 1
            p3 = ((b2 >> i5) ^ (b2 >> i6) ^ c3) & 1
            if p1 == p2 == p3:
                ok = False
                break
        if ok:
            out.append(i)
    return out


# ----------------------------------------------------------------------
# strings
# ----------------------------------------------------------------------

def to_string(n, r, b):
    M = len(bases_colex(n, r))
    return ''.join('+' if (b >> i) & 1 else '-' for i in range(M))


def from_string(n, r, s):
    s = s.strip()
    M = len(bases_colex(n, r))
    assert len(s) == M, (len(s), M)
    b = 0
    for i, ch in enumerate(s):
        if ch == '+':
            b |= 1 << i
        else:
            assert ch == '-'
    return b


# ----------------------------------------------------------------------
# group elements g = (sig, eps, s)
#   sig: tuple of length n, sig[i-1] = image of i  (1-based images)
#   eps: int bitmask over elements, bit (i-1) set = element i reoriented
#   s:   0/1 global negation
# ----------------------------------------------------------------------

def g_identity(n):
    return (tuple(range(1, n + 1)), 0, 0)


def g_compose(n, g1, g2):
    """g1*g2 acting as g1 after g2: (g1*g2).chi = g1.(g2.chi)."""
    sig1, eps1, s1 = g1
    sig2, eps2, s2 = g2
    sig = tuple(sig1[sig2[i] - 1] for i in range(n))
    # sig1(eps2): bit at sig1(i) = eps2 bit at i
    e = 0
    for i in range(n):
        if (eps2 >> i) & 1:
            e |= 1 << (sig1[i] - 1)
    return (sig, eps1 ^ e, s1 ^ s2)


def g_inverse(n, g):
    sig, eps, s = g
    inv = [0] * n
    for i in range(n):
        inv[sig[i] - 1] = i + 1
    inv = tuple(inv)
    # (g^-1) eps' = inv(eps)
    e = 0
    for i in range(n):
        if (eps >> i) & 1:
            e |= 1 << (inv[i] - 1)
    return (inv, e, s)


@lru_cache(maxsize=None)
def _perm_tables(n, r):
    """For applying permutations quickly: for each basis index i (colex),
    the ascending tuple."""
    return bases_colex(n, r)


def g_apply(n, r, g, b):
    """Apply group element to chirotope bitmask.  Returns new bitmask."""
    sig, eps, s = g
    idx = basis_index(n, r)
    out = 0
    popc = int.bit_count
    for i, B in enumerate(bases_colex(n, r)):
        # value of new chirotope at sorted set B:
        # (g.chi)(B) = (-1)^s (-1)^{|eps cap B|} chi(sig^{-1} B)
        # ... but we build instead by pushing forward: new[sig(B)] etc.
        # Simpler: directly compute at target: for each source basis B with
        # bit v, it contributes to sorted(sig(B)) with sorting sign.
        timg = tuple(sig[x - 1] for x in B)
        st, sg = sort_sign(timg)
        v = (b >> i) & 1                      # 1 = +
        # eps acts on the *new* labels?  Convention: (eps.chi)(x)=
        # (-1)^{|eps cap x|} chi(x); with combined element, eps applies last
        # (outermost).  |eps cap st| uses the image set st.
        ebits = popc(eps & _set_mask(st))
        neg = (s + ebits + (0 if sg > 0 else 1)) & 1
        nv = v ^ neg
        if nv:
            out |= 1 << idx[st]
    return out


def _set_mask(tup):
    m = 0
    for x in tup:
        m |= 1 << (x - 1)
    return m


# ----------------------------------------------------------------------
# duality (uniform):  chi*(coB) = chi(B) * sign(B, coB concatenated)
# ----------------------------------------------------------------------

def dualize(n, r, b):
    """Return bitmask of the dual chirotope of rank n-r.

    chi*(x_{r+1},...,x_n) = chi(x_1,...,x_r) * sgn(x_1,...,x_n)
    for any permutation (x_1..x_n) of E.  (BLSWZ Prop. 3.4.3 / standard.)
    """
    rd = n - r
    idxd = basis_index(n, rd)
    out = 0
    allE = tuple(range(1, n + 1))
    for i, B in enumerate(bases_colex(n, r)):
        co = tuple(x for x in allE if x not in B)
        _, sg = sort_sign(B + co)
        v = 1 if (b >> i) & 1 else -1
        vd = v * sg
        if vd > 0:
            out |= 1 << idxd[co]
    return out


# ----------------------------------------------------------------------
# topes / cocircuits (small-n verification utilities)
# ----------------------------------------------------------------------

def cocircuits(n, r, b):
    """All cocircuits as sign tuples of length n (Handbook Thm 6.2.3):
    for each (r-1)-subset lam: c_j = chi(lam, j) for j not in lam, c_lam=0;
    plus negatives."""
    out = set()
    for lam in combinations(range(1, n + 1), r - 1):
        c = [0] * n
        for j in range(1, n + 1):
            if j in lam:
                continue
            c[j - 1] = chi_eval(n, r, b, lam + (j,))
        c = tuple(c)
        out.add(c)
        out.add(tuple(-x for x in c))
    return out


def topes(n, r, b):
    """All topes (maximal covectors) as +-1 tuples of length n.

    A sign vector T in {+1,-1}^n is a tope iff it is a composition of
    cocircuits ... for uniform OMs we use: T is a tope iff for every
    cocircuit c, T is 'consistent' with c or -c ... Simplest correct
    characterization: T is a tope iff T conforms to the covector span; we
    use the standard fact that topes = maximal compositions and compute by
    closing cocircuits under composition.  Exponential but fine for tests.
    """
    cos = list(cocircuits(n, r, b))
    # iterative composition closure starting from cocircuits until full
    # support vectors; BFS over partial compositions.
    full = set()
    seen = set(cos)
    frontier = list(cos)
    while frontier:
        X = frontier.pop()
        if all(v != 0 for v in X):
            full.add(X)
            continue
        for c in cos:
            Y = tuple(x if x != 0 else y for x, y in zip(X, c))
            if Y not in seen:
                seen.add(Y)
                frontier.append(Y)
    return full


def tope_graph_degrees(n, r, b):
    """dict tope -> degree in tope graph (adjacency = differ in exactly one
    coordinate, both topes)."""
    T = topes(n, r, b)
    deg = {}
    for t in T:
        d = 0
        for i in range(n):
            t2 = t[:i] + (-t[i],) + t[i + 1:]
            if t2 in T:
                d += 1
        deg[t] = d
    return deg
