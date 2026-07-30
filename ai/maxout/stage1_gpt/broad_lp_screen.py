"""Add broad canonical random-U LP starts for every sigma class.

This is a second per-class restart mechanism independent of the local
autodiff path.  It updates polished.json/polished_k*.npz only when a true
fixed-U LP margin improves, and logs every shared random direction set.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from margin_search import (  # noqa: E402
    canonicalize_random_u,
    lp_margin,
    sigma_matrix,
)


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
    parser.add_argument("--trials", type=int, default=2)
    parser.add_argument("--weight-floor", type=float, default=1e-5)
    parser.add_argument("--seed", type=int, default=19440569)
    args = parser.parse_args()
    payload = json.loads(args.sigma_enum.read_text(encoding="utf-8"))
    polished = json.loads(args.polished.read_text(encoding="utf-8"))
    sigmas = sigma_matrix(payload["class_bits"])
    reference_signs = np.asarray(
        payload["reference_genericity"]["triple_det_signs"]
    )
    rng = np.random.default_rng(args.seed)
    trial_us = []
    trial_seeds = []
    for _ in range(args.trials):
        seed = int(rng.integers(0, 2**31 - 1))
        trial_seeds.append(seed)
        trial_us.append(
            canonicalize_random_u(
                np.random.default_rng(seed), reference_signs
            )
        )

    log = {
        "schema": 1,
        "seed": args.seed,
        "trials": args.trials,
        "trial_seeds": trial_seeds,
        "trial_U": [u.tolist() for u in trial_us],
        "weight_floor": args.weight_floor,
        "splits": {},
    }
    for k in (2, 3):
        checkpoint = np.load(args.output_dir / f"polished_k{k}.npz")
        margins = checkpoint["margins"].copy()
        xs = checkpoint["x"].copy()
        us = checkpoint["u"].copy()
        active = list(polished["splits"][str(k)]["active_sides"])
        split_trials = []
        split_start = time.time()
        for trial, u in enumerate(trial_us):
            trial_start = time.time()
            improvements = 0
            trial_best = -np.inf
            trial_best_index = None
            failures = []
            for index, sigma in enumerate(sigmas):
                lp = lp_margin(u, sigma, k, args.weight_floor)
                if not lp["success"]:
                    failures.append({"class_index": index, **lp})
                    continue
                value = float(lp["margin"])
                if value > trial_best:
                    trial_best = value
                    trial_best_index = index
                if value > margins[index]:
                    margins[index] = value
                    xs[index] = np.asarray(lp["x"])
                    us[index] = u
                    active[index] = lp["active_sides"]
                    improvements += 1
                if (index + 1) % 4000 == 0:
                    print(
                        f"broad k={k} trial={trial+1}/{args.trials}: "
                        f"{index+1}/{len(sigmas)}",
                        flush=True,
                    )
            split_trials.append(
                {
                    "trial": trial,
                    "seed": trial_seeds[trial],
                    "best_margin_on_this_U": trial_best,
                    "best_class_index_on_this_U": trial_best_index,
                    "improvements_over_running_table": improvements,
                    "failures": failures,
                    "elapsed_seconds": time.time() - trial_start,
                }
            )
        np.savez_compressed(
            args.output_dir / f"polished_k{k}.npz",
            margins=margins,
            x=xs,
            u=us,
        )
        polished["splits"][str(k)]["margins"] = margins.tolist()
        polished["splits"][str(k)]["active_sides"] = active
        polished["splits"][str(k)]["broad_screen_trials_added"] = args.trials
        log["splits"][str(k)] = {
            "trials": split_trials,
            "best_margin_after_merge": float(np.max(margins)),
            "best_class_index_after_merge": int(np.argmax(margins)),
            "elapsed_seconds": time.time() - split_start,
        }
        args.polished.write_text(json.dumps(polished) + "\n", encoding="utf-8")
        (args.output_dir / "broad_screen.json").write_text(
            json.dumps(log, indent=2) + "\n", encoding="utf-8"
        )
    print("updated polished checkpoints and wrote broad_screen.json")


if __name__ == "__main__":
    main()
