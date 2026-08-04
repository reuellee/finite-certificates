#!/usr/bin/env python3
"""Verify self-describing row-2599 antichain and coordinate-path artifacts.

The two foundational verifiers retain hard-coded manifests for the canonical
charts-12/37 regression.  This wrapper reuses their independent exact
arithmetic while taking the signature family, chart indices, endpoint pair,
and format tag from another certificate.  It is intended for additional
stress families produced by the same certificate builders.  With no command
line arguments it verifies the two committed charts-37/176 artifacts so the
repository-wide ``run_all.py`` discovery contract remains self-contained.
"""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

DEFAULT_CERTIFICATES = (
    ("antichain", HERE / "data" / "ninth_candidate_37_176_antichain.npz"),
    ("path", HERE / "data" / "ninth_candidate_37_176_path.npz"),
)


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
    parser.add_argument("kind", nargs="?", choices=("antichain", "path"))
    parser.add_argument("certificate", nargs="?", type=Path)
    args = parser.parse_args()
    if args.kind is None and args.certificate is None:
        jobs = DEFAULT_CERTIFICATES
    elif args.kind is None or args.certificate is None:
        parser.error("kind and certificate must be supplied together")
    else:
        jobs = ((args.kind, args.certificate),)

    for kind, certificate in jobs:
        if kind == "antichain":
            verify_antichain(certificate)
        else:
            verify_path(certificate)


if __name__ == "__main__":
    main()
