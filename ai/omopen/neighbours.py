#!/usr/bin/env python3
"""The neighbour source `weaponA` documents and never implemented.

`OPEN_ATTACK.md` s10 lists it as escalation step 2:

    the class-lookup neighbour source that is NOT implemented here -- T1/T2
    use only tree edges, so only the parent and already-realized children
    are available; canonicalizing each of the ~15 mutants and looking up
    its row would give every realizable neighbour, at the cost of the group
    element.

For the final residue it is the difference between one starting point and
fifteen.  The last undecided class of the (4,9) sweep, row 3992924, has
**no children in the spanning tree at all** -- its only tree neighbour is
its parent -- while it has 15 mutable bases, hence 15 mutation neighbours
in the full graph.  Fourteen of them are invisible to T1/T2.

THE GROUP ELEMENT, WITHOUT A CONVENTION
=======================================
"at the cost of the group element" is the hard part, and it is avoided
rather than paid.  Canonicalization tells us WHICH catalog row a mutant
belongs to and gives a relabelling; it does not have to tell us how to
move a matrix, because that can be solved for and then checked:

    X realizes the catalog representative chi_s.  Permute its columns by
    the placement (try the placement and its inverse).  Compute the
    permuted matrix's bracket signs s' EXACTLY.  We want column negations
    e in {0,1}^9 and a global flip g in {0,1} with

        s'(B) * (-1)^(g + sum_{i in B} e_i)  =  chi_j(B)   for all 126 B,

    which is a linear system over GF(2) in ten unknowns.  Solve it by
    elimination; negate the columns it names, negate one row if g = 1, and
    RECOMPUTE ALL 126 BRACKETS.  The result is used only if it equals
    chi_j exactly.

So no convention from `omgamma` or from `treewalk.Action` is trusted: a
wrong guess simply fails the bracket check and the neighbour is skipped.
Reorientation and global sign are exactly the transformations that act on a
realization by negating columns and rows, so the search space is complete
given the relabelling.

    python neighbours.py show --row 3992924
    python neighbours.py run  --row 3992924 --budget 3600
"""

import argparse
import json
import os
import sys
import time

sys.dont_write_bytecode = True
for _v in ('OMP_NUM_THREADS', 'MKL_NUM_THREADS', 'OPENBLAS_NUM_THREADS',
           'NUMEXPR_NUM_THREADS'):
    os.environ.setdefault(_v, '1')

import numpy as np                                          # noqa: E402

import catalog                                              # noqa: E402
import exactgate                                            # noqa: E402
import weaponA                                              # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, 'data')
N, R, M = 9, 4, 126


# ----------------------------------------------------------------------
# catalog lookup by key
# ----------------------------------------------------------------------

_IDX = {}


def key_index():
    """A sorted view of the catalog's 128-bit keys, for row lookup."""
    if not _IDX:
        a = catalog.arrays()
        cat = np.zeros(catalog.NROWS, dtype=[('hi', '<u8'), ('lo', '<u8')])
        cat['hi'] = np.asarray(a['hi'])
        cat['lo'] = np.asarray(a['lo'])
        order = np.argsort(cat, order=('hi', 'lo'))
        _IDX['order'] = order
        _IDX['sorted'] = cat[order]
    return _IDX


def row_of_key(hi, lo):
    ix = key_index()
    q = np.zeros(1, dtype=[('hi', '<u8'), ('lo', '<u8')])
    q['hi'], q['lo'] = hi, lo
    p = int(np.searchsorted(ix['sorted'], q)[0])
    if p >= catalog.NROWS:
        return -1
    if ix['sorted']['hi'][p] != hi or ix['sorted']['lo'][p] != lo:
        return -1
    return int(ix['order'][p])


# ----------------------------------------------------------------------
# GF(2) solve for the reorientation + global sign
# ----------------------------------------------------------------------

def solve_reorientation(sprime, target, bases0):
    """Find e in {0,1}^9 and g in {0,1} with
           sprime(B) * (-1)^(g + sum_{i in B} e_i) = target(B).
    Returns (e, g) or None.  Unknowns are ordered (e_0..e_8, g)."""
    nvar = N + 1
    rows = []
    for j, B in enumerate(bases0):
        mask = 0
        for i in B:
            mask |= 1 << i
        mask |= 1 << N                       # the global-sign unknown
        rhs = 0 if sprime[j] == target[j] else 1
        rows.append((mask, rhs))
    piv = {}
    for mask, rhs in rows:
        stored = False
        for c in range(nvar):
            if not (mask >> c) & 1:
                continue
            if c in piv:
                pm, pr = piv[c]
                mask ^= pm
                rhs ^= pr
            else:
                piv[c] = (mask, rhs)
                stored = True
                break
        # `mask == 0 and rhs == 1` is 0 = 1, i.e. inconsistent -- but only
        # when the row was REDUCED to nothing, not when it was just stored
        # as a pivot (which leaves the local `mask` untouched).  Getting
        # that wrong makes every system with an odd right-hand side look
        # unsolvable, which is exactly how this was found.
        if not stored and mask == 0 and rhs == 1:
            return None                      # inconsistent
    sol = [0] * nvar
    for c in sorted(piv, reverse=True):
        mask, rhs = piv[c]
        v = rhs
        for d in range(c + 1, nvar):
            if (mask >> d) & 1:
                v ^= sol[d]
        sol[c] = v
    return sol[:N], sol[N]


