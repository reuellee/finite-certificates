#!/usr/bin/env python3
"""Producer-independent exact certificate for the seven homogenizer types.

The only polynomial payload consumed here is the immutable predecessor JSON.
No constructor, falsifier, or predecessor-certificate code is imported.  The
108-term affine factor, its degree-(2,2,2) trihomogenization, seven boundary
restrictions, tangent derivatives, ambient normal derivatives, chart/type
incidences, and deepest factorization are rebuilt with stdlib integer sparse
arithmetic.

The certificate deliberately stops before unsupported component, overlap,
affine-pullback, or 70-parent classifications.  Candidate artifacts can be
compared through ``canonical_boundary_representation``; comparison is parsed
object equality and therefore independent of JSON whitespace and key order.
"""

from __future__ import annotations

import argparse
import ast
from copy import deepcopy
from hashlib import sha256
from itertools import combinations, product
import json
from pathlib import Path
import struct
import subprocess
import sys
import zipfile


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CYCLE_ID = "2026-09-01-d9-row2599-factor19069-homogenizer-boundary-type-stratification-gate1"
TRACK_ID = "d9-factor19069-homogenizer-boundary-certificate"
TARGET = "D9_ROW2599_FACTOR19069_HOMOGENIZER_BOUNDARY_TYPE_STRATIFICATION_GATE1"
BASE_REVISION = "0ffb0295d74e6c50a3c198b67c9821d2fe2e2760"
BASE_TREE = "d01cfbbe04f721496a91d13f85d3688262869ac0"
OPENING_REVISION = "ff71f37eaafef17d57edda374508f7a8c7d38207"
OPENING_TREE = "4cb7c001243f3e1eb14d0a5867330c198c5dd381"
CANDIDATE_REVISION = "25757510dd88e8b7bbe5668c89f93b2a46b264de"
CANDIDATE_TREE = "47395637cc10c2bd736530719b6e2f3cf57b1629"

VARIABLES = ("a", "b", "c", "u", "d", "e", "f", "v", "g", "h", "i", "w")
BLOCKS = (("a", "b", "c", "u"), ("d", "e", "f", "v"), ("g", "h", "i", "w"))
BLOCK_INDICES = ((0, 1, 2, 3), (4, 5, 6, 7), (8, 9, 10, 11))
AFFINE_VARIABLES = tuple("abcdefghi")
AFFINE_TO_HOMOGENEOUS = (0, 1, 2, 4, 5, 6, 8, 9, 10)
AFFINE_BLOCKS = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
HOMOGENIZERS = ("u", "v", "w")
TYPE_ORDER = (
    ("u", "v", "w"),
    ("u", "v"),
    ("u", "w"),
    ("v", "w"),
    ("u",),
    ("v",),
    ("w",),
)

CYCLE = ROOT / "ops" / "research-team" / "cycles" / CYCLE_ID
OPENING = CYCLE / "OPENING_AUDIT.json"
PREDECESSOR = ROOT / "ops" / "team" / "d9-factor19069-explicit-trihom-jacobian-chart-constructor" / "PROJECTIVE_CHART_FRONTIER.json"
CONSTRUCTOR = ROOT / "ops" / "team" / "d9-factor19069-homogenizer-boundary-constructor"
CONSTRUCTOR_FRONTIER = CONSTRUCTOR / "HOMOGENIZER_BOUNDARY_TYPE_FRONTIER.json"
CONSTRUCTOR_MANIFEST = CONSTRUCTOR / "SOURCE_MANIFEST.json"
CONSTRUCTOR_RESULT = CONSTRUCTOR / "RESULT.json"
SOURCE_RECONSTRUCTION = HERE / "SOURCE_RECONSTRUCTION.json"
BOUNDARY_CERTIFICATE = HERE / "BOUNDARY_CERTIFICATE.json"
CANDIDATE_COMPARISON = HERE / "CANDIDATE_COMPARISON.json"
SOURCE_MANIFEST = HERE / "SOURCE_MANIFEST.json"
HOSTILE_TESTS = HERE / "HOSTILE_TESTS.json"
RESULT = HERE / "RESULT.json"
FINDINGS = HERE / "FINDINGS.md"

PINNED_INPUTS = {
    f"ops/research-team/cycles/{CYCLE_ID}/CYCLE.md": "17eabb966da4b6dc6468616fd4b90dea3dfe41672a881fe05e97f99e835e6809",
    f"ops/research-team/cycles/{CYCLE_ID}/OPENING_AUDIT.json": "a430effec7a0defb5646be8d823c39e31aaf09227261e4d3fe816baba3903821",
    f"ops/research-team/cycles/{CYCLE_ID}/OBLIGATION_GRAPH.json": "f85c957eef37a3e991119057f28685f5d5e2208271da053b9e0294e03b530e35",
    f"ops/research-team/cycles/{CYCLE_ID}/WORK_ORDERS.yaml": "1c894fbf181416e84c0ec0397c6a04f45400721871a9c40ad210dce8f2424230",
    f"ops/research-team/cycles/{CYCLE_ID}/verify_opening_audit.py": "4c4a628c4f5a3c4607a3235534e05d8e91d2f64388ce688205d3095e9296d1ed",
    "ops/research-team/PROTOCOL.md": "54f1a15b7774085005707727780b266ffbd4a8edc4687fe14e1e6bc76d229031",
    "ops/research-team/verify_cycle_protocol.py": "4d9e16daed0de08af415e95c746803b512ea8b92c452df6df2c9e09fdcd3b7d1",
    "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-explicit-trihom-jacobian-chart-gate1/CYCLE_REPORT.md": "0d80e1e668a7ab764589365f7e4177b2482ffa4f0e04d23c2d380020de63069e",
    "ops/research-team/cycles/2026-09-01-d9-row2599-factor19069-explicit-trihom-jacobian-chart-gate1/OPENING_AUDIT.json": "e513ef2f63f616cd06d3d5a27884a9919077ea1044132970de1d9691d09bbb55",
    "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-constructor/PROJECTIVE_CHART_FRONTIER.json": "815edf97a68a049f8fb6749adf948cc406ec7a258de480cf3ada3e301ca6de67",
    "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-constructor/SOURCE_MANIFEST.json": "9d4c69493f1ebb0a7a3e1f1bf8832ab56bace65a9841c4700af713322bd4658c",
    "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-certificate/RESULT.json": "ab9e4aa1591e425b210b98442ae22803b99a8974311022088561c1ac708ec375",
    "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-falsifier/RESULT.json": "12ac0d8da67d58720b5ff6f06d30760de8fc78382ff5a856e4976351af94cb57",
    "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-referee/RESULT.json": "e4088338d86d05442fe72289211500be187e6b99acd02c37a4fead51a07edc0f",
    "ai/omreal/data/CANONICAL_RESEARCH_STATE_V6.json": "24d033a7f7d9886d8a538776a1453f1fd00af617da5c03f0f6a6e3921fe8b9bf",
    "ai/omreal/verify_canonical_research_state_v6.py": "0aef5bb2c999e74fcad71e2f8346e276dd66cd3c645d0b874a6d81109934e832",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json": "956fbe7e5c7b1e04c8873ed9c0f3de9cb5420e3e06f1d5fae4c60f4e0571b364",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json": "cc279d125605b45d25a3a01f462ad051038102f2bf12574f494a9d261bfc7401",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin": "adb2e7257457f158e809450683c46fe7ecafdbdd4a7efdf9ac630e8a4f0fb03f",
    "ai/omreal/data/DIAG9_GRAPH_row2599_factor_states.npz": "f44b1fccfb4e61273aeceb8796a18098d82c48473e257556ce3d2a22f99b0bcf",
    "ai/omreal/certs_4_8.jsonl": "c55e805d60d8086bcb84a312f2103a9973fc2691d0fd97f3d9a1d9809d2b163b",
}

CANDIDATE_PINS = {
    "ops/team/d9-factor19069-homogenizer-boundary-constructor/HOMOGENIZER_BOUNDARY_TYPE_FRONTIER.json": "18b0f7bf939646b884f05dc55832b509a54574cf3c2498461839f3c906418a6d",
    "ops/team/d9-factor19069-homogenizer-boundary-constructor/RESULT.json": "d7ad15fd2bc49b25334f836a34de2cc25d75a903902545ac354bded3a919db8b",
    "ops/team/d9-factor19069-homogenizer-boundary-constructor/SOURCE_MANIFEST.json": "0e39b510708b6792c02dfdc537290b10d9897fad7b4a7b5a2f26987ae5ff9083",
}


class Reject(AssertionError):
    """An exact, fail-closed gate rejected its input."""


def require(condition: bool, marker: str) -> None:
    if not condition:
        raise Reject(marker)


def canonical_bytes(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("ascii")


def canonical_digest(value) -> str:
    return sha256(canonical_bytes(value)).hexdigest()


def semantic_digest(value: dict) -> str:
    unsealed = deepcopy(value)
    unsealed.pop("semantic_sha256", None)
    return canonical_digest(unsealed)


def seal(value: dict) -> dict:
    value["semantic_sha256"] = semantic_digest(value)
    return value


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, value) -> None:
    with path.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(json.dumps(value, indent=2, sort_keys=True) + "\n")


def file_digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def normalize(records: list[dict], arity: int = 12) -> list[dict]:
    collected: dict[tuple[int, ...], int] = {}
    for record in records:
        require(set(record) == {"exponents", "coefficient"}, "sparse record schema")
        exponent = tuple(record["exponents"])
        coefficient = record["coefficient"]
        require(len(exponent) == arity, "sparse exponent arity")
        require(all(type(power) is int and power >= 0 for power in exponent), "sparse exponent domain")
        require(type(coefficient) is int, "sparse coefficient domain")
        collected[exponent] = collected.get(exponent, 0) + coefficient
    return [
        {"exponents": list(exponent), "coefficient": coefficient}
        for exponent, coefficient in sorted(collected.items())
        if coefficient
    ]


def polynomial(node_id: str, records: list[dict], arity: int = 12) -> dict:
    value = normalize(records, arity)
    return {
        "node_id": node_id,
        "term_count": len(value),
        "sparse_sha256": canonical_digest(value),
        "sparse_polynomial": value,
    }


def derivative(records: list[dict], coordinate: int, arity: int = 12) -> list[dict]:
    answer = []
    for record in records:
        exponent = list(record["exponents"])
        power = exponent[coordinate]
        if power:
            exponent[coordinate] -= 1
            answer.append({"exponents": exponent, "coefficient": power * record["coefficient"]})
    return normalize(answer, arity)


def restrict(records: list[dict], zero_indices: set[int], arity: int = 12) -> list[dict]:
    return normalize(
        [record for record in records if all(record["exponents"][index] == 0 for index in zero_indices)],
        arity,
    )


def multiply(left: list[dict], right: list[dict], arity: int = 12) -> list[dict]:
    answer = []
    for first in left:
        for second in right:
            answer.append({
                "exponents": [a + b for a, b in zip(first["exponents"], second["exponents"])],
                "coefficient": first["coefficient"] * second["coefficient"],
            })
    return normalize(answer, arity)


def scale(records: list[dict], coefficient: int, arity: int = 12) -> list[dict]:
    return normalize([
        {"exponents": record["exponents"], "coefficient": coefficient * record["coefficient"]}
        for record in records
    ], arity)


def add(*polynomials: list[dict], arity: int = 12) -> list[dict]:
    return normalize([record for value in polynomials for record in value], arity)


def substitute_zero(records: list[dict], zero_indices: set[int], arity: int = 12) -> list[dict]:
    return restrict(records, zero_indices, arity)


def sparse_dictionary(records: list[dict], arity: int = 12) -> dict[tuple[int, ...], int]:
    return {
        tuple(record["exponents"]): record["coefficient"]
        for record in normalize(records, arity)
    }


def sparse_records(value: dict[tuple[int, ...], int]) -> list[dict]:
    return normalize([
        {"exponents": list(exponent), "coefficient": coefficient}
        for exponent, coefficient in value.items()
        if coefficient
    ])


