#!/usr/bin/env python3
"""Build the exact four-support cube/fiber projection certificate."""

import json
from pathlib import Path

import diag3_pair_global_four_support_projection_core as core


OUTPUT = Path(__file__).resolve().parent / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_PROJECTION.json"


def main():
    OUTPUT.write_text(json.dumps(core.build_record(), indent=2, sort_keys=True) + "\n")
    print("WROTE", OUTPUT)


if __name__ == "__main__":
    main()
