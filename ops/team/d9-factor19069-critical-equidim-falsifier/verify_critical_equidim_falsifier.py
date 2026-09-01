#!/usr/bin/env python3
"""Independent adversarial verifier for factor-19069 critical decomposition.

This lane deliberately does not import the constructor or certificate code.  It
rebuilds the signed row-2599 parent factors and factor 19069 from the pinned
mathematical sources, checks the predecessor's unexpanded factor circuit as
data, validates this lane's fail-closed claim, and proves that a suite of
hostile claim mutations is rejected.
"""

from __future__ import annotations

import json
from copy import deepcopy
from hashlib import sha256
from pathlib import Path
import struct
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OMREAL = ROOT / "ai" / "omreal"
DATA = OMREAL / "data"
MANIFEST = HERE / "SOURCE_MANIFEST.json"
RESULT = HERE / "RESULT.json"
HOSTILE = HERE / "HOSTILE_TESTS.json"
PREDECESSOR = (
    ROOT
    / "ops"
    / "team"
    / "d9-factor19069-factored-barrier-constructor"
    / "FACTORED_BARRIER_FRONTIER.json"
)

TARGET_FACTOR = 19069
TARGET_PARENT = 2599
VARIABLES = tuple("abcdefghi")
EXPECTED_PARENT_DIGEST = "1d9b940e2bb954b5c69bcee8b2346f9554b2e15589ea4c5b3c3f8e1e943de701"
EXPECTED_PREDECESSOR_SHA256 = "3f75eeb2f7433234206292012c527604517b516ee904e2ab1d1969e49ed1e8ca"
EXPECTED_PARENT_LABELS = (
    "1234", "1235", "1236", "1237", "1238", "1245", "1246", "1247", "1248", "1256",
    "1257", "1258", "1267", "1268", "1278", "1345", "1346", "1347", "1348", "1356",
    "1357", "1358", "1367", "1368", "1378", "1456", "1457", "1458", "1467", "1468",
    "1478", "1567", "1568", "1578", "1678", "2345", "2346", "2347", "2348", "2356",
    "2357", "2358", "2367", "2368", "2378", "2456", "2457", "2458", "2467", "2468",
    "2478", "2567", "2568", "2578", "2678", "3456", "3457", "3458", "3467", "3468",
    "3478", "3567", "3568", "3578", "3678", "4567", "4568", "4578", "4678", "5678",
)
EXPECTED_PARENT_NODE_IDS = tuple(
    f"H_{index:02d}_{label}" for index, label in enumerate(EXPECTED_PARENT_LABELS)
)

sys.path.insert(0, str(OMREAL))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


class Reject(AssertionError):
    pass


def require(condition: bool, marker: str) -> None:
    if not condition:
        raise Reject(marker)


def digest_path(path: Path) -> str:
    state = sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            state.update(block)
    return state.hexdigest()


