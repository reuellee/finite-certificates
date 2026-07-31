"""Build catalogs of uniform OM isomorphism classes by rank, saving reps.

Usage: python runcat.py <rank> <n_max>
Writes data/cat_<r>_<n>.txt (one canonical-mask string per line, sorted),
and prints counts + extension statistics.
"""
import sys
import time
from math import comb

from core import to_string
from canon import canonical
from extend import uniform_extensions


def main(r, n_max):
    t00 = time.time()
    # base case n = r: single class, the one-basis '+' chirotope
    parents = [1]     # mask with bit0 = '+'  (M = C(r,r) = 1)
    print(f"(r={r}) n={r}: 1 class")
    for n in range(r + 1, n_max + 1):
        t0 = time.time()
        cat = {}
        totext = 0
        for t, pm in enumerate(parents):
            exts = uniform_extensions(n - 1, r, pm)
            totext += len(exts)
            for child in exts:
                res = canonical(n, r, child, want_witness=False)
                k = res['can']
                if k not in cat:
                    cat[k] = res['canmask']
            if (t + 1) % 200 == 0:
                print(f"   ... parent {t+1}/{len(parents)}, "
                      f"classes {len(cat)}, exts {totext}, "
                      f"{time.time()-t0:.0f}s", flush=True)
        dt = time.time() - t0
        print(f"(r={r}) n={n}: {len(cat)} classes   "
              f"[{totext} extensions, {dt:.1f}s, "
              f"{1000*dt/max(totext,1):.2f} ms/ext]", flush=True)
        parents = [cat[k] for k in sorted(cat)]
        with open(f"data/cat_{r}_{n}.txt", "w") as f:
            for pm in parents:
                f.write(to_string(n, r, pm) + "\n")
    print(f"total {time.time()-t00:.1f}s")


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