def apply_reorientation(X, e, g):
    """Negate the named columns; negate one row if the global sign flips."""
    W = np.array(X, dtype=np.int64).copy()
    for i, b in enumerate(e):
        if b:
            W[:, i] = -W[:, i]
    if g:
        W[0, :] = -W[0, :]
    return W


# ----------------------------------------------------------------------
# the neighbour enumeration
# ----------------------------------------------------------------------

def mutants(chi, geom):
    """Bases whose sign can be flipped keeping a valid uniform chirotope."""
    if geom.GP is None:
        geom.build_gp()
    c0 = np.asarray(chi, dtype=np.int64)

    def valid(c):
        for (i1, i2, i3, i4, i5, i6, s1, s2, s3) in geom.GP:
            t1 = s1 * c[i1] * c[i2]
            t2 = s2 * c[i3] * c[i4]
            t3 = s3 * c[i5] * c[i6]
            if t1 == t2 == t3:
                return False
        return True

    out = []
    for j in range(M):
        c = c0.copy()
        c[j] = -c[j]
        if valid(c):
            out.append((j, c.astype(np.int8)))
    return out


def _cc():
    omg = os.path.normpath(os.path.join(HERE, '..', 'omgamma'))
    if omg not in sys.path:
        sys.path.insert(0, omg)
    import coverage_checker
    return coverage_checker


def realizable_neighbours(row, chi, geom, verbose=True):
    """[(j, W)] with W an exact integer realization of the mutant mu_j(chi).

    Every W is verified: its 126 brackets must equal mu_j(chi) exactly, and
    therefore differ from chi in exactly the one position j.
    """
    cc = _cc()
    T = cc.build_tables(N, R)
    a = catalog.arrays()
    st, Z = a['st'], a['Z']

    muts = mutants(chi, geom)
    if verbose:
        print('  %d mutable bases' % len(muts))
    PSI = np.zeros((len(muts), M), dtype=np.uint8)
    for k, (j, c) in enumerate(muts):
        PSI[k] = (np.asarray(c) > 0).astype(np.uint8)
    hi, lo, nargmax, valid, npl, win_pl, win_combo = cc.canon_batch(T, PSI)

    out = []
    stats = {'mutants': len(muts), 'invalid': 0, 'no_row': 0,
             'not_realizable': 0, 'no_group_element': 0, 'ok': 0}
    for k, (j, c) in enumerate(muts):
        if not valid[k]:
            stats['invalid'] += 1
            continue
        s = row_of_key(int(hi[k]), int(lo[k]))
        if s < 0:
            stats['no_row'] += 1
            continue
        if int(st[s]) not in (catalog.WALK, catalog.REPAIR):
            stats['not_realizable'] += 1
            continue
        X = np.asarray(Z[s], dtype=np.int64)
        pl = [int(v) for v in win_pl[k]]           # 1-based placement
        perm = [v - 1 for v in pl]
        inv = [0] * N
        for i, v in enumerate(perm):
            inv[v] = i
        W = None
        for sigma in (perm, inv):
            Xp = X[:, sigma]
            sp = weaponA.rz.exact_bracket_signs(Xp, geom)
            if sp is None:
                continue
            r = solve_reorientation(np.asarray(sp), np.asarray(c),
                                    geom.bases0)
            if r is None:
                continue
            e, g = r
            cand = apply_reorientation(Xp, e, g)
            if weaponA.brackets_ok(cand, c, geom):
                W = cand
                break
        if W is None:
            stats['no_group_element'] += 1
            continue
        diff = np.flatnonzero(
            np.asarray(weaponA.rz.exact_bracket_signs(W, geom)) !=
            np.asarray(chi, dtype=np.int8))
        if len(diff) != 1 or int(diff[0]) != j:
            stats['no_group_element'] += 1
            continue
        stats['ok'] += 1
        out.append((j, W, s))
    if verbose:
        print('  neighbour lookup: %s' % stats)
    return out, stats


# ----------------------------------------------------------------------
# the attack
# ----------------------------------------------------------------------

