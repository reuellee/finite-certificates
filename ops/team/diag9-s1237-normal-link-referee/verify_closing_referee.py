#!/usr/bin/env python3
"""Independent frozen-head referee for the D9 S12,37 normal-link cycle.

The checker does not import any producer, falsifier, or certificate acceptance
module.  It rebuilds the orientation census from transported circuit inputs,
checks the producer's all-occurrence metadata, derives the four decisive
parent initial forms, and replays the factor-8552 recursive-facet wall with
exact rational arithmetic.  Its acceptance is only the local finite-exact
NORMAL_LINK_REDUCTION_NO_GO endpoint; it proves no collar or D9 theorem.
"""

from __future__ import annotations

from collections import Counter, defaultdict
import contextlib
from copy import deepcopy
from fractions import Fraction
import hashlib
from io import StringIO
import itertools
import json
from math import gcd
from pathlib import Path
import subprocess
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OM = ROOT / "ai" / "omreal"
DATA = OM / "data"

FROZEN_HEAD = "5efbd07a25b818306f9fd22597fd81a0f2091309"
FROZEN_TREE = "b8cb35941043ff40be06cba98461ddab0ba14c8f"
FROZEN_PARENT = "c6bd7a6afeda0888fc950710b941cac6f6c9bf95"
OPENING_TREE = "9c2dbe39a3ea0f36e9e9c8f845e6f72e98526421"
TARGET = "D9_S1237_4SUPPORT_NORMAL_LINK_GATE1"
ENDPOINT = "NORMAL_LINK_REDUCTION_NO_GO"

PROVER = ROOT / "ops/team/diag9-s1237-normal-link-prover"
FALSIFIER = ROOT / "ops/team/diag9-s1237-normal-link-falsifier"
CERTIFICATE = ROOT / "ops/team/diag9-s1237-normal-link-certificate"
SOURCE_MANIFEST = HERE / "SOURCE_MANIFEST.json"
CLOSING_MANIFEST = HERE / "CLOSING_MANIFEST.json"
HOSTILE_TESTS = HERE / "HOSTILE_TESTS.json"
ADAPTER = HERE / "REFEREE_ADAPTER.json"
RESULT = HERE / "RESULT.json"

EXPECTED_PRODUCER_LITERAL_DIGEST = "e733196b9b9ba25cf9256c0d51ba0f5d2cd8d4da4a4c05eccd9d609c1ece20e7"
EXPECTED_PRODUCER_NORMAL_DIGEST = "3f891c6421e418758b11371d82522e5cdf789b6c944d1342773478df493445f6"
EXPECTED_PRODUCER_RESULT_DIGEST = "f2169e2bc90f9c92d49f754d695b34b9dc3da770a3aecf6bfb6e84a6cb80b747"
EXPECTED_FALSIFIER_RESULT_DIGEST = "95631d5d6192e9ff86ab04a3bb065e849a4b592be24a752c1cade41d669cf666"
EXPECTED_CERTIFICATE_CENSUS_DIGEST = "a1b9d3d9da1e01df83621dc8f1c7959f86ae2e0d9bd3bc457124c561cbac245a"
EXPECTED_ACTIVE_SECTOR_DIGEST = "6de7ff2716b65853c04b9a08f44eb98ad8966e1f3525887ffafde0a3b805c154"
EXPECTED_PARENT_TARGET_DIGEST = "1d9b940e2bb954b5c69bcee8b2346f9554b2e15589ea4c5b3c3f8e1e943de701"

SUPPORTS = ((3, 1, 15), (3, 3, 7))
TANGENT = (Fraction(3, 4), Fraction(1, 4), Fraction(1, 2))
WALL_BASE = (
    Fraction(3, 4), Fraction(0), Fraction(0), Fraction(0), Fraction(0),
    Fraction(0), Fraction(1, 4), Fraction(2, 3), Fraction(1, 4),
)
NORMAL_AXES = (1, 2, 3, 4, 5, 8)
RADIUS = Fraction(1, 100)
RAYS = {
    "minus": tuple(Fraction(value, 55) for value in (13, 11, 19, 12, 0, -14)),
    "wall": (
        Fraction(51, 247), Fraction(32, 247), Fraction(656, 1235),
        Fraction(164, 1235), Fraction(0), Fraction(-491, 1235),
    ),
    "plus": tuple(Fraction(value, 35) for value in (7, 4, 20, 4, 0, -15)),
}


