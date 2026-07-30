"""Re-solve saved candidates at smaller positive-weight floors."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from margin_search import lp_margin, sigma_matrix  # noqa: E402


def main() -> None:
    sigma_payload = json.loads((HERE / "sigma_enum.json").read_text(encoding="utf-8"))
    margins = json.loads((HERE / "margins.json").read_text(encoding="utf-8"))
    sigmas = sigma_matrix(sigma_payload["class_bits"])
    reference_u = np.asarray(sigma_payload["reference_U"])
    floors = (1e-7, 1e-9)
    score = np.asarray([entry["best_margin"] for entry in margins["classes"]])
    leaders = np.argsort(score)[-300:][::-1]

    candidates: list[dict] = []
    # Top 300: both their polished direction and the reference direction.
    checkpoints = {}
    for k in (2, 3):
        with np.load(HERE / f"polished_k{k}.npz") as data:
            checkpoints[k] = data["u"]
        for index in leaders:
            candidates.append(
                {
                    "source": "top300_polished",
                    "class_index": int(index),
                    "k": k,
                    "U": checkpoints[k][index],
                }
            )
            candidates.append(
                {
                    "source": "top300_reference",
                    "class_index": int(index),
                    "k": k,
                    "U": reference_u,
                }
            )
    # Every stored deep candidate, before and after the broad screens.
    for filename in ("deep_restarts.json", "deep_restarts_pre_broad.json"):
        payload = json.loads((HERE / filename).read_text(encoding="utf-8"))
        for k in (2, 3):
            for leader in payload["splits"][str(k)]["leaders"]:
                for candidate in leader["candidates"]:
                    candidates.append(
                        {
                            "source": filename,
                            "class_index": int(leader["class_index"]),
                            "k": k,
                            "U": np.asarray(candidate["U"]),
                        }
                    )
    # Every stored true-inner-LP outer candidate.
    for filename in (
        "outer_lp_restarts.json",
        "outer_lp_restarts_pre_broad.json",
    ):
        payload = json.loads((HERE / filename).read_text(encoding="utf-8"))
        for k in (2, 3):
            for leader in payload["splits"][str(k)]["leaders"]:
                for run in leader["runs"]:
                    if run["success"]:
                        candidates.append(
                            {
                                "source": filename,
                                "class_index": int(leader["class_index"]),
                                "k": k,
                                "U": np.asarray(run["best_U"]),
                            }
                        )

    results = {}
    for floor in floors:
        best = None
        failures = 0
        above_threshold = 0
        for position, candidate in enumerate(candidates):
            index = candidate["class_index"]
            lp = lp_margin(
                candidate["U"], sigmas[index], candidate["k"], floor
            )
            if not lp["success"]:
                failures += 1
                continue
            if lp["margin"] > 1e-6:
                above_threshold += 1
            record = {
                "margin": float(lp["margin"]),
                "source": candidate["source"],
                "candidate_position": position,
                "class_index": index,
                "class_bits": int(sigma_payload["class_bits"][index]),
                "k": int(candidate["k"]),
                "U": np.asarray(candidate["U"]).tolist(),
                "x": lp["x"],
                "active_sides": lp["active_sides"],
            }
            if best is None or record["margin"] > best["margin"]:
                best = record
        results[str(floor)] = {
            "LPs_attempted": len(candidates),
            "failures": failures,
            "count_above_1e_6": above_threshold,
            "best": best,
        }
    payload = {
        "schema": 1,
        "purpose": (
            "sensitivity of the numerical positivity gauge; saved U values "
            "are re-solved but U is not re-optimized at these floors"
        ),
        "top_class_count": 300,
        "saved_candidate_records": len(candidates),
        "floors": results,
    }
    (HERE / "floor_sensitivity.json").write_text(
        json.dumps(payload, indent=2) + "\n", encoding="utf-8"
    )
    print(
        {
            floor: (
                results[str(floor)]["best"]["margin"],
                results[str(floor)]["count_above_1e_6"],
                results[str(floor)]["failures"],
            )
            for floor in floors
        }
    )


if __name__ == "__main__":
    main()
