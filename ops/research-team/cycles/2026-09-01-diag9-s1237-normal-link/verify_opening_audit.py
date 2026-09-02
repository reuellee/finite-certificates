#!/usr/bin/env python3
"""Fail-closed replay of the D9 S12,37 normal-link opening audit."""

from __future__ import annotations

from collections import defaultdict
from copy import deepcopy
import hashlib
import json
from pathlib import Path
import subprocess
import sys

import numpy as np


ROOT = Path(__file__).resolve().parents[4]
HERE = Path(__file__).resolve().parent
DATA = ROOT / "ai" / "omreal" / "data"
BASE = "c55d896cc5c0370e993b793992a2f05d894e0095"
BASE_TREE = "17299e84397aae158a2111cbe01b52f5be24bfd5"
TARGET = "D9_S1237_4SUPPORT_NORMAL_LINK_GATE1"
ACTIVE_DIGEST = "6de7ff2716b65853c04b9a08f44eb98ad8966e1f3525887ffafde0a3b805c154"
FILTER_DIGEST = "cf4689a6b3a2ae10f7988c4823d2b0283efb0fa9ae4f4861029090765499ec59"

EXPECTED_SOURCES = {
    "ops/research-team/PROTOCOL.md": "54f1a15b7774085005707727780b266ffbd4a8edc4687fe14e1e6bc76d229031",
    "ops/research-team/verify_cycle_protocol.py": "4d9e16daed0de08af415e95c746803b512ea8b92c452df6df2c9e09fdcd3b7d1",
    "ai/omreal/data/CANONICAL_RESEARCH_STATE_V2.json": "508d5433d33eeb5be915e1749838d73541a8bd0055c74fac00bdb74ee28e930f",
    "ai/omreal/NINE_DIAGONAL_STATUS.md": "3c360a2f7311bec48a3b5586684b08eadb70fc928530d1287fc68bc5161255ce",
    "ai/omreal/DIAG9_ACTIVE_SECTOR_THEOREM.md": "132a51b92a9813947e7ab7a43b52aafa6b2c789126e31cfc8a7f0773ee30b790",
    "ai/omreal/verify_diag9_active_sector.py": "8317442e095918748397fe302157212333fd908efadfa9c0ab6b5d175599dfd0",
    "ai/omreal/DIAG9_SIGN_GEODESY_AUDIT.md": "64896fa28a76f57344bd246f1546322e1361f6ac57f164ca6199c58938c30903",
    "ai/omreal/NINTH_DIAGONAL_SAFE_GRAPH.md": "8af233ced03055881572353d26d6f3a7d931649a9456fe7018cbc31202f4556e",
    "ai/omreal/DIAG9_GRAPH_TREE_CERTIFICATE.md": "63966868407713f1977b16b2ae8c435eb186d0569ce6239cc91d623a566ceb2e",
    "ai/omreal/DIAG9_GRAPH_COM_AUDIT.md": "4764626a03b1f5f36ee4b7ee53ca2048d3135c1a1f588d79f23d77cbbaa8844c",
    "ai/omreal/data/DIAG9_GRAPH_global_factor_census.npz": "3984ce87e11fd59d804e59568177248e218cd1c7bb07aae0a9f9f746858728bc",
    "ai/omreal/data/DIAG9_GRAPH_row2599_factor_states.npz": "f44b1fccfb4e61273aeceb8796a18098d82c48473e257556ce3d2a22f99b0bcf",
    "ai/omreal/data/ninth_candidate_12_37_antichain.npz": "11ca66549982ec40ce8425d2caed45b418edb73c4eb415a45b39d57e481bd1e4",
    "ai/omreal/data/ninth_candidate_12_37_path.npz": "8db38e00d9bf8701558c27cd4ede3e024db8953ea3ef9873bf0b4fc65ad6bcda",
    "ai/omreal/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_GATE.md": "2b955d7b50213e2a0a750c268ccecbf6ac9d5e9ed3a146b3bb0faf7a4739dddc",
    "ai/omreal/verify_diag3_pair_global_four_support_gate.py": "90b3d747f71d56245607b281166eca3f43cdfdbe8dff3a49327ad81bf9b3c845",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_FOUR_SUPPORT_GATE.json": "d9a16b39966cb1ce404b3df8362b722052fdc0854db331e5bc12aeec4ef9bcef",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json": "956fbe7e5c7b1e04c8873ed9c0f3de9cb5420e3e06f1d5fae4c60f4e0571b364",
    "ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json": "cc279d125605b45d25a3a01f462ad051038102f2bf12574f494a9d261bfc7401",
}

