#!/usr/bin/env python3
"""Exact parent-positive identities for diagonal-three candidate factors.

The valid 105-segment theorem leaves 6,980 candidate full-support residual
factors unresolved.  This verifier proves that 1,177 of those factors never
vanish in the strict row-2599 parent cell.

For 85 representatives the certificate has the form

    sign * residual = sum(signed_parent_i * signed_parent_j),

For 63 more, one factor in each parent-bracket product is multiplied by a
single positive chart coordinate; for two representatives the certificate is
a sum of positive-coordinate monomial multiples of individual signed parent
brackets.  Every identity is expanded and checked over the integers.  The
signed parent brackets and chart coordinates are strictly positive on the
parent cell, so the represented residual has a strict fixed sign there.

The moving-column action is used only as an algebraic identity generator.
For each transformed identity, every transported signed parent bracket is
matched to an actual row-2599 signed parent bracket with its sign preserved.
The transformed identity is accepted only when all summands acquire the same
sign.  This conditional exact check is valid even though the signed parent
cell itself is not S3-invariant.

The broad product screen uses floating-point linear programming only to
propose identities.  An entry is accepted solely when its proposed unit
coefficients expand to literal equality over the integers.  Numerical error
can therefore cause only a failed replay or a missed identity, never a false
fixed-sign claim.
"""
from __future__ import annotations

from collections import Counter
from itertools import permutations
import hashlib
import json
from pathlib import Path
import sys

import numpy as np
from scipy.optimize import linprog


HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import DIAG2_PIVOT_LABELED_PAIR_ORBITS_VERIFY as labeled  # noqa: E402
import verify_diag3_pair_fullsupport_block_symmetry as symmetry  # noqa: E402
import verify_diag3_pair_global_parent_face_gate as gate  # noqa: E402


EXPECTED_PRODUCT_CLASSES = 85
EXPECTED_SHIFTED_PRODUCT_CLASSES = 63
EXPECTED_MONOMIAL_CLASSES = 2
EXPECTED_SEED_IDENTITIES = 150
EXPECTED_DIRECT_PRODUCT_FACTORS = 965
EXPECTED_DIRECT_PRODUCT_SHA256 = "4121a7abb7610d969ed18cecc5c3df918a6a3263633efb2a1e99129dd3c4469c"
EXPECTED_EMPTY_FACTORS = 1_177
EXPECTED_REMAINING_FACTORS = 5_803
EXPECTED_EMPTY_SHA256 = "f9022c922d56c69ea541d6098cea89004bdfcff73b01a411a159a78b5c369484"
EXPECTED_REMAINING_SHA256 = "0c85f0e7370963df311a5a7d04e175e4a801b79c54fe0600a69bb777bf30a76a"

