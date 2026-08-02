#!/usr/bin/env python3
"""Rebuild the exact realization certificate refuting four-chart SEEAT.

The search is deterministic but is not trusted: four_chart_gate.py and
verify_four_chart_obstruction.py recompute every catalog match and every
bracket in exact arithmetic.  On four laptop cores this builder takes about a
minute for the current code and data.
"""

import argparse
from collections import Counter
import multiprocessing as mp
from pathlib import Path
import sys
import time

import numpy as np

import four_chart_gate as gate


_GEOM = None
_REALIZE = None
_CHIROTOPES = None


def initialize_worker(chirotopes):
    global _GEOM, _REALIZE, _CHIROTOPES
    import realize

    _REALIZE = realize
    _GEOM = realize.Geom(9, 4)
    _CHIROTOPES = chirotopes


def realize_one(index):
    chi = _CHIROTOPES[index]
    stages = (
        ("A", 0 + index, dict(tries=2, sweeps=15, rerolls=3, wall_budget=3)),
        ("C", 1_000_003 + index, dict(tries=8, sweeps=40, rerolls=8, wall_budget=12)),
        ("D", 31_337 + index, dict(tries=60, sweeps=120, rerolls=10, wall_budget=90)),
    )
    matrix = None
    stage = None
    for name, seed, options in stages:
        matrix, _info = _REALIZE.realize(chi, _GEOM, seed=seed, **options)
        if matrix is not None:
            stage = name
            break
    if matrix is None:
        matrix, _info = _REALIZE.realize_via_mutant(
            chi, _GEOM, seed=90_001 + index, kmax=20, attempts=3
        )
        stage = "E" if matrix is not None else "OPEN"
    if matrix is None:
        return index, stage, None
    signs = _REALIZE.exact_bracket_signs(matrix, _GEOM)
    if signs is None or not np.array_equal(signs, chi):
        raise AssertionError(f"search returned a bad matrix at child {index}")
    return index, stage, matrix


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument(
        "--out",
        type=Path,
        default=gate.HERE / "data" / "seeat_parent2599_realizations.npz",
    )
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    if args.out.exists() and not args.force:
        raise SystemExit(f"{args.out} exists; pass --force to replace it")

    parents = [line.strip() for line in gate.CATALOG_48.open() if line.strip()]
    parent_bits, signatures = gate.enumerate_extensions(parents[gate.PARENT_INDEX])
    assert len(signatures) == gate.EXPECTED_EXTENSIONS

    # Use the checker-side canonicalizer, not the catalog generator.
    sys.path.insert(0, str(gate.OMMINOR))
    import minorlib as ml

    extension_bits = gate.extension_bit_matrix(parent_bits, signatures)
    hi, lo, _nargmax, valid = ml.canon_keys(9, 4, extension_bits, batch=500)
    assert valid.all()
    multiplicities = Counter((int(h), int(l)) for h, l in zip(hi, lo))
    keys = sorted(multiplicities)
    assert len(keys) == gate.EXPECTED_CHILD_CLASSES

    key_hi = np.asarray([key[0] for key in keys], dtype=np.uint64)
    key_lo = np.asarray([key[1] for key in keys], dtype=np.uint64)
    mult = np.asarray([multiplicities[key] for key in keys], dtype=np.int32)
    bits = ml.cc().decode_keys(ml.tables(9, 4), key_hi, key_lo)
    chirotopes = np.where(bits, 1, -1).astype(np.int8)

    matrices = np.zeros((len(keys), 4, 9), dtype=np.int64)
    stage_counts = Counter()
    started = time.time()
    with mp.Pool(
        args.workers, initializer=initialize_worker, initargs=(chirotopes,)
    ) as pool:
        jobs = pool.imap_unordered(realize_one, range(len(keys)), chunksize=4)
        for completed, (index, stage, matrix) in enumerate(jobs, 1):
            stage_counts[stage] += 1
            if matrix is None:
                raise SystemExit(f"child class {index} remained OPEN")
            matrices[index] = matrix
            if completed % 500 == 0:
                print(
                    f"{completed}/{len(keys)} exact matrices; "
                    f"{time.time() - started:.1f}s",
                    flush=True,
                )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.out,
        format=np.asarray("seeat-parent2599-realizations-v1"),
        parent_index=np.asarray(gate.PARENT_INDEX, dtype=np.int64),
        key_hi=key_hi,
        key_lo=key_lo,
        multiplicity=mult,
        matrix=matrices,
    )
    gate.verify_realization_certificate(args.out, multiplicities, progress=True)
    print(f"WROTE {args.out} ({args.out.stat().st_size} bytes)")
    print(f"stages {dict(sorted(stage_counts.items()))}")


if __name__ == "__main__":
    main()
