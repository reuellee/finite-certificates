"""The split-orbit accounting for the capstone (stdlib, exact).

The certificate library lives at the reference chirotope chi_ref (of
U_ints) with SPECIFIC split vectors. Transporting a library item along
g = (pi, eps) in S_5 x {+-1}^5 maps (chi_ref, sigma, s) to
(g.chi_ref, g.sigma, pi.s). Because the action is transitive on the 384
uniform chirotopes, the G-orbits of pairs (chirotope, split-subset)
correspond bijectively to the orbits of Stab(chi_ref)'s permutation
image on subsets of {0..4}. This script computes, exactly:

  1. the stabilizer of chi_ref (expect order 10, faithful permutation
     image = a dihedral group D_5, i.e. the pentagon symmetries);
  2. its orbits on k-subsets for k = 0..5;
  3. which orbits are covered by the existing library splits
     ({} at k=0, {0} at k=1, {0,1} at k=2, + complements via the global
     flip (sigma,s) -> (-sigma,-s)) and which orbit still needs a sweep.

Exit code 0 iff the accounting matches the expectation above; prints the
uncovered 2-subset orbit representative that the completion sweep must
run.
"""
from __future__ import annotations

import itertools
import sys

U_INTS = [(-6, -13, 18), (-9, -12, 8), (-13, -4, 16), (4, -19, -8),
          (16, 15, -12)]
TRIPLES = list(itertools.combinations(range(5), 3))


def det3(a, b, c):
    return (a[0] * (b[1] * c[2] - b[2] * c[1])
            - a[1] * (b[0] * c[2] - b[2] * c[0])
            + a[2] * (b[0] * c[1] - b[1] * c[0]))


def sgn(x):
    return (x > 0) - (x < 0)


def chirotope(U):
    return tuple(sgn(det3(U[a], U[b], U[c])) for (a, b, c) in TRIPLES)


def perm_sign_of_sort(tup):
    """Sign of the permutation sorting tup (distinct entries)."""
    lst = list(tup)
    sign = 1
    for i in range(len(lst)):
        for j in range(i + 1, len(lst)):
            if lst[i] > lst[j]:
                lst[i], lst[j] = lst[j], lst[i]
                sign = -sign
    return sign


def act(pi, eps, chi):
    """Chirotope of U' with u'_i = eps_i * u_{pi^-1(i)}."""
    out = []
    for (a, b, c) in TRIPLES:
        pre = (pi.index(a), pi.index(b), pi.index(c))
        s = perm_sign_of_sort(pre)
        srt = tuple(sorted(pre))
        out.append(eps[a] * eps[b] * eps[c] * s * chi[TRIPLES.index(srt)])
    return tuple(out)


def main():
    chi_ref = chirotope(U_INTS)
    assert all(v != 0 for v in chi_ref), "reference configuration not generic"

    stab = []
    for pi in itertools.permutations(range(5)):
        for eps_bits in range(32):
            eps = tuple(1 if eps_bits >> i & 1 else -1 for i in range(5))
            if act(pi, eps, chi_ref) == chi_ref:
                stab.append((pi, eps))
    perms = sorted(set(g[0] for g in stab))
    ok = True
    print(f"stabilizer order: {len(stab)}   distinct permutations: {len(perms)}")
    if len(stab) != 10 or len(perms) != 10:
        ok = False

    # orbits of the permutation image on k-subsets
    def orbits(k):
        subsets = [frozenset(c) for c in itertools.combinations(range(5), k)]
        seen, out = set(), []
        for s in subsets:
            if s in seen:
                continue
            orb = set()
            stack = [s]
            while stack:
                cur = stack.pop()
                if cur in orb:
                    continue
                orb.add(cur)
                for pi in perms:
                    stack.append(frozenset(pi[i] for i in cur))
            seen |= orb
            out.append(sorted(tuple(sorted(x)) for x in orb))
        return out

    per_k = {k: orbits(k) for k in range(6)}
    for k in range(6):
        reps = [o[0] for o in per_k[k]]
        sizes = [len(o) for o in per_k[k]]
        print(f"k={k}: {len(per_k[k])} orbit(s), sizes {sizes}, reps {reps}")

    if not (len(per_k[0]) == 1 and len(per_k[1]) == 1 and len(per_k[2]) == 2
            and len(per_k[3]) == 2 and len(per_k[4]) == 1
            and len(per_k[5]) == 1):
        ok = False

    # coverage: existing library splits (as subsets A = {t : s_t = +1})
    covered = {0: [frozenset()], 1: [frozenset({0})], 2: [frozenset({0, 1})]}
    # flip (sigma,s)->(-sigma,-s) sends subset A to its complement
    full = frozenset(range(5))
    for k in (0, 1, 2):
        covered.setdefault(5 - k, []).extend(full - a for a in covered[k])

    uncovered = []
    for k in range(6):
        for orb in per_k[k]:
            hit = any(frozenset(rep) in map(frozenset, orb)
                      for rep in covered.get(k, []))
            if not hit:
                uncovered.append((k, orb[0], len(orb)))
    for (k, rep, size) in uncovered:
        print(f"UNCOVERED orbit: k={k} representative {rep} (orbit size {size})")

    # expectation: exactly one uncovered 2-subset orbit, and the uncovered
    # k=3 orbit is the one containing the complements of its members (so a
    # sweep at the 2-subset representative + the global flip closes both)
    two = [u for u in uncovered if u[0] == 2]
    three = [u for u in uncovered if u[0] == 3]
    if len(uncovered) == 2 and len(two) == 1 and len(three) == 1:
        comp = tuple(sorted(frozenset(range(5)) - frozenset(two[0][1])))
        three_orbit = next(o for o in per_k[3] if o[0] == three[0][1])
        if comp not in three_orbit:
            ok = False
    else:
        ok = False
    if ok:
        print(f"ACCOUNTING CONFIRMED: sweep needed at 2-subset split "
              f"A = {two[0][1]} (its k=3 flip partner then follows).")
    else:
        print("ACCOUNTING MISMATCH - do not proceed on these assumptions")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
