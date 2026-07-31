"""Which sign parts can the holonomy subgroup H have?

Setting (OMGAMMA.md Sec. 2/3).  Gbar = G'/K4 has sign subgroup
Rbar = {0,1}^n / <1^n>  (order 2^(n-1)), and Gbar/Rbar = S_n via pi.
For a subgroup H <= Gbar put S := H cap Rbar (the "sign part").  Since
Rbar is normal, S is normal in H, and conjugation by h in H with
pi(h) = sigma acts on a pure sign element by
    (sigma,delta,s)(id,eps,0)(sigma,delta,s)^{-1} = (id, sigma(eps))
(direct computation with the project's composition rule).  Hence S is
invariant under pi(H).  If pi(H) = S_n then S is an F_2[S_n]-submodule of
Rbar = F_2^n/<1^n>.

The code tracks S by the lift U <= F_2^n, U = preimage of S, which always
contains 1^n (SignSpace is seeded with it); the reported "sign d/n" is
dim U, so dim S = dim U - 1 and [Rbar : S] = 2^(n-1-dim S) = 2^(n-dim U).
With pi(H) = S_n one gets  #components(Gamma_bar) = [Gbar : H]
= [Rbar : S] = 2^(n - dim U).

This script enumerates, by brute force, ALL S_n-invariant subspaces of
F_2^n (n = 5..10) and reports which contain 1^n -- i.e. exactly the
possible values of U.  Two independent methods + a canary:

  M1  every S_n-invariant subspace is the sum of the spans of the S_n
      ORBITS of its elements, and the orbits of S_n on F_2^n are exactly
      the n+1 weight classes; so the invariant subspaces are exactly the
      2^(n+1) sums  sum_{w in W} span(weight-w vectors),  W subset of
      {0..n}  (deduplicated).
  M2  (n <= 7) enumerate ALL subspaces of F_2^n via their unique reduced
      row echelon forms and filter by invariance under the generators
      (1 2) and (1 2 ... n).  The counts must equal the Galois numbers.
  canary: a deliberately NON-invariant subspace (span of e_1) must be
      rejected by the invariance test, and M1's list must not contain it.

Usage: python submodules.py [outfile.json]
"""
import json
import sys
from itertools import combinations


def perm_act(n, sigma, v):
    """sigma acts by moving bit i to bit sigma(i) (sigma 0-based list)."""
    w = 0
    for i in range(n):
        if (v >> i) & 1:
            w |= 1 << sigma[i]
    return w


def span(vecs):
    """Gaussian basis (dict pivot -> vector) of the span."""
    basis = {}
    for v in vecs:
        x = v
        while x:
            p = x.bit_length() - 1
            if p in basis:
                x ^= basis[p]
            else:
                basis[p] = x
                break
    return basis


def reduce_basis(basis):
    """Back-substitute to the UNIQUE reduced echelon basis, so that
    `canon(basis)` identifies a subspace."""
    piv = sorted(basis, reverse=True)
    vecs = {p: basis[p] for p in piv}
    for i, p in enumerate(piv):
        for q in piv[i + 1:]:
            if (vecs[p] >> q) & 1:
                vecs[p] ^= vecs[q]
    return vecs


def canon(basis):
    return tuple(sorted(reduce_basis(basis).values()))


def in_span(basis, v):
    x = v
    while x:
        p = x.bit_length() - 1
        if p not in basis:
            return False
        x ^= basis[p]
    return True


def elements(basis, n):
    """All vectors of the subspace."""
    bs = sorted(basis.values())
    out = [0]
    for b in bs:
        out += [x ^ b for x in out]
    return sorted(set(out))


def gens_Sn(n):
    """(1 2) and the n-cycle, as 0-based image lists."""
    t = list(range(n))
    t[0], t[1] = t[1], t[0]
    c = [(i + 1) % n for i in range(n)]
    return [t, c]


def is_invariant(n, basis):
    for sigma in gens_Sn(n):
        for v in list(basis.values()):
            if not in_span(basis, perm_act(n, sigma, v)):
                return False
    return True


# ------------------------------------------------------------------ M1

