#!/usr/bin/env python3
"""Exact parent-feasibility gate on the row-2599 compactification faces.

The ambient compactification ``(Delta^3)^3`` has 3,375 relative support
strata.  This checker canonically multihomogenizes the seventy signed parent
brackets and restricts them to every stratum.  A Bernstein restriction with
only coefficients of the wrong parent sign excludes the whole relative
stratum from the weak parent closure.

The eleven strata not excluded by this sign test are independently shown
nonempty by exact rational witnesses.  Candidate residual-factor states are
then replayed directly on those eleven strata, and the two surviving ambient
support edges are solved exactly.  This is a support-face gate, not the
internal parent/residual master-cell decomposition inside the full chart.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
import hashlib
from itertools import combinations
import json
from pathlib import Path
import struct
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
DATA = HERE / "data"
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG9_GRAPH_exact_topes as topes  # noqa: E402
import DIAG9_GRAPH_global_factor_census as global_factors  # noqa: E402
import verify_diag2_canonical_robust_edges as evaluator  # noqa: E402
import verify_diag3_pair_global_face_bernstein_atlas as bernstein  # noqa: E402
import verify_diag3_triple_rank_drop_parent_atlas as normalization  # noqa: E402
import verify_diag9_parent_ranking as ranking  # noqa: E402


CATALOG = HERE / "certs_4_8.jsonl"
POINT_BANK = DATA / "seeat_parent2599_upper178.npz"
FACTOR_CENSUS = DATA / "DIAG9_GRAPH_global_factor_census.npz"
CANDIDATES = DATA / "DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin"
MANIFEST = DATA / "DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json"

PARENT = 2_599
CATALOG_SHA256 = "c55e805d60d8086bcb84a312f2103a9973fc2691d0fd97f3d9a1d9809d2b163b"
POINT_BANK_SHA256 = "3b90799d26b7783e92c2ac697eaaf8b76d26a787f53205873b997657e114180a"
FACTOR_CENSUS_SHA256 = "3984ce87e11fd59d804e59568177248e218cd1c7bb07aae0a9f9f746858728bc"
CANDIDATE_SHA256 = "adb2e7257457f158e809450683c46fe7ecafdbdd4a7efdf9ac630e8a4f0fb03f"
EXPECTED_SEMANTIC = "3be26a3ff6849043a43b8e56cc3ac29a05cc9c955b2a0fbe41b74ba4c742c106"
EXPECTED_TARGET_DIGEST = "1d9b940e2bb954b5c69bcee8b2346f9554b2e15589ea4c5b3c3f8e1e943de701"

ZERO = 0
RIGHT = 1
WRONG = 2
MIXED = 3

SPECIAL_WITNESS = (
    Fraction(71, 81), Fraction(67, 100), Fraction(1, 2),
    Fraction(48, 91), Fraction(36, 71), Fraction(0),
    Fraction(43, 60), Fraction(87, 94), Fraction(35, 53),
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def sign(value) -> int:
    if not value:
        raise AssertionError("uniform parent sample acquired a zero bracket")
    return 1 if value > 0 else -1


def normalized_values(matrix) -> tuple[Fraction, ...]:
    normalized = normalization.normalized_matrix(matrix, tuple(range(8)))
    answer = []
    for column in (5, 6, 7):
        gauge = normalized[column][0]
        if gauge <= 0 or any(value / gauge <= 0 for value in normalized[column]):
            raise AssertionError("moving column left the positive projective chart")
        answer.extend(normalized[column][row] / gauge for row in (1, 2, 3))
    return tuple(answer)


def parent_polynomials(record):
    matrix = global_factors.normalized_matrix()
    sample = normalized_values(record["matrix"])
    answer = []
    target_bits = []
    for basis in combinations(range(8), 4):
        polynomial = global_factors.primitive(
            global_factors.square_minor(matrix, basis)
        )
        target = sign(evaluator.evaluate(polynomial, sample))
        label = "".join(str(index + 1) for index in basis)
        multidegree = tuple(
            max(
                sum(monomial[index] for index in variables)
                for monomial in polynomial
            )
            for variables in bernstein.GROUPS
        )
        terms = tuple(
            (
                bernstein.term_support(monomial, multidegree),
                sign(coefficient) * target,
            )
            for monomial, coefficient in polynomial.items()
        )
        answer.append((label, target, polynomial, terms))
        target_bits.append(int(target > 0))
    digest = hashlib.sha256(
        b"diag3-row2599-normalized-parent-signs-v1\0" + bytes(target_bits)
    ).hexdigest()
    if digest != EXPECTED_TARGET_DIGEST:
        raise AssertionError("normalized parent-sign digest changed")
    return tuple(answer), digest


def verify_parent_sources(record, parents):
    expected_raw = tuple(1 if character == "+" else -1 for character in record["chi"])
    if topes.parent_signs(record["matrix"]) != expected_raw:
        raise AssertionError("catalog matrix no longer realizes parent 2599")
    expected = tuple(target for _label, target, _polynomial, _terms in parents)
    with np.load(POINT_BANK, allow_pickle=False) as source:
        matrices = np.asarray(source["chart_matrix"], dtype=np.int64)
    if matrices.shape != (178, 4, 8):
        raise AssertionError("row-2599 point-bank shape changed")
    for matrix in matrices:
        values = normalized_values(matrix.tolist())
        actual = tuple(
            sign(evaluator.evaluate(polynomial, values))
            for _label, _target, polynomial, _terms in parents
        )
        if actual != expected:
            raise AssertionError("stored row-2599 sample left the normalized parent cell")
    return len(matrices)


def restriction_state(terms, face):
    signs = {
        coefficient_sign
        for support, coefficient_sign in terms
        if all(mask & ~allowed == 0 for mask, allowed in zip(support, face, strict=True))
    }
    if not signs:
        return ZERO
    if signs == {1}:
        return RIGHT
    if signs == {-1}:
        return WRONG
    if signs == {1, -1}:
        return MIXED
    raise AssertionError("invalid Bernstein sign state")


def default_witness(face):
    answer = []
    for support in face:
        answer.extend(
            Fraction(1, 2) if support & (1 << row) else Fraction(0)
            for row in (1, 2, 3)
        )
    return tuple(answer)


def verify_witness(face, values, parents):
    if len(values) != 9:
        raise AssertionError("wrong parent-face witness dimension")
    for block, support in enumerate(face):
        for row in (1, 2, 3):
            value = values[3 * block + row - 1]
            if (value > 0) != bool(support & (1 << row)):
                raise AssertionError("witness has the wrong homogeneous support")
    evaluations = tuple(
        target * evaluator.evaluate(polynomial, values)
        for _label, target, polynomial, _terms in parents
    )
    if any(value < 0 for value in evaluations):
        raise AssertionError("claimed parent-face witness has a wrong bracket sign")
    return sum(value == 0 for value in evaluations)


def parse_candidates():
    raw = CANDIDATES.read_bytes()
    header = struct.calcsize("<8sIII")
    magic, parent, factor_count, candidate_count = struct.unpack_from("<8sIII", raw)
    if (
        magic != ranking.CANDIDATE_MAGIC
        or parent != PARENT
        or factor_count != 26_740
        or candidate_count != 17_824
    ):
        raise AssertionError("candidate artifact header changed")
    answer = tuple(map(int, np.frombuffer(raw, dtype="<u4", offset=header)))
    if answer != tuple(sorted(set(answer))):
        raise AssertionError("candidate IDs are not canonical")
    return answer


def residual_counts(face_order):
    candidate_ids = parse_candidates()
    _occurrences, _occurrence_factor, polynomials = labeled.factor_polynomials()
    counts = {}
    for face in face_order:
        state = [0, 0, 0]
        for factor_id in candidate_ids:
            polynomial = polynomials[factor_id]
            multidegree = tuple(
                max(
                    sum(monomial[index] for index in variables)
                    for monomial in polynomial
                )
                for variables in bernstein.GROUPS
            )
            signs = {
                sign(coefficient)
                for monomial, coefficient in polynomial.items()
                if all(
                    mask & ~allowed == 0
                    for mask, allowed in zip(
                        bernstein.term_support(monomial, multidegree),
                        face,
                        strict=True,
                    )
                )
            }
            index = 0 if not signs else (1 if len(signs) == 1 else 2)
            state[index] += 1
        counts[face] = tuple(state)
    return counts


def verify_support_one_skeleton(nonexcluded, parents, residual):
    vertices = [row for row in nonexcluded if row["dimension"] == 0]
    edges = [row for row in nonexcluded if row["dimension"] == 1]
    if [row["support"] for row in vertices] != [[1, 1, 1]]:
        raise AssertionError("support vertex census changed")
    if [row["support"] for row in edges] != [[1, 1, 5], [3, 1, 1]]:
        raise AssertionError("support edge census changed")

    expected = {
        (1, 1, 5): ("2458", 7),
        (3, 1, 1): ("3456", 0),
    }
    for row in edges:
        face = tuple(row["support"])
        label, variable = expected[face]
        mixed = []
        for parent_label, _target, polynomial, terms in parents:
            if restriction_state(terms, face) == MIXED:
                restricted = Counter()
                for monomial, coefficient in polynomial.items():
                    support = bernstein.term_support(
                        monomial,
                        tuple(
                            max(
                                sum(term[index] for index in variables)
                                for term in polynomial
                            )
                            for variables in bernstein.GROUPS
                        ),
                    )
                    if all(
                        mask & ~allowed == 0
                        for mask, allowed in zip(support, face, strict=True)
                    ):
                        exponent = monomial[variable]
                        restricted[exponent] += coefficient
                target = next(t for l, t, _p, _q in parents if l == parent_label)
                restricted = Counter(
                    {degree: target * value for degree, value in restricted.items() if value}
                )
                mixed.append((parent_label, dict(restricted)))
        if mixed != [(label, {0: 1, 1: -1})]:
            raise AssertionError(f"support edge equation changed: {face}: {mixed}")
        if residual[face][2] != 0:
            raise AssertionError("a support edge acquired an active residual wall")
    return {"vertices": 3, "edges": 2, "edge_parameter_interval": "[0,1]"}


def monomial(a=0, h=0):
    answer = [0] * 9
    answer[0] = a
    answer[7] = h
    return tuple(answer)


def verify_support_two_face(parents):
    face = (3, 1, 5)
    parent_mixed = []
    for label, target, polynomial, terms in parents:
        if restriction_state(terms, face) != MIXED:
            continue
        restricted = {}
        multidegree = tuple(
            max(
                sum(term[index] for index in variables)
                for term in polynomial
            )
            for variables in bernstein.GROUPS
        )
        for exponent, coefficient in polynomial.items():
            support = bernstein.term_support(exponent, multidegree)
            if all(
                mask & ~allowed == 0
                for mask, allowed in zip(support, face, strict=True)
            ):
                restricted[exponent] = target * coefficient
        parent_mixed.append((label, restricted))
    expected_parent = [
        ("2458", {monomial(h=1): -1, monomial(): 1}),
        ("3456", {monomial(a=1): -1, monomial(): 1}),
        (
            "4568",
            {
                monomial(a=1, h=1): -1,
                monomial(h=1): 1,
                monomial(a=1): 1,
            },
        ),
    ]
    if parent_mixed != expected_parent:
        raise AssertionError(f"two-face parent equations changed: {parent_mixed}")

    candidate_ids = parse_candidates()
    _occurrences, _occurrence_factor, polynomials = labeled.factor_polynomials()
    anchors = {
        tuple(
            sorted(
                global_factors.primitive(
                    {monomial(a=1): 1, monomial(h=1): -1}
                ).items()
            )
        ): "a=h",
        tuple(
            sorted(
                global_factors.primitive(
                    {monomial(a=1): 1, monomial(): -1}
                ).items()
            )
        ): "a=1",
        tuple(
            sorted(
                global_factors.primitive(
                    {monomial(h=1): 1, monomial(): -1}
                ).items()
            )
        ): "h=1",
        tuple(
            sorted(
                global_factors.primitive(
                    {
                        monomial(a=1, h=1): 1,
                        monomial(a=1): -1,
                        monomial(h=1): -1,
                    }
                ).items()
            )
        ): "origin-only",
    }
    factor_counts = Counter()
    polynomial_counts = Counter()
    monomial_multipliers = {}
    mixed_factors = 0
    for factor_id in candidate_ids:
        polynomial = polynomials[factor_id]
        multidegree = tuple(
            max(
                sum(term[index] for index in variables)
                for term in polynomial
            )
            for variables in bernstein.GROUPS
        )
        restricted = {
            exponent: coefficient
            for exponent, coefficient in polynomial.items()
            if all(
                mask & ~allowed == 0
                for mask, allowed in zip(
                    bernstein.term_support(exponent, multidegree),
                    face,
                    strict=True,
                )
            )
        }
        if len({sign(value) for value in restricted.values()}) < 2:
            continue
        mixed_factors += 1
        primitive = global_factors.primitive(restricted)
        minimum_a = min(exponent[0] for exponent in primitive)
        minimum_h = min(exponent[7] for exponent in primitive)
        reduced = {
            tuple(
                value - (minimum_a if index == 0 else minimum_h if index == 7 else 0)
                for index, value in enumerate(exponent)
            ): coefficient
            for exponent, coefficient in primitive.items()
        }
        anchor = anchors.get(tuple(sorted(global_factors.primitive(reduced).items())))
        if anchor is None:
            raise AssertionError("two-face residual restriction gained a new wall curve")
        factor_counts[anchor] += 1
        multipliers = monomial_multipliers.setdefault(anchor, set())
        polynomial_counts[anchor] += int((minimum_a, minimum_h) not in multipliers)
        multipliers.add((minimum_a, minimum_h))
    expected_counts = {"a=1": 113, "a=h": 53, "h=1": 113, "origin-only": 56}
    if mixed_factors != 335 or dict(sorted(factor_counts.items())) != expected_counts:
        raise AssertionError("two-face residual wall multiplicities changed")
    if any(value != 4 for value in polynomial_counts.values()):
        raise AssertionError("two-face monomial-multiple compression changed")
    return {
        "support": [3, 1, 5],
        "parent_domain": "0<=a<=1, 0<=h<=1",
        "parent_mixed_equations": ["1-h", "1-a", "a+h-a*h"],
        "mixed_residual_factor_count": mixed_factors,
        "unique_restricted_polynomial_count": sum(polynomial_counts.values()),
        "wall_class_factor_counts": expected_counts,
        "regular_diagonal_cellulation": {"vertices": 4, "edges": 5, "faces": 2},
    }


def canonical_manifest_digest(payload):
    semantic = dict(payload)
    expected = semantic.pop("semantic_sha256")
    actual = hashlib.sha256(
        json.dumps(semantic, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()
    if expected != actual or actual != EXPECTED_SEMANTIC:
        raise AssertionError("parent-face manifest semantic digest changed")
    return actual


def audit():
    for path, expected in (
        (CATALOG, CATALOG_SHA256),
        (POINT_BANK, POINT_BANK_SHA256),
        (FACTOR_CENSUS, FACTOR_CENSUS_SHA256),
        (CANDIDATES, CANDIDATE_SHA256),
    ):
        if sha256(path) != expected:
            raise AssertionError(f"pinned parent-face source changed: {path.name}")
    records = [
        json.loads(line)
        for line in CATALOG.read_text(encoding="utf-8").splitlines()
        if line
    ]
    if len(records) != 2_628 or records[PARENT]["verdict"] != "REALIZABLE":
        raise AssertionError("parent-2599 catalog record changed")
    parents, target_digest = parent_polynomials(records[PARENT])
    samples = verify_parent_sources(records[PARENT], parents)

    face_order = bernstein.faces()
    state_totals = Counter()
    classification_totals = Counter()
    dimension_histogram = {str(dimension): Counter() for dimension in range(10)}
    witness_histogram = Counter()
    stream = hashlib.sha256(b"diag3-row2599-parent-face-feasibility-v1\0")
    nonexcluded = []
    for face in face_order:
        states = tuple(restriction_state(terms, face) for _l, _t, _p, terms in parents)
        state_totals.update(states)
        wrong = [index for index, state in enumerate(states) if state == WRONG]
        classification = "excluded" if wrong else (
            "ambiguous" if MIXED in states else "contained"
        )
        classification_totals[classification] += 1
        dimension = bernstein.face_dimension(face)
        dimension_histogram[str(dimension)][classification] += 1
        witness_index = wrong[0] if wrong else 255
        if wrong:
            witness_histogram[parents[witness_index][0]] += 1
        stream.update(bytes(face))
        stream.update(
            bytes(
                [
                    {"excluded": 0, "ambiguous": 1, "contained": 2}[classification],
                    witness_index,
                ]
            )
        )
        packed = bytearray((len(states) + 3) // 4)
        for index, state in enumerate(states):
            packed[index // 4] |= state << (2 * (index % 4))
        stream.update(packed)
        if not wrong:
            values = SPECIAL_WITNESS if face == (15, 7, 15) else default_witness(face)
            zero_count = verify_witness(face, values, parents)
            nonexcluded.append(
                {
                    "support": list(face),
                    "dimension": dimension,
                    "classification": classification,
                    "witness": [str(value) for value in values],
                    "witness_zero_parent_brackets": zero_count,
                }
            )

    supports = tuple(tuple(row["support"]) for row in nonexcluded)
    residual = residual_counts(supports)
    for row in nonexcluded:
        row["residual_states"] = list(residual[tuple(row["support"])])
    skeleton = verify_support_one_skeleton(nonexcluded, parents, residual)
    two_face = verify_support_two_face(parents)
    mixed = sum(value[2] for value in residual.values())

    return {
        "stored_parent_samples": samples,
        "normalized_parent_sign_sha256": target_digest,
        "parent_bracket_face_state_counts": {
            "zero": state_totals[ZERO],
            "right": state_totals[RIGHT],
            "wrong": state_totals[WRONG],
            "mixed": state_totals[MIXED],
        },
        "support_face_classification_counts": dict(classification_totals),
        "dimension_histogram": {
            dimension: dict(counts) for dimension, counts in dimension_histogram.items()
        },
        "canonical_exclusion_witness_histogram": dict(sorted(witness_histogram.items())),
        "parent_face_state_stream_sha256": stream.hexdigest(),
        "nonexcluded_support_faces": nonexcluded,
        "nonexcluded_support_face_count": len(nonexcluded),
        "excluded_support_face_count": classification_totals["excluded"],
        "excluded_candidate_factor_face_pair_count": classification_totals["excluded"] * 17_824,
        "remaining_candidate_factor_face_pair_count": len(nonexcluded) * 17_824,
        "remaining_mixed_residual_restriction_count": mixed,
        "support_one_skeleton": skeleton,
        "support_two_face": two_face,
    }


def main():
    payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if payload.get("format") != "diag3-pair-global-row2599-parent-face-gate-v1":
        raise AssertionError("wrong parent-face manifest format")
    semantic = canonical_manifest_digest(payload)
    actual = audit()
    for key, value in actual.items():
        if payload.get(key) != value:
            raise AssertionError(
                f"parent-face manifest mismatch for {key}: "
                f"{payload.get(key)!r} != {value!r}"
            )
    print("PASS normalized parent signs on", actual["stored_parent_samples"], "samples")
    print(
        "FACES",
        actual["excluded_support_face_count"],
        "excluded;",
        actual["nonexcluded_support_face_count"],
        "exactly witnessed nonempty",
    )
    print(
        "TASKS",
        actual["excluded_candidate_factor_face_pair_count"],
        "factor-face pairs removed;",
        actual["remaining_mixed_residual_restriction_count"],
        "mixed remain",
    )
    print("PASS support one-skeleton: 3 vertices, 2 edges, no active residual wall")
    print("PASS support two-face: square split by a=h; 4 vertices, 5 edges, 2 faces")
    print("PARENT_FACE_SHA256", actual["parent_face_state_stream_sha256"])
    print("SEMANTIC_SHA256", semantic)
    print("SCOPE support-face gate only; internal full-chart master cells remain open")


if __name__ == "__main__":
    main()
