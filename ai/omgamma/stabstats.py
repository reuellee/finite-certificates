"""Exact stabilizer statistics + the mass identity, straight off the
level_*.npz checkpoints (never off `stab_gens`, which stops being
incremented as soon as H = Gbar short-circuits the harvest).

Prints the histogram of |Stab_{G'}(chi_c)|, the number of classes with a
nontrivial Gbar-stabilizer, the exact rational sum(1/nstates) and the
mass identity against the precomputed target.

Usage: python stabstats.py <r> <n>
"""
import glob
import json
import sys
from fractions import Fraction
from math import factorial

import numpy as np


def main(r, n):
    d = f"data/big_{r}_{n}"
    Gn = factorial(n) * (1 << (n + 1))
    from canon import _sign_kernel
    kappa = len(_sign_kernel(n, r))
    trivial = 1 << kappa
    hist = {}
    tot = 0
    mass = 0
    for p in sorted(glob.glob(f"{d}/level_*.npz")):
        st = np.load(p)['stab']
        tot += len(st)
        u, c = np.unique(st, return_counts=True)
        for s, k in zip(u.tolist(), c.tolist()):
            hist[int(s)] = hist.get(int(s), 0) + int(k)
            mass += (Gn // int(s)) * int(k)
    with open(f"data/mass_target_{r}_{n}.json") as f:
        target = int(json.load(f)['N_chi'])
    nontriv = sum(v for k, v in hist.items() if k > trivial)
    S = sum(Fraction(v, 1) * Fraction(trivial, k) for k, v in hist.items())
    out = {
        'r': r, 'n': n, 'classes': tot,
        'stab_histogram': dict(sorted(hist.items())),
        'sign_kernel_dim_kappa': kappa,
        'trivial_stab_order': trivial,
        'classes_with_nontrivial_Gbar_stabilizer': nontriv,
        'sum_1_over_nstates': str(S),
        'sum_1_minus_1_over_nstates': str(tot - S),
        'mass': str(mass), 'target': str(target),
        'mass_identity_holds': mass == target,
        'mass_pct': 100.0 * mass / target,
    }
    print(json.dumps(out, indent=1))
    with open(f"{d}/stabstats.json", "w") as f:
        json.dump(out, f, indent=1)
    return 0 if mass == target else 1


if __name__ == "__main__":
    sys.exit(main(int(sys.argv[1]), int(sys.argv[2])))
