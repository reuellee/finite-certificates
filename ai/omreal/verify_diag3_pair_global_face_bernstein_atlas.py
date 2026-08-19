#!/usr/bin/env python3
"""Exact Bernstein face preflight for the row-2599 global cell generator.

The three moving columns have positive homogeneous coordinates, so every
primitive residual factor has a canonical multihomogenization on
``(Delta^3)^3``.  On the relative interior of a simplex-support face, the
multihomogeneous monomials form a positive Bernstein basis (up to positive
multinomial scalars).  Consequently:

* no surviving coefficient means the factor vanishes identically;
* coefficients of only one sign prove that the factor wall misses the face;
* coefficients of both signs leave an active subdivision obligation.

This checker exhausts all 17,824 row-2599 candidate factors on all 3,375
ambient support faces.  It is a generator preflight, not a regular-cell
decomposition: a mixed Bernstein restriction may still be sign-definite and
must be refined or decided by a later exact subdivision step.
"""

from __future__ import annotations

from collections import Counter
import hashlib
from itertools import product
import json
from pathlib import Path
import struct
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import verify_diag9_parent_ranking as ranking  # noqa: E402


CANDIDATES = DATA / "DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin"
FACTOR_CENSUS = DATA / "DIAG9_GRAPH_global_factor_census.npz"
MANIFEST = DATA / "DIAG3_PAIR_GLOBAL_row2599_face_bernstein_atlas.json"

CANDIDATE_SHA256 = (
    "adb2e7257457f158e809450683c46fe7ecafdbdd4a7efdf9ac630e8a4f0fb03f"
)
FACTOR_CENSUS_SHA256 = (
    "3984ce87e11fd59d804e59568177248e218cd1c7bb07aae0a9f9f746858728bc"
)
EXPECTED_CANDIDATES = 17_824
EXPECTED_FACES = 3_375
EXPECTED_INFINITY_FACES = 2_863
EXPECTED_SEMANTIC = "1bd501a4a2b08eebd55d39c078fed07c526308a53bbefb21823531843ca0da8b"
GROUPS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_candidates() -> tuple[int, ...]:
    if sha256(CANDIDATES) != CANDIDATE_SHA256:
        raise AssertionError("candidate-factor artifact SHA-256 changed")
    raw = CANDIDATES.read_bytes()
    header = struct.calcsize("<8sIII")
    magic, parent, factor_count, candidate_count = struct.unpack_from(
        "<8sIII", raw
    )
    if (
        magic != ranking.CANDIDATE_MAGIC
        or parent != 2_599
        or factor_count != 26_740
        or candidate_count != EXPECTED_CANDIDATES
        or len(raw) != header + 4 * candidate_count
    ):
        raise AssertionError("candidate-factor artifact header changed")
    answer = tuple(map(int, np.frombuffer(raw, dtype="<u4", offset=header)))
    if answer != tuple(sorted(set(answer))):
        raise AssertionError("candidate-factor IDs are not canonical")
    return answer


def faces() -> tuple[tuple[int, int, int], ...]:
    """Nonempty homogeneous-coordinate supports in lexicographic order."""

    answer = tuple(product(range(1, 16), repeat=3))
    if len(answer) != EXPECTED_FACES:
        raise AssertionError("wrong product-simplex face count")
    return answer


def face_dimension(face: tuple[int, int, int]) -> int:
    return sum(mask.bit_count() - 1 for mask in face)


def term_support(monomial, multidegree) -> tuple[int, int, int]:
    """Support masks after canonical multihomogenization.

    The affine variables in one moving column are rows 2,3,4.  Row 1 is the
    gauge coordinate, whose exponent fills the degree deficit.
    """

    answer = []
    for variables, degree in zip(GROUPS, multidegree, strict=True):
        affine = tuple(monomial[index] for index in variables)
        homogeneous = (degree - sum(affine),) + affine
        if homogeneous[0] < 0 or sum(homogeneous) != degree:
            raise AssertionError("invalid residual multihomogenization")
        answer.append(
            sum((exponent > 0) << row for row, exponent in enumerate(homogeneous))
        )
    return tuple(answer)


