"""Deterministic incidence construction and exhaustive sigma enumeration.

This is intentionally independent of facet_lp.build's randomized chamber
sampling.  A sign vector is a chamber iff the strict homogeneous system

    diag(eps) U x > 0

is feasible.  Homogeneity lets us replace >0 by >=1 and test feasibility by
linear programming.  The side incidence then follows the convention in
facet_lp.build.
"""
from __future__ import annotations

import argparse
import itertools
import json
from pathlib import Path

import networkx as nx
import numpy as np
from scipy.optimize import linprog


TRIPLES = tuple(itertools.combinations(range(5), 3))
PAIRS = tuple(itertools.combinations(range(5), 2))


def unit_rows(u: np.ndarray) -> np.ndarray:
    u = np.asarray(u, dtype=float)
    norms = np.linalg.norm(u, axis=1)
    if u.shape != (5, 3) or np.min(norms) < 1e-14:
        raise ValueError("U must have shape (5,3) with nonzero rows")
    return u / norms[:, None]


def genericity(u: np.ndarray) -> dict:
    u = unit_rows(u)
    dets = np.array([np.linalg.det(u[list(t)]) for t in TRIPLES])
    pair_sines = np.array(
        [np.linalg.norm(np.cross(u[i], u[j])) for i, j in PAIRS]
    )
    return {
        "min_abs_triple_det": float(np.min(np.abs(dets))),
        "min_pair_sine": float(np.min(pair_sines)),
        "triple_det_signs": np.sign(dets).astype(int).tolist(),
    }


def deterministic_build(u: np.ndarray) -> tuple[list[dict], list[list[int]], list[list[int]]]:
    """Return classes, chamber sign vectors, and chamber->side incidence."""
    u = unit_rows(u)
    if genericity(u)["min_abs_triple_det"] < 1e-10:
        raise ValueError("nongeneric directions: a triple determinant is tiny")

    classes: list[dict] = []
    for ci, (i, j) in enumerate(PAIRS):
        r = np.cross(u[i], u[j])
        r /= np.linalg.norm(r)
        classes.append({"class": ci, "pair": [i, j], "r": r.tolist()})

    chambers: list[list[int]] = []
    for eps_tuple in itertools.product((-1, 1), repeat=5):
        eps = np.asarray(eps_tuple, dtype=float)
        # Homogeneous strict feasibility <=> feasibility at an arbitrary
        # positive common margin, here 1.
        res = linprog(
            np.zeros(3),
            A_ub=-(eps[:, None] * u),
            b_ub=-np.ones(5),
            bounds=[(None, None)] * 3,
            method="highs",
        )
        if res.status == 0:
            chambers.append(list(map(int, eps_tuple)))

    ch_rays: list[list[int]] = []
    for eps_list in chambers:
        eps = np.asarray(eps_list)
        sides: list[int] = []
        for ci, item in enumerate(classes):
            i, j = item["pair"]
            r = np.asarray(item["r"])
            d = eps * (u @ r)
            mask = np.ones(5, dtype=bool)
            mask[[i, j]] = False
            if np.all(d[mask] > 1e-9):
                sides.append(2 * ci)
            elif np.all(d[mask] < -1e-9):
                sides.append(2 * ci + 1)
        if len(sides) < 3:
            raise RuntimeError(f"bad chamber incidence: {eps_list} -> {sides}")
        ch_rays.append(sides)
    return classes, chambers, ch_rays


def incidence_graph(ch_rays: list[list[int]], include_side_pairing: bool = True) -> nx.Graph:
    """Colored graph encoding incidence and, optionally, antipodal pairing."""
    graph = nx.Graph()
    for side in range(20):
        graph.add_node(f"s{side}", kind="side")
    for chamber, sides in enumerate(ch_rays):
        cn = f"c{chamber}"
        graph.add_node(cn, kind=f"chamber_degree_{len(sides)}")
        graph.add_edges_from((cn, f"s{s}") for s in sides)
    if include_side_pairing:
        for ci in range(10):
            pn = f"p{ci}"
            graph.add_node(pn, kind="antipodal_pair")
            graph.add_edge(pn, f"s{2 * ci}")
            graph.add_edge(pn, f"s{2 * ci + 1}")
    return graph


def graph_isomorphism(
    ch_a: list[list[int]], ch_b: list[list[int]], include_side_pairing: bool = True
) -> dict | None:
    ga = incidence_graph(ch_a, include_side_pairing)
    gb = incidence_graph(ch_b, include_side_pairing)
    matcher = nx.algorithms.isomorphism.GraphMatcher(
        ga, gb, node_match=lambda a, b: a["kind"] == b["kind"]
    )
    if not matcher.is_isomorphic():
        return None
    mapping = matcher.mapping
    return {
        "side_map": [
            int(mapping[f"s{s}"][1:]) for s in range(20)
        ],
        "chamber_map": [
            int(mapping[f"c{c}"][1:]) for c in range(len(ch_a))
        ],
    }


def chamber_masks(ch_rays: list[list[int]]) -> list[int]:
    return [sum(1 << side for side in sides) for sides in ch_rays]


