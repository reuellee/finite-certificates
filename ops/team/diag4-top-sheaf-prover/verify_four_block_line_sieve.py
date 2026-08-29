#!/usr/bin/env python3
"""Exact semantic-kernel audit for the diagonal-four 3+1 shear sieve.

The proof in ``PROOF.md`` is topological.  This verifier checks its finite
support premise on the complete cover-all support domain fixed by D4-SP:

* enumerate all cover-all three-, four-, and five-subsets of the 56 parent
  triples (exactly 1,715,980 supports);
* decide the three-common-apex-plus-one-line (``B31``) predicate;
* quotient exactly by the full S_8 action; and
* exercise positive, negative, out-of-domain, and hostile split--remerge
  canaries.

``B31`` is not inferred from unsigned counts.  The proof shows that whenever
it holds, four support-preserving column shears leave every *signed* Gordan
row and every zero-weight face unchanged, and compact-support Leray descent
kills H_c^q for q <= 3.  The enumeration only classifies where that theorem
applies.
"""

from __future__ import annotations

from collections import Counter
from hashlib import sha256
from itertools import combinations, permutations
import json
from pathlib import Path
import sys

import numpy as np


HERE = Path(__file__).resolve()
OMREAL = HERE.parents[3] / "ai" / "omreal"
sys.path.insert(0, str(OMREAL))

import prototype_koszul_circuits as koszul  # noqa: E402
import verify_seeat_shatter8 as shatter  # noqa: E402


VERTICES = tuple(range(8))
TRIPLES = tuple(combinations(VERTICES, 3))
TRIPLE_INDEX = {triple: index for index, triple in enumerate(TRIPLES)}
CERTIFICATE = OMREAL / "data" / "seeat_parent2599_shatter8.npz"

EXPECTED = {
    "full_cover_labeled": 1_715_980,
    "full_cover_orbits": 130,
    "full_b31_labeled": 915_740,
    "full_b31_orbits": 77,
    "full_survivor_labeled": 800_240,
    "full_survivor_orbits": 53,
    "generic_labeled": 2_021_992,
    "generic_cover_labeled": 1_099_560,
    "generic_cover_orbits": 66,
    "generic_b31_labeled": 339_360,
    "generic_b31_orbits": 21,
    "generic_survivor_labeled": 760_200,
    "generic_survivor_orbits": 45,
}


def encode_support(indices: tuple[int, ...]) -> int:
    return sum(1 << index for index in indices)


def decode_support(mask: int) -> tuple[int, ...]:
    return tuple(index for index in range(len(TRIPLES)) if mask & (1 << index))


def support_name(indices: tuple[int, ...]) -> str:
    return "/".join(
        "".join(str(vertex + 1) for vertex in TRIPLES[index])
        for index in indices
    )


def support_from_name(name: str) -> tuple[int, ...]:
    return tuple(sorted(
        TRIPLE_INDEX[tuple(int(character) - 1 for character in token)]
        for token in name.split("/")
    ))


def generic_cover_data(indices: tuple[int, ...]):
    """Return the degree sequence, or None off the generic cover-all domain."""
    degrees = [0] * 8
    codegrees = Counter()
    for index in indices:
        triple = TRIPLES[index]
        for vertex in triple:
            degrees[vertex] += 1
            if degrees[vertex] >= 4:
                return None
        for pair in combinations(triple, 2):
            codegrees[pair] += 1
            if codegrees[pair] >= 3:
                return None
    if not min(degrees):
        return None
    return tuple(degrees)


