"""Export a runbig state dir into checker-format certificate files.

Usage: python export_bigcert.py <r> <n>
Reads  data/big_<r>_<n>/level_*.npz (+ gens.txt, exhibits.txt)
Writes data/big_<r>_<n>/reps.txt.gz and tree.txt.gz
"""
import glob
import gzip
import sys
from math import comb

import numpy as np


def main(r, n):
    d = f"data/big_{r}_{n}"
    M = comb(n, r)
    files = sorted(glob.glob(f"{d}/level_*.npz"))
    assert files
    fr = gzip.open(f"{d}/reps.txt.gz", "wt")
    ft = gzip.open(f"{d}/tree.txt.gz", "wt")
    cid = 0
    for path in files:
        z = np.load(path)
        masks = z['masks']
        par = z['parent']
        flip = z['flip']
        sig = z['sigma']
        eps = z['eps']
        m = len(masks)
        # rep strings
        for t in range(m):
            v = (int(masks[t, 0]) << 64) | int(masks[t, 1])
            fr.write(''.join('+' if (v >> j) & 1 else '-'
                             for j in range(M)) + "\n")
        for t in range(m):
            if par[t] < 0:
                ft.write(f"{cid} root\n")
            else:
                ft.write(f"{cid} {int(par[t])} {int(flip[t])} "
                         f"{','.join(str(int(x)) for x in sig[t])} "
                         f"{int(eps[t])} 0\n")
            cid += 1
        print(f"{path}: +{m} (total {cid})", flush=True)
    fr.close()
    ft.close()
    print(f"exported {cid} classes")


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
