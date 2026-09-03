#!/usr/bin/env python3
"""Independent stdlib verifier for the frozen D3 mixed-100 midpoint.

Producer verifier modules are deliberately never imported or executed.  This
checker reconstructs the exact lower complex, finite category, logical scope,
and convergence gate from pinned source bytes and untrusted JSON handoffs.
"""

from __future__ import annotations

import copy
from fractions import Fraction
from hashlib import sha256
import itertools
import json
import math
from pathlib import Path
import subprocess


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CYCLE_DIR = Path("ops/research-team/cycles/2026-09-03-d3-mixed-block-100-universal-carrier-gate1")

LANE_OPENING_COMMIT = "69983136e6f222ede46433da12a674dda613244e"
LANE_OPENING_TREE = "2656b5ad4d9406a7fc38993d162051b8a88836ee"
INTEGRATED_COMMIT = "833d61bd0702529c892c9b37ad8a2ee5c7b8b972"
INTEGRATED_TREE = "736228f57bcbb1bbad355a87266bfb833fb420ce"
CONSTRUCTOR_COMMIT = "a92c459340d0f76c3578a49f10cbb7968d07c156"
CONSTRUCTOR_TREE = "2dabeee664c946325eb34ed4f833aa547a961344"
OPENING_COMMIT = "1c6519d89335dde215e93887de074ea4e6d6464a"
OPENING_TREE = "ff8a33e13952e86b27f184e3d8c40e768fbeb110"
CANONICAL_COMMIT = "fb667bfe33ef9e945a82e9a23b615e67f5f39c0f"
CANONICAL_TREE = "117850b25cd94f865cb85e681c465b8260dd9c6a"

EXPECTED_SOURCES = {
    "ops/research-team/PROTOCOL.md": (11222, "c3fbec5b483426fcce97a523ba1ea1edc3e561cb33a1c4e5e957674e4270a246"),
    str(CYCLE_DIR / "CYCLE.md").replace("\\", "/"): (11012, "9f88215d6b9fdacd5318c056d27322b0339f2c04bbbe5ce378f45d6ac4d515cb"),
    str(CYCLE_DIR / "OPENING_STATE.json").replace("\\", "/"): (5569, "442081ba35778ba103ff4caccf274329b8694e826a7349fdf5b30fb662514e00"),
    str(CYCLE_DIR / "WORK_ORDERS.yaml").replace("\\", "/"): (7900, "3ba2bb478e6efe2f28d385204bb698b0308854731eb8d36a10093b91943c7901"),
    str(CYCLE_DIR / "verify_opening_state.py").replace("\\", "/"): (7462, "064a8c6944b33238abd8555c79a8304269d85755716c7a8aa658ada217dfd760"),
    str(CYCLE_DIR / "MID_CYCLE_CHECKPOINT.json").replace("\\", "/"): (4549, "fd0e4c908d0418bcb642d8c3cc821d135384c72aef50c02d0b8cfa70f1e84cec"),
    str(CYCLE_DIR / "verify_mid_cycle.py").replace("\\", "/"): (7898, "136976e4b84c5d227014b03d2e5f4ecced04b26d76ccbe71b77f64d8e1bfa22d"),
    "ai/omreal/data/CANONICAL_RESEARCH_STATE_V10.json": (6535, "405e1f34789e999d2b8725881a4b99c1db81cec3ecfa70abcdfa9b3fbb7a46bf"),
    "ai/omreal/verify_canonical_research_state_v10.py": (13118, "662267d9d8692c6724ab0b55472b3ca262461cce864a7cbb8bd9296bef788917"),
    "ops/research-team/cycles/2026-09-02-d3-triple-critical-saturation-component-gate1/CLOSING_MANIFEST.json": (8258, "f64592cf7f5bd991a7085ebc0f6197ed0b5361f6605a053fc0ad814a1dbff428"),
    "ops/research-team/cycles/2026-09-02-d3-triple-critical-saturation-component-gate1/CYCLE_REPORT.md": (9584, "89daf49e419b23bcdf91830c883a8ba381c226da2a366ef894c64cb3465073d6"),
    "ops/team/d3-mixed-carrier-topology/THEOREM_MEMO.md": (11362, "131ec929171abf633b18e4eefbd1b45ec8aeea97b9d2d1a6f89a73cb205b7f76"),
    "ops/team/d3-mixed-carrier-topology/RESULT.json": (18496, "7e54007c1bb97be457cbdc039c5520267cd39e39e08a930828b42708443a99e5"),
    "ops/team/d3-mixed-carrier-naturality/NATURALITY_MEMO.md": (13465, "a24821526bd0e89a1473e887d60c6e38c9e28f8d65c6a86e7f5e0d3a5d2cdb86"),
    "ops/team/d3-mixed-carrier-naturality/RESULT.json": (10798, "2911e7478a31090582dda2aeeb5e952ab84cf83946bcd5f29d3900813309e3e0"),
    "ops/team/theorem-reset-falsifier/FINDINGS.md": (6659, "893ecc8d530e7af0970cc4bb232fb34e99cb8fc5e0e6b073c93d423c7313420f"),
    "ops/team/theorem-reset-falsifier/RESULT.json": (10935, "c955c6886ed611ae915d56b21a57740f27acb5fb750b22f1900aa58e2996c663"),
    "ai/omreal/9DVL_THEOREM_PROSPECTUS.md": (23473, "9d7fa818ef48ec1df8d7cadc8525d6d705377f2f1294d9eba692dc15a2533cb7"),
    "ai/omreal/DIAG3_JOINED_FLOW_TRIANGLE.md": (16265, "20aafd28f9624ca595a44e3124934baa4d33b942b6c8eca6bff210fedb114c8a"),
    "ai/omreal/verify_diag3_joined_flow_triangle.py": (9283, "ac01851b53d4bed1c859f74bad2e71a5025825fe7accdac13263f5d6518a0944"),
    "ai/omreal/DIAG3_SINGLE_BAD_TWO_SKELETON.md": (13943, "141da1b6d9fcd4f601e79871aaa5d06cb98721ece928a0d0d5af83518bddf71f"),
    "ai/omreal/verify_diag3_single_bad_two_skeleton.py": (7350, "0ae6a9d54abcddbeb68be882083c52e1e6a9735941cea42eebacdf91ef77bda4"),
    "ai/omreal/verify_diag3_row2599_common_proper_escape.py": (13638, "6b426e94181a0d447f79d70e3eb6f64f2f34227d88b9ae1fa0a87f9539c4297c"),
    "ai/omreal/verify_diag3_row2599_h1_radial_gap.py": (7893, "437358967ebf6a7ea362fe95314e58de3243b6959777be3cee534b982d6ab81e"),
    "ops/team/d3-mixed-100-carrier-constructor/THEOREM_ATTEMPT.md": (10047, "b2195e1a52600975be9ab2a0b3fb3139ba19242aa08803c96fe58f7b085b27dc"),
    "ops/team/d3-mixed-100-carrier-constructor/RESULT.json": (9829, "7df547c8de5cc7259107829e3c34ca427992be978517991cab249d209d4c1785"),
    "ops/team/d3-mixed-100-carrier-constructor/SOURCE_MANIFEST.json": (5672, "b5a670667f34964bdfd668cab7442b9b146cad9d27a548d9e2b7c35e4f146b00"),
    "ops/team/d3-mixed-100-carrier-constructor/verify_constructor.py": (17474, "5cb3cf0ebacf5a40027096e9a1a1c82550f706c31abbbd3c0c4d18bc8a4a2c1c"),
    "ops/team/d3-mixed-100-carrier-falsifier/FINDINGS.md": (8185, "ec5b43253ba71b244bf496d37ceb182a335c8e08f6260bb079f6f538135b16a6"),
    "ops/team/d3-mixed-100-carrier-falsifier/RESULT.json": (9107, "7bc792fe6e4ee8b555de50b42b47cbc713fbc9f5918e7a082a35dac57ff2aa8c"),
    "ops/team/d3-mixed-100-carrier-falsifier/SOURCE_MANIFEST.json": (3946, "193194958d475dc8cb76153ef1af30f99f2f5e1998d1e5db819ef151b37ae642"),
    "ops/team/d3-mixed-100-carrier-falsifier/interface_independence_fixture.json": (3629, "205f109543695a25dc99eea6650e60467c971d6f2f12319b3f06fa2c4ef37061"),
    "ops/team/d3-mixed-100-carrier-falsifier/verify_falsifier.py": (25497, "690f735f5efd7c4ffb7ddd666dc76a597ce299363f861a269456a9ec1709ba14"),
}

