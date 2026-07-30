"""Sharded degree-2 GP sweep outside the single-class boundary.

The all-degree coefficientwise theorem already covers 33,437 labeled
systems.  This script searches every one of the complementary 32,843
systems with the exact degree-2 quotient cone used by
``gp_degree3_search.py``.
"""
from __future__ import annotations

import argparse
import gzip
import io
import json
import time
from fractions import Fraction

import numpy as np

from common import HERE, U_INTS, class_pattern, full_system_rows
from gp_degree3_search import (
    NEGATIVE_CANARY,
    find_exact_kernel,
    find_exact_separator,
    normal_forms,
    positive_control,
    quotient_matrix,
)


COVERAGE_PATH = HERE / "equal_pair_coverage.json.gz"
BOUNDARY_PATH = HERE / "coefficientwise_boundary.json.gz"
SEED = 2026073104
DEGREE = 2


def load_gz(path):
    with gzip.open(path, "rt", encoding="utf-8") as handle:
        return json.load(handle)


def write_json_gz(path, payload):
    with path.open("wb") as raw:
        with gzip.GzipFile(
            filename="", mode="wb", fileobj=raw, compresslevel=9, mtime=0
        ) as zipped:
            with io.TextIOWrapper(zipped, encoding="utf-8") as text:
                json.dump(payload, text, separators=(",", ":"), sort_keys=True)
                text.write("\n")


def check_negative_canary():
    witness = [
        Fraction(value) for value in NEGATIVE_CANARY["exact_strict_primal_witness"]
    ]
    margins = [
        sum(Fraction(a) * b for a, b in zip(row, witness))
        for row in full_system_rows(0, 1)
    ]
    if min(margins) <= 0:
        raise AssertionError("negative canary witness failed")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard-index", type=int, required=True)
    parser.add_argument("--n-shards", type=int, required=True)
    args = parser.parse_args()
    if not 0 <= args.shard_index < args.n_shards:
        raise ValueError("invalid shard index")

    start = time.time()
    check_negative_canary()
    coverage = load_gz(COVERAGE_PATH)
    boundary = load_gz(BOUNDARY_PATH)
    complement = []
    for global_index, (bits, k, key, objective1_status) in enumerate(
        coverage["systems"]
    ):
        if (
            boundary["pattern_results"][key]["status"]
            == "ALL_DEGREES_IMPOSSIBLE"
        ):
            complement.append(
                (global_index, bits, k, key, objective1_status)
            )
    if len(complement) != 32843:
        raise AssertionError("single-class complement count changed")
    targets = [
        target
        for position, target in enumerate(complement)
        if position % args.n_shards == args.shard_index
    ]

    forms = normal_forms(DEGREE + 1)
    rng = np.random.default_rng(SEED + args.shard_index)

    # Both controls are deliberately run inside every independent shard.
    control_results = []
    for target in (NEGATIVE_CANARY, positive_control()):
        bits = int(target["sigma_bits"])
        split = tuple(target["split"])
        variables, row_keys, matrix = quotient_matrix(
            bits, split, DEGREE, forms
        )
        certificate, statuses = find_exact_kernel(matrix, rng)
        if target["id"] == NEGATIVE_CANARY["id"]:
            if certificate is not None:
                raise RuntimeError("CANARY FAILURE: invalid sigma certified")
            separator, separator_status = find_exact_separator(matrix)
            if separator is None:
                raise RuntimeError("negative canary lacks exact separator")
            outcome = {
                "status": "EXACT_DEGREE_NO_GO",
                "separator": separator,
                "lp_statuses": statuses,
                "separator_lp_status": separator_status,
            }
        else:
            if certificate is None:
                raise RuntimeError("positive control failed")
            outcome = {
                "status": "EXACT_CELLWIDE_CERTIFICATE",
                "certificate": certificate,
                "lp_statuses": statuses,
            }
        control_results.append({"target": target, "outcome": outcome})
    print(
        f"shard {args.shard_index}: controls PASS; "
        f"targets={len(targets)}",
        flush=True,
    )

    results = []
    status_counts = {}
    for position, (
        global_index,
        bits,
        k,
        pattern_key,
        objective1_status,
    ) in enumerate(targets, 1):
        split = tuple(1 if t < k else -1 for t in range(5))
        variables, row_keys, matrix = quotient_matrix(
            bits, split, DEGREE, forms
        )
        certificate, statuses = find_exact_kernel(matrix, rng)
        if certificate is not None:
            outcome = {
                "status": "EXACT_CELLWIDE_CERTIFICATE",
                "certificate": certificate,
                "support_size": len(certificate),
                "n_variables": len(variables),
                "n_quotient_rows": len(row_keys),
                "lp_statuses": statuses,
            }
        else:
            separator, separator_status = find_exact_separator(matrix)
            outcome = {
                "status": (
                    "EXACT_DEGREE_NO_GO"
                    if separator is not None
                    else "EMPIRICAL_NO_GO"
                ),
                "separator": separator,
                "n_variables": len(variables),
                "n_quotient_rows": len(row_keys),
                "lp_statuses": statuses,
                "separator_lp_status": separator_status,
            }
        status_counts[outcome["status"]] = (
            status_counts.get(outcome["status"], 0) + 1
        )
        results.append({
            "global_system_index": global_index,
            "sigma_bits": bits,
            "k": k,
            "pattern_key": pattern_key,
            "objective1_status": objective1_status,
            "outcome": outcome,
        })
        if position % 250 == 0 or position == len(targets):
            print(
                f"shard {args.shard_index}: {position}/{len(targets)} "
                f"{status_counts}; elapsed={time.time() - start:.1f}s",
                flush=True,
            )

    output = HERE / (
        f"gp_all_d2_shard_{args.shard_index:02d}_of_{args.n_shards:02d}.json.gz"
    )
    payload = {
        "schema": 1,
        "status": "complete",
        "degree": DEGREE,
        "shard_index": args.shard_index,
        "n_shards": args.n_shards,
        "U_ints": [list(row) for row in U_INTS],
        "n_global_complement_systems": len(complement),
        "n_targets": len(targets),
        "target_partition": (
            "Position in the 32,843-system single-class complement modulo "
            "n_shards equals shard_index."
        ),
        "controls": control_results,
        "status_counts": status_counts,
        "results": results,
        "seed_for_float_support_hints": SEED + args.shard_index,
        "elapsed_seconds": time.time() - start,
    }
    write_json_gz(output, payload)
    print(f"wrote {output} ({output.stat().st_size} bytes)", flush=True)


if __name__ == "__main__":
    main()
