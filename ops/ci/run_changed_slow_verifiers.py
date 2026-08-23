#!/usr/bin/env python3
"""Run slow verifiers changed by, or directly dependent on, a Git diff."""

from __future__ import annotations

import argparse
from pathlib import Path
import subprocess
import sys
import time

from classify_changes import ROOT, changed_paths, slow_verifier_paths


TIMEOUT_SECONDS = 7_200


def parser() -> argparse.ArgumentParser:
    answer = argparse.ArgumentParser(description=__doc__)
    answer.add_argument("--base", required=True)
    answer.add_argument("--head", required=True)
    return answer


def main() -> int:
    arguments = parser().parse_args()
    paths = slow_verifier_paths(changed_paths(arguments.base, arguments.head))
    if not paths:
        print("PASS no changed slow verifier requires direct replay")
        return 0

    failures = []
    for raw in paths:
        path = ROOT / raw
        started = time.monotonic()
        print(f"START {raw}", flush=True)
        try:
            result = subprocess.run(
                [sys.executable, path.name],
                cwd=path.parent,
                timeout=TIMEOUT_SECONDS,
            )
        except subprocess.TimeoutExpired:
            failures.append(raw)
            print(f"TIMEOUT {raw} after {TIMEOUT_SECONDS}s", flush=True)
            continue
        elapsed = time.monotonic() - started
        status = "PASS" if result.returncode == 0 else "FAIL"
        print(f"{status} {raw} {elapsed:.1f}s", flush=True)
        if result.returncode != 0:
            failures.append(raw)
    print(f"{len(paths)} changed slow verifiers run; {len(failures)} failed")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
