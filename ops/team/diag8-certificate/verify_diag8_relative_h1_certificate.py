#!/usr/bin/env python3
"""Independent exact replay for the abstract diagonal-eight H1 interface.

The verifier deliberately has no producer or discovery dependency.  It checks
a finite labelled regular-CW *interface*, forms every proper dominance-
antichain of the requested size, deletes the certified true-infinity
subcomplex by passing to relative cellular chains, and computes H1 over F2.

Geometry is outside this algebraic verifier.  Missing, undischarged, or
digest-mismatched geometry obligations fail closed.  A discharged reference
binds the abstract certificate to external evidence; it does not cause this
program to claim that the external evidence is mathematically correct.
"""

from __future__ import annotations

import copy
import hashlib
import json
from collections import Counter
from itertools import combinations
from pathlib import Path
from typing import Iterable


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[2]
FIXTURES = HERE / "DIAG8_RELATIVE_H1_FIXTURES.json"
FORMAT = "diag8-relative-h1-certificate-v1"
FIXTURE_FORMAT = "diag8-relative-h1-fixtures-v1"
REQUIRED_OBLIGATIONS = {
    "ambient_coverage",
    "regular_cell_structure",
    "complete_cellular_incidence",
    "complete_signature_labels",
    "genuine_true_infinity_identification",
    "relative_model_matches_target_space",
}


