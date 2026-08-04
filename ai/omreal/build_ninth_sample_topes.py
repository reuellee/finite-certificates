#!/usr/bin/env python3
"""Build a discovery-only tope matrix for the 178 row-2599 sample charts.

This is a roadmap search aid, not a proof artifact.  For each exact integer
parent chart in ``seeat_parent2599_upper178.npz`` it enumerates the topes of
the 56-plane derived arrangement from its rank-one flats.  Structural
non-simple flats are handled by enumerating the localized rank-three
arrangement in a transverse space.  A generic rank-four arrangement on 56
planes has 26,112 oriented topes; that count is required for every chart.

Floating point is used only to discover sign vectors.  Any family selected
from the output must be rechecked with exact extension witnesses/Gordan
certificates and with an exact path or separator certificate before it can
support a theorem.
"""

from __future__ import annotations

import argparse
from itertools import combinations
from multiprocessing import Pool
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import four_chart_gate as gate
from verify_seeat_upper_bound import chart_rows_and_parent


SOURCE = HERE / "data" / "seeat_parent2599_upper178.npz"
DEFAULT_OUTPUT = Path("/tmp/ninth_parent2599_sample_topes.npz")
EXPECTED_TOPES = 26_112
FULL_MASK = (1 << 56) - 1


def null_vector_3x4(matrix: np.ndarray) -> np.ndarray:
    """Alternating maximal minors of a numerical 3-by-4 matrix."""
    return np.asarray(
        [
            np.linalg.det(matrix[:, 1:]),
            -np.linalg.det(matrix[:, (0, 2, 3)]),
            np.linalg.det(matrix[:, (0, 1, 3)]),
            -np.linalg.det(matrix[:, :3]),
        ]
    )


def transverse_basis(ray: np.ndarray) -> np.ndarray:
    """Return a stable orthonormal basis of the complement of ``ray``."""
    _, _, vh = np.linalg.svd(ray.reshape(1, 4))
    return vh[1:].T


def localized_topes(rows: np.ndarray, tolerance: float) -> set[int]:
    """Enumerate topes of an essential central rank-three arrangement.

    Every spherical chamber has a vertex.  At a possibly non-simple vertex,
    the incident great circles give a two-dimensional fan; sampling one angle
    between every consecutive pair of fan rays enumerates all local sectors.
    """
    answer: set[int] = set()
    count = len(rows)
    for first, second in combinations(range(count), 2):
        ray = np.cross(rows[first], rows[second])
        norm = np.linalg.norm(ray)
        if norm <= tolerance:
            continue
        ray /= norm
        for orientation in (1.0, -1.0):
            point = orientation * ray
            values = rows @ point
            zero = np.flatnonzero(np.abs(values) <= tolerance)

            seed = np.eye(3)[int(np.argmin(np.abs(point)))]
            u = seed - point * np.dot(seed, point)
            u /= np.linalg.norm(u)
            v = np.cross(point, u)

            critical: list[float] = []
            for index in zero:
                alpha = float(rows[index] @ u)
                beta = float(rows[index] @ v)
                angle = float(np.arctan2(-alpha, beta) % (2 * np.pi))
                critical.extend((angle, float((angle + np.pi) % (2 * np.pi))))
            critical.sort()
            unique: list[float] = []
            for angle in critical:
                if not unique or abs(
                    ((angle - unique[-1] + np.pi) % (2 * np.pi)) - np.pi
                ) > 100 * tolerance:
                    unique.append(angle)
            if not unique:
                continue

            zero_set = set(map(int, zero))
            for left, right in zip(unique, unique[1:] + [unique[0] + 2 * np.pi]):
                angle = (left + right) / 2
                direction = np.cos(angle) * u + np.sin(angle) * v
                perturbed = rows @ direction
                mask = 0
                for index in range(count):
                    value = perturbed[index] if index in zero_set else values[index]
                    if value > 0:
                        mask |= 1 << index
                answer.add(mask)
    return answer


