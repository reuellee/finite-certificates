"""Tests for extend.py: brute-force anchors + small catalog counts."""
import sys
from math import comb

from core import (bases_colex, is_uniform_chirotope, from_string, to_string)
from extend import uniform_extensions, build_catalog, newvars
from canon import canonical
from test_core import IC74, random_config

FAILS = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        FAILS.append(name)


def brute_extensions(m, r, parent_mask):
    base = comb(m, r)
    nv = len(newvars(m, r))
    n = m + 1
    out = []
    for xbits in range(1 << nv):
        child = parent_mask | (xbits << base)
        if is_uniform_chirotope(n, r, child):
            out.append(child)
    return out


def main():
    # 1. brute force agreement
    for (m, r) in [(5, 3), (5, 4), (6, 4)]:
        _, pm = random_config(m, r)
        bf = set(brute_extensions(m, r, pm))
        fa = set(uniform_extensions(m, r, pm))
        check(f"extensions brute == solver ({m},{r})->({m+1},{r}) "
              f"[{len(fa)} exts]", bf == fa)
        ok = all(is_uniform_chirotope(m + 1, r, c) for c in fa)
        check(f"all solver extensions valid ({m},{r})", ok)

    # 2. catalog ladder rank 4: n=5,6,7 -> 1,1,11; rank 3: n=5,6,7 -> 1,4,11
    canon_fn = lambda n, r, b: canonical(n, r, b, want_witness=False)
    for r, counts in [(4, {5: 1, 6: 1, 7: 11}), (3, {5: 1, 6: 4, 7: 11})]:
        # start from n=r: single class, all-plus (one basis)
        cat = {0: (1 << comb(r, r)) - 1}   # mask with the one basis +
        parents = list(cat.values())
        ok_all = True
        for n in range(r + 1, 8):
            cat = build_catalog(r, n, parents, canon_fn)
            parents = list(cat.values())
            if n in counts:
                got = len(cat)
                if got != counts[n]:
                    ok_all = False
                    print(f"   ({n},{r}): got {got}, expected {counts[n]}")
        check(f"catalog counts rank {r} up to n=7 match Finschi", ok_all)

    # 3. (7,4) catalog classes match Finschi's 11 exactly (as orbit keys)
    cat = {0: (1 << 1) - 1}
    parents = [(1 << 1) - 1]
    for n in range(5, 8):
        cat = build_catalog(4, n, parents, canon_fn)
        parents = list(cat.values())
    mykeys = set(cat.keys())
    fkeys = {canonical(7, 4, from_string(7, 4, s), want_witness=False)['can']
             for s in IC74}
    check("(7,4): my 11 classes == Finschi's 11 classes (key sets equal)",
          mykeys == fkeys)

    # 4. CANARY: corrupt one parent sign (invalid parent) -> solver output
    # children must fail validity (extension solver assumes valid parent;
    # a corrupted parent must be caught by downstream validity checks)
    _, pm = random_config(6, 4)
    bad = pm ^ 1  # flip basis 0; may or may not stay valid; find truly bad
    from core import mutable_bases
    nonmut = [i for i in range(comb(6, 4))
              if i not in set(mutable_bases(6, 4, pm))]
    bad = pm ^ (1 << nonmut[0])
    kids = uniform_extensions(6, 4, bad)
    badkid = any(not is_uniform_chirotope(7, 4, c) for c in kids) or \
        len(kids) == 0
    check("canary: corrupted parent yields invalid/no children "
          f"({len(kids)} children)", badkid)

    print()
    if FAILS:
        print("FAILURES:", FAILS)
        sys.exit(1)
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
