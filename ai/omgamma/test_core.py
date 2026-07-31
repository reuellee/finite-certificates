"""Tests + canaries for core.py.  Run: python test_core.py  (exit 0 = pass).

External anchors:
  * the 11 representatives IC(7,4,1..11) scraped verbatim from Finschi's
    catalog (finschi.com/math/om, page ?p=catom&card=7&rank=4&filter=nondeg)
  * exact-integer chirotopes of random rational point configurations
    (must always satisfy GP; group action must match acting on coordinates)

Canaries (deliberately broken inputs that MUST fail):
  * scrambled sign strings must fail the GP check
  * flipping a non-mutable basis must fail the GP check
  * a wrong composition rule must break the action-homomorphism test
"""
import random
import sys
from itertools import combinations

from core import (bases_colex, basis_index, gp3_conditions,
                  is_uniform_chirotope, mutable_bases, to_string, from_string,
                  g_identity, g_compose, g_inverse, g_apply, dualize,
                  chi_eval, cocircuits, topes, tope_graph_degrees, sort_sign)

random.seed(20260731)

IC74 = [
    "++++++++++++++++++++++++-++++------",
    "+++++++++++++++++++++++++++-------+",
    "++++++++++++++++++++++++++++--+--++",
    "++++++++++++++++++++++++++++-++---+",
    "++++++++++++++++++++++++++++-++--++",
    "++++++++++++++++++++++++++++++-----",
    "++++++++++++++++++++++++++++++-+---",
    "++++++++++++++++++++++++++++++++---",
    "+++++++++++++++++++++++++++++++++--",
    "++++++++++++++++++++++++++++++++++-",
    "+++++++++++++++++++++++++++++++++++",
]

FAILS = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


# ---------------------------------------------------------------- dets
def det_int(M):
    m = len(M)
    if m == 1:
        return M[0][0]
    tot = 0
    for j in range(m):
        if M[0][j]:
            minor = [row[:j] + row[j + 1:] for row in M[1:]]
            tot += (-1) ** j * M[0][j] * det_int(minor)
    return tot


def chirotope_of_points(n, r, pts):
    """pts: list of n integer vectors of length r; returns bitmask or None
    if degenerate."""
    idx = basis_index(n, r)
    b = 0
    for B in bases_colex(n, r):
        M = [pts[x - 1] for x in B]
        d = det_int(M)
        if d == 0:
            return None
        if d > 0:
            b |= 1 << idx[B]
    return b


def random_config(n, r, lo=-9, hi=9):
    while True:
        pts = [[random.randint(lo, hi) for _ in range(r)] for _ in range(n)]
        b = chirotope_of_points(n, r, pts)
        if b is not None:
            return pts, b


