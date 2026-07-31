"""Canonicalization of uniform chirotopes under G = S_n x {0,1}^n x {0,1}.

Canonical form (matches Finschi's RevLex-Index convention): the
lexicographically MAXIMAL sign string ('+' > '-') over the group orbit,
bases in colex order.  Works on chirotope PAIRS {chi,-chi} automatically
because global negation s is part of the group.

Encoding: "canonint" = integer with bit (M-1-j) = 1 iff string char j is
'+'.  Then integer comparison == lexicographic string comparison.

Algorithm: place new labels 1..n one level at a time.
  * A DFS state is just the tuple of original elements placed so far
    (occupying new positions 1..k).  Sign choices are NOT branched:
    for a fixed partial relabeling the set of achievable prefixes is an
    affine F2 space  raw + span(L_k), and its lex-max is computed greedily
    against a precomputed echelon basis of L_k (columns: reorientation of
    new positions 1..k, plus global negation; rows: bases inside [k]).
  * At each level only the states achieving the maximal sign-maxed prefix
    survive (lex-prefix domination makes this sound and complete).
  * Element invariants (mutation-degree profiles refined WL-style) give an
    ordered coloring; positions are pre-assigned to color blocks, states
    must respect blocks.  Invariants are reorientation/negation-invariant
    and relabel-equivariant, so this is canonical.

Returns (canonint, witness g, stabilizer generators, color signature).
witness g satisfies  g . chi = chi_canonical  (exactly, as chirotopes).
"""
from functools import lru_cache
from itertools import combinations

from core import (bases_colex, basis_index, mutable_bases, g_compose,
                  g_inverse, g_apply, to_string, from_string)


# ---------------------------------------------------------------- helpers

@lru_cache(maxsize=None)
def _prefix_counts(n, r):
    """pc[k] = number of bases contained in [k] = C(k,r)."""
    from math import comb
    return tuple(comb(k, r) for k in range(n + 1))


@lru_cache(maxsize=None)
def _colex_within(n, r):
    """For each k, list of bases inside [k] in colex order = first C(k,r)
    bases of bases_colex(k... but with labels 1..k as subset of 1..n: the
    colex order restricted is just bases_colex(n,r) filtered to max<=k,
    which equals the first C(k,r) entries."""
    return bases_colex(n, r)


@lru_cache(maxsize=None)
def _level_new_bases(n, r):
    """new_bases[k] = list of (basis, colex position j) for bases whose max
    element is exactly k (these are the chars added at level k). Positions
    are global colex indices; they occupy slots pc[k-1]..pc[k]-1."""
    pc = _prefix_counts(n, r)
    out = {k: [] for k in range(1, n + 1)}
    for j, B in enumerate(bases_colex(n, r)):
        out[B[-1]].append((B, j))
    # sanity: contiguous slots
    for k in range(1, n + 1):
        lst = out[k]
        assert [j for _, j in lst] == list(range(pc[k - 1], pc[k]))
    return out


@lru_cache(maxsize=None)
def _sign_echelons(n, r):
    """For each level k: reduced echelon basis (list of ints, canonint
    encoding restricted to prefix of length pc[k]) of the span of
    { column of eps_i (i=1..k), global negation }, over the prefix rows.

    canonint encoding for a prefix of length P: bit (P-1-j) = char j.
    Each echelon vector also carries its (eps,s) label for witness
    tracking: list of (vec, eps_bits, s_bit).
    """
    pc = _prefix_counts(n, r)
    bs = bases_colex(n, r)
    res = {}
    for k in range(r, n + 1):
        P = pc[k]
        cols = []
        for i in range(1, k + 1):
            v = 0
            for j in range(P):
                if i in bs[j]:
                    v |= 1 << (P - 1 - j)
            cols.append((v, 1 << (i - 1), 0))
        cols.append(((1 << P) - 1, 0, 1))       # global negation flips all
        # gaussian elimination to reduced echelon (over F2), high bits first
        ech = []
        for v, e, s in cols:
            for w, we, ws in ech:
                if v & (w & -w if False else 0):
                    pass
            # reduce v by existing pivots
            for w, we, ws in ech:
                p = w.bit_length() - 1
                if (v >> p) & 1:
                    v ^= w
                    e ^= we
                    s ^= ws
            if v:
                ech.append((v, e, s))
                ech.sort(key=lambda t: -t[0].bit_length())
        # back-substitute to reduced form
        ech2 = []
        for idx in range(len(ech)):
            v, e, s = ech[idx]
            for w, we, ws in ech[idx + 1:]:
                p = w.bit_length() - 1
                if (v >> p) & 1:
                    v ^= w
                    e ^= we
                    s ^= ws
            ech2.append((v, e, s))
        res[k] = tuple(ech2)
    return res


