#!/usr/bin/env python3
"""Build the exact chart-89 to [1237]=0 parent-boundary attachment."""

from __future__ import annotations

import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import diag3_pair_parent_boundary_attachment_core as core  # noqa: E402


def main():
    record = core.build_record(progress=True)
    core.OUTPUT.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(core.OUTPUT)


if __name__ == "__main__":
    main()
