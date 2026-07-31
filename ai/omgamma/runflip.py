"""Run exhaustive mutation-BFS + holonomy for (n,r); persist results and
certificate data; cross-validate against the extension catalog.

Usage: python runflip.py <r> <n>
"""
import json
import sys
import time
from math import comb, factorial

from core import to_string, from_string
from flip import bfs_holonomy
from masscheck import catalog_masks


def perm_str(sig):
    return ",".join(map(str, sig))


def main(r, n):
    start = (1 << comb(n, r)) - 1     # moment-curve class (all-plus)
    res = bfs_holonomy(n, r, start, verbose=True)
    hol = res['hol']
    p_ord, p_full, u_dim, u_full = hol.status()

    # cross-validate BFS class set against extension catalog
    try:
        cat = set()
        for cm in catalog_masks(r, n):
            from canon import canonical
            cat.add(canonical(n, r, cm, want_witness=False)['can'])
        bfsset = set(res['classes'].keys())
        same = (cat == bfsset)
    except FileNotFoundError:
        cat, same = None, None

    summary = {
        'n': n, 'r': r,
        'classes': res['nclasses'],
        'directed_edge_traversals': res['nedges_directed'],
        'undirected_mutation_edges_with_multiplicity':
            res['nedges_directed'] // 2,
        'perm_holonomy_order': p_ord,
        'S_n_order': p_full,
        'sign_dim': u_dim,
        'sign_dim_full': u_full,
        'sign_part_exact': bool(getattr(hol, 'exact', False)),
        'H_equals_Gbar': hol.full(),
        'gamma_hat_connected_on_bfs': True,
        'catalog_matches_bfs': same,
        'gamma_bar_connected': None,
        'gamma_tilde_connected': None,
        'seconds': res['seconds'],
    }
    if same:
        summary['gamma_bar_connected'] = hol.full()
        summary['gamma_tilde_connected'] = (p_ord == p_full)

    with open(f"data/flip_{r}_{n}_summary.json", "w") as f:
        json.dump(summary, f, indent=1)

    # certificate data: reps in BFS order, tree with voltages, generators
    with open(f"data/flip_{r}_{n}_reps.txt", "w") as f:
        for cm in res['reps']:
            f.write(to_string(n, r, cm) + "\n")
    with open(f"data/flip_{r}_{n}_tree.txt", "w") as f:
        for cid, td in enumerate(res['tree']):
            if td is None:
                f.write(f"{cid} root\n")
            else:
                p, j, (sig, eps, s) = td
                f.write(f"{cid} {p} {j} {perm_str(sig)} {eps} {s}\n")
    with open(f"data/flip_{r}_{n}_gens.txt", "w") as f:
        for prov, g, _grew in hol.elems:
            sig, eps, s = g
            f.write(f"{'|'.join(map(str,prov))} {perm_str(sig)} "
                    f"{eps} {s}\n")
    ex, exdim = hol.sign_exhibits()
    with open(f"data/flip_{r}_{n}_exhibits.txt", "w") as f:
        for w, v in ex:
            f.write(f"{v} {','.join(map(str, w))}\n")
    summary['exhibit_sign_dim'] = exdim
    with open(f"data/flip_{r}_{n}_summary.json", "w") as f:
        json.dump(summary, f, indent=1)

    print(json.dumps(summary, indent=1))


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