def b31_witness(indices: tuple[int, ...]):
    """Return a canonical 3+1 domination witness, if one exists.

    The output is ``(block, f, g, h)``.  The three labels in ``block`` are
    dominated by the fixed common apex ``f``; the fourth moving label ``g``
    is dominated by the fixed apex ``h``.  Both apices lie outside all four
    moving labels, and the two apices are distinct.
    """
    occurrence = [0] * 8
    for position, index in enumerate(indices):
        for vertex in TRIPLES[index]:
            occurrence[vertex] |= 1 << position

    # In the cover-all domain every occurrence mask is nonzero.  Retain the
    # generic definition for canaries outside that domain: a genuinely
    # omitted label is not treated as dominated by every apex.
    dominated = {
        (moving, apex)
        for moving in VERTICES
        for apex in VERTICES
        if moving != apex
        and occurrence[moving]
        and not (occurrence[moving] & ~occurrence[apex])
    }
    for common_apex in VERTICES:
        candidates = tuple(
            moving
            for moving in VERTICES
            if (moving, common_apex) in dominated
        )
        for block in combinations(candidates, 3):
            if common_apex in block:
                continue
            for line_label in VERTICES:
                if line_label == common_apex or line_label in block:
                    continue
                for line_apex in VERTICES:
                    if (
                        line_apex == line_label
                        or line_apex == common_apex
                        or line_apex in block
                    ):
                        continue
                    if (line_label, line_apex) in dominated:
                        return block, common_apex, line_label, line_apex
    return None


def classify(indices: tuple[int, ...]) -> str:
    if len(indices) not in (3, 4, 5):
        return "OUT_OF_DOMAIN"
    covered = set().union(*(set(TRIPLES[index]) for index in indices))
    if covered != set(VERTICES):
        return "OUT_OF_DOMAIN"
    if b31_witness(indices) is not None:
        return "CERTIFIED_B31"
    return "SURVIVES"


def relabel_map(permutation: tuple[int, ...]) -> tuple[int, ...]:
    return tuple(
        TRIPLE_INDEX[
            tuple(sorted(permutation[vertex] for vertex in triple))
        ]
        for triple in TRIPLES
    )


def relabeled_mask(indices: tuple[int, ...], mapping: tuple[int, ...]) -> int:
    return sum(1 << mapping[index] for index in indices)


def rank_over_q(matrix: list[list[int]]) -> int:
    """Tiny exact rational rank by fraction-free elimination."""
    rows = [row[:] for row in matrix]
    if not rows:
        return 0
    rank = 0
    columns = len(rows[0])
    for column in range(columns):
        pivot = next(
            (row for row in range(rank, len(rows)) if rows[row][column]),
            None,
        )
        if pivot is None:
            continue
        rows[rank], rows[pivot] = rows[pivot], rows[rank]
        pivot_value = rows[rank][column]
        for row in range(len(rows)):
            if row == rank or not rows[row][column]:
                continue
            factor = rows[row][column]
            rows[row] = [
                pivot_value * left - factor * right
                for left, right in zip(rows[row], rows[rank], strict=True)
            ]
        rank += 1
        if rank == len(rows):
            break
    return rank