# ---------------------------------------------------------------- tests
def main():
    # 0. basis order matches Finschi header for (7,4)
    bs = bases_colex(7, 4)
    check("colex(7,4) starts 1234,1235,1245,1345,2345,1236",
          bs[:6] == ((1, 2, 3, 4), (1, 2, 3, 5), (1, 2, 4, 5),
                     (1, 3, 4, 5), (2, 3, 4, 5), (1, 2, 3, 6)))
    check("colex(7,4) count 35", len(bs) == 35)
    check("gp3 condition count (7,4) = C(7,2)*C(5,4) = 105",
          len(gp3_conditions(7, 4)) == 105)

    # 1. Finschi's 11 representatives are valid uniform chirotopes
    ok = all(is_uniform_chirotope(7, 4, from_string(7, 4, s)) for s in IC74)
    check("all 11 IC(7,4,*) reps satisfy GP", ok)
    check("roundtrip strings", all(
        to_string(7, 4, from_string(7, 4, s)) == s for s in IC74))

    # 2. moment curve => all-plus chirotope valid, for several (n,r)
    for (n, r) in [(6, 3), (7, 3), (8, 3), (9, 3), (6, 4), (7, 4), (8, 4),
                   (9, 4), (7, 5), (9, 5)]:
        pts = [[t ** k for k in range(r)] for t in range(1, n + 1)]
        b = chirotope_of_points(n, r, pts)
        allplus = (1 << len(bases_colex(n, r))) - 1
        check(f"moment curve ({n},{r}) gives all-plus and valid",
              b == allplus and is_uniform_chirotope(n, r, b))

    # 3. random exact configurations always satisfy GP
    ok = True
    for (n, r) in [(7, 3), (8, 3), (9, 3), (7, 4), (8, 4), (9, 4), (9, 5)]:
        for _ in range(8):
            _, b = random_config(n, r)
            if not is_uniform_chirotope(n, r, b):
                ok = False
    check("random exact-integer configs satisfy GP (7 shapes x8)", ok)

    # 4. CANARY: random sign strings should (essentially always) fail
    bad = 0
    for _ in range(300):
        b = random.getrandbits(35)
        if is_uniform_chirotope(7, 4, b):
            bad += 1
    check("canary: random 35-bit strings almost never valid (found "
          f"{bad}/300)", bad <= 3)

    # 5. CANARY: flipping a non-mutable basis of IC(7,4,1) fails GP
    b = from_string(7, 4, IC74[0])
    mut = set(mutable_bases(7, 4, b))
    nonmut = [i for i in range(35) if i not in mut]
    check("IC(7,4,1) has a non-mutable basis", len(nonmut) > 0)
    check("canary: flipping non-mutable basis fails GP",
          all(not is_uniform_chirotope(7, 4, b ^ (1 << i))
              for i in nonmut))
    check("flipping mutable basis keeps GP",
          all(is_uniform_chirotope(7, 4, b ^ (1 << i)) for i in mut))

    # 6. group action matches coordinate action, composition, inverse
    ok_perm = ok_reor = ok_glob = ok_comp = ok_inv = True
    for trial in range(10):
        n, r = random.choice([(7, 4), (8, 4), (8, 3), (9, 4)])
        pts, b = random_config(n, r)
        # relabeling sig: new config x'_j = x_{sig^{-1}(j)}
        sig = list(range(1, n + 1))
        random.shuffle(sig)
        sig = tuple(sig)
        inv = [0] * n
        for i in range(n):
            inv[sig[i] - 1] = i + 1
        pts2 = [pts[inv[j - 1] - 1] for j in range(1, n + 1)]
        b2 = chirotope_of_points(n, r, pts2)
        if b2 != g_apply(n, r, (sig, 0, 0), b):
            ok_perm = False
        # reorientation eps: negate those vectors
        eps = random.getrandbits(n)
        pts3 = [[-v for v in pts[i]] if (eps >> i) & 1 else pts[i]
                for i in range(n)]
        b3 = chirotope_of_points(n, r, pts3)
        if b3 != g_apply(n, r, (tuple(range(1, n + 1)), eps, 0), b):
            ok_reor = False
        # global negation: negate first coordinate of every vector
        pts4 = [[-p[0]] + p[1:] for p in pts]
        b4 = chirotope_of_points(n, r, pts4)
        if b4 != g_apply(n, r, (tuple(range(1, n + 1)), 0, 1), b):
            ok_glob = False
        # composition + inverse
        def rand_g():
            sg = list(range(1, n + 1))
            random.shuffle(sg)
            return (tuple(sg), random.getrandbits(n), random.getrandbits(1))
        g1, g2 = rand_g(), rand_g()
        if g_apply(n, r, g1, g_apply(n, r, g2, b)) != \
           g_apply(n, r, g_compose(n, g1, g2), b):
            ok_comp = False
        if g_apply(n, r, g_inverse(n, g1), g_apply(n, r, g1, b)) != b:
            ok_inv = False
    check("action matches permuting coordinates", ok_perm)
    check("action matches negating vectors (reorientation)", ok_reor)
    check("action matches global sign flip", ok_glob)
    check("g_apply is a homomorphism (composition)", ok_comp)
    check("inverse works", ok_inv)

    # 6b. CANARY: a deliberately wrong composition (forgetting to permute
    # eps) must break the homomorphism test on some sample
    def bad_compose(n, g1, g2):
        sig1, eps1, s1 = g1
        sig2, eps2, s2 = g2
        sig = tuple(sig1[sig2[i] - 1] for i in range(n))
        return (sig, eps1 ^ eps2, s1 ^ s2)   # WRONG: eps2 not permuted
    broke = False
    n, r = 7, 4
    pts, b = random_config(n, r)
    for _ in range(60):
        sg1 = list(range(1, n + 1)); random.shuffle(sg1)
        sg2 = list(range(1, n + 1)); random.shuffle(sg2)
        g1 = (tuple(sg1), random.getrandbits(n), 0)
        g2 = (tuple(sg2), random.getrandbits(n), 0)
        if g_apply(n, r, g1, g_apply(n, r, g2, b)) != \
           g_apply(n, r, bad_compose(n, g1, g2), b):
            broke = True
            break
    check("canary: wrong composition rule detected", broke)

    # 6c. even-rank kernel: all-ones reorientation acts trivially (r=4)
    b = from_string(7, 4, IC74[0])
    check("r=4: all-ones reorientation acts trivially",
          g_apply(7, 4, (tuple(range(1, 8)), (1 << 7) - 1, 0), b) == b)

    # 7. duality: valid -> valid, involution up to sign, action-compatible
    ok_v = ok_i = True
    for (n, r) in [(7, 4), (8, 3), (7, 3)]:
        for _ in range(5):
            _, b = random_config(n, r)
            bd = dualize(n, r, b)
            if not is_uniform_chirotope(n, n - r, bd):
                ok_v = False
            bdd = dualize(n, n - r, bd)
            allm = (1 << len(bases_colex(n, r))) - 1
            if bdd != b and bdd != b ^ allm:
                ok_i = False
    check("dual of valid is valid", ok_v)
    check("double dual = +-original", ok_i)
    # mutation sets correspond under duality (complement bases)
    _, b = random_config(7, 4)
    bd = dualize(7, 4, b)
    mb = {bases_colex(7, 4)[i] for i in mutable_bases(7, 4, b)}
    mbd = {bases_colex(7, 3)[i] for i in mutable_bases(7, 3, bd)}
    comp = {tuple(x for x in range(1, 8) if x not in B) for B in mb}
    check("mutable bases of dual = complements of mutable bases", comp == mbd)

    # 8. realizable => at least n mutations (Roudneff-Sturmfels 1.2/Shannon)
    ok = True
    for (n, r) in [(7, 4), (8, 4), (9, 4), (8, 3)]:
        for _ in range(4):
            _, b = random_config(n, r)
            if len(mutable_bases(n, r, b)) < n:
                ok = False
    check("realizable samples have >= n mutations (RS88)", ok)

    # 9. tope-graph equivalence of mutation definition (small cases)
    for (n, r) in [(6, 3), (6, 4), (7, 4)]:
        _, b = random_config(n, r)
        T = topes(n, r, b)
        # count topes: uniform OM has known tope count sum_{k<=r-1} C(n-1,k)*2
        expect = 2 * sum_binom(n - 1, r - 1)
        deg = tope_graph_degrees(n, r, b)
        simp = [t for t, d in deg.items() if d == r]
        mut = mutable_bases(n, r, b)
        c1 = (len(T) == expect)
        c2 = (len(simp) == 2 * len(mut))
        # basis of each simplicial tope = set of coordinates whose flip
        # stays a tope; multiset over simplicial topes = each mutable basis
        # exactly twice
        from collections import Counter
        cnt = Counter()
        for t in simp:
            Bset = tuple(sorted(i + 1 for i in range(n)
                                if t[:i] + (-t[i],) + t[i + 1:] in T))
            cnt[Bset] += 1
        mutsets = {bases_colex(n, r)[i] for i in mut}
        c3 = (set(cnt) == mutsets and all(v == 2 for v in cnt.values()))
        check(f"tope-graph mutation equivalence ({n},{r}): "
              f"topes {len(T)}=={expect}, simplicial {len(simp)}=="
              f"2*{len(mut)}, bases match", c1 and c2 and c3)

    print()
    if FAILS:
        print("FAILURES:", FAILS)
        sys.exit(1)
    print("ALL TESTS PASSED")


def sum_binom(m, k):
    from math import comb
    return sum(comb(m, j) for j in range(0, k + 1))


if __name__ == "__main__":
    main()
