"""Build a STANDALONE H = Gbar certificate from a checkpoint, without
waiting for (or disturbing) a running coverage sweep.

Rationale: `runbig.py` writes gens/exhibits only when the whole sweep
finishes, so a long campaign that dies late leaves no certificate at all
even though the holonomy was settled early.  This script reconstructs the
holonomy from any checkpoint --
  family (i): tau_c u tau_c^{-1} for every class with a nontrivial
              Gbar-stabilizer (complete on the checkpointed classes);
  family (ii): edge voltages, harvested by expanding classes in id order
              until H = Gbar (usually a handful) --
runs the exact staged Schreier completion, and writes gens/exhibits under
a SEPARATE prefix so nothing a running campaign will write is touched.

The result is a lower bound H' <= H; H' = Gbar therefore proves H = Gbar
exactly (a lower bound equal to the whole group is the whole group).

Usage: python certify.py <r> <n> [max_expand] [prefix] [start_class]
  start_class: where to begin expanding for family (ii).  The classes
  near the root live in the highly symmetric neighbourhood of the
  alternating OM; at (9,4) the first 2000 of them yield 26,013 edge
  voltages whose permutation parts are ALL EVEN, so pi stays at A_9.
  Starting inside a middle level finds an odd one almost immediately.
"""
import json
import sys
import time
from math import comb

import numpy as np

from bigstate import load_state
from canon import canonical, _sign_kernel
from core import mutable_bases_np
from flip import Holonomy, bar_compose, bar_inverse
from runbig import harvest_stab, write_hol_files


def main(r, n, max_expand=20000, prefix=None, start=0):
    d = f"data/big_{r}_{n}"
    prefix = prefix or f"{d}/certA"
    t0 = time.time()
    st = load_state(r, n, d)
    kappa = len(_sign_kernel(n, r))
    trivial = 1 << kappa
    hol = Holonomy(n)

    cids = np.flatnonzero(st['stab'] > trivial)
    ng = harvest_stab(n, r, hol, cids, cids, st['masks'], st['keys'],
                      st['stab'], st['tau_sig'], st['tau_eps'], trivial)
    print(f"family (i): {ng} stabilizer conjugates from {len(cids)} "
          f"classes; hol {hol.status()}", flush=True)
    try:
        hol.saturate(limit=200_000_000)
    except RuntimeError:
        pass
    print(f"after exact saturation: hol {hol.status()}, "
          f"full={hol.full()}", flush=True)

    known, known_ids = st['known'], st['known_ids'].astype(np.int64)
    tau_sig, tau_eps = st['tau_sig'], st['tau_eps']
    masks = st['masks']
    nedge = 0
    nexp = 0
    for c in range(start, min(start + max_expand,
                              st['total_classes'])):
        if hol.full():
            break
        nexp += 1
        chi = (int(masks[c, 0]) << 64) | int(masks[c, 1])
        taup = (tuple(int(x) for x in tau_sig[c]), int(tau_eps[c]), 0)
        for j in mutable_bases_np(n, r, chi):
            if hol.full():
                break
            res = canonical(n, r, chi ^ (1 << j), want_witness=True)
            tvol = bar_inverse(n, res['g'])
            kk = np.array([[(res['can'] >> 64) & ((1 << 64) - 1),
                            res['can'] & ((1 << 64) - 1)]],
                          dtype=np.uint64).view(
                [('hi', np.uint64), ('lo', np.uint64)]).reshape(-1)
            pos = int(np.searchsorted(known, kk)[0])
            if pos >= len(known) or known[pos] != kk[0]:
                continue          # child outside the checkpoint: skip
            c2 = int(known_ids[pos])
            tauc = (tuple(int(x) for x in tau_sig[c2]),
                    int(tau_eps[c2]), 0)
            h = bar_compose(n, bar_compose(n, taup, tvol),
                            bar_inverse(n, tauc))
            hol.add(h, prov=('edge', c, j, c2))
            nedge += 1
        # NOTE: no saturate() inside this loop.  The sign part is already
        # complete after the family-(i) saturation above, and the
        # permutation part is tracked incrementally by hol.add, so
        # hol.full() flips the moment pi(H) reaches S_n.  (Calling
        # saturate per class walks a 181440-coset transversal each time
        # and is the difference between seconds and hours.)
    print(f"family (ii): expanded {nexp} classes, {nedge} edge "
          f"generators; hol {hol.status()}, full={hol.full()} "
          f"({time.time()-t0:.0f}s)", flush=True)

    class _P:
        pass
    import os
    os.makedirs(f"{prefix}_dir", exist_ok=True)
    write_hol_files(f"{prefix}_dir", hol,
                    {'phase': 'certify',
                     'checkpoint_level': st['level'],
                     'checkpoint_classes': st['total_classes'],
                     'stab_gens': ng, 'edge_gens': nedge,
                     'classes_expanded': nexp, 'start_class': start,
                     'lower_bound_but_equal_Gbar': hol.full()})
    print(json.dumps(json.load(open(f"{prefix}_dir/holonomy.json")),
                     indent=1))
    return 0 if hol.full() else 1


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]), int(sys.argv[2]),
                  int(sys.argv[3]) if len(sys.argv) > 3 else 20000,
                  sys.argv[4] if len(sys.argv) > 4 else None,
                  int(sys.argv[5]) if len(sys.argv) > 5 else 0))
