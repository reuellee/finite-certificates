"""Strict helpers for committed Python-literal witness artifacts."""

from __future__ import annotations

import ast
from pathlib import Path


def read_literal_assignments(path: Path, expected_names: set[str]) -> dict[str, object]:
    """Read simple literal assignments without executing repository code."""
    values: dict[str, object] = {}
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    for node in tree.body:
        if not (
            isinstance(node, ast.Assign)
            and len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id in expected_names
        ):
            raise ValueError(
                f"{path.name} must contain only assignments to {sorted(expected_names)}"
            )
        name = node.targets[0].id
        if name in values:
            raise ValueError(f"duplicate artifact assignment: {name}")
        values[name] = ast.literal_eval(node.value)
    if set(values) != expected_names:
        raise ValueError(
            f"artifact keys are {sorted(values)}, expected {sorted(expected_names)}"
        )
    return values
