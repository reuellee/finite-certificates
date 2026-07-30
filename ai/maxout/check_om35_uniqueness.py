"""Pin the chirotope landscape at (3,5) by exhaustive computation.

Enumerates every uniform rank-3 chirotope on 5 elements (sign vectors on the
10 sorted triples satisfying all three-term Grassmann-Plucker sign
conditions), then computes orbits under the full symmetry group: relabeling
by S_5 (with permutation-parity sign action), reorientation (negating any
subset of elements), and global negation.

Why it matters (Stage 2c): "cell-wide" certificate transfer at (3,5) is
quantified over chirotope cells. This computation establishes, without
citation, exactly how many cells exist and that they form a SINGLE orbit
under the symmetries that also act on the certificate systems - so a
symbolic certificate family valid on one cell, stated equivariantly,
covers every generic configuration. (Realizability of all rank-3 oriented
matroids on <= 8 elements is classical, so there are no non-realizable
phantom cells at n = 5.)

Also verifies that the chirotope of the program's reference configuration
(U_ints from Stage 2b) satisfies the axioms and lies in the single orbit.

Stdlib only.  Usage: python check_om35_uniqueness.py
"""
import itertools
import sys

ELS = range(5)
TRIPLES = list(itertools.combinations(ELS, 3))
TIDX = {t: i for i, t in enumerate(TRIPLES)}


def chi_lookup(chi, a, b, c):
    """Sign of the ordered triple (a, b, c) given signs on sorted triples."""
    s = sorted((a, b, c))
    # parity of the permutation taking sorted -> seq
    lst = [a, b, c]
    sign = 1
    for i in range(3):
        j = lst.index(s[i], i)
        if j != i:
            lst[i], lst[j] = lst[j], lst[i]
            sign = -sign
    return sign * chi[TIDX[tuple(s)]]


def is_chirotope(chi):
    for a in ELS:
        b, c, d, e = [x for x in ELS if x != a]
        t1 = chi_lookup(chi, a, b, c) * chi_lookup(chi, a, d, e)
        t2 = chi_lookup(chi, a, b, d) * chi_lookup(chi, a, c, e)
        t3 = chi_lookup(chi, a, b, e) * chi_lookup(chi, a, c, d)
        # realizable relation: t1 - t2 + t3 = 0, so {+t1, -t2, +t3}
        # must not be all positive nor all negative
        terms = (t1, -t2, t3)
        if all(x > 0 for x in terms) or all(x < 0 for x in terms):
            return False
    return True


def relabel(chi, perm):
    out = []
    for (i, j, k) in TRIPLES:
        out.append(chi_lookup(chi, perm[i], perm[j], perm[k]))
    return tuple(out)


def reorient(chi, mask):
    out = []
    for idx, (i, j, k) in enumerate(TRIPLES):
        s = chi[idx]
        for e in (i, j, k):
            if mask >> e & 1:
                s = -s
        out.append(s)
    return tuple(out)


def orbit_of(chi, chis):
    seen = set()
    for perm in itertools.permutations(ELS):
        base = relabel(chi, perm)
        for mask in range(32):
            r = reorient(base, mask)
            seen.add(r)
            seen.add(tuple(-x for x in r))
    assert seen <= chis, "orbit left the chirotope set?!"
    return seen


def config_chi(U):
    def det3(a, b, c):
        return (a[0] * (b[1] * c[2] - b[2] * c[1])
                - a[1] * (b[0] * c[2] - b[2] * c[0])
                + a[2] * (b[0] * c[1] - b[1] * c[0]))
    out = []
    for (i, j, k) in TRIPLES:
        d = det3(U[i], U[j], U[k])
        assert d != 0
        out.append(1 if d > 0 else -1)
    return tuple(out)


def main():
    chis = {c for c in itertools.product((-1, 1), repeat=10) if is_chirotope(c)}
    print(f"uniform rank-3 chirotopes on 5 elements: {len(chis)}")
    rep = next(iter(chis))
    orb = orbit_of(rep, chis)
    single = orb == chis
    print(f"orbit of one representative under S5 x reorientation x negation: "
          f"{len(orb)} -> single orbit: {single}")

    U_ints = [(-6, -13, 18), (-9, -12, 8), (-13, -4, 16),
              (4, -19, -8), (16, 15, -12)]
    c1 = config_chi(U_ints)
    ok1 = c1 in chis
    print(f"U_ints chirotope is a valid uniform chirotope in the orbit: {ok1}")

    if not (single and ok1):
        print("FAIL")
        sys.exit(1)
    print("PASS: exactly one reorientation class at (3,5); equivariantly "
          "stated cell-wide certificates cover every generic configuration")
    sys.exit(0)


if __name__ == "__main__":
    main()
