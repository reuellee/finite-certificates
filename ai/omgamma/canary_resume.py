"""Sabotage canaries for the RESUME path: bigstate.load_state and its
sample verification must reject each corrupted checkpoint.

Corruption modes
  mass         total_mass in meta.json off by one orbit
  classes      total_classes in meta.json off by one
  torn         a trailing level file present that meta.json does not know
               about (the crash-between-write-and-meta case)
  gap          a middle level file deleted
  voltage      a tree edge's eps voltage flipped inside a level file
               (must be caught by the re-canonicalization sample check)
  mask         a stored canonical mask bit flipped (ditto)

Usage: python canary_resume.py <r> <n>       (uses data/big_<r>_<n>)
"""
import json
import os
import shutil
import sys

import numpy as np

from bigstate import load_state, verify_sample, selftest_compose

TMP = "data/canary_resume_tmp"


def _prep(src):
    if os.path.exists(TMP):
        shutil.rmtree(TMP)
    shutil.copytree(src, TMP)


def _meta(k, f):
    p = f"{TMP}/meta.json"
    m = json.load(open(p))
    m[k] = f(m[k])
    json.dump(m, open(p, "w"), indent=1)


def _patch_level(lv, field, idx, fn):
    p = f"{TMP}/level_{lv:03d}.npz"
    z = dict(np.load(p))
    a = z[field]
    a[idx] = fn(a[idx])
    z[field] = a
    np.savez_compressed(p, **z)


def main(r, n):
    src = f"data/big_{r}_{n}"
    ok = True
    selftest_compose(n=n)
    print("compose_rows selftest OK")

    def attempt(name, mutate, full_sample=False):
        _prep(src)
        mutate()
        try:
            st = load_state(r, n, TMP, verbose=False)
            verify_sample(st, nsample=st['total_classes'] if full_sample
                          else 200, verbose=False)
        except Exception as e:
            print(f"PASS canary '{name}': rejected ({type(e).__name__}: "
                  f"{str(e)[:70]})")
            return True
        print(f"FAIL canary '{name}': ACCEPTED a corrupt checkpoint")
        return False

    # control: the untouched checkpoint must be ACCEPTED
    _prep(src)
    st = load_state(r, n, TMP, verbose=False)
    verify_sample(st, nsample=200, verbose=False)
    print(f"PASS control: clean checkpoint accepted "
          f"({st['total_classes']} classes)")
    lastlv = st['level']

    ok &= attempt("mass", lambda: _meta(
        'total_mass', lambda v: str(int(v) + 92897280)))
    ok &= attempt("classes", lambda: _meta(
        'total_classes', lambda v: v + 1))
    ok &= attempt("torn", lambda: shutil.copy(
        f"{TMP}/level_{lastlv:03d}.npz",
        f"{TMP}/level_{lastlv+1:03d}.npz"))
    ok &= attempt("gap", lambda: os.remove(f"{TMP}/level_001.npz"))
    ok &= attempt("voltage",
                  lambda: _patch_level(1, 'eps', 0, lambda v: v ^ 5),
                  full_sample=True)
    ok &= attempt("mask",
                  lambda: _patch_level(1, 'masks', (0, 1), lambda v: v ^ 1),
                  full_sample=True)

    print("ALL RESUME CANARIES PASS" if ok else "RESUME CANARY FAILURE")
    shutil.rmtree(TMP, ignore_errors=True)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]))