def _affine_max(vec, ech):
    """lex-max of vec + span(ech); returns (maxvec, eps, s) witness."""
    e_acc = 0
    s_acc = 0
    for w, we, ws in ech:
        p = w.bit_length() - 1
        if not (vec >> p) & 1:
            vec ^= w
            e_acc ^= we
            s_acc ^= ws
    return vec, e_acc, s_acc


def _affine_max_novit(vec, ech):
    for w, _, _ in ech:
        p = w.bit_length() - 1
        if not (vec >> p) & 1:
            vec ^= w
    return vec


# ---------------------------------------------------------------- invariants

def element_colors(n, r, b, rounds=3):
    """Reorientation/negation-invariant, relabel-equivariant coloring.

    Base data: for each element i, deg(i) = #mutable bases containing i;
    for each pair, m2(i,j) = #mutable bases containing both.
    Refined WL-style `rounds` times on the complete graph weighted by m2.
    Returns list color[i-1] = hashable color value.
    """
    mut = mutable_bases(n, r, b)
    bs = bases_colex(n, r)
    deg = [0] * (n + 1)
    m2 = [[0] * (n + 1) for _ in range(n + 1)]
    for i in mut:
        B = bs[i]
        for x in B:
            deg[x] += 1
        for x, y in combinations(B, 2):
            m2[x][y] += 1
            m2[y][x] += 1
    col = {i: (deg[i],) for i in range(1, n + 1)}
    for _ in range(rounds):
        newcol = {}
        for i in range(1, n + 1):
            sig = tuple(sorted((m2[i][j],) + col[j]
                               for j in range(1, n + 1) if j != i))
            newcol[i] = (col[i], sig)
        # compress
        vals = sorted(set(newcol.values()))
        rank = {v: t for t, v in enumerate(vals)}
        col2 = {i: (rank[newcol[i]],) for i in range(1, n + 1)}
        if len(set(col2.values())) == len(set(col.values())):
            col = col2
            break
        col = col2
    # attach raw degree so color VALUES are iso-invariant (compressed ranks
    # alone are fine since ordering of ranks is by invariant data).
    return [col[i] for i in range(1, n + 1)], len(set(col.values()))


# ---------------------------------------------------------------- canonical