EXPECTED_GROUPS = (
    (1705, 1893, 2076),
    (1704, 5585, 15233),
    (254,),
    (2109,),
)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*arguments: str) -> str:
    result = subprocess.run(
        ["git", *arguments],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def git_bytes(revision: str, relative: str) -> bytes:
    return subprocess.run(
        ["git", "show", f"{revision}:{relative}"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    ).stdout


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def validate_audit(audit: dict) -> None:
    require(audit["format"] == "9dvl-opening-audit-v1", "wrong format")
    require(audit["cycle_id"] == HERE.name, "wrong cycle id")
    require(audit["canonical_base"] == {
        "revision": BASE,
        "tree": BASE_TREE,
        "reconciliation": "PR47_MATH_PLUS_PR46_EVIDENCE",
        "ledger": "2/9",
        "state": "PIVOT_REQUIRED",
    }, "canonical base drift")
    require(audit["authority_epoch"] == {
        "canonical_working_store": "CHATGPT_LIBRARY",
        "recovery_mirror": "GOOGLE_DRIVE_PROJECTS_RESEARCH_BACKUPS",
        "local_scratch": "EPHEMERAL_NOT_AUTHORITY",
        "github": "READ_ONLY_UNTIL_NEW_EXPLICIT_USER_INSTRUCTION",
    }, "authority epoch drift")
    require(audit["opening_verdict"] == "PIVOT_SELECT", "wrong opening verdict")
    require(audit["selected_target"] == TARGET, "wrong target")
    require(audit["strategy_table"] == [
        {"route": TARGET, "scores": [4, 5, 3, 4, 5, 5, 5, 2], "verdict": "PIVOT_SELECT"},
        {"route": "D9_GENERIC_SEED_PROJECTION_ROADMAP", "scores": [4, 5, 4, 3, 3, 4, 3, 3], "verdict": "STOP_IN_FAVOR_OF_NORMAL_LINK_GATE"},
        {"route": "D8_PARENT860_GLOBAL_RELATIVE_COMPLEX", "scores": [5, 2, 5, 3, 4, 4, 2, 5], "verdict": "STOP_MASK6_RETIRED_GLOBAL_COVERAGE_ABSENT"},
        {"route": "D3_Q3_COMPLETE_PARENT_BOUNDARY_ATLAS", "scores": [5, 2, 5, 2, 3, 2, 1, 5], "verdict": "PIVOT_AWAY_SAME_GLOBAL_BLOCKERS"},
    ], "strategy table drift")
    require(audit["independent_endorsements"] == [
        {
            "role": "opening_red_team",
            "verdict": "REVISE_THEN_SELECT",
            "load_bearing_reason": "Tangential face restrictions do not determine the codimension-six inward normal link.",
        },
        {
            "role": "d9_target_auditor",
            "verdict": "ACCEPT",
            "load_bearing_reason": "Complete oriented normal-link and recursive facet analysis is the smallest fail-closed D9 target.",
        },
        {
            "role": "cross_diagonal_auditor",
            "verdict": "SELECT",
            "load_bearing_reason": "D3 and D8 retain their global coverage blockers while this D9 gate has a bounded obstruction class.",
        },
    ], "independent endorsements drift")
    require(audit["source_pins"] == EXPECTED_SOURCES, "source pin map drift")

    replay = audit["exact_replays"]
    require(replay["s1237_family_size"] == 9, "family size drift")
    require(replay["s1237_exact_witnesses"] == 63, "witness count drift")
    require(replay["s1237_regions_nonempty_proper_pairwise_incomparable"] is True, "family validity missing")
    require(replay["s1237_endpoint_charts"] == [12, 37], "endpoint drift")
    require(replay["s1237_exact_path_segments"] == 22711, "path count drift")
    require(replay["s1237_path_consequence"] == "ENDPOINTS_IN_SAME_F_S_COMPONENT", "path consequence drift")
    require(replay["residual_occurrences"] == 84840, "occurrence count drift")
    require(replay["certified_empty_factors"] == 8916, "empty-factor count drift")
    require(replay["candidate_active_factors"] == 3539, "active-factor count drift")
    require(replay["active_sector_semantic_digest"] == ACTIVE_DIGEST, "active digest drift")
    require(replay["sign_geodesy_verdict"] == "NO_GO_NO_COVERAGE_OR_ADJACENCY", "geodesy scope drift")
    require(replay["first_pivot_resultant_new_irreducibles"] == 142, "resultant count drift")

    discovery = audit["tangential_discovery"]
    require(
        discovery["scope"] == "FACE_INTERIOR_TANGENTIAL_FILTER_ONLY_NOT_A_COLLAR_OR_NORMAL_LINK_RESULT",
        "tangential discovery promoted",
    )
    require(discovery["semantic_digest"] == FILTER_DIGEST, "filter digest drift")
    first, second = discovery["supports"]
    require(first["support"] == [3, 1, 15], "first support drift")
    require(first["active_factor_ids"] == [254, 1704, 1705, 1893, 2076, 2109, 5585, 15233], "first factor ids drift")
    require(first["factor_id_groups_by_zero_set"] == [list(group) for group in EXPECTED_GROUPS], "zero-set groups drift")
    require((first["factor_id_count"], first["zero_set_count"]) == (8, 4), "first support census drift")
    require(second == {
        "support": [3, 3, 7],
        "active_factor_ids": [],
        "factor_id_groups_by_zero_set": [],
        "factor_id_count": 0,
        "zero_set_count": 0,
    }, "second support census drift")

    contract = audit["target_contract"]
    require(contract["positive_endpoint"] == "COMPLETE_ORIENTED_NORMAL_LINK_GATE", "positive endpoint drift")
    require(contract["negative_endpoint"] == "NORMAL_LINK_REDUCTION_NO_GO", "negative endpoint drift")
    require(contract["null_endpoint"] == "UNRESOLVED_NORMAL_LINK_STRATUM", "null endpoint drift")
    require(contract["timeout_endpoint"] == "HASH_PINNED_NORMAL_LINK_FRONTIER", "timeout endpoint drift")
    require(contract["must_cover"] == [
        "ALL_3539_ORIENTED_LITERALS",
        "ALL_OCCURRENCES_REPRESENTATIVES_AND_UNIT_SIGNS",
        "BOTH_CERTIFIED_SUPPORTS",
        "ALL_PARENT_SAFE_PROJECTIVE_NORMAL_DIRECTIONS",
        "ALL_RECURSIVE_FACETS_BASES_APICES_SEAMS_AND_COFACES",
        "EXACT_FEASIBILITY_GORDAN_LABELS",
        "EXACT_HIGHER_ORDER_STABILIZATION",
    ], "coverage contract incomplete")
    require(contract["prohibited_claims"] == [
        "TANGENTIAL_FILTER_IS_A_COLLAR",
        "BOUNDARY_FACES_GLUE_OPEN_X_COMPONENTS",
        "SAMPLED_LINK_COVERAGE_IS_COMPLETE",
        "MINCUT_ON_AN_UNCERTIFIED_GRAPH",
        "GLOBAL_ACTIVE_SECTOR_CONNECTIVITY",
        "DIAGONAL_9_PROOF_OR_COUNTEREXAMPLE",
        "THEOREM_LEDGER_PROMOTION",
    ], "prohibited scope incomplete")
    require(contract["resource_ceiling"] == {
        "minutes_per_worker": 30,
        "memory_gib_per_worker": 12,
        "unique_link_polynomials": 10000,
        "certified_link_cells": 100000,
    }, "resource ceiling drift")


def hostile_canaries(audit: dict) -> None:
    mutations = []
    candidate = deepcopy(audit)
    candidate["canonical_base"]["ledger"] = "3/9"
    mutations.append(("false ledger promotion", candidate))
    candidate = deepcopy(audit)
    candidate["authority_epoch"]["github"] = "WRITE_ALLOWED"
    mutations.append(("old publication authority", candidate))
    candidate = deepcopy(audit)
    candidate["exact_replays"]["candidate_active_factors"] = 3538
    mutations.append(("dropped active literal", candidate))
    candidate = deepcopy(audit)
    candidate["tangential_discovery"]["scope"] = "COLLAR_CERTIFICATE"
    mutations.append(("tangential as collar", candidate))
    candidate = deepcopy(audit)
    candidate["tangential_discovery"]["supports"][0]["factor_id_groups_by_zero_set"][0].pop()
    mutations.append(("merged orientation group", candidate))
    candidate = deepcopy(audit)
    candidate["target_contract"]["must_cover"].remove("ALL_RECURSIVE_FACETS_BASES_APICES_SEAMS_AND_COFACES")
    mutations.append(("omitted recursive stratum", candidate))
    candidate = deepcopy(audit)
    candidate["target_contract"]["positive_endpoint"] = "DIAGONAL_9_PROVED"
    mutations.append(("false topology", candidate))
    for index, entry in enumerate(audit["target_contract"]["must_cover"]):
        candidate = deepcopy(audit)
        candidate["target_contract"]["must_cover"][index] = "DUMMY_COVERAGE"
        mutations.append((f"coverage mutation {entry}", candidate))
    for index, entry in enumerate(audit["target_contract"]["prohibited_claims"]):
        candidate = deepcopy(audit)
        candidate["target_contract"]["prohibited_claims"][index] = "DUMMY_PROHIBITION"
        mutations.append((f"scope mutation {entry}", candidate))
    for index, endorsement in enumerate(audit["independent_endorsements"]):
        candidate = deepcopy(audit)
        candidate["independent_endorsements"][index]["role"] = "same_role"
        mutations.append((f"endorsement role mutation {endorsement['role']}", candidate))
        candidate = deepcopy(audit)
        candidate["independent_endorsements"][index]["load_bearing_reason"] = ""
        mutations.append((f"endorsement reason removal {endorsement['role']}", candidate))

    for label, mutated in mutations:
        try:
            validate_audit(mutated)
        except (AssertionError, KeyError, TypeError, ValueError):
            continue
        raise AssertionError(f"hostile canary accepted: {label}")


def validate_repository_and_sources(audit: dict) -> None:
    require(git("rev-parse", f"{BASE}^{{commit}}") == BASE, "base commit missing")
    require(git("rev-parse", f"{BASE}^{{tree}}") == BASE_TREE, "base tree drift")
    for relative, expected in EXPECTED_SOURCES.items():
        path = ROOT / relative
        if relative == "ai/omreal/NINE_DIAGONAL_STATUS.md":
            require(
                hashlib.sha256(git_bytes(BASE, relative)).hexdigest() == expected,
                f"canonical-base source drift {relative}",
            )
            continue
        require(path.is_file(), f"missing source {relative}")
        require(sha256(path) == expected, f"source drift {relative}")
        if relative not in {
            "ops/research-team/PROTOCOL.md",
            "ops/research-team/verify_cycle_protocol.py",
        }:
            require(
                not subprocess.run(
                    ["git", "diff", "--quiet", BASE, "--", relative],
                    cwd=ROOT,
                    check=False,
                ).returncode,
                f"source is not the canonical-base blob {relative}",
            )
    require(audit["source_pins"] == EXPECTED_SOURCES, "audit source pins incomplete")
    protocol = subprocess.run(
        [sys.executable, str(ROOT / "ops" / "research-team" / "verify_cycle_protocol.py")],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    require("PASS research-cycle strategy/storage/publication protocol" in protocol.stdout, "protocol verifier did not pass")


def validate_exact_family_inputs() -> None:
    with np.load(DATA / "ninth_candidate_12_37_antichain.npz", allow_pickle=False) as source:
        require(int(source["parent_index"]) == 2599, "antichain parent drift")
        require(source["signature"].shape == (9,), "antichain signature count drift")
        require(source["feasible_point"].shape[:2] == (7, 9), "antichain feasible census drift")
        require(source["gordan_weight"].shape[:2] == (7, 9), "antichain Gordan census drift")
        require(7 * 9 == 63, "antichain witness arithmetic drift")
    with np.load(DATA / "ninth_candidate_12_37_path.npz", allow_pickle=False) as source:
        require(int(source["parent_index"]) == 2599, "path parent drift")
        require(list(map(int, source["endpoint"])) == [12, 37], "path endpoints drift")
        segments = len(source["update_col_a"]) + len(source["update_col_b"]) + len(source["bridge_col"])
        require(segments == 22711, "path segment census drift")


def encode_polynomial(polynomial) -> list[list[int]]:
    rows = []
    for exponent, coefficient in polynomial:
        require(coefficient.denominator == 1, "nonintegral discovery coefficient")
        rows.append([*map(int, exponent), int(coefficient)])
    return rows


def reconstruct_tangential_filter() -> str:
    sys.path.insert(0, str(ROOT / "ai" / "omreal"))
    import verify_diag9_active_sector as active
    import diag3_pair_global_four_support_core as four_support

    active.verify_pins()
    certificates = active.transported_certificates()
    with np.load(DATA / "DIAG9_GRAPH_global_factor_census.npz", allow_pickle=False) as source:
        fourset_array = np.asarray(source["occurrence_fourset"], dtype=np.uint8)
        occurrence_factor = np.asarray(source["occurrence_factor"], dtype=np.uint32)
        factor_count = len(source["factor_multiplicity"])
    foursets = tuple(tuple(map(int, row)) for row in fourset_array)
    with np.load(DATA / "seeat_parent2599_upper178.npz", allow_pickle=False) as source:
        charts = source["chart_matrix"]
    oriented, conflicting_occurrences = active.oriented_occurrences(
        foursets, certificates, active.topes.derived_rows(charts[0])
    )
    empty_factors = {int(occurrence_factor[index]) for index in conflicting_occurrences}
    require(len(foursets) == 84840, "residual occurrence count drift")
    require(len(empty_factors) == 8916, "empty-factor count drift")

    representative = np.full(factor_count, -1, dtype=np.int64)
    for occurrence_index, factor in enumerate(map(int, occurrence_factor)):
        if representative[factor] < 0:
            representative[factor] = occurrence_index
    require(bool(np.all(representative >= 0)), "factor without representative")
    representative_raw_sign = np.asarray(
        [oriented[index][1] for index in representative], dtype=np.int8
    )
    with np.load(DATA / "ninth_candidate_12_37_antichain.npz", allow_pickle=False) as source:
        signatures = tuple(map(int, source["signature"]))

    family_literals: dict[int, int] = {}
    for signature in signatures:
        for (certificate_data, raw_sign), factor in zip(
            oriented, map(int, occurrence_factor), strict=True
        ):
            if factor in empty_factors:
                continue
            allowed_raw = active.aligned_literal(signature, certificate_data)
            if allowed_raw is None:
                continue
            allowed_representative = (
                allowed_raw * raw_sign * int(representative_raw_sign[factor])
            )
            previous = family_literals.setdefault(factor, allowed_representative)
            require(previous == allowed_representative, "inconsistent factor orientation")
    active_factors = set(family_literals)
    require(len(active_factors) == 3539, "active-factor count drift")

    candidate_ids = four_support.gate.parse_candidates()
    _occurrences, _assignments, factor_polynomials = four_support.labeled.factor_polynomials()
    reports_by_support = {}
    for support in four_support.SUPPORTS:
        _state, reports, _facets = four_support.residual_groups(
            support, factor_polynomials, candidate_ids
        )
        reports_by_support[support] = reports

    empty_polynomials = {
        tuple(sorted(reduced.items())): reduced
        for reports in reports_by_support.values()
        for reduced, report in reports.values()
        if report["status"] == "INTERIOR_EMPTY"
    }
    empty_order = [
        empty_polynomials[key]
        for key in sorted(
            empty_polynomials,
            key=lambda item: (four_support.degree(dict(item)), item),
        )
    ]
    support_maps = {}
    for support, reports in reports_by_support.items():
        wall_map = defaultdict(list)
        for reduced, report in reports.values():
            if report["status"] != "INTERIOR_NONEMPTY":
                continue
            quotient, _removed = four_support.positive_factor_quotient(
                reduced, empty_order
            )
            key = tuple(sorted(quotient.items()))
            wall_map[key].extend(
                factor_id
                for factor_id in report["factor_ids"]
                if factor_id in active_factors
            )
        support_maps[support] = {
            key: tuple(sorted(factor_ids))
            for key, factor_ids in wall_map.items()
            if factor_ids
        }

    first = support_maps[(3, 1, 15)]
    second = support_maps[(3, 3, 7)]
    require(sum(map(len, first.values())) == 8 and len(first) == 4, "first support filter drift")
    require(second == {}, "second support filter drift")
    by_factor_ids = {factor_ids: polynomial for polynomial, factor_ids in first.items()}
    require(set(by_factor_ids) == set(EXPECTED_GROUPS), "factor zero-set grouping drift")
    digest_rows = [
        {
            "support": [3, 1, 15],
            "factor_ids": list(group),
            "polynomial": encode_polynomial(by_factor_ids[group]),
        }
        for group in EXPECTED_GROUPS
    ]
    digest_rows.append({
        "support": [3, 3, 7],
        "factor_ids": [],
        "polynomial": [],
    })
    payload = json.dumps(
        digest_rows, sort_keys=True, separators=(",", ":")
    ).encode("ascii")
    digest = hashlib.sha256(
        b"d9-s1237-four-support-active-wall-filter-v1\0" + payload
    ).hexdigest()
    require(digest == FILTER_DIGEST, "tangential filter semantic digest drift")
    return digest


def main() -> None:
    audit = json.loads((HERE / "OPENING_AUDIT.json").read_text(encoding="utf-8"))
    validate_audit(audit)
    hostile_canaries(audit)
    validate_repository_and_sources(audit)
    validate_exact_family_inputs()
    digest = reconstruct_tangential_filter()
    print(
        "PASS D9 S12,37 opening audit:",
        "base", BASE[:12],
        "ledger 2/9,",
        "3539 active literals,",
        "tangential 8 IDs / 4 zero sets and 0 / 0,",
        "digest", digest,
        "target", TARGET,
    )


if __name__ == "__main__":
    main()
