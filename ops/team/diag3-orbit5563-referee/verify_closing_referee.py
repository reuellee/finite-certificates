#!/usr/bin/env python3
"""Independent closing replay for the D3 orbit-5563 first-gate null.

This checker does not import either worker checker.  It reconstructs the
projected parent automorphism groups by a GF(2) reorientation-orbit test on
all 70 chirotope signs, enumerates the hard factor-triple stabilizer from the
pinned factor action, reconciles both worker manifests parent by parent, and
enforces the fail-closed transport and repository-scope guards.
"""

from __future__ import annotations

import argparse
from collections import Counter
from copy import deepcopy
import hashlib
from itertools import combinations, permutations
import json
from math import factorial
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OMREAL = ROOT / "ai" / "omreal"
sys.path.insert(0, str(OMREAL))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as factor_source  # noqa: E402


OPENING_LOCAL = "bf6050ddc16e01dbff6da07d3d8c3ec31a9ab52f"
OPENING_TREE = "4213fdb2adf5722d1b8a6b70aba4507e959fba6d"
CANDIDATE_LOCAL = "d4e5a228e5ae5472a838672b54ca074ee0738c25"
CANDIDATE_TREE = "dcd0e683a33468194f38353a72ebc84c213b0b35"
OPENING_PUBLISHED = "9e578f6e9d094b3342ca474f0d188428dd44ae7a"
CANDIDATE_PUBLISHED = "af098d1297dd5c82f194d1f4d03a9ac75afafba9"
PROVER_PUBLISHED = "dd4394c3a6131bfeb9b3d1c1adede830b1941535"
FALSIFIER_PUBLISHED = "e5bc85923ab0694482219399e626d0d2255bc926"

