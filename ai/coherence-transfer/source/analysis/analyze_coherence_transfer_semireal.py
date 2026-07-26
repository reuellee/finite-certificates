#!/usr/bin/env python3
"""Frozen-style analysis for the semi-real coherence-transfer experiment.

The seed, architecture, beta, width, dataset-hash, manipulation, and retention
gates are explicit here so that an unexpected file or a signal-destroying
solution cannot be silently interpreted as support.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd


EXPECTED_ARCHITECTURES = ("l1", "topk")
EXPECTED_WIDTHS = (68,)
EXPECTED_BETAS = (0.0, 0.025, 0.0625, 0.25, 0.5)
EXPECTED_SEEDS = tuple(range(12))
EXPECTED_DATA_SHA256 = (
    "d00e7d6c272ae538920cc91b7ab92e8ba91f522eb1c62b05677fbdc56799bad9"
)
CONTROL_BETA = 0.0
HIGH_BETA = 0.5
BOOTSTRAP_REPS = 20_000
BOOTSTRAP_SEED = 8675309


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def paired_contrast(
    frame: pd.DataFrame,
    architecture: str,
    field: str,
    high_beta: float = HIGH_BETA,
    control_beta: float = CONTROL_BETA,
) -> dict[str, Any]:
    subset = frame[
        (frame["architecture"] == architecture)
        & (frame["beta"].isin([control_beta, high_beta]))
    ]
    pivot = subset.pivot(index="seed", columns="beta", values=field)
    difference = (
        pivot[high_beta].to_numpy() - pivot[control_beta].to_numpy()
    )
    rng = np.random.default_rng(
        BOOTSTRAP_SEED
        + sum(ord(char) for char in architecture + field)
    )
    indices = rng.integers(
        0,
        difference.size,
        size=(BOOTSTRAP_REPS, difference.size),
    )
    bootstrap_means = difference[indices].mean(axis=1)
    lower, upper = np.quantile(bootstrap_means, [0.025, 0.975])
    return {
        "architecture": architecture,
        "field": field,
        "high_beta": high_beta,
        "control_beta": control_beta,
        "n_seeds": int(difference.size),
        "mean_difference": float(difference.mean()),
        "ci95_lower": float(lower),
        "ci95_upper": float(upper),
        "negative_seeds": int(np.sum(difference < 0.0)),
        "positive_seeds": int(np.sum(difference > 0.0)),
        "zero_seeds": int(np.sum(difference == 0.0)),
        "per_seed_difference": {
            str(int(seed)): float(value)
            for seed, value in zip(pivot.index, difference)
        },
    }


def bootstrap_mean_ci(values: np.ndarray, salt: int) -> tuple[float, float]:
    rng = np.random.default_rng(BOOTSTRAP_SEED + salt)
    indices = rng.integers(
        0, values.size, size=(BOOTSTRAP_REPS, values.size)
    )
    means = values[indices].mean(axis=1)
    lower, upper = np.quantile(means, [0.025, 0.975])
    return float(lower), float(upper)


def conformance_checks(
    frame: pd.DataFrame,
    metadata: dict[str, Any],
) -> dict[str, bool]:
    expected_rows = (
        len(EXPECTED_ARCHITECTURES)
        * len(EXPECTED_WIDTHS)
        * len(EXPECTED_BETAS)
        * len(EXPECTED_SEEDS)
    )
    cell_counts = frame.groupby(
        ["architecture", "m", "beta"], dropna=False
    )["seed"].nunique()
    duplicate_count = int(
        frame.duplicated(["architecture", "m", "beta", "seed"]).sum()
    )
    return {
        "row_count": len(frame) == expected_rows,
        "architectures": set(frame["architecture"])
        == set(EXPECTED_ARCHITECTURES),
        "widths": set(frame["m"].astype(int)) == set(EXPECTED_WIDTHS),
        "betas": set(np.round(frame["beta"], 10))
        == set(EXPECTED_BETAS),
        "seeds": set(frame["seed"].astype(int)) == set(EXPECTED_SEEDS),
        "all_cells_have_12_seeds": bool(
            len(cell_counts)
            == len(EXPECTED_ARCHITECTURES)
            * len(EXPECTED_WIDTHS)
            * len(EXPECTED_BETAS)
            and (cell_counts == len(EXPECTED_SEEDS)).all()
        ),
        "no_duplicates": duplicate_count == 0,
        "data_hash": metadata["dataset"]["data_sha256"]
        == EXPECTED_DATA_SHA256,
        "classifier_quality": (
            metadata["dataset"]["classifier_eval_accuracy"] >= 0.94
        ),
        "registered_steps": (
            metadata["config"]["steps"] == 10_000
            and metadata["steps_override"] is None
        ),
        "registered_topk": metadata["config"]["topk_k"] == 16,
        "registered_lambda": abs(
            metadata["config"]["l1_lambda"] - 0.2
        )
        < 1e-12,
    }


def condition_table(frame: pd.DataFrame) -> pd.DataFrame:
    fields = [
        "fvu",
        "l0",
        "dead_fraction",
        "gram_penalty",
        "mean_squared_coherence",
        "max_absolute_coherence",
        "mean_factor_max_positive_cosine",
        "mean_factor_causal_concentration",
        "mean_factor_causal_participation_ratio",
        "mean_factor_causal_split_count",
        "mean_factor_single_gain",
        "mean_factor_family_gain",
        "mean_factor_family_cosine",
        "mean_factor_nnls_residual",
    ]
    return (
        frame.groupby(["architecture", "m", "beta"])[fields]
        .mean()
        .reset_index()
    )


def _markdown_table(frame: pd.DataFrame, columns: list[str]) -> str:
    header = "| " + " | ".join(columns) + " |"
    separator = "|" + "|".join(["---"] * len(columns)) + "|"
    rows = [header, separator]
    for _, row in frame[columns].iterrows():
        values = []
        for column in columns:
            value = row[column]
            if isinstance(value, (float, np.floating)):
                values.append(f"{value:.4f}")
            else:
                values.append(str(value))
        rows.append("| " + " | ".join(values) + " |")
    return "\n".join(rows)


def save_weight_manifest(result_dir: Path) -> list[dict[str, Any]]:
    records = []
    for path in sorted(result_dir.glob("weights_*.npz")):
        records.append(
            {
                "filename": path.name,
                "bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            }
        )
    output_path = result_dir / "weights_sha256.csv"
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(
            handle, fieldnames=["filename", "bytes", "sha256"]
        )
        writer.writeheader()
        writer.writerows(records)
    return records


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("result_dir", type=Path)
    args = parser.parse_args()

    metrics_path = args.result_dir / "run_metrics.csv"
    metadata_path = args.result_dir / "metadata.json"
    frame = pd.read_csv(metrics_path)
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    conformance = conformance_checks(frame, metadata)
    conformance_pass = all(conformance.values())
    table = condition_table(frame)

    manipulation: dict[str, Any] = {}
    retention: dict[str, Any] = {}
    for architecture in EXPECTED_ARCHITECTURES:
        control = table[
            (table["architecture"] == architecture)
            & (table["beta"] == CONTROL_BETA)
        ].iloc[0]
        high = table[
            (table["architecture"] == architecture)
            & (table["beta"] == HIGH_BETA)
        ].iloc[0]
        gram_ratio = float(high["gram_penalty"] / control["gram_penalty"])
        manipulation[architecture] = {
            "control_gram": float(control["gram_penalty"]),
            "high_gram": float(high["gram_penalty"]),
            "high_over_control_ratio": gram_ratio,
            "pass": gram_ratio <= 0.80,
        }
        high_seed_rows = frame[
            (frame["architecture"] == architecture)
            & (frame["beta"] == HIGH_BETA)
        ]
        gain_values = high_seed_rows[
            "mean_factor_family_gain"
        ].to_numpy()
        gain_lower, gain_upper = bootstrap_mean_ci(
            gain_values, 1000 + sum(ord(c) for c in architecture)
        )
        retention[architecture] = {
            "mean_family_gain": float(gain_values.mean()),
            "family_gain_ci95_lower": gain_lower,
            "family_gain_ci95_upper": gain_upper,
            "mean_family_cosine": float(
                high_seed_rows["mean_factor_family_cosine"].mean()
            ),
            "mean_fvu": float(high_seed_rows["fvu"].mean()),
            "pass": bool(
                gain_values.mean() >= 0.75
                and high_seed_rows["mean_factor_family_cosine"].mean()
                >= 0.95
                and high_seed_rows["fvu"].mean() <= 0.10
            ),
        }

    topk_rows = frame[frame["architecture"] == "topk"]
    fixed_sparsity_pass = bool(
        np.max(np.abs(topk_rows["l0"].to_numpy() - 16.0)) <= 0.05
    )
    gate_pass = bool(
        conformance_pass
        and all(item["pass"] for item in manipulation.values())
        and all(item["pass"] for item in retention.values())
        and fixed_sparsity_pass
    )

    contrast_fields = [
        "mean_factor_max_positive_cosine",
        "mean_factor_causal_concentration",
        "mean_factor_causal_participation_ratio",
        "mean_factor_causal_split_count",
        "mean_factor_single_gain",
        "mean_factor_family_gain",
        "fvu",
        "l0",
        "dead_fraction",
        "gram_penalty",
        "max_absolute_coherence",
    ]
    contrasts = [
        paired_contrast(frame, architecture, field)
        for architecture in EXPECTED_ARCHITECTURES
        for field in contrast_fields
    ]
    contrast_lookup = {
        (item["architecture"], item["field"]): item for item in contrasts
    }

    alignment_pass = {
        architecture: (
            contrast_lookup[
                (architecture, "mean_factor_max_positive_cosine")
            ]["ci95_upper"]
            < 0.0
        )
        for architecture in EXPECTED_ARCHITECTURES
    }
    splitting_pass = {
        architecture: (
            contrast_lookup[
                (architecture, "mean_factor_causal_split_count")
            ]["ci95_lower"]
            > 0.0
            and contrast_lookup[
                (architecture, "mean_factor_causal_participation_ratio")
            ]["ci95_lower"]
            > 0.0
        )
        for architecture in EXPECTED_ARCHITECTURES
    }
    concentration_pass = {
        architecture: (
            contrast_lookup[
                (architecture, "mean_factor_causal_concentration")
            ]["ci95_upper"]
            < 0.0
        )
        for architecture in EXPECTED_ARCHITECTURES
    }

    if not gate_pass:
        primary_verdict = "UNINTERPRETABLE: one or more registered gates failed"
    elif all(alignment_pass.values()):
        primary_verdict = (
            "SUPPORTED: strong full-Gram regularization reduced one-atom "
            "causal-direction alignment while the causal direction remained "
            "recoverable at the decoder-family level in both architectures"
        )
    else:
        primary_verdict = (
            "NOT SUPPORTED: the paired alignment criterion did not pass in "
            "both architectures"
        )

    splitting_verdict = (
        "SUPPORTED IN BOTH ARCHITECTURES"
        if all(splitting_pass.values())
        else (
            "SUPPORTED IN "
            + ", ".join(
                key for key, value in splitting_pass.items() if value
            )
            if any(splitting_pass.values())
            else "NOT SUPPORTED"
        )
    )
    concentration_verdict = (
        "SUPPORTED IN BOTH ARCHITECTURES"
        if all(concentration_pass.values())
        else (
            "SUPPORTED IN "
            + ", ".join(
                key for key, value in concentration_pass.items() if value
            )
            if any(concentration_pass.values())
            else "NOT SUPPORTED"
        )
    )

    weight_records = save_weight_manifest(args.result_dir)
    summary = {
        "primary_verdict": primary_verdict,
        "splitting_verdict": splitting_verdict,
        "concentration_verdict": concentration_verdict,
        "gates": {
            "conformance": conformance,
            "conformance_pass": conformance_pass,
            "manipulation": manipulation,
            "retention": retention,
            "topk_fixed_l0": fixed_sparsity_pass,
            "all_gates_pass": gate_pass,
        },
        "alignment_pass": alignment_pass,
        "splitting_pass": splitting_pass,
        "concentration_pass": concentration_pass,
        "contrasts": contrasts,
        "metrics_sha256": sha256_file(metrics_path),
        "metadata_sha256": sha256_file(metadata_path),
        "weight_file_count": len(weight_records),
    }
    (args.result_dir / "analysis_summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    table.to_csv(args.result_dir / "condition_means.csv", index=False)
    pd.DataFrame(
        [
            {
                key: value
                for key, value in contrast.items()
                if key != "per_seed_difference"
            }
            for contrast in contrasts
        ]
    ).to_csv(args.result_dir / "paired_contrasts.csv", index=False)

    focus_columns = [
        "architecture",
        "beta",
        "fvu",
        "l0",
        "dead_fraction",
        "gram_penalty",
        "max_absolute_coherence",
        "mean_factor_max_positive_cosine",
        "mean_factor_causal_concentration",
        "mean_factor_causal_split_count",
        "mean_factor_family_gain",
    ]
    focus_table = table.copy()
    focus_table["beta"] = focus_table["beta"].map(lambda value: f"{value:g}")
    report_lines = [
        "# Semi-real coherence-transfer experiment: registered analysis",
        "",
        f"**Primary verdict:** {primary_verdict}",
        "",
        f"**Activation-aware splitting:** {splitting_verdict}.",
        "",
        f"**Causal-contribution concentration loss:** "
        f"{concentration_verdict}.",
        "",
        "## Gates",
        "",
        f"- Conformance: {'PASS' if conformance_pass else 'FAIL'}",
        f"- Coherence manipulation: "
        f"{'PASS' if all(x['pass'] for x in manipulation.values()) else 'FAIL'}",
        f"- Family-retention gate: "
        f"{'PASS' if all(x['pass'] for x in retention.values()) else 'FAIL'}",
        f"- TopK fixed-L0 gate: {'PASS' if fixed_sparsity_pass else 'FAIL'}",
        "",
        "## Condition means",
        "",
        _markdown_table(focus_table, focus_columns),
        "",
        "## Registered high-minus-control contrasts",
        "",
    ]
    for architecture in EXPECTED_ARCHITECTURES:
        report_lines.append(f"### {architecture.upper()}")
        report_lines.append("")
        for field in [
            "mean_factor_max_positive_cosine",
            "mean_factor_causal_concentration",
            "mean_factor_causal_participation_ratio",
            "mean_factor_causal_split_count",
            "mean_factor_family_gain",
            "fvu",
            "l0",
            "dead_fraction",
            "gram_penalty",
            "max_absolute_coherence",
        ]:
            item = contrast_lookup[(architecture, field)]
            report_lines.append(
                f"- `{field}`: {item['mean_difference']:+.4f}, "
                f"95% paired-seed bootstrap CI "
                f"[{item['ci95_lower']:+.4f}, "
                f"{item['ci95_upper']:+.4f}], "
                f"{item['negative_seeds']}/{item['n_seeds']} negative."
            )
        report_lines.append("")
    report_lines.extend(
        [
            "## Scope",
            "",
            "This is a trained, held-out, matched-seed SAE experiment on a "
            "learned neural representation of real images with two appended "
            "and orthogonally mixed controlled factors. It is not an LLM "
            "activation experiment, and the appended factors are synthetic. "
            "The causal claim is limited to recovery of those known activation "
            "generators. The full squared-Gram penalty tested here also differs "
            "from OrtSAE's randomized positive-neighbor penalty.",
            "",
        ]
    )
    (args.result_dir / "REGISTERED_ANALYSIS.md").write_text(
        "\n".join(report_lines), encoding="utf-8"
    )

    print(primary_verdict)
    print(f"splitting: {splitting_verdict}")
    print(f"concentration: {concentration_verdict}")
    print(f"all gates pass: {gate_pass}")
    for architecture in EXPECTED_ARCHITECTURES:
        item = contrast_lookup[
            (architecture, "mean_factor_max_positive_cosine")
        ]
        print(
            f"{architecture} alignment high-control "
            f"{item['mean_difference']:+.4f} "
            f"CI [{item['ci95_lower']:+.4f}, "
            f"{item['ci95_upper']:+.4f}]"
        )


if __name__ == "__main__":
    main()