C0 = ("v0", "v1", "v2")
C1 = ("e01", "e12", "e20", "r0a", "r1a", "r1b", "r2b", "r2c", "r0c")
C2 = ("T", "S01", "S12", "S20", "H0", "H1", "H2")
D1_BOUNDARIES = {
    "e01": {"v0": -1, "v1": 1},
    "e12": {"v1": -1, "v2": 1},
    "e20": {"v2": -1, "v0": 1},
    "r0a": {"v0": -1}, "r1a": {"v1": -1}, "r1b": {"v1": -1},
    "r2b": {"v2": -1}, "r2c": {"v2": -1}, "r0c": {"v0": -1},
}
D2_BOUNDARIES = {
    "T": {"e01": 1, "e12": 1, "e20": 1},
    "S01": {"e01": 1, "r0a": -1, "r1a": 1},
    "S12": {"e12": 1, "r1b": -1, "r2b": 1},
    "S20": {"e20": 1, "r2c": -1, "r0c": 1},
    "H0": {"r0a": 1, "r0c": -1},
    "H1": {"r1a": -1, "r1b": 1},
    "H2": {"r2b": -1, "r2c": 1},
}
ALPHA = [-1, 1, 1, 1, 1, 1, 1]
FACE_GENERATORS = [
    "support_loss", "zero_weight", "chart_transition", "parent_boundary",
    "parent_rank", "witness_rank", "residual_wall",
]


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_bytes(commit: str, path: str) -> bytes:
    proc = subprocess.run(
        ["git", "show", f"{commit}:{path}"], cwd=ROOT,
        check=True, capture_output=True,
    )
    return proc.stdout


def git_commit(commit: str) -> str:
    return subprocess.run(
        ["git", "cat-file", "-p", commit], cwd=ROOT,
        check=True, capture_output=True, text=True,
    ).stdout


def json_at(commit: str, path: str) -> dict:
    return json.loads(git_bytes(commit, path).decode("utf-8"))


def matrix_from_boundaries(rows: tuple[str, ...], columns: tuple[str, ...], boundaries: dict) -> list[list[int]]:
    return [[int(boundaries[column].get(row, 0)) for column in columns] for row in rows]


def matrix_rank(matrix: list[list[int]]) -> int:
    work = [[Fraction(value) for value in row] for row in matrix]
    if not work:
        return 0
    rows, columns = len(work), len(work[0])
    pivot_row = 0
    for column in range(columns):
        pivot = next((row for row in range(pivot_row, rows) if work[row][column]), None)
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        scale = work[pivot_row][column]
        work[pivot_row] = [entry / scale for entry in work[pivot_row]]
        for row in range(rows):
            if row != pivot_row and work[row][column]:
                factor = work[row][column]
                work[row] = [a - factor * b for a, b in zip(work[row], work[pivot_row])]
        pivot_row += 1
    return pivot_row


