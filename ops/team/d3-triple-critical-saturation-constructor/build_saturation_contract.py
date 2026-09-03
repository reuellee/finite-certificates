#!/usr/bin/env python3
"""Build the Q0 component-decorated saturation contract.

This constructor does not run a Groebner basis, a saturation, a primary
decomposition, or a real-root census.  It packages the exact source ideal,
the ordered parent-wall localizations, attachment obligations, canaries, and
static job counts needed before such a computation may be authorized.
"""

from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
import json
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OMREAL = ROOT / "ai" / "omreal"
CYCLE = (
    ROOT
    / "ops"
    / "research-team"
    / "cycles"
    / "2026-09-02-d3-triple-critical-saturation-component-gate1"
)
OPENING = CYCLE / "OPENING_STATE.json"
SYSTEM = OMREAL / "data" / "DIAG3_triple_fullspace_critical_h1.json"
CRITICAL_MANIFEST = (
    OMREAL / "data" / "DIAG3_triple_fullspace_critical_h1_manifest.json"
)
CONTRACT = HERE / "SATURATION_CONTRACT.json"
MANIFEST = HERE / "SOURCE_MANIFEST.json"
RESULT = HERE / "RESULT.json"
RUNNER = HERE / "run_q1_saturation.py"
VERIFIER = HERE / "verify_saturation_contract.py"

VARIABLES = tuple("abcdefghi")
ZERO = (0,) * 9
OPENING_REVISION = "ba87af7b1ac58d22c0622c908e31dc8ec03d24fa"
OPENING_TREE = "54bcab4da2eaa441a4d4c3823a8d4593d89e6bda"
TARGET = "D3_TRIPLE_ORBIT5563_COMPONENT_DECORATED_CRITICAL_SATURATION_GATE1"
PRESENTATION = (5_563, 16_134, 19_284)
CANONICAL_ROW = (5_563, 4_373, 23_221)
ALLOWED_CLASSES = (
    "PARENT_WALL",
    "CHART_OR_NORMALIZATION_DIVISOR",
    "OCCURRENCE_OR_CONCURRENCE_RANK_STRATUM",
    "EXTRA_RESIDUAL_FACTOR_FRONTIER",
    "PROJECTIVE_INFINITY",
)

sys.path.insert(0, str(OMREAL))
import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402


class Reject(AssertionError):
    pass


def require(condition: bool, marker: str) -> None:
    if not condition:
        raise Reject(marker)


def digest_bytes(data: bytes) -> str:
    return sha256(data).hexdigest()