def enumerate_vectorized(ch_rays: list[list[int]]) -> np.ndarray:
    """Independent method 1: evaluate all 2^20 assignments in NumPy."""
    assignments = np.arange(1 << 20, dtype=np.uint32)
    valid = np.ones(len(assignments), dtype=bool)
    for mask_int in chamber_masks(ch_rays):
        mask = np.uint32(mask_int)
        intersection = assignments & mask
        valid &= (intersection != 0) & (intersection != mask)
    # Canonical representative under global complement: bit zero is zero.
    return assignments[valid & ((assignments & 1) == 0)]


def enumerate_dfs(ch_rays: list[list[int]]) -> list[int]:
    """Independent method 2: constraint-pruned recursive enumeration."""
    masks = chamber_masks(ch_rays)
    touches = [
        sum(bool(mask & (1 << side)) for mask in masks) for side in range(20)
    ]
    # Fix side zero to 0 for the global-complement quotient.
    order = [0] + sorted(range(1, 20), key=lambda s: (-touches[s], s))
    assigned_mask = 1
    one_mask = 0
    out: list[int] = []

    def recurse(pos: int, assigned: int, ones: int) -> None:
        if pos == len(order):
            out.append(ones)
            return
        side = order[pos]
        bit = 1 << side
        # side zero was already assigned its canonical value.
        if side == 0:
            recurse(pos + 1, assigned, ones)
            return
        for value in (0, 1):
            new_assigned = assigned | bit
            new_ones = ones | bit if value else ones
            okay = True
            for mask in masks:
                if (new_assigned & mask) == mask:
                    selected = new_ones & mask
                    if selected == 0 or selected == mask:
                        okay = False
                        break
            if okay:
                recurse(pos + 1, new_assigned, new_ones)

    recurse(0, assigned_mask, one_mask)
    return sorted(out)


def signs_from_bits(bits: int) -> list[int]:
    """Bit 1 is sigma +1; bit 0 is sigma -1."""
    return [1 if bits & (1 << side) else -1 for side in range(20)]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out", type=Path, default=Path("sigma_enum.json"))
    parser.add_argument("--seed", type=int, default=20260730)
    parser.add_argument("--incidence-trials", type=int, default=40)
    args = parser.parse_args()

    rng = np.random.default_rng(args.seed)
    u0 = unit_rows(rng.normal(size=(5, 3)))
    classes, chambers, ch_rays = deterministic_build(u0)
    if len(chambers) != 22:
        raise RuntimeError(f"reference U has {len(chambers)} rather than 22 chambers")

    vectorized = enumerate_vectorized(ch_rays)
    dfs = np.asarray(enumerate_dfs(ch_rays), dtype=np.uint32)
    if not np.array_equal(vectorized, dfs):
        raise RuntimeError("the two exhaustive enumeration methods disagree")

    incidence_trials = []
    all_iso_with_pairing = True
    all_iso_without_pairing = True
    for trial in range(args.incidence_trials):
        u = unit_rows(rng.normal(size=(5, 3)))
        _, trial_chambers, trial_rays = deterministic_build(u)
        iso_pair = graph_isomorphism(ch_rays, trial_rays, True)
        iso_plain = graph_isomorphism(ch_rays, trial_rays, False)
        all_iso_with_pairing &= iso_pair is not None
        all_iso_without_pairing &= iso_plain is not None
        incidence_trials.append(
            {
                "trial": trial,
                "genericity": genericity(u),
                "n_chambers": len(trial_chambers),
                "degree_multiset": sorted(map(len, trial_rays)),
                "isomorphic_with_antipodal_pairing": iso_pair is not None,
                "isomorphic_plain_incidence": iso_plain is not None,
                "side_map_with_pairing": None if iso_pair is None else iso_pair["side_map"],
            }
        )

    hamming = np.bincount(
        np.asarray([int(v).bit_count() for v in vectorized]), minlength=21
    )
    payload = {
        "schema": 1,
        "seed": args.seed,
        "bit_convention": "bit 1 = sigma +1; bit 0 = sigma -1",
        "global_flip_representative": "side 0 is fixed to -1 (bit 0 = 0)",
        "reference_U": u0.tolist(),
        "reference_genericity": genericity(u0),
        "pairs_in_class_order": [list(pair) for pair in PAIRS],
        "chambers": chambers,
        "chamber_side_incidence": ch_rays,
        "chamber_masks": chamber_masks(ch_rays),
        "n_valid_labeled": int(2 * len(vectorized)),
        "n_global_flip_classes": int(len(vectorized)),
        "class_bits": [int(v) for v in vectorized],
        "hamming_weight_histogram_for_representatives": hamming.tolist(),
        "verification": {
            "method_1": "vectorized scan of all 2^20 assignments",
            "method_2": "independent constraint-pruned DFS with side 0 fixed",
            "methods_exactly_agree_in_sorted_order": True,
        },
        "incidence_isomorphism_test": {
            "method": (
                "colored graph isomorphism: chamber nodes colored by degree, "
                "side nodes, and degree-2 nodes encoding the ten antipodal side pairs"
            ),
            "n_random_generic_trials": args.incidence_trials,
            "all_isomorphic_with_antipodal_pairing": all_iso_with_pairing,
            "all_isomorphic_plain_incidence": all_iso_without_pairing,
            "trials": incidence_trials,
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(
        f"{len(vectorized)} global-flip classes "
        f"({2 * len(vectorized)} labeled sigmas); wrote {args.out}"
    )


if __name__ == "__main__":
    main()