# Discovery used a nonnegative floating-point cone search.  The theorem does
# not: this fixed list is replayed by exact integer polynomial expansion.
# Format: representative | fixed sign | positive parent-bracket products.
PRODUCT_CERTIFICATES = """
100|-|2357*3468+2368*2457
201|-|1237*4578+2467*3578+2578*3457
343|+|1346*2578+2368*2478+2378*2458
602|-|2348*3578+2578*3456
724|+|2348*2578+2456*3578
2444|+|1238*1567+1258*3567
2514|-|1237*3568+1568*2357
2625|+|1237*1568+1357*2568
2641|-|1237*2568+1568*2357
2914|+|1238*5678+2678*3458
2923|+|1248*5678+1458*2567
2925|+|1248*5678+2678*3458
2983|+|1256*1478+1578*2456
2984|+|1356*1478+1578*3456
3065|-|1237*4567+1567*2458+2478*3567+2567*3478
3067|-|1348*4567+1458*3567
3253|+|1257*2368+1357*2568
3255|+|1257*2468+1457*2568
3302|+|1248*2567+1267*1458
3322|+|1248*2567+1458*2467
3382|+|1236*2467+1267*3458+2367*2468
3500|-|1247*1568+1257*4568+1457*2568
3503|-|1246*2578+1578*2456
3510|-|1346*3578+1578*3456
3550|-|1237*4678+2457*3678+2678*3457
3577|-|1247*1568+1257*4568
3626|-|1257*4568+1457*2468
3688|-|1347*1568+1357*4568
3731|-|1238*4678+2678*3458
4180|-|1238*5678+1678*2458
4181|-|1238*5678+1678*3458
4406|-|1248*3678+1358*2678
4430|+|1257*1568+1578*2568
4483|+|1238*5678+2458*3678
4504|+|1358*1567+1358*1578+1368*1578
4565|+|1238*5678+1378*2567
4719|+|1268*3578+1358*2678+1378*2678
4769|-|1237*1568+1278*3568
5016|-|1248*5678+1678*3458
5041|+|1257*1468+1578*2468
5109|+|1478*1568+1578*4568
5166|-|1458*2678+1678*2458+2458*4678
5170|+|1248*5678+1678*2458+2458*4678
5277|+|1248*5678+1678*2358
5406|-|1238*4678+2458*3678
5575|-|1348*3567+1458*3467
5589|-|1348*3567+1367*1458
5634|-|1378*2458+1478*2368
5647|+|1348*5678+2458*3678
6237|+|1237*1568+1378*2568
6316|-|1258*3678+1348*2678
6473|+|1348*1578+1358*1467+1378*1456
6625|+|1348*2678+2358*4678
6642|-|1248*3678+1358*4678
6836|-|2458*3678+2678*3458+3458*5678
6840|+|1458*3678+2358*4678
6895|+|1348*5678+1678*2358
6898|+|1348*5678+1678*2458
7077|-|2348*5678+2458*3678+2678*3456
7082|+|1248*3678+2358*4678
7147|-|1237*4678+2467*3678+2678*3478
7192|-|1258*4678+1348*2678
8698|+|1258*1467+1258*4567+1458*2467
9184|+|1258*1467+1458*2467
9206|-|1248*4567+1258*1467
9564|-|1467*2356+1468*2367+2356*4678
9570|+|1278*1456+1478*2456
9571|+|1357*1468+1467*3458+1478*3456
9589|-|1348*4567+1358*1467
9700|-|1246*1578+1478*2456
9702|-|1378*1456+1478*3456
9706|-|1346*1578+1478*3456
9986|-|1238*4678+1678*2458
9987|-|1238*4678+1678*3458
10386|-|1468*1578+1478*4568
14107|+|1268*3567+1357*2568+2568*3567
14423|-|1256*3568+1358*2568+2568*3568
14957|-|1256*1368+1268*1358+1268*1368
16424|+|1368*2567+1568*2467+1568*2567
19412|-|1268*3467+1368*2467+1468*2356
19603|-|1258*1467+1678*2458
19605|+|1256*1478+1258*1467+1268*1478
19629|-|1358*1467+1678*3458
19772|+|1347*1568+1368*1457+1368*1467
20592|-|1467*1578+1678*4578
"""

# The optional ``@k`` suffix multiplies a positive parent-bracket product by
# chart coordinate k.  Unmarked products have multiplier one.
SHIFTED_PRODUCT_CERTIFICATES = """
676|-|1258*3456+2456*3457@8
1051|+|1358*2468+2358*2467@6+2468*3458@5
1251|+|2368*4578@7+2458*2578@6+2458*3578@7
1285|+|1248*3578+1258*3478+2458*3478@2
1286|+|2456*3578@7+2568*3478
1698|+|1358*2456+2457*3456@8
1811|+|1258*3478+1478*2358+2458*3478@2
2057|+|2357*2468@6+2578*3468
2778|+|2456*3568@5+2467*3568+2567*3468
3007|-|1257*1358+1258*3456@5
3043|-|1258*2467+1358*2456@4+1458*2456@5
3262|+|2357*2468@3+2678*3457
3591|+|2348*5678+1567*2458+2458*4567@8
3600|+|1458*3567+2358*4567@6
3612|+|2457*3567@7+2458*2567@3+2567*3478
3670|-|1258*1357+1358*2456@5
4179|-|1238*5678+1567*2358@7
4183|-|1238*5678+1567*2358@6
4236|-|1258*3678+1358*2367@7
4289|-|1278*3567+2478*3568@5
4326|+|1278*3568+1356*2578@7
4344|+|1278*3568+1356*2578@6
4602|-|1567*2358@6+1578*2358@0+1578*2368
4830|-|1358*2468@5+1468*2378
5017|-|1248*5678+1567*2458@6
5046|+|1258*3468@4+1278*1458
5502|-|2357*3468@4+2457*3678
5901|-|1348*2567+2358*2467@3+2467*3478
5910|-|1256*3467+2456*3468@5+2456*3478@2
5968|+|1378*2567+2568*3478@5
6138|-|1257*3468@8+1368*2458@5+1368*2478
6925|-|1268*3478+1368*3478+1457*3468@8+1458*3468@5
7010|-|1368*2458@3+1458*2368@3+1458*3468@5
7022|+|1358*3467@7+1458*3678
7042|-|1278*3458@0+1458*3468@5
7169|+|2457*3678@7+2578*3468@4
7280|-|1358*2378@1+1378*2468
7323|-|2456*3678@6+2568*3478@0
7438|-|1237*5678+1258*1567+1567*2458@5
7884|-|1248*5678@5+1258*1678+1678*2458@5
8022|-|1257*2367@6+1357*2368@4+1457*2367@8
8477|+|1268*3578@3+1357*2678@6
9326|+|1258*1467+1458*2467@8
9360|+|1257*1468+1457*2468@8
9477|-|1358*2468@4+1468*2478
10002|+|1278*1456+1478*2456@8
10007|+|1258*3468@3+1278*3468+1357*2468@6
10213|-|1358*4678+1458*3467@8
10322|-|1378*1456+1478*3456@8
10346|-|1268*3468+2368*3468@4+2468*3478@2
10404|-|1468*2358@4+1478*2468
10417|-|1358*1468@3+1467*3458@6+1478*3456@6
10418|+|1258*3478@0+1478*3468
11803|+|1457*2678+2367*4568@4+2368*4567@4
12188|-|1478*3568@5+1568*2378@3
13261|-|1258*2367@3+1278*2367+1278*3567
18713|-|1268*3457@4+1278*2467@0+1278*3456@1
19514|-|1368*1457+1468*3457@5
20545|-|1256*1478@7+1467*2358@7+1478*2458@1
20927|+|1368*1478+1468*2358@3
20943|+|1368*1478+1378*2458@0
21473|-|1256*3678@3+1267*3678+1357*2678@0
21620|-|1347*5678@2+1457*3678@2+1678*2356@3
"""

