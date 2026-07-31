"""Simulate a crash: drop the trailing level files of a runbig state dir
and rewrite meta.json consistently, so that `--resume` can be exercised
from a mid-level checkpoint.

Usage: python truncate_state.py <r> <n> <keep_level>
"""
import glob
import json
import os
import sys
from math import factorial

import numpy as np


def main(r, n, keep):
    d = f"data/big_{r}_{n}"
    Gn = factorial(n) * (1 << (n + 1))
    for p in sorted(glob.glob(f"{d}/level_*.npz")):
        lv = int(os.path.basename(p)[6:9])
        if lv > keep:
            os.remove(p)
            print("removed", p)
    tot = 0
    mass = 0
    for p in sorted(glob.glob(f"{d}/level_*.npz")):
        z = np.load(p)
        st = z['stab']
        tot += len(st)
        uq, ct = np.unique(st, return_counts=True)
        for s, c in zip(uq.tolist(), ct.tolist()):
            mass += (Gn // int(s)) * int(c)
    with open(f"{d}/mass_target_probe.json", "w") as f:
        json.dump({}, f)
    os.remove(f"{d}/mass_target_probe.json")
    with open(f"data/mass_target_{r}_{n}.json") as f:
        target = int(json.load(f)['N_chi'])
    meta = {'level': keep, 'total_classes': tot,
            'total_edges_expanded': -1, 'total_mass': str(mass),
            'target_mass': str(target), 'complete': mass == target,
            'truncated_by': 'truncate_state.py'}
    with open(f"{d}/meta.json", "w") as f:
        json.dump(meta, f, indent=1)
    print(json.dumps(meta, indent=1))


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]))