def digest_path(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def canonical_digest(value) -> str:
    return digest_bytes(
        json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    )


def seal(value: dict) -> dict:
    value = deepcopy(value)
    value.pop("semantic_sha256", None)
    value["semantic_sha256"] = canonical_digest(value)
    return value


def git(*arguments: str) -> str:
    return subprocess.check_output(
        ["git", *arguments], cwd=ROOT, text=True
    ).strip()


def sparse(polynomial: dict) -> list[list]:
    return [
        [int(coefficient), list(monomial)]
        for monomial, coefficient in sorted(polynomial.items())
        if coefficient
    ]


def degree_terms(terms: list[list]) -> int | None:
    return max((sum(monomial) for _coefficient, monomial in terms), default=None)


def vanishes_on_coordinate_subspace(
    polynomial: dict, zero_variables: tuple[int, ...]
) -> bool:
    return all(
        any(monomial[coordinate] for coordinate in zero_variables)
        for monomial in polynomial
    )


def relative(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def build_source_manifest(opening: dict, critical_manifest: dict) -> dict:
    require(
        git("rev-parse", f"{OPENING_REVISION}^{{tree}}") == OPENING_TREE,
        "opening tree drift",
    )
    require(opening["base"]["commit"] == OPENING_REVISION, "opening revision")
    require(opening["base"]["tree"] == OPENING_TREE, "opening tree")
    require(opening["selected_target"]["id"] == TARGET, "opening target")
    require(opening["q0"]["status"] == "OPEN", "Q0 is not open")
    require(opening["q1"]["status"] == "DENIED_PENDING_Q0", "Q1 is not denied")

    pins = dict(opening["source_pins"])
    pins[relative(OPENING)] = digest_path(OPENING)
    pins[relative(CRITICAL_MANIFEST)] = digest_path(CRITICAL_MANIFEST)
    extra_sources = (
        OMREAL / "DIAG2_PIVOT_REPRESENTATIVE_TRIPLES_VERIFY.py",
        OMREAL / "DIAG9_GRAPH_global_factor_census.py",
        HERE / "build_saturation_contract.py",
        RUNNER,
        VERIFIER,
    )
    for path in extra_sources:
        pins[relative(path)] = digest_path(path)

    for source, expected in opening["source_pins"].items():
        require(digest_path(ROOT / source) == expected, f"opening source drift: {source}")
    require(
        critical_manifest["system_sha256"] == digest_path(SYSTEM),
        "critical system digest drift",
    )
    for filename, expected in critical_manifest["source_sha256"].items():
        require(
            digest_path(OMREAL / filename) == expected,
            f"critical source drift: {filename}",
        )

    return seal(
        {
            "format": "d3-triple-critical-saturation-constructor-source-manifest-v1",
            "track_id": "d3-triple-critical-saturation-constructor",
            "opening_revision": OPENING_REVISION,
            "opening_tree": OPENING_TREE,
            "pins": dict(sorted(pins.items())),
            "source_policy": {
                "network_or_connector_used": False,
                "external_compute_used": False,
                "raw_groebner_or_rur_run": False,
                "constructor_self_acceptance": False,
            },
        }
    )


def source_census(system: dict) -> dict:
    equations = system["equations"]
    nonzero = [equation for equation in equations if equation["terms"]]
    degree_census: dict[str, int] = {}
    kind_census: dict[str, int] = {}
    for equation in equations:
        kind_census[equation["kind"]] = kind_census.get(equation["kind"], 0) + 1
        degree = degree_terms(equation["terms"])
        key = "ZERO" if degree is None else str(degree)
        degree_census[key] = degree_census.get(key, 0) + 1
    coefficients = [
        abs(coefficient)
        for equation in equations
        for coefficient, _monomial in equation["terms"]
    ]
    census = {
        "formal_generator_count": len(equations),
        "nonzero_generator_count": len(nonzero),
        "zero_generator_count": len(equations) - len(nonzero),
        "kind_census": dict(sorted(kind_census.items())),
        "degree_census": dict(sorted(degree_census.items())),
        "sparse_term_count": sum(len(equation["terms"]) for equation in equations),
        "maximum_coefficient_absolute_value": max(coefficients),
        "maximum_coefficient_bit_length": max(coefficients).bit_length(),
    }
    require(
        census
        == {
            "formal_generator_count": 59,
            "nonzero_generator_count": 55,
            "zero_generator_count": 4,
            "kind_census": {"factor": 3, "height_minor": 56},
            "degree_census": {"2": 1, "4": 1, "5": 1, "8": 52, "ZERO": 4},
            "sparse_term_count": 14_741,
            "maximum_coefficient_absolute_value": 7,
            "maximum_coefficient_bit_length": 3,
        },
        "source census drift",
    )
    return census


def parent_wall_ledger() -> tuple[list[dict], list[tuple[str, dict, int]]]:
    records = list(labeled.parent_bracket_factors())
    require(len(records) == 62, "nonconstant parent bracket count")
    require(len({label for label, _polynomial, _sign in records}) == 62, "wall labels")
    degrees = [max(map(sum, polynomial)) for _label, polynomial, _sign in records]
    require(
        {degree: degrees.count(degree) for degree in set(degrees)} == {1: 36, 2: 24, 3: 2},
        "parent wall degree census",
    )
    require(sum(degrees) == 90, "parent wall degree sum")
    require(sum(len(polynomial) for _label, polynomial, _sign in records) == 201, "wall terms")

    ledger = []
    for index, (label, polynomial, normalization_sign) in enumerate(records):
        encoded = sparse(polynomial)
        factor_degree = max(map(sum, polynomial))
        relation_terms = len(encoded) + 1
        ledger.append(
            seal(
                {
                    "stage_index": index,
                    "stage_id": f"SAT-PARENT-{index:02d}-{label}",
                    "saturator_id": f"H_{index:02d}_{label}",
                    "attachment_class": "PARENT_WALL",
                    "parent_bracket_label": label,
                    "normalization_sign": normalization_sign,
                    "degree": factor_degree,
                    "term_count": len(encoded),
                    "sparse_polynomial": encoded,
                    "rabinowitsch_step": {
                        "input_ideal": f"J_{index:02d}",
                        "output_ideal": f"J_{index + 1:02d}",
                        "auxiliary_variable": "u",
                        "relation": f"1-u*H_{index:02d}_{label}=0",
                        "relation_degree": factor_degree + 1,
                        "relation_term_count": relation_terms,
                        "elimination_identity": (
                            f"J_{index + 1:02d}="
                            f"(J_{index:02d}+<1-u*H_{index:02d}_{label}>)"
                            ".intersection(Q[a,b,c,d,e,f,g,h,i])"
                        ),
                        "saturation_identity": (
                            f"J_{index + 1:02d}=J_{index:02d}:"
                            f"H_{index:02d}_{label}^infinity"
                        ),
                    },
                    "component_attachment_contract": {
                        "removed_primary_component_witness": (
                            "For every omitted primary component Q, emit n>=1 and an exact "
                            "reduction certificate H^n in Q."
                        ),
                        "containment_consequence": (
                            f"H_{index:02d}_{label}^n in Q implies "
                            f"V(Q) subset V(H_{index:02d}_{label}), the named parent wall {label}."
                        ),
                        "wall_branch_preserved_as": (
                            f"A_{index:02d}=J_{index:02d}+<H_{index:02d}_{label}>"
                        ),
                        "set_identity": (
                            f"V(J_{index:02d})=V(J_{index + 1:02d}) union V(A_{index:02d})"
                        ),
                    },
                }
            )
        )
    return ledger, records


def fourspace_canaries(
    critical_manifest: dict,
    records: list[tuple[str, dict, int]],
    system: dict,
) -> list[dict]:
    answer = []
    discriminating_walls = ("1346", "1247")
    for component_index, component in enumerate(
        critical_manifest["raw_coordinate_boundary_components"]
    ):
        zero_variables = tuple(component["zero_variable_indices"])
        source_polynomials = [
            {tuple(monomial): int(coefficient) for coefficient, monomial in equation["terms"]}
            for equation in system["equations"]
        ]
        require(
            all(
                vanishes_on_coordinate_subspace(polynomial, zero_variables)
                for polynomial in source_polynomials
            ),
            "fourspace source-ideal containment",
        )
        exact_walls = [
            label
            for label, polynomial, _sign in records
            if vanishes_on_coordinate_subspace(polynomial, zero_variables)
        ]
        require(
            exact_walls == component["identically_zero_parent_brackets"],
            "fourspace wall replay",
        )
        require(len(exact_walls) == 23, "fourspace wall count")
        first_ordered_index = next(
            index for index, (label, _polynomial, _sign) in enumerate(records)
            if label in exact_walls
        )
        first_ordered_label, _first_ordered_polynomial, _sign = records[
            first_ordered_index
        ]
        require(first_ordered_label == "1236", "fourspace first ordered wall")
        canary_label = discriminating_walls[component_index]
        canary_index = next(
            index for index, (label, _polynomial, _sign) in enumerate(records)
            if label == canary_label
        )
        _label, canary_polynomial, _sign = records[canary_index]
        require(canary_label in exact_walls, "discriminating canary attachment")
        require(
            vanishes_on_coordinate_subspace(canary_polynomial, zero_variables),
            "fourspace canary identity",
        )
        canary_variable = "a" if component_index == 0 else "e"
        require(
            canary_polynomial == {
                tuple(1 if index == VARIABLES.index(canary_variable) else 0 for index in range(9)): 1
            },
            "discriminating wall polynomial",
        )
        answer.append(
            seal(
                {
                    "canary_id": f"KNOWN-COORDINATE-FOURSPACE-{component_index}",
                    "coordinate_ideal": [
                        VARIABLES[index] for index in zero_variables
                    ],
                    "free_variables": component["free_variables"],
                    "dimension": 4,
                    "all_source_equations_vanish_identically": True,
                    "named_parent_wall_memberships": exact_walls,
                    "membership_count": len(exact_walls),
                    "first_wall_in_full_order": {
                        "stage_index": first_ordered_index,
                        "parent_wall": first_ordered_label,
                    },
                    "discriminating_isolated_canary": {
                        "stage_index_in_full_order": canary_index,
                        "parent_wall": canary_label,
                        "polynomial": canary_variable,
                        "other_fourspace_has_this_coordinate_free": True,
                    },
                    "exact_localization_contradiction": (
                        f"{canary_label}={canary_variable} belongs to the coordinate "
                        f"ideal, while 1-u*{canary_variable} reduces to 1 modulo that "
                        "ideal; hence this named-wall localization has no point on the "
                        "four-space."
                    ),
                    "attachment_class": "PARENT_WALL",
                    "no_artificial_boundary_used": True,
                }
            )
        )
    return answer


def hostile_canaries(system: dict) -> list[dict]:
    first_minor = next(
        equation
        for equation in system["equations"]
        if equation["kind"] == "height_minor" and equation["terms"]
    )
    return [
        seal(
            {
                "canary_id": "HOSTILE-BOX-FACE-AS-INFINITY",
                "candidate": "128*a-1=0",
                "claimed_attachment_class": "PROJECTIVE_INFINITY",
                "accepted": False,
                "rejection": (
                    "ARTIFICIAL_BOX_FACE_NOT_A_SOURCE_PARENT_WALL_OR_A_HOMOGENIZING_DIVISOR"
                ),
            }
        ),
        seal(
            {
                "canary_id": "HOSTILE-CHART-SEAM-AS-INFINITY",
                "candidate": "an auxiliary chart denominator z_chart=0",
                "claimed_attachment_class": "PROJECTIVE_INFINITY",
                "accepted": False,
                "rejection": (
                    "CHART_SEAM_REQUIRES_CHART_OR_NORMALIZATION_DIVISOR_CLASS_AND_AN_EXACT_CROSS_CHART_COVERAGE_WITNESS"
                ),
            }
        ),
        seal(
            {
                "canary_id": "HOSTILE-WITNESS-RANK-LOSS-AS-INFINITY",
                "candidate": {
                    "source_height_minor_columns": first_minor["columns"],
                    "semantic_sha256": canonical_digest(first_minor),
                },
                "claimed_attachment_class": "PROJECTIVE_INFINITY",
                "accepted": False,
                "rejection": (
                    "SOURCE_CRITICAL_GENERATOR_CANNOT_BE_A_SATURATOR: "
                    "I:M^infinity=<1> WHEN M_IN_I"
                ),
            }
        ),
    ]


def job_census(source: dict, ledger: list[dict], critical_manifest: dict) -> dict:
    relation_terms = sum(
        stage["rabinowitsch_step"]["relation_term_count"] for stage in ledger
    )
    relation_degree_sum = sum(
        stage["rabinowitsch_step"]["relation_degree"] for stage in ledger
    )
    nonzero_degree_sum = sum(
        degree_terms(equation["terms"])
        for equation in source["equations"]
        if equation["terms"]
    )
    modular_10 = critical_manifest["modular_feasibility"]["10"]
    rows_10 = (
        modular_10["primes"]["2"]["rows_q"]
        + modular_10["primes"]["2"]["rows_minor"]
    )
    columns_10 = modular_10["monomials"]
    dense_uint64_bytes = rows_10 * columns_10 * 8
    census = {
        "base_ring": {
            "coefficient_field": "Q",
            "variable_count": 9,
            "variables": list(VARIABLES),
        },
        "source_ideal": source_census(source),
        "parent_boundary": {
            "raw_bracket_coordinate_count": 70,
            "nonzero_constant_brackets_not_saturated": 8,
            "nonconstant_wall_saturator_count": len(ledger),
            "wall_degree_census": {"1": 36, "2": 24, "3": 2},
            "wall_degree_sum": sum(stage["degree"] for stage in ledger),
            "wall_sparse_term_count": sum(stage["term_count"] for stage in ledger),
        },
        "ordered_sequential_compilation": {
            "stage_count": len(ledger),
            "transient_auxiliary_variables_per_stage": 1,
            "maximum_transient_variable_count": 10,
            "fixed_rabinowitsch_relation_count": len(ledger),
            "fixed_rabinowitsch_relation_term_count": relation_terms,
            "post_stage_basis_generator_counts": "RUNTIME_EXACT_OUTPUT_REQUIRED",
        },
        "simultaneous_preflight_representation_not_execution_order": {
            "variable_count": 9 + len(ledger),
            "formal_equation_count": 59 + len(ledger),
            "nonzero_equation_count": 55 + len(ledger),
            "sparse_term_count": 14_741 + relation_terms,
            "maximum_total_degree": 8,
            "sum_of_nonzero_generator_degrees": nonzero_degree_sum + relation_degree_sum,
        },
        "prior_degree_10_modular_screen": {
            "monomial_columns": columns_10,
            "rows": rows_10,
            "rank_over_F2_and_F3": modular_10["primes"]["2"]["rank"],
            "dense_uint64_projection_bytes": dense_uint64_bytes,
            "dense_uint64_projection_gib": round(dense_uint64_bytes / (1 << 30), 6),
            "status": "DIAGNOSTIC_ONLY_NOT_A_CHARACTERISTIC_ZERO_FORECAST",
        },
    }
    require(census["simultaneous_preflight_representation_not_execution_order"] == {
        "variable_count": 71,
        "formal_equation_count": 121,
        "nonzero_equation_count": 117,
        "sparse_term_count": 15_004,
        "maximum_total_degree": 8,
        "sum_of_nonzero_generator_degrees": 579,
    }, "static job census")
    return census


def build_contract(
    opening: dict, system: dict, critical_manifest: dict, source_manifest: dict
) -> dict:
    require(tuple(system["variables"]) == VARIABLES, "system variables")
    require(tuple(system["named_presentation"]) == PRESENTATION, "presentation")
    require(tuple(system["canonical_row"]) == CANONICAL_ROW, "canonical row")
    ledger, records = parent_wall_ledger()
    canaries = fourspace_canaries(critical_manifest, records, system)
    hostile = hostile_canaries(system)
    contract = {
        "format": "d3-triple-component-decorated-saturation-contract-v1",
        "track_id": "d3-triple-critical-saturation-constructor",
        "opening_revision": OPENING_REVISION,
        "opening_tree": OPENING_TREE,
        "target": {
            "id": TARGET,
            "named_presentation": list(PRESENTATION),
            "canonical_row": list(CANONICAL_ROW),
            "height_coordinate": "b",
            "coefficient_field": "Q",
        },
        "source_manifest_semantic_sha256": source_manifest["semantic_sha256"],
        "source_ideal": {
            "ideal_id": "J_00",
            "artifact": relative(SYSTEM),
            "artifact_sha256": digest_path(SYSTEM),
            "artifact_semantic_sha256": canonical_digest(system),
            "ordered_generator_contract": (
                "the three residual factors followed by all 56 formal height-b minors; "
                "the four zero minors remain explicit formal records"
            ),
            "census": source_census(system),
        },
        "saturation_contract": {
            "ordered": True,
            "anonymous_product_saturation_used": False,
            "initial_ideal": "J_00",
            "final_ideal": "J_62",
            "stage_count": len(ledger),
            "stage_order": [stage["stage_id"] for stage in ledger],
            "stages": ledger,
            "execution_rule": (
                "Execute all Rabinowitsch eliminations one at a time in the recorded order; "
                "retain each wall branch and every exact reduction witness."
            ),
            "allowed_attachment_classes": list(ALLOWED_CLASSES),
            "classes_used_by_this_ledger": ["PARENT_WALL"],
            "unsaturated_classes_retained": list(ALLOWED_CLASSES[1:]),
        },
        "singular_locus_retention": {
            "all_59_formal_source_equations_retained_at_every_stage": True,
            "height_minors_used_as_saturators": False,
            "residual_factors_used_as_saturators": False,
            "jacobian_rank_or_singularity_equations_used_as_saturators": False,
            "exact_open_set_identity": (
                "V(J_00) intersect D(PRODUCT(H_00,...,H_61)) equals "
                "V(J_62) intersect D(PRODUCT(H_00,...,H_61)); therefore every "
                "singular source point in the parent interior is retained."
            ),
            "qualification": (
                "Singular loci on a saturated parent wall may leave the interior branch "
                "only through that named wall branch; no other singular locus is discarded."
            ),
        },
        "known_fourspace_canaries": canaries,
        "hostile_boundary_canaries": hostile,
        "job_census": job_census(system, ledger, critical_manifest),
        "numeric_local_resource_forecast": {
            "forecast_kind": "PREREGISTERED_HARD_BUDGET_WITH_LOW_CONFIDENCE",
            "exact_backend": {
                "environment": "WSL lee-dev",
                "prefix": "/home/lee/.local/share/9dvl-exact-cas/v1",
                "engine": "Singular 4.4.1",
                "library": "elim.lib",
                "procedure": "sat_with_exp",
                "use": "SEQUENTIAL_ONE_NAMED_PARENT_WALL_AT_A_TIME",
            },
            "ordered_saturation_stages": len(ledger),
            "per_stage_wall_seconds": 180,
            "stage_wall_seconds": len(ledger) * 180,
            "preflight_and_certificate_seconds": 1_440,
            "projected_total_wall_seconds": len(ledger) * 180 + 1_440,
            "projected_total_wall_minutes": (len(ledger) * 180 + 1_440) // 60,
            "projected_peak_ram_gib": 7,
            "projected_scratch_gib": 9,
            "cycle_ceiling_wall_seconds": 14_400,
            "cycle_ceiling_peak_ram_gib": 32,
            "cycle_ceiling_scratch_gib": 10,
            "observed_wsl_ram_gib": 7.676846,
            "observed_host_physical_ram_gib": 15.835438,
            "numeric_envelope_inside_ceiling": True,
            "numeric_envelope_inside_observed_wsl_ram": True,
            "empirical_exact_cas_calibration_available": False,
            "construction_replay_baselines": {
                "exact_d3_source_replay_wall_seconds": 4.802,
                "exact_d3_source_replay_peak_mib": 213.7,
                "d9_inverse_circuit_check_wall_seconds": 0.789,
                "d9_inverse_circuit_check_peak_mib": 35.4,
                "scope": "CONSTRUCTION_AND_REPLAY_ONLY_NOT_SATURATION_SOLVE",
            },
            "confidence": "LOW",
            "hard_stop_rule": (
                "Stop before a stage exceeds 180 seconds or observed RSS exceeds 7 GiB; "
                "preserve the exact last completed J_k and return TIMEOUT."
            ),
            "forecast_consequence": (
                "The arithmetic envelope is inside the ceiling, but lack of an empirical "
                "exact-CAS calibration is an independent-verifier acceptance risk."
            ),
        },
        "conditional_q1_executor": {
            "path": relative(RUNNER),
            "sha256": digest_path(RUNNER),
            "q0_safe_modes": ["--dry-run", "--smoke-test"],
            "guard": (
                "--execute requires an independent ACCEPT artifact bound to both the "
                "contract byte digest and semantic digest"
            ),
            "method": (
                "Singular 4.4.1 elim.lib sat_with_exp, one named parent wall per "
                "fresh 180-second/7-GiB-limited process, with saturation exponent, "
                "standard-basis state, timing, and peak-RSS frontier retained"
            ),
            "scope_after_all_62_stages": (
                "SATURATION_ONLY; Q1 still requires dimension, real-root, component "
                "attachment, chamber classification, true-infinity, and S8 checks"
            ),
        },
        "constructor_replay": {
            "path": relative(VERIFIER),
            "sha256": digest_path(VERIFIER),
            "independent_verifier": False,
            "hostile_mutation_count": 27,
        },
        "q0_disposition": {
            "constructor_status": "CANDIDATE_HANDOFF_ONLY",
            "independently_accepted": False,
            "q0_closed": False,
            "q1_status": "DENIED_PENDING_INDEPENDENT_Q0_ACCEPTANCE",
            "theorem_ledger_before": "2/9",
            "theorem_ledger_after": "2/9",
            "triple_source_residual_before": 1_162_302,
            "triple_source_residual_after": 1_162_302,
            "nonconsequence": (
                "This contract does not prove zero-dimensionality, emptiness, a real-root "
                "census, parent-chamber coverage, true-infinity continuation, or S8 transfer."
            ),
        },
    }
    return seal(contract)


def build_result(contract: dict, source_manifest: dict) -> dict:
    return seal(
        {
            "format": "d3-triple-critical-saturation-constructor-result-v1",
            "track_id": "d3-triple-critical-saturation-constructor",
            "target": TARGET,
            "endpoint": "Q0_CANDIDATE_HANDOFF_PENDING_INDEPENDENT_REPLAY",
            "accepted": False,
            "q0_status": "CANDIDATE",
            "q1_status": "DENIED_PENDING_INDEPENDENT_Q0_ACCEPTANCE",
            "contract": relative(CONTRACT),
            "contract_sha256": digest_path(CONTRACT),
            "contract_semantic_sha256": contract["semantic_sha256"],
            "source_manifest": relative(MANIFEST),
            "source_manifest_sha256": digest_path(MANIFEST),
            "source_manifest_semantic_sha256": source_manifest["semantic_sha256"],
            "ordered_parent_wall_saturators": 62,
            "known_fourspace_canaries": 2,
            "hostile_boundary_canaries": 3,
            "theorem_ledger_before": "2/9",
            "theorem_ledger_after": "2/9",
            "triple_source_residual_before": 1_162_302,
            "triple_source_residual_after": 1_162_302,
        }
    )


def write_json(path: Path, value: dict) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="ascii")


def main() -> None:
    opening = json.loads(OPENING.read_text(encoding="utf-8"))
    system = json.loads(SYSTEM.read_text(encoding="ascii"))
    critical_manifest = json.loads(CRITICAL_MANIFEST.read_text(encoding="utf-8"))
    source_manifest = build_source_manifest(opening, critical_manifest)
    write_json(MANIFEST, source_manifest)
    contract = build_contract(opening, system, critical_manifest, source_manifest)
    write_json(CONTRACT, contract)
    result = build_result(contract, source_manifest)
    write_json(RESULT, result)
    print("WROTE", relative(MANIFEST), digest_path(MANIFEST))
    print("WROTE", relative(CONTRACT), digest_path(CONTRACT))
    print("WROTE", relative(RESULT), digest_path(RESULT))
    print("Q0 CANDIDATE ONLY; Q1 DENIED; LEDGER 2/9; RESIDUAL 1162302")


if __name__ == "__main__":
    main()