# sign * residual = sum(x^exponent * signed_parent[label]).
MONOMIAL_CERTIFICATES = {
    3978: (
        -1,
        (
            ("1357", (0, 0, 0, 0, 0, 0, 0, 1, 0)),
            ("3457", (0, 1, 0, 0, 0, 0, 0, 0, 1)),
        ),
    ),
    5783: (
        -1,
        (
            ("1257", (0, 0, 0, 0, 0, 0, 1, 0, 0)),
            ("2457", (1, 0, 0, 0, 0, 0, 0, 0, 1)),
        ),
    ),
}


def add(*polynomials):
    result = Counter()
    for polynomial in polynomials:
        result.update(polynomial)
    return {monomial: coefficient for monomial, coefficient in result.items() if coefficient}


def multiply(left, right):
    result = Counter()
    for a, x in left.items():
        for b, y in right.items():
            result[tuple(a[i] + b[i] for i in range(9))] += x * y
    return {monomial: coefficient for monomial, coefficient in result.items() if coefficient}


def scale(polynomial, coefficient):
    return {monomial: coefficient * value for monomial, value in polynomial.items()}


def monomial(exponent):
    return {tuple(exponent): 1}


def exponent_cap(polynomial):
    return tuple(max(term[index] for term in polynomial) for index in range(9))


def exact_direct_product_screen(polynomials, factor_ids, signed_parents, sample):
    """Use LP only to propose identities; accept solely by exact ZZ equality."""
    raw_products = []
    parent_items = tuple(signed_parents.items())
    for left_index, (left_label, left) in enumerate(parent_items):
        for right_label, right in parent_items[left_index:]:
            product = multiply(left, right)
            raw_products.append(
                ((left_label, right_label), product, exponent_cap(product))
            )
    products = tuple(
        {tuple(sorted(product.items())): (labels, product, cap)
         for labels, product, cap in raw_products}.values()
    )

    certified = set()
    for factor_id in sorted(factor_ids):
        target = polynomials[factor_id]
        cap = exponent_cap(target)
        sign = 1 if gate.evaluator.evaluate(target, sample) > 0 else -1
        generators = [
            product
            for _labels, product, product_cap in products
            if all(product_cap[index] <= cap[index] for index in range(9))
        ]
        basis = sorted(
            set(target) | set().union(*(set(generator) for generator in generators))
        ) if generators else sorted(target)
        columns = generators + [monomial(term) for term in basis]
        matrix = np.asarray([
            [float(column.get(term, 0)) for column in columns]
            for term in basis
        ])
        right = np.asarray([float(sign * target.get(term, 0)) for term in basis])
        proposal = linprog(
            np.ones(len(columns)),
            A_eq=matrix,
            b_eq=right,
            bounds=(0, None),
            method="highs",
        )
        if not proposal.success or np.max(np.abs(matrix @ proposal.x - right)) >= 1e-8:
            continue
        active = [index for index, value in enumerate(proposal.x) if value > 1e-8]
        if not all(
            index < len(generators) and abs(proposal.x[index] - 1) < 1e-8
            for index in active
        ):
            continue
        # This equality, not the LP residual, is the proof gate.
        if add(*(generators[index] for index in active)) == scale(target, sign):
            certified.add(factor_id)
    return certified


