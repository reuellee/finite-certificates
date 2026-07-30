"""Conservative symbolic Grassmann--Pluecker certificate search.

The 100 largest Stage-1-margin classes are mapped into the literal U_INTS
labeling by a signed permutation of generators.  For each mapped system we
enumerate four-side normal circuits.  Cofactor multipliers are expanded as
polynomials in D_ijk=|det(U_i,U_j,U_k)| using

  det(a x b, c x d, e x f)
    = det(c,d,f)det(a,b,e) - det(c,d,e)det(a,b,f).

A result is accepted only if, after substituting the fixed chirotope signs,
all multiplier polynomials are coefficientwise positive and all five
positivity-slack polynomials are coefficientwise nonnegative.  This
sufficient test needs no inequality reasoning modulo Pluecker relations, so
every reported success is valid throughout the literal reference
reorientation cell.  Failure is only failure of this deliberately narrow
four-circuit/coefficientwise test.
"""
from __future__ import annotations

import itertools
import json
from pathlib import Path

import numpy as np

from make_stage2b import (
    HERE,
    PAIRS,
    U_INTS,
    cross,
    det3,
    exact_chambers_with_witnesses,
    exact_incidence,
)


STAGE1 = HERE.parent / "stage1_gpt"
MARGIN_PATH = STAGE1 / "margins.json"
SIGMA_PATH = STAGE1 / "sigma_enum.json"
N_TARGETS = 100
SEARCH_SEED = 2026073004
TRIPLES = tuple(itertools.combinations(range(5), 3))
TRIPLE_INDEX = {triple: index for index, triple in enumerate(TRIPLES)}


def sign(value):
    if value == 0:
        raise ValueError("zero where a strict chirotope sign was required")
    return 1 if value > 0 else -1


def chirotope(U):
    return tuple(sign(det3(U[i], U[j], U[k])) for i, j, k in TRIPLES)


def permutation_sign(values):
    inversions = sum(
        values[i] > values[j]
        for i in range(len(values)) for j in range(i + 1, len(values))
    )
    return -1 if inversions % 2 else 1


def signed_plucker(indices, chi):
    if len(set(indices)) < 3:
        return None
    ordered = tuple(sorted(indices))
    coefficient = permutation_sign(indices) * chi[TRIPLE_INDEX[ordered]]
    return coefficient, TRIPLE_INDEX[ordered]


def clean(poly):
    return {monomial: coefficient for monomial, coefficient in poly.items()
            if coefficient}


def add_term(poly, monomial, coefficient):
    if coefficient:
        poly[tuple(sorted(monomial))] = (
            poly.get(tuple(sorted(monomial)), 0) + coefficient
        )


def scale_poly(poly, scalar):
    return clean({monomial: scalar * coefficient
                  for monomial, coefficient in poly.items()})


def multiply_variable(poly, variable):
    out = {}
    for monomial, coefficient in poly.items():
        add_term(out, monomial + (variable,), coefficient)
    return clean(out)


def triple_cross_poly(edge1, edge2, edge3, chi):
    """Polynomial for det(C_edge1,C_edge2,C_edge3)."""
    a, b = edge1
    c, d = edge2
    e, f = edge3
    out = {}
    left1 = signed_plucker((c, d, f), chi)
    right1 = signed_plucker((a, b, e), chi)
    if left1 is not None and right1 is not None:
        add_term(out, (left1[1], right1[1]), left1[0] * right1[0])
    left2 = signed_plucker((c, d, e), chi)
    right2 = signed_plucker((a, b, f), chi)
    if left2 is not None and right2 is not None:
        add_term(out, (left2[1], right2[1]), -left2[0] * right2[0])
    return clean(out)


