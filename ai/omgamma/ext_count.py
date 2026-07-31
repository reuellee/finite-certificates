"""Parallel extension-COUNT sweep: computes the mass-formula target

   N_chi(n, r) = sum over classes c of (n-1, r):  orbit8(c) * E(c)

where orbit(c) = (n-1)! 2^n / stab_c  and E(c) = number of uniform
single-element extension signings of the representative chirotope.
No canonicalization of children — cheap.

Usage: python ext_count.py <r> <n> <nworkers>
Writes data/mass_target_{r}_{n}.json
"""
import json
import sys
import time
from math import comb, factorial
from multiprocessing import Pool

from extend import extension_system
from masscheck import catalog_masks
from canon import canonical


def count_extensions(m, r, parent_mask):
    """Count solutions of the extension system (no mask building)."""
    nv, by_last = extension_system(m, r)
    conds_resolved = []
    for v in range(nv):
        lst = []
        for ct in by_last[v]:
            rs = []
            for (nvs, olds, cc) in ct:
                for o in olds:
                    cc ^= (parent_mask >> o) & 1
                rs.append((nvs, cc))
            lst.append(tuple(rs))
        conds_resolved.append(lst)

    x = [0] * nv
    trail = [0] * nv
    v = 0
    count = 0
    while True:
        if trail[v] > 1:
            trail[v] = 0
            v -= 1
            if v < 0:
                break
            trail[v] += 1
            continue
        x[v] = trail[v]
        ok = True
        for ct in conds_resolved[v]:
            ps = []
            for (nvs, cc) in ct:
                p = cc
                for u in nvs:
                    p ^= x[u]
                ps.append(p)
            if ps[0] == ps[1] == ps[2]:
                ok = False
                break
        if ok:
            if v == nv - 1:
                count += 1
                trail[v] += 1
            else:
                v += 1
                trail[v] = 0
        else:
            trail[v] += 1
    return count


def count_extensions_fast(m, r, parent_mask):
    """Tightened counter: conditions flattened to 6 var-slots + 3 consts
    with a sentinel variable (index nv, always 0)."""
    nv, by_last = extension_system(m, r)
    SEN = nv
    flat = [[] for _ in range(nv)]
    for v in range(nv):
        for ct in by_last[v]:
            row = []
            for (nvs, olds, cc) in ct:
                c = cc
                for o in olds:
                    c ^= (parent_mask >> o) & 1
                a = nvs[0] if len(nvs) > 0 else SEN
                b = nvs[1] if len(nvs) > 1 else SEN
                row += [a, b, c]
            flat[v].append(tuple(row))
    x = [0] * (nv + 1)          # sentinel at x[nv] = 0
    trail = [0] * nv
    v = 0
    count = 0
    last = nv - 1
    while True:
        tv = trail[v]
        if tv > 1:
            trail[v] = 0
            v -= 1
            if v < 0:
                break
            trail[v] += 1
            continue
        x[v] = tv
        ok = True
        for (a1, b1, c1, a2, b2, c2, a3, b3, c3) in flat[v]:
            p1 = x[a1] ^ x[b1] ^ c1
            if p1 == (x[a2] ^ x[b2] ^ c2) and p1 == (x[a3] ^ x[b3] ^ c3):
                ok = False
                break
        if ok:
            if v == last:
                count += 1
                trail[v] += 1
            else:
                v += 1
                trail[v] = 0
        else:
            trail[v] += 1
    return count


def _work(args):
    m, r, i, pm = args
    E = count_extensions_fast(m, r, pm)
    stab = canonical(m, r, pm, want_witness=True)['stab_order_exact']
    return i, pm, E, stab


def main(r, n, nw):
    m = n - 1
    parents = catalog_masks(r, m)
    Gp = factorial(m) * (1 << (m + 1))
    t0 = time.time()
    ckpt = f"data/extcount_{r}_{n}.jsonl"
    done_idx = {}
    try:
        with open(ckpt) as f:
            for line in f:
                rec = json.loads(line)
                done_idx[rec['i']] = rec
    except FileNotFoundError:
        pass
    todo = [(m, r, i, pm) for i, pm in enumerate(parents)
            if i not in done_idx]
    print(f"{len(done_idx)} done, {len(todo)} to go", flush=True)
    if todo:
        with Pool(nw) as pool, open(ckpt, "a") as ck:
            ndone = len(done_idx)
            for i, pm, E, stab in pool.imap_unordered(
                    _work, todo, chunksize=2):
                rec = {'i': i, 'E': E, 'stab': stab}
                ck.write(json.dumps(rec) + "\n")
                ck.flush()
                done_idx[i] = rec
                ndone += 1
                if ndone % 50 == 0:
                    print(f"  {ndone}/{len(parents)} parents, "
                          f"{time.time()-t0:.0f}s", flush=True)
    total = 0
    totE = 0
    for i in range(len(parents)):
        rec = done_idx[i]
        assert Gp % rec['stab'] == 0
        total += (Gp // rec['stab']) * rec['E']
        totE += rec['E']
    out = {'r': r, 'n': n, 'N_chi': str(total),
           'N_pairs': str(total // 2),
           'sum_E_over_reps': totE,
           'parents': len(parents), 'seconds': time.time() - t0}
    with open(f"data/mass_target_{r}_{n}.json", "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
