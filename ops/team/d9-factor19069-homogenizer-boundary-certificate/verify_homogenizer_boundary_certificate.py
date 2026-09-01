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
SOURCE_RECONSTRUCTION = HERE / "SOURCE_RECONSTRUCTION.json"
BOUNDARY_CERTIFICATE = HERE / "BOUNDARY_CERTIFICATE.json"
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
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


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


def reconstruct_all() -> tuple[dict, dict, dict]:
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
    certificate = seal({
        "format": "d9-factor19069-homogenizer-boundary-certificate-v1",
        "cycle_id": CYCLE_ID,
        "track_id": TRACK_ID,
        "canonical_boundary_representation_semantic_sha256": representation["semantic_sha256"],
        "accepted_scope": {
            "source_terms": 108,
            "trihomogeneous_multidegree": [2, 2, 2],
            "seven_restricted_sources": True,
            "tangent_derivative_transfer_identities": 72,
            "restricted_normal_derivatives": 12,
            "ambient_stratum_distinction": True,
            "deepest_11_term_factorization": True,
            "deepest_set_theoretic_stratum_singular_cover": True,
            "deepest_parent_factor_sparse_matches": 3,
            "remaining_six_type_parent_factor_matches": 0,
            "standard_charts": 64,
            "directed_overlap_records": 4032,
            "boundary_type_chart_incidences": 279,
            "explicit_overlap_atlas_replayed": True,
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
            "first_unresolved_branch": "UVW-SING-H-MINOR:AMBIENT_NORMAL_FILTER_COMPONENT_DECOMPOSITION",
        },
        "classification": "ACCEPT_EXACT_SEVEN_TYPE_RECONSTRUCTION_FAIL_CLOSED_NULL_FRONTIER",
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
        "boundary_certificate_semantic_sha256": certificate["semantic_sha256"],
        "certificate_gates": certificate["accepted_scope"],
        "hostile_tests": {"required": 24, "run": 0, "rejected": 0},
        "ledger_before": "2/9",
        "ledger_after": "2/9",
        "ledger_delta": "0/9",
        "ledger_change_recommended": "none",
        "nonconsequences": [
            "NO_COMPLETE_AMBIENT_BOUNDARY_COMPONENT_DECOMPOSITION",
            "NO_SCHEME_MULTIPLICITY_OR_RADICALITY_CLAIM",
            "NO_BRANCH_OVERLAP_DEDUPLICATION",
            "NO_ACCEPTED_AFFINE_COMPONENT_PULLBACK",
            "NO_COMPLETE_70_PARENT_FACTOR_INCIDENCE",
            "NO_STRICT_REAL_RESIDENCE_OR_CONNECTED_PARENT_TAG",
            "NO_THEOREM_LEVEL_COUNTEREXAMPLE",
            "NO_DIAGONAL_9_PROOF_OR_COUNTEREXAMPLE",
            "NO_9DVL_SCORE_CHANGE",
        ],
    })
    return reconstruction, certificate, result


def validate_reconstruction(candidate: dict, expected: dict) -> None:
    require(candidate.get("semantic_sha256") == semantic_digest(candidate), "reconstruction semantic seal")
    require(candidate == expected, "reconstruction exact canonical equality")


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


def run_hostile_tests(reconstruction: dict, certificate: dict) -> list[str]:
    tests: list[tuple[str, str, object]] = []

    def source_test(label: str, mutate) -> None:
        tests.append((label, "source", mutate))

    def certificate_test(label: str, mutate) -> None:
        tests.append((label, "certificate", mutate))

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

    rejected = []
    for label, kind, mutate in tests:
        candidate = deepcopy(reconstruction if kind == "source" else certificate)
        mutate(candidate)
        # Re-sealing tests semantic acceptance rather than only stale hashes.
        candidate = seal({key: value for key, value in candidate.items() if key != "semantic_sha256"})
        try:
            if kind == "source":
                validate_reconstruction(candidate, reconstruction)
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