def parse_product_certificates():
    result = {}
    for raw in PRODUCT_CERTIFICATES.strip().splitlines():
        factor, sign, expression = raw.split("|")
        terms = tuple(tuple(term.split("*")) for term in expression.split("+"))
        result[int(factor)] = (1 if sign == "+" else -1, terms)
    if len(result) != EXPECTED_PRODUCT_CLASSES:
        raise AssertionError("product certificate census changed")
    return result


def parse_shifted_product_certificates():
    result = {}
    for raw in SHIFTED_PRODUCT_CERTIFICATES.strip().splitlines():
        factor, sign, expression = raw.split("|")
        terms = []
        for term in expression.split("+"):
            product, marker, coordinate = term.partition("@")
            left, right = product.split("*")
            terms.append((left, right, int(coordinate) if marker else None))
        result[int(factor)] = (1 if sign == "+" else -1, tuple(terms))
    if len(result) != EXPECTED_SHIFTED_PRODUCT_CLASSES:
        raise AssertionError("shifted-product certificate census changed")
    return result


def main():
    # Replay the load-bearing segment theorem and the signed-symmetry no-go.
    symmetry.main()

    records = [json.loads(line) for line in gate.CATALOG.read_text().splitlines() if line]
    parents, _digest = gate.parent_polynomials(records[2599])
    signed_parents = {
        label: scale(polynomial, target)
        for label, target, polynomial, _terms in parents
    }
    if len(signed_parents) != 70:
        raise AssertionError("parent bracket label census changed")

    _occurrences, _mapping, polynomials = labeled.factor_polynomials()
    candidates = gate.parse_candidates()
    with np.load(gate.POINT_BANK, allow_pickle=False) as source:
        matrices = np.asarray(source["chart_matrix"], dtype=np.int64)
    points = tuple(gate.normalized_values(matrix.tolist()) for matrix in matrices)
    base_open = set(symmetry.base_open_ids(points, polynomials, candidates))
    candidate_set = set(candidates)
    crossed = candidate_set - base_open

    factor_index = {
        symmetry.primitive_key(polynomial): factor_id
        for factor_id, polynomial in enumerate(polynomials)
    }
    perms = tuple(permutations(range(3)))
    signed_parent_keys = {
        symmetry.directed_key(polynomial) for polynomial in signed_parents.values()
    }

    def transported_parent_sign(label, perm):
        key = symmetry.directed_key(
            symmetry.raw_transform(signed_parents[label], perm)
        )
        if key in signed_parent_keys:
            return 1
        if symmetry.negative_key(key) in signed_parent_keys:
            return -1
        raise AssertionError((label, perm, "left unsigned parent divisor set"))

    def transported_factor_id(factor_id, perm):
        key = symmetry.primitive_key(
            symmetry.raw_transform(polynomials[factor_id], perm)
        )
        return factor_index[key]

    product_certificates = parse_product_certificates()
    shifted_product_certificates = parse_shifted_product_certificates()
    certificate_sets = (
        set(product_certificates),
        set(shifted_product_certificates),
        set(MONOMIAL_CERTIFICATES),
    )
    if len(set().union(*certificate_sets)) != sum(map(len, certificate_sets)):
        raise AssertionError("certificate families overlap")

    # First replay every seed identity directly over ZZ.
    for factor_id, (sign, products) in product_certificates.items():
        if factor_id not in base_open:
            raise AssertionError(f"product seed {factor_id} left the base-open set")
        positive_terms = []
        for left, right in products:
            positive_terms.append(multiply(signed_parents[left], signed_parents[right]))
        if add(*positive_terms) != scale(polynomials[factor_id], sign):
            raise AssertionError(f"parent-product identity failed for {factor_id}")

    for factor_id, (sign, products) in shifted_product_certificates.items():
        if factor_id not in base_open:
            raise AssertionError(f"shifted-product seed {factor_id} left the base-open set")
        positive_terms = []
        for left, right, coordinate in products:
            term = multiply(signed_parents[left], signed_parents[right])
            if coordinate is not None:
                exponent = tuple(int(index == coordinate) for index in range(9))
                term = multiply(monomial(exponent), term)
            positive_terms.append(term)
        if add(*positive_terms) != scale(polynomials[factor_id], sign):
            raise AssertionError(f"shifted parent-product identity failed for {factor_id}")

    for factor_id, (sign, terms) in MONOMIAL_CERTIFICATES.items():
        if factor_id not in base_open:
            raise AssertionError(f"monomial seed {factor_id} left the base-open set")
        positive_terms = [
            multiply(monomial(exponent), signed_parents[label])
            for label, exponent in terms
        ]
        if add(*positive_terms) != scale(polynomials[factor_id], sign):
            raise AssertionError(f"parent-monomial identity failed for {factor_id}")

    if sum(map(len, certificate_sets)) != EXPECTED_SEED_IDENTITIES:
        raise AssertionError("seed identity census changed")

    direct_product_factors = exact_direct_product_screen(
        polynomials, base_open, signed_parents, points[0]
    )
    direct_product_digest = hashlib.sha256(
        ",".join(map(str, sorted(direct_product_factors))).encode("ascii")
    ).hexdigest()
    if len(direct_product_factors) != EXPECTED_DIRECT_PRODUCT_FACTORS:
        raise AssertionError((len(direct_product_factors), direct_product_digest))
    if direct_product_digest != EXPECTED_DIRECT_PRODUCT_SHA256:
        raise AssertionError((len(direct_product_factors), direct_product_digest))

    # Transform identities only as polynomial formulas.  A transported
    # summand is sign-usable precisely when its parent-bracket factors map to
    # actual row-2599 signed parent brackets with a common overall sign.
    certified_factors = set(direct_product_factors)
    for factor_id, (_sign, products) in product_certificates.items():
        for perm in perms:
            term_signs = [
                transported_parent_sign(left, perm)
                * transported_parent_sign(right, perm)
                for left, right in products
            ]
            if len(set(term_signs)) == 1:
                certified_factors.add(transported_factor_id(factor_id, perm))

    for factor_id, (_sign, products) in shifted_product_certificates.items():
        for perm in perms:
            term_signs = [
                transported_parent_sign(left, perm)
                * transported_parent_sign(right, perm)
                for left, right, _coordinate in products
            ]
            if len(set(term_signs)) == 1:
                certified_factors.add(transported_factor_id(factor_id, perm))

    for factor_id, (_sign, terms) in MONOMIAL_CERTIFICATES.items():
        for perm in perms:
            term_signs = [
                transported_parent_sign(label, perm) for label, _exponent in terms
            ]
            if len(set(term_signs)) == 1:
                certified_factors.add(transported_factor_id(factor_id, perm))

    # A fixed-sign candidate cannot also have an exact segment crossing.
    contradiction = certified_factors & crossed
    if contradiction:
        raise AssertionError(("fixed-sign/segment contradiction", sorted(contradiction)))
    certified_factors &= base_open
    if len(certified_factors) != EXPECTED_EMPTY_FACTORS:
        raise AssertionError("certified factor count changed")

    digest = hashlib.sha256(
        ",".join(map(str, sorted(certified_factors))).encode("ascii")
    ).hexdigest()
    if digest != EXPECTED_EMPTY_SHA256:
        raise AssertionError((len(certified_factors), digest))

    remaining = base_open - certified_factors
    remaining_digest = hashlib.sha256(
        ",".join(map(str, sorted(remaining))).encode("ascii")
    ).hexdigest()
    if (
        len(remaining) != EXPECTED_REMAINING_FACTORS
        or remaining_digest != EXPECTED_REMAINING_SHA256
    ):
        raise AssertionError((len(remaining), remaining_digest))

    print("PASS", EXPECTED_PRODUCT_CLASSES, "exact parent-product seed identities")
    print("PASS", EXPECTED_SHIFTED_PRODUCT_CLASSES, "exact coordinate-shifted product seed identities")
    print("PASS", EXPECTED_MONOMIAL_CLASSES, "exact parent-monomial seed identities")
    print("PASS", len(direct_product_factors), "direct parent-product identities")
    print("DIRECT_PRODUCT_SHA256", direct_product_digest)
    print("PASS", len(certified_factors), "base-open candidate factors have empty strict-parent zero sets")
    print("EMPTY_SHA256", digest)
    print("OPEN", len(remaining), "candidate factors retained without a feasibility classification")
    print("OPEN_SHA256", remaining_digest)
    print("SCOPE exact wall-emptiness certificates only; diagonal three remains open")


if __name__ == "__main__":
    main()
