"""Cell-wide certificates at the second 2-subset split orbit: A = {0,2},
s = (+1,-1,+1,-1,-1). Its k=3 flip partners follow by (sigma,s)->(-sigma,-s).

`check_split_orbits.py` proves the library's splits ({}, {0}, {0,1}, +
flips) miss exactly one Stab(chi_ref)-orbit of splits: the 2-subsets in
the orbit of {0,2} (and their k=3 complements). This sweep closes it for
all 33,140 valid labeled sigmas, with the same two mechanisms as the
earlier sweeps:

  FAMILY_SINGLE_CLASS: some class (i,j) has equal side signs sigma* with
  sigma* . s_t = -1 for every t outside {i,j} (for this split: exactly
  class (0,2) with both its side bits set); the closed-form certificate
  {y_sides = 1, y_wt = 2 D_tij} applies, cell-wide, no GP needed.

  EXACT_CELLWIDE_CERTIFICATE: the degree-(2,3) quotient-ring kernel
  search (gp_degree3_search), escalating to degree (3,4) on failure.

Canaries per shard (both verified before the sweep starts):
  negative: (bits=0, split (+,-,-,-,-)) - provably uncertifiable, the
  kernel search must fail on it at every degree tried;
  positive: (bits=3181, split (+,+,-,-,-)) - certificated in the audited
  shard 0 of the full-complement sweep, the search must succeed.

Usage: python split02_cellwide_sweep.py --shard-index I --n-shards N
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "stage2c2_gpt"))

from common import VALID_BITS, U_INTS  # noqa: E402
from k0_cellwide_sweep import write_json_gz  # noqa: E402
from gp_degree3_search import (  # noqa: E402
    PAIRS,
    find_exact_kernel,
    find_exact_separator,
    normal_forms,
    quotient_matrix,
)

SPLIT = (1, -1, 1, -1, -1)
SEED = 2026073107


def family_criterion(bits, split):
    for ci, (i, j) in enumerate(PAIRS):
        sp = 1 if bits >> (2 * ci) & 1 else -1
        sm = 1 if bits >> (2 * ci + 1) & 1 else -1
        if sp == sm and all(sp * split[t] == -1
                            for t in range(5) if t not in (i, j)):
            return True
    return False


def search(bits, split, degree, forms, rng):
    variables, row_keys, matrix = quotient_matrix(int(bits), tuple(split),
                                                  degree, forms)
    certificate, statuses = find_exact_kernel(matrix, rng)
    return certificate, statuses, matrix


def run_canaries(forms, rng):
    cert, _, _ = search(0, (1, -1, -1, -1, -1), 2, forms, rng)
    if cert is not None:
        raise SystemExit("NEGATIVE CANARY FAILED: impossible system certified")
    cert, _, _ = search(3181, (1, 1, -1, -1, -1), 2, forms, rng)
    if cert is None:
        raise SystemExit("POSITIVE CANARY FAILED: known-good system rejected")
    print("canaries OK", flush=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard-index", type=int, required=True)
    parser.add_argument("--n-shards", type=int, required=True)
    args = parser.parse_args()
    if not 0 <= args.shard_index < args.n_shards:
        raise ValueError("invalid shard index")

    targets = [b for pos, b in enumerate(VALID_BITS)
               if pos % args.n_shards == args.shard_index]
    print(f"shard {args.shard_index}: {len(targets)} targets, split {SPLIT}",
          flush=True)

    forms2 = normal_forms(3)
    forms3 = None  # built lazily on first degree-2 failure
    rng = np.random.default_rng(SEED + args.shard_index)
    run_canaries(forms2, rng)

    start = time.time()
    results = []
    counts = {}
    for position, bits in enumerate(targets, 1):
        if family_criterion(bits, SPLIT):
            entry = dict(sigma_bits=int(bits), split=list(SPLIT),
                         outcome={"status": "FAMILY_SINGLE_CLASS"})
        else:
            certificate, statuses, matrix = search(bits, SPLIT, 2, forms2, rng)
            degree_used = 2
            if certificate is None:
                if forms3 is None:
                    forms3 = normal_forms(4)
                certificate, statuses3, matrix3 = search(bits, SPLIT, 3,
                                                         forms3, rng)
                if certificate is not None:
                    degree_used, statuses, matrix = 3, statuses3, matrix3
            if certificate is not None:
                entry = dict(sigma_bits=int(bits), split=list(SPLIT), outcome={
                    "status": "EXACT_CELLWIDE_CERTIFICATE",
                    "degree": degree_used,
                    "certificate": certificate,
                    "support_size": len(certificate),
                    "lp_statuses": statuses})
            else:
                separator, sep_status = find_exact_separator(matrix)
                entry = dict(sigma_bits=int(bits), split=list(SPLIT), outcome={
                    "status": ("EXACT_DEGREE_NO_GO" if separator is not None
                               else "EMPIRICAL_NO_GO"),
                    "separator": separator,
                    "separator_lp_status": sep_status})
        st = entry["outcome"]["status"]
        counts[st] = counts.get(st, 0) + 1
        results.append(entry)
        if position % 250 == 0 or position == len(targets):
            print(f"shard {args.shard_index}: {position}/{len(targets)} "
                  f"{counts}; elapsed={time.time()-start:.1f}s", flush=True)

    out = HERE / (f"split02_cellwide_shard_{args.shard_index:02d}"
                  f"_of_{args.n_shards:02d}.json.gz")
    write_json_gz(out, dict(schema=1, U_ints=U_INTS, split=list(SPLIT),
                            degree=2, shard_index=args.shard_index,
                            n_shards=args.n_shards, status="complete",
                            status_counts=counts,
                            seed_for_float_support_hints=SEED + args.shard_index,
                            elapsed_seconds=time.time() - start,
                            note="closes the second 2-subset split orbit; "
                                 "k=3 partners by the global flip",
                            results=results))
    print(f"shard {args.shard_index}: DONE {counts}", flush=True)


if __name__ == "__main__":
    main()
