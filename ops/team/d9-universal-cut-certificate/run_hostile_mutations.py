#!/usr/bin/env python3
"""Adversarial mutation harness for the universal-cut and portability gates."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any, Callable

import verify_portable_predecessor as portable
import verify_universal_cut_certificate as cut


HERE = Path(__file__).resolve().parent
CATALOG = HERE / "HOSTILE_MUTATIONS.json"


class HostileHarnessError(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise HostileHarnessError(message)


def endpoint_fixture(name: str) -> dict[str, Any]:
    for certificate in cut.load_fixtures():
        if certificate["endpoint"] == name:
            return copy.deepcopy(certificate)
    raise HostileHarnessError(f"fixture endpoint missing: {name}")


def reject_certificate(name: str, candidate: dict[str, Any], rejected: list[str], *, preserve_digest: bool = False) -> None:
    if not preserve_digest:
        candidate["semantic_sha256"] = cut.object_digest(
            b"9dvl-d9-universal-cut-certificate-v1", candidate
        )
    try:
        cut.validate_certificate(candidate, allow_fixture=True)
    except (cut.CertificateError, KeyError, IndexError, TypeError):
        rejected.append(name)
        return
    raise HostileHarnessError(f"hostile certificate mutation accepted: {name}")


def certificate_mutations() -> list[str]:
    positive = endpoint_fixture("UNIVERSAL_D9_CUT_OBSTRUCTIONS_UNSAT")
    negative = endpoint_fixture("EXACT_D9_TWO_COMPONENT_SEPARATOR")
    null = endpoint_fixture("UNIVERSAL_CUT_SCHEMA_COVERAGE_GAP")
    timeout = endpoint_fixture("HASH_PINNED_D9_CUT_SCHEMA_FRONTIER")
    cases: list[tuple[str, dict[str, Any], bool]] = []

    candidate = copy.deepcopy(positive)
    candidate["source_binding"]["opening_tree"] = "0" * 40
    cases.append(("opening-tree", candidate, False))
    candidate = copy.deepcopy(positive)
    candidate["quantifiers"]["parents"] = "ONE_PARENT"
    cases.append(("parent-quantifier", candidate, False))
    candidate = copy.deepcopy(positive)
    candidate["grammar"]["residual_wall_type_count"] = 12
    cases.append(("wall-type-count", candidate, False))
    candidate = copy.deepcopy(positive)
    candidate["grammar"]["atoms"][4]["kind"] = "RECURSIVE_BOUNDARY_STRATUM"
    cases.append(("missing-grammar-kind", candidate, False))
    candidate = copy.deepcopy(positive)
    candidate["grammar"]["atoms"].append(copy.deepcopy(candidate["grammar"]["atoms"][-1]))
    cases.append(("duplicate-atom", candidate, False))
    candidate = copy.deepcopy(timeout)
    candidate["grammar"]["pending_atom_ids"].append("a-wall")
    cases.append(("frontier-overlap", candidate, False))
    candidate = copy.deepcopy(null)
    candidate["grammar"]["boundary_contract"]["recursive_facet_default"] = "GLOBAL_SEPARATOR"
    cases.append(("false-recursive-separator", candidate, False))
    candidate = copy.deepcopy(positive)
    candidate["coverage"]["adapter"]["status"] = "INDEPENDENTLY_REPLAYED"
    cases.append(("adapter-status", candidate, False))
    candidate = copy.deepcopy(positive)
    candidate["scope"]["sample_only"] = True
    cases.append(("sample-promotion", candidate, False))
    candidate = copy.deepcopy(negative)
    candidate["scope"]["ledger_after"] = "3/9"
    cases.append(("ledger-mutation", candidate, False))
    candidate = copy.deepcopy(positive)
    candidate["evidence"]["instances"][0]["positive_multipliers"] = ["1", "2"]
    cases.append(("positive-gordan", candidate, False))
    candidate = copy.deepcopy(positive)
    candidate["grammar"]["covered_atom_ids"].remove("e-infinity")
    candidate["grammar"]["pending_atom_ids"] = ["e-infinity"]
    cases.append(("positive-incomplete-coverage", candidate, False))
    candidate = copy.deepcopy(negative)
    candidate["evidence"]["feasible_witnesses"][0]["point"] = ["0"]
    cases.append(("negative-infeasible-witness", candidate, False))
    candidate = copy.deepcopy(negative)
    candidate["evidence"]["separator"]["coefficients"] = ["0", "-1"]
    cases.append(("negative-separator-side", candidate, False))
    candidate = copy.deepcopy(null)
    candidate["coverage"]["status"] = "COMPLETE"
    cases.append(("null-no-gap", candidate, False))
    candidate = copy.deepcopy(null)
    candidate["evidence"]["first_uncovered"]["atom_id"] = "a-wall"
    cases.append(("null-gap-not-pending", candidate, False))
    candidate = copy.deepcopy(timeout)
    candidate["evidence"]["processed"] = ["a-wall"]
    cases.append(("timeout-frontier-drift", candidate, False))
    candidate = copy.deepcopy(timeout)
    candidate["evidence"]["ceiling"]["observed"] = 249_999
    cases.append(("timeout-ceiling-not-reached", candidate, False))
    candidate = copy.deepcopy(positive)
    candidate["endpoint"] = "UNIVERSAL_CUT_SCHEMA_COVERAGE_GAP"
    cases.append(("endpoint-class-mismatch", candidate, False))
    candidate = copy.deepcopy(positive)
    candidate["semantic_sha256"] = "0" * 64
    cases.append(("semantic-digest", candidate, True))

    rejected: list[str] = []
    for name, candidate, preserve_digest in cases:
        reject_certificate(name, candidate, rejected, preserve_digest=preserve_digest)
    return rejected


def reject_portable(name: str, candidate: dict[str, Any], rejected: list[str], *, preserve_digest: bool = False) -> None:
    if not preserve_digest:
        candidate["semantic_sha256"] = portable.object_digest(candidate)
    try:
        portable.validate_adapter(candidate, check_files=False, check_git=False)
    except (portable.PortableReplayError, KeyError, TypeError):
        rejected.append(name)
        return
    raise HostileHarnessError(f"hostile portable mutation accepted: {name}")


def portable_mutations() -> list[str]:
    base = json.loads(portable.ADAPTER_PATH.read_text(encoding="utf-8"))
    mutations: list[tuple[str, Callable[[dict[str, Any]], None], bool]] = [
        ("pretend-historical-object-exists", lambda x: x["historical_referee"].__setitem__("object_existence_claim", "PRESENT"), False),
        ("require-historical-dereference", lambda x: x["historical_referee"].__setitem__("dereference_policy", "REQUIRED"), False),
        ("canonical-state-digest", lambda x: x["canonical_state"].__setitem__("sha256", "0" * 64), False),
        ("reviewed-head-substitution", lambda x: x["reviewed_math"].__setitem__("head", portable.HISTORICAL_REFEREE), False),
        ("mutable-wrapper", lambda x: x["source_derived_replay"].__setitem__("mutable_wrapper", "INVOKED"), False),
        ("producer-acceptance-logic", lambda x: x["source_derived_replay"].__setitem__("acceptance_logic", "PRODUCER_VERIFIER"), False),
        ("source-census-drift", lambda x: x["source_derived_replay"].__setitem__("active_factor_classes", 3538), False),
        ("false-global-coverage", lambda x: x["scope"].__setitem__("global_cut_coverage", "PROVED"), False),
        ("false-diagonal-nine", lambda x: x["scope"].__setitem__("diagonal_9", "PROVED"), False),
        ("false-ledger-promotion", lambda x: x["scope"].__setitem__("ledger", "3/9"), False),
        ("kernel-digest", lambda x: x["source_derived_replay"].__setitem__("kernel_sha256", "0" * 64), False),
        ("portable-semantic-digest", lambda x: x.__setitem__("semantic_sha256", "0" * 64), True),
    ]
    rejected: list[str] = []
    for name, mutate, preserve_digest in mutations:
        candidate = copy.deepcopy(base)
        mutate(candidate)
        reject_portable(name, candidate, rejected, preserve_digest=preserve_digest)
    return rejected


def main() -> None:
    catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
    require(catalog["format"] == "9dvl-d9-universal-cut-hostile-mutations-v1", "hostile catalog format")
    certificate_rejected = certificate_mutations()
    portable_rejected = portable_mutations()
    require(certificate_rejected == catalog["certificate_mutations"], "certificate hostile catalog drift")
    require(portable_rejected == catalog["portable_mutations"], "portable hostile catalog drift")
    require(portable.HISTORICAL_REFEREE not in portable.REQUIRED_GIT_OBJECTS, "absent object entered Git dereference allowlist")
    total = len(certificate_rejected) + len(portable_rejected)
    print(f"PASS hostile mutations rejected {total}/{total}")
    print(f"PASS certificate mutations {len(certificate_rejected)}/{len(certificate_rejected)}")
    print(f"PASS portability mutations {len(portable_rejected)}/{len(portable_rejected)}")
    print("PASS recursive-facet wall cannot be promoted to a global separator")
    print("PASS absent historical referee identifier is not a required Git object")


if __name__ == "__main__":
    main()
