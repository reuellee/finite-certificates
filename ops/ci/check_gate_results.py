#!/usr/bin/env python3
"""Fail the stable required check if an expected CI job skipped or failed."""

from __future__ import annotations

import json
import os


FLAG_TO_JOB = {
    "proof_change": "fast-suite",
    "slow_changed": "changed-slow-verifiers",
    "external_changed": "external-input-verifier-policy",
}
FULL_OR_FLAG_TO_JOB = {
    "maxout": "maxout-capstone",
}
FULL_EXHAUSTIVE_OR_FLAG_TO_JOB = {
    "diag2_atlas": "nine-dvl-diag2-atlas",
    "labeled_pairs": "nine-dvl-labeled-pairs",
    "source_block_labels": "nine-dvl-source-block-labels",
    "parent860": "nine-dvl-parent860-pilot",
}
EXHAUSTIVE_JOBS = ("suite-shards",)
FULL_JOBS = ("full-audit",)
ALWAYS_JOBS = ("plan", "quick-gate")


def truth(value: object) -> bool:
    return str(value).lower() == "true"


def audit(plan: dict[str, object], results: dict[str, object]) -> list[str]:
    failures = []

    def result(job: str) -> str:
        payload = results.get(job, {})
        return str(payload.get("result", "missing"))

    for job in ALWAYS_JOBS:
        if result(job) != "success":
            failures.append(f"{job}: expected success, got {result(job)}")

    full = truth(plan["full"])
    for flag, job in FLAG_TO_JOB.items():
        expected = truth(plan[flag])
        wanted = "success" if expected else "skipped"
        if result(job) != wanted:
            failures.append(f"{job}: expected {wanted}, got {result(job)}")
    exhaustive = full or truth(plan["exhaustive"])
    for flag, job in FULL_OR_FLAG_TO_JOB.items():
        expected = full or truth(plan[flag])
        wanted = "success" if expected else "skipped"
        if result(job) != wanted:
            failures.append(f"{job}: expected {wanted}, got {result(job)}")
    for flag, job in FULL_EXHAUSTIVE_OR_FLAG_TO_JOB.items():
        expected = exhaustive or truth(plan[flag])
        wanted = "success" if expected else "skipped"
        if result(job) != wanted:
            failures.append(f"{job}: expected {wanted}, got {result(job)}")
    for job in FULL_JOBS:
        wanted = "success" if full else "skipped"
        if result(job) != wanted:
            failures.append(f"{job}: expected {wanted}, got {result(job)}")
    for job in EXHAUSTIVE_JOBS:
        wanted = "success" if exhaustive else "skipped"
        if result(job) != wanted:
            failures.append(f"{job}: expected {wanted}, got {result(job)}")

    return failures


def main() -> int:
    plan = json.loads(os.environ["CI_PLAN"])
    results = json.loads(os.environ["CI_RESULTS"])
    failures = audit(plan, results)
    if failures:
        for failure in failures:
            print("FAIL", failure)
        return 1
    print("PASS every CI job required by the deterministic plan completed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