def determinant(matrix: list[list[int]]) -> int:
    size = len(matrix)
    require(all(len(row) == size for row in matrix), "determinant requires square matrix")
    if size == 0:
        return 1
    work = [[Fraction(value) for value in row] for row in matrix]
    sign = 1
    value = Fraction(1)
    for column in range(size):
        pivot = next((row for row in range(column, size) if work[row][column]), None)
        if pivot is None:
            return 0
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            sign *= -1
        pivot_value = work[column][column]
        value *= pivot_value
        for entry in range(column, size):
            work[column][entry] /= pivot_value
        for row in range(column + 1, size):
            factor = work[row][column]
            if factor:
                for entry in range(column, size):
                    work[row][entry] -= factor * work[column][entry]
    require(value.denominator == 1, "integer matrix acquired nonintegral determinant")
    return sign * value.numerator


def has_unit_minor(matrix: list[list[int]], size: int) -> bool:
    for rows in itertools.combinations(range(len(matrix)), size):
        for columns in itertools.combinations(range(len(matrix[0])), size):
            minor = [[matrix[row][column] for column in columns] for row in rows]
            if abs(determinant(minor)) == 1:
                return True
    return False


def matmul(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [[sum(left[i][k] * right[k][j] for k in range(len(right)))
             for j in range(len(right[0]))] for i in range(len(left))]


def matvec(matrix: list[list[int]], vector: list[int]) -> list[int]:
    return [sum(a * b for a, b in zip(row, vector)) for row in matrix]


def compose_permutations(left: tuple[int, ...], right: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(left[right[index]] for index in range(len(left)))


def verify_manifest(manifest: dict, check_files: bool) -> None:
    require(manifest["format"] == "d3-mixed-100-independent-verifier-source-manifest-v1", "manifest format")
    require(manifest["cycle_id"] == "2026-09-03-d3-mixed-block-100-universal-carrier-gate1", "manifest cycle")
    require(manifest["track_id"] == "d3-mixed-100-independent-verifier", "manifest track")
    require(manifest["branch"] == "research/lane-d3-mixed-100-independent-verifier-20260903", "manifest branch")
    require((manifest["lane_opening_commit"], manifest["lane_opening_tree"]) == (LANE_OPENING_COMMIT, LANE_OPENING_TREE), "manifest lane opening")
    require((manifest["integrated_evidence_commit"], manifest["integrated_evidence_tree"]) == (INTEGRATED_COMMIT, INTEGRATED_TREE), "manifest integrated evidence")
    require((manifest["opening_commit"], manifest["opening_tree"]) == (OPENING_COMMIT, OPENING_TREE), "manifest opening")
    require((manifest["canonical_base_commit"], manifest["canonical_base_tree"]) == (CANONICAL_COMMIT, CANONICAL_TREE), "manifest canonical")
    entries = {row["path"]: (row["bytes"], row["sha256"]) for row in manifest["sources"]}
    require(len(entries) == len(manifest["sources"]) == 33, "manifest source count/uniqueness")
    require(entries == EXPECTED_SOURCES, "manifest source set or pin")
    require(manifest["source_drift"] is False, "manifest source drift")
    require(manifest["producer_code_imported_or_executed_as_acceptance_logic"] is False, "producer logic independence")
    require(manifest["network_sources"] == [], "network sources")
    if check_files:
        for relative, (length, digest) in EXPECTED_SOURCES.items():
            disk = (ROOT / relative).read_bytes()
            frozen = git_bytes(LANE_OPENING_COMMIT, relative)
            require(len(disk) == len(frozen) == length, f"source length drift: {relative}")
            require(sha256(disk).hexdigest() == sha256(frozen).hexdigest() == digest, f"source hash drift: {relative}")


def verify_git_graph() -> None:
    expected = {
        LANE_OPENING_COMMIT: (LANE_OPENING_TREE, INTEGRATED_COMMIT),
        INTEGRATED_COMMIT: (INTEGRATED_TREE, CONSTRUCTOR_COMMIT),
        CONSTRUCTOR_COMMIT: (CONSTRUCTOR_TREE, OPENING_COMMIT),
        OPENING_COMMIT: (OPENING_TREE, CANONICAL_COMMIT),
    }
    for commit, (tree, parent) in expected.items():
        payload = git_commit(commit)
        require(f"tree {tree}\n" in payload, f"wrong Git tree for {commit}")
        require(f"parent {parent}\n" in payload, f"wrong Git parent for {commit}")
    require(f"tree {CANONICAL_TREE}\n" in git_commit(CANONICAL_COMMIT), "wrong canonical tree")


def verify_control(opening: dict, midpoint: dict, constructor: dict, falsifier: dict) -> None:
    require(opening["canonical"]["score"] == "2/9", "opening ledger")
    require(opening["canonical"]["pair_residual"] == opening["canonical"]["pair_coverage"] == "UNKNOWN", "opening pair accounting")
    require(opening["canonical"]["triple_residual"] == 1162302, "opening triple residual")
    require(opening["proof_distance"]["selected_route_open_count"] == 2, "opening route residual")
    require(opening["proof_distance"]["minimum_acceptable_decrease"] == "PROVE_O3_AND_O4_OR_EXACTLY_DISPROVE_THEIR_FULL_QUANTIFIED_CONJUNCTION", "opening endpoint")
    require(opening["route_baseline"]["formal_taxonomy_is_global_denominator"] is False, "opening false denominator")
    require(opening["route_baseline"]["provisional_3_of_10_is_end_to_end_coverage"] is False, "opening false coverage")

    source_pins = opening["source_pins"]
    for relative, digest in source_pins.items():
        require(relative in EXPECTED_SOURCES, f"opening source absent from independent manifest: {relative}")
        require(EXPECTED_SOURCES[relative][1] == digest, f"opening pin mismatch: {relative}")

    require(midpoint["opening"] == {"commit": OPENING_COMMIT, "tree": OPENING_TREE}, "midpoint opening")
    require(midpoint["integrated_evidence"] == {"commit": INTEGRATED_COMMIT, "tree": INTEGRATED_TREE}, "midpoint integrated evidence")
    require(midpoint["verdict"]["constructor"] == midpoint["verdict"]["falsifier"] == "NULL", "midpoint lane verdicts")
    require(midpoint["verdict"]["universal_proof"] is False, "midpoint positive overclaim")
    require(midpoint["verdict"]["exact_admissible_universal_obstruction"] is False, "midpoint negative overclaim")
    require(midpoint["verdict"]["positive_token"] is midpoint["verdict"]["negative_token"] is None, "midpoint tokens")
    require(midpoint["verdict"]["repair_authorized"] is False, "midpoint repair")
    require(midpoint["verdict"]["discovery_action"] == "FREEZE_NULL_AND_STOP", "midpoint action")
    require(midpoint["first_missing_edge"]["id"] == "O3_MIXED_GEOMETRIC_RELATIVE_BOUNDARY_SURJECTIVITY", "midpoint edge")
    require(midpoint["first_missing_edge"]["bounded_repair"] is False, "midpoint bounded repair")
    require(midpoint["exact_information"]["formal_kernel_cone_exists"] is True, "midpoint formal cone")
    require(midpoint["exact_information"]["formal_kernel_cone_is_geometric_mixed_proper"] is False, "midpoint geometry scope")
    require(midpoint["exact_information"]["empty_carrier_interpretation_is_actual_9dvl_instance"] is False, "midpoint empty scope")
    require(midpoint["proof_distance"]["opening_vector"] == midpoint["proof_distance"]["midpoint_vector"], "midpoint vector drift")
    require(midpoint["proof_distance"]["selected_route_opening"] == midpoint["proof_distance"]["selected_route_midpoint"], "midpoint route drift")
    require(midpoint["proof_distance"]["minimum_acceptable_decrease_met"] is False, "midpoint decrease")
    require(midpoint["proof_distance"]["trajectory"] == "STALLED", "midpoint trajectory")
    require(midpoint["accounting"]["ledger_delta"] == "0/9", "midpoint ledger")
    require(midpoint["accounting"]["formal_taxonomy_is_global_denominator"] is False, "midpoint denominator")
    for relative, digest in midpoint["source_pins"].items():
        require(EXPECTED_SOURCES[relative][1] == digest, f"midpoint producer pin mismatch: {relative}")

    require(constructor["handoff"] == "NULL" and constructor["assessment"] == "NULL_STALLED_STOP", "constructor handoff")
    require(constructor["positive_token"] is constructor["negative_token"] is None, "constructor tokens")
    require(constructor["constructor_self_acceptance"] is False, "constructor self acceptance")
    target = constructor["target_status"]
    require(target["O3_proved"] is target["O4_proved"] is target["full_quantifier_obstruction_proved"] is False, "constructor endpoint overclaim")
    require(constructor["row2599_diagnostic"]["certified_mixed_d3_cells"] == 0, "constructor invented mixed cell")
    require(constructor["row2599_diagnostic"]["absence_is_nonexistence_proof"] is False, "constructor absence overclaim")
    require(constructor["naturality_frontier"]["mixed_degree_three_face_functor_constructed"] is False, "constructor mixed functor")
    require(constructor["naturality_frontier"]["arbitrary_flag_equality_proved"] is False, "constructor flag overclaim")

    require(falsifier["handoff"] == "NO_UNIVERSAL_OBSTRUCTION_FOUND_WITHIN_FROZEN_SCOPE", "falsifier handoff")
    require(falsifier["classification"] == "NULL", "falsifier class")
    require(falsifier["universal_counterexample_found"] is falsifier["full_quantifier_negative_proved"] is False, "falsifier negative overclaim")
    require(falsifier["finite_independence_fixture"]["actual_negative_instance"] is False, "falsifier fixture promotion")
    require(falsifier["proof_distance"]["strict_decrease"] is False, "falsifier false decrease")
    require(falsifier["proof_distance"]["canonical_ledger_delta"] == "0/9", "falsifier ledger")


def verify_producer_manifests(constructor_manifest: dict, falsifier_manifest: dict) -> None:
    for producer_manifest in (constructor_manifest, falsifier_manifest):
        sources = producer_manifest["sources"]
        require(len({row["path"] for row in sources}) == len(sources), "producer duplicate source")
        for row in sources:
            relative = row["path"]
            require((row["bytes"], row["sha256"]) == EXPECTED_SOURCES.get(relative), f"producer source pin mismatch: {relative}")
    require(not any(constructor_manifest["restrictions"].values()), "constructor scope restriction violation")
    require(falsifier_manifest["source_drift"] is False, "falsifier source drift")
    require(falsifier_manifest["network_sources"] == falsifier_manifest["constructor_sources"] == [], "falsifier source independence")


def verify_row2599(result: dict, constructor: dict, falsifier: dict, fixture: dict) -> None:
    d1 = matrix_from_boundaries(C0, C1, D1_BOUNDARIES)
    d2 = matrix_from_boundaries(C1, C2, D2_BOUNDARIES)
    require(matmul(d1, d2) == [[0] * 7 for _ in range(3)], "row2599 boundary squared")
    require(matrix_rank(d1) == 3 and matrix_rank(d2) == 6, "row2599 ranks")
    require(has_unit_minor(d1, 3), "partial_1 not integrally onto")
    require(has_unit_minor(d2, 6), "partial_2 missing unit maximal minor")
    require(matvec(d2, ALPHA) == [0] * 9 and math.gcd(*map(abs, ALPHA)) == 1, "primitive kernel class")
    require(len(C2) - matrix_rank(d2) == 1, "kernel rank")

    lower = fixture["lower_interface"]
    require(lower["C0_basis"] == list(C0) and lower["C1_basis"] == list(C1) and lower["C2_basis"] == list(C2), "fixture bases")
    require(lower["partial_1_rows"] == d1 and lower["partial_2_rows"] == d2, "fixture boundary drift")
    require(lower["primitive_kernel_class"] == ALPHA, "fixture primitive drift")
    require(lower["expected_ranks"] == {"partial_1": 3, "partial_2": 6, "C2": 7, "kernel_partial_2": 1}, "fixture ranks")

    canary = constructor["row2599_diagnostic"]
    require(canary["relative_chain_ranks"] == {"partial_1": 3, "partial_2": 6, "C2": 7}, "constructor row ranks")
    require(canary["primitive_class"] == ALPHA and canary["relative_homology"] == {"H0": 0, "H1": 0, "H2": "Z"}, "constructor row homology")
    finite = falsifier["finite_independence_fixture"]
    require((finite["rank_partial_1"], finite["rank_partial_2"], finite["rank_C2"]) == (3, 6, 7), "falsifier row ranks")
    require(finite["primitive_class"] == ALPHA, "falsifier row primitive")

    rebuilt = result["row2599_independent_reconstruction"]
    require(rebuilt["ranks"] == {"C0": 3, "C1": 9, "C2": 7, "partial_1": 3, "partial_2": 6, "kernel_partial_2": 1}, "result rebuilt ranks")
    require(rebuilt["partial_1_partial_2_zero"] and rebuilt["partial_1_integrally_surjective"] and rebuilt["partial_2_unit_maximal_minor"], "result rebuilt algebra")
    require(rebuilt["partial_2_nonzero_smith_invariants"] == [1] * 6, "result Smith invariants")
    require(rebuilt["primitive_kernel_generator"] == ALPHA, "result kernel")
    require(rebuilt["homology"] == {"H0": 0, "H1": 0, "H2": "Z"}, "result homology")
    require(rebuilt["geometric_mixed_C3_columns_certified"] == 0, "result invented C3")
    require(rebuilt["scope"] == "LOCAL_DIAGNOSTIC_NOT_GLOBAL_DENOMINATOR_OR_O3_WITNESS", "result row scope")


def verify_category(result: dict, fixture: dict) -> None:
    category = fixture["specialization_category"]
    require(category["face_generators"] == FACE_GENERATORS, "face generators")
    dimension = len(FACE_GENERATORS)
    objects = list(range(1 << dimension))
    morphisms = [(source, target) for source in objects for target in objects if source & ~target == 0]
    require(len(objects) == 2**dimension == 128, "Boolean object count")
    require(len(morphisms) == 3**dimension == 2187, "Boolean morphism count")
    local_triples = ((0, 0, 0), (0, 0, 1), (0, 1, 1), (1, 1, 1))
    composable_pairs = list(itertools.product(local_triples, repeat=dimension))
    require(len(composable_pairs) == 4**dimension == 16384, "Boolean composable-pair count")
    for coordinates in composable_pairs:
        require(all(a <= b <= c for a, b, c in coordinates), "noncomposable Boolean triple")

    s3 = set(itertools.permutations(range(3)))
    identity = (0, 1, 2)
    require(len(s3) == 6 and identity in s3, "S3 order/identity")
    for p in s3:
        require(any(compose_permutations(p, q) == compose_permutations(q, p) == identity for q in s3), "S3 inverse")
        for q in s3:
            require(compose_permutations(p, q) in s3, "S3 closure")
            for r in s3:
                require(compose_permutations(compose_permutations(p, q), r) == compose_permutations(p, compose_permutations(q, r)), "S3 associativity")
    c2 = {0, 1}
    require(all((a + b) % 2 in c2 for a in c2 for b in c2), "C2 closure")
    direct_product = {(p, c) for p in s3 for c in c2}
    require(len(direct_product) == 12, "S3 x C2 order")

    require(category["boolean_object_count"] == 128 and category["boolean_morphism_count"] == 2187, "fixture category counts")
    require(category["active_block_permutation_group"] == "S3" and category["active_block_permutation_order"] == 6, "fixture S3")
    require(category["monodromy_group"] == "C2" and category["monodromy_order"] == 2, "fixture C2")
    require(category["lower_chain_representation"] == "TRIVIAL_IDENTITY_ON_THE_DISPLAYED_COMPLEX", "fixture nontrivial representation")
    require(category["parent_boundary_is_not_automatically_true_infinity"] is True, "fixture infinity distinction")

    rebuilt = result["finite_category_reconstruction"]
    require((rebuilt["boolean_face_coordinates"], rebuilt["boolean_objects"], rebuilt["boolean_morphisms"], rebuilt["composable_arrow_pairs"]) == (7, 128, 2187, 16384), "result category counts")
    require(rebuilt["boolean_thin_category_associative"] and rebuilt["all_finite_flags_coherent_by_associativity_and_identity_representation"], "result flag coherence")
    require((rebuilt["active_block_group_order"], rebuilt["monodromy_group_order"], rebuilt["direct_product_symmetry_order"]) == (6, 2, 12), "result symmetry orders")
    require(rebuilt["representation"] == "TRIVIAL_IDENTITY", "result representation")
    require(rebuilt["actual_full_source_face_category_constructed"] is False, "result actual category overclaim")
    require(rebuilt["scope_note"] == "2187_COUNTS_ONLY_BOOLEAN_COMPARABLE_PAIRS_NOT_GROUP_DECORATED_MORPHISMS", "result category scope")


def verify_logic(result: dict, fixture: dict) -> None:
    cone = result["formal_kernel_cone_lemma"]
    require(cone["valid_for_finite_diagrams_of_finite_free_integral_lower_complexes"], "cone lemma validity")
    require(cone["finite_free"] and cone["integral_fill_for_every_kernel_class"], "cone algebra")
    require(cone["identities_compositions_automorphisms_and_all_flags_strict"], "cone coherence")
    require(cone["scope"] == "FORMAL_ALGEBRAIC_ONLY", "cone scope")
    require(not any(cone[key] for key in ("proves_genuinely_mixed_semialgebraic_realization", "proves_properness_or_true_parent_infinity", "proves_O3_or_O4")), "cone geometric overclaim")

    expansions = fixture["two_expansions_of_the_same_lower_interface"]
    formal = expansions["formal_kernel_cone"]
    empty = expansions["empty_geometric_carrier_interpretation"]
    require(formal["partial_3_columns"] == [ALPHA] and formal["fills_primitive_class_integrally"] is True, "fixture formal cone")
    require(formal["certifies_genuinely_mixed_semialgebraic_realization"] is False, "fixture cone geometric overclaim")
    require(empty["C3_basis"] == [] and empty["primitive_class_remains_unfilled"] is True, "fixture empty expansion")
    require(empty["actual_9dvl_admissibility_established"] is False, "fixture empty actual promotion")

    boundary = result["logical_non_entailment_boundary"]
    require(boundary["declared_interface_determines_lower_C0_C1_C2_and_specializations"], "lower interface")
    require(boundary["declared_interface_contains_geometric_mixed_C3_universe"] is False, "invented interface C3")
    require(boundary["formal_cone_is_an_algebraic_expansion"] is True and boundary["formal_cone_is_an_admissible_geometric_carrier"] is False, "formal cone boundary")
    require(boundary["empty_carrier_is_a_syntactic_non_entailment_expansion"] is True, "non-entailment")
    require(boundary["empty_carrier_actual_9dvl_admissibility_established"] is boundary["non_entailment_is_an_exact_admissible_counterexample"] is False, "negative overclaim")
    require(boundary["conclusion"] == "NEITHER_POSITIVE_NOR_NEGATIVE_TOKEN_JUSTIFIED", "logical conclusion")


def verify_result(result: dict) -> None:
    require(result["format"] == "d3-mixed-100-independent-verifier-result-v1", "result format")
    require(result["cycle_id"] == "2026-09-03-d3-mixed-block-100-universal-carrier-gate1", "result cycle")
    require(result["track_id"] == "d3-mixed-100-independent-verifier" and result["role"] == "independent-verifier", "result track/role")
    require(result["branch"] == "research/lane-d3-mixed-100-independent-verifier-20260903", "result branch")
    require(result["owned_surface"] == "ops/team/d3-mixed-100-independent-verifier", "result surface")
    require(result["lane_opening"] == {"commit": LANE_OPENING_COMMIT, "tree": LANE_OPENING_TREE}, "result lane opening")
    require(result["frozen_integrated_evidence"] == {"commit": INTEGRATED_COMMIT, "tree": INTEGRATED_TREE}, "result integrated evidence")
    require(result["status"] == "PASS" and result["verdict"] == "NULL_STALLED_STOP_INDEPENDENTLY_CONFIRMED" and result["handoff"] == "NULL", "result verdict")
    require(result["positive_token"] is result["negative_token"] is None, "result tokens")
    acceptance = result["acceptance"]
    require(acceptance["constructor_null_confirmed"] and acceptance["falsifier_null_confirmed"], "lane nulls")
    require(acceptance["producer_agreement_used_as_acceptance"] is False, "producer agreement acceptance")
    require(acceptance["O3_universal_mixed_chain"] == acceptance["O4_arbitrary_flag_coherence"] == "OPEN", "O3/O4 status")
    require(acceptance["universal_positive_proved"] is acceptance["exact_admissible_full_quantifier_negative_proved"] is False, "endpoint overclaim")
    require(acceptance["first_missing_edge"] == "O3_MIXED_GEOMETRIC_RELATIVE_BOUNDARY_SURJECTIVITY", "first edge")

    sources = result["source_reconstruction"]
    require(sources["inputs_pinned"] == 33, "source count")
    require(all(sources[key] for key in ("all_bytes_and_sha256_match_frozen_midpoint", "all_bytes_and_sha256_match_disk", "opening_source_pins_reconciled", "midpoint_producer_pins_reconciled", "git_commit_tree_parent_chain_reconstructed")), "source reconstruction")
    require(sources["producer_verifier_code_imported_or_executed"] is False, "producer code dependence")

    require(set(result["quantifier_audit"].values()) == {"OPEN", "FORMALLY_CONED_GEOMETRICALLY_OPEN", "FORMALLY_TRIVIAL_FIXTURE_ONLY_GEOMETRICALLY_OPEN", "OPEN_NOT_ENCODED_BY_FORMAL_CONE"}, "quantifier status set")
    distance = result["proof_distance"]
    require(distance["canonical_opening_vector"] == distance["canonical_closing_vector"], "canonical distance drift")
    require(distance["selected_route_opening"] == distance["selected_route_closing"] == ["O3_universal_mixed_chain", "O4_arbitrary_flag_coherence"], "route distance drift")
    require(distance["strict_decrease"] is distance["minimum_acceptable_decrease_met"] is False, "false decrease")
    require((distance["canonical_ledger_before"], distance["canonical_ledger_after"], distance["canonical_ledger_delta"]) == ("2/9", "2/9", "0/9"), "ledger")
    require(distance["trajectory"] == "STALLED" and distance["required_action"] == "STOP", "trajectory/action")
    require(distance["same_route_continue"] is distance["successor_selected"] is distance["formal_3_of_10_is_global_or_end_to_end_coverage"] is False, "strategy overclaim")
    require(result["hostile_mutations"] == {"required_minimum": 24, "implemented": 45, "all_rejected": True}, "hostile contract")
    scope = result["scope_compliance"]
    require(scope["edited_only_owned_surface"] is True, "owned surface")
    require(not any(value for key, value in scope.items() if key != "edited_only_owned_surface"), "scope violation")
    require(result["verification"] == {"command": "python -B ops/team/d3-mixed-100-independent-verifier/verify_independent.py", "python_standard_library_only": True, "producer_modules_imported": False}, "verification contract")
    require(len(result["nonconsequences"]) == 8 and "NO_SUCCESSOR_SELECTION" in result["nonconsequences"], "nonconsequences")


def verify_all(documents: dict, manifest: dict, check_files: bool = False) -> None:
    result = documents["result"]
    opening = documents["opening"]
    midpoint = documents["midpoint"]
    constructor = documents["constructor"]
    falsifier = documents["falsifier"]
    fixture = documents["fixture"]
    verify_manifest(manifest, check_files=check_files)
    verify_result(result)
    verify_control(opening, midpoint, constructor, falsifier)
    verify_producer_manifests(documents["constructor_manifest"], documents["falsifier_manifest"])
    verify_row2599(result, constructor, falsifier, fixture)
    verify_category(result, fixture)
    verify_logic(result, fixture)
    if check_files:
        verify_git_graph()
        cycle = git_bytes(LANE_OPENING_COMMIT, str(CYCLE_DIR / "CYCLE.md").replace("\\", "/")).decode("utf-8")
        orders = git_bytes(LANE_OPENING_COMMIT, str(CYCLE_DIR / "WORK_ORDERS.yaml").replace("\\", "/")).decode("utf-8")
        review = (HERE / "REVIEW.md").read_text(encoding="utf-8")
        for phrase in ("Minimum acceptable decrease", "formal ten-shape taxonomy", "Positive handoff", "Negative handoff", "Null handoff"):
            require(phrase in cycle, f"cycle contract phrase missing: {phrase}")
        for phrase in ("independent-verifier", "No producer acceptance import", "No O1/O2/O5/O6 construction"):
            require(phrase in orders, f"work-order phrase missing: {phrase}")
        for phrase in ("NULL_STALLED_STOP_INDEPENDENTLY_CONFIRMED", "Kernel-cone lemma", "Finite category check", "This review selects no successor", "45 hostile"):
            require(phrase in review, f"review phrase missing: {phrase}")


def set_path(document: dict, path: tuple[object, ...], value: object) -> None:
    target = document
    for part in path[:-1]:
        target = target[part]  # type: ignore[index]
    target[path[-1]] = value  # type: ignore[index]


def hostile_mutations(documents: dict, manifest: dict) -> int:
    mutations = [
        ("verdict-positive", "result", lambda x: set_path(x, ("verdict",), "PROVED")),
        ("positive-token", "result", lambda x: set_path(x, ("positive_token",), "PROVED_UNIVERSAL_MIXED_100_CARRIER_AND_COHERENCE")),
        ("negative-token", "result", lambda x: set_path(x, ("negative_token",), "DISPROVED_UNIVERSAL_MIXED_100_CARRIER_BY_EXACT_ADMISSIBLE_OBSTRUCTION")),
        ("close-o3", "result", lambda x: set_path(x, ("acceptance", "O3_universal_mixed_chain"), "PROVED")),
        ("close-o4", "result", lambda x: set_path(x, ("acceptance", "O4_arbitrary_flag_coherence"), "PROVED")),
        ("trust-producer-agreement", "result", lambda x: set_path(x, ("acceptance", "producer_agreement_used_as_acceptance"), True)),
        ("source-count", "result", lambda x: set_path(x, ("source_reconstruction", "inputs_pinned"), 32)),
        ("source-drift", "manifest", lambda x: set_path(x, ("source_drift",), True)),
        ("drop-source", "manifest", lambda x: x["sources"].pop()),
        ("source-hash", "manifest", lambda x: set_path(x, ("sources", 0, "sha256"), "0" * 64)),
        ("midpoint-commit", "result", lambda x: set_path(x, ("lane_opening", "commit"), INTEGRATED_COMMIT)),
        ("midpoint-tree", "manifest", lambda x: set_path(x, ("lane_opening_tree",), INTEGRATED_TREE)),
        ("row-rank-d1", "result", lambda x: set_path(x, ("row2599_independent_reconstruction", "ranks", "partial_1"), 2)),
        ("row-rank-d2", "result", lambda x: set_path(x, ("row2599_independent_reconstruction", "ranks", "partial_2"), 5)),
        ("row-alpha", "result", lambda x: set_path(x, ("row2599_independent_reconstruction", "primitive_kernel_generator", 0), -2)),
        ("row-smith", "result", lambda x: set_path(x, ("row2599_independent_reconstruction", "partial_2_nonzero_smith_invariants", 0), 2)),
        ("invent-geometric-c3", "result", lambda x: set_path(x, ("row2599_independent_reconstruction", "geometric_mixed_C3_columns_certified"), 1)),
        ("cone-invalid", "result", lambda x: set_path(x, ("formal_kernel_cone_lemma", "valid_for_finite_diagrams_of_finite_free_integral_lower_complexes"), False)),
        ("cone-geometric", "result", lambda x: set_path(x, ("formal_kernel_cone_lemma", "proves_genuinely_mixed_semialgebraic_realization"), True)),
        ("cone-o3", "result", lambda x: set_path(x, ("formal_kernel_cone_lemma", "proves_O3_or_O4"), True)),
        ("category-objects", "result", lambda x: set_path(x, ("finite_category_reconstruction", "boolean_objects"), 127)),
        ("category-morphisms", "result", lambda x: set_path(x, ("finite_category_reconstruction", "boolean_morphisms"), 2186)),
        ("category-flags", "result", lambda x: set_path(x, ("finite_category_reconstruction", "composable_arrow_pairs"), 16383)),
        ("category-symmetry", "result", lambda x: set_path(x, ("finite_category_reconstruction", "direct_product_symmetry_order"), 6)),
        ("category-actual", "result", lambda x: set_path(x, ("finite_category_reconstruction", "actual_full_source_face_category_constructed"), True)),
        ("interface-has-c3", "result", lambda x: set_path(x, ("logical_non_entailment_boundary", "declared_interface_contains_geometric_mixed_C3_universe"), True)),
        ("formal-is-geometric", "result", lambda x: set_path(x, ("logical_non_entailment_boundary", "formal_cone_is_an_admissible_geometric_carrier"), True)),
        ("empty-is-actual", "result", lambda x: set_path(x, ("logical_non_entailment_boundary", "empty_carrier_actual_9dvl_admissibility_established"), True)),
        ("nonentailment-negative", "result", lambda x: set_path(x, ("logical_non_entailment_boundary", "non_entailment_is_an_exact_admissible_counterexample"), True)),
        ("close-route", "result", lambda x: set_path(x, ("proof_distance", "selected_route_closing"), [])),
        ("ledger-promote", "result", lambda x: set_path(x, ("proof_distance", "canonical_ledger_after"), "3/9")),
        ("strict-decrease", "result", lambda x: set_path(x, ("proof_distance", "strict_decrease"), True)),
        ("converging", "result", lambda x: set_path(x, ("proof_distance", "trajectory"), "CONVERGING")),
        ("continue", "result", lambda x: set_path(x, ("proof_distance", "same_route_continue"), True)),
        ("false-denominator", "result", lambda x: set_path(x, ("proof_distance", "formal_3_of_10_is_global_or_end_to_end_coverage"), True)),
        ("constructor-positive", "constructor", lambda x: set_path(x, ("handoff",), "PROVED_UNIVERSAL_MIXED_100_CARRIER_AND_COHERENCE")),
        ("constructor-o3", "constructor", lambda x: set_path(x, ("target_status", "O3_proved"), True)),
        ("constructor-cell", "constructor", lambda x: set_path(x, ("row2599_diagnostic", "certified_mixed_d3_cells"), 1)),
        ("falsifier-negative", "falsifier", lambda x: set_path(x, ("handoff",), "DISPROVED_UNIVERSAL_MIXED_100_CARRIER_BY_EXACT_ADMISSIBLE_OBSTRUCTION")),
        ("falsifier-counterexample", "falsifier", lambda x: set_path(x, ("universal_counterexample_found",), True)),
        ("falsifier-actual", "falsifier", lambda x: set_path(x, ("finite_independence_fixture", "actual_negative_instance"), True)),
        ("fixture-cone-geometric", "fixture", lambda x: set_path(x, ("two_expansions_of_the_same_lower_interface", "formal_kernel_cone", "certifies_genuinely_mixed_semialgebraic_realization"), True)),
        ("fixture-empty-actual", "fixture", lambda x: set_path(x, ("two_expansions_of_the_same_lower_interface", "empty_geometric_carrier_interpretation", "actual_9dvl_admissibility_established"), True)),
        ("opening-ledger", "opening", lambda x: set_path(x, ("canonical", "score"), "3/9")),
        ("midpoint-decrease", "midpoint", lambda x: set_path(x, ("proof_distance", "minimum_acceptable_decrease_met"), True)),
    ]
    require(len(mutations) == 45, "hostile mutation count")
    rejected = 0
    for name, target_name, mutate in mutations:
        candidate_documents = copy.deepcopy(documents)
        candidate_manifest = copy.deepcopy(manifest)
        target = candidate_manifest if target_name == "manifest" else candidate_documents[target_name]
        mutate(target)
        try:
            verify_all(candidate_documents, candidate_manifest, check_files=False)
        except (AssertionError, KeyError, TypeError, ValueError, IndexError):
            rejected += 1
        else:
            raise AssertionError(f"hostile mutation accepted: {name}")
    return rejected


def main() -> None:
    documents = {
        "result": load_json(HERE / "RESULT.json"),
        "opening": json_at(LANE_OPENING_COMMIT, str(CYCLE_DIR / "OPENING_STATE.json").replace("\\", "/")),
        "midpoint": json_at(LANE_OPENING_COMMIT, str(CYCLE_DIR / "MID_CYCLE_CHECKPOINT.json").replace("\\", "/")),
        "constructor": json_at(LANE_OPENING_COMMIT, "ops/team/d3-mixed-100-carrier-constructor/RESULT.json"),
        "constructor_manifest": json_at(LANE_OPENING_COMMIT, "ops/team/d3-mixed-100-carrier-constructor/SOURCE_MANIFEST.json"),
        "falsifier": json_at(LANE_OPENING_COMMIT, "ops/team/d3-mixed-100-carrier-falsifier/RESULT.json"),
        "falsifier_manifest": json_at(LANE_OPENING_COMMIT, "ops/team/d3-mixed-100-carrier-falsifier/SOURCE_MANIFEST.json"),
        "fixture": json_at(LANE_OPENING_COMMIT, "ops/team/d3-mixed-100-carrier-falsifier/interface_independence_fixture.json"),
    }
    manifest = load_json(HERE / "SOURCE_MANIFEST.json")
    verify_all(documents, manifest, check_files=True)
    rejected = hostile_mutations(documents, manifest)
    print("PASS frozen source pins: 33/33 match midpoint Git bytes and disk")
    print("PASS row2599 independent chain reconstruction: ranks 3/6, primitive kernel Z*alpha, H=(0,0,Z)")
    print("PASS formal kernel cone: integral and strictly functorial, algebraic scope only")
    print("PASS finite category: 128 objects, 2187 Boolean arrows, 16384 composable pairs, trivial S3 x C2 coherence")
    print("PASS logical boundary: neither geometric positive nor admissible negative follows")
    print(f"PASS hostile mutations rejected: {rejected}/45")
    print("VERDICT NULL / STALLED / STOP; O3 and O4 remain 2/2 open; ledger remains 2/9")


if __name__ == "__main__":
    main()