def chart_topes(task: tuple[int, np.ndarray, float]) -> tuple[int, np.ndarray]:
    chart_index, matrix, tolerance = task
    _, exact_rows = chart_rows_and_parent(matrix)
    rows = np.asarray(exact_rows, dtype=float)
    rows /= np.linalg.norm(rows, axis=1)[:, None]

    topes: set[int] = set()
    seen_rays: set[tuple[int, ...]] = set()
    for support in combinations(range(56), 3):
        ray = null_vector_3x4(rows[list(support)])
        norm = np.linalg.norm(ray)
        if norm <= tolerance:
            continue
        ray /= norm
        first_nonzero = int(np.flatnonzero(np.abs(ray) > tolerance)[0])
        if ray[first_nonzero] < 0:
            ray = -ray
        key = tuple(np.rint(ray / (100 * tolerance)).astype(np.int64))
        if key in seen_rays:
            continue
        seen_rays.add(key)

        values = rows @ ray
        zero = np.flatnonzero(np.abs(values) <= 10 * tolerance)
        zero_mask = sum(1 << int(index) for index in zero)
        positive = sum((int(value > 0) << index) for index, value in enumerate(values))
        positive &= ~zero_mask
        negative = sum((int(value < 0) << index) for index, value in enumerate(values))
        negative &= ~zero_mask

        if len(zero) == 3:
            local_masks = range(8)
            for local in local_masks:
                global_mask = 0
                for bit, index in enumerate(zero):
                    if (local >> bit) & 1:
                        global_mask |= 1 << int(index)
                topes.add(positive | global_mask)
                topes.add(negative | global_mask)
            continue

        local_rows = rows[zero] @ transverse_basis(ray)
        for local in localized_topes(local_rows, 10 * tolerance):
            global_mask = 0
            for bit, index in enumerate(zero):
                if (local >> bit) & 1:
                    global_mask |= 1 << int(index)
            topes.add(positive | global_mask)
            topes.add(negative | global_mask)

    if len(topes) != EXPECTED_TOPES:
        raise RuntimeError(
            f"chart {chart_index}: found {len(topes)} topes, expected {EXPECTED_TOPES}"
        )
    return chart_index, np.asarray(sorted(topes), dtype=np.uint64)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--tolerance", type=float, default=1e-9)
    args = parser.parse_args()

    source = np.load(args.source, allow_pickle=False)
    charts = source["chart_matrix"]
    tasks = [(index, chart, args.tolerance) for index, chart in enumerate(charts)]
    with Pool(processes=args.workers) as pool:
        rows = list(pool.imap_unordered(chart_topes, tasks))
    rows.sort(key=lambda item: item[0])

    parent_text = gate.CATALOG_48.read_text(encoding="utf-8").splitlines()[
        gate.PARENT_INDEX
    ]
    _, signatures = gate.enumerate_extensions(parent_text)
    signature_index = {int(signature): index for index, signature in enumerate(signatures)}
    support = np.zeros((len(charts), len(signatures)), dtype=np.bool_)
    for chart_index, topes in rows:
        for signature in map(int, topes):
            try:
                support[chart_index, signature_index[signature]] = True
            except KeyError as error:
                raise RuntimeError(
                    f"chart {chart_index}: derived tope is not an abstract extension"
                ) from error

    args.output.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        args.output,
        format=np.asarray("ninth-parent2599-sample-topes-discovery-v1"),
        parent_index=np.asarray(gate.PARENT_INDEX, dtype=np.int64),
        signature=np.asarray(signatures, dtype=np.uint64),
        support_packed=np.packbits(support, axis=1),
        chart_count=np.asarray(len(charts), dtype=np.int64),
        signature_count=np.asarray(len(signatures), dtype=np.int64),
        tope_count=np.asarray(EXPECTED_TOPES, dtype=np.int64),
    )
    print(f"WROTE {args.output}")
    print(f"DISCOVERY: {len(charts)} charts x {len(signatures)} signatures")
    print(f"REGRESSION: every chart has exactly {EXPECTED_TOPES} topes")
    print("CAVEAT: selected families still require independent exact certificates")


if __name__ == "__main__":
    main()
