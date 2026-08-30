#!/usr/bin/env python3
"""Discovery generator for the complete canonical D4-S53 structural scan.

This is deliberately not an acceptance checker. It reconstructs the accepted
cover-all support universe and writes candidate structural records. The
independent ``verify_structural_scan.py`` checker reconstructs every record.
"""

from __future__ import annotations

import argparse
from collections import Counter
from hashlib import sha256
from itertools import combinations, permutations, product
import json
from pathlib import Path

VERTICES = tuple(range(8))
TRIPLES = tuple(combinations(VERTICES, 3))
TRIPLE_INDEX = {triple: index for index, triple in enumerate(TRIPLES)}
EXPECTED_SEMANTIC = "16b11cba052b49af777354f256a783b419ec6e246d178de70c238807e50ecc11"


def encode(indices):
    return sum(1 << index for index in indices)


def decode(mask):
    return tuple(index for index in range(56) if mask & (1 << index))


def name(indices):
    return "/".join("".join(str(v + 1) for v in TRIPLES[i]) for i in indices)


def relabel_maps():
    return tuple(
        tuple(TRIPLE_INDEX[tuple(sorted(p[v] for v in triple))] for triple in TRIPLES)
        for p in permutations(VERTICES)
    )


def dominance(indices):
    occurrence = [0] * 8
    for position, index in enumerate(indices):
        for vertex in TRIPLES[index]:
            occurrence[vertex] |= 1 << position
    return tuple(
        (moving, apex)
        for moving in VERTICES
        for apex in VERTICES
        if moving != apex and occurrence[moving]
        and not occurrence[moving] & ~occurrence[apex]
    )


def b31_witness(indices):
    arrows = set(dominance(indices))
    for apex in VERTICES:
        block = tuple(m for m in VERTICES if (m, apex) in arrows)
        for movers in combinations(block, 3):
            for moving in VERTICES:
                if moving in movers or moving == apex:
                    continue
                for other_apex in VERTICES:
                    if (other_apex not in movers
                            and other_apex not in (moving, apex)
                            and (moving, other_apex) in arrows):
                        return movers, apex, moving, other_apex
    return None


def generic(indices):
    if len(indices) != 5:
        return False
    degrees = Counter(v for i in indices for v in TRIPLES[i])
    codegrees = Counter(pair for i in indices for pair in combinations(TRIPLES[i], 2))
    return max(degrees.values()) < 4 and max(codegrees.values()) < 3