def signed_row_canary():
    """Check actual signed OM occurrences on both sides of the sieve."""
    selected = (0, 4, 3, 5)
    q0 = support_from_name("123/134/267/258/468")
    q7 = support_from_name("123/124/235/147/368")
    with np.load(CERTIFICATE, allow_pickle=False) as stored:
        signatures = tuple(int(value) for value in stored["signature"])
        base_parent, normals = shatter.parent_signs_and_rows(
            stored["pattern_chart"][0]
        )
        if len(base_parent) != 70 or not set(base_parent) <= {"+", "-"}:
            raise AssertionError("row-2599 canary parent is not uniform")
        for signature_index, expected_support in ((0, q0), (7, q7)):
            weights = tuple(
                int(value)
                for value in stored["gordan_weight"][0, signature_index]
            )
            active = tuple(index for index, value in enumerate(weights) if value)
            active_lex = tuple(sorted(
                TRIPLE_INDEX[tuple(vertex - 1 for vertex in koszul.TRIPLES[index])]
                for index in active
            ))
            if active_lex != expected_support or any(
                weights[index] <= 0 for index in active
            ):
                raise AssertionError("wrong strict support in signed canary")
            rows = [
                tuple(
                    value
                    if (signatures[signature_index] >> index) & 1
                    else -value
                    for value in normal
                )
                for index, normal in enumerate(normals)
            ]
            for coordinate in range(4):
                if sum(
                    weights[index] * rows[index][coordinate]
                    for index in active
                ):
                    raise AssertionError("signed weights do not annihilate the rows")
            if koszul.matrix_rank([rows[index] for index in active]) != len(active) - 1:
                raise AssertionError("signed circuit is not support-minimal")

        # The stored shatter patterns prove properness and incomparability of
        # the four-signature family: all sixteen good/bad patterns occur.
        for local_pattern in range(16):
            global_pattern = sum(
                ((local_pattern >> bit) & 1) << signature_index
                for bit, signature_index in enumerate(selected)
            )
            parent, chart_normals = shatter.parent_signs_and_rows(
                stored["pattern_chart"][global_pattern]
            )
            if parent != base_parent:
                raise AssertionError("shatter canary changed parent chirotope")
            for bit, signature_index in enumerate(selected):
                signed = [
                    tuple(
                        value
                        if (signatures[signature_index] >> index) & 1
                        else -value
                        for value in normal
                    )
                    for index, normal in enumerate(chart_normals)
                ]
                if (local_pattern >> bit) & 1:
                    shatter.verify_feasible(
                        signed,
                        stored["feasible_point"][global_pattern, signature_index],
                    )
                else:
                    shatter.verify_infeasible(
                        signed,
                        stored["gordan_weight"][global_pattern, signature_index],
                    )
    if classify(q0) != "SURVIVES":
        raise AssertionError("actual signed Q0 survivor was accidentally removed")
    if classify(q7) != "CERTIFIED_B31":
        raise AssertionError("actual signed B31 support was not certified")


def canaries():
    positive = support_from_name("123/124/235/147/368")
    negative = support_from_name("123/134/267/258/468")
    null = support_from_name("123/124/125/126/127")
    if classify(positive) != "CERTIFIED_B31":
        raise AssertionError("positive B31 canary was rejected")
    if b31_witness(positive) != ((4, 5, 7), 2, 3, 0):
        raise AssertionError("positive B31 witness changed")
    if classify(negative) != "SURVIVES":
        raise AssertionError("negative survivor canary was removed")
    if classify(null) != "OUT_OF_DOMAIN":
        raise AssertionError("out-of-domain null canary was promoted")

    # Hostile abstract split--remerge core: two parallel compact edges from a
    # split vertex to a merge vertex.  Each branch can be extended by a ray,
    # but the anti-diagonal 1-chain is a nonzero cycle.  This is the finite
    # semantic kernel of the doubled-interval warning; it is intentionally
    # not claimed to be an oriented-matroid occurrence.
    boundary = [[-1, -1], [1, 1]]
    if rank_over_q(boundary) != 1:
        raise AssertionError("hostile Reeb boundary rank changed")
    anti_diagonal = (1, -1)
    if any(
        sum(row[column] * anti_diagonal[column] for column in range(2))
        for row in boundary
    ):
        raise AssertionError("hostile anti-diagonal is not a cycle")
    if 2 - rank_over_q(boundary) != 1:
        raise AssertionError("hostile split--remerge H1 is not one-dimensional")

    # Hostile separate-convexity core: a square cycle.  It records the H1
    # class in the deformation retract of {(x,y): x.y > 0} for two-dimensional
    # blocks.  B31 is stronger: it supplies convex three-sections over a
    # one-dimensional base, so this two-plus-two kernel is out of scope.
    square_boundary = [
        [-1, 0, 0, 1],
        [1, -1, 0, 0],
        [0, 1, -1, 0],
        [0, 0, 1, -1],
    ]
    if rank_over_q(square_boundary) != 3:
        raise AssertionError("hostile separate-convexity boundary rank changed")
    if 4 - rank_over_q(square_boundary) != 1:
        raise AssertionError("hostile separate-convexity H1 is not one-dimensional")
    signed_row_canary()
    print("PASS canaries: positive / negative / null / hostile_split_remerge / hostile_separate_convexity")
    print("PASS signed canaries: exact row-2599 B31 and survivor occurrences")


