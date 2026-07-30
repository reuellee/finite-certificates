"""Cell-wide certificates for the k = 0 split (s = all-minus); k = 5 follows
by the global flip (sigma, s) -> (-sigma, -s).

Closes the last split gap in the cell-wide chain: Stage 2b closed k = 0/5
numerically at U_ints only; the global theorem needs cell-wide symbolic
certificates. Two mechanisms, in order:

  FAMILY_SINGLE_CLASS: with s = all-minus the single-class criterion
  sigma* . s_t = -1 (t outside the class) reduces to sigma* = +1, so any
  class with both side signs +1 yields the standard single-class
  certificate, cell-wide, no search needed.

  EXACT_CELLWIDE_CERTIFICATE / EXACT_DEGREE_NO_GO: otherwise the Stage
  2c-2 degree-2 quotient-ring machinery (gp_degree3_search) with the
  all-minus split vector.

Usage: python k0_cellwide_sweep.py --shard-index I --n-shards N
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import time

import numpy as np

from common import HERE, U_INTS, VALID_BITS
from gp_degree3_search import (
    find_exact_kernel,
    find_exact_separator,
    normal_forms,
    quotient_matrix,
)

SPLIT = (-1, -1, -1, -1, -1)
DEGREE = 2
SEED = 2026073105


def family_killed(bits):
    for ci in range(10):
        if bits >> (2 * ci) & 1 and bits >> (2 * ci + 1) & 1:
            return True
    return False


def write_json_gz(path, payload):
    with path.open("wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw,
                           compresslevel=9, mtime=0) as zipped:
            with io.TextIOWrapper(zipped, encoding="utf-8") as text:
                json.dump(payload, text, separators=(",", ":"), sort_keys=True)
                text.write("\n")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard-index", type=int, required=True)
    parser.add_argument("--n-shards", type=int, required=True)
    args = parser.parse_args()
    if not 0 <= args.shard_index < args.n_shards:
        raise ValueError("invalid shard index")

    targets = [b for pos, b in enumerate(VALID_BITS)
               if pos % args.n_shards == args.shard_index]
    print(f"shard {args.shard_index}: {len(targets)} targets", flush=True)

    forms = normal_forms(DEGREE + 1)
    rng = np.random.default_rng(SEED + args.shard_index)
    start = time.time()
    results = []
    counts = {}
    for position, bits in enumerate(targets, 1):
        if family_killed(bits):
            entry = dict(sigma_bits=int(bits), k=0,
                         outcome={"status": "FAMILY_SINGLE_CLASS"})
        else:
            variables, row_keys, matrix = quotient_matrix(
                int(bits), SPLIT, DEGREE, forms)
            certificate, statuses = find_exact_kernel(matrix, rng)
            if certificate is not None:
                entry = dict(sigma_bits=int(bits), k=0, outcome={
                    "status": "EXACT_CELLWIDE_CERTIFICATE",
                    "certificate": certificate,
                    "support_size": len(certificate),
                    "lp_statuses": statuses})
            else:
                separator, sep_status = find_exact_separator(matrix)
                entry = dict(sigma_bits=int(bits), k=0, outcome={
                    "status": ("EXACT_DEGREE_NO_GO" if separator is not None
                               else "EMPIRICAL_NO_GO"),
                    "separator": separator,
                    "separator_lp_status": sep_status,
                    "lp_statuses": statuses})
        st = entry["outcome"]["status"]
        counts[st] = counts.get(st, 0) + 1
        results.append(entry)
        if position % 250 == 0 or position == len(targets):
            print(f"shard {args.shard_index}: {position}/{len(targets)} "
                  f"{counts}; elapsed={time.time()-start:.1f}s", flush=True)

    out = HERE / (f"k0_cellwide_shard_{args.shard_index:02d}"
                  f"_of_{args.n_shards:02d}.json.gz")
    write_json_gz(out, dict(schema=1, U_ints=U_INTS, split=list(SPLIT),
                            degree=DEGREE, shard_index=args.shard_index,
                            n_shards=args.n_shards, status="complete",
                            status_counts=counts,
                            seed_for_float_support_hints=SEED + args.shard_index,
                            elapsed_seconds=time.time() - start,
                            note="k=5 follows by the global flip "
                                 "(sigma,s)->(-sigma,-s)",
                            results=results))
    print(f"shard {args.shard_index}: DONE {counts}", flush=True)


if __name__ == "__main__":
    main()
