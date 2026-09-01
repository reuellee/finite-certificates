#!/usr/bin/env python3
"""Producer-independent certificate for the factor-19069 null frontier."""

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
REVIEWED = "2f0c7026aace6cf6f10f79fd8b1e1dfdccb577ac"
REVIEWED_TREE = "f75c0ce659f0662d2a5865f399e5c3589729d182"
FRONTIER_PATH = "ops/team/d9-factor19069-active-margin-constructor/ACTIVE_MARGIN_FRONTIER.json"
CONSTRUCTOR_RESULT_PATH = "ops/team/d9-factor19069-active-margin-constructor/RESULT.json"
FALSIFIER_RESULT_PATH = "ops/team/d9-factor19069-active-margin-falsifier/RESULT.json"
PINS = {
    FRONTIER_PATH: "0875dd345a307bf9c4e33287cc13df1e6944c902d8a84c419a35cf9ddccbd243",
    CONSTRUCTOR_RESULT_PATH: "b6b9a8329abde76d9a5755f33df41f59209c7fa6f7a91133edbd3c0607ccbe5f",
    FALSIFIER_RESULT_PATH: "bf14ffa83fa95c05d64ad36ca5c8008f0b38dd00fd61a911ad38cd93da4deb0f",
    "ops/team/d9-factor19069-active-margin-falsifier/verify_active_margin_falsifier.py": "152d15747813910a4e88328722511bcee9ba02973e1676724ad29c3bc69ed76f",
}
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


def frozen(path: str) -> bytes:
    return git("show", f"{REVIEWED}:{path}", binary=True)


def semantic_digest(candidate: dict) -> str:
    unsealed = deepcopy(candidate)
    unsealed.pop("semantic_sha256", None)
    return sha256(
        json.dumps(unsealed, sort_keys=True, separators=(",", ":")).encode("ascii")
    ).hexdigest()


def inventory_digest(parent_inventory: list[dict]) -> str:
    return sha256(
        json.dumps(
            {"parents": parent_inventory},
            sort_keys=True,
            separators=(",", ":"),
        ).encode("ascii")
    ).hexdigest()


def degree(polynomial) -> int:
    return max(map(sum, polynomial))


def primitive_univariate(coefficients):
    result = list(map(Fraction, coefficients))
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return tuple(result)


def root_count(coefficients) -> int:
    polynomial = primitive_univariate(coefficients)
    require(sturm.polynomial_value(polynomial, Fraction(0)) != 0, "edge endpoint root")
    require(sturm.polynomial_value(polynomial, Fraction(1)) != 0, "edge endpoint root")
    return sturm.root_count(polynomial, Fraction(0), Fraction(1))


def boundary_state(polynomial, multidegree, face) -> str:
    signs = set()
    for monomial, coefficient in polynomial.items():
        support = bernstein.term_support(monomial, multidegree)
        if all(item & ~allowed == 0 for item, allowed in zip(support, face, strict=True)):
            signs.add(1 if coefficient > 0 else -1)
    if not signs:
        return "IDENTICALLY_ZERO"
    if signs == {1, -1}:
        return "BERNSTEIN_MIXED_UNRESOLVED"
    if signs == {1}:
        return "BERNSTEIN_POSITIVE"
    if signs == {-1}:
        return "BERNSTEIN_NEGATIVE"
    raise Reject("boundary state")


