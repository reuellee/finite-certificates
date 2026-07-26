#!/usr/bin/env python3
"""Matched-seed semi-real test of coherence-induced causal-feature splitting.

This experiment deliberately sits between a toy superposition model and an
LLM-scale SAE:

* the background representation is the hidden layer of a classifier trained on
  the real sklearn handwritten-digits dataset;
* two independent binary interventions are added as exact one-dimensional
  causal factors;
* an orthogonal mixing hides the privileged coordinates;
* a genuinely overcomplete, amortized ReLU-L1 SAE is trained end to end; and
* all four intervention states are retained on held-out images, permitting
  activation-aware causal scoring rather than decoder-cosine scoring alone.

The decoder regularizer is the exact full squared-Gram penalty in the finite
certificate:

    C_sum(D) = sum_{i<j} <d_i, d_j>^2

with unit decoder columns.  It is not OrtSAE's chunked positive-neighbor
penalty, and the script does not claim to be a transformer-activation test.

The implementation uses only NumPy, SciPy, and scikit-learn so that the full
matched-seed study is runnable on CPU in the repository's base environment.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import sys
import time
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import scipy
import sklearn
from scipy.optimize import nnls
from sklearn.datasets import load_digits
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier


@dataclass(frozen=True)
class Config:
    data_seed: int = 20260725
    classifier_seed: int = 271828
    mixing_seed: int = 314159
    hidden_dim: int = 32
    expansion: int = 2
    factor_amplitude: float = 1.5
    l1_lambda: float = 0.2
    topk_k: int = 16
    steps: int = 10000
    batch_size: int = 256
    learning_rate: float = 0.002
    grad_clip: float = 10.0
    eval_threshold: float = 1e-6
    alignment_threshold: float = 0.90
    split_relative_threshold: float = 0.10


@dataclass
class DatasetBundle:
    train_x: np.ndarray
    eval_x: np.ndarray
    eval_states: np.ndarray
    causal_directions: np.ndarray
    effective_factor_amplitude: float
    classifier_train_accuracy: float
    classifier_eval_accuracy: float
    hidden_dim: int
    ambient_dim: int
    train_base_n: int
    eval_base_n: int
    data_sha256: str


def _array_digest(arrays: Iterable[np.ndarray]) -> str:
    digest = hashlib.sha256()
    for array in arrays:
        contiguous = np.ascontiguousarray(array)
        digest.update(str(contiguous.shape).encode("ascii"))
        digest.update(str(contiguous.dtype).encode("ascii"))
        digest.update(contiguous.tobytes())
    return digest.hexdigest()


def _hidden_activations(model: MLPClassifier, x: np.ndarray) -> np.ndarray:
    hidden = x @ model.coefs_[0] + model.intercepts_[0]
    return np.maximum(hidden, 0.0)


def _factorial_expand(
    hidden: np.ndarray,
    q_mix: np.ndarray,
    factor_amplitude: float,
) -> tuple[np.ndarray, np.ndarray]:
    # Row order per base image is fixed: 00, 10, 01, 11.  The evaluator uses
    # this order to form exact paired intervention contrasts.
    states = np.asarray(
        [[0.0, 0.0], [1.0, 0.0], [0.0, 1.0], [1.0, 1.0]],
        dtype=np.float32,
    )
    repeated_hidden = np.repeat(hidden.astype(np.float32), 4, axis=0)
    tiled_states = np.tile(states, (hidden.shape[0], 1))
    augmented = np.concatenate(
        [repeated_hidden, factor_amplitude * tiled_states],
        axis=1,
    )
    return (augmented @ q_mix).astype(np.float32), tiled_states


def build_dataset(cfg: Config) -> DatasetBundle:
    digits_x, digits_y = load_digits(return_X_y=True)
    indices = np.arange(digits_x.shape[0])
    train_idx, eval_idx = train_test_split(
        indices,
        test_size=0.30,
        random_state=cfg.data_seed,
        stratify=digits_y,
    )

    pixel_mean = digits_x[train_idx].mean(axis=0)
    pixel_std = digits_x[train_idx].std(axis=0)
    pixel_std[pixel_std < 1e-8] = 1.0
    x_train_std = (digits_x[train_idx] - pixel_mean) / pixel_std
    x_eval_std = (digits_x[eval_idx] - pixel_mean) / pixel_std

    classifier = MLPClassifier(
        hidden_layer_sizes=(cfg.hidden_dim,),
        activation="relu",
        solver="lbfgs",
        alpha=1e-4,
        max_iter=600,
        random_state=cfg.classifier_seed,
    )
    classifier.fit(x_train_std, digits_y[train_idx])
    train_accuracy = accuracy_score(
        digits_y[train_idx], classifier.predict(x_train_std)
    )
    eval_accuracy = accuracy_score(
        digits_y[eval_idx], classifier.predict(x_eval_std)
    )

    h_train = _hidden_activations(classifier, x_train_std)
    h_eval = _hidden_activations(classifier, x_eval_std)
    hidden_scale = math.sqrt(cfg.hidden_dim) / np.mean(
        np.linalg.norm(h_train, axis=1)
    )
    h_train = (h_train * hidden_scale).astype(np.float32)
    h_eval = (h_eval * hidden_scale).astype(np.float32)

    ambient_dim = cfg.hidden_dim + 2
    mixing_rng = np.random.default_rng(cfg.mixing_seed)
    raw_mix = mixing_rng.standard_normal((ambient_dim, ambient_dim))
    q_mix, r_mix = np.linalg.qr(raw_mix)
    # Fix the QR sign convention, which can otherwise vary across LAPACK builds.
    signs = np.sign(np.diag(r_mix))
    signs[signs == 0] = 1.0
    q_mix = (q_mix * signs).astype(np.float32)

    train_x, _ = _factorial_expand(
        h_train, q_mix, cfg.factor_amplitude
    )
    eval_x, eval_states = _factorial_expand(
        h_eval, q_mix, cfg.factor_amplitude
    )

    # One scalar normalization matches the convention used in the real Pythia
    # trainer: mean input norm is sqrt(d).  It preserves all angles.
    total_scale = math.sqrt(ambient_dim) / np.mean(
        np.linalg.norm(train_x, axis=1)
    )
    train_x = (train_x * total_scale).astype(np.float32)
    eval_x = (eval_x * total_scale).astype(np.float32)
    causal_directions = q_mix[-2:, :].astype(np.float32)
    effective_factor_amplitude = cfg.factor_amplitude * total_scale

    data_hash = _array_digest(
        [train_x, eval_x, eval_states, causal_directions]
    )
    return DatasetBundle(
        train_x=train_x,
        eval_x=eval_x,
        eval_states=eval_states,
        causal_directions=causal_directions,
        effective_factor_amplitude=float(effective_factor_amplitude),
        classifier_train_accuracy=float(train_accuracy),
        classifier_eval_accuracy=float(eval_accuracy),
        hidden_dim=cfg.hidden_dim,
        ambient_dim=ambient_dim,
        train_base_n=len(train_idx),
        eval_base_n=len(eval_idx),
        data_sha256=data_hash,
    )


def _gram_penalty_and_grad(decoder: np.ndarray) -> tuple[float, np.ndarray]:
    gram = decoder.T @ decoder
    offdiag = gram - np.eye(gram.shape[0], dtype=gram.dtype)
    penalty = 0.5 * float(np.sum(offdiag * offdiag))
    gradient = 2.0 * (decoder @ offdiag)
    return penalty, gradient


class Adam:
    def __init__(
        self,
        parameters: dict[str, np.ndarray],
        learning_rate: float,
    ) -> None:
        self.learning_rate = learning_rate
        self.m = {name: np.zeros_like(value) for name, value in parameters.items()}
        self.v = {name: np.zeros_like(value) for name, value in parameters.items()}
        self.t = 0

    def step(
        self,
        parameters: dict[str, np.ndarray],
        gradients: dict[str, np.ndarray],
        learning_rate_scale: float,
    ) -> None:
        self.t += 1
        beta1 = 0.9
        beta2 = 0.999
        epsilon = 1e-8
        lr = self.learning_rate * learning_rate_scale
        for name, parameter in parameters.items():
            gradient = gradients[name]
            self.m[name] = beta1 * self.m[name] + (1.0 - beta1) * gradient
            self.v[name] = beta2 * self.v[name] + (1.0 - beta2) * (
                gradient * gradient
            )
            m_hat = self.m[name] / (1.0 - beta1**self.t)
            v_hat = self.v[name] / (1.0 - beta2**self.t)
            parameter -= lr * m_hat / (np.sqrt(v_hat) + epsilon)


def _apply_topk(
    dense_features: np.ndarray,
    k: int,
) -> tuple[np.ndarray, np.ndarray]:
    if k <= 0 or k > dense_features.shape[1]:
        raise ValueError(f"top-k must be in [1, {dense_features.shape[1]}]")
    top_indices = np.argpartition(
        dense_features, dense_features.shape[1] - k, axis=1
    )[:, -k:]
    mask = np.zeros_like(dense_features, dtype=bool)
    np.put_along_axis(mask, top_indices, True, axis=1)
    mask &= dense_features > 0.0
    return dense_features * mask, mask


def _encode(
    x: np.ndarray,
    encoder: np.ndarray,
    encoder_bias: np.ndarray,
    decoder_bias: np.ndarray,
    architecture: str,
    topk_k: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    preactivation = (x - decoder_bias) @ encoder + encoder_bias
    dense_features = np.maximum(preactivation, 0.0)
    if architecture == "l1":
        active_mask = preactivation > 0.0
        features = dense_features
    elif architecture == "topk":
        features, active_mask = _apply_topk(dense_features, topk_k)
    else:
        raise ValueError(f"unknown architecture: {architecture}")
    return preactivation, features, active_mask


def train_sae(
    train_x: np.ndarray,
    cfg: Config,
    seed: int,
    beta: float,
    architecture: str = "l1",
    latent_width: int | None = None,
    steps_override: int | None = None,
) -> tuple[dict[str, np.ndarray], dict[str, float]]:
    steps = cfg.steps if steps_override is None else steps_override
    d = train_x.shape[1]
    m = cfg.expansion * d if latent_width is None else latent_width
    if m <= d:
        raise ValueError(f"latent width must be overcomplete: got m={m}, d={d}")
    init_rng = np.random.default_rng(seed)
    batch_rng = np.random.default_rng(1_000_000 + seed)

    decoder = init_rng.standard_normal((d, m)).astype(np.float32)
    decoder /= np.linalg.norm(decoder, axis=0, keepdims=True).clip(1e-8)
    encoder = (
        decoder + 0.05 * init_rng.standard_normal((d, m)).astype(np.float32)
    )
    encoder_bias = np.full(m, -0.05, dtype=np.float32)
    decoder_bias = np.zeros(d, dtype=np.float32)

    parameters = {
        "encoder": encoder,
        "encoder_bias": encoder_bias,
        "decoder": decoder,
        "decoder_bias": decoder_bias,
    }
    optimizer = Adam(parameters, cfg.learning_rate)
    final_values: dict[str, float] = {}

    for step in range(steps):
        batch_indices = batch_rng.integers(
            0, train_x.shape[0], size=cfg.batch_size
        )
        batch = train_x[batch_indices]
        centered = batch - decoder_bias
        preactivation = centered @ encoder + encoder_bias
        dense_features = np.maximum(preactivation, 0.0)
        if architecture == "l1":
            features = dense_features
            active_mask = preactivation > 0.0
        elif architecture == "topk":
            features, active_mask = _apply_topk(
                dense_features, cfg.topk_k
            )
        else:
            raise ValueError(f"unknown architecture: {architecture}")
        reconstruction = features @ decoder.T + decoder_bias
        residual = reconstruction - batch

        batch_n = batch.shape[0]
        reconstruction_loss = float(
            np.sum(residual * residual) / batch_n
        )
        sparsity_loss = float(np.sum(features) / batch_n)
        gram_penalty, gram_gradient = _gram_penalty_and_grad(decoder)

        grad_reconstruction = (2.0 / batch_n) * residual
        grad_decoder = grad_reconstruction.T @ features + beta * gram_gradient
        grad_features = grad_reconstruction @ decoder
        if architecture == "l1":
            grad_features += cfg.l1_lambda / batch_n
        grad_preactivation = grad_features * active_mask
        grad_encoder = centered.T @ grad_preactivation
        grad_encoder_bias = np.sum(grad_preactivation, axis=0)
        grad_decoder_bias = np.sum(grad_reconstruction, axis=0)
        grad_decoder_bias -= np.sum(
            grad_preactivation @ encoder.T, axis=0
        )

        gradients = {
            "encoder": grad_encoder,
            "encoder_bias": grad_encoder_bias,
            "decoder": grad_decoder,
            "decoder_bias": grad_decoder_bias,
        }
        global_norm = math.sqrt(
            sum(float(np.sum(value * value)) for value in gradients.values())
        )
        if global_norm > cfg.grad_clip:
            factor = cfg.grad_clip / global_norm
            for value in gradients.values():
                value *= factor

        if step < steps // 2:
            learning_rate_scale = 1.0
        elif step < (4 * steps) // 5:
            learning_rate_scale = 1.0 / 3.0
        else:
            learning_rate_scale = 1.0 / 10.0
        optimizer.step(parameters, gradients, learning_rate_scale)
        decoder /= np.linalg.norm(decoder, axis=0, keepdims=True).clip(1e-8)

        if step == steps - 1:
            final_values = {
                "train_reconstruction_loss_last_batch": reconstruction_loss,
                "train_l1_last_batch": sparsity_loss,
                "train_gram_last_step": gram_penalty,
                "train_total_last_batch": (
                    reconstruction_loss
                    + (
                        cfg.l1_lambda * sparsity_loss
                        if architecture == "l1"
                        else 0.0
                    )
                    + beta * gram_penalty
                ),
                "train_gradient_norm_last_batch": global_norm,
            }

    return parameters, final_values


def _paired_factor_effects(
    values: np.ndarray,
    eval_base_n: int,
) -> tuple[np.ndarray, np.ndarray]:
    shaped = values.reshape(eval_base_n, 4, *values.shape[1:])
    # state order: 00, 10, 01, 11
    effect_1 = 0.5 * (
        (shaped[:, 1] - shaped[:, 0])
        + (shaped[:, 3] - shaped[:, 2])
    )
    effect_2 = 0.5 * (
        (shaped[:, 2] - shaped[:, 0])
        + (shaped[:, 3] - shaped[:, 1])
    )
    return effect_1, effect_2


def evaluate_sae(
    parameters: dict[str, np.ndarray],
    dataset: DatasetBundle,
    cfg: Config,
    seed: int,
    beta: float,
    architecture: str = "l1",
) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    encoder = parameters["encoder"]
    encoder_bias = parameters["encoder_bias"]
    decoder = parameters["decoder"]
    decoder_bias = parameters["decoder_bias"]

    _, features, _ = _encode(
        dataset.eval_x,
        encoder,
        encoder_bias,
        decoder_bias,
        architecture,
        cfg.topk_k,
    )
    reconstruction = features @ decoder.T + decoder_bias
    residual = reconstruction - dataset.eval_x
    eval_centered = dataset.eval_x - dataset.eval_x.mean(axis=0)
    fvu = float(
        np.sum(residual * residual) / np.sum(eval_centered * eval_centered)
    )
    l0 = float(np.mean(np.sum(features > cfg.eval_threshold, axis=1)))
    dead_mask = np.max(features, axis=0) <= cfg.eval_threshold
    dead_fraction = float(np.mean(dead_mask))
    gram_penalty, _ = _gram_penalty_and_grad(decoder)
    gram = decoder.T @ decoder
    upper = np.abs(gram[np.triu_indices(gram.shape[0], k=1)])
    max_abs_coherence = float(np.max(upper))
    mean_sq_coherence = float(np.mean(upper * upper))

    feature_effects = _paired_factor_effects(
        features, dataset.eval_base_n
    )
    reconstruction_effects = _paired_factor_effects(
        reconstruction, dataset.eval_base_n
    )

    result: dict[str, Any] = {
        "seed": seed,
        "beta": beta,
        "architecture": architecture,
        "d": dataset.ambient_dim,
        "m": decoder.shape[1],
        "fvu": fvu,
        "l0": l0,
        "dead_fraction": dead_fraction,
        "gram_penalty": gram_penalty,
        "mean_squared_coherence": mean_sq_coherence,
        "max_absolute_coherence": max_abs_coherence,
    }

    factor_arrays: dict[str, np.ndarray] = {}
    for factor_index, (
        direction,
        feature_effect,
        reconstruction_effect,
    ) in enumerate(
        zip(
            dataset.causal_directions,
            feature_effects,
            reconstruction_effects,
        ),
        start=1,
    ):
        mean_feature_effect = feature_effect.mean(axis=0)
        mean_reconstruction_effect = reconstruction_effect.mean(axis=0)
        decoder_cosines = direction @ decoder
        positive_geometry = np.maximum(decoder_cosines, 0.0)
        absolute_geometry = np.abs(decoder_cosines)

        # The mean causal contribution of atom k is
        # E[delta f_k] d_k.  Its projection onto the true causal direction is
        # the activation-aware amount of the factor carried by that atom.
        aligned_contributions = mean_feature_effect * decoder_cosines
        positive_contributions = np.maximum(aligned_contributions, 0.0)
        contribution_sum = float(np.sum(positive_contributions))
        contribution_max = float(np.max(positive_contributions))
        concentration = (
            contribution_max / contribution_sum
            if contribution_sum > 1e-12
            else 0.0
        )
        participation_ratio = (
            contribution_sum * contribution_sum
            / float(np.sum(positive_contributions**2))
            if np.sum(positive_contributions**2) > 1e-12
            else 0.0
        )
        split_count = int(
            np.sum(
                positive_contributions
                >= cfg.split_relative_threshold
                * max(contribution_max, 1e-12)
            )
        )

        family_gain = float(
            direction @ mean_reconstruction_effect
            / dataset.effective_factor_amplitude
        )
        family_norm_ratio = float(
            np.linalg.norm(mean_reconstruction_effect)
            / dataset.effective_factor_amplitude
        )
        family_cosine = float(
            direction @ mean_reconstruction_effect
            / max(np.linalg.norm(mean_reconstruction_effect), 1e-12)
        )
        single_gain = (
            contribution_max / dataset.effective_factor_amplitude
        )

        nnls_code, nnls_residual = nnls(decoder, direction)
        nnls_reconstruction = decoder @ nnls_code
        nnls_cosine = float(
            direction @ nnls_reconstruction
            / max(np.linalg.norm(nnls_reconstruction), 1e-12)
        )

        prefix = f"factor{factor_index}_"
        result.update(
            {
                prefix + "max_positive_cosine": float(
                    np.max(positive_geometry)
                ),
                prefix + "max_absolute_cosine": float(
                    np.max(absolute_geometry)
                ),
                prefix + "faithful_geometry": bool(
                    np.max(positive_geometry) >= cfg.alignment_threshold
                ),
                prefix + "causal_concentration": float(concentration),
                prefix + "causal_participation_ratio": float(
                    participation_ratio
                ),
                prefix + "causal_split_count": split_count,
                prefix + "single_gain": float(single_gain),
                prefix + "family_gain": family_gain,
                prefix + "family_norm_ratio": family_norm_ratio,
                prefix + "family_cosine": family_cosine,
                prefix + "nnls_residual": float(nnls_residual),
                prefix + "nnls_cosine": nnls_cosine,
            }
        )
        factor_arrays[prefix + "decoder_cosines"] = decoder_cosines
        factor_arrays[prefix + "mean_feature_effect"] = mean_feature_effect
        factor_arrays[
            prefix + "positive_contributions"
        ] = positive_contributions

    # Factor averages are the preregistration's seed-level experimental units.
    average_fields = [
        "max_positive_cosine",
        "max_absolute_cosine",
        "causal_concentration",
        "causal_participation_ratio",
        "causal_split_count",
        "single_gain",
        "family_gain",
        "family_norm_ratio",
        "family_cosine",
        "nnls_residual",
        "nnls_cosine",
    ]
    for field in average_fields:
        result["mean_factor_" + field] = float(
            0.5 * (result["factor1_" + field] + result["factor2_" + field])
        )
    result["both_faithful_geometry"] = bool(
        result["factor1_faithful_geometry"]
        and result["factor2_faithful_geometry"]
    )
    return result, factor_arrays


def _parse_csv_numbers(text: str, cast: Any) -> list[Any]:
    return [cast(item.strip()) for item in text.split(",") if item.strip()]


def _write_csv(path: Path, records: list[dict[str, Any]]) -> None:
    fieldnames: list[str] = []
    seen: set[str] = set()
    for record in records:
        for key in record:
            if key not in seen:
                fieldnames.append(key)
                seen.add(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(records)


def _environment_metadata() -> dict[str, Any]:
    return {
        "python": sys.version,
        "platform": platform.platform(),
        "numpy": np.__version__,
        "scipy": scipy.__version__,
        "sklearn": sklearn.__version__,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--architectures",
        default="l1",
        help="comma-separated architectures from {l1,topk}",
    )
    parser.add_argument(
        "--seeds",
        default="0,1,2,3,4,5,6,7",
        help="comma-separated SAE initialization seeds",
    )
    parser.add_argument(
        "--betas",
        default="0,0.025,0.0625,0.25,0.5",
        help="comma-separated full squared-Gram coefficients",
    )
    parser.add_argument(
        "--widths",
        default="68",
        help="comma-separated overcomplete latent widths",
    )
    parser.add_argument(
        "--steps",
        type=int,
        default=None,
        help="override the registered 10000 training steps (for smoke/pilot only)",
    )
    parser.add_argument(
        "--outdir",
        type=Path,
        required=True,
        help="new or existing result directory",
    )
    parser.add_argument(
        "--save-weights",
        action="store_true",
        help="save small NumPy weight archives for every run",
    )
    args = parser.parse_args()

    cfg = Config()
    seeds = _parse_csv_numbers(args.seeds, int)
    betas = _parse_csv_numbers(args.betas, float)
    widths = _parse_csv_numbers(args.widths, int)
    architectures = [
        item.strip()
        for item in args.architectures.split(",")
        if item.strip()
    ]
    args.outdir.mkdir(parents=True, exist_ok=True)
    if not seeds or not betas or not architectures or not widths:
        raise ValueError(
            "at least one architecture, width, seed, and beta are required"
        )
    if any(item not in {"l1", "topk"} for item in architectures):
        raise ValueError("architectures must be l1 and/or topk")

    started = time.time()
    dataset = build_dataset(cfg)
    print(
        "dataset "
        f"train={dataset.train_x.shape} eval={dataset.eval_x.shape} "
        f"classifier_acc={dataset.classifier_eval_accuracy:.4f} "
        f"sha256={dataset.data_sha256[:16]}",
        flush=True,
    )

    records: list[dict[str, Any]] = []
    for architecture in architectures:
        for latent_width in widths:
            if latent_width <= dataset.ambient_dim:
                raise ValueError(
                    f"width {latent_width} is not overcomplete for "
                    f"d={dataset.ambient_dim}"
                )
            for seed in seeds:
                for beta in betas:
                    run_started = time.time()
                    parameters, train_stats = train_sae(
                        dataset.train_x,
                        cfg,
                        seed=seed,
                        beta=beta,
                        architecture=architecture,
                        latent_width=latent_width,
                        steps_override=args.steps,
                    )
                    result, factor_arrays = evaluate_sae(
                        parameters,
                        dataset,
                        cfg,
                        seed=seed,
                        beta=beta,
                        architecture=architecture,
                    )
                    result.update(train_stats)
                    result["wall_seconds"] = float(time.time() - run_started)
                    records.append(result)
                    print(
                        f"arch={architecture} m={latent_width} "
                        f"seed={seed:03d} beta={beta:.6g} "
                        f"FVU={result['fvu']:.4f} L0={result['l0']:.1f} "
                        f"dead={result['dead_fraction']:.1%} "
                        f"align={result['mean_factor_max_positive_cosine']:.3f} "
                        f"conc={result['mean_factor_causal_concentration']:.3f} "
                        f"family={result['mean_factor_family_gain']:.3f} "
                        f"split={result['mean_factor_causal_split_count']:.1f} "
                        f"({result['wall_seconds']:.1f}s)",
                        flush=True,
                    )
                    if args.save_weights:
                        weight_path = args.outdir / (
                            f"weights_{architecture}_m{latent_width}_"
                            f"seed{seed:03d}_beta{beta:.6g}.npz"
                        )
                        np.savez_compressed(
                            weight_path,
                            **parameters,
                            **factor_arrays,
                        )

    csv_path = args.outdir / "run_metrics.csv"
    _write_csv(csv_path, records)
    metadata = {
        "config": asdict(cfg),
        "architectures": architectures,
        "widths": widths,
        "seeds": seeds,
        "betas": betas,
        "steps_override": args.steps,
        "dataset": {
            "data_sha256": dataset.data_sha256,
            "classifier_train_accuracy": dataset.classifier_train_accuracy,
            "classifier_eval_accuracy": dataset.classifier_eval_accuracy,
            "train_base_n": dataset.train_base_n,
            "eval_base_n": dataset.eval_base_n,
            "train_shape": list(dataset.train_x.shape),
            "eval_shape": list(dataset.eval_x.shape),
            "ambient_dim": dataset.ambient_dim,
            "effective_factor_amplitude": (
                dataset.effective_factor_amplitude
            ),
        },
        "environment": _environment_metadata(),
        "wall_seconds": float(time.time() - started),
    }
    metadata_path = args.outdir / "metadata.json"
    metadata_path.write_text(
        json.dumps(metadata, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(f"saved {csv_path} and {metadata_path}", flush=True)


if __name__ == "__main__":
    main()
