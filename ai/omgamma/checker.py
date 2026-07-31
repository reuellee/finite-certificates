"""STANDALONE certificate checker for the mutation-graph connectivity
results.  Shares NO code with the generator (independent implementations
of chirotope validity, the group action, and group-generation tests,
written directly from the definitions).

Certificate contents for (n, r):
  reps   : one +/- string per class (colex basis order), class id = line no
  tree   : lines "cid root" or "cid parent flipidx sigma eps s"
  gens   : lines "prov... sigma eps s"  where prov is 'stab|cid' or
           'edge|c|j|c2'
  exhibits: lines "eps w1,w2,..."  (word over gen indices, negative =
           inverse, leftmost factor outermost)

What is verified (everything in exact integer arithmetic):
  V1 every representative satisfies the uniform 3-term Grassmann-Pluecker
     conditions  (independent implementation from the axiom);
  V2 every tree edge: flipping basis j of rep[parent] yields EXACTLY
     +-(sigma,eps,s).rep[child]  — hence a genuine mutation edge of the
     labeled graph, and the tree spans all listed classes;
  V3 every generator h: its provenance identity holds
     ('stab': (tau_c^-1 h tau_c). rep[c] = +-rep[c];
      'edge': rep[c] xor bit_j = +-(tau_c^-1 h tau_c2).rep[c2]),
     with the transports tau recomputed here from the tree;
  V4 the permutation parts of the verified generators generate S_n
     (orbit-stabilizer chain computed here from scratch);
  V5 the exhibit words compose (here) to pure-sign elements whose eps
     vectors together with 1^n span F_2^n.

Given the reduction theorem (OMGAMMA.md Sec. 3) and the completeness of
the class list (trust boundary: mass identity + published counts), V1-V5
certify: Gamma_hat connected, and H = Gbar, hence Gamma_bar (labeled) and
Gamma_tilde (reorientation classes) are connected.

Usage:  python checker.py <n> <r> <repsfile> <treefile> <gensfile> \
            <exhibitsfile>
Exit 0 iff all checks pass.
"""
import sys
from itertools import combinations
from math import comb, factorial


# ----------------------------------------------------------- independent core

def colex_bases(n, r):
    bs = sorted(combinations(range(1, n + 1), r),
                key=lambda B: tuple(sorted(B, reverse=True)))
    return bs


def parity_sorting(t):
    """(-1)^(number of inversions); 0 on repeats."""
    if len(set(t)) < len(t):
        return 0
    inv = 0
    for i in range(len(t)):
        for j in range(i + 1, len(t)):
            if t[i] > t[j]:
                inv += 1
    return -1 if inv & 1 else 1