def lexicographic_division(dividend: list[dict], divisor: list[dict]) -> tuple[list[dict], list[dict]]:
    """Exact multivariate division by one divisor in lex order a,...,w."""
    pending = sparse_dictionary(dividend)
    divisor_dict = sparse_dictionary(divisor)
    require(divisor_dict, "division by nonzero polynomial")
    divisor_lead = max(divisor_dict)
    divisor_lead_coefficient = divisor_dict[divisor_lead]
    quotient: dict[tuple[int, ...], int] = {}
    remainder: dict[tuple[int, ...], int] = {}
    while pending:
        lead = max(pending)
        lead_coefficient = pending[lead]
        divisible = all(left >= right for left, right in zip(lead, divisor_lead))
        coefficient_divisible = lead_coefficient % divisor_lead_coefficient == 0
        if divisible and coefficient_divisible:
            exponent = tuple(left - right for left, right in zip(lead, divisor_lead))
            coefficient = lead_coefficient // divisor_lead_coefficient
            quotient[exponent] = quotient.get(exponent, 0) + coefficient
            for divisor_exponent, divisor_coefficient in divisor_dict.items():
                target = tuple(left + right for left, right in zip(exponent, divisor_exponent))
                pending[target] = pending.get(target, 0) - coefficient * divisor_coefficient
                if pending[target] == 0:
                    pending.pop(target)
        else:
            remainder[lead] = remainder.get(lead, 0) + lead_coefficient
            pending.pop(lead)
    return sparse_records(quotient), sparse_records(remainder)


def divide_by_coordinate(records: list[dict], coordinate: int) -> list[dict]:
    answer = []
    for record in normalize(records):
        require(record["exponents"][coordinate] >= 1, "coordinate exact divisibility")
        exponent = list(record["exponents"])
        exponent[coordinate] -= 1
        answer.append({"exponents": exponent, "coefficient": record["coefficient"]})
    return normalize(answer)


def term(coefficient: int = 1, **powers: int) -> dict:
    return {
        "exponents": [powers.get(variable, 0) for variable in VARIABLES],
        "coefficient": coefficient,
    }


def affine_dehomogenize(homogeneous: list[dict]) -> list[dict]:
    records = []
    for record in homogeneous:
        records.append({
            "exponents": [record["exponents"][index] for index in AFFINE_TO_HOMOGENEOUS],
            "coefficient": record["coefficient"],
        })
    return normalize(records, 9)


def homogenize(affine: list[dict]) -> list[dict]:
    records = []
    for record in affine:
        source = record["exponents"]
        exponent = [0] * 12
        for affine_index, homogeneous_index in enumerate(AFFINE_TO_HOMOGENEOUS):
            exponent[homogeneous_index] = source[affine_index]
        exponent[3] = 2 - sum(source[index] for index in AFFINE_BLOCKS[0])
        exponent[7] = 2 - sum(source[index] for index in AFFINE_BLOCKS[1])
        exponent[11] = 2 - sum(source[index] for index in AFFINE_BLOCKS[2])
        require(min(exponent) >= 0, "homogenization nonnegative exponents")
        records.append({"exponents": exponent, "coefficient": record["coefficient"]})
    return normalize(records)


def multidegrees(records: list[dict]) -> set[tuple[int, int, int]]:
    return {
        tuple(sum(record["exponents"][index] for index in block) for block in BLOCK_INDICES)
        for record in records
    }


def read_npy_member(npz_path: Path, member: str) -> tuple[dict, bytes]:
    """Read the metadata and raw body of a simple .npy member using stdlib."""
    with zipfile.ZipFile(npz_path) as archive:
        raw = archive.read(member + ".npy")
    require(raw[:6] == b"\x93NUMPY", f"npy magic {member}")
    major, _minor = raw[6], raw[7]
    require(major in (1, 2, 3), f"npy version {member}")
    if major == 1:
        header_length = struct.unpack_from("<H", raw, 8)[0]
        start = 10
    else:
        header_length = struct.unpack_from("<I", raw, 8)[0]
        start = 12
    header = ast.literal_eval(raw[start:start + header_length].decode("latin1"))
    return header, raw[start + header_length:]


def unpack_unsigned_npy(npz_path: Path, member: str) -> tuple[tuple[int, ...], tuple[int, ...]]:
    header, body = read_npy_member(npz_path, member)
    require(header["fortran_order"] is False, f"npy C order {member}")
    descriptor = header["descr"]
    formats = {"<u2": ("<H", 2), "<u4": ("<I", 4), "|u1": ("B", 1)}
    require(descriptor in formats, f"npy unsigned dtype {member}")
    fmt, width = formats[descriptor]
    count = len(body) // width
    require(count * width == len(body), f"npy byte count {member}")
    values = tuple(value[0] for value in struct.iter_unpack(fmt, body))
    shape = tuple(header["shape"])
    expected = 1
    for extent in shape:
        expected *= extent
    require(expected == len(values), f"npy shape {member}")
    return shape, values


def validate_pinned_sources() -> dict:
    for relative, expected in PINNED_INPUTS.items():
        path = ROOT / relative
        require(path.is_file(), f"pinned source exists {relative}")
        require(file_digest(path) == expected, f"pinned source digest {relative}")

    opening = read_json(OPENING)
    require(opening["cycle_id"] == CYCLE_ID, "opening cycle")
    require(opening["base_revision"] == BASE_REVISION and opening["base_tree"] == BASE_TREE, "opening base")
    require(opening["selected_target"] == TARGET and opening["selected_count"] == 1, "opening target")
    require(opening["opening_ledger"] == "2/9", "opening ledger")
    require(opening["target"]["processing_order"] == ["u_v_w", "u_v", "u_w", "v_w", "u", "v", "w"], "opening type order")
    require(opening["target"]["parent_sign_factors"] == 70, "opening parent census")

    canonical = read_json(ROOT / "ai/omreal/data/CANONICAL_RESEARCH_STATE_V6.json")
    require(canonical["format"] == "9dvl-canonical-research-state-v6", "canonical state format")
    require(canonical["theorem"]["score"] == "2/9", "canonical state ledger")
    require(canonical["theorem"]["diagonal_nine"] == "OPEN", "canonical diagonal nine")

    compactification = read_json(ROOT / "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json")
    require(compactification["parent_index"] == 2599, "compactification parent")
    require(compactification["chart_atlas"]["chart_count"] == 64, "compactification charts")
    require(compactification["chart_atlas"]["ordered_transition_count"] == 4096, "compactification transitions including identities")
    require(len(compactification["boundary_divisors"]) == 12, "compactification boundary divisors")

    parent_gate = read_json(ROOT / "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json")
    require(parent_gate["parent_index"] == 2599, "parent gate parent")
    require(parent_gate["nonexcluded_support_face_count"] == 11, "parent gate nonexcluded faces")

    candidates = (ROOT / "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin").read_bytes()
    require(len(candidates) >= 20, "candidate factor header")
    magic, parent, factor_count, candidate_count = struct.unpack_from("<8sIII", candidates)
    require((magic, parent, factor_count, candidate_count) == (b"D3PFC001", 2599, 26740, 17824), "candidate factor header fields")
    ids = tuple(value[0] for value in struct.iter_unpack("<I", candidates[20:]))
    require(len(ids) == candidate_count and ids == tuple(sorted(set(ids))), "candidate factor canonical IDs")
    require(19069 in ids, "factor 19069 candidate membership")

    npz = ROOT / "ai/omreal/data/DIAG9_GRAPH_row2599_factor_states.npz"
    shape, parent_values = unpack_unsigned_npy(npz, "parent_index")
    require(shape == () and parent_values == (2599,), "factor-state parent")
    varied_shape, varied = unpack_unsigned_npy(npz, "varied_factor")
    require(varied_shape == (10844,) and 19069 in varied, "factor-state varied factor membership")

    lines = (ROOT / "ai/omreal/certs_4_8.jsonl").read_text(encoding="utf-8").splitlines()
    require(len(lines) == 2628, "canonical parent record count")
    parent_record = json.loads(lines[2599])
    require(parent_record["n"] == 8 and parent_record["r"] == 4, "row2599 parent rank")
    require(parent_record["verdict"] == "REALIZABLE", "row2599 realizability")
    require(len(parent_record["matrix"]) == 4 and all(len(row) == 8 for row in parent_record["matrix"]), "row2599 matrix shape")

    predecessor_manifest = read_json(ROOT / "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-constructor/SOURCE_MANIFEST.json")
    require(predecessor_manifest["semantic_sha256"] == semantic_digest(predecessor_manifest), "predecessor manifest seal")
    require(predecessor_manifest["source_policy"]["predecessor_builder_code_imported"] is False, "predecessor source policy")
    require(predecessor_manifest["source_policy"]["numerical_or_modular_probe_used"] is False, "predecessor exact policy")

    prior_certificate = read_json(ROOT / "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-certificate/RESULT.json")
    prior_falsifier = read_json(ROOT / "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-falsifier/RESULT.json")
    prior_referee = read_json(ROOT / "ops/team/d9-factor19069-explicit-trihom-jacobian-chart-referee/RESULT.json")
    require(prior_certificate["outcome"] == "pass" and prior_certificate["ledger_delta"] == "0/9", "prior certificate")
    require(prior_falsifier["outcome"] == "pass" and prior_falsifier["theorem_ledger"] == "2/9", "prior falsifier")
    require(prior_referee["verdict"] == "ACCEPT_FAIL_CLOSED_TIMEOUT_FRONTIER", "prior referee")

    return {
        "pin_count": len(PINNED_INPUTS),
        "candidate_factor_count": candidate_count,
        "factor19069_candidate": True,
        "factor19069_varied_state": True,
        "parent_record_count": len(lines),
        "compactification_charts": 64,
        "parent_sign_factors": 70,
    }


def reconstruct_source() -> tuple[dict, list[dict]]:
    predecessor = read_json(PREDECESSOR)
    require(predecessor["semantic_sha256"] == semantic_digest(predecessor), "predecessor frontier seal")
    require(predecessor["outcome"] == "pass", "predecessor outcome")
    require(predecessor["theorem_ledger"] == "2/9", "predecessor ledger")
    require(predecessor["endpoint"] == "HASH_PIN_ALL_COMPLETED_CHART_BRANCHES_AND_FIRST_PENDING_BRANCH", "predecessor endpoint")
    source = predecessor["trihomogeneous_source"]
    require(source["semantic_sha256"] == semantic_digest(source), "predecessor source seal")
    require(source["ring"] == "Q[a,b,c,u,d,e,f,v,g,h,i,w]", "homogeneous ring")
    require(source["multidegree"] == [2, 2, 2], "homogeneous multidegree")
    require(source["term_count"] == 108, "homogeneous source terms")
    require(source["dehomogenization_exact_sparse_equality"] is True, "predecessor dehomogenization flag")
    require(source["affine_source_is_homogeneous"] is False, "false affine homogeneity guard")
    require(source["affine_source_is_multiaffine"] is False, "false affine multiaffinity guard")
    require(source["trihomogenization_is_decomposition_certificate"] is False, "homogenization decomposition guard")
    payload = source["polynomial"]
    require(payload["coordinate_order"] == list(VARIABLES), "source coordinate order")
    homogeneous = normalize(payload["sparse_polynomial"])
    require(homogeneous == payload["sparse_polynomial"], "source canonical order")
    require(len(homogeneous) == payload["term_count"] == 108, "source collected term count")
    require(payload["semantic_sha256"] == semantic_digest(payload), "source polynomial seal")
    require(multidegrees(homogeneous) == {(2, 2, 2)}, "source termwise multidegree")
    affine = affine_dehomogenize(homogeneous)
    require(len(affine) == 108, "affine dehomogenization terms")
    require(homogenize(affine) == homogeneous, "independent trihomogenization equality")
    return predecessor, homogeneous


