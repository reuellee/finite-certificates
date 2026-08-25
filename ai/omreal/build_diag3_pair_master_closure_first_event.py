#!/usr/bin/env python3
"""Build the exact row-2599 64-box first-new-event certificate."""

from __future__ import annotations

import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
OUTPUT = HERE / "data" / "DIAG3_PAIR_MASTER_CLOSURE_FIRST_EVENT.json"
sys.path.insert(0, str(HERE))
import diag3_pair_first_event_core as core  # noqa: E402


def main():
    record = core.build_record()
    OUTPUT.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    print("WROTE", OUTPUT)


if __name__ == "__main__":
    main()
