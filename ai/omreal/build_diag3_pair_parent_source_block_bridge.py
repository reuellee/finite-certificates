#!/usr/bin/env python3
"""Build the exact row-2599 chart-0-to-chart-152 block bridge."""

from __future__ import annotations

import json

import diag3_pair_parent_source_block_bridge_core as core


def main():
    record = core.build_record(progress=True)
    core.OUTPUT.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(core.OUTPUT)


if __name__ == "__main__":
    main()