class Chk:
    def __init__(self, n, r):
        self.n = n
        self.r = r
        self.bases = colex_bases(n, r)
        self.M = len(self.bases)
        self.idx = {B: i for i, B in enumerate(self.bases)}

    def parse(self, s):
        assert len(s) == self.M and set(s) <= {'+', '-'}, "bad rep string"
        return [1 if c == '+' else -1 for c in s]

    def value(self, chi, tup):
        sg = parity_sorting(tup)
        if sg == 0:
            return 0
        return sg * chi[self.idx[tuple(sorted(tup))]]

    def gp_valid(self, chi):
        """All uniform 3-term GP conditions, straight from the axiom:
        for lam (r-2 elements) and a<b<c<d disjoint: the set
        {chi(lam,a,b)chi(lam,c,d), -chi(lam,a,c)chi(lam,b,d),
         chi(lam,a,d)chi(lam,b,c)} contains +1 and -1."""
        n, r = self.n, self.r
        E = range(1, n + 1)
        for lam in combinations(E, r - 2):
            rest = [x for x in E if x not in lam]
            for a, b, c, d in combinations(rest, 4):
                t1 = self.value(chi, lam + (a, b)) * \
                    self.value(chi, lam + (c, d))
                t2 = -self.value(chi, lam + (a, c)) * \
                    self.value(chi, lam + (b, d))
                t3 = self.value(chi, lam + (a, d)) * \
                    self.value(chi, lam + (b, c))
                s = {t1, t2, t3}
                if not (1 in s and -1 in s):
                    return False
        return True

    def act(self, g, chi):
        """(sigma,eps,s).chi as a list, independent implementation:
        new(B) = (-1)^s (-1)^{|eps cap B|} chi(sigma^-1 B) with sorting
        parity."""
        sig, eps, s = g
        n, r = self.n, self.r
        inv = [0] * (n + 1)
        for i in range(1, n + 1):
            inv[sig[i - 1]] = i
        out = [0] * self.M
        for i, B in enumerate(self.bases):
            pre = tuple(inv[x] for x in B)
            sg = parity_sorting(pre)
            v = sg * chi[self.idx[tuple(sorted(pre))]]
            e = sum(1 for x in B if (eps >> (x - 1)) & 1)
            if (e + s) & 1:
                v = -v
            out[i] = v
        return out

    def compose(self, g1, g2):
        """g1 then... (g1*g2).chi = g1.(g2.chi)."""
        n = self.n
        s1, e1, x1 = g1
        s2, e2, x2 = g2
        sig = tuple(s1[s2[i] - 1] for i in range(n))
        e = e1
        for i in range(n):
            if (e2 >> i) & 1:
                e ^= 1 << (s1[i] - 1)
        return (sig, e, x1 ^ x2)

    def inverse(self, g):
        n = self.n
        sig, eps, s = g
        inv = [0] * n
        for i in range(n):
            inv[sig[i] - 1] = i + 1
        e = 0
        for i in range(n):
            if (eps >> i) & 1:
                e |= 1 << (inv[i] - 1)
        return (tuple(inv), e, s)


def group_order_from_perms(n, perms):
    """Order of <perms> <= S_n by an orbit-stabilizer chain, implemented
    from scratch (no Schreier-Sims code reuse): recursively, order =
    |orbit of point p| * |stabilizer of p|, with stabilizer generators
    obtained via Schreier's lemma (transversal products), depth n."""
    perms = [tuple(p) for p in perms if tuple(p) != tuple(range(1, n + 1))]
    if not perms:
        return 1

    def helper(gens, points):
        if not gens or not points:
            return 1
        p = points[0]
        # orbit + transversal
        orb = {p: tuple(range(1, n + 1))}
        frontier = [p]
        while frontier:
            x = frontier.pop()
            tx = orb[x]
            for g in gens:
                y = g[x - 1]
                if y not in orb:
                    # element mapping p -> y : g o tx
                    orb[y] = tuple(g[tx[i] - 1] for i in range(n))
                    frontier.append(y)
        # Schreier generators for the stabilizer of p
        inv = {}
        stab = set()
        for x, tx in orb.items():
            for g in gens:
                y = g[x - 1]
                ty = orb[y]
                tyi = [0] * n
                for i in range(n):
                    tyi[ty[i] - 1] = i + 1
                w = tuple(g[tx[i] - 1] for i in range(n))
                sgen = tuple(tyi[w[i] - 1] for i in range(n))
                if sgen != tuple(range(1, n + 1)):
                    stab.add(sgen)
        return len(orb) * helper(sorted(stab), points[1:])

    return helper(perms, list(range(1, n + 1)))


# ----------------------------------------------------------- driver

def fail(msg):
    print("CHECK FAILED:", msg)
    sys.exit(1)