class RefereeError(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RefereeError(message)


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def object_digest(domain: bytes, value: dict, field: str = "semantic_sha256") -> str:
    payload = deepcopy(value)
    payload.pop(field, None)
    return sha256_bytes(domain + b"\0" + canonical(payload))


def stream_digest(domain: bytes, values: list[dict]) -> str:
    digest = hashlib.sha256(domain + b"\0")
    for value in values:
        digest.update(canonical(value))
        digest.update(b"\n")
    return digest.hexdigest()


def git(*arguments: str) -> str:
    return subprocess.check_output(["git", *arguments], cwd=ROOT, text=True).strip()


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sign(value: int | Fraction) -> int:
    require(value != 0, "unexpected zero sign")
    return 1 if value > 0 else -1


def fraction_text(value: Fraction | int) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def determinant4(matrix) -> int:
    total = 0
    for permutation in itertools.permutations(range(4)):
        inversions = sum(
            permutation[left] > permutation[right]
            for left in range(4) for right in range(left + 1, 4)
        )
        product = 1
        for row, column in enumerate(permutation):
            product *= int(matrix[row][column])
        total += (-1 if inversions & 1 else 1) * product
    return total


def det_rows(rows, identifiers) -> int:
    return determinant4(tuple(rows[index] for index in identifiers))


def orient_certificate(occurrence, certificate, rows):
    raw = det_rows(rows, occurrence)
    require(raw != 0, "orientation anchor lies on residual wall")
    if certificate[0] == "ordinary":
        circuit, auxiliary = certificate[1], certificate[2]
        columns = circuit + (auxiliary,)
        coefficients = tuple(
            (-1) ** omitted * det_rows(rows, columns[:omitted] + columns[omitted + 1:])
            for omitted in range(4)
        )
        require(all(coefficients), "ordinary localization coefficient vanished")
        order = sign(det_rows(rows, circuit)) * sign(raw)
        data = (circuit, tuple(map(sign, coefficients)), auxiliary, order)
    else:
        circuit, residual, structural = certificate[1:4]
        columns = circuit + (residual, structural)
        coefficients = tuple(
            (-1) ** omitted * det_rows(rows, columns[:omitted] + columns[omitted + 1:])
            for omitted in range(5)
        )
        require(all(coefficients[index] for index in range(3)), "localized coefficient vanished")
        require(coefficients[3] == 0 and coefficients[4] != 0, "localization zero pattern")
        order = sign(det_rows(rows, circuit + (residual,))) * sign(raw)
        data = (
            circuit,
            tuple(sign(coefficients[index]) for index in range(3)),
            structural,
            order,
        )
    return data, sign(raw)


def normalized_pattern(data):
    circuit, coefficients = data[:2]
    ordered = tuple(value for _, value in sorted(zip(circuit, coefficients, strict=True)))
    if ordered[0] < 0:
        ordered = tuple(-value for value in ordered)
    return tuple(sorted(circuit)), ordered


def allowed_raw(signature: int, data) -> int | None:
    circuit, coefficients, auxiliary, order = data
    values = tuple(
        coefficient * (1 if (signature >> row) & 1 else -1)
        for coefficient, row in zip(coefficients, circuit, strict=True)
    )
    if len(set(values)) != 1:
        return None
    auxiliary_sign = 1 if (signature >> auxiliary) & 1 else -1
    return -values[0] * auxiliary_sign * order


def validate_source_manifest() -> dict:
    manifest = load_json(SOURCE_MANIFEST)
    require(manifest["format"] == "diag9-s1237-normal-link-referee-source-manifest-v1", "source manifest format")
    require(manifest["frozen_head"] == FROZEN_HEAD and manifest["frozen_tree"] == FROZEN_TREE, "source manifest frozen binding")
    require(manifest["frozen_parent"] == FROZEN_PARENT, "source manifest parent binding")
    sources = manifest["sources"]
    require(isinstance(sources, dict) and len(sources) >= 25, "source manifest incomplete")
    for relative, expected in sources.items():
        path = (ROOT / relative).resolve()
        require(path.is_relative_to(ROOT), f"source path escape: {relative}")
        require(path.is_file() and sha256(path) == expected, f"source drift: {relative}")
    require(
        manifest["semantic_sha256"]
        == object_digest(b"d9-s1237-normal-link-referee-sources-v1", manifest),
        "source manifest semantic digest",
    )
    return manifest


def validate_revision_and_authority() -> None:
    require(git("rev-parse", f"{FROZEN_HEAD}^{{commit}}") == FROZEN_HEAD, "frozen head missing")
    require(git("rev-parse", f"{FROZEN_HEAD}^{{tree}}") == FROZEN_TREE, "frozen tree drift")
    require(git("rev-parse", f"{FROZEN_PARENT}^{{tree}}") == OPENING_TREE, "opening tree drift")
    require(git("rev-parse", f"{FROZEN_HEAD}^") == FROZEN_PARENT, "frozen parent drift")
    changed = git("diff", "--name-only", FROZEN_PARENT, FROZEN_HEAD).splitlines()
    allowed = (
        "ops/team/diag9-s1237-normal-link-prover/",
        "ops/team/diag9-s1237-normal-link-falsifier/",
        "ops/team/diag9-s1237-normal-link-certificate/",
    )
    require(changed and all(path.startswith(allowed) for path in changed), "frozen head unauthorized changed path")

    protocol = (ROOT / "ops/research-team/PROTOCOL.md").read_text(encoding="utf-8")
    orders = (ROOT / "ops/research-team/cycles/2026-09-01-diag9-s1237-normal-link/WORK_ORDERS.yaml").read_text(encoding="utf-8")
    protocol_words = " ".join(protocol.replace(">", " ").split())
    order_words = " ".join(orders.replace(">", " ").split())
    required = (
        "ChatGPT Library as the canonical durable working branch",
        "Projects/research-backups",
        "GitHub is read-only",
        "Local scratch is ephemeral and is not an authority",
        "do not push commits",
        "trigger or rerun CI",
    )
    for phrase in required:
        require(phrase in protocol_words and phrase in order_words, f"authority phrase missing: {phrase}")
    completed = subprocess.run(
        [sys.executable, "ops/research-team/verify_cycle_protocol.py"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    require("PASS research-cycle" in completed.stdout, "protocol replay failed")
    opened = subprocess.run(
        [sys.executable, "ops/research-team/cycles/2026-09-01-diag9-s1237-normal-link/verify_opening_audit.py"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    require("3539 active literals" in opened.stdout and TARGET in opened.stdout, "opening audit replay failed")


def rebuild_census() -> dict:
    sys.path.insert(0, str(OM))
    with contextlib.redirect_stdout(StringIO()):
        import verify_diag9_active_sector as active
    import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled
    import verify_diag2_canonical_robust_edges as evaluator
    import verify_diag3_pair_global_parent_face_gate as parent_gate

    active.verify_pins()
    certificates = active.transported_certificates()
    with np.load(DATA / "DIAG9_GRAPH_global_factor_census.npz", allow_pickle=False) as source:
        require(str(source["format"].item()) == "diag9-global-residual-factor-census-v1", "factor census format")
        fourset_array = np.asarray(source["occurrence_fourset"], dtype=np.uint8)
        occurrence_factor = np.asarray(source["occurrence_factor"], dtype=np.uint32)
        factor_multiplicity = np.asarray(source["factor_multiplicity"], dtype=np.uint32)
        factor_offsets = np.asarray(source["factor_offset"], dtype=np.uint32)
        factor_exponents = np.asarray(source["factor_exponent"], dtype=np.uint8)
        factor_coefficients = np.asarray(source["factor_coefficient"], dtype=np.int64)
        unit_offsets = np.asarray(source["occurrence_unit_offset"], dtype=np.uint32)
        unit_indices = np.asarray(source["occurrence_unit_index"], dtype=np.uint8)
        parent_labels_array = np.asarray(source["parent_bracket_label"], dtype=np.uint8)
    foursets = tuple(tuple(map(int, row)) for row in fourset_array)
    require(fourset_array.shape == (84_840, 4) and set(foursets) == set(certificates), "occurrence source census")
    with np.load(DATA / "seeat_parent2599_upper178.npz", allow_pickle=False) as source:
        charts = np.asarray(source["chart_matrix"], dtype=np.int64)
    rows = active.topes.derived_rows(charts[0])

    oriented = []
    conflicting = set()
    for occurrence_index, occurrence in enumerate(foursets):
        alternatives = tuple(
            orient_certificate(occurrence, certificate, rows)
            for certificate in certificates[occurrence]
        )
        require(len({raw for _data, raw in alternatives}) == 1, "raw occurrence sign conflict")
        if len({normalized_pattern(data) for data, _raw in alternatives}) > 1:
            conflicting.add(occurrence_index)
        oriented.append(alternatives[0])
    empty_factors = {int(occurrence_factor[index]) for index in conflicting}
    require(len(conflicting) == 27_944 and len(empty_factors) == 8_916, "empty-factor replay")

    factor_count = len(factor_multiplicity)
    representatives = [-1] * factor_count
    occurrences_by_factor = [[] for _ in range(factor_count)]
    for occurrence_index, factor in enumerate(map(int, occurrence_factor)):
        occurrences_by_factor[factor].append(occurrence_index)
        if representatives[factor] < 0:
            representatives[factor] = occurrence_index
    require(all(index >= 0 for index in representatives), "factor without representative")
    representative_raw = [oriented[index][1] for index in representatives]
    with np.load(DATA / "ninth_candidate_12_37_antichain.npz", allow_pickle=False) as source:
        signatures = tuple(map(int, source["signature"]))
    require(len(signatures) == 9, "signature family drift")

    family = {}
    signature_incidence = defaultdict(list)
    occurrence_signature_incidence = defaultdict(list)
    per_occurrence_sides = [[] for _ in foursets]
    aligned_occurrence_union = set()
    for signature_index, signature in enumerate(signatures):
        per_signature = {}
        for occurrence_index, ((data, raw), factor) in enumerate(
            zip(oriented, map(int, occurrence_factor), strict=True)
        ):
            if factor in empty_factors:
                continue
            permitted_raw = allowed_raw(signature, data)
            if permitted_raw is None:
                continue
            aligned_occurrence_union.add(occurrence_index)
            permitted_representative = permitted_raw * raw * representative_raw[factor]
            previous = per_signature.setdefault(factor, permitted_representative)
            require(previous == permitted_representative, "within-signature orientation conflict")
            occurrence_signature_incidence[(factor, occurrence_index)].append(signature_index)
            per_occurrence_sides[occurrence_index].append(
                (signature_index, permitted_raw, permitted_representative)
            )
        for factor, orientation in per_signature.items():
            previous = family.setdefault(factor, orientation)
            require(previous == orientation, "family orientation conflict")
            signature_incidence[factor].append(signature_index)
    require(len(family) == 3_539 and len(aligned_occurrence_union) == 5_026, "active census counts")
    require({int(occurrence_factor[index]) for index in aligned_occurrence_union} == set(family), "aligned occurrence class mismatch")

    _occurrences, _occurrence_map, factor_polynomials = labeled.factor_polynomials()
    anchor_values = parent_gate.normalized_values(charts[0].tolist())
    primitive_anchor_sign = {
        factor: sign(evaluator.evaluate(factor_polynomials[factor], anchor_values))
        for factor in family
    }
    catalog = [json.loads(line) for line in parent_gate.CATALOG.read_text().splitlines() if line]
    parents, parent_target_digest = parent_gate.parent_polynomials(catalog[parent_gate.PARENT])
    require(len(parents) == 70 and parent_target_digest == EXPECTED_PARENT_TARGET_DIGEST, "parent source replay")
    parent_sign = {label: target for label, target, _polynomial, _terms in parents}
    parent_label_text = tuple("".join(str(int(value) + 1) for value in row) for row in parent_labels_array)
    require(len(parent_label_text) == 62 and len(set(parent_label_text)) == 62, "unit bracket label census")

    producer = load_json(PROVER / "ACTIVE_LITERAL_INVENTORY.json")
    require(producer["factor_count"] == 3_539 and producer["occurrence_count"] == 6_167, "producer census header")
    stored_by_factor = {row["factor_id"]: row for row in producer["literal_rows"]}
    require(list(stored_by_factor) == sorted(family) and len(stored_by_factor) == 3_539, "producer factor rows")
    multiplicity = Counter()
    all_occurrence_count = 0
    for factor in sorted(family):
        row = stored_by_factor[factor]
        representative = representatives[factor]
        q_sign = primitive_anchor_sign[factor]
        expected_allowed_primitive = family[factor] * representative_raw[factor] * q_sign
        require(row["allowed_representative_sign"] == family[factor], f"factor {factor}: representative orientation")
        require(row["representative_occurrence_index"] == representative, f"factor {factor}: representative index")
        require(row["representative_fourset"] == list(foursets[representative]), f"factor {factor}: representative fourset")
        require(row["representative_raw_sign_at_anchor"] == representative_raw[factor], f"factor {factor}: representative raw sign")
        require(row["primitive_sign_at_anchor"] == q_sign, f"factor {factor}: primitive anchor sign")
        require(row["allowed_primitive_sign"] == expected_allowed_primitive, f"factor {factor}: primitive orientation")
        require(row["active_signature_indices"] == signature_incidence[factor], f"factor {factor}: signature incidence")
        expected_occurrences = occurrences_by_factor[factor]
        require([value["occurrence_index"] for value in row["occurrences"]] == expected_occurrences, f"factor {factor}: occurrence omission")
        multiplicity[len(expected_occurrences)] += 1
        all_occurrence_count += len(expected_occurrences)
        for stored, occurrence_index in zip(row["occurrences"], expected_occurrences, strict=True):
            start, stop = int(unit_offsets[occurrence_index]), int(unit_offsets[occurrence_index + 1])
            indices = list(map(int, unit_indices[start:stop]))
            require(len(indices) <= 1, "multiple stripped units")
            unit_label = parent_label_text[indices[0]] if indices else None
            unit_sign = parent_sign[unit_label] if unit_label is not None else 1
            raw_to_primitive = oriented[occurrence_index][1] * q_sign
            expected = {
                "occurrence_index": occurrence_index,
                "fourset": list(foursets[occurrence_index]),
                "raw_to_primitive_sign": raw_to_primitive,
                "unit_bracket_label": unit_label,
                "unit_sign_in_parent": unit_sign,
                "constant_scalar_sign": raw_to_primitive * unit_sign,
                "active_signature_indices": occurrence_signature_incidence[(factor, occurrence_index)],
            }
            require(stored == expected, f"factor {factor}: occurrence metadata {occurrence_index}")
    require(all_occurrence_count == 6_167, "all-occurrence active-factor count")
    require(multiplicity == Counter({1: 3453, 2: 2, 15: 55, 65: 29}), "multiplicity census")
    producer_core = {key: producer[key] for key in (
        "family", "parent_index", "signatures", "factor_count", "occurrence_count",
        "multiplicity_census", "literal_rows",
    )}
    require(
        producer["semantic_sha256"]
        == sha256_bytes(b"diag9-s1237-oriented-active-literals-v1\0" + canonical(producer_core))
        == EXPECTED_PRODUCER_LITERAL_DIGEST,
        "producer literal semantic digest",
    )

    certificate_records = []
    for factor in sorted(family):
        start, stop = int(factor_offsets[factor]), int(factor_offsets[factor + 1])
        polynomial = [
            {"exponent": list(map(int, factor_exponents[index])), "coefficient": int(factor_coefficients[index])}
            for index in range(start, stop)
        ]
        polynomial.sort(key=lambda term: term["exponent"])
        representative = representatives[factor]
        occurrences = []
        for occurrence_index in occurrences_by_factor[factor]:
            start, stop = int(unit_offsets[occurrence_index]), int(unit_offsets[occurrence_index + 1])
            indices = list(map(int, unit_indices[start:stop]))
            raw = oriented[occurrence_index][1]
            occurrences.append({
                "occurrence_index": occurrence_index,
                "fourset": list(foursets[occurrence_index]),
                "raw_sign_at_chart0": raw,
                "unit_bracket_indices": indices,
                "unit_bracket_labels": [list(map(int, parent_labels_array[index])) for index in indices],
                "unit_sign_to_representative": raw * representative_raw[factor],
                "aligned_family_sides": [
                    {
                        "signature_index": signature_index,
                        "allowed_raw_sign": permitted_raw,
                        "allowed_representative_sign": permitted_representative,
                    }
                    for signature_index, permitted_raw, permitted_representative in per_occurrence_sides[occurrence_index]
                ],
            })
        certificate_records.append({
            "factor_id": factor,
            "allowed_representative_sign": family[factor],
            "active_signature_indices": signature_incidence[factor],
            "primitive_factor": polynomial,
            "representative": {
                "occurrence_index": representative,
                "fourset": list(foursets[representative]),
                "raw_sign_at_chart0": representative_raw[factor],
            },
            "occurrences": occurrences,
        })
    certificate_digest = stream_digest(b"9dvl-d9-s1237-literal-census-v1", certificate_records)
    require(certificate_digest == EXPECTED_CERTIFICATE_CENSUS_DIGEST, "certificate census semantic digest")
    factor_8552 = next(row for row in certificate_records if row["factor_id"] == 8_552)
    require(family[8_552] == -1 and [row["occurrence_index"] for row in factor_8552["occurrences"]] == [24_140], "factor 8552 orientation/occurrence")
    require(factor_8552["primitive_factor"] == [
        {"exponent": [0, 0, 0, 0, 1, 0, 0, 0, 0], "coefficient": -1},
        {"exponent": [0, 0, 0, 1, 0, 0, 0, 0, 1], "coefficient": 1},
    ], "factor 8552 polynomial")
    compact = [
        {
            "factor_id": factor,
            "orientation": family[factor],
            "occurrences": occurrences_by_factor[factor],
            "aligned_occurrences": [index for index in occurrences_by_factor[factor] if per_occurrence_sides[index]],
        }
        for factor in sorted(family)
    ]
    return {
        "active_factor_count": len(family),
        "all_occurrence_count": all_occurrence_count,
        "aligned_occurrence_count": len(aligned_occurrence_union),
        "empty_factor_count": len(empty_factors),
        "producer_literal_semantic_sha256": producer["semantic_sha256"],
        "certificate_census_semantic_sha256": certificate_digest,
        "referee_census_semantic_sha256": stream_digest(b"d9-s1237-referee-census-v1", compact),
        "family": family,
        "factor_polynomials": factor_polynomials,
        "parents": parents,
    }


def evaluate(polynomial, point) -> Fraction:
    total = Fraction(0)
    for exponent, coefficient in polynomial.items():
        value = Fraction(coefficient)
        for axis, power in enumerate(exponent):
            value *= point[axis] ** power
        total += value
    return total


def derivative_at(polynomial, point, axis: int) -> Fraction:
    total = Fraction(0)
    for exponent, coefficient in polynomial.items():
        power = exponent[axis]
        if not power:
            continue
        value = Fraction(coefficient) * power
        for index, other_power in enumerate(exponent):
            value *= point[index] ** (other_power - (1 if index == axis else 0))
        total += value
    return total


def parent_linear_form(polynomial, target: int, support) -> tuple[Fraction, ...]:
    a, g, h = TANGENT
    if support == (3, 1, 15):
        point = (a, 0, 0, 0, 0, 0, g, h, g)
        ambient_axes = (1, 2, 3, 4, 5, 8)
    else:
        point = (a, 0, 0, g, 0, 0, g, h, 0)
        ambient_axes = (1, 2, 4, 5, 8, 3)
    require(target * evaluate(polynomial, point) == 0, "load-bearing parent does not vanish")
    raw = tuple(target * derivative_at(polynomial, point, axis) for axis in ambient_axes)
    denominator = 1
    for value in raw:
        denominator = denominator * value.denominator // gcd(denominator, value.denominator)
    integers = tuple(int(value * denominator) for value in raw)
    common = 0
    for value in integers:
        common = gcd(common, abs(value))
    require(common > 0, "load-bearing parent has zero linear form")
    return tuple(Fraction(value // common) for value in integers)


def multiply_univariate(left, right):
    answer = [Fraction(0)] * (len(left) + len(right) - 1)
    for first_index, first in enumerate(left):
        for second_index, second in enumerate(right):
            answer[first_index + second_index] += first * second
    return answer


def path_coefficients(polynomial, base, ray):
    coordinate_polynomials = []
    for axis, value in enumerate(base):
        coordinate_polynomials.append([value, ray[NORMAL_AXES.index(axis)]] if axis in NORMAL_AXES else [value])
    answer = []
    for exponent, coefficient in polynomial.items():
        row = [Fraction(coefficient)]
        for axis, power in enumerate(exponent):
            for _ in range(power):
                row = multiply_univariate(row, coordinate_polynomials[axis])
        if len(answer) < len(row):
            answer += [Fraction(0)] * (len(row) - len(answer))
        for degree, value in enumerate(row):
            answer[degree] += value
    return answer


def exact_lift(name, ray):
    point = list(WALL_BASE)
    for axis, value in zip(NORMAL_AXES, ray, strict=True):
        point[axis] += RADIUS * value
    if name == "wall":
        point[4] = point[3] * point[8]
    return tuple(point)


def replay_geometry(census: dict) -> dict:
    parents = census["parents"]
    parent_by_label = {label: (target, polynomial) for label, target, polynomial, _terms in parents}
    specifications = (
        ((3, 1, 15), "1237", (0, 0, 0, 0, 1, 0), "1367", (0, 0, 0, 0, -1, 0)),
        ((3, 3, 7), "1237", (0, 0, 0, 1, 0, 0), "1278", (0, 0, 0, -1, 0, 0)),
    )
    derived = []
    for support, positive_label, positive_expected, negative_label, negative_expected in specifications:
        positive_target, positive_polynomial = parent_by_label[positive_label]
        negative_target, negative_polynomial = parent_by_label[negative_label]
        positive = parent_linear_form(positive_polynomial, positive_target, support)
        negative = parent_linear_form(negative_polynomial, negative_target, support)
        require(positive == tuple(map(Fraction, positive_expected)), f"{support} positive initial form")
        require(negative == tuple(map(Fraction, negative_expected)), f"{support} negative initial form")
        require(tuple(first + second for first, second in zip(positive, negative, strict=True)) == (Fraction(0),) * 6, f"{support} Gordan sum")
        derived.append({
            "support": list(support),
            "positive_label": positive_label,
            "positive_form": [fraction_text(value) for value in positive],
            "negative_label": negative_label,
            "negative_form": [fraction_text(value) for value in negative],
            "gordan_weights": [1, 1],
        })

    producer_normal = load_json(PROVER / "NORMAL_FORM_INVENTORY.json")
    normal_core = {key: producer_normal[key] for key in ("coordinates", "tangent_point", "supports")}
    require(
        producer_normal["semantic_sha256"]
        == sha256_bytes(b"diag9-s1237-six-normal-forms-v1\0" + canonical(normal_core))
        == EXPECTED_PRODUCER_NORMAL_DIGEST,
        "producer normal inventory semantic digest",
    )
    for specification, support_record in zip(specifications, producer_normal["supports"], strict=True):
        support, positive_label, positive_expected, negative_label, negative_expected = specification
        require(support_record["support"] == list(support), "normal inventory support order")
        require(len(support_record["factor_initial_forms"]) == 3_539, "normal inventory factor omission")
        require(len(support_record["parent_initial_forms"]) == 70, "normal inventory parent omission")
        by_label = {row["label"]: row for row in support_record["parent_initial_forms"]}
        require(len(by_label) == 70 and set(by_label) == set(parent_by_label), "normal inventory parent labels")
        for label, expected in ((positive_label, positive_expected), (negative_label, negative_expected)):
            terms = by_label[label]["tangent_point_normal_terms"]
            nonzero = [(tuple(row["exponent"]), row["coefficient"]) for row in terms]
            expected_nonzero = [(tuple(1 if value else 0 for value in expected), sign(next(value for value in expected if value)))]
            require(nonzero == expected_nonzero and by_label[label]["radial_order"] == 1, f"stored load-bearing form {support} {label}")

    producer_result = load_json(PROVER / "DIAG9_S1237_NORMAL_LINK_NO_GO.json")
    require(
        producer_result["semantic_sha256"]
        == object_digest(b"diag9-s1237-oriented-normal-link-no-go-v1", producer_result)
        == EXPECTED_PRODUCER_RESULT_DIGEST,
        "producer result semantic digest",
    )
    require(producer_result["endpoint"] == ENDPOINT, "producer endpoint")
    require(producer_result["complete_frontier_before_stop"] == {
        "active_literals": 3_539,
        "labeled_occurrences": 6_167,
        "support_factor_initial_forms": 7_078,
        "support_parent_initial_forms": 140,
        "both_supports_materialized": True,
        "resource_ceiling_crossed": False,
    }, "producer frontier scope")

    zero_on_face = []
    for label, target, polynomial, _terms in parents:
        value = target * evaluate(polynomial, WALL_BASE)
        require(value >= 0, f"wall base parent sign {label}")
        if value == 0:
            zero_on_face.append(label)
    require(len(zero_on_face) == 25, "wall base vanishing-parent count")
    q = {(0, 0, 0, 0, 1, 0, 0, 0, 0): -1, (0, 0, 0, 1, 0, 0, 0, 0, 1): 1}
    expected_q1 = {"minus": Fraction(-29, 220), "wall": Fraction(0), "plus": Fraction(1, 35)}
    expected_q = {"minus": Fraction(-40141, 30250000), "wall": Fraction(0), "plus": Fraction(8, 30625)}
    ray_records = []
    for name in ("minus", "wall", "plus"):
        ray = RAYS[name]
        require(sum(ray[:5]) == 1, f"{name}: projective normalization")
        q1 = Fraction(1, 4) * ray[2] - ray[3]
        require(q1 == expected_q1[name], f"{name}: factor 8552 initial form")
        zero_profile = []
        for label, target, polynomial, _terms in parents:
            if target * evaluate(polynomial, WALL_BASE) != 0:
                continue
            coefficients = path_coefficients(polynomial, WALL_BASE, ray)
            first = next((target * value for value in coefficients[1:] if value), None)
            if first is None:
                zero_profile.append(label)
            else:
                require(first > 0, f"{name}: parent-unsafe first order {label}")
        require(zero_profile == ["1237"], f"{name}: first-order recursive stratum")
        point = exact_lift(name, ray)
        evaluations = [(label, target * evaluate(polynomial, point)) for label, target, polynomial, _terms in parents]
        require(all(value >= 0 for _label, value in evaluations), f"{name}: lift outside weak parent closure")
        zeros = [label for label, value in evaluations if value == 0]
        require(zeros == ["1237"], f"{name}: lift changed recursive stratum")
        q_value = evaluate(q, point)
        require(q_value == expected_q[name], f"{name}: exact lifted factor value")
        evaluation_digest = sha256_bytes(
            b"d9-s1237-normal-link-parent-values-v1\0"
            + json.dumps([(label, fraction_text(value)) for label, value in evaluations], separators=(",", ":")).encode("ascii")
        )
        ray_records.append({
            "side": name,
            "q1": fraction_text(q1),
            "q": fraction_text(q_value),
            "zero_profile": zeros,
            "parent_evaluation_sha256": evaluation_digest,
        })

    falsifier_result = load_json(FALSIFIER / "RESULT.json")
    require(
        falsifier_result["semantic_sha256"]
        == object_digest(b"d9-s1237-normal-link-falsifier-result-v1", falsifier_result)
        == EXPECTED_FALSIFIER_RESULT_DIGEST,
        "falsifier result semantic digest",
    )
    require(falsifier_result["factor"]["factor_id"] == 8_552, "falsifier factor label")
    require(falsifier_result["factor"]["family_allowed_orientation"] == census["family"][8_552] == -1, "factor 8552 allowed orientation")
    require(falsifier_result["obstruction"]["rays"] == [
        {
            **stored,
        }
        for stored in falsifier_result["obstruction"]["rays"]
    ], "falsifier ray structure")
    for derived_ray, stored_ray in zip(ray_records, falsifier_result["obstruction"]["rays"], strict=True):
        require(derived_ray["side"] == stored_ray["side"], "falsifier ray order")
        require(derived_ray["q1"] == stored_ray["lowest_residual_form"], "falsifier q1 drift")
        require(derived_ray["q"] == stored_ray["exact_factor_value"], "falsifier q drift")
        require(derived_ray["zero_profile"] == stored_ray["lift_parent_zero_profile"] == stored_ray["first_order_parent_zero_profile"], "falsifier stratum drift")
        require(derived_ray["parent_evaluation_sha256"] == stored_ray["parent_evaluation_sha256"], "falsifier parent-evaluation digest")
    require(falsifier_result["strength"]["level_c_strict_open_parent_crossing"] is False, "false strict crossing")
    return {
        "parent_inequality_count": len(parents),
        "face_vanishing_parent_count": len(zero_on_face),
        "gordan_pairs": derived,
        "factor_8552_rays": ray_records,
        "producer_normal_semantic_sha256": producer_normal["semantic_sha256"],
        "producer_result_semantic_sha256": producer_result["semantic_sha256"],
        "falsifier_result_semantic_sha256": falsifier_result["semantic_sha256"],
    }


def validate_certificate_contract(census: dict) -> dict:
    result = load_json(CERTIFICATE / "RESULT.json")
    require(result["mathematical_endpoint"] is None, "certificate engineer overclaimed endpoint")
    require(result["outcome"] == "VERSIONED_FAIL_CLOSED_ENVELOPE_PRODUCER_PAYLOAD_ABSENT", "certificate gap classification")
    require(result["literal_census"] == {
        "class_count": 3_539,
        "active_occurrence_count": 5_026,
        "semantic_sha256": EXPECTED_CERTIFICATE_CENSUS_DIGEST,
        "reconstruction": "INDEPENDENT_FROM_PINNED_DETERMINANT_AND_CIRCUIT_SOURCES",
    }, "certificate census binding")
    require(census["certificate_census_semantic_sha256"] == EXPECTED_CERTIFICATE_CENSUS_DIGEST, "referee/certificate census mismatch")
    completed = subprocess.run(
        [sys.executable, "ops/team/diag9-s1237-normal-link-certificate/verify_normal_link_certificate.py"],
        cwd=ROOT, check=True, capture_output=True, text=True,
    )
    require("incomplete/sample-only producer template rejected" in completed.stdout, "certificate fail-closed replay")
    return {
        "contract_endpoint": None,
        "template_rejected": True,
        "census_digest": EXPECTED_CERTIFICATE_CENSUS_DIGEST,
        "acceptance_gap": "CLOSED_ONLY_BY_REFEREE_ADAPTER_V1_FOR_THE_TWO_MATERIALIZED_WITNESS_METHODS",
    }


def validate_closing_manifest(manifest: dict, census: dict, geometry: dict, certificate: dict) -> None:
    require(manifest["format"] == "diag9-s1237-normal-link-referee-closing-manifest-v1", "closing format")
    require(manifest["frozen_head"] == FROZEN_HEAD and manifest["frozen_tree"] == FROZEN_TREE, "closing frozen binding")
    require(manifest["frozen_parent"] == FROZEN_PARENT, "closing parent binding")
    require(manifest["target_id"] == TARGET and manifest["endpoint"] == ENDPOINT, "closing endpoint binding")
    require(manifest["verdict"] == "ACCEPT" and manifest["classification"] == "FINITE_EXACT_LOCAL_NO_GO", "closing verdict")
    require(manifest["ledger"] == {"before": "2/9", "after": "2/9", "delta": 0}, "closing ledger")
    require(manifest["authority_epoch"] == "LIBRARY_CANONICAL_DRIVE_RECOVERY_GITHUB_READ_ONLY", "closing authority")
    require(manifest["counts"] == {
        "active_factor_classes": census["active_factor_count"],
        "all_occurrences_of_active_classes": census["all_occurrence_count"],
        "aligned_occurrence_union": census["aligned_occurrence_count"],
        "parent_inequalities": geometry["parent_inequality_count"],
        "load_bearing_initial_forms": 4,
        "gordan_relations": 2,
        "factor_8552_exact_lifts": 3,
    }, "closing counts")
    digests = manifest["semantic_digests"]
    require(digests == {
        "active_sector": EXPECTED_ACTIVE_SECTOR_DIGEST,
        "producer_literal_inventory": census["producer_literal_semantic_sha256"],
        "producer_normal_inventory": geometry["producer_normal_semantic_sha256"],
        "producer_result": geometry["producer_result_semantic_sha256"],
        "falsifier_result": geometry["falsifier_result_semantic_sha256"],
        "certificate_literal_census": census["certificate_census_semantic_sha256"],
        "referee_census": census["referee_census_semantic_sha256"],
    }, "closing semantic digests")
    require(manifest["adapter"] == {
        "version": "diag9-s1237-normal-link-referee-adapter-v1",
        "producer_method": "EXACT_OPPOSITE_PARENT_INITIAL_FORMS_WITH_POSITIVE_GORDAN_WEIGHTS",
        "falsifier_method": "EXACT_SAME_RECURSIVE_STRATUM_TWO_SIDED_FACTOR_WALL",
        "certificate_v1_payload_status": "ABSENT_AND_NOT_RETROACTIVELY_ACCEPTED",
        "referee_effect": "INDEPENDENTLY_REDERIVES_ONLY_THE_TWO_FROZEN_WITNESS_METHODS",
    }, "closing adapter boundary")
    adapter = load_json(ADAPTER)
    require(adapter["format"] == "diag9-s1237-normal-link-referee-adapter-v1", "adapter format")
    require(adapter["frozen_head"] == FROZEN_HEAD and adapter["frozen_tree"] == FROZEN_TREE, "adapter frozen binding")
    require(adapter["accepted_endpoint"] == ENDPOINT and len(adapter["accepted_methods"]) == 2, "adapter method boundary")
    require(adapter["certificate_v1"]["producer_payload_status"] == "ABSENT", "adapter certificate gap")
    require(adapter["certificate_v1"]["treatment"] == "PRESERVED_FAIL_CLOSED; NOT_RETROACTIVELY_ACCEPTED", "adapter fail-closed treatment")
    require(adapter["scope"]["ledger"] == "2/9" and adapter["scope"]["diagonal_9"] == "OPEN", "adapter scope")
    require(
        adapter["semantic_sha256"] == object_digest(b"d9-s1237-normal-link-referee-adapter-v1", adapter),
        "adapter semantic digest",
    )
    require(manifest["scope"] == {
        "accepted": "FINITE_EXACT_LOCAL_NORMAL_LINK_ROUTE_NO_GO",
        "ordinary_radial_model": "SINGULAR_AT_THE_EXACT_REPLAYED_SUPPORT_POINTS",
        "weighted_recursive_links": "OPEN",
        "strict_open_parent_crossing": "NOT_CLAIMED",
        "global_coverage_or_separator": "NOT_CLAIMED",
        "collar_or_mincut": "NOT_CLAIMED",
        "diagonal_9": "OPEN",
        "tangential_four_support_reduction": "RETIRED_AS_STATED",
    }, "closing scope")
    for relative, expected in manifest["artifact_sha256"].items():
        path = (ROOT / relative).resolve()
        require(path.is_relative_to(ROOT) and path.is_file(), f"closing artifact path {relative}")
        require(sha256(path) == expected, f"closing artifact drift {relative}")
    require(
        manifest["semantic_sha256"] == object_digest(b"d9-s1237-normal-link-referee-closing-v1", manifest),
        "closing manifest semantic digest",
    )
    require(certificate["template_rejected"] is True, "certificate gap not fail-closed")
    result = load_json(RESULT)
    require(result["reviewed_head"] == FROZEN_HEAD and result["reviewed_tree"] == FROZEN_TREE, "result frozen binding")
    require(result["verdict"] == "ACCEPT" and result["endpoint"] == ENDPOINT, "result verdict")
    require(result["ledger"]["delta"] == 0 and result["ledger"]["after"] == "2/9", "result ledger")
    require(result["hostile_mutations_rejected"] == 16, "result hostile count")
    require(result["closing_manifest_semantic_sha256"] == manifest["semantic_sha256"], "result closing binding")
    require(
        result["semantic_sha256"] == object_digest(b"d9-s1237-normal-link-referee-result-v1", result),
        "result semantic digest",
    )


def hostile_canaries(stored: dict, census: dict, geometry: dict, certificate: dict) -> int:
    tests = load_json(HOSTILE_TESTS)
    require(tests["format"] == "diag9-s1237-normal-link-referee-hostile-tests-v1", "hostile test format")
    require(len(tests["mutations"]) == 16, "hostile test census")
    mutations = (
        (("frozen_tree",), "0" * 40),
        (("counts", "active_factor_classes"), 3_538),
        (("counts", "all_occurrences_of_active_classes"), 6_166),
        (("counts", "parent_inequalities"), 69),
        (("semantic_digests", "producer_literal_inventory"), "0" * 64),
        (("semantic_digests", "falsifier_result"), "0" * 64),
        (("adapter", "producer_method"), "DIGEST_ONLY_GEOMETRY"),
        (("adapter", "falsifier_method"), "SAMPLED_WALL"),
        (("scope", "ordinary_radial_model"), "GLOBALLY_EMPTY"),
        (("scope", "weighted_recursive_links"), "CLOSED"),
        (("scope", "strict_open_parent_crossing"), "PROVED"),
        (("scope", "collar_or_mincut"), "PROVED"),
        (("scope", "diagonal_9"), "PROVED"),
        (("ledger", "after"), "3/9"),
        (("artifact_sha256", "../unauthorized"), "0" * 64),
        (("authority_epoch",), "GITHUB_PUSH_AUTHORIZED"),
    )
    require([name for name, _description in tests["mutations"]] == [
        "source-tree", "literal-omission", "occurrence-omission", "parent-omission",
        "orientation-sign-digest", "factor-wall-digest", "digest-only-geometry",
        "sampled-wall", "false-no-arc", "false-radius", "false-strict-crossing",
        "false-collar", "false-d9", "false-3-of-9", "unauthorized-path", "authority-epoch",
    ], "hostile test names")
    rejected = 0
    for path, value in mutations:
        candidate = deepcopy(stored)
        target = candidate
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        try:
            validate_closing_manifest(candidate, census, geometry, certificate)
        except (AssertionError, FileNotFoundError):
            rejected += 1
    require(rejected == len(mutations), "hostile mutation survived")
    return rejected


def main() -> None:
    validate_revision_and_authority()
    validate_source_manifest()
    census = rebuild_census()
    geometry = replay_geometry(census)
    certificate = validate_certificate_contract(census)
    closing = load_json(CLOSING_MANIFEST)
    validate_closing_manifest(closing, census, geometry, certificate)
    rejected = hostile_canaries(closing, census, geometry, certificate)
    require(not git("status", "--porcelain"), "referee worktree is not clean")
    print(
        "PASS frozen referee adapter:",
        census["active_factor_count"], "classes /",
        census["all_occurrence_count"], "all occurrences /",
        census["aligned_occurrence_count"], "aligned occurrences;",
        geometry["parent_inequality_count"], "parent inequalities;",
        "4 initial forms / 2 Gordan relations; factor 8552 three-lift wall",
    )
    print(f"PASS {rejected}/{rejected} hostile closing mutations rejected")
    print("ACCEPT", ENDPOINT, "at", FROZEN_HEAD, FROZEN_TREE)
    print("SCOPE finite-exact local normal-link route no-go; weighted walls, strict open-parent crossing, global coverage, collar, and D9 remain open; ledger 2/9")
    print("CLOSING SEMANTIC SHA256", closing["semantic_sha256"])


if __name__ == "__main__":
    main()
