"""DIAGNOSTIC: harvest the class-STABILIZER holonomy generators that
runbig.py's phase 2 never harvested.

Lemma 2 generates H from (i) tau_c u tau_c^{-1} for u in Stab(chi_c) and
(ii) tau_c t tau_{c'}^{-1} for the mutation edges.  runbig.phase1 harvests
both; runbig phase 2 harvests ONLY (ii) -- `_wexpand` computes the
canonical stabilizer and discards everything but its order.  So for every
class discovered in phase 2 the (i) generators are missing.

A class contributes a nontrivial (i) generator iff its stabilizer in Gbar
is nontrivial, i.e. iff stab_order_exact > 2^kappa where 2^kappa =
|kernel of the sign action on strings| (kappa = 1 for (9,4): only 1^9).
Those classes are rare and are already flagged in the checkpoints, so the
whole backfill costs one canonicalization per flagged class.

Usage: python diag_stabhol.py <r> <n> [--with-root-edges]
"""
import json
import sys
from math import comb, factorial

import numpy as np

from bigstate import load_state
from canon import canonical, _sign_kernel
from flip import Holonomy, bar_compose, bar_inverse


def main(r, n):
    outdir = f"data/big_{r}_{n}"
    st = load_state(r, n, outdir)
    kappa = len(_sign_kernel(n, r))
    trivial = 1 << kappa
    print(f"sign-kernel dim kappa = {kappa}; a class has trivial Gbar-"
          f"stabilizer iff stab_order_exact == {trivial}")
    stab = st['stab']
    idx = np.flatnonzero(stab > trivial)
    print(f"{len(idx)} of {st['total_classes']} classes have a NONTRIVIAL "
          f"Gbar-stabilizer")
    hol = Holonomy(n)
    nadd = 0
    ngen = 0
    keymis = 0
    for c in idx.tolist():
        mv = (int(st['masks'][c, 0]) << 64) | int(st['masks'][c, 1])
        res = canonical(n, r, mv, want_witness=True)
        kv = (int(st['keys'][c, 0]) << 64) | int(st['keys'][c, 1])
        if res['can'] != kv or res['stab_order_exact'] != int(stab[c]):
            keymis += 1
            continue
        tau = (tuple(int(x) for x in st['tau_sig'][c]),
               int(st['tau_eps'][c]), 0)
        taui = bar_inverse(n, tau)
        for u in res['stab']:
            h = bar_compose(n, bar_compose(n, tau, u), taui)
            if h[0] == tuple(range(1, n + 1)) and h[1] == 0:
                continue          # trivial in Gbar
            ngen += 1
            if hol.add(h, prov=('stab', c)):
                nadd += 1
    print(f"harvested {ngen} nontrivial stabilizer conjugates "
          f"({nadd} grew H); key/stab mismatches: {keymis}")
    hol.saturate(limit=200_000_000)
    p_ord, p_full, u_dim, u_full = hol.status()
    print(f"H(stabilizers only): |pi| = {p_ord}/{p_full}, "
          f"sign dim = {u_dim}/{u_full}")
    print(f"sign part NONTRIVIAL: {u_dim > 1}")
    out = {'r': r, 'n': n, 'classes_scanned': st['total_classes'],
           'nontrivial_stab_classes': int(len(idx)),
           'stab_generators': ngen, 'perm_order': p_ord,
           'sign_dim': u_dim, 'sign_nontrivial': bool(u_dim > 1),
           'key_mismatches': keymis}
    with open(f"{outdir}/diag_stabhol.json", "w") as f:
        json.dump(out, f, indent=1)
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