def reconstruct_atlas(predecessor: dict) -> dict:
    atlas = predecessor["chart_atlas"]
    require(atlas["semantic_sha256"] == semantic_digest(atlas), "predecessor atlas seal")
    require(atlas["standard_chart_count"] == len(atlas["charts"]) == 64, "atlas chart count")
    require(atlas["directed_overlap_record_count"] == 4032, "atlas directed overlaps")
    require(atlas["boundary_stratum_record_count"] == 279, "atlas boundary incidences")
    require(atlas["global_nonempty_boundary_type_count"] == 7, "atlas boundary types")
    require(atlas["all_product_charts_retained"] is True, "atlas chart retention")
    require(atlas["all_available_boundary_strata_retained"] is True, "atlas stratum retention")
    require(atlas["symmetry_quotient_used"] is False, "atlas no symmetry quotient")

    expected_pivots = list(product(*BLOCKS))
    chart_ids = []
    overlap_canonical = []
    type_chart_ids: dict[tuple[str, ...], list[str]] = {boundary_type: [] for boundary_type in TYPE_ORDER}
    for index, (chart, pivots) in enumerate(zip(atlas["charts"], expected_pivots)):
        chart_id = f"JCH-{index:02d}-{'-'.join(pivots)}"
        require(chart["chart_index"] == index and chart["chart_id"] == chart_id, f"chart identity {index}")
        require(chart["pivots"] == list(pivots), f"chart pivots {chart_id}")
        available = [homogenizer for pivot, homogenizer in zip(pivots, HOMOGENIZERS) if pivot != homogenizer]
        require(chart["boundary_homogenizers"] == available, f"chart boundary homogenizers {chart_id}")
        expected_subsets = [
            list(subset)
            for mask in range(1, 8)
            if all(not (mask & (1 << bit)) or HOMOGENIZERS[bit] in available for bit in range(3))
            for subset in [tuple(HOMOGENIZERS[bit] for bit in range(3) if mask & (1 << bit))]
        ]
        require([record["zero_homogenizers"] for record in chart["boundary_strata"]] == expected_subsets, f"chart strata {chart_id}")
        require(len(chart["overlap_records"]) == 63, f"chart overlap count {chart_id}")
        chart_ids.append(chart_id)
        for boundary_type in TYPE_ORDER:
            if set(boundary_type).issubset(available):
                type_chart_ids[boundary_type].append(chart_id)

        stored_by_target = {record["target_chart_id"]: record for record in chart["overlap_records"]}
        require(len(stored_by_target) == 63, f"unique overlap targets {chart_id}")
        for target_index, target_pivots in enumerate(expected_pivots):
            if target_index == index:
                continue
            target_id = f"JCH-{target_index:02d}-{'-'.join(target_pivots)}"
            transitions = []
            required = []
            for block_index, (source_pivot, target_pivot) in enumerate(zip(pivots, target_pivots)):
                if source_pivot != target_pivot:
                    required.append(target_pivot)
                    transitions.append({
                        "block_index": block_index,
                        "source_pivot": source_pivot,
                        "target_pivot": target_pivot,
                        "required_nonzero_source_coordinate": target_pivot,
                        "target_normalization_scale": f"1/{target_pivot}",
                    })
            expected = {
                "target_chart_id": target_id,
                "required_nonzero_coordinates": required,
                "block_transitions": transitions,
                "overlap_status": "EXPLICIT_NONEMPTY_PRINCIPAL_OPEN_WHEN_REQUIREMENTS_HOLD",
            }
            require(stored_by_target[target_id] == expected, f"exact overlap transition {chart_id}->{target_id}")
            overlap_canonical.append({"source_chart_id": chart_id, **expected})

    require(len(set(chart_ids)) == 64, "unique chart IDs")
    counts = {"_".join(boundary_type): len(type_chart_ids[boundary_type]) for boundary_type in TYPE_ORDER}
    require(counts == {"u_v_w": 27, "u_v": 36, "u_w": 36, "v_w": 36, "u": 48, "v": 48, "w": 48}, "type incidence counts")
    require(sum(counts.values()) == 279, "type incidence total")
    return {
        "standard_chart_count": 64,
        "directed_overlap_record_count": 4032,
        "directed_overlap_semantic_sha256": canonical_digest(overlap_canonical),
        "boundary_type_chart_incidence_count": 279,
        "type_incidence_counts": counts,
        "compatible_chart_ids": {"_".join(key): value for key, value in type_chart_ids.items()},
        "deduplication_performed": False,
        "deduplication_policy": "NO_BRANCH_QUOTIENT_WITHOUT_EXPLICIT_INVERTIBLE_OVERLAP_WITNESS",
    }


def lift_affine(records: list[dict]) -> list[dict]:
    lifted = []
    for record in records:
        exponent = [0] * 12
        for affine_index, homogeneous_index in enumerate(AFFINE_TO_HOMOGENEOUS):
            exponent[homogeneous_index] = record["exponents"][affine_index]
        lifted.append({"exponents": exponent, "coefficient": record["coefficient"]})
    return normalize(lifted)


def normalize_sign(records: list[dict]) -> tuple[list[dict], int]:
    value = normalize(records)
    require(value, "sign normalization nonzero polynomial")
    multiplier = 1 if value[0]["coefficient"] > 0 else -1
    return normalize([
        {"exponents": record["exponents"], "coefficient": multiplier * record["coefficient"]}
        for record in value
    ]), multiplier


def deepest_data(restricted: list[dict], normal_derivatives: list[dict], parent_records: list[dict]) -> dict:
    h_factor = [term(h=1)]
    minor = [term(a=1, f=1), term(-1, c=1, d=1)]
    determinant = [
        term(a=1, e=1, i=1),
        term(-1, a=1, f=1, h=1),
        term(-1, b=1, d=1, i=1),
        term(b=1, f=1, g=1),
        term(c=1, d=1, h=1),
        term(-1, c=1, e=1, g=1),
    ]
    factored = multiply(multiply(h_factor, minor), determinant)
    factored = [{"exponents": record["exponents"], "coefficient": -record["coefficient"]} for record in factored]
    factored = normalize(factored)
    require(restricted == factored, "deepest exact factorization")
    require(len(restricted) == 11, "deepest restriction term count")

    # All 2x2 minors are the exact gradient equations of the 3x3 determinant.
    matrix = (("a", "b", "c"), ("d", "e", "f"), ("g", "h", "i"))
    rank_one_minors = []
    for row_pair in combinations(range(3), 2):
        for column_pair in combinations(range(3), 2):
            x = matrix[row_pair[0]][column_pair[0]]
            y = matrix[row_pair[0]][column_pair[1]]
            z = matrix[row_pair[1]][column_pair[0]]
            q = matrix[row_pair[1]][column_pair[1]]
            rank_one_minors.append(polynomial(
                f"minor_{x}{q}_{y}{z}",
                [term(**{x: 1, q: 1}), term(-1, **{y: 1, z: 1})],
            ))
    determinant_derivatives = [derivative(determinant, VARIABLES.index(variable)) for variable in AFFINE_VARIABLES]
    require(
        {canonical_digest(normalize_sign(value)[0]) for value in determinant_derivatives}
        == {canonical_digest(normalize_sign(record["sparse_polynomial"])[0]) for record in rank_one_minors},
        "determinant gradient equals signed rank-one minors",
    )

    factors = [
        {
            **polynomial("UVW-FAC-H", h_factor),
            "equation": "h=0",
            "multidegree": [0, 0, 1],
            "factorization_exponent": 1,
            "projective_product_divisor_dimension": 5,
        },
        {
            **polynomial("UVW-FAC-MINOR", minor),
            "equation": "a*f-c*d=0",
            "multidegree": [1, 1, 0],
            "factorization_exponent": 1,
            "projective_product_divisor_dimension": 5,
        },
        {
            **polynomial("UVW-FAC-DET", determinant),
            "equation": "a*e*i-a*f*h-b*d*i+b*f*g+c*d*h-c*e*g=0",
            "multidegree": [1, 1, 1],
            "factorization_exponent": 1,
            "projective_product_divisor_dimension": 5,
        },
    ]
    require(len(parent_records) == 70, "parent record census at deepest comparison")
    expected_parent_matches = (
        (8, "H_08_1248", h_factor, 1),
        (22, "H_22_1367", minor, -1),
        (34, "H_34_1678", determinant, 1),
    )
    parent_factor_correspondences = []
    for parent_index, parent_node, displayed_factor, exact_multiplier in expected_parent_matches:
        record = parent_records[parent_index]
        require(record["semantic_sha256"] == semantic_digest(record), f"parent factor record seal {parent_node}")
        require(record["factor_index"] == parent_index and record["factor_node_id"] == parent_node, f"parent factor identity {parent_node}")
        lifted = lift_affine(record["sparse_polynomial"])
        exact_expected = normalize([
            {"exponents": item["exponents"], "coefficient": exact_multiplier * item["coefficient"]}
            for item in displayed_factor
        ])
        require(lifted == exact_expected, f"exact parent factor equality {parent_node}")
        normalized_parent, parent_sign = normalize_sign(lifted)
        normalized_displayed, displayed_sign = normalize_sign(displayed_factor)
        require(normalized_parent == normalized_displayed, f"sign-normalized parent factor equality {parent_node}")
        parent_factor_correspondences.append({
            "parent_factor_index": parent_index,
            "parent_factor_node_id": parent_node,
            "deepest_factor_node_id": factors[len(parent_factor_correspondences)]["node_id"],
            "parent_equals_multiplier_times_deepest_factor": exact_multiplier,
            "exact_sparse_equality": True,
            "sign_normalized_sparse_equality": True,
            "parent_sign_normalization_multiplier": parent_sign,
            "deepest_factor_sign_normalization_multiplier": displayed_sign,
            "sign_normalized_sparse_sha256": canonical_digest(normalized_parent),
            "source_parent_record_semantic_sha256": record["semantic_sha256"],
        })
    normal_ids = [record["node_id"] for record in normal_derivatives]
    singular_cover = [
        {
            "branch_id": "UVW-SING-H-MINOR",
            "stratum_equations": ["UVW-FAC-H", "UVW-FAC-MINOR"],
            "stratum_support_dimension": 4,
            "ambient_candidate_additional_equations": normal_ids,
            "ambient_component_dimension_degree_multiplicity": "UNRESOLVED_FAIL_CLOSED",
            "projective_infinity_only": True,
        },
        {
            "branch_id": "UVW-SING-H-DET",
            "stratum_equations": ["UVW-FAC-H", "UVW-FAC-DET"],
            "stratum_support_dimension": 4,
            "ambient_candidate_additional_equations": normal_ids,
            "ambient_component_dimension_degree_multiplicity": "UNRESOLVED_FAIL_CLOSED",
            "projective_infinity_only": True,
        },
        {
            "branch_id": "UVW-SING-MINOR-DET",
            "stratum_equations": ["UVW-FAC-MINOR", "UVW-FAC-DET"],
            "stratum_support_dimension": 4,
            "ambient_candidate_additional_equations": normal_ids,
            "ambient_component_dimension_degree_multiplicity": "UNRESOLVED_FAIL_CLOSED",
            "projective_infinity_only": True,
        },
        {
            "branch_id": "UVW-SING-DET-RANK-LE-1",
            "stratum_equations": [record["node_id"] for record in rank_one_minors],
            "stratum_support_dimension": 2,
            "ambient_candidate_additional_equations": normal_ids,
            "ambient_component_dimension_degree_multiplicity": "UNRESOLVED_FAIL_CLOSED",
            "projective_infinity_only": True,
        },
    ]
    return {
        "restriction_identity": "F|u=v=w=0=-h*(a*f-c*d)*(a*e*i-a*f*h-b*d*i+b*f*g+c*d*h-c*e*g)",
        "restriction_term_count": 11,
        "factors": factors,
        "parent_factor_correspondences": parent_factor_correspondences,
        "deepest_parent_factor_matches_certified": 3,
        "remaining_six_type_parent_factor_matches_certified": 0,
        "factorization_identity_exact": True,
        "factorization_exponents_certified_only_in_displayed_product": True,
        "unsupported_scheme_multiplicity_claim": False,
        "determinant_rank_one_minor_equations": rank_one_minors,
        "stratum_singular_set_cover": singular_cover,
        "stratum_singular_set_identity": "Sing(V(h*minor*det))=V(h,minor) union V(h,det) union V(minor,det) union Sing(det)",
        "stratum_singular_set_theorem_scope": "EXACT_SET_THEORETIC_PRODUCT_RULE_COVER_WITH_SING_MINOR_CONTAINED_IN_V_MINOR_DET",
        "ambient_filter_policy": "INTERSECT_EACH_STRATUM_BRANCH_WITH_RESTRICTED_NORMAL_DERIVATIVES_DF_DU_DF_DV_DF_DW",
        "ambient_component_decomposition_complete": False,
        "first_unresolved_branch": "UVW-SING-H-MINOR:AMBIENT_NORMAL_FILTER_COMPONENT_DECOMPOSITION",
    }


