#!/usr/bin/env python3
"""Independent falsifier for the factor-19069 active-margin endpoint."""

from __future__ import annotations

from copy import deepcopy
from fractions import Fraction
from hashlib import sha256
import json
from math import comb
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OMREAL = ROOT / "ai" / "omreal"
DATA = OMREAL / "data"
FRONTIER = ROOT / "ops" / "team" / "d9-factor19069-active-margin-constructor" / "ACTIVE_MARGIN_FRONTIER.json"
CONSTRUCTOR = "fe7eaa80f4949a5702d102afc55b53f9644e7e5b"
CONSTRUCTOR_TREE = "23a78cc3900bbbf0003f11de25f839b838809fda"
EXPECTED_FRONTIER_SHA256 = "0875dd345a307bf9c4e33287cc13df1e6944c902d8a84c419a35cf9ddccbd243"
sys.path.insert(0, str(OMREAL))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import DIAG9_GRAPH_verify_row2599_slice as sturm  # noqa: E402
import diag3_pair_parent_source_transition_core as transition  # noqa: E402
import verify_diag3_pair_fullsupport_safe_segment_walls as safe  # noqa: E402
import verify_diag3_pair_global_face_bernstein_atlas as bernstein  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


class Reject(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise Reject(message)


def git(*arguments: str, binary: bool = False):
    result = subprocess.check_output(
        ["git", *arguments], cwd=ROOT, text=not binary
    )
    return result if binary else result.strip()


def digest(data: bytes) -> str:
    return sha256(data).hexdigest()


def polynomial_degree(polynomial) -> int:
    return max(map(sum, polynomial))


def primitive_univariate(coefficients):
    result = list(map(Fraction, coefficients))
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return tuple(result)


def root_count(polynomial) -> int:
    polynomial = primitive_univariate(polynomial)
    require(sturm.polynomial_value(polynomial, Fraction(0)) != 0, "edge endpoint root")
    require(sturm.polynomial_value(polynomial, Fraction(1)) != 0, "edge endpoint root")
    return sturm.root_count(polynomial, Fraction(0), Fraction(1))


def face_state(polynomial, multidegree, face) -> str:
    signs = {
        1 if coefficient > 0 else -1
        for monomial, coefficient in polynomial.items()
        if all(
            support & ~allowed == 0
            for support, allowed in zip(
                bernstein.term_support(monomial, multidegree), face, strict=True
            )
        )
    }
    if not signs:
        return "IDENTICALLY_ZERO"
    if signs == {1, -1}:
        return "BERNSTEIN_MIXED_UNRESOLVED"
    if signs == {1}:
        return "BERNSTEIN_POSITIVE"
    if signs == {-1}:
        return "BERNSTEIN_NEGATIVE"
    raise Reject("face state")


def independently_recompute() -> dict:
    records = [
        json.loads(line)
        for line in gate.CATALOG.read_text(encoding="utf-8").splitlines()
        if line
    ]
    parents, parent_digest = gate.parent_polynomials(records[2599])
    require(len(parents) == 70, "parent tag count")
    candidates = gate.parse_candidates()
    _occurrences, _occurrence_factor, factors = labeled.factor_polynomials()
    require(19069 in candidates, "target candidate")
    factor = factors[19069]
    require(polynomial_degree(factor) == 6 and len(factor) == 108, "factor structure")
    multidegree = tuple(
        max(sum(monomial[index] for index in group) for monomial in factor)
        for group in bernstein.GROUPS
    )
    require(multidegree == (2, 2, 2), "factor multidegree")

    _matrices, points, _packed, _states, _hamming, _multiplicity = transition.exact_inputs()
    cover = json.loads((DATA / "DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json").read_text(encoding="utf-8"))
    selected = tuple(cover["source_bank"]["selected_edge_indices"])
    require(len(selected) == 40, "skeleton edge count")
    tag_checks = 0
    roots = {}
    for edge_index in selected:
        left, right = safe.EDGES[edge_index]
        for label, target, polynomial, _terms in parents:
            restricted = safe.segment_power(polynomial, points[left], points[right])
            require(
                safe.positive_unit([target * coefficient for coefficient in restricted]),
                f"parent tag {edge_index}:{label}",
            )
            tag_checks += 1
        roots[str(edge_index)] = root_count(
            safe.segment_power(factor, points[left], points[right])
        )
    require(tag_checks == 2800, "parent tag checks")
    require([int(edge) for edge, count in roots.items() if count] == [39], "rooted edge")
    require(roots["39"] == 1, "edge39 root count")

    manifest = json.loads((DATA / "DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json").read_text(encoding="utf-8"))
    proper_states = []
    for record in manifest["nonexcluded_support_faces"]:
        if record["dimension"] < 9:
            proper_states.append(face_state(factor, multidegree, tuple(record["support"])))
    require(proper_states.count("IDENTICALLY_ZERO") == 8, "zero boundary restrictions")
    require(proper_states.count("BERNSTEIN_MIXED_UNRESOLVED") == 2, "mixed boundary restrictions")
    require(len(proper_states) == 10, "proper boundary frontier")

    cumulative = 0
    active = {}
    for size in range(1, 10):
        cumulative += comb(70, size)
        active[str(size)] = cumulative
    require(active["3"] == 57225 and active["4"] == 974120, "ceiling frontier")
    require(active["9"] == 75816847319, "support-nine frontier")
    return {
        "parent_digest": parent_digest,
        "tag_checks": tag_checks,
        "roots": roots,
        "proper_states": proper_states,
        "active_cumulative": active,
    }


def validate(candidate: dict, replay: dict) -> None:
    require(candidate["format"] == "d9-factor19069-active-margin-frontier-v1", "format")
    require(candidate["classification"] == "EXACT_FAIL_CLOSED_PARENT_RESIDENCE_NULL", "classification")
    require(candidate["target"]["factor_id"] == 19069, "target factor")
    require(candidate["target"]["parent_sign_tags"] == 70, "parent tag count")
    require(candidate["target"]["parent_sign_digest"] == replay["parent_digest"], "parent digest")
    source = candidate["exact_source_replay"]
    require(source["parent_path_tag_checks"] == replay["tag_checks"], "parent tag checks")
    require(source["factor19069_open_root_counts_by_skeleton_edge"] == replay["roots"], "root census")
    require(source["factor19069_rooted_skeleton_edges"] == [39], "rooted edge")
    require(source["global_component_inference_from_collar"] is False, "collar scope")
    active = candidate["active_margin_frontier"]
    require(active["cumulative_candidate_active_sets"] == replay["active_cumulative"], "active frontier")
    require(active["opening_exact_system_ceiling"] == 100000, "system ceiling")
    require(active["first_support_size_exceeding_ceiling"] == 4, "ceiling crossing")
    require(active["complete_source_derived_active_tie_incidence_filter"] == "ABSENT", "tie filter")
    require(active["critical_systems_solved"] == 0, "critical systems")
    boundary = candidate["true_boundary_frontier"]
    require(boundary["proper_nonexcluded_support_strata"] == 10, "proper boundary frontier")
    require(boundary["factor19069_proper_support_state_counts"]["IDENTICALLY_ZERO"] == 8, "zero boundary restrictions")
    require(boundary["factor19069_proper_support_state_counts"]["BERNSTEIN_MIXED_UNRESOLVED"] == 2, "mixed boundary restrictions")
    require(boundary["complete_parent_component_closure_path_tags"] is False, "boundary path tags")
    require(boundary["first_unclassified_stratum"]["support"] == [1, 1, 1], "first boundary obligation")
    components = candidate["component_classification"]
    require(components["complete_wall_component_count"] is None, "component count")
    require(components["attached_global_components"] is None, "attachment count")
    require(candidate["theorem_ledger"] == "2/9", "ledger")


def hostile_mutations(stored: dict, replay: dict) -> list[str]:
    mutations = []
    candidate = deepcopy(stored); candidate["classification"] = "COMPLETE"; mutations.append((candidate, "classification"))
    candidate = deepcopy(stored); candidate["target"]["parent_sign_tags"] = 69; mutations.append((candidate, "parent tag count"))
    candidate = deepcopy(stored); candidate["exact_source_replay"]["factor19069_rooted_skeleton_edges"] = [27, 39]; mutations.append((candidate, "rooted edge"))
    candidate = deepcopy(stored); candidate["exact_source_replay"]["global_component_inference_from_collar"] = True; mutations.append((candidate, "collar scope"))
    candidate = deepcopy(stored); candidate["active_margin_frontier"]["cumulative_candidate_active_sets"]["9"] = 1; mutations.append((candidate, "active frontier"))
    candidate = deepcopy(stored); candidate["active_margin_frontier"]["first_support_size_exceeding_ceiling"] = 9; mutations.append((candidate, "ceiling crossing"))
    candidate = deepcopy(stored); candidate["active_margin_frontier"]["complete_source_derived_active_tie_incidence_filter"] = "COMPLETE"; mutations.append((candidate, "tie filter"))
    candidate = deepcopy(stored); candidate["active_margin_frontier"]["critical_systems_solved"] = 70; mutations.append((candidate, "critical systems"))
    candidate = deepcopy(stored); candidate["true_boundary_frontier"]["proper_nonexcluded_support_strata"] = 0; mutations.append((candidate, "proper boundary frontier"))
    candidate = deepcopy(stored); candidate["true_boundary_frontier"]["complete_parent_component_closure_path_tags"] = True; mutations.append((candidate, "boundary path tags"))
    candidate = deepcopy(stored); candidate["component_classification"]["complete_wall_component_count"] = 1; mutations.append((candidate, "component count"))
    candidate = deepcopy(stored); candidate["theorem_ledger"] = "3/9"; mutations.append((candidate, "ledger"))
    rejected = []
    for candidate, marker in mutations:
        try:
            validate(candidate, replay)
        except Reject as error:
            require(marker in str(error), f"wrong hostile rejection: {marker}: {error}")
            rejected.append(marker)
            continue
        raise Reject(f"hostile mutation accepted: {marker}")
    return rejected


def main() -> None:
    require(git("rev-parse", f"{CONSTRUCTOR}^{{tree}}") == CONSTRUCTOR_TREE, "constructor tree")
    frozen = git(
        "show",
        f"{CONSTRUCTOR}:ops/team/d9-factor19069-active-margin-constructor/ACTIVE_MARGIN_FRONTIER.json",
        binary=True,
    )
    require(digest(frozen) == EXPECTED_FRONTIER_SHA256, "frozen frontier pin")
    require(FRONTIER.read_bytes() == frozen, "frontier worktree drift")
    stored = json.loads(frozen.decode("utf-8"))
    replay = independently_recompute()
    validate(stored, replay)
    rejected = hostile_mutations(stored, replay)
    print("PASS independent factor-19069 skeleton and boundary replay")
    print("PASS null classification; collar cannot promote global component coverage")
    print(f"PASS hostile_mutations={len(rejected)} all rejected")
    print("SCOPE complete active-margin/parent-residence endpoint rejected; ledger=2/9")


if __name__ == "__main__":
    main()