def full_classification():
    generic_count = 0
    cover_masks = set()
    full_labeled_by_size = Counter()
    full_b31_by_size = Counter()
    generic_cover_by_degree = Counter()
    generic_b31_by_degree = Counter()

    for size in (3, 4, 5):
        for indices in combinations(range(len(TRIPLES)), size):
            degrees = [0] * 8
            codegrees = Counter()
            generic = size == 5
            for index in indices:
                triple = TRIPLES[index]
                for vertex in triple:
                    degrees[vertex] += 1
                    if degrees[vertex] >= 4:
                        generic = False
                if size == 5:
                    for pair in combinations(triple, 2):
                        codegrees[pair] += 1
                        if codegrees[pair] >= 3:
                            generic = False
            if size == 5 and generic:
                generic_count += 1
            if not min(degrees):
                continue
            cover_masks.add(encode_support(indices))
            full_labeled_by_size[size] += 1
            witness = b31_witness(indices)
            if witness is not None:
                full_b31_by_size[size] += 1
            if size == 5 and generic:
                degree_sequence = tuple(sorted(degrees))
                generic_cover_by_degree[degree_sequence] += 1
                if witness is not None:
                    generic_b31_by_degree[degree_sequence] += 1

    mappings = tuple(relabel_map(permutation) for permutation in permutations(VERTICES))
    records = []
    full_orbits_by_size = Counter()
    full_b31_orbits_by_size = Counter()
    generic_orbits_by_degree = Counter()
    generic_b31_orbits_by_degree = Counter()
    while cover_masks:
        representative_mask = min(cover_masks)
        representative = decode_support(representative_mask)
        orbit = {
            relabeled_mask(representative, mapping)
            for mapping in mappings
        }
        cover_masks.difference_update(orbit)
        degrees = tuple(
            sum(vertex in TRIPLES[index] for index in representative)
            for vertex in VERTICES
        )
        degree_sequence = tuple(sorted(degrees))
        witness = b31_witness(representative)
        status = "CERTIFIED_B31" if witness is not None else "SURVIVES"
        size = len(representative)
        full_orbits_by_size[size] += 1
        if witness is not None:
            full_b31_orbits_by_size[size] += 1
        generic = size == 5 and generic_cover_data(representative) is not None
        if generic:
            generic_orbits_by_degree[degree_sequence] += 1
            if witness is not None:
                generic_b31_orbits_by_degree[degree_sequence] += 1
        records.append(
            {
                "support": support_name(representative),
                "size": size,
                "degree_sequence": "".join(map(str, degree_sequence)),
                "generic": generic,
                "orbit_size": len(orbit),
                "status": status,
                "witness": None
                if witness is None
                else {
                    "block": [value + 1 for value in witness[0]],
                    "common_apex": witness[1] + 1,
                    "line_label": witness[2] + 1,
                    "line_apex": witness[3] + 1,
                },
            }
        )

    certified = [record for record in records if record["status"] == "CERTIFIED_B31"]
    survivors = [record for record in records if record["status"] == "SURVIVES"]
    generic_records = [record for record in records if record["generic"]]
    generic_certified = [
        record for record in generic_records if record["status"] == "CERTIFIED_B31"
    ]
    generic_survivors = [
        record for record in generic_records if record["status"] == "SURVIVES"
    ]
    full_cover_labeled = sum(full_labeled_by_size.values())
    full_b31_labeled = sum(full_b31_by_size.values())
    generic_cover_labeled = sum(generic_cover_by_degree.values())
    generic_b31_labeled = sum(generic_b31_by_degree.values())
    if sum(record["orbit_size"] for record in records) != full_cover_labeled:
        raise AssertionError("full S8 orbit sizes do not sum to the labeled domain")
    if sum(record["orbit_size"] for record in certified) != full_b31_labeled:
        raise AssertionError("B31 S8 orbit sizes do not sum to the labeled domain")
    summary = {
        "full_cover_labeled": full_cover_labeled,
        "full_cover_orbits": len(records),
        "full_b31_labeled": full_b31_labeled,
        "full_b31_orbits": len(certified),
        "full_survivor_labeled": full_cover_labeled - full_b31_labeled,
        "full_survivor_orbits": len(survivors),
        "generic_labeled": generic_count,
        "generic_cover_labeled": generic_cover_labeled,
        "generic_cover_orbits": len(generic_records),
        "generic_b31_labeled": generic_b31_labeled,
        "generic_b31_orbits": len(generic_certified),
        "generic_survivor_labeled": generic_cover_labeled - generic_b31_labeled,
        "generic_survivor_orbits": len(generic_survivors),
    }
    if summary != EXPECTED:
        raise AssertionError(f"classification counts changed: {summary}")

    expected_labeled_degrees = {
        (1, 1, 1, 1, 2, 3, 3, 3): 144_480,
        (1, 1, 1, 2, 2, 2, 3, 3): 582_960,
        (1, 1, 2, 2, 2, 2, 2, 3): 341_880,
        (1, 2, 2, 2, 2, 2, 2, 2): 30_240,
    }
    expected_orbit_degrees = {
        (1, 1, 1, 1, 2, 3, 3, 3): 10,
        (1, 1, 1, 2, 2, 2, 3, 3): 30,
        (1, 1, 2, 2, 2, 2, 2, 3): 22,
        (1, 2, 2, 2, 2, 2, 2, 2): 4,
    }
    if dict(generic_cover_by_degree) != expected_labeled_degrees:
        raise AssertionError("cover-all labeled degree census changed")
    if dict(generic_orbits_by_degree) != expected_orbit_degrees:
        raise AssertionError("cover-all orbit degree census changed")

    semantic = json.dumps(records, sort_keys=True, separators=(",", ":")).encode()
    digest = sha256(semantic).hexdigest()
    print("PASS complete D4-SP cover-all size-3/4/5 support classification")
    for key, value in summary.items():
        print(f"{key.upper()}={value}")
    print("FULL_LABELED_BY_SIZE=" + json.dumps(dict(full_labeled_by_size), sort_keys=True))
    print("FULL_B31_BY_SIZE=" + json.dumps(dict(full_b31_by_size), sort_keys=True))
    print("FULL_ORBITS_BY_SIZE=" + json.dumps(dict(full_orbits_by_size), sort_keys=True))
    print("FULL_B31_ORBITS_BY_SIZE=" + json.dumps(dict(full_b31_orbits_by_size), sort_keys=True))
    print("GENERIC_B31_LABELED_BY_DEGREE=" + json.dumps({
        "".join(map(str, key)): generic_b31_by_degree[key]
        for key in sorted(generic_b31_by_degree)
    }, sort_keys=True))
    print("GENERIC_B31_ORBITS_BY_DEGREE=" + json.dumps({
        "".join(map(str, key)): generic_b31_orbits_by_degree[key]
        for key in sorted(generic_b31_orbits_by_degree)
    }, sort_keys=True))
    print("SURVIVOR_SUPPORTS=" + ",".join(record["support"] for record in survivors))
    print(f"SEMANTIC_SHA256={digest}")
    return digest


def main():
    canaries()
    full_classification()
    print("THEOREM_HANDOFF: B31 kills H_c^q through q=3 on 77/130 full-domain orbits")
    print("NONCONSEQUENCE: D4-SP remains open on 53 orbits; restriction maps remain open")


if __name__ == "__main__":
    main()
