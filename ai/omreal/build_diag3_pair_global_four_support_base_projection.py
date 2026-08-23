#!/usr/bin/env python3
"""Build the exact second-projection frontier for the four-support base CAD."""

from __future__ import annotations

import gzip
import json
from pathlib import Path

import diag3_pair_global_four_support_base_projection_core as core


OUTPUT = Path(__file__).resolve().parent / "data" / "DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_BASE_PROJECTION.json.gz"


def main():
    record = core.build_record()
    encoded = (json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n").encode("ascii")
    OUTPUT.write_bytes(gzip.compress(encoded, compresslevel=9, mtime=0))
    print("WROTE", OUTPUT)
    print(
        "PROJECTION",
        record["second_projection"]["raw_nonconstant_obligations"],
        "->",
        record["second_projection"]["distinct_squarefree_boundary_reduced_polynomials"],
        "->",
        record["second_projection"]["distinct_factor_count"],
    )
    print(
        "ROOT_INCIDENCES",
        record["second_projection"]["factor_interior_root_incidences"],
    )


if __name__ == "__main__":
    main()
