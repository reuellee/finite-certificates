#!/usr/bin/env python3
"""Build the exact D9 roadmap projection/stratification preflight.

This producer does not solve critical systems.  It reconstructs the pinned
S12,37 factor inventory, derives exact system/frontier counts, and enforces the
opening resource ceiling before any expensive enumeration is authorized.
"""

from __future__ import annotations

import argparse
from collections import Counter
import contextlib
from io import StringIO
import hashlib
import json
from math import comb, gcd
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OM = ROOT / "ai/omreal"
PRIOR = ROOT / "ops/team/diag9-s1237-normal-link-prover"
OUTPUT = HERE / "PROJECTION_STRATIFICATION_PREFLIGHT.json"

BASE_REVISION = "90134ab3501eb77d56bbbf126817b41f5d2e6736"
BASE_TREE = "348bad06165af070fab51fa74cdc727b898c8a02"
SYSTEM_CEILING = 100_000
PROJECTION_VECTOR = tuple(1 << index for index in range(9))

SOURCE_PATHS = (
    "ops/research-team/cycles/2026-09-01-d9-component-roadmap/OPENING_AUDIT.json",
    "ops/team/d9-component-roadmap-certificate/RESULT.json",
    "ops/team/diag9-s1237-normal-link-prover/ACTIVE_LITERAL_INVENTORY.json",
    "ops/team/diag9-s1237-normal-link-prover/build_normal_link_no_go.py",
    "ai/omreal/DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY.py",
    "ai/omreal/verify_diag3_pair_global_parent_face_gate.py",
    "ai/omreal/certs_4_8.jsonl",
    "ai/omreal/data/CANONICAL_RESEARCH_STATE_V4.json",
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as source:
        for block in iter(lambda: source.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def census(values) -> dict[str, int]:
    return {
        str(key): count
        for key, count in sorted(Counter(values).items())
    }


def polynomial_degree(polynomial: dict) -> int:
    return max(sum(exponent) for exponent in polynomial)


def load_prior_producer():
    print("loading exact active-sector dependencies", flush=True)
    sys.path.insert(0, str(PRIOR))
    sys.path.insert(0, str(OM))
    with contextlib.redirect_stdout(StringIO()):
        import build_normal_link_no_go as prior
    return prior


def build() -> dict:
    prior = load_prior_producer()
    print("reconstructing the 3,539-factor S12,37 inventory", flush=True)
    rebuilt, factor_polynomials, parents, parent_sign_digest = (
        prior.reconstruct_active_literals()
    )
    stored = json.loads(
        (PRIOR / "ACTIVE_LITERAL_INVENTORY.json").read_text(encoding="utf-8")
    )
    require(rebuilt == stored, "active literal inventory does not rebuild")

    active_factors = tuple(row["factor_id"] for row in rebuilt["literal_rows"])
    require(len(active_factors) == rebuilt["factor_count"] == 3_539, "factor census")
    require(len(set(active_factors)) == len(active_factors), "duplicate active factor")

    factor_degrees = [polynomial_degree(factor_polynomials[index]) for index in active_factors]
    factor_terms = [len(factor_polynomials[index]) for index in active_factors]
    parent_degrees = [polynomial_degree(polynomial) for _label, _sign, polynomial, _terms in parents]
    parent_terms = [len(polynomial) for _label, _sign, polynomial, _terms in parents]
    require(len(parents) == 70, "parent bracket census")

    one_wall_systems = len(active_factors)
    naive_pair_strata = comb(len(active_factors), 2)
    naive_one_and_two_wall_systems = one_wall_systems + naive_pair_strata
    require(naive_pair_strata == 6_260_491, "pair-stratum arithmetic")
    require(naive_one_and_two_wall_systems == 6_264_030, "system-frontier arithmetic")

    state = json.loads(
        (OM / "data/CANONICAL_RESEARCH_STATE_V4.json").read_text(encoding="utf-8")
    )
    local_candidates = state["completed_cycle"]["circuit_gate"][
        "persistent_support_candidates"
    ]
    require(local_candidates == 2_420, "local candidate census")
    require(gcd(*PROJECTION_VECTOR) == 1, "projection vector is not primitive")

    result = {
        "format": "d9-component-roadmap-projection-stratification-preflight-v1",
        "track_id": "d9-component-roadmap-constructor",
        "base_revision": BASE_REVISION,
        "base_tree": BASE_TREE,
        "scope": "EXACT_PREFLIGHT_NO_CRITICAL_SYSTEMS_SOLVED",
        "source_pins": {
            relative: sha256(ROOT / relative) for relative in SOURCE_PATHS
        },
        "fixed_domain": {
            "parent_index": rebuilt["parent_index"],
            "family": rebuilt["family"],
            "active_factor_classes": len(active_factors),
            "active_occurrences": rebuilt["occurrence_count"],
            "parent_brackets": len(parents),
            "parent_sign_digest": parent_sign_digest,
        },
        "polynomial_inventory": {
            "variables": list("abcdefghi"),
            "active_factor_degree_census": census(factor_degrees),
            "active_factor_term_count_census": census(factor_terms),
            "active_factor_max_degree": max(factor_degrees),
            "active_factor_max_terms": max(factor_terms),
            "parent_degree_census": census(parent_degrees),
            "parent_term_count_census": census(parent_terms),
            "factored_boundary_barrier_factors": len(parents),
            "factored_boundary_barrier_total_degree": sum(parent_degrees),
            "expanded_boundary_barrier_required": False,
        },
        "projection": {
            "coordinates": list("abcdefghi"),
            "primitive_integer_vector": list(PROJECTION_VECTOR),
            "linear_form": "+".join(
                f"{coefficient}*{variable}"
                for coefficient, variable in zip(PROJECTION_VECTOR, "abcdefghi", strict=True)
            ),
            "one_wall_system": "q=0 and lambda_0*d_j(q)-lambda_j*d_0(q)=0 for j=1..8",
            "equations_per_one_wall_system": 9,
            "genericity_discriminant_certificate": "ABSENT",
            "specialization_authorized": False,
        },
        "stratification_frontier": {
            "one_wall_systems": one_wall_systems,
            "naive_pair_strata": naive_pair_strata,
            "naive_one_and_two_wall_systems": naive_one_and_two_wall_systems,
            "opening_system_ceiling": SYSTEM_CEILING,
            "naive_frontier_exceeds_ceiling": naive_one_and_two_wall_systems > SYSTEM_CEILING,
            "known_memoryless_local_candidates": local_candidates,
            "known_local_candidates_complete_for_global_multiwalls": False,
            "required_filter": "SOURCE_DERIVED_COMPLETE_ACTIVE_MULTIWALL_INCIDENCE",
            "positive_dimensional_singular_strata_must_be_registered": True,
        },
        "endpoint": "STRATIFIED_SYSTEM_FRONTIER_EXCEEDS_GATE_WITHOUT_COMPLETE_INCIDENCE_FILTER",
        "classification": "EXACT_FAIL_CLOSED_PREFLIGHT_NULL",
        "critical_systems_solved": 0,
        "critical_enumeration_authorized": False,
        "exact_consequence": "ONE_WALL_SYSTEMS_FIT_THE_CEILING_BUT_THE_UNFILTERED_PAIR_STRATUM_FRONTIER_DOES_NOT",
        "nonconsequences": [
            "NO_PROOF_THAT_ALL_PAIR_STRATA_ARE_NONEMPTY",
            "NO_PROOF_THAT_THE_2420_LOCAL_CANDIDATES_ARE_GLOBALLY_COMPLETE",
            "NO_GENERIC_PROJECTION_SPECIALIZATION_CERTIFICATE",
            "NO_FIXED_DOMAIN_ROADMAP",
            "NO_FIXED_DOMAIN_CONNECTIVITY_OR_DISCONNECTION",
            "NO_DIAGONAL_9_RESULT",
            "NO_9DVL_SCORE_CHANGE",
        ],
        "next_action": "Construct a source-derived complete active multiwall-incidence filter and an exact projection-discriminant exclusion certificate before solving any critical system.",
        "theorem_ledger": "2/9",
    }
    return result


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    arguments = parser.parse_args()
    result = build()
    if arguments.write:
        OUTPUT.write_bytes((json.dumps(result, indent=2, sort_keys=True) + "\n").encode("utf-8"))
        print(f"wrote {OUTPUT.relative_to(ROOT)}", flush=True)
    print(f"endpoint={result['endpoint']}")
    frontier = result["stratification_frontier"]
    print(
        "systems",
        frontier["one_wall_systems"],
        frontier["naive_pair_strata"],
        frontier["opening_system_ceiling"],
    )
    print("critical_enumeration=DENIED")


if __name__ == "__main__":
    main()
