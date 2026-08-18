#!/usr/bin/env python3
"""Independent direct-determinant replay of the row-2599 candidate list.

The generator in ``verify_diag9_parent_ranking.py`` uses catalog-wide
chirotope bitsets and invariant bracket formulas.  This checker instead uses
the stored integer realization of parent 2599, constructs every transported
circuit certificate, and evaluates its four-by-four determinants directly.
The complement of the conflicting-factor set must equal the binary artifact
entry for entry.

Candidate means only "not certified empty by this circuit conflict".  No
candidate factor wall is asserted to be nonempty.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
import struct
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
sys.path.insert(0, str(HERE))

import DIAG9_GRAPH_exact_topes as topes  # noqa: E402
import verify_diag9_parent_ranking as ranking  # noqa: E402


ARTIFACT = DATA / "DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin"
ARTIFACT_SHA256 = "adb2e7257457f158e809450683c46fe7ecafdbdd4a7efdf9ac630e8a4f0fb03f"
FACTOR_CENSUS = DATA / "DIAG9_GRAPH_global_factor_census.npz"
FACTOR_CENSUS_SHA256 = "3984ce87e11fd59d804e59568177248e218cd1c7bb07aae0a9f9f746858728bc"
CATALOG = HERE / "certs_4_8.jsonl"
CATALOG_SHA256 = "c55e805d60d8086bcb84a312f2103a9973fc2691d0fd97f3d9a1d9809d2b163b"
PARENT = 2_599
FACTOR_COUNT = 26_740
CANDIDATE_COUNT = 17_824
EMPTY_COUNT = 8_916
CONFLICTING_OCCURRENCES = 27_944


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def sign(value):
    if not value:
        raise AssertionError("a direct circuit coefficient vanished")
    return 1 if value > 0 else -1


def direct_pattern(certificate, rows):
    if certificate[0] == "ordinary":
        circuit, auxiliary = certificate[1], certificate[2]
        columns = circuit + (auxiliary,)
        coefficient_count = 4
    else:
        circuit, residual, structural = certificate[1:4]
        columns = circuit + (residual, structural)
        coefficient_count = 3
    coefficients = {
        circuit[omitted]: (-1 if omitted & 1 else 1)
        * sign(
            ranking.det4(
                *(rows[index] for index in columns[:omitted] + columns[omitted + 1 :])
            )
        )
        for omitted in range(coefficient_count)
    }
    support = tuple(sorted(circuit))
    normalization = coefficients[support[0]]
    return support, tuple(
        coefficients[index] * normalization for index in support
    )


def parse_artifact():
    if sha256(ARTIFACT) != ARTIFACT_SHA256:
        raise AssertionError("candidate-factor artifact SHA-256 changed")
    raw = ARTIFACT.read_bytes()
    magic, parent, factor_count, candidate_count = struct.unpack_from(
        "<8sIII", raw
    )
    if (
        magic != ranking.CANDIDATE_MAGIC
        or parent != PARENT
        or factor_count != FACTOR_COUNT
        or candidate_count != CANDIDATE_COUNT
        or len(raw) != struct.calcsize("<8sIII") + 4 * candidate_count
    ):
        raise AssertionError("candidate-factor artifact header changed")
    candidates = tuple(
        map(
            int,
            np.frombuffer(raw, dtype="<u4", offset=struct.calcsize("<8sIII")),
        )
    )
    if (
        candidates != tuple(sorted(candidates))
        or len(set(candidates)) != candidate_count
        or candidates[0] < 0
        or candidates[-1] >= factor_count
    ):
        raise AssertionError("candidate-factor IDs are malformed")
    return candidates


def direct_candidates():
    if sha256(FACTOR_CENSUS) != FACTOR_CENSUS_SHA256:
        raise AssertionError("global factor census SHA-256 changed")
    if sha256(CATALOG) != CATALOG_SHA256:
        raise AssertionError("rank-four catalog SHA-256 changed")
    records = [
        json.loads(line)
        for line in CATALOG.read_text(encoding="utf-8").splitlines()
        if line
    ]
    if len(records) != 2_628 or records[PARENT]["verdict"] != "REALIZABLE":
        raise AssertionError("row-2599 catalog record changed")
    matrix = records[PARENT]["matrix"]
    expected_signs = tuple(
        1 if symbol == "+" else -1 for symbol in records[PARENT]["chi"]
    )
    if topes.parent_signs(matrix) != expected_signs:
        raise AssertionError("row-2599 matrix does not realize its chirotope")
    rows = topes.derived_rows(matrix)
    certificates = ranking.transported_certificates()

    with np.load(FACTOR_CENSUS, allow_pickle=False) as source:
        if str(source["format"].item()) != "diag9-global-residual-factor-census-v1":
            raise AssertionError("wrong global factor census format")
        foursets = tuple(
            tuple(map(int, row)) for row in source["occurrence_fourset"]
        )
        occurrence_factor = tuple(map(int, source["occurrence_factor"]))
        factor_count = len(source["factor_multiplicity"])
    if (
        len(foursets) != 84_840
        or tuple(sorted(certificates)) != foursets
        or factor_count != FACTOR_COUNT
    ):
        raise AssertionError("factor occurrence transport changed")

    empty = set()
    conflicting = 0
    for occurrence_index, occurrence in enumerate(foursets):
        patterns = {
            direct_pattern(certificate, rows)
            for certificate in certificates[occurrence]
        }
        if len(patterns) > 1:
            conflicting += 1
            empty.add(occurrence_factor[occurrence_index])
    if conflicting != CONFLICTING_OCCURRENCES or len(empty) != EMPTY_COUNT:
        raise AssertionError("the direct row-2599 conflict census changed")
    return tuple(factor for factor in range(factor_count) if factor not in empty)


def main():
    stored = parse_artifact()
    direct = direct_candidates()
    if stored != direct:
        raise AssertionError("stored candidates disagree with direct determinants")
    print("PASS binary candidate-factor artifact", len(stored), ARTIFACT_SHA256)
    print("PASS independent direct row-2599 determinant replay")
    print(
        "PASS",
        CONFLICTING_OCCURRENCES,
        "conflicting occurrences certify",
        EMPTY_COUNT,
        "empty factor walls",
    )
    print("CANDIDATE_INPUT", CANDIDATE_COUNT, "sorted zero-based factor IDs")
    print("SCOPE generator input only; no candidate wall is asserted nonempty")


if __name__ == "__main__":
    main()
