#!/usr/bin/env python3
"""Independent frozen-head referee for the universal-D9 cut opening gate.

The checker never imports current-cycle producer acceptance modules.  It reads
all reviewed evidence from the frozen Git tree, validates every producer
source pin, independently reconstructs the decisive type-36, chamber-graph,
boundary, polynomial-countermodel, portability, scope, and ledger facts, and
then attacks its own acceptance predicate with hostile mutations.

Use ``--full-source-replay`` to additionally rerun the canonical 142-resultant
audit and the predecessor's source-derived independent referee kernel.  Those
two replays are intentionally external to this acceptance predicate.
"""

from __future__ import annotations

import argparse
from collections import Counter, deque
from copy import deepcopy
from fractions import Fraction
from functools import reduce
import hashlib
from io import BytesIO
from itertools import combinations, permutations
import json
from math import gcd
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
CYCLE = "ops/research-team/cycles/2026-09-01-d9-universal-cut"
FROZEN = "39035a9c35b27a9893db393dbb8a9ec1b621754d"
FROZEN_TREE = "e05535180e3522521f5f151f956a9f407f5a2956"
FROZEN_PARENT = "9cb3652b00c0a07901b6fa32dd3f7d03987cfb66"
FROZEN_PARENT_TREE = "37f605949a2fbfdf8be8983b6ea24121eea4a177"
MATH_BASE = "cbe84ccd7273252c81fd4da17ee360a284d2a2a6"
MATH_BASE_TREE = "da3cd6feca1052ea14ed5036413c72b8f7fadc2a"
OPENING = "6cbd1b4a7d3ed61bee268b6b54cbfadeece90f0e"
OPENING_TREE = "84eaf80b30e1f366b8f959bd6435a217762636b3"
HISTORICAL = "ca730426cdd5847ae262ddc29c6f4ae98369eba3"
TARGET = "D9_UNIVERSAL_FEASIBLE_COMPONENT_CUT_GATE1"
ENDPOINT = "UNIVERSAL_CUT_SCHEMA_COVERAGE_GAP"

CANDIDATE = f"{CYCLE}/CLOSING_CANDIDATE.json"
REPORT = f"{CYCLE}/CYCLE_REPORT.md"
PROVER = "ops/team/d9-universal-cut-prover"
CIRCUITS = "ops/team/d9-universal-cut-circuits"
BOUNDARY = "ops/team/d9-universal-cut-boundary"
FALSIFIER = "ops/team/d9-universal-cut-falsifier"
CERTIFICATE = "ops/team/d9-universal-cut-certificate"
MANIFEST = HERE / "CLOSING_MANIFEST.json"
RESULT = HERE / "RESULT.json"
FINDINGS = HERE / "FINDINGS.md"

EXPECTED_TYPES = (36, 37, 38, 39, 41, 42, 44, 46, 47, 48, 49, 50, 51)
EXPECTED_FAILURES = {
    "NO_COMPLETE_COMPACTIFIED_COMPONENT_FAITHFUL_INCIDENCE_OBJECT",
    "THIRTEEN_LOCAL_TYPES_NOT_PROJECTION_CLOSED",
    "MEMORYLESS_LOCAL_GRAMMAR_CANNOT_DETERMINE_GLOBAL_CUTS",
    "NO_STRICT_COFACE_ATTACHMENT_FOR_RECURSIVE_FACET_WALL",
    "NO_PROVED_D9_GLOBAL_PROPERTY_REJECTS_COUNTERMODEL_MECHANISM",
    "NO_CERTIFIED_10000_TYPE_OR_250000_INSTANCE_BOUND",
}
EXPECTED_NONCONSEQUENCES = {
    "NO_SOURCE_REALIZED_D9_COUNTEREXAMPLE",
    "NO_UNIVERSAL_D9_CUT_COVERAGE_THEOREM",
    "NO_EXHAUSTIVE_OBSTRUCTION_UNSAT_RESULT",
    "NO_STRICT_OPEN_PARENT_SEPARATOR",
    "NO_WEIGHTED_RECURSIVE_LINK_CLASSIFICATION",
    "NO_DIAGONAL_9_RESULT",
    "NO_9DVL_SCORE_CHANGE",
}


