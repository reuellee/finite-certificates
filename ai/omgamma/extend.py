"""Single-element extensions of uniform chirotopes, and catalog generation.

Extending a uniform chirotope on [m] (rank r) by a new largest element
m+1: the child's bases inside [m] keep their signs (and colex indices);
the new bases S u {m+1} (S an (r-1)-subset of [m], colex order) get new
sign variables x_S.  Validity of the child = all 3-term GP conditions
involving m+1; each such condition is a not-all-equal constraint on three
F2-affine forms, each form involving 1 or 2 new variables plus constants
from the parent.  We enumerate all solutions by chronological backtracking.

Completeness of catalog generation: every uniform (n,r) chirotope deletes
(element n) to a uniform (n-1,r) chirotope, so every isomorphism class of
(n,r) appears among extensions of the (n-1,r) class representatives.
"""
from functools import lru_cache
from itertools import combinations
from math import comb

from core import bases_colex, basis_index, sort_sign


@lru_cache(maxsize=None)
def newvars(m, r):
    """(r-1)-subsets of [m] in colex order  (= new-basis order)."""
    vs = sorted(combinations(range(1, m + 1), r - 1),
                key=lambda t: tuple(reversed(t)))
    return tuple(vs)


@lru_cache(maxsize=None)
def extension_system(m, r):
    """Compile the constraint system for extending [m] -> [m+1].

    Returns (nv, conds_by_lastvar) where a condition is
       ((terms), ) with terms = 3 tuples (vars, const_flip) ;
       vars = tuple of new-var indices (len 1 or 2),
       const_flip = 0/1 XOR-constant *excluding* parent-sign contributions,
       plus for terms with old bases a list of parent basis indices whose
       bits get XORed in at solve time.
    Condition encoding: term parity p = XOR(newbits) ^ XOR(parentbits) ^ c;
    p==0 means term sign +1.  Condition satisfied iff not p1==p2==p3.
    """
    n = m + 1
    vidx = {S: i for i, S in enumerate(newvars(m, r))}
    pidx = basis_index(m, r)     # parent bases (subsets of [m])
    conds = []
    E = range(1, n + 1)
    for lam in combinations(E, r - 2):
        rest = [x for x in E if x not in lam]
        for quad in combinations(rest, 4):
            if n not in lam and n not in quad:
                continue
            a, bb, c, d = quad
            terms = []
            for (x, y), extra in (((a, bb), 0), ((c, d), 0),
                                  ((a, c), 1), ((bb, d), 0),
                                  ((a, d), 0), ((bb, c), 0)):
                B = lam + (x, y)
                st, sg = sort_sign(B)
                cbit = (1 if sg < 0 else 0) ^ extra
                if n in st:
                    S = tuple(e for e in st if e != n)
                    terms.append(('new', vidx[S], cbit))
                else:
                    terms.append(('old', pidx[st], cbit))
            # combine pairs (terms come in 3 pairs)
            ct = []
            for k in range(3):
                t1 = terms[2 * k]
                t2 = terms[2 * k + 1]
                nvs = []
                olds = []
                cc = t1[2] ^ t2[2]
                for t in (t1, t2):
                    if t[0] == 'new':
                        nvs.append(t[1])
                    else:
                        olds.append(t[1])
                ct.append((tuple(nvs), tuple(olds), cc))
            lastvar = max(v for (nvs, _, _) in ct for v in nvs)
            conds.append((lastvar, tuple(ct)))
    nv = len(newvars(m, r))
    by_last = {v: [] for v in range(nv)}
    for lastvar, ct in conds:
        by_last[lastvar].append(ct)
    return nv, {v: tuple(t) for v, t in by_last.items()}


def uniform_extensions(m, r, parent_mask):
    """Yield all child bitmasks on [m+1] extending parent_mask (on [m])."""
    nv, by_last = extension_system(m, r)
    base = comb(m, r)            # child bit offset for new bases
    # pre-resolve parent bits into constants
    conds_resolved = {}
    for v, cts in by_last.items():
        lst = []
        for ct in cts:
            rs = []
            for (nvs, olds, cc) in ct:
                for o in olds:
                    cc ^= (parent_mask >> o) & 1
                rs.append((nvs, cc))
            lst.append(tuple(rs))
        conds_resolved[v] = lst

    x = [0] * nv
    out = []
    v = 0
    choice = [0] * nv           # 0 = trying 0, 1 = trying 1, 2 = exhausted

    def check(v):
        for ct in conds_resolved[v]:
            ps = []
            for (nvs, cc) in ct:
                p = cc
                for u in nvs:
                    p ^= x[u]
                ps.append(p)
            if ps[0] == ps[1] == ps[2]:
                return False
        return True

    # chronological backtracking
    state = 0
    trail = [0] * nv            # next value to try at depth v
    v = 0
    while True:
        if trail[v] > 1:
            trail[v] = 0
            v -= 1
            if v < 0:
                break
            trail[v] += 1
            continue
        x[v] = trail[v]
        if check(v):
            if v == nv - 1:
                mask = 0
                for i in range(nv):
                    if x[i]:
                        mask |= 1 << (base + i)
                out.append(mask | parent_mask)
                trail[v] += 1
            else:
                v += 1
                trail[v] = 0
        else:
            trail[v] += 1
    return out


# ---------------------------------------------------------------- catalog

def build_catalog(r, n, parents, canon_fn, progress=None):
    """parents: list of canonical masks at (n-1, r).  Returns dict
    key -> canonical mask at (n, r)."""
    cat = {}
    for t, pm in enumerate(parents):
        for child in uniform_extensions(n - 1, r, pm):
            res = canon_fn(n, r, child)
            if res['can'] not in cat:
                cat[res['can']] = res['canmask']
        if progress and (t + 1) % progress == 0:
            print(f"  parent {t+1}/{len(parents)}: classes so far "
                  f"{len(cat)}", flush=True)
    return cat
