#!/usr/bin/env python3
"""Build the exact S12,37 oriented normal-link no-go certificate.

This producer stops at the first strict-parent interior link wall.  It does
not construct a collar, a cell complex, or a diagonal-nine separator.
"""

from __future__ import annotations

import argparse
import contextlib
from collections import Counter, defaultdict
from copy import deepcopy
from fractions import Fraction
from functools import reduce
import hashlib
from io import StringIO
import json
from math import comb, gcd
from pathlib import Path
import subprocess
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OM = ROOT / "ai" / "omreal"
DATA = OM / "data"
sys.path.insert(0, str(OM))

with contextlib.redirect_stdout(StringIO()):
    import verify_diag9_active_sector as active
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled
import verify_diag2_canonical_robust_edges as evaluator
import verify_diag3_pair_global_parent_face_gate as parent_gate


FORMAT = "diag9-s1237-oriented-normal-link-no-go-v1"
OPENING_COMMIT = "c6bd7a6afeda0888fc950710b941cac6f6c9bf95"
OPENING_TREE = "9c2dbe39a3ea0f36e9e9c8f845e6f72e98526421"
SUPPORTS = ((3, 1, 15), (3, 3, 7))
TANGENT_POINT = (Fraction(3, 4), Fraction(1, 4), Fraction(1, 2))

SOURCE_PATHS = (
    "ops/research-team/cycles/2026-09-01-diag9-s1237-normal-link/OPENING_AUDIT.json",
    "ai/omreal/verify_diag9_active_sector.py",
    "ai/omreal/DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY.py",
    "ai/omreal/verify_diag3_pair_global_parent_face_gate.py",
    "ai/omreal/DIAG9_GRAPH_global_factor_census.py",
    "ai/omreal/data/DIAG9_GRAPH_global_factor_census.npz",
    "ai/omreal/data/seeat_parent2599_upper178.npz",
    "ai/omreal/data/ninth_candidate_12_37_antichain.npz",
    "ai/omreal/certs_4_8.jsonl",
)


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def sign(value):
    require(value != 0, "unexpected zero sign")
    return 1 if value > 0 else -1


def fraction_text(value):
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def semantic_digest(domain, value):
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(domain + b"\0" + payload).hexdigest()