def reconstruct_representation(predecessor: dict, homogeneous: list[dict]) -> dict:
    atlas = reconstruct_atlas(predecessor)
    parent_frontier = predecessor["parent_factor_incidence_frontier"]
    require(parent_frontier["semantic_sha256"] == semantic_digest(parent_frontier), "parent-factor frontier seal")
    require(parent_frontier["ordered_factor_count"] == len(parent_frontier["records"]) == 70, "parent-factor frontier census")
    require(parent_frontier["completed_component_factor_pairs"] == 0, "no inherited component parent tests")
    require(parent_frontier["inverse_variable_discovery_used"] is False, "no inverse-variable discovery")
    homogeneous_derivatives = [derivative(homogeneous, index) for index in range(12)]
    boundary_types = []
    tangent_identity_count = 0
    normal_derivative_count = 0
    deepest_normal = None
    deepest_restricted = None
    for boundary_type in TYPE_ORDER:
        type_id = "_".join(boundary_type)
        zero_indices = {VARIABLES.index(variable) for variable in boundary_type}
        active_variables = [variable for variable in VARIABLES if variable not in boundary_type]
        restricted = restrict(homogeneous, zero_indices)
        tangent_derivatives = []
        normal_derivatives = []
        for coordinate, variable in enumerate(VARIABLES):
            derivative_then_restrict = restrict(homogeneous_derivatives[coordinate], zero_indices)
            if coordinate not in zero_indices:
                restrict_then_derivative = derivative(restricted, coordinate)
                require(restrict_then_derivative == derivative_then_restrict, f"tangent derivative transfer {type_id}:{variable}")
                tangent_derivatives.append(polynomial(f"dF_d{variable}|{type_id}", restrict_then_derivative))
                tangent_identity_count += 1
            else:
                normal_derivatives.append(polynomial(f"dF_d{variable}|{type_id}", derivative_then_restrict))
                normal_derivative_count += 1
        boundary_types.append({
            "type_id": type_id,
            "zero_homogenizers": list(boundary_type),
            "active_variables": active_variables,
            "codimension_in_product": len(boundary_type),
            "compatible_standard_chart_count": atlas["type_incidence_counts"][type_id],
            "compatible_chart_ids": atlas["compatible_chart_ids"][type_id],
            "restricted_source": polynomial(f"F|{type_id}", restricted),
            "tangent_derivatives": tangent_derivatives,
            "normal_derivatives": normal_derivatives,
            "tangent_derivative_transfer_exact": True,
            "ambient_singularity_generator_node_ids": [
                polynomial(f"F|{type_id}", restricted)["node_id"],
                *[record["node_id"] for record in tangent_derivatives],
                *[record["node_id"] for record in normal_derivatives],
            ],
            "stratum_singularity_generator_node_ids": [
                polynomial(f"F|{type_id}", restricted)["node_id"],
                *[record["node_id"] for record in tangent_derivatives],
            ],
            "ambient_and_stratum_singularity_conflated": False,
            "factorization_status": (
                "EXACT_DISPLAYED_THREE_FACTOR_IDENTITY"
                if boundary_type == ("u", "v", "w")
                else "UNRESOLVED_EXACT_POLYNOMIAL_RETAINED"
            ),
        })
        if boundary_type == ("u", "v", "w"):
            deepest_restricted = restricted
            deepest_normal = normal_derivatives
    require(tangent_identity_count == 72, "tangent derivative identity count")
    require(normal_derivative_count == 12, "normal derivative count")
    require(deepest_restricted is not None and deepest_normal is not None, "deepest reconstruction")
    representation = {
        "format": "d9-factor19069-homogenizer-boundary-canonical-representation-v1",
        "coordinate_order": list(VARIABLES),
        "homogeneous_blocks": [list(block) for block in BLOCKS],
        "homogeneous_source": polynomial("F", homogeneous),
        "multidegree": [2, 2, 2],
        "affine_dehomogenization": polynomial("f_19069", affine_dehomogenize(homogeneous), 9),
        "type_processing_order": ["_".join(boundary_type) for boundary_type in TYPE_ORDER],
        "boundary_types": boundary_types,
        "tangent_derivative_transfer_identity_count": tangent_identity_count,
        "restricted_normal_derivative_count": normal_derivative_count,
        "derivative_semantics": {
            "tangent": "d(F|S)/dx=(dF/dx)|S for x not in S",
            "normal": "normal equation is (dF/ds)|S and is not discarded merely because s=0 on S",
            "ambient_and_stratum_singularity_distinguished": True,
        },
        "deepest_type": deepest_data(
            deepest_restricted,
            deepest_normal,
            predecessor["parent_factor_incidence_frontier"]["records"],
        ),
        "atlas_coverage": atlas,
    }
    return seal(representation)


def git(*arguments: str, binary: bool = False):
    value = subprocess.check_output(
        ["git", "-c", f"safe.directory={ROOT.as_posix()}", *arguments],
        cwd=ROOT,
        text=not binary,
    )
    return value if binary else value.strip()


def validate_candidate_pins() -> dict:
    require(git("rev-parse", f"{CANDIDATE_REVISION}^{{commit}}") == CANDIDATE_REVISION, "candidate commit")
    require(git("rev-parse", f"{CANDIDATE_REVISION}^{{tree}}") == CANDIDATE_TREE, "candidate tree")
    for relative, expected in CANDIDATE_PINS.items():
        path = ROOT / relative
        require(path.is_file(), f"candidate input exists {relative}")
        require(file_digest(path) == expected, f"candidate input digest {relative}")
        frozen = git("show", f"{CANDIDATE_REVISION}:{relative}", binary=True)
        require(sha256(frozen).hexdigest() == expected, f"frozen candidate digest {relative}")
        require(path.read_bytes() == frozen, f"candidate worktree drift {relative}")
    return {
        "candidate_revision": CANDIDATE_REVISION,
        "candidate_tree": CANDIDATE_TREE,
        "candidate_pin_count": len(CANDIDATE_PINS),
        "constructor_frontier_sha256": CANDIDATE_PINS["ops/team/d9-factor19069-homogenizer-boundary-constructor/HOMOGENIZER_BOUNDARY_TYPE_FRONTIER.json"],
    }


def validate_constructor_polynomial(candidate: dict, expected: list[dict], marker: str) -> str:
    require(len(candidate["semantic_sha256"]) == 64, f"candidate polynomial semantic tag {marker}")
    require(candidate["coefficient_field"] == "Q", f"candidate coefficient field {marker}")
    require(candidate["coordinate_order"] == list(VARIABLES), f"candidate coordinate order {marker}")
    value = normalize(candidate["sparse_polynomial"])
    require(value == candidate["sparse_polynomial"], f"candidate canonical sparse order {marker}")
    require(candidate["term_count"] == len(value), f"candidate term count {marker}")
    require(value == normalize(expected), f"candidate sparse equality {marker}")
    return candidate["semantic_sha256"]


def independent_type_derivatives(record: dict) -> tuple[dict[str, list[dict]], dict[str, list[dict]]]:
    tangent = {}
    normal = {}
    for item in record["tangent_derivatives"]:
        variable = item["node_id"].split("dF_d", 1)[1].split("|", 1)[0]
        tangent[variable] = item["sparse_polynomial"]
    for item in record["normal_derivatives"]:
        variable = item["node_id"].split("dF_d", 1)[1].split("|", 1)[0]
        normal[variable] = item["sparse_polynomial"]
    return tangent, normal


