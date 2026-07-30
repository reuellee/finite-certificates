"""Deep leader search with the *true* fixed-U LP value as outer objective.

This complements the differentiable soft-min search in margin_search.py.
COBYLA moves ten spherical direction coordinates while the inner LP globally
optimizes (T, alpha, beta, margin).  Signed triple-determinant constraints keep
the search in the reference chirotope cell.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, str(Path(__file__).resolve().parent))
from incidence_enum import TRIPLES, genericity  # noqa: E402
from margin_search import (  # noqa: E402
    canonicalize_random_u,
    lp_margin,
    sigma_matrix,
)


def to_angles(u: np.ndarray) -> np.ndarray:
    u = np.asarray(u)
    theta = np.arctan2(u[:, 1], u[:, 0])
    phi = np.arcsin(np.clip(u[:, 2], -1.0, 1.0))
    return np.column_stack([theta, phi]).ravel()


def from_angles(angles: np.ndarray) -> np.ndarray:
    angles = np.asarray(angles).reshape(5, 2)
    theta = angles[:, 0]
    phi = angles[:, 1]
    return np.column_stack(
        [
            np.cos(theta) * np.cos(phi),
            np.sin(theta) * np.cos(phi),
            np.sin(phi),
        ]
    )


def signed_dets(u: np.ndarray, reference_signs: np.ndarray) -> np.ndarray:
    return (
        np.asarray([np.linalg.det(u[list(triple)]) for triple in TRIPLES])
        * reference_signs
    )


def optimize_one(
    initial_u: np.ndarray,
    sigma: np.ndarray,
    k: int,
    reference_signs: np.ndarray,
    weight_floor: float,
    generic_floor: float,
    maxiter: int,
) -> dict:
    calls = 0
    lp_failures = 0
    best_margin = -np.inf
    best_u = np.asarray(initial_u).copy()
    best_lp = None

    def constraints(angles: np.ndarray) -> np.ndarray:
        return signed_dets(from_angles(angles), reference_signs) - generic_floor

    def objective(angles: np.ndarray) -> float:
        nonlocal calls, lp_failures, best_margin, best_u, best_lp
        calls += 1
        u = from_angles(angles)
        dets = signed_dets(u, reference_signs)
        if np.min(dets) < generic_floor:
            # COBYLA also sees the explicit constraints, but this avoids asking
            # the LP about a side/chamber labeling outside the reference cell.
            return 1.0 + 100.0 * (generic_floor - np.min(dets))
        lp = lp_margin(u, sigma, k, weight_floor)
        if not lp["success"]:
            lp_failures += 1
            return 2.0
        if lp["margin"] > best_margin:
            best_margin = float(lp["margin"])
            best_u = u.copy()
            best_lp = lp
        return -float(lp["margin"])

    start = time.time()
    result = minimize(
        objective,
        to_angles(initial_u),
        method="COBYLA",
        constraints=[{"type": "ineq", "fun": constraints}],
        options={
            "maxiter": maxiter,
            "rhobeg": 0.22,
            "tol": 2e-6,
            "catol": generic_floor * 0.05,
        },
    )
    # Ensure a result exists even if the first trial was rejected unexpectedly.
    if best_lp is None:
        fallback = lp_margin(initial_u, sigma, k, weight_floor)
        if fallback["success"]:
            best_lp = fallback
            best_margin = float(fallback["margin"])
    return {
        "success": best_lp is not None,
        "best_margin": None if best_lp is None else best_margin,
        "best_U": None if best_lp is None else best_u.tolist(),
        "best_lp": best_lp,
        "calls": calls,
        "lp_failures": lp_failures,
        "elapsed_seconds": time.time() - start,
        "optimizer": {
            "success": bool(result.success),
            "status": int(result.status),
            "message": str(result.message),
            "fun": float(result.fun),
            "nfev": int(result.nfev),
        },
        "best_genericity": None if best_lp is None else genericity(best_u),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sigma-enum",
        type=Path,
        default=Path(__file__).with_name("sigma_enum.json"),
    )
    parser.add_argument(
        "--polished",
        type=Path,
        default=Path(__file__).with_name("polished.json"),
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path(__file__).resolve().parent
    )
    parser.add_argument("--top-n", type=int, default=20)
    parser.add_argument("--random-restarts", type=int, default=10)
    parser.add_argument("--maxiter", type=int, default=600)
    parser.add_argument("--weight-floor", type=float, default=1e-5)
    parser.add_argument("--generic-floor", type=float, default=2e-5)
    parser.add_argument("--seed", type=int, default=19440568)
    args = parser.parse_args()

    payload = json.loads(args.sigma_enum.read_text(encoding="utf-8"))
    polished = json.loads(args.polished.read_text(encoding="utf-8"))
    sigmas = sigma_matrix(payload["class_bits"])
    reference_signs = np.asarray(
        payload["reference_genericity"]["triple_det_signs"]
    )
    scores = np.maximum(
        np.asarray(polished["splits"]["2"]["margins"]),
        np.asarray(polished["splits"]["3"]["margins"]),
    )
    leaders = np.argsort(scores)[-args.top_n :][::-1]
    rng = np.random.default_rng(args.seed)

    output = {
        "schema": 1,
        "seed": args.seed,
        "top_n": args.top_n,
        "leader_class_indices": leaders.astype(int).tolist(),
        "random_restarts_per_class_per_split": args.random_restarts,
        "plus_reference_and_polished_starts": True,
        "maxiter": args.maxiter,
        "weight_floor": args.weight_floor,
        "generic_floor": args.generic_floor,
        "splits": {},
    }
    for k in (2, 3):
        checkpoint = np.load(args.output_dir / f"polished_k{k}.npz")
        split_records = []
        split_start = time.time()
        for leader_position, class_index in enumerate(leaders):
            starts = [
                {
                    "kind": "reference",
                    "seed": None,
                    "U": np.asarray(payload["reference_U"]),
                },
                {
                    "kind": "all_class_polished",
                    "seed": None,
                    "U": checkpoint["u"][class_index],
                },
            ]
            for _ in range(args.random_restarts):
                seed = int(rng.integers(0, 2**31 - 1))
                starts.append(
                    {
                        "kind": "canonical_random",
                        "seed": seed,
                        "U": canonicalize_random_u(
                            np.random.default_rng(seed), reference_signs
                        ),
                    }
                )
            runs = []
            for restart, start in enumerate(starts):
                run = optimize_one(
                    start["U"],
                    sigmas[class_index],
                    k,
                    reference_signs,
                    args.weight_floor,
                    args.generic_floor,
                    args.maxiter,
                )
                runs.append(
                    {
                        "restart": restart,
                        "start_kind": start["kind"],
                        "seed": start["seed"],
                        **run,
                    }
                )
            split_records.append(
                {
                    "class_index": int(class_index),
                    "class_bits": int(payload["class_bits"][class_index]),
                    "runs": runs,
                }
            )
            print(
                f"outer LP k={k}: leader {leader_position+1}/{len(leaders)} "
                f"class={class_index}, best="
                f"{max(r['best_margin'] for r in runs if r['success']):.9g}, "
                f"elapsed={time.time()-split_start:.1f}s",
                flush=True,
            )
            output["splits"][str(k)] = {"leaders": split_records}
            (args.output_dir / "outer_lp_restarts.json").write_text(
                json.dumps(output, indent=2) + "\n", encoding="utf-8"
            )
        output["splits"][str(k)]["elapsed_seconds"] = time.time() - split_start
    (args.output_dir / "outer_lp_restarts.json").write_text(
        json.dumps(output, indent=2) + "\n", encoding="utf-8"
    )
    print("wrote outer_lp_restarts.json")


if __name__ == "__main__":
    main()
