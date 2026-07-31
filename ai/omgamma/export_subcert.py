"""Export a COMPACT, fully checkable certificate from a runbig state.

The full (9,4) class list has ~9.3M representatives; re-verifying the
Grassmann-Plucker axiom on all of them is not the point of the holonomy
certificate.  What the checker actually needs is:

  * the spanning-tree paths from the root to every class referenced by a
    holonomy generator (so that the transports tau it recomputes are the
    same ones the generator identities were built with), and
  * the generators + sign exhibits themselves.

The union of those root-paths is closed under `parent`, so restricting
the tree to it and renumbering by increasing original id yields a valid,
topologically ordered certificate in exactly the checker's format.  It
certifies  H = Gbar  (hence: Gamma_bar has [Gbar:H] = 1 component over
each component of Gamma_hat).  It does NOT certify class-list
completeness -- that is the mass identity's job (separate trust
boundary).

Usage: python export_subcert.py <r> <n> [outprefix] [gensdir]
       gensdir defaults to the state dir; pass e.g.
       data/big_4_9/certA_dir to package a certify.py holonomy instead.
"""
import gzip
import json
import os
import sys
from math import comb

import numpy as np

from bigstate import load_state


def main(r, n, prefix=None, gensdir=None):
    d = f"data/big_{r}_{n}"
    gensdir = gensdir or d
    prefix = prefix or f"{d}/subcert"
    M = comb(n, r)
    st = load_state(r, n, d, meta_gate=False)
    parent = st['parent']
    masks = st['masks']
    flip = st['flip']
    sigma = st['sigma']
    eps = st['eps']

    gens = []
    with open(f"{gensdir}/gens.txt") as f:
        for line in f:
            parts = line.split()
            if parts:
                gens.append(parts)
    needed = set()
    for parts in gens:
        prov = parts[0].split('|')
        if prov[0] == 'stab':
            needed.add(int(prov[1]))
        elif prov[0] == 'edge':
            needed.add(int(prov[1]))
            needed.add(int(prov[3]))
        else:
            raise RuntimeError("unknown provenance " + parts[0])
    print(f"{len(gens)} generators reference {len(needed)} classes")

    closed = set()
    stack = list(needed)
    while stack:
        c = stack.pop()
        if c in closed:
            continue
        closed.add(c)
        p = int(parent[c])
        if p >= 0 and p not in closed:
            stack.append(p)
    keep = sorted(closed)
    newid = {c: i for i, c in enumerate(keep)}
    if keep[0] != 0:
        raise RuntimeError("root class 0 missing from the closure")
    print(f"root-path closure: {len(keep)} classes "
          f"(of {st['total_classes']})")

    with gzip.open(f"{prefix}_reps.txt.gz", "wt") as fr, \
            gzip.open(f"{prefix}_tree.txt.gz", "wt") as ft:
        for c in keep:
            v = (int(masks[c, 0]) << 64) | int(masks[c, 1])
            fr.write(''.join('+' if (v >> j) & 1 else '-'
                             for j in range(M)) + "\n")
            i = newid[c]
            p = int(parent[c])
            if p < 0:
                ft.write(f"{i} root\n")
            else:
                ft.write(f"{i} {newid[p]} {int(flip[c])} "
                         f"{','.join(str(int(x)) for x in sigma[c])} "
                         f"{int(eps[c])} 0\n")
    with open(f"{prefix}_gens.txt", "w") as fg:
        for parts in gens:
            prov = parts[0].split('|')
            if prov[0] == 'stab':
                prov[1] = str(newid[int(prov[1])])
            else:
                prov[1] = str(newid[int(prov[1])])
                prov[3] = str(newid[int(prov[3])])
            fg.write("|".join(prov) + " " + " ".join(parts[1:]) + "\n")
    if os.path.exists(f"{gensdir}/exhibits.txt"):
        with open(f"{gensdir}/exhibits.txt") as a, \
                open(f"{prefix}_exhibits.txt", "w") as b:
            b.write(a.read())
    info = {'r': r, 'n': n, 'classes_in_subcert': len(keep),
            'classes_total': st['total_classes'],
            'generators': len(gens),
            'files': [f"{prefix}_reps.txt.gz", f"{prefix}_tree.txt.gz",
                      f"{prefix}_gens.txt", f"{prefix}_exhibits.txt"]}
    with open(f"{prefix}_info.json", "w") as f:
        json.dump(info, f, indent=1)
    print(json.dumps(info, indent=1))


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]),
         sys.argv[3] if len(sys.argv) > 3 else None,
         sys.argv[4] if len(sys.argv) > 4 else None)