def replay_sources() -> dict:
    records = [
        json.loads(line)
        for line in gate.CATALOG.read_text(encoding="utf-8").splitlines()
        if line
    ]
    parents, parent_sign_digest = gate.parent_polynomials(records[2599])
    require(len(parents) == 70, "parent count")
    parent_inventory = [
        {
            "label": label,
            "target_sign": target,
            "affine_degree": degree(polynomial),
            "term_count": len(polynomial),
        }
        for label, target, polynomial, _terms in parents
    ]
    candidates = gate.parse_candidates()
    _occurrences, _occurrence_factor, factors = labeled.factor_polynomials()
    require(19069 in candidates, "factor candidate")
    factor = factors[19069]
    require(degree(factor) == 6 and len(factor) == 108, "factor structure")
    multidegree = tuple(
        max(sum(monomial[index] for index in group) for monomial in factor)
        for group in bernstein.GROUPS
    )
    require(multidegree == (2, 2, 2), "factor multidegree")

    _matrices, points, _packed, _states, _hamming, _multiplicity = transition.exact_inputs()
    cover = json.loads((DATA / "DIAG3_PAIR_FULLSUPPORT_SEGMENT_COVER.json").read_text(encoding="utf-8"))
    selected = tuple(cover["source_bank"]["selected_edge_indices"])
    require(len(selected) == 40, "skeleton edges")
    tag_state = sha256(b"d9-factor19069-all-parent-path-tags-v1\0")
    roots = {}
    checks = 0
    for edge_index in selected:
        left, right = safe.EDGES[edge_index]
        for label, target, polynomial, _terms in parents:
            restriction = safe.segment_power(polynomial, points[left], points[right])
            require(
                safe.positive_unit([target * coefficient for coefficient in restriction]),
                f"parent path tag {edge_index}:{label}",
            )
            tag_state.update(edge_index.to_bytes(2, "little"))
            tag_state.update(label.encode("ascii"))
            checks += 1
        roots[str(edge_index)] = root_count(
            safe.segment_power(factor, points[left], points[right])
        )
    require(checks == 2800, "path tag checks")
    require([int(edge) for edge, count in roots.items() if count] == [39], "rooted edges")
    require(roots["39"] == 1, "edge39 root")

    parent_face = json.loads((DATA / "DIAG3_PAIR_GLOBAL_row2599_parent_face_gate.json").read_text(encoding="utf-8"))
    boundary_records = []
    for record in parent_face["nonexcluded_support_faces"]:
        face = tuple(record["support"])
        boundary_records.append(
            {
                "support": list(face),
                "dimension": record["dimension"],
                "parent_bernstein_classification": record["classification"].upper(),
                "weak_sign_witness_zero_parent_brackets": record["witness_zero_parent_brackets"],
                "factor19069_restriction": boundary_state(factor, multidegree, face),
                "path_tag_to_pinned_parent_component_closure": "ABSENT",
            }
        )
    proper = [record for record in boundary_records if record["dimension"] < 9]
    require(len(proper) == 10, "proper support count")
    require(sum(record["factor19069_restriction"] == "IDENTICALLY_ZERO" for record in proper) == 8, "zero support count")
    require(sum(record["factor19069_restriction"] == "BERNSTEIN_MIXED_UNRESOLVED" for record in proper) == 2, "mixed support count")

    active_by_size = {str(size): comb(70, size) for size in range(1, 10)}
    running = 0
    cumulative = {}
    for size in range(1, 10):
        running += active_by_size[str(size)]
        cumulative[str(size)] = running
    require(cumulative["3"] == 57225 and cumulative["4"] == 974120, "active ceiling")
    require(cumulative["9"] == 75816847319, "active total")
    return {
        "parent_sign_digest": parent_sign_digest,
        "parent_inventory": parent_inventory,
        "parent_inventory_digest": inventory_digest(parent_inventory),
        "path_tag_digest": tag_state.hexdigest(),
        "roots": roots,
        "boundary_records": boundary_records,
        "active_by_size": active_by_size,
        "cumulative": cumulative,
    }


def validate(candidate: dict, replay: dict) -> None:
    require(candidate["format"] == "d9-factor19069-active-margin-frontier-v1", "format")
    require(candidate["semantic_sha256"] == semantic_digest(candidate), "semantic digest")
    require(candidate["classification"] == "EXACT_FAIL_CLOSED_PARENT_RESIDENCE_NULL", "classification")
    require(candidate["endpoint"].endswith("FIRST_UNCLASSIFIED_STRATUM"), "endpoint")
    target = candidate["target"]
    require(target["factor_id"] == 19069, "factor")
    require(target["parent_sign_tags"] == 70, "parent count")
    require(target["parent_sign_digest"] == replay["parent_sign_digest"], "parent sign digest")
    require(target["parent_inventory"] == replay["parent_inventory"], "parent inventory")
    require(target["parent_inventory_semantic_sha256"] == replay["parent_inventory_digest"], "parent inventory digest")
    source = candidate["exact_source_replay"]
    require(source["parent_path_tag_checks"] == 2800, "path tag checks")
    require(source["parent_path_tag_semantic_sha256"] == replay["path_tag_digest"], "path tag digest")
    require(source["factor19069_open_root_counts_by_skeleton_edge"] == replay["roots"], "root census")
    require(source["factor19069_rooted_skeleton_edges"] == [39], "rooted edge")
    require(source["global_component_inference_from_collar"] is False, "collar scope")
    active = candidate["active_margin_frontier"]
    require(active["candidate_active_sets_by_support_size"] == replay["active_by_size"], "active sizes")
    require(active["cumulative_candidate_active_sets"] == replay["cumulative"], "active cumulative")
    require(active["opening_exact_system_ceiling"] == 100000, "system ceiling")
    require(active["first_support_size_exceeding_ceiling"] == 4, "ceiling crossing")
    require(active["complete_source_derived_active_tie_incidence_filter"] == "ABSENT", "tie filter")
    require(active["critical_systems_solved"] == 0, "systems solved")
    require(active["component_samples_constructed"] == 0, "samples")
    boundary = candidate["true_boundary_frontier"]
    require(boundary["records"] == replay["boundary_records"], "boundary records")
    require(boundary["proper_nonexcluded_support_strata"] == 10, "proper supports")
    require(boundary["complete_parent_component_closure_path_tags"] is False, "boundary paths")
    require(boundary["first_unclassified_stratum"]["support"] == [1, 1, 1], "first stratum")
    components = candidate["component_classification"]
    require(components["complete_wall_component_count"] is None, "component count")
    require(components["attached_global_components"] is None, "attachment")
    require(components["unattached_global_components"] is None, "nonattachment")
    require(candidate["next_action"].startswith("D9_ROW2599_FACTOR19069_FACTORED_BARRIER_COMPONENT_SAMPLER_GATE1"), "successor")
    require(candidate["theorem_ledger"] == "2/9", "ledger")


