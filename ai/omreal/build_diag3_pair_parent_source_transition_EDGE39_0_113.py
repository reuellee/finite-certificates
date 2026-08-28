#!/usr/bin/env python3
"""Generate the exact retained-edge-39 residual transition certificate."""

import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import diag3_pair_parent_source_transition_EDGE39_0_113_core as core  # noqa: E402


def main():
    record = core.build_record(progress=True)
    core.OUTPUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print("WROTE", core.OUTPUT)


if __name__ == "__main__":
    main()
