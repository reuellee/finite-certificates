#!/usr/bin/env python3
"""Verify proof-surface entry points, local links, and archive policy."""

from __future__ import annotations

import re
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parent
ENTRY_POINTS = (
    "README.md",
    "CONTRIBUTING.md",
    "docs/RESEARCH_INDEX.md",
    "ai/maxout/README.md",
    "ai/omgamma/README.md",
    "ai/omopen/FINAL_RESIDUE.md",
    "ai/omminor/MINOR_THEORY.md",
    "ai/omreal/README.md",
    "ai/omreal/NINE_DIAGONAL_STATUS.md",
    "ai/omreal/data/DIAG9_RESEARCH_DECISION_LEDGER.json",
)
NAVIGATION_DOCS = (
    "README.md",
    "CONTRIBUTING.md",
    "docs/RESEARCH_INDEX.md",
    "ai/omreal/README.md",
)
REQUIRED_IGNORES = frozenset({"/backups/", "/reviews/"})
LINK_PATTERN = re.compile(r"\[[^\]]*\]\(([^)]+)\)")


def local_target(source: Path, raw_target: str) -> Path | None:
    target = raw_target.strip()
    if not target or target.startswith(("#", "http://", "https://", "mailto:")):
        return None
    target = target.split("#", 1)[0]
    return (source.parent / target).resolve()


def broken_links(source: Path, text: str) -> list[str]:
    failures = []
    for raw_target in LINK_PATTERN.findall(text):
        target = local_target(source, raw_target)
        if target is None:
            continue
        try:
            target.relative_to(ROOT)
        except ValueError:
            failures.append(f"{source.relative_to(ROOT)}: escapes repository: {raw_target}")
            continue
        if not target.exists():
            failures.append(f"{source.relative_to(ROOT)}: missing target: {raw_target}")
    return failures


def canaries() -> None:
    source = ROOT / "README.md"
    assert broken_links(source, "[external](https://example.com)") == []
    failure = broken_links(source, "[missing](definitely-not-present.md)")
    assert len(failure) == 1 and "missing target" in failure[0]
    escape = broken_links(source, "[escape](../outside.md)")
    assert len(escape) == 1 and "escapes repository" in escape[0]


def main() -> int:
    canaries()
    failures = []

    for relative in ENTRY_POINTS:
        if not (ROOT / relative).is_file():
            failures.append(f"missing proof entry point: {relative}")

    ignore_rules = {
        line.strip()
        for line in (ROOT / ".gitignore").read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    }
    for rule in sorted(REQUIRED_IGNORES - ignore_rules):
        failures.append(f"missing archive ignore rule: {rule}")

    ignored_tracked = subprocess.run(
        ["git", "ls-files", "-ci", "--exclude-standard"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.splitlines()
    if ignored_tracked:
        failures.append(
            f"{len(ignored_tracked)} files are both ignored and tracked"
        )

    for relative in NAVIGATION_DOCS:
        source = ROOT / relative
        if source.is_file():
            failures.extend(broken_links(source, source.read_text(encoding="utf-8")))

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if "**2/9**" not in readme:
        failures.append("README must expose the honest 9DVL score")
    if "reviews/" in readme:
        failures.append("README must not route readers to the raw review archive")

    if failures:
        for failure in failures:
            print("FAIL", failure)
        return 1

    print(
        "PASS repository proof surface:",
        len(ENTRY_POINTS),
        "entry points,",
        len(NAVIGATION_DOCS),
        "navigation documents, archive policy enforced",
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