def compare_constructor_candidate(reconstruction: dict) -> dict:
    frozen = validate_candidate_pins()
    representation = reconstruction["canonical_boundary_representation"]
    frontier = read_json(CONSTRUCTOR_FRONTIER)
    manifest = read_json(CONSTRUCTOR_MANIFEST)
    result = read_json(CONSTRUCTOR_RESULT)

    require(frontier["semantic_sha256"] == "70d980c28c536dd10a679ac086939fadcf78722dd68839658062948c1e0dd5ec", "candidate frontier semantic identity")
    require(frontier["format"] == "d9-factor19069-homogenizer-boundary-type-constructor-frontier-v1", "candidate frontier format")
    require(frontier["cycle_id"] == CYCLE_ID, "candidate cycle")
    require(frontier["base_revision"] == BASE_REVISION and frontier["base_tree"] == BASE_TREE, "candidate base")
    require(frontier["opening_revision"] == "aad8e1efa5a45e47c9f924dce5263a07996a10e9", "candidate opening")
    require(frontier["outcome"] == "pass" and frontier["theorem_ledger"] == "2/9", "candidate outcome and ledger")
    require(frontier["boundary_type_order"] == representation["type_processing_order"], "candidate type order")
    require(frontier["boundary_type_count"] == len(frontier["boundary_type_records"]) == 7, "candidate type count")
    require(frontier["boundary_stratum_chart_incidence_count"] == 279, "candidate incidence total")

    require(manifest["semantic_sha256"] == "3ca47972a9458a8cb044f2da8a01f11e823d14d0344f9d092054a2cd9732d790", "candidate manifest semantic identity")
    require(manifest["source_policy"]["predecessor_json_is_only_polynomial_source"] is True, "candidate polynomial source policy")
    require(manifest["source_policy"]["numerical_or_modular_probe_used"] is False, "candidate exact source policy")
    require(manifest["source_policy"]["whole_atlas_groebner_retry_used"] is False, "candidate retired route guard")
    require(manifest["source_policy"]["unsupported_overlap_quotient_used"] is False, "candidate overlap policy")

    independent_types = {record["type_id"]: record for record in representation["boundary_types"]}
    type_comparisons = []
    tangent_checks = 0
    normal_checks = 0
    for index, candidate_type in enumerate(frontier["boundary_type_records"]):
        require(len(candidate_type["semantic_sha256"]) == 64, f"candidate type semantic tag {index}")
        type_id = representation["type_processing_order"][index]
        independent = independent_types[type_id]
        require(candidate_type["type_index"] == index and candidate_type["type_id"] == type_id, f"candidate type identity {type_id}")
        require(candidate_type["zero_homogenizers"] == independent["zero_homogenizers"], f"candidate type zeros {type_id}")
        validate_constructor_polynomial(candidate_type["restricted_source"], independent["restricted_source"]["sparse_polynomial"], f"restricted source {type_id}")
        tangent, normal = independent_type_derivatives(independent)
        ambient = candidate_type["ambient_singularity"]
        require(ambient["definition"] == "RESTRICT_ALL_TWELVE_PARTIALS_OF_FULL_F_AFTER_DIFFERENTIATION", f"ambient definition {type_id}")
        require(ambient["derivative_count"] == len(ambient["restricted_derivatives"]) == 12, f"ambient derivative count {type_id}")
        candidate_ambient = {item["variable"]: item["polynomial"] for item in ambient["restricted_derivatives"]}
        require(set(candidate_ambient) == set(VARIABLES), f"ambient derivative variables {type_id}")
        for variable, expected in {**tangent, **normal}.items():
            validate_constructor_polynomial(candidate_ambient[variable], expected, f"ambient derivative {type_id}:{variable}")
        normal_checks += len(normal)

        stratum = candidate_type["stratum_singularity"]
        require(stratum["definition"] == "DIFFERENTIATE_RESTRICTED_SOURCE_ONLY_IN_TANGENT_COORDINATES", f"stratum definition {type_id}")
        require(stratum["normal_derivatives_are_not_stratum_generators"] is True, f"normal distinction {type_id}")
        require(stratum["tangent_transfer_exact_sparse_equality"] is True, f"tangent transfer flag {type_id}")
        require(stratum["tangent_variables"] == list(tangent), f"tangent variable order {type_id}")
        require(stratum["derivative_count"] == len(stratum["derivatives"]) == len(tangent), f"stratum derivative count {type_id}")
        candidate_tangent = {item["variable"]: item["polynomial"] for item in stratum["derivatives"]}
        require(set(candidate_tangent) == set(tangent), f"stratum derivative variables {type_id}")
        for variable, expected in tangent.items():
            validate_constructor_polynomial(candidate_tangent[variable], expected, f"stratum derivative {type_id}:{variable}")
            tangent_checks += 1

        require(candidate_type["chart_incidence_count"] == len(candidate_type["chart_incidences"]) == independent["compatible_standard_chart_count"], f"chart incidence count {type_id}")
        require([item["chart_id"] for item in candidate_type["chart_incidences"]] == independent["compatible_chart_ids"], f"chart incidence IDs {type_id}")
        for incidence in candidate_type["chart_incidences"]:
            require(incidence["zero_homogenizers"] == independent["zero_homogenizers"], f"incidence zeros {type_id}")
            require(incidence["chart_id"] == f"JCH-{incidence['chart_index']:02d}-{'-'.join(incidence['pivots'])}", f"incidence chart identity {type_id}")
        require(candidate_type["overlap_deduplication"] == {
            "overlap_unit_certificates": [],
            "representatives_quotiented": 0,
            "status": "NO_DEDUPLICATION_PERFORMED_OR_CLAIMED",
        }, f"candidate no type deduplication {type_id}")
        type_comparisons.append({
            "type_id": type_id,
            "restricted_source_semantic_sha256": candidate_type["restricted_source"]["semantic_sha256"],
            "restricted_source_term_count": candidate_type["restricted_source"]["term_count"],
            "ambient_derivatives_compared": 12,
            "tangent_derivatives_compared": len(tangent),
            "normal_derivatives_compared": len(normal),
            "chart_incidences_compared": candidate_type["chart_incidence_count"],
            "nondeepest_factor_records_certified": 0,
        })
    require(tangent_checks == 72 and normal_checks == 12, "candidate derivative comparison census")

    deepest_independent = representation["deepest_type"]
    deepest = frontier["deepest_branch_frontier"]
    factorization = deepest["factorization"]
    h = deepest_independent["factors"][0]["sparse_polynomial"]
    minor = deepest_independent["factors"][1]["sparse_polynomial"]
    determinant = deepest_independent["factors"][2]["sparse_polynomial"]
    validate_constructor_polynomial(factorization["h"], h, "deepest h")
    validate_constructor_polynomial(factorization["L"], minor, "deepest L")
    validate_constructor_polynomial(factorization["C"], determinant, "deepest C")
    require(factorization["identity"] == "F|u=v=w=0=-h*L*C" and factorization["exact_sparse_identity"] is True, "candidate deepest identity")
    require(factorization["factor_irreducibility_asserted"] is False and factorization["scheme_multiplicity_asserted"] is False, "candidate deepest invariant restraint")
    require(factorization["entire_deepest_source_excluded_from_strict_parent"] is True, "candidate deepest parent exclusion")
    require([item["parent_factor_node_id"] for item in factorization["parent_factor_matches"]] == ["H_08_1248", "H_22_1367", "H_34_1678"], "candidate deepest parent records")

    cover = deepest["stratum_singular_set_cover"]
    require(cover == {
        "identity": "Sing(h*L*C)=V(h,L) union V(h,C) union V(L,C) union Sing(L) union Sing(C)",
        "scope": "SET_THEORETIC_COVER_IN_CHARACTERISTIC_ZERO;_NO_PRIMARY_DECOMPOSITION_CLAIM",
        "seed_count": 5,
    }, "candidate five-seed cover")
    processed = deepest["processed_seed"]
    queued = deepest["queued_seed_branches"]
    require(len(processed["semantic_sha256"]) == 64, "processed seed semantic tag")
    require([processed["branch_id"], *[item["branch_id"] for item in queued]] == [
        "B-UVW-01-h-L",
        "B-UVW-02-h-C",
        "B-UVW-03-L-C",
        "B-UVW-04-SingL",
        "B-UVW-05-SingC",
    ], "candidate five seed IDs")
    require(len(processed["equations"]) == 2, "processed seed equation count")
    validate_constructor_polynomial(processed["equations"][0], h, "processed seed h")
    validate_constructor_polynomial(processed["equations"][1], minor, "processed seed L")
    require(processed["strict_parent_exclusion"]["parent_factor_node_ids"] == ["H_08_1248", "H_22_1367"], "processed seed parent exclusion")
    for item in queued:
        require(len(item["semantic_sha256"]) == 64, f"queued seed semantic tag {item['branch_id']}")
        require(item["status"] == "COMPLETED_PROJECTIVE_INFINITY_AND_STRICT_PARENT_EXCLUSION", f"queued seed status {item['branch_id']}")
        require(item["strict_parent_exclusion"]["status"] == "PROVED", f"queued seed parent exclusion {item['branch_id']}")
    require(queued[0]["equations"] == ["h", "C"] and queued[0]["strict_parent_exclusion"]["parent_factor_node_ids"] == ["H_08_1248", "H_34_1678"], "seed h C")
    require(queued[1]["equations"] == ["a*f-c*d", "C"] and queued[1]["strict_parent_exclusion"]["parent_factor_node_ids"] == ["H_22_1367", "H_34_1678"], "seed L C")
    require(queued[2]["equations"] == ["a", "c", "d", "f"] and queued[2]["strict_parent_exclusion"]["parent_factor_node_ids"] == ["H_22_1367"], "seed SingL")
    require(queued[3]["equations"] == ["ALL_NINE_2x2_MINORS_OF_MATRIX_[[a,b,c],[d,e,f],[g,h,i]]"] and queued[3]["strict_parent_exclusion"]["parent_factor_node_ids"] == ["H_34_1678"], "seed SingC")
    singular_minor_zero = {VARIABLES.index(variable) for variable in ("a", "c", "d", "f")}
    require(substitute_zero(minor, singular_minor_zero) == [] and substitute_zero(determinant, singular_minor_zero) == [], "independent SingL containment in V(L,C)")
    require(len(deepest_independent["determinant_rank_one_minor_equations"]) == 9, "independent SingC minor census")
    require(deepest["completed_source_factor_seed_count"] == 5 and deepest["type_classification"] == "COMPLETE_PROJECTIVE_INFINITY_AND_STRICT_PARENT_EXCLUSION", "candidate deepest completion")

    deepest_type = independent_types["u_v_w"]
    _tangent, deepest_normal = independent_type_derivatives(deepest_type)
    normal_transfer = processed["ambient_normal_transfer"]
    _nu_quotient, nu_remainder = lexicographic_division(deepest_normal["u"], h)
    require(nu_remainder == [], "independent dF_du in ideal h")
    h_minor = multiply(h, minor)
    _nv_quotient, nv_remainder = lexicographic_division(deepest_normal["v"], h_minor)
    require(nv_remainder == [], "independent dF_dv in ideal hL")
    require(normal_transfer["dF_du"] == "ZERO_MOD_h_L_BY_EXACT_FACTOR_h", "candidate dF_du identity label")
    require(normal_transfer["dF_dv"] == "ZERO_MOD_h_L_BY_EXACT_FACTOR_h_L", "candidate dF_dv identity label")
    nw_quotient, nw_remainder = lexicographic_division(deepest_normal["w"], minor)
    validate_constructor_polynomial(normal_transfer["dF_dw_quotient_by_L"], nw_quotient, "deepest dF_dw quotient")
    validate_constructor_polynomial(normal_transfer["dF_dw_remainder"], nw_remainder, "deepest dF_dw remainder")
    q_independent = divide_by_coordinate(nw_remainder, VARIABLES.index("e"))
    require(normalize(multiply([term(e=1)], q_independent)) == normalize(nw_remainder), "independent remainder eQ")
    require(normal_transfer["identity"] == "dF_dw = (QUO-Nw-by-L)*L + e*Q", "candidate normal identity label")
    require(add(multiply(nw_quotient, minor), nw_remainder, arity=12) == normalize(deepest_normal["w"]), "independent normal remainder identity")
    children = processed["ambient_children"]
    require(processed["ambient_cover_identity"] == "V(h,L,e*Q)=V(h,L,e) union V(h,L,Q)", "candidate ambient child cover identity")
    require(deepest["completed_ambient_child_count"] == len(children) == 2, "candidate ambient child count")
    for child in children:
        require(len(child["semantic_sha256"]) == 64, f"ambient child semantic tag {child['branch_id']}")
        require(child["projective_infinity_only"] is True and child["parent_factor_tests_required"] == 0, f"ambient child projective scope {child['branch_id']}")
        require(child["parent_exclusion"] == ["H_08_1248", "H_22_1367"], f"ambient child parent exclusion {child['branch_id']}")
    require(children[0]["branch_id"] == "B-UVW-01a-h-L-e" and children[0]["equations"] == ["h", "a*f-c*d", "e"], "candidate e child")
    require(substitute_zero(minor, {VARIABLES.index("e"), VARIABLES.index("h")}) == normalize(minor), "independent e child nonzero divisor equation")
    require(children[0]["dimension"] == 3 and children[0]["degree"] is None and children[0]["multiplicity"] is None, "candidate e child invariants")
    require(children[1]["branch_id"] == "B-UVW-01b-h-L-Q" and children[1]["equations"] == ["h", "a*f-c*d", "Q"], "candidate Q child")
    validate_constructor_polynomial(children[1]["Q"], q_independent, "candidate child Q")
    require(children[1]["dimension"] is None and children[1]["degree"] is None and children[1]["multiplicity"] is None, "candidate Q child invariants fail closed")

    uv = frontier["u_v_branch_frontier"]
    require(uv["completed_known_branch_count"] == len(uv["completed_known_branches"]) == 1, "candidate uv known branch count")
    uv_branch = uv["completed_known_branches"][0]
    require(uv_branch["semantic_sha256"] == "f5bc2dcb0047f494f420a8383ce0aedf9d369af5588ed27848577f5c7ad22097", "candidate uv branch semantic identity")
    require(uv_branch["branch_id"] == "B-UV-00-linear-P3-family", "candidate uv branch ID")
    require(uv_branch["global_homogeneous_equations"] == ["u", "v", "b", "c", "e", "f"], "candidate uv family equations")
    uv_zero = {VARIABLES.index(variable) for variable in ("u", "v", "b", "c", "e", "f")}
    uv_independent = independent_types["u_v"]
    uv_tangent, uv_normal = independent_type_derivatives(uv_independent)
    require(substitute_zero(uv_independent["restricted_source"]["sparse_polynomial"], uv_zero) == [], "independent uv family source vanishing")
    for variable, value in {**uv_tangent, **uv_normal}.items():
        require(substitute_zero(value, uv_zero) == [], f"independent uv family derivative vanishing {variable}")
    require(uv_branch["ambient_singular_membership"] == "ALL_TWELVE_RESTRICTED_FULL_DERIVATIVES_SUBSTITUTE_TO_EXACT_ZERO", "candidate uv ambient membership")
    require(uv_branch["dimension"] == 3 and uv_branch["degree"] == 1 and uv_branch["multiplicity"] is None, "candidate uv exact invariants")
    require(uv_branch["standard_chart_witness"] == {
        "fixed_zero_coordinates": ["u", "v", "b", "c", "e", "f"],
        "free_parameters": ["g", "h", "i"],
        "pivot_values": {"a": 1, "d": 1, "w": 1},
        "pivots": ["a", "d", "w"],
    }, "candidate uv chart witness")
    h22 = scale(minor, -1)
    require(substitute_zero(h22, uv_zero) == [], "independent uv H22 exclusion")
    require(uv_branch["strict_parent_exclusion"]["parent_factor_node_id"] == "H_22_1367" and uv_branch["strict_parent_exclusion"]["status"] == "PROVED", "candidate uv H22 exclusion")
    require(uv["component_completeness_proved"] is False, "candidate uv completeness fail closed")

    pending = frontier["first_pending_branch"]
    expected_pending = {
        "ambient_equation_count": 12,
        "ambient_equation_node_ids": [f"AD-1-{variable}" for variable in VARIABLES],
        "branch_id": "B-UV-01-unclassified-ambient-components",
        "completed_known_branch_semantic_sha256": uv_branch["semantic_sha256"],
        "factorization_status": "NO_NONTRIVIAL_FACTOR_IDENTITY_ASSERTED",
        "known_branch_exhausts_ambient_ideal": False,
        "restricted_source_semantic_sha256": frontier["boundary_type_records"][1]["restricted_source"]["semantic_sha256"],
        "status": "FIRST_SOURCE_PINNED_UNRESOLVED_BRANCH_FAIL_CLOSED",
        "stratum_equation_count": 10,
        "type_id": "u_v",
        "unresolved_obligations": [
            "CHARACTERISTIC_ZERO_AMBIENT_COMPONENT_CENSUS",
            "AMBIENT_COMPONENT_CLOSURE_VERSUS_STRATUM_ONLY_BRANCH",
            "EXPLICIT_OVERLAP_UNIT_DEDUPLICATION_IF_ANY",
            "EXACT_AFFINE_PULLBACK_BEFORE_PARENT_TESTS",
            "ALL_70_PARENT_FACTOR_TESTS_FOR_ANY_ACCEPTED_AFFINE_PULLBACK",
        ],
    }
    require(pending == {**expected_pending, "semantic_sha256": "2747fcc6923b44996bfe79c0d06d2f88169f9fedea465cdecaa3c104bcf6b8b5"}, "candidate pending branch exact record")
    require(uv["first_pending_branch_id"] == pending["branch_id"] and uv["first_pending_branch_semantic_sha256"] == pending["semantic_sha256"], "candidate uv pending binding")

    require(frontier["overlap_accounting"] == {
        "explicit_overlap_unit_certificates": 0,
        "inherited_directed_overlap_records": 4032,
        "representatives_quotiented": 0,
        "unsupported_deduplications": 0,
    }, "candidate overlap fail-closed accounting")
    require(frontier["parent_factor_frontier"] == {
        "accepted_affine_branch_count": 0,
        "completed_branch_parent_factor_pairs": 0,
        "ordered_parent_factor_count": 70,
        "policy": "PULLBACK_TO_AFFINE_SINGULAR_IDEAL_BEFORE_ALL_70_PARENT_TESTS",
        "source_semantic_sha256": "442c422ca3bd9e80f57f3055b5214fb3eba0f9f91f937f7c0496f497d9aba18a",
        "status": "NO_AFFINE_BRANCH_ACCEPTED;PROJECTIVE_ONLY_CHILD_REQUIRES_ZERO_PARENT_TESTS;FIRST_PENDING_PRESERVED_FAIL_CLOSED",
    }, "candidate parent frontier fail closed")
    require(frontier["classification"] == "DEEPEST_TYPE_EXCLUDED_BY_PINNED_PARENT_FACTORS_THEN_FIRST_u_v_BRANCH_UNRESOLVED_FAIL_CLOSED", "candidate classification")
    require(frontier["endpoint"] == "FIRST_SOURCE_PINNED_UNRESOLVED_TYPE_OR_BRANCH_CLASSIFICATION", "candidate endpoint")
    require(frontier["ledger_change_recommended"] == "none", "candidate ledger recommendation")
    expected_nonconsequences = [
        "NO_COMPLETE_SEVEN_TYPE_BRANCH_CLASSIFICATION",
        "NO_COMPLETE_CHARACTERISTIC_ZERO_COMPONENT_CENSUS",
        "NO_UNSUPPORTED_RADICALITY_DEGREE_OR_MULTIPLICITY_CLAIM",
        "NO_OVERLAP_DEDUPLICATION",
        "NO_ACCEPTED_AFFINE_SINGULAR_BRANCH",
        "NO_70_PARENT_FACTOR_CENSUS_FOR_AN_AFFINE_BRANCH",
        "NO_STRICT_REAL_RESIDENCE_OR_CONNECTED_PARENT_TAG",
        "NO_THEOREM_LEVEL_COUNTEREXAMPLE",
        "NO_DIAGONAL_9_PROOF_OR_COUNTEREXAMPLE",
        "NO_9DVL_SCORE_CHANGE",
    ]
    require(frontier["nonconsequences"] == result["nonconsequences"] == expected_nonconsequences, "candidate nonconsequences")
    require(result["outcome"] == "pass" and result["theorem_ledger"] == "2/9", "candidate result outcome")
    require(result["first_pending_branch_id"] == pending["branch_id"] and result["first_pending_branch_semantic_sha256"] == pending["semantic_sha256"], "candidate result pending binding")
    require(result["accepted_affine_branch_count"] == 0 and result["completed_affine_branch_parent_factor_pairs"] == 0, "candidate result affine fail closed")

    return seal({
        "format": "d9-factor19069-homogenizer-boundary-certificate-candidate-comparison-v1",
        "cycle_id": CYCLE_ID,
        "track_id": TRACK_ID,
        **frozen,
        "constructor_frontier_semantic_sha256": frontier["semantic_sha256"],
        "constructor_manifest_sha256": CANDIDATE_PINS["ops/team/d9-factor19069-homogenizer-boundary-constructor/SOURCE_MANIFEST.json"],
        "constructor_manifest_semantic_sha256": manifest["semantic_sha256"],
        "constructor_result_sha256": CANDIDATE_PINS["ops/team/d9-factor19069-homogenizer-boundary-constructor/RESULT.json"],
        "independent_reconstruction_semantic_sha256": reconstruction["semantic_sha256"],
        "comparison_policy": {
            "constructor_code_imported": False,
            "constructor_acceptance_logic_imported": False,
            "frozen_constructor_data_only": True,
            "exact_sparse_field_comparison": True,
            "candidate_semantic_tags_validated_by_frozen_file_hash_and_cross_binding": True,
            "numerical_modular_or_sampled_inference_used": False,
        },
        "type_comparisons": type_comparisons,
        "accepted_candidate_scope": {
            "restricted_sources_compared": 7,
            "ambient_derivatives_compared": 84,
            "tangent_derivative_identities_compared": tangent_checks,
            "normal_derivatives_compared": normal_checks,
            "chart_incidences_compared": 279,
            "deepest_factor_records_compared": 3,
            "nondeepest_factor_records_certified": 0,
            "deepest_set_theoretic_seed_cover_size": 5,
            "deepest_ambient_children_compared": 2,
            "u_v_linear_P3_family_all_derivatives_zero": True,
            "u_v_linear_P3_dimension": 3,
            "u_v_linear_P3_degree": 1,
            "u_v_linear_P3_excluded_by": "H_22_1367",
            "residual_branch_id": pending["branch_id"],
            "residual_branch_semantic_sha256": pending["semantic_sha256"],
            "complete_seven_type_component_classification": False,
            "accepted_affine_branch_count": 0,
            "overlap_representatives_quotiented": 0,
            "universal_diagonal_certificate": False,
        },
        "classification": "ACCEPT_FROZEN_CONSTRUCTOR_EXACT_PARTIAL_FRONTIER_FAIL_CLOSED_NULL",
        "endpoint": "FIRST_SOURCE_PINNED_UNRESOLVED_TYPE_OR_BRANCH_CLASSIFICATION",
        "ledger_delta": "0/9",
        "nonconsequences": expected_nonconsequences,
    })