def survival_bitsets(face_order):
    """Faces on which a monomial with each support triple survives."""

    answer = {}
    for support in product(range(16), repeat=3):
        bits = 0
        for index, face in enumerate(face_order):
            if all(
                term_mask & ~face_mask == 0
                for term_mask, face_mask in zip(support, face, strict=True)
            ):
                bits |= 1 << index
        answer[support] = bits
    return answer


def canonical_manifest_digest(payload):
    semantic = dict(payload)
    expected = semantic.pop("semantic_sha256")
    actual = hashlib.sha256(
        json.dumps(semantic, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    if expected != actual or actual != EXPECTED_SEMANTIC:
        raise AssertionError("Bernstein face manifest semantic digest changed")
    return actual


def audit():
    if sha256(FACTOR_CENSUS) != FACTOR_CENSUS_SHA256:
        raise AssertionError("global factor census SHA-256 changed")
    candidate_ids = parse_candidates()
    _occurrences, _occurrence_factor, polynomials = labeled.factor_polynomials()
    if len(polynomials) != 26_740:
        raise AssertionError("wrong global residual-factor count")

    face_order = faces()
    face_count = len(face_order)
    byte_width = (face_count + 7) // 8
    valid_final_bits = (1 << (face_count & 7)) - 1 if face_count & 7 else 0xFF
    survival = survival_bitsets(face_order)
    positive_table = np.zeros((len(candidate_ids), byte_width), dtype=np.uint8)
    negative_table = np.zeros_like(positive_table)
    multidegree_histogram = Counter()
    signed_profile_histogram = Counter()
    stream = hashlib.sha256(b"diag3-row2599-face-bernstein-v1\0")

    full_face_index = face_order.index((15, 15, 15))
    for row, factor_id in enumerate(candidate_ids):
        polynomial = polynomials[factor_id]
        multidegree = tuple(
            max(sum(monomial[index] for index in variables) for monomial in polynomial)
            for variables in GROUPS
        )
        if any(degree not in (0, 1, 2) for degree in multidegree):
            raise AssertionError("candidate factor left the degree-two envelope")
        multidegree_histogram[multidegree] += 1
        positive = 0
        negative = 0
        for monomial, coefficient in polynomial.items():
            target = survival[term_support(monomial, multidegree)]
            if coefficient > 0:
                positive |= target
            elif coefficient < 0:
                negative |= target
            else:
                raise AssertionError("stored residual factor has zero coefficient")
        if not (positive & (1 << full_face_index)) or not (
            negative & (1 << full_face_index)
        ):
            raise AssertionError("a candidate factor is Bernstein definite globally")

        positive_bytes = positive.to_bytes(byte_width, "little")
        negative_bytes = negative.to_bytes(byte_width, "little")
        positive_table[row] = np.frombuffer(positive_bytes, dtype=np.uint8)
        negative_table[row] = np.frombuffer(negative_bytes, dtype=np.uint8)
        signed_profile_histogram[(positive_bytes, negative_bytes)] += 1
        stream.update(factor_id.to_bytes(4, "little"))
        stream.update(bytes(multidegree))
        stream.update(positive_bytes)
        stream.update(negative_bytes)

    padding_mask = np.uint8(0xFF ^ valid_final_bits)
    if np.any(positive_table[:, -1] & padding_mask) or np.any(
        negative_table[:, -1] & padding_mask
    ):
        raise AssertionError("nonzero padding bit in face-state table")

    positive = np.unpackbits(positive_table, axis=1, bitorder="little")[:, :face_count]
    negative = np.unpackbits(negative_table, axis=1, bitorder="little")[:, :face_count]
    mixed = positive & negative
    nonzero = positive | negative
    zero = nonzero ^ np.uint8(1)
    definite = nonzero & (mixed ^ np.uint8(1))
    if np.any(mixed + zero + definite != 1):
        raise AssertionError("face restriction states do not partition the atlas")

    active_by_face = mixed.sum(axis=0, dtype=np.int64)
    zero_by_face = zero.sum(axis=0, dtype=np.int64)
    definite_by_face = definite.sum(axis=0, dtype=np.int64)
    dimensions = np.asarray([face_dimension(face) for face in face_order])
    infinity = np.asarray(
        [any(not (mask & 1) for mask in face) for face in face_order], dtype=bool
    )
    if int(infinity.sum()) != EXPECTED_INFINITY_FACES:
        raise AssertionError("wrong standard-chart infinity support count")

    dimension_histogram = {}
    for dimension in range(10):
        selector = dimensions == dimension
        dimension_histogram[str(dimension)] = {
            "faces": int(selector.sum()),
            "zero": int(zero_by_face[selector].sum()),
            "definite": int(definite_by_face[selector].sum()),
            "mixed": int(active_by_face[selector].sum()),
        }

    active_columns = np.packbits(mixed, axis=0, bitorder="little").T
    unique_active_sets = len({row.tobytes() for row in active_columns})
    proper_face_selector = np.arange(face_count) != full_face_index
    factors_active_on_no_proper_face = int(
        np.count_nonzero(mixed[:, proper_face_selector].sum(axis=1) == 0)
    )

    state_pairs = int(len(candidate_ids) * face_count)
    counts = {
        "zero": int(zero.sum(dtype=np.int64)),
        "definite": int(definite.sum(dtype=np.int64)),
        "mixed": int(mixed.sum(dtype=np.int64)),
    }
    if sum(counts.values()) != state_pairs:
        raise AssertionError("global face-state accounting failed")

    return {
        "candidate_count": len(candidate_ids),
        "face_count": face_count,
        "infinity_face_count": int(infinity.sum()),
        "factor_face_pair_count": state_pairs,
        "state_counts": counts,
        "dimension_histogram": dimension_histogram,
        "active_factor_range_per_face": [
            int(active_by_face.min()), int(active_by_face.max())
        ],
        "zero_factor_range_per_face": [int(zero_by_face.min()), int(zero_by_face.max())],
        "definite_factor_range_per_face": [
            int(definite_by_face.min()), int(definite_by_face.max())
        ],
        "unique_signed_factor_face_profiles": len(signed_profile_histogram),
        "maximum_signed_profile_multiplicity": max(signed_profile_histogram.values()),
        "unique_active_factor_sets_on_faces": unique_active_sets,
        "factors_active_on_no_proper_face": factors_active_on_no_proper_face,
        "multidegree_histogram": {
            ",".join(map(str, degree)): count
            for degree, count in sorted(multidegree_histogram.items())
        },
        "face_state_stream_sha256": stream.hexdigest(),
    }


def main():
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if payload.get("format") != "diag3-pair-global-row2599-face-bernstein-v1":
        raise AssertionError("wrong Bernstein face manifest format")
    semantic = canonical_manifest_digest(payload)
    actual = audit()
    for key, value in actual.items():
        if payload.get(key) != value:
            raise AssertionError(
                f"Bernstein face manifest mismatch for {key}: "
                f"{payload.get(key)!r} != {value!r}"
            )
    counts = actual["state_counts"]
    eliminated = counts["zero"] + counts["definite"]
    print("PASS canonical multihomogenization of", actual["candidate_count"], "factors")
    print("PASS exact Bernstein restrictions on", actual["face_count"], "support faces")
    print(
        "STATES",
        counts["zero"],
        "identically-zero;",
        counts["definite"],
        "wall-free;",
        counts["mixed"],
        "active",
    )
    print("ELIMINATED", eliminated, "of", actual["factor_face_pair_count"], "face tasks")
    print(
        "ACTIVE_RANGE",
        *actual["active_factor_range_per_face"],
        "over",
        actual["unique_active_factor_sets_on_faces"],
        "distinct face inputs",
    )
    print("FACE_STATE_SHA256", actual["face_state_stream_sha256"])
    print("SEMANTIC_SHA256", semantic)
    print("SCOPE exact generator preflight; mixed restrictions still require subdivision")


if __name__ == "__main__":
    main()
