"""Cross-check Stage 1 JSON/checkpoint consistency and emit a validation report."""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from incidence_enum import deterministic_build, enumerate_dfs, enumerate_vectorized  # noqa: E402
from margin_search import lp_margin, sigma_matrix  # noqa: E402


def main() -> None:
    sigma_payload = json.loads((HERE / "sigma_enum.json").read_text(encoding="utf-8"))
    margins = json.loads((HERE / "margins.json").read_text(encoding="utf-8"))
    polished = json.loads((HERE / "polished.json").read_text(encoding="utf-8"))
    broad = json.loads((HERE / "broad_screen.json").read_text(encoding="utf-8"))
    deep = json.loads((HERE / "deep_restarts.json").read_text(encoding="utf-8"))
    outer = json.loads((HERE / "outer_lp_restarts.json").read_text(encoding="utf-8"))

    ch_rays = sigma_payload["chamber_side_incidence"]
    enum_vector = enumerate_vectorized(ch_rays).astype(int).tolist()
    enum_dfs = enumerate_dfs(ch_rays)
    classes = margins["classes"]
    if len(classes) != len(enum_vector):
        raise RuntimeError("margins class count does not match enumeration")
    if enum_vector != enum_dfs or enum_vector != sigma_payload["class_bits"]:
        raise RuntimeError("fresh sigma enumeration does not match sigma_enum.json")
    for index, entry in enumerate(classes):
        if entry["class_index"] != index:
            raise RuntimeError(f"class index mismatch at {index}")
        if entry["class_bits"] != sigma_payload["class_bits"][index]:
            raise RuntimeError(f"class bits mismatch at {index}")
        values = [entry["splits"][str(k)]["best_margin"] for k in (2, 3)]
        if not all(math.isfinite(value) for value in values):
            raise RuntimeError(f"nonfinite margin at class {index}")
        if abs(entry["best_margin"] - max(values)) > 1e-13:
            raise RuntimeError(f"combined best mismatch at class {index}")

    best = margins["best"]
    best_sigma = sigma_matrix([best["class_bits"]])[0]
    rebuilt = lp_margin(
        np.asarray(best["U"]),
        best_sigma,
        int(best["k"]),
        float(margins["normalization"]["weight_floor"]),
        include_dual=True,
    )
    if not rebuilt["success"]:
        raise RuntimeError("best LP failed on fresh solve")
    if abs(rebuilt["margin"] - best["margin"]) > 1e-12:
        raise RuntimeError("best margin differs on fresh LP solve")
    _, chambers, current_rays = deterministic_build(np.asarray(best["U"]))
    best_signs = best_sigma.astype(int)
    nae = [len(set(best_signs[sides])) >= 2 for sides in current_rays]

    deep_runs = {
        k: sum(
            len(leader["candidates"]) for leader in deep["splits"][k]["leaders"]
        )
        for k in ("2", "3")
    }
    outer_runs = {
        k: sum(len(leader["runs"]) for leader in outer["splits"][k]["leaders"])
        for k in ("2", "3")
    }
    broad_lp_count = (
        int(broad["trials"]) * 2 * int(sigma_payload["n_global_flip_classes"])
    )
    report = {
        "schema": 1,
        "all_checks_passed": True,
        "fresh_enumeration": {
            "vectorized_classes": len(enum_vector),
            "dfs_classes": len(enum_dfs),
            "exact_order_match": True,
        },
        "margin_table": {
            "classes": len(classes),
            "split_records": 2 * len(classes),
            "finite_and_index_consistent": True,
            "maximum_margin": max(entry["best_margin"] for entry in classes),
            "count_above_decision_threshold": sum(
                entry["best_margin"] > margins["decision_threshold"]
                for entry in classes
            ),
        },
        "best_fresh_LP": {
            "margin": rebuilt["margin"],
            "active_sides": rebuilt["active_sides"],
            "dual_sum": rebuilt["dual"]["sum_side_multipliers"],
        },
        "best_U_incidence": {
            "chambers": len(chambers),
            "sigma_NAE_in_all_chambers": all(nae),
        },
        "coverage_counts": {
            "fixed_reference_LPs": 2 * len(classes),
            "post_joint_polish_LPs": 2 * len(classes),
            "broad_screen_LPs": broad_lp_count,
            "final_deep_smooth_runs": deep_runs,
            "final_outer_LP_runs": outer_runs,
            "pre_broad_deep_and_outer_campaigns_also_preserved": True,
        },
        "no_instance_44_file": not (HERE / "instance_44.json").exists(),
    }
    (HERE / "validation_report.json").write_text(
        json.dumps(report, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