class Reject(AssertionError):
    """The frozen closing candidate failed an exact acceptance gate."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def git(*arguments: str, binary: bool = False) -> str | bytes:
    return subprocess.check_output(
        ["git", *arguments], cwd=ROOT, text=not binary,
        env={"GIT_NO_LAZY_FETCH": "1"},
    ).strip() if not binary else subprocess.check_output(
        ["git", *arguments], cwd=ROOT, env={"GIT_NO_LAZY_FETCH": "1"}
    )


def frozen_bytes(path: str) -> bytes:
    return git("show", f"{FROZEN}:{path}", binary=True)  # type: ignore[return-value]


def frozen_text(path: str) -> str:
    return frozen_bytes(path).decode("utf-8")


def frozen_json(path: str) -> dict[str, Any]:
    value = json.loads(frozen_text(path))
    require(isinstance(value, dict), f"frozen JSON object required: {path}")
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def canonical(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")


def semantic(domain: bytes, value: dict[str, Any]) -> str:
    copy = deepcopy(value)
    copy.pop("semantic_sha256", None)
    return sha256_bytes(domain + b"\0" + canonical(copy))


def verify_revision_and_authority() -> None:
    require(git("rev-parse", f"{FROZEN}^{{commit}}") == FROZEN, "frozen commit absent")
    require(git("rev-parse", f"{FROZEN}^{{tree}}") == FROZEN_TREE, "frozen tree drift")
    require(git("rev-parse", f"{FROZEN}^") == FROZEN_PARENT, "frozen parent drift")
    require(git("rev-parse", f"{FROZEN_PARENT}^{{tree}}") == FROZEN_PARENT_TREE, "integration tree drift")
    require(git("rev-parse", f"{MATH_BASE}^{{tree}}") == MATH_BASE_TREE, "math base drift")
    require(git("rev-parse", f"{OPENING}^{{tree}}") == OPENING_TREE, "opening tree drift")
    changed = str(git("diff", "--name-only", FROZEN_PARENT, FROZEN)).splitlines()
    require(set(changed) == {CANDIDATE, REPORT, f"{CYCLE}/verify_closing_candidate.py"},
            "closing candidate changed non-control-plane paths")
    cycle = frozen_text(f"{CYCLE}/CYCLE.md")
    orders = frozen_text(f"{CYCLE}/WORK_ORDERS.yaml")
    authority = " ".join((cycle + "\n" + orders).replace("`", "").split())
    for phrase in (
        "ChatGPT Library as the canonical durable working branch",
        "Google Drive `Projects/research-backups`",
        "GitHub is read-only",
        "do not push commits",
        "Local scratch is ephemeral and is not an authority",
    ):
        require(phrase.replace("`", "") in authority, f"authority phrase missing: {phrase}")


def extract_source_pins(manifest: dict[str, Any]) -> list[tuple[str, str]]:
    if "files" in manifest:
        return list(manifest["files"].items())
    if "inputs" in manifest:
        return [(row["path"], row["sha256"]) for row in manifest["inputs"]]
    if "sources" in manifest:
        source = manifest["sources"]
        return list(source.items()) if isinstance(source, dict) else [
            (row["path"], row["sha256"]) for row in source
        ]
    if "used_sha256" in manifest:
        return list(manifest["used_sha256"].items())
    raise Reject("unrecognized source-manifest layout")


def verify_all_source_pins(candidate: dict[str, Any]) -> tuple[int, int]:
    manifest_paths = [
        f"{PROVER}/SOURCE_MANIFEST.json",
        f"{CIRCUITS}/SOURCE_MANIFEST.json",
        f"{BOUNDARY}/SOURCE_MANIFEST.json",
        f"{FALSIFIER}/SOURCE_MANIFEST.json",
        f"{CERTIFICATE}/SOURCE_MANIFEST.json",
    ]
    pins: list[tuple[str, str]] = []
    for path in manifest_paths:
        pins.extend(extract_source_pins(frozen_json(path)))
    unique: dict[str, str] = {}
    for path, expected in pins:
        require(path not in unique or unique[path] == expected, f"conflicting source pins: {path}")
        unique[path] = expected
        require(sha256_bytes(frozen_bytes(path)) == expected, f"source pin drift: {path}")
    for path, expected in candidate["artifacts"].items():
        require(sha256_bytes(frozen_bytes(path)) == expected, f"candidate artifact drift: {path}")
    return len(pins), len(unique)


# Small exact polynomial kernel, independent of the prover track.
NVAR = 9
ZERO = (0,) * NVAR


def p_clean(p: dict[tuple[int, ...], int]) -> dict[tuple[int, ...], int]:
    return {m: int(c) for m, c in p.items() if c}


def p_const(c: int) -> dict[tuple[int, ...], int]:
    return {} if c == 0 else {ZERO: c}


def p_var(i: int) -> dict[tuple[int, ...], int]:
    exponent = [0] * NVAR
    exponent[i] = 1
    return {tuple(exponent): 1}


def p_add(*values: dict[tuple[int, ...], int]) -> dict[tuple[int, ...], int]:
    result: dict[tuple[int, ...], int] = {}
    for value in values:
        for monomial, coefficient in value.items():
            result[monomial] = result.get(monomial, 0) + coefficient
    return p_clean(result)


def p_neg(value: dict[tuple[int, ...], int]) -> dict[tuple[int, ...], int]:
    return {m: -c for m, c in value.items()}


def p_mul(*values: dict[tuple[int, ...], int]) -> dict[tuple[int, ...], int]:
    result = p_const(1)
    for value in values:
        product: dict[tuple[int, ...], int] = {}
        for left, lc in result.items():
            for right, rc in value.items():
                exponent = tuple(left[i] + right[i] for i in range(NVAR))
                product[exponent] = product.get(exponent, 0) + lc * rc
        result = p_clean(product)
    return result


def p_key(value: dict[tuple[int, ...], int]) -> tuple[tuple[tuple[int, ...], int], ...]:
    value = p_clean(value)
    divisor = reduce(gcd, (abs(c) for c in value.values()), 0)
    terms = [(m, c // divisor) for m, c in value.items()]
    if dict(terms)[max(m for m, _ in terms)] < 0:
        terms = [(m, -c) for m, c in terms]
    return tuple(sorted(terms))


def p_det(matrix: tuple[tuple[dict[tuple[int, ...], int], ...], ...]) -> dict[tuple[int, ...], int]:
    total: dict[tuple[int, ...], int] = {}
    for permutation in permutations(range(len(matrix))):
        inversions = sum(permutation[i] > permutation[j]
                         for i in range(len(matrix)) for j in range(i + 1, len(matrix)))
        term = p_mul(*(matrix[row][permutation[row]] for row in range(len(matrix))))
        total = p_add(total, term if inversions % 2 == 0 else p_neg(term))
    return total


def verify_projection_gap(prover: dict[str, Any], candidate: dict[str, Any]) -> None:
    gap = prover["first_uncovered_mode"]
    require(gap["residual_type"] == 36, "first projection type")
    require(gap["elimination_polynomial_up_to_sign"] == "p = c*d - c + f", "first projection polynomial")
    variables = [p_var(i) for i in range(NVAR)]
    a, _, c, d, _, f, _, _, _ = variables
    q36 = p_add(p_mul(a, f), p_neg(p_mul(c, d)), c, p_neg(f))
    restricted = {m: coefficient for m, coefficient in q36.items() if m[0] == 0}
    target = p_add(p_mul(c, d), p_neg(c), f)
    require(p_key(restricted) == p_key(target), "type-36 facet restriction")

    one, zero = p_const(1), p_const(0)
    matrix = (
        (one, zero, zero, zero, one, one, one, one),
        (zero, one, zero, zero, one, variables[0], variables[3], variables[6]),
        (zero, zero, one, zero, one, variables[1], variables[4], variables[7]),
        (zero, zero, zero, one, one, variables[2], variables[5], variables[8]),
    )
    brackets = {}
    for basis in combinations(range(8), 4):
        brackets["".join(str(i + 1) for i in basis)] = p_det(tuple(
            tuple(matrix[row][column] for column in basis) for row in range(4)
        ))
    require(len(brackets) == 70 and brackets["1346"] == a, "70 parent bracket reconstruction")
    require(p_key(target) not in {p_key(value) for value in brackets.values()}, "projection factor is a parent bracket")

    with np.load(BytesIO(frozen_bytes("ai/omreal/data/DIAG9_GRAPH_global_factor_census.npz")), allow_pickle=False) as source:
        offsets = np.asarray(source["factor_offset"], dtype=np.int64)
        exponents = np.asarray(source["factor_exponent"], dtype=np.int64)
        coefficients = np.asarray(source["factor_coefficient"], dtype=np.int64)
    require(offsets.shape == (26741,) and offsets[0] == 0 and offsets[-1] == len(exponents),
            "26740-factor census shape")
    target_key = p_key(target)
    keys = set()
    for index in range(26740):
        polynomial = {tuple(map(int, exponents[j])): int(coefficients[j])
                      for j in range(offsets[index], offsets[index + 1])}
        keys.add(p_key(polynomial))
    require(len(keys) == 26740 and target_key not in keys, "projection factor already in residual census")
    require(candidate["exact_counts"]["first_layer_new_irreducibles"] == 142, "first-layer count scope")
    audit = frozen_text("ai/omreal/DIAG9_SIGN_GEODESY_AUDIT.md")
    require("142 distinct new irreducibles" in audit and all(
        f"| {degree} | {count} |" in audit for degree, count in ((2, 23), (3, 71), (4, 43), (5, 5))
    ), "pinned first-layer audit statement")


def components(graph: dict[str, Any], sign_filter: str | None) -> int:
    signs = {row["id"]: row["active_sign"] for row in graph["vertices"]}
    vertices = set(signs) if sign_filter is None else {v for v, sign in signs.items() if sign == sign_filter}
    adjacency = {v: set() for v in vertices}
    for edge in graph["edges"]:
        left, right = edge["ends"]
        if left in vertices and right in vertices:
            adjacency[left].add(right)
            adjacency[right].add(left)
    count = 0
    unseen = set(vertices)
    while unseen:
        count += 1
        queue = deque([unseen.pop()])
        while queue:
            node = queue.popleft()
            for neighbor in adjacency[node] & unseen:
                unseen.remove(neighbor)
                queue.append(neighbor)
    return count


def local_observation(graph: dict[str, Any]) -> dict[str, Any]:
    signs = {row["id"]: row["active_sign"] for row in graph["vertices"]}
    vertex = Counter()
    edge = Counter()
    incident = {v: Counter() for v in signs}
    for record in graph["edges"]:
        left, right = record["ends"]
        kind = record["kind"]
        incident[left][kind] += 1
        incident[right][kind] += 1
        edge[("".join(sorted((signs[left], signs[right]))), kind, record["transport"])] += 1
    for node, counts in incident.items():
        vertex[(signs[node], tuple(sorted(counts.items())))] += 1
    return {"vertex": vertex, "edge": edge, "multiwalls": graph["multiwall_incidences"]}


def verify_circuit_frontier(frontier: dict[str, Any]) -> None:
    require(tuple(frontier["residual_partition"]["ordinary"] + frontier["residual_partition"]["localization"])
            != EXPECTED_TYPES, "partition ordering unexpectedly canonical")
    require(set(frontier["residual_partition"]["ordinary"] + frontier["residual_partition"]["localization"])
            == set(EXPECTED_TYPES), "13-type partition")
    opposite = next(row for row in frontier["surviving_productions"]
                    if row["name"] == "OPPOSITE_PARTNER_ELIMINATION_INTERVAL")
    counts = {int(k): int(v) for k, v in opposite["certified_auxiliary_counts"].items()}
    require(set(counts) == set(EXPECTED_TYPES) and sum(counts.values()) == 123, "auxiliary row census")
    require(sum(v * (v - 1) // 2 for v in counts.values()) == 671, "opposite-pair census")
    ordinary = set(frontier["residual_partition"]["ordinary"])
    supports = sum((v * (v - 1) // 2) * (4 if kind in ordinary else 3)
                   for kind, v in counts.items())
    require(supports == 2420, "persistent-support census")
    note = frozen_text("ai/omreal/BLOCK_GORDAN_RESIDUAL_ELIMINATION_CELLS.md")
    rows = re.findall(r"^\|\s*(\d+)\s*\|\s*(ordinary|localization)\s*\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*([\d,]+)\s*\|$", note, re.M)
    require(len(rows) == 13 and sum(int(row[2]) for row in rows) == 123, "displayed per-type sum")
    require("| **total** |  | **131** | **671** | **2,420** |" in note, "preserved 131 typo")

    pair = frontier["local_memory_counterpair"]
    cut = pair["cut_configuration"]
    noncut = pair["noncut_configuration"]
    require(len(cut["vertices"]) == len(noncut["vertices"]) == 16, "counterpair chamber count")
    require(local_observation(cut) == local_observation(noncut), "counterpair local observations differ")
    require((components(cut, "+"), components(noncut, "+")) == (2, 1), "positive cut behavior")
    require(components(cut, None) == components(noncut, None) == 1, "full graph connectedness")
    require(pair["scope"] == "ABSTRACT_SIGNED_CHAMBER_GRAPH_NOT_UOM_4_8_REALIZATION",
            "counterpair promoted to source D9")
    require(frontier["scope"]["local_type_only_completeness"] == "DISPROVED", "local no-go status")
    require(frontier["scope"]["actual_uom_4_8_universal_cut_grammar"] == "UNRESOLVED", "D9 scope")
    require(frontier["scope"]["obstruction_type_bound_10000"] == "NOT_PROVED", "type ceiling overclaim")
    require(frontier["scope"]["exact_instance_bound_250000"] == "NOT_PROVED", "instance ceiling overclaim")


def q_values(point: tuple[Fraction, ...]) -> tuple[Fraction, ...]:
    x, y, *z = point
    return (y, x * x - 1 - y, *z)


def noninclusion(i: int, j: int) -> tuple[Fraction, ...]:
    point = [Fraction(0), Fraction(0), *([Fraction(1)] * 7)]
    if i == 0:
        point[1] = 1
        if j >= 2:
            point[j] = -1
    elif i == 1:
        point[0] = 2
        if j >= 2:
            point[j] = -1
    elif j >= 2:
        point[j] = -1
    return tuple(point)


def verify_countermodels(result: dict[str, Any], prover_model: dict[str, Any]) -> None:
    model = result["minimal_exact_countermodel"]
    require(model["component_count"] == 2, "minimal model component count")
    left = tuple(Fraction(v) for v in (-2, 1, 1, 1, 1, 1, 1, 1, 1))
    right = tuple(Fraction(v) for v in (2, 1, 1, 1, 1, 1, 1, 1, 1))
    require(q_values(left) == q_values(right) and all(v > 0 for v in q_values(left)), "same-word feasible witnesses")
    witnesses = 0
    for i in range(9):
        for j in range(9):
            if i == j:
                continue
            values = q_values(noninclusion(i, j))
            require(values[i] > 0 and values[j] <= 0, f"ordered noninclusion {i}->{j}")
            witnesses += 1
    require(witnesses == model["local_certificates"]["ordered_noninclusion_witnesses_replayed"] == 72,
            "72 ordered noninclusions")
    require("not_an_actual_d9_counterexample" in model, "source-domain exclusion")
    gate = result["countermodel_rejection_hypotheses"]
    require(gate["exact_structural_discriminator"]["status_for_actual_d9"] == "UNPROVED",
            "unproved D9 global discriminator promoted")
    require(result["endpoint"] == ENDPOINT and result["ledger_change_recommended"] == "none; remain 2/9",
            "falsifier endpoint or ledger")
    require(prover_model["component_count"] == 3, "canonical quartic model component count")
    roots = (-2, -1, 1, 2)
    quartic = lambda x: (x * x - 1) * (x * x - 4)
    require(all(quartic(Fraction(x)) == 0 for x in roots), "canonical quartic roots")
    require([quartic(Fraction(x)) > 0 for x in (-3, 0, 3)] == [True, True, True], "three quartic sectors")


def verify_boundary(counterexample: dict[str, Any]) -> None:
    require(counterexample["active_factor"]["factor_id"] == 8552, "boundary factor ID")
    require(counterexample["active_factor"]["polynomial"] == "d*i-e", "boundary polynomial")
    require(counterexample["active_factor"]["family_allowed_side"] == "d*i-e<0", "boundary orientation")
    signs = []
    for ray in counterexample["exact_rays"]:
        point = tuple(Fraction(value) for value in ray["exact_lift_point"])
        q = point[3] * point[8] - point[4]
        require(q == Fraction(ray["exact_factor_value"]), f"factor-8552 lift {ray['side']}")
        require(point[5] == 0 and ray["lift_parent_zero_profile"] == ["1237"], "lift left divisor 1237")
        require(ray["strictly_positive_parent_brackets"] == 69, "strict parent bracket count")
        signs.append((q > 0) - (q < 0))
    require(signs == [-1, 0, 1], "boundary lift signs")
    atlas = frozen_json("ai/omreal/data/DIAG3_PAIR_GLOBAL_row2599_compactification_atlas.json")
    require(atlas["chart_atlas"]["chart_count"] == 64, "64-chart compactification")
    divisor = [row for row in atlas["boundary_divisors"] if row["parent_bracket"] == "1237"]
    require(divisor == [counterexample["boundary_incidence"]["compactification_divisor"]], "genuine 1237 divisor")
    obstruction = counterexample["singular_transport_obstruction"]
    require(obstruction["positive_parent_initial_form"] == "+n4" and
            obstruction["negative_parent_initial_form"] == "-n4" and
            obstruction["ordinary_common_radial_strict_parent_link"] == "EMPTY", "opposite-parent no-go")
    gate = counterexample["strict_parent_separator_gate"]
    require(gate["witness_contained_in_boundary"] is True, "boundary residence")
    require(gate["witness_separates_strict_parent"] is False, "strict-parent separator overclaim")
    require(gate["recursive_facet_wall_promoted_to_global_separator"] is False, "global separator overclaim")
    require(obstruction["strict_open_parent_lift_certified"] is False, "missing strict coface hidden")


def verify_portability(adapter: dict[str, Any]) -> None:
    history = adapter["historical_referee"]
    require(history == {
        "recorded_identifier": HISTORICAL,
        "recorded_tree": "56fe7f95a4e20dea581736cb5539abb502e05a63",
        "availability_at_opening": "ABSENT",
        "object_existence_claim": "NONE",
        "dereference_policy": "FORBIDDEN_AND_NOT_REQUIRED",
    }, "historical-object portability policy")
    missing = subprocess.run(["git", "cat-file", "-e", f"{HISTORICAL}^{{commit}}"], cwd=ROOT,
                             env={"GIT_NO_LAZY_FETCH": "1"}, capture_output=True)
    require(missing.returncode != 0, "historical object unexpectedly available at review")
    replay = adapter["source_derived_replay"]
    require(replay["acceptance_logic"] == "PINNED_INDEPENDENT_REFEREE_KERNEL_ONLY", "portable trust boundary")
    require(replay["mutable_wrapper"] == "NOT_INVOKED", "mutable predecessor wrapper used")
    require((replay["active_factor_classes"], replay["all_occurrences"], replay["aligned_occurrences"],
             replay["parent_inequalities"], replay["hostile_mutations_rejected"]) == (3539, 6167, 5026, 70, 16),
            "portable predecessor census")
    script = frozen_text(f"{CERTIFICATE}/verify_portable_predecessor.py")
    require("commit in REQUIRED_GIT_OBJECTS" in script and "HISTORICAL_REFEREE not in REQUIRED_GIT_OBJECTS" in script,
            "portable dereference allow-list missing")
    require(HISTORICAL not in adapter["source_derived_replay"]["entrypoints"], "historical object registered as entrypoint")


def validate_candidate(candidate: dict[str, Any], evidence: dict[str, dict[str, Any]]) -> None:
    require(candidate["format"] == "9dvl-d9-universal-cut-closing-candidate-v1", "candidate format")
    require(candidate["cycle_id"] == "2026-09-01-d9-universal-cut", "cycle ID")
    require(candidate["opening_base"] == {"commit": MATH_BASE, "tree": MATH_BASE_TREE}, "opening base")
    require(candidate["evidence_integration"] == {"commit": FROZEN_PARENT, "tree": FROZEN_PARENT_TREE},
            "evidence integration binding")
    require(candidate["opening_gate"] == "FAILED_CLOSED", "opening gate promotion")
    require(candidate["mathematical_endpoint"] == ENDPOINT, "endpoint")
    require(candidate["classification"] == "EXACT_NULL_GLOBAL_COVERAGE_AND_ATTACHMENT_NO_GO", "classification")
    require(candidate["theorem"] == {
        "id": "9DVL", "opening_score": "2/9", "closing_score": "2/9", "promotion": "NONE",
    }, "theorem ledger")
    require(candidate["main_census"] == {"authorized": False, "started": False}, "main census denial")
    require(set(candidate["failure_reasons"]) == EXPECTED_FAILURES, "failure reason census")
    require(set(candidate["nonconsequences"]) == EXPECTED_NONCONSEQUENCES, "nonconsequence census")
    require(candidate["route_disposition"] == "RETIRED_UNTIL_GLOBAL_ATTACHMENT_AND_PROJECTION_CLOSURE_INPUTS",
            "route disposition")
    require(candidate["selected_successor"] is None and candidate["next_state"] == "PIVOT_REQUIRED", "successor scope")
    require(candidate["exact_counts"] == {
        "local_wall_types": 13,
        "opposite_partner_pairs": 671,
        "persistent_support_candidates": 2420,
        "abstract_counterpair_chambers": 16,
        "first_layer_new_irreducibles": 142,
        "parent_brackets_checked": 70,
        "global_residual_factors_checked": 26740,
        "boundary_charts_checked": 64,
        "certificate_hostile_mutations_rejected": 32,
        "falsifier_ordered_noninclusions": 72,
    }, "exact count vector")

    prover = evidence["prover"]
    require(prover["global_stratified_coverage"] == {
        "status": "MISSING",
        "required_theorem": prover["global_stratified_coverage"]["required_theorem"],
        "repository_state": prover["global_stratified_coverage"]["repository_state"],
        "certificate": None,
    }, "global coverage was promoted")
    matrix = prover["coverage_matrix"]
    require(matrix["source_reconstructible_global_cut_coverage"] == "FAILED", "opening requirement 1")
    require(matrix["recursive_facets"] == "MISSING_PROJECTION_CLOSURE_AND_COMPLETE_ATTACHMENTS", "opening requirement 2")
    require(matrix["genuine_infinity"] == "MISSING_COMPLETE_TAGGED_COMPACTIFICATION", "opening requirement 2 infinity")
    require(matrix["abstract_countermodel_formal_domain_rejection"] == "PASS", "opening requirement 3 domain")
    require(matrix["abstract_countermodel_cut_mechanism_exclusion"] == "FAILED", "opening requirement 3 mechanism")

    verify_projection_gap(prover, candidate)
    verify_circuit_frontier(evidence["circuits"])
    verify_countermodels(evidence["falsifier"], evidence["prover_model"])
    verify_boundary(evidence["boundary"])
    verify_portability(evidence["portable"])
    certificate = evidence["certificate_result"]
    require(certificate["mathematical_endpoint"] is None, "schema fixture promoted to endpoint")
    require(certificate["coverage"]["excluded"] == "NO_LIVE_UNIVERSAL_COVERAGE_ADAPTER_OR_MATHEMATICAL_D9_ENDPOINT",
            "live adapter invented")
    require(certificate["canaries"]["hostile"] == "PASS_32_OF_32_REJECTED", "certificate hostile replay")


def evidence_snapshot() -> dict[str, dict[str, Any]]:
    return {
        "prover": frozen_json(f"{PROVER}/CUT_REDUCTION_SCHEMA.json"),
        "prover_model": frozen_json(f"{PROVER}/ABSTRACT_DISCONNECTED_COUNTERMODEL.json"),
        "circuits": frozen_json(f"{CIRCUITS}/FINITE_GRAMMAR_FRONTIER.json"),
        "boundary": frozen_json(f"{BOUNDARY}/BOUNDARY_TRANSPORT_COUNTEREXAMPLE.json"),
        "falsifier": frozen_json(f"{FALSIFIER}/RESULT.json"),
        "portable": frozen_json(f"{CERTIFICATE}/PORTABLE_PREDECESSOR_ADAPTER.json"),
        "certificate_result": frozen_json(f"{CERTIFICATE}/RESULT.json"),
    }


def hostile_mutations(candidate: dict[str, Any], evidence: dict[str, dict[str, Any]]) -> int:
    mutations = (
        ("opening-pass", lambda c, e: c.__setitem__("opening_gate", "PASSED")),
        ("wrong-endpoint", lambda c, e: c.__setitem__("mathematical_endpoint", "DIAGONAL_9_PROVED")),
        ("promotion", lambda c, e: c["theorem"].__setitem__("promotion", "PROVED")),
        ("ledger", lambda c, e: c["theorem"].__setitem__("closing_score", "3/9")),
        ("census-authorized", lambda c, e: c["main_census"].__setitem__("authorized", True)),
        ("census-started", lambda c, e: c["main_census"].__setitem__("started", True)),
        ("erase-failure", lambda c, e: c["failure_reasons"].pop()),
        ("erase-nonconsequence", lambda c, e: c["nonconsequences"].pop()),
        ("successor-selected", lambda c, e: c.__setitem__("selected_successor", "TYPE36_CLOSURE")),
        ("type-count", lambda c, e: c["exact_counts"].__setitem__("local_wall_types", 12)),
        ("resultant-count", lambda c, e: c["exact_counts"].__setitem__("first_layer_new_irreducibles", 141)),
        ("global-coverage", lambda c, e: e["prover"]["global_stratified_coverage"].__setitem__("status", "PROVED")),
        ("projection-closed", lambda c, e: e["prover"]["first_uncovered_mode"].__setitem__("residual_type", 37)),
        ("counterpair-realized", lambda c, e: e["circuits"]["local_memory_counterpair"].__setitem__("scope", "ACTUAL_UOM_4_8")),
        ("type-bound", lambda c, e: e["circuits"]["scope"].__setitem__("obstruction_type_bound_10000", "PROVED")),
        ("factor8552-crosses", lambda c, e: e["boundary"]["strict_parent_separator_gate"].__setitem__("witness_separates_strict_parent", True)),
        ("strict-coface", lambda c, e: e["boundary"]["singular_transport_obstruction"].__setitem__("strict_open_parent_lift_certified", True)),
        ("D9-discriminator", lambda c, e: e["falsifier"]["countermodel_rejection_hypotheses"]["exact_structural_discriminator"].__setitem__("status_for_actual_d9", "PROVED")),
        ("historical-required", lambda c, e: e["portable"]["historical_referee"].__setitem__("dereference_policy", "REQUIRED")),
        ("live-adapter", lambda c, e: e["certificate_result"]["coverage"].__setitem__("excluded", "LIVE_UNIVERSAL_ADAPTER")),
    )
    rejected = 0
    for name, mutation in mutations:
        hostile_candidate = deepcopy(candidate)
        hostile_evidence = deepcopy(evidence)
        mutation(hostile_candidate, hostile_evidence)
        try:
            validate_candidate(hostile_candidate, hostile_evidence)
        except Reject:
            rejected += 1
        else:
            raise Reject(f"hostile mutation accepted: {name}")
    require(rejected == len(mutations), "hostile rejection count")
    return rejected


def verify_own_artifacts() -> None:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    result = json.loads(RESULT.read_text(encoding="utf-8"))
    require(manifest["format"] == "d9-universal-cut-referee-closing-manifest-v1", "closing manifest format")
    require(manifest["frozen_commit"] == FROZEN and manifest["frozen_tree"] == FROZEN_TREE, "closing frozen binding")
    require(manifest["verdict"] == "ACCEPT" and manifest["endpoint"] == ENDPOINT, "closing verdict")
    require(manifest["ledger"] == {"before": "2/9", "after": "2/9", "delta": 0}, "closing ledger")
    require(manifest["semantic_sha256"] == semantic(b"d9-universal-cut-referee-closing-manifest-v1", manifest),
            "closing manifest semantic digest")
    for relative, expected in manifest["referee_artifact_sha256"].items():
        require(sha256_path(ROOT / relative) == expected, f"referee artifact digest: {relative}")
    require(result["format"] == "d9-universal-cut-closing-referee-result-v1", "result format")
    require(result["reviewed_commit"] == FROZEN and result["reviewed_tree"] == FROZEN_TREE, "result frozen binding")
    require(result["verdict"] == "ACCEPT" and result["endpoint"] == ENDPOINT, "result verdict")
    require(result["ledger"] == {"before": "2/9", "after": "2/9", "delta": 0, "change_recommended": "none"},
            "result ledger")
    require(result["closing_manifest_semantic_sha256"] == manifest["semantic_sha256"], "result/manifest binding")
    require(result["semantic_sha256"] == semantic(b"d9-universal-cut-closing-referee-result-v1", result),
            "result semantic digest")


def full_source_replay() -> None:
    commands = (
        ([sys.executable, "ai/omreal/verify_diag9_sign_geodesy_audit.py", "--workers", "7"],
         ("first pivot-boundary resultant layer has 142 new irreducibles",
          "degree census = 2:23, 3:71, 4:43, 5:5",
          "proves neither sign-geodesy")),
        ([sys.executable, f"{CERTIFICATE}/verify_portable_predecessor.py"],
         ("ca730426 is recorded as absent and never dereferenced",
          "3539 classes / 6167 occurrences / 5026 aligned / 70 parent inequalities / 16 hostile rejections",
          "NORMAL_LINK_REDUCTION_NO_GO")),
    )
    for command, tokens in commands:
        completed = subprocess.run(command, cwd=ROOT, env={"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0", "PATH": "/usr/local/bin:/usr/bin:/bin"},
                                   capture_output=True, text=True, check=False)
        require(completed.returncode == 0, f"source replay failed: {' '.join(command)}\n{completed.stdout}\n{completed.stderr}")
        require(all(token in completed.stdout for token in tokens), f"source replay output drift: {' '.join(command)}")
        print("PASS full source replay", " ".join(command))


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--full-source-replay", action="store_true")
    parser.add_argument("--candidate-only", action="store_true")
    arguments = parser.parse_args()
    verify_revision_and_authority()
    candidate = frozen_json(CANDIDATE)
    total_pins, unique_pins = verify_all_source_pins(candidate)
    evidence = evidence_snapshot()
    validate_candidate(candidate, evidence)
    rejected = hostile_mutations(candidate, evidence)
    if not arguments.candidate_only:
        verify_own_artifacts()
    if arguments.full_source_replay:
        full_source_replay()
    print(f"PASS frozen candidate {FROZEN} tree {FROZEN_TREE}")
    print(f"PASS source pins {total_pins} declarations / {unique_pins} unique paths")
    print("PASS five opening requirements adjudicated: FAIL, FAIL, FAIL, PASS, PASS")
    print("PASS type-36 projection gap, 16-chamber scope, factor-8552 boundary residence")
    print("PASS 123-vs-131 discrepancy: displayed rows sum to 123; 671 and 2420 unchanged")
    print("PASS portable predecessor: unavailable historical object is not required")
    print(f"PASS independent hostile mutations {rejected}/{rejected}")
    print(f"ACCEPT {ENDPOINT}; main census denied; ledger 2/9; next state PIVOT_REQUIRED")


if __name__ == "__main__":
    main()