def canonical_digest(value) -> str:
    return sha256(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def polynomial_degree(polynomial: dict) -> int:
    return max(map(sum, polynomial))


def multidegree(polynomial: dict) -> tuple[int, int, int]:
    groups = ((0, 1, 2), (3, 4, 5), (6, 7, 8))
    return tuple(
        max(sum(exponents[index] for index in group) for exponents in polynomial)
        for group in groups
    )


def decode_sparse(records: list[dict], marker: str) -> dict:
    require(all(set(row) == {"exponents", "coefficient"} for row in records), marker)
    keys = [tuple(row["exponents"]) for row in records]
    require(len(keys) == len(set(keys)), marker)
    require(all(len(key) == 9 and all(isinstance(x, int) and x >= 0 for x in key) for key in keys), marker)
    require(all(isinstance(row["coefficient"], int) and row["coefficient"] for row in records), marker)
    return {key: row["coefficient"] for key, row in zip(keys, records, strict=True)}


def candidate_ids() -> tuple[int, ...]:
    raw = (DATA / "DIAG3_PAIR_GLOBAL_row2599_candidate_factors.bin").read_bytes()
    header = struct.calcsize("<8sIII")
    magic, parent, universe, count = struct.unpack_from("<8sIII", raw)
    require((magic, parent, universe, count) == (b"D3PFC001", 2599, 26740, 17824), "candidate source header")
    require(len(raw) == header + 4 * count, "candidate source length")
    values = tuple(item[0] for item in struct.iter_unpack("<I", raw[header:]))
    require(values == tuple(sorted(set(values))), "candidate source ordering")
    return values


def reconstruct_sources() -> dict:
    records = [
        json.loads(line)
        for line in (OMREAL / "certs_4_8.jsonl").read_text(encoding="utf-8").splitlines()
        if line
    ]
    require(len(records) == 2628, "parent record census")
    require(records[TARGET_PARENT]["verdict"] == "REALIZABLE", "parent realizability")
    parent_sources, parent_digest = gate.parent_polynomials(records[TARGET_PARENT])
    require(parent_digest == EXPECTED_PARENT_DIGEST, "parent source digest")
    require(len(parent_sources) == 70, "parent factor count")
    require(tuple(row[0] for row in parent_sources) == EXPECTED_PARENT_LABELS, "parent factor ordering")
    signed_parents = tuple(
        {
            exponents: target_sign * coefficient
            for exponents, coefficient in polynomial.items()
        }
        for _label, target_sign, polynomial, _terms in parent_sources
    )
    require(sum(len(polynomial) for polynomial in signed_parents) == 209, "parent sparse-term census")

    require(TARGET_FACTOR in candidate_ids(), "factor-19069 candidate membership")
    _occurrences, _occurrence_factor, factors = labeled.factor_polynomials()
    factor = factors[TARGET_FACTOR]
    require(polynomial_degree(factor) == 6, "factor-19069 total degree")
    require(multidegree(factor) == (2, 2, 2), "factor-19069 multidegree")
    require(len(factor) == 108, "factor-19069 sparse-term census")
    return {
        "parent_digest": parent_digest,
        "signed_parents": signed_parents,
        "factor": factor,
    }


def validate_predecessor(candidate: dict, replay: dict) -> None:
    require(digest_path(PREDECESSOR) == EXPECTED_PREDECESSOR_SHA256, "predecessor byte pin")
    require(candidate["format"] == "d9-factor19069-factored-barrier-frontier-v1", "predecessor format")
    require(candidate["target"]["parent_index"] == TARGET_PARENT, "predecessor parent")
    require(candidate["target"]["factor_id"] == TARGET_FACTOR, "predecessor factor")
    require(candidate["target"]["parent_sign_digest"] == replay["parent_digest"], "predecessor parent digest")
    circuit = candidate["factor_circuit"]
    require(candidate["factor_circuit_semantic_sha256"] == canonical_digest(circuit), "predecessor circuit digest")
    require(circuit["coordinates"] == list(VARIABLES), "predecessor coordinates")
    require(decode_sparse(circuit["wall_polynomial"]["sparse_polynomial"], "predecessor wall source") == replay["factor"], "predecessor wall source")
    nodes = circuit["parent_factor_nodes"]
    require(len(nodes) == 70, "predecessor parent node count")
    require(tuple(node["node_id"] for node in nodes) == EXPECTED_PARENT_NODE_IDS, "predecessor parent node ordering")
    for node, polynomial in zip(nodes, replay["signed_parents"], strict=True):
        require(decode_sparse(node["sparse_polynomial"], "predecessor parent source") == polynomial, "predecessor parent source")
    barrier = circuit["barrier"]
    require(barrier["ordered_factor_node_ids"] == list(EXPECTED_PARENT_NODE_IDS), "predecessor 70-factor provenance")
    require(barrier["factor_count"] == 70, "predecessor barrier factor count")
    require(barrier["expanded_polynomial_present"] is False, "predecessor unexpanded barrier")
    require(len(circuit["wedge_equation_nodes"]) == 36, "predecessor wedge census")
    require(candidate["strict_interior_critical_frontier"]["singular_pieces_discarded"] == 0, "predecessor singular scope")
    require(candidate["theorem_ledger"] == "2/9", "predecessor ledger")


def validate_manifest(candidate: dict) -> None:
    require(candidate["format"] == "d9-factor19069-critical-equidim-falsifier-source-manifest-v1", "manifest format")
    require(candidate["source_count"] == len(candidate["source_sha256"]), "manifest source count")
    for relative, expected in candidate["source_sha256"].items():
        require(digest_path(ROOT / relative) == expected, f"source pin {relative}")
    require(candidate["drive_connector_used"] is False, "drive authority")
    require(candidate["github_write"] is False, "github authority")


def validate_claim(candidate: dict) -> None:
    require(candidate["format"] == "d9-factor19069-critical-equidim-falsifier-result-v1", "result format")
    target = candidate["target"]
    require(target["parent_index"] == TARGET_PARENT, "target parent")
    require(target["factor_id"] == TARGET_FACTOR, "target factor")
    require(target["ambient_parameter_dimension"] == 9, "target ambient dimension")
    require(target["parent_sign_digest"] == EXPECTED_PARENT_DIGEST, "target parent digest")

    ideal = candidate["audited_ideal_contract"]
    require(ideal["factor_circuit_semantic_sha256"] == "0e10d3d4692a53a6040ea8822be05376775e9c674c74d532f42236d3dfb1a7cf", "factor circuit binding")
    require(ideal["wall_equation"] == "f_19069=0", "wall equation membership")
    require(ideal["critical_equations"] == ["all_36_coefficients_of_dB_wedge_df=0"], "critical equation membership")
    require(ideal["parent_factor_node_ids"] == list(EXPECTED_PARENT_NODE_IDS), "parent factor membership")
    require(ideal["barrier_representation"] == "UNEXPANDED_ORDERED_PRODUCT_OF_70_SOURCE_DERIVED_FACTORS", "unexpanded barrier")
    saturation = ideal["saturation"]
    require(saturation["invert_exactly"] == list(EXPECTED_PARENT_NODE_IDS), "saturation factor membership")
    require(saturation["must_not_invert"] == ["f_19069", "Jacobian_singular_locus", "true_parent_boundary_strata"], "saturation exclusion scope")
    require(saturation["connected_parent_selector"] == "EXACT_PATH_TO_PINNED_ROW2599_PARENT_SAMPLE_REQUIRED", "connected parent selector")
    require(ideal["singular_wall_pieces_retained"] is True, "singular wall retention")
    require(ideal["true_boundary_strata_retained"] is True, "true boundary retention")
    require(ideal["true_boundary_distinct_from"] == ["SOLVER_BOUNDARY", "BOX_BOUNDARY", "COLLAR_BOUNDARY", "SKELETON_EDGE_ENDPOINT"], "boundary-class separation")
    require(ideal["source_derived_parent_component_tags"] is True, "parent tag provenance")

    decomposition = candidate["decomposition_audit"]
    require(decomposition["status"] == "UNRESOLVED_FAIL_CLOSED", "decomposition status")
    require(decomposition["exact_component_dimensions"] is None, "unsupported dimension claim")
    require(decomposition["exact_component_degrees"] is None, "unsupported degree claim")
    require(decomposition["exact_component_multiplicities"] is None, "unsupported multiplicity claim")
    require(decomposition["positive_dimensional_piece_status"] == "NOT_EXCLUDED", "positive-dimensional scope")
    require(decomposition["zero_dimensionality_proved"] is False, "zero-dimensionality overreach")
    require(decomposition["exact_real_root_count_frontier"] is None, "real-root overreach")
    first = decomposition["first_unresolved_obligation"]
    require(first["stratum_id"] == "FB-C0-STRICT-INTERIOR-FULL-SUPPORT", "first unresolved stratum")
    require(first["obligation"] == "COMPUTE_EXACT_SATURATED_IDEAL_DIMENSION_BEFORE_ANY_COMPONENT_SAMPLING", "first unresolved obligation")
    require(first["possible_dimensions"] == list(range(9)), "unresolved dimension frontier")

    guards = candidate["inference_guards"]
    require(guards["sampling_used_as_dimension_proof"] is False, "sampling inference")
    require(guards["projection_used_as_dimension_proof"] is False, "projection inference")
    require(guards["local_skeleton_or_edge39_used_globally"] is False, "skeleton inference")
    require(guards["collar_used_as_global_component_proof"] is False, "collar inference")
    require(guards["boundary_or_singular_stratum_omitted"] is False, "stratum omission")
    require(candidate["ledger_delta"] == "none", "ledger delta")
    require(candidate["theorem_ledger"] == "2/9", "ledger scope")
    require(candidate["ledger_promotion_recommended"] is False, "ledger promotion")
    require(candidate["outcome"] == "pass", "falsifier outcome")


def hostile_mutations(stored: dict) -> list[str]:
    mutations: list[tuple[str, dict]] = []

    def add(marker: str, edit) -> None:
        candidate = deepcopy(stored)
        edit(candidate)
        mutations.append((marker, candidate))

    add("target factor", lambda c: c["target"].__setitem__("factor_id", 19068))
    add("target parent", lambda c: c["target"].__setitem__("parent_index", 2600))
    add("target parent digest", lambda c: c["target"].__setitem__("parent_sign_digest", "0" * 64))
    add("factor circuit binding", lambda c: c["audited_ideal_contract"].__setitem__("factor_circuit_semantic_sha256", "0" * 64))
    add("wall equation membership", lambda c: c["audited_ideal_contract"].__setitem__("wall_equation", "1=0"))
    add("critical equation membership", lambda c: c["audited_ideal_contract"].__setitem__("critical_equations", []))
    add("parent factor membership", lambda c: c["audited_ideal_contract"]["parent_factor_node_ids"].pop())
    add("parent factor membership", lambda c: c["audited_ideal_contract"]["parent_factor_node_ids"].__setitem__(slice(0, 2), list(reversed(c["audited_ideal_contract"]["parent_factor_node_ids"][:2]))))
    add("unexpanded barrier", lambda c: c["audited_ideal_contract"].__setitem__("barrier_representation", "EXPANDED_POLYNOMIAL"))
    add("saturation factor membership", lambda c: c["audited_ideal_contract"]["saturation"]["invert_exactly"].pop())
    add("saturation exclusion scope", lambda c: c["audited_ideal_contract"]["saturation"]["must_not_invert"].remove("Jacobian_singular_locus"))
    add("saturation exclusion scope", lambda c: c["audited_ideal_contract"]["saturation"]["must_not_invert"].remove("true_parent_boundary_strata"))
    add("connected parent selector", lambda c: c["audited_ideal_contract"]["saturation"].__setitem__("connected_parent_selector", "SIGNS_ONLY"))
    add("singular wall retention", lambda c: c["audited_ideal_contract"].__setitem__("singular_wall_pieces_retained", False))
    add("true boundary retention", lambda c: c["audited_ideal_contract"].__setitem__("true_boundary_strata_retained", False))
    add("boundary-class separation", lambda c: c["audited_ideal_contract"]["true_boundary_distinct_from"].pop())
    add("parent tag provenance", lambda c: c["audited_ideal_contract"].__setitem__("source_derived_parent_component_tags", False))
    add("unsupported dimension claim", lambda c: c["decomposition_audit"].__setitem__("exact_component_dimensions", [0]))
    add("unsupported degree claim", lambda c: c["decomposition_audit"].__setitem__("exact_component_degrees", [1]))
    add("unsupported multiplicity claim", lambda c: c["decomposition_audit"].__setitem__("exact_component_multiplicities", [1]))
    add("positive-dimensional scope", lambda c: c["decomposition_audit"].__setitem__("positive_dimensional_piece_status", "EXCLUDED_BY_NUMERICAL_SAMPLING"))
    add("zero-dimensionality overreach", lambda c: c["decomposition_audit"].__setitem__("zero_dimensionality_proved", True))
    add("real-root overreach", lambda c: c["decomposition_audit"].__setitem__("exact_real_root_count_frontier", 0))
    add("first unresolved obligation", lambda c: c["decomposition_audit"]["first_unresolved_obligation"].__setitem__("obligation", "SAMPLE_MORE_POINTS"))
    add("unresolved dimension frontier", lambda c: c["decomposition_audit"]["first_unresolved_obligation"].__setitem__("possible_dimensions", [0]))
    add("sampling inference", lambda c: c["inference_guards"].__setitem__("sampling_used_as_dimension_proof", True))
    add("projection inference", lambda c: c["inference_guards"].__setitem__("projection_used_as_dimension_proof", True))
    add("skeleton inference", lambda c: c["inference_guards"].__setitem__("local_skeleton_or_edge39_used_globally", True))
    add("collar inference", lambda c: c["inference_guards"].__setitem__("collar_used_as_global_component_proof", True))
    add("stratum omission", lambda c: c["inference_guards"].__setitem__("boundary_or_singular_stratum_omitted", True))
    add("ledger delta", lambda c: c.__setitem__("ledger_delta", "+1"))
    add("ledger scope", lambda c: c.__setitem__("theorem_ledger", "3/9"))
    add("ledger promotion", lambda c: c.__setitem__("ledger_promotion_recommended", True))

    rejected = []
    for marker, candidate in mutations:
        try:
            validate_claim(candidate)
        except Reject as error:
            require(marker in str(error), f"hostile wrong rejection {marker}: {error}")
            rejected.append(marker)
        else:
            raise Reject(f"hostile mutation accepted: {marker}")
    require(len(rejected) == len(mutations) == 33, "hostile mutation census")
    return rejected


def main() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    hostile = json.loads(HOSTILE.read_text(encoding="utf-8"))
    validate_manifest(manifest)
    replay = reconstruct_sources()
    predecessor = json.loads(PREDECESSOR.read_text(encoding="utf-8"))
    validate_predecessor(predecessor, replay)
    validate_claim(result)
    rejected = hostile_mutations(result)
    require(hostile["total"] == hostile["rejected"] == len(rejected), "hostile manifest census")
    require(hostile["rejection_markers"] == rejected, "hostile manifest markers")
    print("PASS independent row-2599 parent reconstruction: 70 ordered factors, 209 sparse terms")
    print("PASS independent factor-19069 reconstruction: degree 6, multidegree (2,2,2), 108 terms")
    print("PASS predecessor unexpanded 70-factor circuit and 36 wedge equations")
    print("PASS exact saturation, boundary, singular, connected-parent, and inference scope guards")
    print(f"PASS hostile_mutations={len(rejected)}/33 rejected")
    print("CLASSIFICATION FAIL_CLOSED_EXACT_EQUIDIMENSIONAL_DECOMPOSITION_UNRESOLVED ledger=2/9")


if __name__ == "__main__":
    main()