def reconstruct_all() -> tuple[dict, dict, dict, dict]:
    source_census = validate_pinned_sources()
    predecessor, homogeneous = reconstruct_source()
    representation = reconstruct_representation(predecessor, homogeneous)
    reconstruction = seal({
        "format": "d9-factor19069-homogenizer-boundary-certificate-source-reconstruction-v1",
        "cycle_id": CYCLE_ID,
        "track_id": TRACK_ID,
        "base_revision": BASE_REVISION,
        "base_tree": BASE_TREE,
        "opening_revision": OPENING_REVISION,
        "opening_tree": OPENING_TREE,
        "pins": dict(sorted(PINNED_INPUTS.items())),
        "source_policy": {
            "constructor_code_imported": False,
            "constructor_acceptance_imported": False,
            "falsifier_code_imported": False,
            "predecessor_certificate_code_imported": False,
            "network_or_connector_used": False,
            "numerical_modular_or_sampled_inference_used": False,
            "stdlib_exact_sparse_integer_arithmetic": True,
            "sympy_dependency": False,
        },
        "pinned_source_census": source_census,
        "canonical_boundary_representation": representation,
    })
    comparison = compare_constructor_candidate(reconstruction)
    certificate = seal({
        "format": "d9-factor19069-homogenizer-boundary-certificate-v1",
        "cycle_id": CYCLE_ID,
        "track_id": TRACK_ID,
        "canonical_boundary_representation_semantic_sha256": representation["semantic_sha256"],
        "candidate_comparison_semantic_sha256": comparison["semantic_sha256"],
        "accepted_scope": {
            "source_terms": 108,
            "trihomogeneous_multidegree": [2, 2, 2],
            "seven_restricted_sources": True,
            "tangent_derivative_transfer_identities": 72,
            "restricted_normal_derivatives": 12,
            "ambient_stratum_distinction": True,
            "deepest_11_term_factorization": True,
            "deepest_set_theoretic_stratum_singular_cover": True,
            "deepest_five_seed_product_rule_cover": True,
            "deepest_parent_factor_sparse_matches": 3,
            "remaining_six_type_parent_factor_matches": 0,
            "standard_charts": 64,
            "directed_overlap_records": 4032,
            "boundary_type_chart_incidences": 279,
            "explicit_overlap_atlas_replayed": True,
            "frozen_constructor_candidate_compared": True,
            "deepest_ambient_children_compared": 2,
            "u_v_linear_P3_family_certified": True,
            "u_v_linear_P3_dimension": 3,
            "u_v_linear_P3_degree": 1,
            "u_v_linear_P3_parent_exclusion": "H_22_1367",
            "first_unresolved_branch": "B-UV-01-unclassified-ambient-components",
            "first_unresolved_branch_semantic_sha256": "2747fcc6923b44996bfe79c0d06d2f88169f9fedea465cdecaa3c104bcf6b8b5",
            "branch_overlap_deduplication_performed": False,
            "ambient_component_decomposition_complete": False,
            "affine_pullback_classifications_complete": False,
            "all_70_parent_factor_classifications_complete": False,
            "strict_real_residence_complete": False,
            "connected_parent_tags_complete": False,
            "universal_diagonal_certificate": False,
        },
        "endpoint_accounting": {
            "positive": False,
            "negative": False,
            "null": True,
            "timeout": False,
            "first_unresolved_branch": "B-UV-01-unclassified-ambient-components",
        },
        "classification": "ACCEPT_FROZEN_CONSTRUCTOR_EXACT_PARTIAL_FRONTIER_FAIL_CLOSED_NULL",
        "ledger_before": "2/9",
        "ledger_after": "2/9",
        "ledger_delta": "0/9",
    })
    result = seal({
        "format": "d9-factor19069-homogenizer-boundary-certificate-result-v1",
        "cycle_id": CYCLE_ID,
        "track_id": TRACK_ID,
        "outcome": "pass",
        "classification": certificate["classification"],
        "endpoint": "FIRST_SOURCE_PINNED_UNRESOLVED_TYPE_OR_BRANCH_CLASSIFICATION",
        "positive_endpoint_reached": False,
        "negative_endpoint_reached": False,
        "null_endpoint_reached": True,
        "timeout_endpoint_reached": False,
        "first_unresolved_branch": certificate["endpoint_accounting"]["first_unresolved_branch"],
        "source_reconstruction_semantic_sha256": reconstruction["semantic_sha256"],
        "canonical_boundary_representation_semantic_sha256": representation["semantic_sha256"],
        "candidate_comparison_semantic_sha256": comparison["semantic_sha256"],
        "candidate_revision": CANDIDATE_REVISION,
        "candidate_tree": CANDIDATE_TREE,
        "candidate_comparison_policy": comparison["comparison_policy"],
        "constructor_frontier_sha256": comparison["constructor_frontier_sha256"],
        "constructor_frontier_semantic_sha256": comparison["constructor_frontier_semantic_sha256"],
        "boundary_certificate_semantic_sha256": certificate["semantic_sha256"],
        "certificate_gates": certificate["accepted_scope"],
        "hostile_tests": {"required": 24, "run": 0, "rejected": 0},
        "ledger_before": "2/9",
        "ledger_after": "2/9",
        "ledger_delta": "0/9",
        "ledger_change_recommended": "none",
        "nonconsequences": [
            "NO_COMPLETE_SEVEN_TYPE_BRANCH_CLASSIFICATION",
            "NO_COMPLETE_CHARACTERISTIC_ZERO_COMPONENT_CENSUS",
            "NO_UNSUPPORTED_RADICALITY_DEGREE_OR_MULTIPLICITY_CLAIM",
            "NO_OVERLAP_DEDUPLICATION",
            "NO_ACCEPTED_AFFINE_SINGULAR_BRANCH",
            "NO_70_PARENT_FACTOR_CENSUS_FOR_AN_AFFINE_BRANCH",
            "NO_STRICT_REAL_RESIDENCE_OR_CONNECTED_PARENT_TAG",
            "NO_THEOREM_LEVEL_COUNTEREXAMPLE",
            "NO_DIAGONAL_9_PROOF_OR_COUNTEREXAMPLE",
            "NO_9DVL_SCORE_CHANGE",
        ],
    })
    return reconstruction, comparison, certificate, result