def find_signed_permutation(source_U, target_U):
    """Return new-index -> old-index permutation and row reorientations."""
    target_chi = chirotope(target_U)
    for permutation in itertools.permutations(range(5)):
        for flip_bits in range(32):
            flips = tuple(
                1 if flip_bits & (1 << index) else -1 for index in range(5)
            )
            candidate = tuple(
                tuple(flips[t] * source_U[permutation[t]][d] for d in range(3))
                for t in range(5)
            )
            if chirotope(candidate) == target_chi:
                return permutation, flips
    raise RuntimeError("no signed permutation maps the Stage-1 chirotope")


def map_sigma_bits(old_bits, permutation, flips):
    old_pair_index = {pair: ci for ci, pair in enumerate(PAIRS)}
    new_bits = 0
    side_map = []
    for new_ci, (i, j) in enumerate(PAIRS):
        a, b = permutation[i], permutation[j]
        old_ci = old_pair_index[tuple(sorted((a, b)))]
        orientation = flips[i] * flips[j] * (1 if a < b else -1)
        old_plus = 2 * old_ci if orientation == 1 else 2 * old_ci + 1
        old_minus = 2 * old_ci + 1 if orientation == 1 else 2 * old_ci
        side_map.extend([old_plus, old_minus])
        if old_bits & (1 << old_plus):
            new_bits |= 1 << (2 * new_ci)
        if old_bits & (1 << old_minus):
            new_bits |= 1 << (2 * new_ci + 1)
    return new_bits, side_map


def mapped_split(old_k, permutation):
    old_split = [1] * old_k + [-1] * (5 - old_k)
    return tuple(old_split[permutation[t]] for t in range(5))


def normal_scalar(bits, side):
    sigma = 1 if bits & (1 << side) else -1
    ray_orientation = 1 if side % 2 == 0 else -1
    return sigma * ray_orientation


def side_weight_sign(bits, side, split, t):
    ci = side // 2
    i, j = PAIRS[ci]
    if t in (i, j):
        return None
    sigma = 1 if bits & (1 << side) else -1
    triple = tuple(sorted((t, i, j)))
    return sigma * split[t], TRIPLE_INDEX[triple]


