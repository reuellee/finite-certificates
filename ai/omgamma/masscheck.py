"""Mass-formula (orbit-stabilizer double counting) completeness machinery.

For a COMPLETE catalog at (n-1, r) with exact chirotope-stabilizer orders,
the number of labeled uniform chirotopes at (n, r) is

   N_chi(n,r) = sum over classes c of (n-1,r):
                   [ (n-1)! * 2^n / stab_c ] * E_c

(orbit size of the chirotope under G'_(n-1) = S_{n-1} x {0,1}^{n-1} x {0,1},
|G'| = (n-1)! 2^n, times the number of single-element extension signings of
one representative chirotope — extension counts are constant on orbits).

Independently, for any SET S of (n,r) classes:

   mass(S) = sum over c in S of  n! * 2^(n+1) / stab_c .

mass(S) <= N_chi(n,r), with equality  iff  S is the complete catalog.
This turns catalog completeness into an exact integer identity.

This module validates the machinery on levels where the catalog is known
complete, and provides the pieces for the (9,4) certificate.
"""
import sys
import time
from math import comb, factorial
from itertools import permutations

from core import from_string, g_apply, bases_colex
from canon import canonical
from extend import uniform_extensions


def catalog_masks(r, n):
    with open(f"data/cat_{r}_{n}.txt") as f:
        return [from_string(n, r, line.strip()) for line in f
                if line.strip()]


def stab_order_bruteforce(n, r, b):
    """|{g in G' : g.b == b}| by full enumeration (tiny n only)."""
    cnt = 0
    for perm in permutations(range(1, n + 1)):
        for eps in range(1 << n):
            for s in (0, 1):
                if g_apply(n, r, (perm, eps, s), b) == b:
                    cnt += 1
    return cnt


def mass_from_parents(r, n, verbose=True):
    parents = catalog_masks(r, n - 1)
    m = n - 1
    Gp = factorial(m) * (1 << (m + 1))
    total = 0
    t0 = time.time()
    for i, pm in enumerate(parents):
        res = canonical(m, r, pm)
        stab = res['stab_order_exact']
        assert Gp % stab == 0
        E = len(uniform_extensions(m, r, pm))
        total += (Gp // stab) * E
        if verbose and (i + 1) % 500 == 0:
            print(f"   parents {i+1}/{len(parents)} "
                  f"({time.time()-t0:.0f}s)", flush=True)
    return total


def mass_from_classes(r, n, verbose=True):
    cls = catalog_masks(r, n)
    Gn = factorial(n) * (1 << (n + 1))
    total = 0
    t0 = time.time()
    for i, cm in enumerate(cls):
        res = canonical(n, r, cm)
        stab = res['stab_order_exact']
        assert Gn % stab == 0
        total += Gn // stab
        if verbose and (i + 1) % 1000 == 0:
            print(f"   classes {i+1}/{len(cls)} "
                  f"({time.time()-t0:.0f}s)", flush=True)
    return total


def main():
    # canary: stab_order_exact vs brute force on tiny cases
    for (n, r) in [(5, 4), (6, 3), (6, 4)]:
        cm = catalog_masks(r, n)[0]
        so = canonical(n, r, cm)['stab_order_exact']
        bf = stab_order_bruteforce(n, r, cm)
        tag = "PASS" if so == bf else "FAIL"
        print(f"{tag} stab order exact ({n},{r}): fast {so} brute {bf}")
        if so != bf:
            sys.exit(1)

    # validate mass formula on known-complete levels
    for (r, n) in [(4, 7), (3, 7), (3, 8), (4, 8), (3, 9)]:
        a = mass_from_parents(r, n, verbose=False)
        b = mass_from_classes(r, n, verbose=(n >= 9))
        tag = "PASS" if a == b else "FAIL"
        print(f"{tag} mass formula ({r},{n}): parents {a} == classes {b}"
              f"   [labeled chirotopes = {a}, pairs = {a//2}]")
        if a != b:
            sys.exit(1)
    print("ALL MASS CHECKS PASSED")


if __name__ == "__main__":
    main()