class CertificateError(AssertionError):
    """A fail-closed schema or exact-replay rejection."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise CertificateError(message)


def exact_keys(record: dict, expected: set[str], context: str) -> None:
    require(isinstance(record, dict), f"{context}: expected object")
    require(set(record) == expected, f"{context}: wrong fields")


def is_sha256(value: object) -> bool:
    return (
        isinstance(value, str)
        and len(value) == 64
        and all(character in "0123456789abcdef" for character in value)
    )


def repository_path(relative: object) -> Path:
    require(isinstance(relative, str) and relative, "external evidence: path")
    path = (HERE / relative).resolve()
    try:
        path.relative_to(REPOSITORY)
    except ValueError as error:
        raise CertificateError("external evidence: path escapes repository") from error
    require(path.is_file(), "external evidence: missing artifact")
    return path


def check_external_geometry(record: dict) -> None:
    exact_keys(record, {"artifact", "sha256", "obligations"}, "external geometry")
    require(is_sha256(record["sha256"]), "external geometry: bad digest")
    path = repository_path(record["artifact"])
    actual = hashlib.sha256(path.read_bytes()).hexdigest()
    require(actual == record["sha256"], "external geometry: digest mismatch")

    obligations = record["obligations"]
    require(isinstance(obligations, dict), "external geometry: obligations")
    require(set(obligations) == REQUIRED_OBLIGATIONS, "external geometry: incomplete obligations")
    require(
        all(status == "DISCHARGED_EXTERNALLY" for status in obligations.values()),
        "external geometry: undischarged obligation",
    )


def gf2_rank(rows: list[int], column_count: int) -> int:
    """Rank of bit-packed rows over F2, without numeric dependencies."""
    work = list(rows)
    rank = 0
    for column in range(column_count):
        pivot = next(
            (row_index for row_index in range(rank, len(work)) if (work[row_index] >> column) & 1),
            None,
        )
        if pivot is None:
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        for row_index in range(len(work)):
            if row_index != rank and ((work[row_index] >> column) & 1):
                work[row_index] ^= work[rank]
        rank += 1
    return rank


def boundary_rows(
    cells_by_dimension: dict[int, list[str]],
    boundary: dict[str, dict[str, int]],
    dimension: int,
) -> list[int]:
    rows = []
    columns = cells_by_dimension[dimension]
    for low in cells_by_dimension[dimension - 1]:
        packed = 0
        for column, high in enumerate(columns):
            if boundary[high].get(low, 0) % 2:
                packed |= 1 << column
        rows.append(packed)
    return rows


def strict_subsets(left: frozenset[str], right: frozenset[str]) -> bool:
    return left < right


def maximum_bipartite_matching(adjacency: list[list[int]], right_count: int) -> int:
    """Deterministic augmenting-path matching, sufficient for Dilworth."""
    matched_right = [-1] * right_count

    def augment(left: int, seen: set[int]) -> bool:
        for right in adjacency[left]:
            if right in seen:
                continue
            seen.add(right)
            owner = matched_right[right]
            if owner == -1 or augment(owner, seen):
                matched_right[right] = left
                return True
        return False

    return sum(augment(left, set()) for left in range(len(adjacency)))


def poset_width(supports: list[frozenset[str]]) -> int:
    adjacency = [
        [right for right, other in enumerate(supports) if strict_subsets(support, other)]
        for support in supports
    ]
    return len(supports) - maximum_bipartite_matching(adjacency, len(supports))


def antichains_of_size(
    supports: list[frozenset[str]], family_size: int
) -> Iterable[tuple[int, ...]]:
    """Enumerate each fixed-size antichain once, in lexicographic order."""
    incomparable = [
        {
            other
            for other, other_support in enumerate(supports)
            if support != other_support
            and not support <= other_support
            and not other_support <= support
        }
        for support in supports
    ]

    def visit(prefix: tuple[int, ...], candidates: tuple[int, ...]):
        needed = family_size - len(prefix)
        if needed == 0:
            yield prefix
            return
        if len(candidates) < needed:
            return
        for offset, chosen in enumerate(candidates):
            tail = tuple(
                candidate
                for candidate in candidates[offset + 1 :]
                if candidate in incomparable[chosen]
            )
            yield from visit(prefix + (chosen,), tail)

    yield from visit((), tuple(range(len(supports))))


def validate_cellular_interface(record: dict):
    exact_keys(
        record,
        {
            "format",
            "id",
            "scope",
            "claim",
            "external_geometry",
            "signatures",
            "cells",
            "global_signature_accounting",
        },
        "certificate",
    )
    require(record["format"] == FORMAT, "certificate: format")
    require(isinstance(record["id"], str) and record["id"], "certificate: id")
    require(record["scope"] == "ABSTRACT_FINITE_RELATIVE_2_COMPLEX", "certificate: scope")
    check_external_geometry(record["external_geometry"])

    claim = record["claim"]
    exact_keys(
        claim,
        {"family_size", "coefficient_field", "expected_all_admissible_h1_zero"},
        "claim",
    )
    require(claim["family_size"] == 8, "claim: family size")
    require(claim["coefficient_field"] == "F2", "claim: coefficient field")
    require(
        isinstance(claim["expected_all_admissible_h1_zero"], bool),
        "claim: expected verdict",
    )

    signatures = record["signatures"]
    require(
        isinstance(signatures, list)
        and signatures == sorted(signatures)
        and len(signatures) == len(set(signatures))
        and all(isinstance(signature, str) and signature for signature in signatures),
        "signatures: require sorted unique nonempty strings",
    )
    signature_set = set(signatures)

    cells = record["cells"]
    require(isinstance(cells, list) and cells, "cells: nonempty list required")
    by_id = {}
    for cell in cells:
        exact_keys(cell, {"id", "dimension", "boundary", "labels", "true_infinity"}, "cell")
        identifier = cell["id"]
        require(isinstance(identifier, str) and identifier, "cell: id")
        require(identifier not in by_id, "cells: duplicate id")
        require(cell["dimension"] in {0, 1, 2}, "cell: dimension")
        require(isinstance(cell["true_infinity"], bool), "cell: true infinity flag")
        labels = cell["labels"]
        require(
            isinstance(labels, list)
            and labels == sorted(labels)
            and len(labels) == len(set(labels))
            and set(labels) <= signature_set,
            "cell: labels",
        )
        require(isinstance(cell["boundary"], list), "cell: boundary")
        by_id[identifier] = cell

    boundary: dict[str, dict[str, int]] = {}
    for identifier, cell in by_id.items():
        entries = {}
        for entry in cell["boundary"]:
            require(
                isinstance(entry, list)
                and len(entry) == 2
                and isinstance(entry[0], str)
                and isinstance(entry[1], int)
                and not isinstance(entry[1], bool),
                "incidence: malformed entry",
            )
            face, coefficient = entry
            require(coefficient in {-1, 1}, "incidence: regular-CW coefficient must be a unit")
            require(face not in entries, "incidence: duplicate face")
            require(face in by_id, "incidence: unknown face")
            require(
                by_id[face]["dimension"] == cell["dimension"] - 1,
                "incidence: wrong face dimension",
            )
            entries[face] = coefficient
        if cell["dimension"] == 0:
            require(not entries, "incidence: zero-cell has boundary")
        elif cell["dimension"] == 1:
            require(len(entries) == 2, "incidence: regular one-cell needs two endpoints")
            require(sum(entries.values()) == 0, "incidence: oriented one-cell boundary")
        else:
            require(len(entries) >= 2, "incidence: regular two-cell needs a boundary cycle")
        boundary[identifier] = entries

    # Label monotonicity makes every family-selected set a subcomplex.
    for high, entries in boundary.items():
        for low in entries:
            require(
                set(by_id[high]["labels"]) <= set(by_id[low]["labels"]),
                "labels: selected cells are not a subcomplex",
            )

    # The true-infinity cells must themselves be a subcomplex.
    infinity = {identifier for identifier, cell in by_id.items() if cell["true_infinity"]}
    for high in infinity:
        require(set(boundary[high]) <= infinity, "true infinity: not a subcomplex")

    cells_by_dimension = {
        dimension: sorted(
            identifier
            for identifier, cell in by_id.items()
            if cell["dimension"] == dimension
        )
        for dimension in (0, 1, 2)
    }

    # Integral d^2=0 is stronger than the mod-two condition used below.
    for vertex in cells_by_dimension[0]:
        for face in cells_by_dimension[2]:
            total = sum(
                boundary[edge].get(vertex, 0) * boundary[face].get(edge, 0)
                for edge in cells_by_dimension[1]
            )
            require(total == 0, "incidence: integral d squared is nonzero")

    # Each declared 2-cell boundary is a connected simple cycle.  This is an
    # internal combinatorial check; geometric regularity remains external.
    for face in cells_by_dimension[2]:
        edges = set(boundary[face])
        vertices = {vertex for edge in edges for vertex in boundary[edge]}
        degrees = Counter(
            vertex for edge in edges for vertex in boundary[edge]
        )
        require(
            vertices and all(degrees[vertex] == 2 for vertex in vertices),
            "incidence: two-cell boundary is not a simple cycle",
        )
        pending = [next(iter(vertices))]
        reached = set()
        while pending:
            vertex = pending.pop()
            if vertex in reached:
                continue
            reached.add(vertex)
            for edge in edges:
                if vertex in boundary[edge]:
                    pending.extend(set(boundary[edge]) - {vertex})
        require(reached == vertices, "incidence: disconnected two-cell boundary")

    return claim, signatures, by_id, boundary, infinity


def semantic_accounting(
    signatures: list[str],
    by_id: dict[str, dict],
    infinity: set[str],
):
    ordinary_cells = frozenset(set(by_id) - infinity)
    support_to_signatures: dict[frozenset[str], list[str]] = {}
    for signature in signatures:
        support = frozenset(
            identifier
            for identifier, cell in by_id.items()
            if identifier not in infinity and signature in cell["labels"]
        )
        support_to_signatures.setdefault(support, []).append(signature)
    class_items = sorted(
        ((tuple(names), support) for support, names in support_to_signatures.items()),
        key=lambda item: item[0],
    )
    proper_items = [
        (names, support)
        for names, support in class_items
        if support and support != ordinary_cells
    ]
    semantic = {
        "ordinary_cells": sorted(ordinary_cells),
        "classes": [
            {
                "members": list(names),
                "support": sorted(support),
                "proper": bool(support and support != ordinary_cells),
            }
            for names, support in class_items
        ],
        "proper_dominance": [
            [left_names[0], right_names[0]]
            for left_names, left in proper_items
            for right_names, right in proper_items
            if left <= right
        ],
    }
    digest = hashlib.sha256(
        json.dumps(semantic, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()
    return ordinary_cells, class_items, proper_items, digest


def verify_global_signature_accounting(
    declared: dict,
    signatures: list[str],
    by_id: dict[str, dict],
    infinity: set[str],
):
    exact_keys(
        declared,
        {
            "domain",
            "semantic_sha256",
            "equivalence_classes",
            "properness_witnesses",
            "declared_width",
            "width_antichain",
            "antichain_separations",
            "chain_cover",
        },
        "global signature accounting",
    )
    require(
        declared["domain"] == "ENTIRE_CERTIFIED_RELATIVE_COMPLEX",
        "global signature accounting: partial domain",
    )
    require(is_sha256(declared["semantic_sha256"]), "global signature accounting: digest")
    ordinary_cells, class_items, proper_items, digest = semantic_accounting(
        signatures, by_id, infinity
    )
    require(digest == declared["semantic_sha256"], "global signature accounting: semantic digest")
    expected_classes = [list(names) for names, _support in class_items]
    require(
        declared["equivalence_classes"] == expected_classes,
        "global signature accounting: equivalence classes",
    )

    representatives = [names[0] for names, _support in proper_items]
    support_by_representative = {names[0]: support for names, support in proper_items}
    expected_properness = [
        {
            "class": names[0],
            "present": min(support),
            "absent": min(ordinary_cells - support),
        }
        for names, support in proper_items
    ]
    require(
        declared["properness_witnesses"] == expected_properness,
        "global signature accounting: properness witnesses",
    )

    supports = [support for _names, support in proper_items]
    width = poset_width(supports)
    require(declared["declared_width"] == width, "global signature accounting: width")
    antichain = declared["width_antichain"]
    require(
        isinstance(antichain, list)
        and len(antichain) == width
        and len(set(antichain)) == width
        and set(antichain) <= set(representatives),
        "global signature accounting: width antichain",
    )
    expected_separations = []
    for left, right in combinations(antichain, 2):
        left_support = support_by_representative[left]
        right_support = support_by_representative[right]
        require(
            not left_support <= right_support and not right_support <= left_support,
            "global signature accounting: comparable width witness",
        )
        expected_separations.append(
            {
                "left": left,
                "right": right,
                "left_not_right": min(left_support - right_support),
                "right_not_left": min(right_support - left_support),
            }
        )
    require(
        declared["antichain_separations"] == expected_separations,
        "global signature accounting: incomparability witnesses",
    )

    chain_cover = declared["chain_cover"]
    require(isinstance(chain_cover, list) and len(chain_cover) == width, "global signature accounting: chain cover size")
    flattened = [representative for chain in chain_cover for representative in chain]
    require(
        sorted(flattened) == sorted(representatives) and len(flattened) == len(set(flattened)),
        "global signature accounting: chain cover partition",
    )
    for chain in chain_cover:
        require(isinstance(chain, list) and chain, "global signature accounting: empty chain")
        for left, right in zip(chain, chain[1:]):
            require(
                support_by_representative[left] < support_by_representative[right],
                "global signature accounting: invalid dominance chain",
            )
    return class_items, proper_items, width


def h1_for_family(
    family: tuple[frozenset[str], ...],
    by_id: dict[str, dict],
    boundary: dict[str, dict[str, int]],
    infinity: set[str],
) -> tuple[int, tuple[int, int, int, int, int]]:
    common_support = set.intersection(*(set(support) for support in family))
    relative = common_support - infinity
    cells_by_dimension = {
        dimension: sorted(
            identifier for identifier in relative if by_id[identifier]["dimension"] == dimension
        )
        for dimension in (0, 1, 2)
    }
    d1 = boundary_rows(cells_by_dimension, boundary, 1)
    d2 = boundary_rows(cells_by_dimension, boundary, 2)
    rank_d1 = gf2_rank(d1, len(cells_by_dimension[1]))
    rank_d2 = gf2_rank(d2, len(cells_by_dimension[2]))

    # Relative subcomplex closure implies the quotient matrices still compose.
    for row in d1:
        composed = 0
        for edge_index in range(len(cells_by_dimension[1])):
            if (row >> edge_index) & 1:
                composed ^= d2[edge_index]
        require(composed == 0, "relative replay: d squared is nonzero")

    h1 = len(cells_by_dimension[1]) - rank_d1 - rank_d2
    require(h1 >= 0, "relative replay: negative H1 dimension")
    census = (
        len(cells_by_dimension[0]),
        len(cells_by_dimension[1]),
        len(cells_by_dimension[2]),
        rank_d1,
        rank_d2,
    )
    return h1, census


def verify_certificate(record: dict) -> dict:
    claim, signatures, by_id, boundary, infinity = validate_cellular_interface(record)
    class_items, proper_items, width = verify_global_signature_accounting(
        record["global_signature_accounting"], signatures, by_id, infinity
    )
    classes = [names for names, _support in proper_items]
    supports = [support for _names, support in proper_items]

    family_size = claim["family_size"]
    families = [] if width < family_size else antichains_of_size(supports, family_size)
    histogram = Counter()
    census_histogram = Counter()
    nonzero_examples = []
    count = 0
    for family_indices in families:
        count += 1
        family_supports = tuple(supports[index] for index in family_indices)
        h1, census = h1_for_family(family_supports, by_id, boundary, infinity)
        histogram[h1] += 1
        census_histogram[census + (h1,)] += 1
        if h1 and len(nonzero_examples) < 8:
            nonzero_examples.append([classes[index] for index in family_indices])

    all_zero = not histogram or set(histogram) == {0}
    require(
        all_zero == claim["expected_all_admissible_h1_zero"],
        "claim: declared all-family H1 verdict is false",
    )
    return {
        "id": record["id"],
        "signature_count": len(signatures),
        "dominance_class_count": len(class_items),
        "proper_dominance_class_count": len(classes),
        "proper_poset_width": width,
        "admissible_family_count": count,
        "h1_histogram": dict(sorted(histogram.items())),
        "chain_histogram": {
            str(key): value for key, value in sorted(census_histogram.items())
        },
        "nonzero_examples": nonzero_examples,
        "all_admissible_h1_zero": all_zero,
    }


def mutate(record: dict, mutation: dict) -> dict:
    exact_keys(mutation, {"id", "base", "operation", "expected_error"}, "hostile mutation")
    candidate = copy.deepcopy(record)
    operation = mutation["operation"]
    by_id = {cell["id"]: cell for cell in candidate["cells"]}
    if operation == "drop_disk_incidence":
        by_id["f012"]["boundary"].pop()
    elif operation == "drop_disk_two_cell":
        candidate["cells"] = [cell for cell in candidate["cells"] if cell["id"] != "f012"]
    elif operation == "erase_relative_infinity":
        for cell in candidate["cells"]:
            cell["true_infinity"] = False
    elif operation == "nonclosed_infinity":
        by_id["e01"]["true_infinity"] = True
        by_id["v1"]["true_infinity"] = False
    elif operation == "drop_face_label":
        by_id["e01"]["labels"].remove("s7")
    elif operation == "bad_geometry_digest":
        candidate["external_geometry"]["sha256"] = "0" * 64
    elif operation == "undischarged_geometry":
        candidate["external_geometry"]["obligations"]["ambient_coverage"] = "OPEN"
    elif operation == "duplicate_cell_id":
        candidate["cells"][1]["id"] = candidate["cells"][0]["id"]
    elif operation == "flip_claim":
        claim = candidate["claim"]
        claim["expected_all_admissible_h1_zero"] = not claim[
            "expected_all_admissible_h1_zero"
        ]
    elif operation == "duplicate_boundary_face":
        by_id["e01"]["boundary"].append(list(by_id["e01"]["boundary"][0]))
    elif operation == "corrupt_global_width":
        candidate["global_signature_accounting"]["declared_width"] = 7
    else:
        raise CertificateError(f"hostile mutation: unknown operation {operation!r}")
    return candidate


def assert_rejected(record: dict, label: str, expected_error: str) -> None:
    try:
        verify_certificate(record)
    except CertificateError as error:
        require(
            expected_error in str(error),
            f"hostile canary rejected at wrong gate: {label}: {error}",
        )
        return
    raise AssertionError(f"hostile canary was accepted: {label}")


def main() -> None:
    suite = json.loads(FIXTURES.read_text(encoding="utf-8"))
    exact_keys(suite, {"format", "certificates", "hostile_mutations"}, "fixture suite")
    require(suite["format"] == FIXTURE_FORMAT, "fixture suite: format")
    certificates = {}
    results = {}
    for record in suite["certificates"]:
        require(record["id"] not in certificates, "fixture suite: duplicate certificate id")
        certificates[record["id"]] = record
        results[record["id"]] = verify_certificate(record)

    for mutation in suite["hostile_mutations"]:
        exact_keys(
            mutation,
            {"id", "base", "operation", "expected_error"},
            "hostile mutation",
        )
        require(mutation["base"] in certificates, "hostile mutation: unknown base")
        assert_rejected(
            mutate(certificates[mutation["base"]], mutation),
            mutation["id"],
            mutation["expected_error"],
        )

    require(set(results) == {"contractible_disk", "unfilled_loop", "relative_boundary"}, "fixture census")
    require(results["contractible_disk"]["h1_histogram"] == {0: 1}, "disk fixture")
    require(results["unfilled_loop"]["h1_histogram"] == {1: 1}, "loop fixture")
    require(results["relative_boundary"]["h1_histogram"] == {1: 1}, "relative fixture")
    one_skeletons = {
        identifier: [cell for cell in certificates[identifier]["cells"] if cell["dimension"] <= 1]
        for identifier in ("contractible_disk", "unfilled_loop")
    }
    require(
        one_skeletons["contractible_disk"] == one_skeletons["unfilled_loop"],
        "filled/unfilled negative: one-skeletons differ",
    )
    require(
        results["contractible_disk"]["proper_poset_width"]
        == results["unfilled_loop"]["proper_poset_width"]
        == results["relative_boundary"]["proper_poset_width"]
        == 8,
        "width fixture",
    )

    print("PASS abstract finite relative 2-complex schema")
    for identifier in sorted(results):
        result = results[identifier]
        print(
            "PASS",
            identifier,
            f"width={result['proper_poset_width']}",
            f"families={result['admissible_family_count']}",
            f"H1_F2={result['h1_histogram']}",
        )
    print(f"PASS {len(suite['hostile_mutations'])}/{len(suite['hostile_mutations'])} hostile mutations rejected")
    print("NEGATIVE same labelled one-skeleton has H1_F2 0 when filled and 1 when unfilled")
    print("SCOPE abstract certificates only; external geometry obligations remain external")


if __name__ == "__main__":
    main()
