#!/usr/bin/env python3
"""Build the exact chart-0 to chart-89 row-2599 transition roadmap."""

from __future__ import annotations

import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import diag3_pair_parent_source_transition_core as core  # noqa: E402


def canonical_record(record):
    """Return the platform-independent serialization of a core record."""

    return {
        **record,
        "inputs": {
            **record["inputs"],
            "point_bank_path": core.POINT_BANK.relative_to(HERE.parents[1]).as_posix(),
            "factor_states_path": core.FACTOR_STATES.relative_to(HERE.parents[1]).as_posix(),
            "factor_census_path": core.FACTOR_CENSUS.relative_to(HERE.parents[1]).as_posix(),
            "candidate_factor_path": core.CANDIDATES.relative_to(HERE.parents[1]).as_posix(),
        },
    }


def build_record():
    return canonical_record(core.build_record())


def main():
    record = build_record()
    core.OUTPUT.write_text(
        json.dumps(record, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    print("WROTE", core.OUTPUT)


if __name__ == "__main__":
    main()
