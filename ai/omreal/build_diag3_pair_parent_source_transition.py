#!/usr/bin/env python3
"""Build the exact chart-0 to chart-89 row-2599 transition roadmap."""

from __future__ import annotations

import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import diag3_pair_parent_source_transition_core as core  # noqa: E402


def main():
    record = core.build_record()
    core.OUTPUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print("WROTE", core.OUTPUT)


if __name__ == "__main__":
    main()
