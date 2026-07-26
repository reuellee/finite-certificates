#!/usr/bin/env python3
"""Finite-difference checks for the NumPy SAE and causal-data construction."""

from __future__ import annotations

import sys
from dataclasses import replace
from pathlib import Path

import numpy as np

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT))

from experiments.coherence_transfer_semireal import (
    Config,
    _apply_topk,
    _gram_penalty_and_grad,
    build_dataset,
)


def objective_and_gradients(
    batch: np.ndarray,
    parameters: dict[str, np.ndarray],
    cfg: Config,
    beta: float,
    architecture: str,
) -> tuple[float, dict[str, np.ndarray]]:
    encoder = parameters["encoder"]
    encoder_bias = parameters["encoder_bias"]
    decoder = parameters["decoder"]
    decoder_bias = parameters["decoder_bias"]
    centered = batch - decoder_bias
    preactivation = centered @ encoder + encoder_bias
    dense_features = np.maximum(preactivation, 0.0)
    if architecture == "l1":
        features = dense_features
        active_mask = preactivation > 0.0
    else:
        features, active_mask = _apply_topk(
            dense_features, cfg.topk_k
        )
    reconstruction = features @ decoder.T + decoder_bias
    residual = reconstruction - batch
    batch_n = batch.shape[0]
    gram_penalty, gram_gradient = _gram_penalty_and_grad(decoder)
    objective = float(np.sum(residual * residual) / batch_n)
    if architecture == "l1":
        objective += cfg.l1_lambda * float(np.sum(features) / batch_n)
    objective += beta * gram_penalty

    grad_reconstruction = (2.0 / batch_n) * residual
    grad_decoder = grad_reconstruction.T @ features + beta * gram_gradient
    grad_features = grad_reconstruction @ decoder
    if architecture == "l1":
        grad_features += cfg.l1_lambda / batch_n
    grad_preactivation = grad_features * active_mask
    gradients = {
        "encoder": centered.T @ grad_preactivation,
        "encoder_bias": np.sum(grad_preactivation, axis=0),
        "decoder": grad_decoder,
        "decoder_bias": (
            np.sum(grad_reconstruction, axis=0)
            - np.sum(grad_preactivation @ encoder.T, axis=0)
        ),
    }
    return objective, gradients


def directional_check(architecture: str) -> float:
    rng = np.random.default_rng(1234)
    batch_n, d, m = 7, 4, 6
    cfg = replace(Config(), topk_k=2)
    batch = rng.normal(size=(batch_n, d))
    decoder = rng.normal(size=(d, m))
    decoder /= np.linalg.norm(decoder, axis=0, keepdims=True)
    parameters = {
        "encoder": rng.normal(size=(d, m)) * 0.3,
        "encoder_bias": rng.normal(size=m) * 0.2 + 0.15,
        "decoder": decoder,
        "decoder_bias": rng.normal(size=d) * 0.1,
    }
    directions = {
        name: rng.normal(size=value.shape)
        for name, value in parameters.items()
    }
    direction_norm = np.sqrt(
        sum(np.sum(value * value) for value in directions.values())
    )
    for value in directions.values():
        value /= direction_norm

    _, gradients = objective_and_gradients(
        batch, parameters, cfg, beta=0.17, architecture=architecture
    )
    analytic = float(
        sum(
            np.sum(gradients[name] * directions[name])
            for name in parameters
        )
    )
    epsilon = 1e-6
    plus = {
        name: value + epsilon * directions[name]
        for name, value in parameters.items()
    }
    minus = {
        name: value - epsilon * directions[name]
        for name, value in parameters.items()
    }
    objective_plus, _ = objective_and_gradients(
        batch, plus, cfg, beta=0.17, architecture=architecture
    )
    objective_minus, _ = objective_and_gradients(
        batch, minus, cfg, beta=0.17, architecture=architecture
    )
    numeric = (objective_plus - objective_minus) / (2.0 * epsilon)
    relative_error = abs(analytic - numeric) / max(
        1.0, abs(analytic), abs(numeric)
    )
    print(
        f"{architecture}: analytic={analytic:.12f} "
        f"numeric={numeric:.12f} relative_error={relative_error:.3e}"
    )
    return relative_error


def gram_check() -> float:
    rng = np.random.default_rng(4321)
    decoder = rng.normal(size=(5, 8))
    decoder /= np.linalg.norm(decoder, axis=0, keepdims=True)
    direction = rng.normal(size=decoder.shape)
    direction /= np.linalg.norm(direction)
    _, gradient = _gram_penalty_and_grad(decoder)
    analytic = float(np.sum(gradient * direction))
    epsilon = 1e-6
    plus, _ = _gram_penalty_and_grad(decoder + epsilon * direction)
    minus, _ = _gram_penalty_and_grad(decoder - epsilon * direction)
    numeric = (plus - minus) / (2.0 * epsilon)
    relative_error = abs(analytic - numeric) / max(
        1.0, abs(analytic), abs(numeric)
    )
    print(
        f"gram: analytic={analytic:.12f} numeric={numeric:.12f} "
        f"relative_error={relative_error:.3e}"
    )
    return relative_error


def causal_direction_check() -> float:
    cfg = Config()
    dataset = build_dataset(cfg)
    shaped = dataset.eval_x.reshape(dataset.eval_base_n, 4, -1)
    observed_1 = 0.5 * (
        (shaped[:, 1] - shaped[:, 0])
        + (shaped[:, 3] - shaped[:, 2])
    )
    observed_2 = 0.5 * (
        (shaped[:, 2] - shaped[:, 0])
        + (shaped[:, 3] - shaped[:, 1])
    )
    expected = (
        dataset.effective_factor_amplitude
        * dataset.causal_directions
    )
    error = max(
        float(np.max(np.abs(observed_1 - expected[0]))),
        float(np.max(np.abs(observed_2 - expected[1]))),
    )
    print(f"causal construction max_abs_error={error:.3e}")
    return error


def main() -> None:
    errors = [
        gram_check(),
        directional_check("l1"),
        directional_check("topk"),
    ]
    causal_error = causal_direction_check()
    assert max(errors) < 1e-7
    assert causal_error < 2e-6
    print("ALL GRADIENT AND CAUSAL-CONSTRUCTION CHECKS PASSED")


if __name__ == "__main__":
    main()