def main(n, r, repsfile, treefile, gensfile, exfile):
    C = Chk(n, r)
    reps = []
    with open(repsfile) as f:
        for line in f:
            line = line.strip()
            if line:
                reps.append(C.parse(line))
    K = len(reps)
    print(f"[checker] {K} representatives loaded")

    # V1 validity
    for i, chi in enumerate(reps):
        if not C.gp_valid(chi):
            fail(f"rep {i} violates Grassmann-Pluecker")
        if i % 200 == 0:
            print(f"[checker] V1 validity ... {i}/{K}", end="\r",
                  flush=True)
    print(f"[checker] V1: all {K} representatives are uniform chirotopes")

    # tree parse
    tree = {}
    roots = []
    with open(treefile) as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            cid = int(parts[0])
            if parts[1] == 'root':
                roots.append(cid)
            else:
                p = int(parts[1])
                j = int(parts[2])
                sig = tuple(int(x) for x in parts[3].split(','))
                eps = int(parts[4])
                s = int(parts[5])
                tree[cid] = (p, j, (sig, eps, s))
    if roots != [0] or set(tree) != set(range(1, K)):
        fail("tree does not cover classes exactly once with root 0")

    # V2 edges + transports  (children reference earlier parents => order)
    tau = {0: (tuple(range(1, n + 1)), 0, 0)}
    for cid in range(1, K):
        p, j, t = tree[cid]
        if p >= cid:
            fail(f"tree not topologically ordered at {cid}")
        flipped = list(reps[p])
        flipped[j] = -flipped[j]
        img = C.act(t, reps[cid])
        if img != flipped and [-v for v in img] != flipped:
            fail(f"tree edge identity fails at class {cid}")
        tau[cid] = C.compose(tau[p], t)
        if cid % 200 == 0:
            print(f"[checker] V2 edges ... {cid}/{K}", end="\r", flush=True)
    print(f"[checker] V2: all {K-1} tree mutation edges verified; "
          "transports computed")

    # V3 generators
    gens = []
    with open(gensfile) as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            prov = parts[0].split('|')
            sig = tuple(int(x) for x in parts[1].split(','))
            eps = int(parts[2])
            s = int(parts[3])
            h = (sig, eps, s)
            if prov[0] == 'stab':
                c = int(prov[1])
                u = C.compose(C.compose(C.inverse(tau[c]), h), tau[c])
                img = C.act(u, reps[c])
                if img != reps[c] and [-v for v in img] != reps[c]:
                    fail(f"stab generator at class {c} fails")
            elif prov[0] == 'edge':
                c, j, c2 = int(prov[1]), int(prov[2]), int(prov[3])
                t = C.compose(C.compose(C.inverse(tau[c]), h), tau[c2])
                flipped = list(reps[c])
                flipped[j] = -flipped[j]
                img = C.act(t, reps[c2])
                if img != flipped and [-v for v in img] != flipped:
                    fail(f"edge generator ({c},{j},{c2}) fails")
            else:
                fail("unknown provenance " + parts[0])
            gens.append(h)
    print(f"[checker] V3: {len(gens)} holonomy generators verified")

    # V4 permutation generation
    order = group_order_from_perms(n, [g[0] for g in gens])
    if order != factorial(n):
        fail(f"perm parts generate order {order} != {factorial(n)}")
    print(f"[checker] V4: permutation parts generate S_{n} "
          f"(order {order})")

    # V5 sign exhibits
    basis = {}

    def gadd(v):
        while v:
            p = v.bit_length() - 1
            if p in basis:
                v ^= basis[p]
            else:
                basis[p] = v
                return True
        return False

    gadd((1 << n) - 1)
    with open(exfile) as f:
        for line in f:
            parts = line.split()
            if not parts:
                continue
            word = [int(x) for x in parts[1].split(',')]
            g = (tuple(range(1, n + 1)), 0, 0)
            for idx in word:
                fpart = gens[idx] if idx >= 0 else \
                    C.inverse(gens[-idx - 1])
                g = C.compose(g, fpart)
            if g[0] != tuple(range(1, n + 1)):
                fail("exhibit word is not a pure sign element")
            gadd(g[1])
            # s component: irrelevant on pairs (global negation kernel)
    if len(basis) != n:
        fail(f"sign space dimension {len(basis)} != {n}")
    print(f"[checker] V5: sign space spans F_2^{n} (incl. kernel 1^n)")

    print(f"[checker] ALL CHECKS PASSED: spanning tree over {K} classes + "
          f"holonomy generators establishing H = Gbar.")
    print("[checker] Conclusion (given the reduction theorem and the "
          "completeness of the class list): Gamma_hat, Gamma_tilde and "
          "Gamma_bar are CONNECTED for these (n, r).")
    return 0


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3],
                  sys.argv[4], sys.argv[5], sys.argv[6]))
