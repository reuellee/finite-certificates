#!/usr/bin/env python3
"""Build the exact clipped-wall route-refutation certificate.

This is discovery/prover-side code.  It deliberately depends only on pinned
repository inputs and exact ``Fraction`` arithmetic.  The key calculation is
an exact tensor-Bernstein positivity certificate for q16134 on macrobox 20,
which proves that the proposed clipped terminal cell contains no triple zero.
"""

from __future__ import annotations

from fractions import Fraction
import hashlib
from itertools import product
import json
from math import comb
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))

import verify_diag3_triple_local_roadmap_canary as exact  # noqa: E402
import diag3_research_ledger_compatibility as ledger_compat  # noqa: E402


OUTPUT = ROOT / "ops/team/clipped-wall-prover/DIAG3_CLIPPED_WALL_PROVER_CERTIFICATE.json"
LEDGER = HERE / "data/DIAG3_RESEARCH_DECISION_LEDGER.json"
LOCAL_CERTIFICATE = HERE / "data/DIAG3_TRIPLE_LOCAL_ROADMAP_CANARY.json"
FRONTIER_CERTIFICATE = ROOT / "ops/team/triple-frontier/DIAG3_TRIPLE_FRONTIER_MULTIBOX_CANARY.json"
FRONTIER_BUILDER = HERE / "diag3_triple_frontier_build_multibox.py"
FRONTIER_VERIFIER = HERE / "diag3_triple_frontier_verify_multibox.py"