def validate_reconstruction(candidate: dict, expected: dict) -> None:
    require(candidate.get("semantic_sha256") == semantic_digest(candidate), "reconstruction semantic seal")
    require(candidate == expected, "reconstruction exact canonical equality")


def validate_candidate_comparison(candidate: dict, expected: dict) -> None:
    require(candidate.get("semantic_sha256") == semantic_digest(candidate), "candidate comparison semantic seal")
    require(candidate == expected, "candidate comparison exact equality")
    scope = candidate["accepted_candidate_scope"]
    require(scope["restricted_sources_compared"] == 7, "comparison restricted sources")
    require(scope["ambient_derivatives_compared"] == 84, "comparison ambient derivatives")
    require(scope["tangent_derivative_identities_compared"] == 72, "comparison tangent identities")
    require(scope["normal_derivatives_compared"] == 12, "comparison normal derivatives")
    require(scope["deepest_set_theoretic_seed_cover_size"] == 5, "comparison five seeds")
    require(scope["u_v_linear_P3_family_all_derivatives_zero"] is True, "comparison uv derivative vanishing")
    require(scope["complete_seven_type_component_classification"] is False, "comparison completeness fail closed")
    require(scope["accepted_affine_branch_count"] == 0, "comparison affine count fail closed")
    require(scope["overlap_representatives_quotiented"] == 0, "comparison no overlap quotient")
    require(scope["universal_diagonal_certificate"] is False, "comparison universal gate fail closed")
    require(candidate["ledger_delta"] == "0/9", "comparison ledger delta")


def validate_certificate(candidate: dict, expected: dict) -> None:
    require(candidate.get("semantic_sha256") == semantic_digest(candidate), "certificate semantic seal")
    require(candidate == expected, "certificate exact fail-closed equality")
    scope = candidate["accepted_scope"]
    require(scope["branch_overlap_deduplication_performed"] is False, "no overlap quotient without branch witnesses")
    require(scope["ambient_component_decomposition_complete"] is False, "ambient decomposition fail closed")
    require(scope["affine_pullback_classifications_complete"] is False, "affine pullback fail closed")
    require(scope["all_70_parent_factor_classifications_complete"] is False, "parent incidence fail closed")
    require(scope["strict_real_residence_complete"] is False, "real residence fail closed")
    require(scope["connected_parent_tags_complete"] is False, "parent tag fail closed")
    require(scope["universal_diagonal_certificate"] is False, "universal gate fail closed")
    require(candidate["ledger_delta"] == "0/9", "certificate ledger delta")


def validate_result(candidate: dict, expected: dict, hostile_count: int | None = None) -> None:
    require(candidate.get("semantic_sha256") == semantic_digest(candidate), "result semantic seal")
    comparison = deepcopy(candidate)
    canonical = deepcopy(expected)
    if hostile_count is not None:
        canonical["hostile_tests"] = {"required": 24, "run": hostile_count, "rejected": hostile_count}
        canonical = seal({key: value for key, value in canonical.items() if key != "semantic_sha256"})
    require(comparison == canonical, "result exact equality")
    require(candidate["positive_endpoint_reached"] is False, "positive endpoint fail closed")
    require(candidate["negative_endpoint_reached"] is False, "negative endpoint fail closed")
    require(candidate["null_endpoint_reached"] is True, "null endpoint retained")
    require(candidate["timeout_endpoint_reached"] is False, "no false timeout")
    require(candidate["ledger_delta"] == "0/9", "result ledger delta")


def run_hostile_tests(reconstruction: dict, comparison: dict, certificate: dict) -> list[str]:
    tests: list[tuple[str, str, object]] = []

    def source_test(label: str, mutate) -> None:
        tests.append((label, "source", mutate))

    def certificate_test(label: str, mutate) -> None:
        tests.append((label, "certificate", mutate))

    def comparison_test(label: str, mutate) -> None:
        tests.append((label, "comparison", mutate))

    source_test("source-coefficient", lambda x: x["canonical_boundary_representation"]["homogeneous_source"]["sparse_polynomial"][0].__setitem__("coefficient", 99))
    source_test("source-term-omission", lambda x: x["canonical_boundary_representation"]["homogeneous_source"]["sparse_polynomial"].pop())
    source_test("source-multidegree", lambda x: x["canonical_boundary_representation"].__setitem__("multidegree", [2, 2, 1]))
    source_test("coordinate-order", lambda x: x["canonical_boundary_representation"]["coordinate_order"].reverse())
    source_test("type-omission", lambda x: x["canonical_boundary_representation"]["boundary_types"].pop())
    source_test("type-order", lambda x: x["canonical_boundary_representation"]["boundary_types"].reverse())
    source_test("restricted-source", lambda x: x["canonical_boundary_representation"]["boundary_types"][0]["restricted_source"]["sparse_polynomial"][0].__setitem__("coefficient", -123))
    source_test("restricted-term-count", lambda x: x["canonical_boundary_representation"]["boundary_types"][0]["restricted_source"].__setitem__("term_count", 12))
    source_test("tangent-derivative", lambda x: x["canonical_boundary_representation"]["boundary_types"][0]["tangent_derivatives"][0]["sparse_polynomial"].pop())
    source_test("normal-derivative", lambda x: x["canonical_boundary_representation"]["boundary_types"][0]["normal_derivatives"].pop())
    source_test("derivative-semantics", lambda x: x["canonical_boundary_representation"]["derivative_semantics"].__setitem__("ambient_and_stratum_singularity_distinguished", False))
    source_test("ambient-stratum-conflation", lambda x: x["canonical_boundary_representation"]["boundary_types"][0].__setitem__("ambient_and_stratum_singularity_conflated", True))
    source_test("incidence-count", lambda x: x["canonical_boundary_representation"]["atlas_coverage"].__setitem__("boundary_type_chart_incidence_count", 278))
    source_test("compatible-chart-count", lambda x: x["canonical_boundary_representation"]["boundary_types"][0].__setitem__("compatible_standard_chart_count", 26))
    source_test("compatible-chart-id", lambda x: x["canonical_boundary_representation"]["boundary_types"][0]["compatible_chart_ids"].__setitem__(0, "FAKE"))
    source_test("chart-census", lambda x: x["canonical_boundary_representation"]["atlas_coverage"].__setitem__("standard_chart_count", 63))
    source_test("overlap-census", lambda x: x["canonical_boundary_representation"]["atlas_coverage"].__setitem__("directed_overlap_record_count", 4031))
    source_test("overlap-digest", lambda x: x["canonical_boundary_representation"]["atlas_coverage"].__setitem__("directed_overlap_semantic_sha256", "0" * 64))
    source_test("false-dedup", lambda x: x["canonical_boundary_representation"]["atlas_coverage"].__setitem__("deduplication_performed", True))
    source_test("deepest-factor", lambda x: x["canonical_boundary_representation"]["deepest_type"]["factors"][1]["sparse_polynomial"][0].__setitem__("coefficient", 2))
    source_test("deepest-factor-exponent", lambda x: x["canonical_boundary_representation"]["deepest_type"]["factors"][2].__setitem__("factorization_exponent", 2))
    source_test("deepest-factor-dimension", lambda x: x["canonical_boundary_representation"]["deepest_type"]["factors"][0].__setitem__("projective_product_divisor_dimension", 4))
    source_test("deepest-singular-branch-omission", lambda x: x["canonical_boundary_representation"]["deepest_type"]["stratum_singular_set_cover"].pop())
    source_test("deepest-normal-filter", lambda x: x["canonical_boundary_representation"]["deepest_type"]["stratum_singular_set_cover"][0]["ambient_candidate_additional_equations"].pop())
    source_test("deepest-parent-factor-node", lambda x: x["canonical_boundary_representation"]["deepest_type"]["parent_factor_correspondences"][1].__setitem__("parent_factor_node_id", "H_FAKE"))
    source_test("deepest-parent-factor-sign", lambda x: x["canonical_boundary_representation"]["deepest_type"]["parent_factor_correspondences"][1].__setitem__("parent_equals_multiplier_times_deepest_factor", 1))
    source_test("remaining-type-parent-overclaim", lambda x: x["canonical_boundary_representation"]["deepest_type"].__setitem__("remaining_six_type_parent_factor_matches_certified", 1))
    source_test("false-ambient-completeness", lambda x: x["canonical_boundary_representation"]["deepest_type"].__setitem__("ambient_component_decomposition_complete", True))
    source_test("pin-drift", lambda x: x["pins"].__setitem__("ops/research-team/PROTOCOL.md", "0" * 64))
    certificate_test("false-branch-dedup", lambda x: x["accepted_scope"].__setitem__("branch_overlap_deduplication_performed", True))
    certificate_test("false-ambient-complete", lambda x: x["accepted_scope"].__setitem__("ambient_component_decomposition_complete", True))
    certificate_test("false-affine-pullback", lambda x: x["accepted_scope"].__setitem__("affine_pullback_classifications_complete", True))
    certificate_test("false-parent-70", lambda x: x["accepted_scope"].__setitem__("all_70_parent_factor_classifications_complete", True))
    certificate_test("false-real-residence", lambda x: x["accepted_scope"].__setitem__("strict_real_residence_complete", True))
    certificate_test("false-connected-tag", lambda x: x["accepted_scope"].__setitem__("connected_parent_tags_complete", True))
    certificate_test("false-universal", lambda x: x["accepted_scope"].__setitem__("universal_diagonal_certificate", True))
    certificate_test("false-positive-endpoint", lambda x: x["endpoint_accounting"].__setitem__("positive", True))
    certificate_test("lost-null-endpoint", lambda x: x["endpoint_accounting"].__setitem__("null", False))
    certificate_test("false-ledger-delta", lambda x: x.__setitem__("ledger_delta", "1/9"))
    comparison_test("candidate-revision", lambda x: x.__setitem__("candidate_revision", "0" * 40))
    comparison_test("candidate-tree", lambda x: x.__setitem__("candidate_tree", "0" * 40))
    comparison_test("candidate-frontier-hash", lambda x: x.__setitem__("constructor_frontier_sha256", "0" * 64))
    comparison_test("candidate-frontier-semantic", lambda x: x.__setitem__("constructor_frontier_semantic_sha256", "0" * 64))
    comparison_test("candidate-type-omission", lambda x: x["type_comparisons"].pop())
    comparison_test("candidate-ambient-count", lambda x: x["accepted_candidate_scope"].__setitem__("ambient_derivatives_compared", 83))
    comparison_test("candidate-tangent-count", lambda x: x["accepted_candidate_scope"].__setitem__("tangent_derivative_identities_compared", 71))
    comparison_test("candidate-normal-count", lambda x: x["accepted_candidate_scope"].__setitem__("normal_derivatives_compared", 11))
    comparison_test("candidate-five-seed-cover", lambda x: x["accepted_candidate_scope"].__setitem__("deepest_set_theoretic_seed_cover_size", 4))
    comparison_test("candidate-ambient-children", lambda x: x["accepted_candidate_scope"].__setitem__("deepest_ambient_children_compared", 1))
    comparison_test("candidate-uv-derivative", lambda x: x["accepted_candidate_scope"].__setitem__("u_v_linear_P3_family_all_derivatives_zero", False))
    comparison_test("candidate-uv-dimension", lambda x: x["accepted_candidate_scope"].__setitem__("u_v_linear_P3_dimension", 2))
    comparison_test("candidate-uv-degree", lambda x: x["accepted_candidate_scope"].__setitem__("u_v_linear_P3_degree", 2))
    comparison_test("candidate-uv-parent", lambda x: x["accepted_candidate_scope"].__setitem__("u_v_linear_P3_excluded_by", "H_FAKE"))
    comparison_test("candidate-residual-id", lambda x: x["accepted_candidate_scope"].__setitem__("residual_branch_id", "B-FAKE"))
    comparison_test("candidate-residual-hash", lambda x: x["accepted_candidate_scope"].__setitem__("residual_branch_semantic_sha256", "0" * 64))
    comparison_test("candidate-false-completeness", lambda x: x["accepted_candidate_scope"].__setitem__("complete_seven_type_component_classification", True))
    comparison_test("candidate-false-affine", lambda x: x["accepted_candidate_scope"].__setitem__("accepted_affine_branch_count", 1))
    comparison_test("candidate-false-overlap", lambda x: x["accepted_candidate_scope"].__setitem__("overlap_representatives_quotiented", 1))
    comparison_test("candidate-false-universal", lambda x: x["accepted_candidate_scope"].__setitem__("universal_diagonal_certificate", True))
    comparison_test("candidate-false-ledger-delta", lambda x: x.__setitem__("ledger_delta", "1/9"))

    rejected = []
    for label, kind, mutate in tests:
        candidate = deepcopy(reconstruction if kind == "source" else comparison if kind == "comparison" else certificate)
        mutate(candidate)
        # Re-sealing tests semantic acceptance rather than only stale hashes.
        candidate = seal({key: value for key, value in candidate.items() if key != "semantic_sha256"})
        try:
            if kind == "source":
                validate_reconstruction(candidate, reconstruction)
            elif kind == "comparison":
                validate_candidate_comparison(candidate, comparison)
            else:
                validate_certificate(candidate, certificate)
        except Reject:
            rejected.append(label)
            continue
        raise Reject(f"hostile mutation accepted: {label}")
    require(len(rejected) >= 24 and len(rejected) == len(tests), "hostile mutation census")
    return rejected


