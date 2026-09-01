#!/usr/bin/env python3
"""Independent exact replay of the S12,37 recursive-facet obstruction."""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
from fractions import Fraction
import hashlib
import itertools
import json
from pathlib import Path
import subprocess
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OM = ROOT / "ai" / "omreal"
DATA = OM / "data"
RESULT = HERE / "RESULT.json"
MANIFEST = HERE / "SOURCE_MANIFEST.json"
OPENING_COMMIT = "c6bd7a6afeda0888fc950710b941cac6f6c9bf95"
OPENING_TREE = "9c2dbe39a3ea0f36e9e9c8f845e6f72e98526421"
FACTOR_ID = 8_552
OCCURRENCE_INDEX = 24_140
OCCURRENCE = (4, 9, 23, 37)
SUPPORT = (3, 1, 15)
NORMAL_NAMES = ("b", "c", "d", "e", "f", "delta_i")
NORMAL_AXES = (1, 2, 3, 4, 5, 8)
BASE = (
    Fraction(3, 4), Fraction(0), Fraction(0),
    Fraction(0), Fraction(0), Fraction(0),
    Fraction(1, 4), Fraction(2, 3), Fraction(1, 4),
)
T = Fraction(1, 100)
RAYS = {
    "minus": tuple(Fraction(value, 55) for value in (13, 11, 19, 12, 0, -14)),
    "wall": (
        Fraction(51, 247), Fraction(32, 247), Fraction(656, 1235),
        Fraction(164, 1235), Fraction(0), Fraction(-491, 1235),
    ),
    "plus": tuple(Fraction(value, 35) for value in (7, 4, 20, 4, 0, -15)),
}


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def fraction_text(value: Fraction | int) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def parse_fraction(value: str) -> Fraction:
    return Fraction(value)