def attack_with_neighbours(row, chi, budget=3600.0, seed=20260803,
                           per_p=40, depth=24, verbose=True):
    S = exactgate.ExactSearcher(seed=seed)
    geom = S.g9
    t0 = time.time()
    nb, stats = realizable_neighbours(row, chi, geom, verbose=verbose)
    dels = [weaponA.Deletion(chi, S.g9, S.g8, p) for p in range(N)]
    log = {'neighbours': stats, 'tested': 0, 'infeasible': 0,
           'deletions_covered': set()}

    order = list(range(len(nb)))
    rng = np.random.default_rng(seed)
    rounds = 0
    while time.time() - t0 < budget:
        rounds += 1
        rng.shuffle(order)
        for k in order:
            j, W, s = nb[k]
            Wc = [[int(W[i][q]) for i in range(R)] for q in range(N)]
            for p in geom.bases0[j]:
                dele = dels[p]
                Y = [Wc[q] for q in dele.keep]
                st_, payload, blk = S.complete_exact(Y, dele, chi)
                log['tested'] += 1
                if st_ == 'INFEASIBLE':
                    log['infeasible'] += 1
                    log['deletions_covered'].add(int(p))
                if st_ == 'FEASIBLE':
                    log['found'] = 'neighbour(mutant %d, row %d)' % (j, s)
                    log['seconds'] = round(time.time() - t0, 1)
                    log['deletions_covered'] = sorted(
                        log['deletions_covered'])
                    return payload, log
                for _ in range(per_p):
                    Y = S.walk_big(Y, dele, steps=1, blockers=blk)
                    st_, payload, blk = S.complete_exact(Y, dele, chi)
                    log['tested'] += 1
                    if st_ == 'INFEASIBLE':
                        log['infeasible'] += 1
                        log['deletions_covered'].add(int(p))
                    if st_ == 'FEASIBLE':
                        log['found'] = ('neighbour_walk(mutant %d, row %d)'
                                        % (j, s))
                        log['seconds'] = round(time.time() - t0, 1)
                        log['deletions_covered'] = sorted(
                            log['deletions_covered'])
                        return payload, log
                    if time.time() - t0 > budget:
                        break
                if time.time() - t0 > budget:
                    break
            if time.time() - t0 > budget:
                break
        if not nb:
            break
    log['found'] = None
    log['rounds'] = rounds
    log['seconds'] = round(time.time() - t0, 1)
    log['deletions_covered'] = sorted(log['deletions_covered'])
    return None, log


def _chi_of(row):
    return catalog.chi_of_rows([row])[0]


def cmd_show(a):
    chi = _chi_of(a.row)
    S = weaponA.Searcher(seed=1)
    nb, stats = realizable_neighbours(a.row, chi, S.g9)
    print('row %d: %d realizable mutation neighbours recovered' %
          (a.row, len(nb)))
    st = catalog.arrays()['st']
    for (j, W, s) in nb:
        print('   mutant at basis %3d -> catalog row %8d (%s), '
              'max|entry| %d' % (j, s, catalog.STATUS[int(st[s])],
                                 int(np.abs(W).max())))


def cmd_run(a):
    chi = _chi_of(a.row)
    chis = catalog.chi_string(chi)
    Z, log = attack_with_neighbours(a.row, chi, budget=a.budget,
                                    seed=a.seed, per_p=a.per_p,
                                    depth=a.depth)
    rec = {'row': a.row, 'chi': chis,
           'verdict': 'REALIZABLE' if Z is not None else 'STILL_OPEN',
           'method': 'neighbours', 'budget': a.budget, 'seed': a.seed}
    rec.update({k: v for k, v in log.items() if k != 'certs'})
    with open(os.path.join(DATA, 'neighbours_%d_%d.jsonl'
                           % (a.row, a.seed)), 'a') as fh:
        fh.write(json.dumps(rec) + '\n')
    if Z is not None:
        mat = [[Z[q][i] for q in range(N)] for i in range(R)]
        with open(os.path.join(DATA, 'certs_realizable.jsonl'), 'a') as fh:
            fh.write(json.dumps({'n': N, 'r': R, 'chi': chis,
                                 'verdict': 'REALIZABLE',
                                 'matrix': mat}) + '\n')
        print('*** REALIZED row %d via %s in %.1f s'
              % (a.row, log['found'], log['seconds']))
    else:
        print('row %d still open after %.1f s: %d exact tests, %d '
              'INFEASIBLE, deletions covered %s'
              % (a.row, log['seconds'], log['tested'], log['infeasible'],
                 log['deletions_covered']))


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest='cmd', required=True)
    s = sub.add_parser('show')
    s.add_argument('--row', type=int, required=True)
    s.set_defaults(fn=cmd_show)
    r = sub.add_parser('run')
    r.add_argument('--row', type=int, required=True)
    r.add_argument('--budget', type=float, default=3600.0)
    r.add_argument('--seed', type=int, default=20260803)
    r.add_argument('--per-p', type=int, default=40)
    r.add_argument('--depth', type=int, default=24)
    r.set_defaults(fn=cmd_run)
    a = ap.parse_args()
    a.fn(a)


if __name__ == '__main__':
    main()
