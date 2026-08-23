#!/usr/bin/env python3
"""Block changes to verifiers whose pinned external input is unavailable in CI."""

from __future__ import annotations

import sys


def main() -> int:
    print(
        "FAIL an external-input verifier changed, but its pinned replay input is "
        "not committed or otherwise available to CI"
    )
    print(
        "Provide a replayable pinned input and a required CI command before "
        "changing this verifier. A syntax-only check is not proof validation."
    )
    return 1


if __name__ == "__main__":
    sys.exit(main())