def findings_text(reconstruction: dict, certificate: dict, hostile_count: int) -> str:
    representation = reconstruction["canonical_boundary_representation"]
    type_counts = [
        f"`{record['type_id']}`: {record['restricted_source']['term_count']} terms"
        for record in representation["boundary_types"]
    ]
    return (
        "# Producer-independent homogenizer boundary certificate\n\n"
        "Verdict: **accepted exact seven-type reconstruction with a fail-closed null frontier**.\n\n"
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
        "The exact set-theoretic stratum-singular cover consists of the three pairwise "
        "factor intersections plus the determinant rank-at-most-one locus.  Each is then "
        "intersected with the three retained normal derivatives for ambient singularity.\n\n"
        "The same pinned 70-record parent stream gives three and only three certified "
        "deepest-factor correspondences: `H_08_1248=h`, "
        "`H_22_1367=-(a*f-c*d)`, and `H_34_1678=det`.  Each was checked by exact "
        "and sign-normalized sparse equality.  No parent-factor correspondence is "
        "inferred for any of the remaining six types.\n\n"
        "The inherited atlas replay certifies 64 charts, 4,032 directed principal-open "
        "overlap records, and 279 type/chart incidences (`27+36+36+36+48+48+48`).  No "
        "branch duplicates were quotiented: a later quotient must provide an explicit "
        "invertible overlap witness.\n\n"
        f"All {hostile_count} hostile mutations were rejected.  The first unresolved "
        "node is `UVW-SING-H-MINOR:AMBIENT_NORMAL_FILTER_COMPONENT_DECOMPOSITION`. "
        "No ambient component decomposition, scheme multiplicity, affine pullback, "
        "70-parent classification, strict-real residence, or connected-parent tag is "
        "certified.  The ledger remains `2/9` with delta `0/9`.\n"
    )


def emit_artifacts(reconstruction: dict, certificate: dict, result: dict, rejected: list[str]) -> None:
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
        "source_reconstruction_semantic_sha256": reconstruction["semantic_sha256"],
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
    write_json(SOURCE_RECONSTRUCTION, reconstruction)
    write_json(BOUNDARY_CERTIFICATE, certificate)
    write_json(SOURCE_MANIFEST, manifest)
    write_json(HOSTILE_TESTS, hostile)
    write_json(RESULT, result)
    FINDINGS.write_text(findings_text(reconstruction, certificate, len(rejected)), encoding="utf-8")
    validate_result(read_json(RESULT), result, len(rejected))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit", action="store_true", help="write deterministic lane artifacts")
    parser.add_argument("--compare", type=Path, help="compare an external canonical boundary representation")
    arguments = parser.parse_args()

    reconstruction, certificate, result = reconstruct_all()
    validate_reconstruction(reconstruction, reconstruction)
    validate_certificate(certificate, certificate)
    rejected = run_hostile_tests(reconstruction, certificate)
    if arguments.emit:
        emit_artifacts(reconstruction, certificate, result, rejected)
    else:
        require(SOURCE_RECONSTRUCTION.is_file(), "stored reconstruction exists")
        require(BOUNDARY_CERTIFICATE.is_file(), "stored certificate exists")
        require(SOURCE_MANIFEST.is_file(), "stored manifest exists")
        require(HOSTILE_TESTS.is_file(), "stored hostile artifact exists")
        require(RESULT.is_file(), "stored result exists")
        validate_reconstruction(read_json(SOURCE_RECONSTRUCTION), reconstruction)
        validate_certificate(read_json(BOUNDARY_CERTIFICATE), certificate)
        stored_hostile = read_json(HOSTILE_TESTS)
        require(stored_hostile["semantic_sha256"] == semantic_digest(stored_hostile), "hostile artifact seal")
        require(stored_hostile["labels"] == rejected, "hostile artifact labels")
        validate_result(read_json(RESULT), result, len(rejected))
        manifest = read_json(SOURCE_MANIFEST)
        require(manifest["semantic_sha256"] == semantic_digest(manifest), "manifest seal")
        require(manifest["pins"] == dict(sorted(PINNED_INPUTS.items())), "manifest pins")
        require(manifest["source_reconstruction_semantic_sha256"] == reconstruction["semantic_sha256"], "manifest reconstruction binding")

    comparison = "none"
    if arguments.compare:
        comparison = compare_external(arguments.compare, reconstruction["canonical_boundary_representation"])
    print("PASS producer-independent homogenizer boundary certificate")
    print("PASS source_terms=108 multidegree=2,2,2 types=7 tangent_identities=72 normal_derivatives=12")
    print("PASS deepest_terms=11 factors=3 singular_cover_branches=4 charts=64 overlaps=4032 incidences=279")
    print(f"PASS hostile={len(rejected)}/{len(rejected)} null_frontier=true ledger=2/9 external_compare={comparison}")


if __name__ == "__main__":
    try:
        main()
    except Reject as error:
        print(f"REJECT {error}", file=sys.stderr)
        raise SystemExit(1)