PARENT_TYPES = 2_604
FRAMES = factorial(8)
RAW_PRESENTATIONS = PARENT_TYPES * FRAMES
QUOTIENT_CLASSES = 100_086_840
PRESENTATION = (5_563, 16_134, 19_284)
CANONICAL_ROW = (5_563, 4_373, 23_221)
NAMED_TO_CANONICAL = (5, 1, 4, 7, 2, 3, 0, 6)
EXPECTED_ORDER_HISTOGRAM = {
    1: 2_382,
    2: 183,
    3: 10,
    4: 16,
    6: 3,
    8: 6,
    12: 1,
    16: 1,
    24: 2,
}
EXPECTED_CLASS_HISTOGRAM = {
    order: count * (FRAMES // order)
    for order, count in EXPECTED_ORDER_HISTOGRAM.items()
}
REQUIRED_STRATA = (
    "open_parent_points",
    "coordinate",
    "chart_divisor",
    "parent_wall",
    "singular_rank_drop",
    "occurrence_rank",
    "concurrence_rank",
    "extra_factor",
    "simultaneous_wall",
    "true_parent_infinity",
)

CATALOG = OMREAL / "certs_4_8.jsonl"
EXTCOUNTS = ROOT / "ai" / "omgamma" / "data" / "extcount_4_9.jsonl"
PROVER_DIR = ROOT / "ops" / "team" / "diag3-orbit5563-prover"
FALSIFIER_DIR = ROOT / "ops" / "team" / "diag3-orbit5563-falsifier"
PROVER_MANIFEST = PROVER_DIR / "TYPE_FRAME_S8_QUOTIENT_MANIFEST.json"
PROVER_TRANSPORT = PROVER_DIR / "TRANSPORT_CONTRACT.json"
FALSIFIER_MANIFEST = FALSIFIER_DIR / "QUOTIENT_MANIFEST.json"
FALSIFIER_TRANSPORT = FALSIFIER_DIR / "TRANSPORT_CONTRACT.json"

EXPECTED_SHA256 = {
    "ops/team/diag3-orbit5563-prover/CANARIES.json": "09c30f020819d02caa21b543e9e2c8e3f79428a68c3647c96fc403dd22a7d529",
    "ops/team/diag3-orbit5563-prover/PROOF_NOTE.md": "ed3853cd4f0d78cc85801c6978dd9c7e37fd545f2fcdb3a0faef294153bdbdf1",
    "ops/team/diag3-orbit5563-prover/REPLAY_MANIFEST.json": "150684b4190130b26e556858d6cf4bb55619167e48b2bc766b97a228c2265236",
    "ops/team/diag3-orbit5563-prover/RESULT.yaml": "c5d6d9df1e73f96d00a5e4bd5d75c87c0f02bd17d081d5f7e335fb2d85aa8430",
    "ops/team/diag3-orbit5563-prover/TRANSPORT_CONTRACT.json": "099ad1e0518854bed8477fac92731482569c95eb89be4e65090b3972a5a9728b",
    "ops/team/diag3-orbit5563-prover/TYPE_FRAME_S8_QUOTIENT_MANIFEST.json": "95f7d5f362a4af3445ca4f6cffbf8b5b2d812aad45ffd5cc655af9ea1216685b",
    "ops/team/diag3-orbit5563-prover/verify_diag3_orbit5563_prover.py": "a564fce15b42b6e6feca75a6f96b6a0ae7eb8fafa4414fbf2e7b406d67a4e74f",
    "ops/team/diag3-orbit5563-falsifier/FINDINGS.md": "d8ab4bbd11c67846830fa53850f0f7795873a9f3288090ea40510152a8bd86b0",
    "ops/team/diag3-orbit5563-falsifier/QUOTIENT_MANIFEST.json": "911d4ff842e2e962ab2c67d1725037580b6fe2d5fa113f4ccdd4c4786e027b14",
    "ops/team/diag3-orbit5563-falsifier/RESULT.yaml": "d3c38f13ebbcf2e69829bd3d5544e911e5facb5693986fc2c0977f80fd7ee2c9",
    "ops/team/diag3-orbit5563-falsifier/TRANSPORT_CONTRACT.json": "4455a630c3d212f09e844812013e97e2591b2bd813a076fdf243e5f55aee0d2a",
    "ops/team/diag3-orbit5563-falsifier/verify_falsifier_gate.py": "84be5b538afd31ad71acd1385ad2d3170b6d1deb45f4643e81f63ac782ad12bc",
}

CONTROL_SHA256 = {
    "ops/research-team/cycles/2026-08-30-diag3-orbit5563-global-exit/CYCLE.md": "97b5878586a57f54a6820b3f8bb1dea794e47bf1333695235523c9ac160c74a4",
    "ops/research-team/cycles/2026-08-30-diag3-orbit5563-global-exit/CYCLE_REPORT.md": "a2baf8cf0a8e0cfdfc845f38569557e95e2953995ad8964b912ef8738ffa7c5f",
    "ops/research-team/cycles/2026-08-30-diag3-orbit5563-global-exit/WORK_ORDERS.yaml": "cd6182913d08f6ce3ede91e0967e30ac44b75d7cce262571cfe586f357f81a5a",
    "ops/team/diag3-orbit5563-referee/OPENING_HANDOFF.yaml": "c1401692f3c1e624e11193305364afd1371f820cef4a22e88113c1559a5a678a",
    "ops/team/diag3-orbit5563-referee/OPENING_REVIEW.md": "a9ffbd81ea8a2bfb8f2b93f76b6bc345589c282df4d2a5b9834ccce1cfa5e990",
    "ops/team/diag3-orbit5563-referee/OPENING_REREVIEW.md": "616f95abce7c6f1d1e35518d18712d3f5316f7deebfa9d75f76c1851d002ee76",
    "ops/team/diag3-orbit5563-referee/OPENING_REREVIEW_HANDOFF.yaml": "d6034c5b1160ef759cea25724a602a6e1f7e4c2e02fd1bee09b64de0dfbd1497",
    "ops/team/diag3-orbit5563-referee/CLOSING_HANDOFF.yaml": "9386bd77bce6c886046107511abf1efe8f87306c63ba9607ae9aef2ad805b12f",
    "ops/team/diag3-orbit5563-referee/CLOSING_REVIEW.md": "e1801e2782445374f606dfeef51f24694edaaaf494581ee1956738ae74d67a35",
}

CYCLE_DIR = ROOT / "ops" / "research-team" / "cycles" / "2026-08-30-diag3-orbit5563-global-exit"
EXPECTED_D3_PATHS = frozenset(
    (*EXPECTED_SHA256, *CONTROL_SHA256, "ops/team/diag3-orbit5563-referee/verify_closing_referee.py")
)

BASES = tuple(
    sorted(combinations(range(8), 4), key=lambda basis: tuple(reversed(basis)))
)
BASIS_INDEX = {basis: index for index, basis in enumerate(BASES)}


class AuditError(AssertionError):
    """Fail-closed closing-audit error."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        while block := source.read(1 << 20):
            digest.update(block)
    return digest.hexdigest()


def semantic_digest(payload: dict) -> str:
    unsealed = dict(payload)
    unsealed.pop("semantic_sha256", None)
    return hashlib.sha256(
        json.dumps(unsealed, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()


def reseal(payload: dict) -> dict:
    payload["semantic_sha256"] = semantic_digest(payload)
    return payload


def git(*args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
    ).stdout.strip()


def git_optional(*args: str) -> str | None:
    result = subprocess.run(
        ["git", *args],
        cwd=ROOT,
        check=False,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def d3_surface_paths() -> set[str]:
    roots = (CYCLE_DIR, PROVER_DIR, FALSIFIER_DIR, HERE)
    return {
        path.relative_to(ROOT).as_posix()
        for root in roots
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }


def verify_repository_surface() -> str:
    actual_paths = d3_surface_paths()
    require(actual_paths == EXPECTED_D3_PATHS, "D3 governed surface changed")
    for relative, expected in {**EXPECTED_SHA256, **CONTROL_SHA256}.items():
        require(sha256(ROOT / relative) == expected, f"governed artifact changed: {relative}")

    # A full checkout must authenticate the two published historical trees and
    # their exact twelve-file worker delta. Local-only commit IDs are recorded
    # in the handoff, but are deliberately not required from a remote clone.
    opening_tree = git_optional("rev-parse", f"{OPENING_PUBLISHED}^{{tree}}")
    candidate_tree = git_optional("rev-parse", f"{CANDIDATE_PUBLISHED}^{{tree}}")
    if opening_tree is not None or candidate_tree is not None:
        require(opening_tree is not None and candidate_tree is not None, "partial published history")
        require(opening_tree == OPENING_TREE, "published opening tree moved")
        require(candidate_tree == CANDIDATE_TREE, "published candidate tree moved")
        changed = set(
            filter(
                None,
                git("diff", "--name-only", OPENING_PUBLISHED, CANDIDATE_PUBLISHED).splitlines(),
            )
        )
        require(changed == set(EXPECTED_SHA256), "published candidate changed unauthorized files")
        return "FULL_PUBLISHED_HISTORY"

    # GitHub Actions checks out the synthetic pull-request merge at depth one.
    # Historical commits are then intentionally absent. Fail closed unless the
    # repository advertises that exact shallow state, every governed D3 path is
    # present with its pinned digest, and this verifier itself is tracked and
    # unmodified. This is not a generic escape hatch for a damaged full clone.
    require(git("rev-parse", "--is-shallow-repository") == "true", "published history missing from full checkout")
    verifier_relative = str(Path(__file__).resolve().relative_to(ROOT))
    require(
        git("ls-files", "--error-unmatch", verifier_relative) == verifier_relative,
        "closing verifier is not tracked",
    )
    require(
        not git("status", "--porcelain", "--untracked-files=all", "--", *sorted(EXPECTED_D3_PATHS)),
        "governed D3 surface is dirty in shallow checkout",
    )
    return "SHALLOW_PINNED_SURFACE"


def load_parent_signs():
    records = [json.loads(line) for line in CATALOG.read_text().splitlines()]
    require(len(records) == 2_628, "catalog record census")
    realizable = []
    negative_by_basis = [0] * len(BASES)
    for source_index, record in enumerate(records):
        require(record.get("n") == 8 and record.get("r") == 4, "catalog rank")
        chi = record.get("chi", "")
        require(len(chi) == 70 and not (set(chi) - {"+", "-"}), "catalog uniformity")
        if record.get("verdict") != "REALIZABLE":
            continue
        parent = len(realizable)
        realizable.append((source_index, chi))
        for basis, sign in enumerate(chi):
            if sign == "-":
                negative_by_basis[basis] |= 1 << parent
    require(len(realizable) == PARENT_TYPES, "realizable parent census")
    return tuple(realizable), tuple(negative_by_basis)


def odd_permutation(values) -> bool:
    return bool(
        sum(
            values[left] > values[right]
            for left in range(len(values))
            for right in range(left + 1, len(values))
        )
        & 1
    )


def sign_action_row(basis) -> int:
    """GF(2) row for global sign plus eight element reorientations."""

    row = 1
    for element in basis:
        row ^= 1 << (element + 1)
    return row


def sign_action_coordinates():
    rows = tuple(sign_action_row(basis) for basis in BASES)
    span = {0: 0}
    pivot_indices = []
    for index, row in enumerate(rows):
        if row in span:
            continue
        bit = 1 << len(pivot_indices)
        pivot_indices.append(index)
        span.update({value ^ row: coeff ^ bit for value, coeff in tuple(span.items())})
    require(len(pivot_indices) == 8 and len(span) == 256, "sign-action rank")
    require(all(row in span for row in rows), "sign-action row span")
    return rows, tuple(pivot_indices), tuple(span[row] for row in rows)


def reconstruct_parent_automorphisms(negative_by_basis):
    """Enumerate every projected automorphism without either worker's gauge."""

    _rows, pivots, coordinates = sign_action_coordinates()
    all_parents = (1 << PARENT_TYPES) - 1
    ranks = [[] for _ in range(PARENT_TYPES)]
    mask_digest = hashlib.sha256(b"diag3-orbit5563-referee-gf2-masks-v1\0")
    byte_width = (PARENT_TYPES + 7) // 8
    frame_count = 0
    for frame_rank, frame in enumerate(permutations(range(8))):
        frame_count += 1
        delta = []
        for basis_index, positions in enumerate(BASES):
            ordered = tuple(frame[position] for position in positions)
            pulled = negative_by_basis[BASIS_INDEX[tuple(sorted(ordered))]]
            if odd_permutation(ordered):
                pulled ^= all_parents
            delta.append(pulled ^ negative_by_basis[basis_index])
        pivot_delta = tuple(delta[index] for index in pivots)
        matches = all_parents
        for value, coordinate in zip(delta, coordinates, strict=True):
            predicted = 0
            for pivot_index, pivot_value in enumerate(pivot_delta):
                if coordinate & (1 << pivot_index):
                    predicted ^= pivot_value
            matches &= all_parents ^ (value ^ predicted)
            if not matches:
                break
        mask_digest.update(matches.to_bytes(byte_width, "little"))
        while matches:
            low = matches & -matches
            ranks[low.bit_length() - 1].append(frame_rank)
            matches ^= low
    require(frame_count == FRAMES, "frame census")
    return tuple(tuple(values) for values in ranks), mask_digest.hexdigest()


def verify_hard_triple(all_frames):
    occurrences, occurrence_factor, _polynomials = factor_source.factor_polynomials()
    factor_occurrence = {}
    factor_members = {}
    for occurrence in occurrences:
        factor = occurrence_factor[occurrence]
        factor_occurrence.setdefault(factor, occurrence)
        factor_members.setdefault(factor, []).append(occurrence)

    # Re-establish that the source factor quotient is equivariant on the seven
    # adjacent transpositions, without calling the source's acceptance helper.
    generator_maps = []
    for left in range(7):
        permutation = list(range(8))
        permutation[left], permutation[left + 1] = permutation[left + 1], permutation[left]
        generator_maps.append(
            tuple(
                factor_source.TRIPLE_INDEX[
                    tuple(sorted(permutation[value] for value in triple))
                ]
                for triple in factor_source.TRIPLES
            )
        )
    for members in factor_members.values():
        for mapping in generator_maps:
            images = {
                occurrence_factor[tuple(sorted(mapping[index] for index in member))]
                for member in members
            }
            require(len(images) == 1, "factor action not well defined")

    target = frozenset(PRESENTATION)
    stabilizer = []
    images = set()
    named_image = None
    for frame_rank, frame in enumerate(all_frames):
        mapping = tuple(
            factor_source.TRIPLE_INDEX[
                tuple(sorted(frame[value] for value in triple))
            ]
            for triple in factor_source.TRIPLES
        )
        image = tuple(
            sorted(
                occurrence_factor[
                    tuple(sorted(mapping[index] for index in factor_occurrence[factor]))
                ]
                for factor in PRESENTATION
            )
        )
        images.add(image)
        if frozenset(image) == target:
            stabilizer.append(frame_rank)
        if frame == NAMED_TO_CANONICAL:
            named_image = image
    require(stabilizer == [0], "hard-triple stabilizer")
    require(len(images) == FRAMES, "hard-triple orbit")
    require(set(named_image or ()) == set(CANONICAL_ROW), "named presentation map")
    return stabilizer


def falsifier_rows(manifest):
    sources = manifest["parent_stream"]["catalog_source_indices"]
    encoding = manifest["automorphism_group_encoding"]
    default = encoding["default"]
    exceptions = {row["parent_index"]: row for row in encoding["exceptions"]}
    require(len(exceptions) == len(encoding["exceptions"]), "duplicate falsifier exception")
    return tuple(
        (
            sources[index],
            row["automorphism_order"],
            row["quotient_class_count"],
            tuple(row["automorphism_frame_ranks"]),
        )
        for index in range(PARENT_TYPES)
        for row in (exceptions.get(index, default),)
    )


def validate_artifacts(prover, falsifier, prover_transport, falsifier_transport, source_indices, ranks):
    require(prover.get("semantic_sha256") == semantic_digest(prover), "prover semantic seal")
    require(falsifier.get("semantic_sha256") == semantic_digest(falsifier), "falsifier semantic seal")
    require(prover_transport.get("semantic_sha256") == semantic_digest(prover_transport), "prover transport seal")
    require(falsifier_transport.get("semantic_sha256") == semantic_digest(falsifier_transport), "falsifier transport seal")

    orders = tuple(len(values) for values in ranks)
    classes = tuple(FRAMES // order for order in orders)
    require(Counter(orders) == Counter(EXPECTED_ORDER_HISTOGRAM), "parent automorphism histogram")
    require(sum(classes) == QUOTIENT_CLASSES, "quotient class count")
    require(sum(order * count for order, count in zip(orders, classes, strict=True)) == RAW_PRESENTATIONS, "raw multiplicity sum")

    prover_rows = tuple(tuple(row) for row in prover["catalog"]["entries"])
    expected_rows = tuple(zip(source_indices, orders, classes, strict=True))
    require(prover_rows == expected_rows, "prover parent rows")
    falsifier_manifest_rows = falsifier_rows(falsifier)
    require(
        tuple((source, order, count) for source, order, count, _frame_ranks in falsifier_manifest_rows)
        == expected_rows,
        "falsifier parent rows",
    )
    require(
        tuple(frame_ranks for _source, _order, _count, frame_ranks in falsifier_manifest_rows)
        == ranks,
        "falsifier automorphism elements",
    )

    pquot = prover["quotient_definition"]
    ftotals = falsifier["totals"]
    require(pquot["number_of_quotient_classes"] == QUOTIENT_CLASSES, "prover quotient total")
    require(pquot["sum_of_raw_multiplicities"] == RAW_PRESENTATIONS, "prover raw total")
    require(ftotals["quotient_classes"] == QUOTIENT_CLASSES, "falsifier quotient total")
    require(ftotals["quotient_multiplicity_sum"] == RAW_PRESENTATIONS, "falsifier raw total")
    require(
        {int(key): value for key, value in pquot["parent_type_automorphism_order_histogram"].items()}
        == EXPECTED_ORDER_HISTOGRAM,
        "prover order histogram",
    )
    require(
        {int(key): value for key, value in ftotals["automorphism_order_distribution"].items()}
        == EXPECTED_ORDER_HISTOGRAM,
        "falsifier order histogram",
    )
    require(
        {int(key): value for key, value in pquot["quotient_class_raw_multiplicity_histogram"].items()}
        == EXPECTED_CLASS_HISTOGRAM,
        "prover class histogram",
    )
    require(
        {int(key): value for key, value in ftotals["quotient_class_multiplicity_histogram"].items()}
        == EXPECTED_CLASS_HISTOGRAM,
        "falsifier class histogram",
    )
    require(prover["group"]["selected_stabilizer_order"] == 1, "prover hard stabilizer")
    require(falsifier["quotient_definition"]["triple_stabilizer_frame_ranks"] == [0], "falsifier hard stabilizer")

    pguards = prover_transport["scope_guards"]
    require(prover_transport["terminal_classification"] == "null", "prover null")
    require(prover_transport["missing_transport"]["status"] == "MISSING", "prover missing closure transport")
    require(prover_transport["missing_transport"]["attachment_artifacts"] == [], "prover attachment absence")
    require(not pguards["representative_matrix_covers_full_realization_space"], "prover representative promotion")
    require(not pguards["artificial_scope_boundary_is_true_parent_infinity"], "prover artificial infinity")
    require(not pguards["topology_computation_permitted_after_this_gate"], "prover topology stop")
    require(pguards["row_count_before"] == pguards["row_count_after"] == 1_162_302, "prover row change")
    require(pguards["ledger_change_recommended"] == "none", "prover ledger change")

    fdomain = falsifier_transport["quantified_domain"]
    obligations = {item["id"]: item["status"] for item in falsifier_transport["obligations"]}
    require(tuple(fdomain["required_strata"]) == REQUIRED_STRATA, "falsifier stratum census")
    require(fdomain["representative_matrix_promotion"] == "PROHIBITED", "falsifier representative promotion")
    require(falsifier_transport["exact_open_cell_transport"]["status"] == "PASS", "falsifier open transport")
    require(obligations == {
        "Q1_EXACT_TYPE_FRAME_TRIPLE_QUOTIENT": "PASS",
        "Q2_OPEN_CELL_SIGN_AND_CHART_TRANSPORT": "PASS",
        "Q3_COMPLETE_PARENT_BOUNDARY_ATLAS": "MISSING",
        "Q4_COMPONENT_AND_RANK_DROP_ATTACHMENTS": "BLOCKED_BY_Q3",
        "Q5_TRUE_PARENT_INFINITY_TAGS": "BLOCKED_BY_Q3",
    }, "falsifier obligation graph")
    require(falsifier_transport["smallest_missing_obligation"]["id"] == "Q3_COMPLETE_PARENT_BOUNDARY_ATLAS", "smallest missing obligation")
    require(not any(falsifier_transport["canary_policy"].values()), "falsifier hostile scope policy")
    fgate = falsifier_transport["first_gate"]
    require(fgate["classification"] == "null", "falsifier null")
    require(not fgate["topology_computation_authorized"], "falsifier topology stop")
    require(fgate["count_change"] == 0 and fgate["ledger_change"] == "NONE", "falsifier accounting")


def expect_reject(label: str, operation) -> None:
    try:
        operation()
    except (AuditError, KeyError, TypeError, ValueError, ZeroDivisionError):
        return
    raise AuditError(f"hostile mutation accepted: {label}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--surface-only",
        action="store_true",
        help="verify the full-history or fail-closed shallow repository surface, then stop",
    )
    args = parser.parse_args()
    surface_mode = verify_repository_surface()
    print("PASS repository surface", surface_mode)
    if args.surface_only:
        return
    realizable, negative_by_basis = load_parent_signs()
    ranks, gf2_mask_digest = reconstruct_parent_automorphisms(negative_by_basis)
    all_frames = tuple(permutations(range(8)))
    verify_hard_triple(all_frames)

    extcounts = {row["i"]: row for row in map(json.loads, EXTCOUNTS.read_text().splitlines())}
    require(set(extcounts) == set(range(2_628)), "extcount source census")
    require(
        all(extcounts[source]["stab"] == 2 * len(ranks[index]) for index, (source, _chi) in enumerate(realizable)),
        "external stabilizer reconciliation",
    )

    prover = json.loads(PROVER_MANIFEST.read_text())
    falsifier = json.loads(FALSIFIER_MANIFEST.read_text())
    prover_transport = json.loads(PROVER_TRANSPORT.read_text())
    falsifier_transport = json.loads(FALSIFIER_TRANSPORT.read_text())
    source_indices = tuple(source for source, _chi in realizable)
    validate_artifacts(prover, falsifier, prover_transport, falsifier_transport, source_indices, ranks)

    hostile_cases = []
    corrupt = deepcopy(prover)
    corrupt["catalog"]["entries"].pop()
    reseal(corrupt)
    hostile_cases.append(("missing parent row", corrupt, falsifier, prover_transport, falsifier_transport))
    corrupt_f = deepcopy(falsifier)
    corrupt_f["totals"]["quotient_class_multiplicity_histogram"]["1"] -= 1
    reseal(corrupt_f)
    hostile_cases.append(("missing quotient multiplicity", prover, corrupt_f, prover_transport, falsifier_transport))
    corrupt = deepcopy(prover)
    corrupt["group"]["selected_stabilizer_order"] = 2
    reseal(corrupt)
    hostile_cases.append(("nontrivial hard stabilizer", corrupt, falsifier, prover_transport, falsifier_transport))
    corrupt_ft = deepcopy(falsifier_transport)
    corrupt_ft["canary_policy"]["artificial_boundaries_are_true_infinity"] = True
    reseal(corrupt_ft)
    hostile_cases.append(("artificial boundary as infinity", prover, falsifier, prover_transport, corrupt_ft))
    corrupt_ft = deepcopy(falsifier_transport)
    corrupt_ft["quantified_domain"]["required_strata"].remove("singular_rank_drop")
    reseal(corrupt_ft)
    hostile_cases.append(("omitted rank-drop stratum", prover, falsifier, prover_transport, corrupt_ft))
    corrupt_ft = deepcopy(falsifier_transport)
    corrupt_ft["quantified_domain"]["representative_matrix_promotion"] = "ALLOWED"
    reseal(corrupt_ft)
    hostile_cases.append(("representative promotion", prover, falsifier, prover_transport, corrupt_ft))
    corrupt_ft = deepcopy(falsifier_transport)
    corrupt_ft["obligations"][2]["status"] = "PASS"
    reseal(corrupt_ft)
    hostile_cases.append(("false boundary-atlas completion", prover, falsifier, prover_transport, corrupt_ft))
    for label, pvalue, fvalue, ptvalue, ftvalue in hostile_cases:
        expect_reject(
            label,
            lambda pvalue=pvalue, fvalue=fvalue, ptvalue=ptvalue, ftvalue=ftvalue: validate_artifacts(
                pvalue,
                fvalue,
                ptvalue,
                ftvalue,
                source_indices,
                ranks,
            ),
        )

    order_histogram = dict(sorted(Counter(map(len, ranks)).items()))
    summary = {
        "candidate_local": CANDIDATE_LOCAL,
        "candidate_tree": CANDIDATE_TREE,
        "candidate_published": CANDIDATE_PUBLISHED,
        "opening_published": OPENING_PUBLISHED,
        "prover_published": PROVER_PUBLISHED,
        "falsifier_published": FALSIFIER_PUBLISHED,
        "parent_types": PARENT_TYPES,
        "frames": FRAMES,
        "raw_presentations": RAW_PRESENTATIONS,
        "quotient_classes": QUOTIENT_CLASSES,
        "order_histogram": order_histogram,
        "hard_triple_stabilizer": [0],
        "gf2_mask_stream_sha256": gf2_mask_digest,
        "prover_manifest_semantic_sha256": prover["semantic_sha256"],
        "falsifier_manifest_semantic_sha256": falsifier["semantic_sha256"],
        "smallest_missing_obligation": "Q3_COMPLETE_PARENT_BOUNDARY_ATLAS",
        "terminal_classification": "null",
        "row_before": 1_162_302,
        "row_after": 1_162_302,
        "ledger_before": "2/9",
        "ledger_after": "2/9",
        "strategy": "PIVOT",
        "hostile_canaries": len(hostile_cases),
    }
    summary_digest = hashlib.sha256(
        json.dumps(summary, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    print(
        "PASS independent GF2 parent reconstruction:",
        f"parents={PARENT_TYPES}",
        f"frames={FRAMES}",
        f"classes={QUOTIENT_CLASSES}",
        f"raw={RAW_PRESENTATIONS}",
    )
    print("PASS parent automorphism histogram", order_histogram)
    print("PASS both manifests agree parent-by-parent and element-by-element")
    print("PASS hard-triple stabilizer is identity; orbit size=40320")
    print("PASS exact open-cell transport only; Q3 boundary atlas is missing")
    print(f"PASS {len(hostile_cases)}/{len(hostile_cases)} independent hostile mutations rejected")
    print("PASS no topology, row, ledger, or unauthorized candidate-surface change")
    print("GF2_MASK_STREAM_SHA256", gf2_mask_digest)
    print("CLOSING_SEMANTIC_SHA256", summary_digest)
    print("ACCEPT terminal=null row=1162302 ledger=2/9 strategy=PIVOT")


if __name__ == "__main__":
    main()