def reseal(candidate: dict) -> dict:
    candidate["semantic_sha256"] = semantic_digest(candidate)
    return candidate


def hostile_mutations(stored: dict, replay: dict) -> list[str]:
    mutations = []
    altered = deepcopy(stored); altered["classification"] = "COMPLETE"; mutations.append((reseal(altered), "classification"))
    altered = deepcopy(stored); altered["target"]["factor_id"] = 19068; mutations.append((reseal(altered), "factor"))
    altered = deepcopy(stored); altered["target"]["parent_sign_tags"] = 69; mutations.append((reseal(altered), "parent count"))
    altered = deepcopy(stored); altered["target"]["parent_inventory"].pop(); mutations.append((reseal(altered), "parent inventory"))
    altered = deepcopy(stored); altered["exact_source_replay"]["parent_path_tag_checks"] = 2730; mutations.append((reseal(altered), "path tag checks"))
    altered = deepcopy(stored); altered["exact_source_replay"]["factor19069_rooted_skeleton_edges"] = []; mutations.append((reseal(altered), "rooted edge"))
    altered = deepcopy(stored); altered["exact_source_replay"]["global_component_inference_from_collar"] = True; mutations.append((reseal(altered), "collar scope"))
    altered = deepcopy(stored); altered["active_margin_frontier"]["cumulative_candidate_active_sets"]["9"] = 9; mutations.append((reseal(altered), "active cumulative"))
    altered = deepcopy(stored); altered["active_margin_frontier"]["first_support_size_exceeding_ceiling"] = 9; mutations.append((reseal(altered), "ceiling crossing"))
    altered = deepcopy(stored); altered["active_margin_frontier"]["complete_source_derived_active_tie_incidence_filter"] = "COMPLETE"; mutations.append((reseal(altered), "tie filter"))
    altered = deepcopy(stored); altered["active_margin_frontier"]["component_samples_constructed"] = 1; mutations.append((reseal(altered), "samples"))
    altered = deepcopy(stored); altered["true_boundary_frontier"]["records"].pop(); mutations.append((reseal(altered), "boundary records"))
    altered = deepcopy(stored); altered["true_boundary_frontier"]["complete_parent_component_closure_path_tags"] = True; mutations.append((reseal(altered), "boundary paths"))
    altered = deepcopy(stored); altered["component_classification"]["complete_wall_component_count"] = 1; mutations.append((reseal(altered), "component count"))
    altered = deepcopy(stored); altered["component_classification"]["attached_global_components"] = 1; mutations.append((reseal(altered), "attachment"))
    altered = deepcopy(stored); altered["next_action"] = "SAMPLE_ANOTHER_SEPARATOR"; mutations.append((reseal(altered), "successor"))
    altered = deepcopy(stored); altered["theorem_ledger"] = "3/9"; mutations.append((reseal(altered), "ledger"))
    rejected = []
    for candidate, marker in mutations:
        try:
            validate(candidate, replay)
        except Reject as error:
            require(marker in str(error), f"wrong hostile rejection {marker}: {error}")
            rejected.append(marker)
            continue
        raise Reject(f"hostile mutation accepted: {marker}")
    return rejected


def main() -> None:
    require(git("rev-parse", f"{REVIEWED}^{{tree}}") == REVIEWED_TREE, "reviewed tree")
    for path, expected in PINS.items():
        data = frozen(path)
        require(digest(data) == expected, f"frozen pin {path}")
        require((ROOT / path).read_bytes() == data, f"worktree drift {path}")
    frontier = json.loads(frozen(FRONTIER_PATH).decode("utf-8"))
    constructor = json.loads(frozen(CONSTRUCTOR_RESULT_PATH).decode("utf-8"))
    falsifier = json.loads(frozen(FALSIFIER_RESULT_PATH).decode("utf-8"))
    replay = replay_sources()
    validate(frontier, replay)
    require(constructor["frontier_sha256"] == PINS[FRONTIER_PATH], "constructor cross-pin")
    require(constructor["classification"] == frontier["classification"], "constructor classification")
    require(falsifier["classification"] == "EXACT_SCOPE_REJECTION_CONFIRMS_NULL", "falsifier classification")
    require(falsifier["accepted_endpoint"] == frontier["endpoint"], "falsifier endpoint")
    require(falsifier["hostile_mutations"] == {"rejected": 12, "total": 12}, "falsifier mutations")
    rejected = hostile_mutations(frontier, replay)
    print("PASS producer-independent factor-19069 active-margin null certificate")
    print("PASS exact 70x40 parent tags, skeleton roots, active census, and boundary frontier")
    print(f"PASS hostile_mutations={len(rejected)} re-sealed semantic mutations rejected")
    print("ACCEPT null endpoint; no component count, no D9 result, ledger=2/9")


if __name__ == "__main__":
    main()
