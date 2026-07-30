"""Seeded sigma-complete numerical max-margin search for (3,5).

Combinatorial completeness comes from incidence_enum.py.  Numerical global
optimization is not complete: every sigma class gets a fixed-U exact LP and a
batched joint-U local run, while the leaders receive many deeper restarts.

The sign constraints are homogeneous in x=(T,alpha,beta), so the stated
row-normalized margin is scale-unbounded without a gauge.  We impose

    sum(alpha)+sum(beta) = 1,  alpha,beta >= weight_floor.

For fixed U and sigma, maximizing the true minimum margin is then a tiny LP.
The joint-U stage uses a differentiable soft minimum, followed by the exact LP
at the optimized U.  A chirotope barrier keeps the literal side/chamber
incidence equal to the reference incidence.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import sys
import time
from pathlib import Path

import numpy as np
from scipy.optimize import linprog

try:
    import torch
except ImportError as exc:  # pragma: no cover
    raise SystemExit("margin_search.py requires torch") from exc

sys.path.insert(0, str(Path(__file__).resolve().parent))
from incidence_enum import PAIRS, TRIPLES, genericity, unit_rows  # noqa: E402


def sigma_matrix(class_bits: list[int]) -> np.ndarray:
    bits = np.asarray(class_bits, dtype=np.uint32)
    positions = np.arange(20, dtype=np.uint32)
    return np.where((bits[:, None] >> positions[None, :]) & 1, 1.0, -1.0)


def numpy_rows(u: np.ndarray, k: int) -> np.ndarray:
    """The 20 normalized constraint rows in facet_lp side order."""
    u = unit_rows(u)
    rows = []
    for i, j in PAIRS:
        r = np.cross(u[i], u[j])
        r /= np.linalg.norm(r)
        w = np.abs(u @ r)
        w[[i, j]] = 0.0
        w[k:] *= -1.0
        for normal in (r, -r):
            row = np.concatenate([normal, w])
            rows.append(row / np.linalg.norm(row))
    return np.asarray(rows)


def lp_margin(
    u: np.ndarray,
    sigma: np.ndarray,
    k: int,
    weight_floor: float,
    t_bound: float = 50.0,
    include_dual: bool = False,
) -> dict:
    """Maximize the true minimum normalized margin at fixed U."""
    rows = numpy_rows(u, k)
    # Variables are T[3], weights[5], margin t.
    a_ub = np.column_stack([-sigma[:, None] * rows, np.ones(20)])
    a_eq = np.zeros((1, 9))
    a_eq[0, 3:8] = 1.0
    result = linprog(
        np.r_[np.zeros(8), -1.0],
        A_ub=a_ub,
        b_ub=np.zeros(20),
        A_eq=a_eq,
        b_eq=np.ones(1),
        bounds=[(-t_bound, t_bound)] * 3
        + [(weight_floor, 1.0)] * 5
        + [(None, None)],
        method="highs",
    )
    if not result.success:
        return {
            "success": False,
            "status": int(result.status),
            "message": str(result.message),
            "margin": None,
            "x": None,
        }
    x = result.x[:8]
    actual = sigma * (rows @ x)
    payload = {
        "success": True,
        "status": int(result.status),
        "message": str(result.message),
        "margin": float(np.min(actual)),
        "reported_lp_margin": float(result.x[8]),
        "x": x.tolist(),
        "active_sides": np.flatnonzero(
            actual <= np.min(actual) + 2e-7
        ).astype(int).tolist(),
        "all_side_margins": actual.tolist(),
    }
    if include_dual:
        # For HiGHS' minimization convention the useful nonnegative
        # multipliers of our <= inequalities are -marginals.
        payload["dual"] = {
            "side_multipliers": (-result.ineqlin.marginals).tolist(),
            "inequality_residuals": result.ineqlin.residual.tolist(),
            "equality_marginal": result.eqlin.marginals.tolist(),
            "lower_bound_marginals": result.lower.marginals.tolist(),
            "upper_bound_marginals": result.upper.marginals.tolist(),
            "sum_side_multipliers": float(
                np.sum(-result.ineqlin.marginals)
            ),
        }
    return payload


def canonicalize_random_u(
    rng: np.random.Generator, reference_signs: np.ndarray, attempts: int = 20
) -> np.ndarray:
    """Map a random generic labeled configuration to the reference chirotope.

    We exhaust the 120 row permutations and 32 row reorientations.  For five
    elements every tested generic configuration has admitted such a map.
    """
    for _ in range(attempts):
        source = unit_rows(rng.normal(size=(5, 3)))
        for perm in itertools.permutations(range(5)):
            up = source[list(perm)]
            for flip_bits in range(32):
                flips = np.asarray(
                    [1.0 if flip_bits & (1 << i) else -1.0 for i in range(5)]
                )
                candidate = up * flips[:, None]
                signs = np.asarray(genericity(candidate)["triple_det_signs"])
                if np.array_equal(signs, reference_signs):
                    return candidate
    raise RuntimeError("could not canonicalize a random U to the reference chirotope")


def torch_rows(u_raw: torch.Tensor, k: int) -> tuple[torch.Tensor, torch.Tensor]:
    """Batched rows and normalized U. u_raw shape: (batch,5,3)."""
    u = torch.nn.functional.normalize(u_raw, dim=2)
    row_chunks = []
    for i, j in PAIRS:
        r = torch.linalg.cross(u[:, i], u[:, j], dim=1)
        r = torch.nn.functional.normalize(r, dim=1)
        dots = torch.abs(torch.einsum("btd,bd->bt", u, r))
        mask = torch.ones(5, dtype=u.dtype, device=u.device)
        mask[i] = 0.0
        mask[j] = 0.0
        w = dots * mask
        if k < 5:
            split_sign = torch.ones(5, dtype=u.dtype, device=u.device)
            split_sign[k:] = -1.0
            w = w * split_sign
        plus = torch.cat([r, w], dim=1)
        minus = torch.cat([-r, w], dim=1)
        row_chunks.extend([plus, minus])
    rows = torch.stack(row_chunks, dim=1)
    rows = torch.nn.functional.normalize(rows, dim=2)
    return rows, u


def torch_signed_determinants(
    u: torch.Tensor, reference_signs: torch.Tensor
) -> torch.Tensor:
    dets = []
    for triple in TRIPLES:
        dets.append(torch.linalg.det(u[:, list(triple), :]))
    return torch.stack(dets, dim=1) * reference_signs[None, :]


def optimize_batch(
    sigmas: np.ndarray,
    initial_u: np.ndarray,
    initial_x: np.ndarray,
    k: int,
    reference_signs: np.ndarray,
    *,
    steps: int,
    lr: float,
    tau_start: float,
    tau_end: float,
    weight_floor: float,
    generic_floor: float,
    barrier_strength: float,
    seed: int,
) -> dict:
    """Joint local optimization of one independent U/x per sigma."""
    torch.manual_seed(seed)
    dtype = torch.float64
    sigma_t = torch.as_tensor(sigmas, dtype=dtype)
    u_raw = torch.nn.Parameter(torch.as_tensor(initial_u, dtype=dtype).clone())
    t_param = torch.nn.Parameter(torch.as_tensor(initial_x[:, :3], dtype=dtype).clone())
    init_weights = np.maximum(initial_x[:, 3:8], weight_floor)
    init_weights /= init_weights.sum(axis=1, keepdims=True)
    logits0 = np.log(init_weights)
    logits0 -= logits0.mean(axis=1, keepdims=True)
    logits = torch.nn.Parameter(torch.as_tensor(logits0, dtype=dtype))
    ref_t = torch.as_tensor(reference_signs, dtype=dtype)
    optimizer = torch.optim.Adam([u_raw, t_param, logits], lr=lr)

    best_soft = np.full(len(sigmas), -np.inf)
    best_true = np.full(len(sigmas), -np.inf)
    best_u = np.asarray(initial_u).copy()
    best_x = np.asarray(initial_x).copy()
    trace = []
    t0 = time.time()

    for step in range(steps):
        fraction = step / max(1, steps - 1)
        tau = tau_start * (tau_end / tau_start) ** fraction
        optimizer.zero_grad()
        rows, u = torch_rows(u_raw, k)
        weights = torch.softmax(logits, dim=1)
        weights = weight_floor + (1.0 - 5.0 * weight_floor) * weights
        x = torch.cat([t_param, weights], dim=1)
        margins = sigma_t * torch.einsum("bsd,bd->bs", rows, x)
        softmin = -tau * torch.logsumexp(-margins / tau, dim=1)
        signed_dets = torch_signed_determinants(u, ref_t)
        barrier = torch.relu(generic_floor - signed_dets).square().mean(dim=1)
        # Mean makes the update scale independent of batch size.
        loss = (-softmin + barrier_strength * barrier).mean()
        loss.backward()
        torch.nn.utils.clip_grad_norm_([u_raw, t_param, logits], 20.0)
        optimizer.step()

        with torch.no_grad():
            true_min = margins.min(dim=1).values
            eligible = signed_dets.min(dim=1).values > 0.25 * generic_floor
            soft_np = softmin.cpu().numpy()
            true_np = true_min.cpu().numpy()
            update = eligible.cpu().numpy() & (true_np > best_true)
            if np.any(update):
                best_soft[update] = soft_np[update]
                best_true[update] = true_np[update]
                best_u[update] = u[update].cpu().numpy()
                best_x[update] = x[update].cpu().numpy()
            if step in {0, steps // 4, steps // 2, 3 * steps // 4, steps - 1}:
                trace.append(
                    {
                        "step": step,
                        "tau": tau,
                        "median_true_min": float(torch.median(true_min)),
                        "max_true_min": float(torch.max(true_min)),
                        "min_signed_det": float(torch.min(signed_dets)),
                        "elapsed_seconds": time.time() - t0,
                    }
                )
    return {
        "best_soft": best_soft,
        "best_true": best_true,
        "best_u": best_u,
        "best_x": best_x,
        "trace": trace,
        "elapsed_seconds": time.time() - t0,
    }


def run_fixed_screen(
    payload: dict,
    output_dir: Path,
    weight_floor: float,
) -> dict:
    u0 = np.asarray(payload["reference_U"])
    sigmas = sigma_matrix(payload["class_bits"])
    result = {
        "schema": 1,
        "weight_floor": weight_floor,
        "reference_U": u0.tolist(),
        "splits": {},
    }
    for k in (2, 3):
        start = time.time()
        margins = np.empty(len(sigmas))
        xs = np.empty((len(sigmas), 8))
        active = []
        failures = []
        for index, sigma in enumerate(sigmas):
            lp = lp_margin(u0, sigma, k, weight_floor)
            if lp["success"]:
                margins[index] = lp["margin"]
                xs[index] = lp["x"]
                active.append(lp["active_sides"])
            else:
                margins[index] = np.nan
                xs[index] = np.nan
                active.append([])
                failures.append({"class_index": index, **lp})
            if (index + 1) % 2000 == 0:
                print(
                    f"fixed screen k={k}: {index+1}/{len(sigmas)} "
                    f"in {time.time()-start:.1f}s",
                    flush=True,
                )
        result["splits"][str(k)] = {
            "margins": margins.tolist(),
            "x": xs.tolist(),
            "active_sides": active,
            "failures": failures,
            "elapsed_seconds": time.time() - start,
        }
        checkpoint = output_dir / "fixed_screen.json"
        checkpoint.write_text(json.dumps(result) + "\n", encoding="utf-8")
    return result


def run_all_class_joint(
    payload: dict,
    fixed: dict,
    output_dir: Path,
    *,
    batch_size: int,
    steps: int,
    weight_floor: float,
    master_seed: int,
) -> dict:
    u0 = np.asarray(payload["reference_U"])
    ref_signs = np.asarray(payload["reference_genericity"]["triple_det_signs"])
    all_sigmas = sigma_matrix(payload["class_bits"])
    rng = np.random.default_rng(master_seed)
    result = {
        "schema": 1,
        "master_seed": master_seed,
        "batch_size": batch_size,
        "steps": steps,
        "splits": {},
    }
    for k in (2, 3):
        fixed_x = np.asarray(fixed["splits"][str(k)]["x"])
        n = len(all_sigmas)
        best_true = np.full(n, -np.inf)
        best_soft = np.full(n, -np.inf)
        best_u = np.repeat(u0[None, :, :], n, axis=0)
        best_x = fixed_x.copy()
        traces = []
        start = time.time()
        for lo in range(0, n, batch_size):
            hi = min(n, lo + batch_size)
            # Small class-specific perturbations give each optimization its own U
            # while remaining well inside the reference chirotope cell.
            initial_u = np.repeat(u0[None, :, :], hi - lo, axis=0)
            initial_u += rng.normal(scale=0.035, size=initial_u.shape)
            # Rarely a perturbation can cross a determinant wall before the
            # barrier gets its first step. Reset such starts to the reference
            # instead of letting an ineligible initializer survive as "best".
            for local_index in range(hi - lo):
                signs = np.asarray(
                    genericity(initial_u[local_index])["triple_det_signs"]
                )
                if not np.array_equal(signs, ref_signs):
                    initial_u[local_index] = u0
            batch_seed = int(rng.integers(0, 2**31 - 1))
            run = optimize_batch(
                all_sigmas[lo:hi],
                initial_u,
                fixed_x[lo:hi],
                k,
                ref_signs,
                steps=steps,
                lr=0.025,
                tau_start=0.04,
                tau_end=0.004,
                weight_floor=weight_floor,
                generic_floor=0.012,
                barrier_strength=35.0,
                seed=batch_seed,
            )
            best_true[lo:hi] = run["best_true"]
            best_soft[lo:hi] = run["best_soft"]
            best_u[lo:hi] = run["best_u"]
            best_x[lo:hi] = run["best_x"]
            traces.append(
                {
                    "lo": lo,
                    "hi": hi,
                    "seed": batch_seed,
                    "elapsed_seconds": run["elapsed_seconds"],
                    "trace": run["trace"],
                }
            )
            print(
                f"joint k={k}: {hi}/{n}; batch max true "
                f"{np.max(run['best_true']):.7g}; total {time.time()-start:.1f}s",
                flush=True,
            )
        np.savez_compressed(
            output_dir / f"joint_k{k}.npz",
            best_true=best_true,
            best_soft=best_soft,
            best_u=best_u,
            best_x=best_x,
        )
        result["splits"][str(k)] = {
            "checkpoint": f"joint_k{k}.npz",
            "traces": traces,
            "elapsed_seconds": time.time() - start,
        }
        (output_dir / "joint_log.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8"
        )
    return result


def polish_joint_checkpoints(
    payload: dict,
    fixed: dict,
    output_dir: Path,
    weight_floor: float,
) -> dict:
    sigmas = sigma_matrix(payload["class_bits"])
    reference_signs = np.asarray(
        payload["reference_genericity"]["triple_det_signs"]
    )
    polished = {"schema": 1, "weight_floor": weight_floor, "splits": {}}
    for k in (2, 3):
        checkpoint = np.load(output_dir / f"joint_k{k}.npz")
        us = checkpoint["best_u"]
        fixed_margins = np.asarray(fixed["splits"][str(k)]["margins"])
        margins = np.empty(len(sigmas))
        xs = np.empty((len(sigmas), 8))
        active = []
        failures = []
        start = time.time()
        for index, (u, sigma) in enumerate(zip(us, sigmas)):
            current_genericity = genericity(u)
            same_chirotope = np.array_equal(
                np.asarray(current_genericity["triple_det_signs"]),
                reference_signs,
            )
            lp = (
                lp_margin(u, sigma, k, weight_floor)
                if same_chirotope
                else {
                    "success": False,
                    "status": -2,
                    "message": (
                        "rejected learned U: chirotope differs from reference"
                    ),
                    "margin": None,
                    "x": None,
                }
            )
            if lp["success"]:
                # Fixed-U is always a legitimate fallback if joint optimization
                # wandered to a worse U.
                if lp["margin"] >= fixed_margins[index]:
                    margins[index] = lp["margin"]
                    xs[index] = lp["x"]
                    active.append(lp["active_sides"])
                else:
                    margins[index] = fixed_margins[index]
                    xs[index] = np.asarray(fixed["splits"][str(k)]["x"][index])
                    active.append(fixed["splits"][str(k)]["active_sides"][index])
                    us[index] = np.asarray(payload["reference_U"])
            else:
                margins[index] = fixed_margins[index]
                xs[index] = np.asarray(fixed["splits"][str(k)]["x"][index])
                active.append(fixed["splits"][str(k)]["active_sides"][index])
                us[index] = np.asarray(payload["reference_U"])
                failures.append({"class_index": index, **lp})
            if (index + 1) % 2000 == 0:
                print(
                    f"polish k={k}: {index+1}/{len(sigmas)} "
                    f"in {time.time()-start:.1f}s",
                    flush=True,
                )
        np.savez_compressed(
            output_dir / f"polished_k{k}.npz",
            margins=margins,
            x=xs,
            u=us,
        )
        polished["splits"][str(k)] = {
            "margins": margins.tolist(),
            "active_sides": active,
            "failures": failures,
            "checkpoint": f"polished_k{k}.npz",
            "elapsed_seconds": time.time() - start,
        }
        (output_dir / "polished.json").write_text(
            json.dumps(polished) + "\n", encoding="utf-8"
        )
    return polished


def deep_restarts(
    payload: dict,
    polished: dict,
    output_dir: Path,
    *,
    top_n: int,
    restarts: int,
    steps: int,
    weight_floor: float,
    master_seed: int,
) -> dict:
    sigmas = sigma_matrix(payload["class_bits"])
    ref_signs = np.asarray(payload["reference_genericity"]["triple_det_signs"])
    rng = np.random.default_rng(master_seed)
    # Top N classes by their best margin over the two splits.
    score = np.maximum(
        np.asarray(polished["splits"]["2"]["margins"]),
        np.asarray(polished["splits"]["3"]["margins"]),
    )
    leaders = np.argsort(score)[-top_n:][::-1]
    result = {
        "schema": 1,
        "master_seed": master_seed,
        "leader_class_indices": leaders.astype(int).tolist(),
        "top_n": top_n,
        "restarts_per_split_per_class": restarts,
        "steps": steps,
        "splits": {},
    }
    for k in (2, 3):
        base_checkpoint = np.load(output_dir / f"polished_k{k}.npz")
        base_x = base_checkpoint["x"][leaders]
        repeated_sigmas = np.repeat(sigmas[leaders], restarts, axis=0)
        initial_u = np.empty((top_n * restarts, 5, 3))
        initial_x = np.repeat(base_x, restarts, axis=0)
        canonical_seeds = []
        cursor = 0
        for _leader in leaders:
            for _restart in range(restarts):
                seed = int(rng.integers(0, 2**31 - 1))
                canonical_seeds.append(seed)
                local_rng = np.random.default_rng(seed)
                initial_u[cursor] = canonicalize_random_u(local_rng, ref_signs)
                # T and weights from a different U are only a benign start.
                initial_x[cursor, :3] += local_rng.normal(scale=0.08, size=3)
                cursor += 1
        batch_seed = int(rng.integers(0, 2**31 - 1))
        run = optimize_batch(
            repeated_sigmas,
            initial_u,
            initial_x,
            k,
            ref_signs,
            steps=steps,
            lr=0.018,
            tau_start=0.05,
            tau_end=0.0015,
            weight_floor=weight_floor,
            generic_floor=0.008,
            barrier_strength=50.0,
            seed=batch_seed,
        )
        candidates = []
        for leader_pos, class_index in enumerate(leaders):
            class_candidates = []
            for restart in range(restarts):
                q = leader_pos * restarts + restart
                u = run["best_u"][q]
                lp = lp_margin(u, sigmas[class_index], k, weight_floor)
                class_candidates.append(
                    {
                        "restart": restart,
                        "canonical_seed": canonical_seeds[q],
                        "smooth_true_margin": float(run["best_true"][q]),
                        "lp": lp,
                        "U": u.tolist(),
                    }
                )
            candidates.append(
                {
                    "class_index": int(class_index),
                    "class_bits": int(payload["class_bits"][class_index]),
                    "candidates": class_candidates,
                }
            )
        result["splits"][str(k)] = {
            "optimizer_seed": batch_seed,
            "trace": run["trace"],
            "elapsed_seconds": run["elapsed_seconds"],
            "leaders": candidates,
        }
        (output_dir / "deep_restarts.json").write_text(
            json.dumps(result, indent=2) + "\n", encoding="utf-8"
        )
    return result


def assemble_margins(
    payload: dict,
    fixed: dict,
    polished: dict,
    deep: dict,
    output_dir: Path,
) -> dict:
    deep_lookup: dict[tuple[int, int], list[dict]] = {}
    for k in (2, 3):
        for leader in deep["splits"][str(k)]["leaders"]:
            deep_lookup[(k, leader["class_index"])] = leader["candidates"]
    outer_lookup: dict[tuple[int, int], list[dict]] = {}
    outer_path = output_dir / "outer_lp_restarts.json"
    outer = None
    if outer_path.exists():
        outer = json.loads(outer_path.read_text(encoding="utf-8"))
        for k in (2, 3):
            for leader in outer.get("splits", {}).get(str(k), {}).get(
                "leaders", []
            ):
                outer_lookup[(k, leader["class_index"])] = leader["runs"]

    # Materialize compressed members once. Indexing NpzFile by key inside the
    # class loop would decompress the entire member on every iteration.
    checkpoints = {}
    for k in (2, 3):
        with np.load(output_dir / f"polished_k{k}.npz") as checkpoint_file:
            checkpoints[k] = {
                "u": checkpoint_file["u"],
                "x": checkpoint_file["x"],
            }
    broad_us = []
    broad_path = output_dir / "broad_screen.json"
    if broad_path.exists():
        broad_payload = json.loads(broad_path.read_text(encoding="utf-8"))
        broad_us = [np.asarray(u) for u in broad_payload.get("trial_U", [])]
    reference_u = np.asarray(payload["reference_U"])
    entries = []
    best_record = None
    for index, bits in enumerate(payload["class_bits"]):
        split_records = {}
        for k in (2, 3):
            margin = float(polished["splits"][str(k)]["margins"][index])
            u = checkpoints[k]["u"][index]
            x = checkpoints[k]["x"][index]
            active_sides = polished["splits"][str(k)]["active_sides"][index]
            if np.allclose(u, reference_u, rtol=0.0, atol=1e-13):
                source = "reference_fixed_U"
            elif any(np.allclose(u, bu, rtol=0.0, atol=1e-13) for bu in broad_us):
                source = "broad_all_class_LP_screen"
            else:
                source = "all_class_joint_then_LP_polish"
            deep_candidates = deep_lookup.get((k, index), [])
            deep_successes = [
                c for c in deep_candidates if c["lp"]["success"]
            ]
            if deep_successes:
                leader = max(deep_successes, key=lambda c: c["lp"]["margin"])
                if leader["lp"]["margin"] > margin:
                    margin = float(leader["lp"]["margin"])
                    u = np.asarray(leader["U"])
                    x = np.asarray(leader["lp"]["x"])
                    source = f"deep_restart_{leader['restart']}"
                    active_sides = leader["lp"]["active_sides"]
            outer_candidates = [
                candidate
                for candidate in outer_lookup.get((k, index), [])
                if candidate["success"]
            ]
            if outer_candidates:
                outer_leader = max(
                    outer_candidates, key=lambda c: c["best_margin"]
                )
                if outer_leader["best_margin"] > margin:
                    margin = float(outer_leader["best_margin"])
                    u = np.asarray(outer_leader["best_U"])
                    x = np.asarray(outer_leader["best_lp"]["x"])
                    source = f"outer_lp_restart_{outer_leader['restart']}"
                    active_sides = outer_leader["best_lp"]["active_sides"]
            record = {
                "fixed_U_margin": float(fixed["splits"][str(k)]["margins"][index]),
                "best_margin": margin,
                "source": source,
                "active_sides": active_sides,
                "deep_restarts_run": len(deep_candidates),
                "outer_lp_restarts_run": len(outer_candidates),
            }
            split_records[str(k)] = record
            candidate_best = {
                "class_index": index,
                "class_bits": int(bits),
                "k": k,
                "margin": margin,
                "U": u.tolist(),
                "x": x.tolist(),
                "source": source,
                "active_sides": record["active_sides"],
            }
            if best_record is None or candidate_best["margin"] > best_record["margin"]:
                best_record = candidate_best
        entries.append(
            {
                "class_index": index,
                "class_bits": int(bits),
                "splits": split_records,
                "best_margin": max(
                    split_records["2"]["best_margin"],
                    split_records["3"]["best_margin"],
                ),
            }
        )

    result = {
        "schema": 1,
        "status": (
            "positive_candidate_found"
            if best_record is not None and best_record["margin"] > 1e-6
            else "no_positive_candidate_in_numerical_search"
        ),
        "decision_threshold": 1e-6,
        "numerical_zero_tolerance_used_for_interpretation": 1e-10,
        "normalization": {
            "constraint_rows": "each row divided by its Euclidean norm",
            "homogeneous_parameter_gauge": "sum(alpha)+sum(beta)=1",
            "weight_floor": fixed["weight_floor"],
            "T_bounds_in_fixed_U_LPs": [-50.0, 50.0],
        },
        "completeness": {
            "sigma_enumeration": "exhaustive",
            "fixed_U_optimization": "global LP optimum under the stated numerical gauge/bounds",
            "joint_U_optimization": "nonconvex local optimization; not globally complete",
        },
        "seeds_and_logs": {
            "all_class_joint": "joint_log.json",
            "deep_restarts": "deep_restarts.json",
            "deep_restarts_pre_broad": (
                "deep_restarts_pre_broad.json"
                if (output_dir / "deep_restarts_pre_broad.json").exists()
                else None
            ),
            "outer_lp_restarts": (
                "outer_lp_restarts.json" if outer is not None else None
            ),
            "outer_lp_restarts_pre_broad": (
                "outer_lp_restarts_pre_broad.json"
                if (output_dir / "outer_lp_restarts_pre_broad.json").exists()
                else None
            ),
            "broad_all_class_LP_screens": (
                "broad_screen.json"
                if (output_dir / "broad_screen.json").exists()
                else None
            ),
            "weight_floor_sensitivity": (
                "floor_sensitivity.json"
                if (output_dir / "floor_sensitivity.json").exists()
                else None
            ),
        },
        "best": best_record,
        "classes": entries,
    }
    if best_record is not None:
        result["best"]["genericity"] = genericity(
            np.asarray(best_record["U"])
        )
        best_sigma = sigma_matrix([best_record["class_bits"]])[0]
        result["best"]["best_U_LP_with_dual"] = lp_margin(
            np.asarray(best_record["U"]),
            best_sigma,
            int(best_record["k"]),
            float(fixed["weight_floor"]),
            include_dual=True,
        )
    (output_dir / "margins.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sigma-enum",
        type=Path,
        default=Path(__file__).with_name("sigma_enum.json"),
    )
    parser.add_argument(
        "--output-dir", type=Path, default=Path(__file__).resolve().parent
    )
    parser.add_argument(
        "--phase",
        choices=("fixed", "joint", "polish", "deep", "assemble", "all"),
        default="all",
    )
    parser.add_argument("--weight-floor", type=float, default=1e-5)
    parser.add_argument("--batch-size", type=int, default=512)
    parser.add_argument("--joint-steps", type=int, default=320)
    parser.add_argument("--top-n", type=int, default=20)
    parser.add_argument("--deep-restarts", type=int, default=12)
    parser.add_argument("--deep-steps", type=int, default=1400)
    parser.add_argument("--seed", type=int, default=19440566)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    payload = json.loads(args.sigma_enum.read_text(encoding="utf-8"))

    fixed_path = args.output_dir / "fixed_screen.json"
    polished_path = args.output_dir / "polished.json"
    deep_path = args.output_dir / "deep_restarts.json"

    if args.phase in ("fixed", "all"):
        fixed = run_fixed_screen(payload, args.output_dir, args.weight_floor)
    else:
        fixed = json.loads(fixed_path.read_text(encoding="utf-8"))
    if args.phase == "fixed":
        return

    if args.phase in ("joint", "all"):
        run_all_class_joint(
            payload,
            fixed,
            args.output_dir,
            batch_size=args.batch_size,
            steps=args.joint_steps,
            weight_floor=args.weight_floor,
            master_seed=args.seed,
        )
    if args.phase == "joint":
        return

    if args.phase in ("polish", "all"):
        polished = polish_joint_checkpoints(
            payload, fixed, args.output_dir, args.weight_floor
        )
    else:
        polished = json.loads(polished_path.read_text(encoding="utf-8"))
    if args.phase == "polish":
        return

    if args.phase in ("deep", "all"):
        deep = deep_restarts(
            payload,
            polished,
            args.output_dir,
            top_n=args.top_n,
            restarts=args.deep_restarts,
            steps=args.deep_steps,
            weight_floor=args.weight_floor,
            master_seed=args.seed + 1,
        )
    else:
        deep = json.loads(deep_path.read_text(encoding="utf-8"))
    if args.phase == "deep":
        return

    result = assemble_margins(payload, fixed, polished, deep, args.output_dir)
    print(
        f"assembled margins.json; best margin {result['best']['margin']:.10g} "
        f"(class {result['best']['class_index']}, k={result['best']['k']})"
    )


if __name__ == "__main__":
    main()