def weight_orbit_spans(n):
    out = {}
    for w in range(n + 1):
        vecs = []
        for S in combinations(range(n), w):
            v = 0
            for i in S:
                v |= 1 << i
            vecs.append(v)
        out[w] = span(vecs)
    return out


def m1_invariant_subspaces(n):
    ws = weight_orbit_spans(n)
    seen = {}
    for mask in range(1 << (n + 1)):
        vecs = []
        for w in range(n + 1):
            if (mask >> w) & 1:
                vecs += list(ws[w].values())
        b = span(vecs)
        seen[canon(b)] = b
    return list(seen.values())


# ------------------------------------------------------------------ M2

def all_subspaces_rref(n):
    """Every subspace of F_2^n exactly once, via reduced row echelon form.
    Choose pivot columns P (as a sorted tuple, columns 0..n-1 read as bit
    positions n-1..0 is irrelevant -- any fixed convention works); free
    entries are the positions right of a pivot that are not pivots."""
    for k in range(n + 1):
        for piv in combinations(range(n), k):
            free = [c for c in range(n) if c not in piv]
            # for row i (pivot piv[i]) the free positions allowed are the
            # free columns AFTER piv[i]
            slots = [[c for c in free if c > piv[i]] for i in range(k)]
            total = sum(len(s) for s in slots)
            for bits in range(1 << total):
                rows = []
                off = 0
                for i in range(k):
                    v = 1 << (n - 1 - piv[i])
                    for t, c in enumerate(slots[i]):
                        if (bits >> (off + t)) & 1:
                            v |= 1 << (n - 1 - c)
                    off += len(slots[i])
                    rows.append(v)
                yield span(rows)


GALOIS = {0: 1, 1: 2, 2: 5, 3: 16, 4: 67, 5: 374, 6: 2825, 7: 29212,
          8: 417199, 9: 8283458}


def main(outfile=None):
    report = {}
    ok = True
    for n in range(5, 11):
        inv = m1_invariant_subspaces(n)
        dims = sorted(len(b) for b in inv)
        full = (1 << n) - 1
        withone = sorted(len(b) for b in inv if in_span(b, full))
        # invariance of everything M1 produced (self-check)
        for b in inv:
            if not is_invariant(n, b):
                print(f"  !! M1 produced a NON-invariant subspace at n={n}")
                ok = False
        report[n] = {'m1_count': len(inv), 'm1_dims': dims,
                     'dims_containing_all_ones': withone,
                     'components_if_pi_full': [1 << (n - d)
                                               for d in withone]}
        print(f"n={n}: {len(inv)} S_n-invariant subspaces of F_2^n, "
              f"dims {dims}")
        print(f"       containing 1^n: dims {withone} -> "
              f"#components(Gamma_bar) in "
              f"{[1 << (n - d) for d in withone]}")
        if n <= 7:
            cnt = 0
            m2 = []
            for b in all_subspaces_rref(n):
                cnt += 1
                if is_invariant(n, b):
                    m2.append(canon(b))
            m2 = sorted(set(m2))
            m1 = sorted({canon(b) for b in inv})
            agree = (m1 == m2)
            report[n]['m2_total_subspaces'] = cnt
            report[n]['m2_galois_ok'] = (cnt == GALOIS[n])
            report[n]['m1_equals_m2'] = agree
            print(f"       M2: {cnt} subspaces total "
                  f"(Galois number {GALOIS[n]}: "
                  f"{'ok' if cnt == GALOIS[n] else 'MISMATCH'}), "
                  f"{len(m2)} invariant; M1==M2: {agree}")
            ok &= agree and cnt == GALOIS[n]
        # canary: span(e_1) is not invariant for n >= 2, and must not be
        # in the M1 list
        can = span([1])
        if is_invariant(n, can):
            print("  !! CANARY FAILED: span(e_1) declared invariant")
            ok = False
        if canon(can) in {canon(b) for b in inv}:
            print("  !! CANARY FAILED: span(e_1) present in M1 list")
            ok = False
    report['canary'] = 'span(e_1) rejected as non-invariant at every n'
    report['all_checks_passed'] = bool(ok)
    print("\nALL CHECKS PASSED" if ok else "\nCHECK FAILURE")
    if outfile:
        with open(outfile, 'w') as f:
            json.dump(report, f, indent=1)
        print("wrote", outfile)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else None))