def canonical(n, r, b, want_witness=True, max_stab=4096, use_colors=True):
    """Canonical form of the chirotope-pair of bitmask b.

    Returns dict with:
      'can'   : canonint of canonical string
      'canmask': core bitmask (bit i = basis i) of canonical chirotope
      'g'     : witness (sig,eps,s) with g.b == canonical  (if wanted)
      'stab'  : list of generators (as full triples) of the stabilizer of
                the canonical PAIR inside G (bounded by max_stab)
      'ncolors': number of invariant colors (diagnostics)
    """
    M = len(bases_colex(n, r))
    pc = _prefix_counts(n, r)
    newb = _level_new_bases(n, r)
    ech = _sign_echelons(n, r)
    bidx = basis_index(n, r)

    if use_colors:
        colors, ncol = element_colors(n, r, b)
    else:
        colors, ncol = [(0,)] * n, 1
    # NOTE: with use_colors=True the result is a canonical orbit key (max
    # over color-respecting relabelings) but NOT necessarily the global
    # max-string; with use_colors=False it is the literal Finschi RevLex
    # representative (lex-max string over the whole group), slower.
    # order color blocks: (size asc, color value) — iso-invariant ordering
    from collections import defaultdict
    blocks = defaultdict(list)
    for i in range(1, n + 1):
        blocks[colors[i - 1]].append(i)
    order = sorted(blocks, key=lambda c: (len(blocks[c]), c))
    # positions 1..n assigned to blocks in this order
    pos_block = []
    for c in order:
        pos_block += [c] * len(blocks[c])

    # DFS levels; state = tuple of original elements at positions 1..k
    # raw prefix value of a state: computed incrementally; store alongside
    states = [((), 0)]      # (placed tuple, raw canonint of prefix pc[k])
    for k in range(1, n + 1):
        blk = pos_block[k - 1]
        cand = blocks[blk]
        P_old = pc[k - 1]
        P_new = pc[k]
        newchars = newb[k]          # list of (basis(with new labels), j)
        nc = len(newchars)
        best = -1
        newstates = []
        for placed, raw in states:
            used = set(placed)
            for o in cand:
                if o in used:
                    continue
                # evaluate new chars: basis B (new labels, max = k):
                # char = chi(orig images of B) with sign of sorting
                add = 0
                pl = placed + (o,)
                okflag = True
                for B, j in newchars:
                    tup = tuple(pl[x - 1] for x in B)
                    # sort with sign
                    t = list(tup)
                    sg = 1
                    for a1 in range(1, len(t)):
                        a2 = a1
                        while a2 > 0 and t[a2 - 1] > t[a2]:
                            t[a2 - 1], t[a2] = t[a2], t[a2 - 1]
                            sg = -sg
                            a2 -= 1
                    v = (b >> bidx[tuple(t)]) & 1
                    if sg < 0:
                        v ^= 1
                    add = (add << 1) | v
                # raw prefix for new state
                raw2 = (raw << nc) | add
                if k >= r:
                    mx = _affine_max_novit(raw2, ech[k])
                else:
                    mx = raw2      # no bases yet; all equal (=0)
                if mx > best:
                    best = mx
                    newstates = [(pl, raw2)]
                elif mx == best:
                    newstates.append((pl, raw2))
        states = newstates
        if not states:
            raise RuntimeError("empty frontier (bug)")

    # finalize: all states achieve the same sign-maxed full string `best`
    can = best
    out = {'can': can, 'ncolors': ncol, 'nstates': len(states)}
    # exact stabilizer order in G' = S_n x {0,1}^n x {0,1}:
    #   |ExactStab(chi_can)| = |sign kernel| * #states   (each state = one
    #   achieving sigma; the achieving (eps,s) per sigma form a coset of
    #   the sign kernel, which has 2^(#dependent columns) elements).
    out['stab_order_exact'] = (1 << len(_sign_kernel(n, r))) * len(states)
    # convert canonint -> core bitmask
    cm = 0
    for j in range(M):
        if (can >> (M - 1 - j)) & 1:
            cm |= 1 << j
    out['canmask'] = cm

    if want_witness:
        wits = []
        seen_g = set()
        for placed, raw in states:
            _, eps, s = _affine_max(raw, ech[n])
            # sigma: original element placed[p-1] -> new label p
            sig = [0] * n
            for p, o in enumerate(placed, start=1):
                sig[o - 1] = p
            g = (tuple(sig), eps, s)
            if g not in seen_g:
                seen_g.add(g)
                wits.append(g)
                if len(wits) >= max_stab:
                    break
        # also kernel of full-level sign system contributes stabilizing
        # sign-only elements: any (eps,s) with L(eps,s)=0 fixes the string
        # for the SAME sigma.  Compute kernel basis cheaply: full columns.
        kern = _sign_kernel(n, r)
        g0 = wits[0]
        g0i = g_inverse(n, g0)
        stab = []
        for g in wits[1:]:
            stab.append(g_compose(n, g, g0i))
        for (eps, s) in kern:
            if eps != 0 or s != 0:
                u = (tuple(range(1, n + 1)), eps, s)
                # u fixes EVERY chirotope string?  L(eps,s)=0 means the
                # transformation changes no basis sign: acts trivially.
                stab.append(u)
        out['g'] = g0
        out['stab'] = stab
    return out


@lru_cache(maxsize=None)
def _sign_kernel(n, r):
    """Basis of {(eps,s): reorientation eps + global s changes NO basis
    sign} (the kernel K of the sign action; central)."""
    bs = bases_colex(n, r)
    M = len(bs)
    # build matrix rows: for each (eps_i) column i and s column
    cols = []
    for i in range(1, n + 1):
        v = 0
        for j, B in enumerate(bs):
            if i in B:
                v |= 1 << j
        cols.append((v, 1 << (i - 1), 0))
    cols.append(((1 << M) - 1, 0, 1))
    # kernel via gaussian elimination tracking combinations
    ech = []
    kern = []
    for v, e, s in cols:
        for w, we, ws in ech:
            p = w.bit_length() - 1
            if (v >> p) & 1:
                v ^= w
                e ^= we
                s ^= ws
        if v:
            ech.append((v, e, s))
        else:
            kern.append((e, s))
    return tuple(kern)


# ---------------------------------------------------------------- slow ref

def canonical_maxstring_bruteforce(n, r, b):
    """Reference: literal max over the whole group.  Only for tiny n."""
    from itertools import permutations
    best = -1
    M = len(bases_colex(n, r))
    for perm in permutations(range(1, n + 1)):
        for eps in range(1 << n):
            for s in (0, 1):
                b2 = g_apply(n, r, (perm, eps, s), b)
                # canonint
                ci = 0
                for j in range(M):
                    if (b2 >> j) & 1:
                        ci |= 1 << (M - 1 - j)
                if ci > best:
                    best = ci
    return best


def canonint_to_string(n, r, can):
    M = len(bases_colex(n, r))
    return ''.join('+' if (can >> (M - 1 - j)) & 1 else '-'
                   for j in range(M))