def canonical_digest(prefix: bytes, candidate: dict) -> str:
    payload = dict(candidate)
    payload.pop("semantic_sha256", None)
    return hashlib.sha256(
        prefix + json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def validate_manifest() -> dict:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    require(manifest["format"] == "diag9-s1237-normal-link-falsifier-source-manifest-v1", "source manifest format")
    require(manifest["opening_commit"] == OPENING_COMMIT, "source opening commit")
    require(manifest["opening_tree"] == OPENING_TREE, "source opening tree")
    for relative, expected in manifest["sources"].items():
        require(sha256(ROOT / relative) == expected, f"source drift: {relative}")
    actual = canonical_digest(b"d9-s1237-normal-link-falsifier-sources-v1\0", manifest)
    require(actual == manifest["semantic_sha256"], "source manifest semantic digest")
    return manifest


def determinant4(matrix) -> int:
    total = 0
    for permutation in itertools.permutations(range(4)):
        inversions = sum(
            permutation[left] > permutation[right]
            for left in range(4) for right in range(left + 1, 4)
        )
        term = 1
        for row, column in enumerate(permutation):
            term *= int(matrix[row][column])
        total += (-1 if inversions & 1 else 1) * term
    return total


def det_rows(rows, identifiers) -> int:
    return determinant4(tuple(rows[index] for index in identifiers))


def signed(value: int) -> int:
    require(value != 0, "unexpected zero determinant")
    return 1 if value > 0 else -1


def orient_certificate(occurrence, certificate, rows):
    raw = det_rows(rows, occurrence)
    require(raw != 0, "orientation chart lies on residual wall")
    if certificate[0] == "ordinary":
        circuit, auxiliary = certificate[1], certificate[2]
        columns = circuit + (auxiliary,)
        coefficients = tuple(
            (-1) ** omitted
            * det_rows(rows, columns[:omitted] + columns[omitted + 1 :])
            for omitted in range(4)
        )
        require(all(coefficients), "ordinary fixed coefficient vanished")
        order = signed(det_rows(rows, circuit)) * signed(raw)
        data = (circuit, tuple(map(signed, coefficients)), auxiliary, order)
    else:
        circuit, residual, structural = certificate[1:4]
        columns = circuit + (residual, structural)
        coefficients = tuple(
            (-1) ** omitted
            * det_rows(rows, columns[:omitted] + columns[omitted + 1 :])
            for omitted in range(5)
        )
        require(all(coefficients[index] for index in range(3)), "localization coefficient vanished")
        require(coefficients[3] == 0 and coefficients[4] != 0, "localization zero pattern")
        order = signed(det_rows(rows, circuit + (residual,))) * signed(raw)
        data = (
            circuit,
            tuple(signed(coefficients[index]) for index in range(3)),
            structural,
            order,
        )
    return data, signed(raw)


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


def rebuild_family_orientation() -> dict:
    # Transport supplies the canonical source census; every sign and
    # acceptance decision below is recomputed here with an independent 4x4
    # determinant and alignment implementation.
    sys.path.insert(0, str(OM))
    import verify_diag9_active_sector as source

    certificates = source.transported_certificates()
    with np.load(DATA / "DIAG9_GRAPH_global_factor_census.npz", allow_pickle=False) as stored:
        foursets = tuple(tuple(map(int, row)) for row in stored["occurrence_fourset"])
        occurrence_factor = tuple(map(int, stored["occurrence_factor"]))
        factor_count = len(stored["factor_multiplicity"])
        unit_offset = np.asarray(stored["occurrence_unit_offset"], dtype=np.uint32)
        unit_index = np.asarray(stored["occurrence_unit_index"], dtype=np.uint8)
        factor_offset = np.asarray(stored["factor_offset"], dtype=np.uint32)
        factor_exponent = np.asarray(stored["factor_exponent"], dtype=np.uint8)
        factor_coefficient = np.asarray(stored["factor_coefficient"], dtype=np.int64)
    require(len(foursets) == 84_840 and set(foursets) == set(certificates), "occurrence source census")
    with np.load(DATA / "seeat_parent2599_upper178.npz", allow_pickle=False) as stored:
        chart = np.asarray(stored["chart_matrix"][0], dtype=np.int64)
    rows = source.topes.derived_rows(chart)

    oriented = []
    conflicting = set()
    for occurrence_index, occurrence in enumerate(foursets):
        alternatives = tuple(
            orient_certificate(occurrence, certificate, rows)
            for certificate in certificates[occurrence]
        )
        require(len({raw for _data, raw in alternatives}) == 1, "raw occurrence sign conflict")
        patterns = {normalized_pattern(data) for data, _raw in alternatives}
        if len(patterns) > 1:
            conflicting.add(occurrence_index)
        oriented.append(alternatives[0])
    empty_factors = {occurrence_factor[index] for index in conflicting}
    require(len(conflicting) == 27_944 and len(empty_factors) == 8_916, "empty-factor replay")

    representative = [-1] * factor_count
    for occurrence_index, factor in enumerate(occurrence_factor):
        if representative[factor] < 0:
            representative[factor] = occurrence_index
    require(all(index >= 0 for index in representative), "factor without representative")
    representative_sign = [oriented[index][1] for index in representative]
    with np.load(DATA / "ninth_candidate_12_37_antichain.npz", allow_pickle=False) as stored:
        signatures = tuple(map(int, stored["signature"]))

    family = {}
    aligned_signature_indices = defaultdict(list)
    for signature_index, signature in enumerate(signatures):
        for occurrence_index, ((data, raw), factor) in enumerate(zip(oriented, occurrence_factor, strict=True)):
            if factor in empty_factors:
                continue
            allowed = allowed_raw(signature, data)
            if allowed is None:
                continue
            orientation = allowed * raw * representative_sign[factor]
            previous = family.setdefault(factor, orientation)
            require(previous == orientation, "family factor orientation conflict")
            if factor == FACTOR_ID:
                aligned_signature_indices[factor].append(signature_index)
    require(len(family) == 3_539, "active factor count")
    require(family[FACTOR_ID] == -1, "factor 8552 orientation")

    indices = [index for index, factor in enumerate(occurrence_factor) if factor == FACTOR_ID]
    require(indices == [OCCURRENCE_INDEX], "factor 8552 multiplicity")
    require(foursets[OCCURRENCE_INDEX] == OCCURRENCE, "factor 8552 occurrence")
    start, stop = int(factor_offset[FACTOR_ID]), int(factor_offset[FACTOR_ID + 1])
    polynomial = [
        [*map(int, exponent), int(coefficient)]
        for exponent, coefficient in zip(
            factor_exponent[start:stop], factor_coefficient[start:stop], strict=True
        )
    ]
    units = list(map(int, unit_index[int(unit_offset[OCCURRENCE_INDEX]):int(unit_offset[OCCURRENCE_INDEX + 1])]))
    return {
        "candidate_active_factor_count": len(family),
        "certified_empty_factor_count": len(empty_factors),
        "factor_id": FACTOR_ID,
        "primitive_polynomial_rows": polynomial,
        "polynomial": "d*i-e",
        "family_allowed_orientation": -1,
        "family_allowed_side": "d*i-e<0",
        "aligned_signature_indices": sorted(set(aligned_signature_indices[FACTOR_ID])),
        "occurrence_index": OCCURRENCE_INDEX,
        "occurrence_fourset": list(OCCURRENCE),
        "occurrence_multiplicity": 1,
        "stripped_parent_unit_indices": units,
    }


def multiply(left, right):
    answer = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, first in enumerate(left):
        for j, second in enumerate(right):
            answer[i + j] += first * second
    return answer


def path_coefficients(polynomial, ray):
    coordinate_polynomials = []
    for axis, value in enumerate(BASE):
        if axis in NORMAL_AXES:
            coordinate_polynomials.append([value, ray[NORMAL_AXES.index(axis)]])
        else:
            coordinate_polynomials.append([value])
    answer = []
    for monomial, coefficient in polynomial.items():
        row = [Fraction(coefficient)]
        for axis, exponent in enumerate(monomial):
            for _ in range(exponent):
                row = multiply(row, coordinate_polynomials[axis])
        if len(answer) < len(row):
            answer += [Fraction(0)] * (len(row) - len(answer))
        for degree, value in enumerate(row):
            answer[degree] += value
    return answer


def evaluate(polynomial, point):
    total = Fraction(0)
    for monomial, coefficient in polynomial.items():
        value = Fraction(coefficient)
        for axis, exponent in enumerate(monomial):
            value *= point[axis] ** exponent
        total += value
    return total


def lift(ray_name: str, ray):
    point = list(BASE)
    for axis, value in zip(NORMAL_AXES, ray, strict=True):
        point[axis] += T * value
    if ray_name == "wall":
        # Exact residual-wall lift with the same first normal direction.
        point[4] = point[3] * point[8]
    return tuple(point)


def parent_and_wall_replay() -> dict:
    sys.path.insert(0, str(OM))
    import verify_diag3_pair_global_parent_face_gate as parent_source

    records = [json.loads(line) for line in parent_source.CATALOG.read_text().splitlines() if line]
    parents, target_digest = parent_source.parent_polynomials(records[parent_source.PARENT])
    require(len(parents) == 70, "parent bracket count")
    zero_on_face = []
    for label, target, polynomial, _terms in parents:
        value = target * evaluate(polynomial, BASE)
        require(value >= 0, f"base point parent sign: {label}")
        if value == 0:
            zero_on_face.append(label)
    require(len(zero_on_face) == 25, "face-vanishing parent bracket count")

    expected_q1 = {"minus": Fraction(-29, 220), "wall": Fraction(0), "plus": Fraction(1, 35)}
    lift_q = {
        "minus": Fraction(-40141, 30250000),
        "wall": Fraction(0),
        "plus": Fraction(8, 30625),
    }
    factor_polynomial = {
        (0, 0, 0, 0, 1, 0, 0, 0, 0): -1,
        (0, 0, 0, 1, 0, 0, 0, 0, 1): 1,
    }
    ray_rows = []
    for name in ("minus", "wall", "plus"):
        ray = RAYS[name]
        require(sum(ray[:5]) == 1, f"projective normalization: {name}")
        q1 = Fraction(1, 4) * ray[2] - ray[3]
        require(q1 == expected_q1[name], f"lowest residual normal form: {name}")
        zero_profile = []
        for label, target, polynomial, _terms in parents:
            if target * evaluate(polynomial, BASE) != 0:
                continue
            coefficients = path_coefficients(polynomial, ray)
            first = next((target * value for value in coefficients[1:] if value), None)
            if first is None:
                zero_profile.append(label)
            else:
                require(first > 0, f"parent-unsafe normal direction: {name} {label}")
        require(zero_profile == ["1237"], f"link-stratum profile: {name}")

        point = lift(name, ray)
        evaluations = [
            (label, target * evaluate(polynomial, point))
            for label, target, polynomial, _terms in parents
        ]
        require(all(value >= 0 for _label, value in evaluations), f"lift outside weak parent closure: {name}")
        zeros = [label for label, value in evaluations if value == 0]
        require(zeros == ["1237"], f"lift changed recursive parent stratum: {name}")
        q_value = evaluate(factor_polynomial, point)
        require(q_value == lift_q[name], f"lifted residual sign: {name}")
        evaluation_payload = json.dumps(
            [(label, fraction_text(value)) for label, value in evaluations],
            separators=(",", ":"),
        ).encode("ascii")
        evaluation_digest = hashlib.sha256(
            b"d9-s1237-normal-link-parent-values-v1\0" + evaluation_payload
        ).hexdigest()
        ray_rows.append({
            "side": name,
            "normal_direction": [fraction_text(value) for value in ray],
            "projective_sum_first_five": "1",
            "lowest_residual_form": fraction_text(q1),
            "first_order_parent_zero_profile": ["1237"],
            "lift_parameter": fraction_text(T),
            "exact_lift_point": [fraction_text(value) for value in point],
            "exact_factor_value": fraction_text(q_value),
            "lift_parent_zero_profile": zeros,
            "strictly_positive_parent_brackets": 69,
            "parent_evaluation_sha256": evaluation_digest,
        })
    return {
        "support": list(SUPPORT),
        "face_point": [fraction_text(value) for value in BASE],
        "tangential_coordinates": {"a": "3/4", "g": "1/4", "h": "2/3", "i": "g"},
        "normal_coordinates": list(NORMAL_NAMES),
        "parent_brackets_replayed": 70,
        "face_identically_zero_parent_brackets": len(zero_on_face),
        "parent_target_digest": target_digest,
        "common_recursive_link_stratum": {
            "identically_zero_parent_brackets": ["1237"],
            "interpretation": "f=0 recursive parent-link facet",
        },
        "lowest_normal_form": "q1=d/4-e",
        "rays": ray_rows,
    }


def build_expected(manifest: dict) -> dict:
    factor = rebuild_family_orientation()
    obstruction = parent_and_wall_replay()
    candidate = {
        "format": "diag9-s1237-normal-link-falsifier-result-v1",
        "track_id": "diag9-s1237-normal-link-falsifier",
        "target_id": "D9_S1237_4SUPPORT_NORMAL_LINK_GATE1",
        "opening_commit": OPENING_COMMIT,
        "opening_tree": OPENING_TREE,
        "canonical_math_base": "c55d896cc5c0370e993b793992a2f05d894e0095",
        "outcome": "disproved",
        "endpoint": "NORMAL_LINK_REDUCTION_NO_GO",
        "classification": "finite exact obstruction",
        "summary": "Active factor 8552 creates an exact two-sided inward normal wall inside the common recursive parent-link facet 1237 on support (3,1,15).",
        "factor": factor,
        "obstruction": obstruction,
        "strength": {
            "proved_level": "b",
            "level_a_nonzero_boundary_normal_form": True,
            "level_b_two_sided_wall_in_one_certified_link_stratum": True,
            "level_c_strict_open_parent_crossing": False,
        },
        "scope": {
            "included": "One exact active oriented factor, one support, one recursive parent-link facet, and an exact same-stratum two-sided wall.",
            "strict_open_parent_crossing": "NOT_CLAIMED; bracket 1237 remains zero on every displayed lift.",
            "collar_or_mincut": "NOT_CONSTRUCTED",
            "global_d9_separator": "NOT_CLAIMED",
            "all_3539_normal_links": "NOT_ENUMERATED; stop rule fired at the first exact fatal obstruction.",
            "other_support": "NOT_DECIDED",
        },
        "attack_matrix": [
            {"attack": "identically-zero-on-face", "status": "FATAL_DEFECT_FOUND", "evidence": "q=d*i-e restricts identically to zero when d=e=0."},
            {"attack": "lowest-normal-form", "status": "FATAL_DEFECT_FOUND", "evidence": "q1=d/4-e has exact negative, zero, and positive directions."},
            {"attack": "parent-residence", "status": "PASSED_FOR_OBSTRUCTION", "evidence": "All 70 signed parent brackets are exact; each lift has only 1237 zero."},
            {"attack": "recursive-facet/coface", "status": "FATAL_DEFECT_FOUND", "evidence": "All three directions share the f=0 parent-link facet."},
            {"attack": "orientation", "status": "PASSED_FOR_OBSTRUCTION", "evidence": "Independent circuit replay gives family orientation q<0."},
            {"attack": "duplicate-occurrence", "status": "NOT_APPLICABLE_TO_WITNESS", "evidence": "Factor 8552 has one occurrence and no stripped parent unit."},
            {"attack": "higher-order-stabilization", "status": "EXACT_WALL_LIFTED", "evidence": "The wall lift imposes e=d*i exactly; side lifts retain opposite exact signs at t=1/100."},
            {"attack": "boundary-gluing", "status": "GUARDED", "evidence": "The result does not glue through the excluded open-parent boundary."},
            {"attack": "fake-infinity", "status": "GUARDED", "evidence": "No artificial box or point at infinity is introduced."},
            {"attack": "sample-promotion", "status": "GUARDED", "evidence": "Every displayed coefficient and lift is exact rational arithmetic."},
            {"attack": "collar/mincut/global proof", "status": "PROHIBITED_AND_NOT_RUN", "evidence": "The endpoint is local to one recursive normal-link facet."},
        ],
        "ledger": {"opening": "2/9", "closing": "2/9", "delta": 0, "change_recommended": "none"},
        "next_action": "Retire the tangential four-support reduction as stated; any successor must include recursive oriented normal-link walls before a collar or mincut target.",
        "source_manifest_sha256": sha256(MANIFEST),
        "source_manifest_semantic_sha256": manifest["semantic_sha256"],
        "semantic_sha256": "",
    }
    candidate["semantic_sha256"] = canonical_digest(
        b"d9-s1237-normal-link-falsifier-result-v1\0", candidate
    )
    return candidate


def validate(candidate: dict, expected: dict) -> None:
    require(candidate == expected, "stored falsifier result does not replay")
    require(candidate["endpoint"] == "NORMAL_LINK_REDUCTION_NO_GO", "wrong endpoint")
    require(candidate["strength"] == {
        "proved_level": "b",
        "level_a_nonzero_boundary_normal_form": True,
        "level_b_two_sided_wall_in_one_certified_link_stratum": True,
        "level_c_strict_open_parent_crossing": False,
    }, "strength overclaim")
    require(candidate["ledger"]["closing"] == "2/9" and candidate["ledger"]["delta"] == 0, "ledger overclaim")
    require(candidate["semantic_sha256"] == canonical_digest(
        b"d9-s1237-normal-link-falsifier-result-v1\0", candidate
    ), "result semantic digest")


def hostile_canaries(stored: dict, expected: dict) -> int:
    mutations = []
    paths_and_values = (
        (("factor", "factor_id"), 8553),
        (("factor", "primitive_polynomial_rows", 0, 9), 1),
        (("factor", "family_allowed_orientation"), 1),
        (("factor", "occurrence_fourset", 0), 5),
        (("obstruction", "support", 2), 7),
        (("obstruction", "lowest_normal_form"), "0"),
        (("obstruction", "rays", 0, "normal_direction", 0), "0"),
        (("obstruction", "rays", 1, "exact_factor_value"), "1"),
        (("obstruction", "rays", 2, "strictly_positive_parent_brackets"), 68),
        (("obstruction", "common_recursive_link_stratum", "identically_zero_parent_brackets"), []),
        (("strength", "level_c_strict_open_parent_crossing"), True),
        (("scope", "global_d9_separator"), "PROVED"),
        (("ledger", "closing"), "3/9"),
        (("source_manifest_sha256",), "0" * 64),
        (("semantic_sha256",), "0" * 64),
    )
    for path, value in paths_and_values:
        candidate = deepcopy(stored)
        target = candidate
        for key in path[:-1]:
            target = target[key]
        target[path[-1]] = value
        mutations.append(candidate)
    rejected = 0
    for candidate in mutations:
        try:
            validate(candidate, expected)
        except AssertionError:
            rejected += 1
    require(rejected == len(mutations), "hostile mutation survived")
    return rejected


def main() -> None:
    manifest = validate_manifest()
    require(
        subprocess.check_output(["git", "rev-parse", f"{OPENING_COMMIT}^{{tree}}"], cwd=ROOT, text=True).strip()
        == OPENING_TREE,
        "opening commit/tree drift",
    )
    stored = json.loads(RESULT.read_text(encoding="utf-8"))
    expected = build_expected(manifest)
    validate(stored, expected)
    rejected = hostile_canaries(stored, expected)
    print("PASS independent S12,37 active orientation: 3539 factors; factor 8552 has allowed side d*i-e<0")
    print("PASS exact support (3,1,15) normal form: d/4-e")
    print("PASS same recursive facet 1237: exact negative / wall / positive lifts; all 70 parent brackets replayed")
    print(f"PASS {rejected}/{rejected} hostile mutations rejected")
    print("ENDPOINT NORMAL_LINK_REDUCTION_NO_GO (level b)")
    print("SCOPE no strict open-parent crossing, collar, mincut, global D9 separator, or ledger change; honest 2/9")
    print("SEMANTIC SHA256", stored["semantic_sha256"])


if __name__ == "__main__":
    main()
