#!/usr/bin/env python3
"""Build the exact row-2599 first-four-support gate certificate."""

import json
from pathlib import Path

import diag3_pair_global_four_support_core as core


OUTPUT = Path(__file__).resolve().parent / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_GATE.json"


def main():
    OUTPUT.write_text(json.dumps(core.build_record(), indent=2, sort_keys=True) + "\n")
    print("WROTE", OUTPUT)


if __name__ == "__main__":
    main()
