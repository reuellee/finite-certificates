"""Summarize near-optimal side/chamber blockers from margins.json."""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

import numpy as np


def side_description(side: int, pairs: list[list[int]]) -> dict:
    return {
        "side": side,
        "class": side // 2,
        "pair": pairs[side // 2],
        "orientation": "+cross" if side % 2 == 0 else "-cross",
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
        "--out",
        type=Path,
        default=Path(__file__).with_name("obstruction_analysis.json"),
    )
    parser.add_argument("--leader-count", type=int, default=100)
    args = parser.parse_args()
    margins = json.loads(args.margins.read_text(encoding="utf-8"))
    sigma = json.loads(args.sigma_enum.read_text(encoding="utf-8"))
    classes = margins["classes"]
    best_values = np.asarray([entry["best_margin"] for entry in classes])
    leaders = np.argsort(best_values)[-args.leader_count :][::-1]
    ch_rays = sigma["chamber_side_incidence"]
    pairs = sigma["pairs_in_class_order"]

    per_split = {}
    for k in ("2", "3"):
        values = np.asarray([entry["splits"][k]["best_margin"] for entry in classes])
        split_leaders = np.argsort(values)[-args.leader_count :][::-1]
        side_counter: Counter[int] = Counter()
        chamber_counter: Counter[int] = Counter()
        active_sets = []
        for index in split_leaders:
            active = set(classes[index]["splits"][k]["active_sides"])
            active_sets.append(active)
            side_counter.update(active)
            for chamber, sides in enumerate(ch_rays):
                if active.intersection(sides):
                    chamber_counter[chamber] += 1
        always_sides = sorted(set.intersection(*active_sets)) if active_sets else []
        always_chambers = [
            chamber
            for chamber, count in chamber_counter.items()
            if count == len(split_leaders)
        ]
        per_split[k] = {
            "best_margin": float(np.max(values)),
            "leader_class_indices": split_leaders.astype(int).tolist(),
            "leader_margins": values[split_leaders].tolist(),
            "side_active_frequency": [
                {
                    **side_description(side, pairs),
                    "count": side_counter[side],
                    "fraction": side_counter[side] / len(split_leaders),
                }
                for side in range(20)
            ],
            "chamber_incident_to_active_side_frequency": [
                {
                    "chamber_index": chamber,
                    "chamber_sign_vector": sigma["chambers"][chamber],
                    "sides": ch_rays[chamber],
                    "count": chamber_counter[chamber],
                    "fraction": chamber_counter[chamber] / len(split_leaders),
                }
                for chamber in range(22)
            ],
            "sides_active_in_every_leader": [
                side_description(side, pairs) for side in always_sides
            ],
            "chambers_incident_to_an_active_side_in_every_leader": always_chambers,
        }

    best = margins["best"]
    dual_lp = best["best_U_LP_with_dual"]
    dual = dual_lp.get("dual", {})
    dual_multipliers = np.asarray(dual.get("side_multipliers", np.zeros(20)))
    significant_dual = np.flatnonzero(dual_multipliers > 1e-8)
    best_active = set(best["active_sides"])
    best_active_classes = sorted({side // 2 for side in best_active})
    best_active_pairs = [pairs[ci] for ci in best_active_classes]
    best_pair_degrees = Counter(
        endpoint for pair in best_active_pairs for endpoint in pair
    )
    best_chambers = []
    for chamber, sides in enumerate(ch_rays):
        intersection = sorted(best_active.intersection(sides))
        if intersection:
            best_chambers.append(
                {
                    "chamber_index": chamber,
                    "chamber_sign_vector": sigma["chambers"][chamber],
                    "active_incident_sides": intersection,
                }
            )

    thresholds = [0.0, -1e-8, -1e-6, -1e-4, -1e-3, -1e-2]
    deep_campaign_summaries = {}
    for deep_name in (
        "deep_restarts.json",
        "deep_restarts_pre_broad.json",
    ):
        deep_path = args.margins.with_name(deep_name)
        if not deep_path.exists():
            continue
        deep_payload = json.loads(deep_path.read_text(encoding="utf-8"))
        campaign = {}
        for k in ("2", "3"):
            all_patterns = []
            near_zero_patterns = []
            for leader in deep_payload["splits"][k]["leaders"]:
                for candidate in leader["candidates"]:
                    pattern = tuple(candidate["lp"]["active_sides"])
                    all_patterns.append(pattern)
                    if candidate["lp"]["margin"] > -1e-8:
                        near_zero_patterns.append(pattern)
            counts = Counter(near_zero_patterns)
            campaign[k] = {
                "runs": len(all_patterns),
                "near_zero_runs_margin_gt_minus_1e_8": len(near_zero_patterns),
                "near_zero_active_patterns": [
                    {
                        "active_sides": list(pattern),
                        "active_pairs": sorted(
                            {tuple(pairs[side // 2]) for side in pattern}
                        ),
                        "count": count,
                        "fraction_of_near_zero": (
                            count / len(near_zero_patterns)
                            if near_zero_patterns
                            else None
                        ),
                    }
                    for pattern, count in counts.most_common()
                ],
            }
        deep_campaign_summaries[deep_name] = campaign
    payload = {
        "schema": 1,
        "leader_count": args.leader_count,
        "best_margin": float(np.max(best_values)),
        "counts_above_threshold": {
            str(threshold): int(np.sum(best_values > threshold))
            for threshold in thresholds
        },
        "best_overall": {
            key: best[key]
            for key in (
                "class_index",
                "class_bits",
                "k",
                "margin",
                "source",
                "active_sides",
                "genericity",
            )
        },
        "best_active_side_descriptions": [
            side_description(side, pairs) for side in sorted(best_active)
        ],
        "best_active_pair_graph": {
            "pairs": best_active_pairs,
            "generator_degrees": {
                str(generator): best_pair_degrees[generator]
                for generator in range(5)
            },
            "is_five_cycle": (
                len(best_active_pairs) == 5
                and all(best_pair_degrees[generator] == 2 for generator in range(5))
            ),
            "both_antipodal_sides_active_for_every_pair": all(
                2 * ci in best_active and 2 * ci + 1 in best_active
                for ci in best_active_classes
            ),
        },
        "best_chambers_incident_to_active_sides": best_chambers,
        "best_LP_dual": {
            "sum_side_multipliers": dual.get("sum_side_multipliers"),
            "significant_sides": [
                {
                    **side_description(int(side), pairs),
                    "multiplier": float(dual_multipliers[side]),
                    "constraint_residual": float(
                        dual["inequality_residuals"][side]
                    ),
                }
                for side in significant_dual
            ],
            "weight_lower_bounds_active": [
                weight
                for weight, value in enumerate(best["x"][3:8])
                if value <= margins["normalization"]["weight_floor"] + 1e-8
            ],
        },
        "top_overall_classes": [
            {
                "class_index": int(index),
                "class_bits": int(classes[index]["class_bits"]),
                "best_margin": float(classes[index]["best_margin"]),
                "k2_margin": float(classes[index]["splits"]["2"]["best_margin"]),
                "k3_margin": float(classes[index]["splits"]["3"]["best_margin"]),
            }
            for index in leaders
        ],
        "per_split": per_split,
        "deep_campaign_active_pattern_summary": deep_campaign_summaries,
        "interpretation_note": (
            "A chamber is counted here when at least one of its incident side "
            "constraints is active. This is a localization diagnostic, not an "
            "independent chamber dual certificate."
        ),
    }
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
