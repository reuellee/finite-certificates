#!/usr/bin/env python3
"""Independent v1 interface audit for diagonal-three master-closure certificates."""

from __future__ import annotations

import copy
import json
from fractions import Fraction
from pathlib import Path


HERE = Path(__file__).resolve().parent
CANARY = HERE / "data" / "DIAG3_PAIR_MASTER_CLOSURE_V1_CANARY.json"


class CertificateError(AssertionError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CertificateError(message)


def load() -> dict:
    with CANARY.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def validate(record: dict) -> None:
    require(
        record.get("format") == "diag3-pair-master-closure-certificate-v1",
        "format",
    )
    require(record.get("status") in {"SCHEMA_CANARY", "CANDIDATE", "COMPLETE"}, "status")
    scope = record["scope"]
    require(scope["parent_index"] == 2599, "parent")
    require(scope["compactification"] == "(Delta^3)^3", "compactification")

    inputs = record["inputs"]
    for key in ("factor_id_digest", "target_signed_parent_digest"):
        value = inputs[key]
        require(
            len(value) == 64 and all(char in "0123456789abcdef" for char in value),
            f"bad digest: {key}",
        )
    require(inputs["active_factor_count"] >= 0, "factor count")

    generator = record["generator"]
    require(generator["deterministic"], "nondeterministic generator")
    require(generator["uncovered_cases"] == 0, "uncovered cases")
    require(generator["unexplained_cells"] == 0, "unexplained cells")
    if scope["global_parameter_coverage_claimed"]:
        require(
            generator["coverage_certificate_kind"]
            in {"exact_semialgebraic_partition", "exact_roadmap_with_link_certificates"},
            "nonexact global coverage",
        )
        require(
            not generator["sample_bank_used_as_coverage"],
            "sample bank promoted to coverage",
        )

    gate = record["transport_gate"]
    require(gate["signed_parent_cell_preserved"], "unsigned transport")
    require(gate["chart_domain_preserved"], "chart transport")
    require(gate["boundary_tags_preserved"], "boundary transport")

    cells = record["cells"]
    by_id = {cell["id"]: cell for cell in cells}
    require(len(by_id) == len(cells), "duplicate cell id")
    for cell in cells:
        require(cell["dimension"] >= 0, "negative dimension")
        require(cell["regular_ball"], "nonregular cell")
        for coordinate in cell["witness"]:
            Fraction(coordinate)
        require(len(set(cell["boundary"])) == len(cell["boundary"]), "duplicate boundary")
        for face in cell["boundary"]:
            require(face in by_id, "unknown boundary cell")
            require(
                by_id[face]["dimension"] == cell["dimension"] - 1,
                "boundary dimension",
            )

    immediate = {
        (cell["id"], face) for cell in cells for face in cell["boundary"]
    }
    closure = set(immediate)
    changed = True
    while changed:
        changed = False
        for high, middle in tuple(closure):
            for middle2, low in tuple(closure):
                if middle == middle2 and (high, low) not in closure:
                    closure.add((high, low))
                    changed = True
    declared = {tuple(pair) for pair in record["strict_closure_pairs"]}
    require(declared == closure, "incomplete or spurious strict closure")

    chains = {
        (high, middle, low)
        for high, middle in immediate
        for middle2, low in immediate
        if middle == middle2
    }
    require(
        {tuple(chain) for chain in record["strict_three_cell_chains"]} == chains,
        "incomplete or spurious three-cell chain",
    )

    infinity = set(record["parent_infinity_subcomplex"])
    require(infinity <= set(by_id), "unknown infinity cell")
    for high in infinity:
        for parent, face in closure:
            if parent == high:
                require(face in infinity, "infinity is not a subcomplex")

    for signature, members in record["bad_signature_membership"].items():
        member_set = set(members)
        require(len(member_set) == len(members), f"duplicate bad member: {signature}")
        require(member_set <= set(by_id), f"unknown bad member: {signature}")
        for high in member_set:
            for parent, face in closure:
                if parent == high:
                    require(face in member_set, f"bad set is not closed: {signature}")

    boundary = record["integral_boundary"]
    c0 = boundary["c0_basis"]
    c1 = boundary["c1_basis"]
    c2 = boundary["c2_basis"]
    require(set(c0 + c1 + c2) <= set(by_id), "unknown boundary basis")
    require(len(set(c0 + c1 + c2)) == len(c0 + c1 + c2), "duplicate basis cell")
    d1 = {(row, col): value for row, col, value in boundary["d1_entries"]}
    d2 = {(row, col): value for row, col, value in boundary["d2_entries"]}
    for vertex in c0:
        for face in c2:
            total = sum(d1.get((vertex, edge), 0) * d2.get((edge, face), 0) for edge in c1)
            require(total == 0, "d_squared is nonzero")

    acceptance = record["acceptance"]
    require(all(acceptance.values()), "unmet declared acceptance gate")


def assert_rejected(record: dict, label: str) -> None:
    try:
        validate(record)
    except (CertificateError, ValueError, KeyError):
        return
    raise AssertionError(f"hostile canary was accepted: {label}")


def main() -> None:
    record = load()
    validate(record)

    corrupt = copy.deepcopy(record)
    corrupt["transport_gate"]["signed_parent_cell_preserved"] = False
    assert_rejected(corrupt, "unsigned parent transport")

    corrupt = copy.deepcopy(record)
    corrupt["scope"]["global_parameter_coverage_claimed"] = True
    corrupt["generator"]["sample_bank_used_as_coverage"] = True
    assert_rejected(corrupt, "sample bank as coverage")

    corrupt = copy.deepcopy(record)
    corrupt["parent_infinity_subcomplex"] = ["e01", "v0"]
    assert_rejected(corrupt, "nonclosed infinity tag")

    corrupt = copy.deepcopy(record)
    corrupt["strict_closure_pairs"].append(["v0", "e01"])
    assert_rejected(corrupt, "dimension-increasing closure")

    corrupt = copy.deepcopy(record)
    corrupt["inputs"]["factor_id_digest"] = "deadbeef"
    assert_rejected(corrupt, "corrupt digest")

    corrupt = copy.deepcopy(record)
    corrupt["integral_boundary"]["d2_entries"][0][2] = -1
    assert_rejected(corrupt, "nonzero d squared")

    print("PASS master-closure v1 certificate interface")
    print("PASS exact closure, infinity, bad-set, and d_squared gates")
    print("PASS 6/6 hostile canaries rejected")
    print("SCOPE schema canary only; no row2599 coverage claim")


if __name__ == "__main__":
    main()
