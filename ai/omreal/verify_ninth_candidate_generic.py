#!/usr/bin/env python3
"""Verify a self-describing row-2599 antichain or coordinate-path artifact.

The two foundational verifiers retain hard-coded manifests for the canonical
charts-12/37 regression.  This wrapper reuses their independent exact
arithmetic while taking the signature family, chart indices, endpoint pair,
and format tag from another certificate.  It is intended for additional
stress families produced by the same certificate builders.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def verify_antichain(path: Path) -> None:
    import verify_ninth_candidate_antichain as verifier

    certificate = np.load(path, allow_pickle=False)
    verifier.CERTIFICATE = path
    verifier.FORMAT = str(certificate["format"].item())
    verifier.PARENT_INDEX = int(certificate["parent_index"].item())
    verifier.SIGNATURES = tuple(map(int, certificate["signature"]))
    verifier.CHARTS = tuple(map(int, certificate["chart_index"]))
    verifier.PATTERNS = tuple(map(str, certificate["pattern"]))
    verifier.main()


def verify_path(path: Path) -> None:
    import verify_ninth_candidate_path as verifier

    certificate = np.load(path, allow_pickle=False)
    verifier.CERTIFICATE = path
    verifier.FORMAT = str(certificate["format"].item())
    verifier.PARENT_INDEX = int(certificate["parent_index"].item())
    verifier.ENDPOINTS = tuple(map(int, certificate["endpoint"]))
    verifier.SIGNATURES = tuple(map(int, certificate["signature"]))
    verifier.main()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("kind", choices=("antichain", "path"))
    parser.add_argument("certificate", type=Path)
    args = parser.parse_args()
    if args.kind == "antichain":
        verify_antichain(args.certificate)
    else:
        verify_path(args.certificate)


if __name__ == "__main__":
    main()
