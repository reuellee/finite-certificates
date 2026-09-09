#!/usr/bin/env python3
"""Replay a selected historical gate unchanged in its pinned clean worktree.

Publication through GitHub's Git Data API has a different commit ancestry from
the original local research commits.  The evidence bundle supplies those exact
objects.  This adapter keeps historical context assertions intact; missing
objects, changed verifier bytes, changed trees, and replay failures are fatal.
The current canonical-state and exploration gates still run in the live tree.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[4]


def git(*arguments: str, binary: bool = False):
    return subprocess.check_output(
        ["git", *arguments], cwd=ROOT, text=not binary, stderr=subprocess.PIPE
    )


def replay(path: str) -> None:
    tree = ast.parse((ROOT / "run_all.py").read_text(encoding="utf-8"))
    assignments = [
        node for node in tree.body
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "HISTORICAL_REPLAYS"
                for target in node.targets)
    ]
    if len(assignments) != 1:
        raise AssertionError("historical replay mapping must be unique")
    mappings = ast.literal_eval(assignments[0].value)
    if path not in mappings:
        raise AssertionError("path has no declared historical replay")
    revision, expected_tree, current_digest, historical_digest = mappings[path]
    if hashlib.sha256((ROOT / path).read_bytes()).hexdigest() != current_digest:
        raise AssertionError("current verifier differs from reviewed publication input")
    if git("rev-parse", f"{revision}^{{tree}}").strip() != expected_tree:
        raise AssertionError("historical tree pin differs")
    if hashlib.sha256(git("show", f"{revision}:{path}", binary=True)).hexdigest() != historical_digest:
        raise AssertionError("historical verifier differs")

    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    with tempfile.TemporaryDirectory(prefix="finite-certificates-replay-") as temporary:
        checkout = Path(temporary) / "checkout"
        added = False
        try:
            subprocess.run(
                ["git", "worktree", "add", "--quiet", "--detach", str(checkout), revision],
                cwd=ROOT, check=True,
            )
            added = True
            if subprocess.check_output(
                ["git", "status", "--porcelain"], cwd=checkout, text=True
            ).strip():
                raise AssertionError("historical worktree is not clean")
            script = checkout / path
            subprocess.run(
                [sys.executable, "-B", script.name], cwd=script.parent,
                env=environment, check=True,
            )
        finally:
            if added:
                subprocess.run(
                    ["git", "worktree", "remove", "--force", str(checkout)],
                    cwd=ROOT, check=True,
                )
    print(f"PASS historical replay {path} at {revision}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="exact selected repository verifier path")
    replay(parser.parse_args().path)