def enumerate_orbits():
    cover = set()
    for size in (3, 4, 5):
        for indices in combinations(range(56), size):
            if len({v for i in indices for v in TRIPLES[i]}) == 8:
                cover.add(encode(indices))
    maps = relabel_maps()
    records = []
    while cover:
        representative = decode(min(cover))
        orbit = {sum(1 << mapping[i] for i in representative) for mapping in maps}
        cover.difference_update(orbit)
        degrees = tuple(sorted(sum(v in TRIPLES[i] for i in representative) for v in VERTICES))
        witness = b31_witness(representative)
        records.append({
            "support": name(representative), "size": len(representative),
            "degree_sequence": "".join(map(str, degrees)),
            "generic": generic(representative), "orbit_size": len(orbit),
            "status": "CERTIFIED_B31" if witness else "SURVIVES",
            "witness": None if witness is None else {
                "block": [x + 1 for x in witness[0]],
                "common_apex": witness[1] + 1,
                "line_label": witness[2] + 1,
                "line_apex": witness[3] + 1,
            },
            "indices": representative,
        })
    semantic_records = [{k: v for k, v in r.items() if k != "indices"} for r in records]
    digest = sha256(json.dumps(semantic_records, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if digest != EXPECTED_SEMANTIC:
        raise AssertionError(f"canonical semantic digest changed: {digest}")
    return records


def structural_record(base):
    indices = tuple(base["indices"])
    arrows = set(dominance(indices))
    degree = [sum(v in TRIPLES[i] for i in indices) for v in VERTICES]
    masks = [sum(1 << p for p, i in enumerate(indices) if v in TRIPLES[i]) for v in VERTICES]
    common_apex_four = []
    for apex in VERTICES:
        movers = tuple(m for m in VERTICES if (m, apex) in arrows)
        for block in combinations(movers, 4):
            common_apex_four.append([apex + 1, [m + 1 for m in block]])
    profiles = Counter()
    fixed_apex_assignments = 0
    for movers in combinations(VERTICES, 4):
        choices = tuple(tuple(a for a in VERTICES if a not in movers and (m, a) in arrows) for m in movers)
        if not all(choices):
            continue
        for assignment in product(*choices):
            fixed_apex_assignments += 1
            profile = tuple(sorted(Counter(assignment).values(), reverse=True))
            profiles["+".join(map(str, profile))] += 1
    plane_pencil_choices = 0
    plane_elementary_choices = 0
    for e in VERTICES:
        if degree[e] != 1:
            continue
        incident = next(TRIPLES[i] for i in indices if e in TRIPLES[i])
        outside = tuple(v for v in VERTICES if v not in incident and degree[v] <= 2)
        plane_pencil_choices += len(tuple(combinations(outside, 2)))
        elementary = tuple(v for v in outside if any((v, a) in arrows for a in VERTICES))
        plane_elementary_choices += len(tuple(combinations(elementary, 2)))
    return {
        "support": base["support"], "size": base["size"],
        "orbit_size": base["orbit_size"], "degree_sequence": base["degree_sequence"],
        "dominance": [[a + 1, b + 1] for a, b in sorted(arrows)],
        "occurrence_masks": masks,
        "occurrence_class_sizes": sorted(Counter(masks).values(), reverse=True),
        "predicates": {
            "b31": False,
            "common_apex_four": bool(common_apex_four),
            "common_apex_four_witnesses": common_apex_four,
            "fixed_apex_four_assignments": fixed_apex_assignments,
            "fixed_apex_four_profiles": dict(sorted(profiles.items())),
            "degree_one_plane_two_pencils_choices": plane_pencil_choices,
            "degree_one_plane_two_elementary_pencils_choices": plane_elementary_choices,
        },
    }


def build_payload():
    full = enumerate_orbits()
    survivors = [structural_record(r) for r in full if r["status"] == "SURVIVES"]
    summary = {
        "canonical_cover_labeled": sum(r["orbit_size"] for r in full),
        "canonical_cover_orbits": len(full),
        "b31_labeled": sum(r["orbit_size"] for r in full if r["status"] == "CERTIFIED_B31"),
        "b31_orbits": sum(r["status"] == "CERTIFIED_B31" for r in full),
        "survivor_labeled": sum(r["orbit_size"] for r in survivors),
        "survivor_orbits": len(survivors),
        "survivor_size_four_orbits": sum(r["size"] == 4 for r in survivors),
        "survivor_size_five_orbits": sum(r["size"] == 5 for r in survivors),
        "common_apex_four_orbits": sum(r["predicates"]["common_apex_four"] for r in survivors),
        "fixed_apex_four_orbits": sum(r["predicates"]["fixed_apex_four_assignments"] > 0 for r in survivors),
        "plane_two_pencils_orbits": sum(r["predicates"]["degree_one_plane_two_pencils_choices"] > 0 for r in survivors),
    }
    payload = {
        "schema": "diag4-s53-structural-null-v1",
        "canonical_base": "aa784af939b55d3503e4782a9d65a9b06cf81ce0",
        "canonical_survivor_semantic_sha256": EXPECTED_SEMANTIC,
        "tested_predicates": {
            "common_apex_four": "four distinct moving labels dominated by one fixed apex; signed four-parameter jointly affine convex shear block",
            "fixed_apex_four": "four distinct movers each dominated by a nonmoving fixed apex; signed-normal invariant, but profiles below 3+1 have no vanishing theorem",
            "degree_one_plane_two_pencils": "degree-one label gives a two-parameter support-plane motion and two external degree-at-most-two labels give pencils; four parameters but only separate convexity",
            "degree_one_plane_two_elementary_pencils": "the preceding two pencils can both be parent-column domination shears",
        },
        "summary": summary, "survivors": survivors,
    }
    semantic = json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()
    payload["scan_semantic_sha256"] = sha256(semantic).hexdigest()
    return payload


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    text = json.dumps(build_payload(), indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    else:
        print(text, end="")


if __name__ == "__main__":
    main()