BASE_REVISION = "ae8a3afc24abfea94acf4b22ea35c2ca18f3c577"
SCHEMA = "diag3-clipped-wall-prover-route-refutation-v1"
HISTORICAL_DIGESTS = {
    "decision_ledger": ledger_compat.HISTORICAL_LEDGER_SHA256,
    "local_roadmap_certificate": "0ee63d4049278c41b8fdd611aacdbe56b188dc1225bd1b9dc18dc37fb2746c27",
    "critical_system": "c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8",
    "frontier_certificate": "7e7ba6761ba544ab96dc36cd3f559317132b7264b94bc39059be813a8c3b5f70",
    "frontier_builder": "f395fbf1336a01a09524d7f172b75b64530057848af8805ac275bd2b3f4f7fcb",
    "frontier_verifier": "5801c26d872d8615b020751fbb0bb478a02306e25523bac7e0a0f2e7f1e126b8",
}
CURRENT_SUCCESSOR_DIGESTS = {
    "decision_ledger": ledger_compat.CURRENT_LEDGER_SHA256,
    "local_roadmap_certificate": "0ee63d4049278c41b8fdd611aacdbe56b188dc1225bd1b9dc18dc37fb2746c27",
    "critical_system": "c9244a47ded5736e7afe724a9914e75631a22b78653442e88c14f5c397919eb8",
    "frontier_certificate": "7e7ba6761ba544ab96dc36cd3f559317132b7264b94bc39059be813a8c3b5f70",
    # Filled with the exact compatibility successors; historical certificate
    # provenance above remains unchanged.
    "frontier_builder": "0ab04e80eccb0bbadfa9676e1dec9066d7b13f02f31358084d37e8ff737b24fd",
    "frontier_verifier": "08707f73d6f5dc1bb5167bd3fd4237467c31be7967b733024ee85a83f52824b7",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def encoded(value: Fraction) -> str:
    return exact.encoded(Fraction(value))


def semantic_digest(candidate: dict) -> str:
    payload = dict(candidate)
    payload.pop("semantic_sha256", None)
    return hashlib.sha256(
        json.dumps(payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def records_digest(domain: bytes, records) -> str:
    digest = hashlib.sha256(domain + b"\0")
    for record in records:
        digest.update(json.dumps(record, separators=(",", ":")).encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def rectangular_interval(polynomial, bounds):
    answer = (Fraction(0), Fraction(0))
    for monomial, coefficient in polynomial.items():
        term = (coefficient, coefficient)
        for (lower, upper), exponent in zip(bounds, monomial, strict=True):
            term = exact.product_interval(
                term, exact.power_interval(lower, upper, exponent)
            )
        answer = answer[0] + term[0], answer[1] + term[1]
    return answer


def affine_pullback_to_unit_cube(polynomial, bounds):
    """Substitute x_j = lower_j + (upper_j-lower_j) u_j exactly."""

    dimension = len(bounds)
    answer = {}
    for monomial, coefficient in polynomial.items():
        terms = {(0,) * dimension: Fraction(coefficient)}
        for variable, exponent in enumerate(monomial):
            lower, upper = bounds[variable]
            width = upper - lower
            next_terms = {}
            for powers, value in terms.items():
                for unit_power in range(exponent + 1):
                    new_powers = list(powers)
                    new_powers[variable] = unit_power
                    new_powers = tuple(new_powers)
                    next_terms[new_powers] = next_terms.get(
                        new_powers, Fraction(0)
                    ) + (
                        value
                        * comb(exponent, unit_power)
                        * lower ** (exponent - unit_power)
                        * width**unit_power
                    )
            terms = next_terms
        for powers, value in terms.items():
            answer[powers] = answer.get(powers, Fraction(0)) + value
    return {powers: value for powers, value in answer.items() if value}


def tensor_bernstein_controls(polynomial, dimension):
    """Return exact tensor-Bernstein controls at the coordinate multidegree."""

    multidegree = tuple(
        max((monomial[axis] for monomial in polynomial), default=0)
        for axis in range(dimension)
    )
    controls = []
    for beta in product(*(range(degree + 1) for degree in multidegree)):
        value = Fraction(0)
        for alpha, coefficient in polynomial.items():
            if not all(alpha[axis] <= beta[axis] for axis in range(dimension)):
                continue
            factor = Fraction(1)
            for axis in range(dimension):
                if alpha[axis]:
                    factor *= Fraction(
                        comb(beta[axis], alpha[axis]),
                        comb(multidegree[axis], alpha[axis]),
                    )
            value += coefficient * factor
        controls.append((beta, value))
    return multidegree, controls


def bernstein_record(domain: bytes, polynomial, bounds):
    pulled = affine_pullback_to_unit_cube(polynomial, bounds)
    multidegree, controls = tensor_bernstein_controls(pulled, len(bounds))
    minimum = min(controls, key=lambda row: (row[1], row[0]))
    maximum = max(controls, key=lambda row: (row[1], row[0]))
    digest = hashlib.sha256(domain + b"\0")
    for index, value in controls:
        digest.update(bytes(index))
        digest.update(encoded(value).encode("ascii"))
        digest.update(b"\n")
    return {
        "source_polynomial_terms": len(polynomial),
        "unit_cube_power_terms": len(pulled),
        "multidegree": list(multidegree),
        "control_count": len(controls),
        "strictly_positive_control_count": sum(value > 0 for _index, value in controls),
        "minimum_control": encoded(minimum[1]),
        "minimum_index": list(minimum[0]),
        "maximum_control": encoded(maximum[1]),
        "maximum_index": list(maximum[0]),
        "control_record_sha256": digest.hexdigest(),
    }


def restrict_to_wall_g_equals_a(polynomial):
    """Return polynomial in (t,b,c,d,e,f,h,i) after a=g=t."""

    answer = {}
    for monomial, coefficient in polynomial.items():
        restricted = (
            monomial[0] + monomial[6],
            monomial[1],
            monomial[2],
            monomial[3],
            monomial[4],
            monomial[5],
            monomial[7],
            monomial[8],
        )
        answer[restricted] = answer.get(restricted, Fraction(0)) + coefficient
    return {monomial: coefficient for monomial, coefficient in answer.items() if coefficient}


def macro_center(center0, radius, index):
    center = list(center0)
    center[0] -= 2 * radius * index
    return tuple(center)


def macro_bounds(center, radius):
    return tuple((value - radius, value + radius) for value in center)


def main():
    paths = {
        "decision_ledger": LEDGER,
        "local_roadmap_certificate": LOCAL_CERTIFICATE,
        "critical_system": exact.SYSTEM,
        "frontier_certificate": FRONTIER_CERTIFICATE,
        "frontier_builder": FRONTIER_BUILDER,
        "frontier_verifier": FRONTIER_VERIFIER,
    }
    ledger_compat.load_current_ledger(LEDGER)
    actual_digests = {name: sha256(path) for name, path in paths.items()}
    if actual_digests != CURRENT_SUCCESSOR_DIGESTS:
        raise AssertionError(f"pinned input digest changed: {actual_digests}")

    local = json.loads(LOCAL_CERTIFICATE.read_text(encoding="utf-8"))
    exact.verify_candidate(local)
    frontier = json.loads(FRONTIER_CERTIFICATE.read_text(encoding="utf-8"))
    source = json.loads(exact.SYSTEM.read_text(encoding="ascii"))
    registration = json.loads(exact.REGISTRATION.read_text(encoding="utf-8"))
    residuals = tuple(
        exact.decode_polynomial(record["terms"])
        for record in source["equations"][:3]
    )
    q5563, q16134, q19284 = residuals
    center0 = tuple(Fraction(value) for value in registration["fixed_box"]["center"])
    radius = Fraction(registration["fixed_box"]["radius"])
    parent_brackets = exact.parent_brackets()
    projection_minor = exact.jacobian_minor(residuals, (3, 4, 7))
    base_parent_signs = tuple(
        exact.interval_sign(exact.direct_interval(polynomial, center0, radius))
        for _label, polynomial in parent_brackets
    )

    # Positive canary: macrobox 19 really was accepted for parent signs and the
    # fixed minor (using the deterministic g bisection).
    center19 = macro_center(center0, radius, 19)
    parent19 = []
    for index, (label, polynomial) in enumerate(parent_brackets):
        interval = exact.direct_interval(polynomial, center19, radius)
        sign = exact.interval_sign(interval)
        if sign != base_parent_signs[index]:
            raise AssertionError(f"accepted macrobox 19 changed at [{label}]")
        parent19.append([label, encoded(interval[0]), encoded(interval[1]), sign])
    bounds19 = macro_bounds(center19, radius)
    minor19 = []
    for side in (0, 1):
        child = list(bounds19)
        lower, upper = child[6]
        middle = center19[6]
        child[6] = (lower, middle) if side == 0 else (middle, upper)
        interval = rectangular_interval(projection_minor, tuple(child))
        if exact.interval_sign(interval) != -1:
            raise AssertionError("macrobox 19 projection canary changed")
        minor19.append([side, encoded(interval[0]), encoded(interval[1]), -1])

    # Macrobox 20 is rejected as a full parent-interior box only because
    # [3468]=g-a crosses zero.  The other 69 brackets remain strict on the
    # entire macrobox and therefore also on K.
    center20 = macro_center(center0, radius, 20)
    bounds20 = macro_bounds(center20, radius)
    parent20 = []
    failures = []
    strict_margins = []
    for index, (label, polynomial) in enumerate(parent_brackets):
        interval = exact.direct_interval(polynomial, center20, radius)
        sign = exact.interval_sign(interval)
        record = [label, encoded(interval[0]), encoded(interval[1]), sign]
        parent20.append(record)
        if sign != base_parent_signs[index]:
            failures.append(record)
        else:
            margin = interval[0] if sign > 0 else -interval[1]
            strict_margins.append((margin, record))
    if failures != [["3468", "-11/448", "3/448", 0]]:
        raise AssertionError(f"macrobox 20 frontier changed: {failures}")
    if min(strict_margins)[1] != ["2467", "313/448", "327/448", 1]:
        raise AssertionError("closest strict parent bracket changed")

    # The fixed projection minor is negative on all of macrobox 20 after the
    # same one-bisection scheme; this is stronger than sign-definiteness on K.
    minor20 = []
    for side in (0, 1):
        child = list(bounds20)
        lower, upper = child[6]
        middle = center20[6]
        child[6] = (lower, middle) if side == 0 else (middle, upper)
        interval = rectangular_interval(projection_minor, tuple(child))
        sign = exact.interval_sign(interval)
        if sign != -1:
            raise AssertionError("macrobox 20 fixed projection is not sign-definite")
        minor20.append([side, encoded(interval[0]), encoded(interval[1]), sign])

    # Strong route refutation: q16134 is positive on the full rectangular
    # macrobox 20.  Bernstein convex-hull containment makes this an exact
    # emptiness certificate for V intersect K, not a numerical sample.
    full_box_q16134 = bernstein_record(
        b"diag3-clipped-wall-prover-q16134-full-macrobox20-v1",
        q16134,
        bounds20,
    )
    if (
        full_box_q16134["control_count"],
        full_box_q16134["strictly_positive_control_count"],
        full_box_q16134["minimum_control"],
    ) != (576, 576, "846151417395/420906795008"):
        raise AssertionError("full macrobox 20 Bernstein certificate changed")

    # The genuine [3468] wall face uses t=a=g.  Its t range is the
    # intersection of the a and g coordinate intervals.
    wall_bounds = (
        (max(bounds20[0][0], bounds20[6][0]), min(bounds20[0][1], bounds20[6][1])),
        bounds20[1],
        bounds20[2],
        bounds20[3],
        bounds20[4],
        bounds20[5],
        bounds20[7],
        bounds20[8],
    )
    if wall_bounds[0] != (Fraction(-895, 896), Fraction(-889, 896)):
        raise AssertionError("wall-face t range changed")
    wall_q16134 = restrict_to_wall_g_equals_a(q16134)
    wall_q19284 = restrict_to_wall_g_equals_a(q19284)
    wall_q16134_bernstein = bernstein_record(
        b"diag3-clipped-wall-prover-q16134-wall-v1", wall_q16134, wall_bounds
    )
    wall_q19284_bernstein = bernstein_record(
        b"diag3-clipped-wall-prover-q19284-wall-v1", wall_q19284, wall_bounds
    )
    if (
        wall_q16134_bernstein["control_count"],
        wall_q16134_bernstein["strictly_positive_control_count"],
        wall_q16134_bernstein["minimum_control"],
    ) != (288, 288, "879180358095/420906795008"):
        raise AssertionError("wall q16134 Bernstein certificate changed")
    if (
        wall_q19284_bernstein["control_count"],
        wall_q19284_bernstein["strictly_positive_control_count"],
        wall_q19284_bernstein["minimum_control"],
    ) != (384, 384, "2809875/14680064"):
        raise AssertionError("wall q19284 Bernstein certificate changed")

    # The frontier artifact's wall point is a genuine parent-wall witness, but
    # explicitly not a triple-zero witness.
    crossing = frontier["frontier"]["failed_parent_brackets"][0]
    false_wall_witness = tuple(
        Fraction(value) for value in crossing["exact_parent_wall_point"]
    )
    if false_wall_witness[6] - false_wall_witness[0]:
        raise AssertionError("frontier witness is not on [3468]=g-a=0")
    if not all(
        lower <= value <= upper
        for value, (lower, upper) in zip(false_wall_witness, bounds20, strict=True)
    ):
        raise AssertionError("frontier witness left macrobox 20")
    false_wall_values = [exact.evaluate(polynomial, false_wall_witness) for polynomial in residuals]
    if false_wall_values != [
        Fraction(-1, 56),
        Fraction(5_934_694_995, 2_202_927_104),
        Fraction(435_073, 702_464),
    ]:
        raise AssertionError("false wall witness residual values changed")

    # The empty suffix is a bounded diagnostic inside the declared k=0..20
    # scan, not an extension to macrobox 21.  It explains why projection signs
    # alone did not provide a path of zeros to the terminal cell.
    suffix_records = []
    first_positive = None
    for macro_index in range(21):
        center = macro_center(center0, radius, macro_index)
        record = bernstein_record(
            b"diag3-clipped-wall-prover-q16134-corridor-macrobox-v1",
            q16134,
            macro_bounds(center, radius),
        )
        positive = record["strictly_positive_control_count"] == record["control_count"]
        if positive and first_positive is None:
            first_positive = macro_index
        if macro_index >= 6:
            if not positive:
                raise AssertionError(f"empty suffix changed at macrobox {macro_index}")
            suffix_records.append(
                [
                    macro_index,
                    record["minimum_control"],
                    record["maximum_control"],
                    record["control_record_sha256"],
                ]
            )
    if first_positive != 6:
        raise AssertionError("first Bernstein-positive macrobox changed")

    pivot = {(1, 0, 0): Fraction(2)}
    sphere_interval = exact.direct_interval(
        pivot, (Fraction(0), Fraction(0), Fraction(0)), Fraction(1)
    )
    if sphere_interval != (Fraction(-2), Fraction(2)) or exact.interval_sign(sphere_interval):
        raise AssertionError("compact-sphere negative canary accepted")

    wall_feasible_point = (
        Fraction(-223, 224),
        center20[1], center20[2], center20[3], center20[4], center20[5],
        Fraction(-223, 224),
        center20[7], center20[8],
    )
    if not all(
        lower <= value <= upper
        for value, (lower, upper) in zip(wall_feasible_point, bounds20, strict=True)
    ) or wall_feasible_point[6] != wall_feasible_point[0]:
        raise AssertionError("wall-face feasibility point changed")

    candidate = {
        "schema": SCHEMA,
        "status": "DISPROVED_TRIPLE_ZERO_ATTACHMENT_EMPTY_CLIPPED_CELL",
        "track_id": "cycle-20260828-clipped-wall-prover",
        "base_revision": BASE_REVISION,
        "authenticated_target": {
            "named_factor_presentation": source["named_presentation"],
            "canonical_unresolved_row": source["canonical_row"],
            "macrobox_index": 20,
            "wall_label": "3468",
            "wall_polynomial": "g-a",
            "accepted_parent_side": "g-a<=0",
            "clipped_cell": "K=macrobox20 intersect {g-a<=0}",
        },
        # Reproduce the historical v1 artifact exactly.  The current v2
        # ledger and versioned successor tools were authenticated separately.
        "source_digests": HISTORICAL_DIGESTS,
        "quantified_decisions": {
            "fixed_projection": {
                "claim": (
                    "For every x in K, det d(q5563,q16134,q19284)/d(d,e,h)(x)<0."
                ),
                "outcome": True,
                "stronger_domain": "full macrobox20",
                "cover": "two closed rectangular children obtained by bisecting g at -1",
                "child_intervals": minor20,
            },
            "other_parent_brackets": {
                "claim": (
                    "For every x in K and every normalized parent bracket B other than "
                    "[3468], sign(B(x)) equals its accepted base-box sign and B(x)!=0."
                ),
                "outcome": True,
                "stronger_domain": "full macrobox20",
                "strict_bracket_count": 69,
                "closest_strict_record": min(strict_margins)[1],
                "interval_record_sha256": records_digest(
                    b"diag3-clipped-wall-prover-parent20-v1", parent20
                ),
            },
            "triple_zero_wall_attachment": {
                "claim": (
                    "There exists x in K with g-a=0 and q5563(x)=q16134(x)="
                    "q19284(x)=0, connected inside the declared roadmap cell to an "
                    "accepted-corridor triple-zero component."
                ),
                "outcome": False,
                "stronger_refutation": "V intersect K is empty because q16134>0 on full macrobox20",
                "full_macrobox_q16134_bernstein": full_box_q16134,
                "wall_face_q16134_bernstein": wall_q16134_bernstein,
                "wall_face_q19284_bernstein": wall_q19284_bernstein,
            },
        },
        "geometry": {
            "macrobox20_center": [encoded(value) for value in center20],
            "macrobox20_radius": encoded(radius),
            "macrobox20_bounds": [
                [encoded(lower), encoded(upper)] for lower, upper in bounds20
            ],
            "wall_face_parameter_order": ["t=a=g", "b", "c", "d", "e", "f", "h", "i"],
            "wall_face_bounds": [
                [encoded(lower), encoded(upper)] for lower, upper in wall_bounds
            ],
            "wall_face_feasible_point": [encoded(value) for value in wall_feasible_point],
            "macrobox19_shared_seam_with_K": "a=-881/896",
            "K_is_convex_and_nonempty": True,
            "triple_zero_set_on_K": "EMPTY",
        },
        "bounded_corridor_diagnostic": {
            "searched_macrobox_index_interval_inclusive": [0, 20],
            "first_full_box_with_all_q16134_controls_positive": 6,
            "certified_zero_free_suffix": [6, 20],
            "suffix_records": suffix_records,
            "interpretation": (
                "Projection-minor and parent-sign acceptance did not certify occupancy or "
                "component transport; the corridor is q16134-positive from macrobox 6 onward."
            ),
        },
        "canaries": {
            "accepted_macrobox19": {
                "parent_signs_retained": 70,
                "closest_parent_record": next(row for row in parent19 if row[0] == "3468"),
                "projection_g_bisection_intervals": minor19,
            },
            "rejected_full_macrobox20": {
                "failed_parent_records": failures,
                "same_sign_parent_brackets": 69,
            },
            "wall_face_feasibility": True,
            "false_wall_witness": {
                "point": [encoded(value) for value in false_wall_witness],
                "parent_wall_value": "0",
                "residual_values": [encoded(value) for value in false_wall_values],
                "correctly_rejected_as_triple_zero": True,
            },
            "compact_sphere_negative_projection_interval": [
                encoded(sphere_interval[0]), encoded(sphere_interval[1])
            ],
        },
        "scope_and_nonconsequences": {
            "mere_parent_wall_intersection_proved": True,
            "triple_zero_wall_attachment_proved": False,
            "global_noncompactness_proved": False,
            "complete_named_factor_orbits_closed": 0,
            "s8_transport_claimed": False,
            "unresolved_triple_orbits_before": 1_162_302,
            "unresolved_triple_orbits_after": 1_162_302,
            "score_before": "2/9",
            "score_after": "2/9",
            "macrobox21_or_other_triple_searched": False,
        },
        "next_discriminator": (
            "Return to macroboxes 0..5 and locate the first exact boundary face through "
            "which the registered-zero component exits; then continue with an occupancy-"
            "certified adaptive cell chain rather than projection-sign-only extension."
        ),
    }
    candidate["semantic_sha256"] = semantic_digest(candidate)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(candidate, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"WROTE {OUTPUT.relative_to(ROOT)}")
    print("PASS fixed projection negative on K via full-macrobox g bisection 2/2")
    print("PASS other parent brackets strict on K 69/69")
    print(
        "DISPROVED attachment: q16134 full-macrobox Bernstein controls",
        f"{full_box_q16134['strictly_positive_control_count']}/{full_box_q16134['control_count']}",
        f"min={full_box_q16134['minimum_control']}",
    )
    print("PASS exact zero-free suffix macroboxes 6..20")
    print("SCOPE wall intersection only; no wall attachment; no global noncompactness; score=2/9")
    print(f"SEMANTIC {candidate['semantic_sha256']}")


if __name__ == "__main__":
    main()
