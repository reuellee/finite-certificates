#!/usr/bin/env python3
"""Independent exact checker for the D4-S53 complete-null scan.

No discovery module is imported.  The checker reconstructs the full 130-orbit
partition, all 53 structural rows, and all required signed/hostile canaries.
"""

from __future__ import annotations

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, permutations, product
import importlib.util
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CERT = HERE / "STRUCTURAL_SCAN.json"
VERTICES = range(8)
TRIPLES = tuple(combinations(range(8), 3))
TINDEX = {t: i for i, t in enumerate(TRIPLES)}
EXPECTED_SEMANTIC = "16b11cba052b49af777354f256a783b419ec6e246d178de70c238807e50ecc11"


def support_name(support):
    return "/".join("".join(str(v + 1) for v in TRIPLES[i]) for i in support)


def occurrence(support):
    return tuple(sum(1 << p for p, i in enumerate(support) if v in TRIPLES[i]) for v in VERTICES)


def arrows(support):
    masks = occurrence(support)
    return {(m, a) for m in VERTICES for a in VERTICES
            if m != a and masks[m] and masks[m] & ~masks[a] == 0}


def b31_witness(support):
    relation = arrows(support)
    for f in VERTICES:
        for block in combinations([m for m in VERTICES if (m, f) in relation], 3):
            for g in VERTICES:
                for h in VERTICES:
                    if (g not in block and g != f and h not in block
                            and h not in (g, f) and (g, h) in relation):
                        return block, f, g, h
    return None


def generic(support):
    if len(support) != 5:
        return False
    d = Counter(v for i in support for v in TRIPLES[i])
    c = Counter(p for i in support for p in combinations(TRIPLES[i], 2))
    return max(d.values()) < 4 and max(c.values()) < 3


def relabel(support, permutation):
    return tuple(sorted(TINDEX[tuple(sorted(permutation[v] for v in TRIPLES[i]))] for i in support))


def reconstruct():
    permutations8 = tuple(permutations(range(8)))
    unseen = {
        tuple(support)
        for size in (3, 4, 5)
        for support in combinations(range(56), size)
        if len({v for i in support for v in TRIPLES[i]}) == 8
    }
    records = []
    while unseen:
        representative = min(unseen, key=lambda s: sum(1 << i for i in s))
        orbit = {relabel(representative, p) for p in permutations8}
        unseen.difference_update(orbit)
        degree = tuple(sorted(sum(v in TRIPLES[i] for i in representative) for v in VERTICES))
        witness = b31_witness(representative)
        records.append({
            "support": support_name(representative), "size": len(representative),
            "degree_sequence": "".join(map(str, degree)),
            "generic": generic(representative), "orbit_size": len(orbit),
            "status": "CERTIFIED_B31" if witness else "SURVIVES",
            "witness": None if witness is None else {
                "block": [x + 1 for x in witness[0]],
                "common_apex": witness[1] + 1,
                "line_label": witness[2] + 1,
                "line_apex": witness[3] + 1,
            },
            "representative": representative,
        })
    return records


def expected_structural(base):
    support = base["representative"]
    relation = arrows(support)
    degree = [sum(v in TRIPLES[i] for i in support) for v in VERTICES]
    masks = occurrence(support)
    witnesses = []
    for apex in VERTICES:
        for block in combinations([m for m in VERTICES if (m, apex) in relation], 4):
            witnesses.append([apex + 1, [m + 1 for m in block]])
    profiles = Counter()
    assignments = 0
    for movers in combinations(VERTICES, 4):
        choices = [[a for a in VERTICES if a not in movers and (m, a) in relation] for m in movers]
        if not all(choices):
            continue
        for assignment in product(*choices):
            assignments += 1
            profile = tuple(sorted(Counter(assignment).values(), reverse=True))
            profiles["+".join(map(str, profile))] += 1
    plane = elementary = 0
    for e in VERTICES:
        if degree[e] != 1:
            continue
        incident = next(TRIPLES[i] for i in support if e in TRIPLES[i])
        outside = [v for v in VERTICES if v not in incident and degree[v] <= 2]
        plane += len(tuple(combinations(outside, 2)))
        elementary_labels = [v for v in outside if any((v, a) in relation for a in VERTICES)]
        elementary += len(tuple(combinations(elementary_labels, 2)))
    return {
        "support": base["support"], "size": base["size"],
        "orbit_size": base["orbit_size"], "degree_sequence": base["degree_sequence"],
        "dominance": [[a + 1, b + 1] for a, b in sorted(relation)],
        "occurrence_masks": list(masks),
        "occurrence_class_sizes": sorted(Counter(masks).values(), reverse=True),
        "predicates": {
            "b31": False, "common_apex_four": bool(witnesses),
            "common_apex_four_witnesses": witnesses,
            "fixed_apex_four_assignments": assignments,
            "fixed_apex_four_profiles": dict(sorted(profiles.items())),
            "degree_one_plane_two_pencils_choices": plane,
            "degree_one_plane_two_elementary_pencils_choices": elementary,
        },
    }