def circuit_polynomials(bits, sides, chi):
    y = []
    for omitted in range(4):
        retained = [q for q in range(4) if q != omitted]
        edges = [PAIRS[sides[q] // 2] for q in retained]
        poly = triple_cross_poly(edges[0], edges[1], edges[2], chi)
        scalar = (-1 if omitted % 2 else 1)
        for q in retained:
            scalar *= normal_scalar(bits, sides[q])
        y.append(scale_poly(poly, scalar))
    if any(not poly for poly in y):
        return None
    first_sign = sign(next(iter(y[0].values())))
    global_sign = first_sign
    y = [scale_poly(poly, global_sign) for poly in y]
    if any(any(coefficient <= 0 for coefficient in poly.values()) for poly in y):
        return None
    return y


def positivity_slacks(bits, split, sides, y):
    slacks = []
    for t in range(5):
        weight_sum = {}
        for side, poly in zip(sides, y):
            signed_variable = side_weight_sign(bits, side, split, t)
            if signed_variable is None:
                continue
            coefficient, variable = signed_variable
            term = scale_poly(multiply_variable(poly, variable), coefficient)
            for monomial, value in term.items():
                add_term(weight_sum, monomial, value)
        slack = scale_poly(clean(weight_sum), -1)
        if any(coefficient < 0 for coefficient in slack.values()):
            return None
        slacks.append(slack)
    return slacks


def serialize_poly(poly):
    return [
        {
            "coefficient": coefficient,
            "monomial": ["D" + "".join(map(str, TRIPLES[index]))
                         for index in monomial],
        }
        for monomial, coefficient in sorted(poly.items())
    ]


def find_certificate(bits, split, chi):
    for sides in itertools.combinations(range(20), 4):
        # Four copies of fewer than four normal directions cannot give the
        # strictly positive four-circuit sought here.
        if len({side // 2 for side in sides}) < 4:
            continue
        y = circuit_polynomials(bits, sides, chi)
        if y is None:
            continue
        slacks = positivity_slacks(bits, split, sides, y)
        if slacks is None:
            continue
        return {
            "sides": list(sides),
            "side_pairs": [list(PAIRS[side // 2]) for side in sides],
            "multipliers": [serialize_poly(poly) for poly in y],
            "positivity_slacks": [serialize_poly(poly) for poly in slacks],
        }
    return None


def is_valid_sigma(bits, ch_rays):
    for sides in ch_rays:
        values = {1 if bits & (1 << side) else -1 for side in sides}
        if len(values) < 2:
            return False
    return True


def main():
    margins = json.loads(MARGIN_PATH.read_text(encoding="utf-8"))
    sigma_payload = json.loads(SIGMA_PATH.read_text(encoding="utf-8"))
    source_U = tuple(tuple(float(value) for value in row)
                     for row in sigma_payload["reference_U"])
    target_U = tuple(tuple(value for value in row) for row in U_INTS)
    permutation, flips = find_signed_permutation(source_U, target_U)
    target_chi = chirotope(target_U)
    chambers, _ = exact_chambers_with_witnesses(target_U)
    ch_rays = exact_incidence(target_U, chambers)

    leaders = sorted(
        margins["classes"], key=lambda entry: entry["best_margin"], reverse=True
    )[:N_TARGETS]
    results = []
    for rank, entry in enumerate(leaders, 1):
        old_bits = int(entry["class_bits"])
        old_k = max(
            (2, 3),
            key=lambda k: entry["splits"][str(k)]["best_margin"],
        )
        bits, side_map = map_sigma_bits(old_bits, permutation, flips)
        split = mapped_split(old_k, permutation)
        if not is_valid_sigma(bits, ch_rays):
            raise AssertionError(
                f"mapped Stage-1 leader rank {rank} is not valid on U_INTS"
            )
        certificate = find_certificate(bits, split, target_chi)
        results.append({
            "rank": rank,
            "stage1_class_index": entry["class_index"],
            "stage1_class_bits": old_bits,
            "stage1_best_margin": entry["best_margin"],
            "stage1_selected_k": old_k,
            "mapped_sigma_bits": bits,
            "mapped_split": list(split),
            "old_side_for_each_new_side": side_map,
            "symbolic_certificate_found": certificate is not None,
            "certificate": certificate,
        })
        if rank % 10 == 0:
            count = sum(item["symbolic_certificate_found"] for item in results)
            print(f"symbolic: {rank}/{N_TARGETS}, successes={count}", flush=True)

    successes = sum(item["symbolic_certificate_found"] for item in results)
    payload = {
        "schema": 1,
        "status": "exact_sufficient_test_complete",
        "search_seed": SEARCH_SEED,
        "n_targets": N_TARGETS,
        "n_successes": successes,
        "n_failures": N_TARGETS - successes,
        "stage1_ranking_source": str(MARGIN_PATH.relative_to(HERE.parent.parent)),
        "mapping": {
            "new_reference_index_to_old_stage1_index": list(permutation),
            "new_row_reorientation_signs": list(flips),
            "target_literal_chirotope_signs": list(target_chi),
            "explanation": (
                "The signed permutation maps the Stage-1 reference chirotope "
                "to U_INTS. Sigma side labels and the selected split are both "
                "transported by this same map before any symbolic search."
            ),
        },
        "method": (
            "Enumerate four distinct facet-normal classes. Cofactor multipliers "
            "are expanded in absolute determinants using the triple-cross "
            "identity. Accept only coefficientwise-positive multipliers and "
            "coefficientwise-nonnegative weight slacks."
        ),
        "scope": (
            "Every success is exact across the literal U_INTS chirotope cell. "
            "Failures do not rule out larger supports or proofs that require "
            "Grassmann-Pluecker reductions between opposite-sign monomials."
        ),
        "results": results,
    }
    out = HERE / "symbolic_gp_results.json"
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {out}; exact symbolic successes {successes}/{N_TARGETS}")


if __name__ == "__main__":
    main()
