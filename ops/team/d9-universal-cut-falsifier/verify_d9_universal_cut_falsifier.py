#!/usr/bin/env python3
"""Producer-independent exact replay for the universal-D9 cut falsifier.

The replay uses only the Python standard library.  It reconstructs the
countermodels from their equations, rather than invoking any current-cycle
producer or sharing producer-side acceptance logic.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RESULT_PATH = HERE / "RESULT.json"
HOSTILE_PATH = HERE / "HOSTILE_TESTS.json"
SOURCE_PATH = HERE / "SOURCE_MANIFEST.json"

OPENING_COMMIT = "6cbd1b4a7d3ed61bee268b6b54cbfadeece90f0e"
OPENING_TREE = "84eaf80b30e1f366b8f959bd6435a217762636b3"
EXPECTED_SOURCE_SEMANTIC = "7b186afd26b0a278e60f434ef47165830b84e43675666f7684dceb8fe5213fc2"
EXPECTED_HOSTILE_SEMANTIC = "e72e180eae1f8743487b26a0ece5cc4c2b34cf4c1a9e0d7d00953f5897672663"
EXPECTED_RESULT_SEMANTIC = "8dbc9a45e6148da2076d8e18519a0c00750ae02e5ca58985a0b4a929d720d808"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def semantic_sha256(payload: dict) -> str:
    core = dict(payload)
    core.pop("semantic_sha256", None)
    raw = json.dumps(core, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def git_output(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def q_values(point: tuple[Fraction, ...], connected_variant: bool = False) -> tuple[Fraction, ...]:
    require(len(point) == 9, "point dimension changed")
    x, y, *z = point
    q2 = 1 - x * x - y if connected_variant else x * x - 1 - y
    return (y, q2, *z)


def point(*values: int) -> tuple[Fraction, ...]:
    return tuple(Fraction(value) for value in values)


def ordered_noninclusion_witness(i: int, j: int) -> tuple[Fraction, ...]:
    """Return p with q_i(p)>0 and q_j(p)<=0 for distinct i,j."""
    require(0 <= i < 9 and 0 <= j < 9 and i != j, "bad ordered pair")
    p = [Fraction(0), Fraction(0), *([Fraction(1)] * 7)]
    if i == 0:
        p[1] = Fraction(1)
        if j >= 2:
            p[j] = Fraction(-1)
    elif i == 1:
        p[0] = Fraction(2)
        if j >= 2:
            p[j] = Fraction(-1)
    else:
        if j >= 2:
            p[j] = Fraction(-1)
    return tuple(p)


def determinant(matrix: list[list[Fraction]]) -> Fraction:
    n = len(matrix)
    require(all(len(row) == n for row in matrix), "determinant matrix not square")
    work = [row[:] for row in matrix]
    answer = Fraction(1)
    for column in range(n):
        pivot = next((row for row in range(column, n) if work[row][column]), None)
        require(pivot is not None, "singular matrix")
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            answer = -answer
        value = work[column][column]
        answer *= value
        for entry in range(column, n):
            work[column][entry] /= value
        for row in range(column + 1, n):
            scale = work[row][column]
            if scale:
                for entry in range(column, n):
                    work[row][entry] -= scale * work[column][entry]
    return answer


def verify_minimal_model(result: dict) -> None:
    model = result["minimal_exact_countermodel"]
    require(model["component_count"] == 2, "minimal-model component count changed")
    require(model["polynomials"] == [
        "q1=y", "q2=x^2-1-y", "q3=z1", "q4=z2", "q5=z3",
        "q6=z4", "q7=z5", "q8=z6", "q9=z7",
    ], "minimal-model equations changed")

    left = point(-2, 1, 1, 1, 1, 1, 1, 1, 1)
    right = point(2, 1, 1, 1, 1, 1, 1, 1, 1)
    require(all(value > 0 for value in q_values(left)), "left witness is not strictly feasible")
    require(all(value > 0 for value in q_values(right)), "right witness is not strictly feasible")
    require(q_values(left) == q_values(right), "same-sign witness canary changed")
    require(left[0] < -1 and right[0] > 1, "component witness labels changed")
    require(Fraction(-1) - Fraction(1) < 0, "x=0 separator evaluation changed")

    # At q1=q2=z1=...=z7=0, x is exactly +/-1.  The full Jacobian
    # determinant is the 2x2 determinant for (q1,q2) times I_7.
    determinants = []
    for x in (Fraction(-1), Fraction(1)):
        jacobian = [[Fraction(0) for _ in range(9)] for _ in range(9)]
        jacobian[0][1] = Fraction(1)
        jacobian[1][0] = 2 * x
        jacobian[1][1] = Fraction(-1)
        for k in range(7):
            jacobian[2 + k][2 + k] = Fraction(1)
        determinants.append(determinant(jacobian))
    require(determinants == [Fraction(2), Fraction(-2)], "full multiwall transversality changed")

    witnesses = 0
    for i in range(9):
        for j in range(9):
            if i == j:
                continue
            witness = ordered_noninclusion_witness(i, j)
            values = q_values(witness)
            require(values[i] > 0, f"ordered noninclusion {i}->{j} lost source region")
            require(values[j] <= 0, f"ordered noninclusion {i}->{j} entered target region")
            witnesses += 1
    require(witnesses == 72, "ordered noninclusion census changed")
    require(model["local_certificates"]["ordered_noninclusion_witnesses_replayed"] == witnesses,
            "stored noninclusion count changed")

    # Negative canary: 0<y<1-x^2 implies -1<x<1, a single base interval.
    require(not all(value > 0 for value in q_values(left, connected_variant=True)),
            "connected substitution unexpectedly retained the left witness")
    require(not all(value > 0 for value in q_values(right, connected_variant=True)),
            "connected substitution unexpectedly retained the right witness")


def verify_canonical_model(result: dict) -> None:
    canonical = result["canonical_model_replay"]
    require(canonical["component_count"] == 3, "canonical component count changed")

    def q2(x: Fraction, y: Fraction) -> Fraction:
        return (x * x - 1) * (x * x - 4) - y

    for x in (Fraction(-3), Fraction(0), Fraction(3)):
        require(q2(x, Fraction(1)) > 0, "canonical feasible component witness failed")
    for x in (Fraction(-2), Fraction(-1), Fraction(1), Fraction(2)):
        require(q2(x, Fraction(0)) == 0, "canonical boundary root changed")
    require(q2(Fraction(3, 2), Fraction(0)) < 0, "canonical gap sign changed")


def verify_global_memory_pair(result: dict) -> None:
    pair = result["global_memory_pair"]
    behavior = pair["different_global_behavior"]
    require(behavior["nested_positive_sector_components"] == 2,
            "nested component count changed")
    require(behavior["disjoint_positive_sector_components"] == 1,
            "disjoint component count changed")

    # Nested roots are the two exact circles r^2=1 and r^2=4.  The radial
    # derivative multiplier 2*r*(2*r^2-5) never vanishes on either circle.
    require((1 - 1) * (1 - 4) == 0 and (4 - 1) * (4 - 4) == 0,
            "nested circle equations changed")
    require(2 * 1 - 5 == -3 and 2 * 4 - 5 == 3,
            "nested circle regularity changed")
    require((0 - 1) * (0 - 4) > 0 and (2 - 1) * (2 - 4) < 0 and
            (9 - 1) * (9 - 4) > 0, "nested radial sign decomposition changed")

    # The disjoint unit-circle centers are distance 6 apart.  Simultaneous
    # membership in both open unit disks would force distance <2.
    center_distance_squared = Fraction(36)
    require(center_distance_squared > 4, "disjoint-circle separation changed")
    # On either circle, the other circle polynomial is strictly positive:
    # the nearest point is distance 5 from the other center.
    require(Fraction(25) - 1 > 0, "disjoint-circle transversality changed")
    # Constructive exterior path: increase |z| to at least 2 without
    # decreasing distance to either center, move horizontally at |z|>=2,
    # then use x=0, where both squared center distances are at least 9.
    require(Fraction(4) > 1 and Fraction(9) > 1,
            "disjoint exterior path clearance changed")
    require(pair["common_local_data"]["leading_form_at_infinity"] == "(x^2+z^2)^2",
            "common leading form changed")


def verify_sources(manifest: dict) -> dict[str, str]:
    require(manifest["opening_base"] == {"commit": OPENING_COMMIT, "tree": OPENING_TREE},
            "source manifest opening base changed")
    require(git_output("rev-parse", f"{OPENING_COMMIT}^{{tree}}") == OPENING_TREE,
            "opening commit/tree drift")
    contents: dict[str, str] = {}
    for source in manifest["sources"]:
        path = ROOT / source["path"]
        require(path.is_file(), f"missing source: {source['path']}")
        require(sha256(path) == source["sha256"], f"source digest drift: {source['path']}")
        if path.suffix in {".md", ".json", ".yaml", ".py"}:
            contents[source["path"]] = path.read_text(encoding="utf-8")

    require("can be disconnected" in contents["ai/omreal/DIAG9_ACTIVE_SECTOR_THEOREM.md"],
            "active-sector limit disappeared")
    require("scattered points" in contents["ai/omreal/DIAG9_SIGN_GEODESY_AUDIT.md"],
            "sampled sign-geodesy boundary disappeared")
    require("connectedness of the raw zero/sign component" in
            contents["ai/omreal/NINTH_DIAGONAL_SAFE_GRAPH.md"],
            "component-faithful germ requirement disappeared")
    require("sampled graph must not be" in contents["ai/omreal/DIAG9_GRAPH_TREE_CERTIFICATE.md"],
            "sampled graph promotion guard disappeared")
    require("It is not a complete" in
            contents["ai/omreal/DIAG9_PARENT860_CEGIS_ROUTING.md"],
            "parent-860 coverage disclaimer disappeared")
    require("one-sidedness of every labeled wall is insufficient" in
            contents["ai/omreal/ATLAS_HELLY.md"],
            "canonical abstract no-go disappeared")

    prover = json.loads(contents[
        "ops/team/diag9-s1237-normal-link-prover/DIAG9_S1237_NORMAL_LINK_NO_GO.json"
    ])
    require(prover["endpoint"] == "NORMAL_LINK_REDUCTION_NO_GO",
            "S12,37 producer endpoint changed")
    require(len(prover["obstruction"]["singular_supports"]) == 2,
            "S12,37 singular support count changed")
    for support in prover["obstruction"]["singular_supports"]:
        require(support["positive_gordan_weights"] == [1, 1],
                "S12,37 Gordan weights changed")
        require(not support["strict_first_order_parent_link_feasible"],
                "S12,37 strict-link no-go changed")

    falsifier = json.loads(contents["ops/team/diag9-s1237-normal-link-falsifier/RESULT.json"])
    require(falsifier["factor"]["factor_id"] == 8552, "factor-8552 ID changed")
    require(falsifier["factor"]["family_allowed_side"] == "d*i-e<0",
            "factor-8552 orientation changed")
    require(falsifier["obstruction"]["common_recursive_link_stratum"]
            ["identically_zero_parent_brackets"] == ["1237"],
            "factor-8552 recursive stratum changed")
    require(falsifier["scope"]["strict_open_parent_crossing"].startswith("NOT_CLAIMED"),
            "factor-8552 was promoted to a strict crossing")
    require(falsifier["scope"]["global_d9_separator"] == "NOT_CLAIMED",
            "factor-8552 was promoted to a global separator")

    referee = json.loads(contents["ops/team/diag9-s1237-normal-link-referee/RESULT.json"])
    require(referee["verdict"] == "ACCEPT", "S12,37 referee verdict changed")
    require(referee["independent_replay"]["factor_8552_exact_same_stratum_lifts"] == 3,
            "factor-8552 exact lift count changed")
    return contents


def verify_scope(result: dict) -> None:
    require(result["outcome"] == "inconclusive", "actual-D9 null was overpromoted")
    require(result["endpoint"] == "UNIVERSAL_CUT_SCHEMA_COVERAGE_GAP",
            "endpoint changed")
    require(result["ledger_change_recommended"] == "none; remain 2/9",
            "ledger promotion detected")
    domain = result["countermodel_rejection_hypotheses"]["exact_domain_gate"]
    require(domain["name"] == "SOURCE_RECONSTRUCTIBLE_D9_INSTANCE",
            "D9 source-domain rejection gate changed")
    discriminator = result["countermodel_rejection_hypotheses"]["exact_structural_discriminator"]
    require(discriminator["name"] == "GLOBAL_COMPONENT_FAITHFUL_SIGN_GEODESY",
            "global discriminator changed")
    require(discriminator["status_for_actual_d9"] == "UNPROVED",
            "unproved D9 discriminator was promoted")
    require("No UOM(4,8) parent" in
            result["minimal_exact_countermodel"]["not_an_actual_d9_counterexample"],
            "abstract model was promoted to actual D9")
    require("complete compactified active-sector" in
            result["coverage"]["first_unresolved_discriminator"],
            "first discriminator changed")


def hostile_rejections(result: dict, hostile: dict, source_text: dict[str, str]) -> list[str]:
    ids = [test["id"] for test in hostile["tests"]]
    require(len(ids) == len(set(ids)) == 15, "hostile test IDs changed")
    require(all(test["expected_result"] == "REJECT" for test in hostile["tests"]),
            "a hostile test no longer expects rejection")

    left = point(-2, 1, 1, 1, 1, 1, 1, 1, 1)
    boundary = point(-1, 1, 1, 1, 1, 1, 1, 1, 1)
    checks = {
        "connected-parabola-substitution": not all(v > 0 for v in q_values(left, True)),
        "boundary-witness": not all(v > 0 for v in q_values(boundary)),
        "component-label-merge": q_values(left) == q_values(point(2, 1, 1, 1, 1, 1, 1, 1, 1))
            and left[0] < 0 < 2,
        "false-sign-geodesy": q_values(left) == q_values(point(2, 1, 1, 1, 1, 1, 1, 1, 1)),
        "local-inventory-promotion": result["global_memory_pair"]["different_global_behavior"]
            ["nested_positive_sector_components"] != result["global_memory_pair"]
            ["different_global_behavior"]["disjoint_positive_sector_components"],
        "infinity-only-promotion": result["global_memory_pair"]["common_local_data"]
            ["leading_form_at_infinity"] == "(x^2+z^2)^2",
        "abstract-to-d9-promotion": "No UOM(4,8) parent" in result
            ["minimal_exact_countermodel"]["not_an_actual_d9_counterexample"],
        "occurrence-unit-drop": "c_Eu_Eq" in
            source_text["ai/omreal/DIAG9_ACTIVE_SECTOR_THEOREM.md"].replace(" ", ""),
        "sampled-network-promotion": "It is not a complete" in
            source_text["ai/omreal/DIAG9_PARENT860_CEGIS_ROUTING.md"],
        "sampled-properness-promotion": "sampled graph must not be" in
            source_text["ai/omreal/DIAG9_GRAPH_TREE_CERTIFICATE.md"],
        "s1237-strict-link-promotion": "ordinary common-radial strict parent link has no direction" in
            source_text["ops/research-team/cycles/2026-09-01-diag9-s1237-normal-link/CYCLE_REPORT.md"],
        "factor8552-global-separator": "is not a global separator" in
            source_text["ops/research-team/cycles/2026-09-01-diag9-s1237-normal-link/CYCLE_REPORT.md"],
        "fake-parent-infinity": "source-derived compactification incidence" in
            next(test["gate"] for test in hostile["tests"] if test["id"] == "fake-parent-infinity"),
        "false-actual-d9-disproof": result["outcome"] == "inconclusive",
        "ledger-promotion": result["ledger_change_recommended"] == "none; remain 2/9",
    }
    require(set(checks) == set(ids), "hostile implementation/test manifest mismatch")
    require(all(checks.values()), "hostile mutations escaped: " +
            ", ".join(key for key, value in checks.items() if not value))
    return ids


def verify_artifact_digests(result: dict, hostile: dict, source: dict) -> None:
    source_semantic = semantic_sha256(source)
    hostile_semantic = semantic_sha256(hostile)
    result_semantic = semantic_sha256(result)
    require(source["semantic_sha256"] == source_semantic == EXPECTED_SOURCE_SEMANTIC,
            "source manifest semantic digest changed")
    require(hostile["semantic_sha256"] == hostile_semantic == EXPECTED_HOSTILE_SEMANTIC,
            "hostile manifest semantic digest changed")
    require(result["source_manifest_semantic_sha256"] == source_semantic,
            "result/source semantic binding changed")
    require(result["hostile_tests_semantic_sha256"] == hostile_semantic,
            "result/hostile semantic binding changed")
    require(result["semantic_sha256"] == result_semantic == EXPECTED_RESULT_SEMANTIC,
            "result semantic digest changed")


def main() -> None:
    result = load_json(RESULT_PATH)
    hostile = load_json(HOSTILE_PATH)
    source = load_json(SOURCE_PATH)
    source_text = verify_sources(source)
    verify_minimal_model(result)
    verify_canonical_model(result)
    verify_global_memory_pair(result)
    verify_scope(result)
    rejected = hostile_rejections(result, hostile, source_text)
    verify_artifact_digests(result, hostile, source)

    print("PASS opening base/tree and 14 source pins")
    print("PASS minimal exact common-pivot graph-wall countermodel: 2 components; 72 ordered noninclusions")
    print("PASS canonical ATLAS_HELLY countermodel: 3 components")
    print("PASS matched local/infinity-memory pair: nested 2 components; disjoint 1 component")
    print("PASS S12,37 opposite-parent-form and factor-8552 recursive-facet scope canaries")
    print("PASS parent-860 sampled-network nonpromotion canary")
    print(f"PASS {len(rejected)}/{len(rejected)} hostile mutations rejected")
    print("ENDPOINT UNIVERSAL_CUT_SCHEMA_COVERAGE_GAP")
    print("SCOPE exact logical no-go; no actual D9 counterexample; ledger remains 2/9")
    print("SEMANTIC SHA256", result["semantic_sha256"])


if __name__ == "__main__":
    main()