def git(*arguments):
    return subprocess.run(
        ["git", *arguments], cwd=ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()


def multiply(left, right):
    answer = Counter()
    for (left_radial, left_exp), left_coefficient in left.items():
        for (right_radial, right_exp), right_coefficient in right.items():
            exponent = tuple(
                a + b for a, b in zip(left_exp, right_exp, strict=True)
            )
            answer[(left_radial + right_radial, exponent)] += (
                left_coefficient * right_coefficient
            )
    return {key: value for key, value in answer.items() if value}


def coordinate_map(support):
    """Affine coordinates as tangent plus radial-normal coordinates.

    The last normal breaks the parent equality on the four-dimensional
    ambient support face, giving all six normal coordinates to the
    three-dimensional parent stratum.
    """

    if support == (3, 1, 15):
        # (a, r*n0, r*n1, r*n2, r*n3, r*n4, g, h, g+r*n5)
        return (
            (0, None), (None, 0), (None, 1),
            (None, 2), (None, 3), (None, 4),
            (1, None), (2, None), (1, 5),
        )
    if support == (3, 3, 7):
        # (a, r*n0, r*n1, g+r*n5, r*n2, r*n3, g, h, r*n4)
        return (
            (0, None), (None, 0), (None, 1),
            (1, 5), (None, 2), (None, 3),
            (1, None), (2, None), (None, 4),
        )
    raise ValueError(f"unknown support: {support}")


def expand_polynomial(polynomial, support):
    """Expand exactly in r with coefficient variables (a,g,h,n0,...,n5)."""

    mapping = coordinate_map(support)
    answer = Counter()
    for source_exponent, source_coefficient in polynomial.items():
        term = {(0, (0,) * 9): Fraction(source_coefficient)}
        for power, (tangent_variable, normal_variable) in zip(
            source_exponent, mapping, strict=True
        ):
            if not power:
                continue
            factor = {}
            for normal_power in range(power + 1):
                tangent_power = power - normal_power
                if normal_power and normal_variable is None:
                    continue
                if tangent_power and tangent_variable is None:
                    continue
                exponent = [0] * 9
                if tangent_variable is not None:
                    exponent[tangent_variable] = tangent_power
                if normal_variable is not None:
                    exponent[3 + normal_variable] = normal_power
                factor[(normal_power, tuple(exponent))] = Fraction(
                    comb(power, normal_power)
                )
            term = multiply(term, factor)
        answer.update(term)
    return {key: value for key, value in answer.items() if value}


def primitive_rows(polynomial, preserve_sign=True):
    """Primitive integral rows without erasing an oriented sign."""

    require(polynomial, "empty polynomial")
    denominator = 1
    for value in polynomial.values():
        denominator = denominator * value.denominator // gcd(
            denominator, value.denominator
        )
    integers = {
        exponent: int(value * denominator)
        for exponent, value in polynomial.items()
    }
    common = reduce(gcd, (abs(value) for value in integers.values()))
    rows = tuple(sorted((exponent, value // common) for exponent, value in integers.items()))
    if not preserve_sign and rows[-1][1] < 0:
        rows = tuple((exponent, -value) for exponent, value in rows)
    return rows


def json_rows(rows):
    return [
        {"exponent": list(exponent), "coefficient": int(coefficient)}
        for exponent, coefficient in rows
    ]


def initial_form(polynomial, support):
    expanded = expand_polynomial(polynomial, support)
    radial_order = min(radial for radial, _exponent in expanded)
    coefficient = {
        exponent: value
        for (radial, exponent), value in expanded.items()
        if radial == radial_order
    }
    return radial_order, primitive_rows(coefficient), expanded


def evaluate_tangent(rows):
    answer = Counter()
    for exponent, coefficient in rows:
        value = Fraction(coefficient)
        for coordinate, power in zip(TANGENT_POINT, exponent[:3], strict=True):
            value *= coordinate ** power
        answer[exponent[3:]] += value
    return primitive_rows(
        {exponent: value for exponent, value in answer.items() if value}
    )


def source_manifest():
    require(git("rev-parse", f"{OPENING_COMMIT}^{{commit}}") == OPENING_COMMIT, "opening commit missing")
    require(git("rev-parse", f"{OPENING_COMMIT}^{{tree}}") == OPENING_TREE, "opening tree drift")
    files = {relative: sha256(ROOT / relative) for relative in SOURCE_PATHS}
    return {
        "format": "diag9-s1237-normal-link-source-manifest-v1",
        "opening_commit": OPENING_COMMIT,
        "opening_tree": OPENING_TREE,
        "files": files,
    }


def reconstruct_active_literals():
    active.verify_pins()
    certificates = active.transported_certificates()
    with np.load(DATA / "DIAG9_GRAPH_global_factor_census.npz", allow_pickle=False) as source:
        fourset_array = np.asarray(source["occurrence_fourset"], dtype=np.uint8)
        occurrence_factor = np.asarray(source["occurrence_factor"], dtype=np.uint32)
        factor_multiplicity = np.asarray(source["factor_multiplicity"], dtype=np.uint32)
        unit_offsets = np.asarray(source["occurrence_unit_offset"], dtype=np.uint32)
        unit_indices = np.asarray(source["occurrence_unit_index"], dtype=np.uint8)
        parent_labels = np.asarray(source["parent_bracket_label"], dtype=np.uint8)
    foursets = tuple(tuple(map(int, row)) for row in fourset_array)
    with np.load(DATA / "seeat_parent2599_upper178.npz", allow_pickle=False) as source:
        charts = np.asarray(source["chart_matrix"], dtype=np.int64)
    rows = active.topes.derived_rows(charts[0])
    oriented, conflicting = active.oriented_occurrences(foursets, certificates, rows)
    empty_factors = {int(occurrence_factor[index]) for index in conflicting}
    require(len(empty_factors) == 8_916, "empty-factor census drift")

    representatives = np.full(len(factor_multiplicity), -1, dtype=np.int64)
    occurrences_by_factor = defaultdict(list)
    for occurrence_index, factor in enumerate(map(int, occurrence_factor)):
        occurrences_by_factor[factor].append(occurrence_index)
        if representatives[factor] < 0:
            representatives[factor] = occurrence_index
    require(bool(np.all(representatives >= 0)), "factor without representative")
    representative_raw_sign = np.asarray(
        [oriented[index][1] for index in representatives], dtype=np.int8
    )

    with np.load(DATA / "ninth_candidate_12_37_antichain.npz", allow_pickle=False) as source:
        signatures = tuple(map(int, source["signature"]))
    family_literals = {}
    signature_incidence = defaultdict(list)
    occurrence_signature_incidence = defaultdict(list)
    for signature_index, signature in enumerate(signatures):
        per_signature = {}
        for occurrence_index, ((certificate_data, raw_sign), factor) in enumerate(
            zip(oriented, map(int, occurrence_factor), strict=True)
        ):
            if factor in empty_factors:
                continue
            allowed_raw = active.aligned_literal(signature, certificate_data)
            if allowed_raw is None:
                continue
            allowed_representative = (
                allowed_raw * raw_sign * int(representative_raw_sign[factor])
            )
            previous = per_signature.setdefault(factor, allowed_representative)
            require(previous == allowed_representative, "signature orientation conflict")
            occurrence_signature_incidence[(factor, occurrence_index)].append(signature_index)
        for factor, orientation in per_signature.items():
            previous = family_literals.setdefault(factor, orientation)
            require(previous == orientation, "family orientation conflict")
            signature_incidence[factor].append(signature_index)
    require(len(family_literals) == 3_539, "active literal count drift")

    _occurrences, _occurrence_map, factor_polynomials = labeled.factor_polynomials()
    anchor_values = parent_gate.normalized_values(charts[0].tolist())
    primitive_anchor_sign = {
        factor: sign(evaluator.evaluate(factor_polynomials[factor], anchor_values))
        for factor in family_literals
    }

    catalog_records = [
        json.loads(line)
        for line in parent_gate.CATALOG.read_text().splitlines()
        if line
    ]
    parents, parent_sign_digest = parent_gate.parent_polynomials(
        catalog_records[parent_gate.PARENT]
    )
    parent_sign = {label: target for label, target, _polynomial, _terms in parents}
    parent_label_text = tuple(
        "".join(str(int(value) + 1) for value in row)
        for row in parent_labels
    )
    require(len(set(parent_label_text)) == 62, "unit label census drift")

    literal_rows = []
    for factor in sorted(family_literals):
        q_sign = primitive_anchor_sign[factor]
        allowed_representative = family_literals[factor]
        allowed_primitive = (
            allowed_representative
            * int(representative_raw_sign[factor])
            * q_sign
        )
        occurrence_rows = []
        for occurrence_index in occurrences_by_factor[factor]:
            start = int(unit_offsets[occurrence_index])
            stop = int(unit_offsets[occurrence_index + 1])
            indices = tuple(map(int, unit_indices[start:stop]))
            require(len(indices) <= 1, "occurrence has more than one stripped unit")
            unit_label = parent_label_text[indices[0]] if indices else None
            unit_sign = parent_sign[unit_label] if unit_label is not None else 1
            raw_sign = int(oriented[occurrence_index][1])
            raw_to_primitive = raw_sign * q_sign
            scalar_sign = raw_to_primitive * unit_sign
            require(scalar_sign in (-1, 1), "bad scalar sign")
            occurrence_rows.append({
                "occurrence_index": occurrence_index,
                "fourset": list(foursets[occurrence_index]),
                "raw_to_primitive_sign": raw_to_primitive,
                "unit_bracket_label": unit_label,
                "unit_sign_in_parent": unit_sign,
                "constant_scalar_sign": scalar_sign,
                "active_signature_indices": occurrence_signature_incidence[
                    (factor, occurrence_index)
                ],
            })
        representative = int(representatives[factor])
        literal_rows.append({
            "factor_id": factor,
            "allowed_representative_sign": allowed_representative,
            "representative_occurrence_index": representative,
            "representative_fourset": list(foursets[representative]),
            "representative_raw_sign_at_anchor": int(representative_raw_sign[factor]),
            "primitive_sign_at_anchor": q_sign,
            "allowed_primitive_sign": allowed_primitive,
            "active_signature_indices": signature_incidence[factor],
            "occurrences": occurrence_rows,
        })

    occurrence_count = sum(len(row["occurrences"]) for row in literal_rows)
    multiplicity = Counter(len(row["occurrences"]) for row in literal_rows)
    require(occurrence_count == 6_167, "active occurrence census drift")
    require(multiplicity == Counter({1: 3453, 2: 2, 15: 55, 65: 29}), "active multiplicity drift")
    core = {
        "family": "S12,37",
        "parent_index": 2_599,
        "signatures": list(signatures),
        "factor_count": len(literal_rows),
        "occurrence_count": occurrence_count,
        "multiplicity_census": {str(key): value for key, value in sorted(multiplicity.items())},
        "literal_rows": literal_rows,
    }
    inventory = {
        "format": "diag9-s1237-oriented-active-literal-inventory-v1",
        **core,
        "semantic_sha256": semantic_digest(b"diag9-s1237-oriented-active-literals-v1", core),
    }
    return inventory, factor_polynomials, parents, parent_sign_digest


def normal_form_inventory(literal_inventory, factor_polynomials, parents):
    allowed = {
        row["factor_id"]: row["allowed_primitive_sign"]
        for row in literal_inventory["literal_rows"]
    }
    support_rows = []
    factor_expansions = {}
    parent_expansions = {}
    for support in SUPPORTS:
        factor_rows = []
        unique = set()
        radial_census = Counter()
        for factor in sorted(allowed):
            order, rows, expanded = initial_form(factor_polynomials[factor], support)
            factor_expansions[(support, factor)] = expanded
            radial_census[order] += 1
            unique.add((order, rows))
            factor_rows.append({
                "factor_id": factor,
                "radial_order": order,
                "allowed_primitive_sign": allowed[factor],
                "primitive_initial_terms": json_rows(rows),
            })
        parent_rows = []
        parent_radial_census = Counter()
        for label, target, polynomial, _terms in parents:
            oriented_polynomial = {
                exponent: target * coefficient
                for exponent, coefficient in polynomial.items()
            }
            order, rows, expanded = initial_form(oriented_polynomial, support)
            parent_expansions[(support, label)] = expanded
            parent_radial_census[order] += 1
            parent_rows.append({
                "label": label,
                "radial_order": order,
                "oriented_initial_terms": json_rows(rows),
                "tangent_point_normal_terms": json_rows(evaluate_tangent(rows)),
            })
        support_rows.append({
            "support": list(support),
            "normal_coordinate_model": [
                {"tangent_variable": tangent, "normal_variable": normal}
                for tangent, normal in coordinate_map(support)
            ],
            "factor_radial_order_census": {
                str(key): value for key, value in sorted(radial_census.items())
            },
            "distinct_factor_initial_forms": len(unique),
            "factor_initial_forms": factor_rows,
            "parent_radial_order_census": {
                str(key): value for key, value in sorted(parent_radial_census.items())
            },
            "parent_initial_forms": parent_rows,
        })
    core = {
        "coordinates": ["a", "g", "h", "n0", "n1", "n2", "n3", "n4", "n5"],
        "tangent_point": [fraction_text(value) for value in TANGENT_POINT],
        "supports": support_rows,
    }
    inventory = {
        "format": "diag9-s1237-six-normal-initial-form-inventory-v1",
        **core,
        "semantic_sha256": semantic_digest(b"diag9-s1237-six-normal-forms-v1", core),
    }
    return inventory, factor_expansions, parent_expansions


def obstruction_certificate(
    literal_inventory, normal_inventory, factor_polynomials,
    factor_expansions, parent_expansions, parent_sign_digest,
):
    opening = json.loads(
        (ROOT / SOURCE_PATHS[0]).read_text(encoding="utf-8")
    )
    require(
        opening["tangential_discovery"]["scope"]
        == "FACE_INTERIOR_TANGENTIAL_FILTER_ONLY_NOT_A_COLLAR_OR_NORMAL_LINK_RESULT",
        "opening tangential scope drift",
    )

    parent_rows = {
        tuple(row["support"]): {
            entry["label"]: entry
            for entry in row["parent_initial_forms"]
        }
        for row in normal_inventory["supports"]
    }
    specifications = (
        ((3, 1, 15), "1237", "1367", (0, 0, 0, 0, 1, 0), "n4=0"),
        ((3, 3, 7), "1237", "1278", (0, 0, 0, 1, 0, 0), "n3=0"),
    )
    singularities = []
    for support, positive_label, negative_label, exponent, forced_facet in specifications:
        positive = parent_rows[support][positive_label]
        negative = parent_rows[support][negative_label]
        positive_rows = tuple(
            (tuple(row["exponent"]), int(row["coefficient"]))
            for row in positive["tangent_point_normal_terms"]
        )
        negative_rows = tuple(
            (tuple(row["exponent"]), int(row["coefficient"]))
            for row in negative["tangent_point_normal_terms"]
        )
        require(positive["radial_order"] == negative["radial_order"] == 1, "Gordan pair order drift")
        require(positive_rows == ((exponent, 1),), "positive Gordan form drift")
        require(negative_rows == ((exponent, -1),), "negative Gordan form drift")
        summed = Counter(dict(positive_rows))
        summed.update(dict(negative_rows))
        require(not {key: value for key, value in summed.items() if value}, "Gordan sum is nonzero")
        singularities.append({
            "support": list(support),
            "positive_parent_label": positive_label,
            "positive_initial_form": json_rows(positive_rows),
            "negative_parent_label": negative_label,
            "negative_initial_form": json_rows(negative_rows),
            "positive_gordan_weights": [1, 1],
            "weighted_sum": [],
            "strict_first_order_parent_link_feasible": False,
            "forced_recursive_facet": forced_facet,
            "exact_consequence": (
                "The two oriented parent inequalities require one linear "
                "normal coordinate to be simultaneously positive and negative."
            ),
        })

    return {
        "format": FORMAT,
        "endpoint": "NORMAL_LINK_REDUCTION_NO_GO",
        "classification": "FINITE_EXACT_COMPUTATION",
        "base": {"commit": OPENING_COMMIT, "tree": OPENING_TREE},
        "scope": {
            "target": "D9_S1237_4SUPPORT_NORMAL_LINK_GATE1",
            "supports": [list(support) for support in SUPPORTS],
            "result": "FIRST_ORDER_PARENT_NORMAL_LINK_SINGULAR_ON_BOTH_SUPPORTS",
            "stops_at_first_exact_singular_link": True,
            "tangential_filter_is_not_a_collar": True,
            "global_active_sector_connectivity": "NOT_CLAIMED",
            "diagonal_9_proof_or_counterexample": "NOT_CLAIMED",
            "honest_9dvl_score": "2/9",
        },
        "source_digests": {
            "literal_inventory": literal_inventory["semantic_sha256"],
            "normal_form_inventory": normal_inventory["semantic_sha256"],
            "normalized_parent_signs": parent_sign_digest,
        },
        "complete_frontier_before_stop": {
            "active_literals": 3_539,
            "labeled_occurrences": 6_167,
            "support_factor_initial_forms": 7_078,
            "support_parent_initial_forms": 140,
            "both_supports_materialized": True,
            "resource_ceiling_crossed": False,
        },
        "obstruction": {
            "kind": "POSITIVE_GORDAN_CERTIFICATE_FOR_STRICT_LINK_INFEASIBILITY",
            "singular_supports": singularities,
            "ordinary_projectivized_strict_parent_link": "EMPTY",
            "higher_weighted_orders_required": True,
            "stabilization_status": "ORDINARY_FIRST_ORDER_LINK_INVALID_BEFORE_RADIUS_STAGE",
            "deterministic_recursive_frontier": [
                {
                    "support": [3, 1, 15],
                    "forced_facet": "n4=0",
                    "next_exact_task": "weighted blow-up retaining second and higher orders of labels 1237 and 1367",
                },
                {
                    "support": [3, 3, 7],
                    "forced_facet": "n3=0",
                    "next_exact_task": "weighted blow-up retaining second and higher orders of labels 1237 and 1278",
                },
            ],
        },
        "nonconsequence": (
            "The ordinary common-radial normal link is singular before residual "
            "factor feasibility can be decided. This negative endpoint does not "
            "exclude weighted parent-safe arcs, construct a collar or mincut, "
            "or prove or disprove diagonal nine."
        ),
    }


def canary_manifest():
    return {
        "format": "diag9-s1237-normal-link-prover-canaries-v1",
        "mutations": [
            "drop-active-literal",
            "flip-allowed-primitive-sign",
            "drop-labeled-occurrence",
            "flip-unit-sign",
            "merge-duplicate-orientation",
            "omit-parent-bracket",
            "omit-normal-direction",
            "delete-gordan-parent-pair",
            "flip-gordan-parent-orientation",
            "claim-ordinary-stabilization-radius",
            "promote-tangential-filter-to-collar",
            "promote-ledger-to-3/9",
        ],
        "expected": "ALL_REJECTED_BY_EXACT_REBUILD",
    }


def build_all():
    manifest = source_manifest()
    literals, factor_polynomials, parents, parent_sign_digest = (
        reconstruct_active_literals()
    )
    normal_forms, factor_expansions, parent_expansions = normal_form_inventory(
        literals, factor_polynomials, parents
    )
    result = obstruction_certificate(
        literals, normal_forms, factor_polynomials,
        factor_expansions, parent_expansions, parent_sign_digest,
    )
    result["semantic_sha256"] = semantic_digest(
        b"diag9-s1237-oriented-normal-link-no-go-v1", result
    )
    return manifest, literals, normal_forms, result, canary_manifest()


def write_json(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--build", action="store_true")
    arguments = parser.parse_args()
    manifest, literals, normal_forms, result, canaries = build_all()
    if arguments.build:
        write_json(HERE / "SOURCE_MANIFEST.json", manifest)
        write_json(HERE / "ACTIVE_LITERAL_INVENTORY.json", literals)
        write_json(HERE / "NORMAL_FORM_INVENTORY.json", normal_forms)
        write_json(HERE / "DIAG9_S1237_NORMAL_LINK_NO_GO.json", result)
        write_json(HERE / "CANARIES.json", canaries)
    print(
        result["endpoint"],
        "singular_supports", len(result["obstruction"]["singular_supports"]),
        "frontier", result["obstruction"]["deterministic_recursive_frontier"],
        "literal_sha256", literals["semantic_sha256"],
        "normal_sha256", normal_forms["semantic_sha256"],
        "result_sha256", result["semantic_sha256"],
    )


if __name__ == "__main__":
    main()
