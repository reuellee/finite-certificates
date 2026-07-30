"""Reconstruct and independently check a positive-margin candidate.

Uses the same 1e-9 coordinate deduplication and unjoggled SciPy ConvexHull
convention as search_maxout67.py.  It also checks all 20 facet-side signs and
the deterministic 22-chamber NAE condition before saving instance_44.json.
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np
from scipy.optimize import linprog
from scipy.spatial import ConvexHull

sys.path.insert(0, str(Path(__file__).resolve().parent))
from incidence_enum import deterministic_build, genericity  # noqa: E402
from margin_search import numpy_rows, sigma_matrix  # noqa: E402


def signs(n: int) -> np.ndarray:
    return np.asarray(list(itertools.product((-1.0, 1.0), repeat=n)))


def candidates(
    m: np.ndarray, u: np.ndarray, a: np.ndarray, b: np.ndarray
) -> np.ndarray:
    s = signs(len(a))
    center_a = (a[:, None] * m).sum(axis=0)
    center_b = (b[:, None] * m).sum(axis=0)
    pa = center_a + s @ (a[:, None] * u)
    pb = center_b + s @ (b[:, None] * u)
    return np.vstack([pa, pb])


def hull_count(
    m: np.ndarray, u: np.ndarray, a: np.ndarray, b: np.ndarray
) -> tuple[int, np.ndarray, ConvexHull]:
    points = candidates(m, u, a, b)
    unique = np.unique(np.round(points, 9), axis=0)
    hull = ConvexHull(unique)
    return len(hull.vertices), unique, hull


def in_cone(vector: np.ndarray, generators: np.ndarray) -> bool:
    result = linprog(
        np.zeros(len(generators)),
        A_eq=generators.T,
        b_eq=vector,
        bounds=[(0.0, None)] * len(generators),
        method="highs",
    )
    return result.status == 0


def chamber_bicoloring_count(
    u: np.ndarray,
    t: np.ndarray,
    alpha: np.ndarray,
    beta: np.ndarray,
    k: int,
) -> tuple[int, list[dict]]:
    _, chambers, _ = deterministic_build(u)
    details = []
    count = 0
    for eps_list in chambers:
        eps = np.asarray(eps_list)
        w = (
            (
                alpha[:, None]
                * (eps[:k, None] * u[:k])
            ).sum(axis=0)
            - (
                beta[:, None]
                * (eps[k:, None] * u[k:])
            ).sum(axis=0)
        )
        value = t + w
        cone_generators = eps[:, None] * u
        positive_cone = in_cone(value, cone_generators)
        negative_cone = in_cone(-value, cone_generators)
        bicolored = not (positive_cone or negative_cone)
        count += int(bicolored)
        details.append(
            {
                "chamber": eps_list,
                "bicolored": bicolored,
                "in_positive_cone": positive_cone,
                "in_negative_cone": negative_cone,
            }
        )
    return count, details


def reconstruct(best: dict, sigma_payload: dict) -> dict:
    u = np.asarray(best["U"], dtype=float)
    x = np.asarray(best["x"], dtype=float)
    k = int(best["k"])
    t = x[:3]
    weights = x[3:8]
    alpha = weights[:k]
    beta = weights[k:]
    if np.min(weights) <= 0:
        raise ValueError("candidate weights are not all positive")
    m = np.zeros((5, 3))
    m[0] = t / alpha[0]
    a = np.concatenate([2.0 * alpha, beta])
    b = np.concatenate([alpha, 2.0 * beta])
    sigma = sigma_matrix([best["class_bits"]])[0]
    side_margins = sigma * (numpy_rows(u, k) @ x)
    _, chambers, ch_rays = deterministic_build(u)
    actual_side_signs = np.where(side_margins > 0, sigma, -sigma)
    nae = [
        len(set(map(int, actual_side_signs[sides]))) >= 2 for sides in ch_rays
    ]
    vertex_count, unique_points, hull = hull_count(m, u, a, b)
    bicolored_count, chamber_details = chamber_bicoloring_count(
        u, t, alpha, beta, k
    )
    return {
        "schema": 1,
        "construction": (
            "M[0]=T/alpha[0], other midpoints zero; "
            "a=(2*alpha,beta), b=(alpha,2*beta)"
        ),
        "source_best_record": best,
        "sigma": sigma.astype(int).tolist(),
        "U": u.tolist(),
        "T": t.tolist(),
        "alpha": alpha.tolist(),
        "beta": beta.tolist(),
        "k": k,
        "M": m.tolist(),
        "a": a.tolist(),
        "b": b.tolist(),
        "checks": {
            "genericity": genericity(u),
            "n_chambers": len(chambers),
            "minimum_normalized_side_margin": float(np.min(side_margins)),
            "all_normalized_side_margins": side_margins.tolist(),
            "all_chambers_NAE_from_side_signs": bool(all(nae)),
            "NAE_by_chamber": nae,
            "bicolored_chambers_cone_LP": bicolored_count,
            "chamber_cone_details": chamber_details,
            "raw_candidates": 64,
            "unique_candidates_after_round_1e_9": len(unique_points),
            "float_hull_vertices_no_joggle": vertex_count,
            "hull_equations": len(hull.equations),
        },
        "sigma_enum_reference": {
            "reference_U": sigma_payload["reference_U"],
            "class_index": best["class_index"],
            "class_bits": best["class_bits"],
        },
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--margins", type=Path, default=Path(__file__).with_name("margins.json")
    )
    parser.add_argument(
        "--sigma-enum",
        type=Path,
        default=Path(__file__).with_name("sigma_enum.json"),
    )
    parser.add_argument(
        "--out", type=Path, default=Path(__file__).with_name("instance_44.json")
    )
    parser.add_argument("--minimum-margin", type=float, default=1e-6)
    args = parser.parse_args()
    margins = json.loads(args.margins.read_text(encoding="utf-8"))
    sigma_payload = json.loads(args.sigma_enum.read_text(encoding="utf-8"))
    best = margins["best"]
    if best["margin"] <= args.minimum_margin:
        print(
            f"best margin {best['margin']:.10g} does not exceed "
            f"{args.minimum_margin}; not writing an instance"
        )
        return
    result = reconstruct(best, sigma_payload)
    checks = result["checks"]
    if (
        checks["n_chambers"] != 22
        or not checks["all_chambers_NAE_from_side_signs"]
        or checks["bicolored_chambers_cone_LP"] != 22
        or checks["float_hull_vertices_no_joggle"] != 44
    ):
        raise RuntimeError(
            "positive margin candidate failed reconstruction: "
            + json.dumps(
                {
                    key: checks[key]
                    for key in (
                        "n_chambers",
                        "all_chambers_NAE_from_side_signs",
                        "bicolored_chambers_cone_LP",
                        "float_hull_vertices_no_joggle",
                    )
                }
            )
        )
    args.out.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"verified 44 float hull vertices; wrote {args.out}")


if __name__ == "__main__":
    main()