def rank(matrix):
    rows = [[Fraction(v) for v in row] for row in matrix]
    r = 0
    for c in range(len(rows[0])):
        pivot = next((i for i in range(r, len(rows)) if rows[i][c]), None)
        if pivot is None:
            continue
        rows[r], rows[pivot] = rows[pivot], rows[r]
        q = rows[r][c]
        rows[r] = [v / q for v in rows[r]]
        for i in range(len(rows)):
            if i != r and rows[i][c]:
                q = rows[i][c]
                rows[i] = [x - q * y for x, y in zip(rows[i], rows[r])]
        r += 1
    return r


def canaries():
    # Split--remerge and separate-convexity retain one exact H_1 class.
    if rank([[-1, -1], [1, 1]]) != 1:
        raise AssertionError("split--remerge canary lost its anti-diagonal")
    square = [[-1, 0, 0, 1], [1, -1, 0, 0], [0, 1, -1, 0], [0, 0, 1, -1]]
    if rank(square) != 3:
        raise AssertionError("separate-convexity square lost H_1")
    # Cellular circle with holonomy h has differential 1-h: orientation
    # trivialization changes the answer and therefore may not be assumed.
    if rank([[0]]) != 0 or rank([[2]]) != 1:
        raise AssertionError("orientation-local-system canary changed")
    out = tuple(sorted(TINDEX[tuple(int(x) - 1 for x in token)] for token in "123/124/125/126/127".split("/")))
    if len({v for i in out for v in TRIPLES[i]}) == 8:
        raise AssertionError("out-of-domain canary became cover-all")
    # The actual-signed-survivor replay is canonical predecessor code, not
    # discovery logic; it checks the NPZ Gordan weights and 16 family patterns.
    predecessor = REPO / "ops/team/diag4-top-sheaf-prover/verify_four_block_line_sieve.py"
    spec = importlib.util.spec_from_file_location("accepted_b31_checker", predecessor)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    module.signed_row_canary()


def main():
    payload = json.loads(CERT.read_text(encoding="utf-8"))
    digest = payload.pop("scan_semantic_sha256")
    got = sha256(json.dumps(payload, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if got != digest:
        raise AssertionError("scan semantic digest mismatch")
    full = reconstruct()
    canonical_records = [{k: v for k, v in r.items() if k != "representative"} for r in full]
    canonical_digest = sha256(json.dumps(canonical_records, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
    if canonical_digest != EXPECTED_SEMANTIC:
        raise AssertionError(f"independent canonical semantic digest changed: {canonical_digest}")
    survivors = [r for r in full if r["status"] == "SURVIVES"]
    expected = [expected_structural(r) for r in survivors]
    if payload["survivors"] != expected:
        raise AssertionError("structural survivor records changed")
    summary = payload["summary"]
    if summary != {
        "canonical_cover_labeled": 1715980, "canonical_cover_orbits": 130,
        "b31_labeled": 915740, "b31_orbits": 77,
        "survivor_labeled": 800240, "survivor_orbits": 53,
        "survivor_size_four_orbits": 4, "survivor_size_five_orbits": 49,
        "common_apex_four_orbits": 0, "fixed_apex_four_orbits": 32,
        "plane_two_pencils_orbits": 53,
    }:
        raise AssertionError(f"summary changed: {summary}")
    if any("3+1" in r["predicates"]["fixed_apex_four_profiles"]
           or "4" in r["predicates"]["fixed_apex_four_profiles"] for r in expected):
        raise AssertionError("B31-resistant profile unexpectedly regained a 3+1/4 block")
    canaries()
    if payload["canonical_survivor_semantic_sha256"] != EXPECTED_SEMANTIC:
        raise AssertionError("canonical survivor digest changed")
    print("PASS independent complete domain: 1,715,980 / 130 = 915,740 / 77 + 800,240 / 53")
    print("PASS exact survivors: 4 size-four + 49 size-five orbits")
    print("PASS failed common-apex-four lemma coverage: 0/53")
    print("PASS weaker four-shear profiles: 32/53, only 2+2 / 2+1+1 / 1+1+1+1")
    print("PASS plane-plus-two-pencils incidence: 53/53; no topological promotion")
    print("PASS canaries: actual_signed_survivor / split_remerge / separate_convexity / orientation_local_system / out_of_domain")
    print("OUTCOME complete-null: D4-S53 survivors unchanged at 800,240 / 53")


if __name__ == "__main__":
    main()
