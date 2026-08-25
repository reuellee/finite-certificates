#!/usr/bin/env python3
"""Build the exact chart-0/chart-152 source-staircase coverage record."""

from __future__ import annotations

import json

import diag3_pair_source_staircase_coverage_core as core


def main():
    record = core.build_record(progress=True)
    core.OUTPUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n")
    print("WROTE", core.OUTPUT)


if __name__ == "__main__":
    main()