def compare_external(path: Path, representation: dict) -> str:
    candidate = read_json(path)
    if candidate.get("format") == representation["format"]:
        external = candidate
    else:
        require("canonical_boundary_representation" in candidate, "external canonical representation key")
        external = candidate["canonical_boundary_representation"]
    require(external.get("semantic_sha256") == semantic_digest(external), "external representation seal")
    require(external == representation, "external canonical representation equality")
    return file_digest(path)


def findings_text(reconstruction: dict, comparison: dict, certificate: dict, hostile_count: int) -> str:
    representation = reconstruction["canonical_boundary_representation"]
    type_counts = [
        f"`{record['type_id']}`: {record['restricted_source']['term_count']} terms"
        for record in representation["boundary_types"]
    ]
    return (
        "# Producer-independent homogenizer boundary certificate\n\n"
        "Verdict: **accepted frozen constructor partial frontier with a fail-closed null endpoint**.\n\n"
        "The pinned 108-term affine factor was dehomogenized from, then independently "
        "re-homogenized to, the exact degree-`(2,2,2)` source in "
        "`Q[a,b,c,u,d,e,f,v,g,h,i,w]`.  No producer code, numerical probe, modular "
        "evidence, sample, network service, or connector was used.\n\n"
        "The seven deepest-first restrictions are " + ", ".join(type_counts) + ".  "
        "All 72 tangent restrict/differentiate identities hold exactly.  The 12 normal "
        "derivatives are retained separately, so stratum singularity is never promoted "
        "to ambient singularity.\n\n"
        "For `u=v=w=0`, the 11 surviving terms equal exactly "
        "`-h*(a*f-c*d)*(a*e*i-a*f*h-b*d*i+b*f*g+c*d*h-c*e*g)`.  The displayed "
        "factors have multidegrees `(0,0,1)`, `(1,1,0)`, and `(1,1,1)`, occur once in "
        "that displayed product, and define divisors of dimension 5 in `P2 x P2 x P2`. "
        "The constructor's five product-rule seeds—three pairwise factor intersections, "
        "`Sing(L)`, and the determinant rank-at-most-one locus—were checked exactly. "
        "`Sing(L)` is retained as an explicit seed although it lies in `V(L,C)`.\n\n"
        "The same pinned 70-record parent stream gives three and only three certified "
        "deepest-factor correspondences: `H_08_1248=h`, "
        "`H_22_1367=-(a*f-c*d)`, and `H_34_1678=det`.  Each was checked by exact "
        "and sign-normalized sparse equality.  No parent-factor correspondence is "
        "inferred for any of the remaining six types.\n\n"
        "On the processed `V(h,L)` seed, independent lexicographic sparse division proves "
        "that the `u` and `v` normal derivatives lie in `(h,L)` and reconstructs "
        "`dF/dw=quotient*L+e*Q`.  Thus the two exact ambient children are `V(h,L,e)` "
        "and `V(h,L,Q)`; both are projective-infinity only and already excluded by "
        "`H_08_1248` and `H_22_1367`.\n\n"
        "For `u=v=0`, direct substitution into the independently reconstructed source and "
        "all 12 full derivatives proves that `u=v=b=c=e=f=0` is a linear `P3` family. "
        "It has exact dimension 3 and degree 1 and is excluded because "
        "`H_22_1367=c*d-a*f` vanishes identically.  It is not accepted as affine and is "
        "not claimed to exhaust the ambient singular ideal.\n\n"
        "The inherited atlas replay certifies 64 charts, 4,032 directed principal-open "
        "overlap records, and 279 type/chart incidences (`27+36+36+36+48+48+48`).  No "
        "branch duplicates were quotiented: a later quotient must provide an explicit "
        "invertible overlap witness.\n\n"
        f"All {hostile_count} hostile mutations were rejected.  The independently "
        "reconstructed residual is `B-UV-01-unclassified-ambient-components`, SHA-256 "
        f"`{comparison['accepted_candidate_scope']['residual_branch_semantic_sha256']}`. "
        "No complete seven-type component census, nondeepest factor certification, "
        "overlap quotient, accepted affine pullback, 70-parent affine census, strict-real "
        "residence, or connected-parent tag is certified.  The ledger remains `2/9`.\n"
    )


def emit_artifacts(reconstruction: dict, comparison: dict, certificate: dict, result: dict, rejected: list[str]) -> None:
    result = deepcopy(result)
    result["hostile_tests"] = {"required": 24, "run": len(rejected), "rejected": len(rejected)}
    result = seal({key: value for key, value in result.items() if key != "semantic_sha256"})
    manifest = seal({
        "format": "d9-factor19069-homogenizer-boundary-certificate-source-manifest-v1",
        "cycle_id": CYCLE_ID,
        "track_id": TRACK_ID,
        "base_revision": BASE_REVISION,
        "base_tree": BASE_TREE,
        "pins": dict(sorted(PINNED_INPUTS.items())),
        "candidate_pins": dict(sorted(CANDIDATE_PINS.items())),
        "candidate_revision": CANDIDATE_REVISION,
        "candidate_tree": CANDIDATE_TREE,
        "candidate_comparison_policy": comparison["comparison_policy"],
        "source_reconstruction_semantic_sha256": reconstruction["semantic_sha256"],
        "candidate_comparison_semantic_sha256": comparison["semantic_sha256"],
        "canonical_boundary_representation_semantic_sha256": reconstruction["canonical_boundary_representation"]["semantic_sha256"],
        "boundary_certificate_semantic_sha256": certificate["semantic_sha256"],
        "source_policy": reconstruction["source_policy"],
    })
    hostile = seal({
        "format": "d9-factor19069-homogenizer-boundary-certificate-hostile-tests-v1",
        "cycle_id": CYCLE_ID,
        "track_id": TRACK_ID,
        "required": 24,
        "run": len(rejected),
        "rejected": len(rejected),
        "labels": rejected,
    })
    if SOURCE_RECONSTRUCTION.is_file():
        validate_reconstruction(read_json(SOURCE_RECONSTRUCTION), reconstruction)
    else:
        write_json(SOURCE_RECONSTRUCTION, reconstruction)
    write_json(CANDIDATE_COMPARISON, comparison)
    write_json(BOUNDARY_CERTIFICATE, certificate)
    write_json(SOURCE_MANIFEST, manifest)
    write_json(HOSTILE_TESTS, hostile)
    write_json(RESULT, result)
    with FINDINGS.open("w", encoding="utf-8", newline="\n") as stream:
        stream.write(findings_text(reconstruction, comparison, certificate, len(rejected)))
    validate_result(read_json(RESULT), result, len(rejected))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true", help="write deterministic lane artifacts")
    parser.add_argument("--compare", type=Path, help="compare an external canonical boundary representation")
    arguments = parser.parse_args()

    reconstruction, comparison, certificate, result = reconstruct_all()
    validate_reconstruction(reconstruction, reconstruction)
    validate_candidate_comparison(comparison, comparison)
    validate_certificate(certificate, certificate)
    rejected = run_hostile_tests(reconstruction, comparison, certificate)
    if arguments.emit:
        emit_artifacts(reconstruction, comparison, certificate, result, rejected)
    else:
        require(SOURCE_RECONSTRUCTION.is_file(), "stored reconstruction exists")
        require(CANDIDATE_COMPARISON.is_file(), "stored candidate comparison exists")
        require(BOUNDARY_CERTIFICATE.is_file(), "stored certificate exists")
        require(SOURCE_MANIFEST.is_file(), "stored manifest exists")
        require(HOSTILE_TESTS.is_file(), "stored hostile artifact exists")
        require(RESULT.is_file(), "stored result exists")
        validate_reconstruction(read_json(SOURCE_RECONSTRUCTION), reconstruction)
        validate_candidate_comparison(read_json(CANDIDATE_COMPARISON), comparison)
        validate_certificate(read_json(BOUNDARY_CERTIFICATE), certificate)
        stored_hostile = read_json(HOSTILE_TESTS)
        require(stored_hostile["semantic_sha256"] == semantic_digest(stored_hostile), "hostile artifact seal")
        require(stored_hostile["labels"] == rejected, "hostile artifact labels")
        validate_result(read_json(RESULT), result, len(rejected))
        manifest = read_json(SOURCE_MANIFEST)
        require(manifest["semantic_sha256"] == semantic_digest(manifest), "manifest seal")
        require(manifest["pins"] == dict(sorted(PINNED_INPUTS.items())), "manifest pins")
        require(manifest["candidate_pins"] == dict(sorted(CANDIDATE_PINS.items())), "manifest candidate pins")
        require(manifest["candidate_revision"] == CANDIDATE_REVISION and manifest["candidate_tree"] == CANDIDATE_TREE, "manifest candidate revision")
        require(manifest["candidate_comparison_policy"] == comparison["comparison_policy"], "manifest candidate comparison policy")
        require(manifest["source_reconstruction_semantic_sha256"] == reconstruction["semantic_sha256"], "manifest reconstruction binding")
        require(manifest["candidate_comparison_semantic_sha256"] == comparison["semantic_sha256"], "manifest comparison binding")

    external_comparison = "none"
    if arguments.compare:
        external_comparison = compare_external(arguments.compare, reconstruction["canonical_boundary_representation"])
    print("PASS producer-independent homogenizer boundary certificate")
    print("PASS source_terms=108 multidegree=2,2,2 types=7 tangent_identities=72 normal_derivatives=12")
    print("PASS deepest_terms=11 factors=3 five_seeds=5 ambient_children=2 charts=64 overlaps=4032 incidences=279")
    print("PASS uv_linear_P3=true dimension=3 degree=1 excluded_by=H_22_1367 residual=2747fcc6923b")
    print(f"PASS hostile={len(rejected)}/{len(rejected)} null_frontier=true ledger=2/9 external_compare={external_comparison}")


if __name__ == "__main__":
    try:
        main()
    except Reject as error:
        print(f"REJECT {error}", file=sys.stderr)
        raise SystemExit(1)
