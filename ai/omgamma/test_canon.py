"""Tests for canon.py.  Run: python test_canon.py"""
import random
import sys
import os

from core import (bases_colex, from_string, to_string, g_apply,
                  is_uniform_chirotope)
from canon import (canonical, canonical_maxstring_bruteforce,
                   canonint_to_string)
from parse_finschi import parse_ic_strings
from test_core import IC74, random_config

random.seed(4242)
FAILS = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def rand_g(n):
    sg = list(range(1, n + 1))
    random.shuffle(sg)
    return (tuple(sg), random.getrandbits(n), random.getrandbits(1))


def main():
    # 1. brute force agreement on tiny cases
    for (n, r), trials in [((5, 4), 2), ((6, 3), 2), ((6, 4), 2)]:
        ok = True
        for _ in range(trials):
            _, b = random_config(n, r)
            bf = canonical_maxstring_bruteforce(n, r, b)
            fa = canonical(n, r, b, use_colors=False)['can']
            if bf != fa:
                ok = False
        check(f"brute force == fast canonical ({n},{r})", ok)

    # 2. Finschi anchors: IC(7,4,*) are fixed points, distinct, and stable
    cans = []
    ok_fp = ok_wit = ok_stab = True
    for s in IC74:
        b = from_string(7, 4, s)
        res = canonical(7, 4, b, use_colors=False)
        cs = canonint_to_string(7, 4, res['can'])
        if cs != s:
            ok_fp = False
            print("   rep not fixed:", s, "->", cs)
        cans.append(res['can'])
        if g_apply(7, 4, res['g'], b) != res['canmask']:
            ok_wit = False
        for u in res['stab']:
            if g_apply(7, 4, u, res['canmask']) != res['canmask']:
                ok_stab = False
    check("IC(7,4,*) are fixed points of canonicalization", ok_fp)
    check("witness g maps chi to canonical", ok_wit)
    check("stabilizer elements fix canonical chirotope", ok_stab)
    check("11 canonical forms distinct", len(set(cans)) == 11)

    # 3. random transforms land on the same canonical form
    ok = True
    for s in IC74:
        b = from_string(7, 4, s)
        c0 = canonical(7, 4, b)['can']
        for _ in range(6):
            g = rand_g(7)
            b2 = g_apply(7, 4, g, b)
            if canonical(7, 4, b2)['can'] != c0:
                ok = False
    check("canonical invariant under random group elements (7,4)", ok)

    # 4. (8,3) Finschi anchors: 135 reps are fixed points and distinct
    here = os.path.dirname(os.path.abspath(__file__))
    ics = parse_ic_strings(os.path.join(here, "data", "om_83.html"))
    ics = [t for t in ics if t[0] == 8 and t[1] == 3]
    check("parsed 135 IC(8,3,*) strings", len(ics) == 135)
    ok_fp = True
    cans = set()
    for (_, _, k, s) in ics:
        b = from_string(8, 3, s)
        if not is_uniform_chirotope(8, 3, b):
            ok_fp = False
            print("   invalid rep", k)
        res = canonical(8, 3, b, want_witness=False)
        cans.add(res['can'])
    check("all 135 IC(8,3,*) valid", ok_fp)
    ok_fx = True
    for (_, _, k, s) in ics[::17]:
        b = from_string(8, 3, s)
        res = canonical(8, 3, b, want_witness=False, use_colors=False)
        if canonint_to_string(8, 3, res['can']) != s:
            ok_fx = False
            print("   not fixed:", k)
    check("subset of IC(8,3,*) are fixed points of true max-string", ok_fx)
    check("135 canonical forms distinct", len(cans) == 135)

    # 5. transform-stability on a few (8,3) classes and random (8,4),(9,4)
    ok = True
    for (_, _, k, s) in ics[::40]:
        b = from_string(8, 3, s)
        c0 = canonical(8, 3, b, want_witness=False)['can']
        for _ in range(4):
            b2 = g_apply(8, 3, rand_g(8), b)
            if canonical(8, 3, b2, want_witness=False)['can'] != c0:
                ok = False
    check("canonical stable under transforms (8,3)", ok)

    ok = True
    import time
    t0 = time.time()
    cnt = 0
    for (n, r) in [(8, 4), (9, 4)]:
        for _ in range(3):
            _, b = random_config(n, r)
            res = canonical(n, r, b)
            if g_apply(n, r, res['g'], b) != res['canmask']:
                ok = False
            c0 = res['can']
            for _ in range(3):
                b2 = g_apply(n, r, rand_g(n), b)
                if canonical(n, r, b2, want_witness=False)['can'] != c0:
                    ok = False
                cnt += 1
    dt = time.time() - t0
    check(f"canonical stable under transforms (8,4),(9,4) "
          f"[{cnt+6} canonicalizations in {dt:.1f}s]", ok)

    print()
    if FAILS:
        print("FAILURES:", FAILS)
        sys.exit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
